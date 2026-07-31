<task>Round 2. The plan was revised against your round-1 findings. Re-read
docs/superpowers/plans/2026-07-31-kimi-code-swap.md — it was rewritten whole —
and judge the revision. Evidence rules, verdict grammar and boundaries as
before.</task>

<what-changed>
Accepted and fixed:
- Claim 1/2 freshness. New region `round-freshness-boundary` in Task 6 Step 4:
  capture wire line count and log byte length before every call, read only
  past both, fresh calls require a non-existent session dir, and a file
  shorter than its offset fails as truncation rather than being re-read from
  zero. Task 5's test list includes the stale case explicitly.
- Claim 2 validator. New Task 5 builds tools/read-kimi-round-evidence.ps1 with
  hand-normalized fixtures and fourteen enumerated failure cases.
- Claim 2 diagnostic overclaim. Task 6 Step 4 now states the narrow guarantee
  instead of "a failed allowlist yields a different set".
- Claim 3 region. `evidence-hash-continuity` is now a marked region.
- Claim 4 canonicalization. UTF-8, CRLF to LF, over the concatenation of every
  turn.prompt input[] text field. Oversized-brief fallback stated.
- Claim 5 subagents negative branch, Task 4 Step 4. Denylist claim narrowed.
- Claim 6 per-DEBATE naming, and Task 3 Step 4 probes for a thinking-enabled
  differentiator or records that none exists.
- Claim 7 credentials. Task 2 refuses an existing destination, refuses any
  path inside a git work tree, sets an owner-only ACL before the copy, and
  ships Remove-KimiLaneHome.
- Claim 8 partial: Task 3 Step 5 probes which flags a resume accepts and
  Task 6 re-pins those; `resume-inheritance` is stated as version-bound.
- Claim 10: the cp1252 probe is now Task 3 Step 6, before Task 6 rewrites
  Transport. Task 8 states both branches.
- Claim 11: `-r` replaced by `--session` in the help assertion; the builder's
  -Model is mandatory with no literal; state-machine stubs scheduled in Task 1;
  `git add -u` and `grep` removed; Task 2 and 3 reordered so the home exists
  before the probes; canonical provider and effort declared in Task 9 Step 1;
  fallbacks.md rewrite specified in Task 9 Step 3 including the pin at
  test_backup_lane.py:546.

Declined, with reasons in the plan:
- Binding toolsHash to a supported client version. Replaced by recording both
  hashes in the debate record so an upgrade's change is visible without a
  literal that fails for non-route reasons.
- A sacrificial resume write-probe every debate. Replaced by re-pinning every
  resume-accepted flag plus the version floor.

Found by us, not by you: CronList was in neither list, so one built-in tool
was neither allowed nor denied. Fixed in Task 4 Step 2 with a coverage test.
</what-changed>

<claims>
1. The `round-freshness-boundary` region fully restores what deleting the
   offset rule removed, with no remaining path by which a later round's checks
   can be satisfied by an earlier round's records.

2. Task 5's enumerated failure cases are sufficient. Name any failure mode of
   the evidence rule that no listed test would catch.

3. The two declined fixes are correctly declined, and their replacements are
   adequate.

4. The revision introduced no NEW defect. This repo's recurring failure is that
   a fix carries the next round's defect — five rounds running in one prior
   cycle. Attack the new material specifically: the ACL and git-work-tree
   refusal in Task 2, the TryParse floor logic in Task 1, the state-machine
   stub edits in Task 1 Step 5, and the validator's rule ordering in Task 5
   Step 4.

5. The plan is now executable by an engineer with no repository context.
</claims>

<final-check>
List anything you could not verify against files you read this session, as
UNVERIFIED.
</final-check>
