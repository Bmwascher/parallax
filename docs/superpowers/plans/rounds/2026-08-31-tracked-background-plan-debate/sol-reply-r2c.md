Pause the build and replace the plan before Task 3. This is no longer a plan that can be repaired safely while implementation proceeds: it contains a false-completion race, the proposed cwd correction can silently recreate the back-channel, and the round-evidence protocol loses every round following an unbound attempt.

## Blocking findings

1. **An unfinished execution can read as completed.**

The wrapper publishes `pid` and `startticks` with two independent overwriting writes, not one atomic identity transaction ([design:121](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-tracked-background-dispatch-design.md:121)). The tests acknowledge a measured 15–30 ms gap between those writes ([test_dispatch_detached.py:141](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/evals/multi-model-verify/test_dispatch_detached.py:141)).

Run the same prepared wrapper twice:

- A finishes and leaves `exit=0` plus `reply`.
- B starts and overwrites `pid` before overwriting `startticks`.
- Poll sees B’s live pid with A’s ticks, classifies the identity mismatch as `DEAD`, then accepts A’s terminal artifacts as `reply-present` ([dispatch-detached.ps1:483](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:483), [dispatch-detached.ps1:491](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:491)).
- The existing recycled-pid test explicitly pins that fall-through to success when old terminal artifacts exist ([test_dispatch_detached.py:689](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/evals/multi-model-verify/test_dispatch_detached.py:689)).

Thus B is unfinished while Poll exits 0. The receipt binds the directory, but not one execution within it. This applies to all five planned wrappers because both Codex and Kimi use the same two writes ([plan:348](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:348), [plan:420](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:420)).

Require a persistent create-new execution claim and one atomically published identity record containing pid plus ticks. Add concurrent-double-start, rerun-after-completion, and death-between-identity-writes tests.

I searched receipt reuse, prepare interruption, missing/malformed pid and ticks, unmeasurable start time, live-process ordering, missing/partial exit and reply, stale terminal artifacts, and concurrent/rerun execution. I found no second distinct false-completion path in the current Poll ordering; the ordinary missing and partial cases remain nonzero ([dispatch-detached.ps1:444](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:444)).

2. **The cwd-file correction is not sound as written.**

The proposed `Set-Location` has neither `-ErrorAction Stop` nor a terminating-error wrapper, and it appears before the wrapper’s `try` ([plan:348](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:348), [plan:354](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:354)). A missing/deleted target can therefore report an error and continue into the client from the harness’s directory—the exact silent fallback this correction exists to prevent. Kimi has the same shape ([plan:420](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:420)).

Nor does the receipt bind cwd: its schema allows exactly four fields, none of them working-directory identity ([dispatch-detached.ps1:248](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:248)). Fresh directory creation prevents inheritance from an earlier prepare, but nothing detects a wrong initial value, post-prepare mutation, a deleted target, or a non-filesystem provider.

The correction must:

- Resolve and require a filesystem directory.
- Bind its canonical value into the receipt.
- Read and set it with terminating semantics.
- Verify the resulting filesystem location before invoking the client.
- Bind the client transcript’s `workdir:` back to the expected mirror; the current route check only verifies model, provider, effort and sandbox ([SKILL.md:270](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/skills/multi-model-verify/SKILL.md:270)).

At head `937bcb0`, Task 1a remains proposed rather than built: the actual parameter list still has no `-WorkingDirectory` ([dispatch-detached.ps1:220](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:220)).

3. **The second lost round exposes a documented cross-lane state-chain defect.**

The skill says round 1 captures state before dispatch, but every later round uses the previous clean `nextState` ([SKILL.md:281](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/skills/multi-model-verify/SKILL.md:281)); fallbacks repeats that rule verbatim ([fallbacks.md:113](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/skills/multi-model-verify/references/fallbacks.md:113)). A failed Codex binding emits no `nextState` ([read-codex-round-evidence.ps1:91](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/read-codex-round-evidence.ps1:91)); state is emitted only after a clean binding ([read-codex-round-evidence.ps1:1255](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/read-codex-round-evidence.ps1:1255)). Consequently, a void or refused invocation advances the append-only rollout but leaves the documented bookmark behind. The four-user-record refusal was correct ([read-codex-round-evidence.ps1:1079](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/read-codex-round-evidence.ps1:1079)); the protocol feeding it was wrong.

The class sweep found the same chaining assumption in Kimi ([read-kimi-round-evidence.ps1:28](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/read-kimi-round-evidence.ps1:28), [backup-lane.md:376](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/skills/multi-model-verify/references/backup-lane.md:376)).

Every attempted dispatch—not every accepted reply—needs a boundary captured immediately before it. To make “before” enforceable rather than honor-system, seal the prior-state digest into the create-new preparation receipt before the wrapper can run. A state reconstructed after the reply must not be capable of satisfying that receipt.

