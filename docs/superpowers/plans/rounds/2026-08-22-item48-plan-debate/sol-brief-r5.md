# Debate brief - round 5 - mode plan

Subject revision: the plan file at commit `ff34793` on branch
`item51-inline-brief-transport`. Re-read it.

  docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md

Budget: three rounds were authorized after round 3. This is the second of
them. If both lanes have not returned PASS by round 6, the debate pauses
and returns to the user; it never converts into a verdict.

## Disposition of round 4

CONVERGENT, and the round's most serious finding:

1. **The exemption could not fire for the two tasks it was written for.**
   `survey.py` reads `git ls-files`, which lists TRACKED files only, and
   Tasks 4 and 7 ran their `--emit` check BEFORE staging the files they had
   just created. An invisible file and a fully classified one produce the
   identical empty output. Both tasks now `git add` first and assert
   `git ls-files <dir> | wc -l` is nonzero before the emit result is
   trusted. **That was the third fail-open gate in this plan, each written
   while closing the previous one**, and the pattern is now recorded in the
   plan text itself.

Accepted from one lane, verified:

2. The exemption reached too far. It covered `feasibility-record.md`, which
   is genuinely a record, never executed, and which GROWS through Tasks 4
   to 8 — so rows keyed to its line numbers would go stale on the record's
   own prose and block Task 9 for a reason that is not an entry point.
   `NOT_EXEMPT` now excludes that file and `entry-points.tsv`. This also
   resolves the other lane's finding that the standing rule's "matching
   LINE" half had no task carrying it: those lines are prefix-covered as
   `record`, which is what they are.
3. Two more filter shapes, both live: a generic call operator with a
   literal command (`& git -C ...`, `tools/new-kimi-lane-home.ps1:691`) and
   bare `python` (`tools/check-drift.ps1:983`, the pytest gate the
   autotriage flow trusts). The plan's own vocabulary named python and git
   as `launch-nonhost` examples while the filter could not produce such a
   row.
4. **One miss kept deliberately, with its instance named.** Bare `git`
   stays unmatched: 179 further hits, and it starts no PowerShell host. The
   trade and its live instance, `tools/check-drift.ps1:987`, are written
   into `survey.py`'s comment and into the blind-spot list, rather than
   left as an implied empty set.
5. The widening count was stale in the commit that standardized it. It now
   reads EIGHT corrections across four rounds, enumerated.
6. `probe.py` continued past a failed PATH strip and could still exit 0.
   It now returns 1 before invoking anything.
7. The timeout write-up blamed a blocked stdin read that
   `stdin=subprocess.DEVNULL` rules out. Reworded.
8. Task 6 called its CI run "the only evidence that anything PASSED under
   PowerShell 7" while Task 4 runs four `pwsh7` arms. Narrowed to the
   shipped test modules.
9. "A line matching both families produces TWO rows" said two while the
   scanner had three. Now one row per family matched, up to three.
10. Untracked files are invisible to `git ls-files`; the auto-triage
    wrapper scripts under `tools/drift-reports/` are the live example and
    are now named in the blind-spot list.

**One finding was REFUTED, not applied.** A lane reported that the Task 2
Interfaces block still specified the old survey line without the
`files not scanned` field. It does not: that block already lists the
`FAMILY` lines and the full final line. The correction had been applied at
both sites.

## Run, not read

6346 matches, 981 hand rows — 168 host, 277 launch, 536 bare. All 18 entry
points either lane has named across four rounds are caught. The declared
miss is still missing. Five exemption cases pass including three negative
ones: the record file and the TSV ARE prefix-covered, an ordinary `docs/`
file IS, a record-directory script and this plan are NOT. Duplicate refusal
still holds, and a legitimate three-family row set for one line is
accepted.

## What I want from this round

A. **Sweep round 4's amendments.** Fourth time asking; three of the four
   rounds so far found their worst defect inside the previous round's
   fixes. Name each instance with a line reference, or report explicitly
   that you found none.

B. **`NOT_EXEMPT` and the staging fix specifically.** Between them they
   changed which matches are classified by hand and when a check can see a
   file. Can either fail open? Can either fail closed and block the plan?

C. **The filter, an eighth time.** Produce a live instance with a
   file:line, or report none found and say which shapes you looked for.
   Note that bare `git` is a DECLARED miss, so it does not count.

D. Anything else.

## Rules for your reply

- End with exactly one verdict line: PASS, FIX, or ESCALATE.
- **If the plan is sound, PASS is correct and one line is the right
  length.** Four rounds preceding it is not a reason to withhold it. Do not
  manufacture objections; do not concede a point you can refute.
- Quote the line and give its number for every externally checkable claim.
