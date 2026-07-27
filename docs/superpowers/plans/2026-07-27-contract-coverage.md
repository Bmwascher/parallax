# Contract Coverage Checker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make it impossible for a marked contract region to go unpinned, or for a marked region to be deleted, without a test turning red.

**Architecture:** A pure-function module parses `<!-- contract:start id=... -->` regions out of the reference and agent documents, extracts every string literal that a positive-presence assertion clause checks for in the test modules through Python's `ast`, and requires each region to sit whole inside one of those strings. A separate declared inventory of region ids closes the delete-the-whole-region hole. The checker is consumed by one pytest module.

**Tech Stack:** Python 3.12 standard library only (`ast`, `re`, `pathlib`), pytest 9.x, `tmp_path` fixtures. No new dependencies.

**This is revision 4 of the plan, after four rounds of cross-vendor review that found fourteen defects.** Revision 1 split regions into sentences with a regex and treated every string constant as a pin; both were refuted by running the code. Revision 2 fixed those but still let an enclosing expression invert a pin, and still let a multi-line marker comment vanish. See the design's "Revision history" before proposing a return to any earlier behaviour. Do not reintroduce sentence splitting, and do not relax the clause rule into a generic tree walk.

## Global Constraints

- Design spec: `docs/superpowers/specs/2026-07-27-contract-coverage-design.md`. Copied verbatim below where a task depends on it.
- **Whole-region containment.** A region is covered only when ONE pin string contains the whole region body. Overlap does not count, and two pins that jointly span a region do not count.
- **One region, one pin.** There is no sentence splitting anywhere in this plan. A region too long for one pin is two regions.
- **A pin is a string literal in one of exactly three positive-presence CLAUSE forms:** `"literal" in body`; `body.count("literal")` alone or compared `== n` / `>= n` (n ≥ 1) / `> n` (n ≥ 0); or an `and` of those. Nothing else counts.
- **The rule matches a complete clause and NEVER descends into an unrecognized expression.** Matching `in` anywhere in the tree lets an enclosing expression flip its meaning: `assert ("lit" in body) == False` and `assert flag or "lit" in body` both contain a membership test the assertion does not require. The second shape is live at `evals/multi-model-verify/test_flash_implementer.py:58`.
- **The needle must be a plain string literal, not an expression containing one.** Adjacent literals across several lines fold into one constant at parse time, so nearly every existing pin qualifies. A conditional operand does not: `assert ("x" if flag else "y") in body` requires only the selected branch, so collecting both would pin text the assertion never checks.
- **Any positive assertion outside the three forms is rejected, whatever it means.** Excluded, every one an accepted limit whose failure direction is safe — the region reads UNCOVERED, which is a red, never false coverage: a docstring, an assertion's failure message, anything under `not`, anything in a `not in` comparison, anything under `or`, a zero or negative count comparison, a reversed count comparison such as `1 == body.count("x")`, a chained comparison, an `all(...)` comprehension, a walrus, either branch of a conditional, a plain equality such as `result == "text"`, a regex lock such as `re.search(...)`, and a string reached through a variable name.
- Region ids are lowercase letters, digits and hyphens, and unique across the whole repo, not per file.
- All marker and coverage problems are hard test failures. Never warnings, never skips.
- **A marker owns its line.** Any line whose comment keyword is `contract:` must strip to exactly the start or end syntax, or it is a hard failure. Detection does not require a closing `-->`, because an unterminated marker would otherwise be invisible, which is the same silent-deletion hole in a different shape.
- **Marker detection runs over the WHOLE text before the line scan.** An HTML comment may legally span lines, and `<!--` on one line with `contract:start id=demo -->` on the next matches no single line at all. A line scan alone would let that region vanish with no error.
- **`agents/*.md` already carries a different marker family and must keep working.** `agents/implementer.md` and `agents/flash-implementer.md` contain `<!-- shared-contract:start -->` / `<!-- shared-contract:end -->`, the 0.12.0 parity mechanism pinned by `test_shared_contract_parity`. Both files are inside the tree this checker scans. The keyword must therefore be anchored to the start of the comment, so `shared-contract:` is ignored rather than rejected. Do not rename the existing markers.
- Region text and pin text are both whitespace-normalized before comparison, matching the existing `_norm` convention (`" ".join(text.split())`).
- Do not modify the 633 existing assert statements in `evals/**/test_*.py` except to extend ones the checker proves are short.
- Do not reword any text inside a marked region in this plan. Rewording contract text is a separate reviewed change. Item 5 of the backlog will do that for the rotation guard.
- Every task ends green on all four offline gates:
  `python evals/tools/skill_lint.py skills/multi-model-verify --strict`,
  `python evals/tools/skill_scanner.py skills`,
  `python evals/tools/run_trigger_evals.py`,
  `python -m pytest evals -q`
- Baseline before Task 1: `170 passed, 1 skipped`.
- Verified before planning, do not re-litigate: HTML comment markers pass `skill_lint --strict` and `skill_scanner` with zero findings, and a sibling module next to the test files is importable under pytest with no `conftest.py`.

---

## File Structure

| file | responsibility |
|---|---|
| `evals/multi-model-verify/contract_coverage.py` | Create. Pure functions: marker parsing, pin extraction, coverage, failure formatting. No pytest imports, no repo paths baked in. |
| `evals/multi-model-verify/test_contract_coverage.py` | Create. The declared region inventory, the live repo check, and the fixture tests that prove the checker. |
| `evals/multi-model-verify/fixtures/contract-coverage-history/` | Create. Three historical snippets, each with a control region and a defect region, proving the checker catches instances 10, 11 and 12. |
| `skills/multi-model-verify/references/backup-lane.md` | Modify. Markers around three rotation guard regions. |
| `skills/multi-model-verify/references/panels.md` | Modify. Markers around the harness floor rule. |
| `agents/fable-panel-reviewer.md` | Modify. Markers around the harness floor as stated there. |
| `skills/multi-model-verify/references/fallbacks.md` | Modify. Markers around four panel lane regions. |
| `evals/multi-model-verify/test_backup_lane.py` | Modify. Extend two short pins the checker flags. |
| `evals/multi-model-verify/test_seat_reshuffle.py` | Modify. Extend five short pins the checker flags. |
| `README.md`, `CLAUDE.md` | Modify. One line each describing the mechanism. |
| `.claude-plugin/plugin.json` | Modify. Version bump. |

