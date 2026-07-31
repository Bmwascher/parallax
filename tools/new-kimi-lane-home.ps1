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
# Two parameter sets, because a GLOBALLY mandatory -Model would make the
# removal form uncallable:
#   Build (default):  -Path <dir> -Model <id> [-Effort <level>]
#   Remove:            -Path <dir> -Remove
# -Model has NO default. The canonical backup model id is single-sourced
# in skills/multi-model-verify/references/model-prompting-notes.md and
# forbidden as a literal in every tools/*.ps1 file by
# evals/multi-model-verify/test_backup_lane.py's SWEEP_GLOBS; a default
# value here would be exactly that literal.
#
# Windows PowerShell 5.1 compatible, ASCII ONLY.
#
# Exit codes: 0 built/removed, nonzero on any refusal or failure.
[CmdletBinding(DefaultParameterSetName = "Build")]
param(
    [Parameter(Mandatory = $true)][string]$Path,
    [Parameter(ParameterSetName = "Build", Mandatory = $true)][string]$Model,
    [Parameter(ParameterSetName = "Build", Mandatory = $false)][string]$Effort = "high",
    [Parameter(ParameterSetName = "Remove", Mandatory = $true)][switch]$Remove
)

$ErrorActionPreference = "Stop"

$SentinelName = ".parallax-lane-home"
$SentinelMagic = "PARALLAX-LANE-HOME-V1"

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

