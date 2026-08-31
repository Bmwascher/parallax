## Verdict

The completion-state model itself passes: I searched all launch, poll, wrapper, stale-artifact, catch, seam, and exit-code paths and found no way for a killed, hung, or unfinished round to read as completed. Overall verdict is still FIX because the declared source head retains the corrupted `AGENTS.md`, and several explicit contracts remain violated.

## Findings

1. Important — the accepted `AGENTS.md` fix is not in the declared range.

   At `6949ee8`, `AGENTS.md` still exists and identifies this as a “Codex plugin” (`AGENTS.md@6949ee8:1-4`) with the invalid commands at `AGENTS.md@6949ee8:93-95`. That is exactly the file the prior review said could not ship ([fable-whole-branch-review.md:34](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/plans/rounds/2026-08-30-item32-diff-debate/fable-whole-branch-review.md:34)). The ledger claims it was untracked and left only on disk ([build-ledger.md:200](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/build-ledger.md:200), [build-ledger.md:212](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/build-ledger.md:212)), but the actual deletion is the mirror-remediation commit `c7ac9d6`, after the declared head. Apply the deletion to the source branch and review the new head.

2. Important — the dispatcher still has a pid-only kill, the same class fixed in the eval reaper.

   The contract says identity is pid plus start time ([model-prompting-notes.md:354](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/skills/multi-model-verify/references/model-prompting-notes.md:354)), but the launch catch executes bare `taskkill /PID` ([dispatch-detached.ps1:764](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:764)). This is materially reachable: the hold seam can wait sixty seconds after creation ([dispatch-detached.ps1:724](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:724)), during which a short wrapper can exit and its pid can recycle before a later failure triggers the catch. Recheck the recorded ticks immediately before killing, treating unknown as not ours.

   Class sweep found two more shapes:

   - Test teardown also kills by pid alone ([test_dispatch_detached.py:224](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/evals/multi-model-verify/test_dispatch_detached.py:224), [test_dispatch_detached.py:232](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/evals/multi-model-verify/test_dispatch_detached.py:232)). This is a much tighter, test-only window and can be filed.
   - Operator guidance likewise names bare `taskkill` after polling ([model-prompting-notes.md:378](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/skills/multi-model-verify/references/model-prompting-notes.md:378)). It should require an identity recheck at the point of abandonment.

3. Confirmed — `GetProcessTimes` can leave a started tree alive.

   The child exists before `GetProcessTimes`; failure or `FromFileTimeUtc` conversion throws before the C# method returns the pid ([dispatch-detached.ps1:370](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:370), [dispatch-detached.ps1:391](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:391)). PowerShell sets `$launchedPid` only after that return ([dispatch-detached.ps1:713](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:713)), so the catch skips its kill. The split/integer-conversion boundary at lines 720–722 is the same shape. Fix the whole post-creation/pre-pid-publication class before merge; it directly contradicts the pinned “failure after start kills the tree” promise ([model-prompting-notes.md:308](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/skills/multi-model-verify/references/model-prompting-notes.md:308)).

4. Confirmed — exit 2 is not maintained for all binding/internal failures.

   The header promises exit 2 for parameter-binding and internal errors ([dispatch-detached.ps1:76](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:76)), but a Windows PowerShell 5.1 unknown parameter fails before the hand-written checks at lines 567–582. I reproduced this with an unknown switch.

   Class sweep found another instance: top-level `Add-Type` runs at line 239 before those checks and outside any catch. A compilation/temp/environment failure therefore also bypasses exit 2, and even `-Poll` unnecessarily depends on compiling launch-only C# ([dispatch-detached.ps1:239](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:239)). Move it into a caught launch path and either make unknown switches reach exit 2 or narrow the frozen contract. Fix before merge.

5. Confirmed — deviation 4 should be reverted.

   The plan authorizes raising only `BODY_TOKEN_CEILING` ([2026-08-30-item32-detached-dispatch.md:517](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:517)). Raising `BODY_TOKEN_BUDGET` from 5250 to 6250 weakened the warning threshold without changing gate success, and the body was already over 6250 after Task 6 ([build-ledger.md:72](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/build-ledger.md:72)). The comment still calls 6250 the rounded baseline ([skill_lint.py:102](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/evals/tools/skill_lint.py:102)), while tests repeat and pin that stale figure ([test_skill_lint_budget.py:232](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/evals/multi-model-verify/test_skill_lint_budget.py:232)). Keep the justified 6500 ceiling; restore the 5250 budget and update its pins.

## Central completion question

Explicitly: I searched and found no false-completion instance.

- Poll exit 0 exists only for `reply-present`; `running` is exit 3 ([dispatch-detached.ps1:542](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:542)).
- Receipt validity, expected-act identity, marker, token, pid, and matching start ticks all precede terminal artifacts; a live match returns immediately without reading exit or reply ([dispatch-detached.ps1:591](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:591), [dispatch-detached.ps1:622](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:622)).
- The receipt is created last with create-new semantics ([dispatch-detached.ps1:739](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:739), [dispatch-detached.ps1:756](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:756)).
- All five wrappers initialize failure, convert catches to nonzero, and write `exit` last: codex at [SKILL.md:195](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/skills/multi-model-verify/SKILL.md:195) and [SKILL.md:298](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/skills/multi-model-verify/SKILL.md:298); Kimi at [backup-lane.md:104](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/skills/multi-model-verify/references/backup-lane.md:104), [backup-lane.md:134](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/skills/multi-model-verify/references/backup-lane.md:134), and [backup-lane.md:474](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/skills/multi-model-verify/references/backup-lane.md:474).
- I also swept partial receipt/exit writes, stale directory and receipt reuse, recycled pids, wrapper-dead/client-live orphans, catches, and both environment seams. They resolve conservatively or to transport failure, not completion.

The `GetProcessTimes` defect can create an orphan, but no receipt is published, so it does not become a completed round.

## Five deviation judgments

1. CreateProcess allowlist: ratify. The frozen `Start-Process` mechanism cannot meet the nonblocking requirement under a piped caller; the handle allowlist addresses the measured cause ([dispatch-detached.ps1:204](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:204)). Keep it, but fix the post-creation failure and launch-only `Add-Type` hazards above.

2. Forward slashes: ratify. They preserve behavior while keeping both blanket gates intact ([test_backup_lane.py:120](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/evals/multi-model-verify/test_backup_lane.py:120)).

3. Back-channel needle: ratify. It still pins that `AGENTS.md` forces mirror construction rather than silent dispatch ([test_multi_model_verify.py:730](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/evals/multi-model-verify/test_multi_model_verify.py:730)).

4. Budget raise: reject and revert, as above.

5. `prompt_bytes_match=false`: ratify. Both hosts measured the same trailing CRLF while the binder accepted and canonical SHA matched ([wrapper-probe.md:34](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/wrapper-probe.md:34), [wrapper-probe.md:46](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/wrapper-probe.md:46)). That weakens no completion or attribution property.

The reaper’s substring minor is fixed correctly: it compares exact ticks, treats unknown as not ours, and rechecks before killing ([run_behavioral_evals.py:455](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/evals/tools/run_behavioral_evals.py:455), [run_behavioral_evals.py:505](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/evals/tools/run_behavioral_evals.py:505)). It introduced nothing worse.

Finally, the pre-fix full-suite counts do not cover the reaper identity change or source-head correction. Both host suites and the five local gates must be rerun after the fixes; the workflow wiring itself is now present in both host lists ([skill-evals.yml:93](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/.github/workflows/skill-evals.yml:93), [skill-evals.yml:112](C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/.github/workflows/skill-evals.yml:112)).

FIX