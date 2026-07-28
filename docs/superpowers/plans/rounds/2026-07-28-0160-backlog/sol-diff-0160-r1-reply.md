Overall verdict: **FIX.** Q1, Q2, and Q5 overstate the implementation; Q3 and Q4 stand.

## Claim verdicts

### Q1 — FIX

The ordinary branch structure is disjoint: failures set `$autotriageFailure`, trusted outcomes clear `$manualToast`, and the BLOCKED branch sets only `$autotriageBlocked`. The toast precedence also distinguishes failure, blocked, and ordinary manual fallback. `tools/check-drift.ps1:385-390`, `tools/check-drift.ps1:566-573`, `tools/check-drift.ps1:711-741`, `tools/check-drift.ps1:785-800`

But the semantic three-state claim fails for this reachable path:

1. The fallback explicitly includes a nonzero agent exit. `tools/check-drift.ps1:725-728`
2. If that failed run nevertheless emitted exactly one parseable `VERDICT: BLOCKED`, the code ignores `$agentExit` and classifies it as deliberate BLOCKED. `tools/check-drift.ps1:729-741`
3. The pending entry then records an empty failure, which `/parallax:drift-triage` interprets as automation that finished deliberately. `tools/check-drift.ps1:809-817`, `commands/drift-triage.md:31-37`
4. The existing BLOCKED scenario exercises only exit 0, so it does not close this path. `evals/tools/drift_statemachine_tests.ps1:418-433`

There is also a stale code invariant saying failure is nonempty on every enabled manual path except `-NoAutoTriage`; BLOCKED now disproves that comment. `tools/check-drift.ps1:380-390`

Specific fix: classify BLOCKED only when `$agentExit -eq 0`; otherwise set `$autotriageFailure`. Add a nonzero-exit-plus-BLOCKED state-machine scenario and correct the stale comment. `tools/check-drift.ps1:729-741`

### Q2 — FIX

The corrected bare-release guard works for a labelled lock: a missing or different label is refused unless `-Force` is passed. `tools/kimi-lane-lock.ps1:93-112`, `evals/multi-model-verify/test_kimi_lane_lock.py:89-127`

The broader ownership claim is false:

- `-MaxAgeMinutes` is caller-controlled with no range or production/test distinction. `tools/kimi-lane-lock.ps1:30-38`
- `-Acquire -Label debate-B -MaxAgeMinutes 0` treats debate-A’s fresh lock as stale, overwrites it, and exits “acquired” without `-Force`; the shipped test demonstrates exactly that transition. `tools/kimi-lane-lock.ps1:127-147`, `evals/multi-model-verify/test_kimi_lane_lock.py:163-168`
- Labels are optional. An unlabelled lock may be acquired and subsequently removed by any bare release; the suite explicitly blesses this behavior. `tools/kimi-lane-lock.ps1:23-35`, `tools/kimi-lane-lock.ps1:105-110`, `evals/multi-model-verify/test_kimi_lane_lock.py:112-119`
- A parseable future timestamp produces a negative age and therefore never reaches the stale branch until the clock catches up; ordinary callers repeatedly receive BUSY rather than the promised 45-minute recovery. `tools/kimi-lane-lock.ps1:75-85`, `tools/kimi-lane-lock.ps1:127-151`
- The documented last-writer-wins race is honestly stated and is not an additional finding. `tools/kimi-lane-lock.ps1:137-140`

Specific fix: require a nonempty unique ownership token on acquire/release, keep the 45-minute threshold non-overridable outside an explicit test seam, and treat future timestamps as malformed/stale. If labels remain the ownership credential, narrow the invariant and document label collision, unlabelled-lock, configurable-age, and active-round-over-45-minute limits.

### Q3 — PASS

The driver procedure is followable without invention: capture the offset, capture the round’s session id, locate that id’s session event, delimit at the next session event, verify the event kind, and count exactly one of each evidence line within that block. `skills/multi-model-verify/references/backup-lane.md:38-39`, `skills/multi-model-verify/references/backup-lane.md:45-63`, `skills/multi-model-verify/references/backup-lane.md:68-74`

Strictness was not relaxed. Anything other than exactly one of each inside the selected block is still discarded unread; foreign blocks are distinguished rather than tolerated inside the round’s block. `skills/multi-model-verify/references/backup-lane.md:50-63`

The remaining collision inside the startup block is explicitly fail-closed and recorded as residual risk. `skills/multi-model-verify/references/backup-lane.md:75-80`

### Q4 — PASS

Each new or renamed normalized body is contained whole in one positive assertion:

| Region | Contract | Whole-body pin |
|---|---|---|
| `session-block-attribution` | `skills/multi-model-verify/references/backup-lane.md:56-64` | `evals/multi-model-verify/test_backup_lane.py:138-144` |
| `session-block-kind` | `skills/multi-model-verify/references/backup-lane.md:68-74` | `evals/multi-model-verify/test_backup_lane.py:147-151` |
| `session-block-residual` | `skills/multi-model-verify/references/backup-lane.md:75-80` | `evals/multi-model-verify/test_backup_lane.py:154-158` |
| `lane-lock` | `skills/multi-model-verify/references/backup-lane.md:83-91` | `evals/multi-model-verify/test_backup_lane.py:163-169` |
| `rotation-guard-identity` | `skills/multi-model-verify/references/backup-lane.md:118-124` | `evals/multi-model-verify/test_backup_lane.py:229-234` |

The inventory contains all five, and its tests explicitly check both declared-but-missing and found-but-undeclared directions. `evals/multi-model-verify/test_contract_coverage.py:624-655`

### Q5 — FIX

Items 3 and 5 are accurately recorded:

- The attestation predicate remains the same, while rejection text names each failing field and identifies the route note as an exact token. `tools/verify-attestation.ps1:43-74`, `evals/multi-model-verify/test_attestation.py:130-182`
- The rotation text now records successful rotation, requires creation-time comparison, and has a positive correction pin plus a whole-region identity pin. `skills/multi-model-verify/references/backup-lane.md:107-128`, `evals/multi-model-verify/test_backup_lane.py:181-187`, `evals/multi-model-verify/test_backup_lane.py:229-234`

Items 2 and 6 overstate:

- Item 2 says BLOCKED means nothing broke, but a nonzero-exit run carrying a BLOCKED line receives that classification too. `docs/superpowers/plans/2026-07-27-0150-backlog.md:52-58`, `tools/check-drift.ps1:725-741`
- Item 6 says a crashed driver stalls the lane for at most 45 minutes, but the threshold is caller-controlled, a future timestamp can postpone staleness indefinitely under ordinary operation, and an active legitimate round also becomes breakable after 45 minutes because no liveness is checked. `docs/superpowers/plans/2026-07-27-0150-backlog.md:212-224`, `tools/kimi-lane-lock.ps1:10-16`, `tools/kimi-lane-lock.ps1:75-85`, `tools/kimi-lane-lock.ps1:127-151`
- The record still says “14 tests” even though the retained review established that baseline and the applied range added four more lock tests. `docs/superpowers/plans/2026-07-27-0150-backlog.md:217-219`, `docs/superpowers/plans/rounds/2026-07-28-0160-backlog/fable-review-c6b7c85-efe4fa0.md:32`, `evals/multi-model-verify/test_kimi_lane_lock.py:99-137`

## Prior-review adjudications

- I1 was applied, but incompletely because nonzero-exit BLOCKED remains misclassified. `tools/check-drift.ps1:729-741`
- I2’s exact bare-release case is fixed and tested. `tools/kimi-lane-lock.ps1:99-108`, `evals/multi-model-verify/test_kimi_lane_lock.py:99-127`
- m3 is fixed: duplicate evidence is again attached to the discard disposition. `skills/multi-model-verify/references/backup-lane.md:50-51`
- m4 is applied through the positive correction pin. `evals/multi-model-verify/test_backup_lane.py:181-187`
- m5 is applied: overwriting an unreadable lock is announced and tested. `tools/kimi-lane-lock.ps1:122-145`, `evals/multi-model-verify/test_kimi_lane_lock.py:130-137`

## UNVERIFIED — excluded from the verdict

- I did not independently rerun the reported 248/1 pytest result, drift state machine, lint, scanner, or trigger gates; those results remain checkpoint-reported evidence. `.git/parallax/application-checkpoints/2026-07-28-0330-efe4fa0c07d2.md:56-66`
- I could not independently verify the per-user Kimi log timestamps, the 17,583-byte concurrent window, or the assertion that the startup block is under one second. `docs/superpowers/plans/2026-07-27-0150-backlog.md:154-164`, `docs/superpowers/plans/2026-07-27-0150-backlog.md:205-210`, `skills/multi-model-verify/references/backup-lane.md:75-79`

**Overall: FIX** — gate BLOCKED on exit 0, harden or accurately narrow lock ownership/staleness, add the missing regression cases, and correct the Resolved block’s residual and test-count statements. `tools/check-drift.ps1:725-741`, `tools/kimi-lane-lock.ps1:23-38`, `tools/kimi-lane-lock.ps1:75-85`, `tools/kimi-lane-lock.ps1:127-151`

