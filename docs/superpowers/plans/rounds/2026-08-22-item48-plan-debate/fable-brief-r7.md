# Debate brief - round 7 - CONFIRMING ROUND, NARROW SCOPE

## Continuity check, answer FIRST

Your nonce, verbatim. That is all this round needs.

## Subject

Plan file at commit `5cd4626`, branch `item51-inline-brief-transport`.

**This round is DELIBERATELY NARROW and the user authorized it for one purpose: to check round 6's four fixes.** Do not re-sweep the whole plan. Six rounds have done that, both lanes' filter sweeps came back empty last round, and your fresh-executor read found no blockers. If you find something outside the four fixes that is genuinely serious, say it — but a stylistic note on an untouched section is not what this round is for, and naming one costs a round the user is paying for.

If the four fixes are correct, **PASS is the answer and one line is the right length.**

## The four fixes

**1. The staging gates.** Task 4 Step 7 and Task 7 Step 5 now read `test "$(...)" -eq N || { echo STAGED_WRONG; exit 1; }` then `echo STAGED_OK`. The form they replace, `test ... && echo STAGED_OK || echo STAGED_WRONG`, printed the failure and exited 0. Measured in this shell: old form exited 0, new form exits 1. Check the new form is right, both sites carry it, and the surviving mention of the wrong form is only the explanatory warning beside it, not a live command.

**2. The scratch-file prose.** `run.py` deletes the four `*-out.*` files at the end of `main()` on the SUCCESS path only — deliberately, so a failed run still has the parent's output for stage-A adjudication, which is the distinction you drew in round 6. The staging prose said they survive a successful run, contradicting the cleanup; it now says they survive a failed one. Check prose matches code and that the staged count of 5 holds on both paths.

**3. The renamed identifier.** `EXEMPT_FROM_PREFIX` is gone; the mechanism is `EXEMPT_PREFIXES` / `EXEMPT_SUFFIXES` / `EXEMPT_EXACT`. The three prose sites you and the other lane both flagged now say "the exemption in `survey.py`". Check no stale name survives and no site now describes the mechanism wrongly.

**4. `first_difference` on the named arms.** It was always `None` — unusable by the table and indistinguishable from "nothing differed". It now returns the first PARAMETER NAME whose bound value differs, or `None` when nothing does, and the table says the field is an index for positional arms and a name for named ones. Check the expression, including when `child_bound` is not a dict, and that it cannot report `None` for an arm that did differ.

## Your round-6 A1 was REFUTED, and here is the evidence

You reported that a round-5 edit silently dropped `/\\` from bare-family alternative 3, naming `commands/doctor.md:235` and `evals/multi-model-verify/test_kimi_lane_home.py:820` as live entry points that had fallen out.

I tested it rather than accepting it. The regex at the live revision reads `&\s*['\"]?[\w\-/\\:.$()\[\]]*\.ps1` — the separators are present. Both files MATCH, family `bare`, confirmed by running the extracted scanner against them. And the two citations you reported as backslash-mangled read `agents/flash-implementer.md:47` and `tools/check-drift.ps1:987`, forward slashes at both sites.

You were right that this environment mangles backslashes; it is real and it corrupted a committed artifact earlier in this very cycle. It did not happen here. If you still disagree, produce the line and the match and I will re-test. Otherwise say conceded and move on — I am telling you because a lane that is not told keeps carrying the belief into later rounds.

End with exactly one verdict line: PASS, FIX, or ESCALATE. Scope is the four fixes. Do not manufacture objections, and do not withhold PASS because six rounds preceded it.