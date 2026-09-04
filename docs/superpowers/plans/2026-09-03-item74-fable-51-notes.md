# Item 74: Fable 5.1 prompting notes and two dispatch-contract defects — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bring the multi-model-verify skill's Fable guidance up to Claude
Fable 5.1, and make the prepared dispatch command runnable as printed.

**Architecture:** Three independent edits, each reviewable alone. Task 1 is
a PowerShell tool plus its contract test. Task 2 is two prose corrections in
`SKILL.md` under a hard token budget. Task 3 rewrites one reference section
and adds the pins that stop it drifting back into a false measurement.
Nothing here changes the debate protocol, the transport, or any lane's
identity evidence.

**Tech Stack:** PowerShell (Windows PowerShell 5.1 and PowerShell 7),
Python 3.12 with pytest, Markdown skill and reference bodies.

**Spec:** `docs/superpowers/plans/2026-07-27-0150-backlog.md`, item 74. Read
that item in full before starting; it carries the panel's corrections and
the reasons for each, including two corrections to its own earlier drafts.

## Global Constraints

- **`SKILL.md` MUST STAY UNDER ITS HARD CEILING OF 6500 TOKENS.** Measured
  2026-09-03: the body is 413 lines against a warn threshold of 400 and a
  spec limit of 500, and roughly 6437 tokens against a budget of ~5250 and
  that hard ceiling. About 63 tokens of headroom. Task 2's replacement is
  MEASURED as 12 characters longer per occurrence and there are two
  occurrences in `SKILL.md`, so this branch spends headroom rather than
  saving it; that is accepted, and the ceiling is the gate. Prefer wording
  that is neutral or shorter where it costs nothing. Re-run
  `python evals/tools/skill_lint.py skills/multi-model-verify --strict`
  after every `SKILL.md` edit and record the reported token count. If the
  lint reports an ERROR rather than a WARN, or the count reaches 6500, STOP
  and report rather than trimming unrelated text to make room.
- **`tools/dispatch-round.ps1` is "Windows PowerShell 5.1 compatible, ASCII
  only"** (its own header, `tools/dispatch-round.ps1:128`). No non-ASCII
  character may enter that file.
- **Tests change first.** The transport commands and the reviewer isolation
  flags are live-verified contracts; `CLAUDE.md` requires the test edit to
  precede the code edit.
- **Pin integrity.** A pin matching RAW file text needs its phrase unbroken
  on ONE PHYSICAL LINE; a pin built on the whitespace-normalized read does
  not. Both forms are in use and nothing marks which is which. Before
  editing near any pinned phrase, find the assertion and check which read it
  uses. Prefer restructuring prose to keep an existing pin green over
  editing the pin to fit new prose.
- **`test_dispatch_round.py` is WINDOWS ONLY and single-host per run.**
  `PARALLAX_PS_HOST` selects the interpreter. A green suite on one host
  proves one interpreter, so Task 1 runs it under BOTH.
- **Do not bump `.claude-plugin/plugin.json`.** The version bump happens
  AFTER the diff debate, never as a build task. A version consumed before
  the branch is finished recovers only by another bump.
- **Two facts are UNVERIFIED and may not be written as measured:** what the
  `model: fable` alias resolves to in the running harness, and what effort
  level the harness gives a Fable seat. No seat file declares an effort.
  Any sentence about either must be conditional.

## File Structure

| File | Responsibility | Task |
|---|---|---|
| `evals/multi-model-verify/test_dispatch_round.py` | Pins the prepared command's shape. Changes first. | 1 |
| `tools/dispatch-round.ps1` | Builds the printed command at line 588. | 1 |
| `skills/multi-model-verify/SKILL.md` | Two prose corrections, under budget. | 2 |
| `evals/multi-model-verify/test_multi_model_verify.py` | Gains one pin for the corrected dispatch wording; gains the Fable-section pins. | 2, 3 |
| `skills/multi-model-verify/references/model-prompting-notes.md` | The `### Fable 5` section, rewritten for 5.1. | 3 |
| `evals/multi-model-verify/test_seat_reshuffle.py` | Holds the existing heading pin that must stay green. | 3 |

---

### Task 1: the prepared command runs as printed

**Files:**
- Modify: `evals/multi-model-verify/test_dispatch_round.py:429-435`
- Modify: `tools/dispatch-round.ps1:588`

**Interfaces:**
- Consumes: nothing from other tasks.
- Produces: the `command` field of `-Prepare -Json` becomes
  `& "<hostPath>" -NoProfile -NonInteractive -File "<wrapperDest>"`.
  No other field changes. `taskName`, `wrapper`, `dispatchDir` and `round`
  are untouched.

