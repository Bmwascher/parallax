# Single Zero-Judgment Implementer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** One zero-judgment implementer file ships (`agents/flash-implementer.md`); a consent-gated reroute of a task the Flash lane blocked goes to `agents/escalation-implementer.md` with an EMPTY envelope, where any DECISIONS entry is drift; the plugin's PostToolUse hook warns on any implementer dispatch other than `parallax:flash-implementer` whose prompt carries no `Lane:` line naming that agent.

**Architecture:** `agents/implementer.md` is deleted by the session. `agents/escalation-implementer.md` gains the shared-contract block and becomes the parity twin in `test_flash_implementer.py`. `references/frozen-plan-format.md` names the escalation lane as the only second lane, the per-task `**Lane:**` field, and the empty-envelope drift rule. `hooks/superpowers-review-companion.ps1` gains a build-lane check ahead of its reviewer fingerprint, driven by `tool_input.subagent_type`. Tests are written first in Task 1; Tasks 2 to 4 turn them green.

**Tech Stack:** Markdown agent and reference files, PowerShell 7 hook (`pwsh`, the host `hooks/hooks.json` names), Python 3 pytest evals.

**Spec:** `docs/superpowers/specs/2026-09-13-single-implementer-design.md`. Backlog item 110 (ranked first); items 109 and 105 are context.

**Build lane:** parallax:flash-implementer

## Global Constraints

- The workspace is the primary checkout `C:\Users\Brandon\Documents\parallax` on branch `item110-single-implementer`; it is a `trustedWorkspaces` entry. Every task's log-file path is under `C:/Users/Brandon/AppData/Local/Temp/parallax-item110/` (Windows spelling), outside the workspace; the session creates that directory before Task 1.
- Do not reflow any existing paragraph in `skills/`, `agents/`, `commands/` or `README.md`: raw-text pins in `evals/` break on a rewrap. Edit only the lines a task quotes; a task that replaces a span replaces EXACTLY the quoted span.
- Files under `agents/`, `skills/` and `README.md` are UTF-8 with LF line endings and contain em dashes (U+2014); preserve both. A replacement span in this plan reproduces the em dash where the original carries one.
- The literal `gemini-3.8-flash` may appear only in `agents/flash-implementer.md` and `evals/multi-model-verify/test_flash_implementer.py`. No task adds it anywhere else.
- `SKILL.md` is not edited by any task.
- Stage by explicit path (`git add <file> <file>`); `git add -A` is refused by the family git guard. Commit messages are lowercase imperative, no AI attribution, and must not contain a token that looks like a PowerShell flag.
- The release this branch ships is 0.39.0; the text a task quotes with that number is written as quoted. The session bumps `plugin.json`, writes the changelog section and closes backlog item 110 AFTER the diff debate, not in any task.
- Full gate before the final commit of the branch (the session runs it, not a task): the six CI commands in `CLAUDE.md`.

---

### Task 1: Tests first

**Files:**
- Modify: `evals/multi-model-verify/test_flash_implementer.py` (whole file replaced)
- Modify: `evals/multi-model-verify/test_multi_model_verify.py` (insert six methods into `class TestHook`, after `test_silent_on_other_dispatch`)

**Interfaces:**
- Consumes: `TestHook.run_hook(payload)` at `evals/multi-model-verify/test_multi_model_verify.py:2699`, which runs `hooks/superpowers-review-companion.ps1` under `pwsh` with the payload as JSON on stdin and returns `(stdout.strip(), returncode)`.
- Produces: the pins Tasks 2, 3 and 4 satisfy, named in each of those tasks.

- [ ] **Step 1: Replace `evals/multi-model-verify/test_flash_implementer.py` with this exact content**

```python
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
```

- [ ] **Step 2: Make `run_hook` return raw stdout, then insert six methods into `TestHook` in `evals/multi-model-verify/test_multi_model_verify.py`**

First, in the existing `run_hook` helper (the method that starts `def run_hook(self, payload):`), replace this exact line:

```python
        return proc.stdout.strip(), proc.returncode
```

with:

```python
        return proc.stdout, proc.returncode
```

The silent cases assert `out == ""` and a stripped stdout would let whitespace-only output pass them (Astra plan R1, finding 5); `json.loads` tolerates the trailing newline the warning cases carry.

Then find this existing method (it ends at the line `assert out == ""`):

```python
    def test_silent_on_other_dispatch(self):
        payload = {
            "tool_name": "Agent",
            "tool_input": {"description": "Explore",
                           "prompt": "Find all uses of FramePool."},
        }
        out, rc = self.run_hook(payload)
        assert rc == 0
        assert out == ""
```

Immediately after its last line, and before the existing `def test_failure_event_name_is_echoed(self):`, insert exactly this (one blank line above and one below, as between the existing methods):

