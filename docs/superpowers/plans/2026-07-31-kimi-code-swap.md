# kimi-code Backup Lane Swap Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the backup reviewer lane from `kimi-cli` 1.49.0 to kimi-code 0.31.1, delete the machinery that per-session logging makes unnecessary, and keep the parts of it that per-session logging does NOT replace.

**Architecture:** Each debate runs under an isolated `KIMI_CODE_HOME` built from a committed config template plus a copied credential, with one Markdown agent file carrying the tool allowlist. An executable validator reads route evidence from that debate's own session directory. Those files are cumulative and their records split into two classes — session-scoped, written once at session creation, and per-call — so the validator checks each class where it actually appears, behind a freshness boundary that proves the prefix was not replaced.

**Tech Stack:** PowerShell 5.1+ and 7 (both hosts), Python 3.12 + pytest, Markdown contract regions with the `contract:start`/`contract:end` checker.

## Revision history

- **r1** — first draft, unreviewed.
- **r2** — after Sol round 1 (10 FIX). Restored the freshness boundary that r1 deleted along with the offset rule; added a validator and credential handling.
- **r6, this one** — after Sol round 5, which found ONE structural flaw and it was created by r5's own fix. Binding the prior state to `sessionDir` and `sessionId` made the clean FRESH case impossible to instantiate: a fresh call's session does not exist until the client creates it during that call, so the pre-dispatch state could never carry those fields. Fresh and resume now have different identity semantics — a fresh state captures the session-directory INVENTORY and the validator requires exactly one new directory matching the id the client printed, while resume keeps the exact path-and-id comparison. Also fixed: the destructive removal test planted authorizing sentinels on the REAL user profile and a REAL drive root before exercising new deletion code, which would have destroyed what it was testing had the guard been defective; it now uses a subprocess with a temporary profile, a substituted drive, and cleanup in a `finally`. Two surviving "every flag" overclaims narrowed, the stale boundary wording replaced with `metadata`, and the sub-step numbering made unambiguous.
- **r5** — after Sol round 4 (1 PASS, 4 FIX). Sol WITHDREW its demand that the plan prescribe the validator's parsing algorithm, agreeing that an independently written test suite covering every observable invariant is the better specification. Fixed: a failed `--help` still ran the flag loop and emitted five findings describing nothing; an uncaught `--help` throw; `-PriorState` claiming a binding while carrying nothing identifying its session; destructive root guards never exercised with a well-formed sentinel; an unclear fault seam; step misnumbering; and eight missing test cases. Three overclaims narrowed: the floor is a lower bound and forces no re-probe; resume results hold for the four flags tested, not all flags; and record ORDER is now measured rather than assumed — a fresh slice opens with `metadata`, which is not what the rule first said.
- **r4** — after Sol round 3 (1 PASS, 5 FIX). `--skills-dir`-as-mitigation passed and is settled. Fixed: a tautological `KNOWN_TOOLS`; an uncallable `-Remove` (now parameter sets); an impossible drift stub (production resolves `kimi.exe` or `kimi.cmd`); a present-but-unusable binary falling into the "absent" note; a plantable bare-filename sentinel; the log protected by length while the wire got a hash; an undefined prefix-hash framing (offsets are now BYTES); an offset landing mid-call passing every check; and the uncompared second `config.update`, `permission.set_mode.mode`, and per-request hash identity. The validator now takes a single `-PriorState` object and enforces hash continuity itself.
- **r3** — after Sol round 2 (5 FIX) and a six-call measurement session recorded in `rounds/2026-07-31-kimi-code-swap/probe-record-2.md`. r2's central evidence rule was **measured to be wrong in both directions**: it fails a clean round 1 and every resumed round. Sol round 2's fourteen defects are fixed here, and three of its objections are resolved by measurement rather than argument.

Sol plan-debate session `019fb913-1b73-7ab0-961d-ff2ae3a6b4f7`. Round replies retained beside this plan.

## Global Constraints

- Design spec: `docs/superpowers/specs/2026-07-31-kimi-code-swap-design.md`. Measured evidence: `rounds/2026-07-31-kimi-code-swap/probe-record.md` and `probe-record-2.md`. **Every cardinality and flag claim below is measured; do not re-derive it from the client's docs, which do not state any of it.**
- Canonical backup model id is `kimi-code/k3-256k`, UNCHANGED. It may appear ONLY in `references/model-prompting-notes.md` and `evals/multi-model-verify/test_backup_lane.py`. `SWEEP_GLOBS` covers `tools/*.ps1`, so no script under `tools/` may carry the literal, not even as a parameter default.
- The binary is `~/.kimi-code/bin/kimi.exe`, 0.31.1, always invoked by ABSOLUTE PATH. Bare `kimi` is a PATH accident this cycle removes. The old CLI survives as `kimi-legacy.exe` (1.49.0) and is the rollback. Do NOT `pip uninstall kimi-cli`.
- `-r` is a HIDDEN alias absent from `--help`. The public resume flag is `-S/--session`. Any help-text assertion must use `--session`.
- Never `git add -A` and never `git add -u`. Stage by explicit path, every commit.
- Files under `skills/multi-model-verify/references/` are checked for the ABSENCE of backslashes. Use forward slashes in those files.
- Contract regions must sit WHOLE inside a single pin, and a pin is only one of the three clause forms in `CLAUDE.md`. Adding or removing a region means editing `DECLARED_REGIONS`.
- Tests change FIRST for every live-verified contract, then the skill text.
- Gate, all four, from the repo root:
  `python evals/tools/skill_lint.py skills/multi-model-verify --strict`
  `python evals/tools/skill_scanner.py skills`
  `python evals/tools/run_trigger_evals.py`
  `python -m pytest evals -q`
- The invariant governing every check: an unmade, failed, or unreadable measurement is never a clean one.

## Measured facts the plan is built on

Stated once, here, because five tasks depend on them.

**Record classes.** Session-scoped records are emitted ONCE, at session creation, and never again: `config.update` ×2 (first carries `profileName` and `systemPrompt`, second carries `modelAlias` and `thinkingEffort`), `tools.set_active_tools` ×1, `llm.tools_snapshot` ×1, `permission.set_mode` ×1. Per-call records: `turn.prompt` ×1, `llm.request` ×N where N tracks the tool loop (measured 4 on a fresh review, 2 on a resumed one), and exactly one new `llm config` line in the per-session log.

**`systemPromptChars` equals the agent file's body length exactly** (431 in every measured session). `toolCount` equalled the allowlist length on every call.

**Of the four flags tested with a resume**, `-m`, `--skills-dir` and `--add-dir` are accepted and `--agent-file` is REJECTED at parse time with `the agent is bound at session creation`. Nothing is established about flags outside that set.

**Record ORDER in a fresh session** is `metadata`, `config.update`, `tools.set_active_tools`, `config.update`, `permission.set_mode`, `turn.prompt`. A resumed call's slice opens with `turn.prompt`.

**`--skills-dir` changes nothing measurable** in this configuration: with two canary skills planted at both documented project roots, runs with and without it were identical and the reviewer reported `NONE` available. It is a mitigation, not a control.

**Effort is pinnable**: `default_effort = "low"` produced `thinkingEffort=low`. **Thinking-enabled is not observable**: `enabled = false` produced output identical to `true`.

**`subagents: []` resolves to an empty array.**

---

### Task 1: Repair drift watch, including its own test harness

`tools/check-drift.ps1` invokes bare `kimi` and asserts the help lists `--quiet`, `--thinking` and `-w`. Bare `kimi` now resolves to kimi-code, which has none of them, so drift watch currently reports findings that describe nothing. Its offline state-machine harness stubs the same dead surface and must move with it.

**Files:**
- Modify: `tools/check-drift.ps1:133-136`, `:197-216`
- Modify: `tools/drift-snapshot.json:4`
- Modify: `evals/tools/drift_statemachine_tests.ps1:110-117`, `:233`, `:243-276`, `:287-315`, `:686`, `:700-720`
- Test: `evals/multi-model-verify/test_backup_lane.py` (appended)

**Interfaces:**
- Consumes: nothing.
- Produces: `$kimiExe`, `$kimiVersion` in `check-drift.ps1`. Snapshot key stays `kimi`.

- [ ] **Step 1: Write the failing tests**

