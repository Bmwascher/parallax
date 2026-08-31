## 1. Round 7 findings

1. The exact self-authenticating-token defect is closed. The receipt is outside the dispatch directory, is created last with create-new semantics, and a refused second launch cannot create its fresh receipt; the regression explicitly polls that absent receipt and requires `no-receipt`. The plan separately admits that supplying an older receipt remains possible; I treat that as the eighth instance below, not as failure to replace the token mechanism. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:48-52`, `:68-70`, `:102-110` — **CLOSES**

2. LAUNCH UNKNOWN no longer promises an impossible PID remediation. The operation contract says the dangerous form has no PID on disk, `taskkill` cannot clear it, and alternate discovery is unmeasured and must be surfaced to the user. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:226-240` — **CLOSES**

3. The hard-kill test now has a deterministic synchronization point after process creation and before PID publication. The test waits for `.started`, kills the tool, and never releases it; production callers do not set the variable, and its bounded failure path can only fail a launch. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:87-89`, `:104-108` — **CLOSES**

4. Process identity is now PID plus start-time ticks. Recycled PIDs are treated as dead, unreadable start times are nonterminal `pid-unreadable`, and matching ticks alone mean `running`; this matches the cited repository precedent. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:72-74`, `:106`, `:117-120`; `tools/kimi-lane-lock.ps1:219-236` — **CLOSES**

5. The convergence oracle is now case-insensitive and includes the stale state counts, old token interface, old poll shape, encoding claim, and host spelling. That catches the currently uppercase stale count in the design. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:739-752`; `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:190-199` — **CLOSES**

6. The three exact one-task-executability omissions are closed: Task 1 contains both outer commands, Task 3 contains its measurement command, and Task 9 lists and stages the round record. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:76-86`, `:433-442`, `:725-733`, `:778-782` — **CLOSES**

## 2. Completion-model sweep

I am using the requested seven-of-seven base rate. The repository itself says to treat this class as open and records the earlier stale-artifact, missing-state, acceptance-order, and uncentralized-launch failures. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:21-26`, `:791-799`

I found an eighth instance: **a stale receipt can still answer for a new attempt**.

- Input: attempt A has a completed receipt and reply; attempt B is a retry or later act whose launch is unfinished or refused.
- Sequence: the caller mistakenly passes A’s receipt to B’s poll. Poll has no independently supplied expected directory or expected round, so it validates A’s commit and process artifacts and returns `reply-present` from A. The plan explicitly tests and preserves this behavior. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:49-52`, `:68-70`, `:112-122`
- Artifact read as B’s completion: A’s receipt leads to A’s `launch.committed`, PID, exit file, and reply. A different round label makes the mistake visible only if the caller performs the prose comparison; a same-label retry is not distinguished by that comparison at all. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:114-122`, `:410-421`
- The evidence binder narrows this materially: a different brief, route, or session must be rejected. It does not establish attempt identity when an earlier attempt used the same brief and expected session boundary. `skills/multi-model-verify/SKILL.md:215-234`; `skills/multi-model-verify/references/backup-lane.md:250-274`, `:288-316`

Smallest mechanical closure: make Poll accept `-ExpectedDispatchDir` and `-ExpectedRound`, compare both against the receipt before opening any dispatch directory, and return a distinct nonterminal/transport state such as `receipt-not-expected`. Expected directory is necessary because round labels such as `Sol R1` are reusable across retries. The current interface supplies neither value. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:45-52`, `:112-116`

## 3. Cross-act identities

| Shape | Assessment | Evidence |
|---|---|---|
| Location identity | **Narrowed, still open.** Receipt-to-directory identity is token-bound, but nothing binds that receipt to the directory the caller currently expects. | `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:50-52`, `:107-116` |
| Process identity | **Bound.** PID reuse and unreadable start times have explicit fail-closed states. | `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:72-74`, `:117-120` |
| Payload identity | **Narrowed, not directly bound.** The wrapper is copied without its hash appearing among the receipt fields. A wrong brief alone should not become a review result because both lane binders compare client-recorded prompt evidence and discard mismatches; a corrupt wrapper can still cause parse, route, or transport failure. | `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:51`, `:103`, `:124`; `skills/multi-model-verify/SKILL.md:215-234`; `skills/multi-model-verify/references/backup-lane.md:250-274`, `:288-316` |
| Execution-context identity | **Partly bound.** The caller’s PowerShell host and Kimi working directory are explicit. Plugin-tool resolution remains only narrowed: the new call is anchored while three existing calls remain item 58. | `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:76-84`, `:104`, `:489-500`, `:519-535`, `:775-776` |

Therefore the absent wrapper hash is not, by itself, a demonstrated false-completion path. Its completion-sensitive consequences are covered by the brief/route/session binders; its remaining consequences are wrong-command or transport failures. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:124`; `skills/multi-model-verify/SKILL.md:215-234`

## 4. Contradictions and under-specification

Three corrections remain:

- Task 9 says to reconcile the spec with “LAUNCH UNKNOWN first,” but the actual ordered contract has `no-receipt` first and LAUNCH UNKNOWN second. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:53-54`, `:112-116`, `:185-200`, `:735-737`
- Task 1’s negative oracle says to delete the catch “in step 5,” while the catch is step 7; step 5 writes PID/start ticks. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:106-108`, `:126-129`
- Poll exit behavior is underspecified. The plan imports the mirror’s three exit-code meanings but never maps eleven Poll states onto them, so an implementer must decide whether `running`, `no-receipt`, and terminal transport failures exit 0, 1, or 2. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:53-55`, `:112-124`; `tools/new-review-mirror.ps1:17-22`

The receipt validator also needs a minimum schema: required nonempty `dispatchDir`, token, round, and integer start-time fields, plus rejection of missing or wrongly typed fields. “Not this tool’s JSON” does not presently define that boundary. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:51-54`, `:114-118`

## 5. Freeze decision

Not ready to freeze. The smallest required changes are:

1. Mechanically bind Poll to the expected dispatch directory and round.
2. Define receipt validation and Poll exit-code mapping.
3. Correct “LAUNCH UNKNOWN first” to “NO RECEIPT first.”
4. Correct Task 1’s negative oracle from step 5 to step 7.

The actual host-boundary and 90-second detachment behavior remain intentionally unverified until Tasks 1 and 8 execute their real-host measurements. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:76-89`, `:690-714`

**FIX**