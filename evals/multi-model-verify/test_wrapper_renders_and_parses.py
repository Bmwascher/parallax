"""Render, parse and stub-run every wrapper body (Task 7, 2026-08-30
item32-detached-dispatch plan).

Task 1's suite drives the real `tools/dispatch-round.ps1` transaction
end to end, so it already covers reserve-write-launch-record. What it
does NOT cover is whether the five COPIED wrapper bodies these skill
documents embed - two under SKILL.md's new `<!-- wrapper:... -->`
markers, three under Task 4's `<!-- call:... -->` sections in
backup-lane.md - are themselves well-formed PowerShell that behaves
correctly once a client stub stands in for `codex`/`<kimi-code-binary>`.
A wrapper body that will not parse still passes every string pin in
test_multi_model_verify.py and test_backup_lane.py, because those tests
only check for SUBSTRINGS.

This module extracts each body from the REAL documents (never a copy
pasted into this file, which would drift silently), substitutes its
`<placeholder>` tokens with real values, and:

  - parses the rendered body with the exact
    [System.Management.Automation.Language.Parser]::ParseFile snippet
    the task specifies, on whichever host PARALLAX_PS_HOST names;
  - runs it for real against a stub client, per lane, because the two
    lanes produce their reply differently (codex's client writes its own
    reply via --output-last-message; the Kimi wrapper writes the reply
    ITSELF from captured stdout).

The wrapper bodies are run DIRECTLY via `powershell -File`, never through
`tools/dispatch-round.ps1` - Task 1's suite already drives that
transaction, and running the wrapper here with $PSScriptRoot bound to a
throwaway directory is exactly what proves the copied body itself is
sound, independent of the launch mechanism around it.

WINDOWS ONLY, whole module: same reasoning as test_dispatch_round.py -
a selector that merely finds A host would collect these on a
non-Windows box too, where the platform semantics under test (native
process console-decode boundary, OEM code page) do not exist the same
way. A green suite on one host proves ONE interpreter.
"""
import base64
import hashlib
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
SKILL_MD = REPO / "skills" / "multi-model-verify" / "SKILL.md"
BACKUP_LANE = REPO / "skills" / "multi-model-verify" / "references" / "backup-lane.md"

POWERSHELL = (os.environ.get("PARALLAX_PS_HOST")
              or shutil.which("powershell") or shutil.which("pwsh"))

pytestmark = pytest.mark.skipif(
    os.name != "nt" or POWERSHELL is None,
    reason="the wrapper bodies are PowerShell scripts run against a real "
           "Windows host's native-process console-decode boundary")

# One entry per wrapper body this task covers. The two codex ones sit
# under markers Step 1 of this task adds; the three Kimi ones reuse Task
# 4's own `<!-- call:... -->` sections rather than adding a second marker
# beside them.
WRAPPERS = {
    "codex-fresh": (SKILL_MD, "<!-- wrapper:codex-fresh -->"),
    "codex-resume": (SKILL_MD, "<!-- wrapper:codex-resume -->"),
    "kimi-dispatch": (BACKUP_LANE, "<!-- call:kimi-dispatch -->"),
    "kimi-resume": (BACKUP_LANE, "<!-- call:kimi-resume -->"),
    "kimi-write-probe": (BACKUP_LANE, "<!-- call:kimi-write-probe -->"),
}
CODEX_CALLS = ("codex-fresh", "codex-resume")
KIMI_CALLS = ("kimi-dispatch", "kimi-resume", "kimi-write-probe")


