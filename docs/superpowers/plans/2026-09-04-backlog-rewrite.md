# Backlog Rewrite and Maintenance Enforcement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the 5,905-line backlog with a root `BACKLOG.md` whose ranking and status are derived from item headers, checked by a lint, and kept current by project-scope hooks, a pre-push clause and CI.

**Architecture:** One Python checker (`evals/tools/backlog_lint.py`) owns the file grammar, the per-item content digest, the governed-range test and the revision reader; three small Python hook scripts under `tools/backlog-hooks/` call it from Claude Code's SessionStart, PostToolUse and Stop events; the bash pre-push hook and the CI workflow call the same `--range` mode so no two copies of the test exist. The content rewrite is one task, verified by a second reader against the old file's own text.

**Tech Stack:** Python 3.12 stdlib only (no third-party imports in tools or tests except pytest); git; bash pre-push hook under git-bash; PowerShell 5.1 and 7 as hook hosts; GitHub Actions.

**Spec:** `docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md`

## Global Constraints

- Python tools and tests are stdlib only; pytest is the only third-party import, and only in tests.
- Every PowerShell-facing test runs under BOTH hosts. Tests read `PARALLAX_PS_HOST` first, then `shutil.which("powershell")`, then `shutil.which("pwsh")`, exactly as `evals/multi-model-verify/test_kimi_lane_lock.py:29` does. New dual-host modules are added to BOTH host lists in `.github/workflows/skill-evals.yml`.
- Never pipe a test or gate run through `head`, `tail` or `Select-Object -Last`. Retain full output.
- Any parser that expects exactly one output line goes through `accept_exactly_one_nonempty_line()` from `evals/tools/exact_line.py`.
- Commit messages: lowercase, imperative, no AI attribution, and NEVER name a PowerShell flag such as `-Prepare` or `-Range` in the message (the family git guard denies it, backlog item 79). Write "the prepare mode" instead.
- Do not edit any file under `docs/superpowers/plans/rounds/` that exists before this branch; new files under the branch's own round directory are allowed.
- The lint never rewrites `BACKLOG.md`. Rule 7 reads only the file, never git.
- Exit codes of the lint: 0 clean, 1 any rule failure, 2 unreadable or unparseable input.
- Governed paths, verbatim from the spec: `tools/`, `skills/`, `agents/`, `evals/`, `commands/`, `hooks/`, `.claude-plugin/`, `.githooks/`, `.github/`, `README.md`, `CLAUDE.md`.
- Stop hook refusal text, verbatim: `BACKLOG.md carries no re-attested item this session while governed surfaces changed; update the item that owns the work and refresh its Verified field`.
- `BACKLOG.md` is written LAST on the branch (Task 10), after every hook and check exists, and it must pass the lint before the branch is reviewed.
- The version bump in `.claude-plugin/plugin.json` happens AFTER the diff debate, not in this plan.

---

### Task 0: Branch

**Files:** none.

- [ ] **Step 1: Create the feature branch from main**

```bash
git switch -c backlog-rewrite main
```

- [ ] **Step 2: Confirm the tree is clean**

Run: `git status --short`
Expected: no output.

---

### Task 1: Lint parser and structural rules 1 to 6

**Files:**
- Create: `evals/tools/backlog_lint.py`
- Create: `evals/multi-model-verify/test_backlog_lint.py`
- Create: `evals/multi-model-verify/fixtures/backlog/clean.md`

**Interfaces:**
- Produces: module `backlog_lint` with
  - `parse(text: str) -> Document` where `Document` has `.preamble: list[str]`, `.groups: list[Group]` (`Group.name: str`, `Group.raw_header: str`, `Group.ids: list[str]`, `Group.stray_lines: list[str]`), `.items: list[Item]` (`Item.id: str`, `Item.title: str`, `Item.heading: str`, `Item.fields: list[tuple[str, str]]`, `Item.body: list[str]`, `Item.line: int`).
  - `ParseError(Exception)` raised by `parse()` when the file has no `## Ranking` section or a `## ` line that is neither `## Ranking` nor a valid item heading.
  - `check(text: str, *, repo_root: Path, revision: str | None, today: datetime.date) -> list[str]` returning every failure line, empty when clean.
  - `main(argv) -> int`.
- Later tasks add `canonical_digest`, `reattested_items`, `range_check` to this module.

- [ ] **Step 1: Write the clean fixture**

