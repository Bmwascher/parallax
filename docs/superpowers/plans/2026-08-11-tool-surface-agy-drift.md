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
   protection. NONE of its five declared contracts has a DRIFT-SIDE check.
   (Corrected at round 3: an earlier draft said four of five, which
   silently counted the stored version string as the fifth contract. It is
   not one of them; `backlog:787-800` lists the five and the version
   string is not among them.) They are not unchecked: the Flash
   implementer enforces the known operational ones per dispatch and after
   the run. See Task 5.

Both items say "shape of a fix, not decided" and both forbid a design
argued from parsing alone. The probe record was taken first for that
reason.

## What the measurements changed before any code was written

- Item 7's premise "there is no free tool-list view to measure against" is
  **false**. `codex app-server --stdio` answers `mcpServerStatus/list`,
  which names every resolved server and every tool. It starts no turn.
- With the shipped isolation flags, **125 fewer of 128** tools are
  reported. Nothing in this repo had measured that. The wording is
  deliberate: what was measured is what the client REPORTS, and finding 6
  is why that is not the same as what was removed.
- `-c mcp_servers={}`, named as a candidate lever in item 7, is a **no-op**.
- `node_repl` and its `js` code-execution tool **survive** the shipped
  flags.
- A disabled server and a crashed server are **indistinguishable** in the
  record. That, not the tool list, is what constrains the design.
- Item 11's own version string moved from 1.1.8 to **1.1.12** with no
  drift-side contract check in between.
- `settings.json` carries `allowNonWorkspaceAccess: true`. No CHECK reads
  it, though the 0.12.0 build did MEASURE it once: `false` soft-denied the
  lane's own writes on agy 1.1.7, which is why `true` is there.

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

## Task 1 — the tool-surface probe, two-pass with an instrument calibration

Build `tools/codex-tool-surface-probe.ps1`.

It starts `codex app-server --stdio`, sends `initialize` with
`capabilities.experimentalApi = true`, then `mcpServerStatus/list` and
`experimentalFeature/list`, and reads the resolved server and tool set.

**It runs TWO passes and the pair is the evidence.**

- **Pass 1, BASELINE, no isolation flags. This is an INSTRUMENT
  CALIBRATION, not a control.** The probe must be shown able to see
  anything at all: at least one MCP server with a non-null `serverInfo`
  and at least one named tool. If pass 1 sees nothing, the probe is not
  known to be able to see anything, the measurement is UNMADE, and the
  verdict is BLOCKED. A clean pass 2 alone is never reported.
- **Pass 2, DISPATCH, with the exact flags the review dispatch uses.** The
  surviving tools are ENUMERATED, not counted.

**What the pair does and does not establish** (settled at plan round 1,
after the reviewer refuted an earlier draft that called it a positive
control):

- A tool PRESENT in pass 2 that the allowlist does not name is a real
  DETECTION. Observing something present never depends on telling removal
  from silence.
- A tool ABSENT from pass 2 is a MITIGATION. It is observationally
  identical to that server having failed to launch, per probe-record
  finding 6, and pass 1 says nothing about the MCP subsystem's health
  under pass-2 conditions.

Neither the script, the skill, nor any report may describe this as
verified reviewer isolation on the tool axis.

**And "control" is not the right word for the presence direction either**
(round 2). A detection is what happens when a tool IS observed. Nothing
measured establishes that every tool actually present WILL be observed, so
there is no guarantee running in the other direction. The word this design
is entitled to is DETECTION, and only about what it saw.

**The verdict is an allowlist comparison, never a zero-count assertion.**
Finding 6 of the probe record is the reason: a crashed server and a
disabled one both report zero tools, so "assert zero" reads a crash as a
clean removal. The probe instead compares the pass-2 tool names against a
DECLARED ALLOWLIST and blocks on any tool it did not expect. Blocking on
the unexpected does not depend on being able to tell removal from silence.

**The residual is named, not hidden.** Pass 2 losing a tool is consistent
with two causes: the flag removed it, or it failed to launch. This design
does not resolve that ambiguity. It does not need to for the presence
direction, and it cannot for the absence direction. Design question 1
asked whether a survivor control could close it; the round-1 answer was
that none exists in the measured configuration, because after the shipped
flags `node_repl` is the ONLY remaining server, so shape A makes the only
candidate survivor unreported too.

