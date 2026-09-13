# Mirror Reaper Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A review mirror (and the clone bridge a worktree needed) is removed at the one terminal event the plugin already records, the attestation, through a removal that never recurses through a link and terminates with a named error; the mirror tool's own rebuild removal goes through the same function (item 98); the doctor reports the `kv*` inventory and never deletes.

**Architecture:** One dot-sourced function file, `tools/review-tree-removal.ps1`, holds the mirror tool's existing directory-link guard (moved, not copied) and the new explicit post-order removal `Remove-ReviewTree`. `tools/write-attestation.ps1` gains `-ReapMirror` and `-ReapBridge`, validates both against the reviewed repo and the attested head BEFORE writing the record, and removes them AFTER. `tools/new-review-mirror.ps1` uses the same function for `-Force` and names the reap route in its existing-path refusal. `commands/doctor.md` gains an inventory check. A new pytest module drives all of it under both PowerShell hosts.

**Tech Stack:** PowerShell 5.1 and 7 (ASCII-only tools), Python 3 pytest evals, GitHub Actions `powershell-hosts` job.

**Spec:** `docs/superpowers/specs/2026-09-13-mirror-reaper-design.md`. Backlog items 106 (filed) and 98 (paired).

## Global Constraints

- Tools under `tools/` are ASCII ONLY and run under BOTH Windows PowerShell 5.1 and PowerShell 7. Never run a native `git` call under `$ErrorActionPreference = 'Stop'`; read `$LASTEXITCODE` yourself.
- `SKILL.md` is at 6496 of `skill_lint.py`'s 6500-token ceiling (`len(body) // 4` over the frontmatter-stripped body; 25987 characters measured 2026-09-13, so 13 characters of headroom). Task 4 makes EXACTLY the edits it quotes in that file. After every SKILL.md edit run `python evals/tools/skill_lint.py skills/multi-model-verify --strict`; an ERROR line means STOP and report, never trim other text.
- Do not reflow any existing paragraph in `skills/`, `agents/` or `commands/`: raw-text pins in `evals/` break on a rewrap. Insert whole new paragraphs or sections; edit only the sentences a task quotes.
- Stage by explicit path (`git add <file> <file>`); `git add -A` is refused by the family git guard. Commit messages are lowercase imperative, no AI attribution, and must not contain a token that looks like a PowerShell flag (write "the reap mirror parameter", never `-ReapMirror`, in a commit message).
- New tests select the host through `PARALLAX_PS_HOST` and skip off Windows, the way `evals/multi-model-verify/test_review_mirror.py:44-52` does. Before calling a task done, run its PowerShell-facing module under BOTH hosts: in PowerShell, `$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest <module> -q` and then the same with `"pwsh.exe"`.
- Never touch the ten directories `C:\kv-*` and `C:\kvs-*` that exist on this machine; every test builds its own trees under pytest's `tmp_path`.
- The worktree is `C:\Users\Brandon\Documents\_worktrees\parallax-mirror-reaper` on branch `mirror-reaper`; run every command from there. The primary checkout at `C:\Users\Brandon\Documents\parallax` belongs to another session: never write there.
- Full gate before the final commit of the branch (the session runs it, not a task): the six CI commands in `CLAUDE.md`.

---

### Task 1: The shared removal file and its tests

