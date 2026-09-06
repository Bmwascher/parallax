# Mode-diff debate, round 2: rebuttal and fix-verify

Same debate, same rules. Your round 1 produced five confirmed findings
and I applied all five. One of them I am contesting in part, with a
measurement, and I want you to check my measurement rather than concede
to it.

The tree has MOVED since round 1. New head is the commit
`apply diff debate round 1: refuse trailing dot destinations, harden two
oracles, narrow three record claims`. The mirror you are working in was
rebuilt at the same path from that head, so what you read now is the
fixed tree, not the one you reviewed.

## Finding 1: I am contesting the CONSEQUENCE, not the defect

You reported the trailing-dot bypass as reaching recursive deletion of
the source, having executed the construction prefix on both hosts with
`Remove-Item` replaced by a harmless interceptor.

I measured what your interceptor stood in for. On BOTH Windows PowerShell
5.1 and PowerShell 7, with a real directory and a real file inside it:

- `Test-Path` on the dotted path returns True.
- `Remove-Item -LiteralPath <dotted> -Recurse -Force` throws
  `PSArgumentException` and deletes NOTHING.
- `Remove-Item <dotted> -Recurse -Force`, the non-literal form, throws
  the same and deletes nothing.
- The directory and the file inside it both survive.

So the deletion call is REACHED and cannot delete. Your probe established
reachability; substituting the interceptor is exactly what made the
difference invisible to it. I think the round 1 wording claims more than
the evidence supports, in the same way finding 3 caught me doing.

**I am not disputing that the guard is broken.** The removal failure is
non-terminating, this script never sets `$ErrorActionPreference`, so the
build continues and constructs a mirror at a path naming the tree under
review. That is a real defect with a real consequence, and it is
pre-existing rather than introduced by this branch - the same class the
branch had already closed for `-ExtraInput` and left open on the
destructive path.

**Check this.** If you can produce a real deletion through that path on
either host, without an interceptor, say so and I will withdraw the
rebuttal. If you cannot, I want you to say that too, plainly.

## What I changed

**Finding 1.** A spelling guard now runs BEFORE the overlap comparison,
on BOTH operands, since both are user-supplied. Any path component ending
in a dot or a space is refused, exiting 2, with `.` and `..` excluded.
Two tests: `test_a_mirror_path_with_a_trailing_dot_is_refused`, which
also asserts the source survives, and
`test_a_repo_root_with_a_trailing_space_is_refused`.

**Finding 2.** Both weak oracles now assert positively. The
control-character test requires the WHOLE rendered name, so a doubled
prefix or a mangled remainder fails it. The category test requires the
whole escaped name. Both also assert `unknown` is absent, which is what
closes the fallback path you identified.

**Finding 3.** `BACKLOG.md` item 93 and `gate-results.md` now say only
that the slowdown did not reproduce in three runs, that the cause is
unknown, and that no candidate is favoured or excluded. The claims "item
90 did not close a gap" and "not a property of the tracked tree" are
gone.

**Finding 4.** The README now says "the reviews missed them;
implementation exposed them", and records that an earlier draft claimed
impossibility and that you struck it.

**Finding 5.** The stale trailing-newline comment is gone.

Gate after the fixes: 156 passed, 1 skipped under BOTH hosts; backlog
lint clean; the script still pure ASCII.

## What I want from round 2

1. **Verify each of the five fixes against the code, not against this
   summary.** A fix that does not do what its description says is worth
   more to me than a new finding.
2. **Adjudicate finding 1's consequence.** Named above.
3. **Attack the NEW guard specifically.** It is the newest code in the
   tree and nothing has reviewed it. Is the component split right? Does
   it refuse anything legitimate - a UNC path, a drive-relative path, a
   path with a trailing separator already stripped elsewhere? Can a
   spelling still reach the overlap comparison that names a directory
   other than what it compares as? I am thinking specifically about `..`
   segments, short 8.3 names, and alternate data stream syntax, none of
   which I checked.
4. **Continue the class sweep.** Same instruction as round 1: instances
   of the CLASSES, or an explicit none, plus the shapes you searched.
   Negative-only oracles are now a known class in this tree - are there
   others beyond the two you found?

## Output

Same format. Numbered findings, CONFIRMED or SUSPECTED, file and line for
every claim, and a verdict of PASS, FIX or ESCALATE with one sentence on
what it rests on. If the fixes hold and the sweep is empty, PASS is the
honest answer and I would rather have it than a manufactured finding.