```python
    # --- build-lane check (backlog item 110) ---
    # Between 2026-09-09 and 2026-09-13, 122 of 128 build dispatches went
    # to parallax:implementer and no gate saw it. The hook reads
    # tool_input.subagent_type on every Agent call: any implementer other
    # than parallax:flash-implementer warns unless the prompt carries a
    # `Lane:` line naming that agent, which the frozen plan's task text
    # carries at freeze time and the SDD ledger's consent line carries at
    # build time (references/frozen-plan-format.md).

    ESCALATION_TASK = (
        "### Task 3: The reap guard\n\n**Files:**\n- Modify: `tools/x.ps1`\n\n"
        "Decision envelope:\n- D1: the refusal text, bounded to one line.\n"
    )

    def test_implementer_off_the_build_lane_warns(self):
        out, rc = self.run_hook({
            "tool_name": "Agent",
            "tool_input": {"description": "Task 3",
                           "subagent_type": "parallax:escalation-implementer",
                           "prompt": self.ESCALATION_TASK},
        })
        assert rc == 0
        data = json.loads(out)
        assert data["hookSpecificOutput"]["hookEventName"] == "PostToolUse"
        self.assert_lane_warning(data, "parallax:escalation-implementer")

    def assert_lane_warning(self, data, agent):
        # every warning names the dispatched agent, the build lane and
        # the field that would have silenced it (Astra plan R1, finding 5)
        ctx = data["hookSpecificOutput"]["additionalContext"]
        assert agent in ctx
        assert "parallax:flash-implementer" in ctx
        assert "Lane:" in ctx

    def test_plan_named_lane_is_silent(self):
        out, rc = self.run_hook({
            "tool_name": "Agent",
            "tool_input": {"description": "Task 3",
                           "subagent_type": "parallax:escalation-implementer",
                           "prompt": ("**Lane:** parallax:escalation-implementer\n"
                                      + self.ESCALATION_TASK)},
        })
        assert rc == 0
        assert out == ""

    def test_consented_reroute_line_is_silent(self):
        ledger = ".superpowers/sdd/2026-09-13-single-implementer/task-3-consent.md"
        out, rc = self.run_hook({
            "tool_name": "Agent",
            "tool_input": {"description": "Task 3",
                           "subagent_type": "parallax:escalation-implementer",
                           "prompt": (self.ESCALATION_TASK
                                      + "**Lane:** parallax:escalation-implementer"
                                      + " (consented reroute, " + ledger + ")\n")},
        })
        assert rc == 0
        assert out == ""

    def test_lane_line_naming_another_agent_still_warns(self):
        # four prompts that must NOT silence the hook: a Lane line naming
        # a different agent; the field split across a line break; the
        # agent name with a suffix; and no prompt at all (Astra plan R1,
        # findings 4 and 5)
        for prompt in (
            "**Lane:** parallax:flash-implementer\n" + self.ESCALATION_TASK,
            "**Lane:**\nparallax:escalation-implementer\n" + self.ESCALATION_TASK,
            "**Lane:** parallax:escalation-implementer:other\n" + self.ESCALATION_TASK,
            "",
        ):
            out, rc = self.run_hook({
                "tool_name": "Agent",
                "tool_input": {"description": "Task 3",
                               "subagent_type": "parallax:escalation-implementer",
                               "prompt": prompt},
            })
            assert rc == 0, prompt
            self.assert_lane_warning(json.loads(out),
                                     "parallax:escalation-implementer")

    def test_deleted_claude_lane_warns_on_the_failure_event(self):
        # after 0.39.0 a plan that still names parallax:implementer fails
        # at dispatch; PostToolUseFailure is where the warning reaches it
        out, rc = self.run_hook({
            "hook_event_name": "PostToolUseFailure",
            "tool_name": "Agent",
            "tool_input": {"description": "Task 1",
                           "subagent_type": "parallax:implementer",
                           "prompt": "### Task 1: Tests first\n"},
        })
        assert rc == 0
        data = json.loads(out)
        assert data["hookSpecificOutput"]["hookEventName"] == "PostToolUseFailure"
        self.assert_lane_warning(data, "parallax:implementer")

    def test_flash_lane_dispatch_is_silent(self):
        out, rc = self.run_hook({
            "tool_name": "Agent",
            "tool_input": {"description": "Task 1",
                           "subagent_type": "parallax:flash-implementer",
                           "prompt": "### Task 1: Tests first\n"},
        })
        assert rc == 0
        assert out == ""
```

- [ ] **Step 3: Run both modules and read the failures by name**

Run: `python -m pytest evals/multi-model-verify/test_flash_implementer.py -q 2>&1 | grep -E "passed|failed|FAILED"`

