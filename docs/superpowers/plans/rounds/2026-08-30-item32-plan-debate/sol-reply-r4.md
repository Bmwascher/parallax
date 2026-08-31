The rewrite still does not converge. The largest remaining defect is at the new launch boundary: directory creation, wrapper creation, process creation, and PID publication are not one fail-closed transition.

## Revised findings

1. CREATE-NEW SEMANTICS — DOES NOT CLOSE

The proposed reservation command lacks both `-ErrorAction Stop` and an enclosing fail-closed preference: `$d = (New-Item ...).FullName` is the complete command at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:395`. An existing-directory error is non-terminating by default, so the following statements can run with no valid `$d`; the repo’s own measured fail-closed pattern explicitly sets `$ErrorActionPreference = 'Stop'` so later statements become unreachable after failure at `tools/new-kimi-lane-home.ps1:165-173`.

The test also only forbids the exact token order `-ItemType Directory -Force`, so `-Force -ItemType Directory` would evade it at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:104-113`. Task 9 is likely to discover the defect because it requires the second reservation to fail rather than proceed, but that means the plan currently instructs an implementation its own measurement should reject at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:730-736`.

FIX — add `-ErrorAction Stop` to the canonical reservation and `Start-Process` calls, pin the exact fail-closed line, and make the duplicate-path probe assert that a sentinel statement after `New-Item` was not reached.

2. SEVEN STATES — DOES NOT CLOSE

The count is now consistently seven, and liveness correctly dominates reply and exit interpretation when a valid recorded PID exists at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:265-281` and `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:190-207`.

But the model assumes a recorded PID. `Start-Process` runs first and the PID file is written in a separate statement afterward at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:421-425`. A wrapper-write failure, launch failure, partial PID write, or PID-write failure therefore leaves a reserved directory with no usable PID. The polling contract has no branch for that condition because it begins by polling “against the recorded pid” at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:288-298`.

There is also a smaller classification error: state one is RUNNING, yet the region calls all six non-result states “transport failures” at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:269-278`; the thirty-minute rule instead treats a still-running round as UNFINISHED at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:292-295`.

FIX — add a launch-not-committed/no-valid-PID state, make PID publication part of a guarded launch transaction, kill `$proc.Id` if publication fails, and classify RUNNING as unfinished rather than a transport failure.

3. KIMI LAUNCHES AND REPLY ARTIFACT — PARTLY CLOSES

The task now supplies wrappers, captured stdout as `$d\reply`, stderr as `$d\transcript`, and a `Start-Process` shape with `-WorkingDirectory`; I read the two native-line assertions at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:484-512` and the implementation instructions at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:520-540`.

The claim that `>= 3` proves no call was left behind is false. The three reservation and launch counts are global counts, not assertions attached to dispatch, resume, and write-probe respectively at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:494-509`. The test asserts native lines for dispatch and resume only; it does not assert the write-probe’s native invocation at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:484-493`. A write-probe section containing reservation and launch prose/code but no correct probe wrapper can therefore satisfy Task 5’s oracle.

FIX — give each Kimi call a unique marker and assert, per marker, one reservation, the correct native invocation, one launch, and its reply artifact binding.

4. WRAPPER EXTRACTION — PARTLY CLOSES

Unique adjacent markers, exact-match cardinality, explicit indentation handling, placeholder rejection, and absolute-path Kimi substitution address the previous ordinal-fence and PATH-shadowing findings at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:673-700`.

Two holes remain:

- The test is required to read the real documents rather than a copy at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:677-683`, but its self-test deletes a marker in a scratch copy at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:704-707`. No injection point or extractor API is specified that makes the scratch copy become the test input.
- Launch markers are added at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:673-675`, but only wrappers are parsed and executed at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:685-702`. A malformed launch fence can therefore pass Task 8.

FIX — expose an extractor that accepts a source path for the negative scratch-copy test, and parse/stub-run every marked launch as well as every wrapper.

5. TASK-LOCAL ORACLES — DOES NOT CLOSE

Several remain satisfiable by partial work, and Task 9 has no explicit task-local oracle at all. The detailed task-by-task sweep is below. The plan’s blanket assertion that every task now has an oracle at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:13-15` is therefore not true.

FIX — strengthen Tasks 1, 3, 4, 5, 7, 8, 9, and 10 as specified in sweep (c).

6. SPEC RECONCILIATION — DOES NOT CLOSE

The spec still contains the exact stale region-name defect the rewrite says was corrected: its testing section proposes `detached-dispatch-codex` and `detached-dispatch-backup` at `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:246-250`, while its later inventory names the actual five regions at `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:285-291`.

It also retains two refuted mechanism claims:

- It describes every wrapper as carrying the `$OutputEncoding` preamble at `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:136-164`, while the plan correctly says argument-based lanes carry no such preamble at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:226-230`.
- It still says a wrapper file “has no quoting layer at all” at `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:165-169`, while the revised plan correctly admits that PowerShell parsing and native argv construction remain at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:231-235`.

