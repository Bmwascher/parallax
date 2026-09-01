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


def test_a_capitalized_marker_keyword_is_rejected():
    """MARKERISH is case-insensitive so this shape reaches the preflight,
    but START is not, so it is rejected rather than silently ignored."""
    text = "<!-- CONTRACT:START id=demo -->\nThe rule.\n<!-- contract:end -->\n"
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


import ast

from contract_coverage import _clause_pins


@pytest.mark.parametrize("src", [
    "NEEDLE in body",
    'result == "text"',
    '"text" not in body',
    '("a" if flag else "b") in body',
])
def test_clause_pins_returns_empty_for_documented_exclusions(src):
    """Each shape is a documented EXCLUSION with no direct test of
    `_clause_pins` itself before now, only through `collect_pins` on a
    whole file."""
    node = ast.parse(f"assert {src}").body[0]
    assert _clause_pins(node.test) == set()


def test_a_conjunction_of_clauses_collects_both(tmp_path):
    src = (
        'def test_x():\n'
        '    assert "First rule." in body and "Second rule." in body\n'
    )
    p = _write(tmp_path, "test_sample.py", src)
    pins = collect_pins([p])
    assert "First rule." in pins
    assert "Second rule." in pins


def test_a_mixed_conjunction_collects_the_operand_it_recognizes(tmp_path):
    """`A and B` passing means A holds, whatever B is. Dropping the whole
    conjunction because one operand is unrecognized would discard a real
    lock. The grammar in every artifact says so explicitly since the
    0.15.0 diff debate raised the wording."""
    src = (
        'def test_x():\n'
        '    assert "First rule." in body and flag\n'
        '    assert other and "Second rule." in body\n'
    )
    p = _write(tmp_path, "test_sample.py", src)
    pins = collect_pins([p])
    assert "First rule." in pins
    assert "Second rule." in pins


CONSUMED_ASSERTIONS = [
    ('with pytest.raises(AssertionError):\n'
     '        assert "Raises region." in body\n', "Raises region."),
    ('with contextlib.suppress(AssertionError):\n'
     '        assert "Suppress region." in body\n', "Suppress region."),
    ('try:\n'
     '        assert "Try region." in body\n'
     '    except AssertionError:\n'
     '        pass\n', "Try region."),
]


@pytest.mark.parametrize("stmt,needle", CONSUMED_ASSERTIONS)
def test_an_assertion_whose_failure_is_swallowed_is_not_a_pin(
        tmp_path, stmt, needle):
    """An assertion locks its text only because failing it fails the
    suite. Each shape here PASSES when the text is absent, so treating it
    as a lock manufactures coverage - the one direction this checker may
    never produce. Found by the cross-vendor lane in the 0.15.0 diff
    debate, after three earlier reviews missed it."""
    src = f'def test_x():\n    {stmt}'
    p = _write(tmp_path, "test_sample.py", src)
    assert needle not in collect_pins([p])


def test_an_assertion_in_an_xfail_function_is_not_a_pin(tmp_path):
    src = (
        '@pytest.mark.xfail\n'
        'def test_x():\n'
        '    assert "Xfail region." in body\n'
    )
    p = _write(tmp_path, "test_sample.py", src)
    assert "Xfail region." not in collect_pins([p])


def test_an_assertion_in_an_except_handler_is_still_a_pin(tmp_path):
    """The rejection is scoped to the `try` BODY. An assertion in a
    handler runs normally and its failure reaches the runner, so it locks
    its text. Stated as a test because the conservative rule is easy to
    widen by accident until it swallows real pins."""
    src = (
        'def test_x():\n'
        '    try:\n'
        '        something()\n'
        '    except ValueError:\n'
        '        assert "Handler region." in body\n'
    )
    p = _write(tmp_path, "test_sample.py", src)
    assert "Handler region." in collect_pins([p])


def test_an_assertion_in_a_try_without_handlers_is_still_a_pin(tmp_path):
    """`try/finally` runs its cleanup and then lets the AssertionError
    through, so the failure reaches the runner and the assertion locks
    its text. The first version of this rule consumed every `try` body
    and lost such pins, which the round-2 fix re-review caught."""
    src = (
        'def test_x():\n'
        '    try:\n'
        '        assert "Finally region." in body\n'
        '    finally:\n'
        '        cleanup()\n'
    )
    p = _write(tmp_path, "test_sample.py", src)
    assert "Finally region." in collect_pins([p])


