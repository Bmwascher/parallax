"""The reviewer's TOOL surface probe (0.24.0, backlog item 7).

0.17.0 measures the reviewer's PROMPT. Tools are not in the prompt, so a
review could satisfy every rule this repo has while the auditor held a
code execution tool. Measured 2026-08-11, `codex app-server --stdio`
answers `mcpServerStatus/list`, which names every resolved MCP server and
every tool, and starts no turn - so the surface item 7 said did not exist
does exist, and is free.

WHAT THESE CASES LOCK, and the distinction is the whole design. Measured
the same day: a DISABLED server and a server that FAILED TO LAUNCH are
byte-identical in that record, both `serverInfo: null` with zero tools.
So:

- pass 1 is an INSTRUMENT CALIBRATION. If it sees nothing, the probe is
  not known to be able to see anything and the verdict is BLOCKED.
- a tool PRESENT in pass 2 outside the allowlist is a real DETECTION.
- a tool ABSENT from pass 2 is a MITIGATION, never proof of removal.

The cases below exist mostly to hold the BLOCKED directions, because the
one outcome this script may never produce is a clean report from a
measurement nobody made.

Fixtures are synthetic. This repo is public.
"""
import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PROBE = REPO_ROOT / "tools" / "codex-tool-surface-probe.ps1"
STUB = Path(__file__).parent / "fixtures" / "stub-appserver" / "stub-appserver.ps1"

POWERSHELL = (os.environ.get("PARALLAX_PS_HOST")
              or shutil.which("powershell") or shutil.which("pwsh"))

pytestmark = pytest.mark.skipif(
    POWERSHELL is None,
    reason="the probe is a PowerShell tool and needs a host to run")


# A healthy server, as the real one reports it: serverInfo populated, a
# tools map keyed by name. Copied in SHAPE from the 2026-08-11 measurement,
# never a raw recording.
HEALTHY = json.dumps([{
    "name": "node_repl",
    "serverInfo": {"name": "node_repl", "version": "1.0.0"},
    "authStatus": "unsupported",
    "tools": {"js": {}, "js_add_node_module_dir": {}, "js_reset": {}},
}])

# The ambiguous record. `-c mcp_servers.node_repl.enabled=false` and a
# deliberately broken command produced THIS, indistinguishably.
SILENT = json.dumps([{
    "name": "node_repl",
    "serverInfo": None,
    "authStatus": "unsupported",
    "tools": {},
}])

EMPTY = "[]"

TWO_SERVERS = json.dumps([
    {
        "name": "codex_apps",
        "serverInfo": {"name": "codex_apps", "version": "1.0.0"},
        "authStatus": "unsupported",
        "tools": {"app_open": {}, "app_close": {}},
    },
    {
        "name": "node_repl",
        "serverInfo": {"name": "node_repl", "version": "1.0.0"},
        "authStatus": "unsupported",
        "tools": {"js": {}, "js_add_node_module_dir": {}, "js_reset": {}},
    },
])


def run_probe(pass1=HEALTHY, pass2=EMPTY, mode=None, exit_code=None,
              hang_secs=None, extra=(), log=None, timeout=90):
    """Drive the probe against the stub app server.

    The stub is a .ps1 and is invoked IN-PROCESS through -CodexCommand, the
    same way test_codex_context_probe.py drives its stub: routing it through
    `powershell -File` would serialize the arguments through command-line
    parsing and let the harness, rather than the real transport, decide what
    the stub received.
    """
    env = dict(os.environ)
    env["PARALLAX_STUB_AS_PASS1"] = pass1
    env["PARALLAX_STUB_AS_PASS2"] = pass2
    if mode:
        env["PARALLAX_STUB_AS_MODE"] = mode
    if exit_code is not None:
        env["PARALLAX_STUB_AS_EXIT"] = str(exit_code)
    if hang_secs is not None:
        env["PARALLAX_STUB_AS_HANGSECS"] = str(hang_secs)
    if log:
        env["PARALLAX_STUB_AS_LOG"] = str(log)
    for k in ("PARALLAX_STUB_AS_MODE", "PARALLAX_STUB_AS_EXIT"):
        if k in env and env[k] == "":
            del env[k]

    args = [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(PROBE),
            "-CodexCommand", str(STUB), "-Json"]
    args.extend(extra)
    proc = subprocess.run(args, capture_output=True, text=True, env=env,
                          timeout=timeout)
    return proc


