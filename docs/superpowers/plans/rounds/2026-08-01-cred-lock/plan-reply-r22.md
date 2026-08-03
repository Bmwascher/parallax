Round 21’s three edits are correct, but the plan is not yet at PASS. The sweep found four pre-existing blocking defects; two are the exact failed-measurement pattern you asked me to search for.

The narrowed global command rule correctly covers only emitted, dependent multi-step commands and excludes standalone commands and verification examples. Task 6’s four-row execution matrix now exercises every dependency plus apostrophe escaping. Task 10 now checks `git log`’s exit before interpreting output and tests both dirty history and an invalid range. None of those three edits introduced a defect. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:54`, `:435-448`, `:695-704`.

### Task 1: Repair the Windows CI job

The checker has two decisive conditions—path existence and host parity—with an exact initial set and opposite-direction mutations. A missing file or one-host omission cannot pass. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:109-126`. The broken workflow references are present in both current Windows steps. `.github/workflows/skill-evals.yml:79-99`.

Verdict: PASS.

### Task 2: Credential structural validation

The status partition, precedence, field sorting, exact type rules, duplicate-key directions, unreadable fixture, host selection, and fixture-validation oracle are complete and failure-capable. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:130-161`.

Verdict: PASS.

### Task 3: The lock tool

The wait budget is still underspecified and its current literal procedure can exceed the budget. The only numeric rules are `WaitSeconds >= 0` and `PollSeconds > 0`; they do not define integer versus fractional syntax or range. The protocol then says to sleep the entire poll interval before retrying, while both the spec and shipped literal promise that the wait budget bounds caller patience. With `-WaitSeconds 1 -PollSeconds 10`, a literal implementation may wait ten seconds. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:197`, `:211-215`, `:318`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:275-278`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:660`.

Required blocking fix:

- Freeze both parameters as base-10 integer strings fitting `Int32`; `WaitSeconds >= 0`, `PollSeconds > 0`, otherwise exit 2 without mutation.
- Measure the budget with a monotonic `Stopwatch`.
- Sleep for `min(PollSeconds, remaining budget)`.
- Add a dual-host oracle using `WaitSeconds=1`, `PollSeconds=10` that contends, exits 3, leaves the record unchanged, and returns before five seconds. Retain the zero-budget immediate-refusal case.

Verdict: FIX — bound polling to the declared wait budget and freeze the numeric domain.

### Task 4: Live lock-protocol gate

Two underspecifications remain.

First, measurement 20 says only to assert divergence and then mutate the assertion to expect agreement. It never requires each host invocation to exit zero or produce a parseable result. One failed host producing empty output while the other succeeds is itself “divergence” and can therefore pass. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:340`, `:344-349`. The required real result is `Int64` ticks on both hosts, with the date value returning `String` on 5.1 and `DateTime` on 7. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:65-66`. This is the same class as the discarded empty-hash measurement. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:89-95`.

Second, the crash oracle says the parent “waits for the marker” while the child then blocks forever, but gives no timeout or failure teardown. A child that dies or wedges before signalling leaves the implementer to invent the bound and cleanup. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:334-340`.

Required blocking fix:

- For measurement 20, require the selected host process to exit 0 and emit exactly one parseable result before inspecting types; assert the host-specific types above. Add a mutation making that subprocess exit nonzero and confirm the gate fails rather than reporting divergence.
- Bound the ready-marker wait at ten seconds. On timeout, terminate the child in a `finally` and fail without inspecting the lock bytes. Only the observed ready marker licenses killing the child and asserting the crash state.

Verdict: FIX — make both live measurements fatal before interpretation and bound crash synchronization.

### Task 5: The lane login wrapper

The ACL contract remains incomplete. The settled design requires the lane home and its credentials directory to receive restrictive ACL protection. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:183-187`. Task 5 specifies only a full-control rule on the lane home, without the rule’s inheritance and propagation flags, and its test merely says the ACL is “asserted.” An implementer can create a non-inheritable ACE and still satisfy that wording while leaving the credentials directory outside the intended protection. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:368-372`, `:384`.

The existing builder demonstrates the missing exact shape: protected DACL, existing access rules removed, current SID, `FullControl`, `ContainerInherit,ObjectInherit`, propagation `None`, `Allow`. `tools/new-kimi-lane-home.ps1:399-408`.

