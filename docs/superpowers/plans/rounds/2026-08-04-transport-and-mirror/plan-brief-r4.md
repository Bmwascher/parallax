<role>Adversarial reviewer, equal weight, in a two-model mode-diff debate. Round 4. Three rounds of fixes have each carried their own defects. Assume this round's do too.</role>

<task>Round 3 you returned PASS on claims 2 and 6 and FIX on claims 1, 3, 4 and 5. All were applied. The repo is at C:/Users/Brandon/Documents/parallax, read-only. The diff under review is aae5be896b97..e80a8138be40 (base..head). It carries THREE things: your round-3 findings, a defect the driver found in the field, and a change authored in a different session that is being folded into this release rather than given its own.</task>

<rules>
Cite file:line for every claim you make or contest; uncited claims will be struck. If a fix stands, say PASS and move on. End each numbered item with PASS, FIX (with the specific fix), or ESCALATE.

Three project invariants bind this branch:
- A claim may never be wider than its evidence.
- An unmade, failed, or unreadable measurement is never a clean one.
- A test is not evidence until it has been watched to FAIL for the reason it claims.
</rules>

<what-was-applied>

**H1.** The PRIOR STATE document now goes through the same object-root guard as a rollout line. You were right and the guard I had just written did not reach one file over.

**H2.** Strictness no longer delegates to `ConvertFrom-Json`. A record line must carry nothing but whitespace after its JSON value, found by a brace-depth scan that tracks string literals and escapes. Your claim was narrowed on measurement: PowerShell 7.6.3 accepts JSON COMMENTS specifically, and refuses arbitrary trailing text and a second object; 5.1 refuses all three. So the two hosts now refuse a commented line at DIFFERENT checks, and the oracle names both paths rather than pretending one.

**H3.** `new-review-mirror.ps1` post-construction comment narrowed to match its contract region.

**H4.** The oracle count in item 20's closure is now computed, not remembered. It reads 49.

**H5.** YOU WERE RIGHT AND I WAS WRONG. I recorded `bytes` as never-permissive from one tested input. Measured since: JSON `1108257.4` becomes Decimal on 5.1 and Double on 7, `[int]` truncates both, and paired with a prefix hash through the truncated offset it reached the ordinary slice checks. The closure and the amendment now record it as a hole. `prefixSha256` and `sessionId` remain diagnostic-only as recorded.

**H7.** An oracle where both rollout paths are real and the state's offset and hash describe the file actually passed, so only the unconditional comparison can refuse it.

**H8.** The first-line array oracle's docstring now states the measured per-host mechanism instead of asserting the hosts behave alike.

**Found in the field, not by review.** Round 3's own brief binding REFUSED this debate's round-3 dispatch: "a resumed slice must carry exactly one user record, found 2". The reply was discarded unread and only then investigated. The client had re-emitted its instructions preamble on a resume, byte-identical to the session's opening one. Mapped across this session: fresh carried preamble+brief, the first resume carried brief alone, the second resume carried both. The "exactly one" bound came from three measured rounds and the fourth broke it. It is now an IDENTITY rule: at most two user records, brief LAST, and a record in front of the brief must canonically equal the first user record in this session's own prefix. After the fix the same unchanged bytes bound clean and the reply was read.

**Folded in from another session.** `41ab307`: source directory reparse points are now FOLLOWED by the mirror's budget walk rather than refused, because `robocopy /E` without `/XJ` or `/SL` follows them, so refusing to measure across one described a smaller universe than the copy produces. Cycles and repeated link targets are refused; a repo root that is itself a reparse point stays refused.

</what-was-applied>

<claims>

1. The object-root and trailing-content guards are now complete and correctly placed. Try to find any remaining place in either tool where a parsed JSON value's shape is assumed rather than established, on EITHER host.

2. The trailing-content scan is correct. It runs only after a successful parse. Try to find a well-formed JSON object line it accepts with content after the value, or a legitimate line it rejects.

3. The resumed-slice identity rule is sound, and this is the claim I most want attacked. It permits ONE record in front of the brief if it canonically equals the session's first user record. Try to find a way to get text in front of the reviewer that satisfies it. Consider also whether re-binding the previously refused round on the corrected rule was legitimate, or whether it is a gate tuned until it passed.

4. The reparse change is correct and its contract region matches it. It was NOT reviewed by you before it landed. Check the traversal rule, the cycle and repeated-target refusals, and whether the region now over- or under-claims what the walk measures.

5. The record is honest about round 3. Specifically: that `bytes` was a hole I wrongly called diagnostic, and that the resumed-slice bound was falsified by the field rather than by review. Look for anything in the closures, the amendments or the checkpoint that reads better than what happened.

6. Scope: nothing in this diff is untraceable to a round-3 finding, the field finding, or the folded-in change.

</claims>

<boundaries>
Already decided and NOT under debate: the four backlog items and their dispositions; the release grouping; the 260-character policy threshold; reading the JSONL rollout rather than the human transcript; NOT building from an immutable filesystem snapshot in this release; and folding the other session's change into this release instead of giving it its own cycle.

Out of scope: backlog items 18, 19, 24, 25, 26 and 27. The `SKILL.md` token-budget warning is item 19.
</boundaries>

<final-check>List any claim you could not verify against files you actually read, as UNVERIFIED. If everything stands, say so plainly; a round that finds nothing is a real outcome and this branch has not had one yet.</final-check>
