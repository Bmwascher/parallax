# Astra diff R2 fix brief, 2026-09-13

Branch `mirror-reaper`, worktree `C:\Users\Brandon\Documents\_worktrees\parallax-mirror-reaper`, HEAD fafc4ce. Work ONLY in that worktree (never in `C:\Users\Brandon\Documents\parallax`, which is another chat's checkout). The reviewer's round-2 reply is at `C:\Temp\parallax-scratch\2026-09-13-mirror-reaper\astra-diff-r2-reply.md` (read claims 1 and 3). Apply everything in ONE commit. Tools stay ASCII-only, LF, identical under Windows PowerShell 5.1 and PowerShell 7. Never touch `C:\kv-*`, `C:\kvs-*`, `C:\Users\Brandon\AppData\Local\Temp\pxmr` or `C:\Users\Brandon\AppData\Local\Temp\kvs-pxmr`. Do not dispatch subagents.

## F1 (R2-1a). Ordinal read-back comparison - `tools/write-attestation.ps1:300`

PowerShell's `-ne` on strings is case-insensitive (measured on both hosts: `'{"p":"Session"}' -ne '{"p":"session"}'` is False). Replace the condition `if ($writtenText -ne $json) {` with
`if (-not [string]::Equals($writtenText, $json, [System.StringComparison]::Ordinal)) {`
and add a one-line comment above it: `# Ordinal: -ne is case-insensitive on strings, so it would accept a read-back that differs only in letter case.` Nothing else in that block changes. Note `$writtenText` may be `$null` there; `[string]::Equals($null, "x", Ordinal)` returns False, which is the wanted outcome (exit 2). Confirm that on both hosts in a one-liner and state the result in the report.

## F2 (R2-1a, R2-1b). Tests - `evals/multi-model-verify/test_mirror_reaper.py`

(a) Append `test_the_record_comparison_is_ordinal`: `body = read(WRITE)`; assert `body.count("[string]::Equals($writtenText, $json, [System.StringComparison]::Ordinal)") == 1` and `"$writtenText -ne $json" not in body` and `"$writtenText -eq $json" not in body`. Add a two-line comment saying why a source pin: the harness cannot make the file on disk differ from the serialized text by case alone, so the comparison form is locked at the source.

(b) In `test_the_record_lands_in_the_bracketed_repo_and_the_sibling_is_untouched` (line 569): before running `attest`, also pre-plant a stale record in the BRACKETED repository at `att_file(repo, head)` (create its parent directories) with content `{"stale": true}`, so the case rejects e9d2713's false-success branch (old record at the literal path, write landing in the sibling) and not only its write-elsewhere branch; keep `assert "decoy" not in record` and add `assert "stale" not in record`. Replace the decoy assertion with byte equality: capture `decoy_bytes = json.dumps({"decoy": True}).encode("utf-8")`, write it with `write_bytes`, and assert `decoy_file.read_bytes() == decoy_bytes`. Check whether `att_file` creates directories; if it does not, `mkdir(parents=True, exist_ok=True)` the parent yourself. The emitter must OVERWRITE the stale record (it does today: `Set-Content` replaces), so the case still expects exit 0 and `head_sha == head`.

## F3 (R2-3, record). `BACKLOG.md`, item 102

Item 102 ends with residual rows/bullets (read the item; it starts at the line `## 102.`). Add one more residual in the same shape as its neighbours: the post-delete sidecar read-back failure branches (`still exists after removal`, `could not be re-examined after removal`) in `tools/write-attestation.ps1` have no driving test, because the session has no non-administrator mechanism that makes a file survive `[System.IO.File]::Delete` without throwing or makes the following `GetAttributes` throw for a reason other than absence; the ordering is locked only by a source-position pin (`test_sidecar_success_is_read_back`), which a refactor could satisfy without a runtime read-back. Named by the diff debate's round 2. Then run `python evals/tools/backlog_lint.py --digests` if the item carries a `Verified:` digest line and re-attest whatever it tells you to (read the tool's usage first; if the item has no digest, plain `backlog_lint.py` must stay clean).

## Verification, then commit

In PowerShell, foreground: `$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_mirror_reaper.py evals/multi-model-verify/test_attestation.py -q` then with `"pwsh.exe"`; then `python evals/tools/skill_lint.py skills/multi-model-verify --strict`, `python evals/tools/skill_scanner.py skills`, `python evals/tools/backlog_lint.py`. Never run the native git or python calls under `$ErrorActionPreference = 'Stop'`; do not pipe test output through head/tail/Select-Object -Last.

Stage by explicit path (`git add tools/write-attestation.ps1 evals/multi-model-verify/test_mirror_reaper.py BACKLOG.md`). Commit message: `apply diff debate round 2: compare the attestation read-back ordinally, plant a stale record in the bracketed case, and record the untaken read-back failure test`.

Report to `C:\Temp\parallax-scratch\2026-09-13-mirror-reaper\r2-fix-report.md`: per finding the change; the null-Equals measurement on both hosts; both hosts' pytest counts; the lint lines; the commit sha. Reply with status (DONE / DONE_WITH_CONCERNS / BLOCKED), the commit sha, one line of test summary, and concerns only.
