# Frozen plan format

The debate's output is a superpowers-compatible implementation plan. The
implementer (Sonnet 5 or the session model, via superpowers
subagent-driven-development or executing-plans) follows it with **zero
judgment calls** — anything the plan leaves open is a plan defect, found in
mode `diff` as drift.

## Base format

Follow the superpowers writing-plans template exactly (header with Goal /
Architecture / Tech Stack / Global Constraints; bite-sized checkbox tasks
with exact Files / Interfaces / complete code / exact commands / expected
output; no placeholders). Save location: the superpowers default
`docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`, unless the project
overrides it (example: KitnEssentials uses `dev/docs/superpowers/plans/`).

Port-specific Global Constraints to copy in verbatim when the work is a
port (KitnDev-family example — adapt the specifics per project):

- Project naming/style conventions the port must follow (KE example:
  KE namespace, flat DB keys, `KE:ApplyFontToText` for SOFTOUTLINE-capable
  text, string literals only — see the module-port skill).
- Reference source and version the port tracks:
  `References/<name>/` at the fidelity the debate agreed on (faithful core
  logic; project-specific deviations listed one per line WITH the debate
  round that approved each).
- Platform/API constraints the debate verified, each with its citation
  (KE example: WoW 12.0 secret-value rules).

## Debate record appendix (REQUIRED)

Every frozen plan ends with:

```markdown
---

## Debate record

**Participants:** Fable 5 (session) / GPT-5.6 Sol (codex exec, session <id>)
**Rounds used:** N of CAP
**Outcome:** converged | converged with amendments | escalated
**Verification status:** FULL | DEGRADED
**Degradation:** none | codex-missing | model-rejected | auth-expired | quota-exhausted | continuity-lost | <class>
**Authorized by:** n/a | user at round N | not-authorized

### Resolved points
| # | Claim | Raised by | Outcome | Evidence |
|---|-------|-----------|---------|----------|
| 1 | ...   | Sol       | accepted into Task 3 | References/<addon>/<file>:<line> |
| 2 | ...   | Fable     | refuted  | .wow-api-reference/<file> |
| 3 | ...   | Sol       | struck (no citation) | — |

### Escalated points (user-decided)
| # | Question | Fable position | Sol position | Owner's call |
|---|----------|----------------|--------------|--------------|

### Degraded-mode note
(required whenever Verification status is DEGRADED — name what was skipped,
why, and the recorded user authorization. The Participants line must name
the actual participants, never the default Sol line.)
```

The three status fields are structured on purpose: mode `diff` parses
`Verification status` to enforce the degraded-plan poisoning rule (see
SKILL.md) — prose notes cannot be enforced.

The appendix is the audit trail: mode `diff` re-reads it to know which
deviations were approved and which claims were struck. A frozen plan without
the appendix was not verified — treat it as an unfrozen draft.

## Freezing

A plan is frozen when: both sides verdict PASS — or the final round's FIXes
are accepted on the record (converged with amendments, per
debate-protocol.md) — with any escalations carrying the user's recorded
call, the writing-plans self-review checklist has run, and the file is
saved. After freezing, changes require reopening the debate
(a new round appended to the record) — the implementer never edits the plan.