---

### Task 1: Marker parsing and the region inventory

**Files:**
- Create: `evals/multi-model-verify/contract_coverage.py`
- Create: `evals/multi-model-verify/test_contract_coverage.py`

**Interfaces:**
- Consumes: nothing.
- Produces: `MarkerError(Exception)`; `parse_regions(text: str, source: str) -> dict[str, str]` mapping region id to whitespace-normalized body for ONE document; `collect_regions(paths: list[Path]) -> dict[str, tuple[str, str]]` mapping region id to `(body, source_name)` across many documents, raising on a duplicate id.

- [ ] **Step 1: Write the failing tests**

Create `evals/multi-model-verify/test_contract_coverage.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q`
Expected: collection error, `ModuleNotFoundError: No module named 'contract_coverage'`.

- [ ] **Step 3: Write the module**

Create `evals/multi-model-verify/contract_coverage.py`:

```python
"""Contract coverage checker.

Every marked region must sit WHOLE inside some pin string. There is no
sentence splitting: the region is the unit of coverage, and the author
sizes it to be pinnable by one string. Revision 1 split sentences with a
regex; a review produced a counterexample where two fragment pins covered
both halves of a mis-split sentence while nothing covered the sentence,
so coverage passed on an unlocked rule. Dropping the split removes that
bug class rather than patching it.

Pure functions only: no pytest, no repo paths baked in, so the fixture
tests can drive it over temporary directories.

Design: docs/superpowers/specs/2026-07-27-contract-coverage-design.md
"""
import ast
import re

START = re.compile(r"<!--\s*contract:start\s+id=([a-z0-9][a-z0-9-]*)\s*-->")
END = re.compile(r"<!--\s*contract:end\s*-->")

# A line that OPENS a comment whose keyword is contract:. Deliberately
# does NOT require the closing --> : an unterminated marker must be
# rejected, not skipped, or a typo deletes a region silently. That is the
# one outcome this checker may never produce.
#
# The keyword is anchored to the start of the comment on purpose.
# agents/implementer.md and agents/flash-implementer.md already carry
# <!-- shared-contract:start --> markers - the 0.12.0 parity mechanism,
# pinned by test_shared_contract_parity - and both files are inside the
# tree this checker scans. An unanchored search would call every one of
# them malformed and the checker could never run. Case-insensitive so a
# capitalized keyword is REJECTED rather than silently ignored.
# An OPENER of our marker family. `\s*contract\s*:` tolerates a spaced
# colon so that spelling is REJECTED rather than silently ignored, and
# case-insensitive so a capitalized keyword is rejected too. Anchored
# immediately after `<!--`, so `<!-- shared-contract:start -->` - the
# 0.12.0 parity family in agents/ - does not match and is left alone.
MARKERISH = re.compile(r"<!--\s*contract\s*:", re.IGNORECASE)

# The whole-text pass finds openers DIRECTLY rather than iterating
# comment spans. Iterating spans was a silent path: `re.finditer` yields
# NON-OVERLAPPING matches, so a stray `<!-->` earlier in the file
# consumes forward through a later marker's `-->`, the combined body does
# not start with the keyword, and the real marker is never examined by
# either pass. Searching for openers cannot be swallowed that way.
OPENER = MARKERISH


class MarkerError(Exception):
    """Malformed or mis-declared markers. Always a hard failure."""


def _norm(text):
    return " ".join(text.split())


def _classify(line, source, lineno):
    """Return ('start', id) | ('end', None) | (None, None) for one line.

    A marker owns its line: the whole stripped line must be the marker.
    That rejects an unterminated marker, a marker sharing a line with
    prose, and two markers on one line, all in one rule.
    """
    if not MARKERISH.search(line):
        return None, None
    text = line.strip()
    start = START.fullmatch(text)
    if start:
        return "start", start.group(1)
    if END.fullmatch(text):
        return "end", None
    raise MarkerError(
        f"{source}:{lineno}: malformed contract marker {text!r}. "
        "A marker must be alone on its line and exactly "
        "'<!-- contract:start id=<lowercase-id> -->' or "
        "'<!-- contract:end -->'.")


def _preflight(text, source):
    """Reject any marker opener that is not a clean one-line marker.

    Runs over the whole text, so it catches the shapes a line scan cannot
    see: a comment split across lines, and an unterminated one.

    Two details are load-bearing.

    The span runs from the opener to the FIRST `-->` at or after it, or
    to end of text when there is none, so an unterminated opener is
    examined rather than skipped.

    Single-line-ness is tested with `len(span.splitlines()) != 1`, NOT
    with `"\\n" in span`. `str.splitlines` also breaks on `\\r`, `\\v`,
    `\\f`, `\\x1c`-`\\x1e`, `\\x85`, `\\u2028` and `\\u2029`, so a marker
    split by a bare CR would pass a newline-only test here and then be
    split into two invisible halves by the line scan below - a silent
    deletion in a fourth shape.
    """
    for match in OPENER.finditer(text):
        close = text.find("-->", match.start())
        span = (text[match.start():close + 3] if close != -1
                else text[match.start():])
        if (len(span.splitlines()) != 1
                or not (START.fullmatch(span) or END.fullmatch(span))):
            raise MarkerError(
                f"{source}: malformed contract marker {span[:60]!r}. "
                "A marker must be a single line, exactly "
                "'<!-- contract:start id=<lowercase-id> -->' or "
                "'<!-- contract:end -->'.")


def parse_regions(text, source):
    """Return {region_id: normalized_body} for ONE document."""
    _preflight(text, source)
    regions = {}
    open_id = None
    buf = []
    for lineno, line in enumerate(text.splitlines(), 1):
        kind, rid = _classify(line, source, lineno)
        if kind == "start":
            if open_id is not None:
                raise MarkerError(
                    f"{source}:{lineno}: region '{rid}' opens inside "
                    f"still-open region '{open_id}'")
            open_id = rid
            buf = []
            continue
        if kind == "end":
            if open_id is None:
                raise MarkerError(f"{source}:{lineno}: end with no start")
            body = _norm(" ".join(buf))
            if not body:
                raise MarkerError(
                    f"{source}:{lineno}: region '{open_id}' is empty")
            if open_id in regions:
                raise MarkerError(
                    f"{source}:{lineno}: duplicate id '{open_id}'")
            regions[open_id] = body
            open_id = None
            continue
        if open_id is not None:
            buf.append(line)
    if open_id is not None:
        raise MarkerError(f"{source}: region '{open_id}' never closed")
    return regions


def collect_regions(paths):
    """Return {region_id: (body, source_name)} across many documents.

    Ids are unique repo-wide, not per file: one subject stated in two
    documents needs two ids, or a failure message cannot say which file
    to open.
    """
    out = {}
    for path in paths:
        found = parse_regions(path.read_text(encoding="utf-8"), path.name)
        for rid, body in found.items():
            if rid in out:
                raise MarkerError(
                    f"duplicate region id '{rid}' in {out[rid][1]} "
                    f"and {path.name}")
            out[rid] = (body, path.name)
    return out
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q`
Expected: 20 passed.

