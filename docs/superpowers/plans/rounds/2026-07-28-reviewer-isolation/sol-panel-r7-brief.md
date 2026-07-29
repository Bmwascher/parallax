Panel round 7 (your round 15). New head: `37c264d`.
Branch base unchanged: `e2e9242c6153d69e9a4f0c49055e7bf8c81a1dd0`.

Two commits since you last looked, and the second is a DESIGN CHANGE
rather than a fix. Review it as one.

## `a265eec` — your round-14 findings, applied

All three reproduced on both hosts first. The known-family tag grammar
now requires whitespace, `/` or `>` after the name, tokenizes quoted
attribute values, and captures the self-closing slash at the real
terminator.

## `37c264d` — THE BLUNT RULE

I put the pattern to the user: six rounds, six shapes, five of them
reaching a clean report, every one a defect in telling a real block from
a quoted one. I recommended abandoning the structural question, and the
user agreed.

The suppression check no longer parses anything. A known family name
occurring at all, case-insensitively, anywhere in a render, stops the
run. `Get-RawContainerSurface`, `Test-ContainerPresent` and
`Get-StructuralText` are deleted. `Get-SkillReport` and
`Get-FeatureReport` take one argument again. The script is 910 lines,
down from 984.

The three feature families are refused on BOTH renders. The skills family
is expected on the first and refused on the second.

The FIRST render keeps the full parser: it still enumerates every
advertised skill, classifies each by source directory, and refuses an
entry it cannot place.

Nine tests reversed from expecting a pass to expecting a block. Each
names what it used to assert. A shared `assert_blocked_for_a_known_name`
helper carries the three messages a known name can stop on.

The withdrawn promise is the one that started three rounds of this: a
house rule naming a marker in prose used to be legitimate. It now blocks,
and the message tells the user to reword it.

## Your task this round

1. **Attack the decision, not only the code.** Is there a false-clean
   path left in the suppression check? If you believe the blunt rule is
   the wrong trade, say so with the case that makes it wrong.
2. The first render still runs the full parser. Does anything that used
   to be caught by the deleted helpers now go unnoticed THERE, where a
   mistake is a wrong report rather than a broken gate? Name what it
   would misreport.
3. The deletions. Confirm nothing else depended on the three removed
   functions, and that no caller now passes an argument that is ignored.
4. The reversed tests. Are any of them now vacuous, and does the shared
   helper still fail the suite if a run goes clean?
5. Is the recorded cost complete? The design says the cost is any mention
   of the four names in the reviewer's own AGENTS.md or skill
   descriptions, including a mention inside a longer word and a different
   tag name that begins with a family name. Name anything else it blocks
   that the record does not admit.
6. Terminal verdict against head `37c264d`.

## Evidence (verify, do not trust)

- Both hosts: 438 passed / 1 skipped.
- Live probe both hosts: exit 0, clean, 29 -> 0, override sha256
  `180f09f50d282b5603f1c0d0621f2913ff66c8b7798e7a2f3b7fe8d41f432bb8` -
  unchanged through all seven rounds AND through this rewrite.

Say plainly if you find nothing. Cite `path:line`. Anything you did not
check goes under `## Unverified`.
