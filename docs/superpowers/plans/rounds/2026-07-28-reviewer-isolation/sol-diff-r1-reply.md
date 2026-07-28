The branch is not merge-ready. The override handoff and contract pins hold, but the review missed false-clean paths, a potentially destructive relative-path bug, and undeclared post-freeze drift.

### 1. Tasks 1–6 spec fidelity

The final-state deliverables mostly exist: both scripts/tests, transport preambles, six contract regions, dual-host CI, doctor check, and version 0.17.0 are present (`skills/multi-model-verify/SKILL.md:120-230`, `.github/workflows/skill-evals.yml:81-97`, `.claude-plugin/plugin.json:1-4`).

The “every checkbox exactly as frozen” claim nevertheless fails:

- The plan was modified after its stated freeze. At `cd66546`, the parser had one `KnownPromptBlocks` list and treated `permissions instructions` as the tag name (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md@cd66546:458-522`). HEAD replaces that with separate name/container lists and changes unmatched-tag semantics (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:471-486`, `:520-543`). The implementation follows the post-freeze text (`tools/codex-context-probe.ps1:122-195`).
- Frozen Task 1 prescribed double-quoted TOML (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md@cd66546:583-592`); the implementation correctly uses single-quoted literals and rejects apostrophes (`tools/codex-context-probe.ps1:231-257`). Correctness does not erase spec drift.
- Frozen Task 2 prescribed invoking `.ps1` stubs through `powershell` and formatting through `Out-String` (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md@cd66546:1066-1083`). HEAD instead adds in-process invocation, UTF-8 console decoding, and join-not-format behavior (`tools/codex-context-probe.ps1:293-334`). The design itself labels these as “during Task 2” revisions (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:484-493`).
- Frozen Task 3 stages broad pathspecs and does not prune empty parents (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md@cd66546:1921-1938`); HEAD tracks exact entries and prunes parents (`tools/new-review-mirror.ps1:218-255`).
- Task 3’s frozen interface says the probe child receives `-SuppressSkills -Json`, omitting the required `-OverrideOut` (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1343-1346`), while the prescribed/implemented call includes it (`tools/new-review-mirror.ps1:297-305`). That internal contradiction required judgment.
- Task 4’s frozen rewrite orders the client probe before mirror-remediation prose (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2241-2287`); HEAD puts mirror construction first and the client half later (`skills/multi-model-verify/SKILL.md:85-130`).

The scratchpad capture, red-before-green runs, tests-first chronology within combined commits, and every per-task gate invocation are not tree-verifiable.

**Verdict 1: FIX — preserve the `cd66546` blob as the immutable plan, enumerate every post-freeze implementation amendment, and obtain approval rather than silently editing the authority.**

### 2. Declared deviations

The stated justification for the tool-surface addition is reasonable: the plan mandates the behavioral run and then the whole-branch/mode-diff review (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2590-2600`). Given the user decision in the brief, adding the limitation, backlog item, and matching pin did not itself require reopening tool-surface design.

But the deviations are wider than (a)–(c). The post-freeze parser rewrite, Task 2’s three runtime-driven changes, Task 3’s staging/pruning changes, and mutation of the frozen plan are additional deviations. Revision 7 explicitly records three of them as implementation-time discoveries (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:484-493`), while the mirror differs materially from its frozen implementation (`tools/new-review-mirror.ps1:218-255` versus frozen plan `@cd66546:1921-1938`).

These correctness changes should not be reverted blindly, but under the zero-judgment contract they needed user approval when discovered.

**Verdict 2: ESCALATE — ask the user to approve or reject the complete post-freeze amendment set; (a)–(c) are not the complete set.**

### 3. Verified override equals dispatched override

This invariant holds within the documented procedure:

- The second call receives `$override`, and only after block absence is proven are its strict UTF-8 bytes written and hashed (`tools/codex-context-probe.ps1:438-480`).
- `-SuppressSkills` without an output artifact blocks (`tools/codex-context-probe.ps1:426-430`).
- Both dispatch and resume independently read the bytes once, hash them, strict-decode them, and pass the in-memory value (`skills/multi-model-verify/SKILL.md:174-180`, `:219-230`). A file mutation after the read cannot change the already decoded argument; a mutation before it causes a hash mismatch.
- The mirror resolves a default artifact and passes that same target to the probe (`tools/new-review-mirror.ps1:170-193`, `:297-312`).

**Verdict 3: PASS.**

### 4. Fail closed everywhere

Refuted in several independent ways:

