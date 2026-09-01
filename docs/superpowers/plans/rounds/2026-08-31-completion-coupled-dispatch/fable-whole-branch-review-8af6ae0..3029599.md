# Whole-branch review, `8af6ae0..3029599`

Seat: `agents/fable-reviewer.md`. Run 2026-09-01, before the mode-diff
debate, on branch `item32-detached-dispatch`. Raw reply, retained
verbatim and range-bound. The session's adjudication of each finding is
recorded separately below the reply, and the debate brief cites this
file.

---

### Strengths

- The coupling is real and proven where it matters. `tools/dispatch-round.ps1:263-338` writes one wrapper whose first act is a create-new `claim` plus `classification` reservation, whose last act is `-Classify`, and whose final statement is `exit $LASTEXITCODE`. `-Classify` at `:653-677` refuses anything but `classifying:<nonce>` for the nonce minted at `:316`, so a hand call after a kill cannot redeem the round. `evals/multi-model-verify/test_dispatch_round.py:1713-1767` drives exactly the interval Option C would have misread and asserts the wrapper exits non-zero with `exit=0` and a non-empty reply still on disk.
- The second mirror verification is made to actually bind. `test_dispatch_round.py:1865-1881` breaks only the second `@mirrorArgs` splat by index, which is the one shape that would have let the previous stale-`$LASTEXITCODE` defect pass its own test.
- `-Prepare` is fail-closed in the right order: receipt path separation, existence checks and mirror verification all run before anything is created (`dispatch-round.ps1:421-480`), the receipt is written create-new last from the same bytes that were hashed into the wrapper (`:572-579`), and the transaction's failure shape ("reserved directory, no receipt") is stated in the header (`:121-122`).
- The mirror-side fingerprint reuses the source-side algorithm through one function (`tools/new-review-mirror.ps1:538-550`), the two path refusals sit ahead of any digest work (`:671-686`), and the final back-channel sweep runs after the last writer into the mirror (`:1284-1305`). `test_review_mirror.py:2652-2681` proves the ExtraInput smuggle case refuses as a back-channel and not merely as an unmeasured mirror.
- The seal is unforgeable by omission: both binders report `sealed: "not-checked"` unless the caller supplied the digest (`tools/read-codex-round-evidence.ps1:74-80,563-580`; `tools/read-kimi-round-evidence.ps1:103-109,766-783`), and the call sites say that reading is a transport failure (`skills/multi-model-verify/SKILL.md:245-248`).
- The benefit was measured rather than asserted, including the failure surface, on both hosts, with the unobserved item (D5, console window) recorded as NOT OBSERVED rather than passing (`docs/superpowers/plans/rounds/2026-08-31-completion-coupled-dispatch/benefit-measurement.md:66-68,141-149`).
- The kimi lane's gap is stated honestly at all three sites and does not overclaim: "cannot confirm its own reviewed tree from client-reported evidence ... a known and accepted limit" with the exact fixtures swept named (`skills/multi-model-verify/references/backup-lane.md:120-133`), and the substitute binding is described as what it is, a check that "neither depends on the client saying anything about where it ran" (`:129-133`).

### Issues

#### Critical

None.

#### Important

1. **The withdrawn kill claim was corrected in `CLAUDE.md` and left standing in the shipped skill, where a test pins it.** `CLAUDE.md:63-70` now says the 600-second ceiling does not kill and withdraws "measured repeatedly through 0.21.x". The skill the session actually reads still says the opposite at `skills/multi-model-verify/SKILL.md:171-173` ("the caller's 600-second ceiling kills a crossing round with the quota spent and no reply written"), `skills/multi-model-verify/references/backup-lane.md:47-50` (same sentence), and `skills/multi-model-verify/references/model-prompting-notes.md:297-301` ("killed by the CALLER ... the quota is spent for nothing"), with the orphaned qualifier "Measured repeatedly through 0.21.x." now sitting at `:421` after five contract regions were inserted between it and the claim it qualified. `evals/multi-model-verify/test_multi_model_verify.py:1082-1086` pins the false sentence, so the suite enforces the claim `CLAUDE.md` calls withdrawn. The plan scoped Task 11 Step 1 to `CLAUDE.md` alone (`docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1993-2001`); nobody swept the skill. Sessions in other repositories read the skill, not this repo's `CLAUDE.md`. Fix: change the pin first, then state the visibility reason at all three sites.

2. **Residual 2 lost half of itself between the frozen plan and the shipped contract.** The plan's residual 2 is "a caller who reads the run-time nonce ... **or who edits the WRAPPER itself.** The digest binds the receipt; nothing binds the wrapper's own text after preparation" (`2026-08-31-completion-coupled-dispatch.md:2078-2083`, restated at `:2446`). The shipped `round-dispatch-states` region carries only the nonce case and the earlier-act-receipt case (`model-prompting-notes.md:365-375`). The wrapper-edit residual is true of the shipped code: `dispatch-round.ps1:570` writes `wrapper.ps1` and nothing hashes it afterwards, so `-ExpectedReceiptSha256`, the second verification, or the body call can be edited before the harness runs it and the round still exits 0. The region's own framing is "stated rather than fixed, because this is where a reader actually meets them"; this one is not stated where the reader meets it.

