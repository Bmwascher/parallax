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

function Get-CanonicalText([string]$text) {
    # The declared canonicalization, in one place. Both this script and the
    # caller that computes -ExpectedBriefSha256 must apply the same rule, so
    # it is stated rather than left to whichever side reads the bytes first.
    $text.Replace("`r`n", "`n").Trim()
}

function Get-CanonicalSha256([string]$text) {
    $t = Get-CanonicalText $text
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($t)
    Get-Sha256Hex $bytes 0 $bytes.Length
}

# The client's environment preamble, recognised by SHAPE.
# Measured 2026-08-15 across the whole session store: a matched element is
# EXACTLY one envelope carrying five direct fields, or the three-field
# subset a refresh carries. Nothing observed carried an unknown field, a
# duplicate, or text outside the envelope.
$script:EnvOpen = "<environment_context>"
$script:EnvClose = "</environment_context>"
$script:EnvAllowed = @("cwd", "shell", "current_date", "timezone", "filesystem")
# Present in BOTH measured shapes. The allowed set is their UNION and the
# core is their INTERSECTION, so a shape between the two - one carrying
# `cwd` but not `shell` - is admitted by DERIVATION and was never itself
# observed. This is NOT the narrowest possible rule: an exact allow-list
# of the two observed shapes would be narrower. It is the settled
# field-by-field design, chosen because an allow-list breaks again the
# first time the client changes which fields a refresh carries, which is
# the fault this whole item exists to fix. Requiring the core keeps out
# the shapes below both, such as a preamble carrying only a date.
$script:EnvCore = @("current_date", "timezone", "filesystem")

function New-EnvelopeResult($fields, $fault) {
    # BOTH OUTCOMES CARRY THEIR REASON. Returning a bare $null on failure
    # collapses every structural fault into one message, and a refusal
    # that cannot say what it found sends the operator to the wrong place.
    @{ Fields = $fields; Fault = $fault }
}

function Get-EnvironmentEnvelopeFields([string]$canonicalText) {
    # A CURSOR, NOT A SEARCH. The `filesystem` value carries nested tags
    # of its own, so a global scan for field tags cannot tell a direct
    # field from value content. This consumes the envelope end to end and
    # refuses every character it cannot account for.
    # The caller passes CANONICAL text: this compares from the very first
    # character, so a raw record with a trailing newline would refuse.
    if ($null -eq $canonicalText -or
        -not $canonicalText.StartsWith($script:EnvOpen, [System.StringComparison]::Ordinal) -or
        -not $canonicalText.EndsWith($script:EnvClose, [System.StringComparison]::Ordinal)) {
        return New-EnvelopeResult $null "is not a recognised client environment preamble"
    }
    $inner = $canonicalText.Substring(
        $script:EnvOpen.Length,
        $canonicalText.Length - $script:EnvOpen.Length - $script:EnvClose.Length)
    # Ordinal comparer, kept as the innermost of several case layers.
    # Its previous justification was wrong and is corrected here: an
    # OrderedDictionary built with no comparer is already case-SENSITIVE
    # (measured 2026-08-15 on both hosts, `Contains('CWD')` false). A
    # PowerShell `@{}` hashtable is the type that merges `cwd` and `CWD`,
    # and this is not one.
    $fields = New-Object System.Collections.Specialized.OrderedDictionary(
        [System.StringComparer]::Ordinal)
    $i = 0
    while ($i -lt $inner.Length) {
        if ($script:JsonWs -contains $inner[$i]) { $i++; continue }
        if ($inner[$i] -ne '<') {
            return New-EnvelopeResult $null "carries text outside its fields"
        }
        $gt = $inner.IndexOf('>', $i)
        if ($gt -lt 0) {
            return New-EnvelopeResult $null "carries an unterminated tag"
        }
        $name = $inner.Substring($i + 1, $gt - $i - 1)
        # THE OUTERMOST CASE LAYER, and the one that actually fires.
        # Every measured direct field is a bare lowercase tag with no
        # attributes, so this refuses any other name before the closed
        # set at $script:EnvAllowed or the ordinal dictionary above ever
        # sees it. Those two are the fallbacks behind it, not the
        # discriminators: measured 2026-08-15, removing this test alone
        # moves the refusal to the closed set rather than allowing
        # anything through.
        # `\z`, NOT `$`. In .NET `$` matches before a TRAILING NEWLINE,
        # so a name of "cwd`n" satisfied `^[a-z_]+$` and reached the
        # closed set, which refused it as an unknown field - the right
        # verdict with the wrong reason. On the FRESH path there is no
        # closed set behind this test, so `$` would admit the name
        # outright. Backlog item 57(a).
        if ($name -cnotmatch '^[a-z_]+\z') {
            return New-EnvelopeResult $null (
                "carries '" + $name + "', which is not a recognised environment field")
        }
        if ($fields.Contains($name)) {
            return New-EnvelopeResult $null (
                "repeats the environment field '" + $name + "'")
        }
        $closeTag = "</" + $name + ">"
        $end = $inner.IndexOf($closeTag, $gt + 1, [System.StringComparison]::Ordinal)
        if ($end -lt 0) {
            return New-EnvelopeResult $null (
                "never closes the environment field '" + $name + "'")
        }
        $value = $inner.Substring($gt + 1, $end - $gt - 1)
        # A value that re-opens its own tag makes the close ambiguous.
        # Refuse rather than pick one.
        if ($value.Contains("<" + $name + ">")) {
            return New-EnvelopeResult $null (
                "carries an environment field whose value re-opens its own tag: '" +
                $name + "'")
        }
        $fields[$name] = $value
        $i = $end + $closeTag.Length
    }
    if ($fields.Count -lt 1) {
        return New-EnvelopeResult $null "carries no environment fields at all"
    }
    New-EnvelopeResult $fields $null
}

