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
#   2. Exactly one opener and one closer, closer after opener, is the ONLY
#      unambiguous shape. Every other arrangement - none, opener-only,
#      closer-only, two of either, closer before opener - is AMBIGUOUS.
#      "None" is the one non-ambiguous zero case.
#   3. The heading is honoured only INSIDE the container body. A heading
#      anywhere else supplies no entries.
#   4. Known containers are MASKED before the scan, so a delimiter quoted
#      inside one is not a delimiter. Masking is space-for-character, so
#      every offset outside it is unchanged.
#   5. Every entry-looking line is audited. A line that fails the grammar
#      sets Malformed rather than being dropped in silence.
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


def build_cases():
    cases = []

    # Invariant 2: the opener/closer arrangement matrix.
    arrangements = {
        "none": ("plain prompt text", False, False),
        "one-pair": (container(block()), True, False),
        "opener-only": (OPEN + "\n" + block(), True, True),
        "closer-only": (block() + "\n" + CLOSE, False, True),
        "two-openers": (OPEN + "\n" + OPEN + "\n" + block() + "\n" + CLOSE,
                        True, True),
        "two-closers": (OPEN + "\n" + block() + "\n" + CLOSE + "\n" + CLOSE,
                        True, True),
        "closer-before-opener": (CLOSE + "\n" + block() + "\n" + OPEN,
                                 True, True),
        "two-pairs": (container(block()) + "\n" + container(block()),
                      True, True),
    }
    for name, (text, present, ambiguous) in arrangements.items():
        entries = 1 if (present and not ambiguous) else 0
        cases.append(case(f"arrangement/{name}", text, present=present,
                          ambiguous=ambiguous, entries=entries))

    # Invariant 3: heading placement.
    cases.append(case(
        "heading/outside-only",
        HEADING + "\n" + ENTRY + "\n" + container("no heading here"),
        present=True, ambiguous=False, entries=0))
    cases.append(case(
        "heading/both",
        HEADING + "\n" + ENTRY + "\n" + container(block()),
        present=True, ambiguous=False, entries=1))
    cases.append(case(
        "heading/absent",
        container(ENTRY),
        present=True, ambiguous=False, entries=0))

    # Invariant 4: a delimiter QUOTED inside a known container is masked
    # and is not a delimiter. <INSTRUCTIONS> carries AGENTS.md verbatim.
    quoted = ("<INSTRUCTIONS>\nNever emit " + OPEN + " yourself.\n"
              "</INSTRUCTIONS>\n" + container(block()))
    cases.append(case("masking/quoted-opener-in-instructions", quoted,
                      present=True, ambiguous=False, entries=1))
    quoted_pair = ("<INSTRUCTIONS>\nBad: " + OPEN + " ... " + CLOSE + "\n"
                   "</INSTRUCTIONS>\n" + container(block()))
    cases.append(case("masking/quoted-pair-in-instructions", quoted_pair,
                      present=True, ambiguous=False, entries=1))

    # Invariant 5: every entry-looking line is audited.
    cases.append(case(
        "entries/joined-on-one-line",
        container(HEADING + "\n" + ENTRY + " " + ENTRY),
        present=True, ambiguous=False, entries=0, malformed=True))
    cases.append(case(
        "entries/no-file-marker",
        container(HEADING + "\n- demo:widget: Use when demoing."),
        present=True, ambiguous=False, entries=0, malformed=True))
    cases.append(case(
        "entries/path-with-parentheses",
        container(HEADING + "\n- demo:widget: Use when demoing."
                  " (file: C:/Program Files (x86)/s/SKILL.md)"),
        present=True, ambiguous=False, entries=1))
    cases.append(case(
        "entries/description-mentions-file-marker",
        container(HEADING + "\n- demo:widget: Use when (file: x) is shown."
                  " (file: C:/s/demo/SKILL.md)"),
        present=True, ambiguous=False, entries=1))
    cases.append(case(
        "entries/description-with-parens-and-dash",
        container(HEADING + "\n- demo:widget: Use when output is (done)"
                  " - next: retry. (file: C:/s/demo/SKILL.md)"),
        present=True, ambiguous=False, entries=1))
    cases.append(case(
        "entries/three-well-formed",
        container(block(entries=3)),
        present=True, ambiguous=False, entries=3))

    # Line endings, applied across the whole set.
    crlf = [dict(c, name=c["name"] + "/crlf",
                 text=c["text"].replace("\n", "\r\n")) for c in cases]
    return cases + crlf


CASES = build_cases()

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

    Measured, not assumed: Hide-KnownContainer refuses the bad
    arrangements and accepts the good one.
    """
    probe = run_masking_directly()
    assert probe["closer-before-opener"] == "threw", probe
    assert probe["two-openers"] == "threw", probe
    assert probe["one-pair"] == "ok", probe


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


def run_masking_directly():
    text = PROBE.read_text(encoding="utf-8")
    body = text[text.index(BODY_START):text.index(BODY_END)]
    subset = [c for c in CASES
              if c["name"] in ("arrangement/closer-before-opener",
                               "arrangement/two-openers",
                               "arrangement/one-pair")]
    subset = [dict(c, name=c["name"].split("/", 1)[1]) for c in subset]
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


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
