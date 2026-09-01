# dispatch-round.ps1 - prepare a completion-coupled review-round dispatch,
# and classify a finished one: build the round's directory as one
# fail-closed transaction and print the exact command line the caller
# runs as a named background task; later, redeem that round's
# reservation and report the one state its dispatch directory is in.
#
# TWO MODES:
#
#   Prepare:  -DispatchDir <path> -WrapperBody <path> -ReceiptPath <path>
#             -Round <label> -WorkingDirectory <path> -RepoRoot <path>
#             -SourceHead <sha> -MirrorHead <sha> -SourceStatusSha256 <hex>
#             -MirrorStateSha256 <hex> -ExpectedMirrorPath <path>
#             -DispatchHost <pwsh|powershell> -PriorStateFile <path>
#             (-WorkdirEvidence <literal> | -NoWorkdirEvidence) [-Json]
#
#   Classify: -DispatchDir <path> -ReceiptPath <path> -ExpectedRound <label>
#             -ExpectedReceiptSha256 <hex> -Redeem <nonce> [-Json]
#
# -LAUNCH AND -POLL ARE GONE. This tool used to start a detached process
# itself and let a caller poll its liveness from a second, independent
# path to a verdict - the class of defect this cycle kept reproducing.
# -Prepare only builds the directory and prints the command; the caller
# dispatches that command itself as a harness-tracked background task, and
# the WRAPPER this tool writes (a later task builds its full shape) calls
# -Classify as its last act and exits with its status. See
# docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md.
#
# -Classify REDEEMS a reservation the wrapper already made in the
# `classification` file. It never creates one. It accepts exactly one
# content: `classifying:<nonce>` where nonce equals -Redeem; anything
# else (including a plain `reserved`, meaning the wrapper has not
# finished) is refused rather than treated as permission to proceed.
# Once redeemed, the resolved state name is WRITTEN into `classification`,
# so the file is both the reservation and the record, and every later
# call sees a value that is neither `reserved` nor a matching
# `classifying:<n>` and answers `already-classified`.
#
# In this fixed order, stopping at the first match:
#   1. classification absent -> never-reserved
#   2. classification holds 'reserved' -> not-ready
#   3. classification holds classifying:<n> with n not -Redeem, or
#      anything else -> already-classified
#   4. receipt absent, unreadable, or failing the schema -> no-receipt
#   5. receipt's dispatchDir or round is not the pair supplied
#      independently -> receipt-not-expected
#   6. the receipt's own bytes do not hash to -ExpectedReceiptSha256 ->
#      receipt-altered
#   7. no claim file in the dispatch directory -> no-claim
#   8. workingDirectory missing, unresolvable, or not a filesystem
#      container -> cwd-unreadable
#   9. workdirEvidence is not 'none' and no transcript file exists ->
#      no-transcript
#  10. workdirEvidence is not 'none' and the transcript's FIRST
#      'workdir:' header line is absent -> workdir-unconfirmed
#  11. that header line's value differs from workdirEvidence ->
#      workdir-mismatch
#  12. no exit file -> no-exit-file
#  13. exit unreadable or not a plain integer -> exit-unreadable
#  14. exit non-zero -> exit-nonzero
#  15. no reply file -> no-reply
#  16. reply is empty -> reply-empty
#  17. otherwise -> reply-present
#
# -Classify exit codes: 0 is reply-present and nothing else; 2 is a
# parameter-binding failure, an unrecognized argument, or an internal
# execution error; 1 is every other state, with the state name on stdout.
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

    [switch]$Classify,
    [string]$ExpectedRound,
    [string]$ExpectedReceiptSha256,
    [string]$Redeem,

    [switch]$Json,

    # Catches every remaining token so an unrecognized argument is
    # refused rather than silently absorbed. Measured on both hosts: a
    # -File invocation hands this array one PHANTOM $null element even
    # when nothing else would land there - see tools/new-review-mirror.ps1's
    # own $BuildRemainingArgs handling, which this follows. Neither a
    # real flag name nor a real value is ever null or empty, so filtering
    # both out below removes exactly the phantom.
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$Rest
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

