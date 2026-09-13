# Fable whole-branch review reply (raw, retained), range 6038c37..6c38ec9, 2026-09-13

### Strengths

- The removal is the right shape and honours the reparse invariant at every level. `tools/review-tree-removal.ps1:78-83` deletes a directory link with the non-recursive `Directory.Delete` and a file link with `File.Delete`, never descending; `:146-149` refuses a root that is itself a reparse point; the callers run the ancestor guard first (`tools/write-attestation.ps1:114-119`, `tools/new-review-mirror.ps1:1799`). Group 1 drives the intact-junction, dangling-junction and link-root cases against real junctions (`evals/multi-model-verify/test_mirror_reaper.py:137-208`).
- Item 98 is genuinely closed: the postcondition is read back rather than inferred (`tools/review-tree-removal.ps1:167-179`), the mirror tool terminates before `New-Item` on a named failure (`tools/new-review-mirror.ps1:2007-2013` vs `:2015`), and the test drives a real held handle rather than a stub (`evals/multi-model-verify/test_review_mirror.py:3237-3256`).
- The emitter's ordering is correct for the two invariants that matter: every reap refusal runs before `$attDir` is created (`tools/write-attestation.ps1:216-232` precedes `:235`), a failed or absent record write exits 2 with "nothing was reaped" (`:282-291`), and the reap runs only after `attestation written:` (`:292-325`). The parametrised wrong-tree case checks the record is absent for all eight shapes (`test_mirror_reaper.py:313-346`).
- The git identity reads are pinned to the tree's own git dir (`tools/write-attestation.ps1:153`, `:162-164`), so an invalid `.git` directory cannot borrow a parent repository's HEAD; `test_mirror_reaper.py:451-461` proves it. The remediation shape is checked exactly as specified (author email, parent count 2, parent 1 equals head), and I confirmed the mirror tool commits with `-c user.email=parallax@local` (`tools/new-review-mirror.ps1:2216`), which sets the author email `%ae` reads.
- `$MirrorPath` is already absolute (`tools/new-review-mirror.ps1:1250`) when the `-Force` path hands it to `Remove-ReviewTree`, so the .NET `GetFullPath` cwd trap does not apply there; the emitter refuses a non-rooted path outright (`tools/write-attestation.ps1:82-85`).
- The M5 rename is complete: no `kerev` spelling survives under `skills/`, `agents/`, `commands/`, `tools/`, `evals/` or the backlog.
- The M3 fix names the unattempted bridge on a mirror failure (`tools/write-attestation.ps1:297`, pinned at `test_mirror_reaper.py:363`), and the CI module list carries the new module under both hosts with a self-check (`test_mirror_reaper.py:211-221`).

### Issues

#### Critical

None.

#### Important

1. **The spec's central claim does not hold for plan-mode debates, and neither the spec nor item 101 says so.** `docs/superpowers/specs/2026-09-13-mirror-reaper-design.md:44-47` says the attestation is "the one terminal event the plugin already records mechanically" and no sweep exists; `skills/multi-model-verify/SKILL.md:378` restricts the emitter to "Mode diff only". A plan-mode debate builds the same mirror through preflight 3 and has no attestation, so its mirror has no reap point at all. The only route is the hand removal the doctor names (`commands/doctor.md:387`), which is the prose-rule mechanism the spec rejects at `:29-31`. `BACKLOG.md:177-186` ("What closing it means") would close item 101 against a mechanism that covers one of the two debate modes. This is a record defect, not a code defect: state the plan-mode residual in the spec and in item 101 or 102 (one sentence each), so the closure and the doctor's "removed by hand" branch describe the same population.

2. **The full gate at the branch head is not on record.** The plan's Global Constraints (`docs/superpowers/plans/2026-09-13-mirror-reaper.md:20`) require the six CI commands before the final commit. The ledger's last evidence is "230 passed both hosts" at e3818f9 (`.superpowers/sdd/2026-09-13-mirror-reaper/progress.md:30`); commit 6c38ec9 then edited `BACKLOG.md` (items 101 and 102, with `Verified:` digests at `BACKLOG.md:98` and `:144`), and nothing records `backlog_lint.py` or the rest of the gate against that head. Gap, not a finding against the code: run the six commands at 6c38ec9 and record the result in the ledger before the debate treats the digests as verified.

