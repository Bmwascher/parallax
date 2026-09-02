# Round 14 - the receipt-last consequence, propagated

You are the cross-vendor reviewer on backlog item 32 (detached dispatch) and
item 33 (automatic review mirror). This is round 14. Your round 13 reply is
above in this session.

The mirror is a fresh file copy of the working tree at source commit
`ad8b106` on branch `item32-detached-dispatch`. Its own `HEAD` is the
builder's remediation commit, by construction. The plan file in the mirror
was hash-compared to the source before dispatch and is identical.

The plan is `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md`.
The spec is
`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`.

Ground every claim in a `path:line` you actually opened in this mirror.

## Your round 13 findings

Both accepted, and the first one was the most valuable finding since round
9. You were right that the hard-kill test could never have passed: once the
receipt became the last published artifact, a kill before publication leaves
no receipt, so the poll stops at check 1 and never reaches the marker check.
I had moved the mechanism in revision 10 and never propagated the
consequence.

**1. The hard-kill test now requires `no-receipt`, never success**, and the
step records why it previously named the wrong state.

**2. LAUNCH UNKNOWN is redefined** as a VALID receipt whose directory has no
marker. The region now says that since the marker is written before the
receipt, a receipt that exists proves the marker once existed, so this state
means the marker has since gone.

**3. The danger moved with it.** The contract now says NO RECEIPT IS NOT
EVIDENCE THAT NOTHING STARTED, in those words: the receipt is the
transaction's last act, so an interrupted launch leaves no receipt and may
have left a live untracked child, and in its worst form no pid either, so
the whole-tree kill cannot clear it. The operation region's "the case that
command CANNOT clear" now names NO RECEIPT rather than LAUNCH UNKNOWN.

**4. Two new tests for receipt freshness**, which you correctly said was
specified and unpinned:
`test_an_existing_receipt_blocks_before_the_directory_is_reserved`, which
asserts the dispatch directory does NOT exist afterwards so the ordering is
what is proven; and
`test_a_receipt_that_appears_during_the_launch_fails_closed`, which uses the
hold barrier to create the receipt while the tool waits, and requires the
create-new write to fail, the `catch` to kill the tree, and exit 1.

**5. One thing you did not name, which I found while applying yours.**
`test_poll_reports_launch_unknown_when_commit_is_absent` said "a reserved
directory with no `launch.committed`" - an input that now stops at
`no-receipt`, so the test was unreachable for exactly the reason you gave
for the hard-kill one. It is now
`test_poll_reports_launch_unknown_when_the_marker_is_gone`: launch to
success, delete the marker, poll with that launch's own receipt and matching
expected pair. I am telling you because it is the same defect you found and
I would rather you check my repair than discover I made a second one.

## What I want from you

1. For each of your round 13 findings, say CLOSES or DOES NOT CLOSE, citing
   the `path:line` you read. Include my item 5 in that check.

2. **The base rate is thirteen rounds out of thirteen** finding at least one
   completion-model hole, a non-binding oracle, or an internal
   contradiction - though rounds 10 through 13 all found NO new
   false-completion path. State the base rate. Then either name a new
   instance of any of the three kinds, or say explicitly that you searched
   and found none, and name what you searched.

3. Round 13's finding was a consequence of a mechanism change three
   revisions earlier that I failed to propagate. Sweep specifically for
   OTHER unpropagated consequences of the receipt-last ordering and of the
   `-ExpectedDispatchDir`/`-ExpectedRound` addition: any text, test, state
   name, or task step still written as though the older mechanism were in
   force.

4. Say whether this plan is ready to freeze and execute. If not, name the
   smallest set of changes. If it is ready, say so without hedging and give
   me the honest FLOOR: what these nine tasks will NOT have verified when
   they are all done.

End with PASS, FIX, or ESCALATE.
