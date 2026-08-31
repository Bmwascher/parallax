# Round 12 - the four changes from round 11

You are the cross-vendor reviewer on backlog item 32 (detached dispatch) and
item 33 (automatic review mirror). This is round 12. Your round 11 reply is
above in this session.

The mirror is a fresh file copy of the working tree at source commit
`d87f1fe` on branch `item32-detached-dispatch`. Its own `HEAD` is the
builder's remediation commit, by construction. The plan file in the mirror
was hash-compared to the source before dispatch and is identical.

The plan is `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md`.
The spec is
`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`.

Ground every claim in a `path:line` you actually opened in this mirror.

## Your four required changes, and what I did

I reproduced all four before acting. I checked the `Start-Process` counts
myself: 0 in `skills/multi-model-verify/SKILL.md` and 0 in
`skills/multi-model-verify/references/backup-lane.md`. You were right that
both guards pass today.

**1. The exit sentence, matched and wholly pinned.** The point of use now
reads: 0 means `reply-present` and nothing else; 3 means `running`, an
UNFINISHED round; 1 is any other state, a transport failure with the state
name on stdout; 2 is a parameter-binding failure or an internal execution
error. That is Task 1's wording, clause for clause. The per-site assertion
is now ONE literal covering all four clauses, and its message says why: two
clauses could drift or vanish while the test stayed green.

**2. Honest failure counts.** Task 3 now expects **3 FAILED and 1 PASSED**,
and says which one already passes and why. Task 4 the same. I took your
point beyond the arithmetic: a red-then-green ritual that cannot go red
teaches nothing, so both tasks now say to note it in the commit message
rather than let a guard that was green all along read as coverage the task
earned.

**3. The positive spec oracle.** You were right that `grep -c "A\|B\|C"`
counts LINES matching any alternative, so three lines carrying only the
first token satisfied it. Replaced with a section-scoped loop that counts
each token separately and expects every one of the three to be at least 1.

**4. The scope table's task numbers.** Task 9 now opens by correcting
`design.md:65-71`, which assigns the codex sites to Task 4 and the kimi
sites to Task 5 while the plan implements them in Tasks 3 and 4. Its oracle
is stated: the five rows must read Task 3, Task 3, Task 4, Task 4, Task 4,
and a grep for `Task 5` must return nothing outside a passage narrating
history.

## What I want from you

1. For each of your four required changes, say CLOSES or DOES NOT CLOSE,
   citing the `path:line` you read.

2. **The base rate is eleven rounds out of eleven** finding at least one
   completion-model hole, an oracle that binds nothing, or an internal
   contradiction - though rounds 10 and 11 both found NO new
   false-completion path and named the shapes they swept for. State the base
   rate. Then either name a new instance of any of the three kinds, or say
   explicitly that you searched and found none, and name what you searched.

3. Every round since round 8 has found at least one defect that the PREVIOUS
   round's fix introduced, including two oracles that were themselves wrong
   on the first attempt. Revision 11 touched Task 3's point-of-use sentence
   and its per-site assertion, Task 3 and Task 4's expected counts, Task 9's
   positive oracle, and added a scope-table paragraph to Task 9. Sweep that
   text first, and say plainly if you think the fix-introduces-defect rate
   means this plan should be frozen and executed rather than revised again.

4. Say plainly whether this plan is ready to freeze and execute. If not,
   name the smallest set of changes. If it is ready, say so without hedging
   and give me the honest FLOOR: what these nine tasks will NOT have
   verified when they are all done.

End with PASS, FIX, or ESCALATE.
