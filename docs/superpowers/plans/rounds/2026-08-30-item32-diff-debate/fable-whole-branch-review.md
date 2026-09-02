# Whole-branch review, verbatim

Seat: `parallax:fable-reviewer` (claude-fable-5).
Range reviewed: base `8af6ae0456b275e1f8a700bc479cbc19af69c6e8` to head
`98c8a75`. The diff package handed to it was cut at `be2da46`, one commit
earlier, which added only the build-ledger paragraph naming the behavioural
confound.
Dispatched 2026-08-31, before the diff debate's round 1, as the flow
requires.

This file is the reviewer's raw reply, unedited. The session's per-finding
adjudications are in `build-ledger.md` under "The whole-branch review, and
what it changed"; the round-1 brief cites this artifact.

---

### Strengths

- **The completion model is fail-closed end to end.** `tools/dispatch-detached.ps1` has exactly one exit-0 path (`reply-present`, line 756 area; `Get-ExitCodeForState` at :542-546), RUNNING is a distinct exit 3, and every receipt-read failure folds to `no-receipt` at exit 1 via `Get-ReceiptRecord`'s catch-all returns (:420-488). The liveness check short-circuits before any terminal artifact is read (:622-628), and `test_poll_reports_running_while_the_pid_is_alive` (evals/multi-model-verify/test_dispatch_detached.py:825-841) proves the short-circuit rather than assuming it, by planting a premature reply the poll must not surface.
- **The receipt-last transaction is enforced, not described.** Separation and freshness are checked before anything is created (:674-687), the receipt write is `FileMode::CreateNew` (:756-763), and the hold-barrier seam makes the kill-between-start-and-publish race deterministic (`test_a_hard_kill_between_start_and_publication_is_never_success`, test_dispatch_detached.py:598-624). The ORDER_WRAPPER test observes pid, marker, receipt ordering from inside the child by content, not timestamps (test_dispatch_detached.py:536-555).
- **Oracles that can fail.** The wrapper-probe oracle mutates a scratch copy and reruns the SAME assertion function (test_wrapper_probe_record.py:test_the_oracle_can_fail_on_a_changed_value), the extractor has a zero-match negative self-test, and the console-encoding line has a red demonstration scoped to the one host that reproduces it (test_wrapper_renders_and_parses.py:test_deleting_the_console_encoding_line_breaks_the_byte_oracle). The `CREATE_NEW_CONSOLE` isolation note in `run_wrapper` records a real measured cross-test contamination mechanism.
- **The hook-suppression fix is verified by trace, not by absence of failure.** `GIT_TRACE2` proves both `git add` and `git commit` carry `core.hooksPath`, and the directory is asserted empty, in the mirror, and correctly shaped (test_review_mirror.py:1332-1375); non-empty and file-occupied paths both block (tools/new-review-mirror.ps1:1083-1098).
- **The ledger is honest.** The behavioural confound is stated with counts and explicitly not claimed as a finding (build-ledger.md:149-170), and the `| tail` trap firing twice is recorded against the session itself (build-ledger.md:84-87).

### Issues

#### Critical

None found.

#### Important

1. **The dual-host CI job never runs the branch's core test modules.** `.github/workflows/skill-evals.yml:97-108` and :114-125 carry a hardcoded module list per host; the branch adds two Windows-only PowerShell-facing modules (`test_dispatch_detached.py`, `test_wrapper_renders_and_parses.py`) and touches the workflow nowhere (absent from the 104-file diffstat). On the Linux tier-2b job both modules skip (`os.name != "nt"`, test_dispatch_detached.py:196-200), so after merge NO CI job executes the dispatch tool's suite on any host. This is the exact 0.16.0 class the `powershell-hosts` job exists to prevent, and CLAUDE.md's claim that the job "re-runs every PowerShell-facing test module" becomes false on this range. Class sweep: I checked every new/changed test module for the same gap; `test_review_mirror.py` (new hook tests) is already in both lists, and `test_wrapper_probe_record.py` / `test_backup_lane.py` / `test_multi_model_verify.py` additions are pure-text pins that run in tier 2b. No other instance.
2. **A corrupted, unrecorded root `AGENTS.md` entered the range.** The diffstat's first line adds `AGENTS.md` (+207), yet no commit subject, no plan task, no ledger row, and no line of the dispatch summary names it. Its content is a mechanical rebrand of CLAUDE.md that produces false instructions: "Codex plugin" (AGENTS.md:1,3) and the broken commands "`Codex plugin marketplace update parallax`" / "`Codex plugin update parallax@parallax`" (AGENTS.md:94-95). It is also stale against this branch's own CLAUDE.md edit: it lacks the new dispatch-tool paragraph (no `dispatch-detached` match anywhere in the file). A root AGENTS.md is, by this skill's own contract, an instruction back-channel; whatever the intent, an instruction file that misinstructs cannot ship uncorrected and unrecorded. (I could not run `git log` under this tool grant to name the introducing commit; that attribution is a gap the session should close.)
3. **The behavioural-eval reaper kills by pid alone, violating the branch's own pinned invariant.** `evals/tools/run_behavioral_evals.py:478-493` reads each `pid` file, waits up to 20s, then `taskkill /PID <pid> /T /F` with no start-time check; the file `startticks` sits beside `pid` in the same dispatch directory and is never read (no `startticks` reference in the file). The branch's own contract region states "liveness is PID PLUS START TIME, never a pid alone" (skills/multi-model-verify/references/model-prompting-notes.md, detached-dispatch-states region), so a recycled pid here force-kills an unrelated process tree. Class sweep for pid-alone kills: `cleanup_dispatch_pid`/`kill_pid_best_effort` in test_dispatch_detached.py:390-408 is the same shape with a much tighter window (teardown of a process launched seconds earlier); the tool's own catch kill uses a pid read race-free off the CreateProcess handle (not an instance); the operation region's operator `taskkill` guidance applies only after a poll that verified ticks (not an instance).

