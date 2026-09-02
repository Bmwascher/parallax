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
the tool installs reserves BOTH the execution and its answer as its first
act, relocates to the reviewed tree terminatingly, runs the lane's client
as a child process, then calls `-Classify` and exits with its status.
Success is therefore carried by the exit code of the one harness task the
caller dispatched - not by files a later reader finds on disk.

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
          -RepoRoot <path> -SourceHead <sha> -MirrorHead <sha>
          -SourceStatusSha256 <hex> -MirrorStateSha256 <hex>
          -ExpectedMirrorPath <path>
          -DispatchHost <pwsh|powershell> -PriorStateFile <path>
          (-WorkdirEvidence <literal> | -NoWorkdirEvidence) [-Json]

Classify: -Classify -DispatchDir <path> -ReceiptPath <path>
          -ExpectedRound <label> -ExpectedReceiptSha256 <hex>
          -Redeem <nonce> [-Json]
```

`-Classify` is called by the wrapper and by nothing else.
`-ExpectedReceiptSha256` is written into the wrapper's text by `-Prepare`
and is what lets it detect a receipt edited after preparation, in any
field. `-Redeem` is minted at run time by the wrapper itself.

**`-Poll` is deleted outright.** A second, post-hoc path to a verdict is
the class this cycle keeps reproducing. The only authoritative answer is
the exit code of the harness task the caller dispatched.

### The receipt

A JSON object whose fields are exactly those below - all present, all
non-null, no extras. The table is the only place the set is written down:

| field | type | meaning |
|---|---|---|
| `dispatchDir` | non-empty string | the resolved dispatch directory |
| `token` | non-empty string | minted per preparation |
| `round` | non-empty string | the lane-and-round label |
| `workingDirectory` | non-empty string | resolved reviewed tree |
| `dispatchHost` | non-empty string | resolved full path to the host |
| `priorStateSha256` | 64 lowercase hex | the sealed evidence boundary |
| `workdirEvidence` | non-empty string | the `workdir:` header value to expect, or exactly `none` |
| `repoRoot` | non-empty string | the mirror's source repository |
| `sourceHead` | 40 lowercase hex | source identity, for `-VerifyIdentity` |
| `mirrorHead` | 40 lowercase hex | mirror identity, for `-VerifyIdentity` |
| `sourceStatusSha256` | 64 lowercase hex | source status digest, for `-VerifyIdentity` |
| `mirrorStateSha256` | 64 lowercase hex | mirror content digest, added by Task 1a |
| `expectedMirrorPath` | non-empty string | the canonical path the build recorded |
| `schema` | the integer `2` | so a version-1 receipt cannot be read as this one |

`startTicks` is gone with the liveness model.

Any deviation - wrong top-level type, a missing field, an empty string
field, a wrong JSON type, an unknown extra field - is the same
`no-receipt` outcome. Folded deliberately: nothing branches differently on
any of them.

### The wrapper the tool composes

The lane supplies ONLY its client invocation, in its own file. `-Prepare`
installs it as `body.ps1` beside the wrapper and **the wrapper runs it as
a CHILD PROCESS**, never inline:

```powershell
# WRAPPER, written entirely by the tool
$ErrorActionPreference = 'Stop'
$utf8 = New-Object System.Text.UTF8Encoding($false)
# ONE first act, two reservations, in this order. BOTH are create-new:
# WriteAllText is NOT create-new, it overwrites, so the reservation is
# opened with FileMode CreateNew and written through that handle.
[System.IO.File]::Open("$PSScriptRoot/claim", 'CreateNew', 'Write', 'None').Close()
$r = [System.IO.File]::Open("$PSScriptRoot/classification", 'CreateNew', 'Write', 'None')
try { $b = $utf8.GetBytes('reserved'); $r.Write($b, 0, $b.Length) } finally { $r.Close() }

# ONE argument set, defined once, used by BOTH verifications.
$mirrorArgs = @{
    VerifyIdentity      = $true
    RepoRoot            = '<repoRoot>'
    MirrorPath          = '<workingDirectory>'
    SourceHead          = '<sourceHead>'
    MirrorHead          = '<mirrorHead>'
    SourceStatusSha256  = '<sourceStatusSha256>'
    MirrorStateSha256   = '<mirrorStateSha256>'
    ExpectedMirrorPath  = '<expectedMirrorPath>'
}

# The tree is verified HERE, at run time, not merely at preparation.
& '<mirrorToolPath>' @mirrorArgs > "$PSScriptRoot/mirror.verify" 2>&1
if ($LASTEXITCODE -ne 0) { throw 'mirror identity failed at dispatch time' }

Set-Location -LiteralPath '<workingDirectory>' -ErrorAction Stop
$ErrorActionPreference = 'Continue'
$null | & '<hostPath>' -NoProfile -NonInteractive -File "$PSScriptRoot/body.ps1" `
    > "$PSScriptRoot/body.out" 2> "$PSScriptRoot/body.err"
$code = $LASTEXITCODE
# NOT a complete backstop, and the comment must not imply it is. If the
# resolved host binary has been deleted since preparation, the call raises
# a statement-terminating error under Continue and $LASTEXITCODE still
# holds the FIRST verification's zero - a stale 0, not $null, so this line
# does not fire. The round still cannot read as success: the body never
# ran, so there is no reply and no transcript, and classification lands on
# no-transcript or no-reply. But the exit file then records a 0 for a
# client that never launched. Conservative, and worth knowing when reading
# that file.
if ($null -eq $code) { $code = 1 }

# The tree is verified a SECOND time, after the client has finished, so a
# mutation that persisted through the round is caught. A change reverted
# inside the round is not, and no before-and-after check could catch it.
# 'Stop' is restored FIRST: see the note below, this line is load-bearing.
$ErrorActionPreference = 'Stop'
& '<mirrorToolPath>' @mirrorArgs >> "$PSScriptRoot/mirror.verify" 2>&1
if ($LASTEXITCODE -ne 0) { throw 'the mirror changed while the round ran' }

# CONSUME the reservation BEFORE any terminal artifact is published, and
# stamp it with a nonce minted HERE, at run time, that appears in no file
# -Prepare wrote.
$nonce = [System.Guid]::NewGuid().ToString('N')
[System.IO.File]::WriteAllText("$PSScriptRoot/classification", "classifying:$nonce", $utf8)
[System.IO.File]::WriteAllText("$PSScriptRoot/exit", "$code", $utf8)
# test seam: PARALLAX_DISPATCH_HOLD_AFTER_EXIT_WRITE, see below
& '<toolPath>' -Classify -DispatchDir '<dispatchDir>' -ReceiptPath '<receiptPath>' `
    -ExpectedRound '<round>' -ExpectedReceiptSha256 '<receiptSha256>' `
    -Redeem $nonce
exit $LASTEXITCODE
```

**The child's three streams are owned, not inherited, and the form above
is MEASURED rather than assumed.** Measured 2026-08-31, sentinel piped
into the wrapper, on both hosts:

| form | child sees |
|---|---|
| `-InputFormat None` | **`READ:SENTINEL`** - it does NOT close stdin |
| `$null \| & host ...` | `EOF` |
| `cmd /c "host ... < nul"` | `EOF` |
| `ProcessStartInfo` + `StandardInput.Close()` | `EOF` |

`-InputFormat None` only suppresses PowerShell's own pipeline input; the
inherited OS stdin handle stays open and readable, so A4 is NOT met by it.
An earlier version of this plan used it and claimed the opposite. The
null-pipe form is chosen because it stays in PowerShell, needs no extra
process, and was measured to preserve BOTH the child's exit code and the
two output redirections on 5.1 and on 7.

PowerShell has NO input redirection operator: `<` is reserved and a
wrapper using it does not parse, on either host. Do not reach for it.

On Windows PowerShell 5.1 the child's stderr file additionally carries
PowerShell's own error-record decoration around each line. That is
cosmetic, the content is intact, and it is why the round's real transcript
is written by the BODY to its own file rather than read out of
`body.err`.

Without this ownership the body's output reaches the WRAPPER's stdout and
therefore the harness output file, beside the classifier's own line.

**The tree is verified at DISPATCH time, against values fixed at
preparation time.** `tools/new-review-mirror.ps1` does not leave a marker
in the mirror; it prints an identity record and offers `-VerifyIdentity`,
which takes its expected values as ARGUMENTS - deliberately, because a
file re-read later is mutable and would silently redefine the value it is
supposed to pin. `-Prepare` records them in the receipt and writes them
into the wrapper, and the wrapper re-checks them before the client runs.
Checking only at preparation time leaves the tree free to be replaced at
the same path afterwards, which is the post-preparation mutation B4
requires be detected.

**But the shipped verifier is not sufficient on its own, and Task 2a
extends it.** As shipped it compares the source head, the mirror head, and
the SOURCE's status digest. It never measures the MIRROR's contents. So an
edit to a tracked file inside the mirror worktree, without a commit, moves
neither head and changes no source-side value: it passes both
verifications, and the client reads bytes nobody bound. The tool's own
header already states this narrowness honestly; what is new here is that
this design depends on the part it does not cover. Task 1a adds a
mirror-state digest and a source-is-not-the-mirror check before this
design can rely on it, and it runs BEFORE the tool is rewritten.

**Why `$ErrorActionPreference = 'Stop'` is restored before the second
verification, and why the arguments are one defined hashtable.** MEASURED
2026-08-31 on both hosts: under `Continue`, a call that fails to BIND -
splatting a variable that does not exist, for instance - raises a
non-terminating error and leaves `$LASTEXITCODE` at the previous command's
value. The previous command is the client, which had just succeeded. So
the guard reads a stale zero and the verification silently does not
happen:

```
after successful child: LASTEXITCODE=0
after splat of undefined: LASTEXITCODE=0
GUARD DID NOT FIRE - false success
```

An earlier version of this plan wrote the second call with an undefined
`@mirrorArgs`, and that is exactly what it would have done: the
strengthening added to catch a mutated tree would itself have been the
false-success path. One hashtable defined before the first call, used by
both, and `Stop` restored before the second, removes both halves.

**Capture the verifier's stdout at both call sites.** A successful
`-VerifyIdentity` prints `identity: verified`. In `-Prepare` that line
would land in front of the JSON the caller parses; in the wrapper it would
be a second line on the stdout that must carry exactly one. Assign it or
redirect it; do not let it through.

