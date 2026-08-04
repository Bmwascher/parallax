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

## 8. Backup reviewer transport (kimi-code)

Four measurements roll into ONE row, and none of them dispatches a
review or touches a credential value. The lane home is
`$env:USERPROFILE\.parallax-kimi-review`; the lane credential is
`<lane-home>\credentials\kimi-code.json`.

**Aggregate verdict, a TOTAL order.** Binary absent short-circuits the
whole row to N/A before the credential or lock checks run. Otherwise the
row is the WORST substate observed, by `BROKEN > STALE > N/A > OK`, and
every substate observed is still named in the detail text. N/A is IN
that order — it is a real row verdict (see the header note above) that
never contributes to overall failure, and without it a valid binary plus
an absent credential plus a free lock would have no defined row.

- **Binary and floor.** Run `~/.kimi-code/bin/kimi.exe --version` — the
  client's ABSOLUTE path, never a bare `kimi` resolved from PATH (the
  superseded client can still be installed alongside it). Missing binary
  is N/A, short-circuit, "backup lane unavailable, primary unaffected"
  — the fix pointer is references/backup-lane.md. A present binary that
  reports a usable version AT OR ABOVE the floor `0.31.1` is OK, with the
  reported version and the floor comparison both named in the detail —
  the CLEAN row this check used to omit. A present binary that does not
  report a usable version, or reports below the floor, is BROKEN.

