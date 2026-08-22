The live-count fix succeeded narrowly—no `7500`-as-current claim survives—but the structural claim is still wider than the document and code beneath it.

1. Ninth instance: the new convention calls `0 files not scanned` an exit-code invariant. [The record says exit `0` guarantees all three zeroes](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:620), but [`survey.py` ignores `skipped` in its exit predicate](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/survey.py:348). An unreadable or binary file can produce `1 files not scanned` and exit `0`. This is the defect class again, inside the structural fix.

2. The “every absolute count is commit-bound or invariant” claim still has uncovered self-referential figures. Examples:

   - [“83 rows, grouped into 50 bullets,” plus 3 unknown rows](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:737) is neither commit-bound nor guaranteed by the survey.
   - [“34 bulleted entries across 7 buckets”](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:488) is a live count of this mutable record.
   - [“currently no unread file”](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:194) is an unbound current-tree claim.

   All are true at this head, but the claimed structural rule does not cover them. Either bind these figures or narrow the convention’s scope.

3. The `_MISSING` code fix is correct, but it shifted existing `run.py` citations. Fresh sample: **20 cited targets/endpoints checked; 16 landed, 4 failed**, all in `run.py`:

   - [The record cites `run.py:63` and `:112` as the two target-host pins](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:1158); those lines are now `p.unlink()`. The pins moved to `:69` and `:118`.
   - [Two sentences cite `run.py:164-166`](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:1078), but the actual comparison is now [lines 175–180](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/reexec/run.py:175).
   - [`run.py:201-204` is cited as evidence that positional child data is not retained](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:1151), but those lines are the broken-arm check. The relevant returned fields are at `:79-91`. This citation was already wrong before the fix.

4. Finding 6 was disclosed, not fixed against the frozen plan. [The plan requires every `must-change` row “one line each”](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md:813). The record still has 83 rows represented by 50 bullets and now explicitly admits the mismatch. That repairs the overclaim, but frozen-plan fidelity still fails unless the rows are split or a controller override is formally accepted.

5. Finding 7b is only partially fixed. [The comment says reviewers produced nine live misses and “Nobody has produced a tenth”](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/survey.py:51), then immediately says [a second deliberate miss was found later](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/survey.py:67). “Nine corrections/widenings” could be true; “nine live misses” is not. The earlier sentence needs that narrower wording.

Verified clean:

- The live scan is now 5589/1340/571 = 7500, and the record does not publish it as current.
- Every row count in the commit-bound table matches the corresponding Git object.
- Current TSV: 1117 rows, published 612/227/106/54/46/31/15/13/7/5/1 classification split, 83 `must-change`, 3 `unknown`.
- Guard comment now matches its case-sensitive suffix/exact-path implementation; none of the named uncovered extensions exists under `docs/`.
- `_MISSING` correctly distinguishes absent from explicit `null`; `results.json` and `child-named.ps1` are untouched.
- The `skill-evals.yml:74` correction, Ruling 10 cost correction, and Measurement 3 summary correction all land.
- Residual buckets remain 8/5/3/4/4/6/4 = 34.
- The five-condition CONDITIONAL verdict remains sound.

FIX