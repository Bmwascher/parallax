## Cap findings

### 1. Important — case-variant known tags remain a false-clean bypass: DEFECT, MUST BLOCK MERGE

The new anywhere regex is case-sensitive ([tools/codex-context-probe.ps1:248](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:248)). But the fallback scanner skips known names using ordinary `-contains`, which PowerShell evaluates case-insensitively ([tools/codex-context-probe.ps1:258](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:258), [tools/codex-context-probe.ps1:261](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:261)).

Thus `<SKILLS_INSTRUCTIONS version="2">`:

1. Does not match the case-sensitive anywhere scan.
2. Is matched by the general scanner.
3. Is silently skipped as a “known” name by case-insensitive `-contains`.
4. Is absent to the exact skills parser ([tools/codex-context-probe.ps1:80](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:80)).
5. Reaches second-pass absence and then clean exit 0 ([tools/codex-context-probe.ps1:549](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:549), [tools/codex-context-probe.ps1:643](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:643)).

I confirmed the mismatch under both hosts: the new regex rejects the uppercase name while `-contains` returns true.

Fix: make the anywhere name recognition case-insensitive while retaining the case-sensitive whole-literal allowlist. A case variant will then be recognized as a known-name form and rejected because it is not an exact literal. Add first- and second-pass case-variant tests.

### 2. Minor — a quoted closing delimiter can defeat `INSTRUCTIONS` masking: DEFECT, MUST BLOCK MERGE

Putting `INSTRUCTIONS` first correctly protects quoted opening markers. But masking still pairs its opener with the first exact `</INSTRUCTIONS>` substring ([tools/codex-context-probe.ps1:185](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:185), [tools/codex-context-probe.ps1:193](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:193)).

A global `AGENTS.md` that quotes `` `</INSTRUCTIONS>` `` ends the masked span early. Tag-looking prose later in that same user-authored body is then scanned as outer structure and can block a legitimate review. This is the closing-literal counterpart of the opening-literal reproduction that motivated the ordering fix; the body is explicitly arbitrary user-authored text ([tools/codex-context-probe.ps1:165](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:165)).

Fix: delimit the single combined `INSTRUCTIONS` container with its actual outer closing occurrence rather than the first body substring, and add a fixture containing a quoted closing marker followed by paired tag-looking prose.

### 3. Minor — the joined-entry detector rejects legitimate free text: DEFECT, MUST BLOCK MERGE

The greedy final `(file: ` delimiter itself is correct. The new companion detector is too broad:

```regex
\)[ \t]+- [A-Za-z0-9_:-]+:
```

([tools/codex-context-probe.ps1:102](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:102), [tools/codex-context-probe.ps1:107](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:107)).

A valid description such as:

```text
Use when output is (done) - next: retry.
```

matches `$joined` and is marked malformed even though it carries only the renderer’s one final file marker. The previous marker-count rule would have accepted this exact shape.

Fix: detect an earlier complete rendered entry—its `(file: …/SKILL.md)` plus the following entry start—not every close parenthesis followed by bullet-like prose.

### 4. Minor — the new design history note is factually false: DOCUMENTATION DEFECT, MUST FIX

The design says all five newly listed conditions had reached `status: clean`, exit 0, and were reproduced ([reviewer-isolation-design.md:312](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:312)). That is not true:

- The two-entries-on-one-line condition produced a wrong first measurement but was caught by the later suppression check, as the checkpoint itself records ([checkpoint:142](C:/Users/Brandon/Documents/parallax/.git/parallax/application-checkpoints/20260728-1552-22dd63311a33.md:142)).
- `-SkipProbe` exited 0, but it did not emit the probe’s `status: clean` JSON ([checkpoint:18](C:/Users/Brandon/Documents/parallax/.git/parallax/application-checkpoints/20260728-1552-22dd63311a33.md:18)).
- There are four newly added rows above the mirror row, not five ([reviewer-isolation-design.md:306](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:306)).

Fix: say these rows record post-implementation findings; only some were reproduced false-cleans.

## Requested attacks

1. **Anywhere scan:** ordinary attributed inline tags are now caught, but case variants bypass it as Finding 1. Exact known tags inside a correctly masked user body are deliberately hidden. A real attributed container nested inside `INSTRUCTIONS` would also be hidden, but distinguishing that from quoted user text is outside the current outer-block model.

2. **Masking order:** masking `INSTRUCTIONS` first does not hide current exact nested skill or feature blocks from their dedicated raw-text parsers. The remaining concrete ordering hazard is the early quoted closing delimiter in Finding 2.

3. **Post-guard fields:** I found no internal path producing syntactically valid but incorrectly computed values. The resolved path comes from the path just written, and the digest is SHA-256 over the exact bytes passed to `WriteAllBytes` ([tools/codex-context-probe.ps1:584](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:584), [tools/codex-context-probe.ps1:599](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:599)). External mutation after the write remains possible by design, but every dispatch re-reads the file and rejects a hash mismatch ([SKILL.md:178](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:178), [SKILL.md:223](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:223)). **PASS.**

4. **Greedy delimiter:** choosing the last file marker correctly handles marker text in a description. The overly broad joined-entry detector creates Finding 3.

## Record-acceptable items

- Treating content nested inside the user-authored `INSTRUCTIONS` body as prose rather than independent outer prompt surfaces is a **record-acceptable existing scope limit**, not a new implementation defect. The design already defines the guarantee over outer blocks and explains why known bodies are masked ([reviewer-isolation-design.md:389](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:389), [reviewer-isolation-design.md:403](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:403)).
- A10 appearing before A9 is editorially awkward but does not falsify either amendment ([reviewer-isolation.md:2706](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2706)). It is record-acceptable.
- The three findings above are not record-only amendments. Findings 1–3 are code defects; Finding 4 is a false documentation record.

## Verdicts

1. **FIX** — A10 says known-block exactness is checked anywhere, but the case-sensitivity mismatch leaves a remaining known-tag bypass. Fix the implementation and record the cap correction.

2. **PASS** — A8–A10 disclose the post-freeze changes and their provenance. The new defects are defects inside A10, not omitted pre-existing deviations.

3. **PASS** — artifact identity remains load-bearing and correctly reverified per dispatch. No route was found that supplies the reviewer a different configuration from the in-memory value whose expected hash was reported.

4. **FIX** — close the case-variant false-clean, quoted-closing masking boundary, and legitimate-description false positive.

5. **PASS** — no marked contract region or declaration changed in this round; the six-region declaration and whole-body pins remain intact ([test_contract_coverage.py:641](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_contract_coverage.py:641), [test_multi_model_verify.py:352](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_multi_model_verify.py:352)).

6. **PASS** — the whole-branch-review dispositions remain correct; this round does not reopen any of the five minors.

7. **FIX** — the SKILL and source-header scope wording is now honest ([SKILL.md:120](C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:120), [tools/codex-context-probe.ps1:1](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:1)), but the design’s “any form” row is contradicted by the case bypass and its historical note falsely says every listed path reproduced `status: clean`.

## UNVERIFIED

- Claim 1’s historical tests-first chronology remains unverifiable from final files and commit history.
- I did not rerun the mutation-requiring 398-test, gate, or live-probe commands in the read-only workspace.
- Whether a future Codex renderer could introduce semantically real nested containers inside `INSTRUCTIONS` is unverified; it was not used as a defect verdict.
- Model/sandbox influence on rendered prompt content remains explicitly unverified ([reviewer-isolation-design.md:184](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:184)).

**OVERALL: FIX — DO NOT MERGE**