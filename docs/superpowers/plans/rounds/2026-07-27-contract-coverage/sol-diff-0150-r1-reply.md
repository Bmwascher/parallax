Overall verdict: FIX. The implementation has a real false-coverage path and several documentation/record mismatches.

### P1 — FIX

Most planned mechanics match revision 7: whole-region containment is implemented one-way, marker preflight scans the complete text, and `shared-contract:` remains ignored (`docs/superpowers/plans/2026-07-27-contract-coverage.md:16-27`; `evals/multi-model-verify/contract_coverage.py:39-47`; `evals/multi-model-verify/contract_coverage.py:80-109`; `evals/multi-model-verify/contract_coverage.py:287-299`).

Two fidelity problems remain:

1. The plan allows only “an `and` of” recognized clauses, but `_clause_pins` accepts a mixed conjunction and silently collects whichever operands it recognizes. Thus `assert "region" in body and flag` contributes a pin although it is not an `and` solely of the three documented forms (`docs/superpowers/plans/2026-07-27-contract-coverage.md:18-21`; `evals/multi-model-verify/contract_coverage.py:220-238`). This behavior is logically safe for ordinary conjunctions, but it contradicts the frozen grammar. Fix the prose to describe recognized conjunct collection, or reject the entire conjunction unless every operand is recognized.

2. Task 3 says it changes only the fixtures and `test_contract_coverage.py`, and its commit command names only those paths (`docs/superpowers/plans/2026-07-27-contract-coverage.md:910-921`; `docs/superpowers/plans/2026-07-27-contract-coverage.md:1065-1069`). The commit also changed the backup-literal sweep (`evals/multi-model-verify/test_backup_lane.py:516-533`). That change was human-authorized and correctly scoped, but it is still a plan deviation; the reconstructed ledger records the ruling (`docs/superpowers/plans/rounds/2026-07-27-contract-coverage/ledger-reconstruction.md:37-46`). Add it explicitly to the execution-deviation inventory; do not revert it.

The instance-10 historical narrative is also wrong in multiple current surfaces: it says there was “no pin,” while the historical fixture contains a fragment pin inside that sentence (`docs/superpowers/specs/2026-07-27-contract-coverage-design.md:24-27`; `evals/multi-model-verify/fixtures/contract-coverage-history/instance-10-doc.md:1-3`; `evals/multi-model-verify/test_contract_coverage.py:432`; `evals/multi-model-verify/test_contract_coverage.py:480`; `evals/multi-model-verify/fixtures/contract-coverage-history/instance-10-pins.py:143-146`). Correct every live occurrence to “no pin contained the whole disposition sentence.”

### P2 — FIX

The five commits contain no code relaxation: the count wording now matches the implemented positive bounds, the classifier tests add coverage, and the lockstep-shrink entry is correctly marked FALSE COVERAGE (`CLAUDE.md:52-72`; `evals/multi-model-verify/contract_coverage.py:243-256`; `evals/multi-model-verify/test_contract_coverage.py:368-384`; `docs/superpowers/specs/2026-07-27-contract-coverage-design.md:308-316`).

But `f872b34` contradicts the design’s stated inputs. The implementation and `CLAUDE.md` scan all Markdown under `skills/`, plus `agents/*.md` and `commands/*.md` (`evals/multi-model-verify/test_contract_coverage.py:512-516`; `CLAUDE.md:47-50`). The design still specifies only `skills/multi-model-verify/references/` plus `agents/` (`docs/superpowers/specs/2026-07-27-contract-coverage-design.md:120-129`).

This directly refutes the retained re-review’s claim that the design named no old globs (`docs/superpowers/plans/rounds/2026-07-27-contract-coverage/opus-fixwave-rereview-4ec80b1-23709fa.md:22-31`). Update the design’s Inputs section to the widened surface.

### P3 — FIX

A real pytest shape manufactures coverage:

