<!-- Fable panel-reviewer lane, round 5, reviewed at HEAD 3140df9.
     Extracted verbatim from the lane's own transcript;
     evidence/fable-lane-six-rounds.jsonl was the source. -->

All claims verified at HEAD `3140df9`. My state across all four prior rounds is intact.

## 1. The five round-4 changes

1. **The oracle - CLOSES.** Plan:939-940 binds `orph` and `con` at the top; every assertion below uses a bound name, and I traced each one as reachable and failable. Plan:963 records it as the third oracle broken by its predecessor's fix. Your negative execution matches what the code predicts against an unreconciled spec - the orphan clause fires first at plan:946 - and is recorded as your evidence, not mine.
2. **Plan:68 - CLOSES.** The sentence now ends at the split and names round 21's catch of its own predecessor.
3. **Plan:79 - CLOSES.** The verbatim blast radius is the two SKILL.md call sites and region one's SKILL.md clause, with the three placeholder calls standing either way, and it explains why the old count said five.
4. **The record - CLOSES.** Plan:1011 (promise runs to round 21 and four Fable rounds, with both prior drift catches named), plan:1035 (rounds 20 and 21), plan:1037 (Fable third and fourth, correctly attributed).
5. **The pointer - CLOSES.** Plan:861 reads "is where it is exercised."

**Region one's new wording is accurate, not merely different.** Plan:202-225: "ONE PLACE" survives as one path in two spellings, which is true; the substitution claim is scoped exactly to where it was measured; "the placeholder is filled in by the session, which is weaker and is said rather than blurred" states the honest asymmetry; and "The path NAMES the plugin root" replaces "anchored" with the verb the split actually supports. Nothing in the region claims more than the measurement covers.

## 2. The sweep

I checked every occurrence of the token, the placeholder, and the word "anchor": plan:20, :30, :34-36, :68, :77, :79, :112, :116, :379, :394, :400, :488, :500, :574, :582, :622, region one, :992, :1037, :1041, :1047. The history and record passages narrate past states and are fine; every command and test literal carries the right form for its document.

**One site remains, and it is the same class both lanes have been purging.** Plan:77: "So: the documented calls keep `${CLAUDE_PLUGIN_ROOT}` verbatim" - written in revision 20, when all five calls carried the token. Three of the five documented calls now keep the placeholder, so the sentence claims one form inside Step 0 itself, one paragraph above the blast-radius sentence round 21 corrected and one bullet below the constraint that states the split. It is the sixth site of this shape; rounds 21 and my round 3 each fixed some and missed this one.

## 3. What this revision introduced

I compared every touched region against its predecessor: the two design bullets (plan:20, :30), region one (plan:202-225), the oracle and its expected-result text (plan:939-963), and the record entries (plan:1035, :1037). I found nothing new: no contradiction, no oracle regression, no stale count. The entry ordering (20/21 before 18/19) remains non-chronological; cosmetic, noted twice now, not a defect. The record's Fable count of four is true of the commit I reviewed; the round I am writing is the fifth, which only matters if a revision follows - and one must, per below.

## 4. Verdict

Last round I said the round-4 set was the last I saw absent new defects in the repairs. The repairs introduced nothing, but my own sweep - the one this round explicitly asked for - found one site the previous fixes missed, so I will not call it FREEZE with a known instance of this debate's most-repeated class left in the text.

**FIX**, on `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md` at `3140df9`. Smallest set, two edits with no interaction:

1. Plan:77: "the documented calls" becomes "the SKILL.md calls" (or equivalent), so Step 0 agrees with plan:36, :68 and :79.
2. The record's Fable-lane figures (plan:1011, :1037) absorb this fifth round when that edit lands, so round 21's drift finding does not recur in the same revision that cites it.

After those two, I have nothing further: the mechanism has survived five readings, the oracles all run and can fail, every form claim agrees with the measurement's scope, and the floor I stated in round 1 is recorded in the plan rather than papered over. The next revision, carrying exactly these two edits and nothing else, is freezable on sight.

FIX
