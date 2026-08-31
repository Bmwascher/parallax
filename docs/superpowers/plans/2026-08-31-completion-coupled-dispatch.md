# Completion-Coupled Round Dispatch Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> superpowers:subagent-driven-development to implement this plan
> task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** A review round is dispatched as a harness-tracked background
command whose wrapper classifies its own outcome as its final act and
exits with that classification, so a killed, hung or unfinished round can
never read as a completed one.

**Architecture:** The tool stops launching processes. `-Prepare` builds
the round's directory as one fail-closed transaction and prints the exact
command line the caller dispatches as a named background task. The wrapper
the tool installs takes an execution claim as its first act, relocates to
the reviewed tree terminatingly, runs the lane's client, then calls
`-Classify` in-process and exits with its status. Success is therefore
carried by the exit code of the one harness task the caller dispatched -
not by files a later reader finds on disk.

**Tech Stack:** Windows PowerShell 5.1 and PowerShell 7, pytest,
Claude Code harness background commands.

**Spec:** This plan implements Option D from
`docs/superpowers/plans/rounds/2026-08-31-dispatch-options-poll/POLL-RESULT.md`,
argued against
`docs/superpowers/specs/2026-08-31-dispatch-invariants.md` and
`docs/superpowers/specs/2026-08-31-dispatch-options-costing.md`. Read the
poll result first: it is why this plan builds D and not the C that
document recommends.

## Global Constraints

- **Tests first, always.** The tool's behaviour is locked by
  `evals/multi-model-verify/`. Change the test, watch it fail, then change
  the tool. This is the repo rule and it is not optional here.
- **Windows PowerShell 5.1 compatible, ASCII only** in every `.ps1` file.
- **Both hosts.** Every PowerShell-facing test module runs under 5.1 and
  under 7. A green suite on one host proves one interpreter.
- **No `$ErrorActionPreference = 'Stop'` around a native client call.**
  codex writes a benign warning to stderr at startup and `Stop` promotes
  it to a terminating error.
- **Contract regions.** Text inside `contract:start` / `contract:end`
  markers must sit whole inside a single pin in
  `evals/multi-model-verify/`, and `DECLARED_REGIONS` in
  `test_contract_coverage.py` must list every region. Adding, renaming or
  removing a region means editing that list in the same task.
- **A pin can go red without a word changing.** Some pins match raw file
  text and need their phrase unbroken on one physical line. Check which
  read a pin uses before editing near it, and prefer restructuring prose
  to keep an existing pin green.
- **Never `git add -A` while a subagent is working.** Stage explicit
  paths.
- **Dispatch every long command as a named harness background command**,
  named for its lane and round, or for its kind when it has no lane.
- **The plugin version is bumped AFTER the diff debate**, not during the
  build.

---

## The design, stated once

### What the tool becomes

`tools/dispatch-detached.ps1` is renamed to `tools/dispatch-round.ps1`.
The old name describes a mechanism the owner has forbidden, and a contract
must describe the mechanism that actually holds.

Two modes replace the old two:

```
Prepare:  -Prepare -DispatchDir <path> -WrapperBody <path>
          -ReceiptPath <path> -Round <label> -WorkingDirectory <path>
          -DispatchHost <pwsh|powershell> -PriorStateFile <path>
          (-WorkdirEvidence <literal> | -NoWorkdirEvidence) [-Json]

Classify: -Classify -DispatchDir <path> -ReceiptPath <path>
          -ExpectedRound <label> [-Json]
```

**`-Poll` is deleted outright.** A second, post-hoc path to a verdict is
the class this cycle keeps reproducing. The only authoritative answer is
the exit code of the harness task the caller dispatched.

### The receipt

A JSON object holding exactly eight fields, all present, all non-null, no
extras:

| field | type | meaning |
|---|---|---|
| `dispatchDir` | non-empty string | the resolved dispatch directory |
| `token` | non-empty string | minted per preparation |
| `round` | non-empty string | the lane-and-round label |
| `workingDirectory` | non-empty string | resolved reviewed tree |
| `dispatchHost` | non-empty string | resolved full path to the host |
| `priorStateSha256` | 64 lowercase hex | the sealed evidence boundary |
| `workdirEvidence` | non-empty string | literal to find in the transcript, or exactly `none` |
| `schema` | the integer `2` | so a version-1 receipt cannot be read as this one |

`startTicks` is gone with the liveness model.

Any deviation - wrong top-level type, a missing field, an empty string
field, a wrong JSON type, an unknown extra field - is the same
`no-receipt` outcome. Folded deliberately: nothing branches differently on
any of them.

### The wrapper the tool composes

The lane supplies ONLY its client invocation, which must set `$code` and
must write nothing to stdout. `-Prepare` wraps it:

```powershell
# PROLOGUE, written by the tool
$ErrorActionPreference = 'Stop'
[System.IO.File]::Open("$PSScriptRoot/claim", 'CreateNew', 'Write', 'None').Close()
Set-Location -LiteralPath '<workingDirectory>' -ErrorAction Stop
$code = 1
$ErrorActionPreference = 'Continue'

# ---- lane body, verbatim ----

# EPILOGUE, written by the tool
[System.IO.File]::WriteAllText("$PSScriptRoot/exit", "$code", (New-Object System.Text.UTF8Encoding($false)))
& '<tool-path>' -Classify -DispatchDir '<dispatchDir>' -ReceiptPath '<receiptPath>' -ExpectedRound '<round>'
exit $LASTEXITCODE
```

