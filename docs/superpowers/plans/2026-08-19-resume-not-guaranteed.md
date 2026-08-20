# Resume Is Not Guaranteed Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Retire the contract's claim that a Claude Code version floor makes subagent resume reliable, and replace it with a named failure class, a routing rule, and a per-round continuity check that can fail.

**Architecture:** Four contract documents change, in dependency order. `fallbacks.md` gains the Fable resume-failure class first, mirroring the shape the Kimi lane already has, because every other site routes to it. `panels.md` then names the failure modes and adds the continuity check. The panel seat's own agent file and the shared prompting notes follow. Six new locked contract regions are added; every one is pinned and declared in the same task that creates it.

**Tech Stack:** Markdown contract documents under `skills/multi-model-verify/` and `agents/`; pytest pins under `evals/multi-model-verify/`; PowerShell 5.1 and 7 for the gate.

**Spec:** `docs/superpowers/specs/2026-08-19-resume-not-guaranteed-design.md`

## Global Constraints

- **The floor stays at Claude Code 2.1.216 and is NEVER raised.** Raising it is refuted by measurement: the failures happened above it.
- **The phrase `Harness floor: Claude Code 2.1.216` must occur exactly once in `panels.md`.** An existing pin asserts `== 1` and deleting the floor must turn it red.
- **Tests change BEFORE the text they lock**, every task, no exceptions.
- **Every new locked region must sit WHOLE inside a single pin**, in one of the three assertion clause forms `CLAUDE.md` permits: `"literal" in body`, `body.count("literal")` compared in the positive bounds, or an `and` of those.
- **Every region added is also added to `DECLARED_REGIONS`** in `evals/multi-model-verify/test_contract_coverage.py`, in the same task. The set is compared both ways: a missing region and an undeclared region both fail.
- **Use plain hyphens, not em dashes, in all new contract text.** Matches the existing locked regions.
- **Both PowerShell hosts count.** A green suite on one proves one interpreter.

---

### Task 1: The Fable resume-failure class in fallbacks.md

Foundation task. Every other site routes to the class this creates.

**Files:**
- Modify: `skills/multi-model-verify/references/fallbacks.md:210-216`
- Modify: `evals/multi-model-verify/test_contract_coverage.py` (DECLARED_REGIONS)
- Test: `evals/multi-model-verify/test_seat_reshuffle.py:166-197` (`test_fallbacks_panel_lane_loss`)

**Interfaces:**
- Produces: two locked region ids later tasks cite by name, `fable-resume-failure` and `fable-resume-redispatch-record`; and the phrase `lost round continuity`, which Tasks 2 and 3 reuse verbatim.

- [ ] **Step 1: Write the failing pins**

Append inside `test_fallbacks_panel_lane_loss` in `evals/multi-model-verify/test_seat_reshuffle.py`, after the existing final assertion at line 197:

```python
    # 0.27.0 item 50: panel-lane-loss covered only "a dead Fable panel
    # subagent". A resume that cannot reach a transcript leaves the agent
    # NOT dead, so nothing routed it and the consent gate above was never
    # reached - the reported session re-dispatched fresh and the panel
    # still reported as a panel. The Kimi lane already carries this class
    # (fallbacks.md "resume failure: one same-parameters retry"), so this
    # mirrors a proven shape rather than inventing one.
    assert ("for the Fable panel seat, both a dead subagent and a resume "
            "that cannot reach its transcript are directly this "
            "class") in nfb
    assert ("Fable resume failure: a resume that returns no reachable "
            "transcript gets one same-parameters retry, then the consent "
            "gate. The agent is not dead, so this is not agent death; it "
            "is lost round continuity, and it is never resolved by a "
            "silent fresh dispatch.") in nfb
    assert ("A fresh dispatch the user consents to is RECORDED as a fresh "
            "dispatch, and the lane's round continuity is recorded as "
            "broken from that round on. A panel that lost continuity "
            "cannot report as an intact one.") in nfb
```

