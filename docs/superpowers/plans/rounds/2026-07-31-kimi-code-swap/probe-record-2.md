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

Agent file: the five-tool allowlist, the full sixteen-name denylist including
`CronList`, and `subagents: []`. System prompt body 431 characters.

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

## Still unmeasured

- The cp1252 output hazard. It gates only whether a documentation bullet is
  deleted, so it does not block the contract's structure.
- Whether per-session files can be replaced and regrow past a captured offset.
  Sol round 2 is right that length-plus-absence does not prove prefix identity;
  the plan should capture a hash of the pre-call prefix rather than trusting
  length alone.
- Record cardinality for a review that uses far more tool calls than these did.
  The counts above scale with the tool loop, which is exactly why the corrected
  rule bounds `llm.request` from below rather than fixing it.
