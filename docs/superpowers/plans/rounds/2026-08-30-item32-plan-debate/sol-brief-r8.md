# Round 8 - revision 7 answers round 7

You are the cross-vendor reviewer on backlog item 32 (detached dispatch) and
item 33 (automatic review mirror). This is round 8 of the plan debate. Your
round 7 reply is above in this session.

The mirror is a fresh file copy of the repository working tree at source
commit `f88b090` on branch `item32-detached-dispatch`. Its own `HEAD` is a
REMEDIATION commit the mirror builder makes after deleting back-channel
entries, so `.git/refs/heads/...` will not read `f88b090` and that is by
construction, not drift. Your round 7 provenance note was correct to check;
the plan file in the mirror is byte-identical to the one in the source repo,
which I verified with `diff` before dispatching.

The plan is `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md`.
The spec is
`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`.

Ground every claim in a `path:line` you actually opened in this mirror.

## Your round 7 findings, and what I did

I reproduced every one of them before acting. None was refuted.

**1. Launch token DOES NOT CLOSE - accepted, and the token is no longer the
mechanism.** You were right that a token stored inside the artifact it
authenticates is not evidence: the caller can read it out of the directory
it is already looking at. `-Poll` now names a RECEIPT and never a directory.
The receipt is written OUTSIDE the dispatch directory, LAST of all, only on
success, at a path `-Launch` refuses if it already exists. A refused launch
writes no receipt, so there is nothing to substitute.

The regression test is rewritten, because you showed the old one was
impossible to run: launch to success against receipt `R1`; launch again on
the same directory naming a fresh `R2`; take the refusal; assert `R2` was
never created; poll `-Receipt R2` and expect `no-receipt`.

I did NOT claim this eliminates the class. A second test,
`test_a_stale_receipt_answers_for_its_own_round_and_says_so`, polls with
`R1` and asserts it reports `reply-present` with R1's round label, because
that is the truth. The contract states the residual in the same words
LAUNCH UNKNOWN gets, and every poll echoes a `round` label so a misattributed
answer is visible in the record instead of silent.

**2. LAUNCH UNKNOWN remediation contradiction - accepted.** The operation
region no longer puts `taskkill /PID <id>` and LAUNCH UNKNOWN in one
sentence. It says plainly that the dangerous form wrote no pid, that there
is no `<id>` to pass, that clearing it needs another route, and that the
route is unmeasured here so it is surfaced to the user rather than
presented as a remedy.

**3. Hard-kill test has no synchronization seam - accepted.** Step 3 adds
one env-gated seam, `PARALLAX_DISPATCH_HOLD_BEFORE_PUBLISH`: after
`Start-Process` returns and before `pid` is written, the tool creates
`<value>.started` and waits, bounded at sixty seconds, for `<value>.release`.
The test waits for `.started`, kills the tool, never releases. It is
documented as BUILDER CONTRACT on the precedent of the two seams in
`tools/new-kimi-lane-home.ps1`, and it can only make a launch FAIL.

**4. PID identity numeric only - accepted, with your citation.** I read
`tools/kimi-lane-lock.ps1:219-236`. Liveness is now pid PLUS start-time
ticks, computed exactly as `Get-Liveness` computes it: no process is DEAD,
an unreadable start time is `pid-unreadable` and never `running`, differing
ticks mean the pid was recycled so our process is DEAD, and only matching
ticks are `running`. Two new tests cover the recycled pid and the
unmeasurable start time.

**5. Convergence grep is case-sensitive - accepted, and I confirmed the
hit.** The spec spells `SEVEN states` in capitals at
`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:194`,
and the lowercase pattern walked past it. The grep is now `-ni`, and it
also searches `ten states`, `-Token`, and the old poll form.

**6. One-task executability - all three accepted.** Task 1 now carries the
exact documented outer commands verbatim instead of pointing at Task 3.
Task 3's ceiling step carries the measurement command instead of pointing at
Task 2. Task 9 lists and stages
`docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/round-record.md`.

The state list is now ELEVEN: `no-receipt`, `launch-unknown`,
`launch-not-ours`, `pid-unreadable`, `running`, `no-exit-file`,
`exit-unreadable`, `exit-nonzero`, `no-reply`, `reply-empty`,
`reply-present`. `no-receipt` deliberately folds three inputs, stated as a
decision.

## What I want from you

1. For each of your six round 7 findings, say CLOSES or DOES NOT CLOSE,
   citing the `path:line` you read. Do not accept my summary.

2. **The base rate is seven rounds out of seven, each finding at least one
   completion-model hole or an oracle that binds nothing.** State it when
   you answer. Either name an EIGHTH instance - its input, its sequence, and
   the artifact that would be read as this act's result - or say explicitly
   that you searched and found none, and name the shapes you searched for.

3. On your own four cross-act shapes from round 7: location identity,
   process identity, payload identity, execution-context identity. Which of
   the four does revision 7 now bind, which does it only narrow, and which
   is still open? Payload identity in particular: the wrapper file is copied
   into the dispatch directory and its hash is not recorded anywhere. Is
   that reachable as a false completion, or only as a wrong-brief failure
   the round-evidence binder already catches?

4. Is anything in this plan now UNDER-specified in the opposite direction -
   a mechanism described in enough detail that an implementer would have to
   invent behaviour to satisfy it, or two steps that contradict each other?

5. Say plainly whether this plan is ready to freeze and execute, and if not,
   name the smallest set of changes that would make it ready.

End with PASS, FIX, or ESCALATE.
