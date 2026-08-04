# kimi-lane-lock.ps1 - serialize access to the shared kimi-code lane home
# (Task 3 of the 2026-08-01 lane-credential-and-lock plan).
#
# WHY THIS REPLACES 775472c^:tools/kimi-lane-lock.ps1: that file is gone
# and NOT restored here. Its own header named three defects this script
# exists to not have - a 45-minute AGE-based staleness clock (a live round
# past that mark became silently breakable), last-writer-wins acquire (no
# exclusive handle serialized the decision), and a date-string timestamp
# (measurement 20: a date string round-trips as [String] on Windows
# PowerShell 5.1 and as [DateTime] on PowerShell 7, so the SAME file reads
# two different .NET types on the two hosts this tool is gated on).
#
# Staleness here is decided by PROCESS LIVENESS ONLY, never by a clock:
# a held record's owner is checked by asking whether a process with the
# recorded pid still exists AND its start time still matches the recorded
# one (the PID-reuse guard). Liveness has three outcomes - LIVE, DEAD, and
# UNMEASURABLE - and UNMEASURABLE (the pid lookup succeeded but the start
# time could not be read, which happens on another user's process) is
# treated as ALIVE by every mutating mode: an unmade measurement is never
# a clean one, so a lock this tool cannot positively prove dead is never
# reclaimed.
#
# THE FILE-OPEN PROTOCOL. OpenOrCreate is FORBIDDEN: it cannot distinguish
# a file THIS call created from a pre-existing zero-length file, and a
# crash after SetLength(0) leaves exactly that - which OpenOrCreate would
# read as free and steal. Instead:
#   1. Try CreateNew/ReadWrite/None. Success means this call created it.
#      Only -Acquire is ever allowed to reach this step.
#   2. On failure because it exists, open Open/ReadWrite/None.
#   3. On failure because another process holds the handle: CONTENTION.
#      Sleep min(-PollSeconds, budget remaining), retry, exit 3 when the
#      budget expires. The remaining budget is measured with a monotonic
#      Stopwatch, never by comparing clock readings.
#   4. Under the handle: read, decide, SetLength(0), Position = 0, write,
#      Flush($true), close. The file is NEVER deleted by any path.
#
# Windows PowerShell 5.1 compatible, ASCII ONLY.
#
# Every value-shaped parameter is declared [string] and parsed inside the
# script, so no VALUE can ever fail PowerShell's own parameter binder -
# only the invocation SHAPE (an unknown name, a missing mandatory value,
# an ambiguous parameter set) can, and that failure exits nonzero before
# any script code runs and mutates nothing. That is why every mode switch
# below is unconditionally mandatory within its own parameter set rather
# than hand-rolling $args parsing to own that path: a documented, testable
# refusal beats a large hand-written parser that can itself be wrong.
#
# Exit codes (scoped to SUCCESSFULLY BOUND invocations only):
#   0  the mode succeeded
#   2  a parameter value was refused, or owner resolution failed
#   3  contention: the handle, or a holder that is LIVE or UNMEASURABLE,
#      and the wait budget expired
#   4  MUTATING FILE MODES ONLY: the record is MALFORMED or names a
#      foreign host, and the applicable confirmed override is not the
#      mode being run. -Status never emits it.
#   5  a release or override was refused: nothing applicable to release,
#      or the supplied identity/hash did not match
#   6  the file is UNREADABLE, a write or flush failed, or any
#      unclassified runtime failure
#   1  reserved for PowerShell's own parameter-binding refusal; never
#      emitted by script code
[CmdletBinding()]
param(
    [Parameter(ParameterSetName = "Acquire", Mandatory = $true)][switch]$Acquire,
    [Parameter(ParameterSetName = "Release", Mandatory = $true)][switch]$Release,
    [Parameter(ParameterSetName = "Status", Mandatory = $true)][switch]$Status,
    [Parameter(ParameterSetName = "ForceRelease", Mandatory = $true)][switch]$ForceRelease,
    [Parameter(ParameterSetName = "MalformedOverride", Mandatory = $true)][switch]$MalformedOverride,
    [Parameter(ParameterSetName = "ResolveOwner", Mandatory = $true)][switch]$ResolveOwner,

    [Parameter(ParameterSetName = "Acquire", Mandatory = $true)]
    [Parameter(ParameterSetName = "Release", Mandatory = $true)]
    [Parameter(ParameterSetName = "Status", Mandatory = $true)]
    [Parameter(ParameterSetName = "ForceRelease", Mandatory = $true)]
    [Parameter(ParameterSetName = "MalformedOverride", Mandatory = $true)]
    [string]$LaneHome,

    [Parameter(ParameterSetName = "Acquire", Mandatory = $true)]
    [Parameter(ParameterSetName = "Release", Mandatory = $true)]
    [string]$DebateId,

    [Parameter(ParameterSetName = "Acquire", Mandatory = $true)]
    [Parameter(ParameterSetName = "Release", Mandatory = $true)]
    [string]$OwnerPid,

    [Parameter(ParameterSetName = "Acquire", Mandatory = $true)]
    [Parameter(ParameterSetName = "Release", Mandatory = $true)]
    [string]$OwnerStartTicksUtc,

    [Parameter(ParameterSetName = "Acquire", Mandatory = $true)]
    [string]$DebateHome,

    # OPTIONAL, and on -Acquire only. Release and ForceRelease match on
    # the identity they were GIVEN; a display name is not part of that
    # identity and must never become something a caller has to reproduce
    # in order to let go of its own lock.
    [Parameter(ParameterSetName = "Acquire", Mandatory = $false)]
    [string]$OwnerName,

    # Mandatory on -Release (present the nonce this session was given),
    # optional on -Acquire (absent on a fresh acquisition, supplied only
    # to prove an idempotent re-acquire of one's own held lock).
    [Parameter(ParameterSetName = "Acquire", Mandatory = $false)]
    [Parameter(ParameterSetName = "Release", Mandatory = $true)]
    [string]$Nonce,

    [Parameter(ParameterSetName = "ForceRelease", Mandatory = $true)][string]$ConfirmHost,
    [Parameter(ParameterSetName = "ForceRelease", Mandatory = $true)][string]$ConfirmOwnerPid,
    [Parameter(ParameterSetName = "ForceRelease", Mandatory = $true)][string]$ConfirmOwnerStartTicksUtc,
    [Parameter(ParameterSetName = "ForceRelease", Mandatory = $true)][string]$ConfirmDebateId,
    [Parameter(ParameterSetName = "ForceRelease", Mandatory = $true)][string]$ConfirmNonce,

    [Parameter(ParameterSetName = "MalformedOverride", Mandatory = $true)][string]$ConfirmSha256,

    [Parameter(ParameterSetName = "Acquire", Mandatory = $false)]
    [Parameter(ParameterSetName = "Release", Mandatory = $false)]
    [Parameter(ParameterSetName = "Status", Mandatory = $false)]
    [Parameter(ParameterSetName = "ForceRelease", Mandatory = $false)]
    [Parameter(ParameterSetName = "MalformedOverride", Mandatory = $false)]
    [string]$WaitSeconds = "0",

    [Parameter(ParameterSetName = "Acquire", Mandatory = $false)]
    [Parameter(ParameterSetName = "Release", Mandatory = $false)]
    [Parameter(ParameterSetName = "Status", Mandatory = $false)]
    [Parameter(ParameterSetName = "ForceRelease", Mandatory = $false)]
    [Parameter(ParameterSetName = "MalformedOverride", Mandatory = $false)]
    [string]$PollSeconds = "2"
)

