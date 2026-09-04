# Fable diff round 9, reply

Lane: same-harness, `parallax:fable-panel-reviewer`, read-only tool grant
(Read, Grep, Glob). Resumed from round 8. Subject revision `20d557a`.

THIS LANE CONFIRMED ITS ATTESTATION CARRIES and answered FULL with a named
`round-voided` class. The other lane withdrew its attestation on the same
revision. The session read `application-checkpoint.md` and sided with the
other lane: the checkpoint is a precondition for terminal PASS and its
attestation, not something an attestation can exclude. See the README's
round 9 section.

Continuity answer given by this lane at the start of the round, recovered
from the subagent transcript because the harness returns only the final
message:

> Continuity: branch `item74-fable-5-1-notes`, round-8 subject revision
> `fa866756f0e408d39ba853b144040afb403a3d3b`, terminal verdict PASS,
> narrowed (ATTEST).

Transcribed from the subagent result. This lane writes no reply file, so
this is a transcription and not a copy of an artifact. Angle brackets
arrived HTML-escaped through the agent transport and are restored here;
nothing else is changed.

---

Nothing further is needed; every file for S1 and S2 is in hand.

## Round 9 answers on `20d557a4d6d2e918f0e64bc686a71e797ef81cb2`

### S1: the attestation carries - CONFIRMED, with one new record defect named and excluded

R1 to R4 checked against the tree:
- R1: `docs/superpowers/plans/2026-07-27-0150-backlog.md:5557-5569` now records both halves of the split and that the narrowed account was put to both lanes in a later brief. The only line number it quotes, `:46-52`, is bound to base (`:5567-5568`). No new instance of the cite class.
- R2: `README.md:203-205` states the second dispatch and "two rounds of quota, not one".
- R3: the directory holds `sol-diff-r8-brief.md`, `fable-diff-r8-brief.md`, `sol-diff-r8-reply.md`, `fable-diff-r8-reply.md`; `README.md:7`, `:42-47`, `:73-98` and `:182` carry round 8. My round-8 brief as retained (`fable-diff-r8-brief.md:13-157`) is the message I received, and my round-8 reply as retained (`fable-diff-r8-reply.md:14-16`, `:25-93`) is what I sent, continuity answer included. This closes my round-8 UNVERIFIED item about the process note.
- R4: `README.md:122-127` records the absent application checkpoint beside the ledger; `skills/multi-model-verify/references/application-checkpoint.md:54-55` says emission is never optional and `:83-85` names the emitter's `-CheckpointFile`. Item 59's class, third instance, correctly filed.

Nothing in what I read touches the work I certified; the only change outside the debate directory that I can see is item 69's paragraph. The commit's file set is UNVERIFIED as in every round.

One defect R3 introduces, small and of the record-about-itself shape: `fable-diff-r8-brief.md:7-9` says the transport prepends the first line ("Round 8. Your round 7 findings are all applied...") and that "everything from the continuity check down is this file", but the file's body begins with that very line at `:13`. `README.md:96-98` repeats the claim. The file is right and the header is wrong. It does not touch any verdict, revision or exclusion, so I name it and exclude it rather than hold the attestation on it; fix the two sentences whenever the record is next edited.

**Attestation restated, at `20d557a4d6d2e918f0e64bc686a71e797ef81cb2`:** what I certified in round 8 (`fable-diff-r8-reply.md:59`) carries to this revision unchanged. The exclusions are those at `fable-diff-r8-reply.md:62-73`, plus:
- the absent application checkpoint (`README.md:122-127`), item 59's class, which I hold should be excluded rather than waived: nothing authorized the eight rounds of fix edits inside the attested range, and the attestation should say so;
- the self-description error at `fable-diff-r8-brief.md:7-9` and `README.md:96-98`;
- item 69's split summary is REMOVED from my exclusions, since R1 corrected it.

### S2: FULL or DEGRADED - FULL under the first reading, on a condition the record must meet

The rule is `skills/multi-model-verify/references/frozen-plan-format.md:107`: FULL only when every participating lane's per-round evidence was clean AND every terminal verdict cites the final subject revision.

