## Repair adjudication

1. R2-6 / D21. The factual narrowing is correct: the added assertions strengthen coverage while renaming and cleanup-helper changes are neutral. But the next sentence says this is “why none of them was noticed,” despite the entry itself saying the whole-branch review found them. Assertion strength explains why tests stayed green; it does not establish why people missed the drift. Replace it with: “Those departures therefore did not make the suite fail; the whole-branch review found them.” `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/execution-deviations.md:887-903`. **FIX**

2. R2-6 / D24. The four current copies are now correctly counted and the previously missed test-module site is named. The new historical inventory is still inaccurate:

- D24 says a meaning-level sweep found three further occurrences, but lists four files. `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/execution-deviations.md:982-993`.
- The named Sol round-2 brief does not make the exclusivity claim; it says only that the directory is created once. `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/sol-reopen-r2-brief.md:5-8`.
- Actual historical occurrences omitted from D24 remain in the Kimi round-2 brief and reply and the Sol round-4 brief and reply. `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/kimi-reopen-r2-brief.md:4-8`; `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/kimi-reopen-r2-reply.md:69-73`; `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/sol-reopen-r4-brief.md:9-17`; `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/sol-reopen-r4-reply.md:18-22`.

The narrow fix is to stop claiming an exhaustive count: say “A meaning-level sweep found additional historical occurrences, including…” and either list the actual artifacts or omit the inventory. Remove the Sol round-2 brief from the exclusivity-claim list. **FIX**

3. R2-A. The live test comment now matches the builder, CLAUDE.md, and backlog: creation and both seam writers are distinguished, the seams precede the nonempty-directory throw, and the comment claims detector coverage rather than shipped threat evidence. `evals/multi-model-verify/test_kimi_lane_home.py:1901-1914`; `tools/new-kimi-lane-home.ps1:904-948`; `CLAUDE.md:84-93`; `docs/superpowers/plans/2026-07-27-0150-backlog.md:48-55`. **PASS**

4. R2-7. Item 18 now states expectation 1 accurately and limits the conclusion to a failure mode: the grader must see the required `codex exec` invocation, while transcript truncation can hide it regardless of run behavior. `docs/superpowers/plans/2026-07-27-0150-backlog.md:1110-1116`; `evals/multi-model-verify/evals.json:12-16`; `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/execution-deviations.md:876-880`. **PASS**

5. R2-additional. Item 17 no longer claims a one-cell comparison. It identifies the flag-on pair member and the fresh-home difference without claiming those were the only differences, matching the probe record. `docs/superpowers/plans/2026-07-27-0150-backlog.md:22-27`; `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:152-156`. **PASS**

6. Frozen-versus-evidence boundary. The line is correct and none of the four named artifacts should be rewritten:

- The plan statement sits under “What the reopened debate changed,” inside the appended revision-7 debate record. `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:998-1015`.
- The Kimi artifact identifies itself as the reviewer’s retained final reply and frames the statement as “What I would ship.” `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/kimi-reopen-r1-reply.md:1-11`; `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/kimi-reopen-r1-reply.md:73-77`.
- The Sol round-2 brief does not assert exclusivity, so it needs neither preservation rationale nor correction for this claim. `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/sol-reopen-r2-brief.md:3-8`.
- The reopened debate record explicitly says nothing was implemented and the plan had not yet been amended. `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/reopened-debate-record.md:1-6`.

The other omitted round artifacts are likewise retained debate evidence, not current shipped-code descriptions. Keep them unchanged; correct only D24’s account of the sweep. **PASS**

7. Regression check. No executable behavior changed in this repair diff: the only Python edit is a section comment, while the other changed files are the backlog and ledger. The regression is documentary—D24 newly claims an inaccurate meaning-level inventory—and D21 remains incompletely narrowed. `evals/multi-model-verify/test_kimi_lane_home.py:1901-1914`; `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/execution-deviations.md:897-900`; `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/execution-deviations.md:982-993`. **FIX**

## UNVERIFIED

The reported fast-tier executions and 973-passed/13-skipped dual-host results were not independently rerun because this environment has no Python command. They are not used in the verdict. The required gate set is `CLAUDE.md:11-18`.

**Terminal verdict for `e94c0b5..a1f0ddd`: FIX.**