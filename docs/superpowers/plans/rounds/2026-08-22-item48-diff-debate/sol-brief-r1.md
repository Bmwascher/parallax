# Diff debate, round 1 — item 48 PowerShell 7 feasibility

You are one of two equal-weight advisors. I am the other. We verify and
refute each other's claims. Neither of us is the gate; the debate is. End
your reply with **PASS**, **FIX**, or **ESCALATE**.

Working directory is the repo. You have read-only access to all of it.

## What this branch is

Backlog item 48 asked: **can this repo stop supporting Windows PowerShell
5.1 and run only on PowerShell 7?**

The deliverable is an **investigation, not a migration.** Nothing was
migrated. The branch produces a mechanical entry-point survey with a gate
script, five measurements, and a verdict adjudicated against four
pre-committed NO-criteria by five mechanical rules. The verdict is
CONDITIONAL on five named conditions.

## The frozen plan

`docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md`

Frozen after a 7-round panel debate — 28 accepted findings, 3 refuted —
whose record is the appendix at the end of that file. **Verification
status: FULL.** You were one of the two reviewer lanes in that debate
(session `01a028cf-92f6-73b0-b0d9-0d3c5f8ae056`); this is a fresh session
and you should not assume you remember it.

The implementer made **zero judgment calls by design.** Any drift from the
frozen plan is a finding.

## Range

**Base** `a3134dc` (`git merge-base main HEAD`) — **Head** `1bcf912`.
39 commits, 58 files, 10335 insertions.

**Do not try to read the raw diff.** It is roughly 700 KB, and
`git diff --name-status a3134dc..1bcf912` returns only `A` lines — zero
`M`, zero `D`. Every path is new, so the diff and the files are the same
thing. Read the files.

Risk is concentrated almost entirely in one file:
`docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md`
(~2350 lines). Its `## Verdict` section is the part that matters most.

