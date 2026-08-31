# Round 9 - the four changes you named, and the freeze question

You are the cross-vendor reviewer on backlog item 32 (detached dispatch) and
item 33 (automatic review mirror). This is round 9. Your round 8 reply is
above in this session.

The mirror is a fresh file copy of the working tree at source commit
`169d64d` on branch `item32-detached-dispatch`. Its own `HEAD` is the
builder's remediation commit, by construction. The plan file in the mirror
was diffed byte-identical to the source before dispatch.

The plan is `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md`.
The spec is
`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`.

Ground every claim in a `path:line` you actually opened in this mirror.

## The four changes you named as the smallest set to make this freezable

I reproduced all four before acting. None was refuted. I also confirmed both
internal contradictions in the repository myself before fixing them.

**1. Bind Poll to the expected dispatch directory and round.** `-Poll` now
takes `-ExpectedDispatchDir <path>` and `-ExpectedRound <label>`, both
supplied INDEPENDENTLY of the receipt and both compared before any directory
is opened. A mismatch is a new state, `receipt-not-expected`. I took your
reason for requiring the directory as well as the label: `Sol R1` is
reusable across a retry, so the label alone distinguishes nothing there. The
test asserts all three cases separately - both differing, only the label
differing, only the directory differing - because each must be refused on
its own.

I did not claim this closes the class. The contract now states the surviving
residual precisely: a caller that supplies an earlier act's receipt AND that
act's directory AND its label is truthfully told that act's result, because
at that point every value it supplied describes the earlier act. The
remaining controls are the fresh receipt path per round and a launch that
refuses an existing one.

**2. Define receipt validation and the exit-code mapping.**

The schema is now explicit: a JSON object with exactly four fields, all
present - `dispatchDir`, `token` and `round` as non-empty strings,
`startTicks` parsing as a 64-bit integer. A missing field, an empty string, a
`startTicks` that does not parse, a wrong JSON type, or an unknown extra
field is `no-receipt`. Extra fields are rejected so that a future field
cannot be silently ignored by an old tool.

The exit mapping is now part of the contract: exit 0 for `running` and
`reply-present` only; exit 1 for every other state, with the state name on
stdout; exit 2 only when the poll could not be taken at all. The contract
says in those words that EXIT 0 IS NOT A RESULT, because it covers an
unfinished round as well as a finished one, and the documented call site
repeats it. A test asserts one case per state name.

**3. LAUNCH UNKNOWN first, corrected.** Task 9's reconciliation step now
says the first state is NO RECEIPT and the second is LAUNCH UNKNOWN, and
records that the old wording was true only of revision 6.

**4. Task 1's negative oracle, corrected.** It now says to delete the
`catch` written in step 7, and names what step 5 actually does.

The state list is TWELVE: `no-receipt`, `receipt-not-expected`,
`launch-unknown`, `launch-not-ours`, `pid-unreadable`, `running`,
`no-exit-file`, `exit-unreadable`, `exit-nonzero`, `no-reply`,
`reply-empty`, `reply-present`. Every documented poll call site carries the
two new parameters, in Task 1's verbatim commands, Task 3's skill text, and
both lane test strings.

## What I want from you

1. For each of your four required changes, say CLOSES or DOES NOT CLOSE,
   citing the `path:line` you read. Do not accept my summary.

2. **The base rate is eight rounds out of eight**, each finding at least one
   completion-model hole, an oracle that binds nothing, or an internal
   contradiction. State it when you answer. Either name a NINTH instance -
   its input, its sequence, and the artifact that would be read as this
   act's result - or say explicitly that you searched and found none, and
   name the shapes you searched for.

3. Check the new material for the failure mode you have found in three
   separate rounds now: a rule stated in prose with no mechanism, or a test
   whose assertion cannot fail. In particular the receipt schema, the
   exit-code mapping, and the `receipt-not-expected` comparison - is each
   one written so that an implementer producing the wrong behaviour is
   caught by a named test?

4. Does the plan now contain any step whose text CONTRADICTS another step,
   of the kind you found twice in round 8? I would rather you sweep for that
   shape than trust that two were all of them.

5. Say plainly whether this plan is ready to freeze and execute. If it is
   not, name the smallest set of changes that would make it ready, as you
   did in round 8. If it is, say so without hedging, and separately give me
   an honest FLOOR: the things this plan will NOT have verified when its
   nine tasks are done.

End with PASS, FIX, or ESCALATE.
