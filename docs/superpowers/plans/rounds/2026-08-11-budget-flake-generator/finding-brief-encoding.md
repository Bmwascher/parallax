# The documented codex dispatch corrupts a non-ASCII brief on Windows PowerShell 5.1

**Found 2026-08-11, during 0.23.0 plan round 1. Not a review finding — a
transport defect in shipped contract text, caught by the round-evidence tool.**

## What happened

`skills/multi-model-verify/SKILL.md:196` (and the resume form at :250)
documents the dispatch as:

```powershell
Get-Content -Raw <brief-file> | codex exec ... --output-last-message <reply-file> -
```

Run under Windows PowerShell 5.1 with a UTF-8, no-BOM brief containing 45
non-ASCII bytes (14 em dashes), `tools/read-codex-round-evidence.ps1 -Fresh`
returned:

```
{"status":"failed","reason":"the recorded prompt does not match the declared
brief: no user record in this call's slice hashes to 0d3697ac...7e8dd"}
```

Exit 1. Class `brief-attribution`. The reply was discarded unread, as the
contract requires.

## The mechanism, measured not assumed

Diffing the rollout's recorded user record against the brief on disk:

```
recorded chars: 13365   brief chars: 13333
replace  mine: '—'  ->  rec: '???'      (x14)
```

Every em dash arrived as THREE question marks. That count is the proof that
BOTH halves fired, independently:

1. **Wrong decode.** `Get-Content -Raw` on Windows PowerShell 5.1 reads a
   UTF-8 file with no BOM using the ANSI code page, so one 3-byte em dash
   became three cp1252 characters.
2. **Wrong pipe encoding.** `$OutputEncoding` defaults to ASCII on 5.1, so
   each of those three characters was flattened to `?` on the way to the
   native client.

One defect alone would have produced ONE question mark per em dash. Three
means the character was split first and flattened second.

## Why it matters beyond one round

The reviewer answered a brief this side never wrote, and nothing in the
transport said so — exactly the failure the codex brief binding was built
for (`model-prompting-notes.md`, region `codex-brief-binding-calls`). Before
that binding existed this round would have read as clean.

It is the same class as the 0.21.0 finding that 5.1 native argument
splatting strips embedded double quotes: a Windows PowerShell 5.1 marshalling
hazard sitting inside documented contract text, invisible on PowerShell 7.

## The fix that was used to recover, and what it proves

Re-dispatched on the SAME host (5.1) with two changes:

```powershell
$OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$brief = [System.IO.File]::ReadAllText($path, (New-Object System.Text.UTF8Encoding($false, $true)))
$brief | codex exec ...
```

`ReadAllText` with an explicit strict UTF-8 decoder fixes half 1;
`$OutputEncoding` fixes half 2. A clean round-evidence verdict on 5.1 after
the change, against a failing one before it on the same host and the same
brief, is the before/after pair.

## Status

Costed one full round of reviewer quota for nothing. Carried into the 0.23.0
debate as a proposed addition to the release, since it is transport contract
text and the cycle is already editing `SKILL.md`.
