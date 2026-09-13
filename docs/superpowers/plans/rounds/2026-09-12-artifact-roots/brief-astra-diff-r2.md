<role>Adversarial reviewer, equal weight, in a two-model debate (round 2 of the mode-diff debate you opened).</role>

<task>Verify the application of your round-1 findings on the artifact-roots
range, now cd0e863..HEAD (head cf7109b, one commit past aabab81 that
carries every fix). The frozen plan and spec are as before; the spec was
amended in place for the exit-map residual (claim 2 below). Read the files
yourself in this working directory; `git diff aabab81..HEAD` is the fix
diff and is appended under <diff>.</task>

<rules>
Same rules as round 1: cite a repo-relative file:line for every claim you
make or contest, anchored with the full path the first time; uncited claims
are struck; PASS a claim that stands; FIX with the specific fix and its
evidence, or ESCALATE, when it does not; one verdict on the range. The round
is non-interactive; reading any file here and running
`tools/artifact-roots.ps1` read-only on either host against this working
directory or a disposable repository under your own temp directory is
authorized, as in round 1. Report UNVERIFIED items in the final check, and
name any file whose content caused a pause. State findings as plain prose,
no stock phrases, no closing summary, no contrastive framing this brief did
not raise.

Certification unit and the pre-existing-defect rule are unchanged from
round 1. Budget: this is exchange 2 of 4.
</rules>

<claims>
1. Round-1 claim 4, applied. Every path conversion in
   tools/artifact-roots.ps1 now goes through `Resolve-Absolute`: the
   toplevel, the common dir, the temp root and each row's parent. The
   temp root is screened with the forbidden-character set on its non-drive
   part before any path API, so `TEMP=C:\bad|temp` exits 2 with an `ERROR:`
   line on both hosts. The declaration read is inside a try whose failure
   exits 2. `-RepoRoot` is optional-with-check (`-RepoRoot is required`,
   exit 2); binding is named-only (`[CmdletBinding(PositionalBinding =
   $false)]`) and remaining arguments are captured, so an unknown parameter
   or a bare token exits 2 with `ERROR: unknown parameter:`. The named-only
   change also closed a defect the new regression found: a bare token used
   to bind POSITIONALLY to `-DocsRoot` and answer with a docs root nobody
   asked for. The one residual, a named parameter whose VALUE is missing,
   exits 1 from `-File` binding on both hosts and is stated in the header
   and in the spec's exit map. Regressions:
   evals/multi-model-verify/test_artifact_roots.py
   `test_a_forbidden_character_in_temp_is_a_parameter_fault` and
   `test_faults_the_binder_used_to_own_are_script_faults` (three cases).

