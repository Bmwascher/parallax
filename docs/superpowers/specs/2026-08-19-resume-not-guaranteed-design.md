# Design: subagent resume is not guaranteed by a version floor

Date: 2026-08-19. Backlog item 50. Branch `0.27.0-resume-not-guaranteed`.

Reviewed before build by the Fable lane (round 1, verdict FIX-then-sound);
its three required fixes are folded in and marked below.

## The problem

Two locked contract regions promise a harness floor of Claude Code
2.1.216, and the text around them says that at or above it a resumed
background agent keeps its conversation state, its model pin and its
read-only tool grant. Item 50 records a relayed report that the Fable
panel lane would not resume on 2.1.233, above that floor, failing with
`No transcript found`, so every round ran as a fresh dispatch while the
panel still reported as a panel.

## What the evidence supports

**The probe did not reproduce the failure.** Five arms on 2.1.237,
crossing seat against idle, resume depth and a live background child:
nine resumes, nine passes, zero failures. Record at
`docs/superpowers/plans/rounds/2026-08-19-item50-resume-probe/probe-record.md`.

**The probe is not the load-bearing evidence and cannot be.** Nine passes
cannot establish a guarantee about a fault that
`.superpowers/sdd/2026-08-15-resume-preamble-refresh/progress.md:117-122`
records as intermittent on a single agent id - it resumed cleanly twice
and then failed. The probe has low power and its own record says so.

**The load-bearing evidence is three failures MEASURED on 2.1.233**
(`progress.md:70`, `:114-120`, `:347`), which is above the floor. A
version floor is therefore not a sufficient condition for reliable
resume.

**What the probe DID establish**, by capability test rather than
self-report: the panel seat's read-only grant survives resume (it could
not invoke Bash and enumerated exactly its three granted tools), state
persistence is real rather than re-priming (both multi-round arms
answered questions about rounds other than the one that planted the
nonce), and the resume surface still carries no model parameter.

## Decisions settled before build

**The floor STAYS at 2.1.216 and is not raised.** It is scoped to the
silent-revert bug it actually fixed, which has a named changelog
mechanism (`panels.md:81-84`) and which this probe supports: containment
held on every resume tested. Raising it to 2.1.233 or 2.1.237 is refuted
by measurement, because the failures happened above it. Item 50 names
this move and forbids it in its own words.

*(Fable fix 1, accepted.)* The drift capture at
`tools/drift-reports/2026-08-18_131711.txt:6-41` covers 2.1.227 to
2.1.234 only. It argues against a 2.1.233 floor and says NOTHING about
2.1.235 to 2.1.237. It is cited here at that width only. The sufficient
argument against any raise is the measured-failures-above-floor fact plus
the power limit above.

**Item 50's candidates 2 and 3 are not separated, and need not be.**
Candidate 2 is "something else in 2.1.233 broke resume"; candidate 3 is
"resume was never reliable and the 2026-07-26 probe measured a narrower
case". Under candidate 2, re-asserting a guarantee at a new number would
need a named mechanism (none exists in any captured changelog) plus a
probe with power a clean run cannot have. Under candidate 3 the guarantee
was never earned. **Both branches forbid re-asserting the guarantee and
both require the same disposition fix**, so the contract changes
identically either way.

**The defect is disposition, not detection.** `No transcript found` is
loud: the resume call returns it and the driver sees it. But
`panels.md:63-64` names the lane's failure mode as "agent death, which is
loud", and `fallbacks.md:212-213` maps only "a dead Fable panel subagent"
to `panel-lane-loss`. A resume that cannot reach a transcript leaves the
agent not dead, so nothing routes it and the consent gate at
`fallbacks.md:215` is never reached.

**There is a proven shape to mirror.** The Kimi lane already carries this
class at `fallbacks.md:198-199`: "resume failure: one same-parameters
retry, then the consent gate with the fresh-per-round option (full brief
re-sent each round)." The Fable lane simply lacks the analogue. This is a
missing mapping, not a new concept.

## The change set

### Site 1 - `agents/fable-panel-reviewer.md:18-19`

States without qualification that "your conversation state persists
across the resume (probed 2026-07-26)". Becomes best-effort: it usually
persists, it can fail, and the failure has a named disposition. The
no-model-parameter half is unchanged and still true.

### Site 2 - `skills/multi-model-verify/references/panels.md:62-64`