**Files:**
- Create: `tools/review-tree-removal.ps1`
- Create: `evals/multi-model-verify/test_mirror_reaper.py`
- Modify: `.github/workflows/skill-evals.yml` (both host steps' module lists)

**Interfaces:**
- Produces: `Test-PathOrAncestorIsLink($path)` returning the offending path or `$null` (verbatim from the mirror tool; on a read error it prints `ERROR:` and exits 2, as it does today). `Remove-ReviewTree($root)` returning `@{ Ok = $true }` or `@{ Ok = $false; Reason = <string> }`, never exiting the caller. Both are defined by dot-sourcing the file: `. (Join-Path $PSScriptRoot "review-tree-removal.ps1")`.
- Produces: the test module with helpers `run_ps(script, *args)`, `git(repo, *args)`, `make_repo(tmp_path)`, `make_mirror(repo, path)`, `make_bridge(repo, path, branch)`, `junction(link, target)`, `REPO`, `REMOVAL`, `WRITE`, `MIRROR_TOOL`, `POWERSHELL`, that Tasks 2 to 4 extend.

- [ ] **Step 1: Write the failing tests**

Create `evals/multi-model-verify/test_mirror_reaper.py`:

```python
"""The review mirror reaper (BACKLOG items 106 and 98; spec
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
```

- [ ] **Step 2: Run the module and confirm it fails on the missing file**

Run: `python -m pytest evals/multi-model-verify/test_mirror_reaper.py -q`
Expected: FAIL; the first failure is `test_removal_file_is_ascii_and_defines_nothing_but_functions` with `FileNotFoundError` on `review-tree-removal.ps1`, and the harness cases fail because the dot-source finds no file.

- [ ] **Step 3: Write the removal file**

Create `tools/review-tree-removal.ps1` with exactly this content. The `Test-PathOrAncestorIsLink` body is the mirror tool's function at `tools/new-review-mirror.ps1:1791-1819`, copied VERBATIM (Task 2 deletes the original):

```powershell
# review-tree-removal.ps1 - the one removal path for a review tree, and
# the directory-link guard both callers run before it.
#
# DOT-SOURCED, never run:
#   . (Join-Path $PSScriptRoot "review-tree-removal.ps1")
# from tools/new-review-mirror.ps1 (the -Force rebuild, backlog item 98)
# and tools/write-attestation.ps1 (the reap after a terminal verdict,
# backlog item 106). It defines functions and executes nothing else, so
# dot-sourcing it has no effect until a caller calls one.
#
# Windows PowerShell 5.1 compatible, ASCII ONLY.

function Test-PathOrAncestorIsLink($path) {
    # The path itself, then each existing ancestor up to the drive root:
    # is any of them a reparse point? Attributes are read directly
    # rather than after a Test-Path, because a DANGLING junction is a
    # reparse point Test-Path may report as absent; a missing entry is
    # the one condition that skips a level, and it is recognised by the
    # exception type, never by a false from a helper. Returns the
    # offending path or $null.
    $probe = ([string]$path).TrimEnd("\", "/")
    while ($probe -and -not [string]::IsNullOrEmpty([System.IO.Path]::GetFileName($probe))) {
        $pa = 0
        $missing = $false
        try {
            $pa = [int][System.IO.File]::GetAttributes($probe)
        } catch [System.IO.FileNotFoundException] {
            $missing = $true
        } catch [System.IO.DirectoryNotFoundException] {
            $missing = $true
        } catch {
            Write-Output ("ERROR: " + $probe + " could not be read while" +
                " checking for a directory link: " + $_.Exception.Message)
            exit 2
        }
        if (-not $missing -and (($pa -band [int][System.IO.FileAttributes]::ReparsePoint) -ne 0)) {
            return $probe
        }
        $probe = [System.IO.Path]::GetDirectoryName($probe)
    }
    return $null
}

function Remove-ReviewTreeEntries($dir, $depth) {
    # Empties $dir in post-order. Returns $null when every entry beneath
    # it is gone, else the reason, which names the entry that stopped it.
    #
    # NEVER THROUGH A LINK. A directory link is removed with the
    # non-recursive Directory.Delete and a file link with File.Delete;
    # both remove the link and never its target. Measured 2026-09-13 on
    # Windows PowerShell 5.1 and PowerShell 7, intact and dangling. An
    # ordinary directory is emptied by this walk and then removed with
    # the same non-recursive Directory.Delete, which throws when
    # anything survived, so a partial removal cannot read as a whole
    # one. An ordinary file has its read-only bit cleared first, because
    # git marks its object files read-only and File.Delete refuses them
    # as they are (measured the same day).
    if ($depth -gt 128) {
        return ($dir + " sits deeper than 128 levels; the walk stops" +
            " rather than assume the tree ends")
    }
    $entries = $null
    try {
        $entries = [System.IO.Directory]::GetFileSystemEntries($dir)
    } catch {
        return ($dir + " could not be listed: " + $_.Exception.Message)
    }
    foreach ($entry in $entries) {
        $ea = 0
        try {
            $ea = [int][System.IO.File]::GetAttributes($entry)
        } catch {
            return ($entry + " could not be examined: " + $_.Exception.Message)
        }
        $isDir = (($ea -band [int][System.IO.FileAttributes]::Directory) -ne 0)
        $isLink = (($ea -band [int][System.IO.FileAttributes]::ReparsePoint) -ne 0)
        try {
            if ($isLink) {
                if ($isDir) {
                    [System.IO.Directory]::Delete($entry)
                } else {
                    [System.IO.File]::Delete($entry)
                }
            } elseif ($isDir) {
                $inner = Remove-ReviewTreeEntries $entry ($depth + 1)
                if ($null -ne $inner) { return $inner }
                [System.IO.Directory]::Delete($entry)
            } else {
                if (($ea -band [int][System.IO.FileAttributes]::ReadOnly) -ne 0) {
                    [System.IO.File]::SetAttributes($entry, [System.IO.FileAttributes]::Normal)
                }
                [System.IO.File]::Delete($entry)
            }
        } catch {
            return ($entry + " could not be removed: " + $_.Exception.Message)
        }
    }
    return $null
}

function Remove-ReviewTree($root) {
    # Removes the tree at $root. Returns @{ Ok = $true }, or
    # @{ Ok = $false; Reason = <text> } the moment any step fails, with
    # the entry that failed named in the reason. It never exits the
    # caller and never writes output, so the caller decides what a
    # failure costs: the mirror tool refuses to build, the emitter
    # reports a written attestation with an unreaped tree.
    #
    # The root's OWN guards are here; the caller runs the ancestor-link
    # guard (Test-PathOrAncestorIsLink) and its overlap comparisons
    # before ever reaching this, because those are refusals that must
    # cost nothing, while this runs after the emitter has written.
    $full = $null
    try {
        $full = [System.IO.Path]::GetFullPath([string]$root).TrimEnd("\")
    } catch {
        return @{ Ok = $false; Reason = ("the path could not be resolved (" +
            $root + "): " + $_.Exception.Message) }
    }
    $pathRoot = $null
    try {
        $pathRoot = [System.IO.Path]::GetPathRoot($full)
    } catch {
        return @{ Ok = $false; Reason = ("the path has no root (" + $full +
            "): " + $_.Exception.Message) }
    }
    if ((-not $pathRoot) -or ($full.Length -le ([string]$pathRoot).TrimEnd("\").Length)) {
        return @{ Ok = $false; Reason = ($full + " is a filesystem root and" +
            " is never removed") }
    }
    $attr = 0
    try {
        $attr = [int][System.IO.File]::GetAttributes($full)
    } catch [System.IO.FileNotFoundException] {
        return @{ Ok = $false; Reason = ($full + " does not exist") }
    } catch [System.IO.DirectoryNotFoundException] {
        return @{ Ok = $false; Reason = ($full + " does not exist") }
    } catch {
        return @{ Ok = $false; Reason = ($full + " could not be examined: " +
            $_.Exception.Message) }
    }
    if (($attr -band [int][System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        return @{ Ok = $false; Reason = ($full + " is a link, and a tree is" +
            " never removed through a link") }
    }
    if (($attr -band [int][System.IO.FileAttributes]::Directory) -eq 0) {
        return @{ Ok = $false; Reason = ($full + " is a file, not a tree") }
    }
    $failure = Remove-ReviewTreeEntries $full 0
    if ($null -ne $failure) {
        return @{ Ok = $false; Reason = $failure }
    }
    try {
        [System.IO.Directory]::Delete($full)
    } catch {
        return @{ Ok = $false; Reason = ($full + " could not be removed: " +
            $_.Exception.Message) }
    }
    # THE POSTCONDITION, read back rather than inferred from the absence
    # of an exception. Item 98 is a removal that checked nothing after.
    try {
        [void][System.IO.File]::GetAttributes($full)
    } catch [System.IO.FileNotFoundException] {
        return @{ Ok = $true }
    } catch [System.IO.DirectoryNotFoundException] {
        return @{ Ok = $true }
    } catch {
        return @{ Ok = $false; Reason = ($full + " could not be re-examined" +
            " after removal: " + $_.Exception.Message) }
    }
    return @{ Ok = $false; Reason = ($full + " still exists after removal") }
}
```

- [ ] **Step 4: List the module in both CI host steps**

In `.github/workflows/skill-evals.yml`, in the step whose env sets `PARALLAX_PS_HOST: powershell.exe` AND in the step whose env sets `PARALLAX_PS_HOST: pwsh.exe`, add the line `evals/multi-model-verify/test_mirror_reaper.py` immediately after the line `evals/multi-model-verify/test_artifact_roots.py` in each list, keeping the trailing `-q` on the last entry. Then run `python evals/tools/check_workflow_paths.py` and expect a clean exit.

- [ ] **Step 5: Run the module under both hosts**

Run (PowerShell): `$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_mirror_reaper.py -q` then `$env:PARALLAX_PS_HOST = "pwsh.exe"; python -m pytest evals/multi-model-verify/test_mirror_reaper.py -q`
Expected: all 8 cases PASS on both.

- [ ] **Step 6: Commit**

```bash
git add tools/review-tree-removal.ps1 evals/multi-model-verify/test_mirror_reaper.py .github/workflows/skill-evals.yml
git commit -m "add the shared review tree removal: explicit post-order, never through a link, named failure, root re-examined"
```

---

### Task 2: The mirror tool removes through the shared function and names the reap route (item 98)

**Files:**
- Modify: `tools/new-review-mirror.ps1:97` (after the `[Console]::OutputEncoding` line), `:1791-1819` (the function to delete), `:2015-2020` (the existing-path block)
- Modify: `evals/multi-model-verify/test_review_mirror.py` (append two cases at the end of the file)

**Interfaces:**
- Consumes: `Test-PathOrAncestorIsLink` and `Remove-ReviewTree` from `tools/review-tree-removal.ps1` (Task 1).
- Produces: the refusal text `A finished debate reaps it through write-attestation.ps1 -ReapMirror` and the failure text `ERROR: the existing mirror could not be removed:`, both pinned by Task 4's prose tests and by the cases below.

- [ ] **Step 1: Write the failing tests**

Append to `evals/multi-model-verify/test_review_mirror.py`:

```python
def test_an_existing_mirror_refusal_names_the_reap_route_not_force_first(tmp_path):
    # Backlog item 106: the count grew because this refusal suggested
    # -Force and a session that did not want an in-place rebuild built
    # kv-<tag>-2 beside the first. The reap route comes first now, and
    # -Force is named as the mid-debate rebuild it is.
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    mirror.mkdir()
    (mirror / "stale.txt").write_text("from a previous debate\n")
    proc = run_mirror(repo, mirror)
    assert proc.returncode == 2
    assert "already exists" in proc.stdout
    assert ("A finished debate reaps it through write-attestation.ps1"
            " -ReapMirror") in proc.stdout, proc.stdout
    assert proc.stdout.index("-ReapMirror") < proc.stdout.index("-Force"), (
        "the reap route is named before the rebuild flag")
    assert (mirror / "stale.txt").exists()


def test_a_force_rebuild_whose_removal_fails_terminates_by_name_before_creating_anything(tmp_path):
    # Backlog item 98. The old removal was `Remove-Item -Recurse -Force`
    # with nothing checked after it, so a held handle left the stale
    # tree in place and the copy merged over it. This drives a REAL
    # removal failure - a handle this process holds open - not a
    # simulated one.
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    mirror.mkdir()
    held = mirror / "held.txt"
    held.write_text("open\n")
    with open(held, "r"):
        proc = run_mirror(repo, mirror, "-Force")
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "ERROR: the existing mirror could not be removed:" in proc.stdout, proc.stdout
    assert str(held) in proc.stdout, "the failure names the entry that stopped it"
    assert held.exists()
    assert not (mirror / "kept.txt").exists(), (
        "construction must terminate before the copy, so nothing from the"
        " source may have landed over the stale tree")
```

- [ ] **Step 2: Run them and confirm both fail**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -q -k "reap_route or removal_fails"`
Expected: FAIL. The first on the missing `-ReapMirror` text; the second because the old removal continues into the copy (`kept.txt` lands) or exits with a different message.

- [ ] **Step 3: Dot-source the shared file**

In `tools/new-review-mirror.ps1`, immediately after the line
`[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)`
insert:

```powershell

# The directory-link guard and the tree removal are shared with the
# attestation emitter's reap (backlog item 106) and live in one file so
# the two tools cannot drift apart on either. Functions only; nothing
# runs at dot-source time.
. (Join-Path $PSScriptRoot "review-tree-removal.ps1")
```

- [ ] **Step 4: Delete the local copy of the guard**

Delete lines `function Test-PathOrAncestorIsLink($path) {` through its closing `}` (the block at `tools/new-review-mirror.ps1:1791-1819`, ending with `    return $null` and `}`). Keep the comment paragraph above it (`# LINK TARGETS ARE PROTECTED TREES. ...` through `# compared. This runs before anything is created or deleted.`) and append one line to that paragraph:

