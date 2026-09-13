<role>Adversarial reviewer, equal weight, in a two-model debate (round 4 of the mode-diff debate you opened; round 2 was voided on this side).</role>

<task>Verify the application of your round-3 findings on the artifact-roots
range, now cd0e863..HEAD (head 8556599, one commit past 166501e). The
frozen plan and spec are as before; the spec's exit-map paragraph was
amended again (claim 2). `git diff 166501e..HEAD` is the fix diff and is
appended under <diff> (retained round records excluded).</task>

<rules>
Same rules as rounds 1 and 3: cite a repo-relative file:line for every
claim you make or contest, anchored with the full path the first time;
uncited claims are struck; PASS a claim that stands; FIX with the specific
fix and its evidence, or ESCALATE, when it does not; one verdict on the
range. The round is non-interactive; reading any file here and running
`tools/artifact-roots.ps1` read-only on either host against this working
directory or a disposable repository under your own temp directory is
authorized. Report UNVERIFIED items in the final check, and name any file
whose content caused a pause. State findings as plain prose, no stock
phrases, no closing summary, no contrastive framing this brief did not
raise.

Certification unit and the pre-existing-defect rule are unchanged. Budget:
this is exchange 4 of 4, the last declared exchange. A finding here that
is new and substantive pauses the debate for the user's authorization; a
round with no new substantive finding and no contested point is the
adjudicated dry round that ends it.
</rules>

<claims>
1. Round-3 claim 1, applied. tools/artifact-roots.ps1 has NO `param`
   block: a hand parser over `$args` (section "the command line",
   directly after `Fail`) accepts exactly `-RepoRoot`, `-DocsRoot`,
   `-Assert`, `-Expect` (each with a value, inline `-Name:value` or the
   next token) and `-Json` (with an optional true/false token, because
   `-File` splits `-Json:$true` into two tokens and PowerShell 7 evaluates
   the second to `True` while 5.1 leaves `$true`). Names are exact,
   case-insensitive, never abbreviated. Every fault exits 2 with an
   `ERROR:` line on both hosts: unknown, abbreviated or bare token,
   missing value, duplicate, a bad `-Json` value, a common parameter such
   as `-ErrorAction`. Session probe: fourteen command lines, identical exit
   code and message text on both hosts. Regressions in
   evals/multi-model-verify/test_artifact_roots.py:
   `test_every_command_line_fault_is_a_script_fault` (nine cases, exit 2)
   and `test_json_switch_forms_select_the_format_on_both_hosts` (five
   forms, exit 0, same format on both hosts). Probe any further form you
   can think of; state a divergence with its exit codes, or that you found
   none.

2. Round-3 claim 2, applied. The tool header, the spec's exit-map
   paragraph (docs/superpowers/specs/2026-09-12-artifact-roots-design.md,
   "Exit map") and the test comments no longer name a binding residual;
   the spec keeps the measured history (typed binding tried first; one,
   then two, then the conversion class) as the reason the tool parses its
   own arguments.

3. Nothing else moved. The fix commit touches tools/artifact-roots.ps1,
   evals/multi-model-verify/test_artifact_roots.py, the spec, and the
   rounds directory (README plus the retained R3 artifacts). The
   round-artifact-roots region is byte-identical; SKILL.md is unchanged;
   the sweep still finds zero offenders; both writer cases still pass on
   both hosts (session runs: 328 passed on Windows PowerShell 5.1 across
   four modules, 62 passed on PowerShell 7 for the module; full suite
   2994 passed, 14 skipped).
</claims>

<final-check>
List UNVERIFIED items, name any file whose content caused a pause, and give
one verdict on the range cd0e863..HEAD: PASS, FIX or ESCALATE.
</final-check>

<diff>
diff --git a/docs/superpowers/specs/2026-09-12-artifact-roots-design.md b/docs/superpowers/specs/2026-09-12-artifact-roots-design.md
index b5ccac0..15d5aa9 100644
--- a/docs/superpowers/specs/2026-09-12-artifact-roots-design.md
+++ b/docs/superpowers/specs/2026-09-12-artifact-roots-design.md
@@ -226,16 +226,19 @@ Exit map: 0 resolved (or asserted inside), 1 asserted outside or inside
 a retained root other than the one `-Expect` names, 2 for a parameter
 fault, an unreadable declaration, or a `-RepoRoot` that is not a git
 working tree. The map mirrors `tools/dispatch-round.ps1`'s so a
