# Three-lane poll on the dispatch options: result

Asked 2026-08-31, after the tracked-background plan was withdrawn on an
ESCALATE and the owner settled the harness-tracked background command as
the only dispatch method.

The question and the three options are in
`docs/superpowers/specs/2026-08-31-dispatch-options-costing.md`. The brief
each lane received is `brief.md` in this directory, verbatim and identical
for all three.

## Lanes, and what each one is worth

| Lane | Client / seat | Verdict | Reply retained |
|---|---|---|---|
| Sol | `gpt-5.6-sol` via codex, session `01a05928-1149-7e50-bbb3-99699436f35d` | **FIX** | `sol-reply.md`, binding `sol-binding.json` |
| Kimi | `kimi-code/k3-256k`, backup lane | **PASS** | `kimi-reply.md` |
| Fable | `parallax:fable-panel-reviewer` | **FIX** | **NOT RETAINED** - see below |

All three read the SAME frozen file copy at commit `25dde0c`
(`kerev-dd1`), never the live repository.

**Sol's round is bound.** Route read from the client's own header:
`workdir: C:\Users\Brandon\AppData\Local\Temp\kerev-dd1`, `model:
gpt-5.6-sol`, `provider: openai`, `sandbox: read-only`, `reasoning effort:
high`. Round-evidence binding returned `status: clean` against
`priorstate-poll.json` and the brief digest
`81a003182d557b6d548ccc9c74a63c71b26f5c743d71e0efee59d81458cc77c0`.

**Kimi's round is confirmed by content, not by a binder.** Its `exit` file
reads `0` and its reply is 10617 bytes. The tree it read is established
negatively: the live costing document contains `R9` twice and the
`25dde0c` copy contains it zero times, and neither Kimi's reply nor its
transcript mentions `R9` while discussing that document in detail.
`kerev-dd1` is the only tree on the machine holding that file at that
revision.

**Fable's reply was not retained as a file, and that is a process defect
of this poll.** Its answer reached the session as a subagent report and
the verbatim text is no longer recoverable. Its findings are recorded
below from the session's contemporaneous account. Treat them as reported,
not as quoted. Every future panel-lane answer is to be written to a file
before it is read, exactly as the two client lanes already are.

## The one finding all three lanes reached independently

**Option C's safety argument rests on the wrapper's write ordering, and
nothing in the costing document states it.**

The costing document claims a still-running round "also" lands on
`no-exit-file` (`2026-08-31-dispatch-options-costing.md:140-145`). All
three lanes went at that sentence and all three found it load-bearing and
unstated. They did NOT agree on whether it is sufficient.

## Where the lanes disagree, stated rather than averaged

**Kimi says the ordering is sufficient and only needs writing down.** It
searched six shapes - the reproduced rerun race, stale reply, kill
mid-flight, torn writes, forged claim, caller confusion - and found no
path to a false completion, "given the ordering the current wrapper
already has". Verdict PASS, with the ordering promoted to a stated
invariant.

**Sol says the ordering is NOT sufficient, and gives the case.** The
wrapper writes `exit` itself, as a PowerShell statement. Between that
write returning and the wrapper PROCESS ending there is an interval. A
wrapper suspended, hung in teardown, or killed in that interval leaves
claim + `exit=0` + a non-empty reply on disk while its harness task is
still running or was killed. C's classifier reads that as
`reply-present`, exit 0.

**Sol is right and Kimi's sweep has a gap.** Kimi's shape (c) reasons that
"a killed wrapper never reaches that line". Sol's case is a wrapper killed
AFTER that line. The two sweeps agreed and shared a blind spot, which is
the class this repo has already recorded.

Sol's second case: run A completes; the same wrapper is dispatched as B; B
is killed before its first act or refused at the claim; post-hoc
classification still finds A's claim and terminal artifacts and answers
`reply-present`. The claim stops B overwriting A, but claim PRESENCE does
not say which invocation created it.

**Fable's finding is the same defect seen from the other end.** The
wrapper never runs `exit $code`, so the wrapper process exits 0 whatever
the client did, and the harness's trailer and notification announce a
failed round as a success. The session CONFIRMED this live the same hour
on a real failed round: the Kimi poll round shattered its brief on
PowerShell 5.1, the client exited 1, the `exit` file correctly recorded
`1`, and the harness reported `[exited with code 0]`. Recorded as R9 in
the costing document.

## The fourth option, proposed by two lanes and better than C

