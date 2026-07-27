# Review: Contract Coverage Design & Plan (mode `plan`)

Both documents read in full: `docs/superpowers/specs/2026-07-27-contract-coverage-design.md` (216 lines) and `docs/superpowers/plans/2026-07-27-contract-coverage.md` (1098 lines). All load-bearing live-tree facts were checked against the files they cite.

---

## Per-claim verdicts

**Claim 1 — Coverage, not replacement: PASS.**
The spec's Approach (`docs/superpowers/specs/2026-07-27-contract-coverage-design.md:38-59`) keeps substring pins and adds a coverage check; the Goal explicitly preserves the existing assertions (`...design.md:32-33`). The choice is defensible on evidence, not just assertion: the mechanism is additive (no migration of existing pins), reversible, and — decisively — it is gated on reproducing the three real failures before any live region is marked (`docs/superpowers/plans/2026-07-27-contract-coverage.md:451-455`, `:566-570`). Checksums or generated pins would sever the pin from the assertion that uses it, which the spec's registry rejection (`...design.md:56-59`) argues correctly. I pushed here per the boundaries and find no refutation.

**Claim 2 — Marking beats the alternatives: PASS.**
Whole-file rejection rationale at `...design.md:47-49` matches what I read in the reference files (rationale, probe records, and dates interleaved with rules, e.g. `skills/multi-model-verify/references/backup-lane.md:27-32`, `:60-70`). The keyword-detection rebuttal is factually correct: `That is a route-attribution failure` (live at `backup-lane.md:57`) contains no modal word.

**Claim 3 — Whole-sentence containment beats overlap: PASS.**
Reasoning at `...design.md:53-55`. The direction is implemented correctly: `uncovered` requires `sentence in pin`, not the reverse (`...contract-coverage.md:414-416`). Instance 11's failing shape is reproduced as a unit test (`...contract-coverage.md:343-349`).

**Claim 4 — Pins read via `ast`: PASS, with one UNVERIFIED detail.**
The implicit-concatenation premise is confirmed by the repo's actual pin style (`evals/multi-model-verify/test_backup_lane.py:127-128`, `:141-142`, `:163-165`), and the exclusion of a registry is reasoned at `...design.md:56-59`. The measured counts (172 string constants, 40 over 60 characters, `...design.md:88-90`) are UNVERIFIED — I cannot run `ast`; they are not load-bearing for the design.

**Claim 5 — Declared region inventory: PASS.**
The deletion hole is correctly identified (`...design.md:112-116`) and closed by a set-difference test in both directions (`...contract-coverage.md:628-639`). The fixture pins files cannot accidentally satisfy it: they live outside the scanned document trees (`...contract-coverage.md:610-613` vs. fixture path at `:458-463`).

**Claim 6 — Splitter is safe enough: PASS.**
Rule at `...design.md:102-106`, implementation at `...contract-coverage.md:371-390`. The measurement holds: exactly six `e.g.` occurrences exist in the reference set and none is followed by a capital (`skills/multi-model-verify/references/fallbacks.md:16`, `:240`, `:268`; `.../frozen-plan-format.md:93`, `:103`; `.../model-prompting-notes.md:18`). The safe-direction argument is sound: a wrong split can only manufacture an uncovered fragment (a red), and a *missed* split merges sentences, which makes a containing pin harder, not easier, to find. Note, not a defect: the instance-12 fixture's bold heading (`**Harness floor: Claude Code 2.1.216.**`, `skills/multi-model-verify/references/panels.md:66`) ends in `.**`, so the splitter will merge it with the following sentence — the regression test tolerates this via `any(...)` (`...contract-coverage.md:550-554`).

**Claim 7 — Prerequisites verified before planning: PARTIALLY UNVERIFIED.**
Consistent with what I can read: no `conftest.py` exists anywhere under `evals/` (glob confirmed), matching the import claim (`...contract-coverage.md:26`). The `skill_lint`/`skill_scanner` runs and the git-history reproducibility of `4d8a121`/`8eacc8a`/`f9fd9b9` cannot be checked with read-only tools — UNVERIFIED, and not folded into any verdict.

**Claim 8 — Coverage predictions simulated, two wrong: PASS (verified against the live tree).**
- Rotation guard splits into six sentences (`backup-lane.md:52-70`): (1) offset-rule rationale, (2) detection rule, (3) consequence, (4) observation, (5) size-test caveat, (6) contingency. Exactly as `...contract-coverage.md:597-601` states. Only sentence 5 is whole-pinned today (`test_backup_lane.py:163-165`); sentences 2 and 3 are fragments (`test_backup_lane.py:141-142`, `:152`).
- The five unlocked sentences are real: panel-floor reference (`panels.md:73-77`, fragment pins at `test_seat_reshuffle.py:134-136`), panel-floor agent (`agents/fable-panel-reviewer.md:30-33`, fragments at `test_seat_reshuffle.py:78-80`), and the three `panel-lane-unavailable` sentences (`fallbacks.md:220-226`, fragment at `test_seat_reshuffle.py:173`). Containment indeed runs the other way (`...contract-coverage.md:835-837`, `:970-972`).

