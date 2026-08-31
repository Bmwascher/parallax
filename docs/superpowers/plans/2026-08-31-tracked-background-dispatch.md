# Tracked Background Dispatch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Stop a review round from owning the session while it runs, without giving up the user's view of it: the tool prepares the round and the harness runs it as a TRACKED BACKGROUND command, named for its lane and round.

**Architecture:** `tools/dispatch-detached.ps1` keeps its whole completion model and loses its launcher. `-Launch` becomes `-Prepare`, which performs the same fail-closed transaction and stops before creating a child. The caller runs the prepared wrapper as a background command. Each wrapper publishes its own pid and start ticks as its first act. `-Poll` gains one state, `not-started`.

**Tech Stack:** PowerShell 5.1 and PowerShell 7, Markdown skill contracts under `skills/multi-model-verify/`, pytest pins under `evals/multi-model-verify/`.

**Spec:** `docs/superpowers/specs/2026-08-31-tracked-background-dispatch-design.md`

## Global Constraints

- **Change the tests FIRST, then the tool or the skill.** The transport commands are live-verified contracts locked by `evals/multi-model-verify/test_multi_model_verify.py` and `test_backup_lane.py`. The tool is locked by `test_dispatch_detached.py`.
- **Both PowerShell hosts.** A green suite on one proves one interpreter. `$env:PARALLAX_PS_HOST` reaches the other; PowerShell 7 is at `C:\Program Files\PowerShell\7\pwsh.exe`.
- **A killed, hung, or unfinished round must never read as a completed one.** Treat the class as open. This plan removes a launcher, so re-derive the property; do not assume it survived.
- **`-Prepare` is fail-closed.** `$ErrorActionPreference = 'Stop'`, `-ErrorAction Stop` on the reservation, and no receipt published if anything fails.
- **Forward slashes only** in `SKILL.md` and `references/backup-lane.md`. `test_no_backslash_paths_anywhere` and `test_backup_files_no_backslash_paths` are blanket bans covering both files. Do not narrow either: that was tried in the previous cycle and left a second gate red.
- **Two token forms.** `${CLAUDE_PLUGIN_ROOT}` in `SKILL.md`, where harness substitution is measured; `<plugin-checkout>` in `references/backup-lane.md`, which is read raw with the Read tool and where an unsubstituted `${NAME}` would expand to EMPTY.
- **Contract text inside `contract:start`/`contract:end` markers must sit WHOLE inside a single pin**, and `DECLARED_REGIONS` in `test_contract_coverage.py` moves with any region added, removed or renamed.
- **These pins must stay green** (`test_multi_model_verify.py:609-650`): five exact strings at `>= 2` across `SKILL.md`; `test_resume_pipes_the_brief_on_stdin`; and the raw pin forbidding a three-space-indented `& {`.
- **A pin that matches RAW file text needs its phrase unbroken on ONE PHYSICAL LINE**; a pin on the whitespace-normalized read does not. Both forms are in use. Check which read a pin uses before editing near it, and prefer restructuring prose to keep a pin green over editing the pin.
- **Never pipe a gate through `tail`, `head` or `Select-Object -Last`.** The pipe supplies its own exit status and hides the failure names a rerun would need. This produced two false green readings in the previous cycle.
- **Dispatch every round and gate as a tracked background command**, named with lane and round (`Sol R1 debate round`) or, with no lane, its kind (`Gate: pytest 5.1`).

---

### Task 1: Turn `-Launch` into `-Prepare`, tests first

**Files:**
- Modify: `tools/dispatch-detached.ps1`
- Test: `evals/multi-model-verify/test_dispatch_detached.py`

**Interfaces:**
- Produces: `-Prepare -DispatchDir <path> -WrapperBody <path> -ReceiptPath <path> -Round <label> [-Json]`, and `-Poll` unchanged apart from the new state.
- Consumes: nothing from other tasks.

- [ ] **Step 1: Write the failing tests**

Add to `test_dispatch_detached.py`. Keep every existing test that does not name `-Launch`; rewrite those that do.

