# Live probe — resume transport, prompt recording, and extraction safety

**Date:** 2026-08-03. **Client:** `codex-cli 0.144.1`.
**Hosts:** Windows PowerShell `5.1.26100.8875` and PowerShell 7.
**Wrapper under test:** `C:\Users\Brandon\AppData\Local\npm-global\codex.ps1`.
**For:** backlog item 20, and the codex-side brief binding raised in plan round 2.

Written because both reviewer lanes refused, correctly, to fold an earlier
version of this into a verdict: the measurement existed only inside the brief.
**A measurement only its author can see is not evidence.**

Amended after plan round 2 to add the client version, spell out the part-1
fixture, narrow one overwide sentence, and add parts 3 and 4, which answer the
one freeze blocker both lanes named.

## Part 1 — argument splatting, no API calls

`codex` on Windows resolves to the npm wrapper, whose operative line is:

```powershell
& "node$exe" "$basedir/node_modules/@openai/codex/bin/codex.js" $args
```

Splatting `$args` to a native command is host-dependent. The fixture: an
`echoargs.ps1` printing `ARG[n]=` per received argument and a `COUNT=`, invoked
through a `wrapper.ps1` whose only body is
`& powershell.exe -NoProfile -File "$PSScriptRoot/echoargs.ps1" $args`. Each host
then ran `& wrapper.ps1 resume SESSIONID $b` with `$b` a single string.

| `$b` | Windows PowerShell 5.1 | PowerShell 7 |
|---|---|---|
| `Refute the claim that "Show Gems" is off by default.` | 2 args, quotes stripped, `COUNT=4` | intact, `COUNT=3` |
| `The flag is "unmeasurable" today.` | **`COUNT=3`, quotes silently GONE** | intact, `COUNT=3` |

**The second row is the serious half.** When the quoted span contains no space
the argument count does not change, so nothing fails.

## Part 2 — the real client, one seeded session, both forms

Seed on `pwsh`, effort low, prompt `Reply with exactly: SEED-OK`: exit 0, reply
`SEED-OK`, `session id: 019fca2c-86d1-75e0-9609-cb4a02bf6436`.

Both resumes below ran that same id under **Windows PowerShell 5.1**, against a
brief carrying both quote shapes (`Token A: "Show Gems"`, `Token B:
"unmeasurable"`, `Token C: plain`).

### 2a. The form SKILL.md documents today — POSITIONAL

`... --output-last-message $Reply resume $Sid $brief`

- **exit 2**
- `node.exe : error: unexpected argument 'Gems`, raised from `codex.ps1:24`,
  the splatting line
- **no reply file written**

### 2b. The proposed form — STDIN

`Get-Content -Raw $Brief | codex exec ... resume $Sid -`

- **exit 0**
- header echoed `model: gpt-5.6-sol`, `sandbox: read-only`,
  `reasoning effort: low`, and the seeded `session id:` — resumed, not fresh
- reply, verbatim: `"Show Gems" "unmeasurable" plain`

**Narrowed after review, then re-widened by measurement.** An earlier draft said
the quotes were "delivered intact". At that point the only observation was a
REPLY reproducing them, which is consistent with delivery but does not prove it.
Part 3 closes that gap for this exact brief: the client's own record of the
received prompt is 215 characters, matches the brief under canonicalization, and
contains the double-quote character. Delivery is now measured, not inferred.

## Part 3 — the codex lane DOES record the prompt it received

The backup lane binds its brief by hashing it against the recorded prompt
(`references/backup-lane.md`, region `brief-hash-binding`). Nothing in the repo
established a codex equivalent, and under the stdin form the prompt is not in
argv either. Measured rather than assumed.

**3a. The transcript echo.** The `> <transcript-file> 2>&1` capture contains the
prompt after the header's `user` line. Against plan round 1's brief: brief 7338
chars, echoed 7339, and `echoed.strip() == brief.strip()` is **True**. The
one-character difference is trailing whitespace.

**3b. The session rollout, which is the sounder source.** codex writes
`~/.codex/sessions/<yyyy>/<mm>/<dd>/rollout-<timestamp>-<session-id>.jsonl`,
named with the same session id the header reports. Walking it for `role: user`
objects and concatenating their `text` fields, under UTF-8 with CRLF normalized
to LF plus a trailing-whitespace strip:

| session | user-role objects | the round's brief |
|---|---|---|
| plan round 1 (`019fca2e`) | 2 | object 2, 7340 chars, **matches** |
| seeded + quoted resume (`019fca2c`) | 3 | object 3, 215 chars, **matches**, and contains `"` |
| adversarial (`019fca3d`) | 2 | object 2, 376 chars, **matches** |

**What this establishes.** A codex-side brief-delivery binding is feasible, and
it is a CLIENT-ECHO binding: it proves what this client recorded, never what the
server or the model received. That vocabulary matters and the repo already
applies it to route metadata.

