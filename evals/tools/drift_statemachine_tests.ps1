# drift_statemachine_tests.ps1 - offline state-machine tests for
# tools/check-drift.ps1.
#
# Drives the REAL script end to end - probe, canary, auto-triage, verdict
# trust matrix, pytest gate, commit, cross-review, toast matrix, pending
# lifecycle - with every external dependency stubbed:
#   - a throwaway git clone of this repo is the script's $RepoRoot (its own
#     worktrees, branches, and state files never touch the real checkout);
#     the WORKING-TREE check-drift.ps1 is copied over the clone's so
#     uncommitted edits are what gets tested
#   - stub claude.cmd / codex.ps1 on a prepended PATH, behavior selected per
#     scenario via CLAUDE_STUB_MODE / CODEX_STUB_MODE
#   - a fake USERPROFILE holding a plugin registry that points at a fake
#     superpowers install seeded from the pinned fixture
#   - a harness-owned TEMP, so the worktrees the script creates land inside
#     this run's sandbox and can never collide with (or be cleaned up out
#     from under) a real weekly run
#   - the script's two test seams, both gated in production on
#     PARALLAX_DRIFT_STATEMACHINE=1: PARALLAX_DRIFT_TOAST_LOG captures
#     toasts, PARALLAX_DRIFT_TRIAGE_TIMEOUT_MS shortens the 30-min cap
#
# Every environment variable this harness changes is restored in a finally
# block: running it from an interactive shell must not leave that shell with
# a fake USERPROFILE (Sol review 2026-07-13).
#
# Scenarios (triage-timeout LAST - its killed stub can orphan a child that
# briefly holds the worktree, so nothing may run after it):
#   carry-forward      failed version probe keeps the snapshot value
#   blocked-verdict    BLOCKED falls to manual; prior pending re-toasts
#   no-verdict         a verdict-less agent run is not trusted
#   critical-dismissal trusted NO-ACTION on a CRITICAL toasts VERIFY
#   warn-only-silence  WARN-only noise dismissed by triage toasts NOTHING
#   pending-auto-clear a vanished fix branch clears its pending entry
#   fixes-applied      diff -> pytest gate -> commit -> cross-review -> toast
#   gate-failure       a fix that BREAKS the suite is never committed
#   malformed-review   an off-grammar cross-review reads as UNAVAILABLE
#   commit-failure     failed commit discards changes, keeps no branch
#   route-mismatch     wrong header model reads as UNAVAILABLE, fix still lands
#   auth-preflight-fail failed login status skips the review call entirely
#   kimi-flag-drift    help drops --agent-file -> the flag finding
#   kimi-short-flag-drift help keeps --model but drops -m
#   kimi-vocab-drift   import failure -> containment-vocabulary finding
#   kimi-version-carry failed probe never clobbers the snapshot
#   triage-timeout     hung agent is killed at the cap
#
# Runtime: several minutes - four scenarios re-run the full pytest suite
# inside the disposable worktree, exactly as production does. Run directly,
# or via pytest with PARALLAX_STATEMACHINE=1 set
# (test_multi_model_verify.py::TestDriftStateMachine::test_run_state_machine).
#
# Windows PowerShell 5.1, ASCII ONLY (same rules as the script under test).
# Exit code = number of failed assertions (0 = all pass).

param(
    [switch]$KeepTemp
)

$HarnessRoot = $PSScriptRoot                      # evals\tools
$RepoRoot = Split-Path (Split-Path $HarnessRoot)  # repo root
$Root = Join-Path $env:TEMP ("parallax-sm-" + (Get-Date -Format "HHmmss") + "-" + (Get-Random -Maximum 9999))
New-Item -ItemType Directory -Force -Path $Root | Out-Null

# Save EVERY variable we touch; restored in the finally block at the bottom.
$savedEnv = @{}
foreach ($name in @("PATH", "USERPROFILE", "HOME", "TEMP", "TMP",
                    "CLAUDE_STUB_MODE", "CODEX_STUB_MODE",
                    "KIMI_STUB_MODE", "PYTHON_STUB_MODE", "DRIFT_REAL_PYTHON",
                    "PARALLAX_DRIFT_STATEMACHINE",
                    "PARALLAX_DRIFT_TOAST_LOG",
                    "PARALLAX_DRIFT_TRIAGE_TIMEOUT_MS")) {
    $savedEnv[$name] = [Environment]::GetEnvironmentVariable($name, "Process")
}

$script:failCount = 0
$script:LastExit = -1
$script:LastReport = ""
$script:LastToastLog = ""
$script:LastOut = ""

