Round 5. Ledger: 6 authorized, 4 spent, this is unit 5, 1 remaining.

**The round cap was RESET BY THE USER, who authorized exactly one more
round.** You were right to stop at four consecutive contested exchanges
and right to return ESCALATE rather than absorb the finding. I put the
choice to the user with four options, including merging on ESCALATE with
recorded risk acceptance and stopping entirely; they chose one confirming
round. This is that round, and it is the last authorized one.

Both round-4 findings accepted. Nothing refuted, nothing reopened.

**New head:** `3f74843` (was `a51454e`). `git diff a51454e..3f74843` is the
whole of this fix; it touches three files.

## 1. What is hash-pinned, stated as narrowly as the test

`LICENSE-THIRD-PARTY.md` no longer says the fixture's "content is
hash-pinned". It now says the COPIED TEXT BELOW THE BANNER is pinned by
`test_skill_lint_budget.py`, that the banner is prose and EXCLUDED from
the hash, and that banner edits therefore break no pin. It records that
the earlier sentence claimed the whole file and was wider than the test.

I also pinned the narrowed sentence, in
`test_the_frozen_fixture_is_covered_by_the_notice`. Without that, the
notice could drift back to the wider claim silently, which is the same
mechanism that let the notice go stale in the first place.

## 2. The finding count

`README.md`'s through-line no longer totals. It enumerates: four spec
drifts and two narrowed claims at round 1, one blocking spec miss and four
record defects at round 2, one licence obligation and two record residues
at round 3, two overstated claims at round 4. The parenthetical says the
earlier "eleven" contradicted this file's own round table, and why a total
is the wrong shape here: it goes stale the moment a round is added, which
is exactly what happened.

The round table gained its round-4 row, and the README now records what
you did at the cap, because it is the first live exercise of backlog item
24's separation of the round cap from the fix-verify budget.

## Gates on this head

- tiers 1, 1b, 1c: pass. `skill_lint` 0 errors, 0 warnings.
- `python -m pytest evals -q`: **2419 passed, 14 skipped in 476.21s**
- PowerShell 7: the same **2419 passed, 14 skipped** (425.11s). Both hosts.
- Count unchanged at 2419: this round tightened two existing assertions and
  added no tests.

## Outstanding, unchanged and stated once more

Task 8 — twelve live behavioural runs against the INSTALLED plugin under a
rule predeclared before the runs, after the version bump and cache update.
Backlog item 18 reads `RESULT: pending` until then. Item 31 is the named
follow-up for `tools/check-drift.ps1`, excluded by name from this range's
certification unit, which is the documented multi-model-verify dispatch
contract in `skills/multi-model-verify/`.

Nothing else is open from my side. I am raising no new claim and asking
you to reopen nothing.

<final-check>
This is the last authorized unit. If you have no new substantive finding,
say PASS and say explicitly that this is an ADJUDICATED DRY ROUND closing
the fix re-review, so the session can issue the terminal verdict and
attest. If you do have one, say it plainly — it pauses for the user rather
than being absorbed.
</final-check>
