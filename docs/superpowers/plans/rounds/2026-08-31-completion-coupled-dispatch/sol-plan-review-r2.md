The plan is not yet buildable. Two central fixes moved their defects rather than removing them: the reserved answer still authorizes post-kill classification, and the proposed mirror identity record does not exist.

## 1. The six fixes

| Fix | Result | Assessment |
|---|---|---|
| 1. Reserve answer at wrapper start | **MISS** | After the kill seam, `classification` naturally contains `reserved`. `-Classify` explicitly treats `reserved` as permission to proceed, not as already claimed. Therefore a later call still sees `exit=0`, the reply, and returns `reply-present`. The plan’s own refusal test expects `already-classified`, contradicting the state machine. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:123-124,207-213,784-811` |
| 2. Refuse non-mirrors | **MISS** | `new-review-mirror.ps1` does not write an identity record into the mirror. It prints identity fields to stdout, and deliberately accepts recorded values as arguments instead of rereading a mutable file. The plan neither defines a record path/schema nor modifies that producer. `tools/new-review-mirror.ps1:19-33,1195-1208`; `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:507-518` |
| 3. Parse first `workdir:` and split states | **NARROW** | The design text is correct: first-header parsing closes the containment-search defect, and the three names honestly distinguish missing, unconfirmed, and mismatched evidence. But Task 3 omits `workdir-unconfirmed` from its state table and retains a test requiring the old `exit-nonzero`-before-workdir ordering. The implementation cannot satisfy both prose and tests. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:224-261,567-573,615-621` |
| 4. Own child streams | **MISS** | stdout/stderr ownership and the whole-output assertion are right, but `< NUL` is not valid PowerShell syntax on either Windows PowerShell 5.1 or PowerShell 7; both parsers reject `<` as reserved. Thus the proposed wrapper cannot run. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:127-143,833-843` |
| 5. Mandatory seal plus embedded values | **NARROW** | Requiring the seal at every call site closes the optional-omission path, and an ordinary receipt-only edit is detected. But after the kill interval, standalone `-Classify` can still redeem the natural `reserved` state using values read from the receipt/wrapper. Consequently the unattributable post-kill route remains. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:145-152,217-218,823-830,1169-1175`; `docs/superpowers/specs/2026-08-31-dispatch-invariants.md:244-249` |
| 6. Fifth call site | **CLOSE**, with drift | `kimi-write-probe` is now explicitly named and given a migration assertion. However, Task 7 Step 4 still says “each of the four,” and the `>= 5` seal-count assertion does not prove one occurrence in each distinct call site. Change “four” to “five” and preferably pin each call region. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1055-1070,1107-1116,1153-1160` |

## 2. Classifier and wrapper attack

I found two concrete false-success cases.

First, the original post-kill case remains:

1. The wrapper creates `claim` and writes `classification=reserved`.
2. The child writes a non-empty reply and exits zero.
3. The wrapper writes `exit=0` and reaches the deliberate seam.
4. The wrapper is killed, so the harness task is non-successful.
5. A later standalone `-Classify` sees `reserved`, which the classifier accepts; every remaining artifact is successful, so it writes `reply-present` and exits zero.

That is exactly the directory created by the flagship test, and exactly the later call that the next test incorrectly expects to be refused. No file edit is required. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:193-203,207-233,784-811`

It also reproduces earlier-run misattribution: A reaches that seam and dies; B reruns the wrapper and loses at A’s existing claim; a subsequent `-Classify` returns success from A’s artifacts after B’s failed invocation. Claim presence still does not identify which invocation supplied the artifacts—the original poll’s second case. `docs/superpowers/plans/rounds/2026-08-31-dispatch-options-poll/POLL-RESULT.md:77-81`

Second, the proposed mirror check permits a post-preparation tree swap. Even assuming the missing identity record is invented, the receipt binds only the path, while classifier state 7 checks only whether that path still carries a record. Replace the mirror’s contents at the same path while preserving/copying the record; the wrapper relocates successfully, the client reports the expected path, and the classifier returns `reply-present` for the wrong contents. B4 explicitly requires post-preparation mutation detection. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:90-104,220-227,507-518`; `docs/superpowers/specs/2026-08-31-dispatch-invariants.md:68-71`

The copied-record case is partly speculative because the plan never defines that record. Under the stated presence-only check, however, it follows directly.

I also searched: kill before either reservation; kill during the body; kill after final classification; hung body or wrapper; body `exit`/`[Environment]::Exit`; concurrent first starts; ordinary rerun; missing/torn receipt, exit, transcript, or reply; edited receipt; stale artifact reuse; prompt-injected secondary `workdir:` lines; and nonzero exit combined with wrong-tree evidence. Apart from the two routes above, those shapes fail conservatively under the intended ordering. The workdir-before-exit ordering itself is now right. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:205-248`

