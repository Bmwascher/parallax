# Item 32 Detached Dispatch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the four dispatch commands the skill documents incapable of blocking the caller past the 600-second tool ceiling, so a review round can no longer be killed with its quota spent and no reply written.

**Architecture:** Each documented dispatch keeps its existing pipeline verbatim, but that pipeline moves into a wrapper script which is launched with `Start-Process` and left running. The launching call returns at once, writing the child's process id to a file. Later calls poll that id and a sidecar exit-code file the wrapper writes as its own last act. Nothing about the brief, the flags, the route check or the round-evidence binding changes.

**Tech Stack:** Markdown skill contracts under `skills/multi-model-verify/`, pytest pins under `evals/multi-model-verify/`, PowerShell 5.1 and PowerShell 7.

**Spec:** `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`

## Global Constraints

- **Change the tests FIRST, then the skill.** The transport commands are live-verified contracts locked by `evals/multi-model-verify/test_multi_model_verify.py`; the backup lane's by `test_backup_lane.py`.
- **Both PowerShell hosts.** A green suite on one host proves one interpreter. Set `$env:PARALLAX_PS_HOST` to reach the other.
- **A killed, hung, or unfinished round must never be readable as a completed one.** Four states must stay distinguishable: still running; exited non-zero; exited zero WITH a freshly written reply file; exited zero with NO reply file. Only the third is a review result.
- **Item 51 is NOT fixed here.** The kimi-code command string stays byte-identical, inline `-p "<the whole brief>"` included. `test_backup_lane.py:137-148` pins those two strings and must stay green WITHOUT amendment. A red there means the argument path moved, which is out of scope.
- **Item 31 is NOT fixed here.** `tools/check-drift.ps1:1060` and `commands/doctor.md:70` are not touched.
- **The resume-after-a-kill recovery is NOT blessed.** Its soundness is unmeasured. This work stops the kill; it says nothing about recovering from one.
- **These pins must stay green** (`evals/multi-model-verify/test_multi_model_verify.py`): `test_the_brief_is_read_and_piped_as_utf8` counts five exact strings at `>= 2` across `SKILL.md`; `test_resume_pipes_the_brief_on_stdin` matches `$brief | codex exec ... resume <SESSION_ID> -` with `[^\n]*`, so that span stays on ONE physical line; the raw pin `("   & {" + chr(10)) not in text` forbids a three-space-indented `& {`.
- **A pin that matches raw file text needs its phrase unbroken on one physical line.** Check which read a pin uses before editing near it, and prefer restructuring prose to keep an existing pin green over editing the pin to fit new prose.
- **Dispatch every debate round and every full gate DETACHED, from the first attempt.**

---

### Task 1: Raise the SKILL.md token ceiling deliberately, with the measurement recorded

`SKILL.md` has **20 characters** of headroom before the soft warning and **1020** before the hard error. Measured 2026-08-30 at `fb3e2bb`: body 20983 chars, 5245 estimated tokens, budget 5250, ceiling 5500. Tasks 4 and 5 add roughly 1400 characters, which is over the ceiling. `skill_lint.py` names exactly two legitimate remedies and this plan uses both: explanation relocates to `model-prompting-notes.md` (Task 3), and the ceiling rises here with the measurement written down.

**Files:**
- Modify: `evals/tools/skill_lint.py:78-102`

**Interfaces:**
- Consumes: nothing.
- Produces: `BODY_TOKEN_CEILING = 5900`. Tasks 4 and 5 depend on this landing first, or their own verification fails on a budget error unrelated to their change.

- [ ] **Step 1: Measure the current body and record the number**

Run:

```bash
python -c "import io;t=io.open('skills/multi-model-verify/SKILL.md',encoding='utf-8').read();b=t.split('---',2)[2];print(len(b), len(b)//4, len(b.splitlines()))"
```

Expected: three numbers. Record them verbatim in the comment written in Step 2. Do not copy the numbers above if they disagree with what you measure; measure and use yours.

- [ ] **Step 2: Raise the ceiling and write the reason beside it**

