# Whole-branch review — `e94c0b5..5b312d8`

Seat: `agents/fable-reviewer.md`. Dispatched 2026-08-03 as the required input
to the mode-diff debate on this range. Raw reply retained verbatim below.
Range-bound: this artifact covers `e94c0b5..5b312d8` and no other range.

Diff package given to the reviewer: an 81 KB complete diff of
`.claude-plugin/`, `CLAUDE.md`, `evals/`, `skills/` and `tools/`; the backlog
document diff; and a stat manifest of the `docs/` additions. Frozen plan and
execution ledger given by path.

---

## Raw reply

### Strengths

- The probe record is the strongest artifact on the branch: header written before dispatch, cell validity gating (E attempt 1 recorded FAILED, not negative, probe-record.md:106-111), a mechanically applied not-found oracle (probe-record.md:121-132), and a dated CORRECTION section that retracts its own overclaims instead of editing them away (probe-record.md:269-301). The cross-tool generalization defect (a Grep result shape read as every tool's, probe-record.md:177-190) is exactly the kind of finding that pays for a live probe.
- The canary harness is genuinely guarded: transactional plant with a rollback whose failure is reported not swallowed (tools/plant-home-skill-canary.ps1:601-616), non-idempotent remove (:1654-1657 in patch, file Remove section), exact-path ordinal equality, reparse refusal with a manual non-following walk (:1455-1473), and every guard mutation-watched (ledger M1-M6, N1-N5, execution-deviations.md:533-557).
- The builder postcondition is correctly placed. Verified in the file: the throw sits inside the guarded try, the catch deletes the home this invocation created and rethrows (tools/new-kimi-lane-home.ps1:978-996), the finally releases the lock because `$buildCompleted` is still false (:997-1016), and custody JSON is constructed and emitted only after the check (:953-968), which is what makes `test_the_postcondition_refuses_before_emitting_custody_json`'s `stdout == ""` assertion true for the right reason. The two seams fire only on env vars no production caller sets, and their only effect is a failed build, never a silently altered one (:923-932).
- Pin integrity holds for both new regions. Each region's full text sits whole inside a single `assert ("...") in body` clause against `_norm(BACKUP_LANE)` (test_backup_lane.py:126 pattern; pins in the patch at code-diff 76-109), `DECLARED_REGIONS` gained both ids (test_contract_coverage.py:392-393 in patch), and the ledger records direct `collect_regions` verification plus the four coverage mutations including the appended-weakening-sentence case (execution-deviations.md:753-769).
- The tier-1c widening is done right: keyed on the separator not the method name, with a negative-direction case so the gate does not cry wolf on field parses (evals/tools/check_exact_line_oracles.py, `_is_line_split`; test_check_exact_line_oracles.py new cases).
- The ledger itself is the best-disciplined I have reviewed on this repo: 20 deviations including the session's own silences (D4), a refuted reviewer claim settled by measurement on both hosts, and D20 resolved by buying control runs instead of arguing.

### Issues

#### Critical

None.

#### Important

1. **Fifth claim-wider-than-evidence instance: "it measured the deny list, not the flag."** skills/multi-model-verify/SKILL.md:70-71, pinned verbatim by the new `test_the_confounded_flag_claim_stays_corrected` (test_multi_model_verify.py patch lines 1018-1023). The 2026-07-31 comparison measured nothing attributable to the deny list. Its null-null outcome has at least two live explanations the record never separated: the deny list blocking invocation, and the project roots not being auto-discovered at all, which no probe has ever measured (the 2026-08-03 probe canaried only the home root, backup-lane.md:357-358). This is the same attribution shape D17 corrected for cells A and B one file away ("cannot attribute their null result to either layer alone", backup-lane.md:376-379), applied to the 2026-07-31 cells and shipped as a positive claim of what was measured. The defensible sentence is "so it could not observe the flag." The pin and the text must move together.

2. **A locked contract region labels a coherence argument as a measurement.** references/backup-lane.md:359-360 says the project roots' exclusion "rests on the flag's measured replacement semantics", and :362-363 asserts "it does not suppress its own target - it selects it". No cell ever passed the flag with a populated target (all flag-on cells A, B, C ran it at an empty directory, probe-record.md:39-45), so selection was never observed, and the probe record's own CORRECTION explicitly retracts the replacement reading as "text evidence, not a four-root measurement... this record must not launder one into the other" (probe-record.md:286-291). D19 fixed exactly this word in the trailing prose ("measured: replacement" became "suppression of the home root", backup-lane.md:381-383) but the same overclaim survived inside the region the prose trails. This is frozen revision-7 text, so it is a plan-text defect rather than implementer drift, but the region is contract and the branch's governing rule does not exempt frozen text; the fix touches the region and its pin together, ids unchanged.

#### Minor

3. **"The lane was never open"** (docs/superpowers/plans/2026-07-27-0150-backlog.md, item 17 Resolved block, backlog-diff lines 41-46). "Never" spans every prior client and version; the measurement is one composition on kimi-code 0.31.1, and the disposition-limit region itself says a client whose delivery changes shape retires the measurement. "Not open as measured, 0.31.1" is the claim the evidence carries.
4. **Task 5 Step 1's frozen test code was not shipped verbatim and no deviation records it** (test_kimi_lane_home.py:1922-1993). Renamed cases, `stdout == ""` instead of substring absence, added `not target.exists()` and lock-state asserts, and the positive control's emptiness check plus `_remove2`. Every departure strengthens, but D5/D6 established on this same branch that verbatim admits no silent departures, and the ledger is silent here.
5. **The item-17 close-out never names the verdict.** Plan Task 6 Step 1 requires "naming the probe record path, the verdict, the readout...". The label `SUPPRESSED BY THE FLAG` appears nowhere in the inserted block; readout and control cell are named, the verdict is paraphrased.
6. **D20's closing instruction was not executed.** The ledger says the flaky `plan-mode-debate-runs` case should be raised as a backlog item "rather than leaving it to be rediscovered" (execution-deviations.md:864-869); the backlog diff adds no such item.

### Ledger minors triage

- **D2** (mutation named the other host): ride. The per-step property was demonstrated either way; prediction imprecision only.
- **D5** (mirror header not replaced verbatim): ride. The shipped header claims exactly what is true; the verbatim value is spent and recorded.
- **D6** (fourth backlog paragraph): ride. Accurate, outside the oracle's scan surface.
- **D8** (path-equality rationale wider than the mechanism): ride. Confirmed in the tool: `Remove-Item` targets a path derived from `-Root`, never from the state file, so the plan's attack is unreachable and the guard's true purpose is recorded. The mutation still fails its test.
- **D14** (Plant clobbers an existing `-StateOut`): ride. Non-recursive, driver-supplied, fresh per run; a refusal would add a probe failure mode for no measured risk.
- **Task 3 Minor 1** (sweep evasion by respelling): ride. The pinned dispatch template is the load-bearing gate and the record now says so.
- **D19/D20** (the plan's "SHORTENING" sentence now false at 5126 vs 5120 tokens): ride. The plan is frozen; the ledger is the correction channel and carries it.
- **D20** (flaky behavioral case): the flake rides, exonerated by thirteen runs; the missing backlog item is Minor issue 6 above and is a fix-before-merge at the cost of one paragraph.

### Assessment

Ready to merge: **With fixes.** The measurement, harness, postcondition, and pin machinery are sound and unusually well evidenced, but the branch ships two sentences that state measurements nothing made - one pinned in SKILL.md, one inside a locked contract region - and this cycle's own record establishes that class as fix-before-merge (D17 was fixed for exactly this shape). Both fixes are text-plus-pin edits with no runtime effect; the minors are cheap or riding.

---

## Session adjudication

Each finding adjudicated against the repo before any reviewer lane saw it.
Evidence read this session, by me, not taken from the reviewer's report.

| # | Class | Adjudication | Evidence I read |
|---|---|---|---|
| 1 | Important | **ACCEPT** | `SKILL.md:70-71` reads "`Skill` was denied, so it measured the deny list, not the flag." The 2026-07-31 arms differed only in the flag, with `Skill` denied in BOTH, and nothing loaded in either. That null is equally consistent with the deny list blocking invocation and with the project roots never being discovered. Nothing separated them. The same branch already corrected this exact attribution shape one file away at `backup-lane.md:376-379`. |
| 2 | Important | **ACCEPT** | `backup-lane.md:359-363` calls the replacement semantics MEASURED and asserts selection over suppression. The cell table at `probe-record.md:38-45` shows every flag-on cell (A, B, C) ran with no canary in `<debate-home>/skills/`, so a populated target was never exercised. `probe-record.md:285-291` RETRACTS the replacement reading in as many words: "that is text evidence, not a four-root measurement, and this record must not launder one into the other." The locked region contradicts its own cited record. |
| 3 | Minor | **ACCEPT** | "Never" is unbounded over client versions; the measurement is one composition on 0.31.1, and the disposition-limit region itself retires the measurement when delivery shape changes. |
| 4 | Minor | **ACCEPT** | The ledger is silent on a departure from frozen test text. D5 and D6 on this branch established that verbatim admits no silent departures. Recording it is the fix; the departures themselves strengthen and stand. |
| 5 | Minor | **ACCEPT** | The close-out paraphrases the verdict instead of naming the label the probe record issues. |
| 6 | Minor | **ACCEPT** | The ledger instructs a backlog item that the backlog diff does not contain. |

No finding refuted. Nothing escalated into the debate as contested; findings
1 and 2 enter the round-1 brief as ACCEPTED, with the proposed replacement
text, so the reviewer lane checks the REPAIRS rather than re-litigating the
diagnosis.
