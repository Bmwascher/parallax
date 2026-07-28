"""Contract coverage: every marked region must sit whole inside some
test pin.

Design: docs/superpowers/specs/2026-07-27-contract-coverage-design.md

Written RED-first. The checker exists because twelve pin-integrity
instances landed across three cycles, two of them inside the fix for the
one before.
"""
import pytest

from contract_coverage import MarkerError, collect_regions, parse_regions


def _write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return p


def test_parses_a_region_and_normalizes_whitespace():
    text = (
        "intro line\n"
        "<!-- contract:start id=demo -->\n"
        "One rule   here.\nContinued  on two lines.\n"
        "<!-- contract:end -->\n"
        "trailing line\n"
    )
    regions = parse_regions(text, "demo.md")
    assert regions == {"demo": "One rule here. Continued on two lines."}


def test_text_outside_markers_is_not_part_of_the_region():
    text = (
        "Rationale that must never demand a pin.\n"
        "<!-- contract:start id=demo -->\n"
        "The rule.\n"
        "<!-- contract:end -->\n"
        "More rationale.\n"
    )
    assert parse_regions(text, "demo.md")["demo"] == "The rule."


def test_indented_markers_inside_a_list_item_are_recognized():
    """Markers sit at the list item's content indent so they stay inside
    the item. Indentation must not hide them."""
    text = (
        "- **Rule.** Preamble.\n"
        "  <!-- contract:start id=demo -->\n"
        "  The rule.\n"
        "  <!-- contract:end -->\n"
    )
    assert parse_regions(text, "demo.md")["demo"] == "The rule."


def test_start_without_end_is_an_error():
    text = "<!-- contract:start id=demo -->\nbody\n"
    with pytest.raises(MarkerError, match="never closed"):
        parse_regions(text, "demo.md")


def test_end_without_start_is_an_error():
    with pytest.raises(MarkerError, match="end with no start"):
        parse_regions("<!-- contract:end -->\n", "demo.md")


def test_nested_regions_are_an_error():
    text = (
        "<!-- contract:start id=outer -->\n"
        "<!-- contract:start id=inner -->\n"
        "body\n"
        "<!-- contract:end -->\n"
    )
    with pytest.raises(MarkerError, match="opens inside"):
        parse_regions(text, "demo.md")


def test_empty_region_is_an_error():
    text = "<!-- contract:start id=demo -->\n\n<!-- contract:end -->\n"
    with pytest.raises(MarkerError, match="is empty"):
        parse_regions(text, "demo.md")


def test_duplicate_id_within_one_document_is_an_error():
    text = (
        "<!-- contract:start id=demo -->\na\n<!-- contract:end -->\n"
        "<!-- contract:start id=demo -->\nb\n<!-- contract:end -->\n"
    )
    with pytest.raises(MarkerError, match="duplicate id"):
        parse_regions(text, "demo.md")


def test_an_end_marker_carrying_an_id_is_rejected_not_ignored():
    """The vanishing-region hole. A near-miss comment that matches
    neither pattern used to be skipped, so BOTH markers were ignored and
    the region ceased to exist with no error."""
    text = (
        "<!-- contract:start id=demo -->\n"
        "The rule.\n"
        "<!-- contract:end id=demo -->\n"
    )
    with pytest.raises(MarkerError, match="malformed contract marker"):
        parse_regions(text, "demo.md")


def test_an_id_with_illegal_characters_is_rejected_not_ignored():
    text = "<!-- contract:start id=Bad_ID -->\nThe rule.\n<!-- contract:end -->\n"
    with pytest.raises(MarkerError, match="malformed contract marker"):
        parse_regions(text, "demo.md")


def test_a_misspelled_marker_keyword_is_rejected():
    text = "<!-- contract:begin id=demo -->\nThe rule.\n<!-- contract:end -->\n"
    with pytest.raises(MarkerError, match="malformed contract marker"):
        parse_regions(text, "demo.md")