```python
DRIFT = REPO / "tools" / "check-drift.ps1"
STATEMACHINE = REPO / "evals" / "tools" / "drift_statemachine_tests.ps1"
KIMI_CODE_FLOOR = "0.31.1"


def test_drift_probes_the_new_cli_not_the_old_one():
    body = _read(DRIFT)
    assert '"--agent-file", "--skills-dir", "-m", "-p", "--session"' in body
    assert "--quiet" not in body
    assert "--thinking" not in body
    assert "import kimi_cli.tools.file" not in body


def test_drift_does_not_assert_a_hidden_alias():
    """`-r` works but is absent from --help on 0.31.1. Asserting it would
    manufacture the exact false finding this task removes."""
    assert '"-r"' not in _read(DRIFT)


def test_the_version_probe_can_actually_reach_its_failure_branch():
    """r2's floor check was unreachable: $kimiVersion was assigned only
    inside a successful numeric regex, so TryParse could never see a
    malformed value and the fail-closed branch was dead code. A check
    that cannot fail is the defect this whole task is repairing."""
    body = _read(DRIFT)
    assert "$kimiVersion = $kimiRaw" in body
    assert "KimiCodeFloor" in body
    assert KIMI_CODE_FLOOR in body


def test_the_production_lookup_accepts_a_cmd_stub():
    """A .cmd renamed .exe does not execute on Windows, so an absolute
    .exe-only lookup cannot be stubbed offline at all. Production
    therefore resolves either name in that directory - which is also true
    of real Windows CLIs - and the harness stubs the .cmd."""
    body = _read(DRIFT)
    assert "kimi.exe" in body
    assert "kimi.cmd" in body


def test_the_state_machine_stubs_moved_with_the_probe():
    body = _read(STATEMACHINE)
    assert "kimi_cli" not in body
    assert "--thinking" not in body
    # the production lookup is an absolute path under the fake profile,
    # not a PATH entry, so the harness must place the stub there or every
    # kimi scenario silently takes the "absent" branch and asserts nothing
    assert ".kimi-code" in body
    assert "--session" in body
    assert "KIMI_STUB_MODE" in body


def test_a_present_but_unusable_binary_is_a_finding_not_a_note():
    """r3 fixed the regex pre-filter but left a second path open: a binary
    that exists while --version fails or prints nothing still fell into
    the 'absent' note. Absent is a note; present-and-broken is a finding."""
    body = _read(DRIFT)
    assert "$versionExit" in body
    assert "did not report a usable version" in body
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py -k "drift or state_machine or hidden_alias or failure_branch" -v`
Expected: FAIL, all four.

- [ ] **Step 3: Resolve the binary and capture the version fail-closed**

Replace `tools/check-drift.ps1:133-136`:

```powershell
$kimiVersion = ""
$kimiRaw = ""
$versionExit = $null
$kimiExe = ""
$kimiBin = Join-Path $env:USERPROFILE ".kimi-code\bin"
# Either name: a real Windows CLI may ship as .exe or as a .cmd shim, and
# an .exe-only lookup is also impossible to stub offline, which is what
# left every state-machine kimi scenario asserting nothing.
foreach ($n in @("kimi.exe", "kimi.cmd")) {
    $candidate = Join-Path $kimiBin $n
    if (Test-Path $candidate) { $kimiExe = $candidate; break }
}
if ($kimiExe) {
    try {
        $kimiRaw = (& $kimiExe --version 2>&1 | Out-String).Trim()
        $versionExit = $LASTEXITCODE
    } catch { $versionExit = -1 }
    # Assign the RAW value. r2 filtered through a numeric regex first, so a
    # malformed version could never reach the floor check.
    $kimiVersion = $kimiRaw
}
```

Bare `kimi` is deliberately NOT a fallback: two CLIs have carried that name here, so a name-resolved probe can measure the wrong binary.

Three outcomes, kept distinct. No binary is a NOTE — the lane is optional. A binary present whose `--version` exits nonzero or prints nothing is a FINDING, not a note: something is installed and broken, which is not the same as nothing being installed. A usable version goes to the floor check.

- [ ] **Step 4: Replace check 2b**

```powershell
# --- check 2b (every run): kimi-code backup transport surface ------------------
# Short flags (-m/-p) substring-match inside long-flag help text; the long
# flags carry the real detection. `-r` is deliberately absent: it works but
# is a HIDDEN alias that never appears in --help, so asserting it would
# report a break that is not one. `kimi upgrade` self-updates, so the floor
# is checked as well as the version recorded.

$KimiCodeFloor = "0.31.1"

if (-not $kimiExe) {
    $notes += "kimi-code absent - backup-lane probes skipped (lane optional; primary unaffected)"
} elseif ($versionExit -ne 0 -or -not $kimiVersion) {
    $findings += "[CRITICAL] kimi-code is installed at $kimiExe but did not report a usable version (exit $versionExit) - an unmade version check is never a passing one; the backup lane is UNAVAILABLE"
} else {
    $kimiHelp = ""
    $helpExit = -1
    try {
        $kimiHelp = (& $kimiExe --help 2>&1 | Out-String)
        $helpExit = $LASTEXITCODE
    } catch { $helpExit = -1 }
    if ($helpExit -ne 0 -or -not $kimiHelp.Trim()) {
        # STOP here. Running the flag loop against missing or error output
        # emits five more findings that describe nothing - the same
        # false-finding class this task exists to remove.
        $findings += "[CRITICAL] kimi-code --help exited $helpExit or printed nothing - the transport surface could not be measured, so no flag conclusion is available"
    } else {
        foreach ($flag in @("--agent-file", "--skills-dir", "-m", "-p", "--session")) {
            $flagPattern = '(^|[\s,\[])' + [regex]::Escape($flag) + '($|[\s,\]=])'
            if (-not [regex]::IsMatch($kimiHelp, $flagPattern)) {
                $findings += "[CRITICAL] kimi-code --help ($kimiVersion) no longer lists $flag - the backup lane's transport commands are broken; update references/backup-lane.md"
            }
        }
    }
    $parsedFloor = $null
    $parsedSeen = $null
    $okFloor = [version]::TryParse($KimiCodeFloor, [ref]$parsedFloor)
    $okSeen  = [version]::TryParse(($kimiVersion -replace '^\D*', ''), [ref]$parsedSeen)
    if ($okFloor -and $okSeen) {
        if ($parsedSeen -lt $parsedFloor) {
            $findings += "[CRITICAL] kimi-code $kimiVersion is below the lane floor $KimiCodeFloor - the backup lane is UNAVAILABLE, not degraded; see references/backup-lane.md"
        }
    } else {
        $findings += "[CRITICAL] kimi-code version '$kimiVersion' is unparseable against floor $KimiCodeFloor - an unmade floor check is never a passing one"
    }
}
```

Note the three-way split: an ABSENT binary is a note; a PRESENT binary that cannot be measured is a finding; only a usable version reaches the floor. r2 collapsed all three into the note, which is how the failure branch became unreachable.

- [ ] **Step 5: Move the state-machine harness**

In `evals/tools/drift_statemachine_tests.ps1`:

- The harness builds stubs in `$StubDir` and puts them on PATH (`:110-117`). The production lookup is now an ABSOLUTE path under `$env:USERPROFILE`, so a PATH stub is invisible to it and every kimi scenario would take the "absent" branch. Create the stub at `<fake profile>/.kimi-code/bin/kimi.cmd`. This is why Step 3's lookup tries `kimi.exe` then `kimi.cmd`: a `.cmd` renamed `.exe` does not execute on Windows, so an `.exe`-only lookup cannot be stubbed offline at all, and real Windows CLIs legitimately ship either form. The scenarios already set `USERPROFILE` to the fake profile, so no new seam is introduced — in particular, no environment variable is added that could redirect the REAL lookup, which is the lock-stealing shape this repo has already been bitten by twice.
- **Verify the stub is actually reached** before trusting any scenario: run one and confirm the report contains a flag finding or a floor finding rather than the "absent" note. A green suite in which every kimi scenario silently skipped is the failure this task exists to remove, wearing a passing badge.
- Stub usage lines (`:243-276`): re-express in the new vocabulary, advertising `--session` and NOT `-S`, since the production regex matches `--session`. Keep each variant's existing dropped-flag difference so the scenarios still distinguish a full surface from a degraded one.
- Delete the `kimi_cli` import-probe branch and its forwarding comment at `:233`.
- Add a `KIMI_STUB_MODE` value that emits a BELOW-FLOOR version (e.g. `0.30.0`); the existing stub always emits `9.9.9` except on total failure, so the new floor scenario has nothing to trigger it.
- `:686`: keep the scenario asserting the vocabulary probe stays quiet on a flag-only drop, retargeted off `kimi_cli tool modules`.
- `:700-720`: replace the import-failure scenario with a below-floor scenario asserting `is below the lane floor`, and add one asserting the unparseable-version finding.

