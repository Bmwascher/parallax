# read-codex-round-evidence.ps1 - bind ONE codex debate round's reply to
# the brief this side actually sent, by reading the client's OWN append-only
# session rollout.
#
# WHY THIS EXISTS. The backup lane has always failed a round whose recorded
# prompt differs from the brief that was sent. The codex lane had no such
# check, and that asymmetry is the whole defect: measured 2026-08-03,
# Windows PowerShell 5.1 native argument splatting STRIPS a double-quoted
# span that contains no space, and it does so without changing the argument
# COUNT. Nothing errors. The reviewer answers a brief this side never wrote,
# and the driver reads the answer as a clean round.
#
# WHAT IT READS, AND WHY THAT FILE. The human-readable transcript is
# PROMPT-STEERABLE: measured the same day, a brief carrying delimiter-shaped
# payload put a second `session id:` line into the transcript, so a parser
# taking the last match reads the value the BRIEF chose. The JSONL rollout
# under <CODEX_HOME>/sessions/<yyyy>/<mm>/<dd>/ is immune by construction -
# delimiter-shaped text inside a JSON string cannot create a record boundary
# - so it, and never the transcript, is the data source.
#
# WHAT A CLEAN VERDICT DOES AND DOES NOT CLAIM. It claims the client
# RECORDED, in the byte range this call appended, exactly one user prompt
# equal to the declared brief. That is CLIENT-ECHO evidence. It is not
# evidence about what any server received, and it never becomes that.
#
# TWO PARAMETER SETS, because a fresh call must DISCOVER its rollout (the
# file does not exist before the client creates it) and a resume must be
# TOLD which file to measure. Passing a fresh-only argument to the resume
# set, or the reverse, is PowerShell's own parameter-set resolution error,
# never a runtime check.
#
#   Fresh:  -Fresh -SessionsRoot <dir> -SessionIdFromStdout <id>
#           -PriorState <json-file> -ExpectedBriefSha256 <hex> [-Json]
#   Resume: -Resume -RolloutFile <path>
#           -PriorState <json-file> -ExpectedBriefSha256 <hex> [-Json]
#
# -PriorState is a JSON FILE written before this call:
#   fresh state:  kind="fresh", knownRollouts (every rollout-*.jsonl under
#                 -SessionsRoot immediately BEFORE dispatch)
#   resume state: kind="resume", rolloutFile, sessionId, bytes,
#                 prefixSha256 (the previous invocation's nextState)
#
# THE BYTE BOUNDARY IS THE CONTINUITY CHECK. Without it a STALE rollout -
# one this call never appended to - reads exactly like a fresh one, because
# the previous round's prompt is still in the file and still matches its own
# hash. Offsets are BYTE counts, not line counts: a prefix hash through a
# byte offset has one unambiguous definition.
#
# -ExpectedBriefSha256 is a HASH, not a brief file, because a file re-read
# after the call is mutable and would silently redefine the expected value.
# Its canonicalization is DECLARED, not incidental: UTF-8 bytes of the text
# with CRLF folded to LF and leading and trailing whitespace removed.
#
# Exit codes: 0 clean, 1 failed (reason on stdout, see -Json).
param(
    [Parameter(ParameterSetName = "Fresh", Mandatory = $true)]
    [switch]$Fresh,
    [Parameter(ParameterSetName = "Fresh", Mandatory = $true)]
    [string]$SessionsRoot,
    [Parameter(ParameterSetName = "Fresh", Mandatory = $true)]
    [string]$SessionIdFromStdout,

    [Parameter(ParameterSetName = "Resume", Mandatory = $true)]
    [switch]$Resume,
    [Parameter(ParameterSetName = "Resume", Mandatory = $true)]
    [string]$RolloutFile,

    [Parameter(Mandatory = $true)][string]$PriorState,
    [Parameter(Mandatory = $true)][string]$ExpectedBriefSha256,
    [switch]$Json
)

$ErrorActionPreference = "Stop"

function Write-Result($status, $reason, $nextState, $asJson) {
    if ($asJson) {
        $obj = [ordered]@{ status = $status }
        if ($reason) { $obj.reason = $reason }
        if ($nextState) { $obj.nextState = $nextState }
        Write-Output (ConvertTo-Json $obj -Compress -Depth 6)
    } else {
        if ($status -eq "clean") {
            Write-Output "clean"
        } else {
            Write-Output ("failed: " + $reason)
        }
    }
    if ($status -eq "clean") { exit 0 } else { exit 1 }
}

function Fail($reason) {
    Write-Result "failed" $reason $null $Json
}

