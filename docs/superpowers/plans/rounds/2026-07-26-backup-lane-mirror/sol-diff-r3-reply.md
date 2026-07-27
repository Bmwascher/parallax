F4

The working-tree coverage now stands: the exclusion test includes copied-in, ignored, non-ignored untracked, and modified tracked files; directories expand recursively; format, ordering, and capture timing are specified (`skills/multi-model-verify/references/backup-lane.md:175-198`). The pin constrains each of those properties (`evals/multi-model-verify/test_backup_lane.py:145-164`).

One gap remains: the mirror explicitly preserves `.git` (`backup-lane.md:121-129`), while the manifest includes every file present for which HEAD has no blob (`backup-lane.md:175-184`). Literally followed, this recursively hashes `.git` repository metadata—objects, logs, hooks, indexes, and configuration—which HEAD never represents. That is irrelevant, potentially large or volatile data, and the pin does not require its exclusion (`test_backup_lane.py:151-164`).

Verdict: FIX — define the manifest universe as worktree files excluding the root Git administrative entry (`.git`, whether file or directory), and pin that exclusion.

OVERALL VERDICT: FIX — the prior coverage, recursion, format, ordering, and timing gaps are closed, but range `c73ca2f..7ca532f` still over-includes `.git` metadata in the manifest.