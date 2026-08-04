<role>Adversarial reviewer, equal weight, in a two-model mode-diff debate. Round 2. You are not being asked to bless a fix; you are being asked to try to break it.</role>

<task>Round 1 you returned PASS on claims 2 and 5 and FIX on claims 1, 3, 4, 6, 7 and 8. Every finding was reproduced independently in the driver's session before it was accepted, and all six were applied. None was rejected. The repo is at C:/Users/Brandon/Documents/parallax, read-only. The APPLICATION diff is b4275588e950..c9d9cef75112 (base..head). Read whatever you need, including the round-1 state, which is unchanged except where named below.</task>

<rules>
Cite file:line for every claim you make or contest; uncited claims will be struck. Do not manufacture objections: if a fix stands, say PASS and move on. End each numbered item with PASS, FIX (with the specific fix), or ESCALATE.

Three project invariants bind this branch, and a violation of any of them is a finding regardless of whether the code "works":
- A claim may never be wider than its evidence.
- An unmade, failed, or unreadable measurement is never a clean one.
- A test is not evidence until it has been watched to FAIL for the reason it claims.

A FIX is new code and gets no discount. Your round-1 claim-1 finding was a defect INSIDE a fix that a previous reviewer's finding had produced hours earlier. Apply the same suspicion here.
</rules>

<what-was-applied>

**F1, from claim 1.** `-Fresh` now requires `knownRollouts` to be a non-null `[System.Array]` whose every element is a non-empty string; anything else is BLOCKED. `tools/read-codex-round-evidence.ps1`.

**F2, from claim 6b.** `-Resume` now reads the PREFIX's first line with a `StreamReader` under strict UTF-8, requires it to parse as a `session_meta` record, and requires its `payload.id` to equal the resumed session id. Only the first line is read, on the argument that the prefix hash already pins the rest.

**F3, from claim 8.** The mirror-location rule is now stated once, in `skills/multi-model-verify/references/backup-lane.md`, and `SKILL.md` matches it. `SKILL.md` was not edited; it already said the right thing.

**F4, from claims 3 and 6c.** `mirror-path-budget` now says the measured universe is the source AS ENUMERATED at pre-flight time and states outright that this is NOT a guarantee of equality with the universe `robocopy /E` later walks.

**F5, from claims 4 and 6d.** `mirror-identity-gate` now says the bridge proves matching OBSERVED ENDPOINTS and names the away-and-back mutation gap.

**F6, from claim 7.** Item 20's closure records the residue that survives F1 and F2, and corrects a stale oracle count and an over-wide "each watched to fail first" claim. Item 22's closure records ABA and the path-universe mutation window.

Six new oracles in `evals/multi-model-verify/test_codex_round_evidence.py`, five of them refusals watched to fail first, one a positive control.

</what-was-applied>

<claims>

1. F1 and F2 are complete for their own defect class. Specifically: no prior-state shape reaches `clean` where the inventory or the recorded provenance was not actually measured. Try to find a remaining input that reaches exit 0 and should not. Include the RESUME state's own fields, which F1 did not touch.

2. F2's "only the first line is read" argument is sound. The claim is that the prefix hash already pins every other line, so re-parsing them would add nothing. Try to find a case where the first-line check passes, the prefix hash passes, and the rollout is still not the session the state names.

3. The three narrowed regions now match what the code proves, in both directions. A region that is now WEAKER than the code actually is would also be a defect: the contract would be under-claiming a guarantee the operator could have relied on. Check both directions.

4. The two amended closures are now complete. Look for a limitation the code plainly has that item 20's or item 22's closure still does not admit, and for any statement in them that is now wider than what the applied code does.

5. The six new oracles test what they claim to test. Five assert refusals and one asserts an acceptance. Try to find one that would still pass if its target check were removed or inverted.

6. The application is scoped. Nothing outside F1 through F6 changed behaviour. A change in this diff that is not traceable to one of the six is a finding, whether or not it is an improvement.

</claims>

<boundaries>
Already decided and NOT under debate: the four backlog items being closed and their dispositions; the bump to 0.21.0; the release grouping; the 260-character policy threshold; reading the JSONL rollout rather than the human transcript; and the decision NOT to build from an immutable filesystem snapshot in this release. That last one is the alternative you proposed for three round-1 findings; the response was to narrow the claim, which is what these invariants ask for. Re-proposing the snapshot design is out of scope, but a claim that is STILL wider than its evidence after narrowing is in scope.

Out of scope: backlog items 18, 19, 24, 25, 26 and 27 are deliberately not in this release. `plan-mode-debate-runs` failing the behavioural suite is item 18's known-flaky case.

The `SKILL.md` token-budget warning from `skill_lint --strict` is open backlog item 19 and is not a finding here.
</boundaries>

<final-check>List any claim you could not verify against files you actually read, as UNVERIFIED. Do not fold unverified material into your verdict. If all six stand, say so plainly; a round that finds nothing is a real outcome.</final-check>
