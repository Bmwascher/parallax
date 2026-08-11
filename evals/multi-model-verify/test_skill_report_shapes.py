"""Backlog item 9, part B: generated shape coverage for `Get-SkillReport`.

Tier 2b. Windows-only. No model calls, no network, no live codex.

WHY THIS PARSER. Item 9's evidence is entirely PowerShell: the 0.17.0
cycle spent twelve panel rounds and nine defects here, and the function's
own comments name them one by one - which text a span was taken from
(raw versus masked), which arrangement counted as a container, whether a
quoted delimiter was a real one, and whether an unreadable entry line was
dropped in silence. Part A covered the behavioural grader's route parser,
which is cheaper but is not where the defect history lives.

COST. Cases are generated in Python and sent through ONE PowerShell
process per host: `run_functions` dot-sources the production function
block from a file and runs a snippet over the whole matrix. No model
tokens, no live CLI, and CI already runs this directory under both
Windows PowerShell and pwsh.

THE ORACLE IS THE CONSTRUCTION. Each case knows its expected verdict
because the generator built it that way. THE EVIDENCE IS THE MUTATION
RUN: `test_every_defence_is_killed` removes one recorded defence at a
time and requires a generated case to catch it, naming the case.
"""

import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PROBE = REPO_ROOT / "tools" / "codex-context-probe.ps1"

# Same slice the probe's own test module uses, widened at the start so the
# $script:KnownContainers list (which Hide-KnownContainer reads) comes with
# the functions. A slice that omits it would test a function whose
# dependency is undefined, which is a different function.
BODY_START = "function Get-PromptText"
BODY_END = "$toplevel ="

POWERSHELL = (os.environ.get("PARALLAX_PS_HOST")
              or shutil.which("powershell") or shutil.which("pwsh"))

pytestmark = pytest.mark.skipif(
    os.name != "nt" or POWERSHELL is None,
    reason="the probe is a Windows tool and needs a PowerShell host")

OPEN = "<skills_instructions>"
CLOSE = "</skills_instructions>"
HEADING = "### Available skills"
ENTRY = "- demo:widget: Use when demoing. (file: C:/s/demo/SKILL.md)"

# ---------------------------------------------------------------------------
# Frozen invariants - decided before any case was generated.
#
#   1. BlockPresent and Entries are reported SEPARATELY. An absent
#      container and a present-but-unparseable one are different facts.
#   2. TWO shapes are non-ambiguous: NO delimiters at all, representing an
#      absent container, or EXACTLY ONE correctly ordered pair. Every other
#      arrangement - opener-only, closer-only, two or more of either,
#      closer before opener - is AMBIGUOUS.
#      (This wording replaces a self-contradictory one that called the
#      ordered pair the ONLY non-ambiguous shape and then exempted "none"
#      in the next sentence. The generated oracle and production always
#      behaved as stated here; the SENTENCE was wrong, not the code.
#      Found by the cross-vendor lane at round 10.)
#   3. The heading is honoured only INSIDE the container body. A heading
#      anywhere else supplies no entries.
#   4. Known containers are MASKED before the scan, so a delimiter quoted
#      inside one is not a delimiter. Masking is space-for-character, so
#      every offset outside it is unchanged.
#   5. Every entry-looking line is audited. A line that fails the grammar
#      sets Malformed rather than being dropped in silence.
#
# Invariants 6, 7 and 8 were added at CYCLE EXCHANGE 13, which is DIFF
# ROUND 1. Both numbers, because the cycle ran twelve plan rounds and then
# opened a separate diff debate: "round 13" alone reads as a thirteenth
# plan round, which is not where this was found.
#
# The generator was already computing all three; they were simply not
# written down, so those expected values rested on agreement with the
# production code rather than on a decided rule. A generated suite whose
# oracle is read off the implementation is not independent evidence,
# whatever it scores. Nothing about the code or the expected values
# changed when these were added - the RULES had been left implicit.
#
#   6. BlockPresent is TRUE iff at least one OPENER survives masking.
#      A closer with no opener reports the container ABSENT: an opener is
#      what claims a container exists, and a stray closer claims nothing.
#      Presence is therefore independent of ambiguity - a three-opener
#      arrangement is present AND ambiguous.
#   7. Entries are read ONLY from the body of an unambiguous single
#      ordered pair. Every ambiguous arrangement reports ZERO entries even
#      with a heading sitting inside it, because ambiguity means there is
#      no single body to read from. Reporting entries from a guessed body
#      is the failure this rule forbids.
#   8. The entry grammar, as a truth table rather than a regex:
#      an entry is ONE line, `- <name>: <description> (file: <path>)`.
#      The file marker is the LAST such marker on the line, so a
#      description that itself mentions `(file: x)` still parses and a
#      path containing parentheses stays whole. Two entries joined onto
#      one line is MALFORMED and yields no entry. A line with no file
#      marker is MALFORMED and yields no entry. Malformed is reported, not
#      silently dropped, which is invariant 5 applied to this grammar.
# ---------------------------------------------------------------------------


