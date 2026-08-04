## Claim 1 — accepted diagnoses and proposed repairs

### 1a

The diagnosis is correct, but the proposed replacement remains causal beyond the evidence. The earlier record called the deny list only a “plausible mechanism”; its two arms were merely indistinguishable, with no invocation capable of separating non-discovery from denial (`docs/superpowers/plans/rounds/2026-07-31-kimi-code-swap/probe-record-2.md:180-200`). “`Skill` was denied, so it could not observe the flag” still attributes the failure to observe to the deny list.

Use:

> That 2026-07-31 comparison was CONFOUNDED: `Skill` was denied in both arms, so the comparison did not isolate the flag.

The corresponding literal pin must change with it (`evals/multi-model-verify/test_multi_model_verify.py:194-217`).

**1a — FIX: replace causal “could not observe” with non-causal “did not isolate.”**

### 1b

The diagnosis is correct, but the proposed replacement still says “its suppression of the other roots was measured,” plural. Only `~/.agents/skills/` was measured; neither project root nor a populated flag target was exercised (`docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:277-291`).

Use:

> exclusion rests on the client's own help text, which says the flag's target is used instead of auto-discovered directories — text evidence, never a measurement — and on preflight-3 remediation clearing the project roots in the mirror regardless. No cell passed the flag against a POPULATED target, so what the flag does to its own target is unmeasured; suppression was measured only for `~/.agents/skills/`, with that target EMPTY, and that measurement holds only while `<debate-home>/skills/` stays empty:

The region pin must move identically (`evals/multi-model-verify/test_backup_lane.py:868-888`).

**Claim 1 — FIX: both diagnoses stand, but neither proposed replacement is yet the narrowest supported wording.**

## Claim 2 — these are the last claim-width defects

A further instance remains in the probe record: “Cell C is identical in every respect except that `--skills-dir` was passed” (`docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:152-153`). The same record says every cell used its own throwaway home (`docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:55-63`), and the frozen procedure explicitly gives every fresh cell its own home (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:492-497`). Therefore the flag was the intended variable, not literally the only difference.

Replace it with:

> Cells C and D held the declared model, effort, workspace, agent, prompt, nonce, and canary state constant, but used separate freshly built debate homes; the flag was the intended differing variable.

This narrows the record without reopening the settled probe design or verdict.

**Claim 2 — FIX: at least one additional claim-wider-than-evidence instance remains.**

## Claim 3 — builder postcondition and seams

The postcondition itself is sound:

- It enumerates with `-Force -ErrorAction Stop`, converts enumeration failure into a throw, and throws on any entry (`tools/new-kimi-lane-home.ps1:918-947`).
- Custody JSON is emitted only afterward (`tools/new-kimi-lane-home.ps1:949-968`).
- The outer catch deletes the created home and rethrows; the finally releases the acquired lock while `$buildCompleted` remains false (`tools/new-kimi-lane-home.ps1:978-1015`).
- Exit code 1 was measured and recorded (`docs/superpowers/plans/rounds/2026-08-03-home-skills-root/execution-deviations.md:724-735`).

The absolute seam claim is false. Any process—including production use—inheriting either nonempty environment variable triggers the seam; there is no test-only guard (`tools/new-kimi-lane-home.ps1:923-932`). Both paths then necessarily produce a nonempty enumeration and abort, so they cannot manufacture success (`tools/new-kimi-lane-home.ps1:937-947`).

The documentation also incorrectly calls `New-Item` the repository’s only write site despite the two immediately following `Set-Content` sites (`CLAUDE.md:84-89`; `tools/new-kimi-lane-home.ps1:904-930`).

Fix the claim and documentation to say:

> No shipped caller sets these variables. If externally set, the two env-gated seams seed an entry and deliberately force the build to fail; they can never change a failed build into success.

**Claim 3 — FIX: implementation passes, but “cannot fire in production use” and “only write site” must be narrowed.**

## Claim 4 — contract-region pin integrity

Both regions are genuinely locked:

- The required rule is a complete positive membership clause using one folded literal in an assertion capable of escaping to the runner (`CLAUDE.md:91-123`).
- `home-skill-root-disposition` sits whole in one direct `assert ("…") in body` (`evals/multi-model-verify/test_backup_lane.py:855-867`).
- `home-skill-root-disposition-limit` likewise sits whole in one direct membership assertion (`evals/multi-model-verify/test_backup_lane.py:868-888`).
- Those assertions are ordinary statements in an undecorated test function, not inside a catching construct (`evals/multi-model-verify/test_backup_lane.py:776-788`).
- Both identifiers are declared (`evals/multi-model-verify/test_contract_coverage.py:672-680`).

The locked text is currently wrong under Claim 1b, but it is genuinely locked.

**Claim 4 — PASS.**

## Claim 5 — new and modified assertions

Two defects remain.

First, `test_the_fault_seam_fires_after_the_canary_exists` claims that observing the seam message proves creation happened first, but moving the seam before `New-Item` leaves both its message assertion and absence assertion passing (`evals/multi-model-verify/test_home_skill_canary.py:268-282`). The later ACL-based case is the actual timing observation (`evals/multi-model-verify/test_home_skill_canary.py:445-478`), while the preceding case already covers message and rollback behavior (`evals/multi-model-verify/test_home_skill_canary.py:256-265`). Delete the obsolete timing test or narrow its name and docstring so it no longer claims to prove ordering.

Second, D10 says the checker recognizes `.split(<sep>)` whenever the literal separator contains a newline (`docs/superpowers/plans/rounds/2026-08-03-home-skills-root/execution-deviations.md:343-353`). The implementation instead accepts only exact `"\n"`, `"\r\n"`, or `"\r"` membership (`evals/tools/check_exact_line_oracles.py:95-122`), and the added tests cover only LF and CRLF (`evals/multi-model-verify/test_check_exact_line_oracles.py:43-73`). Add a composite-separator case such as `"\n\n"` and implement the recorded “contains CR or LF” predicate, or narrow D10 and the checker’s docstring.

The deliberately pre-green cases are not defects: the plan explicitly allowed the existing review-agent regression guard and clean-builder positive control to pass before implementation (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:442-448`; `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:718-732`).

**Claim 5 — FIX: remove/narrow the obsolete timing test and close the exact-line checker’s stated-versus-implemented scope gap.**

## Claim 6 — deviation completeness

The ledger is not complete beyond the already accepted Task 5 test-code departure.

Two additional unrecorded departures exist:

1. Task 6 requires modifying `CLAUDE.md` (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:855-862`), and that change shipped (`CLAUDE.md:84-89`), but the frozen staging command omits `CLAUDE.md` (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:889-894`). Including it was correct, but it required an implementer judgment and needs a deviation entry.

2. Task 6 froze an em-dash heading (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:864`); the shipped heading uses a hyphen (`docs/superpowers/plans/2026-07-27-0150-backlog.md:20`). Under this review’s exact spec-fidelity rule, that is unrecorded drift.

D10’s “contains a newline” versus exact-three-separators implementation is also an unresolved mismatch between the ledger and shipped code (`execution-deviations.md:343-353`; `evals/tools/check_exact_line_oracles.py:95-122`).

Add deviation entries for the known Task 5 test changes, the Task 6 staging omission and heading substitution; then either implement D10 as recorded or correct its recorded scope.

**Claim 6 — FIX: the 20-entry ledger plus the brief’s known gap is not complete.**

## Claim 7 — severity of the four accepted Minors

The four accepted findings are correctly Minor:

- “The lane was never open” is an overbroad backlog statement, while the operative contract remains version- and delivery-shape-bounded (`docs/superpowers/plans/2026-07-27-0150-backlog.md:37-42`; `skills/multi-model-verify/references/backup-lane.md:355-373`).
- The Task 5 test departures strengthen cleanup, lock, output, and positive-control checks rather than weakening the implementation (`evals/multi-model-verify/test_kimi_lane_home.py:1916-1977`).
- The close-out conveys the measured behavior, readout, and positive control but omits the exact verdict label; the canonical record still names `SUPPRESSED BY THE FLAG` (`docs/superpowers/plans/2026-07-27-0150-backlog.md:22-35`; `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:197-204`).
- The missing backlog entry leaves known reliability debt but does not turn the settled flake into a branch regression (`docs/superpowers/plans/rounds/2026-08-03-home-skills-root/execution-deviations.md:836-868`).

None changes runtime containment or falsifies the operative contract. The two accepted Important findings do.

**Claim 7 — PASS.**

## UNVERIFIED

- I did not rerun the current Python gates; the required gate commands are `CLAUDE.md:9-13`. Historical results in the ledger were read but are not treated as fresh execution evidence (`docs/superpowers/plans/rounds/2026-08-03-home-skills-root/execution-deviations.md:750-755`).
- The raw live probe material was deliberately not committed, so I verified the normalized record’s internal claims and corrections, not the original wire bytes (`docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md:260-265`). Per the stated boundary, this is not folded into the verdict.
- Push, installed-cache refresh, restart, and doctor-version confirmation are not established by this commit range (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:889-902`).

## Terminal verdict

**FIX for `e94c0b5..5b312d8`.** Apply both accepted Important text-plus-pin repairs with the narrower wording above, correct the additional probe-record overclaim, narrow the seam documentation, repair the obsolete timing assertion and D10 scope mismatch, and complete the deviation ledger before re-review.