function Find-EnvelopeSpan([string]$canonicalText) {
    # WHERE the one envelope is, with no opinion about what a caller
    # does when there is not exactly one. Kind is $null on success and
    # "none" or "several" otherwise: the two callers word those two
    # outcomes differently - a session BASELINE that cannot be
    # identified and a FRESH record that is not a preamble are
    # different faults - so the selection is shared and the message is
    # not. Duplicating the selection instead is how the two paths drift
    # apart later.
    if ($null -eq $canonicalText) { return @{ Start = -1; Length = 0; Kind = "none" } }
    $first = $canonicalText.IndexOf($script:EnvOpen, [System.StringComparison]::Ordinal)
    if ($first -lt 0) { return @{ Start = -1; Length = 0; Kind = "none" } }
    if ($canonicalText.IndexOf($script:EnvOpen, $first + 1, [System.StringComparison]::Ordinal) -ge 0) {
        return @{ Start = -1; Length = 0; Kind = "several" }
    }
    $close = $canonicalText.IndexOf($script:EnvClose, $first, [System.StringComparison]::Ordinal)
    if ($close -lt 0) { return @{ Start = -1; Length = 0; Kind = "none" } }
    if ($canonicalText.IndexOf($script:EnvClose, $close + 1, [System.StringComparison]::Ordinal) -ge 0) {
        return @{ Start = -1; Length = 0; Kind = "several" }
    }
    @{ Start = $first
       Length = ($close + $script:EnvClose.Length - $first)
       Kind = $null }
}

function Get-BaselineEnvelopeFields([string]$canonicalText) {
    # The session's FIRST user record joins one, two or three elements
    # (three being the most common composition measured), so the envelope
    # is SELECTED from that text rather than assumed to be all of it.
    # Exactly one, or the structural path is unavailable.
    # ZERO and SEVERAL are different faults and say so. One shared message
    # would make "the session never carried a preamble" and "the session
    # carried two and nobody can say which is the baseline" read alike.
    $none = ("cannot be checked: this session's first user record carries " +
             "no environment preamble to compare it against")
    $several = ("cannot be checked: this session's first user record carries " +
                "more than one environment preamble, so which one is the " +
                "baseline is undefined")
    $span = Find-EnvelopeSpan $canonicalText
    if ($span.Kind -eq "none") { return New-EnvelopeResult $null $none }
    if ($span.Kind -eq "several") { return New-EnvelopeResult $null $several }
    $inner = Get-EnvironmentEnvelopeFields $canonicalText.Substring(
        $span.Start, $span.Length)
    if ($null -eq $inner.Fields) {
        # PROPAGATE, do not collapse. Every scanner fault reaching here
        # would otherwise report as one generic message, which is
        # misleading for a single envelope that merely repeats a field.
        return New-EnvelopeResult $null (
            "cannot be checked: this session's own preamble " + $inner.Fault)
    }
    $inner
}

