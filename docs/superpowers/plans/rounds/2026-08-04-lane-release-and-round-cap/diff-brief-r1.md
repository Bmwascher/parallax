<role>Adversarial reviewer, equal weight, in a two-model DIFF debate. Neither side's claim outranks the other's; only evidence does.</role>

<task>Refute or confirm each numbered claim about the range `02adc87..HEAD` on branch `feat/lane-release-and-round-cap` in the parallax repo at C:/Users/Brandon/Documents/parallax, read-only. The frozen plan, its Amendment 1, the per-task build records and the Fable review record are all appended in `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md`. The backlog items it closes (26, 24, 25) and the one it files (29) are in `docs/superpowers/plans/2026-07-27-0150-backlog.md`. Read whatever you need.</task>

<rules>
Cite repo-relative file:line for every claim you make or contest; uncited claims will be struck. Do not manufacture objections: if a claim stands, say PASS and move on. End each numbered claim with PASS, FIX (with the specific fix) or ESCALATE.

Three project invariants bind this repo, and a violation of any is a finding regardless of whether the design works:
- A claim may never be wider than its evidence.
- An unmade, failed, or unreadable measurement is never a clean one.
- A test is not evidence until it has been watched to FAIL for the reason it claims.

Check spec fidelity against the plan's REVISED task list in Amendment 1, not the original. Amendment 1 DELETED the original task 3; if you find it implemented, that is drift.

A Fable whole-branch review already ran and returned no Critical and no Important, five Minor. Its record is in the plan file. Attack the DISPOSITIONS, not just the code: two were fixed, one was filed as item 29 rather than fixed, two were fixture repairs. A finding Fable missed is worth more than one it made.
</rules>

<claims>

1. **Task 3's refusal is correctly narrowed rather than weakened.** Acquire now refuses a proposed owner measured DEAD (`tools/kimi-lane-lock.ps1`, top of `Invoke-AcquireMode`). The plan asked for "does not measure LIVE"; that was built first and two shipped fault-seam oracles went red, because UNMEASURABLE means the pid lookup SUCCEEDED and only the start-time read failed, so refusing it locks the TRUE owner out of its own lock. The claim shipped is "refuses an owner measured DEAD", never "the recorded owner is live", and the residual (a running pid with WRONG ticks still records when the start-time read fails) is stated in the tool and pinned. Attack the narrowing: is DEAD-only the right line, or does the residual reopen the mutual-exclusion hole this task exists to close?

2. **Task 2's ancestor walk is a defensible trade and the branch's weakest point. Attack it hardest.** `-ResolveOwner` now walks past `pwsh.exe`, `powershell.exe`, `cmd.exe`, `conhost.exe` and stops at the first ancestor that is not one, reporting its NAME, with 16 levels and every failure direction landing on exit 2 with empty stdout. THE COST: a genuinely long-lived orchestration script running inside one of those four hosts is SKIPPED and the owner resolves to ITS parent, which can outlive the debate. That trades backlog item 26's visible half (a stuck lane) against its silent half (two debates on one credential). Is the trade right, is the transport list right, is 16 the right bound, and is there a resolution that does not make this trade at all?

3. **Task 4's optional `ownerName` migration is complete and safe in both directions.** It is in `$HeldFields` and NOT `$HeldRequired`, because a required field would have made every pre-upgrade HELD record MALFORMED at the next cache update. Both migration directions are pinned; both record writers carry it (fresh acquire AND reclaim); both wrapper call chains forward it and neither forwards an empty value; all four copies of the recovery command's EXACT field-set check moved together. Find a consumer that was missed, or a record shape that now classifies differently than the contract says it should.

4. **Tasks 1 and 5 state their own limits.** The new `lane-debate-close` region in `backup-lane.md` names the release step at the debate's close AND says it is advisory, because pinned prose does not execute a teardown and nothing detects a debate that finished without one. The doctor's quiet-holder row decides all four rules the backlog demanded (30 minutes; files under the recorded `debateHome`, recursive, directories excluded; newest `LastWriteTimeUtc`; total silence on ANY partial read failure) and cannot move a verdict or a reclaim right. Attack both: is the doctor's prose precise enough that two runs produce the same answer, and can the quiet reading leak into a reclaim decision by any path?

5. **Tasks 6 and 7 are decidable by a reviewer who was not there.** The round cap counts CONSECUTIVE CONTESTED exchanges, a round is contested while any contested point is OUTSTANDING (raised that round or earlier), a caller-set total fix-verify budget PAUSES for user authorization rather than certifying, and termination requires an adjudicated dry round with no new substantive finding AND no outstanding contested point. The scope rule defines SAME CLASS as a named invariant rather than a similar symptom and VERIFICATION SURFACE as enumerated BEFORE the finding. Attack it: can two independent reviewers reach different answers on the same case under this text, and is there a debate shape that still runs unbounded?

6. **The retained round records support exactly the claims made about them.** `docs/superpowers/plans/rounds/2026-08-04-transport-and-mirror/` holds 7 plan replies with briefs and 5 diff replies, and its README states both what they establish and what they do not. Check the README's table against the replies themselves. A verdict attributed to a round that the reply does not carry is a finding.

7. **Item 29 was filed rather than fixed for a stated reason, and that reason holds.** The ancestry walk has no creation-time ordering guard, so a pid reused inside the walk's own window resolves a wrong live owner. The guard is one comparison. It was NOT added because no test here can watch it fail for the reason it claims, and the residual is named in the code. Is that the right call, or is a guard whose refusal path is unwatched still better than a named residual?

8. **The plan's and the branch's stated limits are complete.** Look for a limit this branch plainly has that it does not admit anywhere: not in the plan, not in a build record, not in the shipped text, not in a backlog item.

</claims>

<boundaries>
Already decided and NOT under debate: the release grouping; that the lock's staleness rule stays LIVENESS and never a clock; that backlog item 28 (the strict JSON lexer) and item 19 (the SKILL.md token budget) are out of scope for this branch.

Out of scope: backlog items 7, 9, 11, 12, 15, 18, 19, 27, 28.
</boundaries>

<final-check>List any claim you could not verify against files you actually read, as UNVERIFIED. Do not fold unverified material into your verdict.</final-check>
