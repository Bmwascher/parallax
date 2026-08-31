# Items 32 and 33 Implementation Plan: detached dispatch, and the mirror prompt that always had one answer

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every long client call the skill documents incapable of blocking the caller past the 600-second tool ceiling, so a review round can no longer be killed with its quota spent and no reply written; and stop the preflight asking a question whose answer has never once differed.

**Architecture:** A new shipped tool, `tools/dispatch-detached.ps1`, performs the whole launch as ONE fail-closed transaction: reserve a directory, install the wrapper, start the process, record the pid, and write a launch-commit artifact last. It also computes the completion state. Each documented call keeps its client invocation verbatim inside a lane-specific wrapper body and calls the tool to launch it.

**Tech Stack:** PowerShell 5.1 and PowerShell 7, Markdown skill contracts under `skills/multi-model-verify/`, pytest pins under `evals/multi-model-verify/`.

**Spec:** `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`

**Revision 5, 2026-08-30.** Four Sol rounds on session `01a055c5-935e-76e3-ad1d-83721bc67d79` plus a two-lane poll. Round 4 closed nothing and named why: the launch is a four-step transaction that existed as five copied snippets, with the rule pinned somewhere else. Sol and Fable were polled separately on the fork and both chose a shipped tool. **The user approved reversing their design-phase choice on 2026-08-30**; the design's settled question 2 is reopened and the record says so plainly.

## What the two lanes conditioned their answer on, and what this plan does with it

- **Sol: the tool does NOT make the failure impossible.** A hard kill between `Start-Process` returning and the pid being recorded still leaves a live untracked process. So `LAUNCH UNKNOWN` is a named state in the contract, not an eliminated one. This plan takes Sol's weaker claim over Fable's stronger one because Fable stated it had not re-verified the round 4 finding and took the relay.
- **Both: anchor the call.** All three tools the skill calls today use bare relative paths — `SKILL.md:94`, `:121`, `:228` — which is item 58's own cause. The new call uses `${CLAUDE_PLUGIN_ROOT}`. The three existing ones stay item 58's, and Task 9 records the asymmetry rather than widening scope silently.
- **Fable: the stub gate could not have caught this.** Task 7 runs the WRAPPER, while reserve-write-launch-record sits outside the wrapper in every copy. With the tool, that sequence is inside a real script with a real test file, which is the point.

## Global Constraints

- **Change the tests FIRST, then the tool or the skill.** The transport commands are live-verified contracts locked by `evals/multi-model-verify/test_multi_model_verify.py`; the backup lane's by `test_backup_lane.py`. The new tool joins that class.
- **Both PowerShell hosts.** A green suite on one proves one interpreter. `$env:PARALLAX_PS_HOST` reaches the other.
- **A killed, hung, or unfinished round must never be readable as a completed one.** Rounds 1, 2, 3 and 4 each found a hole in the completion model. Treat the class as open.
- **The tool is fail-closed.** `$ErrorActionPreference = 'Stop'` around every step, `-ErrorAction Stop` on the reservation and the launch, and a `catch` that kills the process tree and exits non-zero if anything fails after the process starts.
- **Item 51 is NOT fixed here, and the Kimi lane IS detached here.** Item 51's probe measured "a brief file is read and passed inline as `-p <brief>`, exactly the shape `references/backup-lane.md` documents" (`probe-record.md:27-31`). Item 51 keeps the `CommandLineToArgvW` escaping repair (`probe-record.md:112-137`).
- **Item 31 is NOT fixed here**, and **item 58 is NOT fixed here** beyond anchoring this one new call.
- **The resume-after-a-kill recovery is NOT blessed.** Its soundness is unmeasured.
- **These pins must stay green** (`test_multi_model_verify.py:609-650`): five exact strings at `>= 2` across `SKILL.md`; `test_resume_pipes_the_brief_on_stdin` matching `$brief | codex exec ... resume <SESSION_ID> -` with `[^\n]*`; and the raw pin forbidding a three-space-indented `& {`.
- **`test_backup_lane.py:47-50` is a whitespace-NORMALIZED read.** Pins on it prove neither wrapping nor byte identity.
- **Two facts here are NOT repo-verifiable** and are cited as harness tool contract: each tool call gets a fresh shell, and the Agent tool runs subagents in the background.
- **Dispatch every round and gate DETACHED**, named with lane and round (`Sol R1 debate round`) or, with no lane, its kind (`Gate: pytest 5.1`).

---

### Task 1: Build `tools/dispatch-detached.ps1`, tests first

This is the whole point of revision 5. The four steps become one transaction in one file with one test file, instead of five copies with five document pins.

**Files:**
- Create: `tools/dispatch-detached.ps1`
- Create: `evals/multi-model-verify/test_dispatch_detached.py`

**Interfaces:**
- Consumes: nothing.
- Produces two modes, and every later task depends on these exact names:
  - `-Launch -DispatchDir <path> -WrapperBody <path> [-WorkingDirectory <path>] [-Json]`
  - `-Poll -DispatchDir <path> [-Json]`
