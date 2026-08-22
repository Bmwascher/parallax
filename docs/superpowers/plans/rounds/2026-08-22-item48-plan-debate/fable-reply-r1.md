Round 1, Fable lane. Nonce FABLE-I48-7QX2. Subject: `docs/superpowers/plans/2026-08-22-item48-pwsh7-feasibility.md` on branch `item51-inline-brief-transport` (cut from `main` at `a3134dc` per probe-record.md:6-7).

## The session's claims

1. ACCEPTED. probe-record.md:75-89 (Defect 1, the read) and probe-record.md:91-111 (Defect 2, the argument) are two mechanisms; the record shows S2 fixing the read while quotes still vanish, so they are independent.
2. ACCEPTED. probe-record.md:67-73, every 7.6.5 cell reads "exact". Note the ceiling (probe-record.md:131-138) throws on BOTH hosts, so "both defects are 5.1-only" is correct only about the two defects, not about everything the probe found.
3. ACCEPTED with one narrowing. tools/check-drift.ps1:96 writes the task action as `powershell.exe ...`, verified. "Reached only under 5.1" is true of the registered task; a human running check-drift.ps1 by hand under pwsh reaches the same site harmlessly, so the claim is about the shipped path, not the site.
4. ACCEPTED. hooks/hooks.json:10 and hooks/hooks.json:22, both bare `pwsh`.
5. ACCEPTED. Plan lines 106-113; both wrong hand inventories are on record at backlog 3396-3406 and 3435-3445.
6. ACCEPTED. Plan lines 477-480 tie Task 4 to the re-exec NO-criterion.

## A. Oracle adequacy, task by task

