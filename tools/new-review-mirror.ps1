# new-review-mirror.ps1 - build the throwaway review mirror, perform
# SKILL.md preflight-3 remediation inside it, and print the evidence the
# debate record needs.
#
# The mirror is a FILE COPY that preserves .git, never a git clone: a clone
# carries TRACKED FILES ONLY and the review inputs are routinely gitignored
# (frozen plans, References/). Probed 2026-07-26 in KitnEssentials, where a
# cloned workspace handed the reviewer a tree with nothing to review while
# every route and containment check stayed green.
#
# This script never writes to the real tree, never dispatches a review, and
# never decides to proceed. It stops immediately before the brief is
# written, because the brief is the first artifact that is not evidence.
#
# Windows PowerShell 5.1 compatible, ASCII ONLY.
#
# Exit codes: 0 built and clean, 1 blocked (reason on stdout), 2 script or
# environment error.
param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)][string]$MirrorPath,
    [string]$OverrideOut,
    [switch]$Force,
    [switch]$SkipProbe,
    [string]$CodexCommand = "codex"
)

function Invoke-GitProcess($repo, $gitArgs) {
    # Run git and hand back its stdout as RAW BYTES.
    #
    # Reading bytes rather than PowerShell's decoded string is the point.
    # Windows PowerShell 5.1 decodes a native command's output with the
    # console code page, and even a UTF-8 console override maps a malformed
    # byte to U+FFFD SILENTLY. On this boundary a substituted character is
    # a wrong pathname reported as a good one, so the decode happens once,
    # downstream, and strictly.
    #
    # ARGUMENTS ARE WHITESPACE-FREE LITERALS AND THE REPO IS THE WORKING
    # DIRECTORY. .NET Framework's ProcessStartInfo has no ArgumentList, so
    # the command line is one string; passing the repo path through it
    # would mean hand-quoting a value that can contain spaces, which is the
    # defect class this change removes. The guard below refuses an argument
    # this command line cannot express rather than trusting the caller.
    #
    # Every argument is QUOTED. Git for Windows runs on the MSYS2 runtime,
    # which glob-expands an unquoted argument, and `*AGENTS.md` must reach
    # git unexpanded or the back-channel enumeration silently narrows to
    # whatever happens to sit in the working directory.
    foreach ($a in @($gitArgs)) {
        if ([string]$a -match '[\s"]') {
            return @{ Ok = $false; Bytes = @()
                      Reason = ("git argument '" + $a + "' carries" +
                        " whitespace or a quote, which this command line" +
                        " cannot express") }
        }
    }
    $quoted = @($gitArgs | ForEach-Object { '"' + $_ + '"' })
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "git"
    $psi.Arguments = ($quoted -join " ")
    $psi.WorkingDirectory = $repo
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $mem = New-Object System.IO.MemoryStream
    $p = $null
    try {
        $p = [System.Diagnostics.Process]::Start($psi)
        # Drain stderr CONCURRENTLY. A full stderr pipe blocks git before
        # it finishes writing stdout, and the stdout read below would then
        # never return.
        $errTask = $p.StandardError.ReadToEndAsync()
        $p.StandardOutput.BaseStream.CopyTo($mem)
        $p.WaitForExit()
        [void]$errTask.Wait(5000)
    } catch {
        return @{ Ok = $false; Bytes = @()
                  Reason = ("git could not be run: " +
                            $_.Exception.Message) }
    }
    if ($p.ExitCode -ne 0) {
        return @{ Ok = $false; Bytes = @()
                  Reason = ("git exited " + $p.ExitCode) }
    }
    return @{ Ok = $true; Bytes = $mem.ToArray() }
}

function ConvertFrom-NulCapture($bytes) {
    # Turn a `-z` capture into its fields. Every failure here is a STOP.
    #
    # `-z` is why this exists. Git C-style-quotes a pathname whenever
    # quoting would change it, and the trigger set is WIDER than the
    # escapes alone: a plain SPACE is enough. Measured 2026-07-29, a
    # directory named `M+ Timer` came back from `status --porcelain` as
    # `?? "M+ Timer/"`, and `core.quotepath=false` did not suppress it.
    # Under `-z` git emits the pathname verbatim and NUL-terminated and
    # never quotes, so there is no escape grammar to decode.
    $raw = [byte[]]@($bytes)
    if ($raw.Length -eq 0) { return @{ Ok = $true; Fields = @() } }
    if ($raw[$raw.Length - 1] -ne 0) {
        return @{ Ok = $false; Fields = @()
                  Reason = ("the -z capture does not end with a NUL, so it" +
                    " was truncated and its last pathname is a fragment") }
    }
    # throwOnInvalidBytes, deliberately. The permissive decode substitutes
    # U+FFFD and hands back a pathname that names a different file.
    $utf8 = New-Object System.Text.UTF8Encoding($false, $true)
    $text = ""
    try {
        $text = $utf8.GetString($raw)
    } catch {
        return @{ Ok = $false; Fields = @()
                  Reason = ("the -z capture is not valid UTF-8, so a" +
                    " pathname in it cannot be read without guessing") }
    }
    # The capture ends with a NUL, so the split's LAST element is the empty
    # string after it. Drop exactly that one. An empty field anywhere else
    # is a real fault and belongs to the caller, not to this function.
    $parts = $text.Split([char]0)
    $fields = New-Object System.Collections.ArrayList
    for ($i = 0; $i -lt $parts.Length - 1; $i++) {
        [void]$fields.Add($parts[$i])
    }
    return @{ Ok = $true; Fields = @($fields) }
}

function Test-SupportedPathname($value) {
    # Under `-z` git never quotes, so whatever arrives IS the pathname.
    # The question this answers is whether this tool can handle that
    # pathname EXACTLY, in both senses:
    #
    #   1. Would resolving it risk naming the WRONG file? This is NOT a
    #      Windows name validator: it does not check reserved device
    #      names, trailing dots, length limits, or the other characters
    #      Windows refuses. A syntactically fine name with no file
    #      behind it is not this function's business; where it lands
    #      depends on its status shape, and only ONE of those routes is
    #      a stop. See the design record - the manifest stops on a
    #      subject with no file, deletion-only entries are omitted
    #      before that, and a back-channel match goes to remediation.
    #   2. Can Format-StatusPathname record it in the porcelain line form
    #      the baseline contract already uses?
    #
    # The admitted set is therefore an ordinary pathname, or one whose ONLY
    # line-form quoting trigger is a SPACE - the one trigger the renderer
    # reproduces. Everything else the line form quotes or escapes some
    # other way is refused, and so is `>`.
    #
    # REFUSING rather than rendering is the deliberate choice for that
    # residue. Git records it with git's own C-style encoder - NAMED
    # escapes for tab, newline, `"` and `\`, and OCTAL for the rest,
    # including the one reachable case, 0x7F as `\177`. Reproducing any
    # of that would mean writing back the encoder this cycle deletes. A
    # loud stop on a pathological name is the cheaper failure.
    #
    # The BACKSLASH refusal carries a second, heavier reason. git separates
    # path components with a forward slash, so a backslash in a field is a
    # literal character in a NAME - and `Join-Path` would then read it as a
    # separator and resolve a DIFFERENT file, which the script would delete
    # or hash under the name the baseline gave. That is false coverage
    # rather than a refusal, which is the one outcome this preflight exists
    # to prevent.
    #
    # `>` is refused for a reason of its own: Format-StatusRecord renders a
    # rename as `<old> -> <new>`, and that arrow is only unambiguous while
    # no pathname can contain `>`. The guard is what makes that true rather
    # than assumed.
    #
    # 0x7F is refused, and it is the case that shows why this function is
    # NOT named for Windows. Measured 2026-07-29: Windows CREATES
    # `a<0x7F>b.txt`, and `git status --porcelain` prints it as
    # `?? "a\177b.txt"` with AND without `core.quotepath=false`, while `-z`
    # returns the byte raw. It is legal on disk and a quoting trigger this
    # renderer cannot reproduce, so admitting it would put a bare name into
    # a baseline the direct capture quotes.
    #
    # Non-ASCII is NOT refused. The old captures set `core.quotepath=false`
    # and recorded an accented pathname raw, so it is not a trigger for the
    # form this baseline uses.
    $text = [string]$value
    if ($text.Length -eq 0) { return $false }
    foreach ($ch in $text.ToCharArray()) {
        if ([int]$ch -lt 32) { return $false }
        if ([int]$ch -eq 127) { return $false }
        if ($ch -eq [char]34) { return $false }
        if ($ch -eq '\') { return $false }
        if ($ch -eq '>') { return $false }
    }
    return $true
}

function ConvertTo-StatusRecord($fields) {
    # Parse the `-z` status capture STRUCTURALLY. Returns @{Records=..} or
    # @{Error=..}; a caller that cannot parse an entry must BLOCK, never
    # skip, because a skipped entry is a silent hole in the manifest.
    #
    # THE RENAME FIELD ORDER IS INVERTED FROM THE LINE FORM. Measured
    # 2026-07-29: the line form reads `R  <old> -> <new>`, and the same
    # rename under `-z` reads `R  <new>` NUL `<old>` NUL - DESTINATION
    # first, SOURCE second. Nothing about the record hints at the order,
    # which is why it is stated here rather than left to a reader.
    #
    # Each field is the two status columns, one space, then the pathname.
    $records = New-Object System.Collections.ArrayList
    $all = @($fields)
    $i = 0
    while ($i -lt $all.Count) {
        $field = [string]$all[$i]
        $i++
        if ($field.Length -lt 4) {
            return @{ Error = ("status field '" + $field + "' is shorter" +
                " than two status columns, a space and a pathname") }
        }
        if ($field[2] -ne ' ') {
            return @{ Error = ("status field '" + $field + "' has no space" +
                " where the status code ends, so this capture is not the" +
                " porcelain format this parser reads") }
        }
        $x = $field[0]
        $y = $field[1]
        $path = $field.Substring(3)
        if (-not (Test-SupportedPathname $path)) {
            return @{ Error = ("status entry '" + $field + "' names a" +
                " path this script cannot handle exactly, on one of the" +
                " guard's two grounds: resolving it would risk naming the" +
                " WRONG file, or it cannot be recorded unambiguously in" +
                " the baseline's line form") }
        }
        $source = $null
        if ($x -eq "R" -or $x -eq "C" -or $y -eq "R" -or $y -eq "C") {
            if ($i -ge $all.Count) {
                return @{ Error = ("rename or copy entry '" + $field +
                    "' has no source field after it, so the capture is" +
                    " truncated") }
            }
            $source = [string]$all[$i]
            $i++
            if (-not (Test-SupportedPathname $source)) {
                return @{ Error = ("rename or copy entry '" + $field +
                    "' names a source this script cannot handle" +
                    " exactly, on the same two grounds") }
            }
        }
        [void]$records.Add(@{ X = $x; Y = $y; Path = $path
                              Source = $source })
    }
    return @{ Records = @($records) }
}

function Invoke-GitLines($repo, $gitArgs) {
    # Every git capture that produces PATHNAMES goes through here, so both
    # of them answer the same two questions the same way.
    #
    # `core.quotepath=false`: by default git returns a DISPLAY form rather
    # than a pathname - a directory named `cafe` with an acute accent on
    # the last letter comes back as `"caf\303\251/AGENTS.md"`. This comment
    # spells it out because this file is ASCII only, which is itself the
    # rule that keeps both hosts reading the script identically. Verified
    # live 2026-07-28 against both
    # `ls-files` and `status --porcelain`. A caller that treats the display
    # form as a path deletes nothing, hashes nothing, or - worse - hashes
    # whatever the escapes happen to name once Windows reads the
    # backslashes as separators. Found by the mode-diff PANEL, 2026-07-28,
    # raised independently by two lanes.
    #
    # The console encoding guard is the OTHER half, and neither half works
    # alone. Turning the quoting off makes git emit raw UTF-8, and Windows
    # PowerShell 5.1 decodes a native command's output with the console
    # code page - so the flag by itself trades octal escapes for mojibake.
    # The probe script carries the same guard for the same reason.
    $prior = [Console]::OutputEncoding
    $lines = $null
    $code = 0
    try {
        [Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
        $lines = & git -C $repo -c core.quotepath=false @gitArgs 2>$null
        $code = $LASTEXITCODE
    } finally {
        [Console]::OutputEncoding = $prior
    }
    if ($code -ne 0) { return @{ Ok = $false; Lines = @() } }
    return @{ Ok = $true; Lines = @($lines | Where-Object { $_ }) }
}

function Test-GitQuotedPath($value) {
    # git quotes a pathname whenever C-style quoting would change it, and
    # the trigger set is WIDER than the escapes alone: a plain SPACE is
    # enough. Measured 2026-07-29 on a real tree, 5810 of 11874 baseline
    # entries came back quoted and all but one were pure ASCII quoted for
    # a space and nothing else. So "quoted" cannot mean "unresolvable" -
    # treating it that way stops the mirror on half a normal repo.
    return ([string]$value).StartsWith('"')
}

function ConvertFrom-GitQuotedPath($value) {
    # Decode git's C-style quoting into the pathname it names. Returns
    # $null when the text carries an escape this decoder does not define,
    # which the caller must treat as a STOP - that is the safety property
    # the previous blanket refusal was reaching for, kept for the input
    # that actually needs it and dropped for the input that does not.
    #
    # TRIMMING the delimiters is the dangerous operation this replaces:
    # the escapes survive a trim, Windows then reads `caf\303\251/x` as
    # `caf\303\251\x`, and a colliding real path is hashed under the entry
    # the baseline actually named. Decoding has no such failure - either
    # the escape is defined and the byte is exact, or the decode refuses.
    # Found by the mode-diff PANEL 2026-07-28; corrected 2026-07-29.
    #
    # `core.quotepath=false` is set on every capture, so high bytes arrive
    # RAW and octal escapes are left naming control characters only. The
    # octal branch below is still implemented, because the flag guards the
    # display form and not the quoting itself.
    $text = [string]$value
    if (-not $text.StartsWith('"') -or -not $text.EndsWith('"') -or
        $text.Length -lt 2) {
        return $null
    }
    $body = $text.Substring(1, $text.Length - 2)
    $out = New-Object System.Text.StringBuilder
    $i = 0
    while ($i -lt $body.Length) {
        $c = $body[$i]
        if ($c -ne '\') {
            [void]$out.Append($c)
            $i++
            continue
        }
        $i++
        if ($i -ge $body.Length) { return $null }
        $e = $body[$i]
        $i++
        switch ($e) {
            'a'  { [void]$out.Append([char]7);  continue }
            'b'  { [void]$out.Append([char]8);  continue }
            'f'  { [void]$out.Append([char]12); continue }
            'n'  { [void]$out.Append([char]10); continue }
            'r'  { [void]$out.Append([char]13); continue }
            't'  { [void]$out.Append([char]9);  continue }
            'v'  { [void]$out.Append([char]11); continue }
            '\'  { [void]$out.Append('\');      continue }
            '"'  { [void]$out.Append('"');      continue }
            default {
                # Three octal digits, or nothing this decoder defines.
                if ($e -lt '0' -or $e -gt '7') { return $null }
                if ($i + 1 -gt $body.Length - 1) { return $null }
                $d2 = $body[$i]
                $d3 = $body[$i + 1]
                if ($d2 -lt '0' -or $d2 -gt '7' -or
                    $d3 -lt '0' -or $d3 -gt '7') { return $null }
                $code = (([int][string]$e) * 64) + (([int][string]$d2) * 8) +
                        ([int][string]$d3)
                [void]$out.Append([char]$code)
                $i += 2
                continue
            }
        }
    }
    return $out.ToString()
}

function Resolve-GitPathname($value) {
    # One entry point for every pathname read out of a git capture: quoted
    # entries decode, unquoted entries pass through unchanged. $null means
    # the caller must BLOCK.
    if (Test-GitQuotedPath $value) {
        return (ConvertFrom-GitQuotedPath $value)
    }
    return ([string]$value)
}

function Get-BackChannelEntry($repo) {
    # One listing covering tracked, untracked AND ignored files. `--others`
    # without `--exclude-standard` includes ignored paths. `*AGENTS.md`
    # reaches any depth; `.agents/*` is anchored at the repo ROOT and does
    # NOT, which is the asymmetry recorded in SKILL.md's
    # enumeration-depth-asymmetry region. Do not restate "at any depth"
    # here.
    #
    # Returns @{Ok=..; Entries=..}. A function returning a bare @() has its
    # empty array unrolled by PowerShell, so the caller's variable becomes
    # $null and a CLEAN repo reads exactly like a FAILED enumeration.
    $r = Invoke-GitLines $repo @("ls-files", "--cached", "--others",
                                 "*AGENTS.md", ".agents/*")
    if (-not $r.Ok) { return @{ Ok = $false; Entries = @() } }
    # `ls-files` quotes on the same trigger set as `status`, so its entries
    # go through the same decoder. An entry that will not decode is a stop
    # here too: a back-channel this script cannot name is a back-channel it
    # cannot delete, and reporting it as clean is the one outcome the whole
    # preflight exists to prevent.
    $entries = New-Object System.Collections.ArrayList
    foreach ($e in @($r.Lines)) {
        $resolved = Resolve-GitPathname $e
        if ($null -eq $resolved) { return @{ Ok = $false; Entries = @() } }
        [void]$entries.Add($resolved)
    }
    return @{ Ok = $true; Entries = @($entries) }
}

function Test-Tracked($repo, $path) {
    & git -C $repo ls-files --error-unmatch -- $path 2>$null | Out-Null
    return ($LASTEXITCODE -eq 0)
}

function Get-BaselineRaw($repo) {
    # THE STATUS COMMAND, every capture without exception. Bare porcelain
    # OMITS ignored paths and COLLAPSES an untracked directory to one
    # entry; ignored content is the entire reason this workspace is a
    # mirror.
    #
    # The BASELINE is this raw capture, status codes included
    # (references/backup-lane.md). It is recorded verbatim and is NOT the
    # same object as the manifest's subject list below.
    #
    # Same structured shape and same reason as Get-BackChannelEntry: an
    # empty baseline is a legitimate state, and a bare @() return would be
    # indistinguishable from a failed capture.
    return (Invoke-GitLines $repo @("status", "--porcelain", "--ignored",
                                    "-uall"))
}

function Get-ManifestSubject($baselineRaw) {
    # Coverage is exactly the baseline's paths. Returns @{Paths=..} or
    # @{Error=..}; a caller that cannot resolve an entry must BLOCK, never
    # skip, because a skipped entry is a silent hole in the manifest.
    $paths = New-Object System.Collections.ArrayList
    foreach ($line in @($baselineRaw)) {
        if ($line.Length -lt 4) {
            return @{ Error = "unparseable status line: '$line'" }
        }
        $x = $line[0]
        $y = $line[1]
        $rest = $line.Substring(3)
        # Deletion-only entries have no bytes to hash. HEAD plus the
        # baseline already bind the absence, which is the whole content of
        # the fact, so OMIT them.
        if (($x -eq " " -and $y -eq "D") -or ($x -eq "D" -and $y -eq " ")) {
            continue
        }
        # Rename and copy entries hash the CURRENT DESTINATION. EITHER
        # column can carry R or C, so both are tested. Probed 2026-07-28:
        # a staged rename reports `R  a.txt -> b.txt`, and the same rename
        # whose destination is then deleted reports `RD a.txt -> b.txt`.
        if ($x -eq "R" -or $x -eq "C" -or $y -eq "R" -or $y -eq "C") {
            $idx = $rest.IndexOf(" -> ")
            if ($idx -ge 0) { $rest = $rest.Substring($idx + 4) }
        }
        # An `RD` destination no longer exists. That entry names no
        # readable file, so it is a stop rather than a silent omission.
        if ($y -eq "D" -and ($x -eq "R" -or $x -eq "C")) {
            return @{ Error = ("baseline entry '$line' names a destination" +
                " that has been deleted; the mirror is not in a state this" +
                " manifest rule can describe") }
        }
        # A quoted entry DECODES; only an escape the decoder does not
        # define is a stop. See ConvertFrom-GitQuotedPath for why decoding
        # is safe where the previous trim-and-hope was not.
        $resolved = Resolve-GitPathname $rest
        if ($null -eq $resolved) {
            return @{ Error = ("baseline entry '$line' carries an escape" +
                " sequence this script does not define, so the file it" +
                " names cannot be resolved without guessing") }
        }
        [void]$paths.Add($resolved)
    }
    return @{ Paths = @($paths) }
}

function Get-ContentManifest($repo, $paths) {
    # Directories expand RECURSIVELY to their files: a directory subject
    # such as References/ is never one manifest entry, because a hash over
    # a directory name identifies nothing.
    $files = New-Object System.Collections.ArrayList
    foreach ($p in $paths) {
        $full = Join-Path $repo $p
        if (Test-Path $full -PathType Container) {
            $found = Get-ChildItem -LiteralPath $full -Recurse -File -Force
            foreach ($f in $found) {
                $rel = $f.FullName.Substring($repo.Length + 1)
                [void]$files.Add($rel.Replace("\", "/"))
            }
        } elseif (Test-Path $full -PathType Leaf) {
            [void]$files.Add($p.TrimEnd("/").Replace("\", "/"))
        } else {
            # A baseline path with nothing behind it is a stop. Skipping it
            # would leave a hole in the manifest that reads as coverage.
            return @{ Error = "baseline path '$p' has no file behind it" }
        }
    }
    $unique = [string[]]@($files | Sort-Object -Unique)
    [Array]::Sort($unique, [System.StringComparer]::Ordinal)
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $out = New-Object System.Collections.ArrayList
    foreach ($rel in $unique) {
        $bytes = [System.IO.File]::ReadAllBytes((Join-Path $repo $rel))
        $hex = ([System.BitConverter]::ToString($sha.ComputeHash($bytes)) -replace '-', '').ToLower()
        [void]$out.Add($rel + " " + $hex)
    }
    return @{ Paths = @($out) }
}

$toplevel = $true

if (-not (Test-Path $RepoRoot)) {
    Write-Output "ERROR: $RepoRoot does not exist"
    exit 2
}
$RepoRoot = (Resolve-Path $RepoRoot).Path

# RESOLVE ONCE, THROUGH THE PROVIDER, BEFORE ANY GUARD. An earlier
# revision guarded `[IO.Path]::GetFullPath($MirrorPath)`, which resolves a
# relative path against the PROCESS working directory, while `Test-Path`
# and `Remove-Item -Recurse -Force` further down resolve the same parameter
# against PowerShell's PROVIDER location. When a caller's two locations
# differ - any in-session use after Set-Location - the guard approved one
# absolute target and the recursive delete destroyed another. Found by the
# mode-diff review, 2026-07-28; a prior review had called it theoretical,
# which was wrong: -MirrorPath is a public parameter and the divergence is
# an ordinary PowerShell condition. From here down, only the resolved
# values are used.
$MirrorPath = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($MirrorPath)
if ($OverrideOut) {
    $OverrideOut = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OverrideOut)
}

# OVERLAP GUARD, before anything is created or deleted. -Force recursively
# deletes MirrorPath, so a MirrorPath equal to, inside, or containing
# RepoRoot would destroy the user's working tree. robocopy over an
# overlapping pair is equally unsafe. This runs FIRST, because by the time
# Remove-Item runs it is too late to check.
$rr = $RepoRoot.Replace("\", "/").TrimEnd("/") + "/"
$mp = $MirrorPath.Replace("\", "/").TrimEnd("/") + "/"
$cmp = [System.StringComparison]::OrdinalIgnoreCase
if ($mp.Equals($rr, $cmp)) {
    Write-Output "ERROR: the mirror path is the repo root itself"
    exit 2
}
if ($mp.StartsWith($rr, $cmp)) {
    Write-Output ("ERROR: the mirror path is inside the repo ($MirrorPath)" +
        " - building or forcing there would write into, or delete, the" +
        " tree under review")
    exit 2
}
if ($rr.StartsWith($mp, $cmp)) {
    Write-Output ("ERROR: the mirror path contains the repo ($MirrorPath)" +
        " - -Force would delete the repo with it")
    exit 2
}

# Resolve the EFFECTIVE override path here, default included, and guard it
# beside the mirror guard. Deferring the default until after the mirror is
# built, copied, remediated and manifested would mean discovering a stale
# or overlapping artifact only after all that work had already happened,
# and -SkipProbe would bypass the check entirely.
if (-not $OverrideOut) {
    $OverrideOut = Join-Path (Split-Path $MirrorPath -Parent) `
        ((Split-Path $MirrorPath -Leaf) + ".skills-override.txt")
}
$op = $OverrideOut.Replace("\", "/").TrimEnd("/")
foreach ($protected in @($rr, $mp)) {
    if (($op + "/").Equals($protected, $cmp) -or
        ($op + "/").StartsWith($protected, $cmp) -or
        $protected.StartsWith($op + "/", $cmp)) {
        Write-Output ("ERROR: the override path overlaps a protected tree" +
            " ($OverrideOut)")
        exit 2
    }
}
if (Test-Path $OverrideOut) {
    Write-Output ("ERROR: $OverrideOut already exists - a stale override" +
        " reads exactly like a fresh one")
    exit 2
}

if (Test-Path $MirrorPath) {
    if (-not $Force) {
        Write-Output ("ERROR: $MirrorPath already exists - a stale mirror" +
            " reads exactly like a fresh one. Pass -Force to replace it.")
        exit 2
    }
    Remove-Item -LiteralPath $MirrorPath -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $MirrorPath | Out-Null
$MirrorPath = (Resolve-Path $MirrorPath).Path

& robocopy $RepoRoot $MirrorPath /E /COPY:DAT /R:1 /W:1 /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) {
    Write-Output "ERROR: robocopy failed with $LASTEXITCODE"
    exit 2
}

$found = Get-BackChannelEntry $MirrorPath
if (-not $found.Ok) {
    Write-Output "ERROR: could not enumerate back-channels in the mirror"
    exit 2
}
$entries = $found.Entries
# A quoted entry here would silently delete nothing and then surface as
# "survived remediation", which reads as a back-channel that refused to go
# rather than as a name this script could not resolve.
foreach ($entry in $entries) {
    if (Test-GitQuotedPath $entry) {
        Write-Output ("BLOCKED: the back-channel entry " + $entry +
            " arrives in git's quoted form, so remediation cannot name the" +
            " file it points at")
        exit 1
    }
}
$tracked = New-Object System.Collections.ArrayList
foreach ($entry in $entries) {
    if (Test-Tracked $MirrorPath $entry) { [void]$tracked.Add($entry) }
    $full = Join-Path $MirrorPath $entry
    if (Test-Path $full) { Remove-Item -LiteralPath $full -Recurse -Force }
    # Prune the directories the entry lived in, up to but never including
    # the mirror root. `git ls-files` names FILES, so deleting one leaves
    # `.agents/skills/<name>/` standing - an empty shell of the very
    # surface this step exists to remove.
    $dir = Split-Path (Join-Path $MirrorPath $entry) -Parent
    while ($dir -and ($dir.Length -gt $MirrorPath.Length) -and
           (Test-Path $dir) -and
           -not (Get-ChildItem -LiteralPath $dir -Force)) {
        Remove-Item -LiteralPath $dir -Force
        $dir = Split-Path $dir -Parent
    }
}
if ($tracked.Count -gt 0) {
    # Stage exactly the entries that were tracked. `git add -A` over a
    # pathspec would fail when one of the two patterns matches nothing,
    # and `git add -A` over the whole tree would stage the untracked and
    # ignored files the mirror deliberately carries.
    $paths = @($tracked)
    & git -C $MirrorPath add -- @paths 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Output ("BLOCKED: could not stage the removed back-channels" +
            " in the mirror")
        exit 1
    }
    & git -C $MirrorPath -c user.email=parallax@local -c user.name=parallax `
        commit -q -m "remove instruction back-channels for review" 2>&1 | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Output ("BLOCKED: the mirror commit failed. The mirror carries" +
            " the real repo's .git, hooks included, so this is a" +
            " mirror-construction problem, never a finding about the" +
            " reviewed work.")
        exit 1
    }
}

$after = Get-BackChannelEntry $MirrorPath
if (-not $after.Ok) {
    Write-Output "ERROR: could not re-enumerate back-channels in the mirror"
    exit 2
}
if ($after.Entries.Count -gt 0) {
    Write-Output ("BLOCKED: back-channel(s) survived remediation: " +
        ($after.Entries -join "; "))
    exit 1
}

$head = (& git -C $MirrorPath rev-parse HEAD 2>$null | Out-String).Trim()
if (($LASTEXITCODE -ne 0) -or -not $head) {
    Write-Output ("BLOCKED: could not resolve the mirror's HEAD - the" +
        " mirror's identity in the debate record would be blank")
    exit 1
}
$captured = Get-BaselineRaw $MirrorPath
if (-not $captured.Ok) {
    Write-Output ("BLOCKED: the baseline capture failed. A failed capture" +
        " printed as success would quarantine every round of the review" +
        " that follows, or absorb changes it should have caught.")
    exit 1
}
$baseline = $captured.Lines
$subjects = Get-ManifestSubject $baseline
if ($subjects.ContainsKey("Error")) {
    Write-Output ("BLOCKED: " + $subjects.Error)
    exit 1
}
$manifestResult = Get-ContentManifest $MirrorPath $subjects.Paths
if ($manifestResult.ContainsKey("Error")) {
    Write-Output ("BLOCKED: " + $manifestResult.Error)
    exit 1
}
$manifest = $manifestResult.Paths

$probeLine = "skipped"
$overrideFile = ""
if (-not $SkipProbe) {
    # $OverrideOut was resolved and guarded at the top. The probe's
    # verified value IS the dispatch's input, so a mirror built without it
    # leaves the transport with a file that does not exist.
    $probeScript = Join-Path (Split-Path $PSCommandPath -Parent) "codex-context-probe.ps1"
    $hostExe = (Get-Process -Id $PID).Path
    $probeOut = & $hostExe -NoProfile -NonInteractive -File $probeScript `
        -WorkDir $MirrorPath -SuppressSkills -OverrideOut $OverrideOut `
        -Json -CodexCommand $CodexCommand
    if ($LASTEXITCODE -ne 0) {
        Write-Output ("BLOCKED: the client context probe did not pass: " +
            (@($probeOut) -join "`n"))
        exit 1
    }
    $probeLine = (@($probeOut) -join "`n").Trim()
    $overrideFile = $OverrideOut
}

Write-Output ("mirror: " + $MirrorPath)
Write-Output ("head: " + $head)
Write-Output "baseline:"
foreach ($b in $baseline) { Write-Output ("  " + $b) }
Write-Output "manifest:"
foreach ($m in $manifest) { Write-Output ("  " + $m) }
Write-Output ("probe: " + $probeLine)
Write-Output ("override: " + $overrideFile)
# A mirror built without the client probe is NOT cleared for dispatch, and
# must not share its exit code with one that is. -SkipProbe exists for
# offline construction and for the tests; it is not a way to reach a clean
# outcome without a measurement. Found by the mode-diff review, 2026-07-28.
if ($SkipProbe) {
    Write-Output ("BLOCKED: no client measurement was made (-SkipProbe), so" +
        " this mirror is not cleared for dispatch and carries no verified" +
        " override")
    exit 1
}
exit 0