Both Sol and Kimi proposed a fourth option. **Kimi's version - let the
harness trailer replace the wrapper's `exit` file - it then argued against
itself**, because the classifier would depend on a harness-internal format
that is measured today and pinned across no harness version. Called it a
wash.

**Sol's version is different and is the recommendation this poll
produces.**

**Option D, "completion-coupled C".** Keep everything C keeps -
preparation, receipt, create-new claim, working-directory binding, the
outcome states. Change ONE thing: classification is the wrapper's FINAL
ACT, inside the same harness-tracked process, and the wrapper exits with
the classifier's mapped status.

1. The harness starts the named wrapper.
2. The wrapper creates its claim first.
3. It relocates to the working directory terminatingly, runs the client,
   records the outcome.
4. It runs the classifier, emits one outcome record to its own
   harness-captured stdout, and exits with the classifier's status.
5. Only that exact task's completion and output are collected. Reading the
   directory afterwards is diagnostic, never authoritative.

**Why it closes what C leaves open.** If classification succeeds but the
wrapper is killed before it exits, the exact harness task does not report
a successful completion, so the disk state cannot answer alone. If B loses
the claim, B's own harness task exits non-zero, and A's output belongs to
a different task and cannot stand in for it. Success becomes: the exact
named task completed acceptably, AND the classifier returned
`reply-present`, AND the evidence binder was clean.

**It also makes Fable's R9 automatic** rather than a rule someone must
remember: the wrapper's exit code IS the classifier's result, so the
trailer and the classification cannot disagree.

**Cost.** Approximately C's. No pid, no start ticks, no recycled-pid
handling, no C#, no per-host process APIs. It adds a wrapper epilogue and
harness integration tests, and it removes the separate post-notification
classification step.

## What the poll settles

**The recommendation changes from C to D.** Option C is not shipped as
written. Nothing in B is revived: the liveness model stays deleted, and
every lane agreed that deleting it is right.

## Requirement defects, and which lane found each

- **R4's "everywhere" is too broad.** Named by Sol and by Kimi
  independently, and by Fable. Scope it to review-round client dispatch;
  harness-owned background subagents (mechanism 4) stay available.
- **The interpreter and execution environment are absent from R1-R8.**
  Named by Sol and Kimi. A3 and A4 are measured in the invariants and the
  costing document omits them. Under the harness command the host must be
  named explicitly or the PowerShell 5.1 silent downgrade returns.
- **R6 states the destination but not its enforcement.** Named by Sol.
  Canonical directory in the receipt, terminating relocation, and the
  client's own `workdir:` line must all be required.
- **Fail-closed argument handling is missing.** Named by Sol. Pre-existing
  and shipped.
- **The claimed harness behaviour is unverified.** Named by Sol and Kimi.
  The task row, the notification, and the open conversation need direct
  probes. Kimi adds R5: no-window behaviour was measured only for the
  redesign's own spawning, never for a harness-run wrapper, so it stays
  UNMEASURED until probed.
- **Exit code 3, `running`, is still in the shipped poll contract at both
  call sites.** Named by Kimi. C deletes the state and no requirement says
  the call-site loops keyed on it must be rewritten. Unstated, that is how
  a stale exit-3 loop survives into the new design.
- **A hung-round policy is missing.** Named by Kimi. A hung task is
  classified correctly forever and nothing bounds how long it sits.
- **Re-dispatch is not free.** Named by Sol and Kimi. Every attempt
  advances the reviewer's append-only record, so recovery must capture a
  NEW evidence boundary immediately before the new dispatch. Reusing the
  last clean bookmark is the shipped E2 defect.

## What the replacement plan must carry out of this

1. Build Option D, not Option C.
2. State the wrapper's write ordering as an invariant, and test it:
   reply and `exit=0` published while the wrapper is held alive; a kill
   during that hold; concurrent double start; rerun after completion.
3. Test the benefit directly: the named task row, the notification, the
   conversation staying open.
4. Name the interpreter and the execution flags.
5. Bind the working directory into the receipt and check the client's
   `workdir:` line.
6. Rewrite the exit-3 poll contract at both call sites in the same plan.
7. State the recovery rule: `no-exit-file` never means safe to re-run;
   recovery is a fresh preparation with a fresh evidence boundary.
8. Reject unknown arguments.
9. Probe the no-window behaviour of a harness-run wrapper.

## Cost of this poll

Four dispatches for three answers. The first Kimi round was lost to a
shattered brief on Windows PowerShell 5.1 - a live reproduction of open
backlog item 51 - and was retried on PowerShell 7, where it succeeded.
That loss produced R9, so it was not wasted.
