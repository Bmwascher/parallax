Round 6. Cap still lifted; iterate to PASS. Evidence rules and verdict grammar as before.

Plan r5 is written. Re-read docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md.

ACCEPTED, all of round 5, with no reservation. Your two SECURITY findings I
want to name separately, because neither had occurred to me and both would
have shipped into a PUBLIC repo:

- Task 7.2. The probe record commits the client's COMPLETE streams, and I
  wrote a global rule forbidding credential values in logs or commits in the
  same document. There is now an explicit secret guard: before writing
  probe-record.md, compare captured stdout and stderr against every credential
  string value in every fixture home; if one appears, FAIL naming only the
  field, write NOTHING, and keep the value out of pytest output.
- Task 7.3. `assert $before -ne $after` on token values prints BOTH operands
  through pytest's assertion introspection. The comparison now runs through an
  ordinary `if` with `pytest.fail("access_token did not rotate")`, and neither
  value may appear in an assert expression or a failure message.

Everything else applied:

- Task 1: the initial required set is frozen as exactly `test_attestation.py`,
  `test_codex_context_probe.py`, `test_review_mirror.py` and
  `test_kimi_round_evidence.py`, with Task 10 adding its five.
- Task 2: the host-selector refactor and the `os.name != "nt"` guard MOVED
  here out of Task 6, plus a new step 3c that builds `_fake_profile`, runs the
  validator against the credential it wrote, and requires `ok` under each
  host. Task 6 step 2 now says the refactor is already done and not to repeat
  it. Your point stands exactly as you made it: without this, omitting the
  fixture change passed Task 2's own advertised gate.
- Task 3, all three: a FREE record carrying ANY property other than `version`
  and `state` is malformed, worded that way rather than "unknown field",
  because `host` on a free record is a KNOWN property illegal in that state;
  code 5's meaning widened to "nothing applicable to release, or the supplied
  identity or hash did not match"; and your four-step PREPROCESSING order now
  sits before the release table, with foreign-host scoped to `-ForceRelease`
  only, which removes the overlap. Tests cover every foreign-host and mode
  pairing.
- Task 5: scoped to bound invocations with binder code 1 reserved and
  mutation-tested; lock code 5 added; release-failure precedence frozen in
  both directions; and the opposite-direction oracle added - a NONZERO client
  exit leaving a structurally ok credential exits 0, which is what catches an
  implementation that merely propagates the client's code.
- Task 6: `$buildCompleted` is set ONLY after the custody line is emitted,
  with construction and emission inside the guarded try, and a test that a
  failure to emit runs cleanup and RELEASES. Both internal acquires pass
  `-DebateHome` as the resolved `-Path`. The acquire-failure oracle is now a
  REAL held-by-a-different-owner fixture instead of an invented seam. The
  cleanup seam is named `PARALLAX_LANE_HOME_CLEANUP_RELEASE_FAULT`, firing
  only after an original build failure and immediately before cleanup release.
- Task 7: normalization fully frozen with NO fallback - complete normalized
  stderr, fixture root replaced case-insensitively with `<fixture-root>`,
  CRLF to LF, one terminal newline trimmed, run twice, and if the two differ
  STOP and amend the plan rather than let the implementer select a line. C's
  lock identity frozen: `-ResolveOwner` once per module run, resolved home C
  as both `-LaneHome` and `-DebateHome`, one run debate id, nonce captured,
  released with the complete identity.
- Task 8: the seven-step hash algorithm verbatim, and both recovery commands
  written out complete with every Task 3 parameter.
- Task 9: `-LaneHome <lane-home>` added to the login invocation, with the
  reason stated, and the remove command spelled out in full.

Same two questions as last round:

1. PASS, if a zero-judgment implementer could now build this without inventing
   anything; or the precise remaining FIXes, each marked BLOCKING or
   acceptable-as-is.
2. Has any round-5 fix been applied WRONGLY or introduced a new defect? Four
   of them again touched Task 3's partition and Task 6's ordering, which are
   the two places every previous round has found something.
