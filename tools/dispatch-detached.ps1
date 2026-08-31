# dispatch-detached.ps1 - prepare a dispatch directory and receipt for a
# PowerShell wrapper body, then poll its completion. The tool no longer
# starts the wrapper itself: the caller runs it as a tracked background
# command (see the skill), which the harness already reports on by name,
# with no 600-second tool-call ceiling. See
# docs/superpowers/specs/2026-08-31-tracked-background-dispatch-design.md
# for why -Launch became -Prepare.
#
# TWO MODES. Every later task depends on these exact names.
#
#   Prepare: -DispatchDir <path> -WrapperBody <path> -ReceiptPath <path>
#            -Round <label> -WorkingDirectory <path> [-Json]
#   Poll:    -Receipt <path> -ExpectedDispatchDir <path> -ExpectedRound <label>
#            [-Json]
#
# -Poll NAMES A RECEIPT, NEVER A DIRECTORY. A caller that could poll a bare
# directory could read a launch token straight out of the directory it is
# already looking at and hand it back to itself, which proves nothing. The
# receipt is written OUTSIDE the dispatch directory, at a path -Prepare
# refuses if it already exists, LAST of all and only on success.
#
# -Prepare ENFORCES the separation rather than describing it: it resolves
# both paths and BLOCKS, before anything is created, if the receipt path
# is equal to, or inside, the dispatch directory. A refused prepare writes
# no receipt, so there is nothing for a caller to substitute from the
# directory it was refused.
#
# THE RECEIPT is a JSON object holding exactly four fields, all present
# and non-null: dispatchDir (non-empty string), token (non-empty string),
# round (non-empty string), startTicks (a value that parses as a 64-bit
# integer). Any deviation - wrong top-level type, a missing field, an
# empty string field, an unparseable startTicks, a wrong JSON type on any
# field, or an unknown extra field - is the SAME "no-receipt" outcome:
# these are folded deliberately because their disposition is identical and
# no branch follows any of them differently. It is a decision, not an
# omission. startTicks in the RECEIPT no longer describes a real process -
# -Prepare starts none - and is not what -Poll's liveness check compares
# against; see the pid/startticks-file note at step 7 below.
#
# THE TOKEN IS NOT A SECRET. [System.Guid]::NewGuid() mints it, it also
# sits in plain sight inside launch.committed, and a caller determined to
# launder an old directory could read it there. What the receipt actually
# adds is that a REFUSED prepare produces no receipt at all - there is
# nothing to read back.
#
# -Poll is told, INDEPENDENTLY of the receipt, which directory and which
# round it is polling for (-ExpectedDispatchDir / -ExpectedRound), and
# compares BOTH before it opens anything else. A mismatch on either one is
# receipt-not-expected. The label alone would not be enough - a round
# label such as "Sol R1" is reusable across a retry of the same round -
# which is why the directory is checked too. The caller already has both
# values: it passed them to -Prepare.
#
# THE RESIDUAL, admitted rather than claimed closed: a caller that supplies
# an EARLIER attempt's receipt, AND that attempt's directory, AND its
# label, gets that attempt's result - because at that point every value
# the caller supplied genuinely describes the earlier act, and nothing
# inside this tool can distinguish that caller from one who is confused
# about all three at once. The controls are a fresh round-numbered receipt
# path per round and a -Prepare that refuses to overwrite an existing one.
# This is NARROWED, the same way the interrupted prepare that leaves no
# receipt at all is narrowed, not eliminated.
#
# -Poll computes exactly one of these THIRTEEN state names, in the fixed
# order below, and stops at the first that matches:
#   no-receipt, receipt-not-expected, launch-unknown, launch-not-ours,
#   not-started, pid-unreadable, running, no-exit-file, exit-unreadable,
#   exit-nonzero, no-reply, reply-empty, reply-present.
#
# -Poll's exit codes MAP onto those states and are part of the contract:
#   0  reply-present, and NOTHING ELSE.
#   3  running - meaning UNFINISHED, never treated as success. Revision 8
#      of the plan behind this tool gave "running" exit 0 with a comment
#      saying "exit 0 is not a result" beside it - a safety rule in prose
#      next to a command instead of a mechanism inside it. A caller
#      branching on exit status alone would take the success path while
#      the wrapper was still writing its reply. A distinct code makes the
#      unfinished round unrepresentable as success without reading
#      anything.
#   1  every other state, with the state name printed on stdout.
#   2  ONLY a failure to bind the parameters (an unknown mode, a missing
#      required value, both or neither of -Prepare/-Poll) or an internal
#      execution error. Reading the receipt's CONTENT is never exit 2: an
#      absent, unreadable, or schema-failing receipt is no-receipt at
#      exit 1. THE NARROWING, STATED PRECISELY: this promise covers only
#      the binding and internal errors THIS SCRIPT ITSELF can see. This
#      script carries no [CmdletBinding()], so an unrecognized switch is
#      NOT rejected by the PowerShell binder at all - measured, not the
#      assumption an earlier draft of this note made. PowerShell absorbs
#      the unknown token into $args silently and the script runs on to
#      its own mode-check, which finds neither -Prepare nor -Poll bound
#      and exits 2 exactly as a bare invocation would. Measured
#      2026-08-31 on `powershell -File tools/dispatch-detached.ps1
#      -Reciept x`: exit 2 on both Windows PowerShell 5.1 and
#      PowerShell 7 - never 0, because an unbound mode is already this
#      script's own exit-2 case, not because the host rejected anything.
#
# -Poll's own JSON (with -Json) echoes back the receipt's `round` label
# whenever a receipt was successfully read, whatever the state that
# follows - so a poll answering for a different round says so in the
# field the caller records. For no-receipt, nothing was read, so `round`
# is null.
#
# REPLY-PRESENT IS NOT A REVIEW RESULT ON ITS OWN. The caller still runs
# the lane's round-evidence binder, and only a clean binding makes it one.
# Do not read the state name as a verdict.
#
# -Prepare's exit codes match new-review-mirror.ps1:17-18: 0 prepared and
# committed, 1 blocked (reason on stdout), 2 script or environment error
# (including a failure to bind the parameters this script itself sees).
# -Poll extends that set with 3 and narrows 2 as described above.
#
# -Prepare, in order, under $ErrorActionPreference = 'Stop':
#   1. Resolve -WorkingDirectory to a full path and BLOCK, before anything
#      else is checked or created, if it does not exist or is not a
#      directory. -WORKINGDIRECTORY SURVIVED THE LAUNCHER'S DELETION: an
#      earlier draft of the design spec called it launcher-only, this
#      tool dropped it, and the FIRST round dispatched under that version
#      ran with the REAL REPOSITORY as its working directory, where a
#      root AGENTS.md sits on disk and the reviewer client auto-ingests
#      it as instructions - the instruction back-channel the preflight
#      exists to stop. The round was discarded UNREAD; its cost is
#      recorded in
#      docs/superpowers/specs/2026-08-31-tracked-background-dispatch-design.md
#      section 1. It is what puts the client inside the REVIEW MIRROR, so
#      it moved out of launcher plumbing, which nothing pinned, and into
#      wrapper text, which every per-site test pins (see the wrapper's
#      first-act Set-Location at step 4 below).
#   2. Resolve -ReceiptPath and -DispatchDir to full paths. BLOCK if the
#      receipt path is equal to, or inside, the dispatch directory, and
#      BLOCK if the receipt path already exists. Both checks run before
#      anything is created, so a refusal leaves no directory behind.
#   3. Reserve the dispatch directory with New-Item -ItemType Directory
#      and -ErrorAction Stop, and NO -Force: a taken directory must fail
#      loudly rather than silently proceed with an unreliable path.
#      Failure here is BLOCKED and nothing has started.
#   4. Copy -WrapperBody into the directory as wrapper.ps1; create an
#      empty stdin.empty beside it; write the resolved -WorkingDirectory
#      to a `cwd` file beside them, UTF-8 without a BOM, so it is present
#      before the receipt is published. NONE of the three is run -
#      -Prepare starts no process at all. The caller runs wrapper.ps1
#      itself, as a tracked background command named for its lane and
#      round; see the skill and the design spec named above. The
#      wrapper's own first act, right after publishing its pid and
#      startticks, reads this `cwd` file and Set-Location's to it -
#      that is what actually anchors the client to the review mirror.
#   5. If PARALLAX_DISPATCH_HOLD_BEFORE_PUBLISH is set (to a path), create
#      "<value>.started" once launch.committed (step 6) has been written,
#      then wait, bounded at sixty seconds, for "<value>.release" before
#      writing the receipt. On timeout, fail through the same catch as
#      any other failure. The deterministic barrier a
#      fail-closed-before-publication test needs; without it, that test
#      is the same millisecond race in a different costume. Unset, the
#      seam does not exist.
#   6. Mint the launch token and write launch.committed with it.
#   7. Write the RECEIPT last of all, and only now, with create-new
#      semantics (fails if the path was raced into existence since step
#      2's check). Its path was already checked for freshness and for
#      separation in step 2, so this can only fail on a race, and a race
#      here fails through the same catch as any other failure. The
#      receipt's startTicks field is a fixed placeholder (0): -Prepare
#      has no process to describe yet, and it is not what -Poll's
#      liveness check reads - see step 8 of the -Poll order below.
#   8. Steps 4 through 7 are wrapped in one catch that publishes no
#      receipt and exits 1 on any failure. The catch performs NO
#      filesystem cleanup: a directory left behind is inert and
#      inspectable, while a published receipt is not. That is
#      deliberate, not an oversight - a reserved-but-abandoned dispatch
#      directory is the expected shape of a handled failure, never
#      evidence of one. -Prepare starts no process, so unlike the
#      launcher this replaces, there is never a started tree to kill on
#      this path - see the design spec for the three findings that
#      closes by removing their subject rather than patching them.
#
# -Poll computes the state in this fixed order and stops at the first
# match, reading nothing further once it has:
#   1. Receipt absent, unreadable, or failing the schema -> no-receipt.
#      Nothing else is read, and no directory is opened.
#   2. Receipt's dispatchDir != -ExpectedDispatchDir (compared as full
#      resolved paths) OR round != -ExpectedRound (compared exactly) ->
#      receipt-not-expected. Still nothing is opened.
#   3. dispatchDir has no launch.committed -> launch-unknown.
#   4. launch.committed's content != the receipt's token -> launch-not-ours.
#   5. No `cwd` file -> not-started. A prepared round that cannot say
#      where it must run is not runnable, and must never be run from
#      wherever the caller happens to be - it must never fall back to the
#      caller's own directory. Folded into the same state as a missing
#      pid file, immediately below, because both mean the same thing to a
#      caller: neither is a result.
#   6. No pid file -> not-started. The prepared wrapper was never run, or
#      it died before it could publish its own identity - this state
#      deliberately does not distinguish the two, because both mean the
#      same thing to a caller: neither is a result. The brief window
#      where a live wrapper has not yet written its pid also lands here,
#      which is conservative in the correct direction: a live round reads
#      as not-started rather than as finished.
#   7. pid unreadable or not an integer -> pid-unreadable. Same for the
#      startticks FILE the wrapper writes beside it (missing, unreadable,
#      or not an integer): pid and startticks are a pair the wrapper
#      self-publishes as its first act (see the header of each wrapper
#      body), and either half failing to read is the same "cannot confirm
#      identity" outcome, folded together rather than adding a
#      fourteenth state.
#   8. Liveness, computed exactly the way tools/kimi-lane-lock.ps1:219-236
#      computes Get-Liveness, comparing the live process's own StartTime
#      against the startticks FILE (not the receipt's startTicks, which
#      -Prepare never populated with a real value): no such process ->
#      DEAD, continue; the process exists but its start time cannot be
#      read -> pid-unreadable, stop; the process exists and its ticks
#      differ from the startticks file's (the pid was recycled) -> DEAD,
#      continue; ticks match -> running, stop, and NOTHING ELSE IS READ -
#      a reply being written is not a reply.
#   9. No exit file -> no-exit-file. Unreadable or not a plain integer ->
#      exit-unreadable. Non-zero -> exit-nonzero.
#  10. Zero and no reply file -> no-reply. Zero and reply is empty ->
#      reply-empty. Zero and reply has content -> reply-present.
#
# ONE ENV-GATED TEST SEAM, BUILDER CONTRACT rather than test scaffolding,
# the same shape as the two seams in tools/new-kimi-lane-home.ps1: it is
# reachable by any parent process that sets the variable, no shipped
# caller sets it, and it can only make an invocation FAIL or answer MORE
# CONSERVATIVELY - never turn a failing prepare into a successful one.
#   PARALLAX_DISPATCH_HOLD_BEFORE_PUBLISH - see step 5 above.
#
# -Poll KEEPS its own env-gated seam from the same family, unaffected by
# this change:
#   PARALLAX_DISPATCH_POLL_STARTTIME_FAULT - forces the live-process
#     start-time read in step 8 above to throw AFTER the pid lookup has
#     already succeeded, so a test can reach pid-unreadable from a
#     genuinely alive pid without depending on another user's process.
#     Its only reachable effect is to turn what would have been "running"
#     into "pid-unreadable" - a failure classification, never a success
#     one. Unset, the seam does not exist. Same shape as
#     PARALLAX_LANE_LOCK_STARTTIME_FAULT in tools/kimi-lane-lock.ps1.
#
# ${CLAUDE_PLUGIN_ROOT} IN SKILL BODY TEXT: the Claude Code harness
# substitutes it with an absolute path before the model ever sees it -
# measured 2026-08-31 on Claude Code 2.1.251, recorded in
# docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/wrapper-probe.md.
# That measurement covers SKILL.md body text ONLY, never a references
# file read raw with the Read tool - this script has no opinion on either
# form and takes both -DispatchDir and -WrapperBody as plain arguments.
#
# Windows PowerShell 5.1 compatible, ASCII only.