- **Lane credential structure.** Runs only when the binary row did not
  short-circuit. Invoke `tools/read-kimi-credential-state.ps1 -Path
  <credential-file>` against the configured lane credential, and accept
  the measurement ONLY under the FOUR-PART ACCEPTANCE RULE: the process
  launched, it exited 0, stderr was EMPTY, and stdout was exactly one
  parseable line whose status/detail pairing is one of Task 2's table.
  A process-launch failure, ANY nonzero exit, nonempty stderr, zero or
  several stdout lines, a JSON parse failure, wrong keys or types, or a
  pairing outside that table is "the validator itself fails to run":
  BROKEN, and NO credential recovery command is fabricated, because no
  credential state was measured. Otherwise map the accepted `status`:
  - `ok` is OK — "lane credential structurally present".
  - `absent` is N/A, and no hash is taken at all.
  - `unreadable` or `malformed` is BROKEN.

  All three credential-failure rows above — `absent`, `unreadable` and
  `malformed` — print THE LANE LOGIN RECOVERY COMMAND from `Fixed names
  and values`, complete and executable, against the configured lane
  home:

  ```powershell
  & { $ErrorActionPreference = 'Stop'; try { $ownerLines = @(& 'tools/kimi-lane-lock.ps1' -ResolveOwner); $ownerExit = $LASTEXITCODE; if ($ownerExit -ne 0) { throw "owner resolution failed with exit $ownerExit" }; if ($ownerLines.Count -ne 1 -or -not ($ownerLines[0] -is [string]) -or [string]::IsNullOrWhiteSpace([string]$ownerLines[0])) { throw 'owner resolution returned invalid output' }; $owner = $ownerLines[0] | ConvertFrom-Json -ErrorAction Stop; if (-not ($owner -is [System.Management.Automation.PSCustomObject])) { throw 'owner resolution returned invalid schema' }; $ownerFields = @($owner.PSObject.Properties.Name); if ($ownerFields.Count -ne 3 -or -not ($ownerFields -ccontains 'ownerPid') -or -not ($ownerFields -ccontains 'ownerStartTicksUtc') -or -not ($ownerFields -ccontains 'ownerName') -or -not (($owner.ownerPid -is [int]) -or ($owner.ownerPid -is [long])) -or [long]$owner.ownerPid -le 0 -or -not ($owner.ownerStartTicksUtc -is [string]) -or $owner.ownerStartTicksUtc -notmatch '\A[0-9]+\z' -or -not ($owner.ownerName -is [string]) -or [string]::IsNullOrWhiteSpace($owner.ownerName)) { throw 'owner resolution returned invalid schema' }; if ([string]::IsNullOrWhiteSpace($env:TEMP) -or -not (Test-Path -LiteralPath $env:TEMP -PathType Container -ErrorAction Stop)) { throw 'TEMP is not an existing directory' }; $verdictOut = Join-Path -Path $env:TEMP -ChildPath 'parallax-kimi-lane-login-verdict.json' -ErrorAction Stop; & 'tools/new-kimi-lane-login.ps1' -LaneHome '<lane-home>' -OwnerPid ([string]$owner.ownerPid) -OwnerStartTicksUtc $owner.ownerStartTicksUtc -VerdictOut $verdictOut; $loginExit = $LASTEXITCODE; if ($loginExit -ne 0) { throw "lane login failed with exit $loginExit" } } catch { throw } }
  ```

  **Hash procedure, a seven-step algorithm run around the validator call
  above so a hash failure never leaves the validator substate
  unmeasured:**
  1. Test existence of the credential file.
  2. If ABSENT: run the validator, require `absent`, take NO hash.
  3. If PRESENT: attempt hash 1 (SHA-256 of the file's bytes) and record
     success or failure.
  4. Run the validator REGARDLESS of hash 1's outcome.
  5. If the file is still present, attempt hash 2. Disappearance between
     the two hashes is BROKEN.
  6. Compare ONLY if both hashes exist. Never compare a missing value to
     anything.
  7. Any hash failure is BROKEN, and it does NOT suppress the validator
     detail.

  A hash that cannot be taken on a PRESENT credential is BROKEN. The two
  hashes show only that bytes changed during the interval, never WHO
  changed them: differing hashes are BROKEN, "credential bytes changed
  during the check; actor not established"; equal hashes are reported as
  "no net byte change observed", never as proof nothing wrote the file.

  An AUTHENTICATED probe is a SEPARATE operation and is never part of
  check 8. It acquires the lane lock, it MAY REFRESH the dedicated
  lane credential, and it never touches the user's ordinary
  credential. Check 8 reports STRUCTURE only, so a structurally
  present credential is not a working one.

- **Lane lock status.** Run `tools/kimi-lane-lock.ps1 -Status -LaneHome
  <lane-home>`, accepted only under the same four-part rule as the
  credential check above. An unreadable lock, a missing lock tool, or a
  status invocation that fails that rule is "lock status cannot be
  measured": BROKEN, and no recovery command is fabricated from evidence
  the check does not have. Otherwise map the reported record:
  - `free` is OK.
  - `held` and LIVE is OK, reported as held with the holder — LIVE means
    the holder's process is running, and never that a debate was
    abandoned.
  - `held` and DEAD is STALE, reclaimable at the next acquire.
  - `held`, SAME-HOST — the record's `host` equals `$env:COMPUTERNAME`,
    compared case-insensitively — and UNKNOWN is N/A: liveness could NOT
    be determined, and every mutating mode therefore treats the holder
    as alive and will not reclaim it. Same-host is what selects this
    row, because a foreign-host record also reports UNKNOWN liveness.
  - foreign-host — the record's `host` differs from
    `$env:COMPUTERNAME`, compared case-INSENSITIVELY, which is the
    comparison the doctor makes since `-Status` reports the field — is
    STALE, with:
    `tools/kimi-lane-lock.ps1 -ForceRelease -LaneHome <lane-home> -ConfirmHost <host> -ConfirmOwnerPid <pid> -ConfirmOwnerStartTicksUtc <ticks> -ConfirmDebateId <id> -ConfirmNonce <nonce>`
  - MALFORMED is STALE, with:
    `tools/kimi-lane-lock.ps1 -MalformedOverride -LaneHome <lane-home> -ConfirmSha256 <sha256>`

  Every CONFIRMATION placeholder above is a field `-Status` prints,
  which is why `-Status` carries the complete identity; `<lane-home>` is
  not — it is the configured lane home against which status was
  requested.

- **Containment artifact.** Verify the committed
  `skills/multi-model-verify/references/kimi-reviewer-agent.md` exists in
  the installed copy and its `tools:` allowlist is present (do not
  re-derive the list here; report presence/absence only). Missing file or
  allowlist is BROKEN.

Report the version, the floor comparison, the credential structure
verdict, the lock verdict and its holder detail when held, and the
artifact/allowlist presence. This check never imports `kimi_cli` (there
is no such module on this client) and never passes `--quiet` or
`--thinking` (neither flag exists on this client).

## 9. Reviewer context isolation

Same sanitized shell as check 4. Resolve `tools/codex-context-probe.ps1`
under the `installPath` from check 1 — never a bare relative path — and
run it with a FRESH scratch file for the override artifact:

```powershell
$ovr = "$env:TEMP\parallax-doctor-override-$(Get-Random).txt"
powershell -NoProfile -File <installPath>\tools\codex-context-probe.ps1 -WorkDir . -SuppressSkills -OverrideOut $ovr -Json
```

Report all four skill buckets and the two instruction flags from the JSON.
OK is exit 0 with `repo_scoped`, `plugin_cache_scoped`, `unknown_scoped`
and `skills_after` all 0. Report `global_agents_md` as an environment note,
never as a failure: nothing available removes it. Print
`global_agents_md_path` when the probe resolved one; when that field is
empty, say the prompt carries a global instruction block whose source the
prompt itself does not name, rather than inventing a path.

**Split the non-zero exit by SCOPE — this check reports on the MACHINE,
and the current directory is not the machine.** A hit whose source is
`repo_scoped`, or a reported project `AGENTS.md`, is a property of
whatever repo you happen to be standing in, and preflight 3 already
handles it through the review mirror: report `N/A (this repo carries
back-channels — preflight 3 remediates them in the mirror)` and name the
entries. BROKEN is reserved for machine-scoped hits — a non-zero
`plugin_cache_scoped`, `unknown_scoped` or `skills_after`, or any other
blocked reason — because those follow the reviewer everywhere and mean a
review dispatched from this machine right now would carry instruction
sources the gate is supposed to have removed. A check that reads BROKEN in
every normally configured repo teaches the user to ignore BROKEN.

The probe spends no tokens: `codex debug prompt-input` renders the prompt
and calls no model.