- [ ] **Step 6: Run the tests**

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py -k "drift or state_machine or hidden_alias or failure_branch" -v`
Expected: PASS.

- [ ] **Step 7: Snapshot, then run the state machine**

`tools/drift-snapshot.json:4` becomes `"kimi": "0.31.1",`.

Run: `pwsh -File evals/tools/drift_statemachine_tests.ps1`
Expected: ALL SCENARIOS PASS. Confirm in the output that the kimi scenarios exercised the probe rather than the absent branch — a green run where every kimi scenario skipped is the silent-skip failure this repo treats as worst.

- [ ] **Step 8: Commit**

```bash
git add tools/check-drift.ps1 tools/drift-snapshot.json evals/tools/drift_statemachine_tests.ps1 evals/multi-model-verify/test_backup_lane.py
git commit -m "point drift watch at kimi-code and move its state-machine harness"
```

---

### Task 2: Declare the lane's canonical values

Moved ahead of the validator, which compares against them. r2 had the validator requiring a "canonical provider" that no task ever declared.

**Files:**
- Modify: `skills/multi-model-verify/references/model-prompting-notes.md:298-315`
- Modify: `evals/multi-model-verify/test_backup_lane.py:46-61`

**Interfaces:**
- Produces: four backup declarations, read by Tasks 6 and 7.

- [ ] **Step 1: Update the declaration test**

In `test_notes_backup_declarations`, keep every existing primary-parser ordering assertion untouched — those protect the primary lane's runtime parsers — and add:

```python
    assert "Canonical backup provider: `kimi`" in notes
    assert "Canonical backup reasoning effort: `high`" in notes
    assert ("Canonical backup thinking declaration: `[thinking] enabled = true`"
            in notes)
    assert "Canonical backup thinking flag: `--thinking`" not in notes
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py -k notes_backup -v`
Expected: FAIL.

- [ ] **Step 3: Write the declarations**

Under the existing `Canonical backup reviewer model id` line, replace the `--thinking` flag line with the three above, plus this note:

```
This client has no thinking or effort flag. Both are written into the
debate home by tools/new-kimi-lane-home.ps1. Effort is confirmed per call
from the session log's `thinkingEffort` field; thinking-enabled is NOT
confirmable — measured 2026-07-31, `enabled = false` produced output
identical to `enabled = true` in both the log and the wire transcript, so
it is config-asserted only and the debate record says so.
```

Change the section heading to name kimi-code rather than kimi-cli.

- [ ] **Step 4: Run the test**

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py -k notes_backup -v`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add skills/multi-model-verify/references/model-prompting-notes.md evals/multi-model-verify/test_backup_lane.py
git commit -m "declare the backup lane's provider, effort and thinking values"
```

---

### Task 3: The debate home builder

Per-DEBATE, not per-round: built once before round 1 and used by every call of that debate, because the rounds of one debate are one session.

**Files:**
- Create: `tools/new-kimi-lane-home.ps1`
- Create: `evals/multi-model-verify/test_kimi_lane_home.py`

**Interfaces:**
- Consumes: nothing.
- Produces two PARAMETER SETS on `tools/new-kimi-lane-home.ps1`, because a globally mandatory `-Model` makes the removal form uncallable:
  - `Build` (default): `-Path <dir> -Model <id> [-Effort <level>]` — builds and prints the absolute path. `-Model` is mandatory WITHIN THIS SET and has no default.
  - `Remove`: `-Path <dir> -Remove` — deletes a home this script built, and takes no `-Model`.
  Exits non-zero on any refusal.

- [ ] **Step 1: Write the failing tests**

```python
"""Contract pins for the per-debate kimi-code lane home."""
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
BUILDER = REPO / "tools" / "new-kimi-lane-home.ps1"
SENTINEL = ".parallax-lane-home"


def _read(p):
    return p.read_text(encoding="utf-8")


def test_builder_exists():
    assert BUILDER.is_file(), str(BUILDER)


def test_model_is_mandatory_within_the_build_set_only():
    """SWEEP_GLOBS covers tools/*.ps1, so a parameter default carrying the
    canonical id would fail test_backup_literal_single_source. But a
    GLOBALLY mandatory -Model makes `-Remove` uncallable, so the two forms
    are separate parameter sets."""
    body = _read(BUILDER)
    assert 'DefaultParameterSetName = "Build"' in body
    assert 'ParameterSetName = "Build", Mandatory = $true)][string]$Model' in body
    assert "k3-256k" not in body


def test_builder_refuses_without_a_credential():
    assert "the lane is UNAVAILABLE" in _read(BUILDER)


def test_builder_refuses_a_reused_or_unsafe_destination():
    """A reused home carries stale sessions, which is exactly what the
    freshness rule exists to exclude, so reuse corrupts the evidence
    rather than merely being untidy."""
    body = _read(BUILDER)
    assert "destination already exists" in body
    assert "inside a git work tree" in body


def test_the_git_check_fails_closed():
    """r2 treated any nonzero `git rev-parse` as 'not in a work tree', so
    git being absent or erroring placed an OAuth credential in a repo."""
    body = _read(BUILDER)
    assert "$LASTEXITCODE" in body
    assert "could not determine" in body


def test_removal_is_callable_and_guarded():
    """r2 defined a function inside a script invoked with `pwsh -File`,
    which no caller can ever reach. Removal is a parameter set on the same
    script, and it refuses any directory this builder did not create.

    The sentinel's NAME is not the credential: a bare filename can be
    planted in any directory and would then authorize a recursive delete.
    It carries a magic string and the resolved path it was written for,
    and removal refuses a mismatch."""
    body = _read(BUILDER)
    assert "[switch]$Remove" in body
    assert SENTINEL in body
    assert "PARALLAX-LANE-HOME-V1" in body
    assert "sentinel does not match this path" in body


def test_removal_refuses_dangerous_roots():
    """Belt and braces on top of the sentinel: even a correctly-formed
    sentinel must not authorize deleting a drive root, the user profile,
    or a repository root. Task 3 Step 5 exercises all three live, each
    with a correctly-formed sentinel - a guard that has only ever seen a
    malformed sentinel has not been tested."""
    body = _read(BUILDER)
    assert "refusing to remove" in body
    assert "$env:USERPROFILE" in body
    assert "IsPathRooted" in body
    assert ".git" in body


def test_a_failed_build_leaves_no_credential_behind():
    """Cleanup runs only for a directory THIS invocation created and
    marked - an unconditional recursive delete in a catch block would
    delete a directory the script had refused to touch."""
    body = _read(BUILDER)
    assert "try {" in body
    assert "$createdByThisInvocation" in body


def test_cleanup_is_fault_tested_live():
    """A cleanup path with no test asserting it runs is a cleanup path
    that has never run. Task 3 Step 5 injects a post-credential failure."""
    body = _read(BUILDER)
    assert "PARALLAX_LANE_HOME_FAULT" in body


def test_builder_writes_no_hooks():
    """The user's real config carries seven Orca lifecycle hooks including
    PreToolUse and PermissionRequest, each running a shell script."""
    body = _read(BUILDER)
    assert "[[hooks]]" not in body
    assert "carries no hooks by construction" in body


