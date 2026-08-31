# Round 17 - the oracles now assert meaning and order

You are the cross-vendor reviewer on backlog item 32 (detached dispatch) and
item 33 (automatic review mirror). This is round 17. Your round 16 reply is
above in this session.

The mirror is a fresh file copy of the working tree at source commit
`405a0c6` on branch `item32-detached-dispatch`. Its own `HEAD` is the
builder's remediation commit, by construction. The plan file in the mirror
was hash-compared to the source before dispatch and is identical.

The plan is `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md`.
The spec is
`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`.

Ground every claim in a `path:line` you actually opened in this mirror.

## Your round 16 findings

All four accepted. Two of them were the same mistake I have now made three
times - an oracle that checks presence and calls it meaning - and your two
counter-examples are what made it concrete.

**1. "Nothing is left behind".** Replaced. The handled case now guarantees
exactly this and no more: no live process tree survives and no receipt is
published. The step says the directory and control files DO remain, that the
`catch` specifies no filesystem cleanup, and that this is deliberate,
because a directory left behind is inert and inspectable while a published
receipt or a live child is not.

**2 and 3. Both spec oracles rewritten in python, asserting meaning and
order.** Your "Every committed launch has no receipt; an interrupted launch
has a pid" example is exactly why. The orphan check now requires three
verbatim clauses: `the pid is on disk for every committed launch`, `an
interrupted launch leaves no receipt`, and `may leave no pid`. The state
check now collects the index of each of the six state names in the
constraints section and asserts the list equals its own sorted order, so
"liveness is second" fails on position rather than on a forbidden phrase.
Both failures print what they found.

**I ran it against the current unreconciled spec before dispatching.** It
extracted a 514-character orphan section and a 1968-character constraints
section, and reported `ORPHAN RED: orphan section missing: the pid is on
disk for every committed launch` and `LIVENESS RED: the stale liveness claim
survives`.

**4. The record's completion claim.** Broadened to `a FALSE-COMPLETION PATH
OR UNCLASSIFIED COMPLETION CONDITION`, and it now names your two
counter-examples: round 4 found a condition outside the state model
entirely, and round 9 found an unfinished round exiting zero, and neither is
one act's artifact read as another's.

## What I want from you

1. For each of your round 16 findings, say CLOSES or DOES NOT CLOSE, citing
   the `path:line` you read.

2. **The base rate is sixteen numbered dispatches out of sixteen** finding
   at least one completion-model hole, a non-binding oracle, or an internal
   contradiction - though rounds 10 through 16 all found NO new
   false-completion path. State the base rate. Then either name a new
   instance of any of the three kinds, or say explicitly that you searched
   and found none, and name what you searched.

3. I have now written a non-binding oracle three rounds running, each time
   as the fix for the previous one. Answer this directly: is the remaining
   defect rate a property of the PLAN, or of the fact that every round asks
   you to re-examine text I wrote hours earlier? Put another way - if the
   nine tasks were executed as written today, which of the defects you have
   found in rounds 14, 15 and 16 would have produced a WRONG SHIPPED
   ARTIFACT, and which would have been caught by the task's own oracle or
   simply read as awkward prose?

4. Say whether this plan is ready to freeze and execute. If not, name the
   smallest set of changes. If it is ready, say so without hedging and give
   me the honest FLOOR: what these nine tasks will NOT have verified when
   they are all done.

End with PASS, FIX, or ESCALATE.