- [ ] **Step 5: Run the full suite to confirm nothing regressed**

Run: `python -m pytest evals -q`
Expected: 190 passed, 1 skipped.

- [ ] **Step 6: Commit**

```bash
git add evals/multi-model-verify/contract_coverage.py evals/multi-model-verify/test_contract_coverage.py
git commit -m "0.15.0: parse contract regions and reject malformed markers"
```

---

### Task 2: Pin extraction and whole-region coverage

**Files:**
- Modify: `evals/multi-model-verify/contract_coverage.py`
- Modify: `evals/multi-model-verify/test_contract_coverage.py`

**Interfaces:**
- Consumes: `parse_regions`, `collect_regions`, `MarkerError` from Task 1.
- Produces: `collect_pins(paths: list[Path]) -> set[str]` returning whitespace-normalized string literals found in positive-presence assertions; `uncovered(regions: dict[str, tuple[str, str]], pins: set[str]) -> list[tuple[str, str, str]]` returning `(region_id, source_name, body)` for every region with no containing pin; `format_failure(misses: list) -> str`.

- [ ] **Step 1: Write the failing tests**

Append to `evals/multi-model-verify/test_contract_coverage.py`:

```python
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
    body.count(...) == 1 to catch a phrase that occurs twice."""
    src = 'def test_x():\n    assert body.count("The rule stands.") == 1\n'
    p = _write(tmp_path, "test_sample.py", src)
    assert "The rule stands." in collect_pins([p])


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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q`
Expected: `ImportError: cannot import name 'collect_pins'`.

- [ ] **Step 3: Extend the module**

Append to `evals/multi-model-verify/contract_coverage.py`:

```python
def _literal(node):
    """The node's own string value, or nothing.

    Deliberately NOT a walk. Walking every constant below an operand
    collects both branches of a conditional: `assert ("x" if flag else
    "y") in body` requires only the selected value, yet a walk returns
    both, so the unselected one becomes a pin the assertion never checks.
    Adjacent string literals are already folded into ONE constant by the
    parser, which is how nearly every pin in this repo is written, so
    requiring a plain constant costs nothing real.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return {_norm(node.value)}
    return set()


def _is_count_call(node):
    """Any `<something>.count(...)` call.

    Accepted limit: ast sees a method NAME, never a type, so a
    `list.count(...)` would register too. Every live receiver is a
    document string, and checking the type is not possible from the
    syntax tree, so the limit is stated rather than closed.
    """
    return (isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "count")


def _clause_pins(node):
    """Pins from a COMPLETE positive-presence clause, or nothing.

    This function NEVER descends into an expression it does not
    recognize, and that restraint is the whole point. Matching a shape
    anywhere in the tree lets an enclosing expression flip its meaning:
    `assert ("lit" in body) == False` and `assert flag or "lit" in body`
    both CONTAIN a positive membership test that the assertion as a whole
    does not require. The second is live, at
    evals/multi-model-verify/test_flash_implementer.py:58, where the
    assertion permits either the absence of "stdin" or the presence of
    "does not reach" - so treating the latter as an unconditional pin
    would manufacture coverage.

    Three clause forms and no others:
      "literal" in body
      body.count("literal"), alone or compared == n / >= n (n >= 1)
                             or > n (n >= 0)
      <clause> and <clause>

    Measured on the live suite: an unrestricted walk of `ast.Assert`
    yields 715 strings, of which 192 are only reachable through a failure
    message and lock nothing, and 19 sit in `not in` comparisons that
    assert ABSENCE. The clause rule yields 366, and every region in scope
    keeps the coverage it had.

    Never called on `Assert.msg`.
    """
    if isinstance(node, ast.BoolOp) and isinstance(node.op, ast.And):
        pins = set()
        for value in node.values:
            pins |= _clause_pins(value)
        return pins
    if isinstance(node, ast.Compare) and len(node.ops) == 1:
        op, right = node.ops[0], node.comparators[0]
        if isinstance(op, ast.In):
            return _literal(node.left)
        if (_is_count_call(node.left)
                and isinstance(right, ast.Constant)
                and isinstance(right.value, int)
                and not isinstance(right.value, bool)):
            n = right.value
            positive = ((isinstance(op, (ast.Eq, ast.GtE)) and n >= 1)
                        or (isinstance(op, ast.Gt) and n >= 0))
            if positive:
                pins = set()
                for arg in node.left.args:
                    pins |= _literal(arg)
                return pins
        return set()
    if _is_count_call(node):
        pins = set()
        for arg in node.args:
            pins |= _literal(arg)
        return pins
    return set()


def collect_pins(paths):
    """Normalized string literals that some assertion checks for.

    Read through ast, not regex: nearly every pin in this repo is written
    as adjacent string literals across several lines, and the parser
    joins those into one constant for us.

    Accepted limits, all with the same safe failure direction - the
    region reads UNCOVERED, which is a red, never false coverage: a
    string bound to a name and asserted through that name, a regex lock
    such as `re.search(r"...", text)`, and a literal compared with `==`.
    """
    pins = set()
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assert):
                pins |= _clause_pins(node.test)
    return pins


def uncovered(regions, pins):
    """[(region_id, source, body)] for every region no pin contains.

    Containment runs one way only: the PIN must contain the REGION. A pin
    that the region contains is a fragment, which is exactly the defect
    this checker exists to catch.
    """
    misses = []
    for rid in sorted(regions):
        body, source = regions[rid]
        if not any(body in pin for pin in pins):
            misses.append((rid, source, body))
    return misses


def format_failure(misses):
    lines = [
        f"{len(misses)} contract region(s) are not locked by any pin.",
        "For each one, add a pin containing that region whole.",
        "A pin the region contains is a fragment and does not count.",
        "",
    ]
    for rid, source, body in misses:
        lines.append(f"  region '{rid}' in {source}:")
        lines.append(f"    {body}")
    return "\n".join(lines)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q`
