Overall verdict: **FIX before merge.** Claims 1, 2, 3, 4, 5, 6, and 8 do not fully stand; claim 7 stands.

### 1. Task 3’s DEAD-only refusal

The narrowing exposes a false trade because proposed-owner liveness is checked only once, before the acquisition loop. The tool may then wait on a handle or holder, after which both fresh-acquire and reclaim paths write the proposed identity without rechecking it. An owner that was LIVE initially can therefore die during contention and still be recorded DEAD—the silent mutual-exclusion failure the task claims to close. `tools/kimi-lane-lock.ps1:561-577`, `tools/kimi-lane-lock.ps1:604-615`, `tools/kimi-lane-lock.ps1:624-643`, `tools/kimi-lane-lock.ps1:663-677`

The correct boundary is mutation-sensitive: require LIVE immediately before every new record write, while permitting UNMEASURABLE on the non-writing idempotent re-acquire path where the matching nonce and retained identity already establish ownership. The latter path already exists separately. `tools/kimi-lane-lock.ps1:646-656`, `evals/multi-model-verify/test_kimi_lane_lock.py:652-686`

This also removes the residual without locking the true owner out: replace the fresh-acquire oracle that currently requires acceptance under an unmeasurable start time with a refusal oracle, retain the existing idempotent re-entry oracle, and add a contention-synchronized test that kills the proposed owner before the holder releases. `evals/multi-model-verify/test_kimi_lane_lock.py:1237-1259`, `evals/multi-model-verify/test_kimi_lane_lock.py:658-686`

The claim is additionally wider than its own test text permits: the fixture helper still says Acquire refuses anything that “does not measure LIVE,” despite the shipped DEAD-only rule. `evals/multi-model-verify/test_kimi_lane_lock.py:40-47`

**FIX — remeasure immediately before each record write, require LIVE for a fresh/reclaim write, preserve UNMEASURABLE only for non-writing idempotent re-entry, and repair the wider test wording.**

### 2. Task 2’s ancestry walk

This is not faithful to Amendment 1. The revised task requires a “recognized long-lived ancestor” and refusal when none exists; the implementation instead recognizes four transparent transports and accepts the first process with any other name. `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:278-286`, `tools/kimi-lane-lock.ps1:832-836`, `tools/kimi-lane-lock.ps1:879-898`

Consequently, an ephemeral wrapper named `node.exe`, `python.exe`, or anything else outside those four names remains accepted as the owner. The only stability oracle inserts another copy of the same PowerShell host, so it establishes stability across that transport—not “under any wrapper,” as the shipped lifecycle contract claims. `evals/multi-model-verify/test_kimi_lane_lock.py:216-258`, `skills/multi-model-verify/references/backup-lane.md:107-118`

I do not object to 16 as a safety bound: overflow refuses with exit 2, and the build record’s measured chain had depth six. Its risk is availability rather than mutual exclusion. `tools/kimi-lane-lock.ps1:836-854`, `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:398-406`

**FIX — either implement Amendment 1’s recognized-long-lived-owner/refusal contract, or formally amend the task and keep item 26 open for unlisted ephemeral wrappers; the four-transport strategy cannot presently claim general wrapper stability.**

### 3. Optional `ownerName` migration

The runtime migration itself is complete: the field is admitted but optional, shape-checked when present, written on both fresh and reclaim paths, forwarded conditionally through both wrappers, and included in status. `tools/kimi-lane-lock.ps1:136-146`, `tools/kimi-lane-lock.ps1:360-367`, `tools/kimi-lane-lock.ps1:604-638`, `tools/kimi-lane-lock.ps1:795-803`, `tools/new-kimi-lane-home.ps1:375-385`, `tools/new-kimi-lane-home.ps1:579-585`, `tools/new-kimi-lane-login.ps1:537-547`

The four live recovery-command copies also moved together, and the deleted original Task 3 was not implemented: recovery still resolves a fresh login owner, while the login wrapper releases that same retained identity in `finally`. `commands/doctor.md:192`, `tools/new-kimi-lane-home.ps1:179`, `evals/multi-model-verify/test_kimi_lane_home.py:809`, `evals/multi-model-verify/test_backup_lane.py:1413`, `tools/new-kimi-lane-login.ps1:530-575`

But the fixture repair is incomplete. The wrong-PID, zero/negative-PID, wrong-ticks-type, and non-digit-ticks stubs all omit `ownerName`; because recovery now requires that field, every case can pass solely through the missing-name rejection even if its intended validation is deleted. The parametrized assertion checks only generic failure and marker absence. `evals/multi-model-verify/test_kimi_lane_home.py:1692-1715`, `evals/multi-model-verify/test_kimi_lane_home.py:1717-1739`, `evals/multi-model-verify/test_kimi_lane_home.py:1865-1889`

The template’s adjacent comment also still describes an exact two-field record despite the exact three-field implementation. `tools/new-kimi-lane-home.ps1:174-179`

**FIX — give every non-name schema fixture a valid `ownerName`, make each case single-defect/reason-sensitive, and update the stale two-field template comment.**

### 4. Release step and quiet-holder row

The release half stands: the closing region names teardown as the final step, covers ESCALATE/abandonment/transport failure, and states that prose neither executes nor detects omission. `skills/multi-model-verify/references/backup-lane.md:162-183`

Quietness also cannot alter reclaim through the shipped paths: the doctor keeps the row OK and explicitly forbids quietness as reclaim evidence, while the lock’s mutating decisions remain based on process liveness. `commands/doctor.md:235-251`, `tools/kimi-lane-lock.ps1:13-21`, `tools/kimi-lane-lock.ps1:619-646`