def case(name, text, *, present, ambiguous, entries, malformed=False):
    return {"name": name, "text": text, "present": present,
            "ambiguous": ambiguous, "entries": entries,
            "malformed": malformed}


def container(body):
    return OPEN + "\n" + body + "\n" + CLOSE


def block(entries=1, heading=True):
    lines = []
    if heading:
        lines.append(HEADING)
    for i in range(entries):
        lines.append(ENTRY.replace("widget", f"widget{i}")
                          .replace("demo/SKILL", f"demo{i}/SKILL"))
    return "\n".join(lines)


# The QUOTED-CONTAINER axis. <INSTRUCTIONS> carries the global and project
# AGENTS.md bodies verbatim, so a user's own file may legitimately contain
# a skills delimiter as prose. Masking blanks it before the scan, which is
# why a quoted delimiter must never move the counts.
QUOTED = {
    "none": "",
    "one-opener": ("<INSTRUCTIONS>\nNever emit " + OPEN + " yourself.\n"
                   "</INSTRUCTIONS>\n"),
    "opener-and-closer": ("<INSTRUCTIONS>\nBad: " + OPEN + " ... " + CLOSE
                          + "\n</INSTRUCTIONS>\n"),
}
HEADINGS = ("inside", "outside", "both", "absent")


def arrangement(opens, closes, order, inner, outside):
    """Render one delimiter arrangement.

    `order` is "opener-first" or "closer-first"; with no opener or no
    closer the two render identically, and that duplication is kept rather
    than special-cased so the matrix is the declared product.
    """
    parts = []
    if outside:
        parts.append(outside)
    if order == "closer-first" and opens and closes:
        parts += [CLOSE] * closes + [inner] + [OPEN] * opens
    else:
        parts += [OPEN] * opens + [inner] + [CLOSE] * closes
    return "\n".join(p for p in parts if p)


def build_cases():
    """The frozen Cartesian product.

    opener count x closer count x ordering x heading placement x quoted
    container x line ending = 4 * 4 * 2 * 4 * 3 * 2 = 768 cases.

    Written after round 9, which found that the first implementation
    hand-picked 19 arrangements and duplicated them for CRLF instead of
    enumerating the product the plan froze. It had no three-opener or
    three-closer case and never crossed the delimiter, heading and
    quoted-container axes. Killed mutants over a matrix that is not the
    declared one do not satisfy the declared enumeration.
    """
    cases = []
    for opens in range(4):
        for closes in range(4):
            for order in ("opener-first", "closer-first"):
                for heading in HEADINGS:
                    for qname, quoted in QUOTED.items():
                        inner = (block() if heading in ("inside", "both")
                                 else "no heading here")
                        outside = ((HEADING + "\n" + ENTRY)
                                   if heading in ("outside", "both") else "")
                        text = quoted + arrangement(opens, closes, order,
                                                    inner, outside)
                        # Invariant 2, from the construction. A quoted
                        # delimiter is masked, so it never counts.
                        none = opens == 0 and closes == 0
                        ordered = order == "opener-first" or not (opens
                                                                  and closes)
                        one = opens == 1 and closes == 1 and ordered
                        ambiguous = not (none or one)
                        # Invariant 6. An opener is what claims a
                        # container; a closer alone claims nothing.
                        present = opens >= 1
                        # Invariants 3 and 7: the body of the ONE ordered
                        # pair, and nothing else, supplies entries.
                        entries = (1 if (one and heading in ("inside", "both"))
                                   else 0)
                        name = (f"o{opens}c{closes}/{order}/{heading}"
                                f"/quoted-{qname}")
                        for eol, suffix in (("\n", "lf"), ("\r\n", "crlf")):
                            cases.append(case(
                                f"{name}/{suffix}",
                                text.replace("\n", eol),
                                present=present, ambiguous=ambiguous,
                                entries=entries))
    return cases


