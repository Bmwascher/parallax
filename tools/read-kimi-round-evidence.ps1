# read-kimi-round-evidence.ps1 - validate one kimi-code debate round's OWN
# session files against the declared model, agent and tool set, and decide
# whether the round can be attributed to them at all.
#
# WHY THIS EXISTS. If this script says clean, a human trusts the review. If
# it is wrong in the permissive direction, an unverified round reads as
# verified. Every rule below is written to fail closed: an unmade, failed,
# or unreadable measurement is never reported as a clean one.
#
# TWO PARAMETER SETS, because a fresh call must DISCOVER the session
# directory (it does not exist before the client creates it) and a resume
# must be TOLD it. A single -SessionDir signature would ask the fresh
# branch for the very thing it exists to establish.
#
#   Fresh:  -Fresh -SessionsRoot <dir> -SessionIdFromStdout <id>
#           -PriorState <json-file> -Model <id> -Provider <name>
#           -Effort <level> -AgentFile <path> -ExpectedBriefSha256 <hex>
#           [-Json]
#   Resume: -Resume -SessionDir <dir>
#           -PriorState <json-file> -Model <id> -Provider <name>
#           -Effort <level> -AgentFile <path> -ExpectedBriefSha256 <hex>
#           [-Json]
#
# Passing a fresh-only argument to the resume set, or the reverse, is a
# parameter-binding error (PowerShell's own parameter-set resolution),
# never a runtime check.
#
# -PriorState is a JSON FILE, written by the previous invocation's
# nextState (or, for round 1, by the pre-dispatch capture step). Its shape
# depends on the kind of call it describes:
#   Fresh state:  kind="fresh", knownSessionDirs (the session-LEAF
#                 directories under -SessionsRoot immediately before this
#                 dispatch - a member is a directory whose name begins
#                 "session_", and nothing else; the "wd_<workspace>"
#                 container a debate's first call also creates is never a
#                 member).
#   Resume state: kind="resume", sessionDir, sessionId, wireBytes,
#                 logBytes, wirePrefixSha256, logPrefixSha256, toolsHash,
#                 systemPromptHash.
#
# -ExpectedBriefSha256 is a HASH, not a brief file, because a file re-read
# after the call is mutable and would silently redefine the expected
# value.
#
# Offsets are BYTE counts, not line counts, for both files - a prefix hash
# over raw bytes through a byte offset has one unambiguous definition.
#
# TOOLCOUNT is checked for EXACT equality against the -AgentFile allowlist
# length, on BOTH kinds of slice - the frozen plan's rule 13 text, verbatim.
# Fix round 1 history, for anyone reading this later: Task 6's first pass
# measured toolCount=4 against a 5-tool allowlist and loosened this to an
# upper bound, reasoning that a runtime vision-capability gate excluded
# ReadMediaFile from the sent schema. That measurement was of a DEFECT in
# tools/new-kimi-lane-home.ps1, not of client behavior: the home builder was
# hand-writing the model table and omitting the `capabilities` and
# `support_efforts` keys the real config declares. Without them, thinking
# has nothing to resolve against (toolCount 4, thinkingEffort "off"); with
# them (fixed at commit b645810, carrying the real model table verbatim),
# toolCount is 5 and thinkingEffort resolves to the configured value - both
# measured live, twice, once per state, same agent file and model. The
# loosened bound was quietly dangerous on its own terms, independent of
# whether the measurement behind it was right: a resume slice carries no
# llm.tools_snapshot at all, so on resume the bound was the ONLY tool-count
# check, and it would have passed a round running with as few as one tool.
# Fix round 2: fix round 1 also kept a fresh-only cross-check here (toolCount
# vs llm.tools_snapshot.tools.Count "as an ADDITIONAL check"). Removed: it
# could never fail on its own, because rule 12's snapshot tool-NAME equality
# already forces the counts equal first. A check that cannot fail is exactly
# the defect class this rule exists to prevent.
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
    [string]$SessionDir,

    [Parameter(Mandatory = $true)][string]$PriorState,
    [Parameter(Mandatory = $true)][string]$Model,
    [Parameter(Mandatory = $true)][string]$Provider,
    [Parameter(Mandatory = $true)][string]$Effort,
    [Parameter(Mandatory = $true)][string]$AgentFile,
    [Parameter(Mandatory = $true)][string]$ExpectedBriefSha256,
    [string]$SealedPriorStateSha256,
    [switch]$Json
)

$ErrorActionPreference = "Stop"

$Kind = if ($Fresh) { "fresh" } else { "resume" }

# "not-checked" until a supplied -SealedPriorStateSha256 is confirmed
# against the raw bytes of -PriorState. Set before any Fail() can run, so
# an unmade check never reports through a variable that still carries a
# stale "sealed" value from nowhere.
$script:Sealed = "not-checked"

