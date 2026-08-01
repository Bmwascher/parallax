All three round-15 edits are correct. One blocking handoff defect remains because the stated task packet excludes shared values that some tasks require.

### Task 1

Task 1 contains its complete file scope, initial four-module set, two checker behaviors, mutation tests, workflow edit, and verification command. It does not depend on the separate `Fixed names and values` section. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:74-99`

Task 1 is safe to start from its own text plus Global Constraints.

**PASS**

### Task 2

The credential schema, precedence, types, fixtures, host selection, and verification commands are all repeated inside Task 2. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:103-135`

**PASS**

### Task 3

The round-15 normalization fix is correct. It preserves a drive root, normalizes non-roots, freezes ordinal case-insensitive comparison, and requires both-host root and non-root tests. Its justification matches the builder’s existing separate root treatment. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:195-216`; `tools/new-kimi-lane-home.ps1:86-100`

However, a Task 3 implementer receiving only Global Constraints and Task 3 will not receive `Fixed names and values`. That separate section supplies the exact token regex, hostname comparer, tick representation, PID rule, wait/poll bounds, and confirmation-hash rule that Task 3’s validation and MALFORMED behavior require. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:33-49,64-70,155-170,254`

Precise fix: every task packet must contain the shared preamble comprising Goal, Architecture, Tech Stack, Global Constraints, Measured Facts, and Fixed Names and Values—`docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:7-70`—plus that task. Alternatively, duplicate every applicable fixed value inside Task 3; broadening the shared packet is smaller and prevents drift.

**FIX — BLOCKING: include the complete shared preamble through `Fixed names and values` in each implementer’s task packet.**

### Task 4

Its OS-level protocol and failure-capable crash oracles are self-contained, while the implemented Task 3 script will already exist when this task begins. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:278-299`

**PASS**

### Task 5

The code-3 correction is exact and consistent: exclusive-handle, LIVE-holder, and UNMEASURABLE-holder contention all propagate the same code 3. The added explanation correctly establishes why one wrapper test per exit code remains sufficient. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:321-340`

**PASS**

### Task 6

The seam now has the exact name, scope, position, mutation behavior, exit code, stderr sentinel, stdout prohibition, state assertions, and teardown. The justification does not alter or contradict its behavior. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:369-387`

**PASS**

### Task 7

Its three fixture paths, manual setup, custody rules, client gates, cleanup matrices, and verification commands remain complete within the task. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:391-518`

**PASS**

### Task 8

The two new pins remain correct. Under the stated restricted handoff, however, Task 8 does not receive the fixed lane-home path defined outside both Global Constraints and Task 8. Its recovery and Status commands use `<lane-home>` while describing it only as the configured lane home. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:64-70,521-572`

The shared-preamble fix named under Task 3 closes this without duplicating the path.

**FIX — BLOCKING: include `Fixed names and values` in the task packet; no Task 8 behavioral change is needed.**

### Task 9

The three exact literals and their complete normalized pinning procedure are fully contained inside Task 9. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:578-605`

**PASS**

### Task 10

The six modules, version, final gates, live reruns, and history mutation oracle are fully contained inside Task 10. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:609-632`

**PASS**

## Answers

1. **Not yet PASS.** The plan content is behaviorally ready, but the announced implementation packet omits the separate shared values needed by Tasks 3 and 8. Include the complete shared preamble through line 70 with every task.

2. All three round-15 fixes match what I specified. None of the added justification introduces a contradiction. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:199,327,381`

3. Task 1 is independently safe to start from its own text plus Global Constraints. Building the whole plan should wait until the task-packet rule includes the complete shared preamble. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:74-99`

The artifact correction is also honest. “Reproduced without edit” remains an unverified session assertion, but the following provenance paragraph explicitly says it cannot be independently proved and narrows verification to repository-resolvable claims. `docs/superpowers/plans/rounds/2026-08-01-cred-lock/fable-whole-plan-review.md:14-24`

The Actions correction is properly scoped to the branch-filtered command and explicitly retracts the wider unfiltered inference. `docs/superpowers/plans/rounds/2026-08-01-cred-lock/fable-whole-plan-review.md:88-97`

## Overall verdict

**FIX.** The three requested amendments pass. The only remaining blocker is the implementation-packet boundary: provide lines 7–70 plus the assigned task, rather than Global Constraints alone.

## Final check

- **UNVERIFIED:** Measurements 1–21 as external experiments. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:51-62`
- **UNVERIFIED:** The three-login generalization beyond measurement 11. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:397,412-414`
- **UNVERIFIED:** That the fable reply was reproduced without alteration; the artifact now states this limitation correctly. `docs/superpowers/plans/rounds/2026-08-01-cred-lock/fable-whole-plan-review.md:14-24`
- **UNVERIFIED:** Current remote and Actions state. The corrected branch-filtered results are recorded, but this sandbox cannot independently rerun them. `docs/superpowers/plans/rounds/2026-08-01-cred-lock/fable-whole-plan-review.md:88-97`
- **UNVERIFIED:** All implementation, pytest, live, and CI gates because implementation has not begun.

