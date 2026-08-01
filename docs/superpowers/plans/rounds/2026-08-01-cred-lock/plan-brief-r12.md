Round 12. Cap still lifted; iterate to PASS. Evidence rules and verdict grammar as before.

Plan r11 is written. Only Task 7's support-oracle bullets changed. Everything else
is byte-unchanged from what you passed in round 11.

ACCEPTED, both, no reservation. And I took your process answer as given: the
production contract is not cut, the duplicated ORACLE PROSE is.

1. THE IMPOSSIBLE END STATE is gone, replaced by your three-row matrix rather
   than by more prose:

   | Main phases | `-Remove` outcome | Required state and report |
   |---|---|---|
   | pre-command, merge or guard FAILS | succeeds | main failure primary; Remove attempted; home ABSENT; lock `free` |
   | pre-command, merge or guard FAILS | deterministic sentinel refusal | main failure primary; Remove attempted; home PRESENT; original held record BYTE-IDENTICAL |
   | all succeed | deterministic sentinel refusal | Remove failure primary; home PRESENT; original held record BYTE-IDENTICAL |

   with the reason recorded - a sentinel or dangerous-root refusal leaves the home
   present and the record unchanged per Task 6's frozen remove order, and a
   release that fails after deletion leaves the lock not free, because the release
   is what would have freed it. Sentinel repair and a normal `-Remove` are TEARDOWN
   only, after the failure state is asserted. The seed matrix gained the direction
   it never had: a failing read with a SUCCEEDING release, reporting the seed
   failure and leaving the record `free`, alongside the failing-release case that
   pins the state its deterministic fault produces and the successful-read case.

2. "EVERY FAILURE NAMES ONLY THE FIELD" is narrowed to every CREDENTIAL-MATCH
   failure from the secret guard, with the contradiction named: the launch-failure
   and read-or-parse cases have no matched field. The timeout, launch,
   read-or-parse, phase and cleanup failures keep their own individually specified
   sanitized messages, and I added that none of them may carry a credential value
   or a captured stream either, since that property is the whole point and was
   previously riding on the sentence being narrowed.

PLAN RECORD: revision 11, r11 history entry, eleven rounds.

Same two questions:

1. PASS, if a zero-judgment implementer could now build this without inventing
   anything; or the precise remaining FIXes, each marked BLOCKING or
   acceptable-as-is.
2. Has any round-11 fix been applied wrongly or introduced a new defect?
