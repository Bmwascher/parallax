# new-kimi-lane-login.ps1 - the ONLY tool that creates the shared kimi-code
# lane home and performs a login into it (Task 5 of the 2026-08-01
# lane-credential-and-lock plan). It never touches the user's own
# ~/.kimi-code/credentials - it gives the lane its OWN login, at
# <lane-home>\credentials\kimi-code.json, produced by the client's own
# `login` subcommand with KIMI_CODE_HOME pointed at the lane home for the
# duration of that one call only.
#
# THE BOOTSTRAP EXCEPTION. The lock lives INSIDE the lane home, so it
# cannot guard the creation of that home. Exactly THREE operations happen
# before the lock is ever touched: the fail-closed lane-home PROBE, then
# creating the lane-home directory if the probe measured it nonexistent,
# then applying the ACL idempotently for the current identity. All three
# are safe to race - the probe only reads, the other two are idempotent
# and identity-scoped. Everything that reads or writes the CREDENTIAL
# happens under the lock.
#
# FOUR-ROW PROBES, not "create if absent otherwise apply". Both the
# lane-home probe (pre-lock) and the credentials probe (post-lock, on
# <lane-home>\credentials) have four rows: nonexistent (create + ACL),
# directory (ACL only), non-directory (exit 6, no mutation), and
# unmeasurable (exit 6, no mutation). Without the last two rows a REGULAR
# FILE sitting at either path would have its ACL REPLACED before this
# tool ever notices it does not own that object - a privileged write on
# something it never established it owned.
#
# STREAM MECHANISM. The client's stdout and stderr are INHERITED and
# UNTOUCHED - `& $KimiBinary "login"` with no redirection at all - so an
# interactive login renders normally. The machine-readable verdict goes
# only to -VerdictOut, never to stdout. The wrapper's own messages go to
# stderr.
#
# THE LOCK'S STREAMS, handled separately from the client's. The internal
# lock call is invoked IN-PROCESS (`& $LockScript`, not a separate
# process): its stdout (the nonce) is captured by assigning the call to a
# variable, and its stderr - written via [Console]::Error.WriteLine,
# which bypasses PowerShell's own `2>` stream redirection entirely and
# writes straight to the real OS stderr handle - passes through
# UNCHANGED and UNTOUCHED to this wrapper's own stderr as a structural
# side effect of in-process invocation, not by manual re-emission.
# Measured live on both hosts: a nested script's Console.Error write is
# visible on the caller's own stderr immediately, and $LASTEXITCODE
# reflects the nested script's `exit N` without terminating the caller.
#
# THE CREDENTIAL VALIDATOR, in contrast, is launched as a genuine
# SEPARATE PROCESS (Start-Process with independent
# -RedirectStandardOutput/-RedirectStandardError files), because its
# failure rule requires observing stdout and stderr INDEPENDENTLY - "the
# process launched, it exited 0, stderr was EMPTY, and stdout was exactly
# one parseable line" - and in-process invocation cannot separate a
# Console.Error write from the success stream the way this rule needs.
# It is resolved through $PSScriptRoot, so a copied `tools` directory
# resolves the sibling validator rather than the repository's own, and
# relaunched under whichever PowerShell host ((Get-Process -Id
# $PID).Path) is currently running this wrapper, so a pwsh-run wrapper
# never spawns a powershell.exe child or vice versa.
#
# Windows PowerShell 5.1 compatible, ASCII ONLY.
#
# Exit codes (scoped to SUCCESSFULLY BOUND invocations only, same
# convention as tools/kimi-lane-lock.ps1):
#   0  the post-run credential verdict is structurally `ok`
#   2  a parameter value was refused
#   3  lock contention: the exclusive handle, or a holder that is LIVE or
#      UNMEASURABLE, propagated unchanged from the lock tool
#   4  the lock is malformed or foreign-host, propagated from the lock
#      tool
#   5  a release refusal propagated from the lock tool - reachable
#      because the record can be freed or displaced between acquire and
#      the final release
#   6  an unusable lane-home or credentials object, an injected probe
#      fault, validator failure at either call, an invalid post-run
#      credential, a -VerdictOut write failure, or any unclassified
#      runtime failure
#   1  reserved for PowerShell's own parameter-binding refusal; never
#      emitted by script code
[CmdletBinding()]
param(
    [Parameter(Mandatory = $false)]
    [string]$LaneHome = (Join-Path $env:USERPROFILE ".parallax-kimi-review"),

    [Parameter(Mandatory = $true)]
    [string]$OwnerPid,

    [Parameter(Mandatory = $true)]
    [string]$OwnerStartTicksUtc,

    [Parameter(Mandatory = $false)]
    [string]$KimiBinary = (Join-Path $env:USERPROFILE ".kimi-code\bin\kimi.exe"),

    [Parameter(Mandatory = $true)]
    [string]$VerdictOut,

    [Parameter(Mandatory = $false)]
    [switch]$Force
)

