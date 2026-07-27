# Required whole-branch fable review — retained range-bound artifact (UNTRACKED through ship)

Base: c95a09383ff004e5367972451757dd8e111b0dc7
Head: 451ce7b380b07eb2acf54033abce2b06c600c786
Reviewer: installed parallax:fable-reviewer (model pin `fable`, 0.14.0 cache hash-verified), agent id af1fa12810ca194e3, dispatched 2026-07-26 with the frozen plan, the SDD ledger, and the controller-built diff package for this exact range (review-c95a093..451ce7b.diff — differs from the prior range's package only in the two head-sha lines; 451ce7b is tree-identical to b10a9c0). THIS REPORT SUPERSEDES the prior reviews at c95a093..d24fd96 and c95a093..b10a9c0 (raw replies preserved in the session transcript; all their findings adjudicated and discharged — see the ledger).
Session adjudication of THIS report's minor (to be cited by the mode-diff round-3 brief): Minor 1 (smoke-sol-clean-brief.md's in-file status line predates its supersession under the narrow ruling) ACCEPTED-DEFERRED to 0.14.1 as a marker-prepend — the same head-immobility rationale the reviewer itself applies: a commit now would move the reviewed head mid-debate; the demotion is already recorded in the committed quarantine markers' cross-references and the ledger's final panel record.

--- RAW REPLY VERBATIM ---

### Strengths

- **Contract surfaces are byte-exact against the frozen plan.** Every planned artifact matches its plan-specified content exactly: `evals/multi-model-verify/test_seat_reshuffle.py:1-151` (all ten pins verbatim per Task 1), the three agent files (`agents/fable-reviewer.md`, `agents/fable-panel-reviewer.md`, `agents/escalation-implementer.md` — frontmatter pins `model: fable` only, read-only `tools: Read, Grep, Glob` on both reviewer seats, no tools line on the escalation implementer per plan), `skills/multi-model-verify/references/panels.md:1-85`, the four anchored insertions (fallbacks.md panel-lane-loss block, frozen-plan-format.md envelope + panel-recording blocks, backup-lane.md participation paragraph), the SKILL.md required-step/carve-out/panel-pointer edits, the notes driver-seat restructure, and the wholesale README/CLAUDE.md rewrite. Task 3's registry append (`evals/multi-model-verify/test_multi_model_verify.py`, `"panels.md"` after `"backup-lane.md"`) landed in the same commit as the file it registers, per spec section 11.
- **Global Constraints hold on the range.** Pinned sentences live on single physical lines where tests count occurrences (package lines 7071, 7124, 7157, 7194, 7231, 7432, 7434, 7465); both 0.13.0 README pins survive byte-exact (backup-lane table row visible at package line 244; suite green 164/1 per ledger confirms the mermaid pin mechanically); no new `-m <literal>` anywhere in the instruction surfaces; all 24 commit subjects are lowercase imperative with the `0.14.0:` prefix.
- **The row-12 reopened-debate amendment is correctly and symmetrically applied**: `skills/multi-model-verify/references/backup-lane.md:4-7` ("enters through the fallbacks.md consent gate … or via a user-invoked panel (the participation paragraph below)") and the notes backup-block ending (package lines 7398-7399), with the debate-record row and user authorization in the frozen plan's appendix (row 12) and ledger.
- **The remediation chain is honest and legible in-file.** Both contaminated Sol smoke replies carry driver quarantine markers naming the incident, the narrow ruling, and the replacement lane (`smoke-sol-r1-reply.md:1`, `smoke-sol-r2-reply.md:1`, package lines 3937/5174), with bodies byte-preserved. The clean sol2 lane is evidence-complete: fresh blind dispatch with canonical header (gpt-5.6-sol / openai / read-only / high, session 019f9fe5-e676-77b3-9baf-e439d5d0b737, package lines 5590-5600), same-session resume echoing that id (5938-5947), terminal PASS citing the pinned subject revision HEAD c95f18e + blob 69dbdb0f.
- **Evidence-class discipline in the Fable panel lane replies**: both smoke-fable replies self-report their UNVERIFIED residue (blob pin not independently computable under a read-only grant) rather than folding it into the verdict (`smoke-fable-r1-reply.md`, package lines 3015-3016; `smoke-fable-r2-reply.md`, lines 3051-3054) — exactly the contract the new agents codify.
- **The redo gates worked as designed**: the first redo attempt was discarded on tree-identity failure (swept untracked artifact) instead of shipped, and the corrected 451ce7b passed the tree-identical, sweep-clean, and porcelain-scope gates with mechanical checkpoint provenance (CreationTime 14:48:56 < commit 14:49:48) recorded in the ledger.