**The wrapper carries a digest of the WHOLE receipt.** `-Prepare` writes
the receipt, hashes its finished bytes, and writes that one digest into
the wrapper's text as `<receiptSha256>`. `-Classify` re-hashes the receipt
it reads and compares. Any edit to any field after preparation - the only
way a caller could substitute an evidence boundary computed afterwards -
classifies as `receipt-altered`.

**A per-field compare would NOT have been enough, and the first version of
this design got that wrong.** It bound `token` and `priorStateSha256`
only, and claimed on that basis that the receipt was "effectively
immutable". It has fourteen fields. Ten were editable with no detection,
and one of those, `workdirEvidence`, GATES the working-directory states:
editing it to the literal `none` silently switches off the B5 check for
that round - the one carry-over the options poll specifically demanded be
wired. Hashing the whole file costs one line and removes the class rather
than four instances of it.

`token` still earns its place: it is what the digest is minted over
together with everything else, and it makes two preparations of the same
directory produce different receipts.

The lane body ends with `exit $code`, carrying the client's own exit code
out of the child. It writes its reply and its transcript into
`$PSScriptRoot`, which for `body.ps1` is the same dispatch directory.

**The child process is not decoration, and it is not a performance
choice.** If the body were inlined, a body containing `exit 0` - or
`[Environment]::Exit(0)`, which no text scan can catch - would end the
WRAPPER before the epilogue ever ran. The harness would then see exit 0
with no classification ever computed, and an empty reply would read as a
completed round. That is the one direction in which coupling the
classification to the wrapper is WEAKER than classifying afterwards, and
a child process removes it structurally: whatever the body does to its own
process, the wrapper survives to classify.

Six things this ordering buys:

0. **The answer is reserved BEFORE the round runs, not after it.** The
   first version of this plan had `-Classify` create the `classification`
   file itself. That left a window the cross-vendor lane found: a wrapper
   killed after publishing `exit` and `reply` but before classifying
   leaves the file unclaimed, so a later standalone `-Classify` creates
   it, reads that round's artifacts, and returns `reply-present` at exit
   0. Reserving at the START closes that sequence: at every moment after
   the wrapper begins, the file exists.
1. **The claim is create-new and it is the first act.** A second run of the
   same prepared wrapper dies before it can touch anything.
2. **The relocation is terminating.** A missing reviewed tree fails the
   wrapper instead of continuing from whatever directory the harness had.
3. **The body cannot skip the classification.** It runs in its own
   process.
4. **The wrapper's exit code IS the classification.** The harness trailer
   and the outcome cannot disagree, which is R9.
5. **Classification cannot outlive the process.** If the wrapper is
   suspended, hangs in teardown, or is killed after writing `exit`, it
   never reaches `exit $LASTEXITCODE`, so the harness task does not report
   a successful completion. This is the exact hole Option C left open.

### One test seam, and what it may and may not do

`PARALLAX_DISPATCH_HOLD_AFTER_EXIT_WRITE`, set to a path, makes the
wrapper create `<value>.started` after the `exit` file is written and then
wait, bounded at sixty seconds, for `<value>.release` before calling the
classifier. On timeout the wrapper fails through to a non-zero exit.

This is BUILDER CONTRACT, not test scaffolding, the same shape as the
seams in `tools/new-kimi-lane-home.ps1`: any parent process can set it, no
shipped caller sets it, and its only reachable effect is to DELAY or FAIL
a wrapper - never to turn a failing round into a successful one. Without
it, the test that proves this whole design is a millisecond race in a
different costume, which is what the previous cycle shipped.

### The states `-Classify` computes

`-Classify` REDEEMS a reservation the wrapper already consumed. It never
creates one, and it accepts exactly one content: `classifying:<nonce>`
where the nonce equals the `-Redeem` value it was given. Anything else is
refused. In this fixed order, stopping at the first match:

1. `classification` absent -> `never-reserved`
2. `classification` holds `reserved` -> `not-ready`
3. `classification` holds `classifying:<n>` with `n` not the `-Redeem`
   value, or holds anything else -> `already-classified`
4. receipt absent, unreadable, or failing the schema -> `no-receipt`
5. receipt's `dispatchDir` or `round` is not the pair supplied
   independently -> `receipt-not-expected`
6. the receipt's own bytes do not hash to the digest the wrapper carries
   -> `receipt-altered`
7. no `claim` file in the dispatch directory -> `no-claim`
8. `workingDirectory` missing, unresolvable, or not a filesystem
   container -> `cwd-unreadable`
9. `workdirEvidence` is not `none` and no transcript file exists ->
   `no-transcript`
10. `workdirEvidence` is not `none` and the transcript's FIRST `workdir:`
    header line is absent -> `workdir-unconfirmed`
11. that header line's value differs from `workdirEvidence` ->
    `workdir-mismatch`
12. no `exit` file -> `no-exit-file`
13. `exit` unreadable or not a plain integer -> `exit-unreadable`
14. `exit` non-zero -> `exit-nonzero`
15. no `reply` file -> `no-reply`
16. `reply` is empty -> `reply-empty`
17. otherwise -> `reply-present`

The tree's IDENTITY is not among these states: it is checked by
the wrapper at dispatch time, before the client runs, and a failure there
kills the wrapper rather than producing a state. A tree that was wrong
never gets as far as being classified.

Exit codes: **0 is `reply-present` and nothing else; 2 is
a parameter-binding failure or an internal execution error; 1 is every
other state**, with the state name on stdout. There is no exit 3, because
`running` cannot exist: the classifier runs only after the client has
returned.

**The working-directory check now comes BEFORE the exit states.** The
earlier version put `exit-nonzero` first, arguing the client's own failure
report was more actionable. Both reviewer lanes rejected that and they are
right: a round that ran in the wrong tree read an instruction
back-channel, so its failure report describes the wrong subject
altogether. That is the fact the preflight exists to surface, and burying
it behind a generic `exit-nonzero` relies on an operator opening the
transcript unprompted.

**The header is PARSED, never searched for.** A containment search over
the transcript is defeated by the transcript being prompt-steerable, which
this repo has already measured: a brief carrying delimiter-shaped payload
put a second `session id:` line into a codex transcript. The classifier
reads the FIRST `workdir:` header line and compares its value. An
occurrence anywhere else in the transcript proves nothing.

**Three working-directory states, not one, because they are three
different measurements.** No transcript at all indicts the wrapper's
redirection. A transcript with no header line means the tree is
UNCONFIRMED - nothing was measured. A header line that disagrees is a real
mismatch. Naming all three `workdir-mismatch` would put a made-sounding
claim on an unmade measurement.

**What the reservation does and does not close, stated exactly.**

The FIRST attempt at this had `-Classify` create the reservation. A
wrapper killed before classifying left it unclaimed, so a later standalone
call created it and returned success. The SECOND attempt moved the
creation to the wrapper's start - and still missed, because `-Classify`
went on treating `reserved` as permission to proceed. After the very kill
the flagship test performs, the file naturally says `reserved`, and no
deliberate act was needed at all. The plan's own refusal test contradicted
its own state machine, and that is how the miss survived a round.

The transition is what fixes it. `reserved` is consumed into
`classifying:<nonce>` BEFORE the `exit` file is written, so:

- Killed before the transition: the file says `reserved`, `-Classify`
  answers `not-ready`, and there is no `exit` file to succeed on anyway.
- Killed after the transition: the file says `classifying:<nonce>` and
  `-Classify` refuses it unless handed that exact nonce - which was minted
  at run time and appears in nothing `-Prepare` wrote.
- Completed: the file holds the state name, and every later call is
  `already-classified`.

**The residual, honestly bounded.** A caller who opens `classification`,
reads the nonce out of it, and passes it to `-Classify` gets that round's
disk state. Nothing on a filesystem the caller owns can prevent that, and
the shipped tool says the same about its own token. What has changed is
that this is now a DELIBERATE act on a file the caller had to go and read,
where before it was the natural consequence of a killed round. The
control is not secrecy: the authoritative answer is the exit code of the
harness task, and a killed task's exit code is not zero however its
directory reads afterwards.

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
| `tools/read-kimi-round-evidence.ps1` | gains the SAME parameter |
| `evals/multi-model-verify/test_dispatch_round.py` (renamed) | the tool's contract |
| `evals/multi-model-verify/test_contract_coverage.py` | `DECLARED_REGIONS` |
| `evals/multi-model-verify/test_multi_model_verify.py` | call-site pins |
| `skills/multi-model-verify/SKILL.md` | two call sites |
| `skills/multi-model-verify/references/backup-lane.md` | three call sites |
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

## Task 1a: Make the mirror verifier able to detect a changed mirror

The whole tree-identity argument rests on `-VerifyIdentity`, and as
shipped it cannot see a change to the mirror's own working files. This
task closes that before anything depends on it.

**Files:**
- Modify: `tools/new-review-mirror.ps1`
- Modify: `skills/multi-model-verify/references/backup-lane.md` - TWO
  paragraphs. The one telling the reader to re-run `-VerifyIdentity` with
  "the three recorded values", and the copied-in-inputs paragraph, which
  must now name inputs to the BUILD with `-ExtraInput` instead of copying
  them in afterwards.
- Modify: `evals/multi-model-verify/test_backup_lane.py` - the pin that
  quotes the first of those sentences verbatim
- Modify: `docs/superpowers/plans/2026-07-27-0150-backlog.md` - it states
  the same "three recorded values" rule as a live item's standing premise.
  A working document, not a historical record.
- Test: `evals/multi-model-verify/test_review_mirror.py` (the module that
  already exists - do NOT create a new one)

**THIS TASK BREAKS A PINNED SENTENCE, and the pin will not tell you.**
`backup-lane.md` instructs the reader to re-run the verifier with "the
three recorded values". After this task there are five, and that
documented command fails at parameter binding. The sentence is pinned
verbatim in `test_backup_lane.py`, so the gate stays GREEN while the
instruction it locks becomes unrunnable and its count becomes false. Pins
lock TEXT, not behaviour. Fix the sentence and its pin IN THIS TASK - the
pin is a raw-text pin, so re-wrap it carefully - and do not leave it for a
later task to notice.