**Why:** measured 2026-09-03. `SKILL.md` says to dispatch the printed
command verbatim. The printed string starts with a quoted executable path,
which PowerShell parses as a string expression, so running it verbatim is a
`ParserError` and the round never starts. In the measured case the wrapper
had not run, so no reservation existed and the retry was clean. Had the
wrapper started, its create-new reservation would have refused the retry and
the round would have been lost.

- [ ] **Step 1: Change the pin to require a runnable command**

In `evals/multi-model-verify/test_dispatch_round.py`, replace the body of
`test_prepare_emits_a_command_naming_the_resolved_host` with:

```python
def test_prepare_emits_a_command_naming_the_resolved_host(tmp_path):
    out = prepare_default(tmp_path, json_mode=True)
    got = json.loads(out.stdout)
    assert got["command"].endswith(
        "-NoProfile -NonInteractive -File \"%s\"" % got["wrapper"])
    # The command must RUN AS PRINTED. A bare quoted path is a string
    # expression in PowerShell, so a caller following SKILL.md's
    # "verbatim" instruction got a ParserError and no round (measured
    # 2026-09-03). The call operator is what makes verbatim true.
    assert got["command"].startswith('& "')
    assert got["taskName"] == "Sol R1 debate round"
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest evals/multi-model-verify/test_dispatch_round.py::test_prepare_emits_a_command_naming_the_resolved_host -v`

Expected: FAIL on the `startswith('& "')` assertion, because the tool still
emits a command beginning with `"`.

- [ ] **Step 3: Make the tool print a runnable command**

In `tools/dispatch-round.ps1`, line 588 currently reads:

```powershell
$command = '"' + $hostPath + '" -NoProfile -NonInteractive -File "' + $wrapperDest + '"'
```

Replace it with:

```powershell
# The call operator is not decoration. A command beginning with a quoted
# path is a STRING EXPRESSION to PowerShell, so a caller told to run this
# verbatim gets a ParserError and no round (measured 2026-09-03).
$command = '& "' + $hostPath + '" -NoProfile -NonInteractive -File "' + $wrapperDest + '"'
```

ASCII only; the comment above contains no non-ASCII character.

- [ ] **Step 4: Run the test to verify it passes**

Run: `python -m pytest evals/multi-model-verify/test_dispatch_round.py -v`

Expected: PASS, whole module.

- [ ] **Step 5: Run the module under BOTH PowerShell hosts**

```bash
python -m pytest evals/multi-model-verify/test_dispatch_round.py -q
```

then, in PowerShell:

```powershell
$env:PARALLAX_PS_HOST = 'powershell'; python -m pytest evals/multi-model-verify/test_dispatch_round.py -q; Remove-Item Env:PARALLAX_PS_HOST
```

Expected: PASS under both. Record both counts in the task report. A green
suite on one host proves one interpreter.

- [ ] **Step 6: Commit**

```bash
git add evals/multi-model-verify/test_dispatch_round.py tools/dispatch-round.ps1
git commit -m "make the prepared dispatch command runnable as printed"
```

---

### Task 2: correct two SKILL.md sentences under the token budget

**Files:**
- Modify: `skills/multi-model-verify/SKILL.md:200-202` (the `-DispatchHost`
  sentence) and `:213` and `:301` (the two identical dispatch sentences)
- Modify: `skills/multi-model-verify/references/backup-lane.md:143`, `:205`
  and `:558` (the same dispatch sentence, three more times)
- Modify: `evals/multi-model-verify/test_multi_model_verify.py`

**Interfaces:**
- Consumes: Task 1's command shape. Task 2's wording describes a command
  that already carries the call operator, so Task 1 lands first.
- Produces: no interface other tasks read.

**Why:** two wording defects, both hit while convening this item's own
review panel. The first is a real contradiction. The second is ambiguity
that cost one attempt and is a clarity fix, not a bug.

**Pin check before editing.** `"dispatch it as a harness background command"`
and `` "the `taskName` the tool printed" `` are pinned in
`evals/multi-model-verify/test_backup_lane.py:2068` and
`evals/multi-model-verify/test_multi_model_verify.py:3500`. Both phrases must
survive intact and unbroken. The phrase `` "using `command` verbatim" `` is
NOT pinned anywhere and is the part being replaced.

- [ ] **Step 1: Record the starting token count**

Run: `python evals/tools/skill_lint.py skills/multi-model-verify --strict`

