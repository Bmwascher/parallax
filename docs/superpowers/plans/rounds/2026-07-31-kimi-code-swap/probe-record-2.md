# kimi-code probe record 2 — record cardinality and the gated unknowns

Measured 2026-07-31, kimi-code 0.31.1, Windows. Prompted by Sol plan-debate
round 2, which challenged the per-round evidence rule's assumed record
cardinality. The challenge was correct and the measured answer is worse than
either side supposed: revision 2's rule fails a clean round 1 AND every
resumed round.

Six model calls. All in an isolated `KIMI_CODE_HOME` under the session
scratchpad, against a throwaway git workspace, never the real tree.

## Setup

A workspace built so a real review MUST use tools: `PLAN.md` with two numbered
requirements, and `src/parser.py` and `src/config.py` each violating one. Two
canary skills planted, one per documented project discovery root:
`.kimi-code/skills/canary/SKILL.md` and `.agents/skills/canary2/SKILL.md`, each
instructing the model to prefix every reply with a distinct token.

Agent file: the five-tool allowlist, the full denylist including `CronList`,
and `subagents: []`. System prompt body 431 characters.

**Count corrected 2026-07-31** after the fable-reviewer whole-branch review:
this line first said "sixteen-name", which agrees with neither the plan's
seventeen-name denylist nor `probe-record.md:151-155`, whose enumeration lists
21 distinct tools and does not include `CronList` at all. `CronList` entered
during Sol plan-debate round 2 as a built-in found in neither list. The bare
count is removed here rather than guessed at; the plan's Task 5 Step 3b
re-enumerates the inventory from the client and writes the reconciled result
below.

## FINDING 1 — record cardinality. The rule in revision 2 is wrong.

Counts taken from `agents/main/wire.jsonl`, sliced at the pre-call offset.

| record | fresh round (tool-using) | resumed round (tool-using) |
| --- | --- | --- |
| `config.update` | **2** | **0** |
| `tools.set_active_tools` | 1 | **0** |
| `llm.tools_snapshot` | 1 | **0** |
| `permission.set_mode` | 1 | **0** |
| `turn.prompt` | 1 | 1 |
| `llm.request` | **4** | **2** |
| `usage.record` | 4 | 2 |
| `context.append_loop_event` | 24 | 8 |

Revision 2 required "exactly one of each" of `config.update`,
`tools.set_active_tools`, `llm.tools_snapshot` and `llm.request` inside each
call's slice. Measured against that rule:

- Round 1 fails twice: `config.update` is 2 and `llm.request` is 4.
- Every resumed round fails three times: three of the four records do not
  appear in the slice at all.

`llm.request` count tracks the tool loop — one per model round trip — so it is
inherently variable and can never be pinned to a constant.

**Session storage NAMING, added 2026-07-31 after Sol plan-debate round 7 noted
that the earlier record wrote `<session-id>` generically and never established
the prefix the plan's inventory rule depends on.** Read from disk:

```
sessions/
  wd_ws_3aa434a78a27/                                  <- workspace container
    session_1a2cfd21-fba0-4e99-891e-fd681edc1267/      <- session leaf
    session_ec645aec-2c14-47ad-a975-3d469d0464b4/      <- session leaf
```

Containers are `wd_`-prefixed, leaves are `session_`-prefixed, and the id the
client prints on its `To resume this session:` line is the leaf's name exactly.
Both sessions in this home share ONE container, so the container is created per
WORKSPACE and not per session: only a debate's first call in a given workspace
creates one. That is why a first call adds two directories and later calls add
one, and why the inventory rule counts `session_` leaves only.

**Record ORDER, added 2026-07-31 after Sol plan-debate round 4 pointed out that
the counts above establish no ordering.** Read from the same session's
`wire.jsonl`, a fresh session's first six records are, in order:

```
metadata
config.update
tools.set_active_tools
config.update
permission.set_mode
turn.prompt
```

So a fresh call's slice opens with `metadata`, NOT with a `config.update` or
any "session-creation" record — the plan's first wording of the slice-boundary
rule named the wrong record. A resumed call's slice opens with `turn.prompt`.

**The corrected structure, which the plan must adopt.** Records fall into two
classes, and one rule cannot cover both:

- **Session-scoped, emitted once at session creation**: `config.update` ×2
  (the first carries `profileName` and `systemPrompt`, the second carries
  `modelAlias` and `thinkingEffort`), `tools.set_active_tools` ×1,
  `llm.tools_snapshot` ×1, `permission.set_mode` ×1. Verify these ONCE, in the
  round-1 slice, which is the only slice that contains them.
