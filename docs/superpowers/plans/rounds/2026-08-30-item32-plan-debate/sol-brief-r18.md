# Round 18 - the record's counts are now bound to a commit

You are the cross-vendor reviewer on backlog item 32 (detached dispatch) and
item 33 (automatic review mirror). This is round 18. Your round 17 reply is
above in this session.

The mirror is a fresh file copy of the working tree at source commit
`061a2ee` on branch `item32-detached-dispatch`. Its own `HEAD` is the
builder's remediation commit, by construction. The plan file in the mirror
was hash-compared to the source before dispatch and is identical.

The plan is `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md`.
The spec is
`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`.

Ground every claim in a `path:line` you actually opened in this mirror.

## Your round 17 finding, and why I did more than you asked

You said the remaining fix was purely documentary: update the count to
sixteen dispatches, extend the two ranges through round 16, then freeze.

I did that, and I ALSO changed the shape of the claim, because your finding
was the second of its kind. Round 15 caught this record saying four reviews
when fourteen had happened. Round 17 caught the correction already one
behind. A running total inside a document that the next round will review is
stale by construction, and updating it each round is a treadmill, not a fix.

So the section now opens by saying every count in it is BOUND TO A COMMIT,
and why: a claim about a fixed point stays true, where a running total
cannot. It names backlog item 70 as the general form of this hazard. The
figure reads: as of `92c892f`, the commit the paragraph was written on top
of, SEVENTEEN numbered dispatches - sixteen full review rounds and one
two-lane poll, which was dispatch 5.

Note the number is seventeen, not your sixteen. Your count was correct for
what you had seen; round 17 itself is the seventeenth dispatch, and the
paragraph is written after it.

**I also made an off-by-one in the binding and corrected it in the next
commit.** The first version said "as of the PARENT of `92c892f`", which is
the wrong commit: the counts were true as of `92c892f` itself. I am telling
you rather than letting you find it, because it is precisely the class under
discussion and I would rather you check the correction.

The two ranges are extended: "rounds 10 onward found none - through round 17
as this was written", and the per-round entry is now "Rounds 13 to 17",
carrying round 16's two counter-examples and round 15's and 17's record
findings.

I also recorded your answer to my direct question, in your terms: partly the
plan; the runtime mechanism has been stable since revision 10; the recent
defects sit in Task 9's reconciliation text and its oracles; and because
Task 9 ships the reconciled spec, an oracle that accepts inverted meaning is
a real plan defect even though it cannot corrupt the dispatcher.

## What I want from you

1. Say CLOSES or DOES NOT CLOSE on the record correction, citing the
   `path:line` you read - including my off-by-one repair.

2. **The base rate is seventeen numbered dispatches out of seventeen**
   finding at least one completion-model hole, a non-binding oracle, or an
   internal contradiction - though rounds 10 through 17 all found NO new
   false-completion path. State the base rate. Then either name a new
   instance of any of the three kinds, or say explicitly that you searched
   and found none, and name what you searched.

3. You said after the surgical correction: freeze and execute, no further
   mechanism revision justified. If that still holds, say FREEZE without
   hedging.

4. Give me the honest FLOOR either way: what these nine tasks will NOT have
   verified when they are all done, stated as things a reader of the frozen
   plan should not believe are covered.

End with PASS, FIX, or ESCALATE.
