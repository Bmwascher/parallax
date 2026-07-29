Panel round 7, and the user has authorized ONE more round. New head:
`53a5652726ca7b887ac3065702f7e1808d7ee0f5`.
Fix range: `881b676048208761f97f477ec86ce0585bf42ca2..53a5652`.
Branch base unchanged: `e2e9242c6153d69e9a4f0c49055e7bf8c81a1dd0`.

Your workspace is a FRESH review mirror at the new head.
`KIMI-REVIEW-BRIEF.md` is your round-1 brief, unchanged, and `FIX6.diff`
is the range above.

## Your round-6 finding was right, and it reproduced

You traced it at the code and said so. I ran it on both hosts before
applying anything: the shape scan PASSED while `Get-SkillReport`
returned `Ambiguous` true with the SKILLS counts at one opener and one
close. A legitimate render refused, the wrong container named. The other
lane returned PASS on the same head and did not find it.

Both applied, and your minimal fix is the one I took.

- The locator blanks the SAME list in the SAME order as
  `Test-PromptShape`, skills family included. Only bodies are blanked
  and the delimiters survive, so locating is unaffected. A second skills
  container nested in the body is still refused locally, because
  `Hide-KnownContainer`'s count rule runs before that body is blanked -
  which is what you said would happen.
- A blanking failure's own message travels with the verdict as
  `AmbiguousCause`, and the caller appends it.
- Two new cases, both red against `881b676`.

**One test I got wrong, recorded rather than tidied.** The first draft of
the cause test asserted the probe's exit reason end to end and PASSED -
on the UPSTREAM message, because `Test-PromptShape` refuses that text one
line earlier with wording that also names the container. It proved
nothing about the field it was written for. I ran the probe, read the
reason, and rewrote it to assert at the function.

## The other lane's round 10, for your information

It attacked the offset invariant with CRLF, sequential containers and
non-BMP characters and found no drift between the located offsets and
the raw render. It also answered a design question: the recurring
defects came from one function holding three responsibilities -
locating, reading, and proving suppression - and those are now separate.
Your finding showed the loop had not been brought into line with that
separation.

## Your task this round

1. Verify both changes at the code.
2. **Attack the new blanking order.** The skills body is now blanked in
   the locator. Does that lose any detection the previous revision had,
   beyond what survives through the count rule? Name the shape.
3. Is there any remaining disagreement between `Get-SkillReport` and
   `Test-PromptShape` about the same text? That question has produced a
   finding in three consecutive rounds, so treat it as the main one.
4. This is the last round the user has authorized. If you would not sign
   this head, say exactly what stops you.
5. Terminal verdict against head `53a5652`.

## Evidence (verify, do not trust)

- Both hosts: 447 passed / 1 skipped.
- Live probe both hosts: exit 0, clean, 29 -> 0, override sha256
  `180f09f50d282b5603f1c0d0621f2913ff66c8b7798e7a2f3b7fe8d41f432bb8`.
- Both new cases were run against the reverted script first and both
  failed there.

Say plainly if you find nothing.
