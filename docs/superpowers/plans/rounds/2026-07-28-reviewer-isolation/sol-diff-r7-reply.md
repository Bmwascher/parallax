Two safe-direction defects remain. I found no new false-clean path within the frozen tag grammar.

## Findings

1. **DEFECT — two-stage masking fixes global instructions but not other free-text known bodies.**

Stage 1 masks only `INSTRUCTIONS`; exactness then scans that partially masked text, and every other known body is masked afterward ([tools/codex-context-probe.ps1:308](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:308), [tools/codex-context-probe.ps1:312](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:312), [tools/codex-context-probe.ps1:320](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:320)).

A skill description is explicitly free text ([tools/codex-context-probe.ps1:545](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:545)), so this legitimate entry blocks:

```text
<skills_instructions>
- example: Never emit <apps_instructions version="2">. (file: C:/x/SKILL.md)
</skills_instructions>
```

I reproduced the throw against the current function. The tag is interpreted as malformed outer structure at lines 312–317 before the skills body can be masked.

Unknown paired tags in descriptions are handled correctly: stage 2 masks the skills body before the general scan at lines 321–330. The defect is specifically the earlier known-tag exactness pass.

Specific fix: build non-throwing masks for every known container having an unambiguous exact 1/1 span, run exactness on that body-masked text, then run the existing throwing count validation. A malformed actual outer opener has no valid exact span and remains visible, while arbitrary description text is hidden.

2. **DEFECT — “pair” means a close anywhere, including before the opener.**

The scanner tests:

```powershell
$masked.Contains("</" + $name + ">")
```

without requiring the close to follow the matched opener ([tools/codex-context-probe.ps1:329](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:329), [tools/codex-context-probe.ps1:334](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:334)).

I reproduced that this legitimate explanatory prose is classified as an unknown block:

```text
End with </example>; start with <example>
```

That is not an open/close pair in document order. It is a new false positive exposed by removing the line anchor.

Specific fix: require an ordinal closing-literal match after `$m.Index + $m.Length`. Add the reverse-order prose case as a regression test.

## Requested attacks

1. **Stage 1 masking:** it correctly hides malformed known-tag quotations inside `INSTRUCTIONS`, and genuine malformed outer tags remain visible. A future renderer-defined nested structure inside `INSTRUCTIONS` would be hidden, but the stated guarantee is limited to outer blocks ([design:447](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:447)). The undisclosed free-text skill-description false positive above is the material defect.

2. **Unanchored scan:** unknown tags in skill descriptions and other successfully validated known bodies are masked. An ordered paired tag or self-closing tag in an unmasked fenced example does block. That is indistinguishable from an actual inline surface and is record-acceptable, but should be added to Accepted limits. The design currently records only the equivalent known-container-pair ambiguity ([design:384](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:384)).

3. **Pair requirement:** reverse-order matching is a fixable defect. A self-closing form in prose is inherently indistinguishable and record-acceptable. The existing tests intentionally classify self-closing tags as blocks ([test_codex_context_probe.py:238](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_context_probe.py:238), [test_codex_context_probe.py:244](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_context_probe.py:244)).

4. **Remaining false clean:** none found within the frozen `[A-Za-z][A-Za-z0-9_.:\-]*` tag grammar, which the plan specifies literally ([plan:535](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-28-reviewer-isolation.md:535)). Both findings above block too much; neither reaches clean.

5. **Documentation:**

   - The accepted-limit text still says a block opens “a line,” although the implementation is now deliberately unanchored ([design:447](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:447), [tools/codex-context-probe.ps1:329](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:329)).
   - The failure row says the pair requirement keeps prose out, which is false for ordered paired prose, self-closing prose, and currently reverse-order prose ([design:334](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:334)).
   - Amendment A13 is recorded before A12 rather than in numeric order ([plan:2709](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2709), [plan:2710](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2710)).
   - The other new accepted limit is supported: the count rule accepts a solitary 1/1 known pair ([tools/codex-context-probe.ps1:228](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:228), [design:384](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:384)).

## Unverified

I did not rerun the full 408-test dual-host suite or live probes. Their recorded results are at [checkpoint:390](C:/Users/Brandon/Documents/parallax/.git/parallax/application-checkpoints/20260728-1552-22dd63311a33.md:390). I directly exercised the current parser functions for the adversarial shapes above.

## Verdicts

1. **PASS** — implementation fidelity remains recorded under A13.
2. **PASS** — the behavioral deviations are declared; reorder A12/A13 as record cleanup.
3. **PASS** — verified-override dispatch is unaffected.
4. **FIX** — mask all unambiguous known-container bodies before exactness, and require unknown closing tags to follow their opener.
5. **PASS** — contract-region coverage is unaffected.
6. **PASS** — no regression to the whole-branch-review dispositions.
7. **FIX** — remove the stale line-start wording, narrow the claim that pairing excludes prose, record paired/self-closing prose as an accepted limit, and reorder A12/A13.

**OVERALL: FIX — two parser false positives require code changes before merge; no remaining false-clean path was found within the specified grammar.**