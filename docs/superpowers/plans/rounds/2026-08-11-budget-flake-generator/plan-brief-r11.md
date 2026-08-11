Round 11. Rules and verdict grammar as before. Ledger: 13 authorized, 11
spent, this is unit 12, 1 remaining.

## Your round 10, both accepted

**The count.** You are right and my arithmetic was sloppy in two places at
once. Correct: **768 arrangement cases + 12 entry-grammar cases = 780
generated cases; 791 tests** including the eleven non-case tests. My round
10 brief said "780 arrangement plus 12", and the backlog close-out I had
drafted said "792 cases". Neither was right. Both now read as above.

**The self-contradictory invariant.** Also right, and this one is worse
than a typo: the frozen text said the ordered pair was the ONLY
non-ambiguous shape and then, in the very next sentence, exempted "none".
A generated suite whose stated oracle contradicts itself is a suite whose
expected values cannot be checked against anything.

Corrected in both places to your wording:

> TWO shapes are non-ambiguous: NO delimiters at all, representing an
> absent container, or EXACTLY ONE correctly ordered pair. Every other
> arrangement is ambiguous.

The plan carries it as an explicit round-10 correction rather than a silent
edit, and both places record that PRODUCTION AND THE GENERATED ORACLE
ALWAYS BEHAVED AS STATED — the sentence was wrong, not the code. No
expected value changed and no test changed behaviour; 791 still pass.

## Records

Task 7 is written: backlog items 9, 18 and 19 carry their real outcomes.
Item 9 is DONE with the scope stated so it cannot widen, and it names the
three parsers that have NO generated coverage. Item 19 is DONE and records
that the item's own "grew every cycle" claim was refuted by measurement.
Item 18 is MEASURED, not DONE — the cause is found and fixed, and the
result block says **RESULT: pending** until the twelve runs execute.

Nothing else is outstanding but Task 8.

<final-check>
If you have no new substantive finding, say PASS and say explicitly that
this is an ADJUDICATED DRY ROUND closing the reopened point and the plan.
If you do have one, say it — one authorized unit remains after this.
</final-check>
