The plan is not trustworthy exactly as written. Its central completeness oracle misses a spec-defined entry point, and several later tasks can certify unsupported conclusions.

## A. Oracle adequacy, task by task

1. **Task 1 — broken results can pass.** The step promises to verify the criteria “are the backlog’s own, not a paraphrase” (`docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md:144`), but checks only whether the first 40 characters of each bullet occur anywhere: `missing = [w for w in want if w[2:42] not in rec]` (`:156`). Wrong suffixes, order, placement, skeleton headings, and unsupported metadata can all pass.

2. **Task 2 — broken results can pass the required failing run.** Its oracle only requires more than 150 detected hits, all unclassified, and exit 1 (`:343-352`). That proves the gate can fail on what the regexes detect, not that the scanner detects every entry point. The concrete miss is in B.

3. **Task 3 — broken results can pass.** Exit 0 means only “no detected hit lacks a syntactically valid row and no explicit row is stale” (`:304-326`). Nothing verifies that a classification or migration judgment is semantically correct. Prefix-covered hits are never individually classified (`:296-310`), and none of the required inventory prose at `:432-454` has an oracle.

4. **Task 4 — broken probes exit successfully.** The driver records `returncode`, stage A, and stage B (`:597-612`), but `main()` merely prints and returns normally (`:615-626`). Even though the prose says stage A false must stop the task (`:633-636`), the command itself exits 0 for false stage A, false stage B, or nonzero child return codes.

5. **Task 5 — no task-level oracle exists.** Its commands collect workflow text, job metadata, and local installation facts (`:672-733`), but nothing validates the completed section. All commands can complete while the environment conclusions or citations are wrong.

6. **Task 6 — no task-level oracle exists.** It equates files returned by `grep -rln "<script-basename>"` with modules that “exercise” the script (`:775-782`). A comment, constant, fixture, or assertion-only reference passes that search. No command validates the resulting coverage tables.

7. **Task 7 — no pass predicate exists.** A missing executable traceback is an accepted finding, while a successful invocation can also be accepted as evidence that the probe did not reproduce absence (`:891-910`). Nothing checks that the record accurately distinguishes those outcomes.

8. **Task 8 — no result oracle exists.** The commands fetch only job `startedAt` and `completedAt`, after which durations and savings are computed manually (`:942-971`). Arithmetic, job identification, and the savings inference are unchecked.

9. **Task 9 — broken verdicts can pass.** Its only mechanical check is another green survey (`:991-996`). No command validates the four MET/NOT MET answers, their citations, verdict consistency, collected residuals, or draft migration item (`:998-1045`).

## B. Completeness of the survey

Found: **host-inheriting direct script instructions or invocations written as a bare `.ps1` command**.

The spec expressly treats “Anything a subagent or skill instructs to be run” as an entry point (`docs/superpowers/plans/2026-07-27-0150-backlog.md:3531-3532`). One exists here:

> `` `tools/new-review-mirror.ps1 -RepoRoot <repo> -MirrorPath <scratch>`. ``  
> `skills/multi-model-verify/SKILL.md:94`

That line contains neither `powershell.exe`/`pwsh` nor any Task 2 launch-family token. The two families are exactly the expressions at `docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md:219-227`. Therefore both families miss this actual, spec-defined entry point.

The plan’s statement that “a missed entry point is a red gate rather than a silent omission” (`:107-113`) is wider than the script’s evidence.

## C. Sweep for claims wider than their evidence

I found these instances:

- **“Across every tracked file” is overstated.** The method makes that claim at `:111`, but the scanner silently continues past read failures and files containing NUL in their first 4096 characters (`:258-265`).

- **The `docs/` blanket classification defeats the claimed per-match review.** Task 3 says “`docs/` … is entirely historical record” and assigns every future match there `record/no-change` (`:413-416`). The reviewed plan itself is an active agent instruction—“Use … to implement this plan task-by-task” (`:3`)—so “entirely historical” is already false. New matches under that prefix will pass without being read.

- **The skeleton violates the record’s own evidence rule.** The global rule says every claim must carry inline evidence (`:37-40`), but the prescribed skeleton asserts the branch/head, host versions, and driver without citations or captured commands (`:81-84`).

