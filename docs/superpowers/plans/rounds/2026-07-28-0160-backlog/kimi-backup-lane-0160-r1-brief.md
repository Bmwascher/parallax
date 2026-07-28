# Review brief — parallax 0.16.0, whole branch

You are the cross-vendor reviewer for this change. Mode: **diff**. You are an
independent lane: no other reviewer's findings are given to you, on purpose.
Review what is in front of you.

## What this repository is

`parallax` is a Claude Code plugin that runs cross-model verification: a
driving session debates a reviewer from a different vendor over a change,
round by round, until the reviewer says PASS or the session adjudicates a
disagreement. The repo also holds the eval harness that pins the plugin's own
contracts. It is developer tooling, not an application.

## What you are reviewing

Branch `0.16.0-backlog`, range `c6b7c85..7ddb871`, unmerged.

- `0160-commits.txt` — the commit list and the diffstat.
- `0160-diff.txt` — the complete diff with ten lines of context.

Both files are in this workspace, along with a full copy of the repository at
the branch tip, so you can read any file the diff touches in its final state.
You have read-only tools by design: ReadFile, Glob, Grep, ReadMediaFile,
SetTodoList. There is no shell, so you cannot run the tests.

## What the branch does

Four items from a backlog, plus the fixes from four rounds of cross-vendor
review that followed.

1. **`tools/verify-attestation.ps1`** — a rejection message now names the
   field that failed instead of saying only that verification failed.
2. **`tools/check-drift.ps1`** — a weekly watchdog. It could report three
   different situations with one message; they are now separated: the runner
   broke, the triage agent deliberately stopped on a clean exit, or the user
   disabled auto-triage. It also no longer passes an invalid tool-permission
   rule to the agent it dispatches.
3. **`skills/multi-model-verify/references/backup-lane.md`** — the live
   contract for the backup reviewer lane. Two changes: route evidence is now
   attributed by session block rather than by position in a shared log, and a
   new lane lock serializes this plugin's own dispatches.
4. **`tools/kimi-lane-lock.ps1`** — new. An advisory, age-bounded file lock.
   The label in the lock file is the ownership credential; a release must
   present the same label or `-Force`. Its whole test suite is
   `evals/multi-model-verify/test_kimi_lane_lock.py`.

## The contract-coverage mechanism, which you need in order to read the tests

Shipped one version earlier and enforced by
`evals/multi-model-verify/test_contract_coverage.py`. Text inside
`<!-- contract:start id=... -->` / `<!-- contract:end -->` markers in the
skill's Markdown is COVERED only when one string literal inside a Python test
assertion contains the whole region body. One region, one pin. A pin whose
failure is deliberately caught proves nothing and does not count. The
inventory `DECLARED_REGIONS` in that file must list every region, so deleting
one is visible. `CLAUDE.md` in this workspace states the full rule.

## What to attack

- **Correctness of the lock.** Ownership, staleness, and the age routine.
  Assume an attacker who can write the lock file by hand and who wants to
  free a lane another debate is holding, or to hold a lane forever.
- **The three-state classification in `check-drift.ps1`.** Is there a path
  where two states are reported at once, or where a real failure reports as
  something benign, or where a benign outcome reports as a failure?
- **The evidence rules in `backup-lane.md`.** They describe how a driver
  proves which model answered, reading a log shared with every other kimi
  session on the machine. Does the rule as written actually attribute the
  lines it claims to attribute?
- **Test quality.** A test that would pass against the defect it names is
  worse than no test. Say so when you find one.
- **Any claim in the changed documents that the changed code does not
  deliver.** The record files under `docs/superpowers/plans/` are part of the
  diff and are in scope.

## Rules for your reply

- **Cite everything** as `path:line`. A claim with no citation is struck
  without debate rather than argued about, so an uncited finding is worse
  than an omitted one.
- **Do not report what you cannot see.** You cannot run the tests. If a
  claim depends on runtime behaviour, say `UNVERIFIED` and exclude it from
  your verdict rather than assuming either way.
- Order findings by severity. For each: what is wrong, where, why it
  matters, and what would fix it.
- Separate a real defect from a preference. Say which you are reporting.
- **Verdict grammar.** End with exactly one of `Overall verdict: **PASS**`
  or `Overall verdict: **FIX**`. PASS means you found nothing that must
  change before merge. Do not manufacture an objection to justify the round;
  if it holds, say PASS plainly and say it first.
