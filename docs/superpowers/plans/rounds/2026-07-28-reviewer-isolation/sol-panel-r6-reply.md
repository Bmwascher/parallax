Terminal position: **FIX** for head `5e1c5a28df21c7820e75bd956d7e2a321a3f386d`. The previous two false cleans are closed, but the replacement opener grammar has one false-clean and one false-block class.

## Findings

1. Important — quoted `>` truncates a real opener and can restore false clean.

The opener regex stops at the first `>` without respecting quoted attribute values (`tools/codex-context-probe.ps1:98`). Therefore:

```text
<INSTRUCTIONS>
<apps_instructions note="a>b"/>
</INSTRUCTIONS>
```

is matched only as `<apps_instructions note="a>`. That truncated match is not considered self-closing, and with no later close it is discarded (`tools/codex-context-probe.ps1:103-112`). Masking then erases the real tag with the `INSTRUCTIONS` body, so `Test-ContainerPresent` reports absent (`tools/codex-context-probe.ps1:126-152`).

I reproduced under both hosts:

- `Get-RawContainerSurface`: `Present=false`
- `Get-FeatureReport`: `Apps=false`
- `Get-UnknownPromptBlock`: zero
- `Test-PromptShape`: passed

That can proceed to `status: clean`, exit 0 (`tools/codex-context-probe.ps1:1002-1024`). This contradicts the design’s claim that attributes are matched as grammar and complete nested surfaces block (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:394-408`).

This is a DEFECT that blocks merge.

2. Important — `\b` accepts names and text that are not the requested family.

A word boundary is broader than a tag-name terminator. These all match as `apps_instructions` surfaces:

```text
<apps_instructions-extra/>
<apps_instructions.foo/>
<apps_instructions:foo/>
<apps_instructions=off/>
```

I confirmed all four under both hosts. The first three are different tag names—the declared tag grammar expressly allows `-`, `.`, and `:` in names (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:520-524`). The fourth does not have a valid delimiter after the known name under the repository’s own general tag grammar, which permits attributes only after whitespace (`tools/codex-context-probe.ps1:496-500`).

Inside a user’s `AGENTS.md` or skill description, these should be masked as free text. Instead, the raw surface loop rejects them as malformed known-family tags (`tools/codex-context-probe.ps1:643-650`). This is not covered by the accepted limit, which applies to complete surfaces of the four exact known families (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:394-425`).

Replace `\b` with a real tag-name boundary, such as a lookahead allowing only whitespace, `/`, or `>`.

3. Self-closing classification is correct only after correct tokenization.

For normally tokenized forms, `EndsWith("/>")` gives the intended result:

- `<name note="value/">` is not self-closing.
- `<name note="value/"/>` is self-closing.

But because the opener regex is not quote-aware, this legitimate unpaired mention is truncated at the embedded `>` and falsely classified as self-closing:

```text
<apps_instructions note="literal/> only">
```

The truncated match ends in `/>`, so lines 107–109 report a complete non-exact surface and the run blocks (`tools/codex-context-probe.ps1:98-109`). That is another consequence of finding 1.

Minimal correct fix: tokenize quoted attribute values, enforce the real post-name boundary, and capture the self-closing slash at the actual tag terminator rather than inferring it from a potentially truncated match.

4. Case handling passes.

Both opener and close matching are case-insensitive (`tools/codex-context-probe.ps1:98-99`), while exactness comparisons are case-sensitive (`tools/codex-context-probe.ps1:115-120`). I confirmed:

- `<APPS_INSTRUCTIONS>…</apps_instructions>` returns the opener as non-exact.
- `<apps_instructions>…</APPS_INSTRUCTIONS>` returns the closer as non-exact.

Both are then rejected by the four-family loop (`tools/codex-context-probe.ps1:643-650`).

5. Four-family coverage and global guard pass.

Nothing from the old per-function checks was omitted:

- Skills use the shared rule (`tools/codex-context-probe.ps1:193`).
- Plugins, recommended plugins, and apps use it (`tools/codex-context-probe.ps1:285-298`).
- Exactness iterates the same four families (`tools/codex-context-probe.ps1:643-645`).

The global fallback, candidate construction, existence check, and resolution now all sit inside one guard with terminating errors (`tools/codex-context-probe.ps1:845-861`). I found no continuation after a failed global-file check.

## Unverified

- I could not rerun the reported full test suites or live probe because Python remains unavailable on PATH.
- The counterexamples were exercised through the shipped functions under both PowerShell hosts, not through a complete artifact-writing run.
- I did not observe whether the current Codex renderer emits quoted `>` characters in attributes; the finding concerns the required fail-closed response to a tag shape the claimed attribute grammar does not parse.

## Verdicts

1. Surface grammar: **FIX** — make opener parsing quote-aware.
2. Self-closing decision: **FIX** — capture the actual terminal slash after correct tokenization.
3. Case variants: **PASS**.
4. Four-family coverage: **PASS**.
5. Global-file guard: **PASS**.

**OVERALL for `5e1c5a28df21c7820e75bd956d7e2a321a3f386d`: FIX.**

