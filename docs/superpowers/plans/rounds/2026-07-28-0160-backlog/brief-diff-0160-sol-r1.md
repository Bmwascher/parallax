<role>Adversarial reviewer, equal weight, in a two-model debate. Mode
`diff`, round 1.</role>

<task>Verify parallax 0.16.0 against the backlog items it claims to close,
and against its own stated invariants. Refute or confirm each numbered
claim.</task>

<rules>
You have a read-only sandbox and a shell in the repo at branch
`0.16.0-backlog`.

Cite `<repo-relative-path>:<line>` for every claim you make or contest. An
uncited claim is STRUCK, not debated. Anchor each file with its full
repo-relative path the first time you cite it.

Do not manufacture objections. If a claim stands, say PASS and move on.

End with a per-claim verdict and one overall verdict: PASS, FIX (with the
specific fix and its evidence), or ESCALATE.
</rules>

<situation>
Range `c6b7c85..7a89084`, six commits, unmerged. Diff package (93 KB):
C:\Users\Brandon\AppData\Local\Temp\claude\C--Users-Brandon-Documents-parallax\1f1d3d06-111e-4295-9e8d-afd424bcb21e\scratchpad\diff-0160-final.txt

**No frozen plan exists, deliberately.** These are four items worked
straight off a backlog, not a planned feature. The spec baseline is
`docs/superpowers/plans/2026-07-27-0150-backlog.md`: each closed item has a
Resolved block stating what was done, and each item states constraints the
fix had to satisfy. Hold the work to those, and say so if a Resolved block
claims more than the diff delivers. One such overstatement was already
found and corrected in this range, so the class is live.

The four items: 3, the attestation reject message; 5, a false rotation
claim in a contract document; 2, the unattended drift lane dying silently;
6, backup-lane route attribution breaking under concurrent sessions.

Gates at HEAD: 248 passed / 1 skipped; `skill_lint --strict` clean;
`skill_scanner` 0 findings; trigger evals clear; and the offline drift state
machine reports ALL SCENARIOS PASS with zero failed assertions. That last
one drives the real `tools/check-drift.ps1` against stub CLIs, and four of
its scenarios re-run the whole pytest suite inside a disposable worktree.
</situation>

<prior-review>
The required whole-branch review is retained verbatim at
`docs/superpowers/plans/rounds/2026-07-28-0160-backlog/fable-review-c6b7c85-efe4fa0.md`.
Read it. Verdict: ready to merge with fixes, no Critical, two Important,
three Minor. Every finding was ACCEPTED and applied in `7a89084`; nothing
was refuted or deferred. Test each adjudication rather than accepting it.

- **I1, a BLOCKED verdict recorded as a runner failure.** Accepted, and it
  corrected a claim the session had already put in writing. BLOCKED means
  the agent read every finding and stopped deliberately, so
  `commands/drift-triage.md` would have told a triage session to report the
  lane as down when it was working. BLOCKED now sets a separate
  `$autotriageBlocked` and gets its own toast.
- **I2, a label-less `-Release` silently freeing another debate's lock.**
  Accepted. The guard short-circuited on an empty `-Label`, making a bare
  release an undeclared `-Force`. Now refused against a labelled lock, and
  the `lane-lock` contract region requires the label on release.
- **m3** duplicate case reconnected to its discard disposition. **m4** a
  positive pin added on the rotation correction sentence, because two
  absence guards can only catch one phrasing of a falsehood. **m5**
  breaking an unreadable lock now announces itself.

The application checkpoint governing those edits is at
`.git/parallax/application-checkpoints/2026-07-28-0330-efe4fa0c07d2.md`.
</prior-review>

<claims>

Q1. **THE DRIFT LANE NOW DISTINGUISHES THREE STATES CORRECTLY:** the runner
broke, the agent blocked deliberately, and an ordinary findings week.
`$autotriageFailure` and `$autotriageBlocked` are set on disjoint paths, and
every path that reaches the manual toast sets exactly one or neither.
**Trace every branch. Find a path where both are set, or where the runner
fails and neither is set so the old ambiguous toast fires, or where a
successful run sets one.** The prior reviewer traced the two-state version;
this is the three-state version, which is where a new gap would be.

Q2. **THE LANE LOCK CANNOT BE MADE TO FREE A LANE ITS CALLER DOES NOT
HOLD**, except through the explicit `-Force`. Attack
`tools/kimi-lane-lock.ps1` directly: find an argument combination or lock
file state where a caller frees another label's lock without `-Force`, or
where the lane wedges permanently, or where two callers both believe they
hold it beyond the last-writer-wins race the file already documents.

Q3. **THE NEW ATTRIBUTION RULE IS FOLLOWABLE AND STRICTLY BETTER.** The
backup lane's evidence rule changed from counting the three lines across the
whole post-offset window to reading only this round's session block, because
the evidence lines carry no session id. The item's binding constraint was:
"Do not relax the 'exactly one' rule. The fix must make collisions rarer or
distinguishable, not tolerated." **Is that constraint actually met, or was
strictness traded for convenience?** The rule is PROSE executed by an agent,
so also judge whether a driver can follow it without inventing anything.

Q4. **EVERY CONTRACT REGION IN THIS RANGE IS LOCKED WHOLE, AND THE
INVENTORY MATCHES BOTH WAYS.** Five regions are new or renamed, and
`lane-lock` was edited AFTER creation, which moved its pin. Check
containment yourself rather than trusting the suite: for each region, one
pin string must contain the whole normalized body.

Q5. **NO RESOLVED BLOCK OVERSTATES ITS FIX, AND EVERY STATED RESIDUAL IS
HONEST.** The range contains three admitted residuals: collisions still
possible inside a sub-second startup block, the lock advisory rather than
mutually exclusive, and a crashed driver stalling the lane for up to 45
minutes. **Are those the real limits, or are there unstated ones? Is any
residual understated?**

</claims>

<boundaries>
Not under debate: the choice to work these items without a frozen plan; the
decision to ship item 4 in a later cycle; and the five fable findings
already accepted and applied.

IN scope: everything the code does, everything the documents now claim, and
whether the record describes both accurately.
</boundaries>

<final-check>List anything you could not verify against files you read, as
UNVERIFIED, and keep it out of your verdict.</final-check>
