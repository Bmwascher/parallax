"""Review mirror construction (0.17.0, backlog item 4).

The mirror is a FILE COPY preserving .git, never a clone: the review inputs
are routinely gitignored, and a clone carries tracked files only. Probed
2026-07-26 in KitnEssentials, where a cloned workspace dropped the frozen
plan, the spec and the reference source while every route and containment
check stayed green.
"""
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
MIRROR = REPO_ROOT / "tools" / "new-review-mirror.ps1"
FIXTURES = Path(__file__).parent / "fixtures" / "codex-prompt-input"
STUB = Path(__file__).parent / "fixtures" / "stub-codex" / "stub-codex.ps1"


# WINDOWS ONLY, for the same reason as the probe's suite: the mirror runs
# the probe, which resolves the reviewer's global instruction file under
# `$env:USERPROFILE`, and the lane lock lives under `$env:LOCALAPPDATA`.
# Neither exists on Linux, so the run refuses to report a measurement it
# could not make - the script working, not failing.
#
# Guarding only on a PowerShell host being present was not enough: the CI
# runner ships `pwsh`, so these cases ran on Linux and failed there for a
# second, different reason. See the probe suite's header for the full
# sequence.
#
# COVERAGE, recorded rather than assumed: these cases are Windows-only, so
# the ubuntu job skips them. The `powershell-hosts` job on windows-latest
# runs this module under BOTH powershell.exe and pwsh.exe. If this module
# ever leaves both Windows pytest steps, that claim is false and
# test_backup_lane.py asserts it back.
POWERSHELL = (os.environ.get("PARALLAX_PS_HOST")
              or shutil.which("powershell") or shutil.which("pwsh"))

pytestmark = pytest.mark.skipif(
    os.name != "nt" or POWERSHELL is None,
    reason="the review mirror is a Windows tool: it needs a PowerShell "
           "host and the Windows profile variables it measures")


def ps_host():
    return POWERSHELL


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args],
                          capture_output=True, text=True, check=True).stdout


def commit(repo, message):
    git(repo, "-c", "user.email=t@t", "-c", "user.name=t",
        "commit", "-q", "-m", message)


def make_repo(tmp_path):
    """A scratch repo with one tracked file, one ignored file, and one
    untracked file, so the baseline has something to carry."""
    repo = tmp_path / "src"
    repo.mkdir()
    git(tmp_path, "init", "-q", str(repo))
    (repo / "kept.txt").write_text("tracked\n")
    (repo / ".gitignore").write_text("ignored/\n")
    (repo / "ignored").mkdir()
    (repo / "ignored" / "secret.txt").write_text("gitignored input\n")
    (repo / "untracked.txt").write_text("untracked\n")
    git(repo, "add", "kept.txt", ".gitignore")
    commit(repo, "base")
    return repo


def make_clean_repo(tmp_path):
    """A repo with NOTHING for the baseline to carry: no back-channels, no
    untracked files, no ignored files. The ordinary case, and the one an
    empty-array return would have misread as an enumeration failure."""
    repo = tmp_path / "clean"
    repo.mkdir()
    git(tmp_path, "init", "-q", str(repo))
    (repo / "only.txt").write_text("tracked\n")
    git(repo, "add", "only.txt")
    commit(repo, "base")
    return repo


def run_mirror(repo, mirror, *extra):
    return subprocess.run(
        [ps_host(), "-NoProfile", "-NonInteractive", "-File", str(MIRROR),
         "-RepoRoot", str(repo), "-MirrorPath", str(mirror),
         "-SkipProbe", *extra],
        capture_output=True, text=True)


SKIP_BLOCK = "BLOCKED: no client measurement was made (-SkipProbe)"


def assert_built(proc):
    """-SkipProbe builds the mirror but VERIFIES nothing, so it exits 1.

    The exit code reports dispatch-readiness, not construction: a mirror
    with no client measurement is not cleared for dispatch, and must not
    share an exit code with one that is. The mode-diff review of
    2026-07-28 found the old exit 0 there.

    Asserting the SPECIFIC skip line is what keeps these tests able to
    catch a real construction failure, which also exits 1 but with a
    different reason.
    """
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert SKIP_BLOCK in proc.stdout, proc.stdout + proc.stderr


def read_block(stdout, label):
    """Lines of one labelled block from the record output."""
    lines = stdout.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(label))
    out = []
    for line in lines[start + 1:]:
        if line and not line.startswith("  "):
            break
        if line.strip():
            out.append(line.strip())
    return out


def test_the_mirror_carries_gitignored_files(tmp_path):
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror)
    assert_built(proc)
    assert (mirror / "ignored" / "secret.txt").exists(), (
        "a clone would have dropped this; the mirror must not"
    )
    assert (mirror / ".git").exists()


def test_a_tracked_agents_md_is_deleted_and_committed(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "AGENTS.md").write_text("# planted\n")
    git(repo, "add", "AGENTS.md")
    commit(repo, "plant")
    before = git(repo, "rev-parse", "HEAD").strip()
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror)
    assert_built(proc)
    assert not (mirror / "AGENTS.md").exists()
    assert (repo / "AGENTS.md").exists(), "the real tree is never touched"
    after = git(mirror, "rev-parse", "HEAD").strip()
    assert after != before, (
        "a tracked deletion left uncommitted is a tracked modification in"
        " the baseline, which bars mode diff and breaks"
        " HEAD-identifies-content"
    )
    assert "AGENTS.md" not in git(mirror, "status", "--porcelain")


def test_an_ignored_agents_drop_is_deleted_without_a_commit(tmp_path):
    repo = make_repo(tmp_path)
    (repo / ".gitignore").write_text("ignored/\n.agents/\n")
    git(repo, "add", ".gitignore")
    commit(repo, "ignore agents")
    skill = repo / ".agents" / "skills" / "planted"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("---\nname: planted\n---\n")
    before = git(repo, "rev-parse", "HEAD").strip()
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror)
    assert_built(proc)
    assert not (mirror / ".agents").exists()
    after = git(mirror, "rev-parse", "HEAD").strip()
    assert after == before, (
        "nothing to commit alongside an unchanged HEAD is the CORRECT"
        " observation for an ignored entry, not an inconsistency to chase"
    )


def test_a_gitignored_back_channel_is_found_and_removed(tmp_path):
    # Checked 2026-07-28 against a claim that the enumeration misses
    # ignored files: it does not. `--others` WITHOUT `--exclude-standard`
    # lists ignored files too, and a gitignored root AGENTS.md IS ingested
    # by codex.
    repo = make_repo(tmp_path)
    (repo / ".gitignore").write_text("ignored/\n.agents/\nAGENTS.md\n")
    git(repo, "add", ".gitignore")
    commit(repo, "ignore the back-channels")
    (repo / "AGENTS.md").write_text("# ignored but still ingested\n")
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror)
    assert_built(proc)
    assert not (mirror / "AGENTS.md").exists()


