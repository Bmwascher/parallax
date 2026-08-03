## Per-task verdicts

### Task 1

The portable existence check, host-parity check, and both mutation tests remain complete and failure-capable. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:88-113](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)

**Task 1 — PASS**

### Task 2

The structural validator retains explicit opposite-direction duplicate-key tests, fixture validation, host selection, and dual-host gates. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:117-149](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)

**Task 2 — PASS**

### Task 3

The stderr choice is correct. Acquire’s stdout must remain exactly the nonce, while the design requires reclaim and contention to be visible. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:229-234](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md) [docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:275-278](docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md) [docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:297-298](docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md)

Three blocking defects remain:

1. “A fresh acquisition … prints NOTHING” contradicts “Acquire’s STDOUT is the nonce and nothing else.” Replace it with: **“A fresh acquisition over `free` emits no stderr report; stdout remains exactly the new nonce.”** [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:231-233](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)

2. The explicit oracle list tests DEAD reclaim, fresh acquisition, and LIVE-holder contention, but not the separately specified handle-contention diagnostic or the `UNMEASURABLE` substitution. An implementation printing the wrong handle message or `liveness LIVE` under the seam would pass. Add:

   - Exclusive-handle contention: exit 3, empty stdout, exact handle-contention stderr.
   - Competing identity under `PARALLAX_LANE_LOCK_STARTTIME_FAULT`: exit 3, unchanged record, empty stdout, and the exact holder line containing `liveness UNMEASURABLE`.

   [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:234-240](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)

3. The settled design says **both overrides are visible**, but the table still leaves `-ForceRelease` as the underspecified “report what it displaced” and gives successful `-MalformedOverride` no report at all. [docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:280-295](docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md) [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:251-263](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)

   Freeze and test, on stderr with empty stdout:

   - `force-released holder: host <host> pid <pid> ticks <ticks> debate <debateId> home <debateHome>`
   - `overrode malformed lock: bytes <bytes> sha256 <sha256>`

**Task 3 — FIX (BLOCKING): correct the fresh-acquire wording, add handle/UNMEASURABLE diagnostic oracles, and freeze both override reports.**

### Task 4

This remains correctly scoped as an OS-behaviour gate rather than a duplicate record-format regression suite, with synchronized crash and partial-prefix oracles. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:303-324](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)

**Task 4 — PASS**

### Task 5

The wrapper’s contention test still asserts only exit 3 and non-invocation of the client. It passes if the new lock diagnostic is swallowed or replaced. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:351-359](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)

Freeze that internal lock stdout alone is captured as the nonce while lock stderr is forwarded unchanged. Add wrapper-level tests for:

- LIVE-holder contention returning the exact holder diagnostic.
- DEAD-holder reclaim returning the exact reclaim diagnostic while the wrapper otherwise succeeds.

These are caller-boundary oracles; Task 3’s direct tests cannot prove them.

**Task 5 — FIX (BLOCKING): specify and test unchanged propagation of lock stderr.**

### Task 6

Three defects remain:

1. The builder explicitly captures **all** internal lock output, but never says that captured stderr is re-emitted. Thus the newly required reports can disappear while custody JSON remains correct. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:375-381](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)

   Capture stdout as the nonce; forward stderr unchanged. Add successful DEAD-reclaim and failed LIVE-contention integration tests while keeping build stdout exactly the custody JSON.

2. “A directory holding the same files a built home has” still requires the implementer to invent home B’s exact construction. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:399-405](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)

   Use this deterministic setup:

   1. Build B normally and capture its nonce.
   2. Directly `-Release` B’s lock, leaving B on disk.
   3. Build A normally, retaining A’s hold.
   4. Attempt `-Remove` on B using A’s complete identity and nonce.
   5. Assert exit 2 and byte-identical A, B, and lock.
   6. Teardown by normally removing A, acquiring a new B hold, then normally removing B.

3. The builder’s invalid-credential oracle requires only a message **naming** the login wrapper, while the design requires the exact fixing command. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:405](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md) [docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:135-142](docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md)

   Freeze and assert one executable recovery line using the actual resolved, PowerShell-single-quote-escaped lane home:

   ```powershell
   $owner = tools/kimi-lane-lock.ps1 -ResolveOwner | ConvertFrom-Json; tools/new-kimi-lane-login.ps1 -LaneHome '<lane-home>' -OwnerPid $owner.ownerPid -OwnerStartTicksUtc $owner.ownerStartTicksUtc -VerdictOut (Join-Path $env:TEMP 'parallax-kimi-lane-login-verdict.json')
   ```

