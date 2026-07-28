## Round 3 verdict

### D1 — FIX: constrain the AST grammar

The measurements reproduce: 715 assert-scoped strings become 375 pins; only `rotation-guard-residual-gap` and `panel-lane-loss-disposition` cover their proposed bodies. The historical cases also reproduce at 101/104/36 pins, with each control covered and each defect uncovered. `docs/superpowers/plans/2026-07-27-contract-coverage.md:540` `docs/superpowers/plans/2026-07-27-contract-coverage.md:666` `docs/superpowers/plans/2026-07-27-contract-coverage.md:760`

The rule is nevertheless unsound. `_collect_from` recursively descends through every unrecognized parent, so both `assert ("lit" in body) == False` and `assert flag or "lit" in body` collect `"lit"`. The latter shape exists live: the assertion permits either absence of `stdin` or presence of `does not reach`, yet the proposed collector treats `does not reach` as an unconditional pin for text in the scanned agent tree. `docs/superpowers/plans/2026-07-27-contract-coverage.md:558` `docs/superpowers/plans/2026-07-27-contract-coverage.md:570` `evals/multi-model-verify/test_flash_implementer.py:58` `agents/flash-implementer.md:74`

The accepted `body.count("x") == 0` limit should also be fixed. Pins and regions are pooled repo-wide, so an absence assertion against document B can falsely cover identical positive text in document A; it does not require one document to contain and exclude the text simultaneously. `docs/superpowers/specs/2026-07-27-contract-coverage-design.md:198` `docs/superpowers/plans/2026-07-27-contract-coverage.md:574` `docs/superpowers/plans/2026-07-27-contract-coverage.md:595`

### D2 — FIX: make the two shapes complete predicates, not descendant nodes

The stated AST census reproduced exactly. A genuine document lock is deliberately lost: `re.search(r"converged with amendments", text)` locks an exact phrase in `debate-protocol.md`, but the new collector omits it. That false negative is acceptable because it turns red and can be rewritten as membership. `evals/multi-model-verify/test_multi_model_verify.py:313` `skills/multi-model-verify/references/debate-protocol.md:48` `docs/superpowers/specs/2026-07-27-contract-coverage-design.md:190`

The necessary fix is to recognize complete assertion clauses: direct positive membership, positive-count comparisons, and conjunctions of those clauses. Do not generically descend through `or`, arbitrary comparisons, conditionals, or arbitrary calls. `docs/superpowers/plans/2026-07-27-contract-coverage.md:540` `docs/superpowers/plans/2026-07-27-contract-coverage.md:570`

### D3 — FIX: the named negation works, but polarity can still be defeated

`assert not (x and "lit" not in body)` collects nothing, as intended, because the outer `not` returns immediately. `docs/superpowers/plans/2026-07-27-contract-coverage.md:558`

However, `assert ("lit" in body) == False` and an `or` containing positive membership defeat the claimed positive-presence rule through generic child recursion. Add negative regressions for equality-to-false, `or`, and zero-count assertions. `docs/superpowers/plans/2026-07-27-contract-coverage.md:560` `docs/superpowers/plans/2026-07-27-contract-coverage.md:570`

### D4 — FIX: multiline marker comments vanish

All listed one-line cases reproduce, and the anchored pattern correctly ignores the existing `shared-contract:` family. `docs/superpowers/plans/2026-07-27-contract-coverage.md:260` `docs/superpowers/plans/2026-07-27-contract-coverage.md:275` `agents/implementer.md:13` `agents/flash-implementer.md:19`

This valid HTML comment form vanishes silently:

```html
<!--
contract:start id=demo -->
```

`parse_regions` splits the document into lines before `_classify`; neither line contains `<!--` followed by `contract:`, so both are ignored. Perform a whole-text preflight for an HTML comment whose stripped body begins case-insensitively with `contract:`, then reject it unless it is a valid standalone one-line marker. Add this multiline form as a regression test. `docs/superpowers/plans/2026-07-27-contract-coverage.md:293` `docs/superpowers/plans/2026-07-27-contract-coverage.md:313`

### D5 — FIX: one stale instruction remains

The task order, positive-control fixture design, nine-region scope, selection rule, and arithmetic remain coherent. The additions are 16 + 13 + 4 + 2 tests, taking the recorded 170-pass baseline to 205 passes. `docs/superpowers/plans/2026-07-27-contract-coverage.md:648` `docs/superpowers/plans/2026-07-27-contract-coverage.md:817` `docs/superpowers/plans/2026-07-27-contract-coverage.md:1178` `docs/superpowers/plans/2026-07-27-contract-coverage.md:1393`

Task 7 still tells future authors that a pin is merely “a string inside an `assert`,” contradicting the revised two-shape definition. Replace that sentence with the exact positive-presence grammar ultimately implemented. `docs/superpowers/plans/2026-07-27-contract-coverage.md:18` `docs/superpowers/plans/2026-07-27-contract-coverage.md:1333`

## UNVERIFIED

The actual pytest baseline and projected runtime totals are UNVERIFIED because the available Python 3.14 installation has no `pytest` module. The arithmetic is verified, but not execution of the stated gate. `docs/superpowers/plans/2026-07-27-contract-coverage.md:26` `docs/superpowers/plans/2026-07-27-contract-coverage.md:1393`

## Overall — FIX

Before implementation:

1. Replace generic AST recursion with a constrained, polarity-aware positive-presence grammar and reject `or`, false comparisons, and zero-count predicates.
2. Detect multiline marker-family comments at whole-text scope.
3. Correct Task 7’s stale pin definition.

The live and historical simulations pass, but the proposed checker still has two silent false-coverage paths, which is the exact failure class it is intended to eliminate. `docs/superpowers/plans/2026-07-27-contract-coverage.md:5` `docs/superpowers/plans/2026-07-27-contract-coverage.md:540` `docs/superpowers/plans/2026-07-27-contract-coverage.md:286`

