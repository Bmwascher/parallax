Judged HEAD: `ad61503e5814819f4616e2f26ed9b1b72f787606` on `feat/lane-release-and-round-cap`.

1. The write-site implementation materially closes the contention window: both HELD writers call `Assert-OwnerLiveForWrite` before constructing and writing the new record (`tools/kimi-lane-lock.ps1:638`, `tools/kimi-lane-lock.ps1:648`, `tools/kimi-lane-lock.ps1:663`, `tools/kimi-lane-lock.ps1:675`). The zero-length remedy is correct: a write-site refusal initializes a newly created file to free (`tools/kimi-lane-lock.ps1:549`, `tools/kimi-lane-lock.ps1:556`), as does the existing nonce-against-free refusal (`tools/kimi-lane-lock.ps1:618`, `tools/kimi-lane-lock.ps1:632`). The DEAD gate refuses before opening the file, so it has no equivalent cleanup obligation (`tools/kimi-lane-lock.ps1:595`, `tools/kimi-lane-lock.ps1:603`). I found no other newly added refusal leaving a fresh zero-length file.

   The contention oracle is not synchronized as claimed. Its docstring says the fixture is synchronized (`evals/multi-model-verify/test_kimi_lane_lock.py:1273`), but after launching the waiter it merely sleeps two seconds (`evals/multi-model-verify/test_kimi_lane_lock.py:1290`, `evals/multi-model-verify/test_kimi_lane_lock.py:1297`). If the victim is killed before the waiter completes its pre-loop measurement, the DEAD gate returns 2 and the test’s final assertions still pass after the holder is released (`tools/kimi-lane-lock.ps1:595`, `evals/multi-model-verify/test_kimi_lane_lock.py:1298`, `evals/multi-model-verify/test_kimi_lane_lock.py:1300`, `evals/multi-model-verify/test_kimi_lane_lock.py:1309`). The tool already emits a deterministic `"holder"` contention signal (`tools/kimi-lane-lock.ps1:705`) and the fixture already has `wait_for_signal` (`evals/multi-model-verify/test_kimi_lane_lock.py:132`); the test must pass that seam and await `"holder"` before killing the victim.

   The prose also overclaims “every record write”: free-record writes legitimately do not call the helper (`tools/kimi-lane-lock.ps1:557`, `tools/kimi-lane-lock.ps1:633`, `tools/kimi-lane-lock.ps1:735`). More precisely, the helper precedes every HELD-owner write. It also establishes a LIVE measurement before the write, not atomic liveness at the instant of writing—the first call is followed by nonce generation, record construction and serialization (`tools/kimi-lane-lock.ps1:638`, `tools/kimi-lane-lock.ps1:639`, `tools/kimi-lane-lock.ps1:648`). Narrow the guarantee and name that unavoidable residual.

   **FIX — replace the timed sleep with the existing contention signal, and change “every record write/requires LIVE” to “every HELD-owner write is preceded by a LIVE measurement,” explicitly admitting the remaining check-to-write race.**

2. Amendment 2 and item 26 correctly narrow the evidence to one added PowerShell shell frame and name unlisted wrappers as open (`docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:817`, `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:823`, `docs/superpowers/plans/2026-07-27-0150-backlog.md:1683`, `docs/superpowers/plans/2026-07-27-0150-backlog.md:1691`).

   The operative lifecycle contract still says the owner “is the harness session process” and then directs callers to `-ResolveOwner` (`skills/multi-model-verify/references/backup-lane.md:107`, `skills/multi-model-verify/references/backup-lane.md:112`). That is wider than the admitted implementation: an unlisted `node.exe` or `python.exe` wrapper is accepted as owner (`docs/superpowers/plans/2026-07-27-0150-backlog.md:1688`). The exact stale wording is pinned in the suite (`evals/multi-model-verify/test_backup_lane.py:253`, `evals/multi-model-verify/test_backup_lane.py:265`).

   **FIX — revise the lifecycle contract and its exact pin to say that `-ResolveOwner` returns the first ancestor outside the four named transports and therefore may return an unlisted wrapper, rather than asserting it returns the harness session process.**

3. The substantive fixture repair is complete, but its count is wrong. There are seven—not six—non-name invalid-schema fixtures in the parametrization (`evals/multi-model-verify/test_kimi_lane_home.py:1866`, `evals/multi-model-verify/test_kimi_lane_home.py:1872`). All seven now carry a valid `ownerName` while retaining their intended separate defect (`evals/multi-model-verify/test_kimi_lane_home.py:1682`, `evals/multi-model-verify/test_kimi_lane_home.py:1715`). The template comment correctly describes the three-field contract (`tools/new-kimi-lane-home.ps1:174`, `tools/new-kimi-lane-home.ps1:180`).

   **FIX — change “six non-name schema stubs” to “seven” in Amendment 2 (`docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:831`) and the disposition. No fixture-code change is needed.**