Four things this ordering buys, each of them a finding from the poll:

1. **The claim is create-new and it is the first act.** A second run of the
   same prepared wrapper dies before it can touch anything.
2. **The relocation is terminating.** A missing reviewed tree fails the
   wrapper instead of continuing from whatever directory the harness had.
3. **The wrapper's exit code IS the classification.** The harness trailer
   and the outcome cannot disagree, which is R9.
4. **Classification cannot outlive the process.** If the wrapper is
   suspended, hangs in teardown, or is killed after writing `exit`, it
   never reaches `exit $LASTEXITCODE`, so the harness task does not report
   a successful completion. This is the exact hole Option C left open.

### The states `-Classify` computes

In this fixed order, stopping at the first match:

1. receipt absent, unreadable, or failing the schema -> `no-receipt`
2. receipt's `dispatchDir` or `round` is not the pair supplied
   independently -> `receipt-not-expected`
3. no `claim` file in the dispatch directory -> `no-claim`
4. `workingDirectory` missing, unresolvable, or not a filesystem
   container -> `cwd-unreadable`
5. no `exit` file -> `no-exit-file`
6. `exit` unreadable or not a plain integer -> `exit-unreadable`
7. `exit` non-zero -> `exit-nonzero`
8. `workdirEvidence` is not `none` and the transcript does not contain it
   -> `workdir-mismatch`
9. no `reply` file -> `no-reply`
10. `reply` is empty -> `reply-empty`
11. otherwise -> `reply-present`

Eleven states. Exit codes: **0 is `reply-present` and nothing else; 2 is a
parameter-binding failure or an internal execution error; 1 is every other
state**, with the state name on stdout. There is no exit 3, because
`running` cannot exist: the classifier runs only after the client has
returned.

`workdir-mismatch` sits before the reply states on purpose. A round that
read the wrong tree is a worse failure than a missing reply, and a
transcript that was never written must not fall through to a reply check.

### What the caller does

`-Prepare` prints, on success, the two things the caller needs and nothing
it has to compose itself:

- `command`: the full dispatch command line, naming the resolved host
  explicitly with `-NoProfile -NonInteractive -File`.
- `taskName`: the recommended background-task name, built from `-Round`.

The caller dispatches `command` as a harness background command named
`taskName`, and then STOPS. When the completion notification for that
exact task id arrives, the caller reads the harness output file: its
trailer carries the authoritative exit code and its last line carries the
state name.

**Stated limit, not hidden:** the caller reads a harness-produced trailer
whose format is measured on Claude Code 2.1.251 and pinned by no version
guarantee. Nothing in this repo parses it mechanically - a person or the
session reads it - and the state name is available independently on the
wrapper's own stdout. Do not build a script on the trailer's shape.

### Why the client's output cannot forge the outcome

The lane body sends the client's stdout and stderr to
`$PSScriptRoot/transcript`, never to the wrapper's own stdout. The
wrapper's stdout therefore carries exactly one line, written by the
classifier. This matters because a transcript is prompt-steerable: a brief
carrying delimiter-shaped payload has already been measured putting a
second `session id:` line into a codex transcript. The exit code is the
part a client cannot reach at all, which is why it, not the text, is
authoritative.

---

## File structure

| File | Responsibility |
|---|---|
| `tools/dispatch-round.ps1` (renamed) | `-Prepare` and `-Classify` only |
| `tools/dispatch-detached.ps1` | deleted |
| `tools/read-codex-round-evidence.ps1` | gains `-SealedPriorStateSha256` |
| `evals/multi-model-verify/test_dispatch_round.py` (renamed) | the tool's contract |
| `evals/multi-model-verify/test_contract_coverage.py` | `DECLARED_REGIONS` |
| `evals/multi-model-verify/test_multi_model_verify.py` | call-site pins |
| `skills/multi-model-verify/SKILL.md` | two call sites |
| `skills/multi-model-verify/references/backup-lane.md` | two call sites |
| `skills/multi-model-verify/references/model-prompting-notes.md` | four contract regions |
| `skills/multi-model-verify/references/fallbacks.md` | the bookmark rule |
| `CLAUDE.md` | the dispatch digest |

---

## Task 1: Rename the tool and its test module, unchanged in behaviour

Do the rename alone, so every later diff is about behaviour.

**Files:**
- Rename: `tools/dispatch-detached.ps1` -> `tools/dispatch-round.ps1`
- Rename: `evals/multi-model-verify/test_dispatch_detached.py` ->
  `evals/multi-model-verify/test_dispatch_round.py`
- Modify: every reference to the old path

**Interfaces:**
- Consumes: nothing.
- Produces: the path `tools/dispatch-round.ps1`, used by every later task.

- [ ] **Step 1: Find every reference before moving anything**

```bash
grep -rn "dispatch-detached" --include=*.md --include=*.py --include=*.ps1 --include=*.yml .
```

Record the full list. It must include `CLAUDE.md`,
`skills/multi-model-verify/SKILL.md`,
`skills/multi-model-verify/references/backup-lane.md`,
`skills/multi-model-verify/references/model-prompting-notes.md`, and the
test modules. Do not proceed on a shorter list without saying why.

- [ ] **Step 2: Move both files with git**

```bash
git mv tools/dispatch-detached.ps1 tools/dispatch-round.ps1
git mv evals/multi-model-verify/test_dispatch_detached.py evals/multi-model-verify/test_dispatch_round.py
```