The prose is not fully deterministic for reparse points. “Walk recursively” does not say whether file or directory links/junctions are followed, ignored, treated as files themselves, or regarded as unreadable. Two implementations can therefore inspect different file universes while following the written rule. `commands/doctor.md:235-251`

**FIX — specify reparse-point handling; the conservative rule is never follow them and degrade to silence when one prevents a complete in-home measurement.**

### 5. Round cap and scope rule

The contested-round definition and scope definitions are materially clear: outstanding earlier contests continue the counter, SAME CLASS requires the same named invariant, and the verification surface must predate the finding. `skills/multi-model-verify/references/debate-protocol.md:53-62`, `skills/multi-model-verify/references/debate-protocol.md:101-124`

The termination contract contradicts itself. “Converged with amendments” says an accepted final-round FIX makes the plan converged, while the new termination rule says the debate ends only after a dry round with no new substantive finding. The suite separately pins both clauses, so green tests preserve rather than detect the contradiction. `skills/multi-model-verify/references/debate-protocol.md:47-52`, `skills/multi-model-verify/references/debate-protocol.md:81-85`, `evals/multi-model-verify/test_multi_model_verify.py:776-782`, `evals/multi-model-verify/test_multi_model_verify.py:825-839`

The total budget also never defines what consumes one unit. A reviewer can count every exchange, only rounds completing acceptance, or only rounds beginning after an accepted fix; those interpretations can pause at different points. `skills/multi-model-verify/references/debate-protocol.md:63-80`

**FIX — make “converged with amendments” a nonterminal agreement state requiring application plus a confirming dry round, and define the exact exchange/event that decrements the fix-verify budget.**

### 6. Retained round records

The count and most verdict mappings stand: seven plan replies and five diff replies are indexed, and rounds 5, 6, and 7 respectively carry blocked ESCALATE, blocked ESCALATE, and terminal PASS. `docs/superpowers/plans/rounds/2026-08-04-transport-and-mirror/README.md:11-33`, `docs/superpowers/plans/rounds/2026-08-04-transport-and-mirror/plan-reply-r5.md:17-18`, `docs/superpowers/plans/rounds/2026-08-04-transport-and-mirror/plan-reply-r6.md:10-12`, `docs/superpowers/plans/rounds/2026-08-04-transport-and-mirror/plan-reply-r7.md:1-3`

One table entry is unsupported: round 1 is indexed as “FIX, eight findings,” but the reply says eight claims were reviewed and only six—1, 3, 4, 6, 7, and 8—needed fixes. It never carries an eight-finding count. `docs/superpowers/plans/rounds/2026-08-04-transport-and-mirror/README.md:13-16`, `docs/superpowers/plans/rounds/2026-08-04-transport-and-mirror/plan-reply-r1b.md:1-5`

**FIX — change the round-1 index entry to “FIX; claims 1, 3, 4, 6, 7, and 8” or “FIX; six claims require changes.”**

### 7. Item 29 disposition

The disposition stands. The code names the missing ordering guard and its exact failure direction; the backlog records why an unwatched comparison was not shipped and identifies a safe refusal-only fault seam as the preferred future closure. `tools/kimi-lane-lock.ps1:863-872`, `docs/superpowers/plans/2026-07-27-0150-backlog.md:1810-1837`

Under the project’s test-evidence invariant, naming and filing the residual is better than adding a guard whose refusal behavior has never been observed. `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:18-20`, `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:717-730`

**PASS**

### 8. Completeness of stated limits

The limits are incomplete. Neither the plan’s DEAD-only residual nor item 26’s closure admits that the proposed owner can die after the single pre-loop measurement and still be written after contention. Instead, they claim a dead identity can no longer enter the record. `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:333-364`, `docs/superpowers/plans/2026-07-27-0150-backlog.md:1672-1680`, `tools/kimi-lane-lock.ps1:561-577`, `tools/kimi-lane-lock.ps1:604-643`

The ancestry limit likewise admits only the cost of skipping long-lived orchestration inside four named hosts, not that an ephemeral wrapper with any other executable name remains accepted. `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:408-423`, `tools/kimi-lane-lock.ps1:832-898`

The backlog’s top-level status is also stale: it still calls items 24, 25, and 26 open and omits item 29, while their own headings say 24–26 are closed and 29 is open. `docs/superpowers/plans/2026-07-27-0150-backlog.md:11-16`, `docs/superpowers/plans/2026-07-27-0150-backlog.md:1471-1472`, `docs/superpowers/plans/2026-07-27-0150-backlog.md:1522-1523`, `docs/superpowers/plans/2026-07-27-0150-backlog.md:1566-1567`, `docs/superpowers/plans/2026-07-27-0150-backlog.md:1810-1812`

**FIX — record the post-check owner-death and unlisted-wrapper limits, keep item 26 open until they are resolved or explicitly re-scoped, specify the doctor’s reparse behavior, and repair the backlog status summary.**

### UNVERIFIED

- Fresh execution of the required Python gates is UNVERIFIED; the review environment exposed no Python entry point. The required gate set is `CLAUDE.md:5-17`.
- The narrated watched-fail mutations and dual-host pass counts were read but not independently reproduced. `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:338-358`, `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:581-590`, `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:653-665`
- The retained replies’ claimed verbatim identity to the original reviewer output is UNVERIFIED; only their present repository contents were checked. `docs/superpowers/plans/rounds/2026-08-04-transport-and-mirror/README.md:49-53`
- The absolute proposition that no possible test can exercise item 29 is UNVERIFIED; only the absence of a current ordering seam/oracle was established, and the backlog itself describes such a future seam. `docs/superpowers/plans/2026-07-27-0150-backlog.md:1826-1837`

The worktree remains unchanged.