```powershell
# The helper itself is Test-PathOrAncestorIsLink in review-tree-removal.ps1.
```

- [ ] **Step 5: Replace the existing-path block**

Replace exactly this block:

```powershell
if (Test-Path -LiteralPath $MirrorPath) {
    if (-not $Force) {
        Write-Output ("ERROR: $MirrorPath already exists - a stale mirror" +
            " reads exactly like a fresh one. Pass -Force to replace it.")
        exit 2
    }
    Remove-Item -LiteralPath $MirrorPath -Recurse -Force
}
```

with:

```powershell
if (Test-Path -LiteralPath $MirrorPath) {
    if (-not $Force) {
        Write-Output ("ERROR: $MirrorPath already exists - a stale mirror" +
            " reads exactly like a fresh one. A finished debate reaps it" +
            " through write-attestation.ps1 -ReapMirror; pass -Force only" +
            " to rebuild it in place for a debate that is still running.")
        exit 2
    }
    # ITEM 98. The removal used to be `Remove-Item -Recurse -Force` with
    # nothing checked after it: a locked file, a denied ACE or a handle
    # held by another process left the tree partly intact, execution
    # reached New-Item, and robocopy /E merged the source over what
    # survived. Now the shared removal walks the tree itself, stops on
    # the first failure with the entry named, and re-examines the root;
    # a failure terminates construction here, before anything is created
    # or copied.
    $removed = Remove-ReviewTree $MirrorPath
    if (-not $removed.Ok) {
        Write-Output ("ERROR: the existing mirror could not be removed: " +
            $removed.Reason + " - construction stopped before anything" +
            " was created or copied")
        exit 2
    }
}
```