Expected: FAILED lines naming exactly these eight, and no other failure:
`test_shared_contract_parity`, `test_agent_frontmatter_routes`, `test_flash_lane_is_the_declared_default`, `test_empty_envelope_is_zero_judgment`, `test_escalation_empty_envelope_is_zero_judgment`, `test_direct_typing_claude_lane_is_gone`, `test_retired_lane_paths_swept_from_live_surfaces`, `test_sonnet_implementer_literals_removed`. (`test_flash_report_headings` passes: the escalation file's numbered report list already carries the four heading words. `test_flash_literal_single_source` passes: `agents/implementer.md` carries no Flash literal.)

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k TestHook 2>&1 | grep -E "passed|failed|FAILED"`

Expected: FAILED lines naming exactly these three, and no other failure: `TestHook::test_implementer_off_the_build_lane_warns`, `TestHook::test_lane_line_naming_another_agent_still_warns`, `TestHook::test_deleted_claude_lane_warns_on_the_failure_event`. (The three silent cases pass on the current hook, which is silent on every non-reviewer prompt.)

- [ ] **Step 4: Commit**

```bash
git add evals/multi-model-verify/test_flash_implementer.py evals/multi-model-verify/test_multi_model_verify.py
git commit -m "pin the single implementer contract first: escalation lane as parity twin, empty envelope rule, build lane hook cases, retired path sweep"
```

---

### Task 2: The two remaining agent files

**Session step before dispatch (not the implementer's):** the session runs `git rm agents/implementer.md` and commits it alone as `delete the direct-typing claude implementer, the second zero-judgment file item 110 retires`, so the workspace is clean for preflight 4. The deletion is a session act because a Flash delete under `--mode accept-edits` is unmeasured (`agents/flash-implementer.md`, Dispatch step 2) and this cycle does not measure it.

**Files:**
- Modify: `agents/escalation-implementer.md` (whole file replaced)
- Modify: `agents/flash-implementer.md:3` (the `description:` line) and `agents/flash-implementer.md:166-180` (the Lane note)

**Interfaces:**
- Consumes: the shared block between `<!-- shared-contract:start -->` and `<!-- shared-contract:end -->` in `agents/flash-implementer.md:19-36`, reproduced byte for byte.
- Produces: the pins `test_flash_report_headings`, `test_shared_contract_parity`, `test_agent_frontmatter_routes`, `test_escalation_empty_envelope_is_zero_judgment` and `test_direct_typing_claude_lane_is_gone` read.

- [ ] **Step 1: Replace `agents/escalation-implementer.md` with this exact content**

The block between the two `shared-contract` markers is copied from `agents/flash-implementer.md` and carries its em dashes.

```markdown
---
name: escalation-implementer
description: Fable escalation implementer for judgment-heavy frozen-plan tasks and consent-gated reroutes of blocked tasks. Use when a frozen plan routes a task here with an enumerated decision envelope, or when the user consents to rerouting a task the Flash lane blocked - give it the task's verbatim text, the plan's Global Constraints, and the envelope, which is EMPTY for a reroute. It exercises implementation judgment ONLY inside the envelope, logs every decision, and reports deviations separately from decisions.
model: fable
---

# Escalation implementer (judgment inside an envelope)

You execute ONE task that needs implementation judgment. Unlike the
zero-judgment Flash lane, you may choose - but only inside the task's
enumerated decision envelope, and every choice is logged for the diff
debate to adjudicate.

<!-- shared-contract:start -->
## The contract

- Build exactly what the task says: the files it lists, the code it shows,
  the commands it specifies. Nothing else.
- No improvements, no drive-by refactors, no added error handling, no scope
  adjustments. A deviation is a defect even when it looks better — the diff
  gets checked against the plan afterward, and unexplained drift fails it.
- **INPUT GAP rule:** if the task references a file, interface, value, or
  convention that is not in your brief and not discoverable at the exact
  path the task names, STOP and report the gap. Never invent or guess the
  missing piece.
- Run the task's verification commands yourself and read the output. Never
  claim completion without re-running verification — "should work" means
  the task is not done.
<!-- shared-contract:end -->

## The decision envelope

The frozen plan (or the consented reroute record) ENUMERATES this
task's open decision points, each with the constraints that bound it.
That list is the whole of your delegated judgment, and it is the one
place the contract above is suspended:

- Inside a decision point: choose, implement the choice, and log it in
  DECISIONS with its reasoning and evidence.
- Outside the enumerated envelope the contract above applies
  unchanged: build exactly what the task says; anything else is a
  deviation, not a decision.
- An EMPTY envelope delegates nothing: the task is zero-judgment end to
  end, and any DECISIONS entry you write on it is drift the diff debate
  fails. A missing or ambiguous envelope entry is an input gap under the
  contract above - never invent a decision point.

## Entry routes

1. Plan-time designation: the frozen plan routes the task here, the
   task text carries the field `**Lane:** parallax:escalation-implementer`,
   and it carries the envelope - the debate that froze the plan
   authorized that routing.
2. Blocked-task reroute: a task the Flash lane blocked reaches you
   only with user consent, recorded in the cycle's SDD ledger before
   you start, and its envelope is EMPTY by construction: the task was
   frozen as zero-judgment, and consent to reroute it is not consent to
   redesign it. Unattended runs fail closed.

## Verification

Run the task's verification commands yourself and read the output.
Never claim completion without re-running verification.

## Report (final message)

1. STATUS - done | blocked | INPUT GAP: <exactly what is missing>.
2. FILES CHANGED - actual paths from `git status`.
3. VERIFICATION - each command you ran, with its real output.
4. DECISIONS - one entry per enumerated decision point: the choice,
   why, and the evidence behind it. An empty envelope means an empty section, stated explicitly.
5. DEVIATIONS - must be `none`: anything outside the enumerated
   envelope is a deviation, exactly as in the Flash lane, and a
   deviation is a defect even when it looks better.
6. CONCERNS - doubts worth the reviewer's attention, or none.
```

- [ ] **Step 2: Edit the `description:` line of `agents/flash-implementer.md`**

Replace this exact fragment on line 3:

```
dispatch this agent, not implementer, whenever a debate-frozen implementation plan is being built, unless the plan routes a named task elsewhere.
```

with:

```
dispatch this agent, and no other implementer, whenever a debate-frozen implementation plan is being built, unless the plan routes a named task to the escalation lane by a Lane field.
```

The rest of the line is unchanged.

- [ ] **Step 3: Replace the Lane note of `agents/flash-implementer.md`**

Replace this exact span (the file's last three lines of the first Lane note sentence group; the dash on the third line is an em dash):

```
Antigravity CLI resolved ID). The literal lives ONLY here;
`implementer.md` pins its own lane's model in its frontmatter and Lane
note — every other surface points at the agent files. Trust is
```

with:

```
Antigravity CLI resolved ID). The literal lives ONLY here;
every other surface points at this file. Trust is
```

Then append this exact text at the end of the file, after the line `2026-09-13 on 1.2.2), which is why preflight 2 exists.`, separated by one blank line and ending with a newline:

```
Two swap paths, and this is the only implementer file either one edits
(the direct-typing Claude implementer was deleted in 0.39.0, backlog
item 110; the escalation lane in `escalation-implementer.md` is a
judgment seat, not a typing lane):

