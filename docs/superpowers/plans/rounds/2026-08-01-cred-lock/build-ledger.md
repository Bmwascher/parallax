# Build ledger, 2026-08-01 lane credential and lock

Per-task record of WHO built each task, WHAT verification exists, and
WHOSE evidence it is. The last column matters: the session verifies every
task independently and never accepts an implementer's report as the
verdict, so where a report did not arrive the evidence is the session's
own and must not later be attributed to the implementer.

Plan: `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md`,
FROZEN at revision 29 after 30 cross-vendor rounds. Round 30 reopened
the frozen recovery command during building; the remediation row below
is the result.

| Task | Commit | Implementer report | Session verification | Evidence provenance |
|---|---|---|---|---|
| 1 CI repair | `ac3e4d8`, `e6dc4fe` | full, accurate | ran the checker, all four then five host-discovery directions, both mutations | BOTH |
| 2 credential validator | `a5ec09f` | full, accurate | ran all four statuses, the seam, blank path, binding refusal, both hosts | BOTH |
| 3 lock tool | `5365bb0` | full, accurate | ran ResolveOwner, acquire, reclaim, contention, the wait clamp, status | BOTH |
| 4 live protocol gate | `00168a5` | full, accurate | read the acceptance and timeout paths, ran all three host modes | BOTH |
| 5 login wrapper | `74f57ab` | full, accurate | ran the non-directory row and the probe seam, checked the ACE shape, verified `kimi login` against the real client | BOTH |
| 6 builder stops copying | `165e809` | **NONE — agent returned twice with only "I'll wait for the notification"** | copy absence, junction, seam message, terminating deletion, deleted-test audit, first-use live test, both hosts, full suite | **SESSION ONLY** |
| 5+6 fail-closed remediation | `8e5dcaf` | full, accurate | byte-compared the stored template against the frozen line, re-ran the round-30 fail-closed reproduction on both hosts, read all four caller fixes, checked the nine-row matrix and row 9's fixture, 113 tests per host | BOTH |
| 7 live gates | `29f975b` | full, accurate | ran the support suite on both hosts, verified the helper imports with no live check, drove the refusal direction with the opt-in set, traced the guard ahead of the record write | **BOTH, live half UNRUN** |

## Task 6, stated plainly

No implementer report exists. The agent spent roughly 313k tokens and
returned twice without evidence; a direct request for the eight
load-bearing points produced the same non-answer. The work itself is
sound, and every claim in the commit message rests on a check the
session ran and can name:

- no `Copy-Item` and no reference to the user's credential path anywhere
  in the builder
- `New-Item -ItemType Junction` replaces it
- `Remove-Item ... -ErrorAction Stop` followed by an absence verification
- the moved seam's message reads `simulated pre-emission failure`, no
  longer naming a credential copy that no longer exists
- first use live-tested: exit 6, the complete runnable login command, and
  no lane home, no lock and no debate home created
- 60 tests per host; 765 passing across the suite
- the two deleted tests audited individually and both confirmed
  superseded rather than dropped, one re-pointed at the fixture that
  replaced its subject

## Task 7, stated plainly

The offline half is fully verified: 23 tests per host, driving the same
production helper the live suite imports, with no opt-in and no real
credential.

The LIVE half has never run. It needs three pre-provisioned lane homes,
and `PARALLAX_LANE_LIVE_HOME_A`, `_B` and `_C` do not exist, because
creating them needs a one-time interactive login this suite is forbidden
to perform. **Task 7 step 2 requires all pass and ZERO skipped, so that
gate is UNSATISFIED.** Nothing in this branch may claim measurements 5,
6, 7, 10, 11, 16 or 17 are re-verified by an executed gate.

What IS verified is the refusal direction, which is the safe one: with
the opt-in set and the homes absent, all nine tests ERROR rather than
skip, naming the login wrapper and the missing variables. Without the
opt-in they skip.

One open finding, carried to cross-vendor review: the absolute-key
`probe-record.md` is only ever written, never read back and asserted, so
a changed client message cannot fail the suite. The load-bearing fact is
still checked by the nonzero-exit assertion; the exact message is not
pinned.

## Standing note for the whole-branch review

Do not read this ledger's "BOTH" rows as two independent verifications of
equal weight. The implementer runs first and the session checks it; they
share a machine, a working tree and an interpreter. Neither substitutes
for the cross-vendor lane or for CI.

One suite failure is pre-existing and not ours:
`test_review_mirror.py::test_a_non_ascii_baseline_entry_reaches_the_manifest`
fails on `main` as well, deterministically in isolation and in its own
module, intermittently in full-suite runs. It is a local console-encoding
artifact; `main`'s CI is green. Task 10 requires a clean local suite, so
it must be resolved or its gate re-scoped before that task can pass.
