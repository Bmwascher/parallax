# kimi-code Backup Lane Swap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the backup reviewer lane from `kimi-cli` 1.49.0 to kimi-code 0.31.1, delete the machinery that the new client's per-session logging makes unnecessary, and keep the one function of that machinery which per-session logging does NOT replace.

**Architecture:** Each debate runs under an isolated `KIMI_CODE_HOME` built from a committed config template plus a copied credential, with a single Markdown agent file carrying the tool allowlist. Route evidence is read from that debate's own session directory by an executable validator. Those files are CUMULATIVE across rounds, so every call still captures a freshness offset first — that is the one job the old byte-offset rule was doing that a per-session file does not do for you.

**Tech Stack:** PowerShell 5.1+ and 7 (both hosts), Python 3.12 + pytest, Markdown contract regions with the `contract:start`/`contract:end` checker.

## Revision note

Revised after Sol plan-debate round 1 (session `019fb913-1b73-7ab0-961d-ff2ae3a6b4f7`, 2026-07-31; reply retained at `docs/superpowers/plans/rounds/2026-07-31-kimi-code-swap/sol-plan-r1-reply.md`). Round 1 returned 1 PASS and 10 FIX. The structural finding was that revision 1 deleted the byte-offset rule on the reasoning that its only job was cross-session attribution; it also provided per-call freshness inside a session, and the probe record's own resume evidence shows two `llm config` lines accumulating in one session log. Four defects would have failed the build outright and are fixed here.

## Global Constraints

- Design spec: `docs/superpowers/specs/2026-07-31-kimi-code-swap-design.md`. Probe evidence: `docs/superpowers/plans/rounds/2026-07-31-kimi-code-swap/probe-record.md` and `probe-record-2.md`.
- Canonical backup model id is `kimi-code/k3-256k`, UNCHANGED. It may appear ONLY in `references/model-prompting-notes.md` and `evals/multi-model-verify/test_backup_lane.py`. `SWEEP_GLOBS` in that test includes `tools/*.ps1`, so no script under `tools/` may carry the literal, not even as a parameter default.
- The new binary is `~/.kimi-code/bin/kimi.exe`, version 0.31.1. Always invoke it by ABSOLUTE PATH; bare `kimi` is a PATH accident this cycle removes. The old CLI survives as `kimi-legacy.exe` (1.49.0) and is the rollback. Do NOT `pip uninstall kimi-cli`.
- `-r` is a HIDDEN alias on this client and does NOT appear in `--help`. The public resume flag is `-S/--session`. Any help-text assertion must use `--session`.
- Never `git add -A` and never `git add -u`. Stage by explicit path, every commit.
- Files under `skills/multi-model-verify/references/` are checked for the ABSENCE of backslashes by `test_backup_files_no_backslash_paths`. Write every path in those files with forward slashes.
- Contract regions must sit WHOLE inside a single pin, and a pin is only one of the three clause forms in `CLAUDE.md`. Adding or removing a region means editing `DECLARED_REGIONS` in `evals/multi-model-verify/test_contract_coverage.py`.
- Tests change FIRST for every live-verified contract, then the skill text.
- Verification gate, all four, from the repo root:
  `python evals/tools/skill_lint.py skills/multi-model-verify --strict`
  `python evals/tools/skill_scanner.py skills`
  `python evals/tools/run_trigger_evals.py`
  `python -m pytest evals -q`
- The invariant that governs every new check: an unmade, failed, or unreadable measurement is never a clean one.

---

### Task 1: Repair drift watch, including its own test suite

`tools/check-drift.ps1` invokes bare `kimi` and asserts the help lists `--quiet`, `--thinking` and `-w`. Since the installer renamed the Python binary, bare `kimi` resolves to kimi-code 0.31.1, which has none of them. Drift watch is currently broken and would report findings that describe nothing. Its offline state-machine suite stubs the same old surface and must move with it.

**Files:**
- Modify: `tools/check-drift.ps1:133-136` (version capture), `tools/check-drift.ps1:197-216` (check 2b)
- Modify: `tools/drift-snapshot.json:4`
- Modify: `evals/tools/drift_statemachine_tests.ps1:233`, `:250`, `:254`, `:257`, `:263`, `:270`, `:686`, `:706`
- Test: `evals/multi-model-verify/test_backup_lane.py` (appended)

**Interfaces:**
- Consumes: nothing.
- Produces: `$kimiExe` and `$kimiVersion` in `check-drift.ps1`; the snapshot key stays named `kimi`.

- [ ] **Step 1: Write the failing test**

Append to `evals/multi-model-verify/test_backup_lane.py`:

```python
DRIFT = REPO / "tools" / "check-drift.ps1"
STATEMACHINE = REPO / "evals" / "tools" / "drift_statemachine_tests.ps1"
KIMI_CODE_FLOOR = "0.31.1"


def test_drift_probes_the_new_cli_not_the_old_one():
    """The installer renamed the Python binary, so bare `kimi` is now
    kimi-code. Probing for --quiet/--thinking/-w against it produces
    findings that describe nothing real."""
    body = _read(DRIFT)
    assert '"--agent-file", "--skills-dir", "-m", "-p", "--session"' in body
    assert "--quiet" not in body
    assert "--thinking" not in body
    assert "import kimi_cli.tools.file" not in body


def test_drift_does_not_assert_a_hidden_alias():
    """`-r` works but is a HIDDEN alias: it is absent from --help on
    0.31.1. Asserting it would manufacture the exact false finding this
    task exists to remove."""
    body = _read(DRIFT)
    assert '"-r"' not in body


def test_drift_carries_a_kimi_code_version_floor():
    """`kimi upgrade` self-updates, so a recorded version string is not
    protection. The Fable panel seat has a floor; this lane needs one."""
    body = _read(DRIFT)
    assert "KimiCodeFloor" in body
    assert KIMI_CODE_FLOOR in body


def test_the_state_machine_stubs_moved_with_the_probe():
    """The offline suite stubs the CLI it drives. Leaving kimi-cli stubs
    behind makes the suite assert a surface the script no longer probes,
    which is a green suite proving nothing."""
    body = _read(STATEMACHINE)
    assert "kimi_cli" not in body
    assert "--thinking" not in body
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py -k "drift or state_machine or hidden_alias" -v`
Expected: FAIL, all four.

- [ ] **Step 3: Resolve the binary explicitly**

Replace `tools/check-drift.ps1:133-136`:

```powershell
$kimiVersion = ""
$kimiRaw = ""
$kimiExe = Join-Path $env:USERPROFILE ".kimi-code\bin\kimi.exe"
if (-not (Test-Path $kimiExe)) { $kimiExe = "" }
if ($kimiExe) {
    try { $kimiRaw = (& $kimiExe --version 2>&1 | Out-String).Trim() } catch {}
    if ($kimiRaw -match '(\d+\.\d+\.\d+)') { $kimiVersion = $Matches[1] }
}
```

