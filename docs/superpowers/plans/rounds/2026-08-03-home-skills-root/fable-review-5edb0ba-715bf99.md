# Fable per-task review — Task 5

**Range:** `5edb0ba..715bf99`. **Seat:** `agents/fable-reviewer.md`, read-only.
**Verdict at issue: Ready to merge: With fixes** — no Critical, two Important,
four Minor.

Reviewer's raw reply. The session's adjudication is in `execution-deviations.md`.

---

### Strengths

- **The builder postcondition does what the contract text claims, verified on
  the code path.** The throw at `new-kimi-lane-home.ps1:939-944` sits inside the
  build `try` opened at `:558`. At that point `$createdByThisInvocation` is true
  (`:838`) and `$cleanupRoot` is set (`:829`), so the `catch` at `:976-994`
  deletes the home; the rethrow reaches the `finally` at `:995-1014`, where
  `$lockAcquired -and -not $buildCompleted` releases the lock. Stdout is clean
  before the refusal: the only build-mode `Write-Output` is the custody line at
  `:966`, the lock's stdout is captured by assignment (`:144`), and every other
  emitter is `Out-Null`ed or stderr.
- **The implementer caught a live plan defect.** The frozen Task 5 Step 5
  snippet calls `Fail (...)`, and no `Fail` function exists anywhere in the
  builder — the only match is the phrase "Fail closed" in a comment at `:631`.
  Followed verbatim, the plan's code would have refused with a "term not
  recognized" error and the wrong stderr text.
- **The seams are fail-closed in production.** `PARALLAX_SKILLS_SEED_FILE` and
  `_HIDDEN` can fire on a real build if the variables leak, but the only
  reachable outcome is a refused build with the home deleted and the lock
  released — a denial, never a home that dispatches with content.
- **The pin machinery holds for both new regions, checked against the repo's
  live defect class.** `test_backup_lane.py` matches against `_norm(BACKUP_LANE)`
  and `contract_coverage.py` normalizes region bodies with the identical `_norm`,
  requiring pin-contains-region. I compared both bodies word for word against the
  pin literals: ASCII hyphens throughout, character-exact, so containment holds
  and neither pin is a fragment.
- **Scope is exact.** Six files, all listed by the plan; no per-round emptiness
  check; exactly two region ids; the `SKILL.md` change verified a shortening.

### Issues

**Critical:** none.

**Important 1 — a fourth overreach, in the pinned prose after region 2.** "The
load-bearing control as the lane ships is the `Skill` deny list - a discovered
skill cannot be invoked, measured in cells A and B of the same record." Cells A
and B ran with the deny list AND the flag both in force, with an empty flag
target — the exact composition whose non-attributability the probe record's
NARROWED correction states. In A and B the flag suppressed discovery, so those
cells contained no discovered skill whose invocation the deny list blocked. What
they measured is that the composition delivered nothing, plus that `Skill` was
absent from the advertised schema. Failure scenario: a future cycle cites this
pinned sentence to drop `--skills-dir` "because the deny list is the measured
control", exactly the independence claim the correction withdrew.

**Important 2 — the plan's promised pin on the SKILL.md replacement does not
exist.** Task 5 Step 4's rationale states "the replacement gets one direct pin
added in Step 1". Step 1's block contains no SKILL.md pin and the diff adds none.
Failure scenario: a later token-budget edit restores the falsified 2026-07-31
claim and the whole suite stays green — a false record of a measurement, the
defect class this cycle exists to remove.

**Minor 1 — "measured: replacement" compresses past the correction's bound.**
The correction says the cells establish suppression of ONE root under one
condition, and that the "instead of" semantics are help-text evidence the record
must not launder into measurement.

**Minor 2 — the builder's exit-code taxonomy is now stale.** The two new seams
and the postcondition refusal are listed nowhere. Tests only assert nonzero, so
nothing fails, but the header is the tool's documented contract.

**Minor 3 — SKILL.md wording deviates from the frozen plan's Step 4 block.**
Same meaning, shorter, consistent with the lint-budget motive, but a frozen-plan
text deviation should be recorded, not silent.

**Minor 4 — evidence gap, named as a gap.** The diff package carries no run
transcripts, so I could not verify Step 2 (every assertion watched to fail) or
Step 7 (the four coverage mutations). Under the governing rules those tests are
not yet evidence from where I sit.

### Assessment

Ready to merge: **With fixes.** The builder postcondition, its tests, and the
region/pin machinery are correct and verified on the code paths, and the two
contract regions are bounded to the record cell by cell — but the pinned prose
just outside region 2 attributes the deny-list claim to cells A and B against the
record's own dated correction, and the plan-promised pin on the corrected
SKILL.md sentence was never written.
