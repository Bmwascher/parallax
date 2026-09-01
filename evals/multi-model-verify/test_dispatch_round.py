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
import hashlib
import json
import os
import shutil
import subprocess
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
                   round_label=DEFAULT_ROUND, host="powershell", json_mode=False):
    args = [
        "-Prepare", "-DispatchDir", str(dispatch_dir), "-WrapperBody", str(body),
        "-ReceiptPath", str(receipt_path), "-Round", round_label,
        "-WorkingDirectory", str(mirror.path), "-RepoRoot", str(mirror.source),
        "-SourceHead", mirror.source_head, "-MirrorHead", mirror.mirror_head,
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
                     json_mode=False, round_label=DEFAULT_ROUND):
    """A full, otherwise-valid -Prepare invocation (real mirror, real
    prior-state file, real body), with exactly the field(s) under test
    overridden - so a block is attributable to that field alone."""
    mirror = build_real_mirror(tmp_path)
    body, prior = _default_body_and_prior(tmp_path)
    d = dispatch_dir if dispatch_dir is not None else tmp_path / "dispatch"
    r = receipt if receipt is not None else tmp_path / "receipt.json"
    args = _prepare_args(mirror, d, r, body, prior, round_label=round_label,
                          host=host, json_mode=json_mode)
    return run_tool(args)


class Prepared(object):
    def __init__(self, dispatch_dir, receipt_path, result):
        self.dispatch_dir = dispatch_dir
        self.receipt_path = receipt_path
        self.result = result


def prepare(tmp_path, body, round_label=DEFAULT_ROUND):
    """A -Prepare call expected to SUCCEED, returning the dispatch
    directory it built so a test can read body.ps1 / wrapper.ps1 back out
    of it."""
    mirror = build_real_mirror(tmp_path)
    body_path = tmp_path / "body.ps1"
    body_path.write_text(body, encoding="ascii")
    prior = tmp_path / "prior.json"
    prior.write_text('{"kind":"fresh","knownRollouts":[]}', encoding="ascii")
    dispatch_dir = tmp_path / "dispatch"
    receipt_path = tmp_path / "receipt.json"
    args = _prepare_args(mirror, dispatch_dir, receipt_path, body_path, prior,
                          round_label=round_label, json_mode=False)
    result = run_tool(args)
    assert result.returncode == 0, (result.stdout, result.stderr)
    return Prepared(dispatch_dir, receipt_path, result)


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
