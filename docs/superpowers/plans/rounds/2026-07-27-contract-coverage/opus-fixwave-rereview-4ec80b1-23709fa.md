# Scoped re-review of the fix wave — range `4ec80b1..23709fa`

Dispatched on Opus by the controlling session under
subagent-driven-development's final-review fix loop. Raw reply, verbatim,
retained unedited.

---

The fixes hold. All four brief items are closed, verified by running, not by reading. Working tree left exactly as found (clean at `23709fa`).

## 1. Item verification (reproduced independently)

| Probe | Result |
|---|---|
| Malformed unterminated marker appended to `skills/multi-model-verify/SKILL.md` | 2 failed, 49 passed — `MarkerError: SKILL.md: malformed contract marker` at `evals/multi-model-verify/contract_coverage.py:105` |
| Well-formed UNPINNED region in `skills/multi-model-verify/SKILL.md` | 2 failed — `assert not [('probe-unpinned', 'SKILL.md', ...)]` at `evals/multi-model-verify/test_contract_coverage.py:555` |
| Well-formed UNPINNED region in `commands/doctor.md` | 2 failed — `('probe-cmd', 'doctor.md', ...)` |
| Malformed unterminated marker in `commands/intake.md` | 2 failed |

Each probe was reverted with `git checkout --` and `git status --short` was empty after every one. The old `DOC_PATHS` covered neither file; the new one at `evals/multi-model-verify/test_contract_coverage.py:512-516` covers both.

## 2. Widening — collateral damage

Nothing unintended is swept in.

- The whole new surface is 9 + 5 + 3 = 17 files. `find skills -name "*.md"` returns 9; `agents/` has 5, `commands/` has 3. The only `contract:` markers in that surface are the 9 declared regions plus the two `shared-contract:` blocks at `agents/implementer.md:13` and `agents/flash-implementer.md:19`, which the anchored `MARKERISH` at `contract_coverage.py:39` correctly leaves alone.
- No stale doc: nothing in `docs/superpowers/specs/2026-07-27-contract-coverage-design.md` or the module names the old two globs, so the widening left no description behind.
- No symlinks: `git ls-files -s skills agents commands` yields zero mode-120000 entries. Python is 3.12.10, whose `**` does not recurse symlinked directories anyway.
- No globs overlap, so no dedup is needed.
- Repo-wide check: `git grep` for the marker opener finds live markers only in the scanned set, plus `docs/` (design, plan, round records — discussion of the syntax, deliberately unscanned) and `evals/.../fixtures/` (driven by their own tests). Nothing real is left invisible.
- The widened set matches an existing repo convention: `evals/multi-model-verify/test_backup_lane.py:508-510`, `test_flash_implementer.py:142-144`, and `test_multi_model_verify.py:250` already enumerate `skills/**/*.md`, `commands/*.md`, `agents/*.md` as the plugin's document surface.

**Minor, non-blocking:** the checker has no fenced-code-block awareness. I appended a ```markdown fence containing a well-formed marker to `SKILL.md`; it was parsed as a real region and went red. `SKILL.md` and `commands/*.md` are exactly the files most likely to one day document this mechanism to a user. The failure direction is loud, and fence-exemption would create the silent-skip escape hatch the design forbids (`contract_coverage.py:22-25`), so this is a property to know, not a defect to fix.

## 3. Mutation testing — all five new tests are load-bearing

Each mutation was applied to `contract_coverage.py`, the matching test run, then the file restored byte-for-byte.

| Mutation | Test result |
|---|---|
| `_literal` resolves `ast.Name` → returns `node.id` | 1 failed — extra item `'NEEDLE'` |
| `ast.Eq` on a Compare returns `_literal(right)` | 1 failed — extra item `'text'` |
| `ast.NotIn` treated as `ast.In` (`contract_coverage.py:241`) | 1 failed — extra item `'text'` |
| `_literal` walks the subtree instead of reading one node | 1 failed — extra items `'a'`, `'b'` |
| `START`/`END` made `re.IGNORECASE` (`contract_coverage.py:19-20`) | 1 failed — `DID NOT RAISE MarkerError` |
| Bonus: `re.IGNORECASE` removed from `MARKERISH` (`contract_coverage.py:39`) | 1 failed — actual message `'demo.md:3: end with no start'` |

The four parametrized cases fail one at a time, so no case is riding on another. The bonus mutation confirms the capitalized-marker test locks the invariant from both sides: whether the preflight over-accepts or the opener under-matches, it goes red.

## 4. Documentation accuracy

- **`CLAUDE.md` rewrap is meaning-preserving, proven mechanically.** A word-level diff of the whole contract-pin paragraph between `4ec80b1` and `23709fa` shows exactly eleven added words and zero removed — the new scanned-surface sentence at `CLAUDE.md:49-50`. Every other word is identical, so the rewrap changed only line breaks.
- The rule stays correct: `CLAUDE.md:55-56` says `== n` or `>= n` with n at least 1, or `> n` with n at least 0; `CLAUDE.md:66-67` excludes only `== 0` / `>= 0`. That matches `contract_coverage.py:250-251` exactly.
- The over-long line is gone. The longest line in the paragraph is now 71 characters; the only line over 75 in the whole file is `CLAUDE.md:5`, pre-existing and outside the range.
- The scanned-surface sentence is accurate, including the recursive/non-recursive distinction ("all Markdown under `skills/`" vs `agents/*.md`).
- **Design spec addition is correct.** `docs/superpowers/specs/2026-07-27-contract-coverage-design.md:308-316` is tagged **FALSE COVERAGE**, sits among the neighbouring entries, and the diff for that file is purely additive — nine added lines, zero removed. No count of limits was introduced.

## 5. Gates

All four pass at `23709fa`, re-run after all probing:

- `python -m pytest evals -q` → **221 passed, 1 skipped** (216/1 + 5, matching the report)
- `python evals/tools/skill_lint.py skills/multi-model-verify --strict` → PASS, 0 errors / 0 warnings
- `python evals/tools/skill_scanner.py skills` → clean, 0 CRITICAL / 0 WARN / 0 INFO
- `python evals/tools/run_trigger_evals.py` → PASS, 5 positives clear 5 near-misses

## Also found (Minor, pre-existing, outside the reviewed range)

`docs/superpowers/specs/2026-07-27-contract-coverage-design.md:226-228` narrates that the false-coverage count "was written as one, corrected to two, and was still wrong: a reviewer then showed cross-region coverage is a third." The new lockstep entry makes a fourth. The sentence reads as history explaining why the count was dropped, not as a live total, and it is unchanged in `4ec80b1..23709fa`, so it is not this wave's defect. It is the same drift the section warns about, one level down. Not a merge blocker.

**Verdict: SAFE TO MERGE.**
