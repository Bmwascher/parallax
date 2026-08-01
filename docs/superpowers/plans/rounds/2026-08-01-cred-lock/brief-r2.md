Round 2. Evidence rules and verdict grammar as before.

<position-changes>
ACCEPTED, all of them, and each is now a requirement the implementation plan
will carry:

- Claim 6 FIX. Real hole, and the sharpest finding in your reply. An
  abandoned debate under a live harness session holds the lock forever.
- Claim 9 FIX. Correct. Login is outside the lock, so the login-race
  justification was unearned as written.
- Failure mode 1, nonce and debate identity in the release comparison.
- Failure mode 2, atomic stale reclaim.
- Failure mode 3, a present-but-malformed credential must be UNAVAILABLE.
- Failure mode 4, byte-stable start-time representation, gated on both hosts.
- Failure mode 5, the lane home and its credential need their own ACL.
- Claim 5 wording: "the user's ordinary login remains intact", not "costs
  nothing".
- Q1 through Q5 as you answered them, including the point that the plugin
  cache is a versioned copy replaced on update (CLAUDE.md:32-39), which
  makes it disqualifying for credential storage rather than merely untried.

I verified your historical citation and it is STRONGER than you stated. The
deleted lock at `775472c^:10-14` did not merely use age; it explicitly
REJECTED a process handle, reasoning that "a PID recorded here would be dead
by the time the next caller looked, and every lock would read as stale
immediately". That reasoning was correct about the SHELL and wrong about its
PARENT, which is exactly what measurement 14 distinguishes. The same file at
`775472c^:63-73` confirms the 45-minute constant and states the residual you
cited, and `775472c^:105-132` documents the PowerShell 5.1/7 divergence
biting this repo in production, plus a second time-representation trap
(DateTimeOffset versus DateTime, and `Z` stamps read five hours off on a
UTC-05:00 machine, "both reproduced by running them"). Your failure mode 4
is therefore not a hypothetical: it is a repeat of a shipped defect class in
this exact component.

RE-FRAMED, not refuted: your ESCALATEs on claims 1 to 5. You are right that
the repository cannot verify measurements 1 to 14, and right that
`evals/multi-model-verify/test_backup_lane.py:1-7` declares itself offline
with zero CLI calls while `evals/multi-model-verify/test_kimi_lane_home.py:309-317`
drives the builder against a fake profile and a fake token. But these are not
disagreements evidence cannot settle, so they are not escalations to a human;
they are a requirement that the measurements become reproducible in-repo. The
plan will carry live-gated probes for junction read-through, refresh
write-through, deletion-through-junction on BOTH PowerShell hosts, and
absolute-key rejection, under this repo's existing live-gate discipline where
a failed setup is a FAILED gate and never a skipped branch.
</position-changes>

<new-claims>
12. THE DEFECT'S BLAST RADIUS INCLUDES THE DOCTOR, which neither of us
stated. `commands/doctor.md:158-160` has check 8 build a scratch home with
`tools/new-kimi-lane-home.ps1` and run `provider list` under it. Under the
current design that build copies the user's credential
(`tools/new-kimi-lane-home.ps1:410-414`), so running `/parallax:doctor` is
itself capable of retiring the user's refresh token. The command a user runs
when something is already wrong can be the thing that breaks their login.
This raises the severity of the fix and adds a test target.

13. THE DOCTOR ALSO OVERCLAIMS TODAY, and your Q5 answer understates it.
`commands/doctor.md:161-168` is already honest that `source=oauth` does not
prove a dispatch will work, but it still instructs the reporter to say
"credential present and OAuth-sourced". Measurement 16 is that `provider
list` reports `source=oauth` with a garbage credential AND with no
credential file at all, so the check cannot support the "credential present"
half either. That sentence is a live overclaim in shipped text, not just a
gap to fill.

14. THE OFFLINE FIXTURE CONSTRAINS FAILURE MODE 3. The stand-in credential
at `evals/multi-model-verify/test_kimi_lane_home.py:313-314` is
`{"access_token": "not-a-real-token"}` with no refresh token and no expiry.
A "required nonblank fields" validation designed without reference to it
will fail every existing builder test for a reason unrelated to what those
tests cover. So the validation must name EXACTLY which fields are required,
and the fixture must be updated in the same change.
</new-claims>

<proposals-to-check>
Two concrete resolutions. Tell me if each closes the finding it answers, or
what it still leaves open.

P1, answering claim 6. Rather than a dedicated long-lived owner process per
debate, three mechanisms together:
  (a) SAME-OWNER RE-ACQUIRE. If the recorded owner identity equals the
      acquiring caller's, the lock is re-acquired rather than contended,
      and the takeover is logged. This covers abandonment inside one live
      session, which is the case you named.
  (b) An explicit authenticated FORCE-RELEASE for a human, which names the
      holder it is about to displace and requires the operator to confirm
      that holder, so it cannot be scripted into a silent break.
  (c) `/parallax:doctor` reports a held lock with its holder and liveness,
      so an abandoned lock is visible without anyone waiting on it.
My concern with a dedicated owner process is that a spawned keep-alive is
itself a thing that can be orphaned, and it would need its own liveness
story. Is (a)+(b)+(c) sufficient, or does (a) reintroduce a takeover you
consider unacceptable even within one session?

P2, answering failure mode 2. Never delete-then-create. Acquire is:
  (i)  try to create the lock file with CreateNew and no sharing. Success
       means we hold it.
  (ii) if it exists, open the EXISTING file with FileMode.Open,
       FileAccess.ReadWrite, FileShare.None. Only one process can hold that
       handle, so every reclaimer is serialized behind it.
  (iii) holding that exclusive handle, read the record, evaluate liveness,
       and if the owner is dead TRUNCATE and rewrite our identity IN PLACE,
       then keep or close the handle.
  (iv) an open that fails because another process holds the handle is
       contention, not staleness, and waits.
This never unlinks a file another process may be about to write. Does it
close the two-reclaimer race on Windows, and does step (iv) risk reading a
live holder's brief write window as contention in a way that matters?

P3. Given claim 12, should the doctor's check 8 stop building a home at all
and instead validate the lane credential structurally in place, so the
diagnostic command touches no credential it could rotate?
</proposals-to-check>

<final-check>
Same as round 1. Flag anything you could not verify against files you read.
Note: no `python` is on PATH in your sandbox, so the repo's pytest gates are
not runnable there. No code has changed yet, so no gate is implicated; do
not treat their absence as a finding.
</final-check>
