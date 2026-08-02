"""Shared production helper for the kimi-code lane-credential live gate
(Task 7, 2026-08-01 lane-credential-and-lock plan) and its offline
support-oracle suite.

Both evals/multi-model-verify/test_lane_credential_live.py (opt-in, real
client) and evals/multi-model-verify/test_lane_credential_live_support.py
(no opt-in, fake commands) import this module. It performs NO
live-environment check at import time, so importing it never drags live
setup into the offline suite - leaving that check inside this module, as
an early plan revision implied, would have done exactly that.

Everything here follows the plan's governing invariant: an unmade,
failed, or unreadable measurement is never a clean one, and a guard that
cannot be evaluated REFUSES rather than reading as passing. In practice
that means every wrapper below either returns a value that only exists
once every one of its component measurements succeeded, or raises -
never a sentinel (empty string, None, zero) that could compare equal to
another failed measurement.

SECRET DISCIPLINE. This repo is public. Nothing in this module ever
prints, logs, or raises with a credential VALUE embedded in it - the
SecretGuard exists specifically to intercept a captured process stream
before it can reach a pytest assertion or failure message, which is the
one place a write-time-only guard would already be too late (pytest
prints both operands/captured output on a failed assert).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
LOCK_TOOL = REPO_ROOT / "tools" / "kimi-lane-lock.ps1"
BUILDER = REPO_ROOT / "tools" / "new-kimi-lane-home.ps1"
CREDENTIAL_VALIDATOR = REPO_ROOT / "tools" / "read-kimi-credential-state.ps1"
LOGIN_WRAPPER = REPO_ROOT / "tools" / "new-kimi-lane-login.ps1"
MODEL_NOTES = (REPO_ROOT / "skills" / "multi-model-verify" / "references"
               / "model-prompting-notes.md")

SENTINEL_NAME = ".parallax-lane-home"

# The three dedicated lane-home roles (packet "Fixed names and values" /
# Task 7 body). A and B are the coexistence pair; C is the sole home the
# live suite deliberately expires and requires to rotate.
ENV_HOME_A = "PARALLAX_LANE_LIVE_HOME_A"
ENV_HOME_B = "PARALLAX_LANE_LIVE_HOME_B"
ENV_HOME_C = "PARALLAX_LANE_LIVE_HOME_C"
ENV_LIVE_OPT_IN = "PARALLAX_LANE_LIVE"

MARKER_NAME = ".parallax-login-created-ticks-utc"
_MARKER_PATTERN = re.compile(r"\A[0-9]+\Z")

_TOKEN_PATTERN = re.compile(r"\A[0-9a-f]{32}\Z")

# The credential validator's frozen status/detail table (Task 2's
# interface, "Fixed names and values" in the packet).
VALID_VERDICT_PAIRS = {
    ("ok", "valid"),
    ("absent", "no-file"),
    ("unreadable", "read-failed"),
    ("malformed", "not-json"),
    ("malformed", "not-object"),
    ("malformed", "missing-field"),
    ("malformed", "wrong-type"),
    ("malformed", "blank-token"),
}


# =======================================================================
# Host resolution and environment hygiene - the same pattern already used
# by test_kimi_lane_home.py / test_codex_context_probe.py.
# =======================================================================
def resolve_ps_host() -> Optional[str]:
    """PARALLAX_PS_HOST selects the interpreter for THIS invocation; else
    whichever of powershell/pwsh is on PATH. A missing host is reported by
    the caller as a FAILED measurement, never a skip, once the live suite
    has opted in - the module-level skip guard only covers the opt-in and
    the os.name check."""
    return (os.environ.get("PARALLAX_PS_HOST")
            or shutil.which("powershell") or shutil.which("pwsh"))


def clean_env(overrides: Optional[dict] = None) -> dict:
    """A copy of the current environment with every PSModulePath variant
    dropped (case-insensitively - os.environ normalizes keys to upper
    case on Windows, so a plain pop("PSModulePath") removes nothing) and
    `overrides` applied on top. A PowerShell 7 flavoured PSModulePath
    shadows the 5.1 copy of Microsoft.PowerShell.Security inside a
    powershell.exe child and breaks Get-Acl - the same fixture fact
    test_kimi_lane_home.py already relies on."""
    env = dict(os.environ)
    for key in [k for k in env if k.lower() == "psmodulepath"]:
        del env[key]
    if overrides:
        env.update(overrides)
    return env


def new_hex32() -> str:
    return uuid.uuid4().hex


def is_hex32(value: str) -> bool:
    return bool(_TOKEN_PATTERN.match(value or ""))


# =======================================================================
# Canonical backup model identity - read from the single source rather
# than hardcoded, because test_backup_lane.py's SWEEP_GLOBS (which covers
# evals/**/*.py) forbids the literal everywhere except
# skills/multi-model-verify/references/model-prompting-notes.md and
# evals/multi-model-verify/test_backup_lane.py itself.
# =======================================================================
class ModelNotesReadError(Exception):
    pass


def _read_model_notes_field(label: str) -> str:
    text = MODEL_NOTES.read_text(encoding="utf-8")
    match = re.search(re.escape(label) + r": `([^`]+)`", text)
    if not match:
        raise ModelNotesReadError(
            "could not read '%s' from %s" % (label, MODEL_NOTES))
    return match.group(1)


def read_canonical_backup_model() -> str:
    # "reviewer" is part of the label. The declaration in
    # model-prompting-notes.md reads "Canonical backup reviewer model id",
    # while the effort and provider labels below have no such word. A
    # shorter guess here read as a missing declaration and failed the
    # whole live module in its setup, which is the correct direction but
    # made the gate unrunnable rather than wrong.
    return _read_model_notes_field("Canonical backup reviewer model id")


def read_canonical_backup_effort() -> str:
    return _read_model_notes_field("Canonical backup reasoning effort")


def read_canonical_backup_provider() -> str:
    return _read_model_notes_field("Canonical backup provider")


# =======================================================================
# Owner resolution. Fail-closed: a nonzero exit or unparseable JSON
# raises rather than returning a sentinel identity.
# =======================================================================
class OwnerResolutionError(Exception):
    pass


def resolve_owner(host: str, timeout: float = 30) -> "OwnerIdentity":
    proc = subprocess.run(
        [host, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
         "-File", str(LOCK_TOOL), "-ResolveOwner"],
        capture_output=True, text=True, timeout=timeout, env=clean_env())
    if proc.returncode != 0:
        raise OwnerResolutionError(
            "owner resolution failed with exit %d: %s"
            % (proc.returncode, proc.stderr.strip()))
    try:
        obj = json.loads(proc.stdout.strip())
    except ValueError as exc:
        raise OwnerResolutionError(
            "owner resolution produced unparseable JSON: %r" % proc.stdout) from exc
    if (not isinstance(obj, dict) or "ownerPid" not in obj
            or "ownerStartTicksUtc" not in obj):
        raise OwnerResolutionError(
            "owner resolution JSON missing required fields: %r" % obj)
    return OwnerIdentity(str(obj["ownerPid"]), str(obj["ownerStartTicksUtc"]))


@dataclass(frozen=True)
class OwnerIdentity:
    owner_pid: str
    owner_ticks: str


# =======================================================================
# The lock tool: thin, fail-visible wrappers. Each returns the raw
# (returncode, stdout, stderr) shape rather than raising on a nonzero
# lock exit code, because contention/malformed/refused are all
# LEGITIMATE outcomes the callers assert against by exit code.
# =======================================================================
@dataclass
class LockResult:
    returncode: int
    stdout: str
    stderr: str


def _run_lock(host: str, args: list, timeout: float, env: Optional[dict]) -> LockResult:
    proc = subprocess.run(
        [host, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
         "-File", str(LOCK_TOOL)] + args,
        capture_output=True, text=True, timeout=timeout,
        env=(env if env is not None else clean_env()))
    return LockResult(proc.returncode, proc.stdout, proc.stderr)


def lock_acquire(host, lane_home, debate_id, owner_pid, owner_ticks, debate_home,
                  nonce=None, wait_seconds=None, poll_seconds=None,
                  timeout=60, env=None) -> LockResult:
    args = ["-Acquire", "-LaneHome", str(lane_home), "-DebateId", debate_id,
            "-OwnerPid", str(owner_pid), "-OwnerStartTicksUtc", str(owner_ticks),
            "-DebateHome", str(debate_home)]
    if nonce is not None:
        args += ["-Nonce", nonce]
    if wait_seconds is not None:
        args += ["-WaitSeconds", str(wait_seconds)]
    if poll_seconds is not None:
        args += ["-PollSeconds", str(poll_seconds)]
    return _run_lock(host, args, timeout, env)


def lock_release(host, lane_home, debate_id, owner_pid, owner_ticks, nonce,
                  timeout=60, env=None) -> LockResult:
    args = ["-Release", "-LaneHome", str(lane_home), "-DebateId", debate_id,
            "-OwnerPid", str(owner_pid), "-OwnerStartTicksUtc", str(owner_ticks),
            "-Nonce", nonce]
    return _run_lock(host, args, timeout, env)


class LockStatusError(Exception):
    pass


def lock_status(host, lane_home, timeout=60, env=None) -> dict:
    """An unmade measurement is never a clean one: a nonzero exit or
    unparseable stdout raises rather than being read as any particular
    lock state."""
    result = _run_lock(host, ["-Status", "-LaneHome", str(lane_home)], timeout, env)
    if result.returncode != 0:
        raise LockStatusError(
            "lock status failed with exit %d: %s" % (result.returncode, result.stderr))
    try:
        return json.loads(result.stdout)
    except ValueError as exc:
        raise LockStatusError("lock status produced unparseable JSON: %r" % result.stdout) from exc


def read_lock_bytes(lane_home) -> bytes:
    return (Path(lane_home) / "lane.lock").read_bytes()


# =======================================================================
# The credential validator wrapper - the four-part acceptance rule
# ("Fixed names and values" in the packet): the process launched, it
# exited 0, stderr was EMPTY, and stdout was exactly one parseable line
# whose object has exactly status/detail/fields with a status/detail
# pairing from the frozen table. Anything else is VALIDATOR FAILURE and
# is never read as a credential state.
# =======================================================================
@dataclass
class ValidatorResult:
    ok: bool
    status: Optional[str] = None
    detail: Optional[str] = None
    fields: Optional[list] = None


# Acceptance is ONE NONEMPTY LINE, optionally followed by exactly one LF
# or CRLF - not "discard blank lines, then require one survivor", which
# let a stdout of "\n\n{json}\n\n" pass as a single line (the fields
# fixture 8 bug: `[ln for ln in text.splitlines() if ln.strip() != ""]`
# discards blank lines BEFORE counting). \A and \Z, not ^ and $: $ would
# match before a single trailing newline even without multiline mode,
# which would silently accept a second trailing blank line here. Mirrors
# tools/new-kimi-lane-home.ps1's own `'\A(?<singleLine>[^\r\n]+)(\r\n|\n)?\z'`
# after its round-30 fix - the same algorithm, not merely the same intent.
_VALIDATOR_SINGLE_LINE_PATTERN = re.compile(r"\A([^\r\n]+)(\r\n|\n)?\Z")


def _accept_validator_output(returncode: int, stdout: str, stderr: str) -> ValidatorResult:
    """The four-part acceptance rule's pure decision core, split out from
    validate_credential() so the exact-line algorithm has a seam an
    offline oracle can drive directly - the real subprocess call cannot
    be made to emit a specific blank-separated stdout on demand."""
    if returncode != 0:
        return ValidatorResult(ok=False)
    if stderr != "":
        return ValidatorResult(ok=False)
    match = _VALIDATOR_SINGLE_LINE_PATTERN.match(stdout)
    if not match:
        return ValidatorResult(ok=False)
    line = match.group(1)
    try:
        obj = json.loads(line)
    except ValueError:
        return ValidatorResult(ok=False)
    if not isinstance(obj, dict) or set(obj.keys()) != {"status", "detail", "fields"}:
        return ValidatorResult(ok=False)
    status, detail, fields = obj["status"], obj["detail"], obj["fields"]
    if not isinstance(status, str) or not isinstance(detail, str):
        return ValidatorResult(ok=False)
    if not isinstance(fields, list) or not all(isinstance(f, str) for f in fields):
        return ValidatorResult(ok=False)
    if (status, detail) not in VALID_VERDICT_PAIRS:
        return ValidatorResult(ok=False)
    return ValidatorResult(ok=True, status=status, detail=detail, fields=fields)


def validate_credential(host, path, timeout=60, env=None) -> ValidatorResult:
    try:
        proc = subprocess.run(
            [host, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
             "-File", str(CREDENTIAL_VALIDATOR), "-Path", str(path)],
            capture_output=True, text=True, timeout=timeout,
            env=(env if env is not None else clean_env()))
    except (OSError, subprocess.TimeoutExpired):
        return ValidatorResult(ok=False)
    return _accept_validator_output(proc.returncode, proc.stdout, proc.stderr)


# =======================================================================
# The lane-home builder / remover. The BUILDER IS THE ACQUISITION: a
# successful build already holds that home's lock and returns the nonce
# in its custody line; nothing here acquires separately.
# =======================================================================
@dataclass
class BuildResult:
    returncode: int
    stdout: str
    stderr: str
    debate_home: Optional[str] = None
    nonce: Optional[str] = None


def _accept_custody_line(returncode: int, stdout: str):
    """The custody line's acceptance rule, split out so an offline oracle
    can drive it directly - the real builder cannot be made to emit a
    blank-separated stdout on demand.

    It is the SAME exact-line rule the validator uses, not "discard blank
    lines then require one survivor". This line carries the NONCE that
    governs the release, so a builder emitting two lines around a blank
    separator must never read as one custody line.
    """
    if returncode != 0:
        return None, None
    match = _VALIDATOR_SINGLE_LINE_PATTERN.match(stdout)
    if not match:
        return None, None
    try:
        obj = json.loads(match.group(1))
    except ValueError:
        return None, None
    if not isinstance(obj, dict) or set(obj.keys()) != {"debateHome", "nonce"}:
        return None, None
    return obj["debateHome"], obj["nonce"]


def build_lane_home(host, path, model, effort, lane_home, debate_id,
                     owner_pid, owner_ticks, timeout=180, env=None) -> BuildResult:
    args = [host, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
            "-File", str(BUILDER), "-Path", str(path), "-Model", model,
            "-Effort", effort, "-LaneHome", str(lane_home),
            "-DebateId", debate_id, "-OwnerPid", str(owner_pid),
            "-OwnerStartTicksUtc", str(owner_ticks)]
    proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout,
                           env=(env if env is not None else clean_env()))
    debate_home, nonce = _accept_custody_line(proc.returncode, proc.stdout)
    return BuildResult(proc.returncode, proc.stdout, proc.stderr, debate_home, nonce)


@dataclass
class RemoveResult:
    returncode: int
    stdout: str
    stderr: str


def remove_lane_home(host, path, lane_home, debate_id, owner_pid, owner_ticks,
                      nonce, timeout=180, env=None) -> RemoveResult:
    args = [host, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
            "-File", str(BUILDER), "-Path", str(path), "-Remove",
            "-LaneHome", str(lane_home), "-DebateId", debate_id,
            "-OwnerPid", str(owner_pid), "-OwnerStartTicksUtc", str(owner_ticks),
            "-Nonce", nonce]
    proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout,
                           env=(env if env is not None else clean_env()))
    return RemoveResult(proc.returncode, proc.stdout, proc.stderr)


class BuildRefusal(Exception):
    """A Build that never returned a nonce - Task 6's own internal cleanup
    already released whatever it held; -Remove must NEVER be called on
    this path."""

    def __init__(self, result: BuildResult):
        self.result = result
        super().__init__("lane-home build refused: exit %d: %s"
                          % (result.returncode, result.stderr.strip()))


class RemoveFailure(Exception):
    def __init__(self, result: RemoveResult):
        self.result = result
        super().__init__("lane-home remove failed: exit %d: %s"
                          % (result.returncode, result.stderr.strip()))


@dataclass
class Custody:
    host: str
    path: str
    lane_home: str
    debate_id: str
    owner_pid: str
    owner_ticks: str
    debate_home: str
    nonce: str


@contextmanager
def custody_of(host, path, model, effort, lane_home, debate_id, owner_pid,
                owner_ticks, build_timeout=180, remove_timeout=180,
                build_env=None, remove_env=None):
    """The MAIN OPERATION wrapper (packet lines 124-141). The builder IS
    the acquisition: this never acquires separately and never plainly
    releases. On a successful build the caller's `with`-block body runs
    the pre-command phase, the command and its capture, the post-command
    merge, and the stream guard - all four phases, under the SAME
    retained hold - then the real -Remove is ALWAYS attempted in a
    finally with the returned nonce.

    Cleanup precedence, frozen: a failure raised inside the block stays
    PRIMARY even when -Remove also fails; a -Remove failure is reported
    only when the block succeeded. A refused Build (no nonce) never
    enters the block and -Remove is never called on that path - Task 6's
    own internal cleanup already ran.

    A cleanup call that THROWS may not mask the main failure (r31). A
    `finally` that invokes the remover directly loses the saved main
    exception when the remover itself raises - on a launch failure or a
    timeout, not only a nonzero return - because that new exception takes
    over mid-unwind and the `raise main_exc` below never runs. So the
    remover is invoked inside its OWN try/except, INSIDE the finally: the
    finally block itself never raises, and the precedence below is
    applied explicitly instead of being decided by which exception
    happened to propagate.
    """
    build = build_lane_home(host, path, model, effort, lane_home, debate_id,
                             owner_pid, owner_ticks, timeout=build_timeout,
                             env=build_env)
    if build.returncode != 0 or build.nonce is None:
        raise BuildRefusal(build)
    custody = Custody(host, str(path), str(lane_home), debate_id, owner_pid,
                       owner_ticks, build.debate_home, build.nonce)
    main_exc = None
    remove = None
    remove_exc = None
    try:
        yield custody
    except BaseException as exc:  # re-raised unchanged below
        main_exc = exc
    finally:
        try:
            remove = remove_lane_home(host, path, lane_home, debate_id, owner_pid,
                                       owner_ticks, custody.nonce,
                                       timeout=remove_timeout, env=remove_env)
        except BaseException as exc:
            remove_exc = exc
    if main_exc is not None:
        raise main_exc
    if remove_exc is not None:
        raise remove_exc
    if remove.returncode != 0:
        raise RemoveFailure(remove)


# =======================================================================
# The SEED step: the sole direct-acquire exception to builder custody
# (packet line 159). No build has run yet, so there is no hold to
# borrow. Same precedence as custody_of: a failure inside the block stays
# primary over a release failure; a release failure is reported only
# after a successful block.
# =======================================================================
class SeedAcquireFailure(Exception):
    def __init__(self, result: LockResult):
        self.result = result
        super().__init__("seed acquire failed: exit %d: %s"
                          % (result.returncode, result.stderr.strip()))


class SeedReleaseFailure(Exception):
    def __init__(self, result: LockResult):
        self.result = result
        super().__init__("seed release failed: exit %d: %s"
                          % (result.returncode, result.stderr.strip()))


@contextmanager
def seed_hold(host, lane_home, debate_id, owner_pid, owner_ticks, timeout=60, env=None):
    """Acquire with `lane_home` as BOTH -LaneHome and -DebateHome (the seed
    step owns no separate debate home), yield the nonce, then always
    release in a finally.

    Same precedence as custody_of, and the same r31 fix: the release call
    runs inside its OWN try/except inside the finally, so a release that
    THROWS (a timeout, a launch failure - not only a nonzero return)
    cannot mask a failure raised inside the block."""
    acquire = lock_acquire(host, lane_home, debate_id, owner_pid, owner_ticks,
                            lane_home, timeout=timeout, env=env)
    if acquire.returncode != 0:
        raise SeedAcquireFailure(acquire)
    nonce = acquire.stdout.strip()
    main_exc = None
    release = None
    release_exc = None
    try:
        yield nonce
    except BaseException as exc:
        main_exc = exc
    finally:
        try:
            release = lock_release(host, lane_home, debate_id, owner_pid,
                                    owner_ticks, nonce, timeout=timeout, env=env)
        except BaseException as exc:
            release_exc = exc
    if main_exc is not None:
        raise main_exc
    if release_exc is not None:
        raise release_exc
    if release.returncode != 0:
        raise SeedReleaseFailure(release)


# =======================================================================
# File snapshot: SHA-256, byte length, mtime - returned ONLY after all
# three succeed. A failed measurement is never an equality-comparable
# sentinel (no "", None, or 0): the two component steps below each raise
# SnapshotMeasurementError, and measure_file_snapshot never catches that
# to substitute a placeholder value. Split into two separately-failing
# steps (a read+hash step, a stat step) precisely so a test can force
# EITHER one independently - the plan's own item 7 oracle needs a
# pre-command HASH failure and a post-command STAT failure as distinct
# cases.
# =======================================================================
class SnapshotMeasurementError(Exception):
    pass


@dataclass(frozen=True)
class FileSnapshot:
    sha256: str
    length: int
    mtime_ns: int


def _read_and_hash(path: Path):
    with open(path, "rb") as fh:
        data = fh.read()
    return hashlib.sha256(data).hexdigest(), len(data)


def _stat_mtime_ns(path: Path) -> int:
    return os.stat(path).st_mtime_ns


def measure_file_snapshot(path) -> FileSnapshot:
    path = Path(path)
    try:
        sha256, length = _read_and_hash(path)
    except OSError as exc:
        raise SnapshotMeasurementError(
            "hash measurement failed for %s: %s" % (path, exc)) from exc
    try:
        mtime_ns = _stat_mtime_ns(path)
    except OSError as exc:
        raise SnapshotMeasurementError(
            "stat measurement failed for %s: %s" % (path, exc)) from exc
    return FileSnapshot(sha256=sha256, length=length, mtime_ns=mtime_ns)


# =======================================================================
# The secret guard. One retained union of every NONEMPTY credential
# string value observed across every fixture home, scanned against both
# captured streams BEFORE any assertion or failure message can surface
# them. A match fails naming ONLY the field - never the value, never the
# stream.
# =======================================================================
class SecretGuardViolation(Exception):
    def __init__(self, field_name: str):
        self.field = field_name
        super().__init__(
            "secret guard: credential field '%s' matched in a captured stream"
            % field_name)


class SecretGuard:
    def __init__(self):
        # value -> field name. Never discard an old value: a rotated-away
        # token is still a secret that must not be printed, so entries
        # are only ever added, never replaced or removed.
        self._secrets: dict = {}

    def merge_values(self, fields: dict):
        for name, value in fields.items():
            if isinstance(value, str) and value != "" and value not in self._secrets:
                self._secrets[value] = name

    def merge_credential_dict(self, obj) -> bool:
        if not isinstance(obj, dict):
            return False
        self.merge_values({k: v for k, v in obj.items() if isinstance(v, str)})
        return True

    def merge_credential_text(self, raw_json_text: str) -> bool:
        try:
            obj = json.loads(raw_json_text)
        except ValueError:
            return False
        return self.merge_credential_dict(obj)

    def merge_credential_file(self, path) -> bool:
        try:
            raw = Path(path).read_text(encoding="utf-8")
        except OSError:
            return False
        return self.merge_credential_text(raw)

    def find_match(self, text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        for value, name in self._secrets.items():
            if value and value in text:
                return name
        return None

    def scan_or_raise(self, text: Optional[str]):
        field_name = self.find_match(text)
        if field_name is not None:
            raise SecretGuardViolation(field_name)


# =======================================================================
# Process capture. The helper OWNS capture so nothing downstream can
# render a stream before the guard runs: it invokes the command without
# raising the raw exception, and it sanitizes the timeout, launch-failure
# and credential-read-or-parse-fault paths too, since those are exactly
# the paths a test framework prints captured output on.
# =======================================================================
@dataclass
class CommandResult:
    returncode: int
    stdout: str
    stderr: str


class DispatchTimeout(Exception):
    def __init__(self):
        super().__init__("client dispatch timed out")


class DispatchLaunchFailure(Exception):
    def __init__(self):
        super().__init__("client dispatch failed: the process could not be launched")


class DispatchReadFailure(Exception):
    def __init__(self):
        super().__init__("post-command credential read-or-parse failed")


def dispatch_and_guard(args, guard: SecretGuard, timeout=60, cwd=None,
                        env=None, post_capture_merge=None) -> CommandResult:
    """Run `args`, then - while still inside this ONE call, before either
    stream can be returned or rendered - invoke `post_capture_merge()`
    (when given) and only THEN scan both captured streams. Frozen at r32:
    the post-capture merge is a CALLBACK, not a credential path, so each
    caller supplies exactly the merge behaviour its own fixture needs
    rather than this helper choosing a lenient default for everyone. A, B
    and C pass `strict_reread_and_merge_callback(guard, cred_path)` below
    - read, parse and merge must ALL succeed. Item 6's disposable homes
    each pass their own fixture-specific callback instead, carrying that
    fixture's EXPECTED state (valid / garbage / absent); a generic lenient
    mode is FORBIDDEN, because `merge_credential_file` returns the same
    `False` for an unreadable file and for malformed JSON, so a lenient
    mode would read an unmade measurement as an expected garbage fixture.

    The callback runs on the normal path AND the timeout path alike -
    SECURITY (r31): a token ISSUED BY the command being scanned is not in
    the guard's union until the callback has run, so scanning before it
    would let a value that command just emitted pass straight through
    into a pytest assertion or failure message. Capture, the callback, the
    stream scan, and the return are ONE indivisible operation - never
    split across two calls. Only AFTER the callback returns without
    raising may the guard scan and the streams be returned; if it raises,
    that exception propagates instead and NO captured stream is exposed.
    A launch failure (nonexistent executable) has no stream to leak, never
    calls the callback, and raises a fixed, sanitized message."""
    try:
        proc = subprocess.run(args, capture_output=True, text=True,
                               timeout=timeout, cwd=cwd, env=env)
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode(
            "utf-8", errors="replace")
        err = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode(
            "utf-8", errors="replace")
        if post_capture_merge is not None:
            post_capture_merge()
        guard.scan_or_raise(out)
        guard.scan_or_raise(err)
        raise DispatchTimeout() from None
    except OSError:
        raise DispatchLaunchFailure() from None
    if post_capture_merge is not None:
        post_capture_merge()
    guard.scan_or_raise(proc.stdout)
    guard.scan_or_raise(proc.stderr)
    return CommandResult(proc.returncode, proc.stdout, proc.stderr)


def reread_and_merge_credential(guard: SecretGuard, cred_path):
    """Re-read a credential file and merge its (nonempty, string) values
    into `guard` - the post-command merge step, run while the builder's
    hold is still in force. A read or parse fault raises a value-free
    DispatchReadFailure rather than surfacing whatever bytes were on
    disk."""
    try:
        raw = Path(cred_path).read_text(encoding="utf-8")
        obj = json.loads(raw)
    except (OSError, ValueError):
        raise DispatchReadFailure() from None
    if not guard.merge_credential_dict(obj):
        raise DispatchReadFailure()


def strict_reread_and_merge_callback(guard: SecretGuard, cred_path):
    """The strict `post_capture_merge` callback A, B and C pass for every
    operation, per the packet: read, parse and merge must ALL succeed, or
    DispatchReadFailure propagates and no stream is exposed. Returned as a
    zero-argument closure so it can be handed straight to
    dispatch_and_guard's `post_capture_merge` parameter."""
    def _callback():
        reread_and_merge_credential(guard, cred_path)
    return _callback


