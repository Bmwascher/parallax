"""Contract pins for the kimi-code lane login wrapper (Task 5, 2026-08-01
lane-credential-and-lock plan). tools/new-kimi-lane-login.ps1 is the ONLY
thing in the system that creates the shared lane home and performs a
login into it, and it holds the lane lock while it does.

WINDOWS ONLY, whole module: the wrapper manipulates real Windows ACLs,
the exclusive-handle lock, and real process invocation. PARALLAX_PS_HOST
selects which host runs these tests, same pattern as
test_codex_context_probe.py:35-67 - a selector that merely finds A host
would happily collect them on Ubuntu CI too. A green suite on one Windows
host proves ONE interpreter.

Every destructive probe here uses a DISPOSABLE fake client binary and a
fake $env:USERPROFILE passed only through a subprocess's own environment
- never the real ~/.kimi-code, never a real login, never the real
$env:USERPROFILE.
"""
import importlib.util
import json
import os
import re
import shutil
import subprocess
import time
import uuid
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "tools" / "new-kimi-lane-login.ps1"
LOCK_SCRIPT = REPO / "tools" / "kimi-lane-lock.ps1"
VALIDATOR_SCRIPT = REPO / "tools" / "read-kimi-credential-state.ps1"


def _load_exact_line_module():
    path = REPO / "evals" / "tools" / "exact_line.py"
    spec = importlib.util.spec_from_file_location("exact_line", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


accept_exactly_one_nonempty_line = _load_exact_line_module().accept_exactly_one_nonempty_line

POWERSHELL = (os.environ.get("PARALLAX_PS_HOST")
              or shutil.which("powershell") or shutil.which("pwsh"))

pytestmark = pytest.mark.skipif(
    os.name != "nt" or POWERSHELL is None,
    reason="the login wrapper is a Windows tool: it needs a PowerShell "
           "host and the exclusive-handle / ACL platform it targets")

TOKEN_RE = re.compile(r"\A[0-9a-f]{32}\Z")

FAKE_OK_CREDENTIAL = (
    '{"access_token":"fake-access-token-value",'
    '"refresh_token":"fake-refresh-token-value",'
    '"expires_at":9999999999}'
)

STUB_CLIENT_BODY = r"""
param()
$markerFile = $env:PARALLAX_TEST_STUB_MARKER_FILE
if ($markerFile) {
    $count = 0
    if (Test-Path -LiteralPath $markerFile) {
        $count = [int]((Get-Content -LiteralPath $markerFile -Raw).Trim())
    }
    $count = $count + 1
    Set-Content -LiteralPath $markerFile -Value "$count" -NoNewline -Encoding ascii
}

$blockUntil = $env:PARALLAX_TEST_STUB_BLOCK_UNTIL
if ($blockUntil) {
    Write-Output "STUB-STDOUT-MARKER"
    [Console]::Error.WriteLine("STUB-STDERR-MARKER")
    while (-not (Test-Path -LiteralPath $blockUntil)) { Start-Sleep -Milliseconds 100 }
}

$mode = $env:PARALLAX_TEST_STUB_WRITE_CREDENTIAL
if ($mode -and $mode -ne "none") {
    $credDir = Join-Path $env:KIMI_CODE_HOME "credentials"
    if (-not (Test-Path -LiteralPath $credDir)) {
        New-Item -ItemType Directory -Path $credDir -Force | Out-Null
    }
    $credPath = Join-Path $credDir "kimi-code.json"
    if ($mode -eq "ok") {
        Set-Content -LiteralPath $credPath -Value @'
__OK_CRED__
'@ -Encoding ascii -NoNewline
    } elseif ($mode -eq "malformed") {
        Set-Content -LiteralPath $credPath -Value "not even json" -Encoding ascii -NoNewline
    } elseif ($mode -eq "unreadable") {
        New-Item -ItemType Directory -Path $credPath -Force | Out-Null
    }
}

$exitCode = 0
if ($env:PARALLAX_TEST_STUB_EXIT_CODE) { $exitCode = [int]$env:PARALLAX_TEST_STUB_EXIT_CODE }
exit $exitCode
""".replace("__OK_CRED__", FAKE_OK_CREDENTIAL)

STATEFUL_VALIDATOR_STUB_BODY = r"""
param([string]$Path)
$counterFile = $env:PARALLAX_TEST_VALIDATOR_COUNTER_FILE
$callNum = 1
if (Test-Path -LiteralPath $counterFile) {
    $callNum = [int]((Get-Content -LiteralPath $counterFile -Raw).Trim()) + 1
}
Set-Content -LiteralPath $counterFile -Value "$callNum" -NoNewline -Encoding ascii

$failOnCall = [int]$env:PARALLAX_TEST_VALIDATOR_FAIL_ON_CALL
$failMode = $env:PARALLAX_TEST_VALIDATOR_FAIL_MODE

if ($callNum -eq $failOnCall) {
    if ($failMode -eq "nonzero-valid") {
        Write-Output '{"status":"absent","detail":"no-file","fields":[]}'
        exit 3
    } elseif ($failMode -eq "exit0-malformed") {
        Write-Output "not even json"
        exit 0
    } elseif ($failMode -eq "scalar-fields") {
        # @(...) wraps a bare SCALAR into a one-element array, so a bare
        # string "fields" value must not pass an "array of strings" check.
        Write-Output '{"status":"ok","detail":"valid","fields":"access_token"}'
        exit 0
    } elseif ($failMode -eq "case-variant-keys") {
        # The KEYS, not the values. The frozen interface is exactly
        # status/detail/fields; the property-set comparison is what
        # rejects this, and it is a different check from the pair table.
        Write-Output '{"Status":"ok","Detail":"valid","Fields":["access_token"]}'
        exit 0
    } elseif ($failMode -eq "case-variant-pair") {
        # "OK"/"Valid" is NOT the frozen "ok"/"valid" pair. -eq is
        # case-insensitive on this platform, so this used to be accepted
        # and routed on.
        Write-Output '{"status":"OK","detail":"Valid","fields":["access_token"]}'
        exit 0
    } elseif ($failMode -eq "blank-line-padded") {
        # Exactly "\n\n{json}\n\n" - leading, interior and trailing blank
        # lines must all be rejected, not discarded before counting.
        [Console]::Out.Write("`n`n{`"status`":`"ok`",`"detail`":`"valid`",`"fields`":[`"access_token`"]}`n`n")
        exit 0
    }
}

Write-Output '{"status":"ok","detail":"valid","fields":["access_token","refresh_token","expires_at"]}'
exit 0
"""

ACL_DUMP_SCRIPT = r"""
param([string]$Path)
$acl = Get-Acl -LiteralPath $Path
# The outer @() is load-bearing, not decorative: ConvertTo-Json collapses
# a ONE-ELEMENT PowerShell array back to a bare object (dropping the
# array brackets), because `| ForEach-Object` with exactly one output
# collapses to a scalar on assignment unless the WHOLE pipeline result is
# re-wrapped. Without it, Python's json.loads(...)["Rules"] silently
# becomes a dict (whose len() is its KEY COUNT) instead of a list of
# rules whenever there is exactly one rule - reproduced live.
$rules = @(@($acl.Access) | ForEach-Object {
    # .Access returns IdentityReference in NTAccount ("B-PC\Brandon")
    # form by default; translate to SID form so this compares reliably
    # against [WindowsIdentity]::GetCurrent().User.Value.
    $sidValue = $_.IdentityReference.Translate([System.Security.Principal.SecurityIdentifier]).Value
    [ordered]@{
        Identity = $sidValue
        Rights = $_.FileSystemRights.ToString()
        Inheritance = $_.InheritanceFlags.ToString()
        Propagation = $_.PropagationFlags.ToString()
        Type = $_.AccessControlType.ToString()
        IsInherited = $_.IsInherited
    }
})
$obj = [ordered]@{
    Protected = $acl.AreAccessRulesProtected
    Sddl = $acl.Sddl
    Rules = $rules
}
ConvertTo-Json -InputObject $obj -Compress -Depth 5
"""


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def new_token():
    return uuid.uuid4().hex


def clean_env(overrides=None):
    """dict(os.environ), with PSModulePath stripped. This pytest process
    inherits a PowerShell-7-flavoured PSModulePath whose
    `...\\PowerShell\\7\\Modules` entry shadows the 5.1 copy of
    Microsoft.PowerShell.Security, so Get-Acl fails to load inside a
    powershell.exe child - matches test_kimi_lane_home.py's own `_build`
    helper. Dropping the variable lets each host compute its own default;
    nothing under test depends on it. Popped case-insensitively: Windows
    os.environ normalizes keys to upper case, so a plain
    pop("PSModulePath") silently removes nothing."""
    env = dict(os.environ)
    for key in [k for k in env if k.lower() == "psmodulepath"]:
        del env[key]
    if overrides:
        env.update(overrides)
    return env


def run_wrapper(args, env=None, timeout=30):
    cmd = [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(SCRIPT)] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, env=clean_env(env), timeout=timeout)


