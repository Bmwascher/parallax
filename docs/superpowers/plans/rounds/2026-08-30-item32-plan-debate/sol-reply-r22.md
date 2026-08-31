1. NameError oracle — CLOSES. Both sections are assigned before the first assertion, and the unreconciled spec lacks the first required orphan clause, so the repaired oracle reaches the intended semantic failure. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:939-948`, `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:175-183`

2. Two-form propagation — DOES NOT CLOSE. Lines 20, 30, 68, 79, and region one now distinguish the two carriers correctly. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:20`, `:30`, `:68`, `:79`, `:203-225`

   One single-form claim remains: “the documented calls keep `${CLAUDE_PLUGIN_ROOT}` verbatim.” That is unqualified and contradicts the three Kimi calls using `<plugin-checkout>`. Change it to “the two SKILL.md calls.” `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:77`, `:574-582`, `:622`

3. Task 7 pointer — CLOSES. It now says only that Task 7 step 4 is where the encoding is exercised, without the false “below.” `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:861`

Base rate and sweep

Base rate: 21/21, prompt-supplied. The repository correctly keeps its numeric total commit-bound and records later rounds separately rather than pretending to verify the running figure. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:1007-1013`

I searched receipt/expected-act identity, receipt-last interruption, PID reuse and liveness, exit/reply ordering, clean binder plus missing reply, Kimi decoding, oracle execution order, token carriers, and record ownership. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:148-161`, `:606-636`, `:939-959`

I found no new completion-model hole. In particular, the capacity-failure shape remains safely classified: nonzero exit becomes `exit-nonzero` before reply interpretation, and a clean brief binding cannot independently make a review result. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:155-161`, `skills/multi-model-verify/references/fallbacks.md:38-50`, `:121-136`

Revision-introduced defect

The revised record now claims its entries “end where the debate does,” but its Round 21 entry records only the NameError. It omits the first capacity-failed attempt, the remaining two-form propagation finding, and the pointer finding, despite the same record explicitly preserving Round 7’s discarded first attempt. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:1009-1011`, `:1035`

Freeze decision

Do not freeze yet. The smallest changes are:

1. Qualify line 77 as applying only to the two SKILL.md calls.
2. Complete the Round 21 record entry, or weaken line 1011’s promise that the entries end where the debate does.

No mechanism revision is justified. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:77`, `:1011`, `:1035`

FIX