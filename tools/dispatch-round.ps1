# dispatch-round.ps1 - prepare a completion-coupled review-round dispatch:
# build the round's directory as one fail-closed transaction and print the
# exact command line the caller runs as a named background task.
#
# ONE MODE in this revision:
#
#   Prepare: -DispatchDir <path> -WrapperBody <path> -ReceiptPath <path>
#            -Round <label> -WorkingDirectory <path> -RepoRoot <path>
#            -SourceHead <sha> -MirrorHead <sha> -SourceStatusSha256 <hex>
#            -MirrorStateSha256 <hex> -ExpectedMirrorPath <path>
#            -DispatchHost <pwsh|powershell> -PriorStateFile <path>
#            (-WorkdirEvidence <literal> | -NoWorkdirEvidence) [-Json]
#
# -LAUNCH AND -POLL ARE GONE. This tool used to start a detached process
# itself and let a caller poll its liveness from a second, independent
# path to a verdict - the class of defect this cycle kept reproducing.
# -Prepare only builds the directory and prints the command; the caller
# dispatches that command itself as a harness-tracked background task, and
# the WRAPPER this tool writes classifies its own outcome as its last act.
# A later task adds -Classify and the wrapper's full shape - see
# docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md.
#
# -Prepare, in order, under $ErrorActionPreference = 'Stop':
#   1. Resolve -ReceiptPath, -DispatchDir, -WorkingDirectory. BLOCK, before
#      anything is created, if the receipt path is equal to or inside the
#      dispatch directory, if the receipt path already exists, if the
#      dispatch directory already exists, or if the working directory is
#      not an existing filesystem container.
#   1a. BLOCK if the working directory does not verify as the named
#      mirror: tools/new-review-mirror.ps1 -VerifyIdentity is run with
#      every value the caller supplied, and any non-zero exit BLOCKS.
#      There is no override switch - every call site already uses the
#      mirror.
#   2. Resolve -DispatchHost to a full path with Get-Command. Only 'pwsh'
#      and 'powershell' are accepted; anything else, or a name that does
#      not resolve, exits 2.
#   3. Read -PriorStateFile as raw bytes and hash it (SHA256).
#   4. Reserve the dispatch directory with New-Item -ItemType Directory
#      and NO -Force: a taken directory fails loudly instead of
#      proceeding with an unreliable path.
#   5. Copy -WrapperBody into the directory as body.ps1, byte for byte,
#      and write wrapper.ps1 beside it. The wrapper is written ENTIRELY
#      by this tool and never contains the body's text; it runs body.ps1
#      as a child process and exits with its code. A later task builds
#      the wrapper's full shape (the mirror re-verify at dispatch time,
#      the classification reservation, the -Classify call).
#   6. Write the receipt LAST, with create-new semantics. Its fields are
#      exactly: dispatchDir, token, round, workingDirectory, dispatchHost,
#      priorStateSha256, workdirEvidence, repoRoot, sourceHead,
#      mirrorHead, sourceStatusSha256, mirrorStateSha256,
#      expectedMirrorPath, schema (the integer 2).
#   7. Print command, taskName, wrapper, dispatchDir, round.
#
# A failure at any step leaves the reserved directory in place and no
# receipt. That is the shape of a handled failure, not evidence of one.
#
# Exit codes: 0 prepared, 1 blocked (reason on stdout), 2 a failure to
# bind or validate the parameters (an unknown mode, a missing required
# value, an invalid -DispatchHost) or an internal execution error.
#
# Windows PowerShell 5.1 compatible, ASCII only.

param(
    [switch]$Prepare,
    [string]$DispatchDir,
    [string]$WrapperBody,
    [string]$ReceiptPath,
    [string]$Round,
    [string]$WorkingDirectory,
    [string]$RepoRoot,
    [string]$SourceHead,
    [string]$MirrorHead,
    [string]$SourceStatusSha256,
    [string]$MirrorStateSha256,
    [string]$ExpectedMirrorPath,
    [string]$DispatchHost,
    [string]$PriorStateFile,
    [string]$WorkdirEvidence,
    [switch]$NoWorkdirEvidence,

    [switch]$Json
)

$ErrorActionPreference = 'Stop'

function Resolve-UnresolvedPath([string]$Path) {
    return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Path)
}

function Get-Sha256Hex([byte[]]$Bytes) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $hash = $sha.ComputeHash($Bytes)
    } finally {
        $sha.Dispose()
    }
    $sb = New-Object System.Text.StringBuilder
    foreach ($b in $hash) { [void]$sb.Append($b.ToString("x2")) }
    return $sb.ToString()
}

