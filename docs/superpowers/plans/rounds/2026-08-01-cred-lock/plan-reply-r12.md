Not PASS. The matrix’s state decisions are now correct, but it conflicts with one retained cleanup sentence and omits command/capture failure from its Remove-failure rows.

### Tasks 1–6

Byte-unchanged from their passed revisions. Task 6 still establishes that a sentinel refusal leaves the debate home present and the held record unchanged. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:69-368`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:350-360`.

Verdict: PASS.

### Task 7

Two blocking textual/oracle corrections remain.

1. **The general cleanup rule still contradicts the new matrix.**

   The retained rule says that after a failure in any main phase, the assertions are “the same in every case”: home absent and lock free. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:420-423`. The new matrix correctly says a sentinel-refused Remove leaves the home present and held record byte-identical. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:469-477`.

   Required fix: change line 422 to:

   > A failure in any main phase still ATTEMPTS the real `-Remove`. When Remove succeeds, the debate home is ABSENT and the lock is exactly `free`; when Remove fails, the required report and filesystem state are those in the support matrix below.

2. **The matrix omits command/capture failure from the combined precedence oracle.**

   The production definition makes command and capture one of the four main phases. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:420-425`. But the matrix’s failure rows name only pre-command, merge, and guard. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:471-475`. The separate nonzero-command test proves cleanup when Remove succeeds; it does not prove that a simultaneous Remove failure cannot mask a command/capture failure. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:468`.

   Required fix: change both matrix failure rows to “pre-command, command/capture, merge or guard FAILS.” No new row or prose is needed.

The seed matrix is now complete, and the sanitization rule is correctly narrowed to credential-match failures while other failures retain sanitized class-specific messages. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:479-483`.

Verdict: FIX — BLOCKING: scope the general cleanup assertion by Remove outcome and add command/capture to both failure rows.

### Tasks 8–10

Byte-unchanged from their passed revisions. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:496-604`.

Verdict: PASS.

### Plan record

Revision 11 and eleven completed rounds are consistent. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:5-25`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:608-618`.

Verdict: PASS.

## Overall verdict

FIX.

The round-11 matrix and sanitization decisions were applied correctly. The remaining issue is mechanical: one old sentence was not narrowed to agree with the matrix, and the matrix accidentally dropped one already-defined main phase. No feature behavior should be added or cut.

## Final check

- **UNVERIFIED:** Measurements 1–21 remain external measurements assigned to live gates. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:35-67`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:348-364`.
- **UNVERIFIED:** Task 7’s planned files do not yet exist, so its support matrix cannot presently be executed. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:371-375`.

