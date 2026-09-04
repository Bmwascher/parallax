# Fable whole-branch review, range 0ecc7c79f1e01a3933edfa0fe3b095ae8a304cbc..196f3e53c18cf04e909974fe76d5f4cb93ea6ba1

Seat: parallax:fable-reviewer (model pin `fable`, tools Read/Grep/Glob), Claude Code 2.1.258, dispatched 2026-09-04 with the frozen plan path, the SDD ledger path and the controller-built package `review-0ecc7c7..196f3e5.diff`. Raw reply follows verbatim.

---

### Strengths

- The hook entry point is the strongest piece on the branch. `C:\Users\Brandon\Documents\parallax\tools\backlog-hooks\run-hook.ps1:7-15` records the measured reason the script must not touch stdin (both `[Console]::In.ReadToEnd()` and a `StreamReader` returned empty under `-File` on both hosts; `$input` re-decodes through the console code page), and `:18` initialises `$code = 1` so a python that never launches cannot exit 0. `_common.py:34` reads `sys.stdin.buffer` and decodes UTF-8 itself, so the payload path has no host-dependent encoding step.
- The test that would have caught the 5.1 defect on day one now exists: `C:\Users\Brandon\Documents\parallax\evals\multi-model-verify\test_backlog_hooks.py:104` asserts the `s1.json` baseline exists after `start()`, with a comment naming the accidental-pass shape, and `:126` (`test_payload_reaches_python`) proves the payload was parsed by round-tripping a distinctive `cwd`, not by checking a default fired.
- The Stop hook's untracked sweep is scoped correctly. `_common.py:65` records governed untracked paths at SessionStart, `stop.py:36-38` subtracts them, and both directions are tested (`test_backlog_hooks.py:224` pre-existing file does not block, `:236` a file added after start still blocks).
- The lint honours every Global Constraint I could check from the package: stdlib only; exit 0/1/2 as specified (`backlog_lint.py:490-497`, `:503-509`); rule 7 takes no git input (`:206-227`); every failure printed (`:481-486`); the governed list is the spec's verbatim (`:54-56`); the Stop refusal text is the spec's verbatim (`stop.py:12-14`, matched by `test_backlog_hooks.py:204-207`).
- Rule 3 and rule 12 no longer double-report a stray line (`backlog_lint.py:327-338` with the docstring saying which rule owns it; test at `test_backlog_lint.py:425`). The rule 1 missing-Status message is now "missing field Status" rather than an order failure (`:345-351`, `TestRule1Messages` at `:323-337`).
- The widening of the re-attestation predicate is documented in three places that agree: the module docstring (`backlog_lint.py:24-27`), the `reattested_items` docstring (`:556-570`), and tests that pin both the positive case and the DONE-in-both-texts negative case (`test_backlog_lint.py:531-546`).
- The pre-push clause is fail-closed on a missing interpreter (`.githooks/pre-push:45-48`), captures the range output whole (`:53`), and is proven under merge, squash and fast-forward with and without a re-attestation (`test_backlog_prepush.py:109-123`). CI runs the same `--range` mode with `fetch-depth: 0` (`.github/workflows/skill-evals.yml:23`, `:64-75`), and the workflow's `on:` block (`:7-9`) triggers on both `push` and `pull_request`, so the `pull_request` branch of tier 2d is live, not dead.
- `BACKLOG.md` is pure ASCII (a sweep for any byte above 0x7F found none), so the Windows stdout code-page trap cannot bite any hook that prints lint output. The banned-narrative and "Ranked second" sweep across the new file found nothing. The pointer file names the correct last-full-text commit `d19a5ca` (the commit before `4d330a1`) and the inventory path (`docs/superpowers/plans/2026-07-27-0150-backlog.md:1-3`).
- The second-reader record is a real second read: it restored seven losses in six items and lists what it deliberately did not restore with a reason each (`docs/superpowers/plans/rounds/2026-09-04-backlog-rewrite/second-reader.md:141-158`, `:160-214`).

### Issues

#### Critical

None.

#### Important

None.

#### Minor

1. `C:\Users\Brandon\Documents\parallax\BACKLOG.md:946-967` (item 32). The DONE block names the items its close opened (71, 72, 73, a second instance for 59, a live instance for 69) but the residual the second reader flagged, an interrupted launch that leaves NO RECEIPT (narrowed, not eliminated), is now carried by no item; a sweep of the new file for "receipt" in that sense finds nothing. The spec's Problem section names "findings with no owning item" as one of the defects the rewrite exists to remove, and this is a fresh instance of that class created by the rewrite itself. One sentence in item 72 (the receipt item) or a new item closes it.

2. `C:\Users\Brandon\Documents\parallax\evals\tools\backlog_lint.py:613-614` and `.githooks/pre-push:8-11`. The failure message still reads "no OPEN or PARTIAL item was re-attested" and the hook header still describes the predicate in the spec's original words, while `reattested_items` now also accepts a close. The Stop refusal is spec-verbatim and must stay; the range message and the pre-push header are free text and should name the close form, so a reader of a refusal learns the cheaper escape exists.