$ErrorActionPreference = "Stop"

# ---------------------------------------------------------------------
# Record schema constants.
# ---------------------------------------------------------------------
$FreeFields = @("version", "state")
# ownerName is in $HeldFields and NOT in $HeldRequired, and that gap is
# the migration. The held schema is an EXACT field set, so a REQUIRED
# ownerName would have turned every record written before this change
# MALFORMED the moment the plugin cache updated - a lane locked by an
# upgrade rather than by a debate, freeable only through the guarded
# override. Optional means both shapes stay well formed.
$HeldFields = @("version", "state", "host", "ownerPid", "ownerStartTicksUtc",
                "debateId", "nonce", "debateHome", "acquiredTicksUtc",
                "ownerName")
$HeldRequired = @("host", "ownerPid", "ownerStartTicksUtc", "debateId",
                  "nonce", "debateHome", "acquiredTicksUtc")
# -DebateId/-Nonce/-ConfirmDebateId/-ConfirmNonce/debateId/nonce: exactly
# 32 LOWERCASE hex. Every use of $TokenPattern below is via -cmatch, not
# -match: PowerShell's -match is case-INSENSITIVE by default, which
# would silently accept "A".."F" as if they were "a".."f" - reproduced
# live (an all-uppercase 32-hex value passed this check under -match).
# $Sha256Pattern deliberately allows both cases (-ConfirmSha256 is
# compared case-insensitively per its own rule) and stays on -match.
$TokenPattern = '\A[0-9a-f]{32}\z'
$DigitsPattern = '\A[0-9]+\z'
$Sha256Pattern = '\A[0-9a-fA-F]{64}\z'

# Currently-open exclusive handle, tracked at script scope so the
# catch-all below can best-effort release it before mapping an unexpected
# failure to exit 6. Every deliberate exit path also closes it explicitly
# first - exit called from inside a function bypasses an enclosing try's
# catch (measured live on this same branch, prior task), so cleanup here
# is performed by explicit calls, not by relying on `finally` to run
# across an `exit`.
$script:OpenStream = $null
function Close-CurrentStream {
    if ($script:OpenStream) {
        try { $script:OpenStream.Dispose() } catch { }
        $script:OpenStream = $null
    }
}

function Write-Stderr([string]$Line) {
    [Console]::Error.WriteLine($Line)
}

# ---------------------------------------------------------------------
# Contention signal seam, frozen: PARALLAX_LANE_LOCK_CONTENTION_SIGNAL.
# On the FIRST actual contention decision, and once only, write exactly
# one ASCII line - "handle" or "holder" - to that path BEFORE sleeping.
# A failure to write the signal exits 6 with no lock mutation: an oracle
# that cannot synchronize must not silently become a timing test again.
# With the seam unset (ordinary production use) this is a no-op.
# ---------------------------------------------------------------------
$script:ContentionSignalWritten = $false
function Write-ContentionSignalOnce([string]$Branch) {
    if ($script:ContentionSignalWritten) { return }
    $script:ContentionSignalWritten = $true
    $sigPath = $env:PARALLAX_LANE_LOCK_CONTENTION_SIGNAL
    if ([string]::IsNullOrEmpty($sigPath)) { return }
    try {
        [System.IO.File]::WriteAllText($sigPath, ($Branch + "`n"), [System.Text.Encoding]::ASCII)
    } catch {
        Close-CurrentStream
        Write-Stderr "contention signal write failed"
        exit 6
    }
}