def verdict(proc):
    """Parse the -Json report. A report this parser cannot read is itself a
    failure: the caller must never fall back to guessing from the text."""
    out = proc.stdout.strip()
    assert out, "the probe wrote nothing at all: " + proc.stderr
    last = [ln for ln in out.splitlines() if ln.strip().startswith("{")]
    assert last, "no JSON object in the probe output: " + out
    return json.loads(last[-1])


class TestTheInstrumentMustBeShownToWork:
    """Pass 1 is a calibration. Its failure is the one that matters most,
    because a probe that cannot see anything reports a clean pass 2."""

    def test_a_pass_1_that_sees_no_server_at_all_is_blocked(self):
        proc = run_probe(pass1=EMPTY, pass2=EMPTY)
        v = verdict(proc)
        assert v["status"] == "blocked"
        assert proc.returncode == 1
        assert "calibrat" in v["reason"].lower()

    def test_a_pass_1_whose_server_has_null_serverinfo_is_blocked(self):
        # The ambiguous record in pass 1 is not a calibration: it is the
        # instrument failing to demonstrate it can see a running server.
        proc = run_probe(pass1=SILENT, pass2=EMPTY)
        v = verdict(proc)
        assert v["status"] == "blocked"
        assert proc.returncode == 1

    def test_a_pass_1_with_a_server_but_no_tools_is_blocked(self):
        one_server_no_tools = json.dumps([{
            "name": "node_repl",
            "serverInfo": {"name": "node_repl", "version": "1.0.0"},
            "authStatus": "unsupported",
            "tools": {},
        }])
        proc = run_probe(pass1=one_server_no_tools, pass2=EMPTY)
        v = verdict(proc)
        assert v["status"] == "blocked"
        assert proc.returncode == 1

    def test_a_calibrated_pass_1_with_an_empty_pass_2_is_clean(self):
        proc = run_probe(pass1=HEALTHY, pass2=EMPTY)
        v = verdict(proc)
        assert v["status"] == "clean"
        assert proc.returncode == 0


class TestAnUnexpectedToolBlocks:
    """The DETECTION direction. It does not depend on telling removal from
    silence, which is why it is the only direction stated as a finding."""

    def test_a_surviving_tool_outside_the_allowlist_blocks_and_is_named(self):
        proc = run_probe(pass1=HEALTHY, pass2=HEALTHY)
        v = verdict(proc)
        assert v["status"] == "blocked"
        assert proc.returncode == 1
        assert "js" in v["reason"]

    def test_every_unexpected_tool_is_named_not_just_the_first(self):
        proc = run_probe(pass1=HEALTHY, pass2=HEALTHY)
        v = verdict(proc)
        for name in ("js", "js_add_node_module_dir", "js_reset"):
            assert name in v["reason"], name + " missing from: " + v["reason"]

    def test_a_tool_on_a_second_server_is_also_caught(self):
        proc = run_probe(pass1=HEALTHY, pass2=TWO_SERVERS)
        v = verdict(proc)
        assert v["status"] == "blocked"
        assert "app_open" in v["reason"]


