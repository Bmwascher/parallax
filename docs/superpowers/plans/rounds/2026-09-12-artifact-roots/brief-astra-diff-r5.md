<role>Adversarial reviewer, equal weight, in a two-model debate (round 5 of the mode-diff debate you opened; round 2 was voided on this side).</role>

<task>Verify the application of your round-4 finding on the artifact-roots
range, now cd0e863..HEAD (head 5186b9e, one commit past 8556599). The user
extended the fix-verify budget by two exchanges after your ESCALATE, so
this is exchange 5 of 6. `git diff 8556599..HEAD` is the fix diff and is
appended under <diff> (retained round records excluded).</task>

<rules>
Same rules as before: cite a repo-relative file:line for every claim you
make or contest, anchored with the full path the first time; uncited claims
are struck; PASS a claim that stands; FIX with the specific fix and its
evidence, or ESCALATE, when it does not; one verdict on the range. The
round is non-interactive; reading any file here and running
`tools/artifact-roots.ps1` read-only on either host against this working
directory or a disposable repository under your own temp directory is
authorized, including exact-token invocation through
`ProcessStartInfo.ArgumentList` as you did in round 4. Report UNVERIFIED
items in the final check, and name any file whose content caused a pause.
State findings as plain prose, no stock phrases, no closing summary, no
contrastive framing this brief did not raise.

Certification unit and the pre-existing-defect rule are unchanged. A round
with no new substantive finding and no contested point is the adjudicated
dry round that ends the debate; a new substantive finding uses the last
exchange for its verification.
</rules>

<claims>
1. Round-4 claim 1, applied. tools/artifact-roots.ps1 parses the RAW
   process command line: `[Environment]::GetCommandLineArgs()`, the tokens
   after the entry whose full path equals `$PSCommandPath`, with `$args`
   as the fallback only when that path is not on the line (dot-sourced,
   or a host whose command line does not name it). `-File` preprocessing
   therefore cannot hide a token: an empty inline value on any parameter
   (`-Assert:`, `-DocsRoot:`, `-Json:`, alone or followed by more tokens)
   exits 2 with an `ERROR:` line on both hosts, measured with exact
   `ArgumentList` tokens on both. A quoted path with spaces arrives as one
   token. Regressions in evals/multi-model-verify/test_artifact_roots.py:
   four new cases in `test_every_command_line_fault_is_a_script_fault`
   (thirteen in all) and `test_raw_command_line_keeps_a_path_with_spaces_whole`.
   Probe any further way a token could differ between the raw line and
   what the parser sees on either host (quoting, a trailing backslash
   before a closing quote, an empty string argument), and state a
   divergence with its exit codes, or that you found none.

2. Round-4 claim 2, applied. The tool header, the spec's exit-map
   paragraph (docs/superpowers/specs/2026-09-12-artifact-roots-design.md)
   and the test comment name the raw command line and record why `$args`
   was not enough; no sentence claims a residual or claims `$args` is
   complete.

3. Nothing else moved. The fix commit touches tools/artifact-roots.ps1,
   evals/multi-model-verify/test_artifact_roots.py, the spec, and the
   rounds directory (README plus the retained R4 artifacts). The
   round-artifact-roots region is byte-identical; SKILL.md is unchanged;
   the sweep still finds zero offenders; both writer cases pass on both
   hosts (session runs: 333 passed on Windows PowerShell 5.1 across four
   modules, 67 passed on PowerShell 7 for the module; full suite 2999 passed, 14 skipped).
</claims>

<final-check>
List UNVERIFIED items, name any file whose content caused a pause, and give
one verdict on the range cd0e863..HEAD: PASS, FIX or ESCALATE.
</final-check>

