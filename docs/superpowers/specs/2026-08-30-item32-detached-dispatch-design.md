# Items 32 and 33: the dispatch must not block, and the mirror must not ask

Written 2026-08-30. Design only. Nothing is built yet.

Item 33 was added on 2026-08-30, after the design below was approved and
while this cycle's own first debate was being set up. See `## Item 33`
at the end.

Backlog item 32, promoted to first in the ranking by the user on
2026-08-30 after the failure fired again on that session's first dispatch.

## Problem

The foreground tool ceiling is 600 seconds. A review round that crosses it
is killed BY THE CALLER, not by the client. No `--output-last-message`
file is written, so the round is a transport failure rather than a review
result and the reviewer quota is spent for nothing.

### The premise item 32 was filed on is partly stale, and the stale part is the important one

Item 32 (filed 2026-08-11) says the rule "does NOT live in the skill" and
that grepping `SKILL.md` for `background` returns nothing. Measured
2026-08-30 at `8af6ae0`:

- The rule DOES live in the skill.
  `skills/multi-model-verify/references/model-prompting-notes.md:297`
  opens a bullet with **"Dispatch the round DETACHED, and do not let the
  shell kill it."**
- Its CONSEQUENCE sentence is already pinned, by
  `test_dispatch_traps_are_documented_in_the_notes` in
  `evals/multi-model-verify/test_multi_model_verify.py:970`. That pin
  reads the whitespace-normalized file.
- What is NOT pinned is the INSTRUCTION itself — the "Dispatch the round
  DETACHED" clause. Only the description of what goes wrong is locked.
- `SKILL.md` still contains nothing. The grep result in item 32 is still
  true of that file.

**So the fix is not "write the rule down."** The rule was written down,
one file away from the command, and a round was still lost on
2026-08-30. This design proceeds from that, not from the item's original
premise.

### Why the rule does not reach the reader

`SKILL.md:177-188` and `SKILL.md:239-250` present the dispatch as fenced
PowerShell blocks. A session executing the skill copies the block. The
block is a blocking pipeline. Nothing at the point of copying says
otherwise, and the file that does say otherwise is cited from those steps
for two OTHER reasons — composing the brief, and reading the canonical
model id.

**The change therefore has to be to the command, not to the prose around
it.** This was the user's explicit choice on 2026-08-30 when offered
prose-only, wrapper-tool, and change-the-command.

## Scope

### In scope: five commands

**Corrected 2026-08-30 after Sol round 1, which found a fifth.** The first
version of this table said four and omitted the backup lane's write-probe.
All five are shell calls that block the caller and can run past 600 seconds,
and all five are detached by this work.

| # | Site | Call | Disposition |
|---|---|---|---|
| 1 | `skills/multi-model-verify/SKILL.md:186` | codex round 1 | detached, Task 4 |
| 2 | `skills/multi-model-verify/SKILL.md:248` | codex resume | detached, Task 4 |
| 3 | `references/backup-lane.md:25` | kimi-code dispatch | detached, Task 5 |
| 4 | `references/backup-lane.md:30` | kimi-code resume | detached, Task 5 |
| 5 | `references/backup-lane.md:353-359` | kimi-code write-probe | detached, Task 5 |

The write-probe runs before round 1 of every backup-lane debate, in a fresh
disposable session carrying the full debate configuration, and
`references/panels.md:51-53` makes panels inherit it. It is a real client
call and nothing about it is cheaper than a review round.

**The Kimi lane was briefly deferred out of this cycle and then restored.**
The deferral argued that a wrapper must change the argument path item 51
owns. Sol round 2 refuted it against item 51's own probe record, which
states it measured "a brief file is read and passed inline as `-p <brief>`,
exactly the shape `references/backup-lane.md` documents"
(`docs/superpowers/plans/rounds/2026-08-22-item51-inline-brief-probe/probe-record.md:27-31`).
Reading the brief from a file into a variable IS the documented shape, so
the wrapper changes how the call is started and not how the brief reaches
the client. Item 51 keeps the argv escaping repair.

Panels need no separate work. `references/panels.md:49-52` routes the Sol
lane to `SKILL.md` and the Kimi lane to `backup-lane.md` rather than
repeating a command, so fixing those two files fixes panels.

