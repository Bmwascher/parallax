<role>Adversarial reviewer, equal weight, in a two-model PLAN debate. Nothing is built yet. Your job is to attack the plan before it costs implementation.</role>

<task>Refute or confirm each numbered claim about the 0.22.0 plan at `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md`. The repo is at C:/Users/Brandon/Documents/parallax, read-only. It closes backlog items 26, 24 and 25, whose full text is in `docs/superpowers/plans/2026-07-27-0150-backlog.md`. Read whatever you need.</task>

<rules>
Cite file:line for every claim you make or contest; uncited claims will be struck. If a claim stands, say PASS and move on. End each numbered claim with PASS, FIX (with the specific fix), or ESCALATE.

Three project invariants bind this repo, and a violation of any is a finding regardless of whether the design "works":
- A claim may never be wider than its evidence.
- An unmade, failed, or unreadable measurement is never a clean one.
- A test is not evidence until it has been watched to FAIL for the reason it claims.

This is a PLAN debate. Prefer findings that change what gets built over findings about wording, and say which kind each is.
</rules>

<claims>

1. **Task 2 and Task 3 together are the right split of item 26's severe defect.** The item reports that `-ResolveOwner` can return a different pid per call under a wrapping harness, making the recorded owner read as DEAD almost immediately. That instability is ANOTHER session's measurement and is not reproduced here; what IS measured here is that the resolution returns the direct parent and nothing else (`tools/kimi-lane-lock.ps1:741`). The plan therefore proposes to make the failure LEGIBLE (report the resolved process name) and to stop the doctor's recovery command re-resolving at teardown, while explicitly NOT claiming the instability is fixed. Attack that split: is there a fix available here that actually closes the mutual-exclusion hole without a wrapping harness to test against, and is the plan wrong to leave it open?

2. **Task 3 identifies a real, independently reachable defect.** The claim is that a release which RE-RESOLVES the owner cannot release a lock whose recorded owner came from a process that has since exited, and that `-Status` already prints the complete recorded identity, so a release must read it from there. Verify both halves against the shipped doctor text and the lock tool. If the re-resolution is not actually on the release path, this task is built on a misreading and I want to know now.

3. **Task 2's field addition is safe for every existing caller.** Adding `ownerName` to the `-ResolveOwner` record changes a schema that at least one shipped caller validates with an EXACT field-set check. Find every consumer of that record and say whether the plan's stated coupling (the doctor command changes in the same task or the field does not land) is sufficient, or whether a third party breaks silently.

4. **Task 4's quiet-holder row cannot become the age-based expiry the design already rejected.** The constraint is that it changes nothing about reclaim rights, never moves the row off OK, and degrades to SILENCE when the debate home is unreadable or gone. Try to find a way the informational row still leaks into a reclaim decision, or a way "quiet" gets read as "abandoned" by an operator following the doctor's own output.

5. **Task 5's round-cap change is supported by its evidence and does not remove a protection.** The proposal: the cap counts rounds carrying CONTESTED points, a round whose findings are all accepted resets it, and the debate ends on a round producing no new accepted finding. Three runs are cited, including this repo's own 0.21.1 debate - 7 rounds, 0 contested, cap hit at 4, and rounds 5 and 6 each returned ESCALATE on real defects. Attack it: what stops a fix-verify loop running unbounded when the session is the one deciding a finding is "accepted"? The session both accepts findings and decides when to stop, and that is the same actor.

6. **Task 6's scope rule is decidable by a reviewer who was not there.** The rule: fix a pre-existing defect of the SAME CLASS as what the branch already fixes AND on the surface the verification will exercise; record anything else for a follow-up; do not certify a module whose follow-up has not landed. Both "same class" and "the surface the verification exercises" are judgement calls. Say whether two independent reviewers would land in the same place, and if not, what would make them.

7. **The plan's stated limits are complete.** It says it will not close the `-ResolveOwner` instability and leaves item 28 out of scope. Look for a limit the plan plainly has that it does not admit.

</claims>

<boundaries>
Already decided and NOT under debate: the release grouping (26, 24, 25 in 0.22.0); that the lock's staleness rule stays LIVENESS and never a clock, because a predecessor expired holders by AGE and that let anyone break a live round; and that item 28's strict JSON lexer is out of scope.

Out of scope: backlog items 7, 9, 11, 12, 15, 18, 19, 27, 28.
</boundaries>

<final-check>List any claim you could not verify against files you actually read, as UNVERIFIED. Do not fold unverified material into your verdict.</final-check>
