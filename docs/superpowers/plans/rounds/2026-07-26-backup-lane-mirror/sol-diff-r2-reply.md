1. F2/F5 — containment visibility

The command is now consistently required for baseline, per-round, and write-probe captures, and the contract correctly explains why both `--ignored` and `-uall` are load-bearing (`skills/multi-model-verify/references/backup-lane.md:68-72,140-169`). I found no new correctness problem from using it; larger output is the intended cost of enumerating previously invisible paths.

Verdict: PASS.

2. F4 — content identity

The fix remains under-specified. “Path plus SHA-256” does not define:

- Recursive per-file treatment for directory subjects such as `References/`.
- Capture timing relative to remediation, copied inputs, and dispatch.
- Inclusion of inherited non-ignored untracked inputs.
- Inclusion of modified tracked review inputs in non-diff modes, which remain permitted with disclosure.

The prose names only copied-in and gitignored subject material, while elsewhere acknowledging inherited untracked and modified files (`skills/multi-model-verify/references/backup-lane.md:151-180`). The pin merely requires the phrase “content manifest”; it does not constrain scope, recursion, or timing (`evals/multi-model-verify/test_backup_lane.py:145-148,188-193`).

Verdict: FIX — specify a pre-dispatch, deterministically sorted manifest of repo-relative file paths plus SHA-256 of raw file bytes for every review-input file not bound by HEAD, recursively expanding directories and explicitly covering copied-in, ignored, non-ignored untracked, and permitted dirty-tracked inputs.

3. F8 — historical effort evidence

The contradiction is closed. A round without contemporaneous evidence is now recorded as having no verified pin, and the contract explicitly refuses to infer either override or provider-default operation (`skills/multi-model-verify/references/backup-lane.md:80-93`). The new pin requires both propositions (`evals/multi-model-verify/test_backup_lane.py:149-154`).

Verdict: PASS.

4. F10 — pin strength

Both previously weak pins now bite:

- The eval-consumer test requires the complete post-round equality clause already present in `evals.json` (`evals/multi-model-verify/test_backup_lane.py:200-221`; `evals/multi-model-verify/evals.json:95-105`).
- The remediation test now requires both the commit imperative and its mode-diff consequence (`test_backup_lane.py:250-270`; `skills/multi-model-verify/SKILL.md:85-90`).

Verdict: PASS.

The C9 wording deferral remains appropriate: the operational single-source sweep deliberately exempts its enforcement fixture, so no wrong action results (`evals/multi-model-verify/test_backup_lane.py:341-359`). I did not independently rerun the reported gates.

OVERALL VERDICT: FIX — F2/F5, F8, and F10 are closed without a new material defect; F4 still needs an executable manifest scope, format, and capture point.