def test_builder_pins_effort_and_empties_the_skill_sources():
    body = _read(BUILDER)
    assert "extra_skill_dirs = []" in body
    assert "default_effort" in body
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_kimi_lane_home.py -v`
Expected: FAIL.

- [ ] **Step 3: Write the builder**

Create `tools/new-kimi-lane-home.ps1` implementing, in order:

1. `-Remove` mode. Refuse unless `<Path>/.parallax-lane-home` exists AND its first line is `PARALLAX-LANE-HOME-V1` AND its second line is the resolved `-Path` it was written for; otherwise fail with `sentinel does not match this path`. Then refuse outright — message beginning `refusing to remove` — if the resolved path is a drive root, is `$env:USERPROFILE` or above it, or contains a `.git` entry. Only then delete recursively. A bare filename sentinel is plantable anywhere, so the CONTENT is the credential, and the root guards are the backstop for a correctly-formed sentinel in the wrong place.
2. Refuse an existing `-Path`.
3. Resolve whether the parent is inside a git work tree. Run `git rev-parse --is-inside-work-tree`, then check `$LASTEXITCODE`: `true` refuses with the work-tree message; a nonzero exit refuses with `could not determine whether <path> is inside a git work tree`. Only an explicit `false` proceeds. Fail closed — an unmade measurement is never a clean one, and the consequence here is a credential in a repository.
4. Refuse if the source credential is absent, with the UNAVAILABLE message.
5. Set `$createdByThisInvocation = $false`, then wrap everything from directory creation onward in `try { } catch { if ($createdByThisInvocation) { Remove-Item $Path -Recurse -Force } ; throw }`. The flag is set only after this invocation has created the directory and written the sentinel, so a refusal path can never delete a directory the script declined to touch. To make the path testable, honour a `PARALLAX_LANE_HOME_FAULT` environment variable that throws immediately after the credential copy; Step 5 uses it to prove the cleanup runs.
6. Create the directory, write the sentinel (`PARALLAX-LANE-HOME-V1` then the resolved path), set `$createdByThisInvocation = $true`, then set the ACL BEFORE the credential is copied: `SetAccessRuleProtection($true, $false)` to drop inherited rules, remove every existing explicit ACE, then add one FullControl rule for the current identity.
7. Copy the credential, write `config.toml` from the template (no hooks, `extra_skill_dirs = []`, `telemetry = false`, `[thinking] enabled = true`, the model table with `default_effort`), create the empty `skills/` directory.
8. Print `(Resolve-Path $Path).Path` as the only stdout output.

- [ ] **Step 4: Run the tests**

Run: `python -m pytest evals/multi-model-verify/test_kimi_lane_home.py -v`
Expected: PASS.

- [ ] **Step 5: Verify live on both hosts**

Under BOTH `powershell.exe` and `pwsh` — 0.16.1's lock defect was green on one interpreter and broken on the other:

- Build a home, set `KIMI_CODE_HOME`, run `provider list` by absolute binary path, expect `source=oauth`.
- Re-run the build against the same path: expect refusal.
- Build inside a git work tree: expect refusal.
- **Inspect the effective ACL** with `Get-Acl <home> | Format-List`, and confirm only the current identity appears. r2 asserted the ACL API call existed and never looked at the result.
- **Fault-test the cleanup**: build with `PARALLAX_LANE_HOME_FAULT=1` set, confirm the command fails AND the directory is gone, so no credential copy survives a mid-build failure. **Then clear the variable** — leaving it set makes every later build in that shell fail for a reason nobody will look for.
- Run `-Remove` on a real home: gone. On a directory with no sentinel: refused. On a directory carrying a sentinel whose second line names a DIFFERENT path: refused.
- **Exercise the destructive guards against DISPOSABLE targets only.** Each needs a correctly formed sentinel, because a guard that has only ever seen a malformed one has not been tested — but planting an authorizing sentinel on the real user profile or a real drive root and then running newly written recursive-deletion code means that if the guard is defective the test destroys exactly what it exists to protect. So:
  - user-profile branch: run the script in a SUBPROCESS with `USERPROFILE` pointed at a temporary directory, and target that.
  - drive-root branch: use a disposable substituted drive (`subst X: <temp dir>`) and target `X:\`, then `subst /d`.
  - repository branch: a scratch directory containing an empty `.git` entry.
  - Remove every planted sentinel afterwards, in a `finally`, whether the test passed or not.
  Never point any of these at a real profile, a real drive root, or a real repository.
- Confirm `-Remove` works without `-Model`, which is the whole reason for the parameter sets.

- [ ] **Step 6: Commit**

```bash
git add tools/new-kimi-lane-home.ps1 evals/multi-model-verify/test_kimi_lane_home.py
git commit -m "add the per-debate kimi-code lane home builder"
```

---

### Task 4: Close the two remaining probes

Five of seven unknowns were settled in `probe-record-2.md`. Two remain, and neither blocks the contract's structure.

**Files:**
- Modify: `docs/superpowers/plans/rounds/2026-07-31-kimi-code-swap/probe-record-2.md`

- [ ] **Step 1: Probe the cp1252 output hazard**

Build a home. From a console forced to cp1252 (`chcp 1252`), dispatch a prompt asking for a reply containing an em-dash, an arrow and a non-Latin character, redirecting stdout to a file. Confirm the file holds the characters and the process exits 0. This gates whether Task 10 deletes the Python UTF-8 guard or replaces it with one describing this client.

- [ ] **Step 2: Probe whether a session file can be replaced and regrow**

Does the per-session log rotate the way the global log does? `kimi export --no-include-global-log` documents rotated `.1` files for the global log; per-session behaviour is unstated.

**Finite success criterion**, because "enough to pass any plausible threshold" gives an engineer nothing to stop at: grow one session's per-session log past **16 MB**, then check for any sibling matching `kimi-code.log.*` and whether `kimi-code.log` itself shrank. 16 MB is chosen as an order of magnitude above the largest log this lane has produced (359 KB across a full day of real use on the old client) and above the common 1, 5 and 10 MB defaults. Reaching it without rotation is a NEGATIVE result and is recorded as such; the probe is not required to find rotation, only to look at a stated depth.

Grow it with repeated cheap dispatches into one session rather than by writing to the file directly — a hand-appended file proves nothing about what the client does.

Whatever the answer, Task 7's freshness region hashes BOTH files' prefixes, so the rule does not depend on rotation being absent. Record the result so the contract can say whether rotation is known-absent at this depth or merely guarded against.

- [ ] **Step 3: Append both results and remove the probe homes**

Append to `probe-record-2.md` under a new heading, with exact commands and outputs. Then `-Remove` every probe home and confirm no credential copy survives.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/plans/rounds/2026-07-31-kimi-code-swap/probe-record-2.md
git commit -m "close the encoding and session-file-rotation probes"
```

---

### Task 5: The agent file

**Files:**
- Create: `skills/multi-model-verify/references/kimi-reviewer-agent.md`
- Delete: `skills/multi-model-verify/references/kimi-reviewer-agent.yaml`, `kimi-reviewer-system.md`
- Modify: `evals/multi-model-verify/test_backup_lane.py:14-15, 20-29, 41-43, 64-77`

**Interfaces:**
- Produces: `AGENT_MD`, `ALLOWLIST`, `DENYLIST`, `KNOWN_TOOLS` in `test_backup_lane.py`.

- [ ] **Step 1: Rewrite the constants**

```python
AGENT_MD = REFS / "kimi-reviewer-agent.md"
ALLOWLIST = ["Read", "Grep", "Glob", "ReadMediaFile", "TodoList"]
DENYLIST = ["Bash", "Write", "Edit", "WebSearch", "FetchURL",
            "EnterPlanMode", "ExitPlanMode", "Agent", "AgentSwarm",
            "AskUserQuestion", "Skill", "TaskList", "TaskOutput",
            "TaskStop", "CronCreate", "CronList", "CronDelete"]
# Every built-in tool documented for 0.31.1, written out INDEPENDENTLY of
# the two lists above. r3 defined this as their union and then compared the
# union back to it, which is a tautology that detects neither a swapped
# name nor an omission.
#
# Accepted limit, stated plainly because r4 caught the earlier wording
# overclaiming: NOTHING here detects a tool a future client adds. The
# floor check is a LOWER BOUND - it rejects releases below 0.31.1 and
# accepts every newer one, so it does not force a re-probe at upgrade.
# Re-probing the inventory is a manual step at any deliberate version
# bump, and the drift snapshot's recorded version is what makes such a
# bump visible.
KNOWN_TOOLS = {
    "Read", "Write", "Edit", "Grep", "Glob", "ReadMediaFile", "Bash",
    "WebSearch", "FetchURL", "EnterPlanMode", "ExitPlanMode", "TodoList",
    "Agent", "AgentSwarm", "AskUserQuestion", "Skill", "TaskList",
    "TaskOutput", "TaskStop", "CronCreate", "CronList", "CronDelete",
}
```

- [ ] **Step 2: Rewrite the artifact and list tests**

```python
def test_backup_artifacts_exist():
    for p in (BACKUP_LANE, AGENT_MD):
        assert p.is_file(), str(p)
    assert not (REFS / "kimi-reviewer-agent.yaml").exists()
    assert not (REFS / "kimi-reviewer-system.md").exists()


def test_agent_allowlist_and_denylist_exact():
    """Exact LIST equality. Omitting `tools:` means ALL tools on this
    client, so a silent parse failure is PERMISSIVE - hence the denylist
    as well."""
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


def test_the_two_lists_partition_the_known_inventory():
    """Set equality, not a count. r2 asserted len(A)+len(B)==22, which
    stayed green if a real name were swapped for a nonexistent one.

    Accepted limit, stated so it stays deliberate: this cannot see a tool
    a FUTURE client adds, and nothing offline can. The floor is a LOWER
    bound and accepts every newer release, so it does not force a
    re-probe either - re-probing is a manual step at a deliberate version
    bump, made visible by the drift snapshot's recorded version."""
    assert not (set(ALLOWLIST) & set(DENYLIST))
    assert set(ALLOWLIST) | set(DENYLIST) == KNOWN_TOOLS


def test_agent_empties_the_subagent_list():
    """Measured: `subagents` defaults to ALL, including `coder`. That was
    inert only because Agent and AgentSwarm are denied, and the
    coincidence of two controls is not a control."""
    assert "subagents: []" in _read(AGENT_MD)


def test_backup_files_no_backslash_paths():
    for p in (BACKUP_LANE, AGENT_MD):
        assert "\\" not in _read(p), str(p)
```

