# Stub `codex app-server --stdio` for the tool-surface probe tests.
#
# It speaks the same line-delimited JSON-RPC the real app server does:
# read a request object per line from stdin, write a response object per
# line to stdout, exit when stdin closes.
#
# It BRANCHES ON ITS ARGUMENTS, which is what lets one stub serve both
# passes of a two-pass probe and lets a test assert the invocation
# contract at the same time. Pass 2 is recognised by the isolation flags
# the real dispatch carries.
#
# PARALLAX_STUB_AS_LOG       - file to append one JSON array per call to
# PARALLAX_STUB_AS_PASS1     - JSON for pass 1's mcpServerStatus/list data
# PARALLAX_STUB_AS_PASS2     - JSON for pass 2's data
# PARALLAX_STUB_AS_EXIT      - exit with this code instead of 0
# PARALLAX_STUB_AS_MODE      - normal (default), malformed, noframes,
#                              rpcerror, hang, dieafterinit
# PARALLAX_STUB_AS_HANGSECS  - how long `hang` sleeps, default 60
#
# Windows PowerShell 5.1 compatible, ASCII ONLY.
param()

$log = $env:PARALLAX_STUB_AS_LOG
if ($log) { Add-Content -Path $log -Value (ConvertTo-Json @($args) -Compress) }

if ($env:PARALLAX_STUB_AS_EXIT) { exit [int]$env:PARALLAX_STUB_AS_EXIT }

$mode = $env:PARALLAX_STUB_AS_MODE
if (-not $mode) { $mode = "normal" }

if ($mode -eq "noframes") {
    # Consume stdin and say nothing at all. A probe that reads this as an
    # empty tool surface would be reporting an unmade measurement.
    while ($null -ne [Console]::In.ReadLine()) { }
    exit 0
}

if ($mode -eq "hang") {
    $secs = 60
    if ($env:PARALLAX_STUB_AS_HANGSECS) { $secs = [int]$env:PARALLAX_STUB_AS_HANGSECS }
    Start-Sleep -Seconds $secs
    exit 0
}

# The isolation flags identify pass 2. The real dispatch carries them and
# pass 1 deliberately does not.
$isPass2 = ($args -contains "--disable") -and ($args -contains "plugins")

$payload = if ($isPass2) { $env:PARALLAX_STUB_AS_PASS2 } else { $env:PARALLAX_STUB_AS_PASS1 }
if (-not $payload) { $payload = "[]" }

[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)

while ($true) {
    $line = [Console]::In.ReadLine()
    if ($null -eq $line) { break }
    if (-not $line.Trim()) { continue }

    $req = $null
    try { $req = $line | ConvertFrom-Json } catch { continue }
    $id = $req.id
    $method = $req.method

    if ($mode -eq "malformed") {
        [Console]::Out.WriteLine('{"id":' + $id + ',"result":{"data":[{"name":')
        continue
    }

    if ($method -eq "initialize") {
        [Console]::Out.WriteLine((ConvertTo-Json -Compress -Depth 6 @{
            id = $id
            result = @{ userAgent = "stub/0.0.0"; codexHome = "C:\stub" }
        }))
        if ($mode -eq "dieafterinit") { exit 3 }
        continue
    }

    if ($method -eq "mcpServerStatus/list") {
        if ($mode -eq "rpcerror") {
            [Console]::Out.WriteLine((ConvertTo-Json -Compress -Depth 6 @{
                id = $id
                error = @{ code = -32601; message = "method not found" }
            }))
            continue
        }
        # The payload is emitted as raw JSON, not re-serialized, so a test
        # controls the EXACT shape the parser sees - including a null
        # serverInfo, which is the field the whole design turns on.
        [Console]::Out.WriteLine('{"id":' + $id + ',"result":{"data":' + $payload + '}}')
        continue
    }

    if ($method -eq "experimentalFeature/list") {
        [Console]::Out.WriteLine('{"id":' + $id + ',"result":{"data":[]}}')
        continue
    }
}
exit 0
