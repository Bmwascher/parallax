Round 2. Same subject, new revision.

SUBJECT REVISION IS NOW: branch 0.27.0-resume-not-guaranteed at 63a9b3a.
Round 1 verdicted revision bb386b0. Your round 1 FIX has been applied and
this round verdicts the amended revision.

THE FIX DIFF, and it is the only thing that changed since you last looked:
.superpowers/sdd/2026-08-19-resume-not-guaranteed/r1-fix-diff.txt

WHAT I DID WITH YOUR ROUND 1 FINDING.

ACCEPTED in full, both occurrences, and your sub-claim was sharper than the
Fable lane's. I verified independently that the 2026-07-26 probe used a
general-purpose subagent and never capability-tested containment at all, and
that its own Residual limits say so. So containment was capability-tested on
2.1.237 ONLY, on two of nine resumes. Your point stands at its full width:
the branch corrected an evidence overclaim for continuity and left the same
overclaim standing for containment.

The floor did not move. It is still 2.1.216, and the phrase
"Harness floor: Claude Code 2.1.216" still occurs exactly once in panels.md.

Two edits, tests moved first at both sites, and each new pin was proven to
go red on a one-word mutation and green on exact restore:

1. panels.md region panel-floor-scope. Was: "A version above the floor buys
   containment, never continuity." Now: "What the floor marks is the release
   that fixed the silent revert; containment was capability-tested on
   2.1.237 only, so above the floor it rests on that changelog mechanism
   rather than on a measurement covering every version."

2. model-prompting-notes.md. Was: "That holds AT OR ABOVE the 2.1.216 floor
   - below it, containment is precisely what failed silently." Now: "Every
   one of those capability tests ran on 2.1.237. Below the 2.1.216 floor
   containment is precisely what failed silently; above it no measurement
   covers every version, so the floor names the release that fixed the
   silent revert rather than a proven range."

YOUR OTHER ROUND 1 RULINGS, and what I did with each:
- Candidate (b), citation placement in panels.md: you ruled PASS, navigation
  nit. Accepted, not changed.
- The two enforcement-absent instances: you confirmed both and accepted them
  as item 67 follow-up scope rather than merge blockers. Accepted, unchanged.
- Claims 2, 4, 5, 6 and 7: PASS. Nothing changed in those areas.

YOUR TASK THIS ROUND, and it is narrow.

1. Verdict whether your round 1 FIX is now ADDRESSED at both sites, or not.
   State which.

2. Verdict the amended subject revision 63a9b3a as a whole.

3. Sweep the AMENDED text once more for the same class: a claim stated more
   widely than the evidence cited for it, or an operative rule whose
   enforcement is asserted but absent. This branch has now reproduced that
   class inside its own fix THREE times - the escalation seat, the
   untestable-resumes clause, and the containment width you just caught.
   Name any instance with file:line, or report that you found none.
   Reporting none is a useful and expected answer at this point; do not
   manufacture instances to fill the slot.

4. If the new wording introduced any fresh problem of its own, say so. In
   particular judge whether "rests on that changelog mechanism rather than
   on a measurement covering every version" is itself accurate, or whether
   it now understates what IS known.

State position changes explicitly: accepted, refuted with evidence, or
struck for want of a citation. Cite file:line for everything. End with a
verdict per open item and one verdict on the subject as a whole. Report
evidence and conclusions only.
