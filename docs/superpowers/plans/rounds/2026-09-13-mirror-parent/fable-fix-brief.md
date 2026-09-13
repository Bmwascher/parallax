# Fable-review fix wave, branch mirror-parent (head 2df3d45), 2026-09-13

Whole-branch review artifact: C:\Temp\parallax-scratch\2026-09-13-mirror-parent\fable-diff-r1-reply.md
(range a48c35f..2df3d45). The session adjudicated every finding; the ones
below are ACCEPTED and are yours to apply, in ONE commit. Everything not
listed rides.

Worktree: C:\Users\Brandon\Documents\_worktrees\parallax-mirror-parent (branch
mirror-parent). Never write to C:\Users\Brandon\Documents\parallax. Never
touch C:\kv-bl-*, C:\kvs-bl-*, or the three pre-existing directories under
C:\pxm (8904109a, k10392, k92104).

## F1 (Important) - the notes' own command is not executable

`skills/multi-model-verify/references/model-prompting-notes.md`, in the
"Review mirror:" bullet below the round-artifact-roots region, the line
```
  `tools/artifact-roots.ps1 -Assert <mirror-path> -Expect reviewMirror`
```
becomes
```
  `tools/artifact-roots.ps1 -RepoRoot <repo> -Assert <mirror-path> -Expect reviewMirror`
```
(one line, no other change to the bullet; the tool refuses a command line
without `-RepoRoot`, exit 2).

Pin it so the omission cannot return: in
`evals/multi-model-verify/test_artifact_roots.py`,
`test_fixed_rows_state_their_reason_outside_the_region`, replace
```python
    assert "-Expect reviewMirror" in tail
```
with
```python
    assert "-RepoRoot <repo> -Assert <mirror-path> -Expect reviewMirror" in tail
```

## F2 (Minor, ruled a code fix) - the pre-build check and the reap guard must agree on the parent itself

Today `tools/artifact-roots.ps1 -RepoRoot <repo> -Assert C:\pxm -Expect reviewMirror`
answers inside (exit 0) because the assert set uses `Equals` or
`StartsWith` for every row, while the emitter refuses `C:\pxm` as a tree.
The parent itself is never a mirror, so the resolver refuses it for the
mirror row only.

(a) `tools/artifact-roots.ps1`, in the `-Assert` block, replace
```powershell
    $inside = $null
    foreach ($r in $retained) {
        if ($target.Equals($r.Root, $cmp) -or $target.StartsWith($r.Root + "/", $cmp)) {
            $inside = $r.Name
            break
        }
    }
```
with
```powershell
    $inside = $null
    foreach ($r in $retained) {
        # The review mirror parent is the one root a path may never EQUAL:
        # a mirror is a tree under it, and the parent itself is never a
        # tree (the emitter refuses it too), so the answer for the
        # parent is outside, and the two readers agree.
        $mayEqual = ($r.Name -ne "review mirror root")
        if (($mayEqual -and $target.Equals($r.Root, $cmp)) -or $target.StartsWith($r.Root + "/", $cmp)) {
            $inside = $r.Name
            break
        }
    }
```

(b) `evals/multi-model-verify/test_artifact_roots.py`, in
`test_expect_review_mirror_answers_for_the_declared_parent`, add after
the `outside` loop (before the `got = json.loads(...)` line):
```python
    # The parent itself is never a tree: outside for the mirror row, the
    # same answer the emitter's reap guard gives, so the pre-build check
    # and the reap agree.
    for parent in (r"C:\pxm", "C:/pxm/"):
        proc = run_resolver("-RepoRoot", str(repo), "-Assert", parent,
                            "-Expect", "reviewMirror")
        assert proc.returncode == 1, parent + ": " + proc.stdout + proc.stderr
        assert "outside every retained root" in proc.stdout, proc.stdout
```
And in `test_expect_accepts_the_expected_root_and_reports_it` nothing
changes (the rounds root itself still answers inside; only the mirror row
refuses equality).

(c) Prose, one sentence each, no reflow of neighbouring lines:
- `skills/multi-model-verify/references/model-prompting-notes.md`, the
  same bullet as F1, the two lines that follow the command line: change
```
  before the build, and `tools/write-attestation.ps1` refuses to reap a
  tree that is not under the parent (references/preflight-mirror.md,
```
  to
