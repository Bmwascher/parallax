# Diff debate record: the GPT-6 Astra brief-guidance set

**Mode:** diff
**Range:** c30a68624a18fc18ca7022f4c80abd34e3b22626..a341460b91c5c88a350b5408be5ae31035449678 (branch astra-prompting-guide; 3990f9c was the head the whole-branch review and round 1 saw, efaeaae the fix commit round 2 reviewed, a341460 the heading fix round 3 confirmed)
**Frozen plan:** none. The change was made directly from the user's request of 2026-09-05, which was the spec: fold the OpenAI GPT-6 Astra model guidance into the reviewer notes as the set followed for default Astra, without removing the Sol guidance.
**Participants:** Fable 5.1 (session) / GPT-6 Astra (codex exec, session 01a0707d-3a45-7282-adc9-3b2eb083479b)
**Rounds used:** 3 of 4 (fix-verify exchanges: 3 of 6)
**Outcome:** converged, terminal PASS at a341460
**Verification status:** FULL
**Degradation:** none
**Authorized by:** n/a (fix application authorized by the user, "go", 2026-09-05, under the application checkpoint named below)
**Route note:** effective route confirmed. All three rounds' transcript headers read `model: gpt-6-astra`, `provider: openai`, `reasoning effort: high`, `sandbox: read-only`, `workdir: C:\Users\Brandon\AppData\Local\Temp\kerev89`; rounds 2 and 3 resumed round 1's session id. All three rounds were dispatched through the INSTALLED 0.31.1 plugin, whose canonical declaration names Astra. Every round's reply was bound to its brief by the round-evidence binder, clean and sealed.
**Attestation:** `.git/parallax/attestations/a341460b91c5c88a350b5408be5ae31035449678.json` (PASS, FULL, 3 rounds, checkpoint-bound to `20260905T0241-3990f9c675ac.md`)

## Required whole-branch review

`agents/fable-reviewer.md` over c30a686..3990f9c, retained verbatim as `fable-whole-branch-review.md` beside this record. Ready to merge: with fixes; 0 Critical, 1 Important, 5 Minor. Session dispositions, carried into the round-1 brief and applied in efaeaae:

| Fable finding | disposition |
|---|---|
| I1 the non-interactive rule left the shared set when it moved under the Astra heading; the Kimi lane unnamed | accepted; the intro now carries the lane-invariant sentence Astra proposed in round 1, covering named Sol, the backup lane and the degraded skeptic; pinned |
| M1 the Astra sentences: every resume brief or round 1 only | accepted; one clause places them under the lean-brief rule |
| M2 two transport claims in the parameters bullet unmarked | accepted; `codex exec --help` on codex-cli 0.153.4, read 2026-09-05, is cited with its own limit, and configuration_update is marked as read from the page |
| M3 "carried as written" precedes a paraphrase | accepted; "carried in paraphrase, three phrases quoted" |
| M4 item 89's "six instruction sentences" | accepted; the count is gone |
| M5 the commit record named one Sol-era edit; there are two | accepted, record-only: "tell Astra" and "asking Astra" both became "the reviewer" |

## Behavioral evals gate

`python evals/tools/run_behavioral_evals.py --head --changed` before round 1. Six cases skipped (unchanged surface); three selected because their declared surface names model-prompting-notes.md: plan-mode-debate-runs (1/4), diff-mode-spec-fidelity (2/4), no-manufactured-objections (1/3), all FAIL. All three are harness-attributed and identical to item 87's run: the fixture workspace is git-initialised with no commit, so `new-review-mirror.ps1` refuses with "could not resolve HEAD" and the executor stops BLOCKED/DEGRADED-NOT-AUTHORIZED before any round (backlog item 68 Part D). The verdict files are retained beside this record as `behavioral-*.verdicts.json`. No case exercised the new brief sentences; item 89 stays open for exactly that reason.

## Rounds

| round | subject | brief | reply | verdict | evidence |
|---|---|---|---|---|---|
| Astra R1 (fresh) | 3990f9c | brief-astra-r1.md | reply-astra-r1.md | FIX: claims 2, 3, 5, 6 PASS; claim 1 five evidence-width defects; claim 4 the shared-rule sentence; claim 7 the backup lane's set; class sweep (a) (b) (c) reported | receipt-r1.json, binder-r1.json (clean, sealed) |
| Astra R2 (resume) | efaeaae | brief-astra-r2.md | reply-astra-r2.md | FIX: claims 1, 2, 3, 5 PASS; claim 4 item 89's heading contradicted its body | receipt-r2.json, binder-r2.json (clean, sealed) |
| Astra R3 (resume) | a341460 | brief-astra-r3.md | reply-astra-r3.md | PASS on both claims | receipt-r3.json, binder-r3.json (clean, sealed) |

Round-1 findings and their application, under the checkpoint named above (the checkpoint's dispositions table is the full list):

1. Five sentences in the Astra set asserted more than their evidence: "the brief closes the rest", "gains nothing from parallelism", "where a new tool would first show", "the logprobs options", and the "X, not Y" quotation. The first four were accepted and narrowed. The fifth was REFUTED on substance: the page does quote "X, not Y" and "X—not Y" in its stock-phrase prompt; the round-1 brief's source list had omitted it, and round 2's brief added it. The wording still changed to "three phrases quoted".
2. Astra's UNVERIFIED note that the testing bullet's "runs nothing" lacked evidence was accepted as a real defect: Astra ran git and PowerShell inside the read-only sandbox during round 1. The bullet now says the reviewer writes nothing, can run read-only commands, and is asked by no brief to run the gates.
3. Astra's claim-4 sentence and claim-7 sentence were adopted verbatim, the latter with a clause that the Astra set is the primary model's alone.

Round-2 finding: item 89's heading still said "no round has run under it". Accepted under an amendment to the same checkpoint; renamed in a341460 to "The Astra brief-guidance set awaits behavioural-suite measurement".

Deferred, both rounds: full-page paraphrase fidelity of the unquoted Astra sentences, which only the page settles and item 89 keeps open; and this retention record, which did not exist in any mirror.

## Voided rounds

None.
