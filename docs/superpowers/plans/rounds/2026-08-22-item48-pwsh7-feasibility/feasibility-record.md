# Feasibility record: moving everything to PowerShell 7 (backlog item 48)

Date started: 2026-08-22 (local, CDT).
Repo: branch `item51-inline-brief-transport`, cut from `main` at `a3134dcd76d9253057bf24935f3d7a7eef8eb0e4`.
Hosts under test: Windows PowerShell 5.1.26100.9168 and PowerShell 7.6.5.
Driver: Opus 5, subagent-driven per task.
Header facts captured, not asserted from memory, by running
`git rev-parse --abbrev-ref HEAD`, `git merge-base main HEAD`, and
`$PSVersionTable.PSVersion.ToString()` under each of
`C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe` and
`C:\Program Files\PowerShell\7\pwsh.exe` (task-1-report.md carries the
captured output).

**This is an investigation. Nothing in this cycle is repinned and no 5.1
test is deleted.**

## Verdict

NOT YET WRITTEN. Filled by the final task, after every measurement below.

## What would make the verdict NO

Copied verbatim from backlog item 48 BEFORE any measurement was made, so
the answer cannot be shaped by the effort already spent:

- Any entry point that cannot be made to reach 7 - most likely a hook or a
  scheduled task registered outside this repo's control.
- A re-exec that cannot pass arguments through provably intact.
- A user-facing failure mode worse than the bugs being removed.
- Any need to keep a 5.1 code path "just in case", which would mean paying
  for both hosts and testing one.

## Method

The entry point inventory is produced by `survey.py` in this directory and
verified by re-running it, not by rereading it. Two earlier hand
inventories of this item were wrong: the first in three of four entries,
the second in four further ways after claiming to fix the first.

The script matches THREE regex families across every tracked file it can
read, and FAILS if any match lacks a written classification. So a DETECTED
entry point cannot be passed over silently.

It does not do more than that, and this record does not claim it does:

- The families are a filter. They were two when first written and have been
  corrected repeatedly, every time because a reviewer produced a live entry
  point in this repo that the filter did not match. The count and the
  enumerated list live in `survey.py`'s FAMILIES comment and nowhere else;
  copy them from there. There is no argument that the current filter is
  enough - only that nobody has produced the next miss yet, which is not
  the same statement.
- A green run says every detected match carries a row. It says nothing
  about whether the row is CORRECT.
- A file the script cannot read is listed as `NOT SCANNED`, by name. An
  unread file is not a clean one.

## Entry point inventory

Produced by classifying every match `survey.py` detects across the three
regex families (`host`, `launch`, `bare`), split by family across three
tasks in that order, each committing its own rows and each judged per line
by reading the line and its surrounding code, never from the path or from
expectation. Two hand inventories of this exact question shipped wrong
before this method existed.

**Final survey run**, verbatim:

```
FAMILY bare: 5491 hits, 0 unclassified
FAMILY host: 1143 hits, 0 unclassified
FAMILY launch: 529 hits, 0 unclassified
SURVEY: 7163 hits, 7163 classified, 0 unclassified, 0 stale, 0 files not scanned
```

Exit code: `0`.

**What this proves, and no more.** This green run proves every detected
match carries a syntactically valid row, and that no row points at a line
that has changed or gone. It does NOT prove any classification is CORRECT,
and it does not prove the three families detect every entry point.

**Why a re-run today prints different numbers.** Re-running the command
above after this section existed prints higher counts (`7215 hits, 7215
classified, 0 unclassified, 0 stale`, still exit code `0`) than the 7163
captured above. The cause is this section itself: its own prose now
quotes `powershell.exe`, `pwsh.exe` and `.ps1` text about the inventory,
adding matches inside `feasibility-record.md`. That file is covered by
the `docs/` prefix row, so the new matches need no rows and do not turn
the survey red; the 7163 above is the Step 3 run captured before this
section was written, not a number this record keeps in sync with itself.

### Classification counts

Produced by:
`awk -F'\t' '!/^#/ && NF==6 {print $5}' docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/entry-points.tsv | sort | uniq -c | sort -rn`

| count | classification |
|---|---|
| 599 | not-a-launch |
| 211 | test-harness |
| 106 | doc-instruction |
| 54 | launch-nonhost |
| 38 | host-pin-nonexec |
| 30 | fixture |
| 15 | launch-explicit |
| 13 | ci |
| 7 | launch-inherit |
| 4 | host-pin-exec |
| 1 | record |

One row of the 7163 is a prefix row (`docs/	*	*	-	record	no-change`); the
count above is the per-row classification, not per-hit, so the table's
total (1078) is the hand-written row count, not the hit count (7163) the
prefix row also covers.

### `must-change` rows, whole file

Every row whose `migration` value is `must-change`, one line each. Rows
from the `host` and `launch` family tasks are described from reading the
same lines during this pass, not re-classified; only the `bare` rows below
were classified by this task.

- `.githooks/pre-push:24` (host-pin-exec / launch-explicit) — hardcodes
  `powershell.exe` as the attestation verifier's interpreter; must invoke
  `pwsh.exe` (or resolve dynamically) once 5.1 is gone.
- `.github/workflows/skill-evals.yml:74` — the `run:` step body of the
  "PowerShell-facing tests under Windows PowerShell 5.1" job step; the
  whole step must be removed or repurposed with 5.1 dropped.
- `.github/workflows/skill-evals.yml:95` — `PARALLAX_PS_HOST:
  powershell.exe`, the 5.1 job step's env line; the whole step (this line,
  and `:96`/`:97` below) must go with it. (`:112`, the PAIRED `pwsh.exe`
  env line for the step that SURVIVES, is `no-change` — see the
  correction note at the end of this list.)
- `.github/workflows/skill-evals.yml:96`, `:97` (bare) — `run: >` and
  `python -m pytest ...`, the body of that same 5.1 job step. Read on
  their own these lines are host-neutral text; they are `must-change`
  because deleting the step they belong to (per `:95` above) deletes them
  with it — the step and its env line, run header, and command body stand
  or fall together, and the `host` family's `:95` row already reads
  `must-change`.
- `evals/multi-model-verify/test_attestation.py:10` — docstring stating
  the module "runs wherever a PowerShell host exists: Windows
  powershell.exe or pwsh"; the 5.1 half of that sentence must go.
- `evals/multi-model-verify/test_attestation.py:30`, `:36` — the
  `POWERSHELL` host-selector's comment and its
  `shutil.which("powershell")` fallback; the fallback must be dropped.
- `evals/multi-model-verify/test_backup_lane.py:1322,1328,1334,1338,1340,
  1354,1360,1373,1374,1376,1378,1388,1395,1401,1408,1413` —
  `test_check_workflow_paths_flags_host_parity_gap` and its neighbours
  build synthetic workflow text asserting BOTH a `powershell.exe` step and
  a `pwsh.exe` step exist with parity; dropping 5.1 removes the thing
  these tests enforce, so they must be rewritten or removed.
- `evals/multi-model-verify/test_backup_lane.py:1741` — a separate test,
  roughly 330 lines later in the same file (not one of the
  `test_check_workflow_paths_flags_host_parity_gap` neighbours above): it
  reads the real `skill-evals.yml` and asserts a `PARALLAX_PS_HOST:` marker
  exists for BOTH `"powershell.exe"` and `"pwsh.exe"`; the 5.1 half of that
  assertion must go with the step it checks for.
- `evals/multi-model-verify/test_codex_context_probe.py:52` — comment
  stating `powershell-hosts` runs the module "under BOTH powershell.exe
  and pwsh.exe"; the 5.1 half must go.
- `evals/multi-model-verify/test_codex_context_probe.py:58` — the
  `POWERSHELL` selector's `shutil.which("powershell")` fallback; drop it.
- `evals/multi-model-verify/test_codex_round_evidence.py:58` — same
  `POWERSHELL` selector pattern; drop the `powershell` fallback.
- `evals/multi-model-verify/test_codex_tool_surface_probe.py:40`, `:515` —
  the selector fallback, and a test that explicitly resolves both
  `shutil.which("powershell")` and `shutil.which("pwsh")` to drive every
  present host; both must lose their 5.1 half.
- `evals/multi-model-verify/test_home_skill_canary.py:62` — same selector
  fallback pattern; drop it.
- `evals/multi-model-verify/test_kimi_credential_state.py:70` — same
  selector fallback pattern; drop it.
- `evals/multi-model-verify/test_kimi_lane_home.py:61` — same selector
  fallback pattern; drop it.
- `evals/multi-model-verify/test_kimi_lane_home.py:238` — docstring on
  `_clean_env` explaining why `PSModulePath` is scrubbed: a PS7-flavoured
  `PSModulePath` shadows "the 5.1 copy of Microsoft.PowerShell.Security"
  inside a `powershell.exe` child; the whole rationale disappears with 5.1.
- `evals/multi-model-verify/test_kimi_lane_lock.py:30` — same selector
  fallback pattern; drop it.
- `evals/multi-model-verify/test_kimi_lane_lock.py:225` — docstring noting
  the `powershell` fallback "resolves under System32 with no spaces"
  unlike the `pwsh` fallback under Program Files; the 5.1 half of that
  comparison disappears with 5.1.
- `evals/multi-model-verify/test_kimi_lane_login.py:47` — same selector
  fallback pattern; drop it.
- `evals/multi-model-verify/test_kimi_lane_login.py:234` — same
  PSModulePath/`Get-Acl`-shadowing rationale as
  `test_kimi_lane_home.py:238`; the rationale disappears with 5.1.
- `evals/multi-model-verify/test_kimi_round_evidence.py:89` — same
  selector fallback pattern; drop it.
- `evals/multi-model-verify/test_lane_credential_live.py:60` — same
  selector fallback pattern; drop it.
- `evals/multi-model-verify/test_lock_protocol_live.py:21` — docstring
  explaining "Measurement 20's divergence test... needs BOTH
  powershell.exe and pwsh.exe to have actually run"; the whole rationale,
  and the test it describes, must go with 5.1.
- `evals/multi-model-verify/test_lock_protocol_live.py:55` — the
  `POWERSHELL` selector's `shutil.which("powershell")` fallback; drop it.
- `evals/multi-model-verify/test_lock_protocol_live.py:71` — inside
  `ps_host()` (not `required_hosts()`, which starts lower at `:77`), the
  `pytest.fail` text "and neither powershell nor pwsh is on PATH"; the 5.1
  half of that message must go.
