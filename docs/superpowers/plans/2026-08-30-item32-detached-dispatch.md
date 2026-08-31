# Items 32 and 33 Implementation Plan: detached dispatch, and the mirror prompt that always had one answer

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the codex dispatch commands the skill documents incapable of blocking the caller past the 600-second tool ceiling, so a review round can no longer be killed with its quota spent and no reply written; and stop the preflight asking a question whose answer has never once differed.

**Architecture:** Each documented dispatch keeps its existing pipeline verbatim, but that pipeline moves into a wrapper script which is launched with `Start-Process` and left running. The launching call returns at once, writing the child's process id to a file. Later calls poll that id and an exit-code file the wrapper writes as its own last act, after its `finally`. Nothing about the brief, the flags, the route check or the round-evidence binding changes.

**Tech Stack:** Markdown skill contracts under `skills/multi-model-verify/`, pytest pins under `evals/multi-model-verify/`, PowerShell 5.1 and PowerShell 7.

**Spec:** `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`

**Revised 2026-08-30 after Sol round 1**, session `01a055c5-935e-76e3-ad1d-83721bc67d79`, which returned FIX on eight of twelve claims and found one new false-completion path. See `## What round 1 changed` at the end; every finding was reproduced against the repo before it was accepted.

## Global Constraints

- **Change the tests FIRST, then the skill.** The transport commands are live-verified contracts locked by `evals/multi-model-verify/test_multi_model_verify.py`; the backup lane's by `test_backup_lane.py`.
- **Both PowerShell hosts.** A green suite on one host proves one interpreter. Set `$env:PARALLAX_PS_HOST` to reach the other.
- **A killed, hung, or unfinished round must never be readable as a completed one.** FIVE states must stay distinguishable; see the `detached-dispatch-states` region in Task 3. Round 1 found a path that produced exactly this failure, so this constraint is the plan's primary output, not a caveat on it.
- **Every control path is round-numbered and must not exist before the launch.** Wrapper, pid file, exit file, reply file, transcript file. The launch refuses if any is already present. `SKILL.md:220-226` already requires this of the reply and transcript only, which is what made the false-completion path reachable.
- **Item 51 is NOT fixed here**, and the Kimi lane is therefore NOT detached here. See Task 5, which is a deferral with its reason, not an omission.
- **Item 31 is NOT fixed here.** `tools/check-drift.ps1:1060` and `commands/doctor.md:70` are not touched.
- **The resume-after-a-kill recovery is NOT blessed.** Its soundness is unmeasured. This work stops the kill; it says nothing about recovering from one.
- **These pins must stay green** (`evals/multi-model-verify/test_multi_model_verify.py:609-650`): five exact strings counted at `>= 2` across `SKILL.md`; `test_resume_pipes_the_brief_on_stdin` matching `$brief | codex exec ... resume <SESSION_ID> -` with `[^\n]*`, so that span stays on ONE physical line; and the raw pin forbidding a three-space-indented `& {`.
- **A pin that matches raw file text needs its phrase unbroken on one physical line.** Check which read a pin uses before editing near it. `evals/multi-model-verify/test_backup_lane.py:47-50` defines a whitespace-NORMALIZED read; pins built on it do not constrain wrapping and do not prove byte identity.
- **Two facts this plan relies on are NOT repo-verifiable**, and must be cited as harness tool contract rather than as repo evidence: that each tool call gets a fresh shell so shell state does not persist, and that the Agent tool runs subagents in the background. Round 1 correctly flagged both as unverifiable from the tree.
- **Dispatch every debate round and every full gate DETACHED, from the first attempt**, and **name the backgrounded call with its lane and round** — `Sol R1 debate round`, `Kimi R2 debate round` — or, where there is no lane, with its kind: `Gate: pytest 5.1`, `Mirror build`.

---

### Task 1: Raise the SKILL.md token ceiling deliberately, with the measurement recorded

`SKILL.md` has **20 characters** of headroom before the soft warning and **1020** before the hard error. Measured 2026-08-30 at `fb3e2bb`: body 20983 chars, 5245 estimated tokens, budget 5250, ceiling 5500. The remaining tasks add more than that. `skill_lint.py:308-326` names exactly two legitimate remedies and this plan uses both: explanation relocates to `model-prompting-notes.md` (Task 3), and the ceiling rises here with the measurement written down.

