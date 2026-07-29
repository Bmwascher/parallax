## Findings

1. Important — nested feature containers still reach false clean.

`Test-PromptShape` checks features only after quietly masking every known body (`tools/codex-context-probe.ps1:540-558`). Because masking preserves only the outer container’s delimiters and blanks its body (`tools/codex-context-probe.ps1:275-319`), this input hides the apps container:

```text
<INSTRUCTIONS>
<apps_instructions>live</apps_instructions>
</INSTRUCTIONS>
```

I reproduced this through the shipped functions under both PowerShell hosts: `Test-PromptShape` passed and `Apps` was false. The later validating scan masks the same body again (`tools/codex-context-probe.ps1:385-401`). Nothing after that independently checks features: the suppression path checks only skills and ProjectDoc before producing clean (`tools/codex-context-probe.ps1:789-811`, `tools/codex-context-probe.ps1:892-914`).

The polarity test covers only an outer sibling apps container, not a nested one (`evals/multi-model-verify/test_codex_context_probe.py:1199-1207`).

This is a DEFECT that blocks merge. Minimal correct fix: for plugins, apps, and recommended plugins, add a raw ordered-pair backstop analogous to skills. It should recognize known names case-insensitively with attributes allowed; an exact pair reports the feature, while a paired non-exact form blocks as an unsupported shape. An unpaired prose mention may remain masked.

2. Important — the skills backstop is exact-literal-only.

The applied rule closes the exact nested-container reproduction, and using an ordered pair without requiring `### Available skills` is safety-correct: it blocks more ambiguous input in the safe direction. The recorded paired-quotation limit is appropriate (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:394-406`).

But the backstop recognizes only the exact, case-sensitive `<skills_instructions>` literal (`tools/codex-context-probe.ps1:113-121`). Consequently this nested form remains invisible:

```text
<INSTRUCTIONS>
<skills_instructions version="2">
### Available skills
...
</skills_instructions>
</INSTRUCTIONS>
```

The quiet mask erases it before known-tag exactness (`tools/codex-context-probe.ps1:381-397`), structural presence also loses it, and the raw-pair test does not recognize its attributed opener. I reproduced `BlockPresent=false` and zero entries under both hosts. A case variant has the same problem.

Existing attributed-tag tests place the malformed tag outside a masked body (`evals/multi-model-verify/test_codex_context_probe.py:747-769`); the new nested test uses only the exact opener (`evals/multi-model-verify/test_codex_context_probe.py:1154-1168`).

This is a DEFECT that blocks merge. Minimal correct fix: recognize any ordered raw `skills_instructions` pair by known-name grammar, case-insensitively. If its literals are non-exact, route it to the existing exactness failure; if exact, count it as presence. Test attributed and case-variant nested pairs on both renders.

3. Important — global-file failure handling remains incomplete.

The intended corrections are present: `-LiteralPath`, `-PathType Leaf`, and guarded literal resolution (`tools/codex-context-probe.ps1:734-750`). They correctly address directories and wildcard-bearing paths covered by the tests (`evals/multi-model-verify/test_codex_context_probe.py:1210-1237`).

However, `Join-Path` and `Test-Path` remain outside the `try`, and `Test-Path` has no `-ErrorAction Stop` (`tools/codex-context-probe.ps1:734-742`). Under both hosts, an invalid provider path produced two non-terminating errors, left `$candidate`/the existence result empty, and continued with exit 0. The eventual clean report then represents the failed measurement as `global_agents_md=false` (`tools/codex-context-probe.ps1:892-914`).

This is a DEFECT, not a record amendment. Wrap candidate construction, `Test-Path -ErrorAction Stop`, and `Resolve-Path -ErrorAction Stop` in one guard. The error should say the global file’s presence could not be determined, because failure may occur before existence is established.

The additional false blocking caused by the exact ordered-pair rule is record-acceptable; the three false-clean/unmade-measurement paths above are not.

## Unverified

- I could not rerun the reported 428-test suites because no Python executable is available on PATH. I did execute the two parser counterexamples directly through the shipped functions under both `powershell.exe` and `pwsh.exe`.
- I did not reproduce an access-denied real file; I reproduced the unguarded non-terminating path/provider failure under both hosts.

## Verdicts

1. Three applied fixes: **FIX** — their target cases are implemented, but the feature and global-file fixes remain incomplete.
2. Raw-pair rule: **FIX** — recognize paired attributed and case-variant nested skills containers.
3. Quiet feature mask: **FIX** — add a raw ordered-pair backstop for all three feature families.
4. Terminal verdict for `89ef9c41e0553a6ee71c5e97a40c7fc8c2b0168e`: **FIX**.

**OVERALL: FIX — this head is not mergeable until the three defects above are closed.**