- Without `-SuppressSkills`, the probe never performs pass two but still emits `status = "clean"` and exits 0 (`tools/codex-context-probe.ps1:422-426`, `:483-505`).
- `new-review-mirror.ps1 -SkipProbe` explicitly prints `probe: skipped` and exits 0 without any measurement (`tools/new-review-mirror.ps1:295-323`).
- A first-pass skills block that is present but parses to zero is accepted. The code checks presence only (`tools/codex-context-probe.ps1:368-377`); the test itself says the top level “must refuse” that state (`evals/multi-model-verify/test_codex_context_probe.py:105-111`) but tests it only on pass two (`:418-424`). A direct no-suppression run against the committed malformed fixture returned clean with zero skills.
- The skill regex truncates a path at its first `)` (`tools/codex-context-probe.ps1:80-90`). In measurement-only mode, that truncated rooted path can be classified as home and reported clean.
- An unterminated known container is deliberately masked through end-of-prompt rather than rejected (`tools/codex-context-probe.ps1:151-165`), allowing later unknown structures to disappear from the scan.
- “Every failure exits 1” also contradicts the frozen exit contract: script/environment errors are exit 2 (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:15-16`; `tools/codex-context-probe.ps1:338-350`; `tools/new-review-mirror.ps1:140-209`).

The named no-text chunk, unplaceable source, and second-pass-only unknown-block cases do block correctly (`tools/codex-context-probe.ps1:54-60`, `:391-395`, `:442-459`).

**Verdict 4: FIX — reject present-but-zero on pass one; validate container closure and full skill-line/path consumption; reserve `clean`/exit 0 for a completed suppression pass; and make `-SkipProbe` report a non-clean outcome. Keep exit 2 for script errors and narrow the prose accordingly.**

### 5. Contract coverage

All six region bodies are whole-pinned in accepted positive-membership assertions (`evals/multi-model-verify/test_multi_model_verify.py:352-439`). The region bodies match the strings in SKILL.md and model-prompting-notes (`skills/multi-model-verify/SKILL.md:72-81`, `:131-158`, `:182-192`; `skills/multi-model-verify/references/model-prompting-notes.md:334-342`).

`DECLARED_REGIONS` contains exactly the six new ids, with no seventh new or phantom id (`evals/multi-model-verify/test_contract_coverage.py:641-648`). The assertion forms comply with the checker contract (`CLAUDE.md:55-85`).

**Verdict 5: PASS.**

### 6. Whole-branch review adjudication

The artifact factually returned no Critical/Important and five Minors (`docs/superpowers/plans/rounds/2026-07-28-reviewer-isolation/fable-review-e2e9242-5a0293d.md:26-42`). Dispositions 1, 2, and 5 stand: the version wording is now honest (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:349-358`), doctor splits repo versus machine scope (`commands/doctor.md:180-191`), and the historical override has a warning (`docs/superpowers/plans/rounds/2026-07-28-reviewer-isolation/README.md:10-17`).

Two dispositions do not stand:

- Minor 3 remains a wording defect. The design now claims omitted `--sandbox`/`-m` “cannot change what the probe reads” (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:176-185`). Rejection of those flags proves only that parity cannot be requested; it does not prove model or sandbox selection can never affect rendered prompt content. Mark that consequence UNVERIFIED.
- Minor 4 must be fixed. The guard resolves relative `MirrorPath` against process cwd (`tools/new-review-mirror.ps1:146-168`), while `Test-Path`, `Remove-Item`, and `New-Item` later resolve it against PowerShell’s provider location (`:195-204`). In an in-session invocation where those locations diverge, the guard can approve one absolute target and `-Force` can recursively delete another. Documented `-File` examples do not make the public parameter safe. Existing tests use subprocesses and absolute `Path` strings, so they do not exercise this (`evals/multi-model-verify/test_review_mirror.py:66-71`, `:307-359`).

The retained review’s strength assertion that every malformed-block direction is blocked is itself false (`fable-review-e2e9242-5a0293d.md:18`) for the first-pass case above.

**Verdict 6: FIX — resolve `MirrorPath` and `OverrideOut` once through the PowerShell provider before any guard or mutation, then use only those absolute values; add an in-session changed-location regression test. Also narrow Minor 3’s design wording to UNVERIFIED.**

### 7. Documentation honesty

The active documentation still overclaims:

- SKILL.md permits and records a surviving global `AGENTS.md` (`skills/multi-model-verify/SKILL.md:115-130`) but then says a clean probe means the reviewer was “TOLD nothing extra” (`:148-157`).
- The design places the same “told nothing extra” sentence directly beside its admission that global `AGENTS.md` remains a back-channel (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:317-338`).
- README says the prompt must “advertise nothing” (`README.md:165-175`), although clean reports can carry `global_agents_md=true` (`tools/codex-context-probe.ps1:483-503`).
- Backlog item 7 repeats the same prompt-wide claim (`docs/superpowers/plans/2026-07-27-0150-backlog.md:343-349`).
- Retained raw debate artifacts still say `prompt-input` reveals the “whole instruction surface” (`docs/superpowers/plans/rounds/2026-07-28-reviewer-isolation/sol-plan-r1-brief.md:31-34`; `sol-plan-r1-header.txt:44-47`). They are historical, but “nowhere in the range” is therefore literally false.

**Verdict 7: FIX — say precisely that clean means no advertised skills and no plugin/apps feature blocks, while global `AGENTS.md` remains recorded and the tool surface remains unmeasured. Update the region pin, README/design/backlog, and label superseded claims in the rounds README without rewriting raw artifacts.**

UNVERIFIED: scratchpad raw-prompt capture; exact tests-first/red-green chronology; per-task gate executions; and the underlying live Codex claims about rejected flags, MCP startup lines, and prompt contents. I verified their documentation, not the external events.

**Overall verdict: ESCALATE — do not merge. Claims 4, 6, and 7 require fixes, and the wider undeclared post-freeze amendments require explicit user approval.**