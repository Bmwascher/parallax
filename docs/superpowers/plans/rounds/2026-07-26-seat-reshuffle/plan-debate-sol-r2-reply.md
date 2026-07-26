1. Existing-suites-green: the registry edit now lands with `panels.md` in Task 3, while Task 1 expects only the ten new failures (`docs/superpowers/plans/2026-07-26-seat-reshuffle.md:222-240`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:447-452`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:551-577`). This matches the spec’s existing-suite invariant (`docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md:307-340`).

**ACCEPTED**

2. Participants post-loss mapping: the format now distinguishes completed panels from post-loss continuations, lists only terminal-verdict lanes after loss, and records the lost lane/class in failure prose (`docs/superpowers/plans/2026-07-26-seat-reshuffle.md:667-675`). This matches the spec (`docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md:188-193`).

**ACCEPTED**

3. No-fallbacks-banner: the test and artifact carry the same complete sentence, including “no fallbacks banner (nothing degraded)” (`docs/superpowers/plans/2026-07-26-seat-reshuffle.md:162-170`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:690-705`). This now implements the full Kimi panel-entry contract (`docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md:144-151`).

**ACCEPTED**

4. README panel option: the Mermaid now has an explicit user-invoked panel node connected to both plan and diff debates (`docs/superpowers/plans/2026-07-26-seat-reshuffle.md:1052-1067`), satisfying the spec’s visual requirement (`docs/superpowers/specs/2026-07-26-seat-reshuffle-design.md:289-295`).

**ACCEPTED**

5. Task 8 ordering: the smoke now commits before the final Fable review, but the core SHA problem remains. The plan reviews and debates immutable head H, then commits the Fable artifact and debate record after the terminal verdict, producing new head H+1 (`docs/superpowers/plans/2026-07-26-seat-reshuffle.md:1617-1635`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:1652-1655`). The same plan says any extra post-review commit forces re-review (`docs/superpowers/plans/2026-07-26-seat-reshuffle.md:1375-1381`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:1390-1396`), and the actual verifier accepts only the pushed SHA itself or an attested merge parent2 (`tools/verify-attestation.ps1:5-11`; `tools/verify-attestation.ps1:161-183`).

Specific fix: do not commit those artifacts onto the reviewed branch after the verdict. Retain them untracked through ship or on a separate, non-merged evidence ref/location. Otherwise H+1 requires another review and attestation.

**REFUTED**

6. Mislabel and dead-agent scope: the execution note now correctly names Task 8 Step 5 (`docs/superpowers/plans/2026-07-26-seat-reshuffle.md:1652-1655`). The smoke explicitly keeps dead-agent behavior observation-only and OPEN if no death occurs (`docs/superpowers/plans/2026-07-26-seat-reshuffle.md:1611-1615`), matching the probe’s residual limit (`docs/superpowers/plans/rounds/2026-07-26-seat-reshuffle/subagent-resume-probe.md:77-85`).

**ACCEPTED**

The independent replace-extent correction is also valid: the plan now quotes the target file’s actual third-bullet ending (`skills/multi-model-verify/references/model-prompting-notes.md:15-18`; `docs/superpowers/plans/2026-07-26-seat-reshuffle.md:758-762`).

The count correction is accepted: the plan contains ten anchored edits—seven insertions and three replacements—and every current anchor sequence occurs exactly once. No additional evidence-backed defect was found in those amended ranges.

UNVERIFIED: pytest totals remain runtime-unverified because this shell has no Python interpreter; the static test arithmetic and byte-exact pins are consistent.

**FIX**