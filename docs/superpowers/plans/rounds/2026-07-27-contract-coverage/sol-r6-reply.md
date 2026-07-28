FIX — two specific corrections remain before execution.

## Findings

1. P2’s “two manufacture-coverage limits” count is still overstated. The design names the untyped container as one of two and execution blindness as the other (`docs/superpowers/specs/2026-07-27-contract-coverage-design.md:264`, `docs/superpowers/specs/2026-07-27-contract-coverage-design.md:274`). But it separately admits that a region may be satisfied by another region’s pin (`docs/superpowers/specs/2026-07-27-contract-coverage-design.md:293`), while `uncovered` accepts any pooled pin without binding it to the region’s source (`docs/superpowers/plans/2026-07-27-contract-coverage.md:827`, `docs/superpowers/plans/2026-07-27-contract-coverage.md:837`). That is another path to apparent coverage without an assertion locking that document occurrence.

   Specific fix: either call the first two “the two AST-extraction limits” in both documents (`docs/superpowers/plans/2026-07-27-contract-coverage.md:812`), or count cross-region provenance as a third manufacture-coverage limit and state its failure direction explicitly.

2. The new arity regression does not lock the whole accepted fix. It tests only a multi-positional `.count(...) == 1` expression (`docs/superpowers/plans/2026-07-27-contract-coverage.md:605`, `docs/superpowers/plans/2026-07-27-contract-coverage.md:610`). The implementation has separate compared and bare-call branches, each with its own arity and keyword guards (`docs/superpowers/plans/2026-07-27-contract-coverage.md:783`, `docs/superpowers/plans/2026-07-27-contract-coverage.md:795`), while the existing positive test exercises only the compared form (`docs/superpowers/plans/2026-07-27-contract-coverage.md:505`, `docs/superpowers/plans/2026-07-27-contract-coverage.md:508`).

   Specific fix: extend those existing test functions to cover a positive bare count, a bare multi-argument count, and keyword arguments in both branches. This need not change the test-count arithmetic.

## Per-claim verdicts

- P1 — PASS. Both arity guards are present; the fragment-loss wording now acknowledges genuine partial locks; and the membership-container limit states the false-coverage direction (`docs/superpowers/plans/2026-07-27-contract-coverage.md:783`, `docs/superpowers/plans/2026-07-27-contract-coverage.md:795`, `docs/superpowers/specs/2026-07-27-contract-coverage-design.md:155`, `docs/superpowers/specs/2026-07-27-contract-coverage-design.md:259`).

- P2 — FIX: scope “two” to AST-extraction limits or count cross-region provenance as a third false-coverage path (`docs/superpowers/specs/2026-07-27-contract-coverage-design.md:264`, `docs/superpowers/specs/2026-07-27-contract-coverage-design.md:293`).

- P3 — PASS. The design table, Global Constraints, proposed module, and Task 7 text all specify the same three clause forms, literal-needle requirement, positive count bounds, and complete-clause behavior (`docs/superpowers/specs/2026-07-27-contract-coverage-design.md:140`, `docs/superpowers/plans/2026-07-27-contract-coverage.md:18`, `docs/superpowers/plans/2026-07-27-contract-coverage.md:760`, `docs/superpowers/plans/2026-07-27-contract-coverage.md:1568`).

- P4 — PASS. The current plan still has nine declared ids, two-control history fixtures, and 20 + 20 + 4 + 2 test functions, yielding the stated progression (`docs/superpowers/plans/2026-07-27-contract-coverage.md:880`, `docs/superpowers/plans/2026-07-27-contract-coverage.md:1016`, `docs/superpowers/plans/2026-07-27-contract-coverage.md:1430`, `docs/superpowers/plans/2026-07-27-contract-coverage.md:1648`).

- P5 — FIX: close the limits-count wording defect and exercise both arity branches plus keyword rejection before execution (`docs/superpowers/plans/2026-07-27-contract-coverage.md:605`, `docs/superpowers/plans/2026-07-27-contract-coverage.md:812`).

## UNVERIFIED

- Runtime pytest baseline and projected pass totals remain UNVERIFIED; the sandbox’s available Python lacks pytest. The statically enumerated plan arithmetic matches the documented totals (`docs/superpowers/plans/2026-07-27-contract-coverage.md:35`, `docs/superpowers/plans/2026-07-27-contract-coverage.md:1648`).

## Overall verdict

FIX — scope or correct the manufacture-coverage count, and expand the arity regression to cover the bare and keyword branches.