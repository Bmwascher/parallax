## 1. Single source

The executable migration is complete: the runner and drift script parse the canonical declarations, and doctor reads the installed declaration (`evals/tools/run_behavioral_evals.py:813`, `tools/check-drift.ps1:1010`, `commands/doctor.md:58`).

Two qualifications: the literal also appears in a historical probe within the same notes file (`skills/multi-model-verify/references/model-prompting-notes.md:507`); and the sweep covers enumerated globs, not literally everywhere (`evals/multi-model-verify/test_multi_model_verify.py:804`). **Pre-existing:** those globs omit `agents/`; this is a coverage gap, not an additional migration defect found here.

PASS

## 2. Alternate declaration parser safety

No loose `model id:` parser was found in the searched `evals/` and `tools/` sources. Primary parsers match the full canonical label; backup parsing likewise uses its complete label (`evals/tools/run_behavioral_evals.py:813`, `tools/check-drift.ps1:1010`, `evals/multi-model-verify/test_backup_lane.py:71`, `evals/tools/lane_credential_live_support.py:127`). The ordering and route tests use the same explicit labels (`evals/multi-model-verify/test_seat_reshuffle.py:296`, `evals/multi-model-verify/test_route_parser_shapes.py:78`).

PASS

## 3. Alternate literal in the new test

The sweep checks the currently declared ID plus the contiguous flag marker; its additional regex requires a preceding `-m` (`evals/multi-model-verify/test_multi_model_verify.py:791`, `evals/multi-model-verify/test_multi_model_verify.py:801`). The proposed alternate assertion has no such flag, and Task 2 explicitly expects its temporary canonical-literal failure before changing the notes (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:283`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:303`).

PASS

## 4. Contract-pin ordering

The red command selects only the specified module; the later command includes contract coverage after the region edit (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:301`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:501`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:510`). Coverage requires the complete region inside a pin, so changing both instances restores this region’s agreement (`evals/multi-model-verify/test_contract_coverage.py:945`, `evals/multi-model-verify/test_multi_model_verify.py:1327`).

PASS

## 5. Live-label completeness

One generated fixture header remains uncovered: `| Sol position |` in the escalation table (`evals/tools/run_behavioral_evals.py:251`). Revision 6 changes that fixture’s participant and resolved row, but specifies no replacement for this header (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:634`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:641`). It belongs to the generated record, just like the resolved row, rather than a retained historical debate (`evals/tools/run_behavioral_evals.py:235`).

FIX (extend Task 3 Step 9b to replace `| Sol position |` with `| Astra position |` at `evals/tools/run_behavioral_evals.py:251` before its remaining-match check).

## 6. Raw versus normalized pins

`_read` returns raw decoded text, and the composition assertions operate directly on it (`evals/multi-model-verify/test_seat_reshuffle.py:16`, `evals/multi-model-verify/test_seat_reshuffle.py:130`). The task-naming assertion explicitly normalizes whitespace (`evals/multi-model-verify/test_multi_model_verify.py:1327`). The plan preserves the two composition sentences as single physical lines (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:579`).

PASS

## 7. SKILL.md budget and edit scope

The only `Sol` lane label in `SKILL.md` is the task-name example at `skills/multi-model-verify/SKILL.md:213`. The plan restricts its edit to that word and requires recording the subsequent lint count (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:27`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:688`).

I reproduced the linter’s arithmetic: approximately **6,456 currently; 6,457 after the replacement**, below 6,500. This uses the body extraction and character-count estimator, not tokenizer measurements (`evals/tools/skill_lint.py:182`, `evals/tools/skill_lint.py:339`).

PASS

## 8. Evidence-width discipline

The replacement dates and attributes the guidance, explicitly retains the brief shape as a repository convention, calls clarification behavior UNMEASURED under `codex exec`, identifies persistent instructions as an observation with unknown applicability, and dates the config-default observation (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:353`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:374`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:377`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:408`). These satisfy the stated evidence-width constraint; page contents were not verified.

PASS

## 9. Opt-in alternate