def entry_grammar_cases():
    """Invariants 5 and 8, on the one arrangement that reaches the loop.

    Kept as named cases rather than folded into the product: they vary the
    ENTRY LINE, which is a different axis from the delimiter arrangement,
    and crossing them would multiply the matrix without testing anything
    the product does not already cover.

    Every expected value below comes from invariant 8's truth table.
    Cycle exchange 13, diff round 1, found these outcomes were being
    asserted against a rule that existed only as production comments;
    the rule is now written above.
    """
    cases = [
        case("entries/joined-on-one-line",
             container(HEADING + "\n" + ENTRY + " " + ENTRY),
             present=True, ambiguous=False, entries=0, malformed=True),
        case("entries/no-file-marker",
             container(HEADING + "\n- demo:widget: Use when demoing."),
             present=True, ambiguous=False, entries=0, malformed=True),
        case("entries/path-with-parentheses",
             container(HEADING + "\n- demo:widget: Use when demoing."
                       " (file: C:/Program Files (x86)/s/SKILL.md)"),
             present=True, ambiguous=False, entries=1),
        case("entries/description-mentions-file-marker",
             container(HEADING + "\n- demo:widget: Use when (file: x) is"
                       " shown. (file: C:/s/demo/SKILL.md)"),
             present=True, ambiguous=False, entries=1),
        case("entries/description-with-parens-and-dash",
             container(HEADING + "\n- demo:widget: Use when output is (done)"
                       " - next: retry. (file: C:/s/demo/SKILL.md)"),
             present=True, ambiguous=False, entries=1),
        case("entries/three-well-formed", container(block(entries=3)),
             present=True, ambiguous=False, entries=3),
    ]
    return cases + [dict(c, name=c["name"] + "/crlf",
                         text=c["text"].replace("\n", "\r\n"))
                    for c in cases]


CASES = build_cases() + entry_grammar_cases()

RUNNER_SNIPPET = r"""
$cases = Get-Content -Raw -LiteralPath '<CASES>' |
    ConvertFrom-Json
$out = @()
foreach ($c in $cases) {
    $r = Get-SkillReport $c.text
    $out += [ordered]@{
        name      = $c.name
        present   = [bool]$r.BlockPresent
        ambiguous = [bool]$r.Ambiguous
        entries   = @($r.Entries).Count
        malformed = [bool]$r.Malformed
    }
}
$out | ConvertTo-Json -Depth 4 -Compress
"""


def run_matrix(source=None):
    """One PowerShell process for the whole matrix."""
    text = source if source is not None else PROBE.read_text(encoding="utf-8")
    body = text[text.index(BODY_START):text.index(BODY_END)]
    tmp = Path(tempfile.mkdtemp(prefix="parallax-shapes-"))
    try:
        cases_file = tmp / "cases.json"
        cases_file.write_text(json.dumps(CASES), encoding="utf-8")
        script = tmp / "run.ps1"
        # utf-8-sig: the BOM is what makes Windows PowerShell 5.1 read the
        # file as UTF-8, same as the probe's own test module.
        script.write_text(
            body + "\n" + RUNNER_SNIPPET.replace("<CASES>",
                                                 str(cases_file)),
            encoding="utf-8-sig")
        proc = subprocess.run(
            [POWERSHELL, "-NoProfile", "-NonInteractive", "-File",
             str(script)],
            capture_output=True, text=True, timeout=300)
        if proc.returncode != 0:
            return None, proc.stdout + proc.stderr
        raw = proc.stdout.strip()
        if not raw:
            return None, "the host produced no output"
        parsed = json.loads(raw)
        return {r["name"]: r for r in parsed}, ""
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture(scope="module")
def report():
    got, err = run_matrix()
    assert got is not None, err
    assert len(got) == len(CASES), (
        f"{len(got)} results for {len(CASES)} cases - a case was dropped"
        " silently, which is the defect class this module exists for"
    )
    return got


