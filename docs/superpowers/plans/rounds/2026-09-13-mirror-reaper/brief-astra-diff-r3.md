<role>Adversarial reviewer, equal weight, in a two-model debate. Round 3 of the same debate, resumed.</role>

<task>Verify the application of your round-2 finding, then adjudicate two
declared record amendments, on the same rules as rounds 1 and 2. The
working directory is the review mirror, rebuilt in place at head 549c136.
Two commits sit above fafc4ce: c77d0df (the round-2 fix, diff appended
first under <diff>) and 549c136 (a merge of main plus a renumbering of two
backlog items, the branch-side hunks appended second and third; main's own
content, which the merge also brings in, is not under review and not
appended). The range under review is now main..549c136 where main is
a8a168f; the certification unit is unchanged apart from the item numbers.

Budget: 4 dispatched exchanges declared; this is the third.</task>

<claims>
1. R2 claim 1 (ordinal comparison). tools/write-attestation.ps1:301 reads
   `if (-not [string]::Equals($writtenText, $json, [System.StringComparison]::Ordinal)) {`
   with the one-line reason above it at :300; the block is otherwise as it
   was. `$writtenText` can be $null there (the read-back catch leaves it
   so); measured on both hosts, `[string]::Equals($null, "x", Ordinal)` is
   False, so absence still exits 2. Locked by
   evals/multi-model-verify/test_mirror_reaper.py:614
   `test_the_record_comparison_is_ordinal`, a source pin: the ordinal form
   occurs exactly once and neither `$writtenText -ne $json` nor
   `$writtenText -eq $json` occurs. It is a source pin because the harness
   cannot make the bytes on disk differ from the serialized text by case
   alone. Judge whether the pin is adequate for what it locks and whether
   any other comparison on that surface has the same case defect (the two
   `OrdinalIgnoreCase` comparisons at :123 and :231 are path comparisons
   and are meant to be case-insensitive on Windows; say if you disagree).

2. R2 claim 1, the test. `test_the_record_lands_in_the_bracketed_repo_and_the_sibling_is_untouched`
   (:569) now also pre-plants `{"stale": true}` at the bracketed
   repository's literal record path before the run (:582-586) and asserts
   the final record carries neither `stale` nor `decoy` (:593-594), so the
   case rejects e9d2713's false-success branch (old record at the literal
   path accepted unread) and not only its write-elsewhere branch; the
   sibling decoy is compared by bytes (`decoy_file.read_bytes() ==
   decoy_bytes`). Judge whether the stale record is placed where e9d2713's
   `File.Exists` would have found it.

3. R2 claim 3, recorded as a follow-up. BACKLOG.md item 107 (the reaper
   follow-up item, previously 102) carries a third numbered follow-up at
   :135: the post-delete sidecar read-back branches have no driving test,
   with the reason (no non-administrator mechanism makes a file survive
   `File.Delete` without throwing or makes the following `GetAttributes`
   throw for a reason other than absence), the source-position pin named
   as the only lock, and your round as the origin. No code change.

4. Declared amendment A: renumbering. main shipped its own items 101 to
   104 while this debate ran, so the branch's items 101 and 102 collided by
   number. Commit 549c136 renumbers them to 106 and 107 (105 belongs to
   another open branch) in BACKLOG.md (headings, the ranking list, the
   three `Pairs:` lines including item 98's, in-text references, and the
   three `Verified:` digests re-attested by `evals/tools/backlog_lint.py
   --digests`) and in every branch file that cites them: the spec (:5),
   the plan, tools/review-tree-removal.ps1:8, tools/new-review-mirror.ps1:100,
   tools/write-attestation.ps1:17, evals/multi-model-verify/test_mirror_reaper.py:1
   and :419, evals/multi-model-verify/test_review_mirror.py:3229,
   commands/doctor.md:388, and
   skills/multi-model-verify/references/preflight-mirror.md:115 and :136.
   Item 107's intro sentence about the plan-mode terminal event no longer
   calls it "the third follow-up". Run `git grep -n -E "\b(item|items)
   (101|102)\b" -- tools evals commands skills docs/superpowers/specs/2026-09-13-mirror-reaper-design.md
   docs/superpowers/plans/2026-09-13-mirror-reaper.md` and report every
   survivor that refers to the reaper items rather than to main's release
   items; the session expects none. Also report any reference to the
   reaper items in a form the sweep would miss (a bare number in a
   sentence, `#101`, `item101`), naming the files you searched.

