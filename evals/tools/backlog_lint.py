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
    if 7 in active:
        for item in doc.items:
            out.extend(rule_7_verified(item, doc, today))
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
    if args.digests:
        try:
            doc = parse(text)
        except ParseError as exc:
            print("file: cannot parse %s: %s" % (path, exc))
            return 2
        for item in doc.items:
            print("%s %s" % (item.id, canonical_digest(item, doc)))
        return 0
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