function Get-Sha256Hex([byte[]]$bytes, [int]$offset, [int]$count) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        $h = $sha.ComputeHash($bytes, $offset, $count)
    } finally {
        $sha.Dispose()
    }
    ($h | ForEach-Object { $_.ToString("x2") }) -join ""
}

function Get-CanonicalSha256([string]$text) {
    # The declared canonicalization, in one place. Both this script and the
    # caller that computes -ExpectedBriefSha256 must apply the same rule, so
    # it is stated rather than left to whichever side reads the bytes first.
    $t = $text.Replace("`r`n", "`n").Trim()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($t)
    Get-Sha256Hex $bytes 0 $bytes.Length
}

# --------------------------------------------------------------------
# Argument shape. A caller that passes an unusable expected hash must be
# refused here: telling it the round is clean because nothing could be
# compared is precisely the permissive direction this script forbids.
# --------------------------------------------------------------------

if ($ExpectedBriefSha256 -notmatch '^[0-9a-f]{64}$') {
    Fail ("-ExpectedBriefSha256 is not a lowercase 64-character hex digest: '" +
          $ExpectedBriefSha256 + "'")
}

if (-not (Test-Path -LiteralPath $PriorState -PathType Leaf)) {
    Fail ("prior state file not found: " + $PriorState)
}

$priorText = $null
try {
    $priorText = [System.IO.File]::ReadAllText($PriorState)
} catch {
    Fail ("prior state file could not be read: " + $_.Exception.Message)
}

$prior = $null
try {
    $prior = $priorText | ConvertFrom-Json
} catch {
    Fail ("prior state file could not be parsed as JSON: " + $_.Exception.Message)
}

$wantKind = if ($Fresh) { "fresh" } else { "resume" }
if ($prior.kind -ne $wantKind) {
    Fail ("prior state kind is '" + [string]$prior.kind + "' but this call needs kind '" +
          $wantKind + "'")
}

# EVERY field this script compares against must be PRESENT, checked by
# name rather than by truthiness. An absent `knownRollouts` and a
# legitimately empty one are both falsy, so a truthiness test skipped the
# newly-created check exactly when nobody had made the inventory; an
# absent `bytes` casts to 0, which reads as "measure from the start of the
# file". Both are the permissive direction, and an unmade measurement is
# never a clean one.
function Assert-PriorField($name) {
    $present = @($prior.PSObject.Properties.Name) -contains $name
    if (-not $present) {
        Fail ("prior state is missing the required field '" + $name +
              "': the measurement it records was never made")
    }
}

if ($Fresh) {
    Assert-PriorField "knownRollouts"
} else {
    Assert-PriorField "rolloutFile"
    Assert-PriorField "sessionId"
    Assert-PriorField "bytes"
    Assert-PriorField "prefixSha256"
}

# --------------------------------------------------------------------
# Locate the rollout and establish the byte range THIS call appended.
# --------------------------------------------------------------------

function Get-RolloutSessionId([string]$name) {
    # rollout-<timestamp>-<session-id>.jsonl. The id is the tail because a
    # timestamp carries its own hyphens.
    if ($name -match '^rollout-.*-([0-9a-fA-F-]{36})\.jsonl$') { $Matches[1] } else { $null }
}

$targetFile = $null
$expectSessionId = $null
$sliceOffset = 0

