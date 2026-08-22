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

NOT YET WRITTEN.

## Measurement 2: is PowerShell 7 present

NOT YET WRITTEN.

## Measurement 3: behaviour under 7

NOT YET WRITTEN.

## Measurement 4: refusal when pwsh is missing

NOT YET WRITTEN.

## Measurement 5: what is saved

NOT YET WRITTEN.

## Residual limits

NOT YET WRITTEN.
