# new-kimi-lane-home.ps1 - build (or remove) a per-DEBATE, throwaway
# KIMI_CODE_HOME.
#
# WHY: the real ~/.kimi-code/config.toml is user-global and, on this
# machine, carries seven Orca-managed lifecycle hooks - including
# PreToolUse and PermissionRequest - each running a shell script. A hook
# block in the reviewer's own config is a command-executing back-channel
# sitting on its approval path; the isolation this script builds is the
# only thing standing between the backup lane and that surface. The home
# is built once before round 1 of a debate and reused by every call of
# that SAME debate - the rounds of one debate are one session - never
# reused across debates, because a reused home carries stale sessions,
# which corrupts route-attribution evidence rather than merely being
# untidy.
#
# CREDENTIAL SOURCE, task 6 (2026-08-01 lane-credential-and-lock plan):
# this builder no longer COPIES a credential. The single kimi-code login
# lives once, in the persistent LANE HOME at -LaneHome, produced by
# tools/new-kimi-lane-login.ps1. Every debate home's `credentials`
# directory is instead a JUNCTION to the lane home's, so a token refresh
# writes through to the one file on disk instead of forking a copy that
# strands a stale refresh token behind - a copy that refreshes rotates
# BOTH tokens server-side and leaves the source holding a retired one,
# confirmed live. Access to the lane home (credential validation, and the
# junction's target existing) is serialized by tools/kimi-lane-lock.ps1,
# a persistent, liveness-anchored lock file inside the lane home. This
# builder ACQUIRES that lock before validating the lane credential and
# RETAINS it (never releases) on a successful build - custody of the
# nonce passes to the caller in the build's own stdout, and only that
# caller's later -Remove call releases it.
#
# Two parameter sets, because a GLOBALLY mandatory -Model would make the
# removal form uncallable:
#   Build (default):  -Path <dir> -Model <id> [-Effort <level>]
#                      -LaneHome <dir> -DebateId <hex32>
#                      -OwnerPid <pid> -OwnerStartTicksUtc <ticks>
#   Remove:            -Path <dir> -Remove
#                      -LaneHome <dir> -DebateId <hex32>
#                      -OwnerPid <pid> -OwnerStartTicksUtc <ticks>
#                      -Nonce <hex32>
# -LaneHome/-DebateId/-OwnerPid/-OwnerStartTicksUtc are mandatory in BOTH
# modes; -Nonce is additionally mandatory on -Remove only (Build never
# takes one - the lock mints a fresh nonce on a fresh acquisition, and
# custody of it is handed back in the build's own stdout).
# -Model has NO default. The canonical backup model id is single-sourced
# in skills/multi-model-verify/references/model-prompting-notes.md and
# forbidden as a literal in every tools/*.ps1 file by
# evals/multi-model-verify/test_backup_lane.py's SWEEP_GLOBS; a default
# value here would be exactly that literal.
#
# Windows PowerShell 5.1 compatible, ASCII ONLY.
#
# Exit codes:
#   0  built (custody JSON on stdout) / removed ("removed <path>" on stdout)
#   1  a gate refusal that propagates as an ordinary UNCAUGHT PowerShell
#      error: destination reused, unsafe -Model/-Effort, git-work-tree
#      check, model-table carrying, a Remove-mode sentinel/dangerous-root/
#      profile/.git refusal, or - added 0.20.0 - the skills-directory
#      POSTCONDITION and its two test seams. Measured: an uncaught throw
#      exits 1, which is why the postcondition is listed here and not
#      under 2 with the parameter refusals
#   2  a -LaneHome/-DebateId/-OwnerPid/-OwnerStartTicksUtc/-Nonce value was
#      refused by this script or by the lock tool (parameter refusal, or
#      an identity/-Path mismatch at the lock)
#   3  lock contention, propagated unchanged from the lock tool
#   4  the lock is malformed or foreign-host, propagated from the lock tool
#   5  a lock release was refused, propagated from the lock tool
#   6  an unusable lane-home directory, an unusable lane credential (with
#      or without the login recovery command - see below), validator
#      failure, a post-delete verification failure, or an injected fault
#      seam
[CmdletBinding(DefaultParameterSetName = "Build")]
param(
    [Parameter(Mandatory = $true)][string]$Path,
    [Parameter(ParameterSetName = "Build", Mandatory = $true)][string]$Model,
    [Parameter(ParameterSetName = "Build", Mandatory = $false)][string]$Effort = "high",
    [Parameter(ParameterSetName = "Remove", Mandatory = $true)][switch]$Remove,
    [Parameter(Mandatory = $true)][string]$LaneHome,
    [Parameter(Mandatory = $true)][string]$DebateId,
    [Parameter(Mandatory = $true)][string]$OwnerPid,
    [Parameter(Mandatory = $true)][string]$OwnerStartTicksUtc,
    [Parameter(ParameterSetName = "Remove", Mandatory = $true)][string]$Nonce
)

$ErrorActionPreference = "Stop"

$SentinelName = ".parallax-lane-home"
$SentinelMagic = "PARALLAX-LANE-HOME-V1"

$LockScript = Join-Path $PSScriptRoot "kimi-lane-lock.ps1"
$ValidatorScript = Join-Path $PSScriptRoot "read-kimi-credential-state.ps1"

$DigitsPattern = '\A[0-9]+\z'
# -DebateId/-Nonce: exactly 32 LOWERCASE hex, matching the lock tool's own
# $TokenPattern. -cmatch, not -match: PowerShell's -match is
# case-INSENSITIVE by default, which would silently accept "A".."F".
$TokenPattern = '\A[0-9a-f]{32}\z'

function Write-Stderr([string]$Line) {
    [Console]::Error.WriteLine($Line)
}

function Test-NonNegativeIntString([string]$Value) {
    return ($Value -match $DigitsPattern)
}

# -Model and -Effort are caller-supplied and are interpolated directly
# into config.toml below. Unvalidated, a -Model carrying a double quote
# and a newline breaks out of the `[models."$Model"]` quoting and can
# write an attacker-chosen table - including a fabricated hooks array
# of tables - into the rendered config: exactly the command-executing
# back-channel this script exists to keep out of the reviewer's config.
# Everything this pattern allows is also everything the render below
# needs: letters, digits, dot, dash, underscore, slash. Nothing outside
# it can close a TOML string or open a new table.
#
# \A and \z, not ^ and $: in .NET regex, $ matches before a single
# trailing newline at the end of the string even without multiline mode,
# so '^[...]*$' let a value ending in exactly one literal newline through
# despite the newline itself not being in the allowed set - reproduced
# live (a hostile -Model ending in "\n" passed this check and the script
# went on to create directories). \A and \z mean absolute start and
# absolute end of the string, with no such exception, so nothing outside
# the allowed set can pass, trailing newline included.
$SafeTokenPattern = '\A[A-Za-z0-9][A-Za-z0-9._/-]*\z'
function Test-SafeConfigToken([string]$Value) {
    return ($Value -match $SafeTokenPattern)
}

