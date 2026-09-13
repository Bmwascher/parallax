# write-attestation.ps1 - record a multi-model-verify diff-mode TERMINAL
# verdict as a machine-readable, SHA-bound attestation.
#
# Written by the SESSION after its final adjudication - never from the
# reviewer's reply alone; the session's terminal verdict is the thing being
# recorded (family standing rule: a reviewer PASS/FIX is input, not
# terminal). Stored under the repo's GIT COMMON DIR, not the working tree:
# writing it cannot move HEAD out from under its own SHA, it never ships in
# a commit, and worktrees share it. verify-attestation.ps1 is the consumer
# (pre-push lanes, non-blocking v1).
#
# Windows PowerShell 5.1 compatible, ASCII ONLY (see check-drift.ps1
# header for why).
#
# Exit codes: 0 written, 2 argument/repo error, 3 written but a reap failed.
#
# REAP (0.36.0, backlog item 106): -ReapMirror and -ReapBridge name the
# review mirror and the clone bridge the debate ran on. The attestation
# is the one TERMINAL event the plugin records mechanically, so it is
# the reap point - never an age. Both paths are validated against the
# reviewed repository and the attested head BEFORE the record is
# written, so a refused argument costs nothing (exit 2); they are
# removed AFTER it, so a removal failure leaves the verdict standing
# and says so (exit 3). The removal itself is
# tools/review-tree-removal.ps1, shared with the mirror tool.
#
# PARENT (0.37.0, backlog item 107): both trees must also sit under the
# review mirror parent the round-artifact-roots declaration names,
# read here through tools/artifact-roots.ps1 rather than by a literal
# of this file's own, so that one edit to the row moves every reader.
# The rule is the LAST one in Resolve-ReapPath: every other refusal
# keeps its own message.
param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)][string]$BaseSha,
    [Parameter(Mandatory = $true)][string]$HeadSha,
    [Parameter(Mandatory = $true)][ValidateSet("PASS", "FIX", "ESCALATE")][string]$Verdict,
    [Parameter(Mandatory = $true)][int]$Rounds,
    [Parameter(Mandatory = $true)][string]$Participants,
    # Both mandatory, no defaults (Sol diff review 0.6.0): a defaulted
    # success value would let an emitter that never checked the route or
    # the verification status mint a gate-satisfying record.
    [Parameter(Mandatory = $true)][ValidateSet("FULL", "DEGRADED")][string]$VerificationStatus,
    [Parameter(Mandatory = $true)][string]$RouteNote,
    [string]$Mode = "diff",
    # Optional (0.7.0): the application checkpoint that authorized the fix
    # edits inside the attested range (references/application-checkpoint.md).
    # Must live under the checkpoint row of
    # references/model-prompting-notes.md's round-artifact-roots
    # declaration - the verifier re-locates and re-hashes it there, so
    # an artifact anywhere else is unverifiable.
    # When present, the record binds the checkpoint hash AND the
    # emitter-computed changed-path set - never caller-supplied - so an
    # attestation minted for a different change set fails verification.
    [string]$CheckpointFile = "",
    # Optional (0.36.0): the review mirror and the clone bridge to remove
    # once the record is written. See the REAP note in the header.
    [string]$ReapMirror = "",
    [string]$ReapBridge = ""
)

. (Join-Path $PSScriptRoot "review-tree-removal.ps1")

function Resolve-FullSha($repo, $sha, $label) {
    $full = (& git -C $repo rev-parse --verify --quiet ($sha + "^{commit}") 2>$null | Out-String).Trim()
    if (($LASTEXITCODE -ne 0) -or -not $full) {
        Write-Output "ERROR: $label '$sha' does not resolve to a commit in $repo"
        exit 2
    }
    return $full
}

