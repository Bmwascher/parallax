"""Live gate for the OS behaviour the kimi-code lane lock is built on
(Task 4, 2026-08-01 lane-credential-and-lock plan).

Task 3's tests (test_kimi_lane_lock.py) are the implementation oracle for
tools/kimi-lane-lock.ps1's own record format and state table. THIS module
proves the Windows file-locking assumptions underneath that implementation
using raw .NET FileStream operations - it is not a regression gate for the
implemented record format, and it does not re-test the lock tool's state
table.

WINDOWS ONLY, whole module - the sequence under test (CreateNew/Open
semantics, an exclusive FileShare.None handle, process liveness) is real
Windows file-locking behaviour that does not exist the same way elsewhere.
The module-level guard is `os.name != "nt"` ONLY, unlike the sibling
pattern at test_codex_context_probe.py:35-67 and test_kimi_lane_lock.py's
own guard, both of which also skip when no PowerShell host resolves. Here
a resolvable-but-missing host is a FAILED measurement, not a skipped one:
"an unmade, failed, or unreadable measurement is never a clean one. A
guard that cannot be evaluated REFUSES; it never skips. A live gate whose
setup fails is a FAILED gate, never a skipped branch." Measurement 20's
divergence test in particular needs BOTH powershell.exe and pwsh.exe to
have actually run before it can assert anything about how they differ -
an unavailable host there fails the gate outright.
"""
import importlib.util
import json
import os
import shutil
import subprocess
import time
import uuid
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "tools" / "kimi-lane-lock.ps1"