Create `evals/multi-model-verify/fixtures/backlog/clean.md` with this exact content (LF line endings; the `Verified` digests are placeholders that Task 2 replaces with real ones, so Task 1's tests must not run rule 7). The `Last` group is deliberately empty: item 4 is GONE and must not be ranked.

```markdown
# BACKLOG

Headers are the source of truth. The ranking is an ordered list and
nothing else. Closing an item means editing its header and deleting
its ranking line. `evals/tools/backlog_lint.py` enforces all of it.

## Ranking

### First - breaks the review process
- 1
- 3

### Last - housekeeping

## 1. First open item
Status: OPEN
Cost: one line of cost
Pairs: 3
Verified: 2026-09-04 000000000000

Body of item one.

## 2. A closed item
Status: DONE
Closed: 0.29.0
Verified: 2026-09-04 000000000000

Shipped in one sentence.
Record: docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md

## 3. A partial item
Status: PARTIAL
Cost: the remainder costs this
Pairs: 1
Verified: 2026-09-04 000000000000

**What remains.** The mechanical half was never designed and this
paragraph carries at least twenty words so that the shape rule nine
is satisfied by the fixture itself here.

## 4. A gone item
Status: GONE
Closed: superseded
Verified: 2026-09-04 000000000000

Superseded by item 2.
Record: docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md
```

- [ ] **Step 2: Write the failing tests for parsing and rules 1 to 6**

Create `evals/multi-model-verify/test_backlog_lint.py`:

```python
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
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_backlog_lint.py -q`
Expected: FAIL at import, `backlog_lint.py` does not exist.

- [ ] **Step 4: Write the parser and rules 1 to 6**

Create `evals/tools/backlog_lint.py`:

```python
#!/usr/bin/env python3
"""backlog_lint.py - shape checker for the repository backlog.

Spec: docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md, Part 2.

Usage:
    python evals/tools/backlog_lint.py [PATH] [--revision SHA]
    python evals/tools/backlog_lint.py --range BASE..HEAD | --range HEAD
    python evals/tools/backlog_lint.py --digests [PATH]

Exit codes: 0 clean, 1 any rule failure (or a failed range test), 2 a
file that cannot be read or parsed, or a usage error. Every failure is
printed; never only the first.

The checker never rewrites the file and never judges ranking ORDER.
Rule 7 reads only the file, never git, so it behaves identically on the
working tree, in a temporary checkout, and under --revision. Rule 10 is
the one rule that consults git, to resolve a Record: commit. Rules 9 and
10 are SHAPE checks: twenty filler words satisfy 9 and any existing path
satisfies 10; the second reader named in the spec judges substance. Rule
8 is a HEURISTIC that a reworded narrative evades; it exists for the
migration and claims nothing more.

Python 3 stdlib only.
"""
import argparse
import datetime
import hashlib
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

BACKLOG_PATH = "BACKLOG.md"
OLD_PATH = "docs/superpowers/plans/2026-07-27-0150-backlog.md"
POINTER_RULE_PHRASE = "bound to the layout the citing document read"

STATUSES = ("OPEN", "PARTIAL", "DONE", "GONE")
OPEN_STATUSES = ("OPEN", "PARTIAL")
FIELD_ORDER = ("Status", "Closed", "Cost", "Pairs", "Verified")
REQUIRED_FIELDS = {
    "OPEN": ("Status", "Cost", "Pairs", "Verified"),
    "PARTIAL": ("Status", "Cost", "Pairs", "Verified"),
    "DONE": ("Status", "Closed", "Verified"),
    "GONE": ("Status", "Closed", "Verified"),
}
GOVERNED_PREFIXES = ("tools/", "skills/", "agents/", "evals/", "commands/",
                     "hooks/", ".claude-plugin/", ".githooks/", ".github/")
GOVERNED_FILES = ("README.md", "CLAUDE.md")

# Rule 8's list. Extend it here; the test pins that every phrase fails.
BANNED_NARRATIVE = (
    "renumbered",
    "moved up by one",
    "moved down by one",
    "shifted down",
    "formerly entry",
    "used to hold entry",
    "read the numbers as they stand",
)

ID_RE = r"(?:\d+|47a|47b)"
HEADING_RE = re.compile(r"^## (" + ID_RE + r")\. (.+)$")
ANY_H2_RE = re.compile(r"^## ")
GROUP_RE = re.compile(r"^###(.*)$")
RANK_RE = re.compile(r"^- (" + ID_RE + r")$")
FIELD_RE = re.compile(r"^([A-Z][a-z]+): (.*)$")
CLOSED_RE = re.compile(r"^(?:\d+\.\d+\.\d+|record|superseded)$")
VERIFIED_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}) ([0-9a-f]{12})$")
PAIRS_RE = re.compile(r"^(?:none|" + ID_RE + r"(?:, " + ID_RE + r")*)$")
WHAT_REMAINS = "**What remains.**"


class ParseError(Exception):
    """The file cannot be read as a backlog; exit 2."""


@dataclass
class Group:
    raw_header: str
    name: str
    ids: list = field(default_factory=list)
    stray_lines: list = field(default_factory=list)


@dataclass
class Item:
    id: str
    title: str
    heading: str
    line: int
    fields: list = field(default_factory=list)
    body: list = field(default_factory=list)

    def get(self, name):
        for key, value in self.fields:
            if key == name:
                return value
        return None

    @property
    def status(self):
        return self.get("Status")


@dataclass
class Document:
    preamble: list
    groups: list
    items: list

    def group_of(self, item_id):
        for group in self.groups:
            if item_id in group.ids:
                return group
        return None


def strip_trailing(line):
    """Strip ASCII space and tab only; a non-breaking space stays."""
    return line.rstrip(" \t")


def parse(text):
    lines = text.replace("\r\n", "\n").split("\n")
    preamble, groups, items = [], [], []
    section = "preamble"
    current_item = None
    current_group = None
    in_header = False
    for index, line in enumerate(lines):
        if line == "## Ranking":
            if section != "preamble":
                raise ParseError("line %d: a second Ranking section" % (index + 1))
            section = "ranking"
            continue
        heading = HEADING_RE.match(line)
        if heading:
            section = "items"
            current_item = Item(id=heading.group(1), title=heading.group(2),
                                heading=line, line=index + 1)
            items.append(current_item)
            in_header = True
            continue
        if ANY_H2_RE.match(line):
            raise ParseError("line %d: heading is neither Ranking nor an item: %r"
                             % (index + 1, line))
        if section == "preamble":
            preamble.append(line)
        elif section == "ranking":
            group = GROUP_RE.match(line)
            if group:
                current_group = Group(raw_header=line,
                                      name=group.group(1).strip(" \t"))
                groups.append(current_group)
                continue
            if line.strip(" \t") == "":
                continue
            rank = RANK_RE.match(line)
            if current_group is None:
                stray = Group(raw_header="", name="")
                groups.append(stray)
                current_group = stray
            if rank:
                current_group.ids.append(rank.group(1))
            else:
                current_group.stray_lines.append(line)
        else:
            if in_header:
                match = FIELD_RE.match(line)
                if match:
                    current_item.fields.append((match.group(1), match.group(2)))
                    continue
                in_header = False
            current_item.body.append(line)
    if section == "preamble":
        raise ParseError("no '## Ranking' section")
    return Document(preamble=preamble, groups=groups, items=items)


def canonical_digest(item, doc):
    """Task 2 fills this in."""
    raise NotImplementedError


def rule_1_header(item):
    out = []
    names = [k for k, _ in item.fields]
    status = item.get("Status")
    if names[:1] != ["Status"]:
        out.append("item %s: rule 1 (header block): fields out of order: "
                   "first field must be Status" % item.id)
        return out
    if status not in STATUSES:
        out.append("item %s: rule 1 (header block): Status must be one of %s, got %r"
                   % (item.id, "/".join(STATUSES), status))
        return out
    required = REQUIRED_FIELDS[status]
    for name in names:
        if name not in FIELD_ORDER:
            out.append("item %s: rule 1 (header block): unknown field %s"
                       % (item.id, name))
        elif name not in required:
            out.append("item %s: rule 1 (header block): field %s is not allowed for %s"
                       % (item.id, name, status))
    for name in required:
        if name not in names:
            out.append("item %s: rule 1 (header block): missing field %s"
                       % (item.id, name))
    if names.count("Status") > 1 or len(set(names)) != len(names):
        out.append("item %s: rule 1 (header block): a field is repeated" % item.id)
    expected = [n for n in FIELD_ORDER if n in names]
    if names != expected and not any("unknown field" in o for o in out):
        out.append("item %s: rule 1 (header block): fields out of order, expected %s"
                   % (item.id, ", ".join(expected)))
    closed = item.get("Closed")
    if closed is not None and not CLOSED_RE.match(closed):
        out.append("item %s: rule 1 (header block): Closed must be a version, "
                   "'record' or 'superseded', got %r" % (item.id, closed))
    cost = item.get("Cost")
    if cost is not None and cost.strip() == "":
        out.append("item %s: rule 1 (header block): Cost is empty" % item.id)
    pairs = item.get("Pairs")
    if pairs is not None and not PAIRS_RE.match(pairs):
        out.append("item %s: rule 1 (header block): Pairs must be 'none' or "
                   "comma-separated ids, got %r" % (item.id, pairs))
    return out


def pairs_of(item):
    value = item.get("Pairs")
    if value is None or value == "none" or not PAIRS_RE.match(value):
        return []
    return [p.strip() for p in value.split(",")]


def check(text, *, repo_root, revision, today, rules=None):
    """Return every failure. `rules` limits which rules run (tests only)."""
    doc = parse(text)
    active = set(rules) if rules else set(range(1, 13))
    out = []
    by_id = {}
    for item in doc.items:
        if 2 in active and item.id in by_id:
            out.append("item %s: rule 2 (unique id): heading repeated at line %d"
                       % (item.id, item.line))
        by_id.setdefault(item.id, item)
    if 1 in active:
        for item in doc.items:
            out.extend(rule_1_header(item))
    if 3 in active:
        for group in doc.groups:
            for line in group.stray_lines:
                out.append("ranking: rule 3 (ids only): unexpected line %r"
                           % line)
            if group.raw_header == "":
                out.append("ranking: rule 3 (ids only): ids before any group header")
    ranked = [i for g in doc.groups for i in g.ids]
    if 4 in active:
        open_ids = [i.id for i in doc.items if i.status in OPEN_STATUSES]
        for item_id in open_ids:
            count = ranked.count(item_id)
            if count == 0:
                out.append("item %s: rule 4 (ranked once): open item is not ranked"
                           % item_id)
            elif count > 1:
                out.append("item %s: rule 4 (ranked once): ranked %d times"
                           % (item_id, count))
        for item_id in ranked:
            if item_id not in by_id:
                out.append("item %s: rule 4 (ranked once): ranked id has no item"
                           % item_id)
    if 5 in active:
        for item_id in ranked:
            item = by_id.get(item_id)
            if item is not None and item.status in ("DONE", "GONE"):
                out.append("item %s: rule 5 (closed not ranked): %s item is ranked"
                           % (item_id, item.status))
    if 6 in active:
        for item in doc.items:
            for partner_id in pairs_of(item):
                if partner_id == item.id:
                    out.append("item %s: rule 6 (pairs symmetric): names itself"
                               % item.id)
                    continue
                partner = by_id.get(partner_id)
                if partner is None:
                    out.append("item %s: rule 6 (pairs symmetric): names %s, "
                               "which does not exist" % (item.id, partner_id))
                elif partner.status in ("DONE", "GONE"):
                    out.append("item %s: rule 6 (pairs symmetric): names %s, "
                               "which is %s" % (item.id, partner_id, partner.status))
                elif item.id not in pairs_of(partner):
                    out.append("item %s: rule 6 (pairs symmetric): names %s, "
                               "which does not name %s back"
                               % (item.id, partner_id, item.id))
    return out


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("path", nargs="?", default=None)
    parser.add_argument("--revision", default=None)
    parser.add_argument("--range", dest="range_spec", default=None)
    parser.add_argument("--digests", action="store_true")
    args = parser.parse_args(argv)
    repo_root = Path(__file__).resolve().parents[2]
    today_env = os.environ.get("PARALLAX_BACKLOG_TODAY")
    today = (datetime.date.fromisoformat(today_env) if today_env
             else datetime.date.today())
    path = Path(args.path) if args.path else repo_root / BACKLOG_PATH
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        print("file: cannot read %s: %s" % (path, exc))
        return 2
    try:
        failures = check(text, repo_root=repo_root, revision=None, today=today)
    except ParseError as exc:
        print("file: cannot parse %s: %s" % (path, exc))
        return 2
    for line in failures:
        print(line)
    if failures:
        print("%d failure(s)" % len(failures))
        return 1
    print("backlog lint: clean")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest evals/multi-model-verify/test_backlog_lint.py -q`
Expected: all PASS.

- [ ] **Step 6: Run the exact-line oracle gate and commit**

Run: `python evals/tools/check_exact_line_oracles.py`
Expected: exit 0.

```bash
git add evals/tools/backlog_lint.py evals/multi-model-verify/test_backlog_lint.py evals/multi-model-verify/fixtures/backlog/clean.md
git commit -m "add the backlog lint parser and its six structural rules"
```

---

### Task 2: Rule 7, the content digest

**Files:**
- Modify: `evals/tools/backlog_lint.py` (replace `canonical_digest`, add rule 7 to `check`, add `--digests`)
- Modify: `evals/multi-model-verify/test_backlog_lint.py`
- Modify: `evals/multi-model-verify/fixtures/backlog/clean.md` (real digests)

**Interfaces:**
- Produces: `canonical_digest(item: Item, doc: Document) -> str` returning 12 lowercase hex characters; `canonical_bytes(item, doc) -> bytes` (the hashed bytes, exposed for the fixtures).

- [ ] **Step 1: Write the failing tests**

Append to `test_backlog_lint.py`:

```python
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
        nbsp = text.replace("Body of item one.", "Body of item one.\u00a0")
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_backlog_lint.py -q -k Rule7`
Expected: FAIL with `NotImplementedError` or attribute errors.

- [ ] **Step 3: Implement the digest, rule 7 and the flag**

Replace the `canonical_digest` stub in `backlog_lint.py` with:

```python
def canonical_bytes(item, doc):
    """The byte-exact canonical content the spec's 1c defines."""
    lines = [item.heading]
    lines += ["%s: %s" % (k, v) for k, v in item.fields if k != "Verified"]
    lines += item.body
    lines = [strip_trailing(ln) for ln in lines]
    while lines and lines[-1] == "":
        lines.pop()
    group = doc.group_of(item.id)
    group_text = "" if group is None else group.raw_header[3:].strip(" \t")
    text = "\n".join(lines) + "\n" + "group:" + group_text + "\n"
    return text.encode("utf-8")


def canonical_digest(item, doc):
    return hashlib.sha256(canonical_bytes(item, doc)).hexdigest()[:12]


def rule_7_verified(item, doc, today):
    value = item.get("Verified")
    if value is None:
        return []  # rule 1 already reports the missing field
    match = VERIFIED_RE.match(value)
    if not match:
        return ["item %s: rule 7 (verified digest): Verified must be "
                "'YYYY-MM-DD <12 hex>', got %r" % (item.id, value)]
    try:
        stamp = datetime.date.fromisoformat(match.group(1))
    except ValueError:
        return ["item %s: rule 7 (verified digest): invalid date %s"
                % (item.id, match.group(1))]
    out = []
    if stamp > today:
        out.append("item %s: rule 7 (verified digest): date %s is in the future"
                   % (item.id, match.group(1)))
    expected = canonical_digest(item, doc)
    if match.group(2) != expected:
        out.append("item %s: rule 7 (verified digest): content changed since "
                   "attestation; expected digest %s" % (item.id, expected))
    return out
```

In `check`, after the rule 6 block add:

```python
    if 7 in active:
        for item in doc.items:
            out.extend(rule_7_verified(item, doc, today))
```

In `main`, after reading `text` and before `check`, add:

```python
    if args.digests:
        try:
            doc = parse(text)
        except ParseError as exc:
            print("file: cannot parse %s: %s" % (path, exc))
            return 2
        for item in doc.items:
            print("%s %s" % (item.id, canonical_digest(item, doc)))
        return 0
```

- [ ] **Step 4: Refresh the clean fixture's digests**

Run: `python evals/tools/backlog_lint.py --digests evals/multi-model-verify/fixtures/backlog/clean.md`
Copy each printed digest into the matching `Verified:` line of `clean.md`, replacing `000000000000`. Re-run the command and confirm the printed digests are unchanged (the Verified line is outside its own digest, so they must be).

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest evals/multi-model-verify/test_backlog_lint.py -q`
Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add evals/tools/backlog_lint.py evals/multi-model-verify/test_backlog_lint.py evals/multi-model-verify/fixtures/backlog/clean.md
git commit -m "add the backlog lint's content digest rule"
```

---

### Task 3: Rules 8 to 12, the revision reader and exit codes

**Files:**
- Modify: `evals/tools/backlog_lint.py`
- Modify: `evals/multi-model-verify/test_backlog_lint.py`
- Create: `evals/multi-model-verify/fixtures/backlog/pointer.md`

**Interfaces:**
- Produces: `read_at_revision(repo_root: Path, revision: str, path: str) -> str | None` (None when the path is absent at that revision); `check(...)` now accepts `pointer_text: str | None`; `main` supports `--revision SHA`.

- [ ] **Step 1: Write the pointer fixture**

Create `evals/multi-model-verify/fixtures/backlog/pointer.md` (three lines):

```markdown
This file moved to `BACKLOG.md` at the repository root; the full text was last present here at commit `0000000`.
A line citation into this path is bound to the layout the citing document read: the branch inventory beside the rewrite records the resolving commit for each citation where one exists, and a citation the inventory marks unresolved has none.
Do not resolve a citation into this path at any other commit.
```

- [ ] **Step 2: Write the failing tests**

Append to `test_backlog_lint.py`:

```python
import os
import subprocess


def pointer_text():
    return (FIXTURES / "pointer.md").read_text(encoding="utf-8")


def failures_full(text, pointer=None, repo_root=REPO, revision=None):
    return lint.check(text, repo_root=repo_root, revision=revision, today=TODAY,
                      pointer_text=pointer if pointer is not None else pointer_text())


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
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_backlog_lint.py -q -k "Rules8 or Cli"`
Expected: FAIL (unexpected keyword `pointer_text`, unknown flags).

- [ ] **Step 4: Implement rules 8 to 12, the revision reader and the flags**

Add to `backlog_lint.py`:

```python
def git_output(repo_root, *args):
    """Return stdout of a git command, or None on a non-zero exit or a
    missing git binary."""
    try:
        proc = subprocess.run(["git", *args], cwd=str(repo_root),
                              capture_output=True, text=True, encoding="utf-8")
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


def read_at_revision(repo_root, revision, path):
    return git_output(repo_root, "show", "%s:%s" % (revision, path))


def path_exists(repo_root, revision, path):
    if revision is None:
        return (Path(repo_root) / path).exists()
    return git_output(repo_root, "cat-file", "-e", "%s:%s" % (revision, path)) is not None


def commit_exists(repo_root, value):
    if not re.fullmatch(r"[0-9a-f]{7,40}", value):
        return False
    return git_output(repo_root, "cat-file", "-e", value + "^{commit}") is not None


def rule_8_narrative(doc):
    out = []
    for group in doc.groups:
        low = group.raw_header.lower()
        for phrase in BANNED_NARRATIVE:
            if phrase in low:
                out.append("ranking: rule 8 (narrative heuristic): group header "
                           "contains %r" % phrase)
    for item in doc.items:
        if item.status not in OPEN_STATUSES:
            continue
        low = "\n".join(item.body).lower()
        for phrase in BANNED_NARRATIVE:
            if phrase in low:
                out.append("item %s: rule 8 (narrative heuristic): body contains %r"
                           % (item.id, phrase))
    return out


def rule_9_remainder(item):
    if item.status != "PARTIAL":
        return []
    body = item.body
    for index, line in enumerate(body):
        if line.startswith(WHAT_REMAINS):
            words = line[len(WHAT_REMAINS):].split()
            for following in body[index + 1:]:
                if following.strip(" \t") == "":
                    break
                words += following.split()
            if len(words) < 20:
                return ["item %s: rule 9 (remainder shape): '**What remains.**' "
                        "paragraph has %d words, needs at least 20"
                        % (item.id, len(words))]
            return []
    return ["item %s: rule 9 (remainder shape): PARTIAL body has no paragraph "
            "beginning '**What remains.**'" % item.id]


def rule_10_record(item, repo_root, revision):
    if item.status not in ("DONE", "GONE"):
        return []
    records = [ln[len("Record: "):].strip() for ln in item.body
               if ln.startswith("Record: ")]
    if not records:
        return ["item %s: rule 10 (record shape): no 'Record:' line" % item.id]
    out = []
    for value in records:
        if path_exists(repo_root, revision, value) or commit_exists(repo_root, value):
            continue
        out.append("item %s: rule 10 (record shape): Record %r is neither a path "
                   "in the tree nor a commit" % (item.id, value))
    return out


def rule_11_pointer(pointer_text):
    if pointer_text is None or pointer_text.strip() == "":
        return ["pointer: rule 11 (old path): %s is missing or empty" % OLD_PATH]
    out = []
    if BACKLOG_PATH not in pointer_text:
        out.append("pointer: rule 11 (old path): does not name %s" % BACKLOG_PATH)
    if POINTER_RULE_PHRASE not in pointer_text:
        out.append("pointer: rule 11 (old path): does not carry the resolution "
                   "rule (%r)" % POINTER_RULE_PHRASE)
    return out


def rule_12_headers(doc):
    out = []
    for group in doc.groups:
        if group.raw_header == "":
            continue
        words = group.raw_header[3:].split()
        if len(words) > 8:
            out.append("ranking: rule 12 (header shape): %r has %d words, "
                       "at most 8 allowed" % (group.raw_header, len(words)))
        for line in group.stray_lines:
            out.append("ranking: rule 12 (header shape): non-header non-id line %r"
                       % line)
    return out
```

Change the `check` signature to `def check(text, *, repo_root, revision, today, rules=None, pointer_text=None):` and append after the rule 7 block:

```python
    if 8 in active:
        out.extend(rule_8_narrative(doc))
    if 9 in active:
        for item in doc.items:
            out.extend(rule_9_remainder(item))
    if 10 in active:
        for item in doc.items:
            out.extend(rule_10_record(item, repo_root, revision))
    if 11 in active:
        out.extend(rule_11_pointer(pointer_text))
    if 12 in active:
        out.extend(rule_12_headers(doc))
```

Replace `main` with:

```python
def lint_text(text, pointer_text, *, repo_root, revision, today, label):
    """Run every rule and print the result. Returns the exit code."""
    try:
        failures = check(text, repo_root=repo_root, revision=revision, today=today,
                         pointer_text=pointer_text)
    except ParseError as exc:
        print("file: cannot parse %s: %s" % (label, exc))
        return 2
    for line in failures:
        print(line)
    if failures:
        print("%d failure(s)" % len(failures))
        return 1
    print("backlog lint: clean (%s)" % label)
    return 0


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("path", nargs="?", default=None)
    parser.add_argument("--pointer", default=None,
                        help="pointer file path (default: the old backlog path)")
    parser.add_argument("--repo-root", default=None)
    parser.add_argument("--revision", default=None)
    parser.add_argument("--range", dest="range_spec", default=None)
    parser.add_argument("--digests", action="store_true")
    args = parser.parse_args(argv)
    repo_root = (Path(args.repo_root).resolve() if args.repo_root
                 else Path(__file__).resolve().parents[2])
    today_env = os.environ.get("PARALLAX_BACKLOG_TODAY")
    today = (datetime.date.fromisoformat(today_env) if today_env
             else datetime.date.today())
    if args.range_spec:
        return range_check(repo_root, args.range_spec, today)
    if args.revision:
        text = read_at_revision(repo_root, args.revision, BACKLOG_PATH)
        if text is None:
            print("file: cannot read %s at %s" % (BACKLOG_PATH, args.revision))
            return 2
        pointer = read_at_revision(repo_root, args.revision, OLD_PATH)
        label = "%s@%s" % (BACKLOG_PATH, args.revision)
    else:
        path = Path(args.path) if args.path else repo_root / BACKLOG_PATH
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as exc:
            print("file: cannot read %s: %s" % (path, exc))
            return 2
        pointer_path = Path(args.pointer) if args.pointer else repo_root / OLD_PATH
        try:
            pointer = pointer_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            pointer = None
        label = str(path)
    if args.digests:
        try:
            doc = parse(text)
        except ParseError as exc:
            print("file: cannot parse %s: %s" % (label, exc))
            return 2
        for item in doc.items:
            print("%s %s" % (item.id, canonical_digest(item, doc)))
        return 0
    return lint_text(text, pointer, repo_root=repo_root, revision=args.revision,
                     today=today, label=label)


def range_check(repo_root, range_spec, today):
    """Task 4 fills this in."""
    print("range mode not implemented")
    return 2
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest evals/multi-model-verify/test_backlog_lint.py -q`
Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add evals/tools/backlog_lint.py evals/multi-model-verify/test_backlog_lint.py evals/multi-model-verify/fixtures/backlog/pointer.md
git commit -m "add backlog lint rules 8 to 12 and the revision reader"
```

---

### Task 4: The governed-range test (`--range`) and `reattested_items`

**Files:**
- Modify: `evals/tools/backlog_lint.py`
- Modify: `evals/multi-model-verify/test_backlog_lint.py`

**Interfaces:**
- Produces:
  - `is_governed(path: str) -> bool`.
  - `reattested_items(old_text: str | None, new_text: str | None) -> list[str]`: ids of OPEN/PARTIAL items in `new_text` whose `Verified` value differs from `old_text`'s (or that are absent from `old_text`). An unparseable or absent old text counts as having no items. An absent or unparseable new text yields `[]`.
  - `range_check(repo_root, range_spec, today) -> int` printing its verdict and returning 0 or 1 (2 on a bad range). `range_spec` is `BASE..HEAD` or `HEAD` alone. Semantics: changed paths are `git diff --name-only BASE HEAD`, or for HEAD alone `git diff-tree --no-commit-id --root -r --name-only HEAD`; old backlog is `BASE:BACKLOG.md`, or for HEAD alone `HEAD^:BACKLOG.md` when HEAD has a parent, else absent. If any changed path is governed and `reattested_items` is empty, print `range <spec>: governed paths changed (<list>) and no OPEN or PARTIAL item was re-attested` and return 1. If `BACKLOG.md` is among the changed paths, additionally run the full lint at HEAD (`--revision HEAD`) and return 1 on failure. Otherwise print `range <spec>: clean` (naming the re-attested ids when governed paths changed) and return 0.
  - Later consumers: the Stop hook (Task 5), the pre-push clause (Task 7), CI (Task 8).

- [ ] **Step 1: Write the failing tests**

Append to `test_backlog_lint.py`:

```python
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
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_backlog_lint.py -q -k "Reattested or RangeMode"`
Expected: FAIL (attribute errors, exit 2 from the stub).

- [ ] **Step 3: Implement**

Add to `backlog_lint.py` and replace the `range_check` stub:

```python
def is_governed(path):
    path = path.replace("\\", "/")
    return path in GOVERNED_FILES or any(path.startswith(p) for p in GOVERNED_PREFIXES)


def _verified_map(text):
    if text is None:
        return {}
    try:
        doc = parse(text)
    except ParseError:
        return {}
    return {item.id: (item.status, item.get("Verified")) for item in doc.items}


def reattested_items(old_text, new_text):
    old = _verified_map(old_text)
    new = _verified_map(new_text)
    out = []
    for item_id, (status, verified) in new.items():
        if status not in OPEN_STATUSES:
            continue
        if item_id not in old or old[item_id][1] != verified:
            out.append(item_id)
    return out


def range_check(repo_root, range_spec, today):
    if ".." in range_spec:
        base, head = range_spec.split("..", 1)
        if not base or not head:
            print("range %s: malformed" % range_spec)
            return 2
        changed = git_output(repo_root, "diff", "--name-only", base, head)
        old_text = read_at_revision(repo_root, base, BACKLOG_PATH)
    else:
        head = range_spec
        changed = git_output(repo_root, "diff-tree", "--no-commit-id", "--root",
                             "-r", "--name-only", head)
        parent = git_output(repo_root, "rev-parse", "--verify", "--quiet", head + "^")
        old_text = (read_at_revision(repo_root, parent.strip(), BACKLOG_PATH)
                    if parent else None)
    if changed is None:
        print("range %s: git could not list the changed paths" % range_spec)
        return 2
    paths = [p for p in changed.splitlines() if p]
    governed = [p for p in paths if is_governed(p)]
    new_text = read_at_revision(repo_root, head, BACKLOG_PATH)
    code = 0
    if governed:
        ids = reattested_items(old_text, new_text)
        if not ids:
            print("range %s: governed paths changed (%s) and no OPEN or PARTIAL "
                  "item was re-attested" % (range_spec, ", ".join(governed)))
            code = 1
        else:
            print("range %s: governed paths changed (%s); re-attested: %s"
                  % (range_spec, ", ".join(governed), ", ".join(ids)))
    if BACKLOG_PATH in paths:
        if new_text is None:
            print("range %s: %s deleted at %s" % (range_spec, BACKLOG_PATH, head))
            return 1
        pointer = read_at_revision(repo_root, head, OLD_PATH)
        lint_code = lint_text(new_text, pointer, repo_root=repo_root, revision=head,
                              today=today, label="%s@%s" % (BACKLOG_PATH, head))
        if lint_code != 0:
            code = 1
    if code == 0:
        print("range %s: clean" % range_spec)
    return code
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest evals/multi-model-verify/test_backlog_lint.py -q`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add evals/tools/backlog_lint.py evals/multi-model-verify/test_backlog_lint.py
git commit -m "add the backlog lint's governed-range mode"
```

---

### Task 5: The three hook scripts

**Files:**
- Create: `tools/backlog-hooks/run-hook.ps1`
- Create: `tools/backlog-hooks/_common.py`
- Create: `tools/backlog-hooks/session_start.py`
- Create: `tools/backlog-hooks/post_tool_use.py`
- Create: `tools/backlog-hooks/stop.py`
- Create: `evals/multi-model-verify/test_backlog_hooks.py`

**Interfaces:**
- Consumes: `backlog_lint.parse`, `reattested_items`, `lint_text`, `is_governed`, `read_at_revision`, `git_output`, `BACKLOG_PATH`, `OLD_PATH`.
- Produces: a PowerShell entry point `run-hook.ps1 -Script <name.py>` that every hook command calls with `-File` (the shape `hooks/hooks.json:10` already uses), which prints `backlog hook: python not found; nothing checked` and exits 0 when no `python` is on PATH, and otherwise pipes its whole stdin to the named script and exits with the script's code; and three scripts, each reading the hook's JSON on stdin and writing per the Claude Code hook contract. The Stop refusal is printed to BOTH stdout and stderr, because the spec records stdout and the harness documentation is not in this tree to settle which stream a Stop hook's exit 2 surfaces. Baseline directory: `$PARALLAX_BACKLOG_BASELINE_DIR`, else `<tempdir>/parallax-backlog-baselines`; file `<session_id>.json` with keys `head`, `backlog_sha256`, `cwd`.
  - `session_start.py`: writes the baseline; exit 0 always (a note on stdout when git is missing, `head` recorded as `unknown`).
  - `post_tool_use.py`: if `tool_input.file_path` basename is `BACKLOG.md`, runs the lint and prints `{"hookSpecificOutput": {"hookEventName": "PostToolUse", "additionalContext": "<lint output>"}}`; exit 0 always.
  - `stop.py`: exit 0 when `stop_hook_active` is true, when the baseline is missing, when git is unavailable, or when the baseline head is unknown or no longer resolves. Otherwise the 3b logic; exit 2 with the reason on stdout.

- [ ] **Step 1: Write the failing tests**

Create `evals/multi-model-verify/test_backlog_hooks.py`:

```python
"""Hook-shape tests for tools/backlog-hooks/*.py (2026-09-04 backlog
rewrite plan, spec Part 3).

Each script is fed the documented stdin JSON inside a temporary repo and
its exit code asserted. Every script is driven THROUGH the same
PowerShell entry point .claude/settings.json names (run-hook.ps1 with
-File), under whichever host PARALLAX_PS_HOST names, so the stdin
plumbing through the host is what is measured and not only the Python.
Skips when no host is found.
"""
import hashlib
import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "evals" / "multi-model-verify" / "fixtures" / "backlog"
HOOKS = REPO / "tools" / "backlog-hooks"
POWERSHELL = (os.environ.get("PARALLAX_PS_HOST")
              or shutil.which("powershell") or shutil.which("pwsh"))
pytestmark = pytest.mark.skipif(POWERSHELL is None, reason="no PowerShell host")


def _git(repo, *args):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True,
                          encoding="utf-8", check=True).stdout.strip()


def clean_text():
    return (FIXTURES / "clean.md").read_text(encoding="utf-8")


def seed_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "config", "user.email", "t@t")
    _git(repo, "config", "user.name", "t")
    (repo / "BACKLOG.md").write_text(clean_text(), encoding="utf-8")
    old = repo / "docs" / "superpowers" / "plans" / "2026-07-27-0150-backlog.md"
    old.parent.mkdir(parents=True)
    old.write_text((FIXTURES / "pointer.md").read_text(encoding="utf-8"), encoding="utf-8")
    spec = repo / "docs" / "superpowers" / "specs"
    spec.mkdir(parents=True)
    (spec / "2026-09-04-backlog-rewrite-design.md").write_text("x\n", encoding="utf-8")
    (repo / "tools").mkdir()
    (repo / "tools" / "a.txt").write_text("a\n", encoding="utf-8")
    # Importing the scripts writes __pycache__ under governed paths; the
    # real repo ignores it at .gitignore:1 and the seed must too.
    (repo / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
    for name in ("run-hook.ps1", "_common.py", "session_start.py",
                 "post_tool_use.py", "stop.py"):
        (repo / "tools" / "backlog-hooks").mkdir(exist_ok=True)
        shutil.copy(HOOKS / name, repo / "tools" / "backlog-hooks" / name)
    (repo / "evals" / "tools").mkdir(parents=True)
    shutil.copy(REPO / "evals" / "tools" / "backlog_lint.py",
                repo / "evals" / "tools" / "backlog_lint.py")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "seed")
    return repo


HOOK_ARGS = ["-NoProfile", "-NonInteractive", "-File", "tools/backlog-hooks/run-hook.ps1",
             "-Script"]


def run_hook(repo, script, payload, baseline_dir, env_extra=None):
    """Drive the script exactly the way settings.json does: the host, then
    HOOK_ARGS, then the script name. Task 6 asserts the settings file's
    command strings are this same shape."""
    env = dict(os.environ, PARALLAX_BACKLOG_BASELINE_DIR=str(baseline_dir),
               PARALLAX_BACKLOG_TODAY="2026-09-04")
    env.update(env_extra or {})
    proc = subprocess.run([POWERSHELL, *HOOK_ARGS, script],
                          cwd=repo, input=json.dumps(payload), capture_output=True,
                          text=True, encoding="utf-8", env=env)
    return proc


def path_without_python():
    """A PATH with every directory that holds a python executable removed."""
    keep = []
    for entry in os.environ.get("PATH", "").split(os.pathsep):
        if not entry:
            continue
        if any((Path(entry) / name).exists() for name in ("python.exe", "python")):
            continue
        keep.append(entry)
    return os.pathsep.join(keep)


def start(repo, baseline_dir, session="s1"):
    proc = run_hook(repo, "session_start.py", {"session_id": session, "cwd": str(repo),
                                               "hook_event_name": "SessionStart"},
                    baseline_dir)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return proc


def stop(repo, baseline_dir, session="s1", active=False):
    return run_hook(repo, "stop.py", {"session_id": session, "cwd": str(repo),
                                      "hook_event_name": "Stop",
                                      "stop_hook_active": active}, baseline_dir)


class TestSessionStart:
    def test_writes_baseline(self, tmp_path):
        repo = seed_repo(tmp_path)
        base = tmp_path / "b"
        start(repo, base)
        data = json.loads((base / "s1.json").read_text(encoding="utf-8"))
        assert data["head"] == _git(repo, "rev-parse", "HEAD")
        digest = hashlib.sha256((repo / "BACKLOG.md").read_bytes()).hexdigest()
        assert data["backlog_sha256"] == digest

    def test_absent_backlog_recorded(self, tmp_path):
        repo = seed_repo(tmp_path)
        (repo / "BACKLOG.md").unlink()
        base = tmp_path / "b"
        start(repo, base)
        data = json.loads((base / "s1.json").read_text(encoding="utf-8"))
        assert data["backlog_sha256"] == "absent"


class TestEntryPoint:
    def test_missing_python_passes_with_note(self, tmp_path):
        repo = seed_repo(tmp_path)
        proc = run_hook(repo, "stop.py", {"session_id": "s1", "cwd": str(repo),
                                          "stop_hook_active": False},
                        tmp_path / "b", env_extra={"PATH": path_without_python()})
        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "python not found" in proc.stdout

    def test_unknown_script_name_is_refused(self, tmp_path):
        repo = seed_repo(tmp_path)
        proc = run_hook(repo, "nope.py", {}, tmp_path / "b")
        assert proc.returncode == 0 and "not found" in proc.stdout


class TestPostToolUse:
    def test_backlog_edit_reports_lint(self, tmp_path):
        repo = seed_repo(tmp_path)
        (repo / "BACKLOG.md").write_text(clean_text().replace("- 3\n", ""), encoding="utf-8")
        proc = run_hook(repo, "post_tool_use.py",
                        {"tool_name": "Edit",
                         "tool_input": {"file_path": str(repo / "BACKLOG.md")}},
                        tmp_path / "b")
        assert proc.returncode == 0
        data = json.loads(proc.stdout)
        assert "item 3: rule 4" in data["hookSpecificOutput"]["additionalContext"]

    def test_other_file_is_silent(self, tmp_path):
        repo = seed_repo(tmp_path)
        proc = run_hook(repo, "post_tool_use.py",
                        {"tool_name": "Write",
                         "tool_input": {"file_path": str(repo / "tools" / "a.txt")}},
                        tmp_path / "b")
        assert proc.returncode == 0 and proc.stdout.strip() == ""


class TestStop:
    def test_stop_hook_active_passes(self, tmp_path):
        repo = seed_repo(tmp_path)
        base = tmp_path / "b"
        start(repo, base)
        (repo / "tools" / "a.txt").write_text("b\n", encoding="utf-8")
        assert stop(repo, base, active=True).returncode == 0

    def test_missing_baseline_passes_with_note(self, tmp_path):
        repo = seed_repo(tmp_path)
        proc = stop(repo, tmp_path / "b")
        assert proc.returncode == 0 and "baseline" in proc.stdout

    def test_governed_change_without_backlog_blocks(self, tmp_path):
        repo = seed_repo(tmp_path)
        base = tmp_path / "b"
        start(repo, base)
        (repo / "tools" / "a.txt").write_text("b\n", encoding="utf-8")
        proc = stop(repo, base)
        assert proc.returncode == 2
        refusal = ("BACKLOG.md carries no re-attested item this session while governed "
                   "surfaces changed; update the item that owns the work and refresh "
                   "its Verified field")
        assert refusal in proc.stdout and refusal in proc.stderr

    def test_governed_change_committed_still_blocks(self, tmp_path):
        repo = seed_repo(tmp_path)
        base = tmp_path / "b"
        start(repo, base)
        (repo / "tools" / "a.txt").write_text("b\n", encoding="utf-8")
        _git(repo, "commit", "-q", "-am", "x")
        assert stop(repo, base).returncode == 2

    def test_new_untracked_governed_file_blocks(self, tmp_path):
        repo = seed_repo(tmp_path)
        base = tmp_path / "b"
        start(repo, base)
        (repo / "tools" / "new.txt").write_text("b\n", encoding="utf-8")
        assert stop(repo, base).returncode == 2

    def test_governed_change_with_reattest_passes(self, tmp_path):
        repo = seed_repo(tmp_path)
        base = tmp_path / "b"
        start(repo, base)
        (repo / "tools" / "a.txt").write_text("b\n", encoding="utf-8")
        text = clean_text()
        old = [ln for ln in text.splitlines() if ln.startswith("Verified: ")][0]
        text = text.replace(old, old.replace("2026-09-04", "2026-09-03"), 1)
        (repo / "BACKLOG.md").write_text(text, encoding="utf-8")
        proc = stop(repo, base)
        assert proc.returncode == 0 and "re-attested: 1" in proc.stdout

    def test_unrelated_backlog_byte_blocks(self, tmp_path):
        repo = seed_repo(tmp_path)
        base = tmp_path / "b"
        start(repo, base)
        (repo / "tools" / "a.txt").write_text("b\n", encoding="utf-8")
        (repo / "BACKLOG.md").write_text(clean_text().replace("Headers are", "HEADERS are"),
                                         encoding="utf-8")
        assert stop(repo, base).returncode == 2

    def test_docs_only_change_passes(self, tmp_path):
        repo = seed_repo(tmp_path)
        base = tmp_path / "b"
        start(repo, base)
        (repo / "docs" / "superpowers" / "specs" / "2026-09-04-backlog-rewrite-design.md"
         ).write_text("y\n", encoding="utf-8")
        assert stop(repo, base).returncode == 0

    def test_backlog_edit_failing_lint_blocks(self, tmp_path):
        repo = seed_repo(tmp_path)
        base = tmp_path / "b"
        start(repo, base)
        (repo / "BACKLOG.md").write_text(clean_text().replace("- 3\n", ""), encoding="utf-8")
        proc = stop(repo, base)
        assert proc.returncode == 2 and "item 3: rule 4" in proc.stdout

    def test_detached_head_is_handled(self, tmp_path):
        repo = seed_repo(tmp_path)
        _git(repo, "checkout", "-q", "--detach")
        base = tmp_path / "b"
        start(repo, base)
        (repo / "tools" / "a.txt").write_text("b\n", encoding="utf-8")
        assert stop(repo, base).returncode == 2

    def test_git_unavailable_passes_with_note(self, tmp_path):
        repo = seed_repo(tmp_path)
        base = tmp_path / "b"
        start(repo, base)
        (repo / "tools" / "a.txt").write_text("b\n", encoding="utf-8")
        proc = run_hook(repo, "stop.py", {"session_id": "s1", "cwd": str(repo),
                                          "stop_hook_active": False}, base,
                        env_extra={"PARALLAX_BACKLOG_GIT": "C:/no/such/git.exe"})
        assert proc.returncode == 0 and "git" in proc.stdout
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_backlog_hooks.py -q`
Expected: FAIL (scripts missing; `shutil.copy` raises).

- [ ] **Step 3: Write the entry point and the scripts**

`tools/backlog-hooks/run-hook.ps1` (the stdin read is the shape the
shipped `hooks/superpowers-review-companion.ps1:13` already uses under
`-File`):

```powershell
# run-hook.ps1 - entry point for the backlog hooks in .claude/settings.json.
# Passes the hook's stdin JSON to the named Python script and exits with
# its code. A missing python prints a note and exits 0, because a hook
# must never wedge a session (spec, Error handling); the pre-push hook is
# the one place a missing tool refuses, and it is not this file.
param([Parameter(Mandatory = $true)][string]$Script)
$ErrorActionPreference = 'Continue'
$target = Join-Path $PSScriptRoot $Script
if (-not (Test-Path -LiteralPath $target)) {
    Write-Output "backlog hook: script $Script not found; nothing checked"
    exit 0
}
$python = Get-Command python -ErrorAction SilentlyContinue
if (-not $python) {
    Write-Output "backlog hook: python not found; nothing checked"
    exit 0
}
$payload = [Console]::In.ReadToEnd()
$prior = $OutputEncoding
try {
    $OutputEncoding = New-Object System.Text.UTF8Encoding($false)
    $payload | & $python.Source $target
    $code = $LASTEXITCODE
} finally {
    $OutputEncoding = $prior
}
exit $code
```

`tools/backlog-hooks/_common.py`:

```python
"""Shared pieces of the three backlog hook scripts. Stdlib only.

Every script reads the hook's JSON from stdin and prints for the harness.
The baseline directory is PARALLAX_BACKLOG_BASELINE_DIR when set, else
<tempdir>/parallax-backlog-baselines; a file per session_id.
PARALLAX_BACKLOG_GIT overrides the git binary (tests use it to simulate a
missing git).
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKLOG = REPO_ROOT / "BACKLOG.md"


def load_lint():
    path = REPO_ROOT / "evals" / "tools" / "backlog_lint.py"
    spec = importlib.util.spec_from_file_location("backlog_lint", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def read_payload():
    raw = sys.stdin.read()
    try:
        return json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        return {}


def baseline_dir():
    override = os.environ.get("PARALLAX_BACKLOG_BASELINE_DIR")
    base = Path(override) if override else Path(tempfile.gettempdir()) / "parallax-backlog-baselines"
    base.mkdir(parents=True, exist_ok=True)
    return base


def baseline_path(session_id):
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in (session_id or "unknown"))
    return baseline_dir() / (safe + ".json")


def git(*args):
    binary = os.environ.get("PARALLAX_BACKLOG_GIT", "git")
    try:
        proc = subprocess.run([binary, *args], cwd=str(REPO_ROOT), capture_output=True,
                              text=True, encoding="utf-8")
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


def backlog_sha256():
    if not BACKLOG.exists():
        return "absent"
    return hashlib.sha256(BACKLOG.read_bytes()).hexdigest()


def lint_working_tree(lint):
    """Run the lint on the working tree; return (exit_code, output_text)."""
    import io
    import contextlib
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = lint.main(["--repo-root", str(REPO_ROOT)])
    return code, buffer.getvalue()
```

`tools/backlog-hooks/session_start.py`:

```python
"""SessionStart hook: record this session's baseline (spec 3a0)."""
import json
import sys

from _common import backlog_sha256, baseline_path, git, read_payload


def main():
    payload = read_payload()
    head = git("rev-parse", "HEAD")
    if head is None:
        head = "unknown"
        print("backlog baseline: git unavailable, head recorded as unknown")
    data = {"head": head.strip(), "backlog_sha256": backlog_sha256(),
            "cwd": payload.get("cwd", "")}
    baseline_path(payload.get("session_id")).write_text(json.dumps(data), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

`tools/backlog-hooks/post_tool_use.py`:

```python
"""PostToolUse hook on Edit and Write: lint BACKLOG.md after a direct edit
(spec 3a). Reported, never blocked: the edit has already happened."""
import json
import os
import sys

from _common import load_lint, lint_working_tree, read_payload


def main():
    payload = read_payload()
    path = (payload.get("tool_input") or {}).get("file_path", "")
    if os.path.basename(path) != "BACKLOG.md":
        return 0
    lint = load_lint()
    code, output = lint_working_tree(lint)
    message = "backlog lint after edit (exit %d):\n%s" % (code, output)
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                             "additionalContext": message}}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

