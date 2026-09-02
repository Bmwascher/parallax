## 1. Findings

### Round 18 Task 8

**CLOSES.** The record now has fixed fields, the test validates every outcome rather than counting rows, failed measurements must be recorded truthfully, and the mutation demonstration targets a specific value. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:803-820`

### A. Kimi reply encoding

**DOES NOT CLOSE.** The diagnosis stands: the repository’s measured precedent says native output is decoded through the console encoding and records IBM437 as the observed default; the proposed wrapper sets UTF-8 decoding and writes UTF-8 without a BOM. `tools/new-review-mirror.ps1:57-75`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:598-618`

But no test requires that mechanism. Task 4’s per-site assertions check only the launch, poll, client invocation and existence of a reply-path string; Task 7 requires merely “a reply present.” Restoring the defective `> $PSScriptRoot\reply` would satisfy both. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:550-586`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:756-762`

Add a non-ASCII UTF-8 stub result on both hosts and assert the reply’s exact UTF-8 bytes and absence of a BOM. Bind the three Kimi sections to the encoding/write lines individually. Also correct the precedent citation from `:64-66` to the supporting `:57-75`. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:614`

### B. Plugin-root resolution

**DOES NOT CLOSE.** The diagnosis is correct: hooks use the harness token while skill text uses a placeholder. `hooks/hooks.json:10`, `hooks/hooks.json:22`, `skills/multi-model-verify/SKILL.md:325-327`

The repair has three contradictions:

- Global Constraints still says there are **two** non-repo-verifiable harness facts, while Task 1 calls this the third. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:34`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:65`
- Step 0 requires recording the outcome and client version in Task 8’s record, but that record’s fixed schema and oracle contain no plugin-root field. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:68-75`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:803-818`
- The closure instruction still unconditionally calls the new path “anchored,” although Step 0 permits the weaker “named, not resolved” result. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:73`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:940`

Record and assert the measurement, then mechanically require its selected form across the outer-command test, contract region, five call sites and closure text.

### C. Second unkillable orphan shape

**DOES NOT CLOSE.** The new operation region correctly distinguishes completion safety from remedy failure and identifies the dead-wrapper/live-child case. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:280-297`

Task 9 still tells the spec to describe only the interrupted/no-receipt residual, and its positive oracle requires only that case. The reconciled spec can therefore omit the newly discovered committed-launch orphan while every Task 9 check passes. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:851-854`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:895-913`

Add the second remedy failure to the spec rewrite and to the section-scoped positive oracle.

### D. Stale freshness placeholders

**CLOSES.** The current skill names fresh reply/transcript placeholders, while the revision explicitly replaces that obsolete instruction with fresh dispatch-directory and receipt paths. Task 1 mechanically refuses reuse of either. `skills/multi-model-verify/SKILL.md:220-226`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:83-86`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:497-501`

### E. Task 8 Files list

**CLOSES.** The test file is now listed and staged by the same task. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:773-779`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:822-826`

### F. Revision header and exact-string count

**DOES NOT CLOSE.**

The historical Revision 5 paragraph is now labelled honestly, but its replacement immediately contradicts itself: it prints “Revision 19” while saying the revision number is deliberately not restated. Another revision makes that running number stale again. Remove the running number or bind it to a fixed commit. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:13-15`

The four-to-five diagnosis is correct: the test contains five counts. `evals/multi-model-verify/test_multi_model_verify.py:619-647`, `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:208-210`

But Task 9 only forbids “four exact strings.” Deleting the sentence passes; no positive oracle requires the replacement “five exact strings,” despite the plan explaining why negative-only checks are insufficient. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:863-882`

## 2. Sweep

The working base rate is eighteen numbered dispatches out of eighteen. I found no new false-completion path after rechecking receipt publication, expected-act binding, liveness and PID reuse, terminal-file ordering, Kimi output capture, and the two orphan conditions. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:52-64`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:83-118`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:280-297`

I found another record contradiction: the fixed-point paragraph promises that later rounds are recorded below by number, but the detailed record ends at Round 17 even though this revision explicitly incorporates Round 18’s Task 8 finding. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:814-820`, `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:957-983`

## 3. Freeze decision

Do not freeze yet. The smallest sufficient set is:

1. Add binding non-ASCII Kimi reply tests.
2. Bind and propagate the plugin-root measurement.
3. Propagate the second orphan-remedy failure into Task 9’s spec and oracle.
4. Replace the running Revision 19 header.
5. Positively require “five exact strings.”
6. Add the Round 18 detailed record entry.

None requires another detached-dispatch state or launch-mechanism revision.

FIX