def _load_exact_line_module():
    path = REPO / "evals" / "tools" / "exact_line.py"
    spec = importlib.util.spec_from_file_location("exact_line", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


accept_exactly_one_nonempty_line = _load_exact_line_module().accept_exactly_one_nonempty_line

# Same resolution chain as the sibling live-lock suite (PARALLAX_PS_HOST,
# else whichever host is on PATH), but the module guard below drops the
# "no host resolved" branch: this file fails those cases per-test instead
# of skipping the whole module.
POWERSHELL = (os.environ.get("PARALLAX_PS_HOST")
              or shutil.which("powershell") or shutil.which("pwsh"))

pytestmark = pytest.mark.skipif(
    os.name != "nt",
    reason="the lock protocol's exclusive-handle and crash-recovery "
           "guarantees are Windows file-locking behaviour")


def ps_host():
    """The host PARALLAX_PS_HOST selects for THIS invocation (tests 1-4
    below run against exactly one host at a time; the plan's own
    verification runs this module twice, once per host, each time setting
    PARALLAX_PS_HOST before the pytest invocation). A host that fails to
    resolve is a setup failure, not a reason to skip."""
    if POWERSHELL is None:
        pytest.fail("no PowerShell host resolved (PARALLAX_PS_HOST unset "
                    "and neither powershell nor pwsh is on PATH); a live "
                    "gate whose setup fails is a failed gate, never a "
                    "skipped branch")
    return POWERSHELL


def required_hosts():
    """Measurement 20 compares powershell.exe against pwsh.exe directly,
    independent of whichever host PARALLAX_PS_HOST selects for this
    invocation. Both literal binaries are required; either missing FAILS
    the test rather than reading as (vacuous) divergence."""
    resolved = {}
    for name in ("powershell.exe", "pwsh.exe"):
        found = shutil.which(name)
        if found is None:
            pytest.fail(f"{name} is not available on PATH; both hosts are "
                        "required for the measurement-20 divergence gate "
                        "and an unavailable host fails it rather than "
                        "reading as a skip")
        resolved[name] = found
    return resolved


def run_dotnet(host, script, timeout=30):
    """Run a raw PowerShell/.NET snippet - never the lock tool - under
    `host`."""
    return subprocess.run(
        [host, "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, text=True, timeout=timeout)


def run_lock_tool(host, args, timeout=30):
    cmd = [host, "-NoProfile", "-NonInteractive", "-File", str(SCRIPT)] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def wait_for_signal(path: Path, timeout: float = 10.0):
    """Bounded wait for an observed ready marker. The bound only limits
    how long we wait to abort cleanly - it never stands in for the
    observation itself; a timeout here means the state under test was
    never proven, not that it probably happened."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            try:
                content = path.read_text(encoding="ascii").strip()
                if content:
                    return content
            except OSError:
                pass
        time.sleep(0.05)
    return None


def byte_array_literal(data: bytes) -> str:
    """`[byte[]](1,2,3,...)` - avoids embedding raw JSON/quote characters
    inside a -Command string."""
    return "[byte[]](" + ",".join(str(b) for b in data) + ")"


# ---------------------------------------------------------------------
# 1. CreateNew/Open semantics.
# ---------------------------------------------------------------------
def test_createnew_then_open_semantics(tmp_path):
    # A typed `catch [System.IO.IOException]` clause, exactly the idiom
    # tools/kimi-lane-lock.ps1 itself uses (Open-ForAcquire). PowerShell
    # wraps a constructor's thrown exception in a
    # MethodInvocationException for a plain `catch { }`, but a TYPED
    # catch clause matches against the real (unwrapped) exception -
    # measured live: a generic catch here reported
    # "MethodInvocationException" for the identical CreateNew collision
    # that a typed catch correctly reports as IOException. Production
    # relies on the typed form, so that is what this gate proves.
    host = ps_host()
    path = tmp_path / "createnew.bin"
    script = (
        f"$path = '{path}'; $r = @();"
        " try { $fs = New-Object System.IO.FileStream($path, [System.IO.FileMode]::CreateNew,"
        " [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None);"
        " $r += 'fresh:OK'; $fs.Close() } catch [System.IO.IOException] { $r += 'fresh:IOException' }"
        " catch { $r += ('fresh:OTHER:' + $_.Exception.GetType().Name) };"
        " try { $fs = New-Object System.IO.FileStream($path, [System.IO.FileMode]::CreateNew,"
        " [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None);"
        " $r += 'existing:OK'; $fs.Close() } catch [System.IO.IOException] { $r += 'existing:IOException' }"
        " catch { $r += ('existing:OTHER:' + $_.Exception.GetType().Name) };"
        " try { $fs = New-Object System.IO.FileStream($path, [System.IO.FileMode]::Open,"
        " [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None);"
        " $r += 'open:OK'; $fs.Close() } catch [System.IO.IOException] { $r += 'open:IOException' }"
        " catch { $r += ('open:OTHER:' + $_.Exception.GetType().Name) };"
        " $r -join ','"
    )
    proc = run_dotnet(host, script)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    parts = proc.stdout.strip().split(",")
    assert parts == ["fresh:OK", "existing:IOException", "open:OK"], parts


# ---------------------------------------------------------------------
# 2. A second exclusive open while held raises IOException.
# ---------------------------------------------------------------------
def test_second_exclusive_open_while_held_raises_ioexception(tmp_path):
    host = ps_host()
    path = tmp_path / "held.bin"
    path.write_bytes(b"seed")
    sig_path = tmp_path / "held-ready.txt"
    release_path = tmp_path / "held-release.txt"
    holder_script = (
        f"$fs = New-Object System.IO.FileStream('{path}', [System.IO.FileMode]::Open,"
        " [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None);"
        f" [System.IO.File]::WriteAllText('{sig_path}', \"ready`n\", [System.Text.Encoding]::ASCII);"
        f" while (-not (Test-Path '{release_path}')) {{ Start-Sleep -Milliseconds 100 }};"
        " $fs.Close()"
    )
    holder = subprocess.Popen(
        [host, "-NoProfile", "-NonInteractive", "-Command", holder_script],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        marker = wait_for_signal(sig_path, timeout=10)
        if marker is None:
            pytest.fail("holder never signalled readiness within 10s; "
                        "contention was never proven to be in effect")
        attempt_script = (
            f"try {{ $fs = New-Object System.IO.FileStream('{path}', [System.IO.FileMode]::Open,"
            " [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None);"
            " $fs.Close(); 'OK' } catch [System.IO.IOException] { 'IOException' }"
            " catch { 'OTHER:' + $_.Exception.GetType().Name }"
        )
        attempt = run_dotnet(host, attempt_script)
        assert attempt.returncode == 0, (attempt.stdout, attempt.stderr)
        assert attempt.stdout.strip() == "IOException", attempt.stdout
    finally:
        release_path.write_text("go", encoding="ascii")
        if holder.poll() is None:
            holder.terminate()
        try:
            holder.wait(timeout=10)
        except subprocess.TimeoutExpired:
            holder.kill()
            holder.wait(timeout=10)


# ---------------------------------------------------------------------
# 3. Truncate-and-rewrite in place under the held handle.
# ---------------------------------------------------------------------
def test_truncate_and_rewrite_in_place(tmp_path):
    host = ps_host()
    path = tmp_path / "rewrite.bin"
    path.write_bytes(b"OLD RECORD BYTES THAT ARE LONGER THAN THE NEW ONE")
    new_record = b'{"version":1,"state":"free"}'
    script = (
        f"$fs = New-Object System.IO.FileStream('{path}', [System.IO.FileMode]::Open,"
        " [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None);"
        f" $bytes = {byte_array_literal(new_record)};"
        " $fs.SetLength(0); $fs.Position = 0; $fs.Write($bytes, 0, $bytes.Length);"
        " $fs.Flush($true); $fs.Close()"
    )
    proc = run_dotnet(host, script)
    assert proc.returncode == 0, (proc.stdout, proc.stderr)
    assert path.read_bytes() == new_record


# ---------------------------------------------------------------------
# 4. The crash oracle, synchronized so the crash point is PROVEN before
# anything is inspected. The child: opens exclusively, SetLength(0),
# flush, [optionally writes a fixed partial prefix and flushes], writes
# a ready marker, then blocks. The parent waits at most ten seconds for
# that marker; only an OBSERVED marker licenses killing the child and
# inspecting the lock bytes. On timeout, the child is terminated in a
# `finally` and the test fails WITHOUT inspecting the lock bytes - a
# child that never signalled never reached the crash point, so its file
# state proves nothing.
# ---------------------------------------------------------------------
def _valid_held_record_bytes():
    rec = {
        "version": 1, "state": "held", "host": "CRASH-ORACLE-HOST",
        "ownerPid": 4242, "ownerStartTicksUtc": "111111111",
        "debateId": "a" * 32, "nonce": "b" * 32,
        "debateHome": "C:/crash-oracle-debate-home",
        "acquiredTicksUtc": "111111111",
    }
    return json.dumps(rec).encode("utf-8")


def _run_crash_oracle(tmp_path, host, partial_prefix):
    lane_home = tmp_path / "lane"
    lane_home.mkdir()
    lock_file = lane_home / "lane.lock"
    lock_file.write_bytes(_valid_held_record_bytes())
    sig_path = tmp_path / "crash-ready.txt"

    if partial_prefix is None:
        write_stmt = ""
    else:
        write_stmt = (
            f"$partial = {byte_array_literal(partial_prefix)};"
            " $fs.Position = 0; $fs.Write($partial, 0, $partial.Length); $fs.Flush($true);"
        )

    child_script = (
        f"$fs = New-Object System.IO.FileStream('{lock_file}', [System.IO.FileMode]::Open,"
        " [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None);"
        " $fs.SetLength(0); $fs.Flush($true);"
        f" {write_stmt}"
        f" [System.IO.File]::WriteAllText('{sig_path}', \"ready`n\", [System.Text.Encoding]::ASCII);"
        " Start-Sleep -Seconds 3600"
    )
    child = subprocess.Popen(
        [host, "-NoProfile", "-NonInteractive", "-Command", child_script],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        marker = wait_for_signal(sig_path, timeout=10)
        if marker is None:
            pytest.fail("crash oracle child never signalled readiness "
                        "within 10s; its file state proves nothing and "
                        "is not inspected")
        # Observed ready marker: the child has SetLength(0)'d, flushed,
        # and (for the partial fixture) written and flushed its fixed
        # prefix. Only now may it be killed and the bytes inspected.
    finally:
        if child.poll() is None:
            child.terminate()
        try:
            child.wait(timeout=10)
        except subprocess.TimeoutExpired:
            child.kill()
            child.wait(timeout=10)

    expected = b"" if partial_prefix is None else partial_prefix
    assert lock_file.read_bytes() == expected

    debate_home = tmp_path / "debate-home"
    debate_home.mkdir()
    # The owner is THIS process, not a synthetic pid. Acquire refuses to
    # record an owner that measures DEAD, and that refusal is parameter
    # validation: it runs before the lock file is read. A synthetic owner
    # would therefore exit 2 and this oracle would stop measuring what it
    # claims to - that a MALFORMED record exits 4 rather than being
    # reclaimed.
    ticks = subprocess.run(
        [host, "-NoProfile", "-Command",
         "$p = Get-Process -Id " + str(os.getpid()) +
         "; [string]$p.StartTime.ToUniversalTime().Ticks"],
        capture_output=True, text=True, timeout=60).stdout.strip()
    assert ticks.isdigit(), ticks
    acquire = run_lock_tool(host, [
        "-Acquire", "-LaneHome", str(lane_home), "-DebateId", uuid.uuid4().hex,
        "-OwnerPid", str(os.getpid()), "-OwnerStartTicksUtc", ticks,
        "-DebateHome", str(debate_home),
    ])
    assert acquire.returncode == 4, (acquire.stdout, acquire.stderr)


def test_crash_oracle_full_truncation_exits_4_rather_than_reclaiming(tmp_path):
    host = ps_host()
    _run_crash_oracle(tmp_path, host, partial_prefix=None)


def test_crash_oracle_partial_prefix_survives_and_exits_4(tmp_path):
    host = ps_host()
    _run_crash_oracle(tmp_path, host, partial_prefix=b'{"vers')


# ---------------------------------------------------------------------
# 5. Measurement 20: ticks round-trip as Int64 on both hosts; a date
# string round-trips as String on Windows PowerShell 5.1 (powershell.exe)
# and as DateTime on PowerShell 7 (pwsh.exe). "Assert divergence" is
# satisfied by one host failing and emitting nothing while the other
# succeeds - the same shape as the discarded empty-hash measurement at
# docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:
# 89-95, where two empty strings compared equal and read as clean. So
# each host invocation is proven to have HAPPENED - exit 0, exactly one
# parseable result line - before any reported type is inspected.
# ---------------------------------------------------------------------
TYPE_REPORT_SCRIPT = (
    '$o = [ordered]@{ ticks = [int64]123456789012345; whenValue = (Get-Date).ToString("o") };'
    ' $j = ConvertTo-Json $o -Compress;'
    ' $p = $j | ConvertFrom-Json;'
    ' $r = [ordered]@{ ticksType = $p.ticks.GetType().Name; whenType = $p.whenValue.GetType().Name };'
    ' ConvertTo-Json $r -Compress'
)


def measure_type_report(host, script=TYPE_REPORT_SCRIPT, timeout=30):
    """Run `script` under `host` and return its reported types - but only
    once the invocation is PROVEN to have happened. Anything short of
    that (nonzero exit, no output, more than one line, unparseable JSON,
    a shape missing the expected keys) raises rather than being read as
    a measurement of anything, including "divergence"."""
    proc = subprocess.run([host, "-NoProfile", "-NonInteractive", "-Command", script],
                          capture_output=True, text=True, timeout=timeout)
    if proc.returncode != 0:
        raise AssertionError(
            f"{host} exited {proc.returncode}, never a measurement: "
            f"stdout={proc.stdout!r} stderr={proc.stderr!r}")
    line = accept_exactly_one_nonempty_line(proc.stdout)
    if line is None:
        raise AssertionError(
            f"{host} did not emit exactly one result line: stdout={proc.stdout!r}")
    try:
        report = json.loads(line)
    except json.JSONDecodeError as exc:
        raise AssertionError(f"{host} emitted an unparseable line: {line!r}") from exc
    if (not isinstance(report, dict) or "ticksType" not in report
            or "whenType" not in report):
        raise AssertionError(f"{host} result missing the expected shape: {report!r}")
    return report


def test_measurement_20_ticks_and_date_string_types_diverge_across_hosts():
    hosts = required_hosts()
    ps1_report = measure_type_report(hosts["powershell.exe"])
    pwsh_report = measure_type_report(hosts["pwsh.exe"])
    # Both proven to have happened above; only now do their types get
    # compared, against the measured facts specifically (not a bare
    # inequality, which a differently-broken pair of results could also
    # satisfy).
    assert ps1_report["ticksType"] == "Int64", ps1_report
    assert pwsh_report["ticksType"] == "Int64", pwsh_report
    assert ps1_report["whenType"] == "String", ps1_report
    assert pwsh_report["whenType"] == "DateTime", pwsh_report


def test_measurement_20_a_failed_host_invocation_never_reads_as_divergence():
    # This test's own mutation: force one side to exit nonzero and confirm
    # the measurement helper fails closed instead of letting an empty
    # result stand in for "the type differs".
    hosts = required_hosts()
    broken_script = "exit 7"
    with pytest.raises(AssertionError, match="exited 7"):
        measure_type_report(hosts["powershell.exe"], script=broken_script)