- **Per-call**: exactly one `turn.prompt`; one or more `llm.request`, with
  EVERY one carrying the canonical provider, model alias and effort; and
  exactly one new `llm config` line in the per-session log.

The per-session log is the cleaner per-call surface: it emitted exactly one
`llm config` line per call in every session measured, one at `turnStep=0.1`
and one at `turnStep=1.1` after the resume, regardless of how many
`llm.request` records the tool loop produced.

## FINDING 2 — `systemPromptChars` equals the agent body length exactly

The agent file's body is 431 characters and every `llm config` line across
every session read `systemPromptChars=431`. That is a cheap integrity check on
the system prompt that needs no hashing, and it is also how finding 3 below was
established.

`toolCount=5` held on every call of every session, fresh and resumed.

## FINDING 3 — `--skills-dir` is NOT the control. Nothing loads either way.

Ran the identical configuration WITH and WITHOUT `--skills-dir`, both with the
two canaries planted:

- With `--skills-dir <empty>`: `systemPromptChars=431`, no canary token in the
  reply, no skill record anywhere in `wire.jsonl`.
- WITHOUT `--skills-dir`: `systemPromptChars=431`, and asked to list every
  Skill available to it, the reviewer answered `NONE`.

The two runs are indistinguishable, so `--skills-dir` cannot be credited with
suppressing anything here — nothing was ever loaded. The plausible mechanism is
that `Skill` is absent from the agent's `tools:` allowlist, so skills are not
advertised to a custom agent that cannot invoke them.

**What this means for the contract.** `--skills-dir` is a mitigation whose
effect is UNMEASURABLE in this configuration, not a control, and the contract
must not describe it as one. The load-bearing controls are the tool allowlist
excluding `Skill`, and preflight-3 remediation removing the files from the
mirror. Keep passing `--skills-dir` — it costs nothing and covers the case
where a future release advertises skills regardless — but claim nothing for it.

Only tested with a custom `--agent-file`. A default-agent run may behave
differently; the lane never uses one.

**The files are still an injection surface by a different route.** In round 1
the reviewer READ both canary SKILL.md files with its `Read` tool while
surveying the workspace, recognized them as injection attempts, and declined
on its own judgment. Prompt text is never a control, and this is precisely why
preflight-3 remediation removes the files rather than trusting the reviewer to
ignore them.

## FINDING 4 — `subagents: []` works

`state.json`'s `agentProfileCatalog.profiles[0].subagents` resolved to an empty
array. The default without the key was
`agent, coder, explore, plan, parallax-readonly-reviewer`. Subagent containment
is now a control in its own right rather than resting on the `Agent` and
`AgentSwarm` denial alone.

## FINDING 5 — the effort pin works; thinking-enabled has no differentiator

Two homes, each dispatched the same trivial prompt.

- `default_effort = "low"` produced `thinkingEffort=low` in both the log line
  and `llm.request`. So effort IS pinned by the home and confirmed per call.
  The contract may claim effort is verifiable by construction.
- `[thinking] enabled = false` produced `thinkingEffort=high` and
  `thinkingKeep=all` — byte-identical to `enabled = true`. No field in the log
  or in `wire.jsonl` differs.

So thinking-enabled is CONFIG-ASSERTED AND NOT RUNTIME-VERIFIED. The contract
must say exactly that and must not list thinking beside effort as though both
were confirmed per call. The model's `capabilities` include `always_thinking`,
which may be why the key has no observable effect, but that is unconfirmed.

## FINDING 6 — of four flags tested, resume rejects only the agent file

Four flags were tested, not every flag the CLI has. Nothing below establishes
anything about a flag outside this set. Tested for free against a nonexistent
session id, so flag validation is reached without a model call:

| flag with `-r` | result |
| --- | --- |
| `-m` | accepted — failed only on session lookup |
| `--skills-dir` | accepted — failed only on session lookup |
| `--add-dir` | accepted — failed only on session lookup |
| `--agent-file` | REJECTED at parse time |

The rejection message states the mechanism: `Cannot combine
--agent/--agent-file with --session/--continue: the agent is bound at session
creation`.

So the lane should re-pin `-m` and `--skills-dir` on every resume. It is free,
and it narrows the version-bound inheritance risk Sol raised in round 2 to the
one flag that genuinely cannot be re-pinned.

## Task 4 probes — cp1252 output, toolsHash equality, per-session rotation