Bare `kimi` is deliberately NOT a fallback. Two CLIs have carried that name on this machine, so a name-resolved probe can silently measure the wrong binary — which is the failure this whole task is repairing.

- [ ] **Step 4: Replace check 2b**

Replace `tools/check-drift.ps1:197-216`:

```powershell
# --- check 2b (every run): kimi-code backup transport surface ------------------
# Short flags (-m/-p) substring-match trivially inside long-flag help text;
# the long flags carry the real detection. `-r` is deliberately absent: it
# works but is a HIDDEN alias and never appears in --help, so asserting it
# would report a break that is not one. `kimi upgrade` self-updates, so a
# floor is checked as well as a version recorded.

$KimiCodeFloor = "0.31.1"

if ($kimiVersion) {
    $kimiHelp = (& $kimiExe --help 2>&1 | Out-String)
    foreach ($flag in @("--agent-file", "--skills-dir", "-m", "-p", "--session")) {
        $flagPattern = '(^|[\s,\[])' + [regex]::Escape($flag) + '($|[\s,\]=])'
        if (-not [regex]::IsMatch($kimiHelp, $flagPattern)) {
            $findings += "[CRITICAL] kimi-code --help ($kimiVersion) no longer lists $flag - the backup lane's transport commands are broken; update references/backup-lane.md"
        }
    }
    $parsedFloor = $null
    $parsedSeen = $null
    if ([version]::TryParse($KimiCodeFloor, [ref]$parsedFloor) -and
        [version]::TryParse($kimiVersion, [ref]$parsedSeen)) {
        if ($parsedSeen -lt $parsedFloor) {
            $findings += "[CRITICAL] kimi-code $kimiVersion is below the lane floor $KimiCodeFloor - the backup lane is UNAVAILABLE, not degraded; see references/backup-lane.md"
        }
    } else {
        $findings += "[CRITICAL] kimi-code version '$kimiVersion' is unparseable against floor $KimiCodeFloor - an unmade floor check is never a passing one"
    }
} else {
    $notes += "kimi-code absent or version unparseable - backup-lane probes skipped (lane optional; primary unaffected)"
}
```

`TryParse` rather than a bare `[version]` cast: a cast throws on a non-numeric string, and an exception here would abort the whole drift run rather than report a finding.

- [ ] **Step 5: Move the state-machine stubs**

In `evals/tools/drift_statemachine_tests.ps1`:

- Lines 250, 254, 257: replace each stub usage line so it echoes the new surface, e.g.
  `echo usage: kimi [-m MODEL] [--agent-file FILE] [--skills-dir DIR] [-p PROMPT] [-S ID]`
  Keep the three variants' EXISTING differences (which flag each one drops) so the scenarios still distinguish a full surface from a degraded one — just express them in the new flag vocabulary.
- Lines 263 and 270: delete the `kimi_cli` import-probe branch entirely. The new check has no module-import step.
- Line 686: change the assertion's subject from `kimi_cli tool modules` to the floor finding, so the scenario still asserts the vocabulary probe stays quiet on a flag-only drop.
- Line 706: replace the import-failure scenario with a BELOW-FLOOR scenario asserting `is below the lane floor`.
- Line 233's comment: rewrite to describe forwarding everything except the floor check.

- [ ] **Step 6: Run the tests**

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py -k "drift or state_machine or hidden_alias" -v`
Expected: PASS, all four.

- [ ] **Step 7: Update the snapshot**

`tools/drift-snapshot.json:4` becomes `"kimi": "0.31.1",`.

- [ ] **Step 8: Run the drift state machine**

Run: `pwsh -File evals/tools/drift_statemachine_tests.ps1`
Expected: ALL SCENARIOS PASS. Slow — four scenarios re-run the full pytest suite in a disposable worktree.

- [ ] **Step 9: Commit**

```bash
git add tools/check-drift.ps1 tools/drift-snapshot.json evals/tools/drift_statemachine_tests.ps1 evals/multi-model-verify/test_backup_lane.py
git commit -m "point drift watch at kimi-code and move its state-machine stubs"
```

---

### Task 2: The debate home builder

Built BEFORE the probes, because every probe in Task 3 needs a home to run in. Revision 1 had this backwards.

Note the naming, which revision 1 got wrong: the home is per-DEBATE, not per-round. It is built once before round 1 and used by every call of that debate, because the rounds of one debate are one session and the evidence files are that session's.

**Files:**
- Create: `tools/new-kimi-lane-home.ps1`
- Create: `evals/multi-model-verify/test_kimi_lane_home.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `tools/new-kimi-lane-home.ps1 -Path <dir> -Model <id> [-Effort <level>]`. `-Model` is MANDATORY with no default — a default would put the canonical literal in `tools/*.ps1`, which `test_backup_literal_single_source` fails. Prints the home's absolute path as its only stdout output. Exits non-zero on any refusal.

- [ ] **Step 1: Write the failing test**

Create `evals/multi-model-verify/test_kimi_lane_home.py`:

```python
"""Contract pins for the per-debate kimi-code lane home.

The home is what makes the lane's effort and thinking pins verifiable by
construction instead of by a later read of a user-global file, and what
keeps the user's own config hooks off the reviewer's approval path. It
also holds a copied OAuth credential, so its handling rules are part of
the contract rather than left to the caller.
"""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BUILDER = REPO / "tools" / "new-kimi-lane-home.ps1"


def _read(p):
    return p.read_text(encoding="utf-8")


def test_builder_exists():
    assert BUILDER.is_file(), str(BUILDER)


def test_model_has_no_default_literal():
    """SWEEP_GLOBS covers tools/*.ps1, so a parameter default carrying
    the canonical id would fail test_backup_literal_single_source. The
    caller reads the id from model-prompting-notes.md and passes it."""
    body = _read(BUILDER)
    assert "[Parameter(Mandatory = $true)][string]$Model" in body
    assert "k3-256k" not in body


def test_builder_refuses_without_a_credential():
    """An unauthenticated lane must stop, not degrade. A home built with
    no credential fails at dispatch, after the mirror is built and the
    brief written, which reads as a transport flake rather than setup."""
    body = _read(BUILDER)
    assert "the lane is UNAVAILABLE" in body


def test_builder_refuses_a_reused_or_unsafe_destination():
    """A reused home carries stale sessions, and stale sessions are
    exactly what the freshness rule exists to exclude - so reuse would
    undermine the evidence, not merely the tidiness. A destination inside
    any git work tree would put an OAuth credential in a repo."""
    body = _read(BUILDER)
    assert "destination already exists" in body
    assert "inside a git work tree" in body
    assert "rev-parse --is-inside-work-tree" in body


def test_builder_restricts_and_can_revoke_the_credential():
    body = _read(BUILDER)
    assert "SetAccessRuleProtection" in body
    assert "Remove-KimiLaneHome" in body


def test_builder_writes_no_hooks():
    """The user's real ~/.kimi-code/config.toml carries seven Orca
    lifecycle hooks, including PreToolUse and PermissionRequest, each
    running a shell script. A hook block sits on the reviewer's approval
    path and executes commands; it is not an environment note."""
    body = _read(BUILDER)
    assert "[[hooks]]" not in body
    assert "carries no hooks by construction" in body


def test_builder_pins_thinking_effort_and_the_empty_skill_sources():
    body = _read(BUILDER)
    assert "extra_skill_dirs = []" in body
    assert "[thinking]" in body
    assert "default_effort" in body
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest evals/multi-model-verify/test_kimi_lane_home.py -v`
Expected: FAIL on `test_builder_exists`, the rest erroring.

