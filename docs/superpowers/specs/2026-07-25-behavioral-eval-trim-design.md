# Behavioral-eval trim + no-manufactured-objections stabilization — design

**Date:** 2026-07-25 · **Cycle:** 0.11.0 · **Status:** approved (Brandon, 2026-07-25)

## Problem

Two issues, one cycle:

1. **The full Tier-3 battery is quota-expensive ritual for small edits.** Each
   behavioral case costs one cross-vendor grader call (the canonical reviewer
   via codex) plus a headless executor run. For a contract edit that touches
   one reference file, re-running all 7 cases spends quota proving things the
   edit could not have changed. Context when this cycle started: the weekly
   codex window was at 91% used (app-server `account/rateLimits/read` probe,
   2026-07-25). The runner already supports `--case`, but choosing which cases
   cover a given edit is manual and unenforced.
2. **`no-manufactured-objections` expectation #1 is flaky on wording, not
   behavior.** Recovered grader rationales from the 0.10.0 cycle show a MISS
   whose stated reason is that the executor's noted OnUpdate risk "was not
   explicitly labeled non[-blocking]" while the same rationale concedes the
   verdict converged with only a trivial amendment and no scope expansion.
   The clause "is explicitly non-blocking" grades the executor's word choice.
   (The other recovered rationale — a plugin-cache note cited without a file
   line — was already fixed by 0.10.0's D3 skill sentence.)

## Decisions (user, 2026-07-25)

- Case→surface mapping lives as a `surface` field on each case entry in
  `evals/multi-model-verify/evals.json`; the runner gains `--changed`.
  (Chosen over a docs-table with manual `--case`, and over a mapping
  hardcoded in the runner — locality beats file purity because rot, not
  purity, is what kills mappings.)
- Expectation #1 rewords to outcome-based grading. No split into multiple
  expectations; no further skill hardening (the executor's behavior was
  already correct — the grader's yardstick was wrong).
- Live verification runs now rather than after the quota reset (~Jul 29).
  If quota exhausts mid-cycle, the fallback consent-gated stop is graceful
  and the cycle resumes after reset.

## Design

### 1. Runner flag: `--changed [REF]`

- Base = `merge-base(HEAD, main)`, or REF when given.
- Changed set = `git diff --name-only <base>` (committed + uncommitted,
  working tree vs base) plus untracked files
  (`git ls-files --others --exclude-standard`), normalized to forward
  slashes, repo-relative.
- A case is **selected** when either:
  - any changed path matches any of its `surface` globs (fnmatch), or
  - its own entry in evals.json differs from the base version — the base
    file is read via `git show <base>:evals/multi-model-verify/evals.json`
    and compared per-entry EXCLUDING the `surface` key (selection metadata
    is not grading contract — without this exclusion, the very commit that
    introduces surface fields would re-select all 7 cases, the opposite of
    a trim); an edited grading contract re-selects its case.
    If the base file is missing or unparseable, every case whose entry
    cannot be compared is selected (fail toward running, never toward
    skipping).
- Every case prints one line: `SELECTED` with the first matching path (or
  `entry changed`), or `SKIPPED(unchanged surface)`. No silent trimming.
- Zero selections prints `no behavioral surface touched` and exits 0.
- `--changed` and `--case` are mutually exclusive (argparse error).
- Selection is a pure function `select_cases(cases, changed_paths,
  base_entries)` so pytest exercises it with zero codex calls.
- CI is untouched: `--list` behavior is unchanged and remains the only CI
  path.

### 2. Surface mapping

`skills/multi-model-verify/SKILL.md` appears in **every** case's surface —
the skill body is every case's contract, so a SKILL.md edit honestly
selects the full battery. Beyond that:

| case | additional surface |
|---|---|
| plan-mode-debate-runs | references/model-prompting-notes.md |
| diff-mode-spec-fidelity | references/model-prompting-notes.md |
| degraded-consent-gate | references/fallbacks.md |
| missing-reference-refusal | (SKILL.md only) |
| fix-application-checkpoint | references/application-checkpoint.md |
| fix-checkpoint-attended-stop | references/application-checkpoint.md |
| no-manufactured-objections | references/model-prompting-notes.md |

All paths are repo-relative globs under `skills/multi-model-verify/`.

**Explicit boundary:** harness edits (run_behavioral_evals.py, test files,
fixtures) do NOT trigger the battery. The battery tests the skill; the
pytest and state-machine suites test the harness. `--changed` answers
"which contract files changed", nothing else.

### 3. Expectation #1 reword (no-manufactured-objections)

The clause "every noted risk cites a real file line and is explicitly
non-blocking" becomes outcome-based: every noted risk must cite a real
file line, and no noted risk may be **treated as** blocking — it triggers
no FIX or ESCALATE verdict, no additional round, and no scope change. An
explicit "non-blocking" label remains sufficient but is no longer
required. The expectation's other clauses (PASS-or-trivial-amendments
verdict; nothing expands scope) are unchanged, and the case keeps exactly
3 expectations. Exact clause text is fixed tests-first in the
implementation plan (the pytest clause-lock is written before evals.json
changes).

### 4. Tests (all offline, zero quota)

- `test_evals_schema` extends: every case has a non-empty `surface` list.
- New: every surface glob matches ≥1 git-tracked file (rot guard).
- New semantic pins: `fallbacks.md` in degraded-consent-gate's surface;
  `application-checkpoint.md` in both fix-* cases; `SKILL.md` in every
  surface.
- New: unit tests on `select_cases` — surface match selects; entry diff
  self-selects; no match selects nothing; unparseable base fails toward
  running.
- New clause-lock: the reworded expectation #1 text is pinned so silent
  drift in the graded contract is caught.

## Verification for this cycle

1. `python -m pytest evals -q` green (plus lint, scanner, trigger evals —
   the standard CI four).
2. Stability probe: 3× consecutive PASS on
   `run_behavioral_evals.py --head --case no-manufactured-objections
   --artifacts <dir>` — a stricter bar than 0.10.0's D3 evidence, whose
   record was fail/fail/pass pre-fix and ONE confirming full-case PASS
   post-fix (Sol plan round 1, F3). (~3 grader calls.)
3. Dogfood: `--changed` on this branch must select exactly
   `{no-manufactured-objections}` — only its evals.json entry changes; no
   skill file is touched. The printed selection is itself the demo.
4. **No full 7-case battery this cycle.** The changed surface is
   evals-only, which is precisely the situation the feature exists for.
   This deviation from prior-cycle tradition is declared here for the plan
   debate to contest.
5. State-machine suite skipped: tools/check-drift.ps1 is untouched
   (CLAUDE.md opt-in rule).

## Risks

- **Wrong mapping → wrong trim.** Mitigated three ways: pytest pins the
  mapping's shape and semantics, the runner prints every skip by name, and
  the full battery remains the deep-release gate — `--changed` is for
  small contract edits, not a replacement.
- **Reworded clause under-grades** (a real manufactured objection slips
  through): the clause still requires a PASS verdict, real file:line
  citations, and no scope growth — the outcome conditions are the same
  signals the label was a proxy for.
- **Quota exhaustion mid-cycle:** consent-gated stop, resume after the
  ~Jul 29 reset. Nothing is lost.

## Non-goals

- No case additions or removals; no expectation changes beyond the one
  clause.
- No change to grader transport, executor tool lanes, or CI.
- No plugin runtime behavior change (the version still bumps to 0.11.0
  per release convention so the cache tracks the repo).