Required blocking fix:

- Freeze that exact ACE shape for the lane home.
- After acquiring the lock and before any credential validation or client invocation, create the credentials directory if absent and apply the same protected DACL directly to it.
- Make the oracle inspect both directories’ exact ACE sets, inheritance flags, propagation flags, and second-run byte-equivalent/idempotent state. Also verify a fake credential created by the client inherits the intended current-SID access rather than merely checking the parent.

Verdict: FIX — freeze and test the complete ACL propagation contract on both protected directories.

### Task 6: The builder stops copying

The four-row recovery-command matrix now covers owner failure, JSON failure, login failure, and success; the apostrophe-bearing success fixture detects missing escaping; fixture routing executes the builder’s emitted line under both hosts without real credentials. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:435-448`. Custody output and lock diagnostic propagation remain compatible with that command. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:402-418`.

Verdict: PASS.

### Task 7: Live credential gates

Item 7 still has the other failed-measurement pattern. It requires a successful command and expected provider line before comparing SHA-256, length, and mtime, but it never requires each pre/post snapshot component to have been measured successfully. Two suppressed hash failures can compare as equal empty or `None` values—the exact shape measurement 17 previously produced. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:543-551`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:89-95`.

Required blocking fix:

- Define one `measure_file_snapshot` helper returning SHA-256, byte length, and mtime only after all three measurements succeed; any read, hash, or stat failure terminates the main phase before equality is evaluated.
- Never represent a failed measurement with an equality-comparable sentinel.
- Add offline support oracles forcing a pre-command hash failure and a post-command stat failure; each must fail, still attempt the real `-Remove`, and follow the existing cleanup-precedence matrix.

Verdict: FIX — require complete successful snapshots before the invariance comparison.

### Task 8: The doctor stops touching credentials

Every measurement failure has a consuming state: unreadable version, validator failure, present-file hash failure, disappearance, and lock-status failure all contribute `BROKEN`; missing hash values are explicitly never compared. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:595-625`. The `UNKNOWN` and foreign-host rows are disjoint and explicitly pinned. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:608-613`, `:640-644`.

Verdict: PASS.

### Task 9: The contract

All three exact literals remain internally aligned with Tasks 3, 6, and 7. The normalized comparison uses the repository’s actual normalization and substring semantics, while the sentence-deletion mutation makes the coverage oracle fail. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:654-675`; `evals/multi-model-verify/test_contract_coverage.py:21-30`, `:517-526`, `:666-683`.

Verdict: PASS.

### Task 10: CI wiring, version, and full gate

The round-21 history repair is correct: `$LASTEXITCODE` is captured immediately, nonzero throws before output interpretation, and both dirty-history and invalid-range failure directions are required. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:695-704`. The other gates require path-check exit zero, four exit-zero global runs, dual-host live execution, and zero skips. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:683-694`.

I found no second Task 10 measurement interpreted before its success was established.

Verdict: PASS.

## Overall verdict

FIX. Do not change the header to FROZEN yet. The four blocking fixes are:

1. Task 3: bound polling and freeze wait/poll numeric semantics.
2. Task 4: require successful host measurements and bound crash synchronization.
3. Task 5: freeze and decisively test the complete ACL propagation contract.
4. Task 7: make every snapshot component successful before comparing invariance.

The Task 4 and Task 7 findings are additional instances of the exact pattern you asked me to sweep for. The Task 3 and Task 5 findings are underspecifications, not defects introduced by round 21.

## Final check

UNVERIFIED:

- Measurements 1–21 remain external measurements, not reproducible from repository files alone. The spec explicitly distinguishes them from repository live gates. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:35-39`, `:348-354`.
- Three simultaneous lane logins remain a generalization of measurement 11, which established two; the plan’s loud refusal direction is verifiable only during setup. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:482`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:57`.
- The remote-branch and branch-filtered Actions claims were not re-run here. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:101-105`.
- The retained fable report’s provenance cannot independently prove exact transcription; the artifact states that limitation itself. `docs/superpowers/plans/rounds/2026-08-01-cred-lock/fable-whole-plan-review-2.md:20-24`.
- No implementation exists, so none of the planned pytest or live gates can yet verify built behavior. This is not a finding.

