It happened again: the post-child verification moved its defect into an undefined splat. The first five changes close their findings; the sixth is a MISS and leaves a concrete false-success path. The plan needs one small Task 4 correction before implementation.

## 1. The six changes

| Change | Result | Assessment |
|---|---|---|
| 1. Move Task 1a before Task 2 and wire its outputs | **CLOSE** | Task 1a now explicitly precedes Task 2, produces both new values, and Task 2 passes and records them. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:519-529,661-678,754-764` |
| 2. Add `-ExpectedMirrorPath` | **CLOSE** | The verifier now has an independently supplied path to compare against, along with the source-is-not-mirror refusal. This closes the formerly unimplementable moved-path check. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:606-616,667-678` |
| 3. Capture preparation-time verifier output | **CLOSE** | Task 2 explicitly requires assignment or redirection so `identity: verified` cannot precede the JSON. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:754-764` |
| 4. Use `test_review_mirror.py` | **CLOSE** | The plan names the existing module and explicitly forbids creating the invented one. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:514-517,592-596` |
| 5. Remove the stale field count and test current-state measurement failure | **CLOSE** | Task 3 now refers to the receipt table instead of restating its field count, while Task 1a distinguishes a bad expected digest from failure to measure the current mirror. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:577-590,831-853` |
| 6. Verify again after the child | **MISS** | Placement is conceptually right, but the invocation uses `@mirrorArgs`, which is never defined anywhere in the plan. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:154-158` |

The sixth finding was moved rather than removed: “no post-child verification” became “a post-child verification statement that never successfully binds.”

I measured the exact failure on both PowerShell 7 and Windows PowerShell 5.1. With `$ErrorActionPreference = 'Continue'`, splatting the undefined `$mirrorArgs` produces a non-terminating parameter-binding error and leaves `$LASTEXITCODE` at the successful child’s previous value, zero. The wrapper explicitly changes error handling to `Continue` before running the child and then uses that stale value to test verification success. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:147-158`

A concrete false success is therefore:

1. The first verification passes.
2. An external process changes a tracked mirror file while the client is running and leaves it changed.
3. The client writes a nonempty reply and exits zero.
4. The second verifier does not run because `@mirrorArgs` is undefined.
5. Its binding error does not change `$LASTEXITCODE`, so line 158 treats the stale zero as verification success.
6. The wrapper consumes the reservation, writes exit zero, and classifies `reply-present`.

That is precisely the persistent in-round mutation the new verification claims to catch. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:154-169,1869-1878`

## 2. Second-verification ordering

The intended placement is correct: after the child returns, but before the reservation becomes `classifying:<nonce>` and before the exit file is published. A failed check at that point leaves `classification` at `reserved`, which `-Classify` maps to `not-ready`; it cannot become success. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:149-169,291-321`

The second check needs exactly the same arguments as the first. Its purpose is to compare a new measurement against the same preparation-pinned heads, state digest, and expected canonical path—not to mint new expected values. The complete first invocation already shows the necessary set. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:139-145`

The correction should:

- Define one `$mirrorArgs` hashtable before the first verification and use it for both calls.
- Restore `$ErrorActionPreference = 'Stop'` before the second invocation, so invocation or binding failures cannot inherit the child’s exit code.
- Add a Task 4 test whose child persistently edits a tracked mirror file, writes a reply, and exits zero; the wrapper must exit nonzero without consuming the reservation.

Task 4 currently tests only mutation before the wrapper starts, not mutation during the child. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1192-1202`

The fenced PowerShell parses on both hosts; this is a runtime name/error-handling defect, not a parser defect.

## 3. Residuals

The five listed residuals are reasonable once the post-child verification is repaired:

- Git-clean tracked-byte changes are accurately qualified.
- A determined filesystem owner can read the nonce.
- Change-and-revert during the client remains outside before/after verification.
- The harness trailer is measured rather than mechanically parsed.
- Hung rounds cost liveness but cannot produce success.

`docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1856-1887`

As written, however, item 3 overclaims: persistent mutation also survives because the second check does not execute. That is an unstated correctness defect, not an acceptable residual.

The exact earlier-act replay boundary is stated in the Task 8 contract instructions, although it is not duplicated in the residual list. It is therefore not hidden, and I would not block implementation merely to duplicate it. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1597-1608`

Two nonblocking stale counts remain:

- The file table says `backup-lane.md` has two call sites, while Task 7 correctly establishes that it has three. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:434-436,1412-1426`
- Task 8 says “four” regions even though its required split can produce five. The split instruction itself is unambiguous, so this is editorial rather than unbuildable. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1560-1569,1591-1596`

## 4. Task-order buildability

- **Task 1:** buildable; produces the renamed tool and test paths. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:442-454`
- **Task 1a:** buildable; uses the existing mirror test module and produces both verifier arguments. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:508-529`
- **Task 2:** buildable from Tasks 1 and 1a; its command, receipt assertion, and verifier invocation carry both new values. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:633-678,735-803`
- **Task 3:** buildable from Task 2’s receipt and publishes the complete `-Classify` interface. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:825-837,987-1010`
- **Task 4:** **not buildable to its promised behavior** because of undefined `$mirrorArgs`; Step 3 tells the implementer to emit the design wrapper exactly. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1239-1245`
- **Task 5:** buildable from Task 2’s `priorStateSha256`; the unnamed Kimi test module resolves to the existing `test_kimi_round_evidence.py`. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1280-1295`; `evals/multi-model-verify/test_kimi_round_evidence.py:1-4`
- **Task 6:** independent and buildable. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1350-1363`
- **Task 7:** buildable from Tasks 2, 5, and 6; its Kimi workdir measurement is an intentional stop gate, not a missing interface. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1429-1432,1483-1539`
- **Tasks 8 and 9:** buildable once Task 4 is corrected; their region split and content move are explicitly described. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1567-1628,1645-1685`
- **Tasks 10 and 11:** structurally buildable but transitively depend on a working Task 4. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1696-1708,1774-1782`

## Final verdict

This is one small correction short of buildable: make Task 4’s second verifier invocation use a defined argument set and fail closed, then add the persistent-mutation regression test. After that, the remaining limitations can ship as stated residuals.

**FIX**