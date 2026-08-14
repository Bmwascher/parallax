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
# AND IT READS A DIFFERENT SUBCOMMAND FROM THE ONE THE REVIEWER RUNS. This
# script reads `codex app-server`; the review dispatches `codex exec`, and
# for everything measured so far the two resolve their MCP servers
# independently. `codex exec` was measured only to ACCEPT the same flags,
# never probed for its own tool surface. A clean pass 2 is therefore a
# PROXY for the reviewer's surface, not a direct reading of it. Probing the
# exec surface is backlog item 39.
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
    $batchPath = $null
    foreach ($ext in @('\.exe$', '\.(cmd|bat)$', '\.ps1$')) {
        $hit = @($candidates | Where-Object { $_ -match $ext }) | Select-Object -First 1
        if (-not $hit) { continue }
        if ($ext -eq '\.exe$') {
            $file = $hit
        } elseif ($ext -eq '\.(cmd|bat)$') {
            # cmd.exe is the only thing that can run a batch file, and
            # Process.Start will not do it for us. The command line is built
            # separately below, because cmd's own quoting rules are not the
            # ones every other program uses.
            $file = "$env:SystemRoot\System32\cmd.exe"
            $batchPath = $hit
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

    # The argument STRING, not ArgumentList: Windows PowerShell 5.1's
    # ProcessStartInfo has no ArgumentList property at all, and reaching for
    # it there throws on a null.
    #
    # Quoting is on whitespace OR any cmd.exe metacharacter, because the
    # batch branch below hands its line to a shell that RE-PARSES it. A
    # Windows path cannot contain a double quote, so quoting is always safe.
    $quote = {
        param($tok)
        if ($tok -match '[\s&|<>^()]') { '"' + $tok + '"' } else { $tok }
    }
    $tail = ($argList | ForEach-Object { & $quote $_ }) -join " "

    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = $file
    if ($batchPath) {
        # `/s /c "<whole command line>"`, and the shape is the fix rather
        # than decoration. Under a bare `/c`, cmd applies a rule that
        # depends on how many quotes the line has and what sits between
        # them, so `cmd /c "C:\a & b\x.cmd" app-server --stdio` gets taken
        # apart and the `&` runs as a command separator. With `/s`, cmd
        # strips exactly the first and last quote of the remainder and
        # executes what is left verbatim, which is the one predictable
        # form. Found by the diff debate at round 1; quoting the path alone
        # was measured and was NOT enough.
        $psi.Arguments = '/s /c "' + (& $quote $batchPath) + ' ' + $tail + '"'
    } else {
        $psi.Arguments = $tail
    }
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
    $preamble = $null
    $preambleRead = $false
    try {
        $preamble = $proc.StandardInput.Encoding.GetPreamble()
        $preambleRead = $true
    } catch { }
    if (-not $preambleRead) {
        # The check itself could not be made. Swallowing that left the
        # probe proceeding as though the pipe were verified, which is this
        # script's own forbidden shape wearing the clothes of a guard.
        # Fable whole-branch review, minor 3.
        try { $proc.Kill() } catch { }
        return @{ Started = $false
                  Reason = ("the stdin encoding could not be read, so it is" +
                            " not known whether the first JSON-RPC frame" +
                            " would reach the app server intact") }
    }
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
            # TWO methods per poll, on two id ranges: 100+ for the server and
            # tool surface, 200+ for the resolved FEATURE surface.
            #
            # `experimentalFeature/list` was in the frozen plan's task 1 from
            # the start and the first shipped probe simply never sent it -
            # spec drift, found by the diff debate at round 1, not by any
            # test here. It matters beyond fidelity: backlog item 7's problem
            # statement names the memories feature alongside MCP tools, so a
            # probe that reads only tools closes half an item and reports the
            # other half as nothing at all.
            $proc.StandardInput.WriteLine(
                '{"id":' + (100 + $n) + ',"method":"mcpServerStatus/list","params":{}}')
            $proc.StandardInput.WriteLine(
                '{"id":' + (200 + $n) + ',"method":"experimentalFeature/list","params":{}}')
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

function Get-LastResponse($text, $minId, $maxId) {
    <#
      Return the LAST response in the stream whose id falls in [minId,
      maxId], or a fault describing why there is none.

      The last one is the latest poll, so it is the most-connected view
      the server offered. Taking the first would systematically read the
      surface while servers were still connecting - the very shape that
      makes an unmade measurement look like a clean one.

      TWO RULES HERE WERE WRONG IN THE FIRST VERSION and both were
      false-cleans found by the diff debate at round 1:

      1. A non-blank line that is not a JSON object used to be SKIPPED.
         So `garbage` followed by a valid response read as clean, and
         garbage alone blocked with the untrue reason "wrote no frames at
         all". Every non-blank line on this stream is supposed to be a
         JSON-RPC frame; one that is not is a protocol failure, and
         skipping it is how a parser reports a partial stream as a whole
         one.
      2. A result with NO `data` member used to be accepted, and
         `Get-Surface` then turned it into an empty surface, so
         `{"id":101,"result":{}}` reached the clean report. A response
         that carries no surface is not a surface of nothing.
    #>
    $found = $null
    $sawError = $null
    $sawUnreadable = $false
    $sawAnyOutput = $false
    $sawResultWithoutData = $false
    foreach ($line in ($text -split "`n")) {
        $t = $line.Trim()
        if (-not $t) { continue }
        $sawAnyOutput = $true
        if (-not $t.StartsWith("{")) {
            $sawUnreadable = $true
            continue
        }
        $obj = $null
        try {
            $obj = $t | ConvertFrom-Json
        } catch {
            $sawUnreadable = $true
            continue
        }
        if ($null -eq $obj.id) { continue }
        $id = 0
        try { $id = [int]$obj.id } catch { $sawUnreadable = $true; continue }
        if ($id -lt $minId -or $id -gt $maxId) { continue }
        if ($obj.PSObject.Properties.Name -contains "error" -and $obj.error) {
            $sawError = $obj.error
            continue
        }
        if ($obj.PSObject.Properties.Name -contains "result") {
            if ($null -eq $obj.result -or
                -not ($obj.result.PSObject.Properties.Name -contains "data")) {
                $sawResultWithoutData = $true
                continue
            }
            $found = $obj.result
        }
    }
    return @{
        Result       = $found
        RpcError     = $sawError
        Unreadable   = $sawUnreadable
        SawAnyOutput = $sawAnyOutput
        ResultNoData = $sawResultWithoutData
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
    # Both surfaces are read, and each one's failure directions block on
    # their own terms. The FEATURE surface is read because the frozen plan
    # asked for it and because backlog item 7 names the memories feature
    # beside the MCP tools; a probe that reads only tools answers half of
    # that item and says nothing about the other half.
    $status = Read-Surface $pass $label "mcpServerStatus/list" 100 199 $asJson
    $features = Read-Surface $pass $label "experimentalFeature/list" 200 299 $asJson
    return @{
        Servers  = (Get-Surface $status)
        Features = (Get-Features $features)
    }
}

function Read-Surface($pass, $label, $method, $minId, $maxId, $asJson) {
    $parsed = Get-LastResponse $pass.Output $minId $maxId
    if ($parsed.RpcError) {
        Write-Blocked ($label + ": the app server answered " + $method +
            " with an RPC error (" + [string]$parsed.RpcError.message +
            "), so no surface was reported") $asJson
    }
    if ($null -eq $parsed.Result) {
        if ($parsed.ResultNoData) {
            Write-Blocked ($label + ": the app server answered " + $method +
                " with a result carrying no data member, and a response that" +
                " carries no surface is not a surface of nothing") $asJson
        }
        if ($parsed.Unreadable) {
            Write-Blocked ($label + ": the app server wrote output that is not" +
                " a readable JSON-RPC frame, and an unreadable stream is not" +
                " an empty surface") $asJson
        }
        if (-not $parsed.SawAnyOutput) {
            Write-Blocked ($label + ": the app server wrote nothing at all," +
                " which is an unmade measurement, not an empty surface") $asJson
        }
        Write-Blocked ($label + ": the app server never answered " + $method +
            ", so that surface was never reported") $asJson
    }
    if ($parsed.Unreadable) {
        Write-Blocked ($label + ": part of the app server's output is not a" +
            " readable JSON-RPC frame, so the surface read from the rest is a" +
            " partial stream reported as a whole one") $asJson
    }
    if ($parsed.ResultNoData) {
        Write-Blocked ($label + ": one " + $method + " result carried no data" +
            " member, so part of what was reported cannot be read as a" +
            " surface") $asJson
    }
    return $parsed.Result
}

function Get-Features($result) {
    <#
      Reduce the feature response to NAME plus resolved enablement.

      This is VISIBILITY, not a control. The frozen plan's DQ1 settled that
      this list answering proves only that the app server is alive, and it
      defines no allowlist of acceptable features, so nothing here decides a
      verdict. What it does is put the reviewer's resolved features - the
      memories feature among them - into a record that a debate can read,
      which is the half of backlog item 7 the tool list cannot answer.
    #>
    $features = @()
    foreach ($f in @($result.data)) {
        if ($null -eq $f) { continue }
        $enabled = $null
        foreach ($k in @("enabled", "isEnabled", "value")) {
            if ($f.PSObject.Properties.Name -contains $k) { $enabled = $f.$k; break }
        }
        $features += ,@{ Name = [string]$f.name; Enabled = $enabled }
    }
    return $features
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
$read1 = Test-Transport $pass1 "pass 1 (baseline)" $Json
$surface1 = $read1.Servers

# ONE server that is BOTH running and carrying a tool, as one fact about
# one server. Counting running servers and tools separately let a
# tool-less running server and a silent server that reported tools
# calibrate the instrument between them: two half-measurements reported as
# one whole one. No measured record has that shape, which is exactly why
# the code must not depend on that staying true. Fable review, minor 4.
$calibrated = @($surface1 | Where-Object { $_.HasInfo -and $_.Tools.Count -gt 0 })
$tools1 = @($surface1 | ForEach-Object { $_.Tools } | Where-Object { $_ })
if ($calibrated.Count -eq 0) {
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
# `--disable memories` is here because the review dispatch carries it, and
# this pass is worth nothing if it models a configuration the reviewer
# never receives. Measured 2026-08-12 on the live client, BEFORE the flag
# was added: the review configuration reported `memories=True`, so the
# auditor held a cross-session store while plugins and apps were correctly
# off. Continuity within a review comes from resuming the same session,
# which the debate protocol already does for every round after the first.
$dispatchArgs = @(
    "--disable", "plugins",
    "--disable", "apps",
    "--disable", "memories",
    "-c", "mcp_servers.node_repl.enabled=false"
)
$pass2 = Invoke-AppServer $CodexCommand $dispatchArgs $WorkDir $TimeoutSeconds `
                          $PollIntervalMs $PollCount
$read2 = Test-Transport $pass2 "pass 2 (dispatch)" $Json
$surface2 = $read2.Servers

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
# The FEATURE half of the record, and it decides nothing. There is no
# declared allowlist of acceptable features, so no feature here can block;
# what this does is make the reviewer's resolved features readable, which
# is the half of backlog item 7 the tool list cannot answer. A feature
# enabled in pass 2 that a debate cares about is a decision for a person,
# and the note says so rather than implying the probe made it.
$featureNote = "feature enablement is REPORTED, never judged: this probe" +
               " carries no allowlist of acceptable features, so nothing" +
               " here blocks and a feature reported enabled in the dispatch" +
               " configuration has been seen rather than accepted."
Write-Result "clean" $null ([ordered]@{
    baseline_servers  = @($surface1 | ForEach-Object { $_.Name })
    baseline_tools    = $tools1.Count
    baseline_features = @($read1.Features | ForEach-Object {
                            $_.Name + "=" + [string]$_.Enabled })
    dispatch_features = @($read2.Features | ForEach-Object {
                            $_.Name + "=" + [string]$_.Enabled })
    feature_note      = $featureNote
    # MEASURED, not assumed. This was the constant 0, which is exact only
    # while the allowlist is empty: a caller who widens it gets a reviewer
    # holding the allowed tools and a record saying zero. Every tool
    # counted here is one the allowlist named, since anything else blocked
    # above. Fable review, minor 5.
    dispatch_tools   = @($surface2 | ForEach-Object { $_.Tools } |
                         Where-Object { $_ }).Count
    silent_servers   = $silent
    allowlist        = $AllowTool
    note             = $note
}) $Json
