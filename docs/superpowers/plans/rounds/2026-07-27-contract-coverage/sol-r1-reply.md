## Findings

1. **Critical — AST collection does not distinguish pins from arbitrary strings.** The proposed collector admits every `ast.Constant[str]`, and coverage accepts any containing constant; it never verifies that the string participates in an assertion against a document ([docs/superpowers/plans/2026-07-27-contract-coverage.md:393](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-contract-coverage.md:393), [docs/superpowers/plans/2026-07-27-contract-coverage.md:409](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-contract-coverage.md:409)). Existing sources contain module and helper docstrings that the collector therefore calls pins ([evals/multi-model-verify/test_backup_lane.py:1](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_backup_lane.py:1), [evals/multi-model-verify/test_backup_lane.py:36](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_backup_lane.py:36)). A fresh simulation made the first docstring sentence “covered” despite no assertion locking it. Excluding only the checker’s test module does not close this hole ([docs/superpowers/plans/2026-07-27-contract-coverage.md:615](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-contract-coverage.md:615)).

   **Required fix:** define an AST pin as a string participating in a recognized assertion shape against document content, or introduce an explicit syntactic pin marker. Add a negative test where an unused constant or docstring contains the contract sentence and coverage must still fail.

2. **Critical — the sentence splitter is not fail-safe.** The fixed abbreviation list and capital-letter regex are the entire boundary model ([docs/superpowers/plans/2026-07-27-contract-coverage.md:181](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-contract-coverage.md:181), [docs/superpowers/plans/2026-07-27-contract-coverage.md:371](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-contract-coverage.md:371)). Fresh counterexample:

   `Use U.S. Servers only.` → `["Use U.S.", "Servers only."]`

   Two fragment pins cover both outputs even though no pin contains the actual sentence whole. That directly refutes “cannot produce a silent pass” ([docs/superpowers/specs/2026-07-27-contract-coverage-design.md:108](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-27-contract-coverage-design.md:108)). The six `e.g.` measurements reproduced, but they prove only that one known abbreviation is harmless; live references also contain boundaries the regex under-splits through Markdown emphasis, including `**Rotation guard.** The...` and `2.1.216.** Everything...` ([skills/multi-model-verify/references/backup-lane.md:52](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/backup-lane.md:52), [skills/multi-model-verify/references/panels.md:66](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/panels.md:66)).

   **Required fix:** use explicit contract-unit/sentence boundaries instead of inferring unrestricted English boundaries, or specify and test a constrained grammar including initialisms and Markdown closers. Add the fragmented-pin counterexample as a must-fail test.

3. **Important — malformed marker pairs can disappear silently.** The global constraints say all marker problems are hard failures, but the parser only reacts to comments matching the valid regexes ([docs/superpowers/plans/2026-07-27-contract-coverage.md:16](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-contract-coverage.md:16), [docs/superpowers/plans/2026-07-27-contract-coverage.md:178](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-contract-coverage.md:178)). A fresh simulation of the planned code parsed this pair as `{}`:

   `<!-- contract:start id=Bad_ID --> ... <!-- contract:end id=Bad_ID -->`

   **Required fix:** reject any marker-like comment that does not exactly `fullmatch` valid syntax, with a regression test for a malformed start/end pair.

4. **Minor — Task 4’s RED prediction is wrong.** It says “verify both fail,” but before markers exist the inventory test fails while `test_every_marked_sentence_is_locked_by_a_pin` receives zero regions and passes vacuously ([docs/superpowers/plans/2026-07-27-contract-coverage.md:628](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-contract-coverage.md:628), [docs/superpowers/plans/2026-07-27-contract-coverage.md:642](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-contract-coverage.md:642), [docs/superpowers/plans/2026-07-27-contract-coverage.md:648](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-contract-coverage.md:648)).

   **Required fix:** state the actual result: one failed, one passed.

5. **Minor — scope terminology disagrees.** The design says “Three regions marked” and “markers added to the three regions,” while the implementation inventory contains six technical region IDs ([docs/superpowers/specs/2026-07-27-contract-coverage-design.md:187](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-27-contract-coverage-design.md:187), [docs/superpowers/specs/2026-07-27-contract-coverage-design.md:207](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-27-contract-coverage-design.md:207), [docs/superpowers/plans/2026-07-27-contract-coverage.md:934](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-contract-coverage.md:934)).

   **Required fix:** say “six marked regions across three subject areas.”

