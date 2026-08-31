# Dispatch invariants

Written 2026-08-31, after the tracked-background plan was withdrawn on an
ESCALATE. This document does NOT propose a mechanism. It states the
properties any dispatch design must hold, why each exists, and how each one
was broken in practice, so the next plan is argued against something rather
than invented.

Read `docs/superpowers/plans/rounds/2026-08-31-tracked-background-plan-debate/ESCALATION.md`
first. Every invariant below is here because something violated it.

A property is marked **MEASURED** when this repo has run the experiment,
**CONTRACT** when it is asserted by a pin, and **UNMEASURED** when it is
currently believed rather than known. Do not promote an UNMEASURED line
without an experiment.

---

## A. Dispatch

**A1. A dispatch must not own the session.** A foreground call blocks the
conversation for its whole duration: the user cannot see which round is
running and cannot talk to the agent at all. This, and not any kill, is the
defect item 32 exists to remove.

**A2. The 600-second ceiling does not kill. MEASURED 2026-08-31, Claude
Code 2.1.251.** An 11-minute foreground command crossed the ceiling, was
MOVED TO THE BACKGROUND by the harness, completed, and returned exit 0 with
its output intact. The contrary rule sat in `CLAUDE.md` as measured fact
since 0.21.x and was never re-measured. Any design that justifies itself by
the kill is justifying itself by a fiction.

**A3. The interpreter is part of the dispatch, and it is not implied.
MEASURED 2026-08-31.** On this machine a bare `powershell` is
**5.1.26100.9168** and a bare `pwsh` is **7.6.5**. A dispatch that names
neither runs whichever the caller's PATH resolves, so a round intended for
PowerShell 7 silently runs on 5.1 - which is the host whose ANSI decode and
us-ascii `$OutputEncoding` corrupt a brief. The old launcher chose the
host implicitly by re-executing the caller's own executable. Any design
that stops doing that MUST choose explicitly.

**A4. A dispatch's execution environment is contract, not convention.**
`-NoProfile` and `-NonInteractive`, stdin at EOF, and where stdout and
stderr go are all part of what makes a round reproducible. The withdrawn
design named a command to run and settled none of them, and left
`stdin.empty` created with no consumer.

---

## B. Working-tree identity

**B1. The reviewed tree is the review mirror, always, and it must be
impossible to get this wrong silently.** A round that runs in the real
repository reads any root `AGENTS.md` as instructions. That is the
back-channel the preflight exists to stop.

**B2. This failed by DELETION, not by mistake in use.** The withdrawn spec
removed `-WorkingDirectory` as launcher plumbing. It was the anchor. The
next round ran in the real repository, its reply was discarded unread, and
nothing failed loudly at any point.

**B3. An anchor that cannot fail hard is not an anchor.** The correction
added `Set-Location` with no `-ErrorAction Stop`, before the wrapper's
`try`. A missing target reports a non-terminating error and execution
CONTINUES into the client from the caller's directory - the exact fallback
the correction was written to prevent.

**B4. The working directory must be BOUND, not merely passed.** The receipt
schema has four fields and none of them is the working directory. Nothing
detects a wrong initial value, a post-preparation mutation, a deleted
target, or a non-filesystem provider.

**B5. The tree must be confirmed from the CLIENT's own report.** The route
check reads `model:`, `provider:`, `reasoning effort:` and `sandbox:` from
the transcript and never reads `workdir:`. The client states where it ran;
that line is evidence and is currently ignored. Had it been checked, the
void round would have been caught before its reply was written rather than
after.

---

## C. Execution identity

**C1. The receipt binds a DIRECTORY. Nothing binds an EXECUTION within
it.** This is the gap that stopped the plan.

**C2. Identity must be published atomically. REPRODUCED 2026-08-31.**
`pid` and `startticks` were two independent overwriting writes with a
measured 15-30ms gap. Re-running a prepared wrapper gives:

```
A finished. poll: reply-present
--- now simulate B: a LIVE pid overwrites A's, ticks not yet rewritten
live pid planted: 15776
reply-present
POLL EXIT: 0
```

A live pid with the previous run's ticks reads as an identity mismatch,
which classifies DEAD, which falls through to the earlier run's terminal
artifacts and returns success. **An unfinished execution reported as a
completed one, at exit 0** - the exact class the whole cycle exists to
close. One record holding pid and ticks together, published in one act, is
the floor.

**C3. A completed round's artifacts must not be able to answer for a later
round.** `reply` and `exit` outlive the execution that wrote them. Re-use
of a prepared directory must be refused by a persistent create-new
EXECUTION claim, not merely discouraged.

**C4. Liveness is pid PLUS start time, never a pid alone. CONTRACT**,
pinned in the `detached-dispatch-states` region. It has been violated twice
in this cycle's own code: in the launcher's catch-side kill, and in the
behavioural harness's reaper. Both were found by review, not by a gate.

**C5. Unknown must classify as NOT ours.** Every unreadable, unmeasurable
or absent identity input must land on a non-zero state. This holds today
and is the reason the tool survives the cases it does.

---

## D. Harness visibility

**D1. The user must be able to see a running round by name, and keep
talking.** This is the actual deliverable. `Sol R1 debate round` in the
task list, a completion notice, an open conversation.

**D2. The naming convention has no mechanism. CONTRACT-ONLY.** The
`background-task-naming` region is a documentation-presence pin. Nothing
enforces that a dispatch is actually named, or named correctly.

**D3. Visibility and survival are in tension, and the trade is
UNMEASURED.** A tracked task belongs to the session. The withdrawn spec
said the worker "probably" dies with the session and never measured it. The
owner chose visibility over survival, and that choice is sound, but it is
currently made against a guess. **Measure what happens to a running tracked
command when the session ends before the replacement plan freezes this.**