```
  before the build (the parent itself answers outside: it is never a
  tree), and `tools/write-attestation.ps1` refuses to reap a
  tree that is not under the parent (references/preflight-mirror.md,
```
- `skills/multi-model-verify/references/preflight-mirror.md`, in the
  build paragraph, change
```
first; exit 0 is the only clean answer, and a mirror built anywhere
else is refused at the reap and removed by hand.
```
  to
```
first; exit 0 is the only clean answer, the parent itself answers
outside because it is never a tree, and a mirror built anywhere else
is refused at the reap and removed by hand.
```

## F3 - item 107's Cost line describes the pre-branch state

`BACKLOG.md`, item 107, replace the whole `Cost:` line with:
```
Cost: a session that names the wrong tree at the right head has it removed, and the two post-delete sidecar read-back branches are locked only by a source-position pin a refactor could satisfy without a runtime read-back
```
Then recompute the digest: `python evals/tools/backlog_lint.py --digests BACKLOG.md`,
put item 107's digest on its `Verified:` line as `Verified: 2026-09-13 <digest>`,
and `python evals/tools/backlog_lint.py` must exit 0. Edit only item 107.

## F4 - the frozen plan carries two texts the branch corrected

`docs/superpowers/plans/2026-09-13-mirror-parent.md` is a record; correct
it IN PLACE with a dated bracket, never by appending a contradiction below
the old text:

(a) Task 1 Step 2, in the quoted replacement bullet, the line
```
  `tools/artifact-roots.ps1 -Assert <mirror-path> -Expect reviewMirror`
```
becomes
```
  `tools/artifact-roots.ps1 -RepoRoot <repo> -Assert <mirror-path> -Expect reviewMirror`
```
and add, immediately after that code block, the paragraph:
```
[Corrected 2026-09-13 after the Fable whole-branch review: the command as first written omitted `-RepoRoot <repo>`, which the tool requires; the branch carries the corrected line and a pin on it.]
```

(b) Task 3 Step 2, in the quoted doctor text, the phrase
```
`Canonical review mirror root` row of the round-artifact-roots
declaration, read through its one reader: run
```
becomes
```
`Canonical review mirror root` row of model-prompting-notes.md's
round-artifact-roots declaration, read through its one reader: run
```
and add, immediately after that code block, the paragraph:
```
[Corrected 2026-09-13: the citation as first written lacked the `model-prompting-notes.md's` prefix that `evals/multi-model-verify/test_contract_coverage.py` requires for a region id on the command surface; the implementer added it and the ledger records the ruling.]
```

(c) Task 1's **Interfaces** line: the phrase
```
exit 0 inside `C:/pxm` (any depth, or the parent itself, the same rule as every other row)
```
becomes
```
exit 0 inside `C:/pxm` (any depth below it; the parent itself answers outside, unlike every other row, so the pre-build check agrees with the reap guard — corrected 2026-09-13 after the Fable review)
```
and decision 2 in "Decisions the handoff left open, settled here": the
phrase
```
and the same membership rule the resolver's `-Assert` applies to every other row.
```
becomes
```
and the resolver's `-Assert -Expect reviewMirror` answers the same way for the parent itself (outside), a deviation from the other rows corrected 2026-09-13 after the Fable review.
```

## F5 (Minor) - Group 7 duplicates the fake-plugin setup

`evals/multi-model-verify/test_mirror_reaper.py`: add a module-level
helper before Group 7,
```python
def doctored_plugin(tmp_path, replacement):
    """A copy of the three attestation-side tools beside a doctored notes
    file, so a parent-read failure can be driven without touching the real
    declaration. `replacement` is what the review mirror row becomes; an
    empty string removes the row."""
    fake = tmp_path / "plugin"
    (fake / "tools").mkdir(parents=True)
    notes_dir = fake / "skills" / "multi-model-verify" / "references"
    notes_dir.mkdir(parents=True)
    for name in ("write-attestation.ps1", "artifact-roots.ps1", "review-tree-removal.ps1"):
        shutil.copy(REPO / "tools" / name, fake / "tools" / name)
    notes = REPO / "skills" / "multi-model-verify" / "references" / "model-prompting-notes.md"
    row = "Canonical review mirror root: `C:/pxm/<short-name>/`\n"
    assert row in read(notes)
    (notes_dir / "model-prompting-notes.md").write_text(
        read(notes).replace(row, replacement), encoding="utf-8")
    return fake / "tools" / "write-attestation.ps1"
