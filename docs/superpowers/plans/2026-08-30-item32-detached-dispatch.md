# Items 32 and 33 Implementation Plan: detached dispatch, and the mirror prompt that always had one answer

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every long client call the skill documents incapable of blocking the caller past the 600-second tool ceiling, so a review round can no longer be killed with its quota spent and no reply written; and stop the preflight asking a question whose answer has never once differed.

**Architecture:** Each documented call keeps its client invocation verbatim and moves into a wrapper script. Every dispatch first CREATES ITS OWN DIRECTORY, which fails if the directory exists; every control path lives inside it. One shared launch block starts the wrapper with `Start-Process` and returns at once. Later calls check liveness first, then read the exit file and the lane's reply artifact.

**Tech Stack:** Markdown skill contracts under `skills/multi-model-verify/`, pytest pins under `evals/multi-model-verify/`, PowerShell 5.1 and PowerShell 7.

**Spec:** `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`

**Revision 4, 2026-08-30**, after three Sol rounds on session `01a055c5-935e-76e3-ad1d-83721bc67d79`. Round 1 returned FIX on 8 of 12, round 2 closed 7 of 11, round 3 closed 4 of 8 and its sweeps found more. The change tables are at the end. Every finding was reproduced before acceptance and none was refuted.

**Round 3 named a recurring defect in THIS PLAN, not in the code:** three times running, a task described what should happen and pinned the description instead of the mechanism. Two structural changes answer it, and they are why this is a rewrite rather than a fourth patch. First, the launch block is defined ONCE, in `model-prompting-notes.md`, and both lanes cite it; there is no second place for a lane to be "detached" in prose only. Second, every task now carries a **task-local oracle** — a check that fails if that task's own change is missing — because round 3 found several tasks whose verification passed either way.

## Global Constraints

- **Change the tests FIRST, then the skill.** The transport commands are live-verified contracts locked by `evals/multi-model-verify/test_multi_model_verify.py`; the backup lane's by `test_backup_lane.py`.
- **Both PowerShell hosts.** A green suite on one host proves one interpreter. Set `$env:PARALLAX_PS_HOST` to reach the other.
- **A killed, hung, or unfinished round must never be readable as a completed one.** SEVEN states, liveness checked first; see `detached-dispatch-states` in Task 3. Rounds 1, 2 and 3 each found a hole in this, so treat the class as open rather than closed.
- **Every dispatch creates its own directory and everything lives inside it.** `New-Item -ItemType Directory` without `-Force` FAILS when the path exists, which makes creation the reservation. This replaces the round-numbered-path scheme: round 3 established that checking six paths and then launching is a check-then-use window, and that round numbers are already documented as not unique across concurrent debates (`model-prompting-notes.md:279-295`).
- **Item 51 is NOT fixed here, but the Kimi lane IS detached here.** Item 51's probe record states it measured "a brief file is read and passed inline as `-p <brief>`, exactly the shape `references/backup-lane.md` documents" (`probe-record.md:27-31`), so a wrapper does not change the argv path. Item 51 keeps the escaping repair (`probe-record.md:112-137`).
- **Item 31 is NOT fixed here.** `tools/check-drift.ps1:1060` and `commands/doctor.md:70` are not touched.
- **The resume-after-a-kill recovery is NOT blessed.** Its soundness is unmeasured.
- **These pins must stay green** (`evals/multi-model-verify/test_multi_model_verify.py:609-650`): five exact strings counted at `>= 2` across `SKILL.md`; `test_resume_pipes_the_brief_on_stdin` matching `$brief | codex exec ... resume <SESSION_ID> -` with `[^\n]*`; and the raw pin forbidding a three-space-indented `& {`.
- **`evals/multi-model-verify/test_backup_lane.py:47-50` defines a whitespace-NORMALIZED read.** Pins built on it constrain neither wrapping nor byte identity. Use the raw reader for anything that must be copied verbatim.
- **Two facts here are NOT repo-verifiable** and are cited as harness tool contract: that each tool call gets a fresh shell, and that the Agent tool runs subagents in the background.
- **Dispatch every round and every gate DETACHED**, named with its lane and round (`Sol R1 debate round`) or, where there is no lane, its kind (`Gate: pytest 5.1`).

---

### Task 1: Raise the SKILL.md token ceiling deliberately, with the measurement recorded

**Files:** Modify `evals/tools/skill_lint.py:78-102`

**Interfaces:** Consumes nothing. Produces `BODY_TOKEN_CEILING = 5900`, which Tasks 4, 5 and 7 need before their lint step can pass.

- [ ] **Step 1: Measure the current body**

```bash
python -c "import io;t=io.open('skills/multi-model-verify/SKILL.md',encoding='utf-8').read();b=t.split('---',2)[2];print(len(b), len(b)//4, len(b.splitlines()))"
```

Record the three numbers. Use yours, not the ones written here.

- [ ] **Step 2: Raise the ceiling and write the reason beside it**

Change `BODY_TOKEN_CEILING = 5500` to `BODY_TOKEN_CEILING = 5900`. Above it add a comment in the file's style giving: the date, the measured body size from Step 1, that backlog item 32 moved the dispatch steps to a detached form that must be read at the point of use, that explanation was relocated to `references/model-prompting-notes.md` first, and that this is the remedy `skill_lint.py:308-326` names.

Leave `BODY_TOKEN_BUDGET` at `5250`. The soft warning is the signal that the file is growing.

- [ ] **Step 3: TASK-LOCAL ORACLE — assert the constant actually moved**

Round 3's finding: `test_skill_lint_budget.py:68-96` reads `mod.BODY_TOKEN_CEILING` dynamically, so the whole budget suite passes whether or not this task ran. Add to that file:

```python
def test_the_ceiling_records_item_32s_measurement():
    """The band tests read the constant dynamically, so they pass at any
    value. This one fails if the raise did not happen."""
    src = (ROOT / "evals" / "tools" / "skill_lint.py").read_text(encoding="utf-8")
    assert "BODY_TOKEN_CEILING = 5900" in src
    assert "backlog item 32" in src, (
        "the raise must carry its reason beside it; skill_lint.py's own"
        " error text calls a deliberate documented raise one of the two"
        " legitimate remedies")
```

- [ ] **Step 4: Verify**

Run: `python -m pytest evals/multi-model-verify/test_skill_lint_budget.py -q && python evals/tools/skill_lint.py skills/multi-model-verify --strict; echo "exit=$?"`
Expected: PASS and `exit=0`. The frozen pre-change fixture asserting `"5000" in parts[2]` describes a HISTORICAL copy; do not edit it. If strict FAILS on the soft warning, raise `BODY_TOKEN_BUDGET` to `5650` too and record why in the same comment.

- [ ] **Step 5: Commit**

```bash
git add evals/tools/skill_lint.py evals/multi-model-verify/test_skill_lint_budget.py
git commit -m "raise the skill body ceiling for item 32's detached dispatch"
```

---

### Task 2: Pin the detached shape before it exists

**Files:** Modify `evals/multi-model-verify/test_multi_model_verify.py`

**Interfaces:** Consumes nothing. Produces five tests, listed in Step 2's `-k` expression. Task 4 makes the failing ones pass.

- [ ] **Step 1: Write the failing tests**

Add to the class holding `test_the_brief_is_read_and_piped_as_utf8`:

```python
    def test_both_dispatches_reserve_a_fresh_directory(self):
        """Creating the directory IS the reservation.

        Round 3's finding: checking six paths and then launching is a
        check-then-use window, and round numbers are already documented
        as not unique across concurrent debates
        (model-prompting-notes.md:279-295). New-Item without -Force
        fails when the path exists, so the create either wins the name
        or stops the dispatch.
        """
        text = read(SKILL_MD)
        assert text.count(
            "$d = (New-Item -ItemType Directory"
            ' -Path "<dispatch-dir>").FullName') >= 2, (
            "every dispatch must create its own directory, and must not"
            " pass -Force: the failure to create IS the refusal"
        )
        assert "-ItemType Directory -Force" not in text, (
            "-Force turns the reservation back into an overwrite"
        )

    def test_both_dispatches_write_an_exit_code_file(self):
        """The exit code must be a file, written after the finally.

        $proc.ExitCode is not usable: on Windows PowerShell 5.1 the
        file-redirect form of Start-Process never retains a native
        process handle, and ExitCode reads null when the child exits
        before the next statement touches .Handle. A review round always
        wins that race.

        Round 1 refuted the first draft, which wrote the sidecar inside
        the try, before the finally, so an early throw skipped it.
        """
        text = read(SKILL_MD)
        assert text.count(
            "} catch { $code = 1 } finally"
            " { $OutputEncoding = $priorOutputEncoding }\n"
            '[System.IO.File]::WriteAllText("$d\\exit", "$code")') >= 2, (
            "the exit code is written after the finally, as the wrapper's"
            " last act, and every failure path reaches that write"
        )
        assert text.count(
            "$code = 1\n"
            "$priorOutputEncoding = $OutputEncoding\n"
            "try {") >= 2, (
            "the code defaults to failure and the prior encoding is"
            " captured OUTSIDE the try, or the finally restores a value"
            " that was never set"
        )

    def test_both_dispatches_use_the_shared_launch_block(self):
        """One launch block, cited by every lane.

        Round 3's finding, three rounds running: a lane described as
        detached in prose, with no launch command, passes a prose pin.
        There is now one block and no second place to be detached in.
        """
        text = read(SKILL_MD)
        assert text.count(
            "$proc = Start-Process -FilePath (Get-Process -Id $PID).Path"
            ' -ArgumentList @("-NoProfile", "-NonInteractive", "-File",'
            ' "`\"$d\\wrapper.ps1`\"") -NoNewWindow -PassThru'
            ' -RedirectStandardInput "$d\\stdin.empty"'
            ' -RedirectStandardOutput "$d\\launch.out"'
            ' -RedirectStandardError "$d\\launch.err"') >= 2, (
            "both dispatches launch through the shared block, on the"
            " session's own host, with all three streams redirected"
        )
        assert text.count(
            '[System.IO.File]::WriteAllText("$d\\pid", "$($proc.Id)")') >= 2
        assert "-Wait -PassThru" not in text, (
            "-Wait restores the blocking form this item exists to remove"
        )

    def test_the_point_of_use_names_seven_states(self):
        """Round 3's finding: the region said six while SKILL.md said
        five and the spec said four. A pin on the region alone lets the
        instruction a session actually reads stay wrong."""
        text = read(SKILL_MD)
        assert text.count("seven states in references/"
                          "model-prompting-notes.md") >= 2

    def test_the_dispatch_is_not_carried_by_a_here_string(self):
        """A here-string terminator must sit at column 0, and both
        blocks are indented three spaces inside a numbered list, so a
        copied terminator carries the indent and the wrapper dies before
        codex runs."""
        text = read(SKILL_MD)
        assert "@'" not in text
        assert '@"' not in text
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k "reserve_a_fresh_directory or exit_code_file or shared_launch_block or seven_states or here_string"`
Expected: **4 FAILED, 1 PASSED.** The `-k` expression names every test this task adds; round 3 found the previous one silently omitting its own new test.

`test_the_dispatch_is_not_carried_by_a_here_string` passes from the start and that is correct — `SKILL.md` has no here-string marker today. It guards a shape THIS fix could introduce. Do not plant one to make it fail.

- [ ] **Step 3: Commit**

```bash
git add evals/multi-model-verify/test_multi_model_verify.py
git commit -m "pin the detached dispatch shape before building it"
```

---

### Task 3: State the contract in the notes, declare it, pin it

Five regions. The explanation lives here because `SKILL.md` is budgeted and this is read once, when a session learns the flow.

**Files:**
- Modify: `skills/multi-model-verify/references/model-prompting-notes.md:297-314`
- Modify: `evals/multi-model-verify/test_contract_coverage.py:624-728`
- Modify: `evals/multi-model-verify/test_multi_model_verify.py`

**Interfaces:** Consumes nothing. Produces `detached-dispatch-mechanism`, `detached-dispatch-launch`, `detached-dispatch-states`, `detached-dispatch-operation`, `background-task-naming`, each locked by exactly one pin.

- [ ] **Step 1: Insert the five regions**

Insert AFTER the sentence ending `is spent for nothing.` and BEFORE `Measured repeatedly through 0.21.x.`, so the sentence pinned by `test_dispatch_traps_are_documented_in_the_notes` is untouched.

**Region one — mechanism:**

```
  <!-- contract:start id=detached-dispatch-mechanism -->
  The client invocation moves into a WRAPPER SCRIPT which is launched
  with `Start-Process` and left running; the launching call returns at
  once. `Start-Process` is the mechanism this repo selected, not the
  only one that could work: `Start-Job` was rejected because each tool
  call gets a fresh shell, so a job handle does not survive to the call
  that would wait on it. Three parts are load-bearing. For a lane that
  PIPES its brief the encoding preamble goes INSIDE the wrapper, because
  a new process does not inherit the caller's `$OutputEncoding`; a lane
  that passes the brief as an ARGUMENT carries no such preamble and
  adding one would imply a mechanism that does not apply to it. The
  wrapper is a FILE rather than an argument list, which removes the
  `Start-Process -ArgumentList` serialization boundary - that cmdlet
  joins its array with a plain space and does not quote an element
  containing one - but does NOT remove every quoting layer: the wrapper
  is still parsed by PowerShell and still builds a native argv. The
  wrapper writes its own exit code to a file as its last act, after its
  `finally`, because 5.1's file-redirect `Start-Process` never retains a
  native handle and `$proc.ExitCode` reads null whenever the child
  outlives the next statement, which a review round always does.
  <!-- contract:end -->