- [ ] **Step 6: Run the whole mirror module under both hosts**

Run (PowerShell): `$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_review_mirror.py -q` then with `"pwsh.exe"`.
Expected: every case PASS on both, including `test_force_replaces_an_existing_mirror` and the three `already exists` cases that predate this task.

- [ ] **Step 7: Commit**

```bash
git add tools/new-review-mirror.ps1 evals/multi-model-verify/test_review_mirror.py
git commit -m "route the mirror rebuild removal through the shared function and name the reap route in the existing-path refusal, item 98"
```

---

### Task 3: The emitter reaps at the terminal event

**Files:**
- Modify: `tools/write-attestation.ps1` (header comment, param block, a new function after `Resolve-FullSha`, validation before `$attDir` is created, reap after the `attestation written:` line)
- Modify: `evals/multi-model-verify/test_mirror_reaper.py` (append group 2)

**Interfaces:**
- Consumes: `Test-PathOrAncestorIsLink`, `Remove-ReviewTree` (Task 1).
- Produces: parameters `-ReapMirror <path>` and `-ReapBridge <path>`, both optional strings; exit `3` meaning "attestation written, reap failed"; stdout lines `reaped mirror: <path>`, `reaped bridge: <path>`, `reaped sidecar: <path>`, and `ERROR: reap failed for <path>: <reason> - the attestation stands; remove the <label> by hand`. Every refusal before the write starts with `ERROR:` and exits `2`.

- [ ] **Step 1: Write the failing tests**

Append to `evals/multi-model-verify/test_mirror_reaper.py`:

```python
# ---------------------------------------------------------------------
# Group 2: the emitter's reap
# ---------------------------------------------------------------------
def attest(repo, base, head, mirror=None, bridge=None):
    args = [WRITE, "-RepoRoot", str(repo), "-BaseSha", base, "-HeadSha", head,
            "-Verdict", "PASS", "-VerificationStatus", "FULL",
            "-RouteNote", "effective route confirmed", "-Rounds", "1",
            "-Participants", "session/reviewer"]
    if mirror is not None:
        args += ["-ReapMirror", str(mirror)]
    if bridge is not None:
        args += ["-ReapBridge", str(bridge)]
    return run_ps(*args)


def att_file(repo, head):
    return repo / ".git" / "parallax" / "attestations" / (head + ".json")


def test_reaps_mirror_bridge_and_sidecar_after_writing(tmp_path):
    repo, base, head = make_repo(tmp_path)
    bridge = make_bridge(repo, tmp_path / "kvs-t")
    mirror = make_mirror(bridge, tmp_path / "kv-t")
    sidecar = tmp_path / "kv-t.source-manifest"
    sidecar.write_text("advisory\n", encoding="utf-8")
    target = tmp_path / "reference"
    target.mkdir()
    (target / "keep.txt").write_text("kept\n", encoding="utf-8")
    junction(mirror / ".wow-api-reference", target)
    proc = attest(repo, base, head, mirror=mirror, bridge=bridge)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert att_file(repo, head).is_file()
    lines = proc.stdout.splitlines()
    assert lines[0].startswith("attestation written: "), proc.stdout
    assert "reaped mirror: " + str(mirror) in proc.stdout
    assert "reaped sidecar: " + str(sidecar) in proc.stdout
    assert "reaped bridge: " + str(bridge) in proc.stdout
    assert not mirror.exists() and not bridge.exists() and not sidecar.exists()
    assert (target / "keep.txt").is_file(), "the junction target survives"
    assert (repo / "b.txt").is_file(), "the reviewed repo is untouched"


def test_a_remediation_commit_above_the_head_is_still_the_mirror(tmp_path):
    # The mirror tool commits its back-channel removal as parallax@local
    # with the source head as the single parent, so a mirror of a repo
    # with a TRACKED back-channel sits one commit above the attested head.
    repo, base, head = make_repo(tmp_path)
    mirror = make_mirror(repo, tmp_path / "kv-t")
    (mirror / "AGENTS.md").write_text("planted\n", encoding="utf-8")
    git(mirror, "add", "AGENTS.md")
    git(mirror, "commit", "-q", "-m", "planted")
    git(mirror, "rm", "-q", "AGENTS.md")
    subprocess.run(["git", "-C", str(mirror), "-c", "user.email=parallax@local",
                    "-c", "user.name=parallax", "commit", "-q", "-m",
                    "remove instruction back-channels for review"],
                   check=True, capture_output=True)
    # Two commits above head is NOT the remediation shape: refused.
    proc = attest(repo, base, head, mirror=mirror)
    assert proc.returncode == 2 and "not the attested head" in proc.stdout, proc.stdout
    assert not att_file(repo, head).exists(), "a refused argument writes nothing"
    assert mirror.exists()
    # Exactly one parallax@local commit whose parent is the head: accepted.
    mirror2 = make_mirror(repo, tmp_path / "kv-u")
    (mirror2 / "AGENTS.md").write_text("planted\n", encoding="utf-8")
    git(mirror2, "add", "AGENTS.md")
    subprocess.run(["git", "-C", str(mirror2), "-c", "user.email=parallax@local",
                    "-c", "user.name=parallax", "commit", "-q", "-m",
                    "remove instruction back-channels for review"],
                   check=True, capture_output=True)
    proc = attest(repo, base, head, mirror=mirror2)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert not mirror2.exists()


def test_a_bridge_at_a_stale_head_is_refused_by_name(tmp_path):
    repo, base, head = make_repo(tmp_path)
    bridge = make_bridge(repo, tmp_path / "kvs-t")
    (repo / "c.txt").write_text("c\n", encoding="utf-8")
    git(repo, "add", "c.txt")
    git(repo, "commit", "-q", "-m", "fix")
    head2 = git(repo, "rev-parse", "HEAD")
    proc = attest(repo, base, head2, bridge=bridge)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "not the attested head" in proc.stdout and head2 in proc.stdout
    assert bridge.exists() and not att_file(repo, head2).exists()


@pytest.mark.parametrize("shape", ["missing", "file", "inside-repo", "repo-itself",
                                   "contains-repo", "worktree", "no-git", "link"])
def test_every_wrong_tree_is_refused_before_the_record_is_written(tmp_path, shape):
    repo, base, head = make_repo(tmp_path)
    keep = None
    if shape == "missing":
        path = tmp_path / "absent"
    elif shape == "file":
        path = tmp_path / "plain.txt"
        path.write_text("x\n", encoding="utf-8")
    elif shape == "inside-repo":
        path = repo / "nested"
        make_mirror(repo / ".git", path / ".git")
    elif shape == "repo-itself":
        path = repo
    elif shape == "contains-repo":
        path = tmp_path
    elif shape == "worktree":
        path = tmp_path / "wt"
        git(repo, "worktree", "add", "-q", str(path), "main")
        assert (path / ".git").is_file()
    elif shape == "no-git":
        path = tmp_path / "bare"
        path.mkdir()
    else:
        keep = make_mirror(repo, tmp_path / "real")
        path = tmp_path / "link"
        junction(path, keep)
    proc = attest(repo, base, head, mirror=path)
    assert proc.returncode == 2, shape + ": " + proc.stdout + proc.stderr
    assert proc.stdout.startswith("ERROR:"), proc.stdout
    assert not att_file(repo, head).exists(), (
        shape + ": a refused reap path must be refused BEFORE the record is written")
    assert (repo / "b.txt").is_file()
    if shape not in ("missing",):
        assert path.exists(), shape + ": nothing was removed"
    if keep is not None:
        assert (keep / "b.txt").is_file(), "the link's target survives"


def test_a_held_handle_leaves_the_attestation_and_exits_three(tmp_path):
    repo, base, head = make_repo(tmp_path)
    mirror = make_mirror(repo, tmp_path / "kv-t")
    held = mirror / "held.txt"
    held.write_text("open\n", encoding="utf-8")
    with open(held, "r", encoding="utf-8"):
        proc = attest(repo, base, head, mirror=mirror)
    assert proc.returncode == 3, proc.stdout + proc.stderr
    assert att_file(repo, head).is_file(), "the verdict is recorded even when the reap fails"
    assert "ERROR: reap failed for " + str(mirror) in proc.stdout, proc.stdout
    assert str(held) in proc.stdout and "the attestation stands" in proc.stdout
    assert held.exists()


def test_without_the_parameters_the_emitter_removes_nothing(tmp_path):
    repo, base, head = make_repo(tmp_path)
    mirror = make_mirror(repo, tmp_path / "kv-t")
    proc = attest(repo, base, head)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "reaped" not in proc.stdout
    assert mirror.exists()


def test_emitter_header_declares_exit_three():
    body = read(WRITE)
    assert "Exit codes: 0 written, 2 argument/repo error, 3 written but a reap failed" in body
```

- [ ] **Step 2: Run group 2 and confirm it fails**

Run: `python -m pytest evals/multi-model-verify/test_mirror_reaper.py -q -k "reap or remediation or bridge or wrong_tree or held_handle_leaves or without_the or header"`
Expected: FAIL. The emitter rejects `-ReapMirror` as an unknown parameter (exit code 1 or a binding error in stderr), and the header pin is missing.

- [ ] **Step 3: Edit the emitter**

In `tools/write-attestation.ps1`:

(a) Replace the header line `# Exit codes: 0 written, 2 argument/repo error.` with:

```powershell
# Exit codes: 0 written, 2 argument/repo error, 3 written but a reap failed.
#
# REAP (0.35.0, backlog item 106): -ReapMirror and -ReapBridge name the
# review mirror and the clone bridge the debate ran on. The attestation
# is the one TERMINAL event the plugin records mechanically, so it is
# the reap point - never an age. Both paths are validated against the
# reviewed repository and the attested head BEFORE the record is
# written, so a refused argument costs nothing (exit 2); they are
# removed AFTER it, so a removal failure leaves the verdict standing
# and says so (exit 3). The removal itself is
# tools/review-tree-removal.ps1, shared with the mirror tool.
```

(b) In the `param(` block, after the `[string]$CheckpointFile = ""` line, change that line to end with a comma and add:

```powershell
    [string]$CheckpointFile = "",
    # Optional (0.35.0): the review mirror and the clone bridge to remove
    # once the record is written. See the REAP note in the header.
    [string]$ReapMirror = "",
    [string]$ReapBridge = ""
)
```

(c) Immediately after the closing `)` of the param block, add:

```powershell

. (Join-Path $PSScriptRoot "review-tree-removal.ps1")
```

(d) After the `Resolve-FullSha` function, add:

```powershell
function Resolve-ReapPath($label, $raw, $repoTop, $commonFull, $headFull, $allowRemediation) {
    # Returns the resolved full path of a tree this attestation may
    # remove, or prints ERROR and exits 2. Every refusal here runs before
    # the record is written. The rules are the spec's identity guard:
    # rooted and resolvable, not a filesystem root, an existing
    # directory, not through a link, not overlapping the reviewed repo
    # or its common dir, a .git DIRECTORY (a .git FILE is a linked
    # worktree, never a mirror or a bridge), and a HEAD equal to the
    # attested head - or, for the mirror only, one parallax@local
    # remediation commit whose single parent is that head, which is the
    # commit the mirror tool makes over a tracked back-channel.
    if ([string]::IsNullOrWhiteSpace($raw)) {
        Write-Output "ERROR: $label is empty"
        exit 2
    }
    if (-not [System.IO.Path]::IsPathRooted($raw)) {
        Write-Output "ERROR: $label must be an absolute path ($raw)"
        exit 2
    }
    $full = $null
    try {
        $full = [System.IO.Path]::GetFullPath($raw).TrimEnd("\")
    } catch {
        Write-Output ("ERROR: $label could not be resolved ($raw): " + $_.Exception.Message)
        exit 2
    }
    $pathRoot = [System.IO.Path]::GetPathRoot($full)
    if ((-not $pathRoot) -or ($full.Length -le ([string]$pathRoot).TrimEnd("\").Length)) {
        Write-Output "ERROR: $label is a filesystem root ($full)"
        exit 2
    }
    $attr = 0
    try {
        $attr = [int][System.IO.File]::GetAttributes($full)
    } catch [System.IO.FileNotFoundException] {
        Write-Output "ERROR: $label does not exist ($full)"
        exit 2
    } catch [System.IO.DirectoryNotFoundException] {
        Write-Output "ERROR: $label does not exist ($full)"
        exit 2
    } catch {
        Write-Output ("ERROR: $label could not be examined ($full): " + $_.Exception.Message)
        exit 2
    }
    if (($attr -band [int][System.IO.FileAttributes]::Directory) -eq 0) {
        Write-Output "ERROR: $label is a file, not a tree ($full)"
        exit 2
    }
    $hit = Test-PathOrAncestorIsLink $full
    if ($hit) {
        Write-Output ("ERROR: $label passes through a directory link at $hit" +
            " - a tree is never removed through a link")
        exit 2
    }
    # The mirror tool's own overlap comparison, against the reviewed
    # repository and against its git common dir (a linked worktree's
    # common dir sits outside its top level).
    $cmp = [System.StringComparison]::OrdinalIgnoreCase
    $p = $full.Replace("\", "/").TrimEnd("/") + "/"
    foreach ($pair in @(@("the reviewed repository", $repoTop), @("the git common dir", $commonFull))) {
        $g = ([string]$pair[1]).Replace("\", "/").TrimEnd("/") + "/"
        if ($p.Equals($g, $cmp)) {
            Write-Output ("ERROR: $label is " + $pair[0] + " itself ($full)")
            exit 2
        }
        if ($p.StartsWith($g, $cmp)) {
            Write-Output ("ERROR: $label is inside " + $pair[0] + " ($full)")
            exit 2
        }
        if ($g.StartsWith($p, $cmp)) {
            Write-Output ("ERROR: $label contains " + $pair[0] + " ($full)")
            exit 2
        }
    }
    $dotGit = Join-Path $full ".git"
    $ga = 0
    try {
        $ga = [int][System.IO.File]::GetAttributes($dotGit)
    } catch {
        Write-Output "ERROR: $label carries no .git entry, so it is not a review tree ($full)"
        exit 2
    }
    if (($ga -band [int][System.IO.FileAttributes]::Directory) -eq 0) {
        Write-Output ("ERROR: $label has a .git FILE, which marks a linked worktree" +
            " - never a mirror or a bridge ($full)")
        exit 2
    }
    $treeHead = (& git -C $full rev-parse --verify --quiet "HEAD^{commit}" 2>$null | Out-String).Trim()
    if (($LASTEXITCODE -ne 0) -or -not $treeHead) {
        Write-Output "ERROR: $label has no readable HEAD ($full)"
        exit 2
    }
    if ($treeHead -eq $headFull) {
        return $full
    }
    if ($allowRemediation) {
        $author = (& git -C $full log -1 --format=%ae HEAD 2>$null | Out-String).Trim()
        $authorExit = $LASTEXITCODE
        $parents = @(((& git -C $full rev-list --parents -n 1 HEAD 2>$null | Out-String).Trim()) -split "\s+")
        if (($authorExit -eq 0) -and ($LASTEXITCODE -eq 0) -and ($author -eq "parallax@local") -and
            ($parents.Count -eq 2) -and ($parents[1] -eq $headFull)) {
            return $full
        }
    }
    Write-Output ("ERROR: $label is at $treeHead, not the attested head $headFull" +
        " - it is not the tree this verdict was issued on ($full)")
    exit 2
}

function Invoke-Reap($label, $full) {
    # Runs after the record is written: a failure here is exit 3, with
    # the attestation left standing and the reason named.
    $r = Remove-ReviewTree $full
    if (-not $r.Ok) {
        Write-Output ("ERROR: reap failed for " + $full + ": " + $r.Reason +
            " - the attestation stands; remove the " + $label + " by hand")
        exit 3
    }
    Write-Output ("reaped " + $label + ": " + $full)
}
```

(e) Immediately BEFORE the line `$attDir = Join-Path (Join-Path $commonDir "parallax") "attestations"`, add:

```powershell
# REAP VALIDATION, before anything is written. Both trees are resolved
# and checked here so a wrong argument is refused at exit 2 with the
# record unwritten, and the removal below runs only against paths this
# block accepted.
$commonFull = [System.IO.Path]::GetFullPath($commonDir).TrimEnd("\")
$reapMirrorFull = $null
$reapBridgeFull = $null
if ($ReapMirror) {
    $reapMirrorFull = Resolve-ReapPath "the reap mirror" $ReapMirror $toplevel $commonFull $headFull $true
}
if ($ReapBridge) {
    $reapBridgeFull = Resolve-ReapPath "the reap bridge" $ReapBridge $toplevel $commonFull $headFull $false
}
if ($reapMirrorFull -and $reapBridgeFull -and ($reapMirrorFull -ieq $reapBridgeFull)) {
    Write-Output "ERROR: the reap mirror and the reap bridge are the same tree ($reapMirrorFull)"
    exit 2
}
```