- `evals/multi-model-verify/test_lock_protocol_live.py:83` — inside
  `required_hosts()`, the literal `for name in ("powershell.exe",
  "pwsh.exe")` loop that demands BOTH hosts be on PATH; must be rewritten
  to require only `pwsh.exe`.
- `evals/multi-model-verify/test_lock_protocol_live.py:78` — docstring on
  `ps_host()` stating "the plan's own verification runs this module
  twice, once per host"; false once there is one host.
- `evals/multi-model-verify/test_lock_protocol_live.py:381`, `:382`,
  `:400` — `test_measurement_20_ticks_and_date_string_types_diverge_
  across_hosts`, which asserts `powershell.exe` and `pwsh.exe` return
  DIFFERENT `ConvertFrom-Json` types for the same value; the test's whole
  premise is the divergence between two hosts, so it must be removed with
  5.1.
- `evals/multi-model-verify/test_multi_model_verify.py:2954`, `:2961`,
  `:2999` — `os.name != "nt"` skip-reason strings and comments naming
  "drives powershell.exe"; the module they gate hardcodes `powershell.exe`
  (see the next bullet, `:2960`/`:2962`/`:2998`/`:3000`) and must change
  with it.
- `evals/multi-model-verify/test_multi_model_verify.py:2960`, `:2962`,
  `:2998`, `:3000` — the two `subprocess.run(["powershell.exe", ...])`
  calls (`test_run_state_machine` and `TestBriefEncodingOverStdin._run`)
  and their `"-File", str(...)` argument-list halves; both hardcode
  `powershell.exe` as the literal interpreter and must be changed to
  `pwsh.exe`.
- `evals/multi-model-verify/test_review_mirror.py:38` — comment stating
  the `powershell-hosts` job "runs this module under BOTH powershell.exe
  and pwsh.exe"; the 5.1 half must go.
- `evals/multi-model-verify/test_review_mirror.py:42` — same selector
  fallback pattern; drop it.
- `evals/multi-model-verify/test_skill_report_shapes.py:17` — docstring
  stating "CI already runs this directory under both Windows PowerShell
  and pwsh"; false once there is one host.
- `evals/multi-model-verify/test_skill_report_shapes.py:45` — same
  selector fallback pattern; drop it.
- `evals/tools/check_workflow_paths.py:41,42,43` — docstring/comment
  defining the required host MULTISET as "exactly one `powershell.exe`
  and one `pwsh.exe`"; the checker's whole contract changes with 5.1 gone.
- `evals/tools/check_workflow_paths.py:85` — `REQUIRED_HOST_NAMES =
  {"powershell.exe", "pwsh.exe"}`; must drop `"powershell.exe"`.
- `evals/tools/check_workflow_paths.py:153` — comment restating the
  multiset requirement; same change as above.
