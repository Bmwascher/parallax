# Mode-diff debate, round 3: the confirming round

Third and last of the declared budget of three. Same rules.

The tree has moved again. New head is the commit `apply diff debate round
2: refuse alias spellings on all three operands and fix the third
negative oracle`, and the mirror was rebuilt at the same path from it.

Thank you for the round 2 withdrawal. Getting a destructive claim
narrowed to what the evidence supported is worth the round it cost, and
you did it without being pushed twice.

## What I changed from round 2

**Finding 1, the alias spellings.** The guard now refuses three more
forms, each with its own message, on every operand:

- device prefixes, refused on the whole string: a path beginning `\\?\`
  or `\\.\`
- NTFS stream syntax: any path containing `::`
- 8.3 short names, refused per component: a component matching `~[0-9]+$`
  or `~[0-9]+\.[^.]{1,3}$`

I took your framing rather than trying to establish identity: this tool
will not open a handle on a destination it is about to delete, so it
refuses what it cannot resolve, the same stance it already takes for
directory links.

Three tests, one per form: `test_a_short_name_component_is_refused`,
`test_a_stream_form_path_is_refused`,
`test_a_device_prefixed_path_is_refused`. The short-name test also
asserts the source survives.

**Finding 2, the missing operand.** The guard now builds a SUBJECT LIST
and appends the override when one is supplied, rather than naming two
operands inline. The test is
`test_an_override_inside_the_source_through_a_dotted_ancestor_is_refused`
and its docstring says why it exists as a test rather than a one-line
addition: guarding operands one at a time is how this class survived
being fixed once already. You caught me repeating inside my own fix the
exact mistake you had just found in the original code.

**Finding 3, the third negative oracle.**
`test_an_unmeasurable_expected_digest_is_refused` now requires exit 1 and
the string `recorded mirror state hash is missing or malformed`, so exit
2 with empty stdout no longer passes.

Gate: 160 passed and 1 skipped under BOTH hosts, full `pytest evals` 2923
passed and 14 skipped, backlog lint clean, script still pure ASCII.

## What I want from round 3

This is the confirming round, so the bar is different: I am looking for a
DRY round, and if the work is done I would rather have PASS than a
finding manufactured to justify the dispatch.

1. **Verify the six fixes against the code.** Particularly the guard, and
   particularly whether my three new refusal patterns are right in BOTH
   directions - do they refuse everything they should, and do they refuse
   anything legitimate? The 8.3 regex is the one I trust least. A real
   directory can legitimately contain a tilde and digits.
2. **Is the subject-list shape actually complete?** I added the override.
   Are there other destination or protected operands this tool writes to,
   deletes, or compares, that are still outside the guard? That is the
   question that has now caught me twice, so I would rather you answer it
   than me.
3. **One thing I did NOT do,** and I want your read on whether it matters:
   the guard refuses spellings, but the reachability you demonstrated
   depended on the removal failure being non-terminating. I did not add
   an error check after `Remove-Item`, because it is outside this
   branch's scope and I did not want to widen it silently. Is leaving
   that unchecked a defect worth filing, or is refusing the spellings
   sufficient?
4. **Final class sweep.** Negative-only oracles, guard operand omissions,
   spelling-versus-identity comparisons, measurement overclaims. Instances
   or an explicit none, plus the shapes you searched.

## Output

Same format. If you reach PASS, say what the verdict rests on and what
you did NOT check, so the record shows the shape of the remaining
uncertainty rather than implying there is none.
