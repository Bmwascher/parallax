<!-- Fable panel-reviewer lane, round 6, reviewed at HEAD 847e4f3.
     Extracted verbatim from the lane's own transcript;
     evidence/fable-lane-six-rounds.jsonl was the source. -->

All claims verified at HEAD `847e4f3`. My state across all five prior rounds is intact, which matters this round, because the question is partly about what each lane actually said.

## 1. The three changes

1. **Plan:77, the sixth site - CLOSES on substance, and the edit broke the sentence it fixed.** The claim is now correct: two SKILL.md calls keep the token, only those two, three carry the placeholder, revision-20 history recorded. But the inserted history note was spliced into the middle of the old sentence, leaving its second half orphaned: "...one bullet below the constraint that states the split. and Task 1's outer-command test substitutes the installed plugin path itself..." A lowercase "and" opens a fragment with no main clause. Meaning survives; grammar does not. This is the same shape as every recent introduction: a rewrite leaving a piece of the prior text behind.
2. **The record's Fable figures - CLOSES.** Plan:1011 (five rounds), plan:1041 (third, fourth and fifth, with the fifth's sweep described accurately).
3. **The rewritten round 21 and 22 entries - one attribution defect, otherwise accurate.** The capacity-failure record at plan:1035 is right and rightly explained: the binder binds the brief this side sent to what the client recorded, so CLEAN on a round with no reply is correct behavior, and the missing reply plus exit code are what caught it - that matches the binder contract, and the event itself is outside the repo, recorded as such, like round 7's. Plan:1039 is accurate, including the dual credit on the sixth site. **The defect is at plan:1037**: "And one pointer named a task below it that sits above it" is listed as one of the three things "Round 21 itself found." Per your own relayed accounting, that pointer came from my round 4's cosmetic list - you applied it as item 5 of my set in the revision-22 dispatch - and your relay of Sol's round 21 named the NameError plus three single-form sites, no pointer. This entry marks dual finds explicitly everywhere else ("BOTH LANES found independently", "both lanes named that one independently too"), so as written the clause reads as Sol-only. Either credit it to the Fable lane's fourth round or mark it dual if your round log shows Sol found it too; I hold only your relays and my own rounds, so your log is the arbiter.

## 2. Does "freezable on sight" hold?

No, and precisely for the reason I attached to it: I said the next revision carrying exactly my two edits and nothing else was freezable on sight. It carried a third edit and a rewrite, and the rewrite introduced the splice at plan:77 and the attribution clause at plan:1037. The condition failed, so the judgement does not transfer to this text.

## 3. The find-rate question, answered directly

**The remaining find rate is repair churn, not residual plan defect.** The evidence is in the classes and the trend. No completion-model hole in thirteen Sol rounds and six of mine. Since my round 2, every finding either lane has produced falls into three classes: text left behind by an edit, an oracle broken by the fix to the previous oracle, and record bookkeeping. The severity is monotonically falling: dead oracle, then a contradicting sentence, then a sentence fragment and a history clause. And for two rounds running both lanes have converged on the same single finding, which means two independent samplers are drawing from a pool with roughly one item in it - and that item is always the newest edit.

What I would expect a next full round to find, if you ran one: exactly one word-level defect inside whatever edit fixes this round's two items, and nothing in the mechanism, the states, the exit mapping, the pins, or the task oracles. This round is itself the demonstration: everything I found lives in text written since the last round. The review has reached the point where it only finds itself. The residual risk in this plan now lives in implementation - and implementation is governed by the task-local oracles the debate spent seventeen rounds sharpening, not by another prose pass.

So: fix the two word-level items below, verify the diff is exactly those strings, and freeze. Do not run another full round; a confirming read of a three-line diff is enough, by either lane or by you.

## 4. Verdict

**FIX**, on `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md` at `847e4f3`. Smallest set, specified to the word so the edit has no degrees of freedom:

1. Plan:77: replace ". and Task 1's outer-command test substitutes" with ". Task 1's outer-command test substitutes" - one deleted word, one capital.
2. Plan:1037: either "And one pointer named a task below it that sits above it - the Fable lane's fourth-round catch" or, if your round log shows Sol 21 found it independently, append "which both lanes noted." Extend, do not rewrite.
3. With those landing, plan:1011 and plan:1041 absorb this sixth Fable round in one appended clause each - extension, not rewrite, because rewrites are where this debate's last four defects came from.

UNVERIFIED and not folded in: the capacity-failure event and its binder verdict (session artifacts, outside this repository, recorded with that limitation at plan:1035); the contents of Sol's rounds beyond your relays.

FIX
