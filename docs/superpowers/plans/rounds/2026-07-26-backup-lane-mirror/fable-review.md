# Fable whole-branch review — parallax 0.14.2 rider

Seat: `parallax:fable-reviewer` (installed cache 0.14.2), agent id
`a3cae90f94b7e8ae8`. Read-only (Read/Grep/Glob); no Bash grant, so the
four verification suites were run by the driver, not by the reviewer —
the reviewer names this gap itself in every pass.

RETENTION: untracked by design. Committing this artifact would move the
head it reviews mid-debate (the head-immobility rationale established by
the 0.14.0 cycle). Its SHA-256 is recorded in the mode-diff round-1
brief at dispatch time.

Range reviewed: `c73ca2f48a91bef2c42ed4ae92613fb09026ab0a..` — head
advanced across passes as findings were fixed:

| Pass | Head reviewed | Verdict |
|---|---|---|
| 1 — whole branch | `1a22597c6dfe67691c9f4331e1933617c6964fb4` | With fixes (0 Critical, 2 Important, 4 Minor) |
| 2 — fix confirmation | `00fdceb3d401a405aec5770bfa31ac1b6a5dbda5` | With fixes (Important 2 closed; Important 1 closed in substance, 1 introduced Important) |
| 3 — retiming confirmation | `8cfc27b8dc0cc604ba1554dcd1ff6017353be32c` | Ready to merge YES (wedge closed; 1 Minor — stale justification) |
| 4 — range binding | `5b976f7b8160fb153924562a265869a691972a16` | Ready to merge YES; range `c73ca2f..5b976f7` bound, nothing introduced |

There is no frozen plan for this rider: the work came from defects
observed during a live Sol+Kimi panel run in KitnEssentials on
2026-07-26 plus one 0.14.0 deferred finding, so no spec-fidelity
checking applies and the reviewer was told so explicitly.

## Driver adjudications (to be cited by the mode-diff round-1 brief)

Every finding below was verified against the repo before disposition;
none was accepted on authority.

| Finding | Disposition | Evidence |
|---|---|---|
| P1 Important 1 — mirror inherits the real tree's dirt; no baseline, so pre-existing untracked/modified files quarantine every round | ACCEPTED, fixed in `00fdceb` | Reproduced on this repo: `git status --porcelain` shows untracked `docs/superpowers/plans/rounds/2026-07-26-seat-reshuffle/fable-review.md`, which under the as-written rule would have quarantined every round |
| P1 Important 2 — `evals.json` backup-lane case still graded the superseded clone contract while declaring `backup-lane.md` in its surface | ACCEPTED, fixed in `00fdceb` | Read the case: expectation #4 said "throwaway clone … lists exactly KIMI-REVIEW-BRIEF.md"; `surface` does include `backup-lane.md`; `setup.manual = true`, so CI never ran it |
| P1 Minor 1 — "every round to date ran at provider default" overclaims a single present-day config read | ACCEPTED, hedged in `00fdceb` | The probe establishes only current state; earlier rounds' config is unobserved |
| P1 Minor 2 — output-encoding recovery resume's `-p` unspecified | ACCEPTED, specified in `00fdceb` | Resume syntax carries `-p "<rebuttal>"`; in recovery there is no rebuttal, but the flag must not be empty |
| P1 Minor 3 — a commit inside the mirror runs the real repo's hooks | ACCEPTED, clause added in `00fdceb` | The mirror preserves `.git`, hooks included |
| P1 Minor 4 — ASCII parentheticals pinned into tests against the file's em-dash convention | ACCEPTED, normalized in `00fdceb` | Pin and prose moved together |
| P2 Important (introduced by the P1 fix) — baseline captured "immediately after construction" contradicts preflight-3 remediation, which runs between construction and the brief and both deletes entries and can move HEAD | ACCEPTED, fixed in `8cfc27b` | Verified against own text: `SKILL.md` records identity fields after remediation; `backup-lane.md` captured the baseline before it. A remediated debate would fail porcelain equality on every round and pin a stale HEAD |
| P2 Minor — porcelain equality is path-level, not content-level | ACCEPTED, stated in `8cfc27b` | A file already in the baseline shows the same entry however its content changes; allowlist + write-probe remain the load-bearing controls |
| P2 — driver-added constraint (clean tracked tree required in mode diff, disclosure-only elsewhere) | ENDORSED by reviewer, retained | Mode diff reviews a committed range; a dirty-tracked mirror would have the reviewer citing content outside the range while the record pins the range's HEAD |
| P3 Minor — SKILL.md justified the tracked-case commit by the containment rule, which the post-remediation baseline now absorbs; instruction correct, reason stale | ACCEPTED, fixed in `5b976f7` | Verified: with the baseline captured after remediation, an uncommitted ` D` is absorbed and the per-round check never sees it. The commit is forced instead by the tracked-modification-in-baseline consequence (bars mode diff, breaks HEAD-identifies-content) |

