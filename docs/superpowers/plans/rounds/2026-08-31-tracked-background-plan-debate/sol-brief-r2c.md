# Round 2 - the premise you reviewed against was wrong, and there is a NEW plan

Same debate, same branch. Two things changed since your round 1, and the
second one is why this round exists.

The mirror is rebuilt at the SAME path from head `0105d3a`.

## 1. Your round 1, settled

Your five findings, all accepted:

- **`AGENTS.md` not actually removed** - you were right and I was wrong. My
  `git rm --cached` was undone by a later `git add -A` in the same session,
  which re-tracked the file. It is now untracked for real AND gitignored,
  so the same mistake cannot repeat. Verified: `git ls-tree HEAD --
  AGENTS.md` is empty. The preflight still SEES it, because that
  enumeration uses `--others` WITHOUT `--exclude-standard`.
- **Budget raise** - reverted to 5250, ceiling kept at 6500, pins updated.
- **The dispatcher's pid-only kill, the `GetProcessTimes` orphan, and the
  top-level `Add-Type`** - NOT patched. All three are deleted along with
  the launcher, for the reason below. Confirm that is the right disposal
  rather than a dodge.
- **The reaper fix** - you judged it correct; unchanged.

## 2. THE PREMISE OF THE WHOLE CYCLE WAS FALSE

Item 32 says a review round dispatched in the FOREGROUND is KILLED at the
600-second tool ceiling: no reply file, quota spent for nothing. That has
been in `CLAUDE.md` as measured fact since 0.21.x, through five release
cycles.

The user noticed that several commands that day had overrun and been moved
to the background rather than killed, and asked whether our own change had
caused a loss of task visibility. I measured the ceiling instead of
arguing:

    10:09:17  start
              SURVIVED THE CEILING
              exit 0
    10:20:17

An 11-minute command crossed the ceiling, was MOVED TO THE BACKGROUND by
the harness, completed, and returned exit 0 with its output intact.
Nothing was killed. The rule was never re-measured against a newer client;
it was believed because it was written down.

**The real defect is different, and the user named it.** A foreground
dispatch OWNS the session for its whole duration: he cannot see which round
is running, and cannot talk to the agent at all until it ends. The shipped
tool fixed the blocking by launching an OS-DETACHED process - which the
harness does not track, so it also destroyed the visibility the harness was
already providing for free. No task row, no lane-and-round name, no
completion notice. That is a worse trade than the one it replaced.

## 3. What I want reviewed: the NEW spec and plan

- Spec: `docs/superpowers/specs/2026-08-31-tracked-background-dispatch-design.md`
- Plan: `docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md`

The design in one line: the tool PREPARES the round and stops; the caller
runs the prepared wrapper as a TRACKED BACKGROUND command named for its
lane and round; each wrapper publishes its own pid and start ticks as its
first act; `-Poll` gains one state, `not-started`.

**This plan has had NO review rounds.** The item 32 plan you reviewed had
23 cross-vendor rounds plus 6 on the Claude side before it was frozen. This
one went straight from an approved design to building, and the user has now
stopped the build to have it reviewed. Assume it is under-cooked.

Tasks 1 and 2 are already BUILT and committed against it, so judge them as
built code, not as proposals:

- Task 1 `041e042` - the launcher is gone (~200 lines of C# with it),
  `-Prepare` replaces `-Launch`, thirteen states, 67 tests green on BOTH
  hosts. `-Poll` now compares a live process's start time against the
  `startticks` FILE the wrapper writes, because the receipt can no longer
  know a real process's ticks and carries a placeholder `0`. **Judge that
  substitution specifically: is a file inside the dispatch directory a
  sound identity anchor, given the receipt binds that directory?**
- Task 2 `5992f69` - the three contract regions rewritten and re-pinned,
  each mutation-tested red and restored.

**Also measured, and it changes your round-1 finding 4:** the script has no
`[CmdletBinding()]`, so an unknown switch is NOT rejected by the host at
all. It is absorbed into `$args`, the script runs on, its own mode check
finds neither mode bound, and it exits 2. Both hosts returned exit 2. So
the promise holds for that case, by a different mechanism than either of us
assumed. **But I want you to attack the general case: a typo'd OPTIONAL
switch in an otherwise valid invocation is silently absorbed and ignored.
Is there an invocation where that produces a wrong answer rather than a
refusal?**

## 4. Task 3 is BLOCKED, and it is the plan's fault

Task 3 rewrites SKILL.md's two codex call sites. Built, it measures 6610
estimated tokens against a hard ceiling of 6500. The body was ALREADY at
6372 before the task touched it, so roughly a third of the overage is new
and two thirds was pre-existing.

The plan mandated the wrapper content verbatim AND told the implementer not
to raise the ceiling, without checking whether the two could both hold.
That is a plan defect, not an implementer failure. The work is stashed, not
committed.

The three ways out I can see:

- move branch-only text out of `SKILL.md` into a references file, which is
  what the lint error itself recommends;
- raise the ceiling deliberately, with the measurement and reason recorded
  and a test pinning it, which is how 6500 was set;
- restructure the per-site duplication - but note WHY it is duplicated:
  round 6 of the original plan debate found that a GLOBAL count let one
  call site stay foreground undetected, so each site carries the full
  shape on purpose.

Tell me which, and say what it costs.

## What I want from you

1. **Judge the new spec and plan as a whole.** They are unreviewed. Name
   what is wrong with them, not only Task 3's ceiling problem.

2. **The central question, again, because the mechanism changed
   underneath it.** With the launcher deleted and the wrapper publishing
   its own identity, does anything let a killed, hung or unfinished round
   read as a COMPLETED one? Do not carry your round-1 answer forward: the
   code it described is gone. Name an instance or say explicitly that you
   searched and found none, naming what you searched.

3. **Is `not-started` correctly placed and correctly conservative?** It
   covers "never run" and "died before publishing identity" without
   distinguishing them, and a live wrapper that has not yet written its pid
   also lands there. Is collapsing those three right?

4. **The trade.** A tracked task belongs to the session and probably dies
   with it, where a detached process would have survived and could be
   collected later by a fresh `-Poll`. The user made this trade knowingly
   for visibility. Is there a design that keeps both, or is the trade real?

5. **Sweep the CLASS of anything you find** and either name another
   instance or state that you searched and found none, naming the shapes
   you searched for.

End with PASS, FIX, or ESCALATE.

---

## ADDENDUM: this round is a re-dispatch, and the reason is a finding

The first attempt at this round was VOID and its reply was discarded
UNREAD. Recording it here because it is evidence about the plan you are
reviewing, not housekeeping.

**What happened.** My new spec dropped `-WorkingDirectory` from `-Prepare`,
calling it launcher-only plumbing. It was not. It was what put the client
inside the REVIEW MIRROR. With the launcher deleted and nothing setting a
working directory, the wrapper ran wherever the harness started it, which
was the REAL REPOSITORY. Its `workdir:` header read
`C:\Users\Brandon\Documents\parallax`, where a root `AGENTS.md` sits on
disk and the client auto-ingests it as instructions. That is the
instruction back-channel the preflight exists to stop. Cost: one round.

**What I changed before re-dispatching**, at `937bcb0`:

- `-Prepare` keeps `-WorkingDirectory`, MANDATORY, and writes the resolved
  path to a `cwd` file inside the dispatch directory.
- Each wrapper's SECOND act is `Set-Location` to that recorded value, so
  the anchor lives in wrapper text that every per-site test pins, rather
  than in launcher plumbing that nothing pinned.
- A dispatch directory with no readable `cwd` is `not-started`. It can
  never silently fall back to the caller's directory.
- New Task 1a carries this, because Task 1 is already committed.
- An end-to-end test deliberately starts the command in the WRONG
  directory and fails unless the wrapper corrects itself.

**Judge this too**, and treat it as the strongest available evidence about
how carefully the rest of the plan was written:

1. Is the `cwd`-file plus `Set-Location` mechanism sound, or does it just
   move the same silent failure somewhere new? In particular: the wrapper
   reads a file it was handed. What stops a wrong or stale value there?
2. Is `not-started` the right classification for a missing `cwd`, or does
   it overload a state that already carries three meanings?
3. **The obvious question I want answered directly: what ELSE did that
   draft delete or assume without checking?** I found this one by losing a
   round to it. Sweep the spec and plan for the same shape - something
   called incidental that is load-bearing - and either name another
   instance or say explicitly that you searched and found none, naming
   what you searched for.

Note on your working directory for THIS round: you are in the mirror,
rebuilt at the same path from head `937bcb0`, so the plan and spec you
open ALREADY CONTAIN the fix described above, including Task 1a. Review
them as they stand.

---

## SECOND ADDENDUM: this is the third attempt, and the second loss was mine too

Round 2b reached you correctly - right mirror, right route - and I threw
its reply away UNREAD. Recording why, because it is another data point
about how carefully this cycle has been run.

The round-evidence binder refused it: *"a resumed slice may carry at most
two user records, the client's instructions preamble and the brief, found
4."* Correct refusal. My prior-state bookmark still pointed at the end of
round 1, and the session had since grown by TWO rounds - the void one and
2b - so the reply could not be attributed to a single brief.

**Discarding a round's REPLY does not discard its RECORDS.** The void round
lives in your append-only rollout forever, and any later resume measured
from a bookmark taken before it spans more than one round and is refused.

I could have reconstructed a bookmark after the fact to make 2b bind. I did
not: a bookmark computed to make a specific reply pass is exactly the shape
that lets an unattributable round read as clean. So the round was paid for
and discarded.

**A fresh bookmark was taken immediately before THIS dispatch**, which is
the rule that should have applied all along.

Add this to question 3 in the first addendum. You are now looking at a
cycle where the session has lost two consecutive rounds to its own
bookkeeping, after building a whole tool against a premise it never
re-measured. **Weigh the plan accordingly, and say plainly if you think the
work should be paused and re-planned rather than pushed through.** I would
rather hear that than a list of fixes.
