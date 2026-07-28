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
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
PLUGIN_ROOT = HERE.parent.parent
LOCK = PLUGIN_ROOT / "tools" / "kimi-lane-lock.ps1"

POWERSHELL = shutil.which("powershell") or shutil.which("pwsh")

pytestmark = pytest.mark.skipif(
    POWERSHELL is None, reason="no PowerShell host on PATH")


def run_lock(lock_path, *args):
    """Drive the script with the lock redirected into a tmp path.

    PARALLAX_KIMI_LOCK is the script's documented test seam, so the real
    per-user lock is never touched by the suite.
    """
    env = {**dict(__import__("os").environ), "PARALLAX_KIMI_LOCK": str(lock_path)}
    return subprocess.run(
        [POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass",
         "-File", str(LOCK), *args],
        capture_output=True, text=True, timeout=120, env=env)


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


def test_a_label_less_release_frees_an_unlabelled_lock(tmp_path):
    # The refusal is about protecting a KNOWN holder. An unlabelled lock has
    # no holder to protect, so cleanup must still work.
    p = tmp_path / "k.lock"
    assert run_lock(p, "-Acquire").returncode == 0
    r = run_lock(p, "-Release")
    assert r.returncode == 0
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
    p = tmp_path / "k.lock"
    assert run_lock(p, "-Acquire", "-Label", "debate-A").returncode == 0
    r = run_lock(p, "-Acquire", "-Label", "debate-B", "-MaxAgeMinutes", "0")
    assert r.returncode == 0
    assert "stale" in r.stdout, "breaking a lock must never be silent"


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
    p = tmp_path / "k.lock"
    assert run_lock(p, "-Acquire", "-Label", "debate-A").returncode == 0
    r = run_lock(p, "-MaxAgeMinutes", "0")
    assert r.returncode == 0
    assert "STALE" in r.stdout


def test_lock_records_a_parseable_stamp_and_label(tmp_path):
    p = tmp_path / "k.lock"
    assert run_lock(p, "-Acquire", "-Label", "debate-A").returncode == 0
    data = json.loads(p.read_text(encoding="ascii"))
    assert data["label"] == "debate-A"
    assert data["stamp"], "age-based staleness needs a stamp to read"
