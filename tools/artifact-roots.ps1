# artifact-roots.ps1 - resolve every path a multi-model-verify round writes
# into a consumer repository, from the ONE declaration in
# skills/multi-model-verify/references/model-prompting-notes.md.
#
# Item 100 (2026-09-12): rounds, ledgers and mirrors landed in three roots
# per consumer repo because each writer read the repo-side override on
# its own. This tool is the only reader. It prints the resolved set for
# the debate record, and -Assert answers whether one path lies inside a
# retained in-repo root before a retention copy runs.
#
# The declaration is PARSED here, never remembered: a missing or doubled
# line is an error, not a default.
#
# Windows PowerShell 5.1 and PowerShell 7, ASCII ONLY.
#
# Exit codes: 0 resolved (or -Assert inside the expected root, or inside
# any retained root when -Expect is absent), 1 -Assert outside every
# retained root or inside a retained root other than the one -Expect
# names, 2 parameter fault (anything wrong on the command line, a
# forbidden character in -DocsRoot, -Assert or the TEMP variable),
# unreadable declaration, or -RepoRoot not a git working tree. There is
# NO binding residual: this script has no param block, so PowerShell
# binds nothing, and every token reaches the parser below as a string
# on both hosts. The typed forms were measured 2026-09-13 by the diff
# debate: a missing value and a duplicate exited 1 from -File binding
# on both hosts, and `-Json:$true` exited 1 on 5.1 and 0 on 7 (switch
# conversion), so typed binding could not deliver one exit map. The map
# mirrors dispatch-round.ps1.
#
# Arguments (names are exact and case-insensitive, never abbreviated):
#   -RepoRoot <path>   required
#   -DocsRoot <rel>    optional
#   -Assert <path>     optional
#   -Expect <row>      optional, requires -Assert
#   -Json              optional; -Json:true / -Json:false also accepted

$ErrorActionPreference = "Stop"

function Fail($message) {
    Write-Output ("ERROR: " + $message)
    exit 2
}

# ---- the command line --------------------------------------------------
# Hand-parsed from $args: every fault is script-seen and exits 2 with an
# ERROR: line, identically on both hosts.
$RepoRoot = ""
$DocsRoot = ""
$Assert = ""
$Expect = ""
$Json = $false
$bound = @{}
$valueNames = @("RepoRoot", "DocsRoot", "Assert", "Expect")
$argv = @($args)
$ai = 0
while ($ai -lt $argv.Count) {
    $tok = [string]$argv[$ai]
    $m = [regex]::Match($tok, '^-([A-Za-z]+)(:(.*))?$')
    if (-not $m.Success) { Fail ("unknown parameter: " + $tok) }
    $given = $m.Groups[1].Value
    $name = ""
    foreach ($n in ($valueNames + @("Json"))) {
        if ($given -ieq $n) { $name = $n }
    }
    if (-not $name) { Fail ("unknown parameter: " + $tok) }
    if ($bound.ContainsKey($name)) { Fail ("-" + $name + " given more than once") }
    $bound[$name] = $true
    if ($name -eq "Json") {
        if ($m.Groups[2].Success) {
            $flag = $m.Groups[3].Value
            if ($flag -match '^\$?true$') { $Json = $true }
            elseif ($flag -match '^\$?false$') { $Json = $false }
            else { Fail ("-Json takes true or false, not: " + $flag) }
        } else {
            # -File splits `-Json:$true` into `-Json` and a second token,
            # which PowerShell 7 evaluates to `True` and 5.1 leaves as
            # `$true`; both spellings select the format here.
            $Json = $true
            if (($ai + 1) -lt $argv.Count) {
                $peek = [string]$argv[$ai + 1]
                if ($peek -match '^\$?true$') { $Json = $true; $ai++ }
                elseif ($peek -match '^\$?false$') { $Json = $false; $ai++ }
            }
        }
        $ai++
        continue
    }
    if ($m.Groups[2].Success) {
        $value = $m.Groups[3].Value
    } else {
        $ai++
        if ($ai -ge $argv.Count) { Fail ("-" + $name + " is missing its value") }
        $value = [string]$argv[$ai]
        if ($value -match '^-[A-Za-z]') { Fail ("-" + $name + " is missing its value") }
    }
    Set-Variable -Name $name -Value $value
    $ai++
}
if (-not $bound.ContainsKey("RepoRoot") -or -not $RepoRoot) { Fail "-RepoRoot is required" }

