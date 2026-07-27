1. Manifest coverage

The baseline-based rule correctly eliminates the `core.autocrlf` false positives and covers ignored, untracked, and modified tracked entries (`skills/multi-model-verify/references/backup-lane.md:184-204`).

But it is not executable for tracked deletions. The baseline can list ` D path`, while the manifest requires exactly those paths and a SHA-256 of each file’s current raw bytes; a deleted path has no file or bytes (`backup-lane.md:184-190,205-210`). Other modes explicitly permit tracked modifications with disclosure, so mode diff’s clean-tree requirement does not remove this case (`backup-lane.md:218-220`).

Verdict: FIX — define coverage as currently present worktree files represented by baseline entries; omit deletion-only paths because HEAD plus the baseline already binds their absence. For rename/copy entries, explicitly hash the current destination path. Pin both mappings.

2. Pin-integrity fixes

The dispatch and resume pins now cover their complete `-p` payloads (`evals/multi-model-verify/test_backup_lane.py:80-111`). The evidence pin couples offset capture to inspection past that offset and pins write-probe configuration fidelity (`test_backup_lane.py:114-145`). The config sweep now pins the recording imperative (`test_backup_lane.py:289-319`). These exact weakening cases are closed.

Verdict: PASS.

OVERALL VERDICT: FIX — range `c73ca2f..e719634` still has one executable-contract defect: deletion-only baseline entries cannot produce the required content-manifest hash.