# Fable-review fix wave report, branch mirror-parent

Worktree: `C:\Users\Brandon\Documents\_worktrees\parallax-mirror-parent`
Base head: `2df3d45`. New head after this commit: `3032444`.

## Per-finding changes

### F1 — the notes' own command is not executable
- `skills/multi-model-verify/references/model-prompting-notes.md:822` — the
  "Review mirror:" bullet's command line now reads
  `` `tools/artifact-roots.ps1 -RepoRoot <repo> -Assert <mirror-path> -Expect reviewMirror` ``.
- `evals/multi-model-verify/test_artifact_roots.py:86` (in
  `test_fixed_rows_state_their_reason_outside_the_region`) — pin widened to
  `assert "-RepoRoot <repo> -Assert <mirror-path> -Expect reviewMirror" in tail`.

### F2 — the pre-build check and the reap guard must agree on the parent itself
- `tools/artifact-roots.ps1` (`-Assert` block, around line 364) — the
  membership loop now sets `$mayEqual = ($r.Name -ne "review mirror root")`
  and only allows `Equals` when `$mayEqual` is true, so the mirror parent
  itself never matches by equality, only `StartsWith`.
- `evals/multi-model-verify/test_artifact_roots.py` —
  `test_expect_review_mirror_answers_for_the_declared_parent` gained a loop
  over `(r"C:\pxm", "C:/pxm/")` asserting `returncode == 1` and
  `"outside every retained root"` for the bare parent.
  `test_expect_accepts_the_expected_root_and_reports_it` left unchanged
  (confirmed unaffected).
- Prose (F2c), one sentence each, no reflow:
  - `skills/multi-model-verify/references/model-prompting-notes.md:823` —
    "before the build" now reads "before the build (the parent itself
    answers outside: it is never a tree), and ..." (this line was combined
    with the F1 edit since they are adjacent).
  - `skills/multi-model-verify/references/preflight-mirror.md:23` —
    "exit 0 is the only clean answer, and a mirror built anywhere else..."
    became "exit 0 is the only clean answer, the parent itself answers
    outside because it is never a tree, and a mirror built anywhere
    else...".

### F3 — item 107's Cost line described the pre-branch state
- `BACKLOG.md`, item 107 — `Cost:` line replaced with the remainder-focused
  text the brief specified. Digest recomputed:
  `python evals/tools/backlog_lint.py --digests BACKLOG.md` printed
  `107 fb0b98b97df3`; `Verified:` line set to
  `Verified: 2026-09-13 fb0b98b97df3`. `python evals/tools/backlog_lint.py`
  exits 0. Only item 107 touched.

### F4 — the frozen plan carries two texts the branch corrected
`docs/superpowers/plans/2026-09-13-mirror-parent.md`, corrected in place
with dated brackets (never appended below):
- Task 1 Step 2's quoted replacement bullet: the command line gained
  `-RepoRoot <repo>`; a `[Corrected 2026-09-13 after the Fable
  whole-branch review: ...]` paragraph added immediately after that code
  block.
- Task 3 Step 2's quoted doctor text: "row of the round-artifact-roots"
  became "row of model-prompting-notes.md's round-artifact-roots"; a
  `[Corrected 2026-09-13: ...]` paragraph added immediately after that
  code block.
- Task 1's Interfaces line: "any depth, or the parent itself, the same
  rule as every other row" became "any depth below it; the parent itself
  answers outside, unlike every other row, so the pre-build check agrees
  with the reap guard — corrected 2026-09-13 after the Fable review".
- Decision 2 in "Decisions the handoff left open": "and the same
  membership rule the resolver's `-Assert` applies to every other row."
  became "and the resolver's `-Assert -Expect reviewMirror` answers the
  same way for the parent itself (outside), a deviation from the other
  rows corrected 2026-09-13 after the Fable review."

### F5 — Group 7 duplicated the fake-plugin setup
- `evals/multi-model-verify/test_mirror_reaper.py` — added module-level
  helper `doctored_plugin(tmp_path, replacement)` immediately before the
  "Group 7" comment block. `test_an_unreadable_parent_refuses_every_reap`
  and `test_a_roots_tool_that_exits_nonzero_refuses_every_reap` now call
  `doctored_plugin(tmp_path, "Canonical review mirror root: `C:/pxm/`\n")`
  and `doctored_plugin(tmp_path, "")` respectively, use the returned
  emitter path in `run_ps`, and their copied setup blocks were removed.
  Every assertion in both tests is unchanged.