if ($Fresh) {
    if (-not (Test-Path -LiteralPath $SessionsRoot -PathType Container)) {
        Fail ("sessions root not found: " + $SessionsRoot)
    }
    $expectSessionId = $SessionIdFromStdout

    # -Stop, never -SilentlyContinue: a swallowed enumeration error turns
    # "two rollouts, one unreadable" into "exactly one", which is the
    # ambiguity refusal reading as a clean binding.
    $all = @()
    try {
        $all = @(Get-ChildItem -LiteralPath $SessionsRoot -Recurse -File `
                    -Filter "rollout-*.jsonl" -ErrorAction Stop)
    } catch {
        Fail ("the sessions root could not be enumerated: " + $_.Exception.Message)
    }
    $matching = @($all | Where-Object {
        (Get-RolloutSessionId $_.Name) -eq $expectSessionId
    })
    if ($matching.Count -ne 1) {
        Fail ("expected exactly one rollout under the sessions root for session id " +
              $expectSessionId + ", found " + $matching.Count)
    }
    $targetFile = $matching[0].FullName

    # A pre-existing file bearing the right session id is not evidence that
    # THIS call produced it.
    $known = @($prior.knownRollouts | ForEach-Object {
        try { [System.IO.Path]::GetFullPath([string]$_) } catch { [string]$_ }
    })
    $normTarget = [System.IO.Path]::GetFullPath($targetFile)
    foreach ($k in $known) {
        if ($k -and ($k -ieq $normTarget)) {
            Fail ("the rollout for session id " + $expectSessionId +
                  " is not new: it was already present before this call")
        }
    }
    $sliceOffset = 0
} else {
    if (-not (Test-Path -LiteralPath $RolloutFile -PathType Leaf)) {
        Fail ("rollout file not found: " + $RolloutFile)
    }
    $targetFile = (Resolve-Path -LiteralPath $RolloutFile).ProviderPath
    $expectSessionId = [string]$prior.sessionId

    if ($prior.rolloutFile) {
        $statedFile = $null
        try { $statedFile = [System.IO.Path]::GetFullPath([string]$prior.rolloutFile) }
        catch { $statedFile = [string]$prior.rolloutFile }
        if (-not ($statedFile -ieq [System.IO.Path]::GetFullPath($targetFile))) {
            Fail ("prior state names a different rollout file: " + $statedFile)
        }
    }
}

$bytes = $null
try {
    $bytes = [System.IO.File]::ReadAllBytes($targetFile)
} catch {
    Fail ("rollout file could not be read: " + $_.Exception.Message)
}

if ($Resume) {
    $priorBytes = -1
    try { $priorBytes = [int]$prior.bytes } catch { $priorBytes = -1 }
    if ($priorBytes -lt 0) {
        Fail "prior state does not carry a usable byte offset"
    }
    if ($bytes.Length -lt $priorBytes) {
        Fail ("the rollout is shorter than the prior state records (" +
              $bytes.Length + " bytes now, " + $priorBytes + " before)")
    }
    $observedPrefix = Get-Sha256Hex $bytes 0 $priorBytes
    if ($observedPrefix -ne [string]$prior.prefixSha256) {
        Fail ("the rollout prefix changed since the prior state was captured; " +
              "the record this call appended to is not the one it measured")
    }
    if ($bytes.Length -eq $priorBytes) {
        Fail ("the rollout has no new bytes: this call appended nothing, so " +
              "there is no round to bind")
    }
    $sliceOffset = $priorBytes
}

# A final line with no terminating newline is a file still being written.
# Binding against it means reading a measurement that is not finished.
if ($bytes.Length -eq 0 -or $bytes[$bytes.Length - 1] -ne 0x0A) {
    Fail ("the rollout ends with an incomplete record: the last line has no " +
          "terminating newline")
}

# STRICT decode. [Encoding]::UTF8 substitutes U+FFFD for invalid bytes and
# never throws (measured 2026-08-04), so a corrupted slice whose damage sat
# outside the brief record reached a clean verdict while the contract said
# "strict UTF-8 JSONL". UTF8Encoding($false, $true) throws instead.
$sliceText = $null
try {
    $strict = New-Object System.Text.UTF8Encoding($false, $true)
    $sliceText = $strict.GetString(
        $bytes, $sliceOffset, ($bytes.Length - $sliceOffset))
} catch {
    Fail ("this call's slice does not decode as strict UTF-8: " +
          $_.Exception.Message)
}

if ($sliceText.Length -gt 0 -and [int][char]$sliceText[0] -eq 0xFEFF) {
    if ($sliceOffset -eq 0) {
        # A byte order mark at the start of the file is a file-level
        # artifact and not part of any record.
        $sliceText = $sliceText.Substring(1)
    } else {
        Fail ("this call's slice begins with a byte order mark: the bytes " +
              "appended do not start where the prior state recorded")
    }
}

$parts = $sliceText.Split("`n")
# The split's final element is the empty tail after the terminating newline
# checked above, never a record.
$lines = @()
for ($i = 0; $i -lt $parts.Length - 1; $i++) {
    $lines += ,($parts[$i].TrimEnd("`r"))
}

$records = @()
for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i].Trim() -eq "") {
        Fail ("rollout line " + ($i + 1) + " of this call's slice is blank; " +
              "the record stream is not intact")
    }
    $rec = $null
    try {
        $rec = $lines[$i] | ConvertFrom-Json
    } catch {
        Fail ("rollout line " + ($i + 1) + " of this call's slice could not be " +
              "parsed as JSON: " + $_.Exception.Message)
    }
    # `null`, a bare scalar and an array are all valid JSON and none is a
    # record. Ignoring them silently is lenience under a strict-parse claim.
    if (-not ($rec -is [System.Management.Automation.PSCustomObject])) {
        Fail ("rollout line " + ($i + 1) + " of this call's slice is not a " +
              "JSON object")
    }
    $records += ,$rec
}

