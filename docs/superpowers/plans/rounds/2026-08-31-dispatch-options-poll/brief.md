# Three-lane poll: how should a review round be dispatched?

You are one of THREE reviewer lanes being asked the same question
independently. The other two are the cross-vendor codex lane and the
Claude-side panel lane. Your answer will be compared with theirs, so
answer from the documents and the repo, not from what you think the
session wants to hear.

You are reading a FROZEN FILE COPY of the repository at commit `25dde0c`.
Every path below resolves inside it. Ground every claim in a `path:line`
you actually opened.

## Read these first, in full

- `docs/superpowers/specs/2026-08-31-dispatch-options-costing.md` - the
  three options, the requirements, and the session's recommendation.
- `docs/superpowers/specs/2026-08-31-dispatch-invariants.md` - the
  properties any design must hold, each one there because something broke
  it.
- `docs/superpowers/plans/rounds/2026-08-31-tracked-background-plan-debate/ESCALATION.md`
  - why the previous attempt was withdrawn.

## The situation, briefly

Backlog item 32 shipped a tool that dispatches a review round as an
OS-DETACHED process, with a receipt and a thirteen-state completion model.
It works and it passed two independent reviews.

Then three things happened.

**One: the premise was false.** Item 32 was justified by "a foreground
round is KILLED at the 600-second tool ceiling, quota spent for nothing",
recorded as measured fact since 0.21.x. Re-measured 2026-08-31 on Claude
Code 2.1.251: an 11-minute foreground command crossed the ceiling, was
MOVED TO THE BACKGROUND by the harness, completed, and returned exit 0 with
its output intact. Nothing is killed.

**Two: the real defect is different.** A foreground call OWNS the session.
The user cannot see which round is running and cannot talk to the agent
until it ends. The detached tool fixed the blocking and, because the
harness does not track an OS-detached process, ALSO destroyed the
visibility the harness was already providing for free.

**Three: the redesign that tried to fix that was withdrawn on an
ESCALATE**, after the session reproduced a false-completion path in its own
committed code: `pid` and `startticks` published as two separate writes let
an unfinished second run be reported as `reply-present` at exit 0, handed
the first run's answer. Its code has been reverted.

## What the owner has already SETTLED, and is not up for review

- The harness-tracked background command is the ONLY dispatch method. A
  tool may PREPARE work and CLASSIFY its completion; it may not launch its
  own process, because a process the harness does not own is a process the
  user cannot see.
- Surviving past session end is NOT a requirement. A round that dies with
  the session is acceptable. A round nobody can see is not.
- A reviewer never reads the live repository. Always a frozen copy at a
  named commit.

Do not re-litigate these. Design within them.

## The question

The costing document sets out three options. In short:

- **A**: dispatch the client call as a named background command and read
  the output file. No tool, no receipt, no states.
- **B**: the withdrawn design, repaired. Keeps the full liveness model:
  process id, start ticks, recycled-pid handling, thirteen states.
- **C, recommended**: keep the receipt, the fail-closed preparation, a
  create-new EXECUTION CLAIM as the wrapper's first act, and classification
  of the OUTCOME. DELETE the entire liveness model, because it existed to
  infer something the harness now simply announces. Nine states, only
  `reply-present` at exit 0.

The session's reasoning for C: almost all of B's complexity answers "is
the process still running", and under the settled rules the harness owns
the process and notifies on completion. C holds the safety property by
CONSTRUCTION - a fresh directory cannot inherit an old reply, and a
create-new claim makes a second execution fail before it writes anything -
rather than by inference.

The session's stated cost of C: the tool can no longer distinguish "still
running" from "crashed". Both land on `no-exit-file`, non-zero, so the
conservative direction holds, but if a completion notification is ever
MISSED the session cannot tell them apart without inspecting the process
table by hand.

## Answer these, in order

1. **Attack C's central claim.** Does a create-new execution claim, plus
   refusal to reuse a dispatch directory, actually replace the liveness
   model for the purpose of "a killed, hung or unfinished round must never
   read as a completed one"? Name a concrete case where an unfinished or
   killed round reads as COMPLETED under C, or state explicitly that you
   searched and found none, naming what you searched for.

2. **Is losing "running versus crashed" acceptable**, given that survival
   past session end is not required and the harness notifies on
   completion? Or is that loss worse than the session thinks?

3. **Is there a FOURTH option** better than all three? If so, cost it
   against the same requirements. Do not propose one that launches its own
   process; that is settled.

4. **Are the requirements themselves right?** R1 to R8 are in the costing
   document. Name anything wrong, missing, or in conflict.

5. If you would ship C as recommended, say so plainly. If not, name the
   smallest change that would make you ship it.

Be concrete and cite `path:line`. Say when you are speculating. If you
searched for a defect class and found nothing, say so explicitly and name
the shapes you searched for - a clean sheet has to be argued for, not
assumed.

End with PASS, FIX, or ESCALATE.
