"""Contract pins for the Flash implementer lane (agents/flash-implementer.md).

Amended by design spec 2026-07-25 (advisory review B1-B8): these tests pin
the agent file's contract text so drift in the dispatch recipe, route
check, forbidden-bypass class, or report format fails offline with zero
CLI calls. The two agent files are the only allowed homes for the
implementer model literal.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FLASH = REPO / "agents" / "flash-implementer.md"
CLASSIC = REPO / "agents" / "implementer.md"
CANONICAL_ID = "gemini-3.6-flash-medium"
SHARED_START = "<!-- shared-contract:start -->"
SHARED_END = "<!-- shared-contract:end -->"


def _read(p):
    return p.read_text(encoding="utf-8")


def _frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    assert m, "missing frontmatter"
    return m.group(1)


def test_flash_frontmatter_pins_model_and_tools():
    fm = _frontmatter(_read(FLASH))
    assert re.search(r"^model: haiku$", fm, re.MULTILINE)
    m = re.search(r"^tools: (.+)$", fm, re.MULTILINE)
    assert m, "tools allowlist missing"
    tools = [t.strip() for t in m.group(1).split(",")]
    assert sorted(tools) == ["Bash", "Glob", "Grep", "Read"]


def test_flash_dispatch_contract():
    body = _read(FLASH)
    assert "--model " + CANONICAL_ID in body
    assert "--add-dir" in body
    assert "--log-file" in body
    assert "AGY-TASK-BRIEF.md" in body
    # stdin is probed-dead in print mode; the body must not suggest it
    assert "stdin" not in body.lower() or "does not reach" in body.lower()


def test_flash_route_check_strings():
    body = _read(FLASH)
    assert 'Print mode: starting' in body
    assert 'model="' + CANONICAL_ID + '"' in body
    assert "Propagating selected model override" in body
    assert "requested and propagated" in body
    assert "used and confirmed" not in body.replace(
        'never "used and confirmed"', "")
    # log/tree corroboration rule (advisory review B2 amendment)
    assert "every path git status reports changed must appear in the agy log" in body.lower()


def test_flash_preflight_pins():
    body = _read(FLASH)
    assert "agy models" in body
    assert "trustedWorkspaces" in body
    assert "allow rule" in body  # settings-rule absence assertion


def test_flash_forbidden_bypass_class():
    body = _read(FLASH)
    assert "--dangerously-skip-permissions" in body
    idx = body.find("--dangerously-skip-permissions")
    window = body[max(0, idx - 200):idx + 200].lower()
    assert "never" in window or "forbidden" in window
    assert "persisted" in body and "settings" in body


def test_flash_report_headings():
    body = _read(FLASH)
    for heading in ("**STATUS:**", "**ROUTE:**", "**FILES CHANGED:**",
                    "**VERIFICATION:**", "**DEVIATIONS:**"):
        assert heading in body, heading
    # the four shared headings are pinned in BOTH files so a unilateral
    # rename in implementer.md cannot pass the suite (ROUTE is
    # lane-specific to the flash file)
    classic = _read(CLASSIC)
    for heading in ("**STATUS:**", "**FILES CHANGED:**",
                    "**VERIFICATION:**", "**DEVIATIONS:**"):
        assert heading in classic, heading


def _shared_block(text, path):
    assert SHARED_START in text and SHARED_END in text, (
        "missing shared-contract markers in " + str(path))
    return text.split(SHARED_START)[1].split(SHARED_END)[0]


def test_shared_contract_parity():
    # byte-identical shared block; ROUTE is lane-specific and lives
    # outside the block (spec section 1)
    assert _shared_block(_read(FLASH), FLASH) == _shared_block(
        _read(CLASSIC), CLASSIC)


def test_classic_lane_note_retired_stale_claim():
    body = _read(CLASSIC)
    assert "Nothing else in the plugin references" not in body
    assert "flash-implementer" in body


SWEEP_GLOBS = [
    "skills/**/*.md", "commands/*.md", "tools/*.ps1", "hooks/*",
    "evals/**/*.py", "evals/**/*.json", "evals/**/*.ps1",
    "README.md", "CLAUDE.md", "agents/*.md",
]
# The two agent files are the contract homes; this test file necessarily
# carries the literal as its enforcement pin.
ALLOWED = {FLASH.resolve(), CLASSIC.resolve(),
           Path(__file__).resolve()}


def test_flash_literal_single_source():
    offenders = []
    for pattern in SWEEP_GLOBS:
        for p in REPO.glob(pattern):
            if p.resolve() in ALLOWED:
                continue
            if "gemini-3.6-flash" in p.read_text(encoding="utf-8",
                                                 errors="replace"):
                offenders.append(str(p))
    assert offenders == []


def test_sonnet_implementer_literals_removed():
    readme = _read(REPO / "README.md")
    assert "currently `model: sonnet`" not in readme
    # absence pins alone are vacuous against line-wrapped source; the
    # presence pins below are the real oracles for Task 3's rewrites
    assert "`haiku`/`opus` are drop-ins" not in readme
    assert "any Claude tier is a drop-in" in readme
    fpf = _read(REPO / "skills" / "multi-model-verify" / "references"
                / "frozen-plan-format.md")
    assert "Sonnet 5" not in fpf
    assert "the pinned lane in `agents/`" in fpf
