# Mirror Identity Window Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the review mirror's identity refusal name the paths that moved, and ship the quiet-period rule that the refusal enforces, so a session outside this repo can act on both.

**Architecture:** Three independent changes and no change to the gate. The build writes the source side's content manifest to a sibling of the mirror directory, under the same destination guards `-OverrideOut` already carries; the source-status refusal reads that sibling, on that path only, to name what entered coverage, left coverage, or changed content; and the skill grows a contract region plus a timing rule stating that nothing may write inside the reviewed repository between the build and the wrapper's exit. The sidecar file is advisory: it is read after the comparison has already decided to block, so no state it can be in changes any exit code.

**Tech Stack:** Windows PowerShell 5.1 and PowerShell 7 (`tools/new-review-mirror.ps1`), Python 3 with pytest (`evals/multi-model-verify/`), Markdown contract regions under `skills/`.

**Spec:** `docs/superpowers/specs/2026-09-05-mirror-identity-window-design.md`

## Global Constraints

- `tools/new-review-mirror.ps1` is **Windows PowerShell 5.1 compatible and ASCII ONLY**. No smart quotes, no dashes outside the ASCII hyphen, no non-ASCII byte anywhere in the file.
- **No VERIFICATION verdict may change.** Every existing `-VerifyIdentity` outcome stays exactly what it is today, and the new explanation only ADDS printed output on a path already exiting 1. This is NOT a blanket ban on new exit codes: Task 1 deliberately adds CONSTRUCTION refusals that exit 2 for destinations the build previously accepted unguarded. Adding a build refusal is in scope; changing what a verify decides is not.
- **Tests first.** Write the failing test, run it, watch it fail for the stated reason, then implement.
- **Do not bump `.claude-plugin/plugin.json` in this plan.** The bump happens after the diff debate, per `CLAUDE.md`.
- **Do not run pytest, the gates, or any repo-writing command while a review round is in flight.** That is the defect this plan documents.
- A new contract region needs BOTH a whole-region pin in `evals/multi-model-verify/` AND an entry in `DECLARED_REGIONS` in `evals/multi-model-verify/test_contract_coverage.py`.
- A pin asserted with `in text` against the raw file matches **line breaks and leading indentation exactly**. Write the Markdown first, then copy those lines byte for byte into the pin.
- Commits are lowercase imperative with no AI attribution. **A commit message must not contain a bare `-Word` token**: the family git guard reads it as a passed flag and denies the commit (backlog item 79).
- Work on a feature branch, never on `main`.

---

### Task 1: The build writes the source manifest beside the mirror

**Files:**
- Modify: `tools/new-review-mirror.ps1` (the `Get-StatusSha256` return at `:662-694`, two new functions beside it, the guard block at `:951-1008`, the alias guards at `:1258-1290`, and the record block at `:1737-1756`)
- Test: `evals/multi-model-verify/test_review_mirror.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - `Get-StatusSha256($repo)` returns `@{ Ok = $true; Sha = <hex>; Manifest = <string[]> }` on success, unchanged `@{ Ok = $false; Reason = <string> }` on failure. `Manifest` holds `Get-ContentManifest`'s lines, each `"<relpath> <sha256hex>"`.
  - `Get-SourceManifestSidecarPath($mirrorPath)` returns `"<full mirror path>.source-manifest"`, or `$null` when the mirror path is a filesystem root and therefore has no sibling.
  - `Write-SourceManifestSidecar($path, $manifestLines)` returns `$true` or `$false`. It opens the file with `CreateNew`, which makes the FINAL PATH COMPONENT safe against an overwrite and against a link substituted there. It does not and cannot defend a DIRECTORY component; that is the alias guards' job, in Step 5b.
  - The build's record block gains one line, `source_manifest: <path>`, printed after `override:`.

**Why this task is mostly guards.** The sidecar path is DERIVED, not supplied, and a derived string written without a guard is a write into whatever happens to sit there. A link at that path carries the write through to its target, and a target inside the repository would be corrupted by the very function that exists to explain a corrupted repository.

Cross-vendor review found that the first draft had NO destination guards, and then found that the second draft's claim to carry "the override's whole guard set" was false. The override's protection is in TWO places: the lexical block at `:951-1008`, and the alias block at `:1258-1290` that walks each path's ancestors for a reparse point and checks it against every followed link target. The second draft copied only the first. This task copies both, and it validates completely BEFORE it removes anything.

- [ ] **Step 1: Write the failing tests**

Add to `evals/multi-model-verify/test_review_mirror.py`, immediately after `test_the_record_carries_both_heads_and_the_source_status_hash`:

```python
def test_the_build_writes_the_source_manifest_beside_the_mirror(tmp_path):
    """The advisory sidecar the refusal reads to say what moved.

    A SIBLING of the mirror, never a child and never inside the repo:
    a child would enter mirror_state_sha256 and a file in the repo would
    enter source_status_sha256, and this one must enter neither.
    """
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    proc, _ = build_and_read(repo, mirror)
    sidecar = tmp_path / "mirror.source-manifest"
    assert sidecar.is_file(), proc.stdout + proc.stderr
    lines = sidecar.read_text(encoding="utf-8").splitlines()
    assert any(line.startswith("ignored/secret.txt ") for line in lines), lines
    assert record_field(proc.stdout, "source_manifest") == str(sidecar)


def test_the_source_manifest_sidecar_enters_neither_identity(tmp_path):
    """The positive control for the sidecar's placement. If it landed
    inside the mirror or inside the repo, writing it would void the very
    identity it exists to explain, and this verify would refuse."""
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "identity: verified" in proc.stdout, proc.stdout


def test_a_pre_existing_sidecar_is_refused_without_force(tmp_path):
    """A derived destination written without a guard is a write into
    whatever sits there. This is the override's own rule, applied to the
    file that shares the override's shape."""
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    (tmp_path / "mirror.source-manifest").write_text("not ours\n")
    proc = run_mirror(repo, mirror)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "already exists" in proc.stdout, proc.stdout
    assert (tmp_path / "mirror.source-manifest").read_text() == "not ours\n"


def test_force_replaces_a_pre_existing_sidecar(tmp_path):
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    (tmp_path / "mirror.source-manifest").write_text("not ours\n")
    build_and_read(repo, mirror, "-Force")
    text = (tmp_path / "mirror.source-manifest").read_text()
    assert "not ours" not in text, text
    assert "ignored/secret.txt " in text, text


def test_an_override_at_the_sidecar_path_is_refused(tmp_path):
    """The probe writes the verified override, the wrapper hashes it, and
    an unguarded advisory write would replace it between those two acts.
    Refuse the collision instead."""
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    clash = tmp_path / "mirror.source-manifest"
    proc = run_mirror(repo, mirror, "-OverrideOut", str(clash))
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "override path" in proc.stdout, proc.stdout


