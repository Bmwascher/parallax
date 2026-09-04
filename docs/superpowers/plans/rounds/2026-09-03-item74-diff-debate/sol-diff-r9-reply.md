# Sol diff round 9, raw reply

Lane: cross-vendor, `gpt-5.6-sol`, effort `high`, canonical route.
Session `01a06a45-3b54-77a3-9b37-e360b383d1ab`, resumed. Subject revision
`20d557a`. Evidence bound clean and sealed.

THIS LANE WITHDREW ITS ATTESTATION. It holds the missing application
checkpoint to be a precondition that cannot be reduced to an exclusion,
and rules the branch UNATTESTABLE. The session read the contract and
agrees with this lane over the other.

Copied verbatim from the dispatch directory's `reply` file. Not edited.

---

Branch `item74-fable-5-1-notes`; round 8 subject `fa866756f0e408d39ba853b144040afb403a3d3b`; terminal verdict PASS. `docs/superpowers/plans/rounds/2026-09-03-item74-diff-debate/sol-diff-r8-reply.md:32`

S1. FIX. R1–R3 land: the split now records both ownership and status disagreements, the void’s two-dispatch cost is explicit, and the round-8 attestations and inventory are retained. `docs/superpowers/plans/2026-07-27-0150-backlog.md:5557` `docs/superpowers/plans/rounds/2026-09-03-item74-diff-debate/README.md:40` `docs/superpowers/plans/rounds/2026-09-03-item74-diff-debate/README.md:73` `docs/superpowers/plans/rounds/2026-09-03-item74-diff-debate/README.md:201`

The attestation nevertheless does not carry. R4 discloses that review-driven fixes were applied without an application checkpoint; that checkpoint is the authorization to edit, applies to post-adjudication debate fixes, is never optional, and must precede terminal PASS and attestation. It cannot be reduced to an exclusion. `docs/superpowers/plans/rounds/2026-09-03-item74-diff-debate/README.md:122` `skills/multi-model-verify/references/application-checkpoint.md:13` `skills/multi-model-verify/references/application-checkpoint.md:18` `skills/multi-model-verify/references/application-checkpoint.md:52` `skills/multi-model-verify/references/application-checkpoint.md:65`

Specific fix: replay the review-fix application from its pre-fix revision under a checkpoint emitted before the first edit, append verification results, and re-review the resulting head. `skills/multi-model-verify/references/application-checkpoint.md:24` `skills/multi-model-verify/references/application-checkpoint.md:63`

S2. FIX — neither FULL nor DEGRADED is truthful. I apply “every round” to every dispatched, participating-lane round, including a quota-spent void. Round 6 is listed as a round and its dispatch completed but failed binding; a clean round 7 replacement does not retroactively make round 6’s evidence clean. FULL therefore fails the strictest-lane rule. `docs/superpowers/plans/rounds/2026-09-03-item74-diff-debate/README.md:40` `docs/superpowers/plans/rounds/2026-09-03-item74-diff-debate/README.md:189` `docs/superpowers/plans/rounds/2026-09-03-item74-diff-debate/README.md:204` `skills/multi-model-verify/references/frozen-plan-format.md:107`

DEGRADED would falsely describe a cross-vendor-free remainder: the cross-vendor lane remained and produced the round-8 attestation. `skills/multi-model-verify/references/fallbacks.md:234` `docs/superpowers/plans/rounds/2026-09-03-item74-diff-debate/sol-diff-r8-reply.md:3`

The record should currently carry a non-gating `UNATTESTABLE — mandatory checkpoint absent; participating-lane round voided and replaced`, because the emitter accepts only FULL or DEGRADED. Before emission, the format must explicitly define whether a quarantined, cleanly re-run void restores FULL or add an appropriate non-gating status. `tools/write-attestation.ps1:20` `tools/write-attestation.ps1:26`

UNVERIFIED: I did not independently rerun the gates or behavioural suite, and the original void dispatch artifact is not retained. `docs/superpowers/plans/rounds/2026-09-03-item74-diff-debate/README.md:111` `docs/superpowers/plans/rounds/2026-09-03-item74-diff-debate/README.md:114` `docs/superpowers/plans/rounds/2026-09-03-item74-diff-debate/README.md:191`

Terminal verdict: FIX — closing revision `20d557a4d6d2e918f0e64bc686a71e797ef81cb2` may not merge until the checkpoint violation and verification-status contract gap are resolved. `skills/multi-model-verify/references/application-checkpoint.md:65` `skills/multi-model-verify/references/frozen-plan-format.md:107`
