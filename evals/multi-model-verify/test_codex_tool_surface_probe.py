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


# A feature record in the shape the app server reports one. Copied in SHAPE
# only. `memories` is here because backlog item 7 names it beside the MCP
# tools: the tool list cannot answer that half of the item, and the first
# shipped probe never asked for this surface at all.
FEATURES = json.dumps([
    {"name": "memories", "enabled": True},
    {"name": "plugins", "enabled": True},
    {"name": "apps", "enabled": True},
    {"name": "some_other_feature", "enabled": False},
])

# The same surface as the dispatch pass resolves it: every feature the
# dispatch disables comes back reported and FALSE. This is what the live
# 2026-08-14 reading showed on both hosts, and it is the only shape that
# may reach a clean verdict now that those features are policed.
DISABLED_FEATURES = json.dumps([
    {"name": "memories", "enabled": False},
    {"name": "plugins", "enabled": False},
    {"name": "apps", "enabled": False},
    {"name": "some_other_feature", "enabled": False},
])


def run_probe(pass1=HEALTHY, pass2=EMPTY, mode=None, exit_code=None,
              hang_secs=None, extra=(), log=None, timeout=90,
              features1=None, features2=None):
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
    if features1 is not None:
        env["PARALLAX_STUB_AS_FEATURES1"] = features1
    if features2 is not None:
        env["PARALLAX_STUB_AS_FEATURES2"] = features2
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

    def test_calibration_needs_one_server_that_is_running_AND_has_a_tool(self):
        # Fable whole-branch review, minor 4. Counting running servers and
        # tools as two INDEPENDENT facts lets a tool-less running server
        # plus a silent server that reports tools satisfy the calibration
        # between them - two half-measurements reported as one. No measured
        # record has this shape, which is exactly why the code must not
        # depend on that staying true.
        split = json.dumps([
            {
                "name": "codex_apps",
                "serverInfo": {"name": "codex_apps", "version": "1.0.0"},
                "authStatus": "unsupported",
                "tools": {},
            },
            {
                "name": "node_repl",
                "serverInfo": None,
                "authStatus": "unsupported",
                "tools": {"js": {}},
            },
        ])
        proc = run_probe(pass1=split, pass2=EMPTY)
        v = verdict(proc)
        assert v["status"] == "blocked", v
        assert proc.returncode == 1
        assert "calibrat" in v["reason"].lower()

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

    def test_the_reported_dispatch_tool_count_is_measured_not_assumed(self):
        # Fable whole-branch review, minor 5. `dispatch_tools` was the
        # constant 0, which is exact under the shipped EMPTY allowlist and
        # false the day a caller widens it: the reviewer would hold the
        # allowed tools while the record a debate quotes said zero.
        # ONE allowed tool, deliberately. Measured while writing this case:
        # under `powershell -File`, `-AllowTool a,b,c` arrives as a SINGLE
        # string element rather than three, so a multi-value allowlist
        # passed that way matches nothing and every tool blocks. That
        # direction fails SAFE - it over-blocks, it never over-permits - so
        # it is recorded here rather than worked around.
        one_tool = json.dumps([{
            "name": "node_repl",
            "serverInfo": {"name": "node_repl", "version": "1.0.0"},
            "authStatus": "unsupported",
            "tools": {"js": {}},
        }])
        proc = run_probe(pass1=HEALTHY, pass2=one_tool, extra=["-AllowTool", "js"])
        v = verdict(proc)
        assert v["status"] == "clean", v
        assert v["dispatch_tools"] == 1, v

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

    def test_garbage_before_a_valid_frame_blocks(self):
        # Diff debate round 1, claim 1. A non-blank line that is not a
        # JSON-RPC frame used to be SKIPPED, so garbage followed by a
        # perfectly valid response read as CLEAN, and garbage alone blocked
        # with the untrue reason "wrote no frames at all". Every non-blank
        # line on this stream is meant to be a frame.
        proc = run_probe(mode="garbage")
        v = verdict(proc)
        assert v["status"] == "blocked", v
        assert proc.returncode == 1
        assert "readable JSON-RPC frame" in v["reason"], v["reason"]

    def test_a_result_with_no_data_member_blocks(self):
        # Diff debate round 1, claim 1. `{"id":101,"result":{}}` is
        # well-formed JSON with the right id and NO surface in it. It used
        # to become an empty surface and reach the clean report: a response
        # that carries no surface is not a surface of nothing.
        proc = run_probe(mode="nodata")
        v = verdict(proc)
        assert v["status"] == "blocked", v
        assert proc.returncode == 1
        assert "no data member" in v["reason"], v["reason"]

    def test_a_silent_feature_surface_blocks(self):
        proc = run_probe(mode="features-silent")
        v = verdict(proc)
        assert v["status"] == "blocked", v
        assert "experimentalFeature/list" in v["reason"], v["reason"]

    def test_a_feature_rpc_error_blocks(self):
        proc = run_probe(mode="features-rpcerror")
        v = verdict(proc)
        assert v["status"] == "blocked", v
        assert "experimentalFeature/list" in v["reason"], v["reason"]

    def test_a_feature_result_with_no_data_blocks(self):
        proc = run_probe(mode="features-nodata")
        v = verdict(proc)
        assert v["status"] == "blocked", v
        assert "no data member" in v["reason"], v["reason"]

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

    def test_a_cmd_launcher_in_a_path_with_a_metacharacter_starts(self):
        # Diff debate round 1, claim 3. The batch branch hands the path to
        # `cmd.exe /c`, which RE-PARSES it, and the argument builder quoted
        # only on whitespace. A legal directory called `a & b` with an
        # ampersand in it therefore arrived as a command separator. The .cmd
        # case above uses the fixture's ordinary path and could never catch
        # it.
        stub_dir = STUB.parent
        with tempfile.TemporaryDirectory() as td:
            odd = Path(td) / "a & b (x)"
            odd.mkdir()
            for name in ("stub-appserver.ps1", "stub-appserver.cmd"):
                shutil.copy(stub_dir / name, odd / name)
            env = dict(os.environ)
            env["PARALLAX_STUB_AS_PASS1"] = HEALTHY
            env["PARALLAX_STUB_AS_PASS2"] = EMPTY
            proc = subprocess.run(
                [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(PROBE),
                 "-CodexCommand", str(odd / "stub-appserver.cmd"), "-Json"],
                capture_output=True, text=True, env=env, timeout=180)
            v = verdict(proc)
            assert v["status"] == "clean", (
                "a path with a cmd metacharacter did not start: "
                + json.dumps(v) + " / stderr: " + proc.stderr)

    def test_a_cmd_launcher_in_a_path_with_a_percent_sign_blocks(self):
        # Diff debate round 2. The metacharacter regex above covers
        # `&|<>^()` and NOT `%`, and percent is the one cmd.exe expands
        # while parsing - inside double quotes as well, so the quoting that
        # fixed `a & b (x)` cannot touch it, and `%%` only escapes inside a
        # batch FILE. A directory named with a `%NAME%` sequence would
        # therefore launch a DIFFERENT path from the one resolved, and
        # whatever that produced would be reported as a measurement of the
        # real client.
        #
        # So the direction here is BLOCKED, not clean. That is the whole
        # point: an instrument that cannot be aimed has measured nothing,
        # and this is the one case in this class that must not start.
        stub_dir = STUB.parent
        with tempfile.TemporaryDirectory() as td:
            odd = Path(td) / "pct %PATH% dir"
            odd.mkdir()
            for name in ("stub-appserver.ps1", "stub-appserver.cmd"):
                shutil.copy(stub_dir / name, odd / name)
            env = dict(os.environ)
            env["PARALLAX_STUB_AS_PASS1"] = HEALTHY
            env["PARALLAX_STUB_AS_PASS2"] = EMPTY
            proc = subprocess.run(
                [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(PROBE),
                 "-CodexCommand", str(odd / "stub-appserver.cmd"), "-Json"],
                capture_output=True, text=True, env=env, timeout=180)
            v = verdict(proc)
            assert v["status"] == "blocked", (
                "a path carrying a percent sign must not be launched: "
                + json.dumps(v) + " / stderr: " + proc.stderr)
            assert proc.returncode == 1
            assert "percent" in v["reason"], v

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