- [ ] **Step 3: Run tests to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py -k "artifacts or allowlist or partition or subagent or backslash" -v`
Expected: FAIL.

- [ ] **Step 4: Write the agent file**

Frontmatter: `name: parallax-readonly-reviewer`, a description, `tools:` in ALLOWLIST order, `disallowedTools:` in DENYLIST order, `subagents: []`. Body: the exact former contents of `kimi-reviewer-system.md`, unchanged — Task 7's evidence rule compares the recorded `systemPrompt` against this body byte for byte, and `systemPromptChars` against its length.

- [ ] **Step 5: Delete the superseded pair, run the tests**

```bash
git rm skills/multi-model-verify/references/kimi-reviewer-agent.yaml skills/multi-model-verify/references/kimi-reviewer-system.md
```

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py -k "artifacts or allowlist or partition or subagent or backslash" -v`
Expected: PASS.

- [ ] **Step 6: Re-run the write-probe against the committed file**

Build a fresh home; from a throwaway git workspace run the marker-creation prompt with the committed agent file. PASS requires all three: explicit refusal, marker absent, `git -c core.quotepath=false status --porcelain --ignored -uall` unchanged from baseline. Anything else means the lane is BROKEN — stop. Confirm `state.json` shows `subagents: []`, then remove the home.

- [ ] **Step 7: Commit**

```bash
git add skills/multi-model-verify/references/kimi-reviewer-agent.md evals/multi-model-verify/test_backup_lane.py
git commit -m "replace the kimi reviewer agent pair with one markdown agent file"
```

---

### Task 6: The evidence validator and its fixtures

**Files:**
- Create: `tools/read-kimi-round-evidence.ps1`
- Create: `evals/multi-model-verify/fixtures/kimi-round/` (fixtures)
- Create: `evals/multi-model-verify/test_kimi_round_evidence.py`

**Interfaces:**
- Consumes: Task 2's declarations, Task 3's builder, Task 5's agent file.
- Produces:
  `tools/read-kimi-round-evidence.ps1 -SessionDir <dir> -Kind <fresh|resume> -PriorState <path-to-json> -Model <id> -Provider <name> -Effort <level> -AgentFile <path> -ExpectedBriefSha256 <hex> -Json`

  `-PriorState` is a JSON file, written by the previous invocation or by the pre-dispatch capture step. **Its identity fields differ by kind, because a fresh call's session does not exist until the client creates it during that call.** r4's version demanded `sessionDir` and `sessionId` in the pre-dispatch state unconditionally, which made the clean fresh case impossible to instantiate — a fix that broke the thing it was protecting.

  - **Fresh**: `kind: "fresh"` and `knownSessionDirs`, the full list of session directory paths under `<debate-home>/sessions` immediately before dispatch. No offsets or hashes; there is nothing yet to offset into.
  - **Resume**: `kind: "resume"`, `sessionDir`, `sessionId`, `wireBytes`, `logBytes`, `wirePrefixSha256`, `logPrefixSha256`, `toolsHash`, `systemPromptHash`.

  For a fresh call the validator also takes `-SessionIdFromStdout`, the id the client printed on its `To resume this session:` line, so the directory it identifies is cross-checked against what the client itself reported rather than inferred from the filesystem alone.

  `nextState` is always a resume-shaped object bound to the resolved path and id, so round 2 onward carries the exact comparison r4 wanted — just not before the session exists. Exits 0 printing `{"status":"clean", "nextState": {...}}` only when every check passes; otherwise exits non-zero with `"status":"failed"` and a `reason`. `nextState` has the same shape and is fed to the next call.

Four interface points are direct review fixes:

- `-ExpectedBriefSha256` rather than a brief FILE, because a file re-read after the call is mutable and would silently redefine the expected value.
- `-Provider`, which the r2 rule compared against but never received.
- **Offsets are BYTE counts, not line counts**, for both files. This removes r3's framing question entirely: a prefix hash over raw bytes through a byte offset has one unambiguous definition, whereas "SHA-256 of the existing lines" leaves encoding and newline framing undefined and two implementations can disagree.
- **A single `-PriorState` object instead of loose offsets**, carrying `sessionDirExisted` so the fresh-call rule is checkable at all — r3's version asked the validator to know something it was never told — and binding each invocation to the previous one's output so a valid older offset-and-hash pair cannot be replayed.

- [ ] **Step 1: Capture and normalize fixtures**

From a home built for this purpose, capture a fresh tool-using round and a resumed round in one session, then hand-normalize: replace absolute user paths with `C:/fixture/...` and the session id with a fixed placeholder. The repo is PUBLIC and raw captures carry the user's home layout — only hand-normalized synthetic fixtures are committed, the same rule the codex probe fixtures follow.

Build these fixture files: a clean fresh wire and log, a clean resumed wire and log, plus mutated copies for each failure case below.

- [ ] **Step 2: Write the failing tests**

One test per case. Each asserts on `status` and on the `reason` field, never on an exact message string, so the invariant is pinned and the wording stays free.

Clean cases:
- fresh round with correct offsets returns `clean`
- resumed round with correct offsets returns `clean`
- a resumed round is clean **even though its slice contains no `config.update`, `tools.set_active_tools` or `llm.tools_snapshot`** — the measured shape, and the case r2 would have failed
- a fresh round with `llm.request` ×4 is clean — the count is not fixed

Freshness cases:
- resumed round validated with a zero wire offset FAILS: round 1's records would otherwise satisfy it. The stale-evidence case, and the reason the script exists.
- same for a zero log offset, so wire and log are covered symmetrically
- **a stale offset landing MID previous call** — after its `turn.prompt`, before its trailing `llm.request` records — fails `slice-misaligned`. r3 tested only offset zero, and this is the shape that passes every count and value check while mixing two calls.
- wire file shorter than its offset fails as truncation, and specifically is not re-read from zero
- log file shorter than its offset fails the same way
- a wire file whose prefix no longer hashes to `wirePrefixSha256` fails as replacement, even when longer than the offset
- **a LOG whose prefix no longer hashes** fails the same way — the rotation question is about the log, and length-only protection there was r3's asymmetry
Session-identity cases, the fresh branch and the resume branch being different mechanisms and needing separate cover:
- a fresh call producing ZERO new session directories fails `session-not-resolvable`
- a fresh call producing TWO new session directories fails the same way — a concurrent run in the same home, which is the one collision an isolated home does not prevent
- a fresh call whose single new directory does not match `-SessionIdFromStdout` fails `session-id-mismatch`
- a fresh state whose `knownSessionDirs` is stale, so a pre-existing directory reads as new, fails
- a resume whose `-PriorState.sessionDir` or `sessionId` names a DIFFERENT session fails `state-session-mismatch`, rather than being caught incidentally by a prefix hash
- a `-PriorState` that is missing, malformed, or missing a field fails
- a `-PriorState` with a WRONG-TYPED field fails: a string offset, a negative offset, a 63-character hash, `knownSessionDirs` as a string
- a prior state from an OLDER round, replayed, fails rather than validating
- internally inconsistent states fail: a fresh state carrying offsets or hashes or a `sessionDir`; a resume state missing any of them
- the slice-boundary case in both directions: a fresh slice not beginning with `metadata`, and a resume slice not beginning with `turn.prompt`

Missing and malformed:
- missing session directory; missing wire file; missing log file
- a non-JSON line inside the slice fails rather than being skipped
- a VALID-JSON record with a structurally invalid field fails `record-malformed` rather than throwing or coercing: `input` not an array, `input[0]` with no `text`, `toolsHash` not a string
- a missing or unreadable `-AgentFile`, and one whose frontmatter does not parse, fail `agent-file-unusable`
- an `-ExpectedBriefSha256` that is not 64 hex characters fails `bad-argument`
- missing `turn.prompt`; two `turn.prompt` in one slice
- zero `llm.request` in a slice
- missing `llm config` line; two `llm config` lines in one log slice
- session-scoped records missing from a FRESH slice: absent `config.update`, absent `tools.set_active_tools`, absent `llm.tools_snapshot`, absent `permission.set_mode`
- duplicated `config.update` (three of them), duplicated `tools.set_active_tools`, duplicated `llm.tools_snapshot`, duplicated `permission.set_mode` in a fresh slice
- two copies of the FIRST `config.update` shape with the second shape absent — the count is right and the content is not
- the symmetric case: two copies of the SECOND shape with the first absent
- **a RESUME slice containing any session-scoped record**, one case per record type. This is the resume branch's whole reason for existing and r3 gave it no negative test at all.

