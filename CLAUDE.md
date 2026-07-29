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
  the checkout instead of the installed cache; for small contract edits
  `--changed` runs only cases whose declared surface intersects the diff
  vs main, printing every skip by name).
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
public) serves stable installs on other machines.

## Skill editing rules
The multi-model-verify skill's transport commands (codex exec flags, resume
syntax) are LIVE-VERIFIED contracts locked by evals/multi-model-verify/
test_multi_model_verify.py — change the tests first (they encode review
findings), then the skill.

The reviewer's isolation flags (`--disable plugins --disable apps`) and the
context probe's failure directions are live-verified contracts locked by
`evals/multi-model-verify/test_multi_model_verify.py` and
`test_codex_context_probe.py`. Change the tests first. Every failure
direction in the probe lands on BLOCKED; a change that lets an unmade
measurement read as clean is the one outcome these scripts may never
produce.

Contract text inside `contract:start` / `contract:end` HTML comment
markers must sit WHOLE inside a single pin in `evals/multi-model-verify/`.
The checker scans all Markdown under `skills/`, plus `agents/*.md` and
`commands/*.md`.

A pin is a string literal in one of exactly three assertion clause forms:

- `"literal" in body`
- `body.count("literal")`, alone or compared `== n` or `>= n` with n at
  least 1, or `> n` with n at least 0
- an `and`, which contributes every operand it recognizes, so
  `"literal" in body and flag` still pins the literal

The needle must be a plain string literal. Adjacent literals across
several lines are fine, because the parser folds them into one.

The assertion must also be able to FAIL the suite. An assertion whose
failure is deliberately caught proves the opposite of what it looks
like, so it pins nothing: inside a `raises(...)` or `suppress(...)`
block, inside the body of a `try` that has handlers, or in a function
marked xfail. A `try/finally` has no handlers, so its body still pins.

Nothing else counts, and the rule matches a COMPLETE clause rather than
looking for these shapes anywhere in the expression. A string locks
nothing if it sits in a docstring, in an assertion's failure message,
under `not`, in a `not in` comparison, on either side of an `or`, in a
count comparison outside the positive bounds above, such as `== 0` or
`>= 0`, in a plain equality such as `result == "text"`, in a regex such
as `re.search(...)`, in either branch of a conditional, or is reached
through a variable name. Any positive assertion outside the three forms
above is rejected, whatever it means.
In every one of those cases the checker reports the region as unlocked,
which is a red; it never reads as covered.

`test_contract_coverage.py` enforces this and lists any region that is
not locked. A region too long for one pin is two regions. Adding or
removing a marked region also means editing `DECLARED_REGIONS` in that
file, which is what makes deleting a region visible.
