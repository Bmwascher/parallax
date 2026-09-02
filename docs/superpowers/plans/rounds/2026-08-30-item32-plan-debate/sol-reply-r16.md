## 1. Round 15 findings

1. Handled-failure attribution — DOES NOT CLOSE cleanly

The handled/irreducible distinction is now correct: this test exercises the catch, while the hard-kill test bypasses it. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:77`, `:104`.

But the replacement says “nothing is left behind.” The launch has already reserved the directory and installed wrapper/control files, while the catch only kills the process tree and exits; it specifies no filesystem cleanup. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:121-128`.

Specific fix: say “no live process tree is left and no receipt is published,” not “nothing is left behind.”

**DOES NOT CLOSE.**

2. Positive orphan-section oracle — DOES NOT CLOSE

The check is section-scoped and can fail, but its three independent tokens do not bind the required relationships. For example, “Every committed launch has no receipt; an interrupted launch has a pid” contains all three tokens and passes while asserting the opposite behavior. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:800`, `:831-832`, `:839`.

Specific fix: assert exact normalized clauses connecting committed launches to an on-disk pid and interrupted launches to no receipt/possibly no pid.

**DOES NOT CLOSE.**

3. Positive state-order oracle — DOES NOT CLOSE

The loop checks that six names exist but never compares their positions. “Liveness is second” with all six names present passes because the only negative assertion forbids the exact uppercase phrase `LIVENESS IS CHECKED FIRST`. This is precisely the evasion the prose claims the oracle catches. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:833-839`.

Specific fix: assert the indices of the six state names are strictly increasing, preferably in a heading-scoped Python check.

**DOES NOT CLOSE.**

4. Debate record — DOES NOT CLOSE fully

The accounting is corrected: fourteen full reviews plus dispatch 5 as the two-lane poll, with the discarded attempt explicitly marked non-repo-verifiable. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:879`, `:893`.

The completion-history sentence remains overstated, however. It says all eight rounds found cross-act artifact substitution, while the detailed Round 4 and Round 9 entries describe broader completion-model defects—an unclassified condition and an unfinished round exiting zero. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:881`, `:891`, `:899`.

Specific fix: say those rounds found “a false-completion path or unclassified completion condition,” not that every one was cross-act substitution.

**DOES NOT CLOSE.**

## 2. Sweep

The supplied base rate is fifteen numbered dispatches out of fifteen finding a completion hole, non-binding oracle, or contradiction; the plan continues to treat completion safety as open. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:25`.

I found no new false-completion path. I searched receipt creation races, interrupted publication, marker loss, expected-act mismatches, token/PID identity, live partial replies, and all terminal exit/reply combinations. The executable ordering remains fail-closed. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:71-145`.

I did find one newly introduced contradiction and two still-non-binding oracles, extending the broader sequence through Round 16:

- “Nothing is left behind” contradicts the specified lack of filesystem cleanup. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:77`, `:121-128`.
- The orphan token check does not bind subject to consequence. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:831-832`.
- The state token check does not enforce order. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:833-835`.

The discarded Round 7 attempt remains UNVERIFIED, now correctly labeled as such by the plan. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:879`.

## 3. Freeze decision

The plan is not ready to freeze. No mechanism revision is needed. The smallest changes are:

- Replace “nothing is left behind” with the narrower process/receipt guarantee.
- Make the orphan oracle assert the two exact semantic relationships.
- Make the state oracle compare token positions, not merely presence.
- Replace the debate record’s cross-act claim with the broader completion-model wording.

**FIX**