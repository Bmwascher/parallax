1. Exit sentence and pin — CLOSES

The four-clause mapping is identical in the Task 1 contract, the per-site literal assertion, and the point-of-use instruction: exit 0 only for `reply-present`, exit 3 for unfinished `running`, exit 1 for every other state, and exit 2 for invocation/internal errors. [plan:57](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:57) [plan:368](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:368) [plan:465](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:465)

CLOSES.

2. Honest failure counts — CLOSES

Task 3 now expects three failures and one already-passing centralization guard, explicitly explaining why that guard is green before the task. Task 4 does the corresponding three-failure/one-pass accounting for Kimi. [plan:401](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:401) [plan:559](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:559)

CLOSES.

3. Positive spec oracle — DOES NOT CLOSE

The loop counts each token separately, but it does not fail when an early token is missing. `grep -c` can return failure for `dispatch-detached.ps1`, then the loop continues; if the final `-ExpectedDispatchDir` check succeeds, the loop’s overall status is successful. Thus the displayed count can be `0` while the oracle still passes. [plan:802](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:802) [plan:809](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:809)

Specific fix: make every iteration fail explicitly, for example `grep -q -- "$t" || exit 1`.

DOES NOT CLOSE — fix the loop’s failure propagation.

4. Scope-table task numbers — DOES NOT CLOSE

The required mapping is correctly stated as Task 3, Task 3, Task 4, Task 4, Task 4, but its effective automated check only rejects surviving `Task 5` text. An erroneous table containing five `Task 4` values would satisfy that grep while violating the required mapping. “Read the five rows” is a manual instruction, not the task-local oracle requested by the plan’s own test-first invariant. [plan:23](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:23) [plan:782](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:782)

Specific fix: parse the five scope-table rows and assert their task values exactly equal `["Task 3", "Task 3", "Task 4", "Task 4", "Task 4"]`.

DOES NOT CLOSE — replace the Task-5-only grep with an exact mapping assertion.

## Sweep

The base rate remains eleven rounds out of eleven finding a completion-model hole, a non-binding oracle, or an internal contradiction.

I found no new false-completion path. I searched the launch publication window, cross-act receipt/directory/round substitution, PID reuse, malformed or unreadable artifacts, live partial replies, missing exit/reply artifacts, wrapper failure, and status/exit-code ambiguity against the specified launch and ordered poll paths. [plan:71](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:71) [plan:117](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:117) [plan:128](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:128)

I did find two new instances of the other named class: both newly introduced Task 9 oracles can pass without proving their stated condition. They are the positive mechanism loop and the scope-table mapping check described above. [plan:782](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:782) [plan:802](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:802)

The fix-introduces-defect rate is not a reason to freeze known-bad verification. The remaining defects are narrowly confined to two oracle implementations; executing now would contradict the plan’s requirement that a task-local oracle fail when its change is absent. [plan:23](C:/Users/Brandon/AppData/Local/Temp/kerev-i32b/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:23)

The plan is not ready to freeze. The smallest sufficient change set is:

- Make each token check in the mechanism-section loop terminate unsuccessfully when absent.
- Machine-assert the exact five-row Task 3/Task 4 scope mapping.

No further mechanism revision is justified by this sweep.

**FIX**