$ErrorActionPreference = "Stop"

$DigitsPattern = '\A[0-9]+\z'
$LockScript = Join-Path $PSScriptRoot "kimi-lane-lock.ps1"
$ValidatorScript = Join-Path $PSScriptRoot "read-kimi-credential-state.ps1"

function Write-Stderr([string]$Line) {
    [Console]::Error.WriteLine($Line)
}

function Test-NonNegativeIntString([string]$Value) {
    return ($Value -match $DigitsPattern)
}
function ConvertTo-BoundedInt32([string]$Value) {
    try { return [int]::Parse($Value, [System.Globalization.CultureInfo]::InvariantCulture) }
    catch { return $null }
}

# ---------------------------------------------------------------------
# The shared four-row probe: nonexistent / directory / nondirectory /
# unmeasurable. Used for BOTH the lane home (pre-lock) and the
# credentials directory (post-lock). Read-only; never mutates.
# ---------------------------------------------------------------------
function Invoke-DirectoryProbe([string]$Path) {
    try {
        if (Test-Path -LiteralPath $Path) {
            $item = Get-Item -LiteralPath $Path -Force
            if ($item.PSIsContainer) { return "directory" }
            return "nondirectory"
        }
        return "nonexistent"
    } catch {
        return "unmeasurable"
    }
}

# ---------------------------------------------------------------------
# GetAccessControl/SetAccessControl by instance method on 5.1 (Desktop
# .NET), or the [System.IO.FileSystemAclExtensions] static class on 7
# (.NET Core removed the instance methods). Selected by reflection so the
# same script runs on both hosts.
# ---------------------------------------------------------------------
function Get-AclCompat($DirInfo) {
    $method = $DirInfo.GetType().GetMethod("GetAccessControl", [Type[]]@())
    if ($method) { return $DirInfo.GetAccessControl() }
    return [System.IO.FileSystemAclExtensions]::GetAccessControl($DirInfo)
}
function Set-AclCompat($DirInfo, $Acl) {
    $method = $DirInfo.GetType().GetMethod("SetAccessControl",
        [Type[]]@([System.Security.AccessControl.DirectorySecurity]))
    if ($method) { $DirInfo.SetAccessControl($Acl); return }
    [System.IO.FileSystemAclExtensions]::SetAccessControl($DirInfo, $Acl)
}

# ---------------------------------------------------------------------
# The exact ACE shape already used by tools/new-kimi-lane-home.ps1:399-408
# - protection enabled, every existing rule removed, one FullControl
# Allow rule for the current WindowsIdentity SID with
# ContainerInherit,ObjectInherit / None, so a file created later under a
# protected directory inherits it too. Applied idempotently to both the
# lane home and its credentials child - which is where this departs from
# that precedent's own Get-Acl/Set-Acl CMDLET usage. That builder never
# re-applies to an already-protected directory (it refuses a reused
# destination outright), so it never meets this: measured live on both
# hosts, calling the `Set-Acl` CMDLET a SECOND time against a directory
# this same protection was already applied to throws "The process does
# not possess the 'SeSecurityPrivilege' privilege which is required for
# this operation" - reproducible even from a brand-new in-memory
# DirectorySecurity object, so it is not about reading the prior state.
# GetAccessControl/SetAccessControl via the FileSystemInfo object (not
# the Get-Acl/Set-Acl cmdlets) persists only the sections actually
# touched and does not hit this. Measured live on .NET Core (7): an
# empty AuthorizationRuleCollection returned by the static extension
# method wraps to a ONE-ELEMENT array holding $null under `@()`, not an
# empty array, so the existing-rule enumeration is filtered for $null
# before removal, or RemoveAccessRule throws "Value cannot be null".
# ---------------------------------------------------------------------
function Set-ProtectedAcl([string]$ResolvedPath) {
    $dirInfo = New-Object System.IO.DirectoryInfo($ResolvedPath)
    $acl = Get-AclCompat $dirInfo
    $acl.SetAccessRuleProtection($true, $false)
    $existingRules = @($acl.Access) | Where-Object { $null -ne $_ }
    foreach ($existingRule in $existingRules) {
        $acl.RemoveAccessRule($existingRule) | Out-Null
    }
    $currentIdentity = [System.Security.Principal.WindowsIdentity]::GetCurrent().User
    $fullControlRule = New-Object System.Security.AccessControl.FileSystemAccessRule(
        $currentIdentity, "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow")
    $acl.AddAccessRule($fullControlRule)
    Set-AclCompat $dirInfo $acl
}

