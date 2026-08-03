"""Contract pins for tools/read-kimi-round-evidence.ps1, the executable
validator that reads a kimi-code debate round's OWN session files
(wire.jsonl, kimi-code.log) and decides whether the round can be
attributed to the declared model, agent and tool set.

The fixtures under fixtures/kimi-round/ are a single real captured
session (one fresh tool-using call, one resumed call, kimi-code 0.31.1),
normalized by a generator that applies three literal replacements to the
captured bytes: the canonical model alias becomes "fixture-model/x" (and
its bare provider-side form "x"), the session id a fixed placeholder, and
the one real absolute path that leaked into a tool-call event
"C:/fixture/ws". No fixture byte is hand-typed. manifest.json records the
exact byte offsets and hashes measured at the boundary between the two
calls, so every number below is measured, never invented.

RECAPTURED 2026-07-31 (fix round 1), through a home built by the CURRENT
tools/new-kimi-lane-home.ps1. The first capture came from a home built
before commit b645810, whose model table carried no `capabilities` array:
the client then declared no `thinking` capability (thinkingEffort read
`off` despite the config pinning the canonical effort) and no `image_in`
capability (ReadMediaFile was gated out of the sent schema, so a five-tool
allowlist arrived as toolCount=4). Both symptoms are gone from this
capture - it reads thinkingEffort=high and toolCount=5 against the
five-entry allowlist - so rule 12's tool-name EQUALITY and rule 13's
literal toolCount equality are both satisfiable by a real clean round and
are pinned as equalities here.

Each test asserts on `status`, on the process EXIT CODE, and on a
distinguishing substring of `reason`, never on an exact message string.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

import importlib.util as _importlib_util


def _load_exact_line_module():
    path = Path(__file__).resolve().parents[2] / "evals" / "tools" / "exact_line.py"
    spec = _importlib_util.spec_from_file_location("exact_line", path)
    module = _importlib_util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


accept_exactly_one_nonempty_line = _load_exact_line_module().accept_exactly_one_nonempty_line

REPO = Path(__file__).resolve().parents[2]
SCRIPT = REPO / "tools" / "read-kimi-round-evidence.ps1"
FIXTURES = Path(__file__).parent / "fixtures" / "kimi-round"
AGENT_FILE = REPO / "skills" / "multi-model-verify" / "references" / "kimi-reviewer-agent.md"

FIXTURE_MODEL = "fixture-model/x"
FIXTURE_PROVIDER = "kimi"
FIXTURE_EFFORT = "high"
FIXTURE_SESSION_ID = "session_00000000-0000-4000-8000-000000000001"

MANIFEST = json.loads((FIXTURES / "manifest.json").read_text(encoding="utf-8"))


def _agent_tools():
    """The agent file's `tools:` allowlist, parsed from the committed file
    at run time. Never a hardcoded count: the validator derives the same
    list the same way, and a test that typed the number would stop
    tracking the file it is meant to pin."""
    text = AGENT_FILE.read_text(encoding="utf-8").replace("\r\n", "\n")
    front = text.split("\n---\n", 1)[0]
    m = re.search(r"(?m)^tools:[ \t]*$((?:\n[ \t]+-[^\n]*)*)", front)
    assert m, "could not parse the agent file's tools list"
    return [l.strip().lstrip("-").strip() for l in m.group(1).split("\n") if l.strip()]


AGENT_TOOLS = _agent_tools()

# WINDOWS ONLY, same reason as the probe/mirror/lock suites: CI's ubuntu
# runner ships `pwsh`, so guarding on a PowerShell host being present is
# not enough by itself - the module would then RUN on Linux instead of
# skipping, and its `\`-separated evidence-file paths
# (agents\main\wire.jsonl, logs\kimi-code.log) are ordinary filename
# characters there, not path separators, so every clean case would fail
# evidence-file-missing. See test_review_mirror.py's header for the fuller
# history of this exact mistake.
POWERSHELL = os.environ.get("PARALLAX_PS_HOST") or shutil.which("powershell") or shutil.which("pwsh")

pytestmark = pytest.mark.skipif(
    os.name != "nt" or POWERSHELL is None,
    reason="the round-evidence validator is a Windows tool: its evidence-file "
           "paths are backslash-separated")


# ---------------------------------------------------------------------
# Fixture line helpers
# ---------------------------------------------------------------------

def _read_lines(name):
    text = (FIXTURES / name).read_text(encoding="utf-8")
    return [l for l in text.split("\n") if l.strip()]


def fresh_wire():
    return _read_lines("fresh-wire.jsonl")


def fresh_log():
    return _read_lines("fresh-log.log")


def resume_wire():
    return _read_lines("resume-wire.jsonl")


def resume_log():
    return _read_lines("resume-log.log")


def write_lines(path, lines):
    path.write_bytes(("\n".join(lines) + "\n").encode("utf-8"))


def find_index(lines, rec_type, nth=1):
    count = 0
    for i, l in enumerate(lines):
        if json.loads(l).get("type") == rec_type:
            count += 1
            if count == nth:
                return i
    raise AssertionError(f"no {rec_type} #{nth} in these lines")


def mutate(lines, idx, fn):
    """Return a NEW list with line idx's JSON object mutated by fn (in
    place on the dict). One field changed - the rest of the fixture is
    untouched, so every negative case is the clean fixture with ONE thing
    different."""
    new_lines = list(lines)
    obj = json.loads(new_lines[idx])
    fn(obj)
    new_lines[idx] = json.dumps(obj)
    return new_lines


def remove_line(lines, idx):
    return lines[:idx] + lines[idx + 1:]


def insert_line(lines, idx, obj):
    new_lines = list(lines)
    new_lines.insert(idx, json.dumps(obj))
    return new_lines


def duplicate_line(lines, idx):
    return insert_line(lines, idx + 1, json.loads(lines[idx]))


def brief_sha256(text):
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


EMPTY_SHA256 = hashlib.sha256(b"").hexdigest()

ROUND1_BRIEF_SHA = MANIFEST["round1BriefSha256"]
ROUND2_BRIEF_SHA = MANIFEST["round2BriefSha256"]


# ---------------------------------------------------------------------
# Session-directory construction
# ---------------------------------------------------------------------

def build_fresh_layout(tmp_path, wire_lines, log_lines, session_id=FIXTURE_SESSION_ID,
                        workspace="wd_x"):
    """Build <tmp_path>/sessions/<workspace>/<session_id>/... and return
    (sessions_root, session_dir)."""
    root = tmp_path / "sessions"
    sess_dir = root / workspace / session_id
    (sess_dir / "agents" / "main").mkdir(parents=True)
    (sess_dir / "logs").mkdir(parents=True)
    write_lines(sess_dir / "agents" / "main" / "wire.jsonl", wire_lines)
    write_lines(sess_dir / "logs" / "kimi-code.log", log_lines)
    return root, sess_dir


def build_resume_layout(tmp_path, wire_lines, log_lines, session_id=FIXTURE_SESSION_ID,
                         workspace="wd_x"):
    """Build a session directory directly (no sessions/ root enumeration
    needed for a resume call) and return the session dir."""
    root = tmp_path / "sessions"
    sess_dir = root / workspace / session_id
    (sess_dir / "agents" / "main").mkdir(parents=True)
    (sess_dir / "logs").mkdir(parents=True)
    write_lines(sess_dir / "agents" / "main" / "wire.jsonl", wire_lines)
    write_lines(sess_dir / "logs" / "kimi-code.log", log_lines)
    return sess_dir


def write_json(path, obj):
    path.write_text(json.dumps(obj), encoding="utf-8")


def fresh_prior_state(known_session_dirs=None):
    return {"kind": "fresh", "knownSessionDirs": list(known_session_dirs or [])}


def resume_prior_state_round1():
    """The genuine nextState round 1 produced - the correct -PriorState
    for validating round 2."""
    return {
        "kind": "resume",
        "sessionDir": str(FIXTURES),  # overwritten by callers that need a real dir; see resume_prior_state()
        "sessionId": FIXTURE_SESSION_ID,
        "wireBytes": MANIFEST["wireOffsetAfterRound1"],
        "logBytes": MANIFEST["logOffsetAfterRound1"],
        "wirePrefixSha256": MANIFEST["wirePrefixSha256AfterRound1"],
        "logPrefixSha256": MANIFEST["logPrefixSha256AfterRound1"],
        "toolsHash": MANIFEST["toolsHashRound1"],
        "systemPromptHash": MANIFEST["systemPromptHashRound1"],
    }


def resume_prior_state(sess_dir, **overrides):
    state = resume_prior_state_round1()
    state["sessionDir"] = str(sess_dir)
    state.update(overrides)
    return state


# ---------------------------------------------------------------------
# Invocation helpers
# ---------------------------------------------------------------------

def run_fresh(sessions_root, session_id, prior_state_path, agent_file=AGENT_FILE,
              model=FIXTURE_MODEL, provider=FIXTURE_PROVIDER, effort=FIXTURE_EFFORT,
              expected_brief_sha=ROUND1_BRIEF_SHA):
    args = [
        POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT),
        "-Fresh", "-SessionsRoot", str(sessions_root),
        "-SessionIdFromStdout", session_id,
        "-PriorState", str(prior_state_path),
        "-Model", model, "-Provider", provider, "-Effort", effort,
        "-AgentFile", str(agent_file), "-ExpectedBriefSha256", expected_brief_sha,
        "-Json",
    ]
    proc = subprocess.run(args, capture_output=True, text=True, timeout=60)
    return proc


def run_resume(session_dir, prior_state_path, agent_file=AGENT_FILE,
               model=FIXTURE_MODEL, provider=FIXTURE_PROVIDER, effort=FIXTURE_EFFORT,
               expected_brief_sha=ROUND2_BRIEF_SHA):
    args = [
        POWERSHELL, "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(SCRIPT),
        "-Resume", "-SessionDir", str(session_dir),
        "-PriorState", str(prior_state_path),
        "-Model", model, "-Provider", provider, "-Effort", effort,
        "-AgentFile", str(agent_file), "-ExpectedBriefSha256", expected_brief_sha,
        "-Json",
    ]
    proc = subprocess.run(args, capture_output=True, text=True, timeout=60)
    return proc


def parsed(proc):
    """EXACTLY ONE nonempty line, through the shared strict helper. This
    used to parse only the LAST line, so a validator that printed stray
    output before its JSON passed every test in this module - a helper
    that could not fail on the cardinality it exists to check."""
    line = accept_exactly_one_nonempty_line(proc.stdout)
    if line is None:
        raise AssertionError(
            "stdout was not exactly one nonempty line: "
            + repr(proc.stdout) + proc.stderr)
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        raise AssertionError("stdout was not JSON: " + proc.stdout + proc.stderr)


def assert_clean(proc):
    p = parsed(proc)
    assert p.get("status") == "clean", (p, proc.stderr)
    assert "nextState" in p
    # The EXIT CODE is half the contract: the dispatch flow gates on it,
    # so a script that printed "clean" while exiting nonzero (or the
    # reverse) would break every caller that never parses stdout.
    assert proc.returncode == 0, (proc.returncode, p, proc.stderr)
    return p


def assert_failed(proc, reason_substring):
    p = parsed(proc)
    assert p.get("status") == "failed", (p, proc.stderr)
    assert reason_substring in p.get("reason", ""), p
    assert proc.returncode == 1, (proc.returncode, p, proc.stderr)
    return p


# =======================================================================
# FIXTURE HYGIENE
# =======================================================================

def test_fixture_files_contain_no_crlf():
    """The `.gitattributes` `eol=lf` rule for fixtures/kimi-round/* is the
    ONLY thing standing between these byte-exact offsets/hashes and
    `core.autocrlf=true` silently rewriting them on a future checkout - a
    fixture-corrupting bug this task's own report found and fixed once
    already. Nothing pinned that the WORKING TREE bytes actually stay LF,
    so a future edit that reintroduced CRLF (or a machine/config where the
    attribute did not apply) would pass every other test right up until
    the next checkout broke it. This reads the files exactly as the
    validator does - raw bytes, not text-mode - the same gap a
    text-mode read would silently paper over."""
    for name in ("fresh-wire.jsonl", "fresh-log.log",
                 "resume-wire.jsonl", "resume-log.log"):
        raw = (FIXTURES / name).read_bytes()
        assert b"\r\n" not in raw, name


# =======================================================================
# CLEAN CASES
# =======================================================================

def test_fresh_round_is_clean(tmp_path):
    """An inventory and no offsets - the only shape a fresh state has."""
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    proc = run_fresh(root, FIXTURE_SESSION_ID, state_path)
    p = assert_clean(proc)
    assert p["nextState"]["kind"] == "resume"
    assert p["nextState"]["wireBytes"] == MANIFEST["wireOffsetAfterRound1"]


def test_a_fresh_calls_next_state_is_the_resume_calls_prior_state(tmp_path):
    """The design property that makes the two parameter sets compose: a
    fresh call's own nextState IS the next call's -PriorState, with
    nothing from manifest.json involved.

    Every other resume test feeds a state built from the manifest, which
    the FIXTURE GENERATOR wrote - so the two prefix hashes and the two
    continuity hashes the validator emits in rule 16 are never checked
    against what a subsequent resume actually needs, and an error in rule
    16 would pass the whole suite. Here round 1's own output is written to
    disk verbatim, the session's two files are advanced to their
    post-round-2 contents, and round 2 is validated against it."""
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    next_state = assert_clean(run_fresh(root, FIXTURE_SESSION_ID, state_path))["nextState"]

    # The same session, one round later: the client appended round 2's
    # records to both files.
    write_lines(sess_dir / "agents" / "main" / "wire.jsonl", resume_wire())
    write_lines(sess_dir / "logs" / "kimi-code.log", resume_log())

    chained_path = tmp_path / "next-state.json"
    write_json(chained_path, next_state)
    assert_clean(run_resume(sess_dir, chained_path))


def test_resumed_round_with_correct_offsets_is_clean(tmp_path):
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(sess_dir))
    proc = run_resume(sess_dir, state_path)
    assert_clean(proc)


def test_resumed_round_is_clean_with_no_session_scoped_records_in_its_slice(tmp_path):
    """The measured shape: a resumed call's slice carries no config.update,
    tools.set_active_tools or llm.tools_snapshot at all - r2 would have
    failed this. Confirmed directly: the resume fixture's round-2 slice
    (from wireOffsetAfterRound1 onward) has none of the four session-scoped
    record types, and the round is still clean."""
    round2_wire = resume_wire()[len(fresh_wire()):]
    for rec_type in ("config.update", "tools.set_active_tools",
                      "llm.tools_snapshot", "permission.set_mode"):
        assert not any(json.loads(l).get("type") == rec_type for l in round2_wire), rec_type
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(sess_dir))
    assert_clean(run_resume(sess_dir, state_path))


def test_fresh_round_with_four_llm_requests_is_clean(tmp_path):
    """llm.request count tracks the tool loop and is variable - bounded
    from below, never fixed. Built by duplicating the two real llm.request
    records (plus their usage.record) once each, so all toolsHash/
    systemPromptHash stay identical across all four - exactly what a
    longer real tool loop would look like."""
    wire = fresh_wire()
    req1 = find_index(wire, "llm.request", 1)
    wire = duplicate_line(wire, req1)
    req2 = find_index(wire, "llm.request", 3)  # the original second request, now index 3
    wire = duplicate_line(wire, req2)
    assert sum(1 for l in wire if json.loads(l).get("type") == "llm.request") == 4
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_clean(run_fresh(root, FIXTURE_SESSION_ID, state_path))


def test_first_call_of_a_debate_creates_container_and_leaf_and_is_clean(tmp_path):
    """A debate's FIRST call creates BOTH a wd_<workspace> container and
    the session inside it - two new directories, but only one is a
    session_-prefixed leaf. Without the leaf-only rule this would report
    session-not-resolvable on the clean first call of every debate."""
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log(),
                                         workspace="wd_ws_first-call")
    assert (root / "wd_ws_first-call").exists()  # sanity: dir exists
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state(known_session_dirs=[]))
    assert_clean(run_fresh(root, FIXTURE_SESSION_ID, state_path))


def test_system_prompt_with_different_line_endings_is_still_clean(tmp_path):
    """Rule 12's canonicalization (CRLF -> LF on both sides before
    comparing) is what makes this pass. Without it, an autocrlf checkout
    breaks the lane on one machine and not another."""
    wire = fresh_wire()
    idx = find_index(wire, "config.update", 1)
    wire = mutate(wire, idx, lambda o: o.__setitem__(
        "systemPrompt", o["systemPrompt"].replace("\n", "\r\n")))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_clean(run_fresh(root, FIXTURE_SESSION_ID, state_path))


# =======================================================================
# FRESHNESS CASES
# =======================================================================

def test_resume_with_zero_wire_offset_fails(tmp_path):
    """Round 1's records would otherwise satisfy every later check - the
    stale-evidence case, and the reason the script exists."""
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(
        sess_dir, wireBytes=0, wirePrefixSha256=EMPTY_SHA256))
    # offset 0 means the slice starts at "metadata", not "turn.prompt".
    assert_failed(run_resume(sess_dir, state_path), "slice-misaligned")


def test_resume_with_zero_log_offset_fails(tmp_path):
    """Symmetric with the wire case."""
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(
        sess_dir, logBytes=0, logPrefixSha256=EMPTY_SHA256))
    # The wire offset is still correct, so this reaches the log-specific
    # symptom: TWO llm config lines now fall inside the slice (round 1's
    # and round 2's), since the log offset no longer excludes round 1's.
    assert_failed(run_resume(sess_dir, state_path), "log-config-count")


def test_stale_offset_landing_mid_previous_call_fails_slice_misaligned(tmp_path):
    """A stale offset landing AFTER round 1's turn.prompt but BEFORE its
    trailing llm.request records passes every count and value check while
    mixing two calls - the shape r3 never tested."""
    wire = resume_wire()
    fresh = fresh_wire()
    turn_prompt_idx = find_index(fresh, "turn.prompt", 1)
    # Byte offset landing just past round 1's turn.prompt line.
    mid_offset = len(("\n".join(fresh[:turn_prompt_idx + 1]) + "\n").encode("utf-8"))
    prefix_bytes = ("\n".join(fresh[:turn_prompt_idx + 1]) + "\n").encode("utf-8")
    prefix_hash = hashlib.sha256(prefix_bytes).hexdigest()
    sess_dir = build_resume_layout(tmp_path, wire, resume_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(
        sess_dir, wireBytes=mid_offset, wirePrefixSha256=prefix_hash))
    assert_failed(run_resume(sess_dir, state_path), "slice-misaligned")


def test_wire_shorter_than_offset_fails_truncated_not_rereadfromzero(tmp_path):
    """The written wire.jsonl is genuinely SHORTER than the claimed prior
    offset (the real resume-wire.jsonl's total byte length, used as a
    stand-in for "the file used to be this long"), not merely equal to
    it - a length equal to the offset is a legitimate empty slice, not a
    truncation."""
    sess_dir = build_resume_layout(tmp_path, fresh_wire(), resume_log())
    larger_offset = len((FIXTURES / "resume-wire.jsonl").read_bytes())
    assert larger_offset > len((FIXTURES / "fresh-wire.jsonl").read_bytes())
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(sess_dir, wireBytes=larger_offset))
    assert_failed(run_resume(sess_dir, state_path), "truncated")


def test_log_shorter_than_offset_fails_truncated(tmp_path):
    sess_dir = build_resume_layout(tmp_path, resume_wire(), fresh_log())
    larger_offset = len((FIXTURES / "resume-log.log").read_bytes())
    assert larger_offset > len((FIXTURES / "fresh-log.log").read_bytes())
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(sess_dir, logBytes=larger_offset))
    assert_failed(run_resume(sess_dir, state_path), "truncated")


def test_wire_prefix_hash_mismatch_fails_prefix_replaced(tmp_path):
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(sess_dir, wirePrefixSha256="a" * 64))
    assert_failed(run_resume(sess_dir, state_path), "prefix-replaced")


def test_log_prefix_hash_mismatch_fails_prefix_replaced(tmp_path):
    """The rotation question is about the log; length-only protection
    there was r3's asymmetry - this pins that the log gets a real hash
    check too, not just the wire."""
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(sess_dir, logPrefixSha256="b" * 64))
    assert_failed(run_resume(sess_dir, state_path), "prefix-replaced")


# =======================================================================
# SESSION-IDENTITY CASES
# =======================================================================

def test_fresh_call_with_zero_new_session_dirs_fails(tmp_path):
    root = tmp_path / "sessions"
    root.mkdir()
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "session-not-resolvable")


def test_fresh_call_with_two_new_session_dirs_fails(tmp_path):
    """A concurrent run in the same home - the one collision an isolated
    home does not prevent."""
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    other = root / "wd_x" / "session_11111111-1111-4111-8111-111111111111"
    (other / "agents" / "main").mkdir(parents=True)
    (other / "logs").mkdir(parents=True)
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "session-not-resolvable")


def test_fresh_call_whose_new_dir_does_not_match_stdout_id_fails(tmp_path):
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    proc = run_fresh(root, "session_ffffffff-ffff-4fff-8fff-ffffffffffff", state_path)
    assert_failed(proc, "session-id-mismatch")


def test_fresh_state_with_stale_known_session_dirs_fails(tmp_path):
    """A pre-existing directory absent from knownSessionDirs reads as new,
    so a genuinely fresh call now sees two "new" leaves."""
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    preexisting = root / "wd_x" / "session_22222222-2222-4222-8222-222222222222"
    (preexisting / "agents" / "main").mkdir(parents=True)
    (preexisting / "logs").mkdir(parents=True)
    state_path = tmp_path / "state.json"
    # knownSessionDirs is stale: it does not list `preexisting`, even
    # though it existed before this dispatch.
    write_json(state_path, fresh_prior_state(known_session_dirs=[]))
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "session-not-resolvable")


def test_fresh_state_with_forward_slash_spelled_known_session_dir_is_clean(tmp_path):
    """Fix round 2, Important 2: knownSessionDirs is produced by a
    DIFFERENT task's dispatch flow, and nothing in the script, the tests,
    or the header ever pinned its required path spelling. Measured:
    Get-ChildItem's FullName is backslash-spelled on Windows, and a
    genuinely pre-existing directory listed in knownSessionDirs with
    forward slashes instead used to read as session-not-resolvable ("2
    new session directory(ies) found") - the fresh branch compared raw
    strings while the resume branch, a few lines below, already
    normalized both sides with Resolve-Path. Both branches now go through
    the same Resolve-PathSafe helper, so this is clean: exactly one
    genuinely new leaf (the fixture session), the forward-slash-spelled
    directory correctly recognized as already known."""
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    preexisting = root / "wd_x" / "session_22222222-2222-4222-8222-222222222222"
    (preexisting / "agents" / "main").mkdir(parents=True)
    (preexisting / "logs").mkdir(parents=True)
    state_path = tmp_path / "state.json"
    forward_spelled = str(preexisting).replace("\\", "/")
    write_json(state_path, fresh_prior_state(known_session_dirs=[forward_spelled]))
    assert_clean(run_fresh(root, FIXTURE_SESSION_ID, state_path))


def test_prior_state_kind_disagreeing_with_invocation_fails(tmp_path):
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    state_path = tmp_path / "state.json"
    # A fresh-shaped state handed to a -Resume invocation.
    write_json(state_path, fresh_prior_state())
    assert_failed(run_resume(sess_dir, state_path), "state-kind-mismatch")


def test_prior_state_kind_mismatch_the_other_direction(tmp_path):
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    # A resume-shaped state handed to a -Fresh invocation.
    write_json(state_path, resume_prior_state(sess_dir))
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "state-kind-mismatch")


def test_resume_prior_state_naming_a_different_session_dir_fails(tmp_path):
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    other_dir = tmp_path / "elsewhere"
    other_dir.mkdir()
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(other_dir))
    assert_failed(run_resume(sess_dir, state_path), "state-session-mismatch")


def test_resume_prior_state_naming_a_different_session_id_fails(tmp_path):
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(sess_dir, sessionId="session_not-this-one"))
    assert_failed(run_resume(sess_dir, state_path), "state-session-mismatch")


def test_prior_state_missing_is_unusable(tmp_path):
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    state_path = tmp_path / "does-not-exist.json"
    assert_failed(run_resume(sess_dir, state_path), "prior-state-unusable")


def test_prior_state_malformed_json_is_unusable(tmp_path):
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    state_path = tmp_path / "state.json"
    state_path.write_text("{not json", encoding="utf-8")
    assert_failed(run_resume(sess_dir, state_path), "prior-state-unusable")


def test_prior_state_missing_a_field_is_unusable(tmp_path):
    """A generic case from the brief's list ("-PriorState that is missing,
    malformed, or missing a field fails"), not tied to one specific
    reason token. With EVERY field but kind absent, rule 3 (session
    establishment) is reached before rule 4 (state-inconsistent) - the
    resume branch compares -PriorState.sessionDir/sessionId against the
    resolved session first, and a wholly-absent sessionDir/sessionId
    cannot match, so this fails there. See
    test_resume_state_missing_an_offset_is_inconsistent below for the
    complementary case that DOES reach rule 4 directly, by supplying a
    correct sessionDir/sessionId and omitting only an offset field."""
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, {"kind": "resume"})  # everything else absent
    assert_failed(run_resume(sess_dir, state_path), "state-session-mismatch")


def test_prior_state_with_string_offset_is_unusable(tmp_path):
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(sess_dir, wireBytes="19491"))
    assert_failed(run_resume(sess_dir, state_path), "prior-state-unusable")


def test_prior_state_with_negative_offset_is_unusable(tmp_path):
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(sess_dir, wireBytes=-1))
    assert_failed(run_resume(sess_dir, state_path), "prior-state-unusable")


def test_prior_state_with_63_char_hash_is_unusable(tmp_path):
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(sess_dir, wirePrefixSha256="a" * 63))
    assert_failed(run_resume(sess_dir, state_path), "prior-state-unusable")


def test_prior_state_with_known_session_dirs_as_a_string_is_unusable(tmp_path):
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, {"kind": "fresh", "knownSessionDirs": "not-a-list"})
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "prior-state-unusable")


def test_replaying_an_older_rounds_state_fails(tmp_path):
    """A well-formed, internally self-consistent resume state (offset 0,
    hash of the empty prefix, and round 1's real continuity hashes) is
    exactly what would have been fed INTO round 1, not what came out of
    it. Replaying it against round 2's slice is not a malformed object -
    every field is well-typed and hash-consistent AT ITS OWN offset - so
    it must still fail, not validate. It resolves to the same
    slice-misaligned symptom as the zero-offset freshness cases (the slice
    starts at "metadata" instead of "turn.prompt"), which is the point:
    even a well-formed but stale state does not get a pass merely for
    being well-formed."""
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(
        sess_dir, wireBytes=0, wirePrefixSha256=EMPTY_SHA256,
        logBytes=0, logPrefixSha256=EMPTY_SHA256))
    assert_failed(run_resume(sess_dir, state_path), "slice-misaligned")


def test_fresh_state_carrying_a_session_dir_is_inconsistent(tmp_path):
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    state = fresh_prior_state()
    state["sessionDir"] = str(sess_dir)
    write_json(state_path, state)
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "state-inconsistent")


def test_fresh_state_carrying_offsets_is_inconsistent(tmp_path):
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    state = fresh_prior_state()
    state["wireBytes"] = 0
    write_json(state_path, state)
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "state-inconsistent")


def test_resume_state_missing_an_offset_is_inconsistent(tmp_path):
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    state_path = tmp_path / "state.json"
    state = resume_prior_state(sess_dir)
    del state["wireBytes"]
    write_json(state_path, state)
    assert_failed(run_resume(sess_dir, state_path), "state-inconsistent")


def test_fresh_slice_not_beginning_with_metadata_fails_slice_misaligned(tmp_path):
    wire = fresh_wire()
    wire = remove_line(wire, 0)  # drop the leading "metadata" record
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "slice-misaligned")


def test_resume_slice_not_beginning_with_turn_prompt_fails_slice_misaligned(tmp_path):
    """Covered mechanically by test_resume_with_zero_wire_offset_fails
    too; this is the direct, minimal form: the resume fixture's OWN
    second turn.prompt line is removed, so the (correctly-offset) slice
    now opens on a context.append_message instead."""
    wire = resume_wire()
    idx = find_index(wire, "turn.prompt", 2)
    wire = remove_line(wire, idx)
    sess_dir = build_resume_layout(tmp_path, wire, resume_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(sess_dir))
    assert_failed(run_resume(sess_dir, state_path), "slice-misaligned")


# =======================================================================
# MISSING AND MALFORMED
# =======================================================================

def test_missing_session_directory_fails(tmp_path):
    sess_dir = tmp_path / "sessions" / "wd_x" / FIXTURE_SESSION_ID
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(sess_dir))
    assert_failed(run_resume(sess_dir, state_path), "session-dir-missing")


def test_missing_wire_file_fails(tmp_path):
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    (sess_dir / "agents" / "main" / "wire.jsonl").unlink()
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(sess_dir))
    assert_failed(run_resume(sess_dir, state_path), "evidence-file-missing")


def test_missing_log_file_fails(tmp_path):
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    (sess_dir / "logs" / "kimi-code.log").unlink()
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(sess_dir))
    assert_failed(run_resume(sess_dir, state_path), "evidence-file-missing")


def test_non_json_line_in_slice_fails_wire_malformed(tmp_path):
    wire = fresh_wire()
    wire.insert(6, "this is not json")
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "wire-malformed")


def test_turn_prompt_input_not_an_array_fails_record_malformed(tmp_path):
    wire = fresh_wire()
    idx = find_index(wire, "turn.prompt", 1)
    wire = mutate(wire, idx, lambda o: o.__setitem__("input", "not-an-array"))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "record-malformed")


def test_turn_prompt_input_element_with_no_text_fails_record_malformed(tmp_path):
    wire = fresh_wire()
    idx = find_index(wire, "turn.prompt", 1)
    wire = mutate(wire, idx, lambda o: o.__setitem__("input", [{"type": "text"}]))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "record-malformed")


def test_llm_request_toolshash_not_a_string_fails_record_malformed(tmp_path):
    wire = fresh_wire()
    idx = find_index(wire, "llm.request", 1)
    wire = mutate(wire, idx, lambda o: o.__setitem__("toolsHash", 12345))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "record-malformed")


# Fix round 2, Important 1: Test-ToolsSnapshotShape used to check only that
# `tools` was an array, never its elements. Reproduced by the review: an
# element missing `name`, an element that HAD `name` losing it, and `tools`
# as a bare list of strings all used to reach rule 12's Compare-Object
# unvalidated - crashing (a raw binding error, no JSON on stdout) under this
# script's own $ErrorActionPreference = "Stop", or, measured WITHOUT that
# preference, silently evaluating the same expression's .Count to 0 - a
# SILENT PASS on the tool-name equality regardless of what the malformed
# entry actually was. All three now fail record-malformed at rule 10,
# before rule 12 ever runs.

def test_tools_snapshot_entry_missing_name_fails_record_malformed(tmp_path):
    wire = fresh_wire()
    idx = find_index(wire, "llm.tools_snapshot", 1)
    wire = mutate(wire, idx, lambda o: o["tools"].append(
        {"description": "x", "parameters": {}}))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "record-malformed")


def test_tools_snapshot_entry_losing_its_name_fails_record_malformed(tmp_path):
    def drop_name(o):
        del o["tools"][0]["name"]
    wire = fresh_wire()
    idx = find_index(wire, "llm.tools_snapshot", 1)
    wire = mutate(wire, idx, drop_name)
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "record-malformed")


def test_tools_snapshot_tools_as_bare_strings_fails_record_malformed(tmp_path):
    wire = fresh_wire()
    idx = find_index(wire, "llm.tools_snapshot", 1)
    wire = mutate(wire, idx, lambda o: o.__setitem__(
        "tools", [t["name"] for t in o["tools"]]))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "record-malformed")


def test_missing_agent_file_fails(tmp_path):
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    proc = run_fresh(root, FIXTURE_SESSION_ID, state_path,
                      agent_file=tmp_path / "no-such-agent.md")
    assert_failed(proc, "agent-file-unusable")


def test_agent_file_with_unparseable_frontmatter_fails(tmp_path):
    bad_agent = tmp_path / "bad-agent.md"
    bad_agent.write_text("not even frontmatter\n", encoding="utf-8")
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    proc = run_fresh(root, FIXTURE_SESSION_ID, state_path, agent_file=bad_agent)
    assert_failed(proc, "agent-file-unusable")


def test_expected_brief_sha_not_64_hex_fails_bad_argument(tmp_path):
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    proc = run_fresh(root, FIXTURE_SESSION_ID, state_path, expected_brief_sha="not-a-hash")
    assert_failed(proc, "bad-argument")


def test_missing_turn_prompt_fails(tmp_path):
    """turn.prompt is the fresh slice's 6th record (metadata,
    config.update x2, tools.set_active_tools, permission.set_mode, THEN
    turn.prompt), not its first, so removing it does not touch the
    slice-boundary check - it is caught directly by the per-call count."""
    wire = fresh_wire()
    idx = find_index(wire, "turn.prompt", 1)
    wire = remove_line(wire, idx)
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "turn-prompt-count")


def test_two_turn_prompts_in_one_slice_fails_turn_prompt_count(tmp_path):
    wire = fresh_wire()
    idx = find_index(wire, "turn.prompt", 1)
    wire = duplicate_line(wire, idx)
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "turn-prompt-count")


def test_zero_llm_requests_in_slice_fails(tmp_path):
    wire = fresh_wire()
    while True:
        idxs = [i for i, l in enumerate(wire) if json.loads(l).get("type") == "llm.request"]
        if not idxs:
            break
        wire = remove_line(wire, idxs[0])
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "llm-request-count")


def test_missing_llm_config_line_fails(tmp_path):
    log = [l for l in fresh_log() if "llm config" not in l]
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), log)
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "log-config-count")


def test_two_llm_config_lines_in_one_log_slice_fails(tmp_path):
    log = fresh_log()
    config_idx = next(i for i, l in enumerate(log) if "llm config" in l)
    log.insert(config_idx + 1, log[config_idx])
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), log)
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "log-config-count")


@pytest.mark.parametrize("rec_type", [
    "config.update", "tools.set_active_tools", "llm.tools_snapshot", "permission.set_mode",
])
def test_session_scoped_record_absent_from_fresh_slice_fails(tmp_path, rec_type):
    wire = fresh_wire()
    idxs = [i for i, l in enumerate(wire) if json.loads(l).get("type") == rec_type]
    for i in reversed(idxs):
        wire = remove_line(wire, i)
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "session-scoped-count")


def test_duplicated_config_update_three_of_them_fails(tmp_path):
    wire = fresh_wire()
    idx = find_index(wire, "config.update", 1)
    wire = duplicate_line(wire, idx)
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "session-scoped-count")


@pytest.mark.parametrize("rec_type", [
    "tools.set_active_tools", "llm.tools_snapshot", "permission.set_mode",
])
def test_duplicated_singleton_session_scoped_record_fails(tmp_path, rec_type):
    wire = fresh_wire()
    idx = find_index(wire, rec_type, 1)
    wire = duplicate_line(wire, idx)
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "session-scoped-count")


def test_two_copies_of_first_config_update_shape_second_absent_fails(tmp_path):
    """The count is right (2 config.update records) and the content is
    not (both are the profileName/systemPrompt shape; the
    modelAlias/thinkingEffort shape never appears)."""
    wire = fresh_wire()
    first_idx = find_index(wire, "config.update", 1)
    second_idx = find_index(wire, "config.update", 2)
    first_obj = json.loads(wire[first_idx])
    wire[second_idx] = json.dumps(first_obj)
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "session-scoped-content")


def test_two_copies_of_second_config_update_shape_fails(tmp_path):
    """The mirror of the case above, actually isolating the OTHER count
    check this time. Simply overwriting the first record with the second
    record's content (as the case above does for the first shape) makes
    the FIRST-shape count check (exactly one profileName/systemPrompt
    record) fail FIRST, since it drops to zero - never exercising the
    second-shape count check the case's name claims to test, even though
    both checks share the session-scoped-content token and the test
    passed regardless. Fixed by MERGING the second shape's keys into the
    first record instead of replacing it: the first record now satisfies
    BOTH shape predicates (profileName/systemPrompt survive), so the
    first-shape count stays exactly 1 and passes - while the
    second-shape count becomes 2 (the merged record plus the untouched
    second record), which is the check this case exists to reach."""
    wire = fresh_wire()
    first_idx = find_index(wire, "config.update", 1)
    second_idx = find_index(wire, "config.update", 2)
    second_obj = json.loads(wire[second_idx])
    wire = mutate(wire, first_idx, lambda o: o.update(second_obj))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path),
                  "expected exactly one modelAlias/thinkingEffort config.update")


@pytest.mark.parametrize("rec_type", [
    "config.update", "tools.set_active_tools", "llm.tools_snapshot", "permission.set_mode",
])
def test_resume_slice_containing_a_session_scoped_record_fails(tmp_path, rec_type):
    """The resume branch's whole reason for existing - r3 gave it no
    negative test at all. Take round 1's copy of the record and splice it
    into round 2's slice."""
    fresh = fresh_wire()
    resume = resume_wire()
    idx_in_fresh = find_index(fresh, rec_type, 1)
    injected = fresh[idx_in_fresh]
    # Inserted AFTER round 2's own turn.prompt (its first record), not
    # before it - otherwise the injected record becomes the slice's
    # first record and this trips the boundary check (slice-misaligned)
    # instead of reaching the check this case exists to exercise.
    round2_start = len(fresh)
    insert_at = round2_start + 1
    wire = resume[:insert_at] + [injected] + resume[insert_at:]
    sess_dir = build_resume_layout(tmp_path, wire, resume_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(sess_dir))
    assert_failed(run_resume(sess_dir, state_path), "session-scoped-on-resume")


# =======================================================================
# INEQUALITY CASES
# =======================================================================

def test_active_tools_names_unequal_to_allowlist_fails(tmp_path):
    """Appending ExtraTool to tools.set_active_tools.names ALSO breaks the
    llm.tools_snapshot comparison two checks later (:660), since the
    snapshot's own tool names no longer equal the now-longer active
    list - and both checks emit the shared "session-scoped-content" token,
    so a generic substring assertion would still pass even if THIS check
    (:640, tools.set_active_tools vs -AgentFile) were neutered and the
    snapshot check caught the mutation instead. Asserting the check's own
    distinguishing text closes that gap."""
    wire = fresh_wire()
    idx = find_index(wire, "tools.set_active_tools", 1)
    wire = mutate(wire, idx, lambda o: o["names"].append("ExtraTool"))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path),
                  "tools.set_active_tools.names does not match -AgentFile's tools list")


def test_active_tools_disallowed_names_unequal_to_denylist_fails(tmp_path):
    wire = fresh_wire()
    idx = find_index(wire, "tools.set_active_tools", 1)
    wire = mutate(wire, idx, lambda o: o["disallowedNames"].pop())
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "session-scoped-content")


def test_snapshot_tool_names_unequal_while_active_names_correct_fails(tmp_path):
    """Separate records, and one can be right while the other is wrong.
    The ADDITION direction: a name in the snapshot that the allowlist does
    not carry."""
    wire = fresh_wire()
    idx = find_index(wire, "llm.tools_snapshot", 1)
    wire = mutate(wire, idx, lambda o: o["tools"].append(
        {"name": "Bash", "description": "x", "parameters": {}}))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "session-scoped-content")


def test_snapshot_missing_a_tool_the_allowlist_carries_fails(tmp_path):
    """The REMOVAL direction, which a one-sided comparison reports clean.
    Rule 12 mandates equality: a snapshot missing tools describes a sent
    surface that collapsed, and that is the permissive direction - the one
    where an unverified round reads as verified. The log's toolCount is
    lowered to match, so the mutation is internally consistent and this
    case cannot be caught by the toolCount checks instead."""
    wire = fresh_wire()
    idx = find_index(wire, "llm.tools_snapshot", 1)
    wire = mutate(wire, idx, lambda o: o["tools"].pop())
    log = fresh_log()
    log_idx = next(i for i, l in enumerate(log) if "llm config" in l)
    log[log_idx] = re.sub(r"toolCount=\d+", f"toolCount={len(AGENT_TOOLS) - 1}",
                          log[log_idx])
    root, sess_dir = build_fresh_layout(tmp_path, wire, log)
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "session-scoped-content")


def test_profile_name_mismatch_fails(tmp_path):
    wire = fresh_wire()
    idx = find_index(wire, "config.update", 1)
    wire = mutate(wire, idx, lambda o: o.__setitem__("profileName", "someone-else"))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "session-scoped-content")


def test_system_prompt_differing_from_agent_body_fails(tmp_path):
    wire = fresh_wire()
    idx = find_index(wire, "config.update", 1)
    wire = mutate(wire, idx, lambda o: o.__setitem__(
        "systemPrompt", o["systemPrompt"] + " extra unauthorized text"))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "session-scoped-content")


def test_system_prompt_chars_differing_from_body_length_fails(tmp_path):
    log = fresh_log()
    idx = next(i for i, l in enumerate(log) if "llm config" in l)
    log[idx] = re.sub(r"systemPromptChars=\d+", "systemPromptChars=999", log[idx])
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), log)
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "log-config-field")


def test_clean_round_tool_count_equals_the_allowlist_length(tmp_path):
    """The premise rule 13's literal equality stands on. Both the fresh
    and the resume log lines carry the agent file's full allowlist length,
    so the equality below is satisfiable by a real clean round rather than
    being a rule that rejects one."""
    for lines in (fresh_log(), resume_log()):
        for line in lines:
            if "llm config" in line:
                assert f"toolCount={len(AGENT_TOOLS)}" in line, line


@pytest.mark.parametrize("wrong_count_offset", [1, -1])
def test_tool_count_unequal_to_allowlist_length_fails(tmp_path, wrong_count_offset):
    """Rule 13's literal equality, pinned in BOTH directions: a toolCount
    ABOVE the allowlist length is "the allowlist failed to apply", and one
    BELOW it is "part of the sent surface silently vanished". A one-sided
    bound would report the second clean.

    Uses the RESUME fixture deliberately: a resume slice carries no
    llm.tools_snapshot at all, so the (independent, stronger) fresh-only
    cross-check against the snapshot's own tool count cannot catch this
    mutation instead. That isolates the agent-file equality as the only
    check under test - the fresh fixture was measured (mutation testing,
    task-6 round 0) to let the snapshot cross-check catch the same
    mutation first, which made the case prove nothing."""
    log = resume_log()
    idx = max(i for i, l in enumerate(log) if "llm config" in l)  # round 2's own line
    assert f"toolCount={len(AGENT_TOOLS)}" in log[idx]
    log[idx] = re.sub(r"toolCount=\d+",
                      f"toolCount={len(AGENT_TOOLS) + wrong_count_offset}", log[idx])
    sess_dir = build_resume_layout(tmp_path, resume_wire(), log)
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(sess_dir))
    assert_failed(run_resume(sess_dir, state_path), "log-config-field")


def test_model_alias_wrong_in_second_config_update_fails(tmp_path):
    wire = fresh_wire()
    idx = find_index(wire, "config.update", 2)
    wire = mutate(wire, idx, lambda o: o.__setitem__("modelAlias", "wrong-model/y"))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "session-scoped-content")


def test_thinking_effort_wrong_in_second_config_update_fails(tmp_path):
    wire = fresh_wire()
    idx = find_index(wire, "config.update", 2)
    wire = mutate(wire, idx, lambda o: o.__setitem__("thinkingEffort", "max"))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "session-scoped-content")


def test_permission_mode_not_auto_fails(tmp_path):
    wire = fresh_wire()
    idx = find_index(wire, "permission.set_mode", 1)
    wire = mutate(wire, idx, lambda o: o.__setitem__("mode", "manual"))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "session-scoped-content")


@pytest.mark.parametrize("field,value", [
    ("modelAlias", "wrong-model/y"),
    ("provider", "not-kimi"),
    ("thinkingEffort", "max"),
])
def test_llm_request_field_wrong_on_second_request_not_just_first(tmp_path, field, value):
    """Not merely the first - the SECOND llm.request in the slice."""
    wire = fresh_wire()
    idx = find_index(wire, "llm.request", 2)
    wire = mutate(wire, idx, lambda o: o.__setitem__(field, value))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "llm-request-field")


def test_llm_request_tools_hash_empty_fails(tmp_path):
    wire = fresh_wire()
    idx = find_index(wire, "llm.request", 1)
    wire = mutate(wire, idx, lambda o: o.__setitem__("toolsHash", ""))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "llm-request-field")


def test_llm_request_system_prompt_hash_empty_fails(tmp_path):
    wire = fresh_wire()
    idx = find_index(wire, "llm.request", 1)
    wire = mutate(wire, idx, lambda o: o.__setitem__("systemPromptHash", ""))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "llm-request-field")


def test_tools_hash_differing_between_requests_in_one_slice_fails(tmp_path):
    """One request in a tool loop could otherwise run on a different
    surface while the emitted hashes come from another."""
    wire = fresh_wire()
    idx = find_index(wire, "llm.request", 2)
    wire = mutate(wire, idx, lambda o: o.__setitem__("toolsHash", "f" * 64))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "llm-request-hash-inconsistent")


def test_system_prompt_hash_differing_between_requests_in_one_slice_fails(tmp_path):
    wire = fresh_wire()
    idx = find_index(wire, "llm.request", 2)
    wire = mutate(wire, idx, lambda o: o.__setitem__("systemPromptHash", "e" * 64))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "llm-request-hash-inconsistent")


def test_snapshot_hash_absent_fails(tmp_path):
    """Required in BOTH branches of Task 4 Step 1b."""
    wire = fresh_wire()
    idx = find_index(wire, "llm.tools_snapshot", 1)

    def drop_hash(o):
        del o["hash"]
    wire = mutate(wire, idx, drop_hash)
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "record-malformed")


def test_snapshot_hash_empty_fails(tmp_path):
    wire = fresh_wire()
    idx = find_index(wire, "llm.tools_snapshot", 1)
    wire = mutate(wire, idx, lambda o: o.__setitem__("hash", ""))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "session-scoped-content")


def test_requests_toolshash_disagreeing_with_snapshot_hash_fails(tmp_path):
    """Written only because Step 1b measured the two fields EQUAL on this
    client (llm.request.toolsHash == llm.tools_snapshot.hash, confirmed
    2026-07-31 and reconfirmed on the fix-round-1 recapture; see the
    manifest's toolsHashRound1 and the fresh fixture's own
    llm.tools_snapshot.hash - both 3174a328...8777). Consistent request
    hashes that disagree with the snapshot describing the sent schemas are
    a disagreement, not a pass."""
    wire = fresh_wire()
    snap_idx = find_index(wire, "llm.tools_snapshot", 1)
    snapshot = json.loads(wire[snap_idx])
    assert snapshot["hash"] == MANIFEST["toolsHashRound1"], "Step 1b measurement did not hold"
    for n in (1, 2):
        idx = find_index(wire, "llm.request", n)
        wire = mutate(wire, idx, lambda o: o.__setitem__("toolsHash", "d" * 64))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "snapshot-hash-mismatch")


def test_tools_hash_differing_from_prior_state_on_later_round_fails(tmp_path):
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(sess_dir, toolsHash="c" * 64))
    assert_failed(run_resume(sess_dir, state_path), "hash-discontinuity")


def test_system_prompt_hash_differing_from_prior_state_on_later_round_fails(tmp_path):
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(sess_dir, systemPromptHash="9" * 64))
    assert_failed(run_resume(sess_dir, state_path), "hash-discontinuity")


@pytest.mark.parametrize("field,broken", [
    ("provider=kimi", "provider=notkimi"),
    ("modelAlias=fixture-model/x", "modelAlias=wrong-model/y"),
    ("thinkingEffort=high", "thinkingEffort=max"),
])
def test_log_line_field_wrong_while_requests_correct_fails(tmp_path, field, broken):
    """r3's inequality cases covered requests only."""
    log = fresh_log()
    idx = next(i for i, l in enumerate(log) if "llm config" in l)
    assert field in log[idx]
    log[idx] = log[idx].replace(field, broken)
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), log)
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "log-config-field")


def test_turn_prompt_text_not_hashing_to_expected_brief_fails(tmp_path):
    wire = fresh_wire()
    idx = find_index(wire, "turn.prompt", 1)
    wire = mutate(wire, idx, lambda o: o.__setitem__(
        "input", [{"type": "text", "text": "a completely different brief"}]))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "brief-hash")


def _deny_listing(path):
    """Deny THIS user read-data on `path`, so a recursive walk over its
    parent raises instead of silently returning fewer entries. Returns the
    principal, for the caller's cleanup."""
    principal = "%s\\%s" % (os.environ["USERDOMAIN"], os.environ["USERNAME"])
    proc = subprocess.run(["icacls", str(path), "/deny", "%s:(RD)" % principal],
                          capture_output=True, text=True, timeout=60)
    if proc.returncode != 0:
        pytest.fail("could not deny listing on %s: %s" % (path, proc.stdout + proc.stderr))
    return principal


def _undeny_listing(path, principal):
    subprocess.run(["icacls", str(path), "/remove:d", principal],
                   capture_output=True, text=True, timeout=60)


def test_an_unreadable_sessions_subtree_fails_rather_than_shortening_the_inventory(tmp_path):
    """Rule 3 requires EXACTLY ONE new session leaf, so an enumeration that
    silently drops entries can satisfy it on an inventory that was never
    taken. The walk used -ErrorAction SilentlyContinue, so this exact
    layout - the expected leaf visible, a SECOND concurrent leaf inside a
    subtree this user cannot list - passed as a clean fresh round. It must
    refuse: an unmade measurement is never a clean one."""
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    hidden = root / "wd_other"
    (hidden / "session_a_concurrent_debate").mkdir(parents=True)
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())

    principal = _deny_listing(hidden)
    try:
        proc = run_fresh(root, FIXTURE_SESSION_ID, state_path)
    finally:
        _undeny_listing(hidden, principal)

    assert_failed(proc, "session-inventory-unreadable")


def test_the_denied_subtree_is_what_makes_that_case_fail(tmp_path):
    """The positive control for the test above. Without the deny, the same
    layout resolves the session and the round is clean - so that test is
    measuring the unreadable subtree and not some unrelated defect in the
    two-workspace layout."""
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    (root / "wd_other" / "session_a_concurrent_debate").mkdir(parents=True)
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())

    proc = run_fresh(root, FIXTURE_SESSION_ID, state_path)
    p = parsed(proc)
    assert p["status"] == "failed", proc.stdout + proc.stderr
    assert "session-not-resolvable" in p["reason"], p["reason"]
    assert "2 new session" in p["reason"], p["reason"]


# --- case-only differences, one per comparison class --------------------
#
# PowerShell's -eq/-ne and Compare-Object are case-INSENSITIVE (measured),
# so before these were made case-exact a round could declare `AUTO`, carry
# a tool named `read` where the allowlist says `Read`, or name a
# case-variant provider, and still be attributed to the declared
# configuration. Each case below targets a DIFFERENT comparison, so
# neutering one cannot be masked by another catching the mutation.


def test_permission_mode_differing_only_in_case_fails(tmp_path):
    wire = fresh_wire()
    idx = find_index(wire, "permission.set_mode", 1)
    wire = mutate(wire, idx, lambda o: o.__setitem__("mode", "AUTO"))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path),
                  "permission.set_mode.mode is not 'auto'")


def test_a_record_type_differing_only_in_case_is_not_that_record(tmp_path):
    """A record type is matched, not parsed, so a case variant must not
    satisfy the type. Renaming the only permission.set_mode record leaves
    ZERO of them, which is what the count check must see."""
    wire = fresh_wire()
    idx = find_index(wire, "permission.set_mode", 1)
    wire = mutate(wire, idx, lambda o: o.__setitem__("type", "Permission.Set_Mode"))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "session-scoped")


def test_an_active_tool_name_differing_only_in_case_fails(tmp_path):
    """Compare-Object without -CaseSensitive treats `read` and `Read` as
    equal, so the allowlist comparison used to pass on a tool the agent
    file never authorized under that spelling."""
    wire = fresh_wire()
    idx = find_index(wire, "tools.set_active_tools", 1)

    def _lower_first(o):
        o["names"][0] = o["names"][0].lower()

    original = json.loads(wire[idx])["names"][0]
    assert original != original.lower(), (
        "this fixture's first tool name must have an upper-case letter for "
        "the mutation to be a case-only change")
    wire = mutate(wire, idx, _lower_first)
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "session-scoped-content")


def test_an_llm_request_provider_differing_only_in_case_fails(tmp_path):
    wire = fresh_wire()
    idx = find_index(wire, "llm.request", 1)
    wire = mutate(wire, idx, lambda o: o.__setitem__("provider", FIXTURE_PROVIDER.upper()))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "llm-request-field")


def test_parsed_rejects_stray_output_before_the_json():
    """The helper's own failing direction. It used to take the LAST line,
    so this exact shape passed."""
    class _Proc:
        stdout = 'noise\n{"status":"clean"}\n'
        stderr = ""

    with pytest.raises(AssertionError, match="exactly one nonempty line"):
        parsed(_Proc())


def test_parsed_accepts_one_line_with_a_trailing_newline():
    class _Proc:
        stdout = '{"status":"clean"}\n'
        stderr = ""

    assert parsed(_Proc()) == {"status": "clean"}


# --- strict decoding of the evidence itself ------------------------------


def _corrupt_one_byte_inside_a_string(path, marker):
    raw = path.read_bytes()
    assert marker in raw, marker
    path.write_bytes(raw.replace(marker, marker[:2] + b"\x80" + marker[2:], 1))


def test_an_invalid_byte_in_the_wire_slice_fails(tmp_path):
    """The byte goes into a string NOTHING later requires - the metadata
    record's protocol_version - so under replacement decoding every
    required token survives and the round reports CLEAN. Corrupting a
    required token instead only proves which failure wins, which is what
    the first version of this test did."""
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    _corrupt_one_byte_inside_a_string(
        sess_dir / "agents" / "main" / "wire.jsonl", b'"protocol_version":"1.4"')
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "wire-malformed")


def test_an_invalid_byte_in_the_log_slice_fails(tmp_path):
    """The byte goes into a log line the rules never read - `llm response`
    - so under replacement decoding the one `llm config` line is still
    found, still matches, and the round reports CLEAN."""
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    _corrupt_one_byte_inside_a_string(
        sess_dir / "logs" / "kimi-code.log", b"llm response")
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "log-config-malformed")


def test_an_invalid_byte_in_the_agent_file_fails(tmp_path):
    """The fourth strict input. The byte goes into a frontmatter field
    this tool does not read, so under replacement decoding the name, the
    body and the tool list are all unchanged and the round reports
    CLEAN."""
    agent_bytes = AGENT_FILE.read_bytes()
    marker = b"description:"
    assert marker in agent_bytes, "this oracle needs an unread frontmatter field"
    corrupted = tmp_path / "agent-with-a-bad-byte.md"
    idx = agent_bytes.index(marker) + len(marker) + 4
    corrupted.write_bytes(agent_bytes[:idx] + bytes([0x80]) + agent_bytes[idx:])

    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path,
                            agent_file=corrupted), "agent-file-unusable")


def test_the_same_agent_file_without_the_invalid_byte_is_clean(tmp_path):
    """The control for the case above: the same COPIED file, uncorrupted,
    so the copy itself is not what fails."""
    copied = tmp_path / "agent-copy.md"
    copied.write_bytes(AGENT_FILE.read_bytes())
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_clean(run_fresh(root, FIXTURE_SESSION_ID, state_path, agent_file=copied))


def test_an_invalid_byte_in_the_prior_state_fails(tmp_path):
    """The invalid byte sits INSIDE a string value, so a substituting
    decoder still produces parseable JSON and the state is accepted. A
    byte placed in the structural JSON instead would fail on the parse
    whatever the decoder does, which measures the parser rather than the
    decoder - and that is what the first version of this test did."""
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    known = str(tmp_path / "sessions" / "wd_other" / "session_previously_known")
    write_json(state_path, fresh_prior_state(known_session_dirs=[known]))
    raw = state_path.read_bytes()
    marker = b"session_previously_known"
    assert marker in raw
    state_path.write_bytes(raw.replace(marker, marker[:7] + b"\x80" + marker[7:], 1))
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "prior-state-unusable")


def test_the_same_fixtures_uncorrupted_are_clean(tmp_path):
    """The positive control for all three above."""
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_clean(run_fresh(root, FIXTURE_SESSION_ID, state_path))


# --- the remaining case-exactness boundaries ------------------------------


def test_a_case_variant_required_key_in_a_record_is_malformed(tmp_path):
    """Record SHAPE validation used case-insensitive property membership,
    so a record carrying `Provider` satisfied the required `provider`."""
    wire = fresh_wire()
    idx = find_index(wire, "llm.request", 1)
    wire = mutate(wire, idx, lambda o: o.__setitem__("Provider", o.pop("provider")))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "record-malformed")


def test_a_case_variant_first_record_type_misaligns_the_slice(tmp_path):
    """The slice boundary compared the first record's type
    case-insensitively, so a slice starting at `Metadata` read as
    correctly aligned - the reviewer's own named example."""
    wire = fresh_wire()
    idx = find_index(wire, "metadata", 1)
    assert idx == 0, "this oracle must mutate the FIRST record of the slice"
    wire = mutate(wire, idx, lambda o: o.__setitem__("type", "Metadata"))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "slice-misaligned")


def test_a_case_only_profile_name_difference_fails(tmp_path):
    wire = fresh_wire()
    idx = find_index(wire, "config.update", 1)
    original = json.loads(wire[idx]).get("profileName")
    assert original and original != original.upper()
    wire = mutate(wire, idx, lambda o: o.__setitem__("profileName", original.upper()))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "profileName")


def test_a_case_only_system_prompt_difference_fails(tmp_path):
    """The recorded system prompt is compared to the agent file's body.
    A case-only difference is a DIFFERENT prompt."""
    wire = fresh_wire()
    idx = find_index(wire, "config.update", 1)
    original = json.loads(wire[idx]).get("systemPrompt")
    assert original and original != original.upper()
    wire = mutate(wire, idx, lambda o: o.__setitem__("systemPrompt", original.upper()))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "systemPrompt")


# --- kind and session identity are case-exact ---------------------------


def test_a_case_variant_prior_state_kind_is_rejected(tmp_path):
    """`Fresh` is not `fresh`. The literal used to be matched
    case-insensitively, so a state declaring `Fresh` was accepted AND
    routed as a fresh call."""
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    state = fresh_prior_state()
    state["kind"] = "Fresh"
    write_json(state_path, state)
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path), "prior-state-unusable")


def test_a_case_variant_session_id_from_stdout_is_a_mismatch(tmp_path):
    """The session id is a token the client issued and this tool binds a
    round to, so its case is identity. The resolved directory PATH beside
    it stays case-insensitive, because Windows paths are not."""
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID.upper(), state_path),
                  "session-id-mismatch")


def test_the_exact_session_id_is_clean(tmp_path):
    """The control: the same call with the id spelled exactly."""
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_clean(run_fresh(root, FIXTURE_SESSION_ID, state_path))


# --- key membership, through the ONE helper that decides it -------------


@pytest.mark.parametrize("record_type,key,variant", [
    ("llm.request", "provider", "Provider"),
    ("llm.request", "toolsHash", "ToolsHash"),
    ("turn.prompt", "input", "Input"),
    ("llm.tools_snapshot", "hash", "Hash"),
    ("tools.set_active_tools", "names", "Names"),
    ("permission.set_mode", "mode", "Mode"),
])
def test_a_case_variant_required_key_in_each_shape_branch_is_malformed(
        tmp_path, record_type, key, variant):
    """Key membership is decided in ONE helper, so one mutation covers
    every branch - but the branches are still independent expressions, so
    each is driven here rather than argued about."""
    wire = fresh_wire()
    idx = find_index(wire, record_type, 1)
    wire = mutate(wire, idx, lambda o: o.__setitem__(variant, o.pop(key)))
    root, sess_dir = build_fresh_layout(tmp_path, wire, fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    proc = run_fresh(root, FIXTURE_SESSION_ID, state_path)
    p = parsed(proc)
    assert p["status"] == "failed", p


def test_a_case_variant_prior_session_id_is_a_mismatch_on_resume(tmp_path):
    """The RESUME side of the same binding. Only the fresh branch had a
    case oracle, so reverting the resume comparison alone left the suite
    green while a case-variant prior identity was accepted."""
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    state_path = tmp_path / "state.json"
    state = resume_prior_state(sess_dir)
    state["sessionId"] = state["sessionId"].upper()
    write_json(state_path, state)
    assert_failed(run_resume(sess_dir, state_path), "state-session-mismatch")


def test_the_exact_prior_session_id_is_clean_on_resume(tmp_path):
    """The control for the case above, same fixture, exact spelling."""
    sess_dir = build_resume_layout(tmp_path, resume_wire(), resume_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, resume_prior_state(sess_dir))
    assert_clean(run_resume(sess_dir, state_path))


def test_the_exact_prior_state_fixture_without_its_invalid_byte_is_clean(tmp_path):
    """The matching control for the prior-state decode case: the SAME
    known-session entry, absent only the invalid byte. Without it that
    case can still reduce to "the mutation changes which failure wins",
    because the shared clean control carries an EMPTY knownSessionDirs."""
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    known = str(tmp_path / "sessions" / "wd_other" / "session_previously_known")
    write_json(state_path, fresh_prior_state(known_session_dirs=[known]))
    assert_clean(run_fresh(root, FIXTURE_SESSION_ID, state_path))


# --- BOM: this change now owns the behaviour Get-Content used to give ---


def test_a_bom_prefixed_prior_state_is_clean(tmp_path):
    """`Get-Content -Encoding UTF8` stripped a leading BOM, so replacing it
    means this code owns that behaviour. Without -StripBom the BOM
    character reaches ConvertFrom-Json and the parse fails, so this is a
    distinguishing control, not a cosmetic one."""
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    state_path.write_bytes(b"\xef\xbb\xbf" + state_path.read_bytes())
    assert_clean(run_fresh(root, FIXTURE_SESSION_ID, state_path))


def test_a_bom_prefixed_agent_file_is_clean(tmp_path):
    """The same ownership question for the other whole-file reader."""
    bom_agent = tmp_path / "agent-with-bom.md"
    bom_agent.write_bytes(b"\xef\xbb\xbf" + AGENT_FILE.read_bytes())
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_clean(run_fresh(root, FIXTURE_SESSION_ID, state_path, agent_file=bom_agent))


# --- the three ORDINAL comparisons, each driven on its own ---------------
#
# Culture-sensitive matching treats several zero-width characters as
# absent, so each of these comparisons accepts a visually deceptive input
# without the ordinal overload. The BOM controls above cannot reach them:
# they prove -StripBom is required, not that the comparison is ordinal.

ZWNJ = "\u200c"
BOM_CHAR = "\ufeff"


def test_a_zero_width_prefixed_agent_file_does_not_open_with_the_marker(tmp_path):
    """U+200C is NOT stripped by -StripBom (only a leading BOM is), so it
    reaches the marker check. Culture-sensitive StartsWith ignores it and
    accepts the file."""
    agent = tmp_path / "zwnj-agent.md"
    agent.write_text(ZWNJ + AGENT_FILE.read_text(encoding="utf-8"), encoding="utf-8")
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path, agent_file=agent),
                  "agent-file-unusable")


def test_a_zero_width_inside_the_closing_marker_never_closes_the_frontmatter(tmp_path):
    """The closing search is the second ordinal comparison. A marker
    spelled `-<BOM>--` is not `---`, but a culture-sensitive IndexOf finds
    it anyway."""
    body = AGENT_FILE.read_text(encoding="utf-8").replace("\r\n", "\n")
    opening, rest = body.split("\n", 1)
    assert opening == "---", opening
    closing_at = rest.index("\n---\n")
    deceptive = rest[:closing_at] + "\n-" + BOM_CHAR + "--\n" + rest[closing_at + 5:]
    agent = tmp_path / "deceptive-close-agent.md"
    agent.write_text(opening + "\n" + deceptive, encoding="utf-8")

    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())
    assert_failed(run_fresh(root, FIXTURE_SESSION_ID, state_path, agent_file=agent),
                  "agent-file-unusable")


def test_a_zero_width_prefixed_directory_is_not_a_session_leaf(tmp_path):
    """The third ordinal comparison. The frozen rule says a member's name
    BEGINS `session_` and nothing else, so `<BOM>session_decoy` is not a
    member - but a culture-sensitive StartsWith counts it, making two new
    leaves where there is one."""
    root, sess_dir = build_fresh_layout(tmp_path, fresh_wire(), fresh_log())
    decoy = root / "wd_x" / (BOM_CHAR + "session_decoy")
    decoy.mkdir()
    state_path = tmp_path / "state.json"
    write_json(state_path, fresh_prior_state())

    p = assert_clean(run_fresh(root, FIXTURE_SESSION_ID, state_path))
    assert p["nextState"]["sessionId"] == FIXTURE_SESSION_ID, p
