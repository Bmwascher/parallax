"""Contract pins for the kimi-code lane lock (Task 3, 2026-08-01
lane-credential-and-lock plan).

WINDOWS ONLY, whole module: the lock manipulates real Windows exclusive
file handles and real process liveness (Get-Process, Win32_Process).
PARALLAX_PS_HOST selects which host runs these tests, same pattern as
test_codex_context_probe.py:35-67 - a selector that merely finds A host
would happily collect them on Ubuntu CI too, where pwsh is on PATH but
the exclusive-handle and liveness semantics under test do not exist
there the same way. A green suite on one Windows host proves ONE
interpreter - 0.16.1 shipped a lock that did not lock on pwsh because
every local run used powershell.exe only.
"""
import hashlib
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
SCRIPT = REPO / "tools" / "kimi-lane-lock.ps1"

POWERSHELL = (os.environ.get("PARALLAX_PS_HOST")
              or shutil.which("powershell") or shutil.which("pwsh"))

pytestmark = pytest.mark.skipif(
    os.name != "nt" or POWERSHELL is None,
    reason="the lock is a Windows tool: it needs a PowerShell host and "
           "the exclusive-handle / process-liveness platform it targets")

COMPUTERNAME = os.environ.get("COMPUTERNAME", "")


def _live_owner():
    """A genuinely LIVE owner identity: this pytest process.

    Acquire refuses an owner measured DEAD at the gate, and requires
    LIVE again immediately before each record write, so a fixture
    identity of pid 1 / ticks 1 is no longer usable. The pytest process
    is alive for the whole run by construction, and its start ticks are
    read the same way the tool reads them, so the pair the tests pass is
    the pair the tool measures.
    """
    pid = os.getpid()
    proc = subprocess.run(
        [POWERSHELL, "-NoProfile", "-Command",
         "$p = Get-Process -Id " + str(pid) +
         "; [string]$p.StartTime.ToUniversalTime().Ticks"],
        capture_output=True, text=True, timeout=60)
    ticks = proc.stdout.strip()
    if not ticks.isdigit():
        raise RuntimeError("could not read this process's start ticks: "
                           + repr(proc.stdout) + proc.stderr)
    return str(pid), ticks


if os.name == "nt" and POWERSHELL is not None:
    LIVE_PID, LIVE_TICKS = _live_owner()
else:
    LIVE_PID, LIVE_TICKS = "1", "1"

TOKEN_RE = re.compile(r"\A[0-9a-f]{32}\Z")
DIGITS_RE = re.compile(r"\A[0-9]+\Z")


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def new_token():
    return uuid.uuid4().hex


def run_lock(args, env=None, timeout=20):
    full_env = dict(os.environ)
    if env:
        full_env.update(env)
    cmd = [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(SCRIPT)] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, env=full_env, timeout=timeout)


def start_lock_bg(args, env=None):
    full_env = dict(os.environ)
    if env:
        full_env.update(env)
    cmd = [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(SCRIPT)] + list(args)
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, env=full_env)


def lock_path(home):
    return home / "lane.lock"


def write_raw(home, content_bytes):
    lock_path(home).write_bytes(content_bytes)


def read_raw(home):
    p = lock_path(home)
    if not p.exists():
        return None
    return p.read_bytes()


def write_held(home, **overrides):
    rec = {
        "version": 1,
        "state": "held",
        "host": COMPUTERNAME,
        "ownerPid": 999999,
        "ownerStartTicksUtc": "111111111",
        "debateId": new_token(),
        "nonce": new_token(),
        "debateHome": str(home / "debate-home"),
        "acquiredTicksUtc": "111111111",
    }
    rec.update(overrides)
    write_raw(home, json.dumps(rec).encode("utf-8"))
    return rec


def sha256_hex(data: bytes):
    return hashlib.sha256(data).hexdigest()


def wait_for_signal(path: Path, timeout=10.0):
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


def _ticks_for_pid(pid):
    proc = subprocess.run(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-Command",
         f"(Get-Process -Id {pid}).StartTime.ToUniversalTime().Ticks"],
        capture_output=True, text=True)
    return proc.stdout.strip()


@pytest.fixture(scope="module")
def self_identity():
    """A LIVE (pid, ticks) pair that stays alive for the whole module -
    this pytest process itself."""
    pid = os.getpid()
    ticks = _ticks_for_pid(pid)
    assert DIGITS_RE.match(ticks), f"could not resolve self ticks: {ticks!r}"
    return str(pid), ticks


@pytest.fixture
def lane_home(tmp_path):
    p = tmp_path / "lane"
    p.mkdir()
    return p


@pytest.fixture
def debate_home(tmp_path):
    p = tmp_path / "debate-home"
    p.mkdir()
    return p


