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


def _literal(node):
    """The node's own string value, or nothing.

    Deliberately NOT a walk. Walking every constant below an operand
    collects both branches of a conditional: `assert ("x" if flag else
    "y") in body` requires only the selected value, yet a walk returns
    both, so the unselected one becomes a pin the assertion never checks.

    Adjacent string literals are already folded into ONE constant by the
    parser, which is how nearly every pin in this repo is written.

    The cost is real but bounded, and worth stating exactly rather than
    waving away: five fragments are lost, all from runtime-constructed
    needles such as `"--model " + CANONICAL_ID` and
    `'model="' + CANONICAL_ID + '"'`. Those assertions DO require their
    fragments to be present, so these are genuine partial locks, not
    noise. They are dropped deliberately. The correct claim is that the
    strict rule costs no CURRENT MARKED COVERAGE - all nine regions in
    scope and all three history controls are unaffected - not that it
    costs nothing.
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
      an `and`, which contributes each operand it recognizes

    The conjunction rule is stated that way on purpose. A MIXED `and`
    such as `assert "lit" in body and flag` contributes "lit" and drops
    the rest, rather than being rejected whole. That is sound: the
    assertion passes only if every operand is true, so a recognized
    operand's requirement holds regardless of what sits beside it.
    Rejecting mixed conjunctions would discard real locks for no gain.

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
                and len(node.left.args) == 1
                and not node.left.keywords
                and isinstance(right, ast.Constant)
                and isinstance(right.value, int)
                and not isinstance(right.value, bool)):
            n = right.value
            positive = ((isinstance(op, (ast.Eq, ast.GtE)) and n >= 1)
                        or (isinstance(op, ast.Gt) and n >= 0))
            if positive:
                return _literal(node.left.args[0])
        return set()
    if _is_count_call(node) and len(node.args) == 1 and not node.keywords:
        return _literal(node.args[0])
    return set()


# Context managers that swallow the exception an assertion raises.
# Matched by the called NAME, so `pytest.raises(...)`, a bare
# `raises(...)` from `from pytest import raises`, and the contextlib
# equivalents are all caught.
CONSUMING_CALLS = frozenset({"raises", "suppress"})


def _is_consuming_with(node):
    """True for a `with` block whose body's failures are swallowed."""
    if not isinstance(node, (ast.With, ast.AsyncWith)):
        return False
    for item in node.items:
        call = item.context_expr
        if not isinstance(call, ast.Call):
            continue
        func = call.func
        if isinstance(func, ast.Attribute) and func.attr in CONSUMING_CALLS:
            return True
        if isinstance(func, ast.Name) and func.id in CONSUMING_CALLS:
            return True
    return False


def _is_xfail_decorated(node):
    """True for a function marked as expected to fail."""
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    for decorator in node.decorator_list:
        expr = decorator.func if isinstance(decorator, ast.Call) else decorator
        while isinstance(expr, ast.Attribute):
            if expr.attr == "xfail":
                return True
            expr = expr.value
        if isinstance(expr, ast.Name) and expr.id == "xfail":
            return True
    return False


def _assert_tests(node, consumed=False):
    """Yield the test of every assertion whose failure reaches the runner.

    An assertion locks its text only because failing it fails the suite.
    Where that failure is deliberately caught, the assertion proves the
    OPPOSITE and must contribute nothing.

    The shape that forced this, found by the cross-vendor lane in the
    0.15.0 diff debate:

        with pytest.raises(AssertionError):
            assert "Entire marked region." in body

    That test passes when the region text is ABSENT, yet an unrestricted
    walk registered the literal and the region read as covered - false
    coverage, the one direction this checker may never produce. It is not
    the execution-blind limit the design already accepts: the assertion
    runs, and its failure is eaten.

    Detection is by ENCLOSING CONTEXT, not by assertion shape, because
    the assertion itself is identical either way.

    Deliberately conservative on three counts. Any `raises(...)` counts,
    not only `raises(AssertionError)` - narrowing it would mean tracking
    which exception types an assert can raise. Every statement in the
    body of a `try` that HAS HANDLERS counts, whatever those handlers
    catch. And an xfail marker disqualifies the whole function. Each
    over-rejection loses a pin,
    which reads UNCOVERED, which is a red. Under-rejecting manufactures
    coverage. Only one of those is safe to get wrong.

    Costs nothing today: no live pin file contains any of these shapes.
    """
    if isinstance(node, ast.Assert):
        if not consumed:
            yield node.test
        return
    if _is_consuming_with(node) or _is_xfail_decorated(node):
        consumed = True
    if isinstance(node, (ast.Try, ast.TryStar)):
        # Only a handler can catch the failure. `try/finally` runs the
        # cleanup and then lets the AssertionError through, so its body
        # is ordinary asserting code. Consuming it too was stricter than
        # this module's own documented rule and cost real locks for no
        # safety - found in the round-2 fix re-review of this very fix.
        body_consumed = consumed or bool(node.handlers)
        for child in node.body:
            yield from _assert_tests(child, body_consumed)
        for group in (node.handlers, node.orelse, node.finalbody):
            for child in group:
                yield from _assert_tests(child, consumed)
        return
    for child in ast.iter_child_nodes(node):
        yield from _assert_tests(child, consumed)


def collect_pins(paths):
    """Normalized string literals that some assertion checks for.

    Read through ast, not regex: nearly every pin in this repo is written
    as adjacent string literals across several lines, and the parser
    joins those into one constant for us.

    Only assertions whose failure reaches the runner are read; see
    `_assert_tests` for why, and for the shape that proved it necessary.

    Accepted limits, all with the same safe failure direction - the
    region reads UNCOVERED, which is a red, never false coverage: a
    string bound to a name and asserted through that name, a regex lock
    such as `re.search(r"...", text)`, and a literal compared with `==`.

    Some limits run the OTHER way and could in principle manufacture
    coverage. The design tags every limit by direction and states NO
    total, because the total was written as "one", corrected to "two",
    and was still wrong. Read the tags there rather than trusting a count
    here.
    """
    pins = set()
    for path in paths:
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for test in _assert_tests(tree):
            pins |= _clause_pins(test)
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
