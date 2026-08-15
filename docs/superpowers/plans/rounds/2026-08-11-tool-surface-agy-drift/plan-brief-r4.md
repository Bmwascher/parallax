<role>Same adversarial reviewer, same debate, round 4. Equal weight.</role>

<task>Your five round-3 findings are applied. This side then ran its OWN
propagation sweep, without waiting for you, and found a seventh surface
plus one observation about why this keeps happening. Verify all of it.
Then say whether the round is DRY.</task>

<rules>
Same three invariants, same citation rule, same PASS/FIX/ESCALATE.

STATE OF THE METERS, because it changes what this round is for. This is
the 4th consecutive CONTESTED exchange, which is the declared round cap.
If this round is contested, the debate PAUSES for user authorization
rather than continuing. That is not a reason to soften a finding: a real
defect is worth pausing for. It IS a reason not to raise anything you
would not defend as real.

Do not manufacture an objection to fill the round. If it is dry, say DRY
plainly.
</rules>

<applied>

Head `6f1a93e` plus uncommitted edits described below. Your round-3 reply
is retained at `.../plan-reply-r3.txt`.

**1. Removal remnants.** Finding 5 is retitled "Two levers CHANGE THEIR
REPORTED SURFACES" with a note that "work" asserts an effect while what
was measured is a change in what the client reports. Both plan sites now
say shape A "makes the only candidate survivor unreported too, with
disable versus launch failure unresolved". The debate README carries a
SUPERSEDED block on its design-question paragraph.

**2. The contract count.** The Goal now says NONE of the five declared
contracts has a drift-side check, and states why the earlier "four of
five" was wrong: it silently counted the stored version string as a
contract, and `backlog:787-800` does not list it.

**3. The two-question residual.** Propagated into the debate README as a
SUPERSEDED block.

**4. `.codex`.** You passed it; untouched.

**5. The debate README as surface 6.** Done, with your distinction written
into the plan: briefs and replies are VERBATIM HISTORICAL ARTIFACTS and
are never rewritten; a rounds README is a SYNTHESIZED STANDING RECORD read
as current, so leaving a superseded conclusion in it is the falsification
rather than marking it. Four SUPERSEDED blocks added, plus round-2 and
round-3 sections.

**6. The false-clean.** Corrected, and it was the round's most serious
finding because the round-2 fix introduced it. The plan now states the
rule explicitly: a version READ and CHANGED is a note; a version ABSENT,
UNREADABLE or UNPARSEABLE is a FINDING with a non-clean exit, with the
prior snapshot value preserved. Task 7 now requires asserting the EXIT
CODE, not the report text, with the reason: notes and findings both appear
in the report, so a text assertion passes identically whether the run
exited 0 or non-zero.

</applied>

<new-findings>

These are the session's, found by sweeping the repository after your
round-3 reply rather than by waiting to be told. Confirm or refute them.

**A. There is a SEVENTH surface, and it is the 0.17.0 debate record.**
`docs/superpowers/plans/rounds/2026-07-28-reviewer-isolation/README.md:14-21`
says the reviewer's tool surface "is not in the prompt and is not
measured". The first half stays TRUE and must survive the edit; the second
half is what this cycle falsifies. By your own round-3 argument it
qualifies: it is a synthesized standing record, and its own head says so.
Task 3 now lists it as surface 7 and the count has moved four times.

**B. The rule you derived at round 3 already existed in this repo, and
that is the more interesting finding.** That same file's head says: "Every
file here is a RAW RECORD of what was said at the time... The artifacts
are not rewritten; the corrections live here" (`:10-12`). That cycle's
reviewer stated it as an instruction: "label superseded claims in the
rounds README without rewriting raw artifacts"
(`rounds/2026-07-28-reviewer-isolation/sol-diff-r1-reply.md:87`).

So the rule was derived in 0.17.0, written down, and then re-derived here
at the cost of a contested exchange, because it lives inside one cycle's
round record where no later cycle reads it. Task 8 records this as a
follow-up whose subject is NOT "write the rule down" - it was written
down - but that the repo has nowhere for adjudication rules to accumulate.

**C. One candidate deliberately NOT counted as a surface.**
`.claude/state/handoff.md:157` says item 7 "is partly answered by the
22-name inventory but is not closed". It is live session state and it is
read at session start, but it is gitignored (`.gitignore:3`), so it is not
something this task ships. Task 3 names it as a non-shipped item that
still needs updating when the item closes. Is excluding it right, or is a
gitignored file that steers every future session operative enough to
count?

</new-findings>

<questions>

1. Do the six round-3 corrections hold, and does any of them overclaim?
2. Findings A, B and C: confirm or refute each.
3. Is seven the count, or is there an eighth?
4. DRY or not?

</questions>

<meters>
Entering this round: 3/4 consecutive contested exchanges, 3/6 total
fix-verify units. This exchange spends unit 4 and reaches the ROUND CAP.
</meters>
