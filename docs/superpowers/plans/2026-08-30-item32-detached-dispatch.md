# Items 32 and 33 Implementation Plan: detached dispatch, and the mirror prompt that always had one answer

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every long client call the skill documents incapable of blocking the caller past the 600-second tool ceiling, so a review round can no longer be killed with its quota spent and no reply written; and stop the preflight asking a question whose answer has never once differed.

**Architecture:** A new shipped tool, `tools/dispatch-detached.ps1`, performs the whole launch as ONE fail-closed transaction: check that the receipt path is fresh and outside the dispatch directory, reserve the directory, install the wrapper, start the process, record the pid and its start ticks, write the internal launch-commit marker, and publish the EXTERNAL RECEIPT last of all. It also computes the completion state. Each documented call keeps its client invocation verbatim inside a lane-specific wrapper body and calls the tool to launch it.

**Tech Stack:** PowerShell 5.1 and PowerShell 7, Markdown skill contracts under `skills/multi-model-verify/`, pytest pins under `evals/multi-model-verify/`.

**Spec:** `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`

**Revision 5, 2026-08-30.** Four Sol rounds on session `01a055c5-935e-76e3-ad1d-83721bc67d79` plus a two-lane poll. Round 4 closed nothing and named why: the launch is a four-step transaction that existed as five copied snippets, with the rule pinned somewhere else. Sol and Fable were polled separately on the fork and both chose a shipped tool. **The user approved reversing their design-phase choice on 2026-08-30**; the design's settled question 2 is reopened and the record says so plainly.

## What the two lanes conditioned their answer on, and what this plan does with it

- **Sol: the tool does NOT make the failure impossible.** A hard kill between `Start-Process` returning and the receipt being published still leaves a live untracked process. So the contract names that state rather than eliminating it. Since revision 13 the state is `NO RECEIPT`, not `LAUNCH UNKNOWN`: the receipt is the transaction's last act, so an interrupted launch has none. `LAUNCH UNKNOWN` now means something narrower - a valid receipt whose marker has since disappeared. This plan takes Sol's weaker claim over Fable's stronger one because Fable stated it had not re-verified the round 4 finding and took the relay.
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
  - `-Launch -DispatchDir <path> -WrapperBody <path> -ReceiptPath <path> -Round <label> [-WorkingDirectory <path>] [-Json]`
  - `-Poll -Receipt <path> -ExpectedDispatchDir <path> -ExpectedRound <label> [-Json]`
- **`-Poll` names a RECEIPT, never a directory.** Round 6 asked for a launch token and revision 6 supplied one; round 7 showed a token stored inside the artifact it authenticates is not evidence of anything, because the caller can read it out of the old directory it is already looking at and hand it straight back. So the receipt is written OUTSIDE the dispatch directory, at a path `-Launch` refuses if it already exists, LAST of all and only on success. **`-Launch` ENFORCES the separation rather than describing it:** it resolves both paths and BLOCKS before anything is created if the receipt path is equal to, or inside, the dispatch directory. Round 9's finding - the guarantee was claimed in prose while the parameter accepted any path, so a receipt written inside the directory it authenticates would have quietly restored the round 7 defect. A refused launch writes no receipt, so there is nothing for a caller to substitute from the directory it was refused.
- The receipt is JSON: the dispatch directory, the minted token, the `-Round` label, and the launched process's start-time ticks. `-Poll` reads it, and its own JSON echoes `round` back. That is the visibility half: a poll answering for a different round says so in the field the caller records.
- **`-Poll` is told, INDEPENDENTLY of the receipt, which directory and which round it is polling for**, and compares both before it opens anything. A mismatch is `receipt-not-expected`. Round 8's finding: the receipt alone binds a receipt to its own directory, and nothing bound it to the act the caller believes it is performing, so handing an earlier attempt's receipt to a later poll returned the earlier attempt's `reply-present`. The label alone is not enough - `Sol R1` is reusable across a retry of the same round - which is why the expected DIRECTORY is required as well. The caller already knows both values: it passed them to `-Launch`.
- **The residual that remains, stated rather than claimed closed.** A caller that supplies an earlier attempt's receipt AND that attempt's directory AND its label gets that attempt's result, because at that point every value the caller supplied describes the earlier act. Nothing inside the tool can distinguish a caller that is confused about all three. The controls are a FRESH round-numbered receipt path per round and a `-Launch` that refuses an existing one. This is NARROWED, exactly like the interrupted launch that leaves NO RECEIPT, and the contract says so in the same words.
- `-Launch` prints, and `-Poll` returns, JSON with `state` drawn from exactly TWELVE names: `no-receipt`, `receipt-not-expected`, `launch-unknown`, `launch-not-ours`, `pid-unreadable`, `running`, `no-exit-file`, `exit-unreadable`, `exit-nonzero`, `no-reply`, `reply-empty`, `reply-present`.
- `no-receipt` deliberately FOLDS three inputs - the receipt path is absent, or unreadable, or fails the schema below. They are folded because their disposition is identical and no branch follows any of them. It is a decision, not an omission.
- **The receipt schema is stated, because "not this tool's JSON" is not a boundary an implementer can apply.** Round 8's finding. A valid receipt is a JSON object with exactly these four fields, all present: `dispatchDir`, a non-empty string; `token`, a non-empty string; `round`, a non-empty string; `startTicks`, a value that parses as a 64-bit integer. A top-level value that is not a JSON object, a missing field, an empty string where a string is required, a `startTicks` that does not parse, or ANY field holding the wrong JSON type is `no-receipt`. Unknown extra fields are also `no-receipt`, so a future field cannot be silently ignored by an old tool.
- **`-Poll`'s exit codes map onto the states, and the mapping is part of the contract.** Round 8's finding: importing the mirror's three meanings without mapping twelve states onto them left the implementer to invent it.
  - **0 for `reply-present` and NOTHING ELSE.**
  - **3 for `running`**, meaning UNFINISHED.
  - 1 for every other state, each a transport failure per fallbacks.md, with the state name on stdout.
  - 2 ONLY for a failure to bind the parameters or an internal execution error. Reading the receipt's CONTENT is never exit 2: an absent, unreadable or schema-failing receipt is `no-receipt` at exit 1, which round 9 found the previous wording contradicting by listing "an unreadable argument" under 2.