@pytest.mark.parametrize("expected", CASES, ids=[c["name"] for c in CASES])
def test_generated_shape(report, expected):
    got = report[expected["name"]]
    assert got["present"] == expected["present"], got
    assert got["ambiguous"] == expected["ambiguous"], got
    assert got["entries"] == expected["entries"], got
    assert got["malformed"] == expected["malformed"], got


MUTANTS = {
    # The raw-versus-masked source choice. Offsets come from the MASKED
    # text; the body must be sliced from the RAW text so a quoted
    # delimiter is not a delimiter but real content still survives.
    "1-body-sliced-from-masked-text": (
        "$body = $text.Substring($bodyStart, $closeAt - $bodyStart)",
        "$body = $scan.Substring($bodyStart, $closeAt - $bodyStart)"),
    # The heading's search scope.
    "5-heading-searched-in-whole-text": (
        '$start = $body.IndexOf("### Available skills")',
        '$start = $text.IndexOf("### Available skills")'),
    # The silent-drop defence.
    "6-unreadable-entry-dropped-silently": (
        "$m = $rx.Match($trimmed)\n"
        "                if (-not $m.Success) {\n"
        "                    $malformed = $true",
        "$m = $rx.Match($trimmed)\n"
        "                if (-not $m.Success) {\n"
        "                    $malformed = $false"),
    "7-joined-entries-not-detected": (
        "if ($joined.IsMatch($trimmed)) {\n"
        "                    $malformed = $true",
        "if ($false) {\n"
        "                    $malformed = $true"),
    # Masking itself.
    "8-known-containers-not-masked": (
        "foreach ($name in $script:KnownContainers) {\n"
        "            $scan = Hide-KnownContainer $scan $name\n"
        "        }",
        "foreach ($name in $script:KnownContainers) { }"),
}

# DEFENCE IN DEPTH, tested under the fault it defends against.
#
# `Get-SkillReport` re-derives the skills container's ambiguity from its
# own marker counts at lines 222-241. No generated INPUT reaches those
# lines with a bad arrangement, because `skills_instructions` is itself a
# known container: the masking loop runs `Hide-KnownContainer` over it
# first, and that function throws on every arrangement other than exactly
# one correctly ordered pair. So the first matrix run reported all three
# arithmetic mutants as SURVIVING.
#
# My first treatment was to assert the shadow and measure what casts it.
# Sol refused it at round 8, and was right: that locks today's topology in
# place while proving nothing about whether the fallback WORKS. The
# arithmetic's own comment says it exists precisely so that a failure the
# earlier rule misses is still caught, so the way to test it is to inject
# the fault it defends against.
#
# THE FAULT MODEL, declared: the primary guard FAILS OPEN for
# `skills_instructions` only. Everything else is untouched, and this is
# test-only - the production script is not changed by this module.
FAIL_OPEN = (
    "foreach ($name in $script:KnownContainers) {\n"
    "            $scan = Hide-KnownContainer $scan $name\n"
    "        }",
    "foreach ($name in $script:KnownContainers) {\n"
    "            if ($name -ne 'skills_instructions') {\n"
    "                $scan = Hide-KnownContainer $scan $name\n"
    "            }\n"
    "        }")


def fail_open_source():
    source = PROBE.read_text(encoding="utf-8")
    old, new = FAIL_OPEN
    assert old in source, "the masking loop anchor moved"
    return source.replace(old, new, 1)


def test_the_fallback_classifies_correctly_when_the_guard_fails_open():
    """Step one of the fault model: with the primary guard bypassed, the
    UNCHANGED arithmetic must reach the same verdict on every shape.

    If this failed, the fallback would be decoration and the three mutants
    below would be untestable for a different and worse reason."""
    got, err = run_matrix(fail_open_source())
    assert got is not None, err
    wrong = []
    for expected in CASES:
        r = got.get(expected["name"])
        if r is None:
            wrong.append(f"{expected['name']} (no result)")
            continue
        for field in ("present", "ambiguous", "entries", "malformed"):
            if r[field] != expected[field]:
                wrong.append(f"{expected['name']}.{field}"
                             f" (expected {expected[field]}, got {r[field]})")
    assert not wrong, (
        "with Hide-KnownContainer bypassed for skills_instructions the"
        f" downstream arithmetic misclassified: {wrong[:5]}"
    )


