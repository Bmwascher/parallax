Revision 24 is not yet a PASS. The three intended fixes are directionally correct, but the binary-state sweep found six blocking defects.

### Task 1

The checker requires workflow paths merely to “exist,” and its mutation covers only nonexistence. An implementation using `Path.exists()` passes a directory named `test_*.py`, even though the test module has disappeared and pytest may collect nothing from it. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:114-129`

Fix:

- Require every workflow `evals/...py` token to resolve to a readable regular file; stat/readability failure is fatal.
- Add a mutation where the workflow names a directory ending in `.py`; the checker must report it as not a test file.

Verdict: FIX — BLOCKING, distinguish a usable test file from mere path existence.

### Task 2

The status partition, defect precedence, type edges, duplicate-key directions, and dual-host fixture oracle remain complete. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:133-165`

Verdict: PASS

### Task 3

The round-24 change matches the requested fix. The named seam signals only after actual handle or holder contention, a signal failure is fatal, and both clamp and retry-success run against both branches. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:224-237`

The 0.5-to-5-second clamp and 30-second retry budget are acceptable CI tolerances now that PowerShell cold start is outside the proof. No further timing change is required.

Verdict: PASS

### Task 4

The OS-level measurements retain fatal setup checks, bounded synchronization, and mutations for the failure directions. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:350-373`

Verdict: PASS

### Task 5

The login wrapper still treats each directory bootstrap as binary—“create if absent; otherwise apply ACL”—without distinguishing an existing non-directory object or an unmeasurable path. That occurs both for the lane home before acquisition and for `credentials` under the lock. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:392-408`

A regular file at the lane-home path could therefore have its ACL replaced before the wrapper eventually fails to create `lane.lock`. This violates the claim that the pre-lock operations are safe and identity-scoped. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:392-396`

Fix:

- Give both directory probes four rows: nonexistent, directory, non-directory, unmeasurable.
- Lane home: only nonexistent creates; directory applies the ACL; the last two exit 6 without mutation, lock invocation, client invocation, or verdict write.
- Credentials path: only nonexistent creates; directory applies the ACL; the last two exit 6, invoke no client, preserve the obstructing object, and release in `finally`.
- Name deterministic fault seams for both probes.
- Test regular-file collisions and probe faults, asserting file bytes and ACL unchanged; for the credentials case also assert the lock becomes `free`.

Verdict: FIX — BLOCKING, partition both login-wrapper directory probes.

### Task 6

Three defects remain.

First, the new table contradicts its following sentence. The directory row says “proceed to Acquire,” but the next paragraph says the “last three rows”—which includes that directory row—never invoke the lock tool. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:438-445`

Replace that sentence with: “The recovery row and the two refusal rows create nothing and never invoke the lock tool. The directory row alone proceeds to the normal build order.”

Second, the deterministic probe-fault seam is not named or given a firing contract. Production and tests must invent their shared environment variable. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:447`

Freeze, for example:

- `PARALLAX_LANE_HOME_DIRECTORY_PROBE_FAULT`
- Build mode only.
- Fires immediately before the real directory probe.
- Simulates the unmeasurable row.
- No stdout or recovery command, no mutation, no lock invocation.
- Exact stderr sentinel shared by implementation and test.

Third, deletion itself has no failure row or oracle. The plan covers identity refusal, sentinel refusal, successful deletion, and post-deletion release failure, but not `Remove-Item` failing or returning with the home still present. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:463-475` This matters because the current implementation calls `Remove-Item` and immediately prints success, while failed-build cleanup also calls it without a frozen terminating-error boundary. `tools/new-kimi-lane-home.ps1:127-133,482-490`

Fix both deletion paths:

- Remove mode uses terminating deletion and verifies the path is absent before release. A deletion error or residual path is primary, prints no `removed` line, does not release, and leaves the held lock record byte-identical.
- Add a real failure oracle using an exclusively opened file beneath the debate home under both hosts; require nonzero, home present, no success line, and lock still held.
- Failed-build cleanup must preserve the original build failure even if cleanup deletion fails, still attempt release, report the cleanup error only on stderr, and leave the lock `free` when release succeeds.
- Add a named cleanup-deletion seam proving that precedence and release behavior.

Verdict: FIX — BLOCKING, correct the table contradiction, name the probe seam, and partition deletion failure.

### Task 7

Custody, cleanup matrices, secret handling, measurement failures, and exception paths remain explicitly partitioned. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:500-629`

Verdict: PASS

### Task 8

The supposedly total substate table omits the clean binary state. It has rows for binary absent and binary present-but-broken, but none for a readable version at or above the floor, despite saying every substate is named. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:637-655` The existing doctor contract treats a present usable version as the non-failure branch. `commands/doctor.md:146-156`

Fix:

- Add `binary present, readable version at or above floor | OK`.
- Add an all-clean fixture requiring the aggregate verdict `OK` and detail naming the successful binary/floor comparison.
- Pin that row so an implementation mapping the clean binary to `N/A` or omitting it fails.

Verdict: FIX — BLOCKING, add and test the clean binary row.

### Task 9

The new literal still overclaims. “Exactly THREE steps run before the lock” excludes parameter validation and login debate-id generation, both explicitly before acquisition in Task 5. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:394-396,706-708`

Fix the literal to say “Exactly three FILESYSTEM INTERACTIONS are permitted before lock acquisition,” followed by the existing three. That preserves the intended boundary without falsely excluding non-filesystem validation and identity generation.

Verdict: FIX — BLOCKING, narrow “three steps” to three filesystem interactions.

### Task 10

Host parity, final-head live reruns, and the fatal-before-interpretation history check remain decisive. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:723-748`

Verdict: PASS

## Overall verdict

FIX. Do not freeze revision 24.

The round-24 Task 3 change is correct and sufficiently tolerant. Task 6’s intended four-row probe exists, but its next sentence contradicts the table and its seam remains unnamed. The broader sweep also found incomplete path-type partitions in Tasks 1 and 5, an untested deletion-failure state in Task 6, a missing clean binary row in Task 8, and an overbroad shipped lifecycle sentence in Task 9.

## Final check

UNVERIFIED:

- Measurements 1–21 remain externally taken measurements; the spec says the repository cannot verify them. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:35-67,348-354`
- Three simultaneous lane logins remain a generalization from the measured two-login result. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:506-523`
- The normalized absolute-key failure message and live credential/junction results do not exist until Task 7’s live measurements run. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:565-567,584-597`
- The remote-ref and branch-filtered Actions claims were not rerun here. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:104-110`
- No implementation or planned pytest/live gate exists to execute yet; the plan remains DRAFT. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:5,169-173,350-354,377-379,420-422`

The unavailable Python executable is not a finding.