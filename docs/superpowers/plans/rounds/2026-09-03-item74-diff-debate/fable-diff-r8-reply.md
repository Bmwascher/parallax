# Fable diff round 8, reply

Lane: same-harness, `parallax:fable-panel-reviewer`, read-only tool grant
(Read, Grep, Glob). Resumed from round 7. Subject revision `fa86675`.

THIS IS THE LANE'S ATTESTATION, narrowed. It is the first round in which
this lane found no defect of the record-about-itself shape it had found in
each of the three rounds before.

Continuity answer given by this lane at the start of the round, recovered
from the subagent transcript because the harness returns only the final
message:

> Continuity: branch `item74-fable-5-1-notes`, round-7 subject revision
> `08ba01b7f62b4bf10ec4859e0748656689d0a882`, terminal verdict FIX, record
> only, four sentences.

Transcribed from the subagent result. This lane writes no reply file, so
this is a transcription and not a copy of an artifact. Angle brackets
arrived HTML-escaped through the agent transport and are restored here;
nothing else is changed.

---

Nothing further is needed; every file for Q1 to Q5 is in hand.

## Round 8 verdicts on `fa866756f0e408d39ba853b144040afb403a3d3b`

### Q1: P1 to P7 - PASS, one of them unverifiable by this lane

- P1: `README.md:142-152` states the trailing-newline removal and the reason the table hashes the source; `:161` adds round 7. Whether the values reproduce I cannot check; UNVERIFIED as in every round.
- P2: `README.md:184-192` states what the void meant for the verdicts, the re-dispatch at round 7, and where that reply sits; `:41` carries the round-7 verdicts; `sol-diff-r7-reply.md:37` is FIX on the hash method alone, as stated. `sol-diff-r7-brief.md:16-36` discloses the void to that lane in its own brief, as `:190-191` claims.
- P3: `README.md:5-12` splits the two bindings and states the briefs entered during round 6.
- P4: `fable-diff-r6-reply.md` and `fable-diff-r7-reply.md` exist. Both continuity answers are mine, word for word (`r6:15-18`, `r7:14-17`). Both bodies are my final messages, complete and unchanged (`r6:27-95`, `r7:26-102`), including the FIX verdicts, the exclusion lists and every UNVERIFIED item.
- P5: `README.md:55-60` states the error was put to both lanes in round 4, citing `sol-diff-r4-brief.md`, where it stands at `:45`.
- P6: `README.md:194-198` cites the tool and withdraws "already written".
- P7: `README.md:200-208` records the round-1 incident, marks it as recollection with no artifact, and states the material difference (fired at prepare, no quota spent).

### Q2: the record is true about itself - PASS, NONE found

Directory listing: 21 files. `README.md:64-79` names them exactly: the whole-branch review, briefs 1 to 7, cross-vendor replies 1 to 5 and 7, same-harness replies 2 to 7, and this file. The table at `:33-41` has a retained reply or a stated absence for every cell: Fable round 1 (`:87-92`), Sol round 6 (`:72-74`). The same-harness briefs are the third stated absence (`:81-85`); the brief's "two" undercounts the README's own list, and the README is the one that is right. The hash table (`:154-161`) covers rounds 1 to 5 and 7 and omits 6, matching the void. `:69-70` and `:133` are supported by `sol-diff-r7-reply.md:19` and `:15`. I looked for a fifth defect of the shape and found none.

### Q3: honest about the session - PASS, two observations, neither a FIX

The record now names the session as author of every error it corrects (`:5-12`, `:55-60`, `:144-147`, `:175-178`, `:184-185`, `:196-198`, `:200-208`) and attributes each catch to the lane that made it. Nothing I read softens a finding or drops a caveat.

Two observations, not manufactured into fixes:
- The one live document that also summarizes the split, item 69 at `backlog.md:5557-5562`, describes it as a split over ownership and does not carry the second disagreement the README now records (`README.md:43-48`). What it says is true; what it omits is the fifth cite's status. It was passed in rounds 4 and 5 and no amendment since touched it, so it sits under the boundaries. One clause would align it, at the session's discretion.
- The cost paragraph (`:180-182`) counts one round's quota; the remedy at `:189-190` was a second dispatch, whose quota is the other half of the cost. Implied, not stated.