# Validates a parsed receipt against Task 2's schema: exactly the
# fourteen named fields, no missing field, no extra field, every string
# field non-null and non-empty, and `schema` a JSON number equal to 2.
# Any other deviation - wrong top-level type, a missing field, an empty
# string field, a wrong JSON type, an unknown extra field - fails it the
# same way; nothing branches differently on which deviation it was.
function Test-ReceiptSchema($Obj) {
    if ($null -eq $Obj) { return $false }
    if (-not ($Obj -is [System.Management.Automation.PSCustomObject])) {
        return $false
    }

    $requiredStringFields = @(
        'dispatchDir', 'token', 'round', 'workingDirectory', 'dispatchHost',
        'priorStateSha256', 'workdirEvidence', 'repoRoot', 'sourceHead',
        'mirrorHead', 'sourceStatusSha256', 'mirrorStateSha256',
        'expectedMirrorPath')
    $allFields = $requiredStringFields + @('schema')

    $propSet = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach ($p in @($Obj.PSObject.Properties.Name)) { [void]$propSet.Add($p) }
    foreach ($f in $allFields) {
        if (-not $propSet.Contains($f)) { return $false }
    }
    if ($propSet.Count -ne $allFields.Count) { return $false }

    foreach ($f in $requiredStringFields) {
        $v = $Obj.$f
        if ($null -eq $v) { return $false }
        if (-not ($v -is [string])) { return $false }
        if ($v.Length -eq 0) { return $false }
    }

    $schemaVal = $Obj.schema
    if ($null -eq $schemaVal) { return $false }
    if ($schemaVal -is [string]) { return $false }
    $isNumeric = ($schemaVal -is [int]) -or ($schemaVal -is [long]) -or
                 ($schemaVal -is [double]) -or ($schemaVal -is [decimal])
    if (-not $isNumeric) { return $false }
    if ([double]$schemaVal -ne 2) { return $false }

    return $true
}

# ---------------------------------------------------------------------
# Reject unknown arguments for BOTH modes, before anything else runs.
# See the $Rest declaration above for why the phantom filter is needed.
# ---------------------------------------------------------------------
$realRest = @($Rest | Where-Object { $_ })
if ($realRest.Count -gt 0) {
    Write-Output ("ERROR: unrecognized parameter '" + [string]$realRest[0] + "'")
    exit 2
}

# ---------------------------------------------------------------------
# Mode selection and required-value checks are done by hand: every
# parameter above is a plain [string] or [switch], never PowerShell's own
# Mandatory attribute, so a caller who names the wrong mode (including an
# old -Launch or -Poll, which no longer bind to anything) falls through to
# this explicit check rather than into the binder's own error shape.
# ---------------------------------------------------------------------
if ((-not $Prepare) -and (-not $Classify)) {
    Write-Output "ERROR: specify -Prepare or -Classify"
    exit 2
}
if ($Prepare -and $Classify) {
    Write-Output "ERROR: specify exactly one of -Prepare or -Classify"
    exit 2
}

