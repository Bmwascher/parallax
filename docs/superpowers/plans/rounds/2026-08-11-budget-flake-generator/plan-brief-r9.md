Round 9. Rules and verdict grammar as before. Ledger: 10 authorized, 9
spent, this is unit 10, 0 remaining after it. Any further round pauses for
the user.

## Your round 8, accepted in full and built

**Q1 FIX accepted.** You were right that "assert the shadow and what casts
it" locks today's topology while proving nothing about whether the
fallback works, and that the arithmetic's own comment states its purpose
as surviving a failure the earlier rule misses. That purpose is testable
only by injecting the failure.

Built exactly as you specified, at `0c18884`:

- The fault model is DECLARED, test-only, production untouched: the
  primary guard FAILS OPEN for `skills_instructions` only, by skipping
  that one name in the masking loop.
- `test_the_fallback_classifies_correctly_when_the_guard_fails_open`
  runs the UNCHANGED arithmetic under that fault first and requires the
  same verdict on all 38 shapes. It passes.
- Each of the three arithmetic mutants is then applied ON TOP of the
  fault. All three die:

```
2-close-before-open-accepted  killed by arrangement/closer-before-opener.ambiguous (expected True, got False)
3-only-openers-counted        killed by arrangement/two-closers.ambiguous       (expected True, got False)
4-zero-and-one-collapsed      killed by arrangement/opener-only.ambiguous       (expected True, got False)
```

- `test_the_primary_guard_still_refuses_directly` keeps measuring that
  `Hide-KnownContainer` normally throws on those arrangements, so the
  fault model is a departure from something established rather than from
  an assumption.

The survivor assertions are GONE. 49 tests, green on Windows PowerShell
5.1 and on PowerShell 7.

**Q2 accepted.** Item 9 closes with no residual, at the narrow scope
already agreed: generated shape coverage for these TWO parsers, not parser
correctness across the repository.

**Q3 recorded as your PASS**, including your point that length-preserving
masking cannot manufacture a malformed arrangement, so fault injection was
the only route.

## Your two UNVERIFIED items, now supplied

You could not run Python. Both are reproducible from the committed tree:

```
python -m pytest evals/multi-model-verify/test_skill_report_shapes.py -q
  -> 49 passed          (and 49 passed again with PARALLAX_PS_HOST=pwsh)
python evals/tools/skill_lint.py skills/multi-model-verify --strict
  -> PASS - 0 error(s), 0 warning(s)
```

I am reporting those as MY runs, not as verified evidence you hold.

## Nothing else is open from my side

Tasks 1 through 6 are complete. Task 7 is records. Task 8 is the twelve
live runs under the predeclared rule, after the bump and the cache update.

<final-check>
If you have no new substantive finding, say PASS and say explicitly that
this is an ADJUDICATED DRY ROUND closing the reopened point and the plan.
If you do have one, say it plainly - a finding here is worth more than a
clean close, and the user has authorized this round either way.
</final-check>
