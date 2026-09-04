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

The governed-range clause (`--range`) counts a CLOSE as a re-attestation:
an item that was OPEN or PARTIAL before and is DONE or GONE after is named
as '<id> (closed)'. That is a deliberate widening of the spec's 3b/3c
wording; see `reattested_items`.

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

# The single-line oracle lives beside this file. The hooks load this module
# by path, so the directory is put on sys.path here rather than assumed.
_HERE = str(Path(__file__).resolve().parent)
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)
from exact_line import accept_exactly_one_nonempty_line  # noqa: E402

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
# Spec 1b: a group header is the literal `### ` followed by text. `###Name`
# and a bare `###` are therefore stray ranking lines, reported by rule 3.
GROUP_RE = re.compile(r"^### (.+)$")
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
            # A header whose text is only spaces or tabs is not "`### `
            # followed by text" (spec 1b); it falls through as a stray line.
            if group and group.group(1).strip(" \t") != "":
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


def git_bytes(repo_root, *args):
    """Like git_output, but the raw stdout bytes: no newline translation."""
    try:
        proc = subprocess.run(["git", *args], cwd=str(repo_root), capture_output=True)
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    return proc.stdout


def decode_utf8(raw):
    """Strict UTF-8 decode of file bytes with NO newline translation, so a
    lone CR reaches the parser and the digest as the byte it is (spec 1c
    folds CRLF only). Returns None when the bytes are not UTF-8."""
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return None


def read_at_revision(repo_root, revision, path):
    raw = git_bytes(repo_root, "show", "%s:%s" % (revision, path))
    return None if raw is None else decode_utf8(raw)


def in_tree_path(value):
    """A Record: path must be repository-relative: not absolute, not
    drive-rooted, and with no `..` segment. `..` alone would otherwise
    satisfy an existence check from inside any repository."""
    normalized = value.replace("\\", "/")
    if normalized == "" or normalized.startswith("/") or re.match(r"^[A-Za-z]:", normalized):
        return False
    return ".." not in normalized.split("/")


def path_exists(repo_root, revision, path):
    if not in_tree_path(path):
        return False
    if revision is None:
        root = Path(repo_root).resolve()
        target = (root / path).resolve()
        if target != root and root not in target.parents:
            return False
        return target.exists()
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
    """Group headers only. Spec rules 3 and 12 BOTH describe a stray line
    in the ranking (rule 12's second clause repeats rule 3); rule 3 is the
    single reporter, so one stray line is one failure and not two. That
    ownership is a recorded ruling of the 2026-09-04 build, not a dropped
    clause: every line rule 12's clause names is reported, under rule 3."""
    out = []
    for group in doc.groups:
        if group.raw_header == "":
            continue
        words = group.raw_header[3:].split()
        if len(words) > 8:
            out.append("ranking: rule 12 (header shape): %r has %d words, "
                       "at most 8 allowed" % (group.raw_header, len(words)))
    return out


def rule_1_header(item):
    out = []
    names = [k for k, _ in item.fields]
    status = item.get("Status")
    if names[:1] != ["Status"]:
        if "Status" not in names:
            out.append("item %s: rule 1 (header block): missing field Status"
                       % item.id)
        else:
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


def check(text, *, repo_root, revision, today, rules=None, pointer_text=None):
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
    return out


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
            text = decode_utf8(path.read_bytes())
        except OSError as exc:
            print("file: cannot read %s: %s" % (path, exc))
            return 2
        if text is None:
            print("file: cannot read %s: not UTF-8" % path)
            return 2
        pointer_path = Path(args.pointer) if args.pointer else repo_root / OLD_PATH
        try:
            pointer = decode_utf8(pointer_path.read_bytes())
        except OSError:
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
    """Ids re-attested between the two texts, in two forms.

    An item that is OPEN or PARTIAL in the new text counts when its
    Verified field changed or the item is new. An item that was OPEN or
    PARTIAL in the old text and is DONE or GONE in the new one also
    counts, reported as '<id> (closed)': closing an item IS an
    attestation about the governed work that closed it.

    The second form is a DELIBERATE WIDENING of the spec's 3b and 3c
    wording, which speaks only of a re-attested OPEN or PARTIAL item.
    Without it a wave whose only backlog change is a close could never
    satisfy the Stop hook or the pre-push clause. Everything else is
    unchanged: a Verified edit on an item that is DONE in BOTH texts does
    not count, and an unrelated byte does not count.
    """
    old = _verified_map(old_text)
    new = _verified_map(new_text)
    out = []
    for item_id, (status, verified) in new.items():
        if status in OPEN_STATUSES:
            if item_id not in old or old[item_id][1] != verified:
                out.append(item_id)
        elif status in ("DONE", "GONE"):
            if item_id in old and old[item_id][0] in OPEN_STATUSES:
                out.append("%s (closed)" % item_id)
    return out


def range_check(repo_root, range_spec, today):
    """The governed-range clause: if the range touched a governed path,
    BACKLOG.md must carry a re-attested item. `reattested_items` decides
    what counts, and it deliberately widens the spec's 3b/3c wording so a
    CLOSE (OPEN or PARTIAL becoming DONE or GONE) counts too."""
    if ".." in range_spec:
        base, head = range_spec.split("..", 1)
        if not base or not head:
            print("range %s: malformed" % range_spec)
            return 2
        # --no-renames: with rename detection on, a governed file moved to an
        # ungoverned path is listed only at its destination and the governed
        # side of the change disappears from the listing.
        changed = git_output(repo_root, "diff", "--no-renames", "--name-only",
                             base, head)
        old_text = read_at_revision(repo_root, base, BACKLOG_PATH)
    else:
        head = range_spec
        changed = git_output(repo_root, "diff-tree", "--no-commit-id", "--root",
                             "--no-renames", "-r", "--name-only", head)
        parent_out = git_output(repo_root, "rev-parse", "--verify", "--quiet", head + "^")
        parent = (accept_exactly_one_nonempty_line(parent_out)
                  if parent_out is not None else None)
        old_text = (read_at_revision(repo_root, parent, BACKLOG_PATH)
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
                  "item was re-attested (a refreshed Verified line, or the item "
                  "closed to DONE or GONE)" % (range_spec, ", ".join(governed)))
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


if __name__ == "__main__":
    sys.exit(main())