## Per-claim verdicts

1. **FIX** — coverage remains preferable to checksums or generated pins, but only after pin provenance and sentence-boundary defects are fixed. The rejected registry tradeoff remains reasonable ([docs/superpowers/specs/2026-07-27-contract-coverage-design.md:56](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-27-contract-coverage-design.md:56)).

2. **PASS** — the live references demonstrably mix rules, observations, and rationale, and instance 10’s consequence contains no modal keyword ([skills/multi-model-verify/references/backup-lane.md:52](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/backup-lane.md:52), [skills/multi-model-verify/references/backup-lane.md:57](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/backup-lane.md:57)).

3. **PASS** — current pins stop inside the operative sentences, confirming that overlap is insufficient and containment direction is correct ([evals/multi-model-verify/test_backup_lane.py:141](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_backup_lane.py:141), [evals/multi-model-verify/test_backup_lane.py:152](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_backup_lane.py:152)).

4. **FIX** — the 172 constants / 40 over 60 measurement reproduced exactly, including implicit concatenation, but “every constant is a pin” is unsound ([docs/superpowers/specs/2026-07-27-contract-coverage-design.md:86](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-27-contract-coverage-design.md:86)).

5. **PASS** — the bidirectional declared/found comparison closes accidental whole-region deletion and addition ([docs/superpowers/plans/2026-07-27-contract-coverage.md:628](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-contract-coverage.md:628)).

6. **FIX** — six `e.g.` occurrences and zero capital-following cases reproduced, but the fails-safe conclusion is refuted by the initialism counterexample and Markdown boundaries ([docs/superpowers/specs/2026-07-27-contract-coverage-design.md:102](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-27-contract-coverage-design.md:102)).

7. **ESCALATE** — the runnable portions passed, but pytest-dependent prerequisites remain UNVERIFIED below ([docs/superpowers/plans/2026-07-27-contract-coverage.md:21](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-contract-coverage.md:21)).

8. **FIX** — all substantive coverage predictions reproduced, including six rotation units with only the fifth covered and five panel/fallback misses; correct Task 4’s false “both fail” wording ([docs/superpowers/plans/2026-07-27-contract-coverage.md:597](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-contract-coverage.md:597), [docs/superpowers/plans/2026-07-27-contract-coverage.md:835](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-contract-coverage.md:835), [docs/superpowers/plans/2026-07-27-contract-coverage.md:974](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-contract-coverage.md:974)).

9. **PASS** — all three `sed` patterns executed and extracted the claimed bodies; simulating the proposed checker produced the targeted miss in all three one-region fixtures ([docs/superpowers/plans/2026-07-27-contract-coverage.md:475](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-contract-coverage.md:475), [docs/superpowers/plans/2026-07-27-contract-coverage.md:536](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-contract-coverage.md:536)).

10. **FIX** — the stated limits are present, but they omit arbitrary-string false coverage, splitter false coverage, and malformed-marker disappearance ([docs/superpowers/specs/2026-07-27-contract-coverage-design.md:154](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-27-contract-coverage-design.md:154)).

11. **FIX** — 633 AST `assert` nodes reproduced; the fallback inventory also reproduces ten `###` entries, five class-named entries across heading/bullet forms, and anchors at lines 190 and 210 ([skills/multi-model-verify/references/fallbacks.md:130](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/fallbacks.md:130), [skills/multi-model-verify/references/fallbacks.md:190](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/fallbacks.md:190), [skills/multi-model-verify/references/fallbacks.md:210](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/fallbacks.md:210)). Fix only the design’s three-versus-six terminology.

## UNVERIFIED

- `python -m pytest evals -q` and the claimed pytest sibling-module import: `python` is absent from PATH; the available Python 3.14 interpreter has no pytest module. These facts were not used to support the overall verdict ([docs/superpowers/plans/2026-07-27-contract-coverage.md:21](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-contract-coverage.md:21)).
- An actually modified-tree gate run is impossible before implementation. Current lint, scanner, and trigger gates passed; virtual marker injection also produced zero scanner findings, but that is not a substitute for the final edited-tree suite ([docs/superpowers/plans/2026-07-27-contract-coverage.md:26](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-contract-coverage.md:26)).

**OVERALL: FIX — do not execute the plan until pin provenance, explicit/safe sentence boundaries, and malformed-marker rejection are designed and tested. Then apply the two documentation corrections.**

