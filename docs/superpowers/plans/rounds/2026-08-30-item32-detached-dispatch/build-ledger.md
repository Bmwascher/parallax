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

### The behavioural gate: one crash class removed, one question left OPEN

**Removed.** A case that ends before its detached round finishes leaves a
live grandchild holding `<dispatch-dir>/transcript`, and
`TemporaryDirectory` cleanup then died with WinError 32, losing the whole
run's verdicts to a file lock. `reaped_tempdir` in
`evals/tools/run_behavioral_evals.py` now waits out each pid the launch
transaction wrote to disk, kills what survives, retries the delete, and
names a leak by path instead of raising. Committed at `be2da46`. Verified:
the case that crashed now completes and reports a verdict.

A residual leak remains and is not the same defect. The leaked workspace
inspected afterwards held NO dispatch directory and no pid file at all, so
something other than a detached child holds it. It is named in the output,
never hidden.

**OPEN, and deliberately not claimed either way:
`diff-mode-spec-fidelity`.** The counts:

| Arm | Runs | Result |
|---|---|---|
| this branch, `--head` | 3 | FAIL 3/4, PASS 4/4, FAIL 3/4 |
| installed cache 0.27.0 | 1 | PASS 4/4 |

The miss is always expectation 2: the exact-range `git diff base..head`
call returned only a name/stat listing, so the content-bearing line came
from a different call. Nothing in this branch edits the diff-mode
instructions.

**The comparison is CONFOUNDED and must not be read as evidence that the
branch caused it.** The two arms differ in two ways at once, not one:
plugin CONTENT, and the LOAD MECHANISM. `--head` loads through
`--plugin-dir`, and `run_behavioral_evals.py --help` says in its own text
that shadowing against the installed copy is unverified. The control arm
is also a single run against a nondeterministic executor. A like-for-like
comparison needs the version bumped and the cache updated, which by this
repo's rule happens AFTER the diff debate, not before it. Carried into the
debate as an open question with these numbers, not as a finding.

## The whole-branch review, and what it changed

`parallax:fable-reviewer` reviewed the range `8af6ae0..98c8a75` before the
diff debate. It found NO critical issue and reported the completion model
closed on this range, having searched for other exit-0 paths, catches that
convert failure into success, reply reads reachable while the pid is live,
stale-artifact reuse, and seam effects that relax a classification.

It raised three important findings. All three were REPRODUCED before being
accepted, and all three were real.

**1. The dual-host CI job never ran this branch's core modules.** The
`powershell-hosts` job carries a hardcoded module list per host, and the
branch added two Windows-only modules without touching it. On the Linux
tier-2b job both skip on `os.name != "nt"`, so after merge NO CI job would
have executed the dispatch tool's suite on any host - the exact 0.16.0
class that job exists to prevent, and it would have made CLAUDE.md's claim
that the job re-runs every PowerShell-facing module false. Verified by
reading the workflow: `test_dispatch_detached.py` and
`test_wrapper_renders_and_parses.py` appear in neither list. Both are now
in both lists.

**2. A corrupted root `AGENTS.md` had entered the range, unrecorded.** Not
in any task, any commit subject, or any ledger row. It is a mechanical
rebrand of `CLAUDE.md` that misinstructs: it says "Codex plugin" and gives
the commands `Codex plugin marketplace update parallax` and `Codex plugin
update parallax@parallax`, neither of which exists.

Attribution, which the reviewer could not read under its grant: it was
swept into the branch's FIRST commit, `fb3e2bb`, by a `git add` that took
it along. It was untracked before the branch and was never authored for
it.

**It is also a preflight STOP condition for this skill's own flow.**
`git ls-files --cached --others '*AGENTS.md' '.agents/*' '.kimi-code/*'`
lists it, and a root AGENTS.md is an instruction back-channel into the
reviewer. Every debate round this cycle was dispatched against a review
MIRROR with `project_agents_md: false` after remediation, so no round read
it; the defect is that it was about to ship to main.

Untracked with `git rm --cached`, which restores exactly the pre-branch
state. The file is left on disk untouched, because it is the user's to
keep or delete, and it was there before this work started.