# ---------------------------------------------------------------------
# In-process invocation of the lock tool. Stdout is captured via the
# assignment itself; stderr (written by the lock via Console.Error, which
# bypasses PowerShell's own stream redirection) passes straight through
# to this wrapper's real stderr handle, untouched, as a structural
# consequence of running in the same process rather than by manual
# re-emission.
#
# A HASHTABLE splat, not an array. Measured live on both hosts: splatting
# an alternating "-Name","value" ARRAY against kimi-lane-lock.ps1 throws
# "Parameter set cannot be resolved using the specified named parameters"
# even for a trivial `-Status -LaneHome <path>` call, because that
# script's many overlapping parameter sets (five of its six share the
# mandatory -LaneHome) defeat the array-splat binder's set-disambiguation
# pass. A hashtable splat, where every key is an explicit parameter name,
# resolves correctly - reproduced as the fix on the same two hosts.
# ---------------------------------------------------------------------
function Invoke-LockCall([hashtable]$LockArgs) {
    $stdout = & $LockScript @LockArgs
    $exitCode = $LASTEXITCODE
    return @{ Stdout = (@($stdout) -join "`n"); ExitCode = $exitCode }
}

# ---------------------------------------------------------------------
# The credential validator's frozen status/detail table (Task 2's
# interface, read from the already-committed
# tools/read-kimi-credential-state.ps1 this task depends on and must not
# rewrite). A pairing outside this table is VALIDATOR FAILURE, never a
# credential state.
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
# FAILURE and is never read as a credential state.
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

        return @{ Ok = $true; Status = $parsed.status; Raw = $singleLine }
    } finally {
        Remove-Item -LiteralPath $outFile -Force -ErrorAction SilentlyContinue
        Remove-Item -LiteralPath $errFile -Force -ErrorAction SilentlyContinue
    }
}