def start_wrapper_bg(args, env=None):
    cmd = [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(SCRIPT)] + list(args)
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, env=clean_env(env))


def run_lock(args, env=None, timeout=20):
    cmd = [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(LOCK_SCRIPT)] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, env=clean_env(env), timeout=timeout)


def ps_json(script_path, args, timeout=20):
    cmd = [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(script_path)] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, env=clean_env(), timeout=timeout)
    assert result.returncode == 0, (result.stdout, result.stderr)
    return json.loads(result.stdout)


def acl_dump(path, acl_dump_script):
    return ps_json(acl_dump_script, ["-Path", str(path)])


def current_sid():
    cmd = [POWERSHELL, "-NoProfile", "-NonInteractive", "-Command",
           "[System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value"]
    result = subprocess.run(cmd, capture_output=True, text=True, env=clean_env(), timeout=20)
    return result.stdout.strip()


def _ticks_for_pid(pid):
    proc = subprocess.run(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-Command",
         f"(Get-Process -Id {pid}).StartTime.ToUniversalTime().Ticks"],
        capture_output=True, text=True, env=clean_env())
    return proc.stdout.strip()


def lock_path(home):
    return home / "lane.lock"


def write_raw_lock(home, content_bytes):
    lock_path(home).write_bytes(content_bytes)


def wait_for_signal(path: Path, needles, timeout=10.0):
    """Wait until `path` (readlines) contains every string in `needles`."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            try:
                content = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                content = ""
            if all(n in content for n in needles):
                return True
        time.sleep(0.05)
    return False


# ---------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------
@pytest.fixture(scope="module")
def self_identity():
    pid = os.getpid()
    ticks = _ticks_for_pid(pid)
    assert re.match(r"\A[0-9]+\Z", ticks), f"could not resolve self ticks: {ticks!r}"
    return str(pid), ticks


@pytest.fixture(scope="module")
def acl_dump_script(tmp_path_factory):
    p = tmp_path_factory.mktemp("acl-dump") / "dump-acl.ps1"
    p.write_text(ACL_DUMP_SCRIPT, encoding="ascii")
    return p


@pytest.fixture(scope="module")
def current_user_sid():
    return current_sid()


@pytest.fixture
def lane_home(tmp_path):
    # NOT pre-created: this wrapper's own job is to create it (the
    # nonexistent -> create-and-ACL row of the four-row probe).
    return tmp_path / "lane"


@pytest.fixture
def kimi_stub(tmp_path):
    p = tmp_path / "fake-kimi.ps1"
    p.write_text(STUB_CLIENT_BODY, encoding="ascii")
    return p


@pytest.fixture
def stub_tools_dir(tmp_path):
    """A disposable copy of tools/ holding the wrapper, the real lock
    tool, and a STATEFUL validator stub - so $PSScriptRoot resolves the
    stub instead of the repository's own committed validator."""
    d = tmp_path / "tools-copy"
    d.mkdir()
    shutil.copy(str(SCRIPT), str(d / "new-kimi-lane-login.ps1"))
    shutil.copy(str(LOCK_SCRIPT), str(d / "kimi-lane-lock.ps1"))
    (d / "read-kimi-credential-state.ps1").write_text(STATEFUL_VALIDATOR_STUB_BODY, encoding="ascii")
    return d


def run_stub_wrapper(tools_dir, args, env=None, timeout=30):
    cmd = [POWERSHELL, "-NoProfile", "-NonInteractive", "-File",
           str(tools_dir / "new-kimi-lane-login.ps1")] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, env=clean_env(env), timeout=timeout)


# ---------------------------------------------------------------------
# Basic shape
# ---------------------------------------------------------------------
def test_script_exists():
    assert SCRIPT.is_file()