def test_an_unterminated_marker_is_rejected_not_ignored():
    """No closing '-->'. Detection must not wait for one, or a typo makes
    the marker invisible and the region ceases to exist silently."""
    text = "<!-- contract:start id=demo\nThe rule.\n<!-- contract:end -->\n"
    with pytest.raises(MarkerError, match="malformed contract marker"):
        parse_regions(text, "demo.md")


def test_a_marker_split_across_lines_is_rejected_not_ignored():
    """A legal HTML comment may span lines, and then it matches no single
    line at all. A line-by-line scan alone lets the region vanish without
    a word, which is the same silent-deletion hole in a third shape."""
    text = (
        "<!--\ncontract:start id=demo -->\n"
        "The rule.\n"
        "<!-- contract:end -->\n"
    )
    with pytest.raises(MarkerError, match="malformed contract marker"):
        parse_regions(text, "demo.md")


def test_a_marker_split_by_a_bare_carriage_return_is_rejected():
    """`str.splitlines` breaks on more than `\\n`. A newline-only test
    would pass this span, and the line scan would then see two halves,
    neither a complete marker - a silent deletion in a fourth shape."""
    text = "<!--\rcontract:start id=demo -->\nThe rule.\n<!-- contract:end -->\n"
    with pytest.raises(MarkerError, match="malformed contract marker"):
        parse_regions(text, "demo.md")


def test_a_stray_comment_opener_cannot_hide_a_later_marker():
    """`re.finditer` yields NON-OVERLAPPING matches. Scanning comment
    spans let a stray `<!-->` consume forward through a real marker's
    `-->`, so neither pass ever examined the marker. Openers are found
    directly for exactly this reason."""
    text = (
        "<!-->\n"
        "<!--\ncontract:start id=demo -->\n"
        "The rule.\n<!-- contract:end -->\n"
    )
    with pytest.raises(MarkerError, match="malformed contract marker"):
        parse_regions(text, "demo.md")


def test_a_spaced_colon_is_rejected_rather_than_ignored():
    """The opener tolerates `contract :` so this spelling is REJECTED.
    Leaving it undetected would make it invisible, which is the outcome
    this checker may never produce."""
    text = "<!-- contract : start id=demo -->\nx\n<!-- contract:end -->\n"
    with pytest.raises(MarkerError, match="malformed contract marker"):
        parse_regions(text, "demo.md")


def test_a_marker_sharing_a_line_with_prose_is_rejected():
    text = (
        "prose before <!-- contract:start id=demo --> prose after\n"
        "The rule.\n<!-- contract:end -->\n"
    )
    with pytest.raises(MarkerError, match="alone on its line"):
        parse_regions(text, "demo.md")


def test_a_different_marker_family_is_ignored_not_rejected():
    """agents/implementer.md and agents/flash-implementer.md already carry
    shared-contract markers, the 0.12.0 parity mechanism. Both files are
    inside the tree this checker scans, so the keyword is anchored to the
    start of the comment: shared-contract: is not our marker at all."""
    text = (
        "<!-- shared-contract:start -->\n"
        "Shared block owned by another mechanism.\n"
        "<!-- shared-contract:end -->\n"
        "<!-- contract:start id=demo -->\nThe rule.\n<!-- contract:end -->\n"
    )
    assert parse_regions(text, "flash-implementer.md") == {"demo": "The rule."}


def test_duplicate_id_across_documents_is_an_error(tmp_path):
    body = "<!-- contract:start id=demo -->\na\n<!-- contract:end -->\n"
    a = _write(tmp_path, "a.md", body)
    b = _write(tmp_path, "b.md", body)
    with pytest.raises(MarkerError, match="duplicate region id"):
        collect_regions([a, b])


def test_collect_regions_records_the_source_file(tmp_path):
    p = _write(
        tmp_path, "panels.md",
        "<!-- contract:start id=demo -->\nThe rule.\n<!-- contract:end -->\n")
    assert collect_regions([p]) == {"demo": ("The rule.", "panels.md")}
