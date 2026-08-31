The exact tracked-file defect was not moved again: hashing the mirror’s baseline plus manifest catches an ordinary uncommitted edit. However, Task 2a is incompletely wired, and its “recorded canonical path” refusal has no interface capable of implementing it. There is also a narrower, already-documented blind spot for changed files Git still reports clean.

## 1. The seven changes

| Change | Result | Assessment |
|---|---|---|
| 1. Task 2a mirror digest and path checks | **NARROW** | The digest closes the normal tracked-edit and untracked-file cases. But Task 2 neither supplies nor records `mirrorStateSha256`, and no independent expected-path parameter exists for comparing `MirrorPath` with the path printed during construction. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:684-769,516-545,618-623` |
| 2. Capture verifier stdout | **NARROW** | The wrapper redirects both streams to `mirror.verify`, closing its leak. The design says preparation must capture output too, but Task 2 Step 3 still gives no capture instruction; a direct invocation would put `identity: verified` before JSON. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:137-142,216-220,618-623`; `tools/new-review-mirror.ps1:653-654` |
| 3. Null-pipe stdin | **CLOSE** | The selected form is syntactically valid and was measured on both hosts to produce EOF while retaining exit status and both redirections. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:146-180` |
| 4. Correct kill tests and ordering test | **CLOSE** | The seam test now requires `classifying:`, and the separate ordering test requires non-`reserved` once exit exists. Both agree with the wrapper. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1058-1112` |
| 5. Publish `-Redeem` | **CLOSE** | It appears in the public signature, wrapper invocation, Task 3 interface, and classifier rule. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:79-86,158-160,792-798,948-960` |
| 6. State the manual-classification residual honestly | **CLOSE** | Task 7 now distinguishes accidental invocation from a determined caller who reads the nonce. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1495-1500` |
| 7. Remove restated counts | **NARROW** | Most were removed, but Task 3 still says “all twelve fields”; the receipt table actually contains thirteen entries after adding `mirrorStateSha256`. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:94-111,792-798` |

## 2. Task 2a

### What the digest correctly covers

The existing machinery is suitable if Task 2a explicitly reuses `Get-StatusSha256($MirrorPath)`:

- Baseline capture uses `git status --porcelain --ignored -uall -z`, so normal tracked modifications, untracked files, and ignored inputs enter the status boundary. `tools/new-review-mirror.ps1:392-406`
- Manifest paths are enumerated recursively, sorted ordinally, and hashed from raw bytes. `tools/new-review-mirror.ps1:446-499`
- Baseline fields and manifest records are joined with NUL boundaries before UTF-8/SHA-256 hashing, making the representation deterministic and non-forgeable by filenames. `tools/new-review-mirror.ps1:514-547`
- Enumeration, parsing, or file-read failures return structured errors instead of silently omitting content. `tools/new-review-mirror.ps1:526-540,446-495`

Therefore the exact case from round 3—an ordinary tracked `README.md` edited without a commit—changes the status boundary and is caught. Task 2a’s test correctly preserves that shape rather than weakening it to a commit that changes HEAD. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:708-715,1153-1163`

The digest does not change merely because timestamps or directory location changed: its inputs are Git’s status records and selected file bytes. Moving the mirror is refused separately and intentionally. `tools/new-review-mirror.ps1:405-406,477-499,542-547`

### What is incomplete

First, Task 2 is not updated for the new mandatory field:

- Its `-Prepare` invocation omits `-MirrorStateSha256`.
- Its expected receipt fields omit `mirrorStateSha256`.
- Its Step 3 verification command omits the new argument.
- Task 2a’s file list modifies only the mirror tool and a test module, not `dispatch-round.ps1` or its tests.

`docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:516-545,618-623,690-698`

Because Task 2a makes the verifier argument mandatory, the final Task 2 implementation cannot satisfy the design. Either move Task 2a before Task 2, or have Task 2a explicitly modify `dispatch-round.ps1` and `test_dispatch_round.py`.