```
and make `test_an_unreadable_parent_refuses_every_reap` and
`test_a_roots_tool_that_exits_nonzero_refuses_every_reap` call it
(`doctored_plugin(tmp_path, "Canonical review mirror root: `C:/pxm/`\n")`
and `doctored_plugin(tmp_path, "")` respectively), removing their copied
setup blocks and using the returned emitter path in `run_ps`. Every
assertion in both tests stays exactly as it is.


## F6 (found by the session's full gate at 2df3d45, both prose tests) - no backslash in a skill reference file

`evals/multi-model-verify/test_multi_model_verify.py::TestSkillStructure::test_no_backslash_paths_anywhere`
and `evals/multi-model-verify/test_backup_lane.py::test_backup_files_no_backslash_paths`
fail: every file under `skills/multi-model-verify/` must contain NO
backslash at all. Spell every example under `skills/` with forward
slashes; `commands/doctor.md` keeps its backslashes (it is not covered).

- `skills/multi-model-verify/references/backup-lane.md`: `C:\pxm\kv-<tag>` becomes `C:/pxm/kv-<tag>` (one line).
- `skills/multi-model-verify/references/model-prompting-notes.md`: build `C:\pxm\<tag>` becomes build `C:/pxm/<tag>` (one line).
- `skills/multi-model-verify/references/preflight-mirror.md`: `C:\pxm\kv-<tag>` becomes `C:/pxm/kv-<tag>` and `C:\pxm\kv-<tag>-2` becomes `C:/pxm/kv-<tag>-2` (two lines).
- `evals/multi-model-verify/test_mirror_reaper.py`, in `test_preflight_mirror_reference_states_the_end_of_life_rule`: `assert r"C:\pxm\kv-<tag>" in body` becomes `assert "C:/pxm/kv-<tag>" in body`.
- Keep F2(c)'s and F1's sentences exactly as they are written above; they carry no backslash.

After the edits, `grep -rn '\' skills/multi-model-verify/` (a literal backslash) must print nothing.

## F7 - the plan file is untracked

`docs/superpowers/plans/2026-09-13-mirror-parent.md` was never committed
(`git status` shows it `??`). Stage it by path in the same commit; it is
already in the `git add` list below, so nothing changes except that the
add now creates the file in history.

## Verification additions

Add to the verification commands:
```
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_multi_model_verify.py evals/multi-model-verify/test_backup_lane.py -q
```
(these two modules carry the no-backslash tests; both must pass).

## Verification, then commit

From the PowerShell tool, in the worktree:
```
python evals/tools/skill_lint.py skills/multi-model-verify --strict
python evals/tools/backlog_lint.py
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_artifact_roots.py evals/multi-model-verify/test_mirror_reaper.py evals/multi-model-verify/test_contract_coverage.py -q
$env:PARALLAX_PS_HOST = "pwsh.exe"; python -m pytest evals/multi-model-verify/test_artifact_roots.py evals/multi-model-verify/test_mirror_reaper.py -q
```
All exit 0. Confirm the staged blob of `tools/artifact-roots.ps1` is ASCII and LF
(`git show :tools/artifact-roots.ps1`). `Get-ChildItem C:\pxm` lists only the
three pre-existing names.

Stage by explicit path (never `git add -A`):
```
git add skills/multi-model-verify/references/model-prompting-notes.md skills/multi-model-verify/references/preflight-mirror.md tools/artifact-roots.ps1 evals/multi-model-verify/test_artifact_roots.py evals/multi-model-verify/test_mirror_reaper.py BACKLOG.md docs/superpowers/plans/2026-09-13-mirror-parent.md
git commit -m "apply the fable review: the notes' assert command names the repo, the parent itself answers outside for the mirror row, item 107 costs its remainder, and the plan record is corrected in place"
```
(The commit message contains no token that looks like a PowerShell flag.)

Report to C:\Temp\parallax-scratch\2026-09-13-mirror-parent\fable-fix-report.md:
per finding what changed (file:line), the commands run with condensed
output for both hosts, the C:\pxm listing, and any concern.
