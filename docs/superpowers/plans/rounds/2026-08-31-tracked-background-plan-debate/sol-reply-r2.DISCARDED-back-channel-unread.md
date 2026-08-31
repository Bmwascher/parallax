## Verdict

I found a concrete false-completion path. The new mechanism is not ready to resume building.

### Blocking findings

1. **A duplicate or retried wrapper execution can read as completed while another execution is still running.**

The receipt binds the dispatch directory, but it does not bind a particular execution within that directory. Every planned wrapper overwrites `pid` and then separately overwrites `startticks` (`docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:237-241`, `:310-312`). The tests measure a real 15–30 ms gap between those writes (`evals/multi-model-verify/test_dispatch_detached.py:141-150`).

If the prepared wrapper is run twice, concurrently or after an earlier completion:

- execution B can overwrite `pid` while `startticks` still identifies A;
- A can leave `exit=0` and a nonempty reply while B remains live;
- the mismatched pair is classified DEAD (`tools/dispatch-detached.ps1:375-392`);
- `-Poll` then reads the stale terminal artifacts and returns `reply-present`, exit 0 (`tools/dispatch-detached.ps1:483-515`).

The existing recycled-PID test demonstrates exactly the dangerous second half: a live PID plus mismatching ticks falls through to old `exit`/`reply` and succeeds (`evals/multi-model-verify/test_dispatch_detached.py:689-707`).

Therefore, a file inside the receipt-bound directory is a sound identity anchor only if it is immutable and single-writer. This one is neither. The directory binds the prepared attempt, not which execution populated its mutable artifacts.

Fix before Task 3:

- The wrapper’s first act must atomically claim the prepared directory using create-new semantics.
- A losing duplicate must fail before entering any `finally` that could overwrite shared `exit`.
- Prefer one create-new identity record containing PID plus ticks, or a create-new execution claim followed by the current pair.
- Add concurrent-double-start and rerun-after-completion tests on both hosts. Assert that exactly one client body runs and that success cannot become mutable afterward.

The class repeats in all five planned wrappers: both codex sites and all three Kimi sites. I found no single-use claim in the spec, plan, tool, or tests; create-new is currently used only for the receipt (`tools/dispatch-detached.ps1:588-605`).

2. **The plan never verifies its central visibility outcome.**

The spec promises a named task row, completion notice, and continued conversation access (`docs/superpowers/specs/2026-08-31-tracked-background-dispatch-design.md:88-100`). But Task 6 records only prepare/state/encoding fields (`docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:376-388`). The “documented outer command” test explicitly substitutes an ordinary `Popen` process for harness tracking (`evals/multi-model-verify/test_dispatch_detached.py:911-914`), while the naming test admits it is documentation-only and that nothing enforces the name (`evals/multi-model-verify/test_multi_model_verify.py:1241-1255`).

This is the same methodological failure that produced the original false premise: the defining harness behavior is asserted but not measured. Add a retained live probe covering:

- immediate return of conversation control;
- the exact lane-and-round task name shown;
- completion notification;
- stop/cancellation behavior;
- session termination behavior.

Tasks 3 and 4 should also give the exact wrapper invocation and literal background-tool setting, not merely instruct the implementer to “run it as a tracked background command” (`docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:227-230`, `:298-300`).

### Other plan/spec defects

- **The spec incorrectly says the completion model and receipt transaction are unchanged.** It says that twice (`docs/superpowers/specs/2026-08-31-tracked-background-dispatch-design.md:3-7`, `:46-57`), but the receipt now precedes execution, its `startTicks` is a meaningless zero, and liveness trusts a later mutable sidecar (`tools/dispatch-detached.ps1:36-38`, `:478-483`, `:588-596`). That is a completion-model change and must be reviewed as one. The contradictory framing likely caused the missing duplicate-execution case.