Expected: 39 passed.

- [ ] **Step 5: Run the full suite**

Run: `python -m pytest evals -q`
Expected: 209 passed, 1 skipped.

- [ ] **Step 6: Commit**

```bash
git add evals/multi-model-verify/contract_coverage.py evals/multi-model-verify/test_contract_coverage.py
git commit -m "0.15.0: collect pins from asserts and check whole-region coverage"
```

---

### Task 3: Prove the checker catches the three real failures

The checker must catch the failures that motivated it. This task builds
hermetic fixtures from the real historical text so CI needs no git
history.

**Each fixture holds TWO regions.** One is a CONTROL that the historical
pins do cover; one is the DEFECT that they do not. The control is what
makes the red meaningful: without it, a fixture that failed to load its
pins at all would produce the same red for the wrong reason.

**Files:**
- Create: `evals/multi-model-verify/fixtures/contract-coverage-history/instance-10-doc.md`
- Create: `evals/multi-model-verify/fixtures/contract-coverage-history/instance-10-pins.py`
- Create: `evals/multi-model-verify/fixtures/contract-coverage-history/instance-11-doc.md`
- Create: `evals/multi-model-verify/fixtures/contract-coverage-history/instance-11-pins.py`
- Create: `evals/multi-model-verify/fixtures/contract-coverage-history/instance-12-doc.md`
- Create: `evals/multi-model-verify/fixtures/contract-coverage-history/instance-12-pins.py`
- Modify: `evals/multi-model-verify/test_contract_coverage.py`

**Interfaces:**
- Consumes: `collect_regions`, `collect_pins`, `uncovered` from Tasks 1 and 2.
- Produces: nothing new. This task adds tests only.

Simulated against real git history before planning. For all three, the
control region is covered and the defect region is not.

- [ ] **Step 1: Copy the historical pin files verbatim**

```bash
mkdir -p evals/multi-model-verify/fixtures/contract-coverage-history
cd evals/multi-model-verify/fixtures/contract-coverage-history
git show 4d8a121:evals/multi-model-verify/test_backup_lane.py > instance-10-pins.py
git show 8eacc8a:evals/multi-model-verify/test_backup_lane.py > instance-11-pins.py
git show f9fd9b9:evals/multi-model-verify/test_seat_reshuffle.py > instance-12-pins.py
cd -
```

- [ ] **Step 2: Write the three fixture documents**

The bodies below are verbatim from the documents at those commits, with
newlines collapsed. Create each file exactly as shown.

`instance-10-doc.md`:

```markdown
<!-- Verbatim historical text from parallax 4d8a121, backup-lane.md.
     Instance 10: the disposition sentence had no pin. Do not edit; this
     file is evidence, not documentation. -->
<!-- contract:start id=hist-10-control -->
if after the call the file is SMALLER than the captured offset, or absent
<!-- contract:end -->
<!-- contract:start id=hist-10-defect -->
That is a route-attribution failure — and specifically **not a reason to
re-read from zero**, which is the tempting wrong answer: the new file's
opening lines may belong to any session, so reading it attributes nothing
while looking like evidence.
<!-- contract:end -->
```

`instance-11-doc.md`:

```markdown
<!-- Verbatim historical text from parallax 8eacc8a, fallbacks.md.
     Instance 11: the pin stopped at "IS transient". Do not edit; this
     file is evidence, not documentation. -->
<!-- contract:start id=hist-11-control -->
a rotation under the call is the one member that IS transient
<!-- contract:end -->
<!-- contract:start id=hist-11-defect -->
a rotation under the call is the one member that IS transient — a
re-dispatch with a freshly captured offset would produce clean evidence.
<!-- contract:end -->
```

`instance-12-doc.md`:

```markdown
<!-- Verbatim historical text from parallax f9fd9b9, panels.md.
     Instance 12: the pin was the bare phrase "Claude Code 2.1.216",
     which occurred twice. Do not edit; this file is evidence, not
     documentation. -->
<!-- contract:start id=hist-12-control -->
Claude Code 2.1.216
<!-- contract:end -->
<!-- contract:start id=hist-12-defect -->
Check `claude --version` before dispatching the Fable lane; below the
floor the lane is UNAVAILABLE, not degraded - a panel drops to its
remaining lanes under panel-lane-loss, and a Fable-only remainder cannot
proceed at all.
<!-- contract:end -->
```

