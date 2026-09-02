## Round 16 findings

1. **CLOSES — handled-failure residue.** The test now guarantees only that the process tree is dead and no receipt was published, while explicitly permitting the reserved directory and control files to remain. That matches the executable transaction and catch behavior. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:77`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:121-128`

2. **CLOSES — orphan-section oracle.** The Python check scopes itself to the orphan section and requires three complete clauses, including both “every committed launch” and the interrupted launch potentially having no pid. The current stale spec lacks those meanings, so this oracle demonstrably has a red input. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:836-845`, `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:175-183`

3. **CLOSES — state-order oracle.** It rejects the stale liveness-first assertion, requires all six state names, and compares their positions with the executable order. The current spec still contains the forbidden assertion and obsolete seven-state model, so the check cannot pass before reconciliation. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:847-855`, `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:190-207`

4. **CLOSES — completion-condition taxonomy.** The record now distinguishes cross-act false completion from an unclassified condition and from an unfinished round exiting zero. Its detailed Round 4 and Round 9 entries support those examples. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:901`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:911`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:919`

## Sweep

The working base rate is sixteen numbered dispatches out of sixteen. I found no new completion-model hole after searching stale/mismatched receipts, partial publication and hard kills, PID reuse and unreadable liveness, replies written while running, malformed exit artifacts, exit-code mapping, and evidence binding. Those paths are now explicitly ordered and exercised. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:69-108`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:132-145`

I did find a new internal contradiction in the debate record:

- **Input:** the revision containing Round 16’s corrections.
- **Sequence:** the record says there were only fifteen numbered dispatches and fourteen full reviews, then attributes a correction to Round 16, while its “no new completion path” and propagation ranges still end at Round 15.
- **Artifact:** the plan’s own `What the debate changed` record. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:899-903`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:921-923`

## Is the defect rate in the plan?

Partly. Repeated review is exposing the defects, not creating them. The runtime mechanism has remained stable; the recent defects are concentrated in Task 9’s reconciliation text and its oracles. Because Task 9 ships the reconciled spec and closes the backlog items, an oracle that accepts inverted meaning is a real plan defect, even if it does not corrupt the dispatcher. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:778-855`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:882-892`

The Round 14–16 consequences divide as follows:

- Stale orphan/state sections and the non-binding replacement oracles could have shipped a materially wrong spec; their then-current oracles would not have caught it. The current exact-clause and order checks now do. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:798-805`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:828-855`
- The handled/irreducible attribution and “nothing is left behind” were misleading plan prose rather than an oracle-backed runtime requirement: the executable steps required killing the tree and withholding the receipt, not filesystem cleanup. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:77`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:121-128`
- The debate-count and completion-taxonomy errors ship incorrect historical documentation, but do not alter dispatch behavior. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:897-923`

## Freeze decision

Not yet. The smallest sufficient fix is purely documentary:

- Change the record to sixteen numbered dispatches: fifteen full reviews and one poll.
- Extend “Rounds 10 to 15 found none” through Round 16.
- Extend the Round 13–15 entry through Round 16 and record its handled-failure wording and semantic-oracle findings. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:899-923`

After that surgical correction, freeze and execute; I found no justification for another mechanism revision.

UNVERIFIED: the refused Round 7 artifact and its external scratchpad provenance are explicitly outside this repository, so I did not use them in the verdict. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:899`

FIX