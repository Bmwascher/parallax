"""Contract pins for the Kimi backup reviewer lane (0.13.0).

Design spec: docs/superpowers/specs/2026-07-25-kimi-backup-lane-design.md.
These pins lock the lane's transport command shape, containment
allowlist, per-round route+containment evidence rules, single-source
discipline, and fallback wiring - all offline, zero CLI calls.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
REFS = REPO / "skills" / "multi-model-verify" / "references"
BACKUP_LANE = REFS / "backup-lane.md"
AGENT_YAML = REFS / "kimi-reviewer-agent.yaml"
SYSTEM_MD = REFS / "kimi-reviewer-system.md"
NOTES = REFS / "model-prompting-notes.md"
FALLBACKS = REFS / "fallbacks.md"
PLAN_FORMAT = REFS / "frozen-plan-format.md"
BACKUP_ID = "kimi-code/k3-256k"
ALLOWLIST = [
    "kimi_cli.tools.todo:SetTodoList",
    "kimi_cli.tools.file:ReadFile",
    "kimi_cli.tools.file:ReadMediaFile",
    "kimi_cli.tools.file:Glob",
    "kimi_cli.tools.file:Grep",
]
FORBIDDEN_TOOL_MARKERS = ["WriteFile", "StrReplaceFile", "Shell",
                          "SearchWeb", "FetchURL", "tools.web",
                          "tools.shell"]


def _read(p):
    return p.read_text(encoding="utf-8")


def test_backup_artifacts_exist():
    for p in (BACKUP_LANE, AGENT_YAML, SYSTEM_MD):
        assert p.is_file(), str(p)


def test_notes_backup_declarations():
    notes = _read(NOTES)
    assert "Canonical backup reviewer model id: `" + BACKUP_ID + "`" in notes
    assert "Canonical backup thinking flag: `--thinking`" in notes
    # primary parse must survive the amendment, in BOTH parser dialects
    m = re.search(r"Canonical model id: `([^`]+)`", notes)
    assert m and m.group(1) and m.group(1) != BACKUP_ID
    mi = re.search(r"Canonical model id: `([^`]+)`", notes, re.IGNORECASE)
    assert mi and mi.group(1) == m.group(1)
    # backup labels collide with neither primary regex, case-insensitive
    assert not re.search(r"Canonical model id:",
                         "Canonical backup reviewer model id:",
                         re.IGNORECASE)
    # ordering: primary declarations precede the backup block
    assert notes.index("Canonical model id:") < notes.index(
        "Canonical backup reviewer model id:")


def test_agent_yaml_allowlist_exact():
    yaml_text = _read(AGENT_YAML)
    # exact LIST equality: extra, missing, or reordered tool entries all
    # fail - presence checks alone would tolerate an added WriteFile
    tools = re.findall(r'-\s+"([^"]+)"', yaml_text)
    assert tools == ALLOWLIST
    for marker in FORBIDDEN_TOOL_MARKERS:
        assert marker not in yaml_text, marker
    assert "system_prompt_path: ./kimi-reviewer-system.md" in yaml_text


def test_backup_files_no_backslash_paths():
    for p in (BACKUP_LANE, AGENT_YAML, SYSTEM_MD):
        assert "\\" not in _read(p), str(p)


def test_backup_lane_dispatch_and_resume_pins():
    body = _read(BACKUP_LANE)
    # the dispatch pin covers the COMPLETE command through -w and -p:
    # a dropped -w would dispatch the reviewer in the shell's cwd (the
    # same class the resume pin below guards), and a bare substring
    # check would stay green through it (final-review finding, 0.13.0)
    assert ("kimi --quiet --thinking -m <canonical-backup-model-id> "
            "--agent-file <plugin-checkout>/skills/multi-model-verify/"
            "references/kimi-reviewer-agent.yaml -w <throwaway-clone> -p"
            ) in body
    assert "KIMI-REVIEW-BRIEF.md" in body
    # the re-pinned resume is load-bearing: bare -r restores full tools,
    # model/thinking inherit from CONFIG DEFAULTS, and -w does not
    # inherit at all (a resume without it runs in the shell's cwd -
    # caught live against the real tree), so the pin covers the
    # COMPLETE resumed command through -w
    assert ("kimi --quiet -r <session-id> --agent-file <same yaml> -m "
            "<canonical-backup-model-id> --thinking -w <same clone>"
            ) in body
    assert "loads the DEFAULT agent with full write and shell tools" in body
    assert BACKUP_ID not in body  # placeholder discipline


def test_backup_lane_evidence_pins():
    body = _read(BACKUP_LANE)
    assert "capture the byte length of" in body
    assert ("exactly one new `Using LLM model:` line carrying the "
            "canonical backup id") in body
    assert "`Loading agent:` line naming the committed yaml" in body
    assert "`Loaded tools:` line equal to the allowlist exactly" in body
    assert "DISCARDED unread" in body
    assert ("explicit refusal in the reply, marker absent on disk, "
            "clone status delta empty") in body
    assert ("must list exactly the brief file and nothing else") in body
    assert "Never run `kimi export` inside a repo" in body


def test_fallbacks_backup_wiring():
    fb = _read(FALLBACKS)
    assert "[run backup lane (cross-vendor preserved)]" in fb
    # the banner itself carries the conditional-offer semantics and the
    # backup option's own consequence line, not just an Options entry
    assert "offered when a class below qualifies it; on request otherwise" in fb
    assert "reviewer reasoning effort" in fb
    # transport-broken mapping names its member classes
    assert "codex-missing" in fb and "model-rejected" in fb
    assert "quota-exhausted" in fb and "auth-expired" in fb
    assert "route-attribution" in fb
    assert "LLM not set" in fb
    assert "access_terminated_error" in fb


def test_plan_format_lane_substitution_pin():
    fmt = _read(PLAN_FORMAT)
    assert "lane substitution is NOT degradation" in fmt
    assert "backup cross-vendor lane substituted" in fmt


def test_skill_and_readme_route_the_lane():
    skill = _read(REPO / "skills" / "multi-model-verify" / "SKILL.md")
    assert "backup-lane.md" in skill
    # BOTH dispatch sections (mode plan and mode diff) carry the pointer
    # - "backup-lane.md somewhere in the file" would let either mode
    # drop it while staying green
    assert skill.count("Backup lane: same protocol, transport and "
                       "per-round evidence per "
                       "references/backup-lane.md.") == 2
    readme = _read(REPO / "README.md")
    # the table row alone also contains "run backup lane" - pin the
    # mermaid edge exactly so the flowchart cannot drop it while green
    assert ('G -->|run backup lane| BK["cross-vendor backup reviewer'
            ) in readme
    assert ("references/backup-lane.md` | The cross-vendor backup "
            "reviewer lane") in readme


SWEEP_GLOBS = [
    "skills/**/*.md", "skills/**/*.yaml", "commands/*.md", "tools/*.ps1",
    "hooks/*", "evals/**/*.py", "evals/**/*.json", "evals/**/*.ps1",
    "README.md", "CLAUDE.md", "agents/*.md",
    ".claude-plugin/*.json", ".githooks/*",
]
ALLOWED = {NOTES.resolve(), Path(__file__).resolve()}


def test_backup_literal_single_source():
    offenders = []
    for pattern in SWEEP_GLOBS:
        for p in REPO.glob(pattern):
            if not p.is_file() or p.resolve() in ALLOWED:
                continue
            if BACKUP_ID in p.read_text(encoding="utf-8",
                                        errors="replace"):
                offenders.append(str(p))
    assert offenders == []
