Round 5 (re-dispatch) review complete. Both documents were re-read in full, and every claim was checked against the live files cited below.

---

## Per-claim findings

**K1 — The literal-needle rule costs no marked coverage: PASS.**
The live expression-needle class is exactly three assertions, producing the five fragments the brief names: `test_flash_implementer.py:41` (`assert "--model " + CANONICAL_ID in body`), `test_flash_implementer.py:64` (`assert 'model="' + CANONICAL_ID + '"' in body`), and `test_backup_lane.py:48` (`assert "Canonical backup reviewer model id: `" + BACKUP_ID + "`" in notes`). Fragments: `--model `, `model="`, `"`, `` ` ``, `Canonical backup reviewer model id: `. The one name-bound pin is still the only one of its class: `test_seat_reshuffle.py:97-102`, and it locks SKILL.md text, not any of the nine planned regions. None of the five fragments textually overlaps a planned region body (rotation guard, panel floor, fallback classes — `docs/superpowers/plans/2026-07-27-contract-coverage.md:1127-1158, 1290-1291, 1309-1310, 1448-1478`). The corrected claim — "costs no CURRENT MARKED COVERAGE, not that it costs nothing" — now appears in both documents (`docs/superpowers/specs/2026-07-27-contract-coverage-design.md:155-160`, plan:717-726) and is accurate.

**K2 — The opener-based preflight is sound: PASS.**
Attacked the span bound (plan:389-399) directly:
- Valid marker followed by an unterminated `<!--` containing `contract:`: `close == -1`, span runs to end of text, fails `splitlines()`/`fullmatch` → rejected.
- Two openers before any `-->`: first opener's span swallows the second and is multi-line → rejected.
- File ends mid-marker (`<!-- contract:start id=a` at EOF): single-line span, `START.fullmatch` fails (no `-->`) → rejected.
- Two markers on one line: preflight passes each span, but `_classify` (plan:355-367) fails both fullmatches on the combined stripped line → rejected.
- Spaced closing `-- >`: span to EOF or to a later `-->`, never fullmatches → rejected.
- A stray `<!--` without the keyword no longer interacts with markers at all, because openers are found directly (plan:337, 389).

The only input I could construct that still vanishes is one with text between `<!--` and `contract:` (e.g. `<!-- note contract:start id=x -->`), which matches neither `OPENER` (plan:329) nor the line scan. That is inside the broken-opener class already stated openly as process-dependent via the declared inventory (`design:247-258`), and the plan's task order populates the inventory before any document is touched (plan:1078-1082 before 1130, 1263 before 1280, 1424 before 1444). No NEW silent shape.

**K3 — The spaced-colon tolerance broke nothing: PASS.**
All four live `shared-contract:` markers (`agents/implementer.md:13`, `agents/implementer.md:28`, `agents/flash-implementer.md:19`, `agents/flash-implementer.md:34`) are unaffected: after `<!--` and `\s*`, the pattern needs `contract` but finds `shared-`. The references tree currently contains zero `<!--` occurrences (grep over `skills/multi-model-verify/references`, no matches), so nothing else in the scanned trees can match the widened `<!--\s*contract\s*:`. Case-insensitivity only widens toward rejection (a capitalized keyword now errors instead of vanishing), which is the documented intent (plan:322-328).

**K4 — The four artifacts describe the same grammar: PASS.**
Checked all four against the code, as in round 4:
- Design clause table (`design:140-146`) plus the needle/arity rule (`design:148-149`).
- Plan Global Constraints (plan:18-21).
- Module docstrings and code (plan:746-797): BoolOp-And → union; single-op `Compare`/`In` → left literal; count comparison requiring exactly one positional arg, no keywords, a non-bool int literal bound, and `(==|>= n≥1) | (> n≥0)` (plan:779-794); bare count call with one arg and no keywords (plan:795-796).
- Task 7 CLAUDE.md text (plan:1558-1587).

All four state three forms, the same count bounds, the plain-literal needle, and categorical rejection of everything else. The round-5 arity fix is reflected in the code and in `design:149`; the other artifacts use the singular `body.count("literal")`, which the code now enforces. The design table's "the call's arguments" (design:145) is a loose plural, but `design:149` immediately states exactly one argument — observation, not a contradiction. `not in`, chained, and reversed comparisons all fall out of the code's shape restrictions and are named in the documents.

**K5 / L2 — The accepted limits are complete and honest: FIX (minor).**
The container limit (design:259-271) is now stated for both the `.count` receiver and the `in` right operand, and its false-coverage framing is correct: the live suite does assert membership against subprocess output (`test_attestation.py:96, 104, 117, 250` — all `"..." in v.stdout`/`p.stdout`) and hook context, and the pinned needles there are short status strings that cannot contain a marked region, so it is not live. Cross-region coverage (design:278-282) still locks the region text to a real scanned document — editing the region or the pinned document both go red — so "the one accepted limit that could manufacture coverage" (design:263-265) survives.

However, L2 asks whether any OTHER limit is secretly in the manufactured-coverage category, and one is: **pins are collected syntactically, with no execution awareness.** `collect_pins` walks every `ast.Assert` in the file (plan:815-817). An assertion that never runs still registers as a pin. This is live structure, not hypotheticals: `test_attestation.py:29-30` applies a module-level `pytest.mark.skipif` that skips the entire module when no PowerShell host exists, and every membership pin in it (e.g. `:96, :117, :128, :136`) still collects; `pytest.skip` guards at `test_multi_model_verify.py:1168, 1285, 1290, 1813-1817` have the same property. A pin inside a never-executing test locks nothing at runtime regardless of what its container is — that is outside the container limit's stated scope ("whether its container is a document", design:259) and is the same manufactured-coverage category. Not live today: no marked region body sits inside any skipped or dead assertion, and all nine planned pins land in unconditionally-run tests. But the container limit is not live either; both are stated because they are structural, and the suite's own baseline carries "1 skipped" (plan:35). **Specific fix:** one sentence appended to the container limit in `design:259-271`, to the effect of: pins are collected from syntax alone, so an assertion that never executes in the gating environment (a platform-skipped module or test) still registers; like the container limit, closing this is not possible from the syntax tree, so it is stated rather than closed.

**K6 — Nothing from rounds 1-4 regressed: PASS.**
I recounted the test function definitions: Task 1 adds 20 (plan:93-278), Task 2 adds 20 (plan:494-694), Task 3 adds 4 (plan:992-1020), Task 4 adds 2 (plan:1085-1102). Arithmetic: 170+20=190 (plan:465), +20=210 (plan:857, and the intermediate 40 at plan:852 is 20+20), +4=214 (plan:1032), +2=216 (plan:1226, 1376, 1526, 1605), matching the summary at plan:1642-1645. Nine-region scope intact: the final `DECLARED_REGIONS` holds nine ids (plan:1424-1435) matching `design:333-346`. History fixtures keep their two-region control/defect structure with the non-vacuity guard (plan:874-877, 1010-1020). The `fallbacks.md` selection rule (plan:1404-1413) cites `fallbacks.md:190` and `fallbacks.md:210` — both verified: `:190` is the `### Panel lane loss` heading, `:210` the `### Panel lane unavailable` heading. Indentation instructions present in Tasks 4 and 5 (plan:1122, 1285-1286, 1303-1305).

