## Task 1 — The lock tool

1. **`OpenOrCreate` silently converts a pre-existing empty/truncated lock into `free`.** The plan says an empty file means “just created by this open,” but `OpenOrCreate` cannot distinguish a newly created file from an existing zero-length file. That contradicts both rule 7’s “malformed is held” requirement and the settled design’s explicit create-new-then-open-existing sequence. A crash after `SetLength(0)` would therefore make the next caller steal the lock. Add a create-new attempt followed by an existing-file open, and test a pre-existing empty file as `MALFORMED`, recoverable only by hash override. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:123-139`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:237-250,269-293`

2. **Idempotent acquire is unimplementable through the declared interface.** Rule 3 requires the caller to match the recorded nonce, but `-Acquire` has no `-Nonce` parameter; only `-Release` accepts one. Returning the stored nonce merely because the other fields match would make the nonce no longer an ownership credential. Add optional `-Nonce` to acquire: omit it only for first acquisition of a free/dead record; require it for idempotent re-acquire. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:95-105,132-142`

3. **Retry behavior is missing for release and both overrides.** The common state-changing protocol says to retry with `-PollSeconds` until a wait budget expires, but those parameters exist only on acquire. The implementer must invent whether other modes wait, spin, or fail immediately. Put `-WaitSeconds` and `-PollSeconds` on every mutating parameter set, or explicitly specify immediate exit 3 for non-acquire modes. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:95-108,123-128`

4. **Malformed status has contradictory exit semantics.** Rule 7 and the exit table assign malformed records exit 4, while `-Status` promises a `MALFORMED` JSON result and exit 0. Specify that exit 4 applies only to attempted mutations; read-only status returns the diagnostic object with 0. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:112-121,137-144`

5. **The record-validation boundary is incomplete.** The plan defines field presence but not exact types or admissible values for `host`, `ownerPid`, `debateHome`, token fields, or decimal time strings; it also does not define host/string comparison casing, nonce generation shape, or numeric parameter ranges. These decisions determine whether corrupt records are held or accepted. Supply the complete schema and comparison rules, including positive PID, digits-only tick strings, token validation, hostname source/casing, and a fixed nonce generator/format. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:87-110,130-142`

6. **The “exhaustive exit-code” test is not exhaustive.** Producing each documented code once does not detect an undocumented exit 1 from the plan’s instructed `rethrow`, parameter binding, or write failure. Assert the allowed-code set across the complete case matrix and prescribe mapping for all open/read/parse/write/flush failures. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:112-128,152-158`

7. **Rule 5 lacks a deterministic oracle.** “One test per rule” does not say how to force `Get-Process` to succeed while start-time access fails. Without a prescribed test seam or controlled fixture, the implementer must invent a machine-dependent test that may never exercise the catch path. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:130-150`

8. **The dual-host test instruction names a pattern that does not exist.** The cited suite selects one preferred host, and its `_build` helper invokes only that host. Meanwhile CI expects `PARALLAX_PS_HOST` to select each interpreter in separate jobs. Specify the existing environment-selector pattern instead of saying to parameterize “exactly” like this file. `evals/multi-model-verify/test_kimi_lane_home.py:15-21,323-339`; `.github/workflows/skill-evals.yml:79-99`

**Task 1 — FIX:** repair create/open semantics; add acquire nonce input; settle retry/status/error mappings; fully specify record validation; and prescribe deterministic, correctly wired dual-host tests.

## Task 2 — Live lock-protocol gate

1. **The gate tests `CreateNew`, while Task 1 tells production to use `OpenOrCreate`.** It therefore stays green while the empty-existing-file defect survives in built code. Align production with the design’s create-new/open-existing protocol, then make this gate exercise that exact sequence. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:123-127,174-188`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:237-250`

2. **Final-byte equality does not verify durable flush or crash behavior.** The settled live-gate requirements explicitly include durable flush and crash during rewrite; Task 2 only closes the handle normally and checks bytes afterward. Add a child-process crash between truncate and completed rewrite, then verify that the surviving empty/partial file is held as malformed rather than reclaimed. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:183-190`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:348-365`

