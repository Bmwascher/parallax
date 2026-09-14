"""Contract pins for the Flash implementer lane (agents/flash-implementer.md).

Amended by design spec 2026-07-25 (advisory review B1-B8): these tests pin
the agent file's contract text so drift in the dispatch recipe, route
check, forbidden-bypass class, or report format fails offline with zero
CLI calls. Since backlog item 110 the Flash agent file is the only allowed
home for the implementer model literal, and the escalation lane
(agents/escalation-implementer.md) is the shared-contract parity twin:
the direct-typing Claude implementer was deleted in 0.39.0.
"""
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
FLASH = REPO / "agents" / "flash-implementer.md"
ESCALATION = REPO / "agents" / "escalation-implementer.md"
RETIRED = REPO / "agents" / "implementer.md"
FPF = REPO / "skills" / "multi-model-verify" / "references" / "frozen-plan-format.md"
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
    # sonnet since 0.38.0: every control in this lane is a prose rule the
    # wrapper follows (backlog item 105); agy print mode changed between
    # 1.1.7 and 1.2.x (the Dispatch step of the agent file) and 1.2.2
    # does not consult the trust list (item 105), so the seat needs to
    # block on a missing log line rather than rationalize a landed edit
    assert re.search(r"^model: sonnet$", fm, re.MULTILINE)
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
    # 2026-09-13); the log is where the route evidence lives. Astra R1
    # claim 6: "Windows spelling" alone is also satisfied by preflight 2's
    # path rule, so the trap sentence itself is pinned
    assert "Windows spelling" in body
    assert "a Git-Bash `/c/...` spelling produced NO log" in body
    assert "one run with `false` ended with the key removed" in body
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
    # Astra R1 claims 5 and 6: the two log tokens alone survive dropping
    # the empty-id rule or the one-uuid rule, so both are pinned; and the
    # missing-mode-line outcome names what the log fails to show, never a
    # cause the log cannot establish
    assert "an empty id is a missing transcript, not a wildcard" in body
    assert "exactly one distinct uuid" in body
    assert "the requested mode is not corroborated by the log" in body
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
    # Astra R1 claim 6: normalization and equality survive the two pins
    # above, so the rule's other clauses are pinned too
    assert "no trailing separator" in body
    assert "must equal the workspace path or" in body
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
    # rename in either cannot pass the suite (ROUTE is lane-specific to
    # the flash file). The escalation file keeps its numbered report
    # list, so its pins are the heading words in that shape.
    twin = _read(ESCALATION)
    for heading in ("STATUS - ", "FILES CHANGED - ", "VERIFICATION - ",
                    "DEVIATIONS - "):
        assert heading in twin, heading


def _shared_block(text, path):
    assert SHARED_START in text and SHARED_END in text, (
        "missing shared-contract markers in " + str(path))
    return text.split(SHARED_START)[1].split(SHARED_END)[0]


def test_shared_contract_parity():
    # byte-identical shared block; ROUTE is lane-specific and lives
    # outside the block (spec section 1). Since item 110 the twin is the
    # escalation lane: outside its envelope the same zero-judgment
    # contract applies, and the block is that contract.
    assert _shared_block(_read(FLASH), FLASH) == _shared_block(
        _read(ESCALATION), ESCALATION)


def test_agent_frontmatter_routes():
    # 0.38.0: a build session told "use parallax implementers" dispatched
    # parallax:implementer four times and the Flash lane never, because
    # both descriptions said "use when executing tasks from a
    # debate-frozen implementation plan". The description is the ONLY
    # text a session reads when it picks a subagent, so the default is
    # declared there. Item 110 deleted the second file, so the Flash
    # description names no other implementer by name. Agent-file pins
    # and plan-format pins are separate tests so a broken agent edit
    # cannot hide behind a plan-format failure the build expects
    # (Astra plan R1, finding 11).
    flash_fm = _frontmatter(_read(FLASH))
    assert "THE build lane for every frozen-plan task" in flash_fm
    assert "dispatch this agent, and no other implementer," in flash_fm
    assert "not implementer," not in flash_fm
    escalation_fm = _frontmatter(_read(ESCALATION))
    assert "consent-gated reroutes of blocked tasks" in escalation_fm
    assert "which is EMPTY for a reroute" in escalation_fm


def test_flash_lane_is_the_declared_default():
    # the plan format declares the same default and the two routes away
    # from it
    fpf = _read(FPF)
    assert "Build lane: parallax:flash-implementer" in fpf
    assert "no `ROUTE:` line is a lane violation" in fpf
    # the per-task field the hook reads, and the two routes that carry it
    assert "**Lane:** parallax:escalation-implementer" in fpf
    assert "(consented reroute, <ledger path>)" in fpf
    assert "agents/implementer.md" not in fpf


def test_empty_envelope_is_zero_judgment():
    # item 110: a consented reroute of a task the Flash lane blocked goes
    # to the escalation lane with an EMPTY envelope, and mode diff must
    # adjudicate it as zero-judgment. The plan format carries the rule on
    # one physical line.
    fpf = _read(FPF)
    assert "Any DECISIONS entry on an empty envelope is drift" in fpf


def test_escalation_empty_envelope_is_zero_judgment():
    # the agent file carries the same rule, each pin on one physical line
    body = _read(ESCALATION)
    assert "its envelope is EMPTY by construction" in body
    assert "any DECISIONS entry you write on it is drift" in body
    assert "An empty envelope means an empty section" in body


def test_direct_typing_claude_lane_is_gone():
    # the file whose only remaining job was a rare reroute took 122 of
    # 128 build dispatches in five days (item 110's Cost line)
    assert not RETIRED.exists()
    # the vendor-swap Lane note moved into the Flash file, the supervisor
    # pattern it described
    body = _read(FLASH)
    assert "Two swap paths" in body
    assert "stays the SUPERVISOR" in body
    assert "`implementer.md` pins its own lane's model" not in body
    assert "every other surface points at this file" in body


SWEEP_GLOBS = [
    "skills/**/*.md", "commands/*.md", "tools/*.ps1", "hooks/*",
    "evals/**/*.py", "evals/**/*.json", "evals/**/*.ps1",
    "README.md", "CLAUDE.md", "agents/*.md",
]
# The Flash agent file is the contract home; this test file necessarily
# carries the literal as its enforcement pin.
ALLOWED = {FLASH.resolve(), Path(__file__).resolve()}


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


def test_retired_lane_paths_swept_from_live_surfaces():
    # the sweep item 110 asks for, as a gate: no live surface names the
    # deleted file. Records under docs/ and .superpowers/ are not live.
    offenders = []
    for pattern in SWEEP_GLOBS:
        for p in REPO.glob(pattern):
            if p.resolve() == Path(__file__).resolve():
                continue
            text = p.read_text(encoding="utf-8", errors="replace")
            if re.search(r"(?<![\w-])implementer\.md", text):
                offenders.append(str(p))
    assert offenders == []


def test_sonnet_implementer_literals_removed():
    readme = _read(REPO / "README.md")
    assert "currently `model: sonnet`" not in readme
    # absence pins alone are vacuous against line-wrapped source; the
    # presence pins below are the real oracles for Task 3's rewrites
    assert "`haiku`/`opus` are drop-ins" not in readme
    assert "any Claude tier is a drop-in" in readme
    assert "its Lane note carries the two swap paths" in readme
    fpf = _read(FPF)
    assert "Sonnet 5" not in fpf
    assert "the pinned lane in `agents/`" in fpf
