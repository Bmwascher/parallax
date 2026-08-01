The recovery command still needs a FIX. The parse failure is confirmed in the committed Task 6 test: execution continues into login after `ConvertFrom-Json -ErrorAction Stop` fails ([evals/multi-model-verify/test_kimi_lane_home.py:1470](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_kimi_lane_home.py:1470), [evals/multi-model-verify/test_kimi_lane_home.py:1505](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_kimi_lane_home.py:1505)). This directly contradicts the frozen fail-closed claim ([docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:102](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:102), [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:105](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:105)).

## 1. Frozen command

Use this verbatim:

```powershell
& { $ErrorActionPreference = 'Stop'; try { $ownerLines = @(& 'tools/kimi-lane-lock.ps1' -ResolveOwner); $ownerExit = $LASTEXITCODE; if ($ownerExit -ne 0) { throw "owner resolution failed with exit $ownerExit" }; if ($ownerLines.Count -ne 1 -or -not ($ownerLines[0] -is [string]) -or [string]::IsNullOrWhiteSpace([string]$ownerLines[0])) { throw 'owner resolution returned invalid output' }; $owner = $ownerLines[0] | ConvertFrom-Json -ErrorAction Stop; if (-not ($owner -is [System.Management.Automation.PSCustomObject])) { throw 'owner resolution returned invalid schema' }; $ownerFields = @($owner.PSObject.Properties.Name); if ($ownerFields.Count -ne 2 -or -not ($ownerFields -ccontains 'ownerPid') -or -not ($ownerFields -ccontains 'ownerStartTicksUtc') -or -not (($owner.ownerPid -is [int]) -or ($owner.ownerPid -is [long])) -or [long]$owner.ownerPid -le 0 -or -not ($owner.ownerStartTicksUtc -is [string]) -or $owner.ownerStartTicksUtc -notmatch '\A[0-9]+\z') { throw 'owner resolution returned invalid schema' }; if ([string]::IsNullOrWhiteSpace($env:TEMP) -or -not (Test-Path -LiteralPath $env:TEMP -PathType Container -ErrorAction Stop)) { throw 'TEMP is not an existing directory' }; $verdictOut = Join-Path -Path $env:TEMP -ChildPath 'parallax-kimi-lane-login-verdict.json' -ErrorAction Stop; & 'tools/new-kimi-lane-login.ps1' -LaneHome '<lane-home>' -OwnerPid ([string]$owner.ownerPid) -OwnerStartTicksUtc $owner.ownerStartTicksUtc -VerdictOut $verdictOut; $loginExit = $LASTEXITCODE; if ($loginExit -ne 0) { throw "lane login failed with exit $loginExit" } } catch { throw } }
```

The child scriptblock prevents `$ErrorActionPreference` from persisting in the user’s interactive scope. The `try` structurally prevents every later operation after a terminating failure. The owner validation matches Task 3’s exact two-property output and the globally frozen PID/ticks types ([docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:85](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:85), [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:361](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:361)).

Also amend Global Constraint line 61 and the rationale at line 105: `-ErrorAction Stop` promotes an error to terminating, but is not by itself a top-level semicolon-chain guard. The later invocation must be structurally unreachable following failure ([docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:61](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:61)).

## 2. Task 6 row 2

Yes. After replacing the command, row 2 must assert:

- overall nonzero;
- login marker absent;
- no verdict;
- no credential mutation.

Delete the current exemption that deliberately omits marker absence ([evals/multi-model-verify/test_kimi_lane_home.py:1498](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_kimi_lane_home.py:1498), [evals/multi-model-verify/test_kimi_lane_home.py:1505](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_kimi_lane_home.py:1505)).

The existing four-row matrix is no longer exhaustive because it covers only owner exit, JSON syntax, login exit, and success ([docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:511](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:511)). Expand it to cover:

1. Owner launch failure.
2. Owner nonzero.
3. Zero or multiple owner-output lines.
4. Malformed JSON.
5. Valid JSON with wrong object shape, property set, PID type/value, or ticks type/value.
6. Missing/non-directory TEMP, plus a forced `Join-Path` failure.
7. Login launch failure.
8. Login nonzero.
9. Full success.

Every row before login launch must assert that login was never invoked.

## 3. Additional boundaries

Yes—there are more than four.

The unresolved dependencies were owner-output cardinality, owner schema, TEMP suitability, `Join-Path`, and both process-launch boundaries. Merely parsing JSON would accept `{}`, `[]`, wrong types, or additional fields even though Task 3 promises one exact owner object ([docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:361](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:361)).

