# Plan debate, round 5 - 0.26.0 fresh-preamble gate

Same session `01a00b96-1d26-77f2-bb53-13702ab58e1a`, resumed a fourth time.
Route re-confirmed against the transcript header - `gpt-5.6-sol`, openai,
read-only, effort high - and the reply bound by
`tools/read-codex-round-evidence.ps1 -Resume` before it was read: verdict
`clean`, brief digest `db3b50ea03b4ce292ed96ba4a6ec8b2739615723421994579d56aba231adb44f`,
over round 4's `nextState` verbatim as the prior state.

The round asked whether the three round-4 fixes are correct, whether
backlog item 60's own prose is accurate, and for a final sweep of all three
classes plus a fourth if one exists.

Verdict: **FIX**, but the plan itself is clean. All three known classes are
DRY, and the checker fixes and Task 4's regenerated arithmetic are
confirmed correct. The only remaining defects are FOUR RECORD ERRORS
inside backlog item 60 - the item this side filed one round earlier - one
wrong CI tier and three wrong line citations, which the reviewer names as a
fourth class: RECORD-INTEGRITY DRIFT, correct substance carried by wrong
citations or metadata.

All four were verified here against the files before being accepted, and
all four are corrected.

The reply is retained verbatim.

---

The checker fixes and Task 4 arithmetic are correct. The remaining defect is confined to Item 60’s record: one factual tier error and three inaccurate line citations.

## 1. Checker and arithmetic

- The no-heading check runs first, and the closed check is an `elif`, so one bold-number occurrence cannot produce both messages ([plan:1451](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1451)). A heading lacking a status can separately trigger Check 1 and the ranked-item check, but that is two distinct defects in the file state, not double-reporting by the two Check 3 branches ([plan:1380](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1380)).

- The legal first-after-heading shape passes. Joining a heading, one empty line, and `want` produces a body ending in `"\n\n" + want`; `rstrip()` removes only trailing separation after the block ([plan:1481](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1481)). It should pass because Step 2 requires terminal placement and one blank line, not preceding prose ([plan:1198](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1198)).

- The OPEN arithmetic is correct. The current status block contains 33 OPEN items, including 52, 56, and 60 ([backlog:34](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:34)); 52 and 56 are currently OPEN while 57 is partially closed ([backlog:3696](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:3696), [backlog:3938](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:3938), [backlog:3985](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:3985)). Closing 52 and 56 therefore leaves 31 OPEN.

- The ranked arithmetic is correct. The current list is consecutively numbered 1–29, ending with Item 60 ([backlog:196](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:196), [backlog:211](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:211)). Removing entries 6, 7, and 25 leaves 26, matching the regenerated output and renumbering anchors ([plan:1541](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1541), [plan:1555](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1555)).

## 2. Item 60

Its substantive diagnosis is accurate:

- Missing case files warn and continue ([run_trigger_evals.py:101](C:/Users/Brandon/Documents/parallax/evals/tools/run_trigger_evals.py:101)).
- `lexical: false` cases are skipped before scoring ([run_trigger_evals.py:107](C:/Users/Brandon/Documents/parallax/evals/tools/run_trigger_evals.py:107)).
- Comparison requires both filtered sets ([run_trigger_evals.py:117](C:/Users/Brandon/Documents/parallax/evals/tools/run_trigger_evals.py:117)).
- With no accumulated failure, the runner prints `all clear` and returns 0 ([run_trigger_evals.py:131](C:/Users/Brandon/Documents/parallax/evals/tools/run_trigger_evals.py:131)).
- The schema requires positive and negative cases but imposes no requirement after the lexical filter ([test_multi_model_verify.py:1257](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_multi_model_verify.py:1257)).
- The current fixture really contains five positives and five negatives, none marked nonlexical, so the defect is latent rather than currently vacuous ([trigger-cases.json:5](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/trigger-cases.json:5), [trigger-cases.json:35](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/trigger-cases.json:35)).

The proposed fix closes all three paths: requiring a case file closes the missing-file path, while requiring at least one surviving lexical positive and negative closes empty and one-sided filtered sets ([backlog:4173](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:4173)).

Four record corrections are required:

1. Item 60 calls the runner “tier 2b,” but CI identifies trigger/routing as Tier 2; structural pytest is Tier 2b ([backlog:4149](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:4149), [skill-evals.yml:41](C:/Users/Brandon/Documents/parallax/.github/workflows/skill-evals.yml:41), [skill-evals.yml:44](C:/Users/Brandon/Documents/parallax/.github/workflows/skill-evals.yml:44)).

2. The lexical-skip citation says `:104-106`; the skip is at `:107-108` ([backlog:4155](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:4155), [run_trigger_evals.py:107](C:/Users/Brandon/Documents/parallax/evals/tools/run_trigger_evals.py:107)).

3. The success citation says `:131-134`, but the print and return are `:134-135` ([backlog:4160](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:4160), [run_trigger_evals.py:134](C:/Users/Brandon/Documents/parallax/evals/tools/run_trigger_evals.py:134)).

4. The schema citation says `test_multi_model_verify.py:1256`; the relevant test and assertions are `:1257-1266` ([backlog:4168](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:4168), [test_multi_model_verify.py:1257](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_multi_model_verify.py:1257)).

## 3. Final sweep

- Class 1: dry. The regenerated 31-OPEN and 26-ranked outputs are correct.
- Class 2: dry. The changed checker conditions measure the changes they name.
- Class 3: dry in the new checker. The known trigger-runner weakness is accurately scoped as latent and filed rather than falsely presented as closed ([plan:46](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:46)).
- Class 4 exists: record-integrity drift—correct substantive prose supported by wrong citations or metadata. Item 60 contains the four instances above.

**Verdict: FIX** — change Item 60’s tier from 2b to 2 and correct its three line citations. No implementation-plan logic change is otherwise required.

**UNVERIFIED**

- The twelve claimed checker executions have no retained artifact ([plan:1283](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1283)).
- The historical occurrence of the claimed trigger-runner execution has no retained artifact; its current 5/5 outcome is independently supported by the checked inputs.
- Postimplementation suite counts cannot exist until execution.
- The session-store sweeps remain unreproducible from the reviewed files.