- [ ] **Step 3: Update every reference found in Step 1**

Replace `dispatch-detached.ps1` with `dispatch-round.ps1` and
`test_dispatch_detached.py` with `test_dispatch_round.py` at every site.
Leave the four contract region ids alone for now; Task 8 renames them.

- [ ] **Step 4: Prove no reference survives**

```bash
grep -rn "dispatch-detached" --include=*.md --include=*.py --include=*.ps1 --include=*.yml .
```

Expected: no output, except inside `docs/superpowers/plans/rounds/` and
`docs/superpowers/specs/`, which are historical records and must NOT be
rewritten.

- [ ] **Step 5: Run the suite**

```bash
python -m pytest evals -q
```

Expected: the same pass count as before the rename, zero FAILED.

- [ ] **Step 6: Commit**

```bash
git add tools evals skills CLAUDE.md
git commit -m "rename the dispatch tool: it no longer detaches"
```

---

## Task 2: Delete `-Launch` and `-Poll`, add `-Prepare`

**Files:**
- Modify: `tools/dispatch-round.ps1`
- Test: `evals/multi-model-verify/test_dispatch_round.py`

**Interfaces:**
- Consumes: `tools/dispatch-round.ps1` from Task 1.
- Produces: `-Prepare` with the eight-field receipt, and the two output
  fields `command` and `taskName`. Task 3 consumes the receipt schema;
  Task 4 consumes the wrapper the prepare installs.

- [ ] **Step 1: Write the failing tests**

Add to `test_dispatch_round.py`. These replace, not join, the
`-Launch`/`-Poll` tests, which this task deletes.

```python
def test_prepare_writes_the_eight_field_receipt_last(tmp_path):
    d = tmp_path / "d"
    receipt = tmp_path / "r.json"
    body = tmp_path / "body.ps1"
    body.write_text("$code = 0\n", encoding="ascii")
    prior = tmp_path / "prior.json"
    prior.write_text('{"kind":"fresh","knownRollouts":[]}', encoding="ascii")
    cwd = tmp_path / "tree"
    cwd.mkdir()
    out = run_tool([
        "-Prepare", "-DispatchDir", str(d), "-WrapperBody", str(body),
        "-ReceiptPath", str(receipt), "-Round", "Sol R1",
        "-WorkingDirectory", str(cwd), "-DispatchHost", "powershell",
        "-PriorStateFile", str(prior), "-NoWorkdirEvidence", "-Json"])
    assert out.returncode == 0, out.stdout
    got = json.loads(receipt.read_text(encoding="utf-8"))
    assert set(got) == {
        "dispatchDir", "token", "round", "workingDirectory",
        "dispatchHost", "priorStateSha256", "workdirEvidence", "schema"}
    assert got["schema"] == 2
    assert got["round"] == "Sol R1"
    assert got["workdirEvidence"] == "none"
    assert len(got["priorStateSha256"]) == 64


def test_prepare_refuses_an_existing_dispatch_directory(tmp_path):
    d = tmp_path / "d"
    d.mkdir()
    out = prepare_default(tmp_path, dispatch_dir=d)
    assert out.returncode == 1
    assert "dispatch directory already exists" in out.stdout


def test_prepare_refuses_a_receipt_inside_the_dispatch_directory(tmp_path):
    d = tmp_path / "d"
    out = prepare_default(tmp_path, dispatch_dir=d, receipt=d / "r.json")
    assert out.returncode == 1
    assert not d.exists()


def test_prepare_emits_a_command_naming_the_resolved_host(tmp_path):
    out = prepare_default(tmp_path, json_mode=True)
    got = json.loads(out.stdout)
    assert got["command"].endswith(
        "-NoProfile -NonInteractive -File \"%s\"" % got["wrapper"])
    assert got["command"].lower().startswith('"')
    assert got["taskName"] == "Sol R1 debate round"


def test_prepare_refuses_an_unresolvable_host(tmp_path):
    out = prepare_default(tmp_path, host="notashell")
    assert out.returncode == 2


def test_launch_and_poll_are_gone(tmp_path):
    for mode in ("-Launch", "-Poll"):
        out = run_tool([mode])
        assert out.returncode == 2
```

- [ ] **Step 2: Run them and watch them fail**

```bash
python -m pytest evals/multi-model-verify/test_dispatch_round.py -q
```

Expected: FAIL. `-Prepare` is not a parameter.

- [ ] **Step 3: Implement `-Prepare`**

Delete the `-Launch` and `-Poll` parameter sets, the `Add-Type` launcher
block, `HandleListLauncher`, `PARALLAX_DISPATCH_HOLD_BEFORE_PUBLISH`, and
`PARALLAX_DISPATCH_POLL_STARTTIME_FAULT`. None of them can exist once no
process is started here.

`-Prepare`, in order, under `$ErrorActionPreference = 'Stop'`:

1. Resolve `-ReceiptPath`, `-DispatchDir`, `-WorkingDirectory`. BLOCK if
   the receipt path is equal to or inside the dispatch directory, if the
   receipt path exists, or if the working directory is not an existing
   filesystem container. All before anything is created.
2. Resolve `-DispatchHost` to a full path with `Get-Command`. Exactly
   `pwsh` or `powershell` are accepted; anything else, or a name that does
   not resolve, exits 2.
