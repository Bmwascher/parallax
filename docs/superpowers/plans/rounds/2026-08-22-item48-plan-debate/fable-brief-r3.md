# Debate brief - round 3 - mode plan - Fable lane

## Continuity check, answer FIRST

Neither answer is anywhere in this message.

1. Your continuity nonce, verbatim.
2. In your round 2 reply you flagged a hazard in the missing-pwsh probe that could make it BLOCK rather than fail. Name the exact PowerShell expression in the hook script that causes it, and the file:line you cited for it.

If you cannot answer both from memory of your own earlier rounds, say so plainly rather than reconstructing.

## Subject revision, pinned

Plan file at git blob `44600c231e1f102f7d12b2797ba8254aaf4794c0`, commit `2f6dedf`, branch `item51-inline-brief-transport`. Re-read it.

  docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md

## Disposition of round 2

Every finding was ACCEPTED and applied. Nothing refuted, nothing struck. Each was verified against the repo first.

CONVERGENT across both lanes:
- The verdict step gated on residuals collected in a later step, and no oracle withdrew the placeholder tolerance Step 1 granted. Steps reordered so residuals come first; Step 4 now says explicitly to DELETE the placeholder line; a new Step 6 re-runs both gates and requires the placeholder grep to find nothing.
- `load_rows()` last-wins on duplicates. It now REFUSES them, explicit and prefix alike. Exercised against five cases: duplicate explicit row, duplicate prefix row, unknown classification, the new `not-a-launch` value, and a legitimate two-family pair for one line.
- The scanner comment cited skill-evals.yml:70; the `run:` match is at :71. Corrected.
- The named-parameter arm was inconsistent with the checks reading it.

Applied from single-lane findings:
- The Architecture paragraph still said completeness "is enforced"; the skeleton and scanner docstring still said "two regex families". All three rewritten to state what the script does and three things it does not.
- The `docs/` exception named this plan as its reason but did not cover it, and applied only at Task 3 while Tasks 4 and 7 create more matching files afterwards. It now covers the plan file by name and is restated as a STANDING RULE; Task 4 gains a step classifying its own new files and asserting none is left prefix-covered.
- A `parent-named.ps1` with its own `param()` block now forwards its OWN bound values; `run_named` returns the same keys as `run` and records stage A; `main()` is given verbatim rather than described.
- "Every shipped script declares named parameters" was false. Narrowed to "most", with `hooks/superpowers-review-companion.ps1:12-13` named as the counterexample.
- The hook probe now uses `stdin=DEVNULL` and `timeout=60`, and reports a timeout as a probe defect. Your round 2 finding.
- Step 2b now captures `git merge-base main HEAD` instead of `HEAD`.
- The production claim now requires reading the installed cache and citing it, or writing the claim about the checkout only.
- Task 5's Linux command now reads the whole job by awk range. Run here, it finds no `pwsh` invocation in that job at all.
- Task 6 consumes Task 5's revision-bound run id and writes "exercised, pass not evidenced here" where it has no green run.
- Task 8 asks for a gross upper bound only.
- Each family task now asserts every earlier family is still at zero, and commits its own rows.

## The narrowing, and what it cost

Both lanes named live instances the narrowing dropped, and both were right. Call-operator through a variable (`tools/new-kimi-lane-home.ps1:152`, `tools/new-kimi-lane-login.ps1:214`, `tools/new-kimi-lane-login.ps1:442`) and flagless instruction invocations (`README.md:392`, `CLAUDE.md:41`). Both shapes added.

Measured after: the additions also catch `evals/tools/drift_statemachine_tests.ps1:552`, which launches a HOST through a variable. That is the dual-host harness itself, which no lane named and no family previously saw.

The comment justifying the narrowing claimed the dropped lines "were prose references that no migration would edit" - a statement about 155 lines nobody had opened, with the counterexamples inside that set. It now says they were not read individually and claims nothing about them.

Counts now: 5169 matches, 4380 under the `docs/` prefix row, 789 needing hand rows, split 120 host / 241 launch / 428 bare. A `not-a-launch` class was added because some matches (`tools/codex-tool-surface-probe.ps1:193`, `& $quote $_`) start no process, and forcing them into `launch-nonhost` would put a false row in the inventory.

## What I want from this round

A. Sweep the round-2 amendments for the class. Same ask, same reason: last round seven of fifteen fixes carried the defect they were fixing, and this round changed about twenty more things. Name each instance with a line reference, or report explicitly that you found none.

B. The two new script blocks. `parent-named.ps1` and the replaced `main()` are new code nobody has executed. Read them as CODE: wrong key names, a forward that does not forward, an arm that cannot fail, a `param()` block that binds differently than intended.

C. The widened third family now has seven alternatives. Does any match so broadly that a real entry point gets buried, or so narrowly that a shape is still dropped? Name an instance either way, or report none.

D. Anything else.

End with exactly one verdict line: PASS, FIX, or ESCALATE. If the plan is now sound, one line saying so is the right answer. Do not manufacture objections, and do not concede a point you can refute.