def test_a_region_locked_only_by_a_swallowed_assertion_is_uncovered(
        tmp_path):
    """The end-to-end statement of the defect: not merely that the pin is
    dropped, but that the region it would have covered now reads red."""
    src = (
        'def test_x():\n'
        '    with pytest.raises(AssertionError):\n'
        '        assert "The rule stands." in body\n'
    )
    p = _write(tmp_path, "test_sample.py", src)
    regions = {"r": ("The rule stands.", "demo.md")}
    assert uncovered(regions, collect_pins([p])) == [
        ("r", "demo.md", "The rule stands.")]


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
    """Instance 10: no pin contained the whole disposition sentence."""
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


from pathlib import Path

HISTORY = (Path(__file__).resolve().parent / "fixtures"
           / "contract-coverage-history")


def _history_case(stem):
    regions = collect_regions([HISTORY / f"{stem}-doc.md"])
    pins = collect_pins([HISTORY / f"{stem}-pins.py"])
    return regions, uncovered(regions, pins)


def test_catches_instance_10_missing_disposition_pin():
    """4d8a121: no pin held the whole 'That is a route-attribution
    failure' sentence; only a fragment inside it was pinned."""
    regions, misses = _history_case("instance-10")
    assert [rid for rid, _, _ in misses] == ["hist-10-defect"]


def test_catches_instance_11_pin_stopping_mid_sentence():
    """8eacc8a: the pin ended at 'IS transient'."""
    regions, misses = _history_case("instance-11")
    assert [rid for rid, _, _ in misses] == ["hist-11-defect"]


def test_catches_instance_12_bare_phrase_pin():
    """f9fd9b9: the pin was the bare phrase 'Claude Code 2.1.216'."""
    regions, misses = _history_case("instance-12")
    assert [rid for rid, _, _ in misses] == ["hist-12-defect"]


def test_history_fixtures_are_not_vacuous():
    """Each fixture must hold exactly two regions, and its CONTROL must
    be covered. A fixture whose pins failed to load would report both
    regions uncovered and the tests above would still be red - for the
    wrong reason."""
    for stem in ("instance-10", "instance-11", "instance-12"):
        regions, misses = _history_case(stem)
        assert len(regions) == 2, f"{stem} must contain exactly two regions"
        assert len(misses) == 1, (
            f"{stem}: expected exactly the defect region uncovered, got "
            f"{[rid for rid, _, _ in misses]}")


REPO = Path(__file__).resolve().parents[2]

DOC_PATHS = (
    sorted((REPO / "skills").glob("**/*.md"))
    + sorted((REPO / "agents").glob("*.md"))
    + sorted((REPO / "commands").glob("*.md"))
)

# This module is excluded from pin collection on purpose. Its own
# assertions quote whole contract bodies, so including it would let the
# checker satisfy itself.
PIN_PATHS = [p for p in sorted((REPO / "evals" / "multi-model-verify")
                               .glob("test_*.py"))
             if p.name != Path(__file__).name]

