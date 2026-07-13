# drift_statemachine_tests.ps1 - offline state-machine tests for
# tools/check-drift.ps1.
#
# Drives the REAL script end to end - probe, canary, auto-triage, verdict
# trust matrix, commit gate, cross-review, toast matrix, pending lifecycle -
# with every external dependency stubbed:
#   - a throwaway git clone of this repo is the script's $RepoRoot (its own
#     worktrees, branches, and state files never touch the real checkout);
#     the WORKING-TREE check-drift.ps1 is copied over the clone's so
#     uncommitted edits are what gets tested
#   - stub claude.cmd / codex.ps1 on a prepended PATH, behavior selected per
#     scenario via CLAUDE_STUB_MODE / CODEX_STUB_MODE
#   - a fake USERPROFILE holding a valid plugin registry pointing at a fake
#     superpowers install seeded from the pinned fixture (so the template
#     canary passes and the findings driver is the codex flag probe)
#   - the script's two test seams: CROSSCHECK_DRIFT_TOAST_LOG captures
#     toasts to a file, CROSSCHECK_DRIFT_TRIAGE_TIMEOUT_MS shrinks the
#     30-min agent cap to seconds
#
# Scenarios (in run order; triage-timeout LAST - its killed stub can orphan
# a child that briefly holds the worktree, so nothing may run after it):
#   carry-forward      failed version probe keeps the snapshot value
#   blocked-verdict    BLOCKED falls to manual; prior pending re-toasts
#   no-verdict         a verdict-less agent run is not trusted
#   critical-dismissal trusted NO-ACTION on a CRITICAL toasts VERIFY
#   pending-auto-clear a vanished fix branch clears its pending entry
#   fixes-applied      diff -> pytest gate -> commit -> Sol review -> toast
#   commit-failure     failed commit discards changes, keeps no branch
#   triage-timeout     hung agent is killed at the cap
#
# Runtime: several minutes (fixes-applied and commit-failure each re-run the
# full pytest suite inside the disposable worktree, exactly as production
# does). Run directly, or via pytest with CROSSCHECK_STATEMACHINE=1 set
# (test_multi_model_verify.py::TestDriftStateMachine::test_run_state_machine).
#
# Windows PowerShell 5.1, ASCII ONLY (same rules as the script under test).
# Exit code = number of failed assertions (0 = all pass).

param(
    [switch]$KeepTemp
)

$HarnessStart = Get-Date
$HarnessRoot = $PSScriptRoot                      # evals\tools
$RepoRoot = Split-Path (Split-Path $HarnessRoot)  # repo root
$Root = Join-Path $env:TEMP ("crosscheck-sm-" + (Get-Date -Format "HHmmss") + "-" + (Get-Random -Maximum 9999))
New-Item -ItemType Directory -Force -Path $Root | Out-Null

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
# The fixes mode writes into its CWD, which the script sets to the worktree.
# The hang mode never exits on its own so the kill path always fires.
@'
@echo off
if "%~1"=="--version" goto version
if "%CLAUDE_STUB_MODE%"=="version-fail" exit /b 1
if "%CLAUDE_STUB_MODE%"=="hang" goto hang
if "%CLAUDE_STUB_MODE%"=="blocked" goto blocked
if "%CLAUDE_STUB_MODE%"=="noaction" goto noaction
if "%CLAUDE_STUB_MODE%"=="fixes" goto fixes
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
'@ | Set-Content -Path (Join-Path $StubDir "claude.cmd") -Encoding ASCII

# codex.ps1: healthy transport by default; drop-config removes one flag from
# exec --help so the probe raises exactly one CRITICAL (the findings driver
# for scenarios where claude itself must stay healthy). exec with
# --output-last-message answers the cross-review with REVIEW: PASS.
@'
$null = @($input)
$argList = @($args)
if ($argList -contains "--version") { Write-Output "codex-cli 7.7.7"; exit 0 }
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
    Set-Content -Path $argList[$idx + 1] -Value "REVIEW: PASS"
}
exit 0
'@ | Set-Content -Path (Join-Path $StubDir "codex.ps1") -Encoding ASCII

$env:PATH = "$StubDir;" + $env:PATH

