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
