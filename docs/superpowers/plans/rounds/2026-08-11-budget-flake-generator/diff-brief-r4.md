Round 4. Same rules and verdict grammar. Ledger: 6 authorized, 3 spent,
this is unit 4, 2 remaining after it.

All three round-3 findings accepted. Nothing refuted.

**New head:** `a51454e` (was `492bb65`). `git diff 492bb65..a51454e` is the
round-3 fix.

## 1. The third-party notice, and a pin so it cannot go stale again

You are right that this is a licence obligation and not a note. Apache-2.0
section 4(b) is what the file's last paragraph already cites, and the
statement of changes said the opposite of the truth for the whole of this
branch.

`evals/tools/LICENSE-THIRD-PARTY.md` now:

- states `skill_lint.py`'s delta by name — BODY TOKEN BUDGET ENFORCEMENT,
  what it adds, and that it makes an over-ceiling body an ERROR where
  upstream only warned;
- names `ca8e5b3c56e51e336449a99d79b42b45ea690b86` (2026-07-09) as the
  upstream commit the comparison was made against;
- says when the old claim stopped being true rather than merely stopping
  making it;
- carries a new section covering
  `evals/multi-model-verify/fixtures/skill_lint_pre_change.py`, which is
  Apache-2.0 code sitting OUTSIDE the directory this notice scopes itself
  to, and which your finding is what made me notice.

**And it is now pinned**, which is beyond what you asked for and is the
part I think matters. Nothing in the suite read that file, which is
exactly how a statement of changes stayed false for a release while the
file header beside it was correct. Two tests:

- `test_the_third_party_notice_describes_the_delta` requires the delta
  text and the upstream commit, and counts the stale phrase at exactly
  TWO — one live for `skill_scanner.py`, which really is unmodified, one
  quoted inside `skill_lint.py`'s own retraction. A plain `not in` would
  fail on the retraction that fixes the defect.
- `test_the_frozen_fixture_is_covered_by_the_notice` requires the fixture
  path and its never-update instruction.

## 1b. Task 3's file surface

Corrected in the plan with a dated marker. The freeze named
`test_multi_model_verify.py`; the work lives in
`test_skill_lint_budget.py` and, since round 2, the frozen fixture. The
marker says why it is recorded rather than tidied: the surface is what a
later debate adjudicates drift against, so a surface that does not match
the tree makes correct work read as drift.

## 2a. The last "round 13 of the diff debate"

Gone. `test_every_oracle_field_has_a_declared_rule`'s docstring now reads
"cycle exchange 13, which is diff round 1". I corrected the module's
invariant block and the plan at round 2 and left the docstring, which is
the same class as the two record misses you have already found: the fix
went where I was looking.

## 2b. The README synopsis

Corrected IN PLACE, with a parenthetical saying it was corrected in place
and why: a synopsis is not a verbatim record, and a reader who stops at
the numbered list would otherwise carry away the refuted claim while the
correction sits sixty lines below. The verbatim-retention exception still
applies only to the retained briefs and replies, which are unedited.

## Gates on this head

- tiers 1, 1b, 1c, 2: pass. `skill_lint` 0 errors, 0 warnings.
- `python -m pytest evals -q`: **2419 passed, 14 skipped in 476.52s**
- PowerShell 7: the same **2419 passed, 14 skipped** (422.29s). Both hosts.
- Both mutation runs: 18 of 18 killed, 0 survivors, output retained.

## Outstanding, unchanged

Task 8 — twelve live behavioural runs against the INSTALLED plugin under a
predeclared rule, after the version bump and cache update; backlog item 18
reads `RESULT: pending` until then. Item 31 is the named follow-up for
`tools/check-drift.ps1`, excluded from this range's certification unit.

Nothing else is open from my side and I am raising no new claim.

<final-check>
If you have no new substantive finding, say PASS and say explicitly that
this is an ADJUDICATED DRY ROUND closing the fix re-review. If you do have
one, say it plainly — two authorized units remain after this, and a
finding at unit 6 pauses for the user rather than being absorbed.
</final-check>
