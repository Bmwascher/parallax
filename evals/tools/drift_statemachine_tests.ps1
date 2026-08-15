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
#   blocked-crash      a BLOCKED line on a nonzero exit is a runner failure
#   credits-death      an out-of-credits death toasts AUTO-TRIAGE FAILED
#   failure-resurfaces a missed failure toast re-surfaces next run
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
#   kimi-short-flag-drift help drops -m only -> the flag finding
#   kimi-below-floor   installed version parses below the lane floor
#   kimi-unparseable-version version does not parse against the floor
#   kimi-version-carry a present-but-broken probe is a finding, not a note,
#                      and still never clobbers the snapshot
#   agy-contracts-clean   the positive control: a healthy lane is silent
#   agy-version-unreadable an unreadable version is a FINDING with a
#                      NON-CLEAN exit, and the prior value survives
#   agy-version-fail   a failed --version is the same class
#   agy-version-changed a changed version is REPORTED, not carried silently
#   agy-model-renamed  the lane's model literal is gone from `agy models`
#   agy-models-fail    the identity check could not be made at all
#   agy-settings-missing / -malformed / -trustedworkspaces-shape /
#                      -trustedworkspaces-absent  the settings contract
#   agy-brain-missing  the authorship-evidence root is gone
#   agy-absent         an optional lane that is not installed is a NOTE
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
                    "LOCALAPPDATA",
                    "CLAUDE_STUB_MODE", "CODEX_STUB_MODE",
                    "KIMI_STUB_MODE", "AGY_STUB_MODE",
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

function Write-StubFile($body, $path) {
    <#
      Write a stub with CRLF line endings, ALWAYS. This is not cosmetic.

      cmd.exe cannot find a batch LABEL in an LF-only file: `goto badfix`
      fails with "The system cannot find the batch label specified", the
      stub exits 1 having done nothing, and the drift script correctly
      reports an untrusted auto-triage. The scenario then fails while
      looking like a fault in the thing under test.

      The stub bodies below are here-strings, so they inherit THE LINE
      ENDINGS OF THIS FILE. That made every .cmd stub silently depend on
      git rewriting this file to CRLF at checkout: fine on a fresh clone,
      broken the moment an editor writes LF. Measured 2026-08-11 -
      `gate-failure` fell over on a working copy whose endings had been
      normalized to LF, while the same scenario passed in a checked-out
      baseline worktree an hour earlier. A test harness must not depend on
      how its own source happens to be stored.
    #>
    [IO.File]::WriteAllText($path, (($body -replace "`r?`n", "`r`n") + "`r`n"),
                            (New-Object System.Text.ASCIIEncoding))
}

# claude.cmd: version probe + the triage agent, mode via CLAUDE_STUB_MODE.
# fixes/badfix write into the CWD, which the script sets to the worktree:
# 'fixes' makes a harmless change, 'badfix' plants a FAILING test so the
# script's own pytest gate is what has to catch it.
# The hang mode never exits on its own so the kill path always fires.
$claudeStub = @'
@echo off
if "%~1"=="--version" goto version
if "%CLAUDE_STUB_MODE%"=="version-fail" exit /b 1
if "%CLAUDE_STUB_MODE%"=="hang" goto hang
if "%CLAUDE_STUB_MODE%"=="blocked" goto blocked
if "%CLAUDE_STUB_MODE%"=="noaction" goto noaction
if "%CLAUDE_STUB_MODE%"=="fixes" goto fixes
if "%CLAUDE_STUB_MODE%"=="badfix" goto badfix
if "%CLAUDE_STUB_MODE%"=="credits" goto credits
if "%CLAUDE_STUB_MODE%"=="blocked-crash" goto blockedcrash
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

:blockedcrash
echo Findings reviewed; cannot resolve offline.
echo VERDICT: BLOCKED stub cannot resolve this class of drift
exit /b 1

:credits
echo You're out of usage credits. Run /usage-credits to keep using Fable 5 or /model to switch models.
echo stub runner warning on stderr 1>&2
exit /b 1

:badfix
echo def test_stub_planted_failure():> evals\multi-model-verify\test_zz_stub_planted.py
echo     assert False, "planted by the state-machine harness">> evals\multi-model-verify\test_zz_stub_planted.py
echo Applied a fix that breaks the suite.
echo VERDICT: FIXES-APPLIED stub fix that breaks the gate
exit /b 0
'@
Write-StubFile $claudeStub (Join-Path $StubDir "claude.cmd")

# codex.ps1: healthy transport by default.
#   drop-config  - exec --help omits --config, so the flag probe raises
#                  exactly one CRITICAL (the findings driver when claude
#                  itself must stay healthy)
#   bad-review   - the cross-review answers off-grammar, which must read as
#                  UNAVAILABLE, never as a passed review
$codexStub = @'
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
'@
Write-StubFile $codexStub (Join-Path $StubDir "codex.ps1")

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
$SpTemplate = Join-Path $FakeProfile ".claude\plugins\cache\claude-plugins-official\superpowers\6.2.0\skills\requesting-code-review\code-reviewer.md"
$FakeSp = Join-Path $FakeProfile ".claude\plugins\cache\claude-plugins-official\superpowers\6.2.0"
New-Item -ItemType Directory -Force -Path (Split-Path $SpTemplate) | Out-Null
$PinnedFixture = Join-Path $Clone "evals\multi-model-verify\fixtures\superpowers-code-reviewer-6.2.0.md"
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
            @{ version = "6.2.0"; installPath = $FakeSp }
        )
    }
}
ConvertTo-Json -InputObject $registry -Depth 5 | Set-Content -Path (Join-Path $FakeProfile ".claude\plugins\installed_plugins.json")
[IO.File]::WriteAllText((Join-Path $FakeProfile ".gitconfig"),
    "[user]`n`tname = drift-harness`n`temail = drift@localhost`n")

