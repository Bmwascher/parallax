# Mode-diff debate, round 6: the confirming round, second attempt

The user authorized one more exchange after reading that round 5 was not
dry. This is round 6 of 6. Same rules, same bar: an honest PASS is worth
more than a manufactured finding, and if you reach FIX, separate what
blocks merge from what is follow-up.

New head is `150886b` and the mirror was rebuilt at the same path from
it. Five days have passed since round 5; nothing in the tree changed in
that time except the two commits applying your round-5 findings and the
authorization note.

## What I changed from round 5

**Blocker 1, the 8.3 character set.** The basename and extension are now
restricted to the documented legal DOS set - letters, digits, and
`$ % ' - _ @ ~ ` ! ( ) { } ^ # &` - alongside the length bounds. Your
five names are in `test_names_that_8_3_cannot_produce_are_accepted`.

One measurement changed that test's shape. `a[b]~1` passes the guard and
then robocopy exits 16 on a bracketed destination, so the build fails
for a reason unrelated to this guard. It is asserted at the guard only,
with the reason written beside it. Tell me if you think that is the
wrong call.

**Blocker 2.** The acceptance test calls `assert_built` for every name
that can build.

**Editorial.** The doubled-backslash paragraph is corrected IN PLACE with
a note saying why; the obsolete category-test explanation is deleted;
item 98 now says the guards narrow the alias class rather than close it
and points at item 99; the round-4 summary counts one legitimate-input
refusal and one suspected accepted alias.

**Item 99 is filed** for the tilde-free alias, on your adjudication. It
records the `fsutil` experiment nobody has been able to run.

Final gate: 167 passed and 1 skipped under BOTH hosts; all six CI tiers
clean with `pytest evals` at 2930 passed and 14 skipped.

## What I want from this round

1. **Verify the two blocker fixes.** The character class especially: is
   the set right, is it right in the extension as well as the basename,
   and does the PowerShell regex actually express it - the class contains
   `^`, `-`, `'` and a backtick, all of which need care inside a
   single-quoted PowerShell string and a character class.
2. **Is the `a[b]~1` handling defensible?** A guard test that stops short
   of `assert_built` for one case is a weaker test for that case. If you
   think the bracket limitation should be a filed item rather than a
   comment, say so.
3. **Check the in-place corrections.** You asked for them; confirm they
   say what the evidence supports and that no superseded sentence
   survives elsewhere.
4. **Final sweep, same classes.** Instances or an explicit none, and the
   shapes you searched.

## Output

Same format. If PASS, say what it rests on and what you did not check.
If FIX, blockers first, follow-up second, and I go back to the user.
