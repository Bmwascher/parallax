Round 30 is closed, but Task 7 is not ready. Your pin finding is correct, and the full read found additional blocking defects—most importantly, the post-command secret merge currently happens after captured streams become assertion-visible.

## Answers

### 1. The pin is a locking assertion

The ordinary live run must read an existing committed record and compare the complete normalized stderr against it. It must never create or rewrite the record. The plan says both “measured once, then pinned” and “the pin is the COMPLETE normalized stderr,” which is stronger than merely documenting each run ([docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:610](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:610), [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:612](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:612)). The current implementation unconditionally creates and rewrites it ([evals/multi-model-verify/test_lane_credential_live.py:249](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_lane_credential_live.py:249)).

Freeze this behavior:

- Normal run:
  - Missing, unreadable, or malformed record: FAIL before running the absolute-key case; write nothing.
  - Existing record: run the positive control and absolute-key case twice; require the two complete `(exit, normalized stdout, normalized stderr)` tuples to match.
  - Independently require nonzero exit.
  - Require current normalized stderr to equal the committed pinned stderr.
  - Leave the record byte-identical.

- Explicit refresh:
  - Exact opt-in: `PARALLAX_LANE_PROBE_RECORD_REFRESH=1`.
  - Any other nonempty value refuses.
  - Run the positive control and absolute-key case twice, apply the secret guard, require complete tuple stability and nonzero exit, then atomically create or replace the record.
  - A failure or unstable measurement writes nothing.
  - The resulting diff requires human review before commit.

The full tuple must be stable because the record currently stores exit, stdout, and stderr while only stderr is compared between the two measurements ([evals/multi-model-verify/test_lane_credential_live.py:238](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_lane_credential_live.py:238), [evals/multi-model-verify/test_lane_credential_live.py:250](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_lane_credential_live.py:250)). Cross-run pinning remains scoped to normalized stderr, as the plan specifies.

Required offline oracles: matching record passes without writing; mismatch fails without writing; absent record fails without writing; explicit refresh creates it; unstable refresh writes nothing; secret match writes nothing.

**Task 7 finding 1: FIX — BLOCKING.**

### 2. An unrun live gate cannot produce an ordinary merge PASS

CI intentionally excludes the credential-bearing live module, so green CI cannot satisfy the live gate ([docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:775](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:775)). Task 10 separately requires both final live runs with zero skipped ([docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:779](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:779)). The ledger correctly records that this gate is unrun and that measurements 5, 6, 7, 10, 11, 16, and 17 therefore remain unverified ([docs/superpowers/plans/rounds/2026-08-01-cred-lock/build-ledger.md:46](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-01-cred-lock/build-ledger.md:46)).

Recommended outcome: run it on this or another Windows machine after the three manual logins. Until then, Task 10 is blocked.

If the user explicitly authorizes merging without it, reopen Task 10 and record:

- `VerificationStatus: DEGRADED`, never `FULL`;
- degradation: `Task 7 credential-bearing live gate UNRUN`;
- the exact seven unverified measurements;
- explicit user risk acceptance;
- no claim that Task 7 or Task 10 passed their original frozen gates.

The attestation interface supports only `FULL` or `DEGRADED`, not `PARTIAL` or `UNRUN` as a status value ([skills/multi-model-verify/SKILL.md:308](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:308)). Your stated inclination is not yet explicit authorization to weaken the frozen merge gate.

**Task 10: ESCALATE — LIVE GATE UNSATISFIED.**

## Additional Task 7 findings

### 2. The new-token secret guard runs in the wrong order

The plan requires re-reading and merging newly issued credential values before scanning or exposing the captured streams ([docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:622](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:622), [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:625](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:625)). Instead, `dispatch_and_guard` scans only the pre-command set and returns the streams ([evals/tools/lane_credential_live_support.py:607](C:/Users/Brandon/Documents/parallax/evals/tools/lane_credential_live_support.py:607)); the refresh test then performs assertions before re-reading the rotated credential ([evals/multi-model-verify/test_lane_credential_live.py:299](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_lane_credential_live.py:299)).

