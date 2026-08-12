# codex-tool-surface-probe.ps1 - read the reviewer's resolved TOOL surface
# before a review is dispatched, and refuse to report a surface nobody
# measured.
#
# 0.17.0's probe (tools/codex-context-probe.ps1) renders the model-visible
# PROMPT. Tools are not in the prompt, so a round could satisfy every rule
# this repo has while the auditor held a code execution tool. Backlog item
# 7 held that half open and said no free tool-list view existed. Measured
# 2026-08-11, that was true of `codex debug` and false of codex: the app
# server answers `mcpServerStatus/list` over JSON-RPC, which names every
# resolved MCP server and every tool it exposes, and starts no turn. This
# script spends no model tokens.
#
# WHAT IT CAN AND CANNOT ESTABLISH. Measured the same day: a DISABLED
# server and a server that FAILED TO LAUNCH are byte-identical in that
# record - `serverInfo` null, zero tools, `authStatus` unsupported. There
# is no field that separates them. So this script runs two passes and
# treats their directions differently:
#
#   pass 1  no isolation flags. An INSTRUMENT CALIBRATION. If it cannot
#           see a running server with at least one tool, the probe is not
#           known to be able to see anything, the measurement is UNMADE,
#           and the verdict is BLOCKED. A clean pass 2 alone is never
#           reported.
#   pass 2  the flags the review dispatch carries. A tool PRESENT here
#           and outside the allowlist is a real DETECTION - observing
#           something present never depends on telling removal from
#           silence. A tool ABSENT here is a MITIGATION, not proof of
#           removal.
#
# Do NOT describe a clean result as verified reviewer isolation on the
# tool axis. It is not one, and the report says so in its own words.
#
# Both passes poll on the SAME schedule, which is what makes them
# comparable: a pass-2 surface read earlier than pass 1's would be a
# shorter measurement wearing the same name.
#
# EVERY failure direction lands on blocked. Each one of them - a non-zero
# exit, no frames, unreadable JSON, an RPC error, a dead or hanging server
# - produces an empty tool list, which under an empty allowlist is exactly
# what a clean run looks like.
#
# Windows PowerShell 5.1 compatible, ASCII ONLY.
#
# Exit codes: 0 clean, 1 blocked (reason on stdout), 2 script error.
param(
    [string]$WorkDir,
    [switch]$Json,
    [string]$CodexCommand = "codex",
    [int]$TimeoutSeconds = 60,
    [int]$PollIntervalMs = 400,
    [int]$PollCount = 20,
    # The declared allowlist. EMPTY by default: shape A disables the one
    # server that survives the isolation flags, so any tool at all in pass
    # 2 is unexpected. A caller that widens this is widening what the
    # reviewer may hold, and the value belongs in the debate record.
    [string[]]$AllowTool = @()
)

$ErrorActionPreference = "Stop"

function Write-Result($status, $reason, $extra, $asJson) {
    $obj = [ordered]@{ status = $status }
    if ($reason) { $obj.reason = $reason }
    if ($extra) { foreach ($k in $extra.Keys) { $obj[$k] = $extra[$k] } }
    if ($asJson) {
        Write-Output (ConvertTo-Json $obj -Compress -Depth 8)
    } elseif ($status -eq "clean") {
        Write-Output "clean"
        if ($extra -and $extra.note) { Write-Output $extra.note }
    } else {
        Write-Output ("BLOCKED: " + $reason)
    }
    if ($status -eq "clean") { exit 0 } else { exit 1 }
}

function Write-Blocked($reason, $asJson) {
    Write-Result "blocked" $reason $null $asJson
}

# --- transport ---------------------------------------------------------