Second, “refuse a `MirrorPath` that is not the canonical path the build recorded” is not implementable from the stated interface. `-MirrorPath` is the current path; `mirrorStateSha256` contains only baseline/manifest state. There is no `-ExpectedMirrorPath` against which to compare it, and no internal record exists. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:694-698,763-769`

Add the canonical construction path to the external identity interface—preferably `-ExpectedMirrorPath`—or remove that promised refusal.

### Remaining digest boundary

`Get-StatusSha256` hashes only paths Git reports in status. The tool itself states that a tracked file Git reports clean is not covered. `tools/new-review-mirror.ps1:562-570`

Thus a tracked path hidden by `assume-unchanged`, `skip-worktree`, or another clean-filter condition can change bytes without changing HEAD, baseline, or manifest. That is narrower than the ordinary edit Task 2a fixes, but the resulting digest is not literally a digest of every mirror byte.

This can reasonably ship as a stated residual if the contract preserves the tool’s existing qualification. If the requirement is exact byte identity of every tracked file, Task 2a instead needs to refuse such index flags or hash all tracked worktree files.

## 3. Wrapper and classifier attack

I found no new natural false-success path in the completion coupling.

I searched:

- death before either reservation;
- death during either mirror verification;
- child `exit` and `[Environment]::Exit`;
- child failure, missing reply, and malformed artifacts;
- death before nonce consumption;
- death between nonce consumption and exit publication;
- death at the seam;
- death during classification or after final state write;
- concurrent starts and reruns;
- nonce mismatch, torn classification, receipt mutation, and stale artifacts;
- stdin, stdout, and stderr interference.

Those paths are conservative under the stated wrapper ordering. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:126-161,282-323,348-378`

Two mirror residuals remain:

1. A tracked file that changes while Git continues reporting it clean can preserve the proposed digest and yield `reply-present` over changed bytes. This is concrete but depends on a clean-filter/index condition; it is the limitation the mirror tool already documents. `tools/new-review-mirror.ps1:562-570`
2. An external process can mutate the mirror after the wrapper verification returns and before or during the reviewer process. There is no post-child re-verification. This is speculation about a concurrent external writer, but mechanically it would allow a successful review over changed bytes. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:137-160`

The second can be shipped as a filesystem-owner residual if stated explicitly. A cheap strengthening would reverify after the child returns and before consuming the answer reservation; that catches persistent in-round mutation, though no before/after check can detect an adversarial change-and-revert.

The nonce-reading residual remains correctly stated and does not forge the authoritative harness result. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:359-378`

## 4. Still unbuildable, missing, or overclaimed

Ranked by importance:

1. **Correctness/build blocker — Task 2/Task 2a integration.** Task 2 omits the mandatory digest from the command, receipt assertion, and implementation steps, while Task 2a does not modify Task 2’s files. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:516-545,618-623,690-698`
2. **Unbuildable interface — Task 2a Step 3.** No independently recorded path is supplied, so the different-path refusal cannot be implemented. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:763-769`
3. **Build-output defect — Task 2 Step 3.** Preparation-time verifier stdout still is not explicitly captured, so JSON output may be polluted. The existing JSON test should expose this, but the implementation instruction should say where the verifier output goes. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:571-577,618-623`; `tools/new-review-mirror.ps1:653-654`
4. **Test location drift — Task 2a.** The repository’s existing mirror tests are in `test_review_mirror.py`; the plan names nonexistent `test_new_review_mirror.py`. Creating a new module is possible, but its shown helpers are not defined there. Extending the existing module is the smaller build instruction. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:690-704`
5. **Overclaim — Task 3 interface.** “All twelve fields” is wrong after the receipt gained `mirrorStateSha256`. Use “the receipt fields above.” `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:792-798`
6. **Coverage gap — Task 2a Step 1.** The test for an “unmeasurable mirror state” supplies an empty expected digest; it does not exercise a failure while recomputing the current mirror. Add an unreadable mirror input test analogous to the tool’s source-side failure tests. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:740-747`; `tools/new-review-mirror.ps1:526-540`

The fenced PowerShell wrapper parses under both PowerShell hosts. I found no new syntax error in the code blocks.

## 5. Build verdict and last-round priorities

The wrapper/classifier design is now good enough. The plan as a whole is not yet buildable because Task 2a is not connected to Task 2.

For the final round, spend effort in this order:

1. Wire `mirrorStateSha256` through Task 2’s CLI, receipt, tests, wrapper, and captured verifier invocation.
2. Define `-ExpectedMirrorPath` or delete the unimplementable moved-path promise.
3. Add the current-state measurement-failure test and use the existing mirror test module.
4. Remove the stale field count.

Reasonable stated residuals:

- Git-clean tracked-byte changes outside the status/manifest boundary.
- A determined caller reading the nonce.
- Concurrent external mutation after verification, if filesystem ownership after dispatch is explicitly trusted.
- Harness trailer format stability and hung-round policy, already stated.

The preparation-output leak should not be shipped as a residual; it directly breaks machine-readable JSON.

**FIX**