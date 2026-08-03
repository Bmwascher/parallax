Round 3. Evidence rules and verdict grammar as before.

<corrections>
CLAIM 12 IS CORRECTED ON THE RECORD. You were right and I was wider than my
evidence. I have now measured it (measurement 17, this session, kimi-code
0.31.1, against the disposable lane login and never the user's):

  With `expires_at` forced to a past value, `kimi.exe provider list` under
  that home exited 0, printed `managed:kimi-code type=kimi models=4
  source=oauth`, and left the credential file BYTE-IDENTICAL: same SHA-256,
  same length 1478, same mtime to the tick, and `expires_at` still holding
  the forced past value.

So `provider list` is NOT a refresh path on this client version, and the
doctor cannot retire a refresh token through it. Claim 12 narrows to exactly
what you said it was: an unnecessary-copy surface and a stranded-secret
surface. Your FIX still stands on that narrower basis, and P3 is unaffected.

Method note, because it nearly went the other way: my first attempt printed
a verdict of "did not write" that was produced by two EMPTY strings
comparing equal, because the hash call failed silently under a permissive
error preference. I discarded that run and re-ran with the hash failure made
fatal. The result above is from the second run. Reporting it because a
measurement that cannot fail loudly is the exact class this repo's invariant
is about, and I generated one.
</corrections>

<new-evidence>
MEASUREMENT 18, closing your third UNVERIFIED item. The kimi-code 0.31.1
credential JSON carries exactly six keys. Field names and types only; no
values were read out or recorded:

  access_token    string
  refresh_token   string
  expires_at      integer
  scope           string
  token_type      string
  expires_in      integer

That makes failure mode 3 concrete rather than open. The structural
validation requires: the file parses as JSON, and `access_token`,
`refresh_token` and `expires_at` are present and nonblank. `scope`,
`token_type` and `expires_in` are recorded as observed but NOT required,
because one client release adding or dropping an optional field must not
make the lane unavailable. The fixture at
`evals/multi-model-verify/test_kimi_lane_home.py:310-317` gains the two
missing required keys in the same change, per your claim 14.
</new-evidence>

<accepted>
All of round 2, without reservation:

- P1 as you constrained it. Same-owner re-acquire is scoped to an EXACT
  match on the complete recorded identity, hostname plus PID plus start
  ticks plus debate id plus acquisition nonce. Same harness with a different
  debate id or nonce is ordinary contention and never automatic takeover.
  Recovery of a different abandoned debate under a live harness is a bounded
  wait, then a human-confirmed force-release naming the complete recorded
  identity. Your wording point is taken: it is a GUARDED HUMAN OVERRIDE, not
  authentication, and the spec will say that. Doctor reports the holder and
  reports LIVE, and never infers abandonment.
- P2 as you corrected it, which is better than what I proposed. The lock
  file is PERSISTENT and is never unlinked by any path. Acquire, reclaim and
  release are all state transitions written IN PLACE through the same
  exclusive handle, to a well-formed `state=free` or `state=held` record.
  The handle closes after a complete write and a durable flush, because the
  builder's shell exits while the owner is the longer-lived harness. A crash
  between truncation and a complete record leaves a malformed file, which
  the held rule already covers, and doctor plus confirmed force-release is
  the recovery path.
- P3 in full, including hash-before-and-after to prove the doctor mutated
  nothing, and keeping the containment-artifact check at
  `commands/doctor.md:169-173`.
- The two additional live gates: a coexistence gate for measurement 11 and a
  false-positive gate for measurement 16.
- The rule that every destructive refresh probe uses a disposable lane
  credential and never the user's ordinary login. Both measurements above
  already followed it.
- Your standing point that the Windows sharing, flushing, crash and
  per-host behaviour in P2 are probe-required on BOTH PowerShell hosts
  before they are claimed.
</accepted>

<remaining>
I believe nothing is now contested. Every FIX you issued is accepted on the
record with the constraint you attached to it, and the three UNVERIFIED
items that were measurable have been measured. The items that remain
UNVERIFIED are unchanged and are carried as live-gate requirements in the
plan, not as claims: junction read-through, refresh write-through,
deletion-through-junction on both hosts, absolute-key rejection, login
coexistence, the provider-list false-positive cases, and the P2 handle
behaviour.

If you agree, issue PASS and this freezes as converged with amendments. If
any accepted item is one you think I have restated in a way that weakens it,
name it instead.
</remaining>

<final-check>
Same as before. Flag anything you could not verify against files you read,
and treat measurements 17 and 18 as external results recorded here, exactly
as you have treated 1 through 16.
</final-check>
