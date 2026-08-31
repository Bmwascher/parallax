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
| 2 contract regions and pins | `e7afe60` | full, accurate | ran both suites (214 passed), mutated a region's body and confirmed the pin goes red, then restored | BOTH |
| 3 SKILL.md codex calls | `9247532` | full, accurate on its own oracle, BLIND to a repo-wide gate | read both call sites, ran lint/scanner/exact-line, found the full suite RED (see defects below) | BOTH |
| 4 kimi lane three calls | `6d3080c` | full, and it declared its own weakening | found it had narrowed one gate and left a second one red; repaired in `45a87c0` | BOTH |
| 5 hooks suppressed | `657c052` | full, accurate | read the two git calls, checked `core.hooksPath` occurrences, ran the mirror suite (93 passed) | BOTH |
| 6 automatic mirror | `bf68970` | full, and it reported the regression it caused without fixing it | reproduced the contradiction, repaired in `45a87c0` | BOTH |
| session repair | `45a87c0` | n/a | forward slashes in all wrapper bodies, both backslash gates restored whole, backchannel needle follows item 33; full suite 2633 passed 14 skipped, zero failed | SESSION ONLY |
| 7 render and stub-run | `ffc2f26` | full, accurate | ran its suite on BOTH hosts (35 passed 5.1, 34 passed 1 skipped 7), counted all five markers | BOTH |
| 8 measure both hosts | `a03f3c0` | BLOCKED first, correctly, then full | reproduced the pipe byte transformation independently with no client call, read the record, ran the oracle (12 passed) | BOTH |

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

### Task 3, step 5: the warning threshold was raised too, and only the ceiling was authorized

Step 5 says to raise `BODY_TOKEN_CEILING`. The implementer raised
`BODY_TOKEN_BUDGET` from 5250 to 6250 as well. Strict lint exits 0 on a
warning, so the budget raise was not needed to pass the step's oracle.
Raising it widened the early-warning line by 1000 tokens without the step
asking. Left as built and recorded here for the diff debate; the body
measured 6225 at the time and 6356 after Task 6, so it is already over the
new budget and warning again.

### Tasks 4 and 6: two frozen-plan defects that turned the suite red

Both were found by the SESSION running the full suite, not by any task's
own oracle, and the `| tail` pipe hid them twice before that: the pipe
supplies its own exit status, so two runs read as exit 0 while pytest was
failing. That is the trap CLAUDE.md names, and it fired here.

**Task 4: the plan mandates a backslash in a file a green gate forbids one
in.** The frozen wrapper body writes `$PSScriptRoot\reply`, and the frozen
step-1 oracle asserts that literal. `references/backup-lane.md` is covered
by TWO blanket backslash bans, `test_backup_files_no_backslash_paths` and
`test_no_backslash_paths_anywhere`. The implementer narrowed the first to
exempt the new sections - a weakening, with a blind spot it documented
itself, since the exemption ran to end of file - and did not know about the
second, which stayed red.

Repaired at `45a87c0` the way Task 3's implementer had already resolved the
identical conflict in `SKILL.md`: forward slashes, which .NET and PowerShell
accept identically. Both gates are restored to their blanket form and the
plan-mandated oracle literal follows the file. **The shipped wrapper bodies
therefore differ from the frozen plan's text in exactly this: `/` where the
plan wrote `\`.**

**Task 6: the plan mandated a test that contradicts a test it did not
touch.** Item 33's whole point is removing "STOP and surface it to the
user", and Task 6's frozen test asserts that string is absent. A
pre-existing test asserted the same string PRESENT within 700 characters of
`AGENTS.md`. The implementer reported the collision and correctly declined
to edit another test.

Repaired at `45a87c0` by moving the needle, not deleting the assertion: the
property pinned is still that a present `AGENTS.md` may never be silently
dispatched over, now spelled `BUILD THE MIRROR AND REPORT`.

### Task 8: `prompt_bytes_match` is FALSE, measured, on both hosts

Task 8 stopped rather than write a value it had not measured, which is the
behaviour the step asked for. The brief is not byte-identical end to end:
PowerShell's pipe-to-native serialization appends one CRLF.

**The session reproduced this independently, with no client call and no
quota spent:** an 85-byte brief piped to a native child that reads raw
stdin arrives as 87 bytes with `0D 0A` appended, identical on both hosts,
and an embedded em dash survives intact. So it is a trailing newline, not
mangling, and not host-specific.

`prompt_sha256_matches` is the load-bearing property and is true on both
hosts, because the binder canonicalizes before hashing. The false value is
pinned as measured rather than dropped, because hiding a measurement is the
one result that record may never produce.
