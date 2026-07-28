# Fable whole-branch review — range `c6b7c85..efe4fa0`

Seat: `agents/fable-reviewer.md`, dispatched fresh. Required input to the
mode-diff debate. Subject: parallax 0.16.0, backlog items 2, 3, 5 and 6.
No frozen plan exists for this range by design; the spec baseline was
`docs/superpowers/plans/2026-07-27-0150-backlog.md` and its Resolved blocks.

Raw reply, verbatim, retained unedited.

---

### Strengths

- The `$autotriageFailure` state machine is complete on the enabled path. Tracing every branch of `tools/check-drift.ps1` with findings present: timeout sets it (tools/check-drift.ps1:537), commit failure (714), gate failure (718), untrusted run including the null-sidecar case (729-741), worktree-add failure (747), and missing `claude` CLI (770). The only two paths that leave it empty also set `$manualToast = $false` (trusted NO-ACTION at 561-567, committed fix at 706-709), and the only manual path with an empty reason is the deliberate `-NoAutoTriage` (773-783). `$errFile` is defined at 407, before the worktree add, so the stderr block at 753 is safe even on the never-started path. The claim "the plain findings toast fires only under -NoAutoTriage" holds against the code, with one semantic exception filed under Important.
- The attestation rewrite is strictly stronger, not merely different. Each rewritten test now asserts the failing field is named AND the passing fields are absent (evals/multi-model-verify/test_attestation.py:322-325, 335-338, 348-352), plus a new all-three-fail case (354-367). `Test-AttestationPasses` is byte-identical (tools/verify-attestation.ps1:43-50, context-only in the diff). The "every gate field looks valid" guard is reachable only from callers that already saw `Test-AttestationPasses` return false (tools/verify-attestation.ps1:186/195 and 205/214/219), and both functions compare the same three fields with the same operators, so the guard is a genuine self-bug-report, not a live path.
- All five new/renamed contract regions are locked whole by single pins whose bodies match the document verbatim: session-block-attribution (skills/multi-model-verify/references/backup-lane.md:56-64 pinned at evals/multi-model-verify/test_backup_lane.py:138), session-block-kind (68-74, pinned at 147), session-block-residual (75-80, pinned at 154), lane-lock (83-91, pinned at 160), rotation-guard-identity (118-124, pinned at 219). `DECLARED_REGIONS` carries the rename and all four additions (evals/multi-model-verify/test_contract_coverage.py:522-530), and the suite is green, so both directions of the inventory check hold.
- The two restoration guards are correctly framed as pinning nothing: the test says so in its own comment (evals/multi-model-verify/test_backup_lane.py:173-177), and both are `not in` comparisons, which the contract grammar reads as unlocked. They are not mistaken for locks.
- No live document still asserts the false rotation claim. The only surviving occurrence in a live contract is the explicitly quarantined historical note ending "Do not restore them" (backup-lane.md:112-117). Remaining hits are the backlog record, frozen plan records, and history fixtures, all correctly historical.
- The lock script states its own races instead of hiding them: last-writer-wins is documented at the write site (tools/kimi-lane-lock.ps1:117-121), missing or garbled stamps read as infinitely old (66-76), and the credits-death scenario reproduces the real 2026-07-21 failure end to end, including stderr propagation into the report (evals/tools/drift_statemachine_tests.ps1:844-862).
- Commit messages are lowercase imperative with no AI attribution; new PowerShell is 5.1-compatible ASCII.

### Issues

#### Critical

None.

#### Important

1. **A BLOCKED verdict is recorded as a runner failure, contradicting the field's own documentation and overstating the Resolved claim.** `tools/check-drift.ps1:724-727` sets `$autotriageFailure = "agent reported BLOCKED..."` while the comment directly above it says "That is the designed path, not a broken runner." But `commands/drift-triage.md:31-35` defines a non-empty `failure` as "the AUTOMATION itself did not finish ... and the findings were never looked at by anything. Fix the runner problem it names before trusting the next weekly run ... say in your reply that the lane was down." For BLOCKED, the agent looked at every finding, there is no runner problem to fix, and the lane was not down; the triage session will report a false lane-down. The backlog Resolved block's "There was no innocent case" (docs/superpowers/plans/2026-07-27-0150-backlog.md:160-162) overstates: BLOCKED is the innocent case the code itself names. The blocked-verdict scenario asserts neither the new toast text nor the `failure` field (evals/tools/drift_statemachine_tests.ps1:407-423), so this is also the one consumer-visible value of the field with no coverage. Fix is small: either leave `failure` empty for BLOCKED (it is a deliberate handoff) or carve BLOCKED out of the drift-triage.md paragraph.

2. **An unlabeled release frees another debate's live lock silently.** The ownership check is `if (-not $Force -and $Label -and $lock.label -and ($lock.label -ne $Label))` (tools/kimi-lane-lock.ps1:89): when the releasing caller passes no `-Label`, the check is skipped and the lock is removed with a plain "released", which is a silent `-Force`. The contract tells the driver to acquire with a label but says only "release it after the round's evidence is read" with no label mandated (backup-lane.md:84-90), so a driver following the contract literally can bare-release a lane another debate holds; two rounds then dispatch concurrently, the exact case the lock exists to remove. The 14 tests never exercise bare release against a held lock: the refusal test always passes labels (evals/multi-model-verify/test_kimi_lane_lock.py:89-96) and the idempotency test releases a free lane (115-119). Bounded damage: block attribution still catches most interleavings, and the residual region admits collisions are possible. Fix is one line (refuse a label-less release of a labelled lock without `-Force`) or one contract sentence requiring the label on release.

#### Minor

3. **Removing "more than one" from the failure bullet detached the duplicate case from its disposition.** The bullet mapping violations to "DISCARDED unread and the failure goes to the fallbacks.md consent gate" now enumerates only zero, wrong id, wrong agent path, extra tool (backup-lane.md:51). The exactly-one requirement survives inside session-block-attribution (backup-lane.md:61), so item 6's "do not relax exactly one" constraint is met, but a driver who finds two `Using LLM model:` lines inside the block has a violated requirement with no enumerated disposition. This repo's own precedent treats detection-without-disposition as a real class (the 0.14.3 F1 note at evals/multi-model-verify/test_backup_lane.py:196-200). One clause reconnecting "not exactly one inside the block" to the discard sentence closes it.

4. **The restoration guards are wording-fragile.** The absence pins (test_backup_lane.py:176-177) dodge the retained historical mention only by small deltas: "have held by accident" versus the note's "therefore held by accident", and a trailing ", so" versus ", and" (backup-lane.md:114-115). A restored claim in fresh words trips neither, and a benign rewording of the historical note could false-trip one. Acceptable for a stated non-lock, but worth knowing they guard the exact old sentence, not the claim.

5. **Breaking a malformed lock is silent.** `Read-Lock` treats an unparseable lock as absent (tools/kimi-lane-lock.ps1:52-63), so acquiring over one prints plain "acquired" with no break note, while a stale break announces itself (124-125). The backlog's "breaking a stale lock is never silent" claim technically holds, but the adjacent malformed case is the same act without the announcement.

### Ledger minors triage

No SDD ledger exists for this range by design; the backlog file is the record and carries no deferred minors. Nothing to triage.

### Assessment

Ready to merge: With fixes. The two Important findings are small, well-localized seams in otherwise sound work: the BLOCKED path contradicts the documentation shipped beside it and slightly overstates the Resolved claim, and the lock's ownership protection can be bypassed by the calling convention its own contract documents. Everything else, including the hardest claim in the range (auto-triage never fails ambiguously), verifies against the code.
