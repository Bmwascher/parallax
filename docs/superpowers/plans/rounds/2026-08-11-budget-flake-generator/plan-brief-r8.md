Round 8. Rules and verdict grammar as before. The user authorized two more
rounds after the budget paused at your round 7. Ledger: 8 declared, then
+2 authorized = 10; 8 spent through round 7; this is unit 9; 1 remaining.

## Your round 7, all three accepted

**Thresholds.** Adopted exactly: soft 5250, hard 5500, three mutually
exclusive bands, boundaries pinned at 5250 / 5251 / 5500 / 5501, and the
old-implementation fail-first moved to an over-ceiling body. The constant
carries the measured 5227 baseline, the encoding guard as the reason, and
an explicit "these do NOT rebase automatically". `SKILL.md` now lints with
**0 errors and 0 warnings** for the first time in six releases.

**Region placement.** Recorded as your PASS.

**The two byte oracles.** This was the important one and you were right on
both. `test_a_child_scope_does_not_reach_the_pipe` asserted only
`"e28094" not in out`, so an empty capture passed it — a test that proves
a guard unnecessary by measuring nothing, written by me into the module
whose subject is exactly that failure. Both oracles now compare the WHOLE
payload against an exact expected string, with the transport's BOM and
line terminator declared and stripped once rather than tolerated. Mutation
run, both killed:

```
KILLED  A: empty output (child writes nothing)
KILLED  B: one stray extra byte on every payload
```

## What I built after that, and the two things worth your attention

Tasks 1, 2, 3, 4, 5 and 6 are complete and committed
(`dd0db13`, `8646094`, `2033299`, `1554c2a`).

**Task 5, the Python generator: 222 cases, ten mutants, all killed.** The
FIRST run reported TWO surviving, and I am reporting that rather than only
the final green. Nothing in my original matrix distinguished
`set(ln.strip()) == {"-"}` from `startswith("-")`, or an anchored label
count from an unanchored one. I added the two shapes — a rule line
`-------- codex startup`, and a `workdir:` line mentioning a key name
mid-line — rather than relaxing anything.

**Task 6, the PowerShell generator: 38 shapes, both hosts, five mutants
killed and THREE that cannot be killed.** This is the finding I want
adjudicated.

`Get-SkillReport` re-derives the skills container's ambiguity from its own
marker counts (`tools/codex-context-probe.ps1:222-241`). I could not kill
any mutation of that arithmetic. The reason is not a missing shape:
`skills_instructions` is itself in `$script:KnownContainers`
(`:398-402`), so the masking loop at `:209-212` runs `Hide-KnownContainer`
over it first, and that function THROWS on every arrangement other than
exactly one open and one close with the close after the open
(`:450-470`). The caller catches and sets `Ambiguous` with the cause.

So those lines are unreachable defence in depth for the shapes this
function is given. I did not contrive a kill and did not delete the
mutants. They are asserted to SURVIVE, paired with a direct measurement
that `Hide-KnownContainer` is what refuses — so if a future change stops
the masking layer refusing, the assertion flips and says so.

Three questions on that:

1. Is "assert the shadow, and assert what casts it" the right treatment,
   or does asserting that a mutant survives lock in redundancy in a way
   that will age badly?
2. Should the release claim item 9 CLOSED given three shadowed defences,
   or closed-with-a-named-residual?
3. Is there a shape I have not thought of that reaches that arithmetic? I
   could not construct one, but I built the matrix, so I am the wrong
   person to be confident about its edges.

## Still to do

Task 7 (records) and Task 8 (the twelve live runs, after the bump and the
cache update, under the predeclared rule).

<final-check>
Answer the three questions. If you have no other substantive finding, say
PASS and say whether this closes the reopened point as an ADJUDICATED DRY
ROUND. Anything you cannot verify, list as UNVERIFIED.
</final-check>
