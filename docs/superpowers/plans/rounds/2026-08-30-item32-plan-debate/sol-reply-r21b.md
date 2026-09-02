1. Task 1 Files list — CLOSES. The probe record is listed, its split ownership is stated, and Task 1 stages it. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:48`, `:171`

2. Probe-record ownership — CLOSES. Task 7 writes nothing to the record; Task 8 reruns the Kimi measurement, owns both host sections, and stages the record. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:790`, `:821`, `:847`, `:866`

3. `-join` — CLOSES. The contract now honestly specifies canonical LF without a trailing newline, and the test requires exact UTF-8 bytes from stdout. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:612`, `:633`, `:781-783`

   The native-executable requirement also closes the Fable finding: the plan explicitly excludes an in-process `.ps1` stub and requires the negative demonstration to cross the console-decoding boundary. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:783-784`

4. Four clauses — CLOSES. The oracle contains all four, and the expected result now says four. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:942-946`, `:960`

5. Exact-strings scoping — DOES NOT CLOSE. The revised assertion reads `con` before `con` is assigned. Even a perfectly reconciled spec raises `NameError` at line 937; assignment occurs only at line 948, contradicting the promised exit-zero result. Move `con = section('## Constraints that must survive')` above its first use. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:936-948`, `:960`

Token split

The two-form split is the right design. The measured fact is expressly limited to skill-body text; the reference file is read raw, while `<plugin-checkout>` is already its pinned path convention. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:34-36`, `skills/multi-model-verify/references/backup-lane.md:25`, `evals/multi-model-verify/test_backup_lane.py:139-142`

A fourth “harness fact” would be worse unless independently measured. The Kimi sections correctly use `<plugin-checkout>`, while the CLAUDE.md addition is correctly repo-relative. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:569-582`, `:619`, `:981`

However, the split was not propagated through the plan. Current text still says:

- The new call uses `${CLAUDE_PLUGIN_ROOT}`. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:20`
- Item 58 is addressed by “anchoring this one new call.” `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:30`
- The token appears in “every documented call and every test literal.” `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:68`
- If substitution fails, “five documented literals” are wrong. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:79`
- The pinned region calls the path anchored, while closure correctly admits three calls are merely named and unresolved. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:220-222`, `:987`

Those statements now contradict the actual two-form contract.

Sweep

Base rate: 20/20 as stipulated. The repository’s fixed record is deliberately bound to an earlier seventeen-dispatch point and separately records later rounds, so 20/20 itself remains prompt-supplied rather than repo-verifiable. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:1002-1008`, `:1030-1034`

I found no new completion-model hole after checking receipt identity and ordering, PID/start-time identity, liveness-before-terminal-artifacts, exit-code mapping, Kimi empty/non-ASCII output, and record ownership. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:148-161`, `:607-614`, `:781-790`, `:835-859`

I did find a new always-red oracle and the token-split contradictions above. Revision 21 also leaves the minor wrong-direction pointer “Task 7 step 4 below,” although Task 7 precedes Task 8. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:747`, `:805`, `:858`

Freeze decision

Do not freeze yet. The smallest fixes are:

1. Define `con` before the line-937 assertion. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:936-948`
2. Propagate the two-form distinction through lines 20, 30, 68, 77, 79, and 220-222, matching the already-correct closure at line 987.
3. Change “Task 7 step 4 below” to “above.” `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:858`

No mechanism revision is justified.

FIX