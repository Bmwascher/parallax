## Verdict

The revised plan still has two merge-blocking defects: one false-completion path and one silent wrong-directory path. Task 1a is not built at `937bcb0`; the checked-out tool still has no `-WorkingDirectory` parameter (`tools/dispatch-detached.ps1:220-233`).

### 1. Central invariant: duplicate execution can return false completion

The identity file is sound only under an unstated single-execution assumption.

All five planned wrappers overwrite `pid` and then separately overwrite `startticks` (`docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:348-351`, `:420-423`). The tests measured a 15–30 ms gap between those writes (`evals/multi-model-verify/test_dispatch_detached.py:141-150`), but neither plan nor wrapper atomically claims the prepared directory.

If the wrapper is launched twice:

1. B can overwrite `pid` while `startticks` still belongs to A.
2. A can finish and leave `exit=0` plus a reply while B remains live.
3. The mismatched identity is classified DEAD (`tools/dispatch-detached.ps1:375-392`).
4. Poll then accepts A’s terminal artifacts and returns `reply-present`, exit 0 (`tools/dispatch-detached.ps1:483-515`), even though B remains capable of changing them.

The existing recycled-PID test proves that the dangerous latter half is intentional behavior: mismatched live PID plus old terminal artifacts returns success (`evals/multi-model-verify/test_dispatch_detached.py:689-707`).

The receipt binds a prepared directory, not a particular execution inside it. Fix this before Task 3 with a create-new execution claim or, preferably, one create-new identity record containing PID plus ticks. A duplicate must fail before reaching any shared terminal-artifact `finally`. Add concurrent-double-start and rerun-after-completion tests on both hosts.

I found this same instance in all two codex and three Kimi wrapper shapes. I found no other false-completion path in the single-execution state order.

### 2. The `cwd` remedy still silently falls back

The proposed line is:

`docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:351`

```powershell
Set-Location -LiteralPath (...)
```

It lacks `-ErrorAction Stop` and sits before the wrapper’s `try` (`:352-354`). I measured both PowerShell 5.1 and 7: when the recorded directory no longer exists, `Set-Location` prints an error, continues in the original directory, and the process exits 0. That recreates the exact real-repository fallback Task 1a exists to close.

This can happen when the mirror exists during Prepare but is removed or becomes inaccessible before execution. The current proposed tests cover nonexistent-at-prepare, missing `cwd`, and the happy path (`docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:198-237`), but not this post-prepare race.

At minimum:

- Require a FileSystem-provider directory during Prepare. Merely requiring a PowerShell “container” is insufficient (`:255-257`); both hosts can enter `HKCU:\` while native-child cwd remains the prior filesystem directory.
- Use `Set-Location -ErrorAction Stop`.
- Add a test that deletes the mirror after successful Prepare, starts the wrapper from the real repository, and proves the client body never runs.
- Test blank, unreadable, non-filesystem, deleted-target, and wrong-existing-path `cwd` values.

### 3. The `cwd` file is not bound to the receipt

Fresh directory reservation prevents an initially stale `cwd`, but nothing prevents it from being changed after Prepare. The receipt currently binds only directory, token, round, and placeholder ticks (`tools/dispatch-detached.ps1:28-38`, `:248-320`), while Poll independently checks only directory and round (`:449-452`).

Therefore:

- A mutated `cwd` can redirect a round after its receipt was committed.
- A wrong-but-existing `-WorkingDirectory` supplied at Prepare is never independently detected.
- Merely checking that `cwd` exists/readable does not establish that it still contains the prepared value.

Add the canonical working directory—or its hash—to the external receipt, require `-ExpectedWorkingDirectory` on Poll, and compare the `cwd` artifact with both. This gives it the same independent binding already considered necessary for directory and round.

For codex, also bind the transcript’s reported `workdir:` to the review mirror before accepting the reply. Task 6 currently does not record a working-directory result (`docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:487-499`).

### 4. `not-started` is wrong for missing `cwd`

The original three-way collapse—never launched, died before PID publication, or alive just before PID publication—is conservative for the narrow question “is this a result?” It is not operationally identical: the live case should wait, while the first two are failures. Since ordinary transport failure receives an automatic retry (`skills/multi-model-verify/references/fallbacks.md:28-50`), the skill should require checking the tracked-task status before retrying `not-started`.

Missing `cwd` is a different condition again. Because the receipt is written last, a valid receipt proves the `cwd` artifact once existed. Its later absence means committed-dispatch corruption, analogous to a lost marker—not “never started.”

Use a separate `cwd-unreadable`/`working-directory-unavailable` state, or deliberately broaden `launch-unknown`. It should precede PID inspection and exit 1. A readable file whose target is no longer a filesystem directory belongs in the same state.

### 5. The plan no longer truthfully describes its commits

The revised Task 1 says KEEP `-WorkingDirectory` (`docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:136-145`), while Task 1a correctly records that executed Task 1 told the implementer to drop it (`:183-190`). The built parameter block confirms Task 1 dropped it (`tools/dispatch-detached.ps1:220-233`).

Do not rewrite completed Task 1 retroactively. Restore its executed text, place the corrective task chronologically after built Task 2, and record the deviation.

The downstream reconciliation is also missing:

- Built Task 2’s pinned tool/state contracts contain no `cwd` contract (`skills/multi-model-verify/references/model-prompting-notes.md:302-393`).
- Task 3 still says `-Prepare` has “all four parameters,” omitting mandatory `-WorkingDirectory` (`docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:336-338`).
- The stashed codex commands likewise omit it; the current per-site oracle’s exact command has no working directory (`evals/multi-model-verify/test_multi_model_verify.py:1022-1027`).
- Task 5 checks identity but does not require all five rendered wrappers to relocate from a deliberately wrong starting directory (`docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:452-468`).
- The spec says the lost round is recorded in the ledger (`docs/superpowers/specs/2026-08-31-tracked-background-dispatch-design.md:88-96`), but I searched the complete 284-line ledger for `WorkingDirectory`, working directory, `cwd`, void, and `937bcb0`; no record exists. Its latest section records only the premise correction (`docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/build-ledger.md:238-284`).

### 6. Another launcher responsibility was deleted without adjudication

The old launcher fixed an entire execution envelope: current PowerShell executable, `-NoProfile -NonInteractive`, empty stdin, stdout/stderr targets, and working directory (`tools/dispatch-detached.ps1@0105d3a:712-719`). Task 1a restores only cwd.

The new plan never supplies the exact tracked wrapper command. Its test helper uses a chosen PowerShell host plus `-NoProfile -NonInteractive` (`evals/multi-model-verify/test_dispatch_detached.py:118-125`), but the plan merely says “run the prepared wrapper.”

This is load-bearing:

- The existing skill records that a bare `powershell` silently changes a PowerShell 7 caller to 5.1 (`skills/multi-model-verify/SKILL.md:239-243`).
- `-NonInteractive` prevents an unattended wrapper from waiting for input.
- `stdin.empty` is still created (`tools/dispatch-detached.ps1:566-568`) but nothing in the new spec or plan connects it to the wrapper.

Specify and pin the exact per-site wrapper command, including current-host selection, `-NoProfile`, `-NonInteractive`, wrapper path, and the background-task setting/name. For `stdin.empty`, either prove the harness closes stdin and delete the dead artifact, or wire an equivalent closed-input guarantee. Stdout/stderr moving to the visible harness task can be intentional, but state that explicitly.

### 7. Optional-switch typo: yes, an invalid call can answer instead of refuse

I ran a fully bound Poll with `-Jsoon` instead of `-Json` on both hosts. Both executed Poll and emitted plain `no-receipt`, exit 1, rather than refusing.

On a completed receipt, the same invalid invocation reaches `reply-present` and exits 0; `-Json` changes only serialization (`tools/dispatch-detached.ps1:395-408`, `:515`). Thus an invalid invocation can report success while omitting the JSON round field. A valid Prepare with typoed `-Json` can likewise create the dispatch and exit 0 with plain output.

Reject nonempty `$args` before mode execution and test a fully valid Prepare and Poll with a typoed optional switch. The plan’s no-mode `-Reciept` probe does not exercise this (`docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:154-162`). The spec’s claim that the host rejects such switches remains false (`docs/superpowers/specs/2026-08-31-tracked-background-dispatch-design.md:161-172`).

### 8. Task 3 budget

The old stash is no longer the relevant measurement. Applying the two `Set-Location` lines and two mandatory `-WorkingDirectory` arguments in memory raises it from about 6610 to about 6695 estimated tokens.

Use the reference-file option:

- Move branch/debate history and rationale out of `SKILL.md`.
- Keep the complete operational shape independently in both codex sections: single-use identity, strict cwd relocation, Prepare including `-WorkingDirectory`, exact tracked wrapper command, Poll, and full exit mapping.
- Do not globally deduplicate the two call sites.

The historical material at `skills/multi-model-verify/SKILL.md:234-243` is already about 200 estimated tokens; move more than the bare minimum so the body does not land against 6500 again. The cost is one extra reference hop for rationale, while the executable contract remains local. The reference is already required.

Keep the budget at 5250 and ceiling at 6500 (`evals/tools/skill_lint.py:117-127`). Raise the ceiling only if non-operational relocation still cannot fit; a ceiling raise does not itself consume tokens, but it weakens the hard growth guard.

### 9. Visibility and durability

The three old launcher findings are correctly disposed of, not dodged: the launcher symbols are gone and the test enforces their absence (`evals/multi-model-verify/test_dispatch_detached.py:317-327`). The problem was deleting the launcher without inventorying all its other responsibilities.

A two-process design can preserve both visibility and survival: a tracked supervisor launches a detached worker and waits/polls it. If the session dies, the worker survives; while the session lives, the supervisor supplies the named task and completion notice. That restores considerable complexity—two identities, cancellation forwarding, orphan reconciliation, and launcher failure paths—so the user’s tracked-only trade remains reasonable.

But measure it. Task 6 still does not retain evidence for task-row naming, immediate conversation return, completion notification, cancellation, or session termination (`docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:479-499`). The naming oracle explicitly admits it is prose-only (`evals/multi-model-verify/test_multi_model_verify.py:1241-1255`).

### Sweep result

I searched:

- receipt freshness/schema and expected directory/round;
- marker/token loss and substitution;
- missing, partial, malformed, recycled, overwritten, and duplicate identity;
- death before PID, between PID/ticks, before cwd, during client execution, and around exit/reply writes;
- sequential retry and concurrent duplicate wrapper execution;
- missing, blank, unreadable, mutated, non-filesystem, deleted-target, and wrong-existing `cwd`;
- every old launcher parameter and launch-envelope responsibility;
- optional-switch binding on both hosts;
- all five planned wrapper shapes.

The duplicate-execution race is the central false-completion instance, repeated across all five wrappers. The cwd fallback and unbound cwd are separate wrong-review/back-channel defects. I found no additional false-completion path under the single-execution assumption.

**FIX**