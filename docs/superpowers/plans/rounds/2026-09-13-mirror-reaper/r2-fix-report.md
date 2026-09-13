# Astra diff R2 fix report, 2026-09-13

Worktree: `C:\Users\Brandon\Documents\_worktrees\parallax-mirror-reaper`
Base HEAD: fafc4ce4ba9fc3061133f4ab722ea688faeaaed7
Commit: c77d0dfaca335860faaaed03710a15c1282ee9a2

## F1 (R2-1a). Ordinal read-back comparison - `tools/write-attestation.ps1:300`

Replaced `if ($writtenText -ne $json) {` with
`if (-not [string]::Equals($writtenText, $json, [System.StringComparison]::Ordinal)) {`
and added the required one-line comment above it. Nothing else in that
block changed.

**Null-Equals measurement, both hosts** (one-liner:
`[string]::Equals($null, 'x', [System.StringComparison]::Ordinal)`):

- Windows PowerShell 5.1 (`powershell.exe`): `False`
- PowerShell 7 (`pwsh.exe`): `False`

Both hosts return `False` for a `$null` left side against a non-null
right side, which is the wanted outcome: the guard's `-not [string]::Equals(...)`
condition is then `True`, so the block prints the mismatch error and
exits 2, exactly as it did before this change when `$writtenText` was
`$null`.

## F2 (R2-1a, R2-1b). Tests - `evals/multi-model-verify/test_mirror_reaper.py`

(a) Appended `test_the_record_comparison_is_ordinal`, which reads the
emitter source and asserts the ordinal-Equals call appears exactly once
and neither `-ne` nor `-eq` form of the old comparison appears, with a
two-line comment explaining why this is a source pin rather than a
runtime case: the harness cannot make the on-disk file differ from the
serialized text by case alone (`Set-Content` writes exactly `$json`), so
the comparison form itself is what has to be locked.

(b) In `test_the_record_lands_in_the_bracketed_repo_and_the_sibling_is_untouched`:
before calling `attest`, pre-planted a stale record
(`{"stale": true}`) at the literal bracketed path `att_file(repo, head)`,
creating its parent directories first (`att_file` itself does not create
directories - confirmed by reading its definition, a plain path join).
Kept `assert "decoy" not in record` and added `assert "stale" not in
record`. Replaced the decoy assertion with byte equality: captured
`decoy_bytes = json.dumps({"decoy": True}).encode("utf-8")`, wrote it
with `write_bytes`, and now assert `decoy_file.read_bytes() == decoy_bytes`.
The emitter's `Set-Content` overwrites the stale record as expected: the
test still asserts exit 0 and `record["head_sha"] == head`.

## F3 (R2-3, record). `BACKLOG.md`, item 102

Added a third follow-up bullet to item 102's decision list, naming the
post-delete sidecar read-back failure branches
(`still exists after removal`, `could not be re-examined after removal`)
in `tools/write-attestation.ps1` as untested: the session has no
non-administrator mechanism that makes a file survive
`[System.IO.File]::Delete` without throwing, or that makes the
following `GetAttributes` throw for a reason other than absence, and the
ordering is locked only by the source-position pin
`test_sidecar_success_is_read_back`, which a refactor could satisfy
without a runtime read-back. Attributed to the diff debate's round 2.
Updated the list's lead line from "Two follow-ups, one decision each."
to "Three follow-ups, decisions for the first two, a test gap for the
third." for accuracy, since the new item is a test gap rather than a
decision.

Item 102 carries a `Verified:` digest line, so ran
`python evals/tools/backlog_lint.py` (no `--digests`) first, which
reported `item 102: rule 7 (verified digest): content changed since
attestation; expected digest 1524f48584c9`. Updated the line to
`Verified: 2026-09-13 1524f48584c9`. A follow-up plain
`python evals/tools/backlog_lint.py` run reported `backlog lint: clean`.

## Verification

`$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest
evals/multi-model-verify/test_mirror_reaper.py
evals/multi-model-verify/test_attestation.py -q`:
**67 passed** in 60.31s, exit 0.

`$env:PARALLAX_PS_HOST = "pwsh.exe"; python -m pytest
evals/multi-model-verify/test_mirror_reaper.py
evals/multi-model-verify/test_attestation.py -q`:
**67 passed** in 67.80s, exit 0.

(66 pre-existing plus the new `test_the_record_comparison_is_ordinal`,
identical count and result on both hosts.)

`python evals/tools/skill_lint.py skills/multi-model-verify --strict`:
`PASS - 0 error(s), 2 warning(s)` (pre-existing SKILL.md length/token
warnings, unrelated to this diff), exit 0.

`python evals/tools/skill_scanner.py skills`:
`clean - no findings`; `Summary: 0 CRITICAL, 0 WARN, 0 INFO`, exit 0.

`python evals/tools/backlog_lint.py`: `backlog lint: clean`, exit 0.

## Commit

Staged by explicit path: `tools/write-attestation.ps1
evals/multi-model-verify/test_mirror_reaper.py BACKLOG.md`.

Commit `c77d0dfaca335860faaaed03710a15c1282ee9a2`:
"apply diff debate round 2: compare the attestation read-back
ordinally, plant a stale record in the bracketed case, and record the
untaken read-back failure test"

3 files changed, 36 insertions(+), 5 deletions(-).

## Concerns

Item 102's intro paragraph (unedited, pre-existing) separately calls the
plan-mode terminal-event follow-up "the third follow-up" in prose. That
phrase referred to a concept never given its own numbered bullet before
this change; the new bullet 3 added here is a different, unrelated
residual (the sidecar read-back test gap). The two "thirds" name
different things and the brief did not ask to reconcile that
pre-existing prose reference, so it was left as-is - worth a maintainer
look if it reads as confusing.
