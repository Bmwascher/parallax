---
description: Operational health check for the crosscheck plugin - versions, hook, fingerprint, transport, drift state
---

Run the crosscheck operational checks below and present ONE table:
check | state | verdict (OK / STALE / BROKEN) | fix. End with a one-line
overall summary. Report only - fix nothing without being asked.

## 1. Checkout vs installed version

Read `.claude-plugin/plugin.json` `version` in the checkout (locate it via
the marketplace entry in `~/.claude/plugins/installed_plugins.json` -
crosscheck's marketplace points at the local working copy - or ask if
unresolvable). Compare against the installed entry's `version` in
`installed_plugins.json`. Mismatch = STALE: the dev loop is bump ->
`claude plugin update crosscheck@crosscheck` -> restart.

## 2. Hook registration and matcher

Read the INSTALLED copy's `hooks/hooks.json`. Verify both `PostToolUse`
and `PostToolUseFailure` are registered and their matchers match the tool
name `Agent` (regex-match the literal string). A bare `Task` matcher is
BROKEN (tool renamed in Claude Code 2.1.63).

## 3. Superpowers fingerprint

From `installed_plugins.json`, find superpowers' installPath and read
`skills/requesting-code-review/code-reviewer.md`. Both literals "Senior
Code Reviewer" and "Git Range to Review" present = OK; one = BROKEN (hook
warns but cannot extract); none = BROKEN (diff gate inert). Also confirm
`**Base:**`/`**Head:**` placeholders still appear.

## 4. codex transport

`codex --version`, then `codex login status`. If both succeed, run the
cheapest possible round-trip probe and report its outcome:

```powershell
"Reply with exactly: TRANSPORT-OK" | codex exec --sandbox read-only -m gpt-5.6-sol -c model_reasoning_effort=low --output-last-message "$env:TEMP\crosscheck-doctor.txt" -
```

(Model id must match the canonical id in
`skills/multi-model-verify/references/model-prompting-notes.md` - if they
differ, that is itself a BROKEN finding.)

## 5. Drift watch

`schtasks /Query /TN "crosscheck drift watch" /V /FO LIST` - task exists,
next run time sane, and the "Task To Run" path points at an existing
`check-drift.ps1`. Then check `tools\drift-pending.json` next to it:
entries present = list each (status, stamp) and point at
/crosscheck:drift-triage.

## 6. Behavioral eval target

Note (informational): `evals/tools/run_behavioral_evals.py` tests the
INSTALLED plugin by default; `--head` tests the checkout via --plugin-dir.
If check 1 found a version mismatch, any recent behavioral results tested
the stale cache - flag that explicitly.
