# Mirror Identity Window Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the review mirror's identity refusal name the paths that moved, and ship the quiet-period rule that the refusal enforces, so a session outside this repo can act on both.

**Architecture:** Three independent changes and no change to the gate. The build writes the source side's content manifest to a sibling of the mirror directory; the source-status refusal reads that sibling, on that path only, to name what appeared, vanished, or changed content; and the skill grows a contract region plus a timing rule stating that nothing may write inside the reviewed repository between the build and the wrapper's exit. The sidecar file is advisory: it is read after the comparison has already decided to block, so no state it can be in changes any exit code.

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
  - `Get-SourceManifestSidecarPath($mirrorPath)` returns `"<mirrorPath>.source-manifest"`.
  - `Write-SourceManifestSidecar($path, $manifestLines)` returns `$true` or `$false`, never throws.
  - The build's record block gains one line, `source_manifest: <path>`, printed after `override:`.

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
```

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
    return ($mirrorPath.TrimEnd("\", "/") + ".source-manifest")
}

function Write-SourceManifestSidecar($path, $manifestLines) {
    # ADVISORY ONLY. It pins nothing and gates nothing, so a failure to
    # write it is not a build failure - it costs a later refusal its
    # explanation and nothing else. That is also why it may be a file at
    # all: the header's rule about values passed as arguments rather than
    # re-read from a file governs values that PIN something, and this
    # value carries no authority.
    try {
        $utf8 = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllLines($path, [string[]]@($manifestLines), $utf8)
        return $true
    } catch {
        return $false
    }
}
```

- [ ] **Step 5: Write the sidecar and record its path**

In the record block, insert immediately BEFORE the existing `Write-Output ("mirror: " + $MirrorPath)` line (currently `:1737`):

```powershell
# The advisory source manifest, written before the record so the record
# can name it. Its failure is reported and never fatal.
$sidecarPath = Get-SourceManifestSidecarPath $MirrorPath
if (-not (Write-SourceManifestSidecar $sidecarPath $sourceStatus.Manifest)) {
    $sidecarPath = "unwritable"
}
```

Then insert one line immediately AFTER the existing `Write-Output ("override: " + $overrideFile)` line:

```powershell
Write-Output ("source_manifest: " + $sidecarPath)
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
    assert "changed" in proc.stdout, proc.stdout
    assert "ignored/secret.txt" in proc.stdout, proc.stdout


def test_the_refusal_names_a_file_that_appeared(tmp_path):
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    (repo / "brand-new-input.txt").write_text("appeared after the copy\n")
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "appeared" in proc.stdout, proc.stdout
    assert "brand-new-input.txt" in proc.stdout, proc.stdout


def test_the_refusal_names_a_file_that_vanished(tmp_path):
    repo = make_repo(tmp_path)
    mirror = tmp_path / "mirror"
    _, ident = build_and_read(repo, mirror)
    (repo / "ignored" / "secret.txt").unlink()
    proc = run_verify(repo, mirror, ident)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert "vanished" in proc.stdout, proc.stdout
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
    # A line this parser cannot read is DROPPED rather than raised. This
    # function runs only on a path that is already refusing, and a bad
    # explanation must never replace a correct refusal with an error.
    $recorded = @{}
    foreach ($line in @($recordedLines)) {
        $cut = ([string]$line).LastIndexOf(" ")
        if ($cut -lt 1) { continue }
        $recorded[([string]$line).Substring(0, $cut)] = ([string]$line).Substring($cut + 1)
    }
    $live = @{}
    foreach ($line in @($liveLines)) {
        $cut = ([string]$line).LastIndexOf(" ")
        if ($cut -lt 1) { continue }
        $live[([string]$line).Substring(0, $cut)] = ([string]$line).Substring($cut + 1)
    }
    $appeared = New-Object System.Collections.ArrayList
    $vanished = New-Object System.Collections.ArrayList
    $changed = New-Object System.Collections.ArrayList
    foreach ($p in @($live.Keys)) {
        if (-not $recorded.ContainsKey($p)) {
            [void]$appeared.Add($p)
        } elseif ($recorded[$p] -ne $live[$p]) {
            [void]$changed.Add($p)
        }
    }
    foreach ($p in @($recorded.Keys)) {
        if (-not $live.ContainsKey($p)) { [void]$vanished.Add($p) }
    }
    return @{ Appeared = @($appeared | Sort-Object)
              Vanished = @($vanished | Sort-Object)
              Changed  = @($changed  | Sort-Object) }
}
```

- [ ] **Step 4: Add the explanation function**

Insert immediately after `Get-ManifestDrift`:

```powershell
function Write-SourceDriftExplanation($mirrorPath, $liveManifest) {
    # Runs ONLY after the source-status refusal below has been printed.
    # It prints what moved, or says plainly that it could not tell. It
    # never throws, never exits, and never returns a value a caller
    # could branch on, so no state of the sidecar can change a verdict.
    $sidecar = Get-SourceManifestSidecarPath $mirrorPath
    $recorded = $null
    try {
        if (Test-Path -LiteralPath $sidecar -PathType Leaf) {
            $recorded = [System.IO.File]::ReadAllLines($sidecar,
                (New-Object System.Text.UTF8Encoding($false, $true)))
        }
    } catch {
        $recorded = $null
    }
    if ($null -eq $recorded) {
        Write-Output ("  what moved: unknown - no readable source manifest" +
            " at " + $sidecar)
        return
    }
    $drift = Get-ManifestDrift $recorded $liveManifest
    $groups = @(@("changed", $drift.Changed),
                @("appeared", $drift.Appeared),
                @("vanished", $drift.Vanished))
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
            Write-Output ("    " + $n)
            $shown++
        }
    }
    if (-not $any) {
        Write-Output ("  what moved: no content difference, so the status" +
            " listing itself changed - a path took a different status" +
            " code, or a deletion-only entry moved. Those carry no bytes" +
            " and so appear in no manifest.")
    }
}
```

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
   round, so this is a quiet period and not an ordering rule. A round that
   trips it is refused, its reply is NOT evidence, and the quota is spent
   for nothing. Queue every edit until the wrapper exits, however small and
   however unrelated it looks.
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
            "   round, so this is a quiet period and not an ordering rule. A round that\n"
            "   trips it is refused, its reply is NOT evidence, and the quota is spent\n"
            "   for nothing. Queue every edit until the wrapper exits, however small and\n"
            "   however unrelated it looks."
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
there is deliberately no re-mint or reseal mode. Build again. It is
cheap next to a spent round, measured at about 92 seconds on a repo
carrying a linked reference checkout.

When a refusal names `the source status changed since construction`, the
lines beneath it name the paths that changed, appeared or vanished,
read from the `source_manifest` file the record block points at. That
explanation is advisory: it can be missing or wrong and the refusal
stands either way.
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

- [ ] **Step 6: Compute the item's digest and fill it in**

Run: `python evals/tools/backlog_lint.py --digests BACKLOG.md`

Copy the digest printed for item 94 into its `Verified:` line, after the date `2026-09-05`.

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
