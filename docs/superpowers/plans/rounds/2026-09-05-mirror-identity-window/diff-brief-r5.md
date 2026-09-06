# Mode-diff debate, round 5: the confirming round

Last of the five exchanges the user authorized. This is the round where a
dry result means something, and I would rather have an honest PASS than a
finding produced to justify the dispatch. If the work is done, say so.

New head is `7cc9e6f` and the mirror was rebuilt at the same path from
it.

## What I changed from round 4

**Finding 1, the source root's ancestors.** `Test-PathOrAncestorIsLink`
now runs on `$RepoRoot` before the destructive operations, alongside the
walks the other operands already had.
`test_a_repo_root_beneath_a_directory_link_is_refused` builds a real
junction above the source and asserts both the refusal and that the
source survives it.

**Finding 2, the 8.3 shape, third attempt.** Bounded to what 8.3 can
actually produce: basename at most eight characters, no space, tilde then
digits, optional extension of at most three. Two tests, both directions.
`test_names_that_8_3_cannot_produce_are_accepted` covers your
`backup~2026`, `ABCDEF~123456` and `a b~1`;
`test_real_short_name_shapes_are_still_refused` covers `MULTI-~1`,
`ABCDE~10`, `ABCD~100` and `PXD1~1.SOU`.

**Finding 3, the tilde-free short alias.** Not fixed, and I want you to
tell me whether leaving it is defensible. It is written into the helper's
own comment as a stated limit: `fsutil file setshortname` can assign
`LONGFILE.TXT` to `longfilename.txt`, no pattern over spelling can
distinguish that, so refusing tilde forms narrows the class without
closing it. I did not file it as a backlog item. Should I?

**Findings 4 through 7, my four overstated claims.** All narrowed:
- the doubled-backslash account now says interior backslash-separated
  component checking was lost, not that every check was dead, and drops
  "nothing else would have caught it" because the dotted-ancestor
  regression exercises exactly that
- the followed-target comment now says "before the destination-overlap
  comparisons"
- the stream-root docstring now records that `Test-Path` returns TRUE on
  both hosts and that the colon rule is the only demonstrated mechanism
- both fixture tests now read the sidecar back and require the codepoint
  present and the literal escape absent
- item 98 and the debate record now attribute the both-host removal
  simulation to round 4, not round 3
- the ordinals are gone from the oracle comments
- the round-1 account names the runtime-category test

Gate: 167 passed and 1 skipped under BOTH hosts, full `pytest evals` 2930
passed and 14 skipped, backlog lint clean, script pure ASCII.

## What I want from this round

1. **Verify the two code fixes.** The source-root ancestor walk and the
   bounded 8.3 shape. The shape has now been wrong three times, so check
   it in both directions again rather than trusting that the third
   attempt is the charm.
2. **Does the source-root walk break a legitimate build?** Plenty of
   people keep repositories under a junctioned path - `My Documents` is
   the example you used, and it is on this machine. If an ordinary
   checkout under an ordinary junction now cannot be mirrored at all,
   I have traded a reachability bug for a usability wall, and I would
   rather know that now than after merge.
3. **Adjudicate finding 3.** Leave as a stated limit, or file it?
4. **Check my seven corrections** actually say what the evidence
   supports, and are not a fresh set of overclaims in the other
   direction. Four of your round-4 findings were about my record, so this
   is the obvious place for me to have overcorrected.
5. **Final sweep.** Same classes. Instances or an explicit none, and the
   shapes you searched.

## Output

Same format. If PASS, say what it rests on and what you did not check. If
FIX, I have no budget left and would have to go back to the user for it,
so please be clear about which findings are merge-blocking and which are
follow-up work that belongs in the backlog.
