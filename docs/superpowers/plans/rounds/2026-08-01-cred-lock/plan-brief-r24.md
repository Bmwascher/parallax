Round 24. Both round-23 blockers are applied. Plan header reads revision 23. I
contest nothing. Same evidence rules and verdict grammar.

Both findings are the fourth blind class again — an oracle that does not
partition its reachable states. That class has now produced a finding in three
consecutive rounds, in three different tasks, each time inside text a previous
round had just approved.

## Task 3 — both bounds

At `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:224`.

The paragraph now states the failure first: an upper bound alone is satisfied by
an implementation that never waits at all, because exiting 3 immediately
contends, exits 3, preserves the record and returns well under five seconds.

- **The clamp**: `-WaitSeconds 1 -PollSeconds 10` exits 3, record unchanged, and
  takes AT LEAST 0.8 seconds and under five. The text names the lower bound as
  the half that catches immediate refusal.
- **Retry SUCCESS**, at `:226`, your procedure exactly: a real LIVE holder, a
  contender with `-WaitSeconds 4 -PollSeconds 1`, assert after one second that
  the contender HAS NOT EXITED, release the original holder, then require the
  contender to acquire before its budget expires, return a new nonce, and leave
  its own held record. Noted as what separates retrying from sleeping once and
  giving up.
- Zero-budget immediate refusal unchanged.

## Task 6 — first use

At `:426`. Your bounded pre-lock exception exactly: test ONLY whether the
configured lane-home DIRECTORY exists; if absent, emit the exact shared recovery
command, exit nonzero, create NOTHING — no lane home, no lock, no debate home —
and do not invoke the lock tool at all.

The frozen build order is now explicitly scoped to "once the lane home exists",
and the text says an absent `credentials` directory or credential FILE is still
measured under the lock, so the exception cannot be read as widening.

Both tests: an entirely absent lane home refuses with the complete command,
mutates nothing and never invokes the lock tool; an existing lane home with an
absent credential acquires, validates `absent`, emits the same command, and
releases.

I want to record what this defect actually was, because it is the worst
user-facing one this debate found. On a machine where no lane login had ever
run, the first debate would have failed inside Acquire — before credential
validation, so before emitting the recovery command. The user's very first
attempt would have produced a lock error instead of the instructions telling
them to log in. That is the one moment the instructions matter most, and I
surfaced it only because I flagged an ordering question I was fairly confident
was already handled.

## What I want from you

1. Is this a PASS?

2. The retry-success oracle is the first test in this plan that depends on
   real elapsed time in BOTH directions — it must not have exited at one
   second, and it must acquire within four. If you think that is flaky on a
   loaded CI machine, say so now and name the tolerance you want, because a
   test that fails at random will be deleted by someone eventually and I would
   rather set the bound with you than have it quietly removed.

3. If PASS, the record finalization is DRAFT to FROZEN at revision 23, rounds
   used 24, and the outcome line.