def test_a_nested_agents_md_is_found(tmp_path):
    repo = make_repo(tmp_path)
    deep = repo / "a" / "b" / "c"
    deep.mkdir(parents=True)
    (deep / "AGENTS.md").write_text("# deep\n")
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror)
    assert_built(proc)
    assert list(mirror.rglob("AGENTS.md")) == [], (
        "the *AGENTS.md pathspec carries a leading star, so it reaches any"
        " depth; a root-only check misses a nested drop"
    )


def test_a_nested_dot_agents_is_a_recorded_gap_not_a_silent_one(tmp_path):
    # `.agents/*` is anchored at the repo root, so a nested drop is NOT
    # enumerated. Measured 2026-07-28: codex-cli 0.144.1 advertises a ROOT
    # .agents/skills entry and does NOT advertise a nested one, so this is
    # unreachable today. The client probe covers it regardless. This test
    # records the boundary so a future change turns it red instead of
    # passing silently.
    repo = make_repo(tmp_path)
    deep = repo / "sub" / ".agents" / "skills" / "deep"
    deep.mkdir(parents=True)
    (deep / "SKILL.md").write_text("---\nname: deep\n---\n")
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror)
    assert_built(proc)
    assert (mirror / "sub" / ".agents" / "skills" / "deep" / "SKILL.md").exists(), (
        "the root-anchored pathspec does not reach this entry; if this ever"
        " starts being removed, the enumeration changed and the accepted"
        " limit in the design must be updated in the same commit"
    )


def test_enumeration_sweeps_the_kimi_code_back_channel():
    """The reviewed tree's .kimi-code/ and .agents/ entries are removed
    because they are READABLE, not because discovery was observed.
    Measured: nothing was loaded from either root, and the reviewer read a
    planted SKILL.md as ordinary file content and declined on its own
    judgment. Judgment is not a control; removal is. Whether this client
    would ever DISCOVER those roots is unverified, and the sweep does not
    depend on it."""
    body = (REPO_ROOT / "tools" / "new-review-mirror.ps1").read_text(
        encoding="utf-8")
    assert "'.kimi-code/*'" in body


def test_a_clean_repo_is_not_read_as_a_failed_enumeration(tmp_path):
    # PowerShell unrolls an empty array returned from a function, so the
    # caller's variable becomes $null and a clean repo looks exactly like a
    # git failure.
    repo = make_clean_repo(tmp_path)
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror)
    assert_built(proc)
    assert "could not enumerate" not in proc.stdout


def test_an_empty_baseline_is_a_legitimate_state(tmp_path):
    repo = make_clean_repo(tmp_path)
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror)
    assert_built(proc)
    assert read_block(proc.stdout, "baseline:") == []
    assert read_block(proc.stdout, "manifest:") == []
    assert "baseline capture failed" not in proc.stdout


def test_an_existing_mirror_is_refused_without_force(tmp_path):
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    mirror.mkdir()
    (mirror / "stale.txt").write_text("from a previous debate\n")
    proc = run_mirror(repo, mirror)
    assert proc.returncode == 2
    assert "already exists" in proc.stdout


def test_force_replaces_an_existing_mirror(tmp_path):
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    mirror.mkdir()
    (mirror / "stale.txt").write_text("from a previous debate\n")
    proc = run_mirror(repo, mirror, "-Force")
    assert_built(proc)
    assert not (mirror / "stale.txt").exists()


def test_the_manifest_covers_exactly_the_baseline_paths(tmp_path):
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror)
    assert_built(proc)
    paths = [line.rsplit(" ", 1)[0]
             for line in read_block(proc.stdout, "manifest:")]
    assert "ignored/secret.txt" in paths
    assert "untracked.txt" in paths
    assert "kept.txt" not in paths, (
        "kept.txt is clean at HEAD, so HEAD already binds it"
    )


def test_the_manifest_hashes_raw_bytes_and_sorts_by_path(tmp_path):
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror)
    assert_built(proc)
    manifest = read_block(proc.stdout, "manifest:")
    paths = [line.rsplit(" ", 1)[0] for line in manifest]
    assert paths == sorted(paths), "sorted by path in byte order"
    for line in manifest:
        path, digest = line.rsplit(" ", 1)
        raw = (mirror / path).read_bytes()
        assert digest == hashlib.sha256(raw).hexdigest()


def test_a_directory_expands_recursively(tmp_path):
    repo = make_repo(tmp_path)
    (repo / "untr" / "sub").mkdir(parents=True)
    (repo / "untr" / "sub" / "one.txt").write_text("1\n")
    (repo / "untr" / "sub" / "two.txt").write_text("2\n")
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror)
    assert_built(proc)
    paths = [line.rsplit(" ", 1)[0]
             for line in read_block(proc.stdout, "manifest:")]
    assert "untr/sub/one.txt" in paths
    assert "untr/sub/two.txt" in paths
    assert "untr/" not in paths, (
        "a hash over a directory name identifies nothing"
    )


def test_the_baseline_is_the_raw_status_capture(tmp_path):
    # backup-lane.md defines the baseline as the status command's output.
    # An earlier revision printed stripped paths under that label, which
    # would have put a different object into the debate record under a
    # name the contract already owns.
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror)
    assert_built(proc)
    baseline = read_block(proc.stdout, "baseline:")
    assert any(line.startswith("?? ") for line in baseline), (
        "status codes are part of the baseline, not decoration"
    )
    assert any(line.startswith("!! ") for line in baseline), (
        "--ignored is why this workspace is a mirror at all"
    )


def test_a_rename_whose_destination_was_deleted_blocks(tmp_path):
    # Probed 2026-07-28: `git mv a.txt b.txt` then deleting b.txt reports
    # `RD a.txt -> b.txt`. The destination the manifest rule points at is
    # gone, so there is nothing to hash and skipping it would be a silent
    # hole.
    repo = make_repo(tmp_path)
    git(repo, "mv", "kept.txt", "moved.txt")
    (repo / "moved.txt").unlink()
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror)
    assert proc.returncode == 1
    assert "deleted" in proc.stdout


