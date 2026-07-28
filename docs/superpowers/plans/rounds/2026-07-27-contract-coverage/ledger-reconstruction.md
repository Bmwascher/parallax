# SDD ledger — RECONSTRUCTED, not the original

The original ledger lived at
`.superpowers/sdd/2026-07-27-contract-coverage/progress.md` and was
DELETED by the controlling session at the subagent-driven-development
skill's cleanup step, after the final review came back clean and before
this mode-diff debate was requested. It was git-ignored, so it is not
recoverable.

What follows is the controlling session's reconstruction from its own
context. Treat every line as a session claim under the strike rule, not
as a primary artifact. Where a claim is checkable against the repo or
git, check it there.

## Execution shape

Seven tasks from `docs/superpowers/plans/2026-07-27-contract-coverage.md`,
revision 7. One fresh implementer per task, one separate task reviewer per
task, then one whole-branch review.

Commits, in order:

| task | commit | subject |
|---|---|---|
| 1 | `672d831` | parse contract regions and reject malformed markers |
| 2 | `bfe1490` | collect pins from asserts and check whole-region coverage |
| 3 | `e6aa1a6` | prove the checker catches pin-integrity instances 10, 11 and 12 |
| 4 | `a615871` | mark the rotation guard and extend the two pins it proved short |
| 5 | `62b03cc` | mark the panel harness floor and extend the two pins it proved short |
| 6 | `f4cec83` | mark the panel lane failure classes |
| 7 | `2c61b42` | document the contract coverage checker and bump the version |
| 7 fix | `4ec80b1` | fix contract text rule to name excluded count comparison forms precisely |

Test totals reported after each task: 190, 210, 214, 216, 216, 216, 216.
Every one matched the plan's prediction exactly.

## Escalations to the human partner

Two, both plan-mandated conflicts the skill routes to the human.

1. **Task 3 BLOCKED.** The history fixtures are byte-verbatim `git show`
   copies of old test files, so they contain `BACKUP_ID`, which tripped
   `test_backup_literal_single_source` — that test sweeps
   `evals/**/*.py`. Ruling: exclude the fixture directory from the sweep.
   Applied in `test_backup_lane.py` via `Path.is_relative_to`, alongside
   the pre-existing `docs/**` exclusion.

2. **Task 7 CRITICAL.** `CLAUDE.md` said `> n` with n at or above zero
   locks, while its own exclusion list said "a zero or negative count
   comparison" locks nothing. `body.count("x") > 0` does lock. The wrong
   wording originated in the plan's own Global Constraints and survived
   all six plan-review rounds. Ruling: fix all three sites. Landed as
   `4ec80b1`.

## Final whole-branch review

Dispatched on Opus over `8d54f6c..4ec80b1`. Verdict: safe to merge, with
one Important finding and four Minor.

**Important — the marker mechanism was silently inert outside two
directories.** `DOC_PATHS` covered only
`skills/multi-model-verify/references/*.md` and `agents/*.md`.
`skills/multi-model-verify/SKILL.md` and `commands/*.md` are contract
documents and were not scanned. The reviewer verified live that both a
well-formed unpinned region AND a malformed unterminated marker appended
to `SKILL.md` left every test green. The second defeats the design's
headline invariant: a malformed marker must always be rejected, never
skipped. No document named the scanned set, which is why six plan-review
rounds and seven task reviews all read past it.

The reviewer stated it could not produce a false pass on a declared
region, having probed roughly twenty near-miss forms.

## Fix wave

One dispatch covering four items, landing as `f872b34`, `8a6a9fb`,
`8d313b9`, `23709fa`:

1. Widen `DOC_PATHS` to all Markdown under `skills/`, plus `agents/*.md`
   and `commands/*.md`; name that scanned surface in `CLAUDE.md`.
2. Add five tests locking documented exclusions that had none: variable
   needle, plain equality, `not in`, conditional expression, and a
   capitalised `CONTRACT:START` marker that must raise `MarkerError`.
3. Rewrap the over-long `CLAUDE.md` line without changing meaning.
4. Name the lockstep-shrink limit in the design spec, tagged FALSE
   COVERAGE.

Total after the wave: 221 passed, 1 skipped.

One scoped re-review on Opus over `4ec80b1..23709fa` reproduced every
proof independently, mutation-tested all five new tests (each goes red
when its locked behaviour is removed), word-diffed the `CLAUDE.md`
paragraph to show eleven words added and none removed, and found no
collateral damage from the widening. Verdict: SAFE TO MERGE.

## Carried, not fixed

- No fenced-code-block awareness. A marker inside a ``` fence parses as a
  real region. The direction is loud, and exempting fences would build
  the silent-skip hole the design forbids.
- `PIN_PATHS` excludes the self-quoting module by exact filename only.
- `test_flash_implementer.py` carries the same `evals/**/*.py` sweep glob
  with no fixture exclusion, so a future fixture re-opens the Task 3
  ruling.
- The design spec's account of the false-coverage count reads as past
  tense history, not a live total. Left as written; the paragraph argues
  against extending it.

## Known gap in the plan-phase record

`debate-record.md` in this directory covers mode-plan rounds 1 and 2
only. Four further rounds ran (3 through 6, Sol and Kimi as a panel) and
were never folded into it. Twenty-one plan defects were found across all
six rounds. The record's **Verification status: FULL** and terminal PASS
stand; the round accounting in it is incomplete.