function Get-FreshPreambleFault([string]$text) {
    # $null means the record reads as the client's own environment
    # preamble. Anything else is a phrase naming what failed.
    #
    # THIS IS NOT Get-RefreshedPreambleFault AND MUST NOT CALL IT. That
    # function rejects unknown names BEFORE it checks the core, then
    # compares values against a baseline. A fresh call has no baseline:
    # its own first record IS the one every later resumed round is
    # measured against. So this checks SHAPE and nothing else.
    #
    # WHAT IT DOES NOT CLAIM. Not provenance - the rollout is a local
    # file, and anyone able to write it can forge a well-formed
    # preamble. Text BEFORE the envelope is accepted and NOT bound:
    # measured 2026-08-16, 658 of 767 first user records in the whole
    # session store carry the client's own instructions ahead of it,
    # and refusing that direction would refuse the large majority of
    # real traffic. Instruction text inside a field VALUE binds too,
    # because no value is compared here.
    $canonical = Get-CanonicalText $text
    $span = Find-EnvelopeSpan $canonical
    if ($span.Kind -eq "none") {
        return "carries no environment preamble at all"
    }
    if ($span.Kind -eq "several") {
        return ("carries more than one environment preamble, so which one " +
                "the client sent is undefined")
    }
    # THE ENVELOPE MUST END THE RECORD. Nothing followed one in either
    # measured population - 0 of 767 records and 0 of 372 of this
    # repo's own debate dispatches - so that direction closes at no
    # cost. CANONICAL, not raw: this script strips the ends everywhere
    # else, so insignificant terminal whitespace must not decide a
    # round.
    if (($span.Start + $span.Length) -ne $canonical.Length) {
        return "carries text after its environment preamble"
    }
    $env = Get-EnvironmentEnvelopeFields $canonical.Substring(
        $span.Start, $span.Length)
    if ($null -eq $env.Fields) { return $env.Fault }
    # THE CORE, AND DELIBERATELY NOT THE CLOSED SET. They are different
    # rules. The closed set is an UPPER bound that rejects additions,
    # and it buys nothing here - every name and value comes from the
    # record being tested, so a forger can use the five known names -
    # while costing a total fresh-round outage the first time the
    # client adds a field. That bound has been falsified twice, on
    # 2026-08-04 and 2026-08-14, each time blocking paid rounds, and
    # neither falsification dropped a core field. The core is a LOWER
    # bound that keeps out shapes below both measured compositions.
    # Without it a one-field junk wrapper binds and becomes a baseline
    # with no current_date, silently disabling the structural refresh
    # path for the rest of the session.
    foreach ($name in $script:EnvCore) {
        if (-not $env.Fields.Contains($name)) {
            return ("omits the required environment field '" + $name + "'")
        }
    }
    $null
}

function Get-EnvDate([string]$value) {
    # ParseExact, not a regex: `^\d{4}-\d{2}-\d{2}$` accepts 2026-02-31.
    # CANONICALIZED FIRST, the same way every other field is. Every
    # other field is compared through Get-CanonicalSha256, which folds
    # CRLF and strips the ends, so a padded value passes there; this one
    # went to the parser raw, and a padded date was refused where a
    # padded anything-else was accepted. On the baseline side that
    # asymmetry disabled the structural path for a whole session.
    # Backlog item 57(b).
    $d = [datetime]::MinValue
    $ok = [datetime]::TryParseExact(
        (Get-CanonicalText $value), 'yyyy-MM-dd',
        [System.Globalization.CultureInfo]::InvariantCulture,
        [System.Globalization.DateTimeStyles]::None, [ref]$d)
    if ($ok) { $d } else { $null }
}

