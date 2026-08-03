Round 22. All three round-21 blockers are applied. Plan header reads revision
21. I contest nothing. Same evidence rules and verdict grammar.

Task 10 is the one worth stating plainly. That check guards the merge, it sits
in the plan whose governing invariant is "an unmade measurement is never a clean
one", and it violated that invariant directly: `git log` piped into
`Select-String`, exit code never read, so a range it cannot read yields no
matches and no matches prints `clean`. Twenty rounds read past it, because every
one of them read it as prose. It took the runtime rule I added one round earlier
to make it visible.

## The Global Constraint, narrowed

At `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:54`, your
wording. Scope is now user-facing MULTI-STEP commands emitted as one copy-paste
unit where a later step consumes an earlier step's output. Standalone
single-script commands, verification commands, parameter and JSON examples, and
documented prose lifecycles are named as staying with their task-local oracles.

You were right that it over-reached. As written it would have demanded an
execution suite for Task 8's single-invocation override commands, which Task 3
already exercises under both hosts, and would have blurred the line between a
recovery command and a pytest invocation.

## Task 6 — the four-row matrix

At `:437`. Your matrix verbatim, introduced by the reason it replaced the old
text: the command has THREE dependent boundaries, so "both directions" sounded
complete while leaving a JSON-parse failure and a login failure unexercised.

At `:446`, the escaping failure direction, with its own reason: all four rows
could use an ordinary path, so an implementation that never doubles apostrophes
would pass every one. The success row now uses a lane home containing an
apostrophe and requires the doubled apostrophe in the emitted command, writes
confined to the intended lane home, and a structurally `ok` credential.

Fixture routing frozen exactly as you specified: a disposable current directory
containing `tools/`; stubs plus invocation markers for the first three rows; the
real lock tool, wrapper and validator copied in for the success row, with the
fake client under a disposable `USERPROFILE`; and in every row the exact line
extracted from the builder's refusal.

## Task 10 — the history measurement is fatal first

At `:695`. Your snippet verbatim: capture `$messages`, capture `$LASTEXITCODE`,
throw on nonzero, and only then interpret. The step text now names the failure
mode in the plan's own terms rather than just fixing the code.

TWO mutations now, because the check has two failure directions: a controlled
input containing `Claude-Session` must throw, and an INVALID REVISION RANGE must
throw on the `git log` failure and never print `clean`.

## The fourth class

Recorded in the r21 revision entry as **oracle versus reachable failure-state
partition**, with your two examples: fixture constructibility, and Step 1b's
"both directions" hiding four rows.

Your judgment on the comparison set is recorded too, in your terms: not closed
at revision 20, and after these three fixes no further unexamined artifact
boundary in this scope, with the abstract category unprovable either way. I
asked for a stated judgment rather than an absent finding and you gave one, so
it goes in the record rather than in my summary of it.

## What I want from you

1. Is this a PASS?

2. Task 10's defect was PRE-EXISTING, not introduced by any recent round. I have
   not swept the plan for others of its kind — a measurement interpreted without
   first checking whether it was taken. If you can see another from where you
   sit, name it now. If you would rather I sweep the plan for that one pattern
   before you answer, say so and I will, since it is the exact shape that just
   survived twenty rounds.

3. If PASS, the record finalization is DRAFT to FROZEN at revision 21, rounds
   used 22, and the outcome line.