`tools/backlog-hooks/stop.py`:

```python
"""Stop hook: a one-shot reminder that governed changes need a re-attested
backlog item (spec 3b). Blocks by exit 2 with the reason on stdout. Honours
stop_hook_active so it cannot loop; passes with a note when the baseline,
git, or the baseline commit is missing so a broken tool cannot wedge a
session."""
import json
import sys

from _common import (BACKLOG, backlog_sha256, baseline_path, git, lint_working_tree,
                     load_lint, read_payload)

REFUSAL = ("BACKLOG.md carries no re-attested item this session while governed "
           "surfaces changed; update the item that owns the work and refresh its "
           "Verified field")


def main():
    payload = read_payload()
    if payload.get("stop_hook_active"):
        return 0
    path = baseline_path(payload.get("session_id"))
    if not path.exists():
        print("backlog stop check: no baseline for this session (started before the "
              "hook existed); nothing checked")
        return 0
    baseline = json.loads(path.read_text(encoding="utf-8"))
    if git("rev-parse", "--verify", "--quiet", "HEAD") is None:
        print("backlog stop check: git unavailable; nothing checked")
        return 0
    head = baseline.get("head", "unknown")
    if head == "unknown" or git("cat-file", "-e", head + "^{commit}") is None:
        print("backlog stop check: baseline commit %s not found; nothing checked" % head)
        return 0
    lint = load_lint()
    tracked = git("diff", "--name-only", head) or ""
    untracked = git("ls-files", "--others", "--exclude-standard") or ""
    changed = [p for p in (tracked + untracked).splitlines() if p]
    governed = sorted({p for p in changed if lint.is_governed(p)})
    backlog_changed = backlog_sha256() != baseline.get("backlog_sha256")
    if governed:
        old_text = git("show", "%s:%s" % (head, lint.BACKLOG_PATH))
        new_text = BACKLOG.read_text(encoding="utf-8") if BACKLOG.exists() else None
        ids = lint.reattested_items(old_text, new_text)
        if not ids:
            detail = "governed paths changed: " + ", ".join(governed)
            print(REFUSAL)
            print(detail)
            print(REFUSAL, file=sys.stderr)
            print(detail, file=sys.stderr)
            return 2
        print("backlog stop check: governed paths changed; re-attested: " + ", ".join(ids))
    if backlog_changed:
        code, output = lint_working_tree(lint)
        if code != 0:
            print(output)
            print(output, file=sys.stderr)
            return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the tests under the default host, then the other one**

Run: `python -m pytest evals/multi-model-verify/test_backlog_hooks.py -q`
Expected: all PASS.

Run: `$env:PARALLAX_PS_HOST = "pwsh"; python -m pytest evals/multi-model-verify/test_backlog_hooks.py -q; Remove-Item Env:PARALLAX_PS_HOST`
Expected: all PASS. Then the same with `powershell` if the first run used pwsh. If the entry point does not deliver stdin on one host, the failing host names the defect; do not weaken the test.

- [ ] **Step 5: Commit**

```bash
git add tools/backlog-hooks evals/multi-model-verify/test_backlog_hooks.py
git commit -m "add the backlog session, edit and stop hook scripts"
```

---

### Task 6: Wire the hooks in a tracked project settings file

**Files:**
- Create: `.claude/settings.json`
- Modify: `.gitignore:3`
- Modify: `evals/multi-model-verify/test_backlog_hooks.py`

- [ ] **Step 1: Write the failing test**

Append to `test_backlog_hooks.py`:

```python
class TestSettingsWiring:
    def test_settings_file_is_tracked(self):
        tracked = _git(REPO, "ls-files", ".claude/settings.json")
        assert tracked == ".claude/settings.json"

    def test_settings_wire_the_three_scripts(self):
        data = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
        hooks = data["hooks"]
        commands = {event: [h["command"] for group in hooks[event] for h in group["hooks"]]
                    for event in ("SessionStart", "PostToolUse", "Stop")}
        assert any("session_start.py" in c for c in commands["SessionStart"])
        assert any("post_tool_use.py" in c for c in commands["PostToolUse"])
        assert any("stop.py" in c for c in commands["Stop"])
        assert hooks["PostToolUse"][0]["matcher"] == "Edit|Write"
        prefix = "pwsh " + " ".join(HOOK_ARGS) + " "
        for event in commands:
            for command in commands[event]:
                assert command.startswith(prefix), command

    def test_settings_command_shape_matches_the_tests(self):
        """The command string is the host plus HOOK_ARGS plus the script,
        which is exactly the argv run_hook builds, so the hook tests
        exercise what ships."""
        data = json.loads((REPO / ".claude" / "settings.json").read_text(encoding="utf-8"))
        command = data["hooks"]["Stop"][0]["hooks"][0]["command"]
        assert command.split(" ") == ["pwsh", *HOOK_ARGS, "stop.py"]
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest evals/multi-model-verify/test_backlog_hooks.py -q -k Settings`
Expected: FAIL (file not tracked).

- [ ] **Step 3: Change `.gitignore` and create the settings file**

Edit `.gitignore` line 3 from `.claude/` to:

```
.claude/*
!.claude/settings.json
```

Create `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "pwsh -NoProfile -NonInteractive -File tools/backlog-hooks/run-hook.ps1 -Script session_start.py",
            "timeout": 15
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "pwsh -NoProfile -NonInteractive -File tools/backlog-hooks/run-hook.ps1 -Script post_tool_use.py",
            "timeout": 30
          }
        ]
      }
    ],
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "pwsh -NoProfile -NonInteractive -File tools/backlog-hooks/run-hook.ps1 -Script stop.py",
            "timeout": 30
          }
        ]
      }
    ]
  }
}
```

- [ ] **Step 4: Stage and verify the file is tracked**

```bash
git add .gitignore .claude/settings.json
git ls-files .claude/settings.json
```
Expected: prints `.claude/settings.json`. If `git add` refuses because of the ignore rule, the `.gitignore` edit is wrong; fix it before continuing.

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest evals/multi-model-verify/test_backlog_hooks.py -q`
Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git commit -m "wire the backlog hooks in tracked project settings"
```

---

### Task 7: The pre-push clause

**Files:**
- Modify: `.githooks/pre-push`
- Create: `evals/multi-model-verify/test_backlog_prepush.py`

**Interfaces:**
- Consumes: `python evals/tools/backlog_lint.py --range BASE..HEAD` and `--range HEAD`.
- Produces: a blocking clause in the hook that runs before the attestation clause.

- [ ] **Step 1: Write the failing tests**

Create `evals/multi-model-verify/test_backlog_prepush.py`:

```python
"""Disposable-clone tests for the pre-push backlog clause (spec 3c).

A bare stub remote and a clone with core.hooksPath pointing at the
working-tree .githooks/pre-push, so uncommitted hook edits are what gets
tested. Each scenario pushes main with a merge, a squash or a
fast-forward, with and without a re-attested item beside a governed
change. The hook is bash under git; git for Windows ships it.
"""
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "evals" / "multi-model-verify" / "fixtures" / "backlog"
POWERSHELL = (os.environ.get("PARALLAX_PS_HOST")
              or shutil.which("powershell") or shutil.which("pwsh"))


def _git(repo, *args, check=True):
    return subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True,
                          encoding="utf-8", check=check)


def out(repo, *args):
    return _git(repo, *args).stdout.strip()


def clean_text():
    return (FIXTURES / "clean.md").read_text(encoding="utf-8")


def refreshed(text, item_id="1"):
    lines = text.splitlines(keepends=True)
    seen = False
    for index, line in enumerate(lines):
        if line.startswith("## %s. " % item_id):
            seen = True
        if seen and line.startswith("Verified: 2026-09-04 "):
            lines[index] = line.replace("2026-09-04", "2026-09-03", 1)
            break
    return "".join(lines)


@pytest.fixture
def clone(tmp_path):
    remote = tmp_path / "remote.git"
    _git(tmp_path, "init", "-q", "--bare", "-b", "main", str(remote))
    work = tmp_path / "work"
    work.mkdir()
    _git(work, "init", "-q", "-b", "main")
    _git(work, "config", "user.email", "t@t")
    _git(work, "config", "user.name", "t")
    (work / "BACKLOG.md").write_text(clean_text(), encoding="utf-8")
    old = work / "docs" / "superpowers" / "plans" / "2026-07-27-0150-backlog.md"
    old.parent.mkdir(parents=True)
    old.write_text((FIXTURES / "pointer.md").read_text(encoding="utf-8"), encoding="utf-8")
    spec = work / "docs" / "superpowers" / "specs"
    spec.mkdir(parents=True)
    (spec / "2026-09-04-backlog-rewrite-design.md").write_text("x\n", encoding="utf-8")
    (work / "tools").mkdir()
    (work / "tools" / "a.txt").write_text("a\n", encoding="utf-8")
    (work / "README.md").write_text("r\n", encoding="utf-8")
    (work / "CLAUDE.md").write_text("c\n", encoding="utf-8")
    (work / "evals" / "tools").mkdir(parents=True)
    shutil.copy(REPO / "evals" / "tools" / "backlog_lint.py",
                work / "evals" / "tools" / "backlog_lint.py")
    hooks = work / ".githooks"
    hooks.mkdir()
    shutil.copy(REPO / ".githooks" / "pre-push", hooks / "pre-push")
    _git(work, "add", "-A")
    _git(work, "commit", "-q", "-m", "seed")
    _git(work, "remote", "add", "origin", str(remote))
    _git(work, "config", "core.hooksPath", ".githooks")
    seed_push = push(work)
    assert seed_push.returncode == 0, seed_push.stderr
    return work


def push(work):
    """Every push, the seed included, pins today so the fixture's dates
    never read as future on a machine whose clock is behind."""
    env = dict(os.environ, PARALLAX_BACKLOG_TODAY="2026-09-04")
    return subprocess.run(["git", "push", "origin", "main"], cwd=work, capture_output=True,
                          text=True, encoding="utf-8", env=env)


def feature(work, files, message="feat"):
    _git(work, "switch", "-q", "-c", "feat")
    for path, text in files.items():
        target = work / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    _git(work, "add", "-A")
    _git(work, "commit", "-q", "-m", message)
    _git(work, "switch", "-q", "main")


def land(work, how):
    if how == "merge":
        _git(work, "merge", "-q", "--no-ff", "-m", "merge", "feat")
    elif how == "squash":
        _git(work, "merge", "-q", "--squash", "feat")
        _git(work, "commit", "-q", "-m", "squash")
    else:
        _git(work, "merge", "-q", "--ff-only", "feat")


@pytest.mark.parametrize("how", ["merge", "squash", "ff"])
def test_governed_change_without_reattest_is_refused(clone, how):
    feature(clone, {"tools/a.txt": "b\n"})
    land(clone, how)
    proc = push(clone)
    assert proc.returncode != 0
    assert "no OPEN or PARTIAL item was re-attested" in proc.stderr + proc.stdout


@pytest.mark.parametrize("how", ["merge", "squash", "ff"])
def test_governed_change_with_reattest_passes(clone, how):
    feature(clone, {"tools/a.txt": "b\n", "BACKLOG.md": refreshed(clean_text())})
    land(clone, how)
    proc = push(clone)
    assert proc.returncode == 0, proc.stderr


def test_docs_only_push_passes(clone):
    feature(clone, {"docs/note.md": "n\n"})
    land(clone, "ff")
    assert push(clone).returncode == 0


@pytest.mark.parametrize("path", ["README.md", "CLAUDE.md"])
def test_readme_or_claude_alone_is_refused(clone, path):
    feature(clone, {path: "changed\n"})
    land(clone, "ff")
    assert push(clone).returncode != 0


def test_unrelated_backlog_byte_is_refused(clone):
    feature(clone, {"tools/a.txt": "b\n",
                    "BACKLOG.md": clean_text().replace("Headers are", "HEADERS are")})
    land(clone, "ff")
    assert push(clone).returncode != 0


def test_backlog_failing_lint_is_refused(clone):
    feature(clone, {"BACKLOG.md": clean_text().replace("- 3\n", "")})
    land(clone, "ff")
    proc = push(clone)
    assert proc.returncode != 0 and "item 3: rule 4" in proc.stderr + proc.stdout


def test_range_mode_driven_directly_agrees(clone):
    feature(clone, {"tools/a.txt": "b\n"})
    land(clone, "ff")
    base = out(clone, "rev-parse", "origin/main")
    head = out(clone, "rev-parse", "HEAD")
    proc = subprocess.run(["python", "evals/tools/backlog_lint.py", "--range",
                           "%s..%s" % (base, head)], cwd=clone, capture_output=True,
                          text=True, encoding="utf-8",
                          env=dict(os.environ, PARALLAX_BACKLOG_TODAY="2026-09-04"))
    assert proc.returncode == 1


def test_missing_python_refuses(clone, tmp_path):
    feature(clone, {"docs/note.md": "n\n"})
    land(clone, "ff")
    env = dict(os.environ, PARALLAX_BACKLOG_PYTHON="C:/no/such/python.exe")
    proc = subprocess.run(["git", "push", "origin", "main"], cwd=clone, capture_output=True,
                          text=True, encoding="utf-8", env=env)
    assert proc.returncode != 0 and "python" in (proc.stderr + proc.stdout).lower()


def test_non_main_push_is_not_checked(clone):
    feature(clone, {"tools/a.txt": "b\n"})
    proc = subprocess.run(["git", "push", "-q", "origin", "feat"], cwd=clone,
                          capture_output=True, text=True, encoding="utf-8")
    assert proc.returncode == 0, proc.stderr
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_backlog_prepush.py -q`
Expected: the refusal tests FAIL (the push succeeds today).

- [ ] **Step 3: Rewrite the hook**

Replace `.githooks/pre-push` with:

```bash
#!/usr/bin/env bash
# parallax pre-push - two clauses for pushes to main.
#
# CLAUSE 1 (BLOCKING): the backlog governed-range check. For a push to
# refs/heads/main it runs `evals/tools/backlog_lint.py --range remote..local`
# (or `--range local` for a new remote branch). That mode refuses when the
# range changes a governed path - tools/, skills/, agents/, evals/,
# commands/, hooks/, .claude-plugin/, .githooks/, .github/, README.md,
# CLAUDE.md - and no OPEN or PARTIAL backlog item's Verified line changed
# in the same range, and it lints BACKLOG.md at the pushed head whenever
# the range touches it. README.md and CLAUDE.md ARE governed on purpose:
# every session reads them first. Merge topology is not consulted: a
# squash, a fast-forward and a merge commit are judged by the paths they
# carry. Pushes touching no governed path stay friction-free. A missing
# python REFUSES, because a push is the one place a missing tool must not
# read as a pass. CI runs the same mode (skill-evals job), so a clone
# without this hook is detected on arrival.
#
# CLAUSE 2 (non-blocking): the multi-model-verify attestation check for
# the pushed head (SHA-bound review record - tools/verify-attestation.ps1
# documents the fast-forward and merge matching rules). It warns and never
# blocks; the warning is the mechanism that proves the lane out before
# anyone considers making it blocking.
#
# Register once per clone:  git config core.hooksPath .githooks
set -uo pipefail

repo_root="$(git rev-parse --show-toplevel)"
verifier="$repo_root/tools/verify-attestation.ps1"
lint="$repo_root/evals/tools/backlog_lint.py"
python_bin="${PARALLAX_BACKLOG_PYTHON:-python}"

while read -r _lref _lsha _rref _rsha; do
    [ "$_rref" = "refs/heads/main" ] || continue
    # skip deletions (local sha is all zeros)
    case "$_lsha" in *[!0]*) ;; *) continue ;; esac

    # ---- clause 1: backlog governed-range check (blocking) ----
    if ! command -v "$python_bin" >/dev/null 2>&1; then
        echo "[pre-push] REFUSED: python ($python_bin) not found; the backlog range check cannot run" >&2
        exit 1
    fi
    case "$_rsha" in
        *[!0]*) range="$_rsha..$_lsha" ;;
        *) range="$_lsha" ;;
    esac
    if range_out="$("$python_bin" "$lint" --range "$range" 2>&1)"; then
        echo "[pre-push] backlog: $range_out"
    else
        echo "[pre-push] REFUSED by the backlog range check:" >&2
        echo "$range_out" >&2
        exit 1
    fi

    # ---- clause 2: attestation (non-blocking) ----
    [ -f "$verifier" ] || continue
    # powershell.exe needs Windows paths; cygpath ships with git-bash.
    win_verifier="$(cygpath -w "$verifier" 2>/dev/null || echo "$verifier")"
    win_root="$(cygpath -w "$repo_root" 2>/dev/null || echo "$repo_root")"
    if out="$(powershell.exe -NoProfile -ExecutionPolicy Bypass -File "$win_verifier" -RepoRoot "$win_root" -LocalSha "$_lsha" 2>&1)"; then
        echo "[pre-push] attestation: $out"
    else
        echo "[pre-push] note (non-blocking): pushing main @ $_lsha without a matching multi-model-verify attestation - $out (run mode diff + write-attestation.ps1, or ignore for a trivial change)" >&2
    fi
done
exit 0
```

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python -m pytest evals/multi-model-verify/test_backlog_prepush.py -q`
Expected: all PASS. If `python` on the git-bash PATH is the Microsoft Store stub, the missing-python test passes but the others fail with a launcher error; fix the PATH for the test run rather than the hook.

- [ ] **Step 5: Commit**

```bash
git add .githooks/pre-push evals/multi-model-verify/test_backlog_prepush.py
git commit -m "refuse a main push that changes governed paths without a re-attested backlog item"
```

---

### Task 8: Gate and CI wiring

**Files:**
- Modify: `.github/workflows/skill-evals.yml`
- Modify: `CLAUDE.md` (verification list, lines 11 to 18)
- Modify: `evals/multi-model-verify/test_backlog_lint.py`

- [ ] **Step 1: Write the failing test**

Append to `test_backlog_lint.py`:

```python
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
```

- [ ] **Step 2: Run the test to verify it fails**

Run: `python -m pytest evals/multi-model-verify/test_backlog_lint.py -q -k Wiring`
Expected: FAIL.

- [ ] **Step 3: Edit the workflow**

In the `skill-evals` job, change the checkout step to fetch history and add two tiers after Tier 2b:

```yaml
      - name: Checkout
        uses: actions/checkout@v7
        with:
          fetch-depth: 0
```

```yaml
      - name: Tier 2c - backlog lint
        run: python evals/tools/backlog_lint.py

      # The same governed-range and re-attestation test the pre-push hook
      # runs, from git objects, because a local hook can be uninstalled.
      # On a push this runs AFTER the ref moved (detection); on a pull
      # request it runs before the merge but only prevents it when the
      # job is a required check, which is a repository ruleset outside
      # this tree (spec 3d).
      - name: Tier 2d - backlog governed-range check
        if: github.event_name == 'pull_request' || github.ref == 'refs/heads/main'
        env:
          BASE_SHA: ${{ github.event_name == 'pull_request' && github.event.pull_request.base.sha || github.event.before }}
        run: |
          if [ -z "$BASE_SHA" ] || [ "$BASE_SHA" = "0000000000000000000000000000000000000000" ]; then
            python evals/tools/backlog_lint.py --range "$GITHUB_SHA"
          else
            python evals/tools/backlog_lint.py --range "$BASE_SHA..$GITHUB_SHA"
          fi
```

In the `powershell-hosts` job, add these two lines to BOTH module lists (before the `-q`):

```yaml
          evals/multi-model-verify/test_backlog_hooks.py
          evals/multi-model-verify/test_backlog_prepush.py
```

The job's comment says "The hook tests are deliberately absent - hooks.json invokes the hook as `pwsh`, so another host would not match how it runs." That sentence is about the PLUGIN's hooks and stays true of them. Append after it:

```yaml
      # The backlog hooks in .claude/settings.json are different: their
      # entry point tools/backlog-hooks/run-hook.ps1 is host-neutral and
      # the tests drive it under whichever host PARALLAX_PS_HOST names,
      # so test_backlog_hooks.py and test_backlog_prepush.py ARE listed.
```

- [ ] **Step 4: Edit CLAUDE.md**

In the `## Verification` list, after the `python -m pytest evals -q` line, add:

```markdown
- `python evals/tools/backlog_lint.py`
```

and change `CI runs all five on every push` to `CI runs all six on every push`, and `tiers 1, 1b, 1c, 2 and 2b` to `tiers 1, 1b, 1c, 2, 2b and 2c; tier 2d runs the same governed-range test as the pre-push hook on main pushes and pull requests`.

- [ ] **Step 5: Run the workflow path checker and the test**

Run: `python evals/tools/check_workflow_paths.py`
Expected: exit 0 (the new modules exist).

Run: `python -m pytest evals/multi-model-verify/test_backlog_lint.py -q`
Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add .github/workflows/skill-evals.yml CLAUDE.md evals/multi-model-verify/test_backlog_lint.py
git commit -m "run the backlog lint and range check in the gate and in ci"
```

---

### Task 9: Citation inventory, frozen-plan rewrite, and the untruncated grep

**Files:**
- Create: `docs/superpowers/plans/rounds/2026-09-04-backlog-rewrite/citation-inventory.md`
- Create: `docs/superpowers/plans/rounds/2026-09-04-backlog-rewrite/citation-grep.txt`
- Modify: `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:78` and `:975`

- [ ] **Step 1: Run the untruncated grep and retain it**

```bash
mkdir -p docs/superpowers/plans/rounds/2026-09-04-backlog-rewrite
git ls-files | xargs grep -nH '2026-07-27-0150-backlog\.md' > docs/superpowers/plans/rounds/2026-09-04-backlog-rewrite/citation-grep.txt
wc -l docs/superpowers/plans/rounds/2026-09-04-backlog-rewrite/citation-grep.txt
```

No `head`, no `tail`, and `-H` so a one-file final xargs batch still prints its name. The pattern is the bare path, not `path:[0-9]`, because the probe plan's line 158 cites lines of the old file in a second shape (`the path — item 10's heading at `:577` and its status at `:11-14``) that a `:[0-9]` pattern never sees; a sweep must report the shapes it searched for. Every line is retained. Read the file and classify every hit outside `docs/superpowers/plans/rounds/`:

- this plan (`docs/superpowers/plans/2026-09-04-backlog-rewrite.md`), the spec, `CLAUDE.md` and memory or handoff files name the path without a line citation and are not citations;
- `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md` lines 78 and 975 carry `:41`, and line 158 carries `:577` and `:11-14`; lines 288, 856 and 892 name the path with no line and are not citations.

If any OTHER tracked document carries a line citation, in either shape, list it in the inventory and stop to report it, because the spec's inventory (two citations in one frozen plan) would be wrong by more than the third shape already found here.

- [ ] **Step 2: Find the resolving commit for the probe plan's line-41 citation**

```bash
for sha in $(git log --format=%h -- docs/superpowers/plans/2026-07-27-0150-backlog.md); do
  line="$(git show "$sha:docs/superpowers/plans/2026-07-27-0150-backlog.md" | sed -n 41p)"
  case "$line" in *27*) echo "$sha: $line" ;; esac
done
```

Pick the NEWEST commit whose line 41 states the 27-directory measurement (the text names `~/.agents/skills/` and `27`). Record the sha as `<sha41>`.

- [ ] **Step 3: Rewrite the frozen plan's line citations**

In `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md`, replace both occurrences of the exact string `docs/superpowers/plans/2026-07-27-0150-backlog.md:41` with `docs/superpowers/plans/2026-07-27-0150-backlog.md@<sha41>:41`.

Line 158 cites `:577` and `:11-14` of the old file for item 10's heading and its status block. Find its resolving commit the same way as Step 2, checking that line 577 at the candidate is item 10's heading and lines 11 to 14 are the status block:

```bash
for sha in $(git log --format=%h -- docs/superpowers/plans/2026-07-27-0150-backlog.md); do
  h="$(git show "$sha:docs/superpowers/plans/2026-07-27-0150-backlog.md" | sed -n 577p)"
  case "$h" in *"10."*|*"Item 10"*) echo "$sha: $h" ;; esac
done
```

Record the newest matching commit as `<sha158>` and rewrite line 158 so the path reads `docs/superpowers/plans/2026-07-27-0150-backlog.md@<sha158>` with the `:577` and `:11-14` citations kept as written after it. If no commit matches, leave line 158 unchanged and record it as unresolved in the inventory. Nothing else in that file changes; lines 288, 856 and 892 name the path without a line and stay as they are.

Run: `grep -n '0150-backlog\.md' docs/superpowers/plans/2026-08-03-home-skills-root-probe.md`
Expected: six lines; 78 and 975 carry `@<sha41>:41`, 158 carries `@<sha158>` or is recorded unresolved, and 288, 856 and 892 are unchanged.

- [ ] **Step 4: Build the inventory of raw-record citations**

Write `docs/superpowers/plans/rounds/2026-09-04-backlog-rewrite/citation-inventory.md` with this header and one row per line of `citation-grep.txt` that lies under `docs/superpowers/plans/rounds/` AND carries a line citation in either shape (a bare path mention with no line number gets no row), plus a closing paragraph recording the frozen plan's three rewritten citations and their resolving commits from Steps 2 and 3:

```markdown
# Citations into the old backlog path, inventoried 2026-09-04

Source: `citation-grep.txt` beside this file, the full untruncated output of
`git ls-files | xargs grep -nH '2026-07-27-0150-backlog\.md'` at the
commit that adds this file. Two citation shapes were searched for: the
path followed by `:N` or `:N-M`, and the path named on a line that cites
`:N` later in the same line. A bare mention of the path is not a citation. Raw round records are never edited, so nothing
here is applied to them. A row records the commit at which the cited line
carries the text the citation describes, or `unresolved` when no candidate
does. Nothing is guessed.

Candidates tried per row, in order: the subject revision the record names
in its filename or text; the record's own first commit (`git log
--diff-filter=A --format=%h -- <file>`); that commit's first parent.

| citing file | cited line(s) | candidate revision(s) | text at the cited line matches? | resolving commit |
|---|---|---|---|---|
```

For each row, run `git show <candidate>:docs/superpowers/plans/2026-07-27-0150-backlog.md | sed -n '<line>p'` for each candidate and compare with what the citing record says the line holds; write `yes <sha>` or `unresolved`. Include the row for `rounds/2026-07-28-0160-backlog/fable-review-c6b7c85-efe4fa0.md` lines 160 to 162 and expect it to read `unresolved`, as the spec records.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/plans/rounds/2026-09-04-backlog-rewrite docs/superpowers/plans/2026-08-03-home-skills-root-probe.md
git commit -m "inventory every citation into the old backlog path and bind the frozen plan's two"
```

---

### Task 10: Write `BACKLOG.md` and the pointer file

**Files:**
- Create: `BACKLOG.md`
- Modify: `docs/superpowers/plans/2026-07-27-0150-backlog.md` (becomes the three-line pointer)

**Interfaces:**
- Consumes: the lint (`python evals/tools/backlog_lint.py`, `--digests`).
- Produces: the file every later session maintains.

This task is READING work. Every item is condensed or cleaned by reading its own text at the old path; nothing is done by pattern. Read the old file in full before writing (`docs/superpowers/plans/2026-07-27-0150-backlog.md` at the branch's current HEAD, 5,905 lines).

- [ ] **Step 1: Record the last full-text commit**

```bash
git rev-parse --short HEAD
```
Record it as `<lastfull>`; the pointer file names it. It is the commit BEFORE this task's commit, so it must be the current HEAD, not the commit this task makes.

- [ ] **Step 2: Write the preamble and ranking**

Start `BACKLOG.md` with:

```markdown
# BACKLOG

Headers are the source of truth: each item's `Status`, `Closed`, `Cost`,
`Pairs` and `Verified` lines are the only status view there is. The
ranking below is an ordered list of open item ids and nothing else:
groups are labels, not tiers, and the order within and across groups is
the build order. The case for an item's place is its own `Cost` line.
Closing an item means editing its header and deleting its ranking line;
nothing else moves. Refresh an item's `Verified` field after reading it,
with the digest the lint prints. `evals/tools/backlog_lint.py` enforces
all of it, in the gate, at push, in CI, and from the hooks in
`.claude/settings.json`. The full previous text of every closed item is
in git history at `docs/superpowers/plans/2026-07-27-0150-backlog.md`.

## Ranking

### First - breaks the repo's own review process
- 75
- 49
- 59
- 67
- 78
- 51
- 43
- 31
- 58

### Second - taxes every cycle
- 44
- 69
- 77

### Third - changes to the workflow itself
- 46
- 47a
- 45
- 55
- 70

### Fourth - measurements missing or made by proxy
- 73
- 41
- 39
- 63
- 68
- 81
- 82
- 36
- 38
- 76
- 40
- 47b
- 66

### Fifth - correctness not currently biting
- 53
- 80
- 29
- 26
- 34
- 35
- 28
- 27
- 37

### Last - housekeeping and open questions
- 54
- 65
- 64
- 15
- 12
- 60
- 61
- 11
- 71
- 72
- 79
```

Item 11 (agy lane drift protection, PARTIAL since 0.24.0) was never ranked in the old file and the spec is silent on it; rule 4 requires a position, so it takes the Last group beside 71 and 72 with a Cost line in their form: `uncosted: the remainder was never designed and the agy lane's future depends on what item 45 decides`. That placement is a decision this plan makes, recorded here so the second reader can see it.

Ids 80, 81 and 82 are the three new items from spec 1d: 80 classifier refusals have no failure class in `fallbacks.md`; 81 what the `fable` alias resolves to and what effort a seat runs at are unmeasured; 82 resume after a killed round is unmeasured.

- [ ] **Step 3: Write the item headers from this table**

Every item from the old file appears, in ascending id order (`47a` and `47b` in place of 47). Header values:

| Status | Ids |
|---|---|
| DONE | 1 (Closed 0.15.1), 2, 3, 5, 6 (0.16.0), 4, 10 (0.17.0), 7 (0.24.0), 8, 13 (0.18.0), 9, 18, 19, 30 (0.23.0), 14 (record; Record: the merge commit its text names), 17 (0.20.0), 20, 21, 22, 23 (0.21.0), 24, 25 (0.22.0), 32, 33 (0.28.0), 42 (0.25.0), 48 (record; Record: `docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md`), 50 (0.27.0), 52, 56, 57, 62 (0.26.0), 74 (0.29.0) |
| GONE | 16 (Closed superseded) |
| PARTIAL | 11, 26, 65 |
| OPEN | 12, 15, 27, 28, 29, 31, 34, 35, 36, 37, 38, 39, 40, 41, 43, 44, 45, 46, 47a, 47b, 49, 51, 53, 54, 55, 58, 59, 60, 61, 63, 64, 66, 67, 68, 69, 70, 71, 72, 73, 75, 76, 77, 78, 79, 80, 81, 82 |

Where the old heading names a version, that is the `Closed` value; where it names only a date or a record, `Closed: record` and the `Record:` line names the record or commit the item's own text names. Check each `Record:` value exists (`ls` the path or `git cat-file -e <sha>`).

`Pairs` values, every one written on both sides:

| Item | Pairs |
|---|---|
| 75 | none |
| 49 | 59, 67, 78 |
| 59 | 49, 67, 78 |
| 67 | 49, 59, 78 |
| 78 | 49, 59, 67 |
| 51 | 31 |
| 31 | 51 |
| 40 | 43, 41 |
| 43 | 40 |
| 41 | 40 |
| 54 | 77, 76 |
| 77 | 54 |
| 76 | 38, 54 |
| 38 | 76 |
| 55 | 45 |
| 45 | 55 |
| 65 | 64 |
| 64 | 65 |
| every other OPEN or PARTIAL item | none |

Item 27's old pairing with 19 is dropped (19 is DONE). Item 36's dependency on 45 is stated in its Cost line, not as a pair.

`Cost` lines: one line each, what it costs NOW, taken from the item's ranking entry and its own text. Specific ones the spec fixes:
- 35: `the "captured too late" half is open: -PriorStateFile is a plain string hashed as given, and SKILL.md states the capture rule after the dispatch block` (the "no file at all" half is closed by the parameter; say so in the body).
- 71 and 72: `uncosted: <why, from the item's own text>`; 11 likewise, as stated under Step 2.
- 78: Medium, per its own text.
- 34: re-costed to carry the Fable raw-reply case (a retained reviewer reply is not checked to have reached its last section), amended in the body with that case from item 74's close.

- [ ] **Step 4: Write the bodies**

- OPEN and PARTIAL: the item's full current text, minus ranking-history prose (any sentence about entries moving, renumbering, or what entry the item used to hold) and minus any prose status line the header now carries. Keep every measurement, citation and constraint.
- PARTIAL (11, 26, 65): a paragraph beginning `**What remains.**` with at least twenty words, written from what the item's own text says remains.
- DONE and GONE: one to five sentences on what shipped, from the item's own resolution text, then `Record: <path or commit>`.
- New items 80, 81, 82: written from the sentences in item 74's close (80, 81) and item 32's close (82) that raise them; each cites the old-path commit `<lastfull>` and the line range it was raised at.

Rule 8 will flag any banned phrase left in an OPEN body; fix by deleting the narrative, never by rewording it to slip past.

- [ ] **Step 5: Replace the old file with the pointer**

Overwrite `docs/superpowers/plans/2026-07-27-0150-backlog.md` with exactly three lines:

```markdown
This file moved to `BACKLOG.md` at the repository root; the full text was last present here at commit `<lastfull>`.
A line citation into this path is bound to the layout the citing document read: `docs/superpowers/plans/rounds/2026-09-04-backlog-rewrite/citation-inventory.md` records the resolving commit for each citation where one exists, and a citation the inventory marks unresolved has none.
Do not resolve a citation into this path at any other commit.
```

- [ ] **Step 6: Attest every item and run the lint**

Every `Verified` line is first written as `Verified: 2026-09-04 000000000000`. Then:

```bash
python evals/tools/backlog_lint.py --digests
```

Copy each printed digest into its item's `Verified` line. This is the author's attestation of a file the author just wrote from reading every item, which is the explicit per-item act the spec asks for. Then:

```bash
python evals/tools/backlog_lint.py
```
Expected: `backlog lint: clean`. Fix every named failure; the failure names are the list.

- [ ] **Step 7: Run the real-file test and the full gate**

Add to `test_backlog_lint.py`:

```python
def test_real_backlog_passes():
    assert lint.main([]) == 0
```

Run: `python -m pytest evals -q`
Expected: all PASS (the live suites skip as usual).

- [ ] **Step 8: Commit**

```bash
git add BACKLOG.md docs/superpowers/plans/2026-07-27-0150-backlog.md evals/multi-model-verify/test_backlog_lint.py
git commit -m "rewrite the backlog into a root file with derived ranking and status"
```

---

### Task 11: Second-reader verification of the rewrite

**Files:**
- Create: `docs/superpowers/plans/rounds/2026-09-04-backlog-rewrite/second-reader.md`

This task is done by a DIFFERENT subagent from Task 10, with the old text at `git show <lastfull>:docs/superpowers/plans/2026-07-27-0150-backlog.md` beside `BACKLOG.md`.

- [ ] **Step 1: Compare every closed item**

For each DONE and GONE item: does the resolution block say what the old item's own resolution text says shipped? Does the `Record:` value name the record the old text names? Write one row per item: `| id | resolution matches? | record matches? | note |`.

- [ ] **Step 2: Compare every PARTIAL remainder**

For 11, 26 and 65: does the `**What remains.**` paragraph state what the old text says remains? One row each.

- [ ] **Step 3: Check every OPEN body kept its substance**

For each OPEN item: list any measurement, citation or constraint present in the old text and absent from the new body. A deleted ranking-history sentence is not a loss; a deleted measurement is.

- [ ] **Step 4: Check the header decisions against spec 1d**

Confirm each bullet of spec section 1d is reflected: 75 first with no pair; 49, 59, 67, 78 at entries 2 to 5; 35 narrowed; 68, 69, 43 placements; 73, 79, 71, 72 slotted; the pairing repairs; 34 amended; 80, 81, 82 present; no renumbering narrative.

- [ ] **Step 5: Write the record and fix what it found**

Save the rows under the four headings in `second-reader.md`. Every mismatch is fixed in `BACKLOG.md` by the Task 10 author (or this reader, if the fix is a copy of the old text), the item's `Verified` digest refreshed from the lint's printed expected value, and the lint re-run clean.

```bash
python evals/tools/backlog_lint.py
git add BACKLOG.md docs/superpowers/plans/rounds/2026-09-04-backlog-rewrite/second-reader.md
git commit -m "verify the backlog rewrite against the old text and record it"
```

---

### Task 12: Whole-branch gate and the Stop hook's first live pass

**Files:** none new.

- [ ] **Step 1: Run every gate, untruncated**

```bash
python evals/tools/skill_lint.py skills/multi-model-verify --strict
python evals/tools/skill_scanner.py skills
python evals/tools/check_exact_line_oracles.py
python evals/tools/run_trigger_evals.py
python evals/tools/backlog_lint.py
python -m pytest evals -q
```
Expected: every command exits 0.

- [ ] **Step 2: Run the PowerShell-facing modules under the other host**

Run: `$env:PARALLAX_PS_HOST = "pwsh"; python -m pytest evals/multi-model-verify/test_backlog_hooks.py evals/multi-model-verify/test_backlog_prepush.py -q; Remove-Item Env:PARALLAX_PS_HOST`
Then the same with `powershell`. Expected: both PASS.

- [ ] **Step 3: Run the range check over the whole branch**

```bash
python evals/tools/backlog_lint.py --range "$(git merge-base main HEAD)..HEAD"
```
Expected: exit 0 with `re-attested:` naming ids (the whole file is new against main, so every open item counts). If it fails, the branch is not pushable and the failure names why.

- [ ] **Step 4: Report**

State in the task report: every gate's exit code, which host each hook module ran under, and the range check's output line. Do not bump the plugin version; that follows the diff debate.

---

## Self-review against the spec

- Goals 1 to 4: Task 1 to 4 (derived ranking, lint), Task 5 to 8 (Stop reminder, pre-push refusal, CI detection), Task 10 (open work first, closed history short).
- Part 1a preamble: Task 10 Step 2. 1b ranking rules: rules 3, 4, 12. 1c field contract and digest: Tasks 1 and 2; fixtures for U+00A0, padded header, CRLF equality in Task 2. 47a/47b: `ID_RE`. Bodies: Task 10 Step 4. 1d decisions: Task 10 Steps 2 to 4 and Task 11 Step 4. 1e pointer, inventory, frozen-plan rewrite, untruncated grep: Tasks 9 and 10 Step 5; rule 11.
- Part 2 rules 1 to 12, exit codes, every failure printed, `--revision`: Tasks 1 to 3. Rule 7 reads only the file: `rule_7_verified` takes no git input. `--range`: Task 4.
- Part 3 preamble residuals: stated in the hook docstrings and the pre-push header. 3a0, 3a, 3b: Task 5; the exact refusal text; `stop_hook_active`; missing baseline, missing git, detached HEAD. Tracked settings and `.gitignore`: Task 6. 3c: Task 7, including the header rewrite and the README/CLAUDE statement. 3d: Task 8, including the ruleset paragraph as a workflow comment; the user decision itself is not made here.
- Error handling: pre-push refuses on missing python (Task 7); the hook entry point exits 0 with a note on missing python and the scripts exit 0 with a note on missing git, each with a test per host (Task 5).
- Fable plan review R1 (2026-09-04, revision e5a59e3) found six defects, all fixed in this revision: the missing-python note and the settings-command shape (entry point with `-File`, tests build argv from the same shape), the rule-1 order message, the Task 1 assertion Task 2's digest refresh would have broken, the seed repo's missing `.gitignore`, item 11 unranked, and Task 9's grep halting on this plan's own line and missing the probe plan's second citation shape at its line 158.
- Testing section: every bullet has a test in Tasks 2, 4, 5, 7 and 10 Step 7.
- Process: subagent-driven build, second reader (Task 11), version bump deferred, `BACKLOG.md` written last among the build tasks (Task 10 after Tasks 1 to 9).

Placeholder scan: `<sha41>` and `<lastfull>` are values the implementer reads from git at the step that names them, not deferred decisions. Type consistency: `check(text, *, repo_root, revision, today, rules=None, pointer_text=None)`, `reattested_items(old_text, new_text)`, `range_check(repo_root, range_spec, today)`, `lint_text(text, pointer_text, *, repo_root, revision, today, label)` are used with those names in every task.