**Interfaces:**
- Consumes: nothing.
- Produces: `-ExtraInput <path>` on the BUILD, repeatable, copying each
  named file in BEFORE the baseline and manifest are taken and listing it
  in the printed record; `mirrorStateSha256` in that record; and
  `-MirrorStateSha256 <hex>` plus `-ExpectedMirrorPath <path>` as
  mandatory arguments to `-VerifyIdentity`. Task 2's receipt carries both
  and Task 4's wrapper passes both. There is deliberately NO re-mint mode.

**This task runs BEFORE Task 2**, not after it. Task 2 writes a receipt
whose fields include the values this task invents, and calls a verifier
whose arguments this task makes mandatory. Built the other way round, Task
2 cannot satisfy its own design.

- [ ] **Step 1: Write the failing tests**

```python
def test_build_prints_a_mirror_state_digest(tmp_path):
    out = build_mirror(tmp_path)
    assert re.search(r"^mirror_state_sha256: [0-9a-f]{64}$", out, re.M)


def test_verify_detects_an_uncommitted_edit_inside_the_mirror(tmp_path):
    m = build_mirror_record(tmp_path)
    # A TRACKED file, edited, NOT committed. Moves neither head, and
    # changes nothing on the source side.
    (m.path / "README.md").write_text("changed bytes", encoding="utf-8")
    out = verify(m)
    assert out.returncode == 1
    assert "the mirror's contents changed" in out.stdout


def test_verify_detects_an_untracked_file_added_to_the_mirror(tmp_path):
    m = build_mirror_record(tmp_path)
    (m.path / "AGENTS.md").write_text("do as I say", encoding="utf-8")
    out = verify(m)
    assert out.returncode == 1


def test_verify_refuses_when_the_source_is_the_mirror(tmp_path):
    m = build_mirror_record(tmp_path)
    out = verify(m, repo_root=m.path)
    assert out.returncode == 1
    assert "the source and the mirror are the same directory" in out.stdout


def test_verify_refuses_a_mirror_at_a_different_path(tmp_path):
    m = build_mirror_record(tmp_path)
    moved = tmp_path / "moved"
    shutil.move(str(m.path), str(moved))
    out = verify(m, mirror_path=moved)
    assert out.returncode == 1


def test_extra_inputs_are_covered_by_the_digest(tmp_path):
    # Copied in as part of construction, so the identity record describes
    # the tree the reviewer actually reads.
    extra = tmp_path / "standards.md"
    extra.write_text("house rules", encoding="utf-8")
    m = build_mirror_record(tmp_path, extra_inputs=[extra])
    assert (m.path / "standards.md").read_text() == "house rules"
    assert "standards.md" in m.record
    assert verify(m).returncode == 0
    (m.path / "standards.md").write_text("tampered", encoding="utf-8")
    assert verify(m).returncode == 1


def test_there_is_no_reseal_or_remint_mode(tmp_path):
    # Re-blessing a tree that changed since it was measured is exactly
    # what the digest exists to deny.
    for flag in ("-Reseal", "-Remint", "-UpdateIdentity"):
        assert run_mirror_tool([flag]).returncode == 2


def test_an_unmeasurable_expected_digest_is_refused(tmp_path):
    m = build_mirror_record(tmp_path)
    out = verify(m, mirror_state="")
    assert out.returncode != 0


def test_a_mirror_whose_CURRENT_state_cannot_be_measured_is_refused(tmp_path):
    # Not the same test. The one above supplies a bad EXPECTED value; this
    # one makes the live measurement itself fail, which is the direction
    # that could otherwise read as clean. Mirror the source-side failure
    # tests the tool already has.
    m = build_mirror_record(tmp_path)
    with unreadable_input(m.path):
        out = verify(m)
    assert out.returncode != 0
    assert "could not be" in out.stdout
```

The last test is the standing rule: an unmade measurement and a clean one
must never look alike.

- [ ] **Step 2: Run them and watch them fail**

```bash
python -m pytest evals/multi-model-verify/test_review_mirror.py -q
```

- [ ] **Step 3: Implement**

The builder ALREADY computes a mirror baseline and a content manifest and
prints them; it is verify mode that does not accept them. Combine those
two into one `mirrorStateSha256`, print it in the identity record beside
the heads, and require it in verify mode. Recompute it over `MirrorPath`
and refuse on any difference, with the message the test pins.

Add two more refusals to verify mode, both before any digest work:

- canonical `RepoRoot` equal to canonical `MirrorPath` - otherwise passing
  the live repository as both satisfies every remaining comparison
  whenever the two heads are equal, which they are whenever the mirror
  needed no remediation commit;
- a `MirrorPath` whose canonical form differs from `-ExpectedMirrorPath`.
  This needs the new parameter: `mirrorStateSha256` carries baseline and
  manifest state only, and nothing in the shipped interface records where
  the mirror was built. Without that parameter the refusal cannot be
  implemented and must not be promised.

Correct the tool's own header in the same commit. It currently states the
narrowness accurately for what it covered; it must now state what it
covers after this change, and no more.

- [ ] **Step 4: Run the tests on both hosts**

- [ ] **Step 5: Commit**

```bash
git add tools/new-review-mirror.ps1 evals/multi-model-verify/test_review_mirror.py
git commit -m "let the mirror verifier see a changed mirror"
```

---

## Task 2: Delete `-Launch` and `-Poll`, add `-Prepare`

**Files:**
- Modify: `tools/dispatch-round.ps1`
- Test: `evals/multi-model-verify/test_dispatch_round.py`

**Interfaces:**
- Consumes: `tools/dispatch-round.ps1` from Task 1.
- Produces: `-Prepare` with the receipt schema above, and the two output
  fields `command` and `taskName`. Task 3 consumes the receipt schema;
  Task 4 consumes the wrapper the prepare installs.

- [ ] **Step 1: Write the failing tests**

Add to `test_dispatch_round.py`. These replace, not join, the
`-Launch`/`-Poll` tests, which this task deletes.

```python
def test_prepare_writes_the_whole_receipt_last(tmp_path):
    d = tmp_path / "d"
    receipt = tmp_path / "r.json"
    body = tmp_path / "body.ps1"
    body.write_text("$code = 0\n", encoding="ascii")
    prior = tmp_path / "prior.json"
    prior.write_text('{"kind":"fresh","knownRollouts":[]}', encoding="ascii")
    # A REAL mirror, built by the real tool, because -Prepare now refuses
    # anything that does not verify as one. A bare mkdir cannot be used.
    mirror = build_real_mirror(tmp_path)
    out = run_tool([
        "-Prepare", "-DispatchDir", str(d), "-WrapperBody", str(body),
        "-ReceiptPath", str(receipt), "-Round", "Sol R1",
        "-WorkingDirectory", str(mirror.path), "-RepoRoot", str(mirror.source),
        "-SourceHead", mirror.source_head, "-MirrorHead", mirror.mirror_head,
        "-SourceStatusSha256", mirror.source_status_sha256,
        "-MirrorStateSha256", mirror.mirror_state_sha256,
        "-ExpectedMirrorPath", str(mirror.path),
        "-DispatchHost", "powershell",
        "-PriorStateFile", str(prior), "-NoWorkdirEvidence", "-Json"])
    assert out.returncode == 0, out.stdout
    got = json.loads(receipt.read_text(encoding="utf-8"))
    assert set(got) == {
        "dispatchDir", "token", "round", "workingDirectory",
        "dispatchHost", "priorStateSha256", "workdirEvidence",
        "repoRoot", "sourceHead", "mirrorHead", "sourceStatusSha256",
        "mirrorStateSha256", "expectedMirrorPath", "schema"}
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


def test_prepare_installs_the_lane_body_as_its_own_script(tmp_path):
    p = prepare(tmp_path, body="$code = 0\nexit $code\n")
    assert (p.dispatch_dir / "body.ps1").read_text() == "$code = 0\nexit $code\n"
    wrapper = (p.dispatch_dir / "wrapper.ps1").read_text()
    assert "body.ps1" in wrapper
    assert "$code = 0" not in wrapper  # the body is NOT inlined


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
   receipt path exists, if the DISPATCH DIRECTORY already exists, or if
   the working directory is not an existing filesystem container. All
   before anything is created. Each block prints its own message; the
   directory case prints exactly `dispatch directory already exists`.
   Do not rely on `New-Item`'s exception text at step 4 to produce it -
   that check stays as a race backstop, but the message the test pins
   comes from this explicit pre-check.

1a. **BLOCK if the working directory does not verify as the named
   mirror.** Run `tools/new-review-mirror.ps1 -VerifyIdentity` with every
   argument Task 1a made mandatory - `-RepoRoot`, `-MirrorPath`,
   `-SourceHead`, `-MirrorHead`, `-SourceStatusSha256`,
   `-MirrorStateSha256`, `-ExpectedMirrorPath` - and BLOCK on any non-zero
   exit.

   **CAPTURE its stdout.** A successful verification prints
   `identity: verified`, and `-Prepare`'s own output is JSON a caller
   parses. Assign the call's output to a variable or redirect it; a line
   in front of the JSON breaks the caller, not just the eye.

   **There is no identity marker inside a mirror, and this plan must not
   invent one.** An earlier version of this task said to read a record
   `tools/new-review-mirror.ps1` writes into the mirror; it writes no such
   file. It PRINTS an identity record and offers `-VerifyIdentity`, taking
   the three values as arguments on purpose - for the same reason the
   codex brief binder takes a hash rather than a file: a file re-read
   later is mutable and would silently redefine the value it pins.

   Without this check the tool takes the caller's word for the directory
   AND the evidence value, so a caller who supplies the LIVE REPOSITORY
   for both gets a wrapper that deliberately relocates there, a client
   whose own report agrees with the wrong value, and `reply-present`.
   Every check downstream is self-consistent and every one is wrong. This
   is invariant B4's "detect a wrong initial value" and B1's requirement
   that entering the live repository be impossible to get wrong silently.

   Preparation-time verification is NOT sufficient on its own, which is
   why the wrapper repeats it before the client runs: the tree can be
   replaced at the same path in between, and B4 requires that
   post-preparation mutation be detected.

   There is no override switch, and that is a real consequence: a round
   whose working directory is not a verified mirror cannot be prepared at
   all. Every one of the five call sites already uses the mirror, so
   nothing in this repo needs one.
2. Resolve `-DispatchHost` to a full path with `Get-Command`. Exactly
   `pwsh` or `powershell` are accepted; anything else, or a name that does
   not resolve, exits 2.
3. Read `-PriorStateFile` as raw bytes and compute its SHA256.
4. Reserve the dispatch directory with `New-Item -ItemType Directory
   -ErrorAction Stop` and NO `-Force`.
5. Copy `-WrapperBody` into the directory as `body.ps1`, byte for byte,
   and write `wrapper.ps1` beside it. The wrapper is written ENTIRELY by
   the tool and never contains the body's text. Task 4 builds the
   wrapper's full shape; for this task write a wrapper that runs
   `body.ps1` as a child and nothing else, so the tests above pass.
6. Write the receipt LAST, with create-new semantics. **The receipt's
   BYTES must be final before step 5 writes the wrapper**, because the
   wrapper carries their digest. Compose the receipt in memory, hash it,
   write the wrapper, then write the receipt file. "Last" is about which
   file lands last, not about when its content is decided.
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

## Task 3: `-Classify`, its state order and its exit map

**Files:**
- Modify: `tools/dispatch-round.ps1`
- Test: `evals/multi-model-verify/test_dispatch_round.py`

**Interfaces:**
- Consumes: the receipt from Task 2, every field in the table above.
- Produces: `-Classify -DispatchDir <d> -ReceiptPath <r> -ExpectedRound
  <label> -ExpectedReceiptSha256 <hex> -Redeem <nonce>`, exit 0 only on
  `reply-present`. Task 4's wrapper calls it with all five; the last two
  are what make an edited receipt and an outside caller detectable.

- [ ] **Step 1: Write the failing tests, one per state**

```python
STATES = [
    ("never-reserved", 1), ("not-ready", 1), ("already-classified", 1),
    ("no-receipt", 1), ("receipt-not-expected", 1), ("receipt-altered", 1),
    ("no-claim", 1), ("cwd-unreadable", 1),
    ("no-transcript", 1), ("workdir-unconfirmed", 1),
    ("workdir-mismatch", 1),
    ("no-exit-file", 1), ("exit-unreadable", 1), ("exit-nonzero", 1),
    ("no-reply", 1), ("reply-empty", 1), ("reply-present", 0),
]
# This list is the ONLY place the state count is written down. Do not
# restate it as a number in prose: an edited list makes the prose wrong,
# which is a drift class this repo has already recorded.


