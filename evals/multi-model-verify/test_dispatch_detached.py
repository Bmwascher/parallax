"""Contract pins for tools/dispatch-detached.ps1 (Task 1, 2026-08-31
tracked-background-dispatch plan).

Drives the REAL script against stub payloads (stub wrapper .ps1 bodies
written per test, never the real codex/kimi transports). WINDOWS ONLY,
whole module: -Poll reads real process liveness (Get-Process, StartTime
ticks), and several fixtures run a real wrapper.ps1 as its own Windows
process the way the harness now does, per
docs/superpowers/specs/2026-08-31-tracked-background-dispatch-design.md.
PARALLAX_PS_HOST selects which host runs these tests, same pattern as
test_kimi_lane_lock.py - a selector that merely finds A host would
happily collect them on a non-Windows CI box too, where the platform
semantics under test do not exist there the same way. A green suite on
one host proves ONE interpreter.
"""
import json
import os
import shutil
import subprocess
import time
import uuid
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
TOOL_PATH = REPO / "tools" / "dispatch-detached.ps1"

POWERSHELL = (os.environ.get("PARALLAX_PS_HOST")
              or shutil.which("powershell") or shutil.which("pwsh"))

pytestmark = pytest.mark.skipif(
    os.name != "nt" or POWERSHELL is None,
    reason="dispatch-detached.ps1 is a Windows tool: it needs a "
           "PowerShell host and the detached-process / liveness "
           "platform it targets")

ROUND = "R1"

# ---------------------------------------------------------------------
# Stub wrapper bodies. Each is copied into the dispatch directory by
# -Prepare, and RUN SEPARATELY by the test (the way the harness now runs
# it, as a tracked background command - -Prepare itself starts nothing).
# They stand in for the real codex/kimi transport wrappers Task 3/6 will
# generate, and open with the same two lines every real wrapper body
# gains per the design spec section 3: publish pid and startticks as the
# wrapper's own first act, before any client call.
# ---------------------------------------------------------------------
PUBLISH_IDENTITY = (
    "[System.IO.File]::WriteAllText(\"$PSScriptRoot/pid\", \"$PID\", "
    "(New-Object System.Text.UTF8Encoding($false)))\n"
    "[System.IO.File]::WriteAllText(\"$PSScriptRoot/startticks\", "
    "((Get-Process -Id $PID).StartTime.ToUniversalTime().Ticks), "
    "(New-Object System.Text.UTF8Encoding($false)))\n"
)

FAST_WRAPPER = (
    PUBLISH_IDENTITY +
    "$dir = $PSScriptRoot\n"
    "Set-Content -LiteralPath (Join-Path $dir 'reply') -Value 'hello-world' "
    "-NoNewline -Encoding Ascii\n"
    "Set-Content -LiteralPath (Join-Path $dir 'exit') -Value '0' "
    "-NoNewline -Encoding Ascii\n"
)

# Writes a NONEMPTY reply immediately, then sleeps - the Task 8
# arrangement in miniature (a reply being written is not a reply while
# the process is still alive).
SLOW_WRAPPER = (
    PUBLISH_IDENTITY +
    "$dir = $PSScriptRoot\n"
    "Set-Content -LiteralPath (Join-Path $dir 'reply') -Value "
    "'premature-reply-content' -NoNewline -Encoding Ascii\n"
    "Start-Sleep -Seconds 25\n"
    "Set-Content -LiteralPath (Join-Path $dir 'exit') -Value '0' "
    "-NoNewline -Encoding Ascii\n"
)

# A generic wrapper body for tests that only need a legitimate,
# installable file - it publishes its identity and sleeps, never
# reaching a reply/exit. Content only matters when a test actually runs
# it; most callers only ever -Prepare it.
SLEEPER_WRAPPER = PUBLISH_IDENTITY + "Start-Sleep -Seconds 20\n"

# The wrapper shape Task 3 ships, reduced to a sleep and a fixed reply:
# publish identity first, then a short pause a test can observe as
# "running" before it completes on its own.
IDENTITY_THEN_SLEEP_WRAPPER = (
    PUBLISH_IDENTITY +
    "Start-Sleep -Seconds 5\n"
    "Set-Content -LiteralPath (Join-Path $PSScriptRoot 'reply') -Value "
    "'fixed-reply-content' -NoNewline -Encoding Ascii\n"
    "Set-Content -LiteralPath (Join-Path $PSScriptRoot 'exit') -Value '0' "
    "-NoNewline -Encoding Ascii\n"
)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def run_dispatch(args, env=None, timeout=30):
    full_env = dict(os.environ)
    if env:
        full_env.update(env)
    cmd = [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(TOOL_PATH)] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, env=full_env, timeout=timeout)


def start_dispatch_bg(args, env=None):
    full_env = dict(os.environ)
    if env:
        full_env.update(env)
    cmd = [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(TOOL_PATH)] + list(args)
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, env=full_env)


def _run_wrapper_in_background(dispatch_dir):
    """Start a prepared wrapper.ps1 the way the harness now does: as its
    own tracked process, isolated from this test process's own stdio
    (CREATE_NEW_CONSOLE), matching the isolation
    test_wrapper_renders_and_parses.py already found necessary."""
    return subprocess.Popen(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(dispatch_dir / "wrapper.ps1")],
        creationflags=subprocess.CREATE_NEW_CONSOLE)


def write_wrapper(base, content, name):
    base.mkdir(parents=True, exist_ok=True)
    p = base / name
    p.write_text(content, encoding="ascii")
    return p


