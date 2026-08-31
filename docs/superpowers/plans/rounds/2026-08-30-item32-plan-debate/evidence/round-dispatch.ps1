param(
    [Parameter(Mandatory = $true)][string]$N,
    [Parameter(Mandatory = $true)][string]$OverrideSuffix
)

# One debate round, end to end: rebuild the mirror at the session's own
# path, verify the plan copy, compute the prior state from the live
# rollout, dispatch, check the route header, and bind the evidence.
#
# The mirror path is FIXED at kerev-i32b. Measured 2026-08-31: rebuilding
# at a different path while resuming the same codex session makes the
# binder refuse the round, because the resumed slice then carries a
# preamble whose `cwd` is not this session's. That cost one round.

$ErrorActionPreference = 'Continue'

$repo     = "C:\Users\Brandon\Documents\parallax"
$scratch  = "C:\Users\Brandon\AppData\Local\Temp\claude\C--Users-Brandon-Documents-parallax\45fa9c27-1235-4a90-90c2-654907fea480\scratchpad"
$mirror   = "C:\Users\Brandon\AppData\Local\Temp\kerev-i32b"
$ovrF     = "C:\Users\Brandon\AppData\Local\Temp\kerev-$OverrideSuffix.skills-override.txt"
$sessId   = "01a055c5-935e-76e3-ad1d-83721bc67d79"
$rollout  = "C:\Users\Brandon\.codex\sessions\2026\08\30\rollout-2026-08-30T22-03-26-01a055c5-935e-76e3-ad1d-83721bc67d79.jsonl"
$planRel  = "docs\superpowers\plans\2026-08-30-item32-detached-dispatch.md"

$briefF   = Join-Path $scratch "i32-brief-r$N.md"
$replyF   = Join-Path $scratch "i32-reply-r$N.md"
$transF   = Join-Path $scratch "i32-transcript-r$N.txt"
$priorF   = Join-Path $scratch "i32-priorstate-r$N.json"

if (-not (Test-Path -LiteralPath $briefF)) { throw "no brief at $briefF" }
foreach ($p in @($replyF, $transF, $priorF)) {
    if (Test-Path -LiteralPath $p) { throw "control path already exists: $p" }
}
if (Test-Path -LiteralPath $ovrF) { throw "override path already exists: $ovrF" }

"=== MIRROR ==="
& powershell -NoProfile -File (Join-Path $repo "tools\new-review-mirror.ps1") `
    -RepoRoot $repo -MirrorPath $mirror -OverrideOut $ovrF -Force 2>&1 |
    Select-String -Pattern "^mirror:|^source_head:|^mirror_head:|^probe:|^override:" |
    ForEach-Object { $_.Line }

function Get-Sha([string]$path) {
    $b = [System.IO.File]::ReadAllBytes($path)
    return ([System.BitConverter]::ToString(
        ([System.Security.Cryptography.SHA256]::Create()).ComputeHash($b)) -replace '-', '').ToLower()
}

$srcPlan = Get-Sha (Join-Path $repo $planRel)
$mirPlan = Get-Sha (Join-Path $mirror $planRel)
"planIdentical=$($srcPlan -ceq $mirPlan)"
if ($srcPlan -cne $mirPlan) { throw "the mirror's plan copy is not the source's" }

$ovrSha = Get-Sha $ovrF

# Prior state is measured from the live rollout immediately before the
# call. That is the same claim nextState makes, and it does not have to be
# carried across a failed round.
$rBytes = [System.IO.File]::ReadAllBytes($rollout)
$rSha = Get-Sha $rollout
$state = [ordered]@{
    kind         = "resume"
    rolloutFile  = $rollout
    sessionId    = $sessId
    bytes        = $rBytes.Length
    prefixSha256 = $rSha
}
($state | ConvertTo-Json -Depth 5) | Set-Content -LiteralPath $priorF -Encoding UTF8

$briefText = [System.IO.File]::ReadAllText($briefF, (New-Object System.Text.UTF8Encoding($false, $true)))
$canon = $briefText.Replace("`r`n", "`n").Trim()
$briefSha = ([System.BitConverter]::ToString(
    ([System.Security.Cryptography.SHA256]::Create()).ComputeHash(
        [System.Text.Encoding]::UTF8.GetBytes($canon))) -replace '-', '').ToLower()

"=== DISPATCH ==="
"priorBytes=$($rBytes.Length)"
"briefSha256=$briefSha"

$priorOutputEncoding = $OutputEncoding
Push-Location $mirror
try {
    $OutputEncoding = New-Object System.Text.UTF8Encoding($false)
    $brief = [System.IO.File]::ReadAllText($briefF, (New-Object System.Text.UTF8Encoding($false, $true)))
    $bytes = [System.IO.File]::ReadAllBytes($ovrF)
    $seen = ([System.BitConverter]::ToString(([System.Security.Cryptography.SHA256]::Create()).ComputeHash($bytes)) -replace '-', '').ToLower()
    if ($seen -cne $ovrSha) { throw "the override file changed after the probe verified it" }
    $override = (New-Object System.Text.UTF8Encoding($false, $true)).GetString($bytes)
    $brief | codex exec --sandbox read-only --disable plugins --disable apps --disable memories -c mcp_servers.node_repl.enabled=false -c $override -m gpt-5.6-sol -c model_reasoning_effort=high --output-last-message $replyF resume $sessId - > $transF 2>&1
    "codexExit=$LASTEXITCODE"
} finally {
    $OutputEncoding = $priorOutputEncoding
    Pop-Location
}

"replyExists=$(Test-Path -LiteralPath $replyF)"

"=== ROUTE ==="
Get-Content -LiteralPath $transF -TotalCount 20 |
    Select-String -Pattern "workdir:|model:|provider:|sandbox:|reasoning effort:|session id:" |
    ForEach-Object { $_.Line.Trim() }

"=== BINDING ==="
& powershell -NoProfile -File (Join-Path $repo "tools\read-codex-round-evidence.ps1") `
    -Resume -RolloutFile $rollout -PriorState $priorF -ExpectedBriefSha256 $briefSha -Json
"binderExit=$LASTEXITCODE"