class TestTheAbsenceDirectionIsReportedAsAMitigation:
    """A clean report must never read as proof of removal. The record it
    writes is what a debate record will quote, so the wording is a
    contract, not a courtesy."""

    def test_a_clean_report_states_the_absence_is_unresolved(self):
        proc = run_probe(pass1=HEALTHY, pass2=EMPTY)
        v = verdict(proc)
        assert v["status"] == "clean"
        text = json.dumps(v).lower()
        assert "mitigation" in text
        assert "isolation" not in text.replace("tool_surface_isolation", "")

    def test_a_clean_report_distinguishes_silent_from_absent(self):
        # pass 2 reporting the AMBIGUOUS record, rather than no server at
        # all, is still clean under an empty allowlist - and the report
        # must say the server was present but silent, not that it was gone.
        proc = run_probe(pass1=HEALTHY, pass2=SILENT)
        v = verdict(proc)
        assert v["status"] == "clean"
        assert "silent" in json.dumps(v).lower()


class TestEveryTransportFailureDirectionBlocks:
    """An unmade, failed or unreadable measurement is never a clean one.
    Each of these produced, or could produce, an empty tool list, which
    under an empty allowlist is exactly what a clean run looks like."""

    def test_a_non_zero_exit_blocks(self):
        proc = run_probe(exit_code=7)
        v = verdict(proc)
        assert v["status"] == "blocked"
        assert proc.returncode == 1

    def test_a_server_that_writes_no_frames_blocks(self):
        proc = run_probe(mode="noframes")
        v = verdict(proc)
        assert v["status"] == "blocked"
        assert proc.returncode == 1

    def test_malformed_json_blocks_rather_than_parsing_to_empty(self):
        proc = run_probe(mode="malformed")
        v = verdict(proc)
        assert v["status"] == "blocked"
        assert proc.returncode == 1

    def test_an_rpc_error_reply_blocks(self):
        proc = run_probe(mode="rpcerror")
        v = verdict(proc)
        assert v["status"] == "blocked"
        assert proc.returncode == 1

    def test_a_server_that_dies_after_initialize_blocks(self):
        proc = run_probe(mode="dieafterinit")
        v = verdict(proc)
        assert v["status"] == "blocked"
        assert proc.returncode == 1

    def test_a_hanging_server_blocks_on_the_timeout(self):
        proc = run_probe(mode="hang", hang_secs=45,
                         extra=["-TimeoutSeconds", "5"], timeout=120)
        v = verdict(proc)
        assert v["status"] == "blocked"
        assert proc.returncode == 1
        assert "timeout" in v["reason"].lower() or "timed out" in v["reason"].lower()


class TestTheLauncherResolution:
    """Process.Start cannot execute what a shell can.

    Measured 2026-08-11: `codex` on this machine resolves to codex.ps1,
    codex.cmd AND an extensionless codex, with NO codex.exe. Process.Start
    with UseShellExecute=false launches none of them directly, and
    `Get-Command | Select -First 1` returns whichever the host ranks
    first, which differs between Windows PowerShell and pwsh.

    The probe's first version special-cased only .ps1 and passed here by
    luck. Another session on the SAME MACHINE hit the .cmd and the probe
    failed three times before the cause was found - a defect that shipped
    green because every test drove the one form that happened to work.
    """

    def test_a_cmd_launcher_starts(self):
        cmd_stub = STUB.with_suffix(".cmd")
        assert cmd_stub.exists(), "the .cmd stub is the point of this case"
        env = dict(os.environ)
        env["PARALLAX_STUB_AS_PASS1"] = HEALTHY
        env["PARALLAX_STUB_AS_PASS2"] = EMPTY
        proc = subprocess.run(
            [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(PROBE),
             "-CodexCommand", str(cmd_stub), "-Json"],
            capture_output=True, text=True, env=env, timeout=180)
        v = verdict(proc)
        assert v["status"] == "clean", v
        assert proc.returncode == 0

    def test_an_unlaunchable_command_blocks_rather_than_reporting_nothing(self):
        # The failure direction. A probe that cannot start has measured
        # nothing, and "no tools" from a process that never ran is exactly
        # the false-clean this script exists to refuse.
        env = dict(os.environ)
        env["PARALLAX_STUB_AS_PASS1"] = HEALTHY
        env["PARALLAX_STUB_AS_PASS2"] = EMPTY
        proc = subprocess.run(
            [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(PROBE),
             "-CodexCommand", "parallax-no-such-client", "-Json"],
            capture_output=True, text=True, env=env, timeout=180)
        v = verdict(proc)
        assert v["status"] == "blocked"
        assert proc.returncode == 1