### Out of scope, each checked rather than assumed

The user asked for every long client call, "unless those aren't the
same." These are not the same, and the reason differs in each case.

- **The Fable whole-branch reviewer (`agents/fable-reviewer.md`) and the
  Fable panel seat (`agents/fable-panel-reviewer.md`).** These are
  subagents dispatched through the Agent tool, not shell calls. That tool
  runs subagents in the background by default and notifies on completion,
  so the 600-second Bash ceiling never applies to them.
  `references/panels.md:79` already describes this lane in those terms
  ("a resumed background agent").
- **`tools/check-drift.ps1:1054`.** Already detached: `Start-Job`
  followed by `Wait-Job $job -Timeout 900`. Nothing to change. (Its
  brief pipe is defective for an unrelated reason; that is item 31.)
- **`commands/doctor.md:70`.** A reachability probe pinned to
  `model_reasoning_effort=low`, and its own text says so: "Effort `low`
  is deliberate — this is a reachability check, not a review." It is not
  a review round. Its line is also named in item 31, and pulling it in
  here would mix two items on one line.
- **`SKILL.md:325-327`, the attestation emitter.** `SKILL.md` has exactly
  three fenced PowerShell blocks; this is the third. It runs
  `tools/write-attestation.ps1` locally and returns in seconds. It is not
  a client call and cannot approach the ceiling.
- **The full gate and `evals/tools/run_behavioral_evals.py`.** Long, and
  already covered by `CLAUDE.md`'s "dispatch debate rounds AND FULL GATES
  detached". They are not client review calls and are not documented by
  the skill's contract, so they are not part of item 32's surface.

## Design

### Two mechanisms were rejected, both for measured reasons

- **The harness `run_in_background` flag.** This is an instruction about
  how to invoke the tool, which makes it prose. It is the fix that
  already exists in `model-prompting-notes.md` and did not hold.
- **`Start-Job`.** The PowerShell tool gives each call a fresh shell —
  its own contract states that working directory persists between calls
  and shell state does not. A job handle created in one call does not
  exist in the next, so the round could only be waited on inside the same
  call that started it, which is back under the 600-second ceiling.
  `check-drift.ps1` can use `Start-Job` precisely because it starts and
  waits inside one long-lived script.

### The mechanism: a generated wrapper launched with `Start-Process`

1. The session writes a **wrapper script** to its scratchpad containing
   the existing pipeline verbatim — the `$OutputEncoding` preamble, the
   strict-UTF-8 brief read, the override hash check, the native call, and
   the `finally` restore.
2. The session launches it with `Start-Process` on the PowerShell host,
   `-NoNewWindow -PassThru`, and writes `$proc.Id` to a **pid file**. The
   call returns at once.
3. Later calls **poll** the pid, and read a **sidecar exit-code file** the
   wrapper writes as its last act.
4. Completion is read from the reply file as it is today; the route check
   and the round-evidence binding are unchanged.

Three details are load-bearing, and each has in-repo precedent at
`tools/check-drift.ps1:903-945`:

- **The exit code comes from a sidecar file, not from `$proc.ExitCode`.**
  On Windows PowerShell 5.1 the file-redirect form of `Start-Process`
  never retains a native process handle, and `$proc.ExitCode` silently
  reads null when the child exits before the next statement touches
  `.Handle`. A review round always wins that race. The sidecar survives
  it by construction.
- **The encoding preamble moves INSIDE the wrapper.** `Start-Process`
  starts a new process, which does not inherit the caller's
  `$OutputEncoding`. Wrapping today's block without moving the preamble
  would silently reinstate the 0.23.0 defect and send the reviewer a
  brief nobody wrote. This is the single most likely way to get this
  build wrong.
- **A wrapper FILE rather than `-ArgumentList`.** PowerShell 5.1 native
  argument splatting strips embedded double quotes, and
  `Start-Process -ArgumentList` joins its array into one string. The
  override `-c` value and the brief must not cross that boundary. A file
  has no quoting layer at all.

Polling uses `Get-Process -Id` / `Wait-Process -Id`, never `ps -p` from
Git Bash: Git Bash cannot see Windows PIDs and reports a live process as
gone.

### The orphan half of item 32