3. Read `-PriorStateFile` as raw bytes and compute its SHA256.
4. Reserve the dispatch directory with `New-Item -ItemType Directory
   -ErrorAction Stop` and NO `-Force`.
5. Compose `wrapper.ps1` into the directory: prologue, `-WrapperBody`
   verbatim, epilogue. Task 4 builds the composition; for this task write
   the body through unchanged so the test above passes.
6. Write the receipt LAST, with create-new semantics.
7. Print `command`, `taskName`, `wrapper`, `dispatchDir`, `round`.

A failure at any step leaves the reserved directory in place and no
receipt. That is the shape of a handled failure, not evidence of one.

- [ ] **Step 4: Run the tests**

```bash
python -m pytest evals/multi-model-verify/test_dispatch_round.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/dispatch-round.ps1 evals/multi-model-verify/test_dispatch_round.py
git commit -m "replace launch and poll with a fail-closed prepare"
```

---

## Task 3: `-Classify`, its eleven states and its exit map

**Files:**
- Modify: `tools/dispatch-round.ps1`
- Test: `evals/multi-model-verify/test_dispatch_round.py`

**Interfaces:**
- Consumes: the eight-field receipt from Task 2.
- Produces: `-Classify -DispatchDir <d> -ReceiptPath <r> -ExpectedRound
  <label>`, exit 0 only on `reply-present`. Task 4's epilogue calls it.

- [ ] **Step 1: Write the failing tests, one per state**

```python
STATES = [
    ("no-receipt", 1), ("receipt-not-expected", 1), ("no-claim", 1),
    ("cwd-unreadable", 1), ("no-exit-file", 1), ("exit-unreadable", 1),
    ("exit-nonzero", 1), ("workdir-mismatch", 1), ("no-reply", 1),
    ("reply-empty", 1), ("reply-present", 0),
]


@pytest.mark.parametrize("state,code", STATES)
def test_each_state_and_its_exit_code(tmp_path, state, code):
    d = build_dispatch_for_state(tmp_path, state)
    out = classify(d)
    assert out.stdout.strip().endswith(state), out.stdout
    assert out.returncode == code


def test_only_reply_present_exits_zero(tmp_path):
    zero = [s for s, c in STATES if c == 0]
    assert zero == ["reply-present"]


def test_state_order_is_first_match_wins(tmp_path):
    # A directory broken in two ways reports the EARLIER state.
    d = build_dispatch_for_state(tmp_path, "no-claim")
    (d / "exit").write_text("7", encoding="ascii")
    out = classify(d)
    assert out.stdout.strip().endswith("no-claim")


def test_workdir_mismatch_beats_a_missing_reply(tmp_path):
    d = build_dispatch_with_workdir_evidence(tmp_path, evidence="C:\\mirror")
    (d / "transcript").write_text("workdir: C:\\somewhere-else", encoding="utf-8")
    (d / "exit").write_text("0", encoding="ascii")
    # no reply file at all
    out = classify(d)
    assert out.stdout.strip().endswith("workdir-mismatch")
    assert out.returncode == 1


def test_a_missing_transcript_is_workdir_mismatch_not_a_reply_state(tmp_path):
    d = build_dispatch_with_workdir_evidence(tmp_path, evidence="C:\\mirror")
    (d / "exit").write_text("0", encoding="ascii")
    (d / "reply").write_text("a verdict", encoding="utf-8")
    out = classify(d)
    assert out.stdout.strip().endswith("workdir-mismatch")


def test_none_skips_the_workdir_check_only_on_the_exact_literal(tmp_path):
    d = build_dispatch_with_workdir_evidence(tmp_path, evidence="none")
    (d / "exit").write_text("0", encoding="ascii")
    (d / "reply").write_text("a verdict", encoding="utf-8")
    out = classify(d)
    assert out.returncode == 0


def test_a_schema_one_receipt_is_no_receipt(tmp_path):
    d, r = build_dispatch(tmp_path)
    r.write_text(json.dumps({
        "dispatchDir": str(d), "token": "t", "round": "Sol R1",
        "startTicks": "1"}), encoding="utf-8")
    out = classify(d, receipt=r)
    assert out.stdout.strip().endswith("no-receipt")


def test_an_unknown_argument_is_refused_not_absorbed(tmp_path):
    d = build_dispatch_for_state(tmp_path, "reply-present")
    out = classify(d, extra=["-Jsoon"])
    assert out.returncode == 2
    assert "-Jsoon" in out.stdout
```

That last test is invariant F1 and it is written so the typo accompanies a
VALID mode. The shipped test supplied a typo with no valid mode, so its
own mode check returned 2 and the real case was never exercised.

- [ ] **Step 2: Run them and watch them fail**

```bash
python -m pytest evals/multi-model-verify/test_dispatch_round.py -q -k classify
```

Expected: FAIL, `-Classify` is not a parameter.

- [ ] **Step 3: Implement `-Classify`**

Compute the eleven states in the documented order, stopping at the first
match and reading nothing further. Print the state name on stdout; with
`-Json`, print an object carrying `state` and the receipt's `round` when a
receipt was read, `round` null otherwise.

Reject unknown arguments: add `[Parameter(ValueFromRemainingArguments =
$true)] $Rest` to the parameter block and exit 2, naming the first
unrecognised token, whenever it is non-empty. Do this for BOTH modes.

- [ ] **Step 4: Run the tests**

