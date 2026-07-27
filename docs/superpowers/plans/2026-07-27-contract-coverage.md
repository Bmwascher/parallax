# Contract Coverage Checker Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make it impossible for a contract sentence in a marked region to go unpinned, or for a marked region to be deleted, without a test turning red.

**Architecture:** A pure-function module parses `<!-- contract:start id=... -->` regions out of the reference and agent documents, extracts every string constant from the test modules through Python's `ast`, and requires each sentence of each region to sit whole inside one of those strings. A separate declared inventory of region ids closes the delete-the-whole-region hole. The checker is consumed by one pytest module.

**Tech Stack:** Python 3.12 standard library only (`ast`, `re`, `pathlib`), pytest 9.x, `tmp_path` fixtures. No new dependencies.

## Global Constraints

- Design spec: `docs/superpowers/specs/2026-07-27-contract-coverage-design.md`. Copied verbatim below where a task depends on it.
- Whole-sentence containment. A sentence is covered only when one pin string contains it in full. Overlap does not count.
- Region ids are unique across the whole repo, not per file.
- All marker and coverage problems are hard test failures. Never warnings, never skips.
- Sentence split rule: `.`, `?` or `!` followed by whitespace then a capital letter. Abbreviation exceptions, exactly this list: `e.g.`, `i.e.`, `vs.`, `etc.`, `cf.`
- Region text and pin text are both whitespace-normalized before comparison, matching the existing `_norm` convention (`" ".join(text.split())`).
- Do not modify the 633 existing assert statements in `evals/**/test_*.py` except to extend ones the checker proves are short.
- Do not reword any text inside a marked region in this plan. Rewording contract text is a separate reviewed change. Item 5 of the backlog will do that for the rotation guard.
- Every task ends green on all four offline gates:
  `python evals/tools/skill_lint.py skills/multi-model-verify --strict`,
  `python evals/tools/skill_scanner.py skills`,
  `python evals/tools/run_trigger_evals.py`,
  `python -m pytest evals -q`
- Verified before planning, do not re-litigate: HTML comment markers pass `skill_lint --strict` and `skill_scanner` with zero findings, and a sibling module next to the test files is importable under pytest with no `conftest.py`.

---

## File Structure

| file | responsibility |
|---|---|
| `evals/multi-model-verify/contract_coverage.py` | Create. Pure functions: marker parsing, sentence splitting, pin extraction, coverage. No pytest imports, no I/O beyond reading paths it is handed. |
| `evals/multi-model-verify/test_contract_coverage.py` | Create. The declared region inventory, the live repo check, and the fixture tests that prove the checker. |
| `evals/multi-model-verify/fixtures/contract-coverage-history/` | Create. Three verbatim historical snippets proving the checker catches instances 10, 11 and 12. |
| `skills/multi-model-verify/references/backup-lane.md` | Modify. Add markers around the rotation guard rule and residual gap. |
| `skills/multi-model-verify/references/panels.md` | Modify. Add markers around the harness floor. |
| `agents/fable-panel-reviewer.md` | Modify. Add markers around the harness floor as stated there. |
| `skills/multi-model-verify/references/fallbacks.md` | Modify. Add markers around the two panel lane classes. |
| `evals/multi-model-verify/test_backup_lane.py` | Modify. Extend two short pins the checker will flag. |
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
"""Contract coverage: every sentence in a marked region must sit whole
inside some test pin.

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
        "One sentence   here.\nAnd  another.\n"
        "<!-- contract:end -->\n"
        "trailing line\n"
    )
    regions = parse_regions(text, "demo.md")
    assert regions == {"demo": "One sentence here. And another."}


def test_text_outside_markers_is_not_part_of_the_region():
    text = (
        "Rationale that must never demand a pin.\n"
        "<!-- contract:start id=demo -->\n"
        "The rule.\n"
        "<!-- contract:end -->\n"
        "More rationale.\n"
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

Every sentence inside a marked region must sit WHOLE inside some pin
string. Pure functions only: no pytest, no repo paths baked in, so the
fixture tests can drive it over temporary directories.

Design: docs/superpowers/specs/2026-07-27-contract-coverage-design.md
"""
import ast
import re