- [ ] **Step 2: Run the pins to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_seat_reshuffle.py::test_fallbacks_panel_lane_loss -v`
Expected: FAIL on the first new assertion.

- [ ] **Step 3: Widen the class parenthetical**

In `skills/multi-model-verify/references/fallbacks.md`, replace lines 210-213:

```markdown
A reviewer lane failing mid-panel (references/panels.md) first
resolves through its own transport classes above (codex classes for
Sol, the backup-lane classes for Kimi; for the Fable panel seat, both
a dead subagent and a resume that cannot reach its transcript are
directly this class). If the lane cannot continue:
```

- [ ] **Step 4: Add the two new regions**

In the same file, immediately AFTER the existing `contract:end` of `panel-lane-loss-disposition` (line 216) and BEFORE the line beginning `The gate offers:`, insert:

```markdown
<!-- contract:start id=fable-resume-failure -->
Fable resume failure: a resume that returns no reachable transcript gets one same-parameters retry, then the consent gate. The agent is not dead, so this is not agent death; it is lost round continuity, and it is never resolved by a silent fresh dispatch.
<!-- contract:end -->
<!-- contract:start id=fable-resume-redispatch-record -->
A fresh dispatch the user consents to is RECORDED as a fresh dispatch, and the lane's round continuity is recorded as broken from that round on. A panel that lost continuity cannot report as an intact one.
<!-- contract:end -->
```

Each region is one line so it survives any reflow, matching how `panel-lane-loss-disposition` above it is written.

- [ ] **Step 5: Declare both regions**

In `evals/multi-model-verify/test_contract_coverage.py`, add to `DECLARED_REGIONS` (the set beginning at line 624), keeping the file's existing ordering convention:

```python
    "fable-resume-failure",
    "fable-resume-redispatch-record",
```

- [ ] **Step 6: Run the pins and the coverage checker**

Run: `python -m pytest evals/multi-model-verify/test_seat_reshuffle.py::test_fallbacks_panel_lane_loss evals/multi-model-verify/test_contract_coverage.py -v`
Expected: PASS, both files.

- [ ] **Step 7: Commit**

```bash
git add skills/multi-model-verify/references/fallbacks.md evals/multi-model-verify/test_seat_reshuffle.py evals/multi-model-verify/test_contract_coverage.py
git commit -m "give the Fable panel seat a resume-failure class"
```

---

### Task 2: The failure modes and the continuity check in panels.md

**Files:**
- Modify: `skills/multi-model-verify/references/panels.md:62-73`
- Modify: `evals/multi-model-verify/test_contract_coverage.py` (DECLARED_REGIONS)
- Test: `evals/multi-model-verify/test_seat_reshuffle.py:113-152` (`test_panels_reference_pins`)

**Interfaces:**
- Consumes: the class name `panel-lane-loss` and the phrase `lost round continuity` from Task 1.
- Produces: three locked region ids, `panel-round-continuity-check`, `panel-resume-failure-mode` and `panel-floor-scope`.

- [ ] **Step 1: Write the failing pins**

Append inside `test_panels_reference_pins`, after the existing final assertion at line 152:

```python
    # 0.27.0 item 50: this file said round continuity "is evidenced by
    # transcript recall" and nothing made the driver CHECK it, so a resume
    # that succeeded while state was quietly lost passed unnoticed. The
    # recalled item must never ride the resume message or a re-primed
    # agent echoes it back and the check self-satisfies.
    assert ("Round continuity is not assumed, it is CHECKED. Each "
            "resumed round the driver asks the seat for something "
            "established in an EARLIER round that the current message "
            "does not contain, and records the answer. An item that "
            "rides the resume message proves nothing, because a freshly "
            "re-primed agent echoes it back.") in nbody
    # The old text named ONE failure mode, agent death. A failed resume
    # leaves the agent not dead, so a driver meeting `No transcript found`
    # did not recognize the panel-lane-loss case and re-dispatched fresh.
    assert ("This lane has more than one failure mode. The agent can "
            "die; a resume can fail to reach its transcript; and a "
            "resume can succeed with the conversation state gone. All "
            "three are lost round continuity and all three route to "
            "fallbacks.md's panel-lane-loss. Only the first is agent "
            "death.") in nbody
    # The floor bounds CONTAINMENT, never continuity. Three failures were
    # MEASURED on 2.1.233, above this floor.
    assert ("The floor does NOT make resume reliable. Resume is "
            "best-effort at every version above it. A version above the "
            "floor buys containment, never continuity.") in nbody
    # The retired overclaim must be gone, not merely qualified elsewhere.
    assert "Everything in the paragraph above holds only at or above it" not in nbody
```

- [ ] **Step 2: Run the pins to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_seat_reshuffle.py::test_panels_reference_pins -v`
Expected: FAIL on the first new assertion.

- [ ] **Step 3: Replace the evidence-class and floor paragraphs**

In `skills/multi-model-verify/references/panels.md`, replace lines 62-73 (from `so the pin cannot be silently swapped` through `original wording read as a platform guarantee.`) with:

```markdown
  so the pin cannot be silently swapped mid-debate. Self-reported
  identity is priming-class and never evidence.
  <!-- contract:start id=panel-round-continuity-check -->
  Round continuity is not assumed, it is CHECKED. Each resumed round
  the driver asks the seat for something established in an EARLIER
  round that the current message does not contain, and records the
  answer. An item that rides the resume message proves nothing,
  because a freshly re-primed agent echoes it back.
  <!-- contract:end -->
  <!-- contract:start id=panel-resume-failure-mode -->
  This lane has more than one failure mode. The agent can die; a
  resume can fail to reach its transcript; and a resume can succeed
  with the conversation state gone. All three are lost round
  continuity and all three route to fallbacks.md's panel-lane-loss.
  Only the first is agent death.
  <!-- contract:end -->
  **Harness floor: Claude Code 2.1.216.** It bounds ONE thing. Below
  it a resumed background agent silently reverted to the default
  agent, dropping the model pin, the seat's system prompt, and its
  read-only tool restriction in one step - the silent mode that
  defeats the pin and the allowlist together.
  <!-- contract:start id=panel-floor-scope -->
  The floor does NOT make resume reliable. Resume is best-effort at
  every version above it. A version above the floor buys containment,
  never continuity.
  <!-- contract:end -->
  Measured: `No transcript found` three times on 2.1.233, above this
  floor, and nine clean resumes across five conditions on 2.1.237,
  which is too few to bound an intermittent fault. Records:
  docs/superpowers/plans/rounds/2026-08-19-item50-resume-probe/probe-record.md.
```

The existing `panel-floor-reference` region and the changelog citation below it are UNCHANGED and must remain in place.

- [ ] **Step 4: Declare the three regions**

In `evals/multi-model-verify/test_contract_coverage.py`, add to `DECLARED_REGIONS`:

```python
    "panel-round-continuity-check",
    "panel-resume-failure-mode",
    "panel-floor-scope",
```

- [ ] **Step 5: Run the pins and the coverage checker**

Run: `python -m pytest evals/multi-model-verify/test_seat_reshuffle.py::test_panels_reference_pins evals/multi-model-verify/test_contract_coverage.py -v`
Expected: PASS. In particular `nbody.count("Harness floor: Claude Code 2.1.216") == 1` must still hold; the phrase appears exactly once in the replacement.

- [ ] **Step 6: Commit**

```bash
git add skills/multi-model-verify/references/panels.md evals/multi-model-verify/test_seat_reshuffle.py evals/multi-model-verify/test_contract_coverage.py
git commit -m "name the panel lane's real failure modes and check continuity"
```

---

### Task 3: The panel seat's own resume claim

**Files:**
- Modify: `agents/fable-panel-reviewer.md:18-29`
- Modify: `evals/multi-model-verify/test_contract_coverage.py` (DECLARED_REGIONS)
- Test: `evals/multi-model-verify/test_seat_reshuffle.py:50-86` (`test_fable_panel_reviewer_exists_and_pins`)

**Interfaces:**
- Consumes: the failure modes named in Task 2.
- Produces: locked region id `panel-seat-resume-best-effort`.

- [ ] **Step 1: Write the failing pins**

In `test_fable_panel_reviewer_exists_and_pins`, the existing assertions at lines 59-60 pin the sentence this task rewrites:

```python
    assert "the resume surface carries no model parameter" in body
    assert "probed 2026-07-26" in body
```

Both stay green: the rewrite keeps the no-model-parameter fact and keeps its 2026-07-26 citation attached to it.

`nbody` is ALREADY defined at line 77 of this function. Do NOT redefine it. Append the new assertions at the END of the function, after the existing final assertion at line 84, and reuse it:

```python
    # 0.27.0 item 50: this file stated flatly that "your conversation
    # state persists across the resume". Three `No transcript found`
    # failures were measured above the floor, so the seat must be told
    # the truth: usually, not always, and say so when it does not have it.
    assert ("Your conversation state USUALLY persists across a resume, "
            "and it is not guaranteed to. A resume can fail outright, or "
            "succeed with your earlier rounds gone. When the driver asks "
            "you to recall something from an earlier round, answer "
            "honestly - if you do not have it, say so plainly. A seat "
            "that guesses hides the lane's failure.") in nbody
    # The floor qualifies CONTAINMENT only; naming which half it bounds
    # is the whole point of the 0.27.0 change.
    assert "The CONTAINMENT half has a FLOOR" in nbody
    assert "your conversation state persists across the resume" not in nbody
```