function Assert-True($cond, $label) {
    if ($cond) {
        Write-Output "  ok   $label"
    } else {
        Write-Output "  FAIL $label"
        $script:failCount++
    }
}

try {

# --- workspace: clone, stubs, fake profile -----------------------------------

$Clone = Join-Path $Root "repo"
git clone --quiet --no-hardlinks "$RepoRoot" $Clone 2>&1 | Out-Null
git -C $Clone branch main origin/main 2>&1 | Out-Null  # noop when HEAD is main
Copy-Item (Join-Path $RepoRoot "tools\check-drift.ps1") (Join-Path $Clone "tools\check-drift.ps1") -Force
$DriftScript = Join-Path $Clone "tools\check-drift.ps1"
if (-not (Test-Path $DriftScript)) {
    Write-Output "FATAL: clone setup failed - $DriftScript missing"
    exit 1
}
$ToolsDir = Join-Path $Clone "tools"
$ReportsDir = Join-Path $ToolsDir "drift-reports"
$SnapshotFile = Join-Path $ToolsDir "drift-snapshot.json"
$PendingFile = Join-Path $ToolsDir "drift-pending.json"

$StubDir = Join-Path $Root "stubs"
New-Item -ItemType Directory -Force -Path $StubDir | Out-Null

# claude.cmd: version probe + the triage agent, mode via CLAUDE_STUB_MODE.
# fixes/badfix write into the CWD, which the script sets to the worktree:
# 'fixes' makes a harmless change, 'badfix' plants a FAILING test so the
# script's own pytest gate is what has to catch it.
# The hang mode never exits on its own so the kill path always fires.
@'
@echo off
if "%~1"=="--version" goto version
if "%CLAUDE_STUB_MODE%"=="version-fail" exit /b 1
if "%CLAUDE_STUB_MODE%"=="hang" goto hang
if "%CLAUDE_STUB_MODE%"=="blocked" goto blocked
if "%CLAUDE_STUB_MODE%"=="noaction" goto noaction
if "%CLAUDE_STUB_MODE%"=="fixes" goto fixes
if "%CLAUDE_STUB_MODE%"=="badfix" goto badfix
echo stub agent ran and produced no verdict line
exit /b 0

:version
if "%CLAUDE_STUB_MODE%"=="version-fail" (
echo claude: unexpected stub failure
exit /b 1
)
echo 1.2.3
exit /b 0

:hang
ping -n 11 127.0.0.1 > nul
echo VERDICT: NO-ACTION
exit /b 0

:blocked
echo Findings reviewed; cannot resolve offline.
echo VERDICT: BLOCKED stub cannot resolve this class of drift
exit /b 0

:noaction
echo Findings are stub-environment noise; nothing to change.
echo VERDICT: NO-ACTION
exit /b 0

:fixes
echo stub fix marker> STUB-FIX.txt
echo Applied stub fix.
echo VERDICT: FIXES-APPLIED stub state-machine fix
exit /b 0

:badfix
echo def test_stub_planted_failure():> evals\multi-model-verify\test_zz_stub_planted.py
echo     assert False, "planted by the state-machine harness">> evals\multi-model-verify\test_zz_stub_planted.py
echo Applied a fix that breaks the suite.
echo VERDICT: FIXES-APPLIED stub fix that breaks the gate
exit /b 0
'@ | Set-Content -Path (Join-Path $StubDir "claude.cmd") -Encoding ASCII

# codex.ps1: healthy transport by default.
#   drop-config  - exec --help omits --config, so the flag probe raises
#                  exactly one CRITICAL (the findings driver when claude
#                  itself must stay healthy)
#   bad-review   - the cross-review answers off-grammar, which must read as
#                  UNAVAILABLE, never as a passed review
@'
$null = @($input)
$argList = @($args)
if ($argList -contains "--version") { Write-Output "codex-cli 7.7.7"; exit 0 }
if ($argList.Count -ge 2 -and $argList[0] -eq "login" -and $argList[1] -eq "status") {
    if ($env:CODEX_STUB_MODE -eq "auth-fail") { Write-Output "Not logged in"; exit 1 }
    Write-Output "Logged in using ChatGPT"
    exit 0
}
if ($argList.Count -ge 1 -and $argList[0] -eq "exec" -and ($argList -contains "--help")) {
    $flags = "--sandbox --output-last-message --model --config"
    if ($env:CODEX_STUB_MODE -eq "drop-config") {
        $flags = "--sandbox --output-last-message --model"
    }
    Write-Output "usage: codex exec [flags] $flags"
    exit 0
}
$idx = [Array]::IndexOf($argList, "--output-last-message")
if ($idx -ge 0 -and ($idx + 1) -lt $argList.Count) {
    # Echo the startup header the way the real CLI does - the script's
    # effective-route check parses these lines from captured stdout. The
    # healthy stub reflects the requested route back; wrong-model simulates
    # a config override swapping the model out from under the -m flag.
    $reqModel = ""
    $mIdx = [Array]::IndexOf($argList, "-m")
    if ($mIdx -ge 0 -and ($mIdx + 1) -lt $argList.Count) { $reqModel = $argList[$mIdx + 1] }
    $reqEffort = ""
    foreach ($a in $argList) {
        if ("$a" -like "model_reasoning_effort=*") { $reqEffort = "$a".Split("=")[1] }
    }
    $reqSandbox = ""
    $sIdx = [Array]::IndexOf($argList, "--sandbox")
    if ($sIdx -ge 0 -and ($sIdx + 1) -lt $argList.Count) { $reqSandbox = $argList[$sIdx + 1] }
    if ($env:CODEX_STUB_MODE -eq "wrong-model") { $reqModel = "stub-swapped-model" }
    Write-Output "model: $reqModel"
    Write-Output "provider: openai"
    Write-Output "reasoning effort: $reqEffort"
    Write-Output "sandbox: $reqSandbox"
    $verdict = "REVIEW: PASS"
    if ($env:CODEX_STUB_MODE -eq "bad-review") {
        $verdict = "Looks good to me, ship it."
    }
    Set-Content -Path $argList[$idx + 1] -Value $verdict
}
exit 0
'@ | Set-Content -Path (Join-Path $StubDir "codex.ps1") -Encoding ASCII

# Real python captured BEFORE the stub dir shadows it: the python stub
# must forward everything except the kimi_cli import probe, because the
# drift script's own pytest gate runs through the same binary name.
$env:DRIFT_REAL_PYTHON = (Get-Command python).Source

@'
@echo off
if "%~1"=="--version" goto version
if "%~1"=="--help" goto help
exit /b 0

:version
if "%KIMI_STUB_MODE%"=="version-fail" exit /b 1
echo kimi, version 9.9.9
exit /b 0

:help
if "%KIMI_STUB_MODE%"=="drop-agent-file" (
echo usage: kimi [--quiet] [--thinking] [-m MODEL] [-w DIR] [-p PROMPT] [-r ID]
exit /b 0
)
if "%KIMI_STUB_MODE%"=="drop-short-m" (
echo usage: kimi [--quiet] [--thinking] [--model MODEL] [--agent-file FILE] [-w DIR] [-p PROMPT] [-r ID]
exit /b 0
)
echo usage: kimi [--quiet] [--thinking] [-m MODEL] [--agent-file FILE] [-w DIR] [-p PROMPT] [-r ID]
exit /b 0
'@ | Set-Content -Path (Join-Path $StubDir "kimi.cmd") -Encoding ASCII

@'
@echo off
echo %* | findstr /C:"kimi_cli" > nul
if not errorlevel 1 goto kimiprobe
"%DRIFT_REAL_PYTHON%" %*
exit /b %ERRORLEVEL%

:kimiprobe
if "%PYTHON_STUB_MODE%"=="kimi-import-fail" (
echo ModuleNotFoundError: No module named 'kimi_cli' 1>&2
exit /b 1
)
exit /b 0
'@ | Set-Content -Path (Join-Path $StubDir "python.cmd") -Encoding ASCII

$env:PATH = "$StubDir;" + $env:PATH

# Harness-owned TEMP: the script derives its worktree path from $env:TEMP,
# so this keeps every worktree inside $Root. Cleanup then never has to guess
# which parallax-drift-* directories are ours - a sweep by name could
# delete a concurrent production run's worktree (Sol review 2026-07-13).
$FakeTemp = Join-Path $Root "temp"
New-Item -ItemType Directory -Force -Path $FakeTemp | Out-Null
$env:TEMP = $FakeTemp
$env:TMP = $FakeTemp

# Fake profile: plugin registry -> fake superpowers install seeded from the
# pinned fixture, so the template canary passes offline; .gitconfig gives
# the script's worktree commits an identity.
$FakeProfile = Join-Path $Root "profile"
$SpTemplate = Join-Path $FakeProfile ".claude\plugins\cache\claude-plugins-official\superpowers\6.1.1\skills\requesting-code-review\code-reviewer.md"
$FakeSp = Join-Path $FakeProfile ".claude\plugins\cache\claude-plugins-official\superpowers\6.1.1"
New-Item -ItemType Directory -Force -Path (Split-Path $SpTemplate) | Out-Null
$PinnedFixture = Join-Path $Clone "evals\multi-model-verify\fixtures\superpowers-code-reviewer-6.1.1.md"
Copy-Item $PinnedFixture $SpTemplate -Force
# A fake USERPROFILE needs a real profile's shell-folder skeleton: PS 5.1
# resolves its job persistence path through USERPROFILE-expanded folders,
# and without them the script's Start-Job cross-review dies on Receive-Job
# with "The Persistence Path does not exist" (probed 2026-07-13 - the miss
# is silent, it just degrades every review to UNAVAILABLE).
foreach ($dir in @("Documents", "AppData\Roaming", "AppData\Local", "AppData\LocalLow")) {
    New-Item -ItemType Directory -Force -Path (Join-Path $FakeProfile $dir) | Out-Null
}
$registry = @{
    plugins = @{
        "superpowers@claude-plugins-official" = @(
            @{ version = "6.1.1"; installPath = $FakeSp }
        )
    }
}
ConvertTo-Json -InputObject $registry -Depth 5 | Set-Content -Path (Join-Path $FakeProfile ".claude\plugins\installed_plugins.json")
[IO.File]::WriteAllText((Join-Path $FakeProfile ".gitconfig"),
    "[user]`n`tname = drift-harness`n`temail = drift@localhost`n")
$env:USERPROFILE = $FakeProfile
$env:HOME = $FakeProfile
# Unlocks the script's test seams (they are inert in production without it)
# AND guards the pytest wrapper for this harness against recursing when the
# script re-runs the suite inside its worktree.
$env:PARALLAX_DRIFT_STATEMACHINE = "1"

# --- helpers ------------------------------------------------------------------

function Set-Snapshot($claude, $codex, $sp) {
    $snap = @{ claude = $claude; codex = $codex; superpowers = $sp; updated = "2026-01-01T00:00:00" }
    ConvertTo-Json -InputObject $snap | Set-Content -Path $SnapshotFile
}

function Reset-State {
    # Defaults match the stub versions exactly: no version-change notes, no
    # changelog fetch - every scenario runs fully offline. The superpowers
    # template is restored to the pinned fixture so only the scenario that
    # wants a WARN gets one.
    Set-Snapshot "1.2.3" "7.7.7" "6.1.1"
    Copy-Item $PinnedFixture $SpTemplate -Force
    if (Test-Path $PendingFile) { Remove-Item $PendingFile -Force }
    if (Test-Path $ReportsDir) { Remove-Item -Recurse -Force $ReportsDir }
}

function Set-SnapshotWithKimi($claude, $codex, $sp, $kimi) {
    $snap = @{ claude = $claude; codex = $codex; superpowers = $sp; kimi = $kimi; updated = "2026-01-01T00:00:00" }
    ConvertTo-Json -InputObject $snap | Set-Content -Path $SnapshotFile
}

function Invoke-Drift($scenario, $claudeMode, $codexMode, $timeoutMs) {
    Write-Output ""
    Write-Output "SCENARIO $scenario"
    $toastLog = Join-Path $Root "$scenario-toasts.txt"
    if (Test-Path $toastLog) { Remove-Item $toastLog -Force }
    $env:PARALLAX_DRIFT_TOAST_LOG = $toastLog
    $env:PARALLAX_DRIFT_TRIAGE_TIMEOUT_MS = "$timeoutMs"
    $env:CLAUDE_STUB_MODE = $claudeMode
    $env:CODEX_STUB_MODE = $codexMode
    $script:LastToastLog = $toastLog
    $script:LastOut = (& powershell.exe -NoProfile -ExecutionPolicy Bypass -File $DriftScript 2>&1 | Out-String)
    $script:LastExit = $LASTEXITCODE
    $script:LastReport = ""
    if (Test-Path $ReportsDir) {
        $rep = Get-ChildItem $ReportsDir -Filter "*.txt" |
            Where-Object { $_.Name -match '^\d{4}-\d{2}-\d{2}_\d{6}\.txt$' } |
            Select-Object -First 1
        if ($rep) { $script:LastReport = Get-Content $rep.FullName -Raw }
    }
}

function Get-Toasts {
    if (Test-Path $script:LastToastLog) { return (Get-Content $script:LastToastLog -Raw) }
    return ""
}

function Get-Pending {
    if (-not (Test-Path $PendingFile)) { return @() }
    # Same trap the script itself dodges: assign first, THEN wrap - piping
    # ConvertFrom-Json into @() collects a JSON array as one element. The
    # leading comma stops the function-return pipeline from unwrapping a
    # single-entry array back into a bare object (.Count is null on a
    # PSCustomObject in PS 5.1).
    $parsed = Get-Content $PendingFile -Raw | ConvertFrom-Json
    return , @($parsed)
}

function Get-DriftBranches {
    return (git -C $Clone branch --list "drift/*" 2>&1 | Out-String).Trim()
}

function Complete-Scenario($failsBefore) {
    if ($script:failCount -gt $failsBefore) {
        Write-Output "  --- report ---"
        Write-Output $script:LastReport
        Write-Output "  --- toasts ---"
        Write-Output (Get-Toasts)
        Write-Output "  --- script output (exit $($script:LastExit)) ---"
        Write-Output $script:LastOut
    }
}

# --- scenario: carry-forward ---------------------------------------------------
# A failed claude version probe raises CRITICAL but must NOT clobber the
# snapshot's last known-good value (an empty field would disable next week's
# change detection). The failing stub also fails the triage call -> manual.

$b = $script:failCount
Reset-State
Set-Snapshot "9.9.9" "7.7.7" "6.1.1"
Invoke-Drift "carry-forward" "version-fail" "" 60000
Assert-True ($script:LastExit -eq 1) "exit code 1 on findings"
Assert-True ($script:LastReport -match '\[CRITICAL\] claude --version failed') "claude probe failure is CRITICAL"
$snap = Get-Content $SnapshotFile -Raw | ConvertFrom-Json
Assert-True ($snap.claude -eq "9.9.9") "failed probe carries last known claude version forward"
$pend = Get-Pending
Assert-True ($pend.Count -eq 1 -and $pend[0].status -eq "manual-triage-needed") "pending: manual-triage-needed"
Assert-True ((Get-Toasts) -match 'CRITICAL') "manual CRITICAL toast fired"
Complete-Scenario $b

# --- scenario: blocked-verdict ---------------------------------------------------
# VERDICT: BLOCKED is a valid grammar line but never a trusted outcome; the
# run falls to manual. A pre-seeded unresolved prior run must re-toast.

$b = $script:failCount
Reset-State
$old = @(
    @{ status = "manual-triage-needed"; stamp = "2026-01-01_000000"
       report = "tools\drift-reports\2026-01-01_000000.txt"; branch = "" }
)
ConvertTo-Json -InputObject $old -Depth 3 | Set-Content -Path $PendingFile
Invoke-Drift "blocked-verdict" "blocked" "drop-config" 60000
Assert-True ($script:LastReport -match "Auto-triage not trusted \(exit 0; verdict 'BLOCKED") "BLOCKED falls to the manual path"
Assert-True ((Get-Toasts) -match 'UNRESOLVED prior') "unresolved prior run re-toasted"
$pend = Get-Pending
Assert-True ($pend.Count -eq 2) "old pending entry kept, new one appended"
Complete-Scenario $b

# --- scenario: no-verdict --------------------------------------------------------
# An agent run with no strict verdict line is never trusted, whatever its
# exit code says.

$b = $script:failCount
Reset-State
Invoke-Drift "no-verdict" "" "drop-config" 60000
Assert-True ($script:LastReport -match "Auto-triage not trusted \(exit 0; verdict ''") "verdict-less run is not trusted"
$pend = Get-Pending
Assert-True ($pend.Count -eq 1 -and $pend[0].status -eq "manual-triage-needed") "pending: manual-triage-needed"
Complete-Scenario $b

# --- scenario: critical-dismissal ------------------------------------------------
# Trusted NO-ACTION (clean exit, verdict, no diff) silences the manual toast
# but a CRITICAL finding is never silently dismissed: VERIFY toast + pending.

$b = $script:failCount
Reset-State
Invoke-Drift "critical-dismissal" "noaction" "drop-config" 60000
Assert-True ($script:LastReport -match 'Auto-triage verdict: NO-ACTION') "trusted NO-ACTION recorded"
Assert-True ((Get-Toasts) -match 'VERIFY dismissal') "CRITICAL dismissal demands verification"
Assert-True (-not ((Get-Toasts) -match 'Contract-breaking')) "manual toast suppressed on trusted dismissal"
$pend = Get-Pending
Assert-True ($pend.Count -eq 1 -and $pend[0].status -eq "critical-dismissal-needs-verification") "pending: critical-dismissal-needs-verification"
Complete-Scenario $b

# --- scenario: warn-only-silence --------------------------------------------------
# The other half of the toast matrix: WARN-only noise (template hash drift,
# no CRITICAL) that triage dismisses must toast NOTHING and leave NO pending
# entry - the verdict lives in the archived report. A regression here turns
# the weekly watch into a nagging one, which is how people learn to ignore it.

$b = $script:failCount
Reset-State
Add-Content -Path $SpTemplate -Value "`nAn upstream edit that keeps both fingerprint literals.`n"
Invoke-Drift "warn-only-silence" "noaction" "" 60000
Assert-True ($script:LastReport -match '\[WARN\] installed superpowers code-reviewer\.md') "template hash drift is a WARN"
Assert-True (-not ($script:LastReport -match 'CRITICAL')) "no CRITICAL finding in this run"
Assert-True ($script:LastReport -match 'Auto-triage verdict: NO-ACTION') "trusted NO-ACTION recorded"
Assert-True ((Get-Toasts) -eq "") "WARN-only dismissal is SILENT - no toast at all"
Assert-True (-not (Test-Path $PendingFile)) "WARN-only dismissal leaves no pending entry"
Complete-Scenario $b

# --- scenario: pending-auto-clear -------------------------------------------------
# A fix-branch-open entry whose branch no longer exists (merged or
# discarded) clears itself; only this run's new entry remains.

$b = $script:failCount
Reset-State
$ghost = @(
    @{ status = "fix-branch-open"; stamp = "2026-01-02_000000"
       report = "tools\drift-reports\2026-01-02_000000.txt"; branch = "drift/ghost-00000" }
)
ConvertTo-Json -InputObject $ghost -Depth 3 | Set-Content -Path $PendingFile
Invoke-Drift "pending-auto-clear" "noaction" "drop-config" 60000
Assert-True ($script:LastReport -match 'Prior fix branch drift/ghost-00000 is gone') "vanished fix branch clears its pending entry"
Assert-True (-not ((Get-Toasts) -match 'UNRESOLVED')) "no unresolved re-toast after the auto-clear"
$pend = Get-Pending
Assert-True ($pend.Count -eq 1 -and $pend[0].status -eq "critical-dismissal-needs-verification") "only this run's new entry remains"
Complete-Scenario $b

# --- scenario: fixes-applied ------------------------------------------------------
# The full happy path: agent edits the worktree, script re-runs the pytest
# gate itself, commits, verifies the commit landed, gets the stub
# cross-review, toasts fix-ready, records fix-branch-open. SLOW (real
# pytest run inside the worktree).

$b = $script:failCount
Reset-State
Invoke-Drift "fixes-applied" "fixes" "drop-config" 120000
Assert-True ($script:LastReport -match 'committed on drift/') "fix committed on a drift branch"
Assert-True ($script:LastReport -match 'cross-review: PASS') "script-side cross-review verdict recorded"
Assert-True ((Get-Toasts) -match 'fix ready') "fix-ready toast fired"
$pend = Get-Pending
Assert-True ($pend.Count -eq 1 -and $pend[0].status -eq "fix-branch-open") "pending: fix-branch-open"
$fixBranch = ""
if ($pend.Count -ge 1) { $fixBranch = $pend[0].branch }
git -C $Clone rev-parse --verify --quiet $fixBranch > $null 2>&1
Assert-True ($LASTEXITCODE -eq 0) "fix branch exists with the verified commit"
if ($fixBranch) { git -C $Clone branch -D $fixBranch 2>&1 | Out-Null }
Complete-Scenario $b

# --- scenario: gate-failure --------------------------------------------------------
# The load-bearing safety property of the whole auto-triage: the SCRIPT
# re-runs the suite and refuses to believe a "FIXES-APPLIED" claim it
# cannot verify. The stub plants a genuinely failing test, so only a real
# pytest run can catch it. SLOW (real pytest run).

$b = $script:failCount
Reset-State
Invoke-Drift "gate-failure" "badfix" "drop-config" 120000
Assert-True ($script:LastReport -match 'claimed FIXES-APPLIED but the gate FAILED - changes discarded') "a fix that breaks the suite is rejected by the script's own gate"
Assert-True (-not ($script:LastReport -match 'committed on drift/')) "no commit claim on a failed gate"
Assert-True (-not ((Get-Toasts) -match 'fix ready')) "no success toast on a failed gate"
Assert-True ((Get-Toasts) -match 'CRITICAL') "manual toast on a failed gate"
Assert-True (-not (Get-DriftBranches)) "no drift branch survives a failed gate"
$pend = Get-Pending
Assert-True ($pend.Count -eq 1 -and $pend[0].status -eq "manual-triage-needed") "pending: manual-triage-needed"
Complete-Scenario $b

# --- scenario: malformed-review -----------------------------------------------------
# An off-grammar cross-review answer (injected text, a chatty model, a
# truncated file) must read as UNAVAILABLE - never as a review that passed.
# The fix still lands: the human merge decision is the real gate. SLOW.

$b = $script:failCount
Reset-State
# 'bad-review' keeps codex's flag surface HEALTHY, so it raises no finding
# of its own - and with nothing found, the script never reaches triage at
# all. Drive the run with the template WARN instead.
Add-Content -Path $SpTemplate -Value "`nAn upstream edit that keeps both fingerprint literals.`n"
Invoke-Drift "malformed-review" "fixes" "bad-review" 120000
Assert-True ($script:LastReport -match 'committed on drift/') "the verified fix still commits"
Assert-True ($script:LastReport -match 'cross-review UNAVAILABLE') "off-grammar review reads as UNAVAILABLE"
Assert-True (-not ($script:LastReport -match 'cross-review: ')) "an off-grammar answer is never reported as a reviewer verdict"
Assert-True ((Get-Toasts) -match 'cross-review UNAVAILABLE') "the toast carries the UNAVAILABLE state, not silence"
$pend = Get-Pending
if ($pend.Count -ge 1 -and $pend[0].branch) { git -C $Clone branch -D $pend[0].branch 2>&1 | Out-Null }
Complete-Scenario $b

# --- scenario: commit-failure -----------------------------------------------------
# Gate green but the commit itself fails (pre-commit hook): never toast
# success, discard the changes, keep no branch. SLOW (real pytest run).

$b = $script:failCount
Reset-State
$hookPath = Join-Path $Clone ".git\hooks\pre-commit"
[IO.File]::WriteAllText($hookPath, "#!/bin/sh`nexit 1`n")
Invoke-Drift "commit-failure" "fixes" "drop-config" 120000
Remove-Item $hookPath -Force
Assert-True ($script:LastReport -match 'commit FAILED - changes discarded') "failed commit is reported and discarded"
Assert-True ((Get-Toasts) -match 'CRITICAL') "manual toast on commit failure"
$pend = Get-Pending
Assert-True ($pend.Count -eq 1 -and $pend[0].status -eq "manual-triage-needed") "pending: manual-triage-needed"
Assert-True (-not (Get-DriftBranches)) "no orphan drift branch survives a failed commit"
Complete-Scenario $b

# --- scenario: route-mismatch ------------------------------------------------------
# The effective-route check: a header model that differs from the canonical
# declaration reads as UNAVAILABLE - the reviewer reply is never trusted,
# however well-formed (it came over an unverified route). The fix still
# lands; the human merge decision is the real gate. SLOW (real pytest run).

$b = $script:failCount
Reset-State
# wrong-model keeps codex's flag surface healthy (no finding of its own) -
# drive the run with the template WARN, same as malformed-review.
Add-Content -Path $SpTemplate -Value "`nAn upstream edit that keeps both fingerprint literals.`n"
Invoke-Drift "route-mismatch" "fixes" "wrong-model" 120000
Assert-True ($script:LastReport -match 'committed on drift/') "the verified fix still commits"
Assert-True ($script:LastReport -match 'effective route mismatch') "header/canonical disagreement is reported as a route mismatch"
Assert-True ($script:LastReport -match 'cross-review UNAVAILABLE') "route mismatch reads as UNAVAILABLE"
Assert-True (-not ($script:LastReport -match 'cross-review: ')) "a mismatched route is never reported as a reviewer verdict"
$pend = Get-Pending
if ($pend.Count -ge 1 -and $pend[0].branch) { git -C $Clone branch -D $pend[0].branch 2>&1 | Out-Null }
Complete-Scenario $b

# --- scenario: auth-preflight-fail -------------------------------------------------
# A failed `codex login status` preflight skips the billable review call
# entirely and records the crisp auth reason. SLOW (real pytest run).

$b = $script:failCount
Reset-State
Add-Content -Path $SpTemplate -Value "`nAn upstream edit that keeps both fingerprint literals.`n"
Invoke-Drift "auth-preflight-fail" "fixes" "auth-fail" 120000
Assert-True ($script:LastReport -match 'committed on drift/') "the verified fix still commits"
Assert-True ($script:LastReport -match 'cross-review UNAVAILABLE - codex auth not ready') "failed preflight records the auth reason"
Assert-True (-not ($script:LastReport -match 'cross-review: ')) "no reviewer verdict without a passed preflight"
$pend = Get-Pending
if ($pend.Count -ge 1 -and $pend[0].branch) { git -C $Clone branch -D $pend[0].branch 2>&1 | Out-Null }
Complete-Scenario $b

# --- scenario: kimi-flag-drift (help drops --agent-file -> the flag finding) -------

$b = $script:failCount
Reset-State
$env:KIMI_STUB_MODE = "drop-agent-file"
Invoke-Drift "kimi-flag-drift" "noaction" "" 60000
Assert-True ($script:LastReport -match [regex]::Escape("no longer lists --agent-file")) "flag drop raises the agent-file drift finding"
Assert-True ($script:LastReport -notmatch "kimi_cli tool modules") "vocabulary probe stays quiet on a flag-only drop"
Remove-Item Env:KIMI_STUB_MODE -ErrorAction SilentlyContinue
Complete-Scenario $b

# --- scenario: kimi-short-flag-drift (help keeps --model but drops -m) -------------

$b = $script:failCount
Reset-State
$env:KIMI_STUB_MODE = "drop-short-m"
Invoke-Drift "kimi-short-flag-drift" "noaction" "" 60000
Assert-True ($script:LastReport -match [regex]::Escape("no longer lists -m")) "token-boundary probe catches a dropped short flag despite --model remaining"
Remove-Item Env:KIMI_STUB_MODE -ErrorAction SilentlyContinue
Complete-Scenario $b

# --- scenario: kimi-vocab-drift (import failure -> containment-vocabulary finding) -

$b = $script:failCount
Reset-State
$env:PYTHON_STUB_MODE = "kimi-import-fail"
Invoke-Drift "kimi-vocab-drift" "noaction" "" 60000
Assert-True ($script:LastReport -match [regex]::Escape("kimi_cli tool modules no longer import")) "import failure raises the vocabulary drift finding"
Remove-Item Env:PYTHON_STUB_MODE -ErrorAction SilentlyContinue
Complete-Scenario $b

# --- scenario: kimi-version-carry (failed probe never clobbers the snapshot) -------

$b = $script:failCount
Set-SnapshotWithKimi "1.2.3" "7.7.7" "6.1.1" "9.9.9"
Copy-Item $PinnedFixture $SpTemplate -Force
if (Test-Path $PendingFile) { Remove-Item $PendingFile -Force }
if (Test-Path $ReportsDir) { Remove-Item -Recurse -Force $ReportsDir }
$env:KIMI_STUB_MODE = "version-fail"
Invoke-Drift "kimi-version-carry" "noaction" "" 60000
$snapAfter = Get-Content $SnapshotFile -Raw | ConvertFrom-Json
Assert-True ($snapAfter.kimi -eq "9.9.9") "failed kimi probe carries the last known-good version forward"
Assert-True ($script:LastReport -match "backup-lane probes skipped") "skip note is emitted instead of a cascade"
Remove-Item Env:KIMI_STUB_MODE -ErrorAction SilentlyContinue
Complete-Scenario $b

# --- scenario: triage-timeout (LAST - see header) ----------------------------------
# A hung agent is killed at the cap and the run falls to manual.

$b = $script:failCount
Reset-State
Invoke-Drift "triage-timeout" "hang" "drop-config" 2000
Assert-True ($script:LastReport -match 'Auto-triage TIMED OUT') "hung agent killed at the cap"
Assert-True ((Get-Toasts) -match 'CRITICAL') "manual toast after the timeout"
$pend = Get-Pending
Assert-True ($pend.Count -eq 1 -and $pend[0].status -eq "manual-triage-needed") "pending: manual-triage-needed"
Complete-Scenario $b

# --- summary -----------------------------------------------------------------------

Write-Output ""
if ($script:failCount -eq 0) {
    Write-Output "ALL SCENARIOS PASS"
} else {
    Write-Output "$($script:failCount) ASSERTION(S) FAILED"
}

} finally {
    # Restore the caller's environment before anything else: this harness is
    # runnable from an interactive shell, and leaving a fake USERPROFILE or
    # a stub-laden PATH behind would be worse than any test it runs.
    foreach ($name in $savedEnv.Keys) {
        [Environment]::SetEnvironmentVariable($name, $savedEnv[$name], "Process")
    }
    if (-not $KeepTemp) {
        # Everything - clone, stubs, fake profile, and every worktree the
        # script created (its TEMP was ours) - lives under $Root. The killed
        # timeout stub can hold a handle for a few seconds; retry briefly
        # rather than sweeping by name.
        $removed = $false
        foreach ($attempt in 1..6) {
            try {
                Remove-Item -Recurse -Force $Root -ErrorAction Stop
                $removed = $true
                break
            } catch {
                Start-Sleep -Seconds 3
            }
        }
        if (-not $removed) { Write-Output "note: temp left behind at $Root" }
    } else {
        Write-Output "temp kept at $Root"
    }
}

exit $script:failCount
