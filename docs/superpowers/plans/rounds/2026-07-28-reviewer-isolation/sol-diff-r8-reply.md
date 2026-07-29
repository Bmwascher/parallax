Terminal position: the implementation is behaviorally sound within the specified grammar, but the branch still contains current documentation that describes superseded behavior. That documentation defect should be fixed before merge; it is not a record-acceptable limitation.

## Fix attack results

1. **Quiet masking does not hide a relevant malformed outer tag.**

The quiet pass masks only exact, ordered 1/1 spans; missing, duplicate, or reversed boundaries are skipped without mutation ([tools/codex-context-probe.ps1:228](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:228), [tools/codex-context-probe.ps1:241](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:241), [tools/codex-context-probe.ps1:247](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:247), [tools/codex-context-probe.ps1:259](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:259)).

A malformed tag inside an accepted known body is hidden, but that is intentional: the guarantee excludes content inside masked known-container bodies ([design:447](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:447), [design:449](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:449)). A malformed outer tag without such a valid containing span remains visible to exactness at lines 326–332. PASS.

2. **Quiet masking cannot convert real boundary ambiguity into success.**

The validating pass restarts from original `$text`, not `$bodyMasked` ([tools/codex-context-probe.ps1:326](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:326), [tools/codex-context-probe.ps1:337](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:337)). Therefore anything skipped quietly is independently recounted and throws during validation. The only erased delimiters are those inside another accepted known body, which is the declared masking boundary. PASS.

3. **The ordered close search is correct for the requested cases.**

The search starts immediately after the complete opener and uses ordinal comparison ([tools/codex-context-probe.ps1:355](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:355)).

Direct function probes confirmed:

- A self-closing tag at end-of-text remains detected.
- Two ordered instances of one unknown name remain detected.
- A paired first instance followed by an unclosed second instance remains blocked because the valid first pair is sufficient.
- An unknown block wrapping a known container remains detected.
- A reverse-order close/open sequence is ignored as prose.
- A close lying inside a masked known body disappears. That creates no valid outer pair; crossing a known-body boundary is outside the declared structural guarantee.

The positive and negative ordering directions are also locked by separate tests ([test_codex_context_probe.py:995](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_context_probe.py:995), [test_codex_context_probe.py:1009](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_context_probe.py:1009)). PASS.

4. **No remaining false-clean path found within the specified grammar.**

Both renders still execute the complete shape check; clean remains reachable only after suppression, absence of the second skills block, successful artifact production, and validated artifact fields. I found no parser shape within the frozen `[A-Za-z][A-Za-z0-9_.:\-]*` grammar that bypasses those checks.

## Remaining defect

**DEFECT — current comments and one failure-table row describe obsolete behavior. Must fix before merge.**

- The script says exactness runs “ON THE RAW TEXT, BEFORE MASKING,” but it now runs on `$bodyMasked` ([tools/codex-context-probe.ps1:284](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:284), [tools/codex-context-probe.ps1:326](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:326)).
- It says the general scan “is line-anchored by design,” while the current regex is unanchored ([tools/codex-context-probe.ps1:293](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:293), [tools/codex-context-probe.ps1:345](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:345)).
- It says the pair requirement keeps prose out, while the corrected design explicitly says ordered-pair or self-closing prose outside masked bodies blocks ([tools/codex-context-probe.ps1:339](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:339), [design:456](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:456)).
- The inline-unknown test repeats that obsolete pair/prose claim ([test_codex_context_probe.py:961](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_context_probe.py:961), [test_codex_context_probe.py:964](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_context_probe.py:964)).
- The failure table says every non-exact known tag appearing anywhere blocks, but non-exact quotations inside validated masked bodies are now deliberately ignored ([design:306](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:306), [test_codex_context_probe.py:981](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_context_probe.py:981)).

These are fixable false descriptions of current code, not inherent flattened-text ambiguities. Update them to describe the quiet-mask → exactness → validating-mask pipeline and qualify exactness as applying outside unambiguous masked bodies.

## Unverified

I did not rerun the 411-test dual-host suite or live probes. Their results are recorded at [checkpoint:434](C:/Users/Brandon/Documents/parallax/.git/parallax/application-checkpoints/20260728-1552-22dd63311a33.md:434). I directly exercised the current parser functions for the requested adversarial shapes.

## Verdicts

1. **PASS** — implementation fidelity is complete subject to A1–A14.
2. **PASS** — A14 accurately records this round’s behavioral deviations ([plan:2711](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2711)).
3. **PASS** — verified-override dispatch remains intact.
4. **PASS** — no remaining false-clean path found within the specified parser grammar.
5. **PASS** — contract-region coverage is unaffected.
6. **PASS** — the whole-branch-review dispositions remain supported.
7. **FIX** — correct the obsolete script/test comments and qualify the known-tag failure-table row.

**OVERALL: FIX — no behavioral code defect remains, but the branch should not merge until its current documentation matches the implemented masking and scanning pipeline.**