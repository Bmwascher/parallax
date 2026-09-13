# Fable whole-branch review fix brief (pre-round-1), 2026-09-13

Branch `mirror-reaper`, worktree `C:\Users\Brandon\Documents\_worktrees\parallax-mirror-reaper`, HEAD 6c38ec9. The fable-reviewer's raw reply is at `C:\Temp\parallax-scratch\2026-09-13-mirror-reaper\fable-diff-r1-reply.md`; the session accepted the findings below. Apply ALL of them in ONE commit. Tools stay ASCII-only and identical under Windows PowerShell 5.1 and PowerShell 7. Do not reflow existing paragraphs in `skills/`, `commands/` or the spec; append or edit only the sentences named. Never touch `C:\kv-*` or `C:\kvs-*`.

## A. Sidecar failure message and duplication (fable Minor 1 + ledger minor) — `tools/write-attestation.ps1`

The sidecar block (after `Invoke-Reap "mirror" ...`) builds its own failure line and omits the "bridge was not attempted" note. Compute the note ONCE before the mirror reap and reuse it:

```powershell
$bridgeNote = ""
if ($reapBridgeFull) { $bridgeNote = "; the bridge was not attempted: " + $reapBridgeFull }
Invoke-Reap "mirror" $reapMirrorFull $bridgeNote
```

and in the sidecar's `catch`, replace the message with:

```powershell
Write-Output ("ERROR: reap failed for " + $sidecar + ": " + $_.Exception.Message +
    " - the attestation stands; remove the sidecar by hand" + $bridgeNote)
```

Test (append to `evals/multi-model-verify/test_mirror_reaper.py`, group 2 helpers available: `make_repo`, `make_mirror`, `make_bridge`, `attest`, `att_file`): `test_a_sidecar_failure_names_the_unattempted_bridge` — mirror + bridge, sidecar `tmp_path / "kv-t.source-manifest"` written and HELD OPEN by the test (`with open(sidecar, "r")`), call `attest(..., mirror=mirror, bridge=bridge)`; assert exit 3, `"reap failed for " + str(sidecar) in proc.stdout`, `"the bridge was not attempted: " + str(bridge) in proc.stdout`, `att_file` present, `not mirror.exists()`, `bridge.exists()`, `sidecar.exists()`.

## B. A `.git` that is a junction is not a directory (fable Minor 2) — `tools/write-attestation.ps1`, `Resolve-ReapPath`

After the existing `.git`-is-a-file refusal, add:

```powershell
if (($ga -band [int][System.IO.FileAttributes]::ReparsePoint) -ne 0) {
    Write-Output ("ERROR: $label has a .git that is a directory link, so its" +
        " identity would be read through the link ($full)")
    exit 2
}
```

Test `test_a_git_directory_that_is_a_junction_is_refused`: `real = make_mirror(repo, tmp_path / "real")`; `fake = tmp_path / "fake"; fake.mkdir()`; `(fake / "b.txt").write_text("b\n")`; `junction(fake / ".git", real / ".git")`; `attest(repo, base, head, mirror=fake)`; assert exit 2, `"directory link" in proc.stdout`, record absent, `fake.exists()`, `(real / ".git" / "HEAD").is_file()`.

## C. Three untested guard branches (fable Minor 3) — tests only, append to `test_mirror_reaper.py`

1. `test_a_bridge_with_a_remediation_commit_is_refused`: `bridge = make_bridge(repo, tmp_path / "kvs-t")`; add `AGENTS.md` in the bridge and commit it with `-c user.email=parallax@local -c user.name=parallax -m "remove instruction back-channels for review"` (the shape the MIRROR is allowed); `attest(repo, base, head, bridge=bridge)`; assert exit 2, `"not the attested head" in proc.stdout`, record absent, `bridge.exists()`.
2. `test_a_read_only_root_is_removed`: `tree = tmp_path / "tree"; (tree / "sub").mkdir(parents=True); (tree / "sub" / "f.txt").write_text("x\n")`; `subprocess.run(["attrib", "+R", str(tree)], check=True)`; run the group-1 `harness(tmp_path)` with `-Target str(tree)`; assert exit 0 and `not tree.exists()`.
3. `test_a_relative_reap_path_is_refused`: `attest(repo, base, head, mirror="kv-relative")` (a bare relative spelling); assert exit 2, `"absolute path" in proc.stdout`, record absent.

## D. The plan-mode residual is stated (fable Important 1) — record only

1. `docs/superpowers/specs/2026-09-13-mirror-reaper-design.md`, at the end of the section `## The reap point is the attestation`, append this paragraph:

   ```
   Stated limit: a PLAN-mode debate builds the same mirror through preflight
   step 3 and ends with a frozen plan, not an attestation, so its mirror has
   no mechanical reap point. Its removal is the hand route the doctor names
   until a plan-mode terminal event is recorded mechanically; backlog item
   102 carries that residual beside the same-head one.
   ```

2. `BACKLOG.md`, item 101, in the `**What closing it means.**` paragraph, after the sentence ending `never deletes.` insert: `A plan-mode debate has no attestation, so its mirror keeps the hand route; that residual is item 102's.` Then in item 102's first paragraph, after `hiding it.` append: ` A plan-mode debate ends with a frozen plan and no attestation, so its mirror has no mechanical reap point either; a plan-mode terminal event recorded mechanically is the third follow-up.` Re-attest BOTH items: run `python evals/tools/backlog_lint.py --digests BACKLOG.md`, copy the printed 12-hex digests for 101 and 102 into their `Verified: 2026-09-13 <digest>` lines, then `python evals/tools/backlog_lint.py` must print clean.

3. `skills/multi-model-verify/references/preflight-mirror.md`, End of life section, append as a NEW final paragraph (do not touch existing lines):

   ```
   Two limits, stated. A plan-mode debate ends with a frozen plan and no
   attestation, so its mirror has no mechanical reap point and keeps the
   hand route until one exists (backlog item 102). And an ESCALATE the user
   may still extend is not yet terminal: emit the attestation, and with it
   the reap, only once the user has declined to extend, because a reaped
   mirror turns the extension's `resume` into a transport failure.
   ```

   (This also carries fable Minor 5.)

## Verification, then commit

In PowerShell, foreground: `$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_mirror_reaper.py evals/multi-model-verify/test_attestation.py evals/multi-model-verify/test_multi_model_verify.py evals/multi-model-verify/test_contract_coverage.py -q` then with `"pwsh.exe"`; then `python evals/tools/skill_lint.py skills/multi-model-verify --strict` (0 errors), `python evals/tools/skill_scanner.py skills`, `python evals/tools/backlog_lint.py`.

Commit by explicit path (`git add tools/write-attestation.ps1 evals/multi-model-verify/test_mirror_reaper.py docs/superpowers/specs/2026-09-13-mirror-reaper-design.md BACKLOG.md skills/multi-model-verify/references/preflight-mirror.md`), message: `apply the fable whole-branch review: refuse a linked git dir, name the unattempted bridge on a sidecar failure, cover three guard branches, and state the plan-mode residual`.

Report to `C:\Temp\parallax-scratch\2026-09-13-mirror-reaper\fable-fix-report.md` (per item: change + covering test; both hosts' counts; the lint lines). Reply with the short status contract only.
