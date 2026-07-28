FIX.

R2 remains false as written; R1, R3, and R4 pass.

### R2 — FIX

Distinct session IDs are necessary but not sufficient. Each concurrent invocation must also have distinct transcript and `--output-last-message` paths.

The transport explicitly redirects stdout and writes the reply to caller-chosen files ([SKILL.md](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:124)). The existing freshness rule prevents serial stale-reply reuse, but “fresh round-numbered” does not guarantee uniqueness across two simultaneous debates ([SKILL.md](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/SKILL.md:137)).

Concrete counterexample: two distinct sessions both use `reply-r1.md` and `transcript-r1.txt`. Their writers can fail, truncate, or overwrite one another, potentially pairing one session’s header with another session’s reply. The three-call probe only proves the distinct-path arrangement it exercised.

Required amendment to [model-prompting-notes.md](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/model-prompting-notes.md:200):

> Safe across distinct session IDs when every invocation also has distinct transcript and reply paths; never resume one session concurrently.

Also narrow “nothing shared is parsed” to “no shared global output log is parsed for route attribution.” Codex still shares auth, configuration, session storage, and quota. None of that requires a lane lock under the corrected boundary. “Same session unsafe” remains the right conservative line.

### R1 — PASS, with an inventory correction

Both genuinely dual-host modules honor `PARALLAX_PS_HOST` ([attestation selector](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_attestation.py:28), [lock selector](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_kimi_lane_lock.py:34)), and the workflow runs both modules under both names ([skill-evals.yml](/C:/Users/Brandon/Documents/parallax/.github/workflows/skill-evals.yml:70)).

`windows-latest` currently maps to Windows Server 2025, whose image includes PowerShell 7; Microsoft identifies the side-by-side executables as `powershell.exe` and `pwsh.exe`. [GitHub runner inventory](https://github.com/actions/runner-images/blob/main/images/windows/Windows2025-VS2026-Readme.md), [Microsoft PowerShell migration documentation](https://learn.microsoft.com/en-us/powershell/scripting/whats-new/migrating-from-windows-powershell-51-to-powershell-7).

Neither step uses `continue-on-error`; a nonzero pytest exit fails the check. If the first step fails, the second is skipped under GitHub’s default `success()` condition, but the job still fails. [GitHub status-check documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/expressions).

The hook exemption is correct: production and tests both explicitly use `pwsh` ([hooks.json](/C:/Users/Brandon/Documents/parallax/hooks/hooks.json:10), [test_multi_model_verify.py](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_multi_model_verify.py:1294)).

There is a fourth PowerShell-facing surface: the opt-in drift state-machine test invokes `powershell.exe` ([test_multi_model_verify.py](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_multi_model_verify.py:1952)). That is also intentionally host-specific: the production scheduled task hard-pins `powershell.exe` ([check-drift.ps1](/C:/Users/Brandon/Documents/parallax/tools/check-drift.ps1:94)), and the README states the PS7-hook/PS5-drift split ([README.md](/C:/Users/Brandon/Documents/parallax/README.md:218)). No dual-host test change is needed.

### R3 — PASS

This range changes no production PowerShell implementation. The executable selector is the only functional Python change; the remaining changes are CI coverage and documentation. The selector feeds the same subprocess path as before. `git diff --check f527301..11f28ce` is clean, and the worktree is clean.

### R4 — PASS

The checkpoint now distinguishes the historically mislabeled 284-test runs from the valid 76-test dual-host runs ([checkpoint](/C:/Users/Brandon/Documents/parallax/.git/parallax/application-checkpoints/2026-07-28-1000-0161-lockfix.md:78)).

The 76 count reconciles statically: 48 collected lock cases after parametrization plus 28 attestation cases. The record explicitly says why the earlier 284 labels overstated coverage, attributes independent CI only to `f527301`, and leaves current-branch CI pending. No number is presently labeled as a run that did not happen.

Verification boundary: Python was unavailable from this seat, so I did not independently rerun pytest. The reported test and prior-CI results remain execution evidence supplied by you; my confirmation is static.