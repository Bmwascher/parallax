1. All accepted textual fixes are present: corrected goals and rule-8 scope (`docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:36`, `docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:264`), per-citation inventory (`docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:202`), honest hook residuals (`docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:310`), CI range mode (`docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:415`), labelled shape checks and second-reader duties (`docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:284`, `docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:456`), and canonical digest rules (`docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:113`).

One contradiction remains: Goal 2 and Part 3 say nothing reaches main without re-attestation, but the push-event CI range check can only fail after that push has updated main (`docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:36`, `docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:299`, `docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:415`; `.github/workflows/skill-evals.yml:7`). Impact: high for direct pushes without the local hook.

**FIX — Require protected main with direct pushes disabled and the pull-request range job as a required check, or narrow “nothing reaches main” to “violating pushes are detected after arrival.”**

2. The range mode detects the violation on both push and pull-request events, and the existing workflow subscribes to both (`docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:415`; `.github/workflows/skill-evals.yml:7`). It does not itself prevent a hookless direct push: a `push` workflow runs after the ref update. Nor does the tree establish that the pull-request job is a required merge check; the spec names no branch-protection or ruleset requirement (`docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:418`). Impact: high; detection is being described as prevention.

**FIX — Add repository ruleset requirements to the design: forbid direct main pushes and require the range-check job before GitHub UI merges.**

3. The digest now defines encoding, CRLF normalization, line selection, trailing-blank removal, separators, group framing, and final encoding, with the requested equality test (`docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:113`). Two implementation decisions remain: “strip trailing whitespace” does not specify whether whitespace means ASCII space/tab or Unicode whitespace, and “ranking group header text” does not say whether the hashed bytes include the literal `### ` prefix (`docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:118`, `docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:120`). Different reasonable implementations can therefore produce different digests. The CRLF fixture proves that case only; it does not resolve these ambiguities. Impact: medium; independent working-tree and revision implementations can disagree.

**FIX — Define trailing stripping as an exact byte/code-point set, define the group component as either the complete header line or text after `### `, and pin both with fixtures.**

4. Section 1e now rejects every proposed universal resolver, records the concrete intermediate-tree counterexample, and requires per-citation verification with unresolved rows left unresolved (`docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:202`, `docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:218`). That preserves raw round artifacts exactly as the repository requires (`docs/superpowers/plans/rounds/2026-07-28-reviewer-isolation/README.md:10`). Treating the frozen plan differently is consistent because it is synthesized rather than raw, and the spec limits the edit to commit-binding its two citations (`docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:226`). Impact: none established.

**PASS.**

### New risks

None beyond the hard-control and digest-definition gaps in claims 2 and 3.

### Final check

- **UNVERIFIED, claim 2:** whether GitHub currently requires the pull-request job and rejects direct main pushes; needed the repository’s GitHub branch-protection/ruleset configuration, which is not present in the tree.
- **UNVERIFIED, claim 4:** the claimed total of 83 raw records and their resolving/unresolved results; needed the branch citation inventory prescribed at `docs/superpowers/specs/2026-09-04-backlog-rewrite-design.md:218`.