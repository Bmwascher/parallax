# Fable reviewer whole-branch review (mode diff), range cd0e863..f12b703

Dispatched 2026-09-13 via agents/fable-reviewer.md (model fable, tools Read/Grep/Glob),
brief retained as brief-fable-diff-r1.md. Reply below verbatim; the harness rendered
angle brackets as HTML entities (`&lt;` / `&gt;`) in the returned text and they are
restored here to `<` / `>`, which is the only change.

---

### Strengths

- The resolver's exit contract holds on both hosts by construction, not by luck. Every path parameter is screened for the Windows-forbidden set before any .NET path API sees it (`tools/artifact-roots.ps1:167-169` for `-DocsRoot`, `:249-252` for `-Assert`, with the drive colon stripped first), the per-debate `<...>` tail is split off before `GetFullPath` (`:208-213`), and every failure routes through `Fail` outside a `try` (`:67-84`). The six-case parameter-fault test (`evals/multi-model-verify/test_artifact_roots.py:246-263`) includes the unsubstituted-placeholder case that only PowerShell 7 would otherwise accept.
- `-Expect` closes the real hole the final review found, mechanically rather than by prose: the frozen plan parent contains every dated directory beside `plans/rounds/`, so a bare `-Assert` answers inside for the exact KitnEssentials shape. The tool refuses it when the caller names the intended root (`tools/artifact-roots.ps1:270-274`), the answer names both roots, and the test pair proves both directions, including the unchanged bare behaviour and why it is not clean (`test_artifact_roots.py:324-367`). The spec states the parameter as binding authority (`docs/superpowers/specs/2026-09-12-artifact-roots-design.md:217-223`).
- Native git runs under `Continue` with `$LASTEXITCODE` read, and the relative common dir is joined to the directory git ran in, not the toplevel (`tools/artifact-roots.ps1:136-157`); the subdirectory and `-RepoRoot .` cases are both tested (`test_artifact_roots.py:200-235`).
- The sweep is honest about its shape set: six enumerated shapes with `[/\\]` separators, each with a positive and a negative control (`test_artifact_roots.py:439-452`, `:476-517`), the exemption limited to declaration lines between the marker pair by line number (`:420-427`, `:520-529`), and the failure message prints what was searched for.
- The two common-dir rows are bound where a regex cannot reach. The emitter spells them as nested `Join-Path` (`tools/write-attestation.ps1:72`, `:99`), invisible to any `.git/parallax` shape; the writer test runs the real emitter, then asks the resolver `-Expect attestation` and `-Expect checkpoint` for the paths it produced (`test_artifact_roots.py:610-620`), and the notes say exactly this instead of overclaiming (`skills/multi-model-verify/references/model-prompting-notes.md:770-781`).
- The writer test is a path-set diff, directories included, snapshotted again after the resolver runs so the reader is inside the window it polices (`test_artifact_roots.py:564-625`); the two negative controls prove the diff and the membership answer can each fail (`:629-657`).
- `SKILL.md` carries exactly the three plan edits and nothing else (`skills/multi-model-verify/SKILL.md:153-154`, `:327-328`, `:392-394`), and Edit C removes a statement that was wrong in a linked worktree.
- Every new citation resolves under the region-citation rule, which whitespace-normalizes before matching and keys on the bare file name (`evals/multi-model-verify/test_contract_coverage.py:842`, `:856-858`), so the wrapped forms in `frozen-plan-format.md:30-31`, `preflight-mirror.md:17-18`, `backup-lane.md:667-668` and the `references/`-less form in backup-lane are all live citations, not dead pointers.
- Both CI host steps carry the module and the dual-host guard list locks it there (`.github/workflows/skill-evals.yml:143-144`, `:166-167`; `evals/tools/check_workflow_paths.py:79-82`). `build_real_mirror` gained `source=None` with every existing caller unchanged (`evals/multi-model-verify/test_dispatch_round.py:174-191`).
- The post-freeze amendments (the assert-mode character guard, `-Expect`) are recorded in the ledger as rulings with the spec named as the binding authority and a cost-if-wrong line each, which is what the diff debate needs to adjudicate them.

### Issues

#### Critical

None.

#### Important

None.

#### Minor