The em dashes in fixtures 10 and 11 are the characters in the historical
documents. Write the files as UTF-8.

- [ ] **Step 3: Verify each defect body against git before trusting it**

```bash
git show 4d8a121:skills/multi-model-verify/references/backup-lane.md | grep -c "while looking like evidence"
git show 8eacc8a:skills/multi-model-verify/references/fallbacks.md | grep -c "would produce clean evidence"
git show f9fd9b9:skills/multi-model-verify/references/panels.md | grep -c "cannot proceed at"
```

Expected: `1` from each. If any prints `0`, the fixture text is wrong.
Stop and re-extract rather than editing the expectation.

- [ ] **Step 4: Write the failing regression tests**

Append to `evals/multi-model-verify/test_contract_coverage.py`:

```python
from pathlib import Path

HISTORY = (Path(__file__).resolve().parent / "fixtures"
           / "contract-coverage-history")


def _history_case(stem):
    regions = collect_regions([HISTORY / f"{stem}-doc.md"])
    pins = collect_pins([HISTORY / f"{stem}-pins.py"])
    return regions, uncovered(regions, pins)


def test_catches_instance_10_missing_disposition_pin():
    """4d8a121: 'That is a route-attribution failure' had no pin."""
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
```

- [ ] **Step 5: Run the regression tests**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q -k "history or instance"`
Expected: 4 passed. If any fails, the checker does not catch a failure it
was built for. Stop and fix the checker, not the test.

- [ ] **Step 6: Run the full suite**

Run: `python -m pytest evals -q`
Expected: 213 passed, 1 skipped.

- [ ] **Step 7: Commit**

```bash
git add evals/multi-model-verify/fixtures/contract-coverage-history evals/multi-model-verify/test_contract_coverage.py
git commit -m "0.15.0: prove the checker catches pin-integrity instances 10, 11 and 12"
```

---

### Task 4: Wire the checker to the live repo, and mark the rotation guard

**Files:**
- Modify: `evals/multi-model-verify/test_contract_coverage.py`
- Modify: `skills/multi-model-verify/references/backup-lane.md`
- Modify: `evals/multi-model-verify/test_backup_lane.py`

**Interfaces:**
- Consumes: everything from Tasks 1 to 3.
- Produces: module constants `DECLARED_REGIONS: set[str]`, `DOC_PATHS: list[Path]`, `PIN_PATHS: list[Path]`, consumed by Tasks 5 and 6 which each add ids to `DECLARED_REGIONS`.

Simulated against the live tree before planning. Of the three rotation
guard regions, `rotation-guard-residual-gap` is ALREADY covered by an
existing whole-sentence pin. The other two are covered only by fragments
and will be reported.

- [ ] **Step 1: Write the failing live-repo tests**

Append to `evals/multi-model-verify/test_contract_coverage.py`:

```python
REPO = Path(__file__).resolve().parents[2]

DOC_PATHS = (
    sorted((REPO / "skills" / "multi-model-verify" / "references").glob("*.md"))
    + sorted((REPO / "agents").glob("*.md"))
)

# This module is excluded from pin collection on purpose. Its own
# assertions quote whole contract bodies, so including it would let the
# checker satisfy itself.
PIN_PATHS = [p for p in sorted((REPO / "evals" / "multi-model-verify")
                               .glob("test_*.py"))
             if p.name != Path(__file__).name]

DECLARED_REGIONS = {
    "rotation-guard-detection",
    "rotation-guard-disposition",
    "rotation-guard-residual-gap",
}


def test_declared_regions_match_the_documents():
    """Deleting a whole region takes its markers with it. Without this
    check the coverage test would then pass over nothing at all."""
    found = set(collect_regions(DOC_PATHS))
    missing = sorted(DECLARED_REGIONS - found)
    extra = sorted(found - DECLARED_REGIONS)
    assert not missing, (
        f"declared region(s) not found in any document: {missing}. "
        "A region was deleted or renamed.")
    assert not extra, (
        f"region(s) found but not declared: {extra}. "
        "Add them to DECLARED_REGIONS.")


def test_every_marked_region_is_locked_by_a_pin():
    regions = collect_regions(DOC_PATHS)
    misses = uncovered(regions, collect_pins(PIN_PATHS))
    assert not misses, format_failure(misses)
```

- [ ] **Step 2: Run and read the RED carefully**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q -k "declared or marked"`

Expected: **one failed, one passed.**
`test_declared_regions_match_the_documents` FAILS with all three declared
ids missing, because no markers exist yet.
`test_every_marked_region_is_locked_by_a_pin` PASSES VACUOUSLY over zero
regions. That is correct and expected at this step; it becomes meaningful
after Step 3. Do not treat the pass as evidence of anything.

- [ ] **Step 3: Add the markers to backup-lane.md**

In `skills/multi-model-verify/references/backup-lane.md`, the rotation
guard bullet becomes the text below. Only markers are added, and line
breaks move to let a marker sit on its own line. No word changes.

Markers are indented two spaces so they stay inside the list item. They
are HTML blocks, so the bullet renders as several paragraphs instead of
one. That is a rendering change with no word change, and these files are
read by agents, not published.

```markdown
- **Rotation guard.** The offset rule assumes an append-only file, and
  the kimi client does not guarantee one.
  <!-- contract:start id=rotation-guard-detection -->
  Before trusting the offset,
  confirm the stream did not rotate under the call: if after the call the
  file is SMALLER than the captured offset, or absent, it was rotated or
  replaced and every byte position from the earlier measurement is
  meaningless.
  <!-- contract:end -->
  <!-- contract:start id=rotation-guard-disposition -->
  That is a route-attribution failure — and specifically
  **not a reason to re-read from zero**, which is the tempting wrong
  answer: the new file's opening lines may belong to any session, so
  reading it attributes nothing while looking like evidence.
  <!-- contract:end -->
  Observed
  2026-07-26 (kimi-cli 1.49.0, Windows): rotation ATTEMPTS fire and fail
  with `PermissionError: [WinError 32]` because the log is still open, so
  offsets have held by accident rather than by design — do not build on
  that accident.
  <!-- contract:start id=rotation-guard-residual-gap -->
  The size test is necessary, not sufficient: a rotation
  whose replacement file grew back PAST the captured offset within the
  same call would slip through.
  <!-- contract:end -->
  That needs the pre-rotation offset to
  have been small, which only follows an immediately preceding rotation,
  so it is not worth a second mechanism — but if rotation ever starts
  succeeding here, compare file identity (creation time) too, not just
  length.
```

