"""Tests for tools/kimi-lane-lock.ps1.

The backup lane reads its route-attribution evidence out of one
user-global log, so two parallax debates dispatching at once interleave
their startup lines. That cost two of six dispatched rounds on
2026-07-27 (backlog item 6). Ordering-based attribution in
references/backup-lane.md handles FOREIGN kimi sessions; this lock is what
stops parallax colliding with itself.

The lock is advisory and age-bounded by design. It records no process
handle, because the holder is a driver agent whose shell invocations are
each short-lived - a recorded PID would be dead before the next caller
looked, so every lock would read as stale immediately. Staleness is
therefore decided by age alone, and these tests pin that contract
including its limits.

Runs wherever a PowerShell host exists: Windows powershell.exe or pwsh
(GitHub ubuntu runners ship pwsh); skipped otherwise.
"""

import json
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
PLUGIN_ROOT = HERE.parent.parent
LOCK = PLUGIN_ROOT / "tools" / "kimi-lane-lock.ps1"

POWERSHELL = shutil.which("powershell") or shutil.which("pwsh")

pytestmark = pytest.mark.skipif(
    POWERSHELL is None, reason="no PowerShell host on PATH")


def run_lock(lock_path, *args, extra_env=None):
    """Drive the script with the lock redirected into a tmp path.

    PARALLAX_KIMI_LOCK is the script's documented test seam, so the real
    per-user lock is never touched by the suite.

    There is deliberately NO way for a caller to shorten the staleness
    threshold. Two earlier shapes were both lock-stealing: a
    `-MaxAgeMinutes` parameter (`-Acquire -MaxAgeMinutes 0` broke a fresh
    lock with no `-Force`), and an env override honoured whenever the lock
    path was redirected - which gated on the redirect being present rather
    than on it differing from the default, so pointing it at the default
    path stole the real per-user lane. The cross-vendor lane found each of
    them, the second inside the fix for the first. Tests that need a stale
    lock write one with a backdated stamp instead; see `write_lock`.
    """
    env = {**dict(__import__("os").environ), "PARALLAX_KIMI_LOCK": str(lock_path)}
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(LOCK), *args],
        capture_output=True, text=True, timeout=120, env=env)


def write_lock(path, label="debate-A", age_minutes=0.0):
    """Place a lock owned by `label` and stamped `age_minutes` in the past.

    This is how the suite reaches the stale branch: it backdates its own
    temporary lock rather than asking the script to lower its guard.
    """
    stamp = datetime.now(timezone.utc) - timedelta(minutes=age_minutes)
    payload = {"stamp": stamp.isoformat()}
    if label is not None:
        payload["label"] = label
    path.write_text(json.dumps(payload), encoding="ascii")
    return path


def test_script_exists():
    assert LOCK.is_file(), "the lane lock the contract names must exist"


def test_status_reports_free_when_absent(tmp_path):
    r = run_lock(tmp_path / "k.lock")
    assert r.returncode == 0
    assert "free" in r.stdout


def test_acquire_then_status_reports_held(tmp_path):
    p = tmp_path / "k.lock"
    a = run_lock(p, "-Acquire", "-Label", "debate-A")
    assert a.returncode == 0 and "acquired" in a.stdout
    s = run_lock(p)
    assert s.returncode == 0
    assert "held" in s.stdout and "debate-A" in s.stdout


def test_acquire_creates_the_parent_directory(tmp_path):
    # The default location is under LOCALAPPDATA and will not exist on a
    # fresh machine; a first acquire must not fail on that.
    p = tmp_path / "nested" / "deeper" / "k.lock"
    r = run_lock(p, "-Acquire", "-Label", "debate-A")
    assert r.returncode == 0
    assert p.is_file()


def test_second_acquire_is_busy_and_says_not_to_dispatch(tmp_path):
    p = tmp_path / "k.lock"
    assert run_lock(p, "-Acquire", "-Label", "debate-A").returncode == 0
    r = run_lock(p, "-Acquire", "-Label", "debate-B", "-WaitSeconds", "0")
    assert r.returncode == 1, "a busy lane must not read as acquired"
    assert "BUSY" in r.stdout
    assert "debate-A" in r.stdout, "a waiting caller needs to know who holds it"
    assert "Do not dispatch" in r.stdout


