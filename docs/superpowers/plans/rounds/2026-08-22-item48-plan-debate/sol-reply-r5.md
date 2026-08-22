The round-4 amendments reproduce both fail-open and fail-closed gates.

A. Amendment sweep

1. The widening count was corrected at only one site. The scanner says “across FOUR review rounds … EIGHT times” at `docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md:320-326`, but the Architecture still says “across three review rounds … five times” at `:15-17`; the record skeleton says the same and claims “nobody has produced a sixth yet” at `:121-125`; and Task 3 orders the final record to say “across three review rounds … FIVE times” at `:808-811`. Executing the plan writes the stale claim into the deliverable.

2. `NOT_EXEMPT` is contradicted by the classification instructions. The code identifies `feasibility-record.md` and `entry-points.tsv` as prefix-coverable records at `:426-437`, and applies that exception at `:513-520`. But Task 3 still orders “an EXPLICIT per-line row for every match inside the record directory” and says “no prefix row covers them” at `:711-716`. The standing rule likewise says matching lines added to `feasibility-record.md` require explicit rows at `:725-733`. Following those instructions recreates the stale-record failure because every explicit row is still checked by path, line, and digest at `:528-529`. The prose must exclude `NOT_EXEMPT`, or the loader should refuse explicit rows for those paths.

3. The staging checks are not executable assertions. Task 4 runs only `git ls-files … | wc -l` at `:1261-1265`, followed by prose saying “Expected: 5” at `:1267-1268`; Task 7 repeats that shape at `:1741-1748`. Neither command compares the count or exits nonzero when it is zero. Thus the alleged nonzero assertion remains fail-open.

4. The stated staging counts are also wrong on successful probe paths. Task 4 names five source files at `:824-830`, but the driver also leaves `parent-out.txt` and `child-out.txt` at `:944-946`, two JSON sidecars at `:1065-1066`, and `results.json` at `:1179-1180`. The plan stages the entire directory at `:1256-1258`, while `.gitignore:1-8` contains no rule covering those artifacts. A successful run therefore exposes ten files, not the claimed five.

   Task 7 similarly writes `results.json` on its successful-call path at `:1667-1673`, stages the whole directory at `:1741-1743`, but requires the count to be one at `:1748`. The plan explicitly permits “The call succeeds anyway” as a finding at `:1691-1692`, so this is a valid measurement outcome that the new check rejects.

5. The exemption remains wider than its justification. Its comment says “The scripts under them are EXECUTED” at `:412-414`, but the prefix exemption at `:421-437` covers every generated sidecar and result file except the two exact `NOT_EXEMPT` paths. Those artifacts are records, not executed scripts. Narrow the exemption to explicit executable artifacts or make non-code result files prefix-coverable.

B. `NOT_EXEMPT` and staging

The `NOT_EXEMPT` predicate itself correctly makes the two exact paths eligible for prefix coverage (`:513-520`). Its failure comes from contradictory instructions that still create explicit rows.

The staging repair can fail open because its count command never asserts, and fail closed because whole-directory staging includes outcome-dependent generated artifacts. Stage the intended executable files explicitly and use a command that exits nonzero when any expected path is absent.

C. Undeclared filter miss

`agents/flash-implementer.md:47` requires the preflight command “`agy models`”, and `agents/flash-implementer.md:78` explicitly says, “Run … `agy -p …`”. The BARE family names `codex`, `kimi`, and `claude`, generic call-operator forms, and bare `python`, but not bare `agy` (`docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md:382-392`). Neither live instruction contains a call operator, `.ps1`, `python`, or CI `run:` shape, so all three families miss it. This is distinct from the declared bare-`git` omission.

I searched bare native-client instructions, literal and variable call operators, Python process APIs, PowerShell job/remoting forms, script paths, and wrapped invocations.

FIX