Measured 2026-07-31, kimi-code 0.31.1, Windows, same day as the findings
above. Two isolated `KIMI_CODE_HOME` directories, built with
`tools/new-kimi-lane-home.ps1 -Model kimi-code/k3-256k -Effort high`, under
the session scratchpad, never in the real tree and never in this repo. Both
removed with `-Remove` at the end of this work; see the removal log below.

**Setup note — a live bug in the home-builder's rendered `config.toml`.**
`new-kimi-lane-home.ps1`'s template writes `default_model`, `extra_skill_dirs`
and `telemetry` AFTER the `[models."<id>"]` table header and before the next
`[thinking]` header, with no table header of their own in between. Under TOML
rules a bare key-value pair after a table header belongs to THAT table until
the next header, so all three keys land inside `models."kimi-code/k3-256k"`
rather than at the document root. `kimi doctor` reports the file valid (it is
syntactically valid TOML) and `kimi provider list` reports the provider and
model resolved, but a plain `-p` dispatch with no `-m` failed every time with
`error: failed to run prompt: No model configured.` Every dispatch below
therefore passed `-m kimi-code/k3-256k` explicitly on the command line as a
caller-side workaround. This is a finding about the tool built in an earlier
task, not a change to it — Task 4 touches only this file under `docs/`, so no
script was edited to fix it. One throwaway "reply OK" call was spent
confirming the workaround before the real cp1252 probe was run with it; that
call is included in the dispatch count below.

### Step 1 — cp1252 console output hazard: NOT OBSERVED

Console forced to cp1252 with `chcp 1252` in a `cmd.exe` batch script, then
`KIMI_CODE_HOME` set to the isolated home and:

```
kimi.exe -p "Reply with exactly one line containing only three characters
and nothing else, in this order: an em dash (Unicode code point U+2014), a
rightwards arrow (Unicode code point U+2192), and the katakana letter A
(Unicode code point U+30A2). Do not output any words, spaces, quotes, or
explanation before or after them - output only those three characters
concatenated, nothing else." -m "kimi-code/k3-256k" --agent-file <read-only
agent file> > cp1252-out.bin 2> cp1252-err.txt
```

Result: `EXITCODE=0`. Redirected stdout is 15 bytes; hex dump:

```
e280 a220 e280 94e2 8692 e382 a20a 0a
```