class TestTheFeatureSurfaceIsReadAtAll:
    """The frozen plan's task 1 named TWO JSON-RPC methods and the first
    shipped probe sent one.

    That is spec drift, and it was found by the diff debate rather than by
    any test here. It is not a formality: backlog item 7's problem
    statement names the memories feature beside the MCP tools, so a probe
    that reads only tools answers half the item and reports nothing at all
    about the other half.
    """

    def test_the_feature_surface_is_requested_and_reported(self):
        # The baseline may hold memories enabled - that is the state the
        # 2026-08-12 live reading found and the reason the flag exists. What
        # the dispatch may hold is a different question, below.
        proc = run_probe(pass1=HEALTHY, pass2=EMPTY,
                         features1=FEATURES, features2=DISABLED_FEATURES)
        v = verdict(proc)
        assert v["status"] == "clean", v
        assert "memories=True" in v["baseline_features"], v
        assert "memories=False" in v["dispatch_features"], v

    def test_the_feature_report_states_what_it_did_and_did_not_judge(self):
        # No allowlist of acceptable features exists, so nothing beyond the
        # disabled ones may read as acceptance. A record that lists an
        # enabled feature without saying it was not judged is exactly the
        # kind of quiet promotion this repo keeps finding in its own text.
        proc = run_probe(pass1=HEALTHY, pass2=EMPTY,
                         features1=FEATURES, features2=DISABLED_FEATURES)
        v = verdict(proc)
        assert "seen rather than accepted" in v["feature_note"], v
        # ...and it must NOT claim the probe judged nothing, because it now
        # judges exactly the disabled ones.
        assert "memories" in v["feature_note"], v


