Revision 14 is close, but not yet a PASS. Three blocking defects remain; two are consequences of the new cross-task semantics.

### Task 1

Task 1 is safe to start from its own text alone. It identifies the orphan in both Windows steps, freezes the initial four-module parity set, separates Task 10’s later additions, and mutation-tests both path existence and host parity. `.github/workflows/skill-evals.yml:79-99`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:74-99`

It has no dependency on Task 3’s later replacement file—the text expressly prohibits relying on that coincidence. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:78-80`

**PASS**

### Task 2

Unchanged and complete: validation precedence, duplicate-key direction, host selection, fixture validation, and both-host gates remain explicit. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:103-135`

**PASS**

### Task 3

The separate `debateHome` comparison is now coherent, and the delta form is acceptable. It excludes `debateHome` from the five-field holder identity, compares it separately, and explicitly routes every same-host UNMEASURABLE case through the corresponding LIVE outcome. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:194-215`

Your exit-code consequence is also correct: code 3 now covers LIVE and UNMEASURABLE contention consistently with that routing. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:174-182,215`

Foreign-host Status is now complete and has a collision-capable oracle. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:246-250`

One blocking normalization case remains. The algorithm says the result of `GetFullPath()` is absolute and then unconditionally trims one trailing separator. A drive root loses its defining separator, yet Task 3 does not forbid a root-valued `-DebateHome`; the builder itself already treats drive roots as a distinct case requiring special handling. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:151,157-160,198`; `tools/new-kimi-lane-home.ps1:86-100`

Precise fix: after `GetFullPath()`, obtain `GetPathRoot()`. Preserve the normalized string unchanged when it equals its root under ordinal case-insensitive comparison; otherwise trim the normalized trailing separator. Add both-host tests that equivalent root spellings remain the same absolute root and that the existing relative/trailing-separator non-root cases remain equal.

**FIX — BLOCKING: make `debateHome` normalization root-aware and test the root case under both hosts.**

### Task 4

The unchanged OS gate still has failure-capable exclusive-handle, crash-truncation, partial-write, and inverted-host-divergence oracles. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:278-299`

**PASS**

### Task 5

Task 5 still defines lock code 3 as contention from “the exclusive handle OR a live holder.” Revised Task 3 defines the same propagated code for a LIVE or UNMEASURABLE holder. Those are now two definitions of the wrapper’s exit surface. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:178,215,326`

Precise fix: change Task 5’s code-3 text to “the exclusive handle OR a holder that is LIVE or UNMEASURABLE.” Its existing one-test-per-exit-code requirement remains sufficient because the wrapper receives the same lock-tool code 3 in either holder case. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:326-334`

**FIX — BLOCKING: update Task 5’s code-3 definition to include UNMEASURABLE.**

### Task 6

The wrong-`-Path` integration oracle is now strong: valid home B ensures that omitting the lock comparison would permit deletion, while the required result is exit 2 with both homes and the lock unchanged. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:368-380`

The post-deletion release oracle now reaches the correct precedence branch and requires the correct state. However, its seam is unnamed, while the other fault seams are deliberately given exact shared names. The implementer must currently invent the environment variable that production and tests must agree on. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:364-366,380`

Precise fix: name it `PARALLAX_LANE_HOME_REMOVE_RELEASE_FAULT`. State that it is honored only in Remove mode, immediately after successful deletion and before release; when nonempty, it skips lock mutation and produces the simulated release result code 5. Freeze its stderr sentinel as `PARALLAX_LANE_HOME_REMOVE_RELEASE_FAULT injected: simulated post-delete release refusal`, with no stdout.

**FIX — BLOCKING: freeze the Remove release-fault seam’s exact name, scope, result, and diagnostic.**

### Task 7

C’s lifecycle is now executable and noncontradictory: steps 1–4 and 6, with marker step 5 explicitly omitted. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:401-414`

The custody, cleanup, secret-set, and support-oracle rules remain internally aligned. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:431-517`

**PASS**

### Task 8

Both new behaviors now have explicit failure-capable pins: UNKNOWN must map to N/A with its complete explanation, and foreign-host detection must be case-insensitive and carry the complete recovery command. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:527-543,557-572`

**PASS**

### Task 9

The contract literals remain internally consistent with the revised lock behavior and retain normalized whole-region verification. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:578-605`

**PASS**

### Task 10

The six-module dual-host wiring, final live reruns, behavioral evaluation, and throwing history oracle remain complete. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:609-631`

**PASS**

## Answers

1. **Not yet PASS.** Apply the Task 3 root normalization, Task 5 code-3 wording, and Task 6 seam-name fixes above.

2. Both consequences you chose are correct:

   - Updating code 3 to include UNMEASURABLE was required for consistency. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:178,215`
   - The delta form is preferable to duplicating four LIVE rows. It remains zero-judgment because it identifies exactly which rows are inherited and spells out idempotence, exit 2, contention, and no reclamation. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:204-215`

3. Task 1 itself is safe to start from its text alone, but building should not start yet because the plan header still correctly says DRAFT awaiting re-review and the three blockers above remain. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:5,74-99`

The retained fable artifact is now verified present and readable. It contains the reported no-Critical/two-Important/six-Minor verdict and its appended adjudication, so “no inspectable artifact” is closed. `docs/superpowers/plans/rounds/2026-08-01-cred-lock/fable-whole-plan-review.md:1-19,31-59,63-79`

## Overall verdict

**FIX.** Tasks 1, 2, 4, and 7–10 pass. Tasks 3, 5, and 6 require the three precise blocking corrections above.

## Final check

- **UNVERIFIED:** Measurements 1–21 as external experiments. The repository design expressly says those measurements are outside its offline verification. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:50-61`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:348-351`
- **UNVERIFIED:** The three-login generalization beyond measurement 11. It remains correctly labelled and fails loudly. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:397,412-414`
- **UNVERIFIED:** The fable artifact’s claim that the embedded reply is verbatim and came from a fresh subagent; the artifact’s contents are inspectable, but no independent source transcript was supplied. `docs/superpowers/plans/rounds/2026-08-01-cred-lock/fable-whole-plan-review.md:1-15`
- **UNVERIFIED:** The current remote `ls-remote` and GitHub Actions claims. Network access failed and `gh` is unavailable in this sandbox; the retained artifact records the prior results but cannot independently prove their current state. `docs/superpowers/plans/rounds/2026-08-01-cred-lock/fable-whole-plan-review.md:75-79`
- **UNVERIFIED:** All implementation, pytest, live, and CI gates because no implementation exists yet.

