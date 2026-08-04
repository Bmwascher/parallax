Judged HEAD: `71617056b62ea87fc56a5dd23954a207ce1077b1`.

Not terminal: one claim remains wider than its evidence.

1. The three requested repairs landed:

   - Both source comments now say HELD-owner writes and distinguish free-record writes (`tools/kimi-lane-lock.ps1:535`, `tools/kimi-lane-lock.ps1:537`, `tools/kimi-lane-lock.ps1:599`, `tools/kimi-lane-lock.ps1:601`).
   - Amendment 2 retains its historical wording but immediately marks it too wide and points to Amendment 4 (`docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:783`, `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:787`).
   - The victim is killed and waited in `finally` when a signal timeout or branch assertion bypasses the success-path kill (`evals/multi-model-verify/test_kimi_lane_lock.py:1305`, `evals/multi-model-verify/test_kimi_lane_lock.py:1317`, `evals/multi-model-verify/test_kimi_lane_lock.py:1323`).

   The replacement timing comparison is still too wide. The source calls the new race “far NARROWER” and says the old race “spanned the whole wait budget” (`tools/kimi-lane-lock.ps1:543`, `tools/kimi-lane-lock.ps1:545`); Amendment 4 repeats that comparison (`docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:992`, `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:994`). A successful acquisition need not wait the whole budget, and the acknowledged scheduler pause means the new temporal window is not proven “far narrower.” What is statically established is only that the check moved after the acquisition loop and the remaining source interval contains record preparation and serialization (`tools/kimi-lane-lock.ps1:559`, `tools/kimi-lane-lock.ps1:650`, `tools/kimi-lane-lock.ps1:660`).

   **FIX — say the old interval could include contention waiting up to the budget, while the new source interval contains only record preparation and serialization; do not claim a comparative wall-clock magnitude.**

2. The exception is now operationally unambiguous: callers knowing their session identity pass it directly; otherwise they resolve one (`skills/multi-model-verify/references/backup-lane.md:117`, `skills/multi-model-verify/references/backup-lane.md:120`). The whole-region pin carries the same conditional instruction (`evals/multi-model-verify/test_backup_lane.py:277`, `evals/multi-model-verify/test_backup_lane.py:281`).

   **PASS**

3. The seven-fixture correction remains intact in Amendment 2 (`docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:831`, `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:836`) and the parametrization still contains all seven non-name cases (`evals/multi-model-verify/test_kimi_lane_home.py:1866`, `evals/multi-model-verify/test_kimi_lane_home.py:1872`).

   **PASS**

4. The file-link wording remains corrected in both the doctor prose and its pin (`commands/doctor.md:253`, `evals/multi-model-verify/test_backup_lane.py:1626`).

   **PASS**

5. The agreement-not-termination clause and its reason-sensitive exact pin remain aligned (`skills/multi-model-verify/references/debate-protocol.md:52`, `skills/multi-model-verify/references/debate-protocol.md:56`, `evals/multi-model-verify/test_multi_model_verify.py:845`, `evals/multi-model-verify/test_multi_model_verify.py:850`).

   **PASS**

6. The retained round index still matches the reply’s own verdict (`docs/superpowers/plans/rounds/2026-08-04-transport-and-mirror/README.md:15`, `docs/superpowers/plans/rounds/2026-08-04-transport-and-mirror/plan-reply-r1b.md:1`).

   **PASS**

7. The ancestry PID-reuse residual remains named and item 29 remains open (`tools/kimi-lane-lock.ps1:912`, `tools/kimi-lane-lock.ps1:921`, `docs/superpowers/plans/2026-07-27-0150-backlog.md:1837`).

   **PASS**

8. Amendment 4 accurately records the surviving surfaces, unmeasured magnitude and fixture cleanup defect (`docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:972`, `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:1008`). Item 26 remains PARTIALLY CLOSED (`docs/superpowers/plans/2026-07-27-0150-backlog.md:1575`, `docs/superpowers/plans/2026-07-27-0150-backlog.md:1681`).

   Its replacement limit nevertheless contains the unsupported comparison identified in claim 1 (`docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:992`, `tools/kimi-lane-lock.ps1:543`).

   **FIX — narrow the comparison to control-flow placement and explicitly leave comparative wall-clock duration unmeasured.**

UNVERIFIED

- The reported full suite and seven-module second-PowerShell-host gate were not independently run; Python remains unavailable in this environment.
- Both PowerShell tools parse successfully with the available PowerShell parser, but that is not the reported two-host behavioral gate.

