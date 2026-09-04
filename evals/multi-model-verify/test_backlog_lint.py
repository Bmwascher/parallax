"""Tests for evals/tools/backlog_lint.py (2026-09-04 backlog rewrite plan).

One failing fixture per rule, built by mutating the clean fixture in
memory, so that every rule is proven able to fail. Rule 7 (digest) has
its own class in this file; rules 8 to 12, --revision and --range are
added by later tasks in the same module.
"""
import datetime
import importlib.util
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "evals" / "multi-model-verify" / "fixtures" / "backlog"
TODAY = datetime.date(2026, 9, 4)


def _load():
    path = REPO / "evals" / "tools" / "backlog_lint.py"
    spec = importlib.util.spec_from_file_location("backlog_lint", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


lint = _load()


def clean_text():
    return (FIXTURES / "clean.md").read_text(encoding="utf-8")


def failures(text, rules=None):
    out = lint.check(text, repo_root=REPO, revision=None, today=TODAY,
                     rules=rules)
    return out


STRUCTURAL = (1, 2, 3, 4, 5, 6)


def test_parse_reads_items_groups_and_fields():
    doc = lint.parse(clean_text())
    assert [i.id for i in doc.items] == ["1", "2", "3", "4"]
    assert doc.items[0].fields[:3] == [("Status", "OPEN"),
                                       ("Cost", "one line of cost"),
                                       ("Pairs", "3")]
    name, value = doc.items[0].fields[3]
    assert name == "Verified" and lint.VERIFIED_RE.match(value)
    assert len(doc.items[0].fields) == 4
    assert [g.name for g in doc.groups] == [
        "First - breaks the review process", "Last - housekeeping"]
    assert doc.groups[0].ids == ["1", "3"]
    assert doc.items[0].body[0] == ""
    assert doc.items[0].body[1] == "Body of item one."


def test_parse_error_without_ranking_section():
    text = clean_text().replace("## Ranking", "## Ordering")
    with pytest.raises(lint.ParseError):
        lint.parse(text)


def test_parse_error_on_malformed_heading():
    text = clean_text().replace("## 2. A closed item", "## Item 2: closed")
    with pytest.raises(lint.ParseError):
        lint.parse(text)


def test_clean_fixture_passes_structural_rules():
    assert failures(clean_text(), rules=STRUCTURAL) == []


def test_rule_1_missing_required_field():
    text = clean_text().replace("Cost: one line of cost\n", "")
    out = failures(text, rules=STRUCTURAL)
    assert any(f.startswith("item 1: rule 1") and "Cost" in f for f in out)


def test_rule_1_field_forbidden_for_status():
    text = clean_text().replace("Status: DONE\n", "Status: DONE\nCost: x\n")
    out = failures(text, rules=STRUCTURAL)
    assert any(f.startswith("item 2: rule 1") and "Cost" in f for f in out)


def test_rule_1_wrong_order():
    text = clean_text().replace(
        "Status: OPEN\nCost: one line of cost\n",
        "Cost: one line of cost\nStatus: OPEN\n")
    out = failures(text, rules=STRUCTURAL)
    assert any(f.startswith("item 1: rule 1") and "order" in f for f in out)


def test_rule_1_unknown_field():
    text = clean_text().replace("Pairs: 3\n", "Pairs: 3\nOwner: me\n")
    out = failures(text, rules=STRUCTURAL)
    assert any(f.startswith("item 1: rule 1") and "Owner" in f for f in out)


def test_rule_1_bad_status_value():
    text = clean_text().replace("Status: OPEN", "Status: OPEN (mostly)")
    out = failures(text, rules=STRUCTURAL)
    assert any(f.startswith("item 1: rule 1") and "Status" in f for f in out)


def test_rule_1_closed_value_shape():
    text = clean_text().replace("Closed: 0.29.0", "Closed: yesterday")
    out = failures(text, rules=STRUCTURAL)
    assert any(f.startswith("item 2: rule 1") and "Closed" in f for f in out)


def test_rule_2_duplicate_id():
    text = clean_text().replace("## 4. A gone item", "## 2. A gone item")
    out = failures(text, rules=STRUCTURAL)
    assert any(f.startswith("item 2: rule 2") for f in out)


def test_rule_2_non_integer_id_other_than_47ab():
    text = clean_text().replace("## 4. A gone item", "## 4b. A gone item")
    with pytest.raises(lint.ParseError):
        lint.parse(text)


def test_rule_3_prose_in_ranking():
    text = clean_text().replace("- 1\n", "- 1\nmoved here on Tuesday\n")
    out = failures(text, rules=STRUCTURAL)
    assert any(f.startswith("ranking: rule 3") for f in out)


def test_rule_3_position_number_rejected():
    text = clean_text().replace("- 1\n", "1. 1\n")
    out = failures(text, rules=STRUCTURAL)
    assert any(f.startswith("ranking: rule 3") for f in out)


def test_rule_4_open_item_not_ranked():
    text = clean_text().replace("- 3\n", "")
    out = failures(text, rules=STRUCTURAL)
    assert any(f.startswith("item 3: rule 4") for f in out)


def test_rule_4_ranked_twice():
    text = clean_text().replace("- 3\n", "- 3\n- 3\n")
    out = failures(text, rules=STRUCTURAL)
    assert any(f.startswith("item 3: rule 4") for f in out)


def test_rule_4_ranked_unknown_id():
    text = clean_text().replace("- 3\n", "- 3\n- 99\n")
    out = failures(text, rules=STRUCTURAL)
    assert any(f.startswith("item 99: rule 4") for f in out)


def test_rule_5_closed_item_ranked():
    text = clean_text().replace("- 3\n", "- 3\n- 2\n")
    out = failures(text, rules=STRUCTURAL)
    assert any(f.startswith("item 2: rule 5") for f in out)


def test_rule_6_asymmetric_pairs():
    text = clean_text().replace("Pairs: 1\n", "Pairs: none\n")
    out = failures(text, rules=STRUCTURAL)
    assert any(f.startswith("item 1: rule 6") and "3" in f for f in out)


def test_rule_6_pair_names_closed_item():
    text = clean_text().replace("Pairs: 3\n", "Pairs: 3, 2\n")
    out = failures(text, rules=STRUCTURAL)
    assert any(f.startswith("item 1: rule 6") and "2" in f for f in out)


def test_rule_6_pair_names_self():
    text = clean_text().replace("Pairs: 3\n", "Pairs: 3, 1\n")
    out = failures(text, rules=STRUCTURAL)
    assert any(f.startswith("item 1: rule 6") and "itself" in f for f in out)


def test_every_failure_is_reported_not_only_the_first():
    text = clean_text().replace("- 3\n", "").replace("Pairs: 1\n", "Pairs: none\n")
    out = failures(text, rules=STRUCTURAL)
    assert any(f.startswith("item 3: rule 4") for f in out)
    assert any(f.startswith("item 1: rule 6") for f in out)


def _refresh(text, item_id, date="2026-09-04"):
    """Rewrite one item's Verified field to the digest of its current
    content, the way a human does after reading the lint's expected value."""
    doc = lint.parse(text)
    item = next(i for i in doc.items if i.id == item_id)
    digest = lint.canonical_digest(item, doc)
    old = item.get("Verified")
    heading_at = text.index(item.heading)
    before, after = text[:heading_at], text[heading_at:]
    after = after.replace("Verified: " + old, "Verified: %s %s" % (date, digest), 1)
    return before + after


def _refresh_all(text):
    doc = lint.parse(text)
    for item in doc.items:
        text = _refresh(text, item.id)
    return text


class TestRule7Digest:
    def test_initial_file_is_clean(self):
        assert failures(clean_text(), rules=(7,)) == []

    def test_edit_without_refresh_fails_and_prints_expected(self):
        text = clean_text().replace("Body of item one.", "Body of item one, edited.")
        out = failures(text, rules=(7,))
        assert len(out) == 1 and out[0].startswith("item 1: rule 7")
        doc = lint.parse(text)
        expected = lint.canonical_digest(doc.items[0], doc)
        assert expected in out[0]
        assert failures(_refresh(text, "1"), rules=(7,)) == []

    def test_moving_item_to_another_group_fails(self):
        text = clean_text().replace("- 1\n- 3\n", "- 3\n").replace(
            "### Last - housekeeping\n", "### Last - housekeeping\n- 1\n")
        out = failures(text, rules=(7,))
        assert [f.split(":")[0] for f in out] == ["item 1"]

    def test_renamed_heading_fails(self):
        text = clean_text().replace("## 1. First open item", "## 1. First item")
        out = failures(text, rules=(7,))
        assert [f.split(":")[0] for f in out] == ["item 1"]

    def test_two_edits_one_refresh_fails(self):
        text = clean_text().replace("Body of item one.", "Body one, edit A.")
        text = _refresh(text, "1")
        assert failures(text, rules=(7,)) == []
        text = text.replace("Body one, edit A.", "Body one, edit B.")
        out = failures(text, rules=(7,))
        assert [f.split(":")[0] for f in out] == ["item 1"]

    def test_changing_the_verified_date_alone_stays_clean(self):
        text = clean_text()
        doc = lint.parse(text)
        digest = lint.canonical_digest(doc.items[0], doc)
        text = text.replace("Verified: 2026-09-04 " + digest,
                            "Verified: 2026-09-03 " + digest, 1)
        assert failures(text, rules=(7,)) == []

    def test_header_field_change_other_than_verified_fails(self):
        text = clean_text().replace("Cost: one line of cost", "Cost: two lines")
        out = failures(text, rules=(7,))
        assert [f.split(":")[0] for f in out] == ["item 1"]

    def test_future_date_fails(self):
        text = clean_text()
        doc = lint.parse(text)
        digest = lint.canonical_digest(doc.items[0], doc)
        text = text.replace("Verified: 2026-09-04 " + digest,
                            "Verified: 2026-09-05 " + digest, 1)
        out = failures(text, rules=(7,))
        assert any(f.startswith("item 1: rule 7") and "future" in f for f in out)

    def test_invalid_date_fails(self):
        text = clean_text()
        doc = lint.parse(text)
        digest = lint.canonical_digest(doc.items[0], doc)
        text = text.replace("Verified: 2026-09-04 " + digest,
                            "Verified: 2026-13-40 " + digest, 1)
        out = failures(text, rules=(7,))
        assert any(f.startswith("item 1: rule 7") for f in out)

    def test_non_breaking_space_digests_differently(self):
        text = clean_text()
        doc = lint.parse(text)
        base = lint.canonical_digest(doc.items[0], doc)
        nbsp = text.replace("Body of item one.", "Body of item one. ")
        doc2 = lint.parse(nbsp)
        assert lint.canonical_digest(doc2.items[0], doc2) != base
        spaced = text.replace("Body of item one.", "Body of item one. \t")
        doc3 = lint.parse(spaced)
        assert lint.canonical_digest(doc3.items[0], doc3) == base

    def test_padded_group_header_contributes_stripped_bytes(self):
        text = clean_text().replace("### First - breaks the review process",
                                    "###   Name  ")
        doc = lint.parse(text)
        raw = lint.canonical_bytes(doc.items[0], doc)
        assert raw.endswith(b"\ngroup:Name\n")

    def test_crlf_and_lf_digest_equal(self):
        text = clean_text()
        crlf = text.replace("\n", "\r\n")
        doc_lf, doc_crlf = lint.parse(text), lint.parse(crlf)
        for a, b in zip(doc_lf.items, doc_crlf.items):
            assert lint.canonical_digest(a, doc_lf) == lint.canonical_digest(b, doc_crlf)

    def test_trailing_blank_lines_are_dropped(self):
        text = clean_text()
        doc = lint.parse(text)
        base = lint.canonical_digest(doc.items[3], doc)
        padded = text.rstrip("\n") + "\n\n\n\n"
        doc2 = lint.parse(padded)
        assert lint.canonical_digest(doc2.items[3], doc2) == base

    def test_digests_flag_prints_one_line_per_item(self, capsys):
        code = lint.main(["--digests", str(FIXTURES / "clean.md")])
        out = capsys.readouterr().out.splitlines()
        assert code == 0
        assert [ln.split(" ")[0] for ln in out] == ["1", "2", "3", "4"]
        assert all(len(ln.split(" ")[1]) == 12 for ln in out)


import os
import subprocess


def pointer_text():
    return (FIXTURES / "pointer.md").read_text(encoding="utf-8")


def failures_full(text, pointer=None, repo_root=REPO, revision=None):
    return lint.check(text, repo_root=repo_root, revision=revision, today=TODAY,
                      pointer_text=pointer if pointer is not None else pointer_text())


class TestRule1Messages:
    def test_missing_status_says_missing_not_out_of_order(self):
        text = clean_text().replace("Status: OPEN\n", "", 1)
        out = failures_full(text)
        assert any("item 1: rule 1 (header block): missing field Status" in f
                   for f in out)
        assert not any("fields out of order" in f and "item 1:" in f for f in out)

    def test_misplaced_status_still_says_out_of_order(self):
        text = clean_text().replace(
            "Status: OPEN\nCost: one line of cost\n",
            "Cost: one line of cost\nStatus: OPEN\n", 1)
        out = failures_full(text)
        assert any("item 1: rule 1 (header block): fields out of order: "
                   "first field must be Status" in f for f in out)


class TestRules8To12:
    @pytest.mark.parametrize("phrase", lint.BANNED_NARRATIVE)
    def test_rule_8_banned_phrase_in_open_body(self, phrase):
        text = clean_text().replace("Body of item one.", "This was %s last week." % phrase)
        text = _refresh(text, "1")
        out = failures_full(text)
        assert any(f.startswith("item 1: rule 8") and phrase in f for f in out)

    def test_rule_8_banned_phrase_in_group_header(self):
        text = clean_text().replace("### Last - housekeeping", "### Last - renumbered")
        out = failures_full(text)
        assert any(f.startswith("ranking: rule 8") for f in out)

    def test_rule_8_ignores_closed_bodies(self):
        text = clean_text().replace("Shipped in one sentence.", "Shipped; renumbered.")
        text = _refresh(text, "2")
        out = failures_full(text)
        assert not any("rule 8" in f for f in out)

    def test_rule_9_partial_without_remainder(self):
        text = clean_text().replace("**What remains.**", "**Remaining.**")
        text = _refresh(text, "3")
        out = failures_full(text)
        assert any(f.startswith("item 3: rule 9") for f in out)

    def test_rule_9_partial_with_short_remainder(self):
        text = clean_text().replace(
            "**What remains.** The mechanical half was never designed and this\n"
            "paragraph carries at least twenty words so that the shape rule nine\n"
            "is satisfied by the fixture itself here.",
            "**What remains.** Five words are not enough.")
        text = _refresh(text, "3")
        out = failures_full(text)
        assert any(f.startswith("item 3: rule 9") and "20" in f for f in out)

    def test_rule_10_missing_record_line(self):
        text = clean_text().replace(
            "Record: docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md\n\n## 3.",
            "\n## 3.")
        text = _refresh(text, "2")
        out = failures_full(text)
        assert any(f.startswith("item 2: rule 10") for f in out)

    def test_rule_10_record_path_absent(self):
        text = clean_text().replace(
            "Record: docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md",
            "Record: docs/no/such/file.md")
        text = _refresh_all(text)
        out = failures_full(text)
        assert any(f.startswith("item 2: rule 10") for f in out)

    def test_rule_10_record_commit_resolves(self):
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO,
                              capture_output=True, text=True, check=True).stdout.strip()
        text = clean_text().replace(
            "Record: docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md",
            "Record: " + head, 1)
        text = _refresh(text, "2")
        out = failures_full(text)
        assert not any("item 2: rule 10" in f for f in out)

    def test_rule_10_record_commit_unknown(self):
        text = clean_text().replace(
            "Record: docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md",
            "Record: deadbeefdeadbeefdeadbeefdeadbeefdeadbeef", 1)
        text = _refresh(text, "2")
        out = failures_full(text)
        assert any(f.startswith("item 2: rule 10") for f in out)

    def test_rule_11_pointer_missing(self):
        out = failures_full(clean_text(), pointer="")
        assert any(f.startswith("pointer: rule 11") for f in out)

    def test_rule_11_pointer_without_rule_phrase(self):
        out = failures_full(clean_text(), pointer="See BACKLOG.md.\n")
        assert any(f.startswith("pointer: rule 11") for f in out)

    def test_rule_12_header_over_eight_words(self):
        text = clean_text().replace(
            "### Last - housekeeping",
            "### Last - housekeeping and open questions that nobody has ranked")
        out = failures_full(text)
        assert any(f.startswith("ranking: rule 12") for f in out)

    def test_rule_3_owns_stray_ranking_lines_alone(self):
        """A stray ranking line is rule 3's, and reported ONCE: rule 12
        keeps only the eight-word header check."""
        text = clean_text().replace("- 3\n", "- 3\nnot an id\n", 1)
        out = failures_full(text)
        stray = [f for f in out if "not an id" in f]
        assert len(stray) == 1 and stray[0].startswith("ranking: rule 3")

    def test_clean_fixture_passes_every_rule(self):
        assert failures_full(clean_text()) == []