class TestTheDisabledFeaturesArePoliced:
    """Round 1 accepted a fix asking for an enabled-feature policy and a
    fail-first case for an unexpectedly enabled feature. Only the reading
    half was built, and the fixture then fed `memories=True` into pass 2 and
    asserted a CLEAN verdict - a test certifying the exact state that should
    stop a round. Found by the diff debate at round 2.

    This direction is sound where absence is not. A feature reported ENABLED
    after the dispatch disabled it is present and observed, so it needs no
    ability to tell a disabled server from a crashed one. It says the flag
    did not take effect.
    """

    def test_a_disabled_feature_reported_enabled_blocks(self):
        # ONLY memories is left enabled, so the case names the feature it
        # actually tests. Feeding an all-enabled surface here trips
        # `plugins` first and the assertion would pass or fail on which
        # name the loop reaches first rather than on the behaviour.
        memories_on = json.dumps([
            {"name": "plugins", "enabled": False},
            {"name": "apps", "enabled": False},
            {"name": "memories", "enabled": True},
        ])
        proc = run_probe(pass1=HEALTHY, pass2=EMPTY,
                         features1=FEATURES, features2=memories_on)
        v = verdict(proc)
        assert v["status"] == "blocked", v
        assert proc.returncode == 1
        assert "memories=True" in v["reason"], v
        assert "did NOT take effect" in v["reason"], v

    def test_a_disabled_feature_the_surface_never_reports_blocks(self):
        # Silence is not a disabled feature. Whether the flag took effect is
        # simply unmeasured, and an unmade measurement is never a clean one.
        no_memories = json.dumps([
            {"name": "plugins", "enabled": False},
            {"name": "apps", "enabled": False},
        ])
        proc = run_probe(pass1=HEALTHY, pass2=EMPTY,
                         features1=FEATURES, features2=no_memories)
        v = verdict(proc)
        assert v["status"] == "blocked", v
        assert proc.returncode == 1
        assert "memories" in v["reason"], v
        assert "UNMEASURED" in v["reason"], v

    def test_a_disabled_feature_with_a_non_boolean_value_blocks(self):
        # `"false"` is a STRING and is truthy in PowerShell. Read as a
        # value it would pass for disabled while meaning nothing of the
        # kind, so the type is checked rather than the truthiness.
        stringly = json.dumps([
            {"name": "plugins", "enabled": False},
            {"name": "apps", "enabled": False},
            {"name": "memories", "enabled": "false"},
        ])
        proc = run_probe(pass1=HEALTHY, pass2=EMPTY,
                         features1=FEATURES, features2=stringly)
        v = verdict(proc)
        assert v["status"] == "blocked", v
        assert proc.returncode == 1
        assert "non-boolean" in v["reason"], v

    def test_a_disabled_feature_carrying_no_enablement_member_blocks(self):
        nameless = json.dumps([
            {"name": "plugins", "enabled": False},
            {"name": "apps", "enabled": False},
            {"name": "memories"},
        ])
        proc = run_probe(pass1=HEALTHY, pass2=EMPTY,
                         features1=FEATURES, features2=nameless)
        v = verdict(proc)
        assert v["status"] == "blocked", v
        assert "no enabled/isEnabled/value member" in v["reason"], v

    def test_a_disabled_feature_reported_twice_blocks(self):
        # Two records for one name: which one describes the reviewer cannot
        # be read, so neither is taken.
        doubled = json.dumps([
            {"name": "plugins", "enabled": False},
            {"name": "apps", "enabled": False},
            {"name": "memories", "enabled": False},
            {"name": "memories", "enabled": True},
        ])
        proc = run_probe(pass1=HEALTHY, pass2=EMPTY,
                         features1=FEATURES, features2=doubled)
        v = verdict(proc)
        assert v["status"] == "blocked", v
        assert "memories" in v["reason"], v

    def test_the_policed_list_is_derived_from_the_flags_actually_sent(self):
        # plugins and apps are disabled by the same dispatch, so they are
        # policed on the same terms as memories. If this ever stops being
        # true, the policy has been narrowed to one hardcoded name.
        plugins_on = json.dumps([
            {"name": "plugins", "enabled": True},
            {"name": "apps", "enabled": False},
            {"name": "memories", "enabled": False},
        ])
        proc = run_probe(pass1=HEALTHY, pass2=EMPTY,
                         features1=FEATURES, features2=plugins_on)
        v = verdict(proc)
        assert v["status"] == "blocked", v
        assert "plugins=True" in v["reason"], v