# ---------------------------------------------------------------------
# Step 2: extract by marker, from the real documents, through an
# injectable source path.
# ---------------------------------------------------------------------
def extract_wrapper_body(source_path, marker):
    """Return the PowerShell fence immediately following `marker` in
    `source_path`, with the fence's OWN leading indent stripped from
    every line - the transformation a human performs by hand when
    copying the block out of a nested Markdown list item.

    This reproduces that transformation EXPLICITLY: the amount to strip
    is read from the fence-open line itself, and every following line
    must start with exactly that many spaces or the extraction fails
    loudly. `textwrap.dedent` would instead infer the amount from the
    common prefix of every line in the block, which is a guess rather
    than a reproduction of the one rule Markdown list nesting actually
    applies (a fixed left margin per list level).

    `source_path` is a parameter, not a hardcoded document, so a
    scratch copy can be fed to this function - otherwise the "marker
    missing" failure mode could never be demonstrated in this suite
    (round 4's finding).
    """
    text = Path(source_path).read_text(encoding="utf-8")
    count = text.count(marker)
    assert count == 1, (
        "expected exactly one %r in %s, found %d" % (marker, source_path, count))
    after = text.split(marker, 1)[1]
    lines = after.splitlines()

    fence_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("```powershell"):
            fence_idx = i
            break
    assert fence_idx is not None, (
        "no powershell fence follows %r in %s" % (marker, source_path))

    fence_line = lines[fence_idx]
    indent = len(fence_line) - len(fence_line.lstrip(" "))
    prefix = " " * indent

    body_lines = []
    closed = False
    for line in lines[fence_idx + 1:]:
        if line.strip() == "```":
            closed = True
            break
        if line == "":
            body_lines.append("")
        else:
            assert line.startswith(prefix), (
                "line inside the fence following %r is indented less than"
                " the fence's own %d spaces: %r" % (marker, indent, line))
            body_lines.append(line[indent:])
    assert closed, "fence following %r in %s never closes" % (marker, source_path)

    return "\n".join(body_lines) + "\n"


PLACEHOLDER_RE = re.compile(r"<[^<>\n]+>")


def substitute(body, mapping):
    """Reproduce the copy-and-fill-in step a caller performs before
    running a wrapper body: replace every `<placeholder>` token with a
    real value and assert none survives (Step 2's own requirement).
    """
    rendered = body
    for placeholder, value in mapping.items():
        rendered = rendered.replace(placeholder, value)
    leftover = PLACEHOLDER_RE.findall(rendered)
    assert not leftover, "placeholders survived substitution: %r" % (leftover,)
    return rendered


# ---------------------------------------------------------------------
# Render-time value mappings. Real files are created for anything the
# wrapper body reads from disk at runtime (brief, override); everything
# else is a client-invocation argument our stubs ignore, so a plain
# safe token is enough.
# ---------------------------------------------------------------------
def _write_utf8(path, text):
    path.write_bytes(text.encode("utf-8"))
    return path


def codex_mapping(tmp_path, brief_present=True, override_present=True,
                   override_hash_matches=True):
    mapping = {
        "<canonical-model-id>": "stub-model",
        "<canonical-effort>": "low",
        "<SESSION_ID>": "stub-session-1",
    }
    if brief_present:
        mapping["<brief-file>"] = str(
            _write_utf8(tmp_path / "brief.txt", "stub brief text"))
    else:
        mapping["<brief-file>"] = str(tmp_path / "missing-brief.txt")
    if override_present:
        override_path = _write_utf8(tmp_path / "override.txt", '"k"="v"')
        digest = hashlib.sha256(override_path.read_bytes()).hexdigest()
        mapping["<verified-override-file>"] = str(override_path)
        mapping["<override-sha256>"] = digest if override_hash_matches else ("0" * 64)
    else:
        mapping["<verified-override-file>"] = str(tmp_path / "missing-override.txt")
        mapping["<override-sha256>"] = "0" * 64
    return mapping


def kimi_mapping(tmp_path, kimi_binary, brief_present=True):
    mapping = {
        "<kimi-code-binary>": str(kimi_binary),
        "<canonical-backup-model-id>": "stub-backup-model",
        "<plugin-checkout>": str(tmp_path),
        "<debate-home>": str(tmp_path),
        "<session-id>": "stub-session-1",
    }
    if brief_present:
        mapping["<brief-file>"] = str(
            _write_utf8(tmp_path / "brief.txt", "stub brief text"))
    else:
        mapping["<brief-file>"] = str(tmp_path / "missing-brief.txt")
    return mapping


# ---------------------------------------------------------------------
# Step 3: parse each rendered body, with the task's own snippet.
# ---------------------------------------------------------------------
def parse_errors(ps1_path, timeout=30):
    posix_path = str(ps1_path).replace("\\", "/").replace("'", "''")
    cmd = (
        "$errors = $null; "
        "$null = [System.Management.Automation.Language.Parser]::ParseFile("
        "'%s', [ref]$null, [ref]$errors); "
        "if ($errors.Count -gt 0) { $errors | ForEach-Object { $_.Message }; exit 1 }"
        " else { exit 0 }"
    ) % posix_path
    result = subprocess.run(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-Command", cmd],
        capture_output=True, text=True, timeout=timeout)
    messages = [ln for ln in result.stdout.splitlines() if ln.strip()]
    assert (result.returncode == 0) == (not messages), (
        "parse exit code disagrees with the error list: rc=%r messages=%r"
        % (result.returncode, messages))
    return messages