```

**Region two — launch. This is the ONE launch block. Every lane cites it:**

```
  <!-- contract:start id=detached-dispatch-launch -->
  EVERY dispatch begins by creating its OWN DIRECTORY, and every control
  path lives inside it: `wrapper.ps1`, `stdin.empty`, `reply`,
  `transcript`, `exit`, `pid`, `launch.out`, `launch.err`. Creation uses
  `New-Item -ItemType Directory` WITHOUT `-Force`, which fails when the
  path exists, so winning the name and reserving it are the same act;
  checking a list of paths and then launching leaves a window between
  the two, and round numbering alone is not unique across concurrent
  debates. A lane adds parameters to the launch - the backup lane adds
  `-WorkingDirectory`, because that client binds a session to the
  directory it was created in - and changes nothing else about it. There
  is exactly one launch block, and a lane that does not cite it is not
  detached, however its prose reads.
  <!-- contract:end -->
```

**Region three — states:**

```
  <!-- contract:start id=detached-dispatch-states -->
  LIVENESS IS CHECKED FIRST and dominates everything: while the recorded
  pid is alive the round is RUNNING and no file is interpreted, because
  a reply or an exit file being written is not a reply or an exit file.
  After the process is confirmed gone, SEVEN states. One, running. Two,
  no exit file - the wrapper died before it could report, which is never
  the same as running. Three, an exit file that cannot be read or is not
  a plain integer, which includes a failed read and a partial write.
  Four, a non-zero code. Five, zero with no reply artifact. Six, zero
  with a reply artifact that is empty, unreadable, or refused by the
  lane's own round-evidence binding. Seven, zero with a reply artifact
  the binding ACCEPTS. ONLY THE SEVENTH is a review result; the other
  six are transport failures per fallbacks.md. Five and six are the ones
  an operator waves through, so they are named rather than left implied.
  The REPLY ARTIFACT is lane-defined - the codex lane's
  `--output-last-message` file, the backup lane's captured stdout - and
  each lane names its own.
  <!-- contract:end -->
```

**Region four — operation:**

```
  <!-- contract:start id=detached-dispatch-operation -->
  Poll with `Get-Process -Id` or `Wait-Process -Id` against the recorded
  pid, never with `ps -p` from Git Bash, which cannot see Windows pids
  and reports a live process as gone. Each poll is BOUNDED and returns;
  a poll that waits indefinitely is the blocking form again. At THIRTY
  MINUTES without a terminal state, stop polling, report the round
  UNFINISHED, and ask the user whether to keep waiting or abandon it.
  Neither answer is a review result. To abandon, fell the whole tree
  with `taskkill /PID <id> /T /F`: killing the launcher alone leaves the
  client orphaned, which is what the 2026-08-11 report of this item
  observed at zero CPU growth.
  <!-- contract:end -->
```

**Region five — naming. Separate from region four deliberately: round 2 refused to let an unenforced convention share a pin with completion safety, since a naming edit would then reopen a safety pin.**

```
  <!-- contract:start id=background-task-naming -->
  Name the backgrounded call for the person watching it. The reviewer
  LANE and the ROUND lead the description, as in `Sol R1 debate round`
  or `Kimi R2 debate round`; work with no lane leads with its kind, as
  in `Gate: pytest 5.1` or `Mirror build`. A cycle runs several lanes
  across several rounds at once and a name omitting either cannot be
  read at a glance. NOTHING ENFORCES THIS. It is a convention about what
  a human sees, its pin proves only that the rule is written down, and
  it is stated apart from the completion states because it carries none
  of their weight.
  <!-- contract:end -->
