# Debate brief - round 2 - mode plan

Subject revision, pinned: the plan file at git blob
`e2a87c41b697588ba66c8f41fd3588030977095c`, commit `4efc7b9` on branch
`item51-inline-brief-transport`. Re-read the file; it has changed
substantially since round 1.

  docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md

This is a PANEL. Findings below are relayed anonymously and may come from
you or from another lane. Where a finding was raised independently by more
than one lane it is marked CONVERGENT, which is the strongest signal this
panel produces.

## Position changes since round 1

Everything below was ACCEPTED. Nothing was refuted and nothing was struck.
Each was verified against the repo by the session before being accepted,
not taken on the reviewer's word.

CONVERGENT, raised independently by both lanes:

1. The NO-criteria oracle compared a 40-character prefix while the record
   claimed "Copied verbatim". REPLACED with a whole-bullet comparison that
   rejoins wrapped lines and normalizes whitespace, plus a check that all
   ten record headings exist in order.
2. The blanket `docs/` prefix row classified as "never executed" the very
   scripts this plan executes, including `survey.py` and the plan itself.
   The row remains, with a required EXCEPTION: explicit per-line rows for
   every match inside the record directory, which win over the prefix row
   in the existing code path.
3. Task 6's glob omitted `hooks/superpowers-review-companion.ps1`, the one
   shipped script already running under PowerShell 7 in production
   (hooks/hooks.json:10, :22). Added `hooks/*.ps1`, and the pre-committed
   phrase "the 13 shipped scripts" is deleted.
4. Task 5 ordered an unmeasured universal claim about what a stock Windows
   install carries. It must now be either cited to Microsoft's own
   documentation with a URL and date, or labelled "background knowledge,
   not measured here" with what would prove it.
5. Task 9 could reach YES over unmeasured ground. It gains an UNKNOWN
   state; UNKNOWN can never produce YES; a `migration=unknown` row bearing
   on criterion 1 forces CONDITIONAL by name; and every material residual
   must be explicitly dispositioned.

Raised by one lane, verified, accepted:

6. `survey.py` scans `git ls-files` and its own source contains every
   literal in all three families, so a count taken before it is tracked
   can never be reproduced after. Task 2 now COMMITS BEFORE MEASURING, and
   says why, because that inverts the usual order.
7. CI evidence read the working tree while citing a historical run. Task 5
   now reads the workflow at the run's own `headSha` via `git show`, and
   records the evidence as revision-unbound if that SHA is not local.
8. Whole-job durations cannot isolate the 5.1 cost: the job also pays for
   checkout, Python setup and pytest install, and the two hosts are
   separate sequential steps at `.github/workflows/skill-evals.yml:93` and
   `:110`. Task 8 now pulls STEP timings, reports GROSS saving, and states
   that NET is not determined by that task.
9. The missing-pwsh probe invoked `pwsh -Command Write-Output ok` while
   claiming to capture what a user would see; the hook invokes
   `pwsh -NoProfile -NonInteractive -File <script>`. The probe now uses the
   hook's own shape, and says the harness's presentation was not measured.
10. Task 3 wrote `stubs.tsv` into the repo root, breaking this plan's own
    first Global Constraint. It now writes to the scratchpad.
11. Two entry-point classes escaped both regex families, with live
    instances: bare native invocation (`tools/check-drift.ps1:1060`, the
    item 31 site; `tools/check-drift.ps1:500`; and the instruction at
    `skills/multi-model-verify/SKILL.md:94`), and a CI `run:` step whose
    host the platform supplies with no host token on the line
    (`.github/workflows/skill-evals.yml:71`). A THIRD regex family was
    added and all four instances are now caught, verified by running the
    extracted scanner.
12. Task 4 claimed "arbitrary arguments" from ten fixed payloads, and its
    synthetic parent forwarded only positional `$args` while every shipped
    script declares named parameters (`tools/check-drift.ps1:30-34`). A
    NAMED-PARAMETER arm was added, `run.py` now EXITS NONZERO when any arm
    measured nothing, and the claim is narrowed to the shapes tested.

## What the session found on its own, offered as evidence rather than defence

13. The third family, written as first drafted, matched every `.ps1`
    mention anywhere and produced 5683 total matches, 940 outside `docs/`.
    That is not a survey anyone finishes. It was narrowed to INVOCATION
    shapes, measured again, and the narrowing is recorded in the script's
    own comment as a real narrowing rather than as an empty set. Current
    counts, from running the extracted scanner against this repo: 3977
    total, 3243 under the `docs/` prefix row, 734 needing hand-written
    rows, split 120 host / 241 launch / 373 bare.
14. Because 734 rows in one pass is how a survey stops being read, Task 3
    is now split by family, one subagent each, and `survey.py` prints a
    per-family `FAMILY <name>: <n> hits, <n> unclassified` line so each
    split task has an oracle of its own.
15. The mis-transcribed escaper found in round 1 had a cause worth naming:
    this environment's shell heredoc silently drops backslashes. It
    corrupted the snippet in the committed probe record, and it corrupted
    a regex again during today's amendments. Both were caught by running
    the code rather than reading it. The probe record has been corrected
    and now states that its first committed version printed a broken
    escaper.

## What I want from this round

A. **Sweep the AMENDED plan for the same class**: a claim stated more
   widely than its evidence, or an unmade measurement that reads like a
   clean one. Name each instance with a line reference, or report
   explicitly that you found none.

B. **Sweep the AMENDMENTS THEMSELVES for that class.** This is the ask that
   matters most. This repo's last three release cycles each reproduced the
   very defect class they were fixing, inside their own fixes, and no
   author caught it. Twelve of the fifteen items above are new text written
   today under time pressure. Treat them as the most likely place for a new
   instance, not the least.

C. **The third regex family.** It is narrowed to invocation shapes. Name a
   real entry point in this repo that the narrowing now drops, with a
   file:line, or report none. The narrowing was measured, not assumed, but
   it is exactly the kind of trade that hides something.

D. **The per-family split.** Does splitting classification across three
   subagents create a seam where a row can be lost or double-written? The
   `FAMILY` line is the only oracle each split task has.

E. Anything else you find.

## Rules for your reply

- End with exactly one verdict line: PASS, FIX, or ESCALATE.
- If the plan is now sound, say so in one line. A round that converges is
  the system working. Do not manufacture objections to justify the round,
  and do not concede a point you can refute in order to converge faster.
- Quote the line and give its number for every externally checkable claim.
