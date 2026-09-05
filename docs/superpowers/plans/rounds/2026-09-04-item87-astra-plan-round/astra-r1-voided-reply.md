### 1. Single source

The executable conclusion holds: the runner and drift script parse the declarations, and doctor reads the installed declaration. “Only literal” means the only **live declaration**; a historical invocation also contains it. The sweep covers the explicit paths listed in the test, rather than literally every repository file. (`evals/tools/run_behavioral_evals.py:804`, `tools/check-drift.ps1:1007`, `commands/doctor.md:58`, `skills/multi-model-verify/references/model-prompting-notes.md:507`, `evals/multi-model-verify/test_multi_model_verify.py:804`.)

PASS

### 2. Alternate declaration compatibility

No loose declaration consumer was found in the `evals/` and `tools/` search. The relevant parsers require the canonical phrase; the backup tests also check case-insensitive parsing and ordering. Neither proposed alternate label matches those phrases. (`evals/tools/run_behavioral_evals.py:813`, `tools/check-drift.ps1:1010`, `evals/multi-model-verify/test_backup_lane.py:71`, `evals/multi-model-verify/test_route_parser_shapes.py:78`, `evals/multi-model-verify/test_seat_reshuffle.py:296`.)

PASS

### 3. Alternate literal in the new test

After the declaration changes, the alternate literal matches neither the current canonical-id marker nor the flag-dependent regex. The plan correctly anticipates its temporary single-source failure before that change. (`evals/multi-model-verify/test_multi_model_verify.py:793`, `evals/multi-model-verify/test_multi_model_verify.py:801`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:283`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:303`.)

PASS

### 4. Contract-pin ordering

Step 3 excludes the coverage module; Step 6 includes it after both edits. The coverage check requires the normalized region inside a collected pin, while its declared identifier remains unchanged. The ordering is sound for this region. (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:301`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:423`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:432`, `evals/multi-model-verify/test_contract_coverage.py:760`, `evals/multi-model-verify/test_contract_coverage.py:945`.)

PASS

### 5. Live-label completeness

The list misses operative prose: “claims from Sol” in the fabrication-counter rule and advice that “still applies to Sol” in reusable recipes. Task 2 expressly leaves these later bullets untouched. Preserve the Sol-specific evidence attribution, but address the standing rule and repository convention to the reviewer lane. (`skills/multi-model-verify/references/model-prompting-notes.md:542`, `skills/multi-model-verify/references/model-prompting-notes.md:568`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:316`.)

The synthetic fixture also retains `Raised by: Sol` after its Participants header becomes Astra. This is generated fixture content, not a retained historical debate. Add its row to Step 9. (`evals/tools/run_behavioral_evals.py:216`, `evals/tools/run_behavioral_evals.py:237`, `evals/tools/run_behavioral_evals.py:248`, `evals/tools/run_behavioral_evals.py:319`.)

**Plan change:** expand Tasks 2/3 to cover those instances and the contextual corrections identified in the class sweep; expand Step 10 beyond its current six-file search. (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:563`.)

FIX

### 6. Raw versus normalized pins

The panel test uses `_read`, which returns raw text; the naming-region test explicitly normalizes whitespace. The plan’s physical-line requirements accurately reflect both implementations. (`evals/multi-model-verify/test_seat_reshuffle.py:16`, `evals/multi-model-verify/test_seat_reshuffle.py:130`, `evals/multi-model-verify/test_multi_model_verify.py:1327`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:47`.)

PASS

### 7. SKILL.md budget and edit scope