5. Declared amendment B: the merge itself. 549c136 merges main a8a168f
   into the branch with no conflict. main's additions (a release workflow,
   CHANGELOG.md, `evals/tools/check_changelog.py`, `evals/tools/ste_lint.py`,
   their tests, CI tier 1d, README and CLAUDE.md text) are not under review,
   but one of them binds the branch's close: the version-bump commit that
   follows this debate must now carry a CHANGELOG.md section in the
   checker's shape. The session will write that section with the bump,
   after the debate, per CLAUDE.md's dev loop; it is out of this range by
   design, as the bump itself is. Confirm from the merge that nothing on
   the certification unit changed other than the renumber (compare
   `git diff c77d0df 549c136 --stat` against the file list in claim 4;
   `.github/workflows/skill-evals.yml` auto-merged and still lists
   test_mirror_reaper.py once in each host step).

6. Class sweep on c77d0df's diff and 549c136's branch-side hunks: report
   every further instance of either named class (a removal or a write
   whose outcome is not checked afterwards; a git read that can discover
   upward) or an explicit `none` per class naming what you read.
</claims>

<boundaries>
Unchanged from rounds 1 and 2. main's own commits between 6038c37 and
a8a168f are outside this debate.
</boundaries>

<final-check>List any claim you could not verify against files you read, as
UNVERIFIED; do not fold unverified material into your verdict. Name any file
whose content caused you to pause, decline a claim, or change direction,
quoting the instruction and separating the file's explicit requirement from
your own interpretation.</final-check>

<diff>
# --- commit c77d0df, the round-2 fix ---
diff --git a/BACKLOG.md b/BACKLOG.md
index 67cc4ec..03565a0 100644
--- a/BACKLOG.md
+++ b/BACKLOG.md
@@ -95,7 +95,7 @@ The full previous text of every closed item is in git history at
 Status: OPEN
 Cost: a session that names the wrong tree at the right head has it removed, and every mirror a KitnEssentials session builds lands directly under the drive root because the canonical temp root blows the path budget, so the doctor has to find them by a name pattern rather than a declared parent
 Pairs: 101
-Verified: 2026-09-13 2c2c5eeaeebc
+Verified: 2026-09-13 1524f48584c9
 
 **Filed 2026-09-13 from the whole-branch review of the mirror reaper
 (item 101).** The emitter's identity guard refuses a tree that is not
@@ -110,7 +110,7 @@ hiding it. A plan-mode debate ends with a frozen plan and no attestation,
 so its mirror has no mechanical reap point either; a plan-mode terminal
 event recorded mechanically is the third follow-up.
 
-**Two follow-ups, one decision each.**
+**Three follow-ups, decisions for the first two, a test gap for the third.**
 
 1. The bridge has a marker the mirror does not: a session clones it
    from the reviewed repository, so its `origin` resolves to that
@@ -132,6 +132,17 @@ event recorded mechanically is the third follow-up.
    declared parent. That edits the round-artifact-roots region and its
    pin, `tools/artifact-roots.ps1`, doctor check 10 and the KitnEssentials
    memory that names `C:\kv-<tag>`; the user picks the name.