3. **The tick-type mutation only proves an isolated JSON fact.** Changing the expected type to `String` proves that one assertion is live, but the gate would still pass if the lock implementation wrote date strings. Task 1’s real-record tests must remain the implementation oracle; Task 2 must not call this a regression gate for the implemented representation. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:87-90,154-155,183-200`

4. **The host-availability rule is incompatible with default Linux CI collection.** The full suite runs on `ubuntu-latest`, while Task 2 says absence of either Windows host fails. Define the module as Windows-only, require both hosts when on Windows, and wire it into the Windows job; otherwise the ordinary full gate fails for platform non-applicability rather than a broken protocol. `.github/workflows/skill-evals.yml:15-17,41-57`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:192-200`

**Task 2 — FIX:** connect the gate to the real create/open protocol, add the crash oracle, narrow the tick claim, and specify Windows CI collection.

## Task 3 — Credential structural validation

1. **The output schema still requires invention.** `fields` is not defined as known fields versus every observed field, nor is its order fixed; `detail` has no prescribed values. This prevents exact builder/doctor tests and permits the two consumers to interpret output differently. Define exact details and make `fields` a deterministic ordered list. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:204-229`

2. **“JSON integer” is not mapped to exact PowerShell runtime types.** The tests cover `0` and a string but omit fractional numbers, booleans, null, overflow, and duplicate-key behavior. Specify the accepted parsed types or validate the JSON token lexically, then add those negative cases on both hosts. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:219-229`

3. **The unreadable-file case and host matrix are not prescribed.** The task demands an unreadable result but gives no deterministic Windows fixture and, unlike Tasks 1/2, does not say how both supported hosts execute it despite the global both-host claim. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:9,28,217-243`

**Task 3 — FIX:** freeze the complete JSON-output contract, integer semantics, unreadable fixture, and dual-host matrix.

## Task 4 — Lane login wrapper

1. **Interactive login conflicts with “nothing else” on stdout.** A user-performed interactive login needs visible client interaction, while the wrapper promises only the validator verdict. Specify that stdout is reserved for the final JSON verdict and exactly where client prompts/output go. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:247-265`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:135-142`

2. **Environment restoration can be tested vacuously.** A subprocess can never mutate pytest’s parent environment, so merely checking the parent afterward passes even if the wrapper never restores its own environment. Require an in-process PowerShell harness or an observable post-invocation assertion inside the same shell. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:257-264`

3. **Success and existing-home behavior are open.** The plan does not say whether an existing lane home is repaired, reused, or refused, nor whether client exit 0 followed by a malformed/absent credential is wrapper success. Require structural `ok` before success and define the existing-home/re-login path. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:253-266`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:124-156`

4. **Defaults are not fixed in the executable interface.** The prose says `-LaneHome` has a default, but does not state whether `-KimiBinary` defaults to the mandated absolute path or is mandatory. Supply the exact parameter-set declaration. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:22,249-255`

**Task 4 — FIX:** specify stdout routing, a non-vacuous restoration oracle, existing-home/post-login validity behavior, and exact defaults.

## Task 5 — Builder stops copying

1. **The builder cannot release the lock it acquires.** Its added interface contains no nonce; its success output is not changed to return one; yet later `-Remove` must satisfy complete identity. Add nonce custody explicitly—prefer structured build output containing the debate-home path and nonce, plus mandatory `-Nonce` on remove and optional nonce for re-entry. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:276-294`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:132-142`

2. **Wrong-owner removal can destroy the home before discovering it cannot release.** The plan says release occurs after deletion but does not prescribe a pre-deletion ownership check. Require an exact-identity idempotent acquire/check before deletion, and test that identity mismatch leaves both the home and lock byte-identical. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:293-295`; `tools/new-kimi-lane-home.ps1:65-133`

3. **Lock acquisition must precede credential validation, not merely filesystem creation.** Otherwise login can mutate the shared credential between validation and acquisition. State and test the exact order: acquire, validate lane credential, perform all remaining build work, releasing on every refusal. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:288-300`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:193-209,307-318`

4. **The “no file copied” assertion is vacuous.** Any file reached below a correctly targeted junction is necessarily “visible through the junction.” Exact junction type/target plus a physical same-file identity or target-directory inventory is the meaningful oracle. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:288-290`

5. **The claimed all-tests/both-host result is not achievable from the current suite shape.** Existing builder tests select one preferred host, while the plan neither refactors that selector nor adds the suite to the Windows two-host job. `evals/multi-model-verify/test_kimi_lane_home.py:21,323-339`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:294-308`

