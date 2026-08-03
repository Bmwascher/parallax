## Claim 15 — Windows CI is broken

The core claim is confirmed. Both Windows steps pass the nonexistent `evals/multi-model-verify/test_kimi_lane_lock.py` to pytest, and pushes trigger the workflow. Task 1 happens to recreate that exact pathname. `.github/workflows/skill-evals.yml:7-9,79-99`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:79-82`

History inspection also confirms that `775472c` deleted the predecessor test and tool, while the previous test explicitly expected this workflow to run it under both interpreters. `775472c^:evals/multi-model-verify/test_kimi_lane_lock.py:30-42`; `775472c^:tools/kimi-lane-lock.ps1:1-14`

One causal sentence is wider than its evidence: no configured upstream does not prove the branch was never pushed under any ref, nor that no equivalent workflow run occurred. The local configuration proves only that this local branch has no `remote`/`merge` association. Unless remote ref or Actions history is checked, narrow this to “no upstream is configured, and no local remote-tracking ref contains HEAD.” `.git/config:9-14,38-39`

I could not reproduce the reported pytest exit 4 because this sandbox has no `python`. The missing-path defect itself is nevertheless established directly by the workflow and filesystem inspection. `.github/workflows/skill-evals.yml:84,95`

Repairing the workflow explicitly should include a portable path-existence oracle for every explicitly named test module, so deleting a suite cannot leave a stale workflow entry until the branch is pushed. The existing workflow currently relies on pytest itself to discover that error. `.github/workflows/skill-evals.yml:79-99`

**Claim 15 — FIX:** accept the merge blocker; explicitly repair and path-check the workflow, but strike or independently verify the “never pushed / job never run” inference.

## P1 — Make the nonce visible

This closes the lost-nonce deadlock without weakening the property the nonce actually carries. The nonce is already stored in readable lock JSON, the design uses it to distinguish acquisitions and defeat late releases, and the overrides expressly provide no authentication. Printing it changes discoverability, not the authority boundary. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:87-93,140-144`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:211-215,261-267,280-295`

Make the held status object contain every force-release field: `host`, `ownerPid`, `ownerStartTicksUtc`, `debateId`, and `nonce`. `debateHome` may also be reported operationally, but it is not part of the complete release identity. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:89-104,140-146`

Freeze acquire behavior as a state table:

- `free` or dead holder, nonce absent: create/reclaim with a new nonce.
- `free` or dead holder, nonce supplied: exit 2.
- Live exact identity including supplied nonce: idempotent success.
- Live same non-nonce fields with nonce absent or different: contention.
- Live different identity: contention regardless of supplied nonce.

That preserves rule 3’s debate-scoped uniqueness and prevents a supplied old nonce from being reused for a new acquisition. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:132-142`

Add tests proving status-provided identity can force-release, an old nonce fails after reclaim, and routine status remains read-only. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:140-146`

**P1 — PASS.**

## P2 — Start-time failure oracle

Use the explicit seam as the primary oracle. A chosen SYSTEM process is not deterministic across caller elevation, process choice, and machine policy; the plan’s invariant requires the branch itself to be exercised, not conditionally hoped for. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:19,130-150`

The seam should inject failure specifically after PID lookup succeeds but while reading `StartTime`; it must not bypass the entire liveness routine. It is safe for the seam to be monotonic: its only possible production effect is to classify the holder as alive and refuse takeover, never to reclaim a lock. Rule 5 requires exactly that outcome. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:133-139`

There is already a repo precedent for an explicit fault seam whose test proves a normally difficult cleanup branch. `tools/new-kimi-lane-home.ps1:416-423`; `evals/multi-model-verify/test_kimi_lane_home.py:102-106`

Keep the SYSTEM-process case as an optional live confirmation when the machine actually exhibits the required access failure; do not make it the gate.

**P2 — FIX:** test seam primary, SYSTEM fixture optional.

## P3 — Junction oracle

File identity is the right primary oracle for the settled “one physical credential” claim, and the write-through observation is a valuable independent behavioral oracle. Both measurements must fail hard if identity acquisition, reading, or hashing fails. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:165-181`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:288-295`