START = re.compile(r"<!--\s*contract:start\s+id=([a-z0-9][a-z0-9-]*)\s*-->")
END = re.compile(r"<!--\s*contract:end\s*-->")

# Deliberately a fixed, short list. An abbreviation NOT on it causes a
# wrong split, which demands a pin for a fragment - a visible red, never
# a silent pass. The failure direction is safe by construction.
ABBREVIATIONS = ("e.g.", "i.e.", "vs.", "etc.", "cf.")


class MarkerError(Exception):
    """Malformed or mis-declared markers. Always a hard failure."""


def _norm(text):
    return " ".join(text.split())


def parse_regions(text, source):
    """Return {region_id: normalized_body} for ONE document."""
    regions = {}
    open_id = None
    buf = []
    for lineno, line in enumerate(text.splitlines(), 1):
        start = START.search(line)
        end = END.search(line)
        if start and end:
            raise MarkerError(
                f"{source}:{lineno}: start and end markers on one line")
        if start:
            if open_id is not None:
                raise MarkerError(
                    f"{source}:{lineno}: region '{start.group(1)}' opens "
                    f"inside still-open region '{open_id}'")
            open_id = start.group(1)
            buf = []
            continue
        if end:
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
Expected: 9 passed.

- [ ] **Step 5: Run the full suite to confirm nothing regressed**

Run: `python -m pytest evals -q`
Expected: 179 passed, 1 skipped.

- [ ] **Step 6: Commit**

```bash
git add evals/multi-model-verify/contract_coverage.py evals/multi-model-verify/test_contract_coverage.py
git commit -m "0.15.0: parse contract regions and enforce unique region ids"
```

---

### Task 2: Sentence splitting, pin extraction, coverage

**Files:**
- Modify: `evals/multi-model-verify/contract_coverage.py`
- Modify: `evals/multi-model-verify/test_contract_coverage.py`

**Interfaces:**
- Consumes: `parse_regions`, `collect_regions`, `MarkerError` from Task 1.
- Produces: `split_sentences(text: str) -> list[str]`; `collect_pins(paths: list[Path]) -> set[str]` returning whitespace-normalized string constants; `uncovered(regions: dict[str, tuple[str, str]], pins: set[str]) -> list[tuple[str, str, str]]` returning `(region_id, source_name, sentence)` for every sentence with no containing pin; `format_failure(misses: list) -> str`.

- [ ] **Step 1: Write the failing tests**

Append to `evals/multi-model-verify/test_contract_coverage.py`:

```python
from contract_coverage import (
    collect_pins, format_failure, split_sentences, uncovered)


def test_splits_on_sentence_end_followed_by_a_capital():
    text = "First rule here. Second rule here. Third rule here."
    assert split_sentences(text) == [
        "First rule here.", "Second rule here.", "Third rule here."]


def test_does_not_split_inside_a_version_or_filename():
    text = "Check claude --version against 2.1.216 before dispatch."
    assert split_sentences(text) == [
        "Check claude --version against 2.1.216 before dispatch."]


def test_does_not_split_after_a_known_abbreviation():
    text = "Some lanes, e.g. Sol, are cross-vendor. That is the rule."
    assert split_sentences(text) == [
        "Some lanes, e.g. Sol, are cross-vendor.", "That is the rule."]


def test_collects_pins_and_joins_implicit_concatenation(tmp_path):
    src = (
        'def test_x():\n'
        '    assert ("a rotation under the call is the one member "\n'
        '            "that IS transient") in body\n'
    )
    p = tmp_path / "test_sample.py"
    p.write_text(src, encoding="utf-8")
    pins = collect_pins([p])
    assert "a rotation under the call is the one member that IS transient" in pins


def test_pins_are_whitespace_normalized(tmp_path):
    p = tmp_path / "test_sample.py"
    p.write_text('X = "two   spaces\\nand a newline"\n', encoding="utf-8")
    assert "two spaces and a newline" in collect_pins([p])


def test_a_fully_covered_region_reports_nothing():
    regions = {"demo": ("The rule stands.", "demo.md")}
    pins = {"the text says The rule stands. right here"}
    assert uncovered(regions, pins) == []


def test_a_sentence_with_no_pin_at_all_is_reported():
    """Instance 10: the consequence sentence had no pin."""
    regions = {"demo": ("Detect it. That is a route-attribution failure.",
                        "backup-lane.md")}
    pins = {"Detect it."}
    misses = uncovered(regions, pins)
    assert misses == [
        ("demo", "backup-lane.md", "That is a route-attribution failure.")]


def test_a_pin_that_stops_mid_sentence_does_not_cover_it():
    """Instance 11: the pin stopped at 'IS transient'."""
    sentence = ("A rotation is the one member that IS transient, so the "
                "user decides whether to spend another.")
    regions = {"demo": (sentence, "fallbacks.md")}
    pins = {"A rotation is the one member that IS transient"}
    assert uncovered(regions, pins) == [("demo", "fallbacks.md", sentence)]


def test_failure_message_names_region_file_and_sentence():
    misses = [("demo", "panels.md", "The lane is UNAVAILABLE, not degraded.")]
    msg = format_failure(misses)
    assert "demo" in msg
    assert "panels.md" in msg
    assert "The lane is UNAVAILABLE, not degraded." in msg
    assert "add a pin containing that sentence whole" in msg
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q`
Expected: `ImportError: cannot import name 'collect_pins'`.

- [ ] **Step 3: Extend the module**

Append to `evals/multi-model-verify/contract_coverage.py`:

```python
def split_sentences(text):
    """Split a normalized region into sentences.

    Rule: a sentence ends at . ? or ! followed by whitespace then a
    capital letter, unless the run ends with a known abbreviation. A
    wrong split demands a pin for a fragment, which is loud; it can never
    hide a gap.
    """
    parts = []
    start = 0
    for match in re.finditer(r"[.?!]\s+(?=[A-Z])", text):
        head = text[start:match.end()].rstrip()
        if any(head.endswith(abbr) for abbr in ABBREVIATIONS):
            continue
        parts.append(head)
        start = match.end()
    tail = text[start:].strip()
    if tail:
        parts.append(tail)
    return [p for p in parts if p]


def collect_pins(paths):
    """Every string constant in the given Python files, normalized.

    Read through ast, not regex: nearly every pin in this repo is written
    as adjacent string literals across several lines, and the parser
    joins those into one constant for us.
    """
    pins = set()
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                pins.add(_norm(node.value))
    return pins


def uncovered(regions, pins):
    """[(region_id, source, sentence)] for every sentence with no pin."""
    misses = []
    for rid in sorted(regions):
        body, source = regions[rid]
        for sentence in split_sentences(body):
            if not any(sentence in pin for pin in pins):
                misses.append((rid, source, sentence))
    return misses


def format_failure(misses):
    lines = [
        f"{len(misses)} contract sentence(s) are not locked by any pin.",
        "For each one, add a pin containing that sentence whole.",
        "",
    ]
    for rid, source, sentence in misses:
        lines.append(f"  region '{rid}' in {source}:")
        lines.append(f"    {sentence}")
    return "\n".join(lines)
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q`
Expected: 18 passed.

- [ ] **Step 5: Run the full suite**

Run: `python -m pytest evals -q`
Expected: 188 passed, 1 skipped.

- [ ] **Step 6: Commit**

```bash
git add evals/multi-model-verify/contract_coverage.py evals/multi-model-verify/test_contract_coverage.py
git commit -m "0.15.0: add sentence splitting, pin extraction, and coverage"
```

