I've read the brief, both documents, and the live files they make claims about. Verdicts below, each grounded in citations from files read this run. Files anchored: `docs/superpowers/specs/2026-07-27-contract-coverage-design.md` ("spec"), `docs/superpowers/plans/2026-07-27-contract-coverage.md` ("plan"), `skills/multi-model-verify/references/backup-lane.md`, `skills/multi-model-verify/references/panels.md`, `skills/multi-model-verify/references/fallbacks.md`, `skills/multi-model-verify/references/frozen-plan-format.md`, `agents/fable-panel-reviewer.md`, `evals/multi-model-verify/test_backup_lane.py`, `evals/multi-model-verify/test_seat_reshuffle.py`.

---

## Per-claim review

**Claim 1 — Coverage, not replacement: PASS.**
The spec's Goal keeps substring pins and explicitly declines to replace the existing suite (spec docs/superpowers/specs/2026-07-27-contract-coverage-design.md:30-36); the Approach section records the three rejected alternatives with reasoning (:44-59). Pushing as invited: the mechanism is the right one for the defect class, because the defect was never wrong pins but *coverage gaps nothing measured* (spec :27-28) — checksums would lock bytes without naming the unlocked sentence, and generating pins from the document would make the document its own witness. The one real weakness (any pin anywhere satisfies any region) is stated knowingly in Accepted limits (spec :156-160), not hidden. No refutation.

**Claim 2 — Marking beats alternatives, on evidence: PASS.**
Instance 10's sentence `That is a route-attribution failure` (backup-lane.md:57) contains no modal word, so the keyword-rejection rationale is factually grounded (spec :47-52). The whole-file-scanning rejection is also grounded: the reference files demonstrably interleave rules with probe records and dates (backup-lane.md:27-32, :60-70).

**Claim 3 — Containment beats overlap, correct direction: PASS.**
The direction is right in the plan's code: `sentence in pin` (plan docs/superpowers/plans/2026-07-27-contract-coverage.md:415) and the global constraint at plan :14. Instance 11's shape — a pin that touched the sentence but stopped at `IS transient` — is corroborated by the current test file's own comment (test_backup_lane.py:442-447).

**Claim 4 — Pins via `ast`, not a registry: PASS, with one UNVERIFIED sub-figure.**
Implicitly concatenated literals are indeed how the pins are written (test_backup_lane.py:92-97, :127-128; test_seat_reshuffle.py:159-161), and the registry trade-off is stated accurately (spec :56-59). The exact measured counts — 172 string constants, 40 over 60 characters (spec :89-90) — I cannot confirm: I have no execution tools, and I will not pretend to have counted them by eye. See UNVERIFIED list.

**Claim 5 — Declared inventory closes the deletion hole: PASS.**
The hole is real (delete markers and coverage checks nothing, spec :114-116) and the plan's test compares declared vs. found in both directions (plan :628-639). The residual — deleting a region *and* its `DECLARED_REGIONS` entry in one change — is a two-file edit visible in review; nothing mechanical can do better, and the design doesn't claim it does.

**Claim 6 — Splitter fails in the safe direction: PASS, with one recorded caveat.**
The measured fact checks out: exactly six `e.g.` occurrences exist in the reference set (fallbacks.md:16, fallbacks.md:240, fallbacks.md:268, frozen-plan-format.md:93, frozen-plan-format.md:103, model-prompting-notes.md:18), and none is followed by whitespace plus a capital — the tricky one, frozen-plan-format.md:93-94, is followed by a newline then a backtick. Caveat I am recording, not litigating: the absolute "cannot produce a silent pass" (spec :108-110) is very slightly overstrong — in theory a mis-split whose two fragments each happen to sit inside two *different* existing pins would pass while the whole sentence stays unlocked. In practice the two fragments pinned piecewise still lock the text contiguously except at the boundary, and no mis-split exists today, so the exposure is negligible. Not worth a document edit; noting it so the absolute wording is on the record as approximate.

**Claim 7 — Prerequisites verified, not assumed: PASS on verifiable substance; two legs UNVERIFIED.**
Corroborated in-repo: no `conftest.py` exists anywhere under `evals/` (Glob, zero matches) and `evals/multi-model-verify/` has no `__init__.py`, which is consistent with the sibling-module import working under pytest's default prepend import mode. The three historical instances are corroborated by in-repo comments written at the time: instance 10 (test_backup_lane.py:147-152), instance 11 (test_backup_lane.py:442-447), instance 12 (test_seat_reshuffle.py:72-76, :127-131). What I cannot verify: that `skill_lint --strict` and `skill_scanner` actually ran clean with markers present, and that `git show` at the three commits yields the quoted text (plan :470-473). No execution tools. See UNVERIFIED.