3. **The no-override mirror requirement's consequence for RESUMED rounds is stated nowhere.** The tool says "There is no override switch - every call site already uses the mirror" (`dispatch-round.ps1:96-100`), and every `-Prepare` binds `-ExpectedMirrorPath` to the path recorded at construction. Invariant B6 records that a tree change mid-debate needs a new mirror, that a new mirror at a new path makes the codex binder refuse the resumed slice on `cwd`, and that "Neither is written down anywhere yet" (`docs/superpowers/specs/2026-08-31-dispatch-invariants.md:73-96`). The branch did not write it down: the plan never mentions B6, `SKILL.md:290-291` says only "Run `-Prepare` the same way as round 1", and the kimi resume site requires "the SAME working directory" (`backup-lane.md:31,146`) with no instruction for the case where the mirror had to be rebuilt. A reader meets the requirement at the round-1 site and the trap at the resume site. One sentence at each resume site (rebuild at the SAME path with `-Force` and re-record the identity, or dispatch fresh) closes it.

4. **The open finding, `diff-mode-spec-fidelity` 4/4 to 3/4: a defect in the skill's instruction, exposed by a harness that cannot follow the new contract.** Judgement, with reasons:
   - Not the tool. The tool starts nothing and reports nothing; the round's result is the harness task's exit code, which the measurement confirms.
   - The skill's instruction is written for one shape only. Every call site says dispatch "and STOP" and then "On the completion notification for that exact task" (`SKILL.md:214,216,297,299`; `backup-lane.md:139,174,527`), and the operation region says the caller "WAITS for the harness notification" (`model-prompting-notes.md:397-408`). In an interactive session a notification opens a new turn. In a print-mode run the turn the session ends is the last one, so STOP is the end of the run. The harness preamble even tells the session the run is unattended (`evals/tools/run_behavioral_evals.py:47-53`), and the skill has no sentence for that case. The behaviour observed ("I'll wait for the background task notification") is the skill followed exactly.
   - The harness is also behind the branch. `run_behavioral_evals.py:100-105` lets the executor run only `codex:*` and three `git` subcommands, and `--tools` at `:100` exposes no task-output or wait tool. The new call path needs `tools/new-review-mirror.ps1` and `tools/dispatch-round.ps1 -Prepare` before any codex call, so the executor cannot follow the skill as written. This is item 68's class (`docs/superpowers/plans/2026-07-27-0150-backlog.md:4829-4854`), now wider.
   - What should change: (a) one sentence in `round-dispatch-operation` and at the call sites: a session must never end its turn with a dispatched round unfinished; if no notification can reach it, it waits on that task through the harness's own task-output read (still mechanism 1, not a directory poll), and if it cannot wait, it ends as a transport failure and not with a verdict-less finish; (b) the harness's allowlist and tool list updated for the mirror tool, the dispatch tool and a task wait, and the regressed transcript attached to the debate brief, since the package does not carry it and I cannot see which step the executor was refused at.
   - Blocks merge? No, on its own. The deliverable is the interactive property, measured four times; the unattended run ended without a verdict rather than with a false one, so nothing read as clean that was not. The skill sentence in (a) should go in before the diff debate because it is the shipped surface; (b) is a local opt-in gate and belongs in the backlog against item 68.

#### Minor

5. **The eval harness ships the liveness model the plan says is deleted, reading files nothing writes.** `run_behavioral_evals.py:455-530` reaps by `pid` plus `startticks` from `<dispatch-dir>/pid`, cites "the `detached-dispatch-states` region" (a dead id), and says "`dispatch-round.ps1` writes `startticks` beside `pid`". The wrapper writes `claim`, `classification`, `mirror.verify`, `body.out`, `body.err`, `exit` and nothing else (`dispatch-round.ps1:263-338`), and the plan states "No pid, no start ticks" (`:2132-2134`). The reaper is dead code with a false docstring; `test_every_cited_dispatch_region_id_resolves` cannot see it because its scope is `skills/`, `agents/`, `commands/` (`test_contract_coverage.py:611-615`).

6. **The forbidden mechanism's name is on the shipped one.** `backup-lane.md:47` heads the section "**Detached dispatch for all three calls.**" and says each call "launches through" the tool. The invariants forbid OS-detached dispatch (`2026-08-31-dispatch-invariants.md:186-202`) and the tool header says it "no longer detaches". A lane document that calls harness-tracked dispatch "detached" is how the forbidden shape gets regenerated by the next editor.

7. **Stale sentence at the codex-fresh site.** `SKILL.md:175-176`: "with the exit scaffolding added and `$d` supplied by the tool as the directory the wrapper runs in". No `$d` exists in the body; `$PSScriptRoot` is, and the paragraph two lines below says so.

