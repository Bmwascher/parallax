# Design: lane credential ownership and the concurrency lock

Status: CONVERGED (revision 2), cross-vendor debate complete, 3 rounds.
Ready for an implementation plan. No code has changed.
Amends the 0.18.0 backup lane shipped on `feat/kimi-code-backup-lane` at
`91278a1`, which is HELD UNMERGED for this fix.

## The defect, stated exactly

`tools/new-kimi-lane-home.ps1:410-414` copies the user's own kimi-code
credential into every throwaway debate home. The access token's
`expires_in` is 900 seconds, so a refresh during a debate is routine,
and a refresh ROTATES BOTH TOKENS. The copy refreshes; the server
retires the refresh token; the user's real home is left holding a token
the server will never honour again. Measured this cycle: the debate
home's copy refreshed during round 1 (both hashes changed, expiry moved
forward) while the real credential's file was never written. On the
real home's next use the client reported
`Skipped refreshing managed:kimi-code: OAuth provider requires login`
and left the credential file with both fields empty.

Two properties make this ship-blocking rather than an operations
annoyance:

- It is SILENT. Nothing in the debate reports it, and the user
  discovers it at the next unrelated kimi-code use.
- The repo is PUBLIC. A first-time user who runs the backup lane once
  is logged out of a tool the lane did not ask them to give up.

The root cause is a FORK, not a race: two files hold one credential and
only one of them can carry the live refresh token. Serializing access
does not fix it. One debate alone, with nothing concurrent, reproduces
it.

## What was measured, and what each measurement licenses

Every claim below is a measurement made on this machine against
kimi-code 0.31.1. Everything NOT measured is marked as a live-gate
requirement in the section of that name and is not relied on here.

Every destructive probe used a DISPOSABLE LANE CREDENTIAL and never the
user's ordinary login. That is a standing rule for this component, not
a courtesy of these particular runs.

| # | Measurement | Result |
|---|---|---|
| 1 | Access-token lifetime | `expires_in = 900` (15 min) |
| 2 | Refresh behaviour | rotates BOTH tokens; the old refresh token is retired |
| 3 | Copy-then-use | copy refreshes, source is never written, source goes stale |
| 4 | Stale source's next use | client blanks the credential file |
| 5 | Absolute path in the provider's `oauth.key` | does NOT resolve; cannot redirect the credential this way |
| 6 | Directory JUNCTION at `<home>/credentials` | client reads through it |
| 7 | Refresh through a junction | WRITES THROUGH to the real file; no fork |
| 8 | Junction creation privileges | no administrator rights needed |
| 9 | ACL set on the throwaway home | does NOT propagate through the junction |
| 10 | `Remove-Item -Recurse -Force` on a home containing a junction | does NOT delete through, on BOTH PowerShell 5.1 and 7 |
| 11 | Two independent kimi-code logins under different homes | COEXIST; the second does not invalidate the first, and the first still dispatches |
| 12 | Two concurrent dispatches from ONE home, both forced to refresh | BOTH SUCCEEDED; processes started in the same millisecond; the credential ended populated |
| 13 | A third dispatch using the credential the race left behind | SUCCEEDED; the surviving refresh token was live |
| 14 | Parent process of the shell the harness runs | `claude.exe`, stable across separate calls, same PID and same start time |
| 15 | Hooks-disable flag on the client | none exists |
| 16 | `provider list` with a garbage credential, and with no credential file at all | reports `source=oauth` either way; it is not an authentication check |
| 17 | `provider list` against a credential whose `expires_at` is already past | credential file BYTE-IDENTICAL afterwards: same SHA-256, same length, same mtime, expiry unchanged. It is NOT a refresh path |
| 18 | Credential JSON schema (field names and types only; no values read) | exactly six keys: `access_token` string, `refresh_token` string, `expires_at` integer, `scope` string, `token_type` string, `expires_in` integer |
| 19 | The exclusive-handle protocol, run on BOTH PowerShell 5.1 and 7 | identical on both: create-new refuses an existing path, a second exclusive open while held refuses, and truncate-and-rewrite in place under the held handle succeeds |
| 20 | JSON round-trip of the two candidate time representations, BOTH hosts | an integer tick count reads back `Int64` on both. A date STRING reads back `String` on 5.1 and `DateTime` on 7 |
| 21 | Owner anchor resolved as "parent of the invoking shell", from a NESTED shell | resolves to the intermediate shell, not the harness. The anchor is invocation-dependent |

