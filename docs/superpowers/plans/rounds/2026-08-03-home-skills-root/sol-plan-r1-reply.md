The draft is not safe to freeze. Two defects can directly produce a false clean; a third leaves the central exhaustiveness claim unproven.

## Findings ranked by false-clean risk

1. **Cells A and E do not have the canary states declared in the table.**

   The table requires A to have no canary and E to have only the debate-home canary (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:409-415`). But Step 2 plants the real-home canary before A, and Step 8 removes it only after E (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:434-450`). Therefore A is not a canary-absent baseline, and E has canaries in both roots. A/B equality can conceal a canary-induced change shared by both, while E cannot attribute its positive to the controlled root.

   **Required revision:** run A first; plant the real canary; run B/C/D inside an enclosing cleanup block; remove and verify it; only then plant the debate-home canary and run E.

2. **Readout 3 can falsely validate E because the cells use different homes.**

   Every cell receives its own throwaway home (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:405`), yet the plan says everything except the two experimental variables is constant (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:407`). The draft itself acknowledges that a schema may embed the home path and therefore calls readout 3 corroboration (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:618-619`). The gate contradicts that limitation: E may validate the experiment by firing on any readout, including a hash difference, and that can unlock NOT REACHABLE (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:425-430`).

   **Required revision:** rebuild each cell at the same resolved debate-home path, or make hash/count differences corroboration only. E should establish sensitivity through an attributable nonce-bearing result, not an unexplained cross-home hash difference.

   Five dispatches are not redundant: A/B answer current-lane exposure, C/D answer flag suppression, and D/E provide the negative/control pair (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:411-415`). Five remains the minimum if the timing and home identity are corrected.

3. **The plan does not establish that the three readouts exhaust Skill delivery paths.**

   `Skill` is a tool, not system-prompt text (`skills/multi-model-verify/references/kimi-reviewer-agent.md:10-27`). The current experiment deliberately avoids asking the model to use it (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:79-81`). Yet the recorded protocol supports a later tool loop: tool calls and raw tool results enter the wire transcript before another `llm.request` (`evals/multi-model-verify/fixtures/kimi-round/fresh-wire.jsonl:13-18`), and the validator explicitly permits multiple requests (`tools/read-kimi-round-evidence.ps1:803-805`).

   Nothing read establishes that kimi-code must eagerly encode every discoverable skill into the system prompt or Skill schema. A generic, invariant Skill schema followed by lookup on invocation is therefore an unclosed path, not a demonstrated client behavior.

   **Required revision:** make C/D/E request the exact fixed canary by name. E must produce a logged tool result containing the nonce or the probe is VOID. That exercises the possible lazy path while the inert canary prevents instruction execution.

4. **Cleanup is a later step, not a harness guarantee.**

   The displayed plant call has no enclosing `finally`; removal is a separate Step 8 (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:434-450`). The draft expressly concedes that an interrupted session leaves the directory behind (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:439-440`). Also, the proposed negative test requires only that a state-file canary path be “under” the root, while removal recursively deletes that path (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:253-266`). It does not require the state path to equal `<resolved-root>/parallax-home-root-canary` or verify that the directory still contains exactly the file the harness created.

   **Required revision:** wrap every post-plant operation in `try/finally`; require exact root and canary-path equality; verify the expected `SKILL.md` bytes and refuse unexpected normal entries as well as reparse points before deletion.

   Planting in the real root is methodologically justified because that non-relocated root is the subject, while `-Root` exists only to let tests use scratch space (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:42-48`, `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:77`). It is not justified until cleanup is mechanically strengthened.

5. **The probe-agent leak guard is narrower than its claim.**

   The plan says everything under `references/` is lane contract (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:78`), but the proposed test checks only four named documents (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:326-349`). Other contract files exist, including `application-checkpoint.md`, `debate-protocol.md`, `frozen-plan-format.md`, and `model-prompting-notes.md` (`skills/multi-model-verify/references/application-checkpoint.md:1`, `skills/multi-model-verify/references/debate-protocol.md:1`, `skills/multi-model-verify/references/frozen-plan-format.md:1`, `skills/multi-model-verify/references/model-prompting-notes.md:1`).

   **Required revision:** recursively sweep the entire lane contract/dispatch surface for the probe path, and compare probe frontmatter against the review agent so the only tool-list delta permitted is moving `Skill`.

6. **Task 1’s CI oracle is count-based, not structural.**

   Current CI genuinely runs both modules once in each Windows host step (`.github/workflows/skill-evals.yml:82-112`), and both headers are stale (`evals/multi-model-verify/test_codex_context_probe.py:50-53`, `evals/multi-model-verify/test_review_mirror.py:31-34`). But `workflow.count(rel) == 2` only proves two textual occurrences (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:123-135`). Both occurrences could move into one step or comments while the oracle remained green.

   **Required revision:** assert one occurrence inside each named host step’s `run` block, coupled to `PARALLAX_PS_HOST: powershell.exe` and `pwsh.exe`.

## UNVERIFIED

- **Claims 2 and 5:** the actual kimi-code 0.31.1 `Skill` schema and whether skill resolution is eager or invocation-time. The inspected snapshot excludes `Skill` because the current agent denies it (`evals/multi-model-verify/fixtures/kimi-round/fresh-wire.jsonl:3-10`).
- **Cross-home hash stability:** the plan explicitly leaves open whether schemas embed the home or workspace path (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:618-619`).

## Verdicts per claim

1. **FIX** — the earlier result is confounded, but offering `Skill` alone does not make silence coverage; the plan itself requires a firing positive control (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:17-20`, `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:425-426`). Also correct the citation: `Skill` is line 21, and the deny list continues through line 27 (`skills/multi-model-verify/references/kimi-reviewer-agent.md:10-27`).

2. **FIX** — prompt and schema readouts are strongly enforced (`tools/read-kimi-round-evidence.ps1:744-780`, `tools/read-kimi-round-evidence.ps1:865-879`), but invocation-time delivery is not exercised. Add an exact-canary Skill invocation with a nonce-bearing tool-result control.

3. **FIX** — the positive-control principle is correct, but E currently also contains the real-home canary and permits an unattributed cross-home hash difference to count as firing (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:425-445`).

4. **PASS** — the canary contains the nonce in inert metadata/body and no instruction (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:58-73`). Inertness does not impair a sent-content or forced-load measurement.

5. **FIX** — the containment rationale is sound, but “cannot weaken” depends on the unverified eager-loading premise. The prompt deliberately prevents exercising `Skill` (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:79-81`).

6. **FIX** — removal is not guaranteed without an enclosing `finally`, and the draft acknowledges interruption residue (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:434-450`).

7. **FIX** — the probe file is separated from lane contract, but the proposed absence sweep does not cover every lane-contract file (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:326-349`).

8. **PASS** — the validator derives exact tool count and snapshot names from the supplied agent file, so six tools are validated as strictly as five (`tools/read-kimi-round-evidence.ps1:756-780`, `tools/read-kimi-round-evidence.ps1:865-867`).

9. **FIX** — the record correction is accurate and has no plugin-runtime effect, but the count-only oracle does not prove one module occurrence under each host step (`.github/workflows/skill-evals.yml:82-112`, `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:123-135`).

10. **PASS** — all non-NOT-REACHABLE branches halt and reopen the debate; Task 5 is reachable only from NOT REACHABLE (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:423-430`, `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:464-466`).

