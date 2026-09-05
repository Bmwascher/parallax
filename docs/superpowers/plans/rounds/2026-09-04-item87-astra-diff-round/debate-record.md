# Diff debate record: item 87, the Astra reviewer swap

**Mode:** diff
**Range:** adb9ac3da9670936db8e5a01407241dbb07657f3..ec804f73a88864b9bb4bd553be38154ade7b03e7 (branch astra-reviewer-swap; 63d04af was the head the whole-branch review and round 1 saw, ec804f7 is the fix commit round 2 confirmed)
**Frozen plan:** docs/superpowers/plans/2026-09-04-item87-astra-reviewer-swap.md, revision 8, FULL
**Participants:** Fable 5.1 (session) / GPT-6 Astra (codex exec, session 01a07000-a9db-7822-9ad4-4e5e77e4f621)
**Rounds used:** 2 of 4 (fix-verify exchanges: 1 of 6)
**Outcome:** converged, terminal PASS at ec804f7
**Verification status:** FULL
**Degradation:** none
**Authorized by:** n/a
**Route note:** effective route confirmed. Both rounds' transcript headers read `model: gpt-6-astra`, `provider: openai`, `reasoning effort: high`, `sandbox: read-only`, `workdir: C:\Users\Brandon\AppData\Local\Temp\kerev87`; round 2 resumed round 1's session id. Both rounds were dispatched through the INSTALLED 0.31.0 plugin, whose canonical declaration names Astra, so the model came from the notes and not from a session override.
**Attestation:** `.git/parallax/attestations/ec804f73a88864b9bb4bd553be38154ade7b03e7.json` (PASS, FULL, 2 rounds, checkpoint-bound to `2026-09-05T0030-63d04af09d17.md`)

## Required whole-branch review

`agents/fable-reviewer.md` over adb9ac3..63d04af, retained verbatim as `fable-whole-branch-review.md` beside this record. Ready to merge: Yes; 0 Critical, 0 Important, 5 Minor, all record-level. Session dispositions, carried into the round-1 brief:

| Fable finding | disposition |
|---|---|
| M1 plugin.json bumped to 0.31.0 inside a range whose frozen plan forbids it | accepted as a record defect; this record names the overridden constraint (plan Global Constraints, "the bump happens AFTER the diff debate") and the re-bump to 0.31.1 that follows this debate. The plan text is left as frozen. |
| M2 plan step 3 says the debate runs on the installed 0.30.1 "so Sol reviews its own replacement" | accepted; stale. The installed copy was 0.31.0 at 63d04af, so Astra reviewed its own promotion; the headers above are the evidence. |
| M3 the Sol alternate is declared but SKILL.md's route check accepts only the canonical pair | accepted as pre-existing scope; filed as backlog item 88. |
| M4 "these two declarations" above four lines | ride; resolved two paragraphs later. |
| M5 Task 4's dual-host counts absent from the record | accepted; filled during fix application: `test_codex_context_probe.py` 135 passed on pwsh 7 (51.83s) and 135 passed on Windows PowerShell 5.1 (49.07s). |

## Behavioral evals gate

`python evals/tools/run_behavioral_evals.py --changed` against the installed 0.31.0 cache (the plan said `--head`; the cache was content-identical to head and the runner's own help names the cache as the pre-merge form). Nine selected: PASS degraded-consent-gate, missing-reference-refusal, fix-application-checkpoint, fix-checkpoint-attended-stop; SKIPPED(manual) backup-lane-consented-substitution, panel-blind-relay; FAIL plan-mode-debate-runs (2/4), diff-mode-spec-fidelity (3/4), no-manufactured-objections (1/3). All three failures are harness-attributed: backlog item 68 Parts A and C (no agent-dispatch tool, no wait tool) and the new Part D (a `with_reference` fixture has no commit, so the mirror tool refuses it). The plan-mode transcript shows the installed dispatch tool preparing a wrapper with `-m gpt-6-astra` under the task name `Astra R1 debate round`, which is live evidence the swap works from the installed copy. A first attempt of the gate failed entirely because the headless CLI was logged out; the user logged in and it was re-run.

## Rounds

| round | subject | brief | reply | verdict | evidence |
|---|---|---|---|---|---|
| Astra R1 (fresh) | 63d04af | brief-astra-r1.md | reply-astra-r1.md | FIX: two Minor test-coverage gaps; claims 1, 3, 4, 6 PASS; class sweep clean for all five shapes; both plan departures accepted without amendment | receipt-r1.json, binder-r1.json (clean, sealed; canonical brief sha 5d3decc1…cc04) |
| Astra R2 (resume) | ec804f7 | brief-astra-r2.md | reply-astra-r2.md | PASS on all five claims; Astra re-ran both mutations on both hosts | receipt-r2.json, binder-r2.json (clean, sealed; canonical brief sha 7fbaf6bc…cc2e) |

Round-1 findings and their application, under the checkpoint named above:

1. The lane test's ordering assertion chained only the three model-id lines, so the two effort lines could swap unnoticed. Accepted; the chain now fixes all five positions. Red direction shown: efforts swapped, chain False.
2. No test placed a `### Skill roots` table inside the container after `### Available skills`; Astra widened the prefix slice in memory and every existing test stayed green. Accepted, overturning the Fable review's ride on that evidence; a new test holds the boundary. Red direction shown for real: slice widened, new test failed, sibling still passed, file restored with an empty diff.

Non-blocking observation left as-is (round 2, UNVERIFIED list): the new test's docstring says "every test stayed green" under Astra's round-1 mutation, and Astra notes round 1 exercised functions in memory rather than the full suite. A docstring edit would move the head past the terminal PASS, so it rides.

## Departures from the frozen plan, both user-directed

- The version was bumped to 0.31.0 and installed BEFORE this debate so the user could test the swap live in other sessions while the closing gates ran. The plan forbids that ordering; the re-bump to 0.31.1 after this debate is what keeps the installed copy from going cache-stale.
- This debate therefore ran on the installed 0.31.0 with Astra as the reviewer, not on 0.30.1 with Sol as plan step 3 expected.

## Voided rounds

None in this debate. The plan debate's two voided rounds are recorded in the plan's own debate record.
