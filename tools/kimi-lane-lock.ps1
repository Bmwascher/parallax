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
#   - The label is the ownership credential. A nonblank one is required on
#     acquire, and a release must present the same string or -Force.
#   - Ownership is therefore a STRING MATCH and nothing more. Two debates
#     that pass the same label are indistinguishable here, so either can
#     release the other's lane. The contract requires a label unique to the
#     round; this script cannot enforce that, and says so rather than
#     implying an identity check it does not perform.
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

# The staleness threshold is a CONSTANT, with no override of any kind.
# Two earlier shapes both turned out to be lock-stealing:
#   - a `-MaxAgeMinutes` parameter, so `-Acquire -MaxAgeMinutes 0` broke a
#     fresh lock without -Force: the ownership guard bypassed by the flag
#     next to it.
#   - an env override honoured "whenever the lock path is redirected", which
#     gated on the redirect being PRESENT and not on it differing from the
#     default. Pointing it at the default path stole the real per-user lane.
# A test that needs a stale lock writes one with a backdated stamp; it does
# not ask the script to lower its own guard.
$MaxAgeMinutes = 45

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
    # An unusable stamp of any kind reads as INFINITELY old, so a malformed
    # lock is breakable instead of permanent.
    if (-not $lock) { return [double]::MaxValue }
    $stamp = $lock.stamp
    # A stamp that parsed as an OBJECT, an ARRAY or a NUMBER reached TryParse
    # with no matching overload and THREW, terminating this function before
    # it could return the intended infinite age - so the caller saw no age at
    # all, `$null -ge 45` was false, and the lock read as "held 0 min"
    # FOREVER. The routine written to stop a malformed lock wedging the lane
    # was the thing that wedged it. Hence the type check.
    #
    # But "string or unusable" was wrong about the NORMAL case on the other
    # host. Windows PowerShell 5.1 hands back the stamp as a String;
    # PowerShell 7 auto-converts an ISO-8601 string to a DateTime inside
    # ConvertFrom-Json. So on pwsh EVERY well-formed lock read as unusable,
    # every lock was instantly breakable, and the lane had no exclusion at
    # all - while the Windows suite stayed green, because it picks
    # powershell.exe when both hosts are installed. CI caught it; the
    # 0.16.0 release did not. A date the parser already produced is the
    # answer, not a failure: take it, and keep the unusable path for what is
    # genuinely not a time.
    if ($stamp -is [System.DateTimeOffset]) {
        $age = ([System.DateTimeOffset]::Now - $stamp).TotalMinutes
        if ($age -lt 0) { return [double]::MaxValue }
        return $age
    }
    if ($stamp -is [datetime]) {
        # Utc, Local and Unspecified all convert to the right instant: the
        # cast reads Kind, and Unspecified means local, which is what an
        # offsetless stamp means here too.
        $age = ([System.DateTimeOffset]::Now - [System.DateTimeOffset]$stamp).TotalMinutes
        if ($age -lt 0) { return [double]::MaxValue }
        return $age
    }
    if ($stamp -isnot [string]) { return [double]::MaxValue }
    # DateTimeOffset, not DateTime. `[datetime]::TryParse` with
    # RoundtripKind converts an OFFSET-bearing stamp (`+00:00`) to local time
    # but leaves a `Z` stamp as Kind=Utc - and subtracting two DateTime
    # values ignores Kind and compares raw ticks. On a UTC-05:00 machine a
    # CURRENT `Z` stamp therefore read as 300 minutes in the future, became
    # infinitely old, and was broken on sight; a genuinely five-hour-old `Z`
    # stamp read as brand new and held the lane past any threshold. Both
    # reproduced by running them. DateTimeOffset carries the offset into the
    # subtraction, so every representation of the same instant compares
    # equal; a stamp with no offset is assumed local, which is what this
    # script writes.
    $parsed = [System.DateTimeOffset]::MinValue
    $styles = [System.Globalization.DateTimeStyles]::None
    if (-not [System.DateTimeOffset]::TryParse($stamp, [System.Globalization.CultureInfo]::InvariantCulture,
                                               $styles, [ref]$parsed)) {
        return [double]::MaxValue
    }
    $age = ([System.DateTimeOffset]::Now - $parsed).TotalMinutes
    # A stamp in the FUTURE produced a negative age, which never reached the
    # stale branch: the lane stayed BUSY until the clock caught up, and status
    # cheerfully printed "held -360 min" to a human. Clock skew or a tampered
    # file, either way not a lock to respect - so it reads as infinitely old
    # and is breakable, like any other unusable stamp.
    if ($age -lt 0) { return [double]::MaxValue }
    return $age
}

