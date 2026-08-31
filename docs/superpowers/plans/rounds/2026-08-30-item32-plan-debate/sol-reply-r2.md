The revision closes seven findings, but four remain open. Most importantly, the stale-control-path defense is stated and tested but not implemented, and the Kimi deferral contradicts both item 51’s measurement and the linked design.

## Findings 1–11

1. False completion

This is not closed.

First, the requirement is self-contradictory: it says the wrapper must not exist before launch, but Task 4 requires writing the wrapper before launching it (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:20`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:363-369`). The rule must distinguish input artifacts that must be freshly created—wrapper and empty stdin—from output artifacts that must remain absent—PID, exit, reply, transcript, and launch logs.

Second, the actual launch block performs no pre-existence check or refusal; it immediately calls `Start-Process` and writes the PID (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:397-400`). Task 2 likewise pins no refusal mechanism (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:142-181`). Therefore Task 8 expects behavior no implementation step creates (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:631-637`).

Third, the five-state list duplicates “missing exit file” in states two and three, while omitting “fresh valid zero exit with no fresh reply” (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:263-270`). That omitted state was explicitly required by the original design (`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:172-175`).

Finally, killing the real wrapper after its reply appears but before the immediately following sidecar write is an uncontrolled millisecond-scale race (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:384-387`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:631-637`). The probe needs a deliberate pause/test seam between reply publication and sidecar publication.

**DOES NOT CLOSE — FIX: define six exhaustive states; use create-new semantics for fresh input files; add an executable preflight refusing every pre-existing output path; include launch stdout/stderr paths; and make Task 8’s kill window deterministic.**

2. Exit write was not last

The revised wrapper initializes failure before the `try`, captures the prior encoding outside it, joins `catch` and `finally` correctly, and publishes the sidecar after restoration (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:374-387`). Runtime exceptions before or during Codex now reach a nonzero sidecar; parse failures remain distinguishable through the exited-without-sidecar state (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:263-270`).

**CLOSES — PASS**

3. `check-drift.ps1`

The revision now says it remains out of scope because it has a separate explicit automation timeout, rather than claiming it cannot kill a review (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:719-722`). That matches the implementation: timeout leads to `Stop-Job` and `Remove-Job` (`tools/check-drift.ps1:1112-1115`).

**CLOSES — PASS**

4. Backup-lane pins

The Global Constraints now accurately state that `_norm` is whitespace-normalized and proves neither wrapping nor byte identity (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:24-25`). That matches the reader implementation (`evals/multi-model-verify/test_backup_lane.py:44-50`) and the normalized command assertions (`evals/multi-model-verify/test_backup_lane.py:123-148`).

**CLOSES — PASS**

5. Third Kimi call

The revised plan names the mandatory write-probe and its panel inheritance (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:434-440`). However, the linked design still asserts a complete four-command enumeration and omits the write-probe (`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:56-72`).

**DOES NOT CLOSE — FIX: revise the design’s enumeration to five long shell client calls—two Codex and three Kimi—and record each call’s disposition.**

6. Task 5 claimed Kimi detachment but implemented none

The false implementation claim is gone, but the replacement deferral is unsound. The linked design explicitly says the Kimi wrapper preserves the inline argument path and that backgrounding does not touch the 5.1 mangling (`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:190-195`). Item 51’s probe likewise defines the measured path as reading a brief and passing it inline through `-p <brief>` (`docs/superpowers/plans/rounds/2026-08-22-item51-inline-brief-probe/probe-record.md:27-39`).

Moving that same native call into a wrapper changes how the wrapper is started; it need not change the wrapper-to-Kimi argv path. Item 51 remains responsible for repairing that argv path, whose current 5.1 corruption is separately measured (`docs/superpowers/plans/rounds/2026-08-22-item51-inline-brief-probe/probe-record.md:91-118`).

**DOES NOT CLOSE — FIX: detach all three Kimi calls using the existing inline native invocation unchanged, while leaving item 51 responsible for repairing its known corruption.**

7. Quoting claim

The revised mechanism now says precisely that the wrapper removes the extra `Start-Process -ArgumentList` serialization boundary but remains subject to PowerShell parsing and native argv construction (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:248-256`).

**CLOSES — PASS**

8. “Only mechanism”

The region now calls `Start-Process` the selected mechanism and limits its `Start-Job` explanation to why that alternative fails under fresh-shell calls (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:239-245`).

**CLOSES — PASS**

9. Standard streams

All three streams are now redirected in the launch command, matching the cited precedent (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:397-400`, `tools/check-drift.ps1:923-927`).

A separate launch-completeness issue remains: no step creates or validates `<empty-file>`, and the new `<launch-out-file>` and `<launch-err-file>` are absent from the freshness inventory (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:20`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:397-400`). That belongs in finding 1’s control-path fix.

**CLOSES THE STREAM-INHERITANCE FINDING — PASS**

10. Timeout policy

The revision defines bounded polls, a thirty-minute `UNFINISHED` escalation, continue-or-abandon choices, and explicitly says neither choice is a review result (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:283-292`). The previous plan contradiction is gone.

**CLOSES — PASS**

11. Unverifiable harness facts

Both facts are now explicitly classified as harness-contract claims rather than repository evidence (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:26`).