class TestCliAndRevision:
    def test_exit_2_on_missing_file(self, tmp_path):
        assert lint.main([str(tmp_path / "nope.md")]) == 2

    def test_exit_2_on_unparseable_file(self, tmp_path):
        bad = tmp_path / "bad.md"
        bad.write_text("# nothing here\n", encoding="utf-8")
        assert lint.main([str(bad)]) == 2

    def test_exit_1_on_rule_failure(self, tmp_path, monkeypatch):
        monkeypatch.setenv("PARALLAX_BACKLOG_TODAY", "2026-09-04")
        path = tmp_path / "b.md"
        path.write_text(clean_text().replace("- 3\n", ""), encoding="utf-8")
        assert lint.main([str(path), "--pointer", str(FIXTURES / "pointer.md")]) == 1

    def test_revision_reads_git_objects(self, tmp_path, monkeypatch):
        monkeypatch.setenv("PARALLAX_BACKLOG_TODAY", "2026-09-04")
        repo = tmp_path / "repo"
        repo.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=repo, check=True)
        subprocess.run(["git", "config", "user.name", "t"], cwd=repo, check=True)
        (repo / "BACKLOG.md").write_text(clean_text(), encoding="utf-8")
        old = repo / lint.OLD_PATH
        old.parent.mkdir(parents=True)
        old.write_text(pointer_text(), encoding="utf-8")
        spec = repo / "docs" / "superpowers" / "specs"
        spec.mkdir(parents=True)
        (spec / "2026-09-04-backlog-rewrite-design.md").write_text("x\n", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=repo, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "seed"], cwd=repo, check=True)
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True,
                             text=True, check=True).stdout.strip()
        (repo / "BACKLOG.md").write_text("garbage\n", encoding="utf-8")
        assert lint.main(["--repo-root", str(repo), "--revision", sha]) == 0
        assert lint.main(["--repo-root", str(repo)]) == 2