- **Another Claude tier as the wrapper** (sonnet/haiku/opus): edit the
  `model:` line in this file's frontmatter - done. The wrapper never
  types repo code, so the tier changes how reliably the prose controls
  above are followed (backlog item 105), never what gets typed.
- **Another vendor's model as the typist** (a Grok or Codex lane,
  fable-advisor style): the `model:` frontmatter only takes Claude
  models, so the Claude tier stays the SUPERVISOR and the Dispatch and
  Route sections above change to that vendor's CLI - the brief to a file
  in the workspace, the CLI in a mode that opens file edits only, its own
  route and authorship evidence read back, then the task's verification
  re-run here before reporting (never trust the external model's
  completion claim). The report format above stays the contract either
  way.
```

- [ ] **Step 4: Run the agent-file pins**

Run: `python -m pytest evals/multi-model-verify/test_flash_implementer.py evals/multi-model-verify/test_seat_reshuffle.py -q 2>&1 | grep -E "passed|failed|FAILED"`

Expected: `test_seat_reshuffle.py` fully green; in `test_flash_implementer.py` the five agent-file tests named under Interfaces now PASS, and exactly these still fail, nothing else: `test_flash_lane_is_the_declared_default` (the `frozen-plan-format.md` pins), `test_empty_envelope_is_zero_judgment` (`frozen-plan-format.md`), `test_retired_lane_paths_swept_from_live_surfaces` (README, `frozen-plan-format.md` and the two contract-coverage files still name the deleted file), `test_sonnet_implementer_literals_removed` (README).

- [ ] **Step 5: Commit**

```bash
git add agents/escalation-implementer.md agents/flash-implementer.md
git commit -m "make the escalation lane the shared-contract twin with an empty envelope on reroute, and move the vendor-swap note into the flash lane file"
```

---

### Task 3: The plan format, README, and the superseded spec line

**Files:**
- Modify: `skills/multi-model-verify/references/frozen-plan-format.md:10-28`
- Modify: `README.md:32`, `README.md:98-99`, `README.md:279-286`
- Modify: `docs/superpowers/specs/2026-07-25-flash-implementer-design.md:3-4`
- Modify: `evals/multi-model-verify/contract_coverage.py:28` and `evals/multi-model-verify/test_contract_coverage.py:189` (one comment fragment each)

**Interfaces:**
- Produces: the `fpf` and README pins in `test_flash_lane_is_the_declared_default`, `test_empty_envelope_is_zero_judgment`, `test_retired_lane_paths_swept_from_live_surfaces`, `test_sonnet_implementer_literals_removed`; `test_seat_reshuffle.py::test_plan_format_panel_and_envelope_pins` and `::test_readme_reshuffle_pins` stay green.

- [ ] **Step 1: Replace lines 10-28 of `skills/multi-model-verify/references/frozen-plan-format.md`**

The span to replace starts at the line beginning `**The build lane is` and ends at the line `the right one.` (the paragraph before the line beginning `A task the plan routes to the escalation lane carries`). Replace it with exactly:

```markdown
**The build lane is `agents/flash-implementer.md`, by default and by
name.** The plan header carries the line
`Build lane: parallax:flash-implementer` and the session dispatches that
agent for every task. Two kinds of exception exist, and both name the
same second lane, `agents/escalation-implementer.md`, because it is the
only other implementer the plugin ships. At freeze time the plan itself
routes a task there with an enumerated decision envelope, one per task
with the reason in the task text, and that task carries the field
`**Lane:** parallax:escalation-implementer`
on its own line beside `**Files:**`, so the dispatch prompt carries it
verbatim. At build time the Flash lane blocks a task and the user
consents to reroute it to the escalation lane with an EMPTY envelope;
the session records that consent in the SDD ledger, because the plan is
frozen and the implementer never edits it, and the dispatch prompt
carries the ledger's line
`**Lane:** parallax:escalation-implementer (consented reroute, <ledger path>)`.
Any DECISIONS entry on an empty envelope is drift, so mode diff
adjudicates a rerouted task as zero-judgment. A task report with no `ROUTE:` line is a lane violation unless the plan
or a recorded consent routed that task elsewhere, because only the Flash
lane's report carries one; the session names it in the SDD ledger and
reroutes nothing without the user. The plugin's PostToolUse hook warns
on any implementer dispatch other than `parallax:flash-implementer`
whose prompt carries no `Lane:` line naming that agent; the warning is a
reminder, and the ledger and mode diff stay the gates.
Measured 2026-09-13: a build session told "use parallax implementers"
dispatched the direct-typing Claude implementer four times and the
Flash lane never, because both agent descriptions then read the same;
that file, `parallax:implementer`, was deleted in 0.39.0 (backlog item
110). The lane is declared in the descriptions and here so a session
picking by description picks the right one.
```

The line beginning `A task the plan routes to the escalation lane carries` and everything after it are unchanged.

- [ ] **Step 2: Edit `README.md`**

(a) Delete this whole line (line 32), leaving the table rows above and below adjacent:

```
| Implementer (transcription, fallback only) | Claude tier | `agents/implementer.md` (frontmatter default `sonnet`; haiku per dispatch) |
```

(b) Replace this whole line (line 98):

```
| `hooks/` | PostToolUse + PostToolUseFailure hook (matcher `Task\|Agent`): fingerprints the superpowers code-reviewer dispatch, injects the mode-`diff` reminder with matching SHAs; inert everywhere else |
```

with:

```
| `hooks/` | PostToolUse + PostToolUseFailure hook (matcher `Task\|Agent`): fingerprints the superpowers code-reviewer dispatch and injects the mode-`diff` reminder with matching SHAs; warns on any implementer dispatch other than the Flash lane whose prompt carries no `Lane:` line naming that agent; inert everywhere else |
```

(c) Delete this whole line (line 99):

```
| `agents/implementer.md` | Zero-judgment direct-typing fallback for frozen-plan tasks the plan routes to it by name, never the default (model pinned in the file's frontmatter) |
```

(d) Replace this exact span (lines 279-286, two bullets; the dashes after the bold titles are em dashes):

```
- **Implementer, Claude tier** — edit one line: `model:` in
  `agents/implementer.md` frontmatter (any Claude tier is a drop-in). The contract (zero judgment calls, INPUT GAP rule, structured
  report) stays identical whoever fills it.
- **Implementer, cross-vendor** (the fable-advisor v3 Grok pattern) —
  agent frontmatter only accepts Claude tiers, so a vendor swap uses the
  supervisor pattern `agents/flash-implementer.md` implements (documented in `agents/implementer.md`'s Lane note): a Claude
  tier supervises, delegates the body of work to the vendor CLI, and
  re-runs verification itself.
```

with:

```
- **Implementer, wrapper tier** — edit one line: `model:` in
  `agents/flash-implementer.md` frontmatter (any Claude tier is a drop-in). The contract (zero judgment calls, INPUT GAP rule, structured
  report) stays identical whoever fills it; the wrapper never types repo code.
- **Implementer, cross-vendor** (the fable-advisor v3 Grok pattern) —
  agent frontmatter only accepts Claude tiers, so a vendor swap uses the
  supervisor pattern `agents/flash-implementer.md` implements (its Lane note carries the two swap paths): a Claude
  tier supervises, delegates the body of work to the vendor CLI, and
  re-runs verification itself.
```

- [ ] **Step 3: Add the superseded line to `docs/superpowers/specs/2026-07-25-flash-implementer-design.md`**

After line 4 (the line ending `advisory-review amendments folded same day (see Review provenance)`) and before the blank line that follows it, insert this single line:

```
**Superseded in part, 2026-09-13:** Decision A below kept `agents/implementer.md` as the direct-typing lane; backlog item 110 (0.39.0) deleted that file, and the escalation lane takes consent-gated reroutes with an empty envelope. See `docs/superpowers/specs/2026-09-13-single-implementer-design.md`.
```

- [ ] **Step 4: Retire the deleted file's name from the two contract-coverage comments**

In `evals/multi-model-verify/contract_coverage.py` (line 28, a `#` comment) and in `evals/multi-model-verify/test_contract_coverage.py` (line 189, inside a docstring), replace the exact fragment:

```
agents/implementer.md and agents/flash-implementer.md already carry
```

with:

```
agents/escalation-implementer.md and agents/flash-implementer.md already carry
```

One occurrence in each file; nothing else on those lines changes. (Astra plan R1, finding 6: the session's sweep dropped these two lines because each also names `flash-implementer.md`.)

- [ ] **Step 5: Run the pins**

Run: `python -m pytest evals/multi-model-verify/test_flash_implementer.py evals/multi-model-verify/test_seat_reshuffle.py evals/multi-model-verify/test_contract_coverage.py -q 2>&1 | grep -E "passed|failed|FAILED"`

Expected: all three modules green, `0 failed`.

- [ ] **Step 6: Commit**

```bash
git add skills/multi-model-verify/references/frozen-plan-format.md README.md docs/superpowers/specs/2026-07-25-flash-implementer-design.md evals/multi-model-verify/contract_coverage.py evals/multi-model-verify/test_contract_coverage.py
git commit -m "route every reroute to the escalation lane with an empty envelope, name the per-task lane field, and sweep the deleted file from the live surfaces"
```

---

### Task 4: The build-lane check in the hook

**Files:**
- Modify: `hooks/superpowers-review-companion.ps1` (whole file replaced)

**Interfaces:**
- Consumes: the PostToolUse / PostToolUseFailure payload on stdin: `hook_event_name`, `tool_input.subagent_type`, `tool_input.prompt`.
- Produces: the six `TestHook` cases from Task 1 green, with the nine existing `TestHook` cases unchanged.

- [ ] **Step 1: Replace `hooks/superpowers-review-companion.ps1` with this exact content**

```powershell
# PostToolUse hook (Task|Agent), two checks, both warn and never block.
#
# 1. Build lane (backlog item 110): every frozen-plan task is built by
#    parallax:flash-implementer unless the plan, or a consent the session
#    recorded in the SDD ledger, names another lane for THAT task. The
#    evidence is a `Lane:` line in the dispatch prompt carrying the
#    dispatched subagent_type (references/frozen-plan-format.md). An
#    implementer dispatch IS the build, so no other state is consulted;
#    a payload with no subagent_type falls through.
# 2. Review companion: when the superpowers requesting-code-review skill
#    dispatches its code-reviewer subagent, inject a reminder to run the
#    multi-model-verify skill's diff mode on the same commit range.
#    Fingerprint: the rendered code-reviewer.md template (superpowers
#    6.3.0) always contains the literals "Senior Code Reviewer" and "Git
#    Range to Review"; both must be present. Re-check the template after
#    superpowers updates - if the fingerprint rots, this check silently
#    stops firing (fails open, never blocks).
#
# Output contract: silent exit 0 = nothing to add; JSON additionalContext =
# non-blocking context injection.

try {
    $payload = [Console]::In.ReadToEnd() | ConvertFrom-Json
} catch {
    exit 0
}

# Echo the INCOMING event name: this script serves PostToolUse and
# PostToolUseFailure, and the output contract requires hookSpecificOutput
# to name the actual event (Sol holistic MAJOR, 2026-07-13).
$eventName = $payload.hook_event_name
if (-not $eventName) { $eventName = 'PostToolUse' }

$subagent = [string]$payload.tool_input.subagent_type
if ($subagent -and $subagent -imatch 'implementer' -and $subagent -cne 'parallax:flash-implementer') {
    # The field is written as `**Lane:** <agent>` on ONE line in the
    # frozen task text; leading list or emphasis markers are tolerated,
    # nothing crosses a line break, and the agent name is matched exactly
    # and must end at a blank or the end of that line (Astra plan R1,
    # finding 4: `\s*` crossed a newline and `(?![\w-])` accepted
    # `parallax:escalation-implementer:other`).
    $laneLine = '(?m)^[ \t*_>-]*Lane:\**[ \t]*' + [regex]::Escape($subagent) + '(?=[ \t]|\r?$)'
    $promptText = [string]$payload.tool_input.prompt
    if ($promptText -cmatch $laneLine) { exit 0 }
    $warn = @{
        hookSpecificOutput = @{
            hookEventName     = $eventName
            additionalContext = ("parallax: this dispatch went to $subagent, and the " +
                "build lane for every frozen-plan task is parallax:flash-implementer. " +
                "A task the plan routes elsewhere carries the field " +
                "'**Lane:** $subagent' in its task text; a consented reroute of a " +
                "task the Flash lane blocked carries the SDD ledger's line " +
                "'**Lane:** $subagent (consented reroute, <ledger path>)'. This " +
                "prompt carried neither. Either add the line from the plan or the " +
                "ledger, or route the task to parallax:flash-implementer. " +
                "Measured 2026-09-13: 122 of 128 build dispatches in five days went " +
                "to a lane the plan never named (backlog item 110).")
        }
    }
    $warn | ConvertTo-Json -Compress -Depth 5
    exit 0
}

$prompt = $payload.tool_input.prompt
if (-not $prompt) { exit 0 }

$hasReviewer = $prompt -match 'Senior Code Reviewer'
$hasRange = $prompt -match 'Git Range to Review'
if (-not $hasReviewer -and -not $hasRange) { exit 0 }

if ($hasReviewer -ne $hasRange) {
    # Exactly one fingerprint literal matched: this looks like the
    # superpowers code-reviewer dispatch after a template change - the
    # diff gate may be rotting. Warn NOW instead of failing open until
    # the weekly drift check notices (Sol holistic improvement 3).
    $warn = @{
        hookSpecificOutput = @{
            hookEventName     = $eventName
            additionalContext = ("parallax: this dispatch matches only PART of the " +
                "superpowers code-reviewer fingerprint - the template may have " +
                "changed and the multi-model-verify diff gate may be inert. Run " +
                "tools/check-drift.ps1 and re-fingerprint " +
                "hooks/superpowers-review-companion.ps1. If this was a final " +
                "pre-merge code review, run multi-model-verify mode diff manually " +
                "on the review's base/head range.")
        }
    }
    $warn | ConvertTo-Json -Compress -Depth 5
    exit 0
}

$base = ''
$head = ''
if ($prompt -match '\*\*Base:\*\*\s*([^\s`\r\n]+)') { $base = $Matches[1] }
if ($prompt -match '\*\*Head:\*\*\s*([^\s`\r\n]+)') { $head = $Matches[1] }
$range = if ($base -and $head) { "base $base head $head" } else { 'the same base/head range the review used' }

$context = "A superpowers code review just ran on this branch ($range). " +
    "If that was the final pre-merge review (requesting-code-review), also run " +
    "the multi-model-verify skill in mode diff on the SAME range now - " +
    "cross-model spec-fidelity and port-fidelity verification is a separate " +
    "gate from single-model code review. If it was an intermediate per-task " +
    "review, defer multi-model-verify until the final review. Skip only if " +
    "mode diff already ran for this exact range."

$out = @{
    hookSpecificOutput = @{
        hookEventName     = $eventName
        additionalContext = $context
    }
}
$out | ConvertTo-Json -Compress -Depth 5
exit 0
```

- [ ] **Step 2: Run the hook cases**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k TestHook 2>&1 | grep -E "passed|failed|FAILED"`

Expected: `15 passed` (the nine existing cases and the six new ones; `test_superpowers_fingerprint_canary` counts as passed on this machine because superpowers is installed), `0 failed`.

- [ ] **Step 3: Commit**

```bash
git add hooks/superpowers-review-companion.ps1
git commit -m "warn from the hook on any implementer dispatch other than the flash lane whose prompt carries no lane line naming that agent"
```

---

## After the tasks (session, not a task)

1. Full gate: the six `CLAUDE.md` commands, then `python evals/tools/run_behavioral_evals.py --changed --head`.
2. Sweep report in the diff-debate brief: shapes searched (`implementer.md` with a lookbehind that excludes `flash-` and `escalation-`, applied per MATCH and never by dropping whole lines, because a line-level exclusion dropped `contract_coverage.py:28` and `test_contract_coverage.py:189`, which name both files; `parallax:implementer`; bare `implementer` in `commands/`, `tools/`, `hooks/`, `README.md`, `skills/`), the edited surfaces including those two, the explicit none for doctor check 7 and `tools/check-drift.ps1`, and the records left as written.
3. Fable whole-branch review, diff debate on the Astra lane, attestation.
4. Bump to 0.39.0 with the changelog section in the same commit; close backlog item 110 (header to `Status: DONE` / `Closed: 0.39.0`, ranking line removed, `Verified` refreshed with the lint's digest) in that commit too.
5. Doctor check 7b: the Gemini weekly figure read before Task 1 and after Task 4 is the cheap proof the build used the Flash lane.

---

## Debate record

**Participants:** Claude Opus 5 (session) / GPT-6 Astra (codex exec, session 01a09e23-c7b2-7f33-a661-774281556eff)
**Rounds used:** 2 of 4 (fix-verify budget 4 dispatched exchanges, declared before round 1; round cap 4 consecutive contested exchanges; contested counter never left zero)
**Outcome:** converged with amendments
**Verification status:** FULL
**Degradation:** none
**Authorized by:** n/a
**Raw rounds:** docs/superpowers/plans/rounds/2026-09-13-single-implementer/ (briefs, replies, transcripts, binders, receipts, mirror builds, tool-surface probe, artifact roots)

Preflight 2026-09-13: codex-cli 0.153.4, `Logged in using ChatGPT` in a sanitized environment, host `pwsh`. Enumeration on the reviewed repo found one back-channel, an ignored untracked `AGENTS.md` at the repo root; the mirror at `C:\pxm\px110` was built with it removed (no commit, untracked), enumeration on the mirror empty, context probe `clean` (31 skills before, 0 after, `repo_scoped 0`, `plugin_cache_scoped 0`; the user's global `C:\Users\Brandon\.codex\AGENTS.md` exists and is recorded, not a stop), tool-surface probe `clean` (pass 1 four servers and 147 tools, pass 2 zero tools, `node_repl` silent; a mitigation, never proof of removal). Round 1 at head 888ce51, round 2 at 5e3d50d after an in-place `-Force` rebuild; both rounds wrapper exit 0 (`reply-present`), header `model: gpt-6-astra`, `provider: openai`, `reasoning effort: high`, `sandbox: read-only`, `workdir: C:\pxm\px110`, binder `clean` and `sealed` on both, round 2 resumed the round-1 session id. Effective route confirmed.

### Resolved points
| # | Claim | Raised by | Outcome | Evidence |
|---|-------|-----------|---------|----------|
| 1 | Deleting `agents/implementer.md` removes no capability a live surface needs; the delete is a session act because a Flash delete is unmeasured | session | PASS R1 | agents/escalation-implementer.md:3; agents/flash-implementer.md:102-103 |
| 2 | Empty-envelope rule makes mode diff adjudicate a reroute as zero-judgment without editing SKILL.md | session | PASS R1 | skills/multi-model-verify/SKILL.md:340-343 |
| 3 | Escalation file as parity twin keeps every test_seat_reshuffle.py pin | session | PASS R1 | evals/multi-model-verify/test_seat_reshuffle.py:101-110 |
| 4 | Hook exemption regex | session | FIX R1, accepted into Task 4: `\s*` crossed a newline and `(?![\w-])` accepted `parallax:escalation-implementer:other`; replaced with `(?m)^[ \t*_>-]*Lane:\**[ \t]*<agent>(?=[ \t]|\r?$)` | reviewer ran the quoted hook under pwsh; confirmed by reading the pattern |
| 5 | Six hook cases as oracles | session | FIX R1, accepted into Task 1: `run_hook` stripped stdout so whitespace-only output passed silent cases; every warning case now asserts agent, build lane and `Lane:`; four must-warn prompts added in one method | evals/multi-model-verify/test_multi_model_verify.py:2708 |
| 6 | Post-build sweep leaves no bare `implementer.md` under the test globs | session | FIX R1, accepted into Task 3 Step 4: `contract_coverage.py:28` and `test_contract_coverage.py:189` name the file; the session's sweep dropped those lines because each also names `flash-implementer.md` | evals/multi-model-verify/contract_coverage.py:28; test_contract_coverage.py:189 |
| 7 | frozen-plan-format.md rewrite keeps every raw-text pin on one physical line; no contract region touched | session | PASS R1 | frozen-plan-format.md:4,30; test_contract_coverage.py:793-801 |
| 8 | Lane note move keeps check-drift's literal parse | session | PASS R1 | tools/check-drift.ps1:295 |
| 9 | Sweep complete for live surfaces | session | FIX R1 (same two files as 6), accepted; doctor and drift explicit-none confirmed | commands/doctor.md:152-157; tools/check-drift.ps1:291-300 |
| 10 | README edits keep test_readme_reshuffle_pins | session | PASS R1 | test_seat_reshuffle.py:336-347 |
| 11 | Task 2's oracle masked broken agent edits behind an expected plan-format failure, and the DECISIONS pin was split across two lines in the plan's own text | reviewer | FIX R1, accepted into Task 1 (tests split: `test_agent_frontmatter_routes`, `test_escalation_empty_envelope_is_zero_judgment`) and Task 2 (one physical line) | plan text at 888ce51, Task 1 and Task 2 Step 1 |
| 12 | All four fixes applied as specified; hook behaviour under the amended regex; raw stdout keeps the nine existing cases green; failure sets eight then four | session | PASS R2 (confirming round, no new finding) | astra-plan-r2-reply.md |

### Escalated points (user-decided)
| # | Question | Session position | Reviewer position | Owner's call |
|---|----------|------------------|-------------------|--------------|
| none | | | | |

### Degraded-mode note
Not applicable. UNVERIFIED by the reviewer in both rounds: pytest totals (Python is not on the reviewer's PATH inside the sandbox) and the installed-superpowers canary, which reads outside the reviewed tree; the session's own gate run covers both.