Inequality:
- `names` unequal to the allowlist; `disallowedNames` unequal to the denylist
- `llm.tools_snapshot` tool names unequal to the allowlist while `names` is correct — separate records, and one can be right while the other is wrong
- `profileName` mismatch
- `systemPrompt` differing from the agent file's body
- `systemPromptChars` differing from the body's length
- `toolCount` unequal to the allowlist length
- **`modelAlias` or `thinkingEffort` wrong in the SECOND `config.update`**
- **`permission.set_mode.mode` not `auto`**
- `modelAlias`, `provider` or `thinkingEffort` wrong on ANY `llm.request` in the slice, not merely the first
- **`toolsHash` or `systemPromptHash` missing, empty, or differing BETWEEN requests inside one slice**
- **requests carrying a consistent `toolsHash` that DISAGREES with `llm.tools_snapshot.hash`**, and a snapshot whose `hash` field is absent
- **`toolsHash` or `systemPromptHash` differing from `-PriorState`'s** on a later round
- provider, model or effort wrong in the LOG line while correct in the requests — r3's inequality cases covered requests only
- `turn.prompt` text not hashing to `-ExpectedBriefSha256`

- [ ] **Step 3: Run tests to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_kimi_round_evidence.py -v`
Expected: FAIL, all.

- [ ] **Step 4: Write the validator**

Rules, in this order:

1. `-PriorState` unreadable, malformed, missing any required field, or carrying a field of the wrong TYPE — a string where a number belongs, a negative offset, a hash that is not 64 hex characters, `sessionDirExisted` as a string: fail `prior-state-unusable`. An unmade measurement is never a clean one, and this object IS the measurement.
2. **Establish the session, by kind.**
   - `-Kind fresh`: enumerate the session directories under `<debate-home>/sessions` now, and subtract `-PriorState.knownSessionDirs`. Require EXACTLY ONE new directory: zero means the call created no session, more than one means something else ran concurrently in this home and the round cannot be attributed. Fail `session-not-resolvable`. Require that directory's name to equal `-SessionIdFromStdout`; a mismatch means the id the client reported is not the directory being read, so fail `session-id-mismatch`. This is how a fresh call gets an identity it could not have had beforehand.
   - `-Kind resume`: `-PriorState.sessionDir` must equal the resolved session directory and `-PriorState.sessionId` must equal its name, else fail `state-session-mismatch`. This keeps the exact binding for every call after the first.
3. Internally inconsistent state: a fresh state carrying offsets, hashes or a `sessionDir`; a resume state missing any of them. Fail `state-inconsistent`. Each describes a history that cannot have happened, and a validator that proceeds from one is reasoning from a fiction.
4. `-AgentFile` missing, unreadable, or whose frontmatter does not parse into a name, a `tools` list and a `disallowedTools` list: fail `agent-file-unusable`. The validator compares against it, so an unreadable one makes every comparison vacuous. `-ExpectedBriefSha256` that is not 64 hex characters: fail `bad-argument`.
5. Session directory absent or unreadable: fail `session-dir-missing`. Wire or log file absent: fail `evidence-file-missing`.
6. On a FRESH call the offsets are zero by definition, so steps 7 and 8 are skipped; the whole file is the slice. On a RESUME they apply in full.
7. Either file shorter in BYTES than its prior offset: fail `truncated`. Do NOT re-read from zero — a replacement's opening records may belong to any round while looking like evidence.
8. Re-hash each file's first N raw bytes, N being its prior offset, and compare to `wirePrefixSha256` and `logPrefixSha256` INDEPENDENTLY. Either unequal: fail `prefix-replaced`. Both files get this, not just the wire: the open rotation question is specifically about the log, and r3 protected the log by length alone.
9. Slice = bytes past each file's offset, wire slice then parsed as lines. Any unparseable line in the wire slice: fail `wire-malformed`. A line that IS valid JSON but structurally wrong for its type — `input` not an array, a missing `text`, a hash that is not a string — must also fail, with `record-malformed`, never throw and never silently coerce.
10. **Slice boundary check.** The wire slice's FIRST record must be `metadata` when `-Kind fresh`, and `turn.prompt` when `-Kind resume`. Measured 2026-07-31: a fresh session's records open `metadata`, `config.update`, `tools.set_active_tools`, `config.update`, `permission.set_mode`, `turn.prompt`. An offset landing mid-call otherwise yields a slice holding the previous call's trailing `llm.request` records plus this call's prompt and requests, which satisfies every count and value check while mixing two calls. Fail `slice-misaligned`.
11. **Session-scoped checks, only when `-Kind fresh`**: exactly two `config.update`, one `tools.set_active_tools`, one `llm.tools_snapshot`, one `permission.set_mode`. Compare, on the FIRST `config.update` shape, `profileName` and `systemPrompt` against `-AgentFile`'s parsed name and body; on the SECOND shape, `modelAlias` against `-Model` and `thinkingEffort` against `-Effort` — r3 counted both and compared neither. Compare `names`/`disallowedNames` against the agent file's two lists, the snapshot's tool names against the allowlist, and `permission.set_mode`'s `mode` against `auto` — r3 counted that record without ever reading its value, which is a check that cannot fail. The two `config.update` shapes are distinguished by which keys they carry, not by their order.
   When `-Kind resume`, require all four record types ABSENT from the slice. Their presence means the resume started a new session and the debate state is lost — the failure the old lane caught with its session-kind check.
12. **Per-call checks, both kinds**: exactly one `turn.prompt`; at least one `llm.request`, with EVERY one carrying `-Provider`, `-Model` and `-Effort`, and every one carrying NONEMPTY `toolsHash` and `systemPromptHash` that are identical across all requests in the slice. One request in a tool loop could otherwise run on a different surface while the emitted hashes come from another. On a FRESH slice the requests' `toolsHash` must also equal the `llm.tools_snapshot` record's own `hash`: consistent request hashes that contradict the snapshot describing the sent schemas are a disagreement, not a pass. Exactly one new `llm config` line in the log slice, carrying provider, model alias and effort, plus `toolCount` equal to the allowlist length and `systemPromptChars` equal to the agent body's length.
13. From round 2 onward, compare this slice's `toolsHash` and `systemPromptHash` against `-PriorState`'s; unequal: fail `hash-discontinuity`. r3 left this to the caller, which made it advice rather than a check.
14. Hash the concatenation of every `turn.prompt` `input[]` element's `text`, UTF-8, CRLF normalized to LF; unequal to `-ExpectedBriefSha256`: fail `brief-hash`.
15. On success emit `status: clean` and a `nextState` carrying `sessionDir`, `sessionId`, both byte offsets, both prefix hashes, `sessionDirExisted: true`, and the two hashes.

- [ ] **Step 5: Run the tests**

Run: `python -m pytest evals/multi-model-verify/test_kimi_round_evidence.py -v`
Expected: PASS, all.

- [ ] **Step 6: Commit**

```bash
git add tools/read-kimi-round-evidence.ps1 evals/multi-model-verify/test_kimi_round_evidence.py evals/multi-model-verify/fixtures/kimi-round
git commit -m "add an executable validator for kimi-code round evidence"
```

---

### Task 7: Rewrite the lane's transport and evidence contract

**Files:**
- Modify: `skills/multi-model-verify/references/backup-lane.md:18-140`, `:159-198`
- Modify: `evals/multi-model-verify/test_backup_lane.py:80-257`
- Modify: `evals/multi-model-verify/test_contract_coverage.py:624-648`

**Interfaces:**
- Produces regions: `lane-home-isolation`, `round-freshness-boundary`, `per-round-session-evidence`, `evidence-hash-continuity`, `brief-hash-binding`, `resume-inheritance`.

- [ ] **Step 1: Update DECLARED_REGIONS first**

Remove `rotation-guard-detection`, `rotation-guard-disposition`, `rotation-guard-identity`, `session-block-attribution`, `session-block-kind`, `session-block-residual`, `lane-lock`. Add the six above, with a comment recording that `round-freshness-boundary` is the surviving half of the deleted offset rule and that the session-kind check survives inside `per-round-session-evidence`.

- [ ] **Step 2: Run the coverage test to verify it fails**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -k declared -v`
Expected: FAIL both directions.