# Fake profile: plugin registry -> fake superpowers install seeded from the
# pinned fixture, so the template canary passes offline; .gitconfig gives
# the script's worktree commits an identity. Faking USERPROFILE also makes
# the nested pytest gate's registry-reading test resolve here.
$FakeProfile = Join-Path $Root "profile"
$FakeSp = Join-Path $FakeProfile ".claude\plugins\cache\claude-plugins-official\superpowers\6.1.1"
New-Item -ItemType Directory -Force -Path (Join-Path $FakeSp "skills\requesting-code-review") | Out-Null
# A fake USERPROFILE needs a real profile's shell-folder skeleton: PS 5.1
# resolves its job persistence path through USERPROFILE-expanded folders,
# and without them the script's Start-Job cross-review dies on Receive-Job
# with "The Persistence Path does not exist" (probed 2026-07-13 - the miss
# is silent, it just degrades every review to UNAVAILABLE).
foreach ($dir in @("Documents", "AppData\Roaming", "AppData\Local", "AppData\LocalLow")) {
    New-Item -ItemType Directory -Force -Path (Join-Path $FakeProfile $dir) | Out-Null
}
Copy-Item (Join-Path $Clone "evals\multi-model-verify\fixtures\superpowers-code-reviewer-6.1.1.md") `
    (Join-Path $FakeSp "skills\requesting-code-review\code-reviewer.md")
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
# Recursion guard: after this branch merges, the worktree suite contains the
# pytest wrapper for THIS harness - it must skip inside a state-machine run.
$env:CROSSCHECK_DRIFT_STATEMACHINE = "1"

# --- helpers ------------------------------------------------------------------

function Set-Snapshot($claude, $codex, $sp) {
    $snap = @{ claude = $claude; codex = $codex; superpowers = $sp; updated = "2026-01-01T00:00:00" }
    ConvertTo-Json -InputObject $snap | Set-Content -Path $SnapshotFile
}

function Reset-State {
    # Defaults match the stub versions exactly: no version-change notes, no
    # changelog fetch - every scenario runs fully offline.
    Set-Snapshot "1.2.3" "7.7.7" "6.1.1"
    if (Test-Path $PendingFile) { Remove-Item $PendingFile -Force }
    if (Test-Path $ReportsDir) { Remove-Item -Recurse -Force $ReportsDir }
}

function Invoke-Drift($scenario, $claudeMode, $codexMode, $timeoutMs) {
    Write-Output ""
    Write-Output "SCENARIO $scenario"
    $toastLog = Join-Path $Root "$scenario-toasts.txt"
    if (Test-Path $toastLog) { Remove-Item $toastLog -Force }
    $env:CROSSCHECK_DRIFT_TOAST_LOG = $toastLog
    $env:CROSSCHECK_DRIFT_TRIAGE_TIMEOUT_MS = "$timeoutMs"
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
    # single-entry array back into a bare object (first live run failed
    # exactly there: .Count is null on a PSCustomObject in PS 5.1).
    $parsed = Get-Content $PendingFile -Raw | ConvertFrom-Json
    return , @($parsed)
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
# gate itself, commits, verifies the commit landed, gets the stub Sol
# cross-review, toasts fix-ready, records fix-branch-open. SLOW (real
# pytest run inside the worktree).

$b = $script:failCount
Reset-State
Invoke-Drift "fixes-applied" "fixes" "drop-config" 120000
Assert-True ($script:LastReport -match 'committed on drift/') "fix committed on a drift branch"
Assert-True ($script:LastReport -match 'Sol review: PASS') "script-side cross-review verdict recorded"
Assert-True ((Get-Toasts) -match 'fix ready') "fix-ready toast fired"
$pend = Get-Pending
Assert-True ($pend.Count -eq 1 -and $pend[0].status -eq "fix-branch-open") "pending: fix-branch-open"
$fixBranch = ""
if ($pend.Count -ge 1) { $fixBranch = $pend[0].branch }
git -C $Clone rev-parse --verify --quiet $fixBranch > $null 2>&1
Assert-True ($LASTEXITCODE -eq 0) "fix branch exists with the verified commit"
if ($fixBranch) { git -C $Clone branch -D $fixBranch 2>&1 | Out-Null }
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
$leftover = (git -C $Clone branch --list "drift/*" 2>&1 | Out-String).Trim()
Assert-True (-not $leftover) "no orphan drift branch survives a failed commit"
Complete-Scenario $b

# --- scenario: triage-timeout (LAST - see header) ----------------------------------
# A hung agent is killed at the cap and the run falls to manual. The killed
# stub's ping child can hold the worktree open for a few seconds, so this
# scenario runs last and cleanup below waits it out.

$b = $script:failCount
Reset-State
Invoke-Drift "triage-timeout" "hang" "drop-config" 2000
Assert-True ($script:LastReport -match 'Auto-triage TIMED OUT') "hung agent killed at the cap"
Assert-True ((Get-Toasts) -match 'CRITICAL') "manual toast after the timeout"
$pend = Get-Pending
Assert-True ($pend.Count -eq 1 -and $pend[0].status -eq "manual-triage-needed") "pending: manual-triage-needed"
Complete-Scenario $b

# --- summary + cleanup --------------------------------------------------------------

Write-Output ""
if ($script:failCount -eq 0) {
    Write-Output "ALL SCENARIOS PASS"
} else {
    Write-Output "$($script:failCount) ASSERTION(S) FAILED"
}

if (-not $KeepTemp) {
    Start-Sleep -Seconds 10  # let the timeout scenario's orphaned ping exit
    try { Remove-Item -Recurse -Force $Root -ErrorAction Stop } catch {
        Write-Output "note: temp left behind at $Root ($($_.Exception.Message))"
    }
    # Worktrees the killed run could not remove live directly under TEMP;
    # only touch ones created during THIS harness run.
    Get-ChildItem $env:TEMP -Directory -Filter "crosscheck-drift-*" -ErrorAction SilentlyContinue |
        Where-Object { $_.CreationTime -ge $HarnessStart } |
        ForEach-Object { try { Remove-Item -Recurse -Force $_.FullName } catch {} }
} else {
    Write-Output "temp kept at $Root"
}

exit $script:failCount