**Files:**
- Modify: `evals/tools/skill_lint.py:78-102`

**Interfaces:**
- Consumes: nothing.
- Produces: `BODY_TOKEN_CEILING = 5900`. Tasks 4 and 7 depend on this landing first, or their own verification fails on a budget error unrelated to their change.

- [ ] **Step 1: Measure the current body and record the number**

Run:

```bash
python -c "import io;t=io.open('skills/multi-model-verify/SKILL.md',encoding='utf-8').read();b=t.split('---',2)[2];print(len(b), len(b)//4, len(b.splitlines()))"
```

Expected: three numbers. Record them verbatim in the comment written in Step 2. Measure and use yours; do not copy the numbers above if they disagree.

- [ ] **Step 2: Raise the ceiling and write the reason beside it**

In `evals/tools/skill_lint.py`, change `BODY_TOKEN_CEILING = 5500` to `BODY_TOKEN_CEILING = 5900` and add above it a comment in the file's existing style stating: the date, the measured body size, that backlog item 32 moved the dispatch steps to a detached form that must be read at the point of use, that the explanation was relocated to `references/model-prompting-notes.md` first, and that this is the remedy `skill_lint.py`'s own error message names.

Leave `BODY_TOKEN_BUDGET` at `5250`. The soft warning is the signal that the file is growing and this change should not silence it.

- [ ] **Step 3: Verify the budget suite still passes**

Run: `python -m pytest evals/multi-model-verify/test_skill_lint_budget.py -q`
Expected: PASS. The band tests read `mod.BODY_TOKEN_CEILING` dynamically. The frozen pre-change fixture asserts `"BODY_TOKEN_CEILING" not in parts[2]` and `"5000" in parts[2]` about a HISTORICAL copy; it must not be edited.

- [ ] **Step 4: Verify strict lint still exits 0**

Run: `python evals/tools/skill_lint.py skills/multi-model-verify --strict; echo "exit=$?"`
Expected: `exit=0`. If the soft warning turns out to FAIL under `--strict`, raise `BODY_TOKEN_BUDGET` to `5650` as well and record in the same comment that strict escalates warnings. Do not discover this in Task 4.

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
- Produces: four tests — `test_both_dispatches_write_an_exit_code_file`, `test_both_dispatches_are_launched_detached`, `test_the_dispatch_is_not_carried_by_a_here_string`, and `test_every_pre_client_failure_still_writes_an_exit_code`. Task 4 makes the failing ones pass.

- [ ] **Step 1: Write the failing tests**

Add these to the class that already holds `test_the_brief_is_read_and_piped_as_utf8`:

```python
    def test_both_dispatches_write_an_exit_code_file(self):
        """A detached round is read from files, so the exit code must be
        one of them, and it must be written AFTER the finally.

        $proc.ExitCode is not usable: on Windows PowerShell 5.1 the
        file-redirect form of Start-Process never retains a native
        process handle, and ExitCode silently reads null when the child
        exits before the next statement touches .Handle. A review round
        always wins that race.

        Sol round 1 refuted the first draft of this: it wrote the
        sidecar INSIDE the try, before the finally, so it was not the
        wrapper's last act and an exception on the way to the client
        skipped it entirely.
        """
        text = read(SKILL_MD)
        assert text.count(
            "} catch { $code = 1 } finally"
            " { $OutputEncoding = $priorOutputEncoding }\n"
            '[System.IO.File]::WriteAllText("<exit-file>", "$code")') >= 2, (
            "the exit code must be written after the finally, as the"
            " wrapper's last act, so encoding is restored before"
            " completion is published, and every failure path must reach"
            " that write"
        )

    def test_every_pre_client_failure_still_writes_an_exit_code(self):
        """A wrapper that dies before codex runs must still be readable.

        Without the catch, a throw on the override hash check leaves no
        exit file, and 'no exit file' then means both 'still running'
        and 'failed early'. Those are different states and the poll has
        to tell them apart.
        """
        text = read(SKILL_MD)
        assert text.count(
            "$code = 1\n"
            "$priorOutputEncoding = $OutputEncoding\n"
            "try {") >= 2, (
            "the exit code defaults to failure, so any path that does not"
            " reach the client reports failure rather than nothing; and"
            " the prior encoding is captured OUTSIDE the try, or the"
            " finally restores a value that was never set"
        )
        assert text.count("} catch { $code = 1 } finally {") >= 2, (
            "an exception before or during the client call must still"
            " produce an exit code, and catch and finally are one clause:"
            " a separate `} finally {` after a closed catch is a parse"
            " error, which is a new way to spend a round on nothing"
        )

    def test_both_dispatches_are_launched_detached(self):
        """The command a session copies must not be able to block it.

        Filed as backlog item 32 on 2026-08-11 and fired again on
        2026-08-30, on a session whose route was verified correct before
        it dispatched. The rule already existed in
        model-prompting-notes.md and the round was still lost, so the
        instruction now lives in the command rather than beside it.

        All three standard streams are redirected. The in-repo
        precedent at tools/check-drift.ps1:923-927 redirects all three;
        inheriting them through -NoNewWindow alone was Sol round 1's
        finding, because the launched host then shares the caller's
        console handles.

        -Wait is forbidden rather than merely absent: it is the one flag
        that turns this back into the blocking form while still looking
        like the detached one.
        """
        text = read(SKILL_MD)
        assert text.count(
            "$proc = Start-Process -FilePath (Get-Process -Id $PID).Path"
            ' -ArgumentList @("-NoProfile", "-NonInteractive", "-File",'
            ' "`\"<wrapper-file>`\"") -NoNewWindow -PassThru'
            ' -RedirectStandardInput <empty-file>'
            ' -RedirectStandardOutput <launch-out-file>'
            ' -RedirectStandardError <launch-err-file>') >= 2, (
            "both dispatches must launch the wrapper detached, on the"
            " session's own host, with the wrapper path individually"
            " quoted and all three standard streams redirected"
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

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k "exit_code_file or launched_detached or here_string or pre_client_failure"`
Expected: **3 FAILED, 1 PASSED.** The three that fail name the missing strings.

`test_the_dispatch_is_not_carried_by_a_here_string` passes from the start, and that is correct. `SKILL.md` contains no here-string marker today (verified 2026-08-30 at `fb3e2bb`). It guards against a shape THIS fix could introduce, not a shape the fix removes. Do not plant a here-string to make it fail first.

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
- Produces: three marked regions — `detached-dispatch-mechanism`, `detached-dispatch-states`, `detached-dispatch-operation` — each locked by exactly one pin. Task 4 cites them from `SKILL.md`.

- [ ] **Step 1: Insert the three regions**

In `skills/multi-model-verify/references/model-prompting-notes.md`, insert immediately AFTER the sentence ending `is spent for nothing.` and BEFORE `Measured repeatedly through 0.21.x.`, so the sentence pinned by `test_dispatch_traps_are_documented_in_the_notes` is not touched. That pin reads the whitespace-normalized file and asserts that exact sentence.

Region one:

```
  <!-- contract:start id=detached-dispatch-mechanism -->
  The pipeline moves into a WRAPPER SCRIPT which is launched with
  `Start-Process` and left running; the launching call returns at once.
  `Start-Process` is the mechanism this repo selected, not the only one
  that could work: `Start-Job` was rejected because each tool call gets a
  fresh shell, so a job handle does not survive to the call that would
  wait on it. Three parts are load-bearing. The encoding preamble goes
  INSIDE the wrapper, because a new process does not inherit the caller's
  `$OutputEncoding` and a wrapper without it silently reinstates the
  fault 0.23.0 fixed. The wrapper is a FILE rather than an argument list,
  which removes the `Start-Process -ArgumentList` serialization boundary
  - that cmdlet joins its array with a plain space and does not quote an
  element containing one - but does NOT remove every quoting layer: the
  wrapper is still parsed by PowerShell and still builds a native argv.
  The wrapper writes its own exit code to a file as its last act, after
  its `finally`, because 5.1's file-redirect `Start-Process` never
  retains a native handle and `$proc.ExitCode` reads null whenever the
  child outlives the next statement, which a review round always does.
  <!-- contract:end -->
```

Region two:

```
  <!-- contract:start id=detached-dispatch-states -->
  A detached round is read from files, and FIVE states must stay apart.
  Still running. Exited with NO exit file, which means the wrapper died
  before it could report and is never the same as still running. Exited
  with an exit file that is stale, missing or malformed. Exited with a
  fresh valid exit file carrying a non-zero code. Exited with a fresh
  valid exit file carrying zero AND a reply file this round's call
  freshly wrote. ONLY THE LAST is a review result; the other four are
  transport failures per fallbacks.md. Staleness is what makes this
  real: every control path - wrapper, pid, exit, reply, transcript - is
  round-numbered and MUST NOT exist before the launch, and the launch
  refuses if one does. Without that, an exit file left by an earlier
  round plus a reply the client wrote before the wrapper was killed
  reads as the last state and accepts a round nobody finished.
  <!-- contract:end -->
```

Region three:

```
  <!-- contract:start id=detached-dispatch-operation -->
  Poll with `Get-Process -Id` or `Wait-Process -Id` against the recorded
  pid, never with `ps -p` from Git Bash, which cannot see Windows pids
  and reports a live process as gone. Each poll is BOUNDED and returns;
  a poll that waits indefinitely is the blocking form again. At THIRTY
  MINUTES without a terminal state, stop polling, report the round as
  UNFINISHED, and ask the user whether to keep waiting or abandon it.
  Neither answer is a review result. To abandon, fell the whole tree
  with `taskkill /PID <id> /T /F`: killing the launcher alone leaves the
  client orphaned, which is what the 2026-08-11 report of this item
  observed at zero CPU growth. Name the backgrounded call for the person
  watching it - the reviewer LANE and the ROUND lead the description, as
  in `Sol R1 debate round`, and work with no lane leads with its kind,
  as in `Gate: pytest 5.1`. Nothing enforces that name; it is convention
  and this rule is its only carrier.
  <!-- contract:end -->
```

- [ ] **Step 2: Declare the three regions**

Add to `DECLARED_REGIONS` in `evals/multi-model-verify/test_contract_coverage.py`, immediately before the closing `}`:

```python
    # 0.28.0, backlog item 32. The dispatch a session copies could block
    # the caller and be killed at 600 seconds with the quota spent.
    # THREE regions because a region must fit inside a single pin and
    # these say different kinds of thing. MECHANISM is why the wrapper
    # is a file and where the encoding preamble lives. STATES is how a
    # detached round is read, which is the half that decides whether an
    # unfinished round can be mistaken for a clean one - Sol round 1
    # found exactly that path in the first draft, so this region is the
    # plan's primary output. OPERATION is what the human driving it
    # does: bounded polls, the thirty-minute escalation, the whole-tree
    # kill, and what the background task is called.
    "detached-dispatch-mechanism",
    "detached-dispatch-states",
    "detached-dispatch-operation",
