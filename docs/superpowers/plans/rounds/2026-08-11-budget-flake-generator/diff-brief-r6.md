Round 6. **The USER extended the budget by up to three rounds and asked
that the debate run until it goes dry rather than stop at a number.** New
ledger: 8 authorized, 5 spent, this is unit 6, 2 remaining. The round cap
is reset for those three.

I put four options to them, including merging on ESCALATE with recorded
risk acceptance, and told them plainly that the findings were shrinking
each round and that nothing since round 2 had been about code behaviour.
They chose to keep going. So do not soften anything on grounds of cost.

Both round-5 findings accepted. Nothing refuted.

**New head:** `f571cf7` (was `3f74843`). The fix range touches five files:
three fix targets — `evals/tools/LICENSE-THIRD-PARTY.md`,
`evals/multi-model-verify/test_skill_lint_budget.py` and the round
README — plus two retained round-5 artifacts. I am counting them that way
because your second finding was that I miscounted exactly this.

## 1. Prose is free, the separators are not

You were right, and the shape of it is worth naming: round 4's fix
CREATED this. Narrowing "its content is hash-pinned" overshot into
"banner edits do not break any pin", so one paragraph was wrong in both
directions in consecutive drafts. A fix is new code and gets no discount,
and this is that rule landing in a record file rather than a function.

`LICENSE-THIRD-PARTY.md` now says:

- banner PROSE is excluded from the hash and can be reworded freely;
- the banner's two 75-dash SEPARATOR LINES are not prose — the same test
  splits on them and requires exactly three parts, so editing either
  fails a structural assertion even though it changes no hash;
- and it records both earlier drafts and which direction each was wrong
  in, rather than quietly presenting the third attempt as the first.

`test_the_frozen_pre_change_linter_is_the_file_it_claims_to_be`'s
docstring now says it makes TWO assertions covering different things: a
structural one on the separators and a SHA-256 one on the text below
them. `test_the_frozen_fixture_is_covered_by_the_notice` requires the
separator sentence, so the notice cannot drift back in either direction.

## 2. The file count

Corrected in the round README, not in the brief. `diff-brief-r5.md` is
retained verbatim and still says three files; the same treatment
`diff-brief-r2.md` got for its two overstatements. The README says which
briefs still carry which uncorrected claims.

## Gates on this head

- tiers 1, 1b, 1c: pass. `skill_lint` 0 errors, 0 warnings.
- `python -m pytest evals -q`: **2419 passed, 14 skipped in 481.74s**
- PowerShell 7: the same **2419 passed, 14 skipped** (426.05s). Both hosts.
- Count unchanged at 2419: two assertions tightened, one added and one
  replaced inside an existing test.
- Both mutation runs: 18 of 18 killed, 0 survivors, output retained.

## Where I think the remaining risk actually is

Five rounds have found seventeen things and almost all of them were
records rather than behaviour. That pattern could mean the code is sound,
or it could mean we have both been reading the records because the records
are what changed most. If you want to spend one of the two remaining units
somewhere other than the record surface, the places I would point you at
are the ones I built and cannot audit neutrally:

- `sweep_b` and `render_field` in `test_route_parser_shapes.py`, where an
  expected value that happens to match production would look exactly like
  a derived one;
- the FAIL_OPEN fault model in `test_skill_report_shapes.py`, which is the
  only place a test deliberately breaks a production guard;
- `evals/tools/run_behavioral_evals.py`'s cap change, which is the one
  runtime behaviour change on this branch that no generated suite covers.

That is a suggestion, not a request to narrow your scope.

## Outstanding, unchanged

Task 8 — twelve live behavioural runs against the INSTALLED plugin under a
predeclared rule, after the version bump and cache update; item 18 reads
`RESULT: pending`. Item 31 is the named follow-up for
`tools/check-drift.ps1`, excluded by name from this range's certification
unit.

<final-check>
If you have no new substantive finding, say PASS and say explicitly that
this is an ADJUDICATED DRY ROUND closing the fix re-review. If you do have
one, say it plainly — two authorized units remain after this.
</final-check>