# =======================================================================
# The marker contract (packet "The marker contract, frozen"): a file
# named exactly MARKER_NAME in the home's root, ASCII, exactly one line
# of decimal digits.
# =======================================================================
def read_marker(home) -> Optional[str]:
    """Returns the marker's tick string, or None for a missing, empty, or
    non-matching marker - `None` here is a genuine "the home carries no
    usable marker" answer (a completed, negative measurement), not a
    failed one, so it is fine as a sentinel in this one case."""
    p = Path(home) / MARKER_NAME
    if not p.is_file():
        return None
    try:
        text = p.read_text(encoding="ascii")
    except (OSError, UnicodeDecodeError):
        return None
    lines = text.splitlines()
    if len(lines) != 1:
        return None
    line = lines[0]
    if not _MARKER_PATTERN.match(line):
        return None
    return line


# =======================================================================
# Physical inventory: does a SECOND, STANDALONE kimi-code.json exist
# anywhere under a debate home? Get-ChildItem -Recurse does not descend
# into a directory JUNCTION by default (measured live,
# test_kimi_lane_home.py's own junction oracle), so a standalone copy is
# the only way a second kimi-code.json shows up in this listing.
# =======================================================================
class JunctionCheckError(Exception):
    pass


def is_junction(host, path, timeout=30) -> bool:
    """True if `path` is a directory reparse point of type Junction,
    False if it exists and is an ordinary directory. Any other outcome
    (the query itself failing) is an unmade measurement and raises rather
    than reading as either answer - item 4b's deletion-fault case needs
    this to prove the debate home's `credentials` directory is still the
    REAL junction, not merely that something exists at that path."""
    escaped = str(path).replace("'", "''")
    proc = subprocess.run(
        [host, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command",
         "(Get-Item -LiteralPath '%s' -Force).LinkType" % escaped],
        capture_output=True, text=True, timeout=timeout, env=clean_env())
    if proc.returncode != 0:
        raise JunctionCheckError(
            "junction check failed for %s: %s" % (path, proc.stdout + proc.stderr))
    return proc.stdout.strip() == "Junction"


