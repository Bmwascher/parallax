Provenance note: this mirror is not at the stated commit. `.git/HEAD:1` points to `item32-detached-dispatch`, whose ref contains `3b7a6c33…`, not `c8d6b6c`, at `.git/refs/heads/item32-detached-dispatch:1`. I reviewed the files actually present.

## Round 6 FIXes

1. Launch token — DOES NOT CLOSE

Token mismatch now stops before PID and result artifacts at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:92-99`. But the token is stored in the old directory being authenticated at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:87-90`, while the documented caller manually carries `<launch-token>` through prose at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:367-379`.

The regression test is internally impossible as written: the second launch is refused during reservation, while the interface says tokens are minted and returned only on successful launch at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:48-50`; therefore there is no “token the second launch would have used” for the test at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:65`.

A mechanical closure is a fresh success-receipt file written only after commit. `-Poll` should consume that receipt rather than accepting a directory and manually supplied token. A refused launch produces no receipt, so it cannot be polled accidentally.

The LAUNCH UNKNOWN remediation also remains contradictory: the state region says PID-less cases require targeted discovery at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:163-172`, while the operation region still instructs `taskkill /PID <id>` for LAUNCH UNKNOWN generally at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:194-204`.

2. Host boundary — CLOSES

Each Codex assertion and documented command invokes the caller’s executable rather than bare `powershell` at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:287-296` and `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:367-382`. Task 1 also requires exercising the exact outer command at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:68-71`.

3. Per-site Codex oracles — CLOSES

The two unique markers are parametrized, and each bounded section must contain its launch, poll, and Codex invocation at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:263-299`. The `Start-Process` absence test now correctly disclaims any proof of per-site reachability at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:300-311`.

4. PID validation and fixture provenance — DOES NOT FULLY CLOSE

Missing and malformed PID artifacts now fail closed before terminal artifacts, and terminal fixtures originate from successful launches at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:67-71` and `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:92-99`.

Two gaps remain:

- The hard-kill test specifies no synchronization seam between `Start-Process` and publication, so it recreates the millisecond race at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:71-88`. Add a test-only “started” signal and wait barrier before PID publication.
- PID identity remains numeric only. The repo already records start-time ticks and rejects a reused PID whose start time differs at `tools/kimi-lane-lock.ps1:219-236`.

5. Injectable document paths — CLOSES

Task 2 explicitly changes the collector and both coverage tests to accept injected paths, then uses that seam for the negative scratch-copy check at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:230-236`. The current fixed-path dependency is exactly where the plan says it is at `evals/multi-model-verify/test_contract_coverage.py:734-750`.

6. Convergence grep — DOES NOT CLOSE

The missing encoding phrase is now included, but the grep remains case-sensitive at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:692-703`. The current stale spec spells `SEVEN states` in uppercase at `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:190-199`; lowercase `seven states` does not match it.

Use `grep -ni` or positive exact assertions for the replacement contract.

7. Ceiling ordering — CLOSES

The measurement command now exists at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:117-125`, and the conditional ceiling decision occurs before Task 3’s strict-lint oracle and commit at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:392-410`.

## Completion-model sweep

The working base rate is six rounds out of six finding a completion-model hole or an oracle that binds nothing. The repository records the earlier recurring classes at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:742-748`, while revision 6 records the round-6 stale-directory and PID cases at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:50-71`.

### Sixth instance: laundering the old artifact’s own token

Input:

- An old completed directory contains token `T-old`, dead PID, zero exit, and reply.
- A new launch on that directory is refused.

Sequence:

1. The refused launch returns no successful token under the interface at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:48-50`.
2. The caller reads `T-old` from the existing `launch.committed`, where the plan stores it at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:87-90`.
3. The caller substitutes `T-old` into the manual poll command at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:371-379`.
4. Equality passes; the old dead PID, zero exit, and reply produce `reply-present` through the ordered branches at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:94-101`.

Artifact read as this act’s result: the old commit token and then the old reply. The token proves the caller can read the directory, not that it received a successful launch result.

## Other cross-act shapes

- **Location identity:** an old dispatch path exposing old commit, exit, and reply artifacts; the token is intended to bind this at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:48-50`.
- **Process identity:** a numeric PID reused by an unrelated process; liveness then reports `running` and ignores this round’s terminal artifacts at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:96-99`.
- **Payload identity:** a stale or replaced `<wrapper-file>` copied into a fresh directory without its hash being committed at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:84-90`.
- **Execution-context identity:** wrong host, plugin copy, working directory, or resume session. Host selection is now bound at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:382`; plugin-root resolution remains deliberately partial at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:18-28`.

## One-task executability

Three tasks are not executable from their own text plus Global Constraints:

- **Task 1:** its exact-outer-command test requires a command that first appears in Task 3 at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:367-379`; Task 1 only names the test at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:68-71`. Its hard-kill test also lacks a deterministic barrier.
- **Task 3:** its ceiling step refers to “the command in Task 2’s preamble” rather than including that command locally at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:392-396`.
- **Task 9:** Step 1 modifies the round record, but that record is absent from Task 9’s file list and final staging command at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:682-686` and `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:729-733`.

FIX