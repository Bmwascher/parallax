All checks complete. Here is the round-5 review.

---

# Round 5 review — contract coverage design & plan, revision 4

## K1 — The literal-needle rule costs nothing real: **PASS**

I hunted the live test tree for expression-needles in the three clause positions. What exists:

- A concatenation needle: `assert "Canonical backup reviewer model id: `" + BACKUP_ID + "`" in notes` (evals/multi-model-verify/test_backup_lane.py:48) — dropped under `_literal` (plan:706-708), but it locks the model-id line, which is not one of the nine marked regions.
- The name-bound pin from round 4: `required = (...)` then `assert skill.count(required) == 1` (evals/multi-model-verify/test_seat_reshuffle.py:97-102) — dropped, but locks SKILL.md text, outside the scanned trees and outside all nine regions.
- F-string fragments (e.g. test_multi_model_verify.py:1778) — tiny fragments that cannot contain any of the nine region bodies, all of which are full sentences (plan:1110-1139, 1273, 1292, 1431, 1448, 1454, 1460).

Critically, the two pins the plan's RED-step predictions depend on survive the strict rule as plain literals: the residual-gap whole-sentence pin (test_backup_lane.py:163-165, matching plan:1037 and plan:1148-1150) and the panel-lane-loss disposition pin (test_seat_reshuffle.py:159-161, matching plan:1434-1436). No conditional operand exists anywhere in the tree (grep for `if ... else` in `test_*.py`: no matches). No marked region loses a lock.

## K2 — The opener-based preflight is sound: **PASS**

I attacked the span bound (plan:389-399) directly:

- **Valid marker + later unterminated `<!--`:** a bare `<!--` never matches `OPENER` = `<!--\s*contract\s*:` (plan:329, 337); if the unterminated opener carries the keyword, `close == -1` sends the span to end-of-text and it is rejected (plan:391-392).
- **Two openers before any `-->`:** the first `-->` found belongs to a later marker, so the span crosses a line boundary and `len(span.splitlines()) != 1` rejects it (plan:393).
- **File ends mid-marker:** span-to-EOF, single line but no fullmatch → rejected; multi-line → rejected by splitlines.
- **Swallowing:** matches are short opener keywords containing no `<` after `<!--` (only `\s*`), so one match cannot consume a second opener's `<!--`; each opener is examined from its own start. The round-4 `<!-->` case is covered by test (plan:220-231).
- **CRLF/CR:** the splitlines test handles `\r` and friends, with the regression test at plan:211-217.

The only input class that still vanishes is an opener that does not match `OPENER` at all (`<!--- contract:start id=x -->`) — exactly the broken-opener limit the design states openly at docs/superpowers/specs/2026-07-27-contract-coverage-design.md:240-251. I could not construct a marker-shaped input inside the recognizable family that escapes both passes.

## K3 — The spaced-colon tolerance broke nothing: **PASS**

All four live foreign markers are `<!-- shared-contract:start -->` / `<!-- shared-contract:end -->` (agents/flash-implementer.md:19,34; agents/implementer.md:13,28). `OPENER` is anchored immediately after `<!--` (plan:324-329); after `<!-- ` the next character is `s`, so none matches. A grep for `contract\s*:` over both scanned trees (`agents/`, `skills/multi-model-verify/references/`) returns only those four markers — nothing else exists for the widened `\s*contract\s*:` to trip on. The widened pattern also makes the spaced-colon spelling a hard failure, tested at plan:234-240.

## K4 — The four artifacts describe the same grammar: **PASS**

Checked pairwise and against the code:

| point | design | plan constraints | module docstring | CLAUDE.md text | code |
|---|---|---|---|---|---|
| three forms | design:140-146 | plan:18 | plan:738-743 | plan:1544-1549 | plan:752-779 |
| count bounds `==`/`≥` n≥1, `>` n≥0 | design:145 | plan:18 | plan:740-742 | plan:1546-1548 | plan:766-767 |
| plain-literal needle | design:148-153 | plan:20 | plan:696-704 | plan:1551-1552 | plan:706-708 |
| categorical exclusion | design:140, 213-223 | plan:21 | plan:750 ("Never called on Assert.msg"), 789-792 | plan:1560-1561 | plan:773, 779 |

No contradiction found. The bool-guard on the count comparator (plan:763-764) is an implementation detail none of the texts needs. One measurement pair differs — 194 strings "came from `assert x, "msg"`" (design:393) vs 192 "only reachable through a failure message" (plan:528, 744-745) — but "came from" and "only reachable through" are different sets and the former properly contains the latter, so the two are internally consistent. UNVERIFIED as numbers (no shell); the plan holds under either value.

## K5 — The accepted limits are complete and honest: **PASS**

Each named live loss verified live:

- Name-bound pin: test_seat_reshuffle.py:97-102 — the only such pin I could find, matching "one such pin exists today" (design:226-228).
- Regex locks: test_multi_model_verify.py:306, 307, 311, 318, 325 — all five exist, all literal patterns, all against `debate-protocol.md` (verified context at lines 299-325), exactly as design:231-234 states.
- Literal `==`: e.g. test_multi_model_verify.py:68 (design:239).
- `.count` receiver limit: every live receiver — `skill`, `nbody`, `verifier`, `text` (test_seat_reshuffle.py:102-133; test_multi_model_verify.py:1003, 1356; test_backup_lane.py:470) — is a document string, as design:255 claims.
- Broken-opener limit's process dependence is stated openly (design:246-251), and the task order actually provides it: ids are declared before any document is touched in Task 4 (plan:1060-1064 precedes 1098), Task 5 (plan:1240-1252 precedes 1260), and Task 6 (plan:1403-1417 precedes 1424).

Nothing understated; the "all lock text" phrasing (design:217-219) reads as describing pin-shaped uses of those constructs and is defensible — no overstatement I would call a defect.

## K6 — Nothing from rounds 1-4 regressed: **PASS**

- Task order: declaration precedes marking in all three marking tasks (cites above).
- Nine-region scope: 3 + 2 + 4 (plan:1060-1064, 1244-1252, 1405-1417).
- History fixtures unchanged: three instance tests plus the non-vacuity control (plan:974-1002).
- `fallbacks.md` selection rule: cites verified — `### Panel lane loss` is at fallbacks.md:190, `### Panel lane unavailable` at fallbacks.md:210 (plan:1392); the three unavailable rules sit at fallbacks.md:220-226 matching the plan's bodies, and `An unavailable lane is recorded` (fallbacks.md:226-228) correctly stays outside (plan:1442-1443).
- Indentation instructions: Task 4 (plan:1104) and Task 5 (plan:1284-1287) both present; fallbacks.md regions are top-level paragraphs, so none is needed there.
- Arithmetic: 20 Task-1 tests (counted, plan:93-278), 19 Task-2 (counted, plan:494-682), 4 Task-3, 2 Task-4: 170+20=190, +19=209, +4=213, +2=215, matching plan:1624-1626 and the per-task expectations.
- Replace-targets exist byte-for-byte in the live files: test_backup_lane.py:141-142 and :152 (plan:1161-1162, 1181); test_seat_reshuffle.py:134-136, :78-80, :173 (plan:1310-1312, 1333-1335, 1478).

## K7 — Executable by a zero-judgment implementer: **PASS**

Read end to end. Every mark step either quotes the full replacement block (Task 4, plan:1109-1140) or the exact normalized target body (Task 5, plan:1273, 1292; Task 6, plan:1431, 1448, 1454, 1460), and I verified each quoted body against the live documents (panels.md:73-77; fable-panel-reviewer.md:30-33; fallbacks.md:196, 220-226). Every extended pin is given in full and contains its region whole after normalization (checked Task 4 pins plan:1171-1175, 1189-1193 against regions plan:1112-1123; Task 5 plan:1321-1326, 1343-1347; Task 6 plan:1489-1499). Fixture texts are verbatim with git verification steps (plan:946-955). No step requires invention.

## UNVERIFIED items (measurements, no shell)

- 715 → 366 pin counts (design:157-158; plan:744-747) and 194-vs-192 failure-message counts: internally consistent as analyzed under K4; the plan holds if either number differs, since the load-bearing claim is only that all nine regions and three controls keep coverage, which I verified structurally.
- The five dropped fragment strings named in the brief's measurements: one is described as `'Canonical backup reviewer model id: '` (trailing space) where the live source is `"Canonical backup reviewer model id: \`"` ending in a backtick (test_backup_lane.py:48). Immaterial to the artifacts under review — neither document enumerates the five — and either way the fragment cannot contain a marked region.
- Baseline `170 passed, 1 skipped` (plan:35) and the "simulated before planning" predictions (plan:1036-1039, 1299-1302, 1434-1436, 1467-1470): the two that matter structurally (the two already-covered regions) I verified depend on plain-literal pins that survive the strict rule.

## Verdicts

- K1: **PASS**
- K2: **PASS**
- K3: **PASS**
- K4: **PASS** (194/192 noted as UNVERIFIED, internally consistent)
- K5: **PASS**
- K6: **PASS**
- K7: **PASS**

**Overall: PASS.** Round 4's fixes — the strict literal needle, the opener-based preflight with first-`-->` span bounding, the splitlines single-line test, and the spaced-colon tolerance — introduced nothing I can refute against the files, and nothing five rounds has missed surfaced in this pass. This is a clean pass on evidence, not a loop-closing gesture.

To resume this session: kimi -r 049ce8a8-b55a-4be2-a41d-d3d81104faba
