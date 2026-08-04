# 0.22.0 debate round records (lane release and round cap)

Retained at the branch that made retention a task. Backlog item 24 was
closed here partly on the claim that a flat round cap of four would have
stopped earlier debates before their last real defects, and a reviewer
who was not in the session could not check that claim against anything.
These are the replies themselves.

## Plan debate (1 round)

| Round | File | Verdict as the reply states it |
| --- | --- | --- |
| 1 | `plan-reply-r1.md` | Claim 4 PASS; claims 1, 2, 3, 5, 6, 7 FIX |

That round is Amendment 1: it DELETED a planned task whose premise was
false and ADDED the task that became this branch's strongest change.

## Diff debate (6 rounds)

| Round | File | Verdict as the reply states it |
| --- | --- | --- |
| 1 | `diff-reply-r1.md` | FIX; claim 7 PASS, claims 1-6 and 8 FIX |
| 2 | `diff-reply-r2.md` | FIX; claims 6 and 7 PASS (`ad61503e5814`) |
| 3 | `diff-reply-r3.md` | FIX; claims 3-7 PASS (`6565ca0d2cbc`) |
| 4 | `diff-reply-r4.md` | FIX; claims 2-7 PASS (`71617056b62e`) |
| 5 | `diff-reply-r5.md` | FIX; claims 2-7 PASS (`685811283f34`) |
| 6 | `diff-reply-r6.md` | **TERMINAL PASS** (`592c69c9b899`), dry round |

## What these establish, and it is the point of retaining them

**Every one of six rounds found something real, and NOT ONE point was
contested.** That is the regime backlog item 24 says a flat cap of four
exchanges measures wrongly, and here it is happening in the branch that
fixed the cap. Rounds 5 and 6 of the count would have been unreachable:
round 5 found that a correction contradicted itself, and round 6 was the
dry round that ended the debate.

The chain is also a record of claims wider than their evidence, all of
them mine:

- Round 1: liveness was measured once before a wait loop, so an owner
  could die during contention and still be written. A whole-branch Fable
  review returned no Critical and no Important on that same code.
- Round 2: the oracle written to prove round 1's fix slept two seconds
  instead of synchronizing, so it could go green for a gate it was not
  testing. The same round found a pin I had claimed existed and did not.
- Round 3: the narrowed guarantee had landed on one surface out of
  three, and "microseconds" was a number I never measured.
- Round 4: the replacement for "microseconds" was itself an unmeasured
  comparison.
- Round 5: the tool was corrected but the amendment that made the claim
  was not, and its own correction said the comparison was sound after
  round 4 had shown it was not.

**What they do not establish.** The gates are MY reports throughout. The
reviewer had no Python in any round and said so every time, and its
final round lists the un-rerun gates as UNVERIFIED rather than folding
them into the verdict.
