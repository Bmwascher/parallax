# codex-context-probe.ps1 - render the model-visible prompt codex would be
# given from a working directory, classify every ADVERTISED SKILL by the
# directory it came from, and check the named instruction and feature
# blocks around them. It does not classify instruction TEXT, and it does
# not read the reviewer's tool surface at all - see the
# `client-probe-scope-limit` region in SKILL.md, and backlog item 7.
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

function Test-FamilyMentioned($text, $name) {
    # THE BLUNT RULE, and the whole point of it is that there is nothing
    # to parse. Not "is there a container of this family", which is a
    # question about structure, but "does this name occur at all",
    # case-insensitively, anywhere in the render.
    #
    # WHY THE STRUCTURAL ANSWER WAS ABANDONED. Six panel rounds on
    # 2026-07-28 each found a new shape that slipped past the previous
    # round's structural rule, and five of those shapes reached a CLEAN
    # report: a container nested inside a masked body, the same nested in
    # another family, a self-closing tag, a close carrying one extra
    # space, and a tag whose attribute value contained a closing bracket.
    # Every one was a defect in telling a real block from a quoted one.
    # Flattened text does not carry that distinction, so the parser was
    # being asked a question its input cannot answer, and each answer
    # bought one more round.
    #
    # This rule cannot produce a false clean. There is no shape to find,
    # no boundary to get wrong, and no masking to see past. It can only
    # produce a false BLOCK, which is loud, names its own cause, and the
    # user fixes by rewording one line of their own file.
    #
    # ACCEPTED LIMIT, and it is a real one: a reviewer whose global
    # AGENTS.md or whose skill descriptions mention any of these four
    # names cannot run a review until the mention is reworded. Measured
    # 2026-07-28 on this machine, the author's own global file contains
    # none of the four in 1009 characters.
    return ($text.IndexOf($name,
        [System.StringComparison]::OrdinalIgnoreCase) -ge 0)
}

function Get-SkillReport($text) {
    # BlockPresent and Entries are reported separately on purpose. An
    # ABSENT block is the success state once suppression has run; a
    # PRESENT block that yields no entries is a parse failure wearing the
    # same face, and the caller must be able to tell them apart.
    #
    # PRESENCE IS A MENTION, NOT A STRUCTURE. See Test-FamilyMentioned for
    # why the structural answer was abandoned. On the FIRST render the
    # block is genuinely there, so a stray mention costs nothing: the
    # entry parse below either finds entries or the caller stops on a
    # present-but-empty block. On the SECOND render a mention is exactly
    # what must not be there, and that is the check this rule exists for.
    $present = Test-FamilyMentioned $text "skills_instructions"
    $entries = New-Object System.Collections.ArrayList
    $malformed = $false
    $firstBad = ""
    if ($present) {
        $start = $text.IndexOf("### Available skills")
        if ($start -ge 0) {
            $seg = $text.Substring($start)
            $stop = $seg.IndexOf("</skills_instructions>")
            if ($stop -gt 0) { $seg = $seg.Substring(0, $stop) }
            # The path capture is GREEDY to the LAST `)` on its own line,
            # not up to the first one. `[^)]*` truncated
            # `C:/Program Files (x86)/x/SKILL.md` to `C:/Program Files (x86`,
            # which still looks like a rooted path, so it was filed as a
            # harmless home note instead of blocking - and the generated
            # disable entry named a file that does not exist. Found by the
            # mode-diff review, 2026-07-28. `Program Files (x86)` is an
            # ordinary Windows path, not a contrived one.
            # The description prefix is GREEDY, so the LAST `(file: ` on the
            # line is the path delimiter. Counting the marker instead and
            # demanding exactly one rejected a legitimate description that
            # merely mentions `(file: `, since skill descriptions are free
            # text. Mode-diff round 3, 2026-07-28.
            $rx = [regex]'^- ([A-Za-z0-9_:-]+):.*\(file: (.+)\)[ \t]*$'
            # A SECOND entry joined onto the same line is what needs
            # catching, and the detector must match a COMPLETE earlier
            # entry - its own file marker ending in SKILL.md - followed by
            # the next entry start. A bare close paren followed by
            # bullet-like prose is not that: the description
            # `Use when output is (done) - next: retry.` matched the
            # earlier form and was marked malformed. Mode-diff round 4,
            # 2026-07-28. The non-greedy `.*?` is what lets a path
            # containing its own parentheses reach the SKILL.md anchor.
            $joined = [regex]'(?i)\(file: .*?SKILL\.md\)[ \t]+- [A-Za-z0-9_:-]+:'
            # AUDIT EVERY ENTRY-LOOKING LINE. A line that fails the whole
            # grammar is otherwise dropped in silence, which makes the
            # FIRST measurement wrong, and no later suppression check
            # repairs a measurement that was never right.
            foreach ($line in ($seg -split "`n")) {
                $trimmed = $line.TrimEnd("`r")
                if ($trimmed -notmatch '^- [A-Za-z0-9_:-]+:') { continue }
                if ($joined.IsMatch($trimmed)) {
                    $malformed = $true
                    if (-not $firstBad) { $firstBad = $trimmed }
                    continue
                }
                $m = $rx.Match($trimmed)
                if (-not $m.Success) {
                    $malformed = $true
                    if (-not $firstBad) { $firstBad = $trimmed }
                    continue
                }
                [void]$entries.Add(@{
                    Name = $m.Groups[1].Value
                    Path = $m.Groups[2].Value
                })
            }
        }
    }
    return @{ BlockPresent = $present; Entries = @($entries)
              Malformed = $malformed; FirstMalformedLine = $firstBad }
}

