# Round-1 fix report, 2026-09-13

Branch `mirror-reaper`, worktree `C:\Users\Brandon\Documents\_worktrees\parallax-mirror-reaper`,
commit fafc4ce (parent e9d2713).

## F1 (R1-3a) - literal write, content read-back

`tools/write-attestation.ps1`, the write block (was lines 285-296): serialize once to `$json`,
`Set-Content -LiteralPath $outFile -Value $json -Encoding ASCII -NoNewline -ErrorAction Stop`
inside try/catch (write failure -> exit 2, existing "nothing was reaped" message unchanged);
then `[System.IO.File]::ReadAllText($outFile)` inside its own try/catch (any exception, including
absence, leaves `$writtenText = $null`); a mismatch against `$json` (absence, unreadable, or
unequal content) prints `ERROR: the attestation on disk does not match what was written
(<path>) - nothing was reaped` and exits 2. Kept `-NoNewline`: both host runs of
`test_attestation.py` passed with it in place, so it was not dropped.

Covering test: `test_the_record_lands_in_the_bracketed_repo_and_the_sibling_is_untouched`
(new, `evals/multi-model-verify/test_mirror_reaper.py`, Group 6). `git init -q -b main` inside
`repo[1]` succeeded on this host without incident, so the case was not renamed away. The test
asserts exit 0, `att_file(repo, head)` exists with `head_sha == head` and no `decoy` key, the
plain-named sibling `repo1`'s pre-planted `{"decoy": true}` record is untouched, and the mirror
is reaped (`not mirror.exists()`).

## F2 (R1-3b) - sidecar inspection failure named, not swallowed

Same file, the sidecar block: the bare `catch { $sa = $null }` is now three typed catches -
`[System.IO.FileNotFoundException]` and `[System.IO.DirectoryNotFoundException]` set
`$sa = $null` (absence); any other exception prints `ERROR: reap failed for <sidecar>: the
sidecar could not be examined: <message> - the attestation stands; remove the sidecar by
hand<bridgeNote>` and exits 3.

**F2 measurement (both hosts):** built a probe (scratchpad, outside the reviewed tree) that
writes a sidecar-shaped file, runs `icacls <sidecar> /deny "<USERNAME>:(RA)"`, then calls
`[System.IO.File]::GetAttributes($sidecar)` in a try/catch. Result on both hosts:

- `powershell.exe` (5.1): `NO-THROW: attrs=32` - `GetAttributes` succeeded despite RA denied.
- `pwsh.exe` (7): `NO-THROW: attrs=32` - same.

`GetAttributes` on Windows does not consult the RA (read-attributes) ACE the way file-content
reads consult the read-data ACE; denying it to the owning user did not reproduce an inspection
failure on either host. Per the brief, no test was added for this branch; it is recorded as
covered by reading only. The probe's grant/deny ACEs were reverted and the probe file removed
after the measurement (icacls `/remove:d` then `/grant`, then `Remove-Item`).

## F3 (R1-8) - sidecar deletion has an absence read-back

Same block: after `[System.IO.File]::Delete($sidecar)`, the sidecar's attributes are read back
the way `Remove-ReviewTree` does for its root (`tools/review-tree-removal.ps1:167-179`) -
`FileNotFoundException`/`DirectoryNotFoundException` mean gone (fall through to the success
print); a successful read means the sidecar still exists and prints `ERROR: reap failed for
<sidecar>: the sidecar still exists after removal - the attestation stands; remove the sidecar
by hand<bridgeNote>` and exits 3; any other exception prints the "...could not be re-examined
after removal: <message>" variant and exits 3. `reaped sidecar: <path>` now prints only after
that read-back passes.

Covering tests: `test_a_sidecar_failure_names_the_unattempted_bridge` (existing, unchanged - a
held handle fails at `Delete`, before the read-back is reached, so it needed no extension) and
`test_sidecar_success_is_read_back` (new, Group 6) - normal mirror + sidecar reap, asserts the
`reaped sidecar: ` line and absence, and pins ordering by asserting
`body.index("still exists after removal") < body.index('"reaped sidecar: "')` against the tool
source.

## F4 (record) - plan block superseded

`docs/superpowers/plans/2026-09-13-mirror-reaper.md`: inserted the exact superseding paragraph
directly above the line `(f) Replace the final two lines` in Task 3 Step 3.

## Verification (foreground, both hosts)

- `PARALLAX_PS_HOST=powershell.exe`: `python -m pytest evals/multi-model-verify/test_mirror_reaper.py evals/multi-model-verify/test_attestation.py -q`
  -> **66 passed in 66.53s**
- `PARALLAX_PS_HOST=pwsh.exe`: same command -> **66 passed in 79.86s**
- `python evals/tools/skill_lint.py skills/multi-model-verify --strict` -> `PASS - 0 error(s), 2 warning(s)`
  (pre-existing SKILL.md length/token warnings, unrelated to this change - skills/ was not touched)
- `python evals/tools/skill_scanner.py skills` -> `Summary: 0 CRITICAL, 0 WARN, 0 INFO` (clean)
- `python evals/tools/backlog_lint.py` -> `backlog lint: clean`

## Commit

Staged by explicit path (`tools/write-attestation.ps1`, `evals/multi-model-verify/test_mirror_reaper.py`,
`docs/superpowers/plans/2026-09-13-mirror-reaper.md`) and committed as fafc4ce with the brief's
exact message. No native git call ran under `$ErrorActionPreference = 'Stop'`. Verified the
staged blob for `write-attestation.ps1` normalizes back to LF-only (362 lines, 0 CRLF) despite
autocrlf=true checking it out as CRLF in the working tree.

## Concerns

None that block. The only judgment call was F2's coverage: neither host's `GetAttributes`
throws under an RA-denied ACE, so the brief's fallback ("add NO test ... write in the report
exactly what you measured") applies as written.
