Panel round 8 (your round 16). New head: `3a0d88b`.
Fix range: `37c264d0865da38b16f1185ce0cf8d287fbb6819..3a0d88b`.
Branch base unchanged: `e2e9242c6153d69e9a4f0c49055e7bf8c81a1dd0`.

All five of your round-15 items are applied. Your finding 3 was raised
independently by the other lane in the same round, blind to you.

## What was applied

**Your finding 1, chunk boundaries.** `Test-FamilyMentioned` removes
line breaks before searching. I did NOT reject multi-chunk renders: the
join inserts exactly a newline, so removing newlines restores adjacency,
and that direction can only create matches, never remove one. Say if you
think rejecting the shape outright is the better answer.

**Your finding 2, first-render precision.** Reproduced before fixing, and
it was worse than stated: with the renderer emitting no skills block, the
pre-fix probe reported `status: clean` with `skills_before: 1` and wrote
an override built from a skill that was never advertised.
`Get-SkillReport` now requires `<skills_instructions>` in its exact form,
bounds the body by its close, and looks for the entry heading only inside
that body. The suppression render calls `Test-FamilyMentioned` directly
and is not parsed at all, as you specified.

**Your finding 3**, the two stale test callers and the comment. Applied.

**Your finding 4**, the count. Corrected to six test functions and eight
collected cases, and the plan row says the earlier number was wrong.

**Your finding 5**, the recorded cost. Rewritten. It now says the search
covers every text chunk of every message; lists the reviewed tree's
`AGENTS.md`, a skill's name or path, the rendered environment, and
client-generated prose; and marks which of those the user cannot reword.
It also states the asymmetry you named: the three feature families are
refused on both renders, the skills family only on the second, so a skill
description naming the skills family does not prevent a review. The stale
sentence at the design's line 329 is marked REVERSED rather than deleted.

## Your task this round

1. Verify each of the five at the code.
2. **The first-render change is the one to attack.** It reintroduces an
   exact-literal structural test on the render whose result feeds the
   override. What renderer change now produces a WRONG count rather than
   a stop? What legitimate render does it refuse?
3. Does removing line breaks before the search create any blocking case
   the record does not admit?
4. The suppression render is no longer parsed. Confirm nothing downstream
   still depends on a value that parse used to produce.
5. Terminal verdict against head `3a0d88b`.

## Evidence (verify, do not trust)

- Both hosts: 440 passed / 1 skipped.
- Live probe both hosts: exit 0, clean, 29 -> 0, override sha256
  `180f09f50d282b5603f1c0d0621f2913ff66c8b7798e7a2f3b7fe8d41f432bb8`.
- Both new cases were run against the reverted script first. The
  chunk-split case returned exit 0. The prose-entries case returned exit
  0 with `status: clean` and `skills_before: 1`.

Say plainly if you find nothing. Cite `path:line`. Anything you did not
check goes under `## Unverified`.