function Invoke-AppServer($codex, $extraArgs, $workDir, $timeoutSeconds,
                          $pollIntervalMs, $pollCount) {
    <#
      Speak line-delimited JSON-RPC to `codex app-server --stdio`.

      TWO THINGS HERE ARE LOAD-BEARING.

      1. stdout is drained ASYNCHRONOUSLY. The unfiltered surface is 128
         tools WITH their JSON schemas, hundreds of kilobytes; writing
         stdin while an undrained pipe buffer fills deadlocks both ends,
         and the deadlock looks exactly like a hang.
      2. stdin is held OPEN across the polls. Measured 2026-08-11: the
         server exits promptly when stdin closes, and it exits BEFORE its
         MCP servers finish connecting - a request-then-EOF probe gets the
         initialize reply and never sees the tool list at all.
    #>
    $argList = New-Object System.Collections.Generic.List[string]

    # RESOLVE THE COMMAND, AND CHOOSE A FORM Process.Start CAN ACTUALLY
    # RUN. This is more work than it looks and the first version got it
    # wrong.
    #
    # Process.Start with UseShellExecute=false does no PATH or PATHEXT
    # lookup, so a bare name that runs fine at a prompt fails with "cannot
    # find the file specified". Resolving through Get-Command fixes that
    # much. It is NOT enough. Measured 2026-08-11, `codex` on this machine
    # resolves to THREE things:
    #
    #   codex.ps1  ExternalScript  an npm shim
    #   codex.cmd  Application     an npm shim
    #   codex      Application     extensionless, a shell script
    #
    # and there is no codex.exe at all. `Get-Command | Select -First 1`
    # returns whichever the host happens to rank first, which differs
    # between Windows PowerShell and pwsh. Process.Start can execute NONE
    # of those three directly: a .cmd is not an executable image, and
    # neither is an extensionless shell script.
    #
    # The first version of this function took the first candidate and
    # special-cased only .ps1. It worked here by luck. Another session
    # running this probe on the same machine hit the .cmd and the probe
    # failed three times before the cause was found.
    #
    # So: enumerate ALL candidates, and pick by what can be launched -
    # .exe directly, .cmd/.bat through cmd.exe, .ps1 through the current
    # PowerShell host. Prefer .exe because it needs no interpreter at all.
    $candidates = @()
    if (Test-Path -LiteralPath $codex) {
        $candidates = @($codex)
    } else {
        try {
            $candidates = @(Get-Command $codex -All -ErrorAction Stop |
                            ForEach-Object { $_.Source } |
                            Where-Object { $_ })
        } catch { }
        if ($candidates.Count -eq 0) { $candidates = @($codex) }
    }

    $file = $null
    $prefix = @()
    foreach ($ext in @('\.exe$', '\.(cmd|bat)$', '\.ps1$')) {
        $hit = @($candidates | Where-Object { $_ -match $ext }) | Select-Object -First 1
        if (-not $hit) { continue }
        if ($ext -eq '\.exe$') {
            $file = $hit
        } elseif ($ext -eq '\.(cmd|bat)$') {
            # /c, then the batch path. cmd.exe is the only thing that can
            # run a batch file, and Process.Start will not do it for us.
            $file = "$env:SystemRoot\System32\cmd.exe"
            $prefix = @("/c", $hit)
        } else {
            $file = (Get-Process -Id $PID).Path
            $prefix = @("-NoProfile", "-NonInteractive", "-File", $hit)
        }
        break
    }
    if (-not $file) {
        # Nothing launchable. BLOCKED, not a guess: an instrument that
        # cannot start has measured nothing.
        return @{ Started = $false
                  Reason = ("no launchable form of '" + $codex + "' was found" +
                            " (candidates: " + (($candidates -join ", ")) + ")") }
    }
    foreach ($p in $prefix) { $argList.Add($p) }
    $argList.Add("app-server")
    $argList.Add("--stdio")
    foreach ($a in $extraArgs) { $argList.Add($a) }

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $file
    # The argument STRING, not ArgumentList: Windows PowerShell 5.1's
    # ProcessStartInfo has no ArgumentList property at all, and reaching
    # for it there throws on a null. Quoting is applied only to tokens
    # that contain whitespace; every token this script passes is a bare
    # flag or a `key=value` with none.
    $psi.Arguments = ($argList | ForEach-Object {
        if ($_ -match '\s') { '"' + $_ + '"' } else { $_ }
    }) -join " "
    $psi.UseShellExecute = $false
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.StandardOutputEncoding = New-Object System.Text.UTF8Encoding($false)
    $psi.StandardErrorEncoding = New-Object System.Text.UTF8Encoding($false)
    if ($workDir) { $psi.WorkingDirectory = $workDir }

    # THE STDIN ENCODING MUST BE FIXED BEFORE Start, AND NOWHERE ELSE.
    #
    # Measured 2026-08-11. This defect made the probe fail BY CONSTRUCTION
    # on one of the two hosts this repo supports, and twenty green cases
    # said otherwise:
    #
    #   Windows PowerShell 5.1   EF BB BF 7B 22 69 64 ...
    #   pwsh 7                            7B 22 69 64 ...
    #
    # .NET Framework builds Process.StandardInput from Console.InputEncoding.
    # This machine's console is UTF-8, whose encoder carries a THREE-BYTE
    # PREAMBLE, so the `initialize` frame reached the app server with a
    # byte-order mark glued to its opening brace and was not JSON. .NET Core
    # wraps the same encoding to report an EMPTY preamble, which is the whole
    # of why pwsh 7 passed.
    #
    # Two repairs were tried and MEASURED before this one:
    #
    #  - `ProcessStartInfo.StandardInputEncoding` does not exist on 5.1.
    #  - Wrapping `StandardInput.BaseStream` in a preamble-free StreamWriter
    #    does not work either, and the reason is the point: Process.Start
    #    sets AutoFlush on its OWN writer, and setting AutoFlush FLUSHES, so
    #    the three bytes are in the pipe before this function gets the object
    #    back. There is no way to unsend them.
    #
    # So the encoding is changed before Start and restored immediately after.
    $prevInputEncoding = $null
    try {
        $prevInputEncoding = [Console]::InputEncoding
        [Console]::InputEncoding = New-Object System.Text.UTF8Encoding($false)
    } catch {
        # Left to the preamble check below, which BLOCKS. It is never
        # silently accepted.
    }

    $proc = $null
    try {
        $proc = [System.Diagnostics.Process]::Start($psi)
    } catch {
        return @{ Started = $false; Reason = $_.Exception.Message }
    } finally {
        if ($null -ne $prevInputEncoding) {
            try { [Console]::InputEncoding = $prevInputEncoding } catch { }
        }
    }

    # The self-check. The repair above depends on a console property that a
    # host may refuse to set, and a corrupt first frame is unobservable from
    # this side once sent - the server simply reports nothing. So the pipe is
    # inspected instead of trusted, and a preamble is a BLOCK.
    $preamble = @()
    try { $preamble = $proc.StandardInput.Encoding.GetPreamble() } catch { }
    if ($preamble -and $preamble.Length -gt 0) {
        try { $proc.Kill() } catch { }
        return @{ Started = $false
                  Reason = ("the stdin encoding carries a " + $preamble.Length +
                            "-byte preamble, so the first JSON-RPC frame would" +
                            " reach the app server corrupt and no surface could" +
                            " be read") }
    }

    $outTask = $proc.StandardOutput.ReadToEndAsync()
    $errTask = $proc.StandardError.ReadToEndAsync()

    $timedOut = $false
    try {
        $init = '{"id":1,"method":"initialize","params":{"clientInfo":' +
                '{"name":"parallax-tool-surface-probe","version":"1"},' +
                '"capabilities":{"experimentalApi":true}}}'
        $proc.StandardInput.WriteLine($init)
        $proc.StandardInput.Flush()
        for ($n = 1; $n -le $pollCount; $n++) {
            if ($proc.HasExited) { break }
            Start-Sleep -Milliseconds $pollIntervalMs
            $id = 100 + $n
            $proc.StandardInput.WriteLine(
                '{"id":' + $id + ',"method":"mcpServerStatus/list","params":{}}')
            $proc.StandardInput.Flush()
        }
        if (-not $proc.HasExited) { $proc.StandardInput.Close() }
    } catch {
        # A closed pipe mid-write means the child is gone. That is a
        # transport failure and the caller decides; it is never a surface.
    }

    if (-not $proc.WaitForExit($timeoutSeconds * 1000)) {
        $timedOut = $true
        try { $proc.Kill() } catch { }
        try { $proc.WaitForExit(5000) | Out-Null } catch { }
    }

    $out = ""
    $err = ""
    try { $out = $outTask.Result } catch { }
    try { $err = $errTask.Result } catch { }

    return @{
        Started  = $true
        Output   = $out
        Error    = $err
        ExitCode = $(if ($timedOut) { -1 } else { $proc.ExitCode })
        TimedOut = $timedOut
    }
}