2. The spec's exit-map paragraph
   (docs/superpowers/specs/2026-09-12-artifact-roots-design.md, "Exit
   map") now enumerates the script-seen parameter faults, the TEMP screen
   and its reason, and the one residual binding fault, dated as a round-1
   amendment. The tool header says the same thing. The plan text it
   departs from is the plan's defect, as with the two earlier amendments.

3. Round-1 claim 5, applied. The sweep carries a seventh shape,
   `<git-common-dir>[/\\]parallax[/\\]`, with two positive controls and one
   negative control in `test_sweep_can_fail`; the comment above
   `FORBIDDEN_SHAPES` states the forms the shapes do not catch (slashless
   spellings, a ledger root with no separator, runtime-assembled roots,
   surfaces the glob list does not name) and names the writer test as what
   binds the runtime-assembled rows. The three spellings you found now cite
   the declaration instead: skills/multi-model-verify/references/application-checkpoint.md
   ("The artifact" section names the checkpoint root row and only the file
   pattern), tools/verify-attestation.ps1 (header comment),
   tools/write-attestation.ps1 (the `-CheckpointFile` comment). The sweep
   finds zero offenders. Class sweep again: name any remaining hand-spelled
   root on the surface that the seven shapes miss, or state that you found
   none.

4. Round-1 claim 6, applied. The writer test is two cases sharing one
   driver (`run_the_real_writers`): the fresh case asserts the appeared set
   is exactly `.git/parallax`, `.git/parallax/attestations` and the
   attestation file, as the plan's Task 4 and the spec require; the
   checkpoint-bound case pre-creates the checkpoint and asserts the
   appeared set is the attestation directory and file, with `-Expect
   checkpoint` and `-Expect attestation` answers exit 0 and a second
   snapshot after the resolver ran. Both cases pass on both hosts (session
   runs: 140 passed on Windows PowerShell 5.1 across the three modules, 51
   passed on PowerShell 7 for the module).

5. Round-1 claim 7, record only: the README's R1 section records 25,985
   characters and the SKILL citations :153-154, :324, :389; the range makes
   no change to SKILL.md.

6. Nothing else moved. The fix commit touches tools/artifact-roots.ps1,
   tools/verify-attestation.ps1, tools/write-attestation.ps1,
   evals/multi-model-verify/test_artifact_roots.py,
   skills/multi-model-verify/references/application-checkpoint.md, the
   spec, the rounds directory (README plus the retained R1 artifacts), and
   evals/multi-model-verify/test_multi_model_verify.py, where the
   application-checkpoint location pin (`TestApplicationCheckpoint`,
   `test_artifact_location_and_headless_exemption`) required the spelled
   path and now requires the declaration citation, found by the full gate
   (2983 passed, 14 skipped after the move). The round-artifact-roots
   region is byte-identical. The attestation and verification tools
   changed only in comments; test_attestation.py is unchanged and green.
</claims>

<final-check>
List UNVERIFIED items, name any file whose content caused a pause, and give
one verdict on the range cd0e863..HEAD: PASS, FIX or ESCALATE.
</final-check>

<diff>
diff --git a/docs/superpowers/specs/2026-09-12-artifact-roots-design.md b/docs/superpowers/specs/2026-09-12-artifact-roots-design.md
index 137b6e9..6444acc 100644
--- a/docs/superpowers/specs/2026-09-12-artifact-roots-design.md
+++ b/docs/superpowers/specs/2026-09-12-artifact-roots-design.md
@@ -226,7 +226,14 @@ Exit map: 0 resolved (or asserted inside), 1 asserted outside or inside
 a retained root other than the one `-Expect` names, 2 for a parameter
 fault, an unreadable declaration, or a `-RepoRoot` that is not a git
 working tree. The map mirrors `tools/dispatch-round.ps1`'s so a
-caller reads one convention.
+caller reads one convention. Parameter faults the script itself sees
+(amended 2026-09-13 from the diff debate's round 1): a missing
+`-RepoRoot`, an unknown or bare token (binding is named-only), a
+forbidden character in `-DocsRoot`, `-Assert` or the `TEMP` variable,
+which is screened with the same set before any path API because it is
+the one input that is neither a parameter nor git's answer. ONE
+residual stays with PowerShell's `-File` binding on both hosts and exits
+1 without an `ERROR:` line: a named parameter whose value is missing.
 
 ## Skill and agent edits
 
diff --git a/evals/multi-model-verify/test_artifact_roots.py b/evals/multi-model-verify/test_artifact_roots.py
index 025900e..b774e34 100644
--- a/evals/multi-model-verify/test_artifact_roots.py
+++ b/evals/multi-model-verify/test_artifact_roots.py
@@ -88,11 +88,11 @@ def test_fixed_rows_state_their_reason_outside_the_region():
 # ---------------------------------------------------------------------
 # Group 3a: the resolver
 # ---------------------------------------------------------------------
-def run_resolver(*args, tool=None):
+def run_resolver(*args, tool=None, env=None):
     return subprocess.run(
         [POWERSHELL, "-NoProfile", "-NonInteractive", "-File",
          str(tool or TOOL), *args],
-        capture_output=True, text=True, timeout=60)
+        capture_output=True, text=True, timeout=60, env=env)
 
 
 def git(repo, *args):
@@ -263,6 +263,40 @@ def test_unresolvable_paths_are_parameter_faults_not_throws(tmp_path, args):
     assert proc.stdout.startswith("ERROR:"), proc.stdout
 
 
+@needs_host
+def test_a_forbidden_character_in_temp_is_a_parameter_fault(tmp_path):
+    # TEMP is the one input that is neither a parameter nor git's answer.
+    # Unscreened, `|` in it threw on 5.1 (exit 1) and printed on 7 (exit
+    # 0): measured 2026-09-13 by the diff-debate R1 reviewer. Same exit
+    # and prefix on both hosts now.
+    import os
+    repo = make_repo(tmp_path)
+    env = dict(os.environ)
+    env["TEMP"] = r"C:\bad|temp"
+    proc = run_resolver("-RepoRoot", str(repo), env=env)
+    assert proc.returncode == 2, proc.stdout + proc.stderr
+    assert proc.stdout.startswith("ERROR: TEMP contains a character"), proc.stdout
+
+
+@needs_host
+@pytest.mark.parametrize("args", [
+    (),
+    ("-RepoRoot", "{repo}", "-Bogus", "x"),
+    ("-RepoRoot", "{repo}", "stray"),
+])
+def test_faults_the_binder_used_to_own_are_script_faults(tmp_path, args):
+    # A missing -RepoRoot and an unbound token used to exit 1 from
+    # PowerShell's own -File binding, with host-specific text and no
+    # ERROR: line. The parameter is optional-with-check and remaining
+    # arguments are captured, so both are script-seen faults. The one
+    # residual is a named parameter whose VALUE is missing, which the
+    # header states.
+    repo = make_repo(tmp_path)
+    proc = run_resolver(*[a.replace("{repo}", str(repo)) for a in args])
+    assert proc.returncode == 2, proc.stdout + proc.stderr
+    assert proc.stdout.startswith("ERROR:"), proc.stdout
+
+
 @needs_host
 def test_reporoot_must_be_a_git_working_tree(tmp_path):
     plain = tmp_path / "plain"
@@ -436,6 +470,12 @@ def declaration_line_numbers():
 # lookbehind in the first shape only keeps a citation of a nested
 # `plans/rounds/` path from being misread as a root beside plans/; the
 # string `plans/superpowers/rounds/` does not occur in the tree.
+# STATED LIMITS, the forms these shapes do not catch: a slashless
+# spelling (`superpowers rounds`, `dev docs superpowers`), a ledger root
+# with no separator after `sdd`, a root assembled from parts at runtime
+# (`Join-Path $common "parallax"`), and any spelling on a surface the
+# glob list above does not name. The writer test in Group 3b is what
+# binds the runtime-assembled rows.
 FORBIDDEN_SHAPES = [
     ("a rounds root beside plans/ instead of under it",
      re.compile(r"(?<!plans[/\\])superpowers[/\\]rounds[/\\]")),
@@ -449,6 +489,8 @@ FORBIDDEN_SHAPES = [
      re.compile(r"\.git[/\\]parallax[/\\]")),
     ("the default docs root named by hand outside a dated citation",
      re.compile(r"docs[/\\]superpowers(?![/\\](plans[/\\](rounds[/\\])?|specs[/\\])\d{4}-\d{2}-\d{2}-)")),
+    ("a common-dir row spelled by placeholder instead of cited",
+     re.compile(r"<git-common-dir>[/\\]parallax[/\\]")),
 ]
 
 
@@ -515,6 +557,18 @@ def test_sweep_can_fail(tmp_path):
     hits = [label for label, rx in FORBIDDEN_SHAPES
             if rx.search(r"Join-Path $r '.superpowers\sdd\plan'")]
     assert hits == ["a ledger root that is neither the declaration nor a dated citation"]
+    # The seventh shape: a row spelled with its placeholder root, which
+    # three files did until 2026-09-13 (application-checkpoint.md and the
+    # two attestation tools), found by the diff-debate R1 reviewer.
+    hits = [label for label, rx in FORBIDDEN_SHAPES
+            if rx.search("<git-common-dir>/parallax/application-checkpoints/<stamp>.md")]
+    assert hits == ["a common-dir row spelled by placeholder instead of cited"]
+    hits = [label for label, rx in FORBIDDEN_SHAPES
+            if rx.search(r"# <git-common-dir>\parallax\attestations\<head-sha>.json")]
+    assert hits == ["a common-dir row spelled by placeholder instead of cited"]
+    hits = [label for label, rx in FORBIDDEN_SHAPES
+            if rx.search("`<git-common-dir>` is what `git rev-parse --git-common-dir` prints")]
+    assert hits == []
 
 
 def test_declaration_exemption_covers_only_the_marked_region():
@@ -560,32 +614,29 @@ def write_attestation(repo, base, head, checkpoint=None):
     return subprocess.run(args, capture_output=True, text=True, timeout=60)
 
 
-@needs_host
-def test_the_real_writers_create_nothing_in_repo_but_the_attestation(tmp_path):
-    # The three tools that write during a round, run for real against a
-    # disposable two-commit repository. The only path that may appear
-    # inside the repository is the attestation, and it must satisfy the
-    # resolver's own membership answer. This is also what binds the two
-    # common-dir rows to the declaration: the emitter computes the
-    # attestation and checkpoint locations for itself from
-    # `git rev-parse --git-common-dir`, and the resolver's answer for
-    # each is checked here with -Expect.
+def run_the_real_writers(tmp_path, checkpoint):
+    """The three tools that write during a round, run for real against a
+    disposable two-commit repository: the attestation emitter (with
+    -CheckpointFile when `checkpoint` is set), the review mirror tool and
+    dispatch-round.ps1 -Prepare. Returns (repo, head, before, appeared).
+    The snapshot is taken after the checkpoint file exists, so the
+    appeared set is what the three writers created."""
     from test_dispatch_round import build_real_mirror, prepare_default
     repo = make_repo(tmp_path, name="src", commits=2)
     base = git(repo, "rev-parse", "HEAD~1").strip()
     head = git(repo, "rev-parse", "HEAD").strip()
-    # Pre-existing BEFORE the snapshot, on purpose: the checkpoint file at
-    # its canonical location (the same shape as
-    # test_attestation.py's TestCheckpointBinding.make_checkpoint; the
-    # emitter refuses any other location and hashes it there), which
-    # creates `.git/parallax` and `.git/parallax/application-checkpoints`
-    # on the way down. The emitter therefore creates only the attestation
-    # dir and file, and that is the whole appeared set below.
-    cp_dir = repo / ".git" / "parallax" / "application-checkpoints"
-    cp_dir.mkdir(parents=True)
-    cp = cp_dir / "checkpoint.md"
-    cp.write_text("# Application checkpoint\nfile1.txt | x present | F1\n",
-                  encoding="utf-8")
+    cp = None
+    if checkpoint:
+        # The checkpoint file at its canonical location (the same shape
+        # as test_attestation.py's TestCheckpointBinding.make_checkpoint;
+        # the emitter refuses any other location and hashes it there),
+        # which creates `.git/parallax` and the checkpoint dir on the way
+        # down, BEFORE the snapshot.
+        cp_dir = repo / ".git" / "parallax" / "application-checkpoints"
+        cp_dir.mkdir(parents=True)
+        cp = cp_dir / "checkpoint.md"
+        cp.write_text("# Application checkpoint\nfile1.txt | x present | F1\n",
+                      encoding="utf-8")
     before = tree_paths(repo)
 
     att = write_attestation(repo, base, head, checkpoint=cp)
@@ -594,30 +645,21 @@ def test_the_real_writers_create_nothing_in_repo_but_the_attestation(tmp_path):
     assert norm(mirror.source) == norm(repo)
     prep = prepare_default(tmp_path, mirror=mirror)
     assert prep.returncode == 0, prep.stdout + prep.stderr
+    return repo, head, cp, before, new_paths(repo, before)
 
-    appeared = new_paths(repo, before)
-    # The attestation file and the directory the emitter creates for it
-    # (write-attestation.ps1: New-Item -Force on the attestation dir),
-    # and nothing else; `.git/parallax` pre-exists, see above.
-    assert appeared == {
-        ".git/parallax/attestations",
-        f".git/parallax/attestations/{head}.json",
-    }, sorted(appeared)
+
+def assert_attestation_paths_are_inside(repo, head, before, appeared):
     # The attestation root and the file under it are inside the retained
     # set. `.git/parallax` is the parent SHARED by the attestation and
     # checkpoint rows; it is not itself a declared root, so -Assert
-    # refuses it, and the exact-set assertion above is what bounds it.
+    # refuses it, and the exact-set assertion in the caller is what
+    # bounds it.
     for rel in (".git/parallax/attestations",
                 f".git/parallax/attestations/{head}.json"):
         proc = run_resolver("-RepoRoot", str(repo), "-Assert", str(repo / rel),
                             "-Expect", "attestation")
         assert proc.returncode == 0, proc.stdout + proc.stderr
         assert "assert: inside attestation root" in proc.stdout
-    # The checkpoint the emitter hashed sits inside the checkpoint row.
-    proc = run_resolver("-RepoRoot", str(repo), "-Assert", str(cp),
-                        "-Expect", "checkpoint")
-    assert proc.returncode == 0, proc.stdout + proc.stderr
-    assert "assert: inside checkpoint root" in proc.stdout
     proc = run_resolver("-RepoRoot", str(repo), "-Assert", str(repo / ".git" / "parallax"))
     assert proc.returncode == 1, proc.stdout + proc.stderr
     # Second snapshot AFTER the resolver calls: the resolver is a reader,
@@ -625,6 +667,46 @@ def test_the_real_writers_create_nothing_in_repo_but_the_attestation(tmp_path):
     assert new_paths(repo, before) == appeared, sorted(new_paths(repo, before))
 
 
+@needs_host
+def test_the_real_writers_create_nothing_in_repo_but_the_attestation(tmp_path):
+    # The fresh case the plan's Task 4 specifies: nothing under
+    # `.git/parallax` exists before the round, so the appeared set is the
+    # attestation file and the TWO directories the emitter creates for it
+    # (write-attestation.ps1: New-Item -Force on the attestation dir), and
+    # nothing else. The only path that may appear inside the repository
+    # is the attestation, and it must satisfy the resolver's own
+    # membership answer.
+    repo, head, _, before, appeared = run_the_real_writers(tmp_path, checkpoint=False)
+    assert appeared == {
+        ".git/parallax",
+        ".git/parallax/attestations",
+        f".git/parallax/attestations/{head}.json",
+    }, sorted(appeared)
+    assert_attestation_paths_are_inside(repo, head, before, appeared)
+
+
+@needs_host
+def test_the_checkpoint_bound_emitter_stays_inside_the_declared_rows(tmp_path):
+    # The checkpoint-bound case, which is what binds the two common-dir
+    # rows to the declaration: the emitter computes the attestation and
+    # checkpoint locations for itself from `git rev-parse
+    # --git-common-dir`, and the resolver's answer for each is checked
+    # here with -Expect. `.git/parallax` pre-exists (the checkpoint was
+    # written before the snapshot), so the appeared set is the
+    # attestation dir and file only.
+    repo, head, cp, before, appeared = run_the_real_writers(tmp_path, checkpoint=True)
+    assert appeared == {
+        ".git/parallax/attestations",
+        f".git/parallax/attestations/{head}.json",
+    }, sorted(appeared)
+    # The checkpoint the emitter hashed sits inside the checkpoint row.
+    proc = run_resolver("-RepoRoot", str(repo), "-Assert", str(cp),
+                        "-Expect", "checkpoint")
+    assert proc.returncode == 0, proc.stdout + proc.stderr
+    assert "assert: inside checkpoint root" in proc.stdout
+    assert_attestation_paths_are_inside(repo, head, before, appeared)
+
+
 @needs_host
 def test_a_writer_that_strays_is_reported(tmp_path):
     # Negative control for the diff-and-assert logic above: a stub writer
diff --git a/evals/multi-model-verify/test_multi_model_verify.py b/evals/multi-model-verify/test_multi_model_verify.py
index 6198166..a451dd6 100644
--- a/evals/multi-model-verify/test_multi_model_verify.py
+++ b/evals/multi-model-verify/test_multi_model_verify.py
@@ -2424,8 +2424,12 @@ class TestApplicationCheckpoint:
 
     def test_artifact_location_and_headless_exemption(self):
         text = self.checkpoint()
-        assert "parallax/application-checkpoints/" in text
-        assert "git-common-dir" in text, (
+        # 0.34.0: the location is the declaration's checkpoint row, cited
+        # rather than spelled (item 100; the sweep in test_artifact_roots.py
+        # refuses the spelled form on this surface).
+        assert "Canonical checkpoint root" in text
+        assert "round-artifact-roots" in text
+        assert "recording it cannot move HEAD" in text, (
             "same untracked-record rationale as attestations"
         )
         assert re.search(r"N/A.{0,120}(headless|auto-triage)",
diff --git a/skills/multi-model-verify/references/application-checkpoint.md b/skills/multi-model-verify/references/application-checkpoint.md
index 960b60e..dfc648c 100644
--- a/skills/multi-model-verify/references/application-checkpoint.md
+++ b/skills/multi-model-verify/references/application-checkpoint.md
@@ -72,13 +72,12 @@ terminal PASS — and its attestation — come only after that.
 
 ## The artifact
 
-Write the checkpoint to the reviewed repo's git dir — untracked, same
-rationale as attestations (recording it cannot move HEAD, it never ships
-in a commit, worktrees share it):
-
-```
-<git-common-dir>/parallax/application-checkpoints/<stamp>-<reviewed-head12>.md
-```
+Write the checkpoint as `<stamp>-<reviewed-head12>.md` directly under
+the checkpoint root that `tools/artifact-roots.ps1` printed in preflight
+(references/model-prompting-notes.md's round-artifact-roots declaration,
+`Canonical checkpoint root` row) — untracked, same rationale as
+attestations (recording it cannot move HEAD, it never ships in a commit,
+worktrees share it).
 
 At attestation time, pass it to the emitter via `-CheckpointFile`: the
 attestation then records the checkpoint's hash and the emitter-computed
diff --git a/tools/artifact-roots.ps1 b/tools/artifact-roots.ps1
index 7cf46ec..b103d9c 100644
--- a/tools/artifact-roots.ps1
+++ b/tools/artifact-roots.ps1
@@ -16,16 +16,27 @@
 # Exit codes: 0 resolved (or -Assert inside the expected root, or inside
 # any retained root when -Expect is absent), 1 -Assert outside every
 # retained root or inside a retained root other than the one -Expect
-# names, 2 parameter fault, unreadable declaration, or -RepoRoot not a
-# git working tree. A MISSING -RepoRoot exits 1 from PowerShell's own
-# -File parameter binding before this script runs, so 2 covers the
-# faults the script itself sees. The map mirrors dispatch-round.ps1.
+# names, 2 parameter fault (a missing -RepoRoot, an unknown parameter, a
+# forbidden character in -DocsRoot, -Assert or the TEMP variable),
+# unreadable declaration, or -RepoRoot not a git working tree. ONE
+# residual binding fault stays outside the script's reach on both hosts:
+# a named parameter whose VALUE is missing (`-DocsRoot` as the last
+# token) exits 1 from PowerShell's -File binding before any line here
+# runs. Everything else that can go wrong is seen by this script and
+# exits 2 with an ERROR: line. The map mirrors dispatch-round.ps1.
+# Named-only binding: without it a bare token binds POSITIONALLY to
+# -DocsRoot and answers with a docs root nobody asked for.
+[CmdletBinding(PositionalBinding = $false)]
 param(
-    [Parameter(Mandatory = $true)][string]$RepoRoot,
+    [string]$RepoRoot = "",
     [string]$DocsRoot = "",
     [string]$Assert = "",
     [string]$Expect = "",
-    [switch]$Json
+    [switch]$Json,
+    # Captures anything the parameters above did not bind, so a
+    # misspelled parameter is a script-seen fault (exit 2) and not a
+    # binding failure (exit 1) whose text differs by host.
+    [Parameter(ValueFromRemainingArguments = $true)][string[]]$Unbound
 )
 
 $ErrorActionPreference = "Stop"
@@ -83,12 +94,25 @@ function Resolve-Absolute($p) {
     return $full
 }
 
+# ---- parameter faults the binder cannot name ---------------------------
+if ($Unbound -and $Unbound.Count -gt 0) {
+    Fail ("unknown parameter: " + ($Unbound -join " "))
+}
+if (-not $RepoRoot) { Fail "-RepoRoot is required" }
+
 # ---- the declaration ---------------------------------------------------
 $NotesPath = Join-Path $PSScriptRoot "..\skills\multi-model-verify\references\model-prompting-notes.md"
 if (-not (Test-Path -LiteralPath $NotesPath -PathType Leaf)) {
     Fail ("declaration file not found: " + $NotesPath)
 }
-$notes = [System.IO.File]::ReadAllText($NotesPath, (New-Object System.Text.UTF8Encoding($false)))
+$notes = $null
+$readWhy = ""
+try {
+    $notes = [System.IO.File]::ReadAllText($NotesPath, (New-Object System.Text.UTF8Encoding($false)))
+} catch {
+    $readWhy = $_.Exception.Message
+}
+if ($null -eq $notes) { Fail ("declaration file unreadable: " + $NotesPath + ": " + $readWhy) }
 $regionMatch = [regex]::Match($notes,
     '<!-- contract:start id=round-artifact-roots -->(.*?)<!-- contract:end -->',
     [System.Text.RegularExpressions.RegexOptions]::Singleline)
@@ -146,7 +170,7 @@ if (($topExit -ne 0) -or -not $toplevel) {
 if (($commonExit -ne 0) -or -not $commonDir) {
     Fail ("could not resolve the git common dir for " + $RepoRoot)
 }
-$top = Normalize-Slashes ([System.IO.Path]::GetFullPath($toplevel))
+$top = Resolve-Absolute $toplevel
 # A relative common dir is relative to the directory git RAN IN, which
 # is -RepoRoot and not the toplevel: from a subdirectory git prints
 # `../.git`, and joining that to the toplevel lands outside the checkout.
@@ -154,7 +178,7 @@ $top = Normalize-Slashes ([System.IO.Path]::GetFullPath($toplevel))
 if (-not [System.IO.Path]::IsPathRooted($commonDir)) {
     $commonDir = Join-Path $RepoRoot $commonDir
 }
-$common = Normalize-Slashes ([System.IO.Path]::GetFullPath($commonDir))
+$common = Resolve-Absolute $commonDir
 
 # ---- the docs root -----------------------------------------------------
 if ($PSBoundParameters.ContainsKey("DocsRoot")) {
@@ -194,7 +218,14 @@ if ($PSBoundParameters.ContainsKey("DocsRoot")) {
 
 $tempRoot = $env:TEMP
 if (-not $tempRoot) { $tempRoot = [System.IO.Path]::GetTempPath() }
-$tempRoot = Normalize-Slashes ([System.IO.Path]::GetFullPath($tempRoot))
+# The one input that is neither a parameter nor git's answer: screen it
+# with the same set as -DocsRoot and -Assert before any path API, or a
+# `|` in TEMP throws on 5.1 and prints on 7 (measured 2026-09-13 by the
+# diff-debate R1 reviewer). Same exit on both hosts.
+if (($tempRoot -replace '^[A-Za-z]:', '') -match '[<>:"|?*\x00-\x1f]') {
+    Fail ("TEMP contains a character Windows paths forbid: " + $tempRoot)
+}
+$tempRoot = Resolve-Absolute $tempRoot
 
 function Resolve-Row($value) {
     $v = $value.Replace("<docs-root>", $docsRel)
@@ -211,7 +242,7 @@ function Resolve-Row($value) {
     $v = $v.TrimEnd("/")
     if (-not $v) { Fail ("declaration row has no resolvable parent: " + $value) }
     if (-not [System.IO.Path]::IsPathRooted($v)) { $v = $top + "/" + $v }
-    $parent = Normalize-Slashes ([System.IO.Path]::GetFullPath($v))
+    $parent = Resolve-Absolute $v
     if ($tail) { return $parent + "/" + $tail }
     return $parent
 }
diff --git a/tools/verify-attestation.ps1 b/tools/verify-attestation.ps1
index 1b7c827..3616d7e 100644
--- a/tools/verify-attestation.ps1
+++ b/tools/verify-attestation.ps1
@@ -1,6 +1,7 @@
 # verify-attestation.ps1 - check a pushed main sha against the recorded
-# multi-model-verify attestations (written by write-attestation.ps1 into
-# <git-common-dir>\parallax\attestations\<head-sha>.json).
+# multi-model-verify attestations (written by write-attestation.ps1 as
+# <head-sha>.json under the attestation row of
+# references/model-prompting-notes.md's round-artifact-roots declaration).
 #
 # Match rules (Sol consult 2026-07-19, session-adjudicated):
 #   direct / fast-forward: the pushed sha itself is attested (head_sha
diff --git a/tools/write-attestation.ps1 b/tools/write-attestation.ps1
index 9fc73d6..72facac 100644
--- a/tools/write-attestation.ps1
+++ b/tools/write-attestation.ps1
@@ -28,9 +28,10 @@ param(
     [string]$Mode = "diff",
     # Optional (0.7.0): the application checkpoint that authorized the fix
     # edits inside the attested range (references/application-checkpoint.md).
-    # Must live in the canonical <git-common-dir>/parallax/
-    # application-checkpoints/ directory - the verifier re-locates and
-    # re-hashes it there, so an artifact anywhere else is unverifiable.
+    # Must live under the checkpoint row of
+    # references/model-prompting-notes.md's round-artifact-roots
+    # declaration - the verifier re-locates and re-hashes it there, so
+    # an artifact anywhere else is unverifiable.
     # When present, the record binds the checkpoint hash AND the
     # emitter-computed changed-path set - never caller-supplied - so an
     # attestation minted for a different change set fails verification.
</diff>
