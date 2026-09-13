**Plan verdict: FIX.** The pinned plan has failures in the region-citation guard and PowerShell 5.1 resolver, plus path-resolution and verification gaps.

`plan` below means `docs/superpowers/plans/2026-09-12-artifact-roots.md:1`.

1. Placement preserves the model declaration ordering, but compatibility with every reader fails. `evals/multi-model-verify/test_contract_coverage.py:834` searches every declared region id as a substring and requires a preceding `<file>.md's`. Registering `artifact-roots` therefore makes the new `tools/artifact-roots.ps1` and `artifact-roots.txt` references invalid citations (`plan:161`, `plan:212`). Edit A also contains an unqualified region reference (`plan:781`). Use a distinct region id such as `round-artifact-roots`, update its registration, markers, parser, pin and citations, and qualify Edit A. **FIX.**

2. The adjacent literals constitute one whole-region pin (`plan:116`), matching the eight-line region (`plan:169`). Normalization preserves whole-region containment, and registration detects deletion (`evals/multi-model-verify/contract_coverage.py:131`; `evals/multi-model-verify/test_contract_coverage.py:537`, `:546`, `:783`). The citation failure in claim 1 is separate from pin coverage. **PASS.**

3. The branch order implements explicit argument, existing override directory, then default (`plan:561`). The recorded KitnEssentials directories support override selection (`BACKLOG.md:100`). The existing mirror fixture creates a one-file source (`evals/multi-model-verify/test_dispatch_round.py:177`), and the output discloses selection through `docs-root source` (`plan:652`). **PASS.**

4. The fixed-placement reasons hold. I read the vendor files: `C:/Users/Brandon/.claude/plugins/cache/claude-plugins-official/superpowers/6.3.0/skills/subagent-driven-development/scripts/sdd-workspace:35` creates the ledger directory and self-ignore file; the adjacent `skills/subagent-driven-development/SKILL.md:141` reads `<workspace>/progress.md`. Mirror overlap refusals cover all three relationships (`tools/new-review-mirror.ps1:1455`, `:1459`, `:1465`). Attestation and checkpoint use the common directory (`tools/write-attestation.ps1:56`, `:72`, `:99`), which the declaration represents correctly (`plan:176`). Resolver defects are addressed in claim 5. **PASS.**

5. The resolver has three concrete defects, and the JSON rendering claim is false.

   - `Resolve-Row` passes placeholder-bearing strings to `IsPathRooted` (`plan:588`). A read-only probe using `docs/superpowers/plans/<date>-<topic>.md` threw “Illegal characters in path” on PowerShell 5.1 and returned `False` on PowerShell 7. Separate the placeholder tail, resolve the real parent, then append the tail.
   - Git runs from `-RepoRoot`, but relative common-dir output is joined to `$toplevel` (`plan:545`, `plan:555`). In this checkout, running Git from `skills` returns `../.git`; the planned join resolves outside the checkout. Resolve against the directory passed to Git, as the emitter does (`tools/write-attestation.ps1:61`), and add a subdirectory-input regression.
   - Valid `-DocsRoot ./other/root` retains `./` in the printed roots (`plan:562`, `plan:589`), while assertion targets are canonicalized (`plan:617`). The string comparison consequently rejects membership (`plan:629`). Canonicalizing real parents also fixes this case.

   The ordered-object probe produced different whitespace on the two hosts at `-Depth 3`; JSON structure can be compared after parsing, as existing proposed tests already do (`plan:305`, `plan:648`). **FIX.**

6. The ceiling conclusion holds, but the exact accounting needs correction. Applying the linter’s frontmatter removal and newline joining yields **25,987** body characters; the quoted edits yield **25,995**, flooring to **6,498** tokens (`evals/tools/skill_lint.py:163`, `:182`, `:339`; `plan:781`, `plan:788`, `plan:797`). Correct the measurement at `plan:804`. The stop condition respects the user-owned removal decision (`BACKLOG.md:4225`). **FIX, numerical correction only.**

7. The current sweep produces exactly the two stated override-literal hits, and the replacements remove them (`skills/multi-model-verify/SKILL.md:323`; `skills/multi-model-verify/references/frozen-plan-format.md:28`; `plan:797`, `plan:820`). However, the negative control does **not** prove every shape fires: its ledger example only checks the dated exemption (`plan:767`). Add a positive assertion for `.superpowers/sdd/plan/progress.md` against the ledger pattern (`plan:732`). **FIX.**