- [ ] **Step 3: Rewrite Transport**

Command lines use `<kimi-code-binary>` as the placeholder, never a bare `kimi`, so the pin and the absolute-path instruction agree — r2 said one and pinned the other.

- Dispatch: `<kimi-code-binary> -m <canonical-backup-model-id> --agent-file <plugin-checkout>/skills/multi-model-verify/references/kimi-reviewer-agent.md --skills-dir <debate-home>/skills -p "<the whole brief>"`, working directory set to the review mirror.
- Resume: `<kimi-code-binary> --session <session-id> -m <canonical-backup-model-id> --skills-dir <debate-home>/skills -p "<rebuttal>"`. Measured, and stated at exactly the width of the measurement: of the FOUR flags tested, resume accepts `-m`, `--skills-dir` and `--add-dir`, and rejects `--agent-file`. Nothing was established about flags not in that set. Re-pin the ones measured to be accepted; it is free and it narrows the inheritance risk to the one flag known not to be re-pinnable.
- Region `lane-home-isolation`: build once before round 1, set `KIMI_CODE_HOME` on every call of the debate, the two independent reasons, and that an unbuildable home or missing credential makes the lane UNAVAILABLE. Remove the home when the debate ends, because it holds a copied credential.
- Region `resume-inheritance`: what a bare resume was measured to inherit ON 0.31.1, that a wrong-directory resume is refused, that `--agent-file` is rejected because the agent is bound at session creation, and that this is VERSION-BOUND — which is why the floor exists, why what can be re-pinned is re-pinned, and why the evidence check is what actually establishes the surface each round.
- The brief is passed INLINE, never planted as a file with a pointer, because the hash rule can only detect truncation if the recorded prompt IS the brief. A brief that exceeds the inline transport is a transport failure to diagnose, not a reason to switch to a pointer whose hash proves nothing.

- [ ] **Step 4: Rewrite Per-round evidence**

- Region `round-freshness-boundary`: the files are cumulative, so before every call capture, for BOTH the wire transcript and the per-session log, the BYTE length and a SHA-256 over exactly those bytes, after the call read only past the byte offsets and require both prefix hashes unchanged. A file shorter than its offset, or absent, or whose prefix hash changed, was replaced: that is a route-attribution failure and specifically not a reason to re-read from zero. Byte offsets and a hash over raw bytes are what make this unambiguous, and hashing BOTH files is what makes it prove identity rather than length, since length alone passes a file replaced, truncated and regrown. A fresh call has no offsets to capture, because its session does not exist until the client creates it; what is captured before a fresh dispatch is the session-directory INVENTORY, and exactly one new directory must appear, matching the session id the client printed. The slice must also BEGIN at a call boundary — the record `metadata` for a fresh call, `turn.prompt` for a resume, both measured — because an offset landing mid-call yields a slice mixing the previous call's trailing records with this one's while satisfying every count and value check.

- Region `per-round-session-evidence`: state the TWO RECORD CLASSES explicitly, because one rule cannot cover both and a rule that assumed it could was measured to fail a clean round 1 and every resumed round. Session-scoped records — `config.update` twice, `tools.set_active_tools`, `llm.tools_snapshot` and `permission.set_mode` once each — appear ONLY in the session-creating call's slice; require them there and require their ABSENCE from a resume's slice, since their presence means the resume silently started a new session. Per-call records — exactly one `turn.prompt`, one or more `llm.request` with every one carrying the canonical provider, model and effort, and exactly one new `llm config` log line carrying those plus `toolCount` and `systemPromptChars` — appear in every slice. `llm.request` tracks the tool loop and is bounded from below, never fixed. Run `tools/read-kimi-round-evidence.ps1` with the captured offsets and require `status: clean`; a missing directory, a missing or miscounted record, an unreadable file, a malformed line, or any inequality is a route-attribution failure, the reply is DISCARDED unread, and the failure goes to the fallbacks.md consent gate.

- Region `evidence-hash-continuity`: record `toolsHash` and `systemPromptHash` in round 1; the validator itself requires every later round to match, rather than leaving the comparison to a driver who might not make it, and both values are RECORDED IN THE DEBATE RECORD. They are deliberately not pinned to a literal in this repo, because they cover tool schemas any client release may reword and a committed literal would fail every round for a reason that is not a route problem. Recording them is what makes a client upgrade's change visible instead of silently rebaselined at the next round 1.

- Region `brief-hash-binding`: hash the brief before dispatch and require the recorded prompt to match, canonicalized as UTF-8 with CRLF normalized to LF over the concatenation of every `turn.prompt` `input[]` element's `text` field. r2 said "hashes to the same value" while its own evidence matched only after newline normalization — an undefined step a driver would have to invent.

- Unmarked prose, stated NARROWLY: what these checks do and do not guarantee. A failed allowlist does not necessarily change the effective tool set, because the denylist can exclude the same tools by name. What the checks guarantee is that the configured lists, the resolved snapshot, the system prompt and its length are all compared against committed text, so a divergence in any of them surfaces. r2 overclaimed here.

- [ ] **Step 5: Rewrite the Client config surface section**

- Effort: written into the debate home and confirmed per call. Measured: `default_effort = "low"` produced `thinkingEffort=low`.
- Thinking: config-asserted and NOT runtime-verified. Measured: `enabled = false` produced output identical to `true`. Say exactly that; do not list it beside effort.
- Skill discovery: name all four roots — `.kimi-code/skills/`, `.agents/skills/`, `<debate-home>/skills/`, `~/.agents/skills/` — and state that `--skills-dir` is a MITIGATION whose effect is unmeasurable in this configuration. Measured: with canaries planted at both project roots, runs with and without it were identical and the reviewer reported no skills available, most likely because `Skill` is absent from the allowlist. The load-bearing controls are the allowlist and preflight-3 remediation. Keep passing `--skills-dir` because it costs nothing and covers a future release that advertises regardless, but claim nothing for it.
- Record that a planted `SKILL.md` remains readable as ordinary workspace content: in the measured round the reviewer read both canaries with `Read` and declined on judgment. Prompt text is never a control, which is why remediation removes the files.

- [ ] **Step 6: Rewrite the pins**

One test per region, each asserting the region WHOLE via `_norm`. Plus `test_deleted_machinery_does_not_return` holding absence checks for `kimi-lane-lock.ps1`, `Rotation guard` and `Created new session:`, with a comment saying absence checks lock nothing under the grammar and are restoration guards, not coverage.

- [ ] **Step 7: Run the whole suite**

Run: `python -m pytest evals -q`
Expected: PASS. A region reporting uncovered means the pin does not contain it WHOLE — fix the pin, not the region.

- [ ] **Step 8: Commit**

```bash
git add skills/multi-model-verify/references/backup-lane.md evals/multi-model-verify/test_backup_lane.py evals/multi-model-verify/test_contract_coverage.py
git commit -m "rewrite the backup lane's transport and evidence for kimi-code"
```

---

### Task 8: Delete the lane lock

**Files:**
- Delete: `tools/kimi-lane-lock.ps1`, `evals/multi-model-verify/test_kimi_lane_lock.py`

- [ ] **Step 1: Find every reference**

```powershell
Get-ChildItem -Recurse -File | Where-Object { $_.FullName -notmatch '\\\.git\\' } |
  Select-String -Pattern "kimi-lane-lock" -List | Select-Object Path
```

Filter on the full path, not `-Exclude`: `-Exclude` matches file NAMES and does not stop traversal into `.git`, which is r2's defect here.

- [ ] **Step 2: Delete and clean prose**

```bash
git rm tools/kimi-lane-lock.ps1 evals/multi-model-verify/test_kimi_lane_lock.py
```

Edit each remaining non-`docs/**` file the search found, deleting the lock sentence rather than rewording it.

- [ ] **Step 3: Verify and run the suite**

Re-run the search: only `docs/**` should match, being historical records.
Run: `python -m pytest evals -q` — PASS, with 41 fewer tests collected.

- [ ] **Step 4: Commit**

Stage by explicit path, listing each deleted and edited file. Do NOT use `git add -u`.

```bash
git add tools/kimi-lane-lock.ps1 evals/multi-model-verify/test_kimi_lane_lock.py <each edited file>
git commit -m "delete the kimi lane lock, which guarded a shared log that no longer exists"
```

---

### Task 9: Extend preflight 3 to `.kimi-code/`

**Files:**
- Modify: `skills/multi-model-verify/SKILL.md:61-77`, `tools/new-review-mirror.ps1`, `evals/multi-model-verify/test_review_mirror.py`