# ---------------------------------------------------------------------
# A HASHTABLE splat, not an array. Measured live (tools/new-kimi-lane-
# login.ps1's own Invoke-LockCall, same finding): splatting an
# alternating "-Name","value" ARRAY against kimi-lane-lock.ps1 throws
# "Parameter set cannot be resolved using the specified named parameters"
# because five of its six parameter sets share the mandatory -LaneHome,
# defeating the array-splat binder's set-disambiguation pass. This is an
# IN-PROCESS call (`& $LockScript`, not Start-Process): its stdout (the
# nonce) is captured by the assignment; its stderr - written via
# [Console]::Error.WriteLine, which bypasses PowerShell's own `2>` stream
# redirection - passes straight through to this script's own stderr as a
# structural side effect of running in the same process, not by manual
# re-emission. This is what lets a reclaim or contention diagnostic from
# the lock survive into the builder's own stderr unchanged.
# ---------------------------------------------------------------------
function Invoke-LockCall([hashtable]$LockArgs) {
    $stdout = & $LockScript @LockArgs
    $exitCode = $LASTEXITCODE
    return @{ Stdout = (@($stdout) -join "`n"); ExitCode = $exitCode }
}

# ---------------------------------------------------------------------
# THE LANE LOGIN RECOVERY COMMAND. Frozen verbatim in the plan's "Fixed
# names and values" (shared with Task 8's doctor rows, which is why it is
# not hand-built here): a single-quoted template with a literal
# "<lane-home>" placeholder, so building it as a PowerShell single-quoted
# string literal (no $ or ` interpolation) and then a plain, non-regex
# .Replace() is what keeps the frozen text frozen.
#
# THE COMMAND IS FAIL-CLOSED. The first two attempts at it were not: a
# plain `a; b` chain runs `b` whether or not `a` worked, and even with
# -ErrorAction Stop added to the parse, a failed ConvertFrom-Json in a
# bare `;`-chain still lets the next statement run - measured live on
# both hosts, the login wrapper was invoked with a NULL identity. This
# form runs inside a child scriptblock that sets
# $ErrorActionPreference = 'Stop' around a try, so every later step is
# structurally unreachable after any failure and the preference never
# leaks into the user's own shell. It also validates what it received
# rather than only that the call succeeded: exactly one nonblank stdout
# line, a PSCustomObject carrying exactly ownerPid and
# ownerStartTicksUtc, an integral pid above zero, ticks matching
# \A[0-9]+\z, and a TEMP that exists and is a directory.
# ---------------------------------------------------------------------
$RecoveryCommandTemplate = '& { $ErrorActionPreference = ''Stop''; try { $ownerLines = @(& ''tools/kimi-lane-lock.ps1'' -ResolveOwner); $ownerExit = $LASTEXITCODE; if ($ownerExit -ne 0) { throw "owner resolution failed with exit $ownerExit" }; if ($ownerLines.Count -ne 1 -or -not ($ownerLines[0] -is [string]) -or [string]::IsNullOrWhiteSpace([string]$ownerLines[0])) { throw ''owner resolution returned invalid output'' }; $owner = $ownerLines[0] | ConvertFrom-Json -ErrorAction Stop; if (-not ($owner -is [System.Management.Automation.PSCustomObject])) { throw ''owner resolution returned invalid schema'' }; $ownerFields = @($owner.PSObject.Properties.Name); if ($ownerFields.Count -ne 2 -or -not ($ownerFields -ccontains ''ownerPid'') -or -not ($ownerFields -ccontains ''ownerStartTicksUtc'') -or -not (($owner.ownerPid -is [int]) -or ($owner.ownerPid -is [long])) -or [long]$owner.ownerPid -le 0 -or -not ($owner.ownerStartTicksUtc -is [string]) -or $owner.ownerStartTicksUtc -notmatch ''\A[0-9]+\z'') { throw ''owner resolution returned invalid schema'' }; if ([string]::IsNullOrWhiteSpace($env:TEMP) -or -not (Test-Path -LiteralPath $env:TEMP -PathType Container -ErrorAction Stop)) { throw ''TEMP is not an existing directory'' }; $verdictOut = Join-Path -Path $env:TEMP -ChildPath ''parallax-kimi-lane-login-verdict.json'' -ErrorAction Stop; & ''tools/new-kimi-lane-login.ps1'' -LaneHome ''<lane-home>'' -OwnerPid ([string]$owner.ownerPid) -OwnerStartTicksUtc $owner.ownerStartTicksUtc -VerdictOut $verdictOut; $loginExit = $LASTEXITCODE; if ($loginExit -ne 0) { throw "lane login failed with exit $loginExit" } } catch { throw } }'

function Get-LaneLoginRecoveryCommand([string]$ResolvedLaneHome) {
    # "<lane-home>" substitution, a literal algorithm: replace every ' in
    # the resolved lane home with '', then the template's own surrounding
    # quotes enclose the result - not a description, an exact recipe, so
    # the success row of Task 6 Step 1b's four-row oracle (a lane home
    # CONTAINING an apostrophe) can require the DOUBLED apostrophe in the
    # emitted text.
    $escaped = $ResolvedLaneHome.Replace("'", "''")
    return $RecoveryCommandTemplate.Replace("<lane-home>", $escaped)
}

# ---------------------------------------------------------------------
# The credential validator's frozen status/detail table (Task 2's
# interface). A pairing outside this table is VALIDATOR FAILURE, never a
# credential state - same table tools/new-kimi-lane-login.ps1 carries.
# ---------------------------------------------------------------------
$ValidVerdictPairs = @(
    @("ok", "valid"),
    @("absent", "no-file"),
    @("unreadable", "read-failed"),
    @("malformed", "not-json"),
    @("malformed", "not-object"),
    @("malformed", "missing-field"),
    @("malformed", "wrong-type"),
    @("malformed", "blank-token")
)
# The pair match is CASE-EXACT. -eq is case-insensitive on this platform,
# so a validator emitting "OK"/"Valid" was accepted as the frozen
# "ok"/"valid" pair, and this caller then routed on a status the frozen
# table does not contain.
function Test-ValidVerdictPair([string]$Status, [string]$Detail) {
    foreach ($pair in $ValidVerdictPairs) {
        if ($pair[0] -ceq $Status -and $pair[1] -ceq $Detail) { return $true }
    }
    return $false
}

