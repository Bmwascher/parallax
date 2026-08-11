"""Backlog item 9, part A: generated shape coverage for the route parser.

Tier 2b. No model calls, no network, no PowerShell.

WHY THIS EXISTS. 0.17.0 spent twelve panel rounds and nine defects on
mechanical parser faults - which text a marker was counted in, which string
a slice was taken from, which list a loop walked, whether a quoted example
was a container. Every one was found by a model reading code and guessing
the shape that would break it, one shape per round, at two reviewer calls
plus a full gate re-run each time. A generator enumerates those shapes in
milliseconds.

WHAT THIS COVERS, AND NO MORE. ONE parser in ONE module:
`header_block` and `effective_route_ok` in `evals/tools/run_behavioral_evals.py`.
It is the CHEAPEST first target, not a measured highest-value one - the
documented hotspot is the PowerShell probe, covered by its own module.
This does not on its own close backlog item 9.

THE ORACLE IS THE CONSTRUCTION, NOT A SECOND PARSER. Every case knows
whether it is well-formed because the generator BUILT it that way. Writing
an independent parser to check the first one would just reproduce its bugs
in a second place.

THE EVIDENCE IS THE MUTATION RUN, NOT THE GREEN RUN. A generated suite
that passes proves the parser agrees with itself. `test_every_defence_is_killed`
removes each recorded defensive clause in turn and requires the generated
cases to catch it, naming the case that did.
"""

import importlib.util
import itertools
import re
import sys
import types
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "evals" / "tools" / "run_behavioral_evals.py"
NOTES = (REPO_ROOT / "skills" / "multi-model-verify" / "references"
         / "model-prompting-notes.md")

# ---------------------------------------------------------------------------
# The FROZEN route grammar. These seven rules are the oracle, and they were
# frozen in the plan debate BEFORE any case was generated - the first draft
# would have produced cases whose correct answer had not been decided
# (three or more rules, an escape inside a real label, whitespace around a
# value). A case whose expected verdict is not derivable from these rules
# is a defect in this module, not a finding about the parser.
#
#   1. ANSI escapes are removed from the WHOLE output BEFORE anything is
#      located. An escape anywhere is presentation only; it never makes a
#      line malformed.
#   2. A DELIMITER RULE is a line whose stripped form is at least 8
#      characters and consists only of "-".
#   3. The HEADER BLOCK is the lines strictly between the FIRST and the
#      SECOND rule. Fewer than two rules means there is no block.
#   4. Three or more rules is VALID input. The first two select the block;
#      everything from the second rule onward is ignored, however
#      header-shaped.
#   5. For key K: a LABEL matches ^K: and a FIELD LINE matches ^K: (.+)$.
#      K is ACCEPTED with value V iff the block holds EXACTLY ONE label and
#      EXACTLY ONE field line for K, V being the capture stripped.
#   6. Surrounding whitespace in a value is NORMALIZATION, not
#      malformation.
#   7. A bare "K:" or an empty "K: " yields a label and no field line, so K
#      is not accepted. The route is CLEAN iff all four keys are accepted
#      and equal their canonical values.
# ---------------------------------------------------------------------------

ESC = "\x1b[31m"
RESET = "\x1b[0m"


def canonical_pair():
    notes = NOTES.read_text(encoding="utf-8")
    model = re.search(r"Canonical model id: `([^`\n]+)`", notes)
    effort = re.search(r"Canonical reasoning effort: `([^`\n]+)`", notes)
    assert model and effort, "canonical declarations missing"
    return model.group(1), effort.group(1)


MODEL, EFFORT = canonical_pair()
KEYS = {"model": MODEL, "provider": "openai",
        "reasoning effort": EFFORT, "sandbox": "read-only"}


def load_runner(source=None):
    """Import the runner, optionally from mutated source."""
    text = source if source is not None else RUNNER.read_text(encoding="utf-8")
    mod = types.ModuleType("run_behavioral_evals_shapes")
    mod.__file__ = str(RUNNER)
    exec(compile(text, str(RUNNER), "exec"), mod.__dict__)
    return mod


