# Diff debate round-1 fix report, branch mirror-parent

Worktree: C:\Users\Brandon\Documents\_worktrees\parallax-mirror-parent
Base head before fix: ecd4362
Commit after fix: f073752 "refuse an explicitly empty reap argument instead
of reading it as no reap, and drive both parameters on both hosts"

## F1 - tools/write-attestation.ps1, REAP VALIDATION block (lines ~294-307)

Replaced the three truthiness tests (`if ($ReapMirror -or $ReapBridge)`,
`if ($ReapMirror)`, `if ($ReapBridge)`) with `$PSBoundParameters.ContainsKey(...)`
checks (`$reapMirrorGiven`, `$reapBridgeGiven`). An explicitly empty
`-ReapMirror ""` / `-ReapBridge ""` now reaches `Resolve-MirrorParent` and
`Resolve-ReapPath` instead of being read as "no reap was requested" by an
empty-string truthiness test. The `$reapMirrorFull = $null` /
`$reapBridgeFull = $null` declaration lines above were left untouched, as
directed.

Checked the header comment (lines 17-32) and the param-block comments
(lines 40-59): neither describes the reap parameters' entry condition as
"when present" or similar (the one "When present" sentence at line 52
describes `-CheckpointFile`, an unrelated parameter) — nothing needed
changing there.

Checked the write-then-reap tail (lines 387 and 438): it tests
`$reapMirrorFull` / `$reapBridgeFull` (the resolved values), not the raw
`$ReapMirror` / `$ReapBridge` parameters. Confirmed correct as-is; no
INPUT GAP.

## F2 - evals/multi-model-verify/test_mirror_reaper.py, Group 7

Added `test_an_explicitly_empty_reap_argument_is_refused_not_ignored`,
parametrized over `-ReapMirror` / `-ReapBridge`, immediately after
`test_a_roots_tool_that_exits_nonzero_refuses_every_reap` and before the
"Group 6" divider comment, verbatim from the brief.

RED evidence (both hosts, before the F1 fix landed):

```
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_mirror_reaper.py -q -k test_an_explicitly_empty_reap_argument_is_refused_not_ignored
```
Result: 2 failed. Both `[-ReapMirror]` and `[-ReapBridge]` cases got
`proc.returncode == 0` and the assertion failure message showed
`attestation written: ...\attestations\<sha>.json (PASS, ...)` — i.e. today
the record is written with no error, exactly the defect the brief
describes.

```
$env:PARALLAX_PS_HOST = "pwsh.exe"; python -m pytest evals/multi-model-verify/test_mirror_reaper.py -q -k test_an_explicitly_empty_reap_argument_is_refused_not_ignored
```
Result: 2 failed, same shape (returncode 0, attestation written) on both
`[-ReapMirror]` and `[-ReapBridge]`.

`run_ps` delivered the empty argument correctly on both hosts (the
parameter bound as an empty string, not as unbound) — no INPUT GAP.

## F3 - docs/superpowers/plans/2026-09-13-mirror-parent.md, Task 2 Step 2(e)

Inserted the exact bracketed correction paragraph immediately after the
replacement code block ending `if ($ReapBridge) { $reapBridgeFull = ... }`
and before "Step 3: Run the module under both hosts". Nothing else in the
plan was edited.

## GREEN evidence (both hosts, after F1 landed)

```
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_mirror_reaper.py evals/multi-model-verify/test_attestation.py evals/multi-model-verify/test_artifact_roots.py -q
```
Result: `146 passed in 97.29s`

```
$env:PARALLAX_PS_HOST = "pwsh.exe"; python -m pytest evals/multi-model-verify/test_mirror_reaper.py evals/multi-model-verify/test_attestation.py evals/multi-model-verify/test_artifact_roots.py -q
```
Result: `146 passed in 108.20s`

## Staged blob check

`git show :tools/write-attestation.ps1` piped through a non-ASCII byte
scan: clean (no bytes outside 0x00-0x7F). Piped through `file -`: reports
`ASCII text` (not "with CRLF line terminators"). A CR byte count on the
same blob content returned 0. Confirms the committed blob is ASCII and
LF, independent of the CRLF working tree under `core.autocrlf=true` (git
even warned "LF will be replaced by CRLF" on the plan file at `git add`,
consistent with autocrlf normalizing the working tree while the blob
stays LF).

## C:\pxm listing (after the full verification run)

```
8904109a
k10392
k92104
kvs-pxmp
pxmp
pxmp.source-manifest
```
Matches the brief's expected set exactly — only the three pre-existing
directories plus `kvs-pxmp`, `pxmp`, and the `pxmp.source-manifest`
sidecar. No leftover fixture trees (`kv-t`, `t-*`, etc.) from the test
runs.

## Commit

Staged by explicit path only (`git add tools/write-attestation.ps1
evals/multi-model-verify/test_mirror_reaper.py
docs/superpowers/plans/2026-09-13-mirror-parent.md`), never `git add -A`.

```
f073752 refuse an explicitly empty reap argument instead of reading it as
no reap, and drive both parameters on both hosts
```
3 files changed, 34 insertions(+), 5 deletions(-). Working tree clean
after commit. Commit message matches the brief exactly.

## Concerns / deviations

None. No INPUT GAP encountered. `C:\Users\Brandon\Documents\parallax`,
`C:\pxm\pxmp`, `C:\pxm\kvs-pxmp`, `C:\kv-bl-*`, `C:\kvs-bl-*`, and the
three pre-existing `C:\pxm` directories were never written to — all work
was confined to the worktree at
`C:\Users\Brandon\Documents\_worktrees\parallax-mirror-parent`.
