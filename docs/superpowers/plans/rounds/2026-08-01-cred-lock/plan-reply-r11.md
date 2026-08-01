Not PASS. The production custody state machine now stands, but two contradictions remain inside the newly expanded support-oracle text.

### Task 1

Byte-unchanged from the passed revision. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:69-96`.

Verdict: PASS.

### Task 2

Byte-unchanged from the passed revision. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:98-131`.

Verdict: PASS.

### Task 3

Byte-unchanged from the passed revision. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:134-255`.

Verdict: PASS.

### Task 4

Byte-unchanged from the passed revision. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:258-281`.

Verdict: PASS.

### Task 5

Byte-unchanged from the passed revision. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:283-322`.

Verdict: PASS.

### Task 6

Byte-unchanged from the passed revision. Its frozen Remove behavior supplies the decisive evidence for the Task 7 finding below: a sentinel/root refusal leaves both home and held lock unchanged, while a successful Remove deletes before releasing. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:349-359`.

Verdict: PASS.

### Task 7

Two blocking fixes remain.

1. **The combined Remove-failure oracle demands an impossible final state.**

   The plan correctly says any main-phase failure must still attempt Remove and remain primary if Remove also fails. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:419-425`. But the support oracle then combines a main-phase failure with a Remove failure while also requiring the home absent and lock exactly free. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:467-469`.

   Those outcomes cannot coexist:

   - A deterministic Remove refusal at the sentinel/root guard leaves the home and held lock unchanged. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:349-351`.
   - A failure of the final release can occur after deletion, but the lock is then not free because release failed. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:349-351`.

   Required fix: replace the current combined bullet with a parameterized matrix, not more prose:

   | Main phase | Remove outcome | Required state and report |
   |---|---|---|
   | pre-command, merge, or guard fails | Remove succeeds | main failure primary; Remove attempted; home absent; lock free |
   | pre-command, merge, or guard fails | deterministic sentinel refusal | main failure primary; Remove attempted; home present; original held record byte-identical |
   | all main phases succeed | deterministic sentinel refusal | Remove failure primary; home present; original held record byte-identical |

   Repair the sentinel and perform normal Remove only as test teardown after asserting the failure state.

   The seed matrix needs the corresponding missing successful-cleanup direction: seed read fails, Release succeeds, seed failure remains primary, and the record is free. For a combined seed-read/Release failure, assert that Release was attempted and pin the record state produced by the chosen deterministic fault. The present two seed cases do not prove release after a failing seed read. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:465`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:469`.

2. **“Every failure names only the field” contradicts the new exception oracles.**

   The launch-failure case requires a sanitized launch error, and the post-command read/parse case requires a value-free credential-state failure; neither necessarily has a matched credential field. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:470`. The following bullet nevertheless requires *every failure* to name only a field. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:473`.

   Required fix: narrow line 473 to “every credential-match/secret-guard failure names only the matched field.” Timeout, launch, read/parse, phase, and cleanup failures retain their individually specified sanitized messages.

The round-10 production rules themselves are correct: all four main phases are inside custody, every phase reaches Remove, precedence covers every main phase, seed precedence is declared, and item 6 now has a separate unlocked post-command reread. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:419-446`.

Verdict: FIX — BLOCKING: replace the impossible Remove-failure assertion with a state-aware matrix, add the missing seed-read/successful-release oracle, and narrow “every failure” to secret-guard failures.

### Task 8

Byte-unchanged from the passed revision. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:487-528`.

Verdict: PASS.

### Task 9

Byte-unchanged from the passed revision. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:532-559`.

Verdict: PASS.

### Task 10

Byte-unchanged from the passed revision. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:563-585`.

Verdict: PASS.

### Plan record

Revision 10, its history entry, and ten completed rounds are consistent. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:5-24`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:600-608`.

Verdict: PASS.

## Overall verdict

FIX.

The state machine is converging rather than growing uncontrolled production surface. I would not cut the seed, custody, guard, or cleanup behavior. I would cut duplicated oracle prose by replacing the affected bullets with the small outcome matrix above. The remaining problems are contradictions in test expectations, not additional feature behavior.

The round-10 fixes were applied correctly to the production contract. The new defects are confined to the support-oracle wording introduced alongside them.

## Final check

- **UNVERIFIED:** Measurements 1–21 remain external measurements assigned to live gates. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:35-67`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:348-364`.
- **UNVERIFIED:** Task 7’s three planned files do not yet exist, so its support matrix and exception gates cannot presently be executed. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:370-374`.