---

### Task 3: Prove the checker catches the three real failures

The checker must catch the failures that motivated it. This task builds
hermetic fixtures from the real historical text so CI needs no git
history.

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

Verified facts these fixtures encode, confirmed against git before planning:
- At `4d8a121` the sentence `That is a route-attribution failure` appeared once in `backup-lane.md` and zero times in `test_backup_lane.py`.
- At `8eacc8a` the fallbacks pin was exactly `("a rotation under the call is the one member that IS " "transient") in fb`.
- At `f9fd9b9` the panels pin was exactly `assert "Claude Code 2.1.216" in body`.

- [ ] **Step 1: Build the fixtures from git history**

```bash
mkdir -p evals/multi-model-verify/fixtures/contract-coverage-history
cd evals/multi-model-verify/fixtures/contract-coverage-history

git show 4d8a121:skills/multi-model-verify/references/backup-lane.md \
  | sed -n '/- \*\*Rotation guard\.\*\*/,/- This evidence is client-side/p' \
  | head -n -1 > instance-10-body.txt

git show 8eacc8a:skills/multi-model-verify/references/fallbacks.md \
  | sed -n '/route-attribution failure (offset rule/,/does not describe\./p' \
  > instance-11-body.txt

git show f9fd9b9:skills/multi-model-verify/references/panels.md \
  | sed -n '/\*\*Harness floor/,/triaged 2026-07-27\.)/p' \
  > instance-12-body.txt

git show 4d8a121:evals/multi-model-verify/test_backup_lane.py > instance-10-pins.py
git show 8eacc8a:evals/multi-model-verify/test_backup_lane.py > instance-11-pins.py
git show f9fd9b9:evals/multi-model-verify/test_seat_reshuffle.py > instance-12-pins.py
cd -
```

- [ ] **Step 2: Wrap each body in markers to make it a region**

For each of the three `instance-NN-body.txt` files, create the matching
`instance-NN-doc.md` by adding a header comment and the markers. Example
for instance 10, and repeat the same shape for 11 and 12 with ids
`hist-instance-11` and `hist-instance-12`:

```bash
cd evals/multi-model-verify/fixtures/contract-coverage-history
{ echo '<!-- Verbatim historical text from parallax 4d8a121. Instance 10:'
  echo '     the disposition sentence had no pin. Do not edit; this file'
  echo '     is evidence, not documentation. -->'
  echo '<!-- contract:start id=hist-instance-10 -->'
  cat instance-10-body.txt
  echo '<!-- contract:end -->'
} > instance-10-doc.md
rm instance-10-body.txt
cd -
```

- [ ] **Step 3: Write the failing regression tests**

Append to `evals/multi-model-verify/test_contract_coverage.py`:

```python
from pathlib import Path

HISTORY = (Path(__file__).resolve().parent / "fixtures"
           / "contract-coverage-history")


def _history_case(stem):
    regions = collect_regions([HISTORY / f"{stem}-doc.md"])
    pins = collect_pins([HISTORY / f"{stem}-pins.py"])
    return uncovered(regions, pins)


def test_catches_instance_10_missing_disposition_pin():
    """4d8a121: 'That is a route-attribution failure' had no pin."""
    misses = _history_case("instance-10")
    assert any("That is a route-attribution failure" in sentence
               for _, _, sentence in misses)


def test_catches_instance_11_pin_stopping_mid_sentence():
    """8eacc8a: the pin ended at 'IS transient'."""
    misses = _history_case("instance-11")
    assert any("the user decides at the gate whether to spend another"
               in sentence for _, _, sentence in misses)


def test_catches_instance_12_bare_phrase_pin():
    """f9fd9b9: the pin was the bare phrase 'Claude Code 2.1.216'."""
    misses = _history_case("instance-12")
    assert any("UNAVAILABLE" in sentence or "Check `claude" in sentence
               for _, _, sentence in misses)