def start_sleeper(seconds=40):
    """A genuinely separate LIVE process, for holder-contention fixtures
    that must name a pid this tool did not itself spawn as the lock
    holder's identity."""
    return subprocess.Popen(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-Command", f"Start-Sleep -Seconds {seconds}"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


# ---------------------------------------------------------------------
# Basic shape
# ---------------------------------------------------------------------
def test_script_exists():
    assert SCRIPT.is_file()


def test_resolve_owner_prints_pid_and_digit_ticks():
    result = run_lock(["-ResolveOwner"])
    assert result.returncode == 0
    obj = json.loads(result.stdout.strip())
    assert set(obj.keys()) == {"ownerPid", "ownerStartTicksUtc", "ownerName"}
    assert isinstance(obj["ownerPid"], int) and obj["ownerPid"] > 0
    assert DIGITS_RE.match(obj["ownerStartTicksUtc"])


def test_resolve_owner_reports_the_resolved_process_name():
    """The owner was recorded as a bare number, so a wrong owner and a
    right one looked identical in every record and every status read.

    Backlog item 26 opened with a lane blocked for hours and no way to
    tell from the artifacts WHAT held it. The name does not fix the
    resolution; it makes a wrong resolution legible on sight.
    """
    result = run_lock(["-ResolveOwner"])
    assert result.returncode == 0
    obj = json.loads(result.stdout.strip())
    assert isinstance(obj["ownerName"], str) and obj["ownerName"].strip()


def run_lock_through_an_extra_shell(args, timeout=40):
    """Invoke the tool one shell level deeper than run_lock does.

    The inner host is the same executable, so the ONLY difference
    between this and run_lock is an added transparent shell frame.
    """
    # Both paths are QUOTED. This passes today only because
    # PARALLAX_PS_HOST is normally a bare name and the powershell fallback
    # resolves under System32 with no spaces; the shutil.which("pwsh")
    # fallback is under Program Files, and an unquoted splice there fails
    # the inner parse - which would fail this oracle for a TRANSPORT
    # reason while looking like the resolution defect it exists to catch.
    inner = ('"' + POWERSHELL + '" -NoProfile -NonInteractive -File "'
             + str(SCRIPT) + '" ' + " ".join(args))
    cmd = [POWERSHELL, "-NoProfile", "-NonInteractive", "-Command",
           "& " + inner]
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def test_resolve_owner_is_stable_across_an_added_shell_frame():
    """Item 26's instability, reproduced HERE without the other
    session's wrapping harness.

    The report was that `-ResolveOwner` returns a DIFFERENT pid per call
    under a wrapper, so the recorded owner reads DEAD almost at once.
    The mechanism is that resolution took the DIRECT parent, and under a
    wrapper the direct parent is the ephemeral shell the wrapper just
    spawned - a new pid every call, dead by the next status read.

    Adding one shell frame reproduces it exactly. Resolution must walk
    PAST the hosts this tool is invoked through and land on the same
    process either way, or the recorded owner is an artifact of how deep
    the caller happened to nest its shells.
    """
    direct = run_lock(["-ResolveOwner"])
    wrapped = run_lock_through_an_extra_shell(["-ResolveOwner"])
    assert direct.returncode == 0, (direct.stdout, direct.stderr)
    assert wrapped.returncode == 0, (wrapped.stdout, wrapped.stderr)
    a = json.loads(direct.stdout.strip())
    b = json.loads(wrapped.stdout.strip())
    assert a["ownerPid"] == b["ownerPid"], (a, b)
    assert a["ownerStartTicksUtc"] == b["ownerStartTicksUtc"], (a, b)
    assert a["ownerName"] == b["ownerName"], (a, b)


def test_resolve_owner_refuses_when_the_ancestry_cannot_be_read():
    """An unmade measurement is never a clean one.

    The fault seam forces the ancestry walk to throw. It is safe by
    construction: its only reachable effect is to REFUSE, and there is
    no path by which it produces an owner record. Same shape as
    PARALLAX_LANE_LOCK_STARTTIME_FAULT, which can only classify a holder
    alive and refuse a takeover.
    """
    result = run_lock(["-ResolveOwner"],
                      env={"PARALLAX_LANE_LOCK_ANCESTRY_FAULT": "1"})
    assert result.returncode == 2, (result.returncode, result.stdout, result.stderr)
    assert result.stdout.strip() == "", result.stdout


# ---------------------------------------------------------------------
# MALFORMED classification and the per-state property rule
# ---------------------------------------------------------------------
def test_free_record_with_extra_known_property_is_malformed(lane_home):
    write_raw(lane_home, b'{"version":1,"state":"free","host":"X"}')
    result = run_lock(["-Status", "-LaneHome", str(lane_home)])
    assert result.returncode == 0
    assert json.loads(result.stdout)["state"] == "MALFORMED"


def test_free_record_with_wholly_unknown_property_is_malformed(lane_home):
    write_raw(lane_home, b'{"version":1,"state":"free","bogus":"X"}')
    result = run_lock(["-Status", "-LaneHome", str(lane_home)])
    assert result.returncode == 0
    assert json.loads(result.stdout)["state"] == "MALFORMED"


@pytest.mark.parametrize("raw,what", [
    (b'{"version":1,"state":"Free"}', "a capitalized state literal"),
    (b'{"version":1,"state":"FREE"}', "an upper-case state literal"),
    (b'{"Version":1,"state":"free"}', "a capitalized version field name"),
    (b'{"version":1,"State":"free"}', "a capitalized state field name"),
])
def test_case_variant_schema_is_malformed_not_free(lane_home, raw, what):
    """The shipped contract says a record that does not EXACTLY satisfy the
    schema is held and reported, never reclaimed. PowerShell's -eq, -ne and
    -contains are case-INSENSITIVE, so each of these classified as a
    well-formed FREE record and an acquire overwrote a record this tool had
    not actually recognized. Every literal comparison in Get-Classification
    is case-exact for that reason."""
    write_raw(lane_home, raw)
    result = run_lock(["-Status", "-LaneHome", str(lane_home)])
    assert result.returncode == 0
    assert json.loads(result.stdout)["state"] == "MALFORMED", what


def test_the_lower_case_record_those_variants_came_from_is_free(lane_home):
    """The positive control: the same record spelled exactly is FREE, so the
    test above measures case and not some unrelated rejection."""
    write_raw(lane_home, b'{"version":1,"state":"free"}')
    result = run_lock(["-Status", "-LaneHome", str(lane_home)])
    assert result.returncode == 0
    assert json.loads(result.stdout)["state"] == "free"


@pytest.mark.parametrize("variant", ["OwnerPid", "ownerpid", "OWNERPID"])
def test_case_variant_required_field_in_a_held_record_is_malformed(lane_home, debate_home,
                                                                    variant):
    """The FREE variants above cannot fail if only the HELD-side field
    comparisons regress, because they never reach them. A held record whose
    required key is spelled differently is not the frozen schema, so it is
    MALFORMED - and an acquire against a malformed record must leave its
    bytes untouched rather than reclaim it."""
    rec = write_held(lane_home)
    rec[variant] = rec.pop("ownerPid")
    raw = json.dumps(rec).encode("utf-8")
    write_raw(lane_home, raw)

    status = run_lock(["-Status", "-LaneHome", str(lane_home)])
    assert status.returncode == 0
    assert json.loads(status.stdout)["state"] == "MALFORMED"

    acquire = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", new_token(),
                        "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS,
                        "-DebateHome", str(debate_home)])
    assert acquire.returncode != 0, acquire.stdout + acquire.stderr
    assert read_raw(lane_home) == raw, "an unrecognized record must not be overwritten"


def test_held_record_with_unknown_property_is_malformed(lane_home):
    rec = write_held(lane_home)
    rec["extra"] = "nope"
    write_raw(lane_home, json.dumps(rec).encode("utf-8"))
    result = run_lock(["-Status", "-LaneHome", str(lane_home)])
    assert result.returncode == 0
    assert json.loads(result.stdout)["state"] == "MALFORMED"


def test_held_record_missing_a_required_field_is_malformed(lane_home):
    rec = write_held(lane_home)
    del rec["nonce"]
    write_raw(lane_home, json.dumps(rec).encode("utf-8"))
    result = run_lock(["-Status", "-LaneHome", str(lane_home)])
    assert result.returncode == 0
    assert json.loads(result.stdout)["state"] == "MALFORMED"


def test_date_shaped_time_field_is_malformed(lane_home):
    write_held(lane_home, ownerStartTicksUtc="2026-08-01T00:00:00Z")
    result = run_lock(["-Status", "-LaneHome", str(lane_home)])
    assert result.returncode == 0
    assert json.loads(result.stdout)["state"] == "MALFORMED"


def test_zero_length_file_is_malformed_not_free(lane_home):
    write_raw(lane_home, b"")
    result = run_lock(["-Status", "-LaneHome", str(lane_home)])
    assert result.returncode == 0
    obj = json.loads(result.stdout)
    assert obj["state"] == "MALFORMED"
    assert obj["bytes"] == 0
    assert obj["sha256"] == sha256_hex(b"")


MALFORMED_FIXTURES = {
    "not-json": b"not json at all",
    "not-object": b"[1,2,3]",
    "single-byte": b"x",
    "wrong-version": b'{"version":2,"state":"free"}',
    "bad-state-literal": b'{"version":1,"state":"pending"}',
    "held-missing-field": json.dumps({
        "version": 1, "state": "held", "host": COMPUTERNAME, "ownerPid": 1,
        "ownerStartTicksUtc": "1", "debateId": "a" * 32, "nonce": "b" * 32,
        "debateHome": "C:/x",
        # acquiredTicksUtc omitted
    }).encode("utf-8"),
    "held-wrong-type-pid": json.dumps({
        "version": 1, "state": "held", "host": COMPUTERNAME, "ownerPid": "1",
        "ownerStartTicksUtc": "1", "debateId": "a" * 32, "nonce": "b" * 32,
        "debateHome": "C:/x", "acquiredTicksUtc": "1",
    }).encode("utf-8"),
    "free-forbidden-property": b'{"version":1,"state":"free","host":"X"}',
}


