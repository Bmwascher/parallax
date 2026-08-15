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
        # PERCENT IS NOT QUOTABLE, so a line carrying one is REFUSED rather
        # than launched. cmd expands `%NAME%` while parsing, and it does so
        # INSIDE double quotes as well, so the quoting below cannot make it
        # literal and neither `/s` nor `^` reliably suppresses it on a
        # command line - `%%` only escapes inside a batch FILE. A legal
        # Windows path may contain `%`. Launching it anyway would run a
        # DIFFERENT path from the one resolved, and the probe would report
        # whatever that produced as a measurement of the real client.
        # Blocking is the only honest direction: an instrument that cannot
        # be aimed has measured nothing. Found by the diff debate at round
        # 2, which also found the claim below overstated.
        $cmdLine = (& $quote $batchPath) + ' ' + $tail
        if ($cmdLine.Contains('%')) {
            return @{ Started = $false
                      Reason = ("the batch launcher's command line contains a" +
                                " percent sign, which cmd.exe expands even" +
                                " inside quotes, so the line cannot be passed" +
                                " through literally: " + $cmdLine) }
        }
        # `/s /c "<whole command line>"`, and the shape is the fix rather
        # than decoration. Under a bare `/c`, cmd applies a rule that
        # depends on how many quotes the line has and what sits between
        # them, so `cmd /c "C:\a & b\x.cmd" app-server --stdio` gets taken
        # apart and the `&` runs as a command separator. With `/s`, cmd
        # strips exactly the first and last quote of the remainder and runs
        # what is left without re-applying that rule, which is the one
        # predictable form. It is NOT verbatim - percent expansion still
        # happens, which is why the refusal above sits in front of it.
        # Found by the diff debate at round 1; quoting the path alone was
        # measured and was NOT enough.
        $psi.Arguments = '/s /c "' + $cmdLine + '"'
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
        # TWO id ranges, DERIVED from $pollCount so they cannot collide at
        # any value of it. The first version hardcoded 100+n and 200+n and
        # read them back as the fixed windows 100-199 and 200-299, while
        # -PollCount took any integer: at 101 polls the 101st status id is
        # 201, which lands inside the FEATURE window, and a status answer
        # would be read as the feature surface. Nothing capped it. Found by
        # the diff debate at round 2. A cap would have worked; deriving the
        # bases needs no cap and cannot drift out of step with the reader,
        # because the reader is handed these same numbers below.
        $statusBase  = 100
        $featureBase = $statusBase + $pollCount + 1
        for ($n = 1; $n -le $pollCount; $n++) {
            if ($proc.HasExited) { break }
            Start-Sleep -Milliseconds $pollIntervalMs
            #
            # `experimentalFeature/list` was in the frozen plan's task 1 from
            # the start and the first shipped probe simply never sent it -
            # spec drift, found by the diff debate at round 1, not by any
            # test here. It matters beyond fidelity: backlog item 7's problem
            # statement names the memories feature alongside MCP tools, so a
            # probe that reads only tools closes half an item and reports the
            # other half as nothing at all.
            $proc.StandardInput.WriteLine(
                '{"id":' + ($statusBase + $n) + ',"method":"mcpServerStatus/list","params":{}}')
            $proc.StandardInput.WriteLine(
                '{"id":' + ($featureBase + $n) + ',"method":"experimentalFeature/list","params":{}}')
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
        # The reader is TOLD the windows this call actually used, rather
        # than repeating the constants and hoping the two stay in step.
        StatusMin  = ($statusBase + 1)
        StatusMax  = ($statusBase + $pollCount)
        FeatureMin = ($featureBase + 1)
        FeatureMax = ($featureBase + $pollCount)
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
    # TWO flags, not one. They were collapsed, so a present-but-null `data`
    # blocked with the reason "carrying no data member" - which is not what
    # happened, and a test had been written to REQUIRE that inaccurate
    # sentence. A blocked reason is read by a person deciding what broke;
    # one that describes the wrong fault sends them to the wrong place.
    # Found by the diff debate at round 3.
    $sawResultNoDataMember = $false
    $sawResultNullData = $false
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
                $sawResultNoDataMember = $true
                continue
            }
            if ($null -eq $obj.result.data) {
                # `data: null` is the THIRD reading of this rule, and the
                # first two were both false-cleans. Member PRESENCE alone
                # let `{"data":null}` through, and the reducers then walked
                # `@($null)` - a ONE-ELEMENT array holding $null, the same
                # PowerShell trap this file already documents for `tools:
                # {}` - whose single element they skip, producing an empty
                # surface and a clean report. A null surface is not a
                # surface of nothing. Found by the diff debate at round 2.
                $sawResultNullData = $true
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
        ResultNoDataMember = $sawResultNoDataMember
        ResultNullData     = $sawResultNullData
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
    $status = Read-Surface $pass $label "mcpServerStatus/list" `
                  $pass.StatusMin $pass.StatusMax $asJson
    $features = Read-Surface $pass $label "experimentalFeature/list" `
                  $pass.FeatureMin $pass.FeatureMax $asJson
    return @{
        Servers  = (Get-Surface $status)
        Features = (Get-Features $features $label $asJson)
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
        if ($parsed.ResultNoDataMember) {
            Write-Blocked ($label + ": the app server answered " + $method +
                " with a result carrying no data member, and a response that" +
                " carries no surface is not a surface of nothing") $asJson
        }
        if ($parsed.ResultNullData) {
            Write-Blocked ($label + ": the app server answered " + $method +
                " with a result whose data value is null, and a null surface" +
                " is not a surface of nothing") $asJson
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
    if ($parsed.ResultNoDataMember) {
        Write-Blocked ($label + ": one " + $method + " result carried no data" +
            " member, so part of what was reported cannot be read as a" +
            " surface") $asJson
    }
    if ($parsed.ResultNullData) {
        Write-Blocked ($label + ": one " + $method + " result carried a null" +
            " data value, so part of what was reported cannot be read as a" +
            " surface") $asJson
    }
    return $parsed.Result
}

function Get-Features($result, $label, $asJson) {
    <#
      Reduce the feature response to NAME plus resolved enablement.

      Mostly VISIBILITY, with one exception that the caller applies. The
      frozen plan's DQ1 settled that this list ANSWERING proves only that
      the app server is alive - that is about the list as a SURVIVOR
      control, and it is still true. It does not settle what a feature the
      dispatch claims to have DISABLED may report: one that comes back
      enabled says the flag did not take effect, which is a present,
      observed fact rather than an inference from absence. The caller
      blocks on exactly those, and on nothing else.

      An earlier version of this comment cited DQ1 for the wider claim that
      nothing here decides a verdict. That was the comment doing the work
      the plan had not done. Diff debate, round 2.
    #>
    # `data` MUST BE AN ARRAY, checked rather than coerced. `@(...)` wraps a
    # single object into a one-element list, so a server answering with one
    # bare object where a list belongs was accepted and could reach CLEAN.
    # Round 3's accepted fix asked for `data` to be validated as the
    # expected collection and this coercion was left in place. Found by the
    # diff debate at round 4.
    if ($result.data -isnot [System.Array]) {
        Write-Blocked ($label + ": the feature surface's data is not a list (" +
            $result.data.GetType().Name + "), so what it reports cannot be" +
            " read as a set of features") $asJson
    }
    $features = @()
    $index = -1
    foreach ($f in $result.data) {
        $index++
        # EVERY ENTRY IS VALIDATED, not just the ones the policy names.
        # Round 2's accepted fix asked for readable feature-entry schema and
        # this function was left accepting anything: a null element was
        # skipped, any name was cast to a string, and any enablement value
        # was taken. Only the disabled names were checked downstream, so a
        # malformed entry anywhere ELSE in the list still reached the clean
        # report - the same half-built-fix shape as the policy itself. Found
        # by the diff debate at round 3.
        #
        # This is deliberately strict, and the direction is safe: every one
        # of the 92 features in the live 2026-08-14 reading carries a
        # non-empty string name and a real boolean. A future feature that
        # does not will BLOCK loudly rather than be silently reduced.
        if ($null -eq $f) {
            Write-Blocked ($label + ": the feature surface carried a null" +
                " entry at position " + $index + ", and a list with an" +
                " unreadable entry is not a readable surface") $asJson
        }
        $name = $null
        if ($f.PSObject.Properties.Name -contains "name") { $name = $f.name }
        if ($name -isnot [string] -or -not $name.Trim()) {
            Write-Blocked ($label + ": the feature surface entry at position " +
                $index + " has no usable name (" +
                $(if ($null -eq $name) { "no name member" }
                  else { $name.GetType().Name }) +
                "), so what it describes cannot be read") $asJson
        }
        # EXACTLY ONE enablement member, not the first one found. The loop
        # took the first of `enabled`, `isEnabled`, `value` and ignored the
        # rest, so an entry carrying `enabled:false` AND `value:true` was
        # certified as disabled while the surface said two different things
        # about it. Round 3's accepted fix asked for an UNAMBIGUOUS boolean
        # enablement field and this took the first match instead. Found by
        # the diff debate at round 4.
        $present = @(@("enabled", "isEnabled", "value") |
                     Where-Object { $f.PSObject.Properties.Name -contains $_ })
        if ($present.Count -gt 1) {
            Write-Blocked ($label + ": the feature '" + $name + "' carries " +
                $present.Count + " enablement members (" +
                ($present -join ", ") + "), so its resolved enablement is" +
                " ambiguous and cannot be read") $asJson
        }
        $enabled = $null
        $sawMember = $false
        if ($present.Count -eq 1) {
            $enabled = $f.($present[0]); $sawMember = $true
        }
        if (-not $sawMember) {
            Write-Blocked ($label + ": the feature '" + $name + "' carries no" +
                " enabled/isEnabled/value member, so its resolved enablement" +
                " was never reported") $asJson
        }
        if ($enabled -isnot [bool]) {
            Write-Blocked ($label + ": the feature '" + $name + "' reports a" +
                " non-boolean enablement (" +
                $(if ($null -eq $enabled) { "null" } else { $enabled.GetType().Name }) +
                "), and an unreadable value is not a disabled one") $asJson
        }
        $features += ,@{ Name = $name; Enabled = $enabled }
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

# THE DISPATCH FEATURE POLICY. Every feature this pass explicitly DISABLED
# must come back reported and false, or the probe blocks.
#
# Round 1 of the diff debate accepted a fix that asked for an
# enabled-feature policy and a fail-first case for an unexpectedly enabled
# feature. Only the reading half was built, and a comment justified the
# omission by pointing at plan DQ1 - which settles that this list is no
# SURVIVOR control, and settles nothing about a feature the dispatch
# claims to have turned off. Worse, the module's own fixture fed
# `memories=True` into pass 2 and asserted a CLEAN verdict, so a test
# certified the exact state that should stop a round. Found by the diff
# debate at round 2.
#
# This direction is sound where absence is not: `memories=True` here is
# something PRESENT and observed, so it needs no ability to tell a disabled
# server from a crashed one. It says the flag did not take effect, and a
# reviewer holding a cross-session store is the thing item 7 exists to
# stop.
#
# The list is DERIVED from the flags above rather than typed out again, so
# a `--disable` added later is policed without anyone remembering to.
$requiredFalse = @()
for ($i = 0; $i -lt $dispatchArgs.Count - 1; $i++) {
    if ($dispatchArgs[$i] -eq "--disable") { $requiredFalse += $dispatchArgs[$i + 1] }
}
foreach ($name in $requiredFalse) {
    # `-ceq`, CASE-SENSITIVE, and the case matters more than it looks.
    # PowerShell's `-eq` is case-INSENSITIVE, so `Memories=False` satisfied
    # a requirement derived from `--disable memories`. Round 2 declared the
    # limit that a flag name not matching a feature name must fail as
    # "never reported"; `-eq` quietly made one class of mismatch match
    # instead, so the code did not do what its own declared limit said.
    # Found by the diff debate at round 3. The live reading records these
    # names in lower case, so this compares what was measured.
    $hits = @($read2.Features | Where-Object { $_.Name -ceq $name })
    if ($hits.Count -eq 0) {
        Write-Blocked ("pass 2 (dispatch) disabled '" + $name + "' but the" +
            " feature surface never reported it, so whether the flag took" +
            " effect is UNMEASURED") $Json
    }
    if ($hits.Count -gt 1) {
        Write-Blocked ("pass 2 (dispatch) reported the feature '" + $name +
            "' " + $hits.Count + " times, so which one describes the" +
            " reviewer cannot be read") $Json
    }
    $value = $hits[0].Enabled
    if ($value -isnot [bool]) {
        Write-Blocked ("pass 2 (dispatch) reported feature '" + $name +
            "' with a non-boolean enablement (" +
            $(if ($null -eq $value) { "no enabled/isEnabled/value member" }
              else { $value.GetType().Name + " '" + [string]$value + "'" }) +
            "), and an unreadable value is not a disabled one") $Json
    }
    if ($value) {
        Write-Blocked ("pass 2 (dispatch) passed '--disable " + $name +
            "' and the feature surface still reports " + $name +
            "=True, so the flag did NOT take effect and the reviewer would" +
            " hold it") $Json
    }
}

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
# The FEATURE half of the record. It decides EXACTLY ONE thing, and the
# note has to be precise about which, because a debate record quotes it.
#
# Policed: every feature the dispatch explicitly disabled, checked above -
# reaching this line means each came back reported and false. Not policed:
# everything else, because no allowlist of acceptable features exists and
# inventing one here would be a judgment nothing measured supports. A
# feature enabled in pass 2 that this probe did not disable has been SEEN,
# not accepted, and what to do about it is a decision for a person.
$featureNote = "feature enablement is REPORTED. The only features this" +
               " probe judges are the ones the dispatch explicitly" +
               " disabled (" + ($requiredFalse -join ", ") + "), each of" +
               " which was reported and false or this run would have" +
               " blocked. Every OTHER feature listed here is seen rather" +
               " than accepted: no allowlist of acceptable features exists," +
               " so nothing else here blocks."
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
