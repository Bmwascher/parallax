Round 7. Ledger: 8 authorized, 6 spent, this is unit 7, 1 remaining.

Both round-6 findings accepted. Nothing refuted.

**New head:** `6205a06` (was `f571cf7`). The fix touches five files: two
substantive targets — the frozen plan and
`evals/multi-model-verify/test_route_parser_shapes.py` — the round README,
and the two retained round-6 artifacts. I am enumerating rather than
totalling, for the reason round 4 gave and round 6 caught me ignoring.

## 1. The third degenerate crossing is in the record

You were right that two readings were in the authoritative plan and the
third was only in the code, and right that the unrecorded one went the
opposite way from `absent`.

The plan now carries it beside the other two, and states why they differ
rather than asserting that they do:

> With the key ABSENT there is no line at all, so there is no position an
> escape could occupy and no rendering to vary; the duplication is
> forced. With a valueless FORM the line exists and the value position
> exists, it is merely empty, so an escape can genuinely be placed there.

It also says plainly that either reading is defensible and that what was
not defensible was deciding one of them in `render_field` and the other
two in the plan.

`render_field`'s docstring names it as the third crossing, points at the
plan for the reasoning, and says not to change one of the three readings
without changing the record.

I did NOT change the construction. Your finding was that the decision was
unrecorded, not that it was wrong, and switching to duplicate cells now
would trade a recorded reading for an unrecorded change in coverage.

## 2. The total I put back three rounds after removing one

Accepted without qualification. Round 4 took a total out of the README
because totals go stale; the brief I wrote two rounds later opened with a
new one, and it was wrong. The README's enumeration stands at eighteen
across six rounds and it is enumerated, not summed.

I also added an index to the README naming WHICH retained briefs still
carry claims later rounds refuted, since briefs are verbatim and never
edited: `diff-brief-r2.md` on the mutant cells and on rules 5 and 7 alone,
`diff-brief-r5.md` on the file count, `diff-brief-r6.md` on seventeen. A
reader who opens a brief needs to be told where the corrections live.

## What you cleared, and what I take from it

You spent round 6 where I asked and reported no substantive defect in the
FAIL_OPEN fault model or the behavioural cap change, citing the lines you
checked in each. I am recording that as a cleared area rather than as
silence, because you named the specific assertions rather than saying
nothing was found.

That leaves the generator you did find something in as the only
implementation-sensitive area where a finding has landed this debate, and
it was a specification gap rather than a wrong answer.

## Gates on this head

- tiers 1, 1b, 1c: pass. `skill_lint` 0 errors, 0 warnings.
- `python -m pytest evals -q`: **2419 passed, 14 skipped in 479.38s**
- PowerShell 7: the same **2419 passed, 14 skipped** (428.34s). Both hosts.
- Count unchanged at 2419: round 6's fix is a specification record and a
  docstring; no case, expected value or assertion moved.
- Both mutation runs: 18 of 18 killed, 0 survivors, output retained.

## Outstanding

Task 8 — twelve live behavioural runs against the INSTALLED plugin under a
rule predeclared before the runs, after the version bump and cache update;
backlog item 18 reads `RESULT: pending` until then. Item 31 is the named
follow-up for `tools/check-drift.ps1`, excluded by name from this range's
certification unit, which is the documented multi-model-verify dispatch
contract in `skills/multi-model-verify/`.

Nothing is open from my side. I am raising no new claim.

<final-check>
If you have no new substantive finding, say PASS and say explicitly that
this is an ADJUDICATED DRY ROUND closing the fix re-review. If you do have
one, say it plainly — ONE authorized unit remains after this, and the user
has already extended once and asked that the debate run until it goes dry
rather than stop at a number.
</final-check>