<diff>
diff --git a/docs/superpowers/specs/2026-09-12-artifact-roots-design.md b/docs/superpowers/specs/2026-09-12-artifact-roots-design.md
index 15d5aa9..e0f9298 100644
--- a/docs/superpowers/specs/2026-09-12-artifact-roots-design.md
+++ b/docs/superpowers/specs/2026-09-12-artifact-roots-design.md
@@ -227,18 +227,23 @@ a retained root other than the one `-Expect` names, 2 for a parameter
 fault, an unreadable declaration, or a `-RepoRoot` that is not a git
 working tree. The map mirrors `tools/dispatch-round.ps1`'s so a
 caller reads one convention. The tool has NO `param` block (amended
-2026-09-13 from the diff debate's rounds 1 and 3): it parses `$args`
-itself, so every command-line fault is script-seen and exits 2 with an
-`ERROR:` line on both hosts: a missing `-RepoRoot`, an unknown,
-abbreviated or bare token, a missing value, a duplicate, a bad `-Json`
-value, a common parameter, and a forbidden character in `-DocsRoot`,
-`-Assert` or the `TEMP` variable, which is screened with the same set
-before any path API because it is the one input that is neither a
-parameter nor git's answer. Typed binding was tried first and could not
-deliver one exit map: a missing value and a duplicate exited 1 from
-`-File` binding on both hosts, and `-Json:$true` exited 1 on 5.1 and 0
-on 7; earlier drafts of this paragraph named "one" and then "two"
-residuals before the third class was measured.
+2026-09-13 from the diff debate's rounds 1, 3 and 4): it parses the RAW
+process command line (`[Environment]::GetCommandLineArgs()`, the tokens
+after its own path; `$args` only when its path is not on that line), so
+every command-line fault is script-seen and exits 2 with an `ERROR:`
+line on both hosts: a missing `-RepoRoot`, an unknown, abbreviated or
+bare token, a missing or EMPTY value (`-Assert:`), a duplicate, a bad
+`-Json` value, a common parameter, and a forbidden character in
+`-DocsRoot`, `-Assert` or the `TEMP` variable, which is screened with
+the same set before any path API because it is the one input that is
+neither a parameter nor git's answer. Typed binding was tried first and
+could not deliver one exit map: a missing value and a duplicate exited 1
+from `-File` binding on both hosts, and `-Json:$true` exited 1 on 5.1
+and 0 on 7; then `$args` proved lossy, because `-File` preprocessing
+drops an empty inline value on both hosts before any script runs, so an
+intended `-Assert:` answered 0 with no assertion. Earlier drafts of this
+paragraph named "one" and then "two" residuals before those classes were
+measured.
 
 ## Skill and agent edits
 
diff --git a/evals/multi-model-verify/test_artifact_roots.py b/evals/multi-model-verify/test_artifact_roots.py
index c69285d..9b7642c 100644
--- a/evals/multi-model-verify/test_artifact_roots.py
+++ b/evals/multi-model-verify/test_artifact_roots.py
@@ -294,17 +294,40 @@ def test_a_forbidden_character_in_temp_is_a_parameter_fault(tmp_path):
     ("-RepoRoot", "{repo}", "-Json:invalid"),
     ("-RepoRoot", "{repo}", "-ErrorAction", "invalid"),
     ("-Repo", "{repo}"),
+    # An EMPTY inline value: -File preprocessing drops `-Assert:` as the
+    # last token and strips the colon from `-Json:` before $args exists,
+    # on both hosts, so an intended assertion answered 0 with no
+    # assertion line (measured 2026-09-13 by the diff-debate R4
+    # reviewer). The parser reads the raw process command line instead.
+    ("-RepoRoot", "{repo}", "-Assert:"),
+    ("-RepoRoot", "{repo}", "-DocsRoot:"),
+    ("-RepoRoot", "{repo}", "-Json:"),
+    ("-RepoRoot", "{repo}", "-Assert:", "-Json"),
 ])
 def test_every_command_line_fault_is_a_script_fault(tmp_path, args):
-    # The script has no param block: every token reaches its own parser
-    # as a string on both hosts, so there is no binding residual. Each
-    # case exits 2 with an ERROR: line.
+    # The script has no param block and parses the raw process command
+    # line: every token reaches its own parser as a string on both
+    # hosts, so there is no binding residual. Each case exits 2 with an
+    # ERROR: line.
     repo = make_repo(tmp_path)
     proc = run_resolver(*[a.replace("{repo}", str(repo)) for a in args])
     assert proc.returncode == 2, proc.stdout + proc.stderr
     assert proc.stdout.startswith("ERROR:"), proc.stdout
 
 
