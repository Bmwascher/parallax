Panel round 8. FINAL head: `c66b2c8478e8cc1efa08d8eb7935d29c07735405`.
Fix range: `53a5652726ca7b887ac3065702f7e1808d7ee0f5..c66b2c8`.
Branch base unchanged: `e2e9242c6153d69e9a4f0c49055e7bf8c81a1dd0`.

`KIMI-REVIEW-BRIEF.md` in this workspace is your round-1 brief,
unchanged. `FIX7.diff` is the range above.

The user authorized one final pass. This is it. Nothing after this round
gets fixed and re-reviewed; whatever you say here is what the record
carries.

## FIRST: your round-7 brief did not reach you

You recorded it as truncated after "New head:", with no SHA, no task
list and no evidence block. Your reply followed the standing round-1
structure rather than that round's five tasks, and never answered the
round's sign-off question. I treated that as a TRANSPORT FAILURE, not as
a review result, and recorded it in the plan and the checkpoint.

Your route evidence was clean, so the route was sound and the prompt was
not. I could not explain it: that brief carried fewer shell-special
characters than the round-6 one, which arrived whole. **This round the
brief is a FILE in your workspace, which is the file you are reading
now.** If this text ends mid-sentence, say so as your first line and
stop.

Your round-7 finding was still valid and is applied.

## What was applied

**Your finding.** Two records still said every OTHER known container's
body is blanked, which stopped being true one commit earlier. Both
corrected: the probe's headline comment at the top of `Get-SkillReport`,
and the design's sentence. The design now also states that the list and
its order are the shape scanner's exactly, and why.

**From the other lane.** Its round-11 finding was the caller's
diagnosis. When the blanking pass itself failed, the message opened by
calling the SKILLS boundaries ambiguous, printed the valid skills
counts, said choosing the skills span was a guess, and only then
appended the real cause. For an unclosed `environment_context` that
contradicts itself inside one message. That lane called it the sole
reason it would not sign the head.

The reason is now built by `Get-AmbiguityReason`, which branches on
`AmbiguousCause`: with a cause it reports that the first-pass
measurement could not be made because the blanking pass did not finish
and names the cause, making no claim about skills boundaries and
printing no counts; without a cause it returns the counts message.
Extracting it into a function is what makes the wording testable at all,
since the branch sits behind `Test-PromptShape` and no run reaches it.

**Red-before-green is weaker on those two cases, and I am telling you
rather than letting you find it.** The wording they test lived in inline
caller text no test could reach. Against `53a5652` they fail because the
function does not exist, not because the message was wrong.

That lane also opened round 11 by withdrawing its own round-10 PASS:
your round-6 finding was valid and it had missed it.

## Your task this round

1. Verify both changes at the code.
2. Is `Get-AmbiguityReason` correct in both branches, and does the
   extraction change any reachable behaviour?
3. Is any record still describing a rule the code no longer follows?
   That is your finding class two rounds running.
4. **The sign-off question, which you have never been asked on a head
   that reached you.** Is this head one you would merge? If not, what
   remains?
5. Terminal verdict against head `c66b2c8`.

## Evidence (verify, do not trust)

- Both hosts: 449 passed / 1 skipped.
- Live probe both hosts: exit 0, clean, 29 -> 0, override sha256
  `180f09f50d282b5603f1c0d0621f2913ff66c8b7798e7a2f3b7fe8d41f432bb8`.
  Unchanged through all twelve rounds.

Say plainly if you find nothing.
