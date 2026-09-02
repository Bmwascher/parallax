<!-- Fable panel-reviewer lane, round 4, reviewed at HEAD 497f331.
     Extracted verbatim from the lane's own transcript;
     evidence/fable-lane-six-rounds.jsonl was the source. -->

All claims verified at HEAD `497f331`. My state from rounds 1 through 3 is intact.

## 1. The five round-3 changes

1. **Token split - CLOSES**, with a propagation defect listed in section 3. The split is in place everywhere I asked: plan:36 (constraint, correct reason, both citations), plan:571 and :579 (Task 4 test literals use `<plugin-checkout>/tools/dispatch-detached.ps1`), plan:619 (point of use, with the empty-path consequence), region one at plan:203-206, the closure at plan:987 (two resolved, three named, stated as weaker), and plan:981 (CLAUDE.md pointer now repo-relative, with the reason).
2. **Probe-record ownership - CLOSES.** Plan:790 (Task 7 writes nothing, with round 20 named), plan:821 (Task 8 step 2 re-runs the byte case and records it), plan:847 (the "ONLY cross-task write" sentence is now true), plan:808 (Modify).
3. **Task 1 Files list - CLOSES.** Plan:48.
4. **Native-executable clause - CLOSES.** Plan:784, with the in-process reason and the refusing-red consequence.
5. **Three clauses to four - CLOSES.** Plan:960, "all FOUR clauses verbatim", with round 20 credited.

On the `-join` correction: I agree with it, and it is better than my wording. "Discards nothing the redirect preserved" was true but framed as preservation; "canonicalizes, because no form preserves what the client emitted" is the accurate claim, and stating LF-no-trailing-newline as a contract is what makes Task 7's byte-equality oracle well-defined at all (plan:633 correctly makes the payload convention explicit).

## 2. The token split, judged as written

Two forms in two documents is right, and the hazards you name are both guarded by mechanism rather than prose. An implementer copying a launch line between the files hits the OTHER file's per-site pin: Task 3's tests assert the token form inside SKILL.md's marked sections (plan:391, :397), Task 4's assert the placeholder form inside backup-lane's (plan:571, :579), so a cross-copy fails by the destination site's name. A future reader assuming one form meets the split at the constraint (plan:36), the region (plan:203-206), the point of use (plan:619), and the closure (plan:987). The one residual worth keeping in view is already stated honestly: `<plugin-checkout>` is session-filled, so the three kimi calls retain an item-58-shaped residual - a wrong guess fails loudly, never as a false completion. The alternative single-form designs were each worse: the token everywhere rested on an unmeasured extension, the placeholder everywhere discarded the one substitution that IS measured.

## 3. What revision 21 introduced

- **The Task 9 python oracle can never run.** Plan:937 asserts `"counts five exact strings" in con`, and `con` is not assigned until plan:948. The heredoc raises `NameError` on every execution, including against a perfectly reconciled spec. Round 20's scoping fix moved the assertion's target to the constraints section but left it above the line that binds that section. This is the round-13 class - a check that could never pass - and the third instance of an oracle broken by the fix to the previous oracle; the record itself counts the first two at plan:1008. Fix: move the assertion below `con = section('## Constraints that must survive')`.
- **Plan:68 still ships revision 20's single-form claim.** Its last sentence reads "The token is therefore the form this plan ships, in every documented call and every test literal, with no conditional anywhere," which is now false three literals out of five and contradicts plan:36, :571, :579 and :619. Text left behind by a mechanism change, sitting in the same task as Step 0.
- **Plan:79 overstates the verbatim blast radius.** "Five documented literals and one contract region are wrong" was written when all five calls carried the token. Under the split, a `verbatim` re-take invalidates the SKILL.md literals and region one's SKILL.md clause; the three placeholder calls stand. The STOP instruction survives either way, but the stated scope of the damage is stale.
- **The record's promise has outrun its entries again.** Plan:1006 says the record runs to round 19 and the two Fable rounds; round 20's findings are meanwhile credited inline at plan:633, :790, :847 and :960, and this is the third Fable round. Round 19's entry exists because this exact drift was found once already.
- Cosmetic, no fix required to freeze: plan:858 says "Task 7 step 4 below" though Task 7 is above; plan:784 sits un-bulleted between two bullets.

## 4. Verdict

**FIX**, on `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md` at `497f331`. Smallest set:

1. Plan:936-948: reorder the heredoc so `con` is assigned before the exact-strings assertion uses it.
2. Plan:68: end the sentence at the measurement, or restate it as "the token is the SKILL.md form; backup-lane.md carries the placeholder per Global Constraints."
3. Plan:79: restate the verbatim blast radius as the two SKILL.md call sites and region one's clause.
4. Plan:1006 and the entries below it: add round 20 and the third Fable round, or stop the promise at what is recorded.

These are four localized edits with no interaction between them and no reach into the mechanism, which I have now failed to break across four readings. Absent new defects in the repairs themselves, this is the last set I see between the plan and freeze.

FIX