function Write-Result($status, $reason, $nextState, $asJson) {
    if ($asJson) {
        $obj = [ordered]@{ status = $status }
        if ($reason) { $obj.reason = $reason }
        if ($nextState) { $obj.nextState = $nextState }
        $obj.sealed = $script:Sealed
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

$Sha256Rx = '^[0-9a-f]{64}$'

function Test-Sha256Hex($s) {
    return ($s -is [string]) -and ($s -match $Sha256Rx)
}

function ConvertTo-NormalizedLF($s) {
    return ([string]$s) -replace "`r`n", "`n"
}

function ConvertTo-CanonicalBrief($s) {
    # ONE canonicalization for a brief, shared with the codex lane's
    # Get-CanonicalText: UTF-8, CRLF folded to LF, leading and trailing
    # whitespace stripped. Kept SEPARATE from ConvertTo-NormalizedLF
    # rather than added to it: its four agent-file callers compare an
    # agent file's BODY and the client's recorded systemPrompt, where
    # the ends are content and trimming them would widen a different
    # rule. Its one remaining caller is the untrimmed re-hash on the
    # mismatch path below, which is untrimmed by design. Item 52.
    return (ConvertTo-NormalizedLF $s).Trim()
}

function Get-Sha256HexOfBytes($bytes) {
    # An explicit [byte[]] cast on a POSSIBLY-EMPTY or POSSIBLY-Object[]
    # value, taken INSIDE the function rather than trusted from the
    # caller: `$x = if ($cond) {...} else { @() }` silently collapses to
    # $null in PowerShell (confirmed live), and ComputeHash($null) throws
    # "ambiguous overloads" rather than hashing zero bytes. Get-BytePrefix
    # below is the caller-side fix; this cast is the belt-and-braces one.
    #
    # AND THE CAST ALONE DID THE OPPOSITE OF WHAT THE LINE ABOVE CLAIMS.
    # `@($null)` is a ONE-element array holding $null, and `[byte[]]` turns
    # that element into 0x00 - so an empty value hashed ONE ZERO BYTE
    # rather than zero bytes. Measured 2026-08-17 with the script
    # instrumented: an empty brief produced
    # 6e340b9cffb37a989ca544e6bb780a2c78901d3fb33738768511a30617afa01d,
    # which is SHA-256 of `0x00`, where SHA-256 of nothing is
    # e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855.
    # PowerShell UNROLLS an empty array through a function return, so
    # every caller here hands this function $null for an empty sequence
    # however carefully the caller built it. $null and an empty array are
    # therefore the SAME INPUT at this boundary and both mean zero bytes.
    # Found while reproducing round 5 of the 0.26.0 diff debate; neither
    # side named it.
    if ($null -eq $bytes) {
        $safeBytes = New-Object byte[] 0
    } else {
        $safeBytes = [byte[]]@($bytes)
    }
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return ([System.BitConverter]::ToString($sha.ComputeHash($safeBytes)) `
            -replace '-', '').ToLowerInvariant()
    } finally {
        $sha.Dispose()
    }
}

function Get-BytePrefix([byte[]]$all, [long]$n) {
    # `$all[0..($n-1)]` for n=0 need never be evaluated - a negative
    # range crashes - and the $null-collapse bug above means the natural
    # `if ($n -gt 0) {...} else { @() }` shape cannot be trusted either.
    if ($n -le 0) { return New-Object byte[] 0 }
    if ($null -eq $all -or $all.Length -eq 0) { return New-Object byte[] 0 }
    return $all[0..($n - 1)]
}

# Decodes evidence bytes as STRICT UTF-8. `[System.Text.Encoding]::UTF8`
# and `Get-Content -Encoding UTF8` both substitute U+FFFD per invalid
# byte, so a corrupt byte inside an unused JSON string, or after a matched
# log prefix, became a replacement character while the surrounding text
# still parsed and reported CLEAN. This tool's own invariant is that
# unreadable evidence never reports clean, so a decode failure is a
# FAILURE, not a repaired string. Returns $null on failure; every caller
# maps that to its own existing fail reason rather than inventing one.
#
# -StripBom is passed by the two WHOLE-FILE readers only, because
# `Get-Content -Encoding UTF8` stripped a leading BOM and they used it.
# The wire and log SLICES do not pass it: their old path was a direct
# `GetString`, which kept the BOM character, and this change is not the
# place to start tolerating one. Each path keeps exactly the BOM behaviour
# it had.
#
# The recorded byte offsets and prefix hashes are computed from RAW FILE
# BYTES and therefore include any BOM. Nothing here changes that, and an
# earlier version of this comment claimed the opposite.
function ConvertFrom-StrictUtf8([byte[]]$bytes, [switch]$StripBom) {
    if ($null -eq $bytes) { return "" }
    $text = $null
    try {
        $text = (New-Object System.Text.UTF8Encoding($false, $true)).GetString($bytes)
    } catch {
        return $null
    }
    if ($StripBom -and $text.Length -gt 0 -and [int]$text[0] -eq 0xFEFF) {
        $text = $text.Substring(1)
    }
    return $text
}

$script:JsonWs = [char[]]@(' ', "`t", "`r", "`n")

# A DELIBERATE COPY of `Get-JsonObjectLineFault` in
# `tools/read-codex-round-evidence.ps1`, comments and all. The two
# binders are standalone scripts invoked by path, with no shared module
# between them, and this repository already carries the same duplication
# for the canonicalization helpers. CHANGE BOTH. Round 4 of the 0.26.0
# diff debate found this lane had no object-root gate at all, and two of
# its four findings were CLEAN on PowerShell 7 and refused on 5.1 for
# exactly the reason the copied comments describe.

function Get-JsonObjectLineFault([string]$raw, $parsed) {
    # Returns $null when the line is a lone JSON object, else a phrase
    # naming the fault. Two faults, and an operator has to be able to
    # tell them apart: one says the value is the wrong kind, the other
    # says something rode in behind a value of the right kind.
    # A JSONL RECORD IS AN OBJECT, AND `-is [PSCustomObject]` DOES NOT
    # ESTABLISH THAT ON EVERY HOST. Measured 2026-08-04 on
    # `'[{"type":"session_meta",...}]' | ConvertFrom-Json`:
    #   Windows PowerShell 5.1 returns System.Object[] - the type test
    #     catches it.
    #   PowerShell 7.6.3 UNROLLS the single-element array and returns the
    #     PSCustomObject inside it - the type test cannot see it, and the
    #     line's properties then read straight through.
    # So the shipped slice parser's object check, and the resume
    # first-line check added hours earlier, both passed a JSON ARRAY on
    # PowerShell 7 while refusing it on 5.1. That is the 0.16.0 lane-lock
    # class this repo runs two host jobs for: a green suite on one
    # interpreter proves one interpreter.
    # The RAW TEXT decides instead. A JSON object begins with `{`, on
    # every host, and combined with a successful parse that is the whole
    # rule.
    # AND `ConvertFrom-Json` IS NOT A STRICT-JSON GATE EITHER. Measured
    # 2026-08-04: `{"type":"note"} // tail` is ACCEPTED on PowerShell
    # 7.6.3 and refused on 5.1, because 7's parser allows JSON comments.
    # Arbitrary trailing text and a second object are refused on both, so
    # the divergence is comments specifically - narrow, and still enough
    # to make the contract's strict-JSONL claim false on one interpreter.
    # Delegating strictness to the parser is what went wrong; the scan
    # below decides here, the same way for every host.
    if ($null -eq $raw) { return "is not a JSON object" }
    # JSON WHITESPACE ONLY. `.Trim()` strips Unicode whitespace, and both
    # hosts accept a trailing U+00A0 after the value (measured
    # 2026-08-04), so the tail check erased exactly the character it was
    # supposed to catch. JSON defines whitespace as these four.
    $t = $raw.Trim($script:JsonWs)
    if (-not $t.StartsWith("{")) { return "is not a JSON object" }
    if (-not ($parsed -is [System.Management.Automation.PSCustomObject])) {
        return "is not a JSON object"
    }
    # Nothing but whitespace may follow the object's own closing brace.
    # The parse already established well-formed JSON, so this only has to
    # find where the value ends: track string literals so a brace inside
    # one is not counted, and escapes so a quote inside one is not.
    $depth = 0; $inStr = $false; $esc = $false; $end = -1
    for ($i = 0; $i -lt $t.Length; $i++) {
        $c = $t[$i]
        if ($inStr) {
            if ($esc) { $esc = $false }
            elseif ($c -eq '\') { $esc = $true }
            elseif ($c -eq '"') { $inStr = $false }
            continue
        }
        if ($c -eq '"') { $inStr = $true; continue }
        # NO `/` IS LEGAL OUTSIDE A JSON STRING, so one can only begin a
        # comment. PowerShell 7.6.3 accepts comments INSIDE an object as
        # well as after it (measured 2026-08-04; 5.1 refuses both), and a
        # brace-depth scan with no comment state cannot see them - worse,
        # a `}` or `"` inside a comment misleads the scan itself. Refusing
        # the character is exact, host-independent, and cheaper than
        # tracking comment state.
        if ($c -eq '/') { return "carries a comment, which strict JSON has no room for" }
        if ($c -eq '{') { $depth++; continue }
        if ($c -eq '}') {
            $depth--
            if ($depth -eq 0) { $end = $i; break }
        }
    }
    if ($end -lt 0) { return "is not a JSON object" }
    if ($t.Substring($end + 1).Trim($script:JsonWs) -ne "") {
        return "carries trailing content after its JSON value"
    }
    return $null
}

# ONE place decides whether an object carries a key, so ONE mutation
# covers every shape branch below. -ccontains is case-EXACT: PowerShell's
# -contains is not, and its property ACCESS is not either, so a record
# carrying `Provider` satisfied a required `provider` twice over.
function Test-HasKey($obj, [string]$name) {
    return (@($obj.PSObject.Properties.Name) -ccontains $name)
}

function Get-ByteSuffix([byte[]]$all, [long]$offset) {
    # Bytes from $offset to the end. PowerShell's `..` range operator
    # counts DOWN when its left operand exceeds its right: an offset
    # exactly equal to the array's length (the empty-slice-at-EOF case,
    # not an error - a resume validated right after its own prior call)
    # would otherwise evaluate `length..(length-1)`, a descending
    # 2-element range that indexes one element past the end. Handled as
    # its own case, not inferred from what the general branch happens to
    # do with it.
    if ($null -eq $all -or $all.Length -eq 0) { return New-Object byte[] 0 }
    if ($offset -ge $all.Length) { return New-Object byte[] 0 }
    if ($offset -le 0) { return $all }
    return $all[$offset..($all.Length - 1)]
}

function Get-Utf8BytesNoBom($s) {
    $enc = New-Object System.Text.UTF8Encoding($false)
    return $enc.GetBytes([string]$s)
}

function Resolve-PathSafe($p) {
    # Canonicalizes a path so a directory spelled with forward slashes and
    # the SAME directory spelled with backslashes compare equal. Falls
    # back to the input unchanged if the path does not (yet, or ever)
    # exist - Resolve-Path throws on a missing path, and "not found" is a
    # different failure than "found but spelled differently", so callers
    # still see a clean miss rather than this function inventing one.
    if (-not $p) { return $p }
    try { return (Resolve-Path -LiteralPath $p -ErrorAction Stop).Path } catch { return $p }
}

# ---------------------------------------------------------------------
# Rule 1: -PriorState must be readable JSON, well-typed for ITS OWN
# declared kind. This function validates ONLY: (a) the file is readable
# JSON, (b) `kind` is present and is "fresh" or "resume", (c) every field
# that IS present has the right type for that kind's schema. It does NOT
# require every field of the OTHER kind's schema to be absent, and it does
# NOT require every field of ITS OWN kind's schema to be present - both of
# those are rule 4's job (state-inconsistent), so that "a resume state
# missing an offset" and "a fresh state carrying a sessionDir" are
# reachable as state-inconsistent rather than being swallowed here first.
# ---------------------------------------------------------------------
function Read-PriorState($path) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        Fail "prior-state-unusable: -PriorState file not found: $path"
    }
    $raw = $null
    try {
        $raw = ConvertFrom-StrictUtf8 ([System.IO.File]::ReadAllBytes($path)) -StripBom
    } catch {
        Fail ("prior-state-unusable: could not read -PriorState: " + $_.Exception.Message)
    }
    if ($null -eq $raw) {
        Fail "prior-state-unusable: -PriorState is not valid UTF-8"
    }
    $obj = $null
    try {
        $obj = $raw | ConvertFrom-Json -ErrorAction Stop
    } catch {
        Fail ("prior-state-unusable: -PriorState is not valid JSON: " + $_.Exception.Message)
    }
    if ($null -eq $obj) {
        Fail "prior-state-unusable: -PriorState parsed to null"
    }
    # THE RAW TEXT DECIDES WHAT THE ROOT WAS, not the parser. Measured
    # 2026-08-16: a state wrapped in a one-element JSON array bound CLEAN
    # on PowerShell 7, which UNROLLS the singleton and hands back the
    # object inside it, and was refused on 5.1, which does not. Every
    # shape check below then passed on a root the document never
    # declared. Found by round 4 of the 0.26.0 diff debate.
    $rootFault = Get-JsonObjectLineFault $raw $obj
    if ($rootFault) {
        Fail ("prior-state-unusable: -PriorState " + $rootFault +
              " at its root, so the fields read from it are not the " +
              "fields it declares")
    }
    $propNames = @($obj.PSObject.Properties.Name)
    if (-not (Test-HasKey $obj "kind")) {
        Fail "prior-state-unusable: -PriorState has no 'kind' field"
    }
    if (-not ($obj.kind -is [string]) -or
        ($obj.kind -cne "fresh" -and $obj.kind -cne "resume")) {
        Fail "prior-state-unusable: -PriorState.kind is not 'fresh' or 'resume'"
    }

    if ($obj.kind -ceq "fresh") {
        if (-not (Test-HasKey $obj "knownSessionDirs")) {
            Fail "prior-state-unusable: fresh -PriorState has no knownSessionDirs"
        }
        $known = $obj.knownSessionDirs
        # A JSON array of zero or many elements survives ConvertFrom-Json
        # as System.Object[]; only the SINGLE-element case can collide
        # with a bare scalar, and even then only when the value came
        # through the PIPELINE rather than a property access - reading it
        # as a property (as here) keeps a one-element array an array.
        if (-not ($known -is [array])) {
            Fail "prior-state-unusable: fresh -PriorState.knownSessionDirs is not a list"
        }
        foreach ($d in @($known)) {
            if (-not ($d -is [string])) {
                Fail "prior-state-unusable: fresh -PriorState.knownSessionDirs contains a non-string entry"
            }
        }
    } else {
        # Every field PRESENT must be well-typed. Absence of a required
        # resume field is rule 4's job (state-inconsistent), not rule 1's.
        if ((Test-HasKey $obj "sessionDir") -and -not ($obj.sessionDir -is [string])) {
            Fail "prior-state-unusable: resume -PriorState.sessionDir is not a string"
        }
        if ((Test-HasKey $obj "sessionId") -and -not ($obj.sessionId -is [string])) {
            Fail "prior-state-unusable: resume -PriorState.sessionId is not a string"
        }
        foreach ($f in @("wireBytes", "logBytes")) {
            if (Test-HasKey $obj $f) {
                $v = $obj.$f
                if (-not (($v -is [int]) -or ($v -is [long]))) {
                    Fail "prior-state-unusable: resume -PriorState.$f is not an integer"
                }
                if ($v -lt 0) {
                    Fail "prior-state-unusable: resume -PriorState.$f is negative"
                }
            }
        }
        foreach ($f in @("wirePrefixSha256", "logPrefixSha256", "toolsHash", "systemPromptHash")) {
            if (Test-HasKey $obj $f) {
                if (-not (Test-Sha256Hex $obj.$f)) {
                    Fail "prior-state-unusable: resume -PriorState.$f is not a 64-character hex hash"
                }
            }
        }
    }
    return $obj
}

# ---------------------------------------------------------------------
# Rule 5: -AgentFile parsing.
# ---------------------------------------------------------------------
function Get-AgentFileInfo($path) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        Fail "agent-file-unusable: -AgentFile not found: $path"
    }
    $raw = $null
    try {
        $raw = ConvertFrom-StrictUtf8 ([System.IO.File]::ReadAllBytes($path)) -StripBom
    } catch {
        Fail ("agent-file-unusable: could not read -AgentFile: " + $_.Exception.Message)
    }
    if ($null -eq $raw) {
        Fail "agent-file-unusable: -AgentFile is not valid UTF-8"
    }
    $norm = ConvertTo-NormalizedLF $raw
    # ORDINAL. .NET's default String.StartsWith is CULTURE-SENSITIVE and
    # silently ignores zero-width characters, so a BOM-prefixed agent file
    # satisfied this marker check even when the BOM was still in the
    # string - measured. A structural marker check must compare bytes as
    # written, not as a collator sees them.
    if (-not $norm.StartsWith("---`n", [System.StringComparison]::Ordinal)) {
        Fail "agent-file-unusable: -AgentFile does not open with a --- frontmatter marker"
    }
    $rest = $norm.Substring(4)
    $closeIdx = $rest.IndexOf("`n---`n", [System.StringComparison]::Ordinal)
    if ($closeIdx -lt 0) {
        Fail "agent-file-unusable: -AgentFile frontmatter never closes with ---"
    }
    $front = $rest.Substring(0, $closeIdx)
    $body = $rest.Substring($closeIdx + 5).Trim()

    $nameMatch = [regex]::Match($front, '(?m)^name:\s*(\S.*)$')
    if (-not $nameMatch.Success) {
        Fail "agent-file-unusable: -AgentFile frontmatter has no name field"
    }
    $name = $nameMatch.Groups[1].Value.Trim()

    function Get-YamlList($frontText, $key) {
        $pattern = '(?m)^' + [regex]::Escape($key) + ':[ \t]*$(?:(?:\r?\n[ \t]+-[^\r\n]*))*'
        $m = [regex]::Match($frontText, $pattern)
        if (-not $m.Success) { return $null }
        $items = New-Object System.Collections.ArrayList
        foreach ($line in ($m.Value -split "`n")) {
            $t = $line.TrimEnd("`r")
            $im = [regex]::Match($t, '^[ \t]+-\s*(\S.*)$')
            if ($im.Success) { [void]$items.Add($im.Groups[1].Value.Trim()) }
        }
        return @($items)
    }

    $tools = Get-YamlList $front "tools"
    $disallowed = Get-YamlList $front "disallowedTools"
    if ($null -eq $tools -or $null -eq $disallowed) {
        Fail "agent-file-unusable: -AgentFile frontmatter has no tools/disallowedTools list"
    }
    if (-not $name -or $body.Length -eq 0) {
        Fail "agent-file-unusable: -AgentFile has an empty name or body"
    }
    return @{ Name = $name; Tools = @($tools); DisallowedTools = @($disallowed); Body = $body }
}

# ---------------------------------------------------------------------
# Rule 3 (fresh branch): enumerate session-LEAF directories.
# ---------------------------------------------------------------------
function Get-SessionLeaves($root) {
    if (-not (Test-Path -LiteralPath $root -PathType Container)) {
        return @()
    }
    $leaves = New-Object System.Collections.ArrayList
    # A member is a directory whose name begins "session_", found at ANY
    # depth under -SessionsRoot (the measured topology nests leaves one
    # level under a "wd_<workspace>" container, which is itself never a
    # member).
    #
    # The enumeration is TERMINATING. It was -ErrorAction SilentlyContinue,
    # which made a partly failed walk indistinguishable from a complete one:
    # rule 3 requires EXACTLY ONE new leaf, so an unreadable subtree holding
    # a second, concurrent session simply went uncounted and the round
    # passed on an inventory that was never taken. An unmade measurement is
    # never a clean one, so a failure here is a Fail, not a shorter list.
    try {
        Get-ChildItem -LiteralPath $root -Recurse -Directory -ErrorAction Stop |
            Where-Object { $_.Name.StartsWith("session_", [System.StringComparison]::Ordinal) } |
            ForEach-Object { [void]$leaves.Add($_.FullName) }
    } catch {
        Fail ("session-inventory-unreadable: enumerating -SessionsRoot failed: " +
              $_.Exception.Message)
    }
    return @($leaves)
}

# ---------------------------------------------------------------------
# Record-shape validation (rule 10's "record-malformed").
# ---------------------------------------------------------------------
function Test-TurnPromptShape($rec) {
    if (-not (Test-HasKey $rec "input")) { return $false }
    if (-not ($rec.input -is [array])) { return $false }
    # AT LEAST ONE ELEMENT. An empty array satisfied every line below by
    # running the loop zero times, so the record passed a shape test
    # having had no text measured at all - the contract hashes the
    # recorded prompt THROUGH these elements, so a record with none of
    # them carries no prompt. Round 5 of the 0.26.0 diff debate.
    if (@($rec.input).Count -lt 1) { return $false }
    foreach ($item in @($rec.input)) {
        if (-not (Test-HasKey $item "text")) { return $false }
        if (-not ($item.text -is [string])) { return $false }
    }
    return $true
}

function Test-LlmRequestShape($rec) {
    foreach ($f in @("provider", "model", "modelAlias", "thinkingEffort",
                     "toolsHash", "systemPromptHash")) {
        if (-not (Test-HasKey $rec $f)) { return $false }
        if (-not ($rec.$f -is [string])) { return $false }
    }
    return $true
}

function Test-ToolsSnapshotShape($rec) {
    if (-not (Test-HasKey $rec "hash")) { return $false }
    if (-not ($rec.hash -is [string])) { return $false }
    if (-not (Test-HasKey $rec "tools")) { return $false }
    if (-not ($rec.tools -is [array])) { return $false }
    # Every ELEMENT, not just the array wrapper: a tool entry missing its
    # `name`, or a bare string in place of an object, both used to reach
    # rule 12's `Compare-Object` unvalidated. Under this script's own
    # $ErrorActionPreference = "Stop" that throws a raw binding error
    # instead of Fail-ing record-malformed; measured WITHOUT that
    # preference, the same expression instead evaluates to a 0-count diff
    # - a silent PASS on the equality that rule 12 exists to enforce. Both
    # failure modes are closed by validating the element shape here,
    # before rule 12 ever runs.
    foreach ($t in @($rec.tools)) {
        if ($null -eq $t) { return $false }
        if (-not (Test-HasKey $t "name")) { return $false }
        if (-not ($t.name -is [string])) { return $false }
    }
    return $true
}

function Test-ActiveToolsShape($rec) {
    foreach ($f in @("names", "disallowedNames")) {
        if (-not (Test-HasKey $rec $f)) { return $false }
        if (-not ($rec.$f -is [array])) { return $false }
        foreach ($n in @($rec.$f)) { if (-not ($n -is [string])) { return $false } }
    }
    return $true
}

function Test-ConfigUpdateShape($rec) {
    $names = @($rec.PSObject.Properties.Name)
    $isFirst = (Test-HasKey $rec "profileName") -or (Test-HasKey $rec "systemPrompt")
    $isSecond = (Test-HasKey $rec "modelAlias") -or (Test-HasKey $rec "thinkingEffort")
    # EXACTLY ONE GROUP. This returned true for a record carrying
    # NEITHER, which is a shape test that passes on a record with no
    # shape. Measured 2026-08-16: merge both groups into the first
    # config.update and empty the second, and the count stays at two,
    # both shape counts stay at one, and every value comparison reads
    # the SAME record while the other one measures nothing. Round 4 of
    # the diff debate.
    #
    # NEITHER is refused; BOTH is not, and that is deliberate. The
    # reviewer asked for an exclusive-or. Measured instead: a record
    # carrying BOTH groups is already caught downstream every way it can
    # be arranged - the caller counts records by which group they carry
    # and needs exactly one of each, so a both-groups record pushes one
    # of those counts to two unless the OTHER record carries neither,
    # which is the case this line now refuses. An exclusive-or is
    # therefore no stronger here, and it made an existing case
    # (`test_two_copies_of_second_config_update_shape_fails`) refuse at
    # this shape test instead of at the count check it exists to reach,
    # which would have hidden that check behind this one.
    if (-not ($isFirst -or $isSecond)) { return $false }
    if ($isFirst) {
        if (-not ((Test-HasKey $rec "profileName") -and ($rec.profileName -is [string]))) { return $false }
        if (-not ((Test-HasKey $rec "systemPrompt") -and ($rec.systemPrompt -is [string]))) { return $false }
    }
    if ($isSecond) {
        if (-not ((Test-HasKey $rec "modelAlias") -and ($rec.modelAlias -is [string]))) { return $false }
        if (-not ((Test-HasKey $rec "thinkingEffort") -and ($rec.thinkingEffort -is [string]))) { return $false }
    }
    return $true
}

function Test-PermissionModeShape($rec) {
    if (-not (Test-HasKey $rec "mode")) { return $false }
    return ($rec.mode -is [string])
}

# ---------------------------------------------------------------------
# Rules 10-11: read the wire slice past the byte offset, parse lines,
# validate structure, check the slice-boundary record.
# ---------------------------------------------------------------------
function Read-WireSlice($wirePath, $offset, $expectedFirstType) {
    $bytes = [System.IO.File]::ReadAllBytes($wirePath)
    $sliceBytes = Get-ByteSuffix $bytes $offset
    $text = ConvertFrom-StrictUtf8 $sliceBytes
    if ($null -eq $text) {
        Fail "wire-malformed: the wire slice is not valid UTF-8"
    }
    $lines = @($text -split "`n" | Where-Object { $_.TrimEnd("`r").Trim().Length -gt 0 })
    $records = New-Object System.Collections.ArrayList
    foreach ($line in $lines) {
        $clean = $line.TrimEnd("`r")
        $rec = $null
        try {
            $rec = $clean | ConvertFrom-Json -ErrorAction Stop
        } catch {
            Fail "wire-malformed: a line in the wire slice is not valid JSON"
        }
        if ($null -eq $rec -or -not (Test-HasKey $rec "type")) {
            Fail "wire-malformed: a wire record has no type field"
        }
        # THE SAME TWO SHAPE QUESTIONS AS THE PRIOR STATE, one layer
        # down, and both were unasked. A line wrapped in a one-element
        # array bound CLEAN on PowerShell 7 and was refused on 5.1; and a
        # `type` given as an ARRAY bound clean on BOTH, because presence
        # was checked and kind was not, so `switch -CaseSensitive` below
        # enumerates the array into its shape branch and the per-type
        # `-ceq` counts treat the matching array as truthy. Measured
        # 2026-08-16, round 4 of the diff debate.
        $recFault = Get-JsonObjectLineFault $clean $rec
        if ($recFault) {
            Fail ("wire-malformed: a line in the wire slice " + $recFault)
        }
        if (-not ($rec.type -is [string])) {
            Fail "wire-malformed: a wire record's type is not a string"
        }
        $shapeOk = $true
        # -CaseSensitive here is CONSISTENCY, not a load-bearing check, and
        # it is written down as such rather than claimed: a case-variant
        # type falls to `default` and skips shape validation, but the
        # per-type COUNT checks later use -ceq, so the record is not
        # counted as its type and the round fails there instead. The
        # mutation changes which reason is reported, not the outcome.
        switch -CaseSensitive ($rec.type) {
            "turn.prompt" { $shapeOk = Test-TurnPromptShape $rec }
            "llm.request" { $shapeOk = Test-LlmRequestShape $rec }
            "llm.tools_snapshot" { $shapeOk = Test-ToolsSnapshotShape $rec }
            "tools.set_active_tools" { $shapeOk = Test-ActiveToolsShape $rec }
            "config.update" { $shapeOk = Test-ConfigUpdateShape $rec }
            "permission.set_mode" { $shapeOk = Test-PermissionModeShape $rec }
            default { $shapeOk = $true }
        }
        if (-not $shapeOk) {
            Fail ("record-malformed: a " + $rec.type + " record is structurally invalid")
        }
        [void]$records.Add($rec)
    }
    if ($records.Count -eq 0) {
        Fail "slice-misaligned: the wire slice is empty"
    }
    if ($records[0].type -cne $expectedFirstType) {
        Fail ("slice-misaligned: the wire slice's first record is " + $records[0].type +
              ", expected " + $expectedFirstType)
    }
    return @($records)
}

function Read-LogSlice($logPath, $offset) {
    $bytes = [System.IO.File]::ReadAllBytes($logPath)
    $sliceBytes = Get-ByteSuffix $bytes $offset
    $text = ConvertFrom-StrictUtf8 $sliceBytes
    if ($null -eq $text) {
        Fail "log-config-malformed: the log slice is not valid UTF-8"
    }
    $lines = @($text -split "`n" | Where-Object { $_.Trim().Length -gt 0 })
    return @($lines)
}

function Parse-LlmConfigLine($line) {
    # PARSE THE SUFFIX AFTER THE MARKER, NEVER THE WHOLE LINE. The
    # selector picks this line because it CONTAINS "llm config"; an
    # unanchored match then took the first field run anywhere in it, so a
    # line carrying the expected values BEFORE the marker and the real,
    # disagreeing ones after it was accepted, and every field comparison
    # downstream read the decoy. Reproduced on both hosts 2026-08-17,
    # round 5 of the 0.26.0 diff debate.
    #
    # The marker must appear EXACTLY ONCE. Two of them leave no single
    # suffix to parse, and picking either one would be this defect again
    # with an extra step.
    if ($null -eq $line) { return $null }
    $marker = "llm config"
    $first = $line.IndexOf($marker, [System.StringComparison]::Ordinal)
    if ($first -lt 0) { return $null }
    if ($line.IndexOf($marker, $first + 1, [System.StringComparison]::Ordinal) -ge 0) {
        return $null
    }
    $suffix = $line.Substring($first + $marker.Length)
    $rx = [regex]'provider=(\S+)\s+model=(\S+)\s+modelAlias=(\S+)\s+thinkingEffort=(\S+)\s+systemPromptChars=(\d+)\s+toolCount=(\d+)'
    $m = $rx.Match($suffix)
    if (-not $m.Success) { return $null }
    return @{
        Provider = $m.Groups[1].Value
        Model = $m.Groups[2].Value
        ModelAlias = $m.Groups[3].Value
        ThinkingEffort = $m.Groups[4].Value
        SystemPromptChars = [int]$m.Groups[5].Value
        ToolCount = [int]$m.Groups[6].Value
    }
}

# =======================================================================
# MAIN
# =======================================================================

# Rule 1
$priorStateObj = Read-PriorState $PriorState

# -SealedPriorStateSha256 binds this call to the exact -PriorState bytes
# named in the dispatch receipt's priorStateSha256 (Task 2's -Prepare).
# RAW BYTES, not the canonicalized JSON Read-PriorState parsed: the
# receipt hashed the file as written, and comparing anything else would
# let a byte-identical tamper through undetected. Optional here because
# other callers of this script exist; when a caller omits it, the check
# was never made and must never read as though it passed.
if ($PSBoundParameters.ContainsKey("SealedPriorStateSha256")) {
    $priorRawBytes = $null
    try {
        $priorRawBytes = [System.IO.File]::ReadAllBytes($PriorState)
    } catch {
        Fail ("prior-state-unusable: could not read -PriorState: " + $_.Exception.Message)
    }
    $observedSealSha256 = Get-Sha256HexOfBytes $priorRawBytes
    if ($observedSealSha256 -ine $SealedPriorStateSha256) {
        $script:Sealed = "sealed-state-mismatch"
        Fail "sealed-state-mismatch"
    }
    $script:Sealed = "sealed"
}

# Rule 2
if ($priorStateObj.kind -cne $Kind) {
    Fail ("state-kind-mismatch: -PriorState.kind is '" + $priorStateObj.kind +
          "' but this invocation is -" + ($(if ($Fresh) { "Fresh" } else { "Resume" })))
}

# Rule 3: establish the session, by kind.
$resolvedSessionDir = $null
$resolvedSessionId = $null
if ($Fresh) {
    # Both sides canonicalized before comparing, same as the resume branch
    # below - the inventory's producer is a different task's dispatch flow
    # and nothing pins its path spelling. Measured: a knownSessionDirs
    # entry spelled with forward slashes for a genuinely pre-existing
    # directory otherwise reads as a SECOND new directory, not the one
    # already known.
    $known = @($priorStateObj.knownSessionDirs | ForEach-Object { Resolve-PathSafe $_ })
    $current = Get-SessionLeaves $SessionsRoot
    $newLeaves = @($current | Where-Object { $known -notcontains (Resolve-PathSafe $_) })
    if ($newLeaves.Count -ne 1) {
        Fail ("session-not-resolvable: " + $newLeaves.Count +
              " new session directory(ies) found under -SessionsRoot, expected exactly 1")
    }
    $leafName = Split-Path -Leaf $newLeaves[0]
    if ($leafName -cne $SessionIdFromStdout) {
        Fail ("session-id-mismatch: the new session directory is '" + $leafName +
              "' but -SessionIdFromStdout is '" + $SessionIdFromStdout + "'")
    }
    $resolvedSessionDir = $newLeaves[0]
    $resolvedSessionId = $leafName
} else {
    $resolvedSessionDir = $SessionDir
    $resolvedSessionId = Split-Path -Leaf ($SessionDir.TrimEnd('\', '/'))
    $priorNames = @($priorStateObj.PSObject.Properties.Name)
    $priorSessionDir = if (Test-HasKey $priorStateObj "sessionDir") { [string]$priorStateObj.sessionDir } else { $null }
    $priorSessionId = if (Test-HasKey $priorStateObj "sessionId") { [string]$priorStateObj.sessionId } else { $null }
    # $priorFull/$resolvedFull stay case-INSENSITIVE: they are resolved
    # Windows filesystem paths, where case is not identity. The session ID
    # beside them is case-EXACT, because it is a token the client issued
    # and this tool binds a round to.
    $resolvedFull = Resolve-PathSafe $resolvedSessionDir
    $priorFull = Resolve-PathSafe $priorSessionDir
    if (($priorFull -ne $resolvedFull) -or ($priorSessionId -cne $resolvedSessionId)) {
        Fail "state-session-mismatch: -PriorState.sessionDir/sessionId does not name this session"
    }
}

# Rule 4: internally inconsistent state.
$priorNames = @($priorStateObj.PSObject.Properties.Name)
if ($priorStateObj.kind -ceq "fresh") {
    foreach ($f in @("sessionDir", "wireBytes", "logBytes", "wirePrefixSha256",
                     "logPrefixSha256", "toolsHash", "systemPromptHash")) {
        if (Test-HasKey $priorStateObj $f) {
            Fail ("state-inconsistent: a fresh -PriorState carries '" + $f + "'")
        }
    }
} else {
    foreach ($f in @("sessionDir", "wireBytes", "logBytes", "wirePrefixSha256",
                     "logPrefixSha256", "toolsHash", "systemPromptHash")) {
        if (-not (Test-HasKey $priorStateObj $f)) {
            Fail ("state-inconsistent: a resume -PriorState is missing '" + $f + "'")
        }
    }
}

# Rule 5
$agentInfo = Get-AgentFileInfo $AgentFile
if ($ExpectedBriefSha256 -notmatch $Sha256Rx) {
    Fail "bad-argument: -ExpectedBriefSha256 is not 64 hex characters"
}

# Rule 6
if (-not (Test-Path -LiteralPath $resolvedSessionDir -PathType Container)) {
    Fail "session-dir-missing: the session directory does not exist"
}
$wirePath = Join-Path $resolvedSessionDir "agents\main\wire.jsonl"
$logGlob = Join-Path $resolvedSessionDir "logs\kimi-code.log"
if (-not (Test-Path -LiteralPath $wirePath -PathType Leaf)) {
    Fail "evidence-file-missing: wire.jsonl is missing"
}
if (-not (Test-Path -LiteralPath $logGlob -PathType Leaf)) {
    Fail "evidence-file-missing: kimi-code.log is missing"
}

# Rule 7: offsets, by kind.
$wireOffset = 0
$logOffset = 0
if ($Resume) {
    $wireOffset = [long]$priorStateObj.wireBytes
    $logOffset = [long]$priorStateObj.logBytes
}

# Rule 8: truncation.
$wireLen = (Get-Item -LiteralPath $wirePath).Length
$logLen = (Get-Item -LiteralPath $logGlob).Length
if ($wireLen -lt $wireOffset) {
    Fail "truncated: wire.jsonl is shorter than the prior wire offset"
}
if ($logLen -lt $logOffset) {
    Fail "truncated: kimi-code.log is shorter than the prior log offset"
}

# Rule 9: prefix hash, resume only (offsets are zero on fresh, so the
# prefix is empty and trivially matches - nothing to compare against
# anyway since a fresh -PriorState carries no prefix hash).
if ($Resume) {
    $wireBytesAll = [System.IO.File]::ReadAllBytes($wirePath)
    $wirePrefix = Get-BytePrefix $wireBytesAll $wireOffset
    $wirePrefixHash = Get-Sha256HexOfBytes ([byte[]]$wirePrefix)
    if ($wirePrefixHash -ne $priorStateObj.wirePrefixSha256) {
        Fail "prefix-replaced: wire.jsonl's prefix no longer hashes to wirePrefixSha256"
    }
    $logBytesAll = [System.IO.File]::ReadAllBytes($logGlob)
    $logPrefix = Get-BytePrefix $logBytesAll $logOffset
    $logPrefixHash = Get-Sha256HexOfBytes ([byte[]]$logPrefix)
    if ($logPrefixHash -ne $priorStateObj.logPrefixSha256) {
        Fail "prefix-replaced: kimi-code.log's prefix no longer hashes to logPrefixSha256"
    }
}

# Rules 10-11
$expectedFirst = if ($Fresh) { "metadata" } else { "turn.prompt" }
$records = Read-WireSlice $wirePath $wireOffset $expectedFirst
$logLines = Read-LogSlice $logGlob $logOffset

# Rule 12: session-scoped checks, fresh only.
if ($Fresh) {
    # Every comparison against FOREIGN DATA below is case-exact: record
    # types, the permission mode, the model, provider and effort, and the
    # tool names (Compare-Object is case-INSENSITIVE without
    # -CaseSensitive, measured). PowerShell's -eq and -ne are
    # case-insensitive, so a round that declared `AUTO`, or a tool named
    # `read` where the allowlist says `Read`, used to be attributed to a
    # configuration it never actually ran under. The HOSTNAME comparison
    # and the confirmation hashes stay case-insensitive on purpose; they
    # are not this class.
    $configUpdates = @($records | Where-Object { $_.type -ceq "config.update" })
    $activeTools = @($records | Where-Object { $_.type -ceq "tools.set_active_tools" })
    $snapshots = @($records | Where-Object { $_.type -ceq "llm.tools_snapshot" })
    $permModes = @($records | Where-Object { $_.type -ceq "permission.set_mode" })

    if ($configUpdates.Count -ne 2) {
        Fail ("session-scoped-count: expected exactly 2 config.update records, found " + $configUpdates.Count)
    }
    if ($activeTools.Count -ne 1) {
        Fail ("session-scoped-count: expected exactly 1 tools.set_active_tools record, found " + $activeTools.Count)
    }
    if ($snapshots.Count -ne 1) {
        Fail ("session-scoped-count: expected exactly 1 llm.tools_snapshot record, found " + $snapshots.Count)
    }
    if ($permModes.Count -ne 1) {
        Fail ("session-scoped-count: expected exactly 1 permission.set_mode record, found " + $permModes.Count)
    }

    # The two config.update shapes are distinguished by which keys they
    # carry, not by order.
    $firstShapes = @($configUpdates | Where-Object {
        (Test-HasKey $_ "profileName") -or
        (Test-HasKey $_ "systemPrompt") })
    $secondShapes = @($configUpdates | Where-Object {
        (Test-HasKey $_ "modelAlias") -or
        (Test-HasKey $_ "thinkingEffort") })
    if ($firstShapes.Count -ne 1) {
        Fail "session-scoped-content: expected exactly one profileName/systemPrompt config.update"
    }
    if ($secondShapes.Count -ne 1) {
        Fail "session-scoped-content: expected exactly one modelAlias/thinkingEffort config.update"
    }
    $first = $firstShapes[0]
    $second = $secondShapes[0]

    if ($first.profileName -cne $agentInfo.Name) {
        Fail "session-scoped-content: config.update profileName does not match -AgentFile's name"
    }
    $recordedPrompt = ConvertTo-NormalizedLF $first.systemPrompt
    $agentBody = ConvertTo-NormalizedLF $agentInfo.Body
    if ($recordedPrompt -cne $agentBody) {
        Fail "session-scoped-content: config.update systemPrompt does not match -AgentFile's body"
    }
    if ($second.modelAlias -cne $Model) {
        Fail "session-scoped-content: the second config.update's modelAlias does not match -Model"
    }
    if ($second.thinkingEffort -cne $Effort) {
        Fail "session-scoped-content: the second config.update's thinkingEffort does not match -Effort"
    }

    $active = $activeTools[0]
    $activeNames = @($active.names)
    $activeDisallowed = @($active.disallowedNames)
    if (@(Compare-Object $activeNames $agentInfo.Tools -CaseSensitive).Count -ne 0) {
        Fail "session-scoped-content: tools.set_active_tools.names does not match -AgentFile's tools list"
    }
    if (@(Compare-Object $activeDisallowed $agentInfo.DisallowedTools -CaseSensitive).Count -ne 0) {
        Fail "session-scoped-content: tools.set_active_tools.disallowedNames does not match -AgentFile's disallowedTools list"
    }

    $snapshot = $snapshots[0]
    if ([string]::IsNullOrEmpty($snapshot.hash)) {
        Fail "session-scoped-content: llm.tools_snapshot.hash is missing or empty"
    }
    # EQUALITY, in both directions. A one-sided comparison (keeping only
    # the "<=" side indicator) would let a snapshot that is MISSING tools
    # pass clean - the permissive direction, and the one that matters: a
    # round whose sent tool surface collapsed would then be reported
    # clean. Compare-Object with no -SyncWindow is set-based, so a
    # different ORDER is still equal, which is what the measured client
    # emits (the snapshot orders its tools differently from
    # tools.set_active_tools.names).
    $snapshotToolNames = @($snapshot.tools | ForEach-Object { $_.name })
    if (@(Compare-Object $snapshotToolNames $activeNames -CaseSensitive).Count -ne 0) {
        Fail "session-scoped-content: llm.tools_snapshot tool names do not equal the active tool allowlist"
    }

    $permMode = $permModes[0]
    if ($permMode.mode -cne "auto") {
        Fail "session-scoped-content: permission.set_mode.mode is not 'auto'"
    }
} else {
    foreach ($t in @("config.update", "tools.set_active_tools", "llm.tools_snapshot", "permission.set_mode")) {
        $present = @($records | Where-Object { $_.type -ceq $t })
        if ($present.Count -gt 0) {
            Fail ("session-scoped-on-resume: a " + $t + " record is present in a resume slice")
        }
    }
}

# Rule 13: per-call checks, both kinds.
$turnPrompts = @($records | Where-Object { $_.type -ceq "turn.prompt" })
if ($turnPrompts.Count -ne 1) {
    Fail ("turn-prompt-count: expected exactly 1 turn.prompt record, found " + $turnPrompts.Count)
}
$turnPrompt = $turnPrompts[0]

$llmRequests = @($records | Where-Object { $_.type -ceq "llm.request" })
if ($llmRequests.Count -lt 1) {
    Fail "llm-request-count: expected at least 1 llm.request record, found 0"
}

$toolsHashes = New-Object System.Collections.Generic.HashSet[string]
$promptHashes = New-Object System.Collections.Generic.HashSet[string]
foreach ($r in $llmRequests) {
    if ($r.provider -cne $Provider) {
        Fail "llm-request-field: an llm.request's provider does not match -Provider"
    }
    if ($r.modelAlias -cne $Model) {
        Fail "llm-request-field: an llm.request's modelAlias does not match -Model"
    }
    if ($r.thinkingEffort -cne $Effort) {
        Fail "llm-request-field: an llm.request's thinkingEffort does not match -Effort"
    }
    if ([string]::IsNullOrEmpty($r.toolsHash)) {
        Fail "llm-request-field: an llm.request's toolsHash is empty"
    }
    if ([string]::IsNullOrEmpty($r.systemPromptHash)) {
        Fail "llm-request-field: an llm.request's systemPromptHash is empty"
    }
    [void]$toolsHashes.Add($r.toolsHash)
    [void]$promptHashes.Add($r.systemPromptHash)
}
if ($toolsHashes.Count -ne 1) {
    Fail "llm-request-hash-inconsistent: llm.request toolsHash differs between requests in this slice"
}
if ($promptHashes.Count -ne 1) {
    Fail "llm-request-hash-inconsistent: llm.request systemPromptHash differs between requests in this slice"
}
$sliceToolsHash = @($toolsHashes)[0]
$sliceSystemPromptHash = @($promptHashes)[0]

if ($Fresh) {
    $snapshot = @($records | Where-Object { $_.type -ceq "llm.tools_snapshot" })[0]
    # Task 4 Step 1b measured llm.request.toolsHash EQUAL to
    # llm.tools_snapshot.hash on this client - so this branch is taken,
    # not the presence-and-nonempty fallback (see the header comment).
    if ($sliceToolsHash -ne $snapshot.hash) {
        Fail "snapshot-hash-mismatch: llm.request toolsHash disagrees with llm.tools_snapshot.hash"
    }
}

$logConfigLines = @($logLines | Where-Object { $_ -cmatch "llm config" })
if ($logConfigLines.Count -ne 1) {
    Fail ("log-config-count: expected exactly 1 new llm config line, found " + $logConfigLines.Count)
}
$parsedLog = Parse-LlmConfigLine $logConfigLines[0]
if ($null -eq $parsedLog) {
    Fail "log-config-malformed: the llm config line does not match the expected shape"
}
if ($parsedLog.Provider -cne $Provider) {
    Fail "log-config-field: the llm config line's provider does not match -Provider"
}
if ($parsedLog.ModelAlias -cne $Model) {
    Fail "log-config-field: the llm config line's modelAlias does not match -Model"
}
if ($parsedLog.ThinkingEffort -cne $Effort) {
    Fail "log-config-field: the llm config line's thinkingEffort does not match -Effort"
}
if ($parsedLog.ToolCount -ne $agentInfo.Tools.Count) {
    Fail "log-config-field: toolCount does not equal the agent file's allowlist length"
}
# Fix round 2: removed a fresh-only cross-check that used to sit here
# (toolCount vs llm.tools_snapshot.tools.Count). It could never fail on
# its own: rule 12 above already requires the snapshot's tool NAMES to
# equal the active allowlist by full multiset equality (Compare-Object
# flags even a duplicate name as a difference), so any mutation that
# changes the snapshot's tool COUNT changes that name multiset too and is
# caught there first, before this point is ever reached. A check that
# cannot fail is the defect class this validator exists to remove.
$agentBodyNorm = ConvertTo-NormalizedLF $agentInfo.Body
if ($parsedLog.SystemPromptChars -ne $agentBodyNorm.Length) {
    Fail "log-config-field: systemPromptChars does not match the agent body's length"
}

# Rule 14: continuity from round 2 onward.
if ($Resume) {
    if ($sliceToolsHash -ne $priorStateObj.toolsHash) {
        Fail "hash-discontinuity: this slice's toolsHash differs from -PriorState's"
    }
    if ($sliceSystemPromptHash -ne $priorStateObj.systemPromptHash) {
        Fail "hash-discontinuity: this slice's systemPromptHash differs from -PriorState's"
    }
}

# Rule 15: the brief hash.
$briefText = ((@($turnPrompt.input) | ForEach-Object { $_.text }) -join "")
$briefHash = Get-Sha256HexOfBytes (Get-Utf8BytesNoBom (ConvertTo-CanonicalBrief $briefText))
if ($briefHash -ne $ExpectedBriefSha256) {
    # SAY WHAT THE MISMATCH IS NOT. This tool holds an opaque expected
    # digest and never the brief itself, so a failed alternate hash
    # cannot separate changed content from a different encoding, a byte
    # order mark, another newline rule or a caller defect. Naming the
    # one cause that CAN be ruled in or out is the whole of what the
    # evidence supports, and claiming more would be the overclaim this
    # tool exists to refuse. Both directions still fail the round; only
    # the message differs, and the extra hash is computed only here.
    # `-eq`, matching the primary comparison above. `-notmatch` at the
    # argument check is case-INSENSITIVE, so an uppercase expected
    # digest reaches here; comparing the alternate case-sensitively
    # would then diagnose it as unexplained when the whitespace rule
    # explains it exactly.
    $untrimmed = Get-Sha256HexOfBytes (Get-Utf8BytesNoBom (ConvertTo-NormalizedLF $briefText))
    if ($untrimmed -eq $ExpectedBriefSha256) {
        Fail ("brief-hash: turn.prompt does not hash to " +
              "-ExpectedBriefSha256, and the mismatch is explained by " +
              "trim-versus-untrimmed canonicalization: the recorded " +
              "prompt hashes to the expected digest under the untrimmed " +
              "rule this lane used before 2026-08-16")
    }
    Fail ("brief-hash: turn.prompt does not hash to -ExpectedBriefSha256, " +
          "and the mismatch is not explained by surrounding-whitespace " +
          "canonicalization")
}

# Rule 16: success.
$finalWireLen = (Get-Item -LiteralPath $wirePath).Length
$finalLogLen = (Get-Item -LiteralPath $logGlob).Length
$finalWireBytes = [System.IO.File]::ReadAllBytes($wirePath)
$finalWirePrefix = Get-BytePrefix $finalWireBytes $finalWireLen
$finalWirePrefixHash = Get-Sha256HexOfBytes ([byte[]]$finalWirePrefix)
$finalLogBytes = [System.IO.File]::ReadAllBytes($logGlob)
$finalLogPrefix = Get-BytePrefix $finalLogBytes $finalLogLen
$finalLogPrefixHash = Get-Sha256HexOfBytes ([byte[]]$finalLogPrefix)

$nextState = [ordered]@{
    kind = "resume"
    sessionDir = $resolvedSessionDir
    sessionId = $resolvedSessionId
    wireBytes = $finalWireLen
    logBytes = $finalLogLen
    wirePrefixSha256 = $finalWirePrefixHash
    logPrefixSha256 = $finalLogPrefixHash
    toolsHash = $sliceToolsHash
    systemPromptHash = $sliceSystemPromptHash
}

Write-Result "clean" $null $nextState $Json
