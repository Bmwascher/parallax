The mirror fix moved its defect again. The fictional marker is gone, but `-VerifyIdentity` accepts a self-consistent wrong tree and does not verify the mirror’s working contents. Separately, `-InputFormat None` parses but does not put the inherited OS stdin at EOF.

## 1. The five changes

| Change | Result | Assessment |
|---|---|---|
| 1. Consume reservation with runtime nonce | **CLOSE** | The natural killed state is no longer automatically redeemable. Before the transition, `reserved` maps to `not-ready` and no exit exists; after it, an outside call needs the runtime nonce; after completion, the state is final. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:148-158,243-273,320-339` |
| 2. Double `-VerifyIdentity` | **MISS — defect moved** | The caller still supplies all mutually confirming values. When `sourceHead == mirrorHead`, passing the live repo as both `RepoRoot` and `WorkingDirectory` satisfies every check. Moreover, verification checks only the mirror HEAD; it computes status/content state for the source, not the mirror. Same-HEAD mirror edits therefore survive both verifications. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:136-180,579-605`; `tools/new-review-mirror.ps1:612-650` |
| 3. `-InputFormat None` and real CreateNew | **NARROW** | `FileMode.CreateNew` closes the overwrite defect, and the wrapper block parses on both hosts. But `-InputFormat None` only suppresses PowerShell pipeline input; it does not close or redirect the inherited stdin handle. I measured `"SENTINEL" \| powershell/pwsh -InputFormat None -Command '[Console]::In.ReadLine()'`; both children read `SENTINEL`. A4 still is not met. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:129-168`; `docs/superpowers/specs/2026-08-31-dispatch-invariants.md:42-46` |
| 4. Correct interfaces/tests and move identity out of classifier | **NARROW** | The state table, Task 3 interface, failed-client fixture, and “five” wording are corrected. But Task 4’s flagship kill test still asserts `classification == "reserved"` while the immediately following test expects `classifying:<nonce>`. The mirror test also expects behavior the real verifier does not provide. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:651-670,874-880,917-951,1009-1015,1317-1324` |
| 5. Remove restated counts | **MISS** | The plan still says “Seventeen states,” “all twelve fields,” and “seventeen states” outside the authoritative list; Task 2’s test name still says eight-field receipt. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:94-110,275-278,478,651-653,671-673,1392-1399` |

## 2. Wrapper/classifier attack

I found a concrete misattributed-success path through the mirror verification.

### Same-HEAD post-preparation mutation

1. `-Prepare` verifies the mirror successfully.
2. Before the wrapper runs, something modifies a tracked file in the mirror worktree without committing it.
3. The wrapper calls `-VerifyIdentity` again.
4. The mirror HEAD remains unchanged, so the mirror check passes.
5. The source repository and its status remain unchanged, so the source checks pass.
6. The client reads the modified mirror contents, reports the expected path, writes a reply, and exits zero.
7. The classifier returns `reply-present`.

`-VerifyIdentity` calls `Get-HeadSha` for the mirror but never computes the mirror’s baseline or manifest; the only status digest checked at verification is for `RepoRoot`. `tools/new-review-mirror.ps1:625-650` The builder does compute a mirror baseline and manifest, but those values are merely printed and are not accepted by verify mode. `tools/new-review-mirror.ps1:1148-1173,1195-1208`

That is a successful review attributed to the frozen mirror while the client actually read different bytes.

There is also a wrong-initial-value case. If mirror construction required no remediation commit, `sourceHead` and `mirrorHead` can be equal. Passing the live repository as both source and mirror then satisfies the two HEAD comparisons and the source-status comparison; verify mode has no canonical inequality check between `RepoRoot` and `MirrorPath`. `tools/new-review-mirror.ps1:580-650,1195-1202`

The plan’s `swap_mirror_contents` test does not specify whether the swap changes HEAD. If it changes HEAD, it tests the already-implemented HEAD comparison. If it changes only working bytes, the test will fail against the real verifier. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1009-1015`

For completion coupling, I searched kills:

- before `claim`;
- between `claim` and reservation;
- during mirror verification;
- during the child;
- before nonce consumption;
- between nonce consumption and exit publication;
- at the seam;
- during classification;
- after final state write but before wrapper exit;
- concurrent starts and ordinary reruns;
- body `exit` and `[Environment]::Exit`;
- missing, torn, or malformed receipt/classification/exit/reply/transcript;
- nonce mismatch and stale receipt reuse.