```

- [ ] **Step 3: Write one pin per region**

Add three tests beside `test_dispatch_traps_are_documented_in_the_notes`, named `test_the_detached_dispatch_mechanism_is_pinned`, `test_the_detached_dispatch_states_are_pinned`, and `test_the_detached_dispatch_operation_is_pinned`. Each reads `" ".join(read(REFERENCES / "model-prompting-notes.md").split())` and asserts its region's full text as one normalized string literal, in the style of the existing pin at `test_multi_model_verify.py:970-997`.

Write each assertion by copying the region text from Step 1 and normalizing its whitespace, not by retyping it.

- [ ] **Step 4: Run the coverage and pin checks**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py evals/multi-model-verify/test_multi_model_verify.py -q`
Expected: PASS, except the Task 2 tests which still fail. If `test_every_marked_region_is_locked_by_a_pin` reports a region as unlocked, the pin's string does not match the normalized document text — fix the pin's spacing, never the region's words.

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

**Files:**
- Modify: `skills/multi-model-verify/SKILL.md:174-190` (round 1) and `skills/multi-model-verify/SKILL.md:236-251` (resume)

**Interfaces:**
- Consumes: `BODY_TOKEN_CEILING = 5900` from Task 1; the three contract regions from Task 3; the failing tests from Task 2.
- Produces: the finished round-1 and resume steps. Task 8 measures them.

- [ ] **Step 1: Rewrite the round-1 step**

Replace step 2's prose and fenced block. The wrapper block is today's block with the failure scaffolding added; every other character stays as it is, because five pins count exact strings in it.

Prose above the block:

```
2. Compose the reviewer's debate brief per references/model-prompting-notes.md, write
   it to a scratchpad file, then write this wrapper to `<wrapper-file>` — as a
   FILE, never from a here-string, whose terminator cannot survive this block's
   indentation — and launch it DETACHED. Never run it inline: the caller's
   600-second ceiling kills a crossing round with the quota spent and no reply
   written. Every path below is round-numbered and must not already exist
   (references/model-prompting-notes.md).
```