function Get-LockOwner($lock) {
    # The owner credential, or $null when the file carries nothing usable as
    # one. ConvertFrom-Json will happily hand back `label = 0`, `label =
    # $null`, or no label at all, and every one of those is FALSY - which used
    # to short-circuit the release guard and let a bare `-Release` free a
    # recent lock. A number is not a credential a later release can present,
    # so anything that is not a nonblank string reads as "no owner".
    if (-not $lock) { return $null }
    $label = $lock.label
    if ($label -isnot [string]) { return $null }
    if (-not $label.Trim()) { return $null }
    return $label.Trim()
}

function Format-Lock($lock, $ageMin) {
    $owner = Get-LockOwner $lock
    $who = if ($owner) { $owner } else { "no usable owner" }
    # An unusable stamp is reported as such. Printing the sentinel verbatim
    # put "held 1.79769313486232E+308 min" in front of a human, which is the
    # same class as the "held -360 min" already fixed here: a number that
    # cannot be true, presented as though it were a measurement.
    if ($ageMin -ge [double]::MaxValue) { return "$who, age unusable" }
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
    # - the exact case this lock exists to prevent. Only -Force, or the
    # matching label, frees a held lane.
    $owner = Get-LockOwner $lock
    if (-not $Force) {
        if (-not $owner) {
            # No credential exists to present, so there is no correct label to
            # pass and the guard cannot be satisfied. The first fix let these
            # through by testing the raw field for truthiness, which made
            # `label = 0` and `label = null` bare-releasable.
            Write-Output "kimi lane lock: held by a lock with no usable owner label - not released; only -Force can clear it"
            exit 1
        }
        # Case-SENSITIVE, and both sides trimmed. Ownership is a string match
        # and nothing more, so the comparison is exactly that: two labels
        # differing only in case are two different callers.
        if ($owner -cne $Label.Trim()) {
            $who = if ($Label.Trim()) { "a different caller" } else { "another caller and this release names no label" }
            Write-Output "kimi lane lock: held by $who ($owner) - not released; pass the acquiring -Label, or -Force to override"
            exit 1
        }
    }
    Remove-Item $lockPath -Force
    Write-Output "kimi lane lock: released"
    exit 0
}

if ($Acquire) {
    # The label IS the ownership credential, so a lock without a usable one
    # has no holder to protect. Requiring a NONBLANK label here means this
    # script never writes such a lock. It can still READ one - a legacy file,
    # or one written by hand - which is why release checks the field too.
    # Whitespace was accepted as an owner until round 2 of the 0.16.0 debate.
    if (-not $Label -or -not $Label.Trim()) {
        Write-Output "kimi lane lock: a nonblank -Label is required on acquire - it is the ownership credential a later release is checked against"
        exit 2
    }
    $Label = $Label.Trim()
    # The lock file is written as ASCII, which silently rewrites any other
    # character as `?`. Doing that to the OWNERSHIP CREDENTIAL means the
    # holder's own release no longer matches its own label, and the lane sits
    # stranded until it goes stale. Refusing a label this file cannot store
    # faithfully is better than storing a different one, and better than
    # widening the encoding: the contract's label format is ASCII already.
    if ($Label -match '[^\x20-\x7E]') {
        Write-Output "kimi lane lock: -Label must be printable ASCII - the lock file stores it as ASCII, so any other character becomes '?' and the holder could not release its own lane"
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
            if ($stolen) {
                # Same rule as Format-Lock: an unusable stamp is described,
                # never printed as a measurement. This path built its own
                # string and so kept saying "broke a stale lock,
                # 1.79769313486232E+308 min old" after status had stopped.
                $howOld = if ($age -ge [double]::MaxValue) { "age unusable" } else { "$([Math]::Round($age, 1)) min old" }
                $note += " (broke a stale lock, $howOld)"
            }
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