@pytest.mark.parametrize("name", sorted(MALFORMED_FIXTURES))
def test_each_malformed_class_recoverable_by_matching_hash(lane_home, name):
    data = MALFORMED_FIXTURES[name]
    write_raw(lane_home, data)
    good_hash = sha256_hex(data)
    result = run_lock(["-MalformedOverride", "-LaneHome", str(lane_home),
                        "-ConfirmSha256", good_hash])
    assert result.returncode == 0, (name, result.stdout, result.stderr)
    assert "overrode malformed lock:" in result.stderr
    assert read_raw(lane_home) == b'{"version":1,"state":"free"}'


@pytest.mark.parametrize("name", sorted(MALFORMED_FIXTURES))
def test_each_malformed_class_refused_by_mismatching_hash(lane_home, name):
    data = MALFORMED_FIXTURES[name]
    write_raw(lane_home, data)
    result = run_lock(["-MalformedOverride", "-LaneHome", str(lane_home),
                        "-ConfirmSha256", "0" * 64])
    assert result.returncode == 5, (name, result.stdout, result.stderr)
    assert read_raw(lane_home) == data


# ---------------------------------------------------------------------
# Unreadable -> exit 6
# ---------------------------------------------------------------------
def test_unreadable_path_exits_6(lane_home):
    # A directory sitting at the lock path cannot be opened as a file -
    # this is the "unreadable" case every mode maps to exit 6.
    lock_path(lane_home).mkdir()
    result = run_lock(["-Status", "-LaneHome", str(lane_home)])
    assert result.returncode == 6
    assert result.stdout == ""


# ---------------------------------------------------------------------
# Missing-file behaviour, frozen per mode
# ---------------------------------------------------------------------
def test_status_on_missing_reports_free_and_creates_nothing(lane_home):
    result = run_lock(["-Status", "-LaneHome", str(lane_home)])
    assert result.returncode == 0
    assert json.loads(result.stdout) == {"state": "free"}
    assert not lock_path(lane_home).exists()


@pytest.mark.parametrize("args", [
    ["-Release", "-DebateId", None, "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS, "-Nonce", None],
    ["-ForceRelease", "-ConfirmHost", COMPUTERNAME, "-ConfirmOwnerPid", "1",
     "-ConfirmOwnerStartTicksUtc", "1", "-ConfirmDebateId", None, "-ConfirmNonce", None],
    ["-MalformedOverride", "-ConfirmSha256", "a" * 64],
])
def test_release_and_overrides_on_missing_exit_5_and_create_nothing(lane_home, args):
    filled = [new_token() if a is None else a for a in args]
    result = run_lock(filled + ["-LaneHome", str(lane_home)])
    assert result.returncode == 5, (result.stdout, result.stderr)
    assert not lock_path(lane_home).exists()


def test_acquire_on_missing_creates_and_succeeds(lane_home, debate_home):
    result = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", new_token(),
                        "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS,
                        "-DebateHome", str(debate_home)])
    assert result.returncode == 0
    assert TOKEN_RE.match(result.stdout.strip())
    assert lock_path(lane_home).exists()


def test_file_exists_after_every_successful_mutating_mode(lane_home, debate_home):
    debate_id = new_token()
    nonce = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", debate_id,
                       "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS,
                       "-DebateHome", str(debate_home)]).stdout.strip()
    assert lock_path(lane_home).exists()
    result = run_lock(["-Release", "-LaneHome", str(lane_home), "-DebateId", debate_id,
                        "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS, "-Nonce", nonce])
    assert result.returncode == 0
    assert lock_path(lane_home).exists()  # release writes free in place, never deletes


# ---------------------------------------------------------------------
# Acquire table
# ---------------------------------------------------------------------
def test_fresh_acquire_over_free_emits_new_nonce_and_no_stderr(lane_home, debate_home):
    result = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", new_token(),
                        "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS,
                        "-DebateHome", str(debate_home)])
    assert result.returncode == 0
    assert TOKEN_RE.match(result.stdout.strip())
    assert result.stderr == ""


def test_nonce_supplied_against_free_record_exits_2_and_leaves_free(lane_home, debate_home):
    result = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", new_token(),
                        "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS,
                        "-DebateHome", str(debate_home), "-Nonce", new_token()])
    assert result.returncode == 2
    # Only-ACQUIRE-creates: this call's own CreateNew produced the file,
    # which must not be left as a malformed zero-length artifact.
    assert read_raw(lane_home) == b'{"version":1,"state":"free"}'


def test_dead_holder_reclaimed_and_reported(lane_home, debate_home):
    dead_rec = write_held(lane_home, ownerPid=999999, ownerStartTicksUtc="111111111")
    new_debate = new_token()
    result = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", new_debate,
                        "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS,
                        "-DebateHome", str(debate_home)])
    assert result.returncode == 0
    assert TOKEN_RE.match(result.stdout.strip())
    assert (f"reclaimed a dead holder: pid {dead_rec['ownerPid']} "
            f"ticks {dead_rec['ownerStartTicksUtc']} debate {dead_rec['debateId']}"
            f" home {dead_rec['debateHome']}") in result.stderr


def test_nonce_supplied_against_dead_holder_exits_2_no_reclaim(lane_home, debate_home):
    dead_rec = write_held(lane_home)
    before = read_raw(lane_home)
    result = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", new_token(),
                        "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS,
                        "-DebateHome", str(debate_home), "-Nonce", new_token()])
    assert result.returncode == 2
    assert read_raw(lane_home) == before


def test_old_nonce_fails_after_reclaim(lane_home, debate_home):
    dead_rec = write_held(lane_home, ownerPid=999999, ownerStartTicksUtc="111111111")
    run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", new_token(),
              "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS, "-DebateHome", str(debate_home)])
    result = run_lock(["-Release", "-LaneHome", str(lane_home), "-DebateId", dead_rec["debateId"],
                        "-OwnerPid", str(dead_rec["ownerPid"]),
                        "-OwnerStartTicksUtc", dead_rec["ownerStartTicksUtc"],
                        "-Nonce", dead_rec["nonce"]])
    assert result.returncode == 5


def test_idempotent_reacquire_writes_nothing(lane_home, debate_home, self_identity):
    pid, ticks = self_identity
    debate_id = new_token()
    r1 = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", debate_id,
                   "-OwnerPid", pid, "-OwnerStartTicksUtc", ticks,
                   "-DebateHome", str(debate_home)])
    nonce = r1.stdout.strip()
    before = read_raw(lane_home)
    r2 = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", debate_id,
                   "-OwnerPid", pid, "-OwnerStartTicksUtc", ticks,
                   "-DebateHome", str(debate_home), "-Nonce", nonce])
    assert r2.returncode == 0
    assert r2.stdout.strip() == nonce
    assert r2.stderr == ""
    assert read_raw(lane_home) == before  # acquiredTicksUtc included, byte-identical