class PhysicalInventoryError(Exception):
    pass


def no_standalone_credential_file(host, debate_home, timeout=60) -> bool:
    """True if no file literally named kimi-code.json exists anywhere
    under `debate_home` other than by descending into a junction.

    `debate_home` is interpolated into a single-quoted PowerShell string
    literal, so every embedded ' must be doubled to '' first (a
    PowerShell single-quoted literal needs every ' doubled) - an
    unescaped apostrophe would truncate the literal early and corrupt the
    command, which is exactly what a debate-home path segment carrying
    BOTH an apostrophe and a space can trigger."""
    escaped = str(debate_home).replace("'", "''")
    proc = subprocess.run(
        [host, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass", "-Command",
         "Get-ChildItem -LiteralPath '%s' -Recurse -Force -File | "
         "Where-Object { $_.Name -eq 'kimi-code.json' } | "
         "ForEach-Object { $_.FullName }" % escaped],
        capture_output=True, text=True, timeout=timeout, env=clean_env())
    if proc.returncode != 0:
        raise PhysicalInventoryError(
            "junction inventory check failed: %s" % (proc.stdout + proc.stderr))
    return proc.stdout.strip() == ""


# =======================================================================
# Live-suite setup validation. FAILS (raises), never skips: "an unmade,
# failed, or unreadable measurement is never a clean one... a live gate
# whose setup fails is a FAILED gate, never a skipped branch."
# =======================================================================
class LiveSetupError(Exception):
    pass


