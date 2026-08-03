A false-clean path survives revision 3: NOT REACHABLE does not exclude primary-readout positives in B or C. A second ambiguity remains in what “matching the not-found shape exactly” means.

## False-clean findings

1. **The gate ignores some primary positives.**

   Readout 1 is nonce presence anywhere, and readout 2 is prompt-length divergence for every cell (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:493-497`). But:

   - B is declared reachable only on readout 2, so a nonce appearing in B’s wire while its prompt length remains unchanged is ignored (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:511-512`).
   - C can carry the nonce outside its normalized result or diverge on readout 2, yet NOT REACHABLE requires only that C’s result match E2’s not-found shape (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:509-512`).
   - A is described as the canary-absent baseline, but the gate never requires its nonce readout to be negative (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:516`).

   **Required change:** make A’s clean primary readouts a validity precondition. NOT REACHABLE must require that B, C, and D fire on neither primary readout, in addition to C/D’s valid not-found results. B firing either primary means REACHABLE EVEN AS CONFIGURED; C firing while D does not is an unexpected/inverted result that stops rather than passes.

2. **“Matches that shape exactly” is not yet a deterministic oracle.**

   The plan alternates between recording E2’s result verbatim and comparing only its “shape” (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:503-505`, `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:551`). Wire events contain per-call identifiers such as `parentUuid`, `toolCallId`, and `traceId`, while the substantive tool payload sits under `result` (`evals/multi-model-verify/fixtures/kimi-round/fresh-wire.jsonl:13-18`). Full-record equality therefore cannot hold, while an unspecified structural comparison could ignore the very output/error distinction the oracle exists to preserve.

   **Required change:** freeze the canonical comparison explicitly—e.g. compare the complete `event.result` payload after only a precisely named substitution of the requested skill identifier, with no removal of status, error, or output fields. If that canonicalization cannot be defined from E2’s observed result, the probe is VOID.

## Direct answers

**b. PASS — keep E2 as a resume.** Same-session calibration preserves the exact bound agent and tool surface, while a warmed-path difference can only make C/D fail to match and therefore fail closed (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:503-505`, `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:551`). A fresh-home calibration would introduce another configuration boundary without improving the false-clean direction.

**c. PASS — unrunnable is acceptable.** The generic record shape is already evidenced: calls and matching results carry `toolCallId` (`evals/multi-model-verify/fixtures/kimi-round/fresh-wire.jsonl:13-18`). If this client/tool emits another shape, classifying the cell FAILED is the correct direction under the plan’s fail-closed invariant (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:37-40`). A pre-probe may save time, but is not required for correctness.

**d. Two non-false-clean consistency fixes remain.**

- Task 4 says the client is dispatched five times and every cell is FRESH with its own home, but E2 is a sixth client call and a RESUME sharing E’s home (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:474-481`, `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:551`). State this as five fresh cells plus one resumed calibration, and validate E2 using the validator’s RESUME form.
- The open question still calls five dispatches the minimum without accounting for E2 or the separate write-probe call (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:541`, `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:720`).

Verdicts:

- **a. FIX** — require primary-readout negatives for A/B/C/D before NOT REACHABLE, and freeze the E2-result canonicalization.
- **b. PASS** — resumed E2 is the safer calibration boundary.
- **c. PASS** — unknown record shape should fail closed; pre-probing is optional efficiency.
- **d. FIX** — correct the fresh/resume and dispatch-count contradictions.