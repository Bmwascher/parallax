# Mode diff, round 1 - items 32 and 33, detached dispatch

You are the cross-vendor reviewer. This is a MODE DIFF debate: the
implementation is done and you are checking it against its frozen plan and
against the repo, not designing anything.

You are reading a REVIEW MIRROR: a file copy of the working tree, its own
`.git` preserved. Every path below resolves inside it. Ground every claim
in a `path:line` you actually opened here.

## The range

- base `8af6ae0456b275e1f8a700bc479cbc19af69c6e8` (main)
- head `6949ee89b71f037f7d4b0c5206a96088c4049c06`
- 48 commits, 104 files.

`git diff 8af6ae0..6949ee8` runs in this mirror. The code lives under
`tools/`, `evals/`, `skills/`, `.github/`; the rest is docs.

## What it does

Backlog items 32 and 33.

**32.** A review round dispatched in the FOREGROUND is killed at the
caller's 600-second tool ceiling. The client never writes its reply file,
so the round is a transport failure rather than a review result, and the
reviewer quota is spent for nothing. The rule lived in `CLAUDE.md` and NOT
in the skill, so a session following the skill exactly lost the round.

**33.** The preflight asked the user whether to build a review mirror. The
answer has never once differed.

Now all five long client calls the skill documents launch and poll through
ONE shipped tool, `tools/dispatch-detached.ps1`: two codex calls in
`skills/multi-model-verify/SKILL.md`, three kimi calls in
`skills/multi-model-verify/references/backup-lane.md`. The mirror is built
without asking.

## The frozen plan and the spec

- Plan: `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md`,
  FROZEN at `28802bd` after 23 cross-vendor dispatches and 6 Fable-lane
  rounds. Its `## Debate record` appendix states that debate's own floor.
  Read it: it tells you what the plan deliberately did NOT close.
- Spec: `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`,
  reconciled by Task 9.
- Build ledger: `docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/build-ledger.md`.
  Per-task commit, whose evidence verified it, and every deviation.

**Verification status of the frozen plan is FULL.** This is not a degraded
plan, so the poisoning rule does not apply.

## The required whole-branch review, and my adjudications

`parallax:fable-reviewer` reviewed this range before this round, as the
flow requires. Its raw reply is retained at
`docs/superpowers/plans/rounds/2026-08-30-item32-diff-debate/fable-whole-branch-review.md`.
It found NO critical issue. It raised three important findings. I
reproduced all three before accepting them, and all three were real:

1. **CI never ran the branch's core modules.** The `powershell-hosts` job
   carries a hardcoded per-host module list; the two new Windows-only
   modules were on neither list, and they self-skip on Linux, so after
   merge no CI job would have run the dispatch tool's suite on any host.
   ACCEPTED and fixed: both modules are now in both lists
   (`.github/workflows/skill-evals.yml`).
2. **A corrupted root `AGENTS.md` was about to ship.** ACCEPTED. I closed
   the attribution gap the reviewer could not: it entered in the branch's
   FIRST commit `fb3e2bb`, swept in by a `git add`, untracked before the
   branch and authored for nothing. It is a mechanical rebrand of
   `CLAUDE.md` saying "Codex plugin" with two commands that do not exist.
   Untracked with `git rm --cached`, restoring the pre-branch state; the
   file is left on the user's disk.
3. **My own eval reaper killed by pid alone**, violating the invariant
   this branch pins. ACCEPTED and fixed: it now compares pid PLUS
   `startticks` and treats unknown as NOT ours.

Its four minors are NOT fixed and are live questions for you, listed under
"open questions" below.

## Deviations from the frozen plan - judge each, do not assume I was right

