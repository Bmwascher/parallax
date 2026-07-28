FIX.

1. Important — `DateTime` extrema can still throw. The direct cast at [kimi-lane-lock.ps1:125](/C:/Users/Brandon/Documents/parallax/tools/kimi-lane-lock.ps1:125) throws for `DateTime.MaxValue` with `Kind=Local` or `Unspecified` in this UTC−06 zone, before the negative-age guard at line 130. The symmetric `MinValue` failure exists in positive-offset zones. Both installed hosts reproduced the throw in the exact committed function. Conversion failures must return `MaxValue`; add extrema regressions.

2. Important — dual-host execution is optional, not gated. `PARALLAX_PS_HOST` makes both hosts selectable, but nothing invokes both automatically [test_kimi_lane_lock.py:34](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_kimi_lane_lock.py:34). CI remains one Ubuntu/pwsh run [skill-evals.yml:15](/C:/Users/Brandon/Documents/parallax/.github/workflows/skill-evals.yml:15). A future 5.1-only regression can therefore ship. Add a Windows CI job or deterministic wrapper that runs the lock tests once under `powershell.exe` and once under `pwsh.exe`.

Claim disposition:

- R1: FIX. Valid `DateTimeOffset` extrema subtract safely; future DTO and UTC `DateTime` values reach the negative-age guard. Local/Unspecified extrema can throw. An ambiguous offsetless DST time also has no uniquely “right instant”; the cast chooses a local offset, matching the string path, but the comment overstates this.
- R2: PASS. Object, array, number and null cannot satisfy either new strict `-is` branch and still return unusable [kimi-lane-lock.ps1:120](/C:/Users/Brandon/Documents/parallax/tools/kimi-lane-lock.ps1:120). Direct probes on both hosts confirmed this.
- R3: FIX. The exact pwsh defect now has a good regression assertion [test_kimi_lane_lock.py:394](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_kimi_lane_lock.py:394), but supported-host coverage is not mechanically enforced.
- R4: FIX. The release/review failure account is candid and consistent with the local commit history. However, the checkpoint overstates all `DateTime` conversions as correct [lockfix checkpoint:40](/C:/Users/Brandon/Documents/parallax/.git/parallax/application-checkpoints/2026-07-28-1000-0161-lockfix.md:40), and it contains only a verification plan—not the reported 281/1 and 45-test results [lockfix checkpoint:44](/C:/Users/Brandon/Documents/parallax/.git/parallax/application-checkpoints/2026-07-28-1000-0161-lockfix.md:44).

Verification boundary: I did not rerun pytest or CI. I did run the exact committed age function in memory under Windows PowerShell 5.1 and pwsh 7.6.3, and rechecked the exact range plus `git diff --check`.