@pytest.mark.parametrize("state,code", STATES)
def test_each_state_and_its_exit_code(tmp_path, state, code):
    d = build_dispatch_for_state(tmp_path, state)
    out = classify(d)
    assert out.stdout.strip().endswith(state), out.stdout
    assert out.returncode == code


def test_no_state_but_reply_present_can_exit_zero(tmp_path):
    # Drive the TOOL for every state and collect the codes it really
    # returned. Asserting over the STATES constant instead would assert
    # the test module against itself and lock nothing.
    zero = []
    for state, _ in STATES:
        d = build_dispatch_for_state(tmp_path / state, state)
        if classify(d).returncode == 0:
            zero.append(state)
    assert zero == ["reply-present"]


def test_classify_accepts_only_its_own_nonce(tmp_path):
    d, nonce = build_dispatch_ready_to_classify(tmp_path)
    for content, expected in [
        ("reserved", "not-ready"),
        ("classifying:" + "0" * 32, "already-classified"),
        ("reply-present", "already-classified"),
    ]:
        (d / "classification").write_text(content, encoding="utf-8")
        out = classify(d, redeem=nonce)
        assert out.returncode == 1
        assert out.stdout.strip().endswith(expected), content
    (d / "classification").write_text("classifying:" + nonce, encoding="utf-8")
    assert classify(d, redeem=nonce).returncode == 0


def test_a_missing_transcript_is_its_own_state(tmp_path):
    d = build_dispatch_with_workdir_evidence(tmp_path, evidence="C:\\mirror")
    (d / "exit").write_text("0", encoding="ascii")
    (d / "reply").write_text("a verdict", encoding="utf-8")
    # no transcript file at all
    out = classify(d)
    assert out.stdout.strip().endswith("no-transcript")
    assert out.returncode == 1


def test_a_failed_round_in_the_wrong_tree_reports_the_WRONG_TREE(tmp_path):
    # First match wins, and the workdir states are deliberately EARLIER
    # than the exit states. Both reviewer lanes overruled the opposite
    # order: a round that read the wrong tree read an instruction
    # back-channel, so its own failure report describes another subject.
    d = build_dispatch_with_workdir_evidence(tmp_path, evidence="C:\\mirror")
    (d / "exit").write_text("1", encoding="ascii")
    (d / "transcript").write_text("workdir: C:\\elsewhere", encoding="utf-8")
    out = classify(d)
    assert out.stdout.strip().endswith("workdir-mismatch")


def test_only_the_FIRST_workdir_header_counts(tmp_path):
    # The transcript is prompt-steerable, so a later line proves nothing.
    d = build_dispatch_with_workdir_evidence(tmp_path, evidence="C:\\mirror")
    (d / "transcript").write_text(
        "workdir: C:\\elsewhere\nuser\nworkdir: C:\\mirror\n", encoding="utf-8")
    (d / "exit").write_text("0", encoding="ascii")
    (d / "reply").write_text("a verdict", encoding="utf-8")
    out = classify(d)
    assert out.stdout.strip().endswith("workdir-mismatch")


def test_a_transcript_with_no_header_is_unconfirmed_not_mismatched(tmp_path):
    d = build_dispatch_with_workdir_evidence(tmp_path, evidence="C:\\mirror")
    (d / "transcript").write_text("no header here at all", encoding="utf-8")
    (d / "exit").write_text("0", encoding="ascii")
    (d / "reply").write_text("a verdict", encoding="utf-8")
    out = classify(d)
    assert out.stdout.strip().endswith("workdir-unconfirmed")


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

Redeem the wrapper's reservation, and NEVER create one. Refuse at
`never-reserved` when `classification` is absent, at `not-ready` when it
holds `reserved`, and at `already-classified` when it holds anything
other than `classifying:<the -Redeem value>`. Then compute the remaining
states in the documented order, stopping at the first match and
reading nothing further. Print the state name on stdout; with `-Json`,
print an object carrying `state` and the receipt's `round` when a receipt
was read, `round` null otherwise.

Write the resolved state INTO the `classification` file once it is known,
so the file is both the reservation and the record.

Reject unknown arguments: add `[Parameter(ValueFromRemainingArguments =
$true)] $Rest` to the parameter block and exit 2, naming the first
unrecognised token, whenever it is non-empty. Do this for BOTH modes.

**Verify, do not assume, that this works the same on both hosts.**
`ValueFromRemainingArguments` promotes the script to an advanced script,
which changes parameter binding. Run
`test_an_unknown_argument_is_refused_not_absorbed` under 5.1 and under 7
before moving on. If binding differs, an explicit `$args` check replaces
it and this step is corrected in the same commit.

- [ ] **Step 4: Run the tests**

```bash
python -m pytest evals/multi-model-verify/test_dispatch_round.py -q
```

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add tools/dispatch-round.ps1 evals/multi-model-verify/test_dispatch_round.py
git commit -m "add classify: only reply-present exits zero"
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
    # The body is a CHILD SCRIPT now, so setting $code proves nothing.
    # It must EXIT with the code, or the child exits zero and the round
    # reads as a success with no reply.
    d = prepare_and_run(tmp_path, body="exit 1\n")
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


def test_a_wrapper_killed_after_publishing_exit_and_reply_does_not_exit_zero(tmp_path, monkeypatch):
    # THE test. Under Option C's post-hoc classifier this same directory
    # reads reply-present at exit 0.
    barrier = tmp_path / "hold"
    monkeypatch.setenv("PARALLAX_DISPATCH_HOLD_AFTER_EXIT_WRITE", str(barrier))
    p = prepare(tmp_path, body=OK_BODY)
    proc = start_wrapper(p.wrapper)
    # The seam fires AFTER the wrapper writes the exit file and BEFORE it
    # calls the classifier. That is exactly the interval in question.
    wait_for(Path(str(barrier) + ".started"))
    assert (p.dispatch_dir / "exit").read_text().strip() == "0"
    assert (p.dispatch_dir / "reply").read_text().strip() != ""
    # The reservation was CONSUMED before the exit file was written, so
    # by the time a successful-looking exit exists it is no longer in a
    # state any outside caller is handed the key to.
    assert (p.dispatch_dir / "classification").read_text().strip().startswith(
        "classifying:")
    kill_tree(proc.pid)
    assert proc.wait() != 0
    # And the disk state that would have fooled Option C is still there.
    assert (p.dispatch_dir / "exit").read_text().strip() == "0"


def test_a_hand_run_classify_after_that_kill_is_refused(tmp_path, monkeypatch):
    # THE regression test for two failed attempts at this fix. Version one
    # let -Classify CREATE the reservation, so a post-kill call won it.
    # Version two moved creation to the wrapper but still treated
    # "reserved" as permission, so the very kill above left the file in an
    # acceptable state and no deliberate act was needed.
    p = killed_after_publish(tmp_path, monkeypatch)
    held = (p.dispatch_dir / "classification").read_text().strip()
    assert held.startswith("classifying:")   # consumed BEFORE exit was written
    # A caller who does not know the run-time nonce is refused. Guessing
    # every plausible argument does not help: the nonce is in no file
    # -Prepare wrote.
    out = classify(p.dispatch_dir, redeem="0" * 32)
    assert out.returncode == 1
    assert out.stdout.strip().endswith("already-classified")


def test_classify_never_creates_the_reservation(tmp_path):
    p = prepare(tmp_path, body=OK_BODY)  # prepared, never run
    assert not (p.dispatch_dir / "classification").exists()
    out = classify(p.dispatch_dir, redeem="0" * 32)
    assert out.returncode == 1
    assert out.stdout.strip().endswith("never-reserved")
    assert not (p.dispatch_dir / "classification").exists()