Write the reported line count and token count into the task report. This is
the number Step 6 must not exceed.

- [ ] **Step 2: Add a pin for the corrected dispatch wording**

In `evals/multi-model-verify/test_multi_model_verify.py`, inside
`test_both_lanes_dispatch_the_printed_command_as_a_named_task`, add a third
assertion so the corrected wording cannot silently regress:

```python
def test_both_lanes_dispatch_the_printed_command_as_a_named_task(body_skill, body_backup_lane):
    for body in (body_skill, body_backup_lane):
        assert body.count("dispatch it as a harness background command") >= 1
        assert "the `taskName` the tool printed" in body
        # The printed command carries its own call operator (Task 1), so
        # "verbatim" is now true rather than aspirational. A body that
        # tells a caller to strip or retype it reintroduces the
        # ParserError measured 2026-09-03.
        assert "exactly as printed" in body
```

- [ ] **Step 3: Run it to verify it fails**

Run: `python -m pytest "evals/multi-model-verify/test_multi_model_verify.py::test_both_lanes_dispatch_the_printed_command_as_a_named_task" -v`

Expected: FAIL on `"exactly as printed" in body`, for both bodies.

- [ ] **Step 4: Replace both dispatch sentences**

The clause `` using `command` verbatim `` occurs FIVE times across two
files, measured 2026-09-03: `SKILL.md:213` and `:301`, and
`references/backup-lane.md:143`, `:205` and `:558`. Replace the clause in
all five, leaving the rest of each sentence byte-identical:

- from: ``using `command` verbatim``
- to:   ``running `command` exactly as printed``

For reference, the resulting SKILL.md sentence reads:

```text
   `-Prepare` prints `command` and `taskName`: dispatch it as a harness background command, running `command` exactly as printed, under the `taskName` the tool printed, and STOP — but never END THE TURN with the round unfinished (references/model-prompting-notes.md's round-dispatch-operation).
```

**The replacement is LONGER, by 12 characters per occurrence**, measured
rather than estimated. Only the two `SKILL.md` occurrences count against the
token budget, since `backup-lane.md` is a reference rather than the skill
body. That is expected to cost a handful of tokens against roughly 63 of
headroom, but it is NOT assumed: Step 6's lint run is the gate, and if the
count rises past the ceiling, shorten to ``running `command` as printed``
(4 characters longer than the original) rather than accepting the increase.

Keep each sentence on ONE PHYSICAL LINE: the two pinned phrases are
raw-text pins and a rewrap would break them.

- [ ] **Step 5: Replace the `-DispatchHost` sentence**

`skills/multi-model-verify/SKILL.md:200-202` currently reads:

```text
   Run `-Prepare`, naming `-DispatchHost` explicitly as the caller's own
   host (`pwsh` or `powershell`, matching `(Get-Process -Id $PID).Path`,
   never a bare name) and passing `-WorkdirEvidence` with the resolved
```

Replace those three lines with:

```text
   Run `-Prepare`, naming `-DispatchHost` explicitly as the caller's own
   host — the bare token `pwsh` or `powershell`, DERIVED from
   `(Get-Process -Id $PID).Path` rather than guessed; the tool refuses a
   full path — and passing `-WorkdirEvidence` with the resolved
```

The tool accepts only the bare token: `tools/dispatch-round.ps1` rejects a
full path with `ERROR: -DispatchHost must be exactly 'pwsh' or 'powershell'`.
The old wording's "never a bare name" reads as forbidding the only accepted
value.

- [ ] **Step 6: Run the pin suite and the budget check**

```bash
python -m pytest evals/multi-model-verify/test_multi_model_verify.py evals/multi-model-verify/test_backup_lane.py -q
```

Expected: PASS, including the new assertion.

```bash
python evals/tools/skill_lint.py skills/multi-model-verify --strict
```

Expected: PASS, with the same two size WARNs the run already emits and no
ERROR. The count is EXPECTED TO RISE, because the replacement is measured as
longer; what must hold is that it stays below the hard ceiling of 6500.
Record the new count beside Step 1's in the task report. If it reaches 6500,
or the lint reports an ERROR, STOP and report rather than trimming unrelated
text to make room.

- [ ] **Step 7: Commit**

```bash
git add skills/multi-model-verify/SKILL.md skills/multi-model-verify/references/backup-lane.md evals/multi-model-verify/test_multi_model_verify.py
git commit -m "say how to run the prepared command and what -DispatchHost takes"
```

---

### Task 3: rewrite the Fable notes for 5.1

