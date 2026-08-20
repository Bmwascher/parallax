# Fable whole-branch review - range de85e8f..f96f2ed

Seat: `agents/fable-reviewer.md` (model pin fable, read-only grant).
Dispatched 2026-08-20 by the session driver (Opus 5) as the REQUIRED
whole-branch review that precedes a mode-diff debate, per SKILL.md.
Range-bound artifact: it verdicts `de85e8f..f96f2ed` and nothing else.

Inputs given: the contract-only diff package for that exact range
(`skills/`, `agents/`, `evals/`), the frozen plan, the spec, the SDD
ledger with all ten controller rulings, the probe record, and item 50.

## Verdict

**Ready to merge: WITH FIXES.** One fix required; everything else rides
to the debate as filed. No Critical findings. No Important findings.

## Findings

**Minor 1, the one required fix.** `model-prompting-notes.md:52-54` read
"the other arms ran on seats with full tool grants, where the test is not
possible". False for two of the seven untested resumes: arm A resumes 2
and 3 ran on the READ-ONLY panel seat, where the capability test was
possible and simply was not asked. The clause excused unmeasured resumes
as unmeasurable - overstating evidence completeness, which is this
branch's own class, inside this branch's own fix, in the file every
dispatch reads. Unpinned prose, so no pin migration cost.

**Minor 2, flagged not asserted.** `model-prompting-notes.md:54` states
containment present-tense across all versions above the floor, where the
sibling files say "held on every resume where it was measured" and
measurement covers 2.1.220 and 2.1.237 only. Reviewer judged it
defensible on the changelog-mechanism basis and passed it to the debate.

**Minor 3.** `panels.md:60-61` puts "re-confirmed 2026-08-19" next to the
2026-07-26 record path; the 2026-08-19 record is cited 30 lines later.
Reader-navigation nit only, the evidence exists.

## Disposition of the required fix

FIXED in commit `a5b495d`, and the corrected clause is now PINNED, which
the reviewer did not ask for. Rationale: the clause was completely
unpinned, so the correction could drift straight back; pinning it matches
the ruling already made for the parallel evidence claim in `panels.md`.
Tests changed first - the pin was seen RED before the text moved. The
session independently re-verified the pin fails on a one-word mutation
and passes on exact restore.

## The five judgments, as returned

1. **Spec fidelity: yes.** All six sites landed including the
   review-discovered site 4; both constraints on the continuity check
   hold; nothing unauthorized; the floor never moved.
2. **It closes item 50, does not restate it.** Three operative things the
   old contract lacked: a routing class that fires when the agent is not
   dead, a recording rule that stops a degraded panel reporting intact,
   and a check that can fail. One open deviation from item 50's letter -
   step 1 said reproduce on 2.1.233 and the probe ran on 2.1.237 - which
   the record states openly and the spec's invariance argument covers,
   because the load-bearing evidence predates the probe.
3. **All ten controller rulings judged SOUND, none wrong**, including the
   two singled out for challenge: not separating item 50's candidates 2
   and 3, and calling the behavioural case a harness flake. On the
   second: "A fixed-head, fixed-text regression cannot produce that run
   pattern."
4. **Deferring item 67 is correct, not a merge blocker.** The prose check
   is strictly stronger than the pre-branch state, where continuity was
   assumed and never checked at all; mechanizing it needs a fifth
   surface; and the backlog entry names the existing `continuity-lost`
   hook and states the open consequence plainly.
5. **No contradictions** among the four changed documents or against
   `SKILL.md`.

## Class sweep result

One clear instance (Minor 1, now fixed), one borderline (Minor 2, passed
to the debate), plus the enforcement-absent instance that is item 67 by
construction. No others found.

The reviewer also corrected an earlier review this session had relayed:
the prior repeat-defect sweep's verdict of "none" was **slightly generous
but materially right**. Recorded here because a review that overstates its
own cleanliness is the same class as everything else on this branch.

## UNVERIFIED by this reviewer

The test suites were not re-run by this seat; it verdicts the diff
package plus targeted file reads. Gate evidence comes from the session's
own runs, recorded in the SDD ledger, and from the whole-branch reviewer
that re-derived them independently.
