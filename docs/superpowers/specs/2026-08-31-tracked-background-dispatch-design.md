# Tracked background dispatch: design

**Supersedes the launch half of**
`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`.
That spec's completion model, receipt transaction, state machine and exit
mapping are UNCHANGED and are not restated here. Only the way a round is
started changes.

## Why this exists, stated correctly this time

Backlog item 32 was built against a premise that does not hold.

**The recorded premise.** `CLAUDE.md` has carried, since 0.21.x and through
five release cycles, that a review round dispatched in the FOREGROUND is
KILLED at the caller's 600-second tool ceiling: the client never writes its
`--output-last-message` file, so the round is a transport failure rather
than a review result, and the reviewer quota is spent for nothing.

**The measurement.** Taken 2026-08-31 on Claude Code 2.1.251, because the
user noticed that several commands that day had overrun and been moved to
the background rather than killed:

    10:09:17  start
              SURVIVED THE CEILING
              exit 0
    10:20:17

An 11-minute command crossed the ceiling, was moved to the background by
the harness, completed, and returned exit 0 with its output intact. The
same "moved to the background" message had already appeared twice that
session on commands that then completed. **Nothing is killed and nothing is
lost.** The rule was never re-measured against a newer client; it was
believed because it was written down.

**The real defect, in the user's own terms.** A foreground dispatch OWNS
the session for its whole duration. The user cannot see which round is
running, and cannot talk to the agent at all until it ends. That is the
cost worth removing, and it has nothing to do with a kill.

**What the shipped tool got wrong as a result.** It launches an OS-detached
process, which the harness does not track. It fixed the blocking and, in
doing so, removed the visibility the harness was already providing for
free: no task row, no lane-and-round name, no completion notice. That is a
worse trade than the one it replaced.

## What does not change

The completion model. Twenty-three cross-vendor rounds hardened it, and
both reviewers searched it independently and found it closed: a killed,
hung or half-written round cannot read as a completed one. That value never
depended on the kill premise, so none of it is reopened.

Specifically unchanged: the receipt-last transaction; receipt/dispatch-dir
separation and freshness; `-Poll`'s ordered checks; pid PLUS start-ticks as
identity; the exit mapping where 0 means `reply-present` alone, 3 means
`running`, 1 means every other named state and 2 means the tool could not
run; and every contract region and pin that states them.

## What changes

### 1. The tool stops starting processes

`-Launch` becomes `-Prepare`. It performs the same fail-closed transaction
and stops short of creating a child:

1. Resolve, and BLOCK if the receipt path equals or sits inside the
   dispatch directory, or already exists.
2. Create the dispatch directory with `-ErrorAction Stop`; an existing
   directory is a refusal, not a reuse.
3. Copy the wrapper body in; create `stdin.empty`.
4. Mint the launch token and write `launch.committed`.
5. Write the RECEIPT last of all, create-new.

An interrupted `-Prepare` therefore still leaves NO receipt, which is the
property the state machine is built on.

**Deleted with the launcher:** the inline `Add-Type` C# block, the
`PROC_THREAD_ATTRIBUTE_HANDLE_LIST` allowlist, `LaunchDetached`, the
`GetProcessTimes` capture, and the catch-side `taskkill`. Roughly 150 lines.


That deletion resolves three findings from diff-debate round 1 by removing
their subject rather than patching them: the launch catch's pid-only kill,
the `GetProcessTimes` failure that leaves a started tree alive because the
pid was not published yet, and the `Add-Type` compile that runs outside any
catch and made even `-Poll` depend on compiling launch-only C#.

**`-WorkingDirectory` is NOT deleted with it, and an early draft of this
spec said it was.** That draft called the parameter launcher-only. It was
not: it is what put the client inside the REVIEW MIRROR. Dropping it
un-anchored the reviewed tree silently, and the first round dispatched
under the new design ran with the real repository as its working directory,
where a root `AGENTS.md` sits on disk and the client auto-ingests it as
instructions. That is the instruction back-channel the preflight exists to
stop. The round was discarded unread and its cost is recorded in the build
ledger.

So the working directory survives, and it moves to where a test can see it.
`-Prepare` keeps `-WorkingDirectory` and writes its resolved value to a
`cwd` file inside the dispatch directory. The wrapper's SECOND act, right
after publishing its identity, is `Set-Location` to that value. A call site
that omits it fails its own per-site test, which is strictly better than
the old arrangement: as a launcher parameter, nothing pinned it at all.

### 2. The caller runs the wrapper as a TRACKED BACKGROUND command

The skill's documented step is no longer "the tool starts it". It is:

> Run the prepared wrapper as a background command, named for its lane and
> round (`Sol R1 debate round`, `Kimi R2 debate round`, or with no lane its
> kind, `Gate: pytest 5.1`).

The harness owns the process. It appears in the user's task list under that
name, it notifies on completion, the conversation stays open, and the
600-second ceiling does not apply to it at all. The naming convention was
already this repo's practice and had no mechanism behind it; this is what
makes the name load-bearing rather than decorative.

### 3. The wrapper publishes its own identity, first

Each of the five wrapper bodies gains two lines as its FIRST act, before
any client call:

    [System.IO.File]::WriteAllText("$PSScriptRoot/pid", "$PID", (New-Object System.Text.UTF8Encoding($false)))
    [System.IO.File]::WriteAllText("$PSScriptRoot/startticks", ((Get-Process -Id $PID).StartTime.ToUniversalTime().Ticks), (New-Object System.Text.UTF8Encoding($false)))
    Set-Location -LiteralPath ([System.IO.File]::ReadAllText("$PSScriptRoot/cwd", (New-Object System.Text.UTF8Encoding($false, $true))))

A process reporting its own pid needs no handle games and cannot report
another process's. The `Set-Location` is what anchors the client to the
review mirror; it reads the value `-Prepare` resolved rather than trusting
whatever directory the harness happened to start the command in.

The remaining wrapper shape - initialize failure, run
the client, write the reply with .NET and no BOM, write `exit` LAST inside
a `finally` - is unchanged.

### 4. One new state: `not-started`

Ordering changes: the receipt now exists before any pid does. So `-Poll`
gains a state between `launch-not-ours` and `pid-unreadable`:

**`not-started`** - the receipt is valid, expected, and its marker and token
check out, and there is no `pid` file. Exit 1.

`-Poll` also refuses a dispatch directory with no `cwd` file, as
`not-started`: a prepared round that cannot say where it must run is not
runnable, and must never be run from wherever the caller happens to be.

It covers two situations and deliberately does not distinguish them,
because both mean the same thing to a caller: the prepared wrapper was
never run, or it died before it could publish its identity. Neither is a
result.

The brief window where a wrapper is alive but has not yet written its pid
also lands here, which is conservative in the correct direction: a live
round reads as not-started rather than as finished.

The state count goes from twelve to thirteen. `DECLARED_REGIONS` and the
`detached-dispatch-states` region change with it.

### 5. The exit-2 promise gets narrowed to what is true

Round 1's remaining finding stands and is not fixed by the redesign. The
header promises exit 2 for parameter-binding errors, but an unknown switch
fails in the PowerShell `-File` binder before any line of the script runs,
so the exit code is the host's.

The contract is corrected rather than the code: the tool promises exit 2
for the binding and internal errors IT can see, and states that a switch
the host itself rejects never reaches the script and never produces exit 0.
The property that matters is that no such failure can be read as a
completed round, and that is measured, not asserted.

## Constraints that must survive

- Change the tests FIRST, then the tool or the skill.
- Both PowerShell hosts. A green suite on one proves one interpreter.
- A killed, hung, or unfinished round must never read as a completed one.
  Treat the class as open.
- `-Prepare` is fail-closed: `$ErrorActionPreference = 'Stop'`, and any
  failure after the directory exists removes nothing and publishes no
  receipt.
- Forward slashes in `SKILL.md` and `references/backup-lane.md`. Two
  repo-wide gates forbid a backslash in either.
- `${CLAUDE_PLUGIN_ROOT}` in `SKILL.md`, where harness substitution is
  measured; `<plugin-checkout>` in `references/backup-lane.md`, which is
  read raw.
- Contract text inside `contract:start`/`contract:end` markers must sit
  whole inside a single pin, and `DECLARED_REGIONS` moves with it.
- The five pins at `test_multi_model_verify.py:609-650` stay green.

## The honest cost, stated because it is a real loss

A tracked background command belongs to the session. If the session ends,
the round probably dies with it, where an OS-detached process would have
survived and could have been collected later by a fresh `-Poll`.

That trade is deliberate and the user made it: a round nobody can see or
interrupt is worth less than one that appears by name, reports itself, and
leaves the conversation open. It is recorded here rather than buried,
because a later cycle may want the detached path back as an option, and
should know what it is buying.

## What is NOT in scope

- Item 51's argv escaping and item 31's shipped pipes stay open.
- Item 58 beyond naming the plugin root in these calls.
- The `diff-mode-spec-fidelity` behavioural question stays open with its
  confound named.
- The version bump and the install happen after the debate, not here.
