# fable-reviewer whole-branch review, range a48c35f..2df3d45 (branch mirror-parent), 2026-09-13

Seat: parallax:fable-reviewer (same-harness, read-only; agent a1b90caa763edcb37). Brief: brief-fable-diff-r1.md. Raw reply verbatim below.

---

### Strengths

- The parent guard is genuinely last and fail-closed. `tools/write-attestation.ps1:233-260` (package lines 1533-1561) replaces the two early `return $full` paths with an `$identityOk` flag so the head rule, the remediation-commit rule and the new parent rule run in one straight line; `test_the_parent_itself_is_never_a_reap_path` (`evals/multi-model-verify/test_mirror_reaper.py`, package lines 883-892) pins both the ordering and the exact `StartsWith`/`Equals` form.
- The parent read cannot degrade into an accepting parent. `Resolve-MirrorParent` (`tools/write-attestation.ps1:62-124`) exits 2 on a missing tool, a thrown invocation, a non-zero tool exit, unparsable JSON, a missing `reviewMirror` key, a row with no `<` placeholder, and an unrooted parent. The tool it calls ends with an explicit `exit $exitCode` (`tools/artifact-roots.ps1:414`), so `$LASTEXITCODE` is never stale. Both failure directions have live tests: `test_an_unreadable_parent_refuses_every_reap` and `test_a_roots_tool_that_exits_nonzero_refuses_every_reap` (package lines 895-963), the second added from a ledger minor rather than deferred.
- The in-process `$args` fallback is sound. `tools/artifact-roots.ps1:63-78` scans `GetCommandLineArgs()` for its own `$PSCommandPath`; when the emitter is the `-File` target that scan never matches and `$argv = @($args)` carries the emitter's `-RepoRoot <repo> -Json`. The success cases under `pxm` prove it on both hosts.
- The guard's input is already canonical and link-checked. `$p` is built from `GetFullPath($raw)` (`tools/write-attestation.ps1:149,186`), so `..` traversal and separator variants normalize away, and `Test-PathOrAncestorIsLink` (`tools/review-tree-removal.ps1:13-22`) walks every ancestor, so a junction or mount point anywhere under `C:\pxm` is refused before the parent rule is reached.
- The retired form cannot come back silently: the `<TEMP>` sweep shape plus its can-fail proof (`test_artifact_roots.py`, package lines 399-400, 426-433), and the parent-spelling binder with `[/\\]+` and the `.` lookahead (package lines 448-488) tie every prose example to the declaration row.
- The `pxm` fixture is contained: a fresh `C:\pxm\t-<8 hex>` per test, `rmtree` with `onexc` clearing git's read-only bits, and every tree a success case names sits inside it (package lines 553-563 and the relocated cases). CI runs Python 3.12 (`.github/workflows/skill-evals.yml:27,99`), so `onexc` is available there.
- Constraints held: `SKILL.md` carries exactly the one quoted line edit (package lines 1033-1034); `never inside the reviewed repository` is whole on one physical line (`model-prompting-notes.md:808`); the eight declaration lines are unchanged in count; all three commit messages are flag-free.

### Issues

#### Critical

None.

#### Important

- `skills/multi-model-verify/references/model-prompting-notes.md:822` tells the session to run `tools/artifact-roots.ps1 -Assert <mirror-path> -Expect reviewMirror`. The tool refuses that command line: `tools/artifact-roots.ps1:125` fails with `-RepoRoot is required` (exit 2) before any assertion runs. The correct form is the one `references/preflight-mirror.md:22` carries, `-RepoRoot <repo> -Assert <scratch> -Expect reviewMirror`. This is the declaration's own file describing its own check, and the pin `"-Expect reviewMirror" in tail` (package line 235) accepts either spelling, so nothing catches it. The failure direction is closed (a session copying it gets exit 2, not a false clean), which is why this is Important rather than Critical. It is a plan defect: Task 1 Step 2 dictates this text verbatim (plan lines 227-228).

#### Minor