1. **Task 1's launch is NOT the plan's literal `Start-Process`.** It is
   `CreateProcess` through inline `Add-Type` C# with a
   `PROC_THREAD_ATTRIBUTE_HANDLE_LIST` allowlist. Reason, which I
   reproduced independently of the implementer: `Start-Process` with
   `-RedirectStandardOutput/-RedirectStandardError` makes .NET request
   `bInheritHandles=TRUE`, which is process-wide, so the grandchild
   inherits the CALLER's pipe and the caller blocks until the grandchild
   exits. Measured against a 12-second sleeper: piped caller `12.418s`,
   caller redirected to a file `0.215s`. A tool call is the piped shape,
   so the frozen mechanism reintroduces the very blocking this tool
   exists to remove, and two of the task's own required tests cannot pass
   against it.
2. **All five wrapper bodies use `/` where the plan wrote `\`.** Two
   repo-wide gates forbid a backslash anywhere in `SKILL.md` and
   `references/backup-lane.md`. A subagent had instead NARROWED one gate
   and left the second red; I reverted that and restored both gates whole.
   The plan-mandated oracle literal moved with the file.
3. **`test_agents_md_backchannel_check`'s needle moved** from the deleted
   `STOP and surface` to `BUILD THE MIRROR AND REPORT`. Task 6's own
   frozen test asserts the old phrase is ABSENT, so the plan mandated two
   tests that contradicted each other.
4. **`BODY_TOKEN_BUDGET` was raised 5250 to 6250** alongside the
   authorized `BODY_TOKEN_CEILING` raise. Only the ceiling raise was
   asked for. Strict lint exits 0 on a warning, so the budget raise
   changed no gate outcome; it widened the early-warning line unasked.
5. **`prompt_bytes_match` is pinned FALSE**, as measured, on both hosts.

## Gates, session-run rather than reported

- Full pytest, Windows PowerShell 5.1: 2680 passed, 14 skipped.
- Full pytest, PowerShell 7: 2679 passed, 15 skipped.
- `skill_lint --strict`, `skill_scanner`, `check_exact_line_oracles`,
  `run_trigger_evals`: all exit 0.
- Behavioural evals: `diff-mode-spec-fidelity` missed expectation 2 in 2
  of 3 runs on this branch and passed in 1 run on the installed 0.27.0
  cache. The ledger states why that comparison is CONFOUNDED - the arms
  differ in plugin content AND load mechanism at once - and does not
  claim a cause.

Note: the gate counts above predate the three whole-branch fixes. The
suite has not been re-run since them; say so if you think that blocks a
verdict.

## What I want from you

1. **The central question.** Does anything on this range let a killed,
   hung or unfinished round read as a COMPLETED one? That is the class the
   whole plan exists to close, and rounds 1 to 4 and 6 to 9 of the plan
   debate each found a hole in it. Treat the class as open. Name an
   instance or say explicitly that you searched and found none, naming
   what you searched for.

2. **Judge the five deviations.** Any of them that weakens something real
   is a finding. I am most interested in whether deviation 1 is the right
   call or whether it trades one hazard for a worse one, and whether
   deviation 4 should be reverted.

3. **The four open minors from the whole-branch review**, which I have
   NOT fixed. Confirm or refute each, and say which if any must be fixed
   before merge rather than filed:
   - a `GetProcessTimes` failure throws AFTER the child exists and
     discards the pid, so the catch's kill does not run, against the
     pinned sentence that a failure after start kills the tree;
   - an unknown parameter fails in the host's `-File` binder before the
     script's own checks, so the exit-2 promise does not hold there;
   - the budget-raise comment is stale on arrival (body measured 6225
     when the budget was set to 6250, and 6356 after Task 6, so it warns
     again) - the self-quoting-count class;
   - the reaper's grace-period probe was a substring match. I replaced it
     with a tick comparison; check I did not introduce something worse.

4. **Sweep the CLASS of anything you find** and either name another
   instance or state that you searched and found none, naming the shapes
   you searched for. Two independent sweeps agreeing is not coverage if
   both drew the class too narrowly.

5. Spec fidelity: the implementer makes zero judgment calls, so any drift
   from the frozen plan beyond the five deviations above is a finding.

End with PASS, FIX, or ESCALATE.
