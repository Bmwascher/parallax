Not PASS. The round-9 custody structure is coherent, but Task 7 still lacks oracles for several failure paths inside that custody and retains one item-6 wording conflict.

### Task 1

Byte-unchanged from the passed revision. The six-module count remains consistent with Task 10. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:79-94`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:563-568`.

Verdict: PASS.

### Task 2

Byte-unchanged from the passed revision. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:98-129`.

Verdict: PASS.

### Task 3

Byte-unchanged from the passed revision. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:134-253`.

Verdict: PASS.

### Task 4

Byte-unchanged from the passed revision. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:258-279`.

Verdict: PASS.

### Task 5

Byte-unchanged from the passed revision. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:283-319`.

Verdict: PASS.

### Task 6

Byte-unchanged from the passed revision. Its build-success, failed-build, and removal ownership boundaries remain complete. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:324-364`.

Verdict: PASS.

### Task 7

Three blocking fixes remain.

1. **Cleanup coverage and precedence do not include every phase now inside custody.**

   Steps 3–5 contain the pre-command mutation/hash phase, command execution, post-command credential merge, and secret guard; `-Remove` runs in `finally`. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:405-418`. But the precedence rule and support oracle cover only command failure and guard failure in prose, and only command failure in the combined Remove-failure oracle. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:418`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:459-464`.

   A runner can therefore mishandle a pre-command failure, post-command reread/merge failure, or guard failure—skipping Remove or allowing Remove failure to mask the original—and still pass the listed support tests.

   Required fix:

   - Define the “main operation” as pre-command, command/capture, post-command reread/merge, and guard.
   - Require real `-Remove` after failure in every one of those phases, asserting debate home absent and lock exactly free.
   - State that failure from any main phase remains primary if Remove also fails.
   - Add combined oracles for at least pre-command failure plus Remove failure, merge failure plus Remove failure, and guard failure plus Remove failure. The existing command-success/Remove-failure oracle remains the opposite direction.
   - Apply the same rule to seed cleanup: seed-read failure remains primary if release fails; release failure is primary only after a successful seed read.

2. **The claimed timeout, launch-failure, and error sanitization has no oracle.**

   The helper promises to sanitize timeout, launch-failure, and error paths before captured streams can be rendered. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:428-439`. Current support tests cover ordinary stdout, ordinary stderr, and a normally returning command that rotates and emits a token, but none exercises the exception paths the promise specifically names. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:455-464`.

   Required fix:

   - A fake command emits a fake credential value and then blocks until timeout; require a field-only failure containing neither value nor captured stream, no probe record, and successful Remove cleanup.
   - A nonexistent executable exercises launch failure; require a sanitized failure and successful Remove cleanup.
   - A post-command credential-read/parse fault exercises the merge-error path; require a value-free failure and successful Remove cleanup.

3. **Item 6 still conflicts with the universal post-command rule.**

   Item 6 explicitly has no hold, and its values are loaded and merged without a lock. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:400`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:434-435`. The immediately following rule nevertheless says that after *every* command the home is reread while its hold remains in force. Item 6 has no such hold. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:436`.

   Required fix: scope line 436 to builder-custodied A/B/C commands, then state separately that item-6 disposable homes are reread and merged after their command without a lock before the same stream guard runs.

The round-9 failure split itself is correct: nonzero Build invokes neither command nor Remove, while successful parsed custody enters the guarded sequence. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:397-418`. The pre-command placement and direct seed lifecycle are also correct on their success paths. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:411`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:432-437`.

Verdict: FIX — BLOCKING: complete the cleanup/precedence matrix, add exception-path sanitization oracles, and scope item 6’s post-command merge explicitly.

### Task 8

Byte-unchanged from the passed revision. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:478-528`.

Verdict: PASS.

### Task 9

Byte-unchanged from the passed revision. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:532-559`.

Verdict: PASS.

### Task 10

Byte-unchanged from the passed revision. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:563-585`.

Verdict: PASS.

### Plan record

Revision 9, the r8/r9 history entries, and nine completed rounds are now mutually consistent. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:5-23`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:589-599`.

Verdict: PASS.

## Overall verdict

FIX.

All four submitted round-9 changes were applied correctly on their named paths. The remaining defects are Task 7 oracle and partition gaps:

- cleanup after pre-command, merge, and guard failures;
- timeout/launch/error sanitization;
- item 6’s impossible “while held” post-command wording.

## Final check

- **UNVERIFIED:** Measurements 1–21 remain external measurements assigned to live gates by the design. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:35-67`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:348-364`.
- **UNVERIFIED:** Task 7’s three planned files do not yet exist, so none of the new custody or sanitization oracles can presently be executed. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:369-373`.