#### Minor

1. **Sidecar failure omits the unattempted bridge (M3 residual).** `tools/write-attestation.ps1:315-317` exits 3 when the sidecar cannot be deleted, but its message does not carry the "; the bridge was not attempted: <path>" note that `Invoke-Reap` adds at `:297`. A sidecar failure with a bridge named leaves the bridge on disk with no message saying so. One-line fix: append the same `$notAttempted` text.

2. **Rule 5 accepts a `.git` that is a junction.** The spec requires a `.git` DIRECTORY (`spec:63-65`); the check at `tools/write-attestation.ps1:148` tests only the Directory bit, which a junction also carries, so the HEAD read at `:153` goes through the link and the identity is borrowed from the target. The removal itself is safe (the junction is deleted as a link, `review-tree-removal.ps1:78-80`), so the damage is bounded to the named tree's own files, and it is the item 102 class of "the session named the wrong tree". Adding a ReparsePoint test on `$ga` costs one line.

3. **Three guard branches have no test.** The bridge's `$allowRemediation = $false` path (`tools/write-attestation.ps1:161`, a bridge carrying a `parallax@local` commit above the head must be refused; `test_mirror_reaper.py:298-309` covers only a stale head), the read-only ROOT branch (`review-tree-removal.ps1:158-161`; `test_mirror_reaper.py:466-473` sets `+R` on a subdirectory only), and the non-rooted path refusal (`write-attestation.ps1:82-85`). None is a correctness risk on the range; they are the parts of the guard the cross-vendor reviewer will ask about.

4. **Behavioral evals not recorded for the SKILL.md edit.** `CLAUDE.md` names `run_behavioral_evals.py --changed` for skill/prompt changes; the branch removes two Common-mistakes bullets (`skills/multi-model-verify/SKILL.md:411-415`) and inserts a paragraph at `:389-390`. The ledger records skill_lint and the pin suites only. Opt-in by policy, so a gap to name rather than a defect.

5. **An ESCALATE that the user may still extend is not terminal, and the prose does not say so.** `skills/multi-model-verify/references/preflight-mirror.md:93-99` binds the reap to the attestation; the 0.34.0 debate escalated at round 4 and the user extended by two rounds before attestation. A session that emits an ESCALATE attestation with `-ReapMirror` before the user declines to extend turns the extension into a transport failure on `resume`. One clause in the End of life section ("emit the attestation only once the user has declined to extend") closes it.

### Ledger minors triage

- **Task 1: plan cites :1791-1819, actual extent 1791-1820** (`progress.md:16`) - ride. A citation in the plan; the diff shows the whole block removed and re-created verbatim.
- **Task 3: no test for mirror-equals-bridge refusal** (`progress.md:21`) - ride, already closed. `test_overlapping_mirror_and_bridge_are_refused[same]` (`test_mirror_reaper.py:477-490`) drives exactly that shape against the rewritten overlap check at `write-attestation.ps1:225-232`.
- **Task 3: sidecar failure path repeats Invoke-Reap's message format inline** (`progress.md:22`) - fix before merge, because it is now also where Minor 1 lives: routing the sidecar through the same message builder removes the duplication and the missing "not attempted" note in one edit.
- **Task 4: End of life section and doctor check do not mention the .source-manifest sidecar** (`progress.md:26`) - ride. The spec states it (`spec:94-95`), the emitter prints `reaped sidecar:` (`write-attestation.ps1:319`), and the reference is about the guard rather than the inventory.
- **Final fix wave: Group 4 comment omits M3; M4 sentence is one long line** (`progress.md:31`) - ride both. The comment at `test_mirror_reaper.py:437` is a label; the long line at `preflight-mirror.md:115` carries pinned anchors, and the no-reflow constraint makes leaving it the safer choice.

### Assessment

Ready to merge: With fixes

The code on the range is sound and the two project invariants (never through a link, nothing reaped before the record) are enforced by construction and measured by tests; the fixes are the sidecar message (one line), the stated plan-mode residual in the spec and backlog (record, not code), and a recorded full gate at 6c38ec9.
