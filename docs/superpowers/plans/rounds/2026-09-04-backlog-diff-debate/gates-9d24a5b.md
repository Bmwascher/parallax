# Gates for the backlog rewrite, terminal head 9d24a5ba2d0c201585a3dbfb7b2a8a1ca3e783c0

Run on 2026-09-04 on the author's Windows machine. Every line is the
command's own last result line, untruncated where a count is the point.

## At 9d24a5b (the head Sol R4 passed)

| gate | result |
|---|---|
| `python evals/tools/skill_lint.py skills/multi-model-verify --strict` | PASS, 0 error(s), 2 warning(s) (SKILL.md body 414 lines / ~6456 tokens, both pre-existing) |
| `python evals/tools/skill_scanner.py skills` | 0 CRITICAL, 0 WARN, 0 INFO |
| `python evals/tools/check_exact_line_oracles.py` | exit 0 |
| `python evals/tools/run_trigger_evals.py` | trigger & routing: all clear (1 skill) |
| `python evals/tools/backlog_lint.py` | backlog lint: clean |
| `python evals/tools/backlog_lint.py --range 0ecc7c7..HEAD` | range 0ecc7c7..HEAD: clean (governed paths changed; 51 items re-attested) |
| pytest `test_backlog_lint.py test_backlog_hooks.py test_backlog_prepush.py`, host pwsh 7 | 127 passed in 52.83s |
| pytest `test_backlog_hooks.py`, host Windows PowerShell 5.1 | 25 passed in 22.22s |

## Full suite

| head | result |
|---|---|
| a6c4431 (`python -m pytest evals -q`) | 2847 passed, 14 skipped in 1496.87s (0:24:56) |

The full suite was not re-run at 9d24a5b. `git diff --stat a6c4431..9d24a5b`
is five files: BACKLOG.md (item 85's text and digest) and four files
under this record directory (the debate record, the round-3 brief, reply
and receipt). No Python, PowerShell, hook, workflow or skill file
changed, and the one module that reads BACKLOG.md (`test_real_backlog_passes`
in the backlog lint module) was re-run at 9d24a5b in the table above.

## Earlier heads on the debate

| head | what ran | result |
|---|---|---|
| 196f3e5 (build end) | full suite | 2837 passed, 14 skipped (ledger) |
| 24ab582 (round-1 fixes) | three backlog modules, pwsh | 127 passed in 66.97s |
| 24ab582 | hook module, 5.1 | 25 passed in 29.88s |
| 24ab582 | full suite | started, then stopped by the session once a6c4431 superseded it; no result |
| a6c4431 (round-2 fixes) | three backlog modules, pwsh | 127 passed |
| a6c4431 | hook module, 5.1 | 25 passed in 28.76s |
| a6c4431 | attestation and behavioral-eval pins (`-k "behavioral or changed or attestation"`) | 6 passed, 169 deselected |
