# crosscheck — Claude Code plugin (NOT a WoW addon)

This repo is developer tooling: a Claude Code plugin providing cross-model
verification (Fable 5 / GPT-5.6 Sol debates) plus its eval harness. It lives
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

## Dev loop
The plugin is installed from this working copy via a LOCAL marketplace, so
edits are live after `/plugin` update or session restart — plus the GitHub
remote (Bmwascher/crosscheck, private) for stable installs on other
machines. Bump `.claude-plugin/plugin.json` version on user-visible changes.

## Skill editing rules
The multi-model-verify skill's transport commands (codex exec flags, resume
syntax) are LIVE-VERIFIED contracts locked by evals/multi-model-verify/
test_multi_model_verify.py — change the tests first (they encode review
findings), then the skill.
