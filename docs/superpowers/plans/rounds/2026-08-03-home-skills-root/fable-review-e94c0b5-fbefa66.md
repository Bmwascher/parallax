# Fable whole-branch review — range `e94c0b5..fbefa66`

**Seat:** `agents/fable-reviewer.md`. **Branch:** `feat/home-skills-root-probe`.
**Scope:** Task 1 of six only, at the user's request. Tasks 2-6 are not
implemented and their absence was declared out of scope in the dispatch.
**Date:** 2026-08-03.

This is the raw reply, retained verbatim as a range-bound artifact. The diff
debate's round-1 brief cites this file.

---

### Strengths

- **D1 is the real thing.** The vacuous-assertion catch rests on the plan's own "fail for the named reason" rule (execution-deviations.md:40-45), the fix was re-watched to fail on the first staleness clause (execution-deviations.md:58-60), and the record states plainly that both reviewer lanes missed it, quoting the Kimi lane's false positive claim (execution-deviations.md:62-68). That is the honest shape a deviation record should have.
- **The `uncommented` helper is sound.** I checked it as hard as the original: `re` is imported at test_backup_lane.py:8, the regex strips only line-leading comment markers, and the final `" ".join(...).split()` re-normalization collapses the double spaces that `#\s?` (one optional space) would otherwise leave, so a wrapped, an inline, and an unevenly indented re-insertion of the retired sentence are all caught (test_backup_lane.py:1501-1515). I found no defect inside this repair.
- **The step slicing holds against the real workflow.** Verified against .github/workflows/skill-evals.yml:82-112: each `PARALLAX_PS_HOST:` marker sits inside its own step, the `"\n      - name:"` boundary matches the file's 6-space step indent, and comments naming the modules (lines 73-81) sit before the marker so they cannot contaminate a slice. The named perturbations fail closed: a reindent breaks the boundary match, the powershell slice then spans both steps and `count == 2` fails; a step inserted between the hosts shortens the slice at its own `- name:`; the pwsh slice runs to EOF today with nothing after it, and a future appended job would bound it at that job's first `- name:` step. The only false-pass path needs the module dropped from the pwsh step and re-appearing verbatim in job-level preamble text before the next job's first step, which is contrived.
- **The replacement headers claim exactly what is true.** Both modules carry `os.name != "nt"` skip guards (test_codex_context_probe.py:60-63, test_review_mirror.py:44-45), so "the ubuntu job skips them" is a fact, and the workflow runs both modules under both hosts (skill-evals.yml:86-96, 101-112). The headers understate the oracle if anything (it fires when a module leaves either step, not only both), which is the safe direction. The probe header matches the plan's frozen block verbatim.
- **D2's explanation is correct.** The hosts dict is insertion-ordered, powershell.exe is checked first, and M3 puts count 2 in the 5.1 step, so failing there first is the code doing what it says; the plan's prediction was the imprecise party.
- **The backlog closure is accurate and consistent.** Heading style matches siblings (`— DONE, 0.17.0`, cf. lines 182, 473 of the backlog), the Status list matches the actual open set, the retained `**Problem.**` paragraph is the plan's own instruction, and the resolution text does not trip the new oracle, which scans only the two module bodies.

### Issues

#### Critical

None.

#### Important

- **The deviation ledger is narrower than the diff, three times over, and D1 affirmatively claims otherwise.** The frozen plan reads the workflow through `_norm` (plan line 173); the shipped test reads it through `_read` (test_backup_lane.py:1520). This is not cosmetic: `_norm` is `" ".join(text.split())`, which destroys every newline, so the frozen boundary split `"\n      - name:"` could never match, both host slices would run to end of file, and the powershell.exe slice would contain both steps, failing `count == 1` against the CORRECT workflow. That is a second plan defect in the same test, repaired silently, in the exact branch where plan Step 2 orders STOP ("if it fails on the per-step slicing instead, STOP"). D1 says "the two staleness assertions were repointed at it. `_norm` is unchanged and no other pin is affected" (execution-deviations.md:47-49), which reads as a claim that nothing else changed. Two more unrecorded departures: test_review_mirror.py:31-34 was not replaced verbatim per plan Step 4 (the "Guarding only..." paragraph the plan deletes is retained, reworded at line 34, and the "See the probe suite's header" sentence is dropped from inside the frozen block); and the backlog carries a fourth paragraph, "One thing that oracle taught, worth keeping," beyond the plan's verbatim three-paragraph insert. All three deliveries are defensible on the merits, and the resulting text is accurate. The defect is that a zero-judgment implementer made three unadjudicable judgment calls: the diff debate adjudicates deviations "against the plan" from this ledger (execution-deviations.md:4-6), and it cannot adjudicate what the ledger does not carry. Fix is cheap: amend the ledger to record all three, especially the `_norm` to `_read` swap as a plan defect in its own right.

#### Minor

- **The "must name the job" clause is unwatched.** `assert "powershell-hosts" in body` (test_backup_lane.py:1533-1534) was never individually watched to fail; the three plan mutations cover the other clauses, and the initial failing run stopped at an earlier assert. By the plan's own Global Constraint an unwatched assertion is not yet evidence. One extra mutation (delete the job name from one header) closes it. This is a plan scope gap, not an implementer fault.
- **Gap, named per my brief:** the diff package carries commit subjects only, so I could not verify that the three commits' full messages carry no `Claude-Session:` trailer. The subjects are clean; the bodies need one `git log` check by someone with git access.

### Ledger minors triage

- **D1** - fix-before-merge, on the record only: the code repair is verified and rides, but the entry's "no other pin is affected" sentence must be amended to carry the `_norm` to `_read` swap (see the Important finding), or the debate adjudicates from a false completeness claim.
- **D2** - ride: prediction imprecision correctly diagnosed, the property under test (parity fires while the count stays 2) was demonstrated, and no code changed.
- **D3** - ride: contained before commit by the explicit-path staging rule, nothing entered the range, and recording it is itself the value; nothing in-range to fix.

### Assessment

Ready to merge: **With fixes.** The code shipped by Task 1 is correct, its oracle genuinely can fail every load-bearing way it claims, and the mutation evidence is sufficient for those clauses; but the deviation ledger the diff debate adjudicates from omits three departures from frozen text and one entry affirmatively denies them, so the record must be amended (and the commit-trailer gap closed) before the branch's own methodology is satisfied.

---

## Session adjudication of this review

Every finding was verified against the repo before acceptance.

- **The `_norm` to `_read` swap: CONFIRMED and accepted.** Measured directly: under `_norm`, `"\n" in norm` is `False` and `"\n      - name:" in norm` is `False`. The frozen form could not have worked, and Step 2's STOP branch is precisely the one it would have taken. Recorded as D4.
- **The mirror header not being verbatim: CONFIRMED and accepted.** Recorded as D5.
- **The backlog's fourth paragraph: CONFIRMED and accepted.** Recorded as D6.
- **The unwatched job-name clause: CONFIRMED and CLOSED.** Two further mutations run, one per module; each fails naming that clause. Recorded as D7.
- **The commit-trailer gap: CLOSED.** `git log e94c0b5..fbefa66 --format=%B` piped through a `Claude-Session` search returns 0 across all three full commit bodies.

Fable's Assessment stands as written at the moment it was issued. The fixes it named are applied in the commit that retains this artifact.
