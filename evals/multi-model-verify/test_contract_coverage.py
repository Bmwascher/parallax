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


from contract_coverage import collect_pins, format_failure, uncovered


def test_collects_membership_pins_and_joins_implicit_concatenation(tmp_path):
    src = (
        'def test_x():\n'
        '    assert ("a rotation under the call is the one member "\n'
        '            "that IS transient") in body\n'
    )
    p = _write(tmp_path, "test_sample.py", src)
    assert ("a rotation under the call is the one member that IS transient"
            in collect_pins([p]))


def test_a_count_assertion_is_a_pin(tmp_path):
    """The second positive shape. This repo pins several rules with
    body.count(...) == 1 to catch a phrase that occurs twice.

    Both branches are exercised: the COMPARED form and the BARE call.
    They carry separate arity guards, so a test of one proves nothing
    about the other.
    """
    src = (
        'def test_x():\n'
        '    assert body.count("Compared rule.") == 1\n'
        '    assert body.count("Bare rule.")\n'
        '    assert body.count("At least rule.") >= 2\n'
    )
    p = _write(tmp_path, "test_sample.py", src)
    pins = collect_pins([p])
    assert "Compared rule." in pins
    assert "Bare rule." in pins
    assert "At least rule." in pins


def test_a_docstring_is_not_a_pin(tmp_path):
    """Pin provenance. 47 of 172 string constants in test_backup_lane.py
    sit in no assertion, so 'every constant is a pin' would let a
    docstring make a region read as locked while locking nothing."""
    src = (
        '"""That is a route-attribution failure."""\n'
        'def test_x():\n'
        '    """That is a route-attribution failure."""\n'
        '    assert True\n'
    )
    p = _write(tmp_path, "test_sample.py", src)
    assert "That is a route-attribution failure." not in collect_pins([p])


def test_an_assertion_failure_message_is_not_a_pin(tmp_path):
    """192 strings in the live suite are reachable only through a failure
    message. A message checks nothing about any document, so a hermetic
    assertion carrying contract text must not manufacture coverage."""
    src = 'def test_x():\n    assert path.is_file(), "The rule stands."\n'
    p = _write(tmp_path, "test_sample.py", src)
    assert "The rule stands." not in collect_pins([p])


def test_a_negative_membership_assertion_is_not_a_pin(tmp_path):
    """19 strings in the live suite sit in `not in` comparisons. Those
    assert the text is ABSENT, so reading them as coverage would be
    exactly backwards."""
    src = (
        'def test_x():\n'
        '    assert "The rule stands." not in body\n'
        '    assert not ("The other rule." in body)\n'
    )
    p = _write(tmp_path, "test_sample.py", src)
    pins = collect_pins([p])
    assert "The rule stands." not in pins
    assert "The other rule." not in pins


def test_a_membership_test_inverted_by_its_parent_is_not_a_pin(tmp_path):
    """The clause rule exists for this. Matching `in` anywhere in the
    tree lets an enclosing expression flip its meaning."""
    src = 'def test_x():\n    assert ("The rule stands." in body) == False\n'
    p = _write(tmp_path, "test_sample.py", src)
    assert "The rule stands." not in collect_pins([p])


def test_a_membership_test_inside_an_or_is_not_a_pin(tmp_path):
    """Live shape at evals/multi-model-verify/test_flash_implementer.py:58:
    the assertion permits EITHER branch, so neither side is required and
    neither locks anything on its own."""
    src = (
        'def test_x():\n'
        '    assert "stdin" not in body or "The rule stands." in body\n'
    )
    p = _write(tmp_path, "test_sample.py", src)
    assert "The rule stands." not in collect_pins([p])


def test_a_zero_count_assertion_is_not_a_pin(tmp_path):
    """A zero count asserts ABSENCE. Pins and regions are pooled
    repo-wide, so an absence assertion about one document would otherwise
    cover identical text in another."""
    src = 'def test_x():\n    assert body.count("The rule stands.") == 0\n'
    p = _write(tmp_path, "test_sample.py", src)
    assert "The rule stands." not in collect_pins([p])


def test_a_conditional_membership_operand_is_not_a_pin(tmp_path):
    """Only one branch is required, so neither is a pin. Walking every
    constant below the operand would collect both, and the unselected one
    would lock text the assertion never checks."""
    src = (
        'def test_x():\n'
        '    assert ("The rule." if flag else "The other rule.") in body\n'
    )
    p = _write(tmp_path, "test_sample.py", src)
    pins = collect_pins([p])
    assert "The rule." not in pins
    assert "The other rule." not in pins


