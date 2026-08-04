Round 4. Rules and invariants as before. The head has MOVED; state the head you judge.

Your round 3: claims 3, 4, 5, 6 and 7 PASS; claims 1, 2 and 8 FIX. All three accepted, none refuted. Amendment 4 records them.

1. **The three surviving surfaces.** All corrected:
   - The GATE comment inside `Invoke-AcquireMode` now says "before every HELD-OWNER write and establishes LIVE there. Not 'every record write': the free-record writes carry no owner."
   - Amendment 2's "IMMEDIATELY BEFORE EVERY RECORD WRITE" is corrected IN PLACE with a pointer to Amendment 4, not rewritten.
   - The unmeasured "microseconds" magnitude is GONE. The residual now states the comparison that is known (the old window spanned the whole wait budget, this one spans a few statements) and says explicitly that its wall-clock duration is NOT measured and is not bounded by that statement count, because the scheduler can pause the process anywhere inside it.
   - The victim is reaped in `finally`, so a signal timeout or a failed branch assertion can no longer leak a 120-second sleeper. Amendment 4 records that this defect was introduced BY the round-2 rewrite that fixed the synchronization defect.

2. **The contradicted exception.** "So run" is now "OTHERWISE, run", and the whole-region pin was regenerated against the new text.

3-7. Your PASSes stand unless the above disturbed them.

8. Amendment 4 records all four corrections, including that the narrowing had landed on one surface out of three and that a fix introduced its own defect for the sixth time in this repo.

Gates, MY report not verified evidence: full suite and the second PowerShell host on the seven PowerShell-facing modules, both at this head.

This is the fourth round of a chain in which every round has found something real and nothing has been contested. Under this branch's own new rule the debate ends only on an adjudicated dry round - no new substantive finding AND no outstanding contested point - so a PASS here is what ends it. If you find nothing, say PASS and say it is terminal for the head you judged. If you find something, say it.
