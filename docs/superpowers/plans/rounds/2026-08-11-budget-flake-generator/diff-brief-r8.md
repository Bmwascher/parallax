Round 8. Ledger: 8 authorized, 7 spent, this is unit 8, **0 remaining
after it.** A finding here pauses for the user rather than being absorbed;
the user has already extended once and asked that the debate run until it
goes dry rather than stop at a number, so I will put it to them again if
you have one.

Both round-7 findings accepted. Nothing refuted.

**New head:** `9bc9338` (was `6205a06`).

## 1. Both self-contradictions, and a third I found auditing the fix

You caught two. Auditing my own fix before sending this, I found the same
sentence carrying a third, so all three are listed rather than the two you
named.

- The plan said "Two readings the freeze does not settle" above a list of
  three. Now "THREE readings".
- That same sentence also said all three were "recorded here rather than
  left in the code", which was false for the third — it lived in
  `render_field` alone until you found it at round 6. The sentence now
  separates the two facts: all three were DECIDED at the rebuild, only the
  first two were RECORDED then.
- `render_field`'s docstring called `K:` a form with "no value slot" and
  then justified its behaviour by saying the value position exists. Now
  "a VALUELESS form, which carries a value POSITION but no value in it".

Each correction carries a marker naming the round that caught it.

## 2. The count, and why there is now no count

Accepted. Twenty, not eighteen; eighteen was the five-round figure carried
forward without re-adding when round 6 was appended.

That is three wrong totals in four rounds — seventeen, then eighteen, then
eighteen again — produced by a session that had ALREADY written into that
same file, twice, that totals go stale. So the fix is not a fourth number.
**There is no total anywhere in the round README now.** The per-round
enumeration is the record, and the file says why in as many words:

> Three attempts, three wrong numbers, all of them arithmetic over a list
> that is right there. The list is the record.

## What I want on the record about rounds 5 and 7

Both were defects introduced BY THE PREVIOUS ROUND'S FIX. After round 5 I
wrote that down as a lesson — "a fix is new code and gets no discount" —
and then did it again two rounds later, in the fix for the finding that
lesson was attached to. The README says that plainly rather than
presenting seven rounds of corrections as steady progress.

I raise it because it bears on how much weight a PASS here should carry.
The last three rounds have found only record defects, and two of the three
were self-inflicted by the preceding fix. That is a pattern that argues
for one more look at the records rather than for confidence that they are
now clean.

## Gates on this head

- tiers 1, 1b, 1c: pass. `skill_lint` 0 errors, 0 warnings.
- `python -m pytest evals -q`: **2419 passed, 14 skipped in 476.67s**
- PowerShell 7: the same **2419 passed, 14 skipped** (430.07s). Both hosts.
- Count unchanged at 2419: rounds 6 and 7 moved no case, expected value or
  assertion.
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
this is an ADJUDICATED DRY ROUND closing the fix re-review, so the session
can issue the terminal verdict and attest. If you do have one, say it
plainly — this is the last authorized unit and it pauses for the user.
</final-check>