+@needs_host
+def test_raw_command_line_keeps_a_path_with_spaces_whole(tmp_path):
+    # The raw command line is split by the host's own rules; a quoted
+    # path with spaces must arrive as one token, or the parser would
+    # read its second word as a stray argument.
+    repo = make_repo(tmp_path, name="repo with space")
+    proc = run_resolver("-RepoRoot", str(repo), "-Assert",
+                        str(repo / "docs" / "superpowers" / "plans" / "rounds" / "2026-09-13-x" / "r.md"),
+                        "-Expect", "rounds")
+    assert proc.returncode == 0, proc.stdout + proc.stderr
+    assert "assert: inside rounds root" in proc.stdout
+
+
 @needs_host
 @pytest.mark.parametrize("flag,is_json", [
     ("-Json", True),
diff --git a/tools/artifact-roots.ps1 b/tools/artifact-roots.ps1
index 0ec38b3..d8c62e3 100644
--- a/tools/artifact-roots.ps1
+++ b/tools/artifact-roots.ps1
@@ -42,8 +42,17 @@ function Fail($message) {
 }
 
 # ---- the command line --------------------------------------------------
-# Hand-parsed from $args: every fault is script-seen and exits 2 with an
-# ERROR: line, identically on both hosts.
+# Hand-parsed from the RAW process command line, not $args: -File
+# preprocessing drops an empty inline value (`-Assert:` as the last
+# token vanishes, `-Json:` loses its colon) on both hosts before $args
+# exists, so an intended assertion could answer 0 with no assertion at
+# all (measured 2026-09-13 by the diff-debate R4 reviewer).
+# [Environment]::GetCommandLineArgs() still carries every token on both
+# hosts; the tokens after this script's own path are what is parsed.
+# When the script is not the -File target (dot-sourced, or run from a
+# host whose command line does not name it), $args is the fallback.
+# Every fault is script-seen and exits 2 with an ERROR: line,
+# identically on both hosts.
 $RepoRoot = ""
 $DocsRoot = ""
 $Assert = ""
@@ -52,6 +61,21 @@ $Json = $false
 $bound = @{}
 $valueNames = @("RepoRoot", "DocsRoot", "Assert", "Expect")
 $argv = @($args)
+$rawArgs = @([Environment]::GetCommandLineArgs())
+$self = $PSCommandPath
+for ($ri = 0; $ri -lt $rawArgs.Count; $ri++) {
+    $candidate = [string]$rawArgs[$ri]
+    $same = $false
+    try {
+        $same = [System.IO.Path]::GetFullPath($candidate).Equals(
+            [System.IO.Path]::GetFullPath($self), [System.StringComparison]::OrdinalIgnoreCase)
+    } catch { $same = $false }
+    if ($same) {
+        $argv = @()
+        if (($ri + 1) -lt $rawArgs.Count) { $argv = @($rawArgs[($ri + 1)..($rawArgs.Count - 1)]) }
+        break
+    }
+}
 $ai = 0
 while ($ai -lt $argv.Count) {
     $tok = [string]$argv[$ai]
@@ -68,6 +92,7 @@ while ($ai -lt $argv.Count) {
     if ($name -eq "Json") {
         if ($m.Groups[2].Success) {
             $flag = $m.Groups[3].Value
+            if (-not $flag) { Fail "-Json: has no value; write -Json, -Json:true or -Json:false" }
             if ($flag -match '^\$?true$') { $Json = $true }
             elseif ($flag -match '^\$?false$') { $Json = $false }
             else { Fail ("-Json takes true or false, not: " + $flag) }
@@ -87,6 +112,7 @@ while ($ai -lt $argv.Count) {
     }
     if ($m.Groups[2].Success) {
         $value = $m.Groups[3].Value
+        if (-not $value) { Fail ("-" + $name + " is missing its value") }
     } else {
         $ai++
         if ($ai -ge $argv.Count) { Fail ("-" + $name + " is missing its value") }
</diff>
