# dispatch-round.ps1 - launch a PowerShell wrapper body as a detached
# child process and poll its completion without blocking the caller's
# tool-call ceiling (foreground commands cap out at 600 seconds; a review
# round or a live dispatch can run far longer than that).
#
# TWO MODES. Every later task depends on these exact names.
#
#   Launch: -DispatchDir <path> -WrapperBody <path> -ReceiptPath <path>
#           -Round <label> [-WorkingDirectory <path>] [-Json]
#   Poll:   -Receipt <path> -ExpectedDispatchDir <path> -ExpectedRound <label>
#           [-Json]
#
# -Poll NAMES A RECEIPT, NEVER A DIRECTORY. A caller that could poll a bare
# directory could read a launch token straight out of the directory it is
# already looking at and hand it back to itself, which proves nothing. The
# receipt is written OUTSIDE the dispatch directory, at a path -Launch
# refuses if it already exists, LAST of all and only on success.
#
# -Launch ENFORCES the separation rather than describing it: it resolves
# both paths and BLOCKS, before anything is created, if the receipt path
# is equal to, or inside, the dispatch directory. A refused launch writes
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
# omission.
#
# THE TOKEN IS NOT A SECRET. [System.Guid]::NewGuid() mints it, it also
# sits in plain sight inside launch.committed, and a caller determined to
# launder an old directory could read it there. What the receipt actually
# adds is that a REFUSED launch produces no receipt at all - there is
# nothing to read back.
#
# -Poll is told, INDEPENDENTLY of the receipt, which directory and which
# round it is polling for (-ExpectedDispatchDir / -ExpectedRound), and
# compares BOTH before it opens anything else. A mismatch on either one is
# receipt-not-expected. The label alone would not be enough - a round
# label such as "Sol R1" is reusable across a retry of the same round -
# which is why the directory is checked too. The caller already has both
# values: it passed them to -Launch.
#
# THE RESIDUAL, admitted rather than claimed closed: a caller that supplies
# an EARLIER attempt's receipt, AND that attempt's directory, AND its
# label, gets that attempt's result - because at that point every value
# the caller supplied genuinely describes the earlier act, and nothing
# inside this tool can distinguish that caller from one who is confused
# about all three at once. The controls are a fresh round-numbered receipt
# path per round and a -Launch that refuses to overwrite an existing one.
# This is NARROWED, the same way the interrupted launch that leaves no
# receipt at all is narrowed, not eliminated.
#
# -Poll computes exactly one of these TWELVE state names, in the fixed
# order below, and stops at the first that matches:
#   no-receipt, receipt-not-expected, launch-unknown, launch-not-ours,
#   pid-unreadable, running, no-exit-file, exit-unreadable, exit-nonzero,
#   no-reply, reply-empty, reply-present.
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
#      required value, both or neither of -Launch/-Poll) or an internal
#      execution error. Reading the receipt's CONTENT is never exit 2: an
#      absent, unreadable, or schema-failing receipt is no-receipt at
#      exit 1.
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
# -Launch's exit codes match new-review-mirror.ps1:17-18: 0 launched and
# committed, 1 blocked (reason on stdout), 2 script or environment error
# (including a failure to bind the parameters). -Poll extends that set
# with 3 and narrows 2 as described above.
#
# -Launch, in order, under $ErrorActionPreference = 'Stop':
#   1. Resolve -ReceiptPath and -DispatchDir to full paths. BLOCK if the
#      receipt path is equal to, or inside, the dispatch directory, and
#      BLOCK if the receipt path already exists. Both checks run before
#      anything is created, so a refusal leaves no directory behind.
#   2. Reserve the dispatch directory with New-Item -ItemType Directory
#      and -ErrorAction Stop, and NO -Force: a taken directory must fail
#      loudly rather than silently proceed with an unreliable path.
#      Failure here is BLOCKED and nothing has started.
#   3. Copy -WrapperBody into the directory as wrapper.ps1; create an
#      empty stdin.empty beside it.
#   4. Launch the launching host itself against wrapper.ps1, detached, with
#      stdin/stdout/stderr redirected into the directory. NOT Start-Process -
#      see the handle-inheritance note just below $ErrorActionPreference for
#      why, and HandleListLauncher.LaunchDetached for the mechanism. It
#      returns the child's pid and start ticks together, read race-free off
#      the same handle CreateProcess produced.
#   5. If PARALLAX_DISPATCH_HOLD_BEFORE_PUBLISH is set (to a path), create
#      "<value>.started" once the launch call above has returned, then wait,
#      bounded at sixty seconds, for "<value>.release" before writing pid.
#      On timeout, fail through the same catch as any other failure.
#   6. Write pid and startticks (both already captured by step 4), THEN
#      write launch.committed with the minted token as its content.
#   7. Write the RECEIPT last of all, and only now, with create-new
#      semantics (fails if the path was raced into existence since step
#      1's check). Its path was already checked for freshness and for
#      separation in step 1, so this can only fail on a race, and a race
#      here fails through the same catch as any other failure.
#   8. Steps 4 through 7 are wrapped in one catch that runs
#      "taskkill /PID <pid> /T /F" when the process was started, then
#      exits 1. Never leave a started process unrecorded and unreported.
#      The catch performs NO filesystem cleanup: a directory left behind
#      is inert and inspectable, while a published receipt or a live,
#      unrecorded child is not. That is deliberate, not an oversight - a
#      reserved-but-abandoned dispatch directory is the expected shape of
#      a handled failure, never evidence of one.
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
#   5. pid missing, unreadable, or not an integer -> pid-unreadable.
#   6. Liveness, computed exactly the way tools/kimi-lane-lock.ps1:219-236
#      computes Get-Liveness: no such process -> DEAD, continue; the
#      process exists but its start time cannot be read -> pid-unreadable,
#      stop; the process exists and its ticks differ from the receipt's
#      (the pid was recycled) -> DEAD, continue; ticks match -> running,
#      stop, and NOTHING ELSE IS READ - a reply being written is not a
#      reply.
#   7. No exit file -> no-exit-file. Unreadable or not a plain integer ->
#      exit-unreadable. Non-zero -> exit-nonzero.
#   8. Zero and no reply file -> no-reply. Zero and reply is empty ->
#      reply-empty. Zero and reply has content -> reply-present.
#
# TWO ENV-GATED TEST SEAMS, both BUILDER CONTRACT rather than test
# scaffolding, the same shape as the two seams in
# tools/new-kimi-lane-home.ps1: each is reachable by any parent process
# that sets the variable, no shipped caller sets either one, and each can
# only make an invocation FAIL or answer MORE CONSERVATIVELY - never turn
# a failing launch into a successful one, and never turn an unmeasured
# poll state into "running" or a terminal success.
#   PARALLAX_DISPATCH_HOLD_BEFORE_PUBLISH - see step 5 above. The
#     deterministic barrier a hard-kill-before-publication test needs;
#     without it, that test is the same millisecond race in a different
#     costume. Unset, the seam does not exist.
#   PARALLAX_DISPATCH_POLL_STARTTIME_FAULT - forces the live-process
#     start-time read in step 6 above to throw AFTER the pid lookup has
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
    [switch]$Launch,
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