**D4. A design must test its own benefit.** The withdrawn plan measured
preparation time and poll states and never once checked that a task row
appeared, that a notification arrived, or that the conversation stayed
open. A benefit nothing tests is a benefit nobody has.

**D6. THE METHOD OF BACKGROUNDING IS ITSELF THE CONTRACT, not an
implementation detail.** Owner's instruction, 2026-08-31: backgrounding
matters, and so does HOW. FIVE different mechanisms were used in a single
session, each with different visibility, notification and evidence:

| # | Mechanism | Task row | Notifies | Survives session end | Evidence |
|---|---|---|---|---|---|
| 1 | Bash tool `run_in_background` | yes, named | yes | no | harness output file |
| 2 | `dispatch-detached.ps1 -Launch`, OS-detached | NO | NO | yes | receipt + poll |
| 3 | `-Prepare` then (1) runs the wrapper | yes, named | yes | no | receipt + poll |
| 4 | Agent tool subagent in background | yes | yes | no | agent report |
| 5 | Foreground call auto-backgrounded at the ceiling | yes, mid-flight | yes | no | harness output file |

Mechanism 2 is what item 32 shipped and is the one the owner objected to:
it removes the blocking AND the visibility. Mechanism 5 is not a choice,
it is the harness rescuing an overrun. Mechanism 4 nests: a subagent that
starts its own background command produced the stalled turns seen four
times this cycle.

**The standing rule: mechanism 1 is THE method.** A long call is dispatched
by the harness as a tracked background command, named for its lane and
round, or with no lane for its kind. Anything else must be justified in
writing at the call site. A tool in this repo may PREPARE work and CLASSIFY
its completion; it may not launch its own process, because a process the
harness does not own is a process the user cannot see.

Corollary for the replacement plan: this makes D1 concrete. The
requirement is not "the user can see it somehow", it is "the round is a
harness-tracked task with a lane-and-round name", and the plan must test
exactly that.

**D5. Test children must not steal the screen. MEASURED 2026-08-31.**
Spawning with a new visible console pops a window per spawn and takes
focus; across 71 tests that is a storm. `STARTUPINFO`'s `SW_HIDE` is
advisory for a newly created console and Windows ignored it. The private
console needed for encoding isolation must be obtained WITHOUT a window.

---

**D7. A reviewer NEVER reads the live repository.** Owner's decision,
2026-08-31, standing. Every round runs against a frozen file copy at a
named commit, built by `tools/new-review-mirror.ps1`. Two reasons, both
measured this cycle: the live tree carries instruction back-channels the
copy has removed and re-verified as gone, and a live tree changes under a
running review, so its verdict describes a state that no longer exists and
nothing records which state was read. The snapshot's cost is accepted: a
fix made mid-round is invisible to that round, and the answer is to
re-dispatch rather than to pretend the reviewer saw newer code.

## E. Evidence-boundary lifecycle

**E1. A reply is evidence only if it is bound to the brief this side
sent.** Unchanged, and the mechanism works: it caught both bad rounds this
cycle.

**E2. The bookmark must be captured immediately before EVERY dispatch, not
inherited from the last good one.** `SKILL.md` and `fallbacks.md` both
document chaining from the previous clean `nextState`, and a failed binding
emits no `nextState` at all. So any void or refused attempt advances the
client's append-only rollout and leaves the bookmark behind, breaking every
later round in that session. **This is a shipped cross-lane defect**: the
same chaining assumption is in the Kimi lane.

**E3. Discarding a REPLY does not discard the RECORDS.** A voided round
lives in the rollout forever. This is why E2 bites.

**E4. "Captured before" must be ENFORCEABLE, not honour-system.** A
bookmark reconstructed after the fact can be made to bind any reply, which
is precisely the shape that lets an unattributable round read as clean.
The reviewer's remedy: seal the prior-state digest into the create-new
preparation receipt, before the wrapper can run, so a state computed
afterwards cannot satisfy it.

**E5. An unmade measurement and a clean one must never look alike.**
CONTRACT, and the standing rule the rest of this document is an instance
of.

---

## F. Interface honesty

**F1. A mistyped switch must be refused, not absorbed.** The script has an
ordinary parameter block and never rejects `$args`, so `-Poll ... -Jsoon`
is silently ignored and poll emits plain text where the caller asked for
JSON. `-Prepare` has the same branch. The existing test supplies a typo
with NO valid mode, so its own mode check returns 2 and the real case is
never exercised.

**F2. A contract must describe the mechanism that actually holds.** The
exit-2 promise was documented against an assumed host-binder rejection.
Measured, the host does not reject at all; the script's own mode check is
what returns 2. Both hosts returned exit 2 - the right answer for the wrong
stated reason.

---

## What the replacement plan must do with this

1. Settle A3 and A4 explicitly. Name the interpreter and the flags.
2. Make C2 impossible by construction, and prove it with a
   concurrent-double-start test, a rerun-after-completion test, and a
   death-between-identity-writes test.
3. Bind the working directory into the receipt (B4) and check the
   client's own `workdir:` line (B5).
4. Make the anchor terminating (B3).
5. Seal the evidence boundary into the receipt (E4), and fix the chaining
   rule in BOTH lanes (E2).
6. Reject unknown arguments (F1).
7. Measure D3 before freezing the trade, and add probes for D1.
8. Move historical and rationale text out of `SKILL.md`, keeping the full
   operational shape at BOTH call sites, and do not raise the ceiling
   first. The body is 6372 of 6500; the preflight section holds 1976, most
   of it read only when the enumeration finds something, and five contract
   regions whose declarations and pins must travel with it.

**Then review the plan before building from it.** The withdrawn plan went
from an approved design straight into implementation, and every defect
above reached committed code.