Item 32 records that the killed codex process SURVIVES the caller's kill,
idle at zero CPU, holding whatever the round held, and that nothing tells
a session to look for one. The detached form gives that a documented
answer: the pid is on disk, so a session can find the process and fell
the tree with `taskkill /PID <id> /T /F`. `check-drift.ps1:944` already
uses that form and records why `$proc.Kill()` alone is not enough — it
stops only the wrapper and leaves the child running.

## Constraints that must survive

Any implementation that breaks one of these is wrong even if the round
completes.

- **A killed, hung, or unfinished round must never be readable as a
  completed one.** LIVENESS IS CHECKED FIRST and dominates: while the
  recorded pid is alive the round is RUNNING and no file is interpreted,
  because a reply being written is not a reply. After the process is
  confirmed gone the poll must distinguish SEVEN states: running; no exit
  file; an exit file that cannot be read or is not a plain integer; a
  non-zero code; zero with no reply artifact; zero with a reply artifact
  that is empty, unreadable, or refused by the lane's own round-evidence
  binding; and zero with a reply artifact the binding ACCEPTS. Only the
  last is a review result.

  This count reached seven over three debate rounds and it is worth
  recording how. The first draft said four. Round 1 found that a stale
  exit file plus a fresh reply plus a killed wrapper read as complete.
  Round 2 found the five-state replacement duplicating one state and
  omitting "zero with no reply". Round 3 found that state accepting a
  reply on PATH EXISTENCE alone, and that liveness was never given
  priority. Treat the class as open.
- **`test_the_brief_is_read_and_piped_as_utf8`** counts four exact
  strings at `>= 2` occurrences each across `SKILL.md`. The wrapper body
  must carry those lines verbatim in BOTH blocks.
- **`test_resume_pipes_the_brief_on_stdin`** matches
  `$brief | codex exec ... resume <SESSION_ID> -` with `[^\n]*`, so that
  span must stay on ONE physical line.
- **The raw pin `("   & {" + chr(10)) not in text`** forbids a
  three-space-indented `& {` line anywhere in `SKILL.md`. A heredoc
  writing the wrapper must not produce that shape.
- **The pinned notes paragraph** stating that the backup lane passes its
  brief as an argument rather than through a pipe must stay true. This
  design does not change that.
- Both PowerShell hosts. A green suite on one proves one interpreter.

## Non-goals, stated so they are not read as done

- **Item 51 is NOT fixed, and the Kimi lane IS detached.** The kimi
  wrapper keeps the inline `-p` argument path exactly as documented
  today, and backgrounding the launch does not touch 5.1's mangling of
  that argument. Item 51 stays open, stays ranked second, and keeps the
  `CommandLineToArgvW` escaping repair. An earlier revision of this
  design DEFERRED the whole lane on the theory that a wrapper must
  change the argument path; Sol round 2 refuted that against item 51's
  own probe record and the deferral was withdrawn. All three of the
  lane's calls are detached by this work.
- **Item 31 is NOT fixed.** The defective pipes at
  `tools/check-drift.ps1:1060` and `commands/doctor.md:70` are not
  touched here.
- **The resume-after-kill recovery is NOT blessed.** Item 32 requires
  that its soundness be measured before any fix endorses it, and it has
  not been. This build makes the kill not happen. It says nothing about
  recovering from one that did.

## Testing

Tests change first, then the skill. That is the repo rule and these are
live-verified contracts.

- **New contract regions**, one pin each, added to `DECLARED_REGIONS` in
  `evals/multi-model-verify/test_contract_coverage.py`. Proposed names:
  `detached-dispatch-codex` and `detached-dispatch-backup`. Two rather
  than one because a region must fit inside a single pin and the two
  lanes state different things.
- **Amend, do not duplicate**, the existing pins that lock the current
  command shape. `test_the_brief_is_read_and_piped_as_utf8` and
  `test_resume_pipes_the_brief_on_stdin` both encode review findings; the
  0.23.0 precedent in that file is to REPLACE a spelling rather than add
  beside it, so a defective form is never left pinned as correct.
- **One live measurement, which must not be assumed:** a brief containing
  non-ASCII characters dispatched through the detached wrapper on BOTH
  PowerShell hosts, with the round-evidence binding accepting the result.
  This repo has paid for this class three times. A green unit suite does
  not answer it.
