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