function Get-RefreshedPreambleFault([string]$extraText, [string]$baseText) {
    # $null means the record is an acceptable refresh. Anything else is a
    # phrase naming the direction that failed.
    $extra = Get-EnvironmentEnvelopeFields (Get-CanonicalText $extraText)
    if ($null -eq $extra.Fields) { return $extra.Fault }
    foreach ($name in @($extra.Fields.Keys)) {
        if ($script:EnvAllowed -cnotcontains $name) {
            return ("carries the unknown environment field '" + $name + "'")
        }
    }
    foreach ($name in $script:EnvCore) {
        if (-not $extra.Fields.Contains($name)) {
            return ("omits the required environment field '" + $name + "'")
        }
    }
    $base = Get-BaselineEnvelopeFields (Get-CanonicalText $baseText)
    if ($null -eq $base.Fields) { return $base.Fault }
    if (-not $base.Fields.Contains("current_date")) {
        return ("cannot be checked: this session's own preamble carries no " +
                "current_date to bound the refreshed one")
    }
    $baseDate = Get-EnvDate ([string]$base.Fields["current_date"])
    if ($null -eq $baseDate) {
        return ("cannot be checked: this session's own preamble carries a " +
                "current_date that is not a calendar date in yyyy-MM-dd form")
    }
    foreach ($name in @($extra.Fields.Keys)) {
        if ($name -ceq "current_date") { continue }
        if (-not $base.Fields.Contains($name)) {
            return ("carries the environment field '" + $name + "', which " +
                    "this session's own preamble does not")
        }
        if ((Get-CanonicalSha256 ([string]$extra.Fields[$name])) -ne
            (Get-CanonicalSha256 ([string]$base.Fields[$name]))) {
            return ("carries an environment field that does not match this " +
                    "session's own preamble: '" + $name + "'")
        }
    }
    $newDate = Get-EnvDate ([string]$extra.Fields["current_date"])
    if ($null -eq $newDate) {
        return ("carries a current_date that is not a calendar date in " +
                "yyyy-MM-dd form")
    }
    if ($newDate -lt $baseDate) {
        return ("carries a current_date earlier than this session's own " +
                "preamble, so it did not refresh from it")
    }
    if ($newDate -gt [datetime]::Now.Date) {
        return "carries a current_date later than today"
    }
    $null
}

# The four characters JSON calls whitespace. Everything else that
# .NET considers whitespace is content as far as this parser goes.
$script:JsonWs = [char[]]@(' ', "`t", "`r", "`n")

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