That can expose a newly issued token through pytest assertion output. The offline “rotation” oracle does not exercise this path: it merges a prewritten credential, then launches a separate command that emits the value ([evals/multi-model-verify/test_lane_credential_live_support.py:626](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_lane_credential_live_support.py:626)).

FIX:

- Make capture, post-command credential re-read/merge, stream scan, and return one indivisible helper operation.
- Accept a locked post-capture merge callback or credential path.
- Apply the same order to normal completion and timeout partial streams.
- If the re-read fails, expose no captured stream and raise the sanitized read failure.
- Replace the oracle with one fake command that both writes a new credential value and emits that same new value during the same invocation.

**Task 7 finding 2: FIX — BLOCKING, SECURITY.**

### 3. The failed-build cleanup test never acquires the lock

The test uses an invalid model and describes the builder’s safe-token refusal ([evals/multi-model-verify/test_lane_credential_live.py:331](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_lane_credential_live.py:331)). The builder explicitly rejects that model before any filesystem or lock interaction ([tools/new-kimi-lane-home.ps1:609](C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-home.ps1:609)). It therefore does not exercise the failed-build cleanup path required by item 4 ([docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:634](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:634)).

Replace it with `PARALLAX_LANE_HOME_FAULT=1`. That seam fires after acquisition and debate-home construction but before custody emission, causing the real internal cleanup and release ([tools/new-kimi-lane-home.ps1:895](C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-home.ps1:895), [tools/new-kimi-lane-home.ps1:943](C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-home.ps1:943)).

**Task 7 finding 3: FIX — BLOCKING.**

### 4. “Contention during the command” is tested after the command

The plan requires contention while the fake command is still running ([docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:648](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:648)). The current fake command exits before the second acquire occurs ([evals/multi-model-verify/test_lane_credential_live_support.py:301](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_lane_credential_live_support.py:301), [evals/multi-model-verify/test_lane_credential_live_support.py:308](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_lane_credential_live_support.py:308)).

Use readiness/release signals: block the fake command, observe readiness, attempt and require contention, then release the fake command and finish cleanup.

**Task 7 finding 4: FIX — BLOCKING.**

### 5. Thrown cleanup failures mask the main failure

`custody_of` calls `remove_lane_home` inside `finally`; if that Python call raises due to launch failure or timeout, control never reaches the saved-main-exception rethrow ([evals/tools/lane_credential_live_support.py:408](C:/Users/Brandon/Documents/parallax/evals/tools/lane_credential_live_support.py:408)). `seed_hold` has the same structure around `lock_release` ([evals/tools/lane_credential_live_support.py:455](C:/Users/Brandon/Documents/parallax/evals/tools/lane_credential_live_support.py:455)). That contradicts the frozen precedence for every main and seed phase ([docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:600](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:600)).

Capture cleanup invocation exceptions separately; rethrow the main failure first, otherwise report the cleanup failure. Add thrown-timeout/launch-failure directions for custody and seed—not only nonzero-return directions.

Also parameterize simultaneous Remove refusal across pre-command, command/capture, merge, and guard failures; the current combined refusal test reaches only command launch failure ([evals/multi-model-verify/test_lane_credential_live_support.py:369](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_lane_credential_live_support.py:369)).

**Task 7 finding 5: FIX — BLOCKING.**

### 6. Live-home routing is not protected against dangerous or aliased inputs

The suite claims never to touch the user’s ordinary credential and requires three dedicated roles ([docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:551](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:551), [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:568](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:568)). Setup currently checks only that each configured path is a directory with an `ok` credential ([evals/tools/lane_credential_live_support.py:693](C:/Users/Brandon/Documents/parallax/evals/tools/lane_credential_live_support.py:693)).

Before any seed or mutation, fail unless:

- A, B, and C resolve to three pairwise-distinct physical directories;
- none resolves to a drive root or the real `USERPROFILE`;
- none equals or resolves beneath the real `USERPROFILE\.kimi-code`;
- every safety measurement succeeds.

Add offline fixtures for C aliasing A, case-only aliases, junction aliases, drive root, profile root, and the ordinary `.kimi-code` tree.

**Task 7 finding 6: FIX — BLOCKING, SAFETY.**

### 7. The per-home debate ID is regenerated per operation

