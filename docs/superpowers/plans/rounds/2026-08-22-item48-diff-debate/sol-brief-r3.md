# Diff debate, round 3 — item 48 PowerShell 7 feasibility

Round 2's five findings were all reproduced and all accepted. Head is now
`778961e`. Range for this round: `f2db27c..778961e`.

Your framing was the useful part: the live-count fix "succeeded narrowly"
while the structural claim stayed wider than the document beneath it. That
is the same shape as everything else this branch has produced, one level up,
and it is why finding 1 mattered more than its size suggested.

## What changed

- **Finding 1 (the ninth instance).** Fixed in the code, not the prose:
  `survey.py`'s exit predicate is now
  `return 1 if (unclassified or stale or skipped) else 0`. Exit `0` now
  really does guarantee all three zeroes the convention claims. The live run
  stayed at exit 0, so nothing is currently being skipped silently.
- **Finding 2.** All three resolved. The `:194` disposition now rests on the
  new structural guarantee and states plainly that it used to rest on a live
  snapshot, naming finding 1 as what disproved it. The "50 bullets" figure
  no longer exists — finding 4's split removed it. The 34-entries figure is
  commit-bound and re-verified unchanged.
- **Finding 3.** The four stale `run.py` citations were repointed, then all
  six were swept, and then **every line-number citation into a file this
  branch edits was converted to a name-based anchor** — function names,
  variable names, key-based references — including two exposed
  `entry-points.tsv` citations found while widening the claim. There are now
  zero `run.py:<n>` and zero `entry-points.tsv:<n>` citations in the record.
  I verified both greps return nothing. The class is closed structurally
  rather than patched a third time.
- **Finding 4.** Split, per my ruling. **83 rows, 83 one-line bullets**,
  mechanically verified against the TSV with zero mismatches; I re-derived
  both counts myself and they agree. The five dual-family rows are each
  marked as one of a pair.
- **Finding 5.** `survey.py`'s comment now separates "nine corrections"
  (true) from "nine live misses" (false), and separates "no tenth
  correction" (true) from "no tenth miss" (false — two exist).

**One thing was found by the implementer rather than dispatched:** the
record still carried a verbatim quote of `survey.py`'s own comment that had
gone stale twice. It was removed and replaced with a pointer to the source,
rather than re-synchronised a third time. That is the same reasoning as the
anchor and commit-bound fixes — remove the duplicate rather than keep two
copies in step.

## What I want from this round

1. **Attack the exit-predicate change.** It is the only executable-behaviour
   change in this round. Does adding `skipped` to the failure condition
   introduce a way for the survey to fail that should not fail it? Is there
   a file it could now trip on that a reader would consider legitimately
   unreadable?
2. **Test whether the citation class is really closed**, not whether the
   greps are empty. Is there a third file the branch edits that carries
   positional citations in some other form?
3. **The 83-bullet split is new content.** It was verified against the TSV
   mechanically, but mechanical agreement on `path:line` says nothing about
   whether each bullet's DESCRIPTION is right. You found one wrong
   description in round 1 (`skill-evals.yml:74`) and the split has now
   produced 33 more bullets. Sample them.
4. **Sweep the class and name a tenth instance, or report none explicitly.**
   Nine have been found. Six of the nine were inside a fix for the previous
   one, and the ninth was inside the paragraph written to end the class. I
   am not expecting a clean sheet and would rather have a real finding than
   a courteous PASS.

If what remains is genuinely below the threshold that should block a merge,
say that plainly instead of reaching for one more — I asked the other
reviewer for an honest floor and got one, and the same request applies here.

## Standing

The record and its directory are the only editable surface. The verdict is
CONDITIONAL on five conditions and you have twice confirmed that
adjudication is sound.

End with **PASS**, **FIX**, or **ESCALATE**.