```

- [ ] **Step 2: Declare the five regions**

Add to `DECLARED_REGIONS` in `evals/multi-model-verify/test_contract_coverage.py`:

```python
    # 0.28.0, backlog item 32. FIVE regions because a region must fit
    # inside one pin and these say different kinds of thing. MECHANISM
    # is why the wrapper is a file and where the encoding preamble
    # belongs. LAUNCH is the single shared block plus the directory
    # reservation - Sol found a lane "detached" in prose with no launch
    # command three rounds running, so there is now one block and no
    # second place to be detached in. STATES is how a detached round is
    # read; rounds 1, 2 and 3 each found a hole in it. OPERATION is what
    # the driver does. NAMING is separate from OPERATION because it is
    # the only one of the five that nothing enforces, and a naming edit
    # must not reopen a completion-safety pin.
    "detached-dispatch-mechanism",
    "detached-dispatch-launch",
    "detached-dispatch-states",
    "detached-dispatch-operation",
    "background-task-naming",
```

- [ ] **Step 3: Write one pin per region**

Five tests beside `test_dispatch_traps_are_documented_in_the_notes`:
`test_the_detached_dispatch_mechanism_is_pinned`,
`test_the_shared_launch_block_is_pinned`,
`test_the_detached_dispatch_states_are_pinned`,
`test_the_detached_dispatch_operation_is_pinned`,
`test_the_background_task_naming_rule_is_documented`.

Each reads `" ".join(read(REFERENCES / "model-prompting-notes.md").split())` and asserts its region's full text as one normalized literal, in the style of `test_multi_model_verify.py:970-997`. Build each literal by copying the region text and normalizing it, never by retyping.

The last one's docstring must say it is a documentation-presence pin and not behavioural enforcement, so nobody reads a green suite as evidence that a session named anything correctly.

- [ ] **Step 4: TASK-LOCAL ORACLE plus the coverage checks**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py evals/multi-model-verify/test_multi_model_verify.py -q -k "pinned or documented or declared or locked"`
Expected: the five new pins PASS and both coverage tests PASS. If `test_every_marked_region_is_locked_by_a_pin` calls a region unlocked, fix the pin's spacing, never the region's words.

- [ ] **Step 5: Confirm the pre-existing trap pin is untouched**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k dispatch_traps`
Expected: PASS. A failure means the insertion split the sentence that pin asserts.

- [ ] **Step 6: Commit**

```bash
git add skills/multi-model-verify/references/model-prompting-notes.md evals/multi-model-verify/test_contract_coverage.py evals/multi-model-verify/test_multi_model_verify.py
git commit -m "state and pin the detached dispatch contract"
```

---

### Task 4: Make SKILL.md's two codex dispatches detached

**Files:** Modify `skills/multi-model-verify/SKILL.md:174-190` and `:236-251`

**Interfaces:** Consumes Task 1's ceiling, Task 3's regions, Task 2's failing tests. Produces the finished round-1 and resume steps, and the shared launch block's only two copies. Task 8 parses them; Task 9 measures them.

- [ ] **Step 1: Rewrite the round-1 step**

Prose above the blocks:

```
2. Compose the reviewer's debate brief per references/model-prompting-notes.md, write
   it to a scratchpad file, then reserve this round's directory, write the
   wrapper into it — as a FILE, never from a here-string, whose terminator
   cannot survive this block's indentation — and launch it DETACHED. Never run
   it inline: the caller's 600-second ceiling kills a crossing round with the
   quota spent and no reply written.
```

Reservation and wrapper:

```powershell
$d = (New-Item -ItemType Directory -Path "<dispatch-dir>").FullName
```

```powershell
$code = 1
$priorOutputEncoding = $OutputEncoding
try {
$OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$brief = [System.IO.File]::ReadAllText("<brief-file>", (New-Object System.Text.UTF8Encoding($false, $true)))
$bytes = [System.IO.File]::ReadAllBytes("<verified-override-file>")
$seen = ([System.BitConverter]::ToString(([System.Security.Cryptography.SHA256]::Create()).ComputeHash($bytes)) -replace '-', '').ToLower()
if ($seen -cne "<override-sha256>") { throw "the override file changed after the probe verified it" }
$override = (New-Object System.Text.UTF8Encoding($false, $true)).GetString($bytes)
$brief | codex exec --sandbox read-only --disable plugins --disable apps --disable memories -c mcp_servers.node_repl.enabled=false -c $override -m <canonical-model-id> -c model_reasoning_effort=<canonical-effort> --output-last-message $d\reply - > $d\transcript 2>&1
$code = $LASTEXITCODE
} catch { $code = 1 } finally { $OutputEncoding = $priorOutputEncoding }
[System.IO.File]::WriteAllText("$d\exit", "$code")
```

Launch:

```
   Launch it and STOP. Read the round only after the poll reaches one of the
   seven states in references/model-prompting-notes.md:
```

```powershell
[System.IO.File]::WriteAllText("$d\stdin.empty", "")
$proc = Start-Process -FilePath (Get-Process -Id $PID).Path -ArgumentList @("-NoProfile", "-NonInteractive", "-File", "`"$d\wrapper.ps1`"") -NoNewWindow -PassThru -RedirectStandardInput "$d\stdin.empty" -RedirectStandardOutput "$d\launch.out" -RedirectStandardError "$d\launch.err"
[System.IO.File]::WriteAllText("$d\pid", "$($proc.Id)")
```

Keep "Both encoding lines are load-bearing on Windows PowerShell 5.1 (references/model-prompting-notes.md)." and everything from the `verified-override-dispatch` marker onward exactly as it is. The codex lane's REPLY ARTIFACT is `$d\reply`, which is what `--output-last-message` writes.

**Four details are load-bearing and a tidy breaks them.** `$priorOutputEncoding` is captured OUTSIDE the `try`, or the `finally` restores a variable never assigned on an early failure. `catch` and `finally` are ONE clause on ONE line: a `} finally {` after an already-closed `catch` is a parse error and the wrapper dies before codex runs. The exit write is the last line, outside every block. `New-Item` takes no `-Force`, because the failure to create IS the refusal. Transcribe exactly; Task 8 proves it parses before any quota is spent.

- [ ] **Step 2: Rewrite the resume step identically**

Same reservation, same launch, same scaffolding. The `$brief | codex exec ... resume <SESSION_ID> -` line stays on ONE physical line and does not otherwise change. Keep "The preamble repeats in full every round..." and everything after it.

- [ ] **Step 3: TASK-LOCAL ORACLE**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k "reserve_a_fresh_directory or exit_code_file or shared_launch_block or seven_states or here_string"`
Expected: 5 PASSED. These are exactly the tests Task 2 wrote; all five must now pass.

- [ ] **Step 4: Verify the old pins survive untouched**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q && python evals/tools/skill_lint.py skills/multi-model-verify --strict && python evals/tools/skill_scanner.py skills`
Expected: PASS, exit 0. `test_the_brief_is_read_and_piped_as_utf8` and `test_resume_pipes_the_brief_on_stdin` must pass WITHOUT being edited; if either fails, restore the body rather than amending the pin.

- [ ] **Step 5: Commit**

```bash
git add skills/multi-model-verify/SKILL.md
git commit -m "dispatch both codex rounds detached"
```

---

### Task 5: Detach the Kimi lane's three client calls

Round 3's finding, and the third recurrence of this plan's own defect class: the previous revision gave this lane two wrapper bodies and no launch, so a "detached" lane had nothing that detaches. It also gave it no reply artifact, which would have put every successful Kimi round in state five and discarded it.

The three calls are the dispatch (`backup-lane.md:25`), the resume (`:30`), and the write-probe (`:353-359`), which runs before round 1 of every backup-lane debate and which `panels.md:51-53` makes panels inherit.

**Files:**
- Modify: `skills/multi-model-verify/references/backup-lane.md:21-35` and `:353-359`
- Modify: `evals/multi-model-verify/test_backup_lane.py`

**Interfaces:** Consumes Task 3's five regions, and cites the launch region rather than restating it. Produces `test_the_backup_lane_is_detached`.

- [ ] **Step 1: Write the failing test**

Uses the RAW reader, not `_norm`: these lines must be copyable verbatim.

```python
def test_the_backup_lane_is_detached():
    """All three client calls reserve, wrap, launch, and leave.

    Round 3 found the previous revision claiming detachment with no
    launch command at all - the third time this plan let prose stand in
    for a mechanism. So this pin asserts the LAUNCH, not the intent.

    The client command's flags and their order are unchanged and the
    brief is still inline in -p. Item 51's probe measured exactly this
    shape, a brief read from a file and passed inline, so the wrapper
    changes how the call is started and not how the brief reaches the
    client. Item 51 keeps the argv escaping repair.
    """
    body = _read(REFERENCES / "backup-lane.md")
    assert (
        '& "<kimi-code-binary>" -m <canonical-backup-model-id>'
        " --agent-file <plugin-checkout>/skills/multi-model-verify/"
        "references/kimi-reviewer-agent.md --skills-dir"
        " <debate-home>/skills -p $b > $d\\reply 2> $d\\transcript") in body
    assert (
        '& "<kimi-code-binary>" --session <session-id>'
        " -m <canonical-backup-model-id> --skills-dir"
        " <debate-home>/skills -p $b > $d\\reply 2> $d\\transcript") in body
    assert body.count(
        "$d = (New-Item -ItemType Directory"
        ' -Path "<dispatch-dir>").FullName') >= 3, (
        "all THREE calls reserve their own directory: dispatch, resume,"
        " and the write-probe")
    assert body.count(
        "$proc = Start-Process -FilePath (Get-Process -Id $PID).Path"
        ' -ArgumentList @("-NoProfile", "-NonInteractive", "-File",'
        ' "`\\"$d\\wrapper.ps1`\\"") -NoNewWindow -PassThru'
        ' -WorkingDirectory <review-mirror>'
        ' -RedirectStandardInput "$d\\stdin.empty"'
        ' -RedirectStandardOutput "$d\\launch.out"'
        ' -RedirectStandardError "$d\\launch.err"') >= 3, (
        "all three launches use the shared block plus this lane's only"
        " delta, -WorkingDirectory; a lane with no launch command is not"
        " detached however its prose reads")
    assert "REPLY ARTIFACT for this lane is `$d\\reply`" in body, (
        "state seven needs a reply artifact; without one every"
        " successful call lands in state five and is discarded")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py -q -k detached`
Expected: 1 FAILED.

- [ ] **Step 3: Add the wrapper, the launch, and the reply artifact**

Keep the two existing Dispatch and Resume bullets EXACTLY as they are — they document the client contract and `test_backup_lane.py:137-148` reads them. Add below them a paragraph saying: all three calls reserve a directory, run in a wrapper, and launch through the shared block in `model-prompting-notes.md`'s `detached-dispatch-launch` region, with `-WorkingDirectory` as this lane's only delta; that `$b` is the brief read from its file, the same inline payload the bullets describe and the shape item 51 measured, never a pointer, which this lane's contract forbids; and that **the REPLY ARTIFACT for this lane is `$d\reply`**, the client's captured stdout, with stderr going to `$d\transcript`.

Then give the dispatch and resume wrappers in full, each of the shape:

```powershell
$code = 1
try {
$b = [System.IO.File]::ReadAllText("<brief-file>", (New-Object System.Text.UTF8Encoding($false, $true)))
<the client line from the matching bullet, with -p $b, > $d\reply 2> $d\transcript>
$code = $LASTEXITCODE
} catch { $code = 1 }
[System.IO.File]::WriteAllText("$d\exit", "$code")
```

and the reservation and launch lines from Task 4, with `-WorkingDirectory <review-mirror>` added. No `$OutputEncoding` preamble appears on this lane, deliberately: it passes the brief as an argument, which `brief-encoding-transport` already states, and adding one would imply a mechanism that does not apply.

- [ ] **Step 4: Give the write-probe the same treatment**

At `:353-359`, the WRITE-PROBE bullet gains its own reservation, wrapper and launch, written out rather than referred to. It is a real client call in a fresh session with the debate configuration. A sentence saying it "runs in a wrapper too" is exactly the shape round 3 rejected twice.

- [ ] **Step 5: TASK-LOCAL ORACLE**

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py -q`
Expected: PASS, including `test_the_backup_lane_is_detached` and `test_backup_lane.py:137-148` unamended. The `>= 3` counts are the oracle: they fail if any one of the three calls was left behind.