def render(call, tmp_path, mapping):
    source_path, marker = WRAPPERS[call]
    body = extract_wrapper_body(source_path, marker)
    rendered = substitute(body, mapping)
    ps1 = tmp_path / ("wrapper-%s.ps1" % call)
    ps1.write_text(rendered, encoding="utf-8")
    return ps1


def run_wrapper(ps1_path, env_overrides, timeout=60):
    """Run a rendered wrapper body as a genuinely fresh child process.

    A private console matters and is not decoration: without it, a
    console-subsystem child launched from this test process ATTACHES TO
    the ambient console it inherits, and `[Console]::OutputEncoding =`
    (SetConsoleOutputCP under the hood) changes THAT SHARED CONSOLE's
    codepage for every later process attached to it - not just the one
    that set it. Measured here: with a shared console, whichever
    stub-run test happened to set UTF-8 first left the codepage at UTF-8
    for every later test in the same session, so the negative
    demonstration below (deleting the encoding line) intermittently
    passed by accident, on an already-corrected console rather than a
    fresh Windows PowerShell 5.1 default. A hidden new console per call
    is what makes every stub-run test's result depend only on ITS OWN
    wrapper body, not on test execution order.

    CREATE_NO_WINDOW, never CREATE_NEW_CONSOLE. Both give the child its
    own console, so both isolate. Only CREATE_NO_WINDOW does it without
    drawing one. CREATE_NEW_CONSOLE pops a real console per spawn and
    STEALS FOCUS, which across a full run is a storm of windows over
    whatever the user is doing. STARTUPINFO's SW_HIDE does NOT reliably
    suppress it: wShowWindow is advisory for a newly created console,
    and Windows showed them anyway.
    """
    full_env = dict(os.environ)
    full_env.update(env_overrides)
    return subprocess.run(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-File", str(ps1_path)],
        capture_output=True, timeout=timeout, env=full_env,
        creationflags=subprocess.CREATE_NO_WINDOW)


def read_transcript_loosely(path):
    """The `>` redirect that writes the transcript defaults to UTF-16LE
    on Windows PowerShell 5.1 and UTF-8 on PowerShell 7 (backup-lane.md)
    - not this task's concern to fix, only to read past. Try both so a
    marker check works on either host.
    """
    raw = path.read_bytes()
    return (raw.decode("utf-8", errors="ignore")
            + "\x00" + raw.decode("utf-16-le", errors="ignore"))


# ---------------------------------------------------------------------
# Step 4: stub clients.
#
# codex is invoked as a BARE NAME resolved from PATH - PATH shadowing
# works for that shape, so the stub is a .cmd placed first on PATH.
#
# <kimi-code-binary> is substituted with the stub's ABSOLUTE path, so
# PATH shadowing is irrelevant there; what matters is that the stub is a
# NATIVE EXECUTABLE and not a .ps1. `&` on a .ps1 runs it IN-PROCESS, so
# its output never crosses the console decode boundary the byte-exact
# assertion below exists to exercise - the red demonstration would
# simply refuse to appear. A .cmd that shells out to a fresh
# `powershell -File` process (the same shape as
# fixtures/stub-appserver/stub-appserver.cmd, kept for an unrelated
# measured reason) is a genuine child process and crosses that boundary
# for real.
# ---------------------------------------------------------------------
CODEX_STUB_CMD = (
    "@echo off\r\n"
    "echo STUB-CODEX-RAN\r\n"
    "if defined PARALLAX_TEST_CODEX_REPLY_PATH (\r\n"
    "    > \"%PARALLAX_TEST_CODEX_REPLY_PATH%\" echo stub-reply-payload\r\n"
    ")\r\n"
    "exit /b %PARALLAX_TEST_CODEX_EXIT_CODE%\r\n"
)


def make_codex_stub_dir(tmp_path):
    stub_dir = tmp_path / "codex-stub-bin"
    stub_dir.mkdir(exist_ok=True)
    (stub_dir / "codex.cmd").write_text(CODEX_STUB_CMD, encoding="ascii")
    return stub_dir


