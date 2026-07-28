# Stub codex for the context-probe tests. Serves a recorded fixture and
# records the flags it was called with, so the tests can assert BOTH the
# parse result and the invocation contract.
#
# PARALLAX_STUB_FIXTURE  - fixture file to emit on the first call
# PARALLAX_STUB_FIXTURE2 - fixture file to emit on later calls
# PARALLAX_STUB_LOG      - file to append the argument list to
# PARALLAX_STUB_EXIT     - exit code to return instead of 0
param()
$log = $env:PARALLAX_STUB_LOG
$calls = 0
if ($log -and (Test-Path $log)) {
    $calls = @(Get-Content $log).Count
}
# One JSON array per call, so a test can pull the EXACT -c value back out.
# Joining with spaces flattened the argument boundaries, which let a
# substring match stand in for byte identity.
if ($log) { Add-Content -Path $log -Value (ConvertTo-Json @($args) -Compress) }
if ($env:PARALLAX_STUB_EXIT) { exit [int]$env:PARALLAX_STUB_EXIT }
$fixture = $env:PARALLAX_STUB_FIXTURE
if ($calls -ge 1 -and $env:PARALLAX_STUB_FIXTURE2) {
    $fixture = $env:PARALLAX_STUB_FIXTURE2
}
Get-Content -Raw $fixture