DECLARED_REGIONS = {
    # kimi-code swap (backlog item 13). The seven regions that used to sit
    # here - rotation-guard-detection, rotation-guard-disposition,
    # rotation-guard-identity, session-block-attribution,
    # session-block-kind, session-block-residual and lane-lock - all
    # existed to attribute a round inside ONE user-global append log.
    #
    # `lane-lock` below is a REUSED NAME, not a restored region. The
    # deleted one attributed a round inside that append log. The new one
    # is an unrelated rule about the PERSISTENT LANE LOCK FILE beside the
    # credential - liveness-anchored staleness, in-place state
    # transitions, and the two guarded human overrides. Nothing about the
    # deleted rule came back.
    # kimi-code writes a per-session wire transcript and a per-session
    # log, so there is nothing left to attribute and every one of those
    # rules lost its subject. The six below replace them.
    #
    # round-freshness-boundary is the SURVIVING HALF of the deleted
    # offset rule: the files are still cumulative, so a slice still needs
    # a boundary - it is now bounded by a byte offset plus a prefix hash
    # over each file, rather than by position in a shared stream.
    #
    # The session-KIND check survives too, inside
    # per-round-session-evidence: a resume that silently started a new
    # session now shows up as session-scoped records appearing in a slice
    # that must not carry them, instead of as a `Created new session:`
    # line.
    "lane-home-isolation",
    "lane-lock",
    "lane-lock-call-lifecycle",
    "lane-debate-close",
    "round-freshness-boundary",
    "per-round-session-evidence",
    "evidence-hash-continuity",
    "brief-hash-binding",
    "resume-inheritance",
    "panel-round-continuity-check",
    "panel-resume-failure-mode",
    "panel-floor-scope",
    "panel-floor-reference",
    "panel-floor-agent",
    "panel-seat-resume-best-effort",
    "panel-lane-loss-disposition",
    "fable-resume-failure",
    "fable-resume-redispatch-record",
    "panel-unavailable-principle",
    "panel-unavailable-procedure",
    "panel-unavailable-invariant",
    # 0.17.0 backlog item 4: the client half of preflight 3.
    "client-context-probe",
    "plugin-cache-reclassified",
    "verified-override-dispatch",
    # 0.23.0: the brief's encoding across the native stdin boundary. Found
    # by the round-evidence binding refusing a round of this release's own
    # plan debate.
    "brief-encoding-transport",
    "enumeration-depth-asymmetry",
    "brief-scope-guard",
    "client-probe-scope-limit",
    # 0.24.0, backlog item 7: the reviewer's TOOL surface. Two regions
    # rather than one because a region must fit a single pin, and because
    # they say different kinds of thing. The PROBE region holds the
    # measurement's shape - why pass 1 is a calibration and why an absent
    # tool is only a mitigation. The ALLOWLIST region holds a DECISION
    # about what the auditor may hold, which is the part a later cycle
    # would be tempted to widen quietly.
    "tool-surface-probe",
    "tool-surface-allowlist",
    # 0.20.0, from the reopened home-skills-root debate. These replace
    # no earlier region - the text they cover was ordinary pinned prose
    # asserting an UNKNOWN ("unprobed territory") and an unmeasurable
    # mitigation. The probe resolved both. A marked region is what stops
    # a later edit appending "this may be skipped when the driver
    # considers the home trusted" underneath a still-passing pin.
    "home-skill-root-disposition",
    "home-skill-root-disposition-limit",
    # 0.21.0, backlog item 20. The codex lane never verified that the
    # brief it sent is the prompt the client recorded, while the backup
    # lane always did - which is exactly why corruption on this lane
    # could be silent and corruption on that one could not. Two regions
    # rather than one because a region must fit a single pin: the CALLS
    # region holds the fresh and resumed boundaries, the RECORD region
    # holds the prompt shape and the claim's ceiling.
    "codex-brief-binding-calls",
    "codex-brief-binding-record",
    # 0.26.0, backlog item 56. The FRESH record ahead of the brief was
    # bounded by COUNT alone, so arbitrary text bound clean and then
    # became the session's baseline. A third region rather than more
    # text in the RECORD region: a region must fit one pin, and this
    # one says a different kind of thing - the resumed rule is a value
    # comparison against a baseline, this is the admission of that
    # baseline, and it carries the gaps it deliberately leaves open.
    "codex-brief-binding-fresh-record",
    # 0.21.0, backlog item 21. The mirror copies into a NEW root, so a
    # destination legal in the source can be illegal in the mirror, and
    # that failure lands mid-copy leaving a partial tree that reads like
    # a complete one. One region rather than two: the universe, the
    # arithmetic, the limit and the three out-of-universe requirements
    # are one rule, and splitting them is how a reader ends up
    # measuring files but not directories.
    "mirror-path-budget",
    # 0.21.0, backlog item 22. The mirror's two identities, the
    # construction bridge that ties them together, and the dispatch-time
    # gate. One region because the bridge is only meaningful beside the
    # fields it bridges, and the narrowed claim is only honest beside
    # the fingerprint that backs it.
    "mirror-identity-gate",
    # 0.28.0, backlog item 32. TOOL replaced a launch that had been five
    # copied snippets, regenerating the same defect across four debate
    # rounds. STATES leads with NO RECEIPT, then RECEIPT NOT EXPECTED,
    # then LAUNCH UNKNOWN, because the cross-vendor reviewer refused the
    # claim that a tool eliminates the irreducible interrupted launch,
    # then refused a launch token stored inside the artifact it
    # authenticates, then caught this very ordering stated two ways in
    # one document, and finally caught the irreducible case sitting
    # under the wrong state name once the receipt became the last
    # artifact published. NAMING is separate because it is the only
    # unenforced one.
    #
    # 2026-08-31, Task 8 of the completion-coupled dispatch plan renamed
    # the launch/poll design's three regions for the -Prepare/-Classify
    # design that replaced it: detached-dispatch-tool ->
    # round-dispatch-tool, detached-dispatch-operation ->
    # round-dispatch-operation. detached-dispatch-states did not survive
    # as one region: the state list plus the exit map plus the framing
    # sentence did not fit one pin, so it split at the boundary between
    # the state list and the exit map into round-dispatch-states (the
    # framing sentence, the 17-state order, and all five residuals this
    # plan ships stated rather than fixed) and round-dispatch-exit-map
    # (the exit code mapping alone). background-task-naming keeps its
    # name; its only change is the new fact that -Prepare now prints the
    # taskName.
    "round-dispatch-tool",
    "round-dispatch-states",
    "round-dispatch-exit-map",
    "round-dispatch-operation",
    "background-task-naming",
    # 0.28.0, backlog item 33. The prompt put "skip the cross-vendor
    # lane" one tap from the recommended answer, and the answer never
    # differed. This region holds what SURVIVES the prompt's removal -
    # the evidence duty, the empty re-enumeration, the hook suppression,
    # and BLOCKED - rather than the removal itself.
    "back-channel-auto-mirror",
}