@pytest.mark.parametrize("tree", ["repo", "mirror"])
@pytest.mark.parametrize("relation", ["same", "inside", "parent"])
def test_an_overlapping_override_path_is_refused(tmp_path, tree, relation):
    # Six cases, not three. An earlier matrix named same/inside/parent but
    # every entry was an INSIDE case against a different tree, so equality
    # and containment were never exercised.
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    protected = repo if tree == "repo" else mirror
    target = {"same": protected,
              "inside": protected / "sub" / "o.txt",
              "parent": protected.parent}[relation]
    proc = subprocess.run(
        [ps_host(), "-NoProfile", "-NonInteractive", "-File", str(MIRROR),
         "-RepoRoot", str(repo), "-MirrorPath", str(mirror),
         "-OverrideOut", str(target), "-SkipProbe"],
        capture_output=True, text=True)
    assert proc.returncode == 2, proc.stdout
    assert "overlaps a protected tree" in proc.stdout
    assert (repo / "kept.txt").exists(), "the repo must still be there"


def test_a_stale_override_artifact_is_refused_before_any_work(tmp_path):
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    stale = tmp_path / "override.txt"
    stale.write_text("skills.config=[from a previous debate]")
    proc = subprocess.run(
        [ps_host(), "-NoProfile", "-NonInteractive", "-File", str(MIRROR),
         "-RepoRoot", str(repo), "-MirrorPath", str(mirror),
         "-OverrideOut", str(stale), "-SkipProbe"],
        capture_output=True, text=True)
    assert proc.returncode == 2
    assert "already exists" in proc.stdout
    assert not mirror.exists(), (
        "the check must come before the mirror is built, not after it has"
        " been copied, remediated and manifested"
    )
    assert stale.read_text() == "skills.config=[from a previous debate]"


@pytest.mark.parametrize("relation", ["same", "inside", "parent"])
def test_an_overlapping_mirror_path_is_refused(tmp_path, relation):
    # -Force recursively deletes MirrorPath. An overlapping pair would
    # delete the tree under review. The guard runs before anything is
    # created or removed.
    repo = make_repo(tmp_path)
    target = {"same": repo,
              "inside": repo / "nested" / "mirror",
              "parent": tmp_path}[relation]
    proc = run_mirror(repo, target, "-Force")
    assert proc.returncode == 2, proc.stdout
    assert (repo / "kept.txt").exists(), "the repo must still be there"
    assert (repo / "ignored" / "secret.txt").exists()


def test_the_probe_runs_and_the_default_override_is_recorded(tmp_path):
    # The only mirror test that does NOT pass -SkipProbe. It proves the
    # default artifact path is allocated, written, hashed and printed,
    # which is the whole handoff the transport depends on.
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    env = dict(os.environ)
    env["PARALLAX_STUB_FIXTURE"] = str(FIXTURES / "flagged.json")
    env["PARALLAX_STUB_FIXTURE2"] = str(FIXTURES / "suppressed.json")
    env["PARALLAX_STUB_LOG"] = str(tmp_path / "calls.log")
    proc = subprocess.run(
        [ps_host(), "-NoProfile", "-NonInteractive", "-File", str(MIRROR),
         "-RepoRoot", str(repo), "-MirrorPath", str(mirror),
         "-CodexCommand", str(STUB)],
        capture_output=True, text=True, env=env)
    # The ONE mirror test whose run made a real measurement, so exit 0 is
    # the correct expectation here and nowhere else in this module.
    assert proc.returncode == 0, proc.stdout + proc.stderr
    line = next(l for l in proc.stdout.splitlines()
                if l.startswith("override: "))
    artifact = Path(line[len("override: "):].strip())
    assert artifact.exists()
    raw = artifact.read_bytes()
    assert raw.startswith(b"skills.config=[")
    probe_line = next(l for l in proc.stdout.splitlines()
                      if l.startswith("probe: "))
    report = json.loads(probe_line[len("probe: "):])
    assert report["override_sha256"] == hashlib.sha256(raw).hexdigest()
    assert report["skills_after"] == 0


def test_a_failing_probe_blocks_the_mirror(tmp_path):
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    env = dict(os.environ)
    env["PARALLAX_STUB_FIXTURE"] = str(FIXTURES / "full.json")
    env["PARALLAX_STUB_FIXTURE2"] = str(FIXTURES / "full.json")
    env["PARALLAX_STUB_LOG"] = str(tmp_path / "calls.log")
    proc = subprocess.run(
        [ps_host(), "-NoProfile", "-NonInteractive", "-File", str(MIRROR),
         "-RepoRoot", str(repo), "-MirrorPath", str(mirror),
         "-CodexCommand", str(STUB)],
        capture_output=True, text=True, env=env)
    assert proc.returncode == 1
    assert "client context probe did not pass" in proc.stdout


def test_the_real_tree_is_never_written_to(tmp_path):
    repo = make_repo(tmp_path)
    before = sorted(p.relative_to(repo).as_posix()
                    for p in repo.rglob("*") if p.is_file())
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror)
    assert_built(proc)
    after = sorted(p.relative_to(repo).as_posix()
                   for p in repo.rglob("*") if p.is_file())
    assert before == after


def test_a_relative_mirror_path_is_resolved_where_it_is_deleted(tmp_path):
    """The guard and the deletion must resolve the SAME path.

    An earlier revision guarded the process-relative form of MirrorPath,
    while the later existence check and the forced replacement resolved
    the same parameter against PowerShell's provider location. Here the
    two differ: the process working directory puts the relative path
    outside the repo, so the old guard approved it, and the provider
    location puts it INSIDE the repo, so the forced replacement then
    destroyed part of the tree under review.

    Found by the mode-diff review of 2026-07-28, after an earlier review
    had called it theoretical. It is not: -MirrorPath is a public
    parameter and a differing session location is ordinary.
    """
    repo = make_repo(tmp_path)
    victim = repo / "inside" / "mirror"
    victim.mkdir(parents=True)
    canary = victim / "canary.txt"
    canary.write_text("part of the tree under review\n")

    script = (
        f"Set-Location -LiteralPath '{repo.as_posix()}'; "
        f"& '{MIRROR.as_posix()}' -RepoRoot '{repo.as_posix()}' "
        "-MirrorPath 'inside/mirror' -Force -SkipProbe; "
        "exit $LASTEXITCODE"
    )
    proc = subprocess.run(
        [ps_host(), "-NoProfile", "-NonInteractive", "-Command", script],
        capture_output=True, text=True, cwd=str(tmp_path))

    assert canary.exists(), (
        "the guard approved one absolute path while the forced replacement"
        " destroyed another"
    )
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "inside the repo" in proc.stdout, proc.stdout + proc.stderr


def test_skipping_the_probe_is_not_a_passing_outcome(tmp_path):
    # Named explicitly rather than left implicit inside assert_built: an
    # unmade measurement must never share an exit code with a made one.
    repo = make_clean_repo(tmp_path)
    proc = run_mirror(repo, tmp_path / "mirror")
    assert proc.returncode == 1
    assert "not cleared for dispatch" in proc.stdout