def test_history_fixtures_are_not_vacuous():
    """A fixture that parsed to zero regions would pass every test above
    for the wrong reason."""
    for stem in ("instance-10", "instance-11", "instance-12"):
        regions = collect_regions([HISTORY / f"{stem}-doc.md"])
        assert len(regions) == 1, f"{stem} must contain exactly one region"
        assert regions, f"{stem} parsed to no regions"
```

- [ ] **Step 4: Run the regression tests**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q -k "history or instance"`
Expected: 4 passed. If any fails, the checker does not catch a failure it
was built for. Stop and fix the checker, not the test.

- [ ] **Step 5: Run the full suite**

Run: `python -m pytest evals -q`
Expected: 192 passed, 1 skipped.

- [ ] **Step 6: Commit**

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

Simulated against the live tree before planning. The rotation guard
paragraph splits into six sentences. Only sentence 5 is covered today.
Sentences 1, 4 and 6 are rationale and observation and stay OUTSIDE the
markers. Sentences 2 and 3 are operative and are short-pinned, so this
task will flag them.

- [ ] **Step 1: Write the failing live-repo tests**

Append to `evals/multi-model-verify/test_contract_coverage.py`:

```python
REPO = Path(__file__).resolve().parents[2]

DOC_PATHS = (
    sorted((REPO / "skills" / "multi-model-verify" / "references").glob("*.md"))
    + sorted((REPO / "agents").glob("*.md"))
)

# This module is excluded from pin collection on purpose. Its fixture
# strings contain whole contract sentences, so including it would let the
# checker satisfy itself.
PIN_PATHS = [p for p in sorted((REPO / "evals" / "multi-model-verify")
                               .glob("test_*.py"))
             if p.name != Path(__file__).name]

DECLARED_REGIONS = {
    "rotation-guard-rule",
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


def test_every_marked_sentence_is_locked_by_a_pin():
    regions = collect_regions(DOC_PATHS)
    misses = uncovered(regions, collect_pins(PIN_PATHS))
    assert not misses, format_failure(misses)
```

- [ ] **Step 2: Run to verify both fail**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q -k "declared or marked"`
Expected: `test_declared_regions_match_the_documents` fails with both
declared ids missing, because no markers exist yet.

- [ ] **Step 3: Add the markers to backup-lane.md**

In `skills/multi-model-verify/references/backup-lane.md`, the rotation
guard bullet becomes the text below. Only markers are added. No word of
the existing text changes.

```markdown
- **Rotation guard.** The offset rule assumes an append-only file, and
  the kimi client does not guarantee one.
<!-- contract:start id=rotation-guard-rule -->
  Before trusting the offset,
  confirm the stream did not rotate under the call: if after the call the
  file is SMALLER than the captured offset, or absent, it was rotated or
  replaced and every byte position from the earlier measurement is
  meaningless. That is a route-attribution failure — and specifically
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
Expected: FAIL naming region `rotation-guard-rule` and these two
sentences, which are the two operative halves the current pins only
partially cover:

```
Before trusting the offset, confirm the stream did not rotate under the call: if after the call the file is SMALLER than the captured offset, or absent, it was rotated or replaced and every byte position from the earlier measurement is meaningless.
That is a route-attribution failure — and specifically **not a reason to re-read from zero**, which is the tempting wrong answer: the new file's opening lines may belong to any session, so reading it attributes nothing while looking like evidence.
```

- [ ] **Step 5: Extend the two short pins**

In `evals/multi-model-verify/test_backup_lane.py`, inside
`test_backup_lane_evidence_pins`, replace the two partial pins with full
sentence pins. Keep the existing comments above them; add the note below.

Replace:

```python
    assert ("if after the call the file is SMALLER than the captured "
            "offset, or absent") in body
```

with:

```python
    # 0.15.0: extended from a fragment to the whole sentence, because the
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
    assert ("That is a route-attribution failure — and specifically "
            "**not a reason to re-read from zero**, which is the "
            "tempting wrong answer: the new file's opening lines may "
            "belong to any session, so reading it attributes nothing "
            "while looking like evidence.") in body
```