- **Why `running` is not 0.** Revision 8 gave it 0 and wrote "exit 0 is not a result" beside it. Round 9's finding: that is the exact shape this whole cycle exists to remove - a safety rule in prose next to a command instead of a mechanism inside it. A caller branching on exit status alone would take the success path while the wrapper was still writing the reply, and Task 8 deliberately builds that arrangement. A distinct code makes the unfinished round unrepresentable as success without reading anything.
- `-Launch`'s exit codes match `new-review-mirror.ps1:17-18`: 0 launched and committed, 1 blocked with the reason on stdout, 2 script or environment error. `-Poll` extends that set with 3 and narrows 2 as above; say so in the header, because a reader who assumes the three-code convention is exactly the reader this mapping protects.

- [ ] **Step 1: Write the failing tests**

`evals/multi-model-verify/test_dispatch_detached.py`, driving the REAL script against stub payloads. Every case runs on whichever host `PARALLAX_PS_HOST` names, so CI covers both.

Cases, each named for what it protects:

- `test_a_taken_directory_blocks_and_starts_nothing` — pre-create the directory; expect exit 1, the reason on stdout, and no process started. The reservation is `New-Item -ItemType Directory` with `-ErrorAction Stop` and no `-Force`; round 4 found that without `-ErrorAction Stop` the error is non-terminating and the following statements run with no valid path.
- `test_an_existing_receipt_blocks_before_the_directory_is_reserved` — **round 13's finding: the requirement was in step 1 and in no test.** Create the receipt path first, then launch. Expect exit 1 and expect the dispatch directory NOT to exist afterwards, which is what proves the check ran before the reservation rather than after it.
- `test_a_receipt_that_appears_during_the_launch_fails_closed` — use the hold barrier: wait for `.started`, create the receipt path while the tool waits, then release. The create-new write at step 7 must FAIL, the `catch` must kill the tree, and the exit must be 1. An overwrite here would publish a receipt over one this launch did not write, which is the round 7 defect arriving through a race instead of a caller.
- `test_a_receipt_path_inside_the_dispatch_directory_is_blocked` — the receipt path equal to the dispatch directory, and inside it at one and two levels down. Expect exit 1 and expect NO dispatch directory to have been created, because the check runs first. Round 9's finding: the separation was a claim with no mechanism, and a receipt inside the directory it authenticates is the round 7 defect returning.
- `test_force_is_not_accepted_in_any_argument_order` — assert the script source contains no `-Force` on the reservation, checked by parsing the command rather than by string order. Round 4 found the previous pin only forbade the exact token order `-ItemType Directory -Force`.
- `test_a_committed_launch_publishes_pid_then_marker_then_receipt` — assert ALL THREE positions, by content rather than by timestamp: `pid` and `startticks` exist before `launch.committed`, and the RECEIPT is written after both. Round 10's finding: four places called the commit marker the last artifact while the executable sequence published the receipt after it, and the test name carried the wrong claim into the suite.
- `test_a_failure_after_start_kills_the_tree_and_blocks` — inject a failure between start and commit; expect exit 1 and the started process gone. This is the state Sol said cannot be eliminated, so the tool must at least not leave it silently.
- `test_poll_reports_launch_unknown_when_the_marker_is_gone` — launch to success, then DELETE `launch.committed` and poll with that launch's own receipt and its matching expected pair. Expect `launch-unknown`. Not running, not failed, not complete. **This is the only way the state is reachable**, and round 13's rewrite of the hard-kill case is why: the marker is written before the receipt, so a valid receipt proves the marker once existed, and a directory that never got one has no receipt to poll with either. The previous wording said "a reserved directory with no `launch.committed`", which describes an input that stops at `no-receipt` instead.
- `test_a_refused_launch_writes_no_receipt_and_cannot_be_polled` — **the round 6 regression, rewritten because round 7 showed the previous version was impossible to run.** It said to poll with "the token the second launch would have used", and a refused launch mints nothing. Instead: run a stub launch to completion against receipt `R1`, so the directory holds a real commit, pid, `exit` of `0` and a reply. Launch AGAIN on the same directory naming a FRESH receipt path `R2`. Take the refusal, assert `R2` was never created, then poll `-Receipt R2`. Expect `no-receipt`, never `reply-present`.
- `test_a_stale_receipt_is_refused_against_the_expected_act` — **round 8's finding.** Poll the finished directory with `R1` while `-ExpectedDispatchDir` and `-ExpectedRound` name the SECOND round's directory and label. Expect `receipt-not-expected`. Then run the same case with only the label differing and again with only the directory differing, because a retry can reuse a label and a mistake can reuse a directory; both must be refused on their own.
- `test_the_expected_act_is_checked_before_any_directory_is_opened` — **round 9's finding, and it replaces an assertion that could not be made.** The previous version said to "assert no artifact of the first round was read", which names no observation. This one is observable: point a MISMATCHED receipt at a `dispatchDir` that does not exist, and at a second one that exists but holds no `launch.committed`. Expect `receipt-not-expected` in both. An implementation that checks the commit artifact first returns `launch-unknown` and fails here, which is what makes the ORDER testable rather than merely written down.
- `test_a_stale_receipt_matching_every_expected_value_still_answers_for_its_own_round` — supply `R1` with R1's own directory and label. It DOES report `reply-present`, because at that point every value the caller supplied describes the earlier act. Assert the returned `round` is R1's label. This is the residual the contract admits, and the test exists so the residual is a measured behaviour rather than a hope.
- `test_an_unreadable_receipt_is_no_receipt_at_exit_one` — **round 10's finding.** The classification was stated in prose and no case produced it, so an implementation returning exit 2 for an unreadable receipt satisfied every other case. Pass a DIRECTORY as `-Receipt`: it is a deterministic unreadable-file condition on both hosts and needs no permission juggling. Expect `no-receipt` and exit 1, never exit 2, because reading the receipt's content is never an invocation error.
- `test_a_receipt_failing_the_schema_is_no_receipt` — one case per way to fail it: a top-level value that is not an object (an array, a bare string, a number); each of the four fields missing in turn; an empty string in each of the three string fields; a `startTicks` that does not parse; **each of the four fields in turn holding the wrong JSON type**, not one representative case; and an unknown extra field. Expect `no-receipt` every time. Round 9's finding: the previous list said "a wrong JSON type" once, so an implementer type-checking three fields and not the fourth passed it.
- `test_every_state_maps_to_its_documented_exit_code` — one case per state name. `reply-present` exits 0; `running` exits 3; every other state exits 1 with the state name on stdout; a malformed argument exits 2. Round 8's finding: the exit codes were imported from `new-review-mirror.ps1:17-18` and never mapped, so an implementer had to invent them. Round 9's finding: revision 8's mapping gave `running` a 0 and defended it with a sentence, which is the defect class this cycle exists to remove.
- `test_a_running_round_can_never_exit_zero` — named separately from the mapping test and kept separate on purpose. Build the Task 8 arrangement in miniature: a stub that writes a NONEMPTY reply and then sleeps. Poll while it sleeps. Expect exit 3 and `state` of `running`, and assert the reply's content is not returned. A caller that branches on exit status alone must not be able to reach that reply.
- `test_poll_rejects_a_receipt_whose_token_is_not_the_committed_one` — a receipt pointing at a directory whose `launch.committed` holds a different token; expect `launch-not-ours`.
- `test_poll_reports_pid_unreadable_when_the_pid_is_missing_or_malformed` — a committed directory whose `pid` is absent, empty, or not an integer. Round 6 found the poll jumping from commit existence straight to "pid alive", so such an input fell through to the terminal branches and could reach `reply-present`.
- `test_a_recycled_pid_is_not_read_as_running` — the receipt's start-time ticks do not match the live process now holding that pid. Expect the poll to treat our process as GONE and continue to the terminal artifacts, never `running`. Round 7's finding: pid identity was numeric only. `tools/kimi-lane-lock.ps1:219-236` already solves this exact problem in this repo - `Get-Liveness` compares `StartTime.ToUniversalTime().Ticks` and returns LIVE, DEAD or UNMEASURABLE - so copy that shape rather than inventing one.
- `test_an_unmeasurable_start_time_is_pid_unreadable` — the live-pid branch cannot read a start time. Expect `pid-unreadable`, which is neither `running` nor terminal. `kimi-lane-lock.ps1` keeps UNMEASURABLE distinct from both for the same reason: an unmade measurement must never look like a made one.
- `test_poll_reports_running_while_the_pid_is_alive` — and asserts that NO other file is read in that branch, because a reply being written is not a reply.
- `test_poll_distinguishes_every_terminal_state` — one case per remaining state name above. **Each fixture is built by running a stub launch to a real successful completion and then altering ONLY the artifact that case is about.** Round 6's finding: fixtures assembled from planted files can describe an arrangement `-Launch` could never produce, which proves nothing about the production transition.
- `test_the_documented_outer_command_works_on_this_host` — run the EXACT command string the skill documents, not the script directly. Round 6 found the tests exercising the script under `PARALLAX_PS_HOST` while the documented outer command was never run at all. Round 7's finding: that command must be HERE, not referred forward to Task 3, because Task 1's implementer sees only Task 1. It is, verbatim:

  ```powershell
  & (Get-Process -Id $PID).Path -NoProfile -File ${CLAUDE_PLUGIN_ROOT}/tools/dispatch-detached.ps1 -Launch -DispatchDir <dispatch-dir> -WrapperBody <wrapper-file> -ReceiptPath <receipt-file> -Round <label> -Json
  ```

  ```powershell
  & (Get-Process -Id $PID).Path -NoProfile -File ${CLAUDE_PLUGIN_ROOT}/tools/dispatch-detached.ps1 -Poll -Receipt <receipt-file> -ExpectedDispatchDir <dispatch-dir> -ExpectedRound <label> -Json
  ```

  Task 3 documents these same two lines in the skill. If they ever disagree, this task's test is the one that fails, which is the point.
