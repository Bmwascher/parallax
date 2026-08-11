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

FIELD_FORMS = {
    # form -> (renderer, accepted?)
    "well-formed":   (lambda k, v: f"{k}: {v}", True),
    "bare-label":    (lambda k, v: f"{k}:", False),
    "empty-value":   (lambda k, v: f"{k}: ", False),
    "no-space":      (lambda k, v: f"{k}:{v}", False),
    "leading-space": (lambda k, v: f" {k}: {v}", False),
    "padded-value":  (lambda k, v: f"{k}:  {v}  ", True),   # rule 6
    "escape-in-label": (lambda k, v: f"{k[:2]}{ESC}{k[2:]}: {v}", True),
    "escape-in-value": (lambda k, v: f"{k}: {ESC}{v}{RESET}", True),
    "wrong-value":   (lambda k, v: f"{k}: {v}-decoy", False),
}


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
    """Per field: presence x form x line ending, others well-formed."""
    for key, form, eol in itertools.product(KEYS, FIELD_FORMS,
                                            ("\n", "\r\n")):
        render, accepted = FIELD_FORMS[form]
        fields = well_formed_fields(skip=key) + [render(key, KEYS[key])]
        text, has_block = build("exactly-8", 2, fields, eol=eol)
        yield (f"B[{key},{form},"
               f"eol={'crlf' if eol == chr(13) + chr(10) else 'lf'}]",
               text, has_block and accepted)
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
        yield (f"B[{key},name-appears-mid-line]", text, True)
    # Presence: absent, and duplicated (rule 5 demands exactly one).
    for key in KEYS:
        fields = well_formed_fields(skip=key)
        text, _ = build("exactly-8", 2, fields)
        yield (f"B[{key},absent]", text, False)
        dup = fields + [f"{key}: {KEYS[key]}", f"{key}: {KEYS[key]}"]
        text, _ = build("exactly-8", 2, dup)
        yield (f"B[{key},duplicated-identical]", text, False)
        mixed = fields + [f"{key}: {KEYS[key]}", f"{key}:"]
        text, _ = build("exactly-8", 2, mixed)
        yield (f"B[{key},valid-plus-bare-label]", text, False)


def all_cases():
    return list(sweep_a()) + list(sweep_b())


# ---------------------------------------------------------------------------
# The suite
# ---------------------------------------------------------------------------

CASES = all_cases()


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
    mod = load_runner()
    assert mod.effective_route_ok(text, MODEL, EFFORT) is expected, name


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
