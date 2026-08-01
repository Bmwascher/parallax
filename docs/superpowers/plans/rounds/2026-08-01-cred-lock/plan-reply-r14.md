The two judgment calls are sound, but r13 is not yet a PASS. Four tasks need blocking corrections.

### Task 1

The workflow-path and six-module host-parity requirements remain complete and failure-capable. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:83-98,604-605`

PASS

### Task 2

The validator still has a complete defect precedence and opposite-direction duplicate-key oracles under both hosts. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:108-133`

PASS

### Task 3

Four blocking corrections remain:

1. `debateHome` is declared “not part of the comparison,” but the next table requires comparing it to select idempotent success versus exit 2. Replace that sentence with: “`debateHome` is excluded from holder-identity equality but compared separately after all five identity fields match.” `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:193-206`

2. Its equality rule is unspecified. The plan freezes case-insensitive hostname comparison and string tick comparison, but supplies no normalization or comparer for `debateHome`. Require every caller to normalize it with one stated algorithm—e.g. absolute `GetFullPath`, normalized trailing separator, then ordinal case-insensitive comparison—and test equivalent spellings plus a genuinely different path. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:64-69,195-206`

3. The liveness rules introduce `UNMEASURABLE`, but the Acquire table and exit-code definition cover only `LIVE`. State explicitly that same-host `UNMEASURABLE` records follow every non-DEAD/LIVE Acquire row: exact identity is idempotent; any competing identity contends; neither reclaims. Update code 3 accordingly and test both directions through the fault seam. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:173-180,199-208,241-245`

4. A foreign-host record has no specified Status liveness. The design says its liveness cannot be checked locally, while Status requires a liveness value. Freeze foreign-host Status as `UNKNOWN` without consulting the coincidentally matching local PID, and add that oracle. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:256-273`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:249-257`

Also change the stale “Rows 4 and 5” rationale to “Rows 5 and 6”; after the split, row 4 is the `debateHome` refusal. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:201-210`

FIX — BLOCKING: clarify separate normalized `debateHome` comparison, route `UNMEASURABLE` through Acquire, define foreign-host Status as `UNKNOWN`, and correct the row reference.

### Task 4

The unchanged crash and partial-write oracles still exercise the implemented lock path and require malformed refusal rather than reclamation. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:271-292`

PASS

### Task 5

The validator is now named explicitly, and the lock, verdict, stream, and release ordering remains determinate. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:309-327`

PASS

### Task 6

Two new behaviours lack adequate integration oracles:

1. Remove promises that a wrong `-Path` becomes a `debateHome` mismatch and exits 2, but the test list only says “identity mismatch”—and Task 3 now expressly excludes `debateHome` from identity. Add an explicit test: build home A; prepare a distinct, valid disposable home B; call Remove on B using A’s five identity fields and nonce; require exit 2, no deletion, and byte-identical lock and homes. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:193-195,361-365,373`

2. The new post-deletion release precedence has no failure-capable test. Add a deterministic Remove-only seam immediately after deletion and before release that makes the internal release return a fixed code 5. Require: home absent, original held record unchanged, exit 5, failure on stderr, and no `removed <path>` stdout. Release directly during teardown. The current Task 7 failure matrix exercises pre-deletion sentinel refusal, not this branch. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:365,373,486-494`

FIX — BLOCKING: add the wrong-`-Path` integration oracle and deterministic post-delete release-failure oracle.

### Task 7

C cannot use “the SAME six steps” while writing no marker, because step 5 is precisely “Write the ASCII marker.” Replace this with: “For C, run steps 1–4 and 6, explicitly omitting step 5.” `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:394-405`

The three-login statement is correctly labelled a generalization with a loud refusal direction rather than presented as measured fact. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:390,407`

FIX — BLOCKING: specify C as steps 1–4 and 6, not the same six steps.

### Task 8

The `UNKNOWN → N/A` behavior and the new case-insensitive foreign-host comparison are specified, but the verification instruction only generically says to pin “lock-status reporting.” An implementation mapping `UNKNOWN` incorrectly or comparing hosts case-sensitively could satisfy a narrower interpretation. Add explicit pins for both new behaviors, including the required UNKNOWN detail and complete foreign-host recovery command. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:518-536,550-563`

FIX — BLOCKING: explicitly pin the UNKNOWN verdict/detail and case-insensitive foreign-host branch.

### Task 9

The revised isolation literal clearly separates persistent lane home from throwaway debate home. All three literals remain single regions, contain no backslashes, and have normalized whole-region pinning instructions. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:571-596`

PASS

### Task 10

The final wiring still names all six offline dual-host modules and reruns the live suite explicitly under both hosts. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:600-615`

PASS

## Answers

1. **Not PASS yet.** Tasks 3, 6, 7, and 8 require the blocking fixes above. Nothing listed is acceptable as-is under the zero-judgment contract.

2. The underlying r13 decisions do not contradict the settled design: the design names exactly five identity components and lists debate-home path separately; it also says unevaluable liveness remains held. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:211-215,256-273`  
   The defects are in the newly written execution detail and oracle coverage: contradictory comparison wording, incomplete liveness routing, missing tests, and C’s impossible setup instruction.

3. I agree with both judgments:

   - **`debateHome` mismatch → exit 2:** yes. Matching all five holder-identity fields means there is no competing holder, so contention would be false; the differing path is caller confusion. This fits code 2’s parameter-refusal meaning. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:173-177,193-206`
   - **same-host UNKNOWN liveness → `N/A`:** yes. It cannot be `STALE`, because staleness requires proof that the owner is gone; it should not be `BROKEN`, because Status successfully reported the protocol’s deliberate fail-closed outcome. `N/A` records that the liveness subcheck cannot apply while avoiding a false `OK`. `commands/doctor.md:5-9`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:256-273`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:530-536`

## Overall verdict

**FIX.** The design choices stand, but r13 cannot refreeze until the four blocking task fixes are applied and re-reviewed.

## Final check

- **UNVERIFIED:** Measurements 1–21 as experiments. The design itself says measurements taken outside the repository cannot be verified by its offline suite. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:348-351`
- **UNVERIFIED:** The three-login generalization beyond measurement 11. It is correctly disclosed and fails closed, but has not been established by repository evidence. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:403-407`
- **UNVERIFIED:** The reported fable-reviewer execution and “no Criticals”; no review artifact was identified for direct inspection. The plan records the report, but that is not independent verification. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:13-15`
- **UNVERIFIED:** All planned pytest, live, and dual-host gates. No implementation exists, and the stated sandbox has no `python`; this is not a finding.