**Claim 8 — Predictions simulated, two were wrong: PASS.**
Every checkable element confirms against the live tree. The rotation guard paragraph (backup-lane.md:52-70) splits into exactly six sentences; only sentence 5 is pinned whole today (test_backup_lane.py:163-165), while sentences 2 and 3 carry only fragment pins (test_backup_lane.py:141-142, :145, :152) — matching plan :597-601 exactly, including the decision to leave sentences 1, 4, 6 outside the markers. The five unlocked sentences are confirmed: the panels.md floor sentence's pins are fragments (test_seat_reshuffle.py:134-136), the agent sentence's pins are fragments (test_seat_reshuffle.py:78-80), and the unavailable-class disposition is pinned only by the fragment at test_seat_reshuffle.py:173. I also verified the corrected pins in the plan match the live document text exactly, including the em dash and the `**` formatting (plan :721-742 vs. backup-lane.md:53-60; plan :856-862 vs. panels.md:73-77; plan :878-883 vs. agents/fable-panel-reviewer.md:30-33; plan :989-999 vs. fallbacks.md:220-226). The process sub-claim (that the session first predicted coverage) is not independently verifiable, but its factual content — five sentences unlocked — is.

**Claim 9 — Checker proven before any live region is marked: PASS.**
Task 3 (plan :451-582) precedes all marking tasks (:586 onward); fixtures are hermetic with the stated rationale (plan :453-456); the non-vacuity test asserts exactly one region per fixture (plan :557-563), so a silently-misparsing fixture cannot pass the three regression tests vacuously. Task ordering is red-first throughout, and the one vacuous-pass window — Task 4 Step 2, where the coverage test passes over zero regions — is guarded by the inventory test being red at the same moment with two declared ids missing (plan :648-652).

**Claim 10 — Accepted limits stated, not hidden: PASS.**
All three limits are explicit in the spec (:154-165), and the self-satisfaction hole is closed in the plan by excluding the checker's own module from pin collection with the reason written next to it (plan :615-620). I additionally confirmed the fixture pins files cannot leak into live coverage: `PIN_PATHS` globs only top-level `test_*.py` (plan :618-620), and `contract_coverage.py` doesn't match `test_*.py`, so the checker module's docstrings are out too.

**Claim 11 — Scope is six regions: PASS.**
Six ids, enumerated (plan :931-938). "Eleven classes" in fallbacks.md is countable as stated: seven `###` headings under `## Failure classes` (fallbacks.md:55, :65, :73, :84, :90, :100, :113) plus `missing-rollout` (:107-109), `panel-lane-loss` (:190), `panel-lane-unavailable` (:210), and the reference-failure stop (:247) = 11. The count is mildly convention-dependent, but the substance — two of many, chosen on recorded failures — holds. On "the right six": the earlier instances (7-9) sit in text whose fixes already landed as whole-sentence pins (test_backup_lane.py:256-258), so marking those regions would add little; the recency-based selection is defensible even though the spec's stated rationale ("a recorded failure behind it", spec :189-190) would literally also cover the older sites.

## Boundary items I was asked to push

- **Brittleness (the perpetually-red weakening risk):** bounded, and the design knows the enemy — this repo's own comment records that "the predictable response to a perpetually red test is to weaken it" (test_backup_lane.py:488-490). Mitigations are concrete: whitespace normalization absorbs reflows (plan :18), regions are small and dense by construction (spec :74-77), and the failure message names the exact sentence plus the one-line fix (spec :149-152). The real residual is that normalization is whitespace-*only*, so formatting churn (`**`, backticks, em dash) inside a marked region turns red — but formatting is load-bearing in these contracts (test_seat_reshuffle.py:133 depends on the exact `**` text), so that redness is signal, not noise. This does not rise to an objection.
- **Task order:** safe, for the reasons under claim 9. Each task ends on all four gates (plan :21-26).
- **Missed entirely:** nothing that rises to an objection. New-contract-text marking is a process rule only (plan :1040-1047), but the spec accepts unmarked-text exposure explicitly (spec :163-165) rather than hiding it.

## UNVERIFIED (not folded into any verdict)

1. Exact string-constant counts in `test_backup_lane.py` (172 total, 40 over 60 chars; spec :89-90) — no execution tools.
2. The "529 existing assert statements" figure (spec :33) — same reason.
3. That `skill_lint --strict` and `skill_scanner` ran clean with HTML markers present, and that the full suite stayed green (plan :26) — cannot run them.
4. That `git show 4d8a121 / 8eacc8a / f9fd9b9` yields the exact fixture text quoted (plan :470-495) — cannot run git; corroborated only indirectly by current in-repo comments cited under claim 7.
5. The full-suite baseline test counts threaded through the plan (179/188/192/194 passed; plan :261, :440, :575, :756) — internally consistent arithmetic (each delta matches the tests added per task), but the baseline is unverifiable by me.

## Verdicts

1. PASS 2. PASS 3. PASS 4. PASS (counts UNVERIFIED) 5. PASS 6. PASS (caveat recorded: "cannot produce a silent pass" is approximately, not absolutely, true) 7. PASS on substance (two legs UNVERIFIED) 8. PASS 9. PASS 10. PASS 11. PASS

**Overall: PASS.** The design targets the actual defect class, its load-bearing claims survive checking against the live tree, its self-proof precedes any live marking, and its limits are stated where a reviewer can find them. Converging in round 1.

To resume this session: kimi -r 08d55837-99ba-4a1f-8a03-dd7d622b3017