# ---- -Expect -----------------------------------------------------------
# The frozen plan parent (<docs-root>/plans) contains every dated
# directory beside plans/rounds/, so a rounds retention copy aimed at
# <docs-root>/plans/<date>-<topic>/ would answer "inside" without this.
# -Expect names the ONE retained root the caller intends; any other
# retained root is refused (exit 1). Values are case-sensitive.
$expectMap = @(
    @{ Key = "rounds";      Name = "rounds root" },
    @{ Key = "frozenPlan";  Name = "frozen plan parent" },
    @{ Key = "attestation"; Name = "attestation root" },
    @{ Key = "checkpoint";  Name = "checkpoint root" }
)
$expectedName = ""
if ($bound.ContainsKey("Expect")) {
    if (-not $bound.ContainsKey("Assert")) {
        Fail "-Expect requires -Assert"
    }
    foreach ($e in $expectMap) {
        if ($Expect -ceq $e.Key) { $expectedName = $e.Name }
    }
    if (-not $expectedName) {
        Fail ("-Expect must be one of rounds, frozenPlan, attestation, checkpoint: " + $Expect)
    }
}

function Normalize-Slashes($p) {
    return $p.Replace("\", "/").TrimEnd("/")
}

function Resolve-Absolute($p) {
    # Provider-relative, like new-review-mirror.ps1: a relative path
    # resolves against PowerShell's location, not the process cwd. A
    # path the provider cannot resolve (an unknown drive, an illegal
    # character) is a parameter fault, exit 2, never an uncaught throw:
    # the failure is captured here and Fail is called OUTSIDE the try,
    # so nothing about `exit` inside a catch is relied on.
    $full = $null
    $why = ""
    try {
        $unresolved = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($p)
        $full = Normalize-Slashes ([System.IO.Path]::GetFullPath($unresolved))
    } catch {
        $why = $_.Exception.Message
    }
    if (-not $full) { Fail ("cannot resolve path '" + $p + "': " + $why) }
    return $full
}

# ---- the declaration ---------------------------------------------------
$NotesPath = Join-Path $PSScriptRoot "..\skills\multi-model-verify\references\model-prompting-notes.md"
if (-not (Test-Path -LiteralPath $NotesPath -PathType Leaf)) {
    Fail ("declaration file not found: " + $NotesPath)
}
$notes = $null
$readWhy = ""
try {
    $notes = [System.IO.File]::ReadAllText($NotesPath, (New-Object System.Text.UTF8Encoding($false)))
} catch {
    $readWhy = $_.Exception.Message
}
if ($null -eq $notes) { Fail ("declaration file unreadable: " + $NotesPath + ": " + $readWhy) }
$regionMatch = [regex]::Match($notes,
    '<!-- contract:start id=round-artifact-roots -->(.*?)<!-- contract:end -->',
    [System.Text.RegularExpressions.RegexOptions]::Singleline)
if (-not $regionMatch.Success) {
    Fail ("round-artifact-roots region not found in " + $NotesPath)
}
$region = $regionMatch.Groups[1].Value

$labels = @(
    @{ Key = "docsRoot";         Label = "Canonical docs root" },
    @{ Key = "docsRootOverride"; Label = "Canonical docs root override" },
    @{ Key = "frozenPlan";       Label = "Canonical frozen plan path" },
    @{ Key = "rounds";           Label = "Canonical rounds root" },
    @{ Key = "sddLedger";        Label = "Canonical SDD ledger root" },
    @{ Key = "reviewMirror";     Label = "Canonical review mirror root" },
    @{ Key = "attestation";      Label = "Canonical attestation root" },
    @{ Key = "checkpoint";       Label = "Canonical checkpoint root" }
)
$declared = @{}
foreach ($l in $labels) {
    $pattern = '(?m)^' + [regex]::Escape($l.Label) + ': `([^`\r\n]+)`[ \t]*\r?$'
    $hits = [regex]::Matches($region, $pattern)
    if ($hits.Count -ne 1) {
        Fail ("declaration line '" + $l.Label + "' found " + $hits.Count +
            " times in the round-artifact-roots region; expected exactly 1")
    }
    $declared[$l.Key] = $hits[0].Groups[1].Value
}

# ---- the repository ----------------------------------------------------
# Provider-relative FIRST. PowerShell starts a native child in its OWN
# current location, so `git -C .` itself runs in the right place; what
# breaks is the RELATIVE answer git prints (`.git`, `../.git`) reaching
# .NET GetFullPath, which resolves against the PROCESS working directory
# ([Environment]::CurrentDirectory) and not PowerShell's location.
# Resolving -RepoRoot here makes every later join absolute before any
# .NET path API sees it (measured 2026-09-12 by the R2 and R3 reviewers
# on both hosts; the same distinction new-review-mirror.ps1:1234 draws).
$RepoRoot = Resolve-Absolute $RepoRoot
if (-not (Test-Path -LiteralPath $RepoRoot -PathType Container)) {
    Fail ("-RepoRoot is not a directory: " + $RepoRoot)
}
# Native git under Continue: a benign stderr line must not become a
# terminating error (CLAUDE.md, the dispatch traps).
$priorEap = $ErrorActionPreference
$ErrorActionPreference = "Continue"
$toplevel = (& git -C $RepoRoot rev-parse --show-toplevel 2>$null | Out-String).Trim()
$topExit = $LASTEXITCODE
$commonDir = (& git -C $RepoRoot rev-parse --git-common-dir 2>$null | Out-String).Trim()
$commonExit = $LASTEXITCODE
$ErrorActionPreference = $priorEap
if (($topExit -ne 0) -or -not $toplevel) {
    Fail ("-RepoRoot is not a git working tree: " + $RepoRoot)
}
if (($commonExit -ne 0) -or -not $commonDir) {
    Fail ("could not resolve the git common dir for " + $RepoRoot)
}
$top = Resolve-Absolute $toplevel
# A relative common dir is relative to the directory git RAN IN, which
# is -RepoRoot and not the toplevel: from a subdirectory git prints
# `../.git`, and joining that to the toplevel lands outside the checkout.
# Same join as tools/write-attestation.ps1.
if (-not [System.IO.Path]::IsPathRooted($commonDir)) {
    $commonDir = Join-Path $RepoRoot $commonDir
}
$common = Resolve-Absolute $commonDir

# ---- the docs root -----------------------------------------------------
if ($bound.ContainsKey("DocsRoot")) {
    $rel = $DocsRoot.Replace("\", "/").Trim("/")
    if (-not $rel) { Fail "-DocsRoot is empty" }
    # Validate BEFORE any path API: on Windows PowerShell 5.1 IsPathRooted
    # throws on `|`, on 7 it accepts and prints an unusable path
    # (measured 2026-09-12 by the R3 reviewer). One explicit set, both
    # hosts. The colon is rejected here as well as by the rooted check.
    if ($rel -match '[<>:"|?*\x00-\x1f]') {
        Fail ("-DocsRoot contains a character Windows paths forbid: " + $DocsRoot)
    }
    if ([System.IO.Path]::IsPathRooted($DocsRoot)) {
        Fail ("-DocsRoot must be relative to the repo root: " + $DocsRoot)
    }
    if (@($rel.Split("/")) -contains "..") {
        Fail ("-DocsRoot may not contain a '..' segment: " + $DocsRoot)
    }
    # Canonicalize through the filesystem rules, so `./other/root` and
    # `other//root` print as one spelling and -Assert compares equal.
    $docsFull = Resolve-Absolute (Join-Path $toplevel $rel)
    if ($docsFull.Equals($top, [System.StringComparison]::OrdinalIgnoreCase)) {
        Fail ("-DocsRoot may not be the repo root itself: " + $DocsRoot)
    }
    if (-not $docsFull.StartsWith($top + "/", [System.StringComparison]::OrdinalIgnoreCase)) {
        Fail ("-DocsRoot resolves outside the repo root: " + $DocsRoot)
    }
    $docsRel = $docsFull.Substring($top.Length + 1)
    $source = "-DocsRoot"
} elseif (Test-Path -LiteralPath (Join-Path $toplevel $declared.docsRootOverride) -PathType Container) {
    $docsRel = $declared.docsRootOverride
    $source = "override directory exists"
} else {
    $docsRel = $declared.docsRoot
    $source = "default"
}

$tempRoot = $env:TEMP
if (-not $tempRoot) { $tempRoot = [System.IO.Path]::GetTempPath() }
# The one input that is neither a parameter nor git's answer: screen it
# with the same set as -DocsRoot and -Assert before any path API, or a
# `|` in TEMP throws on 5.1 and prints on 7 (measured 2026-09-13 by the
# diff-debate R1 reviewer). Same exit on both hosts.
if (($tempRoot -replace '^[A-Za-z]:', '') -match '[<>:"|?*\x00-\x1f]') {
    Fail ("TEMP contains a character Windows paths forbid: " + $tempRoot)
}
$tempRoot = Resolve-Absolute $tempRoot

function Resolve-Row($value) {
    $v = $value.Replace("<docs-root>", $docsRel)
    $v = $v.Replace("<TEMP>", $tempRoot)
    $v = $v.Replace("<git-common-dir>", $common)
    # Split off the per-debate placeholder tail BEFORE any path API sees
    # the string: on Windows PowerShell 5.1, IsPathRooted and GetFullPath
    # throw "Illegal characters in path" on `<`, and on 7 they answer
    # False (measured 2026-09-12 by the R1 reviewer). The real parent is
    # resolved; the tail is appended verbatim.
    $i = $v.IndexOf("<")
    $tail = ""
    if ($i -ge 0) { $tail = $v.Substring($i); $v = $v.Substring(0, $i) }
    $v = $v.TrimEnd("/")
    if (-not $v) { Fail ("declaration row has no resolvable parent: " + $value) }
    if (-not [System.IO.Path]::IsPathRooted($v)) { $v = $top + "/" + $v }
    $parent = Resolve-Absolute $v
    if ($tail) { return $parent + "/" + $tail }
    return $parent
}

$resolved = [ordered]@{
    repo         = $top
    docsRoot     = $top + "/" + $docsRel
    source       = $source
    frozenPlan   = Resolve-Row $declared.frozenPlan
    rounds       = Resolve-Row $declared.rounds
    sddLedger    = Resolve-Row $declared.sddLedger
    reviewMirror = Resolve-Row $declared.reviewMirror
    attestation  = Resolve-Row $declared.attestation
    checkpoint   = Resolve-Row $declared.checkpoint
}

# ---- -Assert -----------------------------------------------------------
function Strip-Placeholder($p) {
    # The retained root is the path up to the first per-debate
    # placeholder: ".../plans/<date>-<topic>.md" asserts under ".../plans".
    $i = $p.IndexOf("<")
    $head = if ($i -ge 0) { $p.Substring(0, $i) } else { $p }
    return $head.TrimEnd("/")
}

$assertResult = $null
$exitCode = 0
if ($bound.ContainsKey("Assert")) {
    if (-not $Assert) { Fail "-Assert is empty" }
    # Same forbidden-character rule as -DocsRoot, minus the drive colon:
    # .NET Core's GetFullPath accepts `<`, `>` and `|`, so on PowerShell 7
    # an unsubstituted `<date>-<topic>` placeholder would resolve and could
    # answer inside (measured 2026-09-12 by the Task 2 review), while 5.1
    # throws. One explicit set, both hosts. Only a single drive-letter
    # prefix is exempted, so a provider-qualified form (FileSystem::C:\x)
    # that Resolve-Absolute could take is refused here; no caller passes
    # one, and the guard is deliberately stricter than the resolver.
    $assertBody = $Assert -replace '^[A-Za-z]:', ''
    if ($assertBody -match '[<>:"|?*\x00-\x1f]') {
        Fail ("-Assert contains a character Windows paths forbid: " + $Assert)
    }
    $target = Resolve-Absolute $Assert
    $cmp = [System.StringComparison]::OrdinalIgnoreCase
    # Rounds before the plan parent: the rounds root sits under it and
    # the more specific name is the useful answer.
    $retained = @(
        @{ Name = "rounds root";        Root = Strip-Placeholder $resolved.rounds },
        @{ Name = "frozen plan parent"; Root = Strip-Placeholder $resolved.frozenPlan },
        @{ Name = "attestation root";   Root = Strip-Placeholder $resolved.attestation },
        @{ Name = "checkpoint root";    Root = Strip-Placeholder $resolved.checkpoint }
    )
    $inside = $null
    foreach ($r in $retained) {
        if ($target.Equals($r.Root, $cmp) -or $target.StartsWith($r.Root + "/", $cmp)) {
            $inside = $r.Name
            break
        }
    }
    if ($inside -and $expectedName -and ($inside -ne $expectedName)) {
        # Inside a retained root, but not the one the caller intends:
        # refused, and the answer names both roots.
        $assertResult = [ordered]@{ path = $target; inside = $false; root = $inside; expected = $expectedName }
        $exitCode = 1
    } elseif ($inside) {
        $assertResult = [ordered]@{ path = $target; inside = $true; root = $inside }
        if ($expectedName) { $assertResult["expected"] = $expectedName }
        $exitCode = 0
    } else {
        $assertResult = [ordered]@{ path = $target; inside = $false; root = "" }
        if ($expectedName) { $assertResult["expected"] = $expectedName }
        $exitCode = 1
    }
}

# ---- output ------------------------------------------------------------
if ($Json) {
    $out = [ordered]@{}
    foreach ($k in $resolved.Keys) { $out[$k] = $resolved[$k] }
    if ($assertResult) { $out["assert"] = $assertResult }
    Write-Output (ConvertTo-Json $out -Depth 3)
} else {
    Write-Output ("repo: " + $resolved.repo)
    Write-Output ("docs-root: " + $resolved.docsRoot)
    Write-Output ("docs-root source: " + $resolved.source)
    Write-Output ("frozen-plan: " + $resolved.frozenPlan)
    Write-Output ("rounds: " + $resolved.rounds)
    Write-Output ("sdd-ledger: " + $resolved.sddLedger)
    Write-Output ("review-mirror: " + $resolved.reviewMirror)
    Write-Output ("attestation: " + $resolved.attestation)
    Write-Output ("checkpoint: " + $resolved.checkpoint)
    if ($assertResult) {
        if ($assertResult.inside) {
            Write-Output ("assert: inside " + $assertResult.root + ": " + $assertResult.path)
        } elseif ($assertResult.root) {
            Write-Output ("assert: inside " + $assertResult.root + ", expected " +
                $assertResult.expected + ": " + $assertResult.path)
        } else {
            Write-Output ("assert: outside every retained root: " + $assertResult.path)
        }
    }
}
exit $exitCode
