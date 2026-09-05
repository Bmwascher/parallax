# Fable whole-branch review: adb9ac3..63d04af

Range-bound artifact. Reviewer: `agents/fable-reviewer.md` (model fable), dispatched
2026-09-04 by the session over the controller-built package
`.superpowers/sdd/2026-09-04-item87-astra-reviewer-swap/review-adb9ac3..63d04af.diff`
(merge-base adb9ac3, head 63d04af, 15 commits). The reply below is retained verbatim.

---

### Strengths

- The swap is complete for every runtime parser in one edit and the ordering that makes it safe is now pinned: `evals/multi-model-verify/test_multi_model_verify.py:1149-1178` asserts the heading, all four declarations, and that `Canonical model id:` precedes `Alternate codex reviewer model id:` precedes `Canonical backup reviewer model id:`, while comparing the canonical id by prefix so `test_reviewer_id_has_single_source` keeps its reach.
- The reviewer-lane rewrite at `skills/multi-model-verify/references/model-prompting-notes.md:141-230` keeps every claim at its evidence width: the 5.6 guidance is dated and attributed (`:175-180`), the Astra clarification tendency is called the guide's claim and marked UNMEASURED under `codex exec` (`:198-209`), the `persistent_instructions` block is called an observation, and the effort bullet (`:229-241`) explains why `high` carries over without asserting a measurement on Astra.
- Revision 6's four contextual edits landed exactly as specified and keep Sol's provenance while moving the operative subject to the lane: `:328-330` (resume, "Sol-era evidence not re-checked for Astra"), `:574-577` (fabrication counter, "The record is Sol's; the rule is the lane's"), `:578-584` (tier gating now names `gpt-5.6-sol` as "the canonical id when this was probed"), `:604-605` (recipes "unmeasured for Astra").
- The live-label rename is complete for the surfaces the plan and the counted Astra round enumerated, and the historical citations were left alone: `README.md:27,48,66,258,267`, `CLAUDE.md:134`, `skills/multi-model-verify/SKILL.md:214`, `panels.md:4,12,14,49-52`, `fallbacks.md:218,238`, `frozen-plan-format.md:104`, `evals/tools/run_behavioral_evals.py:238,250,254`. Lines 12 and 14 of `panels.md` stay single physical lines for the raw-read pins at `test_seat_reshuffle.py:133-137`.
- The probe work is fail-closed in every direction it adds. The self-quote mask at `tools/codex-context-probe.ps1:483-489` is an ordinal, exact, length-preserving replacement of one literal, and the tests hold all three refusing directions plus the positive control: `test_codex_context_probe.py:401-435` (masked; no backticks refuses; third pair refuses; different inner text refuses). The alias table is read only from inside the container body before the entries heading (`codex-context-probe.ps1:264-279`), the dictionary is ordinal (`:273`), an unlisted alias stays unplaceable and files as `unknown` (`test_codex_context_probe.py:478-484`), a table outside the body does not expand (`:486-494`), and the end-to-end test proves the override carries absolute paths and never an alias (`:513-527`).
- Tests use single-quoted here-strings (`test_codex_context_probe.py:390-397`, `:456-463`) so backticks, fences and newlines reach the PowerShell parser as written, closing the double-quoted-string defect the Task 4 review found.
- The debate record at `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:1270-1313` is unusually honest: both voided rounds are recorded with their causes, their replies are retained but marked as not evidence, and the counted round's completion evidence is written in full.

### Issues

#### Critical

None.

#### Important

None.

#### Minor

1. `.claude-plugin/plugin.json:3` bumps to 0.31.0 inside a range whose frozen plan forbids it. `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:81-82` says "Do not bump `.claude-plugin/plugin.json`. The bump happens AFTER the diff debate", and `:1256-1261` orders the close of item 87 and the bump after the debate. The ledger (`.superpowers/sdd/2026-09-04-item87-astra-reviewer-swap/progress.md:53-54`) records the deviation as user-directed with a 0.31.1 re-bump to follow, but the frozen plan was not reopened and its text now disagrees with the branch. The diff-debate record should name the overridden constraint and the pending re-bump so the plan's own "changes from here require reopening the debate" sentence is not silently false.

