<role>Adversarial reviewer, equal weight, in a two-model debate; round 2 of the same debate, resumed session.</role>

<task>Verify the application of your round-1 finding and re-verdict the
range. Subject: the range a48c35f285cc220426bedccb98f6d8f6e32ab89c..HEAD on
branch mirror-parent, now at head f073752 (one commit above the ecd4362 you
reviewed). The working directory is the same mirror, rebuilt in place at the
new head. Evidence rules, verdict grammar, the non-interactive rule, the
precedence rule, the no-delegation rule, the writing rule, the certification
unit and the boundaries are as in round 1. The diff of the fix commit
ecd4362..f073752 is appended under <diff>.</task>

<rules>
Position changes since round 1, per the protocol:

ACCEPTED: your claim-2 finding (an explicitly supplied empty reap argument
skipped validation and wrote the record with no reap and no error), in
full, including the plan-record correction; applied under application
checkpoint 20260913-1720-ecd43621a6ba.md (outside this tree).

ACCEPTED, record only: your claim-4 qualification. The round-1 brief said
every refusal case keeps its tree in tmp_path; the overlap and
unreadable-parent cases build under the `pxm` fixture by design, because
they must pass the parent rule to reach the rule under test. The debate
record carries the qualified sentence.

Claim 9's ESCALATE is answered below with the gate evidence at two heads.

Fix-verify budget: 4 dispatched exchanges declared; this is the second.
</rules>

<claims>
1. The empty-argument bypass is closed for both parameters.
   tools/write-attestation.ps1:297-312: the entry conditions are now
   `$reapMirrorGiven = $PSBoundParameters.ContainsKey("ReapMirror")` and
   the bridge counterpart; the parent is read when either was SUPPLIED,
   and each supplied value, empty or not, reaches Resolve-ReapPath, whose
   first rule refuses an empty value with `ERROR: <label> is empty`, exit
   2, before `$attDir` exists. A parameter that was not supplied still
   means no reap and never reads the declaration. The write-then-reap tail
   (:393-445) tests the resolved `$reapMirrorFull` / `$reapBridgeFull`, as
   before. Test:
   evals/multi-model-verify/test_mirror_reaper.py:718-736, parametrised
   over `-ReapMirror` and `-ReapBridge` with an empty string argument,
   asserts exit 2, the `is empty` message, record absent, tree present. The
   implementer recorded RED on both hosts before the change (both cases
   exit 0 with the record written) and GREEN after (146 passed per host
   across test_mirror_reaper.py, test_attestation.py and
   test_artifact_roots.py).

2. The plan record carries the correction in place.
   docs/superpowers/plans/2026-09-13-mirror-parent.md:586-587, a dated
   bracket immediately after Task 2 Step 2 (e)'s code block; nothing else
   in the plan changed in this commit.

3. Gate evidence, answering round 1's claim 9. Full six-command gate plus
   `python -m pytest evals -q` under powershell.exe at 3032444: 3083
   passed, 14 skipped, 0 failed (the head ecd4362 you reviewed differs from
   3032444 by one line in docs/ only). The pwsh.exe half at that head was
   abandoned by the session when this fix wave began, since the wave edits
   the tree, and the same full gate is running now at f073752 under both
   hosts; its result will be recorded in the debate record with the head
   it ran at, and the attestation is emitted only after it is green. Runs
   you cannot make yourself go under UNVERIFIED.

4. Class sweep for this commit only: name any other entry condition in
   tools/write-attestation.ps1 that reads a supplied-but-empty parameter
   as absent (the other string parameters are Mandatory or default to a
   value the code tests by content, such as `$CheckpointFile`; say whether
   `-CheckpointFile ""` has the same shape and whether it matters), and say
   none if none.
</claims>

<final-check>List any claim you could not verify against files you read, as
UNVERIFIED; do not fold unverified material into your verdict. Name any file
whose content caused you to pause, decline a claim, or change direction.
End with a verdict per claim and one verdict on the range
a48c35f..f073752 as a whole.</final-check>