# kimi-code stub: the production lookup is the ABSOLUTE path
# $env:USERPROFILE\.kimi-code\bin\{kimi.exe,kimi.cmd}, not a PATH entry, so
# the stub is placed under the fake profile set below - no new environment
# variable is introduced that could redirect the REAL lookup (the lock-
# stealing shape this repo has already been bitten by twice). A .cmd
# renamed .exe does not execute on Windows, so only the .cmd name can be
# stubbed offline; production tries kimi.exe first, then kimi.cmd.
$KimiBin = Join-Path $FakeProfile ".kimi-code\bin"
New-Item -ItemType Directory -Force -Path $KimiBin | Out-Null
$kimiStub = @'
@echo off
if "%~1"=="--version" goto version
if "%~1"=="--help" goto help
exit /b 0

:version
if "%KIMI_STUB_MODE%"=="version-fail" exit /b 1
if "%KIMI_STUB_MODE%"=="below-floor" (
echo kimi, version 0.30.0
exit /b 0
)
if "%KIMI_STUB_MODE%"=="unparseable" (
echo kimi, version 0.31.1-devbuild
exit /b 0
)
echo kimi, version 9.9.9
exit /b 0

:help
if "%KIMI_STUB_MODE%"=="drop-agent-file" (
echo usage: kimi [--skills-dir DIR] [-m MODEL] [-p PROMPT] [--session ID]
exit /b 0
)
if "%KIMI_STUB_MODE%"=="drop-short-m" (
echo usage: kimi [--agent-file FILE] [--skills-dir DIR] [-p PROMPT] [--session ID]
exit /b 0
)
echo usage: kimi [--agent-file FILE] [--skills-dir DIR] [-m MODEL] [-p PROMPT] [--session ID]
exit /b 0
'@
Write-StubFile $kimiStub (Join-Path $KimiBin "kimi.cmd")

# agy stub, and LOCALAPPDATA redirected to reach it.
#
# THIS REDIRECTION IS NOT TIDINESS. 0.24.0 added agy CONTRACT checks to
# check-drift, including an `agy models` call. LOCALAPPDATA was not
# redirected here, so every scenario in this offline harness would have
# found the REAL agy on the developer's machine and made a REAL network
# call against a lane whose free-tier quota the doctor already calls
# opaque. An offline harness that reaches a live service is not offline,
# and the failure would have been slow and quota-shaped rather than red.
$FakeLocalAppData = Join-Path $FakeProfile "AppData\Local"
$AgyBin = Join-Path $FakeLocalAppData "agy\bin"
New-Item -ItemType Directory -Force -Path $AgyBin | Out-Null
# Same .cmd-only constraint as kimi above: a .cmd renamed .exe does not
# execute on Windows, so only the .cmd name can be stubbed offline, and
# production tries agy.exe first then agy.cmd.
#
# THE MODEL LITERAL HAS ONE HOME and this harness must not become a second
# one. `test_flash_literal_single_source` sweeps evals/**/*.ps1 and fails
# on a copy; it caught this file. The pin is right for a reason beyond
# tidiness: a stub carrying the name keeps asserting the OLD name after a
# rename, which is the exact drift the check it exercises exists to catch.
$FlashAgentFile = Join-Path $RepoRoot "agents\flash-implementer.md"
$AgyModelLiteral = ""
if (Test-Path $FlashAgentFile) {
    if ((Get-Content -Raw -LiteralPath $FlashAgentFile) -match 'Canonical model literal:\s*`?\s*[\r\n]*\s*`([^`]+)`') {
        $AgyModelLiteral = $Matches[1].Trim()
    }
}
if (-not $AgyModelLiteral) {
    Write-Output "FATAL: could not parse the canonical model literal from $FlashAgentFile - this harness reads it rather than carrying a copy"
    exit 1
}
# The rename the check must catch. It must NOT contain the canonical
# literal as a substring, or the watcher's -notmatch test would still find
# the canonical name inside it and report no drift.
$AgyRenamedLiteral = "renamed-model-not-the-canonical-one"

$agyStub = @"
@echo off
if "%~1"=="--version" goto version
if "%~1"=="models" goto models
exit /b 0

:version
if "%AGY_STUB_MODE%"=="version-fail" exit /b 1
if "%AGY_STUB_MODE%"=="version-fail-loud" (
echo 1.1.12
exit /b 1
)
if "%AGY_STUB_MODE%"=="unparseable" (
echo agy version devbuild
exit /b 0
)
if "%AGY_STUB_MODE%"=="version-changed" (
echo 2.0.0
exit /b 0
)
echo 1.1.12
exit /b 0

:models
REM NO PARENTHESES IN THESE ECHOES. The real `agy models` prints
REM "Gemini 3.6 Flash (Medium)", and copying that shape here broke the
REM stub silently: a ")" inside an IF block closes the block early, so cmd
REM mis-parsed everything after it and the DEFAULT branch printed nothing
REM at all. Exit 0, no output, and the watcher correctly reported the
REM model as missing - a stub bug wearing the face of a real finding, in
REM four scenarios at once. The contract only needs the literal.
if "%AGY_STUB_MODE%"=="models-fail" exit /b 4
if "%AGY_STUB_MODE%"=="model-renamed" (
echo $AgyRenamedLiteral  Renamed Flash Model
exit /b 0
)
echo $AgyModelLiteral  Canonical Flash Model
exit /b 0
"@
Write-StubFile $agyStub (Join-Path $AgyBin "agy.cmd")

