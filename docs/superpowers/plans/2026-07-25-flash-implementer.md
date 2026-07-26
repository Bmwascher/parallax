# Flash Implementer Lane Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `agents/flash-implementer.md`, a haiku-wrapper SDD implementer that delegates all code-writing to Gemini 3.6 Flash via the Antigravity CLI (agy) headlessly, with mechanically enforced route and authorship checks.

**Architecture:** Architecture A from the spec (`docs/superpowers/specs/2026-07-25-flash-implementer-design.md`): a new wrapper agent beside the untouched `implementer.md`. The wrapper never types repo code (tools allowlist without Edit/Write + transcript/tree corroboration); every failure is loud (`STATUS: blocked`); reroute is consent-gated. Model literal single-sourced to the two agent files.

**Tech Stack:** Claude Code agent frontmatter, agy 1.1.7 print mode, pytest (offline contract pins), PowerShell (drift snapshot).

**STATUS: FROZEN — CONVERGED.** Frozen 2026-07-25 by the backup-lane plan debate (Kimi K3-256k, 2 rounds); reopened same day by the primary reviewer's check-off (Sol, codex window reset early) and re-frozen at round 4: r1 FIX (5 blocking), r2 FIX (3 blocking + 2 minor), r3 FIX (4 blocking), r4 terminal PASS — primary check-off GRANTED with one trivial accepted amendment (applied). Every finding session-verified and accepted; amendments folded into spec, this plan, and the artifacts via SDD fix waves. The diff debate gates the merge as always. Tasks 5-6 contain ATTENDED steps (user-interactive); Task 6 additionally requires the plugin dev-loop (bump, update, restart).

## Global Constraints

- The canonical implementer-lane literal is the RESOLVED ID `gemini-3.6-flash-medium`; after this cycle it appears ONLY in `agents/implementer.md` and `agents/flash-implementer.md` (spec section 5).
- The wrapper's tools allowlist is exactly Read, Grep, Glob, Bash — no Edit, no Write, no NotebookEdit (spec section 1).
- Route language is "requested and propagated", never "used and confirmed" (spec section 2; doctor check-4 discipline).
- Loud failure only: any preflight, dispatch, route-check, or corroboration failure is `STATUS: blocked` with quoted evidence; reroute to a Claude tier is a user decision recorded under the frozen plan's Escalated points (spec section 4).
- The Flash lane runs in the MAIN CHECKOUT ONLY this cycle (spec
  Decisions), with ONE declared exception: Task 6's trusted scratch repo
  during live verification (Sol check-off round 3, finding 2).
- Probed facts this plan treats as fixed (2026-07-25, agy 1.1.7): stdin does NOT reach the model in print mode; a workspace file named in a short `-p` pointer is read reliably (probed to 7,152 bytes); default-verbosity logs carry NO response-side model attribution (client-side `Print mode: starting` / `Propagating selected model override` lines only).
- All new test code and evals content is pure ASCII.
- Commits: lowercase imperative, prefixed `0.12.0:`, no AI-attribution trailers.
- This cycle's tasks are built by the CURRENT implementer lanes (sonnet/haiku) — the Flash lane cannot build itself.
- Frozen after debate: changes require reopening the debate.

---

### Task 1: Contract tests (all failing first)

**Files:**
- Create: `evals/multi-model-verify/test_flash_implementer.py`
- Test: same file (this task is the test suite)

**Interfaces:**
- Consumes: `agents/implementer.md` (shared-block markers arrive in Task 2 — the parity test FAILS until then; that is expected order).
- Produces: the pinned strings Tasks 2-3 must satisfy verbatim. Later tasks copy pinned text FROM these tests, never the reverse.

- [ ] **Step 1: Write the failing test file**

```python
"""Contract pins for the Flash implementer lane (agents/flash-implementer.md).

Amended by design spec 2026-07-25 (advisory review B1-B8): these tests pin
the agent file's contract text so drift in the dispatch recipe, route
check, forbidden-bypass class, or report format fails offline with zero
CLI calls. The two agent files are the only allowed homes for the
implementer model literal.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FLASH = REPO / "agents" / "flash-implementer.md"
CLASSIC = REPO / "agents" / "implementer.md"
CANONICAL_ID = "gemini-3.6-flash-medium"
SHARED_START = "<!-- shared-contract:start -->"
SHARED_END = "<!-- shared-contract:end -->"


def _read(p):
    return p.read_text(encoding="utf-8")


def _frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert m, "missing frontmatter"
    return m.group(1)


def test_flash_frontmatter_pins_model_and_tools():
    fm = _frontmatter(_read(FLASH))
    assert re.search(r"^model: haiku$", fm, re.MULTILINE)
    m = re.search(r"^tools: (.+)$", fm, re.MULTILINE)
    assert m, "tools allowlist missing"
    tools = [t.strip() for t in m.group(1).split(",")]
    assert sorted(tools) == ["Bash", "Glob", "Grep", "Read"]


def test_flash_dispatch_contract():
    body = _read(FLASH)
    assert "--model " + CANONICAL_ID in body
    assert "--add-dir" in body
    assert "--log-file" in body
    # unique-suffix brief name + full lifecycle, pinned by exact sentence
    # fragments so a regression cannot pass on loose keywords
    # (Sol check-off round 2, finding 3)
    assert "AGY-TASK-BRIEF-" in body
    assert "sole transient exception" in body.lower()
    assert "the dispatch log file's basename" in body
    assert "on success, failure, and interruption alike" in body
    # brief-borne no-commands line (Sol diff-debate F1: a task whose text
    # carries a verification command otherwise soft-denies in print mode
    # and blocks the green path - live-verified 2026-07-25)
    assert ("Do not run commands or attempt verification - the wrapper "
            "runs all verification after you finish; your only job is "
            "the file edits.") in body
    # stdin is probed-dead in print mode; the body must not suggest it
    assert "stdin" not in body.lower() or "does not reach" in body.lower()


def test_flash_route_check_strings():
    body = _read(FLASH)
    assert 'Print mode: starting' in body
    assert 'model="' + CANONICAL_ID + '"' in body
    assert "Propagating selected model override" in body
    assert "requested and propagated" in body
    assert "used and confirmed" not in body.replace(
        'never "used and confirmed"', "")
    # transcript/tree corroboration (Sol check-off F1: the log carries no
    # file actions; evidence lives in the brain transcript)
    assert "transcript_full.jsonl" in body
    assert "conversationID" in body
    assert ("every path git status reports changed must appear in the "
            "brain transcript as a successful file-changing action"
            ) in body.lower()


def test_flash_preflight_pins():
    body = _read(FLASH)
    assert "agy models" in body
    assert "trustedWorkspaces" in body
    # conservative rule-class ban + clean baseline + stale-brief check,
    # pinned by exact sentence fragments (Sol check-off round 2,
    # finding 3): loose keyword pins would still pass a regression to
    # path-scoped matching or a dropped preflight
    assert "any `write_file(` entry, whatever path it names" in body
    assert "allow rule" in body
    assert "git status --porcelain" in body
    assert "No file matching `AGY-TASK-BRIEF-*`" in body
    # main-checkout scope with its one declared carve-out (Sol round 3)
    assert "sole live-verification exception" in body


def test_flash_route_report_carries_transcript():
    body = _read(FLASH)
    assert "AND the brain transcript's path" in body


def test_flash_forbidden_bypass_class():
    body = _read(FLASH)
    assert "--dangerously-skip-permissions" in body
    idx = body.find("--dangerously-skip-permissions")
    window = body[max(0, idx - 200):idx + 200].lower()
    assert "never" in window or "forbidden" in window
    assert "persisted" in body and "settings" in body


def test_flash_report_headings():
    body = _read(FLASH)
    for heading in ("**STATUS:**", "**ROUTE:**", "**FILES CHANGED:**",
                    "**VERIFICATION:**", "**DEVIATIONS:**"):
        assert heading in body, heading
    # the four shared headings are pinned in BOTH files so a unilateral
    # rename in implementer.md cannot pass the suite (ROUTE is
    # lane-specific to the flash file)
    classic = _read(CLASSIC)
    for heading in ("**STATUS:**", "**FILES CHANGED:**",
                    "**VERIFICATION:**", "**DEVIATIONS:**"):
        assert heading in classic, heading


def _shared_block(text, path):
    assert SHARED_START in text and SHARED_END in text, (
        "missing shared-contract markers in " + str(path))
    return text.split(SHARED_START)[1].split(SHARED_END)[0]


def test_shared_contract_parity():
    # byte-identical shared block; ROUTE is lane-specific and lives
    # outside the block (spec section 1)
    assert _shared_block(_read(FLASH), FLASH) == _shared_block(
        _read(CLASSIC), CLASSIC)


def test_classic_lane_note_retired_stale_claim():
    body = _read(CLASSIC)
    assert "Nothing else in the plugin references" not in body
    assert "flash-implementer" in body


SWEEP_GLOBS = [
    "skills/**/*.md", "commands/*.md", "tools/*.ps1", "hooks/*",
    "evals/**/*.py", "evals/**/*.json", "evals/**/*.ps1",
    "README.md", "CLAUDE.md", "agents/*.md",
]
# The two agent files are the contract homes; this test file necessarily
# carries the literal as its enforcement pin.
ALLOWED = {FLASH.resolve(), CLASSIC.resolve(),
           Path(__file__).resolve()}


def test_flash_literal_single_source():
    offenders = []
    for pattern in SWEEP_GLOBS:
        for p in REPO.glob(pattern):
            if p.resolve() in ALLOWED:
                continue
            if "gemini-3.6-flash" in p.read_text(encoding="utf-8",
                                                 errors="replace"):
                offenders.append(str(p))
    assert offenders == []


def test_sonnet_implementer_literals_removed():
    readme = _read(REPO / "README.md")
    assert "currently `model: sonnet`" not in readme
    # absence pins alone are vacuous against line-wrapped source; the
    # presence pins below are the real oracles for Task 3's rewrites
    assert "`haiku`/`opus` are drop-ins" not in readme
    assert "any Claude tier is a drop-in" in readme
    fpf = _read(REPO / "skills" / "multi-model-verify" / "references"
                / "frozen-plan-format.md")
    assert "Sonnet 5" not in fpf
    assert "the pinned lane in `agents/`" in fpf
```

- [ ] **Step 2: Run the new file to verify everything fails for the right reasons**

Run: `python -m pytest evals/multi-model-verify/test_flash_implementer.py -v`
Expected: FAIL — flash tests AND parity with FileNotFoundError (agent file absent; the parity test's "missing shared-contract markers" assertion can only fire once the file exists without markers), `test_classic_lane_note_retired_stale_claim` and `test_sonnet_implementer_literals_removed` with assertion errors. `test_flash_literal_single_source` PASSES vacuously (no stray literal exists yet) — that is correct behavior, not a defect.

- [ ] **Step 3: Confirm the rest of the suite is untouched**

Run: `python -m pytest evals -q --ignore=evals/multi-model-verify/test_flash_implementer.py`
Expected: green (133 passed, 1 skipped baseline).

- [ ] **Step 4: Commit**

```bash
git add evals/multi-model-verify/test_flash_implementer.py
git commit -m "0.12.0: add flash implementer contract tests (failing)"
```

---

### Task 2: The agent file + classic Lane-note edit

**Files:**
- Create: `agents/flash-implementer.md`
- Modify: `agents/implementer.md` (shared-contract markers around its "The contract" section; Lane note pointer + stale-sentence retirement)

**Interfaces:**
- Consumes: Task 1's pinned strings (copy them exactly).
- Produces: the shared-contract block text both files carry; the ROUTE report line later tasks and the diff-debate brief reference.

- [ ] **Step 1: Write `agents/flash-implementer.md` exactly as follows**

````markdown
---
name: flash-implementer
description: Zero-judgment Flash implementer for frozen-plan tasks. Use when executing build tasks from a debate-frozen implementation plan - give it ONE task's verbatim text plus the plan's Global Constraints and a log-file path. It delegates ALL code-writing to Gemini 3.6 Flash via the Antigravity CLI headlessly, verifies route and authorship evidence, runs the task's verification itself, and reports. It never types repo code and never makes design decisions.
model: haiku
tools: Read, Grep, Glob, Bash
---

# Flash implementer (agy wrapper)

You supervise ONE task from a frozen implementation plan. Gemini 3.6 Flash
does ALL the typing through the Antigravity CLI (`agy`); you do preflight,
dispatch, evidence checks, verification, and honest reporting. You never
edit or create repo files yourself — your tool grant has no Edit or Write,
and using Bash to write repo content is equally forbidden: a changed file
the brain transcript cannot account for fails the task. The one declared
carve-out is the brief file below — the sole transient exception to the
never-write rule, and it never survives to the evidence checks.

<!-- shared-contract:start -->
## The contract

- Build exactly what the task says: the files it lists, the code it shows,
  the commands it specifies. Nothing else.
- No improvements, no drive-by refactors, no added error handling, no scope
  adjustments. A deviation is a defect even when it looks better — the diff
  gets checked against the plan afterward, and unexplained drift fails it.
- **INPUT GAP rule:** if the task references a file, interface, value, or
  convention that is not in your brief and not discoverable at the exact
  path the task names, STOP and report the gap. Never invent or guess the
  missing piece.
- Run the task's verification commands yourself and read the output. Never
  claim completion without re-running verification — "should work" means
  the task is not done.
<!-- shared-contract:end -->

## Inputs (from the dispatching controller)

- The task's verbatim text and the plan's Global Constraints.
- The workspace directory (this cycle: the main checkout only, with the
  sole live-verification exception — the plan's Task 6 trusted scratch
  repo).
- A log-file path OUTSIDE the workspace (the controller owns it; you never
  place logs in the repo tree).

## Preflight (all five must pass BEFORE dispatch)

1. `agy models` (binary at `$LOCALAPPDATA/agy/bin/agy.exe`) — output must
   contain `gemini-3.6-flash-medium`. Anything else (missing binary,
   sign-out, missing model) is blocked.
2. `~/.gemini/antigravity-cli/settings.json` — `trustedWorkspaces` must
   contain the workspace directory. If not: blocked, and the report quotes
   the fix ("run one interactive `agy` session in the workspace and approve
   trust").
3. The same settings file must carry NO file-writing per-tool allow rule
   at all — any `write_file(` entry, whatever path it names, is blocking.
   A persisted settings allow rule is the durable, call-site-invisible
   bypass class — its absence is the load-bearing permission control; path
   spellings vary, so the rule CLASS is banned rather than path-matched.
   If present: blocked, quoting the rule.
4. `git status --porcelain` in the workspace must be EMPTY. A dirty tree
   makes authorship attribution impossible — blocked, quoting the paths.
5. No file matching `AGY-TASK-BRIEF-*` exists in the workspace — a stale
   brief means an earlier dispatch died mid-cleanup: blocked.

## Dispatch

1. Write the brief to `<workspace>/AGY-TASK-BRIEF-<unique>.md` with a Bash
   heredoc — `<unique>` is the dispatch log file's basename, so briefs
   never collide. Content: the task's verbatim text, the Global
   Constraints, the exact files list, and this exact closing line:
   `Do not run commands or attempt verification - the wrapper runs all verification after you finish; your only job is the file edits.`
   (Print mode auto-denies command execution, so a verification attempt
   by Flash soft-denies and blocks the run — live-verified 2026-07-25.
   stdin does not reach the model in print mode — probed 2026-07-25; the
   workspace brief file is the delivery mechanism.) This file is the sole
   transient exception to your never-write rule.
2. Run (single line):
   `agy -p "Read the file AGY-TASK-BRIEF-<unique>.md in the workspace and execute it exactly." --model gemini-3.6-flash-medium --add-dir <workspace> --log-file <log-path>`
3. Delete the brief file immediately after agy exits — on success,
   failure, and interruption alike — and always BEFORE any evidence
   check, so it never appears in `git status`. If your run is resumed
   after an interruption, delete any leftover brief FIRST.

## Route and authorship checks (every run)

- On the log file: `Print mode: starting` line present containing
  `model="gemini-3.6-flash-medium"`.
- On the log file: `Propagating selected model override` line present
  (presence only — its display label is not matched).
- Transcript/tree corroboration: parse `conversationID="<uuid>"` from the
  log's `Print mode: starting` line, then read the brain transcript at
  `~/.gemini/antigravity-cli/brain/<conversationID>/.system_generated/logs/transcript_full.jsonl`
  (the `--log-file` log itself carries NO file actions — probed). Every
  path git status reports changed must appear in the brain transcript as
  a successful file-changing action. A changed file the transcript never
  mentions means someone other than Flash typed it — blocked, no matter
  what the tests say. A missing transcript is blocked.
- This evidence is client-side: report the route as **requested and
  propagated**, never "used and confirmed". Server-side substitution is
  not detectable from this evidence class.

## Failure handling — loud, never silent

Blocked (quote the exact output) on: any preflight failure, the print-mode
soft-deny line ("auto-denied"), nonzero exit, a missing or mismatched
route line, a corroboration mismatch, or writes diverted to agy's internal
scratch (expected files absent from the tree). Never retry with
`--dangerously-skip-permissions` — that flag is forbidden in this lane, as
is ANY approval-bypass flag or persisted per-tool allow rule added to agy
settings. Never complete the work yourself: rerouting a blocked task to a
Claude tier is the user's decision, recorded in the plan's Escalated
points — not yours.

## Report format (your final message)

- **STATUS:** done | blocked | INPUT GAP: <exactly what is missing>
- **ROUTE:** the resolved model ID as requested and propagated, plus the
  retained log file's path AND the brain transcript's path
- **FILES CHANGED:** actual paths from `git status` — on blocked, STILL
  list every path Flash already touched so the session can revert a
  partial write
- **VERIFICATION:** each command you ran yourself, with its real output
  (condensed)
- **DEVIATIONS:** must be "none" — anything else means you stopped and are
  explaining why the task could not be built as written

## Lane note

This agent pins the Flash implementation lane. Canonical model literal:
`gemini-3.6-flash-medium` (Gemini 3.6 Flash, medium reasoning effort,
Antigravity CLI resolved ID). The literal lives ONLY here;
`implementer.md` pins its own lane's model in its frontmatter and Lane
note — every other surface points at the agent files. Trust is per-directory and interactive-only, so this lane runs in
the main checkout this cycle, with the plan's Task 6 trusted scratch repo
as the sole live-verification exception — a worktree trust story is
future work.
````

- [ ] **Step 2: Edit `agents/implementer.md`**

Wrap its existing "## The contract" section (the four bullets, verbatim,
from "## The contract" heading's first bullet through the "should work"
bullet) in the same markers:

```markdown
<!-- shared-contract:start -->
## The contract
[existing four bullets unchanged]
<!-- shared-contract:end -->
```

Then in its Lane note, replace the sentence
"This agent pins the cheap implementation lane (currently Sonnet 5). Nothing
else in the plugin references the implementer's model. Two swap paths:"
with:

```markdown
This agent pins the direct-typing Claude lane (currently Sonnet 5;
transcription tasks dispatch it with a haiku override). Build tasks run on
the Flash lane instead — see `flash-implementer.md`, the supervisor-pattern
wrapper this note's vendor-swap path describes. Two swap paths:
```

- [ ] **Step 3: Run the contract tests**

Run: `python -m pytest evals/multi-model-verify/test_flash_implementer.py -v`
Expected: all PASS except `test_sonnet_implementer_literals_removed` (README and frozen-plan-format literals remain until Task 3).

- [ ] **Step 4: Commit**

```bash
git add agents/flash-implementer.md agents/implementer.md
git commit -m "0.12.0: add flash-implementer agent, mark shared contract"
```

---

### Task 3: Literal single-sourcing (README + frozen-plan-format)

**Files:**
- Modify: `README.md` (repo-map row ~line 66; role-plug section ~lines 126-139)
- Modify: `skills/multi-model-verify/references/frozen-plan-format.md` (line 4)

**Interfaces:**
- Consumes: Task 1's absence pins (the exact strings that must vanish).
- Produces: a repo where `test_flash_implementer.py` is fully green.

- [ ] **Step 1: README repo-map row**

Replace the `agents/implementer.md` row's text
"Zero-judgment executor for frozen-plan tasks, pinned to the cheap lane (currently `model: sonnet`)"
with:
"Zero-judgment direct-typing executor for frozen-plan tasks (model pinned in the file's frontmatter)"

Add a new row directly beneath it:
"| `agents/flash-implementer.md` | Zero-judgment Flash lane: haiku wrapper drives Gemini Flash through the Antigravity CLI headlessly; route + authorship evidence checked every run (model literal pinned in the file) |"

- [ ] **Step 2: README role-plug section**

Replace
"- **Implementer, Claude tier** — edit one line: `model:` in `agents/implementer.md` frontmatter (`sonnet` today; `haiku`/`opus` are drop-ins). The contract (zero judgment calls, INPUT GAP rule, structured report) stays identical whoever fills it."
with:
"- **Implementer, Claude tier** — edit one line: `model:` in `agents/implementer.md` frontmatter (any Claude tier is a drop-in). The contract (zero judgment calls, INPUT GAP rule, structured report) stays identical whoever fills it."

Replace, in the cross-vendor bullet that follows, the text
"a vendor swap uses the supervisor pattern documented in `agents/implementer.md`:"
with:
"a vendor swap uses the supervisor pattern `agents/flash-implementer.md` implements (documented in `agents/implementer.md`'s Lane note):"

- [ ] **Step 3: frozen-plan-format.md line 4**

Replace
"The implementer (Sonnet 5 or the session model, via superpowers"
with:
"The implementer (the pinned lane in `agents/`, or the session model, via superpowers"

- [ ] **Step 4: Full suite green**

Run: `python -m pytest evals -q`
Expected: baseline + all new tests pass, 0 failures.

Run: `python evals/tools/skill_lint.py skills/multi-model-verify --strict && python evals/tools/skill_scanner.py skills && python evals/tools/run_trigger_evals.py`
Expected: all green (frozen-plan-format.md is a skill reference — lint must stay clean).

- [ ] **Step 5: Commit**

```bash
git add README.md skills/multi-model-verify/references/frozen-plan-format.md
git commit -m "0.12.0: single-source implementer model literals"
```

---

### Task 4: Doctor row + drift-snapshot version field

**Files:**
- Modify: `commands/doctor.md` (new check 7)
- Modify: `tools/check-drift.ps1` (snapshot gains `agy` field)

**Interfaces:**
- Consumes: `agents/flash-implementer.md`'s Lane note as the parse source.
- Produces: doctor check 7; snapshot key `agy`.

- [ ] **Step 1: Append to `commands/doctor.md`**

````markdown
## 7. agy transport (Flash implementer lane)

Resolve the INSTALLED copy's `agents/flash-implementer.md` under the
`installPath` from check 1 and parse the canonical model literal from its
Lane note (the pinned model-ID token declared there) — the agent file is the ONE
place the implementer model is defined; carry no literal here. A missing
declaration is itself BROKEN. Then:

- `& "$env:LOCALAPPDATA\agy\bin\agy.exe" --version` — missing binary =
  BROKEN (the Flash lane cannot dispatch), report the install one-liner.
- `agy models` — output must contain the parsed literal. Sign-out or a
  missing model = BROKEN with the actual output. No generation probe —
  this is a reachability check, and agy free-tier quota is opaque.

Report the route language as declared in the agent file: evidence is
client-side, requested and propagated only.
````

- [ ] **Step 2: Snapshot field in `tools/check-drift.ps1`**

Read the FULL file first. The file's mandated style is the carry-forward
pattern (check-drift.ps1:193-205: "A transient probe failure must never
clobber the last known-good value"), and snapshot values are precomputed
variables, never inline statements (an `if` used directly as a hashtable
value is a parse error under the script's Windows PowerShell 5.1
runtime). Three additions, each beside its existing sibling:

1. Beside the other version probes (near the codex probe, ~lines 119-125):

```powershell
$agyVersion = ""
$agyExe = Join-Path $env:LOCALAPPDATA "agy\bin\agy.exe"
if (Test-Path $agyExe) {
    $agyVersion = (& $agyExe --version 2>$null | Select-Object -First 1)
}
```

2. In the carry-forward block (inside the existing `if ($snapshot)` at
~lines 198-205, alongside `$codexVersionToSave`):

```powershell
$agyVersionToSave = $agyVersion
# and inside if ($snapshot):
if (-not $agyVersionToSave -and $snapshot.agy) { $agyVersionToSave = $snapshot.agy }
```

3. In the `$newSnapshot` object (~lines 274-279, beside `codex = ...`):

```powershell
agy = $agyVersionToSave
```

Informational only: no comparison logic, no failure path — mirrors how the
codex version note works (STALE note, never BROKEN).

- [ ] **Step 3: State-machine suite (mandatory — check-drift.ps1 changed)**

Run: `evals/tools/drift_statemachine_tests.ps1`
Expected: ALL PASS. This is the CLAUDE.md opt-in rule; it is slow (four scenarios re-run pytest in a disposable worktree) — budget ~15+ minutes.

- [ ] **Step 4: Full pytest again (attestation tests read doctor.md)**

Run: `python -m pytest evals -q`
Expected: green.

- [ ] **Step 5: Commit**

```bash
git add commands/doctor.md tools/check-drift.ps1
git commit -m "0.12.0: doctor agy row and drift snapshot version field"
```

---

### Task 5: Settings hygiene, repo trust, version bump (ATTENDED)

**Files:**
- Modify: `~/.gemini/antigravity-cli/settings.json` (user-global, outside repo)
- Modify: `.claude-plugin/plugin.json`

**Interfaces:**
- Consumes: spec section 3's declared fallback.
- Produces: a settings state the agent's preflight (Task 2 text) passes against; plugin version 0.12.0.

- [ ] **Step 1: Remove the probe-dir allow rule (keep its trust entry for now)**

Edit `~/.gemini/antigravity-cli/settings.json`: delete the `write_file`
entry in `permissions.allow` whose path targets the agy-probe scratchpad
directory, whatever its exact path spelling in the file (leave the array
empty if nothing else remains), then re-read the file to confirm the
deletion. Do NOT remove the probe dir's `trustedWorkspaces` entry yet —
Step 2's probe needs a trusted directory.

- [ ] **Step 2: allowNonWorkspaceAccess narrowing attempt (bounded)**

Try exactly one narrowing: set `allowNonWorkspaceAccess` to `false`, then
run this raw probe against the still-trusted probe dir (PowerShell;
`$probe` = the agy-probe scratchpad dir from the spec's probe record):

```powershell
& "$env:LOCALAPPDATA\agy\bin\agy.exe" -p "Create a file named narrow-probe.txt in the workspace directory $probe containing exactly the line: NARROW-OK" --model gemini-3.6-flash-low --add-dir $probe --log-file "$probe\narrow.log"
```

`narrow-probe.txt` lands with NARROW-OK = keep `false`. Soft-denied or
absent = restore `true` and record in the SDD ledger:
"allowNonWorkspaceAccess=true required for print-mode writes as of agy
1.1.7 — documented fallback per spec section 3." Do not iterate further.

- [ ] **Step 3: Drop the probe-dir trust entry**

Remove the probe dir from `trustedWorkspaces` (session-temporary dir; the
repo is the lane's only PERSISTENT implementation workspace this cycle —
Task 6's trusted scratch repo is the declared live-verification
exception).

- [ ] **Step 4 (ATTENDED - user): Trust the repo**

User runs one interactive `agy` session in
`C:\Users\Brandon\Documents\parallax`, approves trust, exits. Verify:
`trustedWorkspaces` in the settings file now contains the repo path.

- [ ] **Step 5: Version bump + commit**

Edit `.claude-plugin/plugin.json`: `"version": "0.12.0"`. Commit
IMMEDIATELY (Sol check-off round 3, finding 1 — the dry-run's clean-tree
check cannot pass over an uncommitted bump):

```bash
git add .claude-plugin/plugin.json
git commit -m "0.12.0: bump plugin version"
```

- [ ] **Step 6: Preflight dry-check (post-commit, clean tree)**

Run the agent's FIVE preflight checks by hand against the real
environment, verbatim from the agent body: (1) `agy models` contains the
pinned ID; (2) `trustedWorkspaces` contains the repo path; (3) the
settings file carries NO `write_file(` entry at all — if an unrelated
write rule remains, STOP and surface it for user disposition (never
silently delete shared configuration); (4) `git status --porcelain` in
the repo is empty (the bump is already committed); (5) no
`AGY-TASK-BRIEF-*` file exists in the repo. All five must pass.

---

### Task 6: Live verification (ATTENDED; runs only after the plan debate converges)

**Files:**
- None in-repo (scratch repo + probe records; SDD ledger notes)

**Interfaces:**
- Consumes: the installed 0.12.1 cache (dev loop: `claude plugin update parallax@parallax`, restart — the agent is NOT live before that).
- Produces: the live evidence the diff debate's brief cites.

- [ ] **Step 1 (ATTENDED - user): Dev loop**

Bump is committed (Task 5: 0.12.0; the amendment bump to 0.12.1 is resolved row 25); user runs `claude plugin update parallax@parallax` and restarts the session. Without the restart the dispatched agent is the cached pre-0.12.1 set — a dry-run before restart tests nothing.

- [ ] **Step 2: Scratch repo setup**

Create a scratch git repo in the session scratchpad with one file
(`hello.py`, `print("hello")`), and COMMIT it — the agent's clean-tree
preflight (check 4) requires an empty `git status --porcelain` before
dispatch (Sol check-off round 2, finding 1). Then an interactive trust
approval (ATTENDED - user, same mechanism as Task 5 Step 4).

- [ ] **Step 3: Green dry-run through the REAL agent**

Verify `git status --porcelain` in the scratch repo is empty. Dispatch
`parallax:flash-implementer` (fresh subagent) with a minimal task:
"Modify hello.py so it prints exactly 'hello flash'. Verification:
`python hello.py` prints `hello flash`." plus a log path in the
scratchpad. The controller supplies ONLY these frozen inputs — the
no-commands closing line is brief-borne per the agent's Dispatch step 1,
never a controller addition (Sol diff-debate F1). Expected report:
STATUS done; ROUTE carries
`gemini-3.6-flash-medium` + log path + brain transcript path; FILES
CHANGED lists `hello.py`; VERIFICATION shows the wrapper's own
`python hello.py` output; DEVIATIONS none. Controller re-runs
`python hello.py` itself (never trust the report alone — 0.10.0 lesson:
controller-owned verification). Then COMMIT the green result in the
scratch repo and verify `git status --porcelain` is empty again, so the
later probes start from a clean baseline.

- [ ] **Step 4a: Raw red probe — the CLI's invalid-model path (no agent)**

Controller runs, directly in the scratch repo (split from a single
disjunctive probe by Sol check-off F5 — a wrapper refusing a
contradictory brief must not count as exercising this path):

```powershell
& "$env:LOCALAPPDATA\agy\bin\agy.exe" -p "Reply with exactly: X" --model gemini-9.9-fake --add-dir <scratch> --log-file <scratchpad>\red-raw.log
```

Expected: loud "invalid model selection" rejection, nonzero exit, no
file changes in the scratch tree.

- [ ] **Step 4b: Reachable-failure probe — the REAL agent's blocked path**

First save the ORIGINAL settings content
(`~/.gemini/antigravity-cli/settings.json`) to the session scratchpad.
Then plant a NONMATCHING SENTINEL rule in `permissions.allow`:
`write_file(/parallax-sentinel-never-matches/)` — preflight check 3 bans
the rule CLASS, so the sentinel triggers it without ever granting a
functional permission (Sol check-off round 2, finding 4). Dispatch
`parallax:flash-implementer` with a trivial task in the scratch repo.
Expected: STATUS blocked at preflight check 3, quoting the sentinel; no
dispatch reaches agy; `git status --porcelain` still empty. Restore the
saved ORIGINAL settings content afterward — including on an aborted or
interrupted run, restore-before-anything-else on resume — and re-read
the file to confirm it matches the saved copy.

- [ ] **Step 5 (ATTENDED - user): skip-permissions print-mode probe**

User runs, in the scratch repo (isolated), the one command the spec's
probe task left open:
`agy -p "Create a file named skip-probe.txt containing SKIP-OK" --model gemini-3.6-flash-low --add-dir <scratch> --dangerously-skip-permissions --log-file <scratchpad>\probe-skip.log`
after REMOVING the scratch repo's trust entry. Record the outcome in the
SDD ledger: file created = the flag works in print mode (both bypass
surfaces live); soft-denied = the flag is inert in print mode (the
settings assertion is the whole live defense). Either way the lane's
contract is unchanged — the flag stays forbidden; this only settles which
defense is load-bearing, per spec section 2.

- [ ] **Step 6: Record**

Write the dry-run + red-probe + skip-probe outcomes into the SDD ledger
(`.superpowers/sdd/2026-07-25-flash-implementer/`), with log paths — the
diff-debate brief cites them.

---

## Debate record

**Participants:** Fable 5 (session) / Kimi K3 `kimi-code/k3-256k` (kimi-cli 1.49.0, session 4ba130bb-1615-4c95-9afc-d1e3049bb857) / GPT-5.6 Sol (codex exec, sessions 019f9ad5-e318-7831-8a3f-0c02c94caa8e primary check-off, 019f9c24-8351-7942-aeea-06f87774d26b mode-diff)
**Rounds used:** 2 of 4 (Kimi, plan mode) + 4 of 4 (Sol, primary check-off: r1 FIX, r2 FIX, r3 FIX, r4 terminal) + mode-diff debate at merge (Sol: r1 FIX, fix wave applied — resolved row 25; re-review in flight)
**Outcome:** converged with amendments
**Verification status:** FULL
**Degradation:** quota-exhausted (primary lane at the plan gate; backup lane substituted for rounds 1-2, primary check-off ran on the reset window)
**Authorized by:** user at round 1 (backup-lane substitution; the user's standing ruling retained the primary check-off before branch close)
**Raw rounds:** docs/superpowers/plans/rounds/2026-07-25-flash-implementer/ (plan-round1-brief.md, plan-round{1,2}-transcript.txt — Kimi; sol-checkoff-round{1,2,3,4}-{brief,reply,header} — Sol; diff-round{n}-{brief,reply,header} — Sol mode-diff)

Backup-lane note: Kimi ran read-only via a custom agent-file
(ReadFile/ReadMediaFile/Glob/Grep/SetTodoList; pre-review write-probe
refused) against a throwaway clone — the real tree was never exposed.
Route evidence per round: `Using LLM model: provider='managed:kimi-code'
model='k3-256k'` in ~/.kimi/logs/kimi.log (client-side class). Clone
`git status` after round 2: sole untracked file was the session-authored
brief (retained evidence: rounds/.../clone-status-after-round2.txt).
Sol round 1 route: header block model gpt-5.6-sol / provider openai /
sandbox read-only / effort high.

### Resolved points

| # | Claim | Raised by | Outcome | Evidence |
|---|-------|-----------|---------|----------|
| 1 | Task 4 doctor text trips the plan's own literal sweep | Kimi r1 | accepted; doctor text reworded (5391455) | plan Task 4 vs test sweep globs |
| 2 | Task 1 expected parity failure signature wrong (FileNotFoundError first) | Kimi r1 | accepted; expectation corrected | test_flash_implementer.py `_read` order |
| 3 | README drop-ins absence pin vacuous (line-wrapped source) | Kimi r1 | accepted; presence pins added | README.md:132-133 line break |
| 4 | Sweep omits evals/**/*.ps1 vs the reviewer sweep it mirrors | Kimi r1 | accepted; glob added | test_multi_model_verify.py:249 |
| 5 | Flash Lane note misstates where the literal lives | Kimi r1 | accepted; reworded | implementer.md carries no gemini literal |
| 6 | Drift-snapshot snippet violates carry-forward invariant; PS 5.1 parse risk | Kimi r1 | accepted; Task 4 Step 2 rewritten to carry-forward | check-drift.ps1:193-205 |
| 7 | Red-probe expectation contradicts pinned dispatch contract | Kimi r1 | accepted; made disjunctive (superseded by #14) | plan Task 6 vs agent body pin |
| 8 | Settings-deletion instruction pins unverifiable path spelling | Kimi r1 | accepted; made spelling-agnostic | settings file outside workspace |
| 9 | Parity narrower than spec claim (headings unpinned in classic) | Kimi r1 | accepted; headings pinned in both files | spec section 1 vs test scope |
| 10 | Corroboration evidence source wrong: --log-file log carries NO file actions; brain transcript does | Sol r1 | accepted; evidence source corrected to transcript_full.jsonl | probe9.log: 0 hits for probe-write4; brain/<cid>/.../transcript_full.jsonl: 5 hits |
| 11 | Brief-file lifecycle unsafe (collision, interruption, unbaselined git status) | Sol r1 | accepted; unique name + collision preflight + guaranteed cleanup + clean-baseline preflight | agent body Dispatch/Preflight sections |
| 12 | Debate record lacked required schema fields and session adjudication | Sol r1 | accepted; this record | frozen-plan-format.md:36-68, debate-protocol.md:63 |
| 13 | Settings check had no path-matching algorithm | Sol r1 | accepted; conservative rule-class ban (any write_file( entry) | trust entry vs allow rule spelling mismatch on this machine |
| 14 | Red probe vacuous (wrapper refusal passes without exercising failure path) | Sol r1 | accepted; split into raw-CLI probe + reachable-failure probe | plan Task 6 Steps 4a/4b |
| 15 | Task 6 green run cannot satisfy the new clean-tree preflight | Sol r2 | accepted; scratch baseline committed, post-run commit + clean check | plan Task 6 Steps 2-3 |
| 16 | Task 5 dry-check still tested the obsolete three-preflight contract | Sol r2 | accepted; Step 6 runs all five checks verbatim, unrelated rules escalate to user | plan Task 5 Step 6 |
| 17 | F2/F4 amendments not actually pinned (loose keyword asserts) | Sol r2 | accepted; exact-sentence pins + ROUTE transcript pin added | test_flash_implementer.py dispatch/preflight tests |
| 18 | Step 4b installs a functional bypass without interruption-safe restore | Sol r2 | accepted; nonmatching sentinel rule + save/restore-in-finally | plan Task 6 Step 4b |
| 19 | Stale cross-references (log/tree, workdir-scoped, log-only ROUTE, #13 for #14) | Sol r2 | accepted; synchronized | plan header, spec Decisions + section 6, resolved point 7 |
| 20 | Task 5 dry-run's clean-tree check cannot pass over the uncommitted bump | Sol r3 | accepted; bump commits first, dry-run post-commit | plan Task 5 Steps 5-6 |
| 21 | MAIN-CHECKOUT-ONLY absolute vs Task 6 scratch dispatch | Sol r3 | accepted; sole live-verification exception declared in constraints, spec, agent body (pinned) | Global Constraints, spec Decisions, agent Inputs + Lane note |
| 22 | Spec ROUTE line and step-4b recipe out of sync with amended contract | Sol r3 | accepted; synchronized (transcript path; sentinel + save/restore) | spec sections 1 and 6 |
| 23 | Record metadata lagged live rounds; r2/r3 raw artifacts unretained | Sol r3 | accepted; this revision + artifacts retained | rounds/ dir, this appendix |
| 24 | Task 5 Step 3 phrase omitted the declared Task 6 exception | Sol r4 | trivial accepted amendment; applied | plan Task 5 Step 3 |
| 25 | Task 6 green run patched the frozen dispatch input at runtime — the no-commands line was controller-added, not contract text, and lived only in the gitignored ledger | Sol diff-r1 | accepted; exact brief-borne closing line added to Dispatch step 1, test-pinned, plugin bumped 0.12.1, Task 6 Step 3 + 4b rerun with frozen inputs only | flash-dryrun.log:126 soft-deny vs flash-dryrun2.log clean; agent Dispatch step 1; test_flash_implementer.py dispatch pins |

### Escalated points (user-decided)

| # | Question | Session position | Reviewer position | Owner's call |
|---|----------|------------------|-------------------|--------------|

(none this debate; the consent-gated reroute mechanism records future
blocked-task reroutes here)

### Session adjudication (debate-protocol closing step)

Each Sol round-1 finding was verified against live evidence before
acceptance: #10 by grepping the retained WRITE4 probe log (zero
file-path hits) and the brain transcript (five hits); #11/#14 against
the agent body and plan text as cited; #12 against
frozen-plan-format.md:36-68; #13 against the live settings file's mixed
path spellings. Kimi's rounds 1-2 were adjudicated at the time (all nine
findings verified, fixes committed 5391455, round-2 re-verification by
the reviewer). Sol rounds 2-3 were each verified the same way (rows
15-23: cited lines read, sequencing conflicts reproduced by inspection,
fix waves re-reviewed in scope). No finding was refuted; no point
escalated. Convergence = Sol round-4 terminal confirmation of the
rounds-1-3 amendment chain (transcript retained under Raw rounds).

Mode-diff round 1 (row 25) was adjudicated the same way before
acceptance: the run-1 vs run-2 dispatch inputs differ only by the
controller-added no-commands line (retained logs: flash-dryrun.log line
126 soft-deny; flash-dryrun2.log zero soft-denies), and the frozen brief
recipe permitted only task text + Global Constraints + files list —
Sol's drift claim reproduced by inspection. Application governed by
checkpoint 20260725-2115-d46045700de2.