However, those two assertions still permit a correct canonical junction plus an extra copied credential elsewhere under the debate home. The original requirement also says no second copy exists. Add a physical-tree inventory that does not traverse reparse points and asserts that no standalone credential file exists beneath the debate home. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:289-290,323-324`

Use the full file identity returned for both opened paths, not a textual resolved path. The test should then mutate only an obviously fake lane fixture and observe the new bytes through the debate path. The real lane credential remains outside every destructive probe. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:23,35,288-295`

**P3 — FIX:** file identity primary and write-through required, plus a non-following physical inventory for extra copies.

## P4 — Host selector and CI matrix

This closes Task 1.8, Task 2.4, Task 5.5, and Task 9.2. The established pattern is exactly: prefer `PARALLAX_PS_HOST`, mark the module Windows-only, and let the two workflow steps select 5.1 and 7 independently. `evals/multi-model-verify/test_codex_context_probe.py:35-67`; `.github/workflows/skill-evals.yml:46-99`

The Ubuntu job needs no behavioral mechanism beyond the platform marker for Windows-only modules. The marker must include `os.name != "nt"`; checking only whether `pwsh` exists is insufficient because Ubuntu supplies `pwsh` and previously ran Windows-specific suites accidentally. `evals/multi-model-verify/test_codex_context_probe.py:42-60`; `evals/multi-model-verify/test_review_mirror.py:30-45`

Add every offline dual-host module—including the refactored builder suite—to both Windows command lists. The external credential/client live suite remains opt-in and should not acquire CI credentials merely to avoid a skip. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:30-35,329-335`; `.github/workflows/skill-evals.yml:79-99`

For claim 15, separately add the portable workflow-path existence check; otherwise recreating the old filename repairs the stale line functionally but does not add a regression oracle. `.github/workflows/skill-evals.yml:79-99`

**P4 — PASS**, with claim 15’s path-existence oracle added separately.

## P5 — Contract-region placement

Use a separate declared region. Keep `lane-lock` for persistent-file semantics: location, liveness-only staleness, unevaluable-is-held, waiting, in-place transitions, and the two overrides. Add `lane-lock-call-lifecycle` for resolve-once ownership, builder parameters, nonce capture/retention, cleanup, and recovery. The repository explicitly says a region too long for one pin is two regions. `CLAUDE.md:55-92`

This also prevents the operational call sequence from becoming an incidental tail of a large mechanism pin. Both literals and both pins must appear exactly in r2, and both identifiers must be added to `DECLARED_REGIONS`. `evals/multi-model-verify/test_contract_coverage.py:624-683`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:367-390`

The existing `lane-home-isolation` region should retain freshness, junction, and unavailable-disposition rules; it should point into the call-lifecycle region instead of duplicating the complete nonce protocol. `skills/multi-model-verify/references/backup-lane.md:47-67`

**P5 — PASS with split:** `lane-lock` plus `lane-lock-call-lifecycle`.

## Round 2 overall verdict

**FIX.** P1 and P4 stand. P2 needs the seam promoted to the primary oracle; P3 needs a non-following inventory in addition to identity and write-through; P5 should be split into two declared regions. Claim 15 is a confirmed merge blocker, but its “never pushed” explanation remains wider than the locally verified evidence.

## Final check

- **UNVERIFIED:** measurements 1–21 remain external empirical results recorded by the design, not reproduced here. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:35-67,348-365`

- **UNVERIFIED:** the exact pytest exit code reported for the missing CI file; `python` is unavailable here. The missing file reference itself was verified. `.github/workflows/skill-evals.yml:84,95`

- **UNVERIFIED:** whether this branch or equivalent HEAD was ever pushed or received a GitHub Actions run. Local configuration proves no upstream association, not remote history. `.git/config:9-14,38-39`

- **UNVERIFIED:** whether a suitable SYSTEM-owned process reliably produces the proposed split success/failure behavior; that is why it should not be the primary gate. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:135-136`

- **UNVERIFIED:** P5’s eventual exact region literals and pins; r2 has not yet been written or read. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:376-390`

No files changed.