```bash
python -m pytest evals/multi-model-verify/test_dispatch_round.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/dispatch-round.ps1 evals/multi-model-verify/test_dispatch_round.py
git commit -m "add classify: eleven states, only reply-present exits zero"
```

---

## Task 4: Compose the wrapper, and prove the coupling holds

This is the task the whole plan exists for. Everything above is
preparation.

**Files:**
- Modify: `tools/dispatch-round.ps1`
- Test: `evals/multi-model-verify/test_dispatch_round.py`

**Interfaces:**
- Consumes: `-Prepare` from Task 2, `-Classify` from Task 3.
- Produces: a `wrapper.ps1` whose exit code is the classification.

- [ ] **Step 1: Write the failing tests**

```python
def test_the_wrapper_exit_code_is_the_classification(tmp_path):
    # A lane body that succeeds and writes a reply.
    d = prepare_and_run(tmp_path, body='''
$code = 0
[System.IO.File]::WriteAllText("$PSScriptRoot/reply", "a verdict")
''')
    assert d.returncode == 0


def test_a_failed_client_makes_the_wrapper_exit_nonzero(tmp_path):
    d = prepare_and_run(tmp_path, body="$code = 1\n")
    assert d.returncode == 1
    assert "exit-nonzero" in d.stdout


def test_the_claim_is_created_before_the_lane_body_runs(tmp_path):
    d = prepare_and_run(tmp_path, body='''
$code = 0
if (-not (Test-Path "$PSScriptRoot/claim")) { throw "no claim yet" }
[System.IO.File]::WriteAllText("$PSScriptRoot/reply", "ok")
''')
    assert d.returncode == 0


def test_a_second_run_of_the_same_wrapper_fails_and_writes_nothing(tmp_path):
    first = prepare_and_run(tmp_path, body=OK_BODY)
    assert first.returncode == 0
    before = snapshot(first.dispatch_dir)
    second = run_wrapper(first.wrapper)
    assert second.returncode != 0
    assert snapshot(first.dispatch_dir) == before


def test_two_concurrent_first_runs_leave_exactly_one_winner(tmp_path):
    p = prepare(tmp_path, body=SLOW_OK_BODY)
    a, b = run_wrapper_concurrently(p.wrapper, p.wrapper)
    codes = sorted([a.returncode, b.returncode])
    assert codes[0] == 0
    assert codes[1] != 0


def test_a_missing_working_directory_fails_the_wrapper(tmp_path):
    p = prepare(tmp_path, body=OK_BODY)
    shutil.rmtree(p.working_directory)
    out = run_wrapper(p.wrapper)
    assert out.returncode != 0
    assert not (p.dispatch_dir / "reply").exists()


def test_a_wrapper_killed_after_publishing_exit_and_reply_does_not_exit_zero(tmp_path):
    # The Option C hole, made a test.
    p = prepare(tmp_path, body=HOLD_AFTER_PUBLISH_BODY)
    proc = start_wrapper(p.wrapper)
    wait_for(p.dispatch_dir / "exit")
    wait_for(p.dispatch_dir / "reply")
    assert (p.dispatch_dir / "exit").read_text().strip() == "0"
    assert (p.dispatch_dir / "reply").read_text().strip() != ""
    kill_tree(proc.pid)
    assert proc.wait() != 0


def test_the_wrapper_stdout_carries_only_the_classifier_line(tmp_path):
    d = prepare_and_run(tmp_path, body='''
$code = 0
Write-Output "this must not reach the harness"
[System.IO.File]::WriteAllText("$PSScriptRoot/reply", "ok")
''')
    # The lane body's own stdout is a lane defect, not a tool one, but the
    # tool must not ADD any line of its own.
    assert d.stdout.strip().splitlines()[-1].endswith("reply-present")
```

The seventh test is the one that separates D from C. Under Option C's
classifier the same directory reads `reply-present` at exit 0. Under D the
process never reaches its `exit` statement, so the task it belongs to
cannot report success.

`HOLD_AFTER_PUBLISH_BODY` writes `exit` and `reply`, then blocks on a
sentinel file so the kill lands in the interval Sol named. Build it as a
deterministic barrier, not a sleep: a millisecond race in a different
costume is what the previous cycle shipped.

Note also that `exit` is written by the EPILOGUE, so the body must publish
`reply` and then hold; the epilogue's `exit` write happens when the body
returns. Structure the barrier accordingly and say in a comment which
statement the kill is landing between.

- [ ] **Step 2: Run them and watch them fail**

```bash
python -m pytest evals/multi-model-verify/test_dispatch_round.py -q -k wrapper
```

- [ ] **Step 3: Implement the composition**

`-Prepare` writes `wrapper.ps1` as prologue + body + epilogue, exactly as
in the design section above. Single-quote every interpolated path in the
generated text and double any embedded single quote, so a path containing
one cannot break the generated script.

Verify, do not assume, that `& '<tool>.ps1'` calling `exit N` sets
`$LASTEXITCODE` to N on both hosts. If it does not, the epilogue captures
the classifier's code another way and the plan's design section is
corrected in the same commit.

- [ ] **Step 4: Run the tests on both hosts**

```bash
python -m pytest evals/multi-model-verify/test_dispatch_round.py -q
```

Then set `$env:PARALLAX_PS_HOST` to the other host and run it again. Both
must pass.

- [ ] **Step 5: Commit**

```bash
git add tools/dispatch-round.ps1 evals/multi-model-verify/test_dispatch_round.py
git commit -m "couple the outcome to the wrapper's own exit code"
```

