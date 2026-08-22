# Diff debate, round 2 — item 48 PowerShell 7 feasibility

Round 1 was your strongest work in this cycle. **I reproduced all eight
findings and accepted all eight.** None was refuted.

Head is now `f2db27c` (base `a3134dc`). Range for this round: `1bcf912..f2db27c`.

## Your finding 1, and what it forced

You predicted `7493` — and the 5585/1337/571 split — from a read-only
reimplementation of `survey.py`'s regex, digest, prefix and stale logic,
without executing anything. I ran the survey: exactly right.

You also identified the mechanism precisely: **retaining the review artifact
changed the input universe the review had measured.**

That made the deeper problem visible. The record was publishing a live
figure about a tree it is part of, so the figure is self-invalidating by
construction. It had been wrong four times before you caught the fifth. I
ruled that writing `7493` was the wrong fix, because a fifth number is stale
the moment anyone edits the branch — including the commit that fixes it.

**The fix is structural.** Every absolute count the record publishes about
its own survey or its own tree is now either commit-bound ("as measured at
commit `<sha>`", a historical statement no later edit can falsify) or an
invariant that `survey.py`'s exit code actually guarantees (`0 unclassified,
0 stale, 0 files not scanned`, exit `0`). The single "today" figure is
replaced by a commit-by-commit table, with cells that were never separately
measured marked exactly that way rather than back-filled with an invented
number. A convention paragraph states the rule next to the existing
line-number convention.

**Test that claim rather than reading it.** The live count has moved four
more times since you measured it — 7493, then 7495, 7497, 7498 during the
fix, and `7500` at this head. The record cites none of them as current. If
you can find any place where it still states a live figure about itself as
an "is", the fix was not structural and I want to know.

## The other seven

- **2 (path constraint).** Accepted, and it was my claim that was too wide,
  not the record's. **Nothing was edited.** Your distinction is the one I
  kept: the narrower NOTHING-IS-REPINNED claim holds — no runtime file
  modified, no test removed, all paths adds — while the literal path
  constraint does not hold branch-wide. The debate-round directory is where
  this repo puts debate records, so the files stay and my claim narrows.
- **3 (guard).** Fixed by narrowing the comment to state exactly what the
  code enforces, not by widening the tuple a third time. It now names the
  uncovered cases explicitly — `.BAT`, `.PSM1`, `.SH`, upper-cased
  `.PS1`/`.PY`/`.CMD` — records that `git ls-files 'docs/*'` has no such
  name in any case today, and calls itself a stated scope limit. I chose
  that direction because there is no broader claim left to overstate, so it
  cannot recur.
- **4 (`first_difference`).** Fixed with a `_MISSING` sentinel at
  `reexec/run.py:29`, used at `:180`. The probe was NOT re-run and
  `results.json` is untouched — I verified that in the diff. The record
  states the stored arms predate the fix and are unaffected because the
  child emits exactly three keys.
- **5 (`skill-evals.yml:74`).** Fixed, and the correction is stated rather
  than silently swapped.
- **6 (list format).** Fixed by restating the promise honestly — 83 rows,
  50 bullets, and why they differ — rather than splitting bullets.
- **7a (Ruling 10's cost).** I overruled myself. The cost is restated as
  what widening actually does: it adds hits needing classification and moves
  published counts; it does not invalidate keyed rows. The decision not to
  widen stands.
- **7b (blind-spot count).** `survey.py:67` now reads "TWO KNOWN MISSES ARE
  LEFT IN DELIBERATELY" and names both.
- **8 (Measurement 3 summary).** Fixed to say what the detail says: trap 3's
  coverage is this record's own Measurement 1, and it is one of the two
  covered traps, not one of the other three.

## What I want from this round

1. **Verify the structural fix by attacking it.** Not "is there a convention
   paragraph" but "is there any self-referential figure it does not cover".
   Row totals, per-family counts, the classification table, anything in the
   residual or migration sections.
2. **Sweep the class again and name a ninth instance or report none
   explicitly.** Eight have been found; five of the eight were inside a fix
   for the previous one. The base rate here is not low.
3. **Re-check the seven fixes above against source.** Particularly 4 and 7b,
   where I changed executable code and a load-bearing comment.
4. Your citation sample was 39 of 40. If you sample again, tell me the
   denominator.

## Standing constraints on this branch

The record and its directory are the only editable surface; the backlog file
is edited at merge, not here. The verdict is CONDITIONAL on five conditions
and you confirmed that adjudication is correct — challenge it if you have
changed your mind, but it is not in question from my side.

End with **PASS**, **FIX**, or **ESCALATE**.
