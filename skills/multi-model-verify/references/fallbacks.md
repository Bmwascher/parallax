# Fallbacks and degraded modes

**Governing rule: no transition that reduces vendor diversity, evidence
quality, or conversation continuity happens without explicit user consent.**
The skill never enters degraded mode automatically. Degradation that is not
consented to is a stop, not a mode.

## The consent gate

When a failure survives bounded recovery (below), STOP and present a banner
to the user — before any degraded work happens:

```text
== CROSS-VENDOR VERIFICATION UNAVAILABLE ==
What failed:      <exact command + error>
What degraded mode would verify:     <e.g. claims via a fresh Fable skeptic>
What it would NOT verify:            <cross-vendor independence>
Options: [fix codex] [run degraded] [abort]
```

- The user's choice is recorded in the debate record (`Authorized by:` field
  — see frozen-plan-format.md).
- **Unattended runs fail closed**: if no user can answer, terminate as
  `BLOCKED/DEGRADED-NOT-AUTHORIZED` with a non-success status. Never wait
  indefinitely, never infer consent.

## Bounded recovery (automatic, consent-free)

One retry with the SAME model, sandbox, effort, and session parameters is
the DEFAULT recovery for any failure that has no named immediate-gate rule
below (codex-missing, model-rejected, auth-expired, and quota-exhausted go
straight to the gate — retrying those changes nothing). The retry reduces
nothing, so it needs no consent. A failed retry goes to the consent gate.
This covers timeouts and transient transport errors.

**Catch-all: any codex failure not named in this file — nonzero exit, empty
reply file, malformed output, network loss, resume failure —
gets the same treatment: one same-parameters retry, then the consent gate.**
No failure class is ever an implicit license to degrade.

## Failure classes

### codex CLI missing or broken
`codex --version` fails → consent gate immediately (there is nothing to
retry). If the user chooses degraded mode: replace each Sol round with a
FRESH-context skeptic subagent (Fable, read-only tools) — fresh context is
mandatory; same-context self-critique rubber-stamps (see
model-prompting-notes.md). Brief the skeptic with the same XML-style brief
Sol would have received, including the strike rule and the
anti-manufactured-objection rule.

### Reviewer model rejected (400 "not supported when using Codex with a ChatGPT account")
The account tier lost access to the canonical reviewer model (the id is
declared ONLY in model-prompting-notes.md). Do NOT silently substitute
another model — the reviewer model is a user directive. Consent gate: fix
subscription / run degraded / abort. Tier-gating diagnostics for the
current lane (which sibling model confirms gating vs a CLI problem) live
in model-prompting-notes.md's Lane diagnostics bullet.

### Usage limit reached (session or weekly quota) — class `quota-exhausted`
The ChatGPT account's usage quota is exhausted; codex's error names which
limit was hit (the ~5-hour session window vs the weekly cap) and when it
resets. **Skip the retry** — nothing about a quota window is transient, and
a retry only burns another attempt against it. Go straight to the consent
gate with codex's reset time quoted verbatim in the `What failed:` line;
here the "fix codex" option means *wait for the reset* or *upgrade the
tier* — record which. If a debate is mid-flight, also note the codex
session id in the debate record so the debate resumes after the reset
instead of restarting from round 1.

### codex auth expired
`codex login status` fails → the fix needs the user anyway (`codex login`
is an interactive browser sign-in): consent gate.

### Session id lost or resume fails
Losing the resumed session degrades conversation continuity — an advertised
protocol property — so it is NOT automatic: one retry, then the consent
gate with the specific option "continue with fresh per-round Sol calls
(full brief re-sent each round; costs tokens, loses Sol's debate memory)".

### Stale API evidence
If the project's API-reference drift check reports the build changed under
a claim, that claim is **struck until re-verified** — the strike rule does
not weaken to a flag. Re-verify against the updated reference (or an
in-game/runtime probe) before the claim re-enters the debate.

## Degraded-mode output requirements (after consent)

- The SUPERVISING SESSION emits the banner — never delegate the banner to
  the skeptic subagent's output, or a formatting miss becomes a quiet path.
- Every round after the transition starts with
  `== DEGRADED (single-vendor) ==`.
- The finish line and the frozen plan carry the structured fields
  (`Verification status: DEGRADED`, `Degradation: <class>`,
  `Authorized by: user at round N`) per frozen-plan-format.md.
- The debate record's Participants line must name the actual participants
  (e.g. `Fable 5 (session) / Fable 5 skeptic subagent (DEGRADED -
  codex-missing)`), never the default Sol template line.
- A DEGRADED-frozen plan poisons downstream PASSes — see SKILL.md mode
  `diff` for the enforcement rule.

## Reference failures (not degraded modes — hard stops)

### Reference source missing for a port
Ask the user for the path. NEVER proceed with an ungrounded debate — a
debate about remembered reference behavior is two models fabricating at
each other. This is a hard stop, not a degraded mode.

## Known limits (documented, not silent)

- The review-companion hook is ADVISORY: it injects the diff-mode reminder;
  it cannot block a merge. The enforcement backstop is the finish rule and
  the user. It is also registered for failed review dispatches
  (PostToolUseFailure), so a crashed code review still surfaces the gate.
- Hook fingerprint rot is detected by the eval suite (pinned template
  fixture in CI + installed-template canary locally), not at runtime.

## Alternative transport (documented, rejected for v1)

CLIProxyAPI (the Theo/Tibo "claudex" setup) runs a SEPARATE Claude Code
process pointed at a local proxy that translates to the Codex backend
(same ChatGPT OAuth), with env vars like `CLAUDE_CODE_SUBAGENT_MODEL`
selecting Sol — it does not touch the existing Fable session's traffic.
Revisit only if codex exec proves limiting (e.g. a cross-vendor implementer
lane needs Claude Code's own tool harness). It does NOT bypass the
subscription tier gate — same auth, same 400 on free accounts. Costs: a
local proxy service to run and keep patched, a second configured process,
and untested cross-vendor hook and permission semantics.
