# run-hook.ps1 - entry point for the backlog hooks in .claude/settings.json.
# Passes the hook's stdin JSON to the named Python script and exits with
# its code. A missing python prints a note and exits 0, because a hook
# must never wedge a session (spec, Error handling); the pre-push hook is
# the one place a missing tool refuses, and it is not this file.
param([Parameter(Mandatory = $true)][string]$Script)
$ErrorActionPreference = 'Continue'
$target = Join-Path $PSScriptRoot $Script
if (-not (Test-Path -LiteralPath $target)) {
    Write-Output "backlog hook: script $Script not found; nothing checked"
    exit 0
}
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Output "backlog hook: python not found; nothing checked"
    exit 0
}
$payload = [Console]::In.ReadToEnd()
$prior = $OutputEncoding
try {
    $OutputEncoding = New-Object System.Text.UTF8Encoding($false)
    $payload | & $python.Source $target
    $code = $LASTEXITCODE
} finally {
    $OutputEncoding = $prior
}
exit $code
