Both documents and all the live trees the claims point at are now read. Executing the round-4 brief claim by claim.

---

## Evidence gathered this run

- Scanned trees: `skills/multi-model-verify/references/` contains **zero** HTML comments; `agents/` contains exactly four, all one-line `shared-contract:` markers (`agents/flash-implementer.md:19`, `:34`; `agents/implementer.md:13`, `:28`).
- Live pin shapes: `.count(` receivers are `skill`, `verifier`, `text`, `nbody` (`test_seat_reshuffle.py:102–106`, `:133`; `test_multi_model_verify.py:1003`, `:1356`; `test_backup_lane.py:470`).
- The live `or`-shape is confirmed at `evals/multi-model-verify/test_flash_implementer.py:58`, plus a second one at `:104` (`assert "never" in window or "forbidden" in window`).
- The name-bound pin is confirmed exactly once: `test_seat_reshuffle.py:97–102` (`required = (...)` then `assert skill.count(required) == 1`).
- The regex lock the design cites is real but at `test_multi_model_verify.py:318`, not `:313` — and it is **not** the only literal regex lock on the same document: `:306` (`manufacture`), `:307` (`sound plan`), `:325` (`final adjudication`) all pin `debate-protocol.md` literal phrases in the same file, plus `:370`, `:417`, `:934` elsewhere.

---

## Per-claim review

**G1 — clause grammar cannot be inverted. PASS, with one latent defect in the *implementation* of the count form (F3).**
Inversion is genuinely closed: `_clause_pins` recurses only through `ast.BoolOp`/`ast.And` (plan `docs/superpowers/plans/2026-07-27-contract-coverage.md:661-665`); `Or`, `UnaryOp`, `not in`, and `== False` all hit the terminal `return set()` (`:682`, `:688`). Both live `or`-shapes (`test_flash_implementer.py:58`, `:104`) yield nothing, so `does not reach` cannot leak. Constructed cost case (required but dropped): `assert (n := body.count("The rule.")) >= 1` — a walrus left operand fails `_is_count_call` and is dropped; safe direction, same class as the documented name-bound limit. Constructed defect case (not required but collected): `_is_count_call` (`:627-630`) matches **any** attribute named `count`, so `assert path_list.count("The rule stands.") == 1` — a list-membership count over something that is not a document — manufactures a pin. Not live today (all four live receivers are document strings), but the code is broader than every one of the four grammar statements, which all say `body.count(...)`.

**G2 — the three forms are the right three. PASS.**
Every positive shape the repo actually uses is either collected or a documented limit: `in` with implicit concatenation (`test_seat_reshuffle.py:113-119`), `count == n` (`:103-106`, `:133`), `count >= n` (`test_multi_model_verify.py:1003`, `:1356`), `and`-conjunctions (`test_attestation.py:304`, `test_multi_model_verify.py:1800`). Excluded live shapes are all genuinely non-required: the two `or`-shapes, the one name-bound pin (documented at design `docs/superpowers/specs/2026-07-27-contract-coverage-design.md:210-213`), `==` equality (all live instances are JSON fields, not document prose — `test_attestation.py:232`, `test_multi_model_verify.py:68`), and regex locks (a documented limit — but see F2). No undocumented positive exclusion found.

**G3 — whole-text preflight closes the marker class. PASS.**
I constructed the three shapes the brief names against the code at plan `:291-299` and `:332-351`: (a) a marker in a fenced code block is not fence-aware, but it *fires* (parses or hard-fails), never vanishes — and the live scanned trees contain no comments at all to trip it; (b) a marker nested in another comment on one line (`<!-- <!-- contract:start id=x --> -->`) is skipped by `_preflight` (`KEYWORD` anchor, `:299`) but then caught by the line scan (`MARKERISH` hits, `START.fullmatch` fails, `:317-329`) — rejected, not vanished; (c) when both passes could fire, preflight strictly raises first on multi-line/unterminated spans (`:345-351`), and the one disagreement direction (two clean comments sharing a line) is caught by the line scan's "alone on its line" rule and covered by the test at plan `:210-216`. Nothing I constructed vanishes without the declared-inventory backstop also firing. One adjacent documentation gap under G5 (F4).

**G4 — preflight cannot break the live tree. PASS.**
`DOC_PATHS` scans only `skills/multi-model-verify/references/*.md` and `agents/*.md` (plan `:957-960`) — confirmed, not assumed: `docs/` is not globbed, so the plan's and spec's own marker examples are unscanned. The four live `shared-contract:` markers are each a clean single-line comment whose body starts with `shared-`, so `KEYWORD` (`\s*contract:` anchored, plan `:299`) does not match and `MARKERISH` (`<!--\s*contract:`, `:291`) does not either. The Task-3 fixture docs' multi-line header comments (plan `:805-807`) likewise fail `KEYWORD` and are skipped. `COMMENT`'s non-greedy `(.*?)(?:-->|\Z)` (`:298`) terminates each match at the first `-->`, so comments cannot bleed into each other.

