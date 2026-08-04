<role>Adversarial reviewer, equal weight, in a two-model debate. Read-only.</role>

<task>Mode diff. Verify the implementation on `e94c0b5..5b312d8` against its
frozen plan, and check the two accepted repairs below actually close what they
claim to close. Refute or confirm each numbered claim.</task>

<rules>
Cite `path:line` for every claim you make or contest; uncited claims are
struck. Do not manufacture objections: if a claim stands, say PASS and move on.
End each claim PASS, FIX (with the specific fix), or ESCALATE, then give one
terminal verdict for the range.

This repo's two governing invariants, which are the review standard:
- A claim may never be wider than its evidence.
- An unmade, failed, or unreadable measurement is never a clean one.

Spec fidelity is a finding: the implementer makes zero judgment calls, so any
drift from the frozen plan is a defect unless the execution ledger records it
as a deviation. Drift the ledger does NOT record is the thing to hunt.
</rules>

<context>
You are in the repo root. Read what you need:

- Full diff: run `git diff e94c0b5..5b312d8`. It is 44 files, +5755/-75.
  Most of the volume is added documentation under
  `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/` - these are
  evidence artifacts (reviewer replies, the probe record), not product.
  The product changes are in `skills/`, `tools/`, `evals/`, `CLAUDE.md`
  and `.claude-plugin/plugin.json`.
- Frozen plan, revision 7:
  `docs/superpowers/plans/2026-08-03-home-skills-root-probe.md`
- Execution ledger, deviations D1-D20:
  `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/execution-deviations.md`
- The measured probe record, which is the evidence every text claim rests on:
  `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/probe-record.md`
- The required whole-branch review of this exact range, with my per-finding
  adjudications appended:
  `docs/superpowers/plans/rounds/2026-08-03-home-skills-root/fable-review-e94c0b5-5b312d8.md`

WHAT THE BRANCH DID. Backlog item 17 asked whether the user's home skills
root, `~/.agents/skills/`, is reachable by kimi-code, the backup reviewer
lane's client. An earlier 2026-07-31 probe reported that the `--skills-dir`
flag "suppresses nothing observable", and the shipped skill carried that.
This branch ran a live 6-cell probe and found the earlier comparison
confounded, the home root reachable with the flag omitted, and suppressed
with the flag passed against an empty target. The lane itself was not open,
because the reviewer agent denies the `Skill` tool.
</context>

<claims>

1. The whole-branch review of this range returned two Important findings, both
   of the claim-wider-than-evidence class. I ACCEPTED both after reading the
   evidence myself. They are not yet fixed in the range you are reading.
   Claim: both diagnoses are correct, and my proposed replacement text below
   is the narrowest wording the evidence carries - neither still too wide, nor
   narrowed past what was actually measured.

   1a. `skills/multi-model-verify/SKILL.md:70-71` currently reads:
       "That 2026-07-31 comparison was CONFOUNDED: `Skill` was denied, so it
       measured the deny list, not the flag."
       Defect: the 2026-07-31 arms differed only in the flag, with `Skill`
       denied in both, and nothing loaded in either. That null is equally
       consistent with the deny list blocking invocation and with the project
       roots never being discovered at all. Nothing separated them, so
       "it measured the deny list" attributes a result to a layer never
       isolated.
       Proposed replacement: "That 2026-07-31 comparison was CONFOUNDED:
       `Skill` was denied, so it could not observe the flag."

   1b. `skills/multi-model-verify/references/backup-lane.md:358-363`, inside
       the locked contract region `home-skill-root-disposition-limit`,
       currently reads that the two project roots' "exclusion rests on the
       flag's measured replacement semantics and the client's own help text",
       and that "The flag REPLACES discovery with its target rather than
       adding to it, so it does not suppress its own target - it selects it".
       Defect: no cell ever passed the flag against a POPULATED target
       (`probe-record.md:38-45`, cells A, B and C all flag-on with no canary
       in `<debate-home>/skills/`), so selection was never observed; and
       `probe-record.md:285-291` explicitly RETRACTS the replacement reading
       as "text evidence, not a four-root measurement, and this record must
       not launder one into the other". The locked region contradicts its own
       cited record.
       Proposed replacement for those two sentences: "exclusion rests on the
       client's own help text, which says the flag's target is used instead
       of auto-discovered directories - text evidence, never a measurement -
       and on preflight-3 remediation clearing them in the mirror regardless.
       No cell passed the flag against a POPULATED target, so what the flag
       does to its own target is unmeasured; its suppression of the other
       roots was measured only with that target EMPTY, and holds only while
       `<debate-home>/skills/` stays empty:"

