Round 5. Rules, verdict grammar and boundaries as before.

Your round 4 answered the sample question and issued a conditional terminal
PASS. All three sampling amendments accepted verbatim. I am NOT treating
round 4 as terminal, and the reason is this repo's own rule, which 0.22.0
shipped three commits ago:

> Converged with amendments ... THIS IS AGREEMENT, NOT TERMINATION. The
> amendments still have to be APPLIED, and the debate still ends the way
> the termination rule below says it ends: on an adjudicated dry round. A
> round that produces accepted fixes is a round that produced new
> substantive findings, so it is not that round.

`skills/multi-model-verify/references/debate-protocol.md:47-55`. Round 4
produced three accepted fixes, so it is not the dry round. This round is
the request for one.

## The three amendments, as applied

1. **"Fixed tree" is the INSTALLED plugin.** All twelve runs go through the
   installed cache, not `--head`. `run_behavioral_evals.py:21-24` says an
   un-updated cache behaviourally tests the stale copy, and `:772-775` says
   `--head` shadowing is unverified and the pre-merge run should use the
   installed cache. Both verified. Sequence: finish the branch, bump,
   `claude plugin update parallax@parallax`, record the branch SHA and the
   installed version, then all twelve against that one installation.

2. **The discard rule is narrowed, and no longer blanket.**
   - executor timeout or nonzero exit: a FAILED run, counted. The runner
     deliberately classifies it that way at `:482-486` so a partial
     transcript from a crash cannot be graded into success.
   - grader auth, grader process, or grader route failure: NO expectation
     was measured; record and replace.
   - missing or malformed grader verdict array: same, record and replace.
   - **Replacement cap: 6.** Declared now, before any run. Beyond six
     replacements the sample STOPS as blocked and the block is reported,
     rather than quietly spending more live calls until the numbers look
     answerable.

3. **The aggregate claims only post-fix performance.** Bands renamed to
   "the post-fix case met / remains unreliable / failed its repair gate".
   No causal claim is made from a fixed-only sample. At 10-12, item 18
   closes ONLY if expectation 1 failed zero times AND every remaining
   failure is grounded in real agent noncompliance rather than missing,
   truncated, elided or unbound harness evidence. Any harness-caused miss
   leaves item 18 open.

I also accept your correction that 3-of-13 is not a control. It is two
historical arms whose failure modes the record found identical, and it will
be described that way and never as a baseline.

## A process deviation of mine, declared late rather than left unsaid

`debate-protocol.md:80-89` requires a TOTAL FIX-VERIFY BUDGET, caller-set
and declared BEFORE round 1, where one unit is one dispatched exchange. I
did not declare one. That is my miss, in the branch whose predecessor wrote
the rule.

Declaring it now, with the deviation on the record: **budget 8 dispatched
exchanges.** Five are spent — the void encoding round counts, because the
rule counts every round sent to a reviewer including one that returns
nothing usable. Three remain before the debate pauses for the user.

## What I am asking for

Nothing new is open from my side. The plan is the four items and the
sampling rules exactly as amended above.

<final-check>
If you have no new substantive finding, say PASS and say explicitly that it
is an ADJUDICATED DRY ROUND — no new finding and no outstanding contested
point — for the four-item plan as amended. If you do have one, say it
plainly; a fifth round finding something real is a better outcome than a
polite dry one.
</final-check>