- [ ] **Step 6: Commit**

```bash
git add skills/multi-model-verify/references/backup-lane.md evals/multi-model-verify/test_backup_lane.py
git commit -m "dispatch all three kimi lane calls detached"
```

---

### Task 6: Suppress repository hooks during the mirror's remediation commit

Item 33 makes mirror construction automatic. Round 1 established construction is not side-effect-free: when a back-channel was TRACKED, `tools/new-review-mirror.ps1:1071-1089` runs `git commit` inside the copied repository, and that script's own BLOCKED message says the mirror carries the real repo's `.git`, hooks included. This lands BEFORE Task 7.

**Files:** Modify `tools/new-review-mirror.ps1:1071-1089` and `evals/multi-model-verify/test_review_mirror.py`

**Interfaces:** Consumes nothing. Produces a hook-free remediation commit, pinned.

- [ ] **Step 1: Write the failing test**

Assert that both the `git add` and the `git commit` in `new-review-mirror.ps1` carry `-c core.hooksPath=` pointed at a directory the script created and verified empty in the same run, and that a non-empty or uncreatable directory exits BLOCKED.

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -q -k hooks`
Expected: 1 FAILED.

- [ ] **Step 3: Create a verified-empty hooks directory and use it**

Before staging, create a fresh empty directory, assert zero entries, and pass `-c core.hooksPath=<it>` to both git calls. If it cannot be created or is not empty, exit BLOCKED with the reason. Never fall back to committing with hooks live.

- [ ] **Step 4: TASK-LOCAL ORACLE**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -q`
Expected: PASS. Then confirm by hand that `grep -c 'core.hooksPath' tools/new-review-mirror.ps1` is at least 2.

- [ ] **Step 5: Commit**

```bash
git add tools/new-review-mirror.ps1 evals/multi-model-verify/test_review_mirror.py
git commit -m "run the mirror remediation commit with hooks suppressed"
```

---

### Task 7: Build the review mirror automatically instead of asking (backlog item 33)

The preflight says "STOP and surface it to the user" and that clearing happens "only on the user's choice, never automatically". The answer has never differed. Item 33 records a second, worse cost: the prompt put "skip the cross-vendor lane" one tap from the recommended answer, when the user is least likely to be weighing it.

**Files:** Modify `skills/multi-model-verify/SKILL.md:90-93`, `evals/multi-model-verify/test_contract_coverage.py`, `evals/multi-model-verify/test_multi_model_verify.py`

**Interfaces:** Consumes Task 6's hook suppression — do NOT land this first; it makes automatic an act that Task 6 makes safe. Produces `back-channel-auto-mirror`.

- [ ] **Step 1: Write the failing pin**

```python
    def test_the_back_channel_response_is_automatic(self):
        """The prompt bought a round trip and offered a worse option.

        Backlog item 33, filed 2026-08-11 with a screenshot from ANOTHER
        repo - so a skill defect, not a parallax quirk - and restated by
        the user on 2026-08-30 when it fired again. The two choices were
        building the mirror and skipping the cross-vendor lane; a
        question whose recommended answer never changes should not put
        dropping that lane one tap away.

        The CHECK is not what is removed. Only the question is.
        """
        text = " ".join(read(SKILL_MD).split())
        assert (
            "If present: BUILD THE MIRROR AND REPORT. Do NOT ask first - "
            "every deletion happens in a file COPY, and the remediation "
            "commit runs with repository hooks suppressed, so nothing in "
            "the reviewed tree executes and there is no destructive act "
            "to consent to. What was found is still EVIDENCE and still "
            "goes in the debate record with its paths, and the "
            "post-mirror re-enumeration must still come back empty before "
            "any round dispatches. A mirror that cannot be built - path "
            "budget blown, scratch unavailable, hooks not suppressible - "
            "is BLOCKED, never a fallback to dispatching over the real "
            "tree.") in text
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k back_channel_response`
Expected: 1 FAILED.

- [ ] **Step 3: Replace the prompt with the report**

Replace these two passages and the blank line between them:

```
   If present: STOP and surface it to the user - never dispatch a review
   over an instruction back-channel.

   Clearing it - only on the user's choice, never automatically: run
```

with the marked region whose text is the pin's string above, wrapped in `<!-- contract:start id=back-channel-auto-mirror -->` and `<!-- contract:end -->`, followed by `Run`. Copy it exactly: the originals use em dashes, the replacement uses hyphens, and the pin depends on it.