@dataclass
class LiveHomes:
    a: Path
    b: Path
    c: Path
    marker_a: str
    marker_b: str


def _physically_resolve(label: str, home: Path) -> str:
    """Full resolution for identity comparison: the real Windows path
    with every reparse point (junction) followed, normalized so a
    case-only difference and a junction alias both collapse to the SAME
    string. `strict=True` because an unresolvable path is a measurement
    that cannot be made, which the r31 SAFETY amendment treats as a
    failure, never a pass."""
    try:
        resolved = Path(home).resolve(strict=True)
    except OSError as exc:
        raise LiveSetupError(
            "lane home %s (%s) could not be physically resolved: %s"
            % (label, home, exc)) from exc
    return os.path.normcase(str(resolved))


def _validate_live_home_safety(homes: dict) -> None:
    """The live homes are SAFETY-CHECKED before any seed or mutation,
    frozen at r31. `homes` maps "A"/"B"/"C" to a Path already confirmed
    to be a directory. FAIL unless every measurement below both succeeds
    and passes - checking only "is a directory with an ok credential" let
    the suite's own deliberate expiry land on the user's real home if a
    variable were mistyped, which is the exact defect this plan exists to
    remove, reintroduced through the fixture routing."""
    physical = {label: _physically_resolve(label, home) for label, home in homes.items()}

    seen = {}
    for label in ("A", "B", "C"):
        p = physical[label]
        if p in seen:
            raise LiveSetupError(
                "lane homes %s and %s resolve to the same physical "
                "directory; the three lane homes must be pairwise "
                "distinct after full resolution" % (seen[p], label))
        seen[p] = label

    profile_env = os.environ.get("USERPROFILE")
    if not profile_env:
        raise LiveSetupError(
            "USERPROFILE is not set; cannot safety-check the live lane "
            "homes against the real profile")
    try:
        real_profile_path = Path(profile_env).resolve(strict=True)
    except OSError as exc:
        raise LiveSetupError(
            "the real USERPROFILE (%s) could not be physically resolved: %s"
            % (profile_env, exc)) from exc
    real_profile = os.path.normcase(str(real_profile_path))
    # .kimi-code need NOT exist yet on an otherwise-clean machine - a
    # lane home whose OWN existence was already confirmed (is_dir, above)
    # cannot physically sit beneath a directory that does not exist at
    # all, so this stays a plain textual join off the (strictly resolved)
    # profile root rather than requiring .kimi-code's own strict
    # resolution, which would fail the measurement on every machine that
    # has not yet provisioned it - an unmade measurement the safety
    # property does not actually depend on here.
    real_kimi_code = os.path.normcase(str(real_profile_path / ".kimi-code"))
    real_kimi_code_prefix = real_kimi_code.rstrip("\\") + "\\"

    for label in ("A", "B", "C"):
        p = physical[label]
        drive, rest = os.path.splitdrive(p)
        if drive and rest in ("", "\\"):
            raise LiveSetupError(
                "lane home %s resolves to a drive root; refusing" % label)
        if p == real_profile:
            raise LiveSetupError(
                "lane home %s resolves to the real USERPROFILE; refusing" % label)
        if p == real_kimi_code or p.startswith(real_kimi_code_prefix):
            raise LiveSetupError(
                "lane home %s resolves at or beneath the real "
                "USERPROFILE\\.kimi-code; refusing" % label)