There are also three blocking caller defects already present in Tasks 5 and 6:

- Both callers accept a scalar string as `fields`, because `@($parsed.fields)` converts it into a one-element array before validation. That violates the frozen requirement that `fields` itself be an array ([tools/new-kimi-lane-login.ps1:282](C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-login.ps1:282), [tools/new-kimi-lane-home.ps1:240](C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-home.ps1:240), [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:97](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:97)). Require `fields -is [System.Array]` before validating its elements, with an exit-zero scalar-fields fixture at every validator call position.

- Both callers discard blank lines before counting stdout lines, so output containing extra blank lines can pass the “exactly one line” contract ([tools/new-kimi-lane-login.ps1:270](C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-login.ps1:270), [tools/new-kimi-lane-home.ps1:228](C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-home.ps1:228)). Freeze acceptance as one nonempty line, optionally followed by exactly one LF or CRLF; reject leading, interior, or additional blank lines.

- Both use `Get-Content -ErrorAction SilentlyContinue` and convert a failed stderr read into empty stderr, allowing an unmade measurement to satisfy the acceptance rule ([tools/new-kimi-lane-login.ps1:262](C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-login.ps1:262), [tools/new-kimi-lane-home.ps1:220](C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-home.ps1:220)). Make both capture reads terminating; any read failure is validator failure. Add a deterministic capture-read fault oracle.

Finally, both callers pass unquoted script and credential paths through `Start-Process -ArgumentList` ([tools/new-kimi-lane-login.ps1:254](C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-login.ps1:254), [tools/new-kimi-lane-home.ps1:212](C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-home.ps1:212)). Task 6’s success test explicitly avoids a path segment combining a space and apostrophe because it currently mis-tokenizes ([evals/multi-model-verify/test_kimi_lane_home.py:1519](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_kimi_lane_home.py:1519)). Quote both file-path arguments correctly and make the dual-host success fixture contain both characters; the test must not work around the shipped defect.

## Per-task verdicts

- Task 1 — Built and independently verified; unaffected by this reopening ([docs/superpowers/plans/rounds/2026-08-01-cred-lock/build-ledger.md:14](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-01-cred-lock/build-ledger.md:14)). **PASS**
- Task 2 — Its shared validator contract is sufficiently explicit; the discovered violations are in its callers ([docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:86](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:86)). **PASS**
- Task 3 — `-ResolveOwner` already freezes the exact output needed by the corrected command ([docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:361](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:361)). **PASS**
- Task 4 — Unaffected by this reopening; its committed verification is recorded ([docs/superpowers/plans/rounds/2026-08-01-cred-lock/build-ledger.md:17](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-01-cred-lock/build-ledger.md:17)). **PASS**
- Task 5 — Fix argument quoting, exact-line parsing, scalar `fields`, and capture-read failure handling; add decisive dual-host oracles. **FIX — BLOCKING**
- Task 6 — Replace the shared command, expand Step 1b’s state partition, restore row-2 marker absence, and apply the same caller fixes as Task 5. **FIX — BLOCKING**
- Task 7 — Plan text unaffected. Built implementation has not yet entered the ledger’s reviewed set. **PASS**
- Task 8 — Consume and pin the replacement shared command; retain Task 6 as its sole execution oracle ([docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:693](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:693)). **FIX — BLOCKING**
- Task 9 — No shipped-literal change follows from this correction. **PASS**
- Task 10 — Its final gates must be rerun after Tasks 5, 6, and 8 change. **PASS**

## Overall verdict

**FIX — BLOCKING.** Do not re-freeze yet. The command, its global rationale, Task 6’s execution partition, Task 8’s pin, and both validator callers require correction.

## Final check

UNVERIFIED:

- The proposed replacement command has not yet been run end-to-end under both hosts.
- Task 7’s built implementation is unreviewed and absent from the current ledger, which records only Tasks 1–6 ([docs/superpowers/plans/rounds/2026-08-01-cred-lock/build-ledger.md:12](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-01-cred-lock/build-ledger.md:12)).
- Cross-vendor and CI verification remain outstanding; the ledger explicitly says local implementer/session evidence is not a substitute ([docs/superpowers/plans/rounds/2026-08-01-cred-lock/build-ledger.md:42](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-01-cred-lock/build-ledger.md:42)).
- The final full-suite gate still has the recorded console-encoding failure to resolve or re-scope ([docs/superpowers/plans/rounds/2026-08-01-cred-lock/build-ledger.md:49](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-01-cred-lock/build-ledger.md:49)).
- External measurements remain unverified from repository files.