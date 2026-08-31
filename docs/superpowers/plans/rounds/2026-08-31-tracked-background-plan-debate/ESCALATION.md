# ESCALATED, and the build is stopped

**Status: the tracked-background plan is WITHDRAWN before Task 3. Tasks 1,
1a and 2 stay committed as evidence and are NOT to be built on.**

Owner's decision, 2026-08-31: take the escalation.

## What the reviewer said

`gpt-5.6-sol`, session `01a0584f-2b47-7130-af7c-9d8b2b2f188c`, round 2c,
bound clean, verdict **ESCALATE**. Raw reply: `sol-reply-r2c.md`.

> The two consecutive lost rounds, the false original premise, the cwd
> omission, and the new false-completion race are process evidence that
> this plan should not be incrementally pushed through.

## The finding that decided it, REPRODUCED by the session

The wrapper publishes `pid` and `startticks` as TWO independent
overwriting writes, with a measured 15-30ms gap between them. So:

1. Round A runs to completion, leaving `exit=0` and `reply`.
2. Round B starts from the same prepared directory and overwrites `pid`.
3. Before B overwrites `startticks`, `-Poll` reads B's LIVE pid against
   A's ticks, calls the identity mismatch DEAD, falls through to the
   terminal artifacts, and returns **`reply-present`, exit 0**.

B is unfinished. The poll says finished, and hands back A's answer.

Reproduced directly, not argued:

```
A finished. poll: reply-present
--- now simulate B: a LIVE pid overwrites A's, ticks not yet rewritten
live pid planted: 15776
reply-present
POLL EXIT: 0
```

**This is the exact class the entire item 32 cycle exists to close, put
back by the redesign meant to improve it.** It is in COMMITTED code, not
only in the plan, and it reaches all five call sites because they share
the two-write shape.

The remedy the reviewer names, and which the replacement plan must carry:
a persistent create-new EXECUTION claim, and ONE atomically published
identity record holding pid and ticks together. The receipt binds the
directory; nothing binds one execution within it.

## The other blocking findings, all accepted

1. **The `Set-Location` correction cannot fail hard.** It has no
   `-ErrorAction Stop`, and it sits before the wrapper's `try`. A missing
   target reports a non-terminating error and execution CONTINUES into the
   client from the harness's directory - the silent fallback the
   correction existed to prevent. The receipt schema has four fields and
   none of them is the working directory, so nothing binds it; and the
   route check verifies model, provider, effort and sandbox but never
   `workdir:`.

2. **The evidence-bookmark defect is CROSS-LANE and documented, not just
   my slip.** `SKILL.md` and `fallbacks.md` both say later rounds chain
   from the previous clean `nextState`, and a failed binding emits no
   `nextState` at all. So any void or refused attempt advances the
   append-only rollout and leaves the bookmark behind, breaking every
   later round. The same chaining assumption is in the Kimi lane. The
   four-user-record refusal was correct; the protocol feeding it was
   wrong. The fix must make "captured before dispatch" ENFORCEABLE -
   sealing the prior-state digest into the create-new preparation receipt,
   so a state reconstructed after the reply cannot satisfy it.

3. **Deleting the launcher dropped more than the working directory.** It
   also selected the caller's PowerShell host, and `SKILL.md` itself
   records that a bare `powershell` silently turns a PS7 call into PS5.
   `-NoProfile`, `-NonInteractive`, stdin EOF, stdout/stderr ownership,
   process-tree termination and task cancellation are all unsettled.
   `stdin.empty` is still created with no consumer named.

4. **The plan never tests its own principal benefit.** The spec promises a
   named task row, a completion notification and an open conversation.
   Task 6 measures prepare time and poll states. Those harness behaviours,
   and what happens to a round when the session ends, need direct probes -
   the spec currently says the worker "probably" dies with the session
   rather than measuring it.

5. **A typo'd optional switch produces a wrong interface, not a refusal.**
   `-Poll ... -Jsoon` is silently ignored and poll emits plain text where
   the caller asked for JSON. `-Prepare` has the same branch. The plan's
   own test supplies the typo with NO valid mode, so it passes without
   exercising the case.

6. **The plan contradicts itself.** Task 1 was edited to claim it kept
   `-WorkingDirectory`; Task 1a truthfully says Task 1 deleted it. Task 3
   still says "all four parameters" when the corrected interface has five.

## What the reviewer did NOT fault

- Deleting the pid-only kill, `GetProcessTimes` and the top-level
  `Add-Type` along with the launcher is the right disposal, not a dodge:
  `-Prepare` starts no process, so those launch-only failure paths cannot
  exist.
- Collapsing never-run, died-before-identity and live-before-identity into
  `not-started` is conservative and safe for RESULT purposes. The name is
  too strong operationally: it must mean "identity not yet available",
  never "safe to start again". A missing or unreadable `cwd` is a
  different thing again - committed-preparation corruption, possibly after
  execution began - and deserves its own non-zero state.
- The `AGENTS.md` untracking plus ignore rule, and the budget revert to
  5250 with the ceiling left at 6500, are both sound.
- The visibility-over-survival trade is reasonable, but is currently
  asserted rather than measured.

## The Task 3 size question, answered

Move HISTORICAL and RATIONALE material out of `SKILL.md` while keeping the
complete operational shape independently at BOTH call sites. Do not
globally deduplicate the sites - that duplication is what caught a call
site left in the foreground - and do not raise the ceiling first. Only if a
measured, materially trimmed skill still will not fit should a minimal,
explicitly pinned ceiling increase be considered.

Session sizing, for the replacement plan: the body is 6372 of 6500. The
preflight section holds 1976 and most of it is mirror-building detail read
only when the enumeration actually finds something. Moving that lands the
body near 5600. Five contract regions live in that section and their
declarations and pins must move with them.

## What happens next

1. Nothing further is built against
   `docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md`. It
   is withdrawn.
2. The invariants get re-derived first, and named explicitly: dispatch,
   working-tree identity, EXECUTION identity, harness visibility, and the
   evidence-boundary lifecycle.
3. A replacement plan is written against those invariants and REVIEWED
   before any implementation resumes. This plan went from an approved
   design straight into building, which is how every defect above reached
   committed code.
4. Task 3's work stays stashed. Tasks 1, 1a and 2 stay committed as
   evidence of what was tried and why it was stopped.

## Cost of this debate, stated plainly

Four dispatches, two of them thrown away unread, both losses the
session's own doing: one ran in the real repository because the spec
deleted the anchor, one could not be attributed because the bookmark was
two rounds stale. The reviewer was never at fault in either.