def test_live_holder_debate_home_differs_exits_2(lane_home, debate_home, self_identity, tmp_path):
    pid, ticks = self_identity
    debate_id = new_token()
    r1 = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", debate_id,
                   "-OwnerPid", pid, "-OwnerStartTicksUtc", ticks,
                   "-DebateHome", str(debate_home)])
    nonce = r1.stdout.strip()
    other_home = tmp_path / "other-debate-home"
    other_home.mkdir()
    result = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", debate_id,
                        "-OwnerPid", pid, "-OwnerStartTicksUtc", ticks,
                        "-DebateHome", str(other_home), "-Nonce", nonce])
    assert result.returncode == 2


def test_four_second_wait_against_live_holder_exits_3_no_reclaim(lane_home, debate_home, self_identity):
    pid, ticks = self_identity
    held = write_held(lane_home, host=COMPUTERNAME, ownerPid=int(pid), ownerStartTicksUtc=ticks)
    before = read_raw(lane_home)
    start = time.monotonic()
    result = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", new_token(),
                        "-OwnerPid", pid, "-OwnerStartTicksUtc", ticks,
                        "-DebateHome", str(debate_home), "-WaitSeconds", "4", "-PollSeconds", "1"],
                       timeout=15)
    elapsed = time.monotonic() - start
    assert result.returncode == 3
    assert elapsed >= 3.5
    assert f"liveness LIVE" in result.stderr
    assert read_raw(lane_home) == before


# ---------------------------------------------------------------------
# DebateHome normalization
# ---------------------------------------------------------------------
def test_debate_home_relative_and_trailing_separator_forms_are_equal(lane_home, tmp_path, self_identity):
    pid, ticks = self_identity
    real = tmp_path / "dh"
    real.mkdir()
    debate_id = new_token()
    r1 = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", debate_id,
                   "-OwnerPid", pid, "-OwnerStartTicksUtc", ticks,
                   "-DebateHome", str(real) + "\\"])
    nonce = r1.stdout.strip()
    assert r1.returncode == 0
    cwd_relative = os.path.relpath(str(real), str(tmp_path))
    r2 = subprocess.run(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(SCRIPT),
         "-Acquire", "-LaneHome", str(lane_home), "-DebateId", debate_id,
         "-OwnerPid", pid, "-OwnerStartTicksUtc", ticks,
         "-DebateHome", cwd_relative, "-Nonce", nonce],
        capture_output=True, text=True, cwd=str(tmp_path))
    assert r2.returncode == 0, (r2.stdout, r2.stderr)
    assert r2.stdout.strip() == nonce


def test_debate_home_drive_root_spellings_are_equal_and_normalize_to_root(lane_home, self_identity):
    pid, ticks = self_identity
    drive_root = os.environ.get("SystemDrive", "C:") + "\\"
    debate_id = new_token()
    r1 = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", debate_id,
                   "-OwnerPid", pid, "-OwnerStartTicksUtc", ticks,
                   "-DebateHome", drive_root])
    nonce = r1.stdout.strip()
    assert r1.returncode == 0
    rec = json.loads(lock_path(lane_home).read_text(encoding="utf-8"))
    assert rec["debateHome"].rstrip("\\/") + "\\" == drive_root or rec["debateHome"] == drive_root
    # A second equivalent spelling of the SAME root (doubled separator)
    # must still compare equal under normalization - never trimmed to a
    # drive-relative "C:" form.
    other_spelling = os.environ.get("SystemDrive", "C:") + "\\\\"
    r2 = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", debate_id,
                   "-OwnerPid", pid, "-OwnerStartTicksUtc", ticks,
                   "-DebateHome", other_spelling, "-Nonce", nonce])
    assert r2.returncode == 0, (r2.stdout, r2.stderr)
    assert r2.stdout.strip() == nonce


def test_debate_home_genuinely_different_path_is_not_equal(lane_home, tmp_path, self_identity):
    pid, ticks = self_identity
    home_a = tmp_path / "a"
    home_b = tmp_path / "b"
    home_a.mkdir()
    home_b.mkdir()
    debate_id = new_token()
    r1 = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", debate_id,
                   "-OwnerPid", pid, "-OwnerStartTicksUtc", ticks, "-DebateHome", str(home_a)])
    nonce = r1.stdout.strip()
    r2 = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", debate_id,
                   "-OwnerPid", pid, "-OwnerStartTicksUtc", ticks,
                   "-DebateHome", str(home_b), "-Nonce", nonce])
    assert r2.returncode == 2


# ---------------------------------------------------------------------
# UNMEASURABLE liveness fault seam
# ---------------------------------------------------------------------
def test_unmeasurable_status_reports_unknown_never_live(lane_home, self_identity):
    pid, ticks = self_identity
    write_held(lane_home, host=COMPUTERNAME, ownerPid=int(pid), ownerStartTicksUtc=ticks)
    result = run_lock(["-Status", "-LaneHome", str(lane_home)],
                       env={"PARALLAX_LANE_LOCK_STARTTIME_FAULT": "1"})
    assert result.returncode == 0
    obj = json.loads(result.stdout)
    assert obj["liveness"] == "UNKNOWN"


def test_unmeasurable_exact_identity_reacquires_idempotently(lane_home, debate_home, self_identity):
    pid, ticks = self_identity
    debate_id = new_token()
    r1 = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", debate_id,
                   "-OwnerPid", pid, "-OwnerStartTicksUtc", ticks,
                   "-DebateHome", str(debate_home)])
    nonce = r1.stdout.strip()
    r2 = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", debate_id,
                   "-OwnerPid", pid, "-OwnerStartTicksUtc", ticks,
                   "-DebateHome", str(debate_home), "-Nonce", nonce],
                  env={"PARALLAX_LANE_LOCK_STARTTIME_FAULT": "1"})
    assert r2.returncode == 0
    assert r2.stdout.strip() == nonce


def test_unmeasurable_competing_identity_contends_not_reclaims(lane_home, debate_home, self_identity):
    pid, ticks = self_identity
    debate_id = new_token()
    run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", debate_id,
              "-OwnerPid", pid, "-OwnerStartTicksUtc", ticks, "-DebateHome", str(debate_home)])
    result = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", new_token(),
                        "-OwnerPid", pid, "-OwnerStartTicksUtc", ticks,
                        "-DebateHome", str(debate_home)],
                       env={"PARALLAX_LANE_LOCK_STARTTIME_FAULT": "1"})
    assert result.returncode == 3
    assert "liveness UNMEASURABLE" in result.stderr


# ---------------------------------------------------------------------
# Foreign-host x mode matrix
# ---------------------------------------------------------------------
def test_foreign_host_acquire_exits_4(lane_home, debate_home):
    write_held(lane_home, host="SOME-OTHER-HOST")
    result = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", new_token(),
                        "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS,
                        "-DebateHome", str(debate_home)])
    assert result.returncode == 4


def test_foreign_host_release_exits_4(lane_home):
    rec = write_held(lane_home, host="SOME-OTHER-HOST")
    result = run_lock(["-Release", "-LaneHome", str(lane_home), "-DebateId", rec["debateId"],
                        "-OwnerPid", str(rec["ownerPid"]), "-OwnerStartTicksUtc", rec["ownerStartTicksUtc"],
                        "-Nonce", rec["nonce"]])
    assert result.returncode == 4