# ---------------------------------------------------------------------
# Mode selection and required-value checks are done by hand: every
# parameter above is a plain [string] or [switch], never PowerShell's own
# Mandatory attribute, so a caller who names the wrong mode (including an
# old -Launch or -Poll, which no longer bind to anything) falls through to
# this explicit check rather than into the binder's own error shape.
# ---------------------------------------------------------------------
if (-not $Prepare) {
    Write-Output "ERROR: specify -Prepare"
    exit 2
}

$requiredValues = [ordered]@{
    DispatchDir        = $DispatchDir
    WrapperBody        = $WrapperBody
    ReceiptPath        = $ReceiptPath
    Round              = $Round
    WorkingDirectory   = $WorkingDirectory
    RepoRoot           = $RepoRoot
    SourceHead         = $SourceHead
    MirrorHead         = $MirrorHead
    SourceStatusSha256 = $SourceStatusSha256
    MirrorStateSha256  = $MirrorStateSha256
    ExpectedMirrorPath = $ExpectedMirrorPath
    DispatchHost       = $DispatchHost
    PriorStateFile     = $PriorStateFile
}
foreach ($name in $requiredValues.Keys) {
    if ([string]::IsNullOrWhiteSpace($requiredValues[$name])) {
        Write-Output ("ERROR: -Prepare requires -" + $name)
        exit 2
    }
}
if ($WorkdirEvidence -and $NoWorkdirEvidence) {
    Write-Output "ERROR: specify exactly one of -WorkdirEvidence or -NoWorkdirEvidence"
    exit 2
}
if ((-not $WorkdirEvidence) -and (-not $NoWorkdirEvidence)) {
    Write-Output "ERROR: specify exactly one of -WorkdirEvidence or -NoWorkdirEvidence"
    exit 2
}

# ---------------------------------------------------------------------
# Step 1: separation and freshness, before anything is created.
# ---------------------------------------------------------------------
try {
    $dispatchFull = Resolve-UnresolvedPath $DispatchDir
    $receiptFull = Resolve-UnresolvedPath $ReceiptPath
    $workingFull = Resolve-UnresolvedPath $WorkingDirectory
} catch {
    Write-Output ("ERROR: could not resolve the prepare paths: " + $_.Exception.Message)
    exit 2
}