# MEASURED 2026-08-31, not assumed: Start-Process's own -RedirectStandardOutput
# / -RedirectStandardError forces .NET's Process class to request
# bInheritHandles=TRUE for the CreateProcess call. That flag is process-wide -
# it duplicates EVERY inheritable handle already open in THIS process into
# the new child, not just the three handles Start-Process means to pass. When
# the caller of -Launch captures ITS OWN stdout/stderr through a pipe (the
# normal shape of a Bash/PowerShell tool call, and how every test in
# evals/multi-model-verify/test_dispatch_round.py drives this script),
# those pipe write-ends are themselves inheritable, so the wrapper child
# inherits them too - and the caller's pipe-read then blocks until the
# wrapper exits, not until -Launch returns. Measured: -Launch built on plain
# Start-Process -RedirectStandardOutput/-RedirectStandardError took the full
# duration of a 25-second wrapper to return when its caller captured -Launch's
# own stdout/stderr through a pipe; switching only the caller's capture mode
# to a non-pipe target removed the delay, isolating the cause to handle
# inheritance rather than anything else in this script's control flow. This
# is exactly the class of caller this tool
# exists to not block - see the header above - so a literal Start-Process
# call cannot be the transport: it would make -Launch itself re-introduce
# the 600-second-ceiling problem this whole tool exists to remove, and
# test_poll_reports_running_while_the_pid_is_alive /
# test_a_running_round_can_never_exit_zero could not pass against it (the
# poll would only ever observe a launch that already reached exit/reply).
#
# The fix restricts the new process's inherited handles to EXACTLY the three
# this script opens for it, via Windows' documented allowlist mechanism
# (PROC_THREAD_ATTRIBUTE_HANDLE_LIST): CreateFile the three redirection
# targets itself (marked inheritable), build a STARTUPINFOEX carrying an
# attribute list naming only those three handles, and call CreateProcess
# with EXTENDED_STARTUPINFO_PRESENT. bInheritHandles is still TRUE (required
# for the three handles to pass at all), but the attribute list overrides the
# default all-or-nothing inheritance, so nothing else open in this process -
# including a caller's own piped stdout/stderr - reaches the child. This is
# the same mechanism Microsoft documents for exactly this scenario ("Silently
# Fixing a Process Launched with Inherited Handles").
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
using System.Text;