def _wrapper(base, content=SLEEPER_WRAPPER, name="wrapper-src.ps1"):
    """A legitimate, installable wrapper body for tests that only need
    -Prepare to succeed and do not care what the wrapper would do."""
    return write_wrapper(base, content, name)


def _wait_for(path, timeout=15):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.exists():
            # The wrapper's identity publish is two sequential writes
            # (pid, then startticks) - Get-Process for the second one
            # measured 15-30ms behind the first. A caller that waits for
            # pid and immediately checks a sibling file needs that gap
            # closed, not just the file it named.
            time.sleep(0.15)
            return True
        time.sleep(0.02)
    return False


def do_launch(base, round_label, wrapper_content=FAST_WRAPPER, env=None,
              dispatch_name="dispatch", receipt_name="receipt.json",
              wrapper_name="wrapper-src.ps1", extra_args=None):
    """Prepare a round and start its wrapper in the background - the two
    steps the harness now performs separately, combined here so existing
    fixture call sites keep their shape. Returns as soon as -Prepare has
    returned; the wrapper keeps running on its own."""
    base.mkdir(parents=True, exist_ok=True)
    dispatch_dir = base / dispatch_name
    receipt_path = base / receipt_name
    wrapper = write_wrapper(base, wrapper_content, wrapper_name)
    args = ["-Prepare", "-DispatchDir", str(dispatch_dir), "-WrapperBody", str(wrapper),
            "-ReceiptPath", str(receipt_path), "-Round", round_label, "-Json"]
    if extra_args:
        args += extra_args
    result = run_dispatch(args, env=env)
    if result.returncode == 0:
        _run_wrapper_in_background(dispatch_dir)
    return dispatch_dir, receipt_path, result


def successful_launch(base, round_label="R1"):
    dispatch_dir, receipt_path, result = do_launch(base, round_label)
    assert result.returncode == 0, (result.stdout, result.stderr)
    assert _wait_for(dispatch_dir / "exit", timeout=15), "wrapper never wrote exit"
    assert _wait_for(dispatch_dir / "reply", timeout=15), "wrapper never wrote reply"
    return dispatch_dir, receipt_path


def _prepared(base, wrapper_content, round_label=ROUND, dispatch_name="dispatch",
              receipt_name="receipt.json", wrapper_name="wrapper-src.ps1"):
    """-Prepare only - no wrapper is ever run. Returns (dispatch_dir,
    wrapper_path, receipt_path)."""
    base.mkdir(parents=True, exist_ok=True)
    dispatch_dir = base / dispatch_name
    receipt_path = base / receipt_name
    wrapper = write_wrapper(base, wrapper_content, wrapper_name)
    args = ["-Prepare", "-DispatchDir", str(dispatch_dir), "-WrapperBody", str(wrapper),
            "-ReceiptPath", str(receipt_path), "-Round", round_label, "-Json"]
    result = run_dispatch(args)
    assert result.returncode == 0, (result.stdout, result.stderr)
    return dispatch_dir, wrapper, receipt_path


def _prepare_raw(dispatch_dir, wrapper_path, receipt_path, round_label):
    """Run -Prepare with no assumption of success; return (exit code,
    stdout text) for a caller that wants to inspect a refusal."""
    args = ["-Prepare", "-DispatchDir", str(dispatch_dir), "-WrapperBody", str(wrapper_path),
            "-ReceiptPath", str(receipt_path), "-Round", round_label]
    result = run_dispatch(args)
    return result.returncode, result.stdout


def run_poll(receipt_path, expected_dispatch_dir, expected_round, env=None,
             timeout=30, json_mode=True):
    args = ["-Poll", "-Receipt", str(receipt_path),
            "-ExpectedDispatchDir", str(expected_dispatch_dir),
            "-ExpectedRound", expected_round]
    if json_mode:
        args.append("-Json")
    return run_dispatch(args, env=env, timeout=timeout)


def poll_json(receipt_path, expected_dispatch_dir, expected_round, env=None, timeout=30):
    result = run_poll(receipt_path, expected_dispatch_dir, expected_round, env=env, timeout=timeout)
    obj = json.loads(result.stdout.strip())
    return result, obj


def _poll(receipt_path, expected_dispatch_dir, expected_round):
    """(state, exit code) - the shape the Step 1 tests read directly."""
    result, obj = poll_json(receipt_path, expected_dispatch_dir, expected_round)
    return obj["state"], result.returncode


def write_receipt(path, dispatch_dir, token="1" * 32, round_label="R1",
                   start_ticks=638500000000000000):
    obj = {"dispatchDir": str(dispatch_dir), "token": token,
           "round": round_label, "startTicks": start_ticks}
    path.write_text(json.dumps(obj), encoding="utf-8")


def kill_pid_best_effort(pid):
    try:
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                        capture_output=True, text=True, timeout=15)
    except Exception:
        pass


def cleanup_dispatch_pid(dispatch_dir):
    """Best-effort teardown for a round left RUNNING (a sleeping
    wrapper) by a test, so the suite does not leak processes."""
    pid_file = dispatch_dir / "pid"
    if pid_file.exists():
        try:
            pid = pid_file.read_text(encoding="ascii").strip()
            if pid:
                kill_pid_best_effort(int(pid))
        except Exception:
            pass