- [ ] **Step 4: Declare the region**

Add `"back-channel-auto-mirror",` to `DECLARED_REGIONS`, noting it holds what SURVIVES the prompt's removal — the evidence duty, the empty re-enumeration, the hook suppression, and BLOCKED — rather than the removal itself. A region naming only what was deleted would let a later edit delete the check with the question.

- [ ] **Step 5: TASK-LOCAL ORACLE**

Run: `python -m pytest evals/multi-model-verify -q -k "back_channel_response or declared or locked" && python evals/tools/skill_lint.py skills/multi-model-verify --strict`
Expected: PASS, exit 0. Then confirm `grep -c "STOP and surface it to the user" skills/multi-model-verify/SKILL.md` is `0`.

- [ ] **Step 6: Commit**

```bash
git add skills/multi-model-verify/SKILL.md evals/multi-model-verify/test_multi_model_verify.py evals/multi-model-verify/test_contract_coverage.py
git commit -m "build the review mirror without asking"
```

---

### Task 8: Render, parse and stub-run every wrapper, before any quota is spent

Round 3's finding: the tests count raw strings, so a wrapper that will not PARSE passes all of them and the first thing to notice would be a real round. This plan already produced one parse error by transcription. Zero quota, no client call.

**Files:** Create `evals/multi-model-verify/test_wrapper_renders_and_parses.py`; modify `SKILL.md` and `backup-lane.md` to add extraction markers.

**Interfaces:** Consumes the finished blocks from Tasks 4 and 5. Produces the gate Task 9 runs behind.

- [ ] **Step 1: Give every wrapper a unique extraction marker**

Round 3's finding: "extract four fenced blocks" does not say WHICH, and the codex wrapper fence is immediately followed by another `powershell` launch fence, so an ordinal extractor can parse the wrong one and pass. Put an HTML comment immediately before each wrapper fence — `<!-- wrapper:codex-fresh -->`, `<!-- wrapper:codex-resume -->`, `<!-- wrapper:kimi-dispatch -->`, `<!-- wrapper:kimi-resume -->`, `<!-- wrapper:kimi-write-probe -->` — and one before each launch fence, `<!-- launch:... -->`.

- [ ] **Step 2: Extract by marker, exactly one match each**

Read the fence following each marker from the DOCUMENTS, never from a copy held in the test: a copy passes while the document rots. Assert exactly one match per marker and fail on zero or more than one.

Reproduce the Markdown-to-copied-code transformation explicitly: strip the same leading indentation a reader copying the block would strip, and assert the result is what those bytes become. Round 3 named a normalizer that "repairs" indentation as a false-green.

Assert **no `<placeholder>` remains** after substitution, so a missed placeholder cannot parse as valid PowerShell and pass.

- [ ] **Step 3: Parse each rendered wrapper on both hosts**

```powershell
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile($path, [ref]$null, [ref]$errors)
if ($errors.Count -gt 0) { $errors | ForEach-Object { $_.Message }; exit 1 }
```

Run under `$env:PARALLAX_PS_HOST` for each host.
Expected: zero parse errors on both.

- [ ] **Step 4: Execute each wrapper against a stub, three outcomes**

Substitute `<kimi-code-binary>` with the stub's ABSOLUTE path. Round 3's finding: PATH shadowing does not intercept an absolute invocation, so a PATH-only stub would let this "zero-quota" gate call the real client. `codex` is invoked by bare name and PATH shadowing does work for it; do both explicitly rather than relying on one mechanism.

Per wrapper: stub exits 0 and writes a reply — expect `exit` contains `0` and the reply artifact exists; stub exits 3 writing nothing — expect `3`; a pre-client throw — expect `exit` EXISTS with a non-zero code, which is what `$code = 1` before the `try` is for.

Assert no real client ran: the stub records its own invocation and the test reads that record.

- [ ] **Step 5: TASK-LOCAL ORACLE**

Run: `python -m pytest evals/multi-model-verify/test_wrapper_renders_and_parses.py -q` on both hosts.
Expected: PASS. Then delete a marker in a scratch copy and confirm the test FAILS on zero matches — a gate that cannot fail is what this task exists to prevent.

- [ ] **Step 6: Commit**

```bash
git add evals/multi-model-verify/test_wrapper_renders_and_parses.py skills/multi-model-verify/SKILL.md skills/multi-model-verify/references/backup-lane.md
git commit -m "parse and stub-run every wrapper before spending quota"
```

---

### Task 9: Measure what the stubs cannot, on both hosts

**Files:** Create `docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/wrapper-probe.md`

**Interfaces:** Consumes Tasks 4, 5 and Task 8's green gate. Produces a per-host, per-measurement record.

- [ ] **Step 1: Measure the harness boundary**

Wrapper body: a 90-second sleep, then the exit write. Launch with the shared block. Record the wall-clock time the launching tool call took to return, whether the pid was alive in a SEPARATE later tool call, and whether the exit file appeared only after the sleep.

Expected: the call returns in seconds, the process is alive in the next call, the exit file appears late. This is the plan's central promise and nothing before this tested it.

- [ ] **Step 2: Measure that the completion states hold**

Against a STUB, not the real client — round 2 established that killing the real wrapper between reply and sidecar is a millisecond race nobody can aim at. The stub writes the reply artifact and then sleeps thirty seconds.

Three cases. Kill the tree with `taskkill /PID <id> /T /F` inside the sleep, then poll: expect state two, exited with no exit file. Run the directory reservation twice on the same path: expect the second to FAIL rather than proceed. Let the stub exit zero having written an EMPTY reply artifact: expect state six, not seven.

