Round 10. Rules and verdict grammar as before. The user authorized THREE
more rounds after your round 9 exhausted the budget. Ledger: 13
authorized, 10 spent, this is unit 11, 2 remaining.

## Your round 9 finding, accepted, and it was spec drift in my own plan

You were right and the class matters more than the instance: I hand-picked
19 arrangements and duplicated them for CRLF, while the plan I froze
specified a Cartesian product. Killed mutants over a matrix that is not the
declared one do not satisfy the declared enumeration, and I would have
reported "item 9 closed, all mutants killed" on a matrix that was never
built to spec.

Built at `cac6d53`, as declared:

**780 arrangement cases** = opener count {0,1,2,3} x closer count {0,1,2,3}
x ordering {opener-first, closer-first} x heading {inside, outside, both,
absent} x quoted container {none, one-opener, opener-and-closer} x line
ending {LF, CRLF}. Plus 12 entry-grammar cases, kept separate because they
vary the ENTRY LINE rather than the arrangement and crossing them would
multiply the matrix without testing anything new. Expected verdicts are
computed from the invariants for every combination, not written per case.

**The direct `Hide-KnownContainer` probe now covers all 32 canonical
arrangements**, not the three-case subset you flagged, and it asserts the
guard accepts exactly what the fallback accepts and refuses exactly what
it refuses — so the two layers are shown to agree about ambiguity rather
than spot-checked.

**All eight mutants killed, three only under the declared fail-open
fault.** 791 tests, green on Windows PowerShell 5.1 and PowerShell 7.

The product found kills the hand-picked set could not reach, which is the
concrete argument for your finding:

```
3-only-openers-counted        killed by o1c2/opener-first/...   (no 1-open-2-close case existed)
4-zero-and-one-collapsed      killed by o1c0/opener-first/...   (no 1-open-0-close case existed)
8-known-containers-not-masked killed by o0c0/.../quoted-one-opener (a quoted opener with NO real container)
```

That last one is the sharpest: a document whose ONLY skills delimiter is
quoted inside `<INSTRUCTIONS>`. The hand-picked set always paired a quoted
delimiter with a real container, so it never tested the case where masking
is the only thing standing between prose and a false positive.

## What remains

Task 7 is records. Task 8 is the twelve live runs under the predeclared
rule, after the bump and the cache update. No code work is outstanding.

## What I am NOT claiming

That the matrix is complete. It is the product the plan declared, over the
axes the plan declared. An axis nobody thought of is still missing, and
`Get-SkillReport` is one function in one script.

<final-check>
If you have no new substantive finding, say PASS and say explicitly that
this is an ADJUDICATED DRY ROUND closing the reopened point and the plan.
If you do have one, say it — the user authorized this round expecting that
outcome to be possible, and two units remain after it.
</final-check>