**K7 — Executable by a zero-judgment implementer: PASS.**
All code blocks are verbatim; every document edit gives the exact normalized target body, and I verified each target sentence exists in the live files: `skills/multi-model-verify/references/panels.md:73-77` (matches plan:1290-1291 after normalization), `agents/fable-panel-reviewer.md:30-33` (matches plan:1309-1310), `skills/multi-model-verify/references/fallbacks.md:196, 220-226` (matches plan:1448-1478, with the sentence after the third region — `An unavailable lane is recorded` at `fallbacks.md:226-227` — correctly excluded per plan:1460-1461). The Task 4/5/6 replacement pins match their marked bodies exactly (plan:1189-1193 vs 1131-1135; 1207-1211 vs 1138-1141; 1339-1344 vs 1291; 1361-1365 vs 1310; 1507-1517 vs 1466-1478). Fixture SHAs and verification greps are given (plan:900-903, 967-972). No step requires invention.

**L1 — The one-argument count rule matches every live pin: PASS.**
All seven live `.count()` call sites take exactly one positional argument and no keywords: `test_backup_lane.py:470-472`, `test_multi_model_verify.py:1003`, `test_multi_model_verify.py:1356`, `test_seat_reshuffle.py:102, 103-104, 105-106, 133`. (`test_seat_reshuffle.py:102` passes a Name, dropped by the name-binding limit — an arity non-issue.) Comparisons are all positive (`== 1`, `== 2`, `>= 2`, `>= 3`). The regression test exists at plan:605-614.

**L3 — The corrected fragment-loss claim is accurate: PASS.**
I read all three assertions (cited under K1). Each genuinely requires its fragments to be present in a document body — `assert "--model " + CANONICAL_ID in body` fails if `--model ` is deleted — so "genuine partial locks, dropped deliberately, costing no current marked coverage" is the honest description, and both documents now say exactly that (design:155-160; plan:717-726).

---

## Unverified measurements (no shell, cannot re-derive)

- The 715 → 366 pool numbers (design:164-165, plan:766-770) and the 633 assert count (design:41). Internally consistent across both documents; if the pool numbers differ, no plan step depends on them — they are context, not gates.
- Baseline `170 passed, 1 skipped` (plan:35) and the per-task suite totals. The plan self-corrects via plan:1640-1646 ("count the tests you actually added"), and my recount of the added test functions (20/20/4/2) confirms the deltas, so the plan holds even if the baseline differs.
- The pre-planning coverage simulations (plan:1054-1057, 1317-1320, 1452-1453, 1485-1488). Each is backed by an exact-body match I verified by hand (K7), so the predictions are grounded, but the RED/GREEN sequence itself is unverifiable from reading.

None of this is folded into any verdict.

---

## Verdicts

- K1: PASS
- K2: PASS
- K3: PASS
- K4: PASS
- K5/L2: **FIX** — add one sentence to the container limit (design:259-271) recording that pins are collected syntactically and a never-executing assertion (platform-skipped module or test) still registers as a pin; same category, same "stated rather than closed" treatment.
- K6: PASS
- K7: PASS
- L1: PASS
- L3: PASS

**Overall: FIX (minor, documentation-only).** The round-4 and round-5 fixes introduced no new mechanical defect that I could construct; the marker parser's new control flow survives every attack shape I could build beyond the one already declared. The single finding is an unstated sibling of the container limit — execution-blindness of pin collection — which belongs in the same bullet for honesty, not because it is live. The plan is otherwise safe to execute as written.

To resume this session: kimi -r 049ce8a8-b55a-4be2-a41d-d3d81104faba