Exit codes match the existing probe: 0 clean, 1 blocked with the reason on
stdout, 2 script error. `-Json` emits the same shape as
`codex-context-probe.ps1` so the round evidence can carry both.

## Task 2 — decide and record what the allowlist contains

The allowlist is a contract, so it lives in the skill's reference text
inside `contract:start`/`contract:end` markers and is pinned.

The open question is `node_repl`. Two shapes, and the debate settles it:

- **Shape A.** Add `-c mcp_servers.node_repl.enabled=false` to the review
  dispatch. Measured to produce ZERO REPORTED TOOLS, with removal versus
  launch failure unresolved (probe record findings 5 and 6). The allowlist
  is then EMPTY and every tool is a block.
- **Shape B.** Keep the dispatch as it is and declare `js`,
  `js_add_node_module_dir` and `js_reset` as accepted residuals with a
  written rationale.

**Settled at plan round 1: Shape A**, with three conditions the reviewer
attached and this plan adopts.

- It applies to BOTH the fresh dispatch and the resume dispatch, which
  today carry identical isolation flags (`SKILL.md:175-188` and
  `SKILL.md:237-250`). A resume that drops the flag would silently restore
  the tool for every round after the first.
- It ships as RISK REDUCTION with an empty allowlist, never described as
  verified isolation.
- The residual from probe-record finding 6 is written into the contract
  text rather than argued away.

Shape B was rejected because it requires asserting that a code-execution
tool in a read-only reviewer is acceptable, and this repo has no
measurement of what `node_repl` can reach. That assertion would be wider
than its evidence. Nothing measured suggests disabling it changes review
behaviour.

## Task 3 — retract the false premise everywhere it is written

SIX standing surfaces carry claims this cycle falsifies. The first draft
named two, round 1 found two more, round 2 found the fifth, and round 3
found the sixth. Task 3 updates ALL of them, plus the test that pins one
of them.

The count moved three times, which is itself the reason this task exists:
the premise was written into more places than anyone remembered, and every
sweep found what the last one missed.

1. `tools/codex-context-probe.ps1:1-23` — the header telling the reader
   the script "does not read the reviewer's tool surface at all - see
   backlog item 7". Point it at the new probe.
2. `skills/multi-model-verify/SKILL.md`, contract region
   `client-probe-scope-limit` — "`codex debug` offers no tool-list view to
   measure instead" and "Backlog item 7 holds the tool half".
3. `README.md:186-200` — states independently that the reviewer's tool
   surface "is not in the prompt and is not measured ... Tracked as
   backlog item 7". Nothing in an earlier draft touched this.
4. Backlog item 7 itself, including its closing note that `-c
   mcp_servers={}` parses and does nothing, so no future cycle proposes
   it again.
5. `docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:378-395`
   — the accepted-limits section, which states that the tool surface is
   "out of reach of this mechanism", that "there is no free tool-list view
   to measure", and that the removal levers are unverified.

**Surface 5 needs a SPLIT, not a rewrite, and this is the subtle part.**
That same document, at lines 184-197, records a DIFFERENT and still-real
limit: `codex debug prompt-input` rejects `--sandbox` and `-m`, so full
flag parity with the dispatch cannot be REQUESTED, and whether model or
sandbox selection changes rendered prompt content is UNVERIFIED. The
document currently calls that "the same missing surface backlog item 7
describes". After this cycle it is NOT the same surface: the tool-list
half is measured, the prompt-parity half is not. Task 3 retracts the
no-free-tool-list premise and the item-7 linkage, and PRESERVES the
prompt-parity limit as its own unverified item.

`docs/superpowers/specs/2026-07-29-mirror-z-capture-design.md:354-360`
says item 7 was outside that cycle's scope. That is a historical statement
about a past cycle, it stays true, and Task 3 does not touch it.

