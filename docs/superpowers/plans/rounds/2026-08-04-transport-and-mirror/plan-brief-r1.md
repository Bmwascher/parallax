<role>Adversarial reviewer, equal weight, in a two-model mode-diff debate. You are not advising a decision that has been made; you are trying to refute it.</role>

<task>Refute or confirm each numbered claim below about the parallax 0.21.0 branch. The repo is at C:/Users/Brandon/Documents/parallax and you have read-only access to it. The range under review is 50575a3ee8a002b0717f64104883057c727e4c18..b427558 (base..head), 16 files. Read whatever you need.</task>

<rules>
Cite file:line for every claim you make or contest; uncited claims will be struck. Do not manufacture objections: if a claim stands, say PASS and move on. End each numbered claim with PASS, FIX (with the specific fix), or ESCALATE.

Three project invariants bind this branch, and a violation of any of them is a finding regardless of whether the code "works":
- A claim may never be wider than its evidence.
- An unmade, failed, or unreadable measurement is never a clean one.
- A test is not evidence until it has been watched to FAIL for the reason it claims.
</rules>

<claims>

1. `tools/read-codex-round-evidence.ps1` cannot report `clean` for any round whose recorded prompt is not the declared brief. Specifically: no input reaches exit 0 where the client recorded something other than the brief, or where the byte range this call appended cannot be established, or where any part of the measurement could not be made. Try to find an input that reaches `clean` and should not.

2. The binding's claim ceiling is honest. It is stated as CLIENT-ECHO evidence in `skills/multi-model-verify/references/model-prompting-notes.md` (region `codex-brief-binding-record`) and in the backlog closure for item 20. Verify that nothing in the branch - tool comments, contract text, SKILL.md, commit messages - implies it proves anything about what a server or model received.

3. The mirror path-budget pre-flight in `tools/new-review-mirror.ps1` measures the same universe robocopy creates, and refuses before creating anything. Try to find a repo shape that BUILDS but should have been refused, or that is refused but should have built.

4. The mirror construction bridge ties the two recorded identities together. Steps 3 and 4 (source head unmoved across the copy; copied tree carries the captured source head) make it impossible to record a `source_head` and a `mirror_head` that are individually valid but do not describe the same construction. Try to find a path to a printed record where either bridge check did not run.

5. The two mirror test seams are one-way: setting either can only cause a build to fail, never cause a build to succeed that would otherwise have failed, and neither writes to the source tree. They are `PARALLAX_MIRROR_SEAM_FAIL_SOURCE_STABLE` and `PARALLAX_MIRROR_SEAM_FAIL_COPIED_HEAD`. This claim was wrong twice before and both earlier shapes are documented in the plan's Amendments 10 and 11; check the CURRENT shape rather than the history.

6. The four contract regions added by this branch (`codex-brief-binding-calls`, `codex-brief-binding-record`, `mirror-path-budget`, `mirror-identity-gate`) each describe what the code actually does, clause by clause. A contract that describes a different rule than the code implements is the defect class this repo cares most about. Check each clause against the implementation.

7. The four backlog closures in `docs/superpowers/plans/2026-07-27-0150-backlog.md` (items 20, 21, 22, 23) state their NOT-COVERED limitations honestly and completely. Look for a limitation the code plainly has that its closure does not admit.

8. The release is coherent as shipped operator guidance. Someone reading `skills/multi-model-verify/SKILL.md` plus its references end to end can run a review with the three new mandatory steps without hitting a contradiction, a missing input, or an undocumented artifact they are expected to author.

</claims>

<boundaries>
Already decided and NOT under debate: the four backlog items being closed and their chosen dispositions; the decision to bump to 0.21.0; the release grouping; the 260-character limit as a policy threshold rather than a measured maximum; the choice to read the JSONL rollout rather than the human transcript.

Out of scope: backlog items 18, 19, 24, 25, 26 and 27 are deliberately NOT in this release. Their absence is not a finding. `plan-mode-debate-runs` failing the behavioural suite is item 18's known-flaky case.

A prior whole-branch review by a Claude-family reviewer already ran on this exact range and its findings were applied. Do not assume it was right. Two of its findings were WRONG and are recorded as such in the plan's Amendment 9 and in Amendment 10's narrowing paragraph. You are a different vendor and your independence is the point.
</boundaries>

<final-check>List any claim you could not verify against files you actually read, as UNVERIFIED. Do not fold unverified material into your verdict.</final-check>
