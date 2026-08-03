# plant-home-skill-canary.ps1 - plant one inert marker skill in a skill
# discovery root, and remove it again, so backlog item 17's probe can ask
# whether that root reaches the Kimi lane's reviewer.
#
# THIS TOOL WRITES INTO THE USER'S REAL HOME DIRECTORY. Every refusal below
# is load-bearing: the cost of a wrong recursive delete is the user's own
# files. It creates and removes exactly one directory, of exactly one fixed
# name, and refuses anything it does not recognise.
#
# PLANT IS TRANSACTIONAL. If it cannot emit a state file good enough to
# remove by, it removes what it created before exiting nonzero. A
# half-succeeded plant leaves a directory in a home with nothing recorded to
# clean it up, and that is the one residue a caller's try/finally cannot
# reach.
#
# REMOVE IS NOT IDEMPOTENT. Finding nothing to remove is a FAILURE, because
# a removal that verified nothing has not established the thing it claims.
#
# Comparison is ORDINAL and CASE-SENSITIVE throughout. PowerShell's
# Compare-Object, -eq, -ne and -contains all fold case by default, and this
# repo has already shipped one allowlist defeated by exactly that.
#
# The nonce is written into the canary file and the state file. It is never
# written to stdout or stderr: this repo is public and the probe record is
# committed.
#
# Windows PowerShell 5.1 compatible, ASCII ONLY.
#
# Exit codes: 0 success, 1 refusal or failure (reason on stderr).
[CmdletBinding(DefaultParameterSetName = "Plant")]
param(
    [Parameter(ParameterSetName = "Plant", Mandatory = $true)]
    [switch]$Plant,
    [Parameter(ParameterSetName = "Plant")]
    [AllowEmptyString()][string]$Nonce,
    [Parameter(ParameterSetName = "Plant")]
    [AllowEmptyString()][string]$StateOut,

    [Parameter(ParameterSetName = "Remove", Mandatory = $true)]
    [switch]$Remove,
    [Parameter(ParameterSetName = "Remove")]
    [AllowEmptyString()][string]$State,

    [Parameter(Mandatory = $true)]
    [AllowEmptyString()][string]$Root
)

$ErrorActionPreference = "Stop"

$CANARY_NAME = "parallax-home-root-canary"
$FAULT_VAR = "PARALLAX_CANARY_STATE_FAULT"
$NONCE_PATTERN = '\A[0-9a-f]{32}\z'

function Fail($message) {
    [Console]::Error.WriteLine($message)
    exit 1
}

function Get-OrdinalNames($path) {
    # -Force lists hidden entries too: a hidden intruder is still an
    # intruder, and a before/after comparison blind to them would call a
    # changed root unchanged.
    $raw = @(Get-ChildItem -LiteralPath $path -Force -Name)
    $list = New-Object "System.Collections.Generic.List[string]"
    foreach ($n in $raw) { [void]$list.Add([string]$n) }
    $list.Sort([System.StringComparer]::Ordinal)
    return ,$list.ToArray()
}

