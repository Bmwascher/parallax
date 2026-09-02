# Verdict: ESCALATE

I would not merge this head. The core completion-coupled exit path is materially sound in the ordinary case, but the frozen plan is not eligible for an ordinary diff verdict, and there are two implementation drifts plus an unrecorded false-success surface.

## Blocking findings

1. The plan does not substantively qualify as `FULL`

This is more than a missing label.

The required format says every frozen plan must contain a structured debate record and that a plan without it “was not verified” and must be treated as an unfrozen draft: `skills/multi-model-verify/references/frozen-plan-format.md:43-58,120-122`.

The plan has extensive review history, but its final text expressly says that version was not reviewed: `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:2459-2462`. Its own tally also says six rounds across two lanes despite eight review sections across Sol, Fable, and Kimi: `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:2168-2450,2452-2457`.

Therefore:

- The substance is strong evidence of review, but not `Verification status: FULL`.
- The missing field cannot be inferred or papered over.
- Its absence blocks an ordinary PASS. The final plan revision needs retrospective cross-vendor verification and a proper record before implementation fidelity can be attested.

2. `body.ps1` can be changed after preparation and manufacture exit-zero success

`-Prepare` copies the body into the dispatch directory at `tools/dispatch-round.ps1:526-530`. The receipt seals the prior state and mirror identity, but contains no body digest: `tools/dispatch-round.ps1:537-555`. The wrapper later executes whatever bytes are then present at `body.ps1`: `tools/dispatch-round.ps1:289-293`.

A caller can therefore replace `body.ps1` after preparation with one that writes an expected `workdir:` transcript, a non-empty reply, and exits zero. The untouched wrapper then passes both mirror verifications and reaches `reply-present`.

The documented residual admits that `wrapper.ps1` is mutable, but not the adjacent body or other invoked dependencies: `skills/multi-model-verify/references/model-prompting-notes.md:370-383`. This is not a new threat boundary—the filesystem owner is already trusted—but the claimed five-residual inventory is incomplete. At minimum it must name `body.ps1`; sealing it would require reopening the design.

3. Task 10 was recorded honestly but not completed as frozen

The frozen task requires observing the no-window behavior and repeating items 1–5 under both hosts: `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1924-1937`.

The record says:

- Conversation openness was observed only for Sol R1/PowerShell 5.1: `benefit-measurement.md:55-60`.
- The screen/no-window requirement was not observed at all: `benefit-measurement.md:66-68`.
- It nevertheless concludes “Both hosts. Done”: `benefit-measurement.md:69`.

Writing “not observed” satisfies the record’s honesty rule, but it does not satisfy the task’s required measurement. The no-window probe and conversation-open observation on the second host remain outstanding.

4. Task 5’s “identical semantics” drifted between binders

The frozen plan requires identical seal semantics in both lanes: `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1473-1476,1512-1519`.

Codex verifies the raw-byte seal before parsing the prior state: `tools/read-codex-round-evidence.ps1:559-583`, with parsing beginning at line 585.

Kimi parses first at `tools/read-kimi-round-evidence.ps1:763-764`, then checks the seal at lines 766-786. Consequently, an invalid post-dispatch mutation is classified as prior-state malformed in Kimi before the promised seal comparison occurs, while Codex reports `sealed-state-mismatch`. It remains fail-closed, but it is not the identical cross-lane behavior the plan froze.

## Task-by-task fidelity

- Tasks 1, 1a, 2, 3, 4, 6, 7, 8 and 11 materially match their planned shipped surfaces.
- Task 5 drifts as described above.
- Task 9 achieved the body-budget extraction, although its planned `test_multi_model_verify.py` edit was not made by `e60fce0`; the relevant region remained in `SKILL.md`, so I found no resulting coverage hole.
- Task 10 is incomplete.
- Task 7’s Kimi cwd outcome is not drift. The plan ordered an escalation if Kimi supplied no cwd evidence, and the record says that happened and the user accepted shipping the recorded gap: `benefit-measurement.md:124-139`. The shipped lane states that limitation plainly at `skills/multi-model-verify/references/backup-lane.md:121-137`.

## Required four-class sweep