# --- parsing -----------------------------------------------------------

function Get-LastStatusResponse($text) {
    <#
      Return the LAST mcpServerStatus/list response in the stream, or a
      fault describing why there is none.

      The last one is the latest poll, so it is the most-connected view
      the server offered. Taking the first would systematically read the
      surface while servers were still connecting - the very shape that
      makes an unmade measurement look like a clean one.
    #>
    $found = $null
    $sawError = $null
    $sawUnreadable = $false
    $sawAny = $false
    foreach ($line in ($text -split "`n")) {
        $t = $line.Trim()
        if (-not $t) { continue }
        if (-not $t.StartsWith("{")) { continue }
        $sawAny = $true
        $obj = $null
        try {
            $obj = $t | ConvertFrom-Json
        } catch {
            # A truncated or malformed frame is not a frame we may skip:
            # skipping it silently is how a parser reports a partial
            # stream as a whole one.
            $sawUnreadable = $true
            continue
        }
        if ($null -eq $obj.id) { continue }
        if ([int]$obj.id -lt 100) { continue }
        if ($obj.PSObject.Properties.Name -contains "error" -and $obj.error) {
            $sawError = $obj.error
            continue
        }
        if ($obj.PSObject.Properties.Name -contains "result") {
            $found = $obj.result
        }
    }
    return @{
        Result     = $found
        RpcError   = $sawError
        Unreadable = $sawUnreadable
        SawAny     = $sawAny
    }
}