"the failure mode is agent death, which is loud" gains a second named
failure mode: a resume that cannot reach the agent's transcript. Both
route to `panel-lane-loss`.

### Site 3 - `skills/multi-model-verify/references/fallbacks.md:212-213`

"a dead Fable panel subagent is directly this class" widens so a resume
that cannot reach the agent's transcript maps to `panel-lane-loss` too,
with the Kimi shape: one same-parameters retry, then the consent gate.

### Site 4 - `skills/multi-model-verify/references/model-prompting-notes.md:46-52`

*(Fable fix 2, accepted. This site was MISSED in the design put to
review, and it is the widest of the four.)*

It states, for "Same-harness Fable seats (panel lane, whole-branch
reviewer, escalation)", that "conversation state persists across resume",
citing the same 2026-07-26 probe. Two defects:

1. It is the retired guarantee, in a file every dispatch consults. Left
   unedited the guarantee survives the fix.
2. It is wider than even the old contract. `agents/fable-reviewer.md`
   contains no mention of resume at all - verified, it is
   single-dispatch - so the sentence guarantees resume for a seat that
   never resumes.

Both are corrected: the claim is scoped to the seats that actually
resume, and stated as best-effort.

### Site 5 - recording a fresh re-dispatch as one

A fresh re-dispatch after a failed resume is RECORDED as a fresh
dispatch, so a panel that lost round continuity cannot report as intact.
The reporting session did this voluntarily; this makes it required.

### Site 6 - the per-round recall check

`panels.md:62-63` says round continuity "is evidenced by transcript
recall", but nothing requires the driver to check it, so a resume that
succeeded while state was quietly lost passes unnoticed. The driver must
perform and bind a recall check each round.

*(Fable fix 3, accepted. Two constraints on its shape:)*

1. **The recalled item must NEVER appear in any resume message.** If it
   rides the message, a freshly re-primed agent echoes it back and the
   check self-satisfies, proving nothing. The check binds the STRONG
   form: the agent is asked about something established in an earlier
   round that the current message does not contain. The probe
   demonstrates the distinction and rates the strong form higher.
2. **A failed recall routes to `panel-lane-loss`**, exactly as a failed
   resume does under site 3. Without this the new control detects lost
   continuity and then quietly re-dispatches, recreating the site-2
   defect one layer up.

## Sequencing: tests before text

Both affected regions are locked, so per `CLAUDE.md` the pins in
`evals/multi-model-verify/` change FIRST. Named explicitly so a partial
fix cannot ship, per the tick-off-every-part rule:

- `evals/multi-model-verify/test_seat_reshuffle.py:59-60` pins the exact
  sentence site 1 rewrites: `"the resume surface carries no model
  parameter"` and `"probed 2026-07-26"`.
- Any contract region ADDED or REMOVED also requires editing
  `DECLARED_REGIONS` in `evals/multi-model-verify/test_contract_coverage.py`
  (a set compared both ways: a missing region and an undeclared region
  both fail).
- Every new locked region must sit WHOLE inside a single pin, in one of
  the three assertion clause forms `CLAUDE.md` permits.

## Out of scope, filed rather than fixed

The Fable sweep for the class *"a contract claim stated as a guarantee,
resting on a probe narrower than the claim"* returned one clear instance
(site 4, in scope and fixed here) and one borderline instance:

`model-prompting-notes.md:337-342` states a subscription tier map
("free/Go tiers get Terra only; Plus and above get Sol - probed
2026-07-12") on the strength of a probe one account could only have run
from its own tier, with no probe record cited. The operative diagnostic
next to it is narrower and sound. Low stakes: it feeds a consent gate,
not a merge gate. Different subsystem from item 50.

**Filed as a new backlog item rather than fixed here**, to keep this
cycle scoped.

The sweep explicitly cleared `backup-lane.md:195-209`, `:552-556`,
`SKILL.md:64-72` and `model-prompting-notes.md:330-332`, which scope
their probes correctly or refuse to generalize.

## Verification

- The five gates in `CLAUDE.md`, both PowerShell hosts.
- `python evals/tools/check_exact_line_oracles.py` and the contract
  coverage checker must stay green with the new and edited regions.
- Behavioural evals are opt-in and this cycle edits skill contract text,
  so `python evals/tools/run_behavioral_evals.py --changed` runs before
  merge.
- A diff debate before merge, per the repo flow. Ask it to sweep the
  CLASS and name an instance or report none, which is what ended 0.26.0.
