# Probe record: the Kimi lane's inline brief on both PowerShell hosts (backlog item 51)

Date: 2026-08-22 (local, CDT).
Hosts: Windows PowerShell **5.1.26100.9168** and PowerShell **7.6.5**, both
read from `$PSVersionTable.PSVersion` at probe time.
Repo: `main` at `a3134dc`, working tree clean; branch
`item51-inline-brief-transport` cut from it.
Plugin cache 0.27.0, `gitCommitSha` `aca2895`, session started after that
install.
Driver: Opus 5, this session. No quota was spent: the reviewer client was
NOT called.

## Why this probe exists

Backlog item 51 records a REPORT, relayed from another session, that the
backup lane's INLINE brief is silently corrupted under Windows PowerShell
5.1 and needs pwsh 7. It was never measured here. Item 51's own "shape of
a fix" requires a measurement on both hosts, with a non-ASCII brief, read
back from what the CHILD received rather than what the console showed.

`skills/multi-model-verify/references/model-prompting-notes.md`, region
`brief-encoding-transport`, closes by saying the backup lane passes its
brief as an ARGUMENT rather than through a pipe, "so this mechanism does
not apply there and nothing here is claimed about it". That silence was
honest. This probe fills it.

## What was measured, and what was deliberately not

**Measured:** the bytes that arrive in the child process's argument vector
when a brief file is read and passed inline as `-p <brief>`, exactly the
shape `references/backup-lane.md` documents for `<kimi-code-binary>`.

**Not measured:** the real `kimi.exe`. The child here is a Python stub that
records `GetCommandLineW` and its own `argv`. That is deliberate. The raw
command line is what THIS side handed the operating system, so a corruption
visible there is ours no matter how the client decodes. A stub also costs
no quota and no lane lock. What a stub cannot settle is whether `kimi.exe`
introduces a FURTHER corruption of its own on an intact command line; that
remains unmeasured and is stated here so the absence is not silence.

## Probe design

The brief file is UTF-8 with NO byte order mark, the shape a scratchpad
brief actually has. Payload, three lines:

```
a—b
q="dq" p='sq' $var `bt` %pct%
ü ß … ✓
```

`✓` (U+2713) is chosen because it has no cp1252 representation at all, so
an ANSI round trip cannot hide by accident. A second brief carries an ODD
number of double quotes, which is what a real brief quoting a snippet of
code produces.

Three spellings, each run under BOTH hosts:

| Spelling | Read | Dispatch |
|---|---|---|
| S1 | `Get-Content -Raw` | `& <exe> ... -p $b` |
| S2 | `[IO.File]::ReadAllText` with a strict UTF-8 decoder | `& <exe> ... -p $b` |
| S3 | same strict decoder | `ProcessStartInfo.Arguments`, command line built with explicit `CommandLineToArgvW` escaping |

## Result: the report REPRODUCES, and there are TWO independent defects

| Spelling | Windows PowerShell 5.1 | PowerShell 7 |
|---|---|---|
| S1 balanced quotes | **corrupt** — non-ASCII mojibaked AND quotes lost | exact |
| S2 balanced quotes | **corrupt** — quotes lost, non-ASCII intact | exact |
| S1/S2 odd quotes | **shattered** — brief split across 4 argv elements | exact |
| S3 balanced quotes | exact | exact |
| S3 odd quotes | exact | exact |

### Defect 1: the READ, on 5.1 only

`Get-Content -Raw` decodes a no-BOM UTF-8 file with the ANSI code page.
The three-line brief above arrives as:

```
61 c3a2 e282ac e2809d 62 ...        (a â € ” b)
```

against an expected `61 e28094 62` (`a — b`). This is the FIRST HALF of
item 30's defect, reaching this lane through a different door. Item 30's
second half — `$OutputEncoding` defaulting to us-ascii — is pipe-specific
and does NOT apply here: with the strict decoder in place, S2 delivered
every non-ASCII character intact through the argument vector on 5.1,
including `✓`.

### Defect 2: the ARGUMENT, on 5.1 only

Windows PowerShell 5.1 wraps a native argument containing spaces in double
quotes but does NOT escape double quotes already inside it. The raw command
line it built, read from `GetCommandLineW` in the child:

```
5.1:   -p "a—b\nq="dq" p='sq' ...\n"
7.6.5: -p "a—b\nq=\"dq\" p='sq' ...\n"
```

PowerShell 7 escapes them; 5.1 does not. The child's standard parser then
consumes the unescaped quotes as delimiters. With a BALANCED count they
vanish silently and the brief still arrives as one argument. With an ODD
count the brief is TORN INTO FOUR arguments and everything after the first
space boundary lands where no `-p` payload is read at all.

This defect is INDEPENDENT of the encoding one. Fixing the read alone —
which is what a reader of item 30's rule would naturally do — leaves it
firing, and it fires on pure ASCII.

### The 5.1-safe form EXISTS

S3 delivered both briefs byte-exact on both hosts. So the answer is not
forced to be a host requirement, which item 51 called the weakest available
answer. The escaping is the standard `CommandLineToArgvW` rule: double
every run of backslashes that precedes a quote, escape the quote, and
double a trailing backslash run.

```powershell
function Esc([string]$s) {
  $s = $s -replace '(\*)"', '$1$1\"'
  $s = $s -replace '(\+)$', '$1$1'
  return '"' + $s + '"'
}
```

## A third finding, not in item 51: the inline path has a hard ceiling

Measured while sizing the payload, on BOTH hosts identically:

| Brief size | 5.1 | 7 |
|---|---|---|
| 7938 chars | exact | exact |
| 29970 chars | exact | exact |
| 31995 chars | exact | exact |
| 32967 chars | **throws** | **throws** |
| 39933 chars | **throws** | **throws** |

The ceiling is the Windows command-line limit of 32767 characters, and it
covers the WHOLE line, not just the brief: the binary path, the flags, the
agent file path and the skills dir all spend from the same budget, and the
escaping above spends one more character per embedded quote.

This failure is LOUD — `The filename or extension is too long`, thrown
before the client starts — so it cannot be confused with a review result.
That matches what `backup-lane.md` already says: a brief that exceeds what
the inline transport carries is a transport failure to diagnose, not a
reason to switch to a pointer. What is new is the NUMBER, which the
contract does not state anywhere.

## What this says about item 31

Item 31 is the same class on the codex lane at `tools/check-drift.ps1:700`,
where the defective `Get-Content -Raw | codex exec` pipe still ships. This
probe does not measure that site. It does establish that the class is live
on two lanes at once and that only one of them has a brief-attribution
binding to notice.

## Residual limits

- The real `kimi.exe` was not called. An intact command line is necessary,
  not proven sufficient.
- Only two hosts, one machine, one code page (cp1252). A different ANSI
  code page changes defect 1's exact bytes, not its existence.
- The ceiling was bracketed between 31995 and 32967 characters, not
  bisected to the exact byte.