# ---------------------------------------------------------------------
# Invokes the credential validator as a genuine SEPARATE process (needed
# to observe its stdout and stderr independently) and accepts the
# measurement ONLY when all four parts hold: the process launched, it
# exited 0, stderr was EMPTY, and stdout was exactly one parseable line
# whose object has exactly status/detail/fields with a status/detail
# pairing from the table above and fields an array of strings. Anything
# else - including a nonzero exit carrying a syntactically valid line, or
# an exit 0 carrying malformed/schema-invalid output - is VALIDATOR
# FAILURE and is never read as a credential state. Copied from
# tools/new-kimi-lane-login.ps1's function of the same name and the same
# contract; that file must not be rewritten by this task, so the
# behaviour is duplicated rather than shared.
#
# Both -File and -Path arguments are individually double-quoted before
# being handed to Start-Process -ArgumentList: that cmdlet joins its
# array elements with a plain space and does NOT quote an element that
# itself contains one, so an unquoted path segment carrying a space
# mis-tokenizes into two argv entries - measured live, and the reason the
# dual-host success fixture below combines a space with an apostrophe in
# one segment.
#
# The captured-stream reads are TERMINATING: a failed read is validator
# failure, never empty-stderr-and-proceed - "-ErrorAction
# SilentlyContinue" turned a read that could not be made into "stderr was
# empty", which is the acceptance rule's own governing invariant
# inverted. Get-Content -Raw on a genuinely EMPTY file still returns
# $null with no error, so that null is mapped to "" only AFTER the read
# has succeeded, never as a stand-in for a failed one.
# PARALLAX_KIMI_CREDENTIAL_VALIDATOR_CAPTURE_READ_FAULT: any nonempty
# value deletes the real stderr capture file immediately before it is
# read, producing a genuine (not simulated) Get-Content failure - isolated
# to stderr, and stdout left untouched, so the oracle cannot be satisfied
# by a coincidental empty-stdout rejection from a different check.
# ---------------------------------------------------------------------
function Invoke-CredentialValidator([string]$CredPath) {
    $hostExe = (Get-Process -Id $PID).Path
    $outFile = [System.IO.Path]::GetTempFileName()
    $errFile = [System.IO.Path]::GetTempFileName()
    try {
        try {
            $proc = Start-Process -FilePath $hostExe `
                -ArgumentList @("-NoProfile", "-NonInteractive", "-File", "`"$ValidatorScript`"", "-Path", "`"$CredPath`"") `
                -RedirectStandardOutput $outFile -RedirectStandardError $errFile `
                -Wait -PassThru -NoNewWindow
        } catch {
            return @{ Ok = $false }
        }
        $exitCode = $proc.ExitCode

        if (-not [string]::IsNullOrEmpty($env:PARALLAX_KIMI_CREDENTIAL_VALIDATOR_CAPTURE_READ_FAULT)) {
            Remove-Item -LiteralPath $errFile -Force -ErrorAction SilentlyContinue
        }
        try {
            $stdoutText = Get-Content -LiteralPath $outFile -Raw -ErrorAction Stop
        } catch {
            return @{ Ok = $false }
        }
        try {
            $stderrText = Get-Content -LiteralPath $errFile -Raw -ErrorAction Stop
        } catch {
            return @{ Ok = $false }
        }
        if ($null -eq $stdoutText) { $stdoutText = "" }
        if ($null -eq $stderrText) { $stderrText = "" }

        if ($exitCode -ne 0) { return @{ Ok = $false } }
        if ($stderrText -ne "") { return @{ Ok = $false } }

        # Acceptance is ONE NONEMPTY LINE, optionally followed by exactly
        # one LF or CRLF - not "discard blank lines, then require one
        # survivor", which let "\n\n{json}\n\n" pass as a single line.
        # \A and \z, not ^ and $: $ matches before a single trailing
        # newline even without multiline mode, which would silently
        # accept a second trailing blank line here.
        if ($stdoutText -notmatch '\A(?<singleLine>[^\r\n]+)(\r\n|\n)?\z') {
            return @{ Ok = $false }
        }
        $singleLine = $Matches['singleLine']

        $parsed = $null
        try {
            $parsed = $singleLine | ConvertFrom-Json -ErrorAction Stop
        } catch {
            return @{ Ok = $false }
        }
        if (($null -eq $parsed) -or -not ($parsed -is [System.Management.Automation.PSCustomObject])) {
            return @{ Ok = $false }
        }
        $propNames = @($parsed.PSObject.Properties.Name | Sort-Object)
        $expectedNames = @("detail", "fields", "status")
        if (($propNames -join ",") -cne ($expectedNames -join ",")) { return @{ Ok = $false } }
        if (-not ($parsed.status -is [string])) { return @{ Ok = $false } }
        if (-not ($parsed.detail -is [string])) { return @{ Ok = $false } }
        # @(...) wraps a bare SCALAR into a one-element array, so a bare
        # string "fields" value would otherwise pass an "array of
        # strings" check. The array-ness of the value itself must be
        # checked BEFORE iterating its (possibly synthesized) elements.
        if (-not ($parsed.fields -is [System.Array])) { return @{ Ok = $false } }
        foreach ($f in $parsed.fields) {
            if (-not ($f -is [string])) { return @{ Ok = $false } }
        }
        if (-not (Test-ValidVerdictPair $parsed.status $parsed.detail)) { return @{ Ok = $false } }

        return @{ Ok = $true; Status = $parsed.status }
    } finally {
        Remove-Item -LiteralPath $outFile -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $errFile -Force -ErrorAction SilentlyContinue
    }
}

# =======================================================================
# Step 1 (both modes): validate the shared identity parameters. Every
# check here runs before any filesystem mutation or lock call, so a
# refused value mutates nothing.
# =======================================================================
if ([string]::IsNullOrWhiteSpace($LaneHome)) {
    Write-Stderr "refusing: -LaneHome is required"
    exit 2
}
if (-not ($DebateId -cmatch $TokenPattern)) {
    Write-Stderr "refusing: -DebateId must be exactly 32 lowercase hex characters"
    exit 2
}
if (-not (Test-NonNegativeIntString $OwnerPid)) {
    Write-Stderr "refusing: -OwnerPid must be a non-negative integer string"
    exit 2
}
if (-not ($OwnerStartTicksUtc -match $DigitsPattern)) {
    Write-Stderr "refusing: -OwnerStartTicksUtc must be a non-negative integer string"
    exit 2
}
if ($Remove) {
    if (-not ($Nonce -cmatch $TokenPattern)) {
        Write-Stderr "refusing: -Nonce must be exactly 32 lowercase hex characters"
        exit 2
    }
}