# ---------------------------------------------------------------------
# Everything from the credentials probe through writing -VerdictOut.
# Runs under the held lock.
#
# Sets $script:MainCode as a SIDE EFFECT and is called as a BARE
# statement (never assigned) by its caller, rather than using `return`
# for its result. Measured live on both hosts: assigning a function
# call's result (`$x = Invoke-Foo`) captures EVERY unconsumed output
# statement inside that function into the assignment - including a
# nested native command's own stdout, even though nothing at the native
# call's own site redirects it. That silently broke the frozen stream
# contract: the interactive client's real-time output was captured into
# a variable instead of reaching the wrapper's real stdout handle. A
# bare (uncaptured) call restores genuine inheritance all the way down
# through this function to the client, while the result still reaches
# the caller through the script-scoped variable rather than the
# pipeline. The caller's single top-level `finally` still always
# releases the lock and applies the release-failure precedence rule
# against whatever this function decided, because `finally` runs
# regardless of how the function communicates its result.
# ---------------------------------------------------------------------
function Invoke-LoginBody {
    param(
        [string]$ResolvedLaneHome,
        [string]$CredentialsDir,
        [string]$CredentialFile,
        [string]$KimiBinaryPath,
        [bool]$ForceLogin
    )

    if (-not [string]::IsNullOrEmpty($env:PARALLAX_KIMI_LANE_LOGIN_CREDENTIALS_PROBE_FAULT)) {
        Write-Stderr "PARALLAX_KIMI_LANE_LOGIN_CREDENTIALS_PROBE_FAULT injected: simulated credentials probe failure"
        $script:MainCode = 6
        return
    }

    $credState = Invoke-DirectoryProbe $CredentialsDir
    switch ($credState) {
        "nonexistent" {
            try {
                New-Item -ItemType Directory -Path $CredentialsDir -Force | Out-Null
                $resolvedCredDir = (Resolve-Path -LiteralPath $CredentialsDir).Path
                Set-ProtectedAcl $resolvedCredDir
            } catch {
                Write-Stderr "credentials directory creation failed: $($_.Exception.Message)"
                $script:MainCode = 6
                return
            }
        }
        "directory" {
            try {
                $resolvedCredDir = (Resolve-Path -LiteralPath $CredentialsDir).Path
                Set-ProtectedAcl $resolvedCredDir
            } catch {
                Write-Stderr "credentials directory ACL application failed: $($_.Exception.Message)"
                $script:MainCode = 6
                return
            }
        }
        default {
            Write-Stderr "credentials probe found an unusable object: $CredentialsDir"
            $script:MainCode = 6
            return
        }
    }

    $pre = Invoke-CredentialValidator $CredentialFile
    if (-not $pre.Ok) {
        Write-Stderr "credential validator failed (pre-client)"
        $script:MainCode = 6
        return
    }

    if (-not ($pre.Status -ceq "ok" -and -not $ForceLogin)) {
        # Redirect the client at the LANE home for the duration of this
        # one call only, so its login writes
        # <lane-home>\credentials\kimi-code.json rather than falling back
        # to the user's own ~/.kimi-code. Restored unconditionally in a
        # `finally`, covering both the previously-set and
        # previously-unset cases, because KIMI_CODE_HOME is a PROCESS
        # environment variable, not a lexically scoped one - a caller
        # that dot-sources or otherwise shares this process would
        # otherwise see the lane home leak into its own environment.
        $previousSet = Test-Path Env:KIMI_CODE_HOME
        $previousValue = $env:KIMI_CODE_HOME
        try {
            $env:KIMI_CODE_HOME = $ResolvedLaneHome
            & $KimiBinaryPath "login"
        } finally {
            if ($previousSet) {
                $env:KIMI_CODE_HOME = $previousValue
            } else {
                Remove-Item Env:KIMI_CODE_HOME -ErrorAction SilentlyContinue
            }
        }
    }

    $post = Invoke-CredentialValidator $CredentialFile
    if (-not $post.Ok) {
        Write-Stderr "credential validator failed (post-client)"
        $script:MainCode = 6
        return
    }

    try {
        [System.IO.File]::WriteAllText($VerdictOut, ($post.Raw + "`n"), [System.Text.Encoding]::ASCII)
    } catch {
        Write-Stderr "failed to write -VerdictOut: $($_.Exception.Message)"
        $script:MainCode = 6
        return
    }

    # Success requires structural validity. The post-run verdict decides
    # the exit code, never the client's own exit code.
    if ($post.Status -ceq "ok") { $script:MainCode = 0 } else { $script:MainCode = 6 }
}

# =======================================================================
# 1. Parameter validation. Every check below runs before any filesystem
# mutation, so a refused value mutates nothing.
# =======================================================================
if ([string]::IsNullOrWhiteSpace($LaneHome)) { exit 2 }
if (-not (Test-NonNegativeIntString $OwnerPid)) { exit 2 }
$OwnerPidInt = ConvertTo-BoundedInt32 $OwnerPid
if ($null -eq $OwnerPidInt -or $OwnerPidInt -le 0) { exit 2 }
if (-not ($OwnerStartTicksUtc -match $DigitsPattern)) { exit 2 }
if ([string]::IsNullOrWhiteSpace($KimiBinary)) { exit 2 }
if ([string]::IsNullOrWhiteSpace($VerdictOut)) { exit 2 }