function Test-AnyReparsePoint($path) {
    # Walk MANUALLY and never step through a reparse point. Get-ChildItem
    # -Recurse follows junctions on some hosts, which would take this scan
    # into whatever the junction aims at - the exact excursion the scan
    # exists to refuse.
    $item = Get-Item -LiteralPath $path -Force
    if (($item.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        return $true
    }
    foreach ($child in @(Get-ChildItem -LiteralPath $path -Force)) {
        if (($child.Attributes -band [System.IO.FileAttributes]::ReparsePoint) -ne 0) {
            return $true
        }
        if ($child.PSIsContainer) {
            if (Test-AnyReparsePoint $child.FullName) { return $true }
        }
    }
    return $false
}

function Get-Sha256($path) {
    # .NET directly, NOT Get-FileHash. Measured 2026-08-03: when this script
    # is launched as a Windows PowerShell 5.1 child of a process whose
    # PSModulePath was inherited from PowerShell 7 - which is how the test
    # suite and the probe driver both invoke it - `Get-FileHash` resolves to
    # nothing and the run dies with a command-not-found. Every other cmdlet
    # used here survives that contamination; this one does not. A tool whose
    # availability depends on which host seeded the environment is not a tool
    # this lane can rely on, so it depends on no module at all.
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $bytes = [System.IO.File]::ReadAllBytes($path)
        return ([System.BitConverter]::ToString($sha.ComputeHash($bytes)) `
                -replace '-', '').ToLower()
    } finally {
        $sha.Dispose()
    }
}

# ---------------------------------------------------------------------------
# Shared root validation. Order matters and is asserted by the suite: a
# blank root is rejected before anything is resolved, and the profile-root
# refusal fires before anything at all is created.
# ---------------------------------------------------------------------------
if ([string]::IsNullOrWhiteSpace($Root)) {
    Fail "root is blank"
}

$resolvedRoot = $null
try {
    $resolvedRoot = (Resolve-Path -LiteralPath $Root -ErrorAction Stop).ProviderPath
} catch {
    $resolvedRoot = $null
}
if ($null -eq $resolvedRoot -or -not (Test-Path -LiteralPath $resolvedRoot -PathType Container)) {
    Fail "root does not exist: it is never created here, because a root that is not there is a measurement about the machine"
}

$profileRoot = $null
if (-not [string]::IsNullOrWhiteSpace($env:USERPROFILE)) {
    try {
        $profileRoot = (Resolve-Path -LiteralPath $env:USERPROFILE -ErrorAction Stop).ProviderPath
    } catch {
        $profileRoot = $null
    }
}
if ($null -ne $profileRoot -and
    [string]::Equals($resolvedRoot.TrimEnd('\'), $profileRoot.TrimEnd('\'),
                     [System.StringComparison]::OrdinalIgnoreCase)) {
    # Case-INSENSITIVE here on purpose, and only here: this is a Windows
    # path identity test, where C:\Users\X and c:\users\x are one directory.
    # Every other comparison in this script is ordinal and case-sensitive,
    # because those compare NAMES, not paths.
    Fail "refusing to plant directly in the profile root"
}

$canaryPath = Join-Path $resolvedRoot $CANARY_NAME

# ---------------------------------------------------------------------------
# Plant
# ---------------------------------------------------------------------------
if ($Plant) {
    # -cnotmatch, not -notmatch. PowerShell's -match/-notmatch are
    # CASE-INSENSITIVE by default, so `[0-9a-f]{32}` accepts an UPPERCASE
    # hex nonce and the pattern silently means something wider than it
    # reads. Measured 2026-08-03: the uppercase case passed until this
    # became -cnotmatch.
    if ($Nonce -cnotmatch $NONCE_PATTERN) {
        Fail "nonce must be exactly 32 lowercase hex characters"
    }
    if ([string]::IsNullOrWhiteSpace($StateOut)) {
        Fail "state output path is blank"
    }
    if (Test-Path -LiteralPath $canaryPath) {
        Fail "canary already present: a previous run did not clean up"
    }

    $before = Get-OrdinalNames $resolvedRoot

    $marker = "PARALLAX-CANARY-" + $Nonce
    $body = @(
        "---",
        ("name: " + $CANARY_NAME),
        ("description: parallax measurement canary " + $marker +
         ". Not a skill. Carries no instructions."),
        "---",
        "",
        "This directory is a measurement canary planted by the parallax plugin to",
        "determine whether this discovery root reaches a kimi-code reviewer. It",
        ("carries no instructions and asks for nothing. Nonce " + $marker + "."),
        "If this directory still exists after a parallax probe run, the probe's",
        "removal step failed and this directory should be deleted by hand."
    ) -join "`r`n"

    # Everything after the first mutation runs under a rollback guard.
    $created = $false
    try {
        New-Item -ItemType Directory -Path $canaryPath -ErrorAction Stop | Out-Null
        $created = $true
        Set-Content -LiteralPath (Join-Path $canaryPath "SKILL.md") -Value $body `
            -Encoding ascii -ErrorAction Stop

        if (-not [string]::IsNullOrEmpty($env:PARALLAX_CANARY_STATE_FAULT)) {
            throw [System.Exception]::new(
                ($FAULT_VAR + " injected: simulated state emission failure"))
        }

        # NOT $state. PowerShell variable names are CASE-INSENSITIVE, and
        # this script declares a [string]$State parameter for the Remove
        # set. `$state = [ordered]@{...}` assigns to that same variable,
        # whose [string] type constraint silently coerces the hashtable via
        # ToString() - so the state file was written as the literal text
        # "System.Collections.Specialized.OrderedDictionary" and every
        # Remove case failed downstream. Measured 2026-08-03. The three
        # ConvertTo-Json call forms are all sound; the collision was the
        # whole defect.
        $stateObj = [ordered]@{
            version      = 1
            root         = $resolvedRoot
            nonce        = $Nonce
            canary       = $canaryPath
            canarySha256 = (Get-Sha256 (Join-Path $canaryPath "SKILL.md"))
            before       = $before
        }
        $json = ConvertTo-Json $stateObj -Compress
        Set-Content -LiteralPath $StateOut -Value $json -Encoding ascii -ErrorAction Stop
    } catch {
        $reason = $_.Exception.Message
        if ($created) {
            # Best effort, but its failure is reported rather than swallowed:
            # a rollback that did not roll back is the residue this guard
            # exists to prevent, and silence about it would be worse than
            # the original failure.
            try {
                Remove-Item -LiteralPath $canaryPath -Recurse -Force -ErrorAction Stop
            } catch {
                Fail ($reason + " (AND the rollback failed: " + $canaryPath +
                      " is still present and must be removed by hand)")
            }
        }
        Fail $reason
    }
    exit 0
}

# ---------------------------------------------------------------------------
# Remove
# ---------------------------------------------------------------------------
if ($Remove) {
    if ([string]::IsNullOrWhiteSpace($State)) {
        Fail "state path is blank"
    }
    if (-not (Test-Path -LiteralPath $State -PathType Leaf)) {
        Fail "state file not found"
    }

    $parsed = $null
    try {
        $parsed = (Get-Content -LiteralPath $State -Raw -Encoding ascii) | ConvertFrom-Json
    } catch {
        Fail "state file is not readable JSON"
    }
    if ($null -eq $parsed) { Fail "state file parsed to null" }

    $fields = @($parsed.PSObject.Properties.Name)
    foreach ($f in @("version", "root", "nonce", "canary", "canarySha256", "before")) {
        if ($fields -cnotcontains $f) { Fail ("state file has no '" + $f + "' field") }
    }
    if ($fields.Count -ne 6) { Fail "state file carries unexpected fields" }

    # EXACT path equality, not a prefix test. Removal is recursive on
    # whatever this field names, so anything short of equality lets a
    # hand-edited state file aim it at a sibling this tool never created.
    if (-not [string]::Equals([string]$parsed.canary, $canaryPath,
                              [System.StringComparison]::Ordinal)) {
        Fail ("state file's canary path is not this root's canary: refusing to " +
              "delete a path this tool did not create")
    }

    if (-not (Test-Path -LiteralPath $canaryPath -PathType Container)) {
        Fail ("canary is already absent: a removal that finds nothing has " +
              "verified nothing, so this is a failure and not a success")
    }

    if (Test-AnyReparsePoint $canaryPath) {
        Fail "canary holds a reparse point; refusing to recurse"
    }

    $contents = @(Get-ChildItem -LiteralPath $canaryPath -Force)
    if ($contents.Count -ne 1 -or
        -not [string]::Equals($contents[0].Name, "SKILL.md",
                              [System.StringComparison]::Ordinal)) {
        Fail ("canary does not hold exactly the file that was planted: " +
              "refusing to delete a directory this tool no longer recognises")
    }
    $seen = Get-Sha256 $contents[0].FullName
    if (-not [string]::Equals($seen, ([string]$parsed.canarySha256).ToLower(),
                              [System.StringComparison]::Ordinal)) {
        Fail ("canary file does not hash to the recorded value: refusing to " +
              "delete a directory this tool no longer recognises")
    }

    Remove-Item -LiteralPath $canaryPath -Recurse -Force

    $after = Get-OrdinalNames $resolvedRoot
    $before = @($parsed.before | ForEach-Object { [string]$_ })
    $diff = @(Compare-Object -ReferenceObject $before -DifferenceObject $after `
                             -CaseSensitive)
    if ($diff.Count -gt 0) {
        $parts = New-Object "System.Collections.Generic.List[string]"
        foreach ($d in $diff) {
            $what = if ($d.SideIndicator -eq "=>") { "appeared" } else { "disappeared" }
            [void]$parts.Add(("'" + $d.InputObject + "' " + $what))
        }
        Fail ("the root changed during the run: " + ($parts -join ", "))
    }
    exit 0
}

Fail "no mode selected"