# ---------------------------------------------------------------------
# Liveness. Three outcomes, not two:
#   LIVE          - a process with that pid exists and its start ticks
#                   (compared as STRINGS) match the recorded ones.
#   DEAD          - no process with that pid, or one whose start ticks
#                   differ (the PID-reuse guard).
#   UNMEASURABLE  - the pid lookup succeeded but the start-time read
#                   failed (Get-Process does this on another user's
#                   process). The catch wraps the start-time read only.
# Every MUTATING mode treats UNMEASURABLE as ALIVE and refuses to
# reclaim. -Status reports it as UNKNOWN, never as LIVE.
#
# Test seam PARALLAX_LANE_LOCK_STARTTIME_FAULT forces the start-time read
# to throw AFTER the pid lookup has already succeeded. It is safe by
# construction: its only possible effect is to classify a holder ALIVE
# and refuse a takeover, never to reclaim one. Precedent:
# tools/new-kimi-lane-home.ps1:416-423,
# evals/multi-model-verify/test_kimi_lane_home.py:102-106.
# ---------------------------------------------------------------------
function Get-Liveness([int]$OwnerPidValue, [string]$TicksValue) {
    $proc = $null
    try {
        $proc = Get-Process -Id $OwnerPidValue -ErrorAction Stop
    } catch {
        return "DEAD"
    }
    $actualTicks = $null
    try {
        if ($env:PARALLAX_LANE_LOCK_STARTTIME_FAULT) {
            throw "PARALLAX_LANE_LOCK_STARTTIME_FAULT injected: simulated start-time read failure"
        }
        $actualTicks = [string]$proc.StartTime.ToUniversalTime().Ticks
    } catch {
        return "UNMEASURABLE"
    }
    if ($actualTicks -eq $TicksValue) { return "LIVE" }
    return "DEAD"
}

# ---------------------------------------------------------------------
# -DebateHome normalization, one stated algorithm. The root guard is not
# decoration: an unconditional trailing-separator trim takes a drive root
# C:\ to C:, which is drive-RELATIVE and a different path entirely, so
# the trim only ever applies when the normalized string is not itself a
# path root.
# ---------------------------------------------------------------------
function Get-NormalizedDebateHome([string]$Path) {
    $full = [System.IO.Path]::GetFullPath($Path)
    $root = [System.IO.Path]::GetPathRoot($full)
    $isRoot = [System.String]::Equals($full, $root, [System.StringComparison]::OrdinalIgnoreCase)
    if (-not $isRoot -and $full.Length -gt 0) {
        $lastChar = $full.Substring($full.Length - 1, 1)
        if ($lastChar -eq '\' -or $lastChar -eq '/') {
            $full = $full.Substring(0, $full.Length - 1)
        }
    }
    return $full
}
function Test-DebateHomeEqual([string]$A, [string]$B) {
    $na = Get-NormalizedDebateHome $A
    $nb = Get-NormalizedDebateHome $B
    return [System.String]::Equals($na, $nb, [System.StringComparison]::OrdinalIgnoreCase)
}

function Test-IntField($Value) {
    return ($Value -is [int]) -or ($Value -is [long])
}

function Get-Sha256Hex([byte[]]$Bytes) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hash = $sha.ComputeHash([byte[]]$Bytes)
    } finally {
        $sha.Dispose()
    }
    $sb = New-Object System.Text.StringBuilder
    foreach ($b in $hash) { [void]$sb.Append($b.ToString("x2")) }
    return $sb.ToString()
}

# ---------------------------------------------------------------------
# Record classification. MALFORMED means any of: not JSON; not an
# object; version absent or not 1; state not one of the two literals; a
# record missing a field required for its state; a record carrying ANY
# property forbidden for its state (a free record allows only version
# and state - a held-only KNOWN property on a free record is just as
# forbidden as a wholly unknown one); a field failing its type or
# pattern rule; a zero-length file.
# ---------------------------------------------------------------------
function Get-Classification([byte[]]$Bytes) {
    if ($Bytes.Length -eq 0) { return @{ Malformed = $true } }
    $text = [System.Text.Encoding]::UTF8.GetString($Bytes)
    $obj = $null
    try {
        $obj = $text | ConvertFrom-Json -ErrorAction Stop
    } catch {
        return @{ Malformed = $true }
    }
    if (($null -eq $obj) -or -not ($obj -is [System.Management.Automation.PSCustomObject])) {
        return @{ Malformed = $true }
    }
    $props = @($obj.PSObject.Properties.Name)

    # Every literal comparison in this function is CASE-EXACT, because the
    # shipped contract says a record that does not exactly satisfy the
    # schema is held and reported rather than reclaimed. PowerShell's
    # -eq, -ne and -contains are case-INSENSITIVE, so `"state":"Free"` and
    # a field spelled `Owner` both used to classify as a well-formed free
    # record, and an acquire would then overwrite a record this tool never
    # actually recognized. That is the same defect the hex tokens already
    # carry -cmatch for.
    if ($props -cnotcontains "version") { return @{ Malformed = $true } }
    if (-not (Test-IntField $obj.version) -or ([int64]$obj.version) -ne 1) {
        return @{ Malformed = $true }
    }
    if ($props -cnotcontains "state") { return @{ Malformed = $true } }
    if (-not ($obj.state -is [string]) -or
        ($obj.state -cne "free" -and $obj.state -cne "held")) {
        return @{ Malformed = $true }
    }

    if ($obj.state -ceq "free") {
        foreach ($p in $props) {
            if ($FreeFields -cnotcontains $p) { return @{ Malformed = $true } }
        }
        return @{ Malformed = $false; State = "free" }
    }

    # state -eq "held"
    foreach ($p in $props) {
        if ($HeldFields -cnotcontains $p) { return @{ Malformed = $true } }
    }
    foreach ($req in $HeldRequired) {
        if ($props -cnotcontains $req) { return @{ Malformed = $true } }
    }
    if (-not ($obj.host -is [string]) -or $obj.host.Trim().Length -eq 0) {
        return @{ Malformed = $true }
    }
    if (-not (Test-IntField $obj.ownerPid) -or ([int64]$obj.ownerPid) -le 0) {
        return @{ Malformed = $true }
    }
    if (-not ($obj.ownerStartTicksUtc -is [string]) -or
        -not ($obj.ownerStartTicksUtc -match $DigitsPattern)) {
        return @{ Malformed = $true }
    }
    if (-not ($obj.debateId -is [string]) -or
        -not ($obj.debateId -cmatch $TokenPattern)) {
        return @{ Malformed = $true }
    }
    if (-not ($obj.nonce -is [string]) -or
        -not ($obj.nonce -cmatch $TokenPattern)) {
        return @{ Malformed = $true }
    }
    if (-not ($obj.debateHome -is [string]) -or $obj.debateHome.Trim().Length -eq 0) {
        return @{ Malformed = $true }
    }
    if (-not ($obj.acquiredTicksUtc -is [string]) -or
        -not ($obj.acquiredTicksUtc -match $DigitsPattern)) {
        return @{ Malformed = $true }
    }
    # Optional in PRESENCE, not in shape: a record that carries the field
    # at all must carry something a reader can act on.
    if ($props -ccontains "ownerName") {
        if (-not ($obj.ownerName -is [string]) -or $obj.ownerName.Trim().Length -eq 0) {
            return @{ Malformed = $true }
        }
    }
    return @{ Malformed = $false; State = "held"; Record = $obj }
}

