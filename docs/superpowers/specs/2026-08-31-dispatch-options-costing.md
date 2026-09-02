# Costing the dispatch options, before any plan is written

Written 2026-08-31, after the tracked-background plan was withdrawn on an
ESCALATE and the owner settled two rules: the harness-tracked background
command is the ONLY dispatch method, and survival past session end is NOT
a requirement.

This document costs THREE options against those rules and the invariants in
`2026-08-31-dispatch-invariants.md`. It recommends one. It is the input to
a three-lane poll, not a decision.

## The environment this must work in, stated as requirements

Owner's specifications for working in Claude Code, gathered across this
session and treated as fixed:

- **R1.** A long call must never own the session. The user keeps talking to
  the agent while it runs.
- **R2.** The running work must be VISIBLE, by a name that says which lane
  and which round it is.
- **R3.** Completion must announce itself. No polling loop as the primary
  signal.
- **R4.** ONE backgrounding method, everywhere. Five variants appeared in
  one session and that itself is the defect.
- **R5.** No windows, no focus stealing. Test children included.
- **R6.** A reviewer never reads the live repository. Always a frozen copy
  at a named commit.
- **R7.** Surviving session end is NOT required.

And the standing safety property, unchanged since item 32:

- **R8.** A killed, hung, or unfinished round must never read as a
  completed one.

## What the harness gives for free

Measured this session:

- A named task row for any command dispatched with the harness's own
  background flag.
- A completion notification carrying the task id and an output file path.
- That output file holds the command's stdout and stderr, and a trailer
  naming its exit code.
- No 600-second ceiling on it. And measured separately: a FOREGROUND call
  that overruns the ceiling is moved to the background rather than killed.

## What the harness does NOT tell you

It reports that the COMMAND exited. It says nothing about whether the ROUND
produced a usable reply. These come apart routinely on this transport:

- the client exits non-zero having written no reply;
- it exits zero with an empty reply file;
- a content filter refuses the round after the brief lands, so no reply is
  written and the quota is spent anyway (recorded, 2026-08-20);
- a reply file from an earlier run is still on disk and reads exactly like
  a fresh one.

Telling those apart is the job of the classifier, and it is the part of
item 32 that survived two independent reviews.

---

## Option A: harness background command, nothing else

Dispatch the client call directly as a named background command. Read the
harness output file when the notification arrives.

**Cost of ownership:** near zero. No tool, no receipt, no states, no pins.

**Where it fails R8.** Every distinction in the list above collapses into
"the command exited, go read some files and judge". That judgment is the
session's, unaided, every round. The whole item 32 cycle exists because
that judgment was wrong often enough to matter. A stale reply from a
previous attempt is indistinguishable from a fresh one, which is the
`fallbacks.md` stale-reply class by construction.

**Verdict: rejected.** It satisfies R1 to R7 and abandons R8.

---

## Option B: the withdrawn design, repaired

Prepare the round, publish process identity atomically, keep the full
liveness model, add an execution claim, bind the working directory, seal
the evidence boundary.

**Cost of ownership:** the largest. Thirteen-plus states, an atomic
identity record, a create-new execution claim, recycled-pid handling,
start-time comparison, and per-host process APIs. This is the design that
just produced a reproduced false-completion race, and the repair list from
the ESCALATE runs to six items before it is even safe to build.

**What its complexity is FOR.** Almost all of it answers one question: *is
the process still running?* Process id, start ticks, liveness, recycled
pids, `not-started`, `pid-unreadable`, the DEAD branch.

**Under R7, that question has changed owner.** The harness owns the
process and announces its completion. The tool was inferring, expensively
and wrongly, something the harness now simply states.

**Verdict: not recommended.** It is carrying a liveness model whose reason
for existing was the detached launcher the owner has now forbidden.

---

## Option C, RECOMMENDED: receipt and reply classification, no liveness

Keep the two things that earned their place; delete the part that exists
only to infer liveness.

**Keep:**
- `-Prepare` builds the round's directory as one fail-closed transaction,
  refuses to reuse an existing directory, records the working directory,
  and writes the receipt LAST.