- [ ] **Step 4: Run the coverage test to see exactly which pins are short**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q -k "marked"`

Expected: FAIL naming exactly two regions,
`rotation-guard-detection` and `rotation-guard-disposition`.
`rotation-guard-residual-gap` must NOT be reported: `test_backup_lane.py`
already pins that sentence whole. If it IS reported, stop: something in
the marker placement changed the body.

- [ ] **Step 5: Extend the two short pins**

In `evals/multi-model-verify/test_backup_lane.py`, inside
`test_backup_lane_evidence_pins`, extend the two fragment pins. Keep the
existing comments above them; add the note below.

Replace:

```python
    assert ("if after the call the file is SMALLER than the captured "
            "offset, or absent") in body
```

with:

```python
    # 0.15.0: extended from a fragment to the whole rule, because the
    # contract coverage checker proved the fragment left the consequence
    # half of the detection rule unlocked.
    assert ("Before trusting the offset, confirm the stream did not "
            "rotate under the call: if after the call the file is "
            "SMALLER than the captured offset, or absent, it was rotated "
            "or replaced and every byte position from the earlier "
            "measurement is meaningless.") in body
```

Replace:

```python
    assert ("That is a route-attribution failure" in body)
```

with:

```python
    # 0.15.0: extended from a fragment to the whole rule. The fragment
    # named the failure class but locked none of the prohibition.
    assert ("That is a route-attribution failure — and specifically "
            "**not a reason to re-read from zero**, which is the "
            "tempting wrong answer: the new file's opening lines may "
            "belong to any session, so reading it attributes nothing "
            "while looking like evidence.") in body
```

The em dash in the second pin is the character already in the document.
`test_backup_lane.py` reads with `_norm`, which normalizes whitespace
only, so the character must match exactly.

- [ ] **Step 6: Run the coverage test to verify it passes**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q`
Expected: all passed.

- [ ] **Step 7: Run the full suite and the two skill gates**

Run: `python -m pytest evals -q`
Expected: 215 passed, 1 skipped.

Run: `python evals/tools/skill_lint.py skills/multi-model-verify --strict`
Expected: `PASS — 0 error(s), 0 warning(s)`

Run: `python evals/tools/skill_scanner.py skills`
Expected: `Summary: 0 CRITICAL, 0 WARN, 0 INFO`

- [ ] **Step 8: Commit**

```bash
git add evals/multi-model-verify/test_contract_coverage.py skills/multi-model-verify/references/backup-lane.md evals/multi-model-verify/test_backup_lane.py
git commit -m "0.15.0: mark the rotation guard and extend the two pins it proved short"
```

---

### Task 5: Mark the panel harness floor in both documents

**Files:**
- Modify: `skills/multi-model-verify/references/panels.md`
- Modify: `agents/fable-panel-reviewer.md`
- Modify: `evals/multi-model-verify/test_contract_coverage.py`
- Modify: `evals/multi-model-verify/test_seat_reshuffle.py`

**Interfaces:**
- Consumes: `DECLARED_REGIONS` from Task 4.
- Produces: two more ids in `DECLARED_REGIONS`.

The same rule is stated in two documents in different words, so it needs
two ids. A single id could not tell the reader which file to open.

- [ ] **Step 1: Add the two ids to the declared set**

In `evals/multi-model-verify/test_contract_coverage.py`, extend:

```python
DECLARED_REGIONS = {
    "rotation-guard-detection",
    "rotation-guard-disposition",
    "rotation-guard-residual-gap",
    "panel-floor-reference",
    "panel-floor-agent",
}
```

- [ ] **Step 2: Run to verify the inventory test fails**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q -k "declared"`
Expected: FAIL, `declared region(s) not found in any document:
['panel-floor-agent', 'panel-floor-reference']`

- [ ] **Step 3: Mark the operative sentence in panels.md**

In `skills/multi-model-verify/references/panels.md`, put
`<!-- contract:start id=panel-floor-reference -->` on its own line
immediately before the sentence beginning ``Check `claude``, and
`<!-- contract:end -->` on its own line immediately after
`quietly convening a smaller panel.` Move line breaks as needed so each
marker owns its line; change no words. Indent both markers to match the
surrounding text so they stay inside the list item.

The marked body must normalize to exactly:

```
Check `claude --version` before dispatching the Fable lane; below the floor the lane is UNAVAILABLE, not degraded, and the case routes to fallbacks.md's `panel-lane-unavailable` - which, like every other lane loss, stops at the consent gate rather than quietly convening a smaller panel.
```

The narrative sentences before it, and the changelog source note in
parentheses after it, stay outside.

- [ ] **Step 4: Mark the operative sentence in the agent file**

In `agents/fable-panel-reviewer.md`, mark the sentence stating what the
driver does, with id `panel-floor-agent`.

The target sentence sits inside the `- Later rounds arrive as resumed
messages` list item. Both markers are standalone lines indented TWO
SPACES, matching that bullet's content indent, exactly as in Step 3. A
marker at column zero would end the list item.

The marked body must normalize to exactly:

```
The driver checks `claude --version` against the floor before dispatching this seat; below it, the Fable lane is unavailable rather than degraded, because a silently unpinned fully-tooled agent is not a weaker reviewer, it is a different one.
```