- `-Launch` prints, and `-Poll` returns, JSON with `state` drawn from exactly: `launch-unknown`, `running`, `no-exit-file`, `exit-unreadable`, `exit-nonzero`, `no-reply`, `reply-empty`, `reply-present`.
- Exit codes match `new-review-mirror.ps1:17-18`: 0 clean, 1 blocked with the reason on stdout, 2 script or environment error.

- [ ] **Step 1: Write the failing tests**

`evals/multi-model-verify/test_dispatch_detached.py`, driving the REAL script against stub payloads. Every case runs on whichever host `PARALLAX_PS_HOST` names, so CI covers both.

Cases, each named for what it protects:

- `test_a_taken_directory_blocks_and_starts_nothing` — pre-create the directory; expect exit 1, the reason on stdout, and no process started. The reservation is `New-Item -ItemType Directory` with `-ErrorAction Stop` and no `-Force`; round 4 found that without `-ErrorAction Stop` the error is non-terminating and the following statements run with no valid path.
- `test_force_is_not_accepted_in_any_argument_order` — assert the script source contains no `-Force` on the reservation, checked by parsing the command rather than by string order. Round 4 found the previous pin only forbade the exact token order `-ItemType Directory -Force`.
- `test_a_committed_launch_publishes_pid_then_commit_last` — `launch.committed` is written AFTER `pid`, and its presence is what distinguishes a committed launch. Assert the order by content, not by timestamp.
- `test_a_failure_after_start_kills_the_tree_and_blocks` — inject a failure between start and commit; expect exit 1 and the started process gone. This is the state Sol said cannot be eliminated, so the tool must at least not leave it silently.
- `test_poll_reports_launch_unknown_when_commit_is_absent` — a reserved directory with no `launch.committed`; expect `launch-unknown`. Not running, not failed, not complete.
- `test_poll_reports_running_while_the_pid_is_alive` — and asserts that NO other file is read in that branch, because a reply being written is not a reply.
- `test_poll_distinguishes_every_terminal_state` — one case per remaining state name above, driven by planted files.
- `test_poll_never_reports_reply_present_without_a_committed_launch`.

