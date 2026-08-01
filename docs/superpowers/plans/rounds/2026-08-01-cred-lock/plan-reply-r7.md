Not PASS. I found two blocking task defects comprising five precise fixes. Task 3’s new mode scoping is correct; Task 7’s locking and secret-guard changes remain underspecified and lack decisive oracles.

### Task 1

The checker separately verifies path existence and dual-host parity, and both failure directions receive mutation tests. The current workflow does name the absent lock test in both Windows steps, so the initial red condition is real. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:65-90`; `.github/workflows/skill-evals.yml:79-99`.

Verdict: PASS.

### Task 2

The duplicate-key cases now distinguish last-value semantics from both duplicate rejection and first-value retention. The fixture change has its own validator oracle and both advertised commands select hosts explicitly. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:100-125`.

Verdict: PASS.

### Task 3

The round-6 mode scoping is correct. Status accepts wait/poll but bypasses mutating preprocessing; ResolveOwner touches no lock file; exit 4 is restricted to mutating modes. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:161-173`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:197-202`.

The acquire table partitions its declared readable, well-formed, same-host domain, and the release/override table partitions everything surviving preprocessing. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:185-218`.

One contradiction remains. The per-state rule says a free record carrying any property besides `version` and `state` is malformed—including known held-only properties such as `host`. The later purportedly exhaustive MALFORMED definition covers unknown fields but omits known fields forbidden in the current state. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:142-144`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:230`. The planned extra-field-on-free test would expose one implementation, but the behavioral contract still gives the implementer two different definitions. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:244`.

Required blocking fix: amend line 230 to include “a record carrying any property forbidden for its state, including any held-only known property on a free record.”

Verdict: FIX — BLOCKING: make the exhaustive MALFORMED definition match the per-state property rule.

### Task 4

The crash point is synchronized, exact zero-length and partial-prefix bytes are asserted, and production `-Acquire` must refuse both damaged states. The host-divergence assertion also has an explicit wrong-expectation mutation. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:254-275`.

Verdict: PASS.

### Task 5

Code 3 now covers both exclusive-handle contention and a live holder. Main-operation versus release-failure precedence is fixed in both directions, and the client-exit oracle prevents simple exit-code propagation. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:296-310`.

Verdict: PASS.

### Task 6

The round-6 seam is correctly placed after custody JSON construction and before emission, and its oracle requires no stdout, removed debate home, and a free lock. The two cleanup flags and acquire-failure non-release oracle cover both incorrect directions. Host-selector ownership is consistently assigned to Task 2. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:320-355`.

Verdict: PASS.

### Task 7

Four blocking defects remain.

1. **Manual marker locking has no executable lifecycle.** Manual setup must call the login wrapper, whose owner fields and `-VerdictOut` are mandatory, then write the marker under a separate lock. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:283-290`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:369-375`. The only owner rule says ResolveOwner runs once per *module run*, which cannot supply the earlier manual setup operations. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:375`.

   Fix: freeze the complete setup sequence for A then B: direct ResolveOwner for the setup session; login invocation with all mandatory parameters; fresh setup DebateId; acquire with that home as both LaneHome and DebateHome; ASCII marker write; release with captured nonce; require A’s tick strictly below B’s.

2. **The secret set has no timing or failure-path contract.** The plan forbids logging any credential value, but only says the helper inspects an “accumulated set.” `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:30`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:381-385`. C deliberately rotates tokens, so a set populated only before the command misses a newly issued value emitted by that same command. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:391`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:47-50`.

   Fix: seed the retained union under each home’s lock; after every command, while its lock remains held, reread that home and merge new values before scanning streams. Never discard old values. Make the helper own non-raising process capture and sanitize timeout/launch/error paths before pytest can render captured streams.

3. **Neither new protection has an adequate oracle.** The seven listed cases test client behavior, but none proves the runner acquired the intended home’s lock, released it after failure, or rejected a credential value in either stream. A runner with no locking and no secret helper can therefore pass the listed functional cases. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:375`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:387-395`.

   Fix: add an offline `test_lane_credential_live_support.py`, sharing the production test helper, that:

   - pre-holds A, B, and C individually under a different live owner and proves the fake command is not invoked;
   - proves contention while a fake command blocks and release after both zero and nonzero exits;
   - injects an existing fake credential value into stdout and stderr separately;
   - has a fake command rotate a credential and emit the new value;
   - asserts failure names only the field, contains no value, and writes no probe record.

   Because its lock tests are Windows/PowerShell-facing, add this module to both Task 10 Windows steps and the host-parity required set.

4. **Fixture routing remains open.** C is explicitly assigned only to items 3 and 7, while A/B are assigned to coexistence; items 1, 2, 4, and 6 do not state which lane home, debate home, or credential construction they use. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:369-375`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:389-395`.

   Fix: add an exact routing table. Use A/B only for coexistence; use C with fresh builder-created debate homes for authenticated items 1–4 and 7; use isolated disposable homes containing structurally valid fake, garbage, and absent credentials for item 6. State which lock each case acquires.

Verdict: FIX — BLOCKING: freeze manual setup, secret-set lifecycle, deterministic lock/secret oracles, and fixture routing.

### Task 8

The aggregate is total, lock-status failure is BROKEN without fabricated recovery, the seven-step hash procedure never compares absent hashes, and every confirmation value has an identified source. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:409-457`.

Verdict: PASS.

### Task 9

The three literals remain separately scoped, the complete status invocation is now present, and the literal text contains no backslash. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:463-490`. The region division conforms to the repository rule that one region must fit wholly inside one pin and an overlong contract must be split. `CLAUDE.md:55-91`.

Verdict: PASS.

### Task 10

The five existing offline dual-host modules are assigned to both host steps, the opt-in credential suite is deliberately excluded, final live reruns are explicit per host, and the history check has a failing mutation. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:494-516`.

Task 7’s required new support module must also be added here.

Verdict: PASS conditional on applying Task 7’s explicitly named workflow addition.

### Plan record

The plan identifies itself as revision 5 and records five rounds even though this is plan r6 reviewed in Round 7. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:5-18`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:520-530`.

This does not force implementation judgment, so it is acceptable as-is for code execution, but should be corrected before the record is frozen.

Verdict: FIX — NONBLOCKING: update revision history and round count.

## Overall verdict

FIX. Task 3 has one blocking contradictory definition. Task 7 has four blocking specification/oracle defects. The round-6 Task 3, Task 5, Task 6, Task 8, and Task 9 fixes were applied correctly; Task 7’s changes were applied incompletely and introduced unverified locking and secret-guard surfaces.

## Final check

- **UNVERIFIED:** Measurements 1–21 remain external machine measurements against kimi-code 0.31.1. The design itself says repository tests cannot verify them and requires live gates instead. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:35-67`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:348-364`.
- **UNVERIFIED:** The remote nonpublication and GitHub-run-history assertions recorded in Task 1 were not rechecked against the network in this sandbox. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:65-71`.
- **UNVERIFIED:** No planned implementation or live-gate module exists yet, so none of the new behavioral gates can presently be executed. The plan itself identifies the lock and live suite as new files. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:130-134`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:365-367`. This is expected and is not a finding.