def resolve_and_validate_live_homes(host, timeout=60) -> LiveHomes:
    missing = [name for name in (ENV_HOME_A, ENV_HOME_B, ENV_HOME_C)
               if not os.environ.get(name)]
    if missing:
        raise LiveSetupError(
            "missing environment variable(s): %s; create the missing lane "
            "home(s) with tools/new-kimi-lane-login.ps1 per the manual "
            "setup sequence before running the live suite"
            % ", ".join(missing))

    homes = {}
    for label, env_name in (("A", ENV_HOME_A), ("B", ENV_HOME_B), ("C", ENV_HOME_C)):
        home = Path(os.environ[env_name])
        if not home.is_dir():
            raise LiveSetupError(
                "lane home %s (%s) is not a directory; run "
                "tools/new-kimi-lane-login.ps1 -LaneHome '%s' ..." % (label, home, home))
        homes[label] = home

    _validate_live_home_safety(homes)

    resolved = {}
    for label, home in homes.items():
        cred_path = home / "credentials" / "kimi-code.json"
        verdict = validate_credential(host, cred_path, timeout=timeout)
        if not verdict.ok or verdict.status != "ok":
            raise LiveSetupError(
                "lane home %s (%s) lacks a structurally ok credential "
                "(validator ok=%s status=%s); run "
                "tools/new-kimi-lane-login.ps1 -LaneHome '%s' ..."
                % (label, home, verdict.ok, verdict.status, home))
        resolved[label] = home

    marker_a = read_marker(resolved["A"])
    marker_b = read_marker(resolved["B"])
    if marker_a is None:
        raise LiveSetupError(
            "lane home A (%s) has a missing, empty, or malformed marker "
            "(%s)" % (resolved["A"], MARKER_NAME))
    if marker_b is None:
        raise LiveSetupError(
            "lane home B (%s) has a missing, empty, or malformed marker "
            "(%s)" % (resolved["B"], MARKER_NAME))
    if not (int(marker_a) < int(marker_b)):
        raise LiveSetupError(
            "lane home A's marker (%s) must be strictly less than lane "
            "home B's (%s)" % (marker_a, marker_b))

    return LiveHomes(a=resolved["A"], b=resolved["B"], c=resolved["C"],
                      marker_a=marker_a, marker_b=marker_b)


