### 1. Single-sourced reviewer identity

The executable configuration is single-sourced: the runner parses the canonical pair at `evals/tools/run_behavioral_evals.py:813`, drift does so at `tools/check-drift.ps1:1010`, and doctor reads the installed declaration at `commands/doctor.md:58`.

“Only literal” needs qualification: a historical probe also contains it at `skills/multi-model-verify/references/model-prompting-notes.md:507`. That does not introduce another configuration source. The plan explicitly preserves historical probes at `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:58`.

**Pre-existing coverage limitation:** the sweep enumerates specific globs, including neither `agents/` nor arbitrary repository files; “everywhere else” overstates its reach (`evals/multi-model-verify/test_multi_model_verify.py:804`). The required class sweep found no missed executable declaration there.

PASS

### 2. Alternate declarations and parsers

The recursive source scan of `evals/` and `tools/` found no loose `model id:` parser that would select the alternate. The executable expressions include the full canonical labels (`evals/tools/run_behavioral_evals.py:813`, `tools/check-drift.ps1:1010`); backup tests explicitly verify separation even under case-insensitive matching (`evals/multi-model-verify/test_backup_lane.py:71`).

The proposed alternate labels differ from those expressions and follow the canonical pair (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:333`).

PASS

### 3. Alternate literal inside the new test

The sweep checks the current declaration, the contiguous flag marker, and a regex requiring preceding `-m` (`evals/multi-model-verify/test_multi_model_verify.py:791`, `evals/multi-model-verify/test_multi_model_verify.py:801`). The proposed alternate assertion contains neither flag shape (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:279`).

Once the canonical declaration changes, that alternate literal is legal. The plan correctly names its temporary single-source failure before the change (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:298`).

PASS

### 4. Contract-pin ordering

The red command selects only the specified test module; the later command includes contract coverage after the notes and naming-region edits (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:296`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:501`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:510`).

Coverage checks complete regions against collected pins, so the temporary mismatch is real but lies outside that red command (`evals/multi-model-verify/test_contract_coverage.py:945`).

PASS

### 5. Live-label rename completeness

No additional live-label omission was found. Task 2 covers the notes’ operative references, and Task 3 covers the remaining documents and fixture labels (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:423`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:533`).

The brief’s abbreviated list omits two fixture cells, but the frozen plan already explicitly changes both: the raised-by cell and “Sol position” header (`evals/tools/run_behavioral_evals.py:248`, `evals/tools/run_behavioral_evals.py:251`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:641`).

PASS

### 6. Raw versus normalized pins

The composition test uses `_read`, which returns raw text, then searches the concatenated literal directly (`evals/multi-model-verify/test_seat_reshuffle.py:16`, `evals/multi-model-verify/test_seat_reshuffle.py:130`). Those phrases must remain on single physical lines.

The naming pin explicitly normalizes whitespace with `" ".join(...split())` (`evals/multi-model-verify/test_multi_model_verify.py:1327`). The plan correctly distinguishes these requirements (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:47`).

PASS

### 7. SKILL.md scope and ceiling

The only `Sol` label in SKILL.md is the example at `skills/multi-model-verify/SKILL.md:213`. The plan changes that word alone and requires recording the subsequent lint count (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:607`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:691`).

I reproduced **6,456 before / 6,457 after** using the lint’s body extraction and `len(body) // 4` formula (`evals/tools/skill_lint.py:182`, `evals/tools/skill_lint.py:339`). These are estimates, not tokenizer counts. The plan’s stop-at-6500 rule is slightly stricter than the lint’s greater-than-6500 error condition (`evals/tools/skill_lint.py:340`).

PASS

### 8. Evidence-width discipline

The replacement dates and attributes the old and current guidance, explicitly retains the brief structure as repository convention, and says the lean-prompt result has not been remeasured (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:355`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:369`).

Clarification behavior is attributed to the guide and marked UNMEASURED under exec; cache applicability remains unknown. The config observation is dated, and effort carryover is attributed to dated migration guidance (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:377`, `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:408`).

PASS

### 9. Opt-in alternate versus fallback

The replacement requires the user to name Sol and expressly excludes it from fallback classes and consent-gate offers (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:341`). The panel transport amendment makes it an alternate occupant of the codex seat (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:588`).

Existing substitution machinery points to the separate backup lane, whose failures are Kimi-specific (`skills/multi-model-verify/references/fallbacks.md:159`, `skills/multi-model-verify/references/fallbacks.md:179`); panels likewise distinguish the codex seat from the consent-gated Kimi backup (`skills/multi-model-verify/references/panels.md:4`). The planned fallback edits change labels only.

PASS

### 10. Context-probe contract

The Task 4 implementation is already present in this checkout. Both lists include the new families, and the mask uses ordinal matching of the exact backtick-wrapped literal (`tools/codex-context-probe.ps1:421`, `tools/codex-context-probe.ps1:436`, `tools/codex-context-probe.ps1:483`).

I exercised the parser in memory under **both PowerShell hosts**. The exact quote passed; missing backticks, different inner text, and a genuine second container refused; an unknown family remained reported; an attributed known tag refused. These correspond to the refusal contracts at `evals/multi-model-verify/test_codex_context_probe.py:400`, `evals/multi-model-verify/test_codex_context_probe.py:408`, `evals/multi-model-verify/test_codex_context_probe.py:418`, `evals/multi-model-verify/test_codex_context_probe.py:426`, and `evals/multi-model-verify/test_codex_context_probe.py:998`.

- **(a)** Early masking inside INSTRUCTIONS preserves length and changes neither INSTRUCTIONS delimiter. Valid instruction bodies are subsequently blanked; malformed INSTRUCTIONS still refuse (`tools/codex-context-probe.ps1:483`, `tools/codex-context-probe.ps1:490`).
- **(b)** `$only` changes the names being processed, but does not bypass the literal mask. The skill parser uses this same function repeatedly (`tools/codex-context-probe.ps1:471`, `tools/codex-context-probe.ps1:221`).
- **(c), pre-existing gap:** native delegation is outside the MCP inventory measurement. Delegation already appears in the existing Sol effort discussion, while the tool probe explicitly measures MCP through a different subcommand (`skills/multi-model-verify/references/model-prompting-notes.md:202`, `skills/multi-model-verify/references/model-prompting-notes.md:211`). Naming the family changes parser acceptance, not tool grants. The existing “proxy, never verified isolation” limitation already bounds the claim (`skills/multi-model-verify/references/model-prompting-notes.md:217`).

PASS

### 11. Override and evidence strength

The dispatch receipt and classification contain no model field; the lane supplies its invocation body (`tools/dispatch-round.ps1:196`, `tools/dispatch-round.ps1:530`, `tools/dispatch-round.ps1:747`). Brief binding operates on session attribution, record structure, and canonicalized brief hashes (`skills/multi-model-verify/references/model-prompting-notes.md:665`, `skills/multi-model-verify/references/model-prompting-notes.md:684`).

The surrounding **route check does depend on the expected model** (`skills/multi-model-verify/references/model-prompting-notes.md:253`). Revision 7 explicitly substitutes the authorized Astra/high pair for this round while retaining the remaining checks (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:1277`). Thus the override preserves the same evidence requirements; actual completion remains unverified below.