**CLOSES — PASS**

## Question A: Kimi scope reduction

The deferral is not sound.

Item 51’s probe measured a local brief read followed by the inline native invocation `-p $b`; that is the documented transport shape (`docs/superpowers/plans/rounds/2026-08-22-item51-inline-brief-probe/probe-record.md:27-31`, `docs/superpowers/plans/rounds/2026-08-22-item51-inline-brief-probe/probe-record.md:57-73`). A Kimi wrapper can read a local data file and execute the same existing native command. The reviewer still receives the brief inline; it is not given a pointer and told to read a file, which is the behavior the backup contract forbids (`skills/multi-model-verify/references/backup-lane.md:37-46`, `skills/multi-model-verify/references/backup-lane.md:583-587`).

That preserves the current wrapper-to-Kimi argv behavior—including its known 5.1 defect. Detachment and repair are separable:

- Item 32 moves the unchanged native invocation into a detached wrapper.
- Item 51 later replaces the defective native argument construction with the measured `CommandLineToArgvW`-safe form (`docs/superpowers/plans/rounds/2026-08-22-item51-inline-brief-probe/probe-record.md:112-137`).

The linked design had already reached this conclusion (`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:190-195`). Closing item 32 while leaving all three Kimi calls foreground would also narrow the original backlog item, which expressly asked whether every long client call should be covered (`docs/superpowers/plans/2026-07-27-0150-backlog.md:2674-2681`).

**FIX — restore all three Kimi calls to item 32’s implementation scope while preserving their current inline native invocation; leave only the argument repair to item 51.**

## Question B: lane/round naming

The convention belongs in this cycle because detachment creates background tasks that need to remain identifiable, and Task 9 actually uses the convention for gates (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:674-692`). The wording is also honest that it is unenforced (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:293-297`).

It should not share the `detached-dispatch-operation` safety region. That region otherwise governs bounded polling, unfinished escalation, and whole-tree termination (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:283-293`). Co-locating an unenforced UI convention makes one normalized pin cover two different contract strengths and forces naming edits to reopen a completion-safety pin (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:322-326`).

**FIX — keep the convention in this cycle but move it to a separate `background-task-naming` region and name its test explicitly as a documentation-presence pin, not behavioral enforcement.**

## Parse-sensitivity disclosure

Task 8 is not sufficient yet. Step 1 executes a different synthetic sleep wrapper, while Step 3 spends a real round to discover whether the actual rendered wrapper parses (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:625-643`). It is also unclear whether Step 3 executes both fresh and resume templates.

Add a zero-quota step before any real dispatch:

- Render both fresh and resume wrappers with concrete scratch paths.
- Parse both with PowerShell’s parser on both hosts.
- Execute both against a native stub that exercises success, nonzero exit, and pre-client exception.
- Require the expected sidecar and no real Codex invocation.

The plan itself records that transcription already produced a parse error (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:404`), while the current tests only count raw strings (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:117-140`).

**FIX — add rendered parse and stub-execution checks for both wrapper forms before the real encoding round.**

## UNVERIFIED

- Actual survival across the harness boundary remains unverified until Task 8 Step 1 runs; the plan accurately labels it as unproven (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:614-629`).
- The Agent-tool background behavior and fresh-shell behavior remain external harness-contract facts rather than repo evidence (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:26`).
- Nothing enforces lane/round task names; the plan says so (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:293-297`).
- Item 51’s safe argv construction was measured against a Python stub, not the real Kimi client (`docs/superpowers/plans/rounds/2026-08-22-item51-inline-brief-probe/probe-record.md:29-39`, `docs/superpowers/plans/rounds/2026-08-22-item51-inline-brief-probe/probe-record.md:171-176`).
- Hook suppression is still planned rather than implemented; current code still runs `git add` and `git commit` without `core.hooksPath` isolation (`tools/new-review-mirror.ps1:1071-1089`).

## Sweeps

### (a) New false-completion path

Yes—the original stale-sidecar path remains reachable because the revised launch block never implements the promised pre-existence refusal (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:397-400`). Task 8 tests a refusal no task builds (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:631-637`).

I did not confirm a second independent false-clean path. I did find a separate unclassified state: fresh valid exit zero with no fresh reply. The revised contract omits it while asserting five exhaustive states (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:263-270`). The “only the last is a result” sentence prevents me from honestly calling that state clean, but leaving it unclassified violates the distinguishability requirement and risks inconsistent operators.

### (b) Revised failure-path distinguishability

- Wrapper parse failure: distinguishable. The process exits without a sidecar, which the contract calls a transport failure rather than running or complete (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:264-270`). Add the zero-quota parser test so this is caught before quota is spent.

- Pre-existing control path: not distinguishable as designed, because no refusal implementation exists. The launcher simply proceeds (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:397-400`).

- Thirty-minute escalation: distinguishable. It reports `UNFINISHED`, and both continue and abandon are expressly non-results (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:286-292`).

- Hook-suppression failure: distinguishable if Task 6 is implemented as written. It must exit `BLOCKED` rather than fall back to live hooks (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:497-499`), and mirror exit code 1 already means blocked (`tools/new-review-mirror.ps1:17-18`).