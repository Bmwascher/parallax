# codex-context-probe.ps1 - render the model-visible prompt codex would be
# given from a working directory, and classify every instruction source it
# reveals.
#
# Preflight 3 has only ever enumerated the REVIEWED TREE. Every source that
# hijacked a review on 2026-07-28 - the user's codex plugin cache, the
# user's own skills directory, the global AGENTS.md - lives on the
# reviewer's machine, outside any tree the old check could see. This script
# reads what the reviewer actually receives instead of listing the sources
# somebody thought of.
#
# It spends no tokens: `codex debug prompt-input` renders the prompt and
# calls no model.
#
# EVERY failure direction lands on blocked. An unmade, failed, or
# unreadable measurement is never reported as a clean one.
#
# Windows PowerShell 5.1 compatible, ASCII ONLY.
#
# Exit codes: 0 clean, 1 blocked (reason on stdout), 2 script error.
param(
    [Parameter(Mandatory = $true)][string]$WorkDir,
    [switch]$SuppressSkills,
    [string]$OverrideOut,
    [switch]$Json,
    [string]$CodexCommand = "codex"
)

function Get-PromptText($raw) {
    # `codex debug prompt-input` emits a JSON list of messages, each with a
    # content list of {type,text}. Anything else is a shape change: throw,
    # because a parser that shrugs and returns "" would report a machine
    # loaded with skills as clean.
    $doc = $null
    try {
        $doc = $raw | ConvertFrom-Json
    } catch {
        throw [System.FormatException]::new(
            "prompt-input output is not JSON")
    }
    if ($null -eq $doc) {
        throw [System.FormatException]::new("prompt-input output was empty")
    }
    $items = @($doc)
    if ($items.Count -eq 0) {
        throw [System.FormatException]::new("prompt-input returned no messages")
    }
    $parts = New-Object System.Collections.ArrayList
    foreach ($item in $items) {
        if ($item.PSObject.Properties.Name -notcontains "content") {
            throw [System.FormatException]::new(
                "prompt-input message has no content list")
        }
        foreach ($chunk in @($item.content)) {
            # A chunk with no text is NOT skipped. Skipping it would let an
            # unknown chunk family carry instructions past this parser
            # while one surviving text chunk kept the run looking clean.
            if ($chunk.PSObject.Properties.Name -notcontains "text") {
                throw [System.FormatException]::new(
                    "prompt-input carried a content chunk with no text field")
            }
            [void]$parts.Add([string]$chunk.text)
        }
    }
    if ($parts.Count -eq 0) {
        throw [System.FormatException]::new(
            "prompt-input carried no text chunks")
    }
    return ($parts -join "`n")
}

function Get-SkillReport($text) {
    # BlockPresent and Entries are reported separately on purpose. An
    # ABSENT block is the success state once suppression has run; a
    # PRESENT block that yields no entries is a parse failure wearing the
    # same face, and the caller must be able to tell them apart.
    $present = $text.Contains("<skills_instructions>")
    $entries = New-Object System.Collections.ArrayList
    if ($present) {
        $start = $text.IndexOf("### Available skills")
        if ($start -ge 0) {
            $seg = $text.Substring($start)
            $stop = $seg.IndexOf("</skills_instructions>")
            if ($stop -gt 0) { $seg = $seg.Substring(0, $stop) }
            $rx = [regex]'(?m)^- ([A-Za-z0-9_:-]+):.*?\(file: ([^)]*)\)'
            foreach ($m in $rx.Matches($seg)) {
                [void]$entries.Add(@{
                    Name = $m.Groups[1].Value
                    Path = $m.Groups[2].Value
                })
            }
        }
    }
    return @{ BlockPresent = $present; Entries = @($entries) }
}

function Get-InstructionReport($text) {
    # The global AGENTS.md and the repo's AGENTS.md share one block,
    # separated by `--- project-doc ---`. The delimiter appears if and only
    # if the working directory's repo carries an AGENTS.md (verified both
    # ways 2026-07-28).
    $present = $text.Contains("<INSTRUCTIONS>")
    $project = $false
    if ($present) {
        $start = $text.IndexOf("<INSTRUCTIONS>")
        $seg = $text.Substring($start)
        $stop = $seg.IndexOf("</INSTRUCTIONS>")
        if ($stop -gt 0) { $seg = $seg.Substring(0, $stop) }
        $project = $seg.Contains("--- project-doc ---")
    }
    return @{ BlockPresent = $present; ProjectDoc = $project }
}

