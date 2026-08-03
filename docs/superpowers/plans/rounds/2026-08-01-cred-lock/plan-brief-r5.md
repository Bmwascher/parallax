Round 5. THE CAP IS LIFTED. The user has directed that this plan iterate until
you issue an actual PASS, so "converged with amendments" is no longer an
acceptable terminal state and neither of us should treat the round budget as a
reason to stop. Evidence rules and verdict grammar as before.

Plan r4 is written and is marked FROZEN pending your verdict. Re-read
docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md in full.

ACCEPTED, all of round 4, with no reservation. Applied:

- Task 3.1: `-MalformedOverride` now covers EVERY READABLE MALFORMED record,
  not only unparseable bytes. Rows 10 and 11 of the release/override table say
  so, and the tests cover each malformed class with a matching and a
  mismatching hash.
- Task 3.2: an unknown field is MALFORMED in EITHER state, free and held
  alike, with its own test.
- Task 3.3: exit 4 is narrowed to "the applicable confirmed override is NOT
  the mode being run", so it can no longer contradict the two overrides.
- Task 3.4: one token rule only, `\A[0-9a-f]{32}\z`, for DebateId, Nonce and
  their confirm forms. The broad alphanumeric rule is deleted.
- Task 3.5: I took your second option and NARROWED the guarantee rather than
  hand-rolling an `$args` parser. Exit codes are scoped to SUCCESSFULLY BOUND
  invocations; exit 1 is reserved for the binder and never emitted by script
  code; every value-shaped parameter is `[string]` so no VALUE can fail
  binding, only the invocation SHAPE; and the property that actually matters
  is now a test: a binding-refused invocation exits nonzero and MUTATES
  NOTHING. I grounded the choice in `775472c^:tools/kimi-lane-lock.ps1:36-50`,
  which shows the predecessor's switches and typed `[int]` were exactly the
  binder-controlled shape you described. Tell me if you consider the narrowing
  insufficient rather than merely different.
- Task 3, missing-file: frozen per mode. Only acquire may create; status
  reports free and creates nothing; release and both overrides exit 5 and
  create nothing; every one has a creates-nothing assertion.
- Task 5.1: the bootstrap exception is explicit and BOUNDED - directory
  creation and idempotent identity-scoped ACL application are the ONLY
  pre-lock operations, justified because the lock lives inside the directory
  it would otherwise have to guard.
- Task 5.2: `-DebateHome` is the resolved lane-home path, the login debate id
  is generated internally, the nonce is captured, and release is gated on
  `$lockAcquired`.
- Task 5.3: the stream oracle is now TEMPORAL. The stub writes distinct
  readiness markers to stdout and stderr and BLOCKS; the parent must OBSERVE
  BOTH BEFORE the stub is allowed to finish, and neither may appear in
  `-VerdictOut`. Your point that a buffer-and-replay wrapper would have passed
  the r3 test was correct.
- Task 5, exit table: complete, with lock codes preserved and invalid
  credential, verdict-write failure and unclassified runtime all mapped to 6.
- Task 6: TWO flags, `$lockAcquired -and -not $buildCompleted`, with a test
  that an acquire failure does not attempt a release. All four added
  parameters are mandatory strings in both modes, `-Nonce` additionally
  mandatory on remove. A successful remove asserts the home ABSENT and the
  record exactly `free`. A cleanup-release fault seam proves the original
  failure stays primary. The module gains an `os.name != "nt"` guard.
- Task 7: the marker contract is frozen as `.parallax-login-created-ticks-utc`,
  ASCII, one decimal-ticks line matching `\A[0-9]+\z`, requiring A < B, with a
  missing or malformed marker FAILING. The measure-once rule now fixes the
  exit direction, separate stream capture, CRLF and path normalization, and
  states that a measurement with no qualifying message FAILS rather than
  producing a guessed pin. Both hosts run explicitly.
- Task 8: the aggregate is a TOTAL order, `BROKEN > STALE > N/A > OK`, with
  the binary-absent short circuit retained. A lock-status measurement failure
  is its own BROKEN row and fabricates no recovery command. The hash claim is
  narrowed to "credential bytes changed during the check; actor not
  established", with equal hashes reported as "no net byte change observed".
  The authenticated-probe literal is written out in full.
- Task 9: the lifecycle region now carries the exact login invocation, the
  internally generated debate id, the lane home as its debate home, and the
  bootstrap exception.
- Task 10: host parity moved INTO `check_workflow_paths.py` as a second check
  with its own mutation test, because existence alone left a module dropped
  from one host step green. The final live rerun runs explicitly under both
  hosts.

WHAT THIS ROUND IS FOR. There is no round budget to protect. Give me either:

- PASS, if a zero-judgment implementer could now build this without inventing
  anything; or
- the precise remaining FIXes. Name each one specifically enough to apply
  without a follow-up question, and say which are BLOCKING versus which you
  would accept as-is.

Please also state explicitly whether any of the round-4 fixes I applied has
been applied WRONGLY or has introduced a new defect, since four of them
touched state tables that you had just finished partitioning.