**Files:**
- Modify: `skills/multi-model-verify/references/model-prompting-notes.md`,
  the `### Fable 5` section (currently lines 28-70)
- Modify: `evals/multi-model-verify/test_multi_model_verify.py`
- Read only, must stay green: `evals/multi-model-verify/test_seat_reshuffle.py:288-292`

**Interfaces:**
- Consumes: nothing from Tasks 1 and 2.
- Produces: no interface other tasks read.

**Existing pin that must stay green.** `test_seat_reshuffle.py:290` asserts
`"### Fable 5" in notes`. Renaming the heading to `### Fable 5.1` KEEPS that
pin green, because the assertion is a substring test. Do not delete the
heading or change its level.

- [ ] **Step 1: Add pins for the three claims that must not drift**

In `evals/multi-model-verify/test_multi_model_verify.py`, add:

```python
def test_fable_notes_are_51_and_keep_their_measurement_limits():
    """0.29.0 item 74. Three sentences in the Fable section are the ones
    a future edit is most likely to turn into a false measurement, so
    each is pinned. Normalized read: these phrases wrap in the
    reference and no needle here contains a newline.
    """
    notes = " ".join(read(REFERENCES / "model-prompting-notes.md").split())
    # The seats carry an unversioned alias; what it resolves to is not
    # measured and may never be written as if it were.
    assert ("the seats declare the unversioned alias `model: fable`, so"
            " which model they run is UNVERIFIED") in notes
    # Effort: the 5.1 guide says re-run the sweep across models, and no
    # seat file declares an effort at all.
    assert ("effort level names do not correspond to the same amount of"
            " thinking across models, so the Fable 5 sweep does not"
            " carry") in notes
    # The conversation-binding item is a FORWARD-LOOKING risk. It cannot
    # explain the three measured failures; saying it can would invent a
    # measurement, which is the one thing these notes may never do.
    assert ("cannot explain the three `No transcript found` failures,"
            " which were measured on 2.1.233 in the 0.25.0 cycle") in notes
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest "evals/multi-model-verify/test_multi_model_verify.py::test_fable_notes_are_51_and_keep_their_measurement_limits" -v`

Expected: FAIL on the first assertion.

- [ ] **Step 3: Rewrite the section**

Replace the `### Fable 5` heading and its bullets with the following. Every
claim below is carried from item 74 and was verified by at least one panel
lane against repo files; do not add claims that item 74 does not carry.

