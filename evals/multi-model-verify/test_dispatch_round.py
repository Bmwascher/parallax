"""Contract pins for tools/dispatch-round.ps1 -Prepare (Task 2, 2026-08-31
completion-coupled-dispatch plan).

-Launch and -Poll are gone - see test_launch_and_poll_are_gone. This
module drives the REAL dispatch-round.ps1 and the REAL
tools/new-review-mirror.ps1 against a stub body.ps1 (never the real
codex/kimi transports). WINDOWS ONLY, whole module: the mirror tool
resolves Windows profile variables and both tools target the Windows
PowerShell hosting model. PARALLAX_PS_HOST selects which host runs these
tests, same pattern as test_review_mirror.py - a selector that merely
finds A host would happily collect them on a non-Windows CI box too. A
green suite on one host proves ONE interpreter.
"""
import concurrent.futures
import hashlib
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "tools" / "dispatch-round.ps1"
MIRROR_TOOL = REPO / "tools" / "new-review-mirror.ps1"

POWERSHELL = (os.environ.get("PARALLAX_PS_HOST")
              or shutil.which("powershell") or shutil.which("pwsh"))

pytestmark = pytest.mark.skipif(
    os.name != "nt" or POWERSHELL is None,
    reason="dispatch-round.ps1 is a Windows tool: it needs a "
           "PowerShell host and the mirror-identity platform it targets")


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------
def run_tool(args, env=None, timeout=30):
    full_env = dict(os.environ)
    if env:
        full_env.update(env)
    cmd = [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(SCRIPT)] + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, env=full_env, timeout=timeout)


def _force_remove(func, path, _exc):
    """git marks its object files read-only, so a plain rmtree of a
    mirror raises PermissionError on Windows before it reaches the
    condition under test. Same fix as test_review_mirror.py's own
    _force_remove."""
    os.chmod(path, 0o700)
    func(path)


def run_wrapper(wrapper_path, env=None, timeout=60):
    """Run a prepared wrapper.ps1 to completion and return its result -
    the REAL end-to-end run this task exists to prove, not a simulation
    of it."""
    full_env = dict(os.environ)
    if env:
        full_env.update(env)
    cmd = [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(wrapper_path)]
    return subprocess.run(cmd, capture_output=True, text=True, env=full_env, timeout=timeout)


def start_wrapper(wrapper_path, env=None):
    """Start a prepared wrapper.ps1 WITHOUT waiting for it, so a test can
    observe an in-flight run (the hold-after-exit-write seam) and kill
    it deliberately."""
    full_env = dict(os.environ)
    if env:
        full_env.update(env)
    cmd = [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(wrapper_path)]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, env=full_env)