- [ ] **Step 5: Run the coverage test to see both regions reported**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q -k "marked"`

Simulated before planning. Expect BOTH new regions reported and no
rotation guard region reported. The 0.14.4 pins are fragments, and
containment runs the other way: the pin must contain the region, not the
region contain the pin.

- [ ] **Step 6: Extend both pins to whole sentences**

In `evals/multi-model-verify/test_seat_reshuffle.py`, inside
`test_panels_reference_pins`, replace these two lines:

```python
    assert ("Check `claude --version` before dispatching the Fable "
            "lane") in nbody
    assert "the lane is UNAVAILABLE, not degraded" in nbody
```

with one whole-sentence pin:

```python
    # 0.15.0: was two fragments. The coverage checker proved neither
    # locked the routing half, which is the part that stops a quiet
    # reduction to a smaller panel.
    assert ("Check `claude --version` before dispatching the Fable "
            "lane; below the floor the lane is UNAVAILABLE, not "
            "degraded, and the case routes to fallbacks.md's "
            "`panel-lane-unavailable` - which, like every other lane "
            "loss, stops at the consent gate rather than quietly "
            "convening a smaller panel.") in nbody
```

In the same file, inside `test_fable_panel_reviewer_exists_and_pins`,
replace these two lines:

```python
    assert ("checks `claude --version` against the floor before "
            "dispatching this seat") in nbody
    assert "unavailable rather than degraded" in nbody
```

with:

```python
    # 0.15.0: was two fragments; neither locked the reason, which is the
    # sentence's whole point.
    assert ("The driver checks `claude --version` against the floor "
            "before dispatching this seat; below it, the Fable lane is "
            "unavailable rather than degraded, because a silently "
            "unpinned fully-tooled agent is not a weaker reviewer, it "
            "is a different one.") in nbody
```

- [ ] **Step 7: Run the coverage test to verify it passes**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q`
Expected: all passed.

- [ ] **Step 8: Run the full suite and both skill gates**

Run: `python -m pytest evals -q`
Expected: 215 passed, 1 skipped.

Run: `python evals/tools/skill_lint.py skills/multi-model-verify --strict`
Expected: `PASS — 0 error(s), 0 warning(s)`

Run: `python evals/tools/skill_scanner.py skills`
Expected: `Summary: 0 CRITICAL, 0 WARN, 0 INFO`

- [ ] **Step 9: Commit**

```bash
git add skills/multi-model-verify/references/panels.md agents/fable-panel-reviewer.md evals/multi-model-verify/test_contract_coverage.py evals/multi-model-verify/test_seat_reshuffle.py
git commit -m "0.15.0: mark the panel harness floor and extend the two pins it proved short"
```

---

### Task 6: Mark the panel lane failure classes

**Files:**
- Modify: `skills/multi-model-verify/references/fallbacks.md`
- Modify: `evals/multi-model-verify/test_contract_coverage.py`
- Modify: `evals/multi-model-verify/test_seat_reshuffle.py`

**Interfaces:**
- Consumes: `DECLARED_REGIONS` from Tasks 4 and 5.
- Produces: four more ids, completing the inventory at nine.

Scope narrowing, recorded deliberately. `fallbacks.md` states its classes
in two shapes: ten `###`-headed entries, and a bullet list of backup-lane
classes under the backup reviewer section. Five entries name a class in
backticks. No single count covers them all, so the selection rule is
stated instead of a total: this task marks the two entries with recorded
failures behind them, both `###`-headed, `panel-lane-loss` at
`fallbacks.md:190` and `panel-lane-unavailable` at `fallbacks.md:210`.
The 0.14.4 review found that new text contradicted `panel-lane-loss`
while inventing mechanics for a case that had no class, so these two are
where the evidence is. The rest get marked as they are next edited.

`panel-lane-unavailable` becomes THREE regions, not one, because one
region is one pin and its disposition paragraph states three separate
rules: the shared principle, the pre-round-1 procedure, and the panel
invariant. Splitting is the design's answer to a paragraph too long for
a single pin.

- [ ] **Step 1: Add the four ids to the declared set**

```python
DECLARED_REGIONS = {
    "rotation-guard-detection",
    "rotation-guard-disposition",
    "rotation-guard-residual-gap",
    "panel-floor-reference",
    "panel-floor-agent",
    "panel-lane-loss-disposition",
    "panel-unavailable-principle",
    "panel-unavailable-procedure",
    "panel-unavailable-invariant",
}
```

- [ ] **Step 2: Run to verify the inventory test fails**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q -k "declared"`
Expected: FAIL naming all four new ids as not found.

- [ ] **Step 3: Mark the panel-lane-loss disposition**

In `skills/multi-model-verify/references/fallbacks.md`, wrap the sentence
that already sits on its own line, with id `panel-lane-loss-disposition`,
so the marked body is exactly:

```
A lost lane stops the panel at the consent gate - continuing with fewer lanes never happens automatically.
```

Simulated before planning: this region is ALREADY covered by an existing
whole-sentence pin and must NOT be reported in Step 5. It is marked so
the region inventory protects it from deletion.

- [ ] **Step 4: Mark the three panel-lane-unavailable rules**

In the `panel-lane-unavailable` section, mark three consecutive regions.
Move line breaks so each marker owns its line; change no words. The
sentence after the third region, beginning `An unavailable lane is
recorded`, stays outside.

`panel-unavailable-principle`:

```
The disposition is the same in the one respect that matters: the panel cannot silently convene without it.
```

`panel-unavailable-procedure`:

```
Before round 1 the driver states which lanes it can actually convene and which it cannot, with the reason, and the user chooses - proceed with the convenable composition, substitute, or abort.
```

`panel-unavailable-invariant`:

```
The panel invariant still binds whatever is chosen: at least one cross-vendor lane, so a composition reduced to Fable alone is not a panel and cannot proceed as one.
```

- [ ] **Step 5: Run the coverage test**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q -k "marked"`