$dNorm = $dispatchFull.TrimEnd('\', '/')
$rNorm = $receiptFull.TrimEnd('\', '/')
$dPrefix = $dNorm + '\'
$cmp = [System.StringComparison]::OrdinalIgnoreCase
if ([string]::Equals($rNorm, $dNorm, $cmp) -or $rNorm.StartsWith($dPrefix, $cmp)) {
    Write-Output ("BLOCKED: the receipt path is equal to, or inside, the dispatch directory (" +
        $receiptFull + " / " + $dispatchFull + ")")
    exit 1
}
if (Test-Path -LiteralPath $receiptFull) {
    Write-Output ("BLOCKED: the receipt path already exists (" + $receiptFull + ")")
    exit 1
}
if (Test-Path -LiteralPath $dispatchFull) {
    Write-Output ("BLOCKED: dispatch directory already exists (" + $dispatchFull + ")")
    exit 1
}
if (-not (Test-Path -LiteralPath $workingFull -PathType Container)) {
    Write-Output ("BLOCKED: the working directory does not exist (" + $workingFull + ")")
    exit 1
}

# ---------------------------------------------------------------------
# Step 1a: the working directory must verify as the named mirror. There
# is no override switch - see the header.
# ---------------------------------------------------------------------
$repoRootFull = Resolve-UnresolvedPath $RepoRoot
$expectedMirrorFull = Resolve-UnresolvedPath $ExpectedMirrorPath
$mirrorToolPath = Join-Path $PSScriptRoot "new-review-mirror.ps1"
$mirrorArgs = @{
    VerifyIdentity     = $true
    RepoRoot           = $repoRootFull
    MirrorPath         = $workingFull
    SourceHead         = $SourceHead
    MirrorHead         = $MirrorHead
    SourceStatusSha256 = $SourceStatusSha256
    MirrorStateSha256  = $MirrorStateSha256
    ExpectedMirrorPath = $expectedMirrorFull
}
$verifyOut = $null
try {
    $verifyOut = & $mirrorToolPath @mirrorArgs 2>&1
} catch {
    Write-Output ("BLOCKED: the working directory did not verify as the named mirror: " +
        $_.Exception.Message)
    exit 1
}
if ($LASTEXITCODE -ne 0) {
    Write-Output ("BLOCKED: the working directory did not verify as the named mirror: " +
        ((@($verifyOut) | Out-String).Trim()))
    exit 1
}

# ---------------------------------------------------------------------
# Step 2: resolve the dispatch host.
# ---------------------------------------------------------------------
if (($DispatchHost -cne 'pwsh') -and ($DispatchHost -cne 'powershell')) {
    Write-Output ("ERROR: -DispatchHost must be exactly 'pwsh' or 'powershell', not '" +
        $DispatchHost + "'")
    exit 2
}
$hostCmd = Get-Command $DispatchHost -ErrorAction SilentlyContinue
if (-not $hostCmd) {
    Write-Output ("ERROR: -DispatchHost '" + $DispatchHost + "' did not resolve")
    exit 2
}
$hostPath = $hostCmd.Source

# ---------------------------------------------------------------------
# Step 3: hash the sealed prior-state evidence.
# ---------------------------------------------------------------------
try {
    $priorFull = Resolve-UnresolvedPath $PriorStateFile
    $priorBytes = [System.IO.File]::ReadAllBytes($priorFull)
} catch {
    Write-Output ("BLOCKED: could not read -PriorStateFile: " + $_.Exception.Message)
    exit 1
}
$priorStateSha256 = Get-Sha256Hex $priorBytes

# ---------------------------------------------------------------------
# Step 4: reserve the dispatch directory. No -Force: a taken directory
# fails loudly instead of proceeding with an unreliable path.
# ---------------------------------------------------------------------
$d = $null
try {
    $d = (New-Item -ItemType Directory -Path $dispatchFull -ErrorAction Stop).FullName
} catch {
    Write-Output ("BLOCKED: could not reserve the dispatch directory: " + $_.Exception.Message)
    exit 1
}

# ---------------------------------------------------------------------
# Steps 5-6: install the body, write the wrapper, write the receipt
# last. Any failure here leaves the reserved directory in place and no
# receipt - a handled failure, not evidence of one.
# ---------------------------------------------------------------------
$wrapperDest = Join-Path $d "wrapper.ps1"
$token = $null
try {
    $bodyDest = Join-Path $d "body.ps1"
    Copy-Item -LiteralPath $WrapperBody -Destination $bodyDest -ErrorAction Stop

    # Written ENTIRELY by this tool and never carries the body's text.
    # This is the minimal shape for this task: run body.ps1 as a child
    # and exit with its code. A later task builds the wrapper's full
    # shape.
    $wrapperContent =
        "`$ErrorActionPreference = 'Stop'`r`n" +
        "& '" + $hostPath + "' -NoProfile -NonInteractive -File `"`$PSScriptRoot/body.ps1`"`r`n" +
        "exit `$LASTEXITCODE`r`n"
    Set-Content -LiteralPath $wrapperDest -Value $wrapperContent -Encoding Ascii -NoNewline

    $token = [System.Guid]::NewGuid().ToString()
    $workdirEvidenceValue = $WorkdirEvidence
    if ($NoWorkdirEvidence) {
        $workdirEvidenceValue = "none"
    }
    $receiptObj = [ordered]@{
        dispatchDir        = $d
        token              = $token
        round              = $Round
        workingDirectory   = $workingFull
        dispatchHost       = $hostPath
        priorStateSha256   = $priorStateSha256
        workdirEvidence    = $workdirEvidenceValue
        repoRoot           = $repoRootFull
        sourceHead         = $SourceHead
        mirrorHead         = $MirrorHead
        sourceStatusSha256 = $SourceStatusSha256
        mirrorStateSha256  = $MirrorStateSha256
        expectedMirrorPath = $expectedMirrorFull
        schema             = 2
    }
    $receiptJson = ConvertTo-Json $receiptObj -Compress
    $receiptBytes = [System.Text.Encoding]::UTF8.GetBytes($receiptJson)
    $fs = New-Object System.IO.FileStream($receiptFull, [System.IO.FileMode]::CreateNew,
        [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
    try {
        $fs.Write($receiptBytes, 0, $receiptBytes.Length)
        $fs.Flush($true)
    } finally {
        $fs.Dispose()
    }
} catch {
    Write-Output ("BLOCKED: " + $_.Exception.Message)
    exit 1
}

# ---------------------------------------------------------------------
# Step 7: print what the caller needs.
# ---------------------------------------------------------------------
$command = '"' + $hostPath + '" -NoProfile -NonInteractive -File "' + $wrapperDest + '"'
$taskName = $Round + " debate round"

if ($Json) {
    $outObj = [ordered]@{
        command     = $command
        taskName    = $taskName
        wrapper     = $wrapperDest
        dispatchDir = $d
        round       = $Round
    }
    Write-Output (ConvertTo-Json $outObj -Compress)
} else {
    Write-Output ("command: " + $command)
    Write-Output ("taskName: " + $taskName)
    Write-Output ("wrapper: " + $wrapperDest)
    Write-Output ("dispatchDir: " + $d)
    Write-Output ("round: " + $Round)
}
exit 0