def test_declared_regions_match_the_documents(doc_paths=DOC_PATHS):
    """Deleting a whole region takes its markers with it. Without this
    check the coverage test would then pass over nothing at all.

    doc_paths is optional so the negative case (a scratch copy of one
    document with a region's markers deleted) can be run directly,
    without repointing the module-level DOC_PATHS constant."""
    found = set(collect_regions(doc_paths))
    missing = sorted(DECLARED_REGIONS - found)
    extra = sorted(found - DECLARED_REGIONS)
    assert not missing, (
        f"declared region(s) not found in any document: {missing}. "
        "A region was deleted or renamed.")
    assert not extra, (
        f"region(s) found but not declared: {extra}. "
        "Add them to DECLARED_REGIONS.")


def test_every_region_citation_uses_a_resolvable_form(doc_paths=DOC_PATHS):
    """A declared id must be cited as `<file>.md's <id>`, never bare.

    Added 2026-09-01, from the third whole-branch review. The dangling
    check above reads two forms; a citation written in any OTHER form is
    invisible to it, so renaming that region leaves a dead pointer no
    gate can see. Two shipped citations were exactly that - a backticked
    `brief-hash-binding` and a backticked `back-channel-auto-mirror`,
    the second naming no file at all.

    Widening the dangling regex to backticks was measured and REJECTED:
    over these same documents it matches eight tokens, and six are not
    regions at all (skill names like `gpt-5-4-prompting`, drift states
    like `manual-triage-needed`). This rule takes the other direction -
    it only ever looks at ids that ARE declared, so it cannot fire on
    prose - and it makes every live citation resolvable.

    It does NOT by itself keep the dangling check able to see a citation
    later; an earlier version of this docstring claimed that and was
    wrong. What makes that true is the `<file>.md's <id>` pattern in the
    dangling check, widened 2026-09-01 to read any file's possessive
    rather than one file's. The two rules are a pair: this one forces
    every citation into that spelling, and that one reads it.
    """
    import re

    declared_in = {}
    for path in doc_paths:
        for rid in re.findall(r"contract:start id=([a-z][a-z0-9-]*)",
                              path.read_text(encoding="utf-8")):
            declared_in.setdefault(rid, set()).add(path.name)
    declared = set(declared_in)
    assert declared, "no regions declared; this guard stopped guarding"
    bad = []
    for path in doc_paths:
        # Normalized: a citation that wraps across two lines is still a
        # citation, and reporting it as a bad form would be the reflow
        # trap rather than a finding.
        text = " ".join(path.read_text(encoding="utf-8").split())
        for rid in declared:
            for match in re.finditer(re.escape(rid), text):
                start, end = match.start(), match.end()
                # its own marker, and any longer id that contains this one
                if re.search(r"contract:start id=$", text[:start]):
                    continue
                if start and text[start - 1] == "-":
                    continue
                if end < len(text) and text[end] == "-":
                    continue
                # Same file shape as the dangling check: no slash and no
                # bracket, so `references/x.md's` and `(x.md's` both
                # yield the bare file name the declaration is keyed by.
                names = re.search(
                    r"([A-Za-z][A-Za-z0-9._-]*\.md)'s $", text[:start])
                if names and names.group(1) in declared_in.get(rid, ()):
                    continue
                bad.append("%s cites %s" % (path.name, rid))
    assert not bad, (
        "region citation(s) not written as `<file>.md's <id>`: "
        f"{sorted(set(bad))}. A reader cannot resolve the region, and "
        "the dangling check cannot see the citation to report it dead "
        "when the region is renamed.")


