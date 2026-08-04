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

# This script decodes git's pathnames as STRICT UTF-8 and refuses to guess
# on a bad byte, then prints them. Without this line the print undoes that
# care: [Console]::OutputEncoding defaults to the OEM code page - measured
# IBM437 on both hosts here - so an accented pathname leaves as one 0x82
# byte and a UTF-8 reader sees U+FFFD. The baseline and the manifest are
# EVIDENCE, and evidence that renames a file is worse than no evidence.
# The ambient encoding also varies by console, which is why this surfaced
# as an order-dependent test rather than a constant one.
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)

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

function Format-StatusPathname($path) {
    # Reproduce the porcelain LINE form's quoting for one pathname, so a
    # recorded baseline is byte-comparable with a capture taken by running
    # THE STATUS COMMAND directly - which is what
    # references/backup-lane.md requires of every round.
    #
    # The rule is one condition because the guard has already removed every
    # other trigger. Measured 2026-07-29: `git status --porcelain` quotes
    # each pathname independently and, once `"` , `\` and the control
    # characters are refused, a SPACE is the only remaining trigger. In the
    # same measurement a rename with a spaced source and a plain
    # destination printed `R  "with space/a.lua" -> plain/a.lua`, and the
    # reverse printed `R  plain/b.lua -> "with space/b.lua"` - each side on
    # its own.
    #
    # Non-ASCII is deliberately NOT quoted. The old captures set
    # `core.quotepath=false`, so an accented pathname was recorded raw, and
    # this render must keep that shape rather than introduce quoting the
    # baseline never had.
    if ([string]$path -match ' ') { return ('"' + $path + '"') }
    return [string]$path
}

function Format-StatusRecord($record) {
    # Render one record in git's own DISPLAY order, `R  <old> -> <new>`, so
    # the recorded baseline keeps the shape references/backup-lane.md
    # already describes and two captures stay comparable across this
    # change.
    #
    # ONE WAY ONLY. Nothing re-parses this text: the manifest's subjects
    # come from the RECORDS. That separation is the whole reason the arrow
    # is safe to write here at all, and Test-SupportedPathname refusing `>`
    # is what keeps it unambiguous.
    $head = [string]$record.X + [string]$record.Y + " "
    if ($record.Source) {
        return ($head + (Format-StatusPathname $record.Source) + " -> " +
                (Format-StatusPathname $record.Path))
    }
    return ($head + (Format-StatusPathname $record.Path))
}

function Invoke-GitFields($repo, $gitArgs) {
    # Every git capture that produces PATHNAMES goes through here, so both
    # of them answer the same questions the same way.
    #
    # `core.quotepath=false` is GONE from these captures and its absence is
    # deliberate. The flag governed the DISPLAY form, and `-z` has no
    # display form: measured 2026-07-29, `git ls-files -z` returned raw
    # UTF-8 bytes with the flag ABSENT. Keeping a flag that does nothing
    # invites a later reader to treat it as load-bearing.
    #
    # The console-encoding guard the old capture needed is gone for the
    # same reason: nothing here goes through PowerShell's decoder. The
    # bytes are read from the process stream and decoded once, strictly,
    # in ConvertFrom-NulCapture.
    $captured = Invoke-GitProcess $repo $gitArgs
    if (-not $captured.Ok) {
        return @{ Ok = $false; Fields = @(); Reason = $captured.Reason }
    }
    return (ConvertFrom-NulCapture $captured.Bytes)
}

