"""Contract tests for the 0.14.0 seat reshuffle.

Pins the three Fable seat agents, the panels reference, the required
fable review, the escalation decision envelope, and their routing.
Written RED-first; plan tasks 2-7 flip them green.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
AGENTS = REPO / "agents"
SKILL_DIR = REPO / "skills" / "multi-model-verify"
REFERENCES = SKILL_DIR / "references"


def _read(p):
    return p.read_text(encoding="utf-8")


def _frontmatter(text):
    m = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    assert m, "frontmatter block missing"
    return m.group(1)


def test_fable_reviewer_exists_and_pins():
    p = AGENTS / "fable-reviewer.md"
    assert p.is_file()
    body = _read(p)
    fm = _frontmatter(body)
    assert "model: fable" in fm
    # exact read-only grant - no Bash, no Edit/Write (0.13.0 lesson:
    # prose refusal under live tools is priming, not containment)
    assert "tools: Read, Grep, Glob" in fm
    assert "Bash" not in fm
    assert "raw reply is retained as a range-bound artifact" in body
    assert "never replaces the cross-vendor gate" in body


def test_fable_panel_reviewer_exists_and_pins():
    p = AGENTS / "fable-panel-reviewer.md"
    assert p.is_file()
    body = _read(p)
    fm = _frontmatter(body)
    assert "model: fable" in fm
    assert "tools: Read, Grep, Glob" in fm
    assert "Bash" not in fm
    assert "dispatch metadata" in body
    assert "the resume surface carries no model parameter" in body
    assert "probed 2026-07-26" in body
    assert "cite the subject revision" in body


def test_escalation_implementer_exists_and_pins():
    p = AGENTS / "escalation-implementer.md"
    assert p.is_file()
    body = _read(p)
    fm = _frontmatter(body)
    assert "model: fable" in fm
    assert "enumerated decision envelope" in body
    assert "DECISIONS" in body
    assert "DEVIATIONS - must be `none`" in body
    assert "only with user consent" in body


def test_skill_routes_required_review_and_panels():
    skill = _read(SKILL_DIR / "SKILL.md")
    required = ("Required before round 1: the agents/fable-reviewer.md "
                "whole-branch review runs on the same range, its raw "
                "reply is retained as a range-bound artifact, and the "
                "round-1 brief cites that artifact with the session's "
                "per-finding adjudications.")
    assert skill.count(required) == 1
    assert skill.count("Panels: any reviewer-lane combination per "
                       "references/panels.md.") == 2
    assert skill.count("a finding, with one carve-out: "
                       "envelope-designated escalation-lane DECISIONS") == 1


def test_panels_reference_pins():
    p = REFERENCES / "panels.md"
    assert p.is_file()
    body = _read(p)
    assert ("Valid compositions: Sol+Kimi, Sol+Fable, Kimi+Fable, "
            "Sol+Kimi+Fable.") in body
    assert ("Every panel contains at least one cross-vendor lane "
            "(Sol or Kimi); an all-Claude panel is invalid.") in body
    assert ("A terminal verdict counts only when it cites the FINAL "
            "subject revision; a verdict against a stale revision is "
            "input, never terminal.") in body
    assert "hub-and-spoke" in body


def test_backup_lane_panel_participation():
    bl = _read(REFERENCES / "backup-lane.md")
    assert ("Panel participation: a user-invoked panel per "
            "references/panels.md is a second sanctioned entry route - "
            "the invocation itself is the consent, with no fallbacks "
            "banner (nothing degraded); containment, per-round "
            "evidence, and the write-probe apply unchanged, and no "
            "failure class is recorded because nothing "
            "substituted.") in bl


def test_fallbacks_panel_lane_loss():
    fb = _read(REFERENCES / "fallbacks.md")
    assert "panel-lane-loss" in fb
    assert ("A lost lane stops the panel at the consent gate - "
            "continuing with fewer lanes never happens "
            "automatically.") in fb
    assert "records DEGRADED" in fb


def test_plan_format_panel_and_envelope_pins():
    fmt = _read(REFERENCES / "frozen-plan-format.md")
    assert ("A panel records Verification status: FULL only when every "
            "participating lane's per-round evidence was clean AND "
            "every terminal verdict cites the final subject "
            "revision.") in fmt
    assert ("A task the plan routes to the escalation lane carries an "
            "enumerated decision envelope; DECISIONS inside the "
            "envelope are authorized outcomes, not drift.") in fmt


def test_notes_driver_seat_sections():
    notes = _read(REFERENCES / "model-prompting-notes.md")
    assert "## The session driver seat" in notes
    assert "### Fable 5" in notes
    assert "### Opus 5" in notes
    assert "## Fable 5 (the session side)" not in notes
    assert "subagent-resume-probe.md" in notes
    # both runtime parsers still resolve the primary declaration and
    # the ordering rule holds (backup declarations stay behind it)
    m = re.search(r"Canonical model id: `([^`\n]+)`", notes)
    assert m and m.group(1)
    assert (notes.index("Canonical model id:")
            < notes.index("Canonical backup reviewer model id:"))


def test_readme_reshuffle_pins():
    readme = _read(REPO / "README.md")
    assert "## Panels" in readme
    assert "fable-reviewer" in readme
    assert "fable-panel-reviewer" in readme
    assert "escalation-implementer" in readme
    assert "private" not in readme.lower()
    # 0.13.0 pins survive the restructure byte-exact
    assert ('G -->|run backup lane| BK["cross-vendor backup reviewer'
            ) in readme
    assert ("references/backup-lane.md` | The cross-vendor backup "
            "reviewer lane") in readme