class TestANullSurfaceIsNotAnEmptyOne:
    """`{"result":{"data":null}}` is the third reading of this rule and the
    first two were both false-cleans. Member presence alone let it through,
    and the reducers then walked `@($null)` - a ONE-ELEMENT array holding
    $null, the same PowerShell trap this fixture already documents for
    `tools: {}` - skipped the single element, and reported an empty surface
    as a clean one. Found by the diff debate at round 2.

    Distinct from the `nodata` case: this shape PASSES the check that stops
    that one, which is why it needs its own fixture and its own case.
    """

    def test_a_status_result_whose_data_is_null_blocks(self):
        proc = run_probe(pass1=HEALTHY, pass2=EMPTY, mode="datanull")
        v = verdict(proc)
        assert v["status"] == "blocked", v
        assert proc.returncode == 1
        # The reason must describe the fault that HAPPENED. An earlier
        # version of this case required the words "no data member" for a
        # response whose data member was present and null - a test locking
        # in a message that would send a reader to the wrong place. Diff
        # debate, round 3.
        assert "null" in v["reason"], v
        assert "no data member" not in v["reason"], v

    def test_a_missing_data_member_and_a_null_one_report_different_reasons(self):
        # The two were collapsed into one flag. They are different faults:
        # one response never carried a surface, the other carried one and
        # said it was nothing.
        missing = verdict(run_probe(pass1=HEALTHY, pass2=EMPTY, mode="nodata"))
        null_data = verdict(run_probe(pass1=HEALTHY, pass2=EMPTY, mode="datanull"))
        assert missing["status"] == "blocked", missing
        assert null_data["status"] == "blocked", null_data
        assert "no data member" in missing["reason"], missing
        assert missing["reason"] != null_data["reason"], (missing, null_data)

    def test_a_feature_result_whose_data_is_null_blocks(self):
        # The feature surface has no calibration pass behind it, so a null
        # here would have reached the clean report on its own.
        proc = run_probe(pass1=HEALTHY, pass2=EMPTY, mode="features-datanull")
        v = verdict(proc)
        assert v["status"] == "blocked", v
        assert proc.returncode == 1
        assert "experimentalFeature/list" in v["reason"], v