def test_release_by_a_different_label_is_refused(tmp_path):
    # One debate must not free another's lane by accident.
    p = tmp_path / "k.lock"
    assert run_lock(p, "-Acquire", "-Label", "debate-A").returncode == 0
    r = run_lock(p, "-Release", "-Label", "debate-B")
    assert r.returncode == 1
    assert "different caller" in r.stdout
    assert p.is_file(), "a refused release must leave the lock in place"


def test_a_label_less_release_cannot_free_a_labelled_lock(tmp_path):
    # A bare -Release used to skip the ownership check entirely, making it an
    # undeclared -Force: it silently freed a lane another debate held, and
    # two rounds could then dispatch at once. That is the exact case the lock
    # exists to prevent, so it must be refused.
    p = tmp_path / "k.lock"
    assert run_lock(p, "-Acquire", "-Label", "debate-A").returncode == 0
    r = run_lock(p, "-Release")
    assert r.returncode == 1, "a bare release must not silently force"
    assert "this release names no label" in r.stdout
    assert p.is_file(), "the holder's lane must survive a bare release"


def test_acquire_requires_a_label(tmp_path):
    # The label is the ownership credential. An UNLABELLED lock has no holder
    # to protect, so any bare release frees it - which the cross-vendor lane
    # named as a hole in the ownership claim. Requiring the label on acquire
    # means an unlabelled lock cannot exist to be exploited.
    p = tmp_path / "k.lock"
    r = run_lock(p, "-Acquire")
    assert r.returncode == 2
    assert "required on acquire" in r.stdout
    assert not p.is_file(), "a refused acquire must not leave a lock behind"


def test_acquire_refuses_a_whitespace_label(tmp_path):
    # `-Label ""` was already refused, but whitespace was accepted as an
    # owner. A blank credential is not one a later release can be checked
    # against, so it must be refused the same way.
    p = tmp_path / "k.lock"
    r = run_lock(p, "-Acquire", "-Label", "   ")
    assert r.returncode == 2
    assert "nonblank" in r.stdout
    assert not p.is_file()


@pytest.mark.parametrize("payload", [
    {"label": 0},
    {"label": None},
    {"label": ""},
    {"label": "   "},
    {},
])
def test_a_bare_release_cannot_free_a_lock_with_no_usable_owner(tmp_path, payload):
    # The first ownership fix tested the parsed field for TRUTHINESS, so a
    # lock carrying `label: 0`, `label: null`, a blank label, or no label at
    # all skipped the guard and was removed by a bare release. This script
    # never writes such a lock, but it can read one - a legacy file, or one
    # written by hand. No credential exists to present, so only -Force clears
    # it.
    p = tmp_path / "k.lock"
    payload["stamp"] = datetime.now(timezone.utc).isoformat()
    p.write_text(json.dumps(payload), encoding="ascii")
    r = run_lock(p, "-Release")
    assert r.returncode == 1, "an unusable owner must not mean unowned"
    assert "no usable owner" in r.stdout
    assert p.is_file()
    assert run_lock(p, "-Release", "-Force").returncode == 0
    assert not p.is_file(), "-Force must still be able to clear it"


def test_release_ownership_is_case_sensitive(tmp_path):
    # Ownership is a string match and nothing more, so it is exactly that:
    # two labels differing only in case are two different callers.
    p = tmp_path / "k.lock"
    assert run_lock(p, "-Acquire", "-Label", "debate-A").returncode == 0
    r = run_lock(p, "-Release", "-Label", "DEBATE-A")
    assert r.returncode == 1
    assert p.is_file()


def test_surrounding_whitespace_does_not_break_ownership(tmp_path):
    # Acquire stores the trimmed label, so release must trim too, or a
    # trailing space in a driver's command would strand the lane.
    p = tmp_path / "k.lock"
    assert run_lock(p, "-Acquire", "-Label", " debate-A ").returncode == 0
    assert json.loads(p.read_text(encoding="ascii"))["label"] == "debate-A"
    assert run_lock(p, "-Release", "-Label", "debate-A ").returncode == 0
    assert not p.is_file()