Simulated before planning: exactly the three `panel-unavailable-*`
regions are reported. `panel-lane-loss-disposition` is not. The 0.14.4
pin is a fragment of the principle sentence, and nothing pins the
procedure or the invariant at all.

- [ ] **Step 6: Extend the short pin into three whole-sentence pins**

In `evals/multi-model-verify/test_seat_reshuffle.py`, inside
`test_fallbacks_panel_lane_loss`, replace this line:

```python
    assert ("the panel cannot silently convene without it") in nfb
```

with three whole-sentence pins, using the normalized reader already in
that module:

```python
    # 0.15.0: was a fragment. The coverage checker proved all three
    # rules of the disposition unlocked - including the only place that
    # says the driver must state the convenable composition BEFORE
    # round 1, which is what stops a quiet reduction.
    assert ("The disposition is the same in the one respect that "
            "matters: the panel cannot silently convene without "
            "it.") in nfb
    assert ("Before round 1 the driver states which lanes it can "
            "actually convene and which it cannot, with the reason, and "
            "the user chooses - proceed with the convenable "
            "composition, substitute, or abort.") in nfb
    assert ("The panel invariant still binds whatever is chosen: at "
            "least one cross-vendor lane, so a composition reduced to "
            "Fable alone is not a panel and cannot proceed as "
            "one.") in nfb
```

Re-run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q`
Expected: all passed.

- [ ] **Step 7: Run the full suite and both skill gates**

Run: `python -m pytest evals -q`
Expected: 215 passed, 1 skipped.

Run: `python evals/tools/skill_lint.py skills/multi-model-verify --strict`
Expected: `PASS — 0 error(s), 0 warning(s)`

Run: `python evals/tools/skill_scanner.py skills`
Expected: `Summary: 0 CRITICAL, 0 WARN, 0 INFO`

- [ ] **Step 8: Commit**

```bash
git add skills/multi-model-verify/references/fallbacks.md evals/multi-model-verify/test_contract_coverage.py evals/multi-model-verify/test_seat_reshuffle.py
git commit -m "0.15.0: mark the panel lane failure classes"
```

---

### Task 7: Document the mechanism and bump the version

**Files:**
- Modify: `README.md`
- Modify: `CLAUDE.md`
- Modify: `.claude-plugin/plugin.json`

**Interfaces:**
- Consumes: the finished checker.
- Produces: nothing consumed by later tasks. This is the last task.

- [ ] **Step 1: Add the rule to CLAUDE.md**

In `CLAUDE.md`, under `## Skill editing rules`, append:

```markdown
Contract text inside `contract:start` / `contract:end` HTML comment
markers must sit WHOLE inside a single pin in `evals/multi-model-verify/`.

A pin is a string literal in one of exactly three assertion clause forms:

- `"literal" in body`
- `body.count("literal")`, alone or compared `== n` or `>= n` with n at
  least 1, or `> n` with n at least 0
- an `and` of those

The needle must be a plain string literal. Adjacent literals across
several lines are fine, because the parser folds them into one.

Nothing else counts, and the rule matches a COMPLETE clause rather than
looking for these shapes anywhere in the expression. A string locks
nothing if it sits in a docstring, in an assertion's failure message,
under `not`, in a `not in` comparison, on either side of an `or`, in a
zero or negative count comparison, in a plain equality such as
`result == "text"`, in a regex such as `re.search(...)`, in either branch
of a conditional, or is reached through a variable name. Any positive
assertion outside the three forms above is rejected, whatever it means.
In every one of those cases the checker reports the region as unlocked,
which is a red; it never reads as covered.

`test_contract_coverage.py` enforces this and lists any region that is
not locked. A region too long for one pin is two regions. Adding or
removing a marked region also means editing `DECLARED_REGIONS` in that
file, which is what makes deleting a region visible.
```

- [ ] **Step 2: Add a row to the README component table**

In `README.md`, in the table that lists `hooks/` and `tools/`, add:

```markdown
| `evals/multi-model-verify/contract_coverage.py` | Contract coverage: every marked document region must sit whole inside some test pin. Closes the pin-integrity class that produced twelve instances across three cycles |
```

- [ ] **Step 3: Bump the version**

In `.claude-plugin/plugin.json`, change `"version": "0.14.4"` to
`"version": "0.15.0"`.

- [ ] **Step 4: Run every gate**

Run: `python -m pytest evals -q`
Expected: 215 passed, 1 skipped.

Run: `python evals/tools/skill_lint.py skills/multi-model-verify --strict`
Expected: `PASS — 0 error(s), 0 warning(s)`

Run: `python evals/tools/skill_scanner.py skills`
Expected: `Summary: 0 CRITICAL, 0 WARN, 0 INFO`

Run: `python evals/tools/run_trigger_evals.py`
Expected: `trigger & routing: all clear (1 skill)`

- [ ] **Step 5: Commit**

```bash
git add README.md CLAUDE.md .claude-plugin/plugin.json
git commit -m "0.15.0: document the contract coverage checker and bump the version"
```

---

## After the plan

This is a mode-diff change to skill contracts, so the standing repo rules
apply before merge: the required whole-branch review from
`agents/fable-reviewer.md`, then a cross-vendor debate, then the session's
own final adjudication, then the attestation emitter with
`-RouteNote "effective route confirmed"` exactly, since any other text
fails the pre-push check.

Backlog item 5 rewrites the rotation guard paragraph, and part of that
paragraph is now inside markers. That is the mechanism working as
designed: changing marked text without updating its pin turns the
coverage test red. Item 5 should be planned separately and should expect
to update the two pins extended in Task 4.

## Counts, and what to do if they differ

Expected `python -m pytest evals -q` after each task: 190, 209, 213, 215,
215, 215, 215 passed, with 1 skipped throughout. These come from the test
functions this plan adds: 20 in Task 1, 19 in Task 2, 4 in Task 3, 2 in
Task 4, none in Tasks 5 to 7. If a number differs, count the tests you
actually added before assuming a regression.