class TestTheFramesGoOutIntactOnBothHosts:
    """The probe failed BY CONSTRUCTION on one of the two supported hosts,
    and twenty green cases said otherwise.

    Measured 2026-08-11. .NET Framework builds Process.StandardInput from
    Console.InputEncoding; this machine's console is UTF-8, whose encoder
    carries a three-byte preamble, and StreamWriter emits it before the
    first write:

        Windows PowerShell 5.1   EF BB BF 7B 22 69 64 ...
        pwsh 7                            7B 22 69 64 ...

    So under 5.1 the real app server received `<BOM>{"id":1,...}`, which is
    not JSON. The suite stayed green because the stub caught the parse
    error and answered the later polls anyway - a lenient stub certifying a
    broken instrument. The stub now exits 9 on a first frame that does not
    begin with `{`, which is what makes every other case in this module a
    guard as well.

    This case is the one that does not depend on which host the suite
    happened to pick: it drives EVERY host present. `CLAUDE.md` states the
    rule it enforces - a green suite on one host proves one interpreter.
    """

    def test_the_first_frame_reaches_the_server_with_no_byte_order_mark(self):
        hosts = [h for h in (shutil.which("powershell"), shutil.which("pwsh"))
                 if h]
        assert hosts, "no PowerShell host at all"
        env = dict(os.environ)
        env["PARALLAX_STUB_AS_PASS1"] = HEALTHY
        env["PARALLAX_STUB_AS_PASS2"] = EMPTY
        for host in hosts:
            proc = subprocess.run(
                [host, "-NoProfile", "-NonInteractive", "-File", str(PROBE),
                 "-CodexCommand", str(STUB), "-Json"],
                capture_output=True, text=True, env=env, timeout=180)
            v = verdict(proc)
            assert v["status"] == "clean", (
                host + " did not get a clean run: " + json.dumps(v) +
                " / stderr: " + proc.stderr)


class TestTheInvocationContract:
    """Pass 2 must carry the flags the real dispatch carries. A probe that
    measured a configuration the reviewer never receives is measuring
    nothing."""

    def test_pass_1_omits_the_isolation_flags_and_pass_2_carries_them(self):
        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / "calls.jsonl"
            run_probe(pass1=HEALTHY, pass2=EMPTY, log=log)
            calls = [json.loads(ln) for ln in
                     log.read_text(encoding="utf-8").splitlines() if ln.strip()]
        assert len(calls) == 2, "expected exactly two passes, got " + str(len(calls))
        first, second = calls
        assert "--disable" not in first, first
        assert "--disable" in second, second
        assert "plugins" in second and "apps" in second

    def test_pass_2_disables_the_surviving_mcp_server(self):
        # Shape A. Measured 2026-08-11 to take the surviving server to zero
        # reported tools; `-c mcp_servers={}` was measured to be INERT and
        # must never appear here in its place.
        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / "calls.jsonl"
            run_probe(pass1=HEALTHY, pass2=EMPTY, log=log)
            calls = [json.loads(ln) for ln in
                     log.read_text(encoding="utf-8").splitlines() if ln.strip()]
        second = " ".join(calls[1])
        assert "mcp_servers.node_repl.enabled=false" in second, second
        assert "mcp_servers={}" not in second, (
            "the inert lever must never ship as a control: " + second)

    def test_both_passes_run_app_server_over_stdio(self):
        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / "calls.jsonl"
            run_probe(pass1=HEALTHY, pass2=EMPTY, log=log)
            calls = [json.loads(ln) for ln in
                     log.read_text(encoding="utf-8").splitlines() if ln.strip()]
        for call in calls:
            assert "app-server" in call
            assert "--stdio" in call