namespace ParallaxDetachedDispatch {
    public static class HandleListLauncher {
        [StructLayout(LayoutKind.Sequential)]
        public struct STARTUPINFO {
            public int cb;
            public IntPtr lpReserved;
            public IntPtr lpDesktop;
            public IntPtr lpTitle;
            public int dwX, dwY, dwXSize, dwYSize, dwXCountChars, dwYCountChars, dwFillAttribute, dwFlags;
            public short wShowWindow, cbReserved2;
            public IntPtr lpReserved2;
            public IntPtr hStdInput, hStdOutput, hStdError;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct STARTUPINFOEX {
            public STARTUPINFO StartupInfo;
            public IntPtr lpAttributeList;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct PROCESS_INFORMATION {
            public IntPtr hProcess, hThread;
            public int dwProcessId, dwThreadId;
        }

        [StructLayout(LayoutKind.Sequential)]
        public struct SECURITY_ATTRIBUTES {
            public int nLength;
            public IntPtr lpSecurityDescriptor;
            public bool bInheritHandle;
        }

        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern bool InitializeProcThreadAttributeList(IntPtr lpAttributeList, int dwAttributeCount, int dwFlags, ref IntPtr lpSize);

        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern bool UpdateProcThreadAttribute(IntPtr lpAttributeList, uint dwFlags, IntPtr Attribute, IntPtr lpValue, IntPtr cbSize, IntPtr lpPreviousValue, IntPtr lpReturnSize);

        [DllImport("kernel32.dll")]
        public static extern void DeleteProcThreadAttributeList(IntPtr lpAttributeList);

        [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
        public static extern bool CreateProcess(
            string lpApplicationName, StringBuilder lpCommandLine,
            IntPtr lpProcessAttributes, IntPtr lpThreadAttributes,
            bool bInheritHandles, uint dwCreationFlags,
            IntPtr lpEnvironment, string lpCurrentDirectory,
            ref STARTUPINFOEX lpStartupInfo,
            out PROCESS_INFORMATION lpProcessInformation);

        [DllImport("kernel32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
        public static extern IntPtr CreateFile(string lpFileName, uint dwDesiredAccess, uint dwShareMode,
            ref SECURITY_ATTRIBUTES lpSecurityAttributes, uint dwCreationDisposition, uint dwFlagsAndAttributes, IntPtr hTemplateFile);

        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern bool CloseHandle(IntPtr hObject);

        [StructLayout(LayoutKind.Sequential)]
        public struct FILETIME {
            public uint dwLowDateTime;
            public uint dwHighDateTime;
        }

        [DllImport("kernel32.dll", SetLastError = true)]
        public static extern bool GetProcessTimes(IntPtr hProcess, out FILETIME lpCreationTime,
            out FILETIME lpExitTime, out FILETIME lpKernelTime, out FILETIME lpUserTime);

        const int PROC_THREAD_ATTRIBUTE_HANDLE_LIST = 0x00020002;
        const uint EXTENDED_STARTUPINFO_PRESENT = 0x00080000;
        const uint CREATE_NO_WINDOW = 0x08000000;
        const uint STARTF_USESTDHANDLES = 0x00000100;
        const uint GENERIC_READ = 0x80000000;
        const uint GENERIC_WRITE = 0x40000000;
        const uint FILE_SHARE_READ = 1, FILE_SHARE_WRITE = 2, FILE_SHARE_DELETE = 4;
        const uint OPEN_EXISTING = 3, CREATE_ALWAYS = 2;
        const uint FILE_ATTRIBUTE_NORMAL = 0x80;

        // Returns "pid,startTicks" as one string (keeping the PowerShell/C#
        // boundary to a plain marshaled type). startTicks is read via
        // GetProcessTimes on the EXACT handle CreateProcess just returned,
        // before that handle is closed - a handle keeps its process object
        // alive in the kernel regardless of how fast the process exits, so
        // this cannot race a PID recycle the way a later Get-Process /
        // OpenProcess(pid) lookup could for an already-finished wrapper.
        // The FILETIME GetProcessTimes returns is 100ns ticks since 1601;
        // converting through DateTime.FromFileTimeUtc gives the same .NET
        // DateTime.Ticks epoch (0001) that Get-Process's own StartTime
        // property uses, so -Poll's liveness check compares like with like.
        public static string LaunchDetached(string exePath, string commandLine, string stdinPath,
                                          string stdoutPath, string stderrPath, string workingDirectory) {
            SECURITY_ATTRIBUTES sa = new SECURITY_ATTRIBUTES();
            sa.nLength = Marshal.SizeOf(typeof(SECURITY_ATTRIBUTES));
            sa.bInheritHandle = true;
            sa.lpSecurityDescriptor = IntPtr.Zero;

            IntPtr hIn = CreateFile(stdinPath, GENERIC_READ, FILE_SHARE_READ | FILE_SHARE_WRITE | FILE_SHARE_DELETE, ref sa, OPEN_EXISTING, FILE_ATTRIBUTE_NORMAL, IntPtr.Zero);
            if (hIn == new IntPtr(-1)) throw new InvalidOperationException("CreateFile stdin failed: " + Marshal.GetLastWin32Error());
            IntPtr hOut = CreateFile(stdoutPath, GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_DELETE, ref sa, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, IntPtr.Zero);
            if (hOut == new IntPtr(-1)) throw new InvalidOperationException("CreateFile stdout failed: " + Marshal.GetLastWin32Error());
            IntPtr hErr = CreateFile(stderrPath, GENERIC_WRITE, FILE_SHARE_READ | FILE_SHARE_DELETE, ref sa, CREATE_ALWAYS, FILE_ATTRIBUTE_NORMAL, IntPtr.Zero);
            if (hErr == new IntPtr(-1)) throw new InvalidOperationException("CreateFile stderr failed: " + Marshal.GetLastWin32Error());

            IntPtr handleArray = Marshal.AllocHGlobal(IntPtr.Size * 3);
            Marshal.WriteIntPtr(handleArray, 0 * IntPtr.Size, hIn);
            Marshal.WriteIntPtr(handleArray, 1 * IntPtr.Size, hOut);
            Marshal.WriteIntPtr(handleArray, 2 * IntPtr.Size, hErr);

            IntPtr attrListSize = IntPtr.Zero;
            InitializeProcThreadAttributeList(IntPtr.Zero, 1, 0, ref attrListSize);
            IntPtr attrList = Marshal.AllocHGlobal(attrListSize);
            if (!InitializeProcThreadAttributeList(attrList, 1, 0, ref attrListSize))
                throw new InvalidOperationException("InitializeProcThreadAttributeList failed: " + Marshal.GetLastWin32Error());

            if (!UpdateProcThreadAttribute(attrList, 0, (IntPtr)PROC_THREAD_ATTRIBUTE_HANDLE_LIST,
                    handleArray, (IntPtr)(IntPtr.Size * 3), IntPtr.Zero, IntPtr.Zero))
                throw new InvalidOperationException("UpdateProcThreadAttribute failed: " + Marshal.GetLastWin32Error());

            STARTUPINFOEX siex = new STARTUPINFOEX();
            siex.StartupInfo.cb = Marshal.SizeOf(typeof(STARTUPINFOEX));
            siex.StartupInfo.dwFlags = (int)STARTF_USESTDHANDLES;
            siex.StartupInfo.hStdInput = hIn;
            siex.StartupInfo.hStdOutput = hOut;
            siex.StartupInfo.hStdError = hErr;
            siex.lpAttributeList = attrList;

            PROCESS_INFORMATION pi;
            StringBuilder cmdLineBuilder = new StringBuilder(commandLine);
            bool ok = CreateProcess(exePath, cmdLineBuilder, IntPtr.Zero, IntPtr.Zero, true,
                EXTENDED_STARTUPINFO_PRESENT | CREATE_NO_WINDOW, IntPtr.Zero,
                string.IsNullOrEmpty(workingDirectory) ? null : workingDirectory,
                ref siex, out pi);
            int err = Marshal.GetLastWin32Error();

            DeleteProcThreadAttributeList(attrList);
            Marshal.FreeHGlobal(attrList);
            Marshal.FreeHGlobal(handleArray);
            CloseHandle(hIn);
            CloseHandle(hOut);
            CloseHandle(hErr);

            if (!ok) throw new InvalidOperationException("CreateProcess failed: " + err);

            CloseHandle(pi.hThread);
            int pid = pi.dwProcessId;
            long startTicks = 0;
            FILETIME ftCreate, ftExit, ftKernel, ftUser;
            if (GetProcessTimes(pi.hProcess, out ftCreate, out ftExit, out ftKernel, out ftUser)) {
                long fileTime = ((long)ftCreate.dwHighDateTime << 32) | (uint)ftCreate.dwLowDateTime;
                startTicks = DateTime.FromFileTimeUtc(fileTime).Ticks;
            }
            CloseHandle(pi.hProcess);
            if (startTicks == 0)
                throw new InvalidOperationException("GetProcessTimes failed: " + Marshal.GetLastWin32Error());
            return pid.ToString() + "," + startTicks.ToString();
        }
    }
}
"@ -ErrorAction Stop

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
if ($Launch -and $Poll) {
    Write-Output "ERROR: -Launch and -Poll are mutually exclusive"
    exit 2
}
if (-not $Launch -and -not $Poll) {
    Write-Output "ERROR: specify exactly one of -Launch or -Poll"
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

    $pidVal = Get-PidFileValue (Join-Path $rec.DispatchDir "pid")
    if ($null -eq $pidVal) {
        Emit-PollResult -State "pid-unreadable" -RoundLabel $rec.Round
    }

    $liveness = Get-PollLiveness -PidValue $pidVal -ExpectedTicks $rec.StartTicks
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
# -Launch
# ---------------------------------------------------------------------
if ([string]::IsNullOrWhiteSpace($DispatchDir) -or [string]::IsNullOrWhiteSpace($WrapperBody) -or
    [string]::IsNullOrWhiteSpace($ReceiptPath) -or [string]::IsNullOrWhiteSpace($Round)) {
    Write-Output "ERROR: -Launch requires -DispatchDir, -WrapperBody, -ReceiptPath and -Round"
    exit 2
}

try {
    $dispatchFull = Resolve-UnresolvedPath $DispatchDir
    $receiptFull = Resolve-UnresolvedPath $ReceiptPath
} catch {
    Write-Output ("ERROR: could not resolve the launch paths: " + $_.Exception.Message)
    exit 2
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

# Steps 3-7: everything from here through the receipt write is one
# transaction. Any failure kills the started process tree (if one was
# started) and blocks - with NO filesystem cleanup, per the header.
$launchedPid = $null
$token = $null
try {
    $wrapperDest = Join-Path $d "wrapper.ps1"
    Copy-Item -LiteralPath $WrapperBody -Destination $wrapperDest -ErrorAction Stop
    New-Item -ItemType File -Path (Join-Path $d "stdin.empty") -ErrorAction Stop | Out-Null

    # See the handle-inheritance note above $ErrorActionPreference: this is
    # NOT Start-Process. LaunchDetached restricts the child's inherited
    # handles to exactly the three redirection targets below.
    $wrapperCmdLine = '"' + (Get-Process -Id $PID).Path + '" -NoProfile -NonInteractive -File "' + $wrapperDest + '"'
    $launchResult = [ParallaxDetachedDispatch.HandleListLauncher]::LaunchDetached(
        (Get-Process -Id $PID).Path,
        $wrapperCmdLine,
        (Join-Path $d "stdin.empty"),
        (Join-Path $d "launch.out"),
        (Join-Path $d "launch.err"),
        $WorkingDirectory)
    $parts = $launchResult.Split(",")
    $launchedPid = [int]$parts[0]
    $startTicks = [string]$parts[1]

    # Step 5: the hold-before-publish barrier. See the header. Absent the
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

    # Step 6: pid and startticks BEFORE the commit marker. Both were
    # already captured race-free by LaunchDetached (see its comment) -
    # this just publishes them.
    Set-Content -LiteralPath (Join-Path $d "pid") -Value ([string]$launchedPid) -NoNewline -Encoding Ascii
    Set-Content -LiteralPath (Join-Path $d "startticks") -Value $startTicks -NoNewline -Encoding Ascii
    $token = [System.Guid]::NewGuid().ToString()
    Set-Content -LiteralPath (Join-Path $d "launch.committed") -Value $token -NoNewline -Encoding Ascii

    # Step 7: the receipt, last of all, create-new only.
    $receiptObj = [ordered]@{
        dispatchDir = $d
        token       = $token
        round       = $Round
        startTicks  = [long]$startTicks
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
    if ($launchedPid) {
        try { & taskkill /PID $launchedPid /T /F 2>&1 | Out-Null } catch { }
    }
    Write-Output ("BLOCKED: " + $_.Exception.Message)
    exit 1
}

if ($Json) {
    $obj = [ordered]@{
        launched    = $true
        dispatchDir = $d
        token       = $token
        round       = $Round
        receiptPath = $receiptFull
    }
    Write-Output (ConvertTo-Json $obj -Compress)
} else {
    Write-Output ("LAUNCHED: " + $d)
}
exit 0
