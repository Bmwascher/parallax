# Diff debate record - 0.27.0, backlog item 50

Mode: diff. Base `de85e8f`. Rounds: 2. Converged.

## Participants and lanes

- Session driver: Opus 5 (this session).
- Cross-vendor reviewer: `gpt-5.6-sol` via `codex exec`, reasoning effort
  high, session `01a01e6b-2be1-7690-b6f8-0c2d19bef000`, resumed for round 2
  so round 1's context carried.
- Required whole-branch review: `agents/fable-reviewer.md`, retained
  separately at `fable-review-de85e8f-f96f2ed.md` and cited by the round-1
  brief.

## Per-round evidence

Both rounds dispatched DETACHED from the first attempt. Both read the brief
as strict UTF-8 with `$OutputEncoding` set at script scope and restored in
`finally`; both briefs were verified PURE ASCII before dispatch, so the
5.1 code-page corruption class could not fire. Both ran under the verified
skill-suppression override whose SHA256 was re-checked at dispatch:
`180f09f5...432bb8`, produced by `tools/codex-context-probe.ps1` which
reported clean - 29 skills measured, 0 surviving suppression. Both calls
returned `LASTEXITCODE=0` and wrote their `--output-last-message` file, so
neither round was a transport failure.

## Round 1 - subject `bb386b0` - verdict FIX

One finding, appearing in two places. The branch corrected a claim that
outran its evidence for CONTINUITY and left the identical overclaim
standing for CONTAINMENT: `panels.md` said a version above the floor "buys
containment", and `model-prompting-notes.md` said containment "holds AT OR
ABOVE" the floor. Both assert every version above 2.1.216.

Claims 2, 4, 5, 6 and 7 PASS. Candidate (b), citation placement, ruled PASS
as a navigation nit. Both enforcement-absent instances confirmed and
accepted as item 67 follow-up scope rather than merge blockers.

**Adjudication: ACCEPTED, and the session reproduced it before accepting.**
The reviewer's sub-claim was sharper than the Fable lane's: the 2026-07-26
probe used a `general-purpose` subagent and never capability-tested
containment at all, which its own Residual limits state. So containment was
capability-tested on 2.1.237 ONLY, on two of nine resumes. The Fable lane
had flagged this and declined to assert it; the cross-vendor lane asserted
it and was right.

Fixed in `63a9b3a`, tests moved first at both sites, each new pin proven to
go red on a one-word mutation and green on exact restore. The floor did not
move.

## Round 2 - subject `63a9b3a` - verdict PASS

Both fixes ADDRESSED. Repeat-defect sweep found NO additional instance. The
reviewer was asked specifically whether the new wording now UNDERSTATES what
is known, since over-correcting an overclaim is its own defect; it judged
the wording accurate, because it retains the independently observed
no-model-parameter result while limiting capability-tested containment to
2.1.237.

Nothing was raised to apply, so the head does not move and the PASS is
terminal for `63a9b3a`.

## What the reviewer would not certify, correctly

- Containment on every untested version at or above 2.1.216: UNVERIFIED.
  That is the finding, now reflected in the contract text.
- A 2.1.233 failure specifically on the PANEL seat: UNVERIFIED. The probe
  says so itself.
- The red-before-green ordering and the mutation/restore runs: UNVERIFIED
  from a committed diff. It said plainly that its verdict does not rest on
  them. The session ran those checks and they are in the SDD ledger.

## The class, across the whole cycle

The defect class was: a claim stated more widely than its evidence, or a
rule whose enforcement is asserted but absent. It was found INSIDE this
branch's own fixes three times - the escalation seat, the
untestable-resumes clause, and the containment width - each caught by a
different reviewer, none by the author. The sweep question is what found
all three. Round 2's "none" is the first clean sweep of the cycle.