```python
def test_prepare_starts_no_process(tmp_path):
    """-Prepare performs the transaction and creates NO child.

    The whole point of the redesign: the harness owns the process, so the
    tool must not spawn one. Proven by counting the dispatch directory's
    own artifacts rather than by watching the process table, which races.
    """
    d, wrapper, receipt = _prepared(tmp_path, SLEEPER_WRAPPER)
    assert (d / "launch.committed").exists()
    assert receipt.exists()
    assert not (d / "pid").exists(), "-Prepare must not publish a pid"
    assert not (d / "startticks").exists()
    assert not (d / "reply").exists()
    assert not (d / "exit").exists()


def test_a_prepared_but_unrun_round_is_not_started(tmp_path):
    """The new state. A receipt with no pid is never a result."""
    d, wrapper, receipt = _prepared(tmp_path, SLEEPER_WRAPPER)
    state, code = _poll(receipt, d, ROUND)
    assert state == "not-started"
    assert code == 1


def test_not_started_never_exits_zero_even_with_a_planted_reply(tmp_path):
    """A reply that appears without a pid is not a completed round.

    Same shape as the planted-reply test for `running`: the classification
    must come from the completion model, never from a file's presence.
    """
    d, wrapper, receipt = _prepared(tmp_path, SLEEPER_WRAPPER)
    (d / "reply").write_text("a reply nobody's round wrote", encoding="utf-8")
    (d / "exit").write_text("0", encoding="utf-8")
    state, code = _poll(receipt, d, ROUND)
    assert state == "not-started"
    assert code != 0


def test_the_wrapper_publishes_its_own_identity_and_then_runs(tmp_path):
    """Run a prepared wrapper the way the harness will, and watch the
    states move: not-started, then running, then reply-present."""
    d, wrapper, receipt = _prepared(tmp_path, IDENTITY_THEN_SLEEP_WRAPPER)
    assert _poll(receipt, d, ROUND) == ("not-started", 1)
    proc = _run_wrapper_in_background(d)
    try:
        _wait_for(d / "pid", timeout=20)
        assert (d / "startticks").exists(), "ticks must land with the pid"
        assert int((d / "pid").read_text()) == proc.pid
        assert _poll(receipt, d, ROUND) == ("running", 3)
    finally:
        proc.wait(timeout=60)
    assert _poll(receipt, d, ROUND) == ("reply-present", 0)


def test_no_csharp_is_compiled_anywhere_in_the_script(tmp_path):
    """The launcher is GONE, not disabled.

    Round 1 of the diff debate found the top-level Add-Type running before
    the script's own checks and outside any catch, so even -Poll depended
    on compiling launch-only C#. Deleting the launcher removes the subject.
    """
    text = TOOL_PATH.read_text(encoding="utf-8")
    for needle in ("Add-Type", "CreateProcess", "PROC_THREAD_ATTRIBUTE",
                   "GetProcessTimes", "LaunchDetached"):
        assert needle not in text, "the launcher survives: " + needle


def test_prepare_refuses_an_existing_dispatch_directory(tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    code, out = _prepare_raw(d, _wrapper(tmp_path), tmp_path / "r.json", ROUND)
    assert code == 1
    assert "BLOCKED" in out
    assert not (tmp_path / "r.json").exists(), "a refused prepare publishes no receipt"


def test_prepare_publishes_no_receipt_when_the_wrapper_cannot_be_installed(tmp_path):
    """Fail-closed after the directory exists."""
    receipt = tmp_path / "r.json"
    code, out = _prepare_raw(tmp_path / "d", tmp_path / "does-not-exist.ps1",
                             receipt, ROUND)
    assert code == 1
    assert not receipt.exists()
```

`IDENTITY_THEN_SLEEP_WRAPPER` is the wrapper shape Task 3 ships, reduced to a sleep and a fixed reply. `_run_wrapper_in_background` starts `powershell -NoProfile -File <d>/wrapper.ps1` with `subprocess.Popen` and `CREATE_NEW_CONSOLE`, matching the isolation `test_wrapper_renders_and_parses.py` already found necessary.

- [ ] **Step 2: Run them and watch them fail**