### F6 — no backslash in a skill reference file
- `skills/multi-model-verify/references/backup-lane.md` — `C:\pxm\kv-<tag>`
  → `C:/pxm/kv-<tag>` (one line).
- `skills/multi-model-verify/references/model-prompting-notes.md:819` —
  `build \`C:\pxm\<tag>\`.` → `build \`C:/pxm/<tag>\`.`
- `skills/multi-model-verify/references/preflight-mirror.md` — lines 13
  and 133: `C:\pxm\kv-<tag>` → `C:/pxm/kv-<tag>`,
  `C:\pxm\kv-<tag>-2` → `C:/pxm/kv-<tag>-2`.
- `evals/multi-model-verify/test_mirror_reaper.py` (in
  `test_preflight_mirror_reference_states_the_end_of_life_rule`) —
  `assert r"C:\pxm\kv-<tag>" in body` → `assert "C:/pxm/kv-<tag>" in body`.
- Verified: `grep -rnF '\' skills/multi-model-verify/` prints nothing.

### F7 — the plan file was untracked
- `docs/superpowers/plans/2026-09-13-mirror-parent.md` staged by explicit
  path and committed; it now exists in history as part of this commit
  (`git status` before the commit showed it `??`; the commit's diffstat
  shows `create mode 100644` for it).

## Commands run, both hosts, condensed output

```
python evals/tools/skill_lint.py skills/multi-model-verify --strict
  -> PASS - 0 error(s), 2 warning(s) (SKILL.md line/token count warnings,
     pre-existing, no ERROR line). Exit 0.

python evals/tools/backlog_lint.py
  -> backlog lint: clean. Exit 0.

$env:PARALLAX_PS_HOST = "powershell.exe"
python -m pytest evals/multi-model-verify/test_artifact_roots.py -q
  -> 71 passed in 35.35s
python -m pytest evals/multi-model-verify/test_mirror_reaper.py -q
  -> 45 passed in 28.27s
python -m pytest evals/multi-model-verify/test_multi_model_verify.py evals/multi-model-verify/test_backup_lane.py -q
  -> 248 passed, 1 skipped in 2.98s
python -m pytest evals/multi-model-verify/test_artifact_roots.py evals/multi-model-verify/test_mirror_reaper.py evals/multi-model-verify/test_contract_coverage.py -q
  -> 177 passed in 62.75s

$env:PARALLAX_PS_HOST = "pwsh.exe"
python -m pytest evals/multi-model-verify/test_artifact_roots.py -q
  -> 71 passed in 46.53s
python -m pytest evals/multi-model-verify/test_mirror_reaper.py -q
  -> 45 passed in 30.83s
python -m pytest evals/multi-model-verify/test_artifact_roots.py evals/multi-model-verify/test_mirror_reaper.py -q
  -> 116 passed in 70.02s
```

Every command exited 0.

Staged blob check: `git show :tools/artifact-roots.ps1` piped through
Python — ASCII-decodes cleanly and contains zero `\r` bytes (LF only),
confirmed both by a plain `file` check (`ASCII text`) and a byte count
(`CR count: 0`).

## C:\pxm listing (after all runs)

```
8904109a
k10392
k92104
```

Only the three pre-existing directories. `C:\kv-bl-*` (f, h, k, m) and
`C:\kvs-bl-*` (f, h, k, m) were never touched (confirmed present and
unmodified after the runs).

## Commit

`3032444` — "apply the fable review: the notes' assert command names the
repo, the parent itself answers outside for the mirror row, item 107
costs its remainder, and the plan record is corrected in place"

8 files changed: `BACKLOG.md`,
`docs/superpowers/plans/2026-09-13-mirror-parent.md` (new),
`evals/multi-model-verify/test_artifact_roots.py`,
`evals/multi-model-verify/test_mirror_reaper.py`,
`skills/multi-model-verify/references/backup-lane.md`,
`skills/multi-model-verify/references/model-prompting-notes.md`,
`skills/multi-model-verify/references/preflight-mirror.md`,
`tools/artifact-roots.ps1`.

`git status` after the commit: clean working tree.

## Concerns / deviations

The brief's F6 instructions explicitly required editing
`skills/multi-model-verify/references/backup-lane.md` (the
`C:\pxm\kv-<tag>` → `C:/pxm/kv-<tag>` fix), but the brief's final "Stage
by explicit path" `git add` list omitted that file. Since F6 required the
edit and the task is to land the whole fix wave in ONE commit with a
clean working tree, I staged and committed `backup-lane.md` alongside the
files the brief's list named, rather than leaving that required edit
uncommitted. No other deviation from the brief.