def test_every_cited_dispatch_region_id_resolves(doc_paths=DOC_PATHS):
    """Prose that names a region id must name one that exists.

    Backlog item 32, 2026-08-31. Task 8 renamed three regions and split
    one. Two sentences in SKILL.md went on citing
    `detached-dispatch-states`, an id that no longer existed, and the
    test that was supposed to keep the reader pointed at the states
    quoted the SAME stale id - so the pair agreed with each other and
    the suite stayed green over a dead citation. A green gate proving a
    dead citation is the worst kind of green.

    SCOPE, stated rather than implied. This began as a check of
    `model-prompting-notes.md`'s regions only, because the same
    `<file>.md's <token>` phrasing is ordinary prose elsewhere -
    `backup-lane.md's per-round evidence`,
    `debate-protocol.md's final-adjudication step`,
    `fallbacks.md's panel-lane-loss` and
    `frozen-plan-format.md's lane envelope` are all English, not ids.
    It is GENERAL now: the three-or-more-word shape excludes the first,
    second and fourth of those, and the one collision is excluded by
    name below. Two shapes it still cannot see, neither with an instance
    today: a declared TWO-word id (only `lane-lock`) cited under any
    file but `model-prompting-notes.md`, and any citation in a file
    outside DOC_PATHS, which is where the backlog's own pointer sits.
    Backlog item 69 tracks the general problem of citations into shipped
    text that nothing verifies.
    """
    import re

    declared_in = {}
    for path in doc_paths:
        for rid in re.findall(r"contract:start id=([a-z][a-z0-9-]*)",
                              path.read_text(encoding="utf-8")):
            declared_in.setdefault(rid, set()).add(path.name)
    declared = set(declared_in)
    cited = {}
    wrong_file = []
    # `fallbacks.md's panel-lane-loss class` is English - the prefix of a
    # real region id (`panel-lane-loss-disposition`) used as a noun. It is
    # the ONLY such phrase over these documents, measured 2026-09-01, so
    # it is excluded by name rather than by widening the shape.
    non_ids = {("fallbacks.md", "panel-lane-loss")}
    patterns = (
        re.compile(r"model-prompting-notes\.md's ([a-z][a-z0-9-]*)"),
        # A BARE parenthesised id, as in `(round-dispatch-operation)`.
        # Three or more hyphen-separated lowercase words: measured
        # 2026-09-01 over every document this checker scans, that shape
        # matches region ids and nothing else in the prose. Without this
        # second form a citation written that way is INVISIBLE to the
        # guard, so renaming its region leaves a dead pointer nothing can
        # see - which is what this cycle's own two new call sites were,
        # added by the very fix that was meant to make them resolvable.
        re.compile(r"\(([a-z][a-z0-9]*(?:-[a-z0-9]+){2,})\)"),
    )
    # ANY file's possessive, not just this one file's. Added 2026-09-01:
    # the previous fix rewrote two citations into `backup-lane.md's <id>`
    # and `SKILL.md's <id>` - forms the two patterns above cannot see - so
    # both moved from one invisible spelling to another and the dead-
    # pointer gap stayed open for the exact cases that motivated closing
    # it. The file part is captured and checked too, because a citation
    # naming the WRONG file resolves for nobody.
    qualified = re.compile(
        r"(?P<file>[A-Za-z][A-Za-z0-9._-]*\.md)'s "
        r"(?P<id>[a-z][a-z0-9]*(?:-[a-z0-9]+){2,})")
    for path in doc_paths:
        text = " ".join(path.read_text(encoding="utf-8").split())
        for pattern in patterns:
            for match in pattern.finditer(text):
                cited.setdefault(match.group(1), set()).add(path.name)
        for match in qualified.finditer(text):
            fname, rid = match.group("file"), match.group("id")
            if (fname, rid) in non_ids:
                continue
            cited.setdefault(rid, set()).add(path.name)
            if rid in declared_in and fname not in declared_in[rid]:
                wrong_file.append(
                    "%s cites %s's %s, declared in %s"
                    % (path.name, fname, rid, sorted(declared_in[rid])))
    assert cited, (
        "no citation found at all; this guard silently stopped guarding")
    dangling = sorted(
        (rid, sorted(where)) for rid, where in cited.items()
        if rid not in declared)
    assert not dangling, (
        "prose cites region id(s) that no document declares: "
        f"{dangling}. A region was renamed, split or deleted and the "
        "sentence pointing at it was left behind.")
    assert not wrong_file, (
        "region citation(s) name the wrong file: "
        f"{sorted(set(wrong_file))}. The id resolves, the pointer does "
        "not, and a reader sent to that file finds nothing.")


def test_every_marked_region_is_locked_by_a_pin(doc_paths=DOC_PATHS):
    regions = collect_regions(doc_paths)
    misses = uncovered(regions, collect_pins(PIN_PATHS))
    assert not misses, format_failure(misses)
