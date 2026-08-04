Round 2. Evidence rules, verdict grammar and the three project invariants as before.

The head has MOVED. Judge `02adc87..HEAD` at its current head, not the head round 1 read. A verdict is terminal only for the head it is issued on, so state the head you are judging.

Your round 1: claim 7 PASS, claims 1-6 and 8 FIX. Every finding was reproduced here and every one was accepted. Nothing was refuted. Amendment 2 is appended to `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md` and records all of it.

Confirm or refute each disposition.

1. **The contention window (your severest finding).** `Assert-OwnerLiveForWrite` now runs immediately before EVERY record write and requires LIVE; the pre-loop gate stays a fast DEAD-only refusal and is documented as a gate rather than the guarantee. UNMEASURABLE survives only on the non-writing idempotent re-entry path. The acceptance oracle became a refusal oracle, and `test_an_owner_that_dies_during_contention_is_never_written` reproduces your window synchronously - the holder is released only AFTER the proposed owner is killed and reaped. Both were watched failing first. The fixture docstring that still said "does not measure LIVE" is corrected.

   THE FIX CARRIED ITS OWN DEFECT and the new oracle caught it: refusing at the fresh-acquire write site left a ZERO-LENGTH lock file, which is MALFORMED by rule, so a refusal would have turned a free lane into one needing the guarded override. The refusal now writes the explicit free record first when that call created the file. Check that remedy specifically, and check that no OTHER refusal path added in this branch has the same obligation unmet.

2. **The task 2 deviation.** Accepted, and dispositioned by the user: the task is formally amended (Amendment 2), the claims are narrowed to what the oracle establishes - stability across an added SHELL frame, not "under any wrapper" - and item 26 is now PARTIALLY CLOSED with the unlisted-wrapper class named at its own heading. The allow-list was NOT built, because it cannot be validated against install shapes nobody here has seen and would refuse this repo's own harness. Is the narrowing now complete everywhere, or does some surface still claim general wrapper stability?

3. **Single-defect schema fixtures.** All six non-name stubs carry a valid `ownerName`. Reason-sensitivity was MEASURED, not asserted: removing the `-le 0` clause fails exactly `pid_zero` and `pid_negative`; removing the digits clause fails exactly `ticks_non_digit`. The template's two-field comment now describes three.

4. **Reparse points.** Never followed - not directory junctions, not symbolic links, not file links - and one encountered anywhere under the home makes the measurement INCOMPLETE, which takes the silence rule.

5. **The termination contradiction and the budget unit.** "Converged with amendments" is now explicitly AGREEMENT, NOT TERMINATION, and says the debate still ends on an adjudicated dry round. One budget unit is ONE DISPATCHED EXCHANGE, whatever it returns. Both are pinned, and a new pin covers the convergence clarification.

6. **The round-1 index entry** now reads "FIX; claims 1, 3, 4, 6, 7 and 8 require changes", matching the reply's own first line.

7. Your PASS stands unless the fixes above disturbed it.

8. **Stated limits.** The backlog status summary is corrected and says why it went stale. Item 26's heading says PARTIALLY CLOSED and names what stays open. Item 26's residual paragraph is rewritten: the earlier DEAD-only residual is GONE rather than restated, because the write-site rule removes it.

Gates, as MY report and not verified evidence: full `python -m pytest evals -q` 1089 passed / 14 skipped, and the seven PowerShell-facing modules under the second host. You could not run Python in round 1; if that is still true, list it UNVERIFIED again rather than folding it in.

Look hardest for a finding neither of us has made yet. Two reviews and two gates have now read this branch.