def _git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True,
                          encoding="utf-8", check=True).stdout.strip()


def make_seed_repo(tmp_path, backlog_text):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    (repo / "BACKLOG.md").write_text(backlog_text, encoding="utf-8")
    old = repo / lint.OLD_PATH
    old.parent.mkdir(parents=True)
    old.write_text(pointer_text(), encoding="utf-8")
    spec = repo / "docs" / "superpowers" / "specs"
    spec.mkdir(parents=True)
    (spec / "2026-09-04-backlog-rewrite-design.md").write_text("x\n", encoding="utf-8")
    (repo / "tools").mkdir()
    (repo / "tools" / "a.txt").write_text("a\n", encoding="utf-8")
    (repo / "docs" / "note.md").write_text("n\n", encoding="utf-8")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "seed")
    return repo


def commit_all(repo, message="change"):
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", message)
    return _git(repo, "rev-parse", "HEAD")


class TestReattested:
    def test_governed_paths(self):
        assert lint.is_governed("tools/x.ps1")
        assert lint.is_governed(".github/workflows/a.yml")
        assert lint.is_governed("README.md")
        assert lint.is_governed("CLAUDE.md")
        assert not lint.is_governed("docs/x.md")
        assert not lint.is_governed("BACKLOG.md")
        assert not lint.is_governed("README.md.bak")

    def test_changed_verified_line_names_the_item(self):
        old = clean_text()
        new = _refresh(old, "1", date="2026-09-03")
        assert lint.reattested_items(old, new) == ["1"]

    def test_unrelated_byte_is_not_a_reattestation(self):
        old = clean_text()
        new = old.replace("Body of item one.", "Body of item one!")
        assert lint.reattested_items(old, new) == []

    def test_closed_item_verified_change_does_not_count(self):
        old = clean_text()
        new = _refresh(old, "2", date="2026-09-03")
        assert lint.reattested_items(old, new) == []

    def test_close_counts_as_a_reattestation(self):
        """A wave whose only backlog change is a CLOSE still attests. The
        widening is deliberate; the id is named with '(closed)'."""
        old = clean_text()
        new = old.replace("## 1. First open item\nStatus: OPEN",
                          "## 1. First open item\nStatus: DONE", 1)
        assert lint.reattested_items(old, new) == ["1 (closed)"]

    def test_done_in_both_texts_never_counts(self):
        """Item 2 is DONE in both texts; neither a Verified edit nor an
        untouched item may produce a '(closed)' entry."""
        old = clean_text()
        assert lint.reattested_items(old, old) == []
        new = _refresh(old, "2", date="2026-09-03")
        assert lint.reattested_items(old, new) == []
        assert not any("(closed)" in i for i in lint.reattested_items(old, new))

    def test_absent_old_text_counts_every_open_item(self):
        assert lint.reattested_items(None, clean_text()) == ["1", "3"]

    def test_unparseable_new_text_is_empty(self):
        assert lint.reattested_items(clean_text(), "garbage") == []


