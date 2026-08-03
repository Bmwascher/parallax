Round 20. All of round 19 is applied. Plan header reads revision 19. I contest
nothing. Same evidence rules and verdict grammar.

Round 19's central finding was correct and I want to state it plainly rather
than just fix it: r18 restored the spec's visibility behaviour in the DIRECT
TOOL and left both callers free to throw it away. The builder's own rule said
all internal lock output is CAPTURED, full stop. So a perfectly correct lock, a
perfectly correct custody JSON, and a fully green suite could still have shipped
a lane that silently reclaims other people's locks. That is worse than the
omission it was meant to fix, because it looks finished.

## Task 3 — three fixes

**Fresh-acquire wording**, at
`docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:241`. Now: "A
fresh acquisition over a `free` record emits NO STDERR REPORT; its stdout is
still exactly the new nonce", with a sentence recording that the old wording
contradicted the stdout rule one line above.

**The oracle list**, at `:250`. It now covers both contention forms and both
liveness values, and says why a list covering only the LIVE-record case is
inadequate. Six oracles: DEAD reclaim with exact line and stdout still the
nonce; fresh acquire with no stderr and stdout still the nonce; LIVE-holder
budget exhaustion; exclusive-handle contention with EMPTY stdout and the exact
handle line, noted as the only case where no record was read; a competing
identity under `PARALLAX_LANE_LOCK_STARTTIME_FAULT` with unchanged record, empty
stdout, and a holder line containing exactly `liveness UNMEASURABLE`; and each
override's success line with empty stdout.

**Both overrides frozen**, at `:244-247`, with your exact strings on stderr and
empty stdout. The two table rows at `:278` and `:282` now point at those frozen
lines instead of saying "report what it displaced" and saying nothing.

## Task 5 — the wrapper propagates lock stderr

At `:377`, as its own frozen paragraph ahead of the test list, separate from the
CLIENT stream rules so the two cannot be confused. Lock STDOUT captured, because
it is the nonce; lock STDERR forwarded UNCHANGED. The paragraph names why the
existing test could not catch it: exit 3 plus a non-invoked stub passes whether
or not the diagnostic survives.

Two caller-boundary tests added to Step 1: LIVE-holder contention surfaces the
lock's EXACT holder diagnostic on the wrapper's stderr, and a DEAD-holder
reclaim surfaces the EXACT reclaim diagnostic while the wrapper otherwise
succeeds.

## Task 6 — three fixes

**Stderr propagation**, at `:403`. The "all output is CAPTURED" sentence is
replaced: stdout captured because it is the nonce, stderr forwarded unchanged,
with the failure mode recorded — correct lock, correct custody JSON, green
tests, swallowed evidence. Remove is covered the same way. Two integration
oracles: a build that RECLAIMS succeeds with the exact reclaim line on stderr
and stdout exactly the custody JSON; a build that CONTENDS fails with the exact
holder line on stderr and nothing on stdout.

**Home B**, at `:429`. Your six-step sequence exactly, using only the real
builder: build B and capture its nonce, release B's lock directly leaving B on
disk, build A retaining A's hold, `-Remove` B with A's identity and nonce,
assert exit 2 and byte-identical A, B and lock, then tear down by removing A
normally and acquiring a fresh hold for B before removing B. The text records
that "prepare a valid home by hand" still left construction to invention and
that building B under A's hold would contend and never reach the case.

**The recovery command**, at `:429`. The refusal now requires the exact
executable command, asserted whole, and cites the spec line requiring it.

## The recovery command is a shared constant

This is my one departure from your instructions, and it follows the packet
lesson rather than ignoring it. You specified the command under Task 6 and then
told Task 8 to use "the same executable one-line recovery command specified
under Task 6". But the packet gives an implementer its own task and never
another, so Task 8's implementer would never see it.

It is now a single frozen constant in `Fixed names and values`, at `:76`, with a
note that it lives there because two tasks emit it and a constant copied into
two tasks drifts. Both tasks reference it. Reject this if you meant something
else.

## Task 8 — the doctor prints it

At `:581`, `:582` and `:594`. All three credential-failure rows — `absent`,
`unreadable`, `malformed` — carry the lane login recovery command against the
configured lane home, and the pin covers the COMPLETE command rather than the
wrapper's filename. The paragraph names the asymmetry that made this visible:
the doctor had recovery commands for both lock overrides and none for the one
failure a user can actually fix themselves.

## Task 9 — the shipped literal

At `:641`. Your replacement wording for the malformed classes, verbatim, so the
literal states the schema RULE instead of enumerating instances that can fall
behind Task 3. Plus your three visibility sentences, so the shipped contract and
the implementation task describe the same tool. The region is pinned whole, so
both additions get a decisive coverage oracle.

## Your answer to question 4

Recorded in the plan's r19 revision entry, both classes named: composition
across caller boundaries, and fixture constructibility. Your point that Minor 4
was the concrete survivor of the second class is exact — that oracle could not
have reached its assertion at all.

I have also retained the second fable report at
`docs/superpowers/plans/rounds/2026-08-01-cred-lock/fable-whole-plan-review-2.md`,
which closes the UNVERIFIED item you raised about it. It carries the same
provenance limit as the first, and its session-adjudication section records that
round 19 found the fix inadequate — so the artifact does not read as though its
Important were cleanly closed.

## What I want from you

1. Is this a PASS?

2. The shared-constant decision above is mine. If you meant the command to be
   duplicated per task, say so and I will duplicate it.

3. You have now named two structural blind classes. Both were found by comparing
   things this debate had only ever compared to themselves — plan against spec,
   tool against caller. Is there a third comparison neither of us has made? I
   would rather spend a round on that than find it after Task 6 is built.
