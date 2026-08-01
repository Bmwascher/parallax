# read-kimi-credential-state.ps1 - structural validation of a kimi-code
# credential file. Reports SHAPE only: whether the document is readable
# JSON, is an object, carries every required field with the right .NET
# type, and carries no blank token after trimming. It never checks
# truthiness (0 is a valid expires_at) and never checks freshness (a past
# expiry is a valid expires_at) - possession and staleness are somebody
# else's problem; this script answers only "is this a well-formed
# credential document". It never prints, logs, or otherwise emits a
# token VALUE - only field names and the frozen status/detail pair.
#
# Defect precedence, frozen: not-json, not-object, missing-field,
# wrong-type, blank-token. A document can carry several defects at once;
# only the FIRST that fires in this order is reported.
#
# Output object, frozen: exactly `status`, `detail`, `fields` - no other
# key, ever. `fields` lists the names observed in the parsed object,
# sorted with [System.StringComparer]::Ordinal, and is [] for exactly
# the four statuses where no field list could be established: absent,
# unreadable, not-json, not-object.
#
# CLASSIFICATION versus FAILURE, and why they use different channels.
# Exit code answers ONE question: did this invocation produce a
# classification at all? It never answers "is the credential clean" -
# that question is `status`, on stdout, and `status` can be `ok`,
# `absent`, `unreadable`, or `malformed` while the exit code is still 0,
# because all four are completed measurements. The doctor that calls
# this script keeps "lane credential absent" (status=absent) and "the
# validator itself failed to run" as SEPARATE rows, and an exit code
# that could not tell those two apart would erase that distinction -
# which is exactly the invariant this repo's fail-closed rule protects:
# an unmade, failed, or unreadable measurement is never a clean one, and
# collapsing "measured and found absent" into the same signal as
# "never measured" would be the unmade-measurement case wearing a
# passing exit code.
#
#   Classification (a status WAS produced): exit 0, exactly one
#     schema-valid JSON line on stdout, NOTHING on stderr.
#   Validator failure (no classification could be produced): exit 1, NO
#     stdout, and exactly one line of text on stderr. The blank/
#     whitespace -Path case and the PARALLAX_KIMI_CREDENTIAL_STATE_FAULT
#     seam both write "credential validator failed", except the fault
#     seam writes its own more specific line instead (see below) so a
#     caller can tell an injected failure from a genuine one in a test
#     log. A PowerShell parameter-binding or process-launch failure is
#     also validator failure by definition, even though this script's
#     own code never runs to produce either message.
param(
    [Parameter(Mandatory = $true)][string]$Path
)

$ErrorActionPreference = "Stop"

$RequiredFields = @("access_token", "refresh_token", "expires_at")

function Write-ValidatorFailure([string]$message = "credential validator failed") {
    [Console]::Error.WriteLine($message)
    exit 1
}

function Write-Result([string]$status, [string]$detail, [string[]]$fields) {
    $obj = [ordered]@{
        status = $status
        detail = $detail
        fields = @($fields)
    }
    Write-Output (ConvertTo-Json $obj -Compress)
    exit 0
}

function Get-SortedFieldNames($obj) {
    $names = [string[]]@($obj.PSObject.Properties.Name)
    [Array]::Sort($names, [System.StringComparer]::Ordinal)
    return $names
}

function Test-IntField($v) {
    # Int32 or Int64 only. A fractional number, a boolean, $null, a
    # numeric-looking string, and an Int64-overflowing value (which
    # ConvertFrom-Json widens to Decimal on Windows PowerShell 5.1 and to
    # BigInteger on PowerShell 7 - neither is [int] or [long]) all fail
    # this test, which is exactly what "wrong-type" requires.
    return ($v -is [int]) -or ($v -is [long])
}

try {
    # -- parameter validation: a blank/whitespace -Path was never a file
    # that got measured and found missing. Treating it as "absent" would
    # report a measurement that was never made as though it had been.
    if ([string]::IsNullOrWhiteSpace($Path)) {
        Write-ValidatorFailure
    }

    # -- fault injection seam, test-only. Fires after parameter
    # validation and immediately before the path probe: any NONEMPTY
    # value activates it, so a test can inject failure without needing a
    # specific magic value.
    if (-not [string]::IsNullOrEmpty($env:PARALLAX_KIMI_CREDENTIAL_STATE_FAULT)) {
        Write-ValidatorFailure "PARALLAX_KIMI_CREDENTIAL_STATE_FAULT injected: simulated validator failure"
    }

    # -- absent: the path does not exist, file or directory alike -------
    if (-not (Test-Path -LiteralPath $Path)) {
        Write-Result "absent" "no-file" @()
    }

    # -- unreadable: the path exists but the bytes cannot be read -------
    $bytes = $null
    try {
        $bytes = [System.IO.File]::ReadAllBytes($Path)
    } catch {
        Write-Result "unreadable" "read-failed" @()
    }

    $text = [System.Text.Encoding]::UTF8.GetString($bytes)

    # -- not-json: the bytes do not parse as JSON ------------------------
    $parsed = $null
    try {
        $parsed = $text | ConvertFrom-Json -ErrorAction Stop
    } catch {
        Write-Result "malformed" "not-json" @()
    }

    # -- not-object: it parses but is not an object ----------------------
    if (($null -eq $parsed) -or
        -not ($parsed -is [System.Management.Automation.PSCustomObject])) {
        Write-Result "malformed" "not-object" @()
    }

    $fieldNames = Get-SortedFieldNames $parsed
    $presentNames = @($parsed.PSObject.Properties.Name)

    # -- missing-field: a required field is absent ------------------------
    foreach ($required in $RequiredFields) {
        if ($presentNames -notcontains $required) {
            Write-Result "malformed" "missing-field" $fieldNames
        }
    }

    # -- wrong-type: a required field is present with the wrong type -----
    # access_token, refresh_token: .NET String. expires_at: Int32 or Int64.
    if (-not ($parsed.access_token -is [string])) {
        Write-Result "malformed" "wrong-type" $fieldNames
    }
    if (-not ($parsed.refresh_token -is [string])) {
        Write-Result "malformed" "wrong-type" $fieldNames
    }
    if (-not (Test-IntField $parsed.expires_at)) {
        Write-Result "malformed" "wrong-type" $fieldNames
    }

    # -- blank-token: access_token or refresh_token empty after Trim() ---
    if ($parsed.access_token.Trim().Length -eq 0) {
        Write-Result "malformed" "blank-token" $fieldNames
    }
    if ($parsed.refresh_token.Trim().Length -eq 0) {
        Write-Result "malformed" "blank-token" $fieldNames
    }

    # -- ok: every required field present and well-typed -------------------
    Write-Result "ok" "valid" $fieldNames
} catch {
    # Anything reaching here is an UNEXPECTED failure - every planned
    # measurement above already has its own try/catch and exits before
    # unwinding this far. An unmade or failed measurement is never a
    # clean one, so this is validator failure, not a classification.
    Write-ValidatorFailure
}
