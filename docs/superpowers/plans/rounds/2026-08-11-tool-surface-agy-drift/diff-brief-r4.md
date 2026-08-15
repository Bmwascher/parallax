<role>Adversarial reviewer, equal weight, in a two-model DIFF debate. Round 4. Neither side's claim outranks the other's; only evidence does.</role>

<task>Round 3 returned four FIX and three PASS. Every finding was verified against the code before anything changed, and every one was ACCEPTED. Adjudicate the fixes. A FIX is new code and gets no discount.

Range is now `ef428c3..ca93356` on branch `0.24.0-tool-surface-agy-drift`, repo C:/Users/Brandon/Documents/parallax, read-only. Your round-3 reply is retained verbatim at `docs/superpowers/plans/rounds/2026-08-11-tool-surface-agy-drift/diff-reply-r3.txt`. The session's adjudications are amendment 12 of `.git/parallax/application-checkpoints/2026-08-11-1630-7945ac1-0240-build.md`.

**THIS IS THE CAP ROUND.** The meters declared before round 1 were 4 consecutive contested exchanges and a total fix-verify budget of 4 units, both authorised by the user in advance. This round reaches both. Exhaustion PAUSES the debate for the user's authorization; it never certifies. So one thing is needed from you beyond the per-claim verdicts, stated plainly at the end:

**Is this range DRY?** Dry means no new substantive finding AND no outstanding contested point. If it is not dry, say what remains and how serious it is, because the user is deciding whether to authorise more rounds and needs the size of the remainder, not a reassurance. Do not soften it to help the branch land, and do not manufacture an objection to look rigorous. Both would corrupt the decision.</task>

<rules>
Cite repo-relative file:line for every claim. End each numbered item PASS, FIX (with the specific fix) or ESCALATE. Do not manufacture objections: if a fix stands, say PASS.

The three invariants still bind: a claim may never be wider than its evidence; an unmade, failed or unreadable measurement is never a clean one; a test is not evidence until it has been watched to FAIL for the reason it claims.
</rules>

<claims>

1. **The two data faults report separately.** A missing `data` member and a present-but-null one now set different flags and produce different blocked reasons, in both the no-result and the partial-stream paths (`tools/codex-tool-surface-probe.ps1`). The case that used to REQUIRE the wrong sentence now refuses it, and a second case asserts the two reasons differ. **Watched to fail:** both were red against the pre-fix code. Attack the wording and the paths: is there a route where one fault still reports as the other?

2. **Every feature entry is validated, not just the policed ones.** A null element, a missing or non-string or blank name, a missing enablement member, and a non-boolean enablement each block, wherever they sit in the list (`tools/codex-tool-surface-probe.ps1`). Four fail-first cases, all red before the fix.

   **A RISK I am declaring rather than leaving for you to find, because it is an availability risk and not a correctness one.** This is strict by intent: it blocks the whole review if any feature in the surface is malformed by its rules. The evidence for that being safe is the live 2026-08-14 reading, where all 88 features carried a non-empty string name and a real boolean. If codex ever ships one feature whose value is a string or a number - a perfectly reasonable thing for a feature list to contain - EVERY review on this machine blocks until someone edits the probe. Attack that trade: is refusing the right default here, or should an unpoliced entry that is merely unusual be reported rather than fatal?

3. **The disabled-name match is case-sensitive.** `-ceq`, because PowerShell's `-eq` is case-INSENSITIVE and `Memories=False` had been satisfying `--disable memories`, which contradicted the limit round 2 declared. Measured directly before fixing. **Watched to fail:** the mixed-case case was red. Attack it: is case-sensitivity right, or does it now reject a name the real server could legitimately report differently?

4. **Both `ConvertTo-Json` calls carry `-Depth 100`.** The token function and the snapshot write, because the default is 2 and truncates silently - measured on 5.1. 100 is the maximum PowerShell accepts. The state-machine helper that seeds snapshots was given the same depth, since a fixture written at the default would have truncated the seeded value and made the scenarios measure the harness rather than the watcher. **Watched to fail:** two nested-value assertions red with nothing else moving. Attack it: is depth the whole exposure, or does an admitted value shape still round-trip wrong?

5. **Item 42 is corrected and narrowed at all three sites**, and the same-day measurement is recorded in the item rather than only in the debate record (`docs/superpowers/plans/2026-07-27-0150-backlog.md`; `.git/parallax/application-checkpoints/...`; `docs/superpowers/plans/rounds/2026-08-11-tool-surface-agy-drift/diff-debate-record.md`). The condition is stated as a resumed slice carrying a refreshed, non-identical preamble ahead of the brief, with a day boundary named as the one observed cause. Attack it: is any statement about item 42 anywhere still wider than one observation?

6. **THIS SIDE CAUGHT A VACUOUS ASSERTION IN ITS OWN FIXTURE, and narrowed your finding in the process.** Three assertions were written for claim 4 and only ONE went red. Rather than accept two passes, the truncation was measured: a Hashtable renders as `System.Collections.Hashtable`, but settings.json parses to a PSCustomObject, which renders as the string `@{deep=one}`.

   - One assertion checked for the Hashtable marker, so it PASSED against the defect. Vacuous, inside the fixture written to catch vacuous behaviour. Replaced with one measuring what the defect actually does: an object becomes a string. It is now red.
   - The nested-CHANGE scenario also passed pre-fix, for a real reason: the truncated rendering still CARRIES the differing text, so the comparison saw a difference and wrote its note anyway. **So the truncation corrupts the STORED value but did NOT blind change detection for this shape.** That is narrower than your finding as written and narrower than this session first accepted it. The scenario is kept and LABELLED a regression guard, with the measurement beside it.

   Attack the narrowing itself: is it correct, or is there a value shape where truncation DOES make a real change read as equal? If there is, the label is wrong and the scenario should be a live case.

</claims>

<boundaries>
Unchanged. Out of scope: `tools/check-drift.ps1:700` and `commands/doctor.md:70` (item 31), `evals/tools/drift_statemachine_tests.ps1:533` (item 41), the round-evidence binder (item 42), and backlog items 12, 15, 26-remainder, 29, 32, 33, 34, 35. The version bump is Task 9 and is deliberately LAST; the manifest still reading 0.23.0 is the ordering rule, not drift.
</boundaries>

<final-check>List any claim you could not verify against files you actually read, as UNVERIFIED. Do not fold unverified material into your verdict. Then answer the DRY question from the task block, explicitly.</final-check>
