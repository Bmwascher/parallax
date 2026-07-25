---
description: Operational health check for the parallax plugin - versions, hook, fingerprint, transport, drift state
---

Run the parallax operational checks below and present ONE table:
check | state | verdict (OK / STALE / BROKEN / N/A) | fix. N/A marks a
check that cannot apply here or an experimental surface that did not
answer; an N/A verdict never contributes to overall failure. End with a
one-line overall summary. Report only - fix nothing without being asked.

## 1. Checkout vs installed version

Two different files, and mixing them up is the whole point of this check:

- CHECKOUT: `~/.claude/plugins/known_marketplaces.json` -> the `parallax`
  marketplace's source. A LOCAL DIRECTORY source has a `source.path`; read
  `.claude-plugin/plugin.json` `version` there. A GITHUB source (the
  README's stable install, `Bmwascher/parallax`) has NO local checkout —
  that is not breakage: report this check as `N/A (GitHub install — the
  installed version is authoritative)` and skip the comparison.
- INSTALLED: `~/.claude/plugins/installed_plugins.json` -> the
  `parallax@parallax` entry's `version` (its `installPath` is the
  VERSIONED CACHE COPY, never the checkout).

Mismatch (directory source only) = STALE, and everything running right now
is the cached version: the dev loop is bump ->
`claude plugin update parallax@parallax` -> restart the session.

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

First sanitize the probe shell — clear `CODEX_API_KEY`, `OPENAI_API_KEY`,
`OPENAI_BASE_URL`, and `CODEX_HOME` (`Remove-Item Env:<name>`) so the
preflight and the probe below see the SAME environment the review lane
uses. Then
`codex --version`, then `codex login status`. The login check must report
the first-party auth STATE — output matching `Logged in using ChatGPT` —
not merely exit 0 (an API-key login also exits 0 but rides different
billing; report that as BROKEN with the actual output). If both pass, run
the cheapest possible round-trip probe. The probe writes to a FRESH unique
output file (the `Get-Random` name below), so a stale `TRANSPORT-OK` from
an earlier run can never read as a pass over a failed probe.

Read the canonical model id from the INSTALLED copy's
`skills/multi-model-verify/references/model-prompting-notes.md` — resolve
it under the `installPath` from check 1, exactly like checks 2 and 3 (a
bare relative path only works when the current directory happens to be the
plugin checkout). The `Canonical model id` declaration is the ONE place
the reviewer model is defined; use it as `<id>` below. A missing
declaration is itself a BROKEN finding. Effort `low` is deliberate — this
is a reachability check, not a review.

```powershell
$probe = "$env:TEMP\parallax-doctor-$(Get-Random).txt"
$hdr = "$env:TEMP\parallax-doctor-hdr-$(Get-Random).txt"
"Reply with exactly: TRANSPORT-OK" | codex exec --sandbox read-only -m <id> -c model_reasoning_effort=low --output-last-message $probe - > $hdr 2>&1
# OK requires ALL of: exit 0; $probe contains exactly TRANSPORT-OK; and the
# captured header ($hdr) echoes the EFFECTIVE ROUTE - first `model: ` line
# equals <id>, first `provider: ` line `openai`, first `reasoning effort: `
# line `low` (the probe pins low), first `sandbox: ` line `read-only` (the
# probe pins it; sandbox mode has no cross-resume continuity, so a default
# bleeding through here would also bleed into review resumes). codex
# prints the RESOLVED config there, so a config.toml override or profile
# silently swapping the reviewer surfaces as a mismatch = BROKEN (report
# header value vs canonical).
```

OK requires the zero exit, fresh `TRANSPORT-OK` content, AND the header
match; anything else is BROKEN. The header is client-resolved metadata —
report it as `effective route confirmed`, never "used and confirmed".

## 4b. codex quota headroom (best effort, experimental)

Same sanitized shell as check 4. `codex app-server --stdio` answers the
JSON-RPC method `account/rateLimits/read` locally (probed 2026-07-24;
experimental capability — drift is expected and is exactly what N/A is
for). Hold stdin OPEN — the server exits when it closes.

```powershell
python -c "import json,shutil,subprocess,threading;bin=shutil.which('codex');p=subprocess.Popen([bin,'app-server','--stdio'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);r={};t=threading.Thread(target=lambda:[r.update(m=l) for l in p.stdout if 'rateLimits' in l],daemon=True);t.start();p.stdin.write(json.dumps({'id':1,'method':'initialize','params':{'clientInfo':{'name':'parallax-doctor','version':'0'},'capabilities':{'experimentalApi':True}}})+'\n'+json.dumps({'id':2,'method':'account/rateLimits/read','params':None})+'\n');p.stdin.flush();t.join(timeout=10);p.kill();print(r.get('m','NO-ANSWER'))"
```

Answer received: report `usedPercent`, `windowDurationMins` (as days/hours),
`resetsAt` (as local time), and `planType` in the state column — verdict
OK. `NO-ANSWER`, a spawn error, or malformed JSON: verdict
`N/A (experimental surface unavailable)` — NEVER BROKEN from this row
alone, and never retry in a loop. This row reads account state only; it
sends no review traffic and must not replace check 4's transport probe.

## 5. Drift watch

`schtasks /Query /TN "parallax drift watch" /V /FO LIST` - task exists,
next run time sane, and the "Task To Run" path points at an existing
`check-drift.ps1`. A legacy `crosscheck drift watch` task still present
(pre-rename installs) is STALE - the fix is re-running
`tools/check-drift.ps1 -Register`, which migrates it. Then check
`tools\drift-pending.json` next to it:
entries present = list each (status, stamp) and point at
/parallax:drift-triage.

Also read `tools\drift-snapshot.json` next to that `check-drift.ps1`: if
its `codex` field differs from the live `codex --version` from check 4,
note it (STALE, informational) — the codex CLI changed since the last
weekly run, so the transport flag surface was last probed against the OLD
version; the next drift run re-probes it.

## 6. Behavioral eval target

Note (informational): `evals/tools/run_behavioral_evals.py` tests the
INSTALLED plugin by default; `--head` tests the checkout via `--plugin-dir`.
If check 1 found a version mismatch, say so here: any behavioral run made
WITHOUT `--head` tested the stale cache, not the checkout. A `--head` run is
unaffected by the mismatch.

## 7. agy transport (Flash implementer lane)

Resolve the INSTALLED copy's `agents/flash-implementer.md` under the
`installPath` from check 1 and parse the canonical model literal from its
Lane note (the pinned model-ID token declared there) — the agent file is the ONE
place the implementer model is defined; carry no literal here. A missing
declaration is itself BROKEN. Then:

- `& "$env:LOCALAPPDATA\agy\bin\agy.exe" --version` — missing binary =
  BROKEN (the Flash lane cannot dispatch), report the install one-liner.
- `agy models` — output must contain the parsed literal. Sign-out or a
  missing model = BROKEN with the actual output. No generation probe —
  this is a reachability check, and agy free-tier quota is opaque.

Report the route language as declared in the agent file: evidence is
client-side, requested and propagated only.
