Panel round 6 (your round 14). New head: `5e1c5a2`.
Fix range: `178853feaa2d6233fd818e7f71764db233d556a3..5e1c5a2`.
Branch base unchanged: `e2e9242c6153d69e9a4f0c49055e7bf8c81a1dd0`.

Both round-13 defects reproduced on both hosts before fixing.

## What was applied

`Get-RawContainerPair` is gone. `Get-RawContainerSurface` replaces it and
matches a complete SURFACE: an ordered open/close pair OR a self-closing
tag, with BOTH delimiters matched as grammar - opener
`(?i)<name\b[^>]*>`, close `(?i)</name\s*>`. Each surface carries the
literal that matched and whether it is the exact form. A non-exact
surface is refused with the existing message, and the message now names
the delimiter that is actually wrong rather than always the opener.

`Test-ContainerPresent` is unchanged in shape: masked presence, or a raw
surface.

The global-file location fallback moved inside the guard.

The design's accepted limit now covers all four families, self-closing
mentions, and an opener and close written in two different bodies.

## Your task this round

1. Attack `Get-RawContainerSurface` at the grammar level. The opener
   pattern is `(?i)<name\b[^>]*>` and the close is `(?i)</name\s*>`. What
   real tag shape does either miss, and what does either match that is
   not a tag at all?
2. Self-closing is decided by `EndsWith("/>")`. Is that right for every
   shape the opener pattern admits, including one with an attribute value
   that itself ends in a slash?
3. The exactness decision now compares the matched literals against
   `<name>` and `</name>` case-sensitively. Confirm a case variant of
   either delimiter still lands on the non-exact block rather than
   anywhere else.
4. Anything the four-family loop misses that the old per-function checks
   caught.
5. Terminal verdict against head `5e1c5a2`.

State plainly if you find nothing. Five rounds have each found a defect
inside the previous round's fix, and a sixth finding invented to continue
the pattern is worse than a clean pass.

Cite `path:line`. Anything you did not check goes under `## Unverified`.