### Issues

#### Critical

None.

#### Important

None.

#### Minor

1. **`docs/superpowers/plans/rounds/2026-07-26-seat-reshuffle/smoke-sol-clean-brief.md:1` — in-file status now misleading relative to the final record.** The brief opens "Fresh-session dispatch replacing two quarantined rounds", but under the ratified narrow ruling that round is itself SUPERSEDED-AS-RECORD (retained as corroboration only; the sol2 sequence is the lane of record). The quarantined replies and the sol2 briefs cross-reference each other correctly in-file, but the sol-clean pair's demotion is legible only in the gitignored ledger — a future reader of the committed rounds/ directory could take it for the terminal round of record. Fixing it now would move the reviewed head mid-debate (the same head-immobility rationale that once deferred M1), so this rides to 0.14.1 as a marker-prepend alongside nothing else.

### Ledger minors triage

- **M1 (d24fd96 review: bare quarantine markers on committed sol smoke replies)** — DISCHARGED in this range: the markers are committed in-file (package lines 3937, 5174). Nothing rides.
- **M2 (empty-prompt artifact provenance)** — REFUTED by session adjudication (spec-phase advisory evidence); no action. Ride as adjudicated.
- **M3 (strictest-lane FULL reading)** — DISCHARGED: put to the debate and ratified NARROW in round 1; the v3 panel record conforms (no quarantined participating-lane rounds counted).
- **M1' (b10a9c0 review: ledger update — sol2 metadata, sweep evidence, final record)** — DISCHARGED by ledger lines 44 and 46. Ride.
- **M2' (sol-clean status line)** — DISCHARGED at ledger level (line 46); the in-file residual is my Minor 1 above. Ride to 0.14.1.
- **M3' (codex v0.144.1 models-cache schema ERROR in transcripts)** — DISCHARGED as a recorded drift note (ledger line 47; visible live at package line 5590); route resolution unaffected, watch class assigned to doctor/0.15.0. Ride.
- **Dead-agent case OPEN** — by design (observation scope, probe record); ride, never claimed covered.
- **Diff-brief obligations (cite debate-record row 12; disclose the AGENTS.md incident)** — not code fixes; they are round-brief obligations and must be honored in the round-3 brief before merge. The round-1 brief already carried them per ledger.

### Assessment

Ready to merge: Yes — 0 Critical, 0 Important, 1 Minor (riding to 0.14.1). The range implements the frozen plan byte-exact with all Global Constraints holding, the reopened-debate amendment properly recorded, and an incident/remediation trail that is unusually well evidenced; the head is tree-identical to the previously reviewed b10a9c0 with all prior findings adjudicated and discharged. The cross-vendor mode-diff debate (round 3 pending) remains the merge gate; this review never replaces it.

**Named-risk checks:** none required — all conclusions were reachable from the three provided inputs; no repo file was read outside them.

**Gaps (state the package lacks, tool-grant read-only, no Bash):**
- Per-commit composition of 451ce7b (the "exactly 8 files by explicit path" claim) is not derivable from a merged range diff; taken from the ledger's mechanically recorded gate results.
- Tree identity 451ce7b^{tree} == b10a9c0^{tree} (de7c678d…) is controller-asserted in the ledger; I cannot run git to confirm it.
- The pre-dispatch "sweep clean" shell evidence for the sol2 dispatches lives outside the package (ledger-asserted).
- The untracked `rounds/fable-review.md` artifact's SHA-256 (E50DE566…) and the full-suite 164 passed / 1 skipped result are ledger/CI-asserted; not re-computable here.

**Reviewed range:** c95a09383ff004e5367972451757dd8e111b0dc7..451ce7b380b07eb2acf54033abce2b06c600c786 on feat/0140-seat-reshuffle (supersedes the c95a093..d24fd96 and c95a093..b10a9c0 reviews). Inputs: frozen plan `C:\Users\Brandon\Documents\parallax\docs\superpowers\plans\2026-07-26-seat-reshuffle.md`; SDD ledger `C:\Users\Brandon\Documents\parallax\.superpowers\sdd\2026-07-26-seat-reshuffle\progress.md`; controller-built diff package `C:\Users\Brandon\Documents\parallax\.superpowers\sdd\2026-07-26-seat-reshuffle\review-c95a093..451ce7b.diff`.
