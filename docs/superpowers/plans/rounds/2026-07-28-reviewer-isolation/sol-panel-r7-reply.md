Reviewed exact head `37c264d0865da38b16f1185ce0cf8d287fbb6819`.

## Findings

### 1. Important — a text-chunk boundary can defeat the blunt rule

`Get-PromptText` accepts multiple text chunks, appends each separately, then inserts a newline between them (`tools/codex-context-probe.ps1:47-72`). `Test-FamilyMentioned` searches only that transformed string (`tools/codex-context-probe.ps1:102-103`).

Consequently, a suppression render split as:

```text
chunk 1: <INSTRUCTIONS><skills_instru
chunk 2: ctions/></INSTRUCTIONS>
```

becomes `skills_instru\nctions`. The only family-name occurrence is destroyed. Because the split tag lies inside `INSTRUCTIONS`, the unknown-surface scan masks that body before scanning (`tools/codex-context-probe.ps1:387-403`). The second-pass report therefore has `BlockPresent=false`, zero entries (`tools/codex-context-probe.ps1:776-800`), and can reach the clean report (`tools/codex-context-probe.ps1:888-910`).

This is a transport-shape false-clean, not another quoted-versus-real structural ambiguity. The parser accepts multiple chunks but has not established that an inserted newline represents the model-visible boundary.

Minimal fix: either reject multiple text chunks as an unsupported shape, or retain an adjacency-preserving representation for family-name detection. Do not change the line-preserving representation used by the entry parser without separately testing wrapped entries.

Whether the current Codex CLI actually splits a family name across chunks is unverified, but fail-closed code cannot accept this shape and assume it will not.

### 2. Important — the first render no longer has reliable block presence or scoped entry parsing

The claimed first-render precision is not preserved. `Get-SkillReport` treats any occurrence of `skills_instructions` as block presence, then searches the entire remaining prompt for the first `### Available skills` heading (`tools/codex-context-probe.ps1:112-127`). It parses entry-shaped lines from that point without requiring an actual skills container (`tools/codex-context-probe.ps1:141-174`).

Therefore, if the renderer stops emitting the real skills block while an `AGENTS.md` contains prose such as:

```text
Documentation for skills_instructions.
### Available skills
- fake: example (file: C:/fixture/home/.agents/skills/fake/SKILL.md)
```

the first-pass missing-block guard is defeated (`tools/codex-context-probe.ps1:630-647`). The fake entry is classified and can be incorporated into the override (`tools/codex-context-probe.ps1:662-690`). That is exactly the wrong-report direction the design says the first-pass parser retains precision against (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:427-432`).

The obsolete assumption is stated directly in the implementation: it says a stray mention “costs nothing” because the real block is genuinely present (`tools/codex-context-probe.ps1:112-117`). Shape-change detection cannot assume the shape it is meant to verify.

Minimal fix:

- First pass: require the exact real skills container and parse entries only from its bounded body.
- Second pass: call `Test-FamilyMentioned` directly. Do not invoke `Get-SkillReport`; currently it still parses the suppression render before blocking (`tools/codex-context-probe.ps1:776-796`).

This preserves the user-approved blunt suppression rule without applying it to first-pass measurement.

### 3. Minor — two test callers still pass a now-ignored argument

The production callers use the new one-argument signature (`tools/codex-context-probe.ps1:628`, `:777`), but two test helpers still call:

```powershell
Get-SkillReport $t (Hide-KnownContainer $t)
```

at `evals/multi-model-verify/test_codex_context_probe.py:75` and `:136`, despite the function having only one declared parameter (`tools/codex-context-probe.ps1:106`).

The comment claiming this matches shipped behavior is now backwards (`evals/multi-model-verify/test_codex_context_probe.py:69-72`). The second expression is evaluated but is not bound to a declared parameter, so these tests retain an unrelated masking dependency that production no longer has.

Remove the second argument and update the comment. I found no executable dependency on the three deleted functions; remaining named references are historical records, such as `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2719-2725`.

### 4. Tests are not vacuous, but the reversal count is wrong

The shared helper requires exit 1 and a matching blocked reason (`evals/multi-model-verify/test_codex_context_probe.py:106-118`). A clean exit therefore fails the suite. I found no vacuous reversed polarity assertion.

However, the record says nine tests were reversed (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2725`). There are six marked test functions: five single cases at `evals/multi-model-verify/test_codex_context_probe.py:1051`, `:1150`, `:1210`, `:1223`, and `:1318`, plus one three-value parametrized test at `:1331-1350`. That is six functions or eight collected cases—not nine.

### 5. Minor — the recorded cost is neither complete nor fully precise

The substring search covers every text chunk from every prompt message, not merely global `AGENTS.md` and skill descriptions (`tools/codex-context-probe.ps1:47-72`, `:102-103`). Additional blocking sources include:

- A cwd or other rendered environment path containing a family name. The fixture confirms cwd is rendered in prompt text (`evals/multi-model-verify/fixtures/codex-prompt-input/suppressed.json:8`).
- Client-generated/system prompt prose.
- Skill names and paths containing one of the three feature-family names.

Those cases may require relocating a mirror, changing installed content, or changing the client—not “rewording one line” as claimed (`tools/codex-context-probe.ps1:92-101`; `docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:413-425`).

Conversely, `skills_instructions` appearing only in a skill description does not itself prevent a review: that mention is expected on pass one and disappears with the skills container before pass two. The three feature names are refused on both renders, while the skills name is refused only on the second (`tools/codex-context-probe.ps1:210-220`, `:776-796`; `docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:394-401`).

The design also retains a stale present-tense statement saying skills presence reads masked structural text (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:327-332`).

## Decision assessment

The blunt rule is defensible for contiguous rendered text: every genuine known-family tag necessarily contains the family substring, so the rule removes the recurring structural false-clean class at the accepted cost of false blocks. I would not reject that trade itself.

The implementation still needs correction because:

- its text extraction can destroy a substring across accepted chunk boundaries; and
- it applies blunt presence to the first-pass measurement, contradicting the decision to retain first-pass precision.

## Unverified

- I could not rerun the reported 438/1 pytest result because no Python interpreter is available in this environment.
- I did not reproduce the live Codex probe or its reported SHA-256.
- Whether current `codex debug prompt-input` can split one generated family name across adjacent text chunks remains unverified.

## Verdicts

1. Suppression decision and false-clean attack: **FIX** — reject or safely scan multi-chunk boundaries.
2. First-render parser: **FIX** — restore exact bounded first-pass block parsing.
3. Deletions and callers: **FIX** — remove the two stale test arguments and comments.
4. Reversed tests: **FIX** — helper passes; correct “nine” to eight collected cases.
5. Recorded cost: **FIX** — document all rendered-text sources and correct the skill-description overstatement.
6. Terminal verdict for `37c264d0865da38b16f1185ce0cf8d287fbb6819`: **FIX**.

**OVERALL: FIX**