Run: `python -m pytest evals/multi-model-verify/test_dispatch_detached.py -q`
Expected: the new tests FAIL naming the missing `-Prepare` parameter; `test_no_csharp_is_compiled_anywhere_in_the_script` FAILS naming `Add-Type`.

- [ ] **Step 3: Make the change**

In `tools/dispatch-detached.ps1`:

1. Rename the `Launch` parameter set to `Prepare`; drop `-WorkingDirectory`, which only the launcher used.
2. DELETE the whole `Add-Type` block, `LaunchDetached`, the `GetProcessTimes` capture and the catch-side `taskkill`.
3. `-Prepare` performs, in order: separation and freshness checks; `New-Item -ItemType Directory -ErrorAction Stop`; copy the wrapper; create `stdin.empty`; mint the token and write `launch.committed`; write the RECEIPT last, create-new. On any failure after the directory exists, publish no receipt and exit 1.
4. Delete step 6's pid and startticks writes. The wrapper owns them now.
5. `-Poll`: after the `launch-not-ours` check and BEFORE reading `pid`, return `not-started` when no `pid` file exists.
6. Update the header's state list to thirteen and correct the exit-2 sentence per the spec: the tool promises exit 2 for the binding and internal errors IT can see, and a switch the host itself rejects never reaches the script and never produces exit 0.

- [ ] **Step 4: Run the suite on BOTH hosts**

Run, each as its own tracked background command:
`python -m pytest evals/multi-model-verify/test_dispatch_detached.py -q`
and the same with `PARALLAX_PS_HOST` set to `C:\Program Files\PowerShell\7\pwsh.exe`.
Expected: all pass on both, no skips other than any the file already declares.

- [ ] **Step 5: Prove the exit-2 narrowing by measurement, not assertion**

Run an unknown switch against the script on both hosts and record the real exit code:

```bash
powershell -NoProfile -File tools/dispatch-detached.ps1 -Reciept x; echo "exit $?"
```

Expected: non-zero, and NOT 0. Write the two observed codes into the header comment beside the narrowed sentence. If either host returns 0, STOP: that is a false-completion path and the narrowing is wrong.

- [ ] **Step 6: Commit**

```bash
git add tools/dispatch-detached.ps1 evals/multi-model-verify/test_dispatch_detached.py
git commit -m "prepare the round and let the harness run it"
```

---

### Task 2: Move the contract regions to the new mechanism

**Files:**
- Modify: `skills/multi-model-verify/references/model-prompting-notes.md`
- Modify: `evals/multi-model-verify/test_contract_coverage.py`
- Test: `evals/multi-model-verify/test_multi_model_verify.py`

**Interfaces:**
- Consumes: Task 1's `-Prepare` interface and the thirteen states.
- Produces: the region text every later task's call sites must agree with.

- [ ] **Step 1: Rewrite the three regions**

`detached-dispatch-tool` states `-Prepare`, that it starts NO process, and that the caller runs the wrapper as a tracked background command named for its lane and round.

`detached-dispatch-states` lists THIRTEEN states in `-Poll`'s check order, with `not-started` between `launch-not-ours` and `pid-unreadable`, and keeps the exit mapping and the pid-plus-start-ticks identity sentence.

`detached-dispatch-operation` replaces the launcher's kill guidance: there is no tool-owned child to kill, and abandoning a round means stopping the harness task and re-checking identity before any manual `taskkill`.

Add to the tool region, as its own sentence, the trade this design makes: a tracked task belongs to the session and probably dies with it, where a detached process would have survived.

- [ ] **Step 2: Update `DECLARED_REGIONS` and the pins**

`background-task-naming` and `back-channel-auto-mirror` are unchanged. Rebuild the three changed regions' pins in `test_multi_model_verify.py` by extracting each region's normalized body with `contract_coverage.parse_regions` on the live file rather than retyping it.

