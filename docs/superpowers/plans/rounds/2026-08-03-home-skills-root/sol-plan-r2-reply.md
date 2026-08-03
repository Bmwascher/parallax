A false-clean path survives revision 2: silence in C or D still counts even when no valid Skill lookup was completed. A second gate contradiction lets E validate through readout 2 without the mandatory nonce-bearing `tool.result`.

## False-clean findings

1. **C and D do not have an invocation-validity gate.**

   The prompt asks the model to invoke Skill, but the plan correctly says a model reply is never the measurement (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:101-109`). Nevertheless, NOT REACHABLE requires only that C and D lack the nonce and prompt-length divergence; it does not require either cell to contain a `tool.call` or corresponding `tool.result` (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:491-496`).

   Thus D can be counted negative if the model:

   - replies `SKILL-NOT-FOUND` without calling Skill;
   - calls Skill with malformed or different arguments;
   - produces a tool error or loses its result;
   - invokes another tool instead.

   E proving that its own model turn invoked Skill does not prove C or D did. The wire format provides the necessary evidence: calls identify the tool and arguments, and results carry a matching `toolCallId` (`evals/multi-model-verify/fixtures/kimi-round/fresh-wire.jsonl:13-18`).

   **Required change:** C, D, and E are valid only if the wire contains the required `tool.call` with exact canary identifier and a matching `tool.result`. Missing, duplicate, malformed, mismatched, or errored calls make that cell FAILED/VOID, never negative.

   A non-nonce result also needs a frozen not-found oracle. Otherwise an infrastructure/tool failure is indistinguishable from successful lookup returning “not found,” contrary to the fail-closed invariant (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:27-30`). If kimi-code exposes no structural success/error field, calibrate the exact not-found result with a deliberately absent skill before allowing C or D’s result to count as negative.

2. **The on-disk E gate does not implement the claimed mandatory tool-result control.**

   Revision history says E is VOID unless it produces a nonce-bearing `tool.result` (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:9-13`). The actual gate instead declares VOID only when both that result and prompt-length divergence are absent, allowing readout 2 alone to validate E (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:491-492`).

   That matters because an eager prompt injection in E could designate readout 2 while C/D never complete their invocation-time lookup. The plan could then reach NOT REACHABLE from unrelated silence.

   **Required change:** require E’s exact Skill call plus matching nonce-bearing `tool.result` unconditionally. Readout 2 may additionally fire, but cannot substitute for the invocation control.

## Direct answers

**b. The exact canary name is the right identifier.** The directory name and frontmatter `name` are identical (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:72-80`), and E tests that same identifier at a known root (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:529`). No read artifact establishes root-specific renaming or namespacing, so I would not manufacture that objection. The missing protection is evidence that C/D actually submitted that exact identifier, not broader skill enumeration.

**c. Extra VOID is the acceptable direction.** If kimi-code carries content through another record type, insisting on a nonce-bearing `tool.result` may reject a working instrument, but it cannot authorize NOT REACHABLE. That matches the plan’s invariant that unreadable or unmade measurements refuse rather than pass (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:27-30`). The gate should state this unconditionally, as above.

**d. The `finally` covers failures during B/C/D, but not every planting failure.** The real-home mutation and `$LASTEXITCODE` check happen before entry into `try` (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:504-515`). If Plant creates the directory and then fails while writing state or returning, the throw at line 509 bypasses cleanup. Hard host termination also skips the block, which the plan acknowledges (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:525`).

Move Plant inside an outer `try`, and require the Plant implementation itself to roll back any partial mutation when it cannot successfully emit the state needed for safe removal. Removal failure should still stop before E, as Step 4 already requires (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:527`).

## Non-false-clean residue

Task 5 still claims the hashes were identical even though the revised gate neither requires nor attributes that equality (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:485-496`, `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:562-578`). It also says the client “advertises” skills through Skill despite revision 2 explicitly accommodating invocation-time lookup (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:61`, `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:609-612`). Those statements should be rewritten to match the actual primary evidence.

Verdicts:

- **a. FIX** — require an exact, matched, successful Skill call/result in C and D before silence can count; require E’s nonce-bearing result unconditionally.
- **b. PASS** — exact name is appropriately bounded; no evidenced alternate-name path.
- **c. PASS on direction, FIX on implementation** — conservative VOID is correct, but the current gate still lets readout 2 substitute.
- **d. FIX** — cleanup covers cell failures after entry into `try`, not partial Plant failure or host termination.