**Task 5 — FIX:** define nonce custody and removal preflight, acquire before credential inspection, replace the vacuous copy oracle, and prescribe real two-host execution.

## Task 6 — Live junction/credential gates

1. **Absolute-key rejection can pass for the wrong failure.** “Dispatch, assert the failure” accepts an unrelated configuration, network, or authentication failure. Require a successful junction-based control using the same credential/config, then assert the absolute-key case fails at the expected credential-resolution stage. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:317-323`

2. **Refresh and `provider list` need positive command oracles.** The expired-file assertions can pass unchanged because the command itself failed. Require exit 0 and the expected provider output before accepting byte/hash/mtime invariance; require successful dispatch plus rotated lane-file fields for refresh write-through. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:323-327`; the discarded empty-hash measurement demonstrates why command failures must be fatal at `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:89-95`.

3. **Delete-through is not specified as an executable test in this module.** “Covered in Task 5; assert here that both paths are exercised” gives Task 6 no mechanism to know those tests ran, and its verification command executes only the Task 6 module. Invoke both real builder cleanup paths here or remove this row and make Task 5’s dual-host test an explicit prerequisite. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:324-335`

4. **Login coexistence omits the decisive ordering.** The required measurement is that login B does not invalidate A, so A must be proven, B created, then A dispatched again, followed by B. Merely dispatching two pre-provisioned homes does not test invalidation. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:325-326`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:57-59`

5. **Credential provisioning is unspecified.** The suite needs two disposable independent logins for coexistence and an expendable refreshable credential for mutation tests, but the plan defines no environment inputs, setup protocol, or cleanup ownership. That leaves implementers to improvise with real credentials or copies that do not test the stated measurement. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:35,317-329`

**Task 6 — FIX:** provide the disposable-credential fixture contract and positive controls, execute both delete paths directly, and specify the coexistence sequence.

## Task 7 — Doctor

1. **Verdict mapping is open.** The plan does not say how check 8 maps absent, unreadable, malformed, validator failure, hash failure, held-live, held-dead, foreign-host, or malformed-lock states into the doctor’s `OK/STALE/BROKEN/N/A` vocabulary. Supply an exact table. `commands/doctor.md:5-9`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:345-356`

2. **Hash proof can still fail clean-looking.** The plan says “hash before and after” but does not require each hash command to succeed, require a present/readable file before comparison, or define the absent/unreadable report. Explicitly make hash acquisition failure BROKEN/UNAVAILABLE and prohibit comparing missing values. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:347-356`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:89-95,335-346`

3. **The authenticated-probe restriction is not among the listed pins.** The rewrite requires that statement, but the planned tests pin only old-text absence, structural inspection, hashes, lock status, and containment. Add an exact positive pin for the separate locked probe and its refresh disclosure. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:345-356`

**Task 7 — FIX:** add an exact verdict matrix, fail-closed hash procedure, and a pin for the authenticated-probe restriction.

## Task 8 — Contract

1. **The plan does not provide either region’s exact text.** “Rewrite … to the text the region will carry” and a list of required concepts force the implementer to author behavior and corresponding pins. Supply the normalized literals for both `lane-home-isolation` and `lane-lock`. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:367-382`

2. **The shipped operating contract omits the new call lifecycle.** It must say how owner identity is resolved once, how the builder receives it, how the acquire nonce is captured, how every resumed operation retains it, and how cleanup supplies it. The current contract invokes build/remove without any of the planned lock parameters. `skills/multi-model-verify/references/backup-lane.md:47-67`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:282-294,376-382`

3. **“Compare byte counts as the previous cycle did” is not an executable instruction.** Give the exact normalization/compare command and expected relationship. The checker itself is adequate once exact regions/pins exist: it requires a whole-region pin and detects undeclared regions. `CLAUDE.md:55-92`; `evals/multi-model-verify/test_contract_coverage.py:609-683`

**Task 8 — FIX:** supply exact contract text and pins, include full owner/nonce/cleanup orchestration, and replace the historical allusion with a deterministic comparison.

## Task 9 — Version and full gate