```markdown
### Fable 5.1

From the official Fable 5.1 guide
(platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5-1,
fetched 2026-09-03) — the three seat-invariant rules above appear in it
near-verbatim; Fable-specific additions:

- Bug-finding recall is a documented strength — the basis for the
  fable-reviewer seat.
- **Which model the seats run is not established here.** All three of
  the seats declare the unversioned alias `model: fable`, so which model
  they run is UNVERIFIED from the tree; that alias is itself pinned by
  `evals/multi-model-verify/test_seat_reshuffle.py`, so introducing a
  versioned pin would be a tests-first change.
- **Effort must be re-swept, and today governs nothing.** The 5.1 guide
  states that effort level names do not correspond to the same amount of
  thinking across models, so the Fable 5 sweep does not carry. No Fable
  seat file declares an effort at all, so the previous guidance applied
  to nothing. Sweep with evals, never silently.
- **A truncated reply corrupts a retained artifact.** At `xhigh` and
  `max`, 5.1 can spend its budget thinking before it writes. The
  whole-branch reviewer's RAW reply is the artifact
  (agents/fable-reviewer.md, SKILL.md's mode diff), and nothing checks
  that a retained reply reached its last section. Leave room for the
  reply, not just the thinking.
- **Prefer targeted edits.** 5.1 rewrites whole files for small changes
  more readily than 5 did. In this repo a rewrite reflows paragraphs, and
  a reflow turns a raw-text pin red without changing a word.
  agents/escalation-implementer.md is the only Fable seat with write
  tools; the other two are read-only by tool grant.
- **Unmarked quoting, narrowly.** 5.1 more often reproduces source text
  without marking it as a quotation. The debate protocol already strikes
  UNCITED claims, so the case that evades detection is repo text carrying
  a RESOLVING citation and presented as a finding.
- **Classifier refusals have no class.** 5.1 can return
  `stop_reason: "refusal"` on benign code work. fallbacks.md carries no
  refusal class for any lane. The cross-vendor lane has its own recorded
  refusal shape at
  docs/superpowers/specs/2026-08-31-dispatch-options-costing.md:54-55,
  distinct from item 47's decline-and-exit-0.
- **Scope behaviour CONVERGES with the escalation seat's existing
  guard**, which already forbids improvements, drive-by refactors and
  scope adjustments. Check whether that wording covers 5.1's named
  behaviours, nearby fixes and extra test files, and add only what is
  missing. That seat has never been used and item 55 proposes retiring
  it.
- Never instruct a Fable seat to echo or transcribe its internal
  reasoning (the reasoning_extraction refusal class): report contracts
  ask for evidence and decisions, never thinking.
- **Conversation binding is a FORWARD-LOOKING risk, not an explanation.**
  5.1 binds thinking blocks to the conversation that produced them, and a
  changed prefix returns an error or drops the blocks. It cannot explain
  the three `No transcript found` failures, which were measured on
  2.1.233 in the 0.25.0 cycle
  (`.superpowers/sdd/2026-08-15-resume-preamble-refresh/progress.md`);
  the binding rule applies to accounts created on or after 2026-08-31 and
  its symptom is an API error, not a transcript lookup failure. The
  2026-08-19 probe measured nine clean resumes and no failures, and lists
  three tested hypotheses and three candidates, so nothing here may say a
  mechanism is unidentified either.
- The one same-harness Fable seat that RESUMES is the panel lane; the
  whole-branch reviewer and the escalation implementer are
  single-dispatch and never resume. Resume probe, 2026-07-26, Claude
  Code 2.1.220, re-run across five conditions 2026-08-19 on 2.1.237:
  the resume surface carries no model parameter, and containment -
  model pin, system prompt, read-only grant - survived every resume
  where it was capability-tested, which was two of the nine; of the
  rest, five ran on seats with full tool grants where the test is not
  possible, and two ran on the read-only seat and were simply not
  asked. Every one of those capability tests ran on 2.1.237. Below the
  2.1.216 floor containment is precisely what failed silently; above it
  no measurement covers every version, so the floor names the release
  that fixed the silent revert rather than a proven range. Conversation
  state usually persists and is NOT guaranteed to - `No transcript found`
  was measured three times on 2.1.233, above the 2.1.216 floor. Full
  records with literal payloads at
  docs/superpowers/plans/rounds/2026-07-26-seat-reshuffle/subagent-resume-probe.md
  and
  docs/superpowers/plans/rounds/2026-08-19-item50-resume-probe/probe-record.md;
  the dead-agent case is narrowed to the 0.14.0 smoke's observation
  scope. Round continuity is CHECKED per round, never assumed - see
  references/panels.md.
```

Note the deliberate repetition in the second bullet: the pinned phrase
"the seats declare the unversioned alias `model: fable`, so which model they
run is UNVERIFIED" must appear intact. If the surrounding sentence reads
awkwardly, restructure the sentence around the pinned phrase rather than
editing the pin.

- [ ] **Step 4: Run the new pins and the existing heading pin**

```bash
python -m pytest evals/multi-model-verify/test_multi_model_verify.py evals/multi-model-verify/test_seat_reshuffle.py -q
```

Expected: PASS, including `test_notes_driver_seat_sections`, whose
`"### Fable 5"` assertion is satisfied by `### Fable 5.1`.

- [ ] **Step 5: Run the whole gate**

```bash
python evals/tools/skill_lint.py skills/multi-model-verify --strict && python evals/tools/skill_scanner.py skills && python evals/tools/check_exact_line_oracles.py && python evals/tools/run_trigger_evals.py && python -m pytest evals -q
```

Expected: all five PASS. `model-prompting-notes.md` is a reference rather
than the skill body, so the token budget is not at issue here, but the lint
still runs.

- [ ] **Step 6: Commit**

```bash
git add skills/multi-model-verify/references/model-prompting-notes.md evals/multi-model-verify/test_multi_model_verify.py
git commit -m "update the fable seat notes for fable 5.1"
```

---

## After the tasks

1. Run the behavioural evals, which are local-only and opt-in and are
   required because this branch changes skill and prompt text:
   `python evals/tools/run_behavioral_evals.py --changed`. Record every
   skip it prints by name.
2. Whole-branch review via `agents/fable-reviewer.md` over the exact
   `base..head` range, retained as a range-bound artifact.
3. Mode-diff debate on the same range, citing that artifact.
4. **Then** bump `.claude-plugin/plugin.json`, because the debate is what
   moves the tree after the last build task.
5. Dev loop: marketplace update, then `plugin update parallax@parallax`,
   then verify the install BY CONTENT rather than by the cache directory
   name.