# ---------------------------------------------------------------------
# Step 1 (2026-08-31 plan): -Prepare replaces -Launch. These tests pin
# the new state directly.
# ---------------------------------------------------------------------
def test_prepare_starts_no_process(tmp_path):
    """-Prepare performs the transaction and creates NO child.

    The whole point of the redesign: the harness owns the process, so the
    tool must not spawn one. Proven by counting the dispatch directory's
    own artifacts rather than by watching the process table, which races.
    """
    d, wrapper, receipt = _prepared(tmp_path, SLEEPER_WRAPPER)
    assert (d / "launch.committed").exists()
    assert receipt.exists()
    assert not (d / "pid").exists(), "-Prepare must not publish a pid"
    assert not (d / "startticks").exists()
    assert not (d / "reply").exists()
    assert not (d / "exit").exists()


def test_a_prepared_but_unrun_round_is_not_started(tmp_path):
    """The new state. A receipt with no pid is never a result."""
    d, wrapper, receipt = _prepared(tmp_path, SLEEPER_WRAPPER)
    state, code = _poll(receipt, d, ROUND)
    assert state == "not-started"
    assert code == 1


def test_not_started_never_exits_zero_even_with_a_planted_reply(tmp_path):
    """A reply that appears without a pid is not a completed round.

    Same shape as the planted-reply test for `running`: the classification
    must come from the completion model, never from a file's presence.
    """
    d, wrapper, receipt = _prepared(tmp_path, SLEEPER_WRAPPER)
    (d / "reply").write_text("a reply nobody's round wrote", encoding="utf-8")
    (d / "exit").write_text("0", encoding="utf-8")
    state, code = _poll(receipt, d, ROUND)
    assert state == "not-started"
    assert code != 0


def test_the_wrapper_publishes_its_own_identity_and_then_runs(tmp_path):
    """Run a prepared wrapper the way the harness will, and watch the
    states move: not-started, then running, then reply-present."""
    d, wrapper, receipt = _prepared(tmp_path, IDENTITY_THEN_SLEEP_WRAPPER)
    assert _poll(receipt, d, ROUND) == ("not-started", 1)
    proc = _run_wrapper_in_background(d)
    try:
        _wait_for(d / "pid", timeout=20)
        assert (d / "startticks").exists(), "ticks must land with the pid"
        assert int((d / "pid").read_text()) == proc.pid
        assert _poll(receipt, d, ROUND) == ("running", 3)
    finally:
        proc.wait(timeout=60)
    assert _poll(receipt, d, ROUND) == ("reply-present", 0)


def test_no_csharp_is_compiled_anywhere_in_the_script(tmp_path):
    """The launcher is GONE, not disabled.

    Round 1 of the diff debate found the top-level Add-Type running before
    the script's own checks and outside any catch, so even -Poll depended
    on compiling launch-only C#. Deleting the launcher removes the subject.
    """
    text = TOOL_PATH.read_text(encoding="utf-8")
    for needle in ("Add-Type", "CreateProcess", "PROC_THREAD_ATTRIBUTE",
                   "GetProcessTimes", "LaunchDetached"):
        assert needle not in text, "the launcher survives: " + needle


