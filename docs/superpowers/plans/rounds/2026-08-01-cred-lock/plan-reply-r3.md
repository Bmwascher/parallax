## Task 1 — Repair Windows CI

The checker has a real RED state, a positive mutation check, portable execution, and an explicit two-phase workflow repair. Recreating the lock test later no longer acts as its only oracle. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:81-109`

The recorded remote-ref and Actions checks are now evidence capable of supporting the narrowed “never pushed/run” conclusion; I did not independently rerun the network-facing checks in this sandbox. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:83-87,551-564`

**Task 1 — PASS.**

## Task 2 — Credential structural validation

1. **Multiple simultaneous defects have no deterministic `detail`.** A document can carry a missing field, a wrong type, and a blank token together, but the output contract permits only one detail and provides no precedence. Add a fixed validation order and multi-defect tests—for example: missing-field, then wrong-type, then blank-token. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:128-147`

2. **`fields` ordering says two different things.** “Ordinal byte order” is ambiguous between .NET ordinal string comparison and ordering UTF-8 bytes. Name the exact comparer or encoding. Also enumerate the statuses that produce `[]`: absent, unreadable, not-json, and not-object. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:130-143`

The integer boundary is otherwise complete: both supported parsed integer types are named, overflow is excluded, and `0`, past expiry, fractions, booleans, null, and numeric strings each have a disposition and test. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:143-151`

**Task 2 — FIX:** add defect precedence and an exact field-name ordering rule.

## Task 3 — Lock tool

1. **The acquire table overlaps and excludes states while claiming completeness.** Row 4’s “either” includes a supplied matching nonce, which belongs to row 3; row 5’s “any identity field” includes nonce, overlapping row 4 again. Foreign-host, malformed, unreadable, and handle-contention states are outside the table despite “No other outcome exists.” Change row 4 to “non-nonce fields equal; nonce absent or supplied-different,” row 5 to “any non-nonce identity field differs,” and narrow the completeness claim to readable, well-formed, same-host record states. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:216-240`

2. **Release and override behavior on non-held inputs is missing.** The plan does not say what `-Release` or `-ForceRelease` does to `free`, or what `-MalformedOverride` does to a readable well-formed record. These need explicit state rows and tests. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:232-265`

3. **Foreign-host recovery is contradictory.** Every mutation of a foreign-host record is assigned exit 4, but Task 8 promises an override command. `-ForceRelease` also lacks `-ConfirmHost`, even though host is part of complete identity. Either add `-ConfirmHost` and expressly permit force-release of an exactly confirmed foreign-host record, or remove the doctor’s override promise and define another recovery. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:181-206,234-250,436-452`

4. **Status handle contention remains unspecified.** Status takes the exclusive handle but has neither wait parameters nor a stated immediate-contention rule. Add wait/poll parameters or say its failed exclusive open exits 3 immediately. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:181-195,203-214,242-250`

5. **“Every invocation has no exit 1” is not yet executable.** PowerShell parameter-binding failures occur before a script-level top-level catch. The plan must require manually parsed/validated parameter values or narrow the guarantee to successfully bound invocations. It must also map owner-resolution failure and all unclassified runtime failures to a specific documented code. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:181-206,252-265`

6. **Validation edges remain open.** Define `WaitSeconds >= 0`, `PollSeconds > 0`, `ConfirmSha256` as exactly 64 hex characters, whether unknown lock-record fields are malformed, and the required type/nonblankness of `host` and `debateHome`. “Free is exactly…” settles extra fields for free but not for held. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:63-77,173-206,232-240`

7. **The status wording is internally inaccurate.** It says status exits 0 for every “parseable” state including MALFORMED, although malformed includes non-JSON and zero-length bytes. Say “every readable file state”; unreadable remains exit 6. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:235-250`

**Task 3 — FIX:** repair the state-table partition, add release/override tables, resolve foreign-host recovery, and finish parameter/schema/error mappings.

## Task 4 — Live lock-protocol gate

1. **The crash setup can pass without proving the intended crash point.** “Zero-length or partial” does not prescribe synchronization proving the child acquired, truncated, and was killed before completing a valid record. Require an initially valid record, a child signal after truncate-and-flush, the child blocking before any rewrite, then kill and assert exactly zero bytes. If partial-write recovery is also required, make it a second exact-prefix fixture. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:288-306`

2. **The focused verification command exercises only the selected/default host.** The module is instructed to honor `PARALLAX_PS_HOST`, while the command sets neither host despite claiming both are required. Show two explicit invocations, or state that the focused gate covers one selected host and Task 10 completes the matrix. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:31,267-277,281-306`