Measurement 20 reproduces, live and on demand, the exact divergence that
shipped the previous lock's defect. It is the direct evidence for the
tick-integer decision below, and it is no longer only a historical claim.

Measurement 21 is a design correction found while probing, AFTER the
debate converged, and it is carried into the implementation plan for
that plan's own debate rather than adopted silently. Deriving the owner
from the invoking shell's parent is correct ONLY when the harness
invokes the tool directly. Under any wrapper or nested shell the parent
is that intermediate process, which exits, and every lock would read as
stale. So the owner is RESOLVED ONCE at the start of a debate and PASSED
EXPLICITLY on every later call; deriving it from the parent is the
documented fallback for a direct invocation, never the mechanism the
lock depends on.

Measurements 12 and 13 are n=1. They license the statement that a
concurrent refresh from one home was observed to survive; they do NOT
license a claim that it always survives, and the design does not rest
on it.

Measurement 17 required a second attempt. The first printed a
clean-looking "no change" verdict that was produced by two EMPTY strings
comparing equal, because the hash call failed silently under a
permissive error preference. That run was discarded and the probe
re-run with the hash failure made fatal. Recorded because a measurement
that cannot fail loudly is the exact class this component's invariant
exists to prevent.

## The decision

**Rejected: repair after the fact.** Copy as today, then copy the
refreshed credential back when the debate ends. It leaves the source
stale for the whole debate, loses the repair if the debate crashes, and
races any other kimi-code use in that window.

**Rejected: redirect the credential by configuration.** Measurement 5
closes this.

**Rejected: one persistent review home used directly as
`KIMI_CODE_HOME`.** It does solve the fork, but the per-debate
freshness rule in `backup-lane.md` rests on a home whose session
inventory belongs to one debate, and a shared home makes every debate's
evidence depend on the lock being correct rather than on the home being
new. It also makes `config.toml`, which carries this debate's pinned
effort, shared mutable state between debates.

**CHOSEN: a dedicated lane login, reached through a junction, guarded
by a lock.** The lane owns its own login, so the blast radius of any
credential fault is the lane's login and never the user's, while the
per-debate throwaway home that the evidence contract rests on is kept.

## The design

### 1. The lane owns its own login

A persistent LANE HOME at a fixed path under the user's profile holds
one thing the lane cares about: `credentials/kimi-code.json`, produced
by its own `kimi login`. It is never the user's credential and never a
copy of one. Measurement 11 establishes that this second login coexists
with the user's.

It does NOT live in the plugin's installed cache. Installs are
versioned cache copies replaced on `claude plugin update`
(`CLAUDE.md:32-39`), so a credential stored there is destroyed by a
routine update. That is disqualifying, not merely untried.

Creating it is a ONE-TIME, EXPLICIT, USER-PERFORMED step through a
LOGIN WRAPPER that acquires the lane lock for the duration. Nothing in
the lane performs a login on the user's behalf, and nothing falls back
to the user's credential if the lane login is absent.

An absent, unreadable, or STRUCTURALLY INVALID lane credential makes
the lane UNAVAILABLE, reported with the exact command that fixes it.
UNAVAILABLE is the fallbacks.md disposition, not a degraded dispatch.

Structural validity is specified per field, not as a single
"nonblank" rule, because measurement 18 shows the fields are not all
strings and a truthiness test would reject a valid integer `0`
(confirmed: PowerShell evaluates `0` as false):

- `access_token`: present, a string, nonempty after trimming.
- `refresh_token`: present, a string, nonempty after trimming.
- `expires_at`: present and a JSON integer. NO truthiness test and NO
  freshness test. An expiry in the past is a normal state, not
  corruption.