- [ ] **Step 2: Run the pins to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_seat_reshuffle.py::test_fable_panel_reviewer_exists_and_pins -v`
Expected: FAIL on the first new assertion.

- [ ] **Step 3: Rewrite the resume bullet**

In `agents/fable-panel-reviewer.md`, replace lines 18-29 (from `- Later rounds arrive` through `together, which is every control the lane relies on at once.`) with:

```markdown
- Later rounds arrive as resumed messages to this same agent.
  <!-- contract:start id=panel-seat-resume-best-effort -->
  Your conversation state USUALLY persists across a resume, and it is
  not guaranteed to. A resume can fail outright, or succeed with your
  earlier rounds gone. When the driver asks you to recall something
  from an earlier round, answer honestly - if you do not have it, say
  so plainly. A seat that guesses hides the lane's failure.
  <!-- contract:end -->
  The resume surface carries no model parameter (probed 2026-07-26,
  re-confirmed 2026-08-19), so your model pin rides the agent
  identity; your identity evidence is dispatch metadata, recorded by
  the driver, never your own claim. The CONTAINMENT half has a FLOOR:
  **Claude Code 2.1.216**. Below it a resumed background agent
  silently reverted to the default agent, and the fix that restores
  "the agent's prompt and tool restrictions" landed in that release.
  So on an older harness this seat silently reverted to the default
  agent - losing the model pin, this system prompt, and the read-only
  tool restriction together, which is every control the lane relies on
  at once. Above the floor containment held on every resume measured
  on 2026-08-19; continuity is a separate question and is checked per
  round.
```

The existing `panel-floor-agent` region immediately below is UNCHANGED.

- [ ] **Step 4: Declare the region**

In `evals/multi-model-verify/test_contract_coverage.py`, add to `DECLARED_REGIONS`:

```python
    "panel-seat-resume-best-effort",
```

- [ ] **Step 5: Run the pins and the coverage checker**

Run: `python -m pytest evals/multi-model-verify/test_seat_reshuffle.py::test_fable_panel_reviewer_exists_and_pins evals/multi-model-verify/test_contract_coverage.py -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add agents/fable-panel-reviewer.md evals/multi-model-verify/test_seat_reshuffle.py evals/multi-model-verify/test_contract_coverage.py
git commit -m "tell the panel seat its resume is best-effort"
```

---

### Task 4: The widest instance, in the shared prompting notes

This site was missed by the design and found by the Fable pre-build review. It is the retired guarantee living in a file every dispatch consults, and it names a seat that never resumes.

**Files:**
- Modify: `skills/multi-model-verify/references/model-prompting-notes.md:46-52`
- Test: `evals/multi-model-verify/test_seat_reshuffle.py:211-225` (`test_notes_driver_seat_sections`)

**Interfaces:**
- Consumes: nothing. Produces: nothing later tasks depend on.

- [ ] **Step 1: Verify the seat really never resumes**

Run: `grep -n -i "resume" agents/fable-reviewer.md`
Expected: NO output. `agents/fable-reviewer.md` is single-dispatch, which is why guaranteeing its resume is wrong twice over. Record the empty result in the task report.

- [ ] **Step 2: Write the failing pins**

Append inside `test_notes_driver_seat_sections`:

```python
    # 0.27.0 item 50, found by the Fable pre-build sweep: this bullet
    # asserted "conversation state persists across resume" for THREE
    # named seats, one of which (the whole-branch reviewer) has no resume
    # in its contract at all - verified by grep, zero hits. It is the same
    # class the 0.27.0 cycle exists to close, in the file every dispatch
    # reads, so leaving it would let the retired guarantee survive the fix.
    nnotes = " ".join(notes.split())
    assert ("Same-harness Fable seats that RESUME (panel lane, "
            "escalation - the whole-branch reviewer is single-dispatch "
            "and never resumes)") in nnotes
    assert ("Conversation state usually persists and is NOT guaranteed "
            "to - `No transcript found` was measured three times on "
            "2.1.233, above the 2.1.216 floor.") in nnotes
    assert "conversation state persists across resume and" not in nnotes
```

- [ ] **Step 3: Run the pins to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_seat_reshuffle.py::test_notes_driver_seat_sections -v`
Expected: FAIL on the first new assertion.

- [ ] **Step 4: Rewrite the bullet**

In `skills/multi-model-verify/references/model-prompting-notes.md`, replace lines 46-52 with:

```markdown
- Same-harness Fable seats that RESUME (panel lane, escalation - the
  whole-branch reviewer is single-dispatch and never resumes) resume
  probe, 2026-07-26, Claude Code 2.1.220, re-run across five
  conditions 2026-08-19 on 2.1.237: the resume surface carries no
  model parameter, and containment - model pin, system prompt,
  read-only grant - survives a resume, verified by capability rather
  than self-report. Conversation state usually persists and is NOT
  guaranteed to - `No transcript found` was measured three times on
  2.1.233, above the 2.1.216 floor. Full records with literal payloads
  at
  docs/superpowers/plans/rounds/2026-07-26-seat-reshuffle/subagent-resume-probe.md
  and
  docs/superpowers/plans/rounds/2026-08-19-item50-resume-probe/probe-record.md;
  the dead-agent case is narrowed to the 0.14.0 smoke's observation
  scope. Round continuity is CHECKED per round, never assumed - see
  references/panels.md.
```

- [ ] **Step 5: Run the pins**

Run: `python -m pytest evals/multi-model-verify/test_seat_reshuffle.py::test_notes_driver_seat_sections -v`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add skills/multi-model-verify/references/model-prompting-notes.md evals/multi-model-verify/test_seat_reshuffle.py
git commit -m "scope the resume claim to the seats that actually resume"
```

---

### Task 5: Full verification on both hosts

No new behaviour. This task proves the four edits together did not break anything, on both interpreters.

**Files:**
- Modify: none expected. Any fix this task needs is committed here.

**Interfaces:**
- Consumes: Tasks 1 through 4, all committed.

- [ ] **Step 1: Run the five CI-tier gates**

Run each and record the literal output. Do NOT pipe through `tail`, `head` or `Select-Object -Last`; the failure names are what a second run needs.

```
python evals/tools/skill_lint.py skills/multi-model-verify --strict
python evals/tools/skill_scanner.py skills
python evals/tools/check_exact_line_oracles.py
python evals/tools/run_trigger_evals.py
python -m pytest evals -q
```

Expected: all five clean. The pytest baseline before this branch was 2558 passed, 14 skipped; this branch adds pins, so the passed count rises and the skipped count must not.

- [ ] **Step 2: Re-run the suite on the OTHER PowerShell host**

Host resolution is `os.environ.get("PARALLAX_PS_HOST") or shutil.which("powershell") or shutil.which("pwsh")`, so unset it resolves to Windows PowerShell 5.1 (`powershell.exe`) on this machine. The two values CI uses are `powershell.exe` and `pwsh.exe`.

First RECORD which host Step 1 actually used:

```
python -c "import os,shutil; print(os.environ.get('PARALLAX_PS_HOST') or shutil.which('powershell') or shutil.which('pwsh'))"
```

Then run the suite under the OTHER one. If Step 1 resolved to `powershell.exe`:

```
$env:PARALLAX_PS_HOST = "pwsh.exe"
python -m pytest evals -q
Remove-Item Env:PARALLAX_PS_HOST
```

If Step 1 resolved to `pwsh.exe` instead, use `powershell.exe` here.

Expected: same counts as Step 1. A green suite on one host proves one interpreter, and 0.16.0 shipped a lane lock that did not lock on PowerShell 7 at all.

- [ ] **Step 3: Run the changed-surface behavioural evals**

This cycle edits skill contract text, so the opt-in behavioural suite runs. Dispatch it DETACHED from the first attempt; the foreground ceiling is 600 seconds.

Run: `python evals/tools/run_behavioral_evals.py --changed`
Expected: every case whose declared surface intersects this diff passes, and every skip is printed by name. Record the skip names.

- [ ] **Step 4: Confirm every region is declared and locked**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -v`
Expected: PASS, with all six new regions present in `DECLARED_REGIONS` and each sitting whole inside one pin.

- [ ] **Step 5: Commit any fix this task required**

```bash
git add -A
git commit -m "close verification gaps found by the full gate"
```

If nothing needed fixing, skip the commit and say so in the task report.

---

## What happens after Task 5

Not tasks, and not to be done by a task implementer:

1. **The diff debate**, per the repo flow, before merge. Ask it to sweep the CLASS and name an instance or report none, which is what ended 0.26.0.
2. **The version bump to 0.27.0**, AFTER the debate, not before. `plugin update` keys only on the version string, and the debate is what moves the tree after the final build task. This has cost three cycles.
3. **Item 50 and item 66 statuses** updated at their own headings, with the status block rebuilt from the headings and diffed, not edited by hand.
