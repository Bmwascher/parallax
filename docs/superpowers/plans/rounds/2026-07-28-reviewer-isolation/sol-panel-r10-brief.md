Panel round 10 (your round 18). New head: `881b676048208761f97f477ec86ce0585bf42ca2`.
Fix range: `6d5c25317086245b161b9c4520c20f5f0cbc9dcc..881b676`.
Branch base unchanged: `e2e9242c6153d69e9a4f0c49055e7bf8c81a1dd0`.

All three of your round-17 items are applied. I reproduced your finding
1 on both hosts before touching anything: 29 entries became 28,
`userskill5` gone, `Malformed` false, `Ambiguous` false, nothing in the
report to say a skill had been removed.

## What was applied

**Your finding 1.** The blanked text now LOCATES the span and nothing
else. `$body` is sliced from `$text` at the located offsets, exactly as
you specified. The new case plants a `<permissions instructions>` pair
inside the skills body around a real entry, with the genuine permissions
container removed from the render first so the count rule does not fire,
and asserts all 29 entries plus `userskill5` by name.

**Your finding 2.** `Ambiguous` is kept and made total. Any shape that is
not `0/0` and not an ordered `1/1` sets it, so a close-only render now
reports `Ambiguous` true with `OpenCount` 0 and `CloseCount` 1. The
caller's presence check still runs first, so a close-only render stops
with the missing-block message; the published field is now consistent
with the rule the function states about itself.

**Your finding 3.** The comment says one production call site and two
checks on its result.

**From the other lane.** It returned PASS with no findings on the same
head and read the very line you found as correct. Its one wording
non-finding is applied: the ambiguity message said the counts were taken
"once every other known container's body was blanked", which is untrue
when the blanking loop itself threw, so it now says "as far as they
could be blanked".

## Your task this round

1. Verify each change at the code.
2. **Attack the raw slice.** The offsets come from one string and the
   content from another, and the whole thing rests on the replacement
   being length-preserving. What input makes those two disagree? Is there
   any path where `$closeAt` or `$bodyStart` indexes past the end of
   `$text`, or lands mid-entry?
3. Does making `Ambiguous` total change any outcome you did not expect?
   The caller order is presence, then ambiguity, then empty entries.
4. Four rounds running, the fix for one round has carried the next
   round's defect, always in the same function. Is there a structural
   reason to stop trusting this design, or is that just what a strict
   parser costs?
5. Terminal verdict against head `881b676`.

## Evidence (verify, do not trust)

- Both hosts: 445 passed / 1 skipped.
- Live probe both hosts: exit 0, clean, 29 -> 0, override sha256
  `180f09f50d282b5603f1c0d0621f2913ff66c8b7798e7a2f3b7fe8d41f432bb8`.
  Unchanged through every round of this cycle.
- Both new cases were run against the reverted script first and both
  failed there.

Say plainly if you find nothing. Cite `path:line`. Anything you did not
check goes under `## Unverified`.
