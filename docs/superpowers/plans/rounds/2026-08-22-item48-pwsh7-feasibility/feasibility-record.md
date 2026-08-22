# Feasibility record: moving everything to PowerShell 7 (backlog item 48)

Date started: 2026-08-22 (local, CDT).
Repo: branch `item51-inline-brief-transport`, cut from `main` at `a3134dcd76d9253057bf24935f3d7a7eef8eb0e4`.
Hosts under test: Windows PowerShell 5.1.26100.9168 and PowerShell 7.6.5.
Driver: Opus 5, subagent-driven per task.
Header facts captured, not asserted from memory, by running
`git rev-parse --abbrev-ref HEAD`, `git merge-base main HEAD`, and
`$PSVersionTable.PSVersion.ToString()` under each of
`C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe` and
`C:\Program Files\PowerShell\7\pwsh.exe` (task-1-report.md carries the
captured output).

**This is an investigation. Nothing in this cycle is repinned and no 5.1
test is deleted.**

## Verdict

NOT YET WRITTEN. Filled by the final task, after every measurement below.

## What would make the verdict NO

Copied verbatim from backlog item 48 BEFORE any measurement was made, so
the answer cannot be shaped by the effort already spent:

- Any entry point that cannot be made to reach 7 - most likely a hook or a
  scheduled task registered outside this repo's control.
- A re-exec that cannot pass arguments through provably intact.
- A user-facing failure mode worse than the bugs being removed.
- Any need to keep a 5.1 code path "just in case", which would mean paying
  for both hosts and testing one.

## Method

The entry point inventory is produced by `survey.py` in this directory and
verified by re-running it, not by rereading it. Two earlier hand
inventories of this item were wrong: the first in three of four entries,
the second in four further ways after claiming to fix the first.

The script matches THREE regex families across every tracked file it can
read, and FAILS if any match lacks a written classification. So a DETECTED
entry point cannot be passed over silently.

It does not do more than that, and this record does not claim it does:

- The families are a filter. They were two when first written and have been
  corrected repeatedly, every time because a reviewer produced a live entry
  point in this repo that the filter did not match. The count and the
  enumerated list live in `survey.py`'s FAMILIES comment and nowhere else;
  copy them from there. There is no argument that the current filter is
  enough - only that nobody has produced the next miss yet, which is not
  the same statement.
- A green run says every detected match carries a row. It says nothing
  about whether the row is CORRECT.
- A file the script cannot read is listed as `NOT SCANNED`, by name. An
  unread file is not a clean one.

## Entry point inventory

NOT YET WRITTEN.

## Measurement 1: re-exec fidelity

NOT YET WRITTEN.

## Measurement 2: is PowerShell 7 present

NOT YET WRITTEN.

## Measurement 3: behaviour under 7

NOT YET WRITTEN.

## Measurement 4: refusal when pwsh is missing

NOT YET WRITTEN.

## Measurement 5: what is saved

NOT YET WRITTEN.

## Residual limits

NOT YET WRITTEN.
