The validator decision is FIX, not ESCALATE: all four reported statuses must exit 0. Nonzero must mean no valid classification was produced.

A separate implementation defect remains in Task 1: duplicate steps for the same host are collapsed before parity checking.

## Frozen validator interface

Add this single contract to `Fixed names and values`, because Tasks 2, 5, 6, and 8 receive separate task packets:

> Invoke the validator as `tools/read-kimi-credential-state.ps1 -Path <credential-file>`. `-Path` is a mandatory string, interpreted literally, and callers pass the resolved absolute credential-file path. For `ok`, `absent`, `unreadable`, and `malformed`, classification SUCCEEDED: exit 0, emit exactly one schema-valid result line on stdout, and emit nothing on stderr. Exit 0 means “classification completed,” never “credential clean.” A bound invocation that cannot produce a classification exits 1, emits no stdout, and emits exactly `credential validator failed` on stderr. PowerShell binding or process-launch failure is also validator failure even when script code never returns an exit code.

The four status mappings should be:

| Status | Exit |
|---|---:|
| `ok` | 0 |
| `absent` | 0 |
| `unreadable` | 0 |
| `malformed` | 0 |
| no valid classification | 1 |

This preserves the distinction already required by the doctor: `absent` is a successfully measured `N/A`, while validator invocation failure is `BROKEN`. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:655](C:\Users\Brandon\Documents\parallax\docs\superpowers\plans\2026-08-01-lane-credential-and-lock.md:655) [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:658](C:\Users\Brandon\Documents\parallax\docs\superpowers\plans\2026-08-01-lane-credential-and-lock.md:658)

`-Path` is the right parameter name. The current implementation already declares it as a mandatory string and applies literal path semantics during probing and reading. [tools/read-kimi-credential-state.ps1:27](C:\Users\Brandon\Documents\parallax\tools\read-kimi-credential-state.ps1:27) [tools/read-kimi-credential-state.ps1:61](C:\Users\Brandon\Documents\parallax\tools\read-kimi-credential-state.ps1:61) [tools/read-kimi-credential-state.ps1:68](C:\Users\Brandon\Documents\parallax\tools\read-kimi-credential-state.ps1:68)

## Task 1

The no-host defect was fixed, but the current extractor stores steps in a dictionary keyed by host. A second `powershell.exe` step overwrites the first, so the checker loses both multiplicity and one step’s module set before checking parity. [evals/tools/check_workflow_paths.py:84](C:\Users\Brandon\Documents\parallax\evals\tools\check_workflow_paths.py:84) [evals/tools/check_workflow_paths.py:112](C:\Users\Brandon\Documents\parallax\evals\tools\check_workflow_paths.py:112)

A synthetic workflow containing two `powershell.exe` steps and one `pwsh.exe` step can therefore present the expected host set even though three steps were discovered. The existing automated mutations cover a missing host set and a module missing from one retained host entry, but not duplicate host multiplicity. [evals/multi-model-verify/test_backup_lane.py:1031](C:\Users\Brandon\Documents\parallax\evals\multi-model-verify\test_backup_lane.py:1031) [evals/multi-model-verify/test_backup_lane.py:1055](C:\Users\Brandon\Documents\parallax\evals\multi-model-verify\test_backup_lane.py:1055)

BLOCKING FIX:

- Preserve every discovered step rather than collapsing them into a host-keyed dictionary.
- Require the discovered host multiset to be exactly one `powershell.exe` and one `pwsh.exe`.
- Check required modules in each preserved step.
- Add a mutation with two `powershell.exe` steps and one correct `pwsh.exe` step, placing a complete module set in the duplicate that would overwrite the incomplete one under the current implementation; require failure.

No design change is needed; this is a follow-up code correction to Task 1’s existing host-parity requirement. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:117](C:\Users\Brandon\Documents\parallax\docs\superpowers\plans\2026-08-01-lane-credential-and-lock.md:117)

Verdict: FIX — preserve and validate host-step multiplicity.

## Task 2