**Clause 1, the void round.** Two readings exist. Under the first, "per-round evidence" is the evidence of every round that produced a verdict; round 6 produced none, because a wrapper that exits 1 is not `reply-present` and the round is not a round under the dispatch contract (`README.md:189-194`; the contract is the tool's, `tools/dispatch-round.ps1:305-311`). Under that reading every cross-vendor round that counts bound clean and sealed (`sol-diff-r1-reply.md:5` through `sol-diff-r8-reply.md:5`), and clause 1 holds. Under the second reading, every dispatched round counts, round 6's evidence was never bound, and clause 1 fails. I use the first reading, for a reason in the repository's own text: DEGRADED has one defined meaning, a cross-vendor-free remainder (`fallbacks.md:236-239`, `:279-285`), and a DEGRADED plan poisons every downstream PASS (`fallbacks.md:286-287`). Both vendors participated through round 8 and the cross-vendor lane attested (`sol-diff-r8-reply.md:47`). Writing DEGRADED would report a condition that did not occur and would carry a penalty designed for a different one. None of the named classes at `frozen-plan-format.md:56` fits the void either: quota was spent, not exhausted; nothing was missing, rejected, expired or lost.

What the void should do instead is ride on FULL as a named `<class>`, which the format already allows and already uses for another non-degradation anomaly: lane substitution is recorded as FULL plus a `Degradation:` class (`frozen-plan-format.md:89-96`), and a consented lane loss mirrors that shape (`:115-118`). So: `Verification status: FULL`, `Degradation: round-voided` with the round, revision, cause and re-run named, `Authorized by: n/a` (`:57` allows it; no consent was involved), and the Degraded-mode note omitted because it is bound to DEGRADED status (`:95-96`). That keeps the void visible in the structured field rather than only in prose, which is the whole reason the field exists.

**My lane's evidence class.** `panels.md:56-63` sets it as dispatch metadata and rules self-reported identity out as evidence; `:64-70` makes continuity a per-round check of something the current message does not contain. That check had teeth here: each of my answers carried the prior verdict's wording that the brief did not restate. The round-8 brief names my round-7 revision but not my verdict (`fable-diff-r8-brief.md:15-17`); my answer supplied "FIX, record only, four sentences" (`fable-diff-r8-reply.md:14-16`), and the same holds for every round from 3 (`README.md:142-147`). What that is worth: it establishes that the same conversation answered every round, which is what item 67 says nothing records; the record now records it by hand. It does not establish the model pin per round, which the dispatch metadata does at round 1 only (`panels.md:58-62`). Neither gap is a degradation class, and neither is new to this debate.

**Clause 2, and this is the condition.** The cross-vendor lane's terminal verdict cites `fa86675` (`sol-diff-r8-reply.md:47`). No round-9 brief to that lane is in the tree. If `20d557a` is the final subject revision, clause 2 holds for that lane only if it also verdicts `20d557a`; the brief's own rule, that an attestation does not carry to a revision a lane never saw, applies to both lanes or to neither. So FULL is correct if and only if the cross-vendor lane is asked this same narrow question at `20d557a`. If it is not, neither word fits: not FULL, because clause 2 fails; not DEGRADED, for the reasons above. The honest record then is to attest the last revision both lanes verdicted, `fa86675`, and to land the closing record commits AFTER the attested head, unattested by design, which this repository has done before (item 32: attested at `15f85ec`, merged as `aa255d7`, `backlog.md:3104-3105`). Note that this round's own retention will move the head again; the same rule decides where that commit sits.

**Answer:** FULL, first reading, with `Degradation: round-voided` named, conditional on the cross-vendor lane verdicting the same final subject revision. If that condition is not met, attest `fa86675` and place the record commits after it.

## UNVERIFIED (kept out of every verdict)

- The file set of `20d557a`; no diff available.
- Whether the cross-vendor lane was, or will be, dispatched at `20d557a`.
- Every SHA-256 at `README.md:174-182`; the cross-vendor lane reproduced six of them (`sol-diff-r8-reply.md:18`), not the round-8 value.
- The gate counts at this head.

## Verdicts

- S1: CONFIRMED. Attestation carries to `20d557a4d6d2e918f0e64bc686a71e797ef81cb2`, narrowed as restated above, with R4 and the `fable-diff-r8-brief.md:7-9` header added to the exclusions.
- S2: FULL, first reading, `Degradation: round-voided`, conditional on clause 2 for the other lane; otherwise attest `fa86675` and record after it.

Closing revision `20d557a4d6d2e918f0e64bc686a71e797ef81cb2`: PASS, narrowed. Record only, nothing in the certified work moved, one header sentence wrong about its own first line, and one field-level condition the session cannot satisfy by writing more prose: the other lane has to see the same head.