# ---------------------------------------------------------------------------
# Case construction
# ---------------------------------------------------------------------------

RULE_FORMS = {
    "exactly-8": "--------",
    "below-floor": "---",
    "long": "-" * 20,
    "trailing-space": "--------   ",
    "coloured": ESC + "--------" + RESET,
    # Long enough AND dash-prefixed, but not ALL dashes. Rule 2 demands
    # both, and this is the shape that tells the two halves apart. Added
    # after the first mutation run: no case in the original matrix could
    # distinguish `set(...) == {"-"}` from `startswith("-")`, so mutant 3
    # survived and the harness reported it as a coverage hole.
    "dash-prefixed-text": "-------- codex startup",
}
# Rule 2: the stripped form must be at least 8 characters of only "-".
# "below-floor" fails the length half; "dash-prefixed-text" fails the
# shape half; "coloured" qualifies, because rule 1 removes the escapes
# before rule 2 looks.
QUALIFIES = {"exactly-8": True, "below-floor": False, "long": True,
             "trailing-space": True, "coloured": True,
             "dash-prefixed-text": False}

# The FIVE field forms the plan froze for sweep B, and their accepted
# verdict from rules 5 to 7. Nothing here is read off the parser.
FIELD_FORMS = {
    # form -> (renderer, accepted?)
    "well-formed":   (lambda k, v: f"{k}: {v}", True),
    "bare-label":    (lambda k, v: f"{k}:", False),
    "empty-value":   (lambda k, v: f"{k}: ", False),
    "no-space":      (lambda k, v: f"{k}:{v}", False),
    "leading-space": (lambda k, v: f" {k}: {v}", False),
}

# The THREE escape placements the plan froze, as an axis of its own rather
# than as extra entries in the form table. Rule 1 removes escapes from the
# whole output before anything is located, so placement can never change a
# verdict - which is exactly the claim this axis exists to test. If any
# expected value below varied by placement, rule 1 would be false.
ESCAPE_PLACEMENTS = ("none", "in-label", "in-value")

# The THREE presence states the plan froze. "twice" is underspecified in
# the freeze: it does not say whether the two occurrences share the form
# and escape under test. THIS MODULE READS IT AS BOTH THE SAME, because
# the axis is per-form and a mixed pair would be a different form
# combination that the product already covers separately. Mixed pairs are
# still covered, as a declared extra below.
PRESENCE = ("absent", "once", "twice")

# Beyond the frozen product. Each earns its place by killing a mutant or
# by pinning a rule the five frozen forms cannot reach; none of them is
# part of the 360, and the count below says so.
EXTRA_FORMS = {
    "padded-value":  (lambda k, v: f"{k}:  {v}  ", True),   # rule 6
    "wrong-value":   (lambda k, v: f"{k}: {v}-decoy", False),
}


def render_field(key, value, form, escape):
    """One field line: a frozen form with a frozen escape placement.

    The escape goes INSIDE the label or INSIDE the value, never between
    them, so the two placements are distinguishable after rule 1 strips
    them. A form with no value slot still gets an in-value case, with the
    escape written where the value would have been - otherwise that cell
    of the product would be a copy of the "none" cell.
    """
    k, v = key, value
    if escape == "in-label":
        k = key[:2] + ESC + key[2:]
    elif escape == "in-value":
        v = ESC + value + RESET
    if form == "well-formed":
        return f"{k}: {v}"
    if form == "no-space":
        return f"{k}:{v}"
    if form == "leading-space":
        return f" {k}: {v}"
    tail = (ESC + RESET) if escape == "in-value" else ""
    if form == "bare-label":
        return f"{k}:{tail}"
    if form == "empty-value":
        return f"{k}: {tail}"
    raise AssertionError(f"unfrozen form {form!r}")


