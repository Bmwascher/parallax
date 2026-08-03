<role>
You are the cross-vendor reviewer in a two-advisor debate. We are equal weight. Refute me where you can. Ground every claim in a file and line you actually read in this repository. Say plainly when you are reasoning from text rather than from evidence. Do not agree in order to be agreeable.
</role>

<repo>
C:\Users\Brandon\Documents\parallax is a Claude Code plugin that provides cross-model verification. It is developer tooling, not a game addon. Ignore any addon conventions you may infer.
</repo>

<background>
The plugin has a BACKUP reviewer lane: Kimi K3 driven through the kimi-code CLI. That client discovers "skills" (directories holding a SKILL.md whose text is injected into the model's context) from FOUR roots. Three are controllable. The fourth, ~/.agents/skills/, lives in the user's own home, is not relocated by KIMI_CODE_HOME, and nothing the lane runs removes it. It holds 27 real skill directories on this machine.

Until today the lane contract called that root "unprobed territory". An earlier probe was CONFOUNDED: canaries were planted at the two PROJECT roots only, and the reviewer agent DENIES the Skill tool, so "no skills available" could not be told apart from "root not read".

A frozen plan, docs/superpowers/plans/2026-08-03-home-skills-root-probe.md, built a probe that breaks the confound. It ran live today. The full record is docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md. READ IT FIRST.
</background>

<measurement>
Five cells, everything constant except two variables, plus a resumed calibration. All eight client calls returned status clean from the lane's own round validator; brief hash matched; route verified client-side.

Cell D: probe agent that ALLOWS Skill, --skills-dir OMITTED, canary planted in ~/.agents/skills/. The wire carries a tool.call named Skill with args.skill = parallax-home-root-canary, a matching tool.result, and a context.append_message whose origin.kind is skill_activation and whose skillPath names the canary SKILL.md, carrying the canary body and its per-run nonce.

Cell C: identical except --skills-dir <debate-home>/skills was PASSED, and the builder creates that directory EMPTY. Result: isError true, "Skill not found in the current skill listing". This equals the calibrated not-found oracle from cell E2 exactly, under a frozen ordinal comparison of the complete event.result payload after one substitution of the requested identifier.

Cell E: canary in <debate-home>/skills, --skills-dir OMITTED. Loaded.

Cells A and B: the REAL reviewer agent, which denies Skill. Canary present in B, absent in A. Neither fires on either primary readout.

systemPromptChars was constant at 462 for the reviewer agent and 1195 for the probe agent, across five separate throwaway homes and every canary condition.
</measurement>

<my_claims>
1. ~/.agents/skills/ is REACHABLE by the kimi-code client. Measured, not unprobed.
2. --skills-dir REPLACES discovery rather than adding to it, so it suppresses all four roots.
3. The flag is a control only CONDITIONALLY: --skills-dir <debate-home>/skills suppresses the home root only because that directory is EMPTY, and I can find no per-round check that it is still empty at dispatch.
4. The lane as it SHIPS has no hole today, held by two independent things: Skill is on the reviewer agent's disallowedTools deny list, and the flag points discovery at an empty directory.
</my_claims>

<questions>
<q1>
Attack my four claims. I believe at least one of them states more than the evidence supports. Find it and say exactly where the reach exceeds the measurement. Do not simply agree with all four.
</q1>

<q2>
Two places assert something the measurement contradicts.

skills/multi-model-verify/SKILL.md near line 69 says a 2026-07-31 probe found runs with and without the flag "indistinguishable", and that "that flag suppresses nothing observable".

skills/multi-model-verify/references/backup-lane.md near lines 345 to 354 says "--skills-dir is a MITIGATION whose effect is UNMEASURABLE in this configuration, not a control", and "Keep passing --skills-dir ... but claim nothing for it".

Both were TRUE of the configuration they were measured in, where Skill was denied so nothing could be invoked either way. Give me exact replacement wording for each, not direction. Constraints: files under references/ are checked for the ABSENCE of backslashes; text inside contract:start and contract:end markers must sit WHOLE inside a single test pin.
</q2>

<q3>
backup-lane.md near line 341 instructs: "Enumerate that root before round 1 and record what it holds; a non-empty one is unprobed territory, recorded as such rather than assumed absorbed by the tool allowlist."

It is no longer unprobed. Should the enumeration survive at all, and what should the recorded disposition say? Argue BOTH sides before recommending.
</q3>

<q4>
Three branches of the plan's own outcome gate turn on "a matching tool.result carrying the nonce". No tool.result ever carries a skill body on this client, in any cell, including both positive controls. Skill's result is a fixed confirmation string; the body arrives as the separate skill_activation message.

The cause is a generalization ACROSS TOOLS: the plan cites a committed fixture whose tool.result is a Grep result, where the raw output genuinely IS the answer, and assumed a Skill result would behave the same.

Give me wording for how that clause should have read. Then SEARCH, do not opine: does the same generalization sit anywhere else in this repository's oracles, meaning any check that reads a tool's EFFECT out of that tool's own result record? Name files and lines. If you find none, say you looked and where.
</q4>

<q5>
Given all of the above, what is the smallest change that leaves the lane honestly documented? I am specifically interested in whether the contract should merely DESCRIBE the unverified precondition in claim 3, or should REQUIRE a check for it before every call. Argue the strongest case AGAINST adding a check, then tell me which you would ship.
</q5>
</questions>

<constraints>
Do not propose new probes or new features beyond what these questions ask. This debate settles contract text and scope.
End your reply with a short list of the points you consider unresolved.
</constraints>
