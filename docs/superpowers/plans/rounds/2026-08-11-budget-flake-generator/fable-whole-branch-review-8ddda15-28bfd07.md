# Fable whole-branch review — range `8ddda15..28bfd07`

**Retained verbatim, range-bound.** Seat: `agents/fable-reviewer.md`.
Dispatched 2026-08-11, before the 0.23.0 mode-diff debate, as the input
that debate is required to cite. Inputs given: the frozen plan
`docs/superpowers/plans/2026-08-11-budget-flake-generator.md`, this
directory of round records, and a 266735-byte `git diff 8ddda15..28bfd07`
package. There is NO SDD ledger this cycle — the session implemented the
plan directly.

The reply below is the reviewer's, unedited. The session's per-finding
adjudications follow it, and the round-1 debate brief cites this file.

---

## Reviewer reply (verbatim)

### Strengths

- **The encoding fix is measured, not asserted.** `evals/multi-model-verify/test_multi_model_verify.py:2768` onward (`TestBriefEncodingOverStdin`) runs both dispatch spellings against a real 5.1 child and compares the WHOLE hex payload, so an empty capture cannot pass; the failed `& { }` attempt is pinned as its own byte-exact case, and the restore-under-throw case proves the `finally` path. In `skills/multi-model-verify/SKILL.md:179-190` and `:240-252` the `throw` sits inside the `try`, so the `finally` restore is reachable on every path, including the override-hash failure.
- **The resume pin was replaced, not supplemented.** `test_multi_model_verify.py:483-499` swaps the regex to the `$brief | codex exec` form and adds negative assertions barring both live-proven defective forms. Exactly what the plan froze.
- **The route generator's oracle really is the frozen grammar.** I derived every `RULE_FORMS`/`FIELD_FORMS` expectation in `evals/multi-model-verify/test_route_parser_shapes.py` from the seven rules independently and found no case whose verdict needs the implementation to justify it. The two post-mutation-run additions (`dash-prefixed-text` at :102-110, mid-line key noise at :199-209) are recorded as coverage holes found by surviving mutants, which is the mechanism working as designed.
- **The ten route mutants are distinct and each has a hand-derivable killer** (e.g. `valid-plus-bare-label` kills 6 and 7 by different clauses; `fields-after-closing-rule` kills 5; `B[sandbox,absent]` kills 9). None is trivial.
- **The PowerShell matrix is the declared product.** `test_skill_report_shapes.py:131` builds 4x4x2x4x3x2 = 768, plus 12 entry cases; the 791 arithmetic checks out (780 + 1 fault-model + 3 fallback + 1 direct-guard + 5 mutants + 1 scope). The fail-open fault model is declared, test-only, and step one (fallback classifies correctly under the fault alone) stops the model from proving decoration.
- **Bands are mutually exclusive in code and in test.** `evals/tools/skill_lint.py:325-343` is `if/elif`; `test_skill_lint_budget.py` asserts `out.count("tokens") == 1` over the ceiling. The vendoring retraction states its scope honestly ("diff against the IMPORTED copy, not upstream's current HEAD").
- **All six relocation pins survive.** Four retargeted onto text preserved verbatim in `references/backup-lane.md:466-482`; `_norm` (`test_backup_lane.py:48-50`) joins the markdown wrap, so the wrapped literals hold. No contract region moved out from under a pin; `brief-encoding-transport` is whole in `model-prompting-notes.md:387-403`, pinned at `test_multi_model_verify.py`, and added to `DECLARED_REGIONS`.
- **The harness claim was narrowed correctly.** `run_behavioral_evals.py:540-556` now claims indivisible records plus announced loss, and the cap comment marks 1327 as one measured dispatch, not a maximum.

### Issues

#### Critical
None found on this range.