def test_a_conditional_count_needle_is_not_a_pin(tmp_path):
    src = (
        'def test_x():\n'
        '    assert body.count("The rule." if flag else "Other.") >= 1\n'
    )
    p = _write(tmp_path, "test_sample.py", src)
    pins = collect_pins([p])
    assert "The rule." not in pins
    assert "Other." not in pins


def test_a_count_call_with_more_than_one_argument_is_not_a_pin(tmp_path):
    """Every artifact states the singular form `body.count("literal")`.
    Iterating all arguments would have made the code broader than the
    grammar it documents, which is how the instruction file and the code
    drifted apart twice before.

    The compared branch and the bare branch have SEPARATE arity and
    keyword guards. Both are exercised here, in both failing shapes, so
    the test locks the whole fix rather than half of it.
    """
    src = (
        'def test_x():\n'
        '    assert receiver.count("Compared a.", "Compared b.") == 1\n'
        '    assert receiver.count("Bare a.", "Bare b.")\n'
        '    assert receiver.count("Compared kw.", start=0) == 1\n'
        '    assert receiver.count("Bare kw.", start=0)\n'
    )
    p = _write(tmp_path, "test_sample.py", src)
    pins = collect_pins([p])
    for needle in ("Compared a.", "Compared b.", "Bare a.", "Bare b.",
                   "Compared kw.", "Bare kw."):
        assert needle not in pins


def test_a_conjunction_of_clauses_collects_both(tmp_path):
    src = (
        'def test_x():\n'
        '    assert "First rule." in body and "Second rule." in body\n'
    )
    p = _write(tmp_path, "test_sample.py", src)
    pins = collect_pins([p])
    assert "First rule." in pins
    assert "Second rule." in pins


def test_an_equality_expectation_is_not_a_pin(tmp_path):
    """None of the three clause forms. Accepted limit: the failure
    direction is a red, never false coverage."""
    src = 'def test_x():\n    assert result == "The rule stands."\n'
    p = _write(tmp_path, "test_sample.py", src)
    assert "The rule stands." not in collect_pins([p])


def test_a_string_assigned_but_never_asserted_is_not_a_pin(tmp_path):
    """An accepted limit, tested so it stays deliberate. The failure
    direction is safe: an uncollected pin makes its region read as
    uncovered, which is a red. It can never manufacture coverage."""
    src = (
        'def test_x():\n'
        '    required = "The rule stands."\n'
        '    assert required in body\n'
    )
    p = _write(tmp_path, "test_sample.py", src)
    assert "The rule stands." not in collect_pins([p])


def test_pins_are_whitespace_normalized(tmp_path):
    src = 'def test_x():\n    assert "two   spaces\\nand a newline" in body\n'
    p = _write(tmp_path, "test_sample.py", src)
    assert "two spaces and a newline" in collect_pins([p])


def test_a_covered_region_reports_nothing():
    regions = {"demo": ("The rule stands.", "demo.md")}
    pins = {"the text says The rule stands. right here"}
    assert uncovered(regions, pins) == []


def test_a_region_with_no_pin_at_all_is_reported():
    """Instance 10: the disposition sentence had no pin."""
    body = "That is a route-attribution failure."
    regions = {"demo": (body, "backup-lane.md")}
    pins = {"Detect it."}
    assert uncovered(regions, pins) == [("demo", "backup-lane.md", body)]


def test_a_pin_that_stops_mid_region_does_not_cover_it():
    """Instance 11: the pin stopped at 'IS transient'."""
    body = ("A rotation is the one member that IS transient, so the user "
            "decides whether to spend another.")
    regions = {"demo": (body, "fallbacks.md")}
    pins = {"A rotation is the one member that IS transient"}
    assert uncovered(regions, pins) == [("demo", "fallbacks.md", body)]


def test_two_pins_that_jointly_span_a_region_do_not_cover_it():
    """The revision-1 silent pass, kept as a regression test. Under
    per-sentence coverage a mis-split let two fragment pins satisfy both
    halves while nothing contained the whole rule."""
    body = "Use U.S. Servers only."
    regions = {"demo": (body, "demo.md")}
    pins = {"Use U.S.", "Servers only."}
    assert uncovered(regions, pins) == [("demo", "demo.md", body)]


def test_failure_message_names_region_file_and_body():
    misses = [("demo", "panels.md", "The lane is UNAVAILABLE, not degraded.")]
    msg = format_failure(misses)
    assert "demo" in msg
    assert "panels.md" in msg
    assert "The lane is UNAVAILABLE, not degraded." in msg
    assert "add a pin containing that region whole" in msg
