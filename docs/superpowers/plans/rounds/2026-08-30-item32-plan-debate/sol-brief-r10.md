# Round 10 - the five changes you named, and the freeze question again

You are the cross-vendor reviewer on backlog item 32 (detached dispatch) and
item 33 (automatic review mirror). This is round 10. Your round 9 reply is
above in this session.

The mirror is a fresh file copy of the working tree at source commit
`9695d9a` on branch `item32-detached-dispatch`. Its own `HEAD` is the
builder's remediation commit, by construction. The plan file in the mirror
was diffed byte-identical to the source before dispatch.

The plan is `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md`.
The spec is
`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`.

Ground every claim in a `path:line` you actually opened in this mirror.

## Your five required changes, and what I did

I reproduced all five before acting. None was refuted. I checked the state
ordering and the exit-code contradiction in the file myself before fixing
them, and confirmed the contract region and the executable list disagreed
exactly as you said.

**1. `receipt-not-expected` second everywhere, plus the ordering
regression.** You were right that I had put it in the wrong slot: the
executable list said NO RECEIPT, RECEIPT NOT EXPECTED, LAUNCH UNKNOWN, and
the pinned region said NO RECEIPT, LAUNCH UNKNOWN, RECEIPT NOT EXPECTED. The
region now reads First NO RECEIPT, Second RECEIPT NOT EXPECTED, Third LAUNCH
UNKNOWN, Fourth LAUNCH NOT OURS, Fifth PID UNREADABLE, Sixth liveness, and
that is ordinal-for-ordinal what the executable list says. Task 2's
declaration comment and Task 9's reconciliation step both name the same
three-state opening.

I also took your point that "assert no artifact was read" names no
observation. A new test,
`test_the_expected_act_is_checked_before_any_directory_is_opened`, points a
MISMATCHED receipt at a `dispatchDir` that does not exist, and at a second
one that exists with no `launch.committed`. An implementation checking the
commit artifact first returns `launch-unknown` and fails. That makes the
order observable rather than merely written down.

**2. `running` gets a distinct UNFINISHED code.** Accepted without
qualification, and I accepted your reason as the more important part: "EXIT
0 IS NOT A RESULT" was a rule in prose beside a command, which is the shape
this cycle was created to remove. `running` is now exit 3. Exit 0 is
`reply-present` and nothing else. The contract region says so in those
terms, and a separate test,
`test_a_running_round_can_never_exit_zero`, builds the Task 8 arrangement in
miniature - a stub that writes a nonempty reply then sleeps - and asserts
exit 3 with the reply's content not returned.

**3. Unreadable receipt content versus exit 2.** The mapping now reads: 0
only `reply-present`; 3 `running`; 1 every other state with the name on
stdout; 2 ONLY a parameter-binding failure or an internal execution error,
with the explicit sentence that reading the receipt's content is never exit
2. The `-Launch` line that imported the mirror's three meanings is now
scoped to `-Launch` and says `-Poll` extends the set with 3 and narrows 2.

**4. Receipt path separation, enforced.** `-Launch` now resolves both paths
and BLOCKS if the receipt path equals the dispatch directory or sits inside
it, as step 1, before anything is created. A named test covers equal, one
level down, and two levels down, and asserts no dispatch directory was
created. The script's steps renumbered, and the negative oracle's reference
moved with them.

**5. Schema test expansion.** The test now covers a non-object top-level
value (array, bare string, number), each of the four fields missing, an
empty string in each of the three string fields, an unparsable `startTicks`,
EACH of the four fields in turn holding the wrong JSON type, and an unknown
extra field.

## What I want from you

1. For each of your five required changes, say CLOSES or DOES NOT CLOSE,
   citing the `path:line` you read. Do not accept my summary.

2. **The base rate is nine rounds out of nine**, each finding at least one
   completion-model hole, an oracle that binds nothing, or an internal
   contradiction. State it when you answer. Either name a TENTH instance -
   its input, its sequence, and the artifact that would be read as this
   act's result - or say explicitly that you searched and found none, and
   name the shapes you searched for.

3. Sweep once more for the two shapes you have now found repeatedly, and say
   which you searched for: a rule stated in prose where a mechanism belongs,
   and a step whose text contradicts another step. Rounds 8 and 9 each found
   contradictions that the previous round's fix had introduced, so treat
   revision 9's own new text as the most likely place.

4. Say plainly whether this plan is ready to freeze and execute. If not,
   name the smallest set of changes, as before. If it is ready, say so
   without hedging, and separately give me an honest FLOOR: what these nine
   tasks will NOT have verified when they are all done.

End with PASS, FIX, or ESCALATE.
