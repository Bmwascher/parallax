Round 7. Cap still lifted; iterate to PASS. Evidence rules and verdict grammar as before.

Plan r6 is written. Re-read docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md.

ACCEPTED, all of round 6, no reservation. Applied:

- Task 2: opposite-direction duplicate-key oracles added - invalid first with
  valid last must be `ok`, valid first with invalid last must report the LAST
  value's precise defect, both hosts. You are right that without them an
  implementation rejecting duplicates, or keeping the first, passes everything
  else.
- Task 3, all three: preprocessing is now headed "for MUTATING FILE MODES ONLY
  - Acquire, Release, ForceRelease and MalformedOverride", and states that
  Status follows its own read-only rule and ResolveOwner performs no lock-file
  operation. The wait/poll sentence now reads "every LOCK-FILE mode accepts
  both, Status included; ResolveOwner accepts neither". Exit code 4 is scoped
  "MUTATING FILE MODES ONLY ... Status never emits it".
- Task 5: code 3 widened to "lock contention: the exclusive handle OR a live
  holder, since a preserved lock code 3 covers both".
- Task 6: the seam is MOVED. `PARALLAX_LANE_HOME_FAULT` now fires immediately
  after custody JSON construction and immediately before emission, with the
  reason stated - a pre-render fault cannot distinguish an implementation
  setting `$buildCompleted` after rendering from one setting it after
  emission. Its test requires no stdout, the home gone, and the lock exactly
  `free`. The stale selector ownership is removed from the file list, which
  now says the selector and guard belong to Task 2.
- Task 7, all three: the guard is restricted to every NONEMPTY credential
  string value, with the reason - `scope` and `token_type` are optional and
  unconstrained and an empty string is a substring of every output. The guard
  is now ONE HELPER applied to EVERY live command, running BEFORE any
  assertion or failure message that could surface a captured stream, with
  probe-record.md using the same helper; your point that a conventional pytest
  failure message prints streams before any write-time guard is the half I had
  missed entirely. And locking is now PER HOME: resolve the owner once per
  module, then acquire that home's own lock before EVERY authenticated command
  against A, B or C, with A and B's setup markers written under their own
  locks too. The role sentence is narrowed to "C is the only home the suite
  DELIBERATELY expires and requires to rotate", with A and B free to refresh
  naturally but only while locked, and the 900-second lifetime cited as why.
- Task 8: the provenance sentence corrected - every CONFIRMATION placeholder
  comes from Status; `<lane-home>` is the configured lane home status was
  requested against.
- Task 9: the status instruction is now the complete
  `tools/kimi-lane-lock.ps1 -Status -LaneHome <lane-home>`.

Tasks 1, 4 and 10 you have passed twice. I have not touched them.

Same two questions:

1. PASS, if a zero-judgment implementer could now build this without inventing
   anything; or the precise remaining FIXes, each marked BLOCKING or
   acceptable-as-is.
2. Has any round-6 fix been applied wrongly or introduced a new defect? Task 3's
   mode scoping and Task 7's locking were the two largest edits and both touch
   text you had already passed in adjacent paragraphs.