The plan freezes one debate ID per home for the module run ([docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:585](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:585)). The implementation generates a new ID for each custody operation, including repeated use of C and repeated A dispatches ([evals/multi-model-verify/test_lane_credential_live.py:209](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_lane_credential_live.py:209), [evals/multi-model-verify/test_lane_credential_live.py:367](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_lane_credential_live.py:367)).

Create one module-scoped mapping `{A, B, C} -> debateId` and use it for seeding and every later operation against that home.

**Task 7 finding 7: FIX — BLOCKING.**

### 8. Item 6 omits its positive control and copies the real config wholesale

The routing table specifies a structurally valid fake credential alongside garbage and absent cases, and every live item must begin with a positive control ([docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:580](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:580), [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:629](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:629)). The implementation runs only garbage and absent cases ([evals/multi-model-verify/test_lane_credential_live.py:382](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_lane_credential_live.py:382)).

It also copies the user’s complete real `config.toml` into each disposable home ([evals/multi-model-verify/test_lane_credential_live.py:180](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_lane_credential_live.py:180)). Replace that with a minimal generated config containing only the non-secret managed Kimi provider/OAuth declaration required for `provider list`; the builder’s equivalent provider block is already explicit and credential-free ([tools/new-kimi-lane-home.ps1:862](C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-home.ps1:862)). Add the structurally valid fake-credential control before the garbage and absent assertions.

**Task 7 finding 8: FIX — BLOCKING.**

### 9. The helper retains Round 30’s blank-line acceptance bug

`validate_credential` discards blank lines before counting, allowing multiple-line output to satisfy “exactly one line” ([evals/tools/lane_credential_live_support.py:266](C:/Users/Brandon/Documents/parallax/evals/tools/lane_credential_live_support.py:266)). This violates the shared caller contract fixed in Round 30 ([docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:97](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:97)).

Apply the same exact-line algorithm and failing blank-separator oracle used by Tasks 5 and 6.

**Task 7 finding 9: FIX — BLOCKING.**

### 10. The physical-inventory command does not escape its path

The PowerShell command embeds `debate_home` inside a single-quoted literal without doubling apostrophes ([evals/multi-model-verify/test_lane_credential_live.py:164](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_lane_credential_live.py:164)). Escape every `'` as `''` before interpolation and add a debate-home path containing both an apostrophe and a space.

**Task 7 finding 10: FIX — BLOCKING.**

## Per-task verdicts

- Task 1 — Built and recorded with decisive host-discovery mutations. **PASS** ([docs/superpowers/plans/rounds/2026-08-01-cred-lock/build-ledger.md:16](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-01-cred-lock/build-ledger.md:16))
- Task 2 — Unchanged by this review. **PASS**
- Task 3 — Unchanged by this review. **PASS**
- Task 4 — Unchanged by this review. **PASS**
- Task 5 — Round 30 remediation is recorded separately and complete. **PASS** ([docs/superpowers/plans/rounds/2026-08-01-cred-lock/build-ledger.md:22](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-01-cred-lock/build-ledger.md:22))
- Task 6 — Round 30 remediation is recorded separately and complete. **PASS**
- Task 7 — Apply the ten fixes above; then rerun the offline suite under both hosts. Its live half remains unsatisfied until provisioned homes exist. **FIX — BLOCKING**
- Task 8 — Not built; no new plan defect found here. **PASS**
- Task 9 — Not built; no new plan defect found here. **PASS**
- Task 10 — Cannot satisfy its mandatory final live gate on the current machine. **ESCALATE — LIVE GATE UNSATISFIED**

## Overall verdict

**FIX — BLOCKING.** The pin, security ordering, and several offline oracles must be corrected before Task 7 can be accepted. After those corrections, ordinary merge remains blocked until the credential-bearing live gate runs, unless the user explicitly authorizes a documented `DEGRADED` merge.

## Final check

UNVERIFIED:

- All seven live measurements: 5, 6, 7, 10, 11, 16, and 17.
- The reported 23-per-host offline executions; I inspected their code and ledger record but did not rerun them.
- The absolute-key stderr baseline, because no committed `probe-record.md` exists yet.
- Task 7 after the required fixes.
- Tasks 8, 9, and 10 implementations.
- CI and final attestation at the eventual final HEAD.

