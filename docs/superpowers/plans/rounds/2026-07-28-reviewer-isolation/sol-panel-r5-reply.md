Terminal position: **FIX** for head `178853feaa2d6233fd818e7f71764db233d556a3`. The consolidation is sound, but the shared raw detector has two remaining nested false-clean forms.

## Findings

1. Important — self-closing known containers evade the shared rule.

`Get-RawContainerPair` recognizes an opener but returns it only when an exact closing literal follows (`tools/codex-context-probe.ps1:90-98`). Therefore this returns `Paired=false`:

```text
<INSTRUCTIONS><apps_instructions/></INSTRUCTIONS>
```

The quiet mask erases the self-closing tag with the `INSTRUCTIONS` body (`tools/codex-context-probe.ps1:327-373`), `Test-ContainerPresent` then returns false (`tools/codex-context-probe.ps1:101-125`), and the validating scan masks it again. I reproduced `shape_passed=true`, `Apps=false`, and zero unknown blocks under both hosts.

This contradicts the documented grammar, where a self-closing tag is a complete tagged block rather than an unpaired prose mention (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:490-502`). It can therefore reach the final clean report (`tools/codex-context-probe.ps1:970-992`).

This is a DEFECT that blocks merge.

2. Important — non-exact closing literals also evade the pair.

The ordinal, case-insensitive search begins at the correct position, but searches only for `</name>` (`tools/codex-context-probe.ps1:91-96`). This nested shape consequently passes:

```text
<INSTRUCTIONS>
<apps_instructions>live</apps_instructions >
</INSTRUCTIONS>
```

I reproduced the same result under both hosts: no raw pair, no feature, no unknown block, and `Test-PromptShape` passed. Even if the closing form is treated as an unsupported renderer change, the script promises an unreadable measurement will block rather than clean (`tools/codex-context-probe.ps1:18-23`).

Minimal correct fix for findings 1 and 2: make the raw helper recognize complete known-family surfaces, not only exact-close pairs:

- Recognize self-closing known-name tags and return them as non-exact surfaces.
- Search for a known-name closing-tag grammar after each opener, case-insensitively, retaining the actual closing literal.
- Require both literals to be exact for the dedicated parser; otherwise emit the existing non-exact-shape block.
- Preserve the current unpaired-opener behavior.

Tests should cover self-closing and whitespace-bearing closes nested inside a masked body, on both renders and across all four families.

3. Record-acceptable — paired free text does block legitimate input.

Because the raw search ignores masking and pairs each opener with any later close in the entire document (`tools/codex-context-probe.ps1:90-98`), it blocks:

- A complete attributed pair quoted in global `AGENTS.md`.
- The same pair inside a skill description.
- An opener and closer written as unrelated prose in different wrapped bodies.

That is the unavoidable safe direction once nested containers must be detected. It is a record-acceptable amendment, not a code defect. However, the design currently records this inside-body limit specifically for skills (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:394-406`) and records generic pairs only outside masked bodies (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:427-434`). It should be broadened to all four families and cross-body raw pairing.

4. Global-file safety passes, but the “whole guard” description is not literal.

For an explicit `CODEX_HOME`, candidate construction, testing, and resolution now stop inside one catchable guard (`tools/codex-context-probe.ps1:820-829`). I found no failed-check path that continues to clean.

The fallback construction from `USERPROFILE` still occurs outside that guard without `-ErrorAction Stop` (`tools/codex-context-probe.ps1:800-803`). Its failure subsequently causes the guarded candidate construction to block, so I found no false clean; nevertheless, it contradicts the comment claiming the whole measurement and every cmdlet are guarded (`tools/codex-context-probe.ps1:811-819`). Move that fallback `Join-Path` into the same `try`.

5. Minor documentation contradiction.

`Get-RawContainerPair` opens by saying it returns “The FIRST opener” (`tools/codex-context-probe.ps1:75-79`) and immediately says every paired opener is returned (`tools/codex-context-probe.ps1:85-89`). The implementation correctly examines all matches (`tools/codex-context-probe.ps1:93-98`); fix the first sentence.

The temporary-file test harness change is behavior-neutral: it writes the same body plus snippet, invokes it with `-File`, and removes it in `finally` (`evals/multi-model-verify/test_codex_context_probe.py:41-62`).

## Unverified

- I could not rerun the reported 431-test suites or live probe because Python is unavailable on PATH.
- I tested the counterexamples through the shipped functions under both PowerShell hosts, not through a complete artifact-writing probe run.
- Whether the current Codex renderer emits either changed shape was not verified; the findings concern the probe’s stated fail-closed behavior when its input shape changes.

## Verdicts

1. `Test-ContainerPresent` / `Get-RawContainerPair`: **FIX** — detect self-closing and non-exact-close nested surfaces.
2. Legitimate paired free text: **PASS**, record-acceptable amendment required.
3. Close-tag search: **FIX** — correct ordering and case handling, incomplete grammar.
4. Global-file guard: **FIX** — safety closes, but move the fallback `Join-Path` into the claimed guard.
5. Head `178853feaa2d6233fd818e7f71764db233d556a3`: **FIX**.

**OVERALL: FIX — the two false-clean container shapes must be closed before merge.**

