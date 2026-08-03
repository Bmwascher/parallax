Round 10. Cap still lifted; iterate to PASS. Evidence rules and verdict grammar as before.

Plan r9 is written. Only Task 7 and the plan record changed. Tasks 1 through 6 and
8 through 10 are byte-unchanged from what you passed in round 9.

ACCEPTED, all three blocking items and the nonblocking one, no reservation.

1. FAILURE BOUNDARY. `custodyReceived` is set ONLY after Build exits 0 AND its
   exact JSON line parses. Steps 3 through 6 - pre-command, command, merge and
   guard, and `-Remove` - run ONLY when it is set. On a refused or failed Build
   the runner invokes NEITHER the command NOR `-Remove`, and preserves the Build
   failure, because Task 6 already owns that cleanup and has already released.
   I named my own error in the text: r8's blanket "`finally` always calls
   `-Remove`" would have called removal with no nonce against a lock the builder
   had already freed. Item 4's routing row is split into 4a successful-build with
   the real `-Remove`, and 4b failed-build with the builder's internal cleanup and
   no `-Remove` call. Cleanup precedence is frozen both ways: a command or guard
   failure stays primary even when `-Remove` also fails, and a `-Remove` failure
   is primary only after main success.

2. SEED LIFECYCLE. Seeding now happens BEFORE any live command through an
   explicit direct-acquire lifecycle - for A, then B, then C: acquire with the
   module owner and that home as both LaneHome and DebateHome, read and merge,
   release with the captured nonce in a `finally`. It is named as THE ONLY place
   in the suite that acquires directly, with builder custody everywhere else, and
   item 6's disposable homes stated as the exception to that exception. The
   offline oracles now include a pre-held seed home preventing its credential read
   and a successful seed leaving that record exactly `free`.

3. PRE-COMMAND PHASE. Step 3 of the custody sequence is now an explicit
   PRE-COMMAND phase, existing only under `custodyReceived`, where every
   deliberate credential mutation and every pre-command hash happens while the
   builder's hold is in force. I stated the failure it closes: without it an
   implementation could force expiry BEFORE the build, mutate a shared credential
   unlocked, and still pass every functional assertion. Items 3 and 7 now both say
   "force expiry IN THE PRE-COMMAND PHASE", and item 7 also takes its pre-command
   hash there. The contention oracle is extended so a second acquire must contend
   DURING THE PRE-COMMAND PHASE as well as during the client process, since
   custody is held the whole time and not only while the client runs.

   I also added the two cleanup-precedence oracles and the byte-identical
   pre-held-record assertion you asked for, and the pre-held oracle now asserts
   `-Remove` is never attempted.

4. PLAN RECORD. The file is revision 9, with r8 and r9 history entries and a round
   count of 9. You caught the label drifting twice now; it is correct as of this
   submission.

Same two questions:

1. PASS, if a zero-judgment implementer could now build this without inventing
   anything; or the precise remaining FIXes, each marked BLOCKING or
   acceptable-as-is.
2. Has any round-9 fix been applied wrongly or introduced a new defect? The
   custody sequence has now been rewritten in three consecutive rounds, which
   makes it the least settled text in the plan even though each individual change
   was yours.