# THE STATE FILE NEEDS THE SAME ROOT GUARD AS A ROLLOUT LINE, and the
# first version of that guard only covered the rollout. Measured on both
# hosts 2026-08-04: a prior state written `[{...}]` UNROLLS on PowerShell
# 7.6.3, so `.kind` and every field below read straight through and the
# document behaves as the object it is not; on 5.1 it stays
# `System.Object[]` and the presence checks happen to fail. One file over
# from where the same defect was just closed, which is the argument for
# putting the rule in a function rather than at a call site.
$priorFault = Get-JsonObjectLineFault $priorText $prior
if ($priorFault) {
    Fail ("prior state " + $priorFault + " at its root, so the fields " +
          "read from it are not the fields it declares")
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
    # PRESENCE IS NOT A MEASUREMENT. Found by the mode-diff debate,
    # cross-vendor reviewer lane, round 1, and measured here first:
    # `knownRollouts: null` satisfies a presence test, and
    # `@($null | ForEach-Object {...})` then yields a ONE-element array,
    # so the inventory became a single entry matching no path, the
    # not-new comparison never fired, and a PRE-EXISTING rollout bound
    # as though this call had created it. An empty ARRAY is still
    # accepted: that is a measurement that found nothing, which is a
    # different thing from one nobody made.
    $inv = $prior.knownRollouts
    if ($null -eq $inv -or -not ($inv -is [System.Array])) {
        Fail ("prior state knownRollouts must be an array; a missing or " +
              "non-array inventory is one nobody made")
    }
    foreach ($item in $inv) {
        if (-not ($item -is [string]) -or [string]::IsNullOrWhiteSpace($item)) {
            Fail ("prior state knownRollouts must hold only non-empty path " +
                  "strings; an entry that is not one cannot be compared")
        }
    }
} else {
    Assert-PriorField "rolloutFile"
    Assert-PriorField "sessionId"
    Assert-PriorField "bytes"
    Assert-PriorField "prefixSha256"
    # THE RESUME HALF CARRIED THE SAME DEFECT F1 CLOSED ON THE FRESH
    # HALF. Found by the mode-diff debate round 2, and measured here
    # before it was accepted: `rolloutFile` null or empty is PRESENT, so
    # the assertion above passed, and the comparison against the
    # caller's -RolloutFile is gated on truthiness further down and was
    # therefore skipped. The state's own record of which file it
    # measured constrained nothing.
    #
    # Of the other three, TWO were diagnostic and one was a hole, and
    # this comment said all three were diagnostic until round 4 read it
    # against the record. A bad `prefixSha256` failed its comparison and
    # a blank `sessionId` disagreed with the filename, so both were
    # already refused and only the REASON was wrong - a schema fault
    # reported as a changed rollout sends the operator to re-measure an
    # artifact that is fine. `bytes` was different: a FRACTIONAL count
    # truncates through `[int]` on both hosts, so paired with a prefix
    # hash taken through the truncated offset it reached the ordinary
    # slice checks. Validating the shape here closes that and makes the
    # other two name their field.
    foreach ($f in @("rolloutFile", "sessionId")) {
        $v = $prior.$f
        if (-not ($v -is [string]) -or [string]::IsNullOrWhiteSpace($v)) {
            Fail ("prior state " + $f + " must be a non-empty string; a " +
                  "blank or non-string value records no measurement")
        }
    }
    $rawBytes = $prior.bytes
    if (-not (($rawBytes -is [int]) -or ($rawBytes -is [long])) -or
        [long]$rawBytes -lt 0) {
        Fail ("prior state bytes must be a non-negative whole number of " +
              "bytes; anything else is not a byte offset anyone measured")
    }
    if (-not ($prior.prefixSha256 -is [string]) -or
        ([string]$prior.prefixSha256) -notmatch '^[0-9a-f]{64}$') {
        Fail ("prior state prefixSha256 must be a lowercase 64-character " +
              "hex digest; a value that cannot be one was never a hash of " +
              "anything")
    }
}

# --------------------------------------------------------------------
# Locate the rollout and establish the byte range THIS call appended.
# --------------------------------------------------------------------

