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
- `python evals/tools/check_exact_line_oracles.py`
- `python evals/tools/run_trigger_evals.py`
- `python -m pytest evals -q`
- `python evals/tools/backlog_lint.py`
CI runs all six on every push (.github/workflows/skill-evals.yml), as tiers
1, 1b, 1c, 2, 2b and 2c of the `skill-evals` job; tier 2d runs the same
governed-range test as the pre-push hook, on main pushes and pull requests.

A SECOND job, `powershell-hosts`, re-runs every PowerShell-facing test
module under BOTH Windows PowerShell 5.1 and PowerShell 7. A green suite
on one host proves ONE interpreter: 0.16.0 shipped a lane lock that did
not lock on PowerShell 7 at all, and the Linux job only caught it after
release. Locally the suite picks whichever host it finds first, so set
`$env:PARALLAX_PS_HOST` to test the other one.

Tier 1c is a mechanical sweep for one defect class, not a proof: it flags
the "discard blank lines, then assert exactly one survivor" idiom, which
accepts a reply the frozen contract must reject. Three hand sweeps each
missed an instance. Write new single-line parsers through
`accept_exactly_one_nonempty_line()` in `evals/tools/exact_line.py`.

Three suites are local-only and opt-in, so run them by hand when you touch
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
- backup-lane credential or lock changes -> set `PARALLAX_LANE_LIVE=1`
  and `PARALLAX_LANE_LIVE_HOME_{A,B,C}` to the three provisioned lane
  homes, then `python -m pytest evals -q`. Windows only. It drives the
  REAL kimi-code client. Unset, the module skips; once opted in, EVERY
  setup failure FAILS the gate instead of skipping it, because a skipped
  credential measurement is not a clean one.

## Long-running commands

DISPATCH DEBATE ROUNDS AND FULL GATES IN THE BACKGROUND, from the FIRST
attempt. The reason is VISIBILITY, not survival, and the difference
matters because the reason written here before was false. A foreground
call OWNS the session: while it runs, nobody can see the round, talk to
the agent, or redirect it. A backgrounded call leaves the session
answering, which is the property measured in
`docs/superpowers/plans/rounds/2026-08-31-completion-coupled-dispatch/benefit-measurement.md`.

THE 600-SECOND CEILING DOES NOT KILL. Measured 2026-09-01 on Claude Code
2.1.251: a foreground call that ran past it was MOVED to the background
by the harness under a new task id and completed with exit 0. The
measured case was a local filesystem command rather than a codex round,
so what it establishes is narrow and stated narrowly - the ceiling is not
a kill. The text here previously said a crossing round is killed with the
quota spent for nothing, and cited "measured repeatedly through 0.21.x";
that claim is withdrawn, and this rule no longer rests on it.

Two traps in the dispatch scripts themselves, both measured 2026-08-04:

- Do NOT run the native `codex` call under
  `$ErrorActionPreference = 'Stop'`. codex prints a benign models-cache
  warning to stderr at startup, and Stop promotes ANY native stderr line
  to a terminating `NativeCommandError`, killing the dispatch before the
  reviewer does any work. Drop to `Continue` around the native call and
  check `$LASTEXITCODE` yourself; nothing is being ignored, only the
  stderr channel is stopped from masquerading as a failure.
- Do NOT pipe an expensive run's output through `tail`, `head` or
  `Select-Object -Last`. The failure NAMES are what a second run needs,
  and truncating them costs the whole run again.
- The brief must be read as STRICT UTF-8 and `$OutputEncoding` set to
  UTF-8 at SCRIPT scope before the pipe, restored in `finally`. Measured
  2026-08-11: Windows PowerShell 5.1 reads a no-BOM file with the ANSI
  code page AND defaults `$OutputEncoding` to us-ascii, so one em dash
  reaches the reviewer as THREE question marks and it answers a brief you
  never sent. `Get-Content -Raw | codex exec` is the defective form. A
  `& { }` block does NOT work: the native pipe reads the OUTER scope, so
  a child-scope assignment is scoped and inert. Only the round-evidence
  binding catches the corruption, and it costs the whole round.
  0.23.0 fixed the SKILL.md dispatch ONLY. `tools/check-drift.ps1:1060`
  still ships the defective form, with no brief binding to catch it, and
  `commands/doctor.md:70` has the same shape on a pure-ASCII payload.
  Both are named in the finding write-up under
  `docs/superpowers/plans/rounds/2026-08-11-budget-flake-generator/`;
  do not read the rule above as a statement that the repo is clean.

**The dispatch is no longer a copied snippet, and the tool no longer
starts anything.** `tools/dispatch-round.ps1` has two modes, and every
lane calls it rather than writing its own.

`-Prepare` builds the round as one fail-closed transaction: verify the
working directory IS the named review mirror, resolve the host, hash the
prior state, reserve the dispatch directory, install the lane's body and
the wrapper around it, and write the receipt last of all. It then PRINTS
the exact command line and the task name, and starts NO process. The
caller dispatches that command as a harness background command.

`-Classify` is the wrapper's own final act, and this is the sentence that
carries the design: THE WRAPPER'S EXIT CODE IS THE CLASSIFICATION. `0`
means `reply-present` and nothing else; `2` is a parameter-binding or
internal failure; `1` is every other state, named on the wrapper's last
stdout line. A wrapper that does not reach its final statement cannot
report success, whatever its directory holds. Measured 2026-09-01: a
round killed after publishing a zero exit file AND a non-empty reply
reported `[killed]`, and left a reservation no later caller could redeem.
Never re-read the dispatch directory to decide a verdict.

Written here as a plain repo-relative path: `CLAUDE.md` is neither skill
body, where the harness substitutes `${CLAUDE_PLUGIN_ROOT}`, nor a lane's
command literal, where `references/backup-lane.md` carries a
session-filled `<plugin-checkout>` placeholder instead. The full contract
lives in five regions in
`skills/multi-model-verify/references/model-prompting-notes.md`:
`round-dispatch-tool`, `round-dispatch-states`,
`round-dispatch-exit-map`, `round-dispatch-operation`, and
`background-task-naming`.

Name every backgrounded call for the person watching it. A reviewer round
leads with its LANE and ROUND, as in `Astra R1 debate round` or
`Kimi R2 debate round`. A gate or a mirror build has no lane, so it leads
with its KIND instead, as in `Gate: pytest 5.1` or `Mirror build`.
`-Prepare` now PRINTS the name, so the convention has a source; nothing
enforces its use.

**DO NOT TOUCH THE REVIEWED TREE BETWEEN `-Prepare` AND THE WRAPPER'S
EXIT.** The wrapper verifies the mirror's identity after the round runs,
and the source fingerprint is built from what `git status` names, so a new
UNTRACKED file is enough to fail it. The round then classifies as `1`, its
reply is not evidence, and the quota is spent for nothing. Measured
2026-09-04: writing six documentation files into the repo mid-round voided
a completed cross-vendor round, and the remedy cost a second dispatch, so
the price was two rounds. The gate is in `tools/dispatch-round.ps1`; NO
prose rule in `skills/` carries it, which is why it is written here. Queue
edits until the wrapper exits, however small and however unrelated they
look.

**WRITE EVERY BRIEF TO DISK BEFORE SENDING IT**, both lanes, outside the
reviewed tree. The codex lane gets this free, because the dispatch pipes a
file. The same-harness lane does NOT: a brief sent as an agent message
leaves no artifact, and it cannot be retained afterwards. Measured in the
same debate: seven of that lane's briefs are permanently unrecoverable, so
the record can show what one lane was asked and not the other. A scratchpad
file costs nothing and the closing commit retains it.

## Dev loop
The plugin is installed user-scope from a LOCAL marketplace pointing at
this working copy, but installs are VERSIONED CACHE COPIES — checkout
edits are NOT live until you: bump `.claude-plugin/plugin.json`, run
`claude plugin marketplace update parallax`, THEN
`claude plugin update parallax@parallax` (qualified name required),
and restart the session when hooks/ or skills/ changed. A restart alone
only reloads the cached version. The marketplace refresh is load-bearing:
the directory-source catalog is read at session start, so with it skipped
the update sees the OLD version and silently does nothing — measured
2026-08-17, the same command copied nothing before the refresh and
installed 0.26.1 after it. GitHub remote (Bmwascher/parallax, public)
serves stable installs on other machines.

BUMP THE VERSION AFTER THE DIFF DEBATE, not when the branch's first task
touches it and not merely as the last BUILD task. `plugin update` keys
ONLY on the version string: once a version has been cached, the same
number reports "already at the latest version" and copies NOTHING,
however much the checkout changed afterwards. Measured 2026-08-03: 0.20.0
was bumped mid-branch, cached at 14:13, and then five diff-debate rounds
rewrote `skills/`. Measured again 2026-08-16: 0.26.0 bumped LAST in the
build, exactly as this rule then read, and six debate rounds still moved
the tree after the bump was cached — the installed copy was five commits
stale and missing fixes the release existed to ship. The debate is what
moves the tree after the final build task, so "last" means after it; a
bump consumed before the branch is finished recovers only by another bump
(that is what 0.26.1 is).

VERIFY THE INSTALL BY CONTENT, never by the cache directory's name: a
directory named `0.26.0` held code from five commits before the shipped
head. The cheap check is `gitCommitSha` in
`~/.claude/plugins/installed_plugins.json`, which records exactly which
commit was copied; the thorough one is hashing the cached files against
the checkout with CRLF normalized. Backlog item 65 holds the full record
and the open question of a mechanical check.

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

The backup lane's credential handling is a live-verified contract locked
by `evals/multi-model-verify/test_kimi_lane_home.py`,
`test_kimi_lane_login.py`, `test_kimi_lane_lock.py` and
`test_kimi_credential_state.py`. A debate home reaches the one credential
through a directory JUNCTION and must never hold a COPY: the access token
lives 900 seconds and a refresh rotates BOTH tokens, so a copy that
refreshes retires the original. Change the tests first.

The same builder asserts, as a POSTCONDITION on its own act, that the
`skills/` directory it just created is empty. That is NOT a per-round
control and must not be described as one: nothing re-checks it at
dispatch, and every writer into that directory sits in the builder
itself - the `New-Item` that creates it, and the two seams below it. Its
cases are in `test_kimi_lane_home.py`. Those two seams are builder
contract rather than test scaffolding. They are gated on environment
variables, so any parent process can set them; no shipped caller does,
and either one can only force the build to FAIL, never turn a failing
build into a successful one.

A pin that matches the RAW file text needs its phrase unbroken on ONE
PHYSICAL LINE; a pin built on the whitespace-normalized read does not.
Both forms are in use, in the same test file, and nothing marks which is
which. So REFLOWING A PARAGRAPH CAN TURN A PIN RED WITHOUT CHANGING A
WORD, and the failure names the pin rather than the wrap. Measured
2026-08-19: one task was blocked twice on this, once when an edit made a
pinned clause sentence-initial (the pins are case-sensitive) and once when
the rewrap split the phrase across lines. Check which read a pin uses
before editing near it, and prefer restructuring the prose to keep an
existing pin green over editing the pin to fit new prose.

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
