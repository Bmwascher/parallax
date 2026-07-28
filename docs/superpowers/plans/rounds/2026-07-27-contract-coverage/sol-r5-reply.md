## Round 5 verdict

### J1 — FIX: the five losses are real fragment locks

The measurements reproduce: 366 pins; unchanged nine-region predictions; historical controls remain covered while defects remain uncovered. `docs/superpowers/plans/2026-07-27-contract-coverage.md:744` `docs/superpowers/plans/2026-07-27-contract-coverage.md:874`

The five removed values are fragments, but they are genuine locks: the assertions require the complete constructed needles, which necessarily require `--model`, `model="`, the canonical-id prefix, backticks, and quotes to remain present. `evals/multi-model-verify/test_flash_implementer.py:41` `evals/multi-model-verify/test_flash_implementer.py:64` `evals/multi-model-verify/test_backup_lane.py:48` `evals/multi-model-verify/test_multi_model_verify.py:1778`

Dropping them is safe because none is load-bearing for the nine regions or history controls, but `_literal`’s statement that strict literals cost “nothing real” is overstated. Replace it with “costs no current marked coverage; five genuine fragment locks are deliberately dropped.” `docs/superpowers/plans/2026-07-27-contract-coverage.md:695` `docs/superpowers/plans/2026-07-27-contract-coverage.md:704` `docs/superpowers/specs/2026-07-27-contract-coverage-design.md:158`

### J2 — PASS

The requested span-bound attacks behave correctly:

- A later unterminated contract opener is found independently and rejected.
- Two openers before one close make the first span malformed.
- `-->` inside an id truncates the span and fails strict matching.
- EOF inside a marker is rejected.
- The earlier `<!-->` counterexample no longer masks a later opener. `docs/superpowers/plans/2026-07-27-contract-coverage.md:370` `docs/superpowers/plans/2026-07-27-contract-coverage.md:389`

A valid region followed by a plain unterminated `<!--` is accepted because that opener is outside this marker family; this is consistent with the documented broken-opener limit. `docs/superpowers/specs/2026-07-27-contract-coverage-design.md:240`

### J3 — PASS

The widened opener rejects spaced-colon and capitalized variants while still requiring `contract` immediately after the HTML opener, modulo whitespace. It does not match `shared-contract:` or `contractor:`. `docs/superpowers/plans/2026-07-27-contract-coverage.md:324` `docs/superpowers/plans/2026-07-27-contract-coverage.md:329`

The live scan reproduced 13 documents, zero opener hits, and four ignored shared-family markers. `agents/implementer.md:13` `agents/implementer.md:28` `agents/flash-implementer.md:19` `agents/flash-implementer.md:34`

### J4 — PASS

The clause behavior remains as previously verified: only conjunctions recurse, positive count bounds are unchanged, nested `and` collects every operand, and unrecognized enclosing expressions return empty. `_literal` changes only operand extraction. `docs/superpowers/plans/2026-07-27-contract-coverage.md:724` `docs/superpowers/plans/2026-07-27-contract-coverage.md:752` `docs/superpowers/plans/2026-07-27-contract-coverage.md:779`

### J5 — FIX: code admits multi-argument count calls

The design table, Global Constraints, clause docstring, and proposed `CLAUDE.md` text agree on the stated grammar. `docs/superpowers/specs/2026-07-27-contract-coverage-design.md:140` `docs/superpowers/plans/2026-07-27-contract-coverage.md:18` `docs/superpowers/plans/2026-07-27-contract-coverage.md:738` `docs/superpowers/plans/2026-07-27-contract-coverage.md:1544`

The code is broader: it iterates every positional argument of any `.count(...)` call. Consequently, `assert receiver.count("x", "y")` collects both literals, although every artifact specifies the singular form `body.count("literal")`. `docs/superpowers/plans/2026-07-27-contract-coverage.md:769` `docs/superpowers/plans/2026-07-27-contract-coverage.md:774`

Require exactly one positional literal argument and no keywords, or explicitly expand all four grammar descriptions and justify additional arguments. The strict one-argument rule matches every live count pin. `docs/superpowers/plans/2026-07-27-contract-coverage.md:505` `evals/multi-model-verify/test_multi_model_verify.py:1003`

### J6 — FIX: membership has an unstated receiver-equivalent limit

The categorical false-negative limits and broken-opener dependency are now stated honestly. `docs/superpowers/specs/2026-07-27-contract-coverage-design.md:213` `docs/superpowers/specs/2026-07-27-contract-coverage-design.md:240`

The `.count` receiver limit has an omitted analogue: the checker cannot determine whether the right operand of `"literal" in container` is document text. Live collected assertions include subprocess output and structured hook context, not document sources. A coincident region could therefore be covered by an assertion unrelated to that document. `docs/superpowers/plans/2026-07-27-contract-coverage.md:757` `evals/multi-model-verify/test_attestation.py:96` `evals/multi-model-verify/test_multi_model_verify.py:1193`

Add an accepted limit stating that membership targets are syntactically untyped, just like `.count` receivers, and that non-document containers can manufacture coverage through coincidence. `docs/superpowers/specs/2026-07-27-contract-coverage-design.md:252`

### J7 — PASS

Task order, nine-region scope, history controls, `fallbacks.md` selection, and Tasks 4–5 indentation remain intact. `docs/superpowers/plans/2026-07-27-contract-coverage.md:856` `docs/superpowers/plans/2026-07-27-contract-coverage.md:1104` `docs/superpowers/plans/2026-07-27-contract-coverage.md:1284` `docs/superpowers/plans/2026-07-27-contract-coverage.md:1386`

The plan contains exactly 20 + 19 + 4 + 2 test functions, matching the stated 190, 209, 213, and 215 progression. `docs/superpowers/plans/2026-07-27-contract-coverage.md:1624`

## UNVERIFIED

Actual pytest pass totals remain UNVERIFIED because the available Python installation has no `pytest` module. Current lint, scanner, trigger gates, and test-function arithmetic were verified. `docs/superpowers/plans/2026-07-27-contract-coverage.md:30` `docs/superpowers/plans/2026-07-27-contract-coverage.md:1624`

## Overall — FIX

Required before execution:

1. Enforce the documented one-literal-argument `.count` grammar.
2. Record the untyped membership-container limit.
3. Correct the claim that the five removed fragments were not real locks.

The opener-based preflight itself passes this round’s attacks; the remaining defects are one code/grammar mismatch and two accuracy gaps in the accepted-cost record. `docs/superpowers/plans/2026-07-27-contract-coverage.md:389` `docs/superpowers/plans/2026-07-27-contract-coverage.md:769`