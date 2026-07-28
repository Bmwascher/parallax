# kimi-lane-lock.ps1 - serialize backup-lane dispatches on one machine.
#
# WHY: ~/.kimi/logs/kimi.log is a single user-global append stream, and the
# lane's route-attribution evidence is read out of it. Two parallax debates
# running at once interleave their startup lines, which cost two of six
# dispatched rounds on 2026-07-27 (backlog item 6). Ordering-based
# attribution in references/backup-lane.md handles FOREIGN kimi sessions;
# this lock removes the case parallax causes itself.
#
# The lock is advisory and time-bounded on purpose. It holds no process
# handle, because the holder is a driver agent whose shell invocations are
# each short-lived - a PID recorded here would be dead by the time the next
# caller looked, and every lock would read as stale immediately. So
# staleness is decided by AGE alone: a lock 45 minutes old is breakable.
#
# What that buys and what it costs, stated exactly rather than as a slogan:
#   - A crashed driver blocks the lane for at most 45 minutes.
#   - A LIVE round still running past 45 minutes also becomes breakable,
#     because nothing here can tell the two apart. Rounds take minutes, so
#     the margin is wide, but this is a real residual and not a corner case
#     that cannot happen.
#   - Acquire is last-writer-wins (see the write site), so this narrows a
#     minutes-wide race to a milliseconds-wide one rather than closing it.
#   - The label is the ownership credential. It is required on acquire, and
#     a release must present it or -Force.
#
# Windows PowerShell 5.1 compatible, ASCII ONLY.
#
# Exit codes: 0 acquired / released / free, 1 busy (timed out waiting or
# held by someone else on release), 2 script error.
[CmdletBinding(DefaultParameterSetName = "Status")]
param(
    [Parameter(ParameterSetName = "Acquire", Mandatory = $true)][switch]$Acquire,
    [Parameter(ParameterSetName = "Release", Mandatory = $true)][switch]$Release,
    [Parameter(ParameterSetName = "Status", Mandatory = $false)][switch]$Status,
    # Who is asking, recorded in the lock and echoed to a waiting caller so
    # a human can tell which debate is holding the lane.
    [string]$Label = "",
    # How long to wait for a busy lane before giving up. A single review
    # round is minutes; the default tolerates one queued round ahead.
    [int]$WaitSeconds = 900,
    # Release a lock this caller does not own. Only for a human clearing a
    # known-dead holder.
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Test seam and escape hatch. Defaults beside the other per-user parallax
# state rather than in the repo, because the resource it guards is
# per-user, not per-checkout.
$lockPath = $env:PARALLAX_KIMI_LOCK
if (-not $lockPath) {
    $lockPath = Join-Path $env:LOCALAPPDATA "parallax\kimi-lane.lock"
}
$lockDir = Split-Path $lockPath -Parent

# The staleness threshold is NOT caller-controlled. It used to be a
# parameter, which made `-Acquire -MaxAgeMinutes 0` a silent way to steal a
# fresh lock without -Force - the ownership guard bypassed by the flag next
# to it. The override now exists only alongside a redirected lock path, so it
# cannot be aimed at the real per-user lane.
$MaxAgeMinutes = 45
if ($env:PARALLAX_KIMI_LOCK -and $env:PARALLAX_KIMI_LOCK_MAX_AGE_MINUTES) {
    $parsedAge = 0
    if ([int]::TryParse($env:PARALLAX_KIMI_LOCK_MAX_AGE_MINUTES, [ref]$parsedAge) -and $parsedAge -ge 0) {
        $MaxAgeMinutes = $parsedAge
    }
}

function Read-Lock($path) {
    # Returns the parsed lock, or $null when there is nothing usable there.
    # $script:LockWasMalformed records the difference between "no lock" and
    # "a lock I could not read", so acquiring over a corrupt one can say so.
    # Breaking a stale lock announces itself; breaking a malformed one used
    # to be silent, which is the same act reported two different ways.
    $script:LockWasMalformed = $false
    if (-not (Test-Path $path)) { return $null }
    try {
        $raw = Get-Content $path -Raw
        if (-not $raw -or -not $raw.Trim()) {
            $script:LockWasMalformed = $true
            return $null
        }
        return $raw | ConvertFrom-Json
    } catch {
        # An unparseable lock is treated as absent rather than as a wedge:
        # a half-written file must never block the lane forever.
        $script:LockWasMalformed = $true
        return $null
    }
}

function Get-LockAgeMinutes($lock) {
    # An unparseable or missing stamp reads as INFINITELY old, so a
    # malformed lock is breakable instead of permanent.
    if (-not $lock -or -not $lock.stamp) { return [double]::MaxValue }
    $parsed = [datetime]::MinValue
    $styles = [System.Globalization.DateTimeStyles]::RoundtripKind
    if (-not [datetime]::TryParse($lock.stamp, [System.Globalization.CultureInfo]::InvariantCulture,
                                  $styles, [ref]$parsed)) {
        return [double]::MaxValue
    }
    $age = ((Get-Date) - $parsed).TotalMinutes
    # A stamp in the FUTURE produced a negative age, which never reached the
    # stale branch: the lane stayed BUSY until the clock caught up, and status
    # cheerfully printed "held -360 min" to a human. Clock skew or a tampered
    # file, either way not a lock to respect - so it reads as infinitely old
    # and is breakable, like any other unusable stamp.
    if ($age -lt 0) { return [double]::MaxValue }
    return $age
}

function Format-Lock($lock, $ageMin) {
    $who = if ($lock.label) { $lock.label } else { "unlabelled" }
    return "$who, held $([Math]::Round($ageMin, 1)) min"
}

if ($Release) {
    $lock = Read-Lock $lockPath
    if (-not $lock) {
        Write-Output "kimi lane lock: already free"
        exit 0
    }
    # A release that names NO label used to skip this check entirely, which
    # made a bare `-Release` an undeclared -Force: it silently freed a lane
    # another debate was holding, and two rounds could then dispatch at once
    # - the exact case this lock exists to prevent. So an unlabelled release
    # of a LABELLED lock is refused too. Releasing an unlabelled lock, or
    # releasing with the matching label, still works.
    if (-not $Force -and $lock.label -and ($lock.label -ne $Label)) {
        $who = if ($Label) { "a different caller" } else { "another caller and this release names no label" }
        Write-Output "kimi lane lock: held by $who ($($lock.label)) - not released; pass the acquiring -Label, or -Force to override"
        exit 1
    }
    Remove-Item $lockPath -Force
    Write-Output "kimi lane lock: released"
    exit 0
}

if ($Acquire) {
    # The label IS the ownership credential, so an unlabelled lock has no
    # holder to protect and any bare release frees it. Requiring it on
    # acquire means an unlabelled lock cannot exist in the first place.
    if (-not $Label) {
        Write-Output "kimi lane lock: -Label is required on acquire - it is the ownership credential a later release is checked against"
        exit 2
    }
    if (-not (Test-Path $lockDir)) {
        New-Item -ItemType Directory -Force -Path $lockDir | Out-Null
    }
    $deadline = (Get-Date).AddSeconds($WaitSeconds)
    $waited = $false
    while ($true) {
        $lock = Read-Lock $lockPath
        $malformed = $script:LockWasMalformed
        $age = Get-LockAgeMinutes $lock
        $free = ($null -eq $lock)
        $stolen = $false
        if (-not $free -and $age -ge $MaxAgeMinutes) {
            $free = $true
            $stolen = $true
        }
        if ($free) {
            $payload = @{
                label = $Label
                stamp = (Get-Date).ToString("o")
                host  = $env:COMPUTERNAME
            }
            # Last-writer-wins. Two callers that pass the free check in the
            # same instant can both write, so this is advisory, not mutual
            # exclusion: it collapses a minutes-wide race into a
            # milliseconds-wide one. Stated rather than papered over.
            $payload | ConvertTo-Json | Set-Content -Path $lockPath -Encoding ASCII
            $note = "kimi lane lock: acquired"
            if ($stolen) { $note += " (broke a stale lock, $([Math]::Round($age, 1)) min old)" }
            elseif ($malformed) { $note += " (broke an unreadable lock)" }
            if ($waited) { $note += " after waiting" }
            Write-Output $note
            exit 0
        }
        if ((Get-Date) -ge $deadline) {
            Write-Output "kimi lane lock: BUSY - $(Format-Lock $lock $age); waited $WaitSeconds s. Do not dispatch: a concurrent round breaks route attribution."
            exit 1
        }
        if (-not $waited) {
            Write-Output "kimi lane lock: waiting - $(Format-Lock $lock $age)"
            $waited = $true
        }
        Start-Sleep -Seconds 5
    }
}

# Status (default): report without changing anything.
$lock = Read-Lock $lockPath
if (-not $lock) {
    Write-Output "kimi lane lock: free ($lockPath)"
    exit 0
}
$age = Get-LockAgeMinutes $lock
$state = if ($age -ge $MaxAgeMinutes) { "STALE" } else { "held" }
Write-Output "kimi lane lock: $state - $(Format-Lock $lock $age) ($lockPath)"
exit 0