Note the em dash in the second pin is the character already in the
document. `test_backup_lane.py` reads with `_norm`, which normalizes
whitespace only, so the character must match exactly.

- [ ] **Step 6: Run the coverage test to verify it passes**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q`
Expected: all passed.

- [ ] **Step 7: Run the full suite and the two skill gates**

Run: `python -m pytest evals -q`
Expected: 194 passed, 1 skipped.

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
- Modify: `evals/multi-model-verify/test_seat_reshuffle.py` (only if the checker proves a pin short)

**Interfaces:**
- Consumes: `DECLARED_REGIONS` from Task 4.
- Produces: two more ids in `DECLARED_REGIONS`.

The same rule is stated in two documents in different words, so it needs
two ids. A single id could not tell the reader which file to open.

- [ ] **Step 1: Add the two ids to the declared set**

In `evals/multi-model-verify/test_contract_coverage.py`, extend:

```python
DECLARED_REGIONS = {
    "rotation-guard-rule",
    "rotation-guard-residual-gap",
    "panel-floor-reference",
    "panel-floor-agent",
}
```

- [ ] **Step 2: Run to verify the inventory test fails**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q -k "declared"`
Expected: FAIL, `declared region(s) not found in any document:
['panel-floor-agent', 'panel-floor-reference']`

- [ ] **Step 3: Mark the operative sentences in panels.md**

In `skills/multi-model-verify/references/panels.md`, wrap only the
operative sentence. The narrative sentences before it, and the changelog
source note after it, stay outside.

Place `<!-- contract:start id=panel-floor-reference -->` immediately
before the sentence beginning `Check \`claude`, and
`<!-- contract:end -->` immediately after `rather than quietly convening
a smaller panel.` so the marked body is exactly:

```
Check `claude --version` before dispatching the Fable lane; below the floor the lane is UNAVAILABLE, not degraded, and the case routes to fallbacks.md's `panel-lane-unavailable` - which, like every other lane loss, stops at the consent gate rather than quietly convening a smaller panel.
```

- [ ] **Step 4: Mark the operative sentence in the agent file**

In `agents/fable-panel-reviewer.md`, wrap the sentence stating what the
driver does, with id `panel-floor-agent`, so the marked body is exactly:

```
The driver checks `claude --version` against the floor before dispatching this seat; below it, the Fable lane is unavailable rather than degraded, because a silently unpinned fully-tooled agent is not a weaker reviewer, it is a different one.
```

- [ ] **Step 5: Run the coverage test to see both pins are short**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q -k "marked"`

Simulated before planning. Expect BOTH sentences reported. The 0.14.4
pins are fragments, and containment runs the other way: the pin must
contain the sentence, not the sentence contain the pin.

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
Expected: 194 passed, 1 skipped.

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

### Task 6: Mark the two panel lane failure classes

**Files:**
- Modify: `skills/multi-model-verify/references/fallbacks.md`
- Modify: `evals/multi-model-verify/test_contract_coverage.py`
- Modify: `evals/multi-model-verify/test_seat_reshuffle.py` (only if the checker proves a pin short)

**Interfaces:**
- Consumes: `DECLARED_REGIONS` from Tasks 4 and 5.
- Produces: two more ids, completing the inventory at six.

Scope narrowing, recorded deliberately. `fallbacks.md` states its
classes in two shapes: ten `###`-headed entries, and a bullet list of
backup-lane classes under the backup reviewer section. Five entries name
a class in backticks. No single count covers them all, so the selection
rule is stated instead of a total: this task marks the two entries with
recorded failures behind them, both `###`-headed, `panel-lane-loss` at
`fallbacks.md:190` and `panel-lane-unavailable` at `fallbacks.md:210`. The 0.14.4 review
found that new text contradicted `panel-lane-loss` while inventing
mechanics for a case that had no class, so these two are where the
evidence is. The other nine get marked as they are next edited.