- `scope`, `token_type`, `expires_in`: recorded as observed, NOT
  required. One client release adding or dropping an optional field
  must not make the lane unavailable.

The offline fixture at
`evals/multi-model-verify/test_kimi_lane_home.py:310-317` currently
carries only `access_token`, so it gains a representative
`refresh_token` and an integer `expires_at` in the same change, or
every existing builder test turns red for a reason unrelated to what
those tests cover.

### 2. The debate home reaches it through a junction

`tools/new-kimi-lane-home.ps1` keeps every gate it has. Two things
change:

- The credential source becomes the LANE HOME, not
  `~/.kimi-code/credentials/kimi-code.json`.
- `<debate-home>/credentials` is created as a directory JUNCTION to
  `<lane-home>/credentials` instead of a directory holding a COPY.

Measurements 6 and 7 are what make this correct: the client reads
through the junction and a refresh writes THROUGH it, so one file holds
the credential and there is no fork to go stale. Measurement 10 is what
makes removal safe, and it covers BOTH recursive-delete paths in that
script: the `-Remove` mode at `tools/new-kimi-lane-home.ps1:127-133`
and the failed-build cleanup at `:482-489`, which removes an ancestor
that can contain the junction.

The lane home and its `credentials` directory get their OWN restrictive
ACL. The builder currently hardens only the throwaway home
(`tools/new-kimi-lane-home.ps1:393-408`), and measurement 9 shows that
protection does not propagate through the junction, so the target would
otherwise be unprotected.

The model table is still read from the user's real
`~/.kimi-code/config.toml`. That read is READ-ONLY and carries no
credential.

### 3. The lock

The lane home is shared state between debates and between sessions, so
it gets a lock. The previous lock, deleted in 0.18.0, is the design
input rather than a thing to avoid mentioning: it explicitly REFUSED to
record a process, reasoning that "a PID recorded here would be dead by
the time the next caller looked, and every lock would read as stale
immediately" (`775472c^:tools/kimi-lane-lock.ps1:10-14`). That
reasoning was correct about the SHELL and wrong about its PARENT, which
is exactly what measurement 14 distinguishes. Having no process anchor,
it fell back to a 45-minute clock, and its own header admits a live
round past that mark became breakable (`775472c^:...:63-73`).

**No clock.** There is no time-based expiry anywhere in this design.

**Where.** One PERSISTENT lock file in the lane home, beside the
credential it guards. It is never unlinked by any code path.

**State.** The file always holds a well-formed record carrying
`state=free` or `state=held`. A held record carries the complete owner
identity: hostname, owner process id, owner process START TIME, debate
id, and a random ACQUISITION NONCE, plus the debate home path and the
acquisition timestamp.

**Owner identity.** The owner is the harness session process, resolved
as the parent of the invoking shell, because the shell exits after
every command and a lock naming it would be stale the instant it is
written. Measurement 14 establishes that this parent is stable across
separate calls within one session and dies with the session. The tool
takes the owner as an overridable parameter and RECORDS what it
resolved. If it cannot resolve an owner, it refuses.

**Start-time representation is fixed and byte-stable:** UTC ticks as a
decimal integer, never a formatted date string. This is not a
stylistic choice. The deleted lock shipped a defect in exactly this
place: Windows PowerShell 5.1 returns a JSON timestamp as a String
while PowerShell 7 auto-converts it to a DateTime inside
`ConvertFrom-Json`, so on pwsh every well-formed lock read as unusable
and instantly breakable while the Windows suite stayed green and CI
caught it after release. The same file documents a second trap, a `Z`
stamp read five hours off on a UTC-05:00 machine, both reproduced by
running them (`775472c^:tools/kimi-lane-lock.ps1:105-132`). Both hosts
are gated.

**All state transitions are serialized through one exclusive handle,
and none of them unlinks the file.**

1. Try to create the lock file with create-new semantics and no
   sharing. Success means we hold it.
