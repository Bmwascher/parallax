The Task 5 answer is: keep the lane-specific file-error vocabulary. The frozen requirement does not require rewriting Kimi’s nine established `prior-state-unusable` assertions.

## Task 5 decision

The broad interface sentence says identical semantics and failure text (`completion-coupled-dispatch.md:1473-1477`), but the operative steps define that parity specifically as:

- Raw-byte, case-insensitive seal comparison.
- `sealed-state-mismatch` for a digest mismatch.
- `sealed: "not-checked"` when omitted.
- The same three tests in each binder (`completion-coupled-dispatch.md:1480-1519`).

Those seal outcomes are identical in the implementation (`read-codex-round-evidence.ps1:570-582`, `read-kimi-round-evidence.ps1:774-786`). Missing or unreadable bytes are pre-existing lane-level `-PriorState` acquisition failures, not evidence that a seal comparison mismatched.

My round-2 interpretation was too broad. Record this as:

> Task 5 parity applies to the `-SealedPriorStateSha256` outcomes enumerated in Steps 1, 3, and 4: raw-byte comparison, `sealed-state-mismatch`, and `sealed: not-checked`. When prior-state bytes exist, seal comparison precedes JSON parsing. Missing or unreadable `-PriorState` retains each binder’s established file-error vocabulary; both lanes fail before parsing, and neither claims that a seal comparison occurred.

That is a resolved interpretation, not an escalation. Merge-floor item 2 is closed without changing Kimi’s vocabulary.

## Current findings

1. The collision mechanism and tests are closed.

The tool now preflights all destinations before copying (`new-review-mirror.ps1:1283-1316`). The tests discriminate against the former behavior by asserting specific refusal text and unchanged contents (`test_review_mirror.py:1891-1932`).

The first test draft was indeed class 3: its generic exit-1 assertion passed on the unrelated terminal `-SkipProbe` refusal. The corrected test records that exact failure (`test_review_mirror.py:1908-1914`). I count the recurrence against the repair, but it is no longer active.

2. The frozen plan still does not structurally settle the collision decision.

Task 1a still says only that every input is copied (`completion-coupled-dispatch.md:592-599`). It does not say duplicate leaf names or existing destinations must be refused. The appendix describes the implemented result (`:2498-2505`), but omits the required `### Resolved points` table through which the debate record records accepted amendments. The required appendix shape includes both Resolved and Escalated tables (`frozen-plan-format.md:43-69`).

Add the refusal semantics to Task 1a and record the decision as a resolved point.

3. The appendix overstates raw-round retention and carries a stale degradation class.

`Raw rounds` says the directory contains “the diff debate’s own rounds” (`completion-coupled-dispatch.md:2481-2483`). Directory enumeration shows only the earlier plan reviews and existing behavioral artifacts—no retained round-1/round-2 diff replies. Either retain them or say the diff rounds were not retained, as required by `frozen-plan-format.md:77-84`.

`final-revision-fix-outstanding` at `completion-coupled-dispatch.md:2479` is now stale: the same appendix says the fix is applied at `:2504-2505`. Keep `DEGRADED`, but rename the class to something historical and currently true, such as `final-revision-reviewed-late`. That is not an upgrade.

4. Task 10 still has one unverified cell.

The current record correctly says D5 is observed on PowerShell 7 but not 5.1 (`benefit-measurement.md:73-89`, `:174`). I cannot observe the user’s screen. If the user reports no window during this round, record that attribution and close the cell. If a window appeared, invariant D5 failed and must be escalated.

## Four-class sweep

Using the same high 5/5 prior:

- Control that controls nothing: PRESENT, knowingly carried—task naming remains an admitted convention (`model-prompting-notes.md:435-445`).
- Measurement/evidence mismatch: PRESENT—the appendix claims unretained diff rounds are in its directory (`completion-coupled-dispatch.md:2481-2483`).
- Partial class fix: PRESENT—the runtime collision fix was not added to Task 1a or the required resolved-points record. The vacuous first test draft was another instance, now corrected.
- Guard blind to written form: PRESENT, knowingly carried—`DOC_PATHS` excludes docs (`test_contract_coverage.py:611-615`), and the guard records that limit (`:863-877`).

No new exit-code false-success path appeared in `c05b5d3..02c6eab`.

## Degraded-plan gate

Yes: the substantive retrospective condition is met. Round 2 reopened the final plan, found the collision defect, and round 3 has now verified the correction and resolved the Task 5 interpretation. That satisfies the reopening required by `SKILL.md:359-363`; it allows an eventual ordinary diff PASS without changing the historical plan status to `FULL`.

## Round-2 merge floor

1. ExtraInput collision: implementation/tests closed; plan record still open.
2. Binder parity: closed by the scoped interpretation above.
3. Three wording/citation corrections: closed (`benefit-measurement.md:167-174`; `fable-whole-branch-review-rounds-2-5.md:25-30`; `backup-lane.md:60-65`).
4. Task 10: open pending the PowerShell 5.1 screen observation.
5. Exact-revision re-review/appendix: substantive re-review closed; appendix shape, degradation class, and raw-round statement still need correction.

I verified the clean `02c6eab` tree and a clean `git diff --check`. I did not run tests; the 105-test result remains your measurement.

**FIX**