If any reports a review result, STOP.

- [ ] **Step 3: Measure the brief's encoding through the wrapper**

A brief with at least one em dash and one non-Latin character, no-BOM UTF-8. Record SHA-256 and byte length BEFORE dispatching. Dispatch through Task 4's blocks against a cheap real round, then bind with `tools/read-codex-round-evidence.ps1 -Fresh`.

Expected: the binding ACCEPTS and the recorded prompt is byte-identical to the fixture.

- [ ] **Step 4: Repeat all three on the other host**

- [ ] **Step 5: Write the record**

Per host and measurement: host version, what was run, what was observed, verdict. State the limits: the Kimi lane's wrappers were stub-run in Task 8 but no real Kimi round was dispatched here; and a passing pin locks a rule's presence in the contract, never any session's behaviour.

If any measurement FAILS, stop. Do not amend a pin to accept it.

- [ ] **Step 6: Commit**

```bash
git add docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/wrapper-probe.md
git commit -m "measure the detached wrapper on both hosts"
```

---

### Task 10: Reconcile the spec, close the items, run the full gates

Round 3's finding: the spec's constraints still said four states, its testing section named obsolete regions, its timeout was still an open question, and Tasks 9 and 10 still told the record to say the Kimi lane was not detached. Every gate would have passed while the committed records described the wrong scope. Reconciliation is a step with an oracle, not an afterthought.

**Files:** Modify `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`, `docs/superpowers/plans/2026-07-27-0150-backlog.md`, `CLAUDE.md`

**Interfaces:** Consumes Tasks 1 to 9.

- [ ] **Step 1: Reconcile the spec with the plan**

Update the spec's state model to SEVEN with liveness first; replace its region names with the five that exist; record that the timeout question is SETTLED at thirty minutes and no longer open; and correct any remaining sentence saying the Kimi lane is not detached.

- [ ] **Step 2: TASK-LOCAL ORACLE for convergence**

```bash
grep -n "four states\|five states\|six states\|not detached\|Open questions" docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md
```

Expected: no hit describing a state count other than seven, and no hit saying the Kimi lane is not detached. This is the check round 3 found missing.

- [ ] **Step 3: Run the five local gates, detached**

Background, named `Gate: five local gates`:

```bash
python evals/tools/skill_lint.py skills/multi-model-verify --strict && python evals/tools/skill_scanner.py skills && python evals/tools/check_exact_line_oracles.py && python evals/tools/run_trigger_evals.py && python -m pytest evals -q
```

Expected: all five green, zero FAILED and zero ERROR. Do not pipe through `tail` or `head`: the failure NAMES are what a second run needs.

- [ ] **Step 4: Run the suite on the other host, and the behavioural evals**

`$env:PARALLAX_PS_HOST` set to the host Step 3 did not use, `python -m pytest evals -q`, detached, named `Gate: pytest <host>`. Then `python evals/tools/run_behavioral_evals.py`, detached. Record any red case by NAME.

- [ ] **Step 5: Update CLAUDE.md**

"Long-running commands" gains a pointer to the five detached-dispatch regions as where the mechanism now lives, and the background-task naming rule for gates and mirrors, which have no lane.

- [ ] **Step 6: Close items 32 and 33**

Both headings `OPEN` to `DONE` with the version. Remove item 32's ranking entry and renumber below it. Rebuild the `**Open.**` and `**Done.**` lists by reading the headings, not by editing the previous list.

State in item 32 what was NOT done: item 51 still owns the argv escaping repair; item 31 is untouched; the resume-after-a-kill recovery is still unmeasured; and no real Kimi round was dispatched in Task 9.

- [ ] **Step 7: Commit**

```bash
git add CLAUDE.md docs/superpowers/plans/2026-07-27-0150-backlog.md docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md
git commit -m "close items 32 and 33"
```

---

## What the rounds changed

Sol session `01a055c5-935e-76e3-ad1d-83721bc67d79`. Round 1: 12 claims, 8 FIX. Round 2: 11 re-judged, 7 closed. Round 3: 8 re-judged, 4 closed, three sweeps each finding more. Every finding was reproduced before acceptance; none was refuted; one reviewer ruling reversed a scope decision I had already told the user about.

**Round 1** — a stale exit file plus a fresh reply plus a killed wrapper read as complete; the exit write sat inside the `try`; `check-drift.ps1` was excluded for a wrong reason; the backup-lane pins were claimed to prove byte identity and do not; a third Kimi call existed; Task 5 asserted detachment and implemented none; the wrapper-file claim overreached; mirror construction runs `git commit` with the reviewed repo's hooks live; `Start-Process` was called the only mechanism; streams were inherited; the plan contradicted itself on the timeout; two harness facts were not repo-verifiable.

**Round 2** — the staleness rule was stated, pinned and probed but never implemented; the freshness rule was unsatisfiable; five states duplicated one and omitted another; the Kimi deferral was unsound and was withdrawn; the spec's enumeration was stale; an unenforced convention shared a pin with completion safety; raw-string tests pass a wrapper that will not parse; the kill window was a millisecond race.

**Round 3** — create-new semantics were promised and not specified; the state count disagreed across region, `SKILL.md` and spec; the Kimi lane had wrappers but no launch and no reply artifact, so every successful call would have been discarded; wrapper extraction could select the wrong fence and a PATH stub cannot intercept an absolute binary; and seven tasks could pass their own verification with their change absent or partial.

**The recurring class, named by round 3:** prose standing in for mechanism, three rounds running. The two structural answers are the single shared launch block and a task-local oracle on every task.

## After the tasks

The version bump comes AFTER the diff debate, not here. `plugin update` keys only on the version string, and a number cached before the debate rewrites the tree installs nothing afterwards.
