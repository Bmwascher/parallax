# Plan debate, round 6 - 0.26.0 fresh-preamble gate

Same session `01a00b96-1d26-77f2-bb53-13702ab58e1a`, resumed a fifth time.
Route re-confirmed against the transcript header - `gpt-5.6-sol`, openai,
read-only, effort high - and the reply bound by
`tools/read-codex-round-evidence.ps1 -Resume` before it was read: verdict
`clean`, brief digest `78232688e74ebc78b94c64b967c26db3e482d20c2b47e056e9afb02a9445e3ec`,
over round 5's `nextState` verbatim as the prior state.

This was the LAST round of the declared six-exchange budget. It asked
whether item 60's corrected citations are right, and swept the fourth class
across everything this branch WROTE - the design spec, the plan's own
citations including the ones inside comments an implementer will paste into
shipped files, the two new contract region texts, and the five retained
round records.

Verdict: **FIX**, and NOT DRY. Item 60's citations are confirmed correct.
The plan's logic is confirmed clean for the second round running: classes
1, 2 and 3 all dry. Four class-4 defects remain, all record-only, and two
of them are this side describing the previous round's corrections
imprecisely - the same drift the previous round found, one generation on.

All four were verified here against the files and applied. The budget is
exhausted, so the debate PAUSES for the user's authorization rather than
continuing.

The reply is retained verbatim.

---

Not dry. Item 60’s operative citations are now correct, but the Class 4 sweep found four record-integrity defects.

1. Item 60 citations

Every source citation now points to the claimed code:

- Tier 2 invokes the trigger runner; Tier 2b runs structural pytest ([skill-evals.yml:41-47](/C:/Users/Brandon/Documents/parallax/.github/workflows/skill-evals.yml:41)).
- Missing fixtures warn and continue at 101–103; lexical exclusions occur at 107–108; comparison is guarded at 117; success prints and returns at 134–135 ([run_trigger_evals.py:99-135](/C:/Users/Brandon/Documents/parallax/evals/tools/run_trigger_evals.py:99)).
- `test_trigger_cases_schema` begins at 1257 and requires unfiltered positives and negatives, not lexical survivors ([test_multi_model_verify.py:1257-1266](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_multi_model_verify.py:1257)).
- The current fixture contains five positive and five negative cases, with no `"lexical": false` field, so the LATENT characterization follows from the files ([trigger-cases.json:5-64](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/trigger-cases.json:5)).

2. Class 4 findings

1. The design names the wrong codex contract region. Its Scope says `codex-brief-binding-record` is in scope ([design:205-212](/C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-08-16-fresh-preamble-gate-design.md:205)), but the plan leaves that existing region in place and adds `codex-brief-binding-fresh-record` to `DECLARED_REGIONS` and the document ([plan:1045-1057](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1045), [plan:1072-1074](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1072)). The existing record region is separately named in the shipped document ([model-prompting-notes.md:475](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/model-prompting-notes.md:475)).

   Fix: change design line 211 to `codex-brief-binding-fresh-record`.

2. Task 4’s Item 42 citation is off by one. The plan says its closing-block shape is “at line 3000” and declares that its references use base commit `a170756` ([plan:53-55](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:53), [plan:1205-1209](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1205)). At `a170756`, `docs/superpowers/plans/2026-07-27-0150-backlog.md:3000` is the separating blank line and the closing paragraph begins at `:3001`; the corresponding current lines are likewise blank at 3006 and paragraph text at 3007 ([backlog:3006-3007](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:3006)).

   Fix: cite base lines `3000-3001`, which actually show the separator and paragraph shape.

3. Item 60 misclassifies its own four original errors as “four wrong citations” ([backlog:4185-4190](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:4185)). The retained round says the actual split was one factual tier error and three inaccurate line citations ([plan-debate-r5.md:28](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-16-fresh-preamble-gate/plan-debate-r5.md:28)).

   Fix: say “four record errors — one wrong CI tier and three wrong line citations.”

4. Round 5’s header repeats the same categorization error, calling all four defects wrong citations ([plan-debate-r5.md:14-19](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-16-fresh-preamble-gate/plan-debate-r5.md:14)), while its retained reply correctly distinguishes the one factual error from the three citations ([plan-debate-r5.md:28](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-16-fresh-preamble-gate/plan-debate-r5.md:28)).

   Fix the header with the same wording above.

The other checkable design citations are aligned: canonicalization points to the actual functions and hash path ([read-codex-round-evidence.ps1:105-110](/C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:105), [read-kimi-round-evidence.ps1:124-126](/C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:124), [read-kimi-round-evidence.ps1:891-897](/C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:891)); the two falsification dates match the shipped comments ([read-codex-round-evidence.ps1:851-870](/C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:851)).

## Verdict

**FIX** — make the four record-only corrections above. Because this is the hard-stop round, execution should pause pending user authorization.

## UNVERIFIED

- The session-store measurements—766/767 records, the 658/73/36/0 and 322/50 splits, and text-length figures—have no retained dataset in the reviewed tree ([design:42-76](/C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-08-16-fresh-preamble-gate-design.md:42)).
- The twelve claimed checker executions and controls have no retained execution artifact ([plan:1283-1306](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1283)).
- The debate headers’ session IDs, digests, rollout inventory, byte count, prefix hash, and binding verdicts cannot be recomputed without the underlying rollouts, briefs, transcript headers, and state files ([round 1:3-11](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-16-fresh-preamble-gate/plan-debate-r1.md:3), [round 2:3-10](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-16-fresh-preamble-gate/plan-debate-r2.md:3), [round 3:3-8](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-16-fresh-preamble-gate/plan-debate-r3.md:3), [round 4:3-8](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-16-fresh-preamble-gate/plan-debate-r4.md:3), [round 5:3-8](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-16-fresh-preamble-gate/plan-debate-r5.md:3)).
- Postimplementation dual-host suite results and pass/skip counts cannot exist until execution ([plan:1122-1132](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1122)).
---

## Session final adjudication, 2026-08-16

Every round-6 finding was verified against the live repo before it was
accepted: the spec's Scope line, the item-42 line citation at the branch
base, and the two imprecise descriptions. All four accepted, all four
applied in commit `03b4eef`. None refuted, none struck.

**Terminal verdict: the plan is APPROVED FOR EXECUTION, and the debate
ended at BUDGET EXHAUSTION on the user's decision rather than on a dry
round.** That distinction is the honest record and is not smoothed over.

What supports the approval: the plan's LOGIC was swept clean twice running.
Rounds 5 and 6 both found classes 1, 2 and 3 dry, and round 6 swept the two
new contract region texts - the only prose here that becomes shipped,
pinned contract - and found nothing.

What the approval does NOT claim: that a seventh round would have been dry.
Class 4 landed in rounds 5 and 6 in the prose written to correct the round
before it, and there is no evidence that generation three would have been
empty. The user was given that reading and chose to build. Recorded here so
a later reader does not mistake this for a converged debate.

Six rounds, six findings sets, every one accepted, not one contested.
