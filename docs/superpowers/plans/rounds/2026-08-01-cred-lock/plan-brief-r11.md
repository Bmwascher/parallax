Round 11. Cap still lifted; iterate to PASS. Evidence rules and verdict grammar as before.

Plan r10 is written. Only Task 7 changed; the other nine tasks are byte-unchanged
from what you passed in round 10.

ACCEPTED, all three, no reservation.

1. CLEANUP COVERAGE AND PRECEDENCE now span every phase inside custody. The MAIN
   OPERATION is defined explicitly as the pre-command phase, the command and its
   capture, the post-command re-read and merge, and the stream guard, with the
   note that naming only the command left three phases where a runner could skip
   `-Remove` or let a removal failure mask the real one. A failure in ANY main
   phase still runs the real `-Remove`, asserting the home absent and the lock
   exactly `free`. Precedence: any main-phase failure stays primary even when
   `-Remove` also fails; `-Remove` is primary only when every main phase
   succeeded. The same rule is stated for seeding. The support oracles now carry
   three combined cases - pre-command plus Remove failure, merge plus Remove
   failure, guard plus Remove failure - each also asserting `-Remove` actually
   ran, alongside the opposite-direction case and the two seed cases.

2. THE THREE EXCEPTION PATHS now have oracles, and you were right that nothing
   reached them: a fake command that emits a fake credential value and then blocks
   until TIMEOUT must fail naming only the field, carry neither the value nor the
   captured stream, write no probe record, and still clean up through `-Remove`; a
   NONEXISTENT EXECUTABLE must produce a sanitized launch failure and still clean
   up; and a post-command credential read-or-parse FAULT must produce a value-free
   failure and still clean up.

3. ITEM 6's wording conflict is resolved. The post-command re-read rule is now
   scoped to A, B and C, the builder-custodied homes, and item 6's disposable
   homes are stated separately: re-read and merged after their command WITHOUT a
   lock, because they never had a hold to keep in force, with the same stream
   guard running over their output unchanged.

PLAN RECORD: revision 10, r10 history entry, ten rounds.

Same two questions:

1. PASS, if a zero-judgment implementer could now build this without inventing
   anything; or the precise remaining FIXes, each marked BLOCKING or
   acceptable-as-is.
2. Has any round-10 fix been applied wrongly or introduced a new defect?

One process observation, offered as evidence rather than argument. Rounds 8, 9 and
10 each found exactly one class of defect, each time inside the text the previous
round had just rewritten, and each time it was a coverage gap rather than a wrong
decision. That pattern is consistent with a specification converging, but it is
also consistent with one that keeps growing new surface faster than it is tested.
If you judge it to be the second, say so plainly and name what you would CUT
rather than add, because a plan too large to hold in one head is its own defect
and I would rather hear that from you than discover it during the build.
