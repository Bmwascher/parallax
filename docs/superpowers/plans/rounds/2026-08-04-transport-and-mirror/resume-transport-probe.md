# Live probe — the `resume` dispatch and embedded double quotes

Measured 2026-08-03 by the session, on this machine, for backlog item 20.
Written because the Kimi lane correctly refused to fold this into a verdict at
plan round 1: the measurement existed only inside the brief, and the repo
attributed all real-client evidence to the earlier KitnEssentials field report
and a different session. **A measurement only its author can see is not
evidence.** This file is that measurement, recorded so it can be read.

This does NOT replace the field report. It is an independent re-measurement,
and it extends the report in one direction the report did not cover: the same
seeded session driven through BOTH dispatch forms on the host where the defect
lives.

## What was under test

`skills/multi-model-verify/SKILL.md:237` documents the resume dispatch with the
brief as a POSITIONAL argument:

```
codex exec ... --output-last-message <reply-file> resume <SESSION_ID> "<rebuttal-brief>" > <transcript-file> 2>&1
```

Round 1 pipes the brief on stdin (`SKILL.md:192`) and is unaffected. Only
`resume` uses the positional form.

## Part 1 — argument splatting, no API calls

`codex` on Windows resolves to `C:\Users\Brandon\AppData\Local\npm-global\codex.ps1`,
which splats `$args` to node. An argument-echoing stand-in was driven through a
wrapper that splats identically, passing ONE string argument containing double
quotes.

| brief content | Windows PowerShell 5.1 | PowerShell 7 |
|---|---|---|
| `Refute the claim that "Show Gems" is off by default.` | splits into 2 args, quotes stripped, `COUNT=4` | intact, `COUNT=3` |
| `The flag is "unmeasurable" today.` | **`COUNT=3`, quotes silently GONE** | intact, `COUNT=3` |

Hosts: `powershell.exe` 5.1.26100.8875 and `pwsh.exe` 7.

**The second row is the serious half.** When the quoted span contains no space
the argument count does not change, so nothing fails. Read together with part 2,
the loud failure is luck of the CLI's arity, not a guarantee.

## Part 2 — the real client, one seeded session, both forms

Seed, `pwsh`, effort low, prompt `Reply with exactly: SEED-OK`:

- exit 0, reply `SEED-OK`
- `session id: 019fca2c-86d1-75e0-9609-cb4a02bf6436`

Both resumes below ran that same session id, under **Windows PowerShell 5.1**
(`5.1.26100.8875`), against a brief carrying both quote shapes:

```
Token A: "Show Gems"
Token B: "unmeasurable"
Token C: plain
```

### 2a. The form SKILL.md documents today — POSITIONAL

```
codex exec --sandbox read-only -m gpt-5.6-sol -c model_reasoning_effort=low --output-last-message $Reply resume $Sid $brief
```

- **exit 2**
- stderr: `node.exe : error: unexpected argument 'Gems`, raised from
  `npm-global\codex.ps1:24`, the line that invokes node with the splatted args
- **no reply file written**

### 2b. The proposed form — STDIN

```
Get-Content -Raw $Brief | codex exec --sandbox read-only -m gpt-5.6-sol -c model_reasoning_effort=low --output-last-message $Reply resume $Sid -
```

- **exit 0**
- header echoed `model: gpt-5.6-sol`, `sandbox: read-only`,
  `reasoning effort: low`, and `session id: 019fca2c-86d1-75e0-9609-cb4a02bf6436`
  — the seeded session, resumed, not a fresh one
- reply, verbatim: `"Show Gems" "unmeasurable" plain`

The reply is the load-bearing part. The brief asked the model to echo the three
tokens exactly, including every double-quote character. Both quoted tokens came
back WITH their quotes, on the host where 2a fails and where part 1 shows the
no-space case losing them silently.

## What this establishes, and what it does not

**Establishes.** On Windows PowerShell 5.1 the documented positional form fails
against the real client with a quoted brief, and the stdin form succeeds on the
same host and the same session with the quotes delivered intact.

**Does NOT establish.** That every 5.1 failure is loud — part 1 shows it is not,
and part 2a happened to use a quoted span containing a space. No silent
real-client corruption was observed directly, because provoking it would mean
dispatching a brief this session knew to be altered and then trusting the reply
to reveal it; part 1 measures that mechanism at the argument layer instead.

**Not measured at all.** Whether the backup lane has the same exposure. That
lane passes its whole brief through `-p "<brief>"`, which is the same positional
shape (`references/backup-lane.md`, Transport). It was raised in plan round 1
and is not answered here.

## Reproduction

Drivers are session scratchpad and deliberately not committed: the repo is
public and these carry local absolute paths. The commands above are complete
enough to re-run; the only inputs are a seeded session id and a brief file
containing a quoted span with a space and one without.
