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
CANONICAL_ID = "gemini-3.8-flash-high"
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
    # agy's own scoped mode opens file edits in print mode and leaves
    # command execution denied (measured 2026-09-13 on agy 1.2.2: without
    # it every write is soft-denied, with it a run_command call still
    # is). It is the ONE switch between a lane that blocks on every
    # dispatch and one that lands edits, and it is on the dispatch line
    # where every reader sees it, unlike a persisted allow rule.
    assert "--mode accept-edits" in body
    assert body.count("--mode accept-edits") >= 2
    # Fable R1 finding 1 (2026-09-13): the two pins above are satisfied
    # by the prose alone, so the flag must be locked to the ONE physical
    # dispatch line, between the model and the workspace binding
    assert ("--model " + CANONICAL_ID + " --mode accept-edits --add-dir"
            ) in body
    assert "command execution stays denied" in body
    # a Git-Bash /c/... log path produced NO log file (measured
    # 2026-09-13); the log is where the route evidence lives
    assert "Windows spelling" in body
    # unique-suffix brief name + full lifecycle, pinned by exact sentence
    # fragments so a regression cannot pass on loose keywords
    # (Sol check-off round 2, finding 3)
    assert "AGY-TASK-BRIEF-" in body
    assert "sole transient exception" in body.lower()
    assert "the dispatch log file's basename" in body
    assert "on success, failure, and interruption alike" in body
    # brief-borne no-commands line (Sol diff-debate F1: a task whose text
    # carries a verification command otherwise soft-denies in print mode
    # and blocks the green path - live-verified 2026-07-25)
    assert ("Do not run commands or attempt verification - the wrapper "
            "runs all verification after you finish; your only job is "
            "the file edits.") in body
    # stdin is probed-dead in print mode; the body must not suggest it
    assert "stdin" not in body.lower() or "does not reach" in body.lower()


def test_flash_route_check_strings():
    body = _read(FLASH)
    assert 'Print mode: starting' in body
    assert 'model="' + CANONICAL_ID + '"' in body
    assert "Propagating selected model override" in body
    # the mode the dispatch line asks for, echoed by the client
    # (measured 2026-09-13 on agy 1.2.2, P2 log line 98)
    assert "Print mode: applying agent mode accept-edits" in body
    assert "requested and propagated" in body
    assert "used and confirmed" not in body.replace(
        'never "used and confirmed"', "")
    # transcript/tree corroboration (Sol check-off F1: the log carries no
    # file actions; evidence lives in the brain transcript)
    assert "transcript_full.jsonl" in body
    # the id is on the session.go "Print mode: conversation=<uuid>, sending
    # message" line; the starting line's conversationID field is EMPTY on
    # agy 1.2.0 and 1.2.2 (both logs measured 2026-09-13), so a wrapper
    # parsing the starting line gets no id and blocks a good run
    assert "Print mode: conversation=<uuid>" in body
    assert 'conversationID=""' in body
    assert "parse `conversationID=" not in body
    assert ("every path git status reports changed must appear in the "
            "brain transcript as a successful file-changing action"
            ) in body.lower()


def test_flash_preflight_pins():
    body = _read(FLASH)
    assert "agy models" in body
    assert "trustedWorkspaces" in body
    # conservative rule-class ban + clean baseline + stale-brief check,
    # pinned by exact sentence fragments (Sol check-off round 2,
    # finding 3): loose keyword pins would still pass a regression to
    # path-scoped matching or a dropped preflight
    assert "any `write_file(` entry, whatever path it names" in body
    assert "allow rule" in body
    assert "git status --porcelain" in body
    assert "No file matching `AGY-TASK-BRIEF-*`" in body
    # scope is the trust list itself, not a named checkout: preflight 2
    # is the mechanical gate and a worktree needs its own entry (measured
    # 2026-09-12: preflight passed in a trusted worktree on agy 1.2.0).
    # The 0.12.0 "main checkout only" carve-out named a plan task that no
    # longer exists.
    assert "any directory listed in `trustedWorkspaces`" in body
    # a parent entry covers a child worktree (measured 2026-09-13 on agy
    # 1.2.2: one entry for the worktrees parent, an edit landed in a
    # worktree under it that was not listed itself); preflight 2 must
    # accept an ancestor or it blocks the configuration that works
    assert "the workspace directory or an ancestor of it" in body
    assert "a worktree needs its own entry" not in body
    # Fable R1 findings 2 and 3 (2026-09-13): the trust list is the LANE's
    # allow-list and preflight 2 is its only enforcement, because agy does
    # not consult it for the write (edit landed in a directory with no
    # listed ancestor, with allowNonWorkspaceAccess true and again false);
    # and the comparison rule is stated so a Bash-only wrapper cannot pick
    # a bare string-prefix test
    assert "agy itself does not consult it" in body
    assert "case-insensitive" in body
    assert "plus a separator" in body
    assert "Task 6" not in body


def test_flash_route_report_carries_transcript():
    body = _read(FLASH)
    assert "AND the brain transcript's path" in body


def test_flash_forbidden_bypass_class():
    body = _read(FLASH)
    assert "--dangerously-skip-permissions" in body
    idx = body.find("--dangerously-skip-permissions")
    window = body[max(0, idx - 200):idx + 200].lower()
    assert "never" in window or "forbidden" in window
    assert "persisted" in body and "settings" in body
    # the scoped mode is named as NOT a member of the banned class, in
    # the same section, so a reader of the ban cannot mistake the
    # dispatch line for a violation of it
    assert "`--mode accept-edits` is not a member of that class" in body
    # Fable R1 finding 6: the narrowing clause is what keeps the carve-out
    # from becoming a general --mode allowance
    assert "No other `--mode` value is used in this lane" in body


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
            if "gemini-3.8-flash" in p.read_text(encoding="utf-8",
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
