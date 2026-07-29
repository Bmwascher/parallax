All verification is complete. Here is the round-5 reply against head `6d5c25317086245b161b9c4520c20f5f0cbc9dcc`, with `FIX4.diff` (`3a0d88b..6d5c253`) as the range under review.

## Task 1 — Verification of each change at the code

1. **Other-body blanking.** `Get-SkillReport` copies the render, then runs `Hide-KnownContainer` over every `$script:KnownContainers` member except `skills_instructions`, in the established order with INSTRUCTIONS first (tools/codex-context-probe.ps1:175-181, list at :330-334). A throw from the validating mask is caught and converted to `$ambiguous = $true` with the reason recorded in the comment (probe:182-187). Replacement is space-for-character inside `Hide-KnownContainer` (probe:406-408), so the offsets used at probe:192-206 still point into the raw render. VERIFIED.
2. **The 1/1 span rule.** Opens and closes are counted on the blanked scan, and anything other than exactly one opener and one close with the close after the opener sets `Ambiguous` before any entry is read (probe:188-203); the body is then taken from the validated span only (probe:204-206). VERIFIED.
3. **The gate.** `$skills.Ambiguous` blocks with a message naming both counts (probe:729-735), after the presence gate (probe:720-724) and before the empty-entry gate (probe:750-757), the scope gates (probe:784-801), and the override build (probe:860-866) and write (probe:937-950). Nothing ambiguous can reach the artifact. VERIFIED.
4. **New report fields.** `Ambiguous`, `OpenCount`, `CloseCount` are returned on every path (probe:262-265) and consumed at probe:729-732; no other consumer exists (grep: only probe:715 and the three one-argument test callers at test_codex_context_probe.py:78, :143, :1478). VERIFIED.
5. **My two round-4 Minor findings.** The stale suppression-render motivation in `Get-SkillReport` is re-pointed at its two pass-1 callers, and names the defect (probe:123-131). Both missing cost rows are added: a skill description naming a FEATURE family (spec:454-460) and a family name spelled across a line break (spec:461-467). The three "rewording one line" claims are corrected at probe:92-98, spec:419-423, and test:97-105, and the A21 row corrects itself in place (docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2725). VERIFIED.
6. **A23 row** matches what the code does (plan:2729). VERIFIED.

## Task 2 — Attack on the new first-render logic

I could not produce a wrong count or a clean report from any shape I traced:

- **Quoted pair inside any known body** (the round-8 reproduction, in either polarity): blanked before the count (probe:175-181), the real container is measured. Pinned end to end at test:1416-1443 and test:1446-1459; both fixtures place the pair inside the permissions body ahead of the real block (flagged.json:8 has exactly one `</permissions instructions>`, and it precedes `<skills_instructions>`).
- **Quoted pair OUTSIDE every known body**: with the real block present, opens=2 → Ambiguous → blocked (probe:198-203, :729). With the real block gone, a single surviving outside pair is indistinguishable from the block itself — that residue is the one narrowed shape the new empty-entry message names (probe:742-757), and it is accurate.
- **Quoted open-only or close-only literal outside all bodies**: opens=2/closes=1 or opens=1 with close before open → Ambiguous → blocked. This closes the round-4 corner I declined to raise (a quoted open-only literal in the global AGENTS.md landing `openAt` on the mention): inside INSTRUCTIONS it is now blanked (probe:178-181); outside it trips the count.
- **Interleaved or nested containers** (permissions opened, skills opened, permissions closed, skills closed; or the skills container nested inside another body): the validating mask throws on the orphan close (probe:383-388, :401-405) and the catch converts it to a block (probe:182-187, :729); a fully nested skills container disappears under blanking → BlockPresent=false → blocked at probe:720. Fail-closed both ways.
- **A second skills container hidden by blanking** (nested in another body, one real one outside): opens=1, the real one is measured, the nested one's entries are never disabled — but the family name survives on render 2 and the blunt rule stops the run (probe:899-908). No report carries the undercount.
- **Chunk boundary splitting the opener literal** on render 1: the exact literal is not found, opens=0, blocked at probe:720 — the flattening at probe:117 applies only to `Test-FamilyMentioned`. Fail-closed, correct direction.
- **Non-exact or case-variant containers**: thrown by the exactness scan (probe:470-486) inside `Test-PromptShape`, which runs on the same text one line before `Get-SkillReport` (probe:714-715).

