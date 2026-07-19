---
description: Triage the latest parallax drift-watch report and repair what broke
---

Triage the newest drift-watch report produced by `tools/check-drift.ps1`
(the weekly "parallax drift watch" toast points here).

## Locate the report

The reports live in the CHECKOUT the scheduled task runs from, not the
plugin cache. Resolve it:

```powershell
schtasks /Query /TN "parallax drift watch" /V /FO LIST
```

The "Task To Run" line contains the absolute path to `check-drift.ps1`;
reports are in `drift-reports\` next to it (newest file by name). If the
task does not exist, ask the user where the parallax checkout lives.

**Check `drift-pending.json` (next to check-drift.ps1) FIRST.** If it
exists, earlier runs are still unresolved — it is a LIST of entries, each
naming its report and status (`manual-triage-needed`, `fix-branch-open`
with the branch awaiting review/merge, or
`critical-dismissal-needs-verification` — a CRITICAL finding the headless
triage dismissed that still needs human eyes). Triage EACH entry (the
newest report may be a later clean week). Resolve entries individually:
rewrite the file without the resolved ones, and delete it when none
remain.

Otherwise read the newest report. If it says "No findings.", report that
and stop.

## Triage each finding

Work in the parallax checkout, on a feature branch (repo rule: behavior
changes never go directly on main). For each finding class:

**`[CRITICAL] fingerprint literal ... gone` (superpowers template)**
The diff-gate hook is inert right now. Read the INSTALLED superpowers
template (path is in the finding), find what the code-reviewer dispatch
prompt now says, then: update the fingerprint literals and the
`**Base:**`/`**Head:**` extraction regexes in
`hooks/superpowers-review-companion.ps1`; re-pin the fixture (copy the
installed template into `evals/multi-model-verify/fixtures/`, add the
attribution comment header, name it for the new version); update the pinned
paths in the tests and `tools/check-drift.ps1`; run the full pytest suite.

**`[WARN] ... no longer matches the pinned fixture` (fingerprints intact)**
The hook probably still fires. Diff the installed template against the
fixture, confirm the `Base:`/`Head:` lines still match the extraction
regexes in the hook script (run the hook e2e tests), then re-pin the
fixture as above.

**`[WARN] Claude Code X -> Y changelog mentions ...`**
Evaluate each quoted changelog line against parallax's four exposure
surfaces: the hook matcher and hook JSON schema (`hooks/hooks.json`), the
plugin cache/install layout (dev loop in README), Skill loading, and the
behavioral runner's `claude -p` / `--allowedTools` invocation
(`evals/tools/run_behavioral_evals.py`). Most lines are irrelevant on
inspection — say so per line. For any line that touches a surface, verify
against the live install (run the pytest suite; run a behavioral case if
the runner surface is implicated) and fix what actually broke.

**`[CRITICAL] codex exec ...` (transport)**
Run `codex exec --help` and `codex exec resume --help` yourself and read
what changed. Update the transport commands in
`skills/multi-model-verify/SKILL.md` and
`skills/multi-model-verify/references/model-prompting-notes.md`, keep the
structural transport pins
in the tests in sync, and live-probe one round-trip
(`codex exec --sandbox read-only -m <canonical model id from
model-prompting-notes.md> ...`) before declaring it fixed — including the
effective-route check: the probe's startup header must echo the canonical
model/provider/effort (model-prompting-notes.md documents the check).

**`[CRITICAL] claude/codex --version failed` or registry/fixture missing**
Environment breakage, not drift: diagnose locally (PATH, reinstall,
moved checkout) and fix the machine, not the repo.

## Finish

Per the repo's standing rules: run all gates, get the cross-vendor
review of the diff, then adjudicate it yourself — verify each finding
against the repo before acting; the reviewer's verdict is input, not the
decision (debate-protocol.md, Final adjudication). Then merge and push,
bump the plugin version, and
`claude plugin update parallax@parallax`. Remind the user to restart
sessions if hooks/ or skills/ changed. If a finding needs no code change,
record the disposition in your reply — the report file stays as the
archive.