KIMI_STUB_PS1 = (
    "$code = 0\r\n"
    "if ($env:PARALLAX_TEST_KIMI_EXIT_CODE) { $code = [int]$env:PARALLAX_TEST_KIMI_EXIT_CODE }\r\n"
    "if ($env:PARALLAX_TEST_KIMI_PAYLOAD_B64) {\r\n"
    "    $bytes = [System.Convert]::FromBase64String($env:PARALLAX_TEST_KIMI_PAYLOAD_B64)\r\n"
    "    $stdout = [Console]::OpenStandardOutput()\r\n"
    "    $stdout.Write($bytes, 0, $bytes.Length)\r\n"
    "    $stdout.Flush()\r\n"
    "}\r\n"
    "exit $code\r\n"
)


def make_kimi_stub(tmp_path):
    stub_dir = tmp_path / "kimi-stub-bin"
    stub_dir.mkdir(exist_ok=True)
    (stub_dir / "stub-kimi.ps1").write_text(KIMI_STUB_PS1, encoding="ascii")
    cmd_text = (
        "@echo off\r\n"
        "\"%s\" -NoProfile -NonInteractive -File \"%%~dp0stub-kimi.ps1\" %%*\r\n"
        "exit /b %%ERRORLEVEL%%\r\n"
    ) % POWERSHELL
    (stub_dir / "stub-kimi.cmd").write_text(cmd_text, encoding="ascii")
    return stub_dir / "stub-kimi.cmd"


KIMI_PAYLOAD = "kimi-stub-reply — 中文 \U0001F600"  # em dash, CJK, astral


# ---------------------------------------------------------------------
# Step 1: exactly one match per marker.
# ---------------------------------------------------------------------
@pytest.mark.parametrize("call", list(WRAPPERS))
def test_wrapper_marker_appears_exactly_once(call):
    source_path, marker = WRAPPERS[call]
    text = source_path.read_text(encoding="utf-8")
    assert text.count(marker) == 1, (
        "%s must contain exactly one %r" % (source_path.name, marker))


# ---------------------------------------------------------------------
# Step 2: the extractor's own negative self-test (also Step 5's oracle).
# ---------------------------------------------------------------------
def test_extractor_fails_on_zero_matches_against_a_scratch_copy(tmp_path):
    marker = "<!-- wrapper:codex-fresh -->"
    original = SKILL_MD.read_text(encoding="utf-8")
    assert marker in original
    scratch = tmp_path / "SKILL-scratch.md"
    scratch.write_text(original.replace(marker, ""), encoding="utf-8")

    with pytest.raises(AssertionError, match="found 0"):
        extract_wrapper_body(scratch, marker)

    # The real document is untouched - this ran against a copy only.
    assert SKILL_MD.read_text(encoding="utf-8") == original


@pytest.mark.parametrize("call", list(WRAPPERS))
def test_no_placeholder_survives_substitution(call, tmp_path):
    source_path, marker = WRAPPERS[call]
    body = extract_wrapper_body(source_path, marker)
    if call in CODEX_CALLS:
        mapping = codex_mapping(tmp_path)
    else:
        stub = make_kimi_stub(tmp_path)
        mapping = kimi_mapping(tmp_path, stub)
    rendered = substitute(body, mapping)
    assert PLACEHOLDER_RE.search(rendered) is None


# ---------------------------------------------------------------------
# Step 3: zero parse errors on this host.
# ---------------------------------------------------------------------
@pytest.mark.parametrize("call", list(WRAPPERS))
def test_wrapper_body_parses_on_this_host(call, tmp_path):
    if call in CODEX_CALLS:
        mapping = codex_mapping(tmp_path)
    else:
        stub = make_kimi_stub(tmp_path)
        mapping = kimi_mapping(tmp_path, stub)
    ps1 = render(call, tmp_path, mapping)
    errors = parse_errors(ps1)
    assert errors == [], "parse errors in %s: %r" % (call, errors)


# ---------------------------------------------------------------------
# Step 4: stub-run, codex shape.
# ---------------------------------------------------------------------
@pytest.mark.parametrize("call", list(CODEX_CALLS))
def test_codex_wrapper_exit_zero_writes_reply(call, tmp_path):
    stub_dir = make_codex_stub_dir(tmp_path)
    mapping = codex_mapping(tmp_path)
    ps1 = render(call, tmp_path, mapping)

    env = dict(os.environ)
    env["PATH"] = str(stub_dir) + os.pathsep + env.get("PATH", "")
    env["PARALLAX_TEST_CODEX_EXIT_CODE"] = "0"
    env["PARALLAX_TEST_CODEX_REPLY_PATH"] = str(tmp_path / "reply")

    run_wrapper(ps1, env)

    exit_path = tmp_path / "exit"
    reply_path = tmp_path / "reply"
    transcript_path = tmp_path / "transcript"
    assert exit_path.read_text(encoding="ascii").strip() == "0"
    assert reply_path.exists() and reply_path.stat().st_size > 0, "expected a reply present"
    assert "STUB-CODEX-RAN" in read_transcript_loosely(transcript_path), (
        "the stub's marker is missing from the transcript - either the"
        " real codex client ran instead, or nothing ran at all")


