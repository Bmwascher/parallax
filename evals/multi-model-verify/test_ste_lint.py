"""Tests for evals/tools/ste_lint.py (item 103).

One failing fixture per rule, so every refusal is proven able to fire,
and one passing fixture per exemption, so the allowlist and the text
handling (code spans, URLs, headings, list items) are proven to work.
The last tests run the checker on the real CHANGELOG.md and through
check_changelog.py, which is the CI path.
"""
import importlib.util
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TOOLS = REPO / "evals" / "tools"


def _load(name):
    spec = importlib.util.spec_from_file_location(name, TOOLS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ste = _load("ste_lint")
EMPTY = {"ing": set(), "state": set(), "word": set()}


def rules(text, allow=None):
    return [f.rule for f in ste.lint_text(text, allow or EMPTY)]


def test_clean_text_has_no_findings():
    assert rules("The tool reads the file. It prints the version.\n") == []


def test_sentence_over_25_words_is_refused():
    text = " ".join(["word"] * 26) + ".\n"
    assert rules(text) == ["sentence length"]
    assert rules(" ".join(["word"] * 25) + ".\n") == []


def test_paragraph_over_6_sentences_is_refused():
    text = " ".join(["The tool runs."] * 7) + "\n"
    assert "paragraph length" in rules(text)
    assert "paragraph length" not in rules(" ".join(["The tool runs."] * 6) + "\n")


def test_passive_voice_is_refused():
    assert rules("The file is written by the tool.\n") == ["passive voice"]
    assert rules("The file was not written.\n") == ["passive voice"]
    assert rules("The round is voided.\n") == ["passive voice"]


def test_state_participle_after_be_is_allowed_from_the_allowlist():
    allow = dict(EMPTY, state={"closed"})
    assert rules("The item is closed.\n", allow) == []
    assert rules("The item is closed.\n") == ["passive voice"]


def test_words_that_end_in_ed_but_are_not_participles_pass():
    assert rules("The count is indeed 5.\n") == []


def test_ing_verb_form_is_refused():
    assert rules("The tool is checking the file.\n") == ["-ing form"]
    assert rules("Checking the file takes time.\n") == ["-ing form"]


def test_ing_nouns_pass_from_the_builtin_and_the_allowlist():
    assert rules("Nothing changes during the run.\n") == []
    assert rules("Typed binding exits 1.\n") == ["-ing form"]
    assert rules("Typed binding exits 1.\n", dict(EMPTY, ing={"binding"})) == []


def test_contraction_is_refused():
    assert rules("The tool doesn't stop.\n") == ["contraction"]
    assert rules("The tool's output is short.\n") == []


def test_unapproved_modal_is_refused():
    for modal in ("should", "would", "might", "may", "shall"):
        assert rules("The tool %s stop.\n" % modal) == ["unapproved modal"], modal
    assert rules("The tool must stop. The tool can stop. The tool will stop.\n") == []


def test_unapproved_word_and_phrase_are_refused_with_the_alternative():
    findings = ste.lint_text("Utilize the tool in order to start.\n", EMPTY)
    assert [f.rule for f in findings] == ["unapproved word", "unapproved word"]
    details = " | ".join(f.detail for f in findings)
    assert "'utilize'; use use" in details
    assert "'in order to'; use to" in details


def test_denylisted_word_used_as_a_name_passes_from_the_allowlist():
    allow = dict(EMPTY, word={"verified"})
    assert rules("Refresh the Verified line.\n", allow) == []


def test_code_spans_urls_and_links_count_as_one_word_and_are_not_read():
    text = ("Run `utilize --should --checking` at https://example.test/utilize/should "
            "and read [the utilize page](https://example.test/x).\n")
    findings = ste.lint_text(text, EMPTY)
    assert [f.rule for f in findings] == ["unapproved word"]
    assert "'utilize'" in findings[0].detail
    words = ste._words(ste._normalize("`" + " ".join(["a"] * 30) + "` runs.\n"))
    assert words == ["CODESPAN", "runs"]


def test_headings_are_skipped_and_list_items_are_paragraphs():
    text = ("## Utilizing the checking should\n"
            "\n"
            "- The first item runs. " + " ".join(["The tool runs."] * 6) + "\n"
            "- The second item runs.\n")
    findings = ste.lint_text(text, EMPTY)
    assert [(f.line, f.rule) for f in findings] == [(3, "paragraph length")]


def test_continuation_lines_join_their_list_item():
    text = ("- The tool reads the file and then it prints the version and then it\n"
            "  prints the tag and then it prints the date and then it stops now.\n")
    findings = ste.lint_text(text, EMPTY)
    assert [f.rule for f in findings] == ["sentence length"]
    assert findings[0].line == 1


def test_allowlist_file_parses_and_refuses_an_unknown_category(tmp_path):
    good = tmp_path / "allow.txt"
    good.write_text("# comment\ning: Binding\nstate: closed  # trailing\n", encoding="utf-8")
    allow = ste.load_allowlist(good)
    assert allow["ing"] == {"binding"} and allow["state"] == {"closed"}
    bad = tmp_path / "bad.txt"
    bad.write_text("noun: thing\n", encoding="utf-8")
    try:
        ste.load_allowlist(bad)
    except ValueError as exc:
        assert "unknown category" in str(exc)
    else:
        raise AssertionError("an unknown category must be refused")


def test_command_line_exit_codes(tmp_path):
    clean = tmp_path / "clean.md"
    clean.write_text("The tool runs.\n", encoding="utf-8")
    dirty = tmp_path / "dirty.md"
    dirty.write_text("The tool should be run.\n", encoding="utf-8")
    for path, expected in ((clean, 0), (dirty, 1), (tmp_path / "absent.md", 2)):
        proc = subprocess.run([sys.executable, str(TOOLS / "ste_lint.py"), str(path)],
                              capture_output=True, text=True, encoding="utf-8")
        assert proc.returncode == expected, (path, proc.stderr)


def test_repository_changelog_is_clean():
    ste_mod = _load("ste_lint")
    text = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    findings = ste_mod.lint_text(text, ste_mod.load_allowlist())
    assert findings == [], "\n".join(str(f) for f in findings)


def test_check_changelog_fails_on_an_ste_finding_and_skips_with_no_ste(tmp_path):
    (tmp_path / ".claude-plugin").mkdir()
    (tmp_path / ".claude-plugin" / "plugin.json").write_text(
        '{"version": "0.1.0"}', encoding="utf-8")
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\n## v0.1.0 (2026-09-13)\n\n- The file should be checked.\n",
        encoding="utf-8")
    checker = str(TOOLS / "check_changelog.py")
    proc = subprocess.run([sys.executable, checker, "--repo-root", str(tmp_path)],
                          capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 1
    assert "STE: line 5: unapproved modal" in proc.stderr
    assert "STE: line 5: passive voice" in proc.stderr
    proc = subprocess.run([sys.executable, checker, "--repo-root", str(tmp_path), "--no-ste"],
                          capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 0, proc.stderr