def test_an_extra_input_at_the_sidecar_path_is_refused(tmp_path):
    """-ExtraInput is resolved before the sidecar guard, so a -Force
    build could delete the declared input and then copy nothing, and the
    unchecked Copy-Item at :1554 would not say so. Refuse the collision
    instead of racing it."""
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    clash = tmp_path / "mirror.source-manifest"
    clash.write_text("a declared review input\n")
    proc = run_mirror(repo, mirror, "-Force", "-ExtraInput", str(clash))
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "extra input" in proc.stdout.lower(), proc.stdout
    assert clash.read_text() == "a declared review input\n"


def test_a_sidecar_reached_through_a_directory_link_is_refused(tmp_path):
    """The alias guard the second draft missed entirely. The mirror path
    and the override path are both walked for a reparse-point ancestor
    at :1258; the sidecar must be walked with them, or a junction above
    it aliases a tree the build then writes into."""
    real = tmp_path / "real"
    real.mkdir()
    repo = make_repo(tmp_path)
    link = tmp_path / "alias"
    make_junction(link, real)
    proc = run_mirror(repo, link / "mirror", "-Force")
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "directory link" in proc.stdout, proc.stdout


def test_no_sidecar_is_removed_before_validation_completes(tmp_path):
    """DELETION AFTER VALIDATION, never during it. The second draft
    removed a pre-existing sidecar under -Force at the lexical guard,
    which runs BEFORE the alias guard that would have refused the build
    outright. The file must survive a build that is going to be
    refused."""
    real = tmp_path / "real"
    real.mkdir()
    repo = make_repo(tmp_path)
    link = tmp_path / "alias"
    make_junction(link, real)
    victim = tmp_path / "alias" / "mirror.source-manifest"
    victim.write_text("must survive\n")
    proc = run_mirror(repo, link / "mirror", "-Force")
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert victim.read_text() == "must survive\n", "deleted before refusing"


@pytest.mark.parametrize("root", ["C:\\", "\\\\server\\share\\"])
def test_a_filesystem_root_has_no_sidecar(tmp_path, root):
    """Measured 2026-09-05: `Split-Path 'C:\\' -Leaf` returns `C:\\`, not
    `C:`, so a regex on the leaf detects no drive root; and
    `Split-Path '\\\\server\\share\\' -Leaf` returns `share` with parent
    `\\\\server`, which would name a DIFFERENT SHARE. The two hosts do not
    agree on the UNC case, so the root test cannot be built on the leaf.
    """
    repo = make_repo(tmp_path)
    proc = run_mirror(repo, pathlib.Path(root))
    assert proc.returncode == 2, proc.stdout + proc.stderr
    assert "root" in proc.stdout.lower(), proc.stdout
```

Add `import pathlib` to the module's imports if it is not already there. The root case never reaches a build: the mirror-path guards refuse a root long before the sidecar is derived, so assert on whichever refusal fires and say in a comment which one it was. What this test locks is that a root NEVER yields a derived sibling.

- [ ] **Step 2: Run the tests and confirm they fail for the stated reason**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -k "sidecar or source_manifest or filesystem_root" -v`

Expected: the build, collision, alias and root tests FAIL. `test_the_source_manifest_sidecar_enters_neither_identity` PASSES already, because nothing writes a sidecar yet; it is a regression guard for Step 6.

- [ ] **Step 3: Return the manifest from `Get-StatusSha256`**

In `tools/new-review-mirror.ps1`, replace the final `return` of `Get-StatusSha256` (currently `:692-693`):

```powershell
    return @{ Ok = $true
              Manifest = @($content.Paths)
              Sha = (Get-CombinedSha256 $captured.Fields $content.Paths) }
```

- [ ] **Step 4: Add the two sidecar functions**

Insert immediately after `Get-StatusSha256`'s closing brace, before `$toplevel = $true`:

```powershell
function Get-SourceManifestSidecarPath($mirrorPath) {
    # A SIBLING of the mirror, never a child. A file inside the mirror
    # would enter mirror_state_sha256 and a file inside the repository
    # would enter source_status_sha256; this one must enter neither,
    # because it is written after both are measured and read only after
    # a comparison has already decided to refuse.
    #
    # ONE derivation, shared by the build that writes the file and the
    # verify that reads it, so the two sides cannot drift apart.
    #
    # A ROOT HAS NO SIBLING, and the leaf is NOT how you detect one.
    # Measured 2026-09-05: `Split-Path 'C:\' -Leaf` returns `C:\` rather
    # than `C:`, so a regex on the leaf never fires for a drive root; and
    # `Split-Path '\\server\share\' -Leaf` returns `share` with parent
    # `\\server`, which appended would name a DIFFERENT SHARE. The two
    # hosts do not agree on the UNC case. So the framework's own root is
    # the test, and the suffix is APPENDED to the full path rather than
    # rejoined to a parent, which removes the UNC rejoin entirely.
    $full = $null
    try {
        $full = [System.IO.Path]::GetFullPath($mirrorPath)
    } catch {
        return $null
    }
    $full = $full.TrimEnd("\")
    $root = $null
    try {
        $root = [System.IO.Path]::GetPathRoot($full)
    } catch {
        return $null
    }
    if (-not $root) { return $null }
    if ($full.Length -le ([string]$root).TrimEnd("\").Length) { return $null }
    return ($full + ".source-manifest")
}

function Write-SourceManifestSidecar($path, $manifestLines) {
    # ADVISORY ONLY. It pins nothing and gates nothing, so a failure to
    # write it is not a build failure - it costs a later refusal its
    # explanation and nothing else. That is also why it may be a file at
    # all: the header's rule about values passed as arguments rather than
    # re-read from a file governs values that PIN something, and this
    # value carries no authority.
    #
    # CREATE-NEW, never WriteAllLines. State the guarantee exactly: it
    # makes the FINAL PATH COMPONENT safe, so a file created between the
    # guards and this write is not overwritten and a link substituted at
    # that name is not written through. It does NOT defend a DIRECTORY
    # component - an ancestor replaced by a junction before this open
    # redirects creation into that junction's target, and no open flag
    # prevents that. The alias guards above are what cover ancestors, and
    # they run before any of this.
    try {
        $utf8 = New-Object System.Text.UTF8Encoding($false)
        $fs = [System.IO.File]::Open($path, 'CreateNew', 'Write', 'None')
        try {
            $sw = New-Object System.IO.StreamWriter($fs, $utf8)
            try {
                foreach ($line in @($manifestLines)) {
                    $sw.WriteLine([string]$line)
                }
            } finally { $sw.Dispose() }
        } finally { $fs.Dispose() }
        return $true
    } catch {
        return $false
    }
}
```

- [ ] **Step 5a: Resolve and lexically guard the destination, WITHOUT touching it**

Insert immediately AFTER the override's pre-existence refusal, the block ending `"a stale override reads exactly like a fresh one"` at `tools/new-review-mirror.ps1:970-973`, and BEFORE the `PATH BUDGET PRE-FLIGHT` comment. `$rr`, `$mp`, `$op` and `$cmp` are the normalized paths and the comparison mode the override guard above already set up.

NOTHING HERE MUTATES ANYTHING. The removal is Step 5c, after every check has passed:

```powershell
# THE ADVISORY SOURCE MANIFEST'S DESTINATION, resolved and LEXICALLY
# guarded here, beside the override, for the same stated reason: a
# destination discovered after the build has copied, remediated and
# manifested is discovered too late, and -SkipProbe would bypass a check
# placed later. Its ALIAS guards are further down with the override's,
# and its removal is after both, because a build that is going to be
# refused must not have deleted anything first.
$SourceManifestOut = Get-SourceManifestSidecarPath $MirrorPath
if (-not $SourceManifestOut) {
    Write-Output ("ERROR: the mirror path is a filesystem root" +
        " ($MirrorPath), which has no sibling, so no advisory source" +
        " manifest can be placed beside it")
    exit 2
}
$smp = $SourceManifestOut.Replace("\", "/").TrimEnd("/")
foreach ($protected in @($rr, $mp)) {
    if (($smp + "/").Equals($protected, $cmp) -or
        ($smp + "/").StartsWith($protected, $cmp) -or
        $protected.StartsWith($smp + "/", $cmp)) {
        Write-Output ("ERROR: the source manifest path overlaps a protected" +
            " tree ($SourceManifestOut)")
        exit 2
    }
}
if ($smp.Equals($op, $cmp)) {
    Write-Output ("ERROR: the source manifest path is the override path" +
        " ($SourceManifestOut) - the advisory write would replace the file" +
        " the probe verified and the wrapper hashes")
    exit 2
}
if ($SourceManifestOut.Length -ge 260) {
    Write-Output ("ERROR: path budget exceeded by the source manifest - " +
        "$SourceManifestOut is $($SourceManifestOut.Length) characters " +
        "and the limit is 260")
    exit 2
}
```

The literal `260` is used here because `$PathBudget` is assigned below this point. If the implementer prefers the variable, MOVE the `$PathBudget = 260` assignment above this block rather than moving this block down: this guard must stay ahead of every mutation.

- [ ] **Step 5b: Add the sidecar to the alias guards**

At `tools/new-review-mirror.ps1:1258`, extend the ancestor-link loop's pair list:

```powershell
foreach ($pair in @(@("mirror path", $MirrorPath), @("override path", $OverrideOut),
                    @("source manifest path", $SourceManifestOut))) {
```

and at the followed-target overlap loop below it (currently `:1281-1290`), extend its pair list the same way, with the sidecar normalized like the override:

```powershell
    foreach ($pair in @(@("mirror path", $mp), @("override path", ($op + "/")),
                        @("source manifest path", ($smp + "/")))) {
```

This is the half the previous draft claimed to have and did not. Without it the sidecar can sit under a junction that aliases a tree the mirror only links to, which is the exact condition the mirror and override paths are already refused for.

- [ ] **Step 5c: Refuse or remove a pre-existing sidecar, AFTER all validation**

Insert immediately AFTER the followed-target overlap loop from Step 5b, so every lexical and alias check has already passed:

```powershell
# LAST, because a build that is going to be refused must not have deleted
# anything first. Read the ATTRIBUTES rather than calling Test-Path: a
# dangling reparse point is not reliably reported as existing, which the
# link walker above documents, and this is the one place where a wrong
# "it is not there" turns into a write.
$smAttr = $null
try {
    $smAttr = [System.IO.File]::GetAttributes($SourceManifestOut)
} catch [System.IO.FileNotFoundException] {
    $smAttr = $null
} catch [System.IO.DirectoryNotFoundException] {
    $smAttr = $null
} catch {
    Write-Output ("ERROR: the source manifest path could not be examined" +
        " ($SourceManifestOut): " + $_.Exception.Message)
    exit 2
}
if ($null -ne $smAttr) {
    if (([int]$smAttr -band [int][System.IO.FileAttributes]::Directory) -ne 0) {
        Write-Output ("ERROR: $SourceManifestOut is a directory - this tool" +
            " replaces a file there and never removes a tree")
        exit 2
    }
    if (-not $Force) {
        Write-Output ("ERROR: $SourceManifestOut already exists - pass" +
            " -Force to replace it, the same rule the mirror path follows")
        exit 2
    }
    # REMOVING a link removes the link and never its target's bytes,
    # which is exactly why the removal is safe where a write through it
    # was not.
    Remove-Item -LiteralPath $SourceManifestOut -Force
}
```

Then, in the `-ExtraInput` resolution above (the loop that resolves each declared extra input, `:919` onward), refuse a declared input at the sidecar path:

```powershell
    if ($eiFull.Replace("\", "/").TrimEnd("/").Equals($smp, $cmp)) {
        Write-Output ("ERROR: -ExtraInput '" + $ei + "' is the source" +
            " manifest path, which this build replaces - a declared review" +
            " input must not be a file this tool overwrites")
        exit 2
    }
```

If `-ExtraInput` is resolved BEFORE `$smp` exists, move this check to sit just after Step 5a instead, iterating the resolved extra inputs there. The ordering requirement is only that it precedes Step 5c's removal.

- [ ] **Step 6: Write the sidecar and record its path**

In the record block, insert immediately BEFORE the existing `Write-Output ("mirror: " + $MirrorPath)` line (currently `:1737`):

```powershell
# The advisory source manifest, written before the record so the record
# can name it. Its destination was fully guarded above; a failure to
# write it here is reported and never fatal.
$sidecarRecord = $SourceManifestOut
if (-not (Write-SourceManifestSidecar $SourceManifestOut $sourceStatus.Manifest)) {
    $sidecarRecord = "unwritable"
}
```

Then insert one line immediately AFTER the existing `Write-Output ("override: " + $overrideFile)` line:

```powershell
Write-Output ("source_manifest: " + $sidecarRecord)
```

Both insertions sit ABOVE the `-SkipProbe` block at the end of the file, so a `-SkipProbe` build writes the sidecar too. The tests depend on that.

- [ ] **Step 7: Run the tests and confirm they pass**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -k "sidecar or source_manifest or filesystem_root" -v`

Expected: all PASS.

- [ ] **Step 8: Run the whole mirror module for regressions**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -q`

Expected: all PASS. If the record-parsing tests fail, the new `source_manifest:` line was inserted inside a labelled block rather than after `override:`.

- [ ] **Step 9: Confirm the file is still ASCII**

Run: `python -c "d=open('tools/new-review-mirror.ps1','rb').read(); bad=[i for i,b in enumerate(d) if b>127]; print('non-ascii at', bad[:5] if bad else 'none')"`

Expected: `non-ascii at none`.

- [ ] **Step 10: Commit**

```bash
git add tools/new-review-mirror.ps1 evals/multi-model-verify/test_review_mirror.py
git commit -m "write the source content manifest beside the review mirror"
```

---

### Task 2: The source-status refusal names what moved

**Files:**
- Modify: `tools/new-review-mirror.ps1` (three new functions beside the sidecar functions, and the refusal at `:845-851`)
- Test: `evals/multi-model-verify/test_review_mirror.py`

**Interfaces:**
- Consumes: `Get-SourceManifestSidecarPath($mirrorPath)` and `Get-StatusSha256`'s `Manifest` field from Task 1.
- Produces:
  - `Get-ManifestDrift($recordedLines, $liveLines)` returns `@{ Entered = <string[]>; Left = <string[]>; Changed = <string[]>; Malformed = <int> }`. The three lists are sorted by path. `Malformed` counts every record the parser rejected.
  - `Format-AdvisoryName($name)` returns a bounded string with every control, format and separator character rendered as `\xNN` or `\uNNNN`.
  - `Write-SourceDriftExplanation($mirrorPath, $liveManifest)` writes lines to the pipeline. It is called for its output; its return value is not read.

**What the previous draft claimed and did not deliver.** Cross-vendor review confirmed four gaps in the second draft, each an instance of the class this whole cycle exists to remove: the parser accepted `bad.txt not-a-hash` as a valid record while the plan said malformed records were counted; `Get-Item` measured the file and a separate `ReadAllBytes` read it, so the size limit bounded nothing; `Format-AdvisoryName` tested `[int]$ch -lt 32` and so passed C1 controls such as U+0085 and U+009B straight through, along with U+2028 and U+202E; and the sidecar path and exception text bypassed the formatter entirely.

- [ ] **Step 1: Write the failing tests**

Replace `test_source_drift_in_an_ignored_file_blocks_the_dispatch`'s assertions and add the following, all directly after it:

```python
def test_the_refusal_names_the_ignored_file_that_changed(tmp_path):
    """The whole reason this task exists. The refusal used to name the
    CLASS of change and stop, so a session hitting it repeatedly could
    not tell a cache write from a planted file."""
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    (repo / "ignored" / "secret.txt").write_text("edited after the copy\n")
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "source status" in proc.stdout.lower(), proc.stdout
    assert "content changed" in proc.stdout, proc.stdout
    assert "ignored/secret.txt" in proc.stdout, proc.stdout


def test_the_refusal_names_a_file_that_entered_coverage(tmp_path):
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    (repo / "brand-new-input.txt").write_text("appeared after the copy\n")
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "entered manifest coverage" in proc.stdout, proc.stdout
    assert "brand-new-input.txt" in proc.stdout, proc.stdout


def test_the_refusal_names_a_file_that_left_coverage(tmp_path):
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    (repo / "ignored" / "secret.txt").unlink()
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "left manifest coverage" in proc.stdout, proc.stdout
    assert "ignored/secret.txt" in proc.stdout, proc.stdout


def test_a_missing_source_manifest_still_refuses(tmp_path):
    """The explanation is ADVISORY. Its absence costs the reason and
    never the refusal."""
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    (tmp_path / "mirror.source-manifest").unlink()
    (repo / "ignored" / "secret.txt").write_text("edited after the copy\n")
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "source status" in proc.stdout.lower(), proc.stdout
    assert "unknown" in proc.stdout, proc.stdout


def test_a_corrupted_source_manifest_still_refuses(tmp_path):
    """The direction that matters. A sidecar an attacker can write must
    never turn a refusal into a pass, and it structurally cannot: it is
    read only after the comparison has already decided to block."""
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    (tmp_path / "mirror.source-manifest").write_bytes(b"\x00garbage\xff\nno")
    (repo / "ignored" / "secret.txt").write_text("edited after the copy\n")
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "source status" in proc.stdout.lower(), proc.stdout


def test_a_clean_tree_verifies_with_no_source_manifest(tmp_path):
    """The other advisory direction. A tree that did not move verifies
    whether or not the sidecar survives, because the sidecar is not an
    input to the comparison."""
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    (tmp_path / "mirror.source-manifest").unlink()
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    assert "identity: verified" in proc.stdout, proc.stdout


def test_a_case_only_rename_is_not_lost_by_the_explanation(tmp_path):
    """A PowerShell hashtable compares keys case-INsensitively, so
    `File.txt` and `file.txt` would collapse into one entry and this
    drift would report nothing at all, while the digest, built from the
    raw strings, changes."""
    repo = make_repo(tmp_path)
    (repo / "ignored" / "Cased.txt").write_text("one\n")
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    (repo / "ignored" / "Cased.txt").rename(repo / "ignored" / "cased.txt")
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "coverage" in proc.stdout, proc.stdout
    assert "cased.txt" in proc.stdout, proc.stdout


def test_a_hostile_but_well_formed_manifest_cannot_manufacture_a_pass(tmp_path):
    """The corrupted-bytes case exercises the reader's catch. This one
    reaches the parser and the renderer with VALID records naming
    innocent files, which is the shape an attacker would use."""
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    (repo / "ignored" / "secret.txt").write_text("edited after the copy\n")
    forged = "\n".join("decoy/%d.txt %064x" % (i, i) for i in range(5)) + "\n"
    (tmp_path / "mirror.source-manifest").write_text(forged)
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "source status" in proc.stdout.lower(), proc.stdout


def test_a_record_whose_hash_field_is_not_a_hash_is_counted(tmp_path):
    """`bad.txt not-a-hash` used to parse as an ordinary record, so a
    truncated digest became a reported difference rather than an
    admission that the explanation is incomplete."""
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    sidecar = tmp_path / "mirror.source-manifest"
    sidecar.write_text(sidecar.read_text() + "bad.txt not-a-hash\n"
                       + "empty.txt \n" + "no-space-here\n")
    (repo / "ignored" / "secret.txt").write_text("edited after the copy\n")
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "3 advisory record(s) could not be read" in proc.stdout, proc.stdout
    assert "incomplete" in proc.stdout, proc.stdout


def test_a_trailing_newline_is_not_counted_as_a_malformed_record(tmp_path):
    """The split artifact is not a record. Counting it would put a
    permanent, meaningless `1 record could not be read` on every
    explanation and teach the operator to ignore the line."""
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    (repo / "ignored" / "secret.txt").write_text("edited after the copy\n")
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "could not be read" not in proc.stdout, proc.stdout


def test_display_controls_in_an_advisory_name_are_rendered(tmp_path):
    """The sidecar is mutable, so a name in it never passed
    Test-SupportedPathname. C1 controls such as U+009B and the
    bidirectional override U+202E are terminal escapes and line-display
    manipulation; `[int]$ch -lt 32` catches neither."""
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    sidecar = tmp_path / "mirror.source-manifest"
    sidecar.write_text("ev\u009bil\u202e.txt " + "0" * 64 + "\n",
                       encoding="utf-8")
    (repo / "ignored" / "secret.txt").write_text("edited after the copy\n")
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "\u009b" not in proc.stdout, "a C1 control reached the terminal"
    assert "\u202e" not in proc.stdout, "a bidi override reached the terminal"
    assert "\\u009b" in proc.stdout or "\\u009B" in proc.stdout, proc.stdout


def test_an_oversized_source_manifest_is_refused_by_the_reader(tmp_path):
    """The size limit must bound the READ, not a separate earlier
    measurement. Written just past the limit so the test stays cheap."""
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    sidecar = tmp_path / "mirror.source-manifest"
    with sidecar.open("wb") as fh:
        fh.write(b"x" * (67108864 + 1))
    (repo / "ignored" / "secret.txt").write_text("edited after the copy\n")
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "past this reader's limit" in proc.stdout, proc.stdout
```

- [ ] **Step 2: Run the tests and confirm they fail for the stated reason**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -k "refusal or advisory or manifest or coverage or reader" -v`

Check the collected count against the list above before trusting the result: a `-k` selector that silently matches fewer tests than were written is how a suite reports green on cases it never ran.

Expected: the naming, malformed, rendering and reader-limit tests FAIL. The two advisory-direction tests and the trailing-newline test PASS already; they are regression guards.

- [ ] **Step 3: Add the diff and rendering functions**

Insert into `tools/new-review-mirror.ps1` immediately after `Write-SourceManifestSidecar`:

```powershell
function Get-ManifestDrift($recordedLines, $liveLines) {
    # Both sides are "<relpath> <sha256hex>" lines, so the LAST space is
    # the separator: a pathname may hold spaces and a hex digest may not.
    #
    # ORDINAL, CASE-SENSITIVE keys. A PowerShell hashtable compares keys
    # case-INsensitively, so `File.txt` and `file.txt` collapse into one
    # entry and a case-only rename reports no difference at all - while
    # the digest, built from the raw strings, changes. The explanation
    # must partition the same strings the digest does.
    #
    # THE GRAMMAR IS CHECKED, not assumed. A record whose hash field is
    # not 64 lowercase hex characters is malformed, and so is a duplicate
    # key, an over-long line, and a line with no separator. Every one is
    # COUNTED, never silently dropped: a dropped record is a difference
    # this explanation would then fail to mention, which is the shape of
    # defect this whole change exists to remove. An EMPTY line is the
    # split artifact of a trailing newline and is not a record at all, so
    # it is skipped without counting.
    $ord = [System.StringComparer]::Ordinal
    $recorded = New-Object "System.Collections.Generic.Dictionary[string,string]" $ord
    $live = New-Object "System.Collections.Generic.Dictionary[string,string]" $ord
    $malformed = 0
    $hexRx = '^[0-9a-f]{64}$'
    foreach ($side in @(@($recordedLines, $recorded), @($liveLines, $live))) {
        $seen = 0
        foreach ($line in @($side[0])) {
            $s = [string]$line
            if ($s.Length -eq 0) { continue }
            # BOUNDED. Both the record count and each record's length are
            # someone else's choice in the advisory file, and a byte
            # limit alone does not bound the working set a split of that
            # file produces.
            $seen++
            if ($seen -gt 200000) { $malformed++; break }
            if ($s.Length -gt 4096) { $malformed++; continue }
            $cut = $s.LastIndexOf(" ")
            if ($cut -lt 1) { $malformed++; continue }
            $hex = $s.Substring($cut + 1)
            if ($hex -cnotmatch $hexRx) { $malformed++; continue }
            $key = $s.Substring(0, $cut)
            if ($side[1].ContainsKey($key)) { $malformed++; continue }
            $side[1][$key] = $hex
        }
    }
    $entered = New-Object System.Collections.ArrayList
    $left = New-Object System.Collections.ArrayList
    $changed = New-Object System.Collections.ArrayList
    foreach ($p in @($live.Keys)) {
        if (-not $recorded.ContainsKey($p)) {
            [void]$entered.Add($p)
        } elseif ($recorded[$p] -ne $live[$p]) {
            [void]$changed.Add($p)
        }
    }
    foreach ($p in @($recorded.Keys)) {
        if (-not $live.ContainsKey($p)) { [void]$left.Add($p) }
    }
    return @{ Entered   = @($entered | Sort-Object)
              Left      = @($left    | Sort-Object)
              Changed   = @($changed | Sort-Object)
              Malformed = $malformed }
}

function Format-AdvisoryName($name) {
    # EVERY untrusted string printed by the explanation goes through
    # here, pathnames and exception text alike. The advisory manifest is
    # MUTABLE, so nothing in it passed Test-SupportedPathname.
    #
    # The test is the UNICODE CATEGORY, never a numeric range. Measured
    # 2026-09-05: `[int]$ch -lt 32` passes the C1 controls U+0085 and
    # U+009B, which are terminal escape introducers, and it passes
    # U+2028 and the bidirectional override U+202E, which manipulate how
    # the rest of the line displays. Control, Format, LineSeparator and
    # ParagraphSeparator cover all of them by name.
    $s = [string]$name
    if ($s.Length -gt 200) { $s = $s.Substring(0, 200) + "[truncated]" }
    $sb = New-Object System.Text.StringBuilder
    foreach ($ch in $s.ToCharArray()) {
        $cat = [System.Globalization.CharUnicodeInfo]::GetUnicodeCategory($ch)
        if (($cat -eq [System.Globalization.UnicodeCategory]::Control) -or
            ($cat -eq [System.Globalization.UnicodeCategory]::Format) -or
            ($cat -eq [System.Globalization.UnicodeCategory]::LineSeparator) -or
            ($cat -eq [System.Globalization.UnicodeCategory]::ParagraphSeparator) -or
            ($cat -eq [System.Globalization.UnicodeCategory]::Surrogate)) {
            [void]$sb.Append("\u" + ([int]$ch).ToString("x4"))
        } else {
            [void]$sb.Append($ch)
        }
    }
    return $sb.ToString()
}
```

**Why `Entered` and `Left` rather than `Appeared` and `Vanished`.** Manifest membership is not file existence. `Get-ManifestSubject` omits a deletion-only entry because it has no bytes (`tools/new-review-mirror.ps1:460-463`), and a clean tracked file that becomes dirty ENTERS the manifest without being created. Both files can exist the whole time. The labels name what the comparison actually measures.

- [ ] **Step 4: Add the explanation function**

Insert immediately after `Format-AdvisoryName`:

```powershell
function Write-SourceDriftExplanation($mirrorPath, $liveManifest) {
    # Runs ONLY after the source-status refusal below has been printed.
    #
    # THE WHOLE BODY IS WRAPPED. What protects the verdict is not any
    # property of this function - Write-Output emits into the pipeline
    # like any other command, and a caller COULD capture it - but the
    # fact that its one caller ignores the output and reaches `exit 1`
    # unconditionally. The wrap is here so that a fault in explaining a
    # refusal cannot replace that refusal with an error.
    try {
        $sidecar = Get-SourceManifestSidecarPath $mirrorPath
        if (-not $sidecar) {
            Write-Output ("  what moved: unknown - the mirror path is a" +
                " filesystem root, so no advisory manifest can sit beside it")
            return
        }
        $shown = Format-AdvisoryName $sidecar
        # ONE HANDLE measures and reads. A separate Get-Item followed by
        # a separate ReadAllBytes bounds nothing: the file can grow or be
        # replaced between them, and Get-Item's failure is NON-TERMINATING
        # in this script, which never sets $ErrorActionPreference, so an
        # unreadable file left the size test unmade and carried on.
        $limit = 67108864
        $bytes = $null
        $fs = [System.IO.File]::Open($sidecar, 'Open', 'Read', 'Read')
        try {
            if ($fs.Length -gt $limit) {
                Write-Output ("  what moved: unknown - the advisory manifest" +
                    " at " + $shown + " is " + $fs.Length + " bytes, past" +
                    " this reader's limit")
                return
            }
            $bytes = New-Object byte[] ([int]$fs.Length)
            $off = 0
            while ($off -lt $bytes.Length) {
                $n = $fs.Read($bytes, $off, $bytes.Length - $off)
                if ($n -le 0) { break }
                $off += $n
            }
        } finally { $fs.Dispose() }
        # DECODE THE BYTES EXPLICITLY. A StreamReader detects a byte-order
        # mark and consumes it, so a first pathname that legitimately
        # begins with U+FEFF would lose that character silently and read
        # as a different path.
        $text = (New-Object System.Text.UTF8Encoding($false, $true)).GetString($bytes)
        $recorded = @($text -split "`r`n|`n|`r")
        $drift = Get-ManifestDrift $recorded $liveManifest
        Write-Output ("  the lines below come from an UNAUTHENTICATED file" +
            " beside the mirror (" + $shown + ") and are advisory only")
        if ($drift.Malformed -gt 0) {
            Write-Output ("  note: " + $drift.Malformed + " advisory record(s)" +
                " could not be read, so this explanation is incomplete")
        }
        $groups = @(@("content changed", $drift.Changed),
                    @("entered manifest coverage", $drift.Entered),
                    @("left manifest coverage", $drift.Left))
        $any = $false
        foreach ($g in $groups) {
            $names = @($g[1])
            if ($names.Count -eq 0) { continue }
            $any = $true
            Write-Output ("  " + $g[0] + " (" + $names.Count + "):")
            $printed = 0
            foreach ($n in $names) {
                if ($printed -ge 20) {
                    Write-Output ("    ... and " + ($names.Count - 20) + " more")
                    break
                }
                Write-Output ("    " + (Format-AdvisoryName $n))
                $printed++
            }
        }
        if (-not $any) {
            Write-Output ("  what moved: the advisory manifest did not" +
                " identify the cause. It records no content difference," +
                " which is also what a stale or replaced manifest records.")
        }
    } catch {
        Write-Output ("  what moved: unknown - the advisory explanation" +
            " failed (" + (Format-AdvisoryName $_.Exception.Message) + ")")
    }
}
```

**Why the fallback no longer names a cause.** An earlier draft concluded that no content difference meant the status listing itself had changed. A replaced or stale sidecar produces the same empty result, so the inference does not hold. A mutable advisory file cannot establish a cause, and this line now says only what it knows.

**What the reader still does not do, stated rather than implied.** It opens whatever the sidecar path resolves to and does not refuse a file link pointing elsewhere. The consequence is bounded: worst case the explanation prints misleading names from an unrelated file, which is why the header line above it says the source is unauthenticated, and why the refusal itself never depends on any of this.

- [ ] **Step 5: Call it from the refusal**

In the verify block, insert one line between the existing `Write-Output` of the source-status refusal and its `exit 1` (currently `:846-851`):

```powershell
        Write-SourceDriftExplanation $MirrorPath $liveStatus.Manifest
```

The refusal's own wording does not change, so the existing `"source status" in proc.stdout.lower()` assertions stay green.

- [ ] **Step 6: Run the tests and confirm they pass**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -k "refusal or advisory or manifest or coverage or reader" -v`

Expected: all PASS, at the collected count checked in Step 2.

- [ ] **Step 7: Run the whole mirror module for regressions**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -q`

Expected: all PASS.

- [ ] **Step 8: Confirm the file is still ASCII**

Run: `python -c "d=open('tools/new-review-mirror.ps1','rb').read(); bad=[i for i,b in enumerate(d) if b>127]; print('non-ascii at', bad[:5] if bad else 'none')"`

Expected: `non-ascii at none`.

- [ ] **Step 9: Commit**

```bash
git add tools/new-review-mirror.ps1 evals/multi-model-verify/test_review_mirror.py
git commit -m "name the paths that moved when the source status refusal fires"
```

---

### Task 3: The skill states the quiet period

**Files:**
- Modify: `skills/multi-model-verify/SKILL.md` (a new contract region in the mirror build step of preflight item 3, immediately after the `back-channel-auto-mirror` region's `contract:end`)
- Modify: `evals/multi-model-verify/test_multi_model_verify.py` (a new pin in `TestSkillStructure`, beside `test_client_context_probe_failure_rule_is_pinned`)
- Modify: `evals/multi-model-verify/test_contract_coverage.py` (`DECLARED_REGIONS`)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: contract region id `mirror-quiet-period` in `SKILL.md`.

- [ ] **Step 1: Write the region into SKILL.md**

Insert this block into `skills/multi-model-verify/SKILL.md` immediately after the `<!-- contract:end -->` that closes the `back-channel-auto-mirror` region, at the same three-space indent as the text around it:

```markdown
   <!-- contract:start id=mirror-quiet-period -->
   NOTHING MAY WRITE INSIDE THE REVIEWED REPOSITORY from the moment the
   mirror is built until the wrapper exits. The identity digest covers the
   fields of `git status --porcelain --ignored` PLUS the content of the
   paths that listing names, ignored ones included, with a directory
   expanded to its files and a deletion-only entry contributing no bytes.
   So a test-cache write, a plan-ledger append, a drift report or one new
   untracked file is enough. The same recorded digest is compared against
   the live source three times: at preparation, before the client runs,
   and after it finishes. The last of those spans the whole round, so this
   is a quiet period and not an ordering rule. Only that last one costs a
   reviewer round; the two before it refuse before the client is invoked
   and spend no quota. State the limits with the rule: the comparison
   samples endpoints, so a change made and reverted inside the round is
   not detected, and a tracked file git reports CLEAN is covered by
   neither fingerprint. Queue every edit until the wrapper exits, however
   small and however unrelated it looks.
   <!-- contract:end -->
```

- [ ] **Step 2: Write the failing pin**

Add to `evals/multi-model-verify/test_multi_model_verify.py`, in `TestSkillStructure` directly after `test_client_context_probe_failure_rule_is_pinned`:

```python
    def test_mirror_quiet_period_is_pinned(self):
        # The whole-body pin for the contract region. The rule existed
        # only in this repo's CLAUDE.md, covering preparation to wrapper
        # exit, so the plugin did not carry it to the repos it is
        # installed into and a session there hit the refusal repeatedly
        # with nothing to read.
        text = read(SKILL_MD)
        assert (
            "   NOTHING MAY WRITE INSIDE THE REVIEWED REPOSITORY from the moment the\n"
            "   mirror is built until the wrapper exits. The identity digest covers the\n"
            "   fields of `git status --porcelain --ignored` PLUS the content of the\n"
            "   paths that listing names, ignored ones included, with a directory\n"
            "   expanded to its files and a deletion-only entry contributing no bytes.\n"
            "   So a test-cache write, a plan-ledger append, a drift report or one new\n"
            "   untracked file is enough. The same recorded digest is compared against\n"
            "   the live source three times: at preparation, before the client runs,\n"
            "   and after it finishes. The last of those spans the whole round, so this\n"
            "   is a quiet period and not an ordering rule. Only that last one costs a\n"
            "   reviewer round; the two before it refuse before the client is invoked\n"
            "   and spend no quota. State the limits with the rule: the comparison\n"
            "   samples endpoints, so a change made and reverted inside the round is\n"
            "   not detected, and a tracked file git reports CLEAN is covered by\n"
            "   neither fingerprint. Queue every edit until the wrapper exits, however\n"
            "   small and however unrelated it looks."
        ) in text
```

If Step 1's block was reflowed on the way in, this pin fails on the wrap and not on the words. Copy the lines out of `SKILL.md` rather than out of this plan if they differ.

- [ ] **Step 3: Declare the region**

In `evals/multi-model-verify/test_contract_coverage.py`, add to `DECLARED_REGIONS` after `"client-probe-scope-limit",`:

```python
    # 0.33.0: the quiet period the mirror identity digest enforces. It
    # lived only in this repo's CLAUDE.md, so the plugin did not carry it
    # anywhere it was installed.
    "mirror-quiet-period",
```

- [ ] **Step 4: Run the pin and the coverage checker**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py::TestSkillStructure::test_mirror_quiet_period_is_pinned evals/multi-model-verify/test_contract_coverage.py -v`

Expected: both PASS. A `region(s) found but not declared` failure means Step 3 was skipped. A `not locked by any pin` failure means the pin text and the Markdown text differ.

- [ ] **Step 5: Run the skill gates**

Run: `python evals/tools/skill_lint.py skills/multi-model-verify --strict && python evals/tools/skill_scanner.py skills`

Expected: both clean.

- [ ] **Step 6: Commit**

```bash
git add skills/multi-model-verify/SKILL.md evals/multi-model-verify/test_multi_model_verify.py evals/multi-model-verify/test_contract_coverage.py
git commit -m "state the mirror quiet period in the skill and lock it"
```

---

### Task 4: The build is ordered last, and the window is filed

**Files:**
- Modify: `skills/multi-model-verify/references/preflight-mirror.md`
- Modify: `BACKLOG.md`
- Test: `evals/multi-model-verify/test_multi_model_verify.py`

**Interfaces:**
- Consumes: the `mirror-quiet-period` region id from Task 3, cited by the new reference text.
- Produces: backlog item 94.

- [ ] **Step 1: Write the failing test for the timing rule**

Add to `evals/multi-model-verify/test_multi_model_verify.py`, in `TestSkillStructure`:

```python
    def test_preflight_mirror_orders_the_build_last(self):
        # The reference stated no timing constraint at all, so a session
        # could build the mirror, run its gates, append its ledger, and
        # then dispatch into a refusal it had itself caused.
        text = read(REFERENCES / "preflight-mirror.md")
        assert "BUILD THE MIRROR LAST" in text
        assert "mirror-quiet-period" in text
```

- [ ] **Step 2: Run it and confirm it fails**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -k orders_the_build_last -v`

Expected: FAIL on the missing `BUILD THE MIRROR LAST`.

- [ ] **Step 3: Add the timing rule**

Append to `skills/multi-model-verify/references/preflight-mirror.md`, as a new final section:

```markdown
## Timing

BUILD THE MIRROR LAST. Every act that writes inside the reviewed
repository finishes first: the gates, the plan ledger, the scratch notes,
the formatter. From the build until the round's wrapper exits, the
repository is quiet, and SKILL.md's `mirror-quiet-period` region states
why. The identity digest covers the content of ignored paths, so a
pytest cache directory or a ledger append is enough to refuse the
dispatch.

A build that has gone stale is not repaired and cannot be re-blessed:
there is deliberately no re-mint or reseal mode. READ THE EXPLANATION
FIRST, then build again. Rebuilding replaces the evidence of what
changed, so a rebuild before reading turns a diagnosable refusal into an
unexplained one. The rebuild itself is cheap next to a spent round,
measured at about 92 seconds on a repo carrying a linked reference
checkout.

When a refusal names `the source status changed since construction`, the
lines beneath it name the paths whose content changed and the paths that
entered or left manifest coverage, read from the `source_manifest` file
the record block points at. That explanation is advisory: it can be
missing, incomplete or wrong, and the refusal stands either way.
Manifest coverage is not file existence, so a path listed as leaving
coverage has not necessarily been deleted.

The two refusals raised by the round wrapper itself print no explanation
to the console. The wrapper redirects both identity checks into
`mirror.verify` inside its dispatch directory and then throws a short
message, so that file is where the detail is.
```

- [ ] **Step 4: Run the test and confirm it passes**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -k orders_the_build_last -v`

Expected: PASS.

- [ ] **Step 5: File backlog item 94**

Append to `BACKLOG.md`, after item 93, using the field order `Status`, `Cost`, `Pairs`, `Verified` that the linter requires for an OPEN item:

```markdown
## 94. The identity digest covers working state that moves on its own
Status: OPEN
Cost: every round is exposed for its whole duration to a write into an ignored working directory it does not control, and a write that persists past the post-client check costs one round of quota
Pairs: 76, 91
Verified: <run the digest command in Step 6 and paste the value here>

**Filed 2026-09-05 from a report by a session running the plugin against
another repository**, which hit repeated
`BLOCKED: the source status changed since construction` refusals and
could not tell why. Design:
`docs/superpowers/specs/2026-09-05-mirror-identity-window-design.md`.

`Get-StatusSha256` fingerprints the content of every path
`git status --porcelain --ignored` names, and `Get-ContentManifest`
expands a directory subject recursively, so one `!! .claude/` entry
pulls in every file beneath it. The content half is deliberate and
load-bearing: editing an already-ignored file leaves the status listing
byte-identical, so a list-only digest would pass through exactly the
tampering the check exists to catch.

The exposure is the WHOLE ROUND, not the preparation gap. The recorded
digest is compared three times, and the third comparison runs after the
client finishes. In a repository whose ignored directories move on their
own, no ordering discipline closes that.

**What this cycle did and did not do.** The refusal now names the paths
that moved, the skill states the quiet period, and the reference orders
the build last. None of that narrows the digest, so the underlying
exposure is unchanged and this item stays OPEN.

**A candidate fix, rejected for now.** A declared allowlist of volatile
ignored paths held outside the content digest. Rejected because the
directories that move on their own, `.claude/` and `.codex/`, are
instruction surfaces, and excluding an instruction surface from the
tamper net defeats the check. Closing this item means a design that
narrows the digest without opening that hole, argued in the
`mirror-identity-gate` contract region and debated on its own.
```

- [ ] **Step 5a: File backlog item 95 for the pre-existing findings**

The plan debate's reviewer swept the class it was asked to sweep and found defects that PREDATE this range. The debate protocol's scope rule says to RECORD anything not of the same class on the same verification surface, so they are filed rather than fixed. Append after item 94:

```markdown
## 95. Three stated properties of the mirror tools that the code does not hold
Status: OPEN
Cost: each one is a promise a reader relies on, and one of them can leave an extra input missing from a mirror the digest then certifies
Pairs: 94
Verified: <run the digest command in Step 6 and paste the value here>

**Filed 2026-09-05 from the plan debate for item 94's cycle**, whose
reviewer was asked to sweep for stated properties the code does not hold.
Record:
`docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window/`.
All three were confirmed against the code by the session before filing.

1. **The header's absolute promise.** `tools/new-review-mirror.ps1:19`
   says the script never writes to the real tree. The directory-link
   guard at `:1101-1112` says git's optional index refresh writes the
   repository's own `.git/index` during every status capture, and refuses
   a linked `.git` for exactly that reason. Qualify the promise or
   suppress the write.

2. **`-ExtraInput` can fail silently.** `tools/new-review-mirror.ps1:1554`
   copies each extra input with `Copy-Item -Force`, with no success check
   and no `-ErrorAction Stop`, and the script never sets
   `$ErrorActionPreference` (its own comment at `:519` says so). A
   non-terminating copy failure leaves the input absent, and the manifest
   cannot discover a file that never entered status. The tool then
   certifies a mirror missing a declared review input.

3. **The verify's same-directory refusal checks spelling.** The
   comparison at `tools/new-review-mirror.ps1:734-745` normalizes two
   provider-resolved strings and compares them, with none of the
   reparse-point resolution the build performs. A junction whose
   spelling differs can reach the same directory, so the refusal is
   narrower than the comment claims.

4. **Construction claims an endpoint comparison cannot support.** The
   comment at `tools/new-review-mirror.ps1:1308` says the retained value
   distinguishes a source that moved and moved back. Two equal endpoint
   measurements cannot establish that. The identity contract already
   admits that intermediate bytes can reach the copy despite matching
   endpoints; this comment has not been aligned with it.

5. **A wrapper verification failure cannot report the classification it
   promises.** Both identity checks in the generated wrapper `throw`
   (`tools/dispatch-round.ps1:287` and `:311`), which exits before
   `-Classify` runs, so the documented exit map does not describe that
   path.

**Corroborated by the plan debate's reviewer with citations, NOT
independently re-checked by the session.** Confirm each before acting on
it: the generated wrapper is written as ASCII so a non-ASCII path
component is lost (`tools/dispatch-round.ps1:570`); the printed command
places paths in expandable double-quoted strings without escaping `$`
(`:591`); `classifying:<nonce>` redemption is a read-then-write with no
exclusive reservation (`:663`); a receipt write that fails after creation
leaves a partial receipt against a documented "no receipt" (`:572`); and
an oversized integer in `exit` passes the regex and throws during
conversion instead of following the classification map (`:794`).

**One earlier report is NOT filed here, deliberately.** The voided round
raised `Test-SupportedPathname` admitting U+FEFF as a defect. It is not
one on its own: it mattered only because the first draft's advisory
reader detected and consumed a byte-order mark, and Task 2 replaces that
reader with explicit byte decoding. Admitting U+FEFF in a pathname is
correct behaviour.
```

- [ ] **Step 6: Compute the item's digest and fill it in**

Run: `python evals/tools/backlog_lint.py --digests BACKLOG.md`

Copy the digest printed for item 94 into its `Verified:` line, after the date `2026-09-05`, and the same for item 95.

- [ ] **Step 7: Run the backlog linter**

Run: `python evals/tools/backlog_lint.py`

Expected: exit 0. Every failure is printed, not only the first, so fix them all before re-running.

- [ ] **Step 8: Commit**

```bash
git add skills/multi-model-verify/references/preflight-mirror.md BACKLOG.md evals/multi-model-verify/test_multi_model_verify.py
git commit -m "order the mirror build last and file the identity window"
```

---

### Task 5: The full gate, on both PowerShell hosts

**Files:**
- No source changes. This task produces evidence only.

**Interfaces:**
- Consumes: everything from Tasks 1 to 4.
- Produces: the gate results the diff debate cites.

- [ ] **Step 1: Run the six CI tiers**

Run each, in this order, and record the output of every one:

```
python evals/tools/skill_lint.py skills/multi-model-verify --strict
python evals/tools/skill_scanner.py skills
python evals/tools/check_exact_line_oracles.py
python evals/tools/run_trigger_evals.py
python -m pytest evals -q
python evals/tools/backlog_lint.py
```

Expected: all six clean. Do not pipe any of these through `tail`, `head`, or `Select-Object -Last`: the failure names are what a second run needs.

- [ ] **Step 2: Run the mirror module under the other PowerShell host**

The suite picks whichever host it finds first, so a green run proves one interpreter. Set the other explicitly:

```powershell
$env:PARALLAX_PS_HOST = "pwsh"; python -m pytest evals/multi-model-verify/test_review_mirror.py -q
```

Then the same with `"powershell"`. Expected: PASS on both. Run this in the BACKGROUND: backlog item 93 measured this module at 18m42s under PowerShell 7 against 94s under Windows PowerShell 5.1.

- [ ] **Step 3: Run the behavioural suite for the changed surface**

Skill and prompt text changed, so this local-only suite applies:

```
python evals/tools/run_behavioral_evals.py --changed
```

Expected: PASS, with every skip printed by name.

- [ ] **Step 4: Commit the gate record**

```bash
git add -A
git commit -m "retain the gate results for the mirror identity window"
```

---

## Self-review

**Spec coverage.** D1 (no gate change) is carried by the Global Constraints and by Task 2's two advisory-direction tests. D2 and D2b (the advisory explanation and its bounds) are Tasks 1 and 2. D2a (the destination guards, in both the lexical and the alias block, validating before removing) is Task 1 Steps 5a, 5b and 5c. D3 (quiet period in the skill) is Task 3. D4 (build ordered last) is Task 4. Every success criterion in the spec has a named test in Task 1 Step 1 or Task 2 Step 1, except the six-tier and two-host criteria, which are Task 5.

**Placeholders.** Two values are deliberately left to be computed rather than guessed: the `Verified:` digests for items 94 and 95, in Task 4 Step 6, because each is a hash of its own item's final text and cannot exist before that text does. The command that produces them is given.

**Type consistency.** `Get-StatusSha256` gains `Manifest` in Task 1 and Task 2 reads `$liveStatus.Manifest`. `Get-SourceManifestSidecarPath` is defined in Task 1 and called by Task 1's guard block and by Task 2's `Write-SourceDriftExplanation`; it returns `$null` for a root and both callers handle that. `Get-ManifestDrift` returns `Entered`, `Left`, `Changed` and `Malformed`, and `Write-SourceDriftExplanation` reads exactly those four. `Format-AdvisoryName` is defined in Task 2 Step 3 and called in Step 4 for names, for the sidecar path and for exception text. The sidecar path `"<full mirror path>.source-manifest"` is derived in Task 1 Step 4 and asserted as `tmp_path / "mirror.source-manifest"` in both tasks' tests.

## After the plan

This plan does NOT bump `.claude-plugin/plugin.json`. Per `CLAUDE.md`, the bump comes after the diff debate, because the debate is what moves the tree last. The sequence after Task 5 is: whole-branch review, mode-diff debate, version bump, merge, marketplace refresh, plugin update, and an install verified by content rather than by the cache directory's name.