- The pre-build check and the reap guard disagree on the parent itself. `tools/artifact-roots.ps1:379` (package line 1390) accepts `Equals($r.Root)`, so `-Assert C:\pxm -Expect reviewMirror` exits 0, while the emitter refuses that path (`tools/write-attestation.ps1:257`). Both prose sites say exit 0 "is the only clean answer" (`preflight-mirror.md:23`, `model-prompting-notes.md:822-824`), so a session that passes the parent as `<scratch>` gets a clean pre-build answer for a tree that can never be reaped, and `new-review-mirror.ps1 -MirrorPath C:\pxm -Force` would rebuild over every sibling. Plan decision 1's interface states the assert rule deliberately, so this is a plan-level choice worth one sentence in the prose ("a direct child, never the parent"), not a code fix.
- `test_mirror_reaper.py` Group 7 duplicates the fake-plugin setup verbatim in two tests (package lines 902-913 and 941-951). A `doctored_plugin(tmp_path, replacement)` helper would keep the third failure direction, if one is ever added, from copying it a third time. Polish only.
- Ledger record: the Task 2 note "Equals branch unreachable behind the .git rule" is wrong in its reasoning, not its conclusion. `C:\pxm` can itself carry a `.git` directory at the attested head (a session that passed `-MirrorPath C:\pxm`), and then the `Equals` branch is the rule that fires. The code is right to keep it; the ledger line should not be cited as a reason to remove it later.

Answers to the five questions, with the evidence above:

1. Readers still pointing at temp or the drive root: none. The surface sweep for `temp directory`, `$env:TEMP`, `GetTempPath`, `<TEMP>`, `drive root`, `kv-<tag>` and `C:\kv-` across `skills/`, `agents/`, `commands/`, `tools/` and `hooks/` finds only the doctor's legacy line (`commands/doctor.md:413-417`, labelled as such), historical prose in the notes bullet, and three unrelated `$env:TEMP` uses (`commands/doctor.md:68-69,243,347`, `tools/check-drift.ps1:817`, `tools/new-kimi-lane-home.ps1:182`) that belong to the lane login and the drift worktree, not mirrors.
2. A tree outside `C:\pxm` through an accepted spelling: not found. `GetFullPath` canonicalizes `..` and slashes; `C:/pxmx/` fails the separator-suffixed `StartsWith`; `\\?\C:\pxm\...` and `\\localhost\C$\pxm\...` are refused (they do not start with `C:/pxm/`), which is the safe direction; a subst drive or a junction/mount point under the parent is refused by the ancestor link walk. Case variants are the same NTFS directory.
3. A failed parent read reading as a parent: no path found; every branch of `Resolve-MirrorParent` exits 2 before `Resolve-ReapPath` is called, and `$mirrorParent` is only ever the function's return value.
4. Tests under the real `C:\pxm`: nothing outside the per-test `t-*` directory is touched; the held-handle and held-sidecar cases close their handles before teardown; the junction target lives in `tmp_path`. Stated limit: if `rmtree` fails even after the chmod retry, the `t-*` directory is orphaned and no later sweep removes it; the doctor would count it. `C:\pxm` itself is created on a fresh runner and never removed (ledger, no action).
5. Executable as written: `preflight-mirror.md:22` and doctor check 10 are; `model-prompting-notes.md:822` is not (the Important above).

Not verified by me, named as gaps: `skill_lint` token count after the SKILL.md edit, the item 107 digest, ASCII/LF on the two tools, and both-host pytest runs. The ledger and the session's gate are the evidence for those.

### Ledger minors triage

- T1: notes prose names the emitter's guard: ride, already landed (`model-prompting-notes.md:816-817`, "The attestation emitter's reap guard").
- T1: spelling floor raised to 4: ride, already landed (package line 478).
- T1: `PARENT_SPELLING` takes `[/\\]+` and `.` in the lookahead: ride, already landed (package lines 449, 487-488).
- T1: parent pin duplicated at `test_artifact_roots.py` (row pin and resolver assertion); `C:` row resolved on every invocation: ride, the double pin is the binding the plan asked for, and a host without `C:` fails legibly.
- T2: tool-exit-nonzero test: ride, already landed (`test_a_roots_tool_that_exits_nonzero_refuses_every_reap`).
- T2: `Equals` branch, fixture creating `C:\pxm`, Group 7 above Group 6: ride all three; see the Minor on the `Equals` reasoning, the branch stays.
- T3: item 107 Cost line still describes the pre-branch state: fix-before-merge, one line plus a digest recompute, and the sentence is false the moment this ships.
- T3: frozen plan Task 3 doctor text carries the unprefixed citation: fix-before-merge as a dated in-place correction, in the same fix wave, so the plan and the shipped doctor agree.
- T3: doctor ordering anchor is first-occurrence: ride, the section is short and the anchor names both words.

### Assessment

Ready to merge: With fixes

The guard, its parent read and the tests do what the plan says and fail closed in every direction I could name; the one Important is a non-executable command in the declaration's own prose, a plan-authored defect that the pins do not catch, plus two backlog and plan record lines from the ledger. All are small text edits for the fix wave before the mode-diff debate.