**Task 4 — FIX:** prescribe crash synchronization and an executable two-host focused gate.

## Task 5 — Lane login wrapper

1. **The stream contract remains mechanically unresolved.** An inherited interactive child writes its stdout to the wrapper’s stdout handle, so “inherited, untouched” conflicts with wrapper stdout containing only verdict JSON. Specify the actual mechanism: redirect and relay child stdout to stderr, or move the machine-readable verdict to a dedicated file. The test stub must emit both stdout and stderr so the oracle exercises this path. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:316-341`

2. **Post-login unreadable credentials are omitted from the failure rule.** Success requires structural validity, but the exact sentence names only absent and malformed. Add unreadable and test it. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:328-341`

3. **The complete wrapper order is still open.** Define when the lane directory/ACL is created, when the lock is acquired, and whether the existing-credential check happens under that lock. Otherwise two wrappers can inspect or alter the shared lane state outside serialization. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:316-340`; the settled login-under-lock requirement is at `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:135-142,307-318`.

**Task 5 — FIX:** choose an implementable stream mechanism, include unreadable failure, and freeze the complete lock/ACL/validation order.

## Task 6 — Builder

1. **The success JSON lacks a planned oracle.** Tests must assert stdout is exactly one JSON line with exactly `debateHome` and `nonce`, and that removal is performed using the returned nonce rather than reading the lock directly. Otherwise lock-tool output can contaminate the stream and nonce custody can remain broken while the listed filesystem tests pass. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:359-385`

2. **“Release on refusal in a `finally`” is ambiguous on success.** An unconditional finally releases the successful build immediately. Require a success flag: release in cleanup only when build did not complete; successful build retains the lock until remove. Also define which error wins if failure cleanup itself cannot release. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:369-375`

3. **Guard failure after remove’s identity check is unspecified.** If the sentinel or dangerous-root guard refuses, state explicitly that deletion does not occur and the pre-existing held lock remains held; test both home and lock unchanged. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:373-385`; the current guards are at `tools/new-kimi-lane-home.ps1:65-133`.

4. **Remove stdout is not frozen.** The idempotent acquire and release both produce output, while the existing builder prints `removed <path>`. Specify whether remove preserves that one line, returns JSON, or is silent, and require internal lock output to be captured. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:359-375`; `tools/new-kimi-lane-home.ps1:131-133`

5. **`DebateId` custody is missing.** The owner and nonce have explicit generation/retention rules, but the driver is never told how to generate one unique stable debate token or retain it through remove. Add it to the call lifecycle and builder tests. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:73-76,359-375,487-489`

The three junction assertions themselves now close the earlier vacuity, including the stray-copy case. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:377-385`

**Task 6 — FIX:** test exact nonce JSON, make cleanup conditional, settle guarded-remove/output behavior, and define DebateId custody.

## Task 7 — Live credential gates

1. **The fixture contract contradicts the coexistence test.** Both A and B are supplied as existing independent logins and the suite “never creates a login,” but measurement 11’s sequence says the suite creates B between two A dispatches. Choose one executable model. If both are pre-provisioned, require evidence that A was logged in before B and test A and B afterward; otherwise define an interactive/manual B-creation phase outside automated pytest. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:399-426`

2. **Three credential roles are mapped onto only two homes without assignment.** Specify which home is A, B, and the expendable refresh fixture, and the exact test order/reset policy after forced expiry and token rotation. Otherwise tests can invalidate one another or depend on pytest ordering. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:404-416`

3. **The positive-control outputs are still descriptions, not exact oracles.** Supply the prompt and expected reply for dispatch, plus the precise client error token/message that identifies absolute-key credential-resolution failure. “Expected reply” and “client’s own message” still require live invention. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:408-416`

4. **Direct fixture mutation is not placed under the lane lock.** Forced expiry and the write-through mutation alter shared credential state. Require acquisition with a fixture-specific debate identity around each mutation/dispatch sequence, or state that these disposable homes are exclusively owned by this gate and prove no other process uses them. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:399-418`; the lock’s stated purpose includes shared lane-home integrity at `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:307-318`.

**Task 7 — FIX:** reconcile login creation, assign fixture roles/order, freeze live command oracles, and serialize fixture mutations.

## Task 8 — Doctor verdict matrix

1. **There is no aggregate-verdict rule.** Check 8 can simultaneously see credential `ok`, hash mismatch, and a DEAD lock, but the matrix does not say which verdict the single doctor row receives. Add explicit precedence and short-circuiting—for example binary absent → N/A; otherwise `BROKEN > STALE > OK`, while still reporting every substate. `commands/doctor.md:5-9`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:430-455`

