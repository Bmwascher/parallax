Panel round 12 (your round 20). FINAL head:
`c66b2c8478e8cc1efa08d8eb7935d29c07735405`.
Fix range: `53a5652726ca7b887ac3065702f7e1808d7ee0f5..c66b2c8`.
Branch base unchanged: `e2e9242c6153d69e9a4f0c49055e7bf8c81a1dd0`.

The user authorized one final pass. This is it. Nothing after this round
gets fixed and re-reviewed; whatever you say here is what the record
carries.

## What was applied

**Your finding, the caller's diagnosis.** Applied as you specified, and
extracted so it can be tested at all. `Get-AmbiguityReason` branches on
`AmbiguousCause`: with a cause it says the first-pass measurement could
not be made because the blanking pass did not finish, then names the
cause, and it makes no claim about skills boundaries and prints no
counts. Without a cause it returns the counts message unchanged. Two
cases pin both branches, including the polarity where the counts ARE the
diagnosis.

**From the other lane.** Two records still said every OTHER known
container's body is blanked, which stopped being true one commit
earlier. Both corrected, and the design now also says the list and its
order are the shape scanner's exactly, and why.

**Red-before-green is weaker on these two cases, and I am telling you so
rather than letting you find it.** The wording they test lived in inline
caller text that no test could reach. Against `53a5652` they fail
because the function does not exist, not because the message was wrong.
The defect itself was verified by reading the old caller and by your
report.

## A transport failure you should know about

The other lane's round-7 brief did not reach it. Its reply records the
text as truncated after "New head:", follows the standing round-1
structure rather than that round's tasks, and never answers the sign-off
question. Its route evidence was clean, so the route was sound and the
prompt was not. I have not explained it: that brief carried FEWER
shell-special characters than the previous one, which arrived whole.
This round I am planting its brief as a file in the mirror instead.

That lane has therefore never answered the sign-off question on any
head. Weigh your own verdict accordingly.

## Your task this round

1. Verify both changes at the code.
2. Is `Get-AmbiguityReason` correct in both branches, and does the
   extraction change any reachable behaviour?
3. **The sign-off question.** You said the caller's diagnosis was the
   sole reason you would not sign `53a5652`. Is it cleared, and is there
   anything else on this head that stops you?
4. Twelve rounds, nineteen checkpoint amendments. Say plainly whether
   this head is one you would merge, and if not, what remains.
5. Terminal verdict against head `c66b2c8`.

## Evidence (verify, do not trust)

- Both hosts: 449 passed / 1 skipped.
- Live probe both hosts: exit 0, clean, 29 -> 0, override sha256
  `180f09f50d282b5603f1c0d0621f2913ff66c8b7798e7a2f3b7fe8d41f432bb8`.
  Unchanged through all twelve rounds.

Say plainly if you find nothing. Cite `path:line`. Anything you did not
check goes under `## Unverified`.
