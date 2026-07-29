All verification is complete. Here is the round-6 reply against head `881b676048208761f97f477ec86ce0585bf42ca2`, with `FIX5.diff` (amendment A24) as the range under review.

## Task 1 — Verification of each change at the code

1. **Entries read from the raw render.** The located span's body is sliced from `$text`, not `$scan` (tools/codex-context-probe.ps1:226). The offsets come from `$scan` (probe:206-207), and the blanking that produced `$scan` is space-for-character (probe:427-428), so scan offsets equal raw offsets. If the blanking loop throws, `$ambiguous` is set (probe:196-201) and the substring at probe:226 is never reached (gate at probe:224). VERIFIED.
2. **Every shape judged.** The new judge (probe:218-223) accepts exactly 0/0 or an ordered 1/1 and sets `Ambiguous` otherwise. Close-only (0/1), open-only (1/0), 2/2, and a reversed 1/1 all now report `Ambiguous` true at the function. When the blanking loop already threw, the judge is correctly skipped (probe:218). VERIFIED.
3. **Message wording.** The Ambiguous block message now says the counts were taken "after blanking the other known containers' bodies as far as they could be blanked" (probe:755-760), matching my round-5 non-finding. The thrown-cause path and the counted path are both honestly described. VERIFIED.
4. **One-caller comment.** The comment now says "There is ONE production call site, not two" (probe:132-133). Grep confirms: the only production call is probe:735; probe:914 is a comment. VERIFIED.
5. **Spec paragraph** recording the round-9 defect and the locate-vs-read split is at docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:506-513, and the **A24 row** at docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2731 matches what the code does. VERIFIED.

## Task 2 — Attack on the new logic

**No false-clean shape found.** Traced:

- **Round-8 polarity (quoted pair in an earlier body):** still blanked before the count (probe:192-195), the real span located, entries read from raw at the real offsets — the fake never enters the measurement. Pinned end to end at test:1416-1443.
- **Round-9 polarity (quoted pair inside the skills body spanning a real entry):** located on scan, entries read from raw, the spanned entry survives. Pinned at test:1485-1516; pre-fix code returns 28/`False` for the count and misses `userskill5`, so the test genuinely fails there.
- **Quoted skills pair inside a description:** the skills body is never blanked in `$scan` (probe:193), so opens=2 → Ambiguous → blocked at probe:749. Fail-closed.
- **Nested container inside the skills body whose content carries entry-shaped lines:** raw read now audits those lines; anything with an unplaceable path blocks at probe:810-814, and joined entries block at probe:784-796. This is the pre-A23 read semantics the round-9 finding explicitly demanded; no new false clean.
- **Blanking loop throws mid-way:** no substring is taken (probe:224 gate), counts are reported as counted, message no longer claims a completed blanking. Fail-closed with honest wording.

**But the locator loop disagrees with the shape scanner one line away — see Finding 1.** This is the same "one function away" class as rounds 7→8, and it survives A24 because A24 rewrote the judge and the read, not the loop's non-quiet call.

## Task 3 — Downstream consumers

`Ambiguous`, `OpenCount`, `CloseCount` are consumed only at probe:749-760; `Entries` consumers (probe:776-808) are unchanged and now receive the raw-read list, which every fixture-based consumer (test:128-157) already expects. No caller passes a second argument (grep: probe:735; test:78, :143, :1478, :1511, :1531, all one-argument). PASS.

## Task 4 — Test integrity of the two new tests

Both fail on the pre-fix code: test:1485-1516 pre-fix yields `28 False False` against the asserted `["29","False","True"]` (the blanked body erased `userskill5`); test:1519-1535 pre-fix yields `False False 0 1` against `["False","True","0","1"]` (the old judge skipped opener-less shapes). Fixture properties check out: flagged.json carries the permissions container ahead of the skills block with `- userskill5:`/`- userskill6:` entries (fixtures/codex-prompt-input/flagged.json:8), and suppressed.json carries zero occurrences of `skills_instructions` (grep, 0 matches), so the appended close-only literal is genuinely the only skills marker. Neither test is vacuous.

