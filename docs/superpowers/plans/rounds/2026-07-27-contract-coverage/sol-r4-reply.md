## Round 4 verdict

### F1 — FIX: “literal” operands are not enforced

The live result reproduces: 371 pins, unchanged nine-region predictions, and all historical controls covered. The new grammar also correctly drops reversed comparisons, chained comparisons, comprehensions, ternaries around the whole clause, walruses, and `count(...) >= 0`; nested conjunctions collect all required operands. `docs/superpowers/plans/2026-07-27-contract-coverage.md:633` `docs/superpowers/plans/2026-07-27-contract-coverage.md:661` `docs/superpowers/plans/2026-07-27-contract-coverage.md:666`

A non-required string is still collected:

```python
assert ("x" if flag else "y") in body
assert body.count("x" if flag else "y") >= 1
```

Both return `{"x", "y"}`, although each assertion requires only the selected value. `_strings` walks every constant below an operand, and both membership and count pass compound operands to it. `docs/superpowers/plans/2026-07-27-contract-coverage.md:622` `docs/superpowers/plans/2026-07-27-contract-coverage.md:668` `docs/superpowers/plans/2026-07-27-contract-coverage.md:679`

Require the membership left operand and the count needle to be an actual `ast.Constant(str)`—implicitly concatenated literals already become one constant—and add negative ternary-operand tests. `docs/superpowers/plans/2026-07-27-contract-coverage.md:694`

### F2 — PASS

The numeric predicate is correct: `== n` and `>= n` require `n >= 1`; `> n` requires `n >= 0`; booleans are explicitly excluded. The live `>= 3` and `>= 2` assertions are collected, while `count(...) >= 0` is rejected. `docs/superpowers/plans/2026-07-27-contract-coverage.md:670` `evals/multi-model-verify/test_multi_model_verify.py:1003` `evals/multi-model-verify/test_multi_model_verify.py:1356`

The one live name-bound count pin remains intentionally excluded. `evals/multi-model-verify/test_seat_reshuffle.py:97` `docs/superpowers/specs/2026-07-27-contract-coverage-design.md:206`

### F3 — FIX: the whole-text pass still has silent paths

The live scan reproduces 13 documents, balanced HTML-comment delimiters, and no preflight failures; the only current comments are the four `shared-contract:` markers. `docs/superpowers/plans/2026-07-27-contract-coverage.md:957` `agents/flash-implementer.md:19` `agents/implementer.md:13`

The listed ordinary malformed inputs are rejected and `shared-contract:` is ignored. Fenced valid markers are treated as real markers, while two markers on one line are rejected by `_classify`’s full match. `docs/superpowers/plans/2026-07-27-contract-coverage.md:310` `docs/superpowers/plans/2026-07-27-contract-coverage.md:332`

A split marker using bare CR or a Unicode line separator vanishes:

```text
<!--\rcontract:start id=a -->
```

`_preflight` rejects only spans containing `\n`, while `splitlines()` subsequently separates `\r`, `\u2028`, and other line boundaries. The preflight accepts the span as whitespace inside a valid marker; the line scan then sees no complete marker. `docs/superpowers/plans/2026-07-27-contract-coverage.md:345` `docs/superpowers/plans/2026-07-27-contract-coverage.md:360`

Use `len(span.splitlines()) != 1`, not `"\n" in span`, and add CR plus Unicode-separator regressions. `docs/superpowers/plans/2026-07-27-contract-coverage.md:345`

### F4 — FIX: a stray opener can mask a later marker

A stray unrelated opener does not necessarily cause the claimed hard failure. This input passes completely:

```text
<!-->
<!--
contract:start id=a -->
```

`COMMENT.finditer` matches non-overlapping spans: the stray opener consumes through the later marker’s closing `-->`; because the combined body does not begin with `contract:`, `_preflight` ignores it, and the line scan cannot see the split marker. `docs/superpowers/plans/2026-07-27-contract-coverage.md:298` `docs/superpowers/plans/2026-07-27-contract-coverage.md:340`