The current implementation explicitly maps only `ok` to 0 and every other successfully reported state to 1. [tools/read-kimi-credential-state.ps1:22](C:\Users\Brandon\Documents\parallax\tools\read-kimi-credential-state.ps1:22) [tools/read-kimi-credential-state.ps1:35](C:\Users\Brandon\Documents\parallax\tools\read-kimi-credential-state.ps1:35) Existing tests pin that mapping for `absent`, `unreadable`, and every malformed class. [evals/multi-model-verify/test_kimi_credential_state.py:132](C:\Users\Brandon\Documents\parallax\evals\multi-model-verify\test_kimi_credential_state.py:132) [evals/multi-model-verify/test_kimi_credential_state.py:139](C:\Users\Brandon\Documents\parallax\evals\multi-model-verify\test_kimi_credential_state.py:139) [evals/multi-model-verify/test_kimi_credential_state.py:155](C:\Users\Brandon\Documents\parallax\evals\multi-model-verify\test_kimi_credential_state.py:155)

BLOCKING FIX:

- Change every status row to expect exit 0.
- Require empty stderr for every successful classification.
- Freeze the output as an object with exactly `status`, `detail`, and `fields`, with allowed status/detail pairings from Task 2’s table and `fields` an array of strings. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:140](C:\Users\Brandon\Documents\parallax\docs\superpowers\plans\2026-08-01-lane-credential-and-lock.md:140)
- Add `PARALLAX_KIMI_CREDENTIAL_STATE_FAULT`: validator-only, activated by any nonempty value after parameter validation and immediately before the path probe; exit 1, empty stdout, and exact stderr `PARALLAX_KIMI_CREDENTIAL_STATE_FAULT injected: simulated validator failure`.
- Test that seam under both hosts.
- Add a binding-refusal test requiring nonzero and no valid result line.
- Require bound blank or whitespace-only `-Path` to take the validator-failure path, never report `absent`.

Verdict: FIX — freeze and implement the classifier-style CLI contract.

## Task 3

No validator dependency or changed lock behavior.

Verdict: PASS. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:172](C:\Users\Brandon\Documents\parallax\docs\superpowers\plans\2026-08-01-lane-credential-and-lock.md:172)

## Task 4

No validator dependency or changed live-lock oracle.

Verdict: PASS. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:352](C:\Users\Brandon\Documents\parallax\docs\superpowers\plans\2026-08-01-lane-credential-and-lock.md:352)

## Task 5

Task 5 invokes the validator twice—before deciding whether to run the client and after any client run—but currently freezes only the status-driven branch. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:399](C:\Users\Brandon\Documents\parallax\docs\superpowers\plans\2026-08-01-lane-credential-and-lock.md:399)

It also needs the acceptance rule beyond exit zero. A caller that checks only exit 0 would accept missing, malformed, or schema-invalid stdout as a completed measurement—the inverse of the current exit-code problem.

BLOCKING FIX:

- Invoke the sibling validator through `$PSScriptRoot`, passing `-Path` the resolved credential-file path.
- Accept a measurement only when the process launched, exited 0, wrote empty stderr, and wrote exactly one parseable, schema-valid result line.
- Anything else is validator failure, not `absent`, `unreadable`, or `malformed`.
- A pre-client validator failure exits the wrapper with 6, invokes no client, writes no `-VerdictOut`, and releases in `finally`.
- A post-client validator failure exits 6, writes no `-VerdictOut`, and releases in `finally`; the client may already have run.
- Add both opposing caller oracles: nonzero with a syntactically valid `absent` line must be treated as validator failure, and exit 0 with malformed/schema-invalid output must also be treated as validator failure.
- Exercise both the pre-client and post-client validator calls. Use a disposable copied `tools` directory containing the wrapper, lock tool, and a stateful validator stub so `$PSScriptRoot` resolves the stub without touching the repository tool.

Verdict: FIX — freeze strict result acceptance and both invocation-failure positions.

## Task 6

Task 6 validates after acquiring the lock, but currently specifies only the three actionable reported states. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:460](C:\Users\Brandon\Documents\parallax\docs\superpowers\plans\2026-08-01-lane-credential-and-lock.md:460) Its recovery tests likewise cover `absent`, `unreadable`, and `malformed`, not a failed validator invocation. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:486](C:\Users\Brandon\Documents\parallax\docs\superpowers\plans\2026-08-01-lane-credential-and-lock.md:486)

