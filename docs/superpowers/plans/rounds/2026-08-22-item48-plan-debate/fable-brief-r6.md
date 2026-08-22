# Debate brief - round 6 - mode plan - Fable lane

## Continuity check, answer FIRST

Neither answer is in this message.

1. Your continuity nonce, verbatim.
2. In round 5 you predicted a secondary effect of sweeping probe artifacts into tracking under an exempt directory — something that would happen to a particular file on a re-run. State what you said would go wrong and to which kind of file.

If you cannot answer both from memory of your own earlier rounds, say so plainly rather than reconstructing.

## Subject revision

Plan file at commit `c69e71b`, branch `item51-inline-brief-transport`. Re-read it.

**This is the LAST round the user authorized.** If both lanes do not return PASS here, the debate pauses and goes back to the user. It does not convert into a verdict either way, so there is no pressure on you to produce one: a real FIX here is worth more than a PASS that is not earned.

## Disposition of round 5

CONVERGENT, both lanes independently:

1. **The staging checks were not gates.** `git ls-files ... | wc -l` followed by a sentence saying "Expected: 5" — nothing compared it, nothing exited nonzero. Now `test "$(...)" -eq N && echo STAGED_OK || echo STAGED_WRONG`. Fourth version of this rule, first that can fail.
2. **Their expected counts were wrong on the SUCCESSFUL path** — your finding, and the sharper half. Both tasks staged a whole directory that by then held `results.json` and the `*-out.*` scratch files, so a clean run staged ten paths where the check demanded five. Sources are now staged by name, and `run.py` deletes the four scratch files at the end of `main()`, exactly as you proposed.
3. **The correction count was stale at three further sites** while being corrected at one — your A2, generalised. It now lives in exactly ONE place, `survey.py`'s FAMILIES comment, and the Architecture paragraph, the record skeleton and Task 3 all point at it. Verified by script: the count appears exactly once in the plan.

Accepted from the other lane, verified:

4. **The exemption was wider than its own justification.** It said the SCRIPTS under the record directory are executed, then exempted every generated sidecar too — which is precisely the secondary effect you predicted in round 5. The test is now the SUFFIX: `.py` and `.ps1` under the record directory, plus this plan file. Everything else there is a record and the blanket row covers it, which also removes the `NOT_EXEMPT` exact-path list entirely.
5. Task 3's prose still ordered explicit rows for every match "inside the record directory", contradicting the code. Rewritten.
6. A ninth client the filter never matched: bare `agy`, live at `agents/flash-implementer.md:47` and `:78`, six non-docs files. Added, 60 hits.

**Your cosmetic finding was REFUTED:** the citation you reported as using a Windows backslash uses forward slashes at both sites, `:1534` and `:1690`. Push back with the line if you disagree.

## Run, not read

6974 matches, 1043 hand rows — 168 host, 278 launch, 597 bare. All 20 named entry points caught. The declared `git` miss still missing. Nine exemption cases correct including the discriminating ones: a `.ps1` under the record directory is NOT prefix-covered, `results.json` and `parent-out.txt` beside it ARE, a `.py` outside the record directory IS. Duplicate refusal holds.

## What I want from this round

A. Sweep round 5's amendments. Every round has found its worst defect inside the previous round's fixes, four times running, and the staging gate alone has now been wrong in four different ways. Six things changed. Name each instance with a line reference, or report explicitly that you found none.

B. The suffix-based exemption. It replaced an exact-path carve-out. Can it fail open — is there an executable artifact under the record directory that is neither `.py` nor `.ps1`? Can it fail closed?

C. The filter, a tenth time. Live instance with a file:line, or none found and which shapes you looked for. Bare `git` is declared and does not count.

D. **A question I have not asked before and should have.** Forget the amendments. Read the plan as an EXECUTOR would, top to bottom, with no memory of this debate. Is there anything that would stop you executing it, or make you execute it wrongly? Ambiguity, a missing file, a command that will not run on this machine, a step whose output the next step cannot use.

End with exactly one verdict line: PASS, FIX, or ESCALATE. **PASS is a real option and one line is the right length for it.** Five preceding rounds is not a reason to withhold it, and this being the last authorized round is not a reason to grant it.