# Debate brief - round 7 - mode plan - CONFIRMING ROUND, NARROW SCOPE

Subject revision: the plan file at commit `5cd4626` on branch
`item51-inline-brief-transport`.

  docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md

**This round is DELIBERATELY NARROW and the user authorized it for one
purpose: to check round 6's four fixes.** Do not re-sweep the whole plan.
Six rounds have done that, both of your filter sweeps came back empty last
round, and the fresh-executor read found no blockers. If you find something
outside the four fixes that is genuinely serious, say so — but a stylistic
observation about an untouched section is not what this round is for, and
naming one would cost a round the user is paying for.

If the four fixes are correct, **PASS is the answer and one line is the
right length.**

## The four fixes to check

**1. The staging gates.** Task 4 Step 7 and Task 7 Step 5 now read:

```
test "$(git ls-files $REC/reexec/ | wc -l)" -eq 5 || { echo STAGED_WRONG; exit 1; }
echo STAGED_OK
```

The form they replace, `test ... && echo STAGED_OK || echo STAGED_WRONG`,
printed the failure and exited 0. Measured in this shell before the change:
old form printed `STAGED_WRONG` and exited 0; new form printed
`STAGED_WRONG` and exited 1. Check the new form is right, that both sites
carry it, and that the surviving mention of the WRONG form is only the
explanatory warning beside it and not a live command.

**2. The scratch-file prose.** `run.py` deletes the four `*-out.*` files at
the end of `main()`, on the SUCCESS path only — deliberately, so a failed
run still has the parent's output for the stage-A adjudication. The staging
prose in Task 4 Step 7 said they survive a successful run, contradicting
the cleanup. It now says they survive a failed one. Check the prose matches
the code, and that the staged count of 5 is right on BOTH paths.

**3. The renamed identifier.** `EXEMPT_FROM_PREFIX` no longer exists; the
mechanism is `EXEMPT_PREFIXES` / `EXEMPT_SUFFIXES` / `EXEMPT_EXACT`. Three
prose sites named the dead identifier and now say "the exemption in
`survey.py`". Check no stale name survives and no site now describes the
mechanism wrongly.

**4. `first_difference` on the named arms.** It was always `None`, which
the measurement table cannot use and which reads identically to "nothing
differed". It now returns the first PARAMETER NAME whose bound value
differs, or `None` when nothing does. The table was updated to say the
field is an argument INDEX for positional arms and a parameter NAME for
named ones. Check the expression is correct — including when
`child_bound` is not a dict — and that it cannot report `None` for an arm
that did differ.

## One finding from round 6 was REFUTED, and you should know why

A lane reported that a round-5 edit had silently dropped `/\\` from one
bare-family alternative, and named `commands/doctor.md:235` and
`evals/multi-model-verify/test_kimi_lane_home.py:820` as live entry points
that had fallen out of the filter. I tested it rather than accepting it:
the separators are present in the regex, BOTH files match under family
`bare`, and the two citations reported as backslash-mangled use forward
slashes. The lane was right that this environment mangles backslashes —
that is real and already recorded in this repo's history — and wrong that
it had happened here.

If you are that lane and you still disagree, produce the line and the
match. If you are not, you may ignore this section.

## Rules for your reply

- End with exactly one verdict line: PASS, FIX, or ESCALATE.
- Scope: the four fixes. PASS means those four are correct.
- Do not manufacture objections. Do not withhold PASS because six rounds
  preceded it.