param(
    [switch]$Prepare,
    [string]$DispatchDir,
    [string]$WrapperBody,
    [string]$ReceiptPath,
    [string]$Round,
    [string]$WorkingDirectory,

    [switch]$Poll,
    [string]$Receipt,
    [string]$ExpectedDispatchDir,
    [string]$ExpectedRound,

    [switch]$Json
)

$ErrorActionPreference = 'Stop'

function Resolve-UnresolvedPath([string]$Path) {
    return $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($Path)
}

function Test-PathsEqual([string]$A, [string]$B) {
    $na = (Resolve-UnresolvedPath $A).TrimEnd('\', '/')
    $nb = (Resolve-UnresolvedPath $B).TrimEnd('\', '/')
    return [string]::Equals($na, $nb, [System.StringComparison]::OrdinalIgnoreCase)
}

# ---------------------------------------------------------------------
# Receipt schema. See the header for the exact rule: a valid receipt is a
# JSON object holding exactly {dispatchDir, token, round, startTicks},
# every field present with the right type and non-empty where a string is
# required. ANY deviation is folded into one Ok=$false outcome.
# ---------------------------------------------------------------------
function Get-ReceiptRecord([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return @{ Ok = $false }
    }
    $bytes = $null
    try {
        $bytes = [System.IO.File]::ReadAllBytes($Path)
    } catch {
        return @{ Ok = $false }
    }
    $text = $null
    try {
        $text = [System.Text.Encoding]::UTF8.GetString($bytes)
    } catch {
        return @{ Ok = $false }
    }
    $obj = $null
    try {
        $obj = $text | ConvertFrom-Json -ErrorAction Stop
    } catch {
        return @{ Ok = $false }
    }
    if (($null -eq $obj) -or -not ($obj -is [System.Management.Automation.PSCustomObject])) {
        return @{ Ok = $false }
    }
    $props = @($obj.PSObject.Properties.Name)
    $required = @("dispatchDir", "token", "round", "startTicks")
    if ($props.Count -ne 4) { return @{ Ok = $false } }
    foreach ($r in $required) {
        if ($props -cnotcontains $r) { return @{ Ok = $false } }
    }
    if (-not ($obj.dispatchDir -is [string]) -or $obj.dispatchDir.Trim().Length -eq 0) {
        return @{ Ok = $false }
    }
    if (-not ($obj.token -is [string]) -or $obj.token.Trim().Length -eq 0) {
        return @{ Ok = $false }
    }
    if (-not ($obj.round -is [string]) -or $obj.round.Trim().Length -eq 0) {
        return @{ Ok = $false }
    }
    $st = $obj.startTicks
    $stOk = $false
    $stValue = [long]0
    if ($st -is [string]) {
        $parsed = [long]0
        if ([long]::TryParse($st, [System.Globalization.NumberStyles]::Integer,
                [System.Globalization.CultureInfo]::InvariantCulture, [ref]$parsed)) {
            $stOk = $true
            $stValue = $parsed
        }
    } elseif (($st -is [int]) -or ($st -is [long])) {
        $stOk = $true
        $stValue = [long]$st
    } elseif ($st -is [double]) {
        # A JSON number large enough to need 64 bits round-trips as
        # [double] on some ConvertFrom-Json implementations rather than
        # [long]. It still "parses as a 64-bit integer" as long as it
        # carries no fractional part and fits in Int64 - reject it
        # otherwise, the same as any other non-integer value.
        if (([double]$st -eq [Math]::Truncate($st)) -and
            ($st -ge [double][long]::MinValue) -and ($st -le [double][long]::MaxValue)) {
            $stOk = $true
            $stValue = [long]$st
        }
    }
    if (-not $stOk) { return @{ Ok = $false } }
    return @{ Ok = $true; DispatchDir = [string]$obj.dispatchDir; Token = [string]$obj.token
              Round = [string]$obj.round; StartTicks = $stValue }
}

function Get-PidFileValue([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    $raw = $null
    try {
        $raw = [System.IO.File]::ReadAllText($Path).Trim()
    } catch {
        return $null
    }
    if ($raw -notmatch '^[0-9]+$') { return $null }
    $val = 0
    if (-not [int]::TryParse($raw, [ref]$val)) { return $null }
    if ($val -le 0) { return $null }
    return $val
}

# The startticks FILE the wrapper writes beside its pid (see the header):
# self-published, so it needs the same "readable or not" treatment as the
# pid, just with a 64-bit parse since a tick count does not fit [int].
function Get-StartTicksFileValue([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return $null }
    $raw = $null
    try {
        $raw = [System.IO.File]::ReadAllText($Path).Trim()
    } catch {
        return $null
    }
    if ($raw -notmatch '^-?[0-9]+$') { return $null }
    $val = [long]0
    if (-not [long]::TryParse($raw, [System.Globalization.NumberStyles]::Integer,
            [System.Globalization.CultureInfo]::InvariantCulture, [ref]$val)) {
        return $null
    }
    return $val
}

function Get-ExitFileValue([string]$Path) {
    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) { return @{ Present = $false } }
    $raw = $null
    try {
        $raw = [System.IO.File]::ReadAllText($Path).Trim()
    } catch {
        return @{ Present = $true; Ok = $false }
    }
    if ($raw -notmatch '^-?[0-9]+$') { return @{ Present = $true; Ok = $false } }
    $val = 0
    if (-not [int]::TryParse($raw, [ref]$val)) { return @{ Present = $true; Ok = $false } }
    return @{ Present = $true; Ok = $true; Code = $val }
}

# Copied in shape from tools/kimi-lane-lock.ps1:219-236's Get-Liveness, per
# the header above: three outcomes, never two, and the seam is the same
# fault-injection idea as PARALLAX_LANE_LOCK_STARTTIME_FAULT there.
function Get-PollLiveness([int]$PidValue, [long]$ExpectedTicks) {
    $proc = $null
    try {
        $proc = Get-Process -Id $PidValue -ErrorAction Stop
    } catch {
        return "DEAD"
    }
    $actualTicks = $null
    try {
        if ($env:PARALLAX_DISPATCH_POLL_STARTTIME_FAULT) {
            throw "PARALLAX_DISPATCH_POLL_STARTTIME_FAULT injected: simulated start-time read failure"
        }
        $actualTicks = $proc.StartTime.ToUniversalTime().Ticks
    } catch {
        return "UNMEASURABLE"
    }
    if ([long]$actualTicks -eq $ExpectedTicks) { return "LIVE" }
    return "DEAD"
}

function Get-ExitCodeForState([string]$State) {
    if ($State -eq "reply-present") { return 0 }
    if ($State -eq "running") { return 3 }
    return 1
}

function Emit-PollResult([string]$State, $RoundLabel) {
    if ($Json) {
        $obj = [ordered]@{ state = $State; round = $RoundLabel }
        Write-Output (ConvertTo-Json $obj -Compress)
    } else {
        Write-Output $State
    }
    exit (Get-ExitCodeForState $State)
}

# ---------------------------------------------------------------------
# Mode selection and required-value checks are done BY HAND, not by
# PowerShell's own Mandatory binder: a missing mandatory parameter binds
# BEFORE $ErrorActionPreference is set and, measured on this host, exits
# 1 - which this tool's -Poll table already uses for a fully-bound
# refusal. Checking by hand here is what makes exit 2 ("a failure to bind
# the parameters") a promise this script keeps rather than an artifact of
# whichever exit code the binder happens to choose.
# ---------------------------------------------------------------------
if ($Prepare -and $Poll) {
    Write-Output "ERROR: -Prepare and -Poll are mutually exclusive"
    exit 2
}
if (-not $Prepare -and -not $Poll) {
    Write-Output "ERROR: specify exactly one of -Prepare or -Poll"
    exit 2
}

if ($Poll) {
    if ([string]::IsNullOrWhiteSpace($Receipt) -or
        [string]::IsNullOrWhiteSpace($ExpectedDispatchDir) -or
        [string]::IsNullOrWhiteSpace($ExpectedRound)) {
        Write-Output "ERROR: -Poll requires -Receipt, -ExpectedDispatchDir and -ExpectedRound"
        exit 2
    }

    try {
        $receiptFull = Resolve-UnresolvedPath $Receipt
    } catch {
        Write-Output ("ERROR: could not resolve -Receipt: " + $_.Exception.Message)
        exit 2
    }

    $rec = Get-ReceiptRecord $receiptFull
    if (-not $rec.Ok) {
        Emit-PollResult -State "no-receipt" -RoundLabel $null
    }

    $dispatchMatches = Test-PathsEqual $rec.DispatchDir $ExpectedDispatchDir
    $roundMatches = [string]::Equals($rec.Round, $ExpectedRound, [System.StringComparison]::Ordinal)
    if ((-not $dispatchMatches) -or (-not $roundMatches)) {
        Emit-PollResult -State "receipt-not-expected" -RoundLabel $rec.Round
    }

    $committedPath = Join-Path $rec.DispatchDir "launch.committed"
    if (-not (Test-Path -LiteralPath $committedPath -PathType Leaf)) {
        Emit-PollResult -State "launch-unknown" -RoundLabel $rec.Round
    }
    $committedToken = $null
    try {
        $committedToken = [System.IO.File]::ReadAllText($committedPath).Trim()
    } catch {
        $committedToken = $null
    }
    if (($null -eq $committedToken) -or
        -not [string]::Equals($committedToken, $rec.Token, [System.StringComparison]::Ordinal)) {
        Emit-PollResult -State "launch-not-ours" -RoundLabel $rec.Round
    }

    $cwdPath = Join-Path $rec.DispatchDir "cwd"
    if (-not (Test-Path -LiteralPath $cwdPath -PathType Leaf)) {
        Emit-PollResult -State "not-started" -RoundLabel $rec.Round
    }

    $pidPath = Join-Path $rec.DispatchDir "pid"
    if (-not (Test-Path -LiteralPath $pidPath -PathType Leaf)) {
        Emit-PollResult -State "not-started" -RoundLabel $rec.Round
    }
    $pidVal = Get-PidFileValue $pidPath
    if ($null -eq $pidVal) {
        Emit-PollResult -State "pid-unreadable" -RoundLabel $rec.Round
    }
    $ticksVal = Get-StartTicksFileValue (Join-Path $rec.DispatchDir "startticks")
    if ($null -eq $ticksVal) {
        Emit-PollResult -State "pid-unreadable" -RoundLabel $rec.Round
    }

    $liveness = Get-PollLiveness -PidValue $pidVal -ExpectedTicks $ticksVal
    if ($liveness -eq "UNMEASURABLE") {
        Emit-PollResult -State "pid-unreadable" -RoundLabel $rec.Round
    }
    if ($liveness -eq "LIVE") {
        Emit-PollResult -State "running" -RoundLabel $rec.Round
    }

    $exitInfo = Get-ExitFileValue (Join-Path $rec.DispatchDir "exit")
    if (-not $exitInfo.Present) {
        Emit-PollResult -State "no-exit-file" -RoundLabel $rec.Round
    }
    if (-not $exitInfo.Ok) {
        Emit-PollResult -State "exit-unreadable" -RoundLabel $rec.Round
    }
    if ($exitInfo.Code -ne 0) {
        Emit-PollResult -State "exit-nonzero" -RoundLabel $rec.Round
    }

    $replyPath = Join-Path $rec.DispatchDir "reply"
    if (-not (Test-Path -LiteralPath $replyPath -PathType Leaf)) {
        Emit-PollResult -State "no-reply" -RoundLabel $rec.Round
    }
    $replyBytes = $null
    try {
        $replyBytes = [System.IO.File]::ReadAllBytes($replyPath)
    } catch {
        $replyBytes = $null
    }
    if (($null -eq $replyBytes) -or ($replyBytes.Length -eq 0)) {
        Emit-PollResult -State "reply-empty" -RoundLabel $rec.Round
    }
    Emit-PollResult -State "reply-present" -RoundLabel $rec.Round
}

# ---------------------------------------------------------------------
# -Prepare
# ---------------------------------------------------------------------
if ([string]::IsNullOrWhiteSpace($DispatchDir) -or [string]::IsNullOrWhiteSpace($WrapperBody) -or
    [string]::IsNullOrWhiteSpace($ReceiptPath) -or [string]::IsNullOrWhiteSpace($Round) -or
    [string]::IsNullOrWhiteSpace($WorkingDirectory)) {
    Write-Output "ERROR: -Prepare requires -DispatchDir, -WrapperBody, -ReceiptPath, -Round and -WorkingDirectory"
    exit 2
}

try {
    $dispatchFull = Resolve-UnresolvedPath $DispatchDir
    $receiptFull = Resolve-UnresolvedPath $ReceiptPath
    $workingDirFull = Resolve-UnresolvedPath $WorkingDirectory
} catch {
    Write-Output ("ERROR: could not resolve the prepare paths: " + $_.Exception.Message)
    exit 2
}

# Step 0a: -WorkingDirectory survived the launcher's deletion. It is what
# puts the reviewer client inside the REVIEW MIRROR. An earlier draft of
# the design spec called it launcher-only and this tool dropped it; the
# FIRST round dispatched under that version ran with the REAL REPOSITORY
# as its working directory, where a root AGENTS.md sits on disk and the
# reviewer client auto-ingests it as instructions - the instruction
# back-channel the preflight exists to stop. The round was discarded
# UNREAD; its cost is recorded in
# docs/superpowers/specs/2026-08-31-tracked-background-dispatch-design.md
# section 1. Checked and BLOCKED here, before the dispatch directory is
# reserved: a round that cannot say where it must run is not runnable.
if (-not (Test-Path -LiteralPath $workingDirFull -PathType Container)) {
    Write-Output ("BLOCKED: -WorkingDirectory does not exist or is not a directory (" +
        $workingDirFull + ")")
    exit 1
}

# Step 1: separation and freshness, before anything is created.
$dNorm = $dispatchFull.TrimEnd('\', '/')
$rNorm = $receiptFull.TrimEnd('\', '/')
$dPrefix = $dNorm + '\'
$cmp = [System.StringComparison]::OrdinalIgnoreCase
if ([string]::Equals($rNorm, $dNorm, $cmp) -or $rNorm.StartsWith($dPrefix, $cmp)) {
    Write-Output ("BLOCKED: the receipt path is equal to, or inside, the dispatch directory (" +
        $receiptFull + " / " + $dispatchFull + ")")
    exit 1
}
if (Test-Path -LiteralPath $receiptFull) {
    Write-Output ("BLOCKED: the receipt path already exists (" + $receiptFull + ")")
    exit 1
}

# Step 2: reserve the directory. No -Force: a taken directory fails
# loudly instead of proceeding with an unreliable path.
$d = $null
try {
    $d = (New-Item -ItemType Directory -Path $dispatchFull -ErrorAction Stop).FullName
} catch {
    Write-Output ("BLOCKED: could not reserve the dispatch directory: " + $_.Exception.Message)
    exit 1
}

# Steps 3-6: everything from here through the receipt write is one
# transaction. -Prepare starts no process, so a failure here has nothing
# to kill - it publishes no receipt and exits 1, with NO filesystem
# cleanup, per the header.
$token = $null
try {
    $wrapperDest = Join-Path $d "wrapper.ps1"
    Copy-Item -LiteralPath $WrapperBody -Destination $wrapperDest -ErrorAction Stop
    New-Item -ItemType File -Path (Join-Path $d "stdin.empty") -ErrorAction Stop | Out-Null

    # Write the resolved working directory in the same step that installs
    # the wrapper, so it is present before the receipt is published (see
    # the header). UTF-8 without a BOM, matching the wrapper's own read
    # (New-Object System.Text.UTF8Encoding($false, $true)) as its second
    # act, right after publishing its identity.
    [System.IO.File]::WriteAllText((Join-Path $d "cwd"), $workingDirFull,
        (New-Object System.Text.UTF8Encoding($false)))

    $token = [System.Guid]::NewGuid().ToString()
    Set-Content -LiteralPath (Join-Path $d "launch.committed") -Value $token -NoNewline -Encoding Ascii

    # Step 4: the hold-before-publish barrier. See the header. Absent the
    # env var, this block does nothing.
    $holdBase = $env:PARALLAX_DISPATCH_HOLD_BEFORE_PUBLISH
    if (-not [string]::IsNullOrEmpty($holdBase)) {
        New-Item -ItemType File -Path ($holdBase + ".started") -Force -ErrorAction Stop | Out-Null
        $releasePath = $holdBase + ".release"
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        while (-not (Test-Path -LiteralPath $releasePath)) {
            if ($sw.Elapsed.TotalSeconds -ge 60) {
                throw "hold-before-publish barrier: no release within 60 seconds"
            }
            Start-Sleep -Milliseconds 100
        }
    }

    # Step 6: the receipt, last of all, create-new only. startTicks is a
    # fixed placeholder - see the header note on why it no longer
    # describes a real process.
    $receiptObj = [ordered]@{
        dispatchDir = $d
        token       = $token
        round       = $Round
        startTicks  = [long]0
    }
    $receiptJson = ConvertTo-Json $receiptObj -Compress
    $receiptBytes = [System.Text.Encoding]::UTF8.GetBytes($receiptJson)
    $fs = New-Object System.IO.FileStream($receiptFull, [System.IO.FileMode]::CreateNew,
        [System.IO.FileAccess]::Write, [System.IO.FileShare]::None)
    try {
        $fs.Write($receiptBytes, 0, $receiptBytes.Length)
        $fs.Flush($true)
    } finally {
        $fs.Dispose()
    }
} catch {
    Write-Output ("BLOCKED: " + $_.Exception.Message)
    exit 1
}

if ($Json) {
    $obj = [ordered]@{
        prepared    = $true
        dispatchDir = $d
        token       = $token
        round       = $Round
        receiptPath = $receiptFull
    }
    Write-Output (ConvertTo-Json $obj -Compress)
} else {
    Write-Output ("PREPARED: " + $d)
}
exit 0