class TestEveryFeatureEntryIsReadable:
    """Round 2's accepted fix asked for readable feature-entry schema and
    only the policed names were ever checked, so a malformed entry ANYWHERE
    ELSE in the list still reached the clean report. That is the same
    half-built-fix shape as the policy itself, one level down. Found by the
    diff debate at round 3.

    Deliberately strict, and the direction is safe: all 92 features in the
    live 2026-08-14 reading carry a non-empty string name and a real
    boolean, so a future entry that does not blocks loudly instead of being
    silently reduced.
    """

    def _pass2_with(self, extra_entry):
        return json.dumps([
            {"name": "plugins", "enabled": False},
            {"name": "apps", "enabled": False},
            {"name": "memories", "enabled": False},
            extra_entry,
        ])

    def test_an_unpoliced_entry_with_no_name_blocks(self):
        proc = run_probe(pass1=HEALTHY, pass2=EMPTY, features1=FEATURES,
                         features2=self._pass2_with({"enabled": True}))
        v = verdict(proc)
        assert v["status"] == "blocked", v
        assert "no usable name" in v["reason"], v

    def test_an_unpoliced_entry_with_a_non_boolean_enablement_blocks(self):
        proc = run_probe(
            pass1=HEALTHY, pass2=EMPTY, features1=FEATURES,
            features2=self._pass2_with({"name": "something", "enabled": "yes"}))
        v = verdict(proc)
        assert v["status"] == "blocked", v
        assert "non-boolean" in v["reason"], v
        assert "something" in v["reason"], v

    def test_an_unpoliced_entry_with_no_enablement_member_blocks(self):
        proc = run_probe(pass1=HEALTHY, pass2=EMPTY, features1=FEATURES,
                         features2=self._pass2_with({"name": "something"}))
        v = verdict(proc)
        assert v["status"] == "blocked", v
        assert "never reported" in v["reason"], v

    def test_a_feature_data_that_is_a_bare_object_blocks(self):
        # `@(...)` wraps a single object into a one-element list, so a
        # server answering with one bare object where a list belongs was
        # accepted and could reach CLEAN. Round 3 asked for `data` to be
        # validated as the expected collection and the coercion was left
        # in. Diff debate, round 4.
        #
        # THE BARE OBJECT GOES IN THE BASELINE, and that placement is the
        # whole case. A first version put it in pass 2, where it DID go red
        # against the pre-fix code - but for the wrong reason: a pass-2
        # object supplying only `memories` still failed the disabled-feature
        # policy on the missing `plugins` and `apps`, so the red proved the
        # policy worked, not that the coercion was a false clean. A test is
        # not evidence until it fails for the reason it CLAIMS, and that one
        # did not. Round 5 caught it. Here pass 2 is valid, so the pre-fix
        # code reaches a CLEAN report off a malformed baseline - which is
        # the defect.
        proc = run_probe(pass1=HEALTHY, pass2=EMPTY,
                         features1=json.dumps({"name": "memories",
                                               "enabled": True}),
                         features2=DISABLED_FEATURES)
        v = verdict(proc)
        assert v["status"] == "blocked", v
        assert "not a list" in v["reason"], v
        assert "pass 1" in v["reason"], v

    def test_a_feature_with_two_enablement_members_blocks(self):
        # `enabled:false` AND `value:true` - the surface says two different
        # things about one feature. Taking the first alias certified it as
        # disabled. Round 3 asked for an UNAMBIGUOUS field and this took
        # the first match instead.
        ambiguous = json.dumps([
            {"name": "plugins", "enabled": False},
            {"name": "apps", "enabled": False},
            {"name": "memories", "enabled": False, "value": True},
        ])
        proc = run_probe(pass1=HEALTHY, pass2=EMPTY,
                         features1=FEATURES, features2=ambiguous)
        v = verdict(proc)
        assert v["status"] == "blocked", v
        assert "ambiguous" in v["reason"], v
        assert "memories" in v["reason"], v

    def test_a_null_entry_in_the_feature_list_blocks(self):
        # `@($null)` skipped it in silence, so a list with a hole in it read
        # as a shorter list rather than an unreadable one.
        proc = run_probe(pass1=HEALTHY, pass2=EMPTY, features1=FEATURES,
                         features2=self._pass2_with(None))
        v = verdict(proc)
        assert v["status"] == "blocked", v
        assert "null entry" in v["reason"], v