- `skills/multi-model-verify/references/model-prompting-notes.md:833-835`: "Before the retention copy, run the tool with `-Assert <destination> -Expect rounds` before the rounds retention copy and ..." doubles "before". This is the operating rule the session reads, outside the pinned region and outside any raw-text pin, so a one-clause edit carries no pin risk.
- `skills/multi-model-verify/references/frozen-plan-format.md:29-32` cites the tool for the plan save but not `-Expect frozenPlan`, while the notes rule (`model-prompting-notes.md:835`) requires it before the frozen plan save. The rounds paragraph at `:89-94` does name `-Expect rounds`. A reader of the format file alone would run the weaker check.
- `skills/multi-model-verify/references/model-prompting-notes.md:835-838` states that a path inside a different retained root is refused, which is true, but `-Expect frozenPlan` still accepts a dated directory beside `plans/rounds/` (it is inside the frozen plan parent, `tools/artifact-roots.ps1:257-262`). The rounds copy is the act that produced the KitnEssentials spread and `-Expect rounds` does refuse it, so this is a stated-limit gap in the prose, not a hole in the gate.
- `docs/superpowers/specs/2026-09-12-artifact-roots-design.md:225-228`: the exit-map paragraph still reads "1 asserted outside" while step 5 (`:217-223`) and the tool header (`tools/artifact-roots.ps1:16-22`) both add the `-Expect` mismatch to exit 1. One sentence, same file, two readings of code 1.
- `tools/artifact-roots.ps1:249-250`: the `-Assert` guard strips only a single drive-letter prefix, so a provider-qualified path (`FileSystem::C:\...`) that `Resolve-Absolute` could resolve is refused as a parameter fault. No shipped caller passes that form; noting it because the guard is stricter than the resolver behind it and the header does not say so.
- `evals/multi-model-verify/test_artifact_roots.py:409-410`: `hooks/*` is non-recursive. `hooks/` holds two files today (checked: `hooks.json`, `superpowers-review-companion.ps1`), so nothing escapes now; a future `hooks/<sub>/` script would.
- `evals/multi-model-verify/test_artifact_roots.py:577-588`: pre-creating the checkpoint before the snapshot buys the checkpoint-row binding at the cost of no longer observing that the emitter creates the shared `.git/parallax` parent on its own (the plan's expected set had it). The comment states the trade; it is the right trade, and `test_attestation.py` owns the emitter's own behaviour.

### Ledger minors triage

- T1, unused `json`/`re`/`subprocess` imports: moot, all three are used by the shipped module (`test_artifact_roots.py:125`, `:415`, `:92`). Ride.
- T2, placeholder rows keep the trailing slash and fixed rows do not: ride; the tests `norm()` it away and the comparisons in `-Assert` strip it, but the text output is the retained `artifact-roots.txt`, so the two spellings will sit in the record side by side. Cosmetic.
- T2, `-DocsRoot "."` wrong message: closed by the fix wave (`tools/artifact-roots.ps1:179-181`, test `:386-391`).
- T2, missing `-RepoRoot` exits 1 from `-File` binding: closed as documentation, the header now says so (`:19-22`). Ride.
- T2, `Resolve-Row` no-resolvable-parent branch untested: ride; reachable only by editing the pinned region, and the branch is a `Fail` with exit 2.
- T2, unknown-drive `-Assert` case now trips the character guard before `Resolve-Absolute`: ride; the test asserts the exit and the `ERROR:` prefix, which is the contract, and the provider-throw path is still exercised by the `-RepoRoot` unknown-drive case.
- T3, W391 blank line at EOF: ride.
- T3, inert lookbehind in the first shape: ride; the fix wave documented it (`:436-438`) and the shape still catches the KE form.
- T3, `test_sweep_can_fail` requests `tmp_path` unused (`:476`): ride, trivial.
- T3, forward-slash-only shapes: closed for backslash by the fix wave (`[/\\]` throughout, controls at `:504-517`); slashless spellings still escape and the comment says so. Ride.
- T3, `agents/fable-reviewer.md:20` cites `references/` relative to the skill dir: ride; the citation rule resolves by bare file name, so the prefix is cosmetic and the form is the required one.
- T3, Edit C brief quoted a fragment: process note, implementer resolved it correctly (`SKILL.md:392-394`). Ride.
- T4, two refusal assertions check exit 1 only (`:625`, `:657`): ride; both paths are refused for the same reason the third case pins, and the exit is the contract.
- T4, cross-module `from test_dispatch_round import` relies on prepend import mode: ride; CI invokes both modules by path in the same directory, and a comment at the import site would be the whole fix if importmode ever changes.
- T5, the one test that skips on pwsh and not on 5.1 is unnamed: ride for this merge (it predates the branch), but the ledger should name it once known, because an unnamed host-specific skip is exactly the shape the dual-host job exists to expose.
- Final, mixed printed casing between the repo row and the common dir: ride; every comparison is `OrdinalIgnoreCase` and the JSON consumers are the tests, which fold case.
- Final, duplicate sweep labels on one offending line: ride; the sweep has zero offenders, and two labels on one line is more information, not less.

### Assessment

Ready to merge: Yes

The range delivers what item 100 asked for with one declaration, one reader, a membership answer that refuses the specific shape that caused the spread, and tests that can fail on both hosts; the seven minors are prose consistency and stated limits, none of which changes what the gate accepts. The debate's useful work is adjudicating the two post-freeze amendments the ledger records (the assert-mode character guard and `-Expect`) against the frozen plan, since the spec rather than the plan is what now describes the shipped tool.
