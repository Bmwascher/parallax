Reviewed exact head `881b676048208761f97f477ec86ce0585bf42ca2`.

## Verification

- Raw slicing is correctly applied: `$scan` locates and validates the boundaries, while `$text` supplies the body (`tools/codex-context-probe.ps1:189-226`).
- The new regression verifies all 29 entries and `userskill5` specifically (`evals/multi-model-verify/test_codex_context_probe.py:1485-1520`). I independently reproduced 29 entries under both hosts.
- `Ambiguous` now covers every shape except `0/0` and ordered `1/1` (`tools/codex-context-probe.ps1:212-223`). The close-only regression pins `false/true/0/1` at `evals/multi-model-verify/test_codex_context_probe.py:1523-1541`.
- The caller’s order remains presence, ambiguity, empty entries (`tools/codex-context-probe.ps1:720-750`).
- The comment now correctly says one production call with separate field checks (`tools/codex-context-probe.ps1:122-133`).
- The revised behavior and history are recorded at `docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:503-511` and `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2729`.

## Offset attack

I found no input that makes the successful mask and raw render use different index spaces.

Each mask replaces exactly `$len` UTF-16 code units with `$len` spaces (`tools/codex-context-probe.ps1:398-408`). Repeated masks therefore preserve total length and every later offset. I checked this under both hosts with CRLF, sequential containers, and non-BMP characters; raw and masked lengths and skills-opener offsets remained equal.

Safety boundaries are correct:

- If masking throws, `Ambiguous=true`, and the raw slice is not attempted (`tools/codex-context-probe.ps1:191-224`).
- The slice occurs only after ordered `1/1` boundaries are established (`tools/codex-context-probe.ps1:218-226`), so neither index can exceed the equal-length raw string.
- A genuine skills container wholly inside another known body is erased from the locator and refused as missing; a partial overlap leaves invalid cardinality/order and is refused as ambiguous (`tools/codex-context-probe.ps1:189-223`, `:720-734`).
- A delimiter deliberately written mid-entry can still define a span, but that is the already-recorded balanced-pair ambiguity outside masked bodies (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:541-548`), not offset drift.

## Ambiguous and design assessment

Making `Ambiguous` total changes the published function report, not current end-to-end precedence. Close-only still stops on missing presence first; opener-bearing malformed shapes still stop through the existing shape validation or ambiguity branch (`tools/codex-context-probe.ps1:720-750`).

Keeping the locally redundant guard is appropriate. This function measures the input used to build reviewer configuration, and it has direct test callers; depending exclusively on caller ordering would recreate the dependency failures documented throughout this cycle.

I see no structural reason to abandon the current design. The recurring defects came from mixing three responsibilities—locating on masked text, parsing raw text, and proving suppression. Those responsibilities are now separated explicitly (`tools/codex-context-probe.ps1:169-188`, `:224-232`, `:886-909`). That is a coherent strict-parser architecture, not merely another pairing heuristic.

The record now covers the implemented behavior and accepted costs; I found no surviving overclaim in the reviewed changes (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:417-511`).

## Unverified

- I could not rerun the reported 445/1 Python suite.
- I did not rerun the live probe or independently verify its reported hash.

## Verdicts

1. Applied changes: **PASS**.
2. Raw-slice and offset invariant: **PASS**.
3. Total `Ambiguous` behavior: **PASS**.
4. Parser design viability: **PASS**.
5. Terminal verdict for `881b676048208761f97f477ec86ce0585bf42ca2`: **PASS**.

**OVERALL: PASS**

