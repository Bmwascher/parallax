"""Contract pins for the Flash implementer lane (agents/flash-implementer.md).

Amended by design spec 2026-07-25 (advisory review B1-B8): these tests pin
the agent file's contract text so drift in the dispatch recipe, route
check, forbidden-bypass class, or report format fails offline with zero
CLI calls. Since backlog item 110 the Flash agent file is the only allowed
home for the implementer model literal, and the escalation lane
(agents/escalation-implementer.md) is the shared-contract parity twin:
the direct-typing Claude implementer was deleted in 0.39.0.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FLASH = REPO / "agents" / "flash-implementer.md"
ESCALATION = REPO / "agents" / "escalation-implementer.md"
RETIRED = REPO / "agents" / "implementer.md"
FPF = REPO / "skills" / "multi-model-verify" / "references" / "frozen-plan-format.md"
CANONICAL_ID = "gemini-3.8-flash-high"
SHARED_START = "<!-- shared-contract:start -->"
SHARED_END = "<!-- shared-contract:end -->"


def _read(p):
    return p.read_text(encoding="utf-8")


def _frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert m, "missing frontmatter"
    return m.group(1)


def test_flash_frontmatter_pins_model_and_tools():
    fm = _frontmatter(_read(FLASH))
    # sonnet since 0.38.0: every control in this lane is a prose rule the
    # wrapper follows (backlog item 105); agy print mode changed between
    # 1.1.7 and 1.2.x (the Dispatch step of the agent file) and 1.2.2
    # does not consult the trust list (item 105), so the seat needs to
    # block on a missing log line rather than rationalize a landed edit
    assert re.search(r"^model: sonnet$", fm, re.MULTILINE)
    m = re.search(r"^tools: (.+)$", fm, re.MULTILINE)
    assert m, "tools allowlist missing"
    tools = [t.strip() for t in m.group(1).split(",")]
    assert sorted(tools) == ["Bash", "Glob", "Grep", "Read"]


def test_flash_dispatch_contract():
    body = _read(FLASH)
    assert "--model " + CANONICAL_ID in body
    assert "--add-dir" in body
    assert "--log-file" in body
    assert "--mode accept-edits" in body
    assert body.count("--mode accept-edits") >= 2
    assert ("--model " + CANONICAL_ID + " --mode accept-edits --add-dir"
            ) in body
    assert "command execution stays denied" in body
    assert "Windows spelling" in body
    assert "a Git-Bash `/c/...` spelling produced NO log" in body
    assert "one run with `false` ended with the key removed" in body
    assert "AGY-TASK-BRIEF-" in body
    assert "sole transient exception" in body.lower()
    assert "the dispatch log file's basename" in body
    assert "on success, failure, and interruption alike" in body
    assert ("Do not run commands or attempt verification - the wrapper "
            "runs all verification after you finish; your only job is "
            "the file edits.") in body
    assert "stdin" not in body.lower() or "does not reach" in body.lower()


def test_flash_route_check_strings():
    body = _read(FLASH)
    assert 'Print mode: starting' in body
    assert 'model="' + CANONICAL_ID + '"' in body
    assert "Propagating selected model override" in body
    assert "Print mode: applying agent mode accept-edits" in body
    assert "requested and propagated" in body
    assert "used and confirmed" not in body.replace(
        'never "used and confirmed"', "")
    assert "transcript_full.jsonl" in body
    assert "Print mode: conversation=<uuid>" in body
    assert 'conversationID=""' in body
    assert "parse `conversationID=" not in body
    assert "an empty id is a missing transcript, not a wildcard" in body
    assert "exactly one distinct uuid" in body
    assert "the requested mode is not corroborated by the log" in body
    assert ("every path git status reports changed must appear in the "
            "brain transcript as a successful file-changing action"
            ) in body.lower()


def test_flash_preflight_pins():
    body = _read(FLASH)
    assert "agy models" in body
    assert "trustedWorkspaces" in body
    assert "any `write_file(` entry, whatever path it names" in body
    assert "allow rule" in body
    assert "git status --porcelain" in body
    assert "No file matching `AGY-TASK-BRIEF-*`" in body
    assert "any directory listed in `trustedWorkspaces`" in body
    assert "the workspace directory or an ancestor of it" in body
    assert "a worktree needs its own entry" not in body
    assert "agy itself does not consult it" in body
    assert "case-insensitive" in body
    assert "plus a separator" in body
    assert "no trailing separator" in body
    assert "must equal the workspace path or" in body
    assert "Task 6" not in body


def test_flash_route_report_carries_transcript():
    body = _read(FLASH)
    assert "AND the brain transcript's path" in body


def test_flash_forbidden_bypass_class():
    body = _read(FLASH)
    assert "--dangerously-skip-permissions" in body
    idx = body.find("--dangerously-skip-permissions")
    window = body[max(0, idx - 200):idx + 200].lower()
    assert "never" in window or "forbidden" in window
    assert "persisted" in body and "settings" in body
    assert "`--mode accept-edits` is not a member of that class" in body
    assert "No other `--mode` value is used in this lane" in body


def test_flash_report_headings():
    body = _read(FLASH)
    for heading in ("**STATUS:**", "**ROUTE:**", "**FILES CHANGED:**",
                    "**VERIFICATION:**", "**DEVIATIONS:**"):
        assert heading in body, heading
    twin = _read(ESCALATION)
    for heading in ("STATUS - ", "FILES CHANGED - ", "VERIFICATION - ",
                    "DEVIATIONS - "):
        assert heading in twin, heading


def _shared_block(text, path):
    assert SHARED_START in text and SHARED_END in text, (
        "missing shared-contract markers in " + str(path))
    return text.split(SHARED_START)[1].split(SHARED_END)[0]


def test_shared_contract_parity():
    assert _shared_block(_read(FLASH), FLASH) == _shared_block(
        _read(ESCALATION), ESCALATION)


def test_agent_frontmatter_routes():
    flash_fm = _frontmatter(_read(FLASH))
    assert "THE build lane for every frozen-plan task" in flash_fm
    assert "dispatch this agent, and no other implementer," in flash_fm
    assert "not implementer," not in flash_fm
    escalation_fm = _frontmatter(_read(ESCALATION))
    assert "consent-gated reroutes of blocked tasks" in escalation_fm
    assert "which is EMPTY for a reroute" in escalation_fm


def test_flash_lane_is_the_declared_default():
    fpf = _read(FPF)
    assert "Build lane: parallax:flash-implementer" in fpf
    assert "no `ROUTE:` line is a lane violation" in fpf
    assert "**Lane:** parallax:escalation-implementer" in fpf
    assert "(consented reroute, <ledger path>)" in fpf
    assert "agents/implementer.md" not in fpf


def test_empty_envelope_is_zero_judgment():
    fpf = _read(FPF)
    assert "Any DECISIONS entry on an empty envelope is drift" in fpf


def test_escalation_empty_envelope_is_zero_judgment():
    body = _read(ESCALATION)
    assert "its envelope is EMPTY by construction" in body
    assert "any DECISIONS entry you write on it is drift" in body
    assert "An empty envelope means an empty section" in body


def test_direct_typing_claude_lane_is_gone():
    assert not RETIRED.exists()
    body = _read(FLASH)
    assert "Two swap paths" in body
    assert "stays the SUPERVISOR" in body
    assert "`implementer.md` pins its own lane's model" not in body
    assert "every other surface points at this file" in body


SWEEP_GLOBS = [
    "skills/**/*.md", "commands/*.md", "tools/*.ps1", "hooks/*",
    "evals/**/*.py", "evals/**/*.json", "evals/**/*.ps1",
    "README.md", "CLAUDE.md", "agents/*.md",
]
ALLOWED = {FLASH.resolve(), Path(__file__).resolve()}


def test_flash_literal_single_source():
    offenders = []
    for pattern in SWEEP_GLOBS:
        for p in REPO.glob(pattern):
            if p.resolve() in ALLOWED:
                continue
            if "gemini-3.8-flash" in p.read_text(encoding="utf-8",
                                                 errors="replace"):
                offenders.append(str(p))
    assert offenders == []


def test_retired_lane_paths_swept_from_live_surfaces():
    offenders = []
    for pattern in SWEEP_GLOBS:
        for p in REPO.glob(pattern):
            if p.resolve() == Path(__file__).resolve():
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
            if re.search(r"(?<![\w-])implementer\.md", text):
                offenders.append(str(p))
    assert offenders == []


def test_sonnet_implementer_literals_removed():
    readme = _read(REPO / "README.md")
    assert "currently `model: sonnet`" not in readme
    assert "`haiku`/`opus` are drop-ins" not in readme
    assert "any Claude tier is a drop-in" in readme
    assert "its Lane note carries the two swap paths" in readme
    fpf = _read(FPF)
    assert "Sonnet 5" not in fpf
    assert "the pinned lane in `agents/`" in fpf