I found no new natural false zero in those shapes. Before nonce consumption there is no redeemable state; after consumption but before exit, classification reaches `no-exit-file`; at the seam an ordinary caller lacks `-Redeem`; and after finalization another classification is refused. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:243-284,309-339`

The admitted deliberate path remains: after a killed or hung wrapper publishes exit, a caller can read the nonce and invoke `-Classify`, which may return zero from disk. The harness task itself remains unfinished or killed, so this does not forge its authoritative result. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:331-339`

## 3. Runtime nonce

The reduction is real, but it is procedural friction rather than authentication.

Previously, an ordinary later `-Classify` invocation could redeem the natural post-kill state using only preparation-time values. Now the caller must inspect a runtime-written file and extract the nonce. A guessed or omitted nonce is refused. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:245-273,320-339`

The nonce is intentionally not secret—it is written in plaintext to `classification`. Therefore a caller who reads it still gets the disk verdict. The plan states exactly that residual, which is acceptable given that the harness task’s exit remains authoritative. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:331-339,1402-1413`

Task 7 nevertheless overclaims that manual classification “will now be refused outright.” A caller holding the read nonce is not refused. That sentence must match the stated residual. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1341-1344`

## 4. Double mirror verification

It is not sound yet.

The existing verifier proves narrowly:

- source HEAD equals expected source HEAD;
- mirror HEAD equals expected mirror HEAD;
- current source status/content fingerprint equals its recorded value.

It does not prove:

- `RepoRoot` and `MirrorPath` are different;
- `MirrorPath` equals the originally recorded mirror path;
- the mirror worktree’s current baseline and manifest equal construction;
- no mutation occurs after verification and before the client reads it.

The implementation itself documents that its identity coverage is narrow. `tools/new-review-mirror.ps1:562-578`

The smallest sound extension is to add a construction-time `mirrorStateSha256` covering the mirror baseline plus content manifest, print it with the identity record, pass it into `-VerifyIdentity`, and recompute it over `MirrorPath` at wrapper time. Also reject canonical `RepoRoot == MirrorPath` and bind the originally printed canonical mirror path.

A deliberate concurrent swap after verification remains a filesystem-owner race; I am speculating about that adversarial case. The same-HEAD mutation before verification is not speculative and currently passes.

## 5. Unbuildable, missing, or overclaimed

- **Task 4 Step 1:** one test requires `reserved` after the seam, while the design and next test require `classifying:<nonce>`. Both cannot pass. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:917-951`
- **Task 4 Step 1:** `test_the_wrapper_reverifies_the_tree_before_the_client_runs` claims arbitrary changed contents are detected, but `-VerifyIdentity` checks only mirror HEAD. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1009-1015`; `tools/new-review-mirror.ps1:625-650`
- **Tasks 2 and 4:** successful mirror verification prints `identity: verified`. Neither call captures or suppresses it. At preparation, that can precede and corrupt JSON output; in the wrapper, it creates an extra stdout line and contradicts the exact-one-line tests and contract. `tools/new-review-mirror.ps1:653-654`; `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:136-139,364-371,532-538,1025-1029`
- **Design interface:** the top-level `Classify:` signature omits mandatory `-Redeem`, although the wrapper and Task 3 interface include it. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:79-86,155-158,651-657`
- **A4 remains missing:** `-InputFormat None` leaves raw stdin inherited. Use `ProcessStartInfo` with redirected stdin and close `StandardInput` immediately, or an equivalent real closed handle. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:143-168`
- **Task 7 Step 4:** “manual classification is refused outright” contradicts the admitted nonce-reading residual. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:331-339,1341-1344`
- **Count-drift claim:** the authoritative-list rule is not followed by the plan itself. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:275,671-673,1397`

I parsed the complete fenced PowerShell wrapper block under both hosts and found no PowerShell grammar error. The Python and Bash blocks contain no additional syntax defect on inspection. The remaining stream problem is semantic, not parsing.

The self-review therefore still overstates row 5: the path and transcript header are bound, but the frozen tree’s current bytes are not. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1684-1690`

## 6. Build verdict

Not yet good enough to build from. The minimum correctness delta is:

1. Bind and reverify the mirror worktree state—not only its HEAD—and reject source/mirror path equality.
2. Give the child an actually closed stdin handle.
3. Capture mirror-verifier stdout and correct the contradictory kill test/interface text.

The runtime nonce itself is good enough; it does not need another redesign.

**FIX**