2. **Absent credential conflicts with hash failure.** Absent is N/A, but “either hash cannot be taken” is BROKEN. State that hashing is not attempted when the validator returns absent; the hash-failure rows apply only to a present credential path. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:438-453`

3. **Foreign-host override is currently impossible.** The matrix promises an override command, while Task 3 assigns foreign-host records exit 4 for mutations and provides no `-ConfirmHost`. Resolve Task 3 first, then give separate exact doctor commands for foreign-host force-release and malformed hash-release. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:183-206,234-250,448-455`

4. **Hash ordering is not exact.** To prove the validator/doctor did not mutate the file, prescribe: confirm present; take hash 1 successfully; run validator; take hash 2 successfully; compare. For unreadable files, report the validator and hash failures without comparing missing values. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:436-455`; the discarded false measurement is recorded at `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:89-95`.

**Task 8 — FIX:** add aggregate precedence, absent/hash short-circuiting, executable override commands, and exact hash order.

## Task 9 — Contract literals

### Literal checks

- **Backslashes:** PASS. None of the three proposed literals contains a backslash, satisfying the reference-file rule. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:27,479-489`

- **Region size:** PASS. Each is one cohesive subject and is within the scale already used by whole pinned regions such as freshness and per-round evidence. No further split is required now. `skills/multi-model-verify/references/backup-lane.md:97-151`; `CLAUDE.md:55-92`

### Defects

1. **`lane-home-isolation` overstates the evidence as a separate account.** The design establishes a dedicated lane login under another home, not necessarily a different kimi-code account identity, and it cannot establish that a user “never dispatches with” it. Say “dedicated lane login distinct from the user’s ordinary login; the lane never falls back to the ordinary credential.” `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:479-482`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:122-142`

2. **`lane-lock` says contention always waits despite the zero default.** Change it to “waits up to the caller-supplied budget; a zero budget refuses immediately.” Also narrow “a well-formed record” to “a well-formed held record.” `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:195,483-485`

3. **`lane-lock-call-lifecycle` still requires command invention.** It supplies concepts but no exact resolve/build/remove/login commands, no JSON-field extraction, and no DebateId generation. The shipped contract currently contains the old executable commands; removing them for prose would reduce operational precision. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:487-495`; `skills/multi-model-verify/references/backup-lane.md:47-67`

4. **The abandoned-debate sentence misstates the transition.** Session exit does not free or rewrite the lock; the record remains held, becomes DEAD by liveness, and is reclaimable only on a later acquire. Say exactly that. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:228-240,487-489`

5. **The deterministic region comparison is underspecified and likely compares the wrong bytes.** Markdown wrapping and Python adjacent literals cannot be raw-byte identical. Use the repository’s existing normalized region and AST pin extraction, then hash the UTF-8 bytes of those normalized runtime strings. Length and hash equality of raw source slices is not the contract checker’s equality. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:491-501`; `CLAUDE.md:55-85`; `evals/multi-model-verify/test_contract_coverage.py:21-30,217-249,517-526`

**Task 9 — FIX:** amend all three semantic points, add executable lifecycle commands, and define comparison over normalized runtime values. No additional region split is required.

## Task 10 — CI wiring, version, full gate

The offline/live CI separation and final-head rerun are now correct. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:505-527`

**The history command is not a failing oracle.** `Select-String` prints matches but does not make the step fail merely because it found one. Replace it with an explicit branch that prints matches and throws/exits nonzero; then mutation-test it with a temporary known matching commit-message fixture or a controlled input string. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:529-535`

**Task 10 — FIX:** make the history check mechanically fail on a match.

## Overall verdict

**FIX.** R2 closes the round-1/2 defects it set out to close, but introduces four build-surviving issues that remain blockers:

- Task 3’s state tables still overlap and leave release/foreign-host recovery undefined.
- Task 5’s interactive-stream and machine-readable-output requirements are not jointly implementable as written.
- Task 7’s fixture contract forbids creating B while its coexistence oracle requires creating B.
- Task 8 promises a foreign-host override that Task 3 forbids.

The contract literals need semantic amendment but do not need another structural split.

## Final check

- **UNVERIFIED:** measurements 1–21 remain external empirical results, not reproduced from repository tests here. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:35-67,348-365`

- **UNVERIFIED:** the newly recorded remote and GitHub Actions checks supporting “never pushed/run”; I read their recorded results but did not rerun the network-facing commands. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:83-87,551-564`

- **UNVERIFIED:** all new Python/pytest gates. No Python executable is available in this sandbox and no implementation exists.

- **Verified from the rewritten plan:** all three proposed contract literals contain zero backslashes, and none presently requires another region split. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:477-489`

No files changed.