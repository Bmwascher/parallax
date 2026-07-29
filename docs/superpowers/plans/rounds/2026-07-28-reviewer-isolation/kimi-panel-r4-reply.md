All verification is complete. Here is the round-4 reply.

## Task 1 — Verification of each change at the code

1. **Chunk-split fix.** `Test-FamilyMentioned` flattens `[\r\n]` before the case-insensitive `IndexOf` (tools/codex-context-probe.ps1:114-116). The pinning test splits `<skills_instructions/>` across two content chunks in the second fixture and asserts a block (evals/multi-model-verify/test_codex_context_probe.py:1356-1376). The reverted-script result (exit 0) is consistent with the old code: the join at probe:72 would have produced `skills_instru\nctions`, which the old un-flattened `IndexOf` could not match. VERIFIED.
2. **First-render strictness.** Exact Ordinal literal required (probe:144-146), body bounded by the close (probe:151-154), heading searched only inside the body (probe:158-160). Missing block blocks at probe:666-669, present-but-empty at probe:683-690. The pinning test asserts exit 1, `"missing on the first pass"`, and that no override file was written (test:1394-1400). The reverted-script reproduction (`clean`, `skills_before: 1`) is consistent with the old whole-render heading search. VERIFIED.
3. **Suppression render unparsed.** `Get-SkillReport $text2` is gone; the check is `Test-FamilyMentioned $text2 "skills_instructions"` (probe:832) with `$after = 0` set only after it passes (probe:842). VERIFIED.
4. **Both helpers one argument.** test:78 and test:139 call `Get-SkillReport $t;`; the function takes exactly one parameter (probe:119), and the comment now names the defect (test:69-75). VERIFIED.
5. **Present-but-empty message names both causes** (probe:683-690). VERIFIED.
6. **Cost record and record corrections.** Sources-with-remedies list at spec:437-450, asymmetry at spec:428-433, transport rule at spec:471-475, reversal-count correction in plan A21 (FIX3.diff:10), stale narrowing paragraph corrected at spec:329-339. VERIFIED.

## Task 2 — Attack on the first-render change

**Wrong count rather than a stop: I could not produce one that reaches any output.** Every shape I traced terminates in a block:

- Entries outside the container, after the close, or under a renamed heading: undercount or zero-count on pass 1, but the residue keeps the family name on render 2 and blocks at probe:832; a missing heading inside the body blocks at probe:683. Case/attribute/whitespace variants of the container are thrown by the pre-existing exactness scan (probe:426-432) before `Get-SkillReport` even runs, or fail presence at probe:666. A chunk boundary splitting the literal on pass 1 blocks at probe:666 (the flattening at probe:114 applies only to `Test-FamilyMentioned`) — fail-closed, correct direction.
- The nearest miss is real but transient. `openAt` is the FIRST exact-literal occurrence on RAW text (probe:145), not a validated container. A user whose global `AGENTS.md` quotes the open literal alone (`<skills_instructions>` with no close — legitimate free text, invisible to the count rule because INSTRUCTIONS is masked first, probe:276-280 and :328), on a client that renders INSTRUCTIONS BEFORE the skills block, makes `openAt` land on the mention; the body then spans mention→real close, and a `### Available skills` heading plus entry-shaped lines in the AGENTS.md after the mention ARE parsed as entries (probe:151-160). `skills_before` is inflated and the in-memory override gains disable entries for skills never advertised. However, the mention persists on render 2 (the global file cannot be suppressed, spec:511-515), so probe:832 blocks before the write at probe:873, and the block message names the right cause. In the shipped fixtures the skills block precedes INSTRUCTIONS (fixtures/codex-prompt-input/flagged.json:8), so the corner additionally needs an ordering the client does not currently produce. No report and no artifact can carry the wrong count — but the comment at probe:155-157 ("a heading written anywhere else in the prompt cannot supply entries") and spec:467-469 are overstated in this corner: the guarantee is delivered by the pass-2 blunt rule, not by the body bound alone.

**Legitimate render refused:** a client that keeps the exact container but renders the `### Available skills` heading OUTSIDE it — the old whole-render heading search accepted that; it now blocks at probe:683-690. Also a user who documents the block by quoting its open literal alone in `AGENTS.md` now blocks at probe:832 (an admitted blunt-rule cost). Attribute/case variants were already refused before this range by the exactness scan, so those are not new.

## Task 3 — Line-break removal: new blocking cases

