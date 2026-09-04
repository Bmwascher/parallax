# Fable diff round 7, reply

Lane: same-harness, `parallax:fable-panel-reviewer`, read-only tool grant
(Read, Grep, Glob). Resumed from round 6. Subject revision `08ba01b`.

This round read the incident note about the void round as an adversary and
found the omission the session had not seen: the record said what went
wrong but not what it meant for the other lane's standing verdict.

Continuity answer given by this lane at the start of the round, recovered
from the subagent transcript because the harness returns only the final
message:

> Continuity: branch `item74-fable-5-1-notes`, round-6 subject revision
> `233a340bc276da9cdb0358b6042c183c8f02dcca`, terminal verdict FIX, record
> only (README count, inventory, briefs, SDD disclosure, blindness
> statement).

Transcribed from the subagent result. This lane writes no reply file, so
this is a transcription and not a copy of an artifact. Angle brackets
arrived HTML-escaped through the agent transport and are restored here;
nothing else is changed.

---

Nothing further is needed; every file for N1 to N6 is in hand.

## Round 7 verdicts on `08ba01b7f62b4bf10ec4859e0748656689d0a882`

### N1: M1 to M6 land, and the README is true about itself - FIX, two defects of the same shape as round 6

Landed and checked:
- M1: "Four rounds" is gone; `README.md:3-10` binds its counts to a commit.
- M2: `README.md:55-65` lists briefs 1 to 6, cross-vendor replies 1 to 5, same-harness replies 2 to 5; the directory listing holds exactly those seventeen files plus the whole-branch review.
- M3: six `sol-diff-r*-brief.md` files exist; `README.md:67-71` states the same-harness briefs cannot be retained and why, and says what the next debate should do.
- M4: `README.md:80-99` carries the gate counts, the three case names with counts, and the SDD absence. The 0/4 cache figure and the attribution to the dispatch fix, which I had never been shown, were disclosed to the cross-vendor lane in round 1 (`sol-diff-r1-brief.md:120-128`), so the README is not inventing them.
- M5: `README.md:12-22` places the end of blindness at round 5 with the reason; `:108-109` uses "every round it was asked, which is rounds 3 onward".
- M6: `sol-diff-r2-brief.md:12-14` and `sol-diff-r3-brief.md:12-14` carry the continuity block; `sol-diff-r2-reply.md:11` and `sol-diff-r3-reply.md:11` open into G1 and H1. Asked and not answered, both halves checkable, as `README.md:115-119` says.

Two remaining defects of the shape the file itself names at `:5-6`:

1. **The binding sentence is false for the inventory.** `README.md:4-5` binds the file's counts to `233a340` "and this directory's own state at that commit". The six briefs were written into the directory while round 6 was running, and round 6's subject revision was `233a340` (`README.md:33`, `:151-155`), so at `233a340` the directory held no brief. The inventory at `:55-57` describes the state at this head, not at the commit the sentence names. FIX: bind the round counts to `233a340` and the inventory to "the commit that carries this text", or drop "and this directory's own state at that commit".

2. **A verdict in the table with no retained reply and no absence note.** `README.md:33` records the same-harness lane's round 6 as FIX. No `fable-diff-r6-reply.md` exists, `:62` lists that lane's replies only through round 5, and nothing says round 6's is missing, unlike the round 1 absence, which `:73-78` states plainly. FIX: retain the round 6 transcription with its continuity answer, or add one line saying it is not yet retained.

### N2: the retained briefs are consistent with the replies - PASS

Each reply answers exactly the claim set its brief poses: F1 to F7 (`sol-diff-r1-brief.md:73-104`, `sol-diff-r1-reply.md:11-38`), G1 to G5 (`r2-brief:86-105`, `r2-reply:11-19`), H1 to H5 (`r3-brief:83-101`, `r3-reply:11-38`), J1 to J6 (`r4-brief:76-103`, `r4-reply:13-23`), K1 to K6 (`r5-brief:68-97`, `r5-reply:20-32`). Round 6's brief has no reply, matching the void. No reply answers a brief it was not given. I cannot verify the briefs against what the lane was sent; see UNVERIFIED.

One thing the retained briefs now make visible: the "disagreed only on OWNERSHIP" error that E1 corrected did not live only in the README. It was the premise of both lanes' round-4 briefs (`sol-diff-r4-brief.md:45`; my round-4 brief said the same). `README.md:40-43` attributes it to "an earlier version of this file". The retained brief shows it also shaped round 4's adjudication for both lanes. See N3.

### N3: the incident note, read as an adversary - FIX, two omissions

What it does right: it names the session as the cause and not the tool (`README.md:151`), states the mechanism (`:154-155`), does not re-read the directory to rescue the round (`:147-149`), and gives the cost in quota and in rollout bytes (`:157-159`). The gate it names exists at `tools/dispatch-round.ps1:305-311`, and its message is quoted exactly.

What a reader needs and does not get:

1. **The consequence for the attestation is not stated.** The cross-vendor lane's last valid verdict is round 5, FIX, on `b9c17bc` (`README.md:32`, `sol-diff-r5-reply.md:36`). That lane has judged neither `233a340` nor this head, and its own round-5 FIX was applied in `233a340` and never confirmed by it. The note does not say whether round 6 will be re-dispatched to that lane, or that the branch would otherwise be attested with one lane's terminal verdict standing at FIX two revisions back. FIX: add that sentence, whichever way it goes.