# --------------------------------------------------------------------
# Session identity. The filename and the session_meta record must AGREE.
# Checking only the name would let a renamed or swapped file pass on its
# label, which is not evidence about what the client wrote.
# --------------------------------------------------------------------

$nameId = Get-RolloutSessionId ([System.IO.Path]::GetFileName($targetFile))
if (-not $nameId) {
    Fail ("the rollout filename does not carry a session id: " +
          [System.IO.Path]::GetFileName($targetFile))
}

if ($Fresh) {
    $metaRecords = @($records | Where-Object { $_.type -eq "session_meta" })
    if ($metaRecords.Count -lt 1) {
        Fail "the fresh rollout carries no session_meta record"
    }
    $metaId = [string]$metaRecords[0].payload.id
    if ($metaId -ne $nameId -or $metaId -ne $expectSessionId) {
        Fail ("the session id disagrees across sources: filename '" + $nameId +
              "', session_meta '" + $metaId + "', dispatch '" + $expectSessionId + "'")
    }
} else {
    if ($nameId -ne $expectSessionId) {
        Fail ("the session id disagrees across sources: filename '" + $nameId +
              "', prior state '" + $expectSessionId + "'")
    }
}

# --------------------------------------------------------------------
# The brief. Exactly one user record in THIS call's slice must equal the
# declared brief, and it must be the LAST one: an extra prompt after it
# means something other than this driver put text in front of the
# reviewer, and the reply cannot be attributed to the brief alone.
# --------------------------------------------------------------------

function Get-UserText($record) {
    # Content elements are joined IN ORDER. The measured sample carried
    # one-element briefs, so a reader taking content[0] would pass every
    # observed round and silently drop the tail of any brief the client
    # chose to split.
    #
    # EVERY element must be `input_text` for the record to be a binding
    # candidate. Hashing only the text elements would bind a record that
    # also carried something else - wider than the frozen rule, and wider
    # than anything measured. A non-candidate returns $null and can never
    # match.
    $elements = @($record.payload.content)
    if ($elements.Count -lt 1) { return $null }
    $sb = New-Object System.Text.StringBuilder
    foreach ($el in $elements) {
        if (-not $el -or $el.type -ne "input_text") { return $null }
        [void]$sb.Append([string]$el.text)
    }
    $sb.ToString()
}

$userRecords = @($records | Where-Object {
    $_.type -eq "response_item" -and $_.payload -and
    $_.payload.type -eq "message" -and $_.payload.role -eq "user"
})

if ($userRecords.Count -lt 1) {
    Fail ("this call's slice carries no user record, so there is no recorded " +
          "prompt to bind the brief to")
}

# A RESUMED slice carried exactly one user record on every measured round:
# the resume payload. There is no instructions preamble to make room for,
# so a second one is unexplained and the round is not attributable. A FRESH
# slice always carries at least two, which is why this bound is resume-only.
if ($Resume -and $userRecords.Count -ne 1) {
    Fail ("a resumed slice must carry exactly one user record, found " +
          $userRecords.Count)
}

$matchIndexes = @()
for ($i = 0; $i -lt $userRecords.Count; $i++) {
    $text = Get-UserText $userRecords[$i]
    if ($null -ne $text -and (Get-CanonicalSha256 $text) -eq $ExpectedBriefSha256) {
        $matchIndexes += ,$i
    }
}

if ($matchIndexes.Count -eq 0) {
    Fail ("the recorded prompt does not match the declared brief: no user " +
          "record in this call's slice hashes to " + $ExpectedBriefSha256)
}
if ($matchIndexes.Count -gt 1) {
    Fail ("the brief is ambiguous: " + $matchIndexes.Count + " user records in " +
          "this call's slice hash to the declared brief")
}
if ($matchIndexes[0] -ne ($userRecords.Count - 1)) {
    Fail ("the brief is not the last user record in this call's slice: " +
          ($userRecords.Count - 1 - $matchIndexes[0]) +
          " further user record(s) follow it")
}

# --------------------------------------------------------------------
# Clean. nextState is what the NEXT round resumes from, so the boundary
# is carried forward by the same script that established it.
# --------------------------------------------------------------------

$next = [ordered]@{
    kind         = "resume"
    rolloutFile  = $targetFile
    sessionId    = $expectSessionId
    bytes        = $bytes.Length
    prefixSha256 = (Get-Sha256Hex $bytes 0 $bytes.Length)
}

Write-Result "clean" $null $next $Json
