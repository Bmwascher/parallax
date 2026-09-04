# Sol diff round 4, brief as sent

The exact text piped to the cross-vendor lane for round 4. Copied verbatim
from the dispatch brief file, whose canonical SHA-256 was recorded by the
round's prepare step and bound by the evidence reader before the reply was
read.

---

<role>Same adversarial reviewer, same panel, round 4. Your rounds 1 to 3 stand; this round judges the third amendment and the resolution of a split you were half of.</role>

<continuity-check>
Before anything else, state in one line: the branch name, the subject revision you reviewed in round 3, and the terminal verdict you gave it. If you cannot recall them, say CONTINUITY LOST and stop.
</continuity-check>

<subject>
Repository: parallax. Branch `item74-fable-5-1-notes`.
Round 3 subject revision: `ee27f273df18278fa003c7b2d3852e72d6e0e7f8`.
AMENDED subject revision, and the one you must verdict:
`fad9b2b0a7a3d6a2324bc83c5c62b1096e17d28b` — one commit on top,
`fad9b2b fix the one stale cite this branch broke, record the four it did not`.
Your working directory is the same review mirror, rebuilt at the amended
head. Run `git diff ee27f27..fad9b2b` yourself. The full range is
`5d20eed..fad9b2b`.
</subject>

<task>
Judge the amendment and the reasoning behind it, then issue a terminal
verdict on the amended revision.
</task>

<rules>
Cite <path>:<line> for every claim, resolvable in your working directory.
Uncited claims are struck, yours included.
Do not manufacture objections: if a fix stands, say PASS and move on.
Verdict grammar: PASS, FIX (with the specific fix), or ESCALATE.
Your terminal verdict must cite the amended subject revision.
Report evidence and conclusions only.
</rules>

<the-split-and-how-it-was-settled>
THE PANEL SPLIT IN ROUND 3, AND YOU WERE ONE HALF OF IT. Both lanes ran the
class sweep and found the SAME five numeric cites into
`model-prompting-notes.md`, at backlog `:3480`, `:4994`, `:5291`, `:5308`
and `:5322`. The lanes disagreed only on OWNERSHIP:

- One lane returned FIX and named all five as merge blockers, on the
  ground that a branch which sweeps a class owns every instance it finds.
- The other returned PASS, holding all five to be pre-existing instances of
  item 69's class and outside this branch's scope. That lane also marked
  its own base arithmetic as UNVERIFIED rather than assert it.

The session did NOT pick a lane. It read
`git show 5d20eed:skills/multi-model-verify/references/model-prompting-notes.md`
and checked all five cites against the base file. The result contradicts
BOTH lanes in part:

C1. Item 38's `:288-291` is a probe-concurrency measurement at base.
    ALREADY STALE at base.
C2. Item 58's `:150` is a `<claims>` tag in a brief skeleton at base.
    ALREADY STALE at base.
C3. Item 66's `:350-355` is dispatch classification states at base.
    ALREADY STALE at base.
C4. Item 66's `:343-345` is dispatch classification states at base.
    ALREADY STALE at base.
C5. Item 66's `:46-52` IS the resume bullet at base. CORRECT AT BASE, and
    broken by this branch, which grew the Fable section by 45 lines and
    pushed that bullet to `:93`.

So the amendment fixes C5 alone, converting it to a description of the
bullet in the same form as the four cites converted earlier in this branch,
and records C1 to C4 under item 69 with the base evidence for each. Item 69
also now carries the split itself and how it was resolved.
</the-split-and-how-it-was-settled>

<claims>
J1. THE BASE MEASUREMENT IS CORRECT. Check C1 to C5 yourself against
`5d20eed`, not against this brief. This is the claim everything else rests
on, and it was made by the session rather than by either lane. If any of the
five is classified wrongly, say which and what the base file actually holds.

J2. C5's fix lands and resolves. The new text describes the resume bullet
rather than numbering it, and that description picks out exactly one bullet
in the notes at head.

J3. THE FOUR RECORDED UNDER ITEM 69 ARE RECORDED HONESTLY. The entry must
not overstate what was measured, must not present the four as fixed, and
must leave them findable. Check that item 69's new text agrees with the base
file and with the four sites as they still stand.

J4. THE OWNERSHIP RULE THE SESSION APPLIED. It is: a branch fixes the
instances it broke, and records the instances it merely found. Say whether
that rule is right for this repository, and whether it was applied
consistently to all five. If you hold that the branch owes more, say what
and why, with the base evidence.

J5. NO NEW INSTANCE. The amendment adds prose to two backlog items and
quotes several line numbers while doing it. Verify it did not introduce a
fresh stale cite of the very class it is about, and that the historical
cites it does carry are bound to a date or a commit.

J6. Nothing outside the amendment's stated scope changed. It touches one
file, the backlog.
</claims>

<disclosures>
Gates re-run at the amended head: all five green, 2720 passed and 14
skipped, unchanged across all four rounds.

The behavioural suite was NOT re-run. All three amendments are documentation
prose; no behavioural surface changed since round 1's measurement.

The SDD ledger is still absent, as disclosed in every round.
</disclosures>

<boundaries>
Not under debate:
- Anything you passed in rounds 1 to 3 that this amendment did not touch.
- The version bump. It happens AFTER this debate by repository rule.
- Whether item 74 should have been built at all.
- Whether items 38, 58 and 66 should be FIXED now. That is item 69's work
  and the user has not scoped it into this branch. Whether they are
  correctly RECORDED is J3 and is in scope.
</boundaries>

<final-check>
List anything you could not verify against files you read, as UNVERIFIED,
and keep it out of your verdicts. J1 is the claim that matters: it is a
session measurement that overrode both lanes, and no lane has checked it.
</final-check>