Minor 2’s cleanup-fault mechanism and end state are correct: it now skips mutation, returns 5, leaves the record held, and requires teardown. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:405](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)

**Task 6 — FIX (BLOCKING): propagate lock stderr, replace the hand-built fixture with the frozen setup above, and print/test the exact login recovery command.**

### Task 7

The custody, seeding, main-operation cleanup matrix, exception-path sanitization, and offline support oracles remain explicit. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:416-540](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)

**Task 7 — PASS**

### Task 8

Minor 1 is correct: `SAME-HOST` makes the UNKNOWN and foreign-host rows disjoint. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:562-568](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)

But the doctor still has only the two lock-recovery commands. It never prints the locked login-wrapper command required when the credential is unavailable. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:582-597](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md) The design expressly requires that command. [docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:335-340](docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md)

Add the same executable one-line recovery command specified under Task 6, using the configured lane home, to the `absent`, `unreadable`, and `malformed` credential details. Pin and test the complete command, not merely the wrapper’s filename.

**Task 8 — FIX (BLOCKING): add and pin the exact locked login recovery command.**

### Task 9

Minor 4 is not complete. The replacement covers a wrong field set, including the known-held-field-on-free case, but Task 3’s MALFORMED definition also includes non-JSON, non-object, invalid version/state, wrong type, and wrong validation-pattern records. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:267-279](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md) The shipped literal still enumerates only unreadable, truncated, zero-length, field-set, and digit-time cases. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:613-615](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)

Replace that portion with:

> an unreadable file, a zero-length file, a file that is not a JSON object, or a JSON object that does not exactly satisfy the record schema — version 1, one of the two state literals, that state's exact field set, and every field's type and validation rule

Also carry the newly restored visibility contract into the pinned region:

> A DEAD-holder reclaim reports the holder it replaced. An exhausted wait reports the LIVE or UNMEASURABLE holder it refused, or reports handle contention when no record could be read. Each confirmed override reports the record or bytes it displaced.

Otherwise the implementation task and shipped lock contract immediately diverge. The region is pinned whole, so both additions receive a decisive coverage oracle. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:613-625](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)

Minor 5’s reused-region instruction is correct and does not restore the deleted contract. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:621-623](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)

**Task 9 — FIX (BLOCKING): make the malformed summary exhaustive and include the restored visibility rules in the pinned literal.**

### Task 10

The six dual-host modules, parity required set, final-head live rerun, and failing history oracle remain explicit. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:634-653](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)

**Task 10 — PASS**

## Answers

1. **No PASS yet.** Tasks 3, 5, 6, 8, and 9 require the blocking fixes above.

2. **The stderr choice and exact reclaim/contention wording are sound.** The defect is only the overbroad phrase “fresh acquisition … prints NOTHING”; it must say no **stderr report**, because stdout still carries the nonce. The added oracles must also cover handle contention and `UNMEASURABLE`. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:231-240](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)

3. **Minor 4 does not yet describe the same exhaustive rule as Task 3.** It closes the state-specific field-set case but omits several other parseable and unparseable MALFORMED classes. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:267-279](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md) [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:613-615](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)

4. The third structurally blind class is **composition across caller boundaries**: a direct tool can implement the right behavior while its wrapper or builder captures and discards the evidence. Task 6’s “capture all output” and Task 5’s code-only contention oracle demonstrate that exact risk. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:357-359](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md) [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:375-381](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)

   The related oracle class is **fixture constructibility**: every integration fixture must have a completely specified setup and teardown that can actually reach its assertion. The current hand-built B is the concrete survivor. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:399-405](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)

## Overall verdict

**FIX — BLOCKING. Do not refreeze or start Task 1 yet.**

The r18 amendment restores the direct-tool design behaviors, but it does not yet preserve them through callers, fully test both contention forms, or carry them consistently into the shipped contract.

## Final check

UNVERIFIED:

- Measurements 1–21 remain externally obtained facts rather than results reproducible from this repository’s planned test suite. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:52-65](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)
- Three simultaneous lane logins remain an explicit generalization from measurement 11’s two-login result. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:439](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)
- The inspectable fable artifact identifies itself as reviewing revision 12; I found no independently inspectable artifact for the reported second review of frozen r17. [docs/superpowers/plans/rounds/2026-08-01-cred-lock/fable-whole-plan-review.md:1-6](docs/superpowers/plans/rounds/2026-08-01-cred-lock/fable-whole-plan-review.md) The plan’s revision-history account is not independent verification. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:15](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)
- The remote-branch and Actions-history claims were not independently rerun here.
- No implementation or executable gates exist yet for the newly planned lock tool and suite; that is expected at this stage, not a finding. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:153-157](docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md)

