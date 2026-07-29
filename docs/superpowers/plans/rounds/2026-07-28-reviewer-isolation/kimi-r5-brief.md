Panel round 5. New head: `6d5c25317086245b161b9c4520c20f5f0cbc9dcc`.
Fix range: `3a0d88bf0791e39b8484bab8f309912a84b4e2c9..6d5c2531`.
Branch base unchanged: `e2e9242c6153d69e9a4f0c49055e7bf8c81a1dd0`.

Your workspace is a FRESH review mirror at the new head.
`KIMI-REVIEW-BRIEF.md` is your round-1 brief, unchanged, and `FIX4.diff`
is the range above.

You returned PASS last round. Both of your Minor findings are applied,
and so is your stale-comment finding.

## Your round-4 findings

**Finding 1**, the stale motivation on `Get-SkillReport`. Applied. The
comment now motivates the `BlockPresent` / `Entries` split by the two
pass-1 callers, and says what it used to describe.

**Finding 2**, the two missing cost rows. Both added: a skill
description naming a FEATURE family, which blocks outright and IS
rewordable, and a family name spelled across a line break, which the
code comment admitted and the design did not.

## The other lane, same round

It returned FIX, and the finding is one you traced and set aside.

You examined the open-only literal inside `INSTRUCTIONS` and concluded
the corner had no reachable consequence. The other lane found the
COMPLETE PAIRED form of it, inside the permissions body, which the
render puts ahead of the skills container. `Get-SkillReport` searched
RAW text while the shape scanner blanked known bodies, so the quoted
example won the search.

I reproduced it, and it goes further than either lane said. At the
function, 29 real entries became ONE fake entry on both hosts. End to
end, with the quoted text absent from the second render, the probe
reported `status: clean` with `skills_before: 1` and WROTE an override
built from the fake while all 29 real skills stayed loaded. With the
quoted text present in the second render, which is what a real body
does, your analysis holds exactly: the blunt rule stops it first. So the
artifact was protected by a rule that has nothing to do with the defect.

## What changed

`Get-SkillReport` now blanks every OTHER known container's body first,
space for character so offsets still point at the raw render, and looks
for the opener there. It refuses the measurement unless exactly one
opener and one close survive, in that order. The close is required
rather than optional. The zero-entry message is narrowed to the one
shape that can still reach it.

## Your task this round

1. Verify each change at the code.
2. **Attack the masking change.** It blanks bodies before measuring the
   one thing that feeds the override. What legitimate render does that
   now measure WRONG rather than refuse? Can blanking erase or truncate
   a genuine skills container, or shift an offset?
3. The `Ambiguous` refusal is unreachable end to end, because
   `Test-PromptShape` refuses the same shapes on the same text one line
   earlier. Is a total measurement function worth an unreachable branch,
   or is that dead code? Say which and why.
4. Is the cost record complete NOW?
5. Terminal verdict against head `6d5c2531`.

## Evidence (verify, do not trust)

- Both hosts: 443 passed / 1 skipped.
- Live probe both hosts: exit 0, clean, 29 -> 0, override sha256
  `180f09f50d282b5603f1c0d0621f2913ff66c8b7798e7a2f3b7fe8d41f432bb8`.
- All three new cases were run against the reverted script first and all
  three failed there.

Say plainly if you find nothing.
