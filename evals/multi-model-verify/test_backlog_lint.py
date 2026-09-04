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
