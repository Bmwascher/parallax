The amended plan still reproduces the target defect class in several fixes.

## A. Sweep of the round-2 amendments

1. **The explicit-row exception has a fail-open oracle.** The scanner defines `unclassified` to exclude anything covered by a prefix (`docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md:464-470`), and `--emit` prints only `unclassified` rows (`:472-476`). Task 4 nevertheless tries to discover prefix-covered re-exec matches with `survey.py --emit` and treats a second empty result as proof that explicit rows exist (`:1142-1164`). With only the `docs/` prefix and no explicit re-exec rows, that command already prints zero—the expected result.

2. **The initial Task 3 exception has the same seam.** Each subagent is told to take only its own family (`:611-618`), while the exception requires explicit rows for every family match in the plan and record directory (`:645-652`). Once the first subagent adds the `docs/` prefix, later `--emit` runs suppress those plan/record matches. No oracle distinguishes explicit coverage from prefix coverage.

3. **The standing rule is not applied by Task 7.** The plan says any task adding a record-directory file must add explicit rows before committing (`:661-668`). Task 7 creates `missing-pwsh/probe.py` (`:1400-1404`), whose source contains `pwsh` and `subprocess.run` matches (`:1431-1490`), but its remaining steps only run, record, and commit the probe (`:1512-1565`). It has no explicit-row step.

4. **Task 4’s own file inventory omits one newly added script.** The standing-rule step names `child.ps1`, `child-named.ps1`, `parent.ps1`, and `run.py` (`:1142-1146`), but Task 4 also creates `parent-named.ps1` (`:742-747`). The path-wide command would catch it only if `--emit` exposed prefix-covered rows—which it does not.

5. **`not-a-launch` was added to code but not to the worker’s closed vocabulary.** `CLASSES` accepts `"not-a-launch"` (`:365-379`), while Task 3’s classification table ends with `record` and never presents `not-a-launch` as an allowed choice (`:620-638`). This is exactly the classification needed for the amendment’s broad variable-call alternative.

6. **The old incorrect CI citation remains in one amended comment.** The scanner still cites `.github/workflows/skill-evals.yml:70` (`:306-313`). Line 70 is `- name: Install pytest`; the `run:` invocation is `.github/workflows/skill-evals.yml:71`.

7. **Task 6’s workflow extraction remains too narrow.** It requests only 25 lines after `powershell-hosts` (`:1306-1315`). The job begins at `.github/workflows/skill-evals.yml:59`, while its actual host test-module lists occupy `:93-125`; the prescribed extraction ends before either list.

8. **Task 6 retains the old overclaim beside its correction.** It still says, “Only `runs` rows count as behaviour proven under a host” (`docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md:1365-1367`). Eleven lines later it correctly says a `runs` row proves invocation, not that the module passed (`:1376-1383`).

9. **Task 6 still combines a historical green run with a working-tree module list.** Its interface consumes Task 5’s revision-bound run (`:1297-1300`), but Step 1 reads only the working-tree workflow (`:1306-1315`). Task 5’s revision-bound command extracts only host/shell terms, not the historical run’s module list (`:1213-1221`). The record therefore cannot establish that the modules tabulated from the working tree are the modules that passed in the cited run.

10. **The timeout amendment still exits successfully on its probe-defect path.** `TimeoutExpired` writes a result and executes bare `return` (`:1491-1499`); `main()` is then called without `SystemExit` (`:1507-1509`). Yet the task says timeout is a probe defect that must be fixed (`:1516-1526`). The command exits 0 over that defect.

11. **Two smaller stale interfaces remain.** Task 2 promises a final survey line ending at `<stale> stale` (`:263-268`), while the implementation also reports files not scanned (`:494-497`). Task 9 says the test-matrix answer was written in Step 2 (`:1741-1751`), but residual collection is now Step 2 and the matrix answer is Step 3 (`:1665-1692`).

The explicit-row problem should be enforced inside `survey.py`: for the plan and `<REC>`, prefix coverage must not count. Then ordinary `unclassified`, `--emit`, and the final green gate all enforce the standing rule mechanically.

## B. `parent-named.ps1` and replacement `main()`

The new code’s core flow is coherent for the fixed parameter set:

- `parent-named.ps1` binds the three parameters, records them, reconstructs the argument list, and forwards that list through both forms (`:1032-1069`).
- `run_named()` invokes that parent, reads both stages, and returns the same oracle keys as the positional arm (`:976-1025`).
- The replacement `main()` runs all eight combinations and fails on nonzero parent return, inexact stage A, or absent child output (`:1072-1097`).

I found no wrong-key, missing-forward, or cannot-fail defect in those three code blocks themselves.

Two surrounding instructions remain wrong:

- The required table asks for `bound_exact` on named arms (`:1121-1126`), but `run_named()` returns `stage_b_child_exact`, not `bound_exact` (`:1014-1025`).
- Stage-A diagnosis tells the worker to inspect `parent-out.txt` against the positional payload (`:1106-1112`), while named arms write `parent-out.json` and compare against `NAMED_EXPECTED` (`:983-1019`).

## C. Widened third family

A real entry-point shape is still dropped: **a command whose backticked invocation wraps across lines before its flags**.

These are active instructions:

> `OTHERWISE, run \`tools/kimi-lane-lock.ps1`  
> `-ResolveOwner\` once …`  
> `skills/multi-model-verify/references/backup-lane.md:119-120`

> `Remove with \`tools/new-kimi-lane-home.ps1`  
> `-Path <debate-home> …`  
> `skills/multi-model-verify/references/backup-lane.md:136-137`

> `Log the lane in with \`tools/new-kimi-lane-login.ps1`  
> `-LaneHome <lane-home> …`  
> `skills/multi-model-verify/references/backup-lane.md:141-143`

The scanner examines one line at a time (`docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md:412-415`). On the first line, `.ps1` is neither followed by a same-line flag nor enclosed by a closing backtick; the continuation line contains the flag but no `.ps1`. None of the seven alternatives at `:355-362` matches these instructions.

The variable-call alternative is also intentionally broad:

> `$tail = ($argList | ForEach-Object { & $quote $_ }) -join " "`  
> `tools/codex-tool-surface-probe.ps1:193`

That starts no process, so the new `not-a-launch` class is necessary; its omission from Task 3’s table makes this broadening operationally incomplete.

FIX