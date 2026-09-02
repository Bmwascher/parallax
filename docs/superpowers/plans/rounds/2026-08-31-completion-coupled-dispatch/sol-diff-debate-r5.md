`16e8d46` is still `FIX`. The executable implementation is at an honest floor, but the required debate record remains false in two places. I would block merging on those because this appendix is the evidence gate, not ordinary commentary.

## Remaining blockers

1. The count-free replacement violates the required format and is already stale.

The format requires `Rounds used: N of CAP` (`frozen-plan-format.md:52-58`). Removing the count is not an invariant-preserving substitute.

More importantly, the new claim says every diff round is retained below (`completion-coupled-dispatch.md:2486-2492`), while Raw rounds ends at `sol-diff-debate-r3` (`:2504-2505`). Round 4 happened and is the review this commit addresses, but neither its reply nor binding is retained.

Use a bound record, for example:

> **Rounds used:** Plan: 8 rounds. Diff: R1–R4 completed and retained; R2–R3 were retrospective verification, R4 confirming. Contested counter: 0 of 4.

Then retain R4. A terminal record is expected to be updated at its terminal boundary; avoiding that update by deleting the required count merely moves the staleness into the prose and raw list.

The sentence at `completion-coupled-dispatch.md:2490-2492` also ends unfinished: “the rounds after that confirm and correct”. Complete or remove it.

2. Resolved point 5 still carries the old ordering overclaim.

Task 1a is now accurate: collision checks occur after tree copy/remediation and before any extra input is copied (`completion-coupled-dispatch.md:594-605`).

But the resolved-point row still says “both collisions refused before any copy” (`:2539`). Change it to “before any `-ExtraInput` copy.” This is the same partial-fix class, one table row away.

## What is closed

- Task 10 is closed in the record. Its heading and itemized result now agree (`benefit-measurement.md:37-43`, `:75-93`). The human screen observations remain externally unverified by me, but attribution is honest.
- Raw-round binding scope is now accurate for Sol versus Fable/Kimi (`completion-coupled-dispatch.md:2497-2503`).
- Task 1a’s operative collision semantics are accurate.
- Task 5’s scoped interpretation remains closed.
- The degraded-plan reopening condition remains met.
- I found no new executable false-success path.

Your two self-caught drafts count as repair-wave class-3 instances. This wave also reproduced the class in the count-free rounds claim and resolved-point row.

## Merge floor and residuals

The substantive round-2 merge floor is closed. Only the required record corrections above block this exact head.

After those corrections, I would knowingly ship the same residual floor as round 4:

- `DEGRADED / final-revision-reviewed-late`.
- Kimi has no client-reported cwd evidence (`backup-lane.md:121-137`, `:156-177`).
- `wrapper.ps1` and `body.ps1` remain mutable by the trusted filesystem owner; the runtime nonce can also be read (`model-prompting-notes.md:370-387`).
- Git-clean hidden-byte changes and change-then-revert mutations remain invisible (`model-prompting-notes.md:362-369`, `:387-393`).
- Harness trailer format is version-measured, not pinned; hung rounds have no bound (`model-prompting-notes.md:393-400`).
- Task naming and citations outside `DOC_PATHS` remain unenforced.
- FAIL/KILL behavior was measured on one interpreter only (`benefit-measurement.md:164-176`).

Nothing is added to or removed from that residual list at this head.

I verified the clean `16e8d46` head and clean `git diff --check`. The reported two-host suites and fast gates remain your measurement, unverified by me.

**FIX**