function Get-FeatureReport($text) {
    return @{
        Plugins = $text.Contains("<plugins_instructions>")
        RecommendedPlugins = $text.Contains("<recommended_plugins>")
        Apps = $text.Contains("<apps_instructions>")
    }
}

# Two lists, because the tag NAME and the container's literal delimiters
# are not the same string. `<permissions instructions>` opens with a
# space, so the grammar below reads its name as `permissions` while
# masking needs the full literal. Running an earlier version against the
# real prompt reported `permissions` as an unknown surface, which would
# have blocked every real review.
$script:KnownPromptBlocks = @(
    "permissions", "skills_instructions", "plugins_instructions",
    "apps_instructions", "recommended_plugins", "INSTRUCTIONS",
    "environment_context", "multi_agent_mode"
)
$script:KnownContainers = @(
    "permissions instructions", "skills_instructions",
    "plugins_instructions", "apps_instructions", "recommended_plugins",
    "INSTRUCTIONS", "environment_context", "multi_agent_mode"
)

function Hide-KnownContainer($text) {
    # Blank the CONTENTS of every known container before scanning for new
    # ones. <INSTRUCTIONS> carries the global and project AGENTS.md bodies
    # verbatim, and a user's AGENTS.md may legitimately contain a line
    # like `<role>`. Scanning the flattened text would call that a new
    # outer surface and block a review that is fine. Replacement is
    # space-for-character so every other offset in the string stays put.
    $masked = $text
    foreach ($name in $script:KnownContainers) {
        $open = "<" + $name + ">"
        $close = "</" + $name + ">"
        $from = 0
        while ($true) {
            $s = $masked.IndexOf($open, $from, [System.StringComparison]::Ordinal)
            if ($s -lt 0) { break }
            $bodyStart = $s + $open.Length
            $e = $masked.IndexOf($close, $bodyStart, [System.StringComparison]::Ordinal)
            if ($e -lt 0) {
                # An unterminated known container: mask to the end rather
                # than leaving its body scannable.
                $e = $masked.Length
            }
            $len = $e - $bodyStart
            $masked = $masked.Substring(0, $bodyStart) +
                (" " * $len) + $masked.Substring($bodyStart + $len)
            $from = $bodyStart + $len
        }
    }
    return $masked
}

function Get-UnknownPromptBlock($text) {
    # Tag grammar allows `-`, `.` and `:` in a name, attributes, a
    # self-closing form, and indentation. Those are TAGGED structures, so
    # missing them would be a gap rather than the accepted
    # untagged-prose limit.
    #
    # A BLOCK is an open/close pair or a self-closing tag. An opening tag
    # with no matching close is prose, not a surface: the real prompt's
    # multi-agent section documents a message format containing the lines
    # `<payload text>`, `<recipient>` and `<author>` inside a fenced code
    # block that sits in no container. Requiring the pair reported ZERO
    # unknown blocks across three real prompts while still catching
    # memories_instructions, a hyphenated tag and a self-closing one.
    $masked = Hide-KnownContainer $text
    $found = New-Object System.Collections.ArrayList
    $rx = [regex]'(?m)^[ \t]*<([A-Za-z][A-Za-z0-9_.:\-]*)((?:\s[^>]*?)?)(/?)>'
    foreach ($m in $rx.Matches($masked)) {
        $name = $m.Groups[1].Value
        if ($script:KnownPromptBlocks -contains $name) { continue }
        $selfClosing = ($m.Groups[3].Value -eq "/")
        if (-not ($selfClosing -or $masked.Contains("</" + $name + ">"))) {
            continue
        }
        if ($found -notcontains $name) { [void]$found.Add($name) }
    }
    return @($found)
}

