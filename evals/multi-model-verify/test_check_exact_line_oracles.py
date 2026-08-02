"""Mutation tests for evals/tools/check_exact_line_oracles.py (Task 11,
2026-08-01 lane-credential-and-lock plan).

The checker exists to catch "discard blank lines from splitlines(), then
require exactly one survivor" - a defect three independent sweeps each
missed at least one instance of before it was found mechanically. A
checker that cannot fail is the exact defect this plan exists to prevent,
so this module proves it in three directions: the bad filter-then-count
idiom must FAIL it, an intentional multi-record blank filter (never
tested for length one) must PASS it, and the real strict regex helper
(evals/tools/exact_line.py) must PASS it.
"""
import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


def _load_checker_module():
    path = REPO / "evals" / "tools" / "check_exact_line_oracles.py"
    spec = importlib.util.spec_from_file_location("check_exact_line_oracles", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


checker = _load_checker_module()


def test_bad_filter_then_count_idiom_is_flagged():
    """Direction 1: the exact defect idiom - discard blanks, then assert
    len == 1 - must be caught."""
    source = (
        "def assert_classification(proc):\n"
        "    lines = [l for l in proc.stdout.splitlines() if l.strip()]\n"
        "    assert len(lines) == 1, lines\n"
        "    return lines[0]\n"
    )
    violations = checker.find_violations(source, filename="bad.py")
    assert violations == [(2, "lines")], violations


def test_bad_filter_then_count_idiom_with_not_equal_test_is_flagged():
    """The same defect written as `if len(lines) != 1: raise ...` (the
    shape actually used at evals/multi-model-verify/test_lock_protocol_
    live.py before Task 11) must also be caught."""
    source = (
        "def measure(proc):\n"
        "    lines = [ln for ln in proc.stdout.splitlines() if ln.strip()]\n"
        "    if len(lines) != 1:\n"
        "        raise AssertionError('nope')\n"
        "    return lines[0]\n"
    )
    violations = checker.find_violations(source, filename="bad2.py")
    assert violations == [(2, "lines")], violations


def test_bad_filter_then_count_idiom_with_ne_empty_string_filter_is_flagged():
    """The other named risky filter shape - `!= \"\"` instead of bare
    truthiness - must also be caught."""
    source = (
        "def assert_classification(proc):\n"
        "    lines = [l for l in proc.stdout.splitlines() if l != '']\n"
        "    assert len(lines) == 1\n"
        "    return lines[0]\n"
    )
    violations = checker.find_violations(source, filename="bad3.py")
    assert violations == [(2, "lines")], violations


def test_intentional_multi_record_blank_filter_is_not_flagged():
    """Direction 2: a comprehension that filters blank lines to build a
    genuine multi-record result - never tested for length one - is
    legitimate and must NOT be flagged."""
    source = (
        "def parse_records(text):\n"
        "    lines = [l for l in text.splitlines() if l.strip()]\n"
        "    return [json.loads(l) for l in lines]\n"
    )
    violations = checker.find_violations(source, filename="ok.py")
    assert violations == [], violations


def test_strict_regex_helper_is_not_flagged():
    """Direction 3: the real shared helper this plan introduced
    (evals/tools/exact_line.py) must PASS - it uses the anchored regex,
    never the filter-then-count idiom."""
    source = (REPO / "evals" / "tools" / "exact_line.py").read_text(encoding="utf-8")
    violations = checker.find_violations(source, filename="exact_line.py")
    assert violations == [], violations


def test_different_scopes_do_not_cross_contaminate():
    """A risky-shaped comprehension in one function and an unrelated
    length-one test of a same-named variable in a SIBLING function must
    not be flagged - the two are different lexical scopes."""
    source = (
        "def build(text):\n"
        "    lines = [l for l in text.splitlines() if l.strip()]\n"
        "    return lines\n"
        "\n"
        "def check(lines):\n"
        "    assert len(lines) == 1\n"
    )
    violations = checker.find_violations(source, filename="scopes.py")
    assert violations == [], violations


def test_check_repository_walks_a_directory_tree(tmp_path):
    """check_repository() (the whole-repo driver main() uses) must find a
    violation in a nested file and report it with its real path."""
    bad_dir = tmp_path / "pkg"
    bad_dir.mkdir()
    bad_file = bad_dir / "bad.py"
    bad_file.write_text(
        "def f(proc):\n"
        "    lines = [l for l in proc.stdout.splitlines() if l.strip()]\n"
        "    assert len(lines) == 1\n",
        encoding="utf-8",
    )
    findings = checker.check_repository(tmp_path)
    assert findings == [(bad_file, 2, "lines")], findings


def test_check_repository_clean_tree_reports_nothing(tmp_path):
    good_file = tmp_path / "good.py"
    good_file.write_text(
        "def f(text):\n"
        "    return [l for l in text.splitlines() if l.strip()]\n",
        encoding="utf-8",
    )
    findings = checker.check_repository(tmp_path)
    assert findings == [], findings


def test_module_docstring_states_the_syntactic_limit():
    """Step 4: the checker's own docstring must state that it catches a
    SYNTACTIC class and must never be described as proving the class is
    gone."""
    doc = checker.__doc__ or ""
    assert "SYNTACTIC" in doc
    assert "semantically equivalent" in doc
