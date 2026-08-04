Judged HEAD: `6565ca0d2cbcd81cc982eb9c6b51b221980ac662`.

Not terminal: claims 1, 2 and 8 still need fixes. Claims 3–7 pass.

1. The oracle is now genuinely synchronized: it supplies the contention-signal path, waits for an exact `"holder"` result, then kills and reaps the proposed owner before releasing the holder (`evals/multi-model-verify/test_kimi_lane_lock.py:1296`, `evals/multi-model-verify/test_kimi_lane_lock.py:1303`, `evals/multi-model-verify/test_kimi_lane_lock.py:1305`, `evals/multi-model-verify/test_kimi_lane_lock.py:1310`). The `"holder"` signal is emitted only after the waiter has entered the holder-contention branch (`tools/kimi-lane-lock.ps1:708`, `tools/kimi-lane-lock.ps1:714`). Amendment 2’s false synchronization statement is visibly corrected rather than erased (`docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:792`, `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:795`).

   Three defects remain:

   - The old guarantee survives inside `Invoke-AcquireMode`: it still says the helper runs before “every record write” and “requires LIVE” (`tools/kimi-lane-lock.ps1:596`, `tools/kimi-lane-lock.ps1:603`). Amendment 2 likewise still says “EVERY RECORD WRITE” without an adjacent correction pointer (`docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:783`, `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:790`). These contradict the corrected HELD-owner wording at `tools/kimi-lane-lock.ps1:535-546` and Amendment 3’s claim that the guarantee “is now” narrowed (`docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:934`, `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:936`).
   - The residual’s duration is asserted as “microseconds” without measurement (`tools/kimi-lane-lock.ps1:540`, `tools/kimi-lane-lock.ps1:545`, `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:937`, `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:940`). Scheduling can pause the process between measurement and write, so the wall-clock duration is not bounded by the number of intervening operations.
   - If waiting for the signal times out or the branch assertion fails, execution never reaches `victim.kill()` (`evals/multi-model-verify/test_kimi_lane_lock.py:1305`, `evals/multi-model-verify/test_kimi_lane_lock.py:1310`), while the `finally` block terminates only the waiter (`evals/multi-model-verify/test_kimi_lane_lock.py:1317`, `evals/multi-model-verify/test_kimi_lane_lock.py:1319`). The 120-second sleeper can therefore escape a failing oracle (`evals/multi-model-verify/test_kimi_lane_lock.py:1292`).

   **FIX — correct the two surviving “every record write/requires LIVE” surfaces, remove the unmeasured duration claim, and kill/reap the victim in `finally`.**

2. The substantive lifecycle description is accurate and its whole-region pin moved with it: it names the four transports, the first non-transport ancestor, the unlisted-wrapper residual and the shell-frame-only evidence (`skills/multi-model-verify/references/backup-lane.md:107`, `skills/multi-model-verify/references/backup-lane.md:116`, `evals/multi-model-verify/test_backup_lane.py:265`, `evals/multi-model-verify/test_backup_lane.py:276`).

   The known-owner exception is immediately contradicted by the next instruction. It says a caller that knows its session identity should pass it “instead of resolving one,” then says “So run `-ResolveOwner` once” (`skills/multi-model-verify/references/backup-lane.md:117`, `skills/multi-model-verify/references/backup-lane.md:120`). The exact pin preserves the same unconditional transition (`evals/multi-model-verify/test_backup_lane.py:277`, `evals/multi-model-verify/test_backup_lane.py:280`).

   **FIX — change “So run” to “Otherwise, run” and regenerate the whole-region pin.**

3. Amendment 2 now correctly says all seven non-name fixtures carry a valid name and identifies the extra-field fixture as the seventh (`docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:831`, `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:836`). That agrees with the seven parametrized fixtures (`evals/multi-model-verify/test_kimi_lane_home.py:1866`, `evals/multi-model-verify/test_kimi_lane_home.py:1872`).

   **PASS**

4. The prose now says a file link can measure a filesystem object outside the debate home (`commands/doctor.md:251`, `commands/doctor.md:254`), and the exact pin carries the same statement (`evals/multi-model-verify/test_backup_lane.py:1622`, `evals/multi-model-verify/test_backup_lane.py:1629`).

   **PASS**

5. The reason-sensitive pin now covers agreement, application of amendments and termination only through an adjudicated dry round (`evals/multi-model-verify/test_multi_model_verify.py:829`, `evals/multi-model-verify/test_multi_model_verify.py:850`). It matches the protocol text (`skills/multi-model-verify/references/debate-protocol.md:48`, `skills/multi-model-verify/references/debate-protocol.md:56`).

   The phrase-only neighbour may remain. It is redundant but no longer bears the semantic burden: it checks label presence (`evals/multi-model-verify/test_multi_model_verify.py:776`, `evals/multi-model-verify/test_multi_model_verify.py:781`), while Amendment 3 explicitly identifies that limitation (`docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:909`, `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:916`).

   **PASS**

6. Neither retained record changed. The index continues to identify the six claims requiring fixes (`docs/superpowers/plans/rounds/2026-08-04-transport-and-mirror/README.md:15`), matching the reply’s first line (`docs/superpowers/plans/rounds/2026-08-04-transport-and-mirror/plan-reply-r1b.md:1`).

   **PASS**

7. Owner resolution still names the missing creation-order guard and its PID-reuse consequence (`tools/kimi-lane-lock.ps1:908`, `tools/kimi-lane-lock.ps1:917`). The current commit changed acquire commentary and tests, not that disposition; item 29 remains the filed residual (`docs/superpowers/plans/2026-07-27-0150-backlog.md:1837`, `docs/superpowers/plans/2026-07-27-0150-backlog.md:1853`).

   **PASS**

8. Amendment 3 does record the unsynchronized oracle, missing pin, wrapper overclaim, HELD-owner distinction, check-to-write residual and corrected fixture count (`docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:885`, `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:947`). Item 26 remains explicitly PARTIALLY CLOSED (`docs/superpowers/plans/2026-07-27-0150-backlog.md:1681`, `docs/superpowers/plans/2026-07-27-0150-backlog.md:1693`).

   The stated limits are not internally complete while operative source still asserts the superseded every-record guarantee (`tools/kimi-lane-lock.ps1:596`, `tools/kimi-lane-lock.ps1:603`) and the residual is assigned an unmeasured “microseconds” duration (`tools/kimi-lane-lock.ps1:540`, `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:939`). The lifecycle exception is also ambiguous because its unconditional resolver instruction follows immediately afterward (`skills/multi-model-verify/references/backup-lane.md:117`, `skills/multi-model-verify/references/backup-lane.md:120`).

   **FIX — reconcile the surviving source/plan wording, remove the unsupported timing magnitude, and make the known-owner exception operationally unambiguous.**

UNVERIFIED

- The reported `1090 passed / 14 skipped` suite and seven-module second-host gate were not run here because `python`, `py`, `python3` and `pytest` remain unavailable.
- The reported mutation that removes the fresh-acquire guard is recorded but not independently reproduced (`docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:899`, `docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:902`).
- The convergence-pin mutation was not independently reproduced; only the current exact assertion was inspected (`docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:915`, `evals/multi-model-verify/test_multi_model_verify.py:843`).
- Both changed PowerShell tools parse successfully under the available PowerShell parser, but that is not the reported two-host behavioral gate.