def test_a_forced_label_less_release_frees_a_labelled_lock(tmp_path):
    p = tmp_path / "k.lock"
    assert run_lock(p, "-Acquire", "-Label", "debate-A").returncode == 0
    r = run_lock(p, "-Release", "-Force")
    assert r.returncode == 0
    assert not p.is_file()


def test_breaking_a_malformed_lock_is_announced(tmp_path):
    # Breaking a stale lock says so; breaking an unreadable one used to be
    # silent. Same act, so it gets the same visibility.
    p = tmp_path / "k.lock"
    p.write_text("{not json", encoding="ascii")
    r = run_lock(p, "-Acquire", "-Label", "debate-A", "-WaitSeconds", "0")
    assert r.returncode == 0
    assert "unreadable" in r.stdout


def test_force_releases_another_callers_lock(tmp_path):
    p = tmp_path / "k.lock"
    assert run_lock(p, "-Acquire", "-Label", "debate-A").returncode == 0
    r = run_lock(p, "-Release", "-Label", "debate-B", "-Force")
    assert r.returncode == 0
    assert not p.is_file()


def test_release_by_the_owner_frees_the_lane(tmp_path):
    p = tmp_path / "k.lock"
    assert run_lock(p, "-Acquire", "-Label", "debate-A").returncode == 0
    assert run_lock(p, "-Release", "-Label", "debate-A").returncode == 0
    assert not p.is_file()
    assert "free" in run_lock(p).stdout


def test_releasing_a_free_lane_is_not_an_error(tmp_path):
    # Release runs in a driver's cleanup path, which must be idempotent.
    r = run_lock(tmp_path / "k.lock", "-Release")
    assert r.returncode == 0
    assert "already free" in r.stdout


def test_a_stale_lock_is_broken_and_says_so(tmp_path):
    # 46 minutes past the fixed 45-minute threshold, written by the test.
    # This used to shorten the threshold instead, which was the very seam the
    # cross-vendor lane then aimed at the real lane.
    p = write_lock(tmp_path / "k.lock", "debate-A", age_minutes=46)
    r = run_lock(p, "-Acquire", "-Label", "debate-B", "-WaitSeconds", "0")
    assert r.returncode == 0
    assert "stale" in r.stdout, "breaking a lock must never be silent"


def test_a_fresh_lock_is_not_stale_at_the_threshold_margin(tmp_path):
    # The other side of the same boundary: 44 minutes still holds the lane.
    # Without this, a threshold accidentally set to zero would pass every
    # stale test above and break every real lock.
    p = write_lock(tmp_path / "k.lock", "debate-A", age_minutes=44)
    r = run_lock(p, "-Acquire", "-Label", "debate-B", "-WaitSeconds", "0")
    assert r.returncode == 1, "a lock inside the threshold must still hold"
    assert "BUSY" in r.stdout


def test_the_staleness_threshold_is_not_caller_controlled(tmp_path):
    # It was a -MaxAgeMinutes parameter, which meant `-Acquire
    # -MaxAgeMinutes 0` stole a fresh lock without -Force: the ownership
    # guard bypassed by the flag next to it. Passing it must now fail rather
    # than quietly work.
    p = tmp_path / "k.lock"
    assert run_lock(p, "-Acquire", "-Label", "debate-A").returncode == 0
    r = run_lock(p, "-Acquire", "-Label", "debate-B", "-MaxAgeMinutes", "0")
    assert r.returncode != 0, "the threshold must not be settable by a flag"
    assert p.is_file()
    holder = json.loads(p.read_text(encoding="ascii"))
    assert holder["label"] == "debate-A", "the fresh lock must survive"


def test_no_environment_variable_can_shorten_the_threshold(tmp_path):
    # The override used to be honoured whenever the lock path was redirected.
    # That gated on the redirect being PRESENT, not on it differing from the
    # default - so redirecting to the default path stole the real per-user
    # lane with no -Force. The seam is gone, and setting it must now do
    # nothing at all.
    p = tmp_path / "k.lock"
    assert run_lock(p, "-Acquire", "-Label", "debate-A").returncode == 0
    r = run_lock(p, "-Acquire", "-Label", "debate-B", "-WaitSeconds", "0",
                 extra_env={"PARALLAX_KIMI_LOCK_MAX_AGE_MINUTES": "0"})
    assert r.returncode == 1, "no env var may lower the staleness guard"
    assert "BUSY" in r.stdout
    holder = json.loads(p.read_text(encoding="ascii"))
    assert holder["label"] == "debate-A", "the fresh lock must survive"