- [ ] **Step 1: Add the two ids to the declared set**

```python
DECLARED_REGIONS = {
    "rotation-guard-rule",
    "rotation-guard-residual-gap",
    "panel-floor-reference",
    "panel-floor-agent",
    "panel-lane-loss-disposition",
    "panel-lane-unavailable-disposition",
}
```

- [ ] **Step 2: Run to verify the inventory test fails**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q -k "declared"`
Expected: FAIL naming both new ids as not found.

- [ ] **Step 3: Mark the panel-lane-loss disposition**

In `skills/multi-model-verify/references/fallbacks.md`, wrap the sentence
that is already pinned by `test_fallbacks_panel_lane_loss`, with id
`panel-lane-loss-disposition`, so the marked body is exactly:

```
A lost lane stops the panel at the consent gate - continuing with fewer lanes never happens automatically.
```

- [ ] **Step 4: Mark the panel-lane-unavailable disposition**

Wrap the three sentences added in 0.14.4 that state what the class does,
with id `panel-lane-unavailable-disposition`, so the marked body is
exactly:

```
The disposition is the same in the one respect that matters: the panel cannot silently convene without it. Before round 1 the driver states which lanes it can actually convene and which it cannot, with the reason, and the user chooses - proceed with the convenable composition, substitute, or abort. The panel invariant still binds whatever is chosen: at least one cross-vendor lane, so a composition reduced to Fable alone is not a panel and cannot proceed as one.
```

- [ ] **Step 5: Run the coverage test and extend any short pin**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q`

Simulated before planning: ALL THREE sentences are reported. The 0.14.4
pins are fragments of the first and third, and containment runs the other
way, so none of the three is locked.

In `evals/multi-model-verify/test_seat_reshuffle.py`, inside
`test_fallbacks_panel_lane_loss`, replace this line:

```python
    assert ("the panel cannot silently convene without it") in nfb
```

with three whole-sentence pins, using the normalized reader already in
that module:

```python
    # 0.15.0: was a fragment. The coverage checker proved all three
    # sentences of the disposition unlocked - including the only place
    # that says the driver must state the convenable composition BEFORE
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

- [ ] **Step 6: Run the full suite and both skill gates**

Run: `python -m pytest evals -q`
Expected: 194 passed, 1 skipped.

Run: `python evals/tools/skill_lint.py skills/multi-model-verify --strict`
Expected: `PASS — 0 error(s), 0 warning(s)`

Run: `python evals/tools/skill_scanner.py skills`
Expected: `Summary: 0 CRITICAL, 0 WARN, 0 INFO`

- [ ] **Step 7: Commit**

```bash
git add skills/multi-model-verify/references/fallbacks.md evals/multi-model-verify/test_contract_coverage.py evals/multi-model-verify/test_seat_reshuffle.py
git commit -m "0.15.0: mark the two panel lane failure classes"
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
Contract text inside `<!-- contract:start id=... -->` markers must have
every sentence locked whole by some pin in `evals/multi-model-verify/`.
`test_contract_coverage.py` enforces it and lists any sentence that is
not. Adding or removing a marked region also means editing
`DECLARED_REGIONS` in that file, which is what makes deleting a region
visible.
```

- [ ] **Step 2: Add a row to the README component table**

In `README.md`, in the table that lists `hooks/` and `tools/`, add:

```markdown
| `evals/multi-model-verify/contract_coverage.py` | Contract coverage: every sentence in a marked document region must sit whole inside some test pin. Closes the pin-integrity class that produced twelve instances across three cycles |
```

- [ ] **Step 3: Bump the version**

In `.claude-plugin/plugin.json`, change `"version": "0.14.4"` to
`"version": "0.15.0"`.

- [ ] **Step 4: Run every gate**

Run: `python -m pytest evals -q`
Expected: 194 passed, 1 skipped.

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