class TestTheDisabledNameIsMatchedCaseSensitively:
    """PowerShell's `-eq` is case-INSENSITIVE, so `Memories=False` satisfied
    a requirement derived from `--disable memories`. Round 2 DECLARED the
    limit that a flag name not matching a feature name must fail as "never
    reported"; `-eq` quietly made one whole class of mismatch match instead,
    so the code did not do what its own declared limit said. Found by the
    diff debate at round 3.
    """

    def test_a_differently_cased_feature_name_is_treated_as_missing(self):
        mixed = json.dumps([
            {"name": "plugins", "enabled": False},
            {"name": "apps", "enabled": False},
            {"name": "Memories", "enabled": False},
        ])
        proc = run_probe(pass1=HEALTHY, pass2=EMPTY,
                         features1=FEATURES, features2=mixed)
        v = verdict(proc)
        assert v["status"] == "blocked", v
        assert "memories" in v["reason"], v
        assert "UNMEASURED" in v["reason"], v


class TestTheTwoIdRangesCannotCollide:
    """Status ids were 100+n and feature ids 200+n, read back as the fixed
    windows 100-199 and 200-299, while -PollCount accepted any integer. At
    101 polls the 101st status id is 201 - inside the FEATURE window - so a
    status answer would be read as the feature surface. Found by the diff
    debate at round 2.

    The bases are now derived from the poll count and handed to the reader,
    so the windows cannot drift out of step with the ids at any value.
    """

    def test_a_poll_count_past_the_old_window_still_reads_both_surfaces(self):
        # 101 is the first count that collided. The interval is dropped to
        # 1ms so the case measures the id arithmetic and not the clock.
        proc = run_probe(pass1=HEALTHY, pass2=EMPTY,
                         features1=FEATURES, features2=DISABLED_FEATURES,
                         extra=["-PollCount", "101", "-PollIntervalMs", "1"])
        v = verdict(proc)
        assert v["status"] == "clean", v
        # The feature surface must still be the FEATURE surface: a status
        # answer read through the feature window would carry no feature
        # names at all.
        assert "memories=False" in v["dispatch_features"], v
        assert v["baseline_tools"] > 0, v


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

    def test_pass_2_disables_the_reviewers_cross_session_memory(self):
        # The probe is worth nothing if pass 2 models a configuration the
        # reviewer never receives. The review dispatch carries
        # `--disable memories`, so this pass must too.
        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / "calls.jsonl"
            run_probe(pass1=HEALTHY, pass2=EMPTY, log=log)
            calls = [json.loads(ln) for ln in
                     log.read_text(encoding="utf-8").splitlines() if ln.strip()]
        first, second = " ".join(calls[0]), " ".join(calls[1])
        assert "memories" in second, second
        assert "memories" not in first, (
            "pass 1 is the BASELINE and must carry no isolation flag: " + first)

    def test_both_passes_run_app_server_over_stdio(self):
        with tempfile.TemporaryDirectory() as td:
            log = Path(td) / "calls.jsonl"
            run_probe(pass1=HEALTHY, pass2=EMPTY, log=log)
            calls = [json.loads(ln) for ln in
                     log.read_text(encoding="utf-8").splitlines() if ln.strip()]
        for call in calls:
            assert "app-server" in call
            assert "--stdio" in call