- Task 1: WEAK. check-nocriteria.py verifies `w[2:42]` (plan line 156), a 40-character prefix of each bullet's first physical line. A paraphrase after character 40 passes while the record claims "Copied verbatim" (plan line 95). The skeleton as written IS verbatim against backlog 3573-3578, and both headings the slicer indexes are unique (backlog 3568, 3580), so the check works today; it just proves less than the record claims.
- Task 2: adequate as a negative control, and cannot detect family incompleteness (see B) \u2014 no cheap oracle could.
- Task 3: a green survey proves every match is CLASSIFIED, not classified correctly. The blanket `docs/ * * - record no-change` row (plan lines 417-421) makes this worse: `record` is defined "never executed" (plan line 241), yet survey.py, reexec/*.ps1 and missing-pwsh/probe.py live under docs/ and ARE executed by this plan. Any future entry point added under docs/ is absorbed silently forever.
- Task 4: the stage-A gate is sound, but the Step 5 table (plan lines 642-643) records only stage A/B exact and first-difference \u2014 a child that never started (nonzero returncode, no output file) tabulates identically to a child that received corrupt arguments. results.json holds returncode; the section table as specified drops it. FIX: add returncode/child-ran columns.
- Task 5: adequate; gh evidence is real-run evidence, and Step 3 correctly writes the Linux side as unproven.
- Task 6: FAILS OVER A BROKEN RESULT. The glob at plan line 772 (`tools/*.ps1 .githooks/* evals/tools/*.ps1`) misses `hooks/superpowers-review-companion.ps1` \u2014 a shipped script, and the only one already running under pwsh in production (hooks/hooks.json:10). The coverage table would omit it and nothing fires. The heading also pre-commits "the 13 shipped scripts" (plan line 767) before the command that counts them, against backlog 3485's own rule that the count is a claim.
- Task 7: strongest task in the plan. Both failure directions and the Windows parent-environment PATH-resolution trap are pre-named with honest stop/record rules (plan lines 895-910).
- Task 8: adequate; range not point, citations by item number.
- Task 9: see D. The only mechanical gate is the survey re-run; nothing checks that the five measurement sections stopped saying `NOT YET WRITTEN.` A verdict written over an empty Measurement 3 passes every command in the plan. FIX: gate Step 2 on zero remaining `NOT YET WRITTEN` outside `## Verdict`.

## B. Entry-point classes both families miss

Two found:

1. Bare native invocation. tools/check-drift.ps1:1060 (`Get-Content -Raw $briefPath | codex exec ...` \u2014 the live codex dispatch, item 31's site; CLAUDE.md's `:700` is stale) and tools/check-drift.ps1:500 (`&amp; codex exec --help`) match neither family: no Start-Process, no subprocess, no `-File` token. Yet the plan's own vocabulary promises `launch-nonhost` rows for exactly "python, git, codex, kimi" (plan line 240 / 400), and 5.1's native-argument quoting \u2014 Defect 2 \u2014 fires at precisely such call sites. The file is still caught via other lines, but the inventory rows the vocabulary exists for are unproducible.
2. Platform-default host. .github/workflows/skill-evals.yml:70-71 is a `run:` step on `windows-latest` with no `shell:` key; GitHub starts pwsh with no host token on any line. An entry point that names no host because the platform supplies one is textually invisible to both families.

## C. The sweep

Six instances of the class in the plan:

1. Plan line 95 "Copied verbatim" vs a 40-character-prefix oracle (line 156). The claim is wider than what its check measures.
2. Plan lines 537-540, run.py docstring: "Python's own argument passing is exact, so a corruption here would mean the probe is broken rather than the re-exec." Between Python's exact command line and `$args` sits powershell.exe's `-File` parsing \u2014 which the plan itself names as unisolated at lines 648-652. A genuine 5.1 `-File` finding would be recorded as "probe broken" per lines 634-636. Loud, but mislabeled.
3. Plan lines 417-418: docs/ "is entirely historical record." It is not \u2014 this plan, and every script Tasks 2, 4 and 7 execute, live under docs/. The green survey then attests "never executed" over executed files.
4. Plan lines 449-454: the "What this method cannot see" list reads as complete and omits the two classes in B, both live in the repo today. A blind-spot list that is itself incomplete reads exactly like a complete one \u2014 the item's own words at backlog 3584.
5. Plan line 767: "the 13 shipped scripts" \u2014 a count stated as fact ahead of its measurement, with a glob that misses hooks/superpowers-review-companion.ps1.
6. Plan lines 722-724: the record must "state plainly that PowerShell 7 is NOT preinstalled on Windows" \u2014 ordered written with no measurement or citation, in a plan whose own constraint (lines 37-40) calls a claim written from memory a violation. True as far as I know, but the class is the class.

Minor, not pressed: "N above 150" (plan line 350) is a predicted count, but a mismatch there is loud, not clean.

## D. Task 9 verdict logic

The MET/NOT-MET-with-citation structure and the reasoning-forces-CONDITIONAL rule (plan lines 1007-1009) are sound in shape. One hole: a YES is reachable while something material is unmeasured, through `migration=unknown` rows. Task 3 legitimizes `unknown` as the honest answer (plan lines 428-431), survey.py's main() never inspects migration values (plan lines 304-326 \u2014 only unclassified and stale gate), and Task 9 never mentions unknowns. So NO-criterion 1 ("any entry point that cannot be made to reach 7") can be answered NOT MET citing an inventory that contains rows whose migratability was never determined, and the CONDITIONAL rule fires only if the writer notices. FIX: Task 9 Step 2 should state that any `migration=unknown` row bearing on criterion 1 forces CONDITIONAL naming those rows. Plus the `NOT YET WRITTEN` gate from A.

## E. Ordering

None found. Task 4 correctly consumes nothing earlier; Task 5 consumes Task 3; Task 8 consumes Task 5's run ids; Task 9 consumes 3-8. No task depends on a later result.

## UNVERIFIED / also found

- probe-record.md:122-123 transcribes the S3 Esc function as `'(\*)"'` and `'(\+)$'` \u2014 escaped literal asterisk/plus, which escapes nothing in general. That cannot be the code that produced byte-exact S3. The plan's parent.ps1 (lines 510-511) carries the corrected `'(\\*)"'` form, so the plan is right and the committed record's snippet is a transcription defect. Anyone building the real item 51 fix from the record's snippet builds a non-escaping escaper.
- Whether GitHub's default shell on windows-latest is pwsh is stated from background knowledge, not from a file in this repo; the entry point itself (workflow line 70-71, `run:` with no `shell:`) is verified, only the identity of the default host is UNVERIFIED here.

The plan's architecture \u2014 NO-criteria frozen first, a survey that must fail before it may pass, honest-stop rules in every probe \u2014 is the right shape, and Tasks 4, 5, 7 and 8 execute it well. The named fixes are specific and cheap: the Task 6 glob, the two additions to the "cannot see" list, the docs/ prefix wording plus an exception for `&lt;REC&gt;` executables, the Task 9 unknown-rows and NOT-YET-WRITTEN gates, the Task 4 returncode column, and a citation or measurement behind the preinstall claim.

FIX