1. **The final release gate can pass without Task 6 running.** Task 6 is environment-gated, but Task 9 runs ordinary pytest without setting that variable. Re-run the credential live gate explicitly at final HEAD and require zero skipped after opt-in. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:329-335,394-403`

2. **CI wiring for the new dual-host modules is absent from the plan.** The current Windows job lists selected PowerShell-facing modules; Task 9 modifies only the version file and never adds the new lock-protocol, credential-state, login, or builder suites. Add the workflow to the files list and define which modules are Windows-only versus portable. `.github/workflows/skill-evals.yml:46-99`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:394-401`

3. **The trailer check has no oracle.** “Confirm … stripped” supplies neither a branch range nor a command nor the expected zero-match result, despite the repo’s no-AI-attribution rule. Add an exact `git log --format=%B <fixed-range>` check that fails on any `Claude-Session:` line. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:405`; `CLAUDE.md:3-9`

The `--head` behavioral invocation itself is correct for testing checkout skill changes. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:403`; `CLAUDE.md:18-24`

**Task 9 — FIX:** rerun the opt-in live suite at final HEAD, add explicit Windows CI wiring, and make the history check executable.

## Direct answers

**Q1.** Yes. Rule 3 is unimplementable because acquire cannot receive the nonce; empty-file handling contradicts malformed-is-held; status-malformed has conflicting exit codes; and mutating-mode retry behavior is missing. The schema, error mapping, and parameter ranges also leave necessary cases to implementer judgment. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:95-156`

**Q2.** No documented caller that lost its nonce can re-acquire while its owner remains live. The ordinary acquire interface cannot present the nonce, and force-release also requires it. The lock remains held until the owner dies or a human reads unprescribed raw state and improvises recovery. That is a live-session deadlock, not acceptable idempotence. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:95-105,132-142`

**Q3.** If `-Remove` is never called, the debate home remains, the lock remains `held` while the owner process lives, and later debates contend. Once the owner dies, the next acquire may reclaim the lock, but the abandoned home remains. The doctor can report `LIVE`; it is explicitly forbidden to infer abandonment, and no task automatically detects the missing removal. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:135-146,291-295,347-356`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:275-298`

**Q4.** Task 2’s create-new gate is disconnected from the planned `OpenOrCreate` implementation, and its final-byte check does not test crash/durability. Task 6’s bare “assert failure,” unchanged-file, cross-module delete, and unordered coexistence checks can all pass without establishing their claimed behavior. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:174-200,317-335`

**Q5. Open points:**

1. **Accept resolve-once/pass-explicitly**, because the spec records that nested-shell derivation selects the wrong process. The contract and tests must prescribe the single resolution point and exact propagation, not merely expose `-ResolveOwner`. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:67-82`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:146,421`

2. **Keep the lock in the builder.** The builder is the operation that links the debate home to shared lane state, while the login wrapper independently locks mutation of that same state. The parameter cost is acceptable; the actual defect is omission of nonce custody and removal preflight. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:307-318`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:276-300,422`

3. **Keep credential/client live gates out of ordinary CI, but make them a mandatory recorded local release gate.** Current ordinary CI is explicitly deterministic and makes no model calls. The OS-only lock gate belongs in the existing Windows job; when the live credential opt-in is set, missing setup must fail and zero tests may skip. `.github/workflows/skill-evals.yml:1-5,46-99`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:329-335,423`

## Overall verdict

**FIX — do not hand this plan to a zero-judgment implementer.** The lock can reclaim a crash-truncated record, acquire idempotence and builder removal cannot carry the nonce, and several live gates can pass on unrelated failure or without exercising production behavior. Those defects cross Tasks 1, 2, 5, 6, and 8 and would survive into built code. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:95-200,276-335,367-390`

## Final check

- **UNVERIFIED:** empirical measurements 1–21. I verified that the design records those results and their claimed boundaries, but not the underlying external trials against kimi-code, credentials, junction refresh, two logins, process ownership, or both PowerShell hosts. The spec itself identifies them as measurements made on this machine and says the repository cannot verify the external measurements. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:35-67,348-365`

- **Verified statically:** the deleted lock really contains the three named traps—45-minute age staleness, last-writer-wins acquisition, and formatted date timestamps. `775472c^:tools/kimi-lane-lock.ps1:10-23,63-73,270-277`

- **UNVERIFIED:** all proposed pytest gates. No Python executable was available, no implementation exists, and no code changed; this is not a finding against the plan’s current test result. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:30-35,148-170`

