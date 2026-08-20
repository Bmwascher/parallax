You are the cross-vendor reviewer lane in a two-model debate. Equal weight:
neither side's claim outranks the other's, only evidence does. Cite
file:line for every claim you make or contest; uncited claims are struck,
including mine. List anything you cannot verify against files you read as
UNVERIFIED and never fold it into a verdict.

REPO: C:/Users/Brandon/Documents/parallax
SUBJECT REVISION: branch 0.27.0-resume-not-guaranteed, range de85e8f..bb386b0.
MODE: diff. You are verifying a committed range against a frozen plan.

READ THESE FIRST:
- Contract-only diff for the exact range:
  .superpowers/sdd/2026-08-19-resume-not-guaranteed/debate-diff-contract.txt
- Frozen plan: docs/superpowers/plans/2026-08-19-resume-not-guaranteed.md
- Spec, the binding authority:
  docs/superpowers/specs/2026-08-19-resume-not-guaranteed-design.md
- The probe the branch rests on:
  docs/superpowers/plans/rounds/2026-08-19-item50-resume-probe/probe-record.md
- The REQUIRED whole-branch Fable review of this same range, already run:
  docs/superpowers/plans/rounds/2026-08-19-resume-not-guaranteed/fable-review-de85e8f-f96f2ed.md
- The backlog item this answers: docs/superpowers/plans/2026-07-27-0150-backlog.md, item 50.

BACKGROUND, all of it checkable in the files above.

Two locked contract regions promised that at or above Claude Code 2.1.216
a resumed background agent keeps its conversation state, its model pin and
its read-only tool grant. Three "No transcript found" failures were
MEASURED on 2.1.233, which is above that floor. A probe on 2.1.237 did not
reproduce them in nine resumes across five conditions, and the probe record
states its own low power and forbids citing its clean result as evidence
of reliability.

The branch keeps the floor at 2.1.216, scopes it to the silent-revert bug
it genuinely fixed, retires the reliability guarantee, names a failed
resume as a routed failure mode, adds a per-round continuity check, and
requires a consented fresh re-dispatch to be recorded as one.

NOT UNDER DEBATE, already decided by the user:
- The floor stays at 2.1.216. Raising it is refuted by measurement.
- Execution is subagent-driven; tests change before the text they lock.
- Items 67 and 68 are filed as follow-ups, not built in this cycle.

MY NUMBERED CLAIMS. Verdict each PASS, FIX with specifics, or ESCALATE.

CLAIM 1. The diff implements the spec and implements nothing the spec does
not authorize. Six sites: the panel seat agent file, panels.md, fallbacks.md,
model-prompting-notes.md, the re-dispatch recording rule, and the per-round
continuity check.

CLAIM 2. It closes item 50 rather than restating it. Three operative things
the old contract lacked now exist: a routing class that fires when the agent
is not dead, a recording rule that stops a degraded panel reporting as
intact, and a continuity check that can fail.

CLAIM 3. Every new claim in the changed text is narrower than or equal to
its evidence. In particular the containment claim is scoped to the two of
nine resumes where it was capability-tested, and says plainly that five of
the rest ran on full-grant seats where the test is impossible and two ran on
the read-only seat and were simply not asked.

CLAIM 4. All six new contract regions sit whole inside a single pin each, in
a permitted assertion form, and all six are declared in DECLARED_REGIONS.
A pin is a string literal in exactly one of: "literal" in body;
body.count("literal") compared in positive bounds; or an and of those. Under
not, in a not in, either side of an or, in a failure message, or reached
through a variable, a literal pins NOTHING.

CLAIM 5. The evidence grounding the change is itself pinned, so it cannot be
deleted while the suite stays green. This applies both to the measurement
paragraph in panels.md and to the containment clause in
model-prompting-notes.md.

CLAIM 6. Deferring the mechanization of the continuity check to backlog item
67 is correct rather than a merge blocker. The prose check is strictly
stronger than the pre-branch state, where continuity was assumed and never
checked at all, and mechanizing it requires frozen-plan-format.md, a fifth
contract surface this cycle deliberately kept closed.

CLAIM 7. No changed document contradicts another, or contradicts SKILL.md,
which this branch does not touch.

THE QUESTION THAT MATTERS MOST.

This branch has twice reproduced a defect inside the fix for that same
defect. Once, a corrected sentence excluded the whole-branch reviewer from a
resume claim on a zero-grep criterion while leaving the escalation seat in,
which fails the same criterion. Again, a clause excused seven untested
resumes as untestable when two of them were testable and simply not asked.
Both were caught by review and fixed.

Sweep the FINAL state of the changed contract text for that class: a claim
stated more widely than the evidence cited for it, or an operative rule
whose enforcement is asserted but absent. Name each instance with file:line,
or report that you found none. Reporting none is a useful answer. Do not
manufacture instances.

Two candidates are already on the record and you should rule on both rather
than rediscover them:
(a) model-prompting-notes.md says containment holds AT OR ABOVE the 2.1.216
    floor, present tense across every version above it, while measurement
    covers only 2.1.220 and 2.1.237. The Fable reviewer flagged this and
    declined to assert it as a defect.
(b) panels.md places "re-confirmed 2026-08-19" next to the 2026-07-26 record
    path, with the 2026-08-19 record cited about thirty lines later.

End with a verdict per claim and one verdict on the subject as a whole.
Report evidence and conclusions only, never your internal deliberation.
