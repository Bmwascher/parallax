• Now let me look at the actual shipped code to ground the analysis — the reverted item 32 build that Option C is carved out of.

• Now let me check the wrapper mechanics — who writes `exit` and `reply`, and in what order — since C's R8-by-construction claim depends on it.

• I have read all three briefed documents in full, the shipped tool (`tools/dispatch-detached.ps1`, the reverted item 32 build), and the wrapper/call-site contract in `skills/multi-model-verify/SKILL.md`. Answers in order.

  ## 1. Attack on C's central claim

  **The claim**: a fresh, never-reused dispatch directory plus a create-new execution claim replaces the liveness model for R8 ("a killed, hung, or unfinished round must never read as a completed one", costing doc `2026-08-31-dispatch-options-costing.md:32-33`).

  **Shapes I searched for, and what I found in each:**

  **(a) The reproduced ESCALATE race — second run reported as first run's completion.** That defect needed a *live, unfinished second execution* whose identity writes raced the poll (ESCALATION.md:19-28; invariants `2026-08-31-dispatch-invariants.md:88-104`). Under C the second run fails at the create-new claim, its first act, *before it can write anything* (costing doc:117-119). There is no window in which an unfinished second execution exists. If run A completed and someone re-runs the wrapper, poll still returns `reply-present` — but that is now a *true* statement about the only execution of that prepared round. The rerun is a rejected duplicate, not a round. **No false completion found.**

  **(b) Stale reply inherited from an earlier attempt.** `-Prepare` refuses an existing directory (costing doc:114, 135-136), and the current tool already reserves with no `-Force` (`tools/dispatch-detached.ps1:691-697`) and writes the receipt create-new (`tools/dispatch-detached.ps1:756`). A fresh directory cannot contain an old reply. Structural, as claimed. **None found.**

  **(c) Killed or hung mid-flight.** The wrapper writes `exit` only at its end, after the client process has exited and written `reply` (SKILL.md:204-207: `codex ... --output-last-message $PSScriptRoot/reply`, then `$code = $LASTEXITCODE`, then `WriteAllText("$PSScriptRoot/exit")` in the final line). A killed wrapper never reaches that line → `no-exit-file`, non-zero. A hung wrapper the same. **None found — but see the caveat below.**

  **(d) Torn writes.** A torn `exit` fails the integer parse → `exit-unreadable` (`tools/dispatch-detached.ps1:513-516`). A torn `reply` with `exit=0` is unreachable *given the ordering in (c)*, because `exit` is written only after the client process that wrote `reply` has exited. **None found, conditional on that ordering.**

  **(e) Forged claim / claim-only completion.** `no-claim` is checked before exit/reply states (costing doc:130-132), and claim presence alone can never reach `reply-present` — a fresh directory has no reply until an execution writes one. **None found.**

  **(f) Caller-confusion residue.** The admitted residual — a caller supplying an earlier attempt's receipt, directory, and label gets that attempt's result (`tools/dispatch-detached.ps1:49-57`) — persists unchanged under C. It is caller confusion about all three inputs at once, not a tool misclassification, and liveness never addressed it either.

  **One gap in the argument as written — not a counterexample, but a silent dependency.** C's R8-by-construction proof depends on the wrapper's write ordering (claim first; `exit` strictly last, after the client exits) and that ordering appears *nowhere* in the costing doc. It exists today in the wrapper body (SKILL.md:194-208) by inheritance, not by requirement. A future wrapper edit that moved the `exit` write into a `finally` that runs on a killed pipeline, or that wrote `exit` before the client finished flushing `reply`, would re-open exactly the class C claims to close — and no stated invariant would catch it. The ESCALATE reviewer made the same point about names: a state must never read as "safe to start again" (ESCALATION.md:102-107); under C, recovery from `no-exit-file` must be re-*prepare* (the claim will refuse a re-run), and that too is currently unstated.

  **Verdict on Q1: I searched shapes (a)-(f) and found no path where an unfinished or killed round reads as `reply-present` at exit 0 under C, given the ordering the current wrapper already has. The claim stands, but its load-bearing precondition is undocumented.**

  ## 2. Losing "running versus crashed"

  Acceptable, and the costing doc actually *overstates* the loss. It says the answer "now lives only in the harness's notification" (costing doc:149) — but the notification is not the only harness signal. Mechanism 1 gives a **named task row** (invariants:39-40, 155) and the settled rule requires the round to be "a harness-tracked task with a lane-and-round name" (invariants:179-182). A task row is queryable mid-session: it *is* a running-versus-finished distinction, maintained by the harness with no pid files, no start ticks, no per-host process APIs. The true residue is narrower than stated: the distinction is lost only when the notification is missed **and** the task row is gone — i.e., after a session restart — and under R7/D3 (invariants:132-141) a round is presumed dead at that point anyway.

  The remaining real cost is operational, not classificatory: on a missed notification the session may re-dispatch a round that is in fact still alive, spending quota twice and producing two completed replies for one slot. Both replies then pass through the E1 binder, so this is muddle and waste, not false attribution — provided the plan states the recovery procedure (check the task row; bounded grace; re-dispatch as a **new** prepare; treat a late first-round reply as new evidence requiring explicit binding, per invariants:206-216 and the re-dispatch rule at invariants:199-200). Conservative direction holds throughout, as the doc claims (costing doc:142-145).

  ## 3. A fourth option?

  **Option D: C, but the harness output file replaces the wrapper-written `exit` file.** The measured harness contract already delivers "stdout and stderr, and a trailer naming its exit code" (costing doc:42-43). The trailer is written by the harness after process death — it cannot be torn by a kill and cannot precede the client's exit — so it provides the ordering guarantee of section 1(d) *by harness construction*, deleting the undocumented dependency I flagged above. Keep: prepare, claim, receipt, `reply` file in the dispatch dir (the harness file interleaves stdout and stderr, so `reply` must stay separate from the transcript — that rules out the purer "reply to stdout" variant). Cost against the requirements: R1-R7 unchanged; R8 arguably *stronger* (ordering guaranteed by the process owner); **new cost** — the classifier parses a harness-internal trailer format that is measured today but not pinned across harness versions, which sits badly with F2/E5 (invariants:226-229, 240-241: a contract must describe the mechanism that actually holds, and an unmade measurement must not look like a clean one), and when a notification *is* missed the session must rediscover the output path from the task row — unmeasured. Net: a genuine refinement, roughly a wash, not clearly better. Worth costing in the plan; not a precondition for shipping C. I am speculating on the trailer format's stability — no measurement of it across versions exists in the repo.

  The cheaper "fourth option" is procedural and I recommend it outright: **C plus a session-side recovery rule that queries the harness task row** to recover running-versus-crashed (per Q2). No process APIs, no self-launched process, nothing the settled rules forbid.

  ## 4. The requirements

  - **Missing: the write-ordering invariant** (Q1). R8's "by construction" silently assumes claim-first and exit-last. It must be stated, and tested with a kill-between-claim-and-exit test and a rerun-refusal test — the same test shapes the invariants doc already demands for C2 (invariants:252-254).
  - **Missing from R1-R8: the interpreter and environment contract.** A3/A4 (invariants:33-47) are measured and the invariants doc orders the plan to settle them (invariants:251), yet the costing doc's "environment this must work in" list omits them entirely. The current call site re-executes the caller's own host (SKILL.md:239-243); under mechanism 1 the harness command line must name `pwsh`/flags explicitly or A3's PS5.1 silent-downgrade returns.
  - **R4 conflicts mildly with the invariants.** "ONE backgrounding method, everywhere" (costing doc:24) vs. the mechanism-4 carve-out for background subagents (invariants:165-169). R4 should read "one method for review-round dispatch."
  - **Missing: a hung-round policy.** R8 classifies a hung round correctly (non-zero forever) but nothing bounds how long a hung harness task sits before kill-and-re-dispatch. Minor, but unnamed.
  - **Missing: call-site migration.** Exit 3 (`running`) is part of the shipped poll contract at both call sites (SKILL.md:234, 325; `tools/dispatch-detached.ps1:67-74`). C deletes the state; no requirement says the poll loops keyed on it must be rewritten. Unstated, this is how a stale exit-3 loop survives into the new design.
  - **R5 under mechanism 1 is assumed, not measured.** Popups were measured only for the redesign's own spawning (invariants:184-188). The harness's own spawn behaviour for a wrapper-shaped background command has not been probed for window creation. Per the doc's own rule (invariants:13-15), keep it UNMEASURED until probed — cheap to fold into the D1 probes already demanded (invariants:261, 179-182).

  ## 5. Ship or not

  **Ship C.** The central claim survives attack; the deleted machinery is exactly the machinery that produced the reproduced race (costing doc:155-157), and the reviewer whose ESCALATE stopped B explicitly prescribed the claim C keeps (ESCALATION.md:45-48). The smallest changes I require in the plan, none of which alter the option:

  1. Promote the wrapper write-ordering (claim create-new as first act; `exit` written strictly after client exit, never in a `finally` reachable by a kill) from incidental to stated invariant, with the kill-mid-round and rerun-refusal tests.
  2. State the recovery rule: `no-exit-file` is never "safe to re-run"; recovery is a fresh `-Prepare`; the harness task row is the running-versus-crashed oracle.
  3. Rewrite the exit-3 poll contract at both call sites (SKILL.md:234, 325) in the same plan.

  PASS.
