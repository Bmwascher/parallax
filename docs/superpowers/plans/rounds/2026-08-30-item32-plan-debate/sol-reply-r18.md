## 1. Record correction

**CLOSES.** The section now explains why its count is fixed to a commit, binds the figure directly to `92c892f`—not its parent—and derives seventeen dispatches as sixteen reviews plus dispatch 5’s poll. The later ranges consistently extend through Round 17. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:901-905`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:925-929`

The detailed entries are internally consistent with that arithmetic: Rounds 1–4, the Round 5 poll, and Rounds 6–17. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:909-927`

## 2. Sweep

The working base rate is seventeen numbered dispatches out of seventeen. The record binds that count at `92c892f` and distinguishes the eight early completion-condition rounds from the later oracle and reconciliation findings. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:903-905`

I found no new completion-model hole. I searched receipt freshness and cross-act substitution, publication races and hard kills, marker/token/PID identity, replies written during liveness, terminal artifact parsing, exit-code mapping, and evidence binding. Those shapes have ordered branches and named cases. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:50-62`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:71-108`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:132-145`

I did find one still-weak oracle: **Task 8 validates the existence and row count of the probe record, not the measured outcomes.** A record containing all six required host/measurement rows could say that the launch blocked for the full sleep, the later process was dead, the state probes returned the wrong states, and the encoding binder rejected; the stated Task 8 oracle would still pass because it checks only that each row exists. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:743-767`

That matters because the plan calls the harness-boundary measurement its first end-to-end test of the central promise, while Task 9’s full gates merely run the resulting test suite. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:747-751`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:864-876`

## 3. Freeze decision

Not yet. No mechanism revision is justified, but the evidence oracle needs one surgical repair:

- Define the expected fields for each host/measurement row.
- Assert the boundary row reports return before child completion, a live process in the later call, and a late exit file.
- Assert the state row reports exactly `no-exit-file`, `no-receipt`, and `reply-empty`.
- Assert the encoding row reports binder acceptance and matching prompt hashes/lengths.
- Mutate one recorded outcome and demonstrate the test goes red.

Those values are already the task’s stated expected results; the missing part is making its designated oracle enforce them. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:747-767`

## 4. Honest floor

Even after all nine tasks succeed, a reader must not believe they have verified or solved:

- Recovery from an interrupted pre-receipt launch that may leave a live child with no pid; the plan deliberately surfaces but does not remediate it. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:211-222`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:269-277`
- Misattribution when a caller supplies an earlier act’s receipt, directory, and label together; the tool truthfully answers that earlier act. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:248-252`
- Item 51’s argv escaping, item 31’s pipes, the three existing item 58 path-resolution sites, or resume-after-kill soundness. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:27-29`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:886`
- Behavioural enforcement of background-task naming; its pin proves documentation presence only. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:283-293`
- The version bump or successful installation of the finished plugin; those occur after this plan. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:933-935`

FIX