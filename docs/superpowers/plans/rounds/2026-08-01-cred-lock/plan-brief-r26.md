Round 26. All six round-25 blockers are applied. Plan header reads revision 25.
I contest nothing. Same evidence rules and verdict grammar.

The sweep was the right thing to ask for. Six findings in five tasks, all one
shape, and two of them are defects in the SHIPPED TOOL rather than in the plan's
prose.

## Task 1 — a usable test file, not a path that exists

At `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:116`. Every
`evals/...py` token must resolve to a READABLE REGULAR FILE, with a stat or
readability failure fatal. The text names the case: a DIRECTORY named
`test_something.py` exists happily and pytest may collect nothing from it, so
`exists()` passes while the module is gone.

Mutation added at `:129`: name a directory ending in `.py` and require the
checker to report it as not a test file. That is the direction an `exists()`
implementation passes.

## Task 5 — both bootstraps are four rows

At `:397` and `:404`. Both probes: only a successfully measured NONEXISTENT path
creates; a DIRECTORY applies the ACL; a NON-DIRECTORY object and an UNMEASURABLE
path each exit 6.

Lane home: no mutation, no lock invocation, no client invocation, no
`-VerdictOut` write. Credentials: no client invocation, the obstructing object
preserved byte-for-byte with its ACL intact, and RELEASE in the `finally` so the
lock ends `free` rather than stranded.

Named fault seams on both, and both directions tested with the object's bytes
AND its ACL asserted unchanged; the credentials case also asserts the lock is
`free`.

I want to name what this one actually was, because "partition the probe"
undersells it: the wrapper would have written an ACL onto an object it had never
established it owned. That is a privileged write on an unidentified target, in
the step whose whole claim is that it is safe and identity-scoped.

## Task 6 — three

**The table contradiction**, at `:446`. My own r24 sentence said "the last three
rows" never invoke the lock, which swept in the DIRECTORY row and contradicted
the table one line above. Now: the recovery row and the two refusal rows create
nothing and never invoke the lock; the directory row alone proceeds.

**The seam is named**, at `:448`:
`PARALLAX_LANE_HOME_DIRECTORY_PROBE_FAULT`, build mode only, firing immediately
before the real probe, simulating the unmeasurable row, no stdout, no recovery
command, no mutation, no lock invocation, one exact stderr sentinel shared by
implementation and test.

**Deletion failure**, at `:470`, and this is a live defect in the shipped tool.
`tools/new-kimi-lane-home.ps1:131-133` calls `Remove-Item` NON-TERMINATINGLY and
prints `removed <path>` on the very next line, so a failed deletion prints
success and exits 0 today. Remove mode now deletes terminatingly and VERIFIES
absence before releasing; a deletion error or a residual path is primary, with
no `removed` line, no release, and the held record byte-identical. Its oracle is
real rather than seamed: an exclusively opened file beneath the debate home,
under both hosts. Failed-build cleanup keeps the original failure primary, still
attempts release, reports the cleanup error on stderr only, and leaves the lock
`free` when release succeeds, proven by a named cleanup-deletion seam.

## Task 8 — the clean row

At `:650`, plus an all-clean fixture at `:693` requiring aggregate `OK` with a
detail naming the successful binary and floor comparison, and the row pinned.

The reason is in the text: without it every fixture in that task was a FAILURE
fixture, so an implementation that never emits `OK` at all would have passed the
lot. A table that calls itself total and omits the success case is the same
defect as an oracle that cannot fail, arriving from the other direction.

## Task 9 — three filesystem interactions

At `:717`. "Exactly THREE steps run before the lock", which r24 had just
written, excluded parameter validation and debate-id generation; it now says
three FILESYSTEM INTERACTIONS, which is the boundary that was actually meant.

## What I want from you

1. Is this a PASS?

2. Two of these six are defects in code that is already committed and running —
   the non-terminating `Remove-Item`, and the ACL bootstrap. Both are fixed by
   tasks in this plan. Neither is fixed by Task 1, which is the merge blocker I
   intend to build first. Do you see any reason to reorder, or does Task 1 still
   go first?

3. If PASS, the record finalization is DRAFT to FROZEN at revision 25, rounds
   used 26, and the outcome line.
