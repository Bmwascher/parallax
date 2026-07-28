## Findings

1. **Important — a non-line-start attributed known block remains a false-clean bypass.** The exact-literal rule is reached only through a regex anchored after spaces or tabs at the start of a line ([tools/codex-context-probe.ps1:226](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:226)). Consequently:

   ```text
   prefix <skills_instructions version="2">
   ...29 entries...
   </skills_instructions>
   ```

   is invisible to the exact skills parser and to the known-name check. On the second pass, `BlockPresent` is false and zero entries are accepted as absence ([tools/codex-context-probe.ps1:524](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:524), [tools/codex-context-probe.ps1:529](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:529)).

   The design limits the general unknown-block grammar to blocks “opening a line” ([reviewer-isolation-design.md:389](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:389)), so this is not frozen-plan drift. It is nevertheless a correctness defect: a targeted scan for known names can catch this tagged form without broadening detection to arbitrary prose.

   Fix: after masking legitimate container bodies, scan for every known opening-name prefix anywhere, not only through the general line-anchored outer-block grammar.

2. **Important — hash generation remains outside the artifact try/catch.** Encoding, writing, and resolving are now correctly guarded ([tools/codex-context-probe.ps1:554](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:554)). But `SHA256.Create()` and `ComputeHash()` remain after that catch ([tools/codex-context-probe.ps1:566](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:566)). A non-terminating failure there can leave `override_sha256` empty and continue into `status: clean` and exit 0 ([tools/codex-context-probe.ps1:605](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:605)).

   The dispatch preamble would still reject an empty/wrong hash, so I found no route to dispatch an unverified value. The probe’s clean result is nonetheless false.

   Fix: include hash creation and computation in the same try/catch and validate both a nonempty resolved artifact path and a 64-character lowercase hash before leaving the suppression branch.

3. **Minor — masking order can block legitimate text inside the global instruction body.** `KnownContainers` processes `skills_instructions`, plugin/apps blocks, and recommended plugins before `INSTRUCTIONS` ([tools/codex-context-probe.ps1:158](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:158)). Each type is searched before the later container’s body has been masked ([tools/codex-context-probe.ps1:172](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:172)).

   Therefore, a global `AGENTS.md` containing a literal such as `` `<skills_instructions>` `` without a matching close is mistaken for an unterminated outer container and blocks at [tools/codex-context-probe.ps1:181](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:181). That is exactly the legitimate-body class masking is intended to protect; the design explicitly permits tag-looking text inside the global instruction body ([reviewer-isolation-design.md:403](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:403)).

   Fix: mask containers in prompt/outermost-span order, or at minimum mask the user-controlled `INSTRUCTIONS` body before examining container literals inside it. Add paired and unpaired known-literal cases inside that body.

4. **Minor — a legitimate description containing `(file: ` is rejected.** The audit requires exactly one marker on the entire line ([tools/codex-context-probe.ps1:109](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:109)). Skill descriptions are free text, so a description mentioning `(file: ` plus the renderer’s actual final marker sets `Malformed` and blocks.

   Fix: parse the final marker as the path delimiter while separately detecting a second rendered entry. A legitimately wrapped entry correctly blocks as an unrecognized rendering rather than being silently dropped: its first entry-looking line fails the full grammar and sets `Malformed` ([tools/codex-context-probe.ps1:101](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:101)).

## Specific attack results

- Case changes and whitespace inside a known opening tag block intentionally because the dedicated parsers are exact and cannot understand those forms. Ordinary indentation and whitespace after `>` pass: the regex admits indentation and `Trim()` removes it before the case-sensitive literal comparison ([tools/codex-context-probe.ps1:226](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:226), [tools/codex-context-probe.ps1:230](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:230)).
- An exact opener with a non-exact closing tag does not bypass the guard: `Hide-KnownContainer` finds the opener, fails to find the exact close, and throws ([tools/codex-context-probe.ps1:177](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:177)). The bypass requires an opening form that evades both the exact parser and line-anchored scanner.
- `Malformed` is explicitly checked only on pass 1 ([tools/codex-context-probe.ps1:447](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:447)). This is not a separate defect: any exact skills block on pass 2 blocks solely because it remains present ([tools/codex-context-probe.ps1:526](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:526)). An attributed line-start block is rejected by `Test-PromptShape` before `Malformed` matters.
- A8 now distinguishes the provider-path fix from `-SkipProbe`, and A9 accurately records this round’s interface widening and three changes ([reviewer-isolation.md:2705](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2705)).
- README and the rounds README are corrected as requested ([README.md:165](C:/Users/Brandon/Documents/parallax/README.md:165), [rounds/README.md:10](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/2026-07-28-reviewer-isolation/README.md:10)).

## Documentation honesty

Three active overclaims survived the README correction:

- SKILL.md still says the probe “sorts every instruction source it reveals,” although only parsed skill entries are directory-classified ([SKILL.md:120](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:120), [tools/codex-context-probe.ps1:457](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:457)).
- The probe’s own header makes the same “classify every instruction source” claim ([tools/codex-context-probe.ps1:1](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:1)).
- The design says every named block with an unrecognized shape and every failure direction blocks ([reviewer-isolation-design.md:288](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:288), [reviewer-isolation-design.md:298](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:298)); the inline attributed-tag and hash paths refute those statements at this head.

Narrow the first two to “classifies every advertised skill and checks named instruction/feature blocks.” The latter claims become honest when Findings 1 and 2 are fixed.

## Verdicts

1. **PASS** — the record now explicitly qualifies fidelity as “implemented subject to the amendments” and identifies A2–A6 as deviations ([reviewer-isolation.md:2690](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2690)).

2. **PASS** — A8 and A9 now disclose the relevant post-freeze changes with their evidence. The new findings above are defects in A9’s implementation, not undeclared existing deviations.

3. **PASS** — the exact-bytes dispatch identity still holds. Hash failure can falsely report clean, but the per-round preamble recomputes and compares the artifact hash before passing the in-memory value, so it cannot dispatch through that failure ([SKILL.md:178](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:178), [SKILL.md:223](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:223)).

4. **FIX** — catch and validate hash generation; catch known-name tags outside the general line-anchored grammar; repair outer-container masking order; parse the final file marker without forbidding that text in descriptions.

5. **PASS** — no contract region or declaration changed this round; the six-region declaration and whole-body pins remain intact ([test_contract_coverage.py:641](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_contract_coverage.py:641), [test_multi_model_verify.py:352](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_multi_model_verify.py:352)).

6. **PASS** — this round does not invalidate the five whole-branch-review dispositions. Provider-path resolution and the explicitly UNVERIFIED model/sandbox parity statement remain correct ([new-review-mirror.ps1:146](C:/Users/Brandon/Documents/parallax/tools/new-review-mirror.ps1:146), [reviewer-isolation-design.md:181](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:181)).

7. **FIX** — narrow the surviving SKILL.md, source-header, and design overclaims identified above.

These are implementation/documentation defects, not merely record-acceptable amendments. A9 itself is a record-acceptable and accurate amendment; subsequent fixes that further widen the frozen interface should be recorded as the next amendment.

## UNVERIFIED

- Claim 1’s historical tests-first chronology remains unverifiable from final files and same-commit history.
- I did not rerun the mutation-requiring 395-test, gate, or live-probe commands in the read-only workspace.
- Whether model or sandbox selection changes rendered prompt content remains explicitly UNVERIFIED by the design ([reviewer-isolation-design.md:184](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:184)).

**OVERALL: FIX**