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
    if (($att.schema -ne 1) -and ($att.schema -ne 2)) { return $null }
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
    # Name the field that actually failed. The old message printed all
    # three values and then said a FULL confirmed-route PASS was
    # required, which reads as a contradiction whenever two of the three
    # are fine: verdict=PASS status=FULL and a route note that looks
    # right, followed by a line saying one of them is missing. The rule
    # itself was never wrong - only this message was.
    $bad = @()
    if ($att.verdict -ne "PASS") {
        $bad += "verdict is '$($att.verdict)', needs PASS"
    }
    if ($att.verification_status -ne "FULL") {
        $bad += "verification status is '$($att.verification_status)', needs FULL"
    }
    if ($att.route_note -ne "effective route confirmed") {
        # A transport-failure class legitimately lands here, so say that
        # the token is exact rather than leaving the reader to diff two
        # similar strings by eye.
        $bad += ("route note is '$($att.route_note)', needs the exact" +
            " text 'effective route confirmed'")
    }
    if ($bad.Count -eq 0) {
        return "attestation for $label was rejected but every gate field looks valid - report this, it is a bug in the verifier"
    }
    return ("attestation for $label does not satisfy the gate: " +
        ($bad -join "; ") + " - re-review")
}

function Get-CheckpointBindingFailure($att, $repo, $commonDir) {
    # 0.7.0 checkpoint binding. Returns $null when the binding holds (or
    # the record is genuinely unbound), else the rejection reason.
    # Binding metadata is ALL-OR-NONE: a record carrying any of the three
    # fields must carry and satisfy all of them, or stripping one field
    # (e.g. deleting changed_paths) would evade the rest. Records with
    # none of the fields (pre-0.7.0, or a clean PASS with no fix
    # application) skip the whole check.
    $fields = @("checkpoint_file", "checkpoint_hash", "changed_paths")
    $names = $att.PSObject.Properties.Name
    $present = @($fields | Where-Object { $names -contains $_ })
    if ($att.schema -ge 2) {
        # Schema 2: the emitter DECLARES the binding state, so deleting
        # the binding fields cannot downgrade a bound record to
        # legacy-unbound (Sol round 2, R-F3). The declaration must exist
        # and agree with the fields actually present.
        if (-not ($names -contains "checkpoint_binding")) {
            return "schema 2 record without checkpoint_binding - stale or tampered; re-review"
        }
        if ($att.checkpoint_binding -eq "none") {
            if ($present.Count -ne 0) {
                return "checkpoint_binding=none but binding fields present - stale or tampered; re-review"
            }
            return $null
        }
        if ($att.checkpoint_binding -cne "bound") {
            return "unknown checkpoint_binding '$($att.checkpoint_binding)' - stale or tampered; re-review"
        }
        if ($present.Count -ne 3) {
            return "checkpoint_binding=bound but binding fields missing - stale or tampered; re-review"
        }
    } else {
        # Schema 1 (legacy, pre-0.7.0): binding presence is inferred.
        if ($present.Count -eq 0) { return $null }
        if ($present.Count -ne 3) {
            return "partial checkpoint metadata ($($present -join ', ')) - binding is all-or-none; stale or tampered, re-review"
        }
    }
    # Re-locate and re-hash the artifact at its canonical location: a
    # checkpoint modified, deleted, or substituted after attestation must
    # invalidate the record. checkpoint_file is a leaf name only - a
    # separator would escape the canonical directory.
    if ($att.checkpoint_file -match '[\\/]') {
        return "checkpoint_file carries a path separator - not a canonical leaf name; re-review"
    }
    $cpPath = Join-Path (Join-Path (Join-Path $commonDir "parallax") "application-checkpoints") $att.checkpoint_file
    if (-not (Test-Path $cpPath)) {
        return "checkpoint artifact missing ($($att.checkpoint_file)) - the attested checkpoint no longer exists; re-review"
    }
    $sha = [System.Security.Cryptography.SHA256]::Create()
    $bytes = [System.IO.File]::ReadAllBytes((Resolve-Path $cpPath).Path)
    $hash = ([System.BitConverter]::ToString($sha.ComputeHash($bytes)) -replace '-', '').ToLower()
    if ($hash -cne $att.checkpoint_hash) {
        return "checkpoint artifact hash mismatch ($($att.checkpoint_file)) - modified after attestation; re-review"
    }
    # Ordinal, case-sensitive path comparison: PS Sort-Object and -ne are
    # case-insensitive by default, so a case-only tamper compares equal.
    $recorded = [string[]]@($att.changed_paths | Where-Object { $_ })
    $actual = [string[]]@(& git -C $repo diff --name-only ($att.base_sha + ".." + $att.head_sha) 2>$null | Where-Object { $_ })
    if ($LASTEXITCODE -ne 0) {
        return "could not compute the changed-path set for the attested range; re-review"
    }
    [Array]::Sort($recorded, [System.StringComparer]::Ordinal)
    [Array]::Sort($actual, [System.StringComparer]::Ordinal)
    $mismatch = ($recorded.Count -ne $actual.Count)
    if (-not $mismatch) {
        for ($i = 0; $i -lt $recorded.Count; $i++) {
            if ($recorded[$i] -cne $actual[$i]) { $mismatch = $true; break }
        }
    }
    if ($mismatch) {
        return "changed-path set no longer matches the attested range - stale or tampered; re-review"
    }
    return $null
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
        $bindFail = Get-CheckpointBindingFailure $att $RepoRoot $commonDir
        if ($bindFail) {
            Write-Output "attestation for $local rejected: $bindFail"
            exit 1
        }
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
        $bindFail = Get-CheckpointBindingFailure $att2 $RepoRoot $commonDir
        if ($bindFail) {
            Write-Output "attestation for merge parent2 $p2 rejected: $bindFail"
            exit 1
        }
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
