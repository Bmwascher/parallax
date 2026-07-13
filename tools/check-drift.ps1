# check-drift.ps1 - dependency drift watch for the crosscheck plugin.
#
# crosscheck's contract points at three moving targets it does not control:
#   1. superpowers  - the review-companion hook fingerprints its code-reviewer
#                     template ("Senior Code Reviewer" / "Git Range to Review")
#                     and extracts **Base:**/**Head:** lines from it.
#   2. Claude Code  - hook events, matcher tool names (Task -> Agent in
#                     v2.1.63 silently killed the hook once already), plugin
#                     cache layout, skill loading, -p/--allowedTools surface.
#   3. codex CLI    - the exec transport flags the skill's commands depend on
#                     (--sandbox, --output-last-message, -m/-c, exec resume).
#
# Every run: hash the INSTALLED superpowers template against the pinned
# fixture (normalized line endings) and probe the codex exec flag surface.
# On a Claude Code version change: fetch the changelog slice between the two
# versions and grep it for keywords that can affect us. Findings -> Windows
# toast + report file; a clean run is silent (report archived only).
#
# Scheduled task (weekly, Tue 13:17 local - 10 min after KE's api-drift
# task so toasts do not collide):    .\check-drift.ps1 -Register
# Written for Windows PowerShell 5.1 (what schtasks runs): no &&, no
# ternary, ASCII ONLY - 5.1 reads BOM-less files as ANSI and a UTF-8 em
# dash decodes into a smart quote that silently terminates strings.
#
#   -Register     create/replace the weekly scheduled task and exit
#   -TestNotify   fire a sample toast and exit (wiring check)
#
# Exit codes: 0 clean, 1 findings, 2 script failure.

param(
    [switch]$Register,
    [switch]$TestNotify,
    [switch]$NoAutoTriage
)

$RepoRoot = Split-Path $PSScriptRoot
$SnapshotFile = Join-Path $PSScriptRoot "drift-snapshot.json"
$ReportDir = Join-Path $PSScriptRoot "drift-reports"
$FixtureFile = Join-Path $RepoRoot "evals\multi-model-verify\fixtures\superpowers-code-reviewer-6.1.1.md"
$ChangelogUrl = "https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md"
# Keywords in a Claude Code changelog entry that can affect crosscheck's
# hook, skill loading, or the behavioral runner's headless invocation.
# Deliberately NO bare 'agent' - background-agent UI churn dominates every
# release; 'renam' + 'tool' still catch tool renames like Task -> Agent
# (v2.1.63, the rename that silently killed the hook once).
$ChangelogKeywords = 'hook|plugin|matcher|\bskills?\b|allowed-?tools|marketplace|headless|--print|renam|\btools?\b'

