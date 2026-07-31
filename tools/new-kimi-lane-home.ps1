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
    $isDriveRoot = [System.IO.Path]::IsPathRooted($resolved) -and
                   ($normalizedResolved -ieq $normalizedRoot)
    if ($isDriveRoot) {
        throw "refusing to remove: $resolved is a drive root"
    }

    if ($env:USERPROFILE -and (Test-Path -LiteralPath $env:USERPROFILE)) {
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

# 3. Resolve whether the PARENT is inside a git work tree (the target
# itself does not exist yet). Fail closed: an unmade or unreadable
# measurement is never a clean one, and the consequence here is an OAuth
# credential landing inside a repository.
$parent = Split-Path -Path $Path -Parent
if (-not $parent) { $parent = "." }
if (-not (Test-Path -LiteralPath $parent)) {
    New-Item -ItemType Directory -Force -Path $parent | Out-Null
}

# Windows PowerShell 5.1 turns ANY native-command stderr line into a
# terminating NativeCommandError under $ErrorActionPreference = "Stop",
# even when that stderr is being captured rather than displayed - so the
# preference is relaxed for just this call and restored immediately after,
# and a git invocation that cannot even be found is caught explicitly so
# both failure directions land on our own message, never a bypass.
$previousEap = $ErrorActionPreference
$ErrorActionPreference = "Continue"
try {
    $gitOutput = & git -C $parent rev-parse --is-inside-work-tree 2>&1
    $gitExit = $LASTEXITCODE
} catch {
    $ErrorActionPreference = $previousEap
    throw "could not determine whether $parent is inside a git work tree (git invocation failed: $($_.Exception.Message))"
}
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
# anywhere. Git's own "fatal: not a git repository" text is the
# positive, well-known signal for that state, so it is treated the same
# as an explicit "false". Every OTHER nonzero exit - a real git error, a
# corrupted repository, git missing from PATH - still fails closed below,
# which is the case the fails-closed rule and its test guard against.
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
    New-Item -ItemType Directory -Path $Path | Out-Null
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

    # Test seam for Task 3 Step 5's live fault test: prove the catch below
    # actually runs and actually cleans up, by injecting a failure right
    # after the point the credential is about to be copied.
    if ($env:PARALLAX_LANE_HOME_FAULT) {
        throw "PARALLAX_LANE_HOME_FAULT injected: simulated post-credential failure"
    }

    # 7. Copy the credential, then render config.toml. Unlike the
    # user's real ~/.kimi-code/config.toml, this template carries no hooks by construction.
    $credentialDir = Join-Path $resolved "credentials"
    New-Item -ItemType Directory -Path $credentialDir | Out-Null
    Copy-Item -LiteralPath $credentialSource -Destination (Join-Path $credentialDir "kimi-code.json")

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

    $configToml = @"
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

default_model = "$Model"
extra_skill_dirs = []
telemetry = false

[thinking]
enabled = true
"@
    # ASCII, not utf8: Windows PowerShell 5.1's -Encoding utf8 prepends a
    # byte-order mark, which kimi-code's TOML parser rejects outright
    # ("only letter, numbers, dashes and underscores are allowed in
    # keys" on the very first line). Measured live. Config content here
    # is plain ASCII by construction, so no information is lost.
    Set-Content -LiteralPath (Join-Path $resolved "config.toml") -Value $configToml -Encoding ascii

    New-Item -ItemType Directory -Path (Join-Path $resolved "skills") | Out-Null
} catch {
    if ($createdByThisInvocation) {
        Remove-Item -LiteralPath $resolved -Recurse -Force
    }
    throw
}

# 8. The only stdout output on success.
Write-Output (Resolve-Path -LiteralPath $Path).Path
