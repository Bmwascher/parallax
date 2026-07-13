# crosscheck

Cross-model verification for Claude Code. Two equal-weight frontier models —
Fable 5 (the session) and GPT-5.6 Sol (via the OpenAI codex CLI on a ChatGPT
subscription) — verify and refute each other's claims with file:line
evidence before a cheaper implementer touches code, and again before the
result merges.

Companion to [superpowers](https://github.com/obra/superpowers), not a
replacement: it fills the cross-model review gap superpowers rules out of
scope. Pattern lineage: the advisor/evals ideas from
[awesome-llm-apps agent_skills](https://github.com/Shubhamsaboo/awesome-llm-apps)
and the plugin shape of
[fable-advisor](https://github.com/DannyMac180/fable-advisor).

## What's in the box

| Piece | What it does |
|---|---|
| `skills/multi-model-verify/` | The debate skill: mode `plan` (before implementation) and mode `diff` (before merge), debate protocol, frozen-plan format, model prompting notes, fallbacks |
| `hooks/` | PostToolUse/Task hook: fingerprints the superpowers code-reviewer dispatch and injects the mode-`diff` reminder with the same base/head SHAs (fails open — inert everywhere else) |
| `evals/` | Deterministic gates for the skill itself: spec lint, security scan, trigger/routing evals, structural pytest (vendored tools — see `evals/tools/LICENSE-THIRD-PARTY.md`) |

## Requirements

- Claude Code with Fable 5 access, superpowers plugin enabled
- OpenAI codex CLI 0.144+ authenticated via ChatGPT sign-in, on a plan with
  GPT-5.6 Sol access (Plus or higher — free tier is Terra-only)
- `pwsh` (PowerShell 7) for the hook; Python 3.10+ for the evals

## Install

Stable (any machine with git auth for this private repo):

```
claude plugin marketplace add Bmwascher/crosscheck
claude plugin install crosscheck@crosscheck
```

Dev loop (this working copy, edits live):

```
claude plugin marketplace add <path-to-this-checkout>
claude plugin install crosscheck@crosscheck
```

## Verify

```
python evals/tools/skill_lint.py skills/multi-model-verify --strict
python evals/tools/skill_scanner.py skills
python evals/tools/run_trigger_evals.py
python -m pytest evals -q
```

All four also run in CI on every push.

## Degraded modes

codex missing/unauthenticated → visibly flagged single-vendor mode (fresh
Fable skeptic subagent). Missing reference material for a port → hard stop,
ask. Details in `skills/multi-model-verify/references/fallbacks.md`.