function Get-Surface($result) {
    <#
      Reduce a status response to servers, each with whether it reported a
      serverInfo and the NAMES of its tools.

      `HasInfo` is the only field that separates a running server from one
      that is not running. It does NOT separate disabled from crashed;
      nothing in this record does.
    #>
    $servers = @()
    $data = $null
    if ($result -and ($result.PSObject.Properties.Name -contains "data")) {
        $data = $result.data
    }
    foreach ($s in @($data)) {
        if ($null -eq $s) { continue }
        $tools = @()
        if ($s.PSObject.Properties.Name -contains "tools" -and $s.tools) {
            # The Where-Object is load-bearing, not defensive tidying.
            # `tools: {}` parses to an object with no properties, whose
            # `.Name` is $null, and `@($null)` in PowerShell is a
            # ONE-ELEMENT array holding $null - so an empty tools map
            # became a single nameless tool and blocked every clean run
            # against a silent server. Caught by
            # test_a_clean_report_distinguishes_silent_from_absent.
            $tools = @($s.tools.PSObject.Properties.Name |
                       Where-Object { $_ })
        }
        $servers += ,@{
            Name    = [string]$s.name
            HasInfo = ($null -ne $s.serverInfo)
            Tools   = $tools
        }
    }
    return $servers
}

function Test-Transport($pass, $label, $asJson) {
    if (-not $pass.Started) {
        Write-Blocked ($label + ": the app server could not be started (" +
            $pass.Reason + ") - nothing is known about the tool surface") $asJson
    }
    if ($pass.TimedOut) {
        Write-Blocked ($label + ": the app server did not exit within the" +
            " timeout, so the probe timed out and the surface was never read") $asJson
    }
    if ($pass.ExitCode -ne 0) {
        Write-Blocked ($label + ": the app server exited " + $pass.ExitCode +
            " - the probe could not be taken, so nothing is known about the" +
            " tool surface") $asJson
    }
    $parsed = Get-LastStatusResponse $pass.Output
    if ($parsed.RpcError) {
        Write-Blocked ($label + ": the app server answered" +
            " mcpServerStatus/list with an RPC error (" +
            [string]$parsed.RpcError.message + "), so no surface was reported") $asJson
    }
    if ($null -eq $parsed.Result) {
        if ($parsed.Unreadable) {
            Write-Blocked ($label + ": the app server's output could not be" +
                " read as JSON, and an unreadable stream is not an empty" +
                " tool surface") $asJson
        }
        if (-not $parsed.SawAny) {
            Write-Blocked ($label + ": the app server wrote no frames at" +
                " all, which is an unmade measurement, not an empty tool" +
                " surface") $asJson
        }
        Write-Blocked ($label + ": the app server never answered" +
            " mcpServerStatus/list, so the surface was never reported") $asJson
    }
    if ($parsed.Unreadable) {
        Write-Blocked ($label + ": part of the app server's output could not" +
            " be read as JSON, so the surface read from the rest is a" +
            " partial stream reported as a whole one") $asJson
    }
    return Get-Surface $parsed.Result
}

