# Sol diff round 2, brief as sent

The exact text piped to the cross-vendor lane for round 2. Copied verbatim
from the dispatch brief file, whose canonical SHA-256 was recorded by the
round's prepare step and bound by the evidence reader before the reply was
read.

---

<role>Same adversarial reviewer, same panel, round 2. Your round 1 reply stands; this round judges only the amendment.</role>

<continuity-check>
Before anything else, state in one line: the branch name, the subject revision you reviewed in round 1, and the verdict you gave the branch. If you cannot recall them, say CONTINUITY LOST and stop.
</continuity-check>

<subject>
Repository: parallax. Branch `item74-fable-5-1-notes`.
Round 1 subject revision: `e0dbb8954dc24617c8ed16ba825dcf32d095082b`.
AMENDED subject revision: `ced2f535e6223fd69114db68b3feaa0690ac9f96`, one
commit on top, `ced2f53 correct the round-1 prose defects both lanes named`.
Your working directory is a NEW review mirror at the amended head. Run
`git diff e0dbb89..ced2f53` yourself. The full range is still
`5d20eed..ced2f53`.
</subject>

<task>
Decide whether the amendment fixes what you named, and whether it
introduces anything new. Then issue a terminal verdict on the amended
revision. Do not re-litigate what you already passed unless the amendment
touched it.
</task>

<rules>
Cite <path>:<line> for every claim, resolvable in your working directory.
Uncited claims are struck, yours included.
Do not manufacture objections: if a fix stands, say PASS and move on.
Verdict grammar: PASS, FIX (with the specific fix), or ESCALATE.
Your terminal verdict must cite the amended subject revision.
Report evidence and conclusions only.
</rules>

<what-changed>
Both lanes returned FIX on prose only, with no code defect between them,
and both contested the session's adjudication table. Every point either
lane raised was ACCEPTED. Nothing was argued back.

Fable section of `skills/multi-model-verify/references/model-prompting-notes.md`:
A1. The lead said two bullets are carried forward and marked; only one
    bullet is marked. It now says ONE bullet carries two claims.
A2. "Effort must be re-swept" implied a prior sweep while the same bullet
    said none ran. Now "Effort guidance must be re-evaluated".
A3. "this repo has never run a Fable effort sweep" is a history claim the
    tree cannot support. Now "no Fable effort sweep is recorded in this
    repo". The matching comment in the pin was changed with it.
A4. `xhigh` and `max` are names item 74 does not carry and nobody
    re-checked against the 5.1 guide. Now "the two highest effort levels".

Backlog `docs/superpowers/plans/2026-07-27-0150-backlog.md`:
A5. "with item 32's own entry gone they now rank first, second and third"
    was false; 49, 59 and 67 are at 3, 4 and 5. Rewritten as historical
    sequencing, and it now tells the reader to take the rank from the list.
A6. "renumbered only by the promotion" was stale. It now names both the
    promotion and the 2026-09-03 filings.
A7. "this group now opens on 69, and the numbering below it did not move"
    was stale. Now bounded to that promotion.
A8. Item 75's ranking entry asserted the Fable instruction channel
    categorically while its heading and body file it as an unverified
    candidate. The entry is now conditional and says CANDIDATE.
A9. `model-prompting-notes.md:572-582` was still a numeric cite and still
    stale; the text is at `:623`. It is now a section reference, matching
    the three converted in `5399655`.

One further change the session found itself, not raised by either lane:
A10. The status block claimed 27, 28, 34, 35 and 37 are open and carry NO
     ranking entry. All five are named in grouped ranking entry 29.
     Measured by script over the ranking section at this head: the only
     open items with no entry are 71, 72 and 73. The 2026-08-22 sweep that
     reported the five could not see a bullet that lists several items, so
     the defect was in the measurement. The block now says so, corrects
     itself, and does not repair the ranking to match. VERIFY THIS ONE
     RATHER THAN ACCEPTING IT: it is the session's own measurement, it
     rewrites a paragraph that pre-dates this branch, and a wrong
     correction here is worse than the error it replaces.
</what-changed>

<claims>
G1. A1 to A4 land, and the Fable section still states nothing as measured
that this branch does not establish. Two facts must stay UNVERIFIED: what
the `model: fable` alias resolves to, and what effort any seat receives.
Sweep the section again for any sentence that reads as a measurement.

G2. A5 to A9 land, and the backlog is internally consistent: items 74 to
77, the ranking, and the status block agree with each other and with the
file's own stated rules. Name any remaining contradiction.

G3. A10 is correct as stated. Check the claim about entry 29 against the
ranking text, and check that 71, 72 and 73 really are the only open items
with no entry. If the session's measurement is wrong, say so plainly.

G4. The four pins in `evals/multi-model-verify/test_multi_model_verify.py`
still lock what they claim after the wording changes, and no pin was
loosened to fit the new prose.

G5. Nothing outside the amendment's stated scope changed. The amendment
touches three files. Name anything in it that no lane asked for.
</claims>

<disclosures>
Gates re-run at the amended head: all five green, 2720 passed and 14
skipped, unchanged from round 1's count. `test_multi_model_verify.py`
re-run alone after its comment edit: 174 passed, 1 skipped.

The behavioural suite was NOT re-run for this amendment. The amendment is
documentation prose and one test comment; no behavioural surface changed.
Round 1's disclosure stands: three baseline failures, none introduced.

The SDD ledger is still absent, as disclosed in round 1.
</disclosures>

<boundaries>
Not under debate:
- Anything you passed in round 1 that the amendment did not touch.
- The version bump. It happens AFTER this debate by repository rule.
- Whether item 74 should have been built at all.
- The decision to file items 74 to 77 as four separate items.
</boundaries>

<final-check>
List anything you could not verify against files you read, as UNVERIFIED,
and keep it out of your verdicts. G3 is the claim most likely to be wrong,
because the session measured it itself and no other lane has checked it.
</final-check>