def test_the_reservation_is_consumed_before_the_exit_file_appears(tmp_path, monkeypatch):
    # Ordering is the whole argument. If exit were written first, the
    # post-kill directory would hold "reserved" plus a successful exit.
    p = killed_after_publish(tmp_path, monkeypatch)
    assert (p.dispatch_dir / "exit").exists()
    assert not (p.dispatch_dir / "classification").read_text().strip() == "reserved"


@pytest.mark.parametrize("field,value", [
    ("priorStateSha256", "ff" * 32),
    ("workdirEvidence", "none"),      # would switch OFF the B5 check
    ("workingDirectory", "C:/elsewhere"),
    ("round", "Sol R2"),
])
def test_an_edit_to_ANY_receipt_field_is_detected(tmp_path, field, value):
    # A per-field compare bound four of fourteen fields and called the
    # receipt immutable. The workdirEvidence case is the one that mattered:
    # editing it to "none" silently disables the working-directory
    # confirmation for that round.
    p = prepare(tmp_path, body=OK_BODY)
    got = json.loads(p.receipt.read_text(encoding="utf-8"))
    got[field] = value
    p.receipt.write_text(json.dumps(got), encoding="utf-8")
    out = run_wrapper(p.wrapper)
    assert out.returncode == 1
    assert "receipt-altered" in out.stdout


def test_a_whitespace_only_receipt_edit_is_detected(tmp_path):
    # The digest is over BYTES, so reformatting is an edit too. This is
    # deliberate: a receipt nobody rewrote has bytes nobody changed.
    p = prepare(tmp_path, body=OK_BODY)
    p.receipt.write_text(p.receipt.read_text(encoding="utf-8") + "
",
                         encoding="utf-8")
    out = run_wrapper(p.wrapper)
    assert "receipt-altered" in out.stdout


def test_the_body_streams_never_reach_the_wrapper_stdout(tmp_path):
    d = prepare_and_run(tmp_path, body='''
Write-Output "stdout from the body"
[Console]::Error.WriteLine("stderr from the body")
[System.IO.File]::WriteAllText("$PSScriptRoot/reply", "ok")
exit 0
''')
    assert d.stdout.strip().splitlines() == [d.stdout.strip()]  # exactly one line
    assert "from the body" not in d.stdout
    assert "stdout from the body" in (d.dispatch_dir / "body.out").read_text()
    assert "stderr from the body" in (d.dispatch_dir / "body.err").read_text()


def test_prepare_refuses_a_working_directory_that_does_not_verify(tmp_path):
    plain = tmp_path / "not-a-mirror"
    plain.mkdir()
    out = prepare_default(tmp_path, working_directory=plain)
    assert out.returncode == 1
    assert "mirror identity" in out.stdout


def test_prepare_refuses_a_mirror_whose_head_does_not_match(tmp_path):
    mirror = build_real_mirror(tmp_path)
    out = prepare_default(tmp_path, mirror=mirror, mirror_head="0" * 40)
    assert out.returncode == 1
    assert "mirror identity" in out.stdout


def test_the_wrapper_reverifies_the_tree_before_the_client_runs(tmp_path):
    # Post-preparation mutation that moves NEITHER head: a tracked file in
    # the mirror worktree, edited, not committed. This is the case the
    # shipped verifier could not see, and it is why Task 1a exists. Do not
    # weaken it to a commit - a commit moves the mirror head and would
    # test the check that already worked.
    p = prepare(tmp_path, body=OK_BODY)
    (p.working_directory / "README.md").write_text("changed", encoding="utf-8")
    out = run_wrapper(p.wrapper)
    assert out.returncode != 0
    assert not (p.dispatch_dir / "reply").exists()


def test_a_mirror_mutated_DURING_the_round_fails_the_wrapper(tmp_path):
    # The test above mutates before the wrapper starts, so it only
    # exercises the FIRST verification. This one exercises the second:
    # the child itself edits a tracked file, writes a good reply, and
    # exits zero. Everything on disk says success.
    # The helper interpolates the real mirror path; the placeholder below
    # is NOT written into the body literally.
    p = prepare(tmp_path, body='''
[System.IO.File]::WriteAllText("{workingDirectory}/README.md", "changed mid-round")
[System.IO.File]::WriteAllText("$PSScriptRoot/reply", "a verdict")
exit 0
''')
    out = run_wrapper(p.wrapper)
    assert out.returncode != 0
    # And the reservation was never consumed, so no later call can redeem
    # it either.
    assert (p.dispatch_dir / "classification").read_text().strip() == "reserved"


def test_a_second_verification_that_cannot_RUN_fails_the_wrapper(tmp_path):
    # Regression for the defect this design introduced and then removed:
    # under Continue, a call that fails to bind leaves $LASTEXITCODE at
    # the client's successful zero, so the guard passes and the check
    # never happened.
    #
    # The helper MUST break only the SECOND call site. The wrapper names
    # the verifier tool twice and nothing in its text distinguishes them,
    # so a helper that breaks both kills the wrapper at the FIRST
    # verification - which the defective version did too, making the test
    # pass against the bug it exists to catch. Break the second
    # occurrence only, by index.
    p = prepare(tmp_path, body=OK_BODY)
    break_second_mirror_call_only(p.wrapper)
    out = run_wrapper(p.wrapper)
    assert out.returncode != 0
    assert (p.dispatch_dir / "classification").read_text().strip() == "reserved"


def test_the_mirror_verifier_output_never_reaches_the_wrapper_stdout(tmp_path):
    d = prepare_and_run(tmp_path, body=OK_BODY)
    assert "identity: verified" not in d.stdout
    assert "identity: verified" in (d.dispatch_dir / "mirror.verify").read_text()


def test_a_body_that_exits_the_process_cannot_skip_the_classification(tmp_path):
    # The body runs as a CHILD, so its own exit cannot end the wrapper.
    d = prepare_and_run(tmp_path, body='[Environment]::Exit(0)\n')
    assert d.returncode != 0
    assert "no-reply" in d.stdout


def test_the_wrapper_stdout_is_the_classifier_line_and_nothing_else(tmp_path):
    d = prepare_and_run(tmp_path, body=OK_BODY)
    lines = d.stdout.strip().splitlines()
    assert len(lines) == 1          # checking only the LAST line would let
    assert lines[0].endswith("reply-present")   # a leaked line pass
```

The kill test is what separates D from C, and it only works because the
seam gives it a deterministic interval. Do NOT build it on a sleep, and do
NOT build it on the body holding: under this design the body is a child
process and the `exit` file is written by the WRAPPER after that child
returns, so a holding body never lets the exit file appear at all. The
seam is in the wrapper, between the exit write and the classify call,
because that is the only place the interval exists.

- [ ] **Step 2: Run them and watch them fail**

```bash
python -m pytest evals/multi-model-verify/test_dispatch_round.py -q -k wrapper
```

- [ ] **Step 3: Implement the composition and the seam**

`-Prepare` writes `wrapper.ps1` exactly as in the design section above:
the claim, the terminating relocation, the body run as a CHILD process
under the resolved host, the exit-file write, the seam, the classifier
call, and `exit $LASTEXITCODE` as the last statement. The body's text
never appears in the wrapper.

Single-quote every interpolated path in the generated text and double any
embedded single quote, so a path containing one cannot break the generated
script.

Implement `PARALLAX_DISPATCH_HOLD_AFTER_EXIT_WRITE` as the design section
states, bounded at sixty seconds, failing to a non-zero exit on timeout.
Document it in the script header as builder contract, with the sentence
that makes it safe: its only reachable effect is to delay or fail a
wrapper, never to turn a failing round into a successful one.

**This is MEASURED, not assumed.** The backup reviewer lane argued that
`& '<tool>.ps1'` where the tool ends in `exit N` would terminate the
WRAPPER's own process, so a successful first mirror verification would
exit the wrapper 0 before the client ever ran - a false success at the one
surface this design makes authoritative. Measured 2026-08-31 on both
hosts, and it does not:

```
outer: before
inner ran
outer: AFTER  (LASTEXITCODE=0)
wrapper exit code: 3
```

The inner `exit` ends the inner SCRIPT, sets `$LASTEXITCODE`, and the
caller continues. A non-zero inner exit propagates correctly and the
guard fires:

```
after inner 0: LASTEXITCODE=0
after inner 7: LASTEXITCODE=7
GUARD FIRED CORRECTLY
```

So the in-process form is correct for the verifier and the classifier, and
`exit $LASTEXITCODE` as the wrapper's last statement carries the
classifier's code. Do not change these three calls to child processes: the
body is a child for a different reason - a body can call
`[Environment]::Exit`, and a tool in this repo does not.

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

## Task 5: Seal the evidence boundary into the receipt, in BOTH lanes

The invariants say the chaining and sealing fixes go in both lanes. One
lane sealed is one lane sealed, not the invariant discharged.

**Files:**
- Modify: `tools/read-codex-round-evidence.ps1`
- Modify: `tools/read-kimi-round-evidence.ps1`
- Test: `evals/multi-model-verify/test_codex_round_evidence.py`
- Test: the kimi binder's own test module

**Interfaces:**
- Consumes: `priorStateSha256` written by Task 2.
- Produces: `-SealedPriorStateSha256 <hex>` on BOTH binders, with
  identical semantics and identical failure text.

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

- [ ] **Step 3: Implement `-SealedPriorStateSha256` in the codex binder**

When supplied, hash the raw bytes of `-PriorState` and compare
case-insensitively. A mismatch is exit 1 with reason `sealed-state-
mismatch`. When omitted, report `sealed: "not-checked"` in the JSON.

- [ ] **Step 4: Implement the identical parameter in the kimi binder**

`tools/read-kimi-round-evidence.ps1` takes its own mandatory
`-PriorState`. Add the same optional `-SealedPriorStateSha256`, with the
same canonicalization (raw bytes), the same reason string, and the same
`sealed: "not-checked"` when omitted. Copy the three tests from Step 1
into that binder's test module rather than sharing them: the two binders
read different clients and a shared test would hide a divergence.

- [ ] **Step 5: Run the tests on both hosts**

- [ ] **Step 6: Commit**

```bash
git add tools/read-codex-round-evidence.ps1 tools/read-kimi-round-evidence.ps1 evals/multi-model-verify
git commit -m "make captured-before-dispatch enforceable in both lanes"
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

## Task 7: Rewrite ALL FIVE call sites