Supporting artifacts in the same directory: `survey.py` (the completeness
gate, ~310 lines), `entry-points.tsv` (1116 classified rows), `reexec/`
(Measurement 1's probe and its `results.json`), `missing-pwsh/` (Measurement
4's probe and its `results.json`).

## The standard

This repo has one recurring defect class, and this investigation exists to
measure it: **a claim stated more widely than its evidence**, and its
relative, **an unmade measurement that reads like a clean one.**

**The branch reproduced that class inside its own work seven times.** Every
one was caught by a reviewer, none by the author, and five of the seven were
inside a fix for the previous one. In order:

1. The verdict certified a Rule 4 residual sweep it had not performed.
2. The rewritten certification was still wrong — four residuals walked
   nowhere.
3. Growing the condition list from four to five updated the count in two of
   three places, and left the ordered-work list with no step for the new
   condition.
4. A fix for a stale published number left a second number beside it stale.
5. A correction that refuted a uniqueness claim in one section left the
   refuted claim standing in three others, so the record asserted and
   refuted the same thing.
6. Fixes moved the record's own line numbers, and five citations INTO this
   record went stale — four of them introduced by the fix that moved them.
7. The convention paragraph written to end (6) said the record cites itself
   "never by line number", while five such citations survived in a spelling
   neither sweep had counted.

The root cause of (4) and (6) is now understood and stated in the record:
**this document quotes its own line counts and classification counts, so
every edit to it moves the numbers the edit is describing.** The structural
fix was to convert self-citations to section anchors and write the rule
into the record.

**Sweep the class. Name an eighth instance, or report none explicitly.** Do
not report "no issues" without saying what you swept for.

## The required whole-branch review, and my adjudications

`docs/superpowers/plans/rounds/2026-08-22-item48-diff-debate/fable-whole-branch-review.md`

A second reviewer seat (Claude-side, read-only) reviewed the whole branch
across four exchanges. Its replies are verbatim in that artifact. It returned
FIX three times and PASS on the fourth. Findings 5, 6 and 7 above are its.

**I adjudicated every finding by reproducing it myself before accepting it.**
All were ACCEPTED; none refuted, none escalated. For finding 5 I ran
`grep -n 'FAILS rather than skips\|strongest'` and read each site in
context. For finding 6 I read the cited targets and the actual targets. For
finding 7 I read all five surviving citations and confirmed record lines 4
and 5 are what they claim.

**Two things about that artifact you should weigh rather than accept:**

- Its terminal PASS is bound to head `bfb018f`. The head is now `1bcf912`
  because retaining the review artifact itself moved it. That single commit
  adds only the artifact and touches nothing the review examined — but the
  PASS does not formally cover the head you are reviewing, and I would
  rather tell you than let you find it.
- Its seat cannot execute. Every round states its own UNVERIFIED list, which
  is the honest form, but it means the gate outputs it cites are my
  measurements, not its own.

## My position, with its evidence

Each claim below is something I checked myself this session. Refute any of
them.

**Spec fidelity holds.** `git diff --name-status a3134dc..1bcf912` is 58
`A` lines, zero `M`, zero `D`. The plan's central Global Constraint —
NOTHING IS REPINNED — therefore holds at the branch level absolutely, not
merely per task. No file under `tools/`, `evals/`, `skills/`, `agents/`,
`hooks/`, `.githooks/` or `.github/` was touched, so no 5.1 test was
deleted, skipped or xfailed anywhere in the range.

**The gates are green.** `python <REC>/survey.py` exits 0, printing
`7484 hits, 7484 classified, 0 unclassified, 0 stale, 0 files not scanned`.
The record has 11 `## ` headings and zero `NOT YET WRITTEN` hits. Both
PowerShell hosts' full suites were green at the Task 9 head: 2558 passed /
14 skipped under Windows PowerShell 5.1 and the same counts under
PowerShell 7. **Nothing after that commit touched executable code outside
`<REC>/survey.py`**, whose only change was to widen an exemption tuple.

**The record's two published re-runnable commands reproduce.** I ran both.
The classification command prints 611/227/106/54/46/31/15/13/7/5/1 summing
to 1116, matching the published table. The verdict's residual-bucket `awk`
prints 8/5/3/4/4/6/4 summing to 34, matching its published table.

**The verdict's chain is sound as far as I can check it.** Four criteria
(one NOT MET, three UNKNOWN), five rules, five conditions, each condition
tracing to a named gap.

## What I want from you

**Spec fidelity is the primary lens.** Does each of the nine tasks deliver
what its plan task specifies? Where the controller ruled against plan text
— fourteen rulings, one withdrawn as wrong, all listed in
`.superpowers/sdd/2026-08-22-item48-pwsh7-feasibility/deferred-minors.md`
with their stated reasons and costs — was each ruling justified?

Beyond that, four things I specifically want tested rather than read:

1. **`survey.py` gates the whole inventory's completeness claim.** Read it
   for what it cannot see. Its executable-file guard was widened twice this
   cycle, the second time because the first widening's comment still claimed
   more than the code enforced. Check the current version does not.
2. **Measurement 4 did NOT reproduce the condition it set out to test** —
   Windows resolved a bare `pwsh` against the parent's environment. The plan
   pre-named that outcome and required "say so and stop". Check it never
   reads as clean, and check the verdict does not quietly treat the
   criterion as satisfied.
3. **Spot-check `path:line` citations.** Two prior reviewers checked about
   68 between them and found one wrong — a line number about to propagate
   into the live backlog. Report how many you checked and how many landed.
4. **The verdict is CONDITIONAL and three independent parties derived it.**
   Challenge the reasoning if it is wrong. Do not treat CONDITIONAL itself
   as a defect.

## Settled — do not re-litigate

- The branch deliberately does not edit
  `docs/superpowers/plans/2026-07-27-0150-backlog.md`. That edit happens at
  merge. A stale heading there is known, and two wrong copies of a line
  number in `CLAUDE.md` and that backlog file are known and filed for merge.
- Do not re-run the pytest suites. They take about 20 minutes per host.

Answer with findings, each carrying its evidence, and end with PASS, FIX or
ESCALATE.
