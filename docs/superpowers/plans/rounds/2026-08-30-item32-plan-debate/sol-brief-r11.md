# Round 11 - the four changes you named after the clean sweep

You are the cross-vendor reviewer on backlog item 32 (detached dispatch) and
item 33 (automatic review mirror). This is round 11. Your round 10 reply is
above in this session.

The mirror is a fresh file copy of the working tree at source commit
`16d0ad7` on branch `item32-detached-dispatch`. Its own `HEAD` is the
builder's remediation commit, by construction. The plan file in the mirror
was hash-compared to the source before dispatch and is identical.

The plan is `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md`.
The spec is
`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`.

Ground every claim in a `path:line` you actually opened in this mirror.

## Your four required changes, and what I did

I reproduced all four in the file before acting. None was refuted.

**1. Task 3's stale exit sentence.** Replaced. The point of use now states
the mapping in full: 0 means `reply-present` and nothing else; 3 means
`running`, an UNFINISHED round; 1 is a transport failure with the state name
on stdout; 2 is a bad invocation. The per-site parametrized test now asserts
that sentence is present in each call's section, so a site that documents
the command without the mapping fails by that site's name.

**2. `test_an_unreadable_receipt_is_no_receipt_at_exit_one`.** Added, using
your suggestion of passing a DIRECTORY as `-Receipt`, because it is
deterministic on both hosts and needs no permission juggling. It requires
state `no-receipt` and exit 1, never exit 2.

**3. Which artifact is last.** You were right and I had it wrong in four
places. The order is now stated the same way everywhere: pid and start
ticks, then the internal `launch.committed` marker, then the EXTERNAL
receipt published last of all. The architecture line, the tool contract
region and the executable steps all say that, and the test is renamed
`test_a_committed_launch_publishes_pid_then_marker_then_receipt` and asserts
all three positions by content. I also removed a sentence inside step 7 that
still claimed the receipt path was checked "before step 1", which was true
before the path check became step 1.

**4. The spec's mechanism section.** Task 9 step 2 now opens by replacing
`design.md:136-148` outright - the section describing the SESSION running
`Start-Process`, writing the pid file and polling it - with the transaction
this plan builds. The convergence grep gained `The session launches it with`
and `sidecar exit-code file`. And the step now carries a POSITIVE oracle
beside the negative one, because every check in that step searched only for
what should be gone: `grep -c` for `dispatch-detached.ps1`, `-ReceiptPath`
and `-ExpectedDispatchDir`, expecting at least three and read to confirm
they are in the mechanism section.

## What I want from you

1. For each of your four required changes, say CLOSES or DOES NOT CLOSE,
   citing the `path:line` you read.

2. **The base rate is ten rounds out of ten** finding at least one
   completion-model hole, an oracle that binds nothing, or an internal
   contradiction - though round 10 found no new false-completion path, and
   named the eight shapes it swept for. State the base rate when you answer.
   Either name a new instance of any of those three kinds, or say explicitly
   that you searched and found none, and name what you searched for.

3. Rounds 8, 9 and 10 each found a contradiction that the PREVIOUS round's
   fix had introduced. Revision 10 touched the architecture line, the tool
   contract region, the executable steps, the test names, Task 3's
   point-of-use text, its per-site test, and Task 9's step 2 and step 3.
   Sweep that new text first.

4. Say plainly whether this plan is ready to freeze and execute. If not,
   name the smallest set of changes. If it is ready, say so without hedging
   and give me the honest FLOOR: what these nine tasks will NOT have
   verified when they are all done.

End with PASS, FIX, or ESCALATE.
