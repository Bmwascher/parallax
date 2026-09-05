# Gate results at 34de155 (branch mirror-link-relink), 2026-09-05

| gate | result |
|---|---|
| tiers 1, 1b, 1c, 2, 2b, 2c (`skill_lint --strict`, `skill_scanner`, `check_exact_line_oracles`, `run_trigger_evals`, `backlog_lint`) | exit 0 |
| `python -m pytest evals -q` under Windows PowerShell 5.1 (`PARALLAX_PS_HOST=powershell`) | 2880 passed, 14 skipped in 1394 s, exit 0 |
| `python -m pytest evals -q` under PowerShell 7 (`PARALLAX_PS_HOST=pwsh`) | 2879 passed, 15 skipped in 1360 s, exit 0 |
| `python evals/tools/run_behavioral_evals.py --head --changed` | exit 0; SELECTED `backup-lane-consented-substitution` (skills/multi-model-verify/references/backup-lane.md), SKIPPED(manual); every other case SKIPPED(unchanged surface); zero cases ran, recorded as a coverage measurement and not as a pass |

The one-test difference between hosts is the module's host-specific skips (the relative-symlink case needs a privilege the session lacks under one host's fixture path).

# Gate results at 0f872e0 (after the round 1 fix), 2026-09-05

| gate | result |
|---|---|
| tiers 1, 1b, 1c, 2, 2b, 2c | exit 0 |
| `python -m pytest evals -q` under Windows PowerShell 5.1 | 2881 passed, 14 skipped, exit 0 |
| `python -m pytest evals -q` under PowerShell 7 | 2880 passed, 15 skipped, exit 0 |

The two full suites ran concurrently in one checkout. The one new case on each host is `test_a_link_target_that_cannot_be_resolved_blocks_the_manifest`, red before 0f872e0 and green after.
