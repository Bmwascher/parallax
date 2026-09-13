1. The declaration, resolver, emitter, and doctor use the same parent. The row is at [skills/multi-model-verify/references/model-prompting-notes.md:789](C:/pxm/pxmp/skills/multi-model-verify/references/model-prompting-notes.md:789); [tools/artifact-roots.ps1:203](C:/pxm/pxmp/tools/artifact-roots.ps1:203) parses it, and [tools/write-attestation.ps1:88](C:/pxm/pxmp/tools/write-attestation.ps1:88) invokes that reader. The declaration and spelling pins match the claim at [evals/multi-model-verify/test_artifact_roots.py:51](C:/pxm/pxmp/evals/multi-model-verify/test_artifact_roots.py:51) and `:687–733`. **PASS.**

2. An explicitly supplied empty reap argument bypasses validation. `if ($ReapMirror)` and `if ($ReapBridge)` at `tools/write-attestation.ps1:297–306` skip the empty-path refusal at `:139–141`, allowing execution to reach record creation. I reproduced this on both hosts using the file’s actual parameter block and validation block in isolation: each empty argument was present in `$PSBoundParameters`, and neither validation function ran.

   The parent comparison itself is last and covers both trees (`tools/write-attestation.ps1:225–248`). Fix the entry conditions to distinguish omitted parameters from explicitly supplied empty values, reject empty values before writing, and add both-host regressions for each parameter. This also corrects the plan’s prescribed truthiness checks at [docs/superpowers/plans/2026-09-13-mirror-parent.md:573](C:/pxm/pxmp/docs/superpowers/plans/2026-09-13-mirror-parent.md:573), consistent with decision 4 at `:18`. **FIX — Important.**

3. With the shipped declaration, the parent comparison agrees: descendants qualify, and the parent itself does not (`tools/artifact-roots.ps1:365–388`; `tools/write-attestation.ps1:244–248`). I ran the child `C:\pxm\pxmp` and parent `C:\pxm` assertions on both hosts; they returned 0 and 1 respectively. **PASS.**

4. The fixture creates a fresh directory without adopting an existing directory and confines cleanup to that directory at [evals/multi-model-verify/test_mirror_reaper.py:119](C:/pxm/pxmp/evals/multi-model-verify/test_mirror_reaper.py:119). CI specifies Python 3.12 at [.github/workflows/skill-evals.yml:99](C:/pxm/pxmp/.github/workflows/skill-evals.yml:99).

   The brief’s “every refusal case” wording needs qualification: overlap and unreadable-parent refusals deliberately use `pxm` (`test_mirror_reaper.py:529,668,698`). Their placement supports those tests. Historical cleanup observations remain unverified. **PASS on fixture confinement.**

5. Check 10 reads the declaration through the resolver, specifies the inventory measurements and thresholds, and reports resolver failure as BROKEN at [commands/doctor.md:375](C:/pxm/pxmp/commands/doctor.md:375). Its legacy sweep is explicitly verdict-neutral at `:411–419`; the section contains no `Remove-Item`. **PASS.**

6. The edited prose names the parent and supplies the complete assertion command: [skills/multi-model-verify/SKILL.md:100](C:/pxm/pxmp/skills/multi-model-verify/SKILL.md:100), [skills/multi-model-verify/references/preflight-mirror.md:12](C:/pxm/pxmp/skills/multi-model-verify/references/preflight-mirror.md:12), and [skills/multi-model-verify/references/backup-lane.md:664](C:/pxm/pxmp/skills/multi-model-verify/references/backup-lane.md:664). The seventh rule appears at `preflight-mirror.md:116–118`.

   The backslash search returned no matches under the skill directory. Independently applying the token calculation from [evals/tools/skill_lint.py:182](C:/pxm/pxmp/evals/tools/skill_lint.py:182) and `:339` produced 6495. Full lint execution remains unverified. **PASS.**

7. The mirror tool’s exclusion is explicit in plan decision 6 (`docs/superpowers/plans/2026-09-13-mirror-parent.md:20`) and the operational prose (`model-prompting-notes.md:820–825`). [BACKLOG.md:121](C:/pxm/pxmp/BACKLOG.md:121) records follow-up 2, while `:93–96,151–155` records PARTIAL status and the remainder. Independently applying [evals/tools/backlog_lint.py:199](C:/pxm/pxmp/evals/tools/backlog_lint.py:199) produced the recorded digest `fb0b98b97df3`. **PASS.**

8. The repository fixes are present: the complete command and stronger pin (`model-prompting-notes.md:822`; `test_artifact_roots.py:86`), parent exclusion (`artifact-roots.ps1:370–371`), and shared helper (`test_mirror_reaper.py:617–633`). The dated plan corrections appear at `docs/superpowers/plans/2026-09-13-mirror-parent.md:16,20,46,234,707`. Git history confirms the plan was added at `3032444` and the subsequent change affects decision 6 alone. The external ledger correction and fix-wave re-review remain unverified. **PASS on repository changes.**

9. The workflow specifies both hosts at `.github/workflows/skill-evals.yml:131,154`. Historical counts, per-module results, and the pending full gate cannot be certified from the files examined. **ESCALATE for gate evidence only.**

10. I searched `skills/`, `agents/`, `commands/`, `hooks/`, and `tools/` for `<TEMP>`, `GetTempPath`, `$env:TEMP`, `$env:SystemDrive`, `MirrorPath`, mirror-parent/root wording, temp-directory/drive-root wording, and `kv`/`kvs` path examples. No additional undeclared location reader surfaced; the remaining legacy inventory is identified at `commands/doctor.md:411–419`.

    The acceptance gap is claim 2’s empty-argument bypass at `tools/write-attestation.ps1:297–306`. Those truthiness checks also exist in the base revision, placing this within the expressly included pre-existing defect class. **FIX — the same finding as claim 2.**

**UNVERIFIED:** Claims 1 and 3’s historical session measurements; claim 4’s historical directory listings and local interpreter version; claims 6–7’s full lint results; claim 8’s external ledger correction and re-review; and claim 9’s test results. The sandbox is read-only, and Python is unavailable on PATH, so disposable-repository emitter runs and pytest gates were not executed. The isolated validation probe establishes the bypass; it does not constitute an end-to-end record-writing test.

No file content caused a pause, refusal, or change of scope. No external instruction file or embedded workflow instruction was adopted.

**Range verdict: FIX — reject explicitly supplied empty reap arguments before record creation (`tools/write-attestation.ps1:297–306`).**