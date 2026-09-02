# Round 16 - both replacements pinned positively, record corrected

You are the cross-vendor reviewer on backlog item 32 (detached dispatch) and
item 33 (automatic review mirror). This is round 16. Your round 15 reply is
above in this session.

The mirror is a fresh file copy of the working tree at source commit
`39b4457` on branch `item32-detached-dispatch`. Its own `HEAD` is the
builder's remediation commit, by construction. The plan file in the mirror
was hash-compared to the source before dispatch and is identical.

The plan is `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md`.
The spec is
`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`.

Ground every claim in a `path:line` you actually opened in this mirror.

## Your round 15 findings

All accepted. You were right on the record accounting, and I checked it
rather than taking it: the round 5 brief opens `Round 5. SHORT POLL, not a
review round.` Your inference was exactly correct.

**1. The stale attribution at Task 1.** Removed.
`test_a_failure_after_start_kills_the_tree_and_blocks` now says plainly that
it is the HANDLED case, that the `catch` runs and the tree dies, and that
the irreducible case is the separate hard-kill test that bypasses the
`catch`. The step records why keeping them straight matters: a handled
failure dressed as the irreducible one makes the irreducible one look
covered.

**2 and 3. Positive oracles for both spec sections.** Task 9 now carries a
section-scoped positive check for each, because a negative grep is equally
satisfied by a section deleted and by one rewritten wrongly:

- the orphan section must contain `every committed launch`, `interrupted`
  and `no receipt`;
- the state section must name all six ordered states - `no-receipt`,
  `receipt-not-expected`, `launch-unknown`, `launch-not-ours`,
  `pid-unreadable`, `running` - and must NOT contain `LIVENESS IS CHECKED
  FIRST`.

Your "liveness is second" evasion is what the second one is built to catch.

**I ran both against the current unreconciled spec before dispatching.** The
orphan block went red on `every committed launch` and exited 1. The state
block extracted a 32-line section and went red on `no-receipt`, exiting 1.
Both go green only when Task 9 does the work.

**4. The debate record.** Corrected to your accounting: fifteen numbered
dispatches, fourteen full review rounds and one two-lane poll which was
dispatch 5; round 7 took two attempts, the first refused and discarded
unread. The completion-hole claim is now `rounds 1 to 4 and 6 to 9` - eight
rounds, not nine - and the record says explicitly that the discarded round's
only artifact is a renamed file in the session scratchpad, outside this
repository, so it is NOT repo-verifiable.

## What I want from you

1. For each of your round 15 findings, say CLOSES or DOES NOT CLOSE, citing
   the `path:line` you read. Check the corrected record against what you
   actually said.

2. **The base rate is fifteen numbered dispatches out of fifteen** finding
   at least one completion-model hole, a non-binding oracle, or an internal
   contradiction - though rounds 10 through 15 all found NO new
   false-completion path. State the base rate. Then either name a new
   instance of any of the three kinds, or say explicitly that you searched
   and found none, and name what you searched.

3. The only class still producing findings is text or oracles left behind by
   an earlier change. Revision 15 touched Task 1's handled-failure test,
   Task 9's oracle block, and the debate record's accounting and per-round
   entries. Sweep that text first.

4. Say whether this plan is ready to freeze and execute. If not, name the
   smallest set of changes. If it is ready, say so without hedging and give
   me the honest FLOOR: what these nine tasks will NOT have verified when
   they are all done.

End with PASS, FIX, or ESCALATE.
