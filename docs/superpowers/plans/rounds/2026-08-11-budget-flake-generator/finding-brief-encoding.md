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
non-ASCII bytes (**15** em dashes — CORRECTED, this file first said 14;
plan-debate point 16 refuted it and the correction is re-measured below),
`tools/read-codex-round-evidence.ps1 -Fresh` returned:

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

### The 32-character delta, reconciled

**ADDED 2026-08-11 after the whole-branch review asked what accounted for
it.** The paragraph above left the reader to assume the em dashes explained
the whole difference. They do not, and the arithmetic did not close: 15
dashes at +2 characters each is +30, not +32.

Re-measured on the retained brief itself
(`plan-brief-r1.md`, byte-identical to the one dispatched):

```
utf8 chars      : 13333
file bytes      : 13363
non-ascii bytes : 45
em dashes       : 15
cp1252-decoded  : 13363
```

So the two halves of the delta have two different causes:

- **+30** from the wrong decode. 15 em dashes, 3 bytes each, each byte
  becoming one cp1252 character: 13333 characters in, 13363 out. Every
  non-ASCII byte in the file belongs to an em dash, which is why the
  decoded length equals the byte length exactly.
- **+2** from the pipe itself. PowerShell appends a trailing CRLF when it
  pipes a string to a native command. That is not corruption and it is not
  new to this defect; it is declared in the byte tests as `EOL = "0d0a"`
  and is present on the fixed path too.

The `x14` in the capture above is the diff tool's replacement COUNT, and it
disagrees with the measured 15. **That disagreement is not explained here.**
The obvious explanation, two adjacent corrupted runs merging into one
replacement, was tested and REFUTED: the fifteen em dashes sit at character
offsets 1381, 1543, 2628, 3028, 3068, 4053, 4133, 4261, 5972, 7199, 7235,
7518, 9072, 9377 and 9958, and the smallest gap between any two is 36
characters, so nothing is adjacent. The diff tool's grouping was not
investigated further. What IS measured is the count in the file: 15.
A count taken from a diff summary was treated as a measurement for three
rounds, and it was not one.

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

## What 0.23.0 does NOT guard

**ADDED 2026-08-11 at the ruling of diff-debate round 1.** This release
fixes the DOCUMENTED SKILL DISPATCH and nothing else. Three other places
send text across the same 5.1 boundary, and naming them is the point of
this section: an unnamed residual reads as an absence.

- **`tools/check-drift.ps1:700` — LIVE and UNGUARDED.** The weekly drift
  autofix review dispatches `Get-Content -Raw $briefPath | codex exec`,
  and its brief embeds the drift report plus a `main..HEAD` diff, which in
  this repo routinely carries em dashes. Its brief is written with
  `Set-Content` and read back with `Get-Content -Raw`, both using the ANSI
  code page, so the round trip is lossless for cp1252 characters and only
  the PIPE degrades: ONE `?` per em dash rather than three. Smaller than
  the defect above, and just as silent, because that dispatch has NO
  brief-attribution binding to catch it. Not fixed here: the diff debate
  applied `debate-protocol.md:108-126` and ruled the file outside this
  range's enumerated verification surface. Held as a named backlog item.
- **`commands/doctor.md:70` — LATENT.** The same pipe shape, but the
  payload is a fixed ASCII literal, so no corruption is reachable today.
  It becomes live the moment that string changes.
- **The backup lane's argument path — UNMEASURED.** kimi-code takes its
  brief as an argument rather than on stdin, so this defect's mechanism
  does not apply unchanged. Whether the 5.1 argument boundary corrupts it
  was not measured this cycle, and an unmade measurement is not a clean
  one.

## Status

Costed one full round of reviewer quota for nothing. Carried into the 0.23.0
debate as a proposed addition to the release, since it is transport contract
text and the cycle is already editing `SKILL.md`.