# ---------------------------------------------------------------------
# Parameter validation (exit 2, no mutation)
# ---------------------------------------------------------------------
def test_bad_owner_pid_exits_2_no_mutation(lane_home, kimi_stub, tmp_path):
    verdict_out = tmp_path / "verdict.json"
    result = run_wrapper(["-LaneHome", str(lane_home), "-OwnerPid", "not-a-pid",
                           "-OwnerStartTicksUtc", "1", "-KimiBinary", str(kimi_stub),
                           "-VerdictOut", str(verdict_out)])
    assert result.returncode == 2
    assert not lane_home.exists()
    assert not verdict_out.exists()


def test_owner_pid_zero_exits_2(lane_home, kimi_stub, tmp_path):
    verdict_out = tmp_path / "verdict.json"
    result = run_wrapper(["-LaneHome", str(lane_home), "-OwnerPid", "0",
                           "-OwnerStartTicksUtc", "1", "-KimiBinary", str(kimi_stub),
                           "-VerdictOut", str(verdict_out)])
    assert result.returncode == 2
    assert not lane_home.exists()


def test_bad_owner_start_ticks_exits_2_no_mutation(lane_home, kimi_stub, tmp_path):
    verdict_out = tmp_path / "verdict.json"
    result = run_wrapper(["-LaneHome", str(lane_home), "-OwnerPid", "1",
                           "-OwnerStartTicksUtc", "not-digits", "-KimiBinary", str(kimi_stub),
                           "-VerdictOut", str(verdict_out)])
    assert result.returncode == 2
    assert not lane_home.exists()


def test_blank_kimi_binary_exits_2(lane_home, tmp_path):
    verdict_out = tmp_path / "verdict.json"
    result = run_wrapper(["-LaneHome", str(lane_home), "-OwnerPid", "1",
                           "-OwnerStartTicksUtc", "1", "-KimiBinary", " ",
                           "-VerdictOut", str(verdict_out)])
    assert result.returncode == 2
    assert not lane_home.exists()


def test_binding_refusal_exits_nonzero_and_creates_nothing(lane_home, kimi_stub, tmp_path):
    verdict_out = tmp_path / "verdict.json"
    result = run_wrapper(["-LaneHome", str(lane_home), "-OwnerPid", "1",
                           "-OwnerStartTicksUtc", "1", "-KimiBinary", str(kimi_stub),
                           "-VerdictOut", str(verdict_out), "-NotARealParameter", "x"])
    assert result.returncode != 0
    assert not lane_home.exists()
    assert not verdict_out.exists()


