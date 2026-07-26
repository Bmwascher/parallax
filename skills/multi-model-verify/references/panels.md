# Panels (multi-reviewer debates)

A panel convenes MORE than one reviewer lane for a single debate -
user-invoked only, never automatic. Sol solo stays the default;
Kimi solo stays the consent-gated backup lane (fallbacks.md). A panel
is for work the user judges worth multiple independent reviewers:
complicated plans, high-risk diffs, or a debate the user wants
cross-examined from more than one vendor culture.

## Compositions

Valid compositions: Sol+Kimi, Sol+Fable, Kimi+Fable, Sol+Kimi+Fable.

Every panel contains at least one cross-vendor lane (Sol or Kimi); an all-Claude panel is invalid.

The invariant is checked before round 1 and quoted with the user's
invocation in the debate record. Fable is never a cross-vendor lane:
with a Claude driver it shares the vendor, which is exactly why it
cannot be a panel's only reviewer.

## Topology: hub-and-spoke, blind

- The driver mediates every exchange. Reviewer lanes never communicate
  directly and never learn which lane raised a finding.
- Findings relay anonymously WITH their evidence; the driver verifies
  each claim against the repo before relaying it (a relayed claim the
  driver could not verify is relayed as UNVERIFIED, not as fact).
- Convergent blind findings - the same defect raised independently by
  more than one lane - are the strongest signal the panel produces;
  they are counted once, fixed once, and marked convergent in the
  record.
- Each lane runs the EXISTING bilateral protocol unchanged: the same
  round structure, strike rule, verdict grammar, and round cap it
  would have solo.

## Subject revision

The driver pins the subject revision in every round brief of every
lane. Mode diff: the base..head git SHAs. Mode plan: the SHA-256 of
the current round's claims section (the canonical position bytes every
lane receives that round) - the frozen plan file's blob hash takes
over only at freeze. An accepted amendment that changes the subject
re-opens all lanes.

A terminal verdict counts only when it cites the FINAL subject revision; a verdict against a stale revision is input, never terminal.

## Lane transports (all pre-existing machinery)

- Sol: codex exec sessions per SKILL.md - env hygiene, header route
  checks, session resume. Unchanged.
- Kimi: the backup-lane transport per references/backup-lane.md -
  contained agent-file dispatch, per-round offset evidence, and the
  pre-round-1 write-probe - all unchanged and all required in panels.
  Panel participation is a sanctioned entry route recorded in
  backup-lane.md; the user's panel invocation is the consent.
- Fable: agents/fable-panel-reviewer.md - a fresh same-harness
  subagent at round 1, resumed for later rounds. Per-round evidence
  class, recorded in these words: dispatch metadata - the round-1
  dispatch names the model pin, and the resume surface carries no
  model parameter (probed 2026-07-26; record:
  docs/superpowers/plans/rounds/2026-07-26-seat-reshuffle/subagent-resume-probe.md),
  so the pin cannot be silently swapped mid-debate. Round continuity
  is evidenced by transcript recall; the failure mode is agent death,
  which is loud (class panel-lane-loss, fallbacks.md). Self-reported
  identity is priming-class and never evidence.

## Convergence and adjudication

Each lane reaches its own terminal verdict under its own round cap
against the final subject revision. The session then adjudicates
across lanes per debate-protocol.md's final-adjudication step -
verify, accept or refute with evidence, escalate genuine deadlocks to
the user. A panel converges when every lane's terminal verdict on the
final subject revision is PASS or its FIXes are accepted on the
record.

## Failure handling and recording

All failure classes live in fallbacks.md (single namespace) - a lost
lane routes through its own transport classes first, then the
panel-lane-loss class governs: the panel stops at the consent gate,
never continues automatically. Record fields for a panel debate live
in frozen-plan-format.md: per-lane Participants and rounds, convergent
marking, the strictest-lane FULL condition, and the required
fable-review artifact path for mode diff.
