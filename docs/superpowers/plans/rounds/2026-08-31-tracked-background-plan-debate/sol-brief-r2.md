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
