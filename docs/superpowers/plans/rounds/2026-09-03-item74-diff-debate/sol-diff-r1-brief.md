# Sol diff round 1, brief as sent

The exact text piped to the cross-vendor lane for round 1. Copied verbatim
from the dispatch brief file, whose canonical SHA-256 was recorded by the
round's prepare step and bound by the evidence reader before the reply was
read.

---

<role>Adversarial reviewer, equal weight, in a pre-merge mode-diff debate. You are one lane of a panel; the other lane reviews the same subject independently and never sees your reply. Findings may be relayed to you later, anonymized, by the driver.</role>

<task>Decide whether this branch may merge. Check SPEC FIDELITY (does the diff do what the frozen plan said, no more and no less) and CORRECTNESS. Verdict each numbered claim, then the branch as a whole.</task>

<rules>
Cite <path>:<line> for every claim you make or contest, resolvable in your working directory. Uncited claims are struck, yours included.
Do not manufacture objections: if a claim stands, say PASS and move on.
Verdict grammar, per claim and then for the branch: PASS, FIX (with the specific fix), or ESCALATE.
Your terminal verdict must cite the subject revision below.
Report evidence and conclusions only.
</rules>

<subject>
Repository: parallax. Branch `item74-fable-5-1-notes`.
Range under review: `5d20eed..e0dbb89`. Base `5d20eed` is main.
Head `e0dbb89`. Your working directory is a review mirror at that head; run
`git diff 5d20eed..e0dbb89` yourself rather than trusting any summary here.
Frozen plan: `docs/superpowers/plans/2026-09-03-item74-fable-51-notes.md`.
Spec: item 74 in `docs/superpowers/plans/2026-07-27-0150-backlog.md`. Note
that item 74 is ADDED by this range, so it is changed content and not a
fixed premise.
</subject>

<required-input>
The whole-branch review that must precede this debate is retained in the
tree at
`docs/superpowers/plans/rounds/2026-09-03-item74-diff-debate/whole-branch-review.md`,
SHA-256 DC86ACBBE42A5B1EB46BC55756E91DCE450EA97E2A14C94D2A1A1BFD8F89AAEC.
It reviewed `5d20eed..7fed651` and returned "Ready to merge: With fixes",
0 Critical, 2 Important, 6 Minor.

Session adjudication: ALL EIGHT findings ACCEPTED and FIXED in commit
`5399655`. Per finding:

1. Important, item 75's self-pointing line cites. ACCEPTED. Verified: item 4
   begins at `:983` while the cited `:530-564` sits inside item 75 itself.
   Fixed by converting three cites to SECTION references rather than
   renumbering them, so they cannot go stale again.
2. Important, ranking preamble contradicts itself. ACCEPTED, and it was
   worse than reported: the session's own splice had also mangled a sentence,
   attaching a parenthetical about item 33 to the clause about 71-73. Fixed
   the offset claim, the mangled sentence, and the stale "those five".
3. Minor, "the Fable 5 sweep does not carry" implies a sweep never run.
   ACCEPTED. Reworded to "Fable 5 effort guidance", tests first.
4. Minor, `"### Fable 5"` is accidentally green. ACCEPTED, and this was the
   sharpest finding: the pin added to prevent drift did not prevent it.
   Added an explicit `"### Fable 5.1" in notes` assertion.
5. Minor, two bullets retargeted to the 5.1 guide with no recorded check.
   ACCEPTED. They are now marked CARRIED FROM THE FABLE 5 GUIDE and
   explicitly not re-checked.
6. Minor, docstring presumes version 0.29.0. ACCEPTED. Version removed.
7. Minor, markdown structure. ACCEPTED, and wider than reported: six entries
   had wrong continuation indents, two caused by the session's renumber
   script assuming an indent width. All six normalized; blank line restored.
8. Minor, no step closes item 74 at merge. ACCEPTED. Added as step 4 of the
   plan's "After the tasks".

Contest any of these adjudications if the fix does not do what this table
says it does.
</required-input>

<claims>

F1. SPEC FIDELITY. The diff implements the frozen plan's three tasks and
nothing beyond them, except the review fixes listed above and this
artifact's own commit. Check each task against the plan and name anything
built that the plan did not ask for, or asked for and is missing.

F2. The dispatch fix is correct and minimal. `tools/dispatch-round.ps1`
prepends the PowerShell call operator to the printed command, and
`evals/multi-model-verify/test_dispatch_round.py` pins it. Verify no other
field of the `-Prepare -Json` object changed, and that the file still
contains no non-ASCII byte, which its own header requires.

F3. The wording changes match what the tool does. The `-DispatchHost`
sentence and the five replaced dispatch clauses describe the tool's actual
behaviour at this head. Verify against the tool rather than against the
plan.

F4. The rewritten Fable section states nothing as measured that this branch
does not establish. Two facts must stay UNVERIFIED: what the `model: fable`
alias resolves to, and what effort any seat receives. Sweep the section for
any other sentence that reads as a measurement.

F5. The four new pins actually lock what they claim, including the new
`### Fable 5.1` assertion. Check that reverting the section to Fable 5 would
now FAIL rather than pass.

F6. The backlog record is internally consistent after the fixes: items 74 to
77, the ranking, and the status block agree with each other and with the
file's own stated rules. This is most of the diff by volume and the previous
review found two self-contradictions here, so weight it accordingly.

F7. The token budget holds. `SKILL.md` is under its hard ceiling of 6500.
Verify the current number rather than accepting one.

</claims>

<disclosures>
Two things the session is required to put in front of you rather than let
you discover.

D-A. THIS BRANCH HAS NO SDD LEDGER. The plan's header requires
`superpowers:subagent-driven-development`, which in this repo writes a
`.superpowers/sdd/<date>-<name>/` ledger. None exists. The tasks were
executed by fresh implementer subagents with session verification between
each, but nothing wrote the ledger and nothing enforced it. The whole-branch
review named this as item 59's class and told the session to disclose it.
It is disclosed. Judge whether it blocks merge.

D-B. THE BEHAVIOURAL SUITE HAS THREE FAILURES, AND THEY ARE BASELINE, NOT
INTRODUCED. Run against the installed 0.28.1 cache, which does not contain
this branch: plan-mode-debate-runs 0/4, diff-mode-spec-fidelity 3/4,
no-manufactured-objections 1/3. Run against this checkout with `--head`: the
same three fail, none worse, and plan-mode-debate-runs improves to 2/4 with
its first expectation now met, namely that a wrapper actually invokes
`codex exec`. That improvement is attributed to F2's fix. The session's first
run omitted `--head` and therefore measured the cache rather than the
branch; it was re-run. Both runs leaked a temp directory with a WARNING.

Gates at head: all five green, 2720 passed and 14 skipped, up one test from
the branch's starting 2719. `test_dispatch_round.py` is 61 passed under both
PowerShell hosts.
</disclosures>

<boundaries>
Not under debate:
- The decision to file items 74 to 77 as four separate items. That was the
  user's call after an earlier panel.
- The version bump. It happens AFTER this debate by repository rule, so its
  absence from this diff is correct, not an omission.
- Whether item 74 should have been built at all.
</boundaries>

<final-check>
List anything you could not verify against files you read, as UNVERIFIED,
and keep it out of your verdicts. F6 is the claim the previous review found
most defective; F5 is the one where a pin already failed to lock what it
claimed once.
</final-check>
