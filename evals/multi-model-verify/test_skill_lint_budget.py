"""Backlog item 19: the SKILL.md token budget is enforced, not announced.

Tier 2b. No model calls, no network.

The vendored linter warned above ~5000 tokens and never failed, so the
number went unowned across several releases while the file grew. This
module pins the three-band behaviour, its four boundaries, and the
vendoring obligations that come with editing a vendored file.
"""

import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LINT_PATH = REPO_ROOT / "evals" / "tools" / "skill_lint.py"


def load_lint():
    spec = importlib.util.spec_from_file_location("skill_lint", LINT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def make_skill(root, body_tokens):
    """A minimal valid skill whose BODY estimates to exactly body_tokens.

    The linter's estimate is len(body) // 4 over the text after the
    frontmatter, so the body is padded to a known character count. Built
    rather than hand-written: a fixture whose size is approximate cannot
    test a boundary.
    """
    d = root / "sized-skill"
    d.mkdir(parents=True, exist_ok=True)
    (d / "references").mkdir(exist_ok=True)
    (d / "references" / "note.md").write_text("note\n", encoding="utf-8")
    front = ("---\n"
             "name: sized-skill\n"
             "description: Use when the body size is what is under test,"
             " for boundary cases only.\n"
             "---\n")
    head = "\n# Sized\n\n## When to use\n\nUse when testing.\n\n"
    pad = body_tokens * 4 - len(head)
    assert pad > 0, "requested body is smaller than the fixed header"
    body = head + ("x" * pad)
    (d / "SKILL.md").write_text(front + body, encoding="utf-8")
    return d


def run_lint(skill_dir):
    proc = subprocess.run(
        [sys.executable, str(LINT_PATH), str(skill_dir), "--strict"],
        capture_output=True, text=True, timeout=120)
    return proc.returncode, proc.stdout + proc.stderr


class TestTheThreeBands:
    """Mutually exclusive outcomes. A body is clean, or warned, or failed."""

    def test_at_the_soft_target_it_is_clean(self, tmp_path):
        mod = load_lint()
        _, out = run_lint(make_skill(tmp_path, mod.BODY_TOKEN_BUDGET))
        assert "tokens" not in out, out

    def test_one_token_over_the_soft_target_warns(self, tmp_path):
        mod = load_lint()
        code, out = run_lint(make_skill(tmp_path, mod.BODY_TOKEN_BUDGET + 1))
        assert code == 0, "a soft-band body must not fail the gate"
        assert "WARN" in out and "hard ceiling" in out, out
        assert "ERROR" not in out, "the bands must be mutually exclusive"

    def test_at_the_ceiling_it_still_only_warns(self, tmp_path):
        mod = load_lint()
        code, out = run_lint(make_skill(tmp_path, mod.BODY_TOKEN_CEILING))
        assert code == 0, "the ceiling itself is the last passing value"
        assert "WARN" in out and "ERROR" not in out, out

    def test_one_token_over_the_ceiling_is_an_error(self, tmp_path):
        mod = load_lint()
        code, out = run_lint(make_skill(tmp_path, mod.BODY_TOKEN_CEILING + 1))
        assert code == 1, "over the ceiling must FAIL, not print"
        assert "over the hard ceiling" in out, out
        # Exactly one band fires. A body that both warns and errors gives
        # a reader two different instructions about the same number.
        assert out.count("tokens") == 1, out

    def test_the_error_names_both_legitimate_remedies(self, tmp_path):
        mod = load_lint()
        _, out = run_lint(make_skill(tmp_path, mod.BODY_TOKEN_CEILING + 1))
        assert "references/" in out, "relocation must be named"
        assert "raise the ceiling deliberately" in out, (
            "a deliberate, recorded ceiling change must be named"
        )
        assert "Deleting text a review asked for is not one of them" in out, (
            "item 19 forbids treating the ceiling as licence to cut"
            " load-bearing text; the failure message has to say so"
        )


class TestTheOldImplementationCouldNotFail:
    """The fail-first proof, run against the pre-change code itself.

    Written because 'we added enforcement' is a claim about a diff. This
    reconstructs the vendored behaviour - a warning and nothing else - and
    shows it passing a body far over the ceiling. If this ever fails, the
    delta being described is not the delta that exists.
    """

    def test_a_warning_only_lint_passes_an_over_ceiling_body(self, tmp_path):
        mod = load_lint()
        oversized = mod.BODY_TOKEN_CEILING + 5000
        skill = make_skill(tmp_path, oversized)
        body = (skill / "SKILL.md").read_text(encoding="utf-8")
        body = re.sub(r"^---\n.*?\n---\n", "", body, flags=re.S)
        est = len(body) // 4
        assert est > mod.BODY_TOKEN_CEILING, "fixture is not over the ceiling"
        # The vendored rule, verbatim in behaviour: warn, never error.
        errors, warnings = [], []
        if est > 5000:
            warnings.append("over budget")
        assert not errors and warnings, (
            "the vendored implementation produced no error for a body"
            f" {est - mod.BODY_TOKEN_CEILING} tokens over today's ceiling"
        )
        # And the shipped implementation does fail it.
        code, out = run_lint(skill)
        assert code == 1 and "over the hard ceiling" in out, out


class TestVendoringObligations:
    """Editing a vendored file carries paperwork, and the paperwork is
    part of the change rather than a nicety: the header instructs the next
    maintainer to re-diff, and a stale header sends them to the wrong
    baseline."""

    def test_the_header_no_longer_claims_to_be_unmodified(self):
        text = LINT_PATH.read_text(encoding="utf-8")
        # The phrase survives ONCE, inside its own retraction. A plain
        # `not in` would have failed on the retraction that fixes it,
        # which is a test that punishes the correction it asked for.
        assert text.count("unmodified except this provenance header") == 1, (
            "the phrase may appear only where it is being retracted"
        )
        assert ('previous\n"unmodified except this provenance header" claim'
                " was true until that\nchange and is false afterwards."
                ) in text, (
            "the retraction has to say when the old claim stopped being"
            " true, not merely stop making it"
        )
        assert "LOCAL DELTA, and there is exactly one." in text
        assert "BODY_TOKEN_CEILING" in text

    def test_the_re_diff_is_recorded_with_its_scope(self):
        text = LINT_PATH.read_text(encoding="utf-8")
        assert "Re-diff performed 2026-08-11" in text
        # The scope limit is the honest part: this was diffed against the
        # imported copy in this repo, not against upstream's current HEAD.
        assert ("That is a diff against the IMPORTED copy,\nnot against"
                " upstream's current HEAD, which was not fetched.") in text

    def test_the_documented_checks_and_exit_codes_match_behaviour(self):
        text = LINT_PATH.read_text(encoding="utf-8")
        assert "ERROR above BODY_TOKEN_CEILING" in text, (
            "the checks list still promised only a warning"
        )
        assert "A body over BODY_TOKEN_CEILING is an ERROR, so it exits 1" in text

    def test_the_policy_is_declared_global_and_non_rebasing(self):
        text = LINT_PATH.read_text(encoding="utf-8")
        assert "GLOBAL LINTER POLICY, not a per-skill setting" in text
        assert "These do NOT rebase automatically." in text, (
            "without this the next release cites this raise as precedent"
        )


def test_the_shipped_skill_is_inside_the_bands():
    """The release's own file, measured. Not a boundary case: the point of
    the exercise was that this number is now owned by someone."""
    mod = load_lint()
    code, out = run_lint(REPO_ROOT / "skills" / "multi-model-verify")
    assert code == 0, out
    m = re.search(r"roughly (\d+) tokens", out)
    if m:
        assert int(m.group(1)) <= mod.BODY_TOKEN_CEILING, out


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
