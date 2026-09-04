# run-hook.ps1 - entry point for the backlog hooks in .claude/settings.json.
# Hands the hook's stdin straight to the named Python script and exits with
# its code. A missing python prints a note and exits 0, because a hook
# must never wedge a session (spec, Error handling); the pre-push hook is
# the one place a missing tool refuses, and it is not this file.
#
# THIS SCRIPT MUST NOT READ STDIN. Measured 2026-09-04 under BOTH hosts,
# with the payload piped into `-File` exactly as settings.json runs it:
# [Console]::In.ReadToEnd() returns EMPTY, and so does a StreamReader over
# [Console]::OpenStandardInput(); $input fills only when the param block
# also declares a ValueFromPipeline parameter, and then the host has
# already re-decoded the bytes with the console code page, so a payload
# holding one em dash reaches Python corrupted on 5.1 AND on 7. Leaving
# stdin untouched lets the child inherit the handle, which delivered the
# payload BYTE-EXACT on both hosts with no encoding step at all.
param([Parameter(Mandatory = $true)][string]$Script)
$ErrorActionPreference = 'Continue'
$code = 1
if ($Script -notmatch '^[A-Za-z0-9_.-]+\.py$' -or $Script -match '\.\.') {
    Write-Output "backlog hook: script $Script is not a bare .py name; nothing checked"
    exit 0
}
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
& $python.Source $target
if ($null -ne $LASTEXITCODE) { $code = $LASTEXITCODE }
exit $code
