Round 2 closes A2, A4, and A5, but A1 and A3 remain incomplete. Three fixes are required before execution.

## Findings

1. **Pin provenance still admits strings that lock no document.** `collect_pins` walks the entire `ast.Assert`, including its optional failure-message expression (`docs/superpowers/plans/2026-07-27-contract-coverage.md:480-505`). The live suite contains examples such as `assert m, "missing frontmatter"` and `assert m, "tools allowlist missing"` (`evals/multi-model-verify/test_flash_implementer.py:24-34`). I re-derived 715 unique collected strings; 194 are assertion-message strings. A hermetic `assert body.is_file(), "The contract rule stands."` makes that region appear covered despite performing no document containment check. This contradicts the design’s rule that a pin must actually lock text (`docs/superpowers/specs/2026-07-27-contract-coverage-design.md:70-74`).

   **Specific fix:** collect literals only from recognized positive-presence expressions in `Assert.test`, such as `"literal" in body` and any explicitly supported `.count("literal")` form. Never inspect `Assert.msg`; do not treat equality expectations or negative membership as pins. Add negative regressions for an assertion message and `assert result == "contract text"`.

2. **Malformed-marker rejection still has a silent hole.** `MARKERISH` requires a closing `-->`, so `<!-- contract:start id=demo` and `<!-- contract:end` are ignored, not rejected (`docs/superpowers/plans/2026-07-27-contract-coverage.md:243-258`). It also extracts a valid marker substring from `prefix <!-- contract:start id=demo --> suffix` and accepts it, despite the plan requiring markers on their own lines (`docs/superpowers/plans/2026-07-27-contract-coverage.md:269-290`). A pair of unterminated malformed markers can therefore disappear exactly as the design forbids (`docs/superpowers/specs/2026-07-27-contract-coverage-design.md:95-99`).

   **Specific fix:** detect `<!--\s*contract:` case-insensitively without requiring a closing delimiter, then require `line.strip()` to fullmatch `START` or `END`. Add tests for an unterminated marker and a marker sharing a line with prose.

3. **The Fable agent marker indentation is underspecified.** The target sentence is inside the `- Later rounds` list item (`agents/fable-panel-reviewer.md:18-33`). Task 5 Step 3 explicitly requires the panel markers to remain on their own lines at the list-item indent, but Step 4 merely says to “mark the sentence” and gives no indentation instruction (`docs/superpowers/plans/2026-07-27-contract-coverage.md:965-991`). A zero-judgment implementer may place those markers at column zero, ending the list item.

   **Specific fix:** state that both `panel-floor-agent` markers are standalone lines indented two spaces, matching the bullet’s content indent.

## Per-claim verdicts

- **C1 — PASS.** Whole-region containment removes sentence-boundary inference completely, and the plan divides the two longer subjects into independently pinnable regions (`docs/superpowers/specs/2026-07-27-contract-coverage-design.md:47-55`, `docs/superpowers/plans/2026-07-27-contract-coverage.md:1096-1100`). The deliberate absence of a weakening valve is appropriate for this repository’s stated failure history (`docs/superpowers/specs/2026-07-27-contract-coverage-design.md:181-185`).

- **C2 — FIX.** The 715 unique assert-scoped strings and the single legitimate assigned-then-asserted pin reproduce, but an `ast.Assert` subtree is broader than a positive document assertion. Assertion messages provide a verified false-coverage path (`docs/superpowers/plans/2026-07-27-contract-coverage.md:480-505`, `evals/multi-model-verify/test_flash_implementer.py:24-34`).

- **C3 — PASS.** All nine predictions reproduced exactly: only `rotation-guard-residual-gap` and `panel-lane-loss-disposition` are currently covered; the other seven are uncovered (`docs/superpowers/plans/2026-07-27-contract-coverage.md:741-744`, `docs/superpowers/plans/2026-07-27-contract-coverage.md:998-1001`, `docs/superpowers/plans/2026-07-27-contract-coverage.md:1162-1169`).

- **C4 — PASS.** The historical counts reproduced as 106, 109, and 42 unique assert-scoped strings. Every control and defect body appears verbatim after whitespace normalization; each control is covered by a real positive membership assertion and each defect is uncovered (`docs/superpowers/plans/2026-07-27-contract-coverage.md:595-649`). The exact-one-miss assertions plus the two-region guard prove the positive controls correctly (`docs/superpowers/plans/2026-07-27-contract-coverage.md:673-707`).

- **C5 — FIX.** All enumerated examples behave as claimed, and `shared-contract:` is correctly ignored. The scanned trees contain no other marker family: the four live markers are the two shared pairs (`agents/implementer.md:13-28`, `agents/flash-implementer.md:19-34`), protected by parity testing (`evals/multi-model-verify/test_flash_implementer.py:122-132`). Unterminated and non-standalone contract markers remain unhandled.

- **C6 — FIX.** Current lint, scanner, trigger gates, and a virtual nine-marker scanner run were clean, consistent with the planned gate contract (`docs/superpowers/plans/2026-07-27-contract-coverage.md:26-32`). However, Task 5 must specify the agent-file indentation identified above (`docs/superpowers/plans/2026-07-27-contract-coverage.md:984-991`).

- **C7 — PASS for task order and arithmetic.** The plan adds 14, 9, 4, and 2 test functions, producing the stated 184, 193, 197, and 199 progression from the 170-pass baseline (`docs/superpowers/plans/2026-07-27-contract-coverage.md:1300-1306`). Runtime counts remain UNVERIFIED below.

- **C8 — PASS.** The nine-region inventory exactly implements the three selected subject areas, and the failure-class selection remains evidence-based rather than count-based (`docs/superpowers/specs/2026-07-27-contract-coverage-design.md:210-224`, `docs/superpowers/plans/2026-07-27-contract-coverage.md:1083-1100`).

## UNVERIFIED

- The runtime baseline `170 passed, 1 skipped` and subsequent pytest totals: the available Python 3.14 interpreter has no pytest module. This did not contribute to the verdict (`docs/superpowers/plans/2026-07-27-contract-coverage.md:26-32`).
- The exact rendered “several paragraphs” Markdown appearance: no local Markdown renderer was available. The missing Fable-marker indentation instruction is established directly from the source structure and does not depend on this rendering claim (`docs/superpowers/plans/2026-07-27-contract-coverage.md:809-812`).
- Final edited-tree gates, because nothing has been implemented (`docs/superpowers/plans/2026-07-27-contract-coverage.md:1262-1274`).

**OVERALL: FIX — restrict pin extraction to genuine positive-presence assertion syntax, reject unterminated/non-standalone contract markers, and specify two-space indentation for the Fable agent markers.**

