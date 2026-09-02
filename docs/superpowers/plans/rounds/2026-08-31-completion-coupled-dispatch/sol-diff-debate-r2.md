The final plan revision does not earn `FULL`. My honest status is:

- `Verification status: DEGRADED`
- `Degradation: final-revision-fix-outstanding`
- `Authorized by: not-authorized`

The branch verdict is `FIX`.

## Findings

1. The post-round-8 correction is directionally sound but incomplete.

Round 8 found that post-construction review inputs would invalidate the newly minted mirror digest (`completion-coupled-dispatch.md:2436-2440`). The correction:

- Added repeatable build-time `-ExtraInput`.
- Required copying before the baseline and manifest.
- Rejected any re-mint/reseal facility.
- Expanded Task 1a’s affected-file list (`completion-coupled-dispatch.md:567-599`, `:2112-2121`).

Choosing rebuild-over-remint is sound: re-minting would bless an already-mutated tree.

The open defect is collision semantics. The plan promises to copy and list “each named file” (`completion-coupled-dispatch.md:592-596`), but the implementation flattens every input to its leaf name and overwrites with `-Force` (`tools/new-review-mirror.ps1:1283-1285`). Therefore:

- Two external inputs named `standards.md` silently collapse to the last one.
- An external `standards.md` can overwrite an existing mirror-root file.
- The record shows one destination and cannot demonstrate that every requested input arrived.

The only positive test uses one non-colliding file (`evals/multi-model-verify/test_review_mirror.py:1874-1888`). This violates the zero-judgment rule at `frozen-plan-format.md:3-7`.

The smallest sound resolution is to require case-insensitive destination uniqueness and refuse any destination already present in the copied mirror, with tests for both cases.

2. The reported seal-ordering case is fixed, but Task 5’s broader identical-semantics requirement remains unmet.

Confirmed:

- Kimi now reads and hashes the raw bytes before parsing at `tools/read-kimi-round-evidence.ps1:774-790`.
- Codex hashes before parsing at `tools/read-codex-round-evidence.ps1:570-596`.
- Both new tests exercise tampered plus invalid JSON (`test_kimi_round_evidence.py:2101-2121`, `test_codex_round_evidence.py:2162-2178`).

But Task 5 promises “identical semantics and identical failure text” (`completion-coupled-dispatch.md:1473-1477`). With a seal supplied and the prior-state file missing:

- Codex returns `prior state file not found` before entering the seal block (`read-codex-round-evidence.ps1:559-560`).
- Kimi enters the seal block and returns `prior-state-unusable: could not read -PriorState` (`read-kimi-round-evidence.ps1:774-780`).

Unreadable-file failures similarly differ (`read-codex-round-evidence.ps1:572-576`). The fix closed the invalid-JSON instance, not the whole sealed-input failure class.

3. Two documentation repairs reproduce their target class.

The benefit record now accurately says Task 10 is incomplete (`benefit-measurement.md:39-41`, `:73-78`), but its closing summary still says “The success path was measured on both hosts” (`:150-158`). That needs narrowing to “successful wrapper executions ran on both hosts”; the complete Task 10 success-path observation did not.

The Fable record now says, “As of the commit that ADDED this file, `ad62961` was the only commit” unseen, immediately followed by the admission that the adding commit was unseen too (`fable-whole-branch-review-rounds-2-5.md:25-30`). The correction should say “Immediately before the commit that added this file.”

These are recurrences inside the round-1 repair wave. I found no new exit-code false-success mechanism in that range.

4. One existing measurement citation is stale.

`backup-lane.md:60-66` cites `tools/new-review-mirror.ps1:57-75` as the IBM437 measurement, but those lines are parameter declarations (`new-review-mirror.ps1:57-75`). The relevant discussion is now at `new-review-mirror.ps1:81-99`. The claim may be true, but its named evidence currently supports something different.

## Four-class sweep

I used the prescribed base rate: 5/5 prior rounds, or 100%, so I did not assume a clean sheet.

- Documented control that controls nothing: PRESENT, knowingly carried. Background-task naming is explicitly unenforced; `-Prepare` only prints a suggestion (`model-prompting-notes.md:435-445`, `dispatch-round.ps1:586-602`).

- Measurement claim broader/different than its evidence: PRESENT. The Task 10 closing summary overstates its own itemized result (`benefit-measurement.md:73-78`, `:150-158`). The stale IBM437 citation is a second instance.

- Fix applied to some instances but not all: PRESENT. Seal-before-parse is fixed for tampered invalid JSON, but missing and unreadable sealed state still differ across binders.

- Guard cannot see the written form: PRESENT, knowingly carried. `DOC_PATHS` covers only `skills`, `agents`, and `commands` (`test_contract_coverage.py:611-615`); the guard itself admits it cannot see citations outside that set (`:863-877`), while the backlog contains such a citation (`2026-07-27-0150-backlog.md:4909-4910`).

## Body sealing

Not sealing `body.ps1` is a defensible call under the stated filesystem-owner threat boundary. The receipt schema has no body digest (`dispatch-round.ps1:196-201`, `:537-555`), and the shipped residual now states that honestly (`model-prompting-notes.md:374-385`).

A body digest checked only by the equally editable wrapper would not stop a deliberate filesystem owner. Properly binding both scripts would require an independent immutable launcher boundary, so it genuinely reopens the design. I would knowingly ship this residual.

## Merge floor

I would not merge `c05b5d3`. My floor is:

1. Settle and test `-ExtraInput` collision behavior in the plan and implementation.
2. Make sealed missing/unreadable prior-state behavior identical across binders.
3. Correct the Task 10 closing summary, the self-quoting Fable sentence, and the stale IBM437 citation.
4. Record the current round’s PowerShell 7 responsiveness and screen observation honestly; those remain unverified by me.
5. Re-review the resulting exact plan revision, append its debate record, and replace the current “This version has not been reviewed” statement (`completion-coupled-dispatch.md:2462-2465`).

I did not execute the test suite. Your reported test counts remain your measurement. I verified the current clean head and ran `git diff --check e297ae5..c05b5d3`, which was clean.

**FIX**