**A DECISION this task must make deliberately, not incidentally.** The
`kimi-write-probe` runs no round-evidence binder today: its PASS criteria
are an explicit refusal in the reply, the marker absent on disk, and an
empty mirror status delta. Giving it the uniform shape below adds a
binding to it, which CHANGES what a probe PASS means. Either do that
knowingly and say so at the site, or exempt the probe from the binder step
and say that instead. What must not happen is the probe quietly acquiring
a new PASS definition because it was swept up in a uniform rewrite.

**There are FIVE, not four.** `backup-lane.md` carries a third
tool-driven operation, `kimi-write-probe`, with its own `-Launch` and
`-Poll` calls. Deleting those modes breaks it, and no earlier version of
this plan named it. Its body is also the exact shape the child contract
breaks: it writes `$code` into the exit file and never runs `exit $code`,
so under the new wrapper the child's ordinary zero exit would overwrite
the failure it recorded. Migrate it explicitly, do not leave it to be
noticed by a failing assertion.

**Files:**
- Modify: `skills/multi-model-verify/SKILL.md` (round 1 and resume)
- Modify: `skills/multi-model-verify/references/backup-lane.md` (round 1,
  resume, AND `kimi-write-probe`)
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


def test_both_lanes_decide_the_workdir_evidence_explicitly(body_skill, body_backup_lane):
    for body in (body_skill, body_backup_lane):
        assert ("-WorkdirEvidence" in body) or ("-NoWorkdirEvidence" in body)


def test_every_ROUND_call_site_passes_the_seal(body_skill, body_backup_lane):
    # FOUR round sites, not five. The write probe runs no round-evidence
    # binder today, and this count must not silently settle the question
    # the task header says to settle deliberately. If the probe is given
    # a binder, raise this to 5 in the commit that records why.
    total = body_skill.count("-SealedPriorStateSha256") \
        + body_backup_lane.count("-SealedPriorStateSha256")
    assert total >= 4


def test_the_write_probe_is_migrated_too(body_backup_lane):
    assert body_backup_lane.count("-Prepare") >= 3
    assert "kimi-write-probe" in body_backup_lane
