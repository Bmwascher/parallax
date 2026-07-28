All three checks are now executable from evidence. Findings below.

---

## Round 6 review — contract coverage design & plan (revision 5)

### M1 — The arity fix is correct and complete: **PASS**

The restriction is applied identically in both branches of `_clause_pins`:

- Compared branch: `if (_is_count_call(node.left) and len(node.left.args) == 1 and not node.left.keywords and ...)` — docs/superpowers/plans/2026-07-27-contract-coverage.md:783-785
- Bare branch: `if _is_count_call(node) and len(node.args) == 1 and not node.keywords:` — docs/superpowers/plans/2026-07-27-contract-coverage.md:795

Both guard exactly one positional argument and zero keywords before `_literal` is consulted. The regression test `test_a_count_call_with_more_than_one_argument_is_not_a_pin` exercises the compared branch and asserts both candidate strings are dropped (docs/superpowers/plans/2026-07-27-contract-coverage.md:605-614).

I re-verified the live call sites by grep this run. There are exactly seven `.count(` assertions in `evals/multi-model-verify/`:

- evals/multi-model-verify/test_backup_lane.py:470-472 — one literal arg (implicitly concatenated), `== 2`
- evals/multi-model-verify/test_multi_model_verify.py:1003 — one literal arg, `>= 3`
- evals/multi-model-verify/test_multi_model_verify.py:1356 — one literal arg, `>= 2`
- evals/multi-model-verify/test_seat_reshuffle.py:102 — one positional arg, but a `Name` (`required`) — already the accepted name-binding limit (docs/superpowers/specs/2026-07-27-contract-coverage-design.md:233-236), dropped by `_literal`, not by the arity guard
- evals/multi-model-verify/test_seat_reshuffle.py:103-104, :105-106, :133 — one literal arg each

Every live count call has exactly one positional argument and no keywords, so the restriction drops nothing that was previously collected. The design's claim "matching all seven live count pins" (docs/superpowers/specs/2026-07-27-contract-coverage-design.md:493-494) is accurate with respect to arity.

Non-blocking observation: the regression test covers only the compared branch; no fixture feeds a multi-argument *bare* count. Since `str.count("a", "b")` is a runtime TypeError, that shape cannot be live. Not a finding.

### M2 — The four artifacts still agree: **PASS**

The grammar in all four artifacts states exactly three clause forms with identical count bounds and the singular needle, and the code implements exactly that (docs/superpowers/plans/2026-07-27-contract-coverage.md:774-797):

| artifact | text | match |
|---|---|---|
| Design clause table | three rows; `== n`, `>= n` (n ≥ 1), `> n` (n ≥ 0); "the call's single argument" (docs/superpowers/specs/2026-07-27-contract-coverage-design.md:142-146) | yes |
| Plan Global Constraints | same three forms, same bounds (docs/superpowers/plans/2026-07-27-contract-coverage.md:18) | yes |
| `_clause_pins` docstring | same three forms, same bounds, singular literal (docs/superpowers/plans/2026-07-27-contract-coverage.md:760-764) | yes |
| Task 7 CLAUDE.md text | same three forms; "== n or >= n with n at least 1, or > n with n at least 0" (docs/superpowers/plans/2026-07-27-contract-coverage.md:1568-1573) | yes |

The singular "the call's single argument" (design:145) now matches the arity guard verified in M1. Code rejects reversed comparisons (`node.left` must be the count call, plan:783), chained comparisons (`len(node.ops) == 1`, plan:779), and zero counts (`n >= 1` for `Eq`, plan:790) — matching the exclusion lists at design:220-230 and plan:21. The CLAUDE.md negative list (plan:1578-1585) names fewer excluded shapes than design:224-226 and plan:21 (it omits reversed/chained/walrus explicitly), but it closes with the identical categorical statement — "Any positive assertion outside the three forms above is rejected, whatever it means" (plan:1584-1585) — so there is no contradiction, only a subset. The round-4 defect class (finding 14: wrong form count, missing bounds, self-contradiction on `==`) does not recur.

### M3 — The limits section: **FIX** (one wording defect, introduced by round 5's own addition)

The container bullet states: "this is **the one** accepted limit that could manufacture coverage rather than merely losing it" (docs/superpowers/specs/2026-07-27-contract-coverage-design.md:264-265). Two paragraphs later, the same bullet now carries the execution-blindness sibling: "An assertion inside a platform-skipped module or behind a `pytest.skip` guard still registers as a pin, and locks nothing at runtime" (docs/superpowers/specs/2026-07-27-contract-coverage-design.md:273-283). I verified both cited structures exist: the module-level `skipif` at evals/multi-model-verify/test_attestation.py:29 and six `pytest.skip` guards in evals/multi-model-verify/test_multi_model_verify.py:1168-1817.

A pin that registers while locking nothing at runtime manufactures coverage — that is the sibling's whole point, and the plan's `collect_pins` docstring says so explicitly, counting "**Two** limits run the OTHER way and could in principle manufacture coverage" (docs/superpowers/plans/2026-07-27-contract-coverage.md:812-816). The design says "the one"; the plan says "two"; the design's own sibling paragraph is the second. The count claim at design:265 went stale the moment the sibling was appended to the same bullet — a defect inside round 5's fix, in the exact class of findings 15, 17 and 18.

**The specific fix:** reword design:265 so it does not claim uniqueness (e.g. "this is one of two accepted limits that could manufacture coverage — the sibling below is the other"), and/or have the sibling paragraph state its failure direction explicitly ("it shares the container limit's direction: it can manufacture coverage, not merely lose it"). One phrase, no mechanism change.

Everything else in the section is coherent: the false-negative limits (design:220-246) are correctly framed with the safe direction ("the region reads uncovered, which is a red", design:227-229); the `== 0` rejection (design:284-289) matches the code (plan:790); no limit is duplicated across the section; the plan docstring's split into safe-direction versus manufacture-coverage limits (plan:807-816) is internally consistent.

### Does anything stop execution?

No mechanism defect, no task-order defect, no artifact drift. The M3 finding is a one-phrase documentation correction in an accepted-limits bullet — the same non-blocking class as round 5's findings 17 and 18. It should be fixed, but it does not gate execution of the plan's tasks, none of which depend on that sentence.

### UNVERIFIED (measurements I cannot re-derive without execution)

- The 715 → 366 string counts and the 192 / 19 breakdown (design:165; plan:766-770)
- "47 of 172 string constants in test_backup_lane.py" (design:390-391)
- The five dropped runtime-constructed fragments census (design:155-160)
- Baseline "170 passed, 1 skipped" (plan:35) and all per-task expected counts (plan:1648-1652)
- That the workspace files are byte-identical to commit `b770eb0`

---

**Per-claim verdicts:** M1: PASS. M2: PASS. M3: FIX (design:265 "the one accepted limit" → acknowledge the execution-blindness sibling as the second manufacture-coverage limit, matching plan:812-816).

**Overall verdict: FIX** — one wording correction in the design's limits section; the plan is otherwise safe to execute, and the fix does not need to precede execution.

To resume this session: kimi -r 049ce8a8-b55a-4be2-a41d-d3d81104faba
