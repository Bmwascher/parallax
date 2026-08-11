# 0.24.0 debate record — the reviewer's tool surface, the agy contracts

Backlog items 7 and 11. Branch `0.24.0-tool-surface-agy-drift`.

Reviewer lane: codex `gpt-5.6-sol`, effort `high`, sandbox `read-only`,
isolation flags plus the probe-generated skill-disable override.

## Meters, declared before round 1

- ROUND CAP: 4 consecutive CONTESTED exchanges. Termination requires an
  adjudicated DRY round.
- TOTAL FIX-VERIFY BUDGET: 6 units, one unit = one dispatched exchange.
- The two meters are separate (backlog item 24, closed 0.22.0).

## Preflight

`tools/codex-context-probe.ps1 -WorkDir <repo> -SuppressSkills
-OverrideOut ... -Json`, run before round 1:

```
status: clean, skills_before: 29, skills_after: 0,
repo_scoped: 0, plugin_cache_scoped: 0, unknown_scoped: 0,
project_agents_md: false, global_agents_md: true,
global_agents_md_path: C:\Users\Brandon\.codex\AGENTS.md
override_sha256: 180f09f5...f432bb8
```

The global `AGENTS.md` survives a clean probe by design and is recorded
here rather than removed. Per `client-probe-scope-limit`, a clean probe is
not full reviewer isolation, and item 7 is the reason.

## Round 0 — VOID, and the cost was real

Round 1 was dispatched once before this record existed, answered, exit 0,
a 15768-byte reply on disk. It was **discarded unread**.

`-PriorState` for `tools/read-codex-round-evidence.ps1` is an inventory of
the codex sessions root that must be captured BEFORE the dispatch. It was
not. Rebuilding it afterwards is not sound: Windows tunnels file creation
times, backlog item 29 is open on the ancestry walk having no
creation-time ordering guard, and any reconstruction that excludes "the
new one" assumes the answer it is meant to establish.

So the reply was never opened, and the round was re-run at full cost.

**This produced backlog item 35.** `SKILL.md` prints the round-1 dispatch
at lines 178-189 and states the pre-dispatch inventory requirement at
lines 229-232, as a subordinate clause about a parameter, roughly fifty
lines later. A session executing the skill in order dispatches first and
learns second. Every other pre-dispatch obligation in that step - the
enumeration, the mirror, the client probe, the override hash - is written
as an ordered step before the command that consumes it. This one is not.

**A second, smaller process defect from the same round.** The round-1
brief states `HEAD ef428c3`. Two commits landed between writing it and
dispatching it, so the reviewer opened with "the live branch was already
beyond the stated `ef428c3` and advanced again during review", and froze
its adjudication to `99a2099` itself. It adapted correctly and nothing was
lost, but the brief asserted a head the dispatch never verified. Worth
folding into item 35's fix, since it is the same family: bookkeeping the
dispatch depends on, written where nothing checks it.

## Round 1 — five FIXes, five PASSes, not dry

Brief: `plan-brief-r1.md`. Reply: `plan-reply-r1.txt`.
Binding: clean (`-Fresh`, session `019ff252-bb4d-7d43-816b-e3e9ca5f31a5`,
rollout boundary 641954 bytes).
Route verified from the transcript: `gpt-5.6-sol`, `openai`, `read-only`,
`high`.

Every FIX was a claim of the session's that was wider than its evidence,
and every one was re-verified against the cited files before being
accepted. That is the invariant this repo puts first, failing five times
in one round on its own plan.

| # | subject | verdict |
|---|---|---|
| 1 | the app-server surface exists and is bounded | PASS |
| 2 | `-c mcp_servers={}` is inert | PASS |
| 3 | removed and crashed are indistinguishable | PASS |
| 4 | the two-pass shape is a positive control | **FIX** |
| 5 | three agy contracts have no check anywhere | **FIX** |
| 6 | the transcript narrowing is stated, not smuggled | PASS |
| 7 | nothing has measured `allowNonWorkspaceAccess` | **FIX** |
| 8 | no version floor for agy | PASS |
| 9 | the `.codex` gap is newly found | **FIX** |
| 10 | two standing surfaces carry the false premise | **FIX** |

**FIX 4.** Pass 1 calibrates the INSTRUMENT under baseline conditions. It
says nothing about the MCP subsystem under pass-2 conditions, and an empty
pass 2 stays observationally identical to the deliberate-crash arm. So the
presence direction is a control and the absence direction is a mitigation.
The pair is not a positive removal control and may not be called one.

**FIX 5.** `agents/flash-implementer.md:45-59` already runs three of item
11's contracts as a per-dispatch preflight, `:100-105` bans any
approval-bypass flag, and `:81-92` blocks a missing transcript after the
run. The gap is that the weekly drift watcher covers none of them and the
doctor mirrors two, so a drift lands mid-build on a frozen plan rather
than before it. Safe, but late.

**FIX 7.** `docs/superpowers/plans/2026-07-25-flash-implementer.md:590-603`
records the 0.12.0 build setting the key to `false`, watching a
trusted-workspace print-mode write get soft-denied, restoring `true`, and
documenting it as required on agy 1.1.7. `true` is a measured lane
requirement. The residual is only what it permits OUTSIDE the workspace on
1.1.12, and item 11's security contract stays explicitly UNMEASURED.

**FIX 9.** `references/model-prompting-notes.md:288-291` already says
"'.codex/' stays unswept — unprobed; probe before adding". Reconfirmed,
not found. The half of the session's claim asserting that codex loads
project-local skills from there while untrusted is RETRACTED: it was the
client's own description, never a measurement, and no canary artifact was
kept.

**FIX 10.** Two more surfaces carry the false premise: `README.md:186-200`
states it independently, and
`evals/multi-model-verify/test_multi_model_verify.py:762-782` pins the
SKILL region VERBATIM as one multi-line literal, so editing the region
without the pin turns a documentation fix into a red suite.

**Design questions, answered.** No sound survivor control exists in the
measured configuration, because after the flags `node_repl` is the only
server left and shape A removes the only candidate. Shape A ships anyway,
on both the fresh AND resume dispatches, as risk reduction with an empty
allowlist. No agy version floor; 1.1.12 is an observed baseline, not a
compatibility boundary. Watch `allowNonWorkspaceAccess`, do not flip it.

Applied at `4be7eee`.

## Round 2 — confirming

Brief: `plan-brief-r2.md`. Asks whether any correction reintroduced the
defect it was written to remove, whether Task 3's second sweep is
exhaustive where the first was not, and whether the round is DRY.