The flattening (probe:114) can only add matches. The one new blocking class is a family name spelled ACROSS an ordinary line wrap in any rendered text — a wrapped path, prose hyphenation, e.g. a line ending `.../plugins_` followed by `instructions/...`. This is admitted in the code comment (probe:110-113) but is NOT in the design's cost list (spec:435-450); the transport paragraph (spec:471-475) asserts only "the direction is safe." Since the features check runs this on raw text of BOTH renders (probe:559-568), a wrapped mention in a skill description or AGENTS.md blocks outright. A small record gap, not a gate defect.

## Task 4 — Suppression render no longer parsed: downstream consumers

The old parse produced `BlockPresent`, `Entries.Count` (`$after`), and `Malformed`. Consumers at head: the `"$after entries parsed"` message text is deleted with the check; the `$after -ne 0` guard is subsumed (entries were only parsed when the name was present, and the name now blocks directly at probe:832); `skills_after` in the report (probe:934) and console line (probe:948) is now 0 by construction — matching every consumer, which all expect 0: commands/doctor.md:174 and :187, test:395, evals/multi-model-verify/test_review_mirror.py:411. tools/new-review-mirror.ps1:386-394 consumes only the probe's exit code and passes the line through verbatim; skills/multi-model-verify/SKILL.md references no report fields (grep, no matches). `Malformed` was never consumed on pass 2. Nothing downstream depends on a value the parse used to produce. PASS.

## Task 5 — Is the cost record complete now?

Substantially yes — the asymmetry (spec:428-433) and the five sources with remedies (spec:437-450) are exactly what rounds 3/7 established. Two residual gaps:

- The cross-line-break adjacency block (new this round) is in the code comment but absent from the design list.
- A skill DESCRIPTION naming a FEATURE family blocks outright on both renders (features are refused on render 1, probe:559-568, and the description is raw text) yet IS rewordable — the asymmetry paragraph covers a description naming the SKILLS family (no block), the sources list covers name/path (not rewordable), and the rewordable-description-naming-a-feature case is the missing middle row. The general sentence at spec:422-426 covers it abstractly, but spec:452-453 declares completeness.

## Findings

1. **Minor — tools/codex-context-probe.ps1:120-123 — stale comment contradicting the new contract.** The opening comment still motivates the `BlockPresent`/`Entries` split by the suppression render ("An ABSENT block is the success state once suppression has run … the caller must be able to tell them apart"), but the suppression caller was deleted this range and the very next paragraph (probe:125) says "THIS FUNCTION IS FIRST-RENDER ONLY." On the first render ABSENT is a failure (probe:666), not a success state. Same defect class as the stale sentence this range itself corrected (plan A22). Minimal fix: re-motivate the split by the two pass-1 callers at probe:666 and :683.
2. **Minor — docs/.../2026-07-28-reviewer-isolation-design.md:435-450 — cost list still incomplete in two cells.** Missing: (a) the cross-line-break adjacency block created by probe:114 (admitted only in the code comment, probe:110-113); (b) a skill description naming a FEATURE family — blocks outright, user-rewordable, the counterpart of the asymmetry case at spec:430-433. The record again claims completeness (spec:452-453). Minimal fix: add both rows.

Non-finding, recorded for the panel: the probe:155-157 comment overstatement from Task 2 (heading outside the container CAN supply entries when a quoted open-only literal precedes the real block with INSTRUCTIONS rendered first) has no reachable consequence — the same mention blocks at probe:832 before any artifact is written (probe:873). I am not raising it as a defect; the fix would be comment wording only.

## Unverified

- I have no execution tools: the 440 passed / 1 skipped counts, the live-probe result, the override sha256, and the two reverted-script reproductions are taken as reported evidence. I verified each is CONSISTENT with the code paths I read (old un-flattened `IndexOf` could not match the split name; old whole-render heading search would parse the prose entries), but I did not run them.
- Render ordering of the real client (INSTRUCTIONS vs skills block) beyond what the fixtures show.

## Verdicts

1. Implementation fidelity — PASS (A21 count correction, A22 row, and all five code changes verified at the code).
2. Dispatch integrity — PASS (write/hash/validate unchanged at probe:870-893; unparsed second render cannot pollute the artifact, probe:832 before :873).
3. No false-clean path — PASS (no input shape traced to `clean`; the wrong-count corner from Task 2 terminates in a block with an accurate message).
4. Honest scope — PASS, with two Minor record gaps (Findings 1-2); nothing overstates the guarantee to a user.
5. Test integrity — PASS (both helpers match the shipped call shape; both new tests assert the block AND the no-artifact invariant; reversal counts now match the plan).
6. Destructive/rejecting bugs — PASS (no changes to new-review-mirror.ps1 in this range; the new refusals are loud and correctly diagnosed).

OVERALL: PASS

To resume this session: kimi -r 80e4075c-c7e7-4c3d-af42-c91955203080