4. **The draft still failed to inventory launcher responsibilities.**

Deleting the pid-only kill, `GetProcessTimes`, and top-level `Add-Type` is the right disposal: `-Prepare` starts no process, so those launch-only failure paths no longer exist ([plan:44](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:44)). It is not a dodge.

But cwd was not the only load-bearing launcher behavior. The prior contract also deliberately selected the caller’s current PowerShell host; the skill explains why a bare `powershell` silently changes a PS7 call to PS5 ([SKILL.md:239](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/skills/multi-model-verify/SKILL.md:239)). The tests run the wrapper with the selected host plus `-NoProfile -NonInteractive` ([test_dispatch_detached.py:118](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/evals/multi-model-verify/test_dispatch_detached.py:118)), while the plan only says to run a named background command. The tool also still creates `stdin.empty`, although the new design names no consumer ([dispatch-detached.ps1:566](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:566)).

The re-plan must explicitly settle host selection, `-NoProfile`, `-NonInteractive`, stdin EOF, stdout/stderr ownership, wrapper/client process-tree termination, and task cancellation.

Most importantly, the plan does not test its principal claimed benefit. The spec promises a named task row, completion notification and an open conversation ([design:109](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-tracked-background-dispatch-design.md:109)); Task 6 measures only prepare time and Poll states ([plan:487](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:487)). Those harness behaviours and session-termination semantics need direct probes.

5. **A typoed optional switch produces a wrong interface, not refusal.**

Because the script has an ordinary parameter block and never rejects `$args`, a valid `-Poll ... -Jsoon` silently ignores the intended `-Json`. Poll then emits plain text instead of JSON ([dispatch-detached.ps1:220](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:220), [dispatch-detached.ps1:401](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:401)). Prepare has the same optional-output branch ([dispatch-detached.ps1:612](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:612)).

The plan’s test supplies only the typo and no valid mode, so its own mode check happens to return 2 without exercising this case ([plan:154](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:154)). Reject nonempty `$args` before mode execution and test a typo alongside an otherwise complete Prepare and Poll invocation.

## `not-started`

For result safety, collapsing never-run, died-before-identity, and live-before-identity is conservative: absence of pid is checked before terminal artifacts, and only `reply-present` maps to zero ([dispatch-detached.ps1:470](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:470), [dispatch-detached.ps1:395](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:395)).

Operationally, the name is too strong: it must mean “identity not yet available,” never “safe to start again.” A missing/unreadable cwd is different again—committed preparation corruption, possibly after execution began—and should have its own nonzero state rather than claiming the process was not started.

## Visibility versus survival

The trade is real for the simple one-process design, but not fundamental. A tracked supervisor can launch an OS-detached worker, remain visible while polling it, and leave the worker recoverable after session death. The cost is substantial: two identities, cancellation forwarding, orphan reconciliation, and a repaired detached launcher. The repo already records the orphan-client difficulty when the wrapper dies first ([model-prompting-notes.md:410](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/skills/multi-model-verify/references/model-prompting-notes.md:410)).

The user’s simpler visibility-over-survival choice is reasonable, but the plan currently says the worker “probably” dies with the session rather than measuring it ([design:192](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-tracked-background-dispatch-design.md:192)). Measure that before freezing the choice.

## Plan integrity and Task 3

The plan contradicts itself: Task 1 now says it kept `-WorkingDirectory` ([plan:140](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:140)), while Task 1a truthfully says Task 1 deleted it ([plan:183](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:183)). Task 3 then says “all four parameters” despite the corrected Prepare interface having five required values ([plan:338](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:338)). Restore Task 1 as actually executed and place the correction afterward.

For the size block, move historical/rationale material out of `SKILL.md` while retaining the complete operational shape independently at both call sites. Do not globally deduplicate those sites, and do not raise the ceiling first. That costs an extra reference read when historical detail is needed, but preserves the per-site oracle and the current honest warning/ceiling boundary of 5250/6500 ([skill_lint.py:117](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/evals/tools/skill_lint.py:117)). If a measured, materially trimmed skill still cannot fit, then consider a minimal, explicitly pinned ceiling increase.

The `AGENTS.md` and budget corrections are sound: the file is now protected from `git add -A` by the ignore rule ([.gitignore:10](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/.gitignore:10)), and the budget is back at 5250 while the ceiling remains 6500 ([skill_lint.py:126](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/evals/tools/skill_lint.py:126)).

The two consecutive lost rounds, the false original premise, the cwd omission, and the new false-completion race are process evidence that this plan should not be incrementally pushed through. Preserve the existing commits as evidence, leave Task 3 stopped, re-derive the invariants—including dispatch, working-tree identity, execution identity, harness visibility, and evidence-boundary lifecycle—and review that replacement plan before resuming implementation.

ESCALATE