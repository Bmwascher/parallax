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
# PARALLAX_STUB_AS_FEATURES1 - JSON for pass 1's experimentalFeature/list
# PARALLAX_STUB_AS_FEATURES2 - JSON for pass 2's
# PARALLAX_STUB_AS_EXIT      - exit with this code instead of 0
# PARALLAX_STUB_AS_MODE      - normal (default), malformed, noframes,
#                              rpcerror, hang, dieafterinit, garbage,
#                              nodata, features-silent, features-rpcerror,
#                              features-nodata
# PARALLAX_STUB_AS_HANGSECS  - how long `hang` sleeps, default 60
#
# Windows PowerShell 5.1 compatible, ASCII ONLY.
param()

$log = $env:PARALLAX_STUB_AS_LOG
if ($log) { Add-Content -Path $log -Value (ConvertTo-Json @($args) -Compress) }

if ($env:PARALLAX_STUB_AS_EXIT) { exit [int]$env:PARALLAX_STUB_AS_EXIT }

$mode = $env:PARALLAX_STUB_AS_MODE
if (-not $mode) { $mode = "normal" }

# STDIN IS READ AS RAW BYTES, NOT THROUGH [Console]::In.
#
# This is the fixture's fidelity to the thing it stands in for, and it was
# NOT here first. A StreamReader built on a UTF-8 encoding silently strips
# a matching preamble before any caller sees it, so this stub could not
# observe a byte-order mark at all - it read a clean `{"id":1,...}` from a
# stream that carried `EF BB BF {"id":1,...}` on the wire. The real app
# server parses BYTES and rejects that frame. Measured 2026-08-11: with
# the defect deliberately restored, a strict first-frame check written on
# top of [Console]::In PASSED, which is a guard proving the opposite of
# what it looks like.
$rawIn = [Console]::OpenStandardInput()

function Read-RawLine($stream) {
    # One line as BYTES. $null at end of stream; an empty array for a blank
    # line, which is a different thing and the caller must not confuse them.
    $bytes = New-Object System.Collections.Generic.List[byte]
    while ($true) {
        $b = $stream.ReadByte()
        if ($b -lt 0) {
            if ($bytes.Count -eq 0) { return $null }
            break
        }
        if ($b -eq 10) { break }
        if ($b -eq 13) { continue }
        $bytes.Add([byte]$b)
    }
    return ,$bytes.ToArray()
}

if ($mode -eq "noframes") {
    # Consume stdin and say nothing at all. A probe that reads this as an
    # empty tool surface would be reporting an unmade measurement.
    while ($null -ne (Read-RawLine $rawIn)) { }
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

# The FEATURE payload, same shape rule: raw JSON so a test controls exactly
# what the parser sees.
$featurePayload = if ($isPass2) { $env:PARALLAX_STUB_AS_FEATURES2 } else { $env:PARALLAX_STUB_AS_FEATURES1 }
if (-not $featurePayload) { $featurePayload = "[]" }

$script:GarbageSent = $false

[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)

# THE FIRST FRAME IS CHECKED STRICTLY, and this is a regression guard
# rather than tidiness. The probe's first version wrote stdin through
# Process.StandardInput, which on Windows PowerShell 5.1 prefixes a
# three-byte UTF-8 preamble to the first write; the real app server saw
# `<BOM>{"id":1,...}`, which is not JSON, and the probe failed by
# construction on that host. Every case in the suite stayed GREEN, because
# the `catch { continue }` below simply skipped the corrupt frame and this
# stub answered the later polls anyway. A lenient stub certified a broken
# instrument.
#
# So a first frame whose FIRST BYTE is not `{` is now a hard stub failure,
# and the probe blocks on the non-zero exit.
$first = $true

while ($true) {
    $raw = Read-RawLine $rawIn
    if ($null -eq $raw) { break }
    if ($first) {
        $first = $false
        if ($raw.Count -eq 0 -or $raw[0] -ne 0x7B) {
            $lead = (@($raw | Select-Object -First 8) |
                     ForEach-Object { $_.ToString("X2") }) -join " "
            [Console]::Error.WriteLine(
                "STUB: the first frame's first byte is not '{' (0x7B). Leading" +
                " bytes: " + $lead)
            exit 9
        }
    }
    # UTF8.GetString does NOT strip a preamble, which is the point: what the
    # check above saw is what the parser below sees.
    $line = [System.Text.Encoding]::UTF8.GetString($raw)
    if (-not $line.Trim()) { continue }

    $req = $null
    try { $req = $line | ConvertFrom-Json } catch { continue }
    $id = $req.id
    $method = $req.method

    if ($mode -eq "malformed") {
        [Console]::Out.WriteLine('{"id":' + $id + ',"result":{"data":[{"name":')
        continue
    }

    # GARBAGE-THEN-VALID. A non-blank line that is not a JSON-RPC frame at
    # all, emitted BEFORE the real answer, so the rest of the exchange is
    # perfectly well formed. The probe used to skip such a line and report
    # the valid answer as a whole stream.
    if ($mode -eq "garbage" -and -not $script:GarbageSent) {
        $script:GarbageSent = $true
        [Console]::Out.WriteLine('this line is not a json-rpc frame')
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
        # A RESULT WITH NO DATA MEMBER. Well-formed JSON, correct id, and no
        # surface in it at all. The probe used to turn this into an empty
        # surface and report clean.
        if ($mode -eq "nodata") {
            [Console]::Out.WriteLine('{"id":' + $id + ',"result":{}}')
            continue
        }
        # The payload is emitted as raw JSON, not re-serialized, so a test
        # controls the EXACT shape the parser sees - including a null
        # serverInfo, which is the field the whole design turns on.
        [Console]::Out.WriteLine('{"id":' + $id + ',"result":{"data":' + $payload + '}}')
        continue
    }

    if ($method -eq "experimentalFeature/list") {
        # The feature surface the frozen plan asked for and the first
        # shipped probe never requested. Its failure directions are the same
        # as the status surface's, so they are stubbable the same way.
        if ($mode -eq "features-silent") { continue }
        if ($mode -eq "features-rpcerror") {
            [Console]::Out.WriteLine((ConvertTo-Json -Compress -Depth 6 @{
                id = $id
                error = @{ code = -32601; message = "method not found" }
            }))
            continue
        }
        if ($mode -eq "features-nodata") {
            [Console]::Out.WriteLine('{"id":' + $id + ',"result":{}}')
            continue
        }
        [Console]::Out.WriteLine('{"id":' + $id + ',"result":{"data":' + $featurePayload + '}}')
        continue
    }
}
exit 0
