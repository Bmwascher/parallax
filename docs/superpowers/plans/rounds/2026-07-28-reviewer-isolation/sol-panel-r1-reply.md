Terminal review is against pinned head `50c82029f178c747467e5a597b281731f70e4188`. The branch is mergeable.

## Fix verification

All five sites now describe the implemented pipeline correctly:

1. The probe comment names the exact sequence: quiet mask → exactness → validating mask → scan, and correctly places exactness on `$bodyMasked` ([tools/codex-context-probe.ps1:284](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:284), [tools/codex-context-probe.ps1:286](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:286), [tools/codex-context-probe.ps1:337](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:337)).

2. The line-anchor history is now past tense and distinguishes the known-tag rule’s round-3 change from the general scan’s round-6 change ([tools/codex-context-probe.ps1:303](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:303), [tools/codex-context-probe.ps1:310](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:310)).

3. The prose explanation correctly attributes protection primarily to masking and records that ordered-pair or self-closing prose outside masked bodies blocks ([tools/codex-context-probe.ps1:350](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:350), [tools/codex-context-probe.ps1:354](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:354), [tools/codex-context-probe.ps1:360](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:360)).

4. The inline-unknown test comment makes the same accurate distinction and points to the recorded accepted limit ([test_codex_context_probe.py:961](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_context_probe.py:961), [test_codex_context_probe.py:964](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_codex_context_probe.py:964)).

5. The failure-table row now limits known-tag exactness to text outside unambiguously masked bodies and explicitly explains why quotations inside `AGENTS.md` or skill descriptions are ignored ([reviewer-isolation-design.md:306](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:306)).

No site is newly wrong.

## Collateral

Commit `50c8202` changes comments and prose only in the script, test, and design. No executable PowerShell statement, Python assertion, fixture, or behavioral configuration changed. The other additions are retained round-8 brief/header/reply artifacts. No behavioral collateral found.

## Override invariant

No bypass found.

The probe creates one `$override` and uses that same value for the suppression measurement ([tools/codex-context-probe.ps1:649](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:649), [tools/codex-context-probe.ps1:656](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:656)). Only after the successful second measurement does it strictly encode that value, write those exact bytes, and hash the same byte array ([tools/codex-context-probe.ps1:667](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:667), [tools/codex-context-probe.ps1:701](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:701), [tools/codex-context-probe.ps1:708](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:708)).

For round 1, SKILL.md:

- reads the artifact once as bytes;
- hashes those bytes;
- rejects a mismatch;
- strictly decodes those same in-memory bytes;
- passes the resulting value to `-c`.

([SKILL.md:180](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:180), [SKILL.md:181](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:181), [SKILL.md:183](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:183), [SKILL.md:184](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:184)).

Every resume repeats the complete operation independently ([SKILL.md:225](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:225), [SKILL.md:229](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:229), [SKILL.md:232](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:232)). Mutation of the file after the read cannot change the already-decoded in-memory value.

## Fail-closed audit

No unmade, failed, or unreadable measurement can reach `clean`:

- First-pass failure or unreadable output blocks ([tools/codex-context-probe.ps1:548](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:548), [tools/codex-context-probe.ps1:555](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:555)).
- Missing or unreadable first-pass skills block blocks ([tools/codex-context-probe.ps1:568](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:568), [tools/codex-context-probe.ps1:578](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:578)).
- Suppression without an artifact path blocks; failed or unreadable second measurement blocks ([tools/codex-context-probe.ps1:644](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:644), [tools/codex-context-probe.ps1:657](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:657), [tools/codex-context-probe.ps1:661](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:661)).
- A present second-pass skills block blocks regardless of parsed count ([tools/codex-context-probe.ps1:670](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:670), [tools/codex-context-probe.ps1:673](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:673)).
- Artifact write, resolution, or hash failure blocks, and both resulting fields are explicitly validated ([tools/codex-context-probe.ps1:702](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:702), [tools/codex-context-probe.ps1:717](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:717), [tools/codex-context-probe.ps1:721](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:721)).
- A run without suppression exits 1 as `measured-only`; the clean report is below that exit ([tools/codex-context-probe.ps1:734](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:734), [tools/codex-context-probe.ps1:758](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:758), [tools/codex-context-probe.ps1:761](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:761)).

## Unverified

I did not rerun the full 411-test dual-host suite or live probe. Those results remain recorded in the checkpoint at [checkpoint:438](C:/Users/Brandon/Documents/parallax/.git/parallax/application-checkpoints/20260728-1552-22dd63311a33.md:438) and [checkpoint:444](C:/Users/Brandon/Documents/parallax/.git/parallax/application-checkpoints/20260728-1552-22dd63311a33.md:444).

## Verdicts

1. **PASS** — plan fidelity is complete subject to recorded amendments A1–A14.
2. **PASS** — deviations are fully declared.
3. **PASS** — the verified override is the dispatched override.
4. **PASS** — no false-clean measurement path found.
5. **PASS** — contract coverage is unchanged and intact.
6. **PASS** — whole-branch-review dispositions remain supported.
7. **PASS** — the five obsolete documentation sites are corrected with no new overclaim.

**OVERALL: PASS — head `50c82029f178c747467e5a597b281731f70e4188` is mergeable.**