@pytest.mark.parametrize("call", list(CODEX_CALLS))
def test_codex_wrapper_exit_three_writes_nothing(call, tmp_path):
    stub_dir = make_codex_stub_dir(tmp_path)
    mapping = codex_mapping(tmp_path)
    ps1 = render(call, tmp_path, mapping)

    env = dict(os.environ)
    env["PATH"] = str(stub_dir) + os.pathsep + env.get("PATH", "")
    env["PARALLAX_TEST_CODEX_EXIT_CODE"] = "3"

    run_wrapper(ps1, env)

    exit_path = tmp_path / "exit"
    transcript_path = tmp_path / "transcript"
    assert exit_path.read_text(encoding="ascii").strip() == "3"
    assert not (tmp_path / "reply").exists()
    assert "STUB-CODEX-RAN" in read_transcript_loosely(transcript_path), (
        "the stub's marker is missing from the transcript - either the"
        " real codex client ran instead, or nothing ran at all")


@pytest.mark.parametrize("call", list(CODEX_CALLS))
def test_codex_wrapper_pre_client_throw_still_exits_nonzero(call, tmp_path):
    """A mismatched override hash throws BEFORE codex is ever invoked -
    the wrapper's own fail-closed guard, exercised on purpose. The stub
    is still on PATH so a real invocation would be visible; it must
    never happen.
    """
    stub_dir = make_codex_stub_dir(tmp_path)
    mapping = codex_mapping(tmp_path, override_hash_matches=False)
    ps1 = render(call, tmp_path, mapping)

    env = dict(os.environ)
    env["PATH"] = str(stub_dir) + os.pathsep + env.get("PATH", "")
    env["PARALLAX_TEST_CODEX_EXIT_CODE"] = "0"
    env["PARALLAX_TEST_CODEX_REPLY_PATH"] = str(tmp_path / "reply")

    run_wrapper(ps1, env)

    exit_path = tmp_path / "exit"
    assert exit_path.exists()
    code = int(exit_path.read_text(encoding="ascii").strip())
    assert code != 0, "a pre-client throw must still exit non-zero"
    assert not (tmp_path / "reply").exists(), "the stub must never have run"


# ---------------------------------------------------------------------
# Step 4: stub-run, Kimi shape.
# ---------------------------------------------------------------------
@pytest.mark.parametrize("call", list(KIMI_CALLS))
def test_kimi_wrapper_reply_bytes_match_the_payload_exactly(call, tmp_path):
    """The oracle for the `[Console]::OutputEncoding` line: restoring
    the defective `> $PSScriptRoot\\reply` satisfied every other
    assertion in Tasks 4 and 7, so this is what actually exercises it.
    """
    stub = make_kimi_stub(tmp_path)
    mapping = kimi_mapping(tmp_path, stub)
    ps1 = render(call, tmp_path, mapping)

    payload_bytes = KIMI_PAYLOAD.encode("utf-8")
    env = {
        "PARALLAX_TEST_KIMI_EXIT_CODE": "0",
        "PARALLAX_TEST_KIMI_PAYLOAD_B64": base64.b64encode(payload_bytes).decode("ascii"),
    }
    run_wrapper(ps1, env)

    exit_path = tmp_path / "exit"
    reply_path = tmp_path / "reply"
    assert exit_path.read_text(encoding="ascii").strip() == "0"
    reply_bytes = reply_path.read_bytes()
    assert reply_bytes == payload_bytes, (
        "reply bytes do not match the payload's UTF-8 encoding exactly:"
        " got %r, want %r" % (reply_bytes, payload_bytes))
    assert not reply_bytes.startswith(b"\xef\xbb\xbf"), "reply must carry no BOM"


