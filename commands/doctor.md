---
description: Operational health check for the crosscheck plugin - versions, hook, fingerprint, transport, drift state
---

Run the crosscheck operational checks below and present ONE table:
check | state | verdict (OK / STALE / BROKEN) | fix. End with a one-line
overall summary. Report only - fix nothing without being asked.

## 1. Checkout vs installed version

Two different files, and mixing them up is the whole point of this check:

- CHECKOUT: `~/.claude/plugins/known_marketplaces.json` -> the `crosscheck`
  marketplace's source. A LOCAL DIRECTORY source has a `source.path`; read
  `.claude-plugin/plugin.json` `version` there. A GITHUB source (the
  README's stable install, `Bmwascher/crosscheck`) has NO local checkout —
  that is not breakage: report this check as `N/A (GitHub install — the
  installed version is authoritative)` and skip the comparison.
- INSTALLED: `~/.claude/plugins/installed_plugins.json` -> the
  `crosscheck@crosscheck` entry's `version` (its `installPath` is the
  VERSIONED CACHE COPY, never the checkout).

Mismatch (directory source only) = STALE, and everything running right now
is the cached version: the dev loop is bump ->
`claude plugin update crosscheck@crosscheck` -> restart the session.

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
cheapest possible round-trip probe. The probe writes to a FRESH unique
output file (the `Get-Random` name below), so a stale `TRANSPORT-OK` from
an earlier run can never read as a pass over a failed probe.

Read the canonical model id from
`skills/multi-model-verify/references/model-prompting-notes.md` (the
`Canonical model id` declaration — the ONE place the reviewer model is
defined) and use it as `<id>` below. A missing declaration is itself a
BROKEN finding. Effort `low` is deliberate — this is a reachability check,
not a review.

```powershell
$probe = "$env:TEMP\crosscheck-doctor-$(Get-Random).txt"
"Reply with exactly: TRANSPORT-OK" | codex exec --sandbox read-only -m <id> -c model_reasoning_effort=low --output-last-message $probe -
# OK only if the command exited 0 AND $probe now contains exactly TRANSPORT-OK
```

OK requires BOTH a zero exit and fresh `TRANSPORT-OK` content; anything else
is BROKEN.

## 5. Drift watch

`schtasks /Query /TN "crosscheck drift watch" /V /FO LIST` - task exists,
next run time sane, and the "Task To Run" path points at an existing
`check-drift.ps1`. Then check `tools\drift-pending.json` next to it:
entries present = list each (status, stamp) and point at
/crosscheck:drift-triage.

## 6. Behavioral eval target

Note (informational): `evals/tools/run_behavioral_evals.py` tests the
INSTALLED plugin by default; `--head` tests the checkout via `--plugin-dir`.
If check 1 found a version mismatch, say so here: any behavioral run made
WITHOUT `--head` tested the stale cache, not the checkout. A `--head` run is
unaffected by the mismatch.