4. The operational rule is deterministic: no junction, symbolic link, or file link is followed, and encountering any reparse point makes the measurement incomplete and silent (`commands/doctor.md:251`, `commands/doctor.md:257`). That entire behavior is pinned (`evals/multi-model-verify/test_backup_lane.py:1614`, `evals/multi-model-verify/test_backup_lane.py:1621`).

   One explanatory claim is false for the enumerated file-link case: following a file link does not “measure a directory” (`commands/doctor.md:252`, `commands/doctor.md:254`). The exact pin preserves that same false statement (`evals/multi-model-verify/test_backup_lane.py:1615`, `evals/multi-model-verify/test_backup_lane.py:1618`).

   **FIX — replace “measures a directory that is not the debate home” with “measures a filesystem object outside the debate home,” in both prose and pin.**

5. The protocol text now resolves the contradiction: “converged with amendments” is agreement, after which amendments are applied and an adjudicated dry round is still required (`skills/multi-model-verify/references/debate-protocol.md:48`, `skills/multi-model-verify/references/debate-protocol.md:56`). The budget unit is explicitly every dispatched exchange, including unusable results, and exhaustion pauses rather than certifies (`skills/multi-model-verify/references/debate-protocol.md:79`, `skills/multi-model-verify/references/debate-protocol.md:87`). Those budget and dry-round rules have exact pins (`evals/multi-model-verify/test_multi_model_verify.py:819`, `evals/multi-model-verify/test_multi_model_verify.py:827`, `evals/multi-model-verify/test_multi_model_verify.py:838`).

   The claimed new convergence pin does not exist. Its test checks only that the phrase “converged with amendments” appears; deleting the agreement-not-termination clarification would leave it green (`evals/multi-model-verify/test_multi_model_verify.py:776`, `evals/multi-model-verify/test_multi_model_verify.py:781`).

   **FIX — replace the phrase-only regex with an exact pin covering agreement, application of amendments, and the mandatory adjudicated dry round; watch deletion of that clarification fail it.**

6. The index now attributes round 1 as “FIX; claims 1, 3, 4, 6, 7 and 8 require changes” (`docs/superpowers/plans/rounds/2026-08-04-transport-and-mirror/README.md:15`). The retained reply says claims 2 and 5 pass and those same six claims need fixes (`docs/superpowers/plans/rounds/2026-08-04-transport-and-mirror/plan-reply-r1b.md:1`).

   **PASS**

7. The write-site changes do not touch owner resolution. The missing creation-order guard and its exact PID-reuse consequence remain named beside the lookup (`tools/kimi-lane-lock.ps1:899`, `tools/kimi-lane-lock.ps1:909`). Item 29 remains OPEN and records both the one-comparison remedy and why it was withheld without a reason-sensitive oracle (`docs/superpowers/plans/2026-07-27-0150-backlog.md:1837`, `docs/superpowers/plans/2026-07-27-0150-backlog.md:1853`, `docs/superpowers/plans/2026-07-27-0150-backlog.md:1858`).

   **PASS**

8. The backlog summary is corrected and explains its earlier staleness (`docs/superpowers/plans/2026-07-27-0150-backlog.md:11`, `docs/superpowers/plans/2026-07-27-0150-backlog.md:25`). Item 26 is explicitly PARTIALLY CLOSED (`docs/superpowers/plans/2026-07-27-0150-backlog.md:1575`, `docs/superpowers/plans/2026-07-27-0150-backlog.md:1681`), and its earlier UNMEASURABLE write residual is stated as removed (`docs/superpowers/plans/2026-07-27-0150-backlog.md:1703`, `docs/superpowers/plans/2026-07-27-0150-backlog.md:1707`).

   The limits are nevertheless incomplete because the plan calls a timed test synchronous and says the write “provably” follows death (`docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:792`, `evals/multi-model-verify/test_kimi_lane_lock.py:1297`); the operative contract still asserts harness-owner resolution despite the admitted unlisted-wrapper class (`skills/multi-model-verify/references/backup-lane.md:108`, `docs/superpowers/plans/2026-07-27-0150-backlog.md:1688`); and the branch does not admit the residual race between its LIVE measurement and the subsequent HELD write (`tools/kimi-lane-lock.ps1:638`, `tools/kimi-lane-lock.ps1:648`).

   **FIX — correct the synchronization claim, narrow the operative wrapper contract, and record the non-atomic check-to-write residual.**

UNVERIFIED

- The reported `1089 passed / 14 skipped` Python gate and seven PowerShell-facing modules were not independently run: no `python`, `py`, `python3`, or `pytest` executable was available. These are required verification surfaces under `CLAUDE.md:5` and `CLAUDE.md:17`.
- The narrated watched-failing contention and zero-length mutations remain unverified here (`docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:792`, `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:797`).
- The reported schema mutation results remain unverified here (`docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:834`, `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:836`).