- [ ] **Step 3: Write the builder**

Create `tools/new-kimi-lane-home.ps1`:

```powershell
<#
.SYNOPSIS
  Build an isolated KIMI_CODE_HOME for one backup-lane debate.

.DESCRIPTION
  The reviewer never runs in the user's real kimi-code home. Two reasons,
  either sufficient alone:

  1. That config can declare lifecycle hooks. A PreToolUse or
     PermissionRequest hook executes a shell command on the reviewer's
     approval path. This home carries no hooks by construction.
  2. Effort and thinking have no CLI flag on this client. Writing the
     config here makes both verifiable by construction, then confirmed
     per call from the session log, instead of inferred from a later
     read of a user-global file.

  The home holds a COPY OF AN OAUTH CREDENTIAL, so this script refuses an
  existing destination, refuses any path inside a git work tree, and
  locks the directory to the current user. Remove-KimiLaneHome deletes it
  when the debate ends.

  Prints the home's absolute path on stdout and nothing else.

.PARAMETER Model
  Mandatory, no default. The canonical id lives in
  skills/multi-model-verify/references/model-prompting-notes.md and is
  read from there by the caller; a default here would place the literal
  in tools/*.ps1, which the single-source sweep forbids.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$Path,
    [Parameter(Mandatory = $true)][string]$Model,
    [string]$Effort = "high"
)

$ErrorActionPreference = "Stop"

function Remove-KimiLaneHome {
    param([Parameter(Mandatory = $true)][string]$Path)
    if (Test-Path $Path) { Remove-Item $Path -Recurse -Force }
}

if (Test-Path $Path) {
    Write-Error "destination already exists: $Path. A reused home carries stale sessions, and the freshness rule exists to exclude exactly those. Pass a fresh path."
    exit 1
}

$parent = Split-Path -Parent $Path
if (-not (Test-Path $parent)) {
    Write-Error "parent directory does not exist: $parent"
    exit 1
}
Push-Location $parent
try {
    $inRepo = (& git rev-parse --is-inside-work-tree 2>$null)
} finally {
    Pop-Location
}
if ($inRepo -eq "true") {
    Write-Error "refusing to build a lane home inside a git work tree: $Path. It would place an OAuth credential in a repository."
    exit 1
}

$srcHome = Join-Path $env:USERPROFILE ".kimi-code"
$srcCred = Join-Path $srcHome "credentials/kimi-code.json"
if (-not (Test-Path $srcCred)) {
    Write-Error "no kimi-code credential at $srcCred - the lane is UNAVAILABLE, not degraded. Run 'kimi login' first."
    exit 1
}

New-Item -ItemType Directory -Path $Path | Out-Null

# Lock the home to the current user BEFORE the credential is written into
# it: inheritance is disabled and inherited rules are dropped, not copied.
$acl = Get-Acl $Path
$acl.SetAccessRuleProtection($true, $false)
$me = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    $me, "FullControl",
    "ContainerInherit,ObjectInherit", "None", "Allow")
$acl.SetAccessRule($rule)
Set-Acl -Path $Path -AclObject $acl

New-Item -ItemType Directory -Path (Join-Path $Path "credentials") | Out-Null
New-Item -ItemType Directory -Path (Join-Path $Path "skills") | Out-Null
Copy-Item $srcCred (Join-Path $Path "credentials/kimi-code.json")

$shortModel = $Model -replace '^[^/]+/', ''
$config = @"
# Written by tools/new-kimi-lane-home.ps1 for one review debate.
# Carries no hooks by construction - see the script header.
default_model = "$Model"
extra_skill_dirs = []
telemetry = false

[thinking]
enabled = true

[providers."managed:kimi-code"]
type = "kimi"
api_key = ""
base_url = "https://api.kimi.com/coding/v1"

[providers."managed:kimi-code".oauth]
storage = "file"
key = "oauth/kimi-code"

[models."$Model"]
provider = "managed:kimi-code"
model = "$shortModel"
max_context_size = 262144
capabilities = [ "thinking", "always_thinking", "image_in", "tool_use" ]
support_efforts = [ "low", "high", "max" ]
default_effort = "$Effort"
"@

$config | Out-File (Join-Path $Path "config.toml") -Encoding utf8

(Resolve-Path $Path).Path
```

- [ ] **Step 4: Run the tests**

Run: `python -m pytest evals/multi-model-verify/test_kimi_lane_home.py -v`
Expected: PASS, all seven.

- [ ] **Step 5: Verify it builds a working home, on both hosts**

```powershell
$h = & <host> -NoProfile -File tools/new-kimi-lane-home.ps1 -Path "<fresh scratch>/lanehome-check" -Model "<id read from model-prompting-notes.md>"
$env:KIMI_CODE_HOME = $h
& "$env:USERPROFILE\.kimi-code\bin\kimi.exe" provider list
Remove-Item Env:\KIMI_CODE_HOME
```

Expected: `managed:kimi-code  type=kimi  models=1  source=oauth`. Run under BOTH `powershell.exe` and `pwsh` — 0.16.1's lock defect was green on one interpreter and broken on the other. Then re-run against the same path and confirm it REFUSES.

- [ ] **Step 6: Commit**

```bash
git add tools/new-kimi-lane-home.ps1 evals/multi-model-verify/test_kimi_lane_home.py
git commit -m "add the per-debate kimi-code lane home builder"
```

---

### Task 3: Probe the five unknowns that gate design claims

Five, not three. Revision 1 referenced an encoding probe in a later task that it never defined, and never checked which flags a resume actually accepts.

**Files:**
- Create: `docs/superpowers/plans/rounds/2026-07-31-kimi-code-swap/probe-record-2.md`