6. `docs/superpowers/plans/rounds/2026-08-11-tool-surface-agy-drift/README.md`
   — THIS CYCLE'S OWN DEBATE RECORD. Found at round 3, and the most
   embarrassing of the six: it was written between rounds 1 and 2, states
   the round-1 conclusions in its own words, and was never revisited when
   rounds 2 and 3 corrected them. It repeats the control/removal language
   and the "doctor mirrors two" miscount.

**The rule for surface 6, because it is not like the other five.** The
retained `plan-brief-r*.md` and `plan-reply-r*.txt` files are VERBATIM
HISTORICAL ARTIFACTS and must never be rewritten; a brief that was sent
and a reply that was received are what they were. The README is a
SYNTHESIZED STANDING RECORD, which is a different kind of document: it is
read as current. So it keeps its round-1 history, and the superseded
conclusions are marked superseded in place with the adjudication that
replaced them appended. Editing it is not falsifying the record; leaving
it is.

**Surface 2 is pinned, and the pin is part of this task, not follow-up.**
`evals/multi-model-verify/test_multi_model_verify.py:762-782`
(`test_the_probe_does_not_claim_the_tool_surface`) asserts that region
VERBATIM as one multi-line literal. Editing the region without editing the
pin turns a documentation fix into a red suite. Per `CLAUDE.md`, change
the test first. `DECLARED_REGIONS` in
`evals/multi-model-verify/test_contract_coverage.py:666-676` keeps the
region declared; if the edit splits or renames it, that file changes too.

**What the replacement text must NOT say.** The region exists to stop a
clean probe reading as full reviewer isolation. The new text must keep
that stop. The tool axis moves from "unmeasured" to "measured, with the
absence direction a mitigation" — which is still not full isolation.

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

**What this task is NOT, corrected at plan round 1.** It is not adding
checks that do not exist. `agents/flash-implementer.md:45-59` already runs
three of item 11's contracts as a per-dispatch preflight, lines 100-105
forbid any approval-bypass flag, and lines 81-92 block a missing
transcript after the run. Those stay exactly as they are.

The gap is that the WEEKLY DRIFT WATCHER covers none of them, so a drift
is discovered when a task is dispatched and blocked, mid-build, on a
frozen plan, with the budget already committed. This task moves the
discovery earlier. It does not replace the enforcement.

The doctor's coverage is stated precisely, because an earlier draft
miscounted it (round 2). `commands/doctor.md:129-144` checks that the
binary exists and that `agy models` contains the declared literal. That is
MODEL DECLARATION AND REACHABILITY, and the doctor's own note says the
route language it offers is client-side requested/propagated only. It is
not two of item 11's five contracts, and calling it that inflates what
exists today.

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

**The agy VERSION CHANGE must be reported, and today it is not.** Round 2
found this and it is a real omission, not a wording point. `check-drift`
emits an explicit change note for codex (`tools/check-drift.ps1:321-323`)
and for superpowers (`:324-326`). agy is only carried forward and saved
(`:274`, `:280`, `:355`), so 1.1.8 becoming 1.1.12 produced no note at
all, which is exactly how item 11's own version moved four releases
unremarked. DQ3's answer was "report version changes"; without this step
the plan records that answer without making it happen.

Add: an agy version differing from the snapshot emits a NOTE in the same
form as the codex and superpowers ones.

**And an unreadable version must be a FINDING, not a note. Round 3 caught
this as a false-clean introduced by the round-2 fix itself.** In this
script the two are not interchangeable. Notes are printed under a "Notes:"
heading (`tools/check-drift.ps1:345-348`) and sit happily beside "No
findings." (`:341`), and the exit is decided by findings alone:
`if ($findings.Count -eq 0) { exit 0 }` (`:411`). So specifying an
unreadable agy version as a note would make an unmade measurement exit
CLEAN, which is the exact invariant this plan opens by declaring.

The rule, stated so the builder cannot get it wrong:

- version READ and CHANGED -> a note, exit unaffected.
- version READ and unchanged -> nothing.
- version ABSENT, UNREADABLE, or UNPARSEABLE -> a FINDING, non-clean exit,
  and the prior snapshot value is PRESERVED rather than overwritten with
  an empty one.

The carry-forward at `:274` and `:280` stays, because losing the last
known good value would destroy the comparison the next run needs. What
must not survive is the carry-forward happening SILENTLY.

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

