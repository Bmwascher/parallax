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
# sequence and for the coverage cost this skip accepts.
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
    paths = [line.split(" ", 1)[0]
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
    paths = [line.split(" ", 1)[0] for line in manifest]
    assert paths == sorted(paths), "sorted by path in byte order"
    for line in manifest:
        path, digest = line.split(" ", 1)
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
    paths = [line.split(" ", 1)[0]
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


def test_a_quoted_baseline_entry_stops_instead_of_being_unquoted(tmp_path):
    # THE SILENT ONE. Trimming the delimiters leaves the escapes, Windows
    # reads the backslashes as separators, and a colliding real path is
    # hashed under the name the baseline gave. That is false coverage
    # rather than a refusal, which is why this entry shape is a stop.
    out = run_functions(
        '$r = Get-ManifestSubject @(' + "'" + '?? "caf\\303\\251/input.txt"'
        + "'" + '); $r.Error')
    assert "quoted form" in out, out
    assert "guessing at the escape sequences" in out, out


def test_the_quoted_form_is_recognized_and_a_plain_path_is_not():
    # The predicate both guards share, pinned in both directions so a
    # future edit cannot make it constant.
    out = run_functions(
        '"{0} {1}" -f (Test-GitQuotedPath ' + "'" + '"a/b"' + "'" +
        '), (Test-GitQuotedPath ' + "'" + 'a/b' + "'" + ')')
    assert out == "True False", out


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