---

## Task 5: Seal the evidence boundary into the receipt

**Files:**
- Modify: `tools/read-codex-round-evidence.ps1`
- Test: `evals/multi-model-verify/test_codex_round_evidence.py`

**Interfaces:**
- Consumes: `priorStateSha256` written by Task 2.
- Produces: `-SealedPriorStateSha256 <hex>` on the binder.

- [ ] **Step 1: Write the failing tests**

```python
def test_the_binder_refuses_a_prior_state_the_receipt_did_not_seal(tmp_path):
    out = bind(prior_state=OTHER_STATE, sealed="00" * 32)
    assert out.returncode == 1
    assert "sealed" in out.stdout


def test_the_binder_accepts_the_sealed_prior_state(tmp_path):
    digest = sha256_of(PRIOR_STATE_BYTES)
    out = bind(prior_state=PRIOR_STATE, sealed=digest)
    assert out.returncode == 0


def test_the_seal_is_optional_only_where_no_receipt_exists(tmp_path):
    # Omitting it is still allowed for lanes with no prepared dispatch,
    # but omitting it does NOT read as a satisfied seal.
    out = bind(prior_state=PRIOR_STATE)
    got = json.loads(out.stdout)
    assert got["sealed"] == "not-checked"
```

The third test is the point: an unmade check must never look like a
passed one.

- [ ] **Step 2: Run them and watch them fail**

- [ ] **Step 3: Implement `-SealedPriorStateSha256`**

When supplied, hash the raw bytes of `-PriorState` and compare
case-insensitively. A mismatch is exit 1 with reason `sealed-state-
mismatch`. When omitted, report `sealed: "not-checked"` in the JSON.

- [ ] **Step 4: Run the tests**

- [ ] **Step 5: Commit**

```bash
git add tools/read-codex-round-evidence.ps1 evals/multi-model-verify/test_codex_round_evidence.py
git commit -m "make captured-before-dispatch enforceable by sealing the digest"
```

---

## Task 6: Fix the bookmark chaining rule, in all three documents

This is a SHIPPED cross-lane defect and it is independent of the tool.

**Files:**
- Modify: `skills/multi-model-verify/SKILL.md:284`
- Modify: `skills/multi-model-verify/references/fallbacks.md:119`
- Modify: `skills/multi-model-verify/references/backup-lane.md` (the
  matching statement in its binder section)
- Test: `evals/multi-model-verify/test_multi_model_verify.py`

**Interfaces:**
- Consumes: nothing.
- Produces: no code interface; a corrected documented rule.

- [ ] **Step 1: Write the failing pins**

```python
def test_the_bookmark_is_captured_per_dispatch_not_chained(body_skill):
    assert "captured immediately before EVERY dispatch" in body_skill
    assert "never inherited from the last clean round" in body_skill


def test_fallbacks_states_why_chaining_breaks(body_fallbacks):
    assert "a failed binding emits no `nextState`" in body_fallbacks
    assert "advances the client's append-only rollout" in body_fallbacks


def test_the_backup_lane_carries_the_same_rule(body_backup_lane):
    assert "captured immediately before EVERY dispatch" in body_backup_lane
```

- [ ] **Step 2: Run them and watch them fail**

- [ ] **Step 3: Correct the rule at all three sites**

The rule to write: the prior state is captured immediately before EVERY
dispatch and is never inherited from the last clean round. A round that
was voided, refused, or failed its binding emits no `nextState` at all,
and yet it has already advanced the client's append-only rollout. Chaining
from the last clean `nextState` therefore leaves the bookmark behind and
breaks every later round in that session.

Do not deduplicate the three sites into one. That duplication is what
caught a call site left in the foreground.

- [ ] **Step 4: Run the tests and the lint**

```bash
python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q
python evals/tools/skill_lint.py skills/multi-model-verify --strict
```

- [ ] **Step 5: Commit**

```bash
git add skills evals
git commit -m "capture the bookmark per dispatch, in both lanes"
```

---

## Task 7: Rewrite the four call sites

**Files:**
- Modify: `skills/multi-model-verify/SKILL.md` (round 1 and resume)
- Modify: `skills/multi-model-verify/references/backup-lane.md` (round 1
  and resume)
- Test: `evals/multi-model-verify/test_multi_model_verify.py`

**Interfaces:**
- Consumes: `-Prepare`'s printed `command` and `taskName` from Task 2.
- Produces: the operational shape each lane follows.

- [ ] **Step 1: Write the failing pins**

```python
def test_no_call_site_still_names_poll_or_exit_three(body_skill, body_backup_lane):
    for body in (body_skill, body_backup_lane):
        assert "-Poll" not in body
        assert "3 means `running`" not in body


def test_both_lanes_dispatch_the_printed_command_as_a_named_task(body_skill, body_backup_lane):
    for body in (body_skill, body_backup_lane):
        assert body.count("dispatch it as a harness background command") >= 1
        assert "the `taskName` the tool printed" in body


def test_both_lanes_read_the_exit_code_not_the_directory(body_skill, body_backup_lane):
    for body in (body_skill, body_backup_lane):
        assert "the exit code of that exact task is the result" in body
        assert "never re-read the dispatch directory for a verdict" in body


def test_both_lanes_name_the_host_explicitly(body_skill, body_backup_lane):
    for body in (body_skill, body_backup_lane):
        assert "-DispatchHost" in body
```