Nothing was refuted and nothing escalated: every finding across all four
passes was verified true against the repo before disposition.

Pattern worth recording for the diff debate: three of the four passes
found a defect that the IMMEDIATELY PRECEDING fix introduced (P1 fix →
retiming wedge; retiming fix → stale justification). Findings were
individually sound each time, but the branch's fix-introduces-defect
rate is the reason the range was re-bound at the final head rather than
asserted from the pass-1 verdict.

---

## Pass 1 — whole branch at `1a22597` (raw reply, verbatim)

### Strengths

- The clone→mirror fix is evidence-grounded and mechanically locked. The failure mode is named concretely in the contract (backup-lane.md:116-124: "a clone carries TRACKED FILES ONLY", with the KitnEssentials probe and the exact gitignored paths), and test_backup_lane.py:98-118 pins that rationale so it cannot silently regress to a clone.
- The porcelain check stayed exact through the rename, not weaker: backup-lane.md:135 requires "exactly the expected untracked set … and nothing else", the set must be "enumerated before the round", and fallbacks.md's integrity class was updated in the same stroke ("a mirror delta beyond the expected untracked set", pinned at test_backup_lane.py:191-192). The old "brief and nothing else" pin was replaced, not deleted.
- The output-encoding class respects the project's own architecture rules: the class lives only in fallbacks.md; backup-lane.md carries the environment guard and still declares "this file defines none of its own" (backup-lane.md:141-145). The disposition reasoning is correct — deterministic re-encode failure, nothing reached disk so nothing is tainted, recovery via resume "with all four flags re-pinned" is consistent with the resume rule at backup-lane.md:35-37.
- UNVERIFIED marking is honest and itself test-pinned: which UTF-8 variable is load-bearing (backup-lane.md:28-30, pinned at test_backup_lane.py:173-175) and the populated-source `merge_all_available_skills` case (backup-lane.md:99-102, pinned at test_backup_lane.py:142-144).
- Placeholder discipline holds in the new config-sweep section (`<canonical-backup-model-id>` at backup-lane.md:81); the pre-existing `BACKUP_ID not in body` assertion (test_backup_lane.py:87) still covers the whole file. Grep confirms the backup model literal appears nowhere outside model-prompting-notes.md.
- The SKILL.md preflight-3 remediation branch is git-accurate: a tracked entry's working-tree deletion does show as ` D` in porcelain, and an ignored/untracked entry's deletion produces no porcelain entry, no commitable change, and an unchanged HEAD — "nothing to commit … is the CORRECT observation" (SKILL.md:85-92) is right, and the tracked case correctly requires a commit so the mirror's containment check comes back clean.
- The 903d602 markers are pure two-line prepends (bodies byte-preserved per the diff) and their content matches the ledger record exactly — same lane-of-record naming (smoke-sol2-r1/r2), same session id 019f9fd0-e19c-7b83-8502-820869ab359d, same deferral rationale.

### Issues

#### Critical
None.

#### Important

