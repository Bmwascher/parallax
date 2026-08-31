Verdict: I would not ship Option C unchanged. Fresh-directory preparation and a create-new claim replace process identity, but they do not by themselves prove that the exact harness task being collected has completed. The smallest repair is to make harness-task completion and exit status a mechanical part of success.

## 1. Attack C’s central claim

No: the claim plus directory freshness is necessary, but not sufficient on its own.

Concrete false-completion case 1 — outcome published before process completion:

1. The wrapper creates its claim, runs the client, obtains a nonempty reply, and writes `exit=0`.
2. After that write returns but before the PowerShell process exits, the process is suspended, hangs during teardown, or is killed.
3. C’s classifier sees claim + `exit=0` + nonempty reply and returns `reply-present`, although the harness task is still running or was killed.

That interval exists because `exit` is written by the wrapper process itself; the wrapper design calls it the last write, not an atomic consequence of OS process termination ([tracked-background design:141](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-tracked-background-dispatch-design.md:141)). The current Codex wrapper likewise writes `exit` as its last PowerShell statement ([SKILL.md:204](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/skills/multi-model-verify/SKILL.md:204), [SKILL.md:207](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/skills/multi-model-verify/SKILL.md:207)).

The current implementation avoids this by checking liveness before opening `exit` or `reply` ([dispatch-detached.ps1:622](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:622), [dispatch-detached.ps1:630](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:630), [dispatch-detached.ps1:641](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:641)). Its test explicitly establishes that a live wrapper may already have written reply content and must short-circuit before terminal classification ([test_dispatch_detached.py:659](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/evals/multi-model-verify/test_dispatch_detached.py:659), [test_dispatch_detached.py:669](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/evals/multi-model-verify/test_dispatch_detached.py:669)).

Therefore C’s statement that a still-running round “also” necessarily has no exit file is false as a filesystem claim ([costing:140](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-dispatch-options-costing.md:140), [costing:142](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-dispatch-options-costing.md:142)). Whether this naturally becomes a long window is speculative; the write-before-process-exit ordering is not.

Concrete false-completion case 2 — a later invocation answers with A’s artifacts:

1. A completes, leaving its claim, `exit=0`, and reply.
2. The same prepared wrapper is dispatched as B.
3. B is killed before its first act, or reaches the create-new claim and is refused.
4. Post-B classification still finds A’s claim and terminal artifacts and returns `reply-present`.

This is the same execution-association shape that caused the escalation: A’s artifacts answered for an unfinished B ([ESCALATION.md:22](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/plans/rounds/2026-08-31-tracked-background-plan-debate/ESCALATION.md:22), [ESCALATION.md:28](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/plans/rounds/2026-08-31-tracked-background-plan-debate/ESCALATION.md:28)). The claim stops B from overwriting A, but claim presence does not say which invocation created it. The current tool already admits that an old receipt supplied with its matching directory and label answers with the old result ([dispatch-detached.ps1:49](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:49)); that residual is pinned as `reply-present` ([test_dispatch_detached.py:531](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/evals/multi-model-verify/test_dispatch_detached.py:531)).

Both cases become safe if success additionally requires completion of the exact harness task with an acceptable command exit. The harness supplies a task id, output path, and exit-code trailer ([costing:39](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-dispatch-options-costing.md:39), [costing:41](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-dispatch-options-costing.md:41)). C mentions that notification as operational information but does not include it among the classifier’s success inputs ([costing:119](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-dispatch-options-costing.md:119), [costing:147](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-dispatch-options-costing.md:147)).

I searched these defect shapes: preparation interruption, directory and receipt reuse, concurrent and sequential wrapper reruns, death before/during claim creation, death after reply/exit publication, partial or unreadable receipt/claim/exit/reply, and task-notification/outcome association. Ordinary missing or malformed exit and empty reply cases remain conservative in the current classifier ([dispatch-detached.ps1:505](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:505), [dispatch-detached.ps1:630](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:630)). The two task-association cases above are the defects I found.

## 2. Losing “running versus crashed”

The diagnostic loss is acceptable after the exact-task completion gate is added. Without that gate, it is worse than the costing says.

If no completion notification exists, the round must remain unknown/incomplete; the classifier must not infer success from disk. Under settled R7, abandoning it and preparing a fresh dispatch is acceptable. The harness already provides the named task and completion signal that liveness was trying to reconstruct ([dispatch invariants:171](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-dispatch-invariants.md:171), [dispatch invariants:179](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-dispatch-invariants.md:179)).

