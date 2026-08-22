The amended plan is still unsound. Several fixes reproduce the same width defect inside themselves.

## A. Sweep of the amended plan

1. **The top-level completeness claim was not updated.** The plan still says the inventory’s “completeness is enforced” and a missed entry point becomes a red gate (`docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md:9-14`). The record skeleton and scanner docstring still say “two regex families across every tracked file” (`:107-113`, `:257-262`), while the implementation has three families (`:301-314`) and expressly concedes they are “A FILTER, NOT A PROOF” (`:289-291`). Files can also be reported `NOT SCANNED` without making the final exit nonzero (`:419-434`).

2. **The `docs/` exception does not cover the plan it claims to cover.** The amendment requires explicit rows only “inside the record directory” (`:564-569`), but then says the reason is that the prefix otherwise classifies “this plan” as never executed (`:570-573`). The plan and record directory are separate allowed paths (`:27-29`, `:51-53`); this plan is outside `<REC>`. It therefore remains swallowed by `docs/ * * record no-change`. The claim that future entry points under `docs/` will no longer be silently absorbed (`:573-575`) is also wider than the exception.

3. **The named-parameter measurement remains narrower than claimed.** The amendment says positional `$args` is not the real shape (`:834-840`), but the parent still has no `param()` block and forwards only `$args` (`:682-710`). `run_named` merely sends parameter-looking strings through that positional parent (`:863-888`) to a named child (`:842-858`). It measures binding at the child, not re-execution by a parent whose own named parameters were already bound.

4. **Named stage A is not measured.** `run_named` writes no `stage_a_parent_exact` or equivalent field (`:871-900`), although the run instructions say stage-A failure makes an arm unmeasured (`:914-920`) and the required eight-row table demands stage A for named arms (`:925-934`). That table cannot be produced honestly from the prescribed result object.

5. **“Every shipped script declares named parameters” is false.** That universal appears at `:834-840`. The shipped-script enumeration includes `hooks/*.ps1` (`:1092-1098`), while `hooks/superpowers-review-companion.ps1` begins executable processing with `try` and reads stdin (`hooks/superpowers-review-companion.ps1:12-13`), not a named-parameter declaration.

6. **Task 5’s Linux command cannot determine what its prose asks.** It says to determine whether “ANY step” in the Ubuntu job invokes `pwsh`, but reads only four lines after `runs-on` (`docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md:1013-1019`). The actual job continues from `.github/workflows/skill-evals.yml:17` through `:47`; the command does not survey that job.

7. **Task 6 still calls declarations “proven behaviour.”** It reads the current workflow and candidate test modules (`docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md:1081-1127`) and then reports how much behaviour “is proven under 7 today” (`:1136-1141`). Its interface consumes only Task 3’s inventory (`:1074-1075`), not Task 5’s revision-bound successful run. A test that invokes a script is not proven green under a host without evidence that the cited module completed successfully under that host.

8. **The production-hook assertion is unmeasured.** Task 6 calls the hook script “the ONLY one already running under PowerShell 7 in production” based on checkout configuration (`:1105-1108`). The plan itself says the versioned plugin-cache copy is what actually runs and changes only after version update plus `plugin update` (`:622-625`). No task inspects the installed cache before making the production claim.

9. **Task 7 retains the claim its amendment disclaims.** The new docstring correctly says Claude Code’s presentation “was not measured” (`:1192-1193`), but Step 3 still calls a Python `FileNotFoundError` traceback “the user-facing failure mode” (`:1251-1254`). If parent-environment resolution makes the call succeed, the plan says absence was not reproduced (`:1257-1266`), yet Step 4 unconditionally requires “captured failure text” (`:1268-1274`).

10. **Task 8 still asks for an undetermined net answer.** It correctly says net saving is not determined until Task 9 defines retained 5.1 cases (`:1331-1338`), but then requires a sentence saying how much of Item 44’s 57 minutes “this change would remove” (`:1343-1344`). At that point only a gross upper bound is supported.

## B. Sweep of the amendments themselves

The new regressions are:

- The `docs/` exception explicitly names this plan as its reason but does not include this plan in its scope (`:564-575`).
- The third family’s narrowing omits variable-resolved call-operator launches; see C.
- The named arm adds a named child rather than a named parent and omits named stage-A evidence (`:682-710`, `:842-900`).
- The named-arm rationale introduces the false “every shipped script” universal (`:834-840`).
- The missing-`pwsh` amendment narrows its docstring correctly but leaves the old “user-facing failure mode” conclusion in place (`:1192-1193`, `:1251-1254`).
- The step-timing amendment correctly labels net unknown but leaves an instruction to state the removed portion as though net were known (`:1331-1344`).
- The per-family amendment adds progress lines but no duplicate-row oracle; see D.
- The new scanner comment cites `.github/workflows/skill-evals.yml:70` as the live CI instance (`:280-287`), but line 70 is the step name and the invocation is at `.github/workflows/skill-evals.yml:71`.

## C. Third regex family

Found: **call-operator invocation through a variable**.

The bare regex recognizes literal client names, literal `.ps1` paths followed by flags, literal `.ps1` paths after `&`, and CI `run:` lines (`docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md:309-313`). It does not recognize these live launches:

> `$stdout = & $LockScript @LockArgs`  
> `tools/new-kimi-lane-home.ps1:152`

> `$stdout = & $LockScript @LockArgs`  
> `tools/new-kimi-lane-login.ps1:214`

The variables are assigned real `.ps1` paths at `tools/new-kimi-lane-home.ps1:96-97` and `tools/new-kimi-lane-login.ps1:107-108`.

It also misses the native-client launch:

> `& $KimiBinaryPath "login"`  
> `tools/new-kimi-lane-login.ps1:442`

None of those lines contains a host token, launch-family token, literal client command, or literal `.ps1` path.

## D. Per-family split

Yes, it has both seams.

- **Lost prior-family rows can pass an intermediate task.** Each subagent checks only its own `FAMILY` line, while the whole exit remains expected red until `bare` finishes (`docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md:487-499`, `:593-595`). The launch task could lose host rows and still report its own family green. The final whole-survey run would eventually catch that loss, but the launch task’s stated oracle would not.

- **Double-written rows are never detected.** `load_rows()` assigns `rows[(rel, int(line), fam)] = ...`, silently overwriting an earlier row with the same key (`:369-389`). Coverage then asks only whether the key exists (`:400-406`), so contradictory duplicates still produce `FAMILY … 0 unclassified`. The inventory count command counts raw TSV rows (`:609-615`), so duplicates can also corrupt the classification totals even while the survey is green.

Reject duplicate explicit and prefix keys during `load_rows()`, and require each split task to keep every previously completed family at zero.

## E. Other defects

- **Task 9 uses residuals before collecting them.** Criterion rule 4 requires dispositioning “Any residual limit from Step 4” (`:1431-1434`), but Step 4 occurs afterward (`:1440-1446`). Residual collection must precede criterion adjudication.

- **The verdict placeholder has no explicit replacement instruction.** Step 1 permits one `NOT YET WRITTEN` inside Verdict (`:1371-1381`), but Steps 2 and 3 only say to write/add subsections (`:1383-1404`). No final oracle reruns the placeholder check after writing the verdict.

FIX