# =======================================================================
# Output normalization, frozen (packet "Live command oracles"): replace
# the resolved fixture root with the literal <fixture-root>,
# case-insensitively; normalize CRLF to LF; trim ONE terminal newline.
# =======================================================================
def normalize_probe_output(text: str, fixture_root: str) -> str:
    pattern = re.compile(re.escape(str(fixture_root)), re.IGNORECASE)
    replaced = pattern.sub("<fixture-root>", text)
    replaced = replaced.replace("\r\n", "\n")
    if replaced.endswith("\n"):
        replaced = replaced[:-1]
    return replaced


# =======================================================================
# The probe record: MEASURED ONCE, then pinned, frozen at r31. "The pin
# is a LOCKING ASSERTION, not documentation" - an ordinary run READS the
# committed record and compares; it never creates it and never rewrites
# it. Only an explicit PARALLAX_LANE_PROBE_RECORD_REFRESH=1 run measures
# and (on success) atomically replaces it. Callers pass an already-
# NORMALIZED measure_fn - normalization needs a fixture root this module
# does not have, so that step stays the caller's job.
# =======================================================================
REFRESH_ENV = "PARALLAX_LANE_PROBE_RECORD_REFRESH"


class ProbeRecordError(Exception):
    """The committed record is missing, unreadable, or malformed."""