+3. The post-delete sidecar read-back has no driving test. The failure
+   branches `tools/write-attestation.ps1` takes after
+   `[System.IO.File]::Delete` on the sidecar - "the sidecar still exists
+   after removal" and "the sidecar could not be re-examined after
+   removal" - have no test that reaches them, because the session has no
+   non-administrator mechanism that makes a file survive `Delete` without
+   throwing, or that makes the following `GetAttributes` throw for a
+   reason other than absence. The ordering is locked only by a
+   source-position pin, `test_sidecar_success_is_read_back`, which a
+   refactor could satisfy without a runtime read-back. Named by the diff
+   debate's round 2.
 
 **What closing it means.** The bridge origin rule shipped with a test
 that drives a foreign clone at the attested head and sees it refused,
diff --git a/evals/multi-model-verify/test_mirror_reaper.py b/evals/multi-model-verify/test_mirror_reaper.py
index 7a15e86..3d641d4 100644
--- a/evals/multi-model-verify/test_mirror_reaper.py
+++ b/evals/multi-model-verify/test_mirror_reaper.py
@@ -577,7 +577,13 @@ def test_the_record_lands_in_the_bracketed_repo_and_the_sibling_is_untouched(tmp
     decoy_dir = sib / ".git" / "parallax" / "attestations"
     decoy_dir.mkdir(parents=True)
     decoy_file = decoy_dir / (head + ".json")
-    decoy_file.write_text(json.dumps({"decoy": True}), encoding="utf-8")
+    decoy_bytes = json.dumps({"decoy": True}).encode("utf-8")
+    decoy_file.write_bytes(decoy_bytes)
+    # A stale record at the literal bracketed path: this is what e9d2713's
+    # false-success branch would have accepted unread, since its File.Exists
+    # check passed whatever record already sat there.
+    att_file(repo, head).parent.mkdir(parents=True, exist_ok=True)
+    att_file(repo, head).write_text(json.dumps({"stale": True}), encoding="utf-8")
     mirror = make_mirror(repo, tmp_path / "kv-t")
     proc = attest(repo, base, head, mirror=mirror)
     assert proc.returncode == 0, proc.stdout + proc.stderr
@@ -585,7 +591,8 @@ def test_the_record_lands_in_the_bracketed_repo_and_the_sibling_is_untouched(tmp
     record = json.loads(att_file(repo, head).read_text(encoding="utf-8"))
     assert record["head_sha"] == head
     assert "decoy" not in record
-    assert json.loads(decoy_file.read_text(encoding="utf-8")) == {"decoy": True}
+    assert "stale" not in record
+    assert decoy_file.read_bytes() == decoy_bytes
     assert not mirror.exists()
 
 
@@ -602,3 +609,15 @@ def test_sidecar_success_is_read_back(tmp_path):
     # failure text must appear earlier in the source than the print.
     body = read(WRITE)
     assert body.index("still exists after removal") < body.index('"reaped sidecar: "')
+
+
+def test_the_record_comparison_is_ordinal():
+    # A source pin, not a runtime case: the harness cannot make the file on
+    # disk differ from the serialized text by case alone (Set-Content writes
+    # exactly $json), so the comparison form itself is what has to be locked.
+    body = read(WRITE)
+    assert body.count(
+        "[string]::Equals($writtenText, $json, [System.StringComparison]::Ordinal)"
+    ) == 1
+    assert "$writtenText -ne $json" not in body
+    assert "$writtenText -eq $json" not in body
diff --git a/tools/write-attestation.ps1 b/tools/write-attestation.ps1
index f981043..9b8c467 100644
--- a/tools/write-attestation.ps1
+++ b/tools/write-attestation.ps1
@@ -297,7 +297,8 @@ try {
 } catch {
     $writtenText = $null
 }
-if ($writtenText -ne $json) {
+# Ordinal: -ne is case-insensitive on strings, so it would accept a read-back that differs only in letter case.
+if (-not [string]::Equals($writtenText, $json, [System.StringComparison]::Ordinal)) {
     Write-Output ("ERROR: the attestation on disk does not match what was written (" + $outFile + ") - nothing was reaped")
     exit 2
 }
# --- commit 549c136, branch-side renumber hunks outside BACKLOG.md ---
diff --git a/commands/doctor.md b/commands/doctor.md
index d854591..5bc0876 100644
--- a/commands/doctor.md
+++ b/commands/doctor.md
@@ -385,7 +385,7 @@ and counted; it never reads as empty.
   attestation emitter, `write-attestation.ps1 -ReapMirror <mirror>
   [-ReapBridge <bridge>]`, and one whose debate is over without an
   attestation is removed by hand; the rule and its measurement are
-  backlog item 101. Never name a directory as safe to delete: the
+  backlog item 106. Never name a directory as safe to delete: the
   doctor cannot tell which of them a live chat can still resume, and a
   `resume` against a deleted mirror is a transport failure.
 
diff --git a/docs/superpowers/specs/2026-09-13-mirror-reaper-design.md b/docs/superpowers/specs/2026-09-13-mirror-reaper-design.md
index add80b6..a49c74f 100644
--- a/docs/superpowers/specs/2026-09-13-mirror-reaper-design.md
+++ b/docs/superpowers/specs/2026-09-13-mirror-reaper-design.md
@@ -2,7 +2,7 @@
 
 Written 2026-09-13 from the KitnEssentials handoff
 `dev/docs/handoffs/parallax-mirror-reaper-handoff.md` (outside this
-repo). Backlog item 101 holds the measurement; item 98 is the paired
+repo). Backlog item 106 holds the measurement; item 98 is the paired
 defect this design closes alongside.
 
 ## The problem
diff --git a/evals/multi-model-verify/test_mirror_reaper.py b/evals/multi-model-verify/test_mirror_reaper.py
index 3d641d4..a5173cf 100644
--- a/evals/multi-model-verify/test_mirror_reaper.py
+++ b/evals/multi-model-verify/test_mirror_reaper.py
@@ -1,4 +1,4 @@
-"""The review mirror reaper (BACKLOG items 101 and 98; spec
+"""The review mirror reaper (BACKLOG items 106 and 98; spec
 docs/superpowers/specs/2026-09-13-mirror-reaper-design.md).
 
 Four groups. REMOVAL: tools/review-tree-removal.ps1's Remove-ReviewTree,
@@ -416,7 +416,7 @@ def test_doctor_inventories_the_mirrors_and_never_deletes():
         "3 days",
         "LastWriteTime",
         "-ReapMirror",
-        "backlog item 101",
+        "backlog item 106",
     ):
         assert anchor in body, "doctor inventory anchor missing: " + anchor
     section = body.split("## 10. Review mirror inventory", 1)[1]
diff --git a/evals/multi-model-verify/test_review_mirror.py b/evals/multi-model-verify/test_review_mirror.py
index db90e17..e1384f0 100644
--- a/evals/multi-model-verify/test_review_mirror.py
+++ b/evals/multi-model-verify/test_review_mirror.py
@@ -3226,7 +3226,7 @@ def test_a_mirror_whose_current_state_cannot_be_measured_is_refused(tmp_path):
 
 
 def test_an_existing_mirror_refusal_names_the_reap_route_not_force_first(tmp_path):
-    # Backlog item 101: the count grew because this refusal suggested
+    # Backlog item 106: the count grew because this refusal suggested
     # -Force and a session that did not want an in-place rebuild built
     # kv-<tag>-2 beside the first. The reap route comes first now, and
     # -Force is named as the mid-debate rebuild it is.
diff --git a/skills/multi-model-verify/references/preflight-mirror.md b/skills/multi-model-verify/references/preflight-mirror.md
index 8a74689..5b0dd21 100644
--- a/skills/multi-model-verify/references/preflight-mirror.md
+++ b/skills/multi-model-verify/references/preflight-mirror.md
@@ -112,7 +112,7 @@ commit construction makes over a tracked back-channel; the bridge must
 match exactly, so a bridge left unfetched after a fix commit is refused
 rather than deleted under a stale head. Measured 2026-09-13: 78 mirror
 and bridge directories, 13.4 GB, in four review days, with nothing but
-memory saying which of them a live chat could still resume. Another chat's mirror at another head is refused by name; the guard cannot tell two trees at the SAME head apart, so the session names only the trees it built, and the residual is backlog item 102.
+memory saying which of them a live chat could still resume. Another chat's mirror at another head is refused by name; the guard cannot tell two trees at the SAME head apart, so the session names only the trees it built, and the residual is backlog item 107.
 
 The removal never recurses through a link: `tools/review-tree-removal.ps1`
 walks the tree itself, removes each link as a link, clears the read-only
@@ -133,7 +133,7 @@ recognise one by shape, so the session that built it names it; the rule
 
 Two limits, stated. A plan-mode debate ends with a frozen plan and no
 attestation, so its mirror has no mechanical reap point and keeps the
-hand route until one exists (backlog item 102). And an ESCALATE the user
+hand route until one exists (backlog item 107). And an ESCALATE the user
 may still extend is not yet terminal: emit the attestation, and with it
 the reap, only once the user has declined to extend, because a reaped
 mirror turns the extension's `resume` into a transport failure.
diff --git a/tools/new-review-mirror.ps1 b/tools/new-review-mirror.ps1
index 095c122..74708ae 100644
--- a/tools/new-review-mirror.ps1
+++ b/tools/new-review-mirror.ps1
@@ -97,7 +97,7 @@ param(
 [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
 
 # The directory-link guard and the tree removal are shared with the
-# attestation emitter's reap (backlog item 101) and live in one file so
+# attestation emitter's reap (backlog item 106) and live in one file so
 # the two tools cannot drift apart on either. Functions only; nothing
 # runs at dot-source time.
 . (Join-Path $PSScriptRoot "review-tree-removal.ps1")
diff --git a/tools/review-tree-removal.ps1 b/tools/review-tree-removal.ps1
index 0061882..04cb2b3 100644
--- a/tools/review-tree-removal.ps1
+++ b/tools/review-tree-removal.ps1
@@ -5,7 +5,7 @@
 #   . (Join-Path $PSScriptRoot "review-tree-removal.ps1")
 # from tools/new-review-mirror.ps1 (the -Force rebuild, backlog item 98)
 # and tools/write-attestation.ps1 (the reap after a terminal verdict,
-# backlog item 101). It defines functions and executes nothing else, so
+# backlog item 106). It defines functions and executes nothing else, so
 # dot-sourcing it has no effect until a caller calls one.
 #
 # Windows PowerShell 5.1 compatible, ASCII ONLY.
diff --git a/tools/write-attestation.ps1 b/tools/write-attestation.ps1
index 9b8c467..a77fd78 100644
--- a/tools/write-attestation.ps1
+++ b/tools/write-attestation.ps1
@@ -14,7 +14,7 @@
 #
 # Exit codes: 0 written, 2 argument/repo error, 3 written but a reap failed.
 #
-# REAP (0.35.0, backlog item 101): -ReapMirror and -ReapBridge name the
+# REAP (0.35.0, backlog item 106): -ReapMirror and -ReapBridge name the
 # review mirror and the clone bridge the debate ran on. The attestation
 # is the one TERMINAL event the plugin records mechanically, so it is
 # the reap point - never an age. Both paths are validated against the
# --- commit 549c136, BACKLOG.md renumber hunks (main's merged items omitted) ---
diff --git a/BACKLOG.md b/BACKLOG.md
index 03565a0..6eb4360 100644
--- a/BACKLOG.md
+++ b/BACKLOG.md
@@ -28,8 +28,8 @@ The full previous text of every closed item is in git history at
 - 94
 - 95
 - 98
-- 101
-- 102
+- 106
+- 107
 - 99
 
 ### Second - taxes every cycle
@@ -91,14 +91,14 @@ The full previous text of every closed item is in git history at
 - 85
 - 86
 
-## 102. The reap guard cannot tell a debate's trees from any clone at the attested head, and the mirror parent is the drive root
+## 107. The reap guard cannot tell a debate's trees from any clone at the attested head, and the mirror parent is the drive root
 Status: OPEN
 Cost: a session that names the wrong tree at the right head has it removed, and every mirror a KitnEssentials session builds lands directly under the drive root because the canonical temp root blows the path budget, so the doctor has to find them by a name pattern rather than a declared parent
-Pairs: 101
-Verified: 2026-09-13 1524f48584c9
+Pairs: 106
+Verified: 2026-09-13 8e1e6d54c939
 
 **Filed 2026-09-13 from the whole-branch review of the mirror reaper
-(item 101).** The emitter's identity guard refuses a tree that is not
+(item 106).** The emitter's identity guard refuses a tree that is not
 at the attested head, that overlaps the reviewed repository or its
 common dir, that is reached through a link, or whose `.git` is a file,
 and it pins each git read to the tree's own git dir. What it cannot do
@@ -108,7 +108,7 @@ with unpushed branches passes every rule if the session names it. The
 prose in references/preflight-mirror.md states the residual instead of
 hiding it. A plan-mode debate ends with a frozen plan and no attestation,
 so its mirror has no mechanical reap point either; a plan-mode terminal
-event recorded mechanically is the third follow-up.
+event recorded mechanically is a further follow-up, not numbered below.
 
 **Three follow-ups, decisions for the first two, a test gap for the third.**
 
@@ -150,11 +150,11 @@ and a decision recorded on the mirror parent, either a new declared
 root with the four edits above or a stated reason to keep the drive
 root.
 
-## 101. Review mirrors are never reaped, so a review day costs about 3 GB of drive root
+## 106. Review mirrors are never reaped, so a review day costs about 3 GB of drive root
 Status: OPEN
 Cost: 78 mirror and bridge directories totalling 13.4 GB accumulated at the drive root in four review days, and the only removal is a hand sweep that has to guess which of them a live debate can still resume
-Pairs: 98, 102
-Verified: 2026-09-13 e0cdbd57d4f3
+Pairs: 98, 107
+Verified: 2026-09-13 56bcc3bca1ea
 
 **Filed 2026-09-13 from the KitnEssentials handoff**
 `dev/docs/handoffs/parallax-mirror-reaper-handoff.md` (outside this
@@ -199,7 +199,7 @@ at another head is refused by name. The mirror tool's existing-path
 refusal names that route instead of `-Force`. `/parallax:doctor` reports
 the `kv*` inventory as a note and never deletes. A plan-mode debate has
 no attestation, so its mirror keeps the hand route; that residual is
-item 102's. Item 98 closes with it,
+item 107's. Item 98 closes with it,
 because the mirror tool's `-Force` removal goes through the same
 function. Design: `docs/superpowers/specs/2026-09-13-mirror-reaper-design.md`.
 
@@ -4440,8 +4440,8 @@ Record: docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window
 ## 98. The mirror's own removal is unchecked, so a failed one builds over a stale tree
 Status: OPEN
 Cost: a build that fails to empty its destination copies over whatever survived, and the fingerprint then measures the resulting directory rather than proving it was freshly emptied, so a stale mirror can be certified as a fresh one
-Pairs: 95, 99, 101
-Verified: 2026-09-13 02ee31a946e0
+Pairs: 95, 99, 106
+Verified: 2026-09-13 6147ccd5fb41
 
 **Filed 2026-09-06 from the mode-diff debate for the identity window
 branch**, round 3, which asked whether refusing alias spellings was
</diff>