**Interfaces:**
- Consumes: `tools/new-kimi-lane-home.ps1` from Task 2.
- Produces: five settled answers. Task 4 uses the subagent answer, Task 6 uses the skills-dir, effort, thinking and resume-flag answers, Task 9 uses the encoding answer.

Build one home for the whole task: `$h = pwsh -File tools/new-kimi-lane-home.ps1 -Path "<fresh scratch>/probe2-home" -Model "<canonical id>"`, then set `$env:KIMI_CODE_HOME = $h` for every probe below.

- [ ] **Step 1: Probe whether `--skills-dir` suppresses a planted project skill**

Plant a canary at `<ws>/.kimi-code/skills/canary/SKILL.md` whose description and body both instruct the model to begin every reply with `CANARY-FIRED`. Dispatch with `--skills-dir <home>/skills`, then again WITHOUT it, and compare. Read the reply AND grep the session `wire.jsonl` for `canary`.

Repeat with the canary at `<ws>/.agents/skills/canary/SKILL.md`, because the client documents both roots and suppressing one proves nothing about the other.

Verdict to record: does `--skills-dir` suppress BOTH project roots. If it suppresses neither or only one, it is a mitigation and Task 6's contract text must say so, with preflight-3 remediation carrying the load instead.

- [ ] **Step 2: Probe whether `subagents: []` empties the catalog**

Dispatch any one-line prompt with an agent file carrying `subagents: []`, then read:

```powershell
Get-Content "$h/sessions/wd_*/session_*/state.json" | ConvertFrom-Json |
  ForEach-Object { $_.agentProfileCatalog.profiles[0].subagents }
```

Expected if it works: an empty array. The default observed without the key was `agent, coder, explore, plan, parallax-readonly-reviewer`.

If it does NOT empty: record that, and Task 4 must state the negative branch — the lane relies on `Agent` and `AgentSwarm` being denied, which is one control rather than two, and the debate record says so.

- [ ] **Step 3: Probe whether the home's effort pin actually overrides**

Both the home config and the model default currently read `high`, so agreement proves nothing. Rebuild the home with `-Effort low`, dispatch one prompt, and read:

```powershell
Select-String "llm config" "$h/sessions/wd_*/session_*/logs/kimi-code.log"
```

Expected if the pin works: `thinkingEffort=low`. If it still reads `high`, effort is provider-declared and NOT pinnable, and Task 6 must drop the "verifiable by construction" claim for effort.

- [ ] **Step 4: Probe for a differentiating signal for thinking-enabled**

The evidence rule verifies `thinkingEffort` but nothing proves `[thinking] enabled = true` took effect — a value that is always present proves nothing about the setting. Build a second home with `enabled = false`, dispatch the same prompt to each, and diff the per-session log and `wire.jsonl` for any field that differs (`thinkingKeep` on `llm.request` is the first candidate).

Record the differentiating field, or record that none exists. If none exists, Task 6 must NOT claim thinking is runtime-verified; it is config-asserted only, and the record says which.

- [ ] **Step 5: Probe which flags a resume accepts**

Measured so far: `--agent-file` is rejected with `--session`. Untested: `-m`, `--skills-dir`, `--add-dir`. Anything a resume ACCEPTS can be re-pinned for free, and free defence in depth against a future release that changes inheritance should be taken.

For each of `-m`, `--skills-dir`: run a resume carrying it and record whether the call is accepted, and whether the resulting `llm.request` still shows the canonical values.

- [ ] **Step 6: Probe the cp1252 output hazard**

kimi-cli was Python and raised `UnicodeEncodeError` AFTER the model answered, losing a paid round on the way to disk. kimi-code is a Node binary, which should write UTF-8 regardless of console codepage, but should is not measured.

From a console forced to cp1252 (`chcp 1252`), dispatch a prompt asking the reviewer to reply with an em-dash, an arrow and a non-Latin character, redirecting stdout to a file. Confirm the file holds the characters and the process exits 0.

If a hazard exists, Task 9 keeps a guard describing THIS client instead of deleting the section.

- [ ] **Step 7: Confirm the freshness observation directly**

The whole of Task 6's freshness rule rests on the files being cumulative. Confirm it rather than inferring it from revision 1's record: capture `(Get-Content wire.jsonl).Count` and the log's byte length, run a resume, and capture both again. Record both pairs.

- [ ] **Step 8: Write the record and clean up**

Create `probe-record-2.md` with, for each of the seven steps: the exact command, the exact output, and a one-line verdict. State every negative answer as a constraint later tasks must honour.

Then `Remove-KimiLaneHome -Path <probe2-home>` and confirm the credential copy is gone.

- [ ] **Step 9: Commit**

```bash
git add docs/superpowers/plans/rounds/2026-07-31-kimi-code-swap/probe-record-2.md
git commit -m "probe skill suppression, subagents, effort, thinking, resume flags and encoding"
```

---

### Task 4: The agent file

**Files:**
- Create: `skills/multi-model-verify/references/kimi-reviewer-agent.md`
- Delete: `skills/multi-model-verify/references/kimi-reviewer-agent.yaml`
- Delete: `skills/multi-model-verify/references/kimi-reviewer-system.md`
- Modify: `evals/multi-model-verify/test_backup_lane.py:14-15, 20-29, 41-43, 64-72, 75-77`

**Interfaces:**
- Consumes: Task 3's subagent verdict.
- Produces: `AGENT_MD`, `ALLOWLIST`, `DENYLIST` in `test_backup_lane.py`, used by Task 5's validator tests and Task 6's pins.

- [ ] **Step 1: Rewrite the test constants**

Replace line 14-15 with `AGENT_MD = REFS / "kimi-reviewer-agent.md"`, and lines 20-29 with:

```python
ALLOWLIST = ["Read", "Grep", "Glob", "ReadMediaFile", "TodoList"]
# Every built-in tool on 0.31.1 that is NOT in the allowlist. CronList was
# missing from revision 1, which left one tool neither allowed nor denied.
DENYLIST = ["Bash", "Write", "Edit", "WebSearch", "FetchURL",
            "EnterPlanMode", "ExitPlanMode", "Agent", "AgentSwarm",
            "AskUserQuestion", "Skill", "TaskList", "TaskOutput",
            "TaskStop", "CronCreate", "CronList", "CronDelete"]
```

- [ ] **Step 2: Rewrite the artifact and allowlist tests**

Replace `test_backup_artifacts_exist` (41-43):

```python
def test_backup_artifacts_exist():
    for p in (BACKUP_LANE, AGENT_MD):
        assert p.is_file(), str(p)
    assert not (REFS / "kimi-reviewer-agent.yaml").exists()
    assert not (REFS / "kimi-reviewer-system.md").exists()
```

Replace `test_agent_yaml_allowlist_exact` (64-72):

