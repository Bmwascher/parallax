Round 4. This is the round CAP. Evidence rules and verdict grammar as before.

Plan r3 is written. Re-read docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md
in full.

ACCEPTED, all of round 3, with no reservation. The four cross-task
contradictions are the class a per-task read cannot catch and all four were
real:

- Task 3's acquire table overlapped rows 3/4/5 and claimed completeness over
  states it never covered. Rows 4 and 5 are now scoped to NON-NONCE fields,
  and the table is explicitly scoped to readable, well-formed, same-host
  records, with foreign-host, malformed, unreadable and handle-contention
  decided before it.
- Task 8 promised a foreign-host override Task 3 forbade. `-ForceRelease`
  now carries `-ConfirmHost` and may free an exactly-confirmed foreign-host
  record; that is the only mutation permitted on one.
- Task 5's inherited interactive child could not coexist with a JSON-only
  stdout. The verdict moved to a mandatory `-VerdictOut` file and the child's
  streams are untouched. The test stub now emits on both streams.
- Task 7 forbade creating login B while its own oracle required creating it.
  The suite is now three pre-provisioned homes with assigned roles, and the
  coexistence claim is NARROWED in the test's own docstring to "A remains
  usable after B was created", which is what a pre-provisioned fixture can
  actually support.

Also fixed: release and override state tables for non-held records; every
parameter declared `[string]` and parsed manually, so binding cannot produce
an undocumented exit 1; the conditional `$buildCompleted` cleanup, because an
unconditional `finally` released a SUCCESSFUL build's lock; unknown fields in
a held record are MALFORMED; the crash oracle is synchronized through a
signal file with a blocking child and asserts exactly zero bytes, plus a
partial-prefix fixture; validation edges frozen; status wording corrected to
"every READABLE file state"; the three literals' overclaims amended; the
history check made to throw; and DebateId custody defined.

I verified your Task 9.5 finding directly rather than taking it:
`evals/multi-model-verify/test_contract_coverage.py:21-30` shows
`parse_regions` collapsing whitespace, `:517-520` shows `collect_pins` doing
the same, and `:523-526` shows coverage is a SUBSTRING test. My raw-byte
length-and-hash comparison could never have passed. Step 5 now compares
normalized runtime values and says explicitly that raw-byte comparison is
the wrong equality.

WHAT THIS ROUND IS FOR. Under the cap, an accepted FIX is agreement and
freezes the plan; only a genuine deadlock goes to the user. So:

1. Are the two new state tables in Task 3 now a correct PARTITION - every
   reachable record class landing in exactly one row, with nothing
   overlapping and nothing missing?
2. Does `-ConfirmHost` actually close the Task 3 / Task 8 contradiction, or
   does permitting one mutation on a foreign-host record reopen something?
3. Did r3 introduce anything r2 did not have? The conditional cleanup, the
   `-VerdictOut` file, the three-home fixture and the measure-once-then-pin
   rule for the absolute-key message are all new surfaces.
4. Anything remaining that a zero-judgment implementer would have to invent.

If your answer is PASS, say so plainly and the plan freezes here. If you have
FIXes you consider necessary, name them precisely enough that I can apply
them without another round, because there is no round 5.