- [ ] **Step 3: Run the coverage gate**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py evals/multi-model-verify/test_multi_model_verify.py -q`
Expected: all pass, and every declared region reported locked.

- [ ] **Step 4: Prove the pins can fail**

Mutate one word inside each of the three rewritten regions, one at a time, and confirm that region's pin goes red and names the region. Restore after each.
Expected: three reds, three restorations, then green.

- [ ] **Step 5: Commit**

```bash
git add skills/multi-model-verify/references/model-prompting-notes.md evals/multi-model-verify/test_contract_coverage.py evals/multi-model-verify/test_multi_model_verify.py
git commit -m "state the tracked background contract"
```

---

### Task 3: Rewrite the two codex call sites

**Files:**
- Modify: `skills/multi-model-verify/SKILL.md`
- Test: `evals/multi-model-verify/test_multi_model_verify.py`

**Interfaces:**
- Consumes: Task 1's `-Prepare`, Task 2's region text.
- Produces: the wrapper shape Task 5 renders and stub-runs.

- [ ] **Step 1: Write the failing per-site test**

Parametrized over `("codex-fresh", "codex-resume")`, asserting that each `<!-- call:... -->` section carries, on the RAW read: the two identity lines as the wrapper's first act; `-Prepare` with all four parameters; the instruction to run the wrapper as a background command named for its lane and round; the `-Poll` command with all three parameters; and the whole exit-code sentence including `not-started`. Assert no section contains `-Launch`.

- [ ] **Step 2: Run it and watch it fail**

Expected: both parametrized cases FAIL.

- [ ] **Step 3: Rewrite both sections**

The wrapper body for round 1, forward slashes throughout, `${CLAUDE_PLUGIN_ROOT}` for the tool path:

```powershell
[System.IO.File]::WriteAllText("$PSScriptRoot/pid", "$PID", (New-Object System.Text.UTF8Encoding($false)))
[System.IO.File]::WriteAllText("$PSScriptRoot/startticks", ((Get-Process -Id $PID).StartTime.ToUniversalTime().Ticks), (New-Object System.Text.UTF8Encoding($false)))
$code = 1
$priorOutputEncoding = $OutputEncoding
try {
$OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$brief = [System.IO.File]::ReadAllText("<brief-file>", (New-Object System.Text.UTF8Encoding($false, $true)))
$bytes = [System.IO.File]::ReadAllBytes("<verified-override-file>")
$seen = ([System.BitConverter]::ToString(([System.Security.Cryptography.SHA256]::Create()).ComputeHash($bytes)) -replace '-', '').ToLower()
if ($seen -cne "<override-sha256>") { throw "the override file changed after the probe verified it" }
$override = (New-Object System.Text.UTF8Encoding($false, $true)).GetString($bytes)
$ErrorActionPreference = 'Continue'
$brief | codex exec --sandbox read-only --disable plugins --disable apps --disable memories -c mcp_servers.node_repl.enabled=false -c $override -m <canonical-model-id> -c model_reasoning_effort=<canonical-effort> --output-last-message "$PSScriptRoot/reply" - > "$PSScriptRoot/transcript" 2>&1
$code = $LASTEXITCODE
} catch { $code = 1 } finally {
$OutputEncoding = $priorOutputEncoding
[System.IO.File]::WriteAllText("$PSScriptRoot/exit", "$code", (New-Object System.Text.UTF8Encoding($false)))
}
```

The resume section is the same with `resume <SESSION_ID>` before the trailing `-`, on ONE physical line, unchanged otherwise.

Then, in both sections, the two tool calls and the run instruction between them, stated in full at each site because a global count let one site stay foreground undetected.

- [ ] **Step 4: Measure the body and keep the ceiling honest**

```bash
python -c "import io;t=io.open('skills/multi-model-verify/SKILL.md',encoding='utf-8').read();b=t.split('---',2)[2];print('chars',len(b),'est_tokens',len(b)//4)"
```

Record the number in the commit message. Do NOT raise `BODY_TOKEN_BUDGET`: the diff debate rejected that once already. If the body crosses `BODY_TOKEN_CEILING` at 6500, STOP and report rather than raising it or deleting skill text.

- [ ] **Step 5: Run the task-local oracle**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q` then `python evals/tools/skill_lint.py skills/multi-model-verify --strict` then `python evals/tools/skill_scanner.py skills`
Expected: all pass, all exit 0. Warnings are allowed; errors are not.

