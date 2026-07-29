Reviewed exact head `3a0d88bf0791e39b8484bab8f309912a84b4e2c9`.

## Important finding — first-pass precision is still bypassable

`Get-SkillReport` searches raw text for the first exact opener (`tools/codex-context-probe.ps1:144-146`). It neither proves that opener is outside another container’s free-text body nor requires a closing delimiter—the body remains unbounded when no close is found (`tools/codex-context-probe.ps1:150-160`).

That conflicts with the shape scanner, which deliberately masks every unambiguous known-container body before interpreting markers (`tools/codex-context-probe.ps1:420-425`). The fixture already puts `permissions` before the genuine skills block (`evals/multi-model-verify/fixtures/codex-prompt-input/full.json:8`).

Therefore legitimate client prose appearing earlier can contain:

```text
<skills_instructions>
### Available skills
- fake: example (file: C:/fixture/home/.agents/skills/fake/SKILL.md)
</skills_instructions>
```

The shape check ignores that quoted example correctly, but `Get-SkillReport` selects it instead of the real later block. I reproduced under both PowerShell hosts:

- shape check passed;
- `BlockPresent=true`;
- one fake entry was reported;
- it classified as `home`;
- `New-SkillDisableOverride` generated an override for the fake path.

Those downstream operations consume the report directly (`tools/codex-context-probe.ps1:705-715`, `:784-800`).

The opposite legitimate case also fails: an earlier paired example without an entry heading causes the present-but-empty branch to block even when a genuine populated block follows (`tools/codex-context-probe.ps1:683-690`).

Minimal fix: locate the first-pass skills opener on text where every other known-container body has been quietly masked, preserve offsets into the raw text, and require the exact closing delimiter. Add polarity tests for:

- quoted exact pair before a genuine block: ignore the quote and measure the genuine block;
- quoted exact pair with no genuine block: report the first-pass block missing.

The new zero-entry explanation is also unreachable in part: `BlockPresent` now requires the exact opener, so “there is no skills block at all” is handled earlier at `tools/codex-context-probe.ps1:663-669`, not at `:683-690`.

## Other fixes

- Chunk-boundary repair: **verified.** Removing CR/LF before searching cannot erase an existing contiguous match (`tools/codex-context-probe.ps1:104-116`). It can synthesize a match across native lines, chunk boundaries, or message boundaries, but the code explicitly records that false-block cost at `tools/codex-context-probe.ps1:110-113`. Rejecting every multi-chunk render would be worse for availability; the current fail-closed choice is reasonable.
- Stale test arguments: **verified fixed.** Both helpers now use the one-argument call at `evals/multi-model-verify/test_codex_context_probe.py:67-84` and `:133-145`.
- Reversal count: **verified fixed** to six functions/eight collected cases at `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2725`.
- Suppression parsing removal: **verified.** Pass two calls `Test-FamilyMentioned` directly and assigns `$after = 0` only after absence is established (`tools/codex-context-probe.ps1:819-842`). Downstream uses `$after` only for the final report (`tools/codex-context-probe.ps1:930-950`); no `$skills2` dependency remains.
- Recorded cost: **partially fixed.** The expanded list and asymmetry are accurate at `docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:422-475`, and the earlier structural rule is marked reversed at `:327-339`.

However, four surviving statements still contradict that expanded record:

- “the user fixes by rewording one line” — `tools/codex-context-probe.ps1:92-100`;
- the same claim — `docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:417-420`;
- tests say any skill-description mention of any of the four must be reworded — `evals/multi-model-verify/test_codex_context_probe.py:97-101`;
- A21 retains the same overbroad description without marking it superseded — `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2725`.

## Unverified

- I could not rerun the reported 440/1 suite because Python is unavailable.
- I did not rerun the live probe or independently verify its reported hash.
- I reproduced the first-pass defect through the shipped functions under both hosts, not through a complete stub-driven probe invocation.

## Verdicts

1. Five applied fixes: **FIX** — first-pass precision and residual documentation remain incorrect.
2. First-render structural change: **FIX** — ignore exact quoted containers inside earlier free-text bodies and require the close.
3. Line-break normalization: **PASS**.
4. Suppression-render downstream dependencies: **PASS**.
5. Terminal verdict for `3a0d88bf0791e39b8484bab8f309912a84b4e2c9`: **FIX**.

**OVERALL: FIX**

