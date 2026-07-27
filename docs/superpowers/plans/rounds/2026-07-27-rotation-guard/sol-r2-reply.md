A1, A2, and A5 are confirmed. The fallback assertion now spans the transient exception, skip rationale, and user re-spend decision (`evals/multi-model-verify/test_backup_lane.py:442-453`), matching the operative prose (`skills/multi-model-verify/references/fallbacks.md:152-160`). The residual false-negative is likewise pinned as a complete normalized sentence (`evals/multi-model-verify/test_backup_lane.py:157-165`), matching `skills/multi-model-verify/references/backup-lane.md:64-66`. All seven lane pins plus the fallback pin are absent at `b040079` and present at `472cdc4`, consistent with the retained check (`docs/superpowers/plans/rounds/2026-07-27-rotation-guard/base-absence-check.txt:8-25`).

One blocking evidence defect remains:

- The gate artifact is not actually captured at subject head `472cdc4`. Its own header says it ran at `8eacc8a + uncommitted pin additions` (`docs/superpowers/plans/rounds/2026-07-27-rotation-guard/gate-output.txt:1`). Although it records successful outputs for all four commands (`gate-output.txt:3-29`), it does not bind those uncommitted bytes to the later commit. Round 2 expressly requires verification against the new revision, and the new commit changed executable test content (`evals/multi-model-verify/test_backup_lane.py:157-165`, `:442-453`). Specific fix: rerun all four gates after checking out committed head `472cdc4`, and retain output whose header records that exact SHA.

I agree with deferring a structural replacement for substring pins. Instances ten and eleven demonstrate recurrence (`evals/multi-model-verify/test_backup_lane.py:147-165`, `:442-453`), but the current eight pins now cover the complete operative clauses. A generalized mechanism would be new design scope, not a missing requirement of this two-item diff.

UNVERIFIED, excluded from the verdict:

- Fresh gate results at committed `472cdc4`.
- The exact 2026-07-27 offsets, route-line multiplicities, and write-probe outcomes. `probe-record.md` records them (`docs/superpowers/plans/rounds/2026-07-27-rotation-guard/probe-record.md:36-65`), but its “verbatim” traceback elides paths (`probe-record.md:15-28`) and its route/write-probe sections are summaries rather than raw captures. The underlying rotation attempt itself remains independently corroborated by a retained raw Loguru error (`docs/superpowers/plans/rounds/2026-07-26-backup-lane-mirror/kimi-r1-reply.md:1-10`).

**VERDICT: FIX — rerun and retain the four gates at exact committed head `472cdc4`.**