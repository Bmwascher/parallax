# Debate brief - round 1 - mode plan

You are the cross-vendor reviewer in a two-advisor debate. We are equal
weight. Neither of us outranks the other; only evidence does. Every
externally checkable claim you make must cite a file:line you actually read
in this run. A claim with no citation is struck, not debated.

You have read-only access to the repository at the working directory. Read
what you need.

## What is being reviewed

An IMPLEMENTATION PLAN for an INVESTIGATION, before any of it is executed:

  docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md

Its spec is one backlog section. Read it in full:

  docs/superpowers/plans/2026-07-27-0150-backlog.md, the section headed
  "## Item 48: feasibility of moving EVERYTHING to PowerShell 7"

Supporting measurement taken today, already committed:

  docs/superpowers/plans/rounds/2026-08-22-item51-inline-brief-probe/probe-record.md

The plan produces a written feasibility record with a VERDICT on declaring
PowerShell 7 the supported host and retiring Windows PowerShell 5.1. It
ships no code and repins nothing. That restriction is item 48's own rule
for itself.

## The session's position, with evidence

1. Backlog item 51 was REPORTED and is now MEASURED, and it is two
   independent defects rather than one. Under Windows PowerShell 5.1,
   (a) Get-Content -Raw decodes a no-BOM UTF-8 brief with the ANSI code
   page, and (b) the host emits a native argument containing double quotes
   WITHOUT escaping them, where PowerShell 7 emits \". A balanced quote
   count loses the quotes silently; an odd count tore the brief into four
   argv elements. Evidence: the probe record cited above, sections
   "Defect 1" and "Defect 2", including the raw GetCommandLineW payloads.

2. Both defects are 5.1-only. On PowerShell 7 every spelling measured
   exact. Evidence: same probe record, result table.

3. Therefore backlog items 51 and 31 are both subsumed by a decision to
   run only PowerShell 7, and item 48 is the question that decides whether
   the fix for 51 is worth building at all. Item 31's site is reached only
   under 5.1 because tools/check-drift.ps1:96 writes its own scheduled
   task action as `powershell.exe -NoProfile -ExecutionPolicy Bypass
   -File "$self"`.

4. The repo already half-requires PowerShell 7: hooks/hooks.json:10 and
   hooks/hooks.json:22 both invoke the hook as bare `pwsh`.

5. The plan's central design decision is that the entry-point inventory is
   produced by a script that FAILS on any unclassified match, rather than
   by a person reading the tree. This is because item 48's own inventory
   was written by hand twice and was wrong both times, the second time
   after claiming to fix the first. The backlog section records both
   corrections.

6. The arm that can produce a verdict of NO is Task 4, the re-exec
   fidelity measurement. Item 48 lists "A re-exec that cannot pass
   arguments through provably intact" as a NO-criterion, and finding (1)
   above shows the 5.1 host corrupts exactly this kind of argument.

## What I want from you

Answer as a reviewer of the PLAN, not of the underlying idea. The question
is whether executing this plan exactly as written produces a feasibility
record whose verdict can be trusted.

Cover at least these, and add anything you find:

A. **Oracle adequacy, task by task.** For each of the nine tasks, can its
   verification command FAIL while the task's deliverable is wrong? Name
   any task whose check would pass over a broken result. Note that Task 2
   deliberately requires a FAILING run and Task 3 requires the same script
   to pass.

B. **Completeness of the survey method.** survey.py in Task 2 matches two
   regex families across every tracked file. Name a class of entry point
   that both families would MISS, with a file:line in this repo where such
   an entry point exists. If you can find none, say "none found" and say
   what you looked for. The plan's own claim is that completeness becomes a
   property of the script; if that claim is wider than the evidence, that
   is the most valuable thing you can find here.

C. **THE SWEEP QUESTION. This repo's recurring defect class is: a claim
   stated more widely than the evidence that supports it, and its close
   relative, an unmade measurement that reads like a clean one.** Sweep the
   PLAN for instances of that class and either name each instance with a
   line reference, or report explicitly that you found none. Do not answer
   this by telling me whether the plan is good. The last three release
   cycles each reproduced this class inside their own fixes, and the sweep
   question is what found them.

D. **The verdict logic in Task 9.** It requires every NO-criterion to be
   NOT MET, each with a citation, for a YES. Is that logic sound, or can a
   YES be reached while something material is unmeasured?

E. **Anything the plan orders wrongly.** Does any task depend on a result
   from a later task?

## Rules for your reply

- End with exactly one verdict line: PASS, FIX, or ESCALATE.
- A sound plan gets one line. Converging in round 1 is the system working,
  not a skipped review. Do not manufacture objections to justify the round.
- Do not concede a point you can refute in order to converge faster.
- If you assert that a file says something, quote the line and give its
  number.
