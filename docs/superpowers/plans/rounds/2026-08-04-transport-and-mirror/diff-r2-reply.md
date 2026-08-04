## Repair adjudication

1a. The replacement now makes only the supported comparative claim: both arms denied `Skill`, so they did not isolate the flag. The positive pin and negative clause would fail if either corrected wording or struck causal wording returned. `skills/multi-model-verify/SKILL.md:70-73`; `evals/multi-model-verify/test_multi_model_verify.py:209-226`; `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/execution-deviations.md:943-949`. **PASS**

1b. The region now separates measured home-root suppression from project-root help text, explicitly leaves populated-target behavior unmeasured, and binds suppression to an empty target. That matches the probe’s retraction exactly. Its full text remains inside one failing assertion, and both region IDs remain declared. `skills/multi-model-verify/references/backup-lane.md:355-377`; `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:280-294`; `evals/multi-model-verify/test_backup_lane.py:868-891`; `evals/multi-model-verify/test_contract_coverage.py:672-679`. **PASS**

2. The probe record correctly names the held constants, fresh-home difference, and flag as the intended—not sole—differing variable. `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:152-156`. **PASS**

3. The two edited comments now match the implementation: `New-Item` plus the two env-gated `Set-Content` sites are all in the builder; the seams precede an exact, forced enumeration; any seeded entry throws before custody output; catch cleanup and lock release remain reachable. Test callers use the seams only to require failure. `CLAUDE.md:84-93`; `tools/new-kimi-lane-home.ps1:904-948`; `tools/new-kimi-lane-home.ps1:980-1003`; `evals/multi-model-verify/test_kimi_lane_home.py:1916-1959`. **PASS**

5a. The incapable timing test is gone, its two valid assertions are assigned to existing coverage, and the surviving timing test actually observes the created directory through failed rollback. `evals/multi-model-verify/test_home_skill_canary.py:256-277`; `evals/multi-model-verify/test_home_skill_canary.py:440-473`. **PASS**

5b. The docstring and D10 now describe exact membership in `"\n"`, `"\r\n"`, or `"\r"`; the implementation does precisely that and excludes composites such as `"\n\n"`. `evals/tools/check_exact_line_oracles.py:95-132`; `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/execution-deviations.md:347-359`. **PASS**

6. D21–D27 record the identified departures, but two new ledger statements are false:

- D21 says every listed departure makes a case stricter, although its own list includes test renames and an added removal helper, neither of which strengthens an assertion. Replace this with “none weakens coverage; the added assertions are stricter.” `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/execution-deviations.md:891-901`.
- D24 says there were three live copies and marks the repair fixed, while a fourth copy remains in `test_kimi_lane_home.py`. Update the count/site list and remove `FIXED` until that comment is repaired. `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/execution-deviations.md:934-970`; `evals/multi-model-verify/test_kimi_lane_home.py:1901-1912`.

**FIX**

7. The verdict label and version-bounded lane statement are correct, and item 18 now exists. But item 18 reverses expectation 1: the expectation asks for an observable `codex exec` invocation; it does not ask for truncation before one. Replace lines 1109–1114 with wording that says transcript truncation prevents the grader from observing the invocation expectation 1 requires. `docs/superpowers/plans/2026-07-27-0150-backlog.md:28-46`; `docs/superpowers/plans/2026-07-27-0150-backlog.md:1094-1118`; `evals/multi-model-verify/evals.json:12-16`; `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/execution-deviations.md:876-880`. **FIX**

## A, B, C

A. The three edited copies are consistent, but “all copies” is not closed: the test-module comment still says `New-Item` is the repository’s only writer, contradicting the two seam writers. Apply the same narrowed explanation there and amend D24’s three-copy account. `evals/multi-model-verify/test_kimi_lane_home.py:1901-1912`; `tools/new-kimi-lane-home.ps1:904-934`; `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/execution-deviations.md:964-970`. **FIX**

B. The historical boundary is the right repair shape. It preserves provenance while explicitly making the resolved block governing, identifies the two falsified claims, and forbids citing the retained text as current. Deletion is unnecessary. `docs/superpowers/plans/2026-07-27-0150-backlog.md:57-64`; `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/execution-deviations.md:1022-1037`. **PASS**

C. The ledger now names revision 7 and records why the prior header was stale; the frozen plan independently identifies itself as revision 7. `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/execution-deviations.md:1-12`; `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:5-7`. **PASS**

## Additional unresolved defect

The current resolved item-17 block still says C and D were “the same cell, one flag apart.” They were separate cells and separate fresh homes. Replace it with “the paired flag-on cell, under the intended flag difference” or equivalent. `docs/superpowers/plans/2026-07-27-0150-backlog.md:22-26`; `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:152-156`. **FIX**

## UNVERIFIED

The reported executions and exact 973/13 counts for the five required Python gates were not independently rerun because this review environment exposes no Python interpreter. Those results are not used in the verdict. `CLAUDE.md:11-18`.

**Terminal verdict for `e94c0b5..43e45ef`: FIX.**