**Legitimate renders newly refused:** only shapes already in the record — a quoted exact pair outside every known body trips the delimiter-count rule whose cost is recorded at spec:517-519, and the message names it. Nothing new is blocked that the record does not admit.

## Task 3 — Downstream consumers and stale callers

No caller passes a second argument to `Get-SkillReport` (probe:715; test:78, :143, :1478). `OpenCount`/`CloseCount` are consumed only in the Ambiguous block message. `Malformed`, `Entries`, `BlockPresent` consumers are unchanged from the round-4 PASS. `skills_after` remains 0 by construction (probe:909) and every consumer expects 0. Nothing downstream depends on a value the deleted second-render parse used to produce. PASS.

## Task 4 — Test integrity of the three new tests

All three fail on the pre-fix code: test:1440-1443 asserts the real count AND the absence of `/fake/` in the written override (pre-fix: `skills_before: 1`, fake path present); test:1458 asserts returncode 0 and 29 (pre-fix: blocked with "no entry could be read"); test:1482 asserts `Ambiguous/OpenCount/CloseCount` at the function, and its literals match the shipped fields (probe:262-265). The `rewritten` helper asserts the anchor exists before replacing (test:1119), and suppressed.json carries no family name (grep, 0 matches), so render 2 genuinely passes and the wrong count is what the test measures — not the blunt rule. None are vacuous.

## Findings

None.

Non-findings, recorded for the panel:

1. The Ambiguous block message always says the counts were taken "once every other known container's body was blanked" (probe:730-734), but when the blanking loop itself threw (probe:182-187) some bodies were NOT blanked when the counts at probe:190-193 were taken. The run still blocks in the correct direction; and in the shipped flow the path is unreachable, because `Test-PromptShape`'s validating mask throws on the same text first (probe:623-631). Message wording only; I am not raising it as a defect.
2. A23 says "three stale claims" corrected; the four texts carrying the claim were the probe comment, the spec paragraph, the test comment, and the A21 row — but the A21 row carries its own self-correction (plan:2725), so three claims plus a self-correcting row is an accurate reading. Not a defect.

## Unverified

- I have no execution tools: the both-hosts test counts, the live-probe result, and the override sha256 are taken as reported evidence. I verified each new test is CONSISTENT with the code paths I read and would fail on the pre-fix script, but I did not run them.
- Whether the real client can split a container literal across transport chunks on render 1 remains unverified; the code's direction (block at probe:720) is fail-closed either way.

## Verdicts

1. Implementation fidelity — PASS (A23 and the A21 correction verified at the code, probe:122-266, :714-757; spec:417-511; plan:2725, :2729; tests:1407-1482; no undeclared drift in the range).
2. Dispatch integrity — PASS (the write/hash/validate handoff is untouched at probe:918-960; every ambiguous or wrong-count input stops before the override is built at probe:860-866).
3. No false-clean path — PASS (every shape traced terminates in a block with an accurate cause, or in the correct measurement; the one hidden-container undercount is caught by the render-2 blunt rule at probe:899).
4. Honest scope — PASS (both record gaps from my round 4 are closed at spec:454-467; all "rewording one line" overstatements corrected; nothing overstates the guarantee to a user).
5. Test integrity — PASS (all three new tests fail on the pre-fix code; literals match the shipped fields; the fixture anchors are asserted).
6. Destructive/rejecting bugs — PASS (no `new-review-mirror.ps1` changes in this range; the new refusals are loud, correctly diagnosed blocks).

OVERALL: PASS