def test_foreign_host_malformed_override_on_wellformed_exits_4(lane_home):
    write_held(lane_home, host="SOME-OTHER-HOST")
    result = run_lock(["-MalformedOverride", "-LaneHome", str(lane_home),
                        "-ConfirmSha256", "a" * 64])
    assert result.returncode == 4


def test_foreign_host_force_release_succeeds_with_confirmed_identity(lane_home):
    rec = write_held(lane_home, host="SOME-OTHER-HOST")
    result = run_lock(["-ForceRelease", "-LaneHome", str(lane_home),
                        "-ConfirmHost", rec["host"], "-ConfirmOwnerPid", str(rec["ownerPid"]),
                        "-ConfirmOwnerStartTicksUtc", rec["ownerStartTicksUtc"],
                        "-ConfirmDebateId", rec["debateId"], "-ConfirmNonce", rec["nonce"]])
    assert result.returncode == 0
    assert (f"force-released holder: host {rec['host']} pid {rec['ownerPid']} "
            f"ticks {rec['ownerStartTicksUtc']} debate {rec['debateId']} "
            f"home {rec['debateHome']}") in result.stderr
    assert read_raw(lane_home) == b'{"version":1,"state":"free"}'


def test_force_release_identity_mismatch_exits_5_untouched(lane_home):
    rec = write_held(lane_home)
    before = read_raw(lane_home)
    result = run_lock(["-ForceRelease", "-LaneHome", str(lane_home),
                        "-ConfirmHost", rec["host"], "-ConfirmOwnerPid", str(rec["ownerPid"]),
                        "-ConfirmOwnerStartTicksUtc", rec["ownerStartTicksUtc"],
                        "-ConfirmDebateId", new_token(), "-ConfirmNonce", rec["nonce"]])
    assert result.returncode == 5
    assert read_raw(lane_home) == before


def test_release_identity_mismatch_exits_5_untouched(lane_home):
    rec = write_held(lane_home)
    before = read_raw(lane_home)
    result = run_lock(["-Release", "-LaneHome", str(lane_home), "-DebateId", rec["debateId"],
                        "-OwnerPid", str(rec["ownerPid"]), "-OwnerStartTicksUtc", rec["ownerStartTicksUtc"],
                        "-Nonce", new_token()])
    assert result.returncode == 5
    assert read_raw(lane_home) == before


def test_release_against_free_record_exits_5(lane_home):
    write_raw(lane_home, b'{"version":1,"state":"free"}')
    result = run_lock(["-Release", "-LaneHome", str(lane_home), "-DebateId", new_token(),
                        "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS, "-Nonce", new_token()])
    assert result.returncode == 5


def test_malformed_override_on_wellformed_same_host_held_exits_5(lane_home):
    write_held(lane_home)
    result = run_lock(["-MalformedOverride", "-LaneHome", str(lane_home),
                        "-ConfirmSha256", "a" * 64])
    assert result.returncode == 5


def test_malformed_exits_4_for_release_and_force_release(lane_home):
    write_raw(lane_home, b"not json")
    r1 = run_lock(["-Release", "-LaneHome", str(lane_home), "-DebateId", new_token(),
                   "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS, "-Nonce", new_token()])
    assert r1.returncode == 4
    r2 = run_lock(["-ForceRelease", "-LaneHome", str(lane_home), "-ConfirmHost", COMPUTERNAME,
                   "-ConfirmOwnerPid", "1", "-ConfirmOwnerStartTicksUtc", "1",
                   "-ConfirmDebateId", new_token(), "-ConfirmNonce", new_token()])
    assert r2.returncode == 4


# ---------------------------------------------------------------------
# -Status: byte-identical, never exit 4
# ---------------------------------------------------------------------
def test_status_leaves_held_file_byte_identical(lane_home):
    write_held(lane_home)
    before = read_raw(lane_home)
    result = run_lock(["-Status", "-LaneHome", str(lane_home)])
    assert result.returncode == 0
    assert read_raw(lane_home) == before


def test_status_on_malformed_exits_0_never_4(lane_home):
    write_raw(lane_home, b"not json")
    result = run_lock(["-Status", "-LaneHome", str(lane_home)])
    assert result.returncode == 0
    assert json.loads(result.stdout)["state"] == "MALFORMED"


def test_status_on_foreign_host_reports_unknown_liveness(lane_home):
    write_held(lane_home, host="SOME-OTHER-HOST", ownerPid=os.getpid())
    result = run_lock(["-Status", "-LaneHome", str(lane_home)])
    assert result.returncode == 0
    obj = json.loads(result.stdout)
    assert obj["liveness"] == "UNKNOWN"


# ---------------------------------------------------------------------
# Parameter-value validation (exit 2, no mutation, pre-handle)
# ---------------------------------------------------------------------
@pytest.mark.parametrize("wait,poll", [("-1", "2"), ("abc", "2"), ("1.5", "2"),
                                        ("1", "0"), ("1", "-1"), ("1", "abc")])
def test_bad_wait_or_poll_values_exit_2_no_mutation(lane_home, debate_home, wait, poll):
    result = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", new_token(),
                        "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS,
                        "-DebateHome", str(debate_home), "-WaitSeconds", wait, "-PollSeconds", poll])
    assert result.returncode == 2
    assert not lock_path(lane_home).exists()


@pytest.mark.parametrize("bad_token", ["not-hex", "a" * 31, "A" * 32, "g" * 32])
def test_bad_debate_id_token_exits_2_no_mutation(lane_home, debate_home, bad_token):
    result = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", bad_token,
                        "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS, "-DebateHome", str(debate_home)])
    assert result.returncode == 2
    assert not lock_path(lane_home).exists()


def test_empty_debate_id_is_refused_nonzero_no_mutation(lane_home, debate_home):
    # An empty string for a mandatory [string] parameter is PowerShell's
    # OWN binder refusal (ParameterArgumentValidationErrorEmptyStringNotAllowed),
    # not this script's -DebateId value check - still exit-code-table row
    # 1 territory (never emitted by script code), so only "nonzero, no
    # mutation" is asserted here, not the specific script-level exit 2.
    result = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", "",
                        "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS, "-DebateHome", str(debate_home)])
    assert result.returncode != 0
    assert not lock_path(lane_home).exists()


def test_owner_pid_zero_exits_2(lane_home, debate_home):
    result = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", new_token(),
                        "-OwnerPid", "0", "-OwnerStartTicksUtc", "1", "-DebateHome", str(debate_home)])
    assert result.returncode == 2


def test_hostname_comparison_is_case_insensitive(lane_home, debate_home, self_identity):
    pid, ticks = self_identity
    write_held(lane_home, host=COMPUTERNAME.lower() if COMPUTERNAME else COMPUTERNAME,
               ownerPid=int(pid), ownerStartTicksUtc=ticks)
    result = run_lock(["-Status", "-LaneHome", str(lane_home)])
    assert result.returncode == 0
    obj = json.loads(result.stdout)
    assert obj["liveness"] == "LIVE"  # same-host recognized despite case difference