- `test_a_hard_kill_between_start_and_publication_is_never_success` — kill the TOOL itself in that window rather than injecting a handled failure, and confirm the poll reports **`no-receipt`**, never success. The injected-failure case exercises the `catch`; this one exercises the case the `catch` cannot reach, which is the one the contract admits is irreducible.

  **Round 13's finding: this test previously expected `launch-unknown`, and could never have passed.** Once the receipt became the last artifact published, a kill before publication leaves no receipt at all, so the poll stops at check 1 and never reaches the marker check. The state is right in spirit and was wrong in name. What changes with it is where the DANGER lives: `no-receipt` now carries the irreducible case, and the contract must say that `no-receipt` is not evidence that nothing started.

  **This test needs a deterministic barrier, or it is the millisecond race again in a different costume.** Round 7's finding. Step 3 below adds one env-gated seam for it: with `PARALLAX_DISPATCH_HOLD_BEFORE_PUBLISH` set to a path, `-Launch` creates `<path>.started` after `Start-Process` returns and then waits, bounded at sixty seconds, for `<path>.release` to appear before it writes `pid`. The test waits for `.started`, kills the tool, and never writes `.release`. Unset, the seam does not exist. Like the two seams in `tools/new-kimi-lane-home.ps1`, it is BUILDER CONTRACT rather than test scaffolding, it is reachable by any parent process that sets the variable, no shipped caller sets it, and it can only make a launch FAIL - it can never turn a failing launch into a successful one. Say all of that in the script header, in those terms.