Superseded 2026-09-13 by the diff debate's round 1 (Astra): the sidecar block below catches every inspection exception as absence and announces the reap without reading the sidecar back; the shipped emitter names an inspection failure and reads the sidecar back after the delete (both exit 3 with the record standing), and writes the record with -LiteralPath and a content read-back. The block is kept as the plan's history, not as the contract.

(f) Replace the final two lines

```powershell
Write-Output "attestation written: $outFile ($Verdict, $baseFull..$headFull)"
exit 0
```

with:

```powershell
Write-Output "attestation written: $outFile ($Verdict, $baseFull..$headFull)"
# THE REAP, after the record and in this order: mirror, its advisory
# sidecar, then the bridge. A failure stops at the first tree that
# could not be removed (exit 3) and leaves the record standing.
if ($reapMirrorFull) {
    Invoke-Reap "mirror" $reapMirrorFull
    # The mirror tool's advisory sibling, `<mirror>.source-manifest`,
    # removed only when it is an ordinary file: a directory or a link
    # there is not the sidecar and is left alone.
    $sidecar = $reapMirrorFull + ".source-manifest"
    $sa = $null
    try {
        $sa = [int][System.IO.File]::GetAttributes($sidecar)
    } catch {
        $sa = $null
    }
    if (($null -ne $sa) -and
        (($sa -band [int][System.IO.FileAttributes]::Directory) -eq 0) -and
        (($sa -band [int][System.IO.FileAttributes]::ReparsePoint) -eq 0)) {
        try {
            [System.IO.File]::SetAttributes($sidecar, [System.IO.FileAttributes]::Normal)
            [System.IO.File]::Delete($sidecar)
        } catch {
            Write-Output ("ERROR: reap failed for " + $sidecar + ": " +
                $_.Exception.Message + " - the attestation stands; remove the sidecar by hand")
            exit 3
        }
        Write-Output ("reaped sidecar: " + $sidecar)
    }
}
if ($reapBridgeFull) {
    Invoke-Reap "bridge" $reapBridgeFull
}
exit 0
```

- [ ] **Step 4: Run the new module and the attestation module under both hosts**

Run (PowerShell): `$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_mirror_reaper.py evals/multi-model-verify/test_attestation.py -q` then with `"pwsh.exe"`.
Expected: all PASS on both. `test_attestation.py` must be untouched by the change: every pre-existing emitter case still passes.

- [ ] **Step 5: Commit**

```bash
git add tools/write-attestation.ps1 evals/multi-model-verify/test_mirror_reaper.py
git commit -m "reap the review mirror and the clone bridge from the attestation emitter, validated against the attested head before the record is written"
```

---

### Task 4: The prose: skill command line, the reference's end-of-life section, the doctor inventory

**Files:**
- Modify: `skills/multi-model-verify/SKILL.md` (three exact edits in the Finish line and Common mistakes sections)
- Modify: `skills/multi-model-verify/references/preflight-mirror.md` (append a section)
- Modify: `commands/doctor.md` (append check 10)
- Modify: `evals/multi-model-verify/test_mirror_reaper.py` (append group 3)

**Interfaces:**
- Consumes: the parameter names and messages from Tasks 2 and 3.

- [ ] **Step 1: Write the failing tests**

Append to `evals/multi-model-verify/test_mirror_reaper.py`:

```python
# ---------------------------------------------------------------------
# Group 3: the prose carries the rule
# ---------------------------------------------------------------------
def test_skill_finish_line_passes_the_reap_paths():
    body = read(SKILL)
    assert "[-ReapMirror <mirror>] [-ReapBridge <bridge>]" in body
    assert "references/preflight-mirror.md's end-of-life section" in body
    assert body.count("write-attestation.ps1") >= 1


def test_preflight_mirror_reference_states_the_end_of_life_rule():
    body = read(PREFLIGHT)
    assert "## End of life" in body
    for anchor in (
        "The attestation is the reap point",
        "-ReapMirror",
        "-ReapBridge",
        "never an age",
        "HEAD is the attested head",
        "a `.git` FILE",
        "kv-<tag>-2",
    ):
        assert anchor in body, "end-of-life anchor missing: " + anchor


def test_doctor_inventories_the_mirrors_and_never_deletes():
    body = read(DOCTOR)
    assert "## 10. Review mirror inventory" in body
    for anchor in (
        "kv*",
        "$env:TEMP",
        "$env:SystemDrive",
        "5 GB",
        "3 days",
        "LastWriteTime",
        "-ReapMirror",
        "backlog item 106",
    ):
        assert anchor in body, "doctor inventory anchor missing: " + anchor
    section = body.split("## 10. Review mirror inventory", 1)[1]
    assert re.search(r"never delete", section, re.IGNORECASE), (
        "the inventory is observation, not action")
    assert "Remove-Item" not in section


def test_mirror_tool_refusal_and_emitter_agree_on_the_parameter_name():
    # One spelling in the tool that names the route and the tool that
    # implements it; a rename that misses one leaves a refusal pointing
    # at a parameter that does not exist.
    assert "write-attestation.ps1 -ReapMirror" in read(MIRROR_TOOL)
    assert "[string]$ReapMirror" in read(WRITE)
    assert "[string]$ReapBridge" in read(WRITE)
```

- [ ] **Step 2: Run group 3 and confirm all four fail**

Run: `python -m pytest evals/multi-model-verify/test_mirror_reaper.py -q -k "prose or skill_finish or preflight_mirror_reference or doctor_inventories or agree_on"`
Expected: `test_mirror_tool_refusal_and_emitter_agree_on_the_parameter_name` PASSES (Tasks 2 and 3 are in); the other three FAIL on missing text.

- [ ] **Step 3: Edit SKILL.md, exactly three edits**

Edit 1. In the Finish line section, the fenced command that begins `powershell -NoProfile -File <plugin-root>/tools/write-attestation.ps1` ends with `[-CheckpointFile <application-checkpoint-artifact>]`. Append ` [-ReapMirror <mirror>] [-ReapBridge <bridge>]` to that same line so it ends with `[-CheckpointFile <application-checkpoint-artifact>] [-ReapMirror <mirror>] [-ReapBridge <bridge>]`.