- A create-new EXECUTION CLAIM as the wrapper's first act. Second run of
  the same prepared wrapper fails immediately, before it can touch
  anything.
- Classification of the OUTCOME: claim present, exit file present and
  readable, exit value, reply present, reply non-empty.
- The working-directory binding, checked against the client's own
  `workdir:` line.
- The evidence boundary sealed into the receipt before the wrapper can run.

**Delete:** process id, start ticks, liveness, recycled-pid handling, the
DEAD branch, `pid-unreadable`, `not-started`, and every per-host process
API call.

**Resulting states, all non-zero but `reply-present`:**
`no-receipt`, `receipt-not-expected`, `no-claim`, `no-exit-file`,
`exit-unreadable`, `exit-nonzero`, `no-reply`, `reply-empty`,
`reply-present`. Nine, down from thirteen.

**How it holds R8 without liveness:**
- Stale artifacts: `-Prepare` refuses an existing directory, so a fresh
  round never inherits an old reply. Structural, not a check.
- Double execution: the create-new claim makes the second run fail before
  it writes anything. This is the reviewer's own prescription, minus the
  identity record.
- Unfinished: no `exit` file means `no-exit-file`, non-zero. A round that
  died mid-flight cannot present as complete.
- Still running: also `no-exit-file`. **The tool cannot distinguish
  running from crashed, and does not try.** The harness distinguishes
  them, by notifying. Both are non-zero, so the conservative direction is
  preserved either way.

**The cost, stated plainly, because it is a real loss:**
- The tool alone can no longer answer "is it running". That answer now
  lives only in the harness's notification.
- **If a notification is missed** - session compaction, an interrupt, a
  client restart - the session cannot tell a still-running round from a
  crashed one without looking at the process table by hand. Under R7 this
  is recoverable by re-dispatching, but it IS a capability the current
  design has and this one gives up.
- Two of today's reproduced defects came from the machinery being
  deleted, so deleting it removes them; but "we deleted the buggy part" is
  not by itself proof the remainder is sound, and the remainder has not
  been reviewed.

**Cost of ownership:** roughly half of Option B. No C#, no process APIs,
no host-specific liveness, four fewer states.

---

## Recommendation

**Option C.** It satisfies R1 to R7, holds R8 by construction rather than
by inference, and deletes the exact class that produced the reproduced
race. The liveness model was load-bearing only for a launcher the owner
has forbidden; keeping it would be carrying the cost of a decision already
reversed.

## R9, added by the poll: the harness's exit code is NOT a round result

**Found by the Fable lane, CONFIRMED LIVE by the session the same hour.**

The wrapper writes the client's exit code into an `exit` FILE and then
ends. It never runs `exit $code`, so the WRAPPER PROCESS exits 0 whatever
the client did. Under the detached design nobody read the wrapper's
process exit, so this was invisible. Under the harness-tracked method the
harness records it, puts it in the output trailer, and ANNOUNCES it in the
completion notification.

Confirmed on a real failed round, 2026-08-31: the Kimi poll round shattered
its brief on Windows PowerShell 5.1, the client exited 1 and wrote no
reply, the `exit` file correctly recorded `1`, and the harness reported:

```
[exited with code 0]
```

with a completion notification reading "completed (exit code 0)". A failed
round announced itself as a success on the harness surface. The session was
not misled only because it opened the `exit` file instead of trusting the
notification.

**This is a false-clean surface CREATED by the method being standardised
on.** It is not R8 - the round is finished, not unfinished - which is why
R1 to R8 did not forbid it.

**R9. The harness's exit surface is never a round result.** Only the
classifier's `reply-present` is. And the wrapper's last statement must be
`exit $code`, so the trailer and the `exit` file cannot disagree in the
first place.

## What the poll is being asked

1. Is Option C's claim sound - that a create-new execution claim plus
   refusal to reuse a directory replaces the liveness model for R8
   purposes? Attack it. Name a case where an unfinished or killed round
   reads as completed under C.
2. Is losing "running versus crashed" acceptable given R7, or is it worse
   than it looks?
3. Is there a FOURTH option better than all three? Say so and cost it.
4. Anything in the requirements R1 to R8 that is wrong, missing, or in
   conflict with another.
