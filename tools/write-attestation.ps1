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
# Exit codes: 0 written, 2 argument/repo error.
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
    # Must live in the canonical <git-common-dir>/parallax/
    # application-checkpoints/ directory - the verifier re-locates and
    # re-hashes it there, so an artifact anywhere else is unverifiable.
    # When present, the record binds the checkpoint hash AND the
    # emitter-computed changed-path set - never caller-supplied - so an
    # attestation minted for a different change set fails verification.
    [string]$CheckpointFile = ""
)

function Resolve-FullSha($repo, $sha, $label) {
    $full = (& git -C $repo rev-parse --verify --quiet ($sha + "^{commit}") 2>$null | Out-String).Trim()
    if (($LASTEXITCODE -ne 0) -or -not $full) {
        Write-Output "ERROR: $label '$sha' does not resolve to a commit in $repo"
        exit 2
    }
    return $full
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

$attDir = Join-Path (Join-Path $commonDir "parallax") "attestations"
New-Item -ItemType Directory -Force -Path $attDir | Out-Null

$att = [ordered]@{
    schema              = 1
    repo                = (Split-Path $toplevel -Leaf)
    mode                = $Mode
    base_sha            = $baseFull
    head_sha            = $headFull
    verdict             = $Verdict
    verification_status = $VerificationStatus
    rounds              = $Rounds
    participants        = $Participants
    route_note          = $RouteNote
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
    $att["checkpoint_file"] = (Split-Path $CheckpointFile -Leaf)
    $att["checkpoint_hash"] = $cpHash
    $att["changed_paths"] = $changed
}
$outFile = Join-Path $attDir ($headFull + ".json")
$att | ConvertTo-Json -Depth 3 | Set-Content -Path $outFile -Encoding ASCII
Write-Output "attestation written: $outFile ($Verdict, $baseFull..$headFull)"
exit 0
