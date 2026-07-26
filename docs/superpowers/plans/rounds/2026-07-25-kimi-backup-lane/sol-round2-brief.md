# Mode plan, round 2 — fix wave applied; re-review requested

Evidence rules and verdict grammar as before. The candidate is amended
at commit 4ab3c83 (your working tree). Position changes since round 1:

ACCEPTED — all seven of your findings, applied:
1. Banner: the fenced block now carries a conditional-offer line
   ("Backup lane: offered when a class below qualifies it; on request
   otherwise — preserves cross-vendor independence; does NOT verify
   reviewer reasoning effort (config-only)") ahead of the amended
   Options line, both test-pinned (plan Task 4 Step 2, Task 1
   test_fallbacks_backup_wiring).
2. Dispatch routing: new Task 5 Step 3b inserts the identical pointer
   sentence into BOTH mode sections at named physical-line anchors; the
   Task 1 pin counts exactly two occurrences.
3. Test false negatives: the resume pin now asserts the COMPLETE
   resumed command through --thinking; the allowlist test regex-parses
   the yaml tools list and asserts LIST equality to ALLOWLIST; a new
   test_backup_files_no_backslash_paths covers all three new artifacts.
4. Task 6 is fully rewritten with exact code: the doctor check as a
   `## 8.` heading with installPath resolution and BROKEN/N/A grammar;
   exact check-drift.ps1 insertions (version probe, carry-forward,
   snapshot field, check-2b flag+vocabulary probes with a no-cascade
   skip note); exact harness edits (DRIFT_REAL_PYTHON capture,
   kimi.cmd + forwarding python.cmd stubs, Set-SnapshotWithKimi,
   three scenarios: flag-drift, vocab-drift, version-carry — each with
   Assert-True conditions and exact match strings).
5. SKILL anchors re-pinned as COMPLETE physical-line blocks (the full
   seven-line Overview paragraph; the full four-line Preflight item).
6. Doctor row resolves under installPath (folded into 4).
7. Task 1 Step 3 RED command now runs both test files.

Blind relay from the second reviewer lane (its five findings, all
session-verified and accepted, folded in the same wave): the spec §8
dispatch-pointer requirement was dropped from Task 5 (= your finding
2); the README "What's in the box" anchor named a nonexistent
fallbacks row and supplied non-table text (= your finding 5, README
part; fixed as a table row after the `skills/multi-model-verify/` row);
the doctor row's installPath violation (= your finding 6); the doctor
heading/verdict-grammar deviation (`## 8.` + BROKEN/N/A — folded);
the spec §5 system-prompt fallback branch was missing from Task 8
(one sentence added to Task 8 Step 4 item 2). Its pin-integrity sweep
of every Task 1 pin against the shipped blocks found zero line-join
defects.

Re-review the amended candidate at 4ab3c83. End with a verdict:
PASS / FIX (specific) / ESCALATE.