**G5 — accepted limits are honest. FIX (two accuracy defects, F2 and F4).**
The `count == 0` rewrite (design `:226-231`) is honest and now gives the correct repo-wide-pooling reason. But:
- **F2:** the regex-lock limit says "a much larger rule for one case" and cites `test_multi_model_verify.py:313` (design `:213-218`). The cited assertion lives at `:318`; line 313 is the test's `def`. And it is not one case: `:306`, `:307`, and `:325` are literal-phrase regex locks on the *same document* in the same file. The decision (drop regexes, safe direction) stands; the justification and citation are wrong.
- **F4:** the marker-spelling limit names exactly one ignored spelling, `contract :` (design `:220-225`), while the mechanism ignores a wider class — e.g. `<!--- contract:start id=x -->` (opener typo) matches neither `MARKERISH` nor `KEYWORD` and is silently ignored, which sits awkwardly next to the failure table's blanket promise that "a `contract:` comment that is neither valid start nor valid end" is a hard failure (design `:192`). The stated safety argument (partner marker + declared inventory populated first, plan `:976-987` and task order) does cover the whole class, so this is a one-sentence broadening of the limit, not a mechanism change.

**G6 — nothing passed in round 3 regressed. PASS.**
Re-checked only what round 3 touched: the two new Task-1 tests (plan `:189-207`) match `_preflight`'s behavior and message text; the five new/rewritten Task-2 tests (`:503-548`) match `_clause_pins`; test counts are 17/17/4/2 (I counted the function definitions in each code block) giving 187/204/208/210 from the 170 baseline (plan `:34`, `:1516-1518`, step expectations `:412`, `:417`, `:743`, `:748`, `:923`, `:1117`); Task 2 Step 4's `34 passed` (`:743`) = 17+17; the nine-region inventory completes at 3+2+4 (`:969-973`, `:1153-1161`, `:1314-1326`); every marking task still adds ids to `DECLARED_REGIONS` in Step 1 before touching documents in Step 3; indentation instructions survive in Tasks 4 and 5 (`:1013-1016`, `:1193-1196`); the vacuous-pass warning survives (`:1000-1005`); the fallbacks selection rule survives (`:1295-1304`).

**G7 — the four artifacts describe the same grammar. FIX (F1 — the headline finding).**
Three of the four agree exactly: design clause table (design `:140-150`), Global Constraints (plan `:18-20`), module docstring (plan `:647-651`) — three forms, `== n`/`>= n` with n ≥ 1, `> n` with n ≥ 0, `and`-conjunction, and the full exclusion list including `or`, zero/negative counts, and regex. The fourth — **Task 7's CLAUDE.md text, the artifact finding 10 just rewrote** (plan `:1450-1456`) — names only **two** forms ("on the left of `"literal" in body`, or an argument to `body.count("literal")`"), omitting the `and` form and the count-comparison bounds entirely, and its "Nothing else counts" list omits `or`, zero-count comparisons, and regex. Concretely: live pins at `test_seat_reshuffle.py:103-106` (`count(...) == 2` / `== 1`) and `test_multi_model_verify.py:1003` (`>= 3`) are collected by the code but match no form CLAUDE.md describes; and an author who writes `assert "a" in body or "b" in body` has not been told `or` excludes both sides. The failure direction is safe (a red, never false coverage), but this is precisely the thirteenth-instance pattern — the instruction file disagreeing with the code — recurring inside the fix for the thirteenth instance.

---

## UNVERIFIED measurements (internally consistent; verdicts do not rest on them)

- `715 → 371` pins, `192` message-only, `19` `not-in` (design `:151`; plan `:654-656`): cannot re-derive without a shell; internally consistent (715−192−19=504, leaving 133 dropped by the remaining exclusions, plausible given the live `re.search` volume I grepped). The brief's own "375 become 371" is the round-2 collector's number and does not contradict the documents.
- "All nine region predictions unchanged, all three history controls still covered" (brief; plan `:945-948`, `:783-784`): simulated against git history I cannot read. The fixture bodies and the not-vacuous guard (plan `:901-911`) make a wrong prediction loud rather than silent, so the plan holds even if a number differs.

---

## Verdicts

- **G1: PASS** (with F3 noted: `_is_count_call` accepts any receiver while all four documents say `body.count` — fix by adding one accepted-limit line, since a receiver-type check is impossible in `ast`).
- **G2: PASS.**
- **G3: PASS.**
- **G4: PASS.**
- **G5: FIX** — correct the regex-lock citation (`:313` → `:318`) and replace "one case" with the true count of literal regex locks (design `:213-218`); broaden the marker-spelling limit from the single `contract :` spelling to the ignored class (design `:220-225`).
- **G6: PASS.**
- **G7: FIX** — rewrite Task 7's CLAUDE.md paragraph (plan `:1450-1456`) to name all three clause forms, the positive-count bound (`== n`/`>= n`, n ≥ 1; `> n`, n ≥ 0), and the complete exclusion list, verbatim-aligned with plan `:18-20`.

**Overall: FIX.** Two documentation-grammar defects (F1 in the CLAUDE.md instruction text, F2 in the design's regex-limit justification), plus two low-severity broadening fixes (F3, F4). The round-3 mechanism fixes themselves — the clause rule and the whole-text preflight — stand: I could not construct an inversion, a leak, or a live-tree break against the files as they actually are.

To resume this session: kimi -r 049ce8a8-b55a-4be2-a41d-d3d81104faba