In `evals/tools/skill_lint.py`, change `BODY_TOKEN_CEILING = 5500` to `BODY_TOKEN_CEILING = 5900` and add above it a comment in the file's existing style stating: the date, the measured body size, that backlog item 32 moved the two dispatch steps to a detached form that must be read at the point of use, that the explanation was relocated to `references/model-prompting-notes.md` first, and that this is the remedy `skill_lint.py`'s own error message names.

Leave `BODY_TOKEN_BUDGET` at `5250`. The soft warning is the signal that the file is growing and this change should not silence it.

- [ ] **Step 3: Verify the budget suite still passes**

Run: `python -m pytest evals/multi-model-verify/test_skill_lint_budget.py -q`
Expected: PASS. The band tests read `mod.BODY_TOKEN_CEILING` dynamically, so they follow the new value. The frozen pre-change fixture asserts `"BODY_TOKEN_CEILING" not in parts[2]` and `"5000" in parts[2]` about a HISTORICAL copy; it must not be edited.

- [ ] **Step 4: Verify strict lint still exits 0**

Run: `python evals/tools/skill_lint.py skills/multi-model-verify --strict; echo "exit=$?"`
Expected: `exit=0`. If the soft warning turns out to FAIL under `--strict`, raise `BODY_TOKEN_BUDGET` to `5650` as well and record in the same comment that strict escalates warnings, which is why the soft band had to move too. Do not discover this in Task 4.

- [ ] **Step 5: Commit**

```bash
git add evals/tools/skill_lint.py
git commit -m "raise the skill body ceiling for item 32's detached dispatch"
```

---

### Task 2: Pin the detached shape before it exists

**Files:**
- Modify: `evals/multi-model-verify/test_multi_model_verify.py`

**Interfaces:**
- Consumes: nothing.
- Produces: three failing tests named `test_both_dispatches_write_an_exit_code_file`, `test_both_dispatches_are_launched_detached`, and `test_the_dispatch_is_not_carried_by_a_here_string`. Task 4 makes them pass.

- [ ] **Step 1: Write the failing tests**

Add these to the class that already holds `test_the_brief_is_read_and_piped_as_utf8` in `evals/multi-model-verify/test_multi_model_verify.py`:

```python
    def test_both_dispatches_write_an_exit_code_file(self):
        """A detached round is read from files, so the exit code must be
        one of them.

        $proc.ExitCode is not usable: on Windows PowerShell 5.1 the
        file-redirect form of Start-Process never retains a native
        process handle, and ExitCode silently reads null when the child
        exits before the next statement touches .Handle. A review round
        always wins that race. The wrapper writes the code itself, as
        its own last act, so there is no race to lose.
        """
        text = read(SKILL_MD)
        assert text.count(
            '[System.IO.File]::WriteAllText("<exit-file>",'
            ' "$LASTEXITCODE")') >= 2, (
            "both dispatches must record the client's exit code to a file;"
            " a detached round has no live handle to read it from"
        )

    def test_both_dispatches_are_launched_detached(self):
        """The command a session copies must not be able to block it.

        Filed as backlog item 32 on 2026-08-11 and fired again on
        2026-08-30, on a session whose route was verified correct before
        it dispatched. The rule already existed in
        model-prompting-notes.md and the round was still lost, so the
        instruction now lives in the command rather than beside it.

        -Wait is forbidden rather than merely absent: it is the one flag
        that turns this back into the blocking form while still looking
        like the detached one.
        """
        text = read(SKILL_MD)
        assert text.count(
            "$proc = Start-Process -FilePath (Get-Process -Id $PID).Path"
            ' -ArgumentList @("-NoProfile", "-NonInteractive", "-File",'
            ' "`\"<wrapper-file>`\"") -NoNewWindow -PassThru') >= 2, (
            "both dispatches must launch the wrapper detached, on the"
            " session's own host, with the wrapper path individually"
            " quoted: Start-Process -ArgumentList joins its array with a"
            " plain space and does not quote an element containing one"
        )
        assert text.count(
            '[System.IO.File]::WriteAllText("<pid-file>",'
            ' "$($proc.Id)")') >= 2, (
            "the child's pid must reach a file: shell state does not"
            " survive to the next call, so $proc cannot be polled later"
        )
        assert "-Wait -PassThru" not in text, (
            "-Wait restores the blocking form this item exists to remove"
        )

    def test_the_dispatch_is_not_carried_by_a_here_string(self):
        """A here-string terminator must sit at column 0.

        Both dispatch blocks are indented three spaces inside a numbered
        list, so a copied here-string terminator carries that indent and
        the wrapper fails to parse before codex is ever called - a new
        way to spend a round on nothing, introduced by the fix for the
        old one.
        """
        text = read(SKILL_MD)
        assert "@'" not in text, (
            "the wrapper is written as a file, never built from a"
            " here-string inside an indented block"
        )
        assert '@"' not in text, (
            "the wrapper is written as a file, never built from a"
            " here-string inside an indented block"
        )
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k "exit_code_file or launched_detached or here_string"`
Expected: **2 FAILED, 1 PASSED.** The two that fail name the missing strings; read each message and confirm it names the string rather than a typo in the test.

`test_the_dispatch_is_not_carried_by_a_here_string` passes from the start, and that is correct. `SKILL.md` contains no here-string marker today (verified 2026-08-30 at `fb3e2bb`: `grep "@'\|@\"" skills/multi-model-verify/SKILL.md` matched nothing). It is a guard against a shape THIS fix could introduce, not a test of the fix. Do not "make it fail first" by planting a here-string.

- [ ] **Step 3: Commit the failing tests**

```bash
git add evals/multi-model-verify/test_multi_model_verify.py
git commit -m "pin the detached dispatch shape before building it"
```

---

### Task 3: State the detached-dispatch contract in the notes, declare it, pin it

The explanation lives here rather than in `SKILL.md` because `SKILL.md` is budgeted and this text is read once, when a session learns the flow.

**Files:**
- Modify: `skills/multi-model-verify/references/model-prompting-notes.md:297-314`
- Modify: `evals/multi-model-verify/test_contract_coverage.py:624-728`
- Modify: `evals/multi-model-verify/test_multi_model_verify.py`

**Interfaces:**
- Consumes: nothing.
- Produces: two marked regions, `detached-dispatch-mechanism` and `detached-dispatch-states`, each locked by exactly one pin. Task 4 cites them from `SKILL.md`.

- [ ] **Step 1: Replace the lead of the existing DETACHED bullet**

In `skills/multi-model-verify/references/model-prompting-notes.md`, the bullet currently opens:

```
- **Dispatch the round DETACHED, and do not let the shell kill it.** A
  round that crosses the caller's foreground timeout is killed by the
  CALLER, not by the client: no `--output-last-message` file is written,
  so it is a transport failure rather than a review result and the quota
  is spent for nothing. Measured repeatedly through 0.21.x. Two traps
```

Insert the two regions immediately AFTER the sentence ending `is spent for nothing.` and BEFORE `Measured repeatedly through 0.21.x.`, so the sentence pinned by `test_dispatch_traps_are_documented_in_the_notes` is not touched. That pin reads the whitespace-normalized file and asserts that exact sentence; breaking it is the failure mode this step exists to avoid.

Region one:

```
  <!-- contract:start id=detached-dispatch-mechanism -->
  The pipeline moves into a WRAPPER SCRIPT which is launched with
  `Start-Process` and left running; the launching call returns at once.
  Three parts are load-bearing. The encoding preamble goes INSIDE the
  wrapper, because a new process does not inherit the caller's
  `$OutputEncoding` and a wrapper without it silently reinstates the
  fault 0.23.0 fixed. The wrapper is a FILE rather than an argument
  list, because 5.1 native argument splatting strips embedded double
  quotes and `Start-Process -ArgumentList` joins its array with a plain
  space without quoting an element that contains one. The wrapper writes
  its own exit code to a file as its last act, because 5.1's
  file-redirect `Start-Process` never retains a native handle and
  `$proc.ExitCode` reads null whenever the child outlives the next
  statement, which a review round always does.
  <!-- contract:end -->