Base rate assumed: five prior whole-branch rounds, with the user-supplied empirical prior that all four classes occurred. I did not use a clean-sheet prior.

1. Documented control that controls nothing — INSTANCE

The background-task naming rule is documentation-only. The contract explicitly says nothing enforces it, while the tool merely prints a suggested name: `skills/multi-model-verify/references/model-prompting-notes.md:431-441`; `tools/dispatch-round.ps1:585-594`.

This is honest and known, not a newly hidden defect.

2. Measurement claim broader than its evidence — INSTANCE

`benefit-measurement.md:37,69` calls the success path complete on both hosts, while the open-conversation observation covers only one host and the no-window observation was not made: `benefit-measurement.md:57-68`.

The plan’s “six rounds across two lanes” claim is also narrower/different from its own eight named review sections: `completion-coupled-dispatch.md:2168-2457`.

3. Fix applied to some instances but not all — INSTANCE

Post-prepare mutation protection covers the receipt at `tools/dispatch-round.ps1:716-721`, but not the installed `body.ps1` at lines 529-530 and 291. Wrapper mutation is documented; body mutation is neither sealed nor included in that residual.

4. Guard cannot see the written form — INSTANCE

The citation resolver explicitly cannot inspect files outside `DOC_PATHS`: `evals/multi-model-verify/test_contract_coverage.py:863-877`. The backlog contains an actual `model-prompting-notes.md's round-dispatch-operation` citation outside that scope at `docs/superpowers/plans/2026-07-27-0150-backlog.md:4909-4910`.

The pointer is currently valid, but the guard cannot detect it becoming dangling.

## Exit-code design attack

For the unmodified, correctly correlated wrapper path, I found no natural internal failure that returns zero. The fixed state order is implemented at `tools/dispatch-round.ps1:653-813`, and only `reply-present` reaches exit 0.

Success can still be unearned through:

- Post-prepare mutation of `body.ps1`, described above.
- Editing `wrapper.ps1`, already admitted at `model-prompting-notes.md:377-381`.
- Reading the runtime nonce and invoking standalone `-Classify`, admitted at lines 370-376.
- Mirror changes hidden from Git status, or mutation followed by reversion before the second check, admitted at lines 362-369 and 383-389.
- Kimi rounds bypass states 9–11 through `-NoWorkdirEvidence`; the lane expressly cannot confirm cwd from client evidence: `backup-lane.md:121-137,156-177`.
- Mis-correlating harness tasks. The exact task ID rule remains procedural, and task names are not enforced or unique across debates.
- Treating exit 0 as a review verdict without the evidence binder. The contract correctly says it means only “reply present”: `model-prompting-notes.md:358-360,398-406`.

## The two unreviewed commits

- `ad62961` is a defensible correction. It removes the invalid `-MirrorPath` claim and adds the missing section bound. The retained `##`-only limitation is explicit, and I found no current `###` instance after the affected last call sites.
- `e297ae5` is documentation-only, but its new artifact says `ad62961` is “the only commit no Fable round has seen” at `fable-whole-branch-review-rounds-2-5.md:25`. At head, `e297ae5` itself is also unreviewed. The wording needs a temporal qualification such as “before this artifact commit.”

## Merge floor

I would merge only after:

1. Reopening and verifying the final frozen-plan revision, then recording a real status rather than inferring `FULL`.
2. Aligning Kimi’s seal check ordering with Codex and adding the malformed-post-seal regression case to both binders.
3. Completing Task 10’s missing no-window and second-host conversation observations.
4. Either sealing `body.ps1` or explicitly adding body/dependency mutation to the accepted filesystem-owner residual.
5. Correcting the `e297ae5` self-excluding review-history sentence.

I would knowingly ship the user-accepted Kimi cwd-evidence gap, nonce/standalone-classifier residual, filesystem change-and-revert gap, Git-clean hidden-byte gap, unenforced naming, unpinned harness trailer, and unbounded hung-round wait—because those are stated limits.

Validation note: the five changed PowerShell scripts parse cleanly under PowerShell 7. The focused pytest run could not execute because this review sandbox denied launching the external Python interpreter; I therefore treat current test status as unverified, not failed.

**ESCALATE — frozen-plan verification status absent and final plan revision expressly unreviewed.**