<diff>
diff --git a/docs/superpowers/plans/2026-09-13-mirror-parent.md b/docs/superpowers/plans/2026-09-13-mirror-parent.md
index dea7191..e53d031 100644
--- a/docs/superpowers/plans/2026-09-13-mirror-parent.md
+++ b/docs/superpowers/plans/2026-09-13-mirror-parent.md
@@ -583,6 +583,8 @@ if ($ReapBridge) {
 }
 ```
 
+[Corrected 2026-09-13 by the diff debate's round 1: the three truthiness tests above let an explicitly empty `-ReapMirror ""` or `-ReapBridge ""` skip validation and write the record with no reap; the branch tests `$PSBoundParameters.ContainsKey(...)` instead, so a supplied value always reaches the validation, and a test per parameter drives the refusal on both hosts.]
+
 - [ ] **Step 3: Run the module under both hosts**
 
 ```powershell
diff --git a/evals/multi-model-verify/test_mirror_reaper.py b/evals/multi-model-verify/test_mirror_reaper.py
index 7a9a4a7..e4a5587 100644
--- a/evals/multi-model-verify/test_mirror_reaper.py
+++ b/evals/multi-model-verify/test_mirror_reaper.py
@@ -715,6 +715,27 @@ def test_a_roots_tool_that_exits_nonzero_refuses_every_reap(tmp_path, pxm):
     assert mirror.exists()
 
 
+@pytest.mark.parametrize("flag", ["-ReapMirror", "-ReapBridge"])
+def test_an_explicitly_empty_reap_argument_is_refused_not_ignored(tmp_path, flag):
+    # `-ReapMirror ""` binds an empty string. A truthiness entry test read
+    # that as "no reap" and wrote the record with nothing reaped and no
+    # error (0.36.0; found by the diff debate's round 1). A parameter that
+    # was SUPPLIED always reaches the validation, where the empty value is
+    # refused before the record is written.
+    repo, base, head = make_repo(tmp_path)
+    mirror = make_mirror(repo, tmp_path / "kv-t")
+    args = [WRITE, "-RepoRoot", str(repo), "-BaseSha", base, "-HeadSha", head,
+            "-Verdict", "PASS", "-VerificationStatus", "FULL",
+            "-RouteNote", "effective route confirmed", "-Rounds", "1",
+            "-Participants", "session/reviewer", flag, ""]
+    proc = run_ps(*args)
+    assert proc.returncode == 2, proc.stdout + proc.stderr
+    label = "the reap mirror" if flag == "-ReapMirror" else "the reap bridge"
+    assert ("ERROR: " + label + " is empty") in proc.stdout, proc.stdout
+    assert not att_file(repo, head).exists(), "an empty reap argument must not write the record"
+    assert mirror.exists()
+
+
 # ---------------------------------------------------------------------
 # Group 6: diff debate round 1 (Astra, R1-3a and R1-8)
 # ---------------------------------------------------------------------
diff --git a/tools/write-attestation.ps1 b/tools/write-attestation.ps1
index 3d90f98..f8cc95a 100644
--- a/tools/write-attestation.ps1
+++ b/tools/write-attestation.ps1
@@ -294,15 +294,21 @@ $commonFull = [System.IO.Path]::GetFullPath($commonDir).TrimEnd("\")
 $reapMirrorFull = $null
 $reapBridgeFull = $null
 $mirrorParent = $null
-if ($ReapMirror -or $ReapBridge) {
-    # Read once, and only when a tree is named: an emitter run without a
-    # reap parameter never touches the declaration.
+# SUPPLIED, not truthy: a parameter that was given on the command line,
+# empty or not, always reaches the validation, so an explicitly empty
+# value is refused there ("is empty", exit 2) instead of silently
+# meaning no reap. A parameter that was not given still means no reap
+# and never reads the declaration. Found by the diff debate's round 1
+# (2026-09-13); the truthiness form shipped in 0.36.0.
+$reapMirrorGiven = $PSBoundParameters.ContainsKey("ReapMirror")
+$reapBridgeGiven = $PSBoundParameters.ContainsKey("ReapBridge")
+if ($reapMirrorGiven -or $reapBridgeGiven) {
     $mirrorParent = Resolve-MirrorParent $RepoRoot
 }
-if ($ReapMirror) {
+if ($reapMirrorGiven) {
     $reapMirrorFull = Resolve-ReapPath "the reap mirror" $ReapMirror $toplevel $commonFull $headFull $true $mirrorParent
 }
-if ($ReapBridge) {
+if ($reapBridgeGiven) {
     $reapBridgeFull = Resolve-ReapPath "the reap bridge" $ReapBridge $toplevel $commonFull $headFull $false $mirrorParent
 }
 if ($reapMirrorFull -and $reapBridgeFull) {

</diff>
