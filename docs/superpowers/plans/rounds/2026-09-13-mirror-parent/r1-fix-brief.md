# Astra round-1 fix brief, branch mirror-parent (head ecd4362), 2026-09-13

Governing checkpoint (already written by the session):
C:\Users\Brandon\Documents\parallax\.git\parallax\application-checkpoints\20260913-1720-ecd43621a6ba.md
Reviewer reply: C:\Temp\parallax-scratch\2026-09-13-mirror-parent\astra-diff-r1-reply.md (claim 2).

Worktree: C:\Users\Brandon\Documents\_worktrees\parallax-mirror-parent (branch
mirror-parent). Never write to C:\Users\Brandon\Documents\parallax. Never
touch C:\kv-bl-*, C:\kvs-bl-*, C:\pxm\pxmp, C:\pxm\kvs-pxmp, or the three
pre-existing directories under C:\pxm (8904109a, k10392, k92104). ONE commit.

## F1 - an explicitly supplied empty reap argument skips validation

`tools/write-attestation.ps1`, REAP VALIDATION block. Today:
```powershell
$mirrorParent = $null
if ($ReapMirror -or $ReapBridge) {
    # Read once, and only when a tree is named: an emitter run without a
    # reap parameter never touches the declaration.
    $mirrorParent = Resolve-MirrorParent $RepoRoot
}
if ($ReapMirror) {
    $reapMirrorFull = Resolve-ReapPath "the reap mirror" $ReapMirror $toplevel $commonFull $headFull $true $mirrorParent
}
if ($ReapBridge) {
    $reapBridgeFull = Resolve-ReapPath "the reap bridge" $ReapBridge $toplevel $commonFull $headFull $false $mirrorParent
}
```
`-ReapMirror ""` (or `-ReapBridge ""`) binds an empty string, every
truthiness test is false, the empty-path refusal inside Resolve-ReapPath
never runs, and the record is written with no reap and no error. Replace
the block with:
```powershell
$mirrorParent = $null
# SUPPLIED, not truthy: a parameter that was given on the command line,
# empty or not, always reaches the validation, so an explicitly empty
# value is refused there ("is empty", exit 2) instead of silently
# meaning no reap. A parameter that was not given still means no reap
# and never reads the declaration. Found by the diff debate's round 1
# (2026-09-13); the truthiness form shipped in 0.36.0.
$reapMirrorGiven = $PSBoundParameters.ContainsKey("ReapMirror")
$reapBridgeGiven = $PSBoundParameters.ContainsKey("ReapBridge")
if ($reapMirrorGiven -or $reapBridgeGiven) {
    $mirrorParent = Resolve-MirrorParent $RepoRoot
}
if ($reapMirrorGiven) {
    $reapMirrorFull = Resolve-ReapPath "the reap mirror" $ReapMirror $toplevel $commonFull $headFull $true $mirrorParent
}
if ($reapBridgeGiven) {
    $reapBridgeFull = Resolve-ReapPath "the reap bridge" $ReapBridge $toplevel $commonFull $headFull $false $mirrorParent
}
```
Leave the two `$reapMirrorFull = $null` / `$reapBridgeFull = $null` lines
above it as they are. Check the header comment and the param-block comment
for the sentence that describes the entry condition; if either says the
parameters are checked "when present" or similar, leave the wording (it
is still true); change nothing else in the file.

Then check the write-then-reap tail: the code that decides whether to
reap after the record is written tests `$reapMirrorFull` / `$reapBridgeFull`
(the resolved values), not the raw parameters. Read it and confirm; if it
tests the raw `$ReapMirror` / `$ReapBridge`, report that as an INPUT GAP
rather than changing it.

## F2 - tests, both parameters, both hosts

`evals/multi-model-verify/test_mirror_reaper.py`, Group 7, after
`test_a_roots_tool_that_exits_nonzero_refuses_every_reap`:
```python
@pytest.mark.parametrize("flag", ["-ReapMirror", "-ReapBridge"])
def test_an_explicitly_empty_reap_argument_is_refused_not_ignored(tmp_path, flag):
    # `-ReapMirror ""` binds an empty string. A truthiness entry test read
    # that as "no reap" and wrote the record with nothing reaped and no
    # error (0.36.0; found by the diff debate's round 1). A parameter that
    # was SUPPLIED always reaches the validation, where the empty value is
    # refused before the record is written.
    repo, base, head = make_repo(tmp_path)
    mirror = make_mirror(repo, tmp_path / "kv-t")
    args = [WRITE, "-RepoRoot", str(repo), "-BaseSha", base, "-HeadSha", head,
            "-Verdict", "PASS", "-VerificationStatus", "FULL",
            "-RouteNote", "effective route confirmed", "-Rounds", "1",
            "-Participants", "session/reviewer", flag, ""]
    proc = run_ps(*args)
    assert proc.returncode == 2, proc.stdout + proc.stderr
    label = "the reap mirror" if flag == "-ReapMirror" else "the reap bridge"
    assert ("ERROR: " + label + " is empty") in proc.stdout, proc.stdout
    assert not att_file(repo, head).exists(), "an empty reap argument must not write the record"
    assert mirror.exists()
```
Run it first and record the failure (RED): today both cases exit 0 and the
record exists. If `run_ps` on either host does not deliver an empty
argument (the parameter reads as not bound), report the exact observed
behaviour per host as an INPUT GAP instead of weakening the assertion.

## F3 - the plan record

`docs/superpowers/plans/2026-09-13-mirror-parent.md`, Task 2 Step 2 (e):
immediately after the code block that begins `$reapMirrorFull = $null` and
contains `if ($ReapMirror -or $ReapBridge) {`, add the paragraph:
```
[Corrected 2026-09-13 by the diff debate's round 1: the three truthiness tests above let an explicitly empty `-ReapMirror ""` or `-ReapBridge ""` skip validation and write the record with no reap; the branch tests `$PSBoundParameters.ContainsKey(...)` instead, so a supplied value always reaches the validation, and a test per parameter drives the refusal on both hosts.]
```
Edit nothing else in the plan.

## Verification, then commit

From the PowerShell tool, in the worktree:
```
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_mirror_reaper.py evals/multi-model-verify/test_attestation.py evals/multi-model-verify/test_artifact_roots.py -q
$env:PARALLAX_PS_HOST = "pwsh.exe"; python -m pytest evals/multi-model-verify/test_mirror_reaper.py evals/multi-model-verify/test_attestation.py evals/multi-model-verify/test_artifact_roots.py -q
```
Both exit 0. Confirm the staged blob of `tools/write-attestation.ps1` is
ASCII and LF (`git show :tools/write-attestation.ps1`). `Get-ChildItem C:\pxm`
lists only 8904109a, k10392, k92104, kvs-pxmp, pxmp (and the sidecar file
pxmp.source-manifest).

Stage by explicit path (never `git add -A`):
```
git add tools/write-attestation.ps1 evals/multi-model-verify/test_mirror_reaper.py docs/superpowers/plans/2026-09-13-mirror-parent.md
git commit -m "refuse an explicitly empty reap argument instead of reading it as no reap, and drive both parameters on both hosts"
```

Report to C:\Temp\parallax-scratch\2026-09-13-mirror-parent\r1-fix-report.md:
per finding what changed (file:line), RED and GREEN evidence with the
commands and condensed output for both hosts, the C:\pxm listing, and any
concern.