1. **The mirror inherits the real tree's dirt, and the containment rule has no baseline provision — the lane self-quarantines on any ordinary working tree.** backup-lane.md:116 defines the mirror as "a FILE COPY of the working tree", and backup-lane.md:135 quarantines any porcelain entry beyond "the brief plus any review inputs copied in". The old clone guaranteed a baseline-clean porcelain; a file copy does not: pre-existing untracked files (this very repo currently has untracked `docs/superpowers/plans/rounds/2026-07-26-seat-reshuffle/fable-review.md`) and any uncommitted tracked modifications ride into the mirror and appear in every round's porcelain, quarantining rounds the reviewer never touched. The declared-set wording cannot absorb them — tracked modifications can never be in an "untracked set", and pre-existing untracked files are neither the brief nor "copied in". The failure direction is safe (false quarantine), but the practical pressure is exactly the loophole risk: a driver will be forced to stretch "expected set" ad hoc. Relatedly, backup-lane.md:136 records `git rev-parse HEAD` as the mirror's identity, but unlike a clone, the copied tree's content is no longer guaranteed to equal that HEAD. Fix: either require/verify a baseline (record the mirror's porcelain immediately after construction, before the brief is written, and quarantine on deltas from that baseline plus the declared set) or require the mirror be taken from a tree whose porcelain is clean apart from enumerated entries — and say which one identifies the reviewed content.

2. **Stale consumer: the backup-lane behavioral eval still grades the superseded contract.** evals\multi-model-verify\evals.json:104 — expectation for `backup-lane-consented-substitution`: "the review runs in a throwaway clone whose post-round git status lists exactly KIMI-REVIEW-BRIEF.md". Both the workspace model ("clone") and the containment rule ("exactly KIMI-REVIEW-BRIEF.md") now contradict backup-lane.md:116/135, and the case's declared `surface` includes backup-lane.md, so the mismatch is on this change's own surface. The case is manual (`"setup": {"manual": true}`), so nothing fails in CI — which is precisely why it will bite later: a future manual run grades correct mirror behavior as a violation. The repo's own sweep rule (every consumer of a changed contract, grep not spot-check) was not met here. One-line fix. All other "clone" hits are correct usage: the intake.md pins at test_multi_model_verify.py:1681/1696-1697 concern cloning an external reference repo (a genuinely different clone), and drift_statemachine_tests.ps1 builds its own test harness clone.

#### Minor

1. **Overclaim beyond the probe:** backup-lane.md:87-88 concludes "every round to date ran at provider default" from a single 2026-07-26 read of the current config. The probe supports "the pin is not set now"; it cannot establish the config state during earlier rounds. One hedge word fixes it — everything else in the section stays inside its evidence.
2. **The output-encoding recovery prompt is unspecified.** fallbacks.md's new class says recovery is "a RESUME of the surviving session", but the pinned resume syntax carries `-p "<rebuttal>"` (backup-lane.md:36) — in recovery there is no rebuttal; the driver needs to ask the session to re-emit its lost reply. Neither file says so.
3. **Tracked-case remediation commits run the copied repo's hooks.** The mirror preserves `.git` including hooks; SKILL.md:87-88's "commit the removal inside the mirror" will execute a project's pre-commit hook inside the scratchpad (this project family installs them). Worth a clause; at worst the commit fails loudly.
4. **Style drift pinned into the tests:** backup-lane.md:135 uses ASCII ` - ` parentheticals where the file's convention is em-dashes, and test_backup_lane.py:115-117 pins the ASCII form — a later style normalization now costs test churn. Same commit also leaves SKILL.md with irregular wrapping (the long inserted lines and the dangling "Files above the repo's git root are" continuation at SKILL.md:94). Cosmetic.

Named gap: no Bash grant, so the four verification suites (skill_lint, scanner, trigger evals, pytest) were not executed here; the new test assertions were verified by reading them against the changed docs, not by running them. The dispatching session should confirm a green run on this head.

### Ledger minors triage

The 0.14.0 seat-reshuffle ledger leaves exactly one item outstanding — "Riding to 0.14.1: marker-prepend on smoke-sol-clean-brief/reply (third-review Minor 1)", which 0.14.1 shipped without. **Discharged in-range** by 903d602: both markers present as prepends, content cross-checked against the ledger's panel-record-final entry (lane of record, session id, retention rationale all match), bodies untouched. The ledger's closing entry ("Nothing further rides from the seat-reshuffle cycle") is accurate. The 0.15.0 backlog items (#53-#55, models-cache drift watch) are backlog, not deferred minors — no triage owed here.

### Assessment

Ready to merge: **With fixes** — Important 1 (define the mirror's porcelain baseline, or require a clean source tree, so the containment rule is satisfiable on ordinary working trees) and Important 2 (update evals.json:104 to the mirror/declared-set contract) before merge; both are small, neither disturbs the design. The change itself is well-motivated, honestly evidenced, and correctly test-locked; the two gaps are consumers/preconditions the rename missed, not flaws in the mirror model.

---

## Pass 2 — fix confirmation at `00fdceb` (raw reply, verbatim)

Fix package read. Verdict within the requested scope — the two Importants, plus what the fixes introduced.

### Important findings — closed?

**Important 2 (stale eval expectation): CLOSED.** evals.json expectation #4 now states the mirror/baseline contract exactly ("review MIRROR (file copy preserving .git, not a clone)… baseline porcelain… equals that baseline plus exactly KIMI-REVIEW-BRIEF.md and any enumerated copied-in review inputs"), consistent with backup-lane.md's rewritten per-round rule. The new `test_backup_lane_eval_case_matches_the_mirror_contract` pins the case's expectations by id, verifies backup-lane.md is in its declared surface, and forbids "throwaway clone" — the two documents can no longer drift apart silently. Nothing weaker than claimed.

**Important 1 (baseline): CLOSED in substance — the baseline is the right mechanism, both halves declared in advance, so the check stays exact rather than adjudicated after the fact — but the fix introduces one ordering wedge that re-opens the false-quarantine in exactly the remediation path:**

- **Introduced, Important (one-line fix): baseline capture timing contradicts preflight-3 remediation.** backup-lane.md now says the baseline is captured "immediately after construction and BEFORE the brief is written" (new BASELINE bullet), while SKILL.md's remediation sequence is construction → delete/commit the back-channel entries in the mirror → "the mirror's identity fields go in the debate record". Remediation happens between construction and the brief and it changes porcelain and possibly HEAD: the offending entry was in the construction-time baseline (`??`, or ` D` then committed), and after remediation it is gone. A driver who follows backup-lane.md's letter — baseline immediately after construction — then fails "porcelain equals BASELINE plus the declared set" on every round of a remediated debate, and in the tracked case records a pre-remediation HEAD that no longer matches the mirror. SKILL.md's ordering (identity fields recorded after remediation) is the correct one; backup-lane.md's baseline bullet should say "after construction and any preflight-3 remediation, immediately before the brief is written". This only bites when preflight 3 fired, but that is precisely the documented procedure the mirror exists to support.
- **Residual, Minor (state it, don't redesign): the porcelain-equality check is path-level, not content-level.** A file that is already `?? ` or ` M` in the baseline shows an identical porcelain entry after a round even if its content changed, so baseline-dirty files become porcelain-invisible write surfaces. This blindness is pre-existing in kind (the old "lists exactly the brief file" rule was equally blind to content changes in the brief itself), and the contract already names the tool allowlist plus write-probe as the load-bearing control — but a one-sentence acknowledgment in the BASELINE bullet would keep the check's claims honest about what it does and does not see.

On the constraint you added without my asking: the line is drawn correctly. Mode diff reviews a committed range, so requiring clean tracked files there (rather than disclosure) is right — a dirty-tracked mirror in mode diff would have the reviewer citing content outside the range while the record pins the range's HEAD. Disclosure-only for the other modes is proportionate, since their subject is the current state, not a committed range.

### Minors and gap

All four minor fixes verified against the package and consistent: the probe hedge now claims only what a present-day read supports ("treat any round without its own contemporaneous config evidence as provider-default" is a clean formulation); the recovery `-p` is specified and test-pinned ("re-emit its previous reply verbatim" — note it honestly treats the re-emission as the round's reply, which is the only recoverable evidence, acceptable); the hooks clause lands with the right disposition ("mirror-construction problem, never a finding"); em-dash normalization matches the updated pin. The suites-green report (170 passed / 1 skipped) is yours, not independently executed by me — same no-Bash gap as before, now covered by your run.

### Assessment

Ready to merge: **With fixes** — Important 2 fully closed; Important 1 closed except for the introduced baseline-vs-remediation ordering wedge in `C:\Users\Brandon\Documents\parallax\skills\multi-model-verify\references\backup-lane.md` (BASELINE bullet), which needs the one-line retiming ("after construction and any preflight-3 remediation, before the brief") plus the matching test-pin update, since the current pin (`"BASELINE, captured immediately after construction and BEFORE the brief is written"`) locks the wrong wording in place. The path-level-blindness sentence is optional polish. Nothing else introduced by the fix commit.

---

## Pass 3 — retiming confirmation at `8cfc27b` (raw reply, verbatim)

### Wedge closed?

**Yes.** backup-lane.md:138 now reads "BASELINE, captured after construction AND after any preflight-3 remediation, immediately before the brief is written", with the load-bearing reason stated in-line (backup-lane.md:144-147: remediation deletes entries and in the tracked case commits, so an earlier baseline fails every round and pins a HEAD the mirror no longer has). The test pin moved with the wording — the stale pin is gone, and the new assertions in `test_mirror_baseline_closes_the_dirty_tree_hole` match the retimed text verbatim, including the reason clause, so the ordering cannot be silently reshuffled without failing the pin.

### Ordering agreement end to end

Verified across both files. SKILL.md's sequence (SKILL.md:75-95) is: build mirror → delete entries → re-run enumeration → "the mirror's identity fields go in the debate record" — identity capture after remediation, and SKILL.md:76-77 defers construction, baseline, and identity fields to backup-lane.md rather than stating its own timing. backup-lane.md's sequence is now: construction → remediation → baseline + identity → brief → write-probe → rounds. No step in either file contradicts another. The write-probe ("mirror status delta empty", backup-lane.md:70) is self-relative — a before/after delta around the probe — so it carries no baseline-timing assumption. Copied-in review inputs are timing-safe either way: whether copied before or after baseline capture, "BASELINE plus exactly the expected untracked set" holds as a union.

### Residual construction-time-baseline assumptions

Grep for baseline language across the skill surface and evals.json found none. evals.json:104 says "baseline porcelain was captured before the brief was written" — still true under the retiming and silent on remediation, so no contradiction. model-prompting-notes.md:146's "baseline" is unrelated prose.

### Third-order check — one Minor found, nothing blocking

The retiming makes one pre-existing SKILL.md justification stale, though the instruction it justifies remains correct:

- **Minor — SKILL.md:85-87:** the tracked-case rationale still reads "shows as ` D` in `git status --porcelain`, **which violates the mirror's containment rule**, so commit the removal". Under the retimed contract that clause is no longer literally true: the baseline is captured after remediation, so an uncommitted ` D` would be absorbed into the baseline, not flagged by the per-round check. The commit is still the right instruction — the real reason is now backup-lane.md:157-161: an uncommitted ` D` is a TRACKED modification in the baseline, which bars mode diff and breaks HEAD-identifies-content — but a driver who notices the baseline would absorb the ` D` could conclude the commit is optional. One clause fixes it (justify the commit by the tracked-modifications-in-baseline consequence rather than the containment rule). Non-blocking: the imperative "so commit the removal" is unconditional, and skipping it trips the disclosure/mode-diff constraint rather than opening a hole.

Other third-order candidates checked and clean: identity-field timing (HEAD and baseline captured together post-remediation, consistent between SKILL.md:80-81 and backup-lane.md:156-158), the PATH-level honesty bullet (backup-lane.md:149-154 claims exactly what the check does, names the allowlist and write-probe as the load-bearing controls — matches the existing Containment section's own framing), and the eval expectation (still accurate, already pinned against drift).

### Assessment

Ready to merge: **Yes** — the wedge is closed, both files agree on ordering end to end, no contract text still assumes a construction-time baseline, and the only thing the retiming surfaced is the one-clause stale justification at `SKILL.md:86`, which is polish, not a defect in the mechanism. Suite results (170 passed / 1 skipped, lint/scanner/trigger clean) remain yours to attest — same standing no-Bash gap as the prior passes.

---

## Pass 4 — range binding at `5b976f7` (raw reply, verbatim)

### Pass-3 Minor: closed, nothing introduced

Verified against the package and one repo check:

- **The clause is the prescribed one and it is accurate.** SKILL.md now justifies the tracked-case commit by the real consequence — an uncommitted ` D` is a tracked modification sitting in the post-remediation baseline, which bars mode diff and breaks HEAD-identifies-content, with the cross-reference to references/backup-lane.md where that rule lives. It even corrects the old rationale explicitly ("the per-round check is not what forces the issue"), which removes the exact misreading I flagged: a driver can no longer conclude the commit is optional because the baseline would absorb the ` D`. The imperative ("so commit the removal inside the mirror") is unchanged and unconditional.
- **The pin survives and still bites.** The pinned substring in `test_skill_preflight_names_the_remediation` ends at `` `git status --porcelain` `` — the edit changed only the punctuation after it (comma to em-dash), so the pin still matches, and the second pin (`nothing to commit` alongside an unchanged HEAD) is untouched.
- **No dangling references to the removed justification.** Grep across skills/ and evals/ for "violates the mirror" and "containment rule" returns only two unrelated comments (test_multi_model_verify.py:1793, an env-var containment comment in the drift-test block; test_backup_lane.py:131, a comment about the declared set). Neither is a pin and neither cites the deleted clause.
- The edit touches one sentence in one file; nothing else in the contract surface consumed the old wording, so there is no consumer to drift.

### Range verdict

**The whole range c73ca2f..5b976f7 carries my verdict: Ready to merge, Yes.** Plainly: both Important findings are closed (baseline mechanism + eval-case pin), the fix-introduced retiming wedge is closed with the ordering now agreeing end to end across SKILL.md and backup-lane.md, all accepted Minors are applied, and this final commit closes the last one without introducing anything. The ledger's sole deferred item was discharged in-range (903d602). Standing caveat, unchanged across all four passes: the suite results (pytest 170 passed / 1 skipped, skill_lint strict, scanner, trigger evals) are yours to attest — I verified every new assertion by reading it against the contract text, not by execution.

Bind this range. The artifact of record for the cross-vendor round is my pass-1 whole-branch report plus the three fix-pass verdicts above, over c73ca2f48a91bef2c42ed4ae92613fb09026ab0a..5b976f7b8160fb153924562a265869a691972a16.
