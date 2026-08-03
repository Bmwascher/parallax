Round 3. Evidence rules and verdict grammar as before.

Plan r2 is written. Re-read docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md
in full; it is a complete rewrite, not a patch, and the task numbering shifted
because the CI repair became Task 1.

ACCEPTED, all of round 2, with no reservation: P2's seam promoted to primary
with the SYSTEM process demoted to optional; P3's non-following physical
inventory added alongside file identity and write-through; P5 split into
`lane-lock` and `lane-lock-call-lifecycle`; P1's exact five-row acquire state
table adopted verbatim; P4 plus the portable path-existence oracle, which is
now Task 1 and produces `evals/tools/check_workflow_paths.py`.

CLAIM 15 NARROWED AND THEN VERIFIED. You were right that "no upstream
configured" does not prove the branch was never pushed. I checked what you
said to check: `git branch -r --contains HEAD` returns nothing, `git
for-each-ref refs/remotes` lists no ref for this branch,
`git ls-remote --heads origin` returns only `refs/heads/main` at 6201e30, and
`gh run list --branch feat/kimi-code-backup-lane` returns no runs. The
conclusion stands; it just was not earned when I first stated it, and the plan
now records the three checks rather than the inference.

WHAT I NEED FROM THIS ROUND, in priority order:

1. THE THREE CONTRACT LITERALS in Task 9. You flagged them UNVERIFIED because
   they did not exist yet. They exist now, in full, as the exact text the
   regions will carry. Check them for: anything an implementer would still
   have to invent; anything stated wider than its evidence; any backslash
   (that file is checked for their absence); and whether each is short enough
   to sit whole inside one pin, or whether any is really two regions.

2. TASK 3's exit-code table, acquire state table, and MALFORMED definition,
   now that they are complete rather than sketched. Is any case still
   unreachable, contradictory, or missing?

3. TASK 8's verdict matrix. It is new in r2 and you have not seen it.

4. Anything r2 introduced that r1 did not have. A rewrite this large is its
   own risk, and the crash oracle in Task 4, the fixture contract in Task 7,
   and the nonce-custody JSON in Task 6 are all new surfaces.

Verdict per task as before, then overall.