def test_the_default_path_is_derived_from_localappdata(tmp_path):
    # Replaces a test that read the REAL per-user lane: it passed for the
    # wrong reason when that lane was free, and failed when it was
    # legitimately stale. Pointing LOCALAPPDATA at a tmp directory exercises
    # the default-path branch hermetically, so the suite never touches the
    # lane a live debate may be holding.
    env = {**dict(__import__("os").environ), "LOCALAPPDATA": str(tmp_path)}
    env.pop("PARALLAX_KIMI_LOCK", None)

    def default_path_run(*args):
        return subprocess.run(
            [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
             "-File", str(LOCK), *args],
            capture_output=True, text=True, timeout=120, env=env)

    assert default_path_run("-Acquire", "-Label", "debate-A").returncode == 0
    s = default_path_run("-Status")
    assert s.returncode == 0
    assert "debate-A" in s.stdout
    assert str(tmp_path) in s.stdout, (
        "the default lock must sit under LOCALAPPDATA, and this run must not "
        "have touched the real lane")


def test_a_future_stamp_cannot_wedge_the_lane(tmp_path):
    # A stamp in the future produced a NEGATIVE age, which never reached the
    # stale branch: the lane stayed BUSY until the clock caught up, and status
    # printed "held -360 min" to a human. Clock skew or tampering, either way
    # not a lock to respect.
    p = tmp_path / "k.lock"
    future = (datetime.now(timezone.utc) + timedelta(hours=6)).isoformat()
    p.write_text(json.dumps({"label": "ghost", "stamp": future}),
                 encoding="ascii")
    r = run_lock(p, "-Acquire", "-Label", "debate-A", "-WaitSeconds", "0")
    assert r.returncode == 0, "a future-stamped lock must not hold the lane"
    holder = json.loads(p.read_text(encoding="ascii"))
    assert holder["label"] == "debate-A"


def test_status_never_reports_a_negative_age(tmp_path):
    p = tmp_path / "k.lock"
    future = (datetime.now(timezone.utc) + timedelta(hours=6)).isoformat()
    p.write_text(json.dumps({"label": "ghost", "stamp": future}),
                 encoding="ascii")
    r = run_lock(p)
    assert r.returncode == 0
    assert "-" not in r.stdout.split("held")[-1].split("min")[0], (
        "a negative age is nonsense to a human reader")


def test_a_malformed_lock_is_breakable(tmp_path):
    # A half-written lock must not wedge the lane permanently.
    p = tmp_path / "k.lock"
    p.write_text("{not json", encoding="ascii")
    r = run_lock(p, "-Acquire", "-Label", "debate-A", "-WaitSeconds", "0")
    assert r.returncode == 0


def test_a_lock_with_no_stamp_is_breakable(tmp_path):
    # Age decides staleness, so a missing stamp must read as infinitely old
    # rather than as a lock that can never expire.
    p = tmp_path / "k.lock"
    p.write_text(json.dumps({"label": "debate-A"}), encoding="ascii")
    r = run_lock(p, "-Acquire", "-Label", "debate-B", "-WaitSeconds", "0")
    assert r.returncode == 0


def test_status_marks_an_expired_lock_stale(tmp_path):
    p = write_lock(tmp_path / "k.lock", "debate-A", age_minutes=60)
    r = run_lock(p)
    assert r.returncode == 0
    assert "STALE" in r.stdout


def test_lock_records_a_parseable_stamp_and_label(tmp_path):
    p = tmp_path / "k.lock"
    assert run_lock(p, "-Acquire", "-Label", "debate-A").returncode == 0
    data = json.loads(p.read_text(encoding="ascii"))
    assert data["label"] == "debate-A"
    assert data["stamp"], "age-based staleness needs a stamp to read"
