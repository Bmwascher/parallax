## Findings

### 1. Important — `LastIndexOf` can hide genuine outer blocks: DEFECT, MUST BLOCK MERGE

The fix assumes the final `</INSTRUCTIONS>` anywhere in the prompt is the real close ([tools/codex-context-probe.ps1:198](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:198), [tools/codex-context-probe.ps1:209](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:209)). That is not guaranteed by the flattened text.

Two failing shapes follow:

```text
<INSTRUCTIONS>
user text
</INSTRUCTIONS>
<memories_instructions>
genuine outer surface
</memories_instructions>
later prose quotes </INSTRUCTIONS>
```

The mask extends through the later quotation and erases the genuine unknown block before scanning.

Likewise, if a future renderer emits two exact `INSTRUCTIONS` containers, the first opener is paired with the second container’s close. Everything between them is masked. `Get-InstructionReport` independently reads only the first opener and first close, so it does not detect that the masking logic merged two containers ([tools/codex-context-probe.ps1:134](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:134), [tools/codex-context-probe.ps1:195](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:195)).

Either shape can complete the suppression call, advertise zero according to the parser, and reach clean while the second prompt was not fully understood.

Fix: bound `INSTRUCTIONS` using a validated outer-layout boundary rather than the last matching substring in the entire prompt, and block when that boundary is missing or ambiguous. Add cases for a later quoted close after a genuine unknown outer block and for two `INSTRUCTIONS` containers.

### 2. Minor — the joined-entry detector still rejects valid free text: DEFECT

The narrowed detector requires a complete-looking prior marker:

```regex
(?i)\(file: .*?SKILL\.md\)[ \t]+- [A-Za-z0-9_:-]+:
```

([tools/codex-context-probe.ps1:102](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:102), [tools/codex-context-probe.ps1:112](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:112)).

That still matches a legitimate description such as:

```text
Parse records like (file: C:/example/SKILL.md) - next: continue.
```

The actual final renderer marker can follow later on the same line, but `$joined` marks the entry malformed before the greedy final-marker parser runs ([tools/codex-context-probe.ps1:117](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:117)).

The non-greedy segment cannot cross a line boundary because matching occurs against one `$trimmed` line at a time ([tools/codex-context-probe.ps1:117](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:117)). A joined first entry whose path does not end in `SKILL.md` is not legitimate under this parser’s existing source-path contract, so that is not a separate finding.

Fix: either identify joined entries using structure unavailable to free-text descriptions, or record the grammar as inherently ambiguous and rely on the second-pass block-presence check rather than claiming all joined lines are detected without false positives.

### 3. Minor — the corrected history still miscounts the table: DOCUMENTATION DEFECT

The design says “The six rows above were added” ([reviewer-isolation-design.md:312](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:312)). The diff added five table rows:

1. Non-exact known block.
2. Malformed/joined entry.
3. No suppression.
4. Artifact failure.
5. `-SkipProbe`.

The case variant is a fourth finding under the existing non-exact-known-block row, not a sixth row ([reviewer-isolation-design.md:306](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:306)). If “six rows” includes the pre-existing content-chunk row, then the statement that all six were added by mode-diff rounds is false.

The disposition details are otherwise consistent with the checkpoint: three full false-cleans, case confirmed mechanically, joined entries caught downstream, and `-SkipProbe` exit 0 without clean JSON ([checkpoint:253](C:/Users/Brandon/Documents/parallax/.git/parallax/application-checkpoints/20260728-1552-22dd63311a33.md:253)).

Fix: say “five rows covering six findings.”

## Attack results

1. **Case handling: PASS.** Case-insensitive name recognition followed by a case-sensitive literal allowlist closes the previous bypass ([tools/codex-context-probe.ps1:266](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:266), [tools/codex-context-probe.ps1:278](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:278)). Any name that the general scanner would consider equal to a known name necessarily satisfies the boundary in the anywhere regex first. Prefix extensions with a word character become unknown names; punctuation-delimited extensions are recognized and blocked. I found no remaining case/prefix/suffix bypass.

2. **Last-close handling: FIX.** It fixes quotations inside the body but can over-mask later genuine structure as Finding 1.

3. **Joined-entry handling: FIX.** It detects valid joined entries with parenthesized paths and remains line-local, but still has Finding 2’s free-text collision.

4. **History: FIX.** The establishment details are now accurate; the row count remains wrong.

5. **Clean control flow:** I found no route that skips the suppression branch or second invocation entirely: clean remains below the `-SuppressSkills` gate ([tools/codex-context-probe.ps1:555](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:555), [tools/codex-context-probe.ps1:645](C:/Users/Brandon/Documents/parallax/tools/codex-context-probe.ps1:645)). Finding 1 is nevertheless a remaining path where that invocation completes but its rendered prompt is not fully understood.

## Verdicts

1. **FIX** — A11’s case change is delivered, but its `INSTRUCTIONS` amendment replaces an early-close false positive with an over-masking false-clean.

2. **PASS** — A11 accurately declares this round’s changes and A9–A11 are now ordered. The remaining issues are defects inside A11, not undeclared earlier deviations ([reviewer-isolation.md:2706](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2706)).

3. **PASS** — no route was found that dispatches bytes differing from the hash-verified in-memory override. The last-close issue affects prompt interpretation, not artifact identity.

4. **FIX** — repair or explicitly redesign the ambiguous `INSTRUCTIONS` boundary and the joined-entry/free-text ambiguity.

5. **PASS** — contract-region declarations and whole-body pins remain unchanged and intact.

6. **PASS** — none of the original whole-branch-review dispositions is reopened.

7. **FIX** — change “six rows” to “five rows covering six findings”; the rest of the revised history is supported. The universal fail-closed documentation also remains untrue until Finding 1 is resolved ([reviewer-isolation-design.md:288](C:/Users/Brandon/Documents/parallax/docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:288)).

## UNVERIFIED

- Claim 1’s historical tests-first chronology remains unverifiable from final files and same-commit history.
- I did not rerun the mutation-requiring 403-test, gate, or live-probe commands in the read-only workspace.
- I did not verify a live prompt containing multiple `INSTRUCTIONS` containers or a later quoted closing marker; the finding follows from the parser’s universal fail-closed claim and the reachable string shapes.
- Model/sandbox influence on rendered prompt content remains explicitly unverified by the design.

**OVERALL: FIX — DO NOT MERGE**