Decoded: `e2 80 a2` (the CLI's own `•` reply-line prefix) `20` (space)
`e2 80 94` = U+2014 EM DASH, `e2 86 92` = U+2192 RIGHTWARDS ARROW,
`e3 82 a2` = U+30A2 KATAKANA LETTER A, then two newlines. All three
requested characters are present, byte-exact valid UTF-8, and unaffected by
the console's active code page. Forcing `chcp 1252` before the dispatch did
not corrupt the redirected-to-file output and the process exited 0. This
gates Task 10's choice between deleting the Python UTF-8 guard and replacing
it with one describing this client — the measured answer supports deletion,
not replacement, for THIS hazard as tested (a single dispatch, three specific
characters, stdout redirected to a file).

### Step 1b — `llm.request.toolsHash` vs `llm.tools_snapshot.hash`: EQUAL

Free, offline, read from Step 1's own session `wire.jsonl`
(`sessions/wd_ws-cp1252_*/session_e8e29860-2060-4f86-94ad-c59cc6c35f2d/agents/main/wire.jsonl`,
no extra model call). The session held exactly one `llm.tools_snapshot`
record and one `llm.request` record (a single-turn, no-tool-call reply):

- `llm.tools_snapshot.hash` =
  `3d2530e113e94d4b1531edea8545bc8d2d505e381f3586948fd944eb5784597b`
- `llm.request.toolsHash` =
  `3d2530e113e94d4b1531edea8545bc8d2d505e381f3586948fd944eb5784597b`

The two strings are identical. **Verdict: EQUAL.** Per the brief, Task 6 rule
13 keeps the cross-record comparison as written; it does not need to fall
back to presence-and-nonempty-only.

### Step 2 — per-session log rotation: NOT OBSERVED up to 18,863 bytes

Second isolated home. One session, five initial cheap dispatches
(`kimi.exe -p "Reply with exactly one word: OK" -m "kimi-code/k3-256k"` for
the first call, `kimi.exe -c -p "Reply with exactly one word: OK" -m
"kimi-code/k3-256k"` continuing the same session for every call after),
`kimi-code.log` size read from disk after each call:

| call | log size (bytes) | delta from prior call |
| --- | --- | --- |
| 1 | 405 | (fresh session) |
| 2 | 876 | 471 |
| 3 | 1347 | 471 |
| 4 | 1818 | 471 |
| 5 | 2289 | 471 |

`R` (bytes per call) measured from these five, per the brief's method:
`(2289 - 405) / 4 = 471` bytes/call, exactly, across all four deltas.
Target depth = `min(16 MB, 40 x 471) = min(16777216, 18840) = 18840` bytes —
far short of 16 MB, so the full 40-dispatch hard budget was spent (not
stopped early) to reach the maximum depth the budget affords, per the
brief's instruction to state the achieved depth and stop there. Calls 6-40
continued the same session, checking for a `kimi-code.log.*` sibling and for
`kimi-code.log` shrinking after every call:

| call | size | call | size | call | size | call | size | call | size |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 6 | 2760 | 14 | 6540 | 22 | 10332 | 30 | 14123 | 38 | 17915 |
| 7 | 3231 | 15 | 7014 | 23 | 10806 | 31 | 14597 | 39 | 18389 |
| 8 | 3702 | 16 | 7488 | 24 | 11280 | 32 | 15071 | 40 | 18863 |
| 9 | 4173 | 17 | 7962 | 25 | 11754 | 33 | 15545 |  |  |
| 10 | 4644 | 18 | 8436 | 26 | 12228 | 34 | 16019 |  |  |
| 11 | 5118 | 19 | 8910 | 27 | 12702 | 35 | 16493 |  |  |
| 12 | 5592 | 20 | 9384 | 28 | 13176 | 36 | 16967 |  |  |
| 13 | 6066 | 21 | 9858 | 29 | 13649 | 37 | 17441 |  |  |

Per-call delta held at exactly 471 bytes for calls 1-10, then shifted to a
steady 474 bytes/call from call 11 onward (one call, 29, delta 473) — the
mechanism was not investigated (plausibly a field in the log line, such as
elapsed-ms or `turnStep`, gaining a digit), and this record states only what
was measured, not why. Every one of the 40 calls exited 0. **After all 40
calls: `kimi-code.log` is 18,863 bytes, no sibling matching
`kimi-code.log.*` exists (verified by a direct directory listing, not by
`Get-ChildItem -Filter`, which has a known Win32 `FindFirstFile` quirk where
a `"name.*"` filter also matches the bare `"name"` file — this false
positive was hit once, at call 6, and corrected before continuing), and the
file never shrank between any two consecutive calls.**

**Stated at exactly the width of the measurement:** no rotation was observed
up to 18,863 bytes (≈18.4 KB). The probe did NOT reach the 1 MB, 5 MB, or
10 MB thresholds — none of them. This is not evidence that rotation is
absent; it is evidence only up to the depth the 40-dispatch budget reached
at the measured growth rate. Task 7's freshness region hashes both files'
prefixes regardless, so this shallow negative result does not block it.

### Dispatch accounting for this section

- Step 1: 2 dispatches (1 throwaway "reply OK" call confirming the `-m`
  workaround, 1 the actual cp1252 probe).
- Step 1b: 0 dispatches (read from Step 1's `wire.jsonl`).
- Step 2: 40 dispatches (5 to measure `R`, 35 more to reach the achieved
  depth) — exactly the hard budget, never exceeded.
- Total for this section: 42 real model calls.

### Probe home removal

Both homes removed with `tools/new-kimi-lane-home.ps1 -Remove -Path <dir>`
after the measurements above were taken; both printed `removed <path>` and
exited 0. Confirmed with `Test-Path` afterward that neither directory (and
therefore neither `credentials/kimi-code.json` copy) exists on disk.

## Still unmeasured

- The real built-in tool inventory for 0.31.1, and specifically whether
  `CronList` exists. See the correction under Setup above.
- Whether per-session files can be replaced and regrow past a captured offset.
  Sol round 2 is right that length-plus-absence does not prove prefix identity;
  the plan should capture a hash of the pre-call prefix rather than trusting
  length alone.
- Record cardinality for a review that uses far more tool calls than these did.
  The counts above scale with the tool loop, which is exactly why the corrected
  rule bounds `llm.request` from below rather than fixing it.

**Closed by Task 4, 2026-07-31:** the `llm.request.toolsHash` /
`llm.tools_snapshot.hash` equality (EQUAL — see above), the cp1252 output
hazard (not observed, single dispatch, three specific characters), and
per-session log rotation (not observed up to 18,863 bytes / 40 calls; the 1,
5 and 10 MB thresholds were not reached). See the new section above for
exact commands, output, and the dispatch count spent.