if ($Prepare) {

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

} elseif ($Classify) {

# ---------------------------------------------------------------------
# -Classify: redeem the wrapper's reservation and report the one state
# the dispatch directory is in. See the header for the full state order.
# ---------------------------------------------------------------------
$requiredClassify = [ordered]@{
    DispatchDir           = $DispatchDir
    ReceiptPath           = $ReceiptPath
    ExpectedRound         = $ExpectedRound
    ExpectedReceiptSha256 = $ExpectedReceiptSha256
    Redeem                = $Redeem
}
foreach ($name in $requiredClassify.Keys) {
    if ([string]::IsNullOrWhiteSpace($requiredClassify[$name])) {
        Write-Output ("ERROR: -Classify requires -" + $name)
        exit 2
    }
}

try {
    $dispatchFull = Resolve-UnresolvedPath $DispatchDir
    $receiptFull = Resolve-UnresolvedPath $ReceiptPath
} catch {
    Write-Output ("ERROR: could not resolve the classify paths: " + $_.Exception.Message)
    exit 2
}

function Write-ClassifyState([string]$State, $RoundOut, [bool]$RecordFile) {
    if ($RecordFile) {
        $classificationPath = Join-Path $dispatchFull "classification"
        $utf8 = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($classificationPath, $State, $utf8)
    }
    if ($Json) {
        $obj = [ordered]@{ state = $State; round = $RoundOut }
        Write-Output (ConvertTo-Json $obj -Compress)
    } else {
        Write-Output $State
    }
}

$classificationPath = Join-Path $dispatchFull "classification"

# 1. classification absent -> never-reserved
if (-not (Test-Path -LiteralPath $classificationPath -PathType Leaf)) {
    Write-ClassifyState "never-reserved" $null $false
    exit 1
}

try {
    $classContent = [System.IO.File]::ReadAllText($classificationPath, [System.Text.Encoding]::UTF8)
} catch {
    Write-Output ("ERROR: could not read classification: " + $_.Exception.Message)
    exit 2
}

# 2. classification holds 'reserved' -> not-ready
if ($classContent -ceq 'reserved') {
    Write-ClassifyState "not-ready" $null $false
    exit 1
}

# 3. classifying:<n> with n != -Redeem, or anything else -> already-classified
$expectedReservation = "classifying:" + $Redeem
if ($classContent -cne $expectedReservation) {
    Write-ClassifyState "already-classified" $null $false
    exit 1
}

# From here, this call owns the reservation: the resolved state is
# WRITTEN into `classification`, so the file is both the reservation and
# the record.
$roundOut = $null

# 4. receipt absent, unreadable, or failing the schema -> no-receipt
if (-not (Test-Path -LiteralPath $receiptFull -PathType Leaf)) {
    Write-ClassifyState "no-receipt" $null $true
    exit 1
}
$receiptBytes = $null
$receiptObj = $null
try {
    $receiptBytes = [System.IO.File]::ReadAllBytes($receiptFull)
    $receiptText = [System.Text.Encoding]::UTF8.GetString($receiptBytes)
    $receiptObj = $receiptText | ConvertFrom-Json -ErrorAction Stop
} catch {
    $receiptObj = $null
}
if (-not (Test-ReceiptSchema $receiptObj)) {
    Write-ClassifyState "no-receipt" $null $true
    exit 1
}
$roundOut = [string]$receiptObj.round

# 5. receipt's dispatchDir or round is not the pair supplied
#    independently -> receipt-not-expected
$receiptDispatchDir = [string]$receiptObj.dispatchDir
$dNormC = $dispatchFull.TrimEnd('\', '/')
$rdNormC = $receiptDispatchDir.TrimEnd('\', '/')
$cmpC = [System.StringComparison]::OrdinalIgnoreCase
if ((-not [string]::Equals($rdNormC, $dNormC, $cmpC)) -or
        ($receiptObj.round -cne $ExpectedRound)) {
    Write-ClassifyState "receipt-not-expected" $roundOut $true
    exit 1
}

# 6. the receipt's own bytes do not hash to the digest the wrapper
#    carries -> receipt-altered
$actualSha = Get-Sha256Hex $receiptBytes
if ($actualSha.ToLowerInvariant() -ne $ExpectedReceiptSha256.ToLowerInvariant()) {
    Write-ClassifyState "receipt-altered" $roundOut $true
    exit 1
}

# 7. no claim file in the dispatch directory -> no-claim
if (-not (Test-Path -LiteralPath (Join-Path $dispatchFull "claim") -PathType Leaf)) {
    Write-ClassifyState "no-claim" $roundOut $true
    exit 1
}

# 8. workingDirectory missing, unresolvable, or not a filesystem
#    container -> cwd-unreadable
$workingDirFull = $null
try {
    $workingDirFull = Resolve-UnresolvedPath ([string]$receiptObj.workingDirectory)
} catch {
    $workingDirFull = $null
}
if ((-not $workingDirFull) -or
        (-not (Test-Path -LiteralPath $workingDirFull -PathType Container))) {
    Write-ClassifyState "cwd-unreadable" $roundOut $true
    exit 1
}

# 9-11. the working-directory evidence check, skipped only on the exact
# literal 'none'. The header is PARSED - the FIRST 'workdir:' line only -
# never searched for, because the transcript is prompt-steerable.
$workdirEvidence = [string]$receiptObj.workdirEvidence
if ($workdirEvidence -cne 'none') {
    $transcriptPath = Join-Path $dispatchFull "transcript"
    if (-not (Test-Path -LiteralPath $transcriptPath -PathType Leaf)) {
        Write-ClassifyState "no-transcript" $roundOut $true
        exit 1
    }
    $transcriptLines = @(Get-Content -LiteralPath $transcriptPath)
    $headerValue = $null
    foreach ($line in $transcriptLines) {
        $lineStr = [string]$line
        if ($lineStr.StartsWith("workdir:")) {
            $headerValue = $lineStr.Substring(8).Trim()
            break
        }
    }
    if ($null -eq $headerValue) {
        Write-ClassifyState "workdir-unconfirmed" $roundOut $true
        exit 1
    }
    if ($headerValue -cne $workdirEvidence) {
        Write-ClassifyState "workdir-mismatch" $roundOut $true
        exit 1
    }
}

# 12. no exit file -> no-exit-file
$exitPath = Join-Path $dispatchFull "exit"
if (-not (Test-Path -LiteralPath $exitPath -PathType Leaf)) {
    Write-ClassifyState "no-exit-file" $roundOut $true
    exit 1
}

# 13. exit unreadable or not a plain integer -> exit-unreadable
$exitContent = $null
try {
    $exitContent = ([System.IO.File]::ReadAllText($exitPath)).Trim()
} catch {
    $exitContent = $null
}
if (($null -eq $exitContent) -or ($exitContent -notmatch '^-?\d+$')) {
    Write-ClassifyState "exit-unreadable" $roundOut $true
    exit 1
}
$exitCode = [int]$exitContent

# 14. exit non-zero -> exit-nonzero
if ($exitCode -ne 0) {
    Write-ClassifyState "exit-nonzero" $roundOut $true
    exit 1
}

# 15. no reply file -> no-reply
$replyPath = Join-Path $dispatchFull "reply"
if (-not (Test-Path -LiteralPath $replyPath -PathType Leaf)) {
    Write-ClassifyState "no-reply" $roundOut $true
    exit 1
}

# 16. reply is empty -> reply-empty
if ((Get-Item -LiteralPath $replyPath).Length -eq 0) {
    Write-ClassifyState "reply-empty" $roundOut $true
    exit 1
}

# 17. otherwise -> reply-present
Write-ClassifyState "reply-present" $roundOut $true
exit 0

}
