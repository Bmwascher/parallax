Your verifications stand, including the correction: `SKILL.md`’s stale “suppresses nothing observable” sentence is currently unlocked. That changes my recommendation materially—full measurement detail belongs only in the required backup-lane reference.

## Point 1: ship the per-call check

The strongest case against option (b) is:

- Every debate home is new; the builder refuses an existing destination and creates the skills directory empty. [new-kimi-lane-home.ps1:607](/C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-home.ps1:607) [new-kimi-lane-home.ps1:900](/C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-home.ps1:900)
- The reviewer denies `Skill`, and the lane verifies its prompt and tool surface. [kimi-reviewer-agent.md:10](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/kimi-reviewer-agent.md:10) [backup-lane.md:263](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/backup-lane.md:263)
- A pre-call listing is not atomic with client startup; another process could populate the directory after the check. Thus “verified control” must still mean “verified at the dispatch boundary,” not an absolute filesystem guarantee.
- A prose-only driver check can itself be skipped unless pinned and recorded.

That is not enough to defeat (b). I would ship **(b)**. The repo cannot knowingly leave the flag’s only measured precondition unmeasured while calling the flag a control. The builder’s one-time construction fact is explicitly weaker than the per-call evidence standard already used elsewhere. [backup-lane.md:186](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/backup-lane.md:186)

The check belongs in the **dispatch step in `references/backup-lane.md`, immediately before every fresh or resumed client call**:

> Immediately before EVERY fresh or resumed client call, enumerate `<debate-home>/skills/` with hidden entries included and a terminating read. Dispatch only if the path is an existing directory and the enumeration contains exactly zero entries. An absent, unreadable, non-directory or non-empty path makes the lane UNAVAILABLE before the client runs. Record `skills-dir precondition: empty` for that call.

Not the builder: it runs only once before round 1. [backup-lane.md:47](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/backup-lane.md:47)

Not the current validator: it runs after the client call and ends by reporting the result and next state. Discovering contamination there would discard the reply but could not undo context exposure. [read-kimi-round-evidence.ps1:891](/C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:891)

Place the requirement adjacent to the two transport commands at [backup-lane.md:24](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/backup-lane.md:24), and cross-reference it from the pre-call evidence rule. The test must first pin all four failure directions—absent, unreadable, wrong type, non-empty—so this is visibly a check that can fail.

## Point 2: withdraw the region rename

I withdraw `skills-dir-conditional-control`.

The frozen names are explicit at [2026-08-03-home-skills-root-probe.md:133](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:133), and Task 5 already explains that the second region binds the disposition’s reach. [2026-08-03-home-skills-root-probe.md:597](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:597)

The newly measured flag behavior, its empty-directory precondition, its per-call verification requirement, and the version-bound system-prompt result are all limits on what “reachable” and “controlled” mean. They fit `home-skill-root-disposition-limit` without semantic strain. Renaming would be unforced drift.

Use exactly:

- `home-skill-root-disposition`
- `home-skill-root-disposition-limit`

## Point 3: minimize `SKILL.md`

Current on-disk body length is 20,483 normalized characters, yielding the linter’s estimate of 5,120 tokens. The linter computes `len(body) // 4` and warns above 5,000. [skill_lint.py:249](/C:/Users/Brandon/Documents/parallax/evals/tools/skill_lint.py:249)

Replace [SKILL.md:67](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:67) through the end of the stale flag paragraph with exactly:

```markdown
   kimi-code also documents `.kimi-code/skills/` as a project-level
   discovery root, so the sweep covers it. Backup-lane discovery controls
   and their measured limits are specified in references/backup-lane.md.
```

That is the right allocation. `SKILL.md` retains only why preflight 3 includes `.kimi-code/`; the required reference owns flag behavior, home-root reachability, per-call emptiness, and version limits. `backup-lane.md` is already declared required reading before any backup round. [SKILL.md:17](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:17)

Because the stale sentence is unlocked, there is no old SKILL pin to remove. Tests-first should add one direct pin for this short routing text before changing the document; no new SKILL contract region is warranted.

## Point 4: adopt the readout, version-bound

It belongs in `home-skill-root-disposition-limit`, because it limits why the reviewer deny list is sufficient today rather than establishing root reachability itself.

Exact sentence:

> On kimi-code 0.31.1, `systemPromptChars` stayed equal to the selected agent body in every cell, including both loaded-canary cells: the measured delivery path was `skill_activation`, not system-prompt injection, so the `Skill` deny list controls that path, while a future system-prompt injection would instead have to be rejected by the lane’s system-prompt equality checks.

The five-cell evidence supports that bounded statement: lengths remained constant across agents, homes, and canary states, while the positive delivery appeared separately as `skill_activation`. [probe-record.md:74](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:74) [probe-record.md:85](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:85) [probe-record.md:138](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:138)

It does **not** support “kimi-code never injects skills into the system prompt.” The version, agent bodies, roots, and observed delivery shape must remain in the sentence.

## Still unresolved

- Whether the per-call emptiness result needs structured machine-readable evidence or a pinned debate-record line.
- Whether the historical probe record’s overbroad “REPLACE discovery” and unconditional “verified control” language receives a correction note or remains an immutable historical record.
- The complete revised bodies and corresponding whole-region pins for the two frozen contract regions.