- [ ] **Step 2: Run them and watch them fail**

- [ ] **Step 3: Rewrite each call site**

Each of the four keeps its COMPLETE operational shape independently. The
new shape is: compose the brief, write the lane body to a file, run
`-Prepare`, dispatch the printed `command` as a harness background command
under the printed `taskName`, and STOP. On the completion notification for
that exact task, read the harness output file: the trailer's exit code is
the result, `0` meaning `reply-present` and nothing else, and the last
stdout line names the state. Then run the lane's round-evidence binder,
passing `-SealedPriorStateSha256` from the receipt. Only a clean binding
makes `reply-present` a review result.

State plainly at each site: never re-read the dispatch directory to
decide a verdict. It is diagnostic only.

- [ ] **Step 4: Run the tests and the lint**

```bash
python -m pytest evals/multi-model-verify -q
python evals/tools/skill_lint.py skills/multi-model-verify --strict
```

The lint's token budget will still warn. Task 9 addresses it. It must not
have gone UP.

- [ ] **Step 5: Commit**

```bash
git add skills evals
git commit -m "rewrite all four call sites for completion-coupled dispatch"
```

---

## Task 8: Rewrite the four contract regions

**Files:**
- Modify: `skills/multi-model-verify/references/model-prompting-notes.md`
- Modify: `evals/multi-model-verify/test_contract_coverage.py`
- Modify: `evals/multi-model-verify/test_multi_model_verify.py`

**Interfaces:**
- Consumes: the design settled in Tasks 2, 3 and 4.
- Produces: four renamed, re-pinned regions.

- [ ] **Step 1: Rename the region ids and update `DECLARED_REGIONS`**

`detached-dispatch-tool` -> `round-dispatch-tool`
`detached-dispatch-states` -> `round-dispatch-states`
`detached-dispatch-operation` -> `round-dispatch-operation`
`background-task-naming` keeps its name.

Edit `DECLARED_REGIONS` in `test_contract_coverage.py` in the SAME commit.
That list is what makes a deleted region visible.

- [ ] **Step 2: Rewrite each region's text**

- `round-dispatch-tool`: the preparation is one transaction in one place;
  no lane writes its own dispatch; a lane supplies only its client
  invocation and its working directory; the tool composes the claim, the
  relocation and the classifying epilogue around it.
- `round-dispatch-states`: the eleven states in order, the exit map, and
  the sentence that carries the whole design - **the classification is the
  wrapper's own exit code, so a wrapper that does not reach its final
  statement cannot report success, whatever its directory holds.**
- `round-dispatch-operation`: there is no poll. The caller waits for the
  harness notification for that exact task. A round with no notification
  is UNFINISHED, never successful; recovery is a fresh `-Prepare` with a
  fresh evidence boundary, never a re-run of the same wrapper, which the
  claim refuses. To abandon a round, kill the harness task. Never poll
  with `ps -p` from Git Bash, which cannot see Windows pids.
- `background-task-naming`: unchanged rule, plus the new fact that
  `-Prepare` now PRINTS the name, so the convention has a source even
  though nothing enforces its use.

- [ ] **Step 3: Write one pin per region and prove coverage**

Each region's text must sit whole inside a single pin. A region too long
for one pin is two regions.

```bash
python -m pytest evals/multi-model-verify/test_contract_coverage.py -q
```

Expected: PASS, with no region reported unlocked.

- [ ] **Step 4: Run the full suite**

```bash
python -m pytest evals -q
```

- [ ] **Step 5: Commit**

```bash
git add skills evals
git commit -m "rewrite the dispatch contract regions for the coupled design"
```

---

## Task 9: Bring the skill body back under budget

**Files:**
- Modify: `skills/multi-model-verify/SKILL.md`
- Create: `skills/multi-model-verify/references/preflight-mirror.md`
- Modify: `evals/multi-model-verify/test_multi_model_verify.py`

**Interfaces:**
- Consumes: the call sites from Task 7.
- Produces: a body under the 6500 ceiling with both call sites intact.

- [ ] **Step 1: Measure first**

```bash
python evals/tools/skill_lint.py skills/multi-model-verify --strict
```

Record the number. Do not raise the ceiling.

- [ ] **Step 2: Move the mirror-building detail out**

The preflight section holds roughly 1976 tokens and most of it is
mirror-building detail read only when the enumeration actually finds
something. Move that to `references/preflight-mirror.md`. Contract regions
living in the moved text move WITH their declarations and their pins, in
this same commit.

Move HISTORICAL and RATIONALE material. Keep the complete operational
shape at BOTH call sites. Do not globally deduplicate the sites.

- [ ] **Step 3: Re-measure**

```bash
python evals/tools/skill_lint.py skills/multi-model-verify --strict
python -m pytest evals/multi-model-verify/test_contract_coverage.py -q
```

Expected: the body is under 6500 and the coverage test is green. If a
measured, materially trimmed body still will not fit, STOP and report -
raising the ceiling is a separate, explicitly pinned decision, not this
task's to take.

- [ ] **Step 4: Commit**

```bash
git add skills evals
git commit -m "move mirror-building detail out of the skill body"
```

---

## Task 10: Measure the benefit, on both hosts

Nothing above proves the thing the cycle is for. The withdrawn plan
measured preparation time and poll states and never once checked that a
task row appeared.

