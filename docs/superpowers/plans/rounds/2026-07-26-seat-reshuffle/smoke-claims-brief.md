# Panel smoke — shared round-1 claims (Sol+Fable, blind hub-and-spoke)

Subject: the report-format contract of `agents/flash-implementer.md` (the
`## Report format (your final message)` section and its supporting rules).
Subject revision (pinned in every round of every lane): checkout HEAD
c95f18e1ec2cb6a5d7de586557e072e638583e9f; reviewed file blob
69dbdb0f77d6606e5729ffe5414bc131aa4922e8
(`git rev-parse HEAD:agents/flash-implementer.md`).

<role>Adversarial reviewer, equal weight, in a multi-reviewer debate. Refute or confirm each numbered claim; cite agents/flash-implementer.md:<line> for every claim you make or contest; uncited claims are struck. Do not manufacture objections. End each claim PASS / FIX (with the specific fix) / ESCALATE, then ONE overall verdict line citing the subject revision.</role>

<claims>
1. The report contract's five fields — STATUS, ROUTE, FILES CHANGED,
   VERIFICATION, DEVIATIONS (agents/flash-implementer.md:111-120) — are
   each verifiable from wrapper-observable evidence alone (git status,
   retained logs, the brain transcript, the wrapper's own command runs);
   none requires trusting the inner Flash model's self-report, consistent
   with the route evidence being declared client-side at line 93.
2. The blocked path preserves recoverability: FILES CHANGED stays
   mandatory on `blocked` (lines 114-116, "STILL list every path Flash
   already touched") so the session can always revert a partial write —
   the contract's recovery property.
3. STATUS's third value `INPUT GAP: <exactly what is missing>` (line 111)
   is a distinct terminal state backed by the stop rule at line 29 ("STOP
   and report the gap") — the contract forbids improvised inputs rather
   than degrading them into a `done`.
4. DEVIATIONS is a drift tripwire, not a change log: the only passing
   value is the literal "none" (lines 119-120), and any other value
   converts the report into an explanation of why the task could not be
   built as written — there is no vocabulary for an accepted deviation
   inside this lane's report.
</claims>

<boundaries>The file's design (zero-judgment lane, Flash delegation, the containment rules outside the report-format section) is not under debate — only the four claims about the report contract as written at this revision.</boundaries>

<final-check>List any claim you could not verify against the lines you read as UNVERIFIED.</final-check>