2. Plan step `:1253-1255` says the diff debate runs on the installed 0.30.1 "so Sol reviews its own replacement; the record says so." The early install (`progress.md:54`) means the installed copy is now 0.31.0 and dispatches Astra. The plan sentence is stale; the diff-debate record must state which model actually ran, not inherit this line.

3. The alternate is declared but not operable from the texts an agent follows. `model-prompting-notes.md:162-172` says a Sol run makes "the effective-route check ... against the alternate declarations", but `skills/multi-model-verify/SKILL.md:233-236` directs the route check at `&lt;canonical-model-id&gt;` and `&lt;canonical-effort&gt;` only, and `frozen-plan-format.md:111-113` ties `-RouteNote` `effective route confirmed` to "that lane's own canonical declarations". A Sol run under SKILL.md as written fails its route check (header `gpt-5.6-sol` against canonical `gpt-6-astra`), which is the safe direction, so this is not a false-clean path; it is a feature the branch declares that no command surface can execute. Backlog it rather than fix here: the plan's Global Constraints forbid changing evidence or transport in this branch.

4. `model-prompting-notes.md:145-146` still says the executables "PARSE these two declarations" directly above four declaration lines. The paragraph at `:170-172` ("Nothing that parses the canonical declarations reads the alternate ones") resolves the ambiguity two paragraphs later. Wording only.

5. The package does not show Task 4's dual-host test counts. Plan step 6 (`:1203-1212`) requires both hosts and "Record both counts"; `progress.md:33` records only the live probe result. CI's `powershell-hosts` job will re-run the module on push, so this is a record gap, not a code risk. Named as a gap the package lacks; nothing was run to fill it.

### Ledger minors triage

- Notes "these two declarations" above four lines (`model-prompting-notes.md:145-146`): ride. Resolved by `:170-172`; a one-word edit near a raw-read heading pin is not worth a re-review cycle.
- `SKILL.md:233` "the two declarations": ride. It names exactly the two placeholders the transport commands substitute, which remain the canonical pair; making it "four" would be wrong.
- Undated `persistent_instructions` observation (`model-prompting-notes.md:207-209`): ride. The plan's measured fact 2 (`:102-104`) dates it 2026-09-04; add the date at the next touch of that bullet.
- `BACKLOG.md:3738-3776` carries the `gpt-6-astra` literal outside the sweep: ride. It is a record, not a declaration; the sweep's exclusion of `BACKLOG.md` is pre-existing and the counted round already logged the `agents/` glob gap (`plan:1279`) as a backlog candidate.
- Nothing beyond the notes directs a Sol-alternate route check: ride, but file it (Minor 3 above). Failure direction is closed, and fixing it means touching SKILL.md under a 43-token ceiling and the route-check contract, both out of this plan's scope.
- Probe: roots line below the entries heading untested (`codex-context-probe.ps1:275-278` reads only `$body.Substring(0, $start)`): ride. The code bounds the read by construction; a test would document, not protect.
- Probe: duplicate alias last-wins (`:277`): ride. Both lines are client-authored; a wrong root yields a path `Get-SkillScope` cannot place, which blocks.
- Probe: self-quote mask runs over the whole prompt on each `$only` iteration (`:483-489`): ride. Idempotent and length-preserving; the Task 4 reviewer and the counted Astra round (`plan:1298`, sub-claim b) both checked the `$only` path.
- Task 3 report count slips: ride. Prose in a task report; the ledger and the gate output carry the numbers that matter.

### Assessment

Ready to merge: Yes

The code and reference changes match the frozen plan at revision 8, every new parser path fails closed, and the pins lock the lane's identity and ordering. The only findings are record-level: the early version bump and the early install make two sentences of the frozen plan stale, and the Sol alternate is declared without a command surface that can run it, which the diff-debate record and a backlog item should carry rather than this branch.