## 3. The stated reservation residual

Stating the deliberate “edit classification back to reserved” residual is enough against a caller who intentionally rewrites every artifact they own; no filesystem-only token can defeat that owner. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:264-273`

But the plan has not reduced the residual to that case. Immediately after the tested kill, the file already says `reserved`; no deliberate edit is necessary. Thus the residual paragraph understates the reachable condition, and Task 8 incorrectly says the create-new claim closes the post-hoc surface. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:796-811,1238-1243`

The smallest structural correction is:

- Before any successful terminal artifact is published, atomically consume `reserved` into a non-redeemable `classifying` state.
- Keep the remaining classification in that same wrapper process, or inline it, so standalone `-Classify` cannot accept `classifying`.
- Move the seam after that transition.

Then a kill leaves `classifying`, and a later call returns `already-classified`; only a deliberate edit back to `reserved` remains. No persistent secret is required.

## 4. Mirror-identity refusal

As written, it cannot work: the claimed record is absent. The existing mirror tool instead has a `-VerifyIdentity` interface taking the expected source head, mirror head, and source-status digest as independent arguments. `tools/new-review-mirror.ps1:25-33,580-654`

Even after defining a record, presence is insufficient. The expected identity must be bound into the receipt/wrapper and reverified before the child runs; otherwise same-path content replacement passes silently. D7 requires a frozen copy at a named commit, not merely a directory carrying a marker. `docs/superpowers/specs/2026-08-31-dispatch-invariants.md:217-225`

Refusing ordinary directories does not break the five intended review call sites: the skill establishes that the mirror is the reviewed tree for every lane, and the Kimi sites already name it explicitly. `skills/multi-model-verify/SKILL.md:101-117`; `skills/multi-model-verify/references/backup-lane.md:116-127,146-154,469-491`

It does contradict the plan’s claim that `-NoWorkdirEvidence` exists for non-review rounds: global mirror refusal makes such a round impossible. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:507-518,1146-1148`

## 5. Still unbuildable, missing, or overclaimed

- **Task 2 Step 1:** the success test creates an ordinary directory, while Step 3 requires every ordinary directory be refused. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:412-426,507-518`
- **Task 2 Step 3:** the identity record has no producer, filename, schema, validation rule, or scheduled modification to `new-review-mirror.ps1`. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:394-404,507-518`
- **Task 3 Step 1:** “one per state” supplies thirteen entries, missing `never-reserved`, `receipt-altered`, and `workdir-unconfirmed`; its wrong-tree/nonzero test pins the superseded order. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:553-573,615-621`
- **Task 3 interface:** it omits `-ExpectedToken` and `-ExpectedPriorStateSha256`, even though Task 4 calls both. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:559-562,133-135`
- **Task 4 Step 1:** the post-kill refusal test contradicts the state machine, and the failed-client fixture sets `$code=1` without `exit $code`; the child therefore normally exits zero and produces `no-reply`, not `exit-nonzero`. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:744-747,804-811`
- **Task 4 Step 3:** `< NUL` is invalid PowerShell, and `WriteAllText(...,'reserved') # create-new` is not create-new—it overwrites. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:123-128,882-903`
- **Task 7 Step 4:** “four” contradicts the task’s explicit inventory of five. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1055-1070,1153-1160`
- **Task 8 Step 2:** the contract text describes a different residual and still claims the answer claim closes post-hoc classification. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1238-1243`

Accordingly, self-review rows 1 and 5 are overclaimed, and the E4 paragraph is established only for the ordinary wrapper path—not the post-kill standalone path. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1514-1526`

The four deliberate omissions remain appropriate and are not load-bearing. The defects above concern completion authority and tree identity, not versioning, liveness, session survival, or hung-task policy. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1491-1508`

## 6. Build verdict

Not yet good enough to build from. The minimal load-bearing revision is:

1. Consume the answer reservation before terminal publication and make that classification continuation wrapper-only.
2. Replace the fictitious mirror marker with a defined, receipt-bound identity verified again before the client runs.
3. Repair the contradictory state tests and valid PowerShell stream invocation.

After those changes, the deliberate filesystem-owner residual can be stated and shipped honestly.

**FIX**