### Q4: scope - UNVERIFIED

No diff available. Everything I read outside the debate directory (`backlog.md:5536-5565`) reads as in round 7.

### Q5: attestation - I ATTEST, narrowed

Both lanes have now judged a revision that carries both lanes' round-7 findings. The cross-vendor lane's round-7 FIX (`sol-diff-r7-reply.md:37`) is on the hash method alone, and the method is corrected at `README.md:142-152`; whether the values reproduce is that lane's to confirm in this round and not mine.

**What I certify, at `fa866756f0e408d39ba853b144040afb403a3d3b`:** the work of the branch as reviewed from round 2 on. The dispatch fix and its pin (`tools/dispatch-round.ps1:588-592`, `evals/multi-model-verify/test_dispatch_round.py:429-439`); the six dispatch-wording replacements and the `-DispatchHost` sentence (`skills/multi-model-verify/SKILL.md:200-203, :214, :302`, `references/backup-lane.md:143, :205, :558`); the Fable 5.1 section (`references/model-prompting-notes.md:28-114`) stating nothing as measured that the tree does not establish; its four pins (`test_multi_model_verify.py:1116-1146`); backlog items 74 to 77, the ranking and the status block as internally consistent; and the debate record as true about itself and about the session to the extent I could read it.

**What I exclude, by name:**
- the four pre-existing stale cites into `model-prompting-notes.md` at `backlog.md:3480`, `:4994`, `:5291` and `:5332`, recorded under item 69 (`:5538-5562`), item 69's work;
- the absent SDD ledger (`README.md:109-113`), item 59's class;
- the three baseline behavioural failures (`README.md:101-107`), measured once and never re-run;
- item 74's OPEN heading and present-tense Problem text (`backlog.md:375-390`, `:479-494`), closed by the plan's post-debate step (`docs/superpowers/plans/2026-09-03-item74-fable-51-notes.md:488-497`);
- the loss of panel blindness from round 5 (`README.md:19-29`), and with it the independence of every round-5-and-later finding, mine included;
- the void cross-vendor round 6 (`README.md:166-192`);
- the round-1 incident, which rests on recollection alone (`README.md:200-208`);
- the SHA-256 table (`README.md:154-161`) and the verbatim-copy claims for the cross-vendor briefs and replies, which this lane cannot compute or compare;
- the base read for the round-4 split, made on a `2580d56` copy rather than `5d20eed` (`fable-diff-r4-reply.md:29, :66`);
- the gate counts, which no lane re-ran (`README.md:98-99`);
- the amendment file sets of every round, never diffed by this lane;
- item 69's split summary at `backlog.md:5557-5562`, which omits the status disagreement, stated above as an observation.

The attestation is my lane's. It does not substitute for the cross-vendor lane's own round-8 word on the one thing only it can check.

## UNVERIFIED (kept out of every verdict)

- Every SHA-256 in `README.md:154-161`, under either method.
- That the retained briefs and replies match their sources; the round-7 confirmation covers briefs 1 to 6 only (`sol-diff-r7-reply.md:19`).
- The rollout byte counts (`README.md:181-182`) and the round-1 recollection (`:200-208`).
- Q4.
- The process note's claim that this round's briefs were written to disk; nothing in the tree shows it yet, and `README.md:81-85` will need one line when the closing commit retains them.

## Verdicts

- Q1: PASS.
- Q2: PASS, NONE.
- Q3: PASS, NONE that flatters; two observations above.
- Q4: no verdict; UNVERIFIED.
- Q5: ATTEST, narrowed as written above.

Branch, at amended subject revision `fa866756f0e408d39ba853b144040afb403a3d3b`: PASS, narrowed. The work has been clean since round 3 and the record is now true about itself and honest about the session as far as this lane can read; what it cannot read is named above and excluded rather than assumed.