2. If it exists, open the EXISTING file for read-write with NO sharing.
   Only one process can hold that handle, so every acquirer, reclaimer
   and releaser is serialized behind it.
3. Holding that handle, read the record and decide. Write the new state
   IN PLACE, then flush durably and close. The handle cannot stay open
   for the debate, because the shell that opened it exits while the
   owner is the longer-lived harness.
4. An open that fails because another process holds the handle is
   CONTENTION, not staleness, and waits.

Release uses the same protocol and writes `state=free` in place. A
close-then-delete release would reopen the race the exclusive handle
just closed.

**Liveness, and only liveness.** A held lock is stale if and only if
its recorded owner is gone. Gone means: no process with that id, OR a
process with that id whose start time differs from the recorded one.
The start-time comparison is the PID-reuse guard.

**Same-owner re-acquire is scoped to the exact debate, not the
session.** An EXACT match on the complete recorded identity — hostname,
pid, start ticks, debate id, and nonce — is an idempotent re-acquire of
the same lock. The same harness with a DIFFERENT debate id or nonce is
ordinary contention and never an automatic takeover; otherwise two
concurrent debates from one session would displace each other, and a
late release from one could free the other's lock.

**What cannot be evaluated is HELD.** A record naming a different
hostname cannot have its liveness checked from here. So is an
unreadable, truncated, or malformed record. This is the same invariant
the rest of the lane runs on: an unmade measurement is never a clean
one.

**Contention waits.** A second session finding a LIVE holder waits and
retries. The wait is bounded by a caller-supplied budget; exhausting it
is a refusal naming the holder, never a break. The wait deadline is a
limit on caller patience and MUST NEVER become a staleness deadline.

**Two distinct human overrides, because one cannot cover both states.**

- FORCE-RELEASE, for a lock whose record is well-formed but whose
  debate was abandoned under a still-live harness. The operator must
  confirm the complete recorded identity. This is a GUARDED HUMAN
  OVERRIDE, not authentication; no cryptographic mechanism is claimed.
- MALFORMED-LOCK OVERRIDE, for a record too damaged to name an
  identity, which is precisely the state the first override cannot
  recover. The doctor reports `MALFORMED` with the file's byte length
  and SHA-256; the human supplies that exact hash; the tool re-hashes
  the current bytes under the exclusive handle and transitions to
  `state=free` only on an exact match. If the file is UNREADABLE the
  tool cannot override it at all, and the user must restore
  readability or the ACL first.

Both overrides are visible, and neither unlinks the file.

**Reclaim is visible.** Taking over a lock whose owner is genuinely
dead reports what it reclaimed and from whom.

**Sol is untouched.** The primary lane clears `CODEX_HOME` and never
copies a credential
(`skills/multi-model-verify/references/model-prompting-notes.md:169-180`,
`:200-229`), so it is structurally immune to this defect and keeps full
multi-session concurrency. The lock is Kimi-only. This is a stated user
requirement, not an inference.

### 4. What the lock is actually for

Stated narrowly, because measurement 12 removes the obvious
justification:

- It is NOT primarily for credential safety. A concurrent refresh from
  one home was observed to survive (measurements 12 and 13, n=1).
- It IS for the shared lane home's integrity, including the login
  wrapper, which now takes the same lock. Without that wrapper the
  login-race justification would be unearned, because `kimi login` is
  otherwise an external command with no obligation to the lock.
- It IS for making a takeover VISIBLE and refusable.

### 5. The doctor stops touching credentials

`commands/doctor.md` check 8 currently builds a scratch home with the
builder and runs `provider list` under it (`commands/doctor.md:157-168`).
Two separate problems:

- It copies a credential it does not need, and can strand that copy if
  the doctor stops before removal. Measurement 17 establishes that it
  does NOT retire the refresh token through `provider list`, so this is
  an unnecessary-copy and stranded-secret surface and nothing wider.
- It reports "credential present and OAuth-sourced", which the check
  cannot support: measurement 16 shows the same `source=oauth` output
  with a garbage credential and with no credential file at all. That
  sentence is a live overclaim in shipped text.

