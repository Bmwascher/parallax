The accepted changes close the round-1 disputes. The live-gate reframing is also sound, with one addition: measurement 11 needs a coexistence gate for claim 5, and measurement 16 needs a false-positive gate for claim 13 (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:51-56`). Destructive refresh probes must use disposable lane credentials, never the user’s ordinary login, consistent with the dedicated-login boundary at `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:93-103`.

## New claims

12. Doctor unquestionably creates the dangerous topology: it builds a scratch home and invokes `provider list` there (`commands/doctor.md:157-168`), while the builder copies the user credential into that home (`tools/new-kimi-lane-home.ps1:410-414`). It can also strand that copied secret if doctor is interrupted before removal.

The token-retirement conclusion is wider than the evidence, however. Refresh/retirement was measured for “copy-then-use,” but nothing says `provider list` performs that use; measurement 16 shows it succeeds without any credential at all (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:43,56`). Doctor is therefore a proven unnecessary-copy and possible stranded-secret surface, but not yet a proven refresh-token retirement path.

**FIX — remove home construction from doctor and add a no-copy/no-write test; do not claim doctor retires the refresh token unless a dedicated `provider list` refresh probe demonstrates it.**

13. Correct. Doctor admits that `source=oauth` does not prove dispatch, but still translates it into “credential present and OAuth-sourced” (`commands/doctor.md:161-168`). Measurement 16 says the same output occurs with no credential, so neither “credential present” nor authenticated reachability follows (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:55-56`).

**FIX — replace the row with direct structural validation of the lane credential and report only “lane credential structurally present”; reserve authenticated availability for an explicit live probe.**

14. The cited content is actually at `evals/multi-model-verify/test_kimi_lane_home.py:310-317`: the fixture contains only `access_token`. Those tests invoke the real builder against that fixture (`evals/multi-model-verify/test_kimi_lane_home.py:323-339`), so stricter validation will turn every builder test red unless the fixture changes simultaneously. The exact production schema is not established by this fixture.

**PASS.**

## P1 — same-owner recovery

Not sufficient as written. Harness identity identifies a session, not one debate: the lock separately records both owner identity and debate id (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:144-154`). Automatic takeover on PID/start-time equality would let two concurrent debates from the same harness displace each other.

The safe rule is:

- Exact `{hostname, PID, start ticks, debate id, acquisition nonce}` match: idempotent re-acquire of the same lock.
- Same harness but different debate id or nonce: ordinary contention; never automatic takeover.
- Abandoned different debate under a live harness: bounded wait, then explicit human-confirmed force-release naming the complete recorded identity.
- Doctor reports the holder and liveness, but must say `LIVE`, not infer whether the live session has abandoned that debate (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:159-177`).

With that restriction, `(a)+(b)+(c)` closes claim 6 without a keep-alive process. “Authenticated” is too strong unless an actual authentication mechanism is added; matching and interactively confirming the recorded identity is a guarded human override, not cryptographic authentication.

**P1 verdict: FIX — constrain same-owner re-acquire to the same debate id and nonce; different-debate recovery remains explicitly human-confirmed.**

## P2 — exclusive-handle reclaim

For cooperating Windows callers, the proposed exclusive-open protocol statically closes the two-reclaimer window: only one caller can inspect and rewrite the record, while another open failure becomes bounded contention. The short initial-write window is handled correctly—another caller waits rather than reading a partial record—which matches the design’s fail-closed contention rule (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:144-177`).

Three details remain:

- The handle must close after a complete write and durable flush. It cannot remain open for the debate because the builder shell exits, while the intended owner is the longer-lived harness (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:150-157`).
- Normal release must use the same serialized protocol. Opening with `FileShare.None`, closing, and then deleting would reopen a release race. Prefer a persistent lock file rewritten in place to a well-formed `state=free` record, with acquire, reclaim, and release all serialized through the exclusive handle.
- A crash after truncation but before the new record completes leaves a malformed file. The existing rule correctly treats that as held (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:165-171`); doctor plus confirmed force-release is then the recovery path.

The precise Windows sharing, flushing, crash, and PowerShell-host behavior still needs live gates on both hosts.

**P2 verdict: FIX — the reclaim race closes only if release also avoids unlinking and every state transition uses the same exclusive-handle, in-place protocol.**

## P3 — doctor without a debate home

Yes. Doctor should stop building a home and stop invoking `provider list`. The current builder consults the user credential (`tools/new-kimi-lane-home.ps1:231-236`) and copies it (`tools/new-kimi-lane-home.ps1:410-414`), while `provider list` establishes neither presence nor authentication (`commands/doctor.md:157-168`).

Default doctor check 8 should:

- Check binary and version floor.
- Inspect the fixed lane credential in place, read-only.
- Require readable, valid JSON and the exact required nonblank fields.
- Hash before and after to prove no mutation.
- Report only structural readiness.
- Print the locked login-wrapper command when unavailable.
- Keep the containment-artifact check already specified at `commands/doctor.md:169-173`.

Any authenticated probe should be explicit, acquire the lane lock, disclose that it may refresh the lane credential, and never touch the user credential.

**P3 verdict: PASS.**

OVERALL VERDICT: FIX — P1 is sound after debate-id/nonce scoping; P2 needs a persistent in-place free/held state so release is serialized too; P3 should replace the current doctor builder/provider-list path.

## Final check

UNVERIFIED:

- Whether `provider list` ever refreshes a present near-expiry credential; claim 12’s token-retirement statement remains unverified.
- Measurement 16 remains external until its garbage-credential and absent-credential cases become live gates.
- The exact kimi-code 0.31.1 credential JSON fields and types are not established by repository artifacts; the current fixture proves only that existing tests use `access_token`.
- The proposed `FileMode.Open`/`FileShare.None` reclaim and in-place release behavior has not been executed on PowerShell 5.1 or 7.
- Crash behavior during truncate/rewrite and durable-flush behavior remain probe-required.

As directed, the unavailable Python runner is not a finding: no code has changed and no implementation gate is presently implicated.