- [ ] **Step 2: Run them to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_dispatch_detached.py -q`
Expected: every test FAILS or ERRORS because the script does not exist. Read the output and confirm the failures name missing behaviour, not a broken test harness.

- [ ] **Step 3: Write the script**

`tools/dispatch-detached.ps1`, ASCII only, Windows PowerShell 5.1 compatible, following the header-comment style of `tools/new-review-mirror.ps1:1-30`: what it is for, what it refuses, and its exit codes.

`-Launch`, in order, under `$ErrorActionPreference = 'Stop'`:

1. Resolve `-ReceiptPath` and `-DispatchDir` to full paths and BLOCK if the receipt path is equal to the dispatch directory or sits inside it, and BLOCK if the receipt path already exists. Both checks run before anything is created, so a refusal leaves no directory behind either.
2. `$d = (New-Item -ItemType Directory -Path $DispatchDir -ErrorAction Stop).FullName`. Failure here is BLOCKED and nothing has started.
3. Copy `$WrapperBody` to `$d\wrapper.ps1`; create the empty `$d\stdin.empty`.
4. `$proc = Start-Process -FilePath (Get-Process -Id $PID).Path -ArgumentList @("-NoProfile", "-NonInteractive", "-File", "`"$d\wrapper.ps1`"") -NoNewWindow -PassThru -ErrorAction Stop -RedirectStandardInput "$d\stdin.empty" -RedirectStandardOutput "$d\launch.out" -RedirectStandardError "$d\launch.err"`, plus `-WorkingDirectory` when given.
5. If `PARALLAX_DISPATCH_HOLD_BEFORE_PUBLISH` is set, create `<value>.started` and wait, bounded at sixty seconds, for `<value>.release`; on timeout, fail through the same `catch` as any other failure. This is the barrier the hard-kill test needs and it exists nowhere else.
6. Write `$d\pid` and `$d\startticks` (the launched process's `StartTime.ToUniversalTime().Ticks`), then write `$d\launch.committed` with the minted token as its content.
7. Write the RECEIPT last of all, and only now: JSON holding `dispatchDir`, `token`, `round`, `startTicks`. It is created with create-new semantics; its path was already checked for freshness and for separation in step 1, so this step can only fail on a race, and a race here fails through the same `catch`.
8. Wrap steps 4 to 7 in a `catch` that runs `taskkill /PID $proc.Id /T /F` when `$proc` exists, then exits 1. Never leave a started process unrecorded and unreported.

The token is minted with `[System.Guid]::NewGuid()`. It binds a receipt to the directory it names. It is NOT a secret from the caller and the contract must not describe it as one: it also sits in `launch.committed`, so a caller determined to launder an old directory can read it there. What the receipt adds is that a REFUSED launch produces no receipt at all.

`-Poll` computes the state in this order, and the order is the contract:

1. Receipt absent, unreadable, or failing the schema above → `no-receipt`. Stop. Nothing else is read, and no directory is opened.
2. The receipt's `dispatchDir` is not `-ExpectedDispatchDir`, compared as full resolved paths, or its `round` is not `-ExpectedRound`, compared exactly → `receipt-not-expected`. Stop. Still nothing is opened. This receipt describes a different act from the one the caller is performing.
3. The receipt's `dispatchDir` has no `launch.committed` → `launch-unknown`. Stop.
4. `launch.committed` does not hold the receipt's token → `launch-not-ours`. Stop. That directory belongs to a different launch and none of its artifacts describe this one.
5. `pid` missing, unreadable, or not an integer → `pid-unreadable`. Stop. A committed launch always wrote one, so its absence means the directory is not in a state this tool produced.
6. Liveness, computed exactly as `tools/kimi-lane-lock.ps1:219-236` computes it: no such process → DEAD, continue to the terminal states; the process exists but its start time cannot be read → `pid-unreadable`, stop; the process exists and its ticks differ from the receipt's → DEAD, because the pid was recycled, continue to the terminal states; the process exists and the ticks match → `running`, stop, and NOTHING ELSE IS READ, because a reply being written is not a reply.
7. No `exit` file → `no-exit-file`. Unreadable or not a plain integer → `exit-unreadable`. Non-zero → `exit-nonzero`.
8. Zero and no `reply` → `no-reply`. Zero and `reply` is empty → `reply-empty`. Zero and `reply` has content → `reply-present`.

Every `-Poll` result carries the receipt's `round` label back in its JSON, whatever the state.

`reply-present` is NOT a review result on its own. The caller still runs the lane's round-evidence binder, and only a clean binding makes it one. Say that in the script header so nobody reads the state name as a verdict.

- [ ] **Step 4: TASK-LOCAL ORACLE**

Run: `python -m pytest evals/multi-model-verify/test_dispatch_detached.py -q` on BOTH hosts.
Expected: all PASS on both. Then run one negative check by hand: delete the `catch` written in step 8 of the script below - step 6 writes the pid and the start ticks, and round 8 caught this reference naming the wrong step, then revision 9 renumbered them again when the receipt-path check became step 1 - confirm `test_a_failure_after_start_kills_the_tree_and_blocks` goes red, and restore it. A test suite that cannot fail is what this task exists to prevent.

- [ ] **Step 5: Commit**

```bash
git add tools/dispatch-detached.ps1 evals/multi-model-verify/test_dispatch_detached.py
git commit -m "add the fail-closed detached dispatch tool"
```

---

### Task 2: State the contract in the notes, declare it, pin it

Four regions. The explanation lives here because `SKILL.md` is budgeted. Measure the body with:

```bash
python -c "import io;t=io.open('skills/multi-model-verify/SKILL.md',encoding='utf-8').read();b=t.split('---',2)[2];print('chars',len(b),'est_tokens',len(b)//4)"
```

Measured 2026-08-30 at `caa7e1b`: 20983 chars, 5245 estimated tokens, against a 5250 soft budget and a 5500 hard ceiling. Task 3 step 5 re-measures with this command once the dispatch steps are rewritten, which is where the ceiling decision belongs.

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
  directory, installs the wrapper, starts the process, records the pid
  and its start ticks, writes the internal launch-commit marker, and
  publishes the EXTERNAL RECEIPT last of all; a failure at any point
  after the process starts kills the tree and BLOCKS rather than leaving
  it unrecorded. The two are not interchangeable: the marker is what
  makes the directory a committed launch, and the receipt is what makes
  the launch pollable, so the receipt is the transaction's final act. No
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
  The tool's `-Poll` mode names a RECEIPT, never a directory, and the
  ORDER of its checks is the contract. First, a receipt that is absent,
  unreadable, or not this tool's own JSON means NO RECEIPT: no directory
  is opened at all. A refused launch writes no receipt, so a caller
  cannot poll the directory it was just refused. NO RECEIPT IS NOT
  EVIDENCE THAT NOTHING STARTED. The receipt is the transaction's last
  act, so a launch interrupted at any earlier point - a hard kill
  between process creation and publication above all - leaves no receipt
  and may well have left a LIVE UNTRACKED CHILD. Shipping the
  transaction in one tool NARROWS that window; it does not remove it,
  and in its worst form no pid was written either, so the whole-tree
  kill below cannot clear it. It is never success. Second, a receipt whose
  directory or round is not the one the caller says it is polling for is
  RECEIPT NOT EXPECTED, and still nothing is opened: the receipt binds
  itself to its own directory, and only this second, independently
  supplied pair binds it to the act being performed. Third, a VALID
  receipt whose directory holds no launch-commit marker is LAUNCH
  UNKNOWN. Since the marker is written before the receipt, a receipt
  that exists proves the marker once existed, so this state means the
  marker has since gone - removed, or lost with the directory. It is
  never success, and it is a different condition from the interrupted
  launch above, which produces NO RECEIPT instead. Fourth, a commit artifact not holding the
  receipt's token is LAUNCH NOT OURS: the directory belongs to another
  launch and none of its artifacts describe this one. Fifth, a missing
  or unreadable pid under a valid commit is PID UNREADABLE, because a
  committed launch always wrote one. Sixth, liveness is PID PLUS START
  TIME, never a pid alone: a live pid whose start time cannot be read is
  PID UNREADABLE, and a live pid whose start time differs from the
  receipt's is a RECYCLED pid, which means our own process is gone. Only
  a live pid whose start time matches is RUNNING, and there NOTHING ELSE
  IS READ - a reply being written is not a reply. Only then come the
  terminal states: no exit file, an exit file unreadable or not a plain
  integer, a non-zero code, zero with no reply artifact, zero with an
  empty reply artifact, and zero with a reply artifact that has content.
  Only the last can become a review result, and it is not one by itself:
  the lane's round-evidence binder must also return clean. Every other
  state is a transport failure per fallbacks.md, except RUNNING, which
  is UNFINISHED. The receipt NARROWS misattribution and does not remove
  it either: a caller that supplies an earlier act's receipt AND that
  act's directory AND its label is truthfully told that act's result,
  because every value it supplied describes the earlier act. The
  controls for that are a fresh receipt path per round and a launch that
  refuses an existing one. EXIT ZERO MEANS REPLY PRESENT AND NOTHING
  ELSE. An unfinished round exits THREE, so a caller reading only the
  exit status cannot take a still-being-written reply for a finished
  one; a rule saying to read the state field would have been prose where
  a mechanism belongs.
  <!-- contract:end -->
```

**Region three — operation:**

```
  <!-- contract:start id=detached-dispatch-operation -->
  Each poll is BOUNDED and returns; a poll that waits indefinitely is
  the blocking form again. At THIRTY MINUTES without a terminal state,
  stop polling, report the round UNFINISHED, and ask the user whether to
  keep waiting or abandon it. Neither answer is a review result. To
  abandon a round whose pid is on disk, fell the whole tree with
  `taskkill /PID <id> /T /F`: killing the launcher alone leaves the
  client orphaned, which is what the 2026-08-11 report of this item
  observed at zero CPU growth. NO RECEIPT after an interrupted launch is
  the case that command CANNOT clear, and the two must not be run
  together in one sentence: in its dangerous form no pid was ever
  written, so there is no `<id>` to pass. Clearing that one means finding the process by another route -
  its command line, its working directory - and it is unmeasured here,
  so surface it to the user rather than claiming a remedy. Never poll
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

Add to `DECLARED_REGIONS` with a comment recording: backlog item 32; that TOOL replaced a launch that had been five copied snippets; that STATES leads with NO RECEIPT, then RECEIPT NOT EXPECTED, then LAUNCH UNKNOWN, because the cross-vendor reviewer refused the claim that a tool eliminates the irreducible interrupted launch, then refused a launch token stored inside the artifact it authenticates, then caught this very ordering stated two ways in one document, and finally caught the irreducible case sitting under the wrong state name once the receipt became the last artifact published; and that NAMING is separate because it is the only unenforced one.

- [ ] **Step 3: Write one pin per region**

Four tests beside `test_dispatch_traps_are_documented_in_the_notes`, each asserting its region's full normalized text, built by copying the region and normalizing rather than retyping. The naming pin's docstring must say it is a documentation-presence pin, not behavioural enforcement.

- [ ] **Step 4: Let the contract collector read an injected document set**

Round 6's finding: the oracle below cannot be run today. `evals/multi-model-verify/test_contract_coverage.py:611` binds `DOC_PATHS` as a module constant and both tests read that constant directly at `:737` and `:749`, so nothing can point the collector at a scratch copy. Give `collect_regions` and those two tests an optional `doc_paths` argument defaulting to `DOC_PATHS`. It adds no assertion and changes no existing one; it only makes the negative case reachable.

- [ ] **Step 5: TASK-LOCAL ORACLE**

Run: `python -m pytest evals/multi-model-verify/test_contract_coverage.py -q` and confirm `test_declared_regions_match_the_documents` and `test_every_marked_region_is_locked_by_a_pin` both pass. Then, through the argument added in step 4, point the collector at a scratch copy of the notes with ONE region's markers deleted, and confirm `test_declared_regions_match_the_documents` FAILS naming that region. Round 4 found this task's previous oracle satisfied by removing a whole region/declaration/pin triplet; round 6 found the oracle itself unrunnable.

- [ ] **Step 6: Confirm the pre-existing trap pin is untouched**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k dispatch_traps`
Expected: PASS.

- [ ] **Step 7: Commit**

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
    CODEX_CALLS = ("codex-fresh", "codex-resume")

    @pytest.mark.parametrize("call", CODEX_CALLS)
    def test_each_codex_call_is_launched_through_the_tool(self, call):
        """Per-site, not a global count.

        Round 6's finding: a global `>= 2` is satisfied by two tool
        calls under round 1 and none under resume, while the document
        still contains no `Start-Process`. Centralization would be
        proven and detachment of each site would not.

        The anchor matters separately: the three tool calls this skill
        already makes are bare relative paths (SKILL.md:94, :121, :228),
        which is backlog item 58's own cause, and a new call must not
        join that. The HOST matters too. A bare `powershell` starts the
        tool under Windows PowerShell 5.1 even from a PowerShell 7
        session, and the tool then hands its own executable to the
        wrapper, so the wrapper silently runs on a host the caller never
        chose. `(Get-Process -Id $PID).Path` is the caller's own host.
        """
        text = read(SKILL_MD)
        marker = "<!-- call:%s -->" % call
        assert text.count(marker) == 1, "exactly one section per call"
        section = text.split(marker, 1)[1].split("<!-- call:", 1)[0]
        assert (
            "& (Get-Process -Id $PID).Path -NoProfile -File"
            " ${CLAUDE_PLUGIN_ROOT}/tools/dispatch-detached.ps1 -Launch"
            " -DispatchDir <dispatch-dir> -WrapperBody <wrapper-file>"
            " -ReceiptPath <receipt-file> -Round <label>"
            " -Json") in section, "this site has no launch"
        assert (
            "& (Get-Process -Id $PID).Path -NoProfile -File"
            " ${CLAUDE_PLUGIN_ROOT}/tools/dispatch-detached.ps1 -Poll"
            " -Receipt <receipt-file>"
            " -ExpectedDispatchDir <dispatch-dir> -ExpectedRound <label>"
            " -Json") in section, "this site has no poll"
        assert "$brief | codex exec" in section, (
            "this site has no client invocation")
        assert (
            "0 means `reply-present` and nothing else; 3 means"
            " `running`, an UNFINISHED round; 1 is any other state, a"
            " transport failure with the state name on stdout; 2 is a"
            " parameter-binding failure or an internal execution"
            " error.") in section, (
            "this site does not state the WHOLE exit mapping. Round 10"
            " found the tool contract and the point of use disagreeing"
            " about exit 0, which is the only place a reader of the"
            " skill would look; round 11 found the replacement asserting"
            " two of its four clauses, so the 1 and 2 clauses could drift"
            " or vanish while this test stayed green. All four clauses"
            " are one literal on purpose")

    def test_no_codex_lane_writes_its_own_launch(self):
        """A CENTRALIZATION guard, and nothing more.

        Round 6 established what this cannot show: an absent
        `Start-Process` proves no second launch implementation exists,
        never that every call site reaches the one that does. The
        per-site test above is what proves that.
        """
        assert "Start-Process" not in read(SKILL_MD), (
            "no lane writes its own launch; the tool owns the whole"
            " transaction and a second copy is how it drifts"
        )

    def test_the_point_of_use_sends_the_reader_to_the_states(self):
        text = read(SKILL_MD)
        assert text.count("references/model-prompting-notes.md's"
                          " detached-dispatch-states") >= 2
```

- [ ] **Step 2: Run them to verify they fail**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q -k "launched_through_the_tool or writes_its_own_launch or sends_the_reader_to_the_states"`
Expected: **3 FAILED and 1 PASSED.** The two parametrized cases fail, and so does `test_the_point_of_use_sends_the_reader_to_the_states`. `test_no_codex_lane_writes_its_own_launch` ALREADY PASSES, because `Start-Process` does not appear in `SKILL.md` today - measured at 0 occurrences. Round 11's finding: expecting it to fail was impossible, and a red-then-green ritual that cannot go red teaches nothing. Note it in the commit message rather than letting a guard that was green all along read as coverage the task earned.

- [ ] **Step 3: Rewrite the round-1 step**

Open this step's content with `<!-- call:codex-fresh -->` and step 4's with `<!-- call:codex-resume -->`, so the per-site test can split the file on them. Round 6's finding: with no per-site split, two tool calls under round 1 and none under resume satisfies a global count while the resume stays foreground.

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
& (Get-Process -Id $PID).Path -NoProfile -File ${CLAUDE_PLUGIN_ROOT}/tools/dispatch-detached.ps1 -Launch -DispatchDir <dispatch-dir> -WrapperBody <wrapper-file> -ReceiptPath <receipt-file> -Round <label> -Json
```

```
   `<receipt-file>` is a FRESH path for this round, alongside the fresh
   reply and transcript paths this skill already requires; the launch
   refuses one that exists. `<label>` names the lane and the round, as in
   `Sol R1`. The poll below reads the receipt, not the directory, so a
   launch that was refused has nothing to poll:
```

```powershell
& (Get-Process -Id $PID).Path -NoProfile -File ${CLAUDE_PLUGIN_ROOT}/tools/dispatch-detached.ps1 -Poll -Receipt <receipt-file> -ExpectedDispatchDir <dispatch-dir> -ExpectedRound <label> -Json
```

`-ExpectedDispatchDir` and `-ExpectedRound` are the same two values passed to the launch, supplied again and INDEPENDENTLY of the receipt: that pair is what stops an earlier attempt's receipt answering for this one. The poll also echoes the `round` back, so record it. Its exit codes are: **0 means `reply-present` and nothing else; 3 means `running`, an UNFINISHED round; 1 is any other state, a transport failure with the state name on stdout; 2 is a parameter-binding failure or an internal execution error.** Round 10's finding: this sentence still carried revision 8's mapping, so the shipped skill would have told the reader that exit 0 covers a round still being written, while the tool said otherwise.

`(Get-Process -Id $PID).Path` is the caller's own host, not a bare `powershell`. Round 6's finding: a bare name resolves to Windows PowerShell 5.1 even from a PowerShell 7 session, and the tool hands its own executable to the wrapper, so the wrapper would run on a host nobody chose.

Keep "Both encoding lines are load-bearing on Windows PowerShell 5.1 (references/model-prompting-notes.md)." and everything from the `verified-override-dispatch` marker onward exactly as it is.

**Three details are load-bearing and a tidy breaks them.** `$priorOutputEncoding` is captured OUTSIDE the `try`, or the `finally` restores a variable never assigned on an early failure. `catch` and `finally` are ONE clause on ONE line: a `} finally {` after a closed `catch` is a parse error and the wrapper dies before codex runs. The exit write is the last line, outside every block.

- [ ] **Step 4: Rewrite the resume step identically**

Same wrapper shape, same two tool calls, under its own `<!-- call:codex-resume -->` marker. The `$brief | codex exec ... resume <SESSION_ID> -` line stays on ONE physical line and does not otherwise change.

- [ ] **Step 5: Measure the body, and raise the ceiling only if the measurement says so**

Round 6's finding: deferring this to Task 9 is circular, because the oracle below cannot pass strict lint until the ceiling permits the body this task just wrote. Round 7's finding: the command belongs here too, not behind a pointer to another task, because this task's implementer sees only this task. It is:

```bash
python -c "import io;t=io.open('skills/multi-model-verify/SKILL.md',encoding='utf-8').read();b=t.split('---',2)[2];print('chars',len(b),'est_tokens',len(b)//4)"
```


If the estimated tokens are at or under 5500, change nothing and write the measured number in the commit message. If they are over, raise `BODY_TOKEN_CEILING` in `evals/tools/skill_lint.py` to a value this measurement justifies, write the date, the number and the reason beside it per `skill_lint.py:308-326`, and add one test asserting the new value with that reason in its docstring - a raise with no test is how the next raise goes unnoticed. Never delete skill text to fit. The tool-based design SHRANK these steps, so a raise may not be needed at all.

- [ ] **Step 6: TASK-LOCAL ORACLE**

Run: `python -m pytest evals/multi-model-verify/test_multi_model_verify.py -q && python evals/tools/skill_lint.py skills/multi-model-verify --strict && python evals/tools/skill_scanner.py skills`
Expected: PASS, exit 0, including every new test and `test_the_brief_is_read_and_piped_as_utf8` and `test_resume_pipes_the_brief_on_stdin` UNAMENDED. The per-site parametrization is the oracle: it names each call, so a site left foreground fails by that site's name rather than by a count.

- [ ] **Step 7: Commit**

```bash
git add skills/multi-model-verify/SKILL.md evals/multi-model-verify/test_multi_model_verify.py evals/tools/skill_lint.py
git commit -m "dispatch both codex rounds through the tool"
```

Stage `skill_lint.py` only if step 5 raised the ceiling.

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
        "& (Get-Process -Id $PID).Path -NoProfile -File"
        " ${CLAUDE_PLUGIN_ROOT}/tools/dispatch-detached.ps1 -Launch"
        " -DispatchDir <dispatch-dir> -WrapperBody <wrapper-file>"
        " -ReceiptPath <receipt-file> -Round <label>"
        " -WorkingDirectory <review-mirror> -Json") in section, (
        "this call has no launch; a lane described as detached with no"
        " launch command is what four rounds kept finding")
    assert (
        "& (Get-Process -Id $PID).Path -NoProfile -File"
        " ${CLAUDE_PLUGIN_ROOT}/tools/dispatch-detached.ps1 -Poll"
        " -Receipt <receipt-file>"
        " -ExpectedDispatchDir <dispatch-dir> -ExpectedRound <label>"
        " -Json") in section, (
        "this call has no poll; a launch whose result is never read is"
        " a round thrown away")
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
Expected: **3 FAILED and 1 PASSED** — the three parametrized cases fail, and `test_the_backup_lane_writes_no_launch_of_its_own` ALREADY PASSES, because `Start-Process` does not appear in `backup-lane.md` today either, measured at 0 occurrences. Round 11's finding, the same one as Task 3's.

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

and the anchored `-Launch` call with `-WorkingDirectory <review-mirror>`, because this client binds a session to the directory it was created in, and the matching `-Poll` call naming the receipt that launch wrote.

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

Against a stub that writes the reply then sleeps thirty seconds. Kill the tree inside that window and poll: expect `no-exit-file`. Reserve the same directory twice, naming a fresh receipt path the second time: expect the second to BLOCK and expect that receipt path NOT to exist afterwards, then poll it and expect `no-receipt`. Let the stub exit zero with an empty reply: expect `reply-empty`.

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

**Files:** Modify the spec, `docs/superpowers/plans/2026-07-27-0150-backlog.md`, and `CLAUDE.md`; create `docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/round-record.md`. Round 7's finding: step 1 writes into that record and no earlier version of this task listed or staged it.

- [ ] **Step 1: Record what Task 3 measured**

The ceiling decision was made in Task 3 step 5, where it has to be: strict lint gates that task's own commit, so deferring the decision to here made the ordering circular. Round 6's finding. Copy the measured char count, the estimated token count, and whether `BODY_TOKEN_CEILING` was raised, into the round record. Do not re-decide it.

- [ ] **Step 2: Reconcile the spec with the plan**

**Correct the scope table's task numbers.** `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:65-71` assigns the two codex sites to Task 4 and the three kimi sites to Task 5. The plan implements them in Task 3 and Task 4, because the tool became Task 1 and pushed everything down. Round 11's finding: the reconciliation list named five things and not this one, and the convergence grep searches for stale prose rather than stale task numbers. Its oracle asserts the mapping EXACTLY, rather than only rejecting the old number. Round 12's finding: a grep for `Task 5` is satisfied by a table reading `Task 4` five times, and "read the five rows" is an instruction to a person, not a task-local oracle.

```bash
python -c "import io,re;t=io.open('docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md',encoding='utf-8').read();rows=[l for l in t.splitlines() if re.match(r'^\| [1-5] \|',l)];got=[re.search(r'Task \d+',l).group(0) for l in rows];assert got==['Task 3','Task 3','Task 4','Task 4','Task 4'],got;print('scope table ok',got)"
```

Expected: `scope table ok` and exit 0. Any other five values, or a row that lost its task number, raises and fails the step.

**Replace two more spec passages that the receipt-last ordering made false.** Round 14's finding, and both are consequences of a change three revisions earlier rather than fresh mistakes:

- `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:175-183` says the orphan half of item 32 has a documented answer because "the pid is on disk". After revision 13 that is exactly backwards for the dangerous case: an interrupted launch leaves NO RECEIPT and may leave no pid either, which is the one case `taskkill /PID <id>` cannot clear. Rewrite it to say the pid is on disk for every COMMITTED launch, and that the interrupted one is the residual the contract names and does not remedy.
- `design.md:190-194` says LIVENESS IS CHECKED FIRST. It is now checked sixth: receipt validity, expected-act identity, the marker, the token and the pid all precede it. Replace the sentence with the ordered list the plan builds.

**Replace the spec's mechanism section outright.** `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:136-148` still describes the SESSION running `Start-Process`, writing the pid file, and polling it - the design the debate rejected in favour of a shipped tool. Round 10's finding: Task 9 updated five things around that section and never replaced the section itself, and the convergence grep does not search for a session-owned launch. Replace it with the transaction this plan builds: the session writes a wrapper body and calls the tool; the tool checks the receipt path, reserves the directory, installs the wrapper, starts the process, records the pid and start ticks, writes the commit marker, and publishes the receipt; later calls poll the RECEIPT with the expected directory and round.

Also update: the state model to the tool's ordered checks, whose first three states are NO RECEIPT, then RECEIPT NOT EXPECTED, then LAUNCH UNKNOWN - round 8 caught this step saying LAUNCH UNKNOWN comes first, which was true only of revision 6, and round 9 caught the correction itself already stale, because adding RECEIPT NOT EXPECTED moved LAUNCH UNKNOWN again; the region inventory to the four that exist plus `back-channel-auto-mirror`; the encoding claim to be lane-specific, since an argument-passing lane carries no preamble; the quoting claim, since a wrapper file removes one serialization boundary and not every quoting layer; and question 2, which the user reopened and answered the other way on 2026-08-30. Say plainly that a settled decision was reversed and by whom.

- [ ] **Step 3: TASK-LOCAL ORACLE for convergence**

```bash
grep -ni "detached-dispatch-codex\|detached-dispatch-backup\|no quoting layer at all\|encoding preamble moves INSIDE the wrapper\|every wrapper\|four states\|five states\|six states\|seven states\|eight states\|nine states\|ten states\|eleven states\|not detached\|The session launches it with\|sidecar exit-code file\|LIVENESS IS CHECKED FIRST\|the pid is on disk, so a session can find\|powershell -NoProfile -File\|-Token\|-DispatchDir <dispatch-dir> -Json" docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md
```

Expected: no hits outside a passage explicitly narrating history. Round 4 found the previous grep searching for none of the terms it claimed to; round 6 found it still missing the encoding claim, which is the very claim the plan says is refuted, so the stale text would have passed.

Two of the patterns need their replacement wording stated exactly, or the reconciliation drifts again:

- The encoding claim becomes lane-specific. The codex lane's wrapper carries the `$OutputEncoding` preamble because its brief goes down a PIPE. The Kimi lane's wrapper carries none because its brief goes as an ARGUMENT, which is a different transport with a different defect, and item 51 owns that one.
- The state count is TWELVE, so every spelled count below twelve is a stale hit, and `powershell -NoProfile -File` is stale because the documented call now uses the caller's own host.
- The grep is `-i`. Round 7's finding: the spec spells `SEVEN states` in capitals at `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:194`, and a case-sensitive pattern walked straight past the one stale count the step was written to catch.

Then run a POSITIVE oracle, because a grep for stale words cannot show that the replacement arrived. It is written as one count per token, inside the mechanism section only:

```bash
sec=$(sed -n '/^### The mechanism/,/^## /p' docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md)
for t in "dispatch-detached.ps1" "-ReceiptPath" "-ExpectedDispatchDir" "-ExpectedRound" "no-receipt" "receipt-not-expected"; do printf '%s: ' "$t"; printf '%s' "$sec" | grep -c -- "$t"; printf '%s' "$sec" | grep -q -- "$t" || exit 1; done
```

Expected: every one of the six at least 1, AND exit 0. Round 14's finding: three tokens let a spec omit `-ExpectedRound` entirely and still pass, and none of them required the receipt-last consequences to appear at all. The `|| exit 1` is the whole oracle. Round 12's finding on the SECOND attempt at this same check: a loop's status is its last iteration's, so a missing first token printed `0` and the block still succeeded, which is the defect this step exists to catch, reproduced inside its own fix. Round 10's finding: every oracle in this step searched only for what should be gone, so a section deleted and never rewritten passed it. Round 11's finding on the first attempt at a fix: `grep -c "A\|B\|C"` counts LINES matching any alternative, so three lines carrying only the first token satisfied "at least three" while the other two were absent, and it was not scoped to the section at all.
- `-Token` and `-DispatchDir <dispatch-dir> -Json` are stale because the poll now names a RECEIPT.

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

State in item 32 what was NOT done: item 51 still owns the argv escaping repair; item 31 is untouched; **item 58 is untouched except that this cycle's ONE new tool call is anchored while the three existing ones at `SKILL.md:94`, `:121` and `:228` are still bare relative paths** — record that asymmetry rather than leaving it to be discovered; the resume-after-a-kill recovery is still unmeasured; and the interrupted launch that leaves NO RECEIPT, possibly with a live untracked child and no pid on disk, is narrowed, not eliminated.

- [ ] **Step 8: Commit**

```bash
git add CLAUDE.md docs/superpowers/plans/2026-07-27-0150-backlog.md docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/round-record.md
git commit -m "close items 32 and 33"
```

---

## What the debate changed

Sol session `01a055c5-935e-76e3-ad1d-83721bc67d79`, FOURTEEN review rounds plus a two-lane poll, plus one round refused by the evidence binder and discarded unread. Every finding was reproduced against the repository before acceptance and none was refuted. Two reviewer rulings reversed decisions I had already reported to the user: the Kimi lane's scope, and the whole launch mechanism.

Rounds 1 to 9 each found at least one way for one act's artifact to be read as another act's result. Rounds 10 to 14 found none, and each named the shapes it had swept for. What they found instead was oracles that could not fail and text left behind by a mechanism change - twice, an oracle written to fix the previous round's oracle.

Round 4 is where this plan stopped being a set of copied snippets: it found the launch was never centralized at all. Round 13 is the deepest single finding after that - a test that could never have passed, because moving the receipt to last in revision 10 changed which state an interrupted launch produces and nothing else was updated.

**Round 1** — a stale exit file plus a fresh reply plus a killed wrapper read as complete; the exit write sat inside the `try`; `check-drift.ps1` was excluded for a wrong reason; the backup-lane pins do not prove byte identity; a third Kimi call existed; Task 5 asserted detachment and implemented none; the wrapper-file claim overreached; mirror construction runs `git commit` with the reviewed repo's hooks live; `Start-Process` was called the only mechanism; streams were inherited; the plan contradicted itself on the timeout; two harness facts were not repo-verifiable.

**Round 2** — the staleness rule was stated, pinned and probed but never implemented; the freshness rule was unsatisfiable; five states duplicated one and omitted another; the Kimi deferral was unsound and was withdrawn; the spec's enumeration was stale; an unenforced convention shared a pin with completion safety; raw-string tests pass a wrapper that will not parse; the kill window was a millisecond race.

**Round 3** — create-new semantics were promised and not specified; the state count disagreed across three documents; the Kimi lane had wrappers but no launch and no reply artifact, so every successful call would have been discarded; extraction could select the wrong fence and a PATH stub cannot intercept an absolute binary; seven tasks could pass their own verification with their change absent.

**Round 4** — the reservation was not fail-closed; an eighth condition existed outside the state model entirely, reachable three ways; `>= N` counts bound nothing to a call site; the launch was never actually centralized; eight of ten oracles were still weak and one task had none; the spec was still stale in ways the convergence grep did not search for.

**Round 5** — the wrapper body's own quoting and the round-numbered path rule.

**Rounds 6 and 7** — the fifth false-completion path: an old completed directory answering after a refused launch. A launch token was proposed, supplied, and then refused as evidence, because a token stored inside the artifact it authenticates can be read out of that artifact by the caller. The receipt replaced it. Also: the documented call hardcoded `powershell`, silently forcing 5.1 on a PowerShell 7 session.

**Round 8** — the receipt bound itself to its own directory and nothing bound it to the act being performed; the receipt had no schema; twelve states were mapped onto three imported exit codes by nobody.

**Round 9** — `running` exited 0 with "exit 0 is not a result" written beside it, which is a rule in prose where a mechanism belongs. It exits 3 now. The receipt-outside-the-directory guarantee was claimed and unenforced.

**Rounds 10 to 12** — no new completion path. The point-of-use text carried a stale exit mapping; two tasks expected a red-then-green cycle on a guard that was already green; and two Task 9 oracles could not fail, the second being the fix for the first.

**Rounds 13 and 14** — the receipt-last ordering, applied in revision 10, had never been propagated. The hard-kill test named a state it could not reach, `LAUNCH UNKNOWN` meant two different things, and four passages plus two spec sections still described the older mechanism.

**The poll** — both lanes independently chose the shipped tool. Sol conditioned it on not claiming the failure is eliminated; Fable observed that the stub gate could not have caught the defect at all, because the launch sequence sat outside the wrapper it ran. Both required the anchored path, and both cited the three existing bare relative paths as item 58's own cause.

## After the tasks

The version bump comes AFTER the diff debate, not here. `plugin update` keys only on the version string, and a number cached before the debate rewrites the tree installs nothing afterwards.
