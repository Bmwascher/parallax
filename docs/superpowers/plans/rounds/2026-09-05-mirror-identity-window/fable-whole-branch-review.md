# Fable whole-branch review, 2026-09-05

Seat: `parallax:fable-reviewer` (Claude, in-harness). Range
`0f485cca16487ff83eee7529787bd9bf3049c66c..31250b8c0cebd83ceceaa092aec35e3868633976`.
Diff package built by the controller at `C:\Temp\diffpkg\`, excluding the
plan-debate transcripts. No SDD ledger existed; the reviewer was told so
and treated it as a limit on its evidence.

Retained verbatim. Findings applied at `79ab77f`.

---

### Strengths

- **The advisory property holds in the shipped code, structurally.** The sidecar is read at exactly one place, `tools/new-review-mirror.ps1:1185`, after the `BLOCKED: the source status changed` line has already been printed and immediately before an unconditional `exit 1` at `:1186`. The whole explanation body is inside one `try`/`catch` (`:962-1029`), the file is read through one handle with the 64 MiB bound tested on that handle's `Length` (`:981-998`), the decoder is the throwing UTF-8 form inside the same `try` (`:989`), and the clean-verify path never opens the file at all (`test_a_clean_tree_verifies_with_no_source_manifest`, `evals/multi-model-verify/test_review_mirror.py`). No tool other than the mirror script names the sidecar (a repo-wide search for `source-manifest` outside `docs/` hits only `tools/new-review-mirror.ps1` and its test module), so nothing downstream can be steered by it. On the build side a write failure is reported as `source_manifest: unwritable` and never fatal (`:2218-2221`). I could not construct a state of the file, absent, malformed, oversized, or well-formed and hostile, that changes an exit code.
- **Refusal ordering deletes nothing.** The lexical sidecar guard sits with the override guard, before the path-budget preflight and before any mutation (`:1320-1354`); the alias walk (`:1636`), the followed-target check (`:1667`), and the extra-input collision guards (`:1683-1726`) all precede the attributes read, and the `Remove-Item` at `:1772` is the last statement before the mirror's own pre-existing `-Force` removal at `:1775`. The test `test_no_sidecar_is_removed_before_validation_completes` pins the exact failure the second draft had.
- **`Get-ManifestDrift` partitions the same strings the digest does.** Ordinal dictionaries (`:798-800`), last-space split so spaces in pathnames survive (`:821`), the 64-hex grammar checked rather than assumed (`:824`), and every unreadable record counted rather than dropped (`:819-826`). `Read-BoundedRecords` peeks before it reads (`:878-882`), so the cap bounds allocation and not just retention, and truncation is reported as its own state (`:994-998`).
- **Unit tests exercise the shipped function text.** `extract_ps_function` pulls `Get-SourceManifestSidecarPath` out of the real script (`test_review_mirror.py`, `extract_ps_function`), so the root and error classifications are tested against what runs, on both hosts, rather than against a copy.
- **The gate record is honest about item 93.** `gate-results.md:34-70` states the hypothesis it floated (item 90 closed the gap), then the three-row measurement that refutes it, and leaves the refuted guess standing labelled as such. `BACKLOG.md:3975` now says the cost is `NOT ESTABLISHED`. That is the right shape.
- **The item 97 widening is bounded correctly.** `_is_readable` (`evals/tools/backlog_lint.py:668-684`) separates "parsed" from "had items", and `test_unparseable_old_text_still_blocks_a_close` keeps the guard that makes an untouched backlog unable to satisfy the gate.

### Issues

#### Critical

None.

#### Important

1. **The record misdescribes what the shipped refusal prints for the R2 void.** `docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window/README.md:152-153` says that had the sidecar shipped, the refusal would have printed `content changed (2): CLAUDE.md, skills/multi-model-verify/SKILL.md`. It would not. Both files were tracked and clean at build time, so they were absent from the recorded manifest; after modification they enter `git status` and appear only in the live manifest, and `Get-ManifestDrift` classifies a key present live and absent recorded as `entered` (`tools/new-review-mirror.ps1:833-835`), not `changed`. The shipped output is `entered manifest coverage (2)`. The reference even carries the caveat this depends on ("Manifest coverage is not file existence", `skills/multi-model-verify/references/preflight-mirror.md:138-139`). The README is the artifact the diff debate and item 94 point at, so a reader would learn the wrong reading of the tool's own output from it. One-line fix.

2. **A fifth dispatched exchange exceeded the declared budget of four, and the record does not say who authorized it.** `README.md:7` declares the budget at 4; `README.md:280` records 4 of 4 used after R3; `README.md:371` records "Budget: 5 dispatched exchanges" after R4 with no authorization line. `references/debate-protocol.md:79-87` says exhaustion PAUSES for the user's authorization and that "a budget the USER controls is the bound a session cannot grant itself". The R2 pause at `README.md:172` is attributed to the user; the R4 resumption is not. If the user authorized it, one sentence closes this; if not, the counted R4 round was dispatched outside the declared bound and the record should say so.

#### Minor

3. **The escape rendering carries two backslashes, and the tests cannot see it.** `tools/new-review-mirror.ps1:926` builds the unit as `"\\u" + hex`. PowerShell strings do not treat backslash as an escape, so the emitted text is `\\u009b`, not `\u009b`. The Python oracles look for the substring `\u009b` (`test_review_mirror.py`, `test_display_controls_in_an_advisory_name_are_rendered`) and strip `\u0890` (`test_a_runtime_category_difference_is_escaped_on_both_hosts`), both of which are satisfied by the doubled form, so they pass either way. Cosmetic in the terminal, but it is the fourth backslash-doubling incident the README itself counts (`README.md:407-414`), this time in hand-written PowerShell rather than a generator.

4. **`Format-AdvisoryName` escapes every non-BMP character and its comment does not say so.** The loop iterates `ToCharArray()` (`:923`), so a supplementary character arrives as two UTF-16 units each classified `Surrogate` (`:919`) and both are escaped. A legitimate emoji or CJK Extension B filename renders as `\\ud83d\\ude00`. That is safe and consistent with the design, but the comment at `:888-908` describes a category test and never states that the escape set effectively includes all of planes 1 through 16. Say it, so the next reader does not "fix" it.

5. **The `CreateNew` comment claims more than was measured.** `:754-757` says a link substituted at the sidecar name "is not written through". For a link to an existing target, `CREATE_NEW` fails and the claim holds; for a DANGLING file symlink, `CreateFile` follows the reparse point and `CREATE_NEW` can create the target. The alias walk at `:1636` runs first and would refuse a reparse point it can see, but `README.md:366-367` records that a dangling file symlink was not measured for either the attributes read or the walk. The record is honest; the code comment is not qualified the same way. Low likelihood (file symlinks need privilege), but this is the one unmeasured case in which "it is not there" becomes a write.

6. **An orphaned sidecar now blocks a rebuild that used to work.** After a manual `Remove-Item` of a mirror directory, `mirror.source-manifest` survives beside it, and the next build without `-Force` refuses at `:1758-1762`. Recoverable from the message, and `-Force` already removes both, but nothing in `preflight-mirror.md` tells the operator the sidecar exists to be cleaned up with the mirror.

7. **The extra-input junction refusal is wider than the collision it exists for.** `:1718-1725` refuses ANY `-ExtraInput` reached through a directory link, whether or not its leaf could name the sidecar. The one shipped caller is the backup lane (`references/backup-lane.md:824`). A user whose declared inputs sit behind a junction gets a new exit 2 with a "pass the path behind the link" remedy. Acceptable, given the tool cannot decide identity, but it is a new refusal for a previously legitimate build and should be named in the release note.

8. **The plan-defect counts disagree across the record.** `README.md:374` is headed "Two plan defects found by RUNNING it" and lists three. `gate-results.md:89-90` calls `git add -A` "the fifth" and says "the other four are in README.md", where only three are; the Task 3 pin-class and Task 4 ranking defects live in the plan instead (`docs/superpowers/plans/2026-09-05-mirror-identity-window.md:1265`, `:1551`), which makes six by my count. Point at the list rather than computing a total about it.

9. **Two count-vs-body mismatches in `BACKLOG.md`.** Item 95's title says "Three stated properties" (`BACKLOG.md:4069`) and the body numbers five. Item 96's paragraph "Numbers 94 and 95 are RESERVED, not missing" (`BACKLOG.md:4139-4141`) is now stale in the same diff that files them. Both items carry a `Verified` digest over their own text, so an edit means re-digesting; ride, but they are the shape the memory rule warns about.

10. **The contract text says a test-cache write "is enough"; the record shows one that was not.** `preflight-mirror.md:102` lists "a test-cache write" among sufficient causes; `README.md:263-271` measured a pytest cache rewrite with byte-identical content that did NOT move the digest. The stated limit at `:108-110` covers a change reverted inside the round, not an identical-content write. Wording only, and the paragraph is pinned whole by `test_mirror_quiet_period_is_pinned`, so a fix is test-first.

11. **Test docstrings carry hard-coded script line numbers** (`:1554`, `:1258` in the Task 1 tests' docstrings). They are already off after this branch's insertions and will drift further. Ride.

### Ledger minors triage

There is no SDD ledger for this branch; the dispatcher stated the reason and I treat it as a fact about the evidence. The consequence is narrow: per-task completion criteria were checked against the commit list and the tests rather than a ledger, so I cannot say which task's implementer claimed what. In its place, the deferrals the record itself names:

- **Behavioural evals not run** (`gate-results.md:72-83`): ride, but it is not a free ride. `CLAUDE.md`'s own rule says skill/prompt changes trigger the suite and Task 3 changed skill text. The record calls it a deliberate gap and names it; the attestation must carry it forward as a gap.
- **Item 94's exposure unchanged**: ride by design (D1, spec `:65-68`).
- **Item 95's five stated-but-unheld properties**: ride, filed.
- **The link walker's unmeasured `Test-Path` premise** (`README.md:363-369`): ride, but it is filed nowhere; item 95 does not list it. Add it to a backlog item before the next cycle so it does not depend on this README being reread.
- **Dangling file symlink unmeasured**: ride; see Minor 5 for the comment that should be qualified to match.
- **Item 93's unexplained 18m42s**: ride, correctly reduced to "reproduce it or record it as a one-off".

### Assessment

Ready to merge: With fixes

The code answers all three adversarial questions the way the spec claims: nothing the sidecar holds can reach a verdict, no refusal deletes before it decides, and every untrusted string reaches the terminal through the renderer. The two Important findings are in the record, not the code, and each is a one-line correction; the remaining items are wording and cosmetic, with Minor 3 the one worth fixing while the module is open.

---

**Disposition by the session:** Important 1 and 2 corrected in the
README. Minor 3 fixed in code. Minor 4 and 5 addressed in comments.
Minor 8 and 9 corrected (totals removed; item 95 title made count-free
and the link-walker premise filed as its property 6; item 96 reservation
note put in the past tense). Minor 6, 7, 10, 11 ridden as the review
proposed; Minor 10's wording sits inside a pinned region and was not
edited.
