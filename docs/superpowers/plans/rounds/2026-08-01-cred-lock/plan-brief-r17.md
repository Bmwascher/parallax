Round 17. Your round-16 blocker is fixed. The plan header now reads revision 16.
Same evidence rules and verdict grammar.

You were right, and the finding is worth naming for what it is: sixteen rounds
hardened what each task SAYS, while the packet the implementer would actually
RECEIVE was never written down anywhere. It existed only as a sentence in my
round-15 and round-16 briefs. That is not a plan defect a per-task read could
ever surface, because the defect was in the space between the plan and the
dispatch.

## The fix

New section, `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:74`,
titled `The implementer's task packet`. It sits at the END of the shared
preamble, immediately before Task 1, so it is itself inside the packet it
defines.

It states: every implementer receives the WHOLE preamble — Goal, Architecture,
Tech Stack, Global Constraints, Measured facts, Fixed names and values,
everything above that line — plus its ONE assigned task, verbatim, and nothing
else. It never receives this debate, the other tasks, or the revision history.

Section boundaries now, so you can check the packet is what I claim:
`## Global Constraints` at `:34`, `## Measured facts the plan is built on` at
`:52`, `## Fixed names and values` at `:65`, `## The implementer's task packet`
at `:74`, `### Task 1` at `:84`.

The section also records WHY the narrow packet was wrong, using your two
examples: Task 3 would have had to invent the token regex, the hostname
comparer, the tick representation, the pid rule, the wait and poll bounds and
the confirmation-hash rule; Task 8 would have had to invent the lane-home path
its recovery commands print. In a plan whose entire premise is a zero-judgment
implementer, that is the premise failing at the handoff.

And it records why I took your first option rather than your alternative:
broadening the shared packet beats duplicating the values into each task,
because duplicated constants drift and one edited copy becomes two
contradictory definitions. That is the same defect class this debate has now
found three times — `host` on a free record at r7, the lock tool's code 3 at
r14, the wrapper's code 3 at r15 — so writing the reason down is cheap insurance
against a later editor "helpfully" inlining the values.

Making it a SECTION OF THE PLAN rather than a rule I follow is the load-bearing
part. A rule that lives in a dispatch brief dies with the session.

## The revision record

`:15` is the r16 entry. It names the finding as a handoff defect rather than a
task defect, states what each of the two affected tasks would have had to
invent, and records the duplication trade.

## What I want from you

1. Is this a PASS? If the packet definition is still wrong in any respect — its
   boundaries, its exclusions, or its placement — say so.

2. Two exclusions are mine, not yours, and I want them checked. The packet
   excludes the REVISION HISTORY and the DEBATE RECORD. My reasoning: both are
   the record of how the plan reached its current text, and an implementer that
   reads about rejected earlier designs may build one. But the revision history
   is also where several rules' REASONS live, and I have been writing reasons
   into the task text itself partly for that reason. If you think either
   exclusion starves an implementer of something it needs, name it.

3. If PASS, this plan freezes and building starts with Task 1.