```python
with pytest.raises(AssertionError):
    assert "Entire marked region." in body
```

The test passes when the region text is absent. Nevertheless, `collect_pins` walks every `ast.Assert` without considering its parent context, and `_clause_pins` registers the membership literal (`evals/multi-model-verify/contract_coverage.py:234-242`; `evals/multi-model-verify/contract_coverage.py:278-284`). `uncovered` then reports the region covered solely because its body occurs in that syntactic pin (`evals/multi-model-verify/contract_coverage.py:287-299`).

This is not the documented execution-blind case: the assertion runs, but its failure is deliberately consumed. The current limit mentions skipped assertions only (`docs/superpowers/specs/2026-07-27-contract-coverage-design.md:284-295`).

Specific fix:

- Add regression cases for `pytest.raises(AssertionError)`, `contextlib.suppress(AssertionError)`, `try/except AssertionError`, and pytest `xfail`.
- Make pin collection parent-aware and reject assertions under those known failure-swallowing contexts.
- Document residual custom failure-handling contexts as FALSE COVERAGE.

### P4 — FIX

The cross-target shrink is genuinely reachable. `uncovered` has no pin-to-document binding; it asks only whether the current body occurs in any pooled pin (`evals/multi-model-verify/contract_coverage.py:294-299`). Therefore, if document A’s region shrinks from `A B` to `A`, an unchanged `A B` pin asserted against document B still covers it. This requires textual coincidence, but not an impossible one. It is substantially covered by the existing cross-region limit (`docs/superpowers/specs/2026-07-27-contract-coverage-design.md:302-307`).

The limits are nevertheless incomplete because expected-failure contexts from P3 are absent.

One direction tag is also wrong by the section’s own definition. FALSE NEGATIVE is defined as an uncovered region producing red (`docs/superpowers/specs/2026-07-27-contract-coverage-design.md:220-224`). The broken-opener bullet admits that two mistyped markers can be invisible and that safety depends on inventory-first task order; another order lacks protection (`docs/superpowers/specs/2026-07-27-contract-coverage-design.md:260-271`). Tag that `FALSE COVERAGE — process-mitigated`, not FALSE NEGATIVE.

### P5 — FIX

The loss did cost something material. The surviving summary says the lost review tried roughly twenty forms without finding a declared-region false pass and concluded the widening was the only false-belief path (`docs/superpowers/plans/rounds/2026-07-27-contract-coverage/sdd-reviews-off-plan-commits.md:47-55`). P3 now refutes that assurance, and the raw probe set cannot be audited because the reply is explicitly lost (`docs/superpowers/plans/rounds/2026-07-27-contract-coverage/sdd-reviews-off-plan-commits.md:16-22`).

The retained widening review also claimed there was no stale design text, which P2 directly refutes (`docs/superpowers/plans/rounds/2026-07-27-contract-coverage/opus-fixwave-rereview-4ec80b1-23709fa.md:24-31`).

The fixture provenance itself is closed: git object comparisons matched all three copied pin files to the historical sources named by the plan, and each fixture region body occurs in the corresponding historical document (`docs/superpowers/plans/2026-07-27-contract-coverage.md:926-933`; `evals/multi-model-verify/fixtures/contract-coverage-history/instance-10-doc.md:4-12`). The lost review’s classifier assurance is the part that remains consequential and should be corrected in the follow-up record.

### UNVERIFIED

Current runtime gates are UNVERIFIED from this seat because no Python or pytest executable is available. The latest retained run reports 221 passed, 1 skipped and all three auxiliary gates clean, but that is prior record evidence, not a current rerun (`docs/superpowers/plans/rounds/2026-07-27-contract-coverage/opus-fixwave-rereview-4ec80b1-23709fa.md:58-65`). This is excluded from the verdict.

Per-claim verdicts:

- P1: FIX
- P2: FIX
- P3: FIX
- P4: FIX
- P5: FIX
- Overall: FIX