## Findings

1. **Minor — tools/codex-context-probe.ps1:193-195 — the locator loop judges quoted literals inside skill descriptions that the shape scanner, one line earlier, deliberately treats as free text.** The loop runs `Hide-KnownContainer` NON-quiet (probe:194) while skipping `skills_instructions` (probe:193), so the skills body is never blanked in `$scan`. A skill description quoting an exact, solitary `<environment_context>` or `</environment_context>` (or `<multi_agent_mode>`) literal — containers processed AFTER skills in the masking order (probe:350-354), and not feature families, so the blunt gate at probe:633-642 does not fire — throws at probe:403-408/409-417, the catch at probe:196-201 converts it to `Ambiguous`, and the run blocks. `Test-PromptShape` passes the same text: its quiet stage blanks the skills body before environment_context is ever counted (probe:499, same order), and the stated principle is that skill descriptions "may legitimately quote a malformed tag" (probe:458-460) — the rule established by the round-7 reproduction of exactly this class (probe:392-401). Two consequences: (a) a legitimate review is refused, a cost the design's accepted-limits record does not admit (spec:515-555); (b) the refusal is misdiagnosed — the block message reports the SKILLS container's boundaries as ambiguous with "1 opening and 1 closing markers" (probe:755-760) while the real cause (`the <environment_context> container never closes`, probe:405-407) is discarded. Fail-closed throughout, so this is a wrong-diagnosis/unrecorded-cost defect, not a gate defect. Minimal fix: with A24's raw-read in place the locator no longer needs the skills body visible in `$scan` — blanking it too (dropping the skip at probe:193) erases description free text exactly as `Test-PromptShape` already does, while the skills delimiters survive blanking (probe:427-428) so locating is unaffected, and a genuinely nested second skills container is still refused by the validating mask's count rule one line earlier (probe:510 inside probe:644-651). Add a regression pinning a description that quotes a solitary exact `<environment_context>`: 29 entries measured, no block.

Non-finding, recorded for the panel: A24's universal judge makes `Ambiguous` true for 0/1 and 1/0 shapes where `BlockPresent` is also false, so the caller stops on the missing-block message (probe:740-744) before the Ambiguous gate (probe:749) — the new field value is only observable at the function. That is the intended totality, and test:1519-1535 pins it there. Not a defect.

## Unverified

- I have no execution tools: any both-hosts test counts, live-probe results, and override hashes for this head are not in my workspace to check; FIX5.diff carries no evidence block. I verified each new test is CONSISTENT with the code paths I read and would fail on the pre-fix script, but I did not run them.
- Finding 1 is traced at the code, not reproduced on a host. The two PowerShell behaviors it leans on (non-quiet throw at probe:403-408; quiet `continue` at probe:404 with the masking order at probe:350-354) are read, not executed.
- Whether a real client render can place a solitary exact `<environment_context>` literal inside a rendered skill description is INFERRED from the descriptions-are-free-text rule (probe:241-245, :458-460), not observed.

## Verdicts

1. Implementation fidelity — PASS (A24 applied exactly as recorded: probe:172-188, :212-226, :749-761, :122-133; spec:506-513; plan:2731; tests:1485-1535; no undeclared drift in the range).
2. Dispatch integrity — PASS (the write/hash/validate handoff is untouched in this range; every ambiguous or wrong-count input still stops before the override is built).
3. No false-clean path — PASS (every shape traced terminates in a correctly diagnosed block or in the correct raw-read measurement; the round-8 and round-9 polarities are both pinned).
4. Honest scope — FIX, Minor (Finding 1: a legitimate-render refusal the accepted-limits record does not admit, contradicting the free-text principle the scanner states at probe:458-460).
5. Test integrity — PASS (both new tests fail on the pre-fix code; fixture anchors verified at flagged.json:8 and by grep on suppressed.json).
6. Destructive/rejecting bugs — FIX, Minor (Finding 1: the locator rejects a legitimate run shape the shape scanner accepts, and names the wrong container and wrong counts when it does; no `new-review-mirror.ps1` changes in this range).

OVERALL: FIX