The wrapper block:

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
$brief | codex exec --sandbox read-only --disable plugins --disable apps --disable memories -c mcp_servers.node_repl.enabled=false -c $override -m <canonical-model-id> -c model_reasoning_effort=<canonical-effort> --output-last-message <reply-file> - > <transcript-file> 2>&1
$code = $LASTEXITCODE
} catch { $code = 1 } finally { $OutputEncoding = $priorOutputEncoding }
[System.IO.File]::WriteAllText("<exit-file>", "$code")
```

Then the launch block and its lead:

```
   Launch it and STOP. Read the round only after the poll reaches one of the
   five states in references/model-prompting-notes.md:
```

```powershell
$proc = Start-Process -FilePath (Get-Process -Id $PID).Path -ArgumentList @("-NoProfile", "-NonInteractive", "-File", "`"<wrapper-file>`"") -NoNewWindow -PassThru -RedirectStandardInput <empty-file> -RedirectStandardOutput <launch-out-file> -RedirectStandardError <launch-err-file>
[System.IO.File]::WriteAllText("<pid-file>", "$($proc.Id)")
```

Keep the existing sentence "Both encoding lines are load-bearing on Windows PowerShell 5.1 (references/model-prompting-notes.md)." and everything from the `verified-override-dispatch` contract marker onward exactly as it is.

**Three details in that block are load-bearing and a "tidy" breaks them.** `$priorOutputEncoding` is captured OUTSIDE the `try`, or the `finally` restores a variable that was never assigned when the failure is early. `catch` and `finally` are ONE clause on ONE line: a `} finally {` written after an already-closed `catch` is a PowerShell parse error, and the wrapper would then die before codex ran - a new way to spend a round on nothing, created by the fix for the old one. The exit write is the last line, outside every block. Transcribe the block exactly, and let Task 8 Step 1 be what proves it parses.

- [ ] **Step 2: Rewrite the resume step the same way**

Apply the identical changes to step 3's block. The `$brief | codex exec ... resume <SESSION_ID> -` line must stay on ONE physical line and must not otherwise change. Keep the paragraph "The preamble repeats in full every round..." and everything after it.

- [ ] **Step 3: Run the Task 2 tests**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k "exit_code_file or launched_detached or here_string or pre_client_failure"`
Expected: 4 PASSED.

- [ ] **Step 4: Run the pins that lock the old shape**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q`
Expected: PASS. `test_the_brief_is_read_and_piped_as_utf8` and `test_resume_pipes_the_brief_on_stdin` must pass WITHOUT being edited. If either fails, the wrapper body was altered beyond the added scaffolding — restore it rather than amending the pin.

- [ ] **Step 5: Run the lint and the scanner**

Run: `python evals/tools/skill_lint.py skills/multi-model-verify --strict && python evals/tools/skill_scanner.py skills`
Expected: both PASS, exit 0. A body-token error means Task 1's ceiling is too low; report the measured number rather than deleting text to fit.

- [ ] **Step 6: Commit**

```bash
git add skills/multi-model-verify/SKILL.md
git commit -m "dispatch both codex rounds detached"
```

---

### Task 5: Record why the Kimi lane is NOT detached in this cycle

**This task writes no mechanism. It writes a deferral and its reason.** The previous revision of this plan claimed to detach the backup lane and in fact only added a paragraph asserting it was detached. Sol round 1 caught that. The honest resolution is not to write the missing mechanism here, because it cannot be written without deciding item 51.

**Why it cannot be done here.** `references/backup-lane.md:24-30` passes the brief INLINE, in the dispatch's own `-p "<the whole brief>"` payload, and `test_backup_lane.py:137-148` documents that form. A wrapper has to get those brief bytes into the client somehow, and every option changes the argument path that item 51 exists to fix: embedding the brief as wrapper source needs byte-safe generation for arbitrary text, and reading it into a variable inside the wrapper replaces the literal argument with a variable expansion, which is precisely the 5.1 splatting surface item 51 measured. Detaching this lane therefore requires item 51's decision, and item 51 is out of scope for this cycle by the user's own constraint.

**There are THREE Kimi client calls, not two.** Round 1 found the third: the write-probe at `references/backup-lane.md:353-359` runs before round 1 of every backup-lane debate, in a fresh disposable session with the full debate configuration, and `references/panels.md:51-53` makes panels inherit it. It can cross the ceiling like any other call. Any future work on this lane covers all three.

**Files:**
- Modify: `skills/multi-model-verify/references/backup-lane.md`
- Modify: `docs/superpowers/plans/2026-07-27-0150-backlog.md` (item 51)

**Interfaces:**
- Consumes: nothing.
- Produces: a paragraph in `backup-lane.md` stating the lane is NOT detached, and a note on item 51 naming the three calls.

- [ ] **Step 1: State the gap in backup-lane.md**

Add after the Resume bullet, as ONE physical line:

```
- This lane is NOT detached, and its three client calls - dispatch, resume, and the write-probe below - can each be killed by the caller's 600-second ceiling with the round's quota spent. Backlog item 32 detached the codex lane and deliberately did not touch this one: every way of getting the inline `-p` brief into a wrapper changes the argument path that backlog item 51 exists to fix, so detaching this lane is part of item 51's work and not separable from it.
```

- [ ] **Step 2: Add the note to item 51**

In `docs/superpowers/plans/2026-07-27-0150-backlog.md`, under item 51, record that item 32's cycle established item 51 now also owns detaching this lane's three calls, and name them with their line references.

- [ ] **Step 3: Verify**

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py -q`
Expected: PASS, including `test_backup_lane.py:137-148` unamended. Those pins read whitespace-normalized text, so they do not prove byte identity; here they only confirm the two command strings were not disturbed by an added paragraph.

- [ ] **Step 4: Commit**

```bash
git add skills/multi-model-verify/references/backup-lane.md docs/superpowers/plans/2026-07-27-0150-backlog.md
git commit -m "record that the kimi lane is not detached and why"
```

---

### Task 6: Suppress repository hooks during the mirror's remediation commit

Item 33 makes mirror construction automatic. Round 1 established that construction is not side-effect-free: when a back-channel was TRACKED, `tools/new-review-mirror.ps1:1071-1089` runs `git commit` inside the copied repository, and that script's own error text says the mirror carries the real repo's `.git`, hooks included. An automatically executed repository hook is a real side effect, so this lands BEFORE Task 7.

**Files:**
- Modify: `tools/new-review-mirror.ps1:1071-1089`
- Modify: `evals/multi-model-verify/test_review_mirror.py`

**Interfaces:**
- Consumes: nothing.
- Produces: a hook-free remediation commit, pinned.

- [ ] **Step 1: Write the failing test**

In `evals/multi-model-verify/test_review_mirror.py`, add a test asserting that the `git add` and `git commit` invocations in `tools/new-review-mirror.ps1` both carry `-c core.hooksPath=` pointed at a directory the script created and verified empty in the same run.

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -q -k hooks`
Expected: 1 FAILED.

- [ ] **Step 3: Create a verified-empty hooks directory and use it**

Before staging, create a fresh empty directory under the mirror's parent, assert it contains zero entries, and pass `-c core.hooksPath=<that directory>` to both the `add` and the `commit`. If the directory cannot be created or is not empty, exit BLOCKED with a reason — never fall back to committing with hooks live.

- [ ] **Step 4: Verify**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -q`
Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/new-review-mirror.ps1 evals/multi-model-verify/test_review_mirror.py
git commit -m "run the mirror remediation commit with hooks suppressed"
```

---

### Task 7: Build the review mirror automatically instead of asking (backlog item 33)

The preflight currently says "STOP and surface it to the user" and that clearing happens "only on the user's choice, never automatically". The answer has never differed. Item 33 also records a second, worse cost: the prompt put "skip the cross-vendor lane" one tap from the recommended answer, at the moment the user is least likely to be weighing it.

**Files:**
- Modify: `skills/multi-model-verify/SKILL.md:90-93`
- Modify: `evals/multi-model-verify/test_contract_coverage.py`
- Modify: `evals/multi-model-verify/test_multi_model_verify.py`

**Interfaces:**
- Consumes: Task 6's hook suppression. Do not land this first: it makes an act automatic that Task 6 makes safe.
- Produces: one marked region, `back-channel-auto-mirror`, locked by one pin.

- [ ] **Step 1: Write the failing pin**

Add to `evals/multi-model-verify/test_multi_model_verify.py`:

```python
    def test_the_back_channel_response_is_automatic(self):
        """The prompt bought a round trip and offered a worse option.

        Filed as backlog item 33 on 2026-08-11 with a screenshot from
        ANOTHER repo, so it is a skill defect rather than a parallax
        quirk, and restated by the user on 2026-08-30 when it fired
        again. The two choices offered were building the mirror and
        skipping the cross-vendor lane; a question whose recommended
        answer never changes should not put dropping that lane one tap
        away.

        The CHECK is not what is being removed. Only the question is.
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

Replace these two passages, and the blank line between them:

```
   If present: STOP and surface it to the user - never dispatch a review
   over an instruction back-channel.

   Clearing it - only on the user's choice, never automatically: run
```

with:

```
   <!-- contract:start id=back-channel-auto-mirror -->
   If present: BUILD THE MIRROR AND REPORT. Do NOT ask first - every
   deletion happens in a file COPY, and the remediation commit runs with
   repository hooks suppressed, so nothing in the reviewed tree executes
   and there is no destructive act to consent to. What was found is still
   EVIDENCE and still goes in the debate record with its paths, and the
   post-mirror re-enumeration must still come back empty before any round
   dispatches. A mirror that cannot be built - path budget blown, scratch
   unavailable, hooks not suppressible - is BLOCKED, never a fallback to
   dispatching over the real tree.
   <!-- contract:end -->
   Run
```

Copy the replacement exactly rather than retyping its punctuation: the originals use em dashes and the replacement uses hyphens, and the pin depends on it.

- [ ] **Step 4: Declare the region**

Add `"back-channel-auto-mirror",` to `DECLARED_REGIONS`, with a comment noting it is backlog item 33 and that the region holds what SURVIVES the prompt's removal — the evidence duty, the empty re-enumeration, the hook suppression, and the BLOCKED state — rather than the removal itself. A region naming only what was deleted would let a later edit delete the check along with the question.

- [ ] **Step 5: Verify**

Run: `python -m pytest evals/multi-model-verify -q && python evals/tools/skill_lint.py skills/multi-model-verify --strict`
Expected: PASS, exit 0.

- [ ] **Step 6: Commit**

```bash
git add skills/multi-model-verify/SKILL.md evals/multi-model-verify/test_multi_model_verify.py evals/multi-model-verify/test_contract_coverage.py
git commit -m "build the review mirror without asking"
```

---

### Task 8: Measure the two things this plan asserts and has not proven

Three measurements, all on both hosts. Round 1 found that the first draft measured encoding only and never measured its own central promise.

**Files:**
- Create: `docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/wrapper-probe.md`

**Interfaces:**
- Consumes: the finished `SKILL.md` blocks from Task 4.
- Produces: a probe record with a per-host verdict for each measurement.

- [ ] **Step 1: Measure the harness boundary**

Write a wrapper whose body is a 90-second sleep followed by the exit write. Launch it with the Task 4 launch block. Record: the wall-clock time the launching tool call took to return, whether the pid was still alive in a SEPARATE later tool call, and whether the exit file appeared only after the sleep.

Expected: the launching call returns in seconds, the process is alive in the next call, and the exit file appears late. That is the plan's central promise and nothing before this step tested it.

- [ ] **Step 2: Measure that the false-completion path is closed**

Plant a stale `<exit-file>` containing `0` at the round's path, then run the launch. Expected: the launch REFUSES because a control path already exists.

Then repeat with fresh paths, kill the wrapper tree with `taskkill /PID <id> /T /F` after the reply file appears but before the wrapper writes its exit file, and poll.

Expected: the poll reports a transport failure, not a review result. If it reports a review result, STOP: that is the exact defect round 1 found and the fix did not close it.

- [ ] **Step 3: Measure the brief's encoding through the wrapper**

Write a brief containing at least one em dash and one non-Latin character as no-BOM UTF-8. Record its SHA-256 and byte length BEFORE dispatching. Dispatch through the Task 4 blocks against a cheap real round, then bind with `tools/read-codex-round-evidence.ps1 -Fresh`.

Expected: the binding ACCEPTS and the recorded prompt is byte-identical to the fixture.

- [ ] **Step 4: Repeat all three on the other host**

Set `$env:PARALLAX_PS_HOST` to the host Steps 1 to 3 did not use and repeat them unchanged.

- [ ] **Step 5: Write the probe record**

Record per host and per measurement: host version, what was run, what was observed, and the verdict. State the limits explicitly: this measures the CODEX lane only; the Kimi lane was not detached and was not measured; and a passing pin locks the rule's presence in the contract, never any session's behaviour.

If any measurement FAILS, stop. Do not amend a pin to accept it.

- [ ] **Step 6: Commit**

```bash
git add docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/wrapper-probe.md
git commit -m "measure the detached wrapper on both hosts"
```

---

### Task 9: Close the items and run the full gates

**Files:**
- Modify: `docs/superpowers/plans/2026-07-27-0150-backlog.md`
- Modify: `CLAUDE.md`

**Interfaces:**
- Consumes: Tasks 1 to 8.
- Produces: a green gate set and closed items.

- [ ] **Step 1: Run the five local gates, detached**

Run in the background, named `Gate: five local gates`:

```bash
python evals/tools/skill_lint.py skills/multi-model-verify --strict && python evals/tools/skill_scanner.py skills && python evals/tools/check_exact_line_oracles.py && python evals/tools/run_trigger_evals.py && python -m pytest evals -q
```

Expected: all five green, zero FAILED and zero ERROR. Do not pipe through `tail` or `head`: the failure NAMES are what a second run needs.

- [ ] **Step 2: Run the suite on the other PowerShell host**

Set `$env:PARALLAX_PS_HOST` to the host Step 1 did not use, re-run `python -m pytest evals -q` detached, named `Gate: pytest <host>`.
Expected: green.

- [ ] **Step 3: Run the behavioural evals**

`skills/` changed, so run `python evals/tools/run_behavioral_evals.py` detached.
Expected: no regression against main. Record any red case by NAME.

- [ ] **Step 4: Update CLAUDE.md**

The "Long-running commands" section gains: a pointer to the skill's three detached-dispatch regions as the place the mechanism now lives; and the background-task naming rule for gates and mirrors, which have no lane.

- [ ] **Step 5: Close items 32 AND 33 in the backlog**

Set both headings from `OPEN` to `DONE` with the version. Remove item 32's ranking entry and renumber below it. Rebuild the `**Open.**` and `**Done.**` lists by reading the headings, not by editing the previous list.

State in item 32 what was NOT done: the Kimi lane is not detached and item 51 now owns it; items 51 and 31 are untouched; the resume-after-a-kill recovery is still unmeasured.

- [ ] **Step 6: Commit**

```bash
git add CLAUDE.md docs/superpowers/plans/2026-07-27-0150-backlog.md
git commit -m "close items 32 and 33"
```

---

## What round 1 changed

Sol session `01a055c5-935e-76e3-ad1d-83721bc67d79`, 12 claims, 8 FIX. Every finding below was reproduced against the repo before acceptance; none was refuted.

| Finding | Where it landed |
|---|---|
| A stale exit file plus a fresh reply plus a killed wrapper reads as a completed round | Four states became FIVE; every control path is round-numbered and must not pre-exist. Task 3 region two, Task 8 Step 2 |
| The exit write sat inside the `try`, so it was not the last act and an early throw skipped it | `$code = 1` default, `catch`, write after `finally`. Task 2, Task 4 |
| `check-drift.ps1` is not immune - it calls `Stop-Job` at 900 seconds | Reason corrected; it stays out of scope for the right reason |
| The backup-lane pins read whitespace-normalized text and do not prove byte identity | Global Constraints corrected; the claim was withdrawn |
| A third Kimi client call exists, the pre-round-1 write-probe | Named in Task 5 and handed to item 51 |
| Task 5 asserted detachment and implemented none of it | Task 5 is now a deferral with its reason, not a claim |
| A wrapper file does not remove every quoting layer | Region one says which boundary it removes and which remain |
| Mirror construction runs `git commit` and the copied repo's hooks execute | New Task 6, landing before item 33's automation |
| `Start-Process` was called the only mechanism | Region one calls it the selected one and says why the alternative fails |
| Streams were inherited rather than redirected | All three redirected, matching `check-drift.ps1:923-927` |
| The plan contradicted itself on the timeout | Policy frozen: bounded polls, thirty-minute escalation, continue-or-kill, never a review result |
| Two harness facts are not repo-verifiable | Global Constraints marks both as tool contract, not repo evidence |

## After the tasks

The version bump comes AFTER the diff debate, not here. `plugin update` keys only on the version string, and a number cached before the debate rewrites the tree installs nothing afterwards.
