# Fable whole-branch review — range `e94c0b5..d0e116a`

**Seat:** `agents/fable-reviewer.md`. **Branch:** `feat/home-skills-root-probe`.
**Scope:** Tasks 1 and 2 of six. Task 2 is the subject; Task 1 is checked for
whether the previous review's fixes were correctly applied.
**Date:** 2026-08-03. **Prior review:** `fable-review-e94c0b5-fbefa66.md`.

Raw reply retained verbatim as a range-bound artifact. Summary of the verdict
and the session's adjudication follow it.

**Assessment as issued: Ready to merge — With fixes.** No Critical. One
Important: the suite's state-file parser was a new instance of the tier-1c
"discard blanks, then count survivors" defect class, spelled with `.split("\n")`
rather than `.splitlines()` so the CI sweep could not see it. Five Minor,
covering an unwatched fault-seam position, two unexercised `-Force` claims, an
empty-root claim, an unguarded `-StateOut` overwrite, and an unwatched
blank-root guard, plus a named gap on commit trailers for the two new commits.

Full text of the Strengths, Issues, Ledger triage and Assessment sections is
reproduced in the session transcript and summarized in the adjudication below;
the operative content is the finding list, which is carried in full into
`execution-deviations.md` as D9 through D14 with each one's disposition.

## Session adjudication

Every finding was checked against the repo before acceptance. One was REFUTED.

- **Important, the tier-1c parser: CONFIRMED and FIXED.** `read_state` used
  `[ln for ln in raw.split("\n") if ln.strip()]` then asserted one survivor,
  which accepts `\n\n{json}\n\n` where the frozen interface says one line. It
  now goes through `accept_exactly_one_nonempty_line()`. Watched: mutation N1
  makes the tool emit a trailing blank line and `test_plant_state_file_shape`
  fails. Recorded as D9.
- **The sweep's blind spot: CONFIRMED, NOT FIXED, awaiting authorization.**
  `check_exact_line_oracles.py:89-91` keys on `gen.iter.func.attr ==
  "splitlines"`, so the `.split("\n")` spelling passes CI. Widening it to
  `("splitlines", "split")` was tested and flags nothing else in the repo.
  It is a change outside the frozen plan's six tasks, so it is recorded as D10
  for the user's call rather than taken unilaterally.
- **Fault-seam position: CONFIRMED and UPGRADED.** The plan froze the seam
  itself as the positive control for creation-before-state-write, and the
  reviewer correctly showed the seam alone cannot prove position. Replaced with
  a real observation: an inherit-only Delete deny on the root makes the rollback
  fail, and the tool's rollback-failure message names the surviving directory.
  Watched: mutation N5 moves the seam before `New-Item` and the test fails.
  Recorded as D11.
- **Two `-Force` claims: CONFIRMED and CLOSED.** Two cases added, one per site.
  Watched by mutations N3 and N4. Recorded as D12.
- **Blank-root guard unwatched: CONFIRMED and CLOSED.** The test now asserts the
  message, not only the exit code. Watched by mutation N2. Recorded as D13.
- **`-StateOut` overwrite: CONFIRMED, accepted as a limit.** Recorded as D14.
- **Empty root: REFUTED, with evidence on both hosts.** The reviewer stated that
  `Compare-Object -ReferenceObject @()` "throws a binding error on both hosts",
  so an empty root would fail after a successful delete. Measured 2026-08-03:
  `Compare-Object -ReferenceObject @() -DifferenceObject @() -CaseSensitive`
  returns count 0 without throwing on BOTH `powershell.exe` and `pwsh.exe`, and
  an end-to-end plant-then-remove against an empty root exits 0 with the canary
  correctly gone on both. No change made. This is the one finding where the
  reviewer's claim was wider than the behaviour.
- **Commit-trailer gap: CLOSED.** `git log e94c0b5..d0e116a` searched for
  `Claude-Session` returns 0.
- **Step 5's "record each observed failure message": CONFIRMED unfulfilled and
  now fulfilled.** The messages are quoted in the ledger's Task 2 verification
  section.
