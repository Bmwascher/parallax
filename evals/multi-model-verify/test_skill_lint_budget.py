"""Backlog item 19: the SKILL.md token budget is enforced, not announced.

Tier 2b. No model calls, no network.

The vendored linter warned above ~5000 tokens and never failed, so the
number went unowned across several releases while the file grew. This
module pins the three-band behaviour, its four boundaries, and the
vendoring obligations that come with editing a vendored file.
"""

import hashlib
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LINT_PATH = REPO_ROOT / "evals" / "tools" / "skill_lint.py"
# The linter as it stood BEFORE this release added enforcement, frozen so
# the fail-first proof can execute it rather than describe it.
PRE_CHANGE_PATH = (Path(__file__).resolve().parent / "fixtures"
                   / "skill_lint_pre_change.py")


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


def run_lint(skill_dir, lint_path=None):
    proc = subprocess.run(
        [sys.executable, str(lint_path or LINT_PATH), str(skill_dir),
         "--strict"],
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
    """The fail-first proof, EXECUTED against the pre-change code.

    The plan requires a test proving the PRE-CHANGE implementation does
    not fail above the ceiling. Two earlier attempts did not satisfy it.
    The first restated the old rule inline and called itself a fail-first
    proof; the second kept the restatement and merely admitted in its
    docstring that it could not fail. The cross-vendor lane refused both,
    the second time on the ground that an honest description of a missing
    measurement is still a missing measurement.

    So the pre-change file is frozen as a fixture and RUN. It is
    `evals/tools/skill_lint.py` at `dd0db13`, the last commit before the
    enforcement landed, and both halves below are subprocess runs against
    the same oversized skill:

    - the pre-change linter warns and EXITS 0;
    - the shipped linter ERRORS and exits 1.

    Either half fails if the delta this release claims is not the delta
    that exists.
    """

    def test_the_frozen_pre_change_linter_is_the_file_it_claims_to_be(self):
        """A pre-change implementation that drifts is not one.

        The banner is prose and the copied text is evidence, so only the
        copied text is hashed.
        """
        text = PRE_CHANGE_PATH.read_text(encoding="utf-8")
        marker = "# " + "-" * 75 + "\n"
        parts = text.split(marker, 2)
        assert len(parts) == 3, "the frozen fixture's banner is malformed"
        body = parts[2].encode("utf-8")
        assert len(body) == 16065, f"fixture body is {len(body)} bytes"
        assert hashlib.sha256(body).hexdigest() == (
            "23172735f1fe7d5e0fbfe8ba2d44b770a3f6264d0ec81e0bb5b39d1de2954745"
        ), "the frozen pre-change linter has been edited"
        # And it really is pre-change: no ceiling, and the number it did
        # carry was the unenforced 5000.
        assert "BODY_TOKEN_CEILING" not in parts[2]
        assert "5000" in parts[2]

    def test_the_pre_change_linter_passes_an_over_ceiling_body(self, tmp_path):
        mod = load_lint()
        # Round-7 correction: the boundary that matters is ABOVE 5500,
        # not above 5250.
        oversized = mod.BODY_TOKEN_CEILING + 5000
        skill = make_skill(tmp_path, oversized)
        code, out = run_lint(skill, lint_path=PRE_CHANGE_PATH)
        assert code == 0, (
            "the pre-change linter FAILED an over-ceiling body, so the"
            f" enforcement this release claims to add already existed:\n{out}"
        )
        assert "ERROR" not in out, out
        # It did notice; it just could not act. That is the defect.
        assert "token" in out.lower(), (
            "the pre-change linter said nothing at all about the body size,"
            f" so this fixture is not exercising the old rule:\n{out}"
        )

    def test_the_shipped_linter_fails_the_same_body(self, tmp_path):
        mod = load_lint()
        skill = make_skill(tmp_path, mod.BODY_TOKEN_CEILING + 5000)
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
        assert ('the claim this header used to make,\n'
                '   "unmodified except this provenance header", was true'
                " until that\n   change and is false afterwards.") in text, (
            "the retraction has to say when the old claim stopped being"
            " true, not merely stop making it"
        )
        assert "LOCAL DELTA, and there is exactly one." in text
        assert "BODY_TOKEN_CEILING" in text

    def test_the_re_diff_is_recorded_with_its_scope(self):
        text = LINT_PATH.read_text(encoding="utf-8")
        assert "RE-DIFF PERFORMED 2026-08-11, TWICE, AGAINST TWO DIFFERENT" in text
        # Both baselines have to be named, because they answer different
        # questions: the imported copy says what THIS repo changed, and
        # live upstream says whether upstream moved underneath it. The
        # first release of this header did only the former and said so;
        # the diff debate ruled that honest disclosure does not discharge
        # a frozen task, so the fetch was performed and pinned here.
        assert "1. Against this file's imported state at `acbf045`:" in text
        assert "Against LIVE UPSTREAM, fetched the same day from" in text
        assert "ca8e5b3c56e51e336449a99d79b42b45ea690b86" in text, (
            "the upstream commit the comparison was made against has to be"
            " named, or the next maintainer cannot tell what moved since"
        )
        assert "gives exactly ONE hunk" in text
        # And the claim must be dated rather than standing, because it
        # decays the moment upstream commits again.
        assert "this statement is dated, not standing." in text

    def test_the_two_thresholds_are_pinned_to_their_literal_values(self):
        """A silent renumber of either constant must break a test.

        The header says these numbers do NOT rebase automatically, and
        the whole point of item 19 is that an unowned number drifts. Every
        other test in this module reads the constants through the module,
        so all of them would follow a renumber quietly. This one does not.
        Changing either value here is the deliberate, recorded act the
        policy demands.

        RAISED 2026-08-31, backlog item 32 task 3: routing both codex
        dispatch sites in SKILL.md through tools/dispatch-detached.ps1
        measured 6225 (test_the_2026_08_31_item32_raise_is_recorded_and_justified
        below carries the full reason).
        """
        mod = load_lint()
        assert mod.BODY_TOKEN_BUDGET == 6250
        assert mod.BODY_TOKEN_CEILING == 6500
        # The four boundaries the plan froze, stated as literals so the
        # band edges are readable without evaluating arithmetic.
        assert (6250, 6251, 6500, 6501) == (
            mod.BODY_TOKEN_BUDGET,
            mod.BODY_TOKEN_BUDGET + 1,
            mod.BODY_TOKEN_CEILING,
            mod.BODY_TOKEN_CEILING + 1,
        )
        text = LINT_PATH.read_text(encoding="utf-8")
        assert "BODY_TOKEN_BUDGET = 6250" in text
        assert "BODY_TOKEN_CEILING = 6500" in text

    def test_the_2026_08_31_item32_raise_is_recorded_and_justified(self):
        """Backlog item 32, task 3. The tool-based rewrite of SKILL.md's two
        codex dispatch sites (routed through tools/dispatch-detached.ps1)
        measured 6225 by the header's own estimate, over the prior 5500
        ceiling. A raise with no test is how the next raise goes unnoticed,
        so the date, the number, and the reason live here rather than only
        in the comment beside the constants.

        The reason is NOT that the rewrite failed to shrink anything: it
        replaced five copied dispatch snippets with one tool. It is that
        the per-site test (test_each_codex_call_is_launched_through_the_tool)
        requires the full wrapper body, the launch command, the poll
        command, and the whole four-clause exit-code sentence inside EACH
        call site's own section - round 6's finding was that a global count
        let one site stay foreground undetected - so the fresh and resumed
        dispatches each carry a full copy of that shape rather than sharing
        one.
        """
        mod = load_lint()
        assert mod.BODY_TOKEN_BUDGET == 6250
        assert mod.BODY_TOKEN_CEILING == 6500
        text = LINT_PATH.read_text(encoding="utf-8")
        assert "RAISED 2026-08-31 (backlog item 32, task 3)." in text
        assert (
            "own command (`t.split('---',2)[2]`, `len(body)//4`) after routing both\n"
            "# codex dispatch sites through tools/dispatch-detached.ps1: 6225."
        ) in text
        assert (
            "so the fresh and resumed dispatches each carry their\n"
            "# own copy of that shape; a global count would have let one site stay\n"
            "# foreground undetected (round 6's finding), so the duplication is the\n"
            "# point, not slack to trim."
        ) in text

    def test_the_documented_checks_and_exit_codes_match_behaviour(self):
        text = LINT_PATH.read_text(encoding="utf-8")
        assert "ERROR above BODY_TOKEN_CEILING" in text, (
            "the checks list still promised only a warning"
        )
        assert "A body over BODY_TOKEN_CEILING is an ERROR, so it exits 1" in text

    def test_the_third_party_notice_describes_the_delta(self):
        """The notice is the Apache-2.0 section 4(b) statement of changes.

        Nothing pinned it before, which is how it stayed on "unmodified
        except the provenance header" for a whole release after the delta
        landed. The file header and this notice are two separate promises
        to two separate readers, and only one of them was being kept.
        """
        notice = (REPO_ROOT / "evals" / "tools"
                  / "LICENSE-THIRD-PARTY.md").read_text(encoding="utf-8")
        assert "BODY TOKEN BUDGET ENFORCEMENT" in notice, (
            "the notice does not state the change it is required to state")
        assert "ca8e5b3c56e51e336449a99d79b42b45ea690b86" in notice, (
            "the notice does not name the upstream commit it was compared"
            " against")
        # The phrase appears exactly TWICE and both are correct: once as a
        # live claim about skill_scanner.py, which really is unmodified,
        # and once quoted inside skill_lint.py's own retraction of it. A
        # plain `not in` would fail on the retraction that fixes the
        # defect, which is a test that punishes the correction it asked
        # for; the header pin above has the same shape for the same
        # reason.
        assert notice.count("unmodified except the provenance header") == 2, (
            "one live use for skill_scanner and one inside skill_lint's"
            " retraction; any other count means a tool's status changed"
            " without this notice being updated"
        )
        assert "skill_scanner.py` — unmodified" in notice
        assert "was false from then until this correction" in notice, (
            "the retraction has to say when the old claim stopped being"
            " true, not merely stop making it"
        )

    def test_the_frozen_fixture_is_covered_by_the_notice(self):
        """It is Apache-2.0 code sitting outside the directory the notice
        scopes itself to, so it has to be named or it is uncovered."""
        notice = (REPO_ROOT / "evals" / "tools"
                  / "LICENSE-THIRD-PARTY.md").read_text(encoding="utf-8")
        rel = "evals/multi-model-verify/fixtures/skill_lint_pre_change.py"
        assert rel in notice, "the frozen fixture is not named in the notice"
        assert "It must never be updated" in notice
        # And the notice must claim NEITHER more coverage nor more
        # freedom than exists. Two drafts got this wrong in opposite
        # directions: "its content is hash-pinned" claimed the whole file,
        # then "banner edits break no pin" forgot that the split asserts
        # on the separator lines.
        assert "the COPIED TEXT BELOW THE BANNER" in notice, (
            "the notice has to say WHICH part of the fixture is pinned")
        assert "Banner PROSE is\nexcluded from the hash" in notice
        assert ("requires exactly three parts, so editing either separator"
                " fails a\nstructural assertion") in notice, (
            "the notice has to say the separator lines are not free to edit")

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