#### Important
1. **`tools/check-drift.ps1:700` still ships the form this branch declares defective.** `CLAUDE.md:79` (added by this branch) states "`Get-Content -Raw | codex exec` is the defective form", yet the drift autofix review dispatches exactly that form, and its brief (built at `check-drift.ps1:683-693`) embeds the drift report plus a `git diff main..HEAD`, which in this repo routinely carries em dashes. Worse than the SKILL.md path: this dispatch has NO brief-binding check, so corruption there is silent. The release carefully records the backup lane's `-p` path as unmeasured but records nothing about this third dispatch site. Either apply the guard (and run the drift state-machine suite) or record the residual; today the CLAUDE.md claim is wider than the repo state.
2. **Backlog close-out miscount, the exact class debate finding 27 fixed elsewhere.** `docs/superpowers/plans/2026-07-27-0150-backlog.md` (item 9, ~line 606) says "222 cases over the behavioural grader's `header_block` / `effective_route_ok`". The module generates 210 cases (sweep A: 6x5x2x2 + 2 = 122; sweep B: 72 + 4 + 12 = 88). 222 is the module's pytest test count (1 + 210 + 10 + 1). "Cases" and "tests" were conflated, the same shape the cycle corrected for the PowerShell module at round 10.
3. **Task 3's boundary pins were not implemented as frozen.** The plan says "Boundary pins, four of them: 5250, 5251, 5500, 5501" and round 12 repeats it. Grep shows those literals exist nowhere in `evals/` except as the constants themselves (`skill_lint.py:81-82`); `test_skill_lint_budget.py` tests band transitions relative to `BODY_TOKEN_BUDGET`/`BODY_TOKEN_CEILING`. A silent renumber of the constants trips no test, which is precisely the act the "do NOT rebase automatically" policy exists to make visible. One assertion pinning the two literal values closes it.
4. **A fail-first docstring claims more than its code does.** `test_skill_lint_budget.py:105-132` (`TestTheOldImplementationCouldNotFail`) says it is "run against the pre-change code itself", but the code reconstructs the vendored behaviour inline (`errors, warnings = [], []` then `if est > 5000: warnings.append(...)`); that half cannot fail for its claimed reason because `errors` is empty by construction. The second half (the shipped lint fails the oversized body) is real evidence. The first sentence is invariant-3's exact failure class, in the module that enforces item 19.

#### Minor
5. **`docs/.../rounds/2026-08-11-budget-flake-generator/finding-brief-encoding.md`** (lines ~15 and ~33) still carries the refuted "14 em dashes" count that debate point 16 corrected to 15, with no correction marker; the README cites this file as the write-up, and the contract region says 15.
6. Same file: recorded 13365 vs 13333 chars is +32, but 15 em dashes at +2 each is +30; nothing reconciles the delta.
7. **One oracle field is taken from the implementation, not the freeze.** `test_skill_report_shapes.py:163` sets `present = opens >= 1`; the five frozen invariants define ambiguity but never define `BlockPresent` for closer-only or multi-opener shapes. It matches production and is a reasonable reading, but it should be declared in the invariant list rather than inferred.
8. `commands/doctor.md:70` pipes through the same 5.1 boundary; safe today only because the payload is pure ASCII. Worth one line wherever finding 1 is recorded.
9. `test_route_parser_shapes.py:test_generated_shape` re-execs the full runner module once per case (~210 execs); cost only, correctness unaffected.

### Ledger minors triage
No SDD ledger exists this cycle (the session implemented the plan directly); there are no deferred minors to triage.

### What I could not verify
- That the mutation runs and the three fail-first tests were watched to fail at the recorded moments; a final diff cannot show order of operations, and the retained failing outputs the plan requires are not in the package.
- The claimed 791-green on both PowerShell hosts; no CI evidence is in the package.
- Task 8 (twelve live runs) and the version bump are absent from this range by design; the backlog honestly says `RESULT: pending`, so item 18 is open and the release is not complete at this head.

### Assessment
Ready to merge: **With fixes.** The code on the range is sound and unusually well evidenced; all four Important findings are record or test-pin corrections, cheap to land, and three of them are instances of the branch's own named failure class (claims wider than evidence, stale or conflated records). Item 18's closure still depends on the post-bump twelve-run measurement, which the range correctly leaves pending.

---

## Session adjudication, per finding

Every finding was checked against the live repo before it was adjudicated.
The evidence column says what THIS SESSION ran, not what the reviewer
reported.

| # | verdict | session evidence |
|---|---|---|
| 1 | **ESCALATE** | CONFIRMED at `tools/check-drift.ps1:700`, read directly. The scope rule (`debate-protocol.md:100-131`) does not resolve it either way on its own, so it goes to the debate rather than to my judgement. See below. |
| 2 | **ACCEPT — FIX** | CONFIRMED by running the module: `len(CASES)` is **210**; `pytest --collect-only` reports **222 tests**. The backlog sentence conflates them. |
| 3 | **ACCEPT — FIX** | CONFIRMED: `grep -rn "5250\|5251\|5500\|5501" evals/` returns ONLY `skill_lint.py:81-82`. No test pins the literals. |
| 4 | **ACCEPT — FIX** | CONFIRMED by reading `test_skill_lint_budget.py:105-132`. `errors` is `[]` by construction, so `assert not errors` cannot fail for the reason the docstring claims. |
| 5 | **ACCEPT — FIX** | CONFIRMED at `finding-brief-encoding.md:16`. Re-measured: the void brief holds **15** em dashes and **45** non-ASCII bytes, so 15 is the count and 14 is refuted twice over. |
| 6 | **ACCEPT — FIX, and the delta now reconciles** | Re-measured on the retained `plan-brief-r1.md`: UTF-8 chars **13333**, file bytes **13363**, non-ASCII bytes **45**, em dashes **15**, cp1252-decoded chars **13363**. The ANSI decode alone accounts for **+30** (15 dashes x 3 chars each). The remaining **+2** is the CRLF PowerShell appends when it pipes a string to a native command, which `TestBriefEncodingOverStdin` already declares as `EOL = "0d0a"`. Neither the reviewer's arithmetic nor mine was the published one: the write-up attributed the whole delta to the dashes. |
| 7 | **ACCEPT — FIX** | CONFIRMED at `test_skill_report_shapes.py:163`. `present = opens >= 1` is correct against production and is NOT derivable from the five frozen invariants. It is an undeclared oracle field, which is the one thing a generated suite may not have. |
| 8 | **ACCEPT — FIX (record)** | CONFIRMED at `commands/doctor.md:70`. Payload is a pure-ASCII literal today, so no corruption is reachable; it is a latent site and rides finding 1's record. |
| 9 | **ACCEPT — no action** | Correct and non-blocking. ~210 subprocess execs, cost only. Recorded so it is not rediscovered. |

## Finding 1, escalated: both positions

**The fact, not in dispute.** `tools/check-drift.ps1:700` dispatches
`Get-Content -Raw $briefPath | codex exec`, the exact form this branch
declares defective, and that dispatch has NO brief-attribution binding, so
corruption there is silent. One correction to the reviewer's mechanism: the
brief is written with `Set-Content` (5.1 default is ANSI) and read back with
`Get-Content -Raw` (ANSI), so the round trip is lossless for cp1252
characters. Only the PIPE degrades, giving ONE `?` per em dash rather than
three. The corruption is smaller than on the SKILL.md path and just as
silent.

**The case for FIXING it in this range.** The defect is live, the branch's
entire fourth work item is this exact defect, and the fix is the same three
lines already proven twice on both hosts. Certifying an encoding release
while shipping the defective form elsewhere in the same repo is the kind of
narrow attestation the scope rule was written to prevent.

**The case for RECORDING it as a named follow-up.** `debate-protocol.md`
requires BOTH halves: same named class AND on the verification surface
ENUMERATED BEFORE the finding. `tools/check-drift.ps1` was not on this
debate's enumerated surface, and CLAUDE.md requires
`evals/tools/drift_statemachine_tests.ps1` for any change to that file —
four scenarios that each re-run the full pytest suite in a disposable
worktree. That is an unbudgeted verification cost admitted after the answer
was already wanted, which is the second half of the rule failing.

**Session position.** RECORD, plus an explicitly narrowed claim: name the two
remaining unguarded dispatch sites (`check-drift.ps1:700`, and
`commands/doctor.md:70` as ASCII-only and therefore latent) in the finding
write-up and in CLAUDE.md, and open a backlog item. The rule forbids silence
about a known defect inside a certified unit; it does not require the fix to
land inside a range that never enumerated the file. Put to the reviewer for
adjudication rather than settled here.