Cases must include, at minimum:

- each contract failing, and the drift report naming which one;
- the agy version CHANGING, and a note appearing in the report;
- the agy version being ABSENT, UNREADABLE or UNPARSEABLE, asserting BOTH
  the finding text AND a non-clean exit code, and asserting the prior
  snapshot value survives;
- agy absent entirely, reported as the lane being unavailable.

**Assert the exit code, not only the text.** The unreadable case is the
one most likely to pass while proving nothing: notes and findings both
appear in the report, so a test that greps the report for a phrase passes
identically whether the run exited 0 or non-zero. The exit code is the
part that carries the invariant.

The carry-forward is the second trap: the existing code path already
carries the old value forward, so a test that only asserts "a version is
present" passes whether or not anything was measured this run.

## Task 8 — record what was measured but NOT decided

**`allowNonWorkspaceAccess`.** Corrected at plan round 1: it HAS been
measured once. `docs/superpowers/plans/2026-07-25-flash-implementer.md:590-603`
records the 0.12.0 build setting it to `false`, watching a trusted-workspace
print-mode write get soft-denied, restoring `true`, and documenting
"allowNonWorkspaceAccess=true required for print-mode writes as of agy
1.1.7". So `true` was a measured lane requirement ON AGY 1.1.7.

**The residual is TWO questions, not one** (round 2 corrected an earlier
draft that named only the second and, in naming only it, quietly promoted
a version-bounded measurement into a present-tense requirement):

1. Does `false` STILL soft-deny the lane's intended trusted-workspace
   writes on 1.1.12? The 1.1.7 result does not answer this. If it no
   longer denies, `true` is no longer required and the setting can simply
   go.
2. What does `true` permit OUTSIDE the workspace, on 1.1.12?

The follow-up item must re-test both. Recording the value as watched drift
answers neither and must not be presented as closing them. Item 11's
security contract is marked explicitly UNMEASURED, and item 11 stays
partially open on that point when the rest of it closes.

**The `<repo>/.codex` enumeration gap.** Also corrected: it was already
known, at
`skills/multi-model-verify/references/model-prompting-notes.md:288-291`
("'.codex/' stays unswept — unprobed; probe before adding"). This cycle
reconfirms it and retracts the unsupported half of the earlier draft: that
codex loads project-local skills from there even when the project is
untrusted was the client's description, never a measurement, and no canary
artifact exists. The reachability stays UNPROBED. The follow-up item is to
probe it, not to widen the sweep on an unmeasured premise.

## Task 9 — the version bump, last

`.claude-plugin/plugin.json` to 0.24.0, then `claude plugin update
parallax@parallax`, then verify the CACHE CONTENTS by hash rather than by
the version number.

---

## Design questions — ANSWERED at plan round 1

**DQ1 — the survivor control. No sound survivor exists in the measured
configuration.** After the shipped flags, `node_repl` is the only
remaining MCP server, so shape A makes the only candidate survivor
unreported too, with disable versus launch failure unresolved, and
`experimentalFeature/list` answering proves only that the app-server is
alive. The absence direction is labelled a MITIGATION. A real control
would need a newly measured MCP failure diagnostic, a resolved-config
echo, or a harmless pass-2 survivor; none is measured, so none is claimed.

**DQ2 — Shape A**, applied to the fresh AND resume dispatches, shipped as
risk reduction with an empty allowlist, never called verified isolation.
See Task 2.

**DQ3 — no version floor for agy.** A floor means "below this the lane is
unavailable", as `tools/check-drift.ps1:250-257` does for the Kimi lane.
No agy breakage boundary has been measured; 1.1.12 is simply today's
version. Instead: report version changes, run the behavioural contract
checks on every drift run, block failed or unreadable checks, and retain
1.1.12 as the OBSERVED BASELINE rather than a compatibility boundary.

**DQ4 — watch `allowNonWorkspaceAccess` and open the focused measurement
item; do not flip it this cycle.** `false` was measured to break the
lane's intended writes on agy 1.1.7. Two things stay unmeasured on 1.1.12:
whether `false` still denies, and what `true` permits outside the
workspace. See Task 8.