- `evals/tools/drift_statemachine_tests.ps1:542` — `if (-not $psHost) {
  $psHost = "powershell.exe" }`, the harness's default host; must default
  to `pwsh.exe` (or the harness's whole dual-host framing must go).
- `evals/tools/lane_credential_live_support.py:84` — `resolve_ps_host()`
  docstring; drop the `powershell` half of the fallback description.
- `evals/tools/lane_credential_live_support.py:89` — the
  `shutil.which("powershell")` fallback inside `resolve_ps_host()`; drop
  it.
- `evals/tools/lane_credential_live_support.py:98` — `clean_env()`
  docstring citing the same PS7-shadows-5.1 `PSModulePath`/`Get-Acl`
  rationale; disappears with 5.1.
- `README.md:312` — "`pwsh` (PowerShell 7) for the hook; Windows
  PowerShell 5.1 for the drift watch scheduled task"; the 5.1 half of the
  Requirements line must go.
- `tools/check-drift.ps1:68` — `$appId =
  '{...}\WindowsPowerShell\v1.0\powershell.exe'`, the toast notifier's
  hardcoded AppID path; must point at the PS7 identity once 5.1 is gone.
- `tools/check-drift.ps1:96` (host and launch rows, both `must-change`) —
  `$action = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File
  ..."`, the scheduled task's registered action; must register `pwsh.exe`
  instead.
- `tools/check-drift.ps1:21` — comment: "Written for Windows PowerShell
  5.1 (what schtasks runs): no &&, no ternary, ASCII ONLY"; the whole
  premise (a script written for 5.1's syntax limits) goes away once 5.1
  is dropped.
- `tools/check-drift.ps1:405` — comment: "an over-boundary scenario
  naming pwsh.exe proves a value past the ceiling is reported"; the
  surrounding paragraph's premise — that 5.1 is the default and pwsh.exe
  is named as the one exception (`:406`-`:407`) — goes away with 5.1.
- `README.md:413`, `:414` (bare) — `powershell tools/check-drift.ps1
  -Register` / `-TestNotify`; both name the literal 5.1 launcher
  (`powershell`, not `pwsh`) and must change to `pwsh` once 5.1 is
  dropped.
- `commands/doctor.md:340` (launch and bare rows, both `must-change`) —
  `powershell -NoProfile -File <installPath>\tools\codex-context-probe.ps1
  ...`; same literal-launcher problem as above, must change to `pwsh`.
- `skills/multi-model-verify/SKILL.md:326` (launch and bare rows, both
  `must-change`) — `powershell -NoProfile -File
  <plugin-root>/tools/write-attestation.ps1 ...`; same literal-launcher
  problem, must change to `pwsh`.
- `evals/multi-model-verify/fixtures/stub-appserver/stub-appserver.cmd:14`
  (host and launch families, both rows) — `powershell.exe -NoProfile
  -NonInteractive -File "%~dp0stub-appserver.ps1" %*`. This is live
  executable code, not description: the file's own comment at `:12`-`:13`
  states that driving the probe through THIS file is what proves the
  `.cmd` branch launches at all, and the line it drives through hardcodes
  `powershell.exe`. Settled to `must-change` on both rows (the `host`
  family's row previously read `unknown`; see the correction note below):
  once 5.1 is gone, `powershell.exe` either does not exist or is no
  longer the intended target, so the line must change to `pwsh.exe` for
  the stub to keep proving what it exists to prove.

### `unknown` rows, whole file

Every row whose `migration` value is `unknown`, with why it could not be
determined from the line. `migration` is a property of the LINE, not of
the family row — one line has one answer, and where the `host` and
`launch` rows for the same line disagreed (`stub-appserver.cmd:14`,
below), that has been settled to a single value rather than left as two
answers; the settlement is recorded in the `must-change` list above, not
here.

- `evals/multi-model-verify/test_backup_lane.py:270` — an `assert` string
  checking that `backup-lane.md` documents `-ResolveOwner`'s four-name
  "TRANSPORTS" allowlist, `pwsh.exe`, `powershell.exe`, `cmd.exe`,
  `conhost.exe`. Whether dropping 5.1 requires removing `powershell.exe`
  from that allowlist depends on whether any process could still present
  as `powershell.exe` in a PS7-only world (e.g. a leftover 5.1 install on
  a user machine) — a question about the *environment* the code runs in,
  not about the line itself.
- `skills/multi-model-verify/references/backup-lane.md:111` — the prose
  documenting that same four-name transparent-hosts list. Same
  undeterminable-from-the-line reason as above.
- `tools/kimi-lane-lock.ps1:887` — `$script:TransparentHosts =
  @("pwsh.exe", "powershell.exe", "cmd.exe", "conhost.exe")`, the actual
  list. Same reason: whether `"powershell.exe"` must be removed depends on
  whether the ancestry walk can still legitimately meet that name after a
  5.1 drop, which this line does not answer.

### What this method cannot see

- **The versioned plugin cache copy of `hooks/hooks.json`.** That copy,
  not the checkout, is what actually runs, and it only changes on a
  version bump plus `plugin update`. The survey reads tracked checkout
  files; it cannot see whether the installed cache has drifted from them.
- **An already-registered scheduled task.** `tools/check-drift.ps1
  -Register` writes the host into the task's action string at
  registration time; a task registered before a code change keeps running
  the OLD action until someone re-registers it. The survey reads source,
  not the Windows Task Scheduler.
- **Any instruction a human or agent follows that is not written in a
  tracked file.** A verbally-relayed or memory-carried instruction to run
  something under a specific host leaves no line for the survey to match.
- **Any file listed as `NOT SCANNED` by the survey, by name.** This run
  reports `0 files not scanned`, so there is currently none to name; a
  future run that cannot read or decode a tracked file would list it here
  instead of counting it clean.
- **A classification that is syntactically valid and semantically
  wrong.** The survey enforces that every match has a row and that the
  row's digest matches the current line; it has no way to check that the
  chosen classification is the CORRECT one for what the line does.
- **Anything UNTRACKED.** `git ls-files` lists tracked files only, so a
  generated or `.gitignore`d file is invisible to the scan. The
  auto-triage wrapper scripts under `tools/drift-reports/` are the live
  example: they invoke a client and are not in the index, so no run of
  this survey will ever see them.
- **A shape the filter does not match at all, so no row exists and this
  record cannot list it as `must-change`.** `--emit` only ever offers a
  row for a DETECTED match; a shape none of the three families' regexes
  catch leaves nothing to classify and nothing to sweep for. Named
  instance: `README.md:412`,
  `powershell tools/check-drift.ps1            # one-shot` — the first
  line of the SAME fenced block whose next two lines, `:413` and `:414`,
  ARE in the inventory as `must-change` (they end in a flag, which the
  `bare` family's `.ps1` alternative requires; `:412` ends in a `#`
  comment instead, so no alternative matches it). It invokes 5.1 by name
  and a migration would have to edit it exactly like its two neighbours.
  `survey.py` was NOT widened to catch this shape: every count in this
  task was measured against the filter as it stands, and widening it now
  would invalidate all 1078 hand-written rows and this whole inventory.
  The plan's own remedy for a known miss is to NAME it, as this bullet
  and the bare-`git` bullet below both do, not to chase it into the
  filter. Consequence stated plainly: the `must-change` count above (83)
  is therefore known to be deflated by at least this one instance.
- **A bare `git` invocation, deliberately.** Matching bare `git` was
  measured to cost 179 further hits, almost all prose and shell plumbing,
  against a class that never starts a PowerShell host — a measured trade,
  not an empty set. Its instance is named in `survey.py`'s own comment:
  `tools/check-drift.ps1:987`.

This list is not itself provably complete, and a blind-spot list that
reads as complete is the same defect one level up. The count is not
restated here from memory or from this instruction; it is copied from the
single place that carries it, `survey.py`'s own FAMILIES comment:

> THE CORRECTIONS, enumerated. Across FIVE review rounds a reviewer
> produced a live entry point this filter did not match NINE times:
>   1-2. two classes prompted the third family at all;
>   3-4. two more widened it (call operator through a variable; flagless
>        instruction invocations);
>   5.   Start-Job joined the launch family;
>   6.   the line-wrapped backtick form;
>   7-8. the generic call operator with a literal command, and bare
>        `python`;
>   9.   bare `agy`, the Flash implementer's client - live at
>        agents/flash-implementer.md:47 and :78, and used across six
>        non-docs files.
>
> Nobody has produced a tenth. That is the only honest statement available,
> and it is not the same as saying there is none.
>
> ONE KNOWN MISS IS LEFT IN DELIBERATELY, with its instance named. Bare
> `git` invocations - tools/check-drift.ps1:987, `git -C $worktree commit`
> - are NOT matched. Matching bare `git` costs 179 further hits, almost all
> of them prose and shell plumbing, against a class that never starts a
> PowerShell host. That is a measured trade and not an empty set: the
> instance above is real and is not in the inventory.

## Measurement 1: re-exec fidelity

Measured by `<REC>/reexec/run.py`, which drives a PARENT script under one
host, has it forward its own arguments to a CHILD script under a NAMED
target host, and compares what each side actually received (as UTF-8 hex
dumps for the positional arm, as parsed JSON for the named arm) against
what was sent. Two stages: Stage A is what the PARENT received (the
control - if this is wrong, the probe measured nothing about forwarding).
Stage B is what the CHILD received after the parent forwarded (the
question). Two forwarding forms: `splat` (native `@args`/`@forward` through
the PowerShell call operator `&`) and `escaped` (the parent hand-builds a
quoted command-line string via an `Esc` function and starts the child
through `System.Diagnostics.ProcessStartInfo`). Two argument shapes:
positional (`$args`, ten hostile strings) and named (three parameters,
one holding an embedded quote and an em dash, another holding spaces and
a trailing backslash). Eight arms in total. Full output verbatim in
`<REC>/reexec/results.json`.

**Stage A never failed.** Every one of the 8 arms shows
`stage_a_parent_exact: true` - the parent always received exactly what
`run.py` sent it, so every stage B result below is measuring forwarding,
not a broken control. (If the parent did not receive what was sent,
nothing downstream is measurable, so this means the task does not stop
early; had any Stage A been false the task would have reported BLOCKED
instead of writing this section.)

`first difference` for the named shape names the first PARAMETER NAME, in
ALPHABETICAL order over the union of expected and received keys
(`run.py:164-166`), that differs - not send order. `routeNote` was sent
first and also differed for `ps51/splat/named`; `path` sorts first
alphabetically, which is why it is the name shown.

| host | form | shape | return code | child ran | stage A exact | stage B exact | first difference |
|---|---|---|---|---|---|---|---|
| ps51 | splat | positional | 0 | yes | true | **false** | index 2 (`has"quote`) |
| ps51 | splat | named | 0 | yes | true | **false** | `path` |
| ps51 | escaped | positional | 0 | yes | true | true | none |
| ps51 | escaped | named | 0 | yes | true | true | none |
| pwsh7 | splat | positional | 0 | yes | true | true | none |
| pwsh7 | splat | named | 0 | yes | true | true | none |
| pwsh7 | escaped | positional | 0 | yes | true | true | none |
| pwsh7 | escaped | named | 0 | yes | true | true | none |

"child ran" is `stage_b_child_count is not None` for every arm - every
child wrote its output file, including the two corrupted arms. That
matters because it means the two `false` rows are a CORRUPTION finding,
not a never-started child: `ps51/splat/positional`'s child received only 8
of the 10 sent items (`stage_b_child_count: 8` against `sent_count: 10`),
and `ps51/splat/named`'s child bound all three parameters but with wrong
values - `routeNote` lost its embedded quotes (`a "quoted" note — here`
arrived as `a quoted note — here`) and `path`'s trailing backslash is
gone, with a quote standing in its place (`C:\dir with space\` arrived as
`C:\dir with space"`). What produced that substitution is not recorded by
this run - `results.json` holds the observation, not a cause, and no
mechanism is asserted here.

**Positional payload, verbatim (`PAYLOAD` in run.py):**

```
"plain"
"has space"
'has"quote'
'odd"quote"count"'
"em\u2014dash"
""
"trailing\\"
"semi;colon &amp"
"$var and `backtick`"
"-looks-like-a-flag"
```

**Named payload, verbatim (`NAMED` sent / `NAMED_EXPECTED` bound, in run.py):**

```
NAMED = ["-Register", "-RouteNote", 'a "quoted" note \u2014 here',
         "-Path", "C:\\dir with space\\"]
NAMED_EXPECTED = {"register": True,
                  "routeNote": 'a "quoted" note \u2014 here',
                  "path": "C:\\dir with space\\"}
```

**Answer to the NO-criterion.** A 5.1 script CAN re-exec into PowerShell 7
with these argument shapes intact - but only under the ESCAPED forwarding
form (a hand-built, hand-quoted command-line string passed through
`ProcessStartInfo`), never under the native `@args`/`@forward` SPLAT form.
Under Windows PowerShell 5.1, splat corrupted both the positional payload
(the child received 8 of 10 items and the first index that differs is 2;
which two items were dropped is not recorded by this run - the positional
arm keeps no per-item child data on the success path, by design, per
`run.py:201-204`) and the named payload (an embedded quote and a trailing
backslash both mangled). The escaped form survived every payload shape
under BOTH parent hosts, and PowerShell 7 as the PARENT host survived
every payload shape under BOTH forwarding forms. The CHILD host was
PowerShell 7 in every one of the eight arms - `run.py:63` and `run.py:112`
pin `PROBE_TARGET_HOST` to `PWSH` unconditionally - so no arm measured
PowerShell 5.1 as a target; the corruption is specific to 5.1 acting as
the SPLAT-forwarding parent, not to PowerShell 7 as a target, and not to
escaping as a technique.

**Width of the evidence.** This measured ten positional payload shapes and
one named-parameter set (three parameters, one holding an embedded quote
and an em dash, another holding spaces and a trailing backslash) - not
arbitrary arguments. Item 48's NO-criterion asks about arguments passing through
"provably intact"; what is proved here is that these eleven shapes survive
under the escaped form and that the same eleven shapes do NOT all survive
under 5.1's native splat form. It does not establish that EVERY possible
argument string survives the escaped form, only that this hostile set -
spaces, quotes, an odd quote count, an em dash, an empty string, a
trailing backslash, a semicolon and ampersand, a dollar sign and
backtick, and a leading-dash flag-like token - does.

**Residual limits, named:**

- **Command-line length.** Not measured against the ~32767-character
  Windows command-line ceiling; every payload item here is short. A
  migration relying on the escaped form for a very large brief (the kind
  `multi-model-verify` sends) is not covered by this measurement.
- **The host's own `-File` parsing.** This measured the escaped form and
  the splat form end-to-end - through the target host's own `-File`
  argument parsing, not isolated from it - so a stage-A pass and a
  stage-B fail together localize the corruption to what happens BETWEEN
  the parent's command-line construction and the CHILD host's own
  argument binding; this measurement cannot further separate "the parent
  built a bad command line" from "the child host's `-File` parsing
  mangled a well-formed one" beyond what `parent_bound`/`child_bound` in
  `results.json` show for the named arm.
- **Parameter shapes not tried.** Arrays, `ValueFromRemainingArguments`,
  and a script that re-execs ITSELF (rather than a sibling script) were
  not measured.
- **One machine, one build of each host.** All eight arms ran on this one
  machine against exactly one installed build of each host: Windows
  PowerShell `5.1.26100.9168` and PowerShell `7.6.5`, captured by running
  `$PSVersionTable.PSVersion.ToString()` under each of the two absolute
  paths `run.py:22-23` pins. Neither host's build is recorded inside
  `results.json` itself. These match the two versions captured
  independently by Task 1 for the record's own header (line 5), so the
  two measurements agree rather than diverge. This measurement says
  nothing about a different build of either host, or a second machine.

## Measurement 2: is PowerShell 7 present

Answers the blunt question under one of the four pre-committed NO-criteria
("any entry point that cannot be made to reach 7") for the four places this
code has to run: the Windows CI runner, the Linux CI runner, a developer
machine, and a plugin user's machine. Only the developer machine (this one)
is directly observable; the other three are evidenced differently, and each
subsection below says which.

**What the workflow file declares (`.github/workflows/skill-evals.yml`),
working tree read via
`grep -n "runs-on\|shell:\|pwsh\|powershell" .github/workflows/skill-evals.yml`:**
`:17` `runs-on: ubuntu-latest`; `:53`, `:55` comment prose mentioning
`pwsh`/`powershell.exe`; `:59` `powershell-hosts:`; `:60`
`runs-on: windows-latest`; `:74`, `:75`, `:78`, `:80`, `:87`, `:91` more
comment prose; `:95` `PARALLAX_PS_HOST: powershell.exe`; `:112`
`PARALLAX_PS_HOST: pwsh.exe`. No `shell:` key appears anywhere in the file
(the grep for it produced zero hits).

### Windows CI runner

Evidence, not declaration: `gh run list --workflow skill-evals.yml --limit 5
--json databaseId,headSha,status,conclusion,createdAt` (run 2026-08-22)
returned the most recent successful run as `databaseId 32391262449`,
`headSha a3134dcd76d9253057bf24935f3d7a7eef8eb0e4`, `conclusion: success`,
`createdAt: 2026-08-20T16:18:35Z` — that SHA is the same commit this
record's own header (line 4) names as the branch cut point.
`gh run view 32391262449 --json jobs --jq '.jobs[] | {name, conclusion,
startedAt, completedAt, runnerName}'` returned the `powershell-hosts` job
with `conclusion: success`, `startedAt: 2026-08-20T16:19:31Z`,
`completedAt: 2026-08-20T17:05:16Z`. (`runnerName` came back `null` for
both jobs — GitHub-hosted runners do not report a runner name through this
field; that is a property of the API, not evidence of anything about the
runner.)

A green `powershell-hosts` job, `runs-on: windows-latest`, whose two steps
(`skill-evals.yml:93-108` and `:110-125`) set `PARALLAX_PS_HOST:
powershell.exe` and `PARALLAX_PS_HOST: pwsh.exe` respectively and then run
`python -m pytest` against the same eleven `evals/multi-model-verify/`
modules, is direct evidence that a `pwsh.exe` host existed and worked on
`windows-latest` for run `32391262449` on 2026-08-20. This proves PowerShell
7 was present and functional on that one runner image on that one date; it
does not prove every future `windows-latest` image carries it, only that the
image GitHub served for this run did.

**Revision binding.** `gh run view 32391262449 --json headSha --jq
'.headSha'` returned `a3134dcd76d9253057bf24935f3d7a7eef8eb0e4`. That SHA
exists locally (`git cat-file -e` succeeded), so `git show
a3134dcd76d9253057bf24935f3d7a7eef8eb0e4:.github/workflows/skill-evals.yml
| grep -n "runs-on\|shell:\|pwsh\|powershell"` was run directly (not the
working tree read as a stand-in) and returned the identical line numbers
and text as the working-tree read above — no drift. This is not a
coincidence to be glossed over: the working tree happens to sit at that
same commit right now, but the comparison was still made against the
commit's own blob via `git show`, not assumed from the tree matching by
name.

### Linux CI runner

`awk '/^  skill-evals:/{f=1} f&&/^  [a-z-]+:/&&!/^  skill-evals:/{exit}
f{print NR": "$0}' .github/workflows/skill-evals.yml | grep
"pwsh\|powershell\|shell:\|run:"` was run over the WHOLE `skill-evals:`
job (`skill-evals.yml:16-47`), not just the lines after `runs-on`. It
returned five `run:` step headers (`:28`, `:36`, `:39`, `:42`, `:45`), none
of which contain `pwsh` or `powershell`, plus two more hits at `:53` and
`:55`. Both of those are comment lines (`#  lock that read every lock as
unusable on pwsh...` and `#  powershell.exe when both are installed...`),
part of the prose block at `:49-58` that explains why the `powershell-hosts`
job below exists — not invocations. So: **zero steps in the `ubuntu-latest`
job invoke `pwsh` or `powershell`.**

PowerShell 7's presence on the `ubuntu-latest` Linux runner is **unproven by
this repo's own evidence.** Nothing in this workflow starts a PowerShell
host on Linux, so there is no green job to point at the way there is for
Windows. What would prove it: a Linux CI step that runs `pwsh -Command
'$PSVersionTable.PSVersion'` (or equivalent) and captures a real version
string, the way `powershell-hosts` does for Windows.

### Developer machine (this one)

Measured directly. `where.exe pwsh` returned two paths: `C:\Program
Files\PowerShell\7\pwsh.exe` and
`C:\Users\Brandon\AppData\Local\Microsoft\WindowsApps\pwsh.exe`. Then
`"C:\Program Files\PowerShell\7\pwsh.exe" -NoProfile -Command
"$PSVersionTable.PSVersion.ToString()"` returned `7.6.5` — matching the
`7.6.5` already captured in this record's header (line 5) and re-captured
independently by Task 4. PowerShell 7 is present and working on this
machine, absolute path confirmed.

### Plugin user's machine

Not measurable at all from here — no telemetry, no fleet, no way to run a
command on a machine this session cannot reach.

**The half-requirement that already exists regardless of any migration:**
`hooks/hooks.json:10` and `:22` (both rows present in
`entry-points.tsv:159-160` (`host` family) and `:424-425` (`launch`
family), classified `host-pin-exec` / `launch-explicit`, `no-change`) each
invoke `"command": "pwsh -NoProfile -NonInteractive -File
\"${CLAUDE_PLUGIN_ROOT}/hooks/superpowers-review-companion.ps1\""`. Any
plugin user who has the hook installed and enabled already needs `pwsh` on
PATH today, before any 5.1-removal work — this is a fact about the repo as
it stands, not a claim about any user's machine.

**The preinstall claim**, in the cited form the brief requires (background
knowledge is not an acceptable substitute for a claim this specific):
Microsoft's own installation documentation, `Install PowerShell 7 on
Windows`, https://learn.microsoft.com/en-us/powershell/scripting/install/installing-powershell-on-windows
(read 2026-08-22), states: "PowerShell 7 doesn't replace Windows PowerShell
5.1. It installs to a new directory and runs side-by-side with Windows
PowerShell 5.1," and, describing the Start Menu entries left after
installing PowerShell 7: "The first and last entries shown are for Windows
PowerShell 5.1, which are installed by default on Windows." Read together,
Windows PowerShell 5.1 ships by default and PowerShell 7 is a separate,
opt-in install (WinGet, MSI, MSIX, ZIP, or `dotnet tool`) that a user or an
administrator has to add. So a plugin user's machine having `pwsh` present
is **unproven** for any given machine, and per this citation is **not the
default state** of a stock Windows install; it is present only where
someone installed it. What would additionally prove it for a *specific*
fleet: a device inventory or telemetry report showing `pwsh.exe` present
across the actual population of plugin users, which this measurement does
not have access to.

## Measurement 3: behaviour under 7

Answers which host-sensitive behaviours already shipped in this repo are
KNOWN to work under PowerShell 7, versus which are only declared to. Item
48's own warning is precise about the shortcut this measurement must not
take: "Not 'does it start'. 0.16.0's lock STARTED fine on 7 and did not
lock." So this section maps COVERAGE - which modules actually invoke which
script as a process, and whether that invocation sits inside a run that is
known to have passed under `pwsh.exe` - and does not re-run the suite
itself.

### Step 1: the dual-host CI job's module list

`.github/workflows/skill-evals.yml:59` opens job `powershell-hosts`,
`runs-on: windows-latest`. Two steps run the SAME eleven-module list, once
per host: `:93` "PowerShell-facing tests under Windows PowerShell 5.1"
(`:95` `PARALLAX_PS_HOST: powershell.exe`, modules at `:98`-`:108`), then
`:110` "PowerShell-facing tests under PowerShell 7" (`:112`
`PARALLAX_PS_HOST: pwsh.exe`, modules at `:115`-`:125`). Both step bodies
list the identical eleven modules, verbatim:
`test_attestation.py`, `test_codex_context_probe.py`,
`test_codex_tool_surface_probe.py`, `test_review_mirror.py`,
`test_kimi_round_evidence.py`, `test_kimi_lane_lock.py`,
`test_lock_protocol_live.py`, `test_kimi_credential_state.py`,
`test_kimi_lane_login.py`, `test_kimi_lane_home.py`,
`test_lane_credential_live_support.py`. Selection is a hand-written list
in the workflow file, not a glob - the job's own comment at `:73`-`:92`
states the intent ("EVERY dual-host module, not just the lock") but
nothing enforces the list is exhaustive.

**Revision binding.** Task 5 bound its cited green run
(`32391262449`/job `96497936725`, `conclusion: success`) to
`headSha a3134dcd76d9253057bf24935f3d7a7eef8eb0e4`, which this record's own
header (line 4) names as this branch's cut point.
`git show a3134dcd76d9253057bf24935f3d7a7eef8eb0e4:.github/workflows/skill-evals.yml`
read directly (not the working tree as a stand-in) and re-filtered the same
way as above returned line-for-line identical step names and module lists
to the working-tree read. So the module list above is the one that SHA's
run actually exercised, not a working-tree list paired with a run from
elsewhere. Re-pulling the job's own log directly
(`gh run view --job 96497936725 --log`, run just now, not copied from the
dispatch note) confirms real execution rather than a skip: `773 passed in
1363.25s` under `PARALLAX_PS_HOST: powershell.exe`, then `773 passed in
1356.53s` under `PARALLAX_PS_HOST: pwsh.exe`, both steps' shell reported as
`C:\Program Files\PowerShell\7\pwsh.EXE` (the Actions runner's own shell,
not the env var the tests select internally). Both lines are BARE `773
passed` - no `skipped` or `deselected` count on either side, which pytest
prints whenever either is nonzero - so a wholesale skip on one host cannot
have produced this output; both invocations actually ran and passed the
identical 773 items.

**Module-level revision binding.** `git diff --name-only
a3134dcd76d9253057bf24935f3d7a7eef8eb0e4..HEAD -- evals/ tools/ hooks/
.githooks/` returns EMPTY output. So every `path:line` citation in the
rest of this section against those four directories - not only the
workflow file checked above - is safe to read against today's working
tree: nothing under any of them has changed since the cited run's commit.

### Step 2: shipped scripts and which are covered

**Pattern used**, run exactly:
`git ls-files 'tools/*.ps1' '.githooks/*' 'evals/tools/*.ps1' 'hooks/*.ps1'`.
This returns **16** files (counted from the command's own output, not
assumed). `hooks/*.ps1` is in the glob deliberately - it is what catches
`hooks/superpowers-review-companion.ps1`, missing from an earlier draft's
hand-written glob, and the checkout's `hooks/hooks.json:10`/`:22` invoke it
as bare `pwsh`.

**Exclusions, named.** A repo-wide `git ls-files '*.ps1'` returns 21
files. Of the 16 entries the four-glob command above returns, only 15
carry a `.ps1` extension - the 16th, `.githooks/pre-push`, has none - so
the excluded `.ps1` set is 21 minus 15, **6 files**, not 5 (an earlier
draft of this section subtracted 5, treating `.githooks/pre-push` as if
it were one of the 21):
- `docs/superpowers/plans/rounds/2026-08-22-item48-pwsh7-feasibility/reexec/{child,child-named,parent,parent-named}.ps1`
  (4 files) - this investigation's OWN measurement harness, built by an
  earlier task in this same plan to produce Measurement 1. Scratch for the
  feasibility record, not shipped product surface a user, hook, or CI job
  invokes.
- `evals/multi-model-verify/fixtures/stub-appserver/stub-appserver.ps1` -
  a test double standing in for an external app server INSIDE the test
  suite, not a script the product ships to run in production. (Its sibling
  `stub-appserver.cmd` already has its own `must-change` row in
  `entry-points.tsv:70`/`:220` for hardcoding `powershell.exe`, so this
  exclusion is not hiding that finding, only scoping THIS table to scripts
  under the four brief-named directories.)
- `evals/multi-model-verify/fixtures/stub-codex/stub-codex.ps1` - the same
  kind of test double, standing in for the codex CLI inside the test
  suite rather than a script the product ships to run in production. It
  DOES appear in the repo-wide `*.ps1` listing (an earlier draft of this
  section said it did not, which was wrong - it is line 6 of that
  listing); it is excluded for the same reason as `stub-appserver.ps1`,
  not because it is absent.

**Coverage table.** For each script, the covering module with the
STRONGEST evidence found (a `runs` row inside a dual-host-job module, where
one exists); citations are `path:line`. "In dual-host job" means the
covering module is one of the eleven from Step 1.

| script | covering module | classification (cite) | in dual-host job |
|---|---|---|---|
| `tools/codex-context-probe.ps1` | `test_codex_context_probe.py` | runs (`:24` `PROBE`, invoked at `:375` via `ps_host()`) | yes |
| `tools/codex-tool-surface-probe.ps1` | `test_codex_tool_surface_probe.py` | runs (`:36` `PROBE`, invoked at `:137`) | yes |
| `tools/kimi-lane-lock.ps1` | `test_kimi_lane_lock.py`, `test_kimi_lane_home.py`, `test_kimi_lane_login.py`, `test_lock_protocol_live.py`, `test_lane_credential_live_support.py` | runs (`test_kimi_lane_lock.py:83,91,599`; `test_kimi_lane_home.py:347,356,369`; `test_kimi_lane_login.py:259`; `test_lock_protocol_live.py:103`; `test_lane_credential_live_support.py:129` calling `evals/tools/lane_credential_live_support.py:163-165 resolve_owner`) | yes (all five) |
| `tools/new-kimi-lane-home.ps1` | `test_kimi_lane_home.py` | runs (`:30` `BUILDER`, copied then invoked at `:702`,`:710`) | yes |
| `tools/new-kimi-lane-login.ps1` | `test_kimi_lane_login.py` | runs (`:31` `SCRIPT`, copied then invoked at `:356`,`:364`) | yes |
| `tools/new-review-mirror.ps1` | `test_review_mirror.py` | runs (`:20` `MIRROR`, invoked at `:118` via `ps_host()`) | yes |
| `tools/read-kimi-credential-state.ps1` | `test_kimi_credential_state.py` | runs (`:56` `VALIDATOR`, invoked at `:104` via `ps_host()`) | yes |
| `tools/read-kimi-round-evidence.ps1` | `test_kimi_round_evidence.py` | runs (`:55` `SCRIPT`, invoked at `:241`,`:257`) | yes |
| `tools/verify-attestation.ps1` | `test_attestation.py` | runs (`:26` `VERIFY`, invoked at `:91` via `run_ps`) | yes |
| `tools/write-attestation.ps1` | `test_attestation.py` | runs (`:25` `WRITE`, invoked at `:81`) | yes |
| `hooks/superpowers-review-companion.ps1` | `test_multi_model_verify.py` | runs (`:22` `HOOK_SCRIPT`, invoked at `:2269` - hardcoded `shutil.which("pwsh")`, always host 7, never selector-driven) | **no** - this module is not one of the eleven; it runs only inside Tier 2b (`skill-evals.yml:44`-`:47`, `ubuntu-latest`), gated by a skip if `pwsh` is absent there, which this task did not check |
| `tools/read-codex-round-evidence.ps1` | `test_codex_round_evidence.py` | runs (`:55` `SCRIPT`, invoked at `:245`,`:254`) | **no** - module not in the eleven |
| `tools/plant-home-skill-canary.ps1` | `test_home_skill_canary.py` | runs (`:48` `TOOL`, invoked at `:93` via `ps_host()`) | **no** - module not in the eleven |
| `tools/check-drift.ps1` | `test_backup_lane.py` (`reads` only - `:1181` `DRIFT`, text asserted at `:1187`,`:1205`,`:1216`,`:1237`, never executed; NOT a dual-host module - `grep -c "test_backup_lane" .github/workflows/skill-evals.yml` returns `0`); `evals/tools/drift_statemachine_tests.ps1` (`runs` - `:120`-`:121` `Copy-Item`/`$DriftScript`, but this IS the local-only harness itself) | reads (non-dual-host module) / runs (non-CI harness) | **no**, and stronger than merely gated off: `test_multi_model_verify.py:2957`-`:2959` gates the harness invocation behind `PARALLAX_STATEMACHINE` (unset in both CI jobs), and the invocation itself (`:2961`) hardcodes `"powershell.exe"`. `tools/check-drift.ps1:406`-`:408` states outright "the rest of the harness still drives 5.1 only (backlog item 41); that one scenario names its host rather than the harness changing hosts" - and that one PS7-naming scenario, `agy-allow-depth-over-boundary` (`drift_statemachine_tests.ps1:1283`), SKIPS ITSELF when `pwsh.exe` is absent (`:1275`). `check-drift.ps1` has no PowerShell 7 execution path at all, in CI or locally, except one opt-in scenario that can skip itself. |
| `evals/tools/drift_statemachine_tests.ps1` | `test_multi_model_verify.py` | runs (`:2903` builds the path, executed under the `PARALLAX_STATEMACHINE`-gated test at `:2957`-`:2959`) | **no** - gated off in both CI jobs; local-only per this repo's own README/CLAUDE.md, opt-in |
| `.githooks/pre-push` | `test_attestation.py` | mentions only (`:5`,`:29` - docstring/comment naming what the hook calls; no module anywhere invokes `.githooks/pre-push` itself as a process) | **no** - no `runs` row exists for this script in the whole repo, on any host |

**Count: 10 of 16 shipped scripts have a `runs` row inside a module that
is one of the eleven the dual-host CI job runs; 6 do not** (one of the 6,
`check-drift.ps1`, has a `runs` row, but only inside a harness the CI jobs
never turn on). Per the width-of-evidence rule this record uses throughout
(Measurement 1, Measurement 2): a `runs` row says the module invokes the
script, not that the invocation passed. What the green run cited above
(`32391262449`/`96497936725`, headSha bound above) adds is the passing
half, for the ten scripts whose covering module is in that job's list -
`773 passed` under `pwsh.exe` covers all eleven modules' test functions
together, not scored per script.

### Step 3: the five named traps, coverage under 7

Backlog item 48's own list, `docs/superpowers/plans/2026-07-27-0150-backlog.md:3456`-`:3470`,
copied here as the fixed set to check, each against whether a test
exercises the SAME behaviour under 7:

1. **`ConvertTo-Json` truncates silently at the default depth; 7 warns
   (0.24.0).** Mitigated in shipped code by hardcoding `-Depth 100` /
   `-Depth 3` (`tools/check-drift.ps1:205,765,1242`), with the rationale at
   `:376`-`:407` ("measured on both hosts rather than argued... an
   over-boundary scenario naming pwsh.exe"). But `:406`-`:408` of that same
   comment says plainly "the rest of the harness still drives 5.1 only
   (backlog item 41)": the only harness that drives this scenario live is
   `evals/tools/drift_statemachine_tests.ps1`, gated behind
   `PARALLAX_STATEMACHINE` (`test_multi_model_verify.py:2957`-`:2959`,
   whose invocation is itself hardcoded to `"powershell.exe"` at `:2961`),
   unset in both CI jobs - and even inside that opt-in harness, the one
   scenario that names `pwsh.exe`, `agy-allow-depth-over-boundary`
   (`drift_statemachine_tests.ps1:1283`), SKIPS ITSELF when `pwsh.exe` is
   absent (`:1275`). **No coverage under 7** in any run this task can point
   to; the comment's "measured on both hosts" describes a past manual/local
   measurement, not a CI-repeatable one.
2. **A no-BOM file reads with the ANSI code page and `$OutputEncoding`
   defaults to us-ascii, flattening an em dash (0.23.0).** Tested by
   `TestBriefEncodingOverStdin` in `test_multi_model_verify.py` (four
   `@pytest.mark.skipif(os.name != "nt", ...)` cases at `:3029`,`:3042`,
   `:3060`,`:3093`), whose `_run` helper (`:2986`-`:3000`) hardcodes
   `"powershell.exe"` at `:2999` as the literal interpreter - never
   selector-driven, never `pwsh`. **No coverage under 7**: every assertion
   about this behaviour is made against 5.1 only. Whether PowerShell 7 (which
   defaults `$OutputEncoding` to UTF-8, per this repo's own CLAUDE.md prose)
   needs or already avoids the same mitigation is asserted in comments and
   documentation, not exercised by a test against `pwsh` here.
3. **Native argument splatting strips embedded double quotes without
   changing the argument count (0.21.0, item 20).** Covered: `##
   Measurement 1: re-exec fidelity` in THIS record, produced by Task 2, ran
   this exact class of corruption under both hosts as PARENT. The
   `pwsh7/splat/positional` and `pwsh7/splat/named` rows both show
   `stage B exact: true` - PowerShell 7 as the splatting parent forwarded
   every hostile shape (embedded quotes, trailing backslash, em dash,
   semicolon/ampersand) intact. This is a direct measurement in this same
   investigation, not a shipped pytest module.
4. **`ConvertFrom-Json` throws at about 100 nested levels; 7 accepts far
   more (0.24.0).** Same gating as trap 1: the only live scenario is inside
   `evals/tools/drift_statemachine_tests.ps1`, behind
   `PARALLAX_STATEMACHINE`, never set in CI. `tools/check-drift.ps1:387`-
   `:407`'s comment states an "over-boundary scenario naming pwsh.exe"
   exists in that harness - the `agy-allow-depth-over-boundary` scenario at
   `drift_statemachine_tests.ps1:1283` - but that scenario SKIPS ITSELF
   when `pwsh.exe` is absent (`:1275`), and the harness does not run in
   either CI job regardless. **No coverage under 7** evidenced by a run
   this task can cite.
5. **The tool-surface probe built the process's stdin from
   `Console.InputEncoding` and put a byte-order mark on the first JSON-RPC
   frame, rejected by the app server - broken on 5.1 only.** Covered:
   `test_codex_tool_surface_probe.py:514`
   `test_the_first_frame_reaches_the_server_with_no_byte_order_mark`, whose
   class docstring (`:510`) states "it drives EVERY host present" - line
   `:515` builds the host list from `shutil.which("powershell")` AND
   `shutil.which("pwsh")` and asserts a clean run for each host found. This
   module IS one of the eleven dual-host-job modules, so the green run
   cited above covers this behaviour under `pwsh.exe` directly.

**Beyond item 48's five: other host-sensitive behaviours found while
reading these scripts.** Item 48's own list is not presented as
exhaustive - `docs/superpowers/plans/2026-07-27-0150-backlog.md:3485`-
`:3490` treats its own entry-point count as "a claim, not a fact" and
records rounds that kept finding more. Reading the 16 shipped scripts for
Steps 1-2 surfaced three more host-sensitive behaviours; recording them
here rather than silently narrowing the search to the five names already
given:

a. **Native stderr promoted to a terminating error.**
   `tools/new-kimi-lane-home.ps1:671`-`:679`: "Windows PowerShell 5.1 turns
   ANY native-command stderr line into a terminating `NativeCommandError`
   under `$ErrorActionPreference = "Stop"`, even when that stderr is being
   captured rather than displayed - so the preference is relaxed for just
   this call and restored immediately after" - a shipped save/restore
   workaround (`:678`-`:679`,`:695`,`:699`). CLAUDE.md carries the same
   rule for the codex-dispatch scripts, so this is a recurring class, not
   a one-off. Its covering module, `test_kimi_lane_home.py`, IS one of the
   eleven and this code path runs on every home build the tests do under
   `pwsh` in the cited green run - but no assertion in that module measures
   whether PowerShell 7 exhibits the same stderr-promotion behaviour.
   Verdict: **exercised, divergence not measured**.
b. **Reparse-point traversal during a recursive directory walk.**
   `tools/plant-home-skill-canary.ps1:70`-`:73`: "Walk MANUALLY and never
   step through a reparse point. `Get-ChildItem -Recurse` follows junctions
   on some hosts, which would take this scan into whatever the junction
   aims at." Its only covering module, `test_home_skill_canary.py:93`, is
   outside the eleven (see this script's own row in Step 2's table).
   Verdict: **no coverage under 7** - neither the divergence itself nor the
   manual-walk mitigation is exercised by anything the dual-host job runs.
c. **`ConvertFrom-Json` returns `String` on 5.1 and `DateTime` on 7 for the
   same ISO-8601 timestamp.** `test_lock_protocol_live.py:379`-`:390`
   `test_measurement_20_ticks_and_date_string_types_diverge_across_hosts`
   measures this directly - the exact coercion behind the 0.16.0 lane lock
   that "did not lock" (`skill-evals.yml:50`-`:53`,
   `2026-07-27-0150-backlog.md:3473`-`:3477`). Its `required_hosts()`
   helper (`:77`-`:91`) is the only host-selection function found anywhere
   in this repo's test suite that FAILS rather than skips when a host is
   missing (`:83`-`:89`: "an unavailable host fails it rather than reading
   as a skip"), which makes a pass of this test the strongest single piece
   of host-presence evidence this record has found. Its module IS one of
   the eleven, so the cited green run covers it. Verdict: **covered under
   7** - and the coverage is BILATERAL: `required_hosts()` demands both
   `powershell.exe` and `pwsh.exe` by literal name, so this exact test
   cannot survive a 5.1 drop unmodified. That is not a coverage caveat, it
   is an asset a 5.1 drop destroys - flagged forward to `## Measurement 5:
   what is saved`, not resolved here.

These three are counted separately below, not folded into item 48's own
"2 of 5" tally, so the scope decision stays visible rather than being
silently absorbed either way.

**2 of item 48's 5 named traps (native-splat corruption, tool-surface-probe
stdin BOM) have real coverage of the same behaviour under PowerShell 7. 3
of 5 (JSON-depth truncation, em-dash/`$OutputEncoding` flattening, the
`ConvertFrom-Json` nesting-limit throw) have no coverage under 7 evidenced
by this task** - two because the only harness that exercises them is
gated off in both CI jobs (and, for the one scenario inside it that DOES
name `pwsh.exe`, self-skipping whenever `pwsh.exe` is absent), one because
the shipped test that guards the fix is written to run 5.1 only, by
design, and nothing here tests the pwsh side of that same claim. Counting
the three additional behaviours above alongside the five named traps: 3 of
8 host-sensitive behaviours this task identified are covered under 7
(traps 3 and 5, plus the Measurement-20 divergence); 5 of 8 are not (traps
1, 2 and 4, plus the reparse-point walk, plus the stderr-promotion
behaviour - the last one "exercised but not measured" rather than
untouched entirely).

### Summary

Of the 16 shipped PowerShell-facing scripts (derived mechanically from
`git ls-files 'tools/*.ps1' '.githooks/*' 'evals/tools/*.ps1' 'hooks/*.ps1'`,
6 further tracked `.ps1` files excluded and named above), 10 have a `runs`
row inside a module the dual-host CI job actually runs, and that job's most
recent green run at this branch's cut commit
(`32391262449`/`96497936725`, headSha `a3134dcd76d9253057bf24935f3d7a7eef8eb0e4`,
re-verified directly against the job log: `773 passed` under both
`powershell.exe` and `pwsh.exe`) is real evidence those ten scripts'
exercised behaviour passed under PowerShell 7, not merely a declaration.
The other 6 scripts have no `runs` row inside a dual-host-job module: three
(`hooks/superpowers-review-companion.ps1`, `read-codex-round-evidence.ps1`,
`plant-home-skill-canary.ps1`) run only in modules outside that job (one
gated by a `pwsh`-presence skip on `ubuntu-latest`, two invoked through
`ps_host()`/a raw host string this task did not resolve against either CI
job); two more
(`check-drift.ps1`, `drift_statemachine_tests.ps1`) are exercised only by a
harness both CI jobs leave switched off; and `.githooks/pre-push` has no
`runs` row anywhere in this repo, on either host. Of backlog item 48's five
named 5.1-specific traps, only 2 have coverage of the same behaviour class
actually exercised under 7 by a real, evidenced run; the other 3 are
"declared, not proven" under 7 - written up, reasoned about in comments,
in one case measured under this record's own Measurement 1, but not
covered by anything the dual-host CI job runs today. Three more
host-sensitive behaviours turned up beyond item 48's named five (native
stderr promotion, reparse-point traversal, and the Measurement-20
`ConvertFrom-Json` type divergence); one of those three is itself the
strongest single piece of coverage evidence in this whole record, and is
also the one asset a 5.1 drop would destroy outright - see Step 3 above
and the forward pointer to Measurement 5. No percentage is given for any
of these counts: the tables above are the width of what this task
measured, and a single number would claim more precision than 10-of-16
scripts, 2-of-5 named traps, or 3-of-8 total behaviours supports.

**Residual limits, named.**
- This section maps INVOCATION, per the interfaces the brief sets: a
  `runs` row is not a claim that the invoking module's assertions are
  correct, only that the script was actually started as a process by test
  code. Whether each assertion inside those ten modules is the RIGHT check
  is outside this task's scope, as it was outside Measurement 2's. Nor
  does this section claim the passing run's assertions match every
  classification in `entry-points.tsv` - that inventory classifies LINES,
  not test coverage, and this section does not re-derive it.
- The 6 uncovered scripts are not all equally unproven: `run_hook` in
  `test_multi_model_verify.py:2269` DOES invoke
  `superpowers-review-companion.ps1` under a real `pwsh`, just outside the
  dual-host job and gated by a presence skip this task did not resolve
  either way on `ubuntu-latest`. That is a narrower gap than
  `.githooks/pre-push`, which no test anywhere invokes.
- The three behaviours found beyond item 48's named five (Step 3, above)
  are not claimed to be the complete set of what a wider search would
  find; they are what this task's reading of the 16 shipped scripts
  surfaced, disclosed rather than dropped for not matching the five given
  names.
- This section did not independently re-verify whether `pwsh` is present
  on the `ubuntu-latest` runner that executes Tier 2b
  (`skill-evals.yml:44`-`:47`) or the module that hook test runs inside
  when it does. Measurement 2 already recorded that PowerShell 7's presence
  on the Linux runner is unproven by this repo's own evidence; this section
  does not contradict that, and does not attempt to resolve it.
- This section's `hooks/hooks.json:10`/`:22` citation (Step 2, `runs`
  classification for `hooks/superpowers-review-companion.ps1`) is scoped to
  the CHECKOUT, matching Measurement 2's own scoping. The versioned plugin
  cache copy actually installed was not inspected by this task either;
  Measurement 2 already names that gap in its own "half-requirement"
  paragraph, and this section does not re-measure or contradict it.

## Measurement 4: refusal when pwsh is missing

Attempted by `<REC>/missing-pwsh/probe.py`, which strips every `PATH` entry
containing `pwsh.exe` from a CHILD environment dict only (the real PATH,
this process's own `os.environ`, and the real `pwsh.exe` binary are never
touched - see `hooks/hooks.json:10` for the invocation shape reproduced,
already recorded in Measurement 2 as `no-change`) and then runs the hook's
own shipped shape - `pwsh -NoProfile -NonInteractive -File
hooks/superpowers-review-companion.ps1` - through that stripped
environment, with `stdin=subprocess.DEVNULL` and a 60-second timeout.

Outcome, named explicitly: the second of the three the task pre-named -
the call succeeded anyway. **Absence of PowerShell 7 was NOT reproduced by
this probe, and item 48's NO-criterion this measurement exists to answer
remains untested by it - see the closing note at the end of this
section.** Verbatim captured output
(`<REC>/missing-pwsh/results.json`, also printed to stdout by the run):

```
{
 "pwsh_on_real_path": "C:\\Program Files\\PowerShell\\7\\pwsh.EXE",
 "pwsh_after_stripping": null,
 "invocation": [
  "pwsh",
  "-NoProfile",
  "-NonInteractive",
  "-File",
  "C:\\Users\\Brandon\\Documents\\parallax\\hooks\\superpowers-review-companion.ps1"
 ],
 "returncode": 0,
 "stdout": "",
 "stderr": ""
}
```

`pwsh_after_stripping` came back `null` - `shutil.which("pwsh",
path=env["PATH"])`, resolving directly against the stripped PATH string
inside THIS process, found nothing, so the strip itself was not the
failure. But the actual `subprocess.run(["pwsh", ...], env=env)` call still
started `pwsh` and it exited `0`. This was checked further, not just
accepted: a `cmd /c "echo %PATH% & where pwsh"` launched through the same
stripped `env` dict shows the CHILD's own `%PATH%` correctly excludes both
`C:\Program Files\PowerShell\7` and
`C:\Users\Brandon\AppData\Local\Microsoft\WindowsApps`, and that child's
own `where pwsh`, searching ITS OWN received environment, genuinely fails
(`INFO: Could not find files for the given pattern(s)`, returncode 1).

The command run (a Python one-liner reusing `probe.py`'s own
`stripped_path()`) and its full verbatim captured output, not merely a
characterisation of it:

```
env = dict(os.environ); env["PATH"] = stripped_path()
proc = subprocess.run(["cmd", "/c", "echo %PATH% & where pwsh"],
                      capture_output=True, text=True, env=env)
```

```
RETURNCODE: 1
---STDOUT---
C:\Users\Brandon\bin;C:\Program Files\Git\mingw64\bin;C:\Program Files\Git\usr\local\bin;C:\Program Files\Git\usr\bin;C:\Program Files\Git\usr\bin;C:\Program Files\Git\mingw64\bin;C:\Program Files\Git\usr\bin;C:\Users\Brandon\bin;C:\Users\Brandon\AppData\Roaming\Code\User\globalStorage\github.copilot-chat\debugCommand;C:\Users\Brandon\AppData\Roaming\Code\User\globalStorage\github.copilot-chat\copilotCli;C:\WINDOWS\system32;C:\WINDOWS;C:\WINDOWS\System32\Wbem;C:\WINDOWS\System32\WindowsPowerShell\v1.0;C:\WINDOWS\System32\OpenSSH;C:\Program Files\NVIDIA Corporation\NVIDIA App\NvDLISR;C:\Program Files (x86)\NVIDIA Corporation\PhysX\Common;C:\Program Files\Git\cmd;C:\Program Files\nodejs;C:\Users\Brandon\.kimi-code\bin;C:\Users\Brandon\AppData\Local\agy\bin;C:\Users\Brandon\Documents\WoW-Dev\lua51\bin;C:\Users\Brandon\AppData\Local\Microsoft\dotnet;C:\Users\Brandon\AppData\Roaming\luarocks\bin;C:\Users\Brandon\scoop\apps\mingw\current\bin;C:\Users\Brandon\scoop\persist\luarocks\rocks\bin;C:\Users\Brandon\scoop\shims;C:\Users\Brandon\AppData\Local\Programs\Python\Python312\Scripts;C:\Users\Brandon\AppData\Local\Programs\Python\Python312;C:\Users\Brandon\AppData\Local\Programs\Python\Launcher;C:\Users\Brandon\AppData\Local\Programs\Microsoft VS Code\bin;C:\Users\Brandon\AppData\Roaming\npm;C:\Users\Brandon\AppData\Local\Programs\luacheck;C:\Users\Brandon\.local\bin;C:\Users\Brandon\AppData\Local\Microsoft\WinGet\Packages\ajeetdsouza.zoxide_Microsoft.Winget.Source_8wekyb3d8bbwe;C:\Users\Brandon\.bun\bin;C:\Users\Brandon\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.1.1-full_build\bin;C:\Users\Brandon\AppData\Local\npm-global;C:\Users\Brandon\AppData\Local\Microsoft\WinGet\Packages\GitHub.cli_Microsoft.Winget.Source_8wekyb3d8bbwe\bin;C:\Users\Brandon\.dotnet\tools;C:\Users\Brandon\AppData\Local\Programs\Orca\resources\bin;C:\Program Files\Git\usr\bin\vendor_perl;C:\Program Files\Git\usr\bin\core_perl;C:\Users\Brandon\.claude\plugins\cache\claude-plugins-official\claude-md-management\1.0.0\bin;C:\Users\Brandon\.claude\plugins\cache\claude-plugins-official\security-guidance\2.0.7\bin;C:\Users\Brandon\.claude\plugins\cache\claude-plugins-official\superpowers\6.3.0\bin;C:\Users\Brandon\.claude\plugins\cache\claude-plugins-official\claude-code-setup\1.0.0\bin;C:\Users\Brandon\.claude\plugins\cache\openai-codex\codex\1.0.6\bin;C:\Users\Brandon\Documents\parallax\bin;C:\Users\Brandon\.claude\plugins\cache\claude-plugins-official\frontend-design\unknown\bin;C:\Users\Brandon\.claude\plugins\cache\i-have-adhd\i-have-adhd\0.2.0\bin;C:\Users\Brandon\.claude\plugins\cache\claude-plugins-official\code-simplifier\1.0.0\bin
---STDERR---
INFO: Could not find files for the given pattern(s).
```

Neither `PowerShell\7` nor `WindowsApps` appears anywhere in that printed
`%PATH%` line - confirmed by reading it, not merely asserted - which is
what makes the `where pwsh` failure on the next line direct rather than
coincidental. So the stripped environment IS what the new process receives
once it exists. What differs is resolving the bare executable NAME
`"pwsh"` to start that process in the first place: Windows resolves a bare
command name using the PARENT process's own environment for that search,
not the `env` dict handed to the child being created - exactly the outcome
the brief pre-named ("the process-creation call resolves it using the
PARENT process's environment, not the child environment being passed in").
This account is specific to the PATH search step of that resolution -
`CreateProcess` also checks the calling process's own directory, the
current directory, `System32`, and the Windows directory before it
consults PATH, and none of those were independently tried. They are ruled
out here only because both known copies of `pwsh.exe` on this machine
live exclusively in PATH-listed directories (`C:\Program
Files\PowerShell\7\` and the WindowsApps alias directory), neither of
which is the probe's own working/calling directory or a system directory
- that placement is the load-bearing elimination, not a direct test of
each of those other locations.

1. **Which outcome:** the call succeeded anyway (outcome 2 of 3). Not a
   failure and not a timeout.
2. **No failure text exists to report.** `returncode` is `0` and both
   `stdout` and `stderr` are empty. Absence of PowerShell 7 was **not
   reproduced** by this probe on this machine, so there is nothing to
   quote as "what a user would see," and no failure text is substituted
   here from a guess about what one would probably look like. Per the
   pre-named handling for this outcome: this is not read as evidence that
   the failure mode is benign, and the strip is not judged to have "failed"
   either - `pwsh_after_stripping: null` and the `cmd`/`where` check above
   both show the stripped environment was genuinely PATH-less for `pwsh`
   from the child's own point of view. What defeated the probe is a
   property of how the parent process asks Windows to CREATE the child
   when given a bare name, not a leak in the environment dict itself.
3. **Named residual limits:**
   - Only the bare-`pwsh` resolution path (as this repo's hook already
     invokes it, `hooks/hooks.json:10`/`:22`) was measured. Entry points
     that today name `powershell.exe` explicitly (the `must-change` rows
     in this record's inventory) were not probed here, since nothing about
     them changes until a migration edits them.
   - The harness's own presentation of a hook failure - what Claude Code's
     hook runner shows a user when a `PostToolUse`/`PostToolUseFailure`
     command hook errors - was not measured by this probe. This probe only
     captures what the OS-level child process produced. Nor was the
     runner's METHOD of resolving the bare name `pwsh` measured, and that
     is a separate thing from its presentation: this probe's own outcome
     was decided by Python's `subprocess.run` resolving a bare executable
     name against the PARENT's environment rather than the child's. If
     Claude Code's hook runner instead starts the command through a shell
     (rather than the same direct bare-name process-creation path Python
     used here), a shell-mediated resolution would consult the CHILD's own
     PATH - and the `cmd`/`where` cross-check above is direct evidence that
     resolution behaves differently in that case (it correctly failed
     against the same stripped environment). Which mechanism the real
     runner uses is not asserted here in either direction; this bullet
     names it as unmeasured rather than leaving the gap implicit.
   - **What this probe actually measured, and what it did not.** It proved
     that stripping `PATH` of every directory holding `pwsh.exe` does not,
     by itself, reproduce "PowerShell 7 is absent" on this machine when the
     caller names the executable barely (as the shipped hook does) via
     Python's `subprocess.run`. It did not measure the refusal message a
     user sees when `pwsh` is genuinely absent, because genuine absence was
     not achieved. What would prove it: a machine, container, or CI runner
     with PowerShell 7 genuinely not installed anywhere on it (no
     `Program Files\PowerShell\7`, no WindowsApps alias, no `App Paths`
     registry entry) - not a PATH-stripped child of a machine that has it.
   - This machine has two resolvable copies of `pwsh.exe`
     (`C:\Program Files\PowerShell\7\pwsh.exe` and
     `C:\Users\Brandon\AppData\Local\Microsoft\WindowsApps\pwsh.exe`, per
     Measurement 2's own `where.exe pwsh` output); both directories were
     confirmed stripped from the child's `PATH` string, and the outcome
     above still occurred, so a wider PATH search was not the gap here.

**Item 48's NO-criterion, left open.** This measurement therefore leaves
item 48's NO-criterion "a user-facing failure mode worse than the bugs
being removed" (see `## What would make the verdict NO` above) UNANSWERED,
and item 48's own requirement that the failure "must stop with a message
naming what to install" is UNTESTED by this task - no failure text was
produced to check that requirement against. `## Verdict` may not treat
this criterion as satisfied on the strength of this section; what would
answer it is named above (a machine, container, or CI runner with
PowerShell 7 genuinely not installed anywhere on it).

## Measurement 5: what is saved

Answers the brief's own question - what the change actually saves - against
the cost the earlier measurements have already surfaced. A section that
lists only savings is not a ledger; both sides are recorded here.

### Step 1: CI wall-clock, STEP timings not job timings

`gh run list --workflow skill-evals.yml --limit 10 --json
databaseId,conclusion,headSha,createdAt --jq '.[] | select(.conclusion==
"success")'` returned seven successful runs; the first five, newest first:
`32391262449` (2026-08-20), `32085653133` (2026-08-18), `32082761519`
(2026-08-18), `32078875878` (2026-08-17), `31956013509` (2026-08-16). These
differ from Measurement 2's cited run only by including four MORE runs
after it in the same list - `32391262449` is the same run Measurement 2
cites (`headSha a3134dcd...`), so the two sections do not disagree, they
just cover different windows of the same run history.

For each id, `gh run view <ID> --json jobs --jq '.jobs[] | select(.name==
"powershell-hosts") | {job: .name, jobStart: .startedAt, jobEnd:
.completedAt, steps: [.steps[] | select(.name | test("PowerShell-facing
tests under")) | {name, startedAt, completedAt}]}'` returned real
`startedAt`/`completedAt` timestamps for both named steps AND the job
itself, for all five runs - no run needed to be marked unmeasured. Per the
brief's own warning, the job total is shown ONLY as context (it also pays
for checkout, Python setup and pytest install, none of which a migration
removes); the two step columns are the load-bearing numbers.

| run id | date | `powershell-hosts` job | `...5.1` step | `...7` step |
|---|---|---|---|---|
| 32391262449 | 2026-08-20 | 45m45s | 22m44s | 22m37s |
| 32085653133 | 2026-08-18 | 46m05s | 22m56s | 22m39s |
| 32082761519 | 2026-08-18 | 43m29s | 20m58s | 21m40s |
| 32078875878 | 2026-08-17 | 46m41s | 23m25s | 22m56s |
| 31956013509 | 2026-08-16 | 45m07s | 22m46s | 22m01s |

**GROSS saving, as a range across these five runs, not one number:** the
5.1 step alone ran between **20m58s and 23m25s** (1258s-1405s) across the
five. That range - not a single averaged figure - is what dropping the 5.1
step removes from the `powershell-hosts` job on each of these five
occasions. It is a GROSS figure: it is what disappears from the job if the
5.1 step is deleted outright, not what disappears from a migration that
keeps some 5.1-starting cases.

**The NET saving is not determined by this task.** Item 48's own answer to
"what does the test matrix become" (`docs/superpowers/plans/2026-07-27-0150-backlog.md:3561`-
`:3563`) is "probably not 'one host' but 'one host plus a small number of
cases proving the refusal and the re-exec work when started from 5.1'."
Which cases those are, and how long they cost to keep running, is Task 9's
decision, not this one's. So: **the net saving is bounded above by the
gross range above (20m58s-23m25s per run of this job) and is not stated as
a number here.** Any sentence claiming a net figure at this point would
state as known something Task 9 has not yet decided.

### Step 2: the already-recorded local pair (cited, not re-measured)

Backlog item 48 itself records local timing evidence, gathered during the
0.27.0 gate, same tree and head, back to back:
`docs/superpowers/plans/2026-07-27-0150-backlog.md:3380`-`:3386` - `2558
passed, 14 skipped` in **32m23s** under Windows PowerShell 5.1 against
**18m33s** under `pwsh.exe`, and a second pair the same night, **20m22s**
against **18m50s**. Counts identical on both hosts both times. Item 48's
own caveat, carried forward rather than dropped: "the runs were not
isolated from other load, and the 5.1 spread (32m to 20m) is wider than the
gap itself" - so this pair is indicative, not a benchmark, and is cited
here rather than re-measured.

### Step 3: item 44's 57 minutes, GROSS upper bound only

Item 44 (`docs/superpowers/plans/2026-07-27-0150-backlog.md:3098`-`:3126`)
measured the gate's three serial passes - full pytest, then the
PowerShell-facing modules under 5.1, then the same modules under 7 - at
**1187s / 1153s / 1092s**, about **57 minutes** total, on the tree
committed as `99d1961`. The GROSS upper bound this change could remove from
that 57 minutes is the 5.1 pass's own duration: **1153s, about 19m13s**.
That is not a net figure: Task 9 has not yet decided which 5.1-starting
cases a migration keeps, and item 44's own "about 20 minutes instead" figure
(`:3105`-`:3108`) is about PARALLELIZING the three passes, a different
change from dropping one of them, so it is not substituted here either.

### Step 4: defects avoided (cited, not re-derived)

`docs/superpowers/plans/rounds/2026-08-22-item51-inline-brief-probe/probe-record.md`
measured two independent corruption defects in the Kimi lane's inline
brief transport, BOTH 5.1-only: Defect 1, the READ (`Get-Content -Raw`
decoding a no-BOM UTF-8 file with the ANSI code page, mangling non-ASCII
text) at `probe-record.md:75`-`:89`; Defect 2, the ARGUMENT (5.1 not
escaping embedded double quotes in a native argument, silently dropping
them when the count is balanced and SHATTERING the brief across multiple
argv elements when the count is odd) at `probe-record.md:91`-`:110`. Its
own summary table (`probe-record.md:67`-`:73`) shows every PowerShell-7
row exact and every corrupted row under 5.1. Dropping 5.1 removes both
defect classes outright, since PowerShell 7 was never the host on which
either fired. This is a real saving and it is already measured elsewhere;
it is cited here, not re-derived.

### Step 5: the edit cost (cited, not recounted)

The other side of "maintenance" - what this change costs to MAKE, as
opposed to what running two hosts costs going forward - is the entry point
inventory's own count, already recorded above (`## Entry point inventory`,
line 369 of this record): **83 `must-change` rows, plus 3 further rows left
`unknown`** because their answer depends on the environment the code runs
in rather than on the line itself. That number lives in one place in this
record (the `## Entry point inventory` section); it is not restated from
memory here, only pointed at.

### Step 6: the cost side - the bilateral test, verified against source

Measurement 3 flagged `evals/multi-model-verify/test_lock_protocol_live.py:379`-
`:390` forward to this section rather than resolving it itself. Verified
directly against the source, not taken from the forward pointer's
characterization:

- `test_measurement_20_ticks_and_date_string_types_diverge_across_hosts`
  (`:379`-`:390`) calls `required_hosts()` (`:380`), then runs the SAME
  script under `hosts["powershell.exe"]` and `hosts["pwsh.exe"]`
  (`:381`-`:382`) and asserts the two hosts report DIFFERENT
  `ConvertFrom-Json` types for the same value - `String` on 5.1,
  `DateTime` on 7 (`:389`-`:390`). Its entire premise is the divergence
  BETWEEN the two hosts; there is no way to rewrite it to run under one
  host and still test what it exists to test, because "these two things
  differ" requires both things.
- `required_hosts()` itself (`:77`-`:91`) loops over the literal tuple
  `("powershell.exe", "pwsh.exe")` (`:83`) and calls `pytest.fail` (`:86`-
  `:89`) - not `pytest.skip` - if either binary is not found on PATH. Read
  against the rest of this file's module docstring (`:14`-`:23`): every
  OTHER host-selection function in this repo's test suite (the sibling
  pattern named at `test_codex_context_probe.py:35`-`:67`, and this same
  file's own `ps_host()` at `:63`-`:74`, which reads `PARALLAX_PS_HOST` or
  falls back to whichever single host is on PATH) tolerates a missing host
  by skipping. `required_hosts()` is the only one in this repo that FAILS
  instead - a red mark on the gate, not a quiet skip - when either host is
  absent. That makes it, as the module docstring itself claims
  (`:16`-`:23`), the single strongest piece of host-presence evidence this
  whole investigation has, and it exists only because BOTH hosts are
  required by name.

**Verified: dropping 5.1 destroys this test.** It is not editable into a
one-host form; deleting the 5.1 half of `required_hosts()`'s tuple removes
the premise the test asserts. That is not a saving - it is an asset the
change consumes, and it belongs on the cost side.

**Is it the only one?** Searched three ways, not just re-read the forward
pointer:

1. `grep -rn "required_hosts\|diverge" evals/multi-model-verify/*.py
   evals/tools/*.py` - the only other hit inside this file is
   `test_measurement_20_a_failed_host_invocation_never_reads_as_divergence`
   (`test_lock_protocol_live.py:393`-`:400`), which ALSO calls
   `required_hosts()` and so is ALSO destroyed by a 5.1 drop as written -
   but its own assertion does not compare the two hosts' behaviour against
   each other: it forces `hosts["powershell.exe"]` to exit nonzero and
   checks that the measurement helper fails closed rather than reading an
   empty result as "the type differs" (`:398`-`:400`). Unlike the
   divergence test above, this one COULD be rewritten to exercise
   `pwsh.exe` instead without losing what it tests - its value comes from
   testing the fail-closed helper, not from comparing two hosts. So it
   shares the same fatal gate today but is not, itself, a bilateral asset.
2. A script (see the tool call recorded in this task's report) searched
   every `evals/multi-model-verify/*.py` and `evals/tools/*.py` function
   body for BOTH literal host names co-occurring in the same function.
   Besides the two above, it found: `check_host_parity` in
   `evals/tools/check_workflow_paths.py` (`REQUIRED_HOST_NAMES` at `:85`)
   and its unit tests `test_check_workflow_paths_flags_host_parity_gap` /
   `test_check_workflow_paths_refuses_a_duplicate_host_step`
   (`test_backup_lane.py`, already itemized in this record's own
   `must-change` list), plus `test_no_module_claims_ci_skips_the_windows_suites`
   (`test_backup_lane.py:1707`-`:1747`). All three require BOTH host NAMES
   to appear as declared steps in the CI workflow TEXT - a parity/coverage
   check on the YAML, not a live measurement of either host's runtime
   behaviour. Per this record's own `must-change` list, dropping 5.1 means
   these get REWRITTEN to require `pwsh.exe` alone, the same way the
   workflow step itself gets edited rather than the checker losing its
   reason to exist - a cost already counted once in the edit-cost figure
   above, not a second, separate asset destroyed.
3. No other `subprocess.run` call anywhere in the two directories was
   found comparing a result from `powershell.exe` against a result from
   `pwsh.exe` within the same assertion.

**Conclusion: `test_measurement_20_ticks_and_date_string_types_diverge_across_hosts`
(`test_lock_protocol_live.py:379`-`:390`) is the only test found whose
entire value comes from comparing the two hosts' live BEHAVIOUR against
each other, in a way no edit can preserve on one host.** Everything else
found either (a) shares the same fail-hard `required_hosts()` gate without
itself being a cross-host comparison (item 1 above - destroyed as written,
but rewritable to test the same thing on one host), or (b) requires both
host NAMES in declared CI text, which the must-change list already prices
as an edit, not a destroyed asset (item 2 above).

### Ledger

**Saved:**
- CI wall-clock: gross 20m58s-23m25s per run of the `powershell-hosts` job
  (Step 1), net not yet determined (bounded above by that range).
- The already-recorded local pair, 32m23s/18m33s and 20m22s/18m50s, cited
  with its own wider-spread caveat (Step 2).
- Item 44's structural 57-minute gate cost: a GROSS upper bound of about
  19m13s removable, not a net figure (Step 3).
- Two independent 5.1-only corruption defects in the Kimi lane's inline
  brief transport, removed outright (Step 4).

**Costs:**
- 83 `must-change` edit rows (plus 3 `unknown`), already counted once in
  `## Entry point inventory` (Step 5).
- One test whose entire value is destroyed outright, not merely edited:
  `test_measurement_20_ticks_and_date_string_types_diverge_across_hosts`
  (`test_lock_protocol_live.py:379`-`:390`), gated by the one fail-hard
  host requirement in this repo's whole test suite (`:77`-`:91`) - verified
  against source, searched for siblings, found none that share its shape
  (Step 6).
- The retained-case set from item 48's own "one host plus a small number of
  cases" answer is not yet chosen (Task 9), so its ongoing cost is not
  priced here either.

## Residual limits

NOT YET WRITTEN.
