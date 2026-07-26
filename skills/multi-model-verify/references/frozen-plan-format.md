# Frozen plan format

The debate's output is a superpowers-compatible implementation plan. The
implementer (the pinned lane in `agents/`, or the session model, via superpowers
subagent-driven-development or executing-plans) follows it with **zero
judgment calls** — anything the plan leaves open is a plan defect, found in
mode `diff` as drift.

A task the plan routes to the escalation lane carries an enumerated decision envelope; DECISIONS inside the envelope are authorized outcomes, not drift.
The envelope is part of the frozen task text: each delegated decision
point is enumerated with the constraints that bound it, the escalation
lane (agents/escalation-implementer.md) logs one DECISIONS entry per
point, and mode diff adjudicates those entries against the envelope -
only envelope overruns are drift.

## Base format

Follow the superpowers writing-plans template exactly (header with Goal /
Architecture / Tech Stack / Global Constraints; bite-sized checkbox tasks
with exact Files / Interfaces / complete code / exact commands / expected
output; no placeholders). Every task's verification command must be able
to FAIL: the debate checks each one for oracle adequacy — a proof that
would pass while the feature is broken (a compile check standing in for a
behavior check, a test that never exercises the changed path) is a plan
defect, found in the debate, not in production. Save location: the
superpowers default
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

**Participants:** <session model> (session) / <reviewer model> (codex exec, session <id>)
**Rounds used:** N of CAP
**Outcome:** converged | converged with amendments | escalated
**Verification status:** FULL | DEGRADED
**Degradation:** none | codex-missing | model-rejected | auth-expired | quota-exhausted | continuity-lost | <class>
**Authorized by:** n/a | user at round N | not-authorized
**Raw rounds:** <paths to the verbatim round replies/transcripts> | not retained

### Resolved points
| # | Claim | Raised by | Outcome | Evidence |
|---|-------|-----------|---------|----------|
| 1 | ...   | reviewer  | accepted into Task 3 | References/<addon>/<file>:<line> |
| 2 | ...   | session   | refuted  | .wow-api-reference/<file> |
| 3 | ...   | reviewer  | struck (no citation) | — |

### Escalated points (user-decided)
| # | Question | Session position | Reviewer position | Owner's call |
|---|----------|------------------|-------------------|--------------|

### Degraded-mode note
(required whenever Verification status is DEGRADED — name what was skipped,
why, and the recorded user authorization. The Participants line must name
the actual participants, never the placeholder template line.)
```

The three status fields are structured on purpose: mode `diff` parses
`Verification status` to enforce the degraded-plan poisoning rule (see
SKILL.md) — prose notes cannot be enforced. `Raw rounds` records where the
verbatim reviewer replies live (scratchpad transcripts are temporary — if
they were not copied somewhere durable, say `not retained`): the summary
tables above are the adjudication, not the provenance, and a later dispute
about what the reviewer actually said needs the raw text or an honest
"gone". The canonical retained location is
`docs/superpowers/plans/rounds/<YYYY-MM-DD>-<topic>/` next to the frozen
plans (established by the 2026-07-24 jinn intake) — prefer it over ad-hoc
paths so retention survives scratchpad cleanup by default.

Lane substitution (backup reviewer): `Verification status: FULL` MAY
carry a `Degradation:` class plus `Authorized by: user at round N` when
a backup cross-vendor lane substituted for the primary — lane substitution is NOT degradation; the Degradation field then names the
PRIMARY-lane failure that triggered substitution, and the Participants
line names the actual backup participant, e.g.
`Kimi K3 (kimi-cli, session <id>)`. This codifies the combination first
used by the 0.12.0 record. The Degraded-mode note stays bound to
DEGRADED status; a debate in which a backup cross-vendor lane substituted for the primary is recorded with this combination, never as DEGRADED.

Panel recording (references/panels.md): the Participants line lists
every lane that produced a terminal verdict, with its transport and
session or agent id — a completed panel lists every member; a
consented post-loss continuation lists only the surviving lanes, with
the lost lane and its loss class in the failure prose; Rounds are
counted per lane (e.g. `Sol 3 of 4 / Kimi 2 of 4`); convergent blind
findings are marked convergent in the resolved rows and counted once;
for mode diff the record names the required fable-review artifact
path.
A panel records Verification status: FULL only when every participating lane's per-round evidence was clean AND every terminal verdict cites the final subject revision.
For the attestation emitter the panel mapping is: `-Rounds` = the
maximum lane round count; `-Participants` names the driver and every
lane; `-RouteNote` stays `effective route confirmed` only under the
strictest-lane rule — every lane's every-round evidence matched that
lane's own canonical declarations; per-lane detail lives in this
record's prose, never in the JSON (emitter and verifier schemas are
unchanged).
A consented post-loss continuation records the panel-lane-loss class
and the consent (`Authorized by:`), mirroring the lane-substitution
shape above; a cross-vendor-free remainder records DEGRADED per
fallbacks.md.

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
