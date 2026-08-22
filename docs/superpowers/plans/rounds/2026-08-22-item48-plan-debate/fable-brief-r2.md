# Debate brief - round 2 - mode plan - Fable lane

## Continuity check, answer FIRST, before anything else

Two questions. Neither answer appears anywhere in this message, so echoing it back will not produce them.

1. State your round 1 continuity nonce verbatim.
2. In your round 1 section A you called one task "the strongest task in the plan". Which task number was it, and in one clause, why did you say so?

If you cannot answer both from your own memory of round 1, say so plainly instead of reconstructing. A lost resume is a lane failure that gets recorded, not something to paper over.

## Subject revision, pinned

The plan file at git blob `e2a87c41b697588ba66c8f41fd3588030977095c`, commit `4efc7b9` on branch `item51-inline-brief-transport`. Re-read it; it changed substantially since round 1.

  docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md

This is a PANEL. Findings below are relayed anonymously and may be yours or the other lane's. CONVERGENT means both lanes raised it independently, which is the strongest signal this panel produces.

## Position changes since round 1

All ACCEPTED. Nothing refuted, nothing struck. Each was verified against the repo by the session before acceptance rather than taken on a reviewer's word.

CONVERGENT (both lanes, independently):

1. The NO-criteria oracle compared a 40-character prefix while the record claimed "Copied verbatim". Replaced with a whole-bullet comparison that rejoins wrapped lines and normalizes whitespace, plus a check that all ten record headings exist in order.
2. The blanket `docs/` prefix row classified as "never executed" the very scripts this plan executes. The row stays, with a required exception: explicit per-line rows for every match inside the record directory, which already win over prefix rows in the existing code path.
3. Task 6's glob omitted `hooks/superpowers-review-companion.ps1`, the one shipped script already running under PowerShell 7 (hooks/hooks.json:10, :22). Added `hooks/*.ps1`; the phrase "the 13 shipped scripts" is deleted.
4. Task 5 ordered an unmeasured universal claim about what a stock Windows install carries. It must now be cited to Microsoft documentation with a URL and date, or labelled "background knowledge, not measured here" with what would prove it.
5. Task 9 could reach YES over unmeasured ground. It gains an UNKNOWN state; UNKNOWN can never produce YES; a `migration=unknown` row bearing on criterion 1 forces CONDITIONAL by name; every material residual must be explicitly dispositioned.

Single-lane, verified, accepted:

6. `survey.py` scans `git ls-files` and its own source contains every literal in all three families, so a count taken before it is tracked cannot be reproduced after. Task 2 now COMMITS BEFORE MEASURING and says why.
7. CI evidence read the working tree while citing a historical run. Task 5 now reads the workflow at the run's own `headSha`, and records the evidence as revision-unbound if that SHA is not local.
8. Whole-job durations cannot isolate the 5.1 cost; the two hosts are separate sequential steps at `.github/workflows/skill-evals.yml:93` and `:110` and the job also pays for shared setup. Task 8 now pulls STEP timings, reports GROSS saving, and states NET is not determined there.
9. The missing-pwsh probe invoked `pwsh -Command Write-Output ok` while claiming to capture what a user would see. It now uses the hook's own `-File` shape and says the harness's own presentation was not measured.
10. Task 3 wrote `stubs.tsv` into the repo root, breaking this plan's first Global Constraint. It now writes to the scratchpad.
11. Two entry-point classes escaped both regex families. A THIRD family was added; all four known instances are now caught, verified by running the extracted scanner.
12. Task 4 claimed "arbitrary arguments" from ten fixed payloads, and its parent forwarded only positional `$args` while every shipped script declares named parameters (`tools/check-drift.ps1:30-34`). A named-parameter arm was added, `run.py` now exits nonzero when any arm measured nothing, and the claim is narrowed to the shapes tested.

## What the session found on its own

13. The third family as first drafted matched every `.ps1` mention and produced 5683 matches, 940 outside `docs/`. It was narrowed to INVOCATION shapes, measured again, and the narrowing is recorded in the script's own comment as a real narrowing rather than as an empty set. Current counts from running the extracted scanner: 3977 total, 3243 under the `docs/` prefix row, 734 needing hand rows, split 120 host / 241 launch / 373 bare.
14. Because 734 rows in one pass is how a survey stops being read, Task 3 is split by family, one subagent each, and `survey.py` prints a per-family `FAMILY <name>: <n> hits, <n> unclassified` line so each split task has its own oracle.
15. The mis-transcribed escaper you found had a cause worth naming: this environment's shell heredoc silently drops backslashes. It corrupted the committed probe record, and corrupted a regex again during today's amendments. Both were caught by RUNNING the code, not reading it. The probe record is corrected and now states that its first committed version printed a broken escaper.

## What I want from this round

A. Sweep the AMENDED plan for the same class: a claim stated more widely than its evidence, or an unmade measurement that reads like a clean one. Name each instance with a line reference, or report explicitly that you found none.

B. Sweep the AMENDMENTS THEMSELVES for that class. This is the ask that matters most. This repo's last three release cycles each reproduced the defect class they were fixing, inside their own fixes, and no author caught it. Twelve of the fifteen items above are new text written today. Treat them as the most likely place for a new instance, not the least.

C. The third regex family is narrowed to invocation shapes. Name a real entry point in this repo that the narrowing now drops, with a file:line, or report none.

D. Does splitting classification across three subagents create a seam where a row can be lost or double-written? The `FAMILY` line is the only oracle each split task has.

E. Anything else.

End with exactly one verdict line: PASS, FIX, or ESCALATE. If the plan is now sound, say so in one line; a round that converges is the system working. Do not manufacture objections, and do not concede a point you can refute.