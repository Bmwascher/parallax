Panel round 4 (your round 12). THE SUBJECT REVISION HAS MOVED AGAIN.

New head: `89ef9c4`
Fix range: `42c942143b7c3d1c319e407c542991bb8fa0637c..89ef9c4`
Branch base unchanged: `e2e9242c6153d69e9a4f0c49055e7bf8c81a1dd0`

Your round-11 FIX has been applied. A terminal verdict counts only when
it cites the new head.

## Your two findings

**Fix 2 / nested skills container — applied, and CONVERGENT.** Another
lane raised the identical defect in the same round, blind to yours. I
reproduced it on BOTH hosts through the built functions before fixing:
raw opener True, structural opener False, `BlockPresent` False, entries 0.

I took a STRICTER rule than either of you proposed. You suggested
detecting an ordered exact raw open/close pair; the other lane suggested
requiring the full signature including `### Available skills`. The
applied rule is the ordered pair alone, with no `### Available skills`
requirement, because it blocks strictly more and the extra blocking is on
the fail-closed side. Say if that reasoning is wrong.

**Fix 4 / global AGENTS.md — applied.** Both halves were measured on this
machine first: a directory named `AGENTS.md` answered a bare `Test-Path`
True, and a real `home[1]/AGENTS.md` answered False bare and True
literal. It now uses `-LiteralPath` with `-PathType Leaf`, and a file
that exists but cannot be resolved BLOCKS rather than reporting absent.

Both accepted limits you asked for are recorded in the design.

## One more fix, from the other lane

`Get-FeatureReport` still tested raw text, so a global `AGENTS.md` naming
`<apps_instructions>` in prose blocked with "the plugin or apps feature is
advertising itself" — the same defect class as the skills marker, one
function away, left behind because the earlier fix went only to the
function that had been named. The feature markers now use the QUIET mask,
chosen over the validating one so this check cannot pre-empt the
unknown-surface scan's own error.

## Evidence (verify, do not trust)

- Both hosts: 428 passed / 1 skipped.
- Live probe both hosts: exit 0, clean, 29 -> 0, `global_agents_md` true,
  `project_agents_md` false, override sha256 unchanged at
  `180f09f50d282b5603f1c0d0621f2913ff66c8b7798e7a2f3b7fe8d41f432bb8`.
- The probe was reverted to the previous commit and the four new cases
  re-run against it; each failed for the reason it exists.

## Your task this round

1. Verify the three fixes at the code.
2. **The pattern to break.** Every round of this cycle but one has found
   the previous round's fix carrying the next round's defect, and the last
   two rounds were both defects inside a fix. Attack these three the same
   way. The raw-pair rule is the highest-risk one: it reintroduces a raw
   text test into a function whose whole point was to stop reading raw
   text, so ask what a raw pair now blocks that should not block, and what
   a masked-and-paired shape still hides.
3. The quiet mask on the feature check: can a real plugins or apps
   container now go unseen, in any container arrangement?
4. Terminal verdict against head `89ef9c4`.

Cite `path:line`. Anything you did not check goes under `## Unverified`.