def run_wrapper_concurrently(wrapper_a, wrapper_b, timeout=60):
    """Start two wrapper runs (the same wrapper.ps1, or two different
    ones) at the same time and return both results, so a race on the
    create-new reservation is actually exercised rather than merely
    argued about."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        fut_a = pool.submit(run_wrapper, wrapper_a, None, timeout)
        fut_b = pool.submit(run_wrapper, wrapper_b, None, timeout)
        return fut_a.result(), fut_b.result()


def wait_for(path, timeout=30):
    """Poll for a file's existence, bounded, rather than sleeping a fixed
    guess - the interval this test seam guarantees is deterministic, but
    process start-up latency before it is not."""
    deadline = time.time() + timeout
    while time.time() < deadline:
        if Path(path).exists():
            return
        time.sleep(0.05)
    raise AssertionError("timed out waiting for " + str(path))


def kill_tree(pid):
    """Kill a process and any children it may have started (the wrapper
    started body.ps1 as a child), the way a harness kill would."""
    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"],
                    capture_output=True, text=True)


def snapshot(dispatch_dir):
    """A comparable snapshot of every file's bytes under a dispatch
    directory, so a test can assert a second run wrote NOTHING rather
    than merely that it exited nonzero."""
    d = Path(dispatch_dir)
    return {p.relative_to(d).as_posix(): p.read_bytes()
            for p in sorted(d.rglob("*")) if p.is_file()}


def _read_text(path):
    """Decode a file PowerShell's own `>` / `2>` redirection wrote,
    whose encoding is HOST-dependent: Windows PowerShell 5.1 defaults
    that redirection to UTF-16LE with a BOM, PowerShell 7 to UTF-8
    without one - measured directly against mirror.verify, body.out and
    body.err on both hosts. Files this tool writes itself through
    [System.IO.File]::WriteAllText carry no such BOM and read correctly
    either way, so this helper is only needed for the three files above."""
    data = Path(path).read_bytes()
    if data[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return data.decode("utf-16")
    if data[:3] == b"\xef\xbb\xbf":
        return data.decode("utf-8-sig")
    return data.decode("utf-8", errors="replace")


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, check=True).stdout


# The exact skip line -SkipProbe prints. -Prepare's own tests need a REAL
# mirror, built by the real tool, because -Prepare now refuses anything
# that does not verify as one - a bare mkdir cannot be used. A build run
# with -SkipProbe exits 1, not 0 (the exit code reports dispatch-
# readiness, not construction), and the mirror IS built - see
# test_review_mirror.py's assert_built, which this follows rather than
# inventing a second reading of the same tool.
SKIP_BLOCK = "BLOCKED: no client measurement was made (-SkipProbe)"


def record_field(stdout, name):
    """One scalar field of the mirror's construction record, or None -
    the same reading test_review_mirror.py's build_and_read uses. The
    identity values must be parsed out of the printed record, never
    guessed."""
    for line in stdout.splitlines():
        if line.startswith(name + ": "):
            return line[len(name) + 2:].strip()
    return None


class RealMirror(object):
    def __init__(self, path, source, source_head, mirror_head,
                 source_status_sha256, mirror_state_sha256):
        self.path = path
        self.source = source
        self.source_head = source_head
        self.mirror_head = mirror_head
        self.source_status_sha256 = source_status_sha256
        self.mirror_state_sha256 = mirror_state_sha256


def build_real_mirror(tmp_path):
    """Build a real mirror with the real tool and return its path, its
    source, and its five identity values, read out of the printed
    record."""
    source = tmp_path / "mirror-src"
    source.mkdir()
    git(tmp_path, "init", "-q", str(source))
    (source / "only.txt").write_text("tracked\n")
    git(source, "add", "only.txt")
    git(source, "-c", "user.email=t@t", "-c", "user.name=t",
        "commit", "-q", "-m", "base")

    mirror_path = tmp_path / "real-mirror"
    proc = subprocess.run(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(MIRROR_TOOL),
         "-RepoRoot", str(source), "-MirrorPath", str(mirror_path), "-SkipProbe"],
        capture_output=True, text=True)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert SKIP_BLOCK in proc.stdout, proc.stdout + proc.stderr

    return RealMirror(
        path=Path(record_field(proc.stdout, "mirror")),
        source=source,
        source_head=record_field(proc.stdout, "source_head"),
        mirror_head=record_field(proc.stdout, "mirror_head"),
        source_status_sha256=record_field(proc.stdout, "source_status_sha256"),
        mirror_state_sha256=record_field(proc.stdout, "mirror_state_sha256"))


DEFAULT_ROUND = "Sol R1"


def _prepare_args(mirror, dispatch_dir, receipt_path, body, prior_state,
                   round_label=DEFAULT_ROUND, host="powershell", json_mode=False,
                   working_directory=None, mirror_head=None):
    """working_directory overrides -WorkingDirectory alone (leaving
    -ExpectedMirrorPath at the mirror's real path, so a mismatch is
    attributable to the working directory); mirror_head overrides
    -MirrorHead alone. Both default to the mirror's own real values, so a
    call with neither is unchanged from before."""
    wd = working_directory if working_directory is not None else mirror.path
    mh = mirror_head if mirror_head is not None else mirror.mirror_head
    args = [
        "-Prepare", "-DispatchDir", str(dispatch_dir), "-WrapperBody", str(body),
        "-ReceiptPath", str(receipt_path), "-Round", round_label,
        "-WorkingDirectory", str(wd), "-RepoRoot", str(mirror.source),
        "-SourceHead", mirror.source_head, "-MirrorHead", mh,
        "-SourceStatusSha256", mirror.source_status_sha256,
        "-MirrorStateSha256", mirror.mirror_state_sha256,
        "-ExpectedMirrorPath", str(mirror.path),
        "-DispatchHost", host,
        "-PriorStateFile", str(prior_state), "-NoWorkdirEvidence"]
    if json_mode:
        args.append("-Json")
    return args


def _default_body_and_prior(tmp_path):
    body = tmp_path / "body.ps1"
    body.write_text("$code = 0\nexit $code\n", encoding="ascii")
    prior = tmp_path / "prior.json"
    prior.write_text('{"kind":"fresh","knownRollouts":[]}', encoding="ascii")
    return body, prior


def prepare_default(tmp_path, dispatch_dir=None, receipt=None, host="powershell",
                     json_mode=False, round_label=DEFAULT_ROUND,
                     working_directory=None, mirror=None, mirror_head=None):
    """A full, otherwise-valid -Prepare invocation (real mirror, real
    prior-state file, real body), with exactly the field(s) under test
    overridden - so a block is attributable to that field alone. Pass an
    already-built `mirror` to reuse one instead of building a fresh one
    (needed when a test wants a REAL, otherwise-valid mirror and then
    overrides just one of its recorded values)."""
    mirror = mirror if mirror is not None else build_real_mirror(tmp_path)
    body, prior = _default_body_and_prior(tmp_path)
    d = dispatch_dir if dispatch_dir is not None else tmp_path / "dispatch"
    r = receipt if receipt is not None else tmp_path / "receipt.json"
    args = _prepare_args(mirror, d, r, body, prior, round_label=round_label,
                          host=host, json_mode=json_mode,
                          working_directory=working_directory,
                          mirror_head=mirror_head)
    return run_tool(args)


class Prepared(object):
    def __init__(self, dispatch_dir, receipt_path, result, wrapper, working_directory):
        self.dispatch_dir = dispatch_dir
        self.receipt_path = receipt_path
        self.receipt = receipt_path
        self.result = result
        self.wrapper = wrapper
        self.working_directory = working_directory


class RunResult(object):
    """The result of running a prepared wrapper to completion, plus the
    dispatch-directory context a test needs to inspect what it left
    behind."""
    def __init__(self, returncode, stdout, stderr, dispatch_dir, wrapper,
                 working_directory):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        self.dispatch_dir = dispatch_dir
        self.wrapper = wrapper
        self.working_directory = working_directory


def prepare(tmp_path, body, round_label=DEFAULT_ROUND, working_directory=None,
            mirror=None, mirror_head=None):
    """A -Prepare call expected to SUCCEED, returning the dispatch
    directory it built so a test can read body.ps1 / wrapper.ps1 back out
    of it. `body` may contain the literal placeholder `{workingDirectory}`,
    which is interpolated to the REAL working directory (forward-slashed,
    so it is safe inside a double-quoted PowerShell string) before the
    body is written - the placeholder itself is never written to disk."""
    mirror = mirror if mirror is not None else build_real_mirror(tmp_path)
    wd = working_directory if working_directory is not None else mirror.path
    body_text = body.replace("{workingDirectory}", str(wd).replace("\\", "/"))
    body_path = tmp_path / "body.ps1"
    body_path.write_text(body_text, encoding="ascii")
    prior = tmp_path / "prior.json"
    prior.write_text('{"kind":"fresh","knownRollouts":[]}', encoding="ascii")
    dispatch_dir = tmp_path / "dispatch"
    receipt_path = tmp_path / "receipt.json"
    args = _prepare_args(mirror, dispatch_dir, receipt_path, body_path, prior,
                          round_label=round_label, json_mode=False,
                          working_directory=wd, mirror_head=mirror_head)
    result = run_tool(args)
    assert result.returncode == 0, (result.stdout, result.stderr)
    wrapper_path = dispatch_dir / "wrapper.ps1"
    receipt_sha256 = hashlib.sha256(receipt_path.read_bytes()).hexdigest()
    _write_meta(tmp_path, receipt_path, round_label, receipt_sha256, "0" * 32)
    return Prepared(dispatch_dir, receipt_path, result, wrapper_path, wd)


def prepare_and_run(tmp_path, body, round_label=DEFAULT_ROUND, env=None, timeout=60):
    """prepare() a wrapper and immediately run it to completion - the
    convenience most Task 4 tests want, since what they are checking is
    the wrapper's OWN exit code and output, not -Prepare's."""
    p = prepare(tmp_path, body, round_label=round_label)
    r = run_wrapper(p.wrapper, env=env, timeout=timeout)
    return RunResult(r.returncode, r.stdout, r.stderr, p.dispatch_dir, p.wrapper,
                      p.working_directory)


# A lane body that succeeds cleanly: writes a reply and exits 0.
OK_BODY = (
    '[System.IO.File]::WriteAllText("$PSScriptRoot/reply", "a verdict")\n'
    'exit 0\n'
)

# The same, but slow enough that two concurrent wrapper runs are still
# both mid-flight when the second one attempts its own claim - widening
# the race window test_two_concurrent_first_runs_leave_exactly_one_winner
# depends on, rather than relying on the two OS process launches to
# happen to overlap on their own.
SLOW_OK_BODY = (
    'Start-Sleep -Milliseconds 500\n'
    '[System.IO.File]::WriteAllText("$PSScriptRoot/reply", "a verdict")\n'
    'exit 0\n'
)


def killed_after_publish(tmp_path, monkeypatch):
    """Prepare a wrapper with the hold-after-exit-write seam armed, run
    it until the seam confirms `exit` and `reply` are published and the
    reservation is consumed, then kill the whole process tree - the
    interval Option C's post-hoc classifier would have read as success.
    Returns the Prepared directory for the caller to inspect afterward."""
    barrier = tmp_path / "hold"
    monkeypatch.setenv("PARALLAX_DISPATCH_HOLD_AFTER_EXIT_WRITE", str(barrier))
    p = prepare(tmp_path, body=OK_BODY)
    proc = start_wrapper(p.wrapper)
    wait_for(Path(str(barrier) + ".started"))
    kill_tree(proc.pid)
    proc.wait()
    return p


def break_second_mirror_call_only(wrapper_path):
    """Break only the SECOND of the wrapper's two identical `@mirrorArgs`
    splats, by index - the wrapper names the verifier tool twice and
    nothing in its text distinguishes the two call sites, so a helper
    that broke both would kill the wrapper at the FIRST verification,
    which the defect this test guards against did too."""
    text = Path(wrapper_path).read_text(encoding="ascii")
    marker = "@mirrorArgs"
    first = text.find(marker)
    assert first != -1, "expected an @mirrorArgs splat in the wrapper"
    second = text.find(marker, first + len(marker))
    assert second != -1, "expected a SECOND @mirrorArgs splat in the wrapper"
    broken = text[:second] + "@doesNotExistSplat" + text[second + len(marker):]
    Path(wrapper_path).write_text(broken, encoding="ascii")


# ---------------------------------------------------------------------
# -Prepare
# ---------------------------------------------------------------------
def test_prepare_writes_the_whole_receipt_last(tmp_path):
    d = tmp_path / "d"
    receipt = tmp_path / "r.json"
    body = tmp_path / "body.ps1"
    body.write_text("$code = 0\n", encoding="ascii")
    prior = tmp_path / "prior.json"
    prior.write_text('{"kind":"fresh","knownRollouts":[]}', encoding="ascii")
    # A REAL mirror, built by the real tool, because -Prepare now refuses
    # anything that does not verify as one. A bare mkdir cannot be used.
    mirror = build_real_mirror(tmp_path)
    out = run_tool([
        "-Prepare", "-DispatchDir", str(d), "-WrapperBody", str(body),
        "-ReceiptPath", str(receipt), "-Round", "Sol R1",
        "-WorkingDirectory", str(mirror.path), "-RepoRoot", str(mirror.source),
        "-SourceHead", mirror.source_head, "-MirrorHead", mirror.mirror_head,
        "-SourceStatusSha256", mirror.source_status_sha256,
        "-MirrorStateSha256", mirror.mirror_state_sha256,
        "-ExpectedMirrorPath", str(mirror.path),
        "-DispatchHost", "powershell",
        "-PriorStateFile", str(prior), "-NoWorkdirEvidence", "-Json"])
    assert out.returncode == 0, out.stdout
    got = json.loads(receipt.read_text(encoding="utf-8"))
    assert set(got) == {
        "dispatchDir", "token", "round", "workingDirectory",
        "dispatchHost", "priorStateSha256", "workdirEvidence",
        "repoRoot", "sourceHead", "mirrorHead", "sourceStatusSha256",
        "mirrorStateSha256", "expectedMirrorPath", "schema"}
    assert got["schema"] == 2
    assert got["round"] == "Sol R1"
    assert got["workdirEvidence"] == "none"
    assert len(got["priorStateSha256"]) == 64


def test_prepare_refuses_an_existing_dispatch_directory(tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    out = prepare_default(tmp_path, dispatch_dir=d)
    assert out.returncode == 1
    assert "dispatch directory already exists" in out.stdout


def test_prepare_installs_the_lane_body_as_its_own_script(tmp_path):
    p = prepare(tmp_path, body="$code = 0\nexit $code\n")
    assert (p.dispatch_dir / "body.ps1").read_text() == "$code = 0\nexit $code\n"
    wrapper = (p.dispatch_dir / "wrapper.ps1").read_text()
    assert "body.ps1" in wrapper
    assert "$code = 0" not in wrapper  # the body is NOT inlined


def test_prepare_refuses_a_receipt_inside_the_dispatch_directory(tmp_path):
    d = tmp_path / "d"
    out = prepare_default(tmp_path, dispatch_dir=d, receipt=d / "r.json")
    assert out.returncode == 1
    assert not d.exists()


def test_prepare_emits_a_command_naming_the_resolved_host(tmp_path):
    out = prepare_default(tmp_path, json_mode=True)
    got = json.loads(out.stdout)
    assert got["command"].endswith(
        "-NoProfile -NonInteractive -File \"%s\"" % got["wrapper"])
    assert got["command"].lower().startswith('"')
    assert got["taskName"] == "Sol R1 debate round"


def test_prepare_refuses_an_unresolvable_host(tmp_path):
    out = prepare_default(tmp_path, host="notashell")
    assert out.returncode == 2


def test_prepare_refuses_a_working_directory_that_is_not_the_verified_mirror(tmp_path):
    """Step 1a's whole reason for existing, which the task's own test
    list did not lock.

    Without it the tool takes the caller's word for the directory AND
    the evidence value, so a caller who supplies the LIVE REPOSITORY for
    both gets a wrapper that deliberately relocates there, a client
    whose own report agrees with the wrong value, and a clean result.
    Every check downstream is self-consistent and every one is wrong.
    That is invariant B4's "detect a wrong initial value" and B1's
    requirement that entering the live repository be impossible to get
    wrong silently.

    Measured 2026-08-31: the guard does refuse. A guard with no test is
    one refactor away from being deleted by someone who cannot see what
    it was for.
    """
    mirror = build_real_mirror(tmp_path)
    body, prior = _default_body_and_prior(tmp_path)
    receipt = tmp_path / "receipt.json"
    args = _prepare_args(mirror, tmp_path / "dispatch", receipt, body, prior)
    # Every other value stays honest, so the refusal is attributable to
    # the directory alone.
    for i, a in enumerate(args):
        if a in ("-WorkingDirectory", "-ExpectedMirrorPath"):
            args[i + 1] = str(mirror.source)
    out = run_tool(args)
    assert out.returncode == 1, out.stdout + out.stderr
    assert "did not verify as the named mirror" in out.stdout, out.stdout
    assert not receipt.exists(), "a refused preparation writes no receipt"


def test_prepare_refuses_a_mirror_mutated_after_construction(tmp_path):
    """The other half of step 1a: the mirror verified at preparation
    time must be the mirror that was measured at construction time.

    only.txt is TRACKED and clean at the mirror's own HEAD, so editing
    it in place moves neither head. Only the mirror-state fingerprint
    Task 1a added can see it, which is why that task had to run first.
    """
    mirror = build_real_mirror(tmp_path)
    (mirror.path / "only.txt").write_text("changed after construction\n")
    body, prior = _default_body_and_prior(tmp_path)
    receipt = tmp_path / "receipt.json"
    out = run_tool(_prepare_args(mirror, tmp_path / "dispatch", receipt,
                                 body, prior))
    assert out.returncode == 1, out.stdout + out.stderr
    assert "did not verify as the named mirror" in out.stdout, out.stdout
    assert not receipt.exists(), "a refused preparation writes no receipt"


def test_launch_and_poll_are_gone(tmp_path):
    for mode in ("-Launch", "-Poll"):
        out = run_tool([mode])
        assert out.returncode == 2


# ---------------------------------------------------------------------
# -Classify
#
# These fixtures build a dispatch directory (and a sidecar receipt) by
# hand, never through -Prepare: -Classify's own contract is about the
# STATE on disk, not about how it got there, and a real mirror is slow
# to build for every one of seventeen states. `meta.json`, written next
# to the dispatch directory, is test bookkeeping only - it is never read
# by the tool - and it is what lets classify() supply -ReceiptPath,
# -ExpectedRound, -ExpectedReceiptSha256 and -Redeem without every test
# having to carry them by hand.
# ---------------------------------------------------------------------
CLASSIFY_ROUND = "Sol R1"
CLASSIFY_NONCE = "1" * 32


def _write_receipt(receipt_path, dispatch_dir, round_label=CLASSIFY_ROUND,
                    working_directory=None, workdir_evidence="none"):
    """A well-formed schema-2 receipt (Task 2's field set). Returns the
    sha256 hex of the bytes written, which is what -ExpectedReceiptSha256
    pins in the real wrapper."""
    obj = {
        "dispatchDir": str(dispatch_dir),
        "token": "tok-" + os.urandom(4).hex(),
        "round": round_label,
        "workingDirectory": str(working_directory),
        "dispatchHost": "C:\\ps.exe",
        "priorStateSha256": "a" * 64,
        "workdirEvidence": workdir_evidence,
        "repoRoot": "C:\\repo",
        "sourceHead": "b" * 40,
        "mirrorHead": "c" * 40,
        "sourceStatusSha256": "d" * 64,
        "mirrorStateSha256": "e" * 64,
        "expectedMirrorPath": "C:\\mirror",
        "schema": 2,
    }
    data = json.dumps(obj)
    Path(receipt_path).write_text(data, encoding="utf-8")
    return hashlib.sha256(data.encode("utf-8")).hexdigest()


def _write_meta(base, receipt_path, round_label, sha256, nonce):
    (Path(base) / "meta.json").write_text(json.dumps({
        "receipt": str(receipt_path), "round": round_label,
        "sha256": sha256, "nonce": nonce}), encoding="utf-8")


def _read_meta(d):
    return json.loads((Path(d).parent / "meta.json").read_text(encoding="utf-8"))


def classify(d, receipt=None, round_label=None, sha256=None, redeem=None,
             extra=None, json_mode=False):
    """Call -Classify against dispatch directory d, filling in
    -ReceiptPath / -ExpectedRound / -ExpectedReceiptSha256 / -Redeem from
    the meta.json sidecar the builder wrote, unless a test overrides one
    to probe that field alone."""
    meta = _read_meta(d)
    args = [
        "-Classify", "-DispatchDir", str(d),
        "-ReceiptPath", str(receipt if receipt is not None else meta["receipt"]),
        "-ExpectedRound", round_label if round_label is not None else meta["round"],
        "-ExpectedReceiptSha256", sha256 if sha256 is not None else meta["sha256"],
        "-Redeem", redeem if redeem is not None else meta["nonce"],
    ]
    if json_mode:
        args.append("-Json")
    if extra:
        args += list(extra)
    return run_tool(args)


def build_dispatch(base):
    """A dispatch directory reserved and ready for -Classify, with no
    receipt written yet - the minimal fixture for receipt-schema tests."""
    base = Path(base)
    base.mkdir(parents=True, exist_ok=True)
    d = base / "dispatch"
    d.mkdir()
    receipt_path = base / "receipt.json"
    (d / "classification").write_text("classifying:" + CLASSIFY_NONCE, encoding="utf-8")
    _write_meta(base, receipt_path, CLASSIFY_ROUND, "0" * 64, CLASSIFY_NONCE)
    return d, receipt_path


def build_dispatch_with_workdir_evidence(base, evidence):
    """A dispatch directory built through the documented order up to and
    including the cwd-container check (state 8): reserved, with a valid
    matching receipt and a claim file, so only the workdir-evidence
    states (9-11) and everything after them remain open. The caller adds
    exit / reply / transcript by hand."""
    base = Path(base)
    base.mkdir(parents=True, exist_ok=True)
    d = base / "dispatch"
    d.mkdir()
    workdir = base / "workdir"
    workdir.mkdir()
    receipt_path = base / "receipt.json"
    (d / "classification").write_text("classifying:" + CLASSIFY_NONCE, encoding="utf-8")
    (d / "claim").write_text("", encoding="utf-8")
    sha = _write_receipt(receipt_path, d, working_directory=workdir,
                          workdir_evidence=evidence)
    _write_meta(base, receipt_path, CLASSIFY_ROUND, sha, CLASSIFY_NONCE)
    return d


def build_dispatch_ready_to_classify(base):
    """A dispatch directory built all the way through reply-present, plus
    the nonce that redeems it - test_classify_accepts_only_its_own_nonce
    rewrites `classification` by hand and must still be able to redeem it
    at the end."""
    d = build_dispatch_for_state(base, "reply-present")
    meta = _read_meta(d)
    return d, meta["nonce"]


def build_dispatch_for_state(base, state):
    """Build a dispatch directory that satisfies every state EARLIER than
    `state` in the documented order and leaves `state`'s own condition
    unmet, so classify(d) with no overrides lands on exactly `state`."""
    base = Path(base)
    base.mkdir(parents=True, exist_ok=True)
    d = base / "dispatch"
    d.mkdir()
    workdir = base / "workdir"
    workdir.mkdir()
    receipt_path = base / "receipt.json"
    nonce = CLASSIFY_NONCE
    round_label = CLASSIFY_ROUND

    if state == "never-reserved":
        _write_meta(base, receipt_path, round_label, "0" * 64, nonce)
        return d
    if state == "not-ready":
        (d / "classification").write_text("reserved", encoding="utf-8")
        _write_meta(base, receipt_path, round_label, "0" * 64, nonce)
        return d
    if state == "already-classified":
        (d / "classification").write_text("done", encoding="utf-8")
        _write_meta(base, receipt_path, round_label, "0" * 64, nonce)
        return d

    # Every state from here on requires a redeemable reservation.
    (d / "classification").write_text("classifying:" + nonce, encoding="utf-8")

    if state == "no-receipt":
        _write_meta(base, receipt_path, round_label, "0" * 64, nonce)
        return d

    if state == "receipt-not-expected":
        sha = _write_receipt(receipt_path, d, round_label="Some Other Round",
                              working_directory=workdir)
        _write_meta(base, receipt_path, round_label, sha, nonce)
        return d

    if state == "receipt-altered":
        sha = _write_receipt(receipt_path, d, round_label=round_label,
                              working_directory=workdir)
        with open(receipt_path, "a", encoding="utf-8") as fh:
            fh.write(" ")
        _write_meta(base, receipt_path, round_label, sha, nonce)
        return d

    # From here on the receipt is valid, expected and unaltered.
    if state == "no-claim":
        sha = _write_receipt(receipt_path, d, round_label=round_label,
                              working_directory=workdir)
        _write_meta(base, receipt_path, round_label, sha, nonce)
        return d
    (d / "claim").write_text("", encoding="utf-8")

    if state == "cwd-unreadable":
        sha = _write_receipt(receipt_path, d, round_label=round_label,
                              working_directory=base / "does-not-exist")
        _write_meta(base, receipt_path, round_label, sha, nonce)
        return d

    if state in ("no-transcript", "workdir-unconfirmed", "workdir-mismatch"):
        sha = _write_receipt(receipt_path, d, round_label=round_label,
                              working_directory=workdir,
                              workdir_evidence="C:\\mirror")
        _write_meta(base, receipt_path, round_label, sha, nonce)
        if state == "no-transcript":
            return d
        if state == "workdir-unconfirmed":
            (d / "transcript").write_text("no header here at all", encoding="utf-8")
            return d
        (d / "transcript").write_text("workdir: C:\\elsewhere", encoding="utf-8")
        return d

    # workdirEvidence "none" for every remaining state: the check is
    # skipped entirely, satisfying states 9-11 vacuously.
    sha = _write_receipt(receipt_path, d, round_label=round_label,
                          working_directory=workdir, workdir_evidence="none")
    _write_meta(base, receipt_path, round_label, sha, nonce)

    if state == "no-exit-file":
        return d
    if state == "exit-unreadable":
        (d / "exit").write_text("not-a-number", encoding="ascii")
        return d
    if state == "exit-nonzero":
        (d / "exit").write_text("7", encoding="ascii")
        return d
    (d / "exit").write_text("0", encoding="ascii")

    if state == "no-reply":
        return d
    if state == "reply-empty":
        (d / "reply").write_text("", encoding="utf-8")
        return d
    if state == "reply-present":
        (d / "reply").write_text("a verdict", encoding="utf-8")
        return d

    raise ValueError("unknown state: " + state)


STATES = [
    ("never-reserved", 1), ("not-ready", 1), ("already-classified", 1),
    ("no-receipt", 1), ("receipt-not-expected", 1), ("receipt-altered", 1),
    ("no-claim", 1), ("cwd-unreadable", 1),
    ("no-transcript", 1), ("workdir-unconfirmed", 1),
    ("workdir-mismatch", 1),
    ("no-exit-file", 1), ("exit-unreadable", 1), ("exit-nonzero", 1),
    ("no-reply", 1), ("reply-empty", 1), ("reply-present", 0),
]
# This list is the ONLY place the state count is written down. Do not
# restate it as a number in prose: an edited list makes the prose wrong,
# which is a drift class this repo has already recorded.


@pytest.mark.parametrize("state,code", STATES)
def test_each_state_and_its_exit_code(tmp_path, state, code):
    d = build_dispatch_for_state(tmp_path, state)
    out = classify(d)
    assert out.stdout.strip().endswith(state), out.stdout
    assert out.returncode == code


def test_no_state_but_reply_present_can_exit_zero(tmp_path):
    # Drive the TOOL for every state and collect the codes it really
    # returned. Asserting over the STATES constant instead would assert
    # the test module against itself and lock nothing.
    zero = []
    for state, _ in STATES:
        d = build_dispatch_for_state(tmp_path / state, state)
        if classify(d).returncode == 0:
            zero.append(state)
    assert zero == ["reply-present"]


def test_classify_accepts_only_its_own_nonce(tmp_path):
    d, nonce = build_dispatch_ready_to_classify(tmp_path)
    for content, expected in [
        ("reserved", "not-ready"),
        ("classifying:" + "0" * 32, "already-classified"),
        ("reply-present", "already-classified"),
    ]:
        (d / "classification").write_text(content, encoding="utf-8")
        out = classify(d, redeem=nonce)
        assert out.returncode == 1
        assert out.stdout.strip().endswith(expected), content
    (d / "classification").write_text("classifying:" + nonce, encoding="utf-8")
    assert classify(d, redeem=nonce).returncode == 0


def test_a_missing_transcript_is_its_own_state(tmp_path):
    d = build_dispatch_with_workdir_evidence(tmp_path, evidence="C:\\mirror")
    (d / "exit").write_text("0", encoding="ascii")
    (d / "reply").write_text("a verdict", encoding="utf-8")
    # no transcript file at all
    out = classify(d)
    assert out.stdout.strip().endswith("no-transcript")
    assert out.returncode == 1


def test_a_failed_round_in_the_wrong_tree_reports_the_WRONG_TREE(tmp_path):
    # First match wins, and the workdir states are deliberately EARLIER
    # than the exit states. Both reviewer lanes overruled the opposite
    # order: a round that read the wrong tree read an instruction
    # back-channel, so its own failure report describes another subject.
    d = build_dispatch_with_workdir_evidence(tmp_path, evidence="C:\\mirror")
    (d / "exit").write_text("1", encoding="ascii")
    (d / "transcript").write_text("workdir: C:\\elsewhere", encoding="utf-8")
    out = classify(d)
    assert out.stdout.strip().endswith("workdir-mismatch")


def test_only_the_FIRST_workdir_header_counts(tmp_path):
    # The transcript is prompt-steerable, so a later line proves nothing.
    d = build_dispatch_with_workdir_evidence(tmp_path, evidence="C:\\mirror")
    (d / "transcript").write_text(
        "workdir: C:\\elsewhere\nuser\nworkdir: C:\\mirror\n", encoding="utf-8")
    (d / "exit").write_text("0", encoding="ascii")
    (d / "reply").write_text("a verdict", encoding="utf-8")
    out = classify(d)
    assert out.stdout.strip().endswith("workdir-mismatch")


def test_a_transcript_with_no_header_is_unconfirmed_not_mismatched(tmp_path):
    d = build_dispatch_with_workdir_evidence(tmp_path, evidence="C:\\mirror")
    (d / "transcript").write_text("no header here at all", encoding="utf-8")
    (d / "exit").write_text("0", encoding="ascii")
    (d / "reply").write_text("a verdict", encoding="utf-8")
    out = classify(d)
    assert out.stdout.strip().endswith("workdir-unconfirmed")


def test_state_order_is_first_match_wins(tmp_path):
    # A directory broken in two ways reports the EARLIER state.
    d = build_dispatch_for_state(tmp_path, "no-claim")
    (d / "exit").write_text("7", encoding="ascii")
    out = classify(d)
    assert out.stdout.strip().endswith("no-claim")


def test_workdir_mismatch_beats_a_missing_reply(tmp_path):
    d = build_dispatch_with_workdir_evidence(tmp_path, evidence="C:\\mirror")
    (d / "transcript").write_text("workdir: C:\\somewhere-else", encoding="utf-8")
    (d / "exit").write_text("0", encoding="ascii")
    # no reply file at all
    out = classify(d)
    assert out.stdout.strip().endswith("workdir-mismatch")
    assert out.returncode == 1


def test_none_skips_the_workdir_check_only_on_the_exact_literal(tmp_path):
    d = build_dispatch_with_workdir_evidence(tmp_path, evidence="none")
    (d / "exit").write_text("0", encoding="ascii")
    (d / "reply").write_text("a verdict", encoding="utf-8")
    out = classify(d)
    assert out.returncode == 0


def test_a_schema_one_receipt_is_no_receipt(tmp_path):
    d, r = build_dispatch(tmp_path)
    r.write_text(json.dumps({
        "dispatchDir": str(d), "token": "t", "round": "Sol R1",
        "startTicks": "1"}), encoding="utf-8")
    out = classify(d, receipt=r)
    assert out.stdout.strip().endswith("no-receipt")


def test_an_unknown_argument_is_refused_not_absorbed(tmp_path):
    d = build_dispatch_for_state(tmp_path, "reply-present")
    out = classify(d, extra=["-Jsoon"])
    assert out.returncode == 2
    assert "-Jsoon" in out.stdout


# ---------------------------------------------------------------------
# Task 4: the wrapper -Prepare composes, and the coupling it exists to
# prove - the exit code of the ONE harness task the caller dispatches is
# the classification, not a file a later reader happens to find on disk.
# ---------------------------------------------------------------------
def test_the_wrapper_exit_code_is_the_classification(tmp_path):
    # A lane body that succeeds and writes a reply.
    d = prepare_and_run(tmp_path, body="""
$code = 0
[System.IO.File]::WriteAllText("$PSScriptRoot/reply", "a verdict")
""")
    assert d.returncode == 0


def test_a_failed_client_makes_the_wrapper_exit_nonzero(tmp_path):
    # The body is a CHILD SCRIPT now, so setting $code proves nothing.
    # It must EXIT with the code, or the child exits zero and the round
    # reads as a success with no reply.
    d = prepare_and_run(tmp_path, body="exit 1\n")
    assert d.returncode == 1
    assert "exit-nonzero" in d.stdout


def test_the_claim_is_created_before_the_lane_body_runs(tmp_path):
    d = prepare_and_run(tmp_path, body="""
$code = 0
if (-not (Test-Path "$PSScriptRoot/claim")) { throw "no claim yet" }
[System.IO.File]::WriteAllText("$PSScriptRoot/reply", "ok")
""")
    assert d.returncode == 0


def test_a_second_run_of_the_same_wrapper_fails_and_writes_nothing(tmp_path):
    first = prepare_and_run(tmp_path, body=OK_BODY)
    assert first.returncode == 0
    before = snapshot(first.dispatch_dir)
    second = run_wrapper(first.wrapper)
    assert second.returncode != 0
    assert snapshot(first.dispatch_dir) == before


def test_two_concurrent_first_runs_leave_exactly_one_winner(tmp_path):
    p = prepare(tmp_path, body=SLOW_OK_BODY)
    a, b = run_wrapper_concurrently(p.wrapper, p.wrapper)
    codes = sorted([a.returncode, b.returncode])
    assert codes[0] == 0
    assert codes[1] != 0


def test_a_missing_working_directory_fails_the_wrapper(tmp_path):
    p = prepare(tmp_path, body=OK_BODY)
    # onerror=_force_remove: git marks its object files read-only, so a
    # plain rmtree raises PermissionError on Windows before reaching the
    # condition under test - see test_review_mirror.py's own helper.
    shutil.rmtree(p.working_directory, onerror=_force_remove)
    out = run_wrapper(p.wrapper)
    assert out.returncode != 0
    assert not (p.dispatch_dir / "reply").exists()


def test_a_wrapper_killed_after_publishing_exit_and_reply_does_not_exit_zero(tmp_path, monkeypatch):
    # THE test. Under Option C's post-hoc classifier this same directory
    # reads reply-present at exit 0.
    barrier = tmp_path / "hold"
    monkeypatch.setenv("PARALLAX_DISPATCH_HOLD_AFTER_EXIT_WRITE", str(barrier))
    p = prepare(tmp_path, body=OK_BODY)
    proc = start_wrapper(p.wrapper)
    # The seam fires AFTER the wrapper writes the exit file and BEFORE it
    # calls the classifier. That is exactly the interval in question.
    wait_for(Path(str(barrier) + ".started"))
    assert (p.dispatch_dir / "exit").read_text().strip() == "0"
    assert (p.dispatch_dir / "reply").read_text().strip() != ""
    # The reservation was CONSUMED before the exit file was written, so
    # by the time a successful-looking exit exists it is no longer in a
    # state any outside caller is handed the key to.
    assert (p.dispatch_dir / "classification").read_text().strip().startswith(
        "classifying:")
    kill_tree(proc.pid)
    assert proc.wait() != 0
    # And the disk state that would have fooled Option C is still there.
    assert (p.dispatch_dir / "exit").read_text().strip() == "0"


def test_a_hand_run_classify_after_that_kill_is_refused(tmp_path, monkeypatch):
    # THE regression test for two failed attempts at this fix. Version one
    # let -Classify CREATE the reservation, so a post-kill call won it.
    # Version two moved creation to the wrapper but still treated
    # "reserved" as permission, so the very kill above left the file in an
    # acceptable state and no deliberate act was needed.
    p = killed_after_publish(tmp_path, monkeypatch)
    held = (p.dispatch_dir / "classification").read_text().strip()
    assert held.startswith("classifying:")   # consumed BEFORE exit was written
    # A caller who does not know the run-time nonce is refused. Guessing
    # every plausible argument does not help: the nonce is in no file
    # -Prepare wrote.
    out = classify(p.dispatch_dir, redeem="0" * 32)
    assert out.returncode == 1
    assert out.stdout.strip().endswith("already-classified")


def test_classify_never_creates_the_reservation(tmp_path):
    p = prepare(tmp_path, body=OK_BODY)  # prepared, never run
    assert not (p.dispatch_dir / "classification").exists()
    out = classify(p.dispatch_dir, redeem="0" * 32)
    assert out.returncode == 1
    assert out.stdout.strip().endswith("never-reserved")
    assert not (p.dispatch_dir / "classification").exists()


def test_the_reservation_is_consumed_before_the_exit_file_appears(tmp_path, monkeypatch):
    # Ordering is the whole argument. If exit were written first, the
    # post-kill directory would hold "reserved" plus a successful exit.
    p = killed_after_publish(tmp_path, monkeypatch)
    assert (p.dispatch_dir / "exit").exists()
    assert not (p.dispatch_dir / "classification").read_text().strip() == "reserved"


@pytest.mark.parametrize("field,value,expected_state", [
    ("priorStateSha256", "ff" * 32, "receipt-altered"),
    ("workdirEvidence", "none", "receipt-altered"),      # would switch OFF the B5 check
    ("workingDirectory", "C:/elsewhere", "receipt-altered"),
    # round is also compared at state 5 (receipt-not-expected), which the
    # already-locked -Classify order (Task 3) checks BEFORE the digest at
    # state 6 - so editing round is caught there first, not as
    # receipt-altered. Still detected, still a non-zero exit; only the
    # NAME of the state that catches it differs for this one field.
    ("round", "Sol R2", "receipt-not-expected"),
])
def test_an_edit_to_ANY_receipt_field_is_detected(tmp_path, field, value, expected_state):
    # A per-field compare bound four of fourteen fields and called the
    # receipt immutable. The workdirEvidence case is the one that mattered:
    # editing it to "none" silently disables the working-directory
    # confirmation for that round.
    p = prepare(tmp_path, body=OK_BODY)
    got = json.loads(p.receipt.read_text(encoding="utf-8"))
    got[field] = value
    p.receipt.write_text(json.dumps(got), encoding="utf-8")
    out = run_wrapper(p.wrapper)
    assert out.returncode == 1
    assert expected_state in out.stdout


def test_a_whitespace_only_receipt_edit_is_detected(tmp_path):
    # The digest is over BYTES, so reformatting is an edit too. This is
    # deliberate: a receipt nobody rewrote has bytes nobody changed.
    p = prepare(tmp_path, body=OK_BODY)
    p.receipt.write_text(p.receipt.read_text(encoding="utf-8") + "\n",
                         encoding="utf-8")
    out = run_wrapper(p.wrapper)
    assert "receipt-altered" in out.stdout


def test_the_body_streams_never_reach_the_wrapper_stdout(tmp_path):
    d = prepare_and_run(tmp_path, body="""
Write-Output "stdout from the body"
[Console]::Error.WriteLine("stderr from the body")
[System.IO.File]::WriteAllText("$PSScriptRoot/reply", "ok")
exit 0
""")
    assert d.stdout.strip().splitlines() == [d.stdout.strip()]  # exactly one line
    assert "from the body" not in d.stdout
    assert "stdout from the body" in _read_text(d.dispatch_dir / "body.out")
    assert "stderr from the body" in _read_text(d.dispatch_dir / "body.err")


def test_prepare_refuses_a_working_directory_that_does_not_verify(tmp_path):
    plain = tmp_path / "not-a-mirror"
    plain.mkdir()
    out = prepare_default(tmp_path, working_directory=plain)
    assert out.returncode == 1
    assert "mirror identity" in out.stdout


def test_prepare_refuses_a_mirror_whose_head_does_not_match(tmp_path):
    mirror = build_real_mirror(tmp_path)
    out = prepare_default(tmp_path, mirror=mirror, mirror_head="0" * 40)
    assert out.returncode == 1
    assert "mirror identity" in out.stdout


def test_the_wrapper_reverifies_the_tree_before_the_client_runs(tmp_path):
    # Post-preparation mutation that moves NEITHER head: a tracked file in
    # the mirror worktree, edited, not committed. This is the case the
    # shipped verifier could not see, and it is why Task 1a exists. Do not
    # weaken it to a commit - a commit moves the mirror head and would
    # test the check that already worked.
    p = prepare(tmp_path, body=OK_BODY)
    (p.working_directory / "README.md").write_text("changed", encoding="utf-8")
    out = run_wrapper(p.wrapper)
    assert out.returncode != 0
    assert not (p.dispatch_dir / "reply").exists()


def test_a_mirror_mutated_DURING_the_round_fails_the_wrapper(tmp_path):
    # The test above mutates before the wrapper starts, so it only
    # exercises the FIRST verification. This one exercises the second:
    # the child itself edits a tracked file, writes a good reply, and
    # exits zero. Everything on disk says success.
    # The helper interpolates the real mirror path; the placeholder below
    # is NOT written into the body literally.
    p = prepare(tmp_path, body="""
[System.IO.File]::WriteAllText("{workingDirectory}/README.md", "changed mid-round")
[System.IO.File]::WriteAllText("$PSScriptRoot/reply", "a verdict")
exit 0
""")
    out = run_wrapper(p.wrapper)
    assert out.returncode != 0
    # And the reservation was never consumed, so no later call can redeem
    # it either.
    assert (p.dispatch_dir / "classification").read_text().strip() == "reserved"


def test_a_second_verification_that_cannot_RUN_fails_the_wrapper(tmp_path):
    # Regression for the defect this design introduced and then removed:
    # under Continue, a call that fails to bind leaves $LASTEXITCODE at
    # the client's successful zero, so the guard passes and the check
    # never happened.
    #
    # The helper MUST break only the SECOND call site. The wrapper names
    # the verifier tool twice and nothing in its text distinguishes them,
    # so a helper that breaks both kills the wrapper at the FIRST
    # verification - which the defective version did too, making the test
    # pass against the bug it exists to catch. Break the second
    # occurrence only, by index.
    p = prepare(tmp_path, body=OK_BODY)
    break_second_mirror_call_only(p.wrapper)
    out = run_wrapper(p.wrapper)
    assert out.returncode != 0
    assert (p.dispatch_dir / "classification").read_text().strip() == "reserved"


def test_the_mirror_verifier_output_never_reaches_the_wrapper_stdout(tmp_path):
    d = prepare_and_run(tmp_path, body=OK_BODY)
    assert "identity: verified" not in d.stdout
    assert "identity: verified" in _read_text(d.dispatch_dir / "mirror.verify")


def test_a_body_that_exits_the_process_cannot_skip_the_classification(tmp_path):
    # The body runs as a CHILD, so its own exit cannot end the wrapper.
    d = prepare_and_run(tmp_path, body="[Environment]::Exit(0)\n")
    assert d.returncode != 0
    assert "no-reply" in d.stdout


def test_the_wrapper_stdout_is_the_classifier_line_and_nothing_else(tmp_path):
    d = prepare_and_run(tmp_path, body=OK_BODY)
    lines = d.stdout.strip().splitlines()
    assert len(lines) == 1          # checking only the LAST line would let
    assert lines[0].endswith("reply-present")   # a leaked line pass