function Get-InstructionReport($text) {
    # The global AGENTS.md and the repo's AGENTS.md share one block,
    # separated by `--- project-doc ---`. The delimiter appears if and only
    # if the working directory's repo carries an AGENTS.md (verified both
    # ways 2026-07-28).
    #
    # The delimiter counts only where it STANDS ALONE ON ITS OWN LINE. The
    # segment searched is exactly the region that carries the user's global
    # AGENTS.md verbatim, so a `Contains` test made a global file that
    # merely mentions the delimiter report a project doc, and the run then
    # stopped with "the reviewed tree's AGENTS.md is being ingested" - the
    # wrong tree and the wrong diagnosis. Found by the mode-diff PANEL,
    # 2026-07-28. Masking is not available here: the real delimiter lives
    # inside this same body, so blanking the body would erase the
    # measurement itself. Both fixtures place the real delimiter alone on
    # its own line, which is how the renderer emits it.
    $present = $text.Contains("<INSTRUCTIONS>")
    $project = $false
    if ($present) {
        $start = $text.IndexOf("<INSTRUCTIONS>")
        $seg = $text.Substring($start)
        $stop = $seg.IndexOf("</INSTRUCTIONS>")
        if ($stop -gt 0) { $seg = $seg.Substring(0, $stop) }
        $project = [regex]::IsMatch($seg,
            "(?m)^[ \t]*--- project-doc ---[ \t]*\r?$")
    }
    return @{ BlockPresent = $present; ProjectDoc = $project }
}

