# Mirror Identity Window Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the review mirror's identity refusal name the paths that moved, and ship the quiet-period rule that the refusal enforces, so a session outside this repo can act on both.

**Architecture:** Three independent changes and no change to the gate. The build writes the source side's content manifest to a sibling of the mirror directory, under the same destination guards `-OverrideOut` already carries; the source-status refusal reads that sibling, on that path only, to name what entered coverage, left coverage, or changed content; and the skill grows a contract region plus a timing rule stating that nothing may write inside the reviewed repository between the build and the wrapper's exit. The sidecar file is advisory: it is read after the comparison has already decided to block, so no state it can be in changes any exit code.

**Tech Stack:** Windows PowerShell 5.1 and PowerShell 7 (`tools/new-review-mirror.ps1`), Python 3 with pytest (`evals/multi-model-verify/`), Markdown contract regions under `skills/`.

**Spec:** `docs/superpowers/specs/2026-09-05-mirror-identity-window-design.md`

## Global Constraints

- `tools/new-review-mirror.ps1` is **Windows PowerShell 5.1 compatible and ASCII ONLY**. No smart quotes, no dashes outside the ASCII hyphen, no non-ASCII byte anywhere in the file.
- **No existing exit code may change in any existing case.** The gate stays fail-closed. Every new code path may only ADD printed output on a path that is already exiting 1.
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
- Modify: `tools/new-review-mirror.ps1` (the `Get-StatusSha256` return at `:662-694`, two new functions beside it, and the record block at `:1737-1756`)
- Test: `evals/multi-model-verify/test_review_mirror.py`

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces:
  - `Get-StatusSha256($repo)` returns `@{ Ok = $true; Sha = <hex>; Manifest = <string[]> }` on success, unchanged `@{ Ok = $false; Reason = <string> }` on failure. `Manifest` holds `Get-ContentManifest`'s lines, each `"<relpath> <sha256hex>"`.
  - `Get-SourceManifestSidecarPath($mirrorPath)` returns `"<parent>/<leaf>.source-manifest"`, or `$null` when the mirror path has no leaf name (a root such as `D:\`).
  - `Write-SourceManifestSidecar($path, $manifestLines)` returns `$true` or `$false`. It opens the file with `CreateNew`, so it can never write through an existing file or link.
  - The build's record block gains one line, `source_manifest: <path>`, printed after `override:`.

**Why this task is mostly guards.** The sidecar path is DERIVED, not supplied, and a derived string written without a guard is a write into whatever happens to sit there. A hard link or symbolic link at that path carries the write through to its target, and a target inside the repository would be corrupted by the very function that exists to explain a corrupted repository. Cross-vendor review of the first draft found that hole, and found that an explicitly supplied `-OverrideOut <MirrorPath>.source-manifest` passes today's checks and would then be silently overwritten, breaking the wrapper's override hash check.

The default override path is a sibling of exactly this shape, `<MirrorPath>.skills-override.txt`, resolved and guarded at `tools/new-review-mirror.ps1:956-973` and length-checked at `:1002-1008`. Copy that guard set. Do not invent a new one.

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
```

`run_mirror` already passes `-SkipProbe`, so `build_and_read` asserts the skip block rather than exit 0; the two refusal tests above call `run_mirror` directly because they must see exit 2 from a guard that fires BEFORE any build work.

- [ ] **Step 2: Run the tests and confirm they fail for the stated reason**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -k "source_manifest" -v`

Expected: `test_the_build_writes_the_source_manifest_beside_the_mirror` FAILS on the missing sidecar file. `test_the_source_manifest_sidecar_enters_neither_identity` PASSES already, because nothing writes a sidecar yet. That is correct: it is a regression guard for Step 3, not a red test.

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
    # A ROOT has no leaf name, and `Split-Path 'D:\' -Leaf` yields `D:`,
    # so the naive form derives the DRIVE-RELATIVE `D:.source-manifest`
    # rather than a sibling. That is not a path this tool can reason
    # about, so it is refused rather than guessed at.
    $leaf = Split-Path $mirrorPath -Leaf
    if ((-not $leaf) -or ($leaf -match '^[A-Za-z]:$')) { return $null }
    return (Join-Path (Split-Path $mirrorPath -Parent) `
        ($leaf + ".source-manifest"))
}

function Write-SourceManifestSidecar($path, $manifestLines) {
    # ADVISORY ONLY. It pins nothing and gates nothing, so a failure to
    # write it is not a build failure - it costs a later refusal its
    # explanation and nothing else. That is also why it may be a file at
    # all: the header's rule about values passed as arguments rather than
    # re-read from a file governs values that PIN something, and this
    # value carries no authority.
    #
    # CREATE-NEW, never WriteAllLines. The guards in the next step
    # resolved this path and refused a pre-existing one, but a file
    # created between that guard and this write is still possible, and an
    # overwrite through a hard link or symbolic link at this path would
    # carry into the link's target - a target that could be inside the
    # repository, corrupted by the function that exists to explain
    # corruption. Create-new fails instead, and a failure here costs only
    # the explanation.
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

- [ ] **Step 5: Guard the destination beside the override's guards**

Insert immediately AFTER the override's pre-existence refusal, the block ending `"a stale override reads exactly like a fresh one"` at `tools/new-review-mirror.ps1:970-973`, and BEFORE the `PATH BUDGET PRE-FLIGHT` comment. `$rr`, `$mp`, `$op` and `$cmp` are the normalized paths and the comparison mode the override guard above already set up:

```powershell
# THE ADVISORY SOURCE MANIFEST'S DESTINATION, resolved and guarded HERE,
# beside the override, for the same stated reason: a destination
# discovered after the build has copied, remediated and manifested is
# discovered too late, and -SkipProbe would bypass a check placed later.
$SourceManifestOut = Get-SourceManifestSidecarPath $MirrorPath
if (-not $SourceManifestOut) {
    Write-Output ("ERROR: the mirror path has no leaf name ($MirrorPath)" +
        " - a root-shaped path derives a drive-relative advisory manifest" +
        " rather than a sibling")
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
if (Test-Path -LiteralPath $SourceManifestOut) {
    if (Test-Path -LiteralPath $SourceManifestOut -PathType Container) {
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

Then add its length check immediately after the override's, the `if ($OverrideOut.Length -ge $PathBudget)` block at `:1002-1008`:

```powershell
# Written BESIDE the mirror by this script, not by robocopy, so the copy
# universe never covers it. Its own check or none - the override's rule.
if ($SourceManifestOut.Length -ge $PathBudget) {
    Write-Output ("ERROR: path budget exceeded by the source manifest - " +
        "$SourceManifestOut is $($SourceManifestOut.Length) characters " +
        "and the limit is $PathBudget")
    exit 2
}
```

- [ ] **Step 5a: Write the sidecar and record its path**

In the record block, insert immediately BEFORE the existing `Write-Output ("mirror: " + $MirrorPath)` line (currently `:1737`):

```powershell
# The advisory source manifest, written before the record so the record
# can name it. Its destination was guarded above; a failure to write it
# here is reported and never fatal.
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

- [ ] **Step 6: Run the tests and confirm they pass**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -k "source_manifest" -v`

Expected: both PASS.

- [ ] **Step 7: Run the whole mirror module for regressions**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -q`

Expected: all PASS. If the record-parsing tests fail, the new `source_manifest:` line was inserted inside a labelled block rather than after `override:`.

- [ ] **Step 8: Commit**

```bash
git add tools/new-review-mirror.ps1 evals/multi-model-verify/test_review_mirror.py
git commit -m "write the source content manifest beside the review mirror"
```

---

### Task 2: The source-status refusal names what moved

**Files:**
- Modify: `tools/new-review-mirror.ps1` (a new diff function and a new explanation function beside the sidecar functions, and the refusal at `:845-851`)
- Test: `evals/multi-model-verify/test_review_mirror.py`

**Interfaces:**
- Consumes: `Get-SourceManifestSidecarPath($mirrorPath)` and `Get-StatusSha256`'s `Manifest` field from Task 1.
- Produces:
  - `Get-ManifestDrift($recordedLines, $liveLines)` returns `@{ Appeared = <string[]>; Vanished = <string[]>; Changed = <string[]> }`, each sorted by path.
  - `Write-SourceDriftExplanation($mirrorPath, $liveManifest)` writes lines to stdout and returns nothing. It never throws and never exits.

- [ ] **Step 1: Write the failing tests**

Replace the existing `test_source_drift_in_an_ignored_file_blocks_the_dispatch` body's final assertion block and add five tests, all directly after it:

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
    raw strings, changes. The explanation must partition the same
    strings the digest does."""
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
    reaches the parser and the renderer with VALID records that name
    innocent files, which is the shape an attacker would actually use."""
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    (repo / "ignored" / "secret.txt").write_text("edited after the copy\n")
    forged = "\n".join(
        "decoy/%d.txt %064x" % (i, i) for i in range(5)) + "\n"
    (tmp_path / "mirror.source-manifest").write_text(forged)
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "source status" in proc.stdout.lower(), proc.stdout


def test_a_manifest_record_that_cannot_be_read_is_reported(tmp_path):
    """A dropped record is a difference the explanation would then fail
    to mention, which is the defect class this whole change removes."""
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    sidecar = tmp_path / "mirror.source-manifest"
    sidecar.write_text(sidecar.read_text() + "no-space-here\n")
    (repo / "ignored" / "secret.txt").write_text("edited after the copy\n")
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "could not be read" in proc.stdout, proc.stdout
    assert "incomplete" in proc.stdout, proc.stdout
```

- [ ] **Step 2: Run the tests and confirm they fail for the stated reason**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -k "refusal or source_manifest_still or no_source_manifest" -v`

Expected: the three naming tests and `test_a_missing_source_manifest_still_refuses` FAIL on the missing `changed` / `appeared` / `vanished` / `unknown` text. The two safety tests PASS already; they are regression guards.

- [ ] **Step 3: Add the diff function**

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
    # A line this parser cannot read is COUNTED, never silently dropped.
    # A dropped record is a difference this explanation would then fail
    # to mention, which is the shape of defect this whole change exists
    # to remove. The count is reported and the explanation says it is
    # incomplete.
    $ord = [System.StringComparer]::Ordinal
    $recorded = New-Object "System.Collections.Generic.Dictionary[string,string]" $ord
    $live = New-Object "System.Collections.Generic.Dictionary[string,string]" $ord
    $malformed = 0
    foreach ($side in @(@($recordedLines, $recorded), @($liveLines, $live))) {
        foreach ($line in @($side[0])) {
            $s = [string]$line
            if ($s.Trim().Length -eq 0) { continue }
            $cut = $s.LastIndexOf(" ")
            if ($cut -lt 1) { $malformed++; continue }
            $key = $s.Substring(0, $cut)
            # A DUPLICATE key is malformed input too. Assigning over it
            # would silently keep the last record and hide the first.
            if ($side[1].ContainsKey($key)) { $malformed++; continue }
            $side[1][$key] = $s.Substring($cut + 1)
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
    # The advisory manifest is MUTABLE, so a name inside it never passed
    # Test-SupportedPathname and may hold anything. A control character
    # reaching a terminal is an escape sequence, so every one is rendered
    # as \xNN, and the name is bounded.
    $s = [string]$name
    if ($s.Length -gt 200) { $s = $s.Substring(0, 200) + "[truncated]" }
    $sb = New-Object System.Text.StringBuilder
    foreach ($ch in $s.ToCharArray()) {
        if (([int]$ch -lt 32) -or ([int]$ch -eq 127)) {
            [void]$sb.Append("\x" + ([int]$ch).ToString("x2"))
        } else {
            [void]$sb.Append($ch)
        }
    }
    return $sb.ToString()
}
```

**Why `Entered` and `Left` rather than `Appeared` and `Vanished`.** Manifest membership is not file existence. `Get-ManifestSubject` omits a deletion-only entry because it has no bytes (`tools/new-review-mirror.ps1:460-463`), and a clean tracked file that becomes dirty ENTERS the manifest without being created. Both files can exist the whole time. The labels name what the comparison actually measures.

- [ ] **Step 4: Add the explanation function**

Insert immediately after `Get-ManifestDrift`:

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
            Write-Output ("  what moved: unknown - the mirror path has no" +
                " leaf name, so no advisory manifest path exists")
            return
        }
        if (-not (Test-Path -LiteralPath $sidecar -PathType Leaf)) {
            Write-Output ("  what moved: unknown - no advisory manifest at " +
                $sidecar)
            return
        }
        # BOUNDED. The file is mutable, so its size is someone else's
        # choice. 64 MB is far above any real manifest here and far below
        # a memory problem.
        $len = (Get-Item -LiteralPath $sidecar).Length
        if ($len -gt 67108864) {
            Write-Output ("  what moved: unknown - the advisory manifest at " +
                $sidecar + " is " + $len + " bytes, past this reader's limit")
            return
        }
        # DECODE THE BYTES EXPLICITLY. A StreamReader detects a byte-order
        # mark and consumes it, so a first pathname that legitimately
        # begins with U+FEFF - which Test-SupportedPathname admits - would
        # lose that character silently and read as a different path.
        $bytes = [System.IO.File]::ReadAllBytes($sidecar)
        $text = (New-Object System.Text.UTF8Encoding($false, $true)).GetString($bytes)
        $recorded = @($text -split "`r`n|`n|`r")
        $drift = Get-ManifestDrift $recorded $liveManifest
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
            $shown = 0
            foreach ($n in $names) {
                if ($shown -ge 20) {
                    Write-Output ("    ... and " + ($names.Count - 20) + " more")
                    break
                }
                Write-Output ("    " + (Format-AdvisoryName $n))
                $shown++
            }
        }
        if (-not $any) {
            Write-Output ("  what moved: the advisory manifest did not" +
                " identify the cause. It records no content difference," +
                " which is also what a stale or replaced manifest records.")
        }
    } catch {
        Write-Output ("  what moved: unknown - the advisory explanation" +
            " failed (" + $_.Exception.Message + ")")
    }
}
```

**Why the fallback no longer names a cause.** The first draft concluded that no content difference meant the status listing itself had changed. A replaced or stale sidecar produces the same empty result, so the inference does not hold. A mutable advisory file cannot establish a cause, and this line now says only what it knows.

- [ ] **Step 5: Call it from the refusal**

In the verify block, insert one line between the existing `Write-Output` of the source-status refusal and its `exit 1` (currently `:846-851`):

```powershell
        Write-SourceDriftExplanation $MirrorPath $liveStatus.Manifest
```

The refusal's own wording does not change, so the existing `"source status" in proc.stdout.lower()` assertions stay green.

- [ ] **Step 6: Run the tests and confirm they pass**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -k "refusal or source_manifest_still or no_source_manifest" -v`

Expected: all six PASS.

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
   CONTENT of every path `git status --porcelain --ignored` names, ignored
   ones included, so a test-cache write, a plan-ledger append, a drift
   report or one new untracked file is enough. The same recorded digest is
   compared against the live source three times: at preparation, before the
   client runs, and after it finishes. The last of those spans the whole
   round, so this is a quiet period and not an ordering rule. Only that
   last one costs a reviewer round; the two before it refuse before the
   client is invoked and spend no quota. State the limits with the rule:
   the comparison samples endpoints, so a change made and reverted inside
   the round is not detected, and a tracked file git reports CLEAN is
   covered by neither fingerprint. Queue every edit until the wrapper
   exits, however small and however unrelated it looks.
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
            "   CONTENT of every path `git status --porcelain --ignored` names, ignored\n"
            "   ones included, so a test-cache write, a plan-ledger append, a drift\n"
            "   report or one new untracked file is enough. The same recorded digest is\n"
            "   compared against the live source three times: at preparation, before the\n"
            "   client runs, and after it finishes. The last of those spans the whole\n"
            "   round, so this is a quiet period and not an ordering rule. Only that\n"
            "   last one costs a reviewer round; the two before it refuse before the\n"
            "   client is invoked and spend no quota. State the limits with the rule:\n"
            "   the comparison samples endpoints, so a change made and reverted inside\n"
            "   the round is not detected, and a tracked file git reports CLEAN is\n"
            "   covered by neither fingerprint. Queue every edit until the wrapper\n"
            "   exits, however small and however unrelated it looks."
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
Cost: every round is exposed for its whole duration to a write into an ignored working directory it does not control, and each such write costs one round of quota
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

**Reported in the same round and NOT yet verified**, listed so a later
session checks rather than re-derives them: the generated wrapper is
written as ASCII so a non-ASCII path component would be lost; the printed
command places paths in expandable double-quoted strings without escaping
`$`; `classifying:<nonce>` redemption is a read-then-write with no
exclusive reservation; a receipt write that fails after creation leaves a
partial receipt against a documented "no receipt"; an oversized integer
in `exit` passes the regex and throws in conversion instead of following
the classification map; and `Test-SupportedPathname` admits U+FEFF, which
a byte-order-mark-detecting reader would consume. Verify each before
acting on it.
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

**Spec coverage.** D1 (no gate change) is carried by the Global Constraints and by Task 2's two safety tests. D2 (advisory explanation) is Tasks 1 and 2. D3 (quiet period in the skill) is Task 3. D4 (build ordered last) is Task 4. The spec's success criteria map to Task 2 Step 6, Task 2 Step 1's two safety tests, Task 3 Step 4, and Task 5.

**Placeholders.** One value is deliberately left to be computed rather than guessed: item 94's `Verified:` digest, in Task 4 Step 6, because it is a hash of the item's own final text and cannot exist before that text does. The command that produces it is given.

**Type consistency.** `Get-StatusSha256` gains `Manifest` in Task 1 and Task 2 reads `$liveStatus.Manifest`. `Get-SourceManifestSidecarPath` is defined in Task 1 and called in Task 2's `Write-SourceDriftExplanation`. The sidecar path `"<mirrorPath>.source-manifest"` is written in Task 1 Step 4 and asserted as `tmp_path / "mirror.source-manifest"` in both tasks' tests.

## After the plan

This plan does NOT bump `.claude-plugin/plugin.json`. Per `CLAUDE.md`, the bump comes after the diff debate, because the debate is what moves the tree last. The sequence after Task 5 is: whole-branch review, mode-diff debate, version bump, merge, marketplace refresh, plugin update, and an install verified by content rather than by the cache directory's name.
