Round 4. Rules, verdict grammar and boundaries as before.

Your round 3: FIX on the em-dash count, FIX on (a), FIX on the missing
vendored-linter obligation, PASS on (c). All three amendments accepted and
incorporated. Two I verified myself:

- **15, not 14.** The brief holds 45 non-ASCII bytes and a character count
  confirms exactly 15 em dashes and nothing else. My 14 came from reading
  merged diff opcodes as one span each; two adjacent dashes sat inside a
  single opcode. The transport record says 15.
- **The vendored claim really does go false.** `skill_lint.py:3-6` says
  "unmodified except this provenance header" and "Re-diff against upstream
  before editing locally", and `skill_lint.py:12-26` documents the token
  budget as a warning and exit 0 as warnings-allowed. Adding a hard ceiling
  falsifies three separate statements in that file's own header. I had not
  looked at the header at all. Accepted with your six obligations.

Amendment (c) is predeclared: if the honest post-relocation body exceeds
5000, the soft threshold is reset to the smallest declared value clearing
the measured body, 5250 stays the hard ceiling, the three outcomes are
mutually exclusive as you specified, and soft / soft+1 / 5250 / 5251 are
pinned. The encoding correction and the final measurement are recorded
beside the constant so the raise reads as a baseline reset.

## The decision rule you flagged as UNVERIFIED, now written

Predeclared, before any run, and not reinterpretable afterwards.

**A RUN** is one `run_behavioral_evals.py --case plan-mode-debate-runs`
invocation. It PASSES only when all four expectations are met. Every run's
per-expectation verdicts are retained as artifacts.

**Aggregate bands.**
- 10 or more of 12 pass: the case is repaired; item 18 closes; no
  expectation text changes.
- 6 to 9 pass: the fix helped and the case is still unreliable; item 18
  does NOT close; the per-expectation tally is recorded and the item stays
  open carrying it.
- 5 or fewer pass: the fix did not repair the case; item 18 does not close.

**One overriding per-expectation rule.** Expectation 1 must fail ZERO times
in 12. A single expectation-1 failure means the rendering change did not
deliver observability, and that is a failure of the fix regardless of where
the aggregate lands. This is the rule that actually tests what we built;
the bands only describe what remains.

**Discards.** A run whose executor exits non-zero, or whose grader auth or
route check fails, measured NO expectation and is discarded and re-run. Each
discard is recorded by name and count. Discards are not failures and are
not passes.

## One thing I want to change about the sample, with my reason

You said twelve UNCHANGED-tree runs. I think the sample is better spent on
the FIXED tree, and I want your verdict rather than my quietly redirecting
it.

The unchanged-tree rate is already measured across THIRTEEN runs on record:
2 of 6 on the unchanged tree and 1 of 7 on the 0.20.0 branch, at
`execution-deviations.md:848-857`, which the same record concludes are not
meaningfully different. Twelve more unchanged-tree runs would re-measure a
quantity we already have at n=13.

What is unmeasured is whether the rendering fix makes expectation 1
observable in a real run, and no amount of unchanged-tree data answers
that. So I propose all twelve on the fixed tree, with the existing 3-of-13
as the historical control rather than re-running one.

The obvious objection is that a fixed-tree-only sample cannot separate "the
fix worked" from "the executor happened to behave differently today", since
the control is historical rather than concurrent. I think the
per-expectation rule above absorbs that: expectation 1 failing for
truncation is a mechanical, diagnosable event, not a coin flip, and zero
occurrences in twelve is a direct observation of the mechanism being gone.
Tell me if that reasoning is too generous to my own fix.

If you disagree, say the split you want — for instance six and six — and I
will take it.

## Nothing else is open from my side

The plan as now specified is four items:

1. **Item 19** — relocate lines 109-125, the checkpoint-binding explanation
   and the resume rationale; then measure; then thresholds per (c) with the
   four boundary pins; plus your six vendored-linter obligations.
2. **Item 18** — the 2400 name-based cap for `Bash` and `PowerShell` with
   your five tests including a fail-first long-input case; then the twelve
   runs under the rule above.
3. **Item 9** — both generators execute; route grammar frozen before any
   case is generated; one source-level mutant killed per recorded defence,
   with the failing output retained; `Get-SkillReport` plus
   `Hide-KnownContainer` driven through `run_functions`.
4. **UTF-8 brief transport** — your six acceptance criteria, replacing the
   pin at `test_multi_model_verify.py:460-487` rather than supplementing
   it, with the `???` case watched to fail on Windows PowerShell 5.1 first.

<final-check>
List anything you could not verify, as UNVERIFIED. If the sample question
is the only thing left, answer it and say whether the plan is terminal
with your answer applied.
</final-check>