```python
def test_agent_allowlist_and_denylist_exact():
    """Exact LIST equality: extra, missing, or reordered entries all fail.
    Omitting `tools:` entirely means ALL tools on this client, so a silent
    parse failure is PERMISSIVE - which is why the denylist exists too."""
    import re
    body = _read(AGENT_MD)
    tools = re.search(r"^tools:\n((?:  - \w+\n)+)", body, re.M)
    assert tools
    assert [t.strip("- ").strip()
            for t in tools.group(1).strip().splitlines()] == ALLOWLIST
    denied = re.search(r"^disallowedTools:\n((?:  - \w+\n)+)", body, re.M)
    assert denied
    assert [t.strip("- ").strip()
            for t in denied.group(1).strip().splitlines()] == DENYLIST


def test_the_two_lists_together_cover_every_known_tool():
    """The denylist defends only against tools it NAMES. Stating that
    explicitly is the point: a client release adding a tool leaves it
    neither allowed nor denied, and only the allowlist would contain it.
    This test is what makes a new tool visible at upgrade time."""
    assert not (set(ALLOWLIST) & set(DENYLIST))
    assert len(ALLOWLIST) + len(DENYLIST) == 22


def test_agent_empties_the_subagent_list():
    """Probed: `subagents` defaults to ALL, including `coder`. That was
    inert only because Agent and AgentSwarm are denied. Relying on the
    coincidence of two controls is not a control."""
    assert "subagents: []" in _read(AGENT_MD)
```

Replace the file tuple at 75-77 with `for p in (BACKUP_LANE, AGENT_MD):`.

- [ ] **Step 3: Run tests to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py -k "artifacts or allowlist or subagent or known_tool" -v`
Expected: FAIL — the file does not exist.

- [ ] **Step 4: Write the agent file**

Create `skills/multi-model-verify/references/kimi-reviewer-agent.md` with frontmatter listing `name: parallax-readonly-reviewer`, a description, `tools:` in ALLOWLIST order, `disallowedTools:` in DENYLIST order, and `subagents: []`. The body is the exact former contents of `kimi-reviewer-system.md`, unchanged — do not reword it, because Task 6's evidence rule compares the wire log's recorded `systemPrompt` against this body byte for byte.

If Task 3 Step 2 found that `subagents: []` does NOT empty the catalog, still write the key, and add a line to the debate-record guidance in Task 6 stating that subagent containment rests on the `Agent`/`AgentSwarm` denial alone.

- [ ] **Step 5: Delete the superseded pair**

```bash
git rm skills/multi-model-verify/references/kimi-reviewer-agent.yaml skills/multi-model-verify/references/kimi-reviewer-system.md
```

- [ ] **Step 6: Run the tests**

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py -k "artifacts or allowlist or subagent or known_tool or backslash" -v`
Expected: PASS.

- [ ] **Step 7: Re-run the write-probe against the committed file**

Build a fresh home, run the marker-creation prompt with the committed agent file and `--skills-dir`, from a throwaway git workspace. PASS requires all three: explicit refusal in the reply, marker absent on disk, and `git -c core.quotepath=false status --porcelain --ignored -uall` unchanged from baseline. Anything else means the lane is BROKEN — stop the plan. Then confirm `state.json` shows the expected `subagents` value and remove the home.

- [ ] **Step 8: Commit**

```bash
git add skills/multi-model-verify/references/kimi-reviewer-agent.md evals/multi-model-verify/test_backup_lane.py
git commit -m "replace the kimi reviewer agent pair with one markdown agent file"
```

---

### Task 5: The evidence validator and its fixtures

Revision 1 promised fixtures and a parser in the design's Testing section and delivered neither — it pinned Markdown prose and called that coverage. A rule that is only prose is executed by a human reading it, differently each time. This task makes it a script with tests.

**Files:**
- Create: `tools/read-kimi-round-evidence.ps1`
- Create: `evals/multi-model-verify/fixtures/kimi-round/wire-clean.jsonl`
- Create: `evals/multi-model-verify/fixtures/kimi-round/wire-resumed.jsonl`
- Create: `evals/multi-model-verify/fixtures/kimi-round/log-clean.txt`
- Create: `evals/multi-model-verify/test_kimi_round_evidence.py`

**Interfaces:**
- Consumes: `ALLOWLIST` and `DENYLIST` from Task 4; the freshness measurements from Task 3 Step 7.
- Produces: `tools/read-kimi-round-evidence.ps1 -SessionDir <dir> -WireOffset <n> -LogOffset <n> -Model <id> -Effort <level> -AgentFile <path> -BriefFile <path> -Json`. Exits 0 and prints `{"status":"clean",...}` only when every check passes; exits non-zero with `"status":"failed"` and a `reason` otherwise. Task 6's contract text cites this script.

- [ ] **Step 1: Capture the fixtures**

From the Task 3 probe home, copy one clean round's `wire.jsonl` and per-session `kimi-code.log` into the fixtures directory, then hand-normalize them: replace absolute user paths with `C:/fixture/...`, and replace the session id with a fixed placeholder. The repo is PUBLIC and raw captures carry the user's home layout — only hand-normalized synthetic fixtures are committed, the same rule the codex probe fixtures follow.

`wire-resumed.jsonl` is the same session AFTER a resume, so it holds two rounds' records and is what the freshness tests run against.

- [ ] **Step 2: Write the failing tests**

Create `evals/multi-model-verify/test_kimi_round_evidence.py` covering, at minimum, one test each for:

- a clean fresh round returns `status: clean`
- a clean resumed round with a correct `-WireOffset` returns `status: clean`
- a resumed round with `-WireOffset 0` FAILS, because round 1's records would otherwise satisfy it — the stale-evidence case, and the reason this script exists
- a missing session directory fails with a named reason
- a missing `tools.set_active_tools` record fails
- a duplicated `llm.request` record inside one slice fails
- a malformed (non-JSON) line inside the slice fails rather than being skipped
- `names` unequal to the allowlist fails
- `disallowedNames` unequal to the denylist fails
- `modelAlias`, `thinkingEffort` or `provider` unequal fails
- `toolCount` unequal to the allowlist length fails
- a `systemPrompt` that differs from the agent file's body fails
- a `turn.prompt` whose text does not hash to the brief's hash fails
- a wire file SHORTER than `-WireOffset` fails as truncation rather than being read from zero

Each test asserts on the `status` and the `reason` field, not on an exact message string, so the invariant is pinned and the wording stays free.