class ProbeRecordUnstable(Exception):
    """Two measurements of the same case did not produce identical
    (exit, stdout, stderr) tuples."""


class ProbeRecordNotFailed(Exception):
    """The measured case exited 0; the absolute-key case is required to
    fail nonzero, independently of the stability check."""


class ProbeRecordMismatch(Exception):
    """The current normalized stderr does not equal the committed pinned
    stderr."""


class ProbeRecordRefreshRefused(Exception):
    """PARALLAX_LANE_PROBE_RECORD_REFRESH was set to something other than
    the exact opt-in value '1'."""


def probe_record_refresh_requested() -> bool:
    """The exact opt-in value is '1'; any other NONEMPTY value REFUSES
    rather than being treated as truthy. Unset or empty means "ordinary
    run" (False)."""
    value = os.environ.get(REFRESH_ENV)
    if not value:
        return False
    if value != "1":
        raise ProbeRecordRefreshRefused(
            "%s must be exactly '1'; got %r" % (REFRESH_ENV, value))
    return True


@dataclass(frozen=True)
class ProbeMeasurement:
    exit_code: int
    stdout: str
    stderr: str


_RECORD_EXIT_RE = re.compile(r"- Exit code: `(-?[0-9]+)`")
_RECORD_STDOUT_RE = re.compile(r"## Normalized stdout\n\n```\n(.*?)\n```", re.S)
_RECORD_STDERR_RE = re.compile(
    r"## Normalized stderr \(the pinned value\)\n\n```\n(.*?)\n```", re.S)


