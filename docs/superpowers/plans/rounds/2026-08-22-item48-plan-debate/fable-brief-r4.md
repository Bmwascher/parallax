# Debate brief - round 4 - mode plan - Fable lane

## Continuity check, answer FIRST

Neither answer is in this message.

1. Your continuity nonce, verbatim.
2. In round 3 you named one live entry-point shape that the filter still dropped, and you said it belonged in a DIFFERENT family than the one that had just been widened. Name the cmdlet, the file:line you cited, and which family you said it belonged in.

If you cannot answer both from memory of your own earlier rounds, say so plainly rather than reconstructing.

## Subject revision

Plan file at commit `7b8ce9c`, branch `item51-inline-brief-transport`. Re-read it. The only change since `54217cb` is the debate-record block recording the budget below.

  docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md

**Budget, declared by the user after round 3, and stated here because the protocol requires it be declared before round 1 and it was not: three further rounds. If both lanes have not returned PASS by round 6, the debate pauses and returns to the user. It never converts into a verdict.**

## Disposition of round 3

All ACCEPTED and applied. Nothing refuted, nothing struck.

CONVERGENT:
1. The explicit-row rule had a fail-open oracle: `--emit` prints only UNCLASSIFIED matches, and a prefix-covered match is not unclassified, so the check written to prove the rows existed printed zero either way. That check was itself written while fixing a fail-open gate. Fixed STRUCTURALLY: `survey.py` now carries `EXEMPT_FROM_PREFIX` listing this plan and the record directory, so no prefix row covers them and a missing row is an ordinary red. Verified by running it against three cases including the negative one.
2. Task 7 never got the step Task 4 got — your finding, and the same asymmetry the standing rule existed to remove. Task 7 has it now, and the text says why it must live in the task: a subagent-per-task dispatch never shows Task 7 Task 3's prose.
3. Two stale cross-references from the round-2 rewrites: Task 9's "Step 2" for the test-matrix answer after the reorder moved it to Step 3, and Task 4's table still asking for `bound_exact` after the rename. Both corrected.

Single-lane, verified, applied:
4. `Start-Job` joins the LAUNCH family, exactly where you said it belonged. 4 hits measured.
5. Backticked invocations whose flags wrap to the next line: `backup-lane.md:119`, `:136`, `:141`. Added, 3 hits measured.
6. `run_named` treated an unparseable child JSON as a failed COMPARISON, filing an arm that measured nothing as evidence toward a NO. Now a broken arm that fails the run.
7. `stage_a_parent_count` and `stage_b_child_count` returned `len(NAMED)` whenever the file merely existed — your "sent count wearing a received count's name". Now count what came back, or `None`.
8. The `TimeoutExpired` path returned bare, so `main()` exited 0 over the defect it exists to catch. Now returns 1; `probe.py` ends with `raise SystemExit(main())`.
9. Task 6's extraction read 25 lines of a job whose host steps sit at `.github/workflows/skill-evals.yml:93-125`. Now an awk range over the whole job, plus a read of the same job at the cited run's `headSha` so the module list and the green run share a revision.
10. Task 6's "Only `runs` rows count as behaviour proven under a host" reworded: a `runs` row says the module INVOKES the script; the green run adds the passing half.
11. Task 4 Step 7 pre-wrote the classification for rows nobody had read, against Task 3's own rule. Reworded as what to expect to find, not what to write.
12. Task 2's stated final survey line omitted the `files not scanned` field and the `FAMILY` lines. Corrected.
13. The filter's miss-count was stated three ways. All now read: across three review rounds the filter was widened FIVE times, each because a reviewer produced a live entry point it did not match.
14. Task 5's awk range also picks up the comment block at `.github/workflows/skill-evals.yml:49-58`. The step now says to read the hits before counting them.

## What was RUN rather than read

Every python block the plan ships was extracted and executed: the scanner against this repo (5186 matches, 4286 prefix-covered, 900 needing hand rows — 167 host, 277 launch, 456 bare, and the plan's stated counts are now those numbers); all 16 entry points either lane has named, every one caught; `EXEMPT_FROM_PREFIX` against three cases; `load_rows` duplicate refusal against four; and both probe drivers for syntax and exit contract.

## What I want from this round

A. Sweep round 3's amendments for the class. Third time asking, and it produced the round's worst finding twice running. Fourteen more things changed. Name each instance with a line reference, or report explicitly that you found none.

B. `EXEMPT_FROM_PREFIX` specifically. It moves a rule from prose into code. Can it fail open? Can it fail CLOSED in a way that blocks the plan? Does it interact wrongly with the per-family split, with `--emit`, or with the stale check?

C. The filter, again. Six widenings so far, each prompted by a reviewer producing a live instance. Produce a seventh with a file:line, or report none found and say which shapes you looked for.

D. Anything else.

End with exactly one verdict line: PASS, FIX, or ESCALATE. **If the plan is sound, PASS is the correct answer and one line is the right length.** Do not manufacture objections to justify the round, and do not withhold PASS because three rounds preceded it. Do not concede a point you can refute.