# verify-attestation.ps1 - check a pushed main sha against the recorded
# multi-model-verify attestations (written by write-attestation.ps1 into
# <git-common-dir>\parallax\attestations\<head-sha>.json).
#
# Match rules (Sol consult 2026-07-19, session-adjudicated):
#   direct / fast-forward: the pushed sha itself is attested (head_sha
#     equals it, verdict PASS).
#   merge commit: parent2 is attested with verdict PASS AND the
#     attestation's base_sha equals parent1 - extra commits or a rebase
#     between review and merge break the parent match, and a squash
#     changes the sha entirely; both correctly force re-review.
#
# Non-blocking v1: the pre-push callers print a warning on nonzero and
# never block the push. Windows PowerShell 5.1 compatible, ASCII ONLY.
#
# Exit codes: 0 attested (detail on stdout), 1 not attested (reason on
# stdout), 2 script/repo error.
param(
    [Parameter(Mandatory = $true)][string]$RepoRoot,
    [Parameter(Mandatory = $true)][string]$LocalSha
)

function Read-Attestation($attDir, $sha, $repoName) {
    $file = Join-Path $attDir ($sha + ".json")
    if (-not (Test-Path $file)) { return $null }
    $att = $null
    try {
        $att = Get-Content $file -Raw | ConvertFrom-Json
    } catch {
        return $null
    }
    if (-not $att) { return $null }
    # Strict shape: wrong schema, wrong mode, wrong repo, or a head_sha
    # that does not match its own filename is a stale or hand-edited
    # record - never a pass.
    if ($att.schema -ne 1) { return $null }
    if ($att.mode -ne "diff") { return $null }
    if ($att.head_sha -ne $sha) { return $null }
    if ($att.repo -ne $repoName) { return $null }
    return $att
}

function Test-AttestationPasses($att) {
    # A gate-satisfying record binds the FULL verification state and the
    # confirmed route, not just the verdict (Sol diff review 0.6.0): a
    # DEGRADED PASS or an unconfirmed-route PASS must not satisfy the gate.
    return (($att.verdict -eq "PASS") -and
            ($att.verification_status -eq "FULL") -and
            ($att.route_note -eq "effective route confirmed"))
}

function Get-AttestationRejectReason($att, $label) {
    return ("attestation for $label is verdict=$($att.verdict)" +
        " status=$($att.verification_status) route='$($att.route_note)'" +
        " - a FULL, confirmed-route PASS is required")
}

$toplevel = (& git -C $RepoRoot rev-parse --show-toplevel 2>$null | Out-String).Trim()
if (($LASTEXITCODE -ne 0) -or -not $toplevel) {
    Write-Output "ERROR: $RepoRoot is not a git repository"
    exit 2
}
$repoName = Split-Path $toplevel -Leaf
$commonDir = (& git -C $RepoRoot rev-parse --git-common-dir 2>$null | Out-String).Trim()
if (-not $commonDir) {
    Write-Output "ERROR: could not resolve the git common dir for $RepoRoot"
    exit 2
}
if (-not [System.IO.Path]::IsPathRooted($commonDir)) {
    $commonDir = Join-Path $RepoRoot $commonDir
}

$local = (& git -C $RepoRoot rev-parse --verify --quiet ($LocalSha + "^{commit}") 2>$null | Out-String).Trim()
if (($LASTEXITCODE -ne 0) -or -not $local) {
    Write-Output "ERROR: '$LocalSha' does not resolve to a commit in $RepoRoot"
    exit 2
}

$attDir = Join-Path (Join-Path $commonDir "parallax") "attestations"
if (-not (Test-Path $attDir)) {
    Write-Output "no attestations recorded yet ($attDir)"
    exit 1
}

# Direct / fast-forward: the pushed sha carries its own attestation.
$att = Read-Attestation $attDir $local $repoName
if ($att) {
    if (Test-AttestationPasses $att) {
        Write-Output "attested: $local (direct, $($att.stamp), $($att.participants))"
        exit 0
    }
    Write-Output (Get-AttestationRejectReason $att $local)
    exit 1
}

# Merge commit: parent2 (the reviewed branch head) must be attested and
# the attestation's base must be parent1 (the main the merge landed on).
$p1 = (& git -C $RepoRoot rev-parse --verify --quiet ($local + "^1") 2>$null | Out-String).Trim()
$p2 = (& git -C $RepoRoot rev-parse --verify --quiet ($local + "^2") 2>$null | Out-String).Trim()
if ($p2) {
    $att2 = Read-Attestation $attDir $p2 $repoName
    if ($att2 -and (Test-AttestationPasses $att2) -and ($att2.base_sha -eq $p1)) {
        Write-Output "attested: merge $local (parent2 $p2 reviewed against base $p1, $($att2.stamp))"
        exit 0
    }
    if ($att2 -and (Test-AttestationPasses $att2)) {
        Write-Output "merge parent2 $p2 is attested but against base $($att2.base_sha), not parent1 $p1 (extra commits or rebase since review) - re-review"
        exit 1
    }
    if ($att2) {
        Write-Output (Get-AttestationRejectReason $att2 "merge parent2 $p2")
        exit 1
    }
    Write-Output "no attestation for $local or its merge parent2 $p2"
    exit 1
}

Write-Output "no attestation for $local"
exit 1