try {
    # ===================================================================
    # 2. Probe the lane home, four rows. Only a successfully measured
    # nonexistent path creates. A directory applies the ACL. A
    # non-directory object and an unmeasurable path each exit 6 with no
    # mutation, no lock invocation, no client invocation, no -VerdictOut
    # write. This is the ONLY pre-lock filesystem interaction besides the
    # probe itself, and it is safe to race: idempotent and
    # identity-scoped.
    # ===================================================================
    if (-not [string]::IsNullOrEmpty($env:PARALLAX_KIMI_LANE_LOGIN_HOME_PROBE_FAULT)) {
        Write-Stderr "PARALLAX_KIMI_LANE_LOGIN_HOME_PROBE_FAULT injected: simulated lane-home probe failure"
        exit 6
    }

    $homeState = Invoke-DirectoryProbe $LaneHome
    $resolvedLaneHome = $null
    switch ($homeState) {
        "nonexistent" {
            try {
                New-Item -ItemType Directory -Path $LaneHome -Force | Out-Null
                $resolvedLaneHome = (Resolve-Path -LiteralPath $LaneHome).Path
                Set-ProtectedAcl $resolvedLaneHome
            } catch {
                Write-Stderr "lane-home creation failed: $($_.Exception.Message)"
                exit 6
            }
        }
        "directory" {
            try {
                $resolvedLaneHome = (Resolve-Path -LiteralPath $LaneHome).Path
                Set-ProtectedAcl $resolvedLaneHome
            } catch {
                Write-Stderr "lane-home ACL application failed: $($_.Exception.Message)"
                exit 6
            }
        }
        default {
            Write-Stderr "lane-home probe found an unusable object: $LaneHome"
            exit 6
        }
    }

    # ===================================================================
    # 3. Generate a login debate id, 32 lowercase hex.
    # ===================================================================
    $LoginDebateId = [System.Guid]::NewGuid().ToString("N")

    # ===================================================================
    # 4. Acquire the lane lock, with -DebateHome set to the resolved
    # lane-home path itself (this login owns no separate debate home).
    # No lock is held yet on failure, so a direct exit here is safe.
    # ===================================================================
    $acquireResult = Invoke-LockCall -LockArgs @{
        Acquire = $true; LaneHome = $resolvedLaneHome; DebateId = $LoginDebateId
        OwnerPid = $OwnerPid; OwnerStartTicksUtc = $OwnerStartTicksUtc
        DebateHome = $resolvedLaneHome
    }
    if ($acquireResult.ExitCode -ne 0) {
        exit $acquireResult.ExitCode
    }
    $nonce = $acquireResult.Stdout.Trim()

    # ===================================================================
    # 4b-9. Everything that reads or writes the credential happens under
    # the held lock, and the lock is ALWAYS released in this `finally` -
    # reached whether Invoke-LoginBody returns normally or an unexpected
    # exception unwinds through it, per the measured fact that `exit`
    # bypasses an enclosing `catch` but NOT an enclosing `finally`.
    # ===================================================================
    $script:MainCode = 6
    try {
        $CredentialsDir = Join-Path $resolvedLaneHome "credentials"
        $CredentialFile = Join-Path $CredentialsDir "kimi-code.json"
        # Called BARE - never assigned - so the client's own real-time
        # stdout/stderr, invoked deep inside this call, is never captured
        # into a variable. See Invoke-LoginBody's own header.
        Invoke-LoginBody -ResolvedLaneHome $resolvedLaneHome `
            -CredentialsDir $CredentialsDir -CredentialFile $CredentialFile `
            -KimiBinaryPath $KimiBinary -ForceLogin $Force.IsPresent
    } finally {
        $releaseResult = Invoke-LockCall -LockArgs @{
            Release = $true; LaneHome = $resolvedLaneHome; DebateId = $LoginDebateId
            OwnerPid = $OwnerPid; OwnerStartTicksUtc = $OwnerStartTicksUtc
            Nonce = $nonce
        }
        if ($releaseResult.ExitCode -ne 0) {
            # Release-failure precedence: if the main operation already
            # failed, preserve that original code (the release failure's
            # own diagnostic already reached stderr unchanged, via the
            # in-process passthrough above). If the main operation
            # SUCCEEDED, the release failure becomes the result.
            if ($script:MainCode -eq 0) {
                $script:MainCode = $releaseResult.ExitCode
            }
        }
    }
    exit $script:MainCode
} catch {
    # Any unclassified runtime failure not already mapped to a specific
    # exit code above. An unmade or failed measurement is never a clean
    # one.
    Write-Stderr "lane login wrapper failed: $($_.Exception.Message)"
    exit 6
}
