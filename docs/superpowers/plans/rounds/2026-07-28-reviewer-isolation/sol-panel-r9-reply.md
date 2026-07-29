Reviewed exact head `6d5c25317086245b161b9c4520c20f5f0cbc9dcc`.

## Important finding — locator masking is also modifying measured entries

The offset-preserving locator is sound, but `Get-SkillReport` subsequently parses the masked string rather than the raw render:

- Other known bodies are blanked in `$scan` (`tools/codex-context-probe.ps1:175-181`).
- The masking preserves length exactly (`tools/codex-context-probe.ps1:398-408`).
- The skills body is then sliced from `$scan`, not `$text` (`tools/codex-context-probe.ps1:204-212`).

That can silently remove advertised entries. I reproduced this under both hosts with an otherwise accepted prompt containing one skills block and no outer permissions block:

```text
- one: visible (...)
Continuation quotes <permissions instructions>
- two: should remain advertised (...)
</permissions instructions>
- three: visible (...)
```

`Test-PromptShape` passed, but `Get-SkillReport` returned only `one` and `three`, with `Malformed=false` and `Ambiguous=false`. The complete `two` entry was blanked before the entry loop could audit it; that loop ignores non-entry lines and cannot report what masking erased (`tools/codex-context-probe.ps1:241-259`).

Thus a renderer change that moves an optional known container into the skills body—or free text whose pair spans an entry—produces a wrong count rather than a refusal. If another known body contains the whole genuine skills container, the opener is erased and the caller safely reports the block missing (`tools/codex-context-probe.ps1:720-734`); offsets themselves do not shift.

Specific fix: use `$scan` only to locate and validate `$bodyStart`/`$closeAt`, then slice the raw render:

```powershell
$body = $text.Substring($bodyStart, $closeAt - $bodyStart)
```

Add a regression where a known pair inside the skills body spans a valid entry and assert that all raw entries remain measured.

## `Ambiguous`: keep it, but complete its contract

Keeping the local guard is justified. Although `Test-PromptShape` currently rejects these shapes first (`tools/codex-context-probe.ps1:714-715`), `Get-SkillReport` is independently exercised by three test callers (`evals/multi-model-verify/test_codex_context_probe.py:78`, `:143`, `:1478`). A measurement that feeds configuration should remain total if caller ordering later changes.

It is not fully total yet. `Ambiguous` is evaluated only when an opener exists (`tools/codex-context-probe.ps1:194-203`). A close-only shape therefore returns:

```text
BlockPresent=false, Ambiguous=false, OpenCount=0, CloseCount=1
```

despite the stated “exactly one opener and one close” contract (`tools/codex-context-probe.ps1:170-174`). Current top-level behavior remains fail-closed through the missing-block check, but the standalone report is internally wrong.

Keep the branch, set `Ambiguous=true` for every non-`0/0` shape that is not exactly ordered `1/1`, and add close-only/open-only function tests.

## Other changes

- Quoted earlier bodies: the two intended polarities are now covered at `evals/multi-model-verify/test_codex_context_probe.py:1413-1464`.
- Four residual statements: corrected at `tools/codex-context-probe.ps1:91-103`, `docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:417-423`, `evals/multi-model-verify/test_codex_context_probe.py:95-105`, and `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2725`.
- Record gaps: feature-family names in descriptions and wrapped names are now explicitly recorded at `docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:454-471`.
- One remaining wording error: `Get-SkillReport` says it has “two pass-1 callers” (`tools/codex-context-probe.ps1:123-131`). Production has one call (`tools/codex-context-probe.ps1:715`); change this to “the caller’s two checks/consumers.”

## Unverified

- I could not rerun the reported 443/1 suite because Python is unavailable.
- I did not rerun the live probe or independently verify its reported hash.
- The wrong-count masking reproduction was function-level under both hosts, not a complete stub-driven probe.

## Verdicts

1. Applied changes: **FIX** — masking locates correctly but measures modified text.
2. Masking attack: **FIX** — slice the raw body after locating boundaries in the mask.
3. `Ambiguous`: **FIX** — keep it, but cover close-only and other non-`0/0`, non-`1/1` shapes.
4. Record completeness: **FIX** — update the new measurement claim and “two callers” wording.
5. Terminal verdict for `6d5c25317086245b161b9c4520c20f5f0cbc9dcc`: **FIX**.

**OVERALL: FIX**