# The resolved -Path, computed once and reused everywhere it is needed:
# as the lock's -DebateHome (before the target exists, so GetFullPath,
# never Resolve-Path, which requires existence), and as the git-work-tree
# check's starting point below.
$fullPath = [System.IO.Path]::GetFullPath($Path)

if ($Remove) {
    # -----------------------------------------------------------------
    # Remove order, frozen. Identity check BEFORE deletion.
    # 1. Verify the caller's complete identity by an idempotent
    #    -Acquire -Nonce, with -DebateHome set to the same resolved
    #    -Path build used - which is what makes a wrong -Path exit 2 at
    #    the lock (the four-part identity matches, but -DebateHome does
    #    not match the held record's own debateHome). A mismatch exits
    #    nonzero and leaves BOTH the home and the lock byte-identical:
    #    this call is read-only when the identity already matches the
    #    held record (no Write-RecordJson on that path in the lock).
    # -----------------------------------------------------------------
    $identityCheck = Invoke-LockCall -LockArgs @{
        Acquire = $true; LaneHome = $LaneHome; DebateId = $DebateId
        OwnerPid = $OwnerPid; OwnerStartTicksUtc = $OwnerStartTicksUtc
        DebateHome = $fullPath; Nonce = $Nonce
    }
    if ($identityCheck.ExitCode -ne 0) {
        exit $identityCheck.ExitCode
    }

    # -----------------------------------------------------------------
    # 2. The existing sentinel and dangerous-root guards, UNCHANGED. If
    # any refuses (throw, implicit exit 1), no deletion occurs and the
    # pre-existing held lock REMAINS HELD - nothing below runs, and the
    # identity check above never wrote to the lock file.
    # -----------------------------------------------------------------
    if (-not (Test-Path -LiteralPath $Path)) {
        throw "sentinel does not match this path: $Path does not exist"
    }
    $resolved = (Resolve-Path -LiteralPath $Path).Path
    $sentinelPath = Join-Path $resolved $SentinelName
    if (-not (Test-Path -LiteralPath $sentinelPath)) {
        throw "sentinel does not match this path: no $SentinelName under $resolved"
    }
    $sentinelLines = @(Get-Content -LiteralPath $sentinelPath)
    if ($sentinelLines.Count -lt 2 -or
        $sentinelLines[0] -ne $SentinelMagic -or
        $sentinelLines[1] -ne $resolved) {
        throw "sentinel does not match this path: $sentinelPath does not authorize $resolved"
    }

    $pathRoot = [System.IO.Path]::GetPathRoot($resolved)
    $normalizedResolved = $resolved.TrimEnd('\', '/')
    $normalizedRoot = $pathRoot.TrimEnd('\', '/')
    $isDriveRoot = [System.IO.Path]::IsPathRooted($resolved) -and
                   ($normalizedResolved -ieq $normalizedRoot)
    if ($isDriveRoot) {
        throw "refusing to remove: $resolved is a drive root"
    }

    if (-not $env:USERPROFILE) {
        throw "refusing to remove: could not evaluate the user-profile guard (USERPROFILE is not set)"
    }
    if (-not (Test-Path -LiteralPath $env:USERPROFILE)) {
        throw "refusing to remove: could not evaluate the user-profile guard (USERPROFILE path does not exist: $env:USERPROFILE)"
    }
    $resolvedProfile = (Resolve-Path -LiteralPath $env:USERPROFILE).Path
    $normalizedProfile = $resolvedProfile.TrimEnd('\', '/')
    $sep = [System.IO.Path]::DirectorySeparatorChar
    $isProfileOrAbove = ($normalizedProfile -ieq $normalizedResolved) -or
        $normalizedProfile.StartsWith($normalizedResolved + $sep,
            [System.StringComparison]::OrdinalIgnoreCase)
    if ($isProfileOrAbove) {
        throw "refusing to remove: $resolved is the user profile or above it"
    }

    if (Test-Path -LiteralPath (Join-Path $resolved ".git")) {
        throw "refusing to remove: $resolved contains a .git entry"
    }

    # -----------------------------------------------------------------
    # 3. Delete the home - TERMINATING, unlike the non-terminating
    # Remove-Item this tool relied on before, which let a failed
    # deletion print "removed <path>" and exit 0.
    # -----------------------------------------------------------------
    try {
        Remove-Item -LiteralPath $resolved -Recurse -Force -ErrorAction Stop
    } catch {
        Write-Stderr "removal failed: $resolved could not be deleted ($($_.Exception.Message))"
        exit 6
    }

    # Seam: PARALLAX_LANE_HOME_REMOVE_VERIFY_FAULT. Remove mode only, any
    # nonempty value, fires AFTER deletion and BEFORE verification,
    # simulating a verification that could not be made. Every failing
    # verification outcome is PRIMARY: no "removed" line, NO release, the
    # held record left byte-identical.
    if ($env:PARALLAX_LANE_HOME_REMOVE_VERIFY_FAULT) {
        Write-Stderr "PARALLAX_LANE_HOME_REMOVE_VERIFY_FAULT injected: simulated post-delete verification failure"
        exit 6
    }

    # Verification has THREE outcomes: absent (proceed), still present
    # (failure), and UNMEASURABLE (also failure - reading an unmeasurable
    # check as absence would release the lock and print success on a
    # measurement never taken).
    $stillExists = $null
    try {
        $stillExists = Test-Path -LiteralPath $resolved
    } catch {
        Write-Stderr "removal failed: could not verify $resolved is absent ($($_.Exception.Message))"
        exit 6
    }
    if ($stillExists) {
        Write-Stderr "removal failed: $resolved still exists after deletion"
        exit 6
    }

    # Seam: PARALLAX_LANE_HOME_REMOVE_RELEASE_FAULT. Remove mode only, any
    # nonempty value, fires immediately after a successfully-verified
    # deletion and immediately before the release. When set it SKIPS the
    # lock mutation entirely (a simulated release result of code 5,
    # leaving the record still HELD) rather than calling the lock tool.
    if ($env:PARALLAX_LANE_HOME_REMOVE_RELEASE_FAULT) {
        Write-Stderr "PARALLAX_LANE_HOME_REMOVE_RELEASE_FAULT injected: simulated post-delete release refusal"
        exit 5
    }

    # -----------------------------------------------------------------
    # 4. Release. Remove's own failure precedence: a release that fails
    # AFTER deletion succeeded is reported as the failure and exits with
    # the lock tool's own code; "removed <path>" is printed only when
    # BOTH the deletion and the release succeeded.
    # -----------------------------------------------------------------
    $releaseResult = Invoke-LockCall -LockArgs @{
        Release = $true; LaneHome = $LaneHome; DebateId = $DebateId
        OwnerPid = $OwnerPid; OwnerStartTicksUtc = $OwnerStartTicksUtc; Nonce = $Nonce
    }
    if ($releaseResult.ExitCode -ne 0) {
        exit $releaseResult.ExitCode
    }

    Write-Output "removed $resolved"
    exit 0
}

# =======================================================================
# --- Build mode ---
# =======================================================================

# -----------------------------------------------------------------------
# FIRST USE: one bounded, read-only, fail-closed pre-lock probe of the
# LANE HOME directory - not -Path. Before anything else, because
# tools/new-kimi-lane-login.ps1 is the only thing that creates the lane
# home, and it creates it BEFORE acquiring; this builder acquires first
# and the lock tool creates only the lock FILE, giving no rule for
# creating its absent parent DIRECTORY. Without this probe, a user's
# very first debate would fail inside Acquire with a lock error instead
# of the login recovery command.
#
# FOUR reachable outcomes, not two. Only a successfully measured
# NONEXISTENT path emits the recovery command; a non-directory object and
# an unmeasurable path both refuse with NO recovery command (a command
# that cannot fix the obstruction is worse than none). All three refusal
# rows create nothing and never invoke the lock tool; the DIRECTORY row
# alone proceeds to Acquire, normal order below.
# -----------------------------------------------------------------------
if ($env:PARALLAX_LANE_HOME_DIRECTORY_PROBE_FAULT) {
    Write-Stderr "PARALLAX_LANE_HOME_DIRECTORY_PROBE_FAULT injected: simulated lane-home directory probe failure"
    exit 6
}

$resolvedLaneHome = [System.IO.Path]::GetFullPath($LaneHome)
$laneHomeProbe = $null
try {
    if (Test-Path -LiteralPath $resolvedLaneHome) {
        $laneHomeItem = Get-Item -LiteralPath $resolvedLaneHome -Force
        if ($laneHomeItem.PSIsContainer) { $laneHomeProbe = "directory" }
        else { $laneHomeProbe = "nondirectory" }
    } else {
        $laneHomeProbe = "nonexistent"
    }
} catch {
    $laneHomeProbe = "unmeasurable"
}

switch ($laneHomeProbe) {
    "nonexistent" {
        $recoveryCommand = Get-LaneLoginRecoveryCommand $resolvedLaneHome
        Write-Stderr "the lane is UNAVAILABLE: no lane home at $resolvedLaneHome; run this to create it:"
        Write-Stderr $recoveryCommand
        exit 6
    }
    "nondirectory" {
        Write-Stderr "refusing to build: $resolvedLaneHome exists and is not a directory"
        exit 6
    }
    "unmeasurable" {
        Write-Stderr "refusing to build: could not determine whether $resolvedLaneHome exists and is a directory"
        exit 6
    }
    default {
        # "directory" - proceed to Acquire below. No other value reaches here.
    }
}

$lockAcquired = $false
$buildCompleted = $false
$createdByThisInvocation = $false
$cleanupRoot = $null
$nonce = $null

try {
    # -------------------------------------------------------------------
    # Build order, frozen, once the lane home exists.
    # 2. ACQUIRE, with -DebateHome set to the resolved -Path. Lock FIRST,
    # because a login can otherwise mutate the shared credential between
    # validation and acquisition.
    # -------------------------------------------------------------------
    $acquireResult = Invoke-LockCall -LockArgs @{
        Acquire = $true; LaneHome = $resolvedLaneHome; DebateId = $DebateId
        OwnerPid = $OwnerPid; OwnerStartTicksUtc = $OwnerStartTicksUtc
        DebateHome = $fullPath
    }
    if ($acquireResult.ExitCode -ne 0) {
        # $lockAcquired stays false: an acquire failure never attempts a
        # release. The finally below still runs (exit does not bypass
        # finally) but its own guard skips the release for exactly this
        # reason.
        exit $acquireResult.ExitCode
    }
    $lockAcquired = $true
    $nonce = $acquireResult.Stdout.Trim()

    # -------------------------------------------------------------------
    # 3. Validate the lane credential via tools/read-kimi-credential-
    # state.ps1, resolved through $PSScriptRoot, accepted only under the
    # four-part rule above. A VALIDATOR FAILURE is not one of the three
    # actionable states: nothing was measured, so nothing can be
    # recommended - no login recovery command, no build work after this
    # point, and the acquired lock is released (via the finally below,
    # since $buildCompleted is never set).
    # -------------------------------------------------------------------
    $laneCredentialFile = Join-Path $resolvedLaneHome "credentials\kimi-code.json"
    $credentialVerdict = Invoke-CredentialValidator $laneCredentialFile
    if (-not $credentialVerdict.Ok) {
        Write-Stderr "credential validator failed"
        exit 6
    }
    if ($credentialVerdict.Status -cne "ok") {
        $recoveryCommand = Get-LaneLoginRecoveryCommand $resolvedLaneHome
        Write-Stderr "the lane credential is unusable (status: $($credentialVerdict.Status)); run this to fix it:"
        Write-Stderr $recoveryCommand
        exit 6
    }

    # -------------------------------------------------------------------
    # 4. Every existing gate, unchanged - only its POSITION moved, from
    # before any lock/credential interaction to after it.
    # -------------------------------------------------------------------

    # Refuse an existing destination: reuse carries stale sessions, which
    # corrupts the freshness the evidence rules depend on.
    if (Test-Path -LiteralPath $Path) {
        throw "refusing to build: destination already exists: $Path"
    }

    # Refuse a -Model or -Effort that cannot be safely rendered into
    # config.toml. This runs before DESTINATION CREATION OR RENDERING, so
    # a hostile value is rejected before any of those side effects, not
    # merely before the render itself.
    #
    # It does NOT run before anything touches the filesystem, which is
    # what this comment used to claim: the lock is already acquired above
    # and the lane credential is already validated. A refusal here unwinds
    # to the finally and releases, but it never reaches the recursive
    # cleanup, because $createdByThisInvocation is still false.
    if (-not (Test-SafeConfigToken $Model)) {
        throw "refusing to build: -Model contains characters outside the allowed set (letters, digits, dot, dash, underscore, slash)"
    }
    if (-not (Test-SafeConfigToken $Effort)) {
        throw "refusing to build: -Effort contains characters outside the allowed set (letters, digits, dot, dash, underscore, slash)"
    }

    # Resolve whether the PARENT is inside a git work tree (the target
    # itself does not exist yet). Fail closed: an unmade or unreadable
    # measurement is never a clean one, and the consequence here is an
    # OAuth credential landing inside a repository.
    #
    # No directory is created for this check. Git's own work-tree
    # detection walks up from a directory looking for a `.git` entry in
    # itself or an ancestor; a not-yet-created directory cannot itself
    # carry one, so querying the NEAREST EXISTING ancestor gives the
    # exact same answer the real parent would give once it exists, with
    # no directory created before every refusal gate below has passed.
    $parent = Split-Path -Path $fullPath -Parent
    $gitCheckDir = $parent
    while ($gitCheckDir -and -not (Test-Path -LiteralPath $gitCheckDir)) {
        $next = Split-Path -Path $gitCheckDir -Parent
        if (-not $next -or $next -eq $gitCheckDir) { break }
        $gitCheckDir = $next
    }
    if (-not $gitCheckDir -or -not (Test-Path -LiteralPath $gitCheckDir)) {
        throw "could not determine whether $parent is inside a git work tree (no existing ancestor directory found)"
    }

    # Windows PowerShell 5.1 turns ANY native-command stderr line into a
    # terminating NativeCommandError under $ErrorActionPreference =
    # "Stop", even when that stderr is being captured rather than
    # displayed - so the preference is relaxed for just this call and
    # restored immediately after, and a git invocation that cannot even
    # be found is caught explicitly so both failure directions land on
    # our own message, never a bypass.
    $previousEap = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    $previousLcAll = $env:LC_ALL
    # Pin git's message language for this call. The "not a git
    # repository" match a few lines down depends on that exact English
    # text; a localized git under a non-English LC_ALL/LANG would
    # translate it, and the unrecognized string would then fail the
    # match - which still fails CLOSED (the catch-all below refuses on
    # anything unrecognized), but pinning the locale here means the
    # common case is decided correctly rather than by falling through to
    # the conservative refusal every time.
    $env:LC_ALL = "C"
    try {
        $gitOutput = & git -C $gitCheckDir rev-parse --is-inside-work-tree 2>&1
        $gitExit = $LASTEXITCODE
    } catch {
        $env:LC_ALL = $previousLcAll
        $ErrorActionPreference = $previousEap
        throw "could not determine whether $parent is inside a git work tree (git invocation failed: $($_.Exception.Message))"
    }
    $env:LC_ALL = $previousLcAll
    $ErrorActionPreference = $previousEap
    $gitAnswer = ("$gitOutput").Trim()
    if ($gitExit -eq 0 -and $gitAnswer -eq "true") {
        throw "refusing to build: $parent is inside a git work tree"
    }
    # Measured (git 2.54.0.windows.1, both hosts): a plain directory with
    # no repository anywhere in its ancestry does NOT exit 0 with
    # "false" - it exits 128 with a "fatal: not a git repository" line,
    # every time, for every such directory tried. A strict
    # "$LASTEXITCODE -ne 0 always refuses" reading therefore refuses in
    # the overwhelmingly ordinary case this script exists to allow, and
    # Build mode could never succeed anywhere. Git's own "fatal: not a
    # git repository" text (LC_ALL=C above) is the positive, well-known
    # signal for that state, so it is treated the same as an explicit
    # "false". Every OTHER nonzero exit - a real git error, a corrupted
    # repository, git missing from PATH - still fails closed below.
    $definitelyNoRepositoryAnywhere = ($gitExit -ne 0) -and
        ($gitAnswer -match "fatal: not a git repository")
    $explicitlyOutsideTheWorkTree = ($gitExit -eq 0) -and ($gitAnswer -eq "false")
    if (-not ($explicitlyOutsideTheWorkTree -or $definitelyNoRepositoryAnywhere)) {
        throw "could not determine whether $parent is inside a git work tree (git rev-parse exited $gitExit, output: $gitAnswer)"
    }

    # Carry the model table for -Model out of the user's REAL config,
    # rather than hand-writing an approximation of it here.
    #
    # WHY, measured: a hand-written table that named only provider/model/
    # max_context_size/default_effort silently disabled two things this
    # lane's evidence contract depends on. With no `capabilities` array
    # the client declares no `thinking` capability, so the session log
    # reads thinkingEffort=off while config.toml says "high"; and with no
    # `support_efforts` array the pinned effort has nothing to resolve
    # against. With no `image_in` capability the ReadMediaFile tool is
    # gated out of the schema sent to the model, so a five-tool allowlist
    # arrives as toolCount=4. A faithful copy of the real table cannot
    # drift that way; a hand-written one drifts every time a field is
    # added.
    #
    # FAIL CLOSED on every direction: a missing, unreadable, or
    # unparseable real config, or one carrying no table for this -Model,
    # refuses the build. NOTHING outside that one table is carried: the
    # scan below stops at the next table header, so no hooks entry, no
    # other model, and no services block can follow the fields in.
    $realConfigPath = Join-Path $env:USERPROFILE ".kimi-code\config.toml"
    if (-not (Test-Path -LiteralPath $realConfigPath)) {
        throw "refusing to build: no kimi-code config at $realConfigPath, so the model table for $Model cannot be read"
    }
    try {
        $realConfigLines = @(Get-Content -LiteralPath $realConfigPath)
    } catch {
        throw "refusing to build: could not read $realConfigPath ($($_.Exception.Message))"
    }

    # A field line the render can carry: a bare key, then a quoted
    # string, an integer, a boolean, or a single-line array of quoted
    # strings. Every character class here is ASCII. Anything else in the
    # table is UNPARSEABLE to this reader, and unparseable refuses.
    $FieldLinePattern = '\A[A-Za-z0-9_-]+ = (?:"[A-Za-z0-9 ._/:+-]*"|-?[0-9]+|true|false|\[ *(?:"[A-Za-z0-9 ._/:+-]*" *, *)*(?:"[A-Za-z0-9 ._/:+-]*" *)?\])\z'
    $wantedHeader = '[models."' + $Model + '"]'
    $modelTableFieldLines = New-Object System.Collections.Generic.List[string]
    $insideWantedTable = $false
    $foundWantedTable = $false
    foreach ($rawLine in $realConfigLines) {
        $line = ("$rawLine").Trim()
        if ($line.StartsWith("[")) {
            if ($line -eq $wantedHeader) {
                if ($foundWantedTable) {
                    throw "refusing to build: $realConfigPath declares the model table for $Model more than once"
                }
                $insideWantedTable = $true
                $foundWantedTable = $true
            } else {
                $insideWantedTable = $false
            }
            continue
        }
        if (-not $insideWantedTable) { continue }
        if ($line -eq "" -or $line.StartsWith("#")) { continue }
        if (-not ($line -match $FieldLinePattern)) {
            throw "refusing to build: unparseable line in the $Model model table of ${realConfigPath}: $line"
        }
        # default_effort is deliberately NOT carried: -Effort is the
        # pinned per-debate value and must win over the real config's.
        if ($line -match '\Adefault_effort *=') { continue }
        $modelTableFieldLines.Add($line)
    }
    if (-not $foundWantedTable) {
        throw "refusing to build: $realConfigPath declares no model table for $Model"
    }
    if ($modelTableFieldLines.Count -eq 0) {
        throw "refusing to build: the model table for $Model in $realConfigPath carries no usable fields"
    }

    # A non-empty table is not the same as a DISPATCHABLE one: a table
    # carrying only display_name renders a model with no provider and no
    # model name, and a table naming a provider this file does not
    # declare renders a dangling reference. Both build cleanly and then
    # fail mid-debate as a confusing client error.
    $RenderedProviders = @("managed:kimi-code")
    $hasProviderKey = $false
    $hasModelKey = $false
    $carriedProvider = $null
    foreach ($fieldLine in $modelTableFieldLines) {
        if ($fieldLine -match '\Aprovider = ') {
            $hasProviderKey = $true
            if ($fieldLine -match '\Aprovider = "([^"]*)"\z') {
                $carriedProvider = $matches[1]
            }
        } elseif ($fieldLine -match '\Amodel = ') {
            $hasModelKey = $true
        }
    }
    if (-not $hasProviderKey) {
        throw "refusing to build: the model table for $Model in $realConfigPath carries no provider key, so the rendered home would name no provider to dispatch through"
    }
    if (-not $hasModelKey) {
        throw "refusing to build: the model table for $Model in $realConfigPath carries no model key, so the rendered home would name no provider-side model to dispatch to"
    }
    if ($RenderedProviders -notcontains $carriedProvider) {
        throw "refusing to build: the model table for $Model in $realConfigPath names provider '$carriedProvider', which this home does not declare (it declares only: $($RenderedProviders -join ', '))"
    }

    $modelTableFields = ($modelTableFieldLines -join [System.Environment]::NewLine)

    # -------------------------------------------------------------------
    # 5. Create, junction, render. $createdByThisInvocation is set ONLY
    # after this invocation has created the directory and written the
    # sentinel, so a refusal path above can never delete a directory the
    # script declined to touch, and the catch below can never delete a
    # directory some OTHER invocation created.
    # -------------------------------------------------------------------
    # This is the ONLY directory-creation in Build mode, and everything
    # above it is read-only (besides the lock's own file). New-Item
    # -Force creates the WHOLE missing ancestor chain silently when
    # $Path is nested under directories that do not exist yet, not just
    # the leaf - so the chain New-Item is ABOUT TO create is recorded
    # BEFORE it runs, by walking up from $Path to the nearest directory
    # that already exists. The SHALLOWEST missing directory is what
    # cleanup actually removes: everything New-Item creates lands inside
    # it, so removing it recursively removes exactly what this
    # invocation created and nothing that existed beforehand.
    $missingChain = New-Object System.Collections.Generic.List[string]
    $walk = $fullPath
    while ($walk -and -not (Test-Path -LiteralPath $walk)) {
        $missingChain.Insert(0, $walk)
        $nextUp = Split-Path -Path $walk -Parent
        if (-not $nextUp -or $nextUp -eq $walk) { break }
        $walk = $nextUp
    }
    $cleanupRoot = $missingChain[0]

    New-Item -ItemType Directory -Force -Path $Path | Out-Null
    $resolved = (Resolve-Path -LiteralPath $Path).Path

    # Sentinel first, then $createdByThisInvocation, then the ACL -
    # BEFORE the junction is created.
    $sentinelPath = Join-Path $resolved $SentinelName
    Set-Content -LiteralPath $sentinelPath -Value @($SentinelMagic, $resolved) -Encoding ascii
    $createdByThisInvocation = $true

    $acl = Get-Acl -LiteralPath $resolved
    $acl.SetAccessRuleProtection($true, $false)
    foreach ($existingRule in @($acl.Access)) {
        $acl.RemoveAccessRule($existingRule) | Out-Null
    }
    $currentIdentity = [System.Security.Principal.WindowsIdentity]::GetCurrent().User
    $fullControlRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        $currentIdentity, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
    $acl.AddAccessRule($fullControlRule)
    Set-Acl -LiteralPath $resolved -AclObject $acl

    # JUNCTION, not a copy: `credentials` under this debate home is a
    # directory junction to the lane home's own `credentials`, so a
    # token refresh writes through to the single file on disk instead of
    # forking a copy that strands a stale refresh token when the server
    # rotates both tokens. No admin rights required (measured). The lane
    # credential was already validated `ok` above, at
    # <lane-home>\credentials\kimi-code.json, so that directory exists.
    # This template, rendered below, carries no hooks by construction -
    # unlike the user's real ~/.kimi-code/config.toml.
    $credentialDir = Join-Path $resolved "credentials"
    $laneCredentialDir = Join-Path $resolvedLaneHome "credentials"
    New-Item -ItemType Junction -Path $credentialDir -Target $laneCredentialDir | Out-Null

    # `provider`, `model`, `max_context_size`, `capabilities`,
    # `support_efforts` and `display_name` all arrive in
    # $modelTableFields, read from the real config above.
    #
    # Root-level keys MUST appear BEFORE any table header: a TOML table
    # header claims every key-value pair that follows it, up to the NEXT
    # header - a blank line does not end a table. default_effort is the
    # one key that belongs inside the model table, and stays there.
    $configToml = @"
default_model = "$Model"
extra_skill_dirs = []
telemetry = false

[providers."managed:kimi-code"]
type = "kimi"
api_key = ""
base_url = "https://api.kimi.com/coding/v1"

[providers."managed:kimi-code".oauth]
storage = "file"
key = "oauth/kimi-code"

[models."$Model"]
$modelTableFields
default_effort = "$Effort"

[thinking]
enabled = true
"@
    # ASCII, not utf8: Windows PowerShell 5.1's -Encoding utf8 prepends a
    # byte-order mark, which kimi-code's TOML parser rejects outright.
    # Measured live. ASCII is sound here - $Model and $Effort were both
    # checked against $SafeTokenPattern above before being interpolated
    # into it, and $modelTableFields reaches this render from a FILE
    # matched against $FieldLinePattern above, whose character classes
    # are ASCII-only and admit no line break and no table header.
    Set-Content -LiteralPath (Join-Path $resolved "config.toml") -Value $configToml -Encoding ascii

    New-Item -ItemType Directory -Path (Join-Path $resolved "skills") | Out-Null

    # POSTCONDITION on the builder's OWN act. NOT a control against unknown
    # writers, and the lane contract says exactly that.
    #
    # The reopened home-skills-root debate (2026-08-03) established that the
    # New-Item above is the ONLY site in this repository that writes here, so
    # there is no shipped writer to defend against and no per-round check is
    # warranted - a check nothing can fail is indistinguishable from a broken
    # one on every run forever. What this DOES catch is a future edit to THIS
    # script that seeds content, a copy that starts following a junction, or a
    # refactor that reorders creation: the one moment content can legitimately
    # enter.
    #
    # -Force, because a hidden intruder is still an intruder and a check blind
    # to it passes the obvious case and fails the real one. TERMINATING,
    # because an enumeration that failed is not an empty directory - an unmade
    # measurement is never a clean one. Both are watched by their own tests.
    $skillsDir = Join-Path $resolved "skills"
    if ($env:PARALLAX_SKILLS_SEED_FILE) {
        Set-Content -LiteralPath (Join-Path $skillsDir "seeded.txt") `
            -Value "PARALLAX_SKILLS_SEED_FILE injected" -Encoding ascii
    }
    if ($env:PARALLAX_SKILLS_SEED_HIDDEN) {
        $hidden = Join-Path $skillsDir "hidden.txt"
        Set-Content -LiteralPath $hidden -Value "hidden" -Encoding ascii
        (Get-Item -LiteralPath $hidden -Force).Attributes = `
            [System.IO.FileAttributes]::Hidden
    }
    # THROW, not a bare stderr write and exit. This sits inside the guarded
    # try above, so throwing is what runs the cleanup that deletes the home
    # and the finally that releases the lock. A refusal that left either
    # behind would hand the caller an unreleasable lane.
    $seeded = @()
    try {
        $seeded = @(Get-ChildItem -LiteralPath $skillsDir -Force -ErrorAction Stop)
    } catch {
        throw ("skills directory could not be enumerated after creation: " +
               $_.Exception.Message)
    }
    if ($seeded.Count -ne 0) {
        throw ("skills directory is not empty after creation: " +
               $seeded.Count + " entry(ies)")
    }

    # -------------------------------------------------------------------
    # 6. Construct AND EMIT the custody JSON line. JSON construction and
    # emission stay INSIDE this guarded try.
    # -------------------------------------------------------------------
    $custody = [ordered]@{ debateHome = $resolved; nonce = $nonce }
    $custodyJson = ConvertTo-Json $custody -Compress

    # Test seam for the live fault test: prove the catch below actually
    # runs and actually cleans up a home that already has a JUNCTION on
    # disk, by injecting a failure right before the custody line is
    # emitted - the boundary between "$buildCompleted set after
    # rendering" (which could not distinguish this from a correct
    # implementation) and "$buildCompleted set after emission" (which
    # can). MOVED here (was: immediately after the credential copy, now
    # deleted) and RENAMED: there is no credential copy any more.
    if ($env:PARALLAX_LANE_HOME_FAULT) {
        throw "PARALLAX_LANE_HOME_FAULT injected: simulated pre-emission failure"
    }

    Write-Output $custodyJson

    # -------------------------------------------------------------------
    # 7. Only now set $buildCompleted. Setting it any earlier means a
    # failure to construct or emit the custody line leaves the flag
    # true, the finally below skips the release, and the lock is
    # retained by a caller who never received the nonce it needs to
    # release it - an unreleasable lane.
    # -------------------------------------------------------------------
    $buildCompleted = $true
} catch {
    # Directory cleanup: only for a directory THIS invocation created and
    # marked, so a refusal path above that never touched the filesystem
    # never triggers a deletion.
    if ($createdByThisInvocation -and $cleanupRoot) {
        if ($env:PARALLAX_LANE_HOME_CLEANUP_DELETE_FAULT) {
            Write-Stderr "PARALLAX_LANE_HOME_CLEANUP_DELETE_FAULT injected: simulated cleanup deletion failure"
        } else {
            try {
                Remove-Item -LiteralPath $cleanupRoot -Recurse -Force -ErrorAction Stop
            } catch {
                # A cleanup error never masks the error that caused the
                # cleanup: report it on stderr only, then rethrow the
                # ORIGINAL failure below unchanged.
                Write-Stderr "cleanup deletion failed: $($_.Exception.Message)"
            }
        }
    }
    throw
} finally {
    # Cleanup needs TWO flags: -not $buildCompleted is also true when
    # Acquire itself failed, and releasing then would release a lock
    # this call never took.
    if ($lockAcquired -and -not $buildCompleted) {
        if ($env:PARALLAX_LANE_HOME_CLEANUP_RELEASE_FAULT) {
            Write-Stderr "PARALLAX_LANE_HOME_CLEANUP_RELEASE_FAULT injected: simulated cleanup release refusal"
        } else {
            $cleanupRelease = Invoke-LockCall -LockArgs @{
                Release = $true; LaneHome = $resolvedLaneHome; DebateId = $DebateId
                OwnerPid = $OwnerPid; OwnerStartTicksUtc = $OwnerStartTicksUtc; Nonce = $nonce
            }
            if ($cleanupRelease.ExitCode -ne 0) {
                # The ORIGINAL failure is what the script reports; a
                # cleanup error never masks it.
                Write-Stderr "cleanup release failed with exit $($cleanupRelease.ExitCode)"
            }
        }
    }
}

exit 0
