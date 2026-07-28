Round 7, mode diff. Fix re-review, narrow. Evidence rules and verdict grammar as before.

POSITION CHANGES. Round 6 ACCEPTED in full, nothing contested. R6.2 was correct and I had written the weaker rule without noticing: counting successful parses meant "exactly once" was really "exactly one line I could read".

WHAT CHANGED, all of it:

- Labels and values are counted separately. `labels = re.findall(rf"(?m)^{re.escape(key)}:", block)` and `found = re.findall(rf"(?m)^{re.escape(key)}: (.+)$", block)`; a field reads as empty unless BOTH counts are exactly one. The keys are also `re.escape`d now.
- The duplicate test that used two valid values is replaced by three parametrized cases: a valid model line plus `model:`, plus `model: `, and plus `model:decoy`. I checked each fails against the OLD code, so none of them is a test that cannot fail.
- The merged-stream comment no longer explains safety through first-match-wins. It states that ordering is what lets the parser bind to the block, and that first-match protected a present field and did nothing for an omitted one.
- The record's exactly-once statements stay as written because the fix makes them true, and the round-6 boundary is named in the amendment rather than the claim being softened.

WHAT WAS APPLIED. Range `5260304..b9ff705`, one commit, 85 diff lines. Diff at C:\Users\Brandon\.claude\jobs\75fb2cba\tmp\diff-0160-r7.txt

280 passed, 1 skipped, from 277. Static gates clean. The parser was re-run against the REAL coloured output of your own round-6 dispatch: block located, route reads correctly. The behavioral case was NOT re-run for this amendment and the record says so — the change is field counting inside a block parse that the round-5 live run already exercised end to end.

Your R1 PASS is not re-opened.

CLAIMS FOR THIS ROUND. Narrow deliberately: this is a four-line change.

R1. LABEL COUNTING IS NOW CORRECT AND COMPLETE. Attack the counting itself: a key that is a prefix of another header key, a label at end-of-block with no trailing newline, leading whitespace before a label, a value containing the key string, CRLF line endings in the captured stream, and a block where the SAME field appears once validly and once with different capitalization.

R2. THE THREE NEW TESTS FAIL AGAINST THE OLD CODE. I verified this. Check my claim rather than taking it: read them and say whether each one would have passed before this commit.

R3. THE FIX INTRODUCED NOTHING. Four of six rounds carried a defect inside the previous fix, so the prior probability here is not low. Four lines changed plus a comment. Name the likeliest error before you look, then check it.

Nothing else is under debate. If it holds, say PASS plainly and say it first. Do not manufacture an objection to justify the round.
