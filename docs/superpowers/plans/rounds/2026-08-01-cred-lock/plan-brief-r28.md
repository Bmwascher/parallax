Round 28. All three round-27 blockers are applied. Plan header reads revision
27. I contest nothing.

## Task 5 — the contradiction

At `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:406`. The
credentials-probe seam said "no mutation" and then required a release in
`finally`, and a release IS a mutation. It now says no mutation OF THE
CREDENTIALS-PATH OBJECT OR ITS ACL, with the required `finally` release named as
the ONLY lock mutation, transitioning the held record exactly to `free`. The
contradiction is recorded in the sentence so it does not get "simplified" back.

## Task 6 — activation and exit codes

All three new seams now activate on ANY NONEMPTY value, which I had stated for
the Task 5 pair and omitted here:

- `PARALLAX_LANE_HOME_DIRECTORY_PROBE_FAULT` at `:450`, and it now **exits 6**.
  Its table row said only "refuse nonzero", so the exit code genuinely was open.
- `PARALLAX_LANE_HOME_REMOVE_VERIFY_FAULT` at `:475`, exit 6 retained.
- `PARALLAX_LANE_HOME_CLEANUP_DELETE_FAULT` at `:479`, original-build-failure
  code and precedence retained.

## Task 9 — the shipped literal

At `:721`. "The first two are safe to repeat" dated from when the list had three
entries. Inserting the probe FIRST made that ordinal silently drop ACL
application, which Task 5 defines as idempotent. It now reads: all four
interactions are safe to repeat, both probes only read, and directory creation
and ACL application are idempotent.

This is the THIRD consecutive round in which a numeric or ordinal reference in
this one shipped sentence was wrong — a count in r25, a different count in r26,
an ordinal now. Each time the fix was correct and the next edit broke a
different number in the same sentence. The sentence no longer counts or
ordinals at all. I am recording that as the argument for enumerating rather than
counting anywhere a list can grow, because it is the only defect in this debate
that recurred three times in the same place.

## Your STARTTIME_FAULT answer

Recorded in the r27 revision entry with your reason: the injected failure is
deliberately converted into an ordinary `UNMEASURABLE` result that has its own
decisive oracles, so a seam-specific sentinel would describe something the user
never sees. That is a better reason than the one I gave, which was only that the
throw is caught.

## What I want from you

1. Is this a PASS?

2. If PASS, the record finalization is DRAFT to FROZEN at revision 27, rounds
   used 28, and the outcome line. Task 1 first, as you have now confirmed twice.

3. One thing I want on the record before building starts, in your words rather
   than mine. Twenty-seven rounds have found defects at a steady rate, and the
   last several were mostly defects introduced by the previous round's fix. If
   you think that rate says the plan is still substantially unsound, say so
   plainly and I will keep going. If you think it now reflects normal editing
   friction on a large frozen artifact rather than unresolved design risk, say
   that instead. I would rather start building on your stated judgment than on a
   round that happens to come back clean.