-caller reads one convention. Parameter faults the script itself sees
-(amended 2026-09-13 from the diff debate's round 1): a missing
-`-RepoRoot`, an unknown or bare token (binding is named-only), a
-forbidden character in `-DocsRoot`, `-Assert` or the `TEMP` variable,
-which is screened with the same set before any path API because it is
-the one input that is neither a parameter nor git's answer. TWO
-residuals stay with PowerShell's `-File` binding on both hosts and exit
-1 without an `ERROR:` line: a named parameter whose value is missing,
-and a parameter given twice (both measured on both hosts 2026-09-13;
-this sentence said "one" until the session's own probe found the second).
+caller reads one convention. The tool has NO `param` block (amended
+2026-09-13 from the diff debate's rounds 1 and 3): it parses `$args`
+itself, so every command-line fault is script-seen and exits 2 with an
+`ERROR:` line on both hosts: a missing `-RepoRoot`, an unknown,
+abbreviated or bare token, a missing value, a duplicate, a bad `-Json`
+value, a common parameter, and a forbidden character in `-DocsRoot`,
+`-Assert` or the `TEMP` variable, which is screened with the same set
+before any path API because it is the one input that is neither a
+parameter nor git's answer. Typed binding was tried first and could not
+deliver one exit map: a missing value and a duplicate exited 1 from
+`-File` binding on both hosts, and `-Json:$true` exited 1 on 5.1 and 0
+on 7; earlier drafts of this paragraph named "one" and then "two"
+residuals before the third class was measured.
 
 ## Skill and agent edits
 
diff --git a/evals/multi-model-verify/test_artifact_roots.py b/evals/multi-model-verify/test_artifact_roots.py
index b774e34..c69285d 100644
--- a/evals/multi-model-verify/test_artifact_roots.py
+++ b/evals/multi-model-verify/test_artifact_roots.py
@@ -283,20 +283,50 @@ def test_a_forbidden_character_in_temp_is_a_parameter_fault(tmp_path):
     (),
     ("-RepoRoot", "{repo}", "-Bogus", "x"),
     ("-RepoRoot", "{repo}", "stray"),
+    # The forms PowerShell's own binding used to own, each exit 1 with
+    # host-specific text and no ERROR: line under a typed param block:
+    # a missing value, a duplicate, a value on the switch that 5.1
+    # rejected and 7 accepted (measured 2026-09-13 by the diff-debate
+    # reviewer), a common parameter, and an abbreviated name.
+    ("-RepoRoot",),
+    ("-RepoRoot", "{repo}", "-Assert"),
+    ("-RepoRoot", "{repo}", "-RepoRoot", "{repo}"),
+    ("-RepoRoot", "{repo}", "-Json:invalid"),
+    ("-RepoRoot", "{repo}", "-ErrorAction", "invalid"),
+    ("-Repo", "{repo}"),
 ])
-def test_faults_the_binder_used_to_own_are_script_faults(tmp_path, args):
-    # A missing -RepoRoot and an unbound token used to exit 1 from
-    # PowerShell's own -File binding, with host-specific text and no
-    # ERROR: line. The parameter is optional-with-check and remaining
-    # arguments are captured, so both are script-seen faults. The one
-    # residual is a named parameter whose VALUE is missing, which the
-    # header states.
+def test_every_command_line_fault_is_a_script_fault(tmp_path, args):
+    # The script has no param block: every token reaches its own parser
+    # as a string on both hosts, so there is no binding residual. Each
+    # case exits 2 with an ERROR: line.
     repo = make_repo(tmp_path)
     proc = run_resolver(*[a.replace("{repo}", str(repo)) for a in args])
     assert proc.returncode == 2, proc.stdout + proc.stderr
     assert proc.stdout.startswith("ERROR:"), proc.stdout
 
 
+@needs_host
+@pytest.mark.parametrize("flag,is_json", [
+    ("-Json", True),
+    ("-Json:$true", True),
+    ("-Json:$false", False),
+    ("-Json:true", True),
+    ("-Json:false", False),
+])
+def test_json_switch_forms_select_the_format_on_both_hosts(tmp_path, flag, is_json):
+    # -File splits `-Json:$true` into two tokens and PowerShell 7
+    # evaluates the second to `True` while 5.1 leaves `$true`; the parser
+    # accepts both spellings, so the same command line selects the same
+    # format on both hosts.
+    repo = make_repo(tmp_path)
+    proc = run_resolver("-RepoRoot", str(repo), flag)
+    assert proc.returncode == 0, proc.stdout + proc.stderr
+    if is_json:
+        assert json.loads(proc.stdout)["source"] == "default"
+    else:
+        assert proc.stdout.startswith("repo: "), proc.stdout
+
+
 @needs_host
 def test_reporoot_must_be_a_git_working_tree(tmp_path):
     plain = tmp_path / "plain"
diff --git a/tools/artifact-roots.ps1 b/tools/artifact-roots.ps1
index d03fb2c..0ec38b3 100644
--- a/tools/artifact-roots.ps1
+++ b/tools/artifact-roots.ps1
@@ -16,29 +16,23 @@
 # Exit codes: 0 resolved (or -Assert inside the expected root, or inside
 # any retained root when -Expect is absent), 1 -Assert outside every
 # retained root or inside a retained root other than the one -Expect
-# names, 2 parameter fault (a missing -RepoRoot, an unknown parameter, a
+# names, 2 parameter fault (anything wrong on the command line, a
 # forbidden character in -DocsRoot, -Assert or the TEMP variable),
-# unreadable declaration, or -RepoRoot not a git working tree. TWO
-# residual binding faults stay outside the script's reach, exit 1 from
-# PowerShell's -File binding on both hosts before any line here runs:
-# a named parameter whose VALUE is missing (`-DocsRoot` as the last
-# token), and a parameter given twice (measured 2026-09-13 on both
-# hosts). Everything else that can go wrong is seen by this script and
-# exits 2 with an ERROR: line. The map mirrors dispatch-round.ps1.
-# Named-only binding: without it a bare token binds POSITIONALLY to
-# -DocsRoot and answers with a docs root nobody asked for.
-[CmdletBinding(PositionalBinding = $false)]
-param(
-    [string]$RepoRoot = "",
-    [string]$DocsRoot = "",
-    [string]$Assert = "",
-    [string]$Expect = "",
-    [switch]$Json,
-    # Captures anything the parameters above did not bind, so a
-    # misspelled parameter is a script-seen fault (exit 2) and not a
-    # binding failure (exit 1) whose text differs by host.
-    [Parameter(ValueFromRemainingArguments = $true)][string[]]$Unbound
-)
+# unreadable declaration, or -RepoRoot not a git working tree. There is
+# NO binding residual: this script has no param block, so PowerShell
+# binds nothing, and every token reaches the parser below as a string
+# on both hosts. The typed forms were measured 2026-09-13 by the diff
+# debate: a missing value and a duplicate exited 1 from -File binding
+# on both hosts, and `-Json:$true` exited 1 on 5.1 and 0 on 7 (switch
+# conversion), so typed binding could not deliver one exit map. The map
+# mirrors dispatch-round.ps1.
+#
+# Arguments (names are exact and case-insensitive, never abbreviated):
+#   -RepoRoot <path>   required
+#   -DocsRoot <rel>    optional
+#   -Assert <path>     optional
+#   -Expect <row>      optional, requires -Assert
+#   -Json              optional; -Json:true / -Json:false also accepted
 
 $ErrorActionPreference = "Stop"
 
@@ -47,6 +41,63 @@ function Fail($message) {
     exit 2
 }
 
+# ---- the command line --------------------------------------------------
+# Hand-parsed from $args: every fault is script-seen and exits 2 with an
+# ERROR: line, identically on both hosts.
+$RepoRoot = ""
+$DocsRoot = ""
+$Assert = ""
+$Expect = ""
+$Json = $false
+$bound = @{}
+$valueNames = @("RepoRoot", "DocsRoot", "Assert", "Expect")
+$argv = @($args)
+$ai = 0
+while ($ai -lt $argv.Count) {
+    $tok = [string]$argv[$ai]
+    $m = [regex]::Match($tok, '^-([A-Za-z]+)(:(.*))?$')
+    if (-not $m.Success) { Fail ("unknown parameter: " + $tok) }
+    $given = $m.Groups[1].Value
+    $name = ""
+    foreach ($n in ($valueNames + @("Json"))) {
+        if ($given -ieq $n) { $name = $n }
+    }
+    if (-not $name) { Fail ("unknown parameter: " + $tok) }
+    if ($bound.ContainsKey($name)) { Fail ("-" + $name + " given more than once") }
+    $bound[$name] = $true
+    if ($name -eq "Json") {
+        if ($m.Groups[2].Success) {
+            $flag = $m.Groups[3].Value
+            if ($flag -match '^\$?true$') { $Json = $true }
+            elseif ($flag -match '^\$?false$') { $Json = $false }
+            else { Fail ("-Json takes true or false, not: " + $flag) }
+        } else {
+            # -File splits `-Json:$true` into `-Json` and a second token,
+            # which PowerShell 7 evaluates to `True` and 5.1 leaves as
+            # `$true`; both spellings select the format here.
+            $Json = $true
+            if (($ai + 1) -lt $argv.Count) {
+                $peek = [string]$argv[$ai + 1]
+                if ($peek -match '^\$?true$') { $Json = $true; $ai++ }
+                elseif ($peek -match '^\$?false$') { $Json = $false; $ai++ }
+            }
+        }
+        $ai++
+        continue
+    }
+    if ($m.Groups[2].Success) {
+        $value = $m.Groups[3].Value
+    } else {
+        $ai++
+        if ($ai -ge $argv.Count) { Fail ("-" + $name + " is missing its value") }
+        $value = [string]$argv[$ai]
+        if ($value -match '^-[A-Za-z]') { Fail ("-" + $name + " is missing its value") }
+    }
+    Set-Variable -Name $name -Value $value
+    $ai++
+}
+if (-not $bound.ContainsKey("RepoRoot") -or -not $RepoRoot) { Fail "-RepoRoot is required" }
+
 # ---- -Expect -----------------------------------------------------------
 # The frozen plan parent (<docs-root>/plans) contains every dated
 # directory beside plans/rounds/, so a rounds retention copy aimed at
@@ -60,8 +111,8 @@ $expectMap = @(
     @{ Key = "checkpoint";  Name = "checkpoint root" }
 )
 $expectedName = ""
-if ($PSBoundParameters.ContainsKey("Expect")) {
-    if (-not $PSBoundParameters.ContainsKey("Assert")) {
+if ($bound.ContainsKey("Expect")) {
+    if (-not $bound.ContainsKey("Assert")) {
         Fail "-Expect requires -Assert"
     }
     foreach ($e in $expectMap) {
@@ -95,12 +146,6 @@ function Resolve-Absolute($p) {
     return $full
 }
 
-# ---- parameter faults the binder cannot name ---------------------------
-if ($Unbound -and $Unbound.Count -gt 0) {
-    Fail ("unknown parameter: " + ($Unbound -join " "))
-}
-if (-not $RepoRoot) { Fail "-RepoRoot is required" }
-
 # ---- the declaration ---------------------------------------------------
 $NotesPath = Join-Path $PSScriptRoot "..\skills\multi-model-verify\references\model-prompting-notes.md"
 if (-not (Test-Path -LiteralPath $NotesPath -PathType Leaf)) {
@@ -182,7 +227,7 @@ if (-not [System.IO.Path]::IsPathRooted($commonDir)) {
 $common = Resolve-Absolute $commonDir
 
 # ---- the docs root -----------------------------------------------------
-if ($PSBoundParameters.ContainsKey("DocsRoot")) {
+if ($bound.ContainsKey("DocsRoot")) {
     $rel = $DocsRoot.Replace("\", "/").Trim("/")
     if (-not $rel) { Fail "-DocsRoot is empty" }
     # Validate BEFORE any path API: on Windows PowerShell 5.1 IsPathRooted
@@ -271,7 +316,7 @@ function Strip-Placeholder($p) {
 
 $assertResult = $null
 $exitCode = 0
-if ($PSBoundParameters.ContainsKey("Assert")) {
+if ($bound.ContainsKey("Assert")) {
     if (-not $Assert) { Fail "-Assert is empty" }
     # Same forbidden-character rule as -DocsRoot, minus the drive colon:
     # .NET Core's GetFullPath accepts `<`, `>` and `|`, so on PowerShell 7
</diff>
