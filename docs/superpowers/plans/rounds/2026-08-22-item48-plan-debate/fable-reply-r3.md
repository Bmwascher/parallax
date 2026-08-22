Round 3, Fable lane. Continuity answered above from memory. Subject verdicted: the plan at commit `2f6dedf` on `item51-inline-brief-transport` (read from the working tree, which carries every round-2 disposition the brief lists).

All round-2 dispositions verified as applied where I checked them; the cited new instances are real — `tools/new-kimi-lane-home.ps1:96` assigns `$LockScript`, `:152` runs `&amp; $LockScript @LockArgs`, and `evals/tools/drift_statemachine_tests.ps1:552` launches a HOST through `&amp; $psHost ... -File` — that last one is correctly described and alternative 4 catches it. The Task 6 installed-cache command is sound: `installed_plugins.json` has exactly the `plugins`-keyed shape with `installPath` the command assumes (verified against the live file).

## A. Round-2 amendments, swept for the class

Four instances found, one material:

1. **The standing rule protects Task 4 and forgets Task 7 — the same asymmetry that created it.** The rule (plan 661-668) says "any task that adds a file under the record directory adds its explicit rows BEFORE its own commit", and Task 4 got Step 7 (1142-1164) implementing it. Task 7 creates `missing-pwsh/probe.py` — which carries `pwsh.exe` (1457), `subprocess.run` (1487) and `-File` (1479), all family matches — and Task 7's steps end at the commit (1560-1565) with NO inventory-row step. Under subagent-per-task dispatch, a Task 7 subagent never sees Task 3's prose. So probe.py is silently absorbed by the `docs/` prefix row and Task 9's green re-run attests `record — never executed` over an executed probe: the defect the rule exists to prevent, one task later than the fix, which is exactly how the round-2 instance was found. Same residue for new matched LINES that Tasks 4-8 write into `feasibility-record.md` itself (Measurement 2's text will contain `pwsh`): shifted old lines go STALE and red loudly at Task 9 Step 1, but the NEW matches have no rows and absorb silently. FIX: give Task 7 the same step, and add a `--emit | grep &lt;record-dir&gt;` = 0 assertion to Task 9 Step 1 covering the whole record directory, not just `reexec/`.

2. **Task 4 Step 7 orders classification from the plan's expectations.** "These are `test-harness` / `no-change`" (1155-1157) pre-writes the classification for rows nobody has read, in direct conflict with Task 3's non-negotiable rule "the classification must come from the line... never from the path or from this plan's expectations" (641-644). The values are almost certainly right; the method is the named failure mode. Reword as the expected outcome of reading, not the value to write.

3. **Two stale cross-references left by the round-2 rewrites.** (a) Task 9 Step 5 says the migration item "cites the test-matrix answer already written in Step 2" (1750) — after the reorder that answer is written in Step 3 (1678-1690); Step 2 is now the residual limits. (b) Task 4 Step 6 says "or `bound_exact` for the named arms" (1122-1123) — `bound_exact` no longer exists; the round-2 fix renamed it `stage_b_child_exact` (1019). Both are the record-drift-outruns-the-fix class.

4. Minor: the filter's miss-count is stated three ways — "four classes" (Architecture, line 16), "two classes" (survey docstring 285-287), "two classes" (Task 3 Step 4, 727-729). Each is defensible on its own scope (two prompted the family, two more widened it), but the artifact set now gives a reader conflicting counts. Also Task 5 Step 3's awk slice (1235) runs to the line before `powershell-hosts:` at workflow :59, so it INCLUDES the comment block at `.github/workflows/skill-evals.yml:49-58`, which contains `pwsh` and `powershell.exe` — the grep will print host-name hits inside the "Linux job" extract and the executor must recognize them as comments; the check answers the question only with that reading step, which the plan does not state.

## B. The two new blocks, read as code

`parent-named.ps1` (1032-1069) is correct: binding is measured before forwarding, the forward reconstructs from bound values (a real migration's shape), extras from a torn quote land in the implicit `$args` and surface as `stage_a_parent_exact: false` → red → the adjudication step fires. Hashtable key order is irrelevant to the `json.loads` dict comparison. Two defects in `run_named` (976-1025):

1. **An unparseable child JSON reads as a NO-shaped result instead of a broken arm.** `load()` returns the string `"unparseable"` (1006-1007); then `stage_b_child_count` = `len(NAMED)` because `parent_bound`/`child_bound` is not None (1020), so the broken gate (1087-1089) passes and the arm reports `stage_b_child_exact: false` — printed under "what a NO looks like" (1114-1115). A child that emitted garbage JSON measured nothing about argument fidelity, and this path files it as evidence toward NO. FIX: treat `"unparseable"` as broken in the gate.
2. **`stage_a_parent_count` and `stage_b_child_count` report the constant `len(NAMED)` (1018, 1020) — a sent count wearing a received-count name.** In `run()` these fields are measured (`len(got_parent)`); in `run_named` they are the number 5 whenever the file exists, including the unparseable case. An unmade measurement rendered as a clean number, in `results.json`, in the NO-arm. FIX: `None` or rename.

Also one nit caught by its own oracle: Step 7's prose file list (1144-1145) omits `parent-named.ps1`, but the `grep -c ... reexec` = 0 check covers it, so it cannot ship unclassified.

## C. The widened family

Too broad: no burial found — alternative 5 (backticked `.ps1`) pulls in many prose mentions, but that is the acknowledged trade, the per-family split absorbs it, and `not-a-launch` exists for alternative 4's false fires like `tools/codex-tool-surface-probe.ps1:193`.

Still dropped, one live instance: **`Start-Job` at `tools/check-drift.ps1:1054`** (`$job = Start-Job -ScriptBlock {`). No family matches the line — not a host name, not a launch-family token (`Start-Process` ≠ `Start-Job`), no bare shape. Yet `Start-Job` spawns a NEW PROCESS of the CURRENT host, and this particular job is the one the codex dispatch runs inside (the denylist test at `evals/multi-model-verify/test_multi_model_verify.py:2536` pins "between Start-Job and the codex call"). Under a migration this line decides which host the background dispatch child runs on — a `launch-inherit` entry point by the plan's own vocabulary, invisible to the filter. It belongs in the LAUNCH family (one token), not family 3; I checked the other candidates I could think of — dot-sourcing a `.ps1` (no instances outside docs/), `Invoke-Command -FilePath` (no instances), `shell: powershell` (none in the workflow) — and found only this one.

## D. Anything else

None beyond the above. The verdict logic, the reordered Task 9, the duplicate-refusing `load_rows`, the earlier-family assertions, and the three-outcome Task 7 write-up are sound as written.

Every finding this round is mechanical and bounded: one missing step, one gate condition, two constants, two cross-references, one regex token, and wording. Nothing touches the architecture, and nothing above is a reason to escalate.

FIX