def well_formed_fields(skip=None):
    return [f"{k}: {v}" for k, v in KEYS.items() if k != skip]


def build(rule_form, rule_count, fields, decoy=False, fields_after=False,
          eol="\n"):
    """Render one case. Returns (text, expected_clean)."""
    rule = RULE_FORMS[rule_form]
    qualifies = QUALIFIES[rule_form]
    out = ["OpenAI Codex v0.144.1"]
    if rule_count == 0:
        out += fields
    else:
        out.append(rule)
        if fields_after:
            # Fields sit between the SECOND and THIRD rule, so the block
            # selected by rule 3 is EMPTY. Rule 4 says later text is
            # ignored however header-shaped.
            out.append(rule)
            out += fields
            for _ in range(rule_count - 2):
                out.append(rule)
        else:
            out += fields
            for _ in range(rule_count - 1):
                out.append(rule)
    if decoy:
        out += [f"{k}: {v}" for k, v in KEYS.items()]
    text = eol.join(out) + eol
    # Expected, from the construction: a block exists only when at least
    # two rules QUALIFY, and the fields must be inside the first one.
    has_block = qualifies and rule_count >= 2 and not fields_after
    return text, has_block


def sweep_a():
    """Block location: rule count x rule form x decoy x line ending."""
    for form, count, decoy, eol in itertools.product(
            RULE_FORMS, range(0, 5), (False, True), ("\n", "\r\n")):
        text, has_block = build(form, count, well_formed_fields(),
                                decoy=decoy, eol=eol)
        # With a block holding every well-formed field, clean == has_block.
        yield (f"A[{form},rules={count},decoy={decoy},"
               f"eol={'crlf' if eol == chr(13) + chr(10) else 'lf'}]",
               text, has_block)
    # Rule 4 explicitly: three rules with the fields in the SECOND gap.
    for count in (3, 4):
        text, _ = build("exactly-8", count, well_formed_fields(),
                        fields_after=True)
        yield (f"A[fields-after-closing-rule,rules={count}]", text, False)


def sweep_b():
    """The frozen product, per key: presence x form x escape x line ending.

    4 keys x 3 presence x 5 forms x 3 escapes x 2 line endings = 360.

    The `absent` cells repeat: with the key omitted, form and escape have
    nothing to act on, so all 30 per key render the same text. They are
    generated anyway, because the product is what the plan froze and a
    quietly pruned product is a matrix nobody specified. The first build
    of this sweep crossed nothing and produced 88 cases; the diff debate
    caught it.
    """
    for key, presence, form, escape, eol in itertools.product(
            KEYS, PRESENCE, FIELD_FORMS, ESCAPE_PLACEMENTS,
            ("\n", "\r\n")):
        _, accepted = FIELD_FORMS[form]
        fields = well_formed_fields(skip=key)
        if presence == "once":
            fields = fields + [render_field(key, KEYS[key], form, escape)]
        elif presence == "twice":
            line = render_field(key, KEYS[key], form, escape)
            fields = fields + [line, line]
        text, has_block = build("exactly-8", 2, fields, eol=eol)
        # From rules 1, 5 and 7. Rules 5 and 7 give the presence and form
        # halves: an absent key yields no label and no field line, a
        # doubled one yields two of whichever the form produces, so either
        # way `exactly one of each` fails and only the `once` cells can be
        # clean, and only in an accepted form. RULE 1 is what licenses the
        # third axis being absent from this expression - escapes are
        # stripped before anything is located, so placement is
        # presentational. Citing only 5 and 7 would leave the escape axis
        # unexplained; the cross-vendor lane caught that at round 2 of the
        # diff debate.
        expected = has_block and presence == "once" and accepted
        yield (f"B[{key},{presence},{form},esc={escape},"
               f"eol={'crlf' if eol == chr(13) + chr(10) else 'lf'}]",
               text, expected)
    # --- beyond the frozen product ---
    for key, form in itertools.product(KEYS, EXTRA_FORMS):
        render, accepted = EXTRA_FORMS[form]
        fields = well_formed_fields(skip=key) + [render(key, KEYS[key])]
        text, has_block = build("exactly-8", 2, fields)
        yield (f"X[{key},{form}]", text, has_block and accepted)
    # A key name appearing MID-LINE inside the block. Rule 5 anchors both
    # patterns at line start, so this is ordinary noise and the route stays
    # clean. Added after the first mutation run: nothing in the original
    # matrix could tell an anchored label count from an unanchored one, so
    # mutant 10 survived. codex really does print a `workdir:` line, and a
    # Windows path can contain anything.
    for key in KEYS:
        noisy = (well_formed_fields()
                 + [f"workdir: C:\\repo (see {key}: elsewhere)"])
        text, _ = build("exactly-8", 2, noisy)
        yield (f"X[{key},name-appears-mid-line]", text, True)
    # A MIXED pair: one good field line and one bare label for the same
    # key. The product's `twice` cells hold two of the SAME form, so this
    # shape is outside it, and it is the one that separates "count the
    # labels" from "count the field lines" - mutants 6 and 7 die on
    # different clauses of it.
    for key in KEYS:
        fields = well_formed_fields(skip=key)
        mixed = fields + [f"{key}: {KEYS[key]}", f"{key}:"]
        text, _ = build("exactly-8", 2, mixed)
        yield (f"X[{key},valid-plus-bare-label]", text, False)