if ($Remove) {
    # 1. Refuse unless the sentinel exists, and its two lines authorize
    # THIS resolved path. The sentinel's file NAME is not the credential -
    # a bare filename is plantable in any directory and would then
    # authorize a recursive delete of it. Its CONTENT is: the magic string,
    # then the resolved path it was written for.
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

    # Belt and braces on top of a correctly-formed sentinel: even one that
    # matches must not authorize deleting a drive root, the real user
    # profile or above it, or a repository root.
    $pathRoot = [System.IO.Path]::GetPathRoot($resolved)
    $normalizedResolved = $resolved.TrimEnd('\', '/')
    $normalizedRoot = $pathRoot.TrimEnd('\', '/')
    # IsPathRooted($resolved) is always true here - $resolved comes out of
    # Resolve-Path, which never returns a relative string. Kept anyway:
    # removing it would drop the literal a live pin depends on
    # (test_removal_refuses_dangerous_roots), and it documents the
    # invariant this comparison relies on rather than asserting it silently.
    $isDriveRoot = [System.IO.Path]::IsPathRooted($resolved) -and
                   ($normalizedResolved -ieq $normalizedRoot)
    if ($isDriveRoot) {
        throw "refusing to remove: $resolved is a drive root"
    }

    # The profile guard must FAIL CLOSED, not skip, when it cannot be
    # evaluated: this project deliberately runs subprocesses with
    # minimized environments, so an unset or unresolvable USERPROFILE is
    # reachable in real use, not just in a test. An unmade measurement is
    # never a clean one - if the guard cannot be evaluated, refuse.
    if (-not $env:USERPROFILE) {
        throw "refusing to remove: could not evaluate the user-profile guard (USERPROFILE is not set)"
    }
    if (-not (Test-Path -LiteralPath $env:USERPROFILE)) {
        throw "refusing to remove: could not evaluate the user-profile guard (USERPROFILE path does not exist: $env:USERPROFILE)"
    }
    $resolvedProfile = (Resolve-Path -LiteralPath $env:USERPROFILE).Path
    $normalizedProfile = $resolvedProfile.TrimEnd('\', '/')
    $sep = [System.IO.Path]::DirectorySeparatorChar
    # "or above it": equal to the profile, OR an ANCESTOR of it (the
    # profile sits somewhere under $resolved). Equality alone never
    # exercises the ancestor half.
    $isProfileOrAbove = ($normalizedProfile -ieq $normalizedResolved) -or
        $normalizedProfile.StartsWith($normalizedResolved + $sep,
            [System.StringComparison]::OrdinalIgnoreCase)
    if ($isProfileOrAbove) {
        throw "refusing to remove: $resolved is the user profile or above it"
    }

    if (Test-Path -LiteralPath (Join-Path $resolved ".git")) {
        throw "refusing to remove: $resolved contains a .git entry"
    }

    Remove-Item -LiteralPath $resolved -Recurse -Force
    Write-Output "removed $resolved"
    exit 0
}

# --- Build mode ---

# 2. Refuse an existing destination: reuse carries stale sessions, which
# corrupts the freshness the evidence rules depend on.
if (Test-Path -LiteralPath $Path) {
    throw "refusing to build: destination already exists: $Path"
}

# 2b. Refuse a -Model or -Effort that cannot be safely rendered into
# config.toml. This runs before ANYTHING touches the filesystem or the
# network, so a hostile value is rejected before any side effect, not
# merely before the render.
if (-not (Test-SafeConfigToken $Model)) {
    throw "refusing to build: -Model contains characters outside the allowed set (letters, digits, dot, dash, underscore, slash)"
}
if (-not (Test-SafeConfigToken $Effort)) {
    throw "refusing to build: -Effort contains characters outside the allowed set (letters, digits, dot, dash, underscore, slash)"
}

# 3. Resolve whether the PARENT is inside a git work tree (the target
# itself does not exist yet). Fail closed: an unmade or unreadable
# measurement is never a clean one, and the consequence here is an OAuth
# credential landing inside a repository.
#
# No directory is created for this check. An earlier version created the
# parent unconditionally here, before this and the credential gate below
# had run, and outside the try/catch that owns cleanup - so a refusal from
# either gate left that directory orphaned on disk. Git's own work-tree
# detection walks up from a directory looking for a `.git` entry in itself
# or an ancestor; a not-yet-created directory cannot itself carry one, so
# querying the NEAREST EXISTING ancestor gives the exact same answer the
# real parent would give once it exists, with no directory created before
# every refusal gate below has passed.
$fullPath = [System.IO.Path]::GetFullPath($Path)
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
# terminating NativeCommandError under $ErrorActionPreference = "Stop",
# even when that stderr is being captured rather than displayed - so the
# preference is relaxed for just this call and restored immediately after,
# and a git invocation that cannot even be found is caught explicitly so
# both failure directions land on our own message, never a bypass.
$previousEap = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$previousLcAll = $env:LC_ALL
# Pin git's message language for this call. The "not a git repository"
# match a few lines down depends on that exact English text; a localized
# git under a non-English LC_ALL/LANG would translate it, and the
# unrecognized string would then fail the match - which still fails
# CLOSED (the catch-all below refuses on anything unrecognized), but
# pinning the locale here means the common case is decided correctly
# rather than by falling through to the conservative refusal every time.
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
# Measured (git 2.54.0.windows.1, both hosts): a plain directory with no
# repository anywhere in its ancestry does NOT exit 0 with "false" - it
# exits 128 with a "fatal: not a git repository" line, every time, for
# every such directory tried. A strict "$LASTEXITCODE -ne 0 always
# refuses" reading therefore refuses in the overwhelmingly ordinary case
# this script exists to allow, and Build mode could never succeed
# anywhere. Git's own "fatal: not a git repository" text (LC_ALL=C above)
# is the positive, well-known signal for that state, so it is treated the
# same as an explicit "false". Every OTHER nonzero exit - a real git
# error, a corrupted repository, git missing from PATH - still fails
# closed below, which is the case the fails-closed rule and its test
# guard against.
$definitelyNoRepositoryAnywhere = ($gitExit -ne 0) -and
    ($gitAnswer -match "fatal: not a git repository")
$explicitlyOutsideTheWorkTree = ($gitExit -eq 0) -and ($gitAnswer -eq "false")
if (-not ($explicitlyOutsideTheWorkTree -or $definitelyNoRepositoryAnywhere)) {
    throw "could not determine whether $parent is inside a git work tree (git rev-parse exited $gitExit, output: $gitAnswer)"
}

# 4. Refuse if the source credential is absent. An unauthenticated lane
# must stop, not degrade.
$credentialSource = Join-Path $env:USERPROFILE ".kimi-code\credentials\kimi-code.json"
if (-not (Test-Path -LiteralPath $credentialSource)) {
    throw "the lane is UNAVAILABLE: no credential at $credentialSource"
}

# 5. $createdByThisInvocation is set ONLY after this invocation has
# created the directory and written the sentinel, so a refusal path above
# can never delete a directory the script declined to touch, and the catch
# below can never delete a directory some OTHER invocation created.
$createdByThisInvocation = $false
try {
    # This is the ONLY directory-creation in Build mode, and everything
    # above it is read-only. New-Item -Force creates the WHOLE missing
    # ancestor chain silently when $Path is nested under directories that
    # do not exist yet, not just the leaf - reproduced live via
    # PARALLAX_LANE_HOME_FAULT against a target several levels below an
    # existing directory: the leaf was correctly removed on failure, but
    # the missing ancestors New-Item had also created were left behind,
    # because the catch below removed only $resolved.
    #
    # So the chain New-Item is ABOUT TO create is recorded BEFORE it runs,
    # by walking up from $Path to the nearest directory that already
    # exists - recorded rather than inferred afterwards, because inferring
    # is how a cleanup deletes something that was already there. The
    # SHALLOWEST missing directory is what cleanup actually removes:
    # everything New-Item creates lands inside it, so removing it
    # recursively removes exactly what this invocation created and
    # nothing that existed beforehand.
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

    # 6. Sentinel first, then $createdByThisInvocation, then the ACL -
    # BEFORE the credential is copied.
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

    # 7. Copy the credential, then render config.toml. Unlike the
    # user's real ~/.kimi-code/config.toml, this template carries no hooks by construction.
    $credentialDir = Join-Path $resolved "credentials"
    New-Item -ItemType Directory -Path $credentialDir | Out-Null
    Copy-Item -LiteralPath $credentialSource -Destination (Join-Path $credentialDir "kimi-code.json")

    # Test seam for Task 3 Step 5's live fault test: prove the catch below
    # actually runs and actually cleans up a home that ALREADY HAS a
    # credential copied onto disk, by injecting a failure right after the
    # copy above completes. An earlier version threw this fault before the
    # copy ran, so the live test it exists to prove never actually
    # exercised cleanup with a credential present.
    if ($env:PARALLAX_LANE_HOME_FAULT) {
        throw "PARALLAX_LANE_HOME_FAULT injected: simulated post-credential-copy failure"
    }

    # The model table's `model` field is the provider-side name, which is
    # everything after the first "/" of the alias - derived, never
    # hardcoded, so this file names no specific backup model id.
    $slashIndex = $Model.IndexOf([char]47)
    if ($slashIndex -lt 0) {
        $providerModelName = $Model
    } else {
        $providerModelName = $Model.Substring($slashIndex + 1)
    }
    # The canonical backup model's real context window, kept as a bare
    # number so this file never carries the model id literal that names
    # it (see model-prompting-notes.md for that identity).
    $maxContextSize = 262144

    # Root-level keys MUST appear BEFORE any table header: a TOML table
    # header claims every key-value pair that follows it, up to the NEXT
    # header - a blank line does not end a table. An earlier version put
    # default_model/extra_skill_dirs/telemetry AFTER [models."$Model"],
    # so all three silently became keys of the MODEL table instead of the
    # document root: extra_skill_dirs (a containment setting) never
    # actually suppressed anything while looking like it did, and
    # telemetry was observed resolving to true despite this file saying
    # false. default_effort is the one key that belongs inside the model
    # table, and stays there.
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
provider = "managed:kimi-code"
model = "$providerModelName"
max_context_size = $maxContextSize
default_effort = "$Effort"

[thinking]
enabled = true
"@
    # ASCII, not utf8: Windows PowerShell 5.1's -Encoding utf8 prepends a
    # byte-order mark, which kimi-code's TOML parser rejects outright
    # ("only letter, numbers, dashes and underscores are allowed in
    # keys" on the very first line). Measured live. ASCII is sound here -
    # not merely because this template's own literals are ASCII, but
    # because $Model and $Effort were both checked against
    # $SafeTokenPattern above before being interpolated into it: neither
    # can carry a quote, a newline, or any non-ASCII byte, so nothing this
    # file writes can close the TOML string it is quoted inside or open an
    # attacker-chosen table.
    Set-Content -LiteralPath (Join-Path $resolved "config.toml") -Value $configToml -Encoding ascii

    New-Item -ItemType Directory -Path (Join-Path $resolved "skills") | Out-Null
} catch {
    if ($createdByThisInvocation) {
        # $cleanupRoot, not $resolved: $resolved is only the leaf, and a
        # nested target can leave empty ancestor directories above it that
        # this invocation also created. Removing $cleanupRoot removes the
        # whole chain this invocation created in one shot.
        Remove-Item -LiteralPath $cleanupRoot -Recurse -Force
    }
    throw
}

# 8. The only stdout output on success.
Write-Output (Resolve-Path -LiteralPath $Path).Path