**Files:**
- Create:
  `docs/superpowers/plans/rounds/2026-08-31-completion-coupled-dispatch/benefit-measurement.md`

**Interfaces:**
- Consumes: the whole build.
- Produces: a measurement record, or a named failure.

- [ ] **Step 1: Prepare a real round against the review mirror**

Use a genuine reviewer round, not a stub. A stub cannot show that the
conversation stays open.

- [ ] **Step 2: Record each of these, as observed, not as expected**

1. A named task row appeared, and its name is the `taskName` the tool
   printed.
2. The session answered a user message WHILE the round was running.
3. A completion notification arrived, carrying the task id and an output
   file path.
4. The output file's trailer exit code equals the classifier's state
   mapping.
5. No console window appeared at any point. Watch the screen; this is
   invariant D5 and it has only ever been measured for the redesign's own
   spawning, never for a harness-run wrapper.
6. Repeat 1 to 5 with `-DispatchHost pwsh` and with `-DispatchHost
   powershell`.

- [ ] **Step 3: Write the record**

Every line is MEASURED or it is not in the record. If something could not
be observed, write that it could not be observed. An unmade measurement
and a clean one must never look alike.

- [ ] **Step 4: Commit**

```bash
git add docs/superpowers/plans/rounds/2026-08-31-completion-coupled-dispatch
git commit -m "measure the dispatch benefit on both hosts"
```

---

## Task 11: Update `CLAUDE.md` and run every gate

**Files:**
- Modify: `CLAUDE.md`
- Test: the five CI gates plus the two opt-in suites this branch touches

**Interfaces:**
- Consumes: everything above.
- Produces: a branch ready for whole-branch review.

- [ ] **Step 1: Correct the two false statements in `CLAUDE.md`**

The "Long-running commands" section opens with a rule justified by a kill
that does not happen. Rewrite it around what IS true: a foreground call
owns the session, so the user cannot see the round or talk to the agent.
Say that the 600-second ceiling does NOT kill - measured 2026-08-31 on
Claude Code 2.1.251, an 11-minute foreground command was moved to the
background by the harness and completed - and that the reason to dispatch
in the background is visibility, not survival.

Replace the `dispatch-detached.ps1` paragraph with the new tool, its two
modes, and the sentence that matters: the wrapper's exit code is the
classification.

- [ ] **Step 2: Run all five CI gates**

```bash
python evals/tools/skill_lint.py skills/multi-model-verify --strict
python evals/tools/skill_scanner.py skills
python evals/tools/check_exact_line_oracles.py
python evals/tools/run_trigger_evals.py
python -m pytest evals -q
```

Every one must be green. Do NOT read any of them through `tail`, `head`
or `Select-Object -Last`: a gate read through a pipe reports the pipe's
status, and that has already hidden a red run on a merge commit in this
repo.

- [ ] **Step 3: Run the full suite on the OTHER host**

Set `$env:PARALLAX_PS_HOST` and run `python -m pytest evals -q` again. A
green suite on one host proves one interpreter.

- [ ] **Step 4: Run the drift state machine**

`tools/check-drift.ps1` is not touched by this plan, but Task 11 edits
`CLAUDE.md`, which its snapshot reads.

```bash
powershell -NoProfile -File evals/tools/drift_statemachine_tests.ps1
```

- [ ] **Step 5: Run the behavioural evals**

This branch changes skill and prompt text, so they are in scope.

```bash
python evals/tools/run_behavioral_evals.py --changed
```

Every skip is printed by name. Read the names; a skip that should have run
is a finding.

- [ ] **Step 6: Commit**

```bash
git add CLAUDE.md
git commit -m "correct the dispatch rules CLAUDE.md still states as measured"
```

---

## What this plan deliberately does NOT do

- **It does not bump the plugin version.** The bump goes after the diff
  debate. A version cached mid-branch copies nothing afterwards, however
  much the tree moves, and this repo has shipped that mistake twice.
- **It does not revive any part of the liveness model.** No pid, no start
  ticks, no recycled-pid handling, no `Add-Type`, no per-host process
  APIs. All three reviewer lanes agreed that deleting it is right.
- **It does not bound a hung round.** Kimi named the absence of a
  hung-round policy and it is real: a hung harness task is classified
  correctly forever and nothing says how long it may sit. It is left open
  deliberately, because the answer is an operator convention and nobody
  has costed it. File it rather than invent it here.
- **It does not measure what happens to a round when the session ends.**
  Survival was dropped as a requirement by the owner. Any future design
  that reintroduces a detached worker to buy survivability is reopening a
  settled decision.

## Self-review, run against the poll's nine required carry-overs

| Required | Task |
|---|---|
| 1. Build Option D, not C | 2, 3, 4 |
| 2. State and test the write ordering | 4 (all seven wrapper tests) |
| 3. Test the benefit directly | 10 |
| 4. Name the interpreter and flags | 2 (`-DispatchHost`), 7 |
| 5. Bind the cwd and check `workdir:` | 2 (receipt), 3 (`workdir-mismatch`) |
| 6. Rewrite the exit-3 contract at both call sites | 7, 8 |
| 7. State the recovery rule | 8 (`round-dispatch-operation`) |
| 8. Reject unknown arguments | 3 |
| 9. Probe the no-window behaviour | 10, step 2, item 5 |

Two further carry-overs, from the invariants rather than the poll: the
evidence boundary is sealed in Task 5 (E4), and the cross-lane bookmark
rule is fixed in Task 6 (E2).