def all_cases():
    return list(sweep_a()) + list(sweep_b())


# ---------------------------------------------------------------------------
# The suite
# ---------------------------------------------------------------------------

CASES = all_cases()

# Loaded ONCE. The unmutated source is the same for every case, and
# re-executing the runner module per case cost several hundred execs for
# no evidence. The mutation test below still loads its own module per
# mutant, because there the source genuinely differs.
REAL = load_runner()


def test_the_frozen_product_is_enumerated_in_full():
    """The plan froze a Cartesian product; this is the arithmetic.

    Stated as a product rather than a total, so a dropped axis names
    itself instead of showing up as a number that is merely different.
    """
    assert len(KEYS) == 4
    assert len(PRESENCE) == 3
    assert len(FIELD_FORMS) == 5
    assert len(ESCAPE_PLACEMENTS) == 3
    product = len(KEYS) * len(PRESENCE) * len(FIELD_FORMS) * len(
        ESCAPE_PLACEMENTS) * 2
    assert product == 360
    frozen = [c for c in CASES if c[0].startswith("B[")]
    assert len(frozen) == 360, (
        f"sweep B enumerated {len(frozen)} of the frozen 360")
    # The extras are counted separately and deliberately, so that "how
    # many cases" never has to mean "how many of them were specified".
    extras = [c for c in CASES if c[0].startswith("X[")]
    assert len(extras) == 16, f"{len(extras)} extras, expected 16"


def test_the_escape_axis_never_changes_a_verdict():
    """Rule 1, asserted over the matrix rather than trusted.

    Every frozen cell has two siblings that differ ONLY in escape
    placement. If any triple disagrees, rule 1 is false and the whole
    oracle rests on something that is not written down.
    """
    by_cell = {}
    for name, _, expected in CASES:
        if not name.startswith("B["):
            continue
        stripped = re.sub(r",esc=[a-z-]+", "", name)
        by_cell.setdefault(stripped, set()).add(expected)
    assert by_cell, "no frozen cells found"
    disagreeing = {k: v for k, v in by_cell.items() if len(v) != 1}
    assert not disagreeing, (
        f"escape placement changed the verdict for {sorted(disagreeing)[:3]}")
    assert len(by_cell) == 120, f"{len(by_cell)} cells, expected 120"


def test_the_matrix_is_not_trivially_one_sided():
    """A generator that only produces failures proves nothing about the
    accepting path, and one that only accepts proves nothing about the
    refusing path."""
    cleans = sum(1 for _, _, expected in CASES if expected)
    assert cleans >= 10, f"only {cleans} of {len(CASES)} cases expect clean"
    assert len(CASES) - cleans >= 40, "too few refusing cases"


