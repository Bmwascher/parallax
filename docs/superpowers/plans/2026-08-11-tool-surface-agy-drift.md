# 0.24.0 — the reviewer's tool surface, and the agy lane's contracts

**Status: DRAFT.** Not frozen. This is the session position going into the
mode-`plan` cross-vendor debate. Every number in it comes from
`rounds/2026-08-11-tool-surface-agy-drift/probe-record.md`, measured
2026-08-11.

## Goal

Close two open backlog items:

1. **Backlog item 7** — the reviewer's TOOL surface is unmeasured. 0.17.0
   measures the reviewer's PROMPT. Tools are not in the prompt, so a review
   can satisfy every rule the repo has while the auditor holds a code
   execution tool.
2. **Backlog item 11** — the agy lane has version tracking but no drift
   protection. Four of its five declared contracts have no check anywhere.

Both items say "shape of a fix, not decided" and both forbid a design
argued from parsing alone. The probe record was taken first for that
reason.

## What the measurements changed before any code was written

- Item 7's premise "there is no free tool-list view to measure against" is
  **false**. `codex app-server --stdio` answers `mcpServerStatus/list`,
  which names every resolved server and every tool. It starts no turn.
- The shipped isolation flags remove **125 of 128** tools. Nothing in this
  repo had measured that.
- `-c mcp_servers={}`, named as a candidate lever in item 7, is a **no-op**.
- `node_repl` and its `js` code-execution tool **survive** the shipped
  flags.
- A disabled server and a crashed server are **indistinguishable** in the
  record. That, not the tool list, is what constrains the design.
- Item 11's own version string moved from 1.1.8 to **1.1.12** with no
  contract check in between.
- `settings.json` carries `allowNonWorkspaceAccess: true` and nothing in
  this repo reads it.

## Architecture

Two independent surfaces, no ordering dependency between them.

**Item 7 — a new script `tools/codex-tool-surface-probe.ps1`.** Not an arm
of `codex-context-probe.ps1`. The transport is different (a JSON-RPC
session over stdio, versus one rendered document), the failure modes are
different, and that file is already 1083 lines. Its header comment names
item 7 as out of scope; the fix updates that comment to point at the new
script rather than growing the file.

**Item 11 — `tools/check-drift.ps1` and `commands/doctor.md`.** No new
script. The agy section grows from a version string to a contract set.

## Tech stack

PowerShell (Windows PowerShell 5.1 and PowerShell 7 both, per the repo's
dual-host rule), Python 3 stdlib and pytest for the eval side. No new
dependencies. `ConvertFrom-Json` for the JSON-RPC frames.

## Global constraints

Copy into every task's context.

- ASCII only in `tools/*.ps1`. Windows PowerShell 5.1 compatible.
- Every failure direction lands on BLOCKED. An unmade, failed, or
  unreadable measurement is never reported as a clean one.
- A claim may never be wider than its evidence.
- A test is not evidence until it has been watched to FAIL for the reason
  it claims. Record the failure text.
- A FIX is new code and gets no discount from any of the above.
- Contract text inside `contract:start`/`contract:end` markers must sit
  whole inside a single pin, and `DECLARED_REGIONS` must be edited in the
  same change.
- Stage by explicit path. Never `git add -A`, never `git add -u`.
- Bump the version LAST.

---

## Task 1 — the tool-surface probe, two-pass with a positive control

Build `tools/codex-tool-surface-probe.ps1`.

It starts `codex app-server --stdio`, sends `initialize` with
`capabilities.experimentalApi = true`, then `mcpServerStatus/list` and
`experimentalFeature/list`, and reads the resolved server and tool set.

**It runs TWO passes and the pair is the evidence.**

- **Pass 1, BASELINE, no isolation flags.** The instrument must be shown to
  work. It must observe at least one MCP server with a non-null
  `serverInfo` and at least one named tool. If pass 1 sees nothing, the
  probe is not known to be able to see anything, the measurement is UNMADE,
  and the verdict is BLOCKED. A clean pass 2 alone is never reported.
- **Pass 2, DISPATCH, with the exact flags the review dispatch uses.** The
  surviving tools are ENUMERATED, not counted.

**The verdict is an allowlist comparison, never a zero-count assertion.**
Finding 6 of the probe record is the reason: a crashed server and a
disabled one both report zero tools, so "assert zero" reads a crash as a
clean removal. The probe instead compares the pass-2 tool names against a
DECLARED ALLOWLIST and blocks on any tool it did not expect. Blocking on
the unexpected does not depend on being able to tell removal from silence.

**The residual is named, not hidden.** Pass 2 losing a tool is consistent
with two causes: the flag removed it, or it failed to launch. This design
does not resolve that ambiguity, and it does not need to for the
allowlist direction. Where it DOES matter is design question 1 below.

Exit codes match the existing probe: 0 clean, 1 blocked with the reason on
stdout, 2 script error. `-Json` emits the same shape as
`codex-context-probe.ps1` so the round evidence can carry both.

## Task 2 — decide and record what the allowlist contains

The allowlist is a contract, so it lives in the skill's reference text
inside `contract:start`/`contract:end` markers and is pinned.

The open question is `node_repl`. Two shapes, and the debate settles it:

- **Shape A.** Add `-c mcp_servers.node_repl.enabled=false` to the review
  dispatch. Measured to work (probe record finding 5). The allowlist is
  then EMPTY and every tool is a block.
- **Shape B.** Keep the dispatch as it is and declare `js`,
  `js_add_node_module_dir` and `js_reset` as accepted residuals with a
  written rationale.

Session position: **Shape A**, with the residual from finding 6 named in
the contract text rather than argued away. Shape B requires asserting that
a code-execution tool in a read-only reviewer is acceptable, and this repo
has no measurement of what `node_repl` can reach. That assertion would be
wider than its evidence.

## Task 3 — retract the false premise in item 7 and in the probe header

`tools/codex-context-probe.ps1:1-23` tells the reader the script "does not
read the reviewer's tool surface at all - see backlog item 7". Item 7 in
turn says no free tool-list view exists. Both statements outlive this
change and both would be false. Update each to point at the new probe and
to state what was measured.

Also record, in the item's closing note, that `-c mcp_servers={}` parses
and does nothing, so no future cycle proposes it again.

## Task 4 — tests for the tool-surface probe

Under `evals/multi-model-verify/`, driven through a stub `codex` the same
way the existing probe tests drive theirs. Cases must include, at minimum:

- pass 1 sees nothing -> BLOCKED, and the reason says the instrument was
  not shown to work.
- pass 1 clean, pass 2 carries a tool outside the allowlist -> BLOCKED
  naming that tool.
- pass 1 clean, pass 2 within the allowlist -> clean.
- the app-server exits non-zero, writes no frames, writes malformed JSON,
  or answers with an RPC `error` -> BLOCKED in every direction.
- the process hangs past a timeout -> BLOCKED, not clean.

Each must be watched to FAIL first, and the failure text recorded.

## Task 5 — extend agy drift watching from a version to its contracts

`tools/check-drift.ps1` currently runs `agy --version` and stores the
string (lines 127-130). Add, beside it, the contract set item 11
enumerates:

- the model literal parsed from `agents/flash-implementer.md` is present in
  `agy models` output. The literal has ONE home; the drift check reads it
  from there rather than repeating it.
- `~/.gemini/antigravity-cli/settings.json` parses as JSON and carries
  `trustedWorkspaces` as an array.
- the value of `allowNonWorkspaceAccess` is RECORDED in the snapshot, so a
  change to it is a drift.
- `~/.gemini/antigravity-cli/brain` exists.

**A narrower claim than item 11 asks for.** Item 11 lists the transcript
path as a contract. The transcript only exists AFTER a run, so a drift
check cannot assert it pre-dispatch. What the check CAN assert is that the
brain root exists. The transcript path itself stays where it is enforced
today, inside the Flash implementer's own evidence step, where a missing
transcript is already blocked. The plan states this narrowing explicitly
rather than letting a weaker check inherit the item's wording.

**Every one of these lands on a drift report, never on silence.** An agy
that is absent is a lane that is unavailable, which the drift report must
say. An `agy models` call that fails is not a passing identity check.

## Task 6 — make the doctor assert the same contracts

`commands/doctor.md:129-141` checks the binary and that `agy models`
contains the literal. Extend it to the settings file and the brain root,
so a drift is visible before a task is dispatched rather than after.

## Task 7 — tests for the agy contract checks

Through the existing drift state-machine harness against stub CLIs, so no
live agy call is needed. Every failure direction, watched to fail first.

## Task 8 — record what was measured but NOT decided

`allowNonWorkspaceAccess: true` is on, and this cycle establishes only
that it exists, that its value is `true`, and that nothing reads it. It
does not establish what agy does with it or whether the plugin set it.
Open a new backlog item for that measurement rather than acting on a guess.

Same for the `<repo>/.codex` enumeration gap in the probe record: the
preflight sweep does not cover it, codex loads project-local skills from
it, and this repo's copy is empty. A gap in the enumeration, not a live
exposure, and a separate item.

## Task 9 — the version bump, last

`.claude-plugin/plugin.json` to 0.24.0, then `claude plugin update
parallax@parallax`, then verify the CACHE CONTENTS by hash rather than by
the version number.

---

## Design questions for the debate

**DQ1 — the survivor control.** Under shape A, pass 2 shows `node_repl`
gone. That is consistent with the flag working AND with a launch failure,
and finding 6 says the record cannot separate them. Is there a sound
survivor control — some server or signal that must REMAIN visible in pass 2
— that would distinguish "the environment is healthy and the flag worked"
from "the MCP subsystem died"? Or is the honest answer that this direction
of the check is a mitigation rather than a control, and must be labelled
that way in the contract text?

**DQ2 — shape A or shape B for `node_repl`.** Session position is A. What
breaks it?

**DQ3 — a version floor for agy.** Item 11 offers a floor, the way the
Fable panel lane has Claude Code 2.1.216. This plan declines it: the only
agy version anything has been measured on is 1.1.12, and a floor asserted
at the version that happens to be installed is a claim with no measurement
under it. Is declining right, or does a floor at the measured version carry
real protection the contract checks do not?

**DQ4 — `allowNonWorkspaceAccess: true`.** Watch it and open an item
(session position), or treat it as a defect this cycle fixes? The plugin
has no measurement of what it permits.