- [ ] **Step 6: Commit**

```bash
git add skills/multi-model-verify/SKILL.md evals/multi-model-verify/test_multi_model_verify.py
git commit -m "prepare and background both codex rounds"
```

---

### Task 4: Rewrite the three kimi call sites

**Files:**
- Modify: `skills/multi-model-verify/references/backup-lane.md`
- Test: `evals/multi-model-verify/test_backup_lane.py`

**Interfaces:**
- Consumes: Task 1's `-Prepare`, Task 2's region text.
- Produces: three wrapper bodies Task 5 renders and stub-runs.

**This file is read RAW with the Read tool and is NOT skill body**, so it carries `<plugin-checkout>`, never `${CLAUDE_PLUGIN_ROOT}`. An unsubstituted token would expand to EMPTY here.

- [ ] **Step 1: Write the failing per-site test**

Parametrized over `("kimi-dispatch", "kimi-resume", "kimi-write-probe")`, same assertions as Task 3's, plus: the reply artifact is `$PSScriptRoot/reply` with a FORWARD slash, and `[Console]::OutputEncoding` is set before the client call. Assert no section contains `-Launch` and none contains a backslash.

- [ ] **Step 2: Run it and watch it fail**

Expected: three parametrized cases FAIL.

- [ ] **Step 3: Rewrite the three sections**

Wrapper body, identity first, forward slashes, encoding line kept because this lane's reply crosses the console decode boundary:

```powershell
[System.IO.File]::WriteAllText("$PSScriptRoot/pid", "$PID", (New-Object System.Text.UTF8Encoding($false)))
[System.IO.File]::WriteAllText("$PSScriptRoot/startticks", ((Get-Process -Id $PID).StartTime.ToUniversalTime().Ticks), (New-Object System.Text.UTF8Encoding($false)))
$code = 1
try {
$b = [System.IO.File]::ReadAllText("<brief-file>", (New-Object System.Text.UTF8Encoding($false, $true)))
[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false)
$out = & "<kimi-code-binary>" <that call's flags, in the documented order> -p $b 2> $PSScriptRoot/transcript
$code = $LASTEXITCODE
[System.IO.File]::WriteAllText("$PSScriptRoot/reply", ($out -join "`n"), (New-Object System.Text.UTF8Encoding($false)))
} catch { $code = 1 } finally {
[System.IO.File]::WriteAllText("$PSScriptRoot/exit", "$code", (New-Object System.Text.UTF8Encoding($false)))
}
```

`-join` CANONICALIZES rather than preserving: it joins with LF and appends no terminal newline. That is the stated contract, unchanged.

- [ ] **Step 4: Run the task-local oracle**

Run: `python -m pytest evals/multi-model-verify/test_backup_lane.py evals/multi-model-verify/test_multi_model_verify.py -q`
Expected: all pass, including both blanket backslash gates.

- [ ] **Step 5: Commit**

```bash
git add skills/multi-model-verify/references/backup-lane.md evals/multi-model-verify/test_backup_lane.py
git commit -m "prepare and background all three kimi calls"
```

---

### Task 5: Re-render, parse and stub-run every wrapper body

**Files:**
- Modify: `evals/multi-model-verify/test_wrapper_renders_and_parses.py`
- Modify: `skills/multi-model-verify/SKILL.md` (marker placement only, if Task 3 moved a fence)

- [ ] **Step 1: Extend the existing tests to the identity lines**

For all five markers, assert the rendered body PARSES with `Parser::ParseFile`, and that a stub run writes `pid`, `startticks`, `reply` and `exit`, with `pid` matching the stub's own process id and `startticks` parsing as an integer.

- [ ] **Step 2: Keep the red demonstrations**

The existing `[Console]::OutputEncoding` red demonstration and the zero-match extractor self-test stay. Add one more: delete the identity lines from a scratch copy and confirm the stub run then leaves no `pid`, so `-Poll` would answer `not-started`.

- [ ] **Step 3: Run on BOTH hosts**

Expected: all pass on both, with only the file's existing declared skips.

- [ ] **Step 4: Commit**

```bash
git add evals/multi-model-verify/test_wrapper_renders_and_parses.py skills/multi-model-verify/SKILL.md
git commit -m "render and stub-run the identity-first wrappers"
```

---

### Task 6: Re-measure the probe record on both hosts

**Files:**
- Modify: `docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/wrapper-probe.md`
- Modify: `evals/multi-model-verify/test_wrapper_probe_record.py`

The existing record measured the DETACHED design. Its numbers no longer describe what ships.

- [ ] **Step 1: Add a new dated section per host, do not edit the old one**

Keep the 2026-08-31 detached sections as history, under a heading that says they measured the superseded design. Add `## host: <name> (tracked background)` sections carrying: `prepare_return_seconds`, `not_started_before_run`, `running_during_run`, `reply_present_after_run`, and the same `encoding` and `kimi_reply` fields as before.

