Round 13. Cap still lifted; iterate to PASS. Evidence rules and verdict grammar as before.

Plan r12 is written. Two edits, both exactly as you specified, nothing else touched.

1. The general cleanup rule now reads, verbatim from your fix: "a failure in any
   main phase still ATTEMPTS the real `-Remove`. When Remove succeeds, the debate
   home is ABSENT and the lock is exactly `free`; when Remove fails, the required
   report and filesystem state are those in the support matrix below."

2. Both matrix failure rows now read "pre-command, command/capture, merge or guard
   FAILS". You were right that the production definition named four main phases
   while the matrix covered three, so a simultaneous Remove failure could have
   masked a command or capture failure with nothing to catch it.

No behaviour added, none cut. Plan record: revision 12, r12 history entry, twelve
rounds.

Same two questions:

1. PASS, if a zero-judgment implementer could now build this without inventing
   anything; or the precise remaining FIXes, each marked BLOCKING or
   acceptable-as-is.
2. Has either round-12 edit been applied wrongly?