3. `C:\Users\Brandon\Documents\parallax\tools\backlog-hooks\session_start.py:15` (`head.strip()`) and `backlog_lint.py:601` (`parent.strip()`). Both consume a `git rev-parse` line as exactly one line without `accept_exactly_one_nonempty_line()`. Global Constraint 4 says any such parser goes through the helper. Tier 1c passed because these are not the discard-blank-lines idiom it sweeps for; the constraint is broader than the sweep. No wrong behaviour today (`rev-parse` cannot emit two lines), so this is conformance, not correctness.

4. `C:\Users\Brandon\Documents\parallax\docs\superpowers\plans\rounds\2026-09-04-backlog-rewrite\second-reader.md:117` cites `task-10-brief.md` and `citation-inventory-check.txt:2` cites `task-9-report.md`. Neither file is in the tree (the round directory holds four files). Retained records that cite unretained inputs are the record-drift class this repo keeps measuring; either retain the two briefs beside the records or reword the citations to say the inputs were ephemeral.

5. `C:\Users\Brandon\Documents\parallax\docs\superpowers\plans\rounds\2026-09-04-backlog-rewrite\citation-inventory.md:465`. The Totals paragraph says most `unresolved` rows are citations "whose content a careful reading likely does support". That is an unmeasured claim inside a record whose header promises "nothing is guessed". Strike the clause or measure a sample.

6. `C:\Users\Brandon\Documents\parallax\tools\backlog-hooks\_common.py:44-48`. The baseline directory under `<tempdir>/parallax-backlog-baselines` gains one JSON file per session and nothing removes them. Harmless for a long time, but unbounded.

7. `C:\Users\Brandon\Documents\parallax\tools\backlog-hooks\stop.py:35`. `git diff --name-only <baseline head>` attributes to THIS session any governed change the working tree acquired by a `pull`, `merge` or `rebase` during the session. That is a known approximation of "what this session did" and is not stated anywhere. One sentence in the docstring.

### Ledger minors triage

- Task 1, missing-Status message reads as an order failure: FIXED on the range (`backlog_lint.py:345-351`, pinned at `test_backlog_lint.py:323-337`). Nothing owed.
- Task 3, rule 12 counts a bare dash as a word: ride. Every shipped header was sized for it (First and Fourth are exactly 8 including the dash) and the rule is the spec's own eight-word shape.
- Task 8, CLAUDE.md verification sentence: FIXED (`CLAUDE.md:16-18` now reads "tiers 1, 1b, 1c, 2, 2b and 2c ... tier 2d runs the same governed-range test as the pre-push hook"). Nothing owed.
- Task 9, 74 of 446 citations resolved under a strict mechanical bar: ride. The spec asks that nothing be guessed, and under-claiming satisfies that; a paraphrase pass is not owed. The one thing owed is Minor 5, the speculative clause in the Totals paragraph.
- Task 10, record policy uneven for items 8 and 16: ride. Both `Record:` values resolve and neither old item named a record, so nothing is contradicted; if a policy sentence is ever wanted it belongs in the preamble, and the spec does not require one.
- Task 10, item 47b Cost line is a fragment: FIXED (`BACKLOG.md:1663` now has a subject and states a cost). Nothing owed.
- Task 11, DONE blocks for 9, 24, 65 drop detail: ride. Spec 1c says closed items keep only a resolution block and the full text stays in git history at the old path, which the preamble names.
- Task 11, item 32 drops its unowned residual: fix before merge (Minor 1). It is the one deferred loss that is a residual open concern rather than closed history.
- Task 11, item 14 `Closed: record` with a merge commit: ride. `CLOSED_RE` admits only a version, `record` or `superseded`, and the old heading named no version, so `record` is the only legal value; the second reader's note already records the mismatch.
- Ruling, build on a branch not a worktree: ride; no consequence on the range.
- Ruling, the 5.1 stdin defect is a build defect: concur. The plan's Task 5 Step 4 said the failing host names the defect and forbade weakening the test; the fix wave did exactly that and added the delivery proof.
- Ruling, a close counts as a re-attestation: concur, recorded for the debate as a spec amendment. Without it a wave whose only backlog change is a close could not pass, which would push sessions to touch an unrelated open item to satisfy the gate, a worse outcome than the widening. Minor 2 is the loose end.
- Ruling, repo-relative `-File` path parked: concur. One correction to the ruling's own wording: a wrong cwd is not a silent off. `pwsh -File` on a missing path exits non-zero, and Claude Code surfaces a non-zero, non-2 hook exit as a visible error, so the failure is loud in the session even though it is not blocking.
- Ruling, PostToolUse spawns pwsh and python per Edit/Write: ride; `post_tool_use.py:13-14` returns before loading the lint for any file that is not `BACKLOG.md`.

### Assessment

Ready to merge: With fixes

No Critical or Important finding on the range; the three defects the build's own review found are verified fixed and tested on both hosts. The one fix I would take before merge is Minor 1 (item 32's unowned residual, one sentence), because it recreates the exact defect class the spec names as the reason for the rewrite; the other Minors can ride or go into the debate as the reviewers see fit.
