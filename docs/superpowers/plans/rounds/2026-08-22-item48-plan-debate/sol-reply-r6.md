The plan still contains a fifth fail-open staging gate.

A. Round-5 amendment sweep

1. Both new “assertions” exit successfully on failure. Task 4 runs:

> `test "$(git ls-files $REC/reexec/ | wc -l)" -eq 5 && echo STAGED_OK || echo STAGED_WRONG`

at `docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md:1313-1315`. When `test` is false, `echo STAGED_WRONG` succeeds, making the compound command’s final exit status zero. Task 7 repeats the same construction at `:1800-1803`. Use `test ... || { echo STAGED_WRONG; exit 1; }`, followed by `echo STAGED_OK`.

2. The cleanup amendment contradicts its staging prose. `run.py` deletes all four scratch files at `:1225-1233`, but Task 4 later says it “leaves `results.json` and four `*-out.*` scratch files” after success at `:1297-1300`.

3. Three instructions still name the removed `EXEMPT_FROM_PREFIX` mechanism at `:1284-1288`, `:1338-1340`, and `:1784-1789`. The actual mechanism is `EXEMPT_PREFIXES`, `EXEMPT_SUFFIXES`, and `EXEMPT_EXACT` at `:452-458`, applied at `:534-543`.

B. Suffix exemption

No planned executable artifact escapes it. Task 2 creates `survey.py` at `:266-268`; Task 4 creates four `.ps1` files and `run.py` at `:856-862`; Task 7 creates `probe.py` at `:1607-1609`; and the plan itself is covered by `EXEMPT_EXACT` at `:456-458`. Generated JSON and scratch artifacts are intentionally prefix-covered records, as stated at `:443-450` and enforced at `:534-543`.

I found no current fail-closed case in the suffix predicate itself. Its only present defect is the stale surrounding terminology above.

C. Filter sweep

None found beyond the declared bare-`git` omission. I checked literal, variable, quoted-path, and expression call operators; dot-sourcing; shebang and shell-command-substitution entry points; native clients; PowerShell jobs/remoting; .NET/WMI process launches; CI shell/run forms; and wrapped script instructions. The active pre-push hook’s relevant PowerShell launch remains visible as:

> `powershell.exe ... -File "$win_verifier"`

at `.githooks/pre-push:24`, which matches both the host and launch families at `docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md:395-413`.

D. Fresh-executor issue

The staging command is the execution blocker: it prints `STAGED_WRONG` but reports success, precisely the fail-open behavior the surrounding text claims to eliminate at `:1308-1318` and `:1802-1806`.

Separately, the named arm cannot supply one required table value. `run_named()` always writes `"first_difference": None` at `:1144-1150`, while the measurement table requires “the index of the first differing argument” for every arm at `:1262-1265`. Specify `N/A` for named dictionaries or return the first differing parameter key.

FIX