#### Minor

1. **One handled-failure path leaves a started tree alive, against the pinned sentence.** If `GetProcessTimes` fails, `LaunchDetached` throws AFTER the child exists (tools/dispatch-detached.ps1:391-398 in the C# block) and discards `pi.dwProcessId`; the PowerShell catch's `if ($launchedPid)` (:765-767) is then null, so no kill runs, contradicting "a failure at any point after the process starts kills the tree" (script header and the pinned tool region). Practically unreachable on a valid handle, but the C# could terminate the child before throwing. Same-class check: the `$parts`/`[int]` conversion at :720-722 shares the window; every other throw path precedes process creation.
2. **Unknown-parameter invocations bypass the hand-rolled exit-2 promise.** A typo'd switch (for example `-Reciept`) fails in the host's `-File` binder before the script's own mode checks (:567-580) run, so the exit code is whatever the binder chooses, with no state name on stdout. `test_a_malformed_invocation_exits_two` (test_dispatch_detached.py:966-978) covers only no-args, both-modes, and incomplete-poll. Untested edge, unverified here (read-only grant).
3. **The budget-raise justification is stale on arrival.** `evals/tools/skill_lint.py` comment says "Budget set at the measured baseline rounded up" (the 6225 measurement), but the ledger records the body at 6356 after Task 6, already over the new 6250 budget and warning again (build-ledger.md:77-80). The self-quoting-count class; bind the figure to its commit or restate as an invariant.
4. **The reaper's liveness probe is a substring match.** `str(pid) not in listed.stdout` (run_behavioral_evals.py:484-486) can substring-match a different, longer pid and keep waiting; it converges to a harmless taskkill of a dead pid, so it only wastes the grace period.

### Ledger minors triage

- **Task 1 launch mechanism drift (`CreateProcess` not `Start-Process`):** ride. The plan froze a mechanism its own tests cannot pass against; the session reproduced the 12.4s vs 0.2s measurement independently. The deviation IS the fix; the debate should ratify it.
- **`$receipt`/`$Receipt` collision:** ride. Fixed in-branch (`$rec`), recorded, same class as item 48's `$s`/`$S`.
- **Budget raise beyond the authorized ceiling raise:** ride, with Minor 3 as the fix-worthy residue. Strict lint exits 0 on a warning per the ledger, so the raise changed no gate outcome; it widened the early-warning line unasked, and the debate should ratify the number knowing the body is already 6356.
- **Task 4/6 frozen-plan defects (backslash mandate, contradictory test):** closed at `45a87c0` with both blanket gates restored whole; ride.
- **`prompt_bytes_match` pinned FALSE:** ride. Pinning the measured value with the load-bearing `prompt_sha256_matches` pinned true is exactly right, and the pin's failure direction (a future byte-exact transport turns it red on purpose) is stated.
- **Behavioural gate: residual non-dispatch scratch leak, and the OPEN `diff-mode-spec-fidelity` confound:** ride. Both are recorded without a causal claim, and the like-for-like comparison is structurally impossible before the post-debate version bump.

### Assessment

**On the central question:** I searched for exit-0 paths other than `reply-present`, catch blocks that could convert a failure into success, reply reads reachable while the pid is live, stale-artifact reuse paths, and seam effects that relax a classification. I found none: an interrupted launch lands on `no-receipt`, a killed tool on `no-receipt` with the tree either killed or admitted as the documented residual, a hung round on `running`/exit 3, a dead wrapper with a live orphan on `no-exit-file`/`exit-nonzero`, and both env seams can only make outcomes more conservative. The class the plan exists to close is closed on this range; the one place the branch itself violates its own liveness rule is the eval reaper (Important 3), which is a teardown, not a completion path.

**Ready to merge: With fixes.** Fix before merge: wire the two new modules into both host lists of `powershell-hosts` (Important 1) and either remove or correct-and-record the root `AGENTS.md` (Important 2); fix the reaper's start-ticks check (Important 3) with them or as an immediate follow-up. The tool, its contract, and its tests are the strongest artifact this repo has shipped in this class; the defects found are all in the scaffolding around it, not in the completion model.