# ---------------------------------------------------------------------
# The bootstrap exception: lane-home four-row probe (pre-lock)
# ---------------------------------------------------------------------
def test_fresh_build_creates_home_acquires_logs_in_and_succeeds(
        lane_home, kimi_stub, tmp_path, current_user_sid, acl_dump_script):
    verdict_out = tmp_path / "verdict.json"
    marker = tmp_path / "marker.txt"
    result = run_wrapper(
        ["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out)],
        env={"PARALLAX_TEST_STUB_MARKER_FILE": str(marker),
             "PARALLAX_TEST_STUB_WRITE_CREDENTIAL": "ok"})
    assert result.returncode == 0, (result.stdout, result.stderr)
    assert lane_home.is_dir()
    assert (lane_home / "credentials").is_dir()
    assert (lane_home / "credentials" / "kimi-code.json").is_file()
    assert marker.read_text().strip() == "1"

    line = accept_exactly_one_nonempty_line(verdict_out.read_text(encoding="ascii"))
    assert line is not None
    obj = json.loads(line)
    assert obj["status"] == "ok"

    home_acl = acl_dump(lane_home, acl_dump_script)
    assert home_acl["Protected"] is True
    assert len(home_acl["Rules"]) == 1
    rule = home_acl["Rules"][0]
    assert rule["Identity"] == current_user_sid
    assert rule["Rights"] == "FullControl"
    assert rule["Inheritance"] == "ContainerInherit, ObjectInherit"
    assert rule["Propagation"] == "None"
    assert rule["Type"] == "Allow"

    cred_dir_acl = acl_dump(lane_home / "credentials", acl_dump_script)
    assert cred_dir_acl["Protected"] is True
    assert len(cred_dir_acl["Rules"]) == 1
    crule = cred_dir_acl["Rules"][0]
    assert crule["Identity"] == current_user_sid
    assert crule["Rights"] == "FullControl"
    assert crule["Inheritance"] == "ContainerInherit, ObjectInherit"
    assert crule["Propagation"] == "None"
    assert crule["Type"] == "Allow"

    # The fake credential the CLIENT created under the protected directory
    # must carry an INHERITED current-SID rule - proof the inheritance
    # flags actually reached the file, not merely the parent.
    cred_file_acl = acl_dump(lane_home / "credentials" / "kimi-code.json", acl_dump_script)
    inherited = [r for r in cred_file_acl["Rules"]
                 if r["Identity"] == current_user_sid and r["IsInherited"] is True]
    assert inherited, cred_file_acl


def test_second_run_is_idempotent_and_skips_the_client(
        lane_home, kimi_stub, tmp_path, acl_dump_script):
    verdict_out = tmp_path / "verdict.json"
    marker = tmp_path / "marker.txt"
    common_env = {"PARALLAX_TEST_STUB_MARKER_FILE": str(marker),
                  "PARALLAX_TEST_STUB_WRITE_CREDENTIAL": "ok"}
    r1 = run_wrapper(["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
                       "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out)],
                      env=common_env)
    assert r1.returncode == 0, (r1.stdout, r1.stderr)
    assert marker.read_text().strip() == "1"

    home_acl_before = acl_dump(lane_home, acl_dump_script)
    cred_acl_before = acl_dump(lane_home / "credentials", acl_dump_script)

    r2 = run_wrapper(["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
                       "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out)],
                      env=common_env)
    assert r2.returncode == 0, (r2.stdout, r2.stderr)
    # Skipped: the marker count must NOT have incremented.
    assert marker.read_text().strip() == "1"

    home_acl_after = acl_dump(lane_home, acl_dump_script)
    cred_acl_after = acl_dump(lane_home / "credentials", acl_dump_script)
    assert home_acl_before == home_acl_after
    assert cred_acl_before == cred_acl_after

    line = accept_exactly_one_nonempty_line(verdict_out.read_text(encoding="ascii"))
    assert line is not None
    assert json.loads(line)["status"] == "ok"


def test_home_probe_fault_seam_exits_6_no_mutation(lane_home, kimi_stub, tmp_path):
    verdict_out = tmp_path / "verdict.json"
    marker = tmp_path / "marker.txt"
    result = run_wrapper(
        ["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out)],
        env={"PARALLAX_KIMI_LANE_LOGIN_HOME_PROBE_FAULT": "1",
             "PARALLAX_TEST_STUB_MARKER_FILE": str(marker)})
    assert result.returncode == 6
    assert ("PARALLAX_KIMI_LANE_LOGIN_HOME_PROBE_FAULT injected: "
            "simulated lane-home probe failure") in result.stderr
    assert not lane_home.exists()
    assert not verdict_out.exists()
    assert not marker.exists()


def test_home_probe_non_directory_collision_exits_6_bytes_and_acl_unchanged(
        lane_home, kimi_stub, tmp_path, acl_dump_script):
    lane_home.parent.mkdir(parents=True, exist_ok=True)
    lane_home.write_bytes(b"not a directory")
    before_bytes = lane_home.read_bytes()
    before_acl = acl_dump(lane_home, acl_dump_script)

    verdict_out = tmp_path / "verdict.json"
    result = run_wrapper(["-LaneHome", str(lane_home), "-OwnerPid", "1",
                           "-OwnerStartTicksUtc", "1", "-KimiBinary", str(kimi_stub),
                           "-VerdictOut", str(verdict_out)])
    assert result.returncode == 6
    assert lane_home.read_bytes() == before_bytes
    assert acl_dump(lane_home, acl_dump_script) == before_acl
    assert not verdict_out.exists()


# ---------------------------------------------------------------------
# Credentials four-row probe (post-lock)
# ---------------------------------------------------------------------
def test_credentials_probe_fault_seam_exits_6_releases_lock(lane_home, kimi_stub, tmp_path):
    verdict_out = tmp_path / "verdict.json"
    marker = tmp_path / "marker.txt"
    result = run_wrapper(
        ["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out)],
        env={"PARALLAX_KIMI_LANE_LOGIN_CREDENTIALS_PROBE_FAULT": "1",
             "PARALLAX_TEST_STUB_MARKER_FILE": str(marker)})
    assert result.returncode == 6
    assert ("PARALLAX_KIMI_LANE_LOGIN_CREDENTIALS_PROBE_FAULT injected: "
            "simulated credentials probe failure") in result.stderr
    assert not verdict_out.exists()
    assert not marker.exists()
    # The home itself WAS created and ACL'd (pre-lock steps ran fine);
    # only the credentials probe, which runs after acquiring, faulted.
    assert lane_home.is_dir()

    status = run_lock(["-Status", "-LaneHome", str(lane_home)])
    assert status.returncode == 0
    assert json.loads(status.stdout) == {"state": "free"}


def test_credentials_probe_non_directory_collision_exits_6_preserved_and_released(
        lane_home, kimi_stub, tmp_path, acl_dump_script):
    # Build the home first with a clean run, then plant a file where the
    # credentials directory would go, and run again.
    verdict_out = tmp_path / "verdict.json"
    marker = tmp_path / "marker.txt"
    r1 = run_wrapper(
        ["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out)],
        env={"PARALLAX_TEST_STUB_MARKER_FILE": str(marker),
             "PARALLAX_TEST_STUB_WRITE_CREDENTIAL": "ok"})
    assert r1.returncode == 0, (r1.stdout, r1.stderr)

    cred_dir = lane_home / "credentials"
    shutil.rmtree(cred_dir)
    cred_dir.write_bytes(b"obstruction")
    before_bytes = cred_dir.read_bytes()
    before_acl = acl_dump(cred_dir, acl_dump_script)

    verdict_out2 = tmp_path / "verdict2.json"
    r2 = run_wrapper(
        ["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out2)],
        env={"PARALLAX_TEST_STUB_MARKER_FILE": str(marker)})
    assert r2.returncode == 6
    assert cred_dir.read_bytes() == before_bytes
    assert acl_dump(cred_dir, acl_dump_script) == before_acl
    assert not verdict_out2.exists()
    # No second client invocation.
    assert marker.read_text().strip() == "1"

    status = run_lock(["-Status", "-LaneHome", str(lane_home)])
    assert status.returncode == 0
    assert json.loads(status.stdout) == {"state": "free"}


# ---------------------------------------------------------------------
# Validator failure: two opposing oracles, both call positions
# ---------------------------------------------------------------------
def test_pre_client_validator_failure_nonzero_valid_line_exits_6_no_client(
        stub_tools_dir, lane_home, kimi_stub, tmp_path):
    verdict_out = tmp_path / "verdict.json"
    marker = tmp_path / "marker.txt"
    counter = tmp_path / "counter.txt"
    result = run_stub_wrapper(
        stub_tools_dir,
        ["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out), "-Force"],
        env={"PARALLAX_TEST_VALIDATOR_COUNTER_FILE": str(counter),
             "PARALLAX_TEST_VALIDATOR_FAIL_ON_CALL": "1",
             "PARALLAX_TEST_VALIDATOR_FAIL_MODE": "nonzero-valid",
             "PARALLAX_TEST_STUB_MARKER_FILE": str(marker)})
    assert result.returncode == 6, (result.stdout, result.stderr)
    assert not verdict_out.exists()
    assert not marker.exists()

    status = run_lock(["-Status", "-LaneHome", str(lane_home)])
    assert status.returncode == 0
    assert json.loads(status.stdout) == {"state": "free"}


def test_pre_client_validator_failure_exit0_malformed_exits_6_no_client(
        stub_tools_dir, lane_home, kimi_stub, tmp_path):
    verdict_out = tmp_path / "verdict.json"
    marker = tmp_path / "marker.txt"
    counter = tmp_path / "counter.txt"
    result = run_stub_wrapper(
        stub_tools_dir,
        ["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out), "-Force"],
        env={"PARALLAX_TEST_VALIDATOR_COUNTER_FILE": str(counter),
             "PARALLAX_TEST_VALIDATOR_FAIL_ON_CALL": "1",
             "PARALLAX_TEST_VALIDATOR_FAIL_MODE": "exit0-malformed",
             "PARALLAX_TEST_STUB_MARKER_FILE": str(marker)})
    assert result.returncode == 6, (result.stdout, result.stderr)
    assert not verdict_out.exists()
    assert not marker.exists()


def test_post_client_validator_failure_nonzero_valid_line_exits_6_client_ran(
        stub_tools_dir, lane_home, kimi_stub, tmp_path):
    verdict_out = tmp_path / "verdict.json"
    marker = tmp_path / "marker.txt"
    counter = tmp_path / "counter.txt"
    result = run_stub_wrapper(
        stub_tools_dir,
        ["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out), "-Force"],
        env={"PARALLAX_TEST_VALIDATOR_COUNTER_FILE": str(counter),
             "PARALLAX_TEST_VALIDATOR_FAIL_ON_CALL": "2",
             "PARALLAX_TEST_VALIDATOR_FAIL_MODE": "nonzero-valid",
             "PARALLAX_TEST_STUB_MARKER_FILE": str(marker)})
    assert result.returncode == 6, (result.stdout, result.stderr)
    assert not verdict_out.exists()
    # The client DID run (this is the post-client position).
    assert marker.read_text().strip() == "1"

    status = run_lock(["-Status", "-LaneHome", str(lane_home)])
    assert status.returncode == 0
    assert json.loads(status.stdout) == {"state": "free"}


def test_post_client_validator_failure_exit0_malformed_exits_6_client_ran(
        stub_tools_dir, lane_home, kimi_stub, tmp_path):
    verdict_out = tmp_path / "verdict.json"
    marker = tmp_path / "marker.txt"
    counter = tmp_path / "counter.txt"
    result = run_stub_wrapper(
        stub_tools_dir,
        ["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out), "-Force"],
        env={"PARALLAX_TEST_VALIDATOR_COUNTER_FILE": str(counter),
             "PARALLAX_TEST_VALIDATOR_FAIL_ON_CALL": "2",
             "PARALLAX_TEST_VALIDATOR_FAIL_MODE": "exit0-malformed",
             "PARALLAX_TEST_STUB_MARKER_FILE": str(marker)})
    assert result.returncode == 6, (result.stdout, result.stderr)
    assert not verdict_out.exists()
    assert marker.read_text().strip() == "1"


# ---------------------------------------------------------------------
# Defect 2 (scalar `fields` passes an array check) and defect 3 (blank
# lines discarded before counting), at BOTH validator call positions -
# each must FAIL before the fix and pass after.
# ---------------------------------------------------------------------
@pytest.mark.parametrize("fail_on_call,client_ran", [(1, False), (2, True)])
def test_validator_scalar_fields_rejected_at_both_call_positions(
        stub_tools_dir, lane_home, kimi_stub, tmp_path, fail_on_call, client_ran):
    verdict_out = tmp_path / "verdict.json"
    marker = tmp_path / "marker.txt"
    counter = tmp_path / "counter.txt"
    result = run_stub_wrapper(
        stub_tools_dir,
        ["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out), "-Force"],
        env={"PARALLAX_TEST_VALIDATOR_COUNTER_FILE": str(counter),
             "PARALLAX_TEST_VALIDATOR_FAIL_ON_CALL": str(fail_on_call),
             "PARALLAX_TEST_VALIDATOR_FAIL_MODE": "scalar-fields",
             "PARALLAX_TEST_STUB_MARKER_FILE": str(marker)})
    assert result.returncode == 6, (result.stdout, result.stderr)
    assert not verdict_out.exists()
    assert marker.exists() == client_ran


@pytest.mark.parametrize("fail_on_call,client_ran", [(1, False), (2, True)])
def test_validator_blank_line_padded_stdout_rejected_at_both_call_positions(
        stub_tools_dir, lane_home, kimi_stub, tmp_path, fail_on_call, client_ran):
    verdict_out = tmp_path / "verdict.json"
    marker = tmp_path / "marker.txt"
    counter = tmp_path / "counter.txt"
    result = run_stub_wrapper(
        stub_tools_dir,
        ["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out), "-Force"],
        env={"PARALLAX_TEST_VALIDATOR_COUNTER_FILE": str(counter),
             "PARALLAX_TEST_VALIDATOR_FAIL_ON_CALL": str(fail_on_call),
             "PARALLAX_TEST_VALIDATOR_FAIL_MODE": "blank-line-padded",
             "PARALLAX_TEST_STUB_MARKER_FILE": str(marker)})
    assert result.returncode == 6, (result.stdout, result.stderr)
    assert not verdict_out.exists()
    assert marker.exists() == client_ran


@pytest.mark.parametrize("fail_on_call,client_ran", [(1, False), (2, True)])
def test_validator_case_variant_result_keys_rejected_at_both_call_positions(
        stub_tools_dir, lane_home, kimi_stub, tmp_path, fail_on_call, client_ran):
    """The frozen interface is exactly `status`, `detail`, `fields`. The
    pair-table oracle varies only the VALUES, so it leaves the property-set
    comparison untested: reverting that comparison to case-insensitive
    would keep it green. This varies the KEYS."""
    verdict_out = tmp_path / "verdict.json"
    marker = tmp_path / "marker.txt"
    counter = tmp_path / "counter.txt"
    result = run_stub_wrapper(
        stub_tools_dir,
        ["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out), "-Force"],
        env={"PARALLAX_TEST_VALIDATOR_COUNTER_FILE": str(counter),
             "PARALLAX_TEST_VALIDATOR_FAIL_ON_CALL": str(fail_on_call),
             "PARALLAX_TEST_VALIDATOR_FAIL_MODE": "case-variant-keys",
             "PARALLAX_TEST_STUB_MARKER_FILE": str(marker)})
    assert result.returncode == 6, (result.stdout, result.stderr)
    assert not verdict_out.exists()
    assert marker.exists() == client_ran


@pytest.mark.parametrize("fail_on_call,client_ran", [(1, False), (2, True)])
def test_validator_case_variant_pair_rejected_at_both_call_positions(
        stub_tools_dir, lane_home, kimi_stub, tmp_path, fail_on_call, client_ran):
    """A pairing outside the frozen table is VALIDATOR FAILURE, never a
    credential state. PowerShell's -eq is case-insensitive, so a validator
    emitting "OK"/"Valid" satisfied the table and this wrapper then routed
    on a status the table does not contain."""
    verdict_out = tmp_path / "verdict.json"
    marker = tmp_path / "marker.txt"
    counter = tmp_path / "counter.txt"
    result = run_stub_wrapper(
        stub_tools_dir,
        ["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out), "-Force"],
        env={"PARALLAX_TEST_VALIDATOR_COUNTER_FILE": str(counter),
             "PARALLAX_TEST_VALIDATOR_FAIL_ON_CALL": str(fail_on_call),
             "PARALLAX_TEST_VALIDATOR_FAIL_MODE": "case-variant-pair",
             "PARALLAX_TEST_STUB_MARKER_FILE": str(marker)})
    assert result.returncode == 6, (result.stdout, result.stderr)
    assert not verdict_out.exists()
    assert marker.exists() == client_ran


# ---------------------------------------------------------------------
# Defect 4 (a failed capture read must be validator failure, not empty
# stderr). The seam deletes the validator's own real stderr capture file
# right before Invoke-CredentialValidator reads it (stdout is left
# genuinely readable), producing a real Get-Content failure rather than a
# simulated one - isolated to stderr so this oracle cannot be satisfied by
# a coincidental empty-stdout rejection from the defect-3 fix instead.
# Both files share one Invoke-CredentialValidator function, so exercising
# it once proves the fix for every call position that function serves.
# ---------------------------------------------------------------------
def test_capture_read_fault_seam_is_validator_failure(lane_home, kimi_stub, tmp_path):
    verdict_out = tmp_path / "verdict.json"
    marker = tmp_path / "marker.txt"
    result = run_wrapper(
        ["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out)],
        env={"PARALLAX_KIMI_CREDENTIAL_VALIDATOR_CAPTURE_READ_FAULT": "1",
             "PARALLAX_TEST_STUB_MARKER_FILE": str(marker)})
    assert result.returncode == 6, (result.stdout, result.stderr)
    assert not verdict_out.exists()
    # The pre-client validator call is what the wrapper reaches first, so
    # a read failure there means the client is never invoked.
    assert not marker.exists()


# ---------------------------------------------------------------------
# Post-run verdict decides the exit code, in BOTH directions
# ---------------------------------------------------------------------
@pytest.mark.parametrize("mode", ["none", "malformed", "unreadable"])
def test_client_exit_0_leaving_bad_credential_fails_with_6(lane_home, kimi_stub, tmp_path, mode):
    expected_status = {"none": "absent", "malformed": "malformed", "unreadable": "unreadable"}[mode]
    verdict_out = tmp_path / "verdict.json"
    result = run_wrapper(
        ["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out)],
        env={"PARALLAX_TEST_STUB_WRITE_CREDENTIAL": mode,
             "PARALLAX_TEST_STUB_EXIT_CODE": "0"})
    assert result.returncode == 6, (result.stdout, result.stderr)
    # Step 8 writes the verdict whenever the post-client validator call
    # itself SUCCEEDED structurally - the exit code is a separate
    # decision from whether -VerdictOut carries the (non-ok) verdict.
    line = accept_exactly_one_nonempty_line(verdict_out.read_text(encoding="ascii"))
    assert line is not None
    assert json.loads(line)["status"] == expected_status


def test_client_exit_nonzero_with_ok_credential_succeeds_with_0(lane_home, kimi_stub, tmp_path):
    """Without this test an implementation that simply propagates the
    client's own exit code would pass every other listed case."""
    verdict_out = tmp_path / "verdict.json"
    result = run_wrapper(
        ["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out)],
        env={"PARALLAX_TEST_STUB_WRITE_CREDENTIAL": "ok",
             "PARALLAX_TEST_STUB_EXIT_CODE": "5"})
    assert result.returncode == 0, (result.stdout, result.stderr)
    line = accept_exactly_one_nonempty_line(verdict_out.read_text(encoding="ascii"))
    assert line is not None
    assert json.loads(line)["status"] == "ok"


# ---------------------------------------------------------------------
# Environment restoration, asserted INSIDE the same shell
# ---------------------------------------------------------------------
def test_kimi_code_home_restored_previously_unset(lane_home, kimi_stub, tmp_path):
    verdict_out = tmp_path / "verdict.json"
    driver = tmp_path / "driver.ps1"
    driver.write_text(
        f'Remove-Item Env:KIMI_CODE_HOME -ErrorAction SilentlyContinue\n'
        f'& "{SCRIPT}" -LaneHome "{lane_home}" -OwnerPid 1 -OwnerStartTicksUtc 1 '
        f'-KimiBinary "{kimi_stub}" -VerdictOut "{verdict_out}"\n'
        f'Write-Output "WASSET=[$(Test-Path Env:KIMI_CODE_HOME)]"\n'
        f'Write-Output "VALUE=[$env:KIMI_CODE_HOME]"\n',
        encoding="ascii")
    full_env = clean_env({"PARALLAX_TEST_STUB_WRITE_CREDENTIAL": "ok"})
    full_env.pop("KIMI_CODE_HOME", None)
    result = subprocess.run([POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(driver)],
                             capture_output=True, text=True, env=full_env, timeout=30)
    assert "WASSET=[False]" in result.stdout, (result.stdout, result.stderr)
    # Never references the real user credential location.
    assert "~/.kimi-code/credentials" not in (result.stdout + result.stderr)
    assert ".kimi-code\\credentials" not in (result.stdout + result.stderr)


def test_kimi_code_home_restored_previously_set(lane_home, kimi_stub, tmp_path):
    verdict_out = tmp_path / "verdict.json"
    sentinel = "sentinel-previous-value-" + new_token()
    driver = tmp_path / "driver.ps1"
    driver.write_text(
        f'$env:KIMI_CODE_HOME = "{sentinel}"\n'
        f'& "{SCRIPT}" -LaneHome "{lane_home}" -OwnerPid 1 -OwnerStartTicksUtc 1 '
        f'-KimiBinary "{kimi_stub}" -VerdictOut "{verdict_out}"\n'
        f'Write-Output "VALUE=[$env:KIMI_CODE_HOME]"\n',
        encoding="ascii")
    full_env = clean_env({"PARALLAX_TEST_STUB_WRITE_CREDENTIAL": "ok"})
    result = subprocess.run([POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(driver)],
                             capture_output=True, text=True, env=full_env, timeout=30)
    assert f"VALUE=[{sentinel}]" in result.stdout, (result.stdout, result.stderr)


def test_wrapper_never_touches_real_userprofile_credential(tmp_path, kimi_stub):
    """Full end-to-end proof: point a FAKE $env:USERPROFILE at a disposable
    directory (never the real one), plant a fake "user" credential outside
    the lane home, run the wrapper using its DEFAULT -LaneHome and
    -KimiBinary (both derived from $env:USERPROFILE), and require the
    planted file to be byte-identical afterwards."""
    fake_profile = tmp_path / "fake-userprofile"
    fake_profile.mkdir()
    user_cred_dir = fake_profile / ".kimi-code" / "credentials"
    user_cred_dir.mkdir(parents=True)
    user_cred_file = user_cred_dir / "kimi-code.json"
    user_cred_file.write_text('{"access_token":"real-user-token","refresh_token":"r","expires_at":1}',
                               encoding="ascii")
    before = user_cred_file.read_bytes()

    bin_dir = fake_profile / ".kimi-code" / "bin"
    bin_dir.mkdir(parents=True)
    default_kimi_path = bin_dir / "kimi.exe"
    # PowerShell's `&` dispatches by extension, not literal name - a
    # ".ps1" stub works the same as a real exe would for this purpose.
    stub_as_exe = bin_dir / "kimi.ps1"
    stub_as_exe.write_text(STUB_CLIENT_BODY, encoding="ascii")

    verdict_out = tmp_path / "verdict.json"
    full_env = clean_env({"USERPROFILE": str(fake_profile),
                           "PARALLAX_TEST_STUB_WRITE_CREDENTIAL": "ok"})
    cmd = [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(SCRIPT),
           "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
           "-KimiBinary", str(stub_as_exe), "-VerdictOut", str(verdict_out)]
    result = subprocess.run(cmd, capture_output=True, text=True, env=full_env, timeout=30)
    assert result.returncode == 0, (result.stdout, result.stderr)

    assert user_cred_file.read_bytes() == before
    lane_home = fake_profile / ".parallax-kimi-review"
    assert lane_home.is_dir()
    assert (lane_home / "credentials" / "kimi-code.json").is_file()
    assert not default_kimi_path.exists()  # never referenced/created


def write_held_lock(home, debate_id, owner_pid, owner_start_ticks_utc, nonce, host=None):
    rec = {
        "version": 1,
        "state": "held",
        "host": host or os.environ.get("COMPUTERNAME", ""),
        "ownerPid": int(owner_pid),
        "ownerStartTicksUtc": str(owner_start_ticks_utc),
        "debateId": debate_id,
        "nonce": nonce,
        "debateHome": str(home),
        "acquiredTicksUtc": "111111111",
    }
    lock_path(home).write_bytes(json.dumps(rec).encode("utf-8"))
    return rec


# ---------------------------------------------------------------------
# Lock acquired before any credential read; released only when acquired
# ---------------------------------------------------------------------
def test_live_holder_contention_exits_3_no_client_no_release(
        lane_home, kimi_stub, tmp_path, self_identity):
    pid, ticks = self_identity
    lane_home.mkdir()
    held_debate = new_token()
    held_nonce = new_token()
    rec = write_held_lock(lane_home, held_debate, pid, ticks, held_nonce)
    before = lock_path(lane_home).read_bytes()

    verdict_out = tmp_path / "verdict.json"
    marker = tmp_path / "marker.txt"
    result = run_wrapper(
        ["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out)],
        env={"PARALLAX_TEST_STUB_MARKER_FILE": str(marker)})
    assert result.returncode == 3, (result.stdout, result.stderr)
    assert not marker.exists()
    assert not verdict_out.exists()
    # No release happened: the lock file is byte-identical to the
    # untouched held record this test seeded.
    assert lock_path(lane_home).read_bytes() == before
    # The lock's own exact holder diagnostic reaches the wrapper's stderr
    # unchanged - the wrapper's default WaitSeconds/PollSeconds are the
    # lock tool's own defaults (0 / 2), so contention against a LIVE
    # same-identity... no, a DIFFERENT identity... holder is immediate.
    assert (f"contended: holder pid {pid} ticks {ticks} debate {held_debate}, "
            f"liveness LIVE, wait budget 0s expired") in result.stderr


def test_dead_holder_reclaimed_reports_lock_diagnostic_and_wrapper_succeeds(
        lane_home, kimi_stub, tmp_path):
    lane_home.mkdir()
    dead_debate = new_token()
    dead_nonce = new_token()
    dead_rec = write_held_lock(lane_home, dead_debate, 999999, "111111111", dead_nonce)

    verdict_out = tmp_path / "verdict.json"
    result = run_wrapper(
        ["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out)],
        env={"PARALLAX_TEST_STUB_WRITE_CREDENTIAL": "ok"})
    assert result.returncode == 0, (result.stdout, result.stderr)
    assert (f"reclaimed a dead holder: pid {dead_rec['ownerPid']} "
            f"ticks {dead_rec['ownerStartTicksUtc']} debate {dead_rec['debateId']} "
            f"home {dead_rec['debateHome']}") in result.stderr


def test_malformed_lock_record_exits_4(lane_home, kimi_stub, tmp_path):
    lane_home.mkdir()
    write_raw_lock(lane_home, b"not json at all")
    verdict_out = tmp_path / "verdict.json"
    result = run_wrapper(["-LaneHome", str(lane_home), "-OwnerPid", "1",
                           "-OwnerStartTicksUtc", "1", "-KimiBinary", str(kimi_stub),
                           "-VerdictOut", str(verdict_out)])
    assert result.returncode == 4
    assert not verdict_out.exists()


# ---------------------------------------------------------------------
# Stream mechanism: the client's streams are INHERITED and UNTOUCHED.
# The oracle is TEMPORAL - a wrapper that buffered both streams and
# replayed them at exit would pass a mere both-streams-emitted check.
# ---------------------------------------------------------------------
def test_client_streams_are_temporally_inherited_and_absent_from_verdict(
        lane_home, kimi_stub, tmp_path):
    lane_home.mkdir()
    verdict_out = tmp_path / "verdict.json"
    release_signal = tmp_path / "release.txt"
    proc = start_wrapper_bg(
        ["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out)],
        env={"PARALLAX_TEST_STUB_BLOCK_UNTIL": str(release_signal),
             "PARALLAX_TEST_STUB_WRITE_CREDENTIAL": "ok"})
    import threading
    out_lines, err_lines = [], []

    def reader(stream, sink):
        for line in iter(stream.readline, ""):
            sink.append(line)

    t_out = threading.Thread(target=reader, args=(proc.stdout, out_lines))
    t_err = threading.Thread(target=reader, args=(proc.stderr, err_lines))
    t_out.start()
    t_err.start()
    try:
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            if (any("STUB-STDOUT-MARKER" in l for l in out_lines) and
                    any("STUB-STDERR-MARKER" in l for l in err_lines)):
                break
            time.sleep(0.05)
        else:
            proc.kill()
            pytest.fail("both stream markers never arrived within 10s")

        # The child is still blocked at this point - the parent observed
        # both markers BEFORE the child was allowed to finish.
        time.sleep(0.5)
        assert proc.poll() is None, "the stub exited before it was released"
    finally:
        release_signal.write_text("go", encoding="ascii")
        proc.wait(timeout=15)
        t_out.join(timeout=5)
        t_err.join(timeout=5)

    assert proc.returncode == 0, ("".join(out_lines), "".join(err_lines))
    verdict_text = verdict_out.read_text(encoding="ascii")
    assert "STUB-STDOUT-MARKER" not in verdict_text
    assert "STUB-STDERR-MARKER" not in verdict_text


# ---------------------------------------------------------------------
# Release-failure precedence, both directions - the record is freed or
# displaced by an OUTSIDE actor between acquire and this wrapper's own
# release, using the identity -Status exposes.
# ---------------------------------------------------------------------
def _displace_lock_externally(lane_home, timeout=10):
    """Poll -Status until a held record appears, then free it directly
    with the real lock tool using the identity -Status exposes - an
    outside actor displacing the record between this wrapper's acquire
    and its own release."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        status = run_lock(["-Status", "-LaneHome", str(lane_home)])
        if status.returncode == 0:
            obj = json.loads(status.stdout)
            if obj.get("state") == "held":
                rel = run_lock(["-Release", "-LaneHome", str(lane_home),
                                 "-DebateId", obj["debateId"], "-OwnerPid", str(obj["ownerPid"]),
                                 "-OwnerStartTicksUtc", obj["ownerStartTicksUtc"],
                                 "-Nonce", obj["nonce"]])
                return rel.returncode == 0
        time.sleep(0.1)
    return False


def test_release_refusal_propagates_when_main_operation_succeeded(
        lane_home, kimi_stub, tmp_path):
    lane_home.mkdir()
    verdict_out = tmp_path / "verdict.json"
    release_signal = tmp_path / "release.txt"
    proc = start_wrapper_bg(
        ["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out)],
        env={"PARALLAX_TEST_STUB_BLOCK_UNTIL": str(release_signal),
             "PARALLAX_TEST_STUB_WRITE_CREDENTIAL": "ok"})
    try:
        displaced = _displace_lock_externally(lane_home)
        assert displaced, "could not externally displace the held lock in time"
    finally:
        release_signal.write_text("go", encoding="ascii")
    stdout, stderr = proc.communicate(timeout=15)

    # The main operation succeeded (a genuinely ok credential was
    # produced) but this wrapper's OWN release then found the record
    # already free - propagated as exit 5.
    assert proc.returncode == 5, (stdout, stderr)
    line = accept_exactly_one_nonempty_line(verdict_out.read_text(encoding="ascii"))
    assert line is not None
    assert json.loads(line)["status"] == "ok"


def test_release_refusal_does_not_override_a_preceding_failure(
        lane_home, kimi_stub, tmp_path):
    lane_home.mkdir()
    verdict_out = tmp_path / "verdict.json"
    release_signal = tmp_path / "release.txt"
    proc = start_wrapper_bg(
        ["-LaneHome", str(lane_home), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict_out)],
        env={"PARALLAX_TEST_STUB_BLOCK_UNTIL": str(release_signal),
             "PARALLAX_TEST_STUB_WRITE_CREDENTIAL": "none"})
    try:
        displaced = _displace_lock_externally(lane_home)
        assert displaced, "could not externally displace the held lock in time"
    finally:
        release_signal.write_text("go", encoding="ascii")
    stdout, stderr = proc.communicate(timeout=15)

    # The main operation already failed (client left the credential
    # absent -> 6), and the release ALSO failed - the ORIGINAL code must
    # be preserved, never overwritten by the release failure.
    assert proc.returncode == 6, (stdout, stderr)
    # The credential WAS structurally classified (absent is a completed
    # measurement), so -VerdictOut still carries it; only the exit code
    # reflects the failure.
    line = accept_exactly_one_nonempty_line(verdict_out.read_text(encoding="ascii"))
    assert line is not None
    assert json.loads(line)["status"] == "absent"


# ---------------------------------------------------------------------
# Exit-code exhaustiveness: every one of the six wrapper-level exit codes
# must be independently reachable, or this assertion is passing by
# having verified nothing.
# ---------------------------------------------------------------------
def test_exit_code_exhaustiveness(tmp_path, kimi_stub, self_identity):
    observed = set()
    pid, ticks = self_identity

    # 0
    home0 = tmp_path / "h0"
    r = run_wrapper(["-LaneHome", str(home0), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
                      "-KimiBinary", str(kimi_stub), "-VerdictOut", str(tmp_path / "v0.json")],
                     env={"PARALLAX_TEST_STUB_WRITE_CREDENTIAL": "ok"})
    observed.add(r.returncode)

    # 2
    home2 = tmp_path / "h2"
    r = run_wrapper(["-LaneHome", str(home2), "-OwnerPid", "0", "-OwnerStartTicksUtc", "1",
                      "-KimiBinary", str(kimi_stub), "-VerdictOut", str(tmp_path / "v2.json")])
    observed.add(r.returncode)

    # 3
    home3 = tmp_path / "h3"
    home3.mkdir()
    write_held_lock(home3, new_token(), pid, ticks, new_token())
    r = run_wrapper(["-LaneHome", str(home3), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
                      "-KimiBinary", str(kimi_stub), "-VerdictOut", str(tmp_path / "v3.json")])
    observed.add(r.returncode)

    # 4
    home4 = tmp_path / "h4"
    home4.mkdir()
    write_raw_lock(home4, b"not json")
    r = run_wrapper(["-LaneHome", str(home4), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
                      "-KimiBinary", str(kimi_stub), "-VerdictOut", str(tmp_path / "v4.json")])
    observed.add(r.returncode)

    # 5
    home5 = tmp_path / "h5"
    home5.mkdir()
    verdict5 = tmp_path / "v5.json"
    release5 = tmp_path / "release5.txt"
    proc = start_wrapper_bg(
        ["-LaneHome", str(home5), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
         "-KimiBinary", str(kimi_stub), "-VerdictOut", str(verdict5)],
        env={"PARALLAX_TEST_STUB_BLOCK_UNTIL": str(release5),
             "PARALLAX_TEST_STUB_WRITE_CREDENTIAL": "ok"})
    try:
        assert _displace_lock_externally(home5)
    finally:
        release5.write_text("go", encoding="ascii")
    proc.communicate(timeout=15)
    observed.add(proc.returncode)

    # 6
    home6 = tmp_path / "h6"
    home6.mkdir()
    home6_lane = home6 / "lane"
    home6_lane.write_bytes(b"not a directory")
    r = run_wrapper(["-LaneHome", str(home6_lane), "-OwnerPid", "1", "-OwnerStartTicksUtc", "1",
                      "-KimiBinary", str(kimi_stub), "-VerdictOut", str(tmp_path / "v6.json")])
    observed.add(r.returncode)

    assert observed <= {0, 2, 3, 4, 5, 6}, observed
    assert observed == {0, 2, 3, 4, 5, 6}, observed
