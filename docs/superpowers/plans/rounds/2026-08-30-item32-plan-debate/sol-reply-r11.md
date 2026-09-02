## 1. The four required changes

1. The point-of-use sentence was replaced, but it still does not match the tool contract completely: Task 3 says exit 2 means “a bad invocation,” while Task 1 says exit 2 also covers internal execution errors. Its parametrized assertion checks only the 0 and 3 clauses, so either the 1 or 2 clause can be absent or wrong while the test passes. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:57-63`, `:368-374`, `:455-459` — **DOES NOT CLOSE**

2. The unreadable-receipt behavior now has a deterministic named test using a directory as `-Receipt`, requiring `no-receipt` and exit 1 rather than 2. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:55-61`, `:81`, `:130` — **CLOSES**

3. Artifact publication order now agrees across the architecture, named test, tool region, and executable steps: PID/start ticks → internal commit marker → external receipt. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:7`, `:74`, `:117-124`, `:181-190` — **CLOSES**

4. Task 9 now explicitly replaces the obsolete session-owned mechanism, and its negative grep covers the old launch and sidecar wording. The positive oracle is still insufficient: `grep -c "A\|B\|C"` counts matching lines, so three occurrences of only one alternative satisfy “at least three,” while all three required strings on fewer than three lines fail. The following instruction to read the matches manually is not a task-local automated oracle. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:774-800` — **DOES NOT CLOSE**

## 2. Base-rate sweep

I used the requested ten-of-ten base rate; the plan itself continues to require treating completion safety as open. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:21-26`

I found no new false-completion path after rechecking:

- receipt substitution and expected-act binding;
- receipt publication races and partial receipt writes;
- hard kills before PID, marker, or receipt publication;
- live wrappers with partial replies;
- PID recycling and unreadable process identity;
- missing, malformed, unreadable, or cross-act control artifacts;
- wrapper parse/client-child failures;
- exit-status-only callers and the evidence-binder boundary. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:71-104`, `:117-141`, `:417-459`, `:562-574`

I did find new oracle and contradiction instances:

1. **Partial exit-mapping oracle:** only codes 0 and 3 are asserted, although the shipped sentence specifies four codes. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:368-374`, `:459`
2. **Positive spec oracle can bind the wrong text:** its alternation count does not require each required token or mechanically constrain them to the mechanism section. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:794-800`
3. **Both initial failure counts are impossible as written.** The Codex and Kimi centralization guards assert that `Start-Process` is absent, and it is currently absent from both shipped documents, so those guards pass before implementation; each task should expect three parametrized/coverage failures and one passing negative guard, not four failures. `skills/multi-model-verify/SKILL.md:174-251`; `skills/multi-model-verify/references/backup-lane.md:21-35`; `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:376-398`, `:514-556`
4. **The spec’s scope table remains scheduled to finish with stale task numbers:** it assigns Codex to Task 4 and Kimi to Task 5, while the plan implements them in Tasks 3 and 4. Task 9’s reconciliation list and oracle do not name those rows. `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:65-71`; `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:319-323`, `:498-504`, `:774-800`

## 3. Revision-10 contradiction sweep

The newly edited architecture, tool region, executable ordering, and publication-order test now agree. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:7`, `:74`, `:117-124`, `:181-190`

The remaining contradictions are:

- exit 2 means parameter-binding **or internal execution error** in Task 1, but only “bad invocation” at the Task 3 point of use; `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:61`, `:459`
- Task 3 expects four initial failures although its absence guard already passes; `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:376-398`
- Task 4 has the same incorrect four-failure expectation; `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:514-556`
- Task 9 can replace the mechanism correctly while leaving the spec’s Task 4/Task 5 scope dispositions inconsistent with the plan. `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:65-71`; `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:774-800`

I did not count the design’s current seven-state model or old mechanism as additional defects because Task 9 explicitly schedules and negatively gates their replacement. `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:136-169`, `:190-207`; `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:774-800`

## 4. Freeze decision

The plan is not ready to freeze. The smallest sufficient changes are:

1. Make Task 3’s point-of-use sentence match all four exit meanings exactly, and assert all four clauses per Codex site.
2. Correct Task 3 and Task 4’s initial expectations to three failures and one passing centralization guard.
3. Replace Task 9’s alternation count with a section-scoped oracle that independently requires all three strings.
4. Add the scope table’s Codex/Kimi task dispositions to Task 9 reconciliation and verify Task 3/Task 4 explicitly.

The two harness-contract facts remain non-repository-verifiable, while actual cross-shell persistence, both-host detachment, and real non-ASCII round binding remain measurements performed during Task 8 rather than facts established by this plan review. `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:32`, `:729-753`

**FIX**