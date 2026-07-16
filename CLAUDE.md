# parallax — Claude Code plugin (NOT a WoW addon)

This repo is developer tooling: a Claude Code plugin providing cross-model
verification (session ⇄ cross-vendor reviewer debates; the reviewer lane is
declared in the skill's model-prompting-notes.md) plus its eval harness. It lives
under KitnDev for convenience, but the WoW addon family conventions in
`../AGENTS.md` (dev loop, /reload, luacheck/busted, 12.0 API rules,
References/) do NOT apply here — only the git basics do (feature branches
for real work, lowercase imperative commits, no AI attribution).

## Verification
- `python evals/tools/skill_lint.py skills/multi-model-verify --strict`
- `python evals/tools/skill_scanner.py skills`
- `python evals/tools/run_trigger_evals.py`
- `python -m pytest evals -q`
CI runs all four on every push (.github/workflows/skill-evals.yml).

Two suites are local-only and opt-in, so run them by hand when you touch
what they cover:
- skill/prompt changes -> `python evals/tools/run_behavioral_evals.py`
  (real headless runs, graded by the cross-vendor reviewer; `--head` tests
  the checkout instead of the installed cache).
- `tools/check-drift.ps1` changes -> run
  `evals/tools/drift_statemachine_tests.ps1` (or, to go through pytest:
  `$env:PARALLAX_STATEMACHINE = "1"; python -m pytest evals -q` — it is
  PowerShell, so no `VAR=1 cmd` prefix). Drives the real script through its
  whole state machine offline against stub CLIs. Slow: four scenarios
  re-run the full pytest suite inside a disposable worktree.

## Dev loop
The plugin is installed user-scope from a LOCAL marketplace pointing at
this working copy, but installs are VERSIONED CACHE COPIES — checkout
edits are NOT live until you: bump `.claude-plugin/plugin.json`, run
`claude plugin update parallax@parallax` (qualified name required),
and restart the session when hooks/ or skills/ changed. A restart alone
only reloads the cached version. GitHub remote (Bmwascher/parallax,
private) serves stable installs on other machines.

## Skill editing rules
The multi-model-verify skill's transport commands (codex exec flags, resume
syntax) are LIVE-VERIFIED contracts locked by evals/multi-model-verify/
test_multi_model_verify.py — change the tests first (they encode review
findings), then the skill.
