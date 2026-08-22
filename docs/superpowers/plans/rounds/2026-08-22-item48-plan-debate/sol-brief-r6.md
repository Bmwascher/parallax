# Debate brief - round 6 - mode plan

Subject revision: the plan file at commit `c69e71b` on branch
`item51-inline-brief-transport`. Re-read it.

  docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md

**This is the LAST round the user authorized.** If both lanes do not return
PASS here, the debate pauses and goes back to the user for a decision. It
does not convert into a verdict either way, and there is no pressure on you
to produce one: a real FIX here is worth more than a PASS that isn't.

## Disposition of round 5

CONVERGENT, both lanes independently:

1. **The staging checks were not gates.** They ran `git ls-files ... | wc -l`
   and then a sentence saying "Expected: 5". Nothing compared it and
   nothing exited nonzero. Now `test "$(...)" -eq N && echo STAGED_OK ||
   echo STAGED_WRONG`. That is the FOURTH version of this rule and the
   first that can fail.
2. **Their expected counts were wrong on the successful path.** Both tasks
   staged a whole directory that by then also held the probe's
   `results.json` and its `*-out.*` scratch files, so a clean run staged
   ten paths where the check demanded five, and one where it demanded one.
   The gate was RED on success. Sources are now staged by name, and
   `run.py` deletes the four scratch files at the end of `main()`.
3. **The correction count was stale at three further sites** while being
   corrected at one. It now lives in exactly ONE place — `survey.py`'s
   FAMILIES comment — and the Architecture paragraph, the record skeleton
   and Task 3 all point at it instead of repeating a number. Verified by
   script: the count now appears exactly once in the whole plan.

Accepted from one lane, verified:

4. **The exemption was wider than the sentence justifying it.** The comment
   said the SCRIPTS under the record directory are executed; the code
   exempted every generated sidecar too, so `results.json` and the scratch
   files would each have needed hand rows keyed to line numbers that change
   on every run. The test is now the SUFFIX: `.py` and `.ps1` under the
   record directory, plus this plan file. Everything else the investigation
   writes there is a record, which is what the blanket row already says.
5. **Task 3's prose still contradicted the code**, ordering explicit rows
   for every match "inside the record directory". Rewritten to match: rows
   for the executable files, none for the records.
6. **A ninth client the filter never matched:** bare `agy`, the Flash
   implementer's binary, live at `agents/flash-implementer.md:47` and
   `:78`, used across six non-docs files. Added; 60 hits.

**Two relayed items were REFUTED, not applied.** A citation reported as
using a Windows backslash uses forward slashes at both sites
(`:1534`, `:1690`). And the Interfaces line reported stale in round 4 was
already correct; that lane has since conceded it and named the cause as
reading a stale revision.

## Run, not read

6974 matches, 1043 hand rows — 168 host, 278 launch, 597 bare. All 20 entry
points either lane has named across five rounds are caught. The declared
`git` miss is still missing. Nine exemption cases correct, including the
discriminating ones: a `.ps1` under the record directory is NOT
prefix-covered, `results.json` and `parent-out.txt` beside it ARE, and a
`.py` outside the record directory IS. Duplicate refusal holds. The
correction count appears exactly once.

## What I want from this round

A. **Sweep round 5's amendments.** Every round so far has found its worst
   defect inside the previous round's fixes — four times running, and the
   staging gate alone has now been wrong in four different ways. Six things
   changed. Name each instance with a line reference, or report explicitly
   that you found none.

B. **The suffix-based exemption.** It replaced an exact-path carve-out.
   Can it fail open — is there an executable artifact under the record
   directory that is neither `.py` nor `.ps1`? Can it fail closed?

C. **The filter, a tenth time.** Produce a live instance with a file:line,
   or report none found and say which shapes you looked for. Bare `git` is
   a declared miss and does not count.

D. **One question I have not asked before, and should have.** Forget the
   amendments. Read the plan as an executor would, top to bottom, with no
   memory of this debate. Is there anything that would stop you executing
   it, or make you execute it wrongly? Ambiguity, a missing file, a command
   that will not run on this machine, a step whose output the next step
   cannot use.

## Rules for your reply

- End with exactly one verdict line: PASS, FIX, or ESCALATE.
- **PASS is a real option and one line is the right length for it.** Five
  preceding rounds is not a reason to withhold it, and this being the last
  authorized round is not a reason to grant it.
- Do not manufacture objections; do not concede a point you can refute.
- Quote the line and give its number for every externally checkable claim.