8. The fixture extension, two commits, file-set comparison, negative control and independent host marks fit together (`plan:954`, `plan:1016`, `plan:1029`, `plan:1037`; `tools/write-attestation.ps1:67`). Dispatch artifacts remain outside the source through the existing fixture (`evals/multi-model-verify/test_dispatch_round.py:230`, `:249`). Both workflow additions and the required-module registration are specified (`plan:1079`, `plan:1088`), matching the guard’s requirement (`evals/tools/check_workflow_paths.py:64`). Its observation limit is addressed in claim 11. **PASS.**

9. The replacement needles match only the two identified comments in the searched evals (`evals/multi-model-verify/test_multi_model_verify.py:1660`, `:3177`). The raw-rounds pin is outside the replacement (`:1722`; `plan:827`). The new citation-guard failure in claim 1 does not invalidate this narrower raw-text-pin claim. **PASS.**

10. Digest recomputation follows the implementation. Canonical content includes the heading, non-Verified fields, body and group identity; stale digests fail comparison (`evals/tools/backlog_lint.py:199`, `:209`, `:234`). Task 5 obtains the new digest and reruns validation (`plan:1164`, `plan:1169`). **PASS.**

11. The checks have failing assertions, but Task 4 does not detect **any additional path**. `tree_paths` filters with `is_file()`, so an unexpected empty directory disappears from the observation (`plan:992`). Include directories, account explicitly for the attestation’s newly created parent directories, and add an empty-directory negative control alongside the existing file control (`plan:1029`, `plan:1043`). **FIX.**

12. The planned changes respect the stated scope exclusions (`docs/superpowers/specs/2026-09-12-artifact-roots-design.md:313`; `plan:1199`). The historical attribution of the 54 MB copy is unresolved separately below. **PASS on scope.**

### Class sweep

I found two additional sentences naming consumer-repository paths outside the declared model:

- `agents/flash-implementer.md:39` identifies the workspace as the checkout; `:67` writes `<workspace>/AGY-TASK-BRIEF-<unique>.md` there, and `:79` deletes it afterward. This is an implementation-time artifact. State its exclusion explicitly if “every path” remains limited to review rounds (`plan:5`, `plan:169`).
- `skills/multi-model-verify/SKILL.md:389` names `.git/parallax/attestations/<head-sha>.json` “inside the reviewed repo.” That description is wrong for linked worktrees; the emitter uses the common directory (`tools/write-attestation.ps1:56`). Correct those words to reference the resolved attestation row and add coverage for the stale spelling. This requires a third targeted SKILL edit beyond Task 3’s authorized pair (`plan:16`, `plan:776`), so that scope decision belongs to the user.

The search included the four forbidden patterns, `.git/`, `.superpowers`, docs and rounds paths, workspace paths, save/write/create prose, and filesystem writers including `Join-Path`, `WriteAll*`, `Set-Content`, `New-Item`, `Copy-Item`, `mkdir` and `write_text`. The planned static sweep covers only four patterns and excludes Python tools through its globs (`plan:713`, `plan:724`).

Another escaping form is a dynamically assembled undeclared destination whose file is rewritten or created and deleted between snapshots. The four regexes cannot identify arbitrary constructed roots, and the final path-set difference cannot observe those writes (`plan:724`, `plan:995`, `plan:1019`, `plan:1028`). The Flash brief’s explicit deletion provides a concrete transient-write example (`agents/flash-implementer.md:79`).

### Final check

**UNVERIFIED:** Claim 12’s attribution of the 54 MB copy to a Codex controller on 2026-09-07. The design asserts it, but the retained pre-read identifies the rollout log as unread (`docs/superpowers/specs/2026-09-12-artifact-roots-design.md:35`; `docs/superpowers/plans/rounds/2026-09-12-artifact-roots/fable-spec-r1-reply.md:47`). That attribution contributes nothing to this verdict.

Instruction-bearing file content affecting the findings:

- `evals/multi-model-verify/test_contract_coverage.py:795`: “A declared id must be cited as `<file>.md's <id>`, never bare.” Its executable assertion establishes the citation failure; I treated it as evidence.
- `agents/flash-implementer.md:67`: “Write the brief to `<workspace>/AGY-TASK-BRIEF-<unique>.md`.” This establishes the additional artifact in the class sweep.
- `plan:16`: “Task 3 makes EXACTLY the two edits it quotes and nothing else in that file.” This makes the additional attestation-sentence correction a user-owned scope decision.

No file instruction paused the review. **Overall verdict: FIX**, principally for claims 1 and 5, with the specific verification corrections above.