```

Region two:

```
  <!-- contract:start id=detached-dispatch-states -->
  A detached round is read from files, and FOUR states must stay apart:
  still running; exited non-zero; exited zero WITH a reply file this
  round's call freshly wrote; exited zero with NO reply file. Only the
  third is a review result. The other three are transport failures per
  fallbacks.md, and the absence of the exit file means the wrapper never
  finished, never that the round is clean. Poll with `Get-Process -Id`
  or `Wait-Process -Id` against the recorded pid, never with `ps -p`
  from Git Bash, which cannot see Windows pids and reports a live
  process as gone. To abandon a round, fell the whole tree with
  `taskkill /PID <id> /T /F`: killing the launcher alone leaves the
  client orphaned, which is what the 2026-08-11 report of this item
  observed at zero CPU growth.
  <!-- contract:end -->
```

- [ ] **Step 2: Declare both regions**

In `evals/multi-model-verify/test_contract_coverage.py`, add to `DECLARED_REGIONS`, immediately before the closing `}`, with a comment in the file's existing style explaining that these are backlog item 32, that two regions rather than one because a region must fit inside a single pin, and that they say different kinds of thing — one is the mechanism, one is how its result is read.

```python
    # 0.28.0, backlog item 32. The dispatch a session copies could block
    # the caller and be killed at 600 seconds with the quota spent. Two
    # regions rather than one because a region must fit inside a single
    # pin, and because they say different kinds of thing: the MECHANISM
    # region holds why the wrapper is a file and where the encoding
    # preamble lives, the STATES region holds how a detached round is
    # read - which is the half that decides whether an unfinished round
    # can be mistaken for a clean one.
    "detached-dispatch-mechanism",
    "detached-dispatch-states",
```

- [ ] **Step 3: Write one pin per region**

Add to `evals/multi-model-verify/test_multi_model_verify.py`, beside `test_dispatch_traps_are_documented_in_the_notes`:

```python
def test_the_detached_dispatch_mechanism_is_pinned():
    """Why the wrapper is a file and where the encoding preamble lives.

    Each of the three parts was a measured defect elsewhere in this
    repo before it was a rule here."""
    notes = " ".join(read(REFERENCES / "model-prompting-notes.md").split())
    assert (
        "The pipeline moves into a WRAPPER SCRIPT which is launched with "
        "`Start-Process` and left running; the launching call returns at "
        "once. Three parts are load-bearing. The encoding preamble goes "
        "INSIDE the wrapper, because a new process does not inherit the "
        "caller's `$OutputEncoding` and a wrapper without it silently "
        "reinstates the fault 0.23.0 fixed. The wrapper is a FILE rather "
        "than an argument list, because 5.1 native argument splatting "
        "strips embedded double quotes and `Start-Process -ArgumentList` "
        "joins its array with a plain space without quoting an element "
        "that contains one. The wrapper writes its own exit code to a "
        "file as its last act, because 5.1's file-redirect "
        "`Start-Process` never retains a native handle and "
        "`$proc.ExitCode` reads null whenever the child outlives the "
        "next statement, which a review round always does.") in notes


def test_the_detached_dispatch_states_are_pinned():
    """The half that decides whether an unfinished round reads as clean.

    A missing exit file means the wrapper never finished. Reading that
    as success is the one outcome this whole item may not produce."""
    notes = " ".join(read(REFERENCES / "model-prompting-notes.md").split())
    assert (
        "A detached round is read from files, and FOUR states must stay "
        "apart: still running; exited non-zero; exited zero WITH a reply "
        "file this round's call freshly wrote; exited zero with NO reply "
        "file. Only the third is a review result. The other three are "
        "transport failures per fallbacks.md, and the absence of the exit "
        "file means the wrapper never finished, never that the round is "
        "clean. Poll with `Get-Process -Id` or `Wait-Process -Id` against "
        "the recorded pid, never with `ps -p` from Git Bash, which cannot "
        "see Windows pids and reports a live process as gone. To abandon "
        "a round, fell the whole tree with `taskkill /PID <id> /T /F`: "
        "killing the launcher alone leaves the client orphaned, which is "
        "what the 2026-08-11 report of this item observed at zero CPU "
        "growth.") in notes
```

- [ ] **Step 4: Run the coverage and pin checks**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py evals/multi-model-verify/test_multi_model_verify.py -q`
Expected: PASS, except the three Task 2 tests which still fail. If `test_every_marked_region_is_locked_by_a_pin` reports either new region as unlocked, the pin's string does not match the normalized document text — fix the pin's spacing, never the region's words.

