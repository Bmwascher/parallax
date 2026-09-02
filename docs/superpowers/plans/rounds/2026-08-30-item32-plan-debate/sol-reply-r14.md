## 1. Round 13 findings

1. Hard-kill test — CLOSES

The test now kills the tool before publication and expects `no-receipt`, while the transaction publishes pid, marker, and only then the receipt. Poll check one therefore handles exactly that arrangement. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:104`, `:126-127`, `:134`.

**CLOSES.**

2. LAUNCH UNKNOWN redefinition — DOES NOT CLOSE globally

The operative test and pinned state region correctly define it as a valid receipt followed by a missing marker. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:78`, `:226-232`.

But three plan passages retain the former meaning:

- The opening still says a hard kill makes `LAUNCH UNKNOWN` the irreducible state. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:17`.
- The residual comparison still calls `LAUNCH UNKNOWN` “narrowed,” although marker loss is no longer the hard-kill window being narrowed. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:53`.
- Item 32’s closure text still records “LAUNCH UNKNOWN is narrowed, not eliminated.” `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:848`.

**DOES NOT CLOSE — replace those residual hard-kill associations with NO RECEIPT.**

3. Danger moved to NO RECEIPT — DOES NOT CLOSE globally

The state and operation regions correctly say an interrupted launch may leave no receipt, no pid, and a live untracked child. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:215-222`, `:272-277`.

However, the spec’s orphan section still claims detached dispatch solves the orphan problem because “the pid is on disk,” and Task 9 does not explicitly schedule that section for replacement or search for that stale sentence. `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:175-183`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:798-805`.

**DOES NOT CLOSE — reconcile and pin the spec’s orphan section.**

4. Receipt-freshness tests — CLOSES

One test proves a receipt present at entry blocks before directory reservation. The other creates it at the deterministic barrier and requires the create-new publication to fail through the tree-killing catch. Those cover both the initial check and its race window. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:72-73`, `:121`, `:125-128`.

**CLOSES.**

5. Marker-gone LAUNCH UNKNOWN fixture — CLOSES

A successful launch provides a valid external receipt; deleting only its marker permits checks one and two to pass and makes check three return `launch-unknown`. This fixture is reachable and consistent with receipt-last ordering. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:78`, `:134-136`.

**CLOSES.**

## 2. Sweep

The supplied base rate is thirteen rounds out of thirteen; the plan itself continues to require treating the completion class as open. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:25`.

I found no new false-completion path. I searched interrupted publication, marker deletion, pre-existing and racing receipts, mismatched expected acts, PID reuse, live partial replies, and terminal exit/reply combinations. The ordered poll still prevents each unfinished arrangement from reaching `reply-present`. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:72-92`, `:132-145`.

I did find new internal contradictions and a non-binding reconciliation oracle, extending the broader sequence to fourteen rounds:

- The plan’s opening, declaration rationale, and closure record still associate the irreducible hard-kill condition with `LAUNCH UNKNOWN`. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:17`, `:299`, `:848`.
- The spec says liveness is checked first, but receipt validity and expected-act identity now precede liveness. `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:190-194`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:132-139`.
- Task 9 instructs polling with the expected directory and round, but its positive oracle checks only `-ExpectedDispatchDir`; omission of `-ExpectedRound` still passes. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:798`, `:819-823`.
- The convergence grep catches the old seven-state count but not the stale claim that liveness runs first or that the pid is always on disk. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:804-805`, `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:180`, `:191`.

## 3. Freeze decision

The plan is not ready to freeze. No launch-mechanism change is needed; the smallest sufficient correction is:

- Replace the stale `LAUNCH UNKNOWN` hard-kill associations at plan lines 17, 53, 299, and 848 with the new NO RECEIPT consequence.
- Make Task 9 explicitly replace the spec’s orphan claim and “LIVENESS IS CHECKED FIRST.”
- Extend Task 9’s positive oracle to require `-ExpectedRound` and the receipt-last consequences: expected-act checks before liveness, NO RECEIPT not proving nothing started, and LAUNCH UNKNOWN meaning a marker that subsequently disappeared.

The exact thirteen-round historical count is prompt-supplied; the repository’s written debate history currently records only the first four rounds. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:859-869`.

**FIX**