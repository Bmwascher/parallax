Two material defects remain: one false block introduced this round and one pre-existing false-clean bypass exposed by the attack.

## Findings

1. **DEFECT — raw exactness rejects legitimate user-authored text.**

`<INSTRUCTIONS>` contains verbatim user-authored material and is deliberately masked to prevent that material being interpreted as outer prompt structure ([tools/codex-context-probe.ps1:194](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:194), [tools/codex-context-probe.ps1:195](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:195)). The new exactness scan instead examines raw text before masking ([tools/codex-context-probe.ps1:261](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:261), [tools/codex-context-probe.ps1:297](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:297)).

Consequently, this legitimate house rule blocks:

```text
<INSTRUCTIONS>
Never emit <skills_instructions version="2">.
</INSTRUCTIONS>
```

The regex recognizes the quoted tag and the strict allowlist rejects it ([tools/codex-context-probe.ps1:298](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:298), [tools/codex-context-probe.ps1:299](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:299)). I reproduced that directly against the current function. The existing regression only covers a quoted **exact** literal, so it does not exercise this shape ([evals/multi-model-verify/test_codex_context_probe.py:786](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_context_probe.py:786), [evals/multi-model-verify/test_codex_context_probe.py:797](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_context_probe.py:797)).

Specific fix: validate the outer `INSTRUCTIONS` boundary, blank its body, then apply known-tag exactness to the remaining text. A malformed actual outer opener must remain visible, while malformed tag prose inside the validated user body must not.

2. **DEFECT — an inline unknown container remains a false-clean path.**

The unknown-block scan is still anchored to the beginning of a line:

```powershell
(?m)^[ \t]*<...
```

([tools/codex-context-probe.ps1:308](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:308)). Therefore:

```text
prefix <memories_instructions>x</memories_instructions>
```

returns zero unknown blocks. I reproduced that directly against the current function. Known-tag exactness cannot catch it because it scans only known names ([tools/codex-context-probe.ps1:294](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:294), [tools/codex-context-probe.ps1:297](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:297)).

This is a genuine clean/exit-0 route: both renders call `Test-PromptShape`, but that function blocks only what `Get-UnknownPromptBlock` returns ([tools/codex-context-probe.ps1:411](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:411), [tools/codex-context-probe.ps1:420](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:420)); the second pass proceeds through that check at line 607 and reaches the clean report at lines 701–723 ([tools/codex-context-probe.ps1:607](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:607), [tools/codex-context-probe.ps1:701](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:701), [tools/codex-context-probe.ps1:723](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:723)).

Specific fix: after masking known bodies, scan unknown paired/self-closing tags anywhere, not only at line starts. The existing unpaired-prose exemption remains possible because it already requires a matching close or self-closing form ([tools/codex-context-probe.ps1:312](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:312), [tools/codex-context-probe.ps1:313](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:313)). Add first- and second-pass inline-unknown tests.

## Requested attacks

1. **Count/masking order:** no additional structural defect found. Counts are taken progressively over `$masked`, and bodies are erased before later containers are counted ([tools/codex-context-probe.ps1:214](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:214), [tools/codex-context-probe.ps1:218](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:218), [tools/codex-context-probe.ps1:242](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:242)). Proper nesting is masked; crossing boundaries leave a later unmatched delimiter and block.

   One residual is record-acceptable: a solitary exact quoted open/close pair outside a masked body is indistinguishable from a real container and will be treated as one. The design discusses quoted-delimiter ambiguity, but the implementation blocks only when counts differ from 1/1 ([tools/codex-context-probe.ps1:226](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:226), [docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:369](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:369)). This limitation should be stated explicitly; it is not independently fixable from flattened text.

2. **Raw exactness:** false positive confirmed; DEFECT as above.

3. **Joined-entry accepted limit:** accurately stated. Detection is line-local and requires a complete earlier `SKILL.md` marker followed by another entry start ([tools/codex-context-probe.ps1:113](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:113), [tools/codex-context-probe.ps1:118](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:118)). Other malformed entry lines are separately covered by the whole-grammar rule ([docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:307](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:307)). PASS.

4. **Remaining false clean:** confirmed—the inline unknown-container bypass above.

5. **Accepted limits/history:** the joined-entry limit and “five rows covering six findings” history are accurate ([docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:312](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:312), [docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:319](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:319), [docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:384](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:384)). Amendment 4 also records the dispositions claimed in the brief ([checkpoint:334](C:/Users/Brandon/Documents/parallax/.git/parallax/application-checkpoints/20260728-1552-22dd63311a33.md:334), [checkpoint:337](C:/Users/Brandon/Documents/parallax/.git/parallax/application-checkpoints/20260728-1552-22dd63311a33.md:337)).

   Documentation still falsely states that an unrecognized outer block on either pass blocks ([docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:334](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:334)), and the script header’s “unreadable measurement is never reported clean” is likewise disproved ([tools/codex-context-probe.ps1:18](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:18)).

## Unverified

I did not rerun the full 405-test dual-host gates or the live probe. The checkpoint records those results at [checkpoint:342](C:/Users/Brandon/Documents/parallax/.git/parallax/application-checkpoints/20260728-1552-22dd63311a33.md:342). The real-prompt occurrence counts and inline `multi_agent_mode` measurement were not independently repeated.

## Verdicts

1. **PASS** — fidelity is implemented subject to recorded amendment A12 ([plan:2709](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2709)).
2. **PASS** — this round’s deviations are recorded in A12.
3. **PASS** — verified artifact generation and per-dispatch hash verification remain intact ([tools/codex-context-probe.ps1:641](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:641), [skills/multi-model-verify/SKILL.md:180](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:180), [skills/multi-model-verify/SKILL.md:225](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:225)).
4. **FIX** — ignore malformed known tags inside a validated user instruction body; detect paired/self-closing unknown blocks inline on both passes.
5. **PASS** — contract declarations remain the six claimed IDs ([test_contract_coverage.py:642](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_contract_coverage.py:642), [test_contract_coverage.py:647](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_contract_coverage.py:647)).
6. **PASS** — no Round-6 regression to the earlier review dispositions; provider paths remain resolved once ([tools/new-review-mirror.ps1:157](C:/Users/Brandon/Documents/parallax/tools/new-review-mirror.ps1:157)).
7. **FIX** — correct the unrecognized-outer-block and universal fail-closed claims; record the solitary 1/1 quoted-pair ambiguity.

**OVERALL: FIX — the inline unknown block is a merge-blocking false clean, and raw exactness is a merge-blocking legitimate-input rejection.**