# Non-ASCII pathnames. git returns a DISPLAY form for them unless
# `core.quotepath=false` is set: `café/AGENTS.md` comes back as
# `"caf\303\251/AGENTS.md"`. Verified live 2026-07-28 against both the
# enumeration and the status capture. Raised independently by two lanes of
# the mode-diff PANEL that day.
CAFE = "café"


def run_mirror_utf8(repo, mirror, *extra):
    """run_mirror, decoding stdout as UTF-8 rather than the locale.

    These cases assert PATHNAMES, so the test must not introduce a decoding
    step of its own that could hide, or invent, a mangled path.
    """
    proc = subprocess.run(
        [ps_host(), "-NoProfile", "-NonInteractive", "-File", str(MIRROR),
         "-RepoRoot", str(repo), "-MirrorPath", str(mirror),
         "-SkipProbe", *extra],
        capture_output=True)
    proc.stdout = proc.stdout.decode("utf-8", errors="replace")
    proc.stderr = proc.stderr.decode("utf-8", errors="replace")
    return proc


def test_a_non_ascii_back_channel_is_removed_not_left_behind(tmp_path):
    # With the display form treated as a path, the delete silently found
    # nothing, the re-enumeration still saw the entry, and the run stopped
    # with "back-channel(s) survived remediation" - which reads as a
    # back-channel that refused to go rather than as a name the script
    # could not resolve.
    repo = make_repo(tmp_path)
    (repo / CAFE).mkdir()
    (repo / CAFE / "AGENTS.md").write_text("# planted\n", encoding="utf-8")
    mirror = tmp_path / "mirror"
    proc = run_mirror_utf8(repo, mirror)
    assert "survived remediation" not in proc.stdout, proc.stdout
    assert_built(proc)
    assert not (mirror / CAFE / "AGENTS.md").exists()
    assert (repo / CAFE / "AGENTS.md").exists(), (
        "the real tree is never touched")


def test_a_non_ascii_baseline_entry_reaches_the_manifest(tmp_path):
    # The other consumer of the same capture. An unresolvable display form
    # stopped the build at "baseline path ... has no file behind it", so a
    # repo carrying any non-ASCII untracked or ignored file could not be
    # mirrored at all.
    repo = make_repo(tmp_path)
    (repo / CAFE).mkdir()
    body = b"subject material\n"
    (repo / CAFE / "input.txt").write_bytes(body)
    proc = run_mirror_utf8(repo, tmp_path / "mirror")
    assert_built(proc)
    expected = hashlib.sha256(body).hexdigest()
    assert f"{CAFE}/input.txt {expected}" in proc.stdout, proc.stdout
    assert f"?? {CAFE}/input.txt" in proc.stdout, proc.stdout


BODY_START = "function Invoke-GitProcess"
BODY_END = "$toplevel ="


def run_functions(snippet):
    """Dot-source the mirror script's function block, then run `snippet`.

    Same slicing the probe tests use. It exists here because git quotes a
    pathname containing a double quote, a backslash or a control character
    whatever `core.quotepath` says - and Windows permits none of those in a
    filename, so the guard for that residue cannot be reached by building a
    real repo.

    The block goes through a FILE, not `-Command`, for the same reason the
    probe's copy does: passed inline it outgrows the Windows command-line
    limit as the script gains rules, and the failure then looks like the
    code under test rather than like the harness. The BOM is what makes
    Windows PowerShell 5.1 read the file as UTF-8.
    """
    text = MIRROR.read_text(encoding="utf-8")
    body = text[text.index(BODY_START):text.index(BODY_END)]
    with tempfile.NamedTemporaryFile("w", suffix=".ps1", delete=False,
                                     encoding="utf-8-sig") as fh:
        # Stop on the FIRST error. Measured 2026-07-29 on both hosts: an
        # undefined function is NON-terminating here, the host exits 0, and
        # the snippet's partial output comes back - so a missing or
        # mistyped function reads as a wrong VALUE instead of an error.
        # These snippets exercise pathname handling; a quiet failure is the
        # one outcome this module must not produce.
        fh.write('$ErrorActionPreference = "Stop"\n' + body + "\n" + snippet)
        path = fh.name
    try:
        proc = subprocess.run(
            [ps_host(), "-NoProfile", "-NonInteractive", "-File", path],
            capture_output=True, text=True)
    finally:
        os.unlink(path)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return proc.stdout.strip()


def test_an_empty_capture_is_a_legitimate_state():
    # A repo with nothing to list produces no bytes. That is not a failure,
    # and the wrapper is what keeps it from reading as one.
    out = run_functions(
        '$r = ConvertFrom-NulCapture ([byte[]]@())\n'
        '"{0}|{1}" -f $r.Ok, (@($r.Fields).Count)')
    assert out == "True|0", out


def test_fields_split_on_nul_and_keep_their_spaces():
    # THE WHOLE POINT. A space in a pathname is what made git quote it, and
    # under -z the space is simply part of the field.
    out = run_functions(
        '$b = [System.Text.Encoding]::UTF8.GetBytes("M+ Timer/a.lua`0b.lua`0")\n'
        '$r = ConvertFrom-NulCapture $b\n'
        '(@($r.Fields) -join "|")')
    assert out == "M+ Timer/a.lua|b.lua", out


def test_a_capture_without_a_trailing_nul_stops():
    # A truncated capture ends mid-pathname. Accepting it would put a
    # fragment into the manifest under the name of a real file.
    out = run_functions(
        '$b = [byte[]]@(97, 46, 116, 120, 116)\n'
        '$r = ConvertFrom-NulCapture $b\n'
        '"{0}|{1}" -f $r.Ok, $r.Reason')
    assert out.startswith("False|"), out
    assert "does not end with a NUL" in out, out


def test_invalid_utf8_stops_instead_of_being_replaced():
    # The reason the bytes are read raw. PowerShell's own decode maps a
    # malformed byte to U+FFFD silently, which on this boundary is a wrong
    # pathname reported as a good one.
    out = run_functions(
        '$b = [byte[]]@(97, 255, 0)\n'
        '$r = ConvertFrom-NulCapture $b\n'
        '"{0}|{1}" -f $r.Ok, $r.Reason')
    assert out.startswith("False|"), out
    assert "not valid UTF-8" in out, out


