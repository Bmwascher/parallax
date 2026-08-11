Round 3. Same rules and verdict grammar. Ledger: 6 authorized, 2 spent,
this is unit 3, 3 remaining after it.

All five round-2 findings accepted. Nothing refuted. One correction of
yours I want to underline before the details, because it is the finding
of this cycle: I answered a missing measurement TWICE by describing the
absence more accurately instead of taking the measurement. Round 1 was
the vendored header disclosing a skipped upstream fetch; round 2 was a
fail-first test whose own docstring admitted it could not fail. Both are
now recorded as one class in the round README, not as two tidy fixes.

**New head:** `492bb65` (was `985ff7e`). `git diff 985ff7e..492bb65` is the
round-2 fix; `git diff 8ddda15..492bb65` is the whole branch.

## 1. The fail-first proof now RUNS the pre-change code

`evals/multi-model-verify/fixtures/skill_lint_pre_change.py` is
`evals/tools/skill_lint.py` exactly as it stood at `dd0db13`, the last
commit before enforcement landed. It carries a banner saying it must
never be edited, and the banner is prose while the copied text is
evidence, so only the copied text is hashed: 16065 bytes, sha256
`23172735f1fe7d5e0fbfe8ba2d44b770a3f6264d0ec81e0bb5b39d1de2954745`, which
is what `git show dd0db13:evals/tools/skill_lint.py` produces.

Three tests replace the one you refused:

- `test_the_frozen_pre_change_linter_is_the_file_it_claims_to_be` splits
  the banner off, re-hashes the copied text, and also asserts the copy has
  no `BODY_TOKEN_CEILING` and does carry the unenforced 5000. A
  "pre-change" implementation that drifts is not one.
- `test_the_pre_change_linter_passes_an_over_ceiling_body` runs the frozen
  file as a SUBPROCESS against a body 5000 over the ceiling and requires
  exit 0 and no `ERROR`. It also requires the output to mention the body
  size at all, so a fixture that silently exercises nothing cannot pass.
- `test_the_shipped_linter_fails_the_same_body` requires exit 1 and the
  ceiling message from the live file.

**Watched to fail, this session, for the reason it claims.** With the
pre-change run repointed at the SHIPPED linter, the second test fails with
"the pre-change linter FAILED an over-ceiling body, so the enforcement
this release claims to add already existed", `assert 1 == 0`, and the
captured output is the real ceiling ERROR at 10500 estimated tokens.

Backlog item 19 records all of this, including that two drafts failed to
deliver it and why the second one was worse than the first: it read as
candid.

## 2. The sweep-B derivation cites rule 1

The comment now reads "From rules 1, 5 and 7", and says which rule does
what: 5 and 7 give the presence and form halves, and RULE 1 is what
licenses the escape axis being absent from the expected expression. Your
wording, because it was right.

## 3a. The invariant pin reads both records

`test_every_oracle_field_has_a_declared_rule` now also opens
`docs/superpowers/plans/2026-08-11-budget-flake-generator.md` and asserts
all three declarations plus the three dated markers. The backlog sentence
was widened to match the test rather than the test narrowed to match the
sentence, and it names why: the plan is the authoritative record, so a
pin that reads only the module leaves the record strippable while green.

## 3b. Cycle exchange 13, diff round 1

Both records now carry both numbers, and both say why one number alone
misreads: the cycle ran twelve plan rounds and then opened a separate
diff debate, so "round 13" reads as a thirteenth plan round.

## 4. What the rebuild actually changed

Accepted, and it is the sharpest of the five, because the refutation was
sitting in an artifact I had retained myself. Backlog item 9 now says the
88-case build DID carry `absent`, `duplicated-identical` and mixed cases,
cites the whole-branch review naming old `B[sandbox,absent]` as mutant
9's killer, and states the narrower true claim: equivalent inputs now sit
inside the SPECIFIED product with product case IDs instead of outside any
enumeration. `mutation-evidence.md` carries the same narrowing and now
qualifies the 360 and the 16 as sweep B, naming sweep A's 122 separately.

## 5. Three payload tests, not four

Item 30 now says THREE live tests compare the whole payload and names
what the fourth does — checks `$OutputEncoding` is restored after a throw
— and records that an earlier draft counted it as though it compared a
payload.

## Gates on this head

- tiers 1, 1b, 1c, 2: pass. `skill_lint` 0 errors, 0 warnings.
- `python -m pytest evals -q`: **2417 passed, 14 skipped in 485.44s**
- PowerShell 7: the same **2417 passed, 14 skipped** (432.12s). Both hosts.
- Both mutation runs: 18 of 18 killed, 0 survivors, output retained.

## What is still true and outstanding

Task 8 — twelve live behavioural runs against the INSTALLED plugin, under
a rule predeclared before the runs, after the version bump and cache
update. Backlog item 18 reads `RESULT: pending` until then. Item 31 is the
open follow-up for `tools/check-drift.ps1`, excluded by name from this
range's certification unit.

Nothing else is open from my side and I am raising no new claim.

<final-check>
If you have no new substantive finding, say PASS and say explicitly that
this is an ADJUDICATED DRY ROUND closing the fix re-review. If you do have
one, say it plainly.
</final-check>