- [ ] **Step 3: Run tests to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_kimi_round_evidence.py -v`
Expected: FAIL, all — the script does not exist.

- [ ] **Step 4: Write the validator**

Create `tools/read-kimi-round-evidence.ps1`. Rules it must implement, in order:

1. If `-SessionDir` is absent or unreadable: fail, reason `session-dir-missing`.
2. Read `agents/main/wire.jsonl`. If its line count is LESS than `-WireOffset`, fail with reason `wire-truncated` — and specifically do NOT re-read from zero. Same for the log against `-LogOffset`.
3. Take only lines past `-WireOffset` and log bytes past `-LogOffset`. This slice is the round.
4. Any line in the slice that is not parseable JSON: fail, reason `wire-malformed`.
5. Require EXACTLY ONE of each of `config.update` carrying `profileName`, `tools.set_active_tools`, `llm.tools_snapshot` and `llm.request` in the slice. Zero or more than one: fail, reason `record-count`.
6. Compare every value: `profileName` and `systemPrompt` against `-AgentFile`'s parsed name and body; `names`/`disallowedNames` against the agent file's two lists; the snapshot's tool names against the allowlist; `modelAlias`, `provider`, `thinkingEffort` against `-Model`, the canonical provider and `-Effort`; the log slice's `llm config` line's `toolCount` against the allowlist length.
7. Hash the concatenation of every `turn.prompt` `input[]` element's `text` field, UTF-8, with CRLF normalized to LF, and compare to the SHA-256 of `-BriefFile` normalized identically. Mismatch: fail, reason `brief-hash`.
8. On success emit `status: clean` plus `toolsHash`, `systemPromptHash`, and the new wire and log offsets, so the caller can pass them as the NEXT round's offsets.

- [ ] **Step 5: Run the tests**

Run: `python -m pytest evals/multi-model-verify/test_kimi_round_evidence.py -v`
Expected: PASS, all.

- [ ] **Step 6: Commit**

```bash
git add tools/read-kimi-round-evidence.ps1 evals/multi-model-verify/test_kimi_round_evidence.py evals/multi-model-verify/fixtures/kimi-round
git commit -m "add an executable validator for kimi-code round evidence"
```

---

### Task 6: Rewrite the lane's transport and evidence contract

**Files:**
- Modify: `skills/multi-model-verify/references/backup-lane.md:18-140`, `:159-198`
- Modify: `evals/multi-model-verify/test_backup_lane.py:80-257`
- Modify: `evals/multi-model-verify/test_contract_coverage.py:624-648`

**Interfaces:**
- Consumes: everything from Tasks 2-5, plus all five probe verdicts.
- Produces: regions `lane-home-isolation`, `round-freshness-boundary`, `per-round-session-evidence`, `evidence-hash-continuity`, `brief-hash-binding`, `resume-inheritance`.

- [ ] **Step 1: Update DECLARED_REGIONS first**

Remove the seven: `rotation-guard-detection`, `rotation-guard-disposition`, `rotation-guard-identity`, `session-block-attribution`, `session-block-kind`, `session-block-residual`, `lane-lock`. Add the six named above, with a comment recording that the freshness region is the surviving half of the deleted offset rule.

- [ ] **Step 2: Run the coverage test to verify it fails**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -k declared -v`
Expected: FAIL both directions — six declared and absent, seven present and undeclared.

- [ ] **Step 3: Rewrite Transport**

Replace `## Transport` (lines 18-43). It must contain, as prose plus four marked regions:

- The absolute-path rule and the floor. The dispatch and resume command lines use `<kimi-code-binary>` as the placeholder, NOT a bare `kimi`, so the pin and the instruction agree. Revision 1 said "absolute path" in prose and then pinned a bare-name command.
- Region `lane-home-isolation`: build once before round 1 with `tools/new-kimi-lane-home.ps1`, set `KIMI_CODE_HOME` on every call of the debate, the two independent reasons (hooks on the approval path; effort and thinking having no CLI flag), and that an unbuildable home or missing credential makes the lane UNAVAILABLE. Say per-DEBATE, not per-round. Remove the home when the debate ends, because it holds a copied credential.
- Dispatch line: `<kimi-code-binary> -m <canonical-backup-model-id> --agent-file <plugin-checkout>/skills/multi-model-verify/references/kimi-reviewer-agent.md --skills-dir <debate-home>/skills -p "<the whole brief>"`, run with the working directory set to the review mirror.
- Resume line: `<kimi-code-binary> --session <session-id> -p "<rebuttal>"`, plus whichever of `-m` and `--skills-dir` Task 3 Step 5 found a resume ACCEPTS — re-pin those, because free defence in depth against a future release changing inheritance is worth taking.
- Region `resume-inheritance`: what a bare resume was measured to inherit ON 0.31.1, that a wrong-directory resume is refused, that `--agent-file` is rejected with a resume, and that this observation is VERSION-BOUND — which is why the floor exists and why anything re-pinnable is re-pinned. It must not read as an indefinite guarantee.
- The brief is passed INLINE, never planted as a file with a pointer, because the hash rule can only detect truncation if the recorded prompt IS the brief. State the oversized fallback: if a brief ever exceeds what the inline transport carries, that is a transport failure to be diagnosed, not a reason to switch silently to a pointer whose hash proves nothing.

- [ ] **Step 4: Rewrite Per-round evidence**

Replace lines 45-139. It must contain:

- Region `round-freshness-boundary`, the heart of this revision:

  ```
  The session's log and wire transcript are CUMULATIVE: a resumed round
  appends to the same files, so round 1's records remain able to satisfy
  a later round's checks. Before every call capture the wire transcript's
  line count and the session log's byte length, and after the call read
  ONLY past both. A fresh call's session directory must not exist
  beforehand, and its captured offsets are zero. If either file is
  SHORTER afterwards than the captured offset, or absent, it was replaced
  and every position from the earlier measurement is meaningless: that is
  a route-attribution failure and specifically not a reason to re-read
  from zero, because the replacement's opening records may belong to any
  round while looking like evidence.
  ```

  This is the surviving half of the deleted byte-offset rule. Per-session files removed its cross-session job, not its per-call one.

- Region `per-round-session-evidence`: run `tools/read-kimi-round-evidence.ps1` with the captured offsets after every call, and require `status: clean`. Enumerate what it checks so the contract does not depend on reading the script. State that a missing session directory, a missing or duplicated record, an unreadable file, a malformed line, or any inequality is a route-attribution failure: the reply is DISCARDED unread and the failure goes to the fallbacks.md consent gate.

- Region `evidence-hash-continuity`, which revision 1 left as unmarked prose that pinned only two fragments: record `toolsHash` and `systemPromptHash` in round 1, require every later round of the debate to match, and record BOTH VALUES IN THE DEBATE RECORD. They are deliberately not pinned to a literal in this repo, because they cover tool schemas that any client release may reword, and a committed literal would fail every round for a reason that is not a route problem. Recording them in the record is what makes a client upgrade's change visible instead of silently rebaselined at the next round 1.

