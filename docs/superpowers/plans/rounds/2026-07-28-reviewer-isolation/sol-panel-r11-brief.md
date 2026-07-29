Panel round 11 (your round 19), and the user has authorized ONE more
round. New head: `53a5652726ca7b887ac3065702f7e1808d7ee0f5`.
Fix range: `881b676048208761f97f477ec86ce0585bf42ca2..53a5652`.
Branch base unchanged: `e2e9242c6153d69e9a4f0c49055e7bf8c81a1dd0`.

You returned PASS on `881b676`. The other lane returned FIX on the same
head, blind to you, and its finding was real. I reproduced it on both
hosts before applying anything.

## What it found, and what you did not

`Get-SkillReport`'s locator loop skipped `skills_instructions` when
blanking. A skill DESCRIPTION - free text, and `Hide-KnownContainer`'s
own comment says so - could therefore carry a solitary exact
`<environment_context>` literal that the LOOP counted as structure and
`Test-PromptShape` did not, because the scanner's quiet stage blanks the
skills body before it ever counts that family.

Reproduced on both hosts: the shape scan PASSED while `Get-SkillReport`
returned `Ambiguous` true with the SKILLS counts at one opener and one
close. A legitimate render refused, the wrong container named in the
message, and a cost the record did not admit.

This is the same one-function-away class as rounds 7 through 9. It
survived amendment 17 because that amendment rewrote the judge and the
read, and left the loop alone. Your round-18 answer said the three
responsibilities were now separated; the separation was right and the
loop had not been brought into line with it.

## What was applied

- The locator blanks the SAME list in the SAME order as
  `Test-PromptShape`, skills family included. Only bodies are blanked and
  the delimiters survive, so locating is unaffected. A second skills
  container nested in the body is still refused locally, because
  `Hide-KnownContainer`'s count rule runs before that body is blanked.
- A blanking failure's own message travels with the verdict as
  `AmbiguousCause`, and the caller appends it. The reason no longer
  reports the skills counts for a failure another container caused.
- Two new cases, both red against `881b676`.

**One test I got wrong, recorded rather than tidied.** The first draft of
`test_another_containers_failure_travels_with_the_verdict` asserted the
probe's exit reason end to end and PASSED - on the UPSTREAM message,
because `Test-PromptShape` refuses that text one line earlier with its
own wording that also names the container. It proved nothing about the
field it was written for. I ran the probe, read the reason, and rewrote
it to assert at the function.

## Your task this round

1. Verify both changes at the code.
2. **Attack the new blanking order.** The skills body is now blanked in
   the locator. Does that lose any detection the previous revision had,
   beyond what I claim survives through the count rule? Name the shape.
3. Is there any remaining disagreement between `Get-SkillReport` and
   `Test-PromptShape` about the same text? That question has now produced
   a finding in three consecutive rounds, so treat it as the main one.
4. This is the last round the user has authorized. If you would not sign
   this head, say exactly what stops you.
5. Terminal verdict against head `53a5652`.

## Evidence (verify, do not trust)

- Both hosts: 447 passed / 1 skipped.
- Live probe both hosts: exit 0, clean, 29 -> 0, override sha256
  `180f09f50d282b5603f1c0d0621f2913ff66c8b7798e7a2f3b7fe8d41f432bb8`.
  Unchanged through every round of this cycle.
- Both new cases were run against the reverted script first and both
  failed there.

Say plainly if you find nothing. Cite `path:line`. Anything you did not
check goes under `## Unverified`.
