# Debate brief - round 4 - mode plan

Subject revision: the plan file at commit `7b8ce9c` on branch
`item51-inline-brief-transport`. Re-read it. (The only change since the
blob you may have read at `54217cb` is the debate-record block at the end,
recording the budget below.)

  docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md

**Budget, declared by the user after round 3 and stated here because the
protocol requires it be declared and it was not declared before round 1:
three further rounds. If both lanes have not returned PASS by round 6 the
debate pauses and returns to the user. It never converts into a verdict.**

Panel round. Findings relayed anonymously; CONVERGENT means both lanes
raised it independently.

## Disposition of round 3

All ACCEPTED and applied. Nothing refuted, nothing struck.

CONVERGENT:

1. **The explicit-row rule had a fail-open oracle.** `--emit` prints only
   UNCLASSIFIED matches, and a prefix-covered match is not unclassified, so
   the check written to prove the rows existed printed zero either way.
   That check was itself written while fixing a fail-open gate.
   **Fixed structurally, not by instruction:** `survey.py` now carries
   `EXEMPT_FROM_PREFIX`, listing this plan and the record directory. No
   prefix row covers them, so a missing row is an ordinary UNCLASSIFIED
   red. Verified by running it: a record-directory script is not
   prefix-covered, this plan is not prefix-covered, an ordinary `docs/`
   file still is.
2. **Task 7 never got the step Task 4 got** — the same asymmetry the
   standing rule existed to remove. Task 7 now has it, and the rule text
   says why it must be in the task rather than in Task 3's prose: a
   subagent-per-task dispatch never shows Task 7 that prose.
3. **Two stale cross-references** from the round-2 rewrites: Task 9 cited
   the test-matrix answer as "Step 2" when the reorder moved it to Step 3,
   and Task 4's table still asked for `bound_exact` after the field was
   renamed `stage_b_child_exact`. Both corrected.

Single-lane, verified, applied:

4. `Start-Job` was in no family. It spawns a child of the CURRENT host, and
   `tools/check-drift.ps1:1054` is the job the codex dispatch runs inside,
   so that line decides which host the background dispatch child gets. It
   is now in the LAUNCH family. Measured cost: 4 hits.
5. A backticked invocation whose flags WRAP to the next line leaves the
   `.ps1` at end of line with no flag after it, so no alternative matched.
   Three live instances at `backup-lane.md:119`, `:136`, `:141`. Added.
   Measured cost: 3 hits.
6. `run_named` treated an unparseable child JSON as a failed COMPARISON,
   so an arm that measured nothing about argument fidelity was filed as
   evidence toward a NO. It is now a broken arm and fails the run.
7. `stage_a_parent_count` and `stage_b_child_count` returned `len(NAMED)`
   whenever the output file merely existed — a SENT count wearing a
   RECEIVED count's name, in the NO-arm's own results file. They now count
   what came back, or report `None`.
8. The `TimeoutExpired` path added in round 2 wrote its result and returned
   bare, so `main()` exited 0 over the defect that path exists to catch.
   Now returns 1, and `probe.py` ends with `raise SystemExit(main())`.
9. Task 6's workflow extraction read 25 lines of a job whose host steps sit
   at `.github/workflows/skill-evals.yml:93-125`. Replaced with an awk
   range over the whole job, plus a step that reads the same job at the
   cited run's `headSha` so the module list and the green run are the same
   revision.
10. Task 6 still said "Only `runs` rows count as behaviour proven under a
    host" beside its own correction. Reworded: a `runs` row says the module
    INVOKES the script; the green run adds the passing half.
11. Task 4 Step 7 pre-wrote the classification for rows nobody had read,
    against Task 3's own non-negotiable rule. Reworded as what you should
    expect to find, not what to write without looking.
12. Task 2's stated final survey line omitted the `files not scanned`
    field the code prints, and the `FAMILY` lines. Corrected.
13. The filter's miss-count was stated three different ways across the
    artifacts. All now say the same thing: across three review rounds the
    filter was widened FIVE times, each time because a reviewer produced a
    live entry point it did not match.
14. Task 5's awk range also picks up the comment block at
    `.github/workflows/skill-evals.yml:49-58`, which discusses `pwsh` in
    prose. The step now says to read the hits before counting them.

## What was RUN rather than read, this round

Every python block the plan ships was extracted and executed:

- the scanner against this repo: 5186 matches, 4286 prefix-covered, 900
  needing hand rows — 167 host, 277 launch, 456 bare. The plan's stated
  counts are now those numbers.
- all 16 entry points either lane has named: every one caught.
- `EXEMPT_FROM_PREFIX` against three cases, including the negative one.
- `load_rows` duplicate refusal against four cases: duplicate explicit row,
  duplicate prefix row, the new `not-a-launch` value, and a legitimate
  two-family pair for one line.
- `run.py` and `probe.py`: syntax, and that both end in
  `raise SystemExit(main())`.

## What I want from this round

A. **Sweep round 3's amendments for the class.** Same ask, third time, and
   it has produced the round's most serious finding twice running: round 2
   found seven fixes carrying the defect they fixed, round 3 found a
   fail-open check written while fixing a fail-open check. Fourteen more
   things changed. Name each instance with a line reference, or report
   explicitly that you found none.

B. **`EXEMPT_FROM_PREFIX` specifically.** It is the round's structural
   change and it moves a rule from prose into code. Can it fail open? Can
   it fail CLOSED in a way that blocks the plan? Does it interact wrongly
   with the per-family split, with `--emit`, or with the stale check?

C. **The filter, again.** Six widenings so far, every one prompted by a
   reviewer producing a live instance. Produce a seventh with a file:line,
   or report none found and say what shapes you looked for.

D. Anything else.

## Rules for your reply

- End with exactly one verdict line: PASS, FIX, or ESCALATE.
- **If the plan is sound, PASS is the correct answer and one line is the
  right length.** Converging is the system working. Do not manufacture
  objections to justify the round, and do not withhold PASS because three
  rounds preceded it.
- Do not concede a point you can refute.
- Quote the line and give its number for every externally checkable claim.
