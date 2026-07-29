Panel round 5 (your round 13). New head: `178853f`.
Fix range: `89ef9c41e0553a6ee71c5e97a40c7fc8c2b0168e..178853f`.
Branch base unchanged: `e2e9242c6153d69e9a4f0c49055e7bf8c81a1dd0`.

All three round-12 defects were reproduced on both hosts before fixing,
exactly as you described them.

## What was applied

I did NOT patch the three sites. Three rounds running, a fix for one
container family left the same hole open in the next one, so the rule
itself was the defect. Presence for EVERY known family - skills, plugins,
recommended plugins, apps - now goes through one function,
`Test-ContainerPresent`: the masked text, OR an ordered raw pair
recognized by known-name grammar with attributes allowed and
case-insensitively.

A paired opener that is not the exact literal is refused as a non-exact
shape wherever it sits, nested included, with the message the masked
exactness scan already used.

The global-file measurement is wholly inside one guard, and `Join-Path`,
`Test-Path` and `Resolve-Path` all stop on error. A failed check blocks
with "could not be determined" rather than reporting an absent file.

## Two failures inside this work, so you can aim at them

1. The first version of the pair rule examined only the FIRST paired
   opener. The real prompt carries a genuine `<skills_instructions>`
   ahead of `<INSTRUCTIONS>`, so it found the exact one, declared the
   family fine, and walked past the attributed pair nested below. Its own
   regression caught it. It now examines every paired opener.
2. Thirty-five dot-source tests failed with WinError 206 because the
   helper passed the whole function block on the command line and the
   block had outgrown the Windows limit. The helper now writes it to a
   file. Nothing about the code under test was involved.

## Evidence (verify, do not trust)

- Both hosts: 431 passed / 1 skipped.
- Live probe both hosts: exit 0, clean, 29 -> 0, override sha256
  unchanged at
  `180f09f50d282b5603f1c0d0621f2913ff66c8b7798e7a2f3b7fe8d41f432bb8`.

## Your task this round

1. Attack `Test-ContainerPresent` and `Get-RawContainerPair` directly.
   They are now the single point of failure for four families at once,
   which is the trade I made deliberately. What input makes either return
   the wrong answer?
2. Does the non-exact-pair refusal fire on anything legitimate? A skill
   DESCRIPTION and the user's own AGENTS.md are both free text, and both
   were the source of earlier false blocks.
3. Is the close-tag search correct? It is ordinal case-insensitive from
   the end of each opener.
4. The global-file guard: any remaining path where the run continues on a
   failed check.
5. Terminal verdict against head `178853f`.

Cite `path:line`. Anything you did not check goes under `## Unverified`.