PASS

### 12. Verification status after adjudication

The brief’s assertion that ESCALATE necessarily leaves DEGRADED is refuted. Outcome and verification status are independent fields; freezing an escalated plan additionally requires the user’s recorded decision (`skills/multi-model-verify/references/frozen-plan-format.md:54`, `skills/multi-model-verify/references/frozen-plan-format.md:126`). Degraded rules concern missing cross-vendor verification, not disagreement (`skills/multi-model-verify/references/fallbacks.md:274`).

**The frozen plan already states the correct handling**, including FULL when evidence requirements are met regardless of outcome (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:1274`). No plan amendment is needed.

PASS

### Class sweep

Searched recursively through `skills/`, `commands/`, `agents/`, and `hooks/`, plus `tools/*.ps1`, README.md and CLAUDE.md. Shapes searched: whole-word `Sol`, literal `GPT-5.6`, literal `5.6`, lowercase `sol` within words/identifiers, and filenames containing `sol`.

- **`Sol`: no missed live instance found.** Covered matches are at `README.md:27`, `README.md:48`, `README.md:66`, `README.md:258`, `README.md:267`, `CLAUDE.md:134`, `skills/multi-model-verify/SKILL.md:213`, `skills/multi-model-verify/references/panels.md:4`, `skills/multi-model-verify/references/panels.md:12`, `skills/multi-model-verify/references/panels.md:14`, `skills/multi-model-verify/references/panels.md:49`, `skills/multi-model-verify/references/fallbacks.md:217`, `skills/multi-model-verify/references/fallbacks.md:236`, and `skills/multi-model-verify/references/frozen-plan-format.md:103`.
- **Notes’ operative labels are covered by Task 2:** `skills/multi-model-verify/references/model-prompting-notes.md:141`, `:156`, `:183`, `:202`, `:298`, `:482`, `:542`, `:546`, `:568`; the replacement and additional edits are specified at `docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:308` and `:423`.
- **`GPT-5.6` / `5.6`: no missed live instance found.** Matches occur in the README seat and notes’ heading, declarations, guidance, and dated probes (`README.md:27`; `skills/multi-model-verify/references/model-prompting-notes.md:141`, `:152`, `:157`, `:167`, `:171`, `:173`, `:177`, `:207`, `:298`, `:507`, `:546`).
- **Lowercase `sol`: no missed live identifier or filename found.** Model-token matches are the declaration and historical probe (`skills/multi-model-verify/references/model-prompting-notes.md:152`, `:507`). Broader substring matches were unrelated vocabulary such as `resolved`, `isolation`, and `Console`.
- **Historical matches remain historical:** review-attribution comments in `hooks/superpowers-review-companion.ps1:23`, `:35`; `tools/check-drift.ps1:51`, `:81`, `:567`, `:726`, `:802`, `:828`, `:873`, `:968`, `:1018`, `:1124`; `tools/verify-attestation.ps1:5`, `:45`, `:94`; and `tools/write-attestation.ps1:23`, `:78`.

### UNVERIFIED

- **Claims 3–4 and 7:** I did not run pytest or the Python lint command because Python was unavailable on PATH. Ordering and formula results were verified from source; future green runs remain implementation-time checks (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:510`, `:683`).
- **Claim 8:** External guidance contents, the actual config read, and cache observations were not independently verified. Only their attribution and qualification were reviewed (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:355`, `:377`, `:408`).
- **Claim 10:** Original live 0.153.4 measurements and the complete native exec tool inventory were not reproduced. Synthetic parser checks do not establish those facts (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:705`; `skills/multi-model-verify/references/model-prompting-notes.md:217`).
- **Claims 11–12:** This round’s actual resolved header, installed dispatch provenance, final wrapper classification, sealed binder result, and subsequent record update cannot be established from the pending completion entry (`docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md:1277`).

Overall: PASS — No additional plan defect was found; the stale assertions in claims 11–12 are already addressed by the frozen plan’s explicit override and independent status rules.