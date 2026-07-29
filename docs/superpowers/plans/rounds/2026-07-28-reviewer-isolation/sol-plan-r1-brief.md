<role>Adversarial reviewer, equal weight, in a two-model debate. Neither side's claim outranks the other's; only evidence does.</role>

<task>Refute or confirm each numbered claim below about a plan for parallax 0.17.0. You are running read-only inside the parallax repo at C:/Users/Brandon/Documents/parallax. Read these two files first, in full:

- docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md
- docs/superpowers/plans/2026-07-28-reviewer-isolation.md

Then read whatever else you need: skills/multi-model-verify/SKILL.md (preflight 3), skills/multi-model-verify/references/backup-lane.md, evals/multi-model-verify/test_multi_model_verify.py, evals/multi-model-verify/test_contract_coverage.py, tools/verify-attestation.ps1 and tools/kimi-lane-lock.ps1 for the house style the new scripts must match.</task>

<rules>
Cite `path:line` in this repo for every claim you make or contest, anchoring each file with its full repo-relative path the first time you cite it. An uncited claim is struck, not debated.

Do not manufacture objections. If a claim stands, say PASS and move on. A sound plan converging in round 1 is the system working, not a skipped review.

Give a verdict per claim: PASS, FIX (with the specific fix), or ESCALATE (a disagreement evidence cannot settle). End with one overall verdict.

You cannot run commands. Where a claim rests on a measurement taken outside this repo, say so and treat it as UNVERIFIED rather than folding it into a verdict.
</rules>

<context>
parallax is a Claude Code plugin providing cross-model verification. This plan is backlog item 4 of `docs/superpowers/plans/2026-07-27-0150-backlog.md`.

Two problems, filed separately in the backlog, treated here as one:

- Preflight 3 (skills/multi-model-verify/SKILL.md:61-107) stops the gate when the reviewed repo carries an `AGENTS.md` or `.agents/skills/*/SKILL.md`. The stop is correct, but the remediation is driver-executed prose rebuilt by hand every run, so the cheap path is to abort into a weaker gate.
- The same preflight says the user's codex plugin cache is "not a stop and never a finding" (SKILL.md:103-107). Measured on 2026-07-28 that is false.

Numbers below were measured on the author's Windows machine, codex-cli 0.144.1, using `codex debug prompt-input`, which renders the model-visible prompt and calls no model. You cannot re-run them. Treat them as UNVERIFIED and attack the reasoning built on them, not the numbers themselves.
</context>

<claims>
1. Measurement, not enumeration, is the right basis for the check. `codex debug prompt-input` reveals the reviewer's whole instruction surface in one command, including classes nobody enumerated. Evidence: with a planted `AGENTS.md` and a planted `.agents/skills/planted/SKILL.md` in a scratch repo, the rendered prompt carried both. The existing check (SKILL.md:68) can only ever see the reviewed tree, and every source that hijacked a review on 2026-07-28 lived outside it.

2. The plugin cache must be reclassified from a non-blocking note to a blocking condition. Measured: 60 advertised skills by default, 31 of them from `~/.codex/plugins/cache`, including `superpowers:using-superpowers`, whose description alone instructs the model to invoke a skill before answering anything.

3. `--disable plugins --disable apps` is the correct lever, and `--ignore-user-config` is not. Measured: the flags take 60 skills to 29 and remove the recommended-plugins and apps blocks; `--ignore-user-config` reaches the same 31 but re-enables three skills the user had deliberately disabled via `[[skills.config]]`, because those entries live in the config file it declines to load.

4. The declared allowed residue is the empty set, and it is achievable. Measured: generating one `skills.config` disable entry per path the first probe named, then re-probing, removed all 29 remaining skills and the `<skills_instructions>` block with them. Prompt size fell from 32069 characters to 8130.

5. The design does not need to understand how `-c skills.config` merges with the user's existing entries, because the second probe asserts the outcome rather than the mechanism.

6. Every failure direction lands on blocked, and the adversarial case is the missing-skills-block-with-plugins-on fixture (plan Task 1, and plan Task 2 `test_a_missing_skills_block_with_plugins_on_blocks`). Absence of the skills block is the SUCCESS state after suppression, so absence alone must not be accepted while other evidence says suppression never ran.

7. Redirecting `CODEX_HOME` is correctly rejected for a public plugin. It needs credentials in the review home, which means either a second `codex login` shipped to every installer or copying `auth.json` per run, and it still does not close the user's own `~/.agents/skills` directory, which lives in the user home rather than the codex home. The repo already treats `CODEX_HOME` as reroute-capable: skills/multi-model-verify/references/model-prompting-notes.md:181-191.

8. Caching the remediated mirror per repo, and recording a per-repo standing decision, are both correctly rejected. Each stores a judgment that goes stale silently, which is the same failure shape as a pin that stays green while the text under it changes. That shape has cost this project twelve recorded instances.

9. The `.agents/*` pathspec in the existing enumeration is anchored at the repo root, so a nested `sub/.agents/skills/x/SKILL.md` is not listed, while `*AGENTS.md` does reach any depth. Measured: codex-cli 0.144.1 advertises a ROOT `.agents/skills` entry and does not advertise a nested one, so the gap is not reachable today. The plan records it as an accepted limit with a test rather than widening the pathspec.

10. A claim raised separately, that the enumeration misses gitignored files despite SKILL.md:69-70 saying it covers them, is false. `git ls-files --others` without `--exclude-standard` lists ignored files; measured in a scratch repo gitignoring both `AGENTS.md` and `.agents/`, the command listed both and adding `--exclude-standard` listed neither. A gitignored root `AGENTS.md` is genuinely ingested.

11. The task decomposition is right-sized and correctly ordered: parser and classifier first against recorded fixtures, then the live CLI with its measured zero, then the mirror script, then the transport pins before the skill text they lock, then the contract regions, then doctor, CI, docs and the bump.

12. The scope guard added to every brief is honestly labelled a mitigation rather than a control, and the controls are the flags plus the measured zero.

13. The mirror script's baseline and manifest rules are carried verbatim from references/backup-lane.md:223-309 rather than reinvented, so the script is an implementation of the existing contract rather than a second authority over it.

14. The fixture counts recorded in plan Task 1 are machine-specific, and the plan says a re-recording must update the assertions in the same commit rather than weakening them to tolerate both.
</claims>

<boundaries>
Already decided by the user and NOT under debate:

- Both halves are in scope: the friction fix and the client-side correctness fix.
- Approach 1, measure-then-subtract, was chosen over enumerate-then-suppress and over an isolated codex home.
- The block itself is not softened and the gate is not made optional. The user's go-ahead is still required, remediation still happens only in the mirror, and a tracked entry's deletion is still committed there.
- PowerShell for the tools, matching tools/verify-attestation.ps1. Python and pytest for the evals.
- Suppressing the global `~/.codex/AGENTS.md` is out of scope for this cycle; it is measured and recorded.

Attack the plan's soundness, its failure directions, its test design, and anything it has missed. Do not re-argue the decided items above.
</boundaries>

<final-check>List any claim you could not verify against files you actually read, as UNVERIFIED, and do not fold unverified material into your verdicts.</final-check>