2. Claim: those two are the LAST instances of the claim-wider-than-evidence
   class in this range. Four earlier instances were caught and fixed during
   the branch (ledger D4, D17, D18, D19) and the review found these two.
   Refute this if you find a sixth anywhere in `SKILL.md`,
   `references/backup-lane.md`, the probe record, the ledger, or the backlog
   close-out. This is the highest-value thing you can do in round 1.

3. Claim: the builder postcondition added to `tools/new-kimi-lane-home.ps1` is
   correct and cannot pass when it should fail. It asserts the `skills/`
   directory it just created is empty, throws on a non-empty or
   unenumerable result, and the throw reaches the catch that deletes the home
   and the finally that releases the lock. Its two `PARALLAX_SKILLS_SEED_*`
   env seams exist only so the tests can drive the failure, cannot fire in
   production use, and can only cause a build to FAIL, never to succeed
   differently. The documented exit code for the failure is 1, measured.

4. Claim: the two new contract regions in `references/backup-lane.md`,
   `home-skill-root-disposition` and `home-skill-root-disposition-limit`, are
   genuinely LOCKED under this repo's pin rule, which `CLAUDE.md` states in
   full: each region's text must sit whole inside a SINGLE string literal in
   one of exactly three assertion clause forms, in an assertion able to fail
   the suite. `DECLARED_REGIONS` in `evals/multi-model-verify/test_contract_coverage.py`
   gained both ids. Twelve pin-integrity defects exist in this repo's history,
   so check the pins themselves, not the checker's verdict.

5. Claim: the new and modified assertions in `evals/multi-model-verify/` -
   principally `test_home_skill_canary.py` (new, 495 lines),
   `test_backup_lane.py`, `test_kimi_lane_home.py`,
   `test_multi_model_verify.py` and `test_check_exact_line_oracles.py` - can
   each fail for the reason they claim. Hunt for assertions that are
   tautological, that would pass unchanged against `e94c0b5`, or that assert
   on a value the test itself produced.

6. Claim: the ledger's 20 deviations are complete for this range, with one
   known gap the review found and I accepted: Task 5 Step 1's frozen test code
   was not shipped verbatim (renamed cases, a stricter `stdout == ""`
   assertion, added lock-state and target-absence checks) and no deviation
   records that. I will add it. Refute this by finding drift from the frozen
   plan that neither the ledger nor this brief records.

7. Claim: the four Minor findings I accepted (the unbounded "never open" in
   the backlog close-out; the unrecorded Task 5 departure; the close-out not
   naming the verdict label `SUPPRESSED BY THE FLAG`; and the ledger's own
   instruction to raise a backlog item for the flaky behavioural case, not
   executed) are correctly classed as Minor, and none of them is a Critical
   or Important wearing a small label.
</claims>

<boundaries>
Not under debate, decided by the user or already settled by measurement:
- The probe's design, its six cells, and its verdict. That debate ran and
  closed; its record is `reopened-debate-record.md`.
- The decision to keep the SKILL.md edit at lines 70-75 rather than send
  readers to a 35 KB reference file. It is kept on independent justification
  and is explicitly NOT claimed as a repair for the behavioural failure.
- The behavioural eval case `plan-mode-debate-runs` being flaky rather than a
  regression. Measured: unchanged tree 6 runs / 2 passes, this branch 7 runs /
  1 pass. Do not re-open it.
- The version bump to 0.20.0 and the merge commit message.
</boundaries>

<final-check>List any claim you could not verify against files you actually
read, as UNVERIFIED. Do not fold unverified material into your verdict.</final-check>