function Resolve-MirrorParent($repoRoot) {
    # The declared review mirror parent, read through the ONE reader of
    # the round-artifact-roots declaration, tools/artifact-roots.ps1,
    # invoked in-process so its exit reaches $LASTEXITCODE here (the
    # tool's documented $args fallback; measured 2026-09-13 on both
    # hosts). Every failure exits 2 with nothing written: a parent that
    # could not be read is never a parent that accepts everything.
    $tool = Join-Path $PSScriptRoot "artifact-roots.ps1"
    if (-not (Test-Path -LiteralPath $tool -PathType Leaf)) {
        Write-Output "ERROR: the declared review mirror parent could not be read: $tool is missing"
        exit 2
    }
    $lines = @()
    $why = ""
    try {
        $lines = @(& $tool -RepoRoot $repoRoot -Json 2>&1)
    } catch {
        $why = $_.Exception.Message
    }
    $toolExit = $LASTEXITCODE
    $text = (@($lines | ForEach-Object { [string]$_ }) -join "`n")
    if ($why) {
        Write-Output ("ERROR: the declared review mirror parent could not be read: " + $why)
        exit 2
    }
    if ($toolExit -ne 0) {
        Write-Output ("ERROR: the declared review mirror parent could not be read: artifact-roots.ps1 exited " + $toolExit + ": " + $text)
        exit 2
    }
    $row = ""
    try {
        $parsed = ConvertFrom-Json $text
        $row = [string]$parsed.reviewMirror
    } catch {
        $row = ""
    }
    if (-not $row) {
        Write-Output ("ERROR: the declared review mirror parent could not be read: no reviewMirror row in the tool's answer: " + $text)
        exit 2
    }
    $i = $row.IndexOf("<")
    if ($i -le 0) {
        Write-Output ("ERROR: the declared review mirror parent could not be read: the row has no per-debate placeholder (" + $row + ")")
        exit 2
    }
    $parent = $row.Substring(0, $i).Replace("\", "/").TrimEnd("/")
    if ((-not $parent) -or (-not [System.IO.Path]::IsPathRooted($parent))) {
        Write-Output ("ERROR: the declared review mirror parent could not be read: the row is not rooted (" + $row + ")")
        exit 2
    }
    return $parent
}

function Resolve-ReapPath($label, $raw, $repoTop, $commonFull, $headFull, $allowRemediation, $mirrorParent) {
    # Returns the resolved full path of a tree this attestation may
    # remove, or prints ERROR and exits 2. Every refusal here runs before
    # the record is written. The rules are the spec's identity guard:
    # rooted and resolvable, not a filesystem root, an existing
    # directory, not through a link, not overlapping the reviewed repo
    # or its common dir, a .git DIRECTORY (a .git FILE is a linked
    # worktree, never a mirror or a bridge), and a HEAD equal to the
    # attested head - or, for the mirror only, one parallax@local
    # remediation commit whose single parent is that head, which is the
    # commit the mirror tool makes over a tracked back-channel. Last of
    # all, under the declared review mirror parent (any depth, never the
    # parent itself), for the mirror and the bridge alike.
    if ([string]::IsNullOrWhiteSpace($raw)) {
        Write-Output "ERROR: $label is empty"
        exit 2
    }
    if (-not [System.IO.Path]::IsPathRooted($raw)) {
        Write-Output "ERROR: $label must be an absolute path ($raw)"
        exit 2
    }
    $full = $null
    try {
        $full = [System.IO.Path]::GetFullPath($raw).TrimEnd("\")
    } catch {
        Write-Output ("ERROR: $label could not be resolved ($raw): " + $_.Exception.Message)
        exit 2
    }
    $pathRoot = [System.IO.Path]::GetPathRoot($full)
    if ((-not $pathRoot) -or ($full.Length -le ([string]$pathRoot).TrimEnd("\").Length)) {
        Write-Output "ERROR: $label is a filesystem root ($full)"
        exit 2
    }
    $attr = 0
    try {
        $attr = [int][System.IO.File]::GetAttributes($full)
    } catch [System.IO.FileNotFoundException] {
        Write-Output "ERROR: $label does not exist ($full)"
        exit 2
    } catch [System.IO.DirectoryNotFoundException] {
        Write-Output "ERROR: $label does not exist ($full)"
        exit 2
    } catch {
        Write-Output ("ERROR: $label could not be examined ($full): " + $_.Exception.Message)
        exit 2
    }
    if (($attr -band [int][System.IO.FileAttributes]::Directory) -eq 0) {
        Write-Output "ERROR: $label is a file, not a tree ($full)"
        exit 2
    }
    $hit = Test-PathOrAncestorIsLink $full
    if ($hit) {
        Write-Output ("ERROR: $label passes through a directory link at $hit" +
            " - a tree is never removed through a link")
        exit 2
    }
    # The mirror tool's own overlap comparison, against the reviewed
    # repository and against its git common dir (a linked worktree's
    # common dir sits outside its top level).
    $cmp = [System.StringComparison]::OrdinalIgnoreCase
    $p = $full.Replace("\", "/").TrimEnd("/") + "/"
    foreach ($pair in @(@("the reviewed repository", $repoTop), @("the git common dir", $commonFull))) {
        $g = ([string]$pair[1]).Replace("\", "/").TrimEnd("/") + "/"
        if ($p.Equals($g, $cmp)) {
            Write-Output ("ERROR: $label is " + $pair[0] + " itself ($full)")
            exit 2
        }
        if ($p.StartsWith($g, $cmp)) {
            Write-Output ("ERROR: $label is inside " + $pair[0] + " ($full)")
            exit 2
        }
        if ($g.StartsWith($p, $cmp)) {
            Write-Output ("ERROR: $label contains " + $pair[0] + " ($full)")
            exit 2
        }
    }
    $dotGit = Join-Path $full ".git"
    $ga = 0
    try {
        $ga = [int][System.IO.File]::GetAttributes($dotGit)
    } catch {
        Write-Output "ERROR: $label carries no .git entry, so it is not a review tree ($full)"
        exit 2
    }
    if (($ga -band [int][System.IO.FileAttributes]::Directory) -eq 0) {
        Write-Output ("ERROR: $label has a .git FILE, which marks a linked worktree" +
            " - never a mirror or a bridge ($full)")
        exit 2
    }
    if (($ga -band [int][System.IO.FileAttributes]::ReparsePoint) -ne 0) {
        Write-Output ("ERROR: $label has a .git that is a directory link, so its" +
            " identity would be read through the link ($full)")
        exit 2
    }
    $treeHead = (& git --git-dir "$dotGit" rev-parse --verify --quiet "HEAD^{commit}" 2>$null | Out-String).Trim()
    if (($LASTEXITCODE -ne 0) -or -not $treeHead) {
        Write-Output "ERROR: $label has no readable HEAD ($full)"
        exit 2
    }
    $identityOk = ($treeHead -eq $headFull)
    if ((-not $identityOk) -and $allowRemediation) {
        $author = (& git --git-dir "$dotGit" log -1 --format=%ae HEAD 2>$null | Out-String).Trim()
        $authorExit = $LASTEXITCODE
        $parents = @(((& git --git-dir "$dotGit" rev-list --parents -n 1 HEAD 2>$null | Out-String).Trim()) -split "\s+")
        if (($authorExit -eq 0) -and ($LASTEXITCODE -eq 0) -and ($author -eq "parallax@local") -and
            ($parents.Count -eq 2) -and ($parents[1] -eq $headFull)) {
            $identityOk = $true
        }
    }
    if (-not $identityOk) {
        Write-Output ("ERROR: $label is at $treeHead, not the attested head $headFull" +
            " - it is not the tree this verdict was issued on ($full)")
        exit 2
    }
    # LAST: the declared parent. StartsWith on the parent WITH its
    # separator, so a sibling whose name merely begins with the parent's
    # (C:/pxmx) is outside, and never Equals, so the parent itself is
    # never a tree. $p already carries the trailing separator.
    $parentSlash = $mirrorParent.TrimEnd("/") + "/"
    if ($p.Equals($parentSlash, $cmp) -or -not $p.StartsWith($parentSlash, $cmp)) {
        Write-Output ("ERROR: $label is not under the declared review mirror parent " + $mirrorParent + " ($full)")
        exit 2
    }
    return $full
}

function Invoke-Reap($label, $full, $notAttempted) {
    # Runs after the record is written: a failure here is exit 3, with
    # the attestation left standing and the reason named. $notAttempted
    # names any other reap tree that was skipped as a result, so the
    # failure message tells the caller everything left to remove by hand.
    $r = Remove-ReviewTree $full
    if (-not $r.Ok) {
        Write-Output ("ERROR: reap failed for " + $full + ": " + $r.Reason +
            " - the attestation stands; remove the " + $label + " by hand" + $notAttempted)
        exit 3
    }
    Write-Output ("reaped " + $label + ": " + $full)
}

$toplevel = (& git -C $RepoRoot rev-parse --show-toplevel 2>$null | Out-String).Trim()
if (($LASTEXITCODE -ne 0) -or -not $toplevel) {
    Write-Output "ERROR: $RepoRoot is not a git repository"
    exit 2
}
# Common dir, not git-dir: a review adjudicated inside a worktree must
# attest the repo every other worktree (and the pre-push hook) sees.
$commonDir = (& git -C $RepoRoot rev-parse --git-common-dir 2>$null | Out-String).Trim()
if (-not $commonDir) {
    Write-Output "ERROR: could not resolve the git common dir for $RepoRoot"
    exit 2
}
if (-not [System.IO.Path]::IsPathRooted($commonDir)) {
    $commonDir = Join-Path $RepoRoot $commonDir
}

$baseFull = Resolve-FullSha $RepoRoot $BaseSha "BaseSha"
$headFull = Resolve-FullSha $RepoRoot $HeadSha "HeadSha"
if ($baseFull -eq $headFull) {
    Write-Output "ERROR: BaseSha and HeadSha resolve to the same commit - nothing was reviewed"
    exit 2
}

# REAP VALIDATION, before anything is written. Both trees are resolved
# and checked here so a wrong argument is refused at exit 2 with the
# record unwritten, and the removal below runs only against paths this
# block accepted.
$commonFull = [System.IO.Path]::GetFullPath($commonDir).TrimEnd("\")
$reapMirrorFull = $null
$reapBridgeFull = $null
$mirrorParent = $null
# SUPPLIED, not truthy: a parameter that was given on the command line,
# empty or not, always reaches the validation, so an explicitly empty
# value is refused there ("is empty", exit 2) instead of silently
# meaning no reap. A parameter that was not given still means no reap
# and never reads the declaration. Found by the diff debate's round 1
# (2026-09-13); the truthiness form shipped in 0.36.0.
$reapMirrorGiven = $PSBoundParameters.ContainsKey("ReapMirror")
$reapBridgeGiven = $PSBoundParameters.ContainsKey("ReapBridge")
if ($reapMirrorGiven -or $reapBridgeGiven) {
    $mirrorParent = Resolve-MirrorParent $RepoRoot
}
if ($reapMirrorGiven) {
    $reapMirrorFull = Resolve-ReapPath "the reap mirror" $ReapMirror $toplevel $commonFull $headFull $true $mirrorParent
}
if ($reapBridgeGiven) {
    $reapBridgeFull = Resolve-ReapPath "the reap bridge" $ReapBridge $toplevel $commonFull $headFull $false $mirrorParent
}
if ($reapMirrorFull -and $reapBridgeFull) {
    $cmp = [System.StringComparison]::OrdinalIgnoreCase
    $m = $reapMirrorFull.Replace("\", "/").TrimEnd("/") + "/"
    $b = $reapBridgeFull.Replace("\", "/").TrimEnd("/") + "/"
    if ($m.Equals($b, $cmp) -or $m.StartsWith($b, $cmp) -or $b.StartsWith($m, $cmp)) {
        Write-Output ("ERROR: the reap mirror and the reap bridge overlap (" + $reapMirrorFull + ", " + $reapBridgeFull + ") - name two separate trees")
        exit 2
    }
}

$attDir = Join-Path (Join-Path $commonDir "parallax") "attestations"
New-Item -ItemType Directory -Force -Path $attDir | Out-Null

# Schema 2 (0.7.0): checkpoint_binding is the emitter-authored
# DECLARATION of whether this record carries checkpoint metadata -
# without it, deleting the binding fields would downgrade a bound record
# to legacy-unbound and the verifier could not tell (Sol round 2).
$att = [ordered]@{
    schema              = 2
    repo                = (Split-Path $toplevel -Leaf)
    mode                = $Mode
    base_sha            = $baseFull
    head_sha            = $headFull
    verdict             = $Verdict
    verification_status = $VerificationStatus
    rounds              = $Rounds
    participants        = $Participants
    route_note          = $RouteNote
    checkpoint_binding  = "none"
    stamp               = (Get-Date -Format "yyyy-MM-ddTHH:mm:ss")
}
if ($CheckpointFile) {
    if (-not (Test-Path $CheckpointFile)) {
        Write-Output "ERROR: checkpoint file not found: $CheckpointFile"
        exit 2
    }
    $cpFull = (Resolve-Path $CheckpointFile).Path
    $cpDir = Join-Path (Join-Path $commonDir "parallax") "application-checkpoints"
    $cpDirFull = if (Test-Path $cpDir) { (Resolve-Path $cpDir).Path } else { $null }
    if ((-not $cpDirFull) -or ((Split-Path $cpFull -Parent) -ne $cpDirFull)) {
        Write-Output "ERROR: checkpoint must live under $cpDir - the verifier re-hashes it there"
        exit 2
    }
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.IO.File]::ReadAllBytes($cpFull)
    $cpHash = ([System.BitConverter]::ToString($sha.ComputeHash($bytes)) -replace '-', '').ToLower()
    $changed = @(& git -C $RepoRoot diff --name-only ($baseFull + ".." + $headFull) 2>$null | Where-Object { $_ })
    if ($LASTEXITCODE -ne 0) {
        Write-Output "ERROR: could not compute the changed-path set for $baseFull..$headFull"
        exit 2
    }
    $att["checkpoint_binding"] = "bound"
    $att["checkpoint_file"] = (Split-Path $CheckpointFile -Leaf)
    $att["checkpoint_hash"] = $cpHash
    $att["changed_paths"] = $changed
}
$outFile = Join-Path $attDir ($headFull + ".json")
$json = $att | ConvertTo-Json -Depth 3
try {
    Set-Content -LiteralPath $outFile -Value $json -Encoding ASCII -NoNewline -ErrorAction Stop
} catch {
    Write-Output ("ERROR: the attestation could not be written to " + $outFile + ": " + $_.Exception.Message + " - nothing was reaped")
    exit 2
}
$writtenText = $null
try {
    $writtenText = [System.IO.File]::ReadAllText($outFile)
} catch {
    $writtenText = $null
}
# Ordinal: -ne is case-insensitive on strings, so it would accept a read-back that differs only in letter case.
if (-not [string]::Equals($writtenText, $json, [System.StringComparison]::Ordinal)) {
    Write-Output ("ERROR: the attestation on disk does not match what was written (" + $outFile + ") - nothing was reaped")
    exit 2
}
Write-Output "attestation written: $outFile ($Verdict, $baseFull..$headFull)"
# THE REAP, after the record and in this order: mirror, its advisory
# sidecar, then the bridge. A failure stops at the first tree that
# could not be removed (exit 3) and leaves the record standing.
if ($reapMirrorFull) {
    $bridgeNote = ""
    if ($reapBridgeFull) { $bridgeNote = "; the bridge was not attempted: " + $reapBridgeFull }
    Invoke-Reap "mirror" $reapMirrorFull $bridgeNote
    # The mirror tool's advisory sibling, `<mirror>.source-manifest`,
    # removed only when it is an ordinary file: a directory or a link
    # there is not the sidecar and is left alone.
    $sidecar = $reapMirrorFull + ".source-manifest"
    $sa = $null
    try {
        $sa = [int][System.IO.File]::GetAttributes($sidecar)
    } catch [System.IO.FileNotFoundException] {
        $sa = $null
    } catch [System.IO.DirectoryNotFoundException] {
        $sa = $null
    } catch {
        Write-Output ("ERROR: reap failed for " + $sidecar + ": the sidecar could not be examined: " +
            $_.Exception.Message + " - the attestation stands; remove the sidecar by hand" + $bridgeNote)
        exit 3
    }
    if (($null -ne $sa) -and
        (($sa -band [int][System.IO.FileAttributes]::Directory) -eq 0) -and
        (($sa -band [int][System.IO.FileAttributes]::ReparsePoint) -eq 0)) {
        try {
            [System.IO.File]::SetAttributes($sidecar, [System.IO.FileAttributes]::Normal)
            [System.IO.File]::Delete($sidecar)
        } catch {
            Write-Output ("ERROR: reap failed for " + $sidecar + ": " + $_.Exception.Message +
                " - the attestation stands; remove the sidecar by hand" + $bridgeNote)
            exit 3
        }
        # THE POSTCONDITION, read back rather than inferred from the
        # absence of an exception (tools/review-tree-removal.ps1:167-179
        # does the same for the tree root).
        try {
            [void][System.IO.File]::GetAttributes($sidecar)
            Write-Output ("ERROR: reap failed for " + $sidecar + ": the sidecar still exists after removal" +
                " - the attestation stands; remove the sidecar by hand" + $bridgeNote)
            exit 3
        } catch [System.IO.FileNotFoundException] {
            # gone: fall through to the success line below
        } catch [System.IO.DirectoryNotFoundException] {
            # gone: fall through to the success line below
        } catch {
            Write-Output ("ERROR: reap failed for " + $sidecar + ": the sidecar could not be re-examined after removal: " +
                $_.Exception.Message + " - the attestation stands; remove the sidecar by hand" + $bridgeNote)
            exit 3
        }
        Write-Output ("reaped sidecar: " + $sidecar)
    }
}
if ($reapBridgeFull) {
    Invoke-Reap "bridge" $reapBridgeFull ""
}
exit 0
