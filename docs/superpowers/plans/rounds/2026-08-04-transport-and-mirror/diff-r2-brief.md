Round 2, fix re-review. Evidence rules and verdict grammar as before.

All round-1 findings are applied at `43e45ef`. Read `git diff 5b312d8..43e45ef`.
The full range is now `e94c0b5..43e45ef`.

WHAT I DID, per finding.

1a. SKILL.md now reads "That 2026-07-31 comparison was CONFOUNDED: `Skill` was
    denied in both arms, so the comparison did not isolate the flag." Your
    wording, unchanged. The pin moved with it and gained a negative clause
    asserting the struck causal wording is absent.

1b. The `home-skill-root-disposition-limit` region now carries your wording,
    with "the project roots" spelled out and suppression claimed only for
    `~/.agents/skills/`. The region id is unchanged and its pin moved with it.

2.  The probe record's cell C sentence now names what was held constant, says
    each cell ran in its own freshly built debate home as the frozen procedure
    requires, and calls the flag the intended differing variable, not the only
    difference.

3.  CLAUDE.md and the builder comment both dropped the "only site that writes
    there" claim. Both now say every writer sits in the builder itself, that
    the two seams are gated on environment variables any parent process can
    set, that no shipped caller sets them, and that either can only force a
    build to FAIL.

5a. `test_the_fault_seam_fires_after_the_canary_exists` is DELETED, with a
    comment in its place naming what covers each of its two assertions.

5b. The `_is_line_split` docstring and D10 both now state the three exact line
    terminators and say why a composite separator is deliberately out of reach.
    The code is unchanged; the words moved to it.

6.  Ledger gains D21 (Task 5 frozen-test departure), D22 (Task 6 staging
    omission), D23 (the em-dash heading, fixed rather than ridden), D24 (the
    four claim-width instances at this gate, including that two of my own
    repairs carried the defect), D25 (the deleted test), D26 (the checker's
    stated reach) and D27.

7.  The four Minors: the backlog close-out now names the verdict
    `SUPPRESSED BY THE FLAG`, bounds the not-open claim to kimi-code 0.31.1
    and says it reaches no further, and a new backlog item 18 records the flaky
    `plan-mode-debate-runs` case with its measured pass rates and the
    grader-truncation cause.

THREE THINGS I FIXED THAT YOU DID NOT FIND. Check these hardest, because they
are mine and unreviewed.

A. The "only site that writes there" sentence had a THIRD copy, in the backlog
   item 17 close-out. You cited CLAUDE.md and the builder. I found it by
   grepping the branch for the claim rather than fixing the two sites cited.
   All three are now consistent.

B. Item 17 retained its whole pre-probe problem statement beneath the Resolved
   block with nothing marking it historical, so the item asserted the
   measurement and then contradicted it forty lines later in the present tense
   ("`--skills-dir` is a mitigation with unmeasurable effect and claims
   nothing"). I added a labelled boundary saying the text below is the item as
   written BEFORE the probe, superseded where the two disagree, naming the two
   falsified claims. I rewrote no sentence inside it. Judge whether that is the
   right repair or whether the stale text should simply go.

C. The ledger header said the frozen plan was at revision 6. It is at revision
   7. Corrected, with the staleness stated.

GATE RESULTS after application: skill_lint PASS (1 warning, SKILL.md 5129
tokens against a ~5000 budget, up 3 from the wrong sentence); skill_scanner
clean; check_exact_line_oracles exit 0; run_trigger_evals all clear; and
`pytest evals -q` 973 passed / 13 skipped, exit 0, on BOTH `powershell.exe` and
`pwsh.exe`. 974 passed before, so the delta is exactly the one deleted case.

WHAT I AM ASKING.

- Does each repair close what it claims to close?
- Is any repair itself wider than its evidence? Two of my four round-1 repairs
  carried the defect they were repairing, so this is the question that matters.
- Are A, B and C correct, and is B the right shape of fix?
- Anything in `5b312d8..43e45ef` that regressed something that was right before.

Give one terminal verdict for `e94c0b5..43e45ef`.