However, “just re-dispatch” is not free. Every attempted round advances the append-only reviewer record, so recovery must capture a new evidence boundary immediately before the new dispatch; reusing the last clean bookmark is a shipped defect ([dispatch invariants:208](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-dispatch-invariants.md:208), [dispatch invariants:219](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-dispatch-invariants.md:219)). The real cost is additional quota and evidence lifecycle work, not a reason to retain PID liveness.

## 3. A fourth option

Yes: call it D, “completion-coupled C.”

Keep C’s preparation, receipt, claim, cwd binding, and outcome states, but make classification the final act of the same harness-tracked wrapper:

1. Harness starts the named wrapper.
2. Wrapper creates the claim first.
3. It performs terminating cwd relocation, runs the client, and records the outcome.
4. It invokes the classifier, emits one outcome record to its own harness-captured stdout, and exits with the classifier’s mapped status.
5. Only that exact task’s completion notification and output are collected. Post-hoc classification is diagnostic, never authoritative.

This remains within the settled architecture: the harness launches and owns the wrapper; no tool launches an OS-detached process. If classification succeeds but the wrapper is killed before it exits, the exact task does not deliver a successful completion. If B loses the claim, B’s own harness task exits nonzero and its output cannot be replaced by A’s separate task output.

Cost against R1–R8:

- R1–R4 and R7: identical harness-tracked dispatch to C.
- R5: still requires explicit no-window integration tests.
- R6: still requires canonical cwd in the receipt, terminating relocation, and validation of the client’s `workdir:` report—the invariants require all three ([dispatch invariants:68](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-dispatch-invariants.md:68), [dispatch invariants:73](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-dispatch-invariants.md:73)).
- R8: stronger than C because outcome success and exact-task completion share one exit path.

Ownership is approximately C’s: no PID, start ticks, recycling logic, C#, or process APIs. It adds a small wrapper epilogue and harness integration tests, while removing the ordinary post-notification classification step.

## 4. Requirements

R1–R8 are directionally right but incomplete.

- Missing: exact task-to-outcome attribution. Define success as: the exact named harness task completed acceptably, its classifier returned `reply-present`, and the evidence binder was clean. `reply-present` is explicitly not a verdict by itself ([dispatch-detached.ps1:88](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/tools/dispatch-detached.ps1:88)); the skill separately requires binding the reply to the sent brief ([SKILL.md:281](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/skills/multi-model-verify/SKILL.md:281)).

- R6 states the destination but not its enforcement. The receipt must bind the canonical filesystem directory, relocation must fail terminatingly, and the client’s `workdir:` must agree ([dispatch invariants:62](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-dispatch-invariants.md:62), [dispatch invariants:68](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-dispatch-invariants.md:68)).

- Missing: explicit interpreter and execution environment. Host selection, `-NoProfile`, `-NonInteractive`, stdin EOF, and stdout/stderr ownership are contract, not convention ([dispatch invariants:33](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-dispatch-invariants.md:33), [dispatch invariants:42](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-dispatch-invariants.md:42)).

- Missing: fail-closed argument handling. A mistyped optional switch is presently silently absorbed in the withdrawn interface ([dispatch invariants:234](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-dispatch-invariants.md:234)).

- Missing: direct verification of the claimed harness behavior—task row, notification, and open conversation ([dispatch invariants:143](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-dispatch-invariants.md:143)).

- R4’s word “everywhere” is too broad. The invariants retain harness-owned background subagents while making the named harness command the only review-client dispatch method ([dispatch invariants:165](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-dispatch-invariants.md:165), [dispatch invariants:171](/C:/Users/Brandon/AppData/Local/Temp/kerev-dd1/docs/superpowers/specs/2026-08-31-dispatch-invariants.md:171)). Scope R4 explicitly to review-round client dispatch.

## 5. Ship decision

I would not ship C as currently stated.

Smallest ship-worthy change: mechanically couple `reply-present` to completion of the exact harness task—preferably by running classification as the wrapper’s final act and mapping that result onto the wrapper’s own exit code. Add tests for:

- reply and `exit=0` published while the wrapper is held alive;
- kill during that hold;
- concurrent double start;
- rerun after completion;
- named task row, notification, and open conversation.

That preserves C’s deletion of the liveness model while closing the gap it currently assumes away.

FIX