function Get-FeatureReport($text) {
    # Same blunt rule as the skills block, and here it applies to BOTH
    # renders: the two flags are supposed to remove these three families
    # outright, so any mention of one is either the feature still being
    # advertised or a prompt this parser no longer describes. Neither is a
    # clean result.
    return @{
        Plugins = Test-FamilyMentioned $text "plugins_instructions"
        RecommendedPlugins = Test-FamilyMentioned $text "recommended_plugins"
        Apps = Test-FamilyMentioned $text "apps_instructions"
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
# INSTRUCTIONS IS MASKED FIRST, and the order here is the masking order.
# It is the one container carrying USER-AUTHORED text: the global and
# project AGENTS.md bodies, verbatim. With it masked later, a house rule
# that merely mentions `<skills_instructions>` in prose was read as an
# unterminated container of that name and blocked a legitimate review.
# Reproduced 2026-07-28, mode-diff round 3. The order still matters even
# though the pairing rule below is now count-based: masking the
# user-authored body first removes any quoted delimiter of ANOTHER
# container before that container's own count is taken.
$script:KnownContainers = @(
    "INSTRUCTIONS", "permissions instructions", "skills_instructions",
    "plugins_instructions", "apps_instructions", "recommended_plugins",
    "environment_context", "multi_agent_mode"
)

function Hide-KnownContainer($text, $only, $quiet) {
    # Blank the CONTENTS of every known container before scanning for new
    # ones. <INSTRUCTIONS> carries the global and project AGENTS.md bodies
    # verbatim, and a user's AGENTS.md may legitimately contain a line
    # like `<role>`. Scanning the flattened text would call that a new
    # outer surface and block a review that is fine. Replacement is
    # space-for-character so every other offset in the string stays put.
    #
    # EACH KNOWN CONTAINER MUST APPEAR EXACTLY ONCE, OR NOT AT ALL.
    # Anything else is ambiguous and stops the run. Three earlier revisions
    # each tried to be clever about WHICH delimiter to pair with, and each
    # traded one wrong answer for another: first-match ended the span at a
    # closing marker a user had merely quoted, and last-match then ran the
    # span past a genuine outer block that followed the real close and
    # erased it before the scan. Both were found by the mode-diff review,
    # 2026-07-28, rounds 3 to 5. Flattened text cannot tell a quoted
    # delimiter from a real one, so the honest answer is to refuse the
    # ambiguity rather than to guess at it. Measured the same day against a
    # real prompt: every container present in it occurs exactly once, open
    # and close, so this rule costs nothing on real input.
    # `$only` runs this over a SUBSET, in two stages. The user-authored
    # body is masked and validated on its own first, so that a house rule
    # QUOTING a malformed known tag is blanked before the exactness scan
    # ever sees it, while a malformed tag in real prompt structure still
    # reaches that scan ahead of the count rule below. Mode-diff round 6,
    # 2026-07-28: with exactness on fully raw text, the legitimate line
    # `Never emit <skills_instructions version="2">.` inside a user's own
    # AGENTS.md blocked the review.
    $names = $script:KnownContainers
    if ($only) { $names = @($only) }
    $masked = $text
    foreach ($name in $names) {
        $open = "<" + $name + ">"
        $close = "</" + $name + ">"
        $opens = ([regex]::Matches($masked, [regex]::Escape($open))).Count
        $closes = ([regex]::Matches($masked, [regex]::Escape($close))).Count
        # `$quiet` masks only what is UNAMBIGUOUS and reports nothing. It
        # is the pass that runs before the known-tag exactness scan, so
        # that arbitrary free text inside a validated body - a skill
        # DESCRIPTION is free text too, not just the global AGENTS.md -
        # cannot be read as outer structure. A malformed outer tag has no
        # exact 1/1 span, so its container is not masked here and stays
        # visible to that scan. Mode-diff round 7, 2026-07-28: with only
        # INSTRUCTIONS masked first, the legitimate entry
        # `- example: Never emit <apps_instructions version="2">. (file: ...)`
        # blocked.
        if (($opens -eq 0) -and ($closes -eq 0)) { continue }
        if (($opens -ge 1) -and ($closes -eq 0)) {
            if ($quiet) { continue }
            throw [System.FormatException]::new(
                "the <" + $name + "> container never closes - the" +
                " remainder of the prompt cannot be scanned")
        }
        if (($opens -ne 1) -or ($closes -ne 1)) {
            if ($quiet) { continue }
            throw [System.FormatException]::new(
                "the <" + $name + "> container's boundaries are ambiguous" +
                " (" + $opens + " opening and " + $closes + " closing" +
                " markers) - flattened text cannot tell a quoted delimiter" +
                " from a real one, so which span is the container is a" +
                " guess")
        }
        $s = $masked.IndexOf($open, [System.StringComparison]::Ordinal)
        $bodyStart = $s + $open.Length
        $e = $masked.IndexOf($close, [System.StringComparison]::Ordinal)
        if ($e -lt $bodyStart) {
            if ($quiet) { continue }
            throw [System.FormatException]::new(
                "the <" + $name + "> container closes before it opens")
        }
        $len = $e - $bodyStart
        $masked = $masked.Substring(0, $bodyStart) +
            (" " * $len) + $masked.Substring($bodyStart + $len)
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
    # THE PIPELINE IS: quiet mask -> exactness -> validating mask -> scan.
    #
    # Exactness runs on the QUIETLY MASKED text, not on raw text and not
    # on the validated mask. Each position is load-bearing and each was
    # established by a reproduction:
    #
    # - Ahead of the VALIDATING mask, because that mask counts delimiters,
    #   so a non-exact known tag would trip the count rule first and report
    #   an ambiguous container instead of the real problem - and the
    #   exactness rule, which is what closes the attributed-tag false
    #   clean, could then rot with all of its tests still green for the
    #   wrong reason (round 5).
    # - Behind the QUIET mask, because every free-text region the renderer
    #   wraps - the global AGENTS.md, and every skill description - may
    #   legitimately quote a malformed tag, and did (rounds 6 and 7).
    #
    # A malformed OUTER tag has no exact 1/1 span, so the quiet mask
    # leaves its container alone and the tag is still visible here.
    #
    # KNOWN NAMES ARE CHECKED ANYWHERE, NOT ONLY AT A LINE START. Every
    # dedicated parser matches an EXACT literal, so any other form of a
    # known tag is invisible to all of them. This rule was line-anchored
    # until round 3, and a tag with text before it on the line escaped
    # both it and the parsers: a second pass carrying all 29 entries under
    # `prefix <skills_instructions version="2">` reported skills_after 0
    # and exit 0. Reproduced 2026-07-28, mode-diff round 3, after round 2's
    # line-anchored form of this same rule. The general scan below lost
    # its own anchor at round 6, for the same reason.
    #
    # The comparison is against WHOLE LITERALS rather than a test for the
    # presence of attributes, because `<permissions instructions>` is a
    # legitimate container whose name parses as `permissions` with
    # ` instructions` read as an attribute. An attribute test would block
    # every real review.
    #
    # NAME RECOGNITION IS CASE-INSENSITIVE, THE LITERAL ALLOWLIST IS NOT.
    # The two must differ. With both case-sensitive,
    # `<SKILLS_INSTRUCTIONS version="2">` matched neither this scan nor the
    # exact parsers, and the general scan below then skipped it because
    # PowerShell's `-contains` is case-INSENSITIVE and called the name
    # known. Confirmed mechanically 2026-07-28, mode-diff round 4: for the
    # list @("skills_instructions"), `-contains "SKILLS_INSTRUCTIONS"` is
    # True while `-ccontains` is False. Recognizing the name loosely and
    # then demanding the exact literal is what closes it.
    $knownOpen = @()
    foreach ($c in $script:KnownContainers) { $knownOpen += ("<" + $c + ">") }
    $names = ($script:KnownPromptBlocks | ForEach-Object { [regex]::Escape($_) }) -join "|"
    $knownRx = [regex]("(?i)<(?:" + $names + ")\b[^>]*>")
    # STAGE 1: mask every known body whose span is UNAMBIGUOUS, reporting
    # nothing. Every free-text region the renderer wraps - the global
    # AGENTS.md inside INSTRUCTIONS, and every skill description inside
    # the skills container - is now blank, while a malformed outer tag,
    # which has no exact span, is still visible.
    $bodyMasked = Hide-KnownContainer $text $null $true
    foreach ($m in $knownRx.Matches($bodyMasked)) {
        if ($knownOpen -ccontains $m.Value) { continue }
        throw [System.FormatException]::new(
            "the known block " + $m.Value + " is not in the exact form" +
            " this parser reads, so every rule about it silently did" +
            " nothing")
    }

    # STAGE 2: mask again, this time VALIDATING every boundary, then look
    # for surfaces nobody enumerated.
    $masked = Hide-KnownContainer $text
    $found = New-Object System.Collections.ArrayList
    # NOT line-anchored. An inline `prefix <memories_instructions>x</...>`
    # returned zero unknown blocks and reached exit 0 with status clean.
    # Mode-diff round 6, 2026-07-28.
    #
    # What keeps ordinary prose out is the MASKING above, not this scan's
    # shape: every free-text region the renderer wraps is already blank by
    # the time this runs. The pair requirement only handles prose that
    # sits outside all of them, and it handles exactly one case - an
    # UNPAIRED mention, such as the real prompt's `<payload text>`,
    # `<recipient>` and `<author>` lines, which sit in no container.
    # Prose outside every masked body that carries an ORDERED pair, or a
    # self-closing tag, does block. That is an accepted limit recorded in
    # the design, not a claim that this scan never fires on prose.
    $rx = [regex]'<([A-Za-z][A-Za-z0-9_.:\-]*)((?:\s[^>]*?)?)(/?)>'
    foreach ($m in $rx.Matches($masked)) {
        $name = $m.Groups[1].Value
        if ($script:KnownPromptBlocks -contains $name) { continue }
        $selfClosing = ($m.Groups[3].Value -eq "/")
        # The close must come AFTER the open. `Contains` accepted a close
        # anywhere in the document, so the explanatory prose
        # `End with </example>; start with <example>` was read as a paired
        # block. That is not a pair in document order. Mode-diff round 7,
        # 2026-07-28, a false positive the unanchored scan exposed.
        $closesAfter = ($masked.IndexOf("</" + $name + ">",
            $m.Index + $m.Length, [System.StringComparison]::Ordinal) -ge 0)
        if (-not ($selfClosing -or $closesAfter)) { continue }
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
    # Every advertised entry names a SKILL.md. A capture that does not is a
    # shape this parser no longer describes - a truncation, or a changed
    # rendering - and belongs in the bucket that blocks, never in `home`.
    if ($norm -notmatch '(?i)/SKILL\.md$') { return "unknown" }
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
    # The feature markers use the blunt mention rule on RAW text. Six
    # panel rounds of structural rules for this same question each bought
    # one more round; see Test-FamilyMentioned. These three families are
    # supposed to be gone outright, so there is nothing here worth being
    # clever about.
    $features = Get-FeatureReport $text
    if ($features.Plugins -or $features.RecommendedPlugins -or $features.Apps) {
        Write-Blocked ("the plugin or apps feature is named in the" +
            " rendered prompt despite --disable plugins --disable apps." +
            " A mention is enough to stop the run: this check does not" +
            " parse structure, because six review rounds showed that" +
            " flattened text cannot tell a real block from a quoted one." +
            " If one of these names appears in your own AGENTS.md or in" +
            " a skill description, reword it") $asJson
    }
    $unknown = @()
    try {
        $unknown = Get-UnknownPromptBlock $text
    } catch {
        # An unterminated known container. Masking past it would hide every
        # later block from the scan, so the malformed prompt stops the run.
        Write-Blocked ("the prompt could not be scanned for new surfaces: " +
            $_.Exception.Message) $asJson
    }
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
# PRESENT and empty is a parse failure, and it is refused HERE rather than
# only on the second pass. codex does not render an empty skills block, so
# zero entries inside a present block means this parser can no longer read
# the entry lines - and every count downstream would then be a measured
# zero that measured nothing. Found by the mode-diff review, 2026-07-28.
if ($skills.Entries.Count -eq 0) {
    Write-Blocked ("the skills block is present but no entry could be read" +
        " - the entry format changed, so every count below would be a zero" +
        " this parser invented rather than measured") $Json
}
if ($skills.Malformed) {
    # ACCEPTED LIMIT, and it blocks rather than guessing. A skill
    # DESCRIPTION is free text, so a description that itself contains a
    # complete file marker followed by another entry start is
    # indistinguishable, in one flattened line, from two entries the
    # renderer joined. Mode-diff round 5, 2026-07-28, after round 4 had
    # already narrowed this detector once. Blocking is the safe direction
    # and the reason names the line, so a user can see what tripped it.
    Write-Blocked ("an entry line inside the skills block does not satisfy" +
        " the whole entry grammar, or reads as two entries on one line - " +
        " the measurement below would be missing or merging sources." +
        " First such line: " + $skills.FirstMalformedLine) $Json
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
#
# THIS RESOLUTION IS THE ONLY MEASUREMENT OF THE GLOBAL FILE, so both
# report fields below are derived from it. They used to carry the
# instruction BLOCK's presence instead - a value Test-PromptShape has
# already refused to let be false, which made `global_agents_md` a
# constant dressed as a measurement while its name claimed a fact about
# the user's file. Found by the mode-diff PANEL, 2026-07-28.
$globalPath = ""
$codexHome = $env:CODEX_HOME
$candidate = ""
# `-PathType Leaf` and `-LiteralPath` are each load-bearing, and both were
# measured on this machine 2026-07-28 (mode-diff PANEL). Without the type
# test, a DIRECTORY named AGENTS.md answers Test-Path and is reported as
# the user's global instruction file. Without -LiteralPath, a CODEX_HOME
# carrying a wildcard character is read as a pattern: a real
# `home[1]/AGENTS.md` answered False bare and True literal.
# THE WHOLE MEASUREMENT SITS IN ONE GUARD, and every cmdlet in it stops on
# error. Building the path and testing it were previously outside the
# guard, and neither stopped: a CODEX_HOME naming a provider that does not
# exist made `Join-Path` emit a non-terminating error and return empty,
# `Test-Path` then emit another, and the run continue to a clean report
# saying the user has no global AGENTS.md. Reproduced on both hosts,
# mode-diff PANEL round 4, 2026-07-28. A measurement that failed and one
# that came back negative are not the same fact, and only one of them is
# safe to publish.
try {
    # The default-location fallback is INSIDE the guard too. Left outside,
    # the comment above claimed every cmdlet was guarded while one was
    # not, and a description that overstates its own coverage is the class
    # of defect this cycle kept finding.
    if (-not $codexHome) {
        $codexHome = Join-Path $env:USERPROFILE ".codex" -ErrorAction Stop
    }
    $candidate = Join-Path $codexHome "AGENTS.md" -ErrorAction Stop
    if (Test-Path -LiteralPath $candidate -PathType Leaf -ErrorAction Stop) {
        $globalPath = (Resolve-Path -LiteralPath $candidate `
            -ErrorAction Stop).Path
    }
} catch {
    Write-Blocked ("whether the reviewer has a global AGENTS.md under " +
        $codexHome + " could not be determined: " + $_.Exception.Message +
        " - an unmade measurement is not an absent file") $Json
}

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
    # THE SECOND PASS KEEPS ITS OWN INSTRUCTION REPORT. An earlier revision
    # voided this return value, so the project-doc fact was measured on the
    # suppression render and thrown away, and the clean report below then
    # published the FIRST pass's stale value. A `--- project-doc ---` that
    # appears only under the generated override reached status clean and
    # exit 0 - the false-clean direction this script may never produce.
    # Found by the mode-diff PANEL, 2026-07-28; the both-renders rule this
    # violated is stated in Test-PromptShape's own opening comment.
    $instructions2 = Test-PromptShape $text2 $Json
    $skills2 = Get-SkillReport $text2
    $after = $skills2.Entries.Count
    # ABSENCE OF THE NAME is the proof, not a zero count and not the
    # absence of a well-formed block. A block that is present but
    # unreadable also counts zero, and every structural way of asking
    # "is a block still here" was defeated by a shape nobody had thought
    # of - five times, each inside the previous fix, over six panel
    # rounds on 2026-07-28. The name either appears in this render or it
    # does not, and that question has no edge cases.
    if ($skills2.BlockPresent) {
        Write-Blocked ("the skills family is still named in the render" +
            " after suppression (" + $after + " entries parsed) -" +
            " suppression did not take, the block can no longer be read," +
            " or one of the reviewer's own instruction sources mentions" +
            " skills_instructions. A mention is enough to stop the run:" +
            " this check does not parse structure, because flattened text" +
            " cannot tell a real block from a quoted one. If it is a" +
            " mention in your own AGENTS.md or in a skill description," +
            " reword it") $Json
    }
    if ($after -ne 0) {
        Write-Blocked ("the reviewer still advertises " + $after +
            " skill(s) after suppression; the declared residue is empty") $Json
    }
    # The suppression render's OWN project-doc answer. It is checked after
    # the two suppression rules above so that a run which both failed to
    # suppress and carries a project doc still reports the suppression
    # failure first, exactly as it did before this check existed.
    if ($instructions2.ProjectDoc) {
        Write-Blocked ("the reviewed tree's AGENTS.md is being ingested as" +
            " instructions - remediate in the mirror") $Json
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
    #
    # The write and the resolve are GUARDED. Unguarded, a `-OverrideOut`
    # under a missing parent printed two errors to stderr and then
    # reported status clean with `override_file: null` and exit 0: the
    # caller was told the machine was verified and handed an artifact path
    # that does not exist. Reproduced 2026-07-28, mode-diff round 2.
    # The hash is computed INSIDE the same guard. Left outside it, a
    # failure there would leave override_sha256 empty and the run would
    # continue into the clean report. Mode-diff round 3, 2026-07-28.
    $enc = New-Object System.Text.UTF8Encoding($false, $true)
    try {
        $bytes = $enc.GetBytes($override)
        [System.IO.File]::WriteAllBytes($OverrideOut, $bytes)
        $overridePath = (Resolve-Path $OverrideOut -ErrorAction Stop).Path
        $sha = [System.Security.Cryptography.SHA256]::Create()
        $overrideHash = ([System.BitConverter]::ToString(
            $sha.ComputeHash($bytes)) -replace '-', '').ToLower()
    } catch {
        Write-Blocked ("the verified override could not be written to " +
            $OverrideOut + ": " + $_.Exception.Message +
            " - a verified value nothing can dispatch is not a clean" +
            " result") $Json
    }
    # And the two fields are CHECKED, not assumed. A guard proves no
    # exception escaped; it does not prove the values are usable.
    if ([string]::IsNullOrWhiteSpace($overridePath)) {
        Write-Blocked ("the override artifact could not be located after" +
            " writing it") $Json
    }
    if ($overrideHash -notmatch '^[0-9a-f]{64}$') {
        Write-Blocked ("the override hash is not a sha-256 digest, so" +
            " nothing downstream can authenticate the artifact") $Json
    }
}

# A run that performed NO suppression pass has verified nothing, and must
# not share its exit code or its status word with one that did. Without
# -SuppressSkills the first pass still measured 29 advertised skills and
# the old code reported `clean` and exit 0 anyway - the exact false clean
# every other rule in this script exists to prevent. Found by the mode-diff
# review, 2026-07-28. The measurement is still printed, because it is
# useful; only the verdict is withheld.
if (-not $SuppressSkills) {
    $partial = @{
        status = "measured-only"
        reason = ("no suppression pass was run, so nothing is verified: " +
            $before + " skill(s) are still advertised. Pass -SuppressSkills" +
            " with -OverrideOut to verify and to produce a dispatchable" +
            " override.")
        skills_before = $before
        skills_after = $before
        repo_scoped = $repoScoped.Count
        plugin_cache_scoped = $cacheScoped.Count
        home_scoped = $homeScoped.Count
        unknown_scoped = $unknownScoped.Count
        global_agents_md = ($globalPath -ne "")
        global_agents_md_path = $globalPath
        project_agents_md = $instructions.ProjectDoc
        override_file = ""
        override_sha256 = ""
    }
    if ($Json) {
        Write-Output (ConvertTo-Json $partial -Compress)
    } else {
        Write-Output ("measured-only: " + $partial.reason)
    }
    exit 1
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
    global_agents_md = ($globalPath -ne "")
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
        ($globalPath -ne ""))
}
exit 0