BLOCKING FIX:

- Use the same `$PSScriptRoot` invocation and strict acceptance rule.
- Validator failure exits 6, emits no login recovery command, performs no build work after validation, runs failed-build cleanup, and releases the acquired lock.
- Add the same two opposing oracles: nonzero plus valid-looking status output, and exit 0 plus invalid output. Neither may be interpreted as a credential state.
- Require no custody JSON, no retained lock, and no credential value in diagnostics.

Verdict: FIX — distinguish actionable credential states from validator failure.

## Task 7

No direct validator-interface change; it consumes credentials through the already specified helper and builder lifecycles.

Verdict: PASS. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:510](C:\Users\Brandon\Documents\parallax\docs\superpowers\plans\2026-08-01-lane-credential-and-lock.md:510)

## Task 8

The existing table already has the correct semantic rows, but it needs a frozen rule selecting them. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:655](C:\Users\Brandon\Documents\parallax\docs\superpowers\plans\2026-08-01-lane-credential-and-lock.md:655)

BLOCKING FIX: Amend and pin check 8 so that:

- `absent`, `unreadable`, `malformed`, and `ok` are consumed only from a strictly accepted exit-0 report.
- Process-launch failure, any nonzero exit, nonempty stderr, zero or multiple stdout lines, JSON parse failure, wrong keys/types, or an invalid status/detail pairing selects “validator itself fails to run” → `BROKEN`.
- No credential recovery command is fabricated for validator failure, because no credential state was measured.
- Add fixtures proving nonzero plus a valid-looking `absent` report remains `BROKEN`, while exit 0 plus a valid `absent` report is `N/A`.

Verdict: FIX — pin the boundary between a reported state and no measurement.

## Task 9

No validator CLI is shipped in the three contract regions, and no amended behavior contradicts their credential-state wording.

Verdict: PASS. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:703](C:\Users\Brandon\Documents\parallax\docs\superpowers\plans\2026-08-01-lane-credential-and-lock.md:703)

## Task 10

The final gate remains valid, but it must run after the Task 1 parity follow-up and the amended Task 2 tests. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:735](C:\Users\Brandon\Documents\parallax\docs\superpowers\plans\2026-08-01-lane-credential-and-lock.md:735)

Verdict: PASS.

## ACL fixture

The `takeown` cleanup is acceptable as implemented. It targets only a credential file created beneath `tmp_path`, runs inside `finally`, and checks both `takeown` and `/reset` return codes. [evals/multi-model-verify/test_kimi_credential_state.py:104](C:\Users\Brandon\Documents\parallax\evals\multi-model-verify\test_kimi_credential_state.py:104) [evals/multi-model-verify/test_kimi_credential_state.py:111](C:\Users\Brandon\Documents\parallax\evals\multi-model-verify\test_kimi_credential_state.py:111) [evals/multi-model-verify/test_kimi_credential_state.py:139](C:\Users\Brandon\Documents\parallax\evals\multi-model-verify\test_kimi_credential_state.py:139)

It also reaches the real operation under test—`ReadAllBytes` failing—rather than merely exercising a validator seam. [tools/read-kimi-credential-state.ps1:65](C:\Users\Brandon\Documents\parallax\tools\read-kimi-credential-state.ps1:65) Given the reported successful round-trip under both hosts, I would not block Task 2 on replacing it.

## Overall verdict

FIX.

The design decision is settled:

- `-Path` is frozen.
- All four classifications exit 0.
- Validator failure exits 1 or fails to launch, produces no accepted report, and is never interpreted as a credential state.
- Every caller requires both successful process execution and a strict valid report.
- Task 1 also needs the duplicate-host-step correction before proceeding as complete.

Final check — UNVERIFIED:

- I read commit `ac3e4d8` and the current Task 2 implementation, but did not rerun the reported Task 1 mutations or the 54 dual-host tests.
- The live claim that `takeown` plus `/reset` round-trips reliably on both hosts is user-measured; I verified the fixture’s code and containment, not the executions.
- Measurements 1–21 and the three-login generalization remain external to this review.
- Tasks 3–10 remain unbuilt except for the uncommitted Task 2-related fixture changes visible in the worktree.