- **Task 4 claims arbitrary-argument proof from a fixed corpus.** It tests ten literal payload elements (`:552-565`) yet commits under “preserves arbitrary arguments” (`:654-659`). The evidence supports those ten cases, not arbitrary arguments. It also uses a synthetic parent with only `$args` (`:498-526`), while a real migration target has named parameters (`tools/check-drift.ps1:30-34`).

- **Task 5 orders an unmade universal claim.** Its commands measure only the current machine (`docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md:713-719`), then require the record to state that any user who never installed PowerShell 7 has only `powershell.exe` (`:722-723`).

- **CI evidence is not revision-bound.** Task 5 collects each run’s `headSha` (`:687`) but never reads the workflow at that SHA; it combines current-file text with job-level metadata (`:690-699`). Thus the evidence does not prove that the cited historical job ran the currently read `pwsh` step.

- **Task 6’s shipped-surface claim exceeds its source list.** Its enumeration omits `hooks/*.ps1` (`:767-773`), although `hooks/hooks.json` executes `hooks/superpowers-review-companion.ps1` at `hooks/hooks.json:10` and again at `:22`. The resulting table cannot support the promised statement about the whole “shipped surface” (`docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md:793-796`).

- **Task 7 does not capture what the actual hook caller shows.** The probe claims it captures “verbatim what a user would see” (`:839-845`) but invokes Python’s `subprocess.run(["pwsh", …, "-Command", "Write-Output ok"])` (`:876-881`). The shipped hook instead invokes `pwsh … -File …superpowers-review-companion.ps1` (`hooks/hooks.json:10`). The probe measures Python’s caller path, not the hook runner’s presentation.

- **Task 8 does not measure the claimed saving.** It requests whole-job start and completion times (`docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md:950-965`). The Windows job contains shared checkout/setup/install work (`.github/workflows/skill-evals.yml:59-71`) and then separate sequential 5.1 and 7 steps (`:93-125`). Whole-job duration cannot isolate the time removed by deleting only the 5.1 step.

## D. Verdict logic

The abstract rule—YES only when every NO-criterion is measured NOT MET—is sound. Its implementation is not sufficient.

Task 9 permits only MET or NOT MET (`docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md:998-1009`); it has no UNKNOWN state. Yet Task 5 explicitly allows environments to remain “unproven” (`:728-733`), Task 6 allows scripts and host-sensitive behaviours to have no coverage under 7 (`:784-796`), and Task 7 may explicitly fail to reproduce a machine without PowerShell 7 (`:901-910`).

Those gaps are material requirements of Item 48: “Does 7 exist everywhere this must run?” and “Does each shipped script still behave under 7?” (`docs/superpowers/plans/2026-07-27-0150-backlog.md:3534-3543`). Neither question is itself a NO-criterion, and collected residual limits do not bar YES (`docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md:1011-1017`). Consequently, a YES can coexist with material unmeasured behaviour.

Require UNKNOWN, make UNKNOWN force CONDITIONAL or NO VERDICT, and require every material residual to be explicitly dispositioned before YES.

## E. Wrong ordering

- **Task 2 records N before its own scanner becomes tracked.** The scanner inventories only `git ls-files` (`:250-253`). Task 2 runs it before committing the newly created `survey.py` and TSV (`:343-358`); Task 3 then expects exactly the same N (`:374-386`). After the commit, `survey.py` is tracked and contains the very host and launch literals being scanned (`:219-227`), so Task 3 necessarily sees hits absent from Task 2’s N.

- **Savings precede the matrix decision they depend on.** Task 8 must state how much the change removes (`:958-971`), but Task 9 decides later which 5.1 refusal and re-exec cases remain in the matrix (`:1019-1035`). Retained 5.1 work must be defined before net savings can be measured.

- **The verdict precedes that same material matrix decision.** Task 9 writes the verdict in Step 2 (`:998-1009`) and only answers “What the test matrix becomes” in Step 4 (`:1028-1035`).

- **Task 3 violates the plan’s own file-scope rule.** The global constraint says no file outside the record directory and plan may be created (`:27-33`), but Task 3 creates `stubs.tsv` in the repository root (`:378-384`).

FIX