function Test-RecordIsUserMessage($rec) {
    # NESTED SHAPES NEED ESTABLISHING TOO, and the root guard does not
    # reach them. `payload` given as a JSON ARRAY enumerates its members
    # on BOTH hosts, so `payload.type` and `payload.role` read straight
    # through a value that is not an object at all - the same defect as
    # the root one, one level down, and found by round 4 of the debate.
    if (-not ($rec -is [System.Management.Automation.PSCustomObject])) { return $false }
    if ($rec.type -ne "response_item") { return $false }
    if (-not ($rec.payload -is [System.Management.Automation.PSCustomObject])) { return $false }
    if ($rec.payload.type -ne "message") { return $false }
    return ($rec.payload.role -eq "user")
}

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

    # UNCONDITIONAL. This used to be gated on `if ($prior.rolloutFile)`,
    # so the falsy forms skipped the one check that ties the caller's
    # -RolloutFile to the file the prior state actually measured. The
    # schema check above now guarantees a non-empty string, and the
    # comparison runs for every resume rather than for the ones whose
    # state happened to be well-formed.
    $statedFile = $null
    try { $statedFile = [System.IO.Path]::GetFullPath([string]$prior.rolloutFile) }
    catch { $statedFile = [string]$prior.rolloutFile }
    if (-not ($statedFile -ieq [System.IO.Path]::GetFullPath($targetFile))) {
        Fail ("prior state names a different rollout file: " + $statedFile)
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
    # A RESUME WITH NO PREFIX HAS NO EVIDENCE. A real resumed session
    # always carries its own session_meta and at least one earlier round,
    # so a zero offset means the prior state measured nothing. Left
    # unrefused it binds clean: the boundary guard below has no byte to
    # check, the prefix's own session_meta check reads the first line of
    # the WHOLE file - this call's own slice - and a slice carrying one
    # user record never reaches the preamble scan. Measured 2026-08-16.
    # Same self-adoption class as the CRLF overrun: evidence from the
    # slice mistaken for evidence from before it.
    if ($priorBytes -eq 0) {
        Fail ("prior state records an empty prefix: a resumed round must " +
              "follow a session that already exists, so there is nothing " +
              "for this call's slice to be measured against")
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
    # THE OFFSET MUST FALL ON A RECORD BOUNDARY, and length plus a
    # matching hash does not prove that. The terminal-newline check below
    # covers the whole file AFTER this call appended to it, so a prefix
    # ending mid-record passes it. The scan then drops its final segment
    # as though the offset were known to be a boundary, the slice decodes
    # cleanly, identity passes, and a stream that is not intact binds
    # clean. Measured 2026-08-16 against a prefix ending in an
    # unterminated fragment.
    if ($priorBytes -gt 0 -and $bytes[$priorBytes - 1] -ne 0x0A) {
        Fail ("prior state's byte offset does not fall on a record " +
              "boundary: the prefix it measures ends mid-record, so the " +
              "record stream before this call is not intact")
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
    $lineFault = Get-JsonObjectLineFault $lines[$i] $rec
    if ($lineFault) {
        Fail ("rollout line " + ($i + 1) + " of this call's slice " +
              $lineFault)
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
    # `payload` must be an OBJECT before its id is read: an array payload
    # enumerates `.id` through on both hosts, so a session identity could
    # be taken from a value that is not a record's payload at all.
    $metaRecords = @($records | Where-Object {
        $_.type -eq "session_meta" -and
        ($_.payload -is [System.Management.Automation.PSCustomObject])
    })
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
    # THE PREFIX'S OWN session_meta, re-measured rather than trusted.
    # The contract says a resumed rollout is resolved by its first
    # `session_meta` record AND its filename; resume checked the
    # filename and the prior state and parsed only the appended slice,
    # so the recorded provenance was taken on faith. Found by the
    # mode-diff debate, cross-vendor lane, round 1. Only the FIRST line
    # is read: the prefix hash already pins the rest, and re-parsing a
    # whole cumulative rollout every round would grow without bound.
    $firstLine = $null
    try {
        $reader = New-Object System.IO.StreamReader(
            $targetFile, (New-Object System.Text.UTF8Encoding($false, $true)))
        try { $firstLine = $reader.ReadLine() } finally { $reader.Dispose() }
    } catch {
        Fail ("the resumed rollout's first record could not be read: " +
              $_.Exception.Message)
    }
    $firstRec = $null
    try {
        $firstRec = $firstLine | ConvertFrom-Json
    } catch {
        Fail ("the resumed rollout's first record is not parseable JSON, so " +
              "its session identity was never measured")
    }
    # PROVE IT IS AN OBJECT BEFORE READING PROPERTIES. A first line that
    # is a JSON ARRAY satisfied a check written to prove the line is a
    # session_meta record, because its properties read straight through.
    # See Get-JsonObjectLineFault for the host divergence that makes the
    # obvious type test the wrong instrument.
    $firstFault = Get-JsonObjectLineFault $firstLine $firstRec
    if ($firstFault) {
        Fail ("the resumed rollout's first line " + $firstFault + ", so it " +
              "is not a session_meta record whatever its properties read as")
    }
    if ($firstRec.type -ne "session_meta") {
        Fail ("the resumed rollout's first record is not a session_meta " +
              "record, so its session identity was never measured")
    }
    if (-not ($firstRec.payload -is [System.Management.Automation.PSCustomObject])) {
        Fail ("the resumed rollout's first record has no object payload, so " +
              "the session identity read from it is not one it declares")
    }
    $prefixId = [string]$firstRec.payload.id
    if ($prefixId -ne $expectSessionId) {
        Fail ("the session id disagrees across sources: session_meta '" +
              $prefixId + "', prior state '" + $expectSessionId + "'")
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
        # An element that is not an OBJECT reads its `type` through member
        # enumeration on both hosts, so `-not $el` never saw it. Same
        # nested-shape class as the payload guard above.
        if (-not ($el -is [System.Management.Automation.PSCustomObject])) { return $null }
        if ($el.type -ne "input_text") { return $null }
        [void]$sb.Append([string]$el.text)
    }
    $sb.ToString()
}

$userRecords = @($records | Where-Object { Test-RecordIsUserMessage $_ })

if ($userRecords.Count -lt 1) {
    Fail ("this call's slice carries no user record, so there is no recorded " +
          "prompt to bind the brief to")
}

# THIS BOUND USED TO BE ARITHMETIC AND THE FIELD FALSIFIED IT.
# "A resumed slice carries exactly one user record" was earned from three
# measured rounds of an earlier session. Session 019fcb9a then ran THREE
# CALLS on 2026-08-04 - one fresh, then two resumes - and its SECOND
# RESUME carried the client's instructions preamble AND the brief, a
# preamble identical to the one at that session's own start. The rule
# BLOCKED a legitimate round. A claim wider than its evidence, inside the
# tool built to refuse those.
#
# The replacement was about IDENTITY, not arithmetic: at most two user
# records, and a record in front of the brief had to be one THIS CLIENT
# ALREADY EMITTED in this session. THE FIELD FALSIFIED THAT TOO, on
# 2026-08-14: a resume across a day boundary carried a REFRESHED preamble
# - a later date, the instructions block absent - and a paid round was
# discarded unread. Identity is now the FIRST of two paths. The second
# recognises a client environment preamble by STRUCTURE and confirms it by
# VALUE: every field but `current_date` canonically equal to the same
# field in this session's own baseline envelope, and the date bounded
# below by the baseline's and above by today. Novel text still cannot get
# in front of the reviewer; a bounded novel DATE can, and nothing else.
# Comparing against the session's first user record needs the PREFIX, so
# the prefix is read only as far as that record - a bounded read near the
# top of the file, not the cumulative whole.
if ($Resume) {
    if ($userRecords.Count -gt 2) {
        Fail ("a resumed slice may carry at most two user records, the " +
              "client's instructions preamble and the brief, found " +
              $userRecords.Count)
    }
}
# A FRESH slice carried exactly TWO on every measured round: the client's
# instructions preamble and the brief. The same argument that earned the
# resume bound earns this one, and leaving it out was unearned width - an
# unexplained user record before the brief is unattributed text in front
# of the reviewer, which is the class this binding exists to refuse.
if ($Fresh -and $userRecords.Count -ne 2) {
    Fail ("a fresh slice must carry exactly two user records, the client's" +
          " instructions preamble and the brief, found " + $userRecords.Count)
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

if ($Resume -and $userRecords.Count -eq 2) {
    # VALIDATED AFTER THE BRIEF, DELIBERATELY. Run before it, this test
    # reads a slice ordered [brief, extra] as though the brief were the
    # preamble and reports the wrong direction. The brief is proved
    # present, unique and last above; only then is there a record that is
    # meaningfully "in front of" it.
    # DECODE THE PREFIX; DO NOT RECONSTRUCT ITS LENGTH. The scan that
    # stood here rebuilt a byte offset from each decoded line plus a
    # hardcoded one-byte terminator. ReadLine strips BOTH bytes of a
    # CRLF, so on a CRLF rollout the count ran one byte short per line,
    # the boundary guard below did not fire in time, and the scan read
    # into THIS call's slice - taking the slice's own record ahead of the
    # brief as the client's preamble, comparing it against itself, and
    # returning clean for text the client never sent. Measured
    # 2026-08-15: 203 CRLF prefix lines with no readable user record were
    # enough, and no LF count reproduced it. The prefix bytes are already
    # in memory, so they are split by exactly the rule the slice is split
    # by above, which also removes the byte order mark divergence.
    $prefixPreamble = $null
    $prefixText = $null
    try {
        $prefixStrict = New-Object System.Text.UTF8Encoding($false, $true)
        $prefixText = $prefixStrict.GetString($bytes, 0, $sliceOffset)
    } catch {
        Fail ("the resumed rollout's prefix does not decode as strict " +
              "UTF-8, so the client's own preamble cannot be read: " +
              $_.Exception.Message)
    }
    if ($prefixText.Length -gt 0 -and [int][char]$prefixText[0] -eq 0xFEFF) {
        # A byte order mark at the start of the file is a file-level
        # artifact and not part of any record, exactly as above.
        $prefixText = $prefixText.Substring(1)
    }
    $prefixParts = $prefixText.Split("`n")
    # The final element is the tail after the last terminator, never a
    # record - the prefix ends at a record boundary the prior state
    # measured.
    # THE SAME GATE AS EVERY OTHER LINE, AND IT REFUSES RATHER THAN
    # SKIPS. This scan used to walk past any line it could not read, so a
    # malformed FIRST user record made it adopt the NEXT one - round
    # one's brief - as the client's preamble, and a slice repeating that
    # record passed identity and bound clean. Measured 2026-08-16 with a
    # user record followed by a non-breaking space, the shape the suite
    # already knows parses but fails the object-line gate. The baseline
    # every later comparison rests on must be the record the contract
    # names, so an unreadable line before it stops the round.
    for ($p = 0; $p -lt $prefixParts.Length - 1; $p++) {
        $ln = $prefixParts[$p].TrimEnd("`r")
        $cand = $null
        if ($ln.TrimStart($script:JsonWs).StartsWith("{")) {
            try { $cand = $ln | ConvertFrom-Json } catch { $cand = $null }
        }
        $lineFault = $null
        if ($null -eq $cand) {
            $lineFault = "it is not a JSON object"
        } else {
            $lineFault = Get-JsonObjectLineFault $ln $cand
        }
        if ($lineFault) {
            Fail ("the resumed rollout's prefix carries an unreadable " +
                  "record at line " + ($p + 1) + ", before the client's " +
                  "own preamble, so the record this slice must be " +
                  "measured against cannot be identified: " + $lineFault)
        }
        if (Test-RecordIsUserMessage $cand) {
            $prefixPreamble = Get-UserText $cand
            break
        }
    }
    $extra = Get-UserText $userRecords[0]
    if ($null -eq $prefixPreamble -or $null -eq $extra) {
        Fail ("a resumed slice carries a user record in front of the brief " +
              "that does not repeat the client's own preamble from this " +
              "session, so it is unattributed text in front of the reviewer")
    }
    if ((Get-CanonicalSha256 $extra) -ne (Get-CanonicalSha256 $prefixPreamble)) {
        # NOT IDENTICAL IS NOT THE SAME AS NOVEL. Measured 2026-08-14:
        # a resume across a day boundary carried a REFRESHED preamble -
        # a later date, and the instructions block absent - and the
        # identity rule discarded a paid round unread. A preamble
        # recognised by structure and confirmed field by field against
        # this session's own baseline falls inside the measured and
        # derived bound; every value but the date is text this session
        # already carried, and the date is bounded at both ends.
        # Anything else still fails here.
        $fault = Get-RefreshedPreambleFault $extra $prefixPreamble
        if ($fault) {
            Fail ("a resumed slice carries a user record in front of the " +
                  "brief that neither repeats the client's own preamble " +
                  "from this session nor reads as a refreshed one: it " +
                  $fault)
        }
    }
}

if ($Fresh) {
    # VALIDATED AFTER THE BRIEF, for the same reason the resumed check
    # above is: run before it, a slice ordered [brief, extra] is tested
    # as though the brief were the preamble and reports the wrong
    # direction. The count rule above guarantees exactly two user
    # records and the checks above guarantee the brief is the last, so
    # the record at index 0 is the one in front of it.
    #
    # WHY THIS EXISTS. The fresh path bounded that record by COUNT and
    # never checked what it was, so arbitrary text bound clean -
    # measured 2026-08-16 with a control. And whatever binds here
    # becomes the BASELINE every later resumed round in this session is
    # measured against, through both the identity path and the
    # structural refresh path, so a miss admits the session rather than
    # one round. This is a baseline admission gate.
    $lead = Get-UserText $userRecords[0]
    if ($null -eq $lead) {
        Fail ("a fresh slice carries a record in front of the brief that is " +
              "not a text-only user record, so it cannot be the client's " +
              "own environment preamble")
    }
    $freshFault = Get-FreshPreambleFault $lead
    if ($freshFault) {
        Fail ("a fresh slice carries a record in front of the brief that " +
              "does not read as the client's own environment preamble: it " +
              $freshFault)
    }
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