Search the whole text directly for every `<!--\s*contract:` opener rather than discovering them through non-overlapping comment spans. That preserves `shared-contract:` anchoring while preventing an earlier malformed comment from swallowing detection. `docs/superpowers/plans/2026-07-27-contract-coverage.md:291` `docs/superpowers/plans/2026-07-27-contract-coverage.md:337`

### F5 — FIX: Task 7 still misstates the grammar

The task order, nine-region scope, positive controls, selection rule, indentation instructions, and arithmetic remain coherent. The plan contains exactly 17 + 17 + 4 + 2 new tests, producing the stated 187, 204, 208, and 210 progression. `docs/superpowers/plans/2026-07-27-contract-coverage.md:765` `docs/superpowers/plans/2026-07-27-contract-coverage.md:1013` `docs/superpowers/plans/2026-07-27-contract-coverage.md:1193` `docs/superpowers/plans/2026-07-27-contract-coverage.md:1295` `docs/superpowers/plans/2026-07-27-contract-coverage.md:1516`

Task 7 remains incorrect. It says any argument to `body.count(...)` is a pin and then says strings in an `==` comparison do not count. That contradicts the valid `body.count("literal") == n` form, omits its positivity constraints, and omits conjunctions. `docs/superpowers/plans/2026-07-27-contract-coverage.md:18` `docs/superpowers/plans/2026-07-27-contract-coverage.md:1452`

Copy the exact three-clause definition—including positive count predicates and `and`—into the proposed `CLAUDE.md` text. `docs/superpowers/plans/2026-07-27-contract-coverage.md:18`

### F6 — FIX: the limits are still understated

The three named live losses are real and safely red. The regex lock is at line 318, however, not the design’s cited line 313. `docs/superpowers/specs/2026-07-27-contract-coverage-design.md:206` `evals/multi-model-verify/test_multi_model_verify.py:318` `skills/multi-model-verify/references/debate-protocol.md:48`

The limits omit other genuine positive assertions that the grammar drops: reversed positive count comparisons, chained comparisons, `all(...)` comprehensions, whole-clause ternaries, walruses, and `count(...) != 0`. These are acceptable costs, but the design should say categorically that every positive assertion outside the three exact forms is rejected, with these examples, instead of presenting only three losses. `docs/superpowers/specs/2026-07-27-contract-coverage-design.md:206` `docs/superpowers/plans/2026-07-27-contract-coverage.md:633` `docs/superpowers/plans/2026-07-27-contract-coverage.md:688`

The spaced-colon edge is safe for this plan because each task declares ids before adding markers; one malformed partner also leaves an unmatched valid marker and fails. Its broader safety remains process-dependent, so the design should either narrow that claim to this task order or detect `contract\s*:` and reject it. `docs/superpowers/specs/2026-07-27-contract-coverage-design.md:220` `docs/superpowers/plans/2026-07-27-contract-coverage.md:969` `docs/superpowers/plans/2026-07-27-contract-coverage.md:1149` `docs/superpowers/plans/2026-07-27-contract-coverage.md:1312`

## UNVERIFIED

The actual pytest baseline and projected runtime totals remain UNVERIFIED because the available Python installation has no `pytest` module. The test-function arithmetic, current lint, scanner, and trigger gates were independently verified. `docs/superpowers/plans/2026-07-27-contract-coverage.md:29` `docs/superpowers/plans/2026-07-27-contract-coverage.md:1516`

## Overall — FIX

Required before execution:

1. Accept only literal `ast.Constant(str)` membership/count needles.
2. Detect every whole-text marker opener independently and reject every `splitlines()` boundary.
3. Correct Task 7’s clause definition.
4. Expand and correct the accepted-limits record.

The live measurements and historical proof stand, but the proposed implementation still permits conditional literals and malformed multiline markers to manufacture silent coverage. `docs/superpowers/plans/2026-07-27-contract-coverage.md:622` `docs/superpowers/plans/2026-07-27-contract-coverage.md:298`