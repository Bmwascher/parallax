# Diff debate, round 4

**Range base:** `8cc00d1345a75f164741f0ea847d86ea97546603`
**Head reviewed:** `0c22d60`
**Reviewer:** `gpt-5.6-sol`, provider `openai`, effort `high`, sandbox `read-only`
**Session id:** `01a00cb4-f0ae-7b21-8170-b8899674b64b`
**Brief digest (declared canonicalization):** `1eb685588f6700404865b66ed1af1f46e73f178fa21d18d72bedee0c711373b2`
**Prior state:** resume, 1581424 bytes
**Round-evidence binding:** clean - the reply was bound to the brief this side sent
before it was read.
**Verdict:** FIX

**What it found.** Crossed to the OTHER lane's binder, which no round had read. Four instances, two of them CLEAN on PowerShell 7 and refused on 5.1.

---

## Reviewer reply, verbatim

No. The Codex surfaces are now guarded, but the Kimi binder contains four reachable instances of the same class.

### 1. Singleton-array prior state — PowerShell 7 CLEAN

State: wrap an otherwise valid fresh Kimi prior state in a one-element JSON array:

```json
[{"kind":"fresh","knownSessionDirs":[]}]
```

`Read-PriorState` parses the text and immediately reads properties without establishing that the root JSON value was an object. On PowerShell 7, `ConvertFrom-Json` unwraps the singleton array, so `kind` and `knownSessionDirs` pass every subsequent shape check. [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:264) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:271) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:280)

This is the exact host divergence already documented and closed in the Codex binder: 5.1 retains the array, while PowerShell 7 returns its contained PSCustomObject. [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:469) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:474)

### 2. Singleton-array wire record — PowerShell 7 CLEAN

Slice: take the valid fixture’s `turn.prompt` line and replace it with:

```json
[{"type":"turn.prompt","input":[{"type":"text","text":"<the same brief>"}], ...}]
```

The wire reader parses the line, checks only for null and a `type` property, then runs ordinary per-record validation. It never checks either the raw leading character or that the parsed root is a PSCustomObject. [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:508) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:512) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:516)

On PowerShell 7 the array unwraps, `turn.prompt` is counted, and its unchanged text hashes normally. [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:809) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:904) [fresh-wire.jsonl](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/fixtures/kimi-round/fresh-wire.jsonl:6)

That contradicts the shipped contract’s rule that a malformed line is an attribution failure. [backup-lane.md](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/backup-lane.md:271)

### 3. Array-valued wire `type` — both hosts CLEAN

Slice: keep the record itself as an object, but change the valid prompt to:

```json
{"type":["turn.prompt"],"input":[{"type":"text","text":"<the same brief>"}]}
```

Presence is checked, but `type` is never required to be a string. The `switch` enumerates the array and validates the prompt shape, while the later `-ceq` filter treats the matching array as truthy and counts it as the sole `turn.prompt`. [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:516) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:526) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:809)

I probed those exact operations on both installed PowerShell hosts; both validated and counted the array-valued type. The repository already documents the underlying array-filter semantics. [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:423)

### 4. Vacuously valid `config.update` — both hosts CLEAN

Start from the valid fresh fixture:

- Merge line 4’s `modelAlias` and `thinkingEffort` into line 2.
- Remove those fields from line 4, leaving it as an otherwise empty `config.update`.

The merged record validates both field groups. The empty record validates vacuously because `Test-ConfigUpdateShape` returns true when neither group is present. [fresh-wire.jsonl](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/fixtures/kimi-round/fresh-wire.jsonl:2) [fresh-wire.jsonl](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/fixtures/kimi-round/fresh-wire.jsonl:4) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:475) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:487)

There are still exactly two `config.update` records, and both shape counts equal one because the merged record satisfies both predicates while the empty record satisfies neither. `$first` and `$second` then both point to the merged record, so all four value comparisons pass. [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:723) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:738) [read-kimi-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:750)

The contract requires two `config.update` records and checks the profile, prompt, model alias, and effort; this construction lets one record provide every measurement while the second contributes only to the count. [backup-lane.md](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/backup-lane.md:250) [backup-lane.md](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/backup-lane.md:255)

### Required fix

- Establish an object root for both Kimi prior-state JSON and every wire JSONL line, using raw-text plus parsed-type validation equivalent to the Codex object gate.
- Require every wire record’s `type` to be a scalar string before `switch`, count, or boundary comparisons.
- Make `Test-ConfigUpdateShape` require exactly one shape: `$isFirst -xor $isSecond`.
- Add dual-host cases for the singleton-array state, singleton-array wire line, array-valued `type`, and merged-plus-empty `config.update` construction.

There are also two record corrections still needed:

- Item 62 still cites `Test-RecordIsUserMessage` at `673-684`, but the round-4 insertion moved it to `683-694`. [2026-07-27-0150-backlog.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:4067) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:683)
- Although Item 62 struck the “every round that logs a tool call” universal, the same unsupported wording remains in the code comment. [2026-07-27-0150-backlog.md](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:4131) [read-codex-round-evidence.ps1](C:/Users/Brandon/Documents/parallax/tools/read-codex-round-evidence.ps1:413)

### UNVERIFIED

- The reported old-head CLEAN reproductions and current-head refusal/control executions.
- The private 60-session, 32,437-record, 250-record, and 60-of-60 measurements.
- The exact 2,550/14 dual-host suite results, binder count, static-tier results, and backlog-checker execution.
- The historical count of eleven previously closed instances across earlier branches.

FIX
