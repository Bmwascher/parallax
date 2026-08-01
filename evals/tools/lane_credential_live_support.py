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
    return _read_model_notes_field("Canonical backup model id")


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


def validate_credential(host, path, timeout=60, env=None) -> ValidatorResult:
    try:
        proc = subprocess.run(
            [host, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
             "-File", str(CREDENTIAL_VALIDATOR), "-Path", str(path)],
            capture_output=True, text=True, timeout=timeout,
            env=(env if env is not None else clean_env()))
    except (OSError, subprocess.TimeoutExpired):
        return ValidatorResult(ok=False)
    if proc.returncode != 0:
        return ValidatorResult(ok=False)
    if proc.stderr != "":
        return ValidatorResult(ok=False)
    lines = [ln for ln in proc.stdout.splitlines() if ln.strip() != ""]
    if len(lines) != 1:
        return ValidatorResult(ok=False)
    try:
        obj = json.loads(lines[0])
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


def build_lane_home(host, path, model, effort, lane_home, debate_id,
                     owner_pid, owner_ticks, timeout=180, env=None) -> BuildResult:
    args = [host, "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
            "-File", str(BUILDER), "-Path", str(path), "-Model", model,
            "-Effort", effort, "-LaneHome", str(lane_home),
            "-DebateId", debate_id, "-OwnerPid", str(owner_pid),
            "-OwnerStartTicksUtc", str(owner_ticks)]
    proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout,
                           env=(env if env is not None else clean_env()))
    debate_home = nonce = None
    if proc.returncode == 0:
        lines = [ln for ln in proc.stdout.splitlines() if ln.strip() != ""]
        if len(lines) == 1:
            try:
                obj = json.loads(lines[0])
            except ValueError:
                obj = None
            if isinstance(obj, dict) and set(obj.keys()) == {"debateHome", "nonce"}:
                debate_home, nonce = obj["debateHome"], obj["nonce"]
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
    try:
        yield custody
    except BaseException as exc:  # re-raised unchanged below
        main_exc = exc
    finally:
        remove = remove_lane_home(host, path, lane_home, debate_id, owner_pid,
                                   owner_ticks, custody.nonce,
                                   timeout=remove_timeout, env=remove_env)
    if main_exc is not None:
        raise main_exc
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
    release in a finally."""
    acquire = lock_acquire(host, lane_home, debate_id, owner_pid, owner_ticks,
                            lane_home, timeout=timeout, env=env)
    if acquire.returncode != 0:
        raise SeedAcquireFailure(acquire)
    nonce = acquire.stdout.strip()
    main_exc = None
    release = None
    try:
        yield nonce
    except BaseException as exc:
        main_exc = exc
    finally:
        release = lock_release(host, lane_home, debate_id, owner_pid,
                                owner_ticks, nonce, timeout=timeout, env=env)
    if main_exc is not None:
        raise main_exc
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
                        env=None) -> CommandResult:
    """Run `args`, scan BOTH captured streams against `guard` before
    returning or raising, and never let a raw stream escape through an
    exception message. A timeout still gets its best-effort partial
    output scanned (Python's subprocess.TimeoutExpired carries whatever
    was already captured) before the sanitized DispatchTimeout is raised;
    a launch failure (nonexistent executable) has no stream to leak and
    raises a fixed, sanitized message."""
    try:
        proc = subprocess.run(args, capture_output=True, text=True,
                               timeout=timeout, cwd=cwd, env=env)
    except subprocess.TimeoutExpired as exc:
        out = exc.stdout if isinstance(exc.stdout, str) else (exc.stdout or b"").decode(
            "utf-8", errors="replace")
        err = exc.stderr if isinstance(exc.stderr, str) else (exc.stderr or b"").decode(
            "utf-8", errors="replace")
        guard.scan_or_raise(out)
        guard.scan_or_raise(err)
        raise DispatchTimeout() from None
    except OSError:
        raise DispatchLaunchFailure() from None
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


def resolve_and_validate_live_homes(host, timeout=60) -> LiveHomes:
    missing = [name for name in (ENV_HOME_A, ENV_HOME_B, ENV_HOME_C)
               if not os.environ.get(name)]
    if missing:
        raise LiveSetupError(
            "missing environment variable(s): %s; create the missing lane "
            "home(s) with tools/new-kimi-lane-login.ps1 per the manual "
            "setup sequence before running the live suite"
            % ", ".join(missing))

    resolved = {}
    for label, env_name in (("A", ENV_HOME_A), ("B", ENV_HOME_B), ("C", ENV_HOME_C)):
        home = Path(os.environ[env_name])
        if not home.is_dir():
            raise LiveSetupError(
                "lane home %s (%s) is not a directory; run "
                "tools/new-kimi-lane-login.ps1 -LaneHome '%s' ..." % (label, home, home))
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