def test_prepare_refuses_an_existing_dispatch_directory(tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    code, out = _prepare_raw(d, _wrapper(tmp_path), tmp_path / "r.json", ROUND)
    assert code == 1
    assert "BLOCKED" in out
    assert not (tmp_path / "r.json").exists(), "a refused prepare publishes no receipt"


def test_prepare_publishes_no_receipt_when_the_wrapper_cannot_be_installed(tmp_path):
    """Fail-closed after the directory exists."""
    receipt = tmp_path / "r.json"
    code, out = _prepare_raw(tmp_path / "d", tmp_path / "does-not-exist.ps1",
                             receipt, ROUND)
    assert code == 1
    assert not receipt.exists()


# ---------------------------------------------------------------------
# -Prepare: reservation and separation
# ---------------------------------------------------------------------
def test_a_taken_directory_blocks_and_starts_nothing(tmp_path):
    dispatch_dir = tmp_path / "dispatch"
    dispatch_dir.mkdir()
    receipt_path = tmp_path / "receipt.json"
    wrapper = write_wrapper(tmp_path, FAST_WRAPPER, "wrapper-src.ps1")

    result = run_dispatch(["-Prepare", "-DispatchDir", str(dispatch_dir),
                            "-WrapperBody", str(wrapper), "-ReceiptPath", str(receipt_path),
                            "-Round", "R1"])
    assert result.returncode == 1, (result.stdout, result.stderr)
    assert result.stdout.strip() != ""
    assert not receipt_path.exists()
    assert not (dispatch_dir / "wrapper.ps1").exists()
    assert not (dispatch_dir / "pid").exists()
    assert list(dispatch_dir.iterdir()) == []


def test_an_existing_receipt_blocks_before_the_directory_is_reserved(tmp_path):
    dispatch_dir = tmp_path / "dispatch"
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text("pre-existing", encoding="ascii")
    wrapper = write_wrapper(tmp_path, FAST_WRAPPER, "wrapper-src.ps1")

    result = run_dispatch(["-Prepare", "-DispatchDir", str(dispatch_dir),
                            "-WrapperBody", str(wrapper), "-ReceiptPath", str(receipt_path),
                            "-Round", "R1"])
    assert result.returncode == 1, (result.stdout, result.stderr)
    assert not dispatch_dir.exists(), "the directory must never be reserved when the receipt path is already taken"
    assert receipt_path.read_text(encoding="ascii") == "pre-existing"


@pytest.mark.parametrize("relative", ["", "one/r.json", "one/two/r.json"],
                          ids=["equal", "one-level", "two-levels"])
def test_a_receipt_path_inside_the_dispatch_directory_is_blocked(tmp_path, relative):
    dispatch_dir = tmp_path / "dispatch"
    receipt_path = dispatch_dir if relative == "" else dispatch_dir.joinpath(*relative.split("/"))
    wrapper = write_wrapper(tmp_path, FAST_WRAPPER, "wrapper-src.ps1")

    result = run_dispatch(["-Prepare", "-DispatchDir", str(dispatch_dir),
                            "-WrapperBody", str(wrapper), "-ReceiptPath", str(receipt_path),
                            "-Round", "R1"])
    assert result.returncode == 1, (result.stdout, result.stderr)
    assert not dispatch_dir.exists(), "the separation check must run before the directory is reserved"


def test_a_receipt_that_appears_during_the_prepare_fails_closed(tmp_path):
    """The exact race the create-new receipt write at the last step must
    refuse rather than overwrite: a receipt planted after the directory
    is reserved but before -Prepare publishes its own."""
    dispatch_dir = tmp_path / "dispatch"
    receipt_path = tmp_path / "receipt.json"
    wrapper = write_wrapper(tmp_path, FAST_WRAPPER, "wrapper-src.ps1")
    hold_base = str(tmp_path / "hold")
    env = {"PARALLAX_DISPATCH_HOLD_BEFORE_PUBLISH": hold_base}

    proc = start_dispatch_bg(
        ["-Prepare", "-DispatchDir", str(dispatch_dir), "-WrapperBody", str(wrapper),
         "-ReceiptPath", str(receipt_path), "-Round", "R1", "-Json"], env=env)
    try:
        started = Path(hold_base + ".started")
        assert _wait_for(started, timeout=15), "hold barrier never signalled .started"

        # Receipt did not exist at the separation/freshness check; it
        # appears now, during the hold - the exact race the create-new
        # write must refuse rather than overwrite.
        receipt_path.write_text("a-receipt-this-prepare-did-not-write", encoding="ascii")

        Path(hold_base + ".release").write_text("go", encoding="ascii")
        stdout, stderr = proc.communicate(timeout=30)
        assert proc.returncode == 1, (stdout, stderr)

        assert receipt_path.read_text(encoding="ascii") == "a-receipt-this-prepare-did-not-write", \
            "the create-new write must never overwrite a receipt it did not write"
    finally:
        if proc.poll() is None:
            proc.kill()
            proc.wait(timeout=15)


def test_force_is_not_accepted_in_any_argument_order(tmp_path):
    """Parse the actual command AST rather than searching for a fixed
    token order in the source text: round 4 found the previous pin only
    forbade the exact literal '-ItemType Directory -Force'."""
    analyzer = tmp_path / "force-check.ps1"
    analyzer.write_text(
        "param([string]$Path)\n"
        "$tokens = $null; $parseErrors = $null\n"
        "$ast = [System.Management.Automation.Language.Parser]::ParseFile($Path, [ref]$tokens, [ref]$parseErrors)\n"
        "$calls = $ast.FindAll({\n"
        "    param($n)\n"
        "    $n -is [System.Management.Automation.Language.CommandAst] -and\n"
        "    $n.GetCommandName() -and\n"
        "    $n.GetCommandName().ToLowerInvariant() -eq 'new-item'\n"
        "}, $true)\n"
        "$results = @()\n"
        "foreach ($c in $calls) {\n"
        "    $text = $c.Extent.Text\n"
        "    $isDirType = [bool]([regex]::IsMatch($text, '(?i)-ItemType\\s+Directory'))\n"
        "    $hasForce = $false\n"
        "    foreach ($el in $c.CommandElements) {\n"
        "        if (($el -is [System.Management.Automation.Language.CommandParameterAst]) -and\n"
        "            ($el.ParameterName -ieq 'Force')) { $hasForce = $true }\n"
        "    }\n"
        "    $results += [ordered]@{ isDirectory = $isDirType; hasForce = $hasForce }\n"
        "}\n"
        "ConvertTo-Json @($results) -Compress\n",
        encoding="ascii")
    result = subprocess.run(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(analyzer), str(TOOL_PATH)],
        capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, (result.stdout, result.stderr)
    calls = json.loads(result.stdout.strip())
    directory_calls = [c for c in calls if c["isDirectory"]]
    assert directory_calls, "no New-Item -ItemType Directory call was found to check at all"
    for c in directory_calls:
        assert c["hasForce"] is False, "the directory reservation must never carry -Force"


def test_a_hard_kill_before_publication_is_never_success(tmp_path):
    dispatch_dir = tmp_path / "dispatch"
    receipt_path = tmp_path / "receipt.json"
    wrapper = write_wrapper(tmp_path, FAST_WRAPPER, "wrapper-src.ps1")
    hold_base = str(tmp_path / "hold")
    env = {"PARALLAX_DISPATCH_HOLD_BEFORE_PUBLISH": hold_base}

    proc = start_dispatch_bg(
        ["-Prepare", "-DispatchDir", str(dispatch_dir), "-WrapperBody", str(wrapper),
         "-ReceiptPath", str(receipt_path), "-Round", "R1", "-Json"], env=env)
    try:
        started = Path(hold_base + ".started")
        assert _wait_for(started, timeout=15), "hold barrier never signalled .started"

        # Kill the TOOL itself here - never release the barrier. This is
        # the case the catch cannot reach.
        proc.kill()
        proc.wait(timeout=15)

        assert not receipt_path.exists()
        result, obj = poll_json(receipt_path, dispatch_dir, "R1")
        assert obj["state"] == "no-receipt", obj
        assert result.returncode == 1
    finally:
        if proc.poll() is None:
            proc.kill()


# ---------------------------------------------------------------------
# -Poll: expected act, ordering of checks
# ---------------------------------------------------------------------
def test_poll_reports_launch_unknown_when_the_marker_is_gone(tmp_path):
    dispatch_dir, receipt_path = successful_launch(tmp_path)
    (dispatch_dir / "launch.committed").unlink()
    result, obj = poll_json(receipt_path, dispatch_dir, "R1")
    assert obj["state"] == "launch-unknown", obj
    assert result.returncode == 1


def test_a_refused_prepare_writes_no_receipt_and_cannot_be_polled(tmp_path):
    dispatch_dir, receipt_r1 = successful_launch(tmp_path, "R1")

    receipt_r2 = tmp_path / "receipt-r2.json"
    wrapper2 = write_wrapper(tmp_path, FAST_WRAPPER, "wrapper-r2.ps1")
    result2 = run_dispatch(["-Prepare", "-DispatchDir", str(dispatch_dir),
                             "-WrapperBody", str(wrapper2), "-ReceiptPath", str(receipt_r2),
                             "-Round", "R2", "-Json"])
    assert result2.returncode == 1, (result2.stdout, result2.stderr)
    assert not receipt_r2.exists()

    result, obj = poll_json(receipt_r2, dispatch_dir, "R2")
    assert obj["state"] == "no-receipt", obj
    assert obj["state"] != "reply-present"
    assert result.returncode == 1


def test_a_stale_receipt_is_refused_against_the_expected_act(tmp_path):
    dispatch_dir_1, receipt_1 = successful_launch(tmp_path / "round1", "R1")
    dispatch_dir_2, receipt_2 = successful_launch(tmp_path / "round2", "R2")

    # Both directory and round differ.
    result, obj = poll_json(receipt_1, dispatch_dir_2, "R2")
    assert obj["state"] == "receipt-not-expected", obj
    assert result.returncode == 1

    # Only the round differs.
    result, obj = poll_json(receipt_1, dispatch_dir_1, "R2")
    assert obj["state"] == "receipt-not-expected", obj

    # Only the directory differs.
    result, obj = poll_json(receipt_1, dispatch_dir_2, "R1")
    assert obj["state"] == "receipt-not-expected", obj


def test_the_expected_act_is_checked_before_any_directory_is_opened(tmp_path):
    # (a) a receipt naming a dispatchDir that does not exist at all.
    missing_dir = tmp_path / "never-created"
    receipt_a = tmp_path / "receipt-a.json"
    write_receipt(receipt_a, missing_dir, round_label="R1")
    result, obj = poll_json(receipt_a, tmp_path / "some-other-expected-dir", "R1")
    assert obj["state"] == "receipt-not-expected", obj

    # (b) a receipt naming a dispatchDir that exists but holds no
    # launch.committed. Control: polled with matching expected values,
    # this genuinely reaches launch-unknown - proving the mismatch above
    # was refused BEFORE that check ran, not because the fixture could
    # never reach it.
    uncommitted_dir = tmp_path / "uncommitted"
    uncommitted_dir.mkdir()
    receipt_b = tmp_path / "receipt-b.json"
    write_receipt(receipt_b, uncommitted_dir, round_label="R1")

    result, obj = poll_json(receipt_b, tmp_path / "some-other-expected-dir-2", "R1")
    assert obj["state"] == "receipt-not-expected", obj

    result, obj = poll_json(receipt_b, uncommitted_dir, "R1")
    assert obj["state"] == "launch-unknown", obj


def test_a_stale_receipt_matching_every_expected_value_still_answers_for_its_own_round(tmp_path):
    dispatch_dir, receipt_path = successful_launch(tmp_path, "R1")
    result, obj = poll_json(receipt_path, dispatch_dir, "R1")
    assert obj["state"] == "reply-present", obj
    assert obj["round"] == "R1", obj
    assert result.returncode == 0


# ---------------------------------------------------------------------
# -Poll: receipt readability and schema
# ---------------------------------------------------------------------
def test_an_unreadable_receipt_is_no_receipt_at_exit_one(tmp_path):
    receipt_path = tmp_path / "receipt-is-a-directory.json"
    receipt_path.mkdir()
    result, obj = poll_json(receipt_path, tmp_path / "whatever-dir", "R1")
    assert obj["state"] == "no-receipt", obj
    assert result.returncode == 1
    assert result.returncode != 2


VALID_RECEIPT = {
    "dispatchDir": "C:\\some\\dispatch\\dir",
    "token": "11111111-1111-1111-1111-111111111111",
    "round": "R1",
    "startTicks": 638500000000000000,
}

SCHEMA_FIXTURES = {
    "top-not-object-array": [1, 2, 3],
    "top-not-object-string": "hello",
    "top-not-object-number": 42,
    "missing-dispatchdir": {k: v for k, v in VALID_RECEIPT.items() if k != "dispatchDir"},
    "missing-token": {k: v for k, v in VALID_RECEIPT.items() if k != "token"},
    "missing-round": {k: v for k, v in VALID_RECEIPT.items() if k != "round"},
    "missing-startticks": {k: v for k, v in VALID_RECEIPT.items() if k != "startTicks"},
    "empty-dispatchdir": {**VALID_RECEIPT, "dispatchDir": ""},
    "empty-token": {**VALID_RECEIPT, "token": ""},
    "empty-round": {**VALID_RECEIPT, "round": ""},
    "startticks-unparseable-string": {**VALID_RECEIPT, "startTicks": "not-a-number"},
    "startticks-float-string": {**VALID_RECEIPT, "startTicks": "1.5"},
    "wrong-type-dispatchdir-number": {**VALID_RECEIPT, "dispatchDir": 123},
    "wrong-type-token-number": {**VALID_RECEIPT, "token": 123},
    "wrong-type-round-number": {**VALID_RECEIPT, "round": 123},
    "wrong-type-startticks-bool": {**VALID_RECEIPT, "startTicks": True},
    "wrong-type-startticks-array": {**VALID_RECEIPT, "startTicks": [1, 2, 3]},
    "unknown-extra-field": {**VALID_RECEIPT, "extra": "nope"},
}


@pytest.mark.parametrize("name", sorted(SCHEMA_FIXTURES))
def test_a_receipt_failing_the_schema_is_no_receipt(tmp_path, name):
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(json.dumps(SCHEMA_FIXTURES[name]), encoding="utf-8")
    result, obj = poll_json(receipt_path, tmp_path / "whatever-dir", "R1")
    assert obj["state"] == "no-receipt", (name, obj)
    assert result.returncode == 1, (name, result.stdout, result.stderr)


def test_the_valid_control_receipt_is_not_no_receipt(tmp_path):
    """Positive control for the schema fixtures above: the unmodified
    VALID_RECEIPT is well-formed (it just names a dispatchDir that does
    not exist, so it resolves to launch-unknown, never no-receipt)."""
    receipt_path = tmp_path / "receipt.json"
    receipt_path.write_text(json.dumps(VALID_RECEIPT), encoding="utf-8")
    result, obj = poll_json(receipt_path, VALID_RECEIPT["dispatchDir"], VALID_RECEIPT["round"])
    assert obj["state"] != "no-receipt", obj


# ---------------------------------------------------------------------
# -Poll: liveness (pid / startticks) and terminal artifacts
# ---------------------------------------------------------------------
def test_poll_rejects_a_receipt_whose_token_is_not_the_committed_one(tmp_path):
    dispatch_dir, receipt_path = successful_launch(tmp_path)
    (dispatch_dir / "launch.committed").write_text("not-the-real-token", encoding="ascii")
    result, obj = poll_json(receipt_path, dispatch_dir, "R1")
    assert obj["state"] == "launch-not-ours", obj
    assert result.returncode == 1


def test_poll_reports_not_started_when_the_pid_file_is_absent(tmp_path):
    """A pid file that never appears (never run) and one that appeared
    and was then removed (mid-run interruption before -Poll observes it)
    read identically: neither is a result."""
    dispatch_dir, receipt_path = successful_launch(tmp_path)
    (dispatch_dir / "pid").unlink()
    result, obj = poll_json(receipt_path, dispatch_dir, "R1")
    assert obj["state"] == "not-started", obj
    assert result.returncode == 1


@pytest.mark.parametrize("mode", ["empty", "non-integer"])
def test_poll_reports_pid_unreadable_when_the_pid_is_malformed(tmp_path, mode):
    dispatch_dir, receipt_path = successful_launch(tmp_path)
    pid_file = dispatch_dir / "pid"
    if mode == "empty":
        pid_file.write_bytes(b"")
    else:
        pid_file.write_text("not-an-integer", encoding="ascii")
    result, obj = poll_json(receipt_path, dispatch_dir, "R1")
    assert obj["state"] == "pid-unreadable", (mode, obj)
    assert result.returncode == 1


@pytest.mark.parametrize("mode", ["missing", "empty", "non-integer"])
def test_poll_reports_pid_unreadable_when_startticks_is_missing_or_malformed(tmp_path, mode):
    """A valid, readable pid with a startticks file that cannot be
    trusted is the same "cannot confirm identity" outcome as a malformed
    pid - folded together rather than adding a fourteenth state."""
    dispatch_dir, receipt_path = successful_launch(tmp_path)
    ticks_file = dispatch_dir / "startticks"
    if mode == "missing":
        ticks_file.unlink()
    elif mode == "empty":
        ticks_file.write_bytes(b"")
    else:
        ticks_file.write_text("not-an-integer", encoding="ascii")
    result, obj = poll_json(receipt_path, dispatch_dir, "R1")
    assert obj["state"] == "pid-unreadable", (mode, obj)
    assert result.returncode == 1


def test_a_recycled_pid_is_not_read_as_running(tmp_path):
    """The completed round's own startticks file does not match the live
    process now holding that pid: this process is genuinely alive, but it
    is not the one that published that pid, so it was recycled and the
    poll must treat it as gone."""
    dispatch_dir, receipt_path = successful_launch(tmp_path)
    original_ticks = (dispatch_dir / "startticks").read_text(encoding="ascii")
    # Overwrite pid with THIS TEST PROCESS's own pid (genuinely alive for
    # the whole run), while startticks keeps the original (now-dead)
    # wrapper's ticks - which will not match this live process's actual
    # start time.
    (dispatch_dir / "pid").write_text(str(os.getpid()), encoding="ascii")

    result, obj = poll_json(receipt_path, dispatch_dir, "R1")
    assert obj["state"] != "running", obj
    # exit/reply are untouched from the real completed launch, so a
    # correctly-recycled pid falls through to reply-present.
    assert obj["state"] == "reply-present", obj
    assert result.returncode == 0
    # sanity: this really was a distinct process, not a coincidence.
    assert str(os.getpid()) != original_ticks
    assert original_ticks is not None


def test_an_unmeasurable_start_time_is_pid_unreadable(tmp_path):
    dispatch_dir, receipt_path = successful_launch(tmp_path)
    (dispatch_dir / "pid").write_text(str(os.getpid()), encoding="ascii")
    result, obj = poll_json(receipt_path, dispatch_dir, "R1",
                             env={"PARALLAX_DISPATCH_POLL_STARTTIME_FAULT": "1"})
    assert obj["state"] == "pid-unreadable", obj
    assert obj["state"] != "running"
    assert result.returncode == 1


def test_poll_reports_running_while_the_pid_is_alive(tmp_path):
    dispatch_dir, receipt_path, result0 = do_launch(tmp_path, "R1", wrapper_content=SLOW_WRAPPER)
    assert result0.returncode == 0, (result0.stdout, result0.stderr)
    try:
        assert _wait_for(dispatch_dir / "reply", timeout=15), "wrapper never wrote its premature reply"
        assert not (dispatch_dir / "exit").exists(), "exit must not exist yet in this fixture"

        result, obj = poll_json(receipt_path, dispatch_dir, "R1")
        assert obj["state"] == "running", obj
        assert result.returncode == 3
        # The whole point: a reply being written is not a reply. If the
        # implementation kept reading past the liveness check it would
        # hit no-exit-file instead (exit truly is absent here), not
        # running - so this also proves the short-circuit.
        assert "premature-reply-content" not in result.stdout
    finally:
        cleanup_dispatch_pid(dispatch_dir)


def test_a_running_round_can_never_exit_zero(tmp_path):
    dispatch_dir, receipt_path, result0 = do_launch(tmp_path, "R1", wrapper_content=SLOW_WRAPPER)
    assert result0.returncode == 0, (result0.stdout, result0.stderr)
    try:
        assert _wait_for(dispatch_dir / "reply", timeout=15)
        result, obj = poll_json(receipt_path, dispatch_dir, "R1")
        assert result.returncode == 3
        assert result.returncode != 0
        assert obj["state"] == "running"
    finally:
        cleanup_dispatch_pid(dispatch_dir)


def test_poll_distinguishes_every_terminal_state(tmp_path):
    """Each fixture is a REAL successful launch with exactly one artifact
    altered afterward - round 6's finding: hand-planted fixtures can
    describe an arrangement -Launch could never produce."""
    cases = ["launch-unknown", "launch-not-ours", "pid-unreadable",
             "no-exit-file", "exit-unreadable", "exit-nonzero",
             "no-reply", "reply-empty", "reply-present"]
    for state in cases:
        base = tmp_path / state
        dispatch_dir, receipt_path = successful_launch(base, "R1")
        if state == "launch-unknown":
            (dispatch_dir / "launch.committed").unlink()
        elif state == "launch-not-ours":
            (dispatch_dir / "launch.committed").write_text("wrong-token", encoding="ascii")
        elif state == "pid-unreadable":
            (dispatch_dir / "pid").write_text("nope", encoding="ascii")
        elif state == "no-exit-file":
            (dispatch_dir / "exit").unlink()
        elif state == "exit-unreadable":
            (dispatch_dir / "exit").write_text("nope", encoding="ascii")
        elif state == "exit-nonzero":
            (dispatch_dir / "exit").write_text("7", encoding="ascii")
        elif state == "no-reply":
            (dispatch_dir / "reply").unlink()
        elif state == "reply-empty":
            (dispatch_dir / "reply").write_bytes(b"")
        # reply-present: leave the successful launch untouched.

        result, obj = poll_json(receipt_path, dispatch_dir, "R1")
        assert obj["state"] == state, (state, obj)


# ---------------------------------------------------------------------
# Exit code mapping, exhaustive over all thirteen states
# ---------------------------------------------------------------------
def _build_state_fixture(base, state):
    """Return (receipt_path, expected_dispatch_dir, expected_round) that
    makes -Poll report `state`."""
    round_label = "R1"
    if state == "no-receipt":
        return base / "missing-receipt.json", base / "missing-dispatch", round_label
    if state == "not-started":
        dispatch_dir, wrapper, receipt_path = _prepared(base, SLEEPER_WRAPPER, round_label)
        return receipt_path, dispatch_dir, round_label
    if state == "running":
        dispatch_dir, receipt_path, result = do_launch(base, round_label, wrapper_content=SLOW_WRAPPER)
        assert result.returncode == 0, (result.stdout, result.stderr)
        assert _wait_for(dispatch_dir / "reply", timeout=15)
        return receipt_path, dispatch_dir, round_label

    dispatch_dir, receipt_path = successful_launch(base, round_label)
    if state == "receipt-not-expected":
        return receipt_path, dispatch_dir, "a-different-round"
    if state == "launch-unknown":
        (dispatch_dir / "launch.committed").unlink()
    elif state == "launch-not-ours":
        (dispatch_dir / "launch.committed").write_text("wrong-token", encoding="ascii")
    elif state == "pid-unreadable":
        (dispatch_dir / "pid").write_text("nope", encoding="ascii")
    elif state == "no-exit-file":
        (dispatch_dir / "exit").unlink()
    elif state == "exit-unreadable":
        (dispatch_dir / "exit").write_text("nope", encoding="ascii")
    elif state == "exit-nonzero":
        (dispatch_dir / "exit").write_text("7", encoding="ascii")
    elif state == "no-reply":
        (dispatch_dir / "reply").unlink()
    elif state == "reply-empty":
        (dispatch_dir / "reply").write_bytes(b"")
    elif state == "reply-present":
        pass
    else:
        raise ValueError(state)
    return receipt_path, dispatch_dir, round_label


STATE_EXIT_CODES = {
    "no-receipt": 1,
    "receipt-not-expected": 1,
    "launch-unknown": 1,
    "launch-not-ours": 1,
    "not-started": 1,
    "pid-unreadable": 1,
    "running": 3,
    "no-exit-file": 1,
    "exit-unreadable": 1,
    "exit-nonzero": 1,
    "no-reply": 1,
    "reply-empty": 1,
    "reply-present": 0,
}


@pytest.mark.parametrize("state,expected_exit", sorted(STATE_EXIT_CODES.items()))
def test_every_state_maps_to_its_documented_exit_code(tmp_path, state, expected_exit):
    base = tmp_path / state
    try:
        receipt_path, expected_dir, expected_round = _build_state_fixture(base, state)
        result, obj = poll_json(receipt_path, expected_dir, expected_round)
        assert result.returncode == expected_exit, (state, result.stdout, result.stderr)
        assert obj["state"] == state, (state, obj)
        if expected_exit != 0:
            assert state in result.stdout

        # Plain (non -Json) mode must also print the bare state name.
        plain = run_poll(receipt_path, expected_dir, expected_round, json_mode=False)
        assert plain.returncode == expected_exit
        assert plain.stdout.strip() == state
    finally:
        if state == "running":
            cleanup_dispatch_pid(base / "dispatch")


def test_a_malformed_invocation_exits_two(tmp_path):
    no_args = run_dispatch([])
    assert no_args.returncode == 2, (no_args.stdout, no_args.stderr)

    both = run_dispatch(["-Prepare", "-Poll", "-DispatchDir", str(tmp_path / "d"),
                          "-WrapperBody", str(tmp_path / "w.ps1"),
                          "-ReceiptPath", str(tmp_path / "r.json"), "-Round", "R1",
                          "-Receipt", str(tmp_path / "r.json"),
                          "-ExpectedDispatchDir", str(tmp_path / "d"), "-ExpectedRound", "R1"])
    assert both.returncode == 2, (both.stdout, both.stderr)

    incomplete_poll = run_dispatch(["-Poll", "-Receipt", str(tmp_path / "r.json")])
    assert incomplete_poll.returncode == 2, (incomplete_poll.stdout, incomplete_poll.stderr)


# ---------------------------------------------------------------------
# The documented outer commands, verbatim: prepare, run the wrapper the
# way the harness now does, then poll.
# ---------------------------------------------------------------------
def test_the_documented_outer_command_works_on_this_host(tmp_path):
    # Step 0 measured (2026-08-31, Claude Code 2.1.251, see
    # docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/
    # wrapper-probe.md) that the Claude Code harness substitutes
    # ${CLAUDE_PLUGIN_ROOT} in plugin skill body text with an absolute
    # path before the model ever sees it. This test performs that same
    # substitution itself, with REPO as the value, because it exercises
    # the script straight from the checkout rather than an installed
    # plugin cache copy - it is doing, in the test host, exactly what the
    # skill relies on the harness to do at model-invocation time.
    dispatch_dir = tmp_path / "outer-dispatch"
    receipt_path = tmp_path / "outer-receipt.json"
    wrapper = write_wrapper(tmp_path, FAST_WRAPPER, "outer-wrapper.ps1")

    prepare_cmd = (
        '& (Get-Process -Id $PID).Path -NoProfile -File '
        '${CLAUDE_PLUGIN_ROOT}/tools/dispatch-detached.ps1 -Prepare '
        f'-DispatchDir "{dispatch_dir}" -WrapperBody "{wrapper}" '
        f'-ReceiptPath "{receipt_path}" -Round OuterR1 -Json'
    ).replace("${CLAUDE_PLUGIN_ROOT}", str(REPO))
    result = subprocess.run([POWERSHELL, "-NoProfile", "-NonInteractive", "-Command", prepare_cmd],
                             capture_output=True, text=True, timeout=30)
    assert result.returncode == 0, (result.stdout, result.stderr)

    # The caller runs the prepared wrapper itself, as a tracked background
    # command - see the skill and the design spec. This test stands in
    # for that with a plain background process.
    wrapper_proc = _run_wrapper_in_background(dispatch_dir)
    try:
        assert _wait_for(dispatch_dir / "exit", timeout=15)
        assert _wait_for(dispatch_dir / "reply", timeout=15)
    finally:
        wrapper_proc.wait(timeout=30)

    poll_cmd = (
        '& (Get-Process -Id $PID).Path -NoProfile -File '
        '${CLAUDE_PLUGIN_ROOT}/tools/dispatch-detached.ps1 -Poll '
        f'-Receipt "{receipt_path}" -ExpectedDispatchDir "{dispatch_dir}" '
        '-ExpectedRound OuterR1 -Json'
    ).replace("${CLAUDE_PLUGIN_ROOT}", str(REPO))
    poll_result = subprocess.run([POWERSHELL, "-NoProfile", "-NonInteractive", "-Command", poll_cmd],
                                  capture_output=True, text=True, timeout=30)
    assert poll_result.returncode == 0, (poll_result.stdout, poll_result.stderr)
    obj = json.loads(poll_result.stdout.strip())
    assert obj["state"] == "reply-present"
    assert obj["round"] == "OuterR1"