**What it does NOT establish.** The first `role: user` object is never the brief
— it was 1532 characters in one session and 4209 in another, so it is neither
fixed in size nor identifiable by position alone. A rule saying "hash the
recorded prompt" is underspecified in exactly the way the kimi rule avoided by
naming `turn.prompt` `input[]`. The codex rule must identify WHICH element is
the round's own prompt by structure, and must FAIL CLOSED when it cannot
identify exactly one.

Not measured: whether the rollout path or schema is stable across codex
versions. It is version-coupled by nature, which is what the drift watch is for.

## Part 4 — prompt text CAN shift a transcript scrape's boundary

Raised by the primary lane in plan round 2: a parser that locates the prompt by
scanning transcript text can be steered by the prompt itself. Measured.

A brief was dispatched whose body contains inert payload lines shaped exactly
like transcript delimiters — a `--------` rule, bare `user` and `codex` lines,
`model:`, `provider:`, `sandbox:`, `reasoning effort:`, a `session id:` line
carrying all zeroes, and `tokens used:`.

**The transcript is attackable.** `^session id: ` now matches TWICE:

```
019fca3d-2220-7402-a297-9841bb21f2ba   <- the real header
00000000-0000-0000-0000-000000000000   <- from the payload
```

A parser taking the last match, or matching anywhere, reads the value the brief
chose. This retroactively shows the existing "check the FIRST `model:`,
`provider:` and `reasoning effort:` lines" discipline is load-bearing rather
than stylistic, and that it is the only thing standing between a scrape and an
attacker-chosen route.

**The rollout is immune by construction.** The same payload produced ONE
`role: user` object whose text matches the brief exactly. Delimiter-shaped lines
are text inside a JSON string; they cannot create a record boundary.

**Conclusion for the binding's design.** Read the rollout, do not scrape the
transcript. The immunity is structural, not a parser that got the escaping right.

## Part 5 — the exact rollout record shape

Added after plan round 3. The primary lane refused the freeze because parts 3
and 4 said the round's prompt must be "identified by structure" without naming
the structure, which is a placeholder standing where a runtime contract belongs.
Measured on `codex-cli 0.144.1`, session `019fca2e`, after three rounds.

**The rollout is CUMULATIVE and append-only across resumes.** The same file held
272 rows after round 1 and 325 after round 3, at 1,139,681 bytes. Each resumed
call appends; nothing rewrites. This is what makes a byte-offset boundary sound.

**The identifying structure**, stated as the four conditions that hold together:

```
row.type            == "response_item"
row.payload.type    == "message"
row.payload.role    == "user"
every row.payload.content[] element has type == "input_text"
```

The prompt text is the in-order concatenation of those elements' `text` fields.

**Verified across all three rounds of one session:**

| round | brief chars | rollout row | match |
|---|---|---|---|
| 1 | 7338 | 8 | yes |
| 2 | 6066 | 171 | yes |
| 3 | 5641 | 279 | yes |

Exactly one matching row per round, and no round's brief matched any other
round's row.

**Do NOT identify the record by content-element count.** The instructions
preamble at row 5 carries 2 `input_text` elements and each brief carried 1,
which makes element count LOOK like a discriminator on this sample. It is not
one: nothing observed here prevents a client from splitting a long prompt across
elements. The sound discriminator is the one the primary lane specified —
exactly one such record WITHIN THE CURRENT-CALL BYTE SLICE — and the cumulative
append-only behaviour above is what makes that slice definable.

**Still unmeasured, and it belongs to the drift watch:** whether the rollout
path, the four-condition shape, or the append-only behaviour is stable across
codex versions. The binding fails closed on anything it cannot identify, so a
schema change degrades to a loud failure rather than a silent pass.

## What is still NOT measured

- **The backup lane's runtime behaviour.** Both kimi forms pass the payload as
  `-p "<brief>"` and `kimi.exe` is a native PE32+ executable, so they are
  STRUCTURALLY exposed to a related class. But the codex defect measured here is
  specifically an npm wrapper splatting `$args` to node; a direct native
  invocation is a different surface. Plausible, not established, and both
  reviewer lanes corrected an earlier draft that called it the same mechanism.
  It is moot for LOUDNESS regardless, because the kimi lane's brief-hash binding
  already fails the round on a mismatch.
- **Whether every 5.1 failure is loud.** Part 1 shows it is not. Part 2a
  happened to use a quoted span containing a space. No silent real-client
  corruption was provoked end to end.
- **Whether a safer non-positional prompt transport exists for kimi-code.**

## Reproduction

Drivers are session scratchpad and deliberately not committed: the repo is
public and they carry local absolute paths. Every command above is stated in
full. The inputs are a seeded session id, a brief containing one quoted span
with a space and one without, and for part 4 a brief containing delimiter-shaped
payload lines.