def test_a_non_ascii_field_arrives_as_one_character_not_two_bytes():
    # THE DECODER DEFECT THIS CYCLE DELETES, pinned so it cannot return.
    # The old ConvertFrom-GitQuotedPath turned the ESCAPE PAIR
    # `\303\251` into character codes 195,169 - two characters -
    # where the byte pair names one, code 233. (The surrounding name
    # decoded normally: `caf\303\251` came out five characters, not
    # two. The two here are the escapes' own output.) Reading raw bytes
    # and decoding once from UTF-8 is what makes that impossible.
    out = run_functions(
        '$b = [byte[]]@(99, 97, 102, 195, 169, 0)\n'
        '$r = ConvertFrom-NulCapture $b\n'
        '(([int[]][char[]]$r.Fields[0]) -join ",")')
    assert out == "99,97,102,233", out


def test_an_empty_field_before_the_end_is_kept_for_the_parser_to_refuse():
    # Only the empty string AFTER the final NUL is dropped. An empty field
    # anywhere else is a real fault and must reach the caller rather than
    # being tidied away here.
    out = run_functions(
        '$b = [System.Text.Encoding]::UTF8.GetBytes("a.txt`0`0b.txt`0")\n'
        '$r = ConvertFrom-NulCapture $b\n'
        '"{0}|{1}" -f (@($r.Fields).Count), (@($r.Fields) -join ",")')
    assert out == "3|a.txt,,b.txt", out


def test_the_supported_pathname_guard_is_pinned_in_both_directions():
    # The guard admits exactly what Format-StatusPathname can record
    # exactly: an ordinary name, and a name whose ONLY quoting trigger is a
    # space. Everything the porcelain line form would quote or escape some
    # other way is refused, plus `>` for the arrow separator. Pinned in
    # both directions so a future edit cannot make the guard constant.
    out = run_functions(
        '$q = [char]34\n'
        '$results = @(\n'
        '  (Test-SupportedPathname "M+ Timer/core.lua"),\n'
        '  (Test-SupportedPathname "caf' + "é" + '/input.txt"),\n'
        '  (Test-SupportedPathname "a$([char]9)b.txt"),\n'
        '  (Test-SupportedPathname "a$([char]10)b.txt"),\n'
        '  (Test-SupportedPathname "a$([char]127)b.txt"),\n'
        '  (Test-SupportedPathname ("a" + $q + "b.txt")),\n'
        '  (Test-SupportedPathname "a\\b.txt"),\n'
        '  (Test-SupportedPathname "a>b.txt"),\n'
        '  (Test-SupportedPathname "")\n'
        ')\n'
        '($results -join ",")')
    assert out == ("True,True,False,False,False,"
                   "False,False,False,False"), out


def test_a_rename_record_reads_destination_first_then_source():
    # THE INVERSION. Measured 2026-07-29 against a real git: the line form
    # reads `R  <old> -> <new>`, and the same rename under -z reads
    # `R  <new>` NUL `<old>` NUL. A parse that carries the line form's order
    # across hashes and deletes the wrong file and says nothing.
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("R  M+ Timer/new name.lua",\n'
        '                              "M+ Timer/old name.lua")\n'
        '$rec = $r.Records[0]\n'
        '"{0}|{1}|[{2}{3}]" -f $rec.Path, $rec.Source, $rec.X, $rec.Y')
    assert out == "M+ Timer/new name.lua|M+ Timer/old name.lua|[R ]", out


def test_a_plain_entry_has_no_source_and_keeps_its_spaces():
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("?? untracked file.txt")\n'
        '$rec = $r.Records[0]\n'
        '"{0}|{1}" -f $rec.Path, ($null -eq $rec.Source)')
    assert out == "untracked file.txt|True", out


def test_a_rename_with_no_source_field_stops():
    # A truncated capture. The record claims a source that is not there.
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("R  new.lua"); $r.Error')
    assert "no source field" in out, out


def test_a_copy_in_the_second_column_also_consumes_a_source():
    # EITHER column can carry R or C, which is why both are tested.
    out = run_functions(
        '$r = ConvertTo-StatusRecord @(" C dest.lua", "src.lua")\n'
        '"{0}|{1}|{2}" -f $r.Records.Count, $r.Records[0].Path,'
        ' $r.Records[0].Source')
    assert out == "1|dest.lua|src.lua", out


def test_a_control_character_in_a_status_pathname_stops():
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("?? a$([char]9)b.txt"); $r.Error')
    assert "cannot handle" in out, out


def test_a_del_character_in_a_status_pathname_stops():
    # 0x7F is the case the guard's old name got wrong. Windows CREATES
    # `a<0x7F>b.txt` - measured 2026-07-29 - and `git status --porcelain`
    # prints it as `?? "a\177b.txt"` with and without core.quotepath=false,
    # while -z returns the byte raw. It is above the control range, so a
    # `< 32` test admits it, and the render would then record it bare where
    # the direct capture quotes it.
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("?? a$([char]127)b.txt"); $r.Error')
    assert "cannot handle" in out, out


def test_a_status_field_too_short_to_carry_a_pathname_stops():
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("?? "); $r.Error')
    assert "shorter than" in out, out


def test_a_status_field_with_no_space_after_the_code_stops():
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("??x.txt"); $r.Error')
    assert "no space where the status code ends" in out, out


def test_an_empty_status_field_stops():
    # ConvertFrom-NulCapture deliberately passes an interior empty field
    # through. This is where it is refused.
    out = run_functions(
        '$r = ConvertTo-StatusRecord @(""); $r.Error')
    assert "shorter than" in out, out


def test_a_rename_renders_in_gits_display_order_with_its_quoting():
    # The recorded baseline must stay byte-comparable with a capture taken
    # by running THE STATUS COMMAND directly, which is what
    # references/backup-lane.md requires of every round. Measured
    # 2026-07-29, that command prints both spaced names QUOTED. The arrow
    # is unambiguous because Test-SupportedPathname refuses `>`.
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("R  M+ Timer/new name.lua",\n'
        '                              "M+ Timer/old name.lua")\n'
        'Format-StatusRecord $r.Records[0]')
    assert out == ('R  "M+ Timer/old name.lua" -> "M+ Timer/new name.lua"'), out


def test_each_side_of_a_rename_is_quoted_independently():
    # Measured 2026-07-29: a spaced source with a plain destination prints
    # `R  "with space/a.lua" -> plain/a.lua`. Quoting the pair together, or
    # quoting both whenever either has a space, would both be wrong.
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("R  plain/a.lua",\n'
        '                              "with space/a.lua")\n'
        'Format-StatusRecord $r.Records[0]')
    assert out == 'R  "with space/a.lua" -> plain/a.lua', out


def test_a_plain_entry_renders_unquoted():
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("!! ignored/note.txt")\n'
        'Format-StatusRecord $r.Records[0]')
    assert out == "!! ignored/note.txt", out


def test_a_spaced_entry_renders_quoted():
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("!! ignored dir/note.txt")\n'
        'Format-StatusRecord $r.Records[0]')
    assert out == '!! "ignored dir/note.txt"', out


