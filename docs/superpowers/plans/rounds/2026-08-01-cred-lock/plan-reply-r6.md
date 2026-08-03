R5 is closer, but not yet a PASS. Task 3’s mutating-mode partition is now correct, but its new preprocessing text accidentally applies to `Status` and `ResolveOwner`. Task 7 also still permits unlocked refreshes of A/B and has two remaining secret-handling gaps.

### Task 1 — CI repair

The initial four-module set is now exact, Task 10’s extension is explicit, and both existence and one-host omission have failing mutation tests. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:73-90,494-495`.

PASS

### Task 2 — Credential validation

The moved selector, platform guard, and direct `_fake_profile` validator oracle correctly close the round-5 finding. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:117-125`.

One specified behavior still lacks an oracle: duplicate keys take the last occurrence, but the test list contains no duplicate-key case. An implementation that rejects duplicates or retains the first value can pass. Add two fixtures:

- invalid first value, valid last value → `ok`;
- valid first value, invalid last value → the last value’s precise defect.

Run both under both hosts. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:115-117`.

FIX — add opposite-direction duplicate-key tests proving last-occurrence behavior.

### Task 3 — Lock tool

The free-record property rule, code 5 meaning, and foreign-host table partition are now correct for mutating file modes. The release/override classes are disjoint and complete once preprocessing is scoped appropriately. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:142-144,165-173,197-224`.

The new preprocessing incorrectly says every mode runs it. Consequently:

- readable malformed `Status` exits 4 under preprocessing but exits 0 under its dedicated rule;
- `ResolveOwner` would preprocess a lock file despite requiring neither `LaneHome` nor any file access. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:197-202,230-242`.

Change the heading to: “Preprocessing for mutating file modes only: Acquire, Release, ForceRelease, and MalformedOverride.” State that `Status` follows its dedicated read-only rule and `ResolveOwner` performs no lock-file operation.

A related sentence says every mode accepts `WaitSeconds` and `PollSeconds`, while the declared `ResolveOwner` parameter set accepts neither. Change it to “every lock-file mode accepts both; ResolveOwner accepts neither.” `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:146-161`.

Also scope exit-code 4 explicitly to mutating file modes so it cannot contradict malformed `Status` returning 0. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:165-173,232-237`.

FIX — exclude `Status` and `ResolveOwner` from preprocessing, narrow the wait/poll statement, and scope code 4 to mutating modes.

### Task 4 — Lock live gate

The OS gate remains synchronized, dual-host, and mutation-tested. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:254-275`.

PASS

### Task 5 — Login wrapper

The binder boundary, code 5, release precedence, opposite-direction client oracle, bootstrap, and temporal stream test are correctly applied. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:292-315`.

Code 3 is still described only as “live contention,” although preserved lock code 3 also covers exclusive-handle contention during acquire or release. Widen it to “lock contention: exclusive handle or LIVE holder.” `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:302`; compare the lock definition at `:169`.

FIX — widen code 3’s description to every preserved lock-code-3 condition.

### Task 6 — Builder

The actual ordering is now correct: acquire uses the resolved debate home, custody output remains inside the guarded `try`, completion is set only after emission, and remove reuses the same path identity. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:324-344`.

The new emission-failure oracle is not frozen at the required point. It refers to `PARALLAX_LANE_HOME_FAULT` at the old post-credential location while also saying it fires after rendering. Those are different paths, and a pre-render fault cannot prove the completion/output boundary. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:338,352`; the current seam is at `tools/new-kimi-lane-home.ps1:416-423`.

Freeze this exactly: move `PARALLAX_LANE_HOME_FAULT` to immediately after custody JSON construction and immediately before emission. Its test requires no stdout, home cleanup, and a `free` persistent lock. That placement catches any implementation setting `$buildCompleted` after rendering.

The Task 6 file list still says this task modifies the selector and guard, while Step 2 says Task 2 already did so. Remove that stale parenthetical from the file list. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:322,353`.

FIX — freeze the existing fault seam immediately before custody emission and remove the stale selector ownership from Task 6’s file list.

### Task 7 — Live credential gates

The deterministic normalization, no-fallback rule, committed-stream secret guard, token comparison safety, and C identity are present as described. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:373-381`.

Three blocking defects remain:

1. The secret guard says every credential string value. Optional credential strings are not constrained to be nonempty, and an empty string occurs in every output. Restrict the comparison to every nonempty credential string value. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:58,115,379`.

2. The guard runs only before writing `probe-record.md`. Other live commands also capture client streams, and a conventional pytest failure message can print them before any guard runs. Require one helper for every live command: inspect both streams against the accumulated set of nonempty credential values before any assertion or failure message; on a match, fail naming only the field. The probe-record guard then uses that same helper. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:30,379-391`.

3. Only C’s lock custody is defined, but A and B perform authenticated dispatches. Because access credentials expire and dispatch can refresh them, A/B may mutate their credentials despite the claim that every fixture mutation is locked. This is an inference from the measured refresh behavior, not a claim that they necessarily refresh on each run. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:43,371-373,385-391`.

Freeze locking per home:

- Resolve the owner once per module.
- Before every authenticated command against A, B, or C, acquire that home’s lock with that resolved home as both `LaneHome` and `DebateHome`.
- Use one per-home run DebateId, capture its nonce, and release in `finally`.
- Write A and B’s setup markers under their respective locks as well.
- Narrow “C is the only home any test rotates” to “C is the only home the suite deliberately expires and requires to rotate”; A/B may refresh naturally, but only while locked.

FIX — exclude empty secret values, guard every captured live stream before assertions, and lock authenticated A/B operations and marker writes under their respective homes.

### Task 8 — Doctor

The total matrix, seven-step hash algorithm, recovery command shapes, and authenticated-probe literal are now executable without behavioral invention. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:409-453`.

One evidence statement is false: not every recovery-command placeholder comes from `Status`. `lane-home` is configuration supplied to `Status`; it is not printed in the status object. Change the sentence to: “Every confirmation placeholder comes from `Status`; `<lane-home>` is the configured lane home against which status was requested.” `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:234-240,440-447`.

FIX — correct the provenance sentence for `lane-home`.

### Task 9 — Contract

The custom lane home and full removal invocation are correctly applied, and the three regions remain forward-slash-only, cohesive single-pin contracts. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:459-486`.

The final status instruction still requires invention because the tool requires `LaneHome`. Replace “Read the state at any time with `-Status`” with:

`Read the state at any time with tools/kimi-lane-lock.ps1 -Status -LaneHome <lane-home>`.

`docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:153,475`.

FIX — spell out the complete status invocation.

### Task 10 — Final wiring

The five-module extension, parity gate, full suite, final dual-host live rerun, behavioral eval, and failing history oracle remain complete. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:490-512`.

PASS

## Round-5 application audit

Applied correctly:

- Task 1’s exact initial set;
- Task 2’s moved selector and fixture oracle;
- Task 3’s per-state property rule, code 5, and mutating-mode foreign partition;
- Task 5’s binder/code-5/precedence/opposite-direction additions;
- Task 6’s completion boundary and resolved `DebateHome`;
- Task 7’s normalization and two explicit security guards;
- Task 8’s seven-step hash procedure and command templates;
- Task 9’s custom login home and complete remove command. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:79-90,117-125,142-224,302-310,324-352,373-381,430-451,475`.

Introduced or applied incompletely:

- Task 3’s new preprocessing was accidentally applied to non-mutating `Status` and `ResolveOwner`. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:197-202,232-242`.
- Task 6’s new output-failure oracle did not freeze the seam at the output boundary. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:338,352`.
- Task 7 froze only C’s custody even though A/B authenticated dispatches may refresh. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:371-373,385-391`.
- Task 8’s new placeholder-provenance sentence incorrectly included `lane-home`. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:440-447`.

## Overall verdict

FIX. Every item above is BLOCKING under the zero-judgment or oracle-adequacy contracts. I found no separate acceptable-as-is defect and no design escalation.

## Final check

UNVERIFIED: measurements 1–21 remain external measurements recorded by the design rather than current committed gates. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:35-67`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:41-52`.

UNVERIFIED: all proposed pytest and live outcomes because implementation has not begun and no runnable `python` is available; this is not a finding. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:38,490-505`.

UNVERIFIED: Task 1’s current remote-head and Actions assertions; repository-local workflow facts are readable, but current remote state was not refreshed. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:65-71`.