class TestRangeMode:
    def test_governed_change_without_reattest_fails(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("PARALLAX_BACKLOG_TODAY", "2026-09-04")
        repo = make_seed_repo(tmp_path, clean_text())
        base = _git(repo, "rev-parse", "HEAD")
        (repo / "tools" / "a.txt").write_text("b\n", encoding="utf-8")
        head = commit_all(repo)
        code = lint.main(["--repo-root", str(repo), "--range", "%s..%s" % (base, head)])
        out = capsys.readouterr().out
        assert code == 1 and "tools/a.txt" in out and "no OPEN or PARTIAL item" in out

    def test_governed_change_with_reattest_passes(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("PARALLAX_BACKLOG_TODAY", "2026-09-04")
        repo = make_seed_repo(tmp_path, clean_text())
        base = _git(repo, "rev-parse", "HEAD")
        (repo / "tools" / "a.txt").write_text("b\n", encoding="utf-8")
        (repo / "BACKLOG.md").write_text(_refresh(clean_text(), "1", "2026-09-03"),
                                         encoding="utf-8")
        head = commit_all(repo)
        code = lint.main(["--repo-root", str(repo), "--range", "%s..%s" % (base, head)])
        out = capsys.readouterr().out
        assert code == 0 and "re-attested: 1" in out

    def test_docs_only_change_passes(self, tmp_path, monkeypatch):
        monkeypatch.setenv("PARALLAX_BACKLOG_TODAY", "2026-09-04")
        repo = make_seed_repo(tmp_path, clean_text())
        base = _git(repo, "rev-parse", "HEAD")
        (repo / "docs" / "note.md").write_text("m\n", encoding="utf-8")
        head = commit_all(repo)
        assert lint.main(["--repo-root", str(repo), "--range", "%s..%s" % (base, head)]) == 0

    def test_backlog_change_is_linted_at_head(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("PARALLAX_BACKLOG_TODAY", "2026-09-04")
        repo = make_seed_repo(tmp_path, clean_text())
        base = _git(repo, "rev-parse", "HEAD")
        (repo / "BACKLOG.md").write_text(clean_text().replace("- 3\n", ""), encoding="utf-8")
        head = commit_all(repo)
        code = lint.main(["--repo-root", str(repo), "--range", "%s..%s" % (base, head)])
        out = capsys.readouterr().out
        assert code == 1 and "item 3: rule 4" in out

    def test_head_alone_uses_its_parent(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setenv("PARALLAX_BACKLOG_TODAY", "2026-09-04")
        repo = make_seed_repo(tmp_path, clean_text())
        (repo / "tools" / "a.txt").write_text("b\n", encoding="utf-8")
        head = commit_all(repo)
        assert lint.main(["--repo-root", str(repo), "--range", head]) == 1
        (repo / "BACKLOG.md").write_text(_refresh(clean_text(), "3", "2026-09-03"),
                                         encoding="utf-8")
        (repo / "tools" / "a.txt").write_text("c\n", encoding="utf-8")
        head2 = commit_all(repo)
        assert lint.main(["--repo-root", str(repo), "--range", head2]) == 0

    def test_root_commit_alone_treats_backlog_as_new(self, tmp_path, monkeypatch):
        monkeypatch.setenv("PARALLAX_BACKLOG_TODAY", "2026-09-04")
        repo = make_seed_repo(tmp_path, clean_text())
        head = _git(repo, "rev-parse", "HEAD")
        assert lint.main(["--repo-root", str(repo), "--range", head]) == 0

    def test_bad_range_is_exit_2(self, tmp_path):
        repo = make_seed_repo(tmp_path, clean_text())
        assert lint.main(["--repo-root", str(repo), "--range", "nope..nope"]) == 2


class TestWiring:
    def test_workflow_runs_lint_and_range(self):
        text = (REPO / ".github" / "workflows" / "skill-evals.yml").read_text(encoding="utf-8")
        assert "python evals/tools/backlog_lint.py\n" in text
        assert "backlog_lint.py --range" in text
        assert "fetch-depth: 0" in text
        assert "github.event.pull_request.base.sha" in text
        assert "github.event.before" in text
        for module in ("test_backlog_hooks.py", "test_backlog_prepush.py"):
            assert text.count("evals/multi-model-verify/" + module) == 2, module

    def test_claude_md_names_the_lint(self):
        text = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
        assert "- `python evals/tools/backlog_lint.py`" in text


def test_real_backlog_passes():
    assert lint.main([]) == 0
