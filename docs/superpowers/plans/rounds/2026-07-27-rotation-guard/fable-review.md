# Fable whole-branch review — parallax 0.14.3

Range: `b040079..63fa715` (branch `fix/log-rotation-guard`)
Seat: `agents/fable-reviewer.md` (fresh subagent, read-only: Read/Grep/Glob)
Dispatched: 2026-07-27
Verdict: **Ready to merge — With fixes**

Raw reply retained verbatim below.

---

### Strengths

- The rotation-guard failure analysis is sound and unusually honest. The detection condition (file smaller than the captured offset, or absent — skills/multi-model-verify/references/backup-lane.md:54-55) is the correct cheap test for a rotated append stream; the explicit prohibition on the tempting recovery ("not a reason to re-read from zero", backup-lane.md:58) names the exact wrong move a driver would otherwise make, with the correct reason (a fresh file's opening lines attribute nothing, backup-lane.md:59-60). The residual-gap paragraph (backup-lane.md:64-70) admits the check is necessary-not-sufficient, and its reasoning is correct: a replacement file can only regrow past the captured offset within one call if the captured offset was small, which only follows an immediately preceding rotation — so declining a second mechanism today while naming the escalation trigger (file identity via creation time) is a defensible engineering call, stated rather than hidden.
- The observed evidence is dated and versioned (2026-07-26, kimi-cli 1.49.0, WinError 32, backup-lane.md:60-62), matching this repo's probe conventions, and "offsets have held by accident rather than by design" (backup-lane.md:63) is exactly the right framing for why the guard exists before the failure has ever fired.
- The item-(2) disposition is correct on the merits. The sweep's stated purpose — placeholder discipline on dispatch surfaces (evals/multi-model-verify/test_backup_lane.py:445-452) — genuinely does not cover docs/: I verified the literal appears in 20 files under docs/, including 48 matching lines in a single retained transcript (docs/superpowers/plans/rounds/2026-07-26-backup-lane-mirror/sol-diff-r1-transcript.txt), which is retained round evidence that must quote the id. Sweeping docs would mean either perpetual red or per-file allowlist churn; the "predictable response to a perpetually red test is to weaken it" argument is right.
- The comment's second factual claim checks out: docs/superpowers/plans/2026-07-25-kimi-backup-lane.md:17 does claim the literal appears ONLY in notes.md and the test file, and that is false of docs/ (the plan file itself contains the literal 4 times). Leaving the historical plan unedited and correcting the record at the enforcement site is the right pattern.
- Three of the four new pins use the wrap-tolerant `_norm` read and lock genuinely operative text: the detection clause (test_backup_lane.py:141-142) and the re-read-from-zero prohibition (test_backup_lane.py:145) are the two halves a careless edit would most plausibly delete. The tests-first shape holds: all four assertions fail against the pre-branch backup-lane.md.
- Version bump to 0.14.3 is present and correct (.claude-plugin/plugin.json:3).

### Issues

#### Critical

None.

#### Important

1. **The rotation guard's DISPOSITION is unpinned — the exact 0.14.2 pin-integrity class, instance ten.** The sentence "That is a route-attribution failure" (backup-lane.md:57) is the load-bearing consequence half of the new contract: it is what routes a detected rotation to no-retry / DISCARDED unread / consent gate via fallbacks.md:152-153. None of the four new pins (test_backup_lane.py:140-146) contains it, and the nearby "DISCARDED unread" pin (test_backup_lane.py:133) is satisfied by the pre-existing bullet at backup-lane.md:51, so deleting the disposition sentence leaves every pin green while a driver who detects a rotation has detection, a prohibition, and **no defined action** — precisely the "driver has to invent a rule" gap that 0.14.2 closed nine times in this same file (cf. the comment at test_backup_lane.py:221-227). Pin the disposition sentence.

#### Minor

2. **The "~40 occurrences today" count is wrong; actual is 92 matching lines across 20 files under docs/** (test_backup_lane.py:449 and the duplicate comment in the doc-facing copy at diff lines; verified by direct count). The figure appears to have been measured excluding the largest single file (92 − 48 = 44 ≈ 40). In a comment whose sole purpose is to be an accurate record that prevents re-litigation, opening with an off-by-2.3x number invites exactly the re-litigation it exists to stop. The conclusion is unaffected (the argument holds at any count ≥ 1), but the number should be corrected or made an order-of-magnitude claim.
3. **Routing rotation to route-attribution silently falsifies that class's stated rationale.** fallbacks.md:152-153 justifies the class's no-retry with "nothing transient" — true of a wrong id, wrong agent path, or extra tool, none of which fix themselves. A rotation-under-call IS transient: a re-dispatch with a freshly captured offset would produce clean evidence. Discarding the unattributable reply is right, and the consent gate keeps the path fail-closed, so the disposition is safe — but neither backup-lane.md nor fallbacks.md acknowledges that this member breaks the class's "nothing transient" premise, and a future reader reconciling the two files will find a contradiction with no recorded reasoning. One sentence in either file (the disposition is chosen for attribution loss, not non-transience) closes it.
4. **The residual-gap paragraph is entirely unpinned.** The necessary-not-sufficient admission and the contingent instruction "if rotation ever starts succeeding here, compare file identity (creation time) too" (backup-lane.md:64-70) can be deleted with all pins green. Lower stakes than issue 1 — it is a caveat plus a contingency, not a live rule while rotation still fails — but it is the only recorded escalation path for the day the accident stops holding.
5. The controller diff package I received (docs/superpowers/plans/rounds/2026-07-27-rotation-guard/diff-package.txt) contained the full diff only — no commit list or stat — so commit-level tests-first ordering within the range is unverified from the package. Named as a gap, not a finding; the pins do fail against the base text, which is the substantive half of the rule.

### Ledger minors triage

No SDD ledger exists in this repo; the two handed-forward 0.14.2 panel items serve in its place.

- **Item (1) rotation guard:** fix-before-merge is already done in substance; the remaining fix is pinning its disposition sentence (Issue 1) — that is the fix-before-merge item this review adds.
- **Item (2) docs sweep scope:** ride the NO decision — it is correct and well-argued — but fix the ~40 count before merge (Issue 2); it is a one-token edit in a comment whose only job is factual accuracy.

### Assessment

Ready to merge: **With fixes.** The contract text itself is correct, honest about its residual gap, and consistent in effect with fallbacks.md; but the guard's consequence sentence is unpinned (Issue 1), which reproduces the exact pin-integrity defect class this file accumulated nine instances of in 0.14.2, and the scope comment ships a wrong count in its first factual claim (Issue 2). Both fixes are small and mechanical; nothing found challenges the design.

---

## Session adjudication (before panel round 1)

| finding | adjudication | evidence |
|---|---|---|
| F1 | **ACCEPTED** — pin added | Verified: the only `route-attribution failure` occurrence anywhere in `evals/` is a COMMENT at test_backup_lane.py:125, so the sentence was deletable with every pin green. |
| F2 | **ACCEPTED, CONVERGENT** — already fixed at `0600be1` | The session found and corrected this independently before the review returned; both counts agree at 92 across 20 files. Counted once. |
| F3 | **ACCEPTED** — rationale sentence added to `fallbacks.md` | fallbacks.md's no-retry rationale reads "nothing transient"; a rotation-under-call is transient. Placed in fallbacks.md rather than backup-lane.md because backup-lane.md is barred from defining failure classes (backup-lane.md:255-256). |
| F4 | **ACCEPTED IN PART** — contingency pinned, caveat prose left unpinned | The escalation instruction is the operative half. Pinning narrative that is neither rule nor consequence makes the suite brittle without protecting a contract. |
| F5 | **ACCEPTED** — package regenerated with commit list and diffstat | |

Application governed by checkpoint
`.git/parallax/application-checkpoints/20260727-055732-63fa7156b63c.md`
(plus Amendment 1).