Edit 2. Immediately after the paragraph that ends `which head it is bound to.` (the `-CheckpointFile` paragraph), insert this paragraph, as its own paragraph with a blank line above and below:

```
Pass the mirror and the clone bridge as `-ReapMirror`/`-ReapBridge`;
references/preflight-mirror.md's end-of-life section states the guard.
```

Edit 3. In Common mistakes, delete the TWO bullets that read exactly (the convergence rule lives in references/debate-protocol.md, which is required reading, and the resume rule is SKILL.md's own step 3; the body sits 13 characters under the ceiling):

```
- Re-sending the full debate context each round instead of resuming the
  codex session.
```

```
- Treating convergence as failure — a sound plan converging in one round is
  the system working, not a skipped debate.
```

The body must end at or under 26000 characters after the frontmatter (`len(body) // 4` at or under 6500). Then run `python evals/tools/skill_lint.py skills/multi-model-verify --strict` and require `0 error(s)`; the token line may still WARN. If it prints an ERROR, STOP and report to the session.

- [ ] **Step 4: Append the end-of-life section to preflight-mirror.md**

Append to the END of `skills/multi-model-verify/references/preflight-mirror.md`:

```markdown

## End of life

The attestation is the reap point. A round's `resume` re-verifies the
mirror's identity, so a mirror deleted mid-debate turns a resumable
round into a transport failure; the one terminal event the plugin
records mechanically is the attestation, so `tools/write-attestation.ps1`
removes the mirror when it is passed as `-ReapMirror <path>`, and the
clone bridge a linked worktree needed when it is passed as
`-ReapBridge <path>`. The reap is bound to that event and never an age:
no sweep exists, and the doctor only reports.

The emitter validates both paths BEFORE it writes the record, so a wrong
argument is refused at exit 2 with nothing written, and removes them
AFTER, so a removal that fails leaves the verdict standing and exits 3
naming the entry that stopped it. A path is accepted only when it
exists as a directory not reached through a link, does not overlap the
reviewed repository or its git common dir, holds a `.git` DIRECTORY
(a `.git` FILE marks a linked worktree, never a mirror or a bridge), and
its HEAD is the attested head. The mirror may instead sit exactly one
`parallax@local` remediation commit above that head, because that is the
commit construction makes over a tracked back-channel; the bridge must
match exactly, so a bridge left unfetched after a fix commit is refused
rather than deleted under a stale head. Measured 2026-09-13: 78 mirror
and bridge directories, 13.4 GB, in four review days, with nothing but
memory saying which of them a live chat could still resume. Another
chat's mirror is at another head and is refused by name.

The removal never recurses through a link: `tools/review-tree-removal.ps1`
walks the tree itself, removes each link as a link, clears the read-only
bit git puts on its objects, and re-examines the root afterwards. The
mirror tool's `-Force` rebuild uses the same function, which is what
closed backlog item 98.

An existing `-MirrorPath` without `-Force` is refused with the reap
route named. Build `kv-<tag>-2` beside a finished debate's mirror and
the count grows by one for every debate; reap the finished one instead,
and rebuild in place with `-Force` only for a debate that is still
running, because a resumed round needs the mirror at the path its
identity was recorded at.

The bridge is the session's. The plugin never created it and cannot
recognise one by shape, so the session that built it names it; the rule
"pass the bridge to the emitter" belongs beside the rule that builds it.
```

- [ ] **Step 5: Append check 10 to doctor.md**

Append to the END of `commands/doctor.md`:

```markdown

## 10. Review mirror inventory

Observation only: this check reports and never deletes, whatever it
finds. List every DIRECTORY whose name begins with `kv` sitting directly
under `$env:SystemDrive\` and directly under `$env:TEMP` - the two
places a review mirror or its clone bridge is built (the canonical
review mirror root is the temp directory; a session whose packets blow
the path budget builds at the drive root instead, and both are outside
every checkout). Measure the count, the total size in GB (sum of file
lengths, reparse points NOT followed), and the oldest `LastWriteTime`
among them. A directory that cannot be measured is named as unmeasured
and counted; it never reads as empty.

- Nothing found: OK, `no review mirrors present`.
- Found, total under 5 GB AND oldest under 3 days: OK, reported as a
  NOTE with the three numbers.
- Total 5 GB or more, OR oldest 3 days or more: STALE, with the three
  numbers and this fix: a finished debate's mirror is removed by the
  attestation emitter, `write-attestation.ps1 -ReapMirror <mirror>
  [-ReapBridge <bridge>]`, and one whose debate is over without an
  attestation is removed by hand; the rule and its measurement are
  backlog item 106. Never name a directory as safe to delete: the
  doctor cannot tell which of them a live chat can still resume, and a
  `resume` against a deleted mirror is a transport failure.

The thresholds are the ones the 2026-09-13 measurement would have
tripped on day two: 13.4 GB across 78 directories accumulated in four
review days, about 3 GB per active day.
```

- [ ] **Step 6: Run the full new module, the skill pins and the doctor pins under both hosts**

Run (PowerShell): `$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_mirror_reaper.py evals/multi-model-verify/test_multi_model_verify.py evals/multi-model-verify/test_contract_coverage.py -q` then with `"pwsh.exe"`.
Then: `python evals/tools/skill_lint.py skills/multi-model-verify --strict` and `python evals/tools/skill_scanner.py skills`.
Expected: all PASS; skill_lint prints `0 error(s)`.

- [ ] **Step 7: Commit**

```bash
git add skills/multi-model-verify/SKILL.md skills/multi-model-verify/references/preflight-mirror.md commands/doctor.md evals/multi-model-verify/test_mirror_reaper.py
git commit -m "state the reap point in the skill and the reference, and inventory review mirrors in the doctor"
```

---

## Not in this plan

- The version bump and the closing edits to items 98 and 106 in `BACKLOG.md`: they follow the diff debate, per `CLAUDE.md`'s dev loop.
- The KitnEssentials memory edit that tells the bridge builder to pass `-ReapBridge`.
- Deleting the ten `C:\kv*` directories that exist today.
