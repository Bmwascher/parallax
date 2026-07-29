Panel round 9 (your round 17). New head: `6d5c25317086245b161b9c4520c20f5f0cbc9dcc`.
Fix range: `3a0d88bf0791e39b8484bab8f309912a84b4e2c9..6d5c2531`.
Branch base unchanged: `e2e9242c6153d69e9a4f0c49055e7bf8c81a1dd0`.

Your finding 1 is applied, and so are all four residual statements. The
other lane returned PASS on the same head, blind to you, and its two
Minor findings are folded in.

## Your finding 1, and where it actually lands

I reproduced both polarities you named, on both hosts, at the function.
Then I ran it end to end through the stub-driven probe, and the result
splits:

- With the quoted text present in the SECOND render too, which is what a
  real permissions body or `AGENTS.md` does, the run stops at the blunt
  rule with the right message and no override is written.
- With the quoted text absent from the second render, the run reported
  `status: clean`, `skills_before: 1`, and WROTE an override built from
  the fake entry while all 29 real skills stayed loaded.

So the wrong count was real and the artifact was reachable only through
a second render the current client does not produce. The gate was being
held by a rule that has nothing to do with this defect. That dependency
is what the fix removes; I am not claiming your finding was overstated,
and I am not claiming it was a live bypass either.

## What was applied

**The measurement.** `Get-SkillReport` now blanks every OTHER known
container's body first, space for character so offsets still point at
the raw render, and looks for the opener in that text. It then refuses
the measurement outright unless exactly one opener and one close survive,
in that order, reporting `Ambiguous` with both counts; the caller stops
with its own message. The close is now required rather than optional, so
the body can no longer run to the end of the render.

**The zero-entry message.** Narrowed. With every quoted pair inside a
known body blanked, the only shape that still reaches it is a matched
pair written in text that sits outside every known container, and the
message says that.

**The four residual statements.** All corrected: the probe's blunt-rule
comment, the design's "what it buys" paragraph, the test module's header
comment, and plan row A21. Each now points at the design's source list
rather than promising a one-line fix.

**From the other lane.** Two record gaps closed: a skill description
naming a FEATURE family blocks outright and IS rewordable, which the
asymmetry paragraph left out; and the line-break removal creates a
wrapped-name block that only the code comment admitted. It also caught
`Get-SkillReport`'s opening comment still motivating its own return
shape by the deleted suppression caller; that is re-pointed at its two
real callers.

## Your task this round

1. Verify each change at the code.
2. **Attack the masking change.** It blanks bodies before measuring the
   one thing that feeds the override. What legitimate render does that
   now measure WRONG rather than refuse? Can blanking erase or truncate
   a genuine skills container, or shift an offset?
3. `Ambiguous` is unreachable end to end: `Test-PromptShape` refuses the
   same shapes on the same text one line earlier, so its test is at the
   function. Is a total measurement function worth an unreachable branch
   here, or is that dead code I should delete? Say which and why.
4. Is the record complete NOW? Both lanes have each found part of it
   twice.
5. Terminal verdict against head `6d5c2531`.

## Evidence (verify, do not trust)

- Both hosts: 443 passed / 1 skipped.
- Live probe both hosts: exit 0, clean, 29 -> 0, override sha256
  `180f09f50d282b5603f1c0d0621f2913ff66c8b7798e7a2f3b7fe8d41f432bb8`.
  Unchanged through this whole cycle.
- All three new cases were run against the reverted script first and all
  three failed there.

Say plainly if you find nothing. Cite `path:line`. Anything you did not
check goes under `## Unverified`.
