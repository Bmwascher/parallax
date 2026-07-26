1. Coverage is incomplete in four places:

- The spec requires existing suites to remain green, but Task 1 deliberately makes two existing tests fail by registering `panels.md` before creating it (`docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md:307-340`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:222-243`). Move the `REQUIRED_REFERENCE_FILES` edit to Task 3; the RED baseline then becomes 10 failed, 154 passed, 1 skipped.
- Post-loss `Participants` must contain only lanes producing terminal verdicts, with the lost lane recorded in failure prose. The plan instead says `EVERY lane` (`docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md:189-193`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:660-677`).
- Sanctioned Kimi panel entry must emit no fallbacks banner, but the planned paragraph omits that rule (`docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md:144-151`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:691-695`).
- The README Mermaid must include the panel option explicitly; its planned graph contains the Fable review but only implies panels through `reviewer(s)` (`docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md:291-295`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:1045-1056`). Add an explicit solo-versus-panel route.

No Task builds a section-14 exclusion; structured transport, driver automation, quickstart, and schema expansion remain absent (`docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md:384-396`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:7-9`).

**FIX**

2. The ten test functions and all their pinned strings match the embedded Tasks 2–7 artifacts (`docs/superpowers/plans/2026-07-26-seat-reshuffle.md:95-219`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:269-437`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:471-556`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:601-695`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:758-954`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:1008-1433`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:1492-1507`). The current arithmetic is consistent: ten new failures plus two displaced existing tests gives 12 failed and 152 passed; restoring those twelve gives 164 passed (`evals/multi-model-verify/test_multi_model_verify.py:27-34`; `evals/multi-model-verify/test_multi_model_verify.py:84-93`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:235-243`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:1460-1464`). Applying Claim 1’s fix requires updating the RED expectation.

**PASS**

3. Both reviewer artifacts use exactly `model: fable` and `tools: Read, Grep, Glob`, while the tests require that line and reject Bash (`docs/superpowers/plans/2026-07-26-seat-reshuffle.md:95-120`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:269-275`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:325-331`). This matches the spec’s containment contract (`docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md:39-45`; `docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md:152-154`).

**PASS**

4. The required sentence is a single physical line, appears once in the planned SKILL replacement, and includes same-range review, retained artifact, and per-finding adjudications (`docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md:60-76`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:135-147`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:932-940`).

**PASS**

5. The panels artifact explicitly restricts panels to more than one lane, enumerates the four valid compositions, rejects all-Claude panels, and implements the mode-plan/mode-diff/final-revision rules (`docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md:118-141`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:474-516`).

**PASS**

6. The proposed failure class stops at consent, forbids automatic continuation, and marks a Fable-only remainder DEGRADED while allowing a clean surviving cross-vendor lane to remain FULL (`docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md:170-188`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:602-620`).

**PASS**

7. The unchanged-schema and strictest-lane sentences are present, but the post-loss mapping is wrong: `Participants` is unconditionally defined as `EVERY lane`, contrary to the spec’s terminal-verdict-only rule (`docs/superpowers/plans/2026-07-26-seat-reshuffle.md:660-677`; `docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md:189-193`). Make the paragraph conditional: completed panels list every lane; post-loss continuations list only terminal lanes, with the lost lane and class in failure prose.

**FIX**

8. The plan establishes one named decision-envelope carve-out across the agent contract, frozen format, and mode-diff routing. It retains `DEVIATIONS - must be none` and treats only in-envelope `DECISIONS` as authorized (`docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md:82-116`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:385-435`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:637-643`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:942-950`).

**PASS**

9. The planned paragraph contains every property named in the claim, but it omits the spec’s separate normative instruction that sanctioned panel participation produces no fallbacks banner (`docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md:144-151`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:691-695`). Add and test-pin that clause in the same paragraph.

**FIX**

10. Every target anchor/replacement sequence occurs once at this revision: fallbacks (`skills/multi-model-verify/references/fallbacks.md:160-164`), both frozen-format locations (`skills/multi-model-verify/references/frozen-plan-format.md:1-7`; `skills/multi-model-verify/references/frozen-plan-format.md:79-88`), backup lane (`skills/multi-model-verify/references/backup-lane.md:11-15`), notes (`skills/multi-model-verify/references/model-prompting-notes.md:3-20`; `skills/multi-model-verify/references/model-prompting-notes.md:74`; `skills/multi-model-verify/references/model-prompting-notes.md:222-225`), and SKILL (`skills/multi-model-verify/SKILL.md:19-24`; `skills/multi-model-verify/SKILL.md:102`; `skills/multi-model-verify/SKILL.md:142-150`). Both README pins survive in the replacement (`docs/superpowers/plans/2026-07-26-seat-reshuffle.md:1098-1100`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:1122-1131`), and the primary declaration remains before the backup declaration (`skills/multi-model-verify/references/model-prompting-notes.md:31`; `skills/multi-model-verify/references/model-prompting-notes.md:208-220`).

**PASS**

11. The plan adds no primary or backup reviewer model-id literal and no literal `-m` invocation. The only added model declarations are the three agent-frontmatter `model: fable` lines (`docs/superpowers/plans/2026-07-26-seat-reshuffle.md:26-30`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:269-275`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:325-331`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:378-383`). The existing sweep covers skills, commands, tools, evals, README, CLAUDE.md, hooks, and agents (`evals/multi-model-verify/test_multi_model_verify.py:233-256`).

**PASS**

12. Three execution defects refute this claim:

- The required review is run and then committed, after which the panel smoke creates another commit. Consequently the later whole-branch mode-diff range cannot equal the range reviewed by Fable (`docs/superpowers/plans/2026-07-26-seat-reshuffle.md:1562-1574`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:1576-1607`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:1627-1629`). Run and commit the smoke first, then run the actual required review against the exact immutable final head; retain its artifact without advancing the subject head.
- The execution note incorrectly calls that artifact “Task 4”; it is created in Task 8 (`docs/superpowers/plans/2026-07-26-seat-reshuffle.md:1562-1574`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:1627-1629`).
- The probe leaves the dead-agent terminal-error case explicitly unexercised and assigns it to the attended smoke, but the smoke exercises only successful agent-file resume and transcript recall (`docs/superpowers/plans/rounds/2026-07-26-seat-reshuffle/subagent-resume-probe.md:77-85`; `docs/superpowers/plans/rounds/2026-07-26-seat-reshuffle/subagent-resume-probe.md:93-100`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:1599-1603`). Add an explicit lane-death/loud-notification probe or narrow the implemented failure claim.

**FIX**

UNVERIFIED — The actual pytest totals could not be executed because this review shell has no Python interpreter. The static test arithmetic was verified against the test structure and plan expectations only (`docs/superpowers/plans/2026-07-26-seat-reshuffle.md:235-243`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:1460-1464`). This does not affect the cited plan-fidelity defects.

**FIX**