FALLBACK_MUTANTS = {
    "2-close-before-open-accepted": (
        "$one = (($opens -eq 1) -and ($closes -eq 1) -and\n"
        "            ($closeAt -ge ($openAt + $open.Length)))",
        "$one = (($opens -eq 1) -and ($closes -eq 1))"),
    "3-only-openers-counted": (
        "$one = (($opens -eq 1) -and ($closes -eq 1) -and",
        "$one = (($opens -eq 1) -and ($closes -ge 1) -and"),
    "4-zero-and-one-collapsed": (
        "if (-not ($none -or $one)) { $ambiguous = $true }",
        "if (-not ($none -or $one -or ($opens -ge 1))) { $ambiguous = $true }"),
}


@pytest.mark.parametrize("mutant", sorted(FALLBACK_MUTANTS))
def test_every_fallback_defence_is_killed_under_the_fault(mutant):
    """Step two: each arithmetic mutant, applied ON TOP of the fault.

    Both edits together represent one real scenario - the primary guard
    fails open AND the fallback is missing this clause - which is the pair
    of failures the fallback exists to survive.
    """
    old, new = FALLBACK_MUTANTS[mutant]
    source = fail_open_source()
    assert old in source, f"{mutant}: anchor no longer present in the source"
    got, err = run_matrix(source.replace(old, new, 1))
    if got is None:
        print(f"{mutant} killed by: the mutated script failed to run"
              f" ({err.strip()[:120]})")
        return
    killers = []
    for expected in CASES:
        r = got.get(expected["name"])
        if r is None:
            killers.append(f"{expected['name']} (no result)")
            continue
        for field in ("present", "ambiguous", "entries", "malformed"):
            if r[field] != expected[field]:
                killers.append(f"{expected['name']}.{field}"
                               f" (expected {expected[field]}, got {r[field]})")
                break
        if len(killers) >= 3:
            break
    assert killers, (
        f"MUTANT SURVIVED under the fail-open fault: {mutant}. The"
        " fallback arithmetic is not doing the job its comment claims."
    )
    print(f"{mutant} killed by: {'; '.join(killers)}")


def test_the_primary_guard_still_refuses_directly():
    """The fault model is only meaningful if the guard normally holds.

    Measured over EVERY canonical arrangement, not a subset: the guard
    must accept exactly the shapes the fallback accepts and refuse
    exactly the ones it refuses, or the two layers disagree about what is
    ambiguous and the fault model tests the wrong thing.
    """
    probe = run_masking_directly()
    wrong = [c["name"] for c in MASKING_CASES
             if probe.get(c["name"]) != c["expected"]]
    assert not wrong, (
        f"the primary guard disagrees with the declared invariant on:"
        f" {wrong}"
    )


MASKING_SNIPPET = r"""
$cases = Get-Content -Raw -LiteralPath '<CASES>' | ConvertFrom-Json
$out = [ordered]@{}
foreach ($c in $cases) {
    try {
        [void](Hide-KnownContainer $c.text "skills_instructions")
        $out[$c.name] = "ok"
    } catch {
        $out[$c.name] = "threw"
    }
}
$out | ConvertTo-Json -Depth 3 -Compress
"""


def masking_cases():
    """Every canonical delimiter arrangement, for the direct probe.

    Round 9 found the earlier probe used a three-case subset, which cannot
    show that the primary guard refuses everything the fallback also
    refuses - only that it refuses three things.
    """
    out = []
    for opens in range(4):
        for closes in range(4):
            for order in ("opener-first", "closer-first"):
                text = arrangement(opens, closes, order, block(), "")
                ordered = order == "opener-first" or not (opens and closes)
                accepted = (opens == 0 and closes == 0) or (
                    opens == 1 and closes == 1 and ordered)
                out.append({"name": f"o{opens}c{closes}/{order}",
                            "text": text,
                            "expected": "ok" if accepted else "threw"})
    return out


MASKING_CASES = masking_cases()