def test_a_non_ascii_entry_renders_unquoted():
    # The old captures set core.quotepath=false, so an accented pathname
    # was recorded RAW. This render must keep that shape rather than
    # introduce quoting the baseline never had.
    #
    # Asserted as CHARACTER CODES, not as a literal. run_functions decodes
    # the host's stdout with the locale, so comparing an accented literal
    # here would test the harness's decoding rather than the renderer. The
    # codes are 63,63,32 for "?? " then 99,97,102,233 for "caf" and the
    # accented letter.
    out = run_functions(
        '$e = [char]233\n'
        '$r = ConvertTo-StatusRecord @("?? caf$e.txt")\n'
        '$line = Format-StatusRecord $r.Records[0]\n'
        '(([int[]][char[]]$line) -join ",")')
    assert out == "63,63,32,99,97,102,233,46,116,120,116", out


def test_a_status_code_with_a_leading_space_survives_rendering():
    # ` M` and ` D` are ordinary porcelain codes. Trimming the render would
    # change what the record says happened.
    out = run_functions(
        '$r = ConvertTo-StatusRecord @(" M kept.txt")\n'
        '"[{0}]" -f (Format-StatusRecord $r.Records[0])')
    assert out == "[ M kept.txt]", out


# A path with a SPACE. This is the whole reason for the -z change: git
# quotes any pathname containing a space, the old capture refused every
# quoted entry, and a repo using the `References/<name with spaces>/`
# convention could not be mirrored at all. Measured 2026-07-29 against a
# throwaway repo, a directory named `M+ Timer` came back as `?? "M+ Timer/"`
# from `status --porcelain`, quoted for the space and nothing else.
SPACED = "M+ Timer"


def test_a_back_channel_under_a_spaced_directory_is_removed(tmp_path):
    repo = make_repo(tmp_path)
    (repo / SPACED).mkdir()
    (repo / SPACED / "AGENTS.md").write_text("# planted\n")
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror)
    assert "survived remediation" not in proc.stdout, proc.stdout
    assert_built(proc)
    assert not (mirror / SPACED / "AGENTS.md").exists()
    assert (repo / SPACED / "AGENTS.md").exists(), (
        "the real tree is never touched")


def test_a_tracked_back_channel_under_a_spaced_directory_is_committed(tmp_path):
    # The STAGING route, which the untracked case above never reaches. A
    # tracked back-channel is deleted, staged and committed, and a spaced
    # pathname is exactly what the old capture refused before it could get
    # here. Fail-closed either way - staging failure and survival both
    # block - but a route that only fails loudly is still a route that has
    # never been run.
    repo = make_repo(tmp_path)
    (repo / SPACED).mkdir()
    (repo / SPACED / "AGENTS.md").write_text("# planted\n")
    git(repo, "add", "--", f"{SPACED}/AGENTS.md")
    commit(repo, "plant a tracked back-channel under a spaced directory")
    before = git(repo, "rev-parse", "HEAD").strip()
    mirror = tmp_path / "mirror"
    proc = run_mirror(repo, mirror)
    assert "survived remediation" not in proc.stdout, proc.stdout
    assert_built(proc)
    assert not (mirror / SPACED / "AGENTS.md").exists()
    assert not (mirror / SPACED).exists(), (
        "the empty directory is pruned; an empty shell of the surface this"
        " step removes is not remediation")
    assert (repo / SPACED / "AGENTS.md").exists(), (
        "the real tree is never touched")
    after = git(mirror, "rev-parse", "HEAD").strip()
    assert after != before, (
        "a tracked deletion left uncommitted is a tracked modification in"
        " the baseline, which bars mode diff")
    assert "AGENTS.md" not in git(mirror, "status", "--porcelain")


def test_a_spaced_mirror_path_builds(tmp_path):
    # The paths this script is GIVEN can carry spaces too, not only the
    # pathnames it reads out of git. Four call sites still pass the repo as
    # `-C <path>` through PowerShell's native invocation rather than
    # through the byte capture, so this is the case that says whether that
    # residue holds: staging, the commit and `rev-parse` all run against a
    # spaced mirror here, and a failure in any of them blocks.
    repo = tmp_path / "src repo"
    repo.mkdir()
    git(tmp_path, "init", "-q", str(repo))
    (repo / "kept.txt").write_text("tracked\n")
    (repo / SPACED).mkdir()
    (repo / SPACED / "AGENTS.md").write_text("# planted\n")
    git(repo, "add", "kept.txt", "--", f"{SPACED}/AGENTS.md")
    commit(repo, "base")
    mirror = tmp_path / "mirror dir"
    proc = run_mirror(repo, mirror)
    assert_built(proc)
    assert not (mirror / SPACED / "AGENTS.md").exists()
    assert (mirror / "kept.txt").exists()
    assert git(mirror, "status", "--porcelain").strip() == "", (
        "the remediation commit landed, so the mirror is clean")


def test_a_spaced_baseline_entry_reaches_the_manifest(tmp_path):
    repo = make_repo(tmp_path)
    (repo / SPACED).mkdir()
    body = b"subject material\n"
    (repo / SPACED / "input.txt").write_bytes(body)
    proc = run_mirror(repo, tmp_path / "mirror")
    assert_built(proc)
    expected = hashlib.sha256(body).hexdigest()
    # The MANIFEST is unquoted and the BASELINE is quoted. Both shapes are
    # what the current script already records for a spaced path; run
    # 2026-07-29 it printed `?? "M+ Timer/input.txt"` under `baseline:` and
    # `M+ Timer/input.txt <sha256>` under `manifest:`.
    assert f"{SPACED}/input.txt {expected}" in proc.stdout, proc.stdout
    assert f'?? "{SPACED}/input.txt"' in proc.stdout, proc.stdout


def test_a_spaced_ignored_entry_reaches_the_manifest(tmp_path):
    # Ignored content is the entire reason this workspace is a mirror.
    repo = make_repo(tmp_path)
    (repo / ".gitignore").write_text("ignored/\nrefs with spaces/\n")
    git(repo, "add", ".gitignore")
    commit(repo, "ignore a spaced directory")
    (repo / "refs with spaces").mkdir()
    body = b"reference source\n"
    (repo / "refs with spaces" / "note.txt").write_bytes(body)
    proc = run_mirror(repo, tmp_path / "mirror")
    assert_built(proc)
    expected = hashlib.sha256(body).hexdigest()
    assert f"refs with spaces/note.txt {expected}" in proc.stdout, proc.stdout
    assert '!! "refs with spaces/note.txt"' in proc.stdout, proc.stdout