# --- main --------------------------------------------------------------

if ($WorkDir) {
    if (-not (Test-Path -LiteralPath $WorkDir)) {
        Write-Output "ERROR: $WorkDir does not exist"
        exit 2
    }
    $WorkDir = (Resolve-Path -LiteralPath $WorkDir).Path
}

# Pass 1: BASELINE. No isolation flags. This is the calibration.
$pass1 = Invoke-AppServer $CodexCommand @() $WorkDir $TimeoutSeconds `
                          $PollIntervalMs $PollCount
$surface1 = Test-Transport $pass1 "pass 1 (baseline)" $Json

$running1 = @($surface1 | Where-Object { $_.HasInfo })
$tools1 = @($surface1 | ForEach-Object { $_.Tools } | Where-Object { $_ })
if ($running1.Count -eq 0 -or $tools1.Count -eq 0) {
    Write-Blocked ("pass 1 (baseline) saw no running MCP server with any" +
        " tool, so the instrument is not calibrated: this probe is not" +
        " known to be able to see a tool at all, and a clean pass 2 from" +
        " an uncalibrated instrument is an unmade measurement") $Json
}

# Pass 2: DISPATCH. The exact flags the review dispatch carries.
#
# `-c mcp_servers.node_repl.enabled=false` is shape A, settled in the
# 0.24.0 plan debate. `-c mcp_servers={}` was MEASURED to be inert - it
# parses, exits 0 and changes nothing - and must never appear here in its
# place.
$dispatchArgs = @(
    "--disable", "plugins",
    "--disable", "apps",
    "-c", "mcp_servers.node_repl.enabled=false"
)
$pass2 = Invoke-AppServer $CodexCommand $dispatchArgs $WorkDir $TimeoutSeconds `
                          $PollIntervalMs $PollCount
$surface2 = Test-Transport $pass2 "pass 2 (dispatch)" $Json

$unexpected = @()
foreach ($s in $surface2) {
    foreach ($t in $s.Tools) {
        if ($AllowTool -notcontains $t) { $unexpected += ($s.Name + "/" + $t) }
    }
}
if ($unexpected.Count -gt 0) {
    Write-Blocked ("pass 2 (dispatch) reported " + $unexpected.Count +
        " tool(s) the allowlist does not name: " + ($unexpected -join ", ") +
        " - the reviewer would hold these") $Json
}

# Clean. The wording below is a contract: a debate record quotes it, and
# it must not let an absence read as a removal.
$silent = @($surface2 | Where-Object { -not $_.HasInfo } |
            ForEach-Object { $_.Name })
$note = "no tool outside the allowlist was reported in the dispatch" +
        " configuration. This is a MITIGATION, not proof of removal: a" +
        " server that was disabled and a server that failed to launch are" +
        " indistinguishable in this record."
if ($silent.Count -gt 0) {
    $note += " Server(s) present but SILENT (no serverInfo, no tools): " +
             ($silent -join ", ") + "."
}
Write-Result "clean" $null ([ordered]@{
    baseline_servers = @($surface1 | ForEach-Object { $_.Name })
    baseline_tools   = $tools1.Count
    dispatch_tools   = 0
    silent_servers   = $silent
    allowlist        = $AllowTool
    note             = $note
}) $Json
