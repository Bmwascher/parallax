# Sol diff round 3, brief as sent

The exact text piped to the cross-vendor lane for round 3. Copied verbatim
from the dispatch brief file, whose canonical SHA-256 was recorded by the
round's prepare step and bound by the evidence reader before the reply was
read.

---

<role>Same adversarial reviewer, same panel, round 3. Your round 1 and round 2 replies stand; this round judges only the second amendment.</role>

<continuity-check>
Before anything else, state in one line: the branch name, the subject revision you reviewed in round 2, and the terminal verdict you gave it. If you cannot recall them, say CONTINUITY LOST and stop.
</continuity-check>

<subject>
Repository: parallax. Branch `item74-fable-5-1-notes`.
Round 2 subject revision: `ced2f535e6223fd69114db68b3feaa0690ac9f96`.
AMENDED subject revision, and the one you must verdict:
`ee27f273df18278fa003c7b2d3852e72d6e0e7f8` — one commit on top,
`ee27f27 correct the round-2 defects both lanes named`.
Your working directory is the same review mirror, rebuilt at the amended
head. Run `git diff ced2f53..ee27f27` yourself. The full range is
`5d20eed..ee27f27`.
</subject>

<task>
Decide whether the amendment fixes what round 2 named, from EITHER lane,
and whether it introduces anything new. Then issue a terminal verdict on
the amended revision. Do not re-litigate what you already passed unless the
amendment touched it.
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
Both lanes returned FIX on the round-2 revision, prose only, no code defect
between them. Six findings in total across the two lanes. Every one was
checked against the tree before it was accepted, all six held, and none was
argued back. Findings B1 and B4 are the other lane's and are new to you;
B2, B3, B5 and B6 may be.

B1. The status block said 71, 72 and 73 were "never added to either list",
    while the Open list four lines above contains all three. It now says
    they were never added to the RANKING, and states plainly that they are
    in the Open list.
B2. `stop_reason: "refusal"` is a literal item 74 does not carry. This is
    the same class as the `xhigh` and `max` names removed in `ced2f53`, and
    the sweep that removed those did not reach this instance. The notes now
    say "can end a turn with a classifier refusal on benign code work".
B3. Item 74 still carried a NUMERIC cite into the notes, `:43-45`, for the
    reasoning_extraction bullet that now sits at `:79-81`. Fourth instance
    of the stale-cite class on this branch and the first outside item 75.
    Converted to a description of the bullet, matching the other three.
B4. Ranking entry 29 said item 33 "rides 32's" entry. Item 32's entry was
    removed when 32 closed, so 33 rode an entry that is not in the file.
    The parenthetical now says so.
B5. The 2026-08-22 sweep IS NOT IN THE TREE. `ced2f53` inferred from its
    result that it could not read a grouped bullet, and stated that as the
    cause. The paragraph now marks the explanation as inferred and keeps
    only the measurement: the five carry entries.
B6. Item 33's heading carries no close date, so "closed as of 2026-08-31"
    asserted a date the record does not hold. It now says DONE at its own
    heading.
</what-changed>

<disclosed-deviation>
The frozen plan's Step 3 drafts the refusal bullet WITH the `stop_reason`
literal. B2 removed it from the notes. The plan was NOT edited, because it
is frozen. So the shipped notes now differ from the plan's draft text by
that phrase, deliberately and in response to a review finding. Nothing pins
the literal. This is disclosed rather than left for you to find; judge
whether it is a spec-fidelity defect.
</disclosed-deviation>

<claims>
H1. B1 to B6 each land, and none of them introduced a new error. Check each
against the tree rather than against this list.

H2. THE CLASS, not the instances. Two defect classes have now each produced
a second instance AFTER the session believed it had swept them: stale
numeric cites into `model-prompting-notes.md`, and unsupported literals in
the Fable section that item 74 does not carry. For EACH class, sweep the
whole branch and report either every remaining instance or an explicit NONE.
Say what shapes you searched for, not just what you found.

H3. The backlog is internally consistent: items 74 to 77, the ranking, and
the status block agree with each other and with the file's own stated rules.
Name any remaining contradiction, including ones no lane has raised.

H4. The disclosed deviation above. PASS or FIX it explicitly.

H5. Nothing outside the amendment's stated scope changed. The amendment
touches two files.
</claims>

<disclosures>
Gates re-run at the amended head: all five green, 2720 passed and 14
skipped, unchanged across all three rounds.

The behavioural suite was NOT re-run. Both amendments are documentation
prose; no behavioural surface changed since round 1's measurement. Round 1's
disclosure stands: three failures, all baseline, none introduced.

The SDD ledger is still absent, as disclosed in rounds 1 and 2.
</disclosures>

<boundaries>
Not under debate:
- Anything you passed in rounds 1 or 2 that neither amendment touched.
- The version bump. It happens AFTER this debate by repository rule.
- Whether item 74 should have been built at all.
- The decision to file items 74 to 77 as four separate items.
</boundaries>

<final-check>
List anything you could not verify against files you read, as UNVERIFIED,
and keep it out of your verdicts. H2 is the claim that matters most: this
branch has now twice shipped a fix for the named instances of a class and
missed another instance of the same class.
</final-check>
