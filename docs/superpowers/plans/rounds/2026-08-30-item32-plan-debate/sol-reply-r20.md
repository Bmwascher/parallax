## 1. Six findings

1. **Kimi reply test — CLOSES.** Task 7 now exercises every Kimi wrapper with non-ASCII and astral-plane output, compares exact UTF-8 bytes on both hosts, checks BOM absence, and proves deletion of the console-encoding line goes red. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:765-780`

   The limitation is honestly stated: malformed bytes decode non-strictly and the real client’s UTF-8 behavior remains unverified. The test proves the declared UTF-8 path, not arbitrary native bytes. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:619-623`

2. **Plugin-root measurement — DOES NOT CLOSE completely.** One invocation is adequate version-scoped evidence because the plan names Claude Code 2.1.251, records the observed substitution, requires a re-take, and stops if the current client returns `verbatim`. It does not need broader hedging. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:34`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:68-76`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:826-847`

   But Task 1 creates and stages `wrapper-probe.md` while omitting it from Task 1’s Files list—the same bookkeeping defect previously fixed in Tasks 8 and 9. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:43-45`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:165-169`

3. **Second orphan — CLOSES.** Task 9 now requires the dead-wrapper/live-child condition, and its positive oracle requires the decisive clause about the pid naming the dead wrapper. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:880-883`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:924-932`

4. **Running revision header — CLOSES.** The current header carries no running number and identifies Revision 5 only as historical context. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:13-15`

5. **“Five exact strings” — DOES NOT CLOSE completely.** The replacement is now positively required, but the assertion searches the entire spec rather than the constraints section containing the requirement. A historical paragraph containing “counts five exact strings” would satisfy it while the actual constraint remained absent. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:899`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:919-935`

6. **Debate record — CLOSES.** It now explicitly covers Round 18, the cold Fable review and Round 19 without changing the commit-bound total. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:988-994`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:1014-1024`

## 2. Sweep

The working base rate is nineteen numbered dispatches out of nineteen.

I found no new completion-model hole after rechecking publication races, stale receipts, liveness/PID reuse, wrapper failure, Kimi empty and malformed output, and both orphan-remedy failures. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:52-64`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:84-118`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:619-625`

I did find a new ownership contradiction: Task 7 says it writes per-host Kimi results into `wrapper-probe.md`, but neither its Files list nor commit includes that file; Task 8 simultaneously says it is the task adding the two host sections. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:743`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:780-790`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:795-835`

## 3. Revision 20 introduced

- Task 1’s probe-record Files omission. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:43-45`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:167-169`
- Task 7/Task 8’s conflicting ownership of the host sections. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:780-790`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:797-835`
- The claim that `-join "\n"` “discards nothing.” The shown expression inserts LF only between captured lines and appends no terminal line ending, so it canonicalizes output rather than preserving what redirection wrote. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:603-606`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:625`
- The Task 9 expected-result prose says “all three clauses,” while the executable oracle requires four. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:928-946`
- The new exact-string positive assertion is not section-scoped. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:919-935`

## 4. Freeze decision

Not yet. The smallest changes are:

1. Add `wrapper-probe.md` to Task 1’s Files list.
2. Give Task 7 or Task 8 sole responsibility for writing/staging `kimi_reply`.
3. Describe `-join` as newline canonicalization and define the test payload’s terminal-newline expectation.
4. Check “counts five exact strings” inside the constraints section.
5. Change “three clauses” to “four clauses.”

No launch, poll, or completion-state revision is justified.

FIX