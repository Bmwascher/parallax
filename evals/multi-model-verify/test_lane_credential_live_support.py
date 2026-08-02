"""Offline oracles for the locking and secret-guard machinery that the
kimi-code lane-credential live gate (Task 7, 2026-08-01
lane-credential-and-lock plan) depends on but does not itself prove.

test_lane_credential_live.py's seven items test the CLIENT: none of them
proves the runner actually acquired the intended home's lock, released it
afterwards, or caught a credential value in a captured stream - a runner
with no locking and no secret guard at all would pass every one of them.
This module drives evals/tools/lane_credential_live_support.py - the SAME
production helper the live suite imports - against FAKE commands, real
disposable lane homes, and the real tools/kimi-lane-lock.ps1 and
tools/new-kimi-lane-home.ps1. No real credential, and no PARALLAX_LANE_LIVE
opt-in required: its lock cases are PowerShell-facing (real Windows file
locking, real ACLs, real junctions), not client-facing.

WINDOWS ONLY, same pattern as test_kimi_lane_home.py: a selector that
merely finds A PowerShell host would happily collect these on Ubuntu CI
too, where pwsh is on PATH but the Windows filesystem behaviour under
test does not exist. A green suite on one Windows host proves ONE
interpreter, which is why the plan's own verification runs this module
twice, once per host.
"""
import importlib.util as _importlib_util
import json
import os
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
_SUPPORT_MODULE_PATH = REPO / "evals" / "tools" / "lane_credential_live_support.py"


def _load_support():
    """The repo's own convention for importing an evals/tools module from
    evals/multi-model-verify (test_backup_lane.py's
    _load_check_workflow_paths): no conftest.py puts evals/tools on
    sys.path, so a plain `import` fails."""
    if "lane_credential_live_support" not in sys.modules:
        spec = _importlib_util.spec_from_file_location(
            "lane_credential_live_support", _SUPPORT_MODULE_PATH)
        module = _importlib_util.module_from_spec(spec)
        sys.modules["lane_credential_live_support"] = module
        spec.loader.exec_module(module)
    return sys.modules["lane_credential_live_support"]


support = _load_support()

POWERSHELL = support.resolve_ps_host()

pytestmark = pytest.mark.skipif(
    os.name != "nt" or POWERSHELL is None,
    reason="this suite drives real Windows locking, ACL, and junction "
           "behaviour through tools/kimi-lane-lock.ps1 and "
           "tools/new-kimi-lane-home.ps1; it needs a PowerShell host and "
           "the platform it actually targets")


# =======================================================================
# Fixtures. A disposable fake USERPROFILE carrying a fake config.toml (so
# the real builder can render a home) and disposable fake lane homes
# carrying a structurally-valid FAKE credential - the same shape
# test_kimi_lane_home.py already uses, duplicated locally rather than
# imported, because that file is a sibling contract-pin module this task
# must not rewrite.
# =======================================================================
PLACEHOLDER_MODEL = "kimi-code/support-test-placeholder-model"

FAKE_REAL_CONFIG = '''default_model = "kimi-code/some-other-model"

[providers."managed:kimi-code"]
type = "kimi"
api_key = ""
base_url = "https://api.kimi.com/coding/v1"

[models."%s"]
provider = "managed:kimi-code"
model = "support-test-placeholder-model"
max_context_size = 262144
capabilities = [ "thinking", "tool_use" ]
display_name = "Support Test Placeholder"
support_efforts = [ "low", "high" ]
default_effort = "low"

[thinking]
enabled = true
''' % PLACEHOLDER_MODEL

VALID_CREDENTIAL_JSON = (
    '{"access_token": "fake-access-token-not-real", '
    '"refresh_token": "fake-refresh-token-not-real", '
    '"expires_at": 900}')


def _fake_profile(tmp_path, name="fake-profile"):
    profile = tmp_path / name
    kimi = profile / ".kimi-code"
    kimi.mkdir(parents=True)
    (kimi / "config.toml").write_text(FAKE_REAL_CONFIG, encoding="ascii")
    return profile


def _fake_lane_home(tmp_path, name="lane-home", credential_text=VALID_CREDENTIAL_JSON):
    lane_home = tmp_path / name
    cred_dir = lane_home / "credentials"
    cred_dir.mkdir(parents=True)
    (cred_dir / "kimi-code.json").write_text(credential_text, encoding="ascii")
    return lane_home


def _build_env(profile):
    return support.clean_env({"USERPROFILE": str(profile)})


@pytest.fixture(scope="module")
def module_owner():
    """Resolved ONCE per module run, per the plan's own rule for the live
    suite - -ResolveOwner reports the PARENT of the PowerShell process it
    runs in, which here is this pytest process itself: a real, live
    process for the whole test session."""
    return support.resolve_owner(POWERSHELL)


def _spawn_live_holder():
    """A real, alive process to serve as a DIFFERENT owner's identity for
    the contention oracles - the stronger oracle over an invented seam,
    matching test_kimi_lane_home.py's own fixture."""
    proc = subprocess.Popen(
        [POWERSHELL, "-NoProfile", "-Command", "Start-Sleep -Seconds 120"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    query = subprocess.run(
        [POWERSHELL, "-NoProfile", "-Command",
         "(Get-Process -Id %d).StartTime.ToUniversalTime().Ticks" % proc.pid],
        capture_output=True, text=True, timeout=30)
    assert query.returncode == 0, query.stdout + query.stderr
    return proc, str(proc.pid), query.stdout.strip()


def _kill_holder(proc):
    try:
        proc.terminate()
        proc.wait(timeout=15)
    except Exception:
        try:
            proc.kill()
        except Exception:
            pass


def _write_fake_command(tmp_path, name, body):
    """A standalone Python script standing in for the real kimi-code
    client, invoked as [sys.executable, path]."""
    script = tmp_path / name
    script.write_text(body, encoding="utf-8")
    return [sys.executable, str(script)]


def _lock_status(lane_home):
    return support.lock_status(POWERSHELL, lane_home)


def _read_lock_bytes(lane_home):
    return support.read_lock_bytes(lane_home)


def _corrupt_sentinel(debate_home):
    (Path(debate_home) / support.SENTINEL_NAME).write_text(
        "not the real sentinel", encoding="ascii")


def _repair_sentinel(debate_home):
    resolved = str(Path(debate_home).resolve())
    (Path(debate_home) / support.SENTINEL_NAME).write_text(
        "\n".join(["PARALLAX-LANE-HOME-V1", resolved]), encoding="ascii")


# =======================================================================
# 1. A pre-held lock (different live owner) blocks Build: the fake
# command is never invoked, -Remove is never attempted, and the pre-held
# record is byte-identical afterwards.
# =======================================================================
def test_a_preheld_lock_blocks_build_for_three_fixture_homes(tmp_path, module_owner, monkeypatch):
    profile = _fake_profile(tmp_path)
    called_remove = []
    monkeypatch.setattr(support, "remove_lane_home",
                         lambda *a, **k: called_remove.append(1) or pytest.fail(
                             "-Remove must never be attempted after a refused Build"))

    for label in ("home-a", "home-b", "home-c"):
        lane_home = _fake_lane_home(tmp_path, name=label)
        target = tmp_path / (label + "-debate-home")
        holder_proc, holder_pid, holder_ticks = _spawn_live_holder()
        try:
            holder_debate_id = support.new_hex32()
            acquire = support.lock_acquire(
                POWERSHELL, lane_home, holder_debate_id, holder_pid, holder_ticks,
                str(tmp_path / (label + "-holder-debate-home")))
            assert acquire.returncode == 0, acquire.stdout + acquire.stderr
            holder_nonce = acquire.stdout.strip()
            before = _read_lock_bytes(lane_home)

            command_marker = tmp_path / (label + "-command-ran.txt")
            with pytest.raises(support.BuildRefusal):
                with support.custody_of(
                        POWERSHELL, target, PLACEHOLDER_MODEL, "high", lane_home,
                        support.new_hex32(), module_owner.owner_pid,
                        module_owner.owner_ticks, build_env=_build_env(profile)) as custody:
                    command_marker.write_text("ran", encoding="ascii")
                    pytest.fail("Build refused; the with-block body must never run")

            assert not command_marker.exists(), "the fake command must never be invoked"
            assert not target.exists()
            assert _read_lock_bytes(lane_home) == before, "a Build refusal must not mutate the held record"
        finally:
            support.lock_release(POWERSHELL, lane_home, holder_debate_id,
                                  holder_pid, holder_ticks, holder_nonce)
            _kill_holder(holder_proc)

    assert called_remove == []


# =======================================================================
# 2. The seed step: a pre-held home refuses (credential never read); a
# successful seed reads the credential and leaves the record exactly
# free.
# =======================================================================
def test_a_preheld_lock_blocks_the_seed_step_and_reads_no_credential(
        tmp_path, module_owner, monkeypatch):
    lane_home = _fake_lane_home(tmp_path)
    guard = support.SecretGuard()
    read_calls = []
    monkeypatch.setattr(support, "reread_and_merge_credential",
                         lambda *a, **k: read_calls.append(1))

    holder_proc, holder_pid, holder_ticks = _spawn_live_holder()
    try:
        holder_debate_id = support.new_hex32()
        acquire = support.lock_acquire(
            POWERSHELL, lane_home, holder_debate_id, holder_pid, holder_ticks,
            str(tmp_path / "holder-debate-home"))
        assert acquire.returncode == 0, acquire.stdout + acquire.stderr
        holder_nonce = acquire.stdout.strip()

        with pytest.raises(support.SeedAcquireFailure):
            with support.seed_hold(POWERSHELL, lane_home, support.new_hex32(),
                                    module_owner.owner_pid, module_owner.owner_ticks) as nonce:
                guard.merge_credential_file(lane_home / "credentials" / "kimi-code.json")
                pytest.fail("seed acquire refused; the body must never run")

        assert read_calls == []
        assert guard._secrets == {}, "a refused seed must never read the credential"
    finally:
        support.lock_release(POWERSHELL, lane_home, holder_debate_id,
                              holder_pid, holder_ticks, holder_nonce)
        _kill_holder(holder_proc)


def test_a_successful_seed_reads_the_credential_and_leaves_the_record_free(
        tmp_path, module_owner):
    lane_home = _fake_lane_home(tmp_path)
    guard = support.SecretGuard()

    with support.seed_hold(POWERSHELL, lane_home, support.new_hex32(),
                            module_owner.owner_pid, module_owner.owner_ticks) as nonce:
        assert support.is_hex32(nonce)
        merged = guard.merge_credential_file(lane_home / "credentials" / "kimi-code.json")
        assert merged

    assert guard.find_match("fake-access-token-not-real") == "access_token"
    status = _lock_status(lane_home)
    assert status == {"state": "free"}


# =======================================================================
# 3. Contention against a builder-retained hold is observed both during
# the pre-command phase and WHILE the client process is still running -
# not merely after it has already exited, which is a weaker claim: the
# fake command below blocks until explicitly released, so the second
# acquire attempt genuinely lands during the client's execution window.
# =======================================================================
def test_contention_against_the_builder_hold_spans_precommand_and_command(
        tmp_path, module_owner):
    profile = _fake_profile(tmp_path)
    lane_home = _fake_lane_home(tmp_path)
    target = tmp_path / "contended-debate-home"
    guard = support.SecretGuard()

    ready_signal = tmp_path / "fake-client-ready.txt"
    release_signal = tmp_path / "fake-client-release.txt"
    fake = _write_fake_command(
        tmp_path, "fake-client-blocking.py",
        "import sys, time, pathlib\n"
        "ready = pathlib.Path(%r)\n"
        "release = pathlib.Path(%r)\n"
        "ready.write_text('ready', encoding='ascii')\n"
        "deadline = time.time() + 60\n"
        "while not release.exists():\n"
        "    if time.time() > deadline:\n"
        "        sys.exit(2)\n"
        "    time.sleep(0.05)\n"
        "sys.stdout.write('PROBE\\n')\n"
        % (str(ready_signal), str(release_signal)))

    holder_proc, holder_pid, holder_ticks = _spawn_live_holder()
    dispatch_outcome = {}

    def _run_dispatch():
        try:
            dispatch_outcome["result"] = support.dispatch_and_guard(fake, guard, timeout=30)
        except BaseException as exc:  # captured and re-raised on the main thread
            dispatch_outcome["exc"] = exc

    try:
        with support.custody_of(
                POWERSHELL, target, PLACEHOLDER_MODEL, "high", lane_home,
                support.new_hex32(), module_owner.owner_pid, module_owner.owner_ticks,
                build_env=_build_env(profile)) as custody:
            # Pre-command phase: attempt a second acquire from a DIFFERENT
            # live owner while the builder's own hold is retained.
            pre_attempt = support.lock_acquire(
                POWERSHELL, lane_home, support.new_hex32(), holder_pid, holder_ticks,
                str(tmp_path / "other-debate-home-1"))
            assert pre_attempt.returncode == 3, pre_attempt.stdout + pre_attempt.stderr

            dispatch_thread = threading.Thread(target=_run_dispatch)
            dispatch_thread.start()

            # Wait for the fake command's OWN readiness signal - proof it
            # has started and is now blocked, not merely "invoked".
            deadline = time.time() + 30
            while not ready_signal.exists():
                if time.time() > deadline:
                    pytest.fail("the fake command never signaled readiness")
                time.sleep(0.05)

            # WHILE the client process is still blocked: contention must
            # be observed against the SAME retained hold.
            during_attempt = support.lock_acquire(
                POWERSHELL, lane_home, support.new_hex32(), holder_pid, holder_ticks,
                str(tmp_path / "other-debate-home-2"))
            assert during_attempt.returncode == 3, during_attempt.stdout + during_attempt.stderr

            release_signal.write_text("go", encoding="ascii")
            dispatch_thread.join(timeout=30)
            assert not dispatch_thread.is_alive(), "the fake command never finished"
    finally:
        _kill_holder(holder_proc)

    if "exc" in dispatch_outcome:
        raise dispatch_outcome["exc"]
    result = dispatch_outcome["result"]
    assert result.returncode == 0
    assert "PROBE" in result.stdout

    assert _lock_status(lane_home) == {"state": "free"}
    assert not target.exists()


# =======================================================================
# 4. Cleanup runs through the real -Remove after BOTH a zero and a
# nonzero fake-command exit, leaving the debate home ABSENT and the lock
# record exactly free.
# =======================================================================
@pytest.mark.parametrize("exit_code", [0, 1])
def test_cleanup_runs_after_both_a_zero_and_nonzero_command_exit(
        tmp_path, module_owner, exit_code):
    profile = _fake_profile(tmp_path)
    lane_home = _fake_lane_home(tmp_path, name="lane-home-%d" % exit_code)
    target = tmp_path / ("exit-%d-debate-home" % exit_code)
    guard = support.SecretGuard()

    fake = _write_fake_command(
        tmp_path, "fake-client-exit-%d.py" % exit_code,
        "import sys; sys.stdout.write('PROBE\\n'); sys.exit(%d)" % exit_code)

    with support.custody_of(
            POWERSHELL, target, PLACEHOLDER_MODEL, "high", lane_home,
            support.new_hex32(), module_owner.owner_pid, module_owner.owner_ticks,
            build_env=_build_env(profile)) as custody:
        result = support.dispatch_and_guard(fake, guard, timeout=30)
        assert result.returncode == exit_code

    assert not target.exists()
    assert _lock_status(lane_home) == {"state": "free"}


# =======================================================================
# 5. Cleanup precedence, the frozen three-row matrix.
# =======================================================================
def test_precedence_main_failure_remove_succeeds(tmp_path, module_owner):
    profile = _fake_profile(tmp_path)
    lane_home = _fake_lane_home(tmp_path, name="precedence-1")
    target = tmp_path / "precedence-1-home"

    with pytest.raises(support.DispatchLaunchFailure):
        with support.custody_of(
                POWERSHELL, target, PLACEHOLDER_MODEL, "high", lane_home,
                support.new_hex32(), module_owner.owner_pid, module_owner.owner_ticks,
                build_env=_build_env(profile)):
            support.dispatch_and_guard(
                [str(tmp_path / "does-not-exist.exe")], support.SecretGuard(), timeout=10)

    assert not target.exists(), "Remove succeeded, so the debate home is gone"
    assert _lock_status(lane_home) == {"state": "free"}


def _phase_fail_pre_command(custody, tmp_path):
    """Stands in for a PRE-COMMAND phase failure - a deliberate
    credential mutation or measurement gone wrong before any command has
    even run."""
    raise RuntimeError("simulated pre-command phase failure")


def _phase_fail_command_capture(custody, tmp_path):
    support.dispatch_and_guard(
        [str(tmp_path / "does-not-exist.exe")], support.SecretGuard(), timeout=10)


def _phase_fail_merge(custody, tmp_path):
    fake = _write_fake_command(
        tmp_path, "fake-client-phase-merge.py",
        "import sys; sys.stdout.write('PROBE\\n')")
    broken_path = Path(custody.debate_home) / "credentials" / "nonexistent-file.json"
    support.dispatch_and_guard(fake, support.SecretGuard(), timeout=30, cred_path=broken_path)


def _phase_fail_guard(custody, tmp_path):
    guard = support.SecretGuard()
    guard.merge_values({"access_token": "PHASE-GUARD-MATCH-VALUE"})
    fake = _write_fake_command(
        tmp_path, "fake-client-phase-guard.py",
        "import sys; sys.stdout.write('PHASE-GUARD-MATCH-VALUE\\n')")
    support.dispatch_and_guard(fake, guard, timeout=30)


# The four main phases inside custody (packet "The MAIN OPERATION is all
# four phases inside custody"): pre-command, command/capture, the
# post-command merge, and the stream guard. Each must reach the SAME
# sentinel-refusal precedence, not only command launch failure.
_MAIN_PHASE_FAILURES = [
    ("pre_command", _phase_fail_pre_command, RuntimeError),
    ("command_capture", _phase_fail_command_capture, support.DispatchLaunchFailure),
    ("merge", _phase_fail_merge, support.DispatchReadFailure),
    ("guard", _phase_fail_guard, support.SecretGuardViolation),
]


@pytest.mark.parametrize("phase_name,fail_fn,exc_type", _MAIN_PHASE_FAILURES,
                          ids=[p[0] for p in _MAIN_PHASE_FAILURES])
def test_precedence_main_failure_remove_also_fails_sentinel_refusal(
        tmp_path, module_owner, phase_name, fail_fn, exc_type):
    profile = _fake_profile(tmp_path)
    lane_home = _fake_lane_home(tmp_path, name="precedence-2-%s" % phase_name)
    target = tmp_path / ("precedence-2-%s-home" % phase_name)

    lock_before = None
    debate_home_seen = None
    try:
        with pytest.raises(exc_type):
            with support.custody_of(
                    POWERSHELL, target, PLACEHOLDER_MODEL, "high", lane_home,
                    support.new_hex32(), module_owner.owner_pid, module_owner.owner_ticks,
                    build_env=_build_env(profile)) as custody:
                debate_home_seen = custody.debate_home
                lock_before = _read_lock_bytes(lane_home)
                _corrupt_sentinel(custody.debate_home)
                fail_fn(custody, tmp_path)

        assert Path(debate_home_seen).exists(), "a sentinel refusal must never delete"
        assert _read_lock_bytes(lane_home) == lock_before
        assert _lock_status(lane_home)["state"] == "held"
    finally:
        if debate_home_seen and Path(debate_home_seen).exists():
            _repair_sentinel(debate_home_seen)
            status = _lock_status(lane_home)
            if status.get("state") == "held":
                support.remove_lane_home(
                    POWERSHELL, debate_home_seen, lane_home, status["debateId"],
                    status["ownerPid"], status["ownerStartTicksUtc"], status["nonce"])


def test_precedence_all_succeed_remove_fails_sentinel_refusal(tmp_path, module_owner):
    profile = _fake_profile(tmp_path)
    lane_home = _fake_lane_home(tmp_path, name="precedence-3")
    target = tmp_path / "precedence-3-home"
    guard = support.SecretGuard()

    lock_before = None
    debate_home_seen = None
    try:
        with pytest.raises(support.RemoveFailure):
            with support.custody_of(
                    POWERSHELL, target, PLACEHOLDER_MODEL, "high", lane_home,
                    support.new_hex32(), module_owner.owner_pid, module_owner.owner_ticks,
                    build_env=_build_env(profile)) as custody:
                debate_home_seen = custody.debate_home
                fake = _write_fake_command(
                    tmp_path, "fake-client-precedence-3.py",
                    "import sys; sys.stdout.write('PROBE\\n')")
                result = support.dispatch_and_guard(fake, guard, timeout=30)
                assert result.returncode == 0
                lock_before = _read_lock_bytes(lane_home)
                _corrupt_sentinel(custody.debate_home)

        assert Path(debate_home_seen).exists()
        assert _read_lock_bytes(lane_home) == lock_before
        assert _lock_status(lane_home)["state"] == "held"
    finally:
        if debate_home_seen and Path(debate_home_seen).exists():
            _repair_sentinel(debate_home_seen)
            status = _lock_status(lane_home)
            if status.get("state") == "held":
                support.remove_lane_home(
                    POWERSHELL, debate_home_seen, lane_home, status["debateId"],
                    status["ownerPid"], status["ownerStartTicksUtc"], status["nonce"])


# =======================================================================
# 5b. A cleanup call that THROWS (a timeout, a launch failure - not only
# a nonzero return) may not mask the main failure. custody_of and
# seed_hold each capture the cleanup invocation's own exception
# separately so a raise from the remover/release cannot skip the
# `raise main_exc` that follows.
# =======================================================================
def test_custody_remove_throws_timeout_does_not_mask_main_failure(
        tmp_path, module_owner, monkeypatch):
    profile = _fake_profile(tmp_path)
    lane_home = _fake_lane_home(tmp_path, name="remove-throws-timeout")
    target = tmp_path / "remove-throws-timeout-home"
    remove_calls = []

    def _throwing_remove(*a, **k):
        remove_calls.append(1)
        raise subprocess.TimeoutExpired(cmd=["kimi-lane-lock.ps1"], timeout=1)

    monkeypatch.setattr(support, "remove_lane_home", _throwing_remove)

    with pytest.raises(support.DispatchLaunchFailure):
        with support.custody_of(
                POWERSHELL, target, PLACEHOLDER_MODEL, "high", lane_home,
                support.new_hex32(), module_owner.owner_pid, module_owner.owner_ticks,
                build_env=_build_env(profile)):
            support.dispatch_and_guard(
                [str(tmp_path / "does-not-exist.exe")], support.SecretGuard(), timeout=10)

    assert remove_calls == [1], "the remover must still be ATTEMPTED even though it throws"


def test_custody_remove_throws_launch_failure_does_not_mask_main_failure(
        tmp_path, module_owner, monkeypatch):
    profile = _fake_profile(tmp_path)
    lane_home = _fake_lane_home(tmp_path, name="remove-throws-launch")
    target = tmp_path / "remove-throws-launch-home"
    remove_calls = []

    def _throwing_remove(*a, **k):
        remove_calls.append(1)
        raise FileNotFoundError("simulated remover launch failure")

    monkeypatch.setattr(support, "remove_lane_home", _throwing_remove)

    with pytest.raises(support.DispatchLaunchFailure):
        with support.custody_of(
                POWERSHELL, target, PLACEHOLDER_MODEL, "high", lane_home,
                support.new_hex32(), module_owner.owner_pid, module_owner.owner_ticks,
                build_env=_build_env(profile)):
            support.dispatch_and_guard(
                [str(tmp_path / "does-not-exist.exe")], support.SecretGuard(), timeout=10)

    assert remove_calls == [1], "the remover must still be ATTEMPTED even though it throws"


def test_seed_release_throws_timeout_does_not_mask_main_failure(
        tmp_path, module_owner, monkeypatch):
    lane_home = _fake_lane_home(tmp_path, name="seed-release-throws-timeout")
    release_calls = []

    def _throwing_release(*a, **k):
        release_calls.append(1)
        raise subprocess.TimeoutExpired(cmd=["kimi-lane-lock.ps1"], timeout=1)

    monkeypatch.setattr(support, "lock_release", _throwing_release)

    class _FakeSeedMainFailureTimeout(Exception):
        pass

    with pytest.raises(_FakeSeedMainFailureTimeout):
        with support.seed_hold(POWERSHELL, lane_home, support.new_hex32(),
                                module_owner.owner_pid, module_owner.owner_ticks):
            raise _FakeSeedMainFailureTimeout("simulated seed main failure")

    assert release_calls == [1], "the release must still be ATTEMPTED even though it throws"


def test_seed_release_throws_launch_failure_does_not_mask_main_failure(
        tmp_path, module_owner, monkeypatch):
    lane_home = _fake_lane_home(tmp_path, name="seed-release-throws-launch")
    release_calls = []

    def _throwing_release(*a, **k):
        release_calls.append(1)
        raise FileNotFoundError("simulated release launch failure")

    monkeypatch.setattr(support, "lock_release", _throwing_release)

    class _FakeSeedMainFailureLaunch(Exception):
        pass

    with pytest.raises(_FakeSeedMainFailureLaunch):
        with support.seed_hold(POWERSHELL, lane_home, support.new_hex32(),
                                module_owner.owner_pid, module_owner.owner_ticks):
            raise _FakeSeedMainFailureLaunch("simulated seed main failure")

    assert release_calls == [1], "the release must still be ATTEMPTED even though it throws"


# =======================================================================
# 6. Seed precedence, the three directions.
# =======================================================================
def test_seed_read_failure_with_succeeding_release_reports_the_seed_failure(
        tmp_path, module_owner):
    lane_home = _fake_lane_home(tmp_path, name="seed-precedence-1")

    class _FakeSeedReadFailure(Exception):
        pass

    with pytest.raises(_FakeSeedReadFailure):
        with support.seed_hold(POWERSHELL, lane_home, support.new_hex32(),
                                module_owner.owner_pid, module_owner.owner_ticks):
            raise _FakeSeedReadFailure("simulated seed read failure")

    assert _lock_status(lane_home) == {"state": "free"}


def test_seed_read_failure_with_failing_release_reports_the_seed_failure(
        tmp_path, module_owner):
    lane_home = _fake_lane_home(tmp_path, name="seed-precedence-2")
    debate_id = support.new_hex32()

    class _FakeSeedReadFailure(Exception):
        pass

    release_calls = []

    with pytest.raises(_FakeSeedReadFailure):
        with support.seed_hold(POWERSHELL, lane_home, debate_id,
                                module_owner.owner_pid, module_owner.owner_ticks) as nonce:
            # Deterministically make the eventual finally-release fail: free
            # the record early, under the correct identity, so the
            # finally's own release call finds nothing to release (exit 5).
            early = support.lock_release(POWERSHELL, lane_home, debate_id,
                                          module_owner.owner_pid, module_owner.owner_ticks, nonce)
            release_calls.append(early.returncode)
            assert early.returncode == 0
            raise _FakeSeedReadFailure("simulated seed read failure")

    assert release_calls == [0], "the release was attempted before the deliberate early free"
    assert _lock_status(lane_home) == {"state": "free"}


def test_successful_seed_read_with_failing_release_reports_the_release_failure(
        tmp_path, module_owner):
    lane_home = _fake_lane_home(tmp_path, name="seed-precedence-3")
    debate_id = support.new_hex32()

    with pytest.raises(support.SeedReleaseFailure):
        with support.seed_hold(POWERSHELL, lane_home, debate_id,
                                module_owner.owner_pid, module_owner.owner_ticks) as nonce:
            early = support.lock_release(POWERSHELL, lane_home, debate_id,
                                          module_owner.owner_pid, module_owner.owner_ticks, nonce)
            assert early.returncode == 0

    assert _lock_status(lane_home) == {"state": "free"}


# =======================================================================
# 7. The three sanitized exception paths, each still cleans up.
# =======================================================================
def test_a_timeout_with_a_known_secret_produces_a_field_only_failure(tmp_path, module_owner):
    profile = _fake_profile(tmp_path)
    lane_home = _fake_lane_home(tmp_path, name="timeout-guard")
    target = tmp_path / "timeout-guard-home"
    guard = support.SecretGuard()
    guard.merge_values({"access_token": "TIMEOUT-FIELD-SECRET-VALUE"})

    fake = _write_fake_command(
        tmp_path, "fake-timeout.py",
        "import sys, time\n"
        "sys.stdout.write('TIMEOUT-FIELD-SECRET-VALUE\\n')\n"
        "sys.stdout.flush()\n"
        "time.sleep(3600)\n")

    with pytest.raises(support.SecretGuardViolation) as excinfo:
        with support.custody_of(
                POWERSHELL, target, PLACEHOLDER_MODEL, "high", lane_home,
                support.new_hex32(), module_owner.owner_pid, module_owner.owner_ticks,
                build_env=_build_env(profile)):
            support.dispatch_and_guard(fake, guard, timeout=2)

    assert excinfo.value.field == "access_token"
    assert "TIMEOUT-FIELD-SECRET-VALUE" not in str(excinfo.value)
    assert not target.exists()
    assert _lock_status(lane_home) == {"state": "free"}


def test_a_timeout_with_no_known_secret_produces_a_fixed_sanitized_message(tmp_path, module_owner):
    profile = _fake_profile(tmp_path)
    lane_home = _fake_lane_home(tmp_path, name="timeout-plain")
    target = tmp_path / "timeout-plain-home"
    guard = support.SecretGuard()  # empty: nothing to match

    fake = _write_fake_command(
        tmp_path, "fake-timeout-plain.py",
        "import sys, time\n"
        "sys.stdout.write('some unrelated output, not a tracked secret\\n')\n"
        "sys.stdout.flush()\n"
        "time.sleep(3600)\n")

    with pytest.raises(support.DispatchTimeout) as excinfo:
        with support.custody_of(
                POWERSHELL, target, PLACEHOLDER_MODEL, "high", lane_home,
                support.new_hex32(), module_owner.owner_pid, module_owner.owner_ticks,
                build_env=_build_env(profile)):
            support.dispatch_and_guard(fake, guard, timeout=2)

    assert str(excinfo.value) == "client dispatch timed out"
    assert "unrelated output" not in str(excinfo.value)
    assert not target.exists()
    assert _lock_status(lane_home) == {"state": "free"}


def test_a_nonexistent_executable_produces_a_sanitized_launch_failure(tmp_path, module_owner):
    profile = _fake_profile(tmp_path)
    lane_home = _fake_lane_home(tmp_path, name="launch-failure")
    target = tmp_path / "launch-failure-home"

    with pytest.raises(support.DispatchLaunchFailure) as excinfo:
        with support.custody_of(
                POWERSHELL, target, PLACEHOLDER_MODEL, "high", lane_home,
                support.new_hex32(), module_owner.owner_pid, module_owner.owner_ticks,
                build_env=_build_env(profile)):
            support.dispatch_and_guard(
                [str(tmp_path / "definitely-does-not-exist.exe")],
                support.SecretGuard(), timeout=10)

    assert str(excinfo.value) == "client dispatch failed: the process could not be launched"
    assert not hasattr(excinfo.value, "field")
    assert not target.exists()
    assert _lock_status(lane_home) == {"state": "free"}


def test_a_postcommand_readorparse_fault_produces_a_value_free_failure(tmp_path, module_owner):
    profile = _fake_profile(tmp_path)
    lane_home = _fake_lane_home(tmp_path, name="read-parse-fault")
    target = tmp_path / "read-parse-fault-home"
    guard = support.SecretGuard()

    with pytest.raises(support.DispatchReadFailure) as excinfo:
        with support.custody_of(
                POWERSHELL, target, PLACEHOLDER_MODEL, "high", lane_home,
                support.new_hex32(), module_owner.owner_pid, module_owner.owner_ticks,
                build_env=_build_env(profile)) as custody:
            fake = _write_fake_command(
                tmp_path, "fake-rotate-badly.py",
                "import sys; sys.stdout.write('PROBE\\n')")
            result = support.dispatch_and_guard(fake, guard, timeout=30)
            assert result.returncode == 0
            broken_path = Path(custody.debate_home) / "credentials" / "nonexistent-file.json"
            support.reread_and_merge_credential(guard, broken_path)

    assert str(excinfo.value) == "post-command credential read-or-parse failed"
    assert not hasattr(excinfo.value, "field")
    assert not target.exists()
    assert _lock_status(lane_home) == {"state": "free"}


# =======================================================================
# 8. The guard fires on a value in stdout, and separately in stderr.
# =======================================================================
def test_guard_fires_on_a_match_in_stdout():
    guard = support.SecretGuard()
    guard.merge_values({"refresh_token": "STDOUT-MATCH-VALUE"})
    with pytest.raises(support.SecretGuardViolation) as excinfo:
        support.dispatch_and_guard(
            [sys.executable, "-c", "import sys; sys.stdout.write('STDOUT-MATCH-VALUE\\n')"],
            guard, timeout=30)
    assert excinfo.value.field == "refresh_token"
    assert "STDOUT-MATCH-VALUE" not in str(excinfo.value)


def test_guard_fires_on_a_match_in_stderr():
    guard = support.SecretGuard()
    guard.merge_values({"access_token": "STDERR-MATCH-VALUE"})
    with pytest.raises(support.SecretGuardViolation) as excinfo:
        support.dispatch_and_guard(
            [sys.executable, "-c", "import sys; sys.stderr.write('STDERR-MATCH-VALUE\\n')"],
            guard, timeout=30)
    assert excinfo.value.field == "access_token"
    assert "STDERR-MATCH-VALUE" not in str(excinfo.value)


# =======================================================================
# 9. A rotated credential's NEW value is caught only because of the
# merge-after-command rule; a seed-once implementation would miss it.
# =======================================================================
def test_merge_after_command_catches_a_rotated_value(tmp_path):
    """SECURITY (r31): the post-command merge happens INSIDE
    dispatch_and_guard, before either stream is scanned. ONE fake command
    both WRITES a new credential value and EMITS that same new value in
    the SAME invocation - a command that merely echoes a pre-written
    value does not reach this path, because a seed-once (or a
    merge-after-return) implementation would have already missed the
    value by the time the command's own stdout is scanned."""
    guard = support.SecretGuard()
    guard.merge_values({"access_token": "OLD-VALUE-BEFORE-ROTATION"})

    cred_file = tmp_path / "rotated-credential.json"
    cred_file.write_text(
        json.dumps({"access_token": "OLD-VALUE-BEFORE-ROTATION",
                    "refresh_token": "still-here", "expires_at": 1234}),
        encoding="ascii")

    fake = _write_fake_command(
        tmp_path, "fake-rotate-and-emit.py",
        "import json, sys\n"
        "with open(%r, 'w') as fh:\n"
        "    json.dump({'access_token': 'NEW-VALUE-AFTER-ROTATION', "
        "'refresh_token': 'still-here', 'expires_at': 1234}, fh)\n"
        "sys.stdout.write('NEW-VALUE-AFTER-ROTATION\\n')\n" % str(cred_file))

    with pytest.raises(support.SecretGuardViolation) as excinfo:
        support.dispatch_and_guard(fake, guard, timeout=30, cred_path=cred_file)

    assert excinfo.value.field == "access_token"
    assert "NEW-VALUE-AFTER-ROTATION" not in str(excinfo.value)


# =======================================================================
# 10. Snapshot measurement: a failed component raises rather than
# returning a comparable sentinel.
# =======================================================================
def test_measure_file_snapshot_succeeds_when_all_three_components_succeed(tmp_path):
    p = tmp_path / "snapshot-target.bin"
    p.write_bytes(b"some bytes")
    snap = support.measure_file_snapshot(p)
    assert len(snap.sha256) == 64
    assert snap.length == len(b"some bytes")
    assert isinstance(snap.mtime_ns, int)


def test_measure_file_snapshot_hash_failure_raises_not_a_sentinel(tmp_path, monkeypatch):
    p = tmp_path / "snapshot-target.bin"
    p.write_bytes(b"some bytes")

    def _broken_hash(path):
        raise OSError("simulated hash failure")

    monkeypatch.setattr(support, "_read_and_hash", _broken_hash)
    with pytest.raises(support.SnapshotMeasurementError, match="hash measurement failed"):
        support.measure_file_snapshot(p)


def test_measure_file_snapshot_stat_failure_raises_not_a_sentinel(tmp_path, monkeypatch):
    p = tmp_path / "snapshot-target.bin"
    p.write_bytes(b"some bytes")

    def _broken_stat(path):
        raise OSError("simulated stat failure")

    monkeypatch.setattr(support, "_stat_mtime_ns", _broken_stat)
    with pytest.raises(support.SnapshotMeasurementError, match="stat measurement failed"):
        support.measure_file_snapshot(p)


def test_two_failed_snapshots_can_never_compare_equal(tmp_path, monkeypatch):
    """The exact regression this helper exists to prevent: two suppressed
    measurement failures must never both collapse to an equality-
    comparable sentinel (empty string, None, zero) that then compares
    equal and reads as a clean 'unchanged' verdict."""
    p1 = tmp_path / "one.bin"
    p2 = tmp_path / "two.bin"
    p1.write_bytes(b"x")
    p2.write_bytes(b"y")

    def _broken_hash(path):
        raise OSError("simulated hash failure")

    monkeypatch.setattr(support, "_read_and_hash", _broken_hash)
    failures = []
    for p in (p1, p2):
        try:
            support.measure_file_snapshot(p)
        except support.SnapshotMeasurementError as exc:
            failures.append(exc)
        else:
            pytest.fail("a broken hash step must never produce a snapshot")
    assert len(failures) == 2
    # Neither failure is a value; there is nothing here that could
    # compare equal the way two empty strings or two Nones would.


# =======================================================================
# 11. The live homes are SAFETY-CHECKED before any seed or mutation
# (r31). Checking only "is a directory with an ok credential" let the
# suite's own deliberate expiry land on the user's real home if a
# variable were mistyped. Six offline fixtures: C aliasing A, a
# case-only alias, a junction alias, a drive root, the profile root, and
# the ordinary .kimi-code tree. Each is read-only up to the point of
# refusal - resolve_and_validate_live_homes safety-checks BEFORE it ever
# calls the credential validator, so none of these fixtures needs a real
# credential.
# =======================================================================
def _set_live_env(monkeypatch, a, b, c):
    monkeypatch.setenv(support.ENV_HOME_A, str(a))
    monkeypatch.setenv(support.ENV_HOME_B, str(b))
    monkeypatch.setenv(support.ENV_HOME_C, str(c))


def test_live_home_safety_rejects_c_aliasing_a(tmp_path, monkeypatch):
    home_a = tmp_path / "home-a"
    home_a.mkdir()
    home_b = tmp_path / "home-b"
    home_b.mkdir()
    _set_live_env(monkeypatch, home_a, home_b, home_a)  # C == A

    with pytest.raises(support.LiveSetupError, match="pairwise distinct"):
        support.resolve_and_validate_live_homes(POWERSHELL)


def test_live_home_safety_rejects_a_case_only_alias(tmp_path, monkeypatch):
    home_a = tmp_path / "CaseSensitiveHome"
    home_a.mkdir()
    home_b = tmp_path / "home-b"
    home_b.mkdir()
    home_c_case_alias = tmp_path / "casesensitivehome"  # same dir, different case
    _set_live_env(monkeypatch, home_a, home_b, home_c_case_alias)

    with pytest.raises(support.LiveSetupError, match="pairwise distinct"):
        support.resolve_and_validate_live_homes(POWERSHELL)


def test_live_home_safety_rejects_a_junction_alias(tmp_path, monkeypatch):
    home_a = tmp_path / "home-a"
    home_a.mkdir()
    home_b = tmp_path / "home-b"
    home_b.mkdir()
    home_c_junction = tmp_path / "home-c-junction"
    proc = subprocess.run(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command",
         "New-Item -ItemType Junction -Path '%s' -Target '%s' | Out-Null"
         % (str(home_c_junction), str(home_a))],
        capture_output=True, text=True, timeout=30)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    _set_live_env(monkeypatch, home_a, home_b, home_c_junction)

    with pytest.raises(support.LiveSetupError, match="pairwise distinct"):
        support.resolve_and_validate_live_homes(POWERSHELL)


def test_live_home_safety_rejects_a_drive_root(tmp_path, monkeypatch):
    home_a = tmp_path / "home-a"
    home_a.mkdir()
    home_b = tmp_path / "home-b"
    home_b.mkdir()
    drive_root = Path(os.environ["SystemDrive"] + "\\")
    _set_live_env(monkeypatch, home_a, home_b, drive_root)

    with pytest.raises(support.LiveSetupError, match="drive root"):
        support.resolve_and_validate_live_homes(POWERSHELL)


def test_live_home_safety_rejects_the_profile_root(tmp_path, monkeypatch):
    fake_profile = tmp_path / "fake-profile"
    fake_profile.mkdir()
    monkeypatch.setenv("USERPROFILE", str(fake_profile))
    home_a = tmp_path / "home-a"
    home_a.mkdir()
    home_b = tmp_path / "home-b"
    home_b.mkdir()
    _set_live_env(monkeypatch, home_a, home_b, fake_profile)  # C == fake USERPROFILE

    with pytest.raises(support.LiveSetupError, match="USERPROFILE"):
        support.resolve_and_validate_live_homes(POWERSHELL)


def test_live_home_safety_rejects_the_ordinary_kimi_code_tree(tmp_path, monkeypatch):
    fake_profile = tmp_path / "fake-profile"
    fake_profile.mkdir()
    monkeypatch.setenv("USERPROFILE", str(fake_profile))
    fake_kimi_code = fake_profile / ".kimi-code"
    nested = fake_kimi_code / "some-lane-home"
    nested.mkdir(parents=True)
    home_a = tmp_path / "home-a"
    home_a.mkdir()
    home_b = tmp_path / "home-b"
    home_b.mkdir()
    _set_live_env(monkeypatch, home_a, home_b, nested)

    with pytest.raises(support.LiveSetupError, match=r"\.kimi-code"):
        support.resolve_and_validate_live_homes(POWERSHELL)


def test_live_home_safety_passes_for_three_distinct_ordinary_directories(tmp_path, monkeypatch):
    """The negative control: three genuinely distinct, unrelated
    directories under neither a drive root nor the (fake) profile must
    clear the safety check and reach credential validation - proven here
    by the failure being the NEXT stage (a missing credential file),
    never a safety refusal."""
    fake_profile = tmp_path / "fake-profile"
    fake_profile.mkdir()
    monkeypatch.setenv("USERPROFILE", str(fake_profile))
    home_a = tmp_path / "home-a"
    home_a.mkdir()
    home_b = tmp_path / "home-b"
    home_b.mkdir()
    home_c = tmp_path / "home-c"
    home_c.mkdir()
    _set_live_env(monkeypatch, home_a, home_b, home_c)

    with pytest.raises(support.LiveSetupError, match="structurally ok credential"):
        support.resolve_and_validate_live_homes(POWERSHELL)


# =======================================================================
# 12. validate_credential carries the blank-line acceptance bug no
# longer: a multi-line reply with a blank separator ("\n\n{json}\n\n")
# must NOT satisfy "exactly one line" just because blank lines were
# discarded before counting.
# =======================================================================
def test_validate_credential_rejects_a_blank_separated_multiline_reply():
    result = support._accept_validator_output(
        0, '\n\n{"status": "ok", "detail": "valid", "fields": []}\n\n', "")
    assert result.ok is False


def test_validate_credential_accepts_a_single_line_with_one_trailing_newline():
    result = support._accept_validator_output(
        0, '{"status": "ok", "detail": "valid", "fields": []}\n', "")
    assert result.ok is True
    assert result.status == "ok"


# =======================================================================
# 12b. The CUSTODY line carries the same rule, and it matters more: that
# line carries the NONCE the release is performed with. The fix for the
# validator left this second instance of the same algorithm in place.
# =======================================================================
_CUSTODY_LINE = json.dumps({"debateHome": "D:/lane/debate", "nonce": "abc123"})


def test_the_custody_line_rejects_a_blank_separated_multiline_reply():
    debate_home, nonce = support._accept_custody_line(
        0, "\n\n" + _CUSTODY_LINE + "\n\n")
    assert debate_home is None
    assert nonce is None


def test_the_custody_line_accepts_one_line_with_one_trailing_newline():
    debate_home, nonce = support._accept_custody_line(0, _CUSTODY_LINE + "\n")
    assert debate_home == "D:/lane/debate"
    assert nonce == "abc123"


def test_the_custody_line_rejects_a_nonzero_exit():
    assert support._accept_custody_line(1, _CUSTODY_LINE + "\n") == (None, None)


# =======================================================================
# 13. The physical-inventory command escapes every embedded apostrophe -
# a debate-home path segment carrying BOTH an apostrophe and a space
# must not corrupt the single-quoted PowerShell literal it is
# interpolated into.
# =======================================================================
def test_no_standalone_credential_file_escapes_apostrophe_and_space_in_the_path(tmp_path):
    debate_home = tmp_path / "o'brien's lane home"
    debate_home.mkdir()
    cred_dir = debate_home / "credentials"
    cred_dir.mkdir()
    (cred_dir / "kimi-code.json").write_text("{}", encoding="ascii")

    result = support.no_standalone_credential_file(POWERSHELL, debate_home)
    assert result is False, "a standalone kimi-code.json must be detected despite the tricky path"


def test_no_standalone_credential_file_true_when_none_exists(tmp_path):
    debate_home = tmp_path / "o'brien's other lane home"
    debate_home.mkdir()

    result = support.no_standalone_credential_file(POWERSHELL, debate_home)
    assert result is True


# =======================================================================
# 14. The probe record: a LOCKING ASSERTION, not documentation (r31). Six
# required offline oracles.
# =======================================================================
def _measurement(exit_code=1, stdout="normalized-stdout", stderr="normalized-stderr"):
    return support.ProbeMeasurement(exit_code, stdout, stderr)


def test_probe_record_gate_matching_record_passes_and_writes_nothing(tmp_path):
    record_path = tmp_path / "probe-record.md"
    committed = _measurement(1, "STDOUT-TEXT", "STDERR-TEXT")
    support.write_probe_record_atomic(
        record_path, committed, measured_at="2026-01-01T00:00:00+00:00")
    before = record_path.read_bytes()

    calls = []

    def measure_fn():
        calls.append(1)
        return committed

    result = support.run_probe_record_gate(record_path, measure_fn, support.SecretGuard(),
                                             refresh=False)
    assert result == committed
    assert len(calls) == 2, "the ordinary run measures the case TWICE"
    assert record_path.read_bytes() == before, "an ordinary run never writes"


def test_probe_record_gate_mismatching_record_fails_and_writes_nothing(tmp_path):
    record_path = tmp_path / "probe-record.md"
    committed = _measurement(1, "STDOUT-TEXT", "OLD-COMMITTED-STDERR")
    support.write_probe_record_atomic(
        record_path, committed, measured_at="2026-01-01T00:00:00+00:00")
    before = record_path.read_bytes()

    current = _measurement(1, "STDOUT-TEXT", "NEW-MEASURED-STDERR")

    with pytest.raises(support.ProbeRecordMismatch):
        support.run_probe_record_gate(record_path, lambda: current, support.SecretGuard(),
                                       refresh=False)
    assert record_path.read_bytes() == before


def test_probe_record_gate_absent_record_fails_and_writes_nothing(tmp_path):
    record_path = tmp_path / "nested" / "does-not-exist" / "probe-record.md"
    calls = []

    def measure_fn():
        calls.append(1)
        return _measurement()

    with pytest.raises(support.ProbeRecordError):
        support.run_probe_record_gate(record_path, measure_fn, support.SecretGuard(),
                                       refresh=False)
    assert calls == [], "a missing record fails BEFORE the case ever measures"
    assert not record_path.exists()


def test_probe_record_gate_explicit_refresh_creates_it(tmp_path):
    record_path = tmp_path / "probe-record.md"
    assert not record_path.exists()
    m = _measurement(1, "STDOUT-TEXT", "STDERR-TEXT")

    result = support.run_probe_record_gate(record_path, lambda: m, support.SecretGuard(),
                                             refresh=True)
    assert result == m
    assert record_path.exists()
    assert support.read_probe_record(record_path) == m


def test_probe_record_gate_unstable_refresh_writes_nothing(tmp_path):
    record_path = tmp_path / "probe-record.md"
    sequence = [_measurement(1, "A", "A"), _measurement(1, "B", "B")]

    def measure_fn():
        return sequence.pop(0)

    with pytest.raises(support.ProbeRecordUnstable):
        support.run_probe_record_gate(record_path, measure_fn, support.SecretGuard(),
                                       refresh=True)
    assert not record_path.exists()


def test_probe_record_gate_secret_guard_match_writes_nothing(tmp_path):
    record_path = tmp_path / "probe-record.md"
    guard = support.SecretGuard()
    guard.merge_values({"access_token": "PROBE-RECORD-SECRET-VALUE"})
    m = _measurement(1, "PROBE-RECORD-SECRET-VALUE", "STDERR-TEXT")

    with pytest.raises(support.SecretGuardViolation):
        support.run_probe_record_gate(record_path, lambda: m, guard, refresh=True)
    assert not record_path.exists()


def test_probe_record_refresh_env_rejects_any_other_nonempty_value(monkeypatch):
    """Fixed name and value: the exact opt-in is '1'; any other nonempty
    value REFUSES rather than being treated as truthy."""
    monkeypatch.setenv(support.REFRESH_ENV, "true")
    with pytest.raises(support.ProbeRecordRefreshRefused):
        support.probe_record_refresh_requested()

    monkeypatch.setenv(support.REFRESH_ENV, "1")
    assert support.probe_record_refresh_requested() is True

    monkeypatch.delenv(support.REFRESH_ENV, raising=False)
    assert support.probe_record_refresh_requested() is False