2. **The first incident is cited and not recorded.** `README.md:160-161` says this is "the second time in this debate that a mid-round edit tripped the identity gate; the first was in round 1". Nothing in the directory describes the first: the round-1 brief does not mention it, and the round-1 Fable loss at `:73-78` is described as a context break, which is a different thing. FIX: record what happened in round 1, which lane, and what it cost, or drop the sentence.

Two smaller points. `README.md:163-164` says the rule "is simple and already written"; the gate is written (`tools/dispatch-round.ps1:305-311`, and its plan at `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:178`), but no prose rule in `skills/` says "do not touch the reviewed tree between `-Prepare` and the wrapper's exit" (grep for that rule's shapes in `skills/`: no hits), so "already written" should cite the tool, not imply a rule the skill text carries. And `:151-153` frames the write as "in response to the same-harness lane's round 6 finding"; the finding asked for retention, not for a write during a round, and the note's own next sentence carries the cause correctly. Keep the cause, drop the framing.

### N4: the blindness statement - PASS, with my own contamination check

`README.md:12-22` is accurate: round 5's briefs sent each lane to the other's round 3 reply (`sol-diff-r5-brief.md:73-75`; my round-5 brief did the same) and both went. For my lane: no finding of mine in rounds 5 or 6 originated in the other lane's text. Three verifications necessarily read it: K2 (`fable-diff-r5-reply.md:37`), and L1 and L3 in round 6, all of which were checks of claims the session relayed, which is the record-checking task itself. In round 6 I read `sol-diff-r5-reply.md` before writing L5; none of L5's four defects appears in it (`sol-diff-r5-reply.md:20-36`), so L5 was not seeded by that lane. The statement is sufficient once N3's first omission is added, because that is the finding the loss of blindness actually bears on: from round 5 the two lanes' errors were no longer independent.

### N5: scope - UNVERIFIED

No diff available. Everything I read outside the debate directory (`tools/dispatch-round.ps1:305-311`, the backlog sites cited in rounds 5 and 6) reads as before.

### N6: the branch

Not yet, and the reason is narrower than in any prior round. The work has been clean since round 3 and I would attest it now. What stops me is not the record's prose defects, which are two lines each, but the fact the incident note leaves out: the cross-vendor lane's terminal verdict on this branch is FIX (`sol-diff-r5-reply.md:36`), issued two revisions ago, and nothing in the record says whether that lane will see this head. A same-harness attestation over a cross-vendor FIX that was never withdrawn is exactly the "explicitly narrowed claim" case of `skills/multi-model-verify/references/debate-protocol.md:128-131`, and the narrowing has to be written by the session, not inferred by me.

When N1's two lines and N3's two sentences land, I attest, with the narrowed claim excluding:
- the four pre-existing stale cites into `model-prompting-notes.md` at `backlog.md:3480`, `:4994`, `:5291` and `:5332`, recorded under item 69 and not fixed here;
- the absent SDD ledger (`README.md:95-99`), item 59's class;
- the three baseline behavioural failures (`README.md:87-93`), measured once and not re-run;
- item 74's OPEN status and present-tense Problem text, to be closed by the plan's post-debate step (`docs/superpowers/plans/2026-09-03-item74-fable-51-notes.md:488-497`);
- the loss of blindness from round 5 (`README.md:17-22`);
- the void cross-vendor round 6 (`README.md:142-164`), and, unless that lane is re-dispatched, the fact that its last verdict on this branch is FIX on `b9c17bc`;
- everything under UNVERIFIED in this and prior rounds, chiefly the base read from a `2580d56` copy (`fable-diff-r4-reply.md:29, :66`) and the SHA-256 table (`README.md:131-137`).

## UNVERIFIED (kept out of every verdict)

- That the six retained briefs are byte-identical to what the cross-vendor lane was sent; the dispatch brief files are outside the tree, and the README's "canonical SHA-256 was recorded by the prepare step" (`sol-diff-r1-brief.md:3-6`) is not reproduced in the record.
- That the void round's output was not read (`README.md:147`).
- The rollout byte counts at `README.md:159`.
- Every SHA-256 in `README.md:131-137`.
- N5.

## Verdicts

- N1: FIX. Rebind `README.md:4-5`; add the round 6 same-harness reply or state its absence beside `README.md:62`.
- N2: PASS.
- N3: FIX. State the consequence for the cross-vendor lane's standing verdict; record or drop the first incident; cite the tool for "already written".
- N4: PASS.
- N5: no verdict; UNVERIFIED.
- N6: attestation deferred to N1 and N3; exclusions named above.

Branch, at amended subject revision `08ba01b7f62b4bf10ec4859e0748656689d0a882`: FIX, record only, four sentences. The work is attestable and has been since round 3; the retained briefs settle every question I could not check before; the void round is logged against the session and honestly on cause and cost. What the record still omits is the one fact an attestation reader must have: the other lane's last word on this branch is FIX, and the record does not say what becomes of it.