```

**THREE of the tests above pin NOTHING, and all three must be labelled,
not just the obvious one.** The pin rules accept exactly three clause
forms:

- `assert "-Poll" not in body` - negative membership, excluded.
- `assert ("-WorkdirEvidence" in body) or ("-NoWorkdirEvidence" in body)` -
  membership inside an `or`, which contributes nothing from either side.
- `test_every_ROUND_call_site_passes_the_seal` - it sums two counts into a
  variable and asserts on the name, so its needles are reached through a
  variable and pin nothing.

All three are worth having as behavioural tests. None may appear in a
coverage argument. Singling out only the `not in` case, as an earlier
version of this task did, is how a coverage claim rots: the next editor
reads the warning as the complete list.

- [ ] **Step 2: Run them and watch them fail**

- [ ] **Step 3: Measure what each client reports about its working
      directory, before writing either call site**

The codex lane's transcript header carries a `workdir:` line naming the
resolved directory. Confirm it on a real round rather than trusting this
sentence, and record the exact literal form.

The kimi lane's transcript is the client's stderr and nothing in this repo
establishes that it names a working directory at all. Run one real backup
round and look. Two outcomes, both acceptable, neither assumed:

- It names one. Then the kimi call site passes `-WorkdirEvidence` with the
  resolved mirror path, exactly as the codex site does.
- **It does not. Then STOP and bring it to the user.** Do not quietly pass
  `-NoWorkdirEvidence` and note the gap. B5 is an invariant, not a quality
  signal, and a lane that cannot confirm its own reviewed tree is a lane
  shipping without one of the properties this whole cycle exists to
  enforce. Whether to ship it anyway is the user's decision, and it needs
  to be made out loud rather than absorbed into a switch.

`-NoWorkdirEvidence` therefore exists for one purpose only: rounds whose
client is not being used as a reviewer at all. It is never the answer to
"the reviewer client did not tell us".

Write the measurement into the Task 10 record either way. An unmeasured
absence and a measured one must not look alike.

- [ ] **Step 4: Rewrite each call site**

Each of the five keeps its COMPLETE operational shape independently. The
new shape is: compose the brief, write the lane body to a file, run
`-Prepare` (naming `-DispatchHost`, and passing `-WorkdirEvidence` or
`-NoWorkdirEvidence` per what Step 3 measured for that lane), dispatch the
printed `command` as a harness background command under the printed
`taskName`, and STOP.

On the completion notification for that exact task, read the harness
output file: the trailer's exit code is the result, `0` meaning
`reply-present` and nothing else, and the last stdout line names the
state. Then run the lane's round-evidence binder, passing
`-SealedPriorStateSha256` from the receipt's `priorStateSha256`. Only a
clean binding makes `reply-present` a review result.

**Passing the seal is MANDATORY at every call site, and a binding that
reports `sealed: "not-checked"` is a transport failure, not a clean
round.** The parameter is optional on the binder because other callers
exist; it is not optional here. An optional check that a call site may
omit is the shape E4 exists to forbid - a boundary computed after the
reply could then satisfy it - so the call sites say "clean binding AND
sealed checked", never just "clean binding".

State plainly at each site: never re-read the dispatch directory to
decide a verdict. A hand-run `-Classify` is refused unless the caller goes
and reads the run-time nonce out of `classification` first - so the
mechanism catches the accident, not the determined caller. The rule stands
either way, and the authoritative answer remains the harness task's exit
code.

- [ ] **Step 5: Run the tests and the lint**

```bash
python -m pytest evals/multi-model-verify -q
python evals/tools/skill_lint.py skills/multi-model-verify --strict
```

The lint's token budget will still warn. Task 9 addresses it. It must not
have gone UP.

- [ ] **Step 6: Commit**

```bash
git add skills evals
git commit -m "rewrite all five call sites for completion-coupled dispatch"
```

---

## Task 8: Rewrite the dispatch contract regions

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
- `round-dispatch-states`: the states in order, the exit map, and
  the sentence that carries the whole design - **the classification is the
  wrapper's own exit code, so a wrapper that does not reach its final
  statement cannot report success, whatever its directory holds.**
  **Expect this to need SPLITTING into two regions.** A region must fit
  whole inside a single pin, and the full state list plus the exit map plus
  that sentence will not. Split it at the boundary between the state list
  and the exit map, and add BOTH ids to `DECLARED_REGIONS`. A region too
  long for one pin is two regions, and discovering that at the coverage
  gate is expected, not a failure of this plan.
- `round-dispatch-states` must carry ALL FIVE residuals from the
  "residuals this plan SHIPS" section, not only the post-hoc one. That
  section says they belong in this region; this is the task that writes
  it, so this instruction is the normative one and the region is where a
  reader will actually meet them. It must also state the post-hoc residual
  plainly, the way the old tool stated its own, and must NOT claim more
  than the mechanism delivers. What it says: deleting `-Poll` does not remove the post-hoc
  surface, because `-Classify` is still a standalone mode. What closes the
  natural case is the reservation being CONSUMED into a run-time nonce
  before any terminal artifact is published, so a killed round leaves a
  state no outside caller is handed the key to. What remains is a caller
  who opens the reservation file, reads the nonce, and passes it - a
  deliberate act on a file they own, which no filesystem mechanism can
  prevent. And a caller who supplies an earlier act's receipt, directory
  and label to a FRESH preparation is still truthfully told that act's
  result.
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

- [ ] **Step 2a: Measure the harness's FAILURE surface, which is the
      design's own premise**

The whole design rests on "a wrapper that does not finish cannot report
success". That is a claim about what the HARNESS says, and nothing above
tests it. This repo has already been burned once here: R9 exists because
the harness announced a failed round as "completed (exit code 0)".

Run two more rounds and record what the notification and the trailer
actually say:

- **A round that FAILS.** Give the lane body a client invocation that
  exits non-zero. Expected non-zero at the trailer and `exit-nonzero` on
  stdout; record what you actually see.
- **A round that is KILLED.** Dispatch with
  `PARALLAX_DISPATCH_HOLD_AFTER_EXIT_WRITE` set, wait for the sentinel,
  then kill the task. Record the notification wording, the trailer, and
  whether `classification` was ever created.

If either comes back reporting success, STOP. That is not a defect in this
plan's tests; it is the design's premise failing, and it goes back to the
reviewer lanes before anything else is built.

- [ ] **Step 2b: Record what each client says about its working
      directory**

Carry Task 7 Step 3's measurement into this record: the codex header's
`workdir:` literal, and whether the kimi transcript names one at all.

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

- [ ] **Step 6: File the hung-round item**

Add one entry to `docs/superpowers/plans/2026-07-27-0150-backlog.md`: no
policy bounds how long a hung harness round may sit before it is killed
and re-dispatched. Named by the Kimi lane in the options poll. It is not a
correctness defect - a hung round can never read as success - so it costs
waiting, not truth. Do not rank it; ranking means costing it and nobody
has.

- [ ] **Step 7: Commit**

```bash
git add CLAUDE.md docs/superpowers/plans/2026-07-27-0150-backlog.md
git commit -m "correct the dispatch rules CLAUDE.md still states as measured"
```

---

## The residuals this plan SHIPS, stated rather than hidden

Each of these was found by a reviewer lane, is real, and is being shipped
as a stated limit rather than fixed. They belong in the
`round-dispatch-states` region, not only here.

1. **A tracked file whose bytes change while git still reports it clean.**
   `-VerifyIdentity` hashes what git's status listing names plus the
   content manifest. A path hidden behind `assume-unchanged`,
   `skip-worktree`, or another clean-filter condition can change without
   moving HEAD, the baseline, or the manifest. The mirror tool already
   documents this boundary in its own header; Task 1a must not widen the
   claim beyond it. Narrower than the ordinary edit Task 1a fixes.
2. **A caller who reads the run-time nonce out of `classification` and
   hands it to `-Classify`, or who edits the WRAPPER itself.** The digest
   binds the receipt; nothing binds the wrapper's own text after
   preparation. They get that round's disk state. No
   filesystem mechanism can stop the owner of the filesystem. The
   authoritative answer remains the harness task's exit code.
3. **A change made to the mirror and undone again before the client
   finishes.** The wrapper verifies before the client runs and again after
   the child returns, so a mutation that PERSISTS through the round is
   caught and the round fails. Only change-and-revert survives, and no
   before-and-after check could catch it. This is filesystem ownership
   during dispatch, explicitly trusted. Note that this residual is
   correctly stated ONLY because the second verification actually runs -
   an earlier version wrote that call so it could not bind, which turned
   this from a narrow residual into an unstated correctness defect.
4. **The harness trailer's format is measured, not pinned across
   versions**, and neither is the premise beside it - that a killed task
   reports a non-zero exit on the harness surface. Task 10 Step 2a
   measures that premise on ONE harness version, with a STOP if it fails.
   Nothing in this repo parses the trailer mechanically.
5. **No bound on how long a hung round may sit.** Filed as a backlog item
   by Task 11; a hung round can never read as success, so this costs
   waiting, not truth.

6. **Review inputs copied into the mirror AFTER construction stop
   working.** The backup lane documents copying in any input the mirror
   cannot inherit - a standards file above the repo root, a spec kept
   outside the tree - and enumerating it before the round. `mirrorStateSha256`
   is minted at construction, and Task 1a provides no way to re-mint it,
   so anything copied in afterwards fails `-Prepare` and the wrapper's
   first check. The direction is conservative - it BLOCKS, it never
   false-passes - but a documented workflow becomes unrunnable. Found by
   the backup lane, which is the lane that uses it.

   **SETTLED, so no implementer has to decide it: Task 1a adds
   `-ExtraInput <path>` to the BUILD, repeatable, and adds NO re-mint
   path.** The named files are copied in as part of construction, before
   the baseline and manifest are taken, so the identity record covers them
   and the printed record enumerates them. A re-mint mode would be the
   ability to re-bless a tree that has changed since it was measured,
   which is exactly the capability the digest exists to deny; it would be
   a hole with a friendly name. If a round needs an input nobody thought
   of until after construction, the answer is to rebuild the mirror, which
   is cheap and leaves the record honest.

**One thing that is NOT shippable as a residual:** the preparation-time
verifier output. `identity: verified` in front of `-Prepare`'s JSON breaks
a machine-readable interface. Task 2 captures it.

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
  has costed it. **Task 11 files it as a backlog item**, because "file it
  rather than invent it" is only true if someone actually files it.
- **It does not measure what happens to a round when the session ends.**
  Survival was dropped as a requirement by the owner. Any future design
  that reintroduces a detached worker to buy survivability is reopening a
  settled decision.

## Self-review, run against the poll's nine required carry-overs

| Required | Task |
|---|---|
| 1. Build Option D, not C | 2, 3, 4 |
| 2. State and test the write ordering | 4, whose test list is the check - do not cite a count here, since editing the list would make the count wrong |
| 3. Test the benefit directly | 10, steps 2 and 2a |
| 4. Name the interpreter and flags | 2 (`-DispatchHost`), 7 |
| 5. Bind the cwd and check `workdir:` | 2 (receipt, plus the mirror-identity refusal), 3 (`no-transcript`, `workdir-unconfirmed`, `workdir-mismatch`, parsed from the header), and 7 step 3, which is what makes a call site actually USE it |
| 6. Rewrite the exit-3 contract at both call sites | 7, 8 |
| 7. State the recovery rule | 8 (`round-dispatch-operation`) |
| 8. Reject unknown arguments | 3 |
| 9. Probe the no-window behaviour | 10, step 2, item 5 |

Two further carry-overs, from the invariants rather than the poll: the
evidence boundary is sealed in BOTH lanes in Task 5 (E4), and the
cross-lane bookmark rule is fixed in BOTH lanes in Task 6 (E2).

**A mechanism no call site uses does not discharge a carry-over.** Row 5
was written once as if building the check were enough; it is not, and the
row now names the task that wires it.

## The round-1 review this plan has already answered

`docs/superpowers/plans/rounds/2026-08-31-completion-coupled-dispatch/fable-plan-review-r1.md`
is the Fable panel lane's review of the FIRST version of this plan, at
commit `b5b5716`. Verdict FIX. Every one of its seven required changes is
applied above:

1. The kill test's mechanics are stated, and the seam that makes them
   deterministic is back.
2. The E4 seal covers both binders.
3. `-WorkdirEvidence` is measured per lane and wired at the call sites.
4. Task 10 measures a failed round and a killed one.
5. The post-hoc `-Classify` residual is closed by the answer claim AND
   stated in the region.
6. The body-self-exit bypass is closed structurally: the body runs as a
   child process.
7. The minor items - the vacuous test, the mislabelled absence checks, the
   `dispatch directory already exists` message, the advanced-script
   verification, the unfiled hung-round item - are all corrected.

## The round-2 review this plan has also answered

`docs/superpowers/plans/rounds/2026-08-31-completion-coupled-dispatch/sol-plan-review-r1.md`
is the cross-vendor lane's review, bound clean, verdict FIX. It found a
real hole in the fix above and five more things:

1. **The answer claim did not close what I said it closed.** With
   `-Classify` creating the reservation, a wrapper killed BEFORE
   classifying left the file unclaimed, so a later standalone call created
   it and returned `reply-present` at exit 0 - the same hole in a new
   place, and my own kill test asserted the condition that made it
   possible. The reservation moved to the wrapper's first act.
2. **A caller supplying the live repository for BOTH the working
   directory and the evidence literal got a self-consistent wrong
   answer.** `-Prepare` now refuses a working directory that is not a
   review mirror.
3. **The transcript check was a containment search**, which a
   prompt-steerable transcript defeats. It now parses the first `workdir:`
   header line, and `workdir-unconfirmed` is separated from
   `workdir-mismatch`.
4. **The child process inherited the wrapper's streams**, so body output
   would have reached the harness file beside the classifier's line. The
   three streams are now owned, and the test checks the WHOLE stdout
   rather than its last line.
5. **The evidence seal was optional and the receipt was mutable.** The
   seal is mandatory at every call site, and the wrapper now carries the
   token and the digest so an edited receipt classifies as
   `receipt-altered`.
6. **A FIFTH call site existed that I never counted**, `kimi-write-probe`
   in the backup lane, whose body would have had its recorded failure
   overwritten by the child's zero exit.

It also rejected my ordering argument, agreeing with the panel lane: the
working-directory states now precede the exit states.

## The round-3 review this plan has also answered

The cross-vendor lane reviewed the revision above, bound clean, and
returned FIX again. It found that **two of the six fixes moved their
defects rather than removing them**, which is the outcome that brief
specifically asked it to look for:

1. **The reservation still authorised a post-kill classification.**
   Moving creation to the wrapper was not enough, because `-Classify` went
   on accepting `reserved` as permission to proceed - and after the very
   kill the flagship test performs, the file naturally holds `reserved`.
   No deliberate act was required, and the plan's own refusal test
   contradicted its own state machine. Fixed by CONSUMING the reservation
   into `classifying:<run-time nonce>` before any terminal artifact is
   published.
2. **The mirror identity record I told the engineer to read does not
   exist.** `tools/new-review-mirror.ps1` writes no marker; it prints an
   identity record and offers `-VerifyIdentity` taking three values as
   arguments, deliberately, because a file re-read later is mutable.
   Verified directly. Fixed by using that interface, recording the three
   values in the receipt, and re-verifying in the WRAPPER before the
   client runs - which also closes the same-path content swap the lane
   raised.
3. **`< NUL` is not valid PowerShell.** Verified on both hosts: `<` is a
   reserved operator and the wrapper would not have parsed. Replaced with
   `-InputFormat None`.
4. **`WriteAllText` is not create-new**, it overwrites. The reservation is
   now opened with `FileMode.CreateNew`.
5. Task 3's state table was missing three states and still pinned the
   superseded ordering; Task 3's interface omitted two parameters Task 4
   called; Task 4's failed-client fixture set `$code` without exiting, so
   under the child contract it would have produced `no-reply` rather than
   the failure it claimed to test; Task 7 still said "four".

Its reply is retained at
`docs/superpowers/plans/rounds/2026-08-31-completion-coupled-dispatch/sol-plan-review-r2.md`.

## The round-4 review this plan has also answered

The cross-vendor lane's third pass, bound clean, FIX again. The nonce
change it called CLOSE. Two things it called a MISS, and both were right:

1. **The mirror fix moved its defect too.** The fictional marker was gone,
   but `-VerifyIdentity` as shipped compares the source head, the mirror
   head, and the SOURCE's status digest - it never measures the MIRROR's
   own contents. So a tracked file edited inside the mirror without a
   commit moves neither head, changes nothing source-side, passes BOTH
   verifications, and the client reads bytes nobody bound. It also showed
   that passing the live repository as both source and mirror satisfies
   every remaining comparison whenever the two heads are equal. **Task 2a
   is new** and closes both before anything depends on the verifier.
2. **`-InputFormat None` does not close stdin.** It suppresses
   PowerShell's pipeline input only. I measured all four candidate forms
   with its sentinel test on both hosts and put the table in the design
   section: `-InputFormat None` reads `SENTINEL`; the null-pipe form,
   `cmd /c < nul`, and a closed `ProcessStartInfo` handle all give `EOF`.
   The null-pipe form is now used, and it was measured to preserve the
   child's exit code and both redirections as well.

It also caught that a successful `-VerifyIdentity` prints
`identity: verified`, which would have landed in front of `-Prepare`'s
JSON and added a second line to the wrapper stdout that must carry exactly
one; that my flagship kill test still asserted `reserved` while the design
and the next test required `classifying:`; that the top-level `Classify`
signature omitted `-Redeem`; that Task 7 still claimed a hand-run is
"refused outright" when a caller who reads the nonce is not; and that I
had removed only one of the four restated counts.

Its reply is retained at
`docs/superpowers/plans/rounds/2026-08-31-completion-coupled-dispatch/sol-plan-review-r3.md`.

## The round-5 review this plan has also answered

The cross-vendor lane's fourth pass, bound clean, FIX. **It found no new
false-success path in the wrapper or the classifier**, and said the
wrapper and classifier design is now good enough. Everything it raised was
wiring:

1. **Task 2a was not connected to Task 2.** It made an argument mandatory
   that Task 2 never passed, invented a receipt field Task 2 never wrote,
   and modified neither the tool nor its tests. Built in that order, Task
   2 could not satisfy its own design. It is now **Task 1a and runs first**,
   and Task 2 passes and records both new values.
2. **The "refuse a moved mirror" promise had no interface.** Nothing
   recorded where the mirror was built, so the refusal could not be
   implemented. `-ExpectedMirrorPath` is added; without it the promise
   would have been deleted rather than left standing.
3. **The preparation-time verifier output was still uncaptured**, so
   `identity: verified` would have landed in front of `-Prepare`'s JSON.
   Named explicitly as the one item that must NOT ship as a residual.
4. **The test module I named does not exist.** The repo's mirror tests are
   in `test_review_mirror.py`; I invented `test_new_review_mirror.py`.
   Verified.
5. A stale field count, and a measurement-failure test that only exercised
   a bad EXPECTED value rather than a failure to measure the CURRENT one -
   which is the direction that could read as clean.

It also accepted a cheap strengthening it proposed: the wrapper verifies
the tree AGAIN after the client returns, so a mutation that persisted
through the round is caught.

And it ranked what could honestly ship as a stated residual, which is now
its own section above rather than scattered through the design.

Its reply is retained at
`docs/superpowers/plans/rounds/2026-08-31-completion-coupled-dispatch/sol-plan-review-r4.md`.

## The round-6 review, the last one, and what it found

The cross-vendor lane's fifth pass, bound clean, FIX - and it caught the
pattern one final time, in the strengthening I had just added at its own
suggestion.

**The second mirror verification could not run.** I wrote its arguments as
a splat of `$mirrorArgs`, a variable no part of the plan defined. The lane
then measured what that actually does, and I reproduced it on both hosts:
under `$ErrorActionPreference = 'Continue'` - which the wrapper sets
before running the client, deliberately, because of the codex stderr trap
- a call that fails to BIND raises a non-terminating error and leaves
`$LASTEXITCODE` at the previous command's value. The previous command is
the client, which had just succeeded.

```
after successful child: LASTEXITCODE=0
after splat of undefined: LASTEXITCODE=0
GUARD DID NOT FIRE - false success
```

So the check would have been skipped, its guard would have read the
client's stale zero, and a round whose tree was mutated mid-flight would
have classified `reply-present`. **The strengthening added to catch a
mutated tree would itself have been the false-success path.**

Fixed by defining ONE `$mirrorArgs` hashtable before the first
verification and using it for both, restoring `Stop` before the second
call, and adding two regression tests: a child that mutates the tree
mid-round and still reports success, and a second verification that cannot
run at all. Both must fail the wrapper with the reservation unconsumed.

It also confirmed the other five changes CLOSE their findings, walked all
twelve tasks in their new order and found only Task 4 unbuildable, judged
the residual list honest once this defect was fixed, and named two
editorial stale counts, both corrected.

Its reply is retained at
`docs/superpowers/plans/rounds/2026-08-31-completion-coupled-dispatch/sol-plan-review-r5.md`.

## The round-7 review: the panel lane, on the corrected version

The Claude-side lane reviewed the version the cross-vendor lane never saw.
It called the `$mirrorArgs`/`Stop` correction itself a PASS, verified that
all seven of its own round-1 requirements survived five later revisions
intact, and found four things worth fixing:

1. **Task 1a breaks a PINNED sentence, and the pin cannot tell you.**
   `backup-lane.md` instructs the reader to re-run `-VerifyIdentity` with
   "the three recorded values". Task 1a makes it five, so that documented
   command fails at parameter binding - while the pin in
   `test_backup_lane.py` that quotes the sentence verbatim stays GREEN,
   because pins lock text and not behaviour. Verified directly. This is
   this repo's most-recorded defect class, shipped inside the plan meant
   to be careful about it. Task 1a now names both files.
2. **One of the two new regression tests was vacuous.** Breaking the
   verifier tool's path breaks BOTH call sites, so the wrapper dies at the
   first verification - which the DEFECTIVE version did too. The test
   passed against the bug it existed to catch. It must break the second
   occurrence only, and the mutation test is the real lock.
3. **The receipt-immutability claim was far wider than its mechanism.**
   Binding `token` and `priorStateSha256` bound four fields of fourteen.
   Ten were editable undetected, and one of them, `workdirEvidence`, GATES
   the working-directory states: editing it to `none` silently switches
   off the B5 check for that round. Replaced with a digest over the WHOLE
   receipt, which costs one line and removes the class instead of four
   instances of it.
4. Three assertions pin nothing under the pin rules, not one; Task 8 was
   told to write only one of the five residuals into the region the
   residuals section says holds all five; the write probe would have
   acquired a new PASS definition by being swept into a uniform rewrite;
   and the `$code` backstop implies coverage it does not have.

Its reply is retained at
`docs/superpowers/plans/rounds/2026-08-31-completion-coupled-dispatch/fable-plan-review-r2.md`.

## The round-8 review: the backup lane, seeing the plan for the first time

The backup lane took part in the options poll and gave the only PASS in
this cycle, then did not see the plan until now. Verdict FIX.

**Its central finding is REFUTED, and I measured it rather than argue.**
It held that the wrapper's in-process `& '<tool>.ps1'` calls would be
terminated by those tools' own `exit N`, so a successful first mirror
verification would exit the wrapper 0 before the client ran - a false
success at the authoritative surface. Measured on both hosts: the inner
`exit` ends the inner SCRIPT, sets `$LASTEXITCODE`, and the caller
continues; a non-zero inner exit propagates and the guard fires. The
measurement is now in the design section, replacing a hedge that had been
sitting there unmeasured since Task 4 was written. The finding was wrong;
raising it is what got the assumption measured.

**Five of its other findings are real, and four are things only this lane
would have noticed**, because they are about its own call sites:

1. **All THREE backup-lane bodies** write `$code` into the exit file and
   none runs `exit $code` - the same shape the plan had called out for the
   write probe alone. Under the child contract every one of them would
   report a failed client as a success. All five sites now get it.
2. **Task 7 breaks three pins in `test_backup_lane.py`**, which its file
   list did not name - the same class as Task 1a's pinned sentence,
   recreated in a later task, differing only in that these fail loud.
3. **The seal-count pin foreclosed a decision the same task says to make
   deliberately.** `total >= 5` is only satisfiable by giving the write
   probe a binder, so the pin decided the either/or the header poses. It
   is now `>= 4`, the number of ROUND sites.
4. **Copied-in review inputs stop working.** The lane documents copying in
   inputs the mirror cannot inherit; the mirror digest is minted at
   construction and Task 1a offered no way to re-mint it. Conservative -
   it blocks rather than false-passes - but it silently breaks a
   documented workflow, and Task 1a now has to resolve it.
5. The backlog carries the same "three recorded values" sentence as a live
   item's premise, and it is a working document, not a record.

It also caught that the receipt's bytes must be final before the wrapper
is written, since the wrapper carries their digest, while Task 2 said the
receipt is written last - and that the wrapper's own text is unbound after
preparation, now folded into residual 2.

Its reply is retained at
`docs/superpowers/plans/rounds/2026-08-31-completion-coupled-dispatch/kimi-plan-review-r1.md`.

## Where the plan stands

EIGHT review rounds across THREE lanes - five cross-vendor Sol rounds,
two Fable, one Kimi backup-lane - each with its own section above. (This
line said "six rounds across two lanes" until cross-vendor round 1 of the
diff debate counted the sections and found otherwise.) The cross-vendor lane's own summary of
this last one: "one small correction short of buildable". That correction
is applied above, and its regression tests are written. Nothing else it
raised is outstanding.

This version was UNREVIEWED when it was frozen, and the line here used to
stop at that. It has since been verified retrospectively: cross-vendor
round 2 of the diff debate read the post-round-8 correction and judged it
"directionally sound but incomplete", finding one open defect in it. The
debate record below carries that outcome and the status it earns.

---

## Debate record

**Participants:** Opus 5 (session) / gpt-5.6-sol (codex exec, session
`01a05f3b-400f-7500-b3e8-0716c7a4dc2f`) / claude-fable (fable-reviewer
seat) / kimi-code/k3-256k (backup lane)
**Rounds used:** 8 on the plan, plus 2 retrospective rounds inside the
diff debate that re-opened this plan's final revision
**Outcome:** escalated
**Verification status:** DEGRADED
**Degradation:** final-revision-fix-outstanding
**Authorized by:** not-authorized
**Raw rounds:** `docs/superpowers/plans/rounds/2026-08-31-completion-coupled-dispatch/`
(sol-plan-review-r1..r5, fable-plan-review-r1..r2, kimi-plan-review-r1,
and the diff debate's own rounds)

### Why this is DEGRADED and not FULL

This status is the cross-vendor reviewer's own words, recorded rather than
inferred, and the session did not upgrade it. It was asked directly which
status the plan honestly earns and answered: `DEGRADED`, degradation
`final-revision-fix-outstanding`, `Authorized by: not-authorized`.

The frozen plan had NO debate record appendix at all until this one, which
`references/frozen-plan-format.md` requires of every frozen plan. Eight
review rounds had happened and none of them was recorded in the required
shape, so nothing in the plan could be read as a verification status. That
absence is the first half of the degradation.

The second half is substantive. The correction made after the plan's
round-8 review was never reviewed before implementation began, and when it
finally was, it was found incomplete: the plan promises `-ExtraInput` will
copy in EACH named file, while the implementation flattened every input to
its leaf name and wrote it with `-Force`. Two inputs sharing a leaf name
silently became one, and an outside file could replace a reviewed file
that the mirror digest then certified. Both are now refused, with tests,
but the defect existed because a plan revision went unreviewed.

### Degraded-mode note

What was skipped: nothing was skipped by choice, and no cross-vendor lane
was unavailable at any point. What was MISSING is a record - the appendix
this section now is - and what was LATE is the review of the final plan
revision, which happened during the implementation's own diff debate
rather than before implementation started.

What that costs: a reader of this plan between its freezing and this
appendix had no way to tell whether it had been verified, and the
implementer built from a revision no reviewer had seen.

This status is not upgraded by the fixes made in response to it. Upgrading
it would require the thing that was missing - a review of the final
revision BEFORE it was built from - and that is not recoverable after the
fact.

