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


def test_launch_and_poll_are_gone(tmp_path):
    for mode in ("-Launch", "-Poll"):
        out = run_tool([mode])
        assert out.returncode == 2
