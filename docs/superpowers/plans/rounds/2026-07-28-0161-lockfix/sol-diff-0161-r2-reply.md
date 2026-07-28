FIX.

One blocking scope gap remains.

- The Windows job uses valid interpreter names. `windows-latest` currently maps to Windows Server 2025; Windows PowerShell 5.1 is installed by default on supported Windows Server versions, and the runner image includes PowerShell 7.6.3. `powershell.exe` and `pwsh.exe` are therefore correct. [GitHub runner images](https://github.com/actions/runner-images), [Microsoft PowerShell 5.1 documentation](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_windows_powershell_5.1?view=powershell-5.1)
- Either pytest failure fails the job. There is no `continue-on-error`, and GitHub propagates native exit codes from PowerShell steps. [GitHub workflow syntax](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#exit-codes-and-error-action-preference)
- But the job does not run all dual-host PowerShell tests as claimed at [skill-evals.yml:46](/C:/Users/Brandon/Documents/parallax/.github/workflows/skill-evals.yml:46). It runs only the lock module at lines 73 and 78.
- [test_attestation.py:10](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_attestation.py:10) also explicitly supports both hosts, but independently hard-selects `powershell` first at [line 27](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_attestation.py:27) and ignores `PARALLAX_PS_HOST`. It therefore remains without gated 5.1 CI coverage. The same fact means `pytest evals` selected solely through `PARALLAX_PS_HOST` does not place every PowerShell-facing test under the named host.

Minimum correction: make `test_attestation.py` honor the selector and include both dual-host test modules in both Windows steps. Also update the now-false “CI has pwsh only” comment at [test_kimi_lane_lock.py:40](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_kimi_lane_lock.py:40).

Claim disposition:

- R1: PASS. The exact committed function returned exactly one non-NaN `double` for 34 root/type/extrema/future cases on each host. Valid `DateTimeOffset` values need no conversion guard; even Min/Max subtraction is representable. DateTime conversion failures return the sentinel.
- R2: FIX. Interpreter availability, names, and failure propagation are correct; coverage scope is incomplete.
- R3: PASS. The string path retains invariant-culture `DateTimeOffset.TryParse` [kimi-lane-lock.ps1:152](/C:/Users/Brandon/Documents/parallax/tools/kimi-lane-lock.ps1:152), followed by the single computation and future guard [line 161](/C:/Users/Brandon/Documents/parallax/tools/kimi-lane-lock.ps1:161). No behavioral regression found.
- R4: Core history PASS; verification scope FIX. The shipped failure and review miss remain bluntly recorded [checkpoint:24](/C:/Users/Brandon/Documents/parallax/.git/parallax/application-checkpoints/2026-07-28-1000-0161-lockfix.md:24), and the reopened wedge is explicit [checkpoint:69](/C:/Users/Brandon/Documents/parallax/.git/parallax/application-checkpoints/2026-07-28-1000-0161-lockfix.md:69). However, the full-suite host labels at lines 82–83 overstate what `PARALLAX_PS_HOST` controls unless the runs used additional PATH isolation.

Verification boundary: exact-function probes and range/`diff --check` were run; pytest, static gates, and branch CI remain unverified from this seat.