Check 8 becomes: binary and version floor; read-only structural
inspection of the lane credential in place, per the field rules in
section 1; hash before and after to PROVE the doctor mutated nothing;
report structural readiness only; print the locked login-wrapper
command when unavailable; keep the containment-artifact check at
`commands/doctor.md:169-173`. It also reports lock state on demand,
saying `LIVE` for a live holder without inferring whether that session
has abandoned the debate.

Any authenticated probe is a separate, explicitly labelled operation
that acquires the lane lock, discloses that it may refresh the lane
credential, and never touches the user's credential.

## Live-gate requirements

The repository cannot verify measurements taken outside it, and the
backup contract suite declares itself offline with zero CLI calls
(`evals/multi-model-verify/test_backup_lane.py:1-7`). These become
live-gated probes under this repo's existing discipline, where a failed
setup is a FAILED gate and never a skipped branch:

1. Junction read-through and refresh write-through (6, 7).
2. Deletion-through-junction on BOTH PowerShell hosts, covering both
   recursive-delete paths (10).
3. Absolute-key rejection in the provider `oauth.key` (5).
4. Login coexistence (11).
5. `provider list` false positives: garbage credential and absent
   credential file (16).
6. The exclusive-handle protocol on both hosts: sharing semantics,
   durable flush, and crash during rewrite.

## What this changes in the shipped contract

`skills/multi-model-verify/references/backup-lane.md:48-67`, region
`lane-home-isolation`, says the home holds a COPIED credential and that
a missing credential makes the lane unavailable. Both change. Its
whole-region pin at `evals/multi-model-verify/test_backup_lane.py:162-194`
changes FIRST, per `CLAUDE.md:41-56`.

A new region covers the lock. Adding it also means editing
`DECLARED_REGIONS` in `evals/multi-model-verify/test_contract_coverage.py`
(`CLAUDE.md:89-92`).

`tools/read-kimi-round-evidence.ps1` is UNAFFECTED. It reads session
evidence, never credentials, and the debate home's session layout does
not change.

## Debate record

- Lane: primary (codex). Participants: Opus 5 (session) / gpt-5.6-sol
  (reviewer). Rounds: 3. Effective route confirmed on every round:
  `model: gpt-5.6-sol`, `provider: openai`, `sandbox: read-only`,
  `reasoning effort: high`, session `019fbb61-cc35-75b3-b34a-5b52219ad5bd`
  echoed on both resumes.
- Preflight: `codex-cli 0.144.1`, `Logged in using ChatGPT`;
  `git ls-files --cached --others '*AGENTS.md' '.agents/*'` empty;
  context probe clean, 29 advertised skills reduced to 0 by the
  generated override, `override_sha256`
  `180f09f50d282b5603f1c0d0621f2913ff66c8b7798e7a2f3b7fe8d41f432bb8`
  re-verified before every dispatch. Environment note: the user's
  `~/.codex/AGENTS.md` is present (1011 bytes) and instructing the
  reviewer; recorded, not a stop.
- Outcome: CONVERGED WITH AMENDMENTS. The reviewer issued FIX in all
  three rounds; every FIX was accepted on the record, and its round-3
  reply states that PASS follows from the two final amendments, both of
  which are incorporated above.
- Amendments the reviewer contributed that the session did not have:
  abandoned-debate-under-live-harness (round 1); login outside the lock
  (round 1); release identity needing debate id and nonce (round 1);
  non-atomic stale reclaim (round 1); malformed credential not
  classified unavailable (round 1); start-time representation, backed by
  a prior shipped defect in this exact component (round 1); lane-home
  ACL (round 1); same-owner re-acquire must be debate-scoped, not
  session-scoped (round 2); release must not unlink either (round 2);
  malformed-lock recovery is impossible under identity-confirmed
  force-release (round 3); `expires_at` cannot be validated by
  nonblankness (round 3).
- Session claim RETRACTED under reviewer challenge: that the doctor can
  retire the user's refresh token. It was wider than its evidence.
  Measurement 17 was taken in response and refutes it.
- Verification status: FULL.
