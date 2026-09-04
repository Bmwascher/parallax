# Backlog rewrite plan: Fable single-round review, 2026-09-04

Subject: `docs/superpowers/plans/2026-09-04-backlog-rewrite.md` at
`e5a59e3`. One round, by the user's instruction; no resume.

Seat and identity evidence: `dispatch-r1.md` beside this file (dispatch
metadata: `parallax:fable-panel-reviewer`, model pin `fable`, harness
2.1.257 above the 2.1.216 floor, fresh background agent). The brief is
`brief-fable-r1.md`, the reply `reply-fable-r1.md`.

Result: FIX on 5 of 8 claims, PASS on 3. Session disposition, all
accepted on evidence, none contested, applied to the plan in the commit
that retains this record:

- A: hook commands now run `tools/backlog-hooks/run-hook.ps1` with
  `-File`; it prints a note and exits 0 on a missing python, and a test
  per host strips python from PATH to prove it.
- 4: the hook tests build argv from the same shape the settings file
  carries, and Task 6 asserts the settings command splits to exactly
  that argv, so the tests exercise what ships.
- C: the rule-1 early-return message names the order.
- D: Task 1's field assertion checks the Verified field by name and
  shape, so Task 2's digest refresh cannot break it.
- E: the hook test's seed repo commits a `.gitignore` for `__pycache__/`.
- F: item 11 is ranked in the Last group with an uncosted Cost line; a
  decision the plan makes and records.
- G: Task 9's grep uses the bare path with `-H`, classifies every hit,
  and covers the probe plan's SECOND citation shape at its line 158
  (`:577`, `:11-14`), which the spec's two-citation inventory missed.
  Verified by the session: the probe plan names the old path on six
  lines (78, 158, 288, 856, 892, 975); three carry line citations.
- Also-found items applied: `-H`, the seed push pins today, and the
  workflow comment on hook tests is extended.
- UNVERIFIED by the seat and left so: which stream a Stop hook's exit 2
  surfaces. The Stop script now prints its reason to BOTH stdout and
  stderr, so the answer does not matter to the hook.

Spec finding to carry into the branch record: spec 1e states the frozen
plan carries two line citations; it carries three, in two shapes. The
plan handles all three and the spec is not edited (it is frozen); the
diff debate should see this note.
