# Build ledger, items 32 and 33 detached dispatch

Per-task record of WHO built each task, WHAT verification exists, and WHOSE
evidence it is. The last column matters: the session verifies every task
independently and never accepts an implementer's report as the verdict, so
where a report did not arrive the evidence is the session's own and must not
later be attributed to the implementer.

Plan: `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md`, FROZEN
at `28802bd` after 23 cross-vendor dispatches and 6 Fable-lane rounds.

| Task | Commit | Implementer report | Session verification | Evidence provenance |
|---|---|---|---|---|
| 1 dispatch tool | `e3cb1de` | full, after one stalled turn that returned no report and was resumed | ran the suite on BOTH hosts (58 passed 5.1, 58 passed 7), reproduced the Start-Process pipe measurement from scratch, live-ran launch/poll/complete/label-mismatch against the shipped tool | BOTH |

## Deviations from the frozen plan

### Task 1, step 4: the launch mechanism is NOT the literal `Start-Process`

**This is drift and is recorded as drift.** The frozen plan names
`Start-Process -FilePath (Get-Process -Id $PID).Path ...`. The shipped tool
uses `CreateProcess` through inline `Add-Type` C#, with a
`PROC_THREAD_ATTRIBUTE_HANDLE_LIST` allowlist naming only the three
redirection handles.

**The session reproduced the reason independently, without the implementer's
script.** A launcher that calls `Start-Process` with
`-RedirectStandardOutput/-RedirectStandardError` returns in 0.0s either way,
but the CALLER does not: `.NET` requests `bInheritHandles=TRUE`, which is
process-wide, so the grandchild inherits the caller's own pipe handle and the
reader waits for EOF until the grandchild exits.

Measured 2026-08-31 against a 12-second sleeper, launcher output piped versus
redirected to a file:

- piped caller: `real 0m12.418s`
- caller output to a file: `real 0m0.215s`

A tool call is the piped shape. So the literal `Start-Process` form
reintroduces exactly the blocking this tool exists to remove, and two of the
task's own required tests
(`test_poll_reports_running_while_the_pid_is_alive`,
`test_a_running_round_can_never_exit_zero`) cannot pass against it.

The shipped tool, measured the same way under a piped caller: `-Launch`
returned in **0.427s** with a 15-second wrapper still running, `-Poll`
answered `running` at exit 3, then `reply-present` at exit 0 once the wrapper
finished, and a wrong `-ExpectedRound` answered `receipt-not-expected` at
exit 1.

**This is a plan defect, not an implementer judgment call.** The plan froze a
mechanism that cannot satisfy the plan's own tests. It is recorded here for
the diff debate to adjudicate rather than being folded into the plan, because
the plan is frozen.

### Task 1, step 3: a variable-name collision fixed inside the script

The `-Poll` block held its receipt object in a variable named `$receipt`,
colliding case-insensitively with the `-Receipt` parameter, so every poll
returned `no-receipt`. Renamed to `$rec`. A bug fix inside the task's own
code, not a design change. It is the same class as the
`$s`/`$S` collision recorded in item 48's cycle.