- **A typoed optional switch is silently accepted.** The only optional switch is `-Json` (`tools/dispatch-detached.ps1:220-233`). I ran a fully bound `-Poll` with `-Jsoon` on both hosts: both executed the poll and emitted plain output instead of refusing. On a completed receipt, the same path can return plain `reply-present` with exit 0 because JSON affects only serialization (`tools/dispatch-detached.ps1:395-408`). It would omit the JSON round echo while treating an invalid invocation as successful.

  The spec’s host-rejection explanation remains false (`docs/superpowers/specs/2026-08-31-tracked-background-dispatch-design.md:135-146`), and the plan’s no-mode `-Reciept` experiment cannot detect this (`docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:154-162`). Reject nonempty `$args` explicitly and test an otherwise-valid invocation with a typoed optional switch.

### `not-started`

Its ordering is correct: receipt, expected directory/round, marker and token are validated first, then missing PID becomes `not-started` (`tools/dispatch-detached.ps1:444-480`). It is non-success, so it is conservative for the central invariant.

Collapsing the three situations is safe only for the question “is this a result?” It is not sufficient for recovery:

- never run or died before publication implies failure/retry;
- a live wrapper before PID publication implies wait;
- yet the contract calls every non-running/non-success state a transport failure (`skills/multi-model-verify/references/model-prompting-notes.md:378-384`), which normally triggers an automatic retry (`skills/multi-model-verify/references/fallbacks.md:28-50`).

Either rename it to `identity-not-published` and require consulting the tracked-task status before retrying, or explicitly document that qualification. Also, death after PID but before ticks currently becomes `pid-unreadable`, not `not-started` (`tools/dispatch-detached.ps1:470-480`), so “died before publishing identity” is broader than the implementation.

### Task 3 ceiling

Move non-operational branch history and rationale from `SKILL.md` into the already-required `model-prompting-notes.md`; keep the complete executable shape independently inside both call-site sections.

For example, the current historical discussion at `skills/multi-model-verify/SKILL.md:234-243` is approximately 200 estimated tokens—enough to recover the roughly 110-token overage without weakening either site’s wrapper, prepare, background, poll, or exit mapping. The cost is modest cross-file indirection for rationale, not operation; that reference is already required.

Do not globally deduplicate the per-site commands, because the plan correctly records why that failed (`docs/superpowers/plans/2026-08-31-tracked-background-dispatch.md:262-270`). Do not raise the ceiling first. If the body remains over 6500 after relocating historical text, then a measured and pinned ceiling raise is defensible. The budget is correctly back at 5250 and the ceiling at 6500 (`evals/tools/skill_lint.py:117-127`).

### The tracked-versus-detached trade

The three launcher findings were correctly disposed of, not dodged: the launcher symbols are absent, and the test mechanically enforces their deletion (`evals/multi-model-verify/test_dispatch_detached.py:317-327`).

The durability trade is real for this one-process design, but not fundamental. A tracked supervisor could start a detached worker and remain alive to report its status. If the session dies, the worker survives; while the session lives, the supervisor supplies the task row and notification.

That costs substantially more: two identities, two failure domains, cancellation forwarding, orphan reconciliation, and much of the launcher complexity just deleted. The simpler tracked-only choice is reasonable given the user’s preference—but “probably dies with the session” (`docs/superpowers/specs/2026-08-31-tracked-background-dispatch-design.md:166-176`) must be measured, not frozen as another inherited belief.

### Sweep result

I searched receipt absence/schema/freshness, expected directory and round, marker/token substitution, missing/partial/malformed identity, live and recycled PID, death before and after each artifact write, orphan clients, terminal-file ordering, sequential retry, concurrent duplicate execution, wrapper rerun, and optional-parameter binding.

Beyond the duplicate/single-use flaw repeated across all five planned wrappers, I found no other false-completion path in the single-execution state order. I found no additional Task 1/2 implementation drift beyond the plan/spec defects above.

**FIX**