**Claim 9 — Checker proven before any live marking: PASS.**
Task 3 precedes all live marking and is an explicit stop-gate ("fix the checker, not the test", `...contract-coverage.md:569-570`). The non-vacuity guard requires exactly one region per fixture (`...contract-coverage.md:557-563`). The `sed` extraction patterns and historical commit contents (`...contract-coverage.md:477-496`) are UNVERIFIED (no shell), but the *design* of the proof is correct.

**Claim 10 — Accepted limits stated: PASS.**
Cross-region coverage and semantic-correctness limits are disclosed at `...design.md:154-165`. Self-satisfaction is closed two ways: the checker's own module is excluded from pin collection by name (`...contract-coverage.md:615-620`), and the historical pins fixtures match neither the `test_*.py` glob nor the document globs (`...contract-coverage.md:610-620`).

**Claim 11 — Six regions, not a mass edit: FIX (one factual error, scope otherwise correct).**
The six regions are the right six, and every quoted marked body matches the live text verbatim: rotation guard (`backup-lane.md:52-70`), panel floor in both documents (`panels.md:73-77`, `agents/fable-panel-reviewer.md:30-33`), and the two panel-lane classes (`fallbacks.md:196`, `:220-226`). The `panel-lane-loss` sentence is indeed already whole-pinned (`test_seat_reshuffle.py:159-161`), inside the function the plan names (`test_seat_reshuffle.py:156`). **But** "fallbacks.md defines eleven classes" (`...contract-coverage.md:921-922`) does not survive counting the file: I count 7 headed classes under `## Failure classes` (`fallbacks.md:55-117`), 8 backup-lane bullet classes (`fallbacks.md:140-185`), and 2 panel classes (`fallbacks.md:190-228`) — 17 entries; headed sections only gives 9; backticked class names only gives 6. No counting rule yields eleven. **Fix: correct the count or state the counting rule.** This does not change which two classes deserve marking — that judgment is evidence-based and stands.

---

## Boundary-driven findings beyond the numbered claims

1. **FIX (cosmetic):** `...contract-coverage.md:809-810` says "wrap only the two operative sentences" in panels.md, but the specified marked body (`...contract-coverage.md:818-820`) is one sentence, matching the live file (`panels.md:73-77`). The exact-body spec is unambiguous, so this is wording-only.
2. **Brittleness (pushed per boundaries): PASS with a caveat.** Containment is whitespace-normalized only (`...contract-coverage.md:18`); pins must match markdown punctuation exactly — the plan demonstrates this is achievable today (em-dash note, `...contract-coverage.md:744-746`) and keeps regions small by design (`...design.md:74-77`). The repo's prior failure mode (weakening a perpetually-red check) is mitigated by hard-failures-only (`...contract-coverage.md:16`) plus the inventory. The pressure point will arrive with "new contract text gets marked as written" (`...design.md:198`): pin-sync friction grows with region count, and the design offers no weakening valve — correctly — so expect that debate later. Not a defect now.
3. **Task order is safe.** Checker proven (Task 3) before live marking (Tasks 4–6); each task ends green; internal test-count arithmetic is consistent (9 → 18 → +4 → +2, `...contract-coverage.md:256`, `:435`, `:575`, `:756`). The known-forward cost — backlog item 5 rewriting marked rotation-guard text — is disclosed in both documents (`...design.md:201-205`, `...contract-coverage.md:1094-1098`), and the falsified Windows observation itself stays *outside* the markers (`...contract-coverage.md:673-677`), so Task 4's extended pins lock text that is not the falsified part.

## UNVERIFIED (not folded into any verdict)

- The 172/40 `ast` string-constant counts (claim 4).
- The lint/scanner/import prerequisite runs and git reproducibility of the three commits (claim 7); the `sed` patterns and historical blob contents in Task 3 Step 1 (claim 9).
- "529 existing assert statements" (`...design.md:33`): grep finds 650 lines containing "assert" across the eval suite, but that includes comment mentions; the exact statement count is not readable statically.

## Overall verdict: **FIX**

Two corrections, both minor: (1) the "eleven classes" count at `docs/superpowers/plans/2026-07-27-contract-coverage.md:921-922` — correct the number or state the counting rule; (2) the "two operative sentences" wording at `...contract-coverage.md:809` — the marked body is one sentence. The mechanism (coverage via whole-sentence containment over marked, inventoried regions) is the right mechanism, is proven before it is trusted, and every load-bearing live-tree fact I could check checked out.

To resume this session: kimi -r 049ce8a8-b55a-4be2-a41d-d3d81104faba