- [ ] **Step 2: Take the measurements**

Boundary and states drive the tool with stub wrappers, never the real client. The encoding row launches the REAL `codex-fresh` wrapper once per host through a review mirror. Reuse the existing override rather than spending a fresh mirror per host.

**If any value comes out other than expected, WRITE IT AS MEASURED and stop.** `prompt_bytes_match` is expected to stay false; that is the measured trailing CRLF, not a defect.

- [ ] **Step 3: Extend the oracle**

Assert the new sections' values exactly as measured, per host, and assert the superseded sections are still present and still labelled superseded. Include a self-test that mutates a scratch copy and confirms the assertion helper raises naming the changed field.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/wrapper-probe.md evals/multi-model-verify/test_wrapper_probe_record.py
git commit -m "measure the tracked background dispatch on both hosts"
```

---

### Task 7: Correct the premise everywhere, then run every gate

**Files:**
- Modify: `CLAUDE.md`
- Modify: `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`
- Modify: `docs/superpowers/plans/2026-07-27-0150-backlog.md`

- [ ] **Step 1: Correct `CLAUDE.md`**

Its "Long-running commands" section states the kill as measured fact. Replace it with what is measured: at the 600-second ceiling the harness MOVES the command to the background and it completes (11-minute command, exit 0, output intact, 2026-08-31, Claude Code 2.1.251). The defect is that a foreground call OWNS the session: no task row, no round name, and no conversation until it ends. State the remedy as `-Prepare` plus a tracked background run, and keep the naming rule.

Do not delete the old paragraph's history silently. Say it was believed since 0.21.x and never re-measured.

- [ ] **Step 2: Mark the superseded spec**

Add a header note to the item 32 design pointing at `2026-08-31-tracked-background-dispatch-design.md` and saying the launch half is superseded and why. Leave the rest, which still describes the shipped completion model.

- [ ] **Step 3: Correct item 32's closure in the backlog**

It is still DONE, and the reason changes: the blocking is what was removed, and the visibility is what was kept. Record that the kill premise did not reproduce, with the measurement.

- [ ] **Step 4: Run the five local gates on the default host**

Run as one tracked background command, no pipes:

```bash
python evals/tools/skill_lint.py skills/multi-model-verify --strict && python evals/tools/skill_scanner.py skills && python evals/tools/check_exact_line_oracles.py && python evals/tools/run_trigger_evals.py && python -m pytest evals -q
```

Expected: exit 0, with the pytest counts reported in full.

- [ ] **Step 5: Run the full suite under PowerShell 7**

Expected: exit 0, counts reported. A count that differs from the 5.1 run by anything other than declared skips is a finding.

- [ ] **Step 6: Run the behavioural evals**

Expected: record any red case BY NAME. `diff-mode-spec-fidelity` is a known open question with a named confound; do not treat it as this plan's regression without evidence.

- [ ] **Step 7: Commit**

```bash
git add CLAUDE.md docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md docs/superpowers/plans/2026-07-27-0150-backlog.md
git commit -m "correct the ceiling premise everywhere it was recorded"
```

---

## After the tasks

The diff debate runs on the whole branch, base `8af6ae0`. The version bump comes AFTER it, not here: `plugin update` keys only on the version string, and a number cached before the debate rewrites the tree installs nothing afterwards.