function Get-BackChannelEntry($repo) {
    # One listing covering tracked, untracked AND ignored files. `--others`
    # without `--exclude-standard` includes ignored paths. `*AGENTS.md`
    # reaches any depth; `.agents/*` is anchored at the repo ROOT and does
    # NOT, which is the asymmetry recorded in SKILL.md's
    # enumeration-depth-asymmetry region. Do not restate "at any depth"
    # here.
    #
    # Returns @{Ok=..; Entries=..; Reason=..}. A function returning a bare
    # @() has its empty array unrolled by PowerShell, so the caller's
    # variable becomes $null and a CLEAN repo reads exactly like a FAILED
    # enumeration.
    $r = Invoke-GitFields $repo @("ls-files", "--cached", "--others", "-z",
                                  "*AGENTS.md", ".agents/*", '.kimi-code/*')
    if (-not $r.Ok) {
        return @{ Ok = $false; Entries = @(); Reason = $r.Reason }
    }
    # An entry this script cannot handle exactly is a stop, on either of
    # the guard's two grounds - a name whose resolution would risk the
    # WRONG file, or a name it could resolve but could not record.
    # Reporting either as clean is the one outcome the whole preflight
    # exists to prevent, and a back-channel is the case where that matters
    # most.
    foreach ($e in @($r.Fields)) {
        if (-not (Test-SupportedPathname $e)) {
            return @{ Ok = $false; Entries = @()
                      Reason = ("the back-channel entry '" + $e + "' names" +
                        " a path this script cannot handle exactly, so it" +
                        " cannot be enumerated, deleted and recorded as a" +
                        " single consistent fact") }
        }
    }
    return @{ Ok = $true; Entries = @($r.Fields) }
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
    return (Invoke-GitFields $repo @("status", "--porcelain", "--ignored",
                                     "-uall", "-z"))
}