- Region `brief-hash-binding`: hash the brief before dispatch and require the recorded prompt to match. Specify the canonicalization exactly — UTF-8, CRLF normalized to LF, over the concatenation of every `turn.prompt` `input[]` element's `text` field — because revision 1 said "hashes to the same value" while its own evidence matched only after newline normalization, which is an undefined step a driver would have to invent.

- Prose, unmarked: why positive equalities beat the old `Loaded tools:` grep, stated NARROWLY. A failed allowlist does not necessarily change the effective tool set, since the denylist may exclude the same tools by name; what the check actually guarantees is that the CONFIGURED lists and the resolved snapshot are all compared against committed text, so a divergence in any of them surfaces. Revision 1 overclaimed here.

- The client-side vocabulary rule, unchanged.

- [ ] **Step 5: Rewrite the Client config surface section**

Replace the effort bullet with one describing the home-written pin and its per-call confirmation, hedged by Task 3 Step 3's verdict. Replace the `merge_all_available_skills` bullet with the skill-discovery bullet naming all four roots — `.kimi-code/skills/`, `.agents/skills/`, `$KIMI_CODE_HOME/skills/`, `~/.agents/skills/` — noting that the home relocation does not cover `~/.agents/skills/`, and stating `--skills-dir`'s measured effect from Task 3 Step 1. If it was not proven to suppress both project roots, say so and route the load to preflight-3 remediation.

Add the thinking sentence per Task 3 Step 4: name the differentiating field if one exists, or state plainly that thinking-enabled is config-asserted and not runtime-verified.

- [ ] **Step 6: Rewrite the pins**

Replace `test_backup_lane_dispatch_and_resume_pins` and `test_backup_lane_evidence_pins` with one test per region, each asserting the region's text WHOLE via `_norm`, plus a `test_deleted_machinery_does_not_return` holding absence checks for `kimi-lane-lock.ps1`, `Rotation guard` and `Created new session:`. Absence checks lock nothing under the grammar and are restoration guards, not pins — say so in the comment so a later reader does not mistake them for coverage.

- [ ] **Step 7: Run the whole suite**

Run: `python -m pytest evals -q`
Expected: PASS. `test_declared_regions_match_the_documents` and `test_every_marked_region_is_locked_by_a_pin` are the two that prove the region edit landed. A region reporting uncovered means the pin does not contain it WHOLE — fix the pin, not the region.

- [ ] **Step 8: Commit**

```bash
git add skills/multi-model-verify/references/backup-lane.md evals/multi-model-verify/test_backup_lane.py evals/multi-model-verify/test_contract_coverage.py
git commit -m "rewrite the backup lane's transport and evidence for kimi-code"
```

---

### Task 7: Delete the lane lock

**Files:**
- Delete: `tools/kimi-lane-lock.ps1`, `evals/multi-model-verify/test_kimi_lane_lock.py`

**Interfaces:**
- Consumes: Task 6's removal of the `lane-lock` region.
- Produces: nothing.

- [ ] **Step 1: Find every reference**

Run: `Select-String -Path (Get-ChildItem -Recurse -File -Exclude *.git*) -Pattern "kimi-lane-lock" -List`
PowerShell, not `grep` — the declared stack for this repo's tooling.

- [ ] **Step 2: Delete**

```bash
git rm tools/kimi-lane-lock.ps1 evals/multi-model-verify/test_kimi_lane_lock.py
```

- [ ] **Step 3: Remove surviving prose references**

Edit each remaining non-`docs/**` file the search found, deleting the lock sentence rather than rewording it.

- [ ] **Step 4: Verify**

Re-run the search. Expected: only `docs/**` matches, which are historical records and stay.

- [ ] **Step 5: Run the whole suite**

Run: `python -m pytest evals -q`
Expected: PASS, with 41 fewer tests collected.

- [ ] **Step 6: Commit**

Stage by explicit path — list each deleted and edited file. Do NOT use `git add -u`.

```bash
git add tools/kimi-lane-lock.ps1 evals/multi-model-verify/test_kimi_lane_lock.py <each edited file>
git commit -m "delete the kimi lane lock, which guarded a shared log that no longer exists"
```

---

### Task 8: Extend preflight 3 to `.kimi-code/`

**Files:**
- Modify: `skills/multi-model-verify/SKILL.md:61-77`
- Modify: `tools/new-review-mirror.ps1` (enumeration pathspecs)
- Modify: `evals/multi-model-verify/test_review_mirror.py`

**Interfaces:**
- Consumes: Task 3 Step 1's verdict on which discovery roots are live.
- Produces: an enumeration pathspec list including `.kimi-code/*`.

- [ ] **Step 1: Write the failing test**

```python
def test_enumeration_sweeps_the_kimi_code_back_channel():
    """kimi-code auto-discovers agents from .kimi-code/agents/ and skills
    from .kimi-code/skills/ in the REVIEWED tree - the same class as
    codex's .agents/skills/ advertisement, on the backup lane's side."""
    body = (REPO / "tools" / "new-review-mirror.ps1").read_text(
        encoding="utf-8")
    assert "'.kimi-code/*'" in body
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -k kimi_code -v`
Expected: FAIL.

- [ ] **Step 3: Add the pathspec and update the preflight text**

Add `'.kimi-code/*'` to the `git ls-files --cached --others` pathspec list in `tools/new-review-mirror.ps1`, and extend SKILL.md's preflight-3 sentence and listing command to name it. Keep the existing root-anchoring behaviour and the existing note about the depth asymmetry, which applies identically to the new pathspec.

**Both branches, stated:** if Task 3 Step 1 found `--skills-dir` suppresses both project roots, this sweep is defence in depth and the text says so. If it does not, this sweep is the PRIMARY control for the reviewed tree's skills and the text must say that instead — a mitigation described as a control is the failure this repo removes.

- [ ] **Step 4: Run the tests**

Run: `python -m pytest evals -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/new-review-mirror.ps1 skills/multi-model-verify/SKILL.md evals/multi-model-verify/test_review_mirror.py
git commit -m "sweep .kimi-code back-channels in preflight 3"
```

---

### Task 9: Declarations, failure routing and the doctor

**Files:**
- Modify: `skills/multi-model-verify/references/model-prompting-notes.md:298-330`
- Modify: `skills/multi-model-verify/references/fallbacks.md:152-179`
- Modify: `commands/doctor.md`, `README.md`
- Modify: `evals/multi-model-verify/test_backup_lane.py:46-61, 489-512`

**Interfaces:**
- Consumes: Task 3 Step 6's encoding verdict; Task 6's contract.
- Produces: canonical provider and effort declarations that Task 5's validator arguments are checked against.

- [ ] **Step 1: Add the two missing declarations**