function Show-Toast($title, $body) {
    try {
        [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        $xml = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent(
            [Windows.UI.Notifications.ToastTemplateType]::ToastText02)
        $texts = $xml.GetElementsByTagName("text")
        $texts.Item(0).AppendChild($xml.CreateTextNode($title)) | Out-Null
        $texts.Item(1).AppendChild($xml.CreateTextNode($body)) | Out-Null
        $toast = New-Object Windows.UI.Notifications.ToastNotification($xml)
        $appId = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\WindowsPowerShell\v1.0\powershell.exe'
        [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($appId).Show($toast)
    } catch {
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.MessageBox]::Show($body, $title) | Out-Null
    }
}

function Get-NormalizedHash($text) {
    # CRLF/LF differences between the git checkout and the plugin cache must
    # not read as template drift; neither may the fixture's leading
    # attribution comment. Only OUR marker is stripped - a generic
    # leading-comment strip would hide an upstream template gaining a
    # meaningful comment of its own (Sol review 2026-07-12).
    $normalized = $text -replace '(?s)^\s*<!--\s*\[pinned fixture.*?-->\s*', ''
    $normalized = $normalized -replace "`r`n", "`n"
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($normalized)
    return ([System.BitConverter]::ToString($sha.ComputeHash($bytes)) -replace '-', '').ToLower()
}

if ($TestNotify) {
    Show-Toast "crosscheck drift watch" "Test notification - wiring OK."
    exit 0
}

if ($Register) {
    $self = Join-Path $PSScriptRoot "check-drift.ps1"
    $action = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File `"$self`""
    schtasks /Create /TN "crosscheck drift watch" /SC WEEKLY /D TUE /ST 13:17 /TR $action /F
    exit $LASTEXITCODE
}

$findings = @()
$notes = @()

# --- gather current versions -------------------------------------------------

$claudeRaw = ""
try { $claudeRaw = (& claude --version 2>&1 | Out-String).Trim() } catch {}
$claudeVersion = ""
if ($claudeRaw -match '(\d+\.\d+\.\d+)') { $claudeVersion = $Matches[1] }
if (-not $claudeVersion) {
    $findings += "[CRITICAL] claude --version failed or unparseable: $claudeRaw"
}

$codexRaw = ""
try { $codexRaw = (& codex --version 2>&1 | Out-String).Trim() } catch {}
$codexVersion = ""
if ($codexRaw -match '(\d+\.\d+\.\d+)') { $codexVersion = $Matches[1] }
if (-not $codexVersion) {
    $findings += "[CRITICAL] codex --version failed or unparseable: $codexRaw"
}

$registryFile = Join-Path $env:USERPROFILE ".claude\plugins\installed_plugins.json"
$spVersion = ""
$spInstall = ""
if (Test-Path $registryFile) {
    $registry = Get-Content $registryFile -Raw | ConvertFrom-Json
    foreach ($prop in $registry.plugins.PSObject.Properties) {
        if ($prop.Name -like "superpowers@*") {
            $entry = $prop.Value | Select-Object -First 1
            $spVersion = $entry.version
            $spInstall = $entry.installPath
        }
    }
}
if (-not $spInstall) {
    $findings += "[CRITICAL] superpowers not found in $registryFile - the review-companion hook has nothing to companion"
}

# --- check 1 (every run): superpowers template fingerprint canary -------------

if ($spInstall) {
    $template = Join-Path $spInstall "skills\requesting-code-review\code-reviewer.md"
    if (-not (Test-Path $template)) {
        $findings += "[CRITICAL] superpowers $spVersion layout changed - $template is gone; re-fingerprint hooks/superpowers-review-companion.ps1"
    } else {
        $installedText = Get-Content $template -Raw
        foreach ($literal in @("Senior Code Reviewer", "Git Range to Review")) {
            if ($installedText.IndexOf($literal) -lt 0) {
                $findings += "[CRITICAL] fingerprint literal '$literal' is gone from the installed superpowers template ($template) - the diff-gate hook is INERT NOW; re-fingerprint hooks/superpowers-review-companion.ps1"
            }
        }
        if (Test-Path $FixtureFile) {
            $fixtureHash = Get-NormalizedHash (Get-Content $FixtureFile -Raw)
            $installedHash = Get-NormalizedHash $installedText
            if ($fixtureHash -ne $installedHash) {
                $findings += "[WARN] installed superpowers code-reviewer.md ($spVersion) no longer matches the pinned fixture - verify the Base:/Head: extraction regexes in hooks/superpowers-review-companion.ps1 still match, then re-pin the fixture (copy the installed template over evals\multi-model-verify\fixtures\ and rename for the new version)"
            } else {
                $notes += "superpowers template matches pinned fixture (sha256 $($fixtureHash.Substring(0,12))...)"
            }
        } else {
            $findings += "[CRITICAL] pinned fixture missing: $FixtureFile"
        }
    }
}

# --- check 2 (every run): codex exec transport surface ------------------------

if ($codexVersion) {
    $execHelp = (& codex exec --help 2>&1 | Out-String)
    foreach ($flag in @("--sandbox", "--output-last-message", "--model", "--config")) {
        if ($execHelp.IndexOf($flag) -lt 0) {
            $findings += "[CRITICAL] codex exec --help ($codexVersion) no longer lists $flag - the skill's transport commands are broken; update SKILL.md + model-prompting-notes.md"
        }
    }
    & codex exec resume --help > $null 2>&1
    if ($LASTEXITCODE -ne 0) {
        $findings += "[CRITICAL] 'codex exec resume --help' failed ($codexVersion) - session resume transport is broken; update SKILL.md round-2+ command"
    }
}

# --- check 3 (on change): Claude Code changelog slice --------------------------

$snapshot = $null
if (Test-Path $SnapshotFile) {
    $snapshot = Get-Content $SnapshotFile -Raw | ConvertFrom-Json
}

# A transient probe failure must never clobber the last known-good value -
# an empty snapshot field would also disable next week's change detection,
# silently skipping the version interval (Sol review 2026-07-12). The
# failure itself is already a CRITICAL finding above, so carrying the old
# value forward here is not a quiet path.
$claudeVersionToSave = $claudeVersion
$codexVersionToSave = $codexVersion
$spVersionToSave = $spVersion
if ($snapshot) {
    if (-not $claudeVersionToSave -and $snapshot.claude) { $claudeVersionToSave = $snapshot.claude }
    if (-not $codexVersionToSave -and $snapshot.codex) { $codexVersionToSave = $snapshot.codex }
    if (-not $spVersionToSave -and $snapshot.superpowers) { $spVersionToSave = $snapshot.superpowers }
}

if ($snapshot -and $claudeVersion -and $snapshot.claude -and ($snapshot.claude -ne $claudeVersion)) {
    $changelog = ""
    try {
        $changelog = (Invoke-WebRequest -Uri $ChangelogUrl -UseBasicParsing -TimeoutSec 30).Content
    } catch {
        $findings += "[WARN] Claude Code changed $($snapshot.claude) -> $claudeVersion but the changelog fetch failed (offline?) - retrying next run"
        $claudeVersionToSave = $snapshot.claude  # do not advance; retry next run
    }
    if ($changelog) {
        $lines = $changelog -split "`n"
        $startIdx = -1
        $endIdx = $lines.Count
        for ($i = 0; $i -lt $lines.Count; $i++) {
            if ($startIdx -lt 0 -and $lines[$i] -match ("^##\s+" + [regex]::Escape($claudeVersion) + "\b")) { $startIdx = $i }
            elseif ($startIdx -ge 0 -and $lines[$i] -match ("^##\s+" + [regex]::Escape([string]$snapshot.claude) + "\b")) { $endIdx = $i; break }
        }
        if ($startIdx -lt 0) {
            $findings += "[WARN] Claude Code changed $($snapshot.claude) -> $claudeVersion but the changelog has no $claudeVersion entry yet - retrying next run"
            $claudeVersionToSave = $snapshot.claude  # do not advance; retry next run
        } else {
            # If the old version's heading is missing (skipped release), cap
            # the slice so we never grep years of history as one "change".
            if ($endIdx -gt ($startIdx + 400)) { $endIdx = $startIdx + 400 }
            $slice = $lines[$startIdx..([Math]::Min($endIdx, $lines.Count - 1))]
            $hits = $slice | Where-Object { $_ -match $ChangelogKeywords }
            if ($hits) {
                $findings += "[WARN] Claude Code $($snapshot.claude) -> $claudeVersion changelog mentions crosscheck-relevant surfaces:"
                foreach ($hit in $hits) { $findings += "    $($hit.Trim())" }
                $findings += "    review against: hook matcher (Task|Agent), plugin cache layout, Skill loading, claude -p --allowedTools"
            } else {
                $notes += "Claude Code $($snapshot.claude) -> $claudeVersion - no crosscheck-relevant keywords in the changelog slice"
            }
        }
    }
}

if ($snapshot -and $codexVersion -and $snapshot.codex -and ($snapshot.codex -ne $codexVersion)) {
    $notes += "codex CLI $($snapshot.codex) -> $codexVersion (flag surface re-probed above)"
}
if ($snapshot -and $spVersion -and $snapshot.superpowers -and ($snapshot.superpowers -ne $spVersion)) {
    $notes += "superpowers $($snapshot.superpowers) -> $spVersion (template canary re-hashed above)"
}

# --- report, toast, snapshot ---------------------------------------------------

New-Item -ItemType Directory -Force -Path $ReportDir | Out-Null
$Stamp = Get-Date -Format "yyyy-MM-dd_HHmmss"
$ReportFile = Join-Path $ReportDir "$Stamp.txt"

$report = @()
$report += "crosscheck drift watch - $Stamp"
$report += "claude: $claudeVersion | codex: $codexVersion | superpowers: $spVersion"
$report += ""
if ($findings.Count -gt 0) {
    $report += "FINDINGS ($($findings.Count)):"
    $report += $findings
} else {
    $report += "No findings."
}
if ($notes.Count -gt 0) {
    $report += ""
    $report += "Notes:"
    foreach ($n in $notes) { $report += "  $n" }
}
$report | Set-Content -Path $ReportFile
$report | Write-Output

$newSnapshot = @{
    claude      = $claudeVersionToSave
    codex       = $codexVersionToSave
    superpowers = $spVersionToSave
    updated     = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
}
$newSnapshot | ConvertTo-Json | Set-Content -Path $SnapshotFile

if ($findings.Count -eq 0) { exit 0 }

$critical = @($findings | Where-Object { $_ -like "*CRITICAL*" }).Count
$manualToast = $true

# --- headless auto-triage (findings-weeks only) --------------------------------
# The weekly loop must not depend on a human running /crosscheck:drift-triage:
# pipe the report plus the triage guide into a headless Claude Code run that
# classifies each finding and repairs real drift on a drift/<stamp> branch.
# It never merges. WARN-only noise dismissed by triage is silent (verdict
# archived in the report); a CRITICAL finding is never silently dismissed;
# any auto-triage failure falls back to the manual toast. Disable with
# -NoAutoTriage. No hard timeout here - the scheduler's own stop-after
# limit is the backstop if a headless run hangs.
$claudeCmd = Get-Command claude -ErrorAction SilentlyContinue
if (-not $NoAutoTriage -and $claudeCmd) {
    $guide = Get-Content (Join-Path $RepoRoot "commands\drift-triage.md") -Raw
    $branch = "drift/$Stamp"
    $prompt = @"
Headless drift auto-triage for the crosscheck plugin. No user is available -
never wait for input. You are in the crosscheck checkout: $RepoRoot.

Today's drift report:
--- REPORT ---
$((Get-Content $ReportFile -Raw))
--- END REPORT ---

Follow the triage guide below, EXCEPT: skip its report-locating step (the
report is above) and skip its Finish section (no merging, no pushing, no
plugin update in headless mode). Hard constraints:
- NEVER commit to main and NEVER merge; all edits go on a new branch $branch.
- Run 'python -m pytest evals -q' before committing; do not commit red.
- If a fix also needs interactive state (plugin cache re-sync, session
  restart, codex login), still commit the code fix and list the follow-up
  steps in your reply.
- If the report is noise (no crosscheck surface actually affected), change
  nothing and say why, per finding.
End your reply with EXACTLY one line:
VERDICT: NO-ACTION
or
VERDICT: FIXED-ON-BRANCH $branch
or
VERDICT: BLOCKED <one-line reason>

--- TRIAGE GUIDE ---
$guide
"@
    $triageFile = Join-Path $ReportDir "$Stamp-autotriage.txt"
    $promptFile = Join-Path $ReportDir "$Stamp-autotriage-prompt.txt"
    $prompt | Set-Content -Path $promptFile
    Push-Location $RepoRoot
    Get-Content -Raw $promptFile | & claude -p --allowedTools "Read,Glob,Grep,Edit,Write,Bash(git:*),Bash(python:*),Bash(codex:*),PowerShell(git:*),PowerShell(python:*),PowerShell(codex:*)" > $triageFile 2>&1
    $triageExit = $LASTEXITCODE
    Pop-Location
    $verdictLine = ""
    if (Test-Path $triageFile) {
        $verdictMatch = Select-String -Path $triageFile -Pattern '^VERDICT: (.+)$' | Select-Object -Last 1
        if ($verdictMatch) { $verdictLine = $verdictMatch.Matches[0].Groups[1].Value.Trim() }
    }
    if ($verdictLine) {
        Add-Content -Path $ReportFile -Value "`r`nAuto-triage verdict: $verdictLine (transcript: $Stamp-autotriage.txt)"
    } else {
        Add-Content -Path $ReportFile -Value "`r`nAuto-triage FAILED (exit $triageExit, no verdict line - transcript: $Stamp-autotriage.txt)"
    }
    if ($triageExit -eq 0 -and $verdictLine -like "FIXED-ON-BRANCH*") {
        Show-Toast "crosscheck drift: fix ready" "Auto-triage committed a fix on $branch - review and merge. Report: tools\drift-reports\$Stamp.txt"
        $manualToast = $false
    } elseif ($triageExit -eq 0 -and $verdictLine -eq "NO-ACTION") {
        if ($critical -gt 0) {
            Show-Toast "crosscheck drift: VERIFY dismissal" "$critical CRITICAL finding(s) auto-triaged as no-action - verify by hand. Report: tools\drift-reports\$Stamp.txt"
        }
        $manualToast = $false
    }
    # BLOCKED, no verdict line, or nonzero exit: fall through to manual toast.
}

if ($manualToast) {
    if ($critical -gt 0) {
        Show-Toast "crosscheck drift: $critical CRITICAL" "Contract-breaking drift found. Triage with /crosscheck:drift-triage (report: tools\drift-reports\$Stamp.txt)"
    } else {
        Show-Toast "crosscheck drift watch" "$($findings.Count) finding(s). Triage with /crosscheck:drift-triage (report: tools\drift-reports\$Stamp.txt)"
    }
}
exit 1
