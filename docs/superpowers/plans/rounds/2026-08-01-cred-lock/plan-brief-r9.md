Round 9. Cap still lifted; iterate to PASS. Evidence rules and verdict grammar as before.

Plan r8 is written. Every task except 1, 7 and 10 is byte-unchanged from what you
passed in round 8.

ACCEPTED, all five blocking items, no reservation.

1. Task 1 now says Task 10 adds its SIX named modules.

2. Task 7.1, and this one was mine to own. I wrote a routing table that told the
   runner to acquire before every command and release in its own `finally`,
   against a builder that Task 6 deliberately makes RETAIN its acquisition and
   return the nonce. The second acquire would have contended with the retained
   hold and the plain release would have broken `-Remove`'s identity
   confirmation. Fixed as you specified: THE BUILDER IS THE ACQUISITION. Pass
   the module owner and the per-home debate id to Build, retain its nonce, run
   the command under that existing hold, merge and guard while the hold is still
   in force, and in `finally` call the real `-Remove` with that nonce, which
   releases. No second acquire and no plain release anywhere. The routing table's
   last column is renamed Custody and every row now reads "build holds X;
   `-Remove` releases". The support oracles are amended to match: a pre-held lock
   must make the BUILD refuse with the fake command never invoked, and contention
   is observed against the BUILDER-RETAINED hold, with cleanup after both zero and
   nonzero exits proved THROUGH `-Remove`, asserting the debate home absent and
   the lock exactly `free`.

3. Task 7.2: the shared helper now has its own declared file,
   `evals/tools/lane_credential_live_support.py`, added to Task 7's file list,
   imported by BOTH test modules, and required to perform no live-environment
   check at import time so the offline support suite does not drag live setup in.

4. Task 7.3: both of Task 7's host commands now collect
   `test_lane_credential_live_support.py` alongside the live module, with the
   reason stated.

5. The item-6 exception is now explicit inside the secret-set lifecycle: A, B and
   C are seeded and re-read while their hold is in force, while item 6's
   disposable homes are loaded and merged WITHOUT a lock because they are
   isolated, disposable, and contain no real shared credential. All values,
   locked and unlocked alike, still pass the same stream guard. I also changed
   "while that home's lock is held" to "while that home's hold is in force"
   throughout, since after fix 2 the hold comes from the builder rather than from
   a separate acquire.

Same two questions:

1. PASS, if a zero-judgment implementer could now build this without inventing
   anything; or the precise remaining FIXes, each marked BLOCKING or
   acceptable-as-is.
2. Has any round-8 fix been applied wrongly or introduced a new defect? Fix 2
   changed the custody model for six of seven live items and rewrote two support
   oracles, so it is the most likely place for a new one.