function ConvertTo-ComparablePath($path) {
    # Compare on forward slashes with a trailing separator, so a sibling
    # directory whose name merely starts with the work dir - `repo-old`
    # next to `repo` - is not swallowed by a bare prefix test.
    $p = ([string]$path).Replace("\", "/").TrimEnd("/")
    return ($p + "/")
}

function Get-SkillScope($path, $workDir) {
    # FAIL CLOSED. Anything this function cannot place is `unknown`, which
    # the caller blocks on. An earlier revision returned `home` from the
    # default branch, so a relative path, a UNC path, an empty string or
    # any shape the parser mangled was filed as a benign environment note.
    $raw = [string]$path
    if ([string]::IsNullOrWhiteSpace($raw)) { return "unknown" }
    $norm = $raw.Replace("\", "/")
    # A locatable source is a rooted local path: `C:/...`. Anything else -
    # relative, UNC, a URI, an environment resource locator - cannot be
    # compared against the work dir at all.
    if ($norm -notmatch '^[A-Za-z]:/') { return "unknown" }
    if ($norm.Contains("/../")) { return "unknown" }
    # REPO is tested FIRST. A checkout under the user profile is the normal
    # case on Windows, so a home-first test would file a planted repo skill
    # as an environment note instead of stopping the gate.
    $p = ConvertTo-ComparablePath $norm
    $w = ConvertTo-ComparablePath $workDir
    if ($p.StartsWith($w, [System.StringComparison]::OrdinalIgnoreCase)) {
        return "repo"
    }
    if ($p -match "/\.codex/plugins/cache/") { return "plugin-cache" }
    return "home"
}

function New-SkillDisableOverride($entries) {
    # Forward slashes are load-bearing: with backslashes the value fails
    # TOML parsing, falls back to a raw string, and codex rejects it with
    # `invalid type: string` (probed 2026-07-28).
    #
    # SINGLE quotes, which are TOML literal strings, and not double
    # quotes. Windows PowerShell 5.1 STRIPS embedded double quotes when it
    # passes an argument to a native command, so a double-quoted value
    # reached codex as `{path=C:/...}` and was rejected with that same
    # `invalid type: string`. PowerShell 7 quotes it correctly, so this
    # failed on one host and passed on the other - the 0.16.1 lesson in a
    # new place. Probed both hosts 2026-07-28: single quotes work on both.
    #
    # A TOML literal string cannot escape its own delimiter, so a path
    # containing a single quote has no representation here. That blocks
    # rather than silently emitting a broken override.
    $parts = New-Object System.Collections.ArrayList
    foreach ($e in @($entries)) {
        $p = ([string]$e.Path).Replace("\", "/")
        if ($p.Contains("'")) {
            throw [System.FormatException]::new(
                "skill path contains a single quote and cannot be written" +
                " as a TOML literal string: " + $p)
        }
        [void]$parts.Add("{path='" + $p + "',enabled=false}")
    }
    return ("skills.config=[" + ($parts -join ",") + "]")
}

function Write-Blocked($reason, $asJson) {
    if ($asJson) {
        Write-Output (ConvertTo-Json @{ status = "blocked"; reason = $reason } -Compress)
    } else {
        Write-Output ("BLOCKED: " + $reason)
    }
    exit 1
}

function Test-PromptShape($text, $asJson) {
    # Every shape rule, applied to BOTH renders. An earlier revision ran
    # these on the first pass only, so a block appearing only under the
    # generated override - or an apps block reappearing on the second pass
    # - passed silently.
    $instructions = Get-InstructionReport $text
    if (-not $instructions.BlockPresent) {
        Write-Blocked ("the <INSTRUCTIONS> block is missing - the prompt" +
            " shape changed and this parser no longer describes it") $asJson
    }
    $features = Get-FeatureReport $text
    if ($features.Plugins -or $features.RecommendedPlugins -or $features.Apps) {
        Write-Blocked ("the plugin or apps feature is advertising itself" +
            " despite --disable plugins --disable apps") $asJson
    }
    $unknown = Get-UnknownPromptBlock $text
    if ($unknown.Count -gt 0) {
        Write-Blocked ("unrecognized prompt block(s): " +
            ($unknown -join ", ") + " - a new instruction family is" +
            " reaching the reviewer and this parser has no rule for it") $asJson
    }
    return $instructions
}

function Invoke-PromptInput($codex, $workDir, $override) {
    $probeArgs = @("debug", "prompt-input",
                   "--disable", "plugins", "--disable", "apps")
    if ($override) { $probeArgs += @("-c", $override) }
    $probeArgs += "probe"
    $out = $null
    $code = 0
    # Decode the child's stdout as UTF-8. Windows PowerShell 5.1 defaults
    # to the console code page, which turns a non-ASCII character in a
    # skill path into mojibake BEFORE this script ever sees it - and the
    # override would then be written, hashed and dispatched in that
    # corrupted form, with every check passing. Writing the artifact as
    # strict UTF-8 is pointless if the value arrives already broken.
    $priorOut = [Console]::OutputEncoding
    Push-Location $workDir
    try {
        [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
        # A .ps1 stub is invoked IN-PROCESS. Routing it through
        # `powershell -File` would serialize the arguments through
        # command-line parsing, which strips the double quotes inside the
        # skills.config value - so the test harness, not the real
        # transport, would decide what the stub received. Native
        # invocation binds the array as-is; a real codex.exe gets the same
        # array through PowerShell's native-command quoting.
        $out = & $codex @probeArgs 2>$null
        $code = $LASTEXITCODE
        # An in-process .ps1 that returns without calling `exit` leaves
        # $LASTEXITCODE untouched, which reads as an empty string rather
        # than 0. A native executable always sets it, so this branch
        # cannot mask a real non-zero exit.
        if (($null -eq $code) -or ($code -eq "")) { $code = 0 }
    } finally {
        [Console]::OutputEncoding = $priorOut
        Pop-Location
    }
    # JOIN, never `Out-String`. Out-String formats for a console and WRAPS
    # at the host width, which inserts newlines into the middle of a skill
    # entry and breaks the line-anchored parse. Short fixtures never
    # trigger it; the first live run did. A native command's output is
    # already an array of lines, so joining reproduces the stream exactly.
    return @{ Output = (@($out) -join "`n"); ExitCode = $code }
}

$toplevel = $true

if (-not (Test-Path $WorkDir)) {
    Write-Output "ERROR: $WorkDir does not exist"
    exit 2
}
$WorkDir = (Resolve-Path $WorkDir).Path

# Freshness is checked BEFORE the first codex call, not at write time.
# WriteAllBytes overwrites silently, so a stale artifact from a previous
# debate would be replaced without anyone learning it had been there.
if ($OverrideOut -and (Test-Path $OverrideOut)) {
    Write-Output ("ERROR: $OverrideOut already exists - a stale override" +
        " reads exactly like a fresh one")
    exit 2
}

$pass1 = Invoke-PromptInput $CodexCommand $WorkDir $null
if ($pass1.ExitCode -ne 0) {
    Write-Blocked ("codex debug prompt-input exited " + $pass1.ExitCode +
        " - the probe could not be taken, so nothing is known about the" +
        " reviewer's context") $Json
}
$text = $null
try {
    $text = Get-PromptText $pass1.Output
} catch {
    Write-Blocked ("could not read the prompt-input output: " +
        $_.Exception.Message) $Json
}

$instructions = Test-PromptShape $text $Json
$skills = Get-SkillReport $text

# The FIRST pass runs with the feature flags and no override, so the skills
# block must be there. Its absence here is a shape change, not a success.
# Absence only means success on the SECOND pass, after the override.
if (-not $skills.BlockPresent) {
    Write-Blocked ("the skills block is missing on the first pass - the" +
        " prompt shape changed, and this parser cannot tell an empty" +
        " machine from one it can no longer read") $Json
}

$repoScoped = @()
$cacheScoped = @()
$homeScoped = @()
$unknownScoped = @()
foreach ($entry in $skills.Entries) {
    switch (Get-SkillScope $entry.Path $WorkDir) {
        "repo"         { $repoScoped += $entry }
        "plugin-cache" { $cacheScoped += $entry }
        "home"         { $homeScoped += $entry }
        default        { $unknownScoped += $entry }
    }
}
if ($unknownScoped.Count -gt 0) {
    Write-Blocked ("skill source(s) could not be placed: " +
        (($unknownScoped | ForEach-Object { "'" + $_.Path + "'" }) -join "; ") +
        " - an unplaceable source is never a benign environment note") $Json
}
if ($repoScoped.Count -gt 0) {
    Write-Blocked ("skill(s) advertised from inside the reviewed tree: " +
        (($repoScoped | ForEach-Object { $_.Path }) -join "; ") +
        " - remediate in the mirror") $Json
}
if ($instructions.ProjectDoc) {
    Write-Blocked ("the reviewed tree's AGENTS.md is being ingested as" +
        " instructions - remediate in the mirror") $Json
}
if ($cacheScoped.Count -gt 0) {
    Write-Blocked ("skill(s) still advertised from the codex plugin cache: " +
        (($cacheScoped | ForEach-Object { $_.Path }) -join "; ")) $Json
}

# The prompt does NOT state where its global instruction text came from,
# and the reviewer's own self-report of that path was wrong on 2026-07-28.
# So resolve the conventional location ourselves and report it only when
# the file is actually there; otherwise report nothing rather than a guess.
$globalPath = ""
$codexHome = $env:CODEX_HOME
if (-not $codexHome) {
    $codexHome = Join-Path $env:USERPROFILE ".codex"
}
$candidate = Join-Path $codexHome "AGENTS.md"
if (Test-Path $candidate) { $globalPath = (Resolve-Path $candidate).Path }

$before = $skills.Entries.Count
$after = $before
$overridePath = ""
$overrideHash = ""
if ($SuppressSkills) {
    if (-not $OverrideOut) {
        Write-Blocked ("-SuppressSkills without -OverrideOut verifies a" +
            " configuration nothing can dispatch") $Json
    }
    $override = $null
    try {
        $override = New-SkillDisableOverride $skills.Entries
    } catch {
        Write-Blocked ("could not build the disable override: " +
            $_.Exception.Message) $Json
    }
    $pass2 = Invoke-PromptInput $CodexCommand $WorkDir $override
    if ($pass2.ExitCode -ne 0) {
        Write-Blocked ("the suppression pass exited " + $pass2.ExitCode) $Json
    }
    $text2 = $null
    try {
        $text2 = Get-PromptText $pass2.Output
    } catch {
        Write-Blocked ("could not read the suppression pass: " +
            $_.Exception.Message) $Json
    }
    [void](Test-PromptShape $text2 $Json)
    $skills2 = Get-SkillReport $text2
    $after = $skills2.Entries.Count
    # ABSENCE of the block is the proof, not a zero count. A block that is
    # present but unreadable also counts zero, and calling that clean is
    # the false-clean direction this script may never produce.
    if ($skills2.BlockPresent) {
        Write-Blocked ("the skills block is still present after suppression" +
            " (" + $after + " entries parsed) - suppression did not take," +
            " or the block can no longer be read") $Json
    }
    if ($after -ne 0) {
        Write-Blocked ("the reviewer still advertises " + $after +
            " skill(s) after suppression; the declared residue is empty") $Json
    }
    # THE HANDOFF. The dispatch must carry this exact value. A probe that
    # verifies a configuration the reviewer never receives has measured
    # nothing.
    #
    # EXACT BYTES, no terminator, STRICT UTF-8 and no BOM. ASCII encoding
    # maps every non-ASCII character to `?`, so a skill path carrying one
    # would be silently corrupted and the hash would then faithfully
    # authenticate the corrupted value. This script's own SOURCE stays
    # ASCII; that is a separate rule about the file, not about the data it
    # writes.
    $enc = New-Object System.Text.UTF8Encoding($false, $true)
    $bytes = $enc.GetBytes($override)
    [System.IO.File]::WriteAllBytes($OverrideOut, $bytes)
    $overridePath = (Resolve-Path $OverrideOut).Path
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $overrideHash = ([System.BitConverter]::ToString(
        $sha.ComputeHash($bytes)) -replace '-', '').ToLower()
}

$report = @{
    status = "clean"
    reason = ""
    skills_before = $before
    skills_after = $after
    repo_scoped = $repoScoped.Count
    plugin_cache_scoped = $cacheScoped.Count
    home_scoped = $homeScoped.Count
    unknown_scoped = $unknownScoped.Count
    global_agents_md = $instructions.BlockPresent
    global_agents_md_path = $globalPath
    project_agents_md = $instructions.ProjectDoc
    override_file = $overridePath
    override_sha256 = $overrideHash
}
if ($Json) {
    Write-Output (ConvertTo-Json $report -Compress)
} else {
    Write-Output ("clean: " + $before + " skill(s) measured, " + $after +
        " after suppression; global AGENTS.md present: " +
        $instructions.BlockPresent)
}
exit 0
