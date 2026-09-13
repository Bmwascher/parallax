"""Tests for evals/tools/check_changelog.py (items 102 and 103).

One failing fixture per rule, so every refusal is proven able to fail:
the newest section not matching plugin.json, a section body with nothing
in it, a version listed twice, a heading without a date, a requested
version with no section, and a section whose lead paragraph is not plain
prose. The `--print` path is checked to emit exactly the section body,
because that output IS the release page. The last test runs the checker
against the real repository, which is the CI step itself.
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CHECKER = REPO / "evals" / "tools" / "check_changelog.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_changelog", CHECKER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checker = _load()

LEAD = "The lead says what changed.\n"
CLEAN = (
    "# Changelog\n"
    "\n"
    "Preamble that is not a section.\n"
    "\n"
    "## v0.2.0 (2026-09-13)\n"
    "\n"
    + LEAD +
    "\n"
    "### Area\n"
    "\n"
    "- **Newest.** A change.\n"
    "\n"
    "## v0.1.0 (2026-09-01)\n"
    "\n"
    "The older lead.\n"
    "\n"
    "- Older change.\n"
)


def _repo(tmp_path, changelog=CLEAN, version="0.2.0"):
    (tmp_path / ".claude-plugin").mkdir(exist_ok=True)
    (tmp_path / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "x", "version": version}), encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text(changelog, encoding="utf-8")
    return tmp_path


def _run(repo, *args):
    proc = subprocess.run(
        [sys.executable, str(CHECKER), "--repo-root", str(repo), *args],
        capture_output=True, text=True, encoding="utf-8")
    return proc.returncode, proc.stdout, proc.stderr


def test_clean_fixture_passes(tmp_path):
    code, out, err = _run(_repo(tmp_path))
    assert code == 0, err
    assert "v0.2.0 section present" in out


def test_newest_section_must_match_plugin_version(tmp_path):
    code, _out, err = _run(_repo(tmp_path, version="0.3.0"))
    assert code == 1
    assert "newest section is v0.2.0 but .claude-plugin/plugin.json says 0.3.0" in err


def test_empty_section_body_is_refused(tmp_path):
    text = CLEAN.replace(LEAD + "\n### Area\n\n- **Newest.** A change.\n", "\n")
    code, _out, err = _run(_repo(tmp_path, changelog=text))
    assert code == 1
    assert "version 0.2.0: section body is empty" in err


def test_duplicate_version_is_refused(tmp_path):
    text = CLEAN + "\n## v0.1.0 (2026-08-01)\n\nA lead.\n\n- Again.\n"
    code, _out, err = _run(_repo(tmp_path, changelog=text))
    assert code == 1
    assert "version 0.1.0 has more than one section" in err


def test_heading_without_date_is_refused(tmp_path):
    text = CLEAN.replace("## v0.2.0 (2026-09-13)", "## v0.2.0")
    code, _out, err = _run(_repo(tmp_path, changelog=text))
    assert code == 1
    assert "heading is not '## vX.Y.Z (YYYY-MM-DD)'" in err


def test_requested_version_without_section_is_refused(tmp_path):
    code, out, err = _run(_repo(tmp_path), "--version", "0.9.9", "--print")
    assert code == 1
    assert out == ""
    assert "no section for v0.9.9" in err


def test_print_emits_exactly_the_section_body(tmp_path):
    """The printed body is the release page. It must hold the section's
    `###` headings (they are body, not delimiters), stop before the next
    `## ` heading, and carry no leading or trailing blank lines."""
    code, out, err = _run(_repo(tmp_path), "--version", "0.2.0", "--print")
    assert code == 0, err
    assert out == LEAD + "\n### Area\n\n- **Newest.** A change.\n"


def test_print_of_an_older_version_does_not_require_it_to_be_newest(tmp_path):
    code, out, _err = _run(_repo(tmp_path), "--version", "0.1.0", "--print")
    assert code == 0
    assert out == "The older lead.\n\n- Older change.\n"


def test_section_that_opens_with_a_heading_or_list_item_is_refused(tmp_path):
    for opener in ("### Area\n", "- A change.\n", "1. A change.\n"):
        text = CLEAN.replace(LEAD, opener)
        code, _out, err = _run(_repo(tmp_path, changelog=text))
        assert code == 1, opener
        assert "version 0.2.0: the section must open with a plain-language paragraph" in err


def test_lead_paragraph_with_code_path_or_url_is_refused(tmp_path):
    cases = (
        ("The lead names `a-tool`.\n", "has a code span"),
        ("The lead names tools/a-tool.ps1 here.\n", "names a file or path"),
        ("The lead names CHANGELOG.md here.\n", "names a file or path"),
        ("The lead links https://example.test/x here.\n", "has a URL"),
    )
    for lead, expected in cases:
        text = CLEAN.replace(LEAD, lead)
        code, _out, err = _run(_repo(tmp_path, changelog=text))
        assert code == 1, lead
        assert "version 0.2.0: the lead paragraph " + expected in err, err


def test_lead_paragraph_rule_stops_at_the_first_blank_line(tmp_path):
    """Code and paths are fine in the SECOND paragraph; only the lead is
    held to plain words."""
    text = CLEAN.replace(LEAD, LEAD + "\nRun `a-tool` from tools/a.ps1.\n")
    code, _out, err = _run(_repo(tmp_path, changelog=text))
    assert code == 0, err


def test_parse_sections_keeps_file_order():
    sections, errors = checker.parse_sections(CLEAN)
    assert errors == []
    assert [s[0] for s in sections] == ["0.2.0", "0.1.0"]
    assert sections[0][1] == "2026-09-13"


def test_missing_changelog_exits_2(tmp_path):
    (tmp_path / ".claude-plugin").mkdir()
    (tmp_path / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"version": "0.2.0"}), encoding="utf-8")
    code, _out, err = _run(tmp_path)
    assert code == 2
    assert "cannot read CHANGELOG.md" in err


def test_repository_changelog_names_the_plugin_version():
    """The CI step, run here so a local pytest catches a bump without an
    entry before the push does."""
    code, out, err = _run(REPO)
    assert code == 0, err
    version = json.loads((REPO / ".claude-plugin" / "plugin.json").read_text(
        encoding="utf-8"))["version"]
    assert "v%s section present" % version in out