# ---------------------------------------------------------------------
# Binding refusal: nonzero exit, no mutation
# ---------------------------------------------------------------------
def test_binding_refusal_exits_nonzero_and_creates_nothing(lane_home):
    result = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-NotARealParameter", "x"])
    assert result.returncode != 0
    assert not lock_path(lane_home).exists()


def test_binding_refusal_leaves_existing_lock_byte_identical(lane_home):
    write_held(lane_home)
    before = read_raw(lane_home)
    result = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-NotARealParameter", "x"])
    assert result.returncode != 0
    assert read_raw(lane_home) == before


def test_ambiguous_parameter_set_exits_nonzero(lane_home, debate_home):
    result = run_lock(["-Acquire", "-Release", "-LaneHome", str(lane_home),
                        "-DebateId", new_token(), "-OwnerPid", "1",
                        "-OwnerStartTicksUtc", "1", "-DebateHome", str(debate_home),
                        "-Nonce", new_token()])
    assert result.returncode != 0


# ---------------------------------------------------------------------
# Exit-code exhaustiveness
# ---------------------------------------------------------------------
def test_exit_code_exhaustiveness_across_the_bound_invocation_matrix(lane_home, debate_home, self_identity):
    pid, ticks = self_identity
    observed = set()

    # 0: successful acquire
    r = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", new_token(),
                  "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS, "-DebateHome", str(debate_home)])
    observed.add(r.returncode)

    # 2: bad parameter value
    r = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", "bad",
                  "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS, "-DebateHome", str(debate_home)])
    observed.add(r.returncode)

    # 3: contention against a LIVE holder, zero wait budget
    write_held(lane_home, host=COMPUTERNAME, ownerPid=int(pid), ownerStartTicksUtc=ticks)
    r = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", new_token(),
                  "-OwnerPid", pid, "-OwnerStartTicksUtc", ticks, "-DebateHome", str(debate_home)])
    observed.add(r.returncode)

    # 4: malformed record
    write_raw(lane_home, b"not json")
    r = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", new_token(),
                  "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS, "-DebateHome", str(debate_home)])
    observed.add(r.returncode)

    # 5: release with nothing applicable
    write_raw(lane_home, b'{"version":1,"state":"free"}')
    r = run_lock(["-Release", "-LaneHome", str(lane_home), "-DebateId", new_token(),
                  "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS, "-Nonce", new_token()])
    observed.add(r.returncode)

    # 6: unreadable (directory at the lock path)
    other_home = lane_home.parent / "lane6"
    other_home.mkdir()
    lock_path(other_home).mkdir()
    r = run_lock(["-Status", "-LaneHome", str(other_home)])
    observed.add(r.returncode)

    assert observed <= {0, 2, 3, 4, 5, 6}, observed
    # every one of the six lock-code branches must be reachable, or this
    # assertion is passing by having verified nothing.
    assert observed == {0, 2, 3, 4, 5, 6}, observed


# ---------------------------------------------------------------------
# Live contention oracles, synchronized on PARALLAX_LANE_LOCK_CONTENTION_SIGNAL.
# Each covers BOTH branches: the exclusive HANDLE, and a readable LIVE
# HOLDER. Wall time never gates the assertions - only the signal does.
# ---------------------------------------------------------------------
def _run_clamp_case(lane_home, debate_home, sig_path, extra_setup_returncode_check=None, **acquire_kwargs):
    args = ["-Acquire", "-LaneHome", str(lane_home), "-DebateId", new_token(),
            "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS, "-DebateHome", str(debate_home),
            "-WaitSeconds", "1", "-PollSeconds", "10"]
    proc = start_lock_bg(args, env={"PARALLAX_LANE_LOCK_CONTENTION_SIGNAL": str(sig_path)})
    branch = wait_for_signal(sig_path, timeout=10)
    if branch is None:
        proc.terminate()
        pytest.fail("contention signal never arrived within 10s")
    t_signal = time.monotonic()
    # still alive at least 0.5s after the signal
    time.sleep(0.5)
    still_alive = proc.poll() is None
    stdout, stderr = proc.communicate(timeout=10)
    elapsed_from_signal = time.monotonic() - t_signal
    if not still_alive:
        pytest.fail("contender exited before 0.5s from the contention signal - "
                     "the wait budget was not honoured")
    assert elapsed_from_signal <= 5.0, elapsed_from_signal
    assert proc.returncode == 3, (stdout, stderr)
    return branch, stdout, stderr


def test_clamp_handle_branch(lane_home, debate_home, tmp_path):
    # Pre-write a valid free record, then hold the exclusive handle on it
    # from a separate process so the contender can never even open it.
    write_raw(lane_home, b'{"version":1,"state":"free"}')
    before = read_raw(lane_home)
    sig_path = tmp_path / "sig-clamp-handle.txt"
    holder_script = (
        f"$fs = [System.IO.File]::Open('{lock_path(lane_home)}', "
        "[System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, "
        "[System.IO.FileShare]::None); Start-Sleep -Seconds 3; $fs.Close()"
    )
    holder = subprocess.Popen([POWERSHELL, "-NoProfile", "-NonInteractive", "-Command", holder_script],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        time.sleep(0.3)  # let the holder actually acquire the handle first
        branch, _, stderr = _run_clamp_case(lane_home, debate_home, sig_path)
        assert branch == "handle"
        assert "contended: the lock file is held by another writer, wait budget 1s expired" in stderr
        # The holder still owns the exclusive OS handle at this point (its
        # own 3s sleep has not elapsed yet) - wait for it to release before
        # reading, or Python's own open() collides with the same
        # FileShare.None handle this test is using to prove contention.
        holder.wait(timeout=10)
        assert read_raw(lane_home) == before
    finally:
        holder.terminate()
        try:
            holder.wait(timeout=10)
        except subprocess.TimeoutExpired:
            holder.kill()


def test_clamp_holder_branch(lane_home, debate_home, tmp_path):
    sleeper = start_sleeper(40)
    try:
        ticks = _ticks_for_pid(sleeper.pid)
        assert DIGITS_RE.match(ticks), ticks
        debate_id = new_token()
        r0 = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", debate_id,
                        "-OwnerPid", str(sleeper.pid), "-OwnerStartTicksUtc", ticks,
                        "-DebateHome", str(debate_home)])
        assert r0.returncode == 0
        before = read_raw(lane_home)
        sig_path = tmp_path / "sig-clamp-holder.txt"
        branch, _, stderr = _run_clamp_case(lane_home, debate_home, sig_path)
        assert branch == "holder"
        assert f"contended: holder pid {sleeper.pid} ticks {ticks} debate {debate_id}, liveness LIVE, wait budget 1s expired" in stderr
        assert read_raw(lane_home) == before
    finally:
        sleeper.terminate()
        try:
            sleeper.wait(timeout=10)
        except subprocess.TimeoutExpired:
            sleeper.kill()


def test_retry_success_handle_branch(lane_home, debate_home, tmp_path):
    write_raw(lane_home, b'{"version":1,"state":"free"}')
    sig_path = tmp_path / "sig-retry-handle.txt"
    release_path = tmp_path / "release-handle.txt"
    holder_script = (
        f"$fs = [System.IO.File]::Open('{lock_path(lane_home)}', "
        "[System.IO.FileMode]::Open, [System.IO.FileAccess]::ReadWrite, "
        "[System.IO.FileShare]::None); "
        f"while (-not (Test-Path '{release_path}')) {{ Start-Sleep -Milliseconds 100 }}; $fs.Close()"
    )
    holder = subprocess.Popen([POWERSHELL, "-NoProfile", "-NonInteractive", "-Command", holder_script],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        time.sleep(0.3)
        args = ["-Acquire", "-LaneHome", str(lane_home), "-DebateId", new_token(),
                "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS, "-DebateHome", str(debate_home),
                "-WaitSeconds", "30", "-PollSeconds", "1"]
        contender = start_lock_bg(args, env={"PARALLAX_LANE_LOCK_CONTENTION_SIGNAL": str(sig_path)})
        branch = wait_for_signal(sig_path, timeout=10)
        if branch is None:
            contender.terminate()
            pytest.fail("contention signal never arrived within 10s")
        assert branch == "handle"
        assert contender.poll() is None, "contender should still be waiting"
        release_path.write_text("go", encoding="ascii")
        stdout, stderr = contender.communicate(timeout=10)
        assert contender.returncode == 0, (stdout, stderr)
        assert TOKEN_RE.match(stdout.strip())
    finally:
        release_path.write_text("go", encoding="ascii")
        holder.terminate()
        try:
            holder.wait(timeout=10)
        except subprocess.TimeoutExpired:
            holder.kill()


def test_retry_success_holder_branch(lane_home, debate_home, tmp_path):
    sleeper = start_sleeper(40)
    try:
        ticks = _ticks_for_pid(sleeper.pid)
        assert DIGITS_RE.match(ticks), ticks
        debate_id = new_token()
        r0 = run_lock(["-Acquire", "-LaneHome", str(lane_home), "-DebateId", debate_id,
                        "-OwnerPid", str(sleeper.pid), "-OwnerStartTicksUtc", ticks,
                        "-DebateHome", str(debate_home)])
        assert r0.returncode == 0
        held_nonce = r0.stdout.strip()

        sig_path = tmp_path / "sig-retry-holder.txt"
        args = ["-Acquire", "-LaneHome", str(lane_home), "-DebateId", new_token(),
                "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS, "-DebateHome", str(debate_home),
                "-WaitSeconds", "30", "-PollSeconds", "1"]
        contender = start_lock_bg(args, env={"PARALLAX_LANE_LOCK_CONTENTION_SIGNAL": str(sig_path)})
        branch = wait_for_signal(sig_path, timeout=10)
        if branch is None:
            contender.terminate()
            pytest.fail("contention signal never arrived within 10s")
        assert branch == "holder"
        assert contender.poll() is None, "contender should still be retrying"

        release = run_lock(["-Release", "-LaneHome", str(lane_home), "-DebateId", debate_id,
                             "-OwnerPid", str(sleeper.pid), "-OwnerStartTicksUtc", ticks,
                             "-Nonce", held_nonce])
        assert release.returncode == 0

        stdout, stderr = contender.communicate(timeout=10)
        assert contender.returncode == 0, (stdout, stderr)
        new_nonce = stdout.strip()
        assert TOKEN_RE.match(new_nonce)
        assert new_nonce != held_nonce

        status = run_lock(["-Status", "-LaneHome", str(lane_home)])
        obj = json.loads(status.stdout)
        assert obj["nonce"] == new_nonce
        assert obj["ownerPid"] == int(LIVE_PID)
    finally:
        sleeper.terminate()
        try:
            sleeper.wait(timeout=10)
        except subprocess.TimeoutExpired:
            sleeper.kill()


# =====================================================================
# 0.22.0, plan debate round 1. Acquire recorded a proposed owner without
# ever checking it was alive.
# =====================================================================

def _dead_pid():
    """A pid that is not running.

    Started and reaped, so the identity is well formed and the process
    is gone - which is exactly the shape a wrapper-resolved owner has by
    the time a debate reaches its teardown.
    """
    proc = subprocess.Popen(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-Command", "exit 0"],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    proc.wait(timeout=30)
    return str(proc.pid)


def test_acquire_refuses_an_owner_that_is_not_live(lane_home, debate_home):
    """The severe half of backlog item 26, and it needed no wrapping
    harness to reach.

    `Get-Liveness` has been in this tool the whole time. Acquire called
    it on ONE thing: the EXISTING holder's record, to decide reclaim
    rights. It never called it on the PROPOSED owner - that path checked
    only that the pid and ticks were syntactically well formed and then
    wrote them down.

    So a caller could record an owner that was already DEAD. The next
    acquire reads that record as DEAD, reclaims it, and the mutual
    exclusion this lock exists to provide is gone while every status
    read looks completely ordinary. The stuck-lock symptom was the
    visible half of item 26; this is the silent half.
    """
    rc = run_lock(["-Acquire", "-LaneHome", str(lane_home),
                   "-DebateId", "a" * 32,
                   "-OwnerPid", _dead_pid(), "-OwnerStartTicksUtc", LIVE_TICKS,
                   "-DebateHome", str(debate_home), "-WaitSeconds", "0"])
    assert rc.returncode != 0, (rc.returncode, rc.stdout, rc.stderr)
    assert "live" in (rc.stdout + rc.stderr).lower(), (rc.stdout, rc.stderr)


def test_acquire_refuses_an_owner_whose_ticks_do_not_match(lane_home, debate_home):
    """A live pid with the WRONG start ticks is the identity-reuse case.

    `Get-Liveness` already classifies it DEAD, because a pid can be
    reused by a different process. Acquire must refuse it for the same
    reason it refuses a vanished one: the identity names something that
    is not the process the caller thinks it is.
    """
    rc = run_lock(["-Acquire", "-LaneHome", str(lane_home),
                   "-DebateId", "b" * 32,
                   "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", "1",
                   "-DebateHome", str(debate_home), "-WaitSeconds", "0"])
    assert rc.returncode != 0, (rc.returncode, rc.stdout, rc.stderr)
    assert "live" in (rc.stdout + rc.stderr).lower(), (rc.stdout, rc.stderr)


# ---------------------------------------------------------------------
# ownerName as an OPTIONAL held-v1 field
# ---------------------------------------------------------------------
def test_acquire_records_an_optional_owner_name(lane_home, debate_home):
    """The name resolution now reports has to reach the RECORD, or the
    only place a wrong owner is legible is the moment it is resolved -
    which is the one moment nobody is looking."""
    rc = run_lock(["-Acquire", "-LaneHome", str(lane_home),
                   "-DebateId", "e" * 32,
                   "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS,
                   "-OwnerName", "claude.exe",
                   "-DebateHome", str(debate_home), "-WaitSeconds", "0"])
    assert rc.returncode == 0, (rc.returncode, rc.stdout, rc.stderr)
    rec = json.loads(read_raw(lane_home).decode("utf-8"))
    assert rec["ownerName"] == "claude.exe", rec


def test_acquire_without_owner_name_writes_no_such_field(lane_home, debate_home):
    """OPTIONAL means absent, not empty.

    A record written with an empty ownerName would be a record claiming
    to carry a name, and every reader would have to decide what an empty
    one means. Absent has one meaning already.
    """
    rc = run_lock(["-Acquire", "-LaneHome", str(lane_home),
                   "-DebateId", "f" * 32,
                   "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS,
                   "-DebateHome", str(debate_home), "-WaitSeconds", "0"])
    assert rc.returncode == 0, (rc.returncode, rc.stdout, rc.stderr)
    rec = json.loads(read_raw(lane_home).decode("utf-8"))
    assert "ownerName" not in rec, rec


def test_a_held_record_carrying_owner_name_is_well_formed(lane_home):
    """The migration direction that matters on the way IN.

    The held schema is an EXACT field set, so before this change a
    record carrying ownerName classified MALFORMED - which is exit 4 and
    a lane nobody can take without the guarded override.
    """
    write_held(lane_home, host=COMPUTERNAME, ownerName="claude.exe")
    result = run_lock(["-Status", "-LaneHome", str(lane_home)])
    assert result.returncode == 0
    obj = json.loads(result.stdout)
    assert obj["state"] == "held", obj
    assert obj["ownerName"] == "claude.exe", obj


def test_a_held_record_without_owner_name_is_still_well_formed(lane_home):
    """The migration direction that matters on the way OUT, and the
    reason the field is optional rather than required.

    Every record written before this change lacks it. A required field
    would have turned all of them MALFORMED the moment the plugin cache
    updated - a lane locked by an upgrade, not by a debate.
    """
    write_held(lane_home, host=COMPUTERNAME)
    result = run_lock(["-Status", "-LaneHome", str(lane_home)])
    assert result.returncode == 0
    obj = json.loads(result.stdout)
    assert obj["state"] == "held", obj
    assert "ownerName" not in obj, obj


def test_acquire_refuses_a_blank_owner_name(lane_home, debate_home):
    """A supplied name that says nothing is a caller error, not a record
    to write. Refusing keeps "present" and "informative" the same thing.
    """
    rc = run_lock(["-Acquire", "-LaneHome", str(lane_home),
                   "-DebateId", "0" * 32,
                   "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS,
                   "-OwnerName", "   ",
                   "-DebateHome", str(debate_home), "-WaitSeconds", "0"])
    assert rc.returncode == 2, (rc.returncode, rc.stdout, rc.stderr)
    assert read_raw(lane_home) in (None, b'{"version":1,"state":"free"}'), read_raw(lane_home)


def test_reclaiming_a_dead_holder_carries_the_new_owner_name(lane_home, debate_home):
    """The reclaim writer is a SECOND record writer, and a field added to
    one writer and not the other is a field that vanishes on reclaim."""
    write_held(lane_home, host=COMPUTERNAME, ownerName="stale.exe")
    rc = run_lock(["-Acquire", "-LaneHome", str(lane_home),
                   "-DebateId", "1" * 32,
                   "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS,
                   "-OwnerName", "claude.exe",
                   "-DebateHome", str(debate_home), "-WaitSeconds", "0"])
    assert rc.returncode == 0, (rc.returncode, rc.stdout, rc.stderr)
    rec = json.loads(read_raw(lane_home).decode("utf-8"))
    assert rec["ownerName"] == "claude.exe", rec


def test_acquire_refuses_to_write_a_record_for_an_unmeasurable_owner(
        lane_home, debate_home):
    """A record is a CLAIM that this owner holds the lane, so writing one
    requires LIVE and not merely "not known to be dead".

    The first shipped cut refused only DEAD, and that left a residual:
    an owner whose start time could not be read was written down without
    the pid-reuse guard ever running. The cross-vendor round pointed out
    that the residual is removable without cost, because the case the
    DEAD-only rule was protecting is the NON-WRITING idempotent re-entry
    - matching nonce, matching identity - which is pinned separately by
    test_unmeasurable_exact_identity_reacquires_idempotently and is
    untouched by this rule.

    So: LIVE to WRITE, and UNMEASURABLE only where nothing is written.
    """
    rc = run_lock(["-Acquire", "-LaneHome", str(lane_home),
                   "-DebateId", "d" * 32,
                   "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS,
                   "-DebateHome", str(debate_home), "-WaitSeconds", "0"],
                  env={"PARALLAX_LANE_LOCK_STARTTIME_FAULT": "1"})
    assert rc.returncode == 2, (rc.returncode, rc.stdout, rc.stderr)
    assert read_raw(lane_home) in (None, b'{"version":1,"state":"free"}'), read_raw(lane_home)


def test_an_owner_that_dies_during_contention_is_never_written(
        lane_home, debate_home, self_identity):
    """The window the single pre-loop check could not see.

    Liveness was measured ONCE, before the acquisition loop. A caller
    that waits behind a holder can therefore be measured LIVE, wait,
    DIE, and still have its identity written the moment the holder
    releases - which is exactly the already-dead record item 26 calls
    the silent half, arrived at by a different road.

    The fixture is synchronized rather than timed: the holder is only
    released AFTER the proposed owner has been killed and reaped, so the
    write attempt provably happens after the death.
    """
    pid, ticks = self_identity
    holder_debate = new_token()
    r1 = run_lock(["-Acquire", "-LaneHome", str(lane_home),
                   "-DebateId", holder_debate,
                   "-OwnerPid", pid, "-OwnerStartTicksUtc", ticks,
                   "-DebateHome", str(debate_home)])
    assert r1.returncode == 0, (r1.stdout, r1.stderr)
    holder_nonce = r1.stdout.strip()

    victim = start_sleeper(seconds=120)
    victim_ticks = _ticks_for_pid(victim.pid)
    assert DIGITS_RE.match(victim_ticks), victim_ticks

    waiter = start_lock_bg(["-Acquire", "-LaneHome", str(lane_home),
                            "-DebateId", new_token(),
                            "-OwnerPid", str(victim.pid),
                            "-OwnerStartTicksUtc", victim_ticks,
                            "-DebateHome", str(debate_home),
                            "-WaitSeconds", "30", "-PollSeconds", "1"])
    try:
        time.sleep(2.0)
        victim.kill()
        victim.wait(timeout=30)
        rel = run_lock(["-Release", "-LaneHome", str(lane_home),
                        "-DebateId", holder_debate, "-OwnerPid", pid,
                        "-OwnerStartTicksUtc", ticks, "-Nonce", holder_nonce])
        assert rel.returncode == 0, (rel.stdout, rel.stderr)
        stdout, stderr = waiter.communicate(timeout=60)
    finally:
        if waiter.poll() is None:
            waiter.kill()

    assert waiter.returncode == 2, (waiter.returncode, stdout, stderr)
    assert read_raw(lane_home) == b'{"version":1,"state":"free"}', read_raw(lane_home)


def test_acquire_still_accepts_a_live_owner(lane_home, debate_home):
    """The positive control. The refusal must not close the ordinary
    case, which is the whole reason the lane exists."""
    rc = run_lock(["-Acquire", "-LaneHome", str(lane_home),
                   "-DebateId", "c" * 32,
                   "-OwnerPid", LIVE_PID, "-OwnerStartTicksUtc", LIVE_TICKS,
                   "-DebateHome", str(debate_home), "-WaitSeconds", "0"])
    assert rc.returncode == 0, (rc.returncode, rc.stdout, rc.stderr)
    assert TOKEN_RE.match(rc.stdout.strip()), rc.stdout