def test_a_rename_with_spaces_hashes_the_destination_not_the_source(tmp_path):
    # THE INVERSION, end to end. Under -z the destination arrives FIRST and
    # the source second, the opposite of the line form. A parse that keeps
    # the old order would hash the source, which no longer exists, and the
    # run would stop with the wrong reason - or worse, hash a file that
    # happens to be there.
    repo = make_repo(tmp_path)
    (repo / SPACED).mkdir()
    body = b"renamed content\n"
    (repo / SPACED / "old name.lua").write_bytes(body)
    git(repo, "add", "--", f"{SPACED}/old name.lua")
    commit(repo, "add the spaced file")
    git(repo, "mv", f"{SPACED}/old name.lua", f"{SPACED}/new name.lua")
    proc = run_mirror(repo, tmp_path / "mirror")
    assert_built(proc)
    expected = hashlib.sha256(body).hexdigest()
    assert f"{SPACED}/new name.lua {expected}" in proc.stdout, proc.stdout
    assert f"{SPACED}/old name.lua {expected}" not in proc.stdout, (
        "the source of a rename no longer exists; hashing it would be a"
        " hash of whatever happened to take its place")


def test_a_rename_renders_in_the_baseline_as_source_arrow_destination(tmp_path):
    # references/backup-lane.md describes the baseline as the status
    # command's output, and every earlier baseline reads `old -> new`. The
    # -z wire order is the opposite, so the render is what keeps two
    # captures comparable across this change.
    repo = make_repo(tmp_path)
    (repo / SPACED).mkdir()
    (repo / SPACED / "old name.lua").write_bytes(b"x\n")
    git(repo, "add", "--", f"{SPACED}/old name.lua")
    commit(repo, "add the spaced file")
    git(repo, "mv", f"{SPACED}/old name.lua", f"{SPACED}/new name.lua")
    proc = run_mirror(repo, tmp_path / "mirror")
    assert_built(proc)
    baseline = read_block(proc.stdout, "baseline:")
    assert (f'R  "{SPACED}/old name.lua" -> "{SPACED}/new name.lua"'
            in baseline), baseline


def test_escape_looking_field_text_is_never_interpreted():
    # `caf\303\251` is the exact string the deleted decoder mishandled.
    # On the quoted form it turned the 15 characters of
    # `caf\303\251.txt` into NINE: three ordinary, two produced by the
    # octal escapes, and four from `.txt`. Neither produced character is
    # the accented letter the real name holds.
    #
    # Under -z the bytes ARE the pathname, so the field must come back as
    # the 15 literal characters it is.
    #
    # This is a FIELD-level case and not an end-to-end one on purpose. A
    # file with this name cannot exist on Windows, because the backslash is
    # a path separator there - measured 2026-07-29. The bytes can still
    # arrive from git's INDEX, which is what Test-SupportedPathname then
    # refuses, so the two halves are tested where each can actually be
    # reached.
    out = run_functions(
        '$b = [System.Text.Encoding]::UTF8.GetBytes("caf\\303\\251.txt`0")\n'
        '$r = ConvertFrom-NulCapture $b\n'
        '"{0}|{1}" -f $r.Fields[0], $r.Fields[0].Length')
    assert out == "caf\\303\\251.txt|15", out


def test_uppercase_escape_looking_field_text_is_never_interpreted():
    # THE SECOND DECODER DEFECT, pinned so it cannot return. PowerShell's
    # `switch` is case-INSENSITIVE by default, so the deleted decoder turned
    # `a\Tb.txt` into a TAB and `a\Nb.txt` into a NEWLINE - escapes C-style
    # quoting leaves undefined. Under -z the bytes are the pathname, so both
    # must arrive as their eight literal characters.
    out = run_functions(
        '$b = [System.Text.Encoding]::UTF8.GetBytes("a\\Tb.txt`0a\\Nb.txt`0")\n'
        '$r = ConvertFrom-NulCapture $b\n'
        '(@($r.Fields | ForEach-Object { ([int[]][char[]]$_) -join "," })'
        ' -join "|")')
    # a \ T b . t x t  and  a \ N b . t x t
    assert out == ("97,92,84,98,46,116,120,116|"
                   "97,92,78,98,46,116,120,116"), out


def test_a_backslash_bearing_index_entry_stops_the_enumeration():
    # The other half. git reads names from its INDEX, which can carry a
    # name Windows cannot represent. Join-Path would read the backslash as
    # a separator and resolve a DIFFERENT file, which the script would then
    # delete or hash under the name the baseline gave.
    out = run_functions(
        '$r = ConvertTo-StatusRecord @("?? caf\\303\\251.txt"); $r.Error')
    assert "cannot handle" in out, out


# =====================================================================
# The path-budget pre-flight (0.21.0, backlog item 21).
#
# The mirror is a robocopy of the whole repo into a NEW root. If that
# root is deep, destinations that were fine in the source exceed what the
# tool will build, and the failure lands MID-COPY: a partially populated
# mirror that reads like a real one. The pre-flight moves that refusal to
# before anything is created.
#
# THE UNIVERSE IS FROZEN TEXT, converged by both reviewer lanes: every
# file and directory destination that the exact robocopy /E operation may
# create beneath the resolved mirror root, including tracked, untracked,
# ignored, and all .git content. Two cases below exist because narrower
# readings are tempting and wrong - a directory with no files in it is
# still a destination, and .git content is not excluded.
# =====================================================================

BUDGET = 260


def long_mirror(tmp_path):
    """A mirror root deliberately much LONGER than the source repo root.

    The source has to be creatable or the fixture measures Python's
    limits instead of the tool's: a destination at 280 characters built
    from a source root the same length needs a 280-character source,
    which `mkdir` refuses before the tool ever runs. `make_repo` uses
    `src`, so this name buys 37 characters of headroom.
    """
    return tmp_path / ("mirrorroot" * 4)


def deep_child(root, total_len, tail="f.txt"):
    """A path under `root` whose FULL length is exactly `total_len`,
    built from nested directories so no single component is
    unreasonable."""
    room = total_len - len(str(root)) - 1 - len(tail)
    assert room >= 2, "root already too long for this case"
    parts = []
    while room > 31:
        parts.append("d" * 29)
        room -= 30
    parts.append("d" * (room - 1))
    return root.joinpath(*parts) / tail


def budget_error(proc):
    """The refusal line, or None. Asserted on rather than a bare exit
    code: several conditions exit 2, and a test that could not tell them
    apart would pass against the wrong refusal."""
    for line in proc.stdout.splitlines():
        if "path budget" in line.lower():
            return line
    return None


def test_a_mirror_just_under_the_budget_builds(tmp_path):
    """The positive control. Without it every refusal below is satisfied
    by a tool that refuses everything."""
    repo = make_repo(tmp_path)
    mirror = long_mirror(tmp_path)
    target = deep_child(mirror, BUDGET - 1)
    src = repo / target.relative_to(mirror)
    src.parent.mkdir(parents=True)
    src.write_text("deep but legal\n")
    proc = run_mirror(repo, mirror)
    assert_built(proc)
    assert target.exists(), "a path one under the budget must be copied"


def test_a_mirror_at_the_budget_is_refused(tmp_path):
    repo = make_repo(tmp_path)
    mirror = long_mirror(tmp_path)
    src = repo / deep_child(mirror, BUDGET).relative_to(mirror)
    src.parent.mkdir(parents=True)
    src.write_text("exactly at the limit\n")
    proc = run_mirror(repo, mirror)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert budget_error(proc), proc.stdout


def test_the_refusal_names_every_number_it_used(tmp_path):
    """A refusal an operator cannot act on is a refusal they will
    override. It must show the root length, the deepest relative path
    length, their sum, and the limit."""
    repo = make_repo(tmp_path)
    mirror = long_mirror(tmp_path)
    deepest = deep_child(mirror, BUDGET + 20)
    src = repo / deepest.relative_to(mirror)
    src.parent.mkdir(parents=True)
    src.write_text("over\n")
    proc = run_mirror(repo, mirror)
    line = budget_error(proc)
    assert line, proc.stdout
    assert str(len(str(mirror))) in line, ("mirror-root length missing", line)
    assert str(len(str(deepest.relative_to(mirror)))) in line, (
        "deepest relative path length missing", line)
    assert str(BUDGET + 20) in line, ("the sum missing", line)
    assert str(BUDGET) in line, ("the limit missing", line)


def test_the_mirror_does_not_exist_after_a_refusal(tmp_path):
    """The whole point of a PRE-flight. A refusal that leaves a directory
    behind has already done part of the thing it refused to do."""
    repo = make_repo(tmp_path)
    mirror = long_mirror(tmp_path)
    src = repo / deep_child(mirror, BUDGET + 5).relative_to(mirror)
    src.parent.mkdir(parents=True)
    src.write_text("over\n")
    proc = run_mirror(repo, mirror)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert not mirror.exists(), "the pre-flight ran after creating the root"


def test_an_over_budget_directory_with_no_files_is_refused(tmp_path):
    """A DIRECTORY is a destination robocopy /E creates. Measuring only
    files reads this repo as fine and then fails mid-copy."""
    repo = make_repo(tmp_path)
    mirror = long_mirror(tmp_path)
    d = repo / deep_child(mirror, BUDGET + 8, tail="leafdir").relative_to(mirror)
    d.mkdir(parents=True)
    proc = run_mirror(repo, mirror)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert budget_error(proc), proc.stdout


def test_an_over_budget_path_under_dot_git_is_refused(tmp_path):
    """.git is copied, so .git counts. Skipping it is the narrower
    universe the frozen sentence rules out."""
    repo = make_repo(tmp_path)
    mirror = long_mirror(tmp_path)
    rel = deep_child(mirror / ".git", BUDGET + 8).relative_to(mirror / ".git")
    src = repo / ".git" / rel
    src.parent.mkdir(parents=True)
    src.write_text("git internals are destinations too\n")
    proc = run_mirror(repo, mirror)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert budget_error(proc), proc.stdout


def test_an_over_budget_override_path_is_refused(tmp_path):
    """-OverrideOut is written BESIDE the mirror by this tool, not by
    robocopy, so the copy universe never covers it. It gets its own
    check or it gets none."""
    repo = make_repo(tmp_path)
    mirror = long_mirror(tmp_path)
    override = deep_child(tmp_path, BUDGET + 4, tail="o.txt")
    # Deliberately NOT created. Windows caps directory creation at 248
    # characters, so a fixture that built this parent would measure
    # `mkdir`'s limit instead of the tool's, and the check under test
    # runs on the resolved string before anything touches disk.
    proc = run_mirror(repo, mirror, "-OverrideOut", str(override))
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert budget_error(proc), proc.stdout
    assert not mirror.exists()


def test_a_source_reparse_point_is_refused(tmp_path):
    """Refused BEFORE measuring, not measured through.

    Nothing here has established that the enumerator and robocopy
    traverse an identical universe across a reparse point, and a budget
    computed over a universe the copy does not share is not a
    measurement of the copy.
    """
    repo = make_repo(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "x.txt").write_text("linked\n")
    link = repo / "linked"
    rc = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(outside)],
                        capture_output=True, text=True)
    if rc.returncode != 0:
        pytest.skip("junction creation unavailable: " + rc.stderr)
    mirror = long_mirror(tmp_path)
    proc = run_mirror(repo, mirror)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "reparse" in proc.stdout.lower(), proc.stdout
    assert not mirror.exists()


def test_an_unreadable_source_path_blocks_rather_than_skips(tmp_path):
    """Hole semantics, the rule the manifest builder already states: a
    path that cannot be measured is not a path known to fit."""
    repo = make_repo(tmp_path)
    locked = repo / "locked"
    locked.mkdir()
    (locked / "inner.txt").write_text("x\n")
    user = os.environ.get("USERNAME") or ""
    if not user:
        pytest.skip("USERNAME not set; cannot build a deny ACE")
    # DENY LIST-DIRECTORY ONLY, never (RX).
    #
    # (RX) also denies ReadPermissions, and an explicit deny is evaluated
    # before the owner's implicit READ_CONTROL/WRITE_DAC. Measured
    # 2026-08-03: the ACE then cannot be read or removed, the directory
    # cannot be deleted, and the fixture leaks a permanently
    # undeletable tree into the temp directory on every run. (RD) blocks
    # the enumeration this case needs and leaves the ACE removable.
    deny = subprocess.run(
        ["icacls", str(locked), "/deny", user + ":(OI)(CI)(RD)"],
        capture_output=True, text=True)
    if deny.returncode != 0:
        pytest.skip("icacls deny unavailable: " + deny.stdout + deny.stderr)
    try:
        mirror = long_mirror(tmp_path)
        proc = run_mirror(repo, mirror)
        assert proc.returncode == 2, proc.stdout + proc.stderr
        assert "could not be enumerated" in proc.stdout.lower(), proc.stdout
        assert not mirror.exists()
    finally:
        undo = subprocess.run(["icacls", str(locked), "/remove:d", user],
                              capture_output=True, text=True)
        # Asserted, not fire-and-forget. A cleanup that silently failed is
        # how the first version of this case leaked.
        assert undo.returncode == 0, undo.stdout + undo.stderr
        assert (locked / "inner.txt").exists(), "the deny ACE is still in force"