- [ ] **Step 1: Write the failing test**

```python
def test_enumeration_sweeps_the_kimi_code_back_channel():
    """kimi-code discovers agents from .kimi-code/agents/ and skills from
    .kimi-code/skills/ in the REVIEWED tree. Measured: the reviewer read a
    planted SKILL.md there as ordinary file content, so removal - not the
    reviewer's judgment - is the control."""
    body = (REPO / "tools" / "new-review-mirror.ps1").read_text(
        encoding="utf-8")
    assert "'.kimi-code/*'" in body
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -k kimi_code -v`
Expected: FAIL.

- [ ] **Step 3: Add the pathspec and update the preflight text**

Add `'.kimi-code/*'` to the `git ls-files --cached --others` pathspec list, and extend SKILL.md's preflight-3 sentence and listing command to name it. Keep root anchoring and the existing depth-asymmetry note, which applies identically.

Because Task 4's measurement showed `--skills-dir` suppresses nothing observable, this sweep is the PRIMARY control for the reviewed tree's skills and agents, and the text must say so. Describing it as defence in depth would be describing a mitigation as a control.

- [ ] **Step 4: Run the tests and commit**

Run: `python -m pytest evals -q` — PASS.

```bash
git add tools/new-review-mirror.ps1 skills/multi-model-verify/SKILL.md evals/multi-model-verify/test_review_mirror.py
git commit -m "sweep .kimi-code back-channels in preflight 3"
```

---

### Task 10: Failure routing, the doctor and the README

**Files:**
- Modify: `skills/multi-model-verify/references/fallbacks.md:152-179`, `commands/doctor.md`, `README.md`
- Modify: `evals/multi-model-verify/test_backup_lane.py:489-512, 546`

- [ ] **Step 1: Rewrite the route-attribution entry**

`fallbacks.md:152-161` names "offset rule in backup-lane.md". Retarget it to the freshness boundary and the validator. Keep the disposition: no retry, reply DISCARDED unread, consent gate. Keep the transient-member carve-out, which still has a member — a session file replaced under the call would yield clean evidence on a re-dispatch.

`test_backup_lane.py:546` currently pins the old rotation sentence and must be rewritten in this same step, or the suite fails.

- [ ] **Step 2: Resolve the encoding class per Task 4 Step 1**

If no hazard was measured: delete the `output-encoding` class from `fallbacks.md:162-179`, delete the four-flags-re-pinned recovery, and remove the Python guard bullet from `backup-lane.md`. If a hazard WAS measured: keep the class and rewrite it to describe this client's failure and recovery.

Replace `test_output_encoding_class_is_wired` with a test matching whichever branch was taken, asserting in both cases that `PYTHONIOENCODING` and `PYTHONUTF8` are gone from the lane.

- [ ] **Step 3: Update the doctor and the README**

Rewrite `commands/doctor.md`'s backup-lane section to check: the binary at the absolute path exists and reports at or above the floor; `provider list` under a freshly built home reports `source=oauth`; the committed agent file's allowlist is present. Drop every reference to `kimi_cli` module imports, `--quiet`, `--thinking` and the lane lock. Fix any `README.md` row naming the deleted yaml or system file.

- [ ] **Step 4: Run the full gate and commit**

All four gate commands — PASS.

```bash
git add skills/multi-model-verify/references/fallbacks.md skills/multi-model-verify/references/backup-lane.md commands/doctor.md README.md evals/multi-model-verify/test_backup_lane.py
git commit -m "retire the stale failure routing and update the doctor for kimi-code"
```

---

### Task 11: Prove the lane, close the backlog, ship

- [ ] **Step 1: Run the opt-in behavioral suite**

Run: `python evals/tools/run_behavioral_evals.py`
Expected: PASS. Record any failing case by name; do not proceed without deciding whether it is a real regression.

- [ ] **Step 2: Run a real two-round debate end to end**

The lane has reviewed nothing until it has. Against a small real diff:

- Build the debate home. Build the mirror.
- **Write the prior-state file BEFORE dispatching.** r2 wrote "dispatch, capture offsets", reversing the one rule the whole design rests on. For round 1 that file is the FRESH shape: `kind: "fresh"` plus `knownSessionDirs`, the session directories present in the debate home right now — normally none, but capture it rather than assuming. There are no offsets or hashes to record, because the session does not exist yet.
- Dispatch round 1. Take the session id from the client's `To resume this session:` line. Run the validator with `-Kind fresh`, that prior-state file, and `-SessionIdFromStdout`. Require `status: clean`. **Persist the returned `nextState`** — it is resume-shaped and carries the resolved path and id, both offsets, both prefix hashes and the two continuity hashes. Round 2 cannot be validated without all of it.
- Resume for round 2 with `-m` and `--skills-dir` re-pinned, passing the persisted `nextState` as `-PriorState`. Run with `-Kind resume`. Require `status: clean`, and confirm it is validating round 2's records and not round 1's.
- Confirm the validator rejected nothing on hash continuity, and record both hashes in the debate record.
- **Negative confirmation on live data**: re-run the round-2 validation with a prior state whose offsets are zeroed, and confirm it FAILS. A freshness rule never seen to reject anything on real data is untested where it matters.
6. Retain every artifact under `rounds/2026-07-31-kimi-code-swap/`, then remove the home.

This is also what item 15 requires before `kimi-cli` may be removed in a later cycle.

- [ ] **Step 3: Mark the backlog**

Item 13 DONE. Item 8 DONE, by the brief-hash rule; truncation did not reproduce at 9033 characters. Item 16 GONE — the lock it describes no longer exists. Item 6's residual answered YES. Item 15 gains a note: the installer renamed the binary to `kimi-legacy.exe`, so the shadowing hazard is gone and the rollback survives; removal still deferred. Update the `**Status.**` line.

- [ ] **Step 4: Bump and rewrite the handoff**

`.claude-plugin/plugin.json` to `0.18.0`. Rewrite `.claude/state/handoff.md` with this cycle's facts, including the four not derivable from the code:

- Session evidence records split into session-scoped and per-call classes; a rule that assumed one class failed a clean round 1 and every resumed round, and only measurement caught it.
- `--skills-dir` suppresses nothing measurable; the allowlist and preflight-3 remediation are the controls.
- Thinking-enabled has no observable signal; effort does.
- Of the four flags tested with a resume, three are accepted and only `--agent-file` is rejected, because the agent is bound at session creation. Nothing is established about untested flags.

Update the standing rules: remove the `PYTHONIOENCODING` and lane-lock bullets, add the absolute-path binary rule and the debate-home rule.

- [ ] **Step 5: Final gate**

All four gate commands, plus `pwsh -File evals/tools/drift_statemachine_tests.ps1`.

- [ ] **Step 6: Commit and update the cache**

```bash
git add docs/superpowers/plans/2026-07-27-0150-backlog.md .claude-plugin/plugin.json .claude/state/handoff.md
git commit -m "0.18.0: close backlog items 13, 8 and 16"
```

Then `claude plugin update parallax@parallax` and restart the session, because `skills/`, `commands/` and `tools/` all changed.

---

## Self-review notes

Every round-2 FIX maps to a step. Freshness identity to Task 7 Step 4's prefix hash and Task 6's `prefix-replaced` case. The missing negative tests to Task 6 Step 2, now enumerated across six groups; the list is not given a count, because every later revision added cases and a stated total goes stale the moment it does. Mutable brief file to `-ExpectedBriefSha256`. Missing `-Provider` to Task 6's interface. Record cardinality to the measured two-class rule in Task 7 Step 4. Unreachable `TryParse` to Task 1 Step 3. State-machine stub location, `-S` versus `--session`, and the missing below-floor mode to Task 1 Step 5. Uncallable and unguarded removal, non-transactional build, fail-open git check and unverified ACL to Task 3. The count-not-inventory test to Task 5 Step 2. `-Exclude` traversal to Task 8 Step 1. Reversed offset capture to Task 11 Step 2. Forward references to canonical declarations and to a deleted probe home resolved by moving declarations to Task 2 and having Task 6 capture its own fixtures.

Two of Sol's fixes remain declined, with reasons in Task 7 Step 4 and Task 7 Step 3: binding `toolsHash` to a client version, replaced by recording both hashes in the debate record; and a sacrificial resume write-probe every debate, replaced by re-pinning the flags a resume was MEASURED to accept — three of the four tested — plus the floor and the per-round evidence check.

Three of Sol's round-2 objections were settled by measurement rather than argument: record cardinality, which was worse than Sol supposed; `--skills-dir`, which turned out to control nothing; and thinking-enabled, which has no observable signal and so cannot be claimed.
