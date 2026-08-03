Not yet PASS. Three round-22 fixes close their defects completely; Task 3’s production rule is correct but its new oracle covers only the upper bound. Your Task 5 ordering question also exposes a separate pre-existing first-use hole in Task 6.

### Task 1: Windows CI repair

Existence, host parity, and both mutation directions remain decisive. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:102-127`.

Verdict: PASS.

### Task 2: Credential structural validation

The result partition, precedence, type edges, duplicate-key directions, and dual-host fixture oracle remain complete. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:131-162`.

Verdict: PASS.

### Task 3: The lock tool

The implementation rule is now correct: integer domains are frozen, elapsed time is monotonic, and sleep is clamped to the remaining budget. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:198-220`.

The oracle is still one-directional. A broken implementation that immediately exits 3 without waiting satisfies every stated assertion: it contends, exits 3, preserves the record, and returns under five seconds. The older four-second test likewise asserts no elapsed lower bound. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:222`, `:325`. That contradicts the settled requirement that contention waits and retries. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:275-278`.

Required blocking fix:

- For the `WaitSeconds=1`, `PollSeconds=10` case, require elapsed time to be at least 0.8 seconds and under five seconds.
- Add a retry-success oracle under both hosts: create a real LIVE holder; start a contender with `WaitSeconds=4`, `PollSeconds=1`; after one second assert the contender has not exited; release the original holder; require the contender to acquire before its budget expires, return a new nonce, and leave its own held record. This catches both immediate refusal and sleep-without-retry implementations.

Verdict: FIX — add the missing lower-bound and successful-retry directions.

### Task 4: Live lock-protocol gate

Both amendments are adequate. Type inspection now occurs only after exit 0 and exactly one parseable result, with a nonzero mutation; crash-state inspection occurs only after the bounded ready signal. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:341-358`.

Verdict: PASS.

### Task 5: Lane login wrapper

The ACL change is correctly applied. It freezes the complete ACE shape, applies it directly to both required directories, and tests the exact rules, inheritance, propagation, idempotence, and credential-file inheritance. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:377-393`. That matches both the existing builder idiom and the settled two-directory requirement. `tools/new-kimi-lane-home.ps1:399-408`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:183-187`.

Creating `credentials` after acquiring the lock is correct and introduces no Task 5 defect.

Verdict: PASS.

### Task 6: Builder stops copying

Your ordering conclusion is correct only when the lane home already exists. In that case, Build acquires, the validator reports the missing credential, and create/junction/render is never reached. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:421-425`.

Before any login has ever run, however, the entire lane home can be absent. Task 5 is the only task instructed to create it before acquiring. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:377-381`. Task 6 instead acquires first, while Task 3’s missing-file protocol creates only the lock file and gives no rule for creating its absent parent directory. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:212-226`. Therefore Build can fail during Acquire before reaching credential validation and before emitting the exact login command required for an absent credential. That violates the shared recovery-command rule and the settled unavailable disposition. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:80-88`, `:421-443`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:140-142`.

Required blocking fix:

- Add one bounded pre-lock exception to Task 6: test only whether the configured lane-home directory exists.
- If it is absent, emit the exact shared lane-login recovery command, exit nonzero, and create nothing—no lane home, lock, or debate home. Do not invoke the lock tool.
- If the lane home exists, preserve the current lock-first order; an absent `credentials` directory or credential file is then measured under the lock.
- Add both tests: entirely absent lane home refuses with the complete command and no mutation or lock invocation; existing lane home with absent credential acquires, validates `absent`, emits the same command, and releases.

Verdict: FIX — define and test first use when the entire lane home is absent.

### Task 7: Live credential gates

The snapshot fix is complete. The helper cannot return partial measurements or equality-comparable failure sentinels, and both pre-hash and post-stat failures reach offline support oracles with cleanup. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:552-567`, `:575-587`.

Verdict: PASS.

### Task 8: Doctor

Every failed measurement remains consumed explicitly, and missing hashes are never compared. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:607-637`.

Verdict: PASS.

### Task 9: Contract

The exact regions and normalized whole-pin oracle remain unchanged and adequate. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:660-687`.

Verdict: PASS.

### Task 10: Final wiring

The workflow, exit-zero gates, dual-host live rerun, and fatal-first history check remain adequate. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:691-716`.

Verdict: PASS.

## Overall verdict

FIX. Two blocking amendments remain:

1. Task 3 needs lower-bound and retry-success wait oracles.
2. Task 6 needs an explicit first-use branch for an entirely absent lane home.

Do not finalize the record or change DRAFT to FROZEN yet. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:5`.

## Final check

UNVERIFIED:

- Measurements 1–21 remain external to the repository’s test suite. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:35-39`, `:348-364`.
- Three simultaneous lane logins remain a generalization of the two-login measurement. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:491`.
- The remote-branch and branch-filtered Actions claims were not re-run here. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:102-106`.
- The retained fable report’s exact transcription provenance is independently unverifiable by its own stated limit. `docs/superpowers/plans/rounds/2026-08-01-cred-lock/fable-whole-plan-review-2.md:20-24`.
- No implementation exists, so no planned runtime or pytest gate was runnable against built behavior.