function Read-AllBytes($Stream) {
    # The leading comma on every return below is NOT decorative: without
    # it PowerShell enumerates a [byte[]] onto the output pipeline
    # element-by-element rather than passing the array itself, which for
    # a zero-length or single-byte file collapses the caller's captured
    # value to $null or a bare scalar instead of an (empty) array -
    # reproduced live via a genuine zero-length lock file, where
    # ComputeHash then threw "Value cannot be null" on the caller's side.
    $Stream.Seek(0, [System.IO.SeekOrigin]::Begin) | Out-Null
    $len = [int]$Stream.Length
    if ($len -eq 0) { return , ([byte[]]@()) }
    $buf = New-Object byte[] $len
    $offset = 0
    while ($offset -lt $len) {
        $readCount = $Stream.Read($buf, $offset, $len - $offset)
        if ($readCount -le 0) { throw "unexpected end of stream reading lock file" }
        $offset += $readCount
    }
    return , $buf
}

function Write-RecordJson($Stream, [string]$Json) {
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($Json)
    $Stream.SetLength(0)
    $Stream.Position = 0
    $Stream.Write($bytes, 0, $bytes.Length)
    $Stream.Flush($true)
}

function New-Nonce {
    return [System.Guid]::NewGuid().ToString("N")
}

# ---------------------------------------------------------------------
# Handle-open helpers. Every retry loop below shares one Stopwatch and
# the one-shot contention signal, so whichever branch (handle or holder)
# is reached first is the one that reports.
# ---------------------------------------------------------------------
function Open-ForAcquire([string]$Path, $Stopwatch, [double]$WaitBudget, [double]$PollBudget) {
    while ($true) {
        try {
            $fs = New-Object System.IO.FileStream($Path, [System.IO.FileMode]::CreateNew,
                [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
            return @{ Stream = $fs; Existed = $false }
        } catch [System.IO.DirectoryNotFoundException] {
            # The lane-home directory itself is missing. This is not a
            # sharing conflict - re-throw so the outer catch-all maps it
            # to exit 6 rather than retrying it as contention forever.
            throw
        } catch [System.IO.IOException] {
            # Exists (CreateNew's only remaining IOException on a path
            # whose parent directory does exist). Fall through to Open.
        }
        try {
            $fs = New-Object System.IO.FileStream($Path, [System.IO.FileMode]::Open,
                [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
            return @{ Stream = $fs; Existed = $true }
        } catch [System.IO.DirectoryNotFoundException] {
            throw
        } catch [System.IO.IOException] {
            # Another process holds the exclusive handle: CONTENTION.
            Write-ContentionSignalOnce "handle"
            $remaining = $WaitBudget - $Stopwatch.Elapsed.TotalSeconds
            if ($remaining -le 0) {
                Write-Stderr "contended: the lock file is held by another writer, wait budget ${WaitBudget}s expired"
                exit 3
            }
            $sleepFor = [Math]::Min($PollBudget, $remaining)
            Start-Sleep -Seconds $sleepFor
        }
    }
}

function Open-NonCreating([string]$Path, $Stopwatch, [double]$WaitBudget, [double]$PollBudget) {
    while ($true) {
        try {
            $fs = New-Object System.IO.FileStream($Path, [System.IO.FileMode]::Open,
                [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
            return @{ Stream = $fs; Missing = $false }
        } catch [System.IO.FileNotFoundException] {
            return @{ Stream = $null; Missing = $true }
        } catch [System.IO.DirectoryNotFoundException] {
            return @{ Stream = $null; Missing = $true }
        } catch [System.IO.IOException] {
            Write-ContentionSignalOnce "handle"
            $remaining = $WaitBudget - $Stopwatch.Elapsed.TotalSeconds
            if ($remaining -le 0) {
                Write-Stderr "contended: the lock file is held by another writer, wait budget ${WaitBudget}s expired"
                exit 3
            }
            $sleepFor = [Math]::Min($PollBudget, $remaining)
            Start-Sleep -Seconds $sleepFor
        }
    }
}

# ---------------------------------------------------------------------
# Numeric / token parameter validation. Every check below runs BEFORE
# any file handle is opened, so a refused value mutates nothing.
# ---------------------------------------------------------------------
function Test-NonNegativeIntString([string]$Value) {
    return ($Value -match $DigitsPattern)
}
function ConvertTo-BoundedInt32([string]$Value) {
    try { return [int]::Parse($Value, [System.Globalization.CultureInfo]::InvariantCulture) }
    catch { return $null }
}

$Mode = $PSCmdlet.ParameterSetName

if ($Mode -ne "ResolveOwner") {
    if (-not (Test-NonNegativeIntString $WaitSeconds)) { exit 2 }
    $WaitSecondsInt = ConvertTo-BoundedInt32 $WaitSeconds
    if ($null -eq $WaitSecondsInt) { exit 2 }

    if (-not ($PollSeconds -match $DigitsPattern) -or $PollSeconds -eq "0") { exit 2 }
    $PollSecondsInt = ConvertTo-BoundedInt32 $PollSeconds
    if ($null -eq $PollSecondsInt -or $PollSecondsInt -le 0) { exit 2 }

    if ([string]::IsNullOrWhiteSpace($LaneHome)) { exit 2 }
    $LockPath = Join-Path $LaneHome "lane.lock"
}

if ($Mode -eq "Acquire" -or $Mode -eq "Release") {
    if (-not ($DebateId -cmatch $TokenPattern)) { exit 2 }
    if (-not (Test-NonNegativeIntString $OwnerPid)) { exit 2 }
    $OwnerPidInt = ConvertTo-BoundedInt32 $OwnerPid
    if ($null -eq $OwnerPidInt -or $OwnerPidInt -le 0) { exit 2 }
    if (-not ($OwnerStartTicksUtc -match $DigitsPattern)) { exit 2 }
}
if ($Mode -eq "Acquire") {
    if ([string]::IsNullOrWhiteSpace($DebateHome)) { exit 2 }
}
# "Provided" means the caller supplied the parameter at all. An empty or
# whitespace value is a REFUSED value, never silently treated as absent,
# because a record claiming to carry a name and carrying nothing forces
# every reader to invent a meaning for it. Same rule as -Nonce.
$OwnerNameProvided = $PSBoundParameters.ContainsKey("OwnerName")
if ($OwnerNameProvided -and [string]::IsNullOrWhiteSpace($OwnerName)) { exit 2 }
# -Nonce: mandatory on -Release (the binder guarantees it is bound, but
# an explicit -Nonce "" still binds successfully, so the pattern is
# checked regardless of emptiness), optional on -Acquire. "Provided"
# means the caller supplied the parameter at all - an empty value is a
# REFUSED value (exit 2), never silently treated as "absent".
$NonceProvided = $PSBoundParameters.ContainsKey("Nonce")
if ($NonceProvided -and -not ($Nonce -cmatch $TokenPattern)) { exit 2 }

if ($Mode -eq "ForceRelease") {
    if ([string]::IsNullOrWhiteSpace($ConfirmHost)) { exit 2 }
    if (-not (Test-NonNegativeIntString $ConfirmOwnerPid)) { exit 2 }
    $ConfirmOwnerPidInt = ConvertTo-BoundedInt32 $ConfirmOwnerPid
    if ($null -eq $ConfirmOwnerPidInt -or $ConfirmOwnerPidInt -le 0) { exit 2 }
    if (-not ($ConfirmOwnerStartTicksUtc -match $DigitsPattern)) { exit 2 }
    if (-not ($ConfirmDebateId -cmatch $TokenPattern)) { exit 2 }
    if (-not ($ConfirmNonce -cmatch $TokenPattern)) { exit 2 }
}
if ($Mode -eq "MalformedOverride") {
    if (-not ($ConfirmSha256 -match $Sha256Pattern)) { exit 2 }
    $ConfirmSha256 = $ConfirmSha256.ToLowerInvariant()
}

# ---------------------------------------------------------------------
# Mode implementations.
# ---------------------------------------------------------------------
# ---------------------------------------------------------------------
# A RECORD IS A CLAIM that this owner holds the lane, so writing one
# requires LIVE - not merely "not known to be dead". Called immediately
# before every record write, never on a path that writes nothing.
#
# UNMEASURABLE refuses HERE and is accepted at the gate above, and the
# asymmetry is the whole design: the pid lookup succeeded, so the
# process exists, but the pid-REUSE guard did not run, and an identity
# whose reuse guard never ran is not one to write down as an owner. Where
# nothing is written there is nothing to be wrong about, which is why the
# idempotent re-entry path never calls this.
# ---------------------------------------------------------------------
function Assert-OwnerLiveForWrite($OpenInfo) {
    $atWrite = Get-Liveness -OwnerPidValue $OwnerPidInt -TicksValue $OwnerStartTicksUtc
    if ($atWrite -ne "LIVE") {
        # A file THIS CALL created must not be left at zero length: a
        # zero-length file is MALFORMED by rule, so a refusal would turn
        # a free lane into one needing the guarded override. Same
        # obligation, and the same remedy, as the nonce-against-free
        # refusal below. Caught by this fix's own oracle, which is what
        # "a fix is new code and gets no discount" looks like in
        # practice.
        if ($null -ne $OpenInfo -and -not $OpenInfo.Existed) {
            Write-RecordJson $OpenInfo.Stream '{"version":1,"state":"free"}'
        }
        Close-CurrentStream
        Write-Stderr ("refusing to record an owner that is not live (" + $atWrite +
                      "): pid " + $OwnerPidInt + ", ticks " + $OwnerStartTicksUtc)
        exit 2
    }
}

function Invoke-AcquireMode {
    # THE PROPOSED OWNER MUST NOT BE DEAD, AND NOTHING CHECKED IT.
    # `Get-Liveness` has been in this file the whole time and acquire
    # called it on ONE thing: the EXISTING holder's record, to decide
    # reclaim rights. The owner being WRITTEN DOWN was validated for
    # syntax only. So a caller could record an already-dead identity,
    # the next acquire would read that record as DEAD and reclaim it,
    # and the mutual exclusion this lock exists to provide was gone
    # while every status read looked ordinary.
    #
    # Found by the 0.22.0 plan debate, backlog item 26's silent half.
    # The item said this needed a wrapping harness to reproduce. It did
    # not: a pid that has exited reaches it directly.
    #
    # THIS GATE IS A FAST REFUSAL, NOT THE GUARANTEE. It refuses DEAD
    # only, and it runs ONCE, before the acquisition loop below - so on
    # its own it cannot be the thing that keeps a dead identity out of
    # the record. A caller that WAITS behind a holder is measured here,
    # waits, may DIE, and would then be written the moment the holder
    # releases. The cross-vendor round found exactly that window.
    #
    # The guarantee is at the WRITE SITES: `Assert-OwnerLiveForWrite` is
    # called immediately before every record write and requires LIVE.
    # UNMEASURABLE survives only where NOTHING is written - the
    # idempotent re-entry path, where a matching nonce and a matching
    # retained identity already establish ownership without a
    # measurement. That is the case the DEAD-only rule was protecting,
    # and it is protected without letting an unmeasured owner be
    # recorded.
    $proposed = Get-Liveness -OwnerPidValue $OwnerPidInt -TicksValue $OwnerStartTicksUtc
    if ($proposed -eq "DEAD") {
        Write-Stderr ("the proposed owner is not live (measured DEAD): pid " +
                      $OwnerPidInt + ", ticks " + $OwnerStartTicksUtc)
        exit 2
    }
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    while ($true) {
        $open = Open-ForAcquire -Path $LockPath -Stopwatch $sw -WaitBudget $WaitSecondsInt -PollBudget $PollSecondsInt
        $script:OpenStream = $open.Stream

        if (-not $open.Existed) {
            $cls = @{ Malformed = $false; State = "free" }
        } else {
            $bytes = Read-AllBytes $open.Stream
            $cls = Get-Classification $bytes
        }

        if ($cls.Malformed) {
            Close-CurrentStream
            exit 4
        }

        if ($cls.State -eq "free") {
            if ($NonceProvided) {
                # "Only ACQUIRE may create the file, initializing it to
                # free and then proceeding through its table" - a nonce
                # supplied against a free record is a table refusal, not
                # a pre-handle parameter refusal, so it can reach here
                # AFTER this call's own CreateNew produced a genuine
                # zero-length file. Leaving that zero-length file behind
                # would read back as MALFORMED (a zero-length file is
                # malformed by rule) rather than the free record this
                # call was supposed to initialize - so a freshly created
                # file is written out as an explicit free record before
                # the refusal exits. A pre-existing free record is left
                # untouched, matching every other refusal in this table.
                if (-not $open.Existed) {
                    Write-RecordJson $open.Stream '{"version":1,"state":"free"}'
                }
                Close-CurrentStream
                exit 2
            }
            Assert-OwnerLiveForWrite $open
            $newNonce = New-Nonce
            $nowTicks = [string]([System.DateTime]::UtcNow.Ticks)
            $rec = [ordered]@{
                version = 1; state = "held"; host = $env:COMPUTERNAME
                ownerPid = $OwnerPidInt; ownerStartTicksUtc = $OwnerStartTicksUtc
                debateId = $DebateId; nonce = $newNonce; debateHome = $DebateHome
                acquiredTicksUtc = $nowTicks
            }
            if ($OwnerNameProvided) { $rec["ownerName"] = $OwnerName }
            Write-RecordJson $open.Stream (ConvertTo-Json $rec -Compress)
            Close-CurrentStream
            Write-Output $newNonce
            exit 0
        }

        # state -eq "held"
        $rec = $cls.Record
        $sameHost = ($rec.host -ieq $env:COMPUTERNAME)
        if (-not $sameHost) { Close-CurrentStream; exit 4 }

        $liveness = Get-Liveness -OwnerPidValue ([int]$rec.ownerPid) -TicksValue $rec.ownerStartTicksUtc

        if ($liveness -eq "DEAD") {
            if ($NonceProvided) { Close-CurrentStream; exit 2 }
            Assert-OwnerLiveForWrite $open
            $newNonce = New-Nonce
            $nowTicks = [string]([System.DateTime]::UtcNow.Ticks)
            $newRec = [ordered]@{
                version = 1; state = "held"; host = $env:COMPUTERNAME
                ownerPid = $OwnerPidInt; ownerStartTicksUtc = $OwnerStartTicksUtc
                debateId = $DebateId; nonce = $newNonce; debateHome = $DebateHome
                acquiredTicksUtc = $nowTicks
            }
            # The RECLAIM writer, and it is a SECOND one. The name here
            # is the new owner's; the dead holder's goes with its record.
            if ($OwnerNameProvided) { $newRec["ownerName"] = $OwnerName }
            Write-RecordJson $open.Stream (ConvertTo-Json $newRec -Compress)
            Close-CurrentStream
            Write-Stderr "reclaimed a dead holder: pid $($rec.ownerPid) ticks $($rec.ownerStartTicksUtc) debate $($rec.debateId) home $($rec.debateHome)"
            Write-Output $newNonce
            exit 0
        }

        # LIVE or UNMEASURABLE - treated identically for routing.
        $fourMatch = ($rec.ownerPid -eq $OwnerPidInt) -and
                     ($rec.ownerStartTicksUtc -eq $OwnerStartTicksUtc) -and
                     ($rec.debateId -eq $DebateId)

        if ($fourMatch -and $NonceProvided -and $rec.nonce -eq $Nonce) {
            if (Test-DebateHomeEqual $DebateHome $rec.debateHome) {
                $stdoutNonce = $rec.nonce
                Close-CurrentStream
                Write-Output $stdoutNonce
                exit 0
            } else {
                Close-CurrentStream
                exit 2
            }
        }

        # Contention (acquire table rows 5 and 6): release the handle so
        # another process can act while this one waits, then retry.
        $holderPid = $rec.ownerPid
        $holderTicks = $rec.ownerStartTicksUtc
        $holderDebateId = $rec.debateId
        Close-CurrentStream
        Write-ContentionSignalOnce "holder"
        $remaining = $WaitSecondsInt - $sw.Elapsed.TotalSeconds
        if ($remaining -le 0) {
            Write-Stderr "contended: holder pid $holderPid ticks $holderTicks debate $holderDebateId, liveness $liveness, wait budget ${WaitSecondsInt}s expired"
            exit 3
        }
        $sleepFor = [Math]::Min($PollSecondsInt, $remaining)
        Start-Sleep -Seconds $sleepFor
    }
}

function Invoke-ReleaseMode {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $open = Open-NonCreating -Path $LockPath -Stopwatch $sw -WaitBudget $WaitSecondsInt -PollBudget $PollSecondsInt
    if ($open.Missing) { exit 5 }
    $script:OpenStream = $open.Stream
    $bytes = Read-AllBytes $open.Stream
    $cls = Get-Classification $bytes
    if ($cls.Malformed) { Close-CurrentStream; exit 4 }
    if ($cls.State -eq "free") { Close-CurrentStream; exit 5 }

    $rec = $cls.Record
    $sameHost = ($rec.host -ieq $env:COMPUTERNAME)
    if (-not $sameHost) { Close-CurrentStream; exit 4 }

    $identityMatch = ($rec.ownerPid -eq $OwnerPidInt) -and
                     ($rec.ownerStartTicksUtc -eq $OwnerStartTicksUtc) -and
                     ($rec.debateId -eq $DebateId) -and
                     ($rec.nonce -eq $Nonce)
    if ($identityMatch) {
        Write-RecordJson $open.Stream '{"version":1,"state":"free"}'
        Close-CurrentStream
        exit 0
    }
    Close-CurrentStream
    exit 5
}

function Invoke-ForceReleaseMode {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $open = Open-NonCreating -Path $LockPath -Stopwatch $sw -WaitBudget $WaitSecondsInt -PollBudget $PollSecondsInt
    if ($open.Missing) { exit 5 }
    $script:OpenStream = $open.Stream
    $bytes = Read-AllBytes $open.Stream
    $cls = Get-Classification $bytes
    if ($cls.Malformed) { Close-CurrentStream; exit 4 }
    if ($cls.State -eq "free") { Close-CurrentStream; exit 5 }

    $rec = $cls.Record
    $match = ($rec.host -ieq $ConfirmHost) -and
             ($rec.ownerPid -eq $ConfirmOwnerPidInt) -and
             ($rec.ownerStartTicksUtc -eq $ConfirmOwnerStartTicksUtc) -and
             ($rec.debateId -eq $ConfirmDebateId) -and
             ($rec.nonce -eq $ConfirmNonce)
    if ($match) {
        Write-RecordJson $open.Stream '{"version":1,"state":"free"}'
        Close-CurrentStream
        Write-Stderr "force-released holder: host $($rec.host) pid $($rec.ownerPid) ticks $($rec.ownerStartTicksUtc) debate $($rec.debateId) home $($rec.debateHome)"
        exit 0
    }
    Close-CurrentStream
    exit 5
}

function Invoke-MalformedOverrideMode {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $open = Open-NonCreating -Path $LockPath -Stopwatch $sw -WaitBudget $WaitSecondsInt -PollBudget $PollSecondsInt
    if ($open.Missing) { exit 5 }
    $script:OpenStream = $open.Stream
    $bytes = Read-AllBytes $open.Stream
    $cls = Get-Classification $bytes

    if (-not $cls.Malformed) {
        # Well-formed. This mode is only for malformed records - exit 5 -
        # EXCEPT a well-formed FOREIGN-HOST held record, which preprocessing
        # scopes to exit 4 (only -ForceRelease may act on it).
        if ($cls.State -eq "held") {
            $sameHost = ($cls.Record.host -ieq $env:COMPUTERNAME)
            if (-not $sameHost) { Close-CurrentStream; exit 4 }
        }
        Close-CurrentStream
        exit 5
    }

    $actualHash = Get-Sha256Hex $bytes
    if ($actualHash -ieq $ConfirmSha256) {
        Write-RecordJson $open.Stream '{"version":1,"state":"free"}'
        Close-CurrentStream
        Write-Stderr "overrode malformed lock: bytes $($bytes.Length) sha256 $actualHash"
        exit 0
    }
    Close-CurrentStream
    exit 5
}

function Invoke-StatusMode {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $open = Open-NonCreating -Path $LockPath -Stopwatch $sw -WaitBudget $WaitSecondsInt -PollBudget $PollSecondsInt
    if ($open.Missing) {
        Write-Output '{"state":"free"}'
        exit 0
    }
    $script:OpenStream = $open.Stream
    $bytes = Read-AllBytes $open.Stream
    Close-CurrentStream

    $cls = Get-Classification $bytes
    if ($cls.Malformed) {
        $hash = Get-Sha256Hex $bytes
        $obj = [ordered]@{ state = "MALFORMED"; bytes = $bytes.Length; sha256 = $hash }
        Write-Output (ConvertTo-Json $obj -Compress)
        exit 0
    }
    if ($cls.State -eq "free") {
        Write-Output '{"state":"free"}'
        exit 0
    }

    $rec = $cls.Record
    $sameHost = ($rec.host -ieq $env:COMPUTERNAME)
    if (-not $sameHost) {
        $livenessOut = "UNKNOWN"
    } else {
        $l = Get-Liveness -OwnerPidValue ([int]$rec.ownerPid) -TicksValue $rec.ownerStartTicksUtc
        if ($l -eq "UNMEASURABLE") { $livenessOut = "UNKNOWN" } else { $livenessOut = $l }
    }
    $obj = [ordered]@{
        state = "held"; host = $rec.host; ownerPid = [int64]$rec.ownerPid
        ownerStartTicksUtc = $rec.ownerStartTicksUtc; debateId = $rec.debateId
        nonce = $rec.nonce; debateHome = $rec.debateHome; liveness = $livenessOut
    }
    if (@($rec.PSObject.Properties.Name) -ccontains "ownerName") {
        $obj["ownerName"] = $rec.ownerName
    }
    Write-Output (ConvertTo-Json $obj -Compress)
    exit 0
}

# ---------------------------------------------------------------------
# Owner resolution walks PAST its own transports.
#
# It used to return the DIRECT parent, which is only the right answer
# when the caller happens to invoke the tool from the process that owns
# the debate. Under a wrapper that spawns a fresh shell per call, the
# direct parent is that shell: a NEW pid every call, already exited by
# the next status read. Backlog item 26 reported exactly that, and
# test_resolve_owner_is_stable_across_an_added_shell_frame reproduces it
# with one added shell frame - no wrapping harness required.
#
# So the walk SKIPS the hosts this tool is invoked through and stops at
# the first ancestor that is not one. Measured chain on the shipped
# path, 2026-08-04: pwsh -> claude -> pwsh -> Code -> Code -> explorer.
# The direct parent is already non-transparent there, so the resolved
# owner is UNCHANGED for the ordinary caller; only nested invocations
# move, and they move onto the stable answer.
#
# THE COST, STATED. A genuinely long-lived orchestration script running
# in one of these hosts is skipped, and the owner resolves to ITS
# parent - a lock that can outlive the debate rather than one that dies
# inside it. That is item 26's visible half traded against its silent
# half, and it is the direction that fails toward a stuck lane rather
# than toward two debates on one credential.
#
# The list names transports, not "approved owners". Adding a name here
# says "this tool is invoked THROUGH that", nothing else.
# ---------------------------------------------------------------------
$script:TransparentHosts = @("pwsh.exe", "powershell.exe", "cmd.exe", "conhost.exe")
$script:AncestryWalkLimit = 16

function Invoke-ResolveOwnerMode {
    try {
        # The seam forces the ancestry read to throw. Safe by
        # construction: its only reachable effect is the refusal below,
        # and no path through it emits an owner record. Same shape as
        # PARALLAX_LANE_LOCK_STARTTIME_FAULT.
        if ($env:PARALLAX_LANE_LOCK_ANCESTRY_FAULT) {
            throw "PARALLAX_LANE_LOCK_ANCESTRY_FAULT injected: simulated ancestry read failure"
        }
        $cursor = $PID
        $steps = 0
        while ($true) {
            $steps++
            if ($steps -gt $script:AncestryWalkLimit) {
                Write-Stderr ("owner resolution found no non-transport ancestor within " +
                              $script:AncestryWalkLimit + " levels")
                exit 2
            }
            $wmi = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId=$cursor" -ErrorAction Stop
            if ($null -eq $wmi) { throw "process $cursor disappeared during the ancestry walk" }
            $parentPid = [int]$wmi.ParentProcessId
            if ($parentPid -le 0) {
                Write-Stderr "owner resolution reached the top of the process tree with no non-transport ancestor"
                exit 2
            }
            # NAMED RESIDUAL: this follows ParentProcessId with no
            # creation-time ordering guard, so an ancestor pid that exited
            # and was REUSED inside the walk's own window resolves a wrong
            # live owner. A merely dead ancestor fails closed (null here,
            # or Get-Process throwing below), so only reuse during the walk
            # slips through, and it lands on the stuck-lane direction this
            # whole function already trades toward. The standard guard - a
            # parent whose start time is not LATER than its child's - would
            # close it, and is not added here because no test in this repo
            # can watch it fail for the reason it claims. Backlog item 29.
            $parentWmi = Get-CimInstance -ClassName Win32_Process -Filter "ProcessId=$parentPid" -ErrorAction Stop
            if ($null -eq $parentWmi) { throw "ancestor $parentPid disappeared during the ancestry walk" }
            $parentName = [string]$parentWmi.Name
            if ([string]::IsNullOrWhiteSpace($parentName)) {
                throw "ancestor $parentPid has no readable process name"
            }
            $isTransparent = $false
            foreach ($h in $script:TransparentHosts) {
                if ([System.String]::Equals($parentName, $h, [System.StringComparison]::OrdinalIgnoreCase)) {
                    $isTransparent = $true
                    break
                }
            }
            if (-not $isTransparent) {
                $parentProc = Get-Process -Id $parentPid -ErrorAction Stop
                $ticks = [string]$parentProc.StartTime.ToUniversalTime().Ticks
                if ([string]::IsNullOrWhiteSpace($ticks)) {
                    throw "ancestor $parentPid has no readable start time"
                }
                $obj = [ordered]@{
                    ownerPid = $parentPid
                    ownerStartTicksUtc = $ticks
                    ownerName = $parentName
                }
                Write-Output (ConvertTo-Json $obj -Compress)
                exit 0
            }
            $cursor = $parentPid
        }
    } catch {
        Write-Stderr "owner resolution failed"
        exit 2
    }
}

try {
    switch ($Mode) {
        "Acquire" { Invoke-AcquireMode }
        "Release" { Invoke-ReleaseMode }
        "Status" { Invoke-StatusMode }
        "ForceRelease" { Invoke-ForceReleaseMode }
        "MalformedOverride" { Invoke-MalformedOverrideMode }
        "ResolveOwner" { Invoke-ResolveOwnerMode }
    }
} catch {
    # Any unclassified runtime failure - a write/flush error, an
    # unreadable file, anything not already mapped to a specific exit
    # code above - is exit 6. An unmade or failed measurement is never a
    # clean one.
    Close-CurrentStream
    Write-Stderr "lock tool failed: $($_.Exception.Message)"
    exit 6
}
