## 1. Round 14 findings

1. Four stale LAUNCH UNKNOWN associations — CLOSES

The opening now assigns the irreducible interruption to NO RECEIPT and defines LAUNCH UNKNOWN as marker loss. The residual, declaration rationale, and closure text now use the same distinction. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:17`, `:53`, `:299`, `:853`.

**CLOSES.**

2. Spec orphan section — DOES NOT CLOSE fully

Task 9 now explicitly schedules the orphan section for correction and the negative grep catches its exact stale sentence. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:798-800`, `:810`.

But no positive oracle covers that section. Deleting it entirely—or replacing it with text that omits the committed-launch/residual distinction—passes both the negative grep and the mechanism-section token loop, which examines a different section. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:821-828`.

**DOES NOT CLOSE — add a positive orphan-section assertion.**

3. LIVENESS IS CHECKED FIRST — DOES NOT CLOSE fully

The replacement instruction correctly says liveness is sixth, and the negative grep rejects the exact old phrase. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:801`, `:810`.

Nothing asserts the replacement ordering. “Liveness is second” would evade the stale phrase and the mechanism token loop while contradicting the executable order, where receipt validity, expected-act identity, marker, token, and pid precede liveness. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:132-139`, `:824-828`.

**DOES NOT CLOSE — assert the ordered state sequence positively.**

4. Positive oracle’s missing ExpectedRound — CLOSES

The mechanism-section loop now requires `-ExpectedRound` independently and terminates on any missing token. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:824-828`.

**CLOSES.**

5. Debate record — DOES NOT CLOSE

The record overcounts reviews. The plan originally records four review rounds followed by a two-lane poll, while the new record calls all fourteen numbered cycles “review rounds” and then adds the poll again. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:13`, `:866`.

It also says rounds 1–9 each found cross-act artifact substitution, but its own Round 5 entry names only wrapper quoting and path rules, while Round 5 was the separately identified poll. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:868`, `:880`.

The accurate accounting is fourteen numbered cycles through Round 14: thirteen full review rounds plus the Round 5 two-lane poll, plus the separately discarded unread dispatch. The stronger claim should be “completion-model holes in Rounds 1–4 and 6–9,” not “cross-act substitution in Rounds 1–9.” `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:872-890`.

**DOES NOT CLOSE — correct the round type and completion-path range.**

## 2. Sweep

The supplied base rate is fourteen numbered cycles out of fourteen finding a completion-model hole, non-binding oracle, or contradiction; the plan continues to require treating completion safety as open. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:25`.

I found no new false-completion path. I searched receipt publication and collision races, absent receipts after interruption, marker deletion, expected-directory/round mismatches, token and PID identity, liveness ordering, and exit/reply terminal combinations. The executable order remains fail-closed. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:71-92`, `:121-145`.

I found two new instances of the other classes:

- Task 9’s new corrections for the orphan and state sections still have no positive oracle capable of detecting deletion or a different wrong replacement. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:798-801`, `:821-828`.
- One additional stale hard-kill association remains: the handled-failure test says it is “the state Sol said cannot be eliminated,” although that test exercises the catch that kills the child; the irreducible condition is the separate hard-kill test that bypasses the catch. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:77`, `:104-108`.

That extends the broader finding sequence to fifteen numbered cycles.

## 3. Propagation sweep

The opening, residual, declaration rationale, and closure text are now consistent. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:17`, `:53`, `:299`, `:853`.

The remaining propagation failures are:

- The stale rationale at Task 1’s handled-failure test. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:77`.
- Task 9 verifies that two old sentences disappear but not that their required replacements arrive. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:798-810`, `:821-828`.
- The debate record turns the Round 5 poll into both a review round and an additional poll. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:866`, `:880`.

The discarded unread round is UNVERIFIED: neither document names an artifact from which its existence or disposition can be checked; it is asserted only in the debate summary. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:866`.

## 4. Freeze decision

The plan is not ready to freeze. No mechanism change is warranted. The smallest sufficient corrections are:

- Remove or correct the stale Sol attribution at Task 1 line 77.
- Add one positive, section-scoped oracle asserting the orphan residual and the ordered state sequence through liveness.
- Correct the debate record to thirteen full reviews plus the Round 5 poll, and identify completion-hole rounds as 1–4 and 6–9.

**FIX**