**3. The behavioural reaper killed by pid alone.** My own code, committed
at `be2da46`, and it violated the invariant this very branch pins: the
`detached-dispatch-states` region says liveness is pid PLUS start time,
never a pid alone, and `dispatch-detached.ps1` writes `startticks` beside
`pid` for exactly that comparison. The reaper read `pid` and ignored
`startticks`, so a recycled pid would have force-killed an unrelated
process tree. It now compares both through `is_our_child`, treats anything
unknown as NOT ours so it never kills on a guess, and re-checks identity
immediately before the kill. That also removes the reviewer's minor 4: the
old liveness probe was a substring search of a process listing, and the new
one compares a tick count.

The reviewer's remaining minors are recorded in its report and carried into
the diff debate rather than fixed here: a `GetProcessTimes` failure path
that can leave a started tree alive, unknown-parameter invocations that
bypass the hand-rolled exit 2, and the stale budget-raise justification
(the body measured 6225 when the budget was set to 6250 and 6356 after Task
6, so it is already warning again - the self-quoting-count class).

Verdict: **ready to merge WITH FIXES.** The two fix-before-merge items and
the third are all done above.

## THE PREMISE WAS WRONG, and the user caught it

Item 32's stated defect, carried in `CLAUDE.md` as measured fact since
0.21.x, is that a review round dispatched in the FOREGROUND is KILLED at
the 600-second tool ceiling: no `--output-last-message` file is written, so
it is a transport failure rather than a review result, and the quota is
spent for nothing.

**That does not reproduce on Claude Code 2.1.251.** The user noticed that
several commands today had overrun and been moved to the background rather
than killed, and asked directly whether our own change had caused the loss
of task visibility. Measuring the ceiling instead of arguing about it:

    10:09:17  start
              SURVIVED THE CEILING
              exit 0
    10:20:17

An 11-minute command crossed the 600-second ceiling, was moved to the
background by the harness, ran to completion and returned exit 0 with its
output intact. Nothing was killed and nothing was lost. The same
"moved to the background" message had already appeared twice earlier in
this session, on commands that then completed.

**The real defect is the one the user named, and it is different.** A
foreground dispatch OWNS the session for its whole duration: the user
cannot see which round is running, and cannot talk to the agent at all
until it ends. A tracked background command has neither problem - it shows
in the task list under its own name, which is what the lane-and-round
naming convention exists for, and the conversation stays open.

**What this costs the branch as built.** The shipped tool launches an
OS-detached process, which the harness does not track. So it fixed the
blocking, and in doing so removed the visibility the harness was already
providing for free. The user identified that as the wrong trade and
directed the design change: dispatch as a TRACKED BACKGROUND command,
keeping the receipt and the completion-state machine.

**What survives untouched.** The completion model, which is what the plan
debate actually hardened over 23 rounds, and which both reviewers searched
and found closed. A killed, hung or half-written round still cannot read as
a completed one. That value never depended on the kill premise.

**What this says about the record.** A rule recorded as measured, repeated
in `CLAUDE.md` and treated as settled through five release cycles, was
never re-measured against a newer client. Nobody checked because it was
written down. The user re-derived it from what was in front of him.

## Two process defects this cycle produced, worth carrying forward

### Subagents end a turn to wait instead of reporting

FOUR implementer dispatches in this cycle ended a turn saying they would
wait for a background notification, returning no report at all: Task 1 and
Task 9 of the item 32 plan, and Tasks 1 and 1a of the tracked-background
plan. Each needed a message telling it to read its own run's output file
and finish. None had actually failed; the work was on disk every time.

The prompt already said "End your turn with the report itself. Do not end a
turn saying you will wait for a notification." That instruction does not
hold. What recovers it, every time, is a follow-up naming the output file
and telling the agent to read it with the Read tool.

Worth a backlog item: the implementer agent should be told that a
background run's output file is readable NOW and that waiting is never the
right end of a turn.

### `git add -A` re-tracks a file you just untracked

`git rm --cached AGENTS.md` stages the deletion. A later `git add -A` in
the same session re-adds the file, silently reversing it, and the commit
then contains the file the earlier command removed. That is exactly how the
stray `AGENTS.md` reached this branch, and how it survived the first
attempt to remove it: the cross-vendor reviewer found it still present at
the declared head after the ledger said it was gone.

Same family as the recorded trap that a `git checkout` of a path writes the
INDEX. The remedy used here: untrack, then ALSO gitignore, so the sweep
cannot re-add it. The preflight still sees it, because that enumeration
uses `--others` WITHOUT `--exclude-standard`.
