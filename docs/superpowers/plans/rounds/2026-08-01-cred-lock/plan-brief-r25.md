Round 25. All three round-24 blockers are applied. Plan header reads revision
24. I contest nothing. Same evidence rules and verdict grammar.

All three were consequences of r23's own two edits, and two of the three are the
fourth blind class for the fourth round running. The retry oracle is the sharper
one: it would have CERTIFIED the exact behaviour it was written to forbid.

## Task 3 — signal-synchronized, both branches

At `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:226`.

The paragraph states both failures before the fix: "has not exited after one
second" does not prove contention was ever REACHED, since the process can still
be starting, so releasing then lets a never-retrying implementation find a free
record on its first real attempt; and contention has TWO branches, so a tool can
retry one and refuse instantly in the other.

**Seam frozen** at `:228`: `PARALLAX_LANE_LOCK_CONTENTION_SIGNAL=<path>`. On the
FIRST actual contention decision, once only, exactly one ASCII line — `handle`
or `holder` — written BEFORE sleeping. A signal-write failure exits 6 with no
lock mutation, so the oracle cannot quietly decay back into a timing test.

Both oracles run against BOTH branches:

- **Clamp**: `-WaitSeconds 1 -PollSeconds 10`, wait up to ten seconds for the
  expected signal, measure FROM the signal, process alive at least 0.5 seconds,
  exit 3 within five, record preserved.
- **Retry success**: `-WaitSeconds 30 -PollSeconds 1`, wait up to ten seconds for
  the signal, assert still running, release the handle or the holder, require
  acquisition within ten seconds with a new nonce and the contender's own held
  record.
- Signal timeout: terminate in a `finally`, keep the fixture until assertions
  finish, fail.

This also answers the flakiness question I raised last round, and answers it
better than I asked. I offered to widen a tolerance; you removed cold-start
scheduling from the proof entirely. The text records why widening would not have
worked: the false-positive path was never about the window's size.

## Task 6 — the probe is four rows

At `:436`. A table, not prose, because two of the four rows are the ones I
missed:

- successfully measured NONEXISTENT: emit the recovery command, exit nonzero
- a DIRECTORY: proceed to Acquire
- exists but NOT a directory: refuse nonzero, NO recovery command
- existence or type CANNOT be measured: fail closed, refuse nonzero, NO recovery
  command

All four create nothing and never invoke the lock tool; the probe only reads.
The text names the consequence of the reading I had left open: printing a login
command that cannot fix an obstruction.

Two oracles: a regular FILE at the lane-home path, and a deterministic
probe-fault seam for the unmeasurable row. The text says why the second is a
seam rather than a real permission denial — machine ACL behaviour is not
something a test may depend on.

## Task 9 — the shipped literal

At `:708`. It named two pre-lock steps and now names three: the login wrapper
creating the directory, the login wrapper applying its ACL, and the builder's
read-only fail-closed probe. It states explicitly that the builder NEVER creates
the directory, that a missing directory means print the command and stop without
taking the lock, and that once the directory is confirmed both the credentials
directory and the credential file are measured UNDER the lock.

This one is worth naming as a pattern rather than a one-off: my Task 6 change
made a SHIPPED CONTRACT SENTENCE false, one region away, and nothing in the task
text pointed at it. That is the second time in this debate a task edit silently
invalidated shipped literal text.

## What I want from you

1. Is this a PASS?

2. The four-row probe table is now the pattern I should have used the first
   time. Are there other places in this plan where I wrote a binary where the
   states are not binary? You have caught four; I would rather you sweep for the
   shape than catch the fifth after building starts.

3. If PASS, the record finalization is DRAFT to FROZEN at revision 24, rounds
   used 25, and the outcome line.