# Check the stubs THEMSELVES, before any scenario runs. An LF-only .cmd
# does not announce itself: `goto` fails, the stub exits 1 having done
# nothing, and the drift script honestly reports an untrusted auto-triage
# three hundred lines later. That reads as a fault in the thing under test.
# Measured 2026-08-11: it cost an hour and two full harness runs to trace
# back. This names the cause on line one instead.
foreach ($stub in @((Join-Path $StubDir "claude.cmd"),
                    (Join-Path $KimiBin "kimi.cmd"),
                    (Join-Path $AgyBin "agy.cmd"))) {
    $bytes = [IO.File]::ReadAllBytes($stub)
    $lf = 0
    $crlf = 0
    for ($i = 0; $i -lt $bytes.Length; $i++) {
        if ($bytes[$i] -eq 10) {
            $lf++
            if ($i -gt 0 -and $bytes[$i - 1] -eq 13) { $crlf++ }
        }
    }
    Assert-True ($lf -gt 0 -and $lf -eq $crlf) `
        ("stub is CRLF: " + (Split-Path -Leaf $stub) +
         " - cmd.exe cannot find a batch label in an LF-only file")
}

# The agy settings file and brain root the contract checks read. Both live
# under USERPROFILE, which is already redirected.
$AgyHome = Join-Path $FakeProfile ".gemini\antigravity-cli"
New-Item -ItemType Directory -Force -Path (Join-Path $AgyHome "brain") | Out-Null
$script:AgySettingsPath = Join-Path $AgyHome "settings.json"
function Set-AgySettings($json) {
    [IO.File]::WriteAllText($script:AgySettingsPath, $json)
}
Set-AgySettings '{"allowNonWorkspaceAccess": true, "trustedWorkspaces": ["C:\\fake\\repo"]}'
# Kept so the agy-absent scenario can delete the stub and Reset-State can
# put it back.
$script:AgyStubBackup = Join-Path $Root "agy-stub-backup.cmd"
Copy-Item (Join-Path $AgyBin "agy.cmd") $script:AgyStubBackup -Force

$env:USERPROFILE = $FakeProfile
$env:HOME = $FakeProfile
$env:LOCALAPPDATA = $FakeLocalAppData
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
    Set-Snapshot "1.2.3" "7.7.7" "6.2.0"
    Copy-Item $PinnedFixture $SpTemplate -Force
    if (Test-Path $PendingFile) { Remove-Item $PendingFile -Force }
    if (Test-Path $ReportsDir) { Remove-Item -Recurse -Force $ReportsDir }
    # agy back to a healthy lane: default stub mode, a settings file that
    # parses with the right shape, and a brain root that exists. Without
    # this reset a scenario that broke one of them would leak into every
    # scenario after it, and the leak would look like a real finding.
    $env:AGY_STUB_MODE = ""
    Set-AgySettings '{"allowNonWorkspaceAccess": true, "trustedWorkspaces": ["C:\\fake\\repo"]}'
    New-Item -ItemType Directory -Force -Path (Join-Path $FakeProfile ".gemini\antigravity-cli\brain") | Out-Null
    $agyStub = Join-Path $FakeLocalAppData "agy\bin\agy.cmd"
    if (-not (Test-Path $agyStub)) { Copy-Item $script:AgyStubBackup $agyStub -Force }
}

function Set-SnapshotWithAgy($claude, $codex, $sp, $agy) {
    $snap = @{ claude = $claude; codex = $codex; superpowers = $sp; agy = $agy; updated = "2026-01-01T00:00:00" }
    ConvertTo-Json -InputObject $snap | Set-Content -Path $SnapshotFile
}

function Set-SnapshotWithAgyAllow($claude, $codex, $sp, $agy, $allow) {
    $snap = @{ claude = $claude; codex = $codex; superpowers = $sp; agy = $agy
               agyAllowNonWorkspaceAccess = $allow; updated = "2026-01-01T00:00:00" }
    # -Depth 100 because a fixture written at the default depth 2 would
    # truncate a NESTED seeded value to "System.Collections.Hashtable", and
    # the nested scenarios would then be measuring this helper's defect
    # rather than the watcher's. A fixture must not be able to fail in the
    # direction the case is looking.
    ConvertTo-Json -InputObject $snap -Depth 100 | Set-Content -Path $SnapshotFile
}

function Get-SavedSnapshot {
    if (Test-Path $SnapshotFile) { return (Get-Content -Raw $SnapshotFile | ConvertFrom-Json) }
    return $null
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
Set-Snapshot "9.9.9" "7.7.7" "6.2.0"
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
# BLOCKED is the innocent case: the agent read every finding and stopped on
# purpose. Nothing is broken, so it must NOT record a runner failure -
# commands/drift-triage.md defines a non-empty `failure` as the automation
# never having looked at the findings, and tells a triage session to report
# the lane as down. It still gets its own toast, because a deliberate handoff
# is not a routine week either.
$toasts = Get-Toasts
Assert-True ($toasts -match 'auto-triage BLOCKED') "BLOCKED gets its own toast"
Assert-True (-not ($toasts -match 'AUTO-TRIAGE FAILED')) "BLOCKED is never reported as a runner failure"
$newEntry = $pend[$pend.Count - 1]
Assert-True (-not $newEntry.failure) "BLOCKED records no runner failure on the pending entry"
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
# An agent that produces no parseable verdict has not done its job either,
# so this counts as a runner failure - just a generic one, with no specific
# remedy to name. With auto-triage enabled, ANY manual fallback means the
# automation did not finish; the plain findings toast now fires only under
# -NoAutoTriage.
Assert-True ($pend[0].failure -match "not trusted \(exit 0, verdict ''\)") "a verdict-less run records a generic runner failure"
Complete-Scenario $b

# --- scenario: blocked-crash -----------------------------------------------------
# A BLOCKED line on a NONZERO exit is not a deliberate handoff. The agent
# died; it merely happened to print the grammar line first. Classifying that
# as BLOCKED would record an empty failure and tell /parallax:drift-triage the
# automation finished on purpose. Found by the cross-vendor lane in the 0.16.0
# diff debate, inside the fix for the whole-branch reviewer's own finding.

$b = $script:failCount
Reset-State
Invoke-Drift "blocked-crash" "blocked-crash" "drop-config" 60000
Assert-True ($script:LastReport -match "Auto-triage not trusted \(exit 1; verdict 'BLOCKED") "a crashed run carrying a BLOCKED line is not trusted"
$toasts = Get-Toasts
Assert-True ($toasts -match 'AUTO-TRIAGE FAILED') "nonzero-exit BLOCKED reports as a runner failure"
Assert-True (-not ($toasts -match 'auto-triage BLOCKED')) "a crashed run is never reported as a deliberate handoff"
$pend = Get-Pending
Assert-True ($pend[$pend.Count - 1].failure -match "not trusted \(exit 1") "the crash is recorded as the failure reason"
Complete-Scenario $b

# --- scenario: credits-death -----------------------------------------------------
# Reproduces the 2026-07-21 silent death: the agent dies on out-of-credits,
# the run falls to manual, and the toast used to be WORD FOR WORD an ordinary
# findings week - so it read as deferrable and sat six days across five
# releases. The toast must now name the automation as the thing that broke,
# the reason must ride on the pending entry, and the runner's own stderr must
# reach the report instead of a sidecar file nobody opens.

$b = $script:failCount
Reset-State
Invoke-Drift "credits-death" "credits" "drop-config" 60000
Assert-True ($script:LastReport -match "Auto-triage not trusted \(exit 1") "out-of-credits run is not trusted"
Assert-True ($script:LastReport -match "Auto-triage runner stderr") "runner stderr reaches the report"
Assert-True ($script:LastReport -match "stub runner warning on stderr") "the stderr TEXT reaches the report"
$toasts = Get-Toasts
Assert-True ($toasts -match 'AUTO-TRIAGE FAILED') "toast names the automation, not just the findings"
Assert-True ($toasts -match 'OUT OF USAGE CREDITS') "toast names the recurring cause"
$pend = Get-Pending
Assert-True ($pend.Count -eq 1 -and $pend[0].status -eq "manual-triage-needed") "pending: manual-triage-needed"
Assert-True ($pend[0].failure -match 'OUT OF USAGE CREDITS') "pending entry carries the failure reason"
Complete-Scenario $b

# --- scenario: failure-resurfaces ------------------------------------------------
# A missed AUTO-TRIAGE FAILED toast gets a second chance: the reason rides on
# the pending entry, so the NEXT run's unresolved-prior toast says the lane
# was down rather than just naming a stale stamp.

$b = $script:failCount
Reset-State
$old = @(
    @{ status = "manual-triage-needed"; stamp = "2026-01-03_000000"
       report = "tools\drift-reports\2026-01-03_000000.txt"; branch = ""
       failure = "OUT OF USAGE CREDITS - top up or switch model, then re-run triage" }
)
ConvertTo-Json -InputObject $old -Depth 3 | Set-Content -Path $PendingFile
Invoke-Drift "failure-resurfaces" "noaction" "drop-config" 60000
Assert-True ($script:LastReport -match "AUTO-TRIAGE FAILED: OUT OF USAGE CREDITS") "prior runner failure re-surfaces in the report"
Assert-True ((Get-Toasts) -match 'AUTO-TRIAGE FAILED: OUT OF USAGE CREDITS') "prior runner failure re-surfaces in the toast"
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
Assert-True ($script:LastReport -notmatch "is below the lane floor") "the floor check stays quiet on a flag-only drop"
Remove-Item Env:KIMI_STUB_MODE -ErrorAction SilentlyContinue
Complete-Scenario $b

# --- scenario: kimi-short-flag-drift (help drops -m only -> the flag finding) ------

$b = $script:failCount
Reset-State
$env:KIMI_STUB_MODE = "drop-short-m"
Invoke-Drift "kimi-short-flag-drift" "noaction" "" 60000
Assert-True ($script:LastReport -match [regex]::Escape("no longer lists -m")) "a dropped short flag is caught even with the other four intact"
Remove-Item Env:KIMI_STUB_MODE -ErrorAction SilentlyContinue
Complete-Scenario $b

# --- scenario: kimi-below-floor (installed version parses below the lane floor) ----

$b = $script:failCount
Reset-State
$env:KIMI_STUB_MODE = "below-floor"
Invoke-Drift "kimi-below-floor" "noaction" "" 60000
Assert-True ($script:LastReport -match [regex]::Escape("is below the lane floor")) "a below-floor version raises the floor finding"
Remove-Item Env:KIMI_STUB_MODE -ErrorAction SilentlyContinue
Complete-Scenario $b

# --- scenario: kimi-unparseable-version (version does not parse against the floor) -

$b = $script:failCount
Reset-State
$env:KIMI_STUB_MODE = "unparseable"
Invoke-Drift "kimi-unparseable-version" "noaction" "" 60000
Assert-True ($script:LastReport -match [regex]::Escape("is unparseable against floor")) "an unparseable version raises its own finding rather than passing the floor check"
Remove-Item Env:KIMI_STUB_MODE -ErrorAction SilentlyContinue
Complete-Scenario $b

# --- scenario: kimi-version-carry (a present-but-broken probe is a finding, not a --
# --- note, and still never clobbers the snapshot) ----------------------------------

$b = $script:failCount
Set-SnapshotWithKimi "1.2.3" "7.7.7" "6.2.0" "9.9.9"
Copy-Item $PinnedFixture $SpTemplate -Force
if (Test-Path $PendingFile) { Remove-Item $PendingFile -Force }
if (Test-Path $ReportsDir) { Remove-Item -Recurse -Force $ReportsDir }
$env:KIMI_STUB_MODE = "version-fail"
Invoke-Drift "kimi-version-carry" "noaction" "" 60000
$snapAfter = Get-Content $SnapshotFile -Raw | ConvertFrom-Json
Assert-True ($snapAfter.kimi -eq "9.9.9") "failed kimi probe carries the last known-good version forward"
Assert-True ($script:LastReport -match [regex]::Escape("did not report a usable version")) "a present-but-broken binary is reported as a finding, not silently skipped"
Remove-Item Env:KIMI_STUB_MODE -ErrorAction SilentlyContinue
Complete-Scenario $b

# --- agy lane contracts (0.24.0, backlog item 11) ---------------------------
#
# Until 0.24.0 the watcher ran `agy --version`, stored the string, and
# compared it to nothing. That is how the item's own quoted 1.1.8 became
# 1.1.12 across four releases with no report ever saying so.
#
# Every scenario below runs with the "noaction" claude stub so triage
# dismisses quickly: these cases are about what the REPORT and the EXIT
# CODE say, not about the triage loop, and a findings-week that re-ran the
# full pytest suite would add ten minutes each for nothing.

# --- scenario: agy-contracts-clean ------------------------------------------
# The positive control. Without it every "no agy finding" assertion below
# is satisfied by a watcher that never looked at agy at all.

$b = $script:failCount
Reset-State
Invoke-Drift "agy-contracts-clean" "noaction" "" 60000
Assert-True (-not ($script:LastReport -match 'agy')) "a healthy agy lane produces no agy finding and no agy note"
Assert-True ($script:LastExit -eq 0) "a clean run exits 0"
$snap = Get-SavedSnapshot
Assert-True ($snap.agy -eq "1.1.12") "the probed agy version is written to the snapshot"
Assert-True ("$($snap.agyAllowNonWorkspaceAccess)" -eq "True") "allowNonWorkspaceAccess is RECORDED so a change to it is visible next week"
Complete-Scenario $b

# --- scenario: agy-version-unreadable ---------------------------------------
# THE ONE THAT MATTERS MOST. The 0.24.0 plan's round-2 fix specified this
# as a NOTE. Notes print beside "No findings." and the exit is decided by
# findings alone, so an unmade measurement would have exited CLEAN - the
# exact false-clean the plan opens by forbidding. Round 3 caught it.
#
# Assert the EXIT CODE, not only the text: a report-only assertion passes
# identically whether the run exited 0 or non-zero, which is what made the
# defect invisible in the first place.

$b = $script:failCount
Reset-State
Set-SnapshotWithAgy "1.2.3" "7.7.7" "6.2.0" "1.1.9"
$env:AGY_STUB_MODE = "unparseable"
Invoke-Drift "agy-version-unreadable" "noaction" "" 60000
Assert-True ($script:LastReport -match '\[CRITICAL\] agy is installed at .* but did not report a usable version') "an unreadable agy version is a FINDING, not a note"
Assert-True ($script:LastExit -ne 0) "an unreadable agy version makes the run NON-CLEAN - a note would have exited 0"
$snap = Get-SavedSnapshot
Assert-True ($snap.agy -eq "1.1.9") "the prior snapshot value is PRESERVED, not overwritten with an empty one"
Complete-Scenario $b

# --- scenario: agy-version-fail ---------------------------------------------
# The binary is there and `--version` exits non-zero. Same class as above
# and the same direction: silence is not a version.

$b = $script:failCount
Reset-State
$env:AGY_STUB_MODE = "version-fail"
Invoke-Drift "agy-version-fail" "noaction" "" 60000
Assert-True ($script:LastReport -match '\[CRITICAL\] agy is installed at') "a failed agy --version is a finding"
Assert-True ($script:LastExit -ne 0) "a failed agy --version makes the run non-clean"
Complete-Scenario $b

# --- scenario: agy-version-fail-loud ----------------------------------------
# The divergent state the whole-branch review named: a client that exits
# NON-ZERO while printing something a version regex matches. The doctor
# calls that BROKEN. This block took stdout from a failed call as a
# measurement, recorded it, and stayed clean - so the two instruments the
# branch says were aligned disagreed about one fact. The kimi block one
# screen below has required exit 0 all along, so it was also a
# disagreement inside a single file.

$b = $script:failCount
Reset-State
Set-SnapshotWithAgy "1.2.3" "7.7.7" "6.2.0" "1.1.8"
$env:AGY_STUB_MODE = "version-fail-loud"
Invoke-Drift "agy-version-fail-loud" "noaction" "" 60000
Assert-True ($script:LastReport -match "'agy --version' exited 1") "a non-zero exit is a finding even when the output parses as a version"
Assert-True ($script:LastExit -ne 0) "a failed version call makes the run non-clean"
$snapAfter = Get-SavedSnapshot
Assert-True ($snapAfter.agy -eq "1.1.8") "the version printed by a FAILED call is discarded, not saved as measured"
# The assertion above is ALSO satisfied by a watcher that died before it
# rewrote the snapshot at all, which would leave the seeded file intact.
# It discriminated the defect it was written for - pre-fix, 1.1.12 was
# saved - but this closes the residual reading. Whole-branch review, second
# pass, minor 3.
Assert-True ($snapAfter.updated -ne "2026-01-01T00:00:00") "the snapshot was actually rewritten, so the carried version is a decision and not a leftover"
Complete-Scenario $b

# --- scenario: agy-allow-removed --------------------------------------------
# Removal is a change. The carry-forward restored last week's value
# whenever this run's read was empty, including when the key had VANISHED
# from a settings file that parsed - so the snapshot asserted a value the
# file no longer carried and no note fired. "A change to it is watched"
# was true of a changed value and false of a removed one.

$b = $script:failCount
Reset-State
Set-SnapshotWithAgyAllow "1.2.3" "7.7.7" "6.2.0" "1.1.12" "True"
Set-AgySettings '{"trustedWorkspaces": ["C:\\fake\\repo"]}'
Invoke-Drift "agy-allow-removed" "noaction" "" 60000
Assert-True ($script:LastReport -match 'allowNonWorkspaceAccess.*absent') "a REMOVED key is reported, not absorbed by the carry-forward"
$snapAfter = Get-SavedSnapshot
Assert-True (-not ($snapAfter.PSObject.Properties.Name -contains "agyAllowNonWorkspaceAccess")) "the removed key does not survive in the snapshot as a measured value"
Complete-Scenario $b

# --- scenario: agy-version-changed ------------------------------------------
# The gap item 11 was actually about. codex and superpowers had change
# notes; agy was carried forward and saved in silence.

$b = $script:failCount
Reset-State
Set-SnapshotWithAgy "1.2.3" "7.7.7" "6.2.0" "1.1.8"
Invoke-Drift "agy-version-changed" "noaction" "" 60000
Assert-True ($script:LastReport -match 'agy 1\.1\.8 -> 1\.1\.12') "an agy version change is REPORTED, not carried silently"
Assert-True ($script:LastExit -eq 0) "a readable version change is a note, so the run stays clean"
Complete-Scenario $b

# --- scenario: agy-model-renamed --------------------------------------------
# The lane's only reachability and identity check. A renamed model is the
# failure item 11 names first, and the literal is read from the agent file
# so this check cannot drift away from the lane it watches.

$b = $script:failCount
Reset-State
$env:AGY_STUB_MODE = "model-renamed"
Invoke-Drift "agy-model-renamed" "noaction" "" 60000
Assert-True ($script:LastReport -match ("no longer lists '" + [regex]::Escape($AgyModelLiteral) + "'")) "a renamed model is a finding naming the literal it looked for"
Assert-True ($script:LastExit -ne 0) "a renamed model makes the run non-clean"
Complete-Scenario $b

# --- scenario: agy-models-fail ----------------------------------------------
# An `agy models` that cannot run is not a passing identity check. Sign-out
# lands here, and the doctor already records that agy quota is opaque.

$b = $script:failCount
Reset-State
$env:AGY_STUB_MODE = "models-fail"
Invoke-Drift "agy-models-fail" "noaction" "" 60000
Assert-True ($script:LastReport -match "'agy models' exited 4") "a failed models call is a finding carrying the exit code"
Assert-True ($script:LastExit -ne 0) "a failed models call makes the run non-clean"
Complete-Scenario $b

# --- scenario: agy-settings-missing -----------------------------------------

$b = $script:failCount
Reset-State
Remove-Item -Force (Join-Path $FakeProfile ".gemini\antigravity-cli\settings.json")
Invoke-Drift "agy-settings-missing" "noaction" "" 60000
Assert-True ($script:LastReport -match '\[CRITICAL\] agy settings\.json is missing') "a missing settings file is a finding"
Assert-True ($script:LastExit -ne 0) "a missing settings file makes the run non-clean"
Complete-Scenario $b

# --- scenario: agy-settings-malformed ---------------------------------------
# An unreadable settings file is not an empty one. Parsing to nothing and
# then finding no forbidden key is the false-clean shape.

$b = $script:failCount
Reset-State
Set-AgySettings '{"trustedWorkspaces": ['
Invoke-Drift "agy-settings-malformed" "noaction" "" 60000
Assert-True ($script:LastReport -match 'did not parse as JSON') "an unparseable settings file is a finding, not an empty config"
Assert-True ($script:LastExit -ne 0) "an unparseable settings file makes the run non-clean"
Complete-Scenario $b

# --- scenario: agy-allow-null -----------------------------------------------
# PRESENCE is not the same question as VALUE. A key holding `null` is
# PRESENT, and reading presence off the value's truthiness made this run
# report the key as REMOVED, write a note saying so, and drop it from the
# snapshot - all about a key that is still sitting in the file. Diff debate
# round 1, claim 4, inside the fix written for the review's minor 6.

$b = $script:failCount
Reset-State
Set-SnapshotWithAgyAllow "1.2.3" "7.7.7" "6.2.0" "1.1.12" "True"
Set-AgySettings '{"allowNonWorkspaceAccess": null, "trustedWorkspaces": ["C:\\fake\\repo"]}'
Invoke-Drift "agy-allow-null" "noaction" "" 60000
Assert-True (-not ($script:LastReport -match 'allowNonWorkspaceAccess.*absent')) "a key holding null is PRESENT, and is never reported as removed"
$snapAfter = Get-SavedSnapshot
Assert-True ($snapAfter.PSObject.Properties.Name -contains "agyAllowNonWorkspaceAccess") "a present key with a null value still survives in the snapshot"
# SURVIVING IS NOT THE SAME AS SURVIVING AS ITSELF. Both assertions above
# are satisfied by a run that saves the WRONG value, and one did: the
# watcher cast every value through `[string]`, so `null` was recorded as
# the empty string. Diff debate round 2 named it, and these two close it.
Assert-True ($null -eq $snapAfter.agyAllowNonWorkspaceAccess) "a null value is saved as NULL, not flattened to an empty string"
Complete-Scenario $b

# --- scenario: agy-allow-null-to-empty --------------------------------------
# The change that the `[string]` cast made INVISIBLE. `null` and `""` are
# different settings values, and the whole point of recording this key is
# that a change to it is drift - but both rendered as the empty string, so
# the comparison found them equal and no note was written. Diff debate
# round 2.

$b = $script:failCount
Reset-State
Set-SnapshotWithAgyAllow "1.2.3" "7.7.7" "6.2.0" "1.1.12" $null
Set-AgySettings '{"allowNonWorkspaceAccess": "", "trustedWorkspaces": ["C:\\fake\\repo"]}'
Invoke-Drift "agy-allow-null-to-empty" "noaction" "" 60000
Assert-True ($script:LastReport -match 'allowNonWorkspaceAccess null -> ""') "a null to empty-string change is REPORTED, not absorbed as equal"
Assert-True ($script:LastExit -eq 0) "a recorded value changing is a note, so the run stays clean"
Complete-Scenario $b

# --- scenario: agy-allow-nested ---------------------------------------------
# THE TOKEN CAN BE EXACT AND THE STORED VALUE STILL WRONG. ConvertTo-Json
# defaults to depth 2 and truncates SILENTLY past it - a nested value comes
# back as the literal text "System.Collections.Hashtable" - so two
# different nested settings produced the same token and a real change read
# as equal. That is the defect the typed token was written to close, one
# level further down, and it lived in both the token function and the
# snapshot write. Diff debate round 3.

$b = $script:failCount
Reset-State
Set-AgySettings '{"allowNonWorkspaceAccess": {"scope": {"paths": {"deep": "one"}}}, "trustedWorkspaces": ["C:\\fake\\repo"]}'
Invoke-Drift "agy-allow-nested" "noaction" "" 60000
$snapNested = Get-SavedSnapshot
$nestedText = ConvertTo-Json $snapNested.agyAllowNonWorkspaceAccess -Compress -Depth 100
Assert-True ($nestedText -match '"deep"\s*:\s*"one"') "a nested value round-trips into the snapshot instead of being truncated"
# THE MARKER MATTERS. A first draft of this asserted the stored text does
# not contain "System.Collections", which is what a truncated HASHTABLE
# renders as - and it PASSED against the defect, because settings.json is
# parsed to PSCustomObject and THAT truncates to the string "@{deep=one}"
# instead. A vacuous assertion, in the fixture written to catch vacuous
# behaviour. What the defect actually does is turn an OBJECT into a
# STRING, so that is what this measures.
Assert-True ($snapNested.agyAllowNonWorkspaceAccess.scope.paths -isnot [string]) "a nested value stays an OBJECT in the snapshot and is never flattened into a string"
Complete-Scenario $b

# --- scenario: agy-allow-nested-change --------------------------------------
# A LIVE DISCRIMINATING CASE, sitting PAST the collapse boundary, and the
# depth is measured rather than guessed.
#
# An earlier version of this used a shallower value and PASSED against the
# defect, which this session then wrote up as "truncation corrupts the
# stored value but does not blind change detection". That narrowing was
# WRONG, and round 4 said so. A truncated PSCustomObject renders via
# ToString, which keeps carrying the differing text for a while and then
# stops.
#
# THE BOUNDARY IS MEASURED, and was got wrong once by counting it rather
# than running it. Tokenising the two values the way the pre-fix watcher
# did: at 2 and 3 nesting levels the tokens still DIFFER, and at FOUR they
# are byte-identical - both `{"l1":{"l2":{"l3":"@{l4=}"}}}` - so two
# genuinely different settings compare EQUAL and no note is written at
# all. A first attempt here used three levels, passed against the defect,
# and proved nothing.
#
# So truncation does hide change. Four levels plus the leaf is the
# shallowest shape that discriminates, which is exactly what this uses.

$b = $script:failCount
Reset-State
Set-SnapshotWithAgyAllow "1.2.3" "7.7.7" "6.2.0" "1.1.12" @{ l1 = @{ l2 = @{ l3 = @{ l4 = @{ leaf = "ONE" } } } } }
Set-AgySettings '{"allowNonWorkspaceAccess": {"l1": {"l2": {"l3": {"l4": {"leaf": "TWO"}}}}}, "trustedWorkspaces": ["C:\\fake\\repo"]}'
Invoke-Drift "agy-allow-nested-change" "noaction" "" 60000
Assert-True ($script:LastReport -match 'allowNonWorkspaceAccess.*leaf') "a change PAST the truncation boundary is reported, not collapsed into equality"
Assert-True ($script:LastReport -match 'TWO') "the note carries the NEW value rather than a rendered placeholder"
Complete-Scenario $b

# --- scenario: agy-allow-nested-array ---------------------------------------
# The ARRAY shape, which the object scenarios above never reach. Round 4
# asked for it by name: an admitted value can be a list, and a list nests
# the same way an object does.

$b = $script:failCount
Reset-State
Set-AgySettings '{"allowNonWorkspaceAccess": {"rules": [{"paths": ["a", "b"]}, {"paths": ["c"]}]}, "trustedWorkspaces": ["C:\\fake\\repo"]}'
Invoke-Drift "agy-allow-nested-array" "noaction" "" 60000
$snapArr = Get-SavedSnapshot
$arrText = ConvertTo-Json $snapArr.agyAllowNonWorkspaceAccess -Compress -Depth 100
Assert-True ($arrText -match '"c"') "a nested ARRAY round-trips into the snapshot instead of being truncated"
# The round-trip above is the DISCRIMINATING one; it was watched red. The
# assertion below was NOT - truncation renders the list's elements but
# leaves a list, so `-is [System.Array]` stays true either way. Kept as a
# shape companion and labelled, rather than left looking like evidence.
Assert-True ($snapArr.agyAllowNonWorkspaceAccess.rules -is [System.Array]) "a nested array stays an ARRAY in the snapshot"
Complete-Scenario $b

# --- scenario: agy-settings-null --------------------------------------------
# A settings file that PARSES and yields nothing. Measured 2026-08-12:
# `null`, `false` and `[]` all parse without throwing and are all falsy in
# PowerShell, so the object guard skipped every contract below it in
# silence and the run exited CLEAN. An unmade measurement must never look
# like a passing one. Whole-branch review, second pass, minor 2.

$b = $script:failCount
Reset-State
Set-AgySettings 'null'
Invoke-Drift "agy-settings-null" "noaction" "" 60000
Assert-True ($script:LastReport -match 'parsed but yielded no object') "a settings file that parses to nothing is a finding, not a skipped check"
Assert-True ($script:LastExit -ne 0) "a settings file that measures no contract makes the run non-clean"
Complete-Scenario $b

# --- scenario: agy-trustedworkspaces-shape ----------------------------------
# The SHAPE, which item 11 names explicitly. The lane's preflight reads
# this key positionally, so a string where an array belongs is a silent
# behaviour change rather than an error.

$b = $script:failCount
Reset-State
Set-AgySettings '{"allowNonWorkspaceAccess": true, "trustedWorkspaces": "C:\\fake\\repo"}'
Invoke-Drift "agy-trustedworkspaces-shape" "noaction" "" 60000
Assert-True ($script:LastReport -match 'trustedWorkspaces is not an array') "a changed settings shape is a finding"
Assert-True ($script:LastExit -ne 0) "a changed settings shape makes the run non-clean"
Complete-Scenario $b

# --- scenario: agy-trustedworkspaces-absent ---------------------------------

$b = $script:failCount
Reset-State
Set-AgySettings '{"allowNonWorkspaceAccess": true}'
Invoke-Drift "agy-trustedworkspaces-absent" "noaction" "" 60000
Assert-True ($script:LastReport -match 'has no trustedWorkspaces key') "a missing trustedWorkspaces key is a finding"
Assert-True ($script:LastExit -ne 0) "a missing trustedWorkspaces key makes the run non-clean"
Complete-Scenario $b

# --- scenario: agy-brain-missing --------------------------------------------
# NARROWER than item 11 asks for, deliberately. The transcript itself only
# exists after a run, so a pre-dispatch check asserts the brain ROOT and
# says so; the transcript stays enforced in the implementer's own evidence
# step, where a missing one already blocks.

$b = $script:failCount
Reset-State
Remove-Item -Recurse -Force (Join-Path $FakeProfile ".gemini\antigravity-cli\brain")
Invoke-Drift "agy-brain-missing" "noaction" "" 60000
Assert-True ($script:LastReport -match 'agy brain root is missing') "a missing brain root is a finding: the lane's authorship evidence lives there"
Assert-True ($script:LastExit -ne 0) "a missing brain root makes the run non-clean"
Complete-Scenario $b

# --- scenario: agy-absent ---------------------------------------------------
# The lane is OPTIONAL, like the backup reviewer lane, so an absent agy is
# a NOTE that says the lane is unavailable - not a finding, and never
# silence. The contract checks must not fire against a lane that is not
# installed, or the report cries wolf on every machine without agy.

$b = $script:failCount
Reset-State
Remove-Item -Force (Join-Path $FakeLocalAppData "agy\bin\agy.cmd")
Invoke-Drift "agy-absent" "noaction" "" 60000
Assert-True ($script:LastReport -match 'agy absent - the Flash implementer lane is UNAVAILABLE') "an absent agy is reported as an unavailable lane"
Assert-True (-not ($script:LastReport -match '\[CRITICAL\] agy')) "an absent lane raises no CRITICAL - the contracts do not fire against a lane that is not installed"
Assert-True ($script:LastExit -eq 0) "an absent optional lane does not fail the run"
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