@pytest.mark.parametrize("call", list(KIMI_CALLS))
def test_kimi_wrapper_exit_three_writes_nothing(call, tmp_path):
    stub = make_kimi_stub(tmp_path)
    mapping = kimi_mapping(tmp_path, stub)
    ps1 = render(call, tmp_path, mapping)

    env = {"PARALLAX_TEST_KIMI_EXIT_CODE": "3"}
    run_wrapper(ps1, env)

    exit_path = tmp_path / "exit"
    assert exit_path.read_text(encoding="ascii").strip() == "3"


@pytest.mark.parametrize("call", list(KIMI_CALLS))
def test_kimi_wrapper_exit_zero_empty_reply_polls_as_reply_empty(call, tmp_path):
    stub = make_kimi_stub(tmp_path)
    mapping = kimi_mapping(tmp_path, stub)
    ps1 = render(call, tmp_path, mapping)

    env = {"PARALLAX_TEST_KIMI_EXIT_CODE": "0"}
    run_wrapper(ps1, env)

    exit_path = tmp_path / "exit"
    reply_path = tmp_path / "reply"
    assert exit_path.read_text(encoding="ascii").strip() == "0"
    assert reply_path.exists(), "an empty reply is still a PRESENT artifact"
    assert reply_path.read_bytes() == b""


@pytest.mark.parametrize("call", list(KIMI_CALLS))
def test_kimi_wrapper_pre_client_throw_still_exits_nonzero(call, tmp_path):
    """A missing brief file throws on the ReadAllText call, BEFORE the
    client is ever invoked.
    """
    stub = make_kimi_stub(tmp_path)
    mapping = kimi_mapping(tmp_path, stub, brief_present=False)
    ps1 = render(call, tmp_path, mapping)

    env = {"PARALLAX_TEST_KIMI_EXIT_CODE": "0"}
    run_wrapper(ps1, env)

    exit_path = tmp_path / "exit"
    assert exit_path.exists()
    code = int(exit_path.read_text(encoding="ascii").strip())
    assert code != 0, "a pre-client throw must still exit non-zero"
    assert not (tmp_path / "reply").exists(), "the stub must never have run"


# ---------------------------------------------------------------------
# Step 4: prove the byte-exact oracle above CAN fail, specifically on
# Windows PowerShell 5.1 - the plan's own scoping, because PowerShell 7
# already defaults its native-command decode to UTF-8 and would not
# reproduce the mismatch. This mutates only an in-memory RENDERED copy
# of the wrapper body; the real documents are never touched, so there is
# nothing to restore.
# ---------------------------------------------------------------------
def _is_windows_powershell_51():
    result = subprocess.run(
        [POWERSHELL, "-NoProfile", "-NonInteractive", "-Command",
         "$PSVersionTable.PSVersion.Major"],
        capture_output=True, text=True, timeout=30)
    return result.stdout.strip() == "5"


@pytest.mark.skipif(
    os.name != "nt" or POWERSHELL is None or not _is_windows_powershell_51(),
    reason="the plan requires this demonstration specifically on Windows"
           " PowerShell 5.1, where the OEM code page default reproduces"
           " the mismatch; PARALLAX_PS_HOST is not pinned to it here")
def test_deleting_the_console_encoding_line_breaks_the_byte_oracle(tmp_path):
    call = "kimi-dispatch"
    source_path, marker = WRAPPERS[call]
    body = extract_wrapper_body(source_path, marker)

    encoding_line = "[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)"
    assert encoding_line in body, "the line this test deletes must exist in the real body"
    defective_body = "\n".join(
        line for line in body.split("\n") if line.strip() != encoding_line
    ) + ("\n" if not body.endswith("\n") else "")

    stub = make_kimi_stub(tmp_path)
    mapping = kimi_mapping(tmp_path, stub)
    rendered = substitute(defective_body, mapping)
    ps1 = tmp_path / "wrapper-defective.ps1"
    ps1.write_text(rendered, encoding="utf-8")

    payload_bytes = KIMI_PAYLOAD.encode("utf-8")
    env = {
        "PARALLAX_TEST_KIMI_EXIT_CODE": "0",
        "PARALLAX_TEST_KIMI_PAYLOAD_B64": base64.b64encode(payload_bytes).decode("ascii"),
    }
    run_wrapper(ps1, env)

    reply_bytes = (tmp_path / "reply").read_bytes()
    assert reply_bytes != payload_bytes, (
        "deleting the [Console]::OutputEncoding line was expected to"
        " corrupt the reply bytes on Windows PowerShell 5.1, and it did"
        " not - the byte-exact oracle above would not have caught its"
        " own regression")
