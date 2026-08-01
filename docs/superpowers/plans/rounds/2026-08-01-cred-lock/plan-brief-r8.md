Round 8. Cap still lifted; iterate to PASS. Evidence rules and verdict grammar as before.

Plan r7 is written. Nine of ten tasks you passed in round 7 are UNCHANGED except
where a fix below explicitly touches them, so the review surface is Task 3's one
line, Task 7 in full, and Task 10's one-line addition.

ACCEPTED, all of round 7, no reservation.

TASK 3, the one blocking contradiction. The exhaustive MALFORMED definition now
reads "a record carrying ANY PROPERTY FORBIDDEN FOR ITS STATE, which includes
any unknown property in either state AND any held-only KNOWN property on a free
record", with a sentence saying why that wording and not "unknown field": `host`
on a free record is a KNOWN property, and two definitions of one condition is
two behaviours for an implementer to pick between.

TASK 7, all four:

1. The manual setup sequence is frozen as six numbered steps, run for A then B,
   and it resolves its OWN owner in the setup shell rather than borrowing the
   module's, because `-ResolveOwner` runs once per module run and setup happens
   earlier. Login with all mandatory parameters and a required `ok` verdict,
   fresh setup debate id, acquire with the home as both LaneHome and DebateHome,
   ASCII marker write, release with the captured nonce. A before B is what
   produces A's tick strictly below B's.

2. The secret set now has a lifecycle: seed the retained union under each home's
   lock; after every command, WHILE THAT LOCK IS STILL HELD, re-read the home and
   MERGE new values before scanning; never discard an old value, because a
   rotated-away token is still a secret. The helper owns process capture and
   sanitizes the timeout, launch-failure and error paths, since those are exactly
   the paths a framework prints captured output on. Your point that a set built
   once cannot contain a value the scanned command itself issued is the case C
   exists to produce, and I had missed it.

3. Step 1b adds `evals/multi-model-verify/test_lane_credential_live_support.py`,
   offline, importing the SAME production helper, with your five proofs
   verbatim: pre-held locks under a different live owner proving the fake command
   is never invoked; contention while a fake command blocks and release after
   both zero and nonzero exits; an existing fake credential value injected into
   stdout and separately into stderr; a fake command that ROTATES and emits the
   new value, which a seed-once implementation fails; and failures that name only
   the field, carry no value, and write no probe record. Task 10 adds it to both
   Windows steps and to the parity required set, which is now six modules.

4. The fixture routing table is added: items 1, 2, 3, 4 and 7 use C with fresh
   builder-created debate homes and acquire C's lock; item 5 uses A and B and
   acquires the lock of whichever home is dispatching; item 6 uses isolated
   disposable homes carrying a structurally valid FAKE credential, a garbage one,
   and no credential file, and acquires nothing because no real credential
   exists to protect. Tell me if that last row is wrong - it is the only routing
   decision I made rather than took from your fix.

PLAN RECORD, your nonblocking item: the file is now labelled revision 7 with r6
and r7 history entries and a round count of 7. You were right that r5's label
had stopped tracking reality two rounds earlier.

Same two questions:

1. PASS, if a zero-judgment implementer could now build this without inventing
   anything; or the precise remaining FIXes, each marked BLOCKING or
   acceptable-as-is.
2. Has any round-7 fix been applied wrongly or introduced a new defect? Task 7
   grew by four surfaces this round, which is the largest single-task expansion
   in the whole debate.