Task 10’s grep does not search for any of those stale statements at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:769-779`.

FIX — reconcile the whole mechanism and testing sections, then make Task 10’s oracle assert the exact five-region inventory and the corrected lane-specific encoding/quoting claims.

## UNVERIFIED

- The fresh-shell and background-Agent behavior remains harness-contract evidence rather than repo evidence, as the plan itself discloses at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:28`.
- Cross-call survival and delayed exit publication remain unverified until Task 9 performs its two-host measurement at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:724-750`.
- No real detached Kimi call is planned for the measurement record; Task 9 explicitly limits Kimi verification to stub execution at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:746-750`.

I did not use those facts to rescue any verdict.

## Sweeps

The base rate remains three completion-model holes in three rounds: the plan itself records the stale-artifact hole, omitted state, and path-existence/liveness hole at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:818-824`. The rewrite does not reset that prior.

### (a) The eighth state

Yes: **DIRECTORY RESERVED, BUT LAUNCH NOT COMMITTED / NO VALID PID**.

Three concrete paths reach it:

1. The directory is created, then writing `wrapper.ps1` or `stdin.empty` fails; wrapper creation is instructed at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:381-395`, while stdin is not created until `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:421-422`.
2. `Start-Process` fails, leaving no `$proc` and no valid PID at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:423-424`.
3. `Start-Process` succeeds but PID publication fails, leaving a live, untracked wrapper because process creation and publication are separate statements at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:423-424`.

Those cases are indistinguishable from disk if no explicit launch-commit artifact exists, yet one may contain a live process. By contrast, a partially written exit file and a reply still being written are now correctly covered when a valid PID exists: liveness dominates first, and an unreadable exit becomes state three at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:265-275`.

FIX — add launch commitment as a guarded phase and never enter the seven completion states without a valid, published PID.

### (b) What centralizing the launch fails to catch

The executable launch was not centralized. The supposedly canonical region contains prose but no `Start-Process` command at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:243-259`. Task 4 still creates two literal copies at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:373-425`, and Task 5 requires at least three more literal copies at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:494-509`.

Concrete false-green: all three Kimi launch strings can occur under two call sites while the write-probe remains unlaunched; the global `>= 3` count still passes at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:494-509`. Five site-specific assertions would catch that association failure.

The Codex instructions also do not cite `detached-dispatch-launch` by name where the launch is copied; they cite the notes for brief composition and the seven states instead at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:381-389` and `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:414-425`. Under the canonical region’s own rule, a lane not citing it is not detached at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:254-258`.

FIX — either centralize executable generation in one shipped/rendered block, or admit five copies and bind one exact launch oracle to each call site.

### (c) Ten task-local oracles

| Task | Assessment |
|---|---|
| 1 | Weak. The required comment must contain the date, measurement, relocation, and remedy rationale at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:47-50`, but the oracle accepts any unrelated occurrence of `"backlog item 32"` at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:61-66`. |
| 2 | Capable of detecting absent tests because all five names and the expected `4 FAILED, 1 PASSED` count are stated at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:186-191`. Its reservation assertion nevertheless pins the broken non-terminating command at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:94-113`. |
| 3 | Weak. Removing one complete region/declaration/pin triplet leaves coverage internally consistent, while the broad `-k "pinned or documented or declared or locked"` command can still return green; no exact expected test-name set is enforced at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:318-357`. |
| 4 | Weak to partial implementation. All assertions are global `>= 2` counts at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:104-174`, so duplication at one site can hide an unchanged other site while its oracle still reports five passes at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:435-438`. |
| 5 | Weak. Global `>= 3` counts and only two native-line assertions do not bind the write-probe’s wrapper to its launch at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:484-512`. |
| 6 | Adequate as written. I read the required assertions for both git calls, verified-empty hooks, and negative BLOCKED cases at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:564-575`, plus the full file test and independent count at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:577-580`. |
| 7 | Weak. The exact new region and zero-count for `"STOP and surface it"` can pass while the old second passage, `"only on the user's choice, never automatically"`, remains; the replacement requires deleting both at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:634-645`, but the oracle checks only the first at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:651-654`. |
| 8 | Weak. It parses wrappers but not marked launches, and the scratch-copy negative test has no specified way to redirect a real-document-only extractor to the scratch input at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:677-707`. |
| 9 | Missing as a task-local oracle. It contains measurements and a manually written record, but no check that the record exists or contains both hosts and all three measurements at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:718-756`; Task 10 does not check that file at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:761-779`. |
| 10 | Weak. Its grep ignores stale region names, stale mechanism text, `CLAUDE.md`, and backlog closure even though those are Task 10’s own outputs at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:765-803`. The current stale region names at `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:246-250` demonstrate the false-green directly. |

FIX — Task 6 is sufficient; Task 2 is locally detectable but pins the wrong reservation semantics; Tasks 1, 3, 4, 5, 7, 8, 9, and 10 require stronger task-specific oracles.