Revision 1's evidence rule required a "canonical provider" and a "canonical effort" for the backup lane, and neither was declared anywhere — an equality with no single source. Add to the backup block in `model-prompting-notes.md`, beside the existing model id:

```
Canonical backup provider: `kimi`

Canonical backup reasoning effort: `high`

Canonical backup thinking declaration: `[thinking] enabled = true`
```

Replace the old `Canonical backup thinking flag: --thinking` line. Add one sentence noting this client has no thinking or effort flag, so both are written into the debate home and confirmed per call from the session log.

- [ ] **Step 2: Update the declaration test**

In `test_backup_lane.py`, update `test_notes_backup_declarations` to assert all four backup declarations, keeping the existing primary-parser ordering assertions untouched — those protect the primary lane's runtime parsers and are not part of this change.

- [ ] **Step 3: Rewrite the stale fallbacks entries**

`fallbacks.md:152-161` names "offset rule in backup-lane.md" and a rotation exception; `:162-179` requires "all four flags re-pinned AND the UTF-8 environment forced". Both describe machinery this cycle deletes.

- Rewrite the route-attribution entry to name the freshness boundary and the validator instead of the offset rule. Keep the disposition unchanged: no retry, reply DISCARDED unread, consent gate. Keep the transient-member carve-out only if a transient member still exists under the new rule — a file replaced under the call still qualifies, so it does.
- Rewrite or delete the `output-encoding` entry per Task 3 Step 6. If no hazard was measured, delete the class and its `fallbacks.md` entry, and remove the four-flags-re-pinned recovery. If a hazard was measured, keep the class and describe THIS client's failure and recovery.

Note that `test_fallbacks_backup_wiring` currently pins the old rotation sentence at `test_backup_lane.py:546`; that pin must be rewritten in the same step or the suite fails.

- [ ] **Step 4: Update the encoding test**

Replace `test_output_encoding_class_is_wired` with a test matching whichever branch Task 3 Step 6 selected, asserting the Python guard is gone from the lane either way.

- [ ] **Step 5: Update the doctor and the README**

Rewrite `commands/doctor.md`'s backup-lane section to check: the binary at the absolute path exists and reports at or above the floor; `provider list` under a freshly built home reports `source=oauth`; and the committed agent file's allowlist is present. Drop every reference to `kimi_cli` module imports, `--quiet`, `--thinking` and the lane lock. Fix any `README.md` row naming the deleted yaml or system file.

- [ ] **Step 6: Run the full gate**

All four commands from Global Constraints.
Expected: all PASS.

- [ ] **Step 7: Commit**

```bash
git add skills/multi-model-verify/references/model-prompting-notes.md skills/multi-model-verify/references/fallbacks.md commands/doctor.md README.md evals/multi-model-verify/test_backup_lane.py
git commit -m "declare the backup lane's provider and effort, and retire the stale failure routing"
```

---

### Task 10: Close the backlog and ship

**Files:**
- Modify: `docs/superpowers/plans/2026-07-27-0150-backlog.md`, `.claude-plugin/plugin.json`, `.claude/state/handoff.md`

- [ ] **Step 1: Run the opt-in behavioral suite**

Run: `python evals/tools/run_behavioral_evals.py`
Expected: PASS. Record any failing case by name; do not proceed without deciding explicitly whether it is a real regression.

- [ ] **Step 2: Run a real backup-lane round end to end**

The lane has not reviewed anything until it has. Run one round against a small real diff: build a home, build a mirror, dispatch, capture offsets, run the validator, confirm `status: clean`, then resume for a second round and confirm the validator still reports clean against the SECOND round's offsets and not round 1's. Retain the evidence under `docs/superpowers/plans/rounds/2026-07-31-kimi-code-swap/`.

This is also what item 15 requires before `kimi-cli` may be removed in a later cycle.

- [ ] **Step 3: Mark the backlog items**

Item 13 DONE, item 8 DONE (brief-hash rule; truncation did not reproduce at 9033 characters), item 16 GONE (the lock it describes no longer exists), item 6's residual answered. Item 15 gains a note: the installer renamed the binary to `kimi-legacy.exe`, so the shadowing hazard is gone and the rollback survives; removal still deferred. Update the `**Status.**` line.

- [ ] **Step 4: Bump the version and rewrite the handoff**

`.claude-plugin/plugin.json` to `0.18.0`. Rewrite `.claude/state/handoff.md`'s "What just shipped" and "What is next" with this cycle's facts, including the three that are not derivable from the code: per-session files are cumulative so the offset rule's freshness half survived while its attribution half was deleted; the real kimi-code home carried seven Orca lifecycle hooks including PermissionRequest; and a bare resume inherits everything while a wrong-directory resume is refused, the inverse of the old rule. Update the standing-rules list — remove the `PYTHONIOENCODING` and lane-lock bullets, add the absolute-path binary rule and the debate-home rule.

- [ ] **Step 5: Final gate**

All four gate commands, plus `pwsh -File evals/tools/drift_statemachine_tests.ps1`.
Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add docs/superpowers/plans/2026-07-27-0150-backlog.md .claude-plugin/plugin.json .claude/state/handoff.md
git commit -m "0.18.0: close backlog items 13, 8 and 16"
```

- [ ] **Step 7: Update the installed cache**

Checkout edits are not live. Run `claude plugin update parallax@parallax`, then restart the session, because `skills/`, `commands/` and `tools/` all changed.

---

## Self-review notes

Every FIX from Sol round 1 maps to a step: freshness to Task 6 Step 4's new region and Task 5's stale-evidence tests; the missing validator and fixtures to Task 5; the hash rule's region and recording to Task 6 Step 4; brief canonicalization and the oversized fallback to Task 6 Steps 3-4; the subagent negative branch to Task 4 Step 4; the narrowed denylist claim to Task 4 Step 2's coverage test; per-debate naming and thinking evidence to Task 3 Step 4 and Task 6; credential handling to Task 2; resume re-pinning to Task 3 Step 5 and Task 6 Step 3; the `-r` help assertion, the state-machine stubs, the model-literal sweep, `git add -u`, `grep`, the dangling encoding probe and the Task 2/3 ordering to Tasks 1, 2, 3, 7 and 9.

Two of Sol's fixes are declined with reasons stated in Task 6 Step 4 and Task 3 Step 5: binding `toolsHash` to a client version, which reintroduces the brittleness the rule exists to avoid and is replaced by recording both hashes in the debate record; and a sacrificial resume write-probe every debate, which spends a call per debate against a hypothetical future-version risk, replaced by re-pinning every flag a resume accepts plus the version floor.

One defect Sol did not find is fixed in Task 4 Step 2: `CronList` was in neither list, so one built-in tool was neither allowed nor denied.
