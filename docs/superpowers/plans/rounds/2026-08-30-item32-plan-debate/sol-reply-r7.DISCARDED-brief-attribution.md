Revision 6 closes four round-6 findings cleanly, but the token remains an instruction-level capability rather than proof that this caller completed `-Launch`. I found a sixth cross-act path and two task-executability defects.

## Round 6 FIXes

1. Launch token — DOES NOT CLOSE

The token correctly stops accidental polling with a different token: `-Launch` writes it into `launch.committed`, and `-Poll` checks equality before PID or terminal artifacts at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:87-99`. The refused-old-directory regression also exercises a real prior launch at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:65-66`.

But the token is not a secret: it is stored in the old directory being authenticated at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:87-90`. The documented site manually carries `<launch-token>` from prose rather than mechanically capturing successful JSON output at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:367-379`. A caller can therefore read the old commit token after a refused launch and pass it back, recreating the old completion path.

The PID-less LAUNCH UNKNOWN contradiction also remains: the state contract says targeted discovery is required when no PID exists at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:163-172`, while the operation region still tells every LAUNCH UNKNOWN to use `taskkill /PID <id>` at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:194-204`.

Mechanism required: `-Launch` should create a fresh success-receipt file only after commit; `-Poll` should accept that receipt, not a caller-supplied directory/token pair. The documented launch must check exit status and persist the returned receipt mechanically. No successful launch means no receipt and therefore no poll.

2. Host boundary — CLOSES

I read the exact per-site assertions and documented commands using the caller’s executable path at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:287-296` and `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:367-382`. Task 1 also requires running the exact documented outer command on the selected host at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:68-71`.

3. Per-site Codex oracles — CLOSES

Both Codex sites have unique markers; each section must contain its own launch, poll, and client invocation at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:263-299`. The `Start-Process` assertion is now accurately described as centralization-only at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:300-311`.

4. PID validation and fixture provenance — PARTLY CLOSES

Missing and malformed PIDs now stop as `pid-unreadable` before terminal artifacts at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:94-99`, and terminal fixtures must originate from a real successful launch at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:67-71`.

The hard-kill test is not executable deterministically. It says to kill the tool between process creation and publication but defines no barrier or test seam in that interval at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:71-71` and `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:82-88`. Without a “started” signal followed by an injected wait, the test is another millisecond race.

The PID also remains a number without process-instance identity. This repo’s existing liveness implementation records start-time ticks and treats PID/start-time mismatch as dead at `tools/kimi-lane-lock.ps1:219-236`; the proposed dispatch tool records only `$proc.Id` at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:86-87`.

5. Injectable document paths — CLOSES

Task 2 identifies the fixed `DOC_PATHS` dependency and explicitly requires optional injected paths for the collector and both coverage tests at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:230-236`. The current tests indeed read the module constant directly at `evals/multi-model-verify/test_contract_coverage.py:734-750`.

6. Convergence grep — DOES NOT CLOSE

The encoding phrase is now included, but the grep is case-sensitive at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:692-703`. The current stale spec says `SEVEN states` in uppercase at `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:190-199`, while the pattern searches lowercase `seven states`; that stale count passes.

Use `grep -ni`, case-insensitive expressions, or positive exact assertions for the ten-state replacement.

7. Ceiling ordering — CLOSES

The measurement command now exists at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:117-125`, and the conditional decision occurs before Task 3’s strict-lint oracle and commit at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:392-410`.

## Completion-model sweep

The base rate is six rounds out of six finding either a completion hole or an oracle that binds nothing. The plan records the first four classes at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:742-748`, and revision 6 itself records round 6’s stale-directory and PID findings at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:50-71`.

### Sixth instance: token laundering from the artifact being authenticated

Input:

- Old completed directory containing token `T-old`, dead PID, zero exit, and reply.
- New launch on that path is refused.

Sequence:

1. The new `-Launch` returns no successful token because reservation failed.
2. The caller reads `T-old` from the existing `launch.committed`; the plan stores the token there at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:87-90`.
3. The caller supplies `T-old` to the documented manual poll placeholder at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:371-379`.
4. Token equality passes, the old PID is dead, and the old zero exit and reply produce `reply-present` under `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:94-101`.

Artifact read as this act’s result: the old `launch.committed` capability, followed by the old reply.

The token proves only that the caller can read the directory. It does not prove that this caller received a successful launch result.

## Other cross-act shapes

- **Location identity:** a reused dispatch path exposing old commit/exit/reply artifacts. The token intends to address this at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:48-50`.
- **Process identity:** a numeric PID reused by an unrelated process. Poll then reports `running` and refuses to read the real terminal artifacts at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:96-99`. The repo’s PID-plus-start-ticks precedent is at `tools/kimi-lane-lock.ps1:219-236`.
- **Payload identity:** a stale or replaced `<wrapper-file>` copied into a fresh dispatch directory. The tool copies whatever path the caller supplies without recording its hash at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:84-90`.
- **Execution-context identity:** wrong host, plugin copy, working directory, or resumed session. Host selection is now bound at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:382`; plugin-root resolution remains explicitly partial at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:18-28`; Kimi’s working directory is passed per call at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:442-453`.

## One-task executability

Three tasks are not self-contained under the stated test:

- **Task 1:** `test_the_documented_outer_command_works_on_this_host` requires an exact command that Task 1 never gives; the first exact command appears only in Task 3 at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:367-379`. Its hard-kill test also lacks a deterministic synchronization seam at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:71-88`.
- **Task 3:** its ceiling step says to use “the command in Task 2’s preamble” rather than reproducing it locally at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:392-396`.
- **Task 9:** Step 1 modifies the round record, but that record is absent from Task 9’s file list and final `git add` at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:682-686` and `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:729-733`.

FIX