The only `Sol` label in the full skill is at line 213. Reproducing the linter’s body extraction and character-count estimate in PowerShell gives **6456**, and **6457** after the two-character increase. This is an estimate, not a tokenizer measurement. The plan requires the actual lint rerun and recorded count. (`skills/multi-model-verify/SKILL.md:213`, `evals/tools/skill_lint.py:182`, `evals/tools/skill_lint.py:339`, `evals/tools/skill_lint.py:133`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:584`.)

PASS

### 8. Evidence-width wording

The replacement attributes and dates the guidance, identifies the retained practices as repository conventions, marks clarification behavior under `codex exec` UNMEASURED, leaves cache applicability unknown, dates the config observation, and attributes carrying effort forward to migration advice. This confirms wording only, as requested. (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:353`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:369`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:377`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:408`.)

PASS

### 9. Opt-in alternate

The alternate paragraph expressly excludes automatic selection and fallback-class membership. The panel amendment lets the named alternate occupy the same codex seat; existing substitution machinery points to the separately declared backup lane. Nothing adds Sol to that machinery. (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:341`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:510`, `skills/multi-model-verify/references/panels.md:49`, `skills/multi-model-verify/references/fallbacks.md:159`.)

PASS

### 10. Context-probe contract

The mask itself preserves the tested refusal directions. Direct in-memory checks accepted the exact quote, rejected missing backticks, different inner text, an additional real container and an attributed known tag, and still reported a following unknown family. The implementation uses ordinal matching and preserves offsets. (`tools/codex-context-probe.ps1:483`, `tools/codex-context-probe.ps1:493`, `tools/codex-context-probe.ps1:602`, `tools/codex-context-probe.ps1:613`.)

- **(a)** Masking that literal inside `INSTRUCTIONS` earlier changes no subsequent count: it contains no `INSTRUCTIONS` delimiter, preserves length, and the containing body is then blanked. (`tools/codex-context-probe.ps1:436`, `tools/codex-context-probe.ps1:483`, `tools/codex-context-probe.ps1:529`.)
- **(b)** The mask runs regardless of `$only`; `Get-SkillReport` threads the returned text through the subset calls. My comparison produced identical whole-list and sequential-subset output. (`tools/codex-context-probe.ps1:220`, `tools/codex-context-probe.ps1:471`.)
- **(c), pre-existing:** the tool-surface probe inventories MCP tools through `app-server`, not native delegation capabilities under `exec`. Sol spawning subagents was already documented. Recognizing another prompt family neither measures nor grants those capabilities; this gap predates the plan. (`tools/codex-tool-surface-probe.ps1:10`, `tools/codex-tool-surface-probe.ps1:34`, `skills/multi-model-verify/references/model-prompting-notes.md:202`.)

The **plan’s verification procedure is defective**, however. Step 4’s filter excludes the self-quote and alias tests. Its claimed self-quote refusal results also require the family-list amendment first: before recognition, those cases report an unknown family instead of throwing for ambiguous known boundaries. Additionally, the three proposed tests contain only two refusal cases; no test covers the different-inner-text direction promised by the comment. (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:906`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:912`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:724`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:995`.)

**Plan change:** split red verification into explicitly selected stages: family tests before Step 5; self-quote tests after Step 5 and before Step 5b; alias tests before Step 5c. Add different-inner-text coverage to the refusal test. Keep both full-module host runs afterward. (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:1062`.)

FIX

### 11. Model-independent dispatch and binding

The specified dispatch and brief-binding mechanisms are model-independent: the caller supplies the invocation, the receipt contains no model field, and binding checks session identity, rollout boundaries and canonicalized brief content. Their evidence class remains client echo. (`skills/multi-model-verify/references/model-prompting-notes.md:362`, `tools/dispatch-round.ps1:537`, `skills/multi-model-verify/references/model-prompting-notes.md:665`, `skills/multi-model-verify/references/model-prompting-notes.md:684`, `skills/multi-model-verify/references/model-prompting-notes.md:745`.)

This confirms the mechanism, conditional on checking the actual header against the expressly selected Astra route. Route confirmation remains a separate requirement; model-independent binding alone does not establish it. (`skills/multi-model-verify/references/model-prompting-notes.md:253`.)

PASS

### 12. Debate-record transition

The convergence branch matches the appendix. The ESCALATE branch conflates **outcome** with **verification status**: they are separate fields, and an unresolved disagreement does not itself mean cross-vendor verification was unavailable. After a qualifying debate, `plan-not-debated` is also no longer an accurate description. (`skills/multi-model-verify/references/frozen-plan-format.md:54`, `skills/multi-model-verify/references/frozen-plan-format.md:71`, `skills/multi-model-verify/references/fallbacks.md:274`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:1135`.)

**Plan change:** update the record after adjudication with actual participants, rounds and outcome. Use FULL when the cross-vendor evidence requirements were met; otherwise record the actual degradation and authorization. An escalated outcome still requires the user’s recorded decision before freezing. A brief path does not substitute for a verbatim reply/transcript in `Raw rounds`. (`skills/multi-model-verify/references/frozen-plan-format.md:58`, `skills/multi-model-verify/references/frozen-plan-format.md:79`, `skills/multi-model-verify/references/frozen-plan-format.md:126`.)

FIX

### Class sweep

Searched `skills/`, `commands/`, `agents/`, `hooks/`, `tools/*.ps1`, `README.md` and `CLAUDE.md`, including filenames.

- **Word `Sol`:** missed live uses at `skills/multi-model-verify/references/model-prompting-notes.md:543` and `skills/multi-model-verify/references/model-prompting-notes.md:568`. Preserve the Sol-specific provenance at `:542`; change the operative rule’s subject.
- **`GPT-5.6`:** no missed live label beyond Task 2’s replacement and Task 3’s README edit. Matches are at `skills/multi-model-verify/references/model-prompting-notes.md:141`, `skills/multi-model-verify/references/model-prompting-notes.md:157` and `README.md:27`.
- **`5.6`:** two retained passages need contextual treatment rather than changing the model number. The resume rationale still invokes 5.6 guidance, and the diagnostic sentence connects the **canonical id** to an old Sol/Terra tier probe. Mark these as Sol-era evidence; do not let changing the canonical declaration silently turn the old diagnostic into an Astra measurement. (`skills/multi-model-verify/references/model-prompting-notes.md:298`, `skills/multi-model-verify/references/model-prompting-notes.md:546`.)
- **Lowercase `sol` in identifiers or filenames:** the reviewer-specific identifier matches are the declaration being replaced and the dated historical invocation; no missed live identifier or filename found. (`skills/multi-model-verify/references/model-prompting-notes.md:152`, `skills/multi-model-verify/references/model-prompting-notes.md:507`.)

Historical review comments remain historical, including `hooks/superpowers-review-companion.ps1:23`, `tools/check-drift.ps1:81` and `tools/verify-attestation.ps1:5`. No additional live labels were found in commands, agents, hooks or PowerShell tools.

### UNVERIFIED

- **Claims 3–4 and 7:** actual post-edit pytest/lint results. Python is unavailable on PATH; the budget calculation above reproduces the estimator, not the complete lint execution. Required commands remain at `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:432` and `:576`.
- **Claim 8:** external page contents, original fetches, account probes, config/cache observations and Astra behavioral measurements. Only their wording and attribution were checked. (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:89`, `:353`, `:377`, `:408`.)
- **Claim 10:** the original live blocker sequence and full dual-host/end-to-end results. The workspace contains the amendments; direct checks here exercised the parser in PowerShell 7. (`tools/codex-context-probe.ps1:417`, `:483`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:1062`.)
- **Claim 11:** this round’s actual installed dispatch version, header, effort, receipt and completed binding. The workspace manifest says 0.30.1, but that does not verify the installed invocation. (`.claude-plugin/plugin.json:3`, `commands/doctor.md:15`, `commands/doctor.md:21`.)
- **Claim 12:** the promised future record rewrite; the current record still reports zero rounds and no reviewer. (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:1131`.)

Overall: FIX — complete the live-label/context sweep, repair Task 4’s staged verification, and separate debate outcome from verification status.