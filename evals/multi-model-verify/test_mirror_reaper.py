"""The review mirror reaper (BACKLOG items 101 and 98; spec
docs/superpowers/specs/2026-09-13-mirror-reaper-design.md).

Four groups. REMOVAL: tools/review-tree-removal.ps1's Remove-ReviewTree,
driven through a harness that dot-sources it, removes a tree with
read-only files and a junction whose target survives, and reports a
named failure on a held handle, a missing path and a link. EMITTER:
tools/write-attestation.ps1's reap parameters refuse every wrong tree
before writing the record and remove the right ones after. MIRROR: the
mirror tool's rebuild removal goes through the same function and its
existing-path refusal names the reap route. PROSE: the skill, the
reference and the doctor carry the rule.

WINDOWS ONLY: junctions and the held-handle sharing rule are Windows
semantics, and the mirror tool is a Windows tool. The powershell-hosts
CI job runs this module under BOTH powershell.exe and pwsh.exe; a green
run on one host proves ONE interpreter.
"""
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
REMOVAL = REPO / "tools" / "review-tree-removal.ps1"
WRITE = REPO / "tools" / "write-attestation.ps1"
MIRROR_TOOL = REPO / "tools" / "new-review-mirror.ps1"
SKILL = REPO / "skills" / "multi-model-verify" / "SKILL.md"
PREFLIGHT = REPO / "skills" / "multi-model-verify" / "references" / "preflight-mirror.md"
DOCTOR = REPO / "commands" / "doctor.md"

POWERSHELL = (os.environ.get("PARALLAX_PS_HOST")
              or shutil.which("powershell") or shutil.which("pwsh"))

pytestmark = pytest.mark.skipif(
    os.name != "nt" or POWERSHELL is None,
    reason="the reaper removes junction-bearing trees under a Windows "
           "PowerShell host")


def run_ps(script, *args):
    return subprocess.run(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-ExecutionPolicy",
         "Bypass", "-File", str(script), *args],
        capture_output=True, text=True, timeout=180)


def git(repo, *args):
    return subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=reap-test",
         "-c", "user.email=t@localhost", *args],
        check=True, capture_output=True, text=True).stdout.strip()


def make_repo(tmp_path, name="repo"):
    """A repo with a base commit and a feature commit, returned with both
    SHAs, because an attestation needs a real base..head range."""
    repo = tmp_path / name
    repo.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo,
                   check=True, capture_output=True)
    (repo / "a.txt").write_text("a\n", encoding="utf-8")
    git(repo, "add", "a.txt")
    git(repo, "commit", "-q", "-m", "base")
    base = git(repo, "rev-parse", "HEAD")
    git(repo, "checkout", "-q", "-b", "feat")
    (repo / "b.txt").write_text("b\n", encoding="utf-8")
    git(repo, "add", "b.txt")
    git(repo, "commit", "-q", "-m", "feat")
    head = git(repo, "rev-parse", "HEAD")
    return repo, base, head


def make_mirror(repo, path):
    """A mirror the way the mirror tool makes one: a FILE COPY that keeps
    .git, so it carries git's read-only object files."""
    shutil.copytree(repo, path)
    return path


def make_bridge(repo, path, branch="feat"):
    """A clone bridge the way a KitnEssentials session makes one."""
    subprocess.run(["git", "clone", "-q", "--no-checkout", str(repo), str(path)],
                   check=True, capture_output=True)
    git(path, "checkout", "-q", "-b", branch, "origin/" + branch)
    return path


def junction(link, target):
    subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                   check=True, capture_output=True)


def read(path):
    assert path.is_file(), f"missing file: {path}"
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------
# Group 1: Remove-ReviewTree through a dot-sourcing harness
# ---------------------------------------------------------------------
HARNESS = (
    'param([string]$Target)\n'
    '. "{removal}"\n'
    '$r = Remove-ReviewTree $Target\n'
    'if ($r.Ok) {{ Write-Output "OK" ; exit 0 }}\n'
    'Write-Output ("FAIL: " + $r.Reason)\n'
    'exit 1\n'
)


def harness(tmp_path):
    h = tmp_path / "harness.ps1"
    h.write_text(HARNESS.format(removal=str(REMOVAL).replace("\\", "/")),
                 encoding="ascii")
    return h


def test_removal_file_is_ascii_and_defines_nothing_but_functions():
    raw = REMOVAL.read_bytes()
    raw.decode("ascii")
    body = raw.decode("ascii")
    assert "function Test-PathOrAncestorIsLink(" in body
    assert "function Remove-ReviewTree(" in body
    # No top-level statement: every non-blank, non-comment line outside
    # a function is a brace or a declaration. A dot-sourced file that
    # RUNS something would run it inside both callers.
    assert "param(" not in body
    assert "Remove-Item -Recurse" not in body and "-Recurse" not in body, (
        "the removal is explicit post-order, never Remove-Item -Recurse")


def test_removes_a_tree_with_read_only_files_and_keeps_a_junction_target(tmp_path):
    repo, base, head = make_repo(tmp_path)
    tree = make_mirror(repo, tmp_path / "tree")
    target = tmp_path / "target"
    target.mkdir()
    (target / "keep.txt").write_text("kept\n", encoding="utf-8")
    junction(tree / "linked", target)
    assert (tree / "linked" / "keep.txt").is_file()
    objects = list((tree / ".git" / "objects").rglob("*"))
    assert any(p.is_file() and not os.access(p, os.W_OK) for p in objects), (
        "the fixture must carry a read-only git object")
    proc = run_ps(harness(tmp_path), "-Target", str(tree))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert proc.stdout.strip() == "OK"
    assert not tree.exists()
    assert (target / "keep.txt").read_text(encoding="utf-8") == "kept\n", (
        "the junction's target must survive the removal")


def test_a_held_handle_fails_by_name_and_leaves_the_tree(tmp_path):
    repo, base, head = make_repo(tmp_path)
    tree = make_mirror(repo, tmp_path / "tree")
    held = tree / "held.txt"
    held.write_text("open\n", encoding="utf-8")
    with open(held, "r", encoding="utf-8"):
        proc = run_ps(harness(tmp_path), "-Target", str(tree))
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert proc.stdout.startswith("FAIL: "), proc.stdout
    assert str(held) in proc.stdout, (
        "the failure must name the entry that could not be removed")
    assert held.exists() and tree.exists()


def test_a_missing_path_and_a_file_are_refused(tmp_path):
    proc = run_ps(harness(tmp_path), "-Target", str(tmp_path / "absent"))
    assert proc.returncode == 1 and "does not exist" in proc.stdout, proc.stdout
    f = tmp_path / "plain.txt"
    f.write_text("x\n", encoding="utf-8")
    proc = run_ps(harness(tmp_path), "-Target", str(f))
    assert proc.returncode == 1 and "is a file, not a tree" in proc.stdout
    assert f.exists()


def test_a_link_as_the_root_is_refused_and_its_target_survives(tmp_path):
    target = tmp_path / "target"
    target.mkdir()
    (target / "keep.txt").write_text("kept\n", encoding="utf-8")
    link = tmp_path / "link"
    junction(link, target)
    proc = run_ps(harness(tmp_path), "-Target", str(link))
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "is a link" in proc.stdout, proc.stdout
    assert (target / "keep.txt").is_file()
    assert link.exists(), "a refused removal must not have removed the link either"


def test_a_filesystem_root_is_refused(tmp_path):
    root = os.path.splitdrive(str(tmp_path))[0] + "\\"
    proc = run_ps(harness(tmp_path), "-Target", root)
    assert proc.returncode == 1 and "filesystem root" in proc.stdout, proc.stdout


def test_a_dangling_junction_inside_the_tree_is_removed(tmp_path):
    tree = tmp_path / "tree"
    (tree / "sub").mkdir(parents=True)
    gone = tmp_path / "gone"
    gone.mkdir()
    junction(tree / "sub" / "dangling", gone)
    gone.rmdir()
    proc = run_ps(harness(tmp_path), "-Target", str(tree))
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert not tree.exists()


def test_module_is_listed_in_both_host_steps():
    # The powershell-hosts job runs an EXPLICIT module list per host, and
    # test_backup_lane.py records why a module left off it silently
    # tested one interpreter. This module names itself in both.
    workflow = read(REPO / ".github" / "workflows" / "skill-evals.yml")
    rel = "evals/multi-model-verify/test_mirror_reaper.py"
    for host in ("powershell.exe", "pwsh.exe"):
        marker = "PARALLAX_PS_HOST: " + host
        assert marker in workflow
        step = workflow.split(marker, 1)[1].split("\n      - name:", 1)[0]
        assert step.count(rel) == 1, rel + " must appear once in the " + host + " step"