def parse_probe_record_text(text: str) -> ProbeMeasurement:
    exit_match = _RECORD_EXIT_RE.search(text)
    stdout_match = _RECORD_STDOUT_RE.search(text)
    stderr_match = _RECORD_STDERR_RE.search(text)
    if not (exit_match and stdout_match and stderr_match):
        raise ProbeRecordError(
            "probe record is malformed: could not locate the exit code, "
            "normalized stdout, or normalized stderr section")
    return ProbeMeasurement(int(exit_match.group(1)), stdout_match.group(1),
                             stderr_match.group(1))


def read_probe_record(path) -> ProbeMeasurement:
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise ProbeRecordError(
            "probe record %s is missing or unreadable: %s" % (path, exc)) from exc
    return parse_probe_record_text(text)


def render_probe_record(measured_at: str, measurement: ProbeMeasurement) -> str:
    return (
        "# Live probe record: absolute oauth.key rejection\n\n"
        "Measured %s against the real kimi-code client on this machine "
        "(Task 7, 2026-08-01 lane-credential-and-lock plan, item 1 / "
        "measurement 5).\n\n"
        "- Exit code: `%d`\n"
        "- Normalization: the resolved fixture root replaced with "
        "`<fixture-root>` (case-insensitive), CRLF normalized to LF, "
        "one terminal newline trimmed.\n\n"
        "## Normalized stdout\n\n```\n%s\n```\n\n"
        "## Normalized stderr (the pinned value)\n\n```\n%s\n```\n"
        % (measured_at, measurement.exit_code, measurement.stdout, measurement.stderr))


def write_probe_record_atomic(path, measurement: ProbeMeasurement, measured_at: str) -> None:
    """Atomically CREATE or REPLACE the record - never a partial write a
    failed run could leave behind."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = render_probe_record(measured_at, measurement)
    tmp = path.with_name(path.name + ".tmp-%s" % uuid.uuid4().hex)
    tmp.write_text(text, encoding="utf-8")
    os.replace(str(tmp), str(path))


def run_probe_record_gate(record_path, measure_fn, guard: SecretGuard,
                           refresh: bool = False) -> ProbeMeasurement:
    """The pin's locking-assertion protocol, frozen at r31.

    `measure_fn()` returns ONE already-normalized ProbeMeasurement per
    call. Every measurement's stdout/stderr is scanned by `guard` before
    it can be compared, written, or surfaced in any exception - the same
    secret-guard discipline that governs every other live command.

    Ordinary run (refresh=False): a missing/unreadable/malformed record
    raises ProbeRecordError BEFORE any measurement is taken, and writes
    nothing. Otherwise measures TWICE, requires the two full tuples to be
    IDENTICAL (raises ProbeRecordUnstable if not), requires nonzero exit
    INDEPENDENTLY of that stability check (raises ProbeRecordNotFailed),
    requires the current normalized stderr to equal the committed pinned
    stderr (raises ProbeRecordMismatch), and returns without writing -
    the record stays byte-identical because this branch never writes.

    Explicit refresh (refresh=True): measures twice, requires the same
    full-tuple stability and nonzero exit as above, then atomically
    creates or replaces the record. A failure or an unstable measurement
    writes NOTHING - the raise happens before any write is attempted.
    """
    committed = None
    if not refresh:
        committed = read_probe_record(record_path)

    m1 = measure_fn()
    guard.scan_or_raise(m1.stdout)
    guard.scan_or_raise(m1.stderr)
    m2 = measure_fn()
    guard.scan_or_raise(m2.stdout)
    guard.scan_or_raise(m2.stderr)

    if m1 != m2:
        raise ProbeRecordUnstable(
            "the two measurements are not identical: %r != %r" % (m1, m2))
    if m1.exit_code == 0:
        raise ProbeRecordNotFailed(
            "the measured case exited 0; it is required to fail nonzero")

    if not refresh:
        if m1.stderr != committed.stderr:
            raise ProbeRecordMismatch(
                "the current normalized stderr does not match the "
                "committed pinned record")
        return m1

    write_probe_record_atomic(
        record_path, m1, measured_at=datetime.now(timezone.utc).isoformat())
    return m1