The alternate paragraph explicitly requires the user to name Sol and excludes automatic selection and fallback-gate offers (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:341`). The panel amendment lets it occupy the codex seat under that same condition; fallback edits only rename the default label (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:585`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:594`). This preserves the existing distinction between the codex seat and Kimi substitution (`skills/multi-model-verify/references/panels.md:49`, `skills/multi-model-verify/references/fallbacks.md:159`).

PASS

## 10. Context-probe contract

The current checkout already contains the proposed family recognition and literal mask (`tools/codex-context-probe.ps1:421`, `tools/codex-context-probe.ps1:483`). In-memory execution confirmed the test directions: the exact quote passes; removing backticks, changing inner text, or adding a real second container refuses; an unknown family remains visible; an attributed known tag refuses (`evals/multi-model-verify/test_codex_context_probe.py:361`, `evals/multi-model-verify/test_codex_context_probe.py:400`, `evals/multi-model-verify/test_codex_context_probe.py:426`, `evals/multi-model-verify/test_codex_context_probe.py:998`).

- **(a)** Earlier masking inside `INSTRUCTIONS` does not change its delimiter counts or offsets: the literal contains neither instruction delimiter, replacement preserves length, and its surrounding body is subsequently blanked (`tools/codex-context-probe.ps1:483`, `tools/codex-context-probe.ps1:493`, `tools/codex-context-probe.ps1:529`).
- **(b)** `$only` changes the container list, while the literal mask runs unconditionally. The skills parser uses that same function (`tools/codex-context-probe.ps1:471`, `tools/codex-context-probe.ps1:222`).
- **(c) Pre-existing limitation:** the tool probe measures MCP tools through `app-server`, explicitly leaving the actual `exec` surface unmeasured. Existing notes already discuss reviewer subagents, so recognizing `multi_agent_role` does not establish a newly introduced capability (`skills/multi-model-verify/references/model-prompting-notes.md:202`, `skills/multi-model-verify/references/model-prompting-notes.md:211`). The plan does not claim to close this documented gap.

PASS

## 11. Model override and round evidence

The dispatch mechanism and brief binding are model-independent: dispatch copies the supplied body, classifies its completion, and requires separate lane evidence; binding checks session attribution and prompt bytes (`tools/dispatch-round.ps1:530`, `tools/dispatch-round.ps1:815`, `skills/multi-model-verify/references/model-prompting-notes.md:403`, `skills/multi-model-verify/references/model-prompting-notes.md:665`).

However, the **route check does depend on the expected model**: current instructions require comparison against the canonical declaration (`skills/multi-model-verify/references/model-prompting-notes.md:253`). The plan’s debate record does not yet contain the asserted deliberate one-round override; it records the pending debate and voided attempt (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:1267`).

FIX (add an explicit debate-record note identifying this round’s user-directed Astra/high override of the installed Sol declaration, requiring route comparison against that explicit pair and the unchanged dispatch/binding checks; record actual completion evidence before asserting equivalence).

## 12. FULL versus ESCALATE

The brief’s “ESCALATE stays DEGRADED” premise is incorrect, but revision 6 already corrected the **plan**: outcome and verification status are independent, and escalation requires the user’s recorded decision before freezing (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:1271`). This matches the separate fields and freezing requirements (`skills/multi-model-verify/references/frozen-plan-format.md:54`, `skills/multi-model-verify/references/frozen-plan-format.md:126`). Degraded rules concern missing verification, including single-vendor participation, rather than disagreement itself (`skills/multi-model-verify/references/fallbacks.md:274`).

PASS

## Class sweep

Searched all requested directories and files, including filenames, with these shapes:

- **Word `Sol`:** no additional missed live labels in the required scope. Existing live matches are covered by Tasks 2–3: `README.md:27`, `README.md:48`, `README.md:66`, `README.md:258`, `README.md:267`, `CLAUDE.md:134`, `skills/multi-model-verify/SKILL.md:213`, `skills/multi-model-verify/references/panels.md:4`, `skills/multi-model-verify/references/panels.md:12`, `skills/multi-model-verify/references/panels.md:14`, `skills/multi-model-verify/references/panels.md:49`, `skills/multi-model-verify/references/fallbacks.md:217`, `skills/multi-model-verify/references/fallbacks.md:236`, `skills/multi-model-verify/references/frozen-plan-format.md:103`. Later notes references are addressed by revision 6 (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:423`).
- **`GPT-5.6`:** no missed live instance. Matches occur in the seat table and reviewer guidance being rewritten (`README.md:27`, `skills/multi-model-verify/references/model-prompting-notes.md:141`, `skills/multi-model-verify/references/model-prompting-notes.md:157`).
- **`5.6`:** no missed live instance. Remaining guidance, resume provenance, and tier-probe references are covered by Task 2 or historical (`skills/multi-model-verify/references/model-prompting-notes.md:167`, `skills/multi-model-verify/references/model-prompting-notes.md:298`, `skills/multi-model-verify/references/model-prompting-notes.md:507`, `skills/multi-model-verify/references/model-prompting-notes.md:546`).
- **Lowercase `sol` within identifiers/model IDs or filenames:** model-ID matches at `skills/multi-model-verify/references/model-prompting-notes.md:152` and `skills/multi-model-verify/references/model-prompting-notes.md:507`; no additional live identifier or filename found.

Historical review attributions remain historical, including `hooks/superpowers-review-companion.ps1:23`, `tools/check-drift.ps1:81`, `tools/verify-attestation.ps1:5`, and `tools/write-attestation.ps1:23`.

The supplementary fixture sweep found the missed live header reported in claim 5: `evals/tools/run_behavioral_evals.py:251`.

## UNVERIFIED

- **Claims 4 and 7:** post-edit pytest/lint results were not executed. `python` is unavailable on PATH; the budget was independently calculated using the checked-in estimator (`evals/tools/skill_lint.py:339`).
- **Claim 8:** external page contents, account configuration, cache contents, and behavioral measurements were not independently verified. Only their wording and attribution were reviewed, as requested (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:353`).
- **Claim 10:** original live CLI failure/probe history and successful execution under both hosts were not independently reproduced. The checked-in parser was exercised in memory under the current host (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:702`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:1198`).
- **Claims 11–12:** this round’s actual model/effort header, installed dispatch version, session ID, final wrapper classification, and post-round binding result were unavailable as completed evidence in this working directory. The pending record cannot establish them (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:1267`).

Overall: FIX — Add the missed generated escalation-table label and explicitly record the one-round model override with its required route and completion evidence.