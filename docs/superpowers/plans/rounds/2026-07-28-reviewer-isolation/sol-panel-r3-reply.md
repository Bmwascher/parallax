Two defects remain at head `42c942143b7c3d1c319e407c542991bb8fa0637c`. Fix 2 introduces a false-clean path for a nested surviving skills container, and fix 4 can report a directory or wildcard match as the global `AGENTS.md` file.

## Five fixes

### 1. Suppression-pass ProjectDoc — PASS

Pass 2 now retains `$instructions2` at `tools/codex-context-probe.ps1:726-736`. The skills-presence and residue checks retain precedence at `tools/codex-context-probe.ps1:741-749`, followed by the new project-document check at `tools/codex-context-probe.ps1:750-757`.

The regressions cover both the pass-2-only case and precedence when both conditions fail at `evals/multi-model-verify/test_codex_context_probe.py:1076-1104`.

### 2. Structural skills presence — FIX

There is a concrete false-clean shape.

`Hide-KnownContainer` processes known containers in fixed order and replaces each validated body with spaces at `tools/codex-context-probe.ps1:252-296`. `Get-StructuralText` returns that fully masked value at `tools/codex-context-probe.ps1:411-428`. `Get-SkillReport` then derives presence exclusively from the masked text and does not even parse raw entries unless that masked presence is true at `tools/codex-context-probe.ps1:96-103`.

Therefore, this suppression render is accepted as having no skills:

```text
<INSTRUCTIONS>
<skills_instructions>
### Available skills
- planted: survives (file: C:/fixture/home/.agents/skills/planted/SKILL.md)
</skills_instructions>
</INSTRUCTIONS>
```

`INSTRUCTIONS` is masked first, erasing the nested skills delimiters and entries. I reproduced the current functions mechanically: raw opener `True`, structural opener `False`, `BlockPresent=False`, `Entries=0`. Pass 2 consequently clears both suppression checks at `tools/codex-context-probe.ps1:734-749` and can reach the clean report at `tools/codex-context-probe.ps1:837-859`.

The polarity test only exercises an ordinary outer sibling block at `evals/multi-model-verify/test_codex_context_probe.py:1125-1131`; it does not test nesting.

This is not covered by the design’s “outer blocks” guarantee, which expressly excludes content inside masked known-container bodies at `docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:472-498`. But the stronger clean-probe promise still says “no skill advertised” without that qualification at `docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:389-393` and `skills/multi-model-verify/SKILL.md:149-162`. A genuine surviving nested block violates that promise.

Minimal correct fix:

- Keep masked structural presence so a lone quoted opener remains legitimate.
- Independently detect an ordered exact raw `<skills_instructions>`/`</skills_instructions>` pair, even inside a masked body.
- Parse raw entries whenever either structural presence or that raw pair exists.
- Treat a paired raw block as present and block suppression.
- Add a pass-2 regression with the complete skills block nested inside `INSTRUCTIONS`.

A user quoting a complete balanced skills block would then block. That is the safe, unavoidable ambiguity and should be recorded as an accepted limit; the existing legitimate case quotes only an opener.

### 3. Standalone project-doc delimiter — PASS, with a record limit

The regex requires the delimiter to occupy its own line, allowing indentation, trailing horizontal whitespace, LF, and CRLF at `tools/codex-context-probe.ps1:161-187`. It operates on raw instruction text, so masking cannot erase a real delimiter. Tests cover the inline false-positive and the real standalone polarity at `evals/multi-model-verify/test_codex_context_probe.py:1134-1160`.

I found no path, within the measured renderer shape, where the real delimiter goes unseen.

One safe-direction ambiguity remains: a global `AGENTS.md` that quotes the delimiter exactly on a standalone line is indistinguishable from Codex’s real separator and will block. That should be recorded as an accepted limit, not “fixed” by weakening the standalone rule.

### 4. `global_agents_md` — FIX

The report now derives its Boolean and path consistently from `$globalPath` at `tools/codex-context-probe.ps1:823-825,837-857`, and the true/false tests own the filesystem state at `evals/multi-model-verify/test_codex_context_probe.py:435-466`.

However, `$globalPath` is populated with:

```powershell
if (Test-Path $candidate) { $globalPath = (Resolve-Path $candidate).Path }
```

at `tools/codex-context-probe.ps1:691-697`.

Two defects remain:

- `Test-Path` does not require `-PathType Leaf`, so a directory named `AGENTS.md` reports as the global file.
- Neither command uses `-LiteralPath`, so wildcard characters in `CODEX_HOME` can produce a false negative or resolve another matching path.

Minimal fix:

```powershell
if (Test-Path -LiteralPath $candidate -PathType Leaf) {
    $globalPath = (Resolve-Path -LiteralPath $candidate -ErrorAction Stop).Path
}
```

Add regressions for an `AGENTS.md` directory and a `CODEX_HOME` containing `[` or `]`.

### 5. Git path handling — PASS

Both pathname captures now go through `Invoke-GitLines` at `tools/new-review-mirror.ps1:28-60,83-108`. The helper supplies `core.quotepath=false`, captures `$LASTEXITCODE` while the Git call is current, and restores the prior console encoding in `finally`; the restore therefore runs on normal return and exceptions at `tools/new-review-mirror.ps1:49-58`.

Residual quoted paths are stopped before back-channel remediation at `tools/new-review-mirror.ps1:63-69,284-294` and before manifest resolution at `tools/new-review-mirror.ps1:144-156`. The old trim-and-resolve collision is gone: no quoted path reaches `Join-Path` at `tools/new-review-mirror.ps1:161-179`.

Integration tests cover accented remediation and manifest hashing at `evals/multi-model-verify/test_review_mirror.py:489-544`; the explicit quoted-form stop is pinned at `evals/multi-model-verify/test_review_mirror.py:570-588`.

The decision not to use `-z` is technically correct. Git documents that porcelain `-z` removes the `->` marker and reverses rename fields. The present parser intentionally depends on `old -> destination` at `tools/new-review-mirror.ps1:129-142`, with its deleted-destination behavior tested at `evals/multi-model-verify/test_review_mirror.py:312-323`. Adopting `-z` would be viable but would require rewriting those rules, not merely changing transport. [Official Git status documentation](https://git-scm.com/docs/git-status)

## Unverified

- I did not rerun the reported 422-test dual-host suite or the live probes/mirrors.
- I reproduced the nested-skills false clean through the current functions under pwsh 7.6.3. Launching Windows PowerShell 5.1 was unavailable in this sandbox; the relevant masking and string operations have no host-specific branch.
- Whether current Codex 0.144.1 ever nests a skills container inside another known container. The finding is a fail-open parser response to a changed prompt shape, not a claim about today’s measured layout.

## Verdicts

- Fix 1: **PASS**
- Fix 2: **FIX** — detect a complete raw skills pair even when structural masking hides it.
- Fix 3: **PASS** — record the standalone quoted-delimiter ambiguity.
- Fix 4: **FIX** — require a literal leaf file when resolving global `AGENTS.md`.
- Fix 5: **PASS**
- **OVERALL: FIX — head `42c942143b7c3d1c319e407c542991bb8fa0637c` must not merge until fixes 2 and 4 are corrected.**

