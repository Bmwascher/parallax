# Flash Implementer Lane Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `agents/flash-implementer.md`, a haiku-wrapper SDD implementer that delegates all code-writing to Gemini 3.6 Flash via the Antigravity CLI (agy) headlessly, with mechanically enforced route and authorship checks.

**Architecture:** Architecture A from the spec (`docs/superpowers/specs/2026-07-25-flash-implementer-design.md`): a new wrapper agent beside the untouched `implementer.md`. The wrapper never types repo code (tools allowlist without Edit/Write + log/tree corroboration); every failure is loud (`STATUS: blocked`); reroute is consent-gated. Model literal single-sourced to the two agent files.

**Tech Stack:** Claude Code agent frontmatter, agy 1.1.7 print mode, pytest (offline contract pins), PowerShell (drift snapshot).

**STATUS: CANDIDATE.** The plan debate (Sol) runs at the ~Jul 29 codex reset and must converge before Tasks 1-6 execute; the diff debate gates the merge. The debate record is appended to this file when the plan debate runs. Tasks 5-6 contain ATTENDED steps (user-interactive); Task 6 additionally requires the plugin dev-loop (bump, update, restart).

## Global Constraints

- The canonical implementer-lane literal is the RESOLVED ID `gemini-3.6-flash-medium`; after this cycle it appears ONLY in `agents/implementer.md` and `agents/flash-implementer.md` (spec section 5).
- The wrapper's tools allowlist is exactly Read, Grep, Glob, Bash — no Edit, no Write, no NotebookEdit (spec section 1).
- Route language is "requested and propagated", never "used and confirmed" (spec section 2; doctor check-4 discipline).
- Loud failure only: any preflight, dispatch, route-check, or corroboration failure is `STATUS: blocked` with quoted evidence; reroute to a Claude tier is a user decision recorded under the frozen plan's Escalated points (spec section 4).
- The Flash lane runs in the MAIN CHECKOUT ONLY this cycle (spec Decisions).
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
    assert "AGY-TASK-BRIEF.md" in body
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
    # log/tree corroboration rule (advisory review B2 amendment)
    assert "every path git status reports changed must appear in the agy log" in body.lower()


def test_flash_preflight_pins():
    body = _read(FLASH)
    assert "agy models" in body
    assert "trustedWorkspaces" in body
    assert "allow rule" in body  # settings-rule absence assertion


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
    "evals/**/*.py", "evals/**/*.json", "README.md", "CLAUDE.md",
    "agents/*.md",
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
    assert "`haiku`/`opus` are drop-ins" not in readme
    fpf = _read(REPO / "skills" / "multi-model-verify" / "references"
                / "frozen-plan-format.md")
    assert "Sonnet 5" not in fpf
```

- [ ] **Step 2: Run the new file to verify everything fails for the right reasons**

Run: `python -m pytest evals/multi-model-verify/test_flash_implementer.py -v`
Expected: FAIL — flash tests with FileNotFoundError (agent file absent), parity with "missing shared-contract markers", `test_classic_lane_note_retired_stale_claim` and `test_sonnet_implementer_literals_removed` with assertion errors (literals still present). `test_flash_literal_single_source` PASSES vacuously (no stray literal exists yet) — that is correct behavior, not a defect.

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
the agy log cannot account for fails the task.

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
- The workspace directory (this cycle: the main checkout only).
- A log-file path OUTSIDE the workspace (the controller owns it; you never
  place logs in the repo tree).

## Preflight (all three must pass BEFORE dispatch)

1. `agy models` (binary at `$LOCALAPPDATA/agy/bin/agy.exe`) — output must
   contain `gemini-3.6-flash-medium`. Anything else (missing binary,
   sign-out, missing model) is blocked.
2. `~/.gemini/antigravity-cli/settings.json` — `trustedWorkspaces` must
   contain the workspace directory. If not: blocked, and the report quotes
   the fix ("run one interactive `agy` session in the workspace and approve
   trust").
3. The same settings file must carry NO per-tool allow rule targeting the
   workspace (for example `write_file(...)`). A persisted settings rule is
   the durable, call-site-invisible bypass class — its absence is the
   load-bearing permission control. If present: blocked, quoting the rule.

## Dispatch

1. Write the brief to `<workspace>/AGY-TASK-BRIEF.md` with a Bash heredoc:
   the task's verbatim text, the Global Constraints, and the exact files
   list. (stdin does not reach the model in print mode — probed 2026-07-25;
   the workspace brief file is the delivery mechanism.)
2. Run (single line):
   `agy -p "Read the file AGY-TASK-BRIEF.md in the workspace and execute it exactly." --model gemini-3.6-flash-medium --add-dir <workspace> --log-file <log-path>`
3. Delete `AGY-TASK-BRIEF.md` immediately after agy exits, BEFORE any
   evidence check, so it never appears in `git status`.

## Route and authorship checks (every run, on the log file)

- `Print mode: starting` line present containing
  `model="gemini-3.6-flash-medium"`.
- `Propagating selected model override` line present (presence only — its
  display label is not matched).
- Log/tree corroboration: every path git status reports changed must
  appear in the agy log as a file Flash touched. A changed file the log
  never mentions means someone other than Flash typed it — blocked, no
  matter what the tests say.
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
  retained log file's path
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
Antigravity CLI resolved ID). The literal lives ONLY here and in
`implementer.md`'s Lane note; every other surface points at the agent
files. Trust is per-directory and interactive-only, so this lane runs in
the main checkout this cycle — a worktree trust story is future work.
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
Lane note (the `gemini-3.6-flash-*` token) — the agent file is the ONE
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

Read the FULL file first. Locate where the snapshot object records the
codex version (search for the `codex` property written to
`drift-snapshot.json`). Add, adjacent and in the same style:

```powershell
agy = if (Test-Path "$env:LOCALAPPDATA\agy\bin\agy.exe") {
    (& "$env:LOCALAPPDATA\agy\bin\agy.exe" --version 2>$null | Select-Object -First 1)
} else { "N/A" }
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

Edit `~/.gemini/antigravity-cli/settings.json`: delete the
`write_file(/Users/Brandon/AppData/.../agy-probe/)` entry from
`permissions.allow` (leave the array empty if nothing else remains). Do
NOT remove the probe dir's `trustedWorkspaces` entry yet — Step 2's probe
needs a trusted directory.

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
repo is the lane's only workspace this cycle).

- [ ] **Step 4 (ATTENDED - user): Trust the repo**

User runs one interactive `agy` session in
`C:\Users\Brandon\Documents\parallax`, approves trust, exits. Verify:
`trustedWorkspaces` in the settings file now contains the repo path.

- [ ] **Step 5: Version bump**

Edit `.claude-plugin/plugin.json`: `"version": "0.12.0"`.

- [ ] **Step 6: Preflight dry-check + commit**

Run the agent's three preflight checks by hand against the real
environment (models list, trust entry, no repo-scoped allow rule) — all
three must pass. Then:

```bash
git add .claude-plugin/plugin.json
git commit -m "0.12.0: bump plugin version"
```

---

### Task 6: Live verification (ATTENDED; runs only after the plan debate converges)

**Files:**
- None in-repo (scratch repo + probe records; SDD ledger notes)

**Interfaces:**
- Consumes: the installed 0.12.0 cache (dev loop: `claude plugin update parallax@parallax`, restart — the agent is NOT live before that).
- Produces: the live evidence the diff debate's brief cites.

- [ ] **Step 1 (ATTENDED - user): Dev loop**

Bump is committed (Task 5); user runs `claude plugin update parallax@parallax` and restarts the session. Without the restart the dispatched agent is the cached pre-0.12.0 set — a dry-run before restart tests nothing.

- [ ] **Step 2: Scratch repo setup**

Create a scratch git repo in the session scratchpad with one file
(`hello.py`, `print("hello")`), plus an interactive trust approval
(ATTENDED - user, same mechanism as Task 5 Step 3).

- [ ] **Step 3: Green dry-run through the REAL agent**

Dispatch `parallax:flash-implementer` (fresh subagent) with a minimal task:
"Modify hello.py so it prints exactly 'hello flash'. Verification:
`python hello.py` prints `hello flash`." plus a log path in the
scratchpad. Expected report: STATUS done; ROUTE carries
`gemini-3.6-flash-medium` + log path; FILES CHANGED lists `hello.py`;
VERIFICATION shows the wrapper's own `python hello.py` output;
DEVIATIONS none. Controller re-runs `python hello.py` itself (never trust
the report alone — 0.10.0 lesson: controller-owned verification).

- [ ] **Step 4: Red probe — bad model must block, not output**

Same dispatch shape but the controller's brief pins
`--model gemini-9.9-fake` for this probe run only. Expected: STATUS
blocked quoting agy's "invalid model selection" output; no file changes.

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

Appended when the plan debate runs (quota-gated to the ~Jul 29 codex
reset). Until then this plan is a CANDIDATE: no task executes, per the
spec's Sol-gate decision. The advisory pass (Opus 5, same-vendor,
2026-07-25, two rounds, FIX -> conditional PASS folded into the spec) is
recorded in the spec's Review provenance section and forms no part of
this gate.