- [ ] **Step 2: Run them to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_dispatch_detached.py -q`
Expected: every test FAILS or ERRORS because the script does not exist. Read the output and confirm the failures name missing behaviour, not a broken test harness.

- [ ] **Step 3: Write the script**

`tools/dispatch-detached.ps1`, ASCII only, Windows PowerShell 5.1 compatible, following the header-comment style of `tools/new-review-mirror.ps1:1-30`: what it is for, what it refuses, and its exit codes.

`-Launch`, in order, under `$ErrorActionPreference = 'Stop'`:

1. `$d = (New-Item -ItemType Directory -Path $DispatchDir -ErrorAction Stop).FullName`. Failure here is BLOCKED and nothing has started.
2. Copy `$WrapperBody` to `$d\wrapper.ps1`; create the empty `$d\stdin.empty`.
3. `$proc = Start-Process -FilePath (Get-Process -Id $PID).Path -ArgumentList @("-NoProfile", "-NonInteractive", "-File", "`"$d\wrapper.ps1`"") -NoNewWindow -PassThru -ErrorAction Stop -RedirectStandardInput "$d\stdin.empty" -RedirectStandardOutput "$d\launch.out" -RedirectStandardError "$d\launch.err"`, plus `-WorkingDirectory` when given.
4. Write `$d\pid`, then write `$d\launch.committed` LAST.
5. Wrap steps 3 to 4 in a `catch` that runs `taskkill /PID $proc.Id /T /F` when `$proc` exists, then exits 1. Never leave a started process unrecorded and unreported.

`-Poll` computes the state in this order, and the order is the contract:

1. No `launch.committed` → `launch-unknown`. Stop. Nothing else is read.
2. Pid alive → `running`. Stop. Nothing else is read.
3. No `exit` file → `no-exit-file`. Unreadable or not a plain integer → `exit-unreadable`. Non-zero → `exit-nonzero`.
4. Zero and no `reply` → `no-reply`. Zero and `reply` is empty → `reply-empty`. Zero and `reply` has content → `reply-present`.

`reply-present` is NOT a review result on its own. The caller still runs the lane's round-evidence binder, and only a clean binding makes it one. Say that in the script header so nobody reads the state name as a verdict.

- [ ] **Step 4: TASK-LOCAL ORACLE**

Run: `python -m pytest evals/multi-model-verify/test_dispatch_detached.py -q` on BOTH hosts.
Expected: all PASS on both. Then run one negative check by hand: delete the `catch` in step 5, confirm `test_a_failure_after_start_kills_the_tree_and_blocks` goes red, and restore it. A test suite that cannot fail is what this task exists to prevent.

- [ ] **Step 5: Commit**

```bash
git add tools/dispatch-detached.ps1 evals/multi-model-verify/test_dispatch_detached.py
git commit -m "add the fail-closed detached dispatch tool"
```

---

### Task 2: State the contract in the notes, declare it, pin it

Four regions. The explanation lives here because `SKILL.md` is budgeted; measured 2026-08-30 at `caa7e1b`, its body is 20983 chars against a 5250 soft budget and a 5500 hard ceiling.

**Files:**
- Modify: `skills/multi-model-verify/references/model-prompting-notes.md:297-314`
- Modify: `evals/multi-model-verify/test_contract_coverage.py:624-728`
- Modify: `evals/multi-model-verify/test_multi_model_verify.py`

**Interfaces:** Produces `detached-dispatch-tool`, `detached-dispatch-states`, `detached-dispatch-operation`, `background-task-naming`, each locked by one pin.

- [ ] **Step 1: Insert the four regions**

Insert AFTER the sentence ending `is spent for nothing.` and BEFORE `Measured repeatedly through 0.21.x.`, leaving untouched the sentence pinned by `test_dispatch_traps_are_documented_in_the_notes`.

**Region one — the tool:**

```
  <!-- contract:start id=detached-dispatch-tool -->
  The launch is ONE TRANSACTION and it lives in ONE PLACE:
  `${CLAUDE_PLUGIN_ROOT}/tools/dispatch-detached.ps1`. It reserves a
  directory, installs the wrapper, starts the process, records the pid,
  and writes a launch-commit artifact LAST; a failure after the process
  starts kills the tree and BLOCKS rather than leaving it unrecorded. No
  lane writes its own launch. A lane supplies a WRAPPER BODY carrying
  its client invocation verbatim and, where its client needs one, a
  working directory; it changes nothing else. This replaced five copied
  snippets, which regenerated the same defect across four debate rounds:
  reserve, write, start and record are four steps, and a rule written in
  one place while the steps are copied to five cannot make them atomic.
  The path is anchored to the plugin root because the three tool calls
  this skill already makes are bare relative paths, which is backlog
  item 58's own cause; a new call must not join that.
  <!-- contract:end -->
```

**Region two — states:**

```
  <!-- contract:start id=detached-dispatch-states -->
  The tool's `-Poll` mode computes the state and the ORDER of the checks
  is the contract. First, no launch-commit artifact means LAUNCH
  UNKNOWN: the directory was reserved and the launch never completed,
  which may mean nothing started or may mean a live untracked process,
  and those are not distinguishable from disk. It is never success.
  Shipping the transaction in one tool NARROWS this state; it does not
  remove it, because a hard kill between process creation and the
  recording of the pid is still reachable. Second, a live pid means
  RUNNING and NOTHING ELSE IS READ - a reply being written is not a
  reply. Only after those two come the terminal states: no exit file,
  an exit file unreadable or not a plain integer, a non-zero code, zero
  with no reply artifact, zero with an empty reply artifact, and zero
  with a reply artifact that has content. Only the last can become a
  review result, and it is not one by itself: the lane's round-evidence
  binder must also return clean. Every other state is a transport
  failure per fallbacks.md, except RUNNING, which is UNFINISHED.
  <!-- contract:end -->
```

**Region three — operation:**

```
  <!-- contract:start id=detached-dispatch-operation -->
  Each poll is BOUNDED and returns; a poll that waits indefinitely is
  the blocking form again. At THIRTY MINUTES without a terminal state,
  stop polling, report the round UNFINISHED, and ask the user whether to
  keep waiting or abandon it. Neither answer is a review result. To
  abandon, or to clear a LAUNCH UNKNOWN that may hold a live process,
  fell the whole tree with `taskkill /PID <id> /T /F`: killing the
  launcher alone leaves the client orphaned, which is what the
  2026-08-11 report of this item observed at zero CPU growth. Never poll
  with `ps -p` from Git Bash, which cannot see Windows pids and reports
  a live process as gone.
  <!-- contract:end -->
```

**Region four — naming**, separate because it is the only one nothing enforces and a naming edit must not reopen a completion-safety pin:

```
  <!-- contract:start id=background-task-naming -->
  Name the backgrounded call for the person watching it. The reviewer
  LANE and the ROUND lead the description, as in `Sol R1 debate round`
  or `Kimi R2 debate round`; work with no lane leads with its kind, as
  in `Gate: pytest 5.1` or `Mirror build`. A cycle runs several lanes
  across several rounds at once and a name omitting either cannot be
  read at a glance. NOTHING ENFORCES THIS. It is a convention about what
  a human sees, and its pin proves only that the rule is written down.
  <!-- contract:end -->
```

- [ ] **Step 2: Declare the four regions**

Add to `DECLARED_REGIONS` with a comment recording: backlog item 32; that TOOL replaced a launch that had been five copied snippets; that STATES leads with LAUNCH UNKNOWN because the cross-vendor reviewer refused the claim that a tool eliminates it; and that NAMING is separate because it is the only unenforced one.

- [ ] **Step 3: Write one pin per region**

Four tests beside `test_dispatch_traps_are_documented_in_the_notes`, each asserting its region's full normalized text, built by copying the region and normalizing rather than retyping. The naming pin's docstring must say it is a documentation-presence pin, not behavioural enforcement.

- [ ] **Step 4: TASK-LOCAL ORACLE**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q` and confirm `test_declared_regions_match_the_documents` and `test_every_marked_region_is_locked_by_a_pin` both pass. Then delete one region's markers in a scratch copy and confirm `test_declared_regions_match_the_documents` FAILS on it. Round 4 found this task's previous oracle satisfied by removing a whole region/declaration/pin triplet.

- [ ] **Step 5: Confirm the pre-existing trap pin is untouched**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k dispatch_traps`
Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add skills/multi-model-verify/references/model-prompting-notes.md evals/multi-model-verify/test_contract_coverage.py evals/multi-model-verify/test_multi_model_verify.py
git commit -m "state and pin the detached dispatch contract"
```

---

### Task 3: Point SKILL.md's two codex dispatches at the tool

**Files:** Modify `skills/multi-model-verify/SKILL.md:174-190` and `:236-251`

**Interfaces:** Consumes Task 1's tool and Task 2's regions. Produces the finished round-1 and resume steps.

- [ ] **Step 1: Write the failing tests**

In `test_multi_model_verify.py`, add:

```python
    def test_both_dispatches_call_the_tool_anchored(self):
        """One launch, in one place, reached by an anchored path.

        Four debate rounds found the same defect while the launch was
        five copied snippets. The anchor matters separately: the three
        tool calls this skill already makes are bare relative paths
        (SKILL.md:94, :121, :228), which is backlog item 58's own cause,
        and a new call must not join that.
        """
        text = read(SKILL_MD)
        assert text.count(
            "powershell -NoProfile -File"
            " ${CLAUDE_PLUGIN_ROOT}/tools/dispatch-detached.ps1 -Launch"
            " -DispatchDir <dispatch-dir> -WrapperBody <wrapper-file>"
            " -Json") >= 2
        assert "Start-Process" not in text, (
            "no lane writes its own launch; the tool owns the whole"
            " transaction and a second copy is how it drifts"
        )

    def test_the_point_of_use_sends_the_reader_to_the_states(self):
        text = read(SKILL_MD)
        assert text.count(
            "-Poll -DispatchDir <dispatch-dir> -Json") >= 2
        assert text.count("references/model-prompting-notes.md's"
                          " detached-dispatch-states") >= 2
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k "call_the_tool_anchored or sends_the_reader_to_the_states"`
Expected: 2 FAILED.

- [ ] **Step 3: Rewrite the round-1 step**

Prose, then the wrapper body, then the launch:

```
2. Compose the reviewer's debate brief per references/model-prompting-notes.md, write
   it to a scratchpad file, then write this wrapper body to `<wrapper-file>` — as
   a FILE, never from a here-string, whose terminator cannot survive this block's
   indentation — and launch it with the tool. Never run it inline: the caller's
   600-second ceiling kills a crossing round with the quota spent and no reply
   written.
```

The wrapper body is today's block with the exit scaffolding added and `$d` supplied by the tool as the directory the wrapper runs in:

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
$brief | codex exec --sandbox read-only --disable plugins --disable apps --disable memories -c mcp_servers.node_repl.enabled=false -c $override -m <canonical-model-id> -c model_reasoning_effort=<canonical-effort> --output-last-message $PSScriptRoot\reply - > $PSScriptRoot\transcript 2>&1
$code = $LASTEXITCODE
} catch { $code = 1 } finally { $OutputEncoding = $priorOutputEncoding }
[System.IO.File]::WriteAllText("$PSScriptRoot\exit", "$code")
```

`$PSScriptRoot` is the dispatch directory, because the tool installs the wrapper into it. That removes the need to pass a path in and removes one more thing a copy can get wrong.

Then the launch and the poll:

```
   Launch it and STOP. Read the round only when the poll reaches a terminal
   state; the order of those checks is references/model-prompting-notes.md's
   detached-dispatch-states and `reply-present` is not a verdict on its own:
```

```powershell
powershell -NoProfile -File ${CLAUDE_PLUGIN_ROOT}/tools/dispatch-detached.ps1 -Launch -DispatchDir <dispatch-dir> -WrapperBody <wrapper-file> -Json
```

```powershell
powershell -NoProfile -File ${CLAUDE_PLUGIN_ROOT}/tools/dispatch-detached.ps1 -Poll -DispatchDir <dispatch-dir> -Json
```

Keep "Both encoding lines are load-bearing on Windows PowerShell 5.1 (references/model-prompting-notes.md)." and everything from the `verified-override-dispatch` marker onward exactly as it is.

**Three details are load-bearing and a tidy breaks them.** `$priorOutputEncoding` is captured OUTSIDE the `try`, or the `finally` restores a variable never assigned on an early failure. `catch` and `finally` are ONE clause on ONE line: a `} finally {` after a closed `catch` is a parse error and the wrapper dies before codex runs. The exit write is the last line, outside every block.

- [ ] **Step 4: Rewrite the resume step identically**

Same wrapper shape, same two tool calls. The `$brief | codex exec ... resume <SESSION_ID> -` line stays on ONE physical line and does not otherwise change.

- [ ] **Step 5: TASK-LOCAL ORACLE**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q && python evals/tools/skill_lint.py skills/multi-model-verify --strict && python evals/tools/skill_scanner.py skills`
Expected: PASS, exit 0, including both new tests and `test_the_brief_is_read_and_piped_as_utf8` and `test_resume_pipes_the_brief_on_stdin` UNAMENDED. The `Start-Process` absence assertion is the oracle: it fails if any copied launch survives anywhere in the file.

If the lint reports a body-token error, the ceiling needs raising; do that as Task 9 Step 1 with the measurement recorded, and never by deleting text to fit.

- [ ] **Step 6: Commit**

```bash
git add skills/multi-model-verify/SKILL.md evals/multi-model-verify/test_multi_model_verify.py
git commit -m "dispatch both codex rounds through the tool"
```

---

### Task 4: Point the Kimi lane's three calls at the tool

The three are the dispatch (`backup-lane.md:25`), the resume (`:30`), and the write-probe (`:353-359`), which runs before round 1 of every backup-lane debate and which `panels.md:51-53` makes panels inherit.

**Files:** Modify `skills/multi-model-verify/references/backup-lane.md:21-35` and `:353-359`, and `evals/multi-model-verify/test_backup_lane.py`

**Interfaces:** Consumes Task 1 and Task 2. Produces three per-call contracts and their pins.

- [ ] **Step 1: Write the failing test**

Round 4 found the previous version's `>= 3` counts proved three strings existed somewhere without binding any of them to a call. So this test asserts PER CALL, using a marker per call.

```python
KIMI_CALLS = ("kimi-dispatch", "kimi-resume", "kimi-write-probe")


@pytest.mark.parametrize("call", KIMI_CALLS)
def test_each_kimi_call_is_launched_through_the_tool(call):
    """Per-call, not a global count.

    Round 4's finding: `>= 3` proved three launch strings existed
    somewhere in the file and bound none of them to a call site, so a
    section with two launches and a write-probe with none still passed.
    """
    body = _read(REFERENCES / "backup-lane.md")
    marker = "<!-- call:%s -->" % call
    assert body.count(marker) == 1, "exactly one section per call"
    section = body.split(marker, 1)[1].split("<!-- call:", 1)[0]
    assert (
        "powershell -NoProfile -File"
        " ${CLAUDE_PLUGIN_ROOT}/tools/dispatch-detached.ps1 -Launch"
        " -DispatchDir <dispatch-dir> -WrapperBody <wrapper-file>"
        " -WorkingDirectory <review-mirror> -Json") in section, (
        "this call has no launch; a lane described as detached with no"
        " launch command is what four rounds kept finding")
    assert '& "<kimi-code-binary>"' in section, (
        "this call has no client invocation")
    assert "$PSScriptRoot\\reply" in section, (
        "no reply artifact: every successful call would land in"
        " no-reply and be discarded")


def test_the_backup_lane_writes_no_launch_of_its_own():
    assert "Start-Process" not in _read(REFERENCES / "backup-lane.md")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py -q -k "launched_through_the_tool or no_launch_of_its_own"`
Expected: 4 FAILED — three parametrized cases and the negative.

- [ ] **Step 3: Give each of the three calls its own marked section**

Keep the existing Dispatch and Resume bullets EXACTLY as they are; they document the client contract and `test_backup_lane.py:137-148` reads them. Below them, and at the write-probe, add one `<!-- call:... -->` marked section per call, each containing: a wrapper body of the shape

```powershell
$code = 1
try {
$b = [System.IO.File]::ReadAllText("<brief-file>", (New-Object System.Text.UTF8Encoding($false, $true)))
& "<kimi-code-binary>" <that call's flags, in the documented order> -p $b > $PSScriptRoot\reply 2> $PSScriptRoot\transcript
$code = $LASTEXITCODE
} catch { $code = 1 }
[System.IO.File]::WriteAllText("$PSScriptRoot\exit", "$code")
```

and the anchored `-Launch` call with `-WorkingDirectory <review-mirror>`, because this client binds a session to the directory it was created in.

State once, above the three: `$b` is the brief read from its file — the same inline payload the bullets describe and the shape item 51 measured, never a pointer, which this lane's contract forbids. This lane's REPLY ARTIFACT is `$PSScriptRoot\reply`, the client's captured stdout, with stderr to `transcript`. No `$OutputEncoding` preamble appears here, deliberately: the brief goes as an argument, which `brief-encoding-transport` already states, and adding one would imply a mechanism that does not apply.

- [ ] **Step 4: TASK-LOCAL ORACLE**

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py -q`
Expected: PASS, all three parametrized cases and `test_backup_lane.py:137-148` unamended. The parametrization is the oracle: it names each call, so leaving one behind fails by name rather than by count.

- [ ] **Step 5: Commit**

```bash
git add skills/multi-model-verify/references/backup-lane.md evals/multi-model-verify/test_backup_lane.py
git commit -m "dispatch all three kimi lane calls through the tool"
```

---

### Task 5: Suppress repository hooks during the mirror's remediation commit

Item 33 makes mirror construction automatic. Round 1 established construction is not side-effect-free: when a back-channel was TRACKED, `tools/new-review-mirror.ps1:1071-1089` runs `git commit` inside the copied repository, and that script's own BLOCKED text says the mirror carries the real repo's `.git`, hooks included. This lands BEFORE Task 6.

**Files:** Modify `tools/new-review-mirror.ps1:1071-1089` and `evals/multi-model-verify/test_review_mirror.py`

- [ ] **Step 1: Write the failing test**

Assert both the `git add` and the `git commit` carry `-c core.hooksPath=` pointed at a directory the script created and verified empty in the same run, and that a non-empty or uncreatable directory exits BLOCKED rather than proceeding.

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -q -k hooks`
Expected: 1 FAILED.

- [ ] **Step 3: Create a verified-empty hooks directory and use it**

Before staging, create a fresh empty directory, assert zero entries, pass `-c core.hooksPath=<it>` to both git calls. If it cannot be created or is not empty, exit BLOCKED with the reason. Never fall back to committing with hooks live.

- [ ] **Step 4: TASK-LOCAL ORACLE**

Run: `python -m pytest evals/multi-model-verify/test_review_mirror.py -q`, then confirm `grep -c 'core.hooksPath' tools/new-review-mirror.ps1` is at least 2.

- [ ] **Step 5: Commit**

```bash
git add tools/new-review-mirror.ps1 evals/multi-model-verify/test_review_mirror.py
git commit -m "run the mirror remediation commit with hooks suppressed"
```

---

### Task 6: Build the review mirror automatically instead of asking (backlog item 33)

The preflight says "STOP and surface it to the user" and that clearing happens "only on the user's choice, never automatically". The answer has never differed. Item 33 records a second, worse cost: the prompt put "skip the cross-vendor lane" one tap from the recommended answer.

**Files:** Modify `skills/multi-model-verify/SKILL.md:90-93`, `evals/multi-model-verify/test_contract_coverage.py`, `evals/multi-model-verify/test_multi_model_verify.py`

**Interfaces:** Consumes Task 5. Do NOT land this first: it makes automatic an act Task 5 makes safe.

- [ ] **Step 1: Write the failing pin**

```python
    def test_the_back_channel_response_is_automatic(self):
        """Backlog item 33. The CHECK is not removed; only the question.

        Filed 2026-08-11 with a screenshot from ANOTHER repo, so a skill
        defect rather than a parallax quirk, and restated by the user on
        2026-08-30 when it fired again mid-cycle.
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
        assert "only on the user's choice, never automatically" not in text
        assert "STOP and surface it to the user" not in text
```

The last two assertions are round 4's finding: the previous oracle checked only the first of the two passages that had to go.

- [ ] **Step 2: Run it to verify it fails**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k back_channel_response`
Expected: 1 FAILED.

- [ ] **Step 3: Replace both passages with the marked region**

Replace both, and the blank line between them, with the pin's text wrapped in `<!-- contract:start id=back-channel-auto-mirror -->` / `<!-- contract:end -->`, followed by `Run`. Copy exactly: the originals use em dashes, the replacement uses hyphens, and the pin depends on it.

- [ ] **Step 4: Declare the region**

Add `"back-channel-auto-mirror",` to `DECLARED_REGIONS`, noting it holds what SURVIVES the prompt's removal — the evidence duty, the empty re-enumeration, the hook suppression, and BLOCKED — rather than the removal itself.

- [ ] **Step 5: TASK-LOCAL ORACLE**

Run: `python -m pytest evals/multi-model-verify -q -k "back_channel_response or declared or locked" && python evals/tools/skill_lint.py skills/multi-model-verify --strict`
Expected: PASS, exit 0. Both "not in" assertions are the oracle.

- [ ] **Step 6: Commit**

```bash
git add skills/multi-model-verify/SKILL.md evals/multi-model-verify/test_multi_model_verify.py evals/multi-model-verify/test_contract_coverage.py
git commit -m "build the review mirror without asking"
```

---

### Task 7: Render, parse and stub-run every wrapper body

The tool now owns the launch, so this task covers what remains copyable: the five wrapper bodies. Fable's round 5 point stands — the previous version of this gate ran the wrapper while the launch sat outside it, so it could not have caught round 4's defect. That gap is closed by Task 1's test file, not by this one; this one still matters because a wrapper body that will not parse passes every string pin.

**Files:** Create `evals/multi-model-verify/test_wrapper_renders_and_parses.py`; add extraction markers to `SKILL.md` and `backup-lane.md`.

- [ ] **Step 1: Mark every wrapper body**

`<!-- wrapper:codex-fresh -->`, `<!-- wrapper:codex-resume -->`, and one per Kimi call reusing Task 4's `<!-- call:... -->` sections. Exactly one match each.

- [ ] **Step 2: Extract by marker, from the documents, through an injectable source path**

Read the fence following each marker from the real documents. Round 4's finding: the negative self-test needs the extractor to accept a SOURCE PATH so a scratch copy can be fed to it; otherwise the test cannot be shown to fail. Give the extractor that parameter.

Reproduce the Markdown-to-copied-code transformation explicitly rather than normalizing, and assert no `<placeholder>` survives substitution.

- [ ] **Step 3: Parse each rendered body on both hosts**

```powershell
$errors = $null
[System.Management.Automation.Language.Parser]::ParseFile($path, [ref]$null, [ref]$errors)
if ($errors.Count -gt 0) { $errors | ForEach-Object { $_.Message }; exit 1 }
```

Expected: zero parse errors on both hosts.

- [ ] **Step 4: Stub-run each body, three outcomes**

Substitute `<kimi-code-binary>` with the stub's ABSOLUTE path — PATH shadowing does not intercept an absolute invocation — and shadow `codex` on PATH, which does work for a bare name. Per body: stub exits 0 writing a reply, expect `exit` = `0` and a reply present; stub exits 3 writing nothing, expect `3`; a pre-client throw, expect `exit` EXISTS with a non-zero code. Assert no real client ran.

- [ ] **Step 5: TASK-LOCAL ORACLE**

Run the suite on both hosts, then point the extractor at a scratch copy with one marker deleted and confirm it FAILS on zero matches.

- [ ] **Step 6: Commit**

```bash
git add evals/multi-model-verify/test_wrapper_renders_and_parses.py skills/multi-model-verify/SKILL.md skills/multi-model-verify/references/backup-lane.md
git commit -m "parse and stub-run every wrapper body"
```

---

### Task 8: Measure what the stubs cannot, on both hosts

**Files:** Create `docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/wrapper-probe.md`

- [ ] **Step 1: Measure the harness boundary**

A wrapper body of a 90-second sleep then the exit write, launched through the tool. Record the wall-clock time the launching tool call took to return, whether the pid was alive in a SEPARATE later tool call, and whether the exit file appeared only after the sleep.

Expected: the call returns in seconds, the process is alive in the next call, the exit file appears late. This is the plan's central promise and nothing before this tested it end to end.

- [ ] **Step 2: Measure the states the unit tests plant**

Against a stub that writes the reply then sleeps thirty seconds. Kill the tree inside that window and poll: expect `no-exit-file`. Reserve the same directory twice: expect the second to BLOCK. Let the stub exit zero with an empty reply: expect `reply-empty`.

- [ ] **Step 3: Measure the brief's encoding through a real round**

A brief with at least one em dash and one non-Latin character, no-BOM UTF-8; record SHA-256 and byte length BEFORE dispatching; dispatch through Task 3's blocks; bind with `tools/read-codex-round-evidence.ps1 -Fresh`.

Expected: the binding ACCEPTS and the recorded prompt is byte-identical to the fixture.

- [ ] **Step 4: Repeat on the other host**

- [ ] **Step 5: TASK-LOCAL ORACLE**

Round 4 found this task had no oracle. Add one: a test asserting the record file EXISTS and contains a row for each of the two hosts and each of the three measurements, so an unwritten or half-written record fails the suite rather than passing silently.

- [ ] **Step 6: Commit**

```bash
git add docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/wrapper-probe.md evals/multi-model-verify/test_wrapper_probe_record.py
git commit -m "measure the detached dispatch on both hosts"
```

---

### Task 9: Reconcile the spec, close the items, run the full gates

Round 4's finding: the spec still carried obsolete region names, a refuted claim that every wrapper carries the encoding preamble, and the refuted claim that a wrapper file has no quoting layer — and Task 10's grep searched for none of them. Reconciliation is a step with an oracle.

**Files:** Modify the spec, `docs/superpowers/plans/2026-07-27-0150-backlog.md`, `CLAUDE.md`, and `evals/tools/skill_lint.py` if the budget needs it.

- [ ] **Step 1: Raise the token ceiling only if the measurement says so**

Measure with the command in Task 2's preamble. If `SKILL.md`'s body is over 5500 estimated tokens, raise `BODY_TOKEN_CEILING` to a value the measurement justifies and write the date, the number and the reason beside it, per `skill_lint.py:308-326`. If it is under, change nothing and say so here. The tool-based design SHRANK the dispatch steps, so this may not be needed at all — do not raise a ceiling that does not need raising.

- [ ] **Step 2: Reconcile the spec with the plan**

Update: the state model to the tool's ordered checks with LAUNCH UNKNOWN first; the region inventory to the four that exist plus `back-channel-auto-mirror`; the encoding claim to be lane-specific, since an argument-passing lane carries no preamble; the quoting claim, since a wrapper file removes one serialization boundary and not every quoting layer; and question 2, which the user reopened and answered the other way on 2026-08-30. Say plainly that a settled decision was reversed and by whom.

- [ ] **Step 3: TASK-LOCAL ORACLE for convergence**

```bash
grep -n "detached-dispatch-codex\|detached-dispatch-backup\|no quoting layer at all\|four states\|five states\|six states\|seven states\|not detached" docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md
```

Expected: no hits outside a passage explicitly narrating history. Round 4 found the previous grep searching for none of these.

- [ ] **Step 4: Run the five local gates, detached**

Background, named `Gate: five local gates`:

```bash
python evals/tools/skill_lint.py skills/multi-model-verify --strict && python evals/tools/skill_scanner.py skills && python evals/tools/check_exact_line_oracles.py && python evals/tools/run_trigger_evals.py && python -m pytest evals -q
```

Expected: all five green, zero FAILED and zero ERROR. Do not pipe through `tail` or `head`.

- [ ] **Step 5: Run the other host and the behavioural evals**

`$env:PARALLAX_PS_HOST` set to the host Step 4 did not use, `python -m pytest evals -q` detached, named `Gate: pytest <host>`. Then `python evals/tools/run_behavioral_evals.py` detached. Record any red case by NAME.

- [ ] **Step 6: Update CLAUDE.md**

"Long-running commands" gains: a pointer to `${CLAUDE_PLUGIN_ROOT}/tools/dispatch-detached.ps1` as where the launch now lives; the four region names; and the background-task naming rule for gates and mirrors, which have no lane.

- [ ] **Step 7: Close items 32 and 33**

Both headings `OPEN` to `DONE` with the version. Remove item 32's ranking entry and renumber below it. Rebuild the `**Open.**` and `**Done.**` lists by reading the headings.

State in item 32 what was NOT done: item 51 still owns the argv escaping repair; item 31 is untouched; **item 58 is untouched except that this cycle's ONE new tool call is anchored while the three existing ones at `SKILL.md:94`, `:121` and `:228` are still bare relative paths** — record that asymmetry rather than leaving it to be discovered; the resume-after-a-kill recovery is still unmeasured; and LAUNCH UNKNOWN is narrowed, not eliminated.

- [ ] **Step 8: Commit**

```bash
git add CLAUDE.md docs/superpowers/plans/2026-07-27-0150-backlog.md docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md
git commit -m "close items 32 and 33"
```

---

## What the debate changed

Sol session `01a055c5-935e-76e3-ad1d-83721bc67d79`, four review rounds plus a two-lane poll. Round 1: 12 claims, 8 FIX. Round 2: 7 of 11 closed. Round 3: 4 of 8 closed. Round 4: nothing closed, and it named why. Every finding was reproduced before acceptance and none was refuted. Two reviewer rulings reversed decisions I had already reported to the user: the Kimi lane's scope, and the whole launch mechanism.

**Round 1** — a stale exit file plus a fresh reply plus a killed wrapper read as complete; the exit write sat inside the `try`; `check-drift.ps1` was excluded for a wrong reason; the backup-lane pins do not prove byte identity; a third Kimi call existed; Task 5 asserted detachment and implemented none; the wrapper-file claim overreached; mirror construction runs `git commit` with the reviewed repo's hooks live; `Start-Process` was called the only mechanism; streams were inherited; the plan contradicted itself on the timeout; two harness facts were not repo-verifiable.

**Round 2** — the staleness rule was stated, pinned and probed but never implemented; the freshness rule was unsatisfiable; five states duplicated one and omitted another; the Kimi deferral was unsound and was withdrawn; the spec's enumeration was stale; an unenforced convention shared a pin with completion safety; raw-string tests pass a wrapper that will not parse; the kill window was a millisecond race.

**Round 3** — create-new semantics were promised and not specified; the state count disagreed across three documents; the Kimi lane had wrappers but no launch and no reply artifact, so every successful call would have been discarded; extraction could select the wrong fence and a PATH stub cannot intercept an absolute binary; seven tasks could pass their own verification with their change absent.

**Round 4** — the reservation was not fail-closed; an eighth condition existed outside the state model entirely, reachable three ways; `>= N` counts bound nothing to a call site; the launch was never actually centralized; eight of ten oracles were still weak and one task had none; the spec was still stale in ways the convergence grep did not search for.

**The poll** — both lanes independently chose the shipped tool. Sol conditioned it on not claiming the failure is eliminated; Fable observed that the stub gate could not have caught the defect at all, because the launch sequence sat outside the wrapper it ran. Both required the anchored path, and both cited the three existing bare relative paths as item 58's own cause.

## After the tasks

The version bump comes AFTER the diff debate, not here. `plugin update` keys only on the version string, and a number cached before the debate rewrites the tree installs nothing afterwards.
