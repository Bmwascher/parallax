<role>Adversarial reviewer, equal weight, in a two-model debate over an implementation plan.</role>

<task>Refute or confirm each numbered claim about the 0.14.0 implementation plan below. The plan is the review subject; the approved design spec is the fidelity baseline. You are reviewing the plan BEFORE it freezes — a missed defect here becomes frozen instruction for a zero-judgment implementer.</task>

<subject>
Plan: docs/superpowers/plans/2026-07-26-seat-reshuffle.md
Spec (fidelity baseline): docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md
Subject revision: commit ea84e4fca86c950c1054d0cf30d1fa5d510d3332 (branch feat/0140-seat-reshuffle). The working tree you are reading IS this revision.
</subject>

<rules>
Cite a repo-relative file:line for every claim you make or contest; uncited claims will be struck. Read the files you cite. Do not manufacture objections: if a claim stands, say PASS and move on. End each claim with PASS, FIX (with the specific fix and its evidence), or ESCALATE, then close with ONE overall verdict line: PASS, FIX, or ESCALATE.
</rules>

<claims>
1. Coverage: every normative spec requirement maps to a plan task — spec sections 3 and 5 (agent contracts) plus the panel-reviewer agent to Task 2 (plan line 253); section 6 (panels reference) to Task 3 (line 456); sections 7-8 (failure handling, declarations, record format) to Task 4 (line 574); sections 4, 8, 9 (required review, driver-seat notes, routing) to Task 5 (line 715); section 10 (README) to Task 6 (line 993); section 12 (eval case) to Task 7 (line 1474); section 11 (tests) to Task 1 (line 54); section 13 (verification and rollout) to Task 8 (line 1525). Nothing normative in spec sections 1-13 lacks a plan home, and no task builds anything section 14 rules out of scope.

2. TDD wiring: the test file embedded in Task 1 Step 1 is internally consistent with the artifacts Tasks 2-7 embed — every string a test pins appears byte-identical in the corresponding embedded artifact — and the expected RED baseline (12 failed, 152 passed, 1 skipped; plan line 243) and final state (164 passed, 1 skipped; line 1463) are arithmetically consistent with ten new tests plus Task 1's REQUIRED_REFERENCE_FILES edit.

3. Containment class: both new reviewer agents pin `model: fable` and `tools: Read, Grep, Glob` in frontmatter with no Bash and no write tools, and the tests pin exactly that (plan lines 100-104) — the tool allowlist, not prose, is the control (the 0.13.0 lesson).

4. The required fable review lands as a single-line byte-exact SKILL.md sentence counted exactly once by the tests, and the routing requires the mode-diff round-1 brief to cite the retained range-bound artifact plus the session's per-finding adjudications (Task 5).

5. Panels invariant: panels.md requires at least two members and at least one cross-vendor lane, declares an all-Claude panel invalid, enumerates exactly the valid compositions Sol+Kimi, Sol+Fable, Kimi+Fable, Sol+Kimi+Fable, and pins the subject-revision rule — diff mode pins SHAs, plan mode pins the SHA-256 of the round claims bytes until freeze, and a terminal verdict counts only when it cites the FINAL subject revision (Task 3).

6. Panel-lane-loss is consent-first: a lost lane stops the panel at the fallbacks.md consent gate, never auto-continues with fewer lanes, and a Fable-only remainder is DEGRADED (Task 4's fallbacks.md insertion).

7. Attestation mapping keeps the record schema unchanged and maps a panel to the strictest lane: Verification status FULL only when every participating lane's per-round evidence was clean AND every terminal verdict cites the final subject revision (Task 4's frozen-plan-format.md insertion).

8. The escalation lane's decision envelope is a single named carve-out from zero-judgment drift: envelope-designated DECISIONS are authorized outcomes, not drift; DEVIATIONS must be none; the carve-out sentence is test-pinned (Tasks 2, 4, 5).

9. Backup-lane panel participation is one paragraph declaring the panel invocation itself the consent, with containment, per-round evidence, and the write-probe applying unchanged, and no failure class recorded because nothing substituted (Task 4's backup-lane.md insertion).

10. Insertion safety: all nine anchored insertions across fallbacks.md, frozen-plan-format.md, backup-lane.md, model-prompting-notes.md, and SKILL.md name anchor text occurring exactly once in the target file at this revision, and no insertion or rewrite disturbs an existing tested pin — in particular the two README pins survive byte-exact (Global Constraints, plan lines 34-37) and the primary `Canonical model id:` declaration stays ahead of the backup block in model-prompting-notes.md.

11. Single-source discipline: no task adds a reviewer model-id literal outside the existing single-source homes; the new agents carry `model: fable` frontmatter only; nothing in the plan adds a `-m <literal>` anywhere.

12. Execution safety: strict task order 1 through 8 with a declared RED window (Tasks 1-6), long suites controller-run, a fresh implementer per task with Task 8 attended, and Task 8's two live verifications — dogfooding the required fable review on this very branch, and a two-round Sol+Fable panel smoke exercising the harness resume surface — cover exactly the two surfaces the probe record left open.
</claims>

<boundaries>
Not under debate (already decided by the user or settled by probe): the approved spec's design decisions themselves (its section 16 advisory record and the nine approved resolutions); seat assignments and the any-combination panel ruling; the README approach and the repo's public status; enforcement choice A; probed harness facts (the subagent resume surface carries no model parameter; Claude Code 2.1.220); the commit-message convention; this debate runs under the currently shipped 0.13.x protocol. Your job is plan-vs-spec fidelity, internal consistency, and execution safety — not relitigating the design.
</boundaries>

<final-check>List any claim you could not verify against files you actually read, as UNVERIFIED — do not fold unverified material into your verdict.</final-check>
