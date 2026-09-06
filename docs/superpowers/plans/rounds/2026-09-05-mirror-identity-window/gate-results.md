# Gate results, mirror identity window

Run at `8ecb177`, the head of `mirror-identity-window` after Tasks 1
through 4. Task 5 changes no source and produces this record only.

## The six CI tiers

| tier | command | result |
| --- | --- | --- |
| 1 | `skill_lint.py skills/multi-model-verify --strict` | PASS, 0 errors, 2 warnings, exit 0 |
| 1b | `skill_scanner.py skills` | clean, 0 CRITICAL / 0 WARN / 0 INFO, exit 0 |
| 1c | `check_exact_line_oracles.py` | clean, exit 0 |
| 2 | `run_trigger_evals.py` | PASS, 5 positives clear 5 near-misses (weakest 0.32 vs strongest 0.00), exit 0 |
| 2b | `python -m pytest evals -q` | **2917 passed, 14 skipped** in 1323.65s (22m03s), exit 0 |
| 2c | `backlog_lint.py` | clean, exit 0 |

Both tier-1 warnings are pre-existing size warnings on `SKILL.md`: 412
lines against a 400 warn threshold, and roughly 6496 tokens against a
6500 hard ceiling. The linter errors only ABOVE 6500, so these are
warnings and the tier passes. The headroom is worth naming anyway: Task 3
spent about eleven of the fifteen tokens that were free before it, and
the next addition to `SKILL.md`'s body breaks this tier.

## Both PowerShell hosts

`evals/multi-model-verify/test_review_mirror.py`, the module Tasks 1 and 2
changed, run under each host explicitly rather than letting the suite pick.

| host | result | elapsed |
| --- | --- | --- |
| `powershell` (Windows PowerShell 5.1) | 154 passed, 1 skipped | 98.73s |
| `pwsh` (PowerShell 7) | 154 passed, 1 skipped | 113.87s |

## A measurement that did NOT reproduce, and it is the backlog's

Backlog item 93 says this exact module takes **18m42s under PowerShell 7
against 94s under Windows PowerShell 5.1**, a factor of twelve, and that
every CI run and every both-host gate pays about eighteen minutes for it.
Measured here on the same module: **113.87s against 98.73s, a factor of
1.15.** The eighteen minutes are not present.

What this does and does not establish. It establishes that the gap is
absent at this commit, on this machine, for this module - the run above
is the whole evidence. It does NOT establish what closed it, and this
record does not guess. The obvious candidate is item 90, which shipped in
0.32.0 on the same day item 93 was measured and changed the mirror to
re-link directory links as junctions rather than copy through them; item
93's own text says it was measured "at item 90's Task 3", which is during
that work rather than after it. That is a hypothesis with a plausible
mechanism and NO measurement behind it here.

Item 93 is left OPEN and untouched. Correcting it means re-measuring
deliberately, on a stated commit, ideally on both sides of item 90's
merge - not editing a cost line on the strength of one incidental
observation. This paragraph is the pointer to that work.

## Not run

`run_behavioral_evals.py --changed` is Task 5 Step 3 and has NOT been
run. It makes real headless model runs graded by the cross-vendor
reviewer, spending from the same quota the diff debate that follows this
plan needs. The decision is the user's and is pending. Nothing above
depends on it; skill and prompt text did change, so it does apply, and
this line is here so a reader cannot mistake its absence for a pass.

## A plan defect in this task

Step 4 as written says `git add -A`. Blanket staging is banned by the
family git rules and a hook denies it. Staged by explicit path instead.
This is the fifth defect found by executing this plan rather than reading
it; the other four are in `README.md`.