function Get-ManifestSubject($records) {
    # Coverage is exactly the baseline's paths. Returns @{Paths=..} or
    # @{Error=..}.
    #
    # Two dispositions are DEFINED and are not the same thing as skipping.
    # A deletion-only entry is OMITTED, deliberately, because it has no
    # bytes; an `RD` destination is a STOP. What must never happen is a
    # third thing: an entry passed over because this function could not
    # make sense of it. That is the silent hole in the manifest, and it is
    # what the stops below exist to prevent.
    #
    # Takes RECORDS, never rendered text. A rename's destination is already
    # the record's Path under `-z`, so there is no arrow to search for and
    # no chance of splitting inside a pathname.
    $paths = New-Object System.Collections.ArrayList
    foreach ($r in @($records)) {
        $x = $r.X
        $y = $r.Y
        # Deletion-only entries have no bytes to hash. HEAD plus the
        # baseline already bind the absence, which is the whole content of
        # the fact, so OMIT them.
        if (($x -eq " " -and $y -eq "D") -or ($x -eq "D" -and $y -eq " ")) {
            continue
        }
        # An `RD` destination no longer exists. That entry names no
        # readable file, so it is a stop rather than a silent omission.
        if ($y -eq "D" -and ($x -eq "R" -or $x -eq "C")) {
            return @{ Error = ("baseline entry '" +
                (Format-StatusRecord $r) + "' names a destination that has" +
                " been deleted; the mirror is not in a state this manifest" +
                " rule can describe") }
        }
        [void]$paths.Add($r.Path)
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

# ---------------------------------------------------------------------
# PATH BUDGET PRE-FLIGHT. Runs here, after the overlap and override
# guards and BEFORE anything is created or deleted, because the failure
# it prevents is a MID-COPY one: robocopy stops at the first destination
# it cannot create, leaving a partially populated mirror that reads
# exactly like a complete one.
#
# THE UNIVERSE, frozen text: every file and directory destination that
# the exact `robocopy /E` operation may create beneath the resolved
# mirror root, including tracked, untracked, ignored, and all `.git`
# content. Two consequences that narrower readings get wrong - a
# directory with no files in it is still a destination, and `.git` is
# copied so `.git` counts.
#
# THE LIMIT is 260 characters as a conservative policy across both
# supported PowerShell hosts. It is a deterministic refusal threshold,
# not a claim about the maximum any host, API, OS configuration, or
# downstream client could support.
#
# THE ARITHMETIC is resolved mirror-root length, plus separator, plus
# the relative destination path length.
$PathBudget = 260
$budgetRoot = $MirrorPath.TrimEnd("\", "/")
$budgetRootLen = $budgetRoot.Length

# -OverrideOut is written BESIDE the mirror by this script, not by
# robocopy, so the copy universe never covers it. Its own check or none.
if ($OverrideOut.Length -ge $PathBudget) {
    Write-Output ("ERROR: path budget exceeded by the override file - " +
        "$OverrideOut is $($OverrideOut.Length) characters and the limit " +
        "is $PathBudget")
    exit 2
}

if ($budgetRootLen -ge $PathBudget) {
    Write-Output ("ERROR: path budget exceeded by the mirror root alone - " +
        "root is $budgetRootLen characters and the limit is $PathBudget")
    exit 2
}

$srcRoot = $RepoRoot.TrimEnd("\", "/")
# The prefix stripped to form a relative path, rebuilt rather than
# derived from a length. A drive root trims to "C:", and "C:".Length + 1
# is 3 only by coincidence of that one case; on any root ending in a
# colon the arithmetic silently under-measures every relative path,
# which is the permissive direction.
$srcPrefix = $srcRoot
if (-not $srcPrefix.EndsWith("\")) { $srcPrefix = $srcPrefix + "\" }

# The ROOT is a source path too. Checking only entries below it leaves
# the one reparse point most likely to exist unmeasured, and the
# contract clause says "a source reparse point" with no exemption.
try {
    $rootAttr = [int][System.IO.File]::GetAttributes($srcRoot)
} catch {
    Write-Output ("ERROR: $srcRoot could not be enumerated, so the path " +
        "budget was never measured: " + $_.Exception.Message)
    exit 2
}
if (($rootAttr -band [int][System.IO.FileAttributes]::ReparsePoint) -ne 0) {
    Write-Output ("ERROR: $srcRoot is a reparse point - the mirror refuses " +
        "to measure or copy across one")
    exit 2
}

$deepestLen = -1
$deepestRel = ""
$dirAttr = [int][System.IO.FileAttributes]::Directory
$reparseAttr = [int][System.IO.FileAttributes]::ReparsePoint

$pending = New-Object System.Collections.Stack
$pending.Push($srcRoot)
while ($pending.Count -gt 0) {
    $dir = $pending.Pop()
    $entries = $null
    try {
        $entries = @([System.IO.Directory]::GetFileSystemEntries($dir))
    } catch {
        # An unreadable path BLOCKS. It is never skipped: a path that
        # cannot be measured is not a path known to fit, and the same
        # hole semantics the manifest builder states apply here.
        Write-Output ("ERROR: $dir could not be enumerated, so the path " +
            "budget was never measured: " + $_.Exception.Message)
        exit 2
    }
    foreach ($entry in $entries) {
        $attr = 0
        try {
            $attr = [int][System.IO.File]::GetAttributes($entry)
        } catch {
            Write-Output ("ERROR: $entry could not be enumerated, so the " +
                "path budget was never measured: " + $_.Exception.Message)
            exit 2
        }
        # Source reparse points are REFUSED before measuring, not
        # measured through. Nothing here establishes that this
        # enumerator and robocopy traverse an identical universe across
        # one, and a budget computed over a universe the copy does not
        # share is not a measurement of the copy.
        if (($attr -band $reparseAttr) -ne 0) {
            Write-Output ("ERROR: $entry is a reparse point - the mirror " +
                "refuses to measure or copy across one")
            exit 2
        }
        $rel = $entry.Substring($srcPrefix.Length)
        if ($rel.Length -gt $deepestLen) {
            $deepestLen = $rel.Length
            $deepestRel = $rel
        }
        if (($attr -band $dirAttr) -ne 0) { $pending.Push($entry) }
    }
}

if ($deepestLen -ge 0) {
    $deepestSum = $budgetRootLen + 1 + $deepestLen
    if ($deepestSum -ge $PathBudget) {
        Write-Output ("ERROR: path budget exceeded - mirror root is " +
            "$budgetRootLen characters, the deepest relative destination " +
            "is $deepestLen characters, their sum is $deepestSum, and the " +
            "limit is $PathBudget. Build the mirror at a shorter path. " +
            "Deepest: $deepestRel")
        exit 2
    }
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
    Write-Output ("ERROR: could not enumerate back-channels in the" +
        " mirror: " + $found.Reason)
    exit 2
}
$entries = $found.Entries
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
    Write-Output ("ERROR: could not re-enumerate back-channels in the" +
        " mirror: " + $after.Reason)
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
    Write-Output ("BLOCKED: the baseline capture failed (" +
        $captured.Reason + "). A failed capture printed as success would" +
        " quarantine every round of the review that follows, or absorb" +
        " changes it should have caught.")
    exit 1
}
$parsed = ConvertTo-StatusRecord $captured.Fields
if ($parsed.ContainsKey("Error")) {
    Write-Output ("BLOCKED: " + $parsed.Error)
    exit 1
}
$baseline = @(@($parsed.Records) |
    ForEach-Object { Format-StatusRecord $_ })
$subjects = Get-ManifestSubject $parsed.Records
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