def run_masking_directly():
    text = PROBE.read_text(encoding="utf-8")
    body = text[text.index(BODY_START):text.index(BODY_END)]
    subset = [{"name": c["name"], "text": c["text"]} for c in MASKING_CASES]
    tmp = Path(tempfile.mkdtemp(prefix="parallax-mask-"))
    try:
        cases_file = tmp / "cases.json"
        cases_file.write_text(json.dumps(subset), encoding="utf-8")
        script = tmp / "mask.ps1"
        script.write_text(
            body + "\n" + MASKING_SNIPPET.replace("<CASES>", str(cases_file)),
            encoding="utf-8-sig")
        proc = subprocess.run(
            [POWERSHELL, "-NoProfile", "-NonInteractive", "-File",
             str(script)],
            capture_output=True, text=True, timeout=300)
        assert proc.returncode == 0, proc.stdout + proc.stderr
        return json.loads(proc.stdout.strip())
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


@pytest.mark.parametrize("mutant", sorted(MUTANTS))
def test_every_defence_is_killed(mutant):
    old, new = MUTANTS[mutant]
    source = PROBE.read_text(encoding="utf-8")
    assert old in source, f"{mutant}: anchor no longer present in the source"
    got, err = run_matrix(source.replace(old, new, 1))
    if got is None:
        print(f"{mutant} killed by: the mutated script failed to run"
              f" ({err.strip()[:120]})")
        return
    killers = []
    for expected in CASES:
        r = got.get(expected["name"])
        if r is None:
            killers.append(f"{expected['name']} (no result)")
            continue
        for field in ("present", "ambiguous", "entries", "malformed"):
            if r[field] != expected[field]:
                killers.append(f"{expected['name']}.{field}"
                               f" (expected {expected[field]}, got {r[field]})")
                break
        if len(killers) >= 3:
            break
    assert killers, (
        f"MUTANT SURVIVED: {mutant}. No generated shape distinguishes the"
        " defended parser from the one without this clause - add the"
        " shape, do not relax the assertion."
    )
    print(f"{mutant} killed by: {'; '.join(killers)}")


def test_the_scope_claim_is_recorded():
    text = Path(__file__).read_text(encoding="utf-8")
    assert "Item 9's evidence is entirely PowerShell" in text
    assert "THE EVIDENCE IS THE MUTATION" in text


def test_every_oracle_field_has_a_declared_rule():
    """No expected value may rest on agreement with production.

    The generator computes four fields per case. Each needs a rule
    written above, or its expected value is a description of what the
    parser does. Three of the four were undeclared until cycle exchange
    13, which is diff round 1, which is why this test exists rather than
    a comment.
    """
    text = Path(__file__).read_text(encoding="utf-8")
    assert "BlockPresent is TRUE iff at least one OPENER survives" in text, (
        "the block-presence rule is undeclared")
    assert "Entries are read ONLY from the body of an unambiguous single" in text, (
        "entry suppression under ambiguity is undeclared")
    assert "The entry grammar, as a truth table rather than a regex" in text, (
        "the entry grammar is undeclared")
    assert "TWO shapes are non-ambiguous" in text, (
        "the ambiguity rule is undeclared")
    # And the addition is dated, so a later reader can tell a rule that
    # was decided in advance from one back-filled after the fact.
    assert "Invariants 6, 7 and 8 were added at CYCLE EXCHANGE 13" in text
    assert "Nothing about the code or the expected values changed when" in text
    # THE PLAN IS THE AUTHORITATIVE RECORD, and this module is not it.
    # Reading only this file would let the declarations be stripped from
    # the plan with the suite still green, which makes the claim "a test
    # fails if any declaration is removed" wider than the test. The
    # cross-vendor lane caught exactly that at diff round 2.
    plan = (REPO_ROOT / "docs" / "superpowers" / "plans"
            / "2026-08-11-budget-flake-generator.md").read_text(
                encoding="utf-8")
    assert "`BlockPresent` is TRUE iff at\n  least one OPENER survives masking" in plan, (
        "the block-presence rule is undeclared in the frozen plan")
    assert "Entries are read ONLY from the\n  body of an unambiguous single ordered pair" in plan, (
        "entry suppression under ambiguity is undeclared in the frozen plan")
    assert "The entry grammar, as a truth\n  table rather than a regex" in plan, (
        "the entry grammar is undeclared in the frozen plan")
    assert plan.count("**ADDED at CYCLE EXCHANGE 13, which is DIFF ROUND 1.**") == 3, (
        "each of the three additions has to carry its own dated marker")


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