@pytest.mark.parametrize("name,text,expected",
                         CASES, ids=[c[0] for c in CASES])
def test_generated_shape(name, text, expected):
    assert REAL.effective_route_ok(text, MODEL, EFFORT) is expected, name


# Ten mutants, one per defence the parser's own comments record. Each is a
# textual edit to the runner source; the generated matrix must catch it.
MUTANTS = {
    "1-ansi-not-stripped-before-locating": (
        'lines = ANSI_ESCAPE.sub("", output or "").splitlines()',
        'lines = (output or "").splitlines()'),
    "2-rule-length-floor-dropped": (
        'if len(ln.strip()) >= 8 and set(ln.strip()) == {"-"}',
        'if len(ln.strip()) >= 1 and set(ln.strip()) == {"-"}'),
    "3-rule-shape-loosened": (
        'if len(ln.strip()) >= 8 and set(ln.strip()) == {"-"}',
        'if len(ln.strip()) >= 8 and ln.strip().startswith("-")'),
    "4-no-block-searches-whole-output": (
        "    if len(rules) < 2:\n        return None",
        '    if len(rules) < 2:\n        return "\\n".join(lines)'),
    "5-last-two-rules-instead-of-first-two": (
        'return "\\n".join(lines[rules[0] + 1:rules[1]])',
        'return "\\n".join(lines[rules[-2] + 1:rules[-1]])'),
    "6-label-count-dropped": (
        "one_each = len(labels) == 1 and len(found) == 1",
        "one_each = len(found) == 1"),
    "7-counts-loosened-to-at-least-one": (
        "one_each = len(labels) == 1 and len(found) == 1",
        "one_each = len(labels) >= 1 and len(found) >= 1"),
    "8-first-match-wins": (
        'header[key] = found[0].strip() if one_each else ""',
        'header[key] = found[0].strip() if found else ""'),
    "9-sandbox-not-compared": (
        '"reasoning effort": effort, "sandbox": "read-only"}',
        '"reasoning effort": effort}'),
    "10-patterns-unanchored": (
        'labels = re.findall(rf"(?m)^{re.escape(key)}:", block)',
        'labels = re.findall(rf"(?m){re.escape(key)}:", block)'),
}


@pytest.mark.parametrize("mutant", sorted(MUTANTS))
def test_every_defence_is_killed(mutant):
    """Remove one defence; the generated matrix must notice.

    This is the evidence. A green run against the real parser only shows
    the parser agrees with itself; a mutant that no generated case kills
    is a COVERAGE HOLE and this test reports it as one.
    """
    old, new = MUTANTS[mutant]
    source = RUNNER.read_text(encoding="utf-8")
    assert old in source, f"{mutant}: anchor no longer present in the source"
    mod = load_runner(source.replace(old, new, 1))
    killers = []
    for name, text, expected in CASES:
        try:
            got = mod.effective_route_ok(text, MODEL, EFFORT)
        except Exception as exc:                      # noqa: BLE001
            killers.append(f"{name} (raised {type(exc).__name__})")
            break
        if got is not expected:
            killers.append(f"{name} (expected {expected}, got {got})")
            if len(killers) >= 3:
                break
    assert killers, (
        f"MUTANT SURVIVED: {mutant}. No generated shape distinguishes the"
        " defended parser from the one without this clause, which is a"
        " coverage hole in this matrix - add the shape, do not relax the"
        " assertion."
    )
    print(f"{mutant} killed by: {'; '.join(killers)}")


def test_the_scope_claim_is_recorded():
    """The claim this module may make, pinned so it cannot widen."""
    text = Path(__file__).read_text(encoding="utf-8")
    assert "ONE parser in ONE module" in text
    assert "does not on its own close backlog item 9" in text


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