- [ ] **Step 5: Confirm the pre-existing trap pin is untouched**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k dispatch_traps`
Expected: PASS. A failure here means the insertion split the sentence that pin asserts.

- [ ] **Step 6: Commit**

```bash
git add skills/multi-model-verify/references/model-prompting-notes.md evals/multi-model-verify/test_contract_coverage.py evals/multi-model-verify/test_multi_model_verify.py
git commit -m "state and pin the detached dispatch contract"
```

---

### Task 4: Make SKILL.md's two dispatches detached

**Files:**
- Modify: `skills/multi-model-verify/SKILL.md:174-190` (round 1) and `skills/multi-model-verify/SKILL.md:236-251` (resume)

**Interfaces:**
- Consumes: `BODY_TOKEN_CEILING = 5900` from Task 1; the two contract regions from Task 3; the three failing tests from Task 2.
- Produces: the finished round-1 and resume steps. Task 6 measures them.

- [ ] **Step 1: Rewrite the round-1 step**

Replace step 2's prose and fenced block. The wrapper block is today's block with ONE line added before the closing `}`; every other character of it stays as it is, because five pins count exact strings in it.

Prose above the block:

```
2. Compose the reviewer's debate brief per references/model-prompting-notes.md, write
   it to a scratchpad file, then write this wrapper to `<wrapper-file>` — as a
   FILE, never from a here-string, whose terminator cannot survive this block's
   indentation — and launch it DETACHED. Never run it inline: the caller's
   600-second ceiling kills a crossing round with the quota spent and no reply
   written (references/model-prompting-notes.md).
```

The wrapper block, unchanged except for the `WriteAllText` line:

```powershell
$priorOutputEncoding = $OutputEncoding
try {
$OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$brief = [System.IO.File]::ReadAllText("<brief-file>", (New-Object System.Text.UTF8Encoding($false, $true)))
$bytes = [System.IO.File]::ReadAllBytes("<verified-override-file>")
$seen = ([System.BitConverter]::ToString(([System.Security.Cryptography.SHA256]::Create()).ComputeHash($bytes)) -replace '-', '').ToLower()
if ($seen -cne "<override-sha256>") { throw "the override file changed after the probe verified it" }
$override = (New-Object System.Text.UTF8Encoding($false, $true)).GetString($bytes)
$brief | codex exec --sandbox read-only --disable plugins --disable apps --disable memories -c mcp_servers.node_repl.enabled=false -c $override -m <canonical-model-id> -c model_reasoning_effort=<canonical-effort> --output-last-message <reply-file> - > <transcript-file> 2>&1
[System.IO.File]::WriteAllText("<exit-file>", "$LASTEXITCODE")
} finally { $OutputEncoding = $priorOutputEncoding }
```

Then the launch block and its one line of prose:

```
   Launch it and STOP. Read the round only after the poll says it finished,
   per references/model-prompting-notes.md's four states:
```

```powershell
$proc = Start-Process -FilePath (Get-Process -Id $PID).Path -ArgumentList @("-NoProfile", "-NonInteractive", "-File", "`"<wrapper-file>`"") -NoNewWindow -PassThru
[System.IO.File]::WriteAllText("<pid-file>", "$($proc.Id)")
```

Keep the existing sentence "Both encoding lines are load-bearing on Windows PowerShell 5.1 (references/model-prompting-notes.md)." and everything from the `verified-override-dispatch` contract marker onward exactly as it is.

- [ ] **Step 2: Rewrite the resume step the same way**

Apply the identical two changes to step 3's block: add the same `WriteAllText("<exit-file>", "$LASTEXITCODE")` line before the closing `}`, and add the identical launch block after it, with the same one-line lead. The `$brief | codex exec ... resume <SESSION_ID> -` line must stay on ONE physical line and must not otherwise change.

Keep the existing paragraph "The preamble repeats in full every round..." and everything after it.

- [ ] **Step 3: Run the three Task 2 tests**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k "exit_code_file or launched_detached or here_string"`
Expected: 3 PASSED.

- [ ] **Step 4: Run the pins that lock the old shape**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q`
Expected: PASS. `test_the_brief_is_read_and_piped_as_utf8` and `test_resume_pipes_the_brief_on_stdin` must pass WITHOUT being edited. If either fails, the wrapper body was altered beyond the one added line — restore it rather than amending the pin.

- [ ] **Step 5: Run the lint and the scanner**

Run: `python evals/tools/skill_lint.py skills/multi-model-verify --strict && python evals/tools/skill_scanner.py skills`
Expected: both PASS, exit 0. A body-token error here means Task 1's ceiling is too low for what was written; report the measured number rather than deleting text to fit.

- [ ] **Step 6: Commit**

```bash
git add skills/multi-model-verify/SKILL.md
git commit -m "dispatch both codex rounds detached"
```

---

### Task 5: Make the backup lane's two dispatches detached, without touching their command strings

**Files:**
- Modify: `skills/multi-model-verify/references/backup-lane.md:21-35`
- Modify: `evals/multi-model-verify/test_backup_lane.py`

**Interfaces:**
- Consumes: the two contract regions from Task 3.
- Produces: a `test_the_backup_dispatch_is_launched_detached` pin and the amended transport section.

- [ ] **Step 1: Write the failing test**

Add to `evals/multi-model-verify/test_backup_lane.py`, beside the test that pins the two command strings:

```python
def test_the_backup_dispatch_is_launched_detached():
    """The kimi lane crosses 600 seconds as readily as the codex lane.

    The command STRING is deliberately unchanged: its inline -p payload
    is backlog item 51's subject, and moving it here would silently
    widen this change into that one. Only the launch changes.
    """
    body = read(REFERENCES / "backup-lane.md")
    assert (
        "Both calls run inside a WRAPPER SCRIPT launched with "
        "`Start-Process` and left running, exactly as the codex lane "
        "does - see model-prompting-notes.md's detached-dispatch "
        "regions for the mechanism and for the four states a detached "
        "round is read through. The command line above is unchanged, "
        "including its inline `-p` payload.") in body
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py -q -k detached`
Expected: 1 FAILED, naming the missing string.

- [ ] **Step 3: Add the paragraph to backup-lane.md**

In `skills/multi-model-verify/references/backup-lane.md`, immediately after the Resume bullet (the one ending "with `KIMI_CODE_HOME` still set to the debate home.") and before the session-id bullet, add:

```
- Both calls run inside a WRAPPER SCRIPT launched with `Start-Process` and left running, exactly as the codex lane does - see model-prompting-notes.md's detached-dispatch regions for the mechanism and for the four states a detached round is read through. The command line above is unchanged, including its inline `-p` payload.
```

Write it as ONE physical line. The pin above reads the raw file.

- [ ] **Step 4: Verify the command-string pins are still green**

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py -q`
Expected: PASS, including the pins at `test_backup_lane.py:137-148`. Those two assertions passing unamended is the evidence that item 51's surface was not touched. If either goes red, the command string moved and the change is out of scope — revert it.

- [ ] **Step 5: Commit**

```bash
git add skills/multi-model-verify/references/backup-lane.md evals/multi-model-verify/test_backup_lane.py
git commit -m "dispatch both backup-lane rounds detached"
```

---

### Task 6: Measure a non-ASCII brief through the detached wrapper on both hosts

This is the measurement the spec says must not be assumed. This repo has paid for this class three times: 0.23.0 found it with the round-evidence binding, and the `& { }` variant was found only after being reasoned about and shipped.

**Files:**
- Create: `docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/wrapper-encoding-probe.md`

**Interfaces:**
- Consumes: the finished `SKILL.md` blocks from Task 4.
- Produces: a probe record with a verdict of REPRODUCED or NOT REPRODUCED per host.

- [ ] **Step 1: Build the fixture**

Write a brief file to the scratchpad containing at least one em dash and one non-Latin character, as no-BOM UTF-8. Record its SHA-256 and its exact byte length in the probe record before dispatching anything.

- [ ] **Step 2: Run the wrapper on Windows PowerShell 5.1**

Follow `SKILL.md`'s round-1 steps literally, substituting the fixture for `<brief-file>`, against a cheap real dispatch. Launch detached. Poll. Then bind the reply to the brief with `tools/read-codex-round-evidence.ps1 -Fresh` and record whether the binding ACCEPTS.

Expected: the binding accepts, and the prompt the client recorded is byte-identical to the fixture.

- [ ] **Step 3: Run the same fixture on PowerShell 7**

Set `$env:PARALLAX_PS_HOST` to the other host and repeat Step 2 unchanged.

Expected: the same result.

- [ ] **Step 4: Write the probe record**

Record, per host: the host version, the fixture hash and length, the wrapper path, the pid, the exit file's contents, whether the reply file was written, and the binding's verdict. State the limit explicitly: this measures the CODEX lane's wrapper. The kimi lane's inline payload was not measured here and item 51 remains open.

If either host FAILS, stop. Do not amend the pins to accept the failure. Report the measurement and the host it failed on; a wrapper that corrupts the brief is worse than the blocking form it replaced, because the round completes and reads clean.

- [ ] **Step 5: Commit**

```bash
git add docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/wrapper-encoding-probe.md
git commit -m "measure the detached wrapper's brief encoding on both hosts"
```

---

### Task 7: Close the item and run the full gates

**Files:**
- Modify: `docs/superpowers/plans/2026-07-27-0150-backlog.md` (item 32's heading and the ranking's first entry)
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: Tasks 1 to 6.
- Produces: a green gate set and a closed item.

- [ ] **Step 1: Run the five local gates, detached**

Run, in the background, not the foreground:

```bash
python evals/tools/skill_lint.py skills/multi-model-verify --strict && python evals/tools/skill_scanner.py skills && python evals/tools/check_exact_line_oracles.py && python evals/tools/run_trigger_evals.py && python -m pytest evals -q
```

Expected: all five green, zero FAILED and zero ERROR. Do not pipe this through `tail` or `head`: the failure NAMES are what a second run needs.

- [ ] **Step 2: Run the suite on the other PowerShell host**

Set `$env:PARALLAX_PS_HOST` to whichever host Step 1 did not use and re-run `python -m pytest evals -q`, detached.
Expected: green. A green suite on one host proves one interpreter.

- [ ] **Step 3: Run the behavioural evals**

`skills/` changed, so run `python evals/tools/run_behavioral_evals.py`, detached.
Expected: no regression against main. Record any case that goes red by NAME.

- [ ] **Step 4: Update CLAUDE.md's "Long-running commands" section**

That section currently tells a session to dispatch detached and names two traps. Add one sentence pointing at the skill's detached-dispatch regions as the place the mechanism now lives, so the instruction and the command do not drift apart again.

- [ ] **Step 5: Close item 32 in the backlog**

Change item 32's heading status from `OPEN` to `DONE`, add the version, move it out of the ranking's first entry, and renumber the entries below it. Update the `**Open.**` and `**Done.**` lists in the status block at the top by reading the headings, not by editing the previous list. State in the item what was NOT done: items 51 and 31 are untouched, and the resume-after-a-kill recovery is still unmeasured.

- [ ] **Step 6: Commit**

```bash
git add CLAUDE.md docs/superpowers/plans/2026-07-27-0150-backlog.md
git commit -m "close item 32 and point CLAUDE.md at the detached dispatch contract"
```

---

## Left open for the plan debate

The spec raised three questions. Two are answered above and one is not.

- **Where the poll lives** — answered: `references/model-prompting-notes.md`, as the `detached-dispatch-states` region. `SKILL.md` has 20 characters of headroom before its soft warning, which settles it.
- **Wrapper shipped under `tools/` or written per round** — answered: written per round to the scratchpad as `<wrapper-file>`. Item 58 is the argument: the skill has already failed to find its own shipped tooling once and reported a false BLOCKED.
- **Whether a timeout is documented, and what happens at it** — NOT answered, deliberately. A documented "fell the tree at N minutes" reintroduces a caller kill, just a later and better-behaved one; leaving it out risks a session polling a hung process forever. `detached-dispatch-states` gives the session the means to decide (the pid, the four states, and `taskkill /PID <id> /T /F`) without setting a policy. Settle this in the debate before the plan is frozen.

## After the tasks

The version bump comes AFTER the diff debate, not here. `plugin update` keys only on the version string, and a number cached before the debate rewrites the tree installs nothing afterwards.
