# Sol diff round 8, brief as sent

The exact text piped to the cross-vendor lane for round 8. Copied verbatim
from the dispatch brief file. Written to disk before it was sent.

This is the round that asked for a terminal answer.

---

<role>Same adversarial reviewer, same panel, round 8. This round asks for a terminal answer on the branch.</role>

<continuity-check>
Before anything else, state in one line: the branch name, the subject revision you reviewed in round 7, and the terminal verdict you gave it.
</continuity-check>

<subject>
Repository: parallax. Branch `item74-fable-5-1-notes`.
Round 7 subject revision: `08ba01b7f62b4bf10ec4859e0748656689d0a882`.
AMENDED subject revision, and the one you must verdict:
`fa866756f0e408d39ba853b144040afb403a3d3b` — one commit on top,
`fa86675 fix the hash method, state what the void round cost, complete the record`.
Your working directory is the review mirror rebuilt at that head. Run
`git diff 08ba01b..fa86675` yourself. The full range is `5d20eed..fa86675`.
</subject>

<rules>
Cite <path>:<line> for every claim, resolvable in your working directory.
Uncited claims are struck, yours included.
Do not manufacture objections: if a fix stands, say PASS and move on.
Verdict grammar: PASS, FIX (with the specific fix), or ESCALATE.
Your terminal verdict must cite the amended subject revision.
Report evidence and conclusions only.
</rules>

<what-changed>
Round 7 produced one FIX from each lane, five defects between them. Every
one was verified against the tree and applied. None was argued back.

P1. THE HASH METHOD WAS FALSE, your finding if you are the cross-vendor
    lane. Hashing the retained body as stored reproduces none of the five
    values. The method now states the trailing-newline removal exactly.
    The section also now says the table hashes the SOURCE artifact
    deliberately, because this repository normalizes line endings on
    checkout and a byte hash of a retained file is not stable across
    clones. All six values were re-checked against the documented method
    and reproduce.

P2. THE INCIDENT NOTE NEVER SAID WHAT THE VOID COST, the other lane's
    finding. It now does: while the void stood, the cross-vendor lane's
    last valid word on this branch was round 5's FIX on `b9c17bc`, two
    revisions back, and that lane's own round 5 findings had been applied
    in `233a340` without it ever confirming them. The branch was NOT
    attestable in that state. Re-dispatching that lane at round 7 against
    `08ba01b` is what resolved it.

P3. THE BINDING SENTENCE was false for the inventory: the briefs entered
    the directory DURING round 6 and were absent at round 6's own subject
    revision. The round table's binding and the inventory's binding are
    now separated and each says what it covers.

P4. A VERDICT WITH NO RETAINED REPLY. The same-harness lane's rounds 6 and
    7 are now retained, with their continuity answers, so every verdict in
    the table has either a retained reply or a stated absence.

P5. THE FALSE PREMISE TRAVELLED FURTHER THAN THE RECORD ADMITTED. The
    "ownership, not facts" error was not only in the README: the retained
    briefs show it was put to BOTH lanes in their round 4 briefs, so it
    shaped that round's adjudication. Now recorded.

Two claims of the session's own were unsupported and are corrected:

P6. "The rule is already written" implied prose in `skills/` that does not
    exist. Only the tool enforces it. Now cited to the tool.

P7. An earlier round 1 identity-gate incident was asserted with no
    evidence. Checked: it fired at PREPARE and cost nothing, which is
    materially different from the round 6 void. Kept, stated precisely,
    and marked as session recollection with no surviving artifact.
</what-changed>

<claims>
Q1. P1 to P7 each land. Check each against the tree rather than this list.
For P1 specifically, reproduce at least one hash by the documented method
and say whether it works.

Q2. THE RECORD IS COMPLETE AND TRUE ABOUT ITSELF. Its inventory matches the
directory, its table matches the retained replies, and its two stated
absences are the only absences. You have found a defect of this shape in
each of the last three rounds. Look again, and if there is none, say NONE.

Q3. THE RECORD IS HONEST ABOUT THE SESSION. Six of the last eight rounds
found defects in text the session wrote about its own conduct. Read the
whole record once more as an adversary and name anything that still
flatters the session, or say NONE.

Q4. Nothing outside the amendment's stated scope changed.

Q5. ATTESTATION. Both lanes have said the work is attestable and has been
since round 3. Say plainly whether you attest the branch at this revision.

If you attest, write the narrowed claim: what you certify, and NAME what
you exclude. At minimum the exclusions are the four pre-existing stale
cites in items 38, 58 and 66; the absent SDD ledger; the three baseline
behavioural failures; item 74's own OPEN status and present-tense Problem
text, which the plan's post-debate step closes; the loss of panel blindness
from round 5; and the void round 6. Add anything else you hold back.

If you do NOT attest, name the specific thing that stops you, and say
whether it is a defect in the work or in the record.
</claims>

<disclosures>
Gates at this head: all five green, 2720 passed and 14 skipped, unchanged
across every round of this debate.

The behavioural suite was NOT re-run. Every amendment since round 1 is
documentation prose. Round 1's measurement stands.

The SDD ledger is still absent.

The session touched nothing in the repository during round 7 and will touch
nothing during this one.

PROCESS NOTE, in answer to the same-harness lane's round 6 finding: both
lanes' briefs for this round were written to disk before being sent, so
both can be retained. The gap that made one lane's briefs unretainable is
closed from this round on, and the closing commit will retain them.
</disclosures>

<boundaries>
Not under debate:
- Anything you passed in earlier rounds that no amendment since has touched.
- The version bump. It happens AFTER this debate by repository rule.
- Whether items 38, 58 and 66 should be FIXED now. That is item 69's work.
- Whether item 74 should have been built at all.
</boundaries>

<final-check>
List anything you could not verify against files you read, as UNVERIFIED,
and keep it out of your verdicts. Q5 is the point of this round: the panel
has spent four rounds on the record and none on the code, and the question
is whether the record is now good enough to certify the work behind it.
</final-check>