8. **Residual 4 states a premise the measurement did not confirm in that form.** The region says the premise is "that a killed task reports a non-zero exit on the harness surface" (`model-prompting-notes.md:380-384`). Measured: a killed task reports `[killed]` and no exit code at all (`benefit-measurement.md:107-110,118-122`). The record is honest; the region and the call sites ("the exit code of that exact task is the result", `SKILL.md:216`) do not tell a reader what to make of a trailer with no exit code. Fail-closed by reading, but unstated.

9. **Non-ASCII in any `-Prepare` argument is silently transliterated.** `dispatch-round.ps1:570` writes the wrapper with `-Encoding Ascii`, so a path, label or host path containing a non-ASCII character becomes `?` in the single-quoted literals. Every resulting failure is fail-closed (mirror verification, relocation or `receipt-not-expected`), but the cause is opaque and no test covers it. A UTF-8-with-BOM `.ps1` would read correctly on both hosts.

10. **Step ordering in `-Prepare` spends a full mirror verification before cheap parameter checks.** Step 1a (`:462-480`) runs before host validation (`:485-495`) and before the prior-state read (`:500-507`); a typo in `-DispatchHost` costs a verification. Not a correctness issue.

11. **`skill_lint.py:105-107` still describes "the launch command, the poll command" as what each site must carry.** The paragraph at `:117-121` hedges it as a historical measurement, and `test_skill_lint_budget.py:2797-2801` pins the wording, so this is a pinned stale comment rather than a false rule.

12. **`test_wrapper_probe_record.py` asserts the withdrawn design's record as if current.** `_assert_boundary` at `:2900-2910` calls a launch that returns "under 15 seconds ... the blocking form again" a requirement; that record describes `dispatch-detached.ps1 -Launch`, which no longer exists. Harmless as an oracle for a retained record, but the module header should say the record is historical.

### Ledger minors triage

No SDD ledger exists for this cycle; there are no deferred minors to triage. The only ledger in range (`docs/superpowers/plans/rounds/2026-08-30-item32-detached-dispatch/build-ledger.md`) belongs to the withdrawn design and was retained as record.

### Sweep for "a fix that moved its defect rather than removing it"

Three instances, named above: (1) the kill claim removed from `CLAUDE.md` and left in three skill files plus its pin; (2) the wrapper-edit half of residual 2 dropped between the plan and the region that promises to state every residual; (5) the pid-plus-ticks liveness model deleted from the tool and left running in the eval harness against files that no longer exist. I found no instance inside the tool or the mirror script themselves; the session's four fix commits (`b0112ca`, `6440ffc`, `ae7a5db`, `747369a`) each close what they claim, with the one scope limit noted in item 5.

### Assessment

**Ready to merge: With fixes.** The design holds as measured and the code is sound; what needs fixing before the diff debate is contract text on the shipped surface: the withdrawn kill claim at three skill sites and its pin (1), residual 2 restored whole (2), the resume-site consequence of the no-override mirror requirement (3), and one sentence for a session that cannot receive a notification (4a). The behavioural-gate regression is real and caused here but is a skill-instruction gap plus a harness that cannot run the new call path, not a defect in the dispatch; it should be recorded in the debate brief with the transcript attached rather than block the merge.

---

## The session's adjudication

Each finding was reproduced before acceptance. Nothing here is accepted
on the reviewer's authority alone.

| # | Verdict | Evidence |
|---|---|---|
| 1 | **ACCEPTED** | Reproduced. `SKILL.md:172` and `backup-lane.md:50` still carry "kills a crossing round with the quota spent and no reply written"; `model-prompting-notes.md:421` carries the orphaned "Measured repeatedly through 0.21.x."; `test_multi_model_verify.py:1082-1086` pins the false sentence verbatim. The suite does enforce what `CLAUDE.md` withdraws. |
| 2 | **ACCEPTED** | Reproduced. Plan residual 2 (`:2078-2083`) names the wrapper-edit case; the shipped region (`model-prompting-notes.md:360-380`) carries only the nonce case and the earlier-act-receipt case. |
| 3 | **ACCEPTED** | Reproduced. Zero hits for a rebuild instruction in `SKILL.md`; B6 is recorded in the spec and written nowhere a reader of the skill would meet it. |
| 4 | **ACCEPTED, split as the reviewer proposes.** (a) is shipped surface and is fixed before the debate. (b) is the local opt-in harness and is filed against item 68. | The regression reproduces: 4/4 against the installed 0.27.0 cache, 3/4 against this checkout with `--head`, the sole miss being a verdict never issued after "I'll wait for the background task notification". |
| 5-12 | Recorded; adjudicated individually in the fix commits that follow. | |

The reviewer's sweep for this cycle's signature defect class returned
three instances rather than a clean sheet, which is the outcome the base
rate predicted and the reason the sweep was asked for explicitly.
