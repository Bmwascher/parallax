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
# the pre-command phase and during the (simulated) client process.
# =======================================================================
def test_contention_against_the_builder_hold_spans_precommand_and_command(
        tmp_path, module_owner):
    profile = _fake_profile(tmp_path)
    lane_home = _fake_lane_home(tmp_path)
    target = tmp_path / "contended-debate-home"
    guard = support.SecretGuard()

    holder_proc, holder_pid, holder_ticks = _spawn_live_holder()
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

            fake = _write_fake_command(
                tmp_path, "fake-client-1.py",
                "import sys; sys.stdout.write('PROBE\\n')")
            result = support.dispatch_and_guard(fake, guard, timeout=30)
            assert result.returncode == 0
            assert "PROBE" in result.stdout

            # During/after the "client process": contention must still be
            # observed against the SAME retained hold.
            during_attempt = support.lock_acquire(
                POWERSHELL, lane_home, support.new_hex32(), holder_pid, holder_ticks,
                str(tmp_path / "other-debate-home-2"))
            assert during_attempt.returncode == 3, during_attempt.stdout + during_attempt.stderr
    finally:
        _kill_holder(holder_proc)

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


def test_precedence_main_failure_remove_also_fails_sentinel_refusal(tmp_path, module_owner):
    profile = _fake_profile(tmp_path)
    lane_home = _fake_lane_home(tmp_path, name="precedence-2")
    target = tmp_path / "precedence-2-home"

    lock_before = None
    debate_home_seen = None
    try:
        with pytest.raises(support.DispatchLaunchFailure):
            with support.custody_of(
                    POWERSHELL, target, PLACEHOLDER_MODEL, "high", lane_home,
                    support.new_hex32(), module_owner.owner_pid, module_owner.owner_ticks,
                    build_env=_build_env(profile)) as custody:
                debate_home_seen = custody.debate_home
                lock_before = _read_lock_bytes(lane_home)
                _corrupt_sentinel(custody.debate_home)
                support.dispatch_and_guard(
                    [str(tmp_path / "does-not-exist.exe")], support.SecretGuard(), timeout=10)

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
    guard = support.SecretGuard()
    guard.merge_values({"access_token": "OLD-VALUE-BEFORE-ROTATION"})

    cred_file = tmp_path / "rotated-credential.json"
    cred_file.write_text(
        json.dumps({"access_token": "NEW-VALUE-AFTER-ROTATION",
                    "refresh_token": "still-here", "expires_at": 1234}),
        encoding="ascii")

    # The "command" that rotated the credential does not itself echo the
    # new value - a seed-once implementation would have nothing to catch
    # it with even after this point.
    support.reread_and_merge_credential(guard, cred_file)
    assert guard.find_match("NEW-VALUE-AFTER-ROTATION") == "access_token"

    with pytest.raises(support.SecretGuardViolation) as excinfo:
        support.dispatch_and_guard(
            [sys.executable, "-c",
             "import sys; sys.stdout.write('NEW-VALUE-AFTER-ROTATION\\n')"],
            guard, timeout=30)
    assert excinfo.value.field == "access_token"


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