- Full gates: the five local gates, both PowerShell hosts, and the
  behavioural runner, because `skills/` changes.

## Questions the debate settled

All three of this design's open questions are closed. They are kept with
their answers rather than deleted, because the reasoning is the part a
later cycle would otherwise re-derive.

1. **Where the poll step lives — SETTLED: `model-prompting-notes.md`.**
   `SKILL.md` had twenty characters of headroom before its soft warning,
   which decided it. `SKILL.md` names the state count at the point of use
   and cites the region for the rest.
2. **Wrapper shipped under `tools/` or written per dispatch — SETTLED:
   written per dispatch, into a directory the dispatch creates.** Item 58
   is the argument against a new shipped tool: the skill has already
   failed to find its own tooling once and reported a false BLOCKED.
3. **Whether a timeout is documented — SETTLED at THIRTY MINUTES**, by the
   user on 2026-08-30, after Sol round 1 refused to leave it open. Each
   poll is bounded and returns; at thirty minutes without a terminal state
   the round is reported UNFINISHED and the user chooses to keep waiting
   or abandon. Neither answer is ever a review result, which is what
   stops a timeout policy from recreating the failure it manages.

## The contract regions this design produces

Five, in `model-prompting-notes.md`: `detached-dispatch-mechanism`,
`detached-dispatch-launch`, `detached-dispatch-states`,
`detached-dispatch-operation`, and `background-task-naming`. Naming is
separate from operation because it is the only one nothing enforces, and
a naming edit must not reopen a completion-safety pin.

## Item 33: build the review mirror instead of asking whether to

Added 2026-08-30, mid-cycle. **This is a scope increase and it is recorded
as one**, not folded in silently.

### What happened

The plan above was approved and this cycle's own plan debate was being
prepared. The preflight enumeration found an untracked `AGENTS.md` in the
repo root, and `SKILL.md:90-93` made the session stop and ask the user
whether to build the review mirror. The user's reply: **"This should never
prompt either, it should be implied to create the mirror."**

That is backlog item 33, filed by the same user on 2026-08-11 against a
screenshot from a DIFFERENT repo, which is what makes it a skill defect
rather than a parallax quirk. Its recorded verbatim ask then was: "Reviews
should always build the review mirror and copies repo to scratch folder if
agents.md and .agents are found. No prompt needed."

### Why it belongs in this cycle rather than its own

- Both items fired inside this cycle's first debate, minutes apart.
- Both are edits to `SKILL.md` under the same pins and the same gate
  profile. The backlog's own ranking rule says items sharing a file and a
  gate profile are built together rather than paying the same slow gate
  twice.
- Neither depends on the other, so a reviewer can reject one and keep the
  other.

### What changes

`SKILL.md:90-93` currently says "STOP and surface it to the user" and that
clearing happens "only on the user's choice, never automatically". Both
passages are replaced by a marked contract region that says to build the
mirror and report.

### Why this is safe, stated precisely

The mirror is a FILE COPY that preserves `.git`, and every deletion happens
in the copy. The user's working tree is never touched, so there is no
destructive act to consent to. That, and only that, is what makes removing
the question reasonable.

Item 33 records a second cost the prompt carried, and it is the stronger
reason: the two options offered were building the mirror and skipping the
cross-vendor lane. A question whose recommended answer has never once
differed should not put dropping that lane one tap away, at the moment the
user is least likely to be weighing it. Removing the question removes that
path.

### What must survive, or the fix is worse than the prompt

- **The check is not the question.** Only the question goes.
- The enumeration result stays EVIDENCE and stays in the debate record
  with the paths it found. An automatic mirror that stops reporting what
  it cleared trades a prompt for a blind spot.
- The post-mirror re-enumeration must still come back empty before any
  round dispatches.
- A mirror that cannot be built - path budget blown, scratch unavailable -
  is BLOCKED. It is never a fallback to dispatching over the real tree.

### Non-goal

Whether the old prompt should be available as an explicit opt-in is NOT
decided here and no opt-in is built. Item 33 lists it as an open question;
nobody has asked for it, and adding an unused lever to a preflight is how
the lever later becomes the default again.
