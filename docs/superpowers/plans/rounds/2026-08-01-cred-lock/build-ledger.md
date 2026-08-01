# Build ledger, 2026-08-01 lane credential and lock

Per-task record of WHO built each task, WHAT verification exists, and
WHOSE evidence it is. The last column matters: the session verifies every
task independently and never accepts an implementer's report as the
verdict, so where a report did not arrive the evidence is the session's
own and must not later be attributed to the implementer.

Plan: `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md`,
FROZEN at revision 28 after 29 cross-vendor rounds.

| Task | Commit | Implementer report | Session verification | Evidence provenance |
|---|---|---|---|---|
| 1 CI repair | `ac3e4d8`, `e6dc4fe` | full, accurate | ran the checker, all four then five host-discovery directions, both mutations | BOTH |
| 2 credential validator | `a5ec09f` | full, accurate | ran all four statuses, the seam, blank path, binding refusal, both hosts | BOTH |
| 3 lock tool | `5365bb0` | full, accurate | ran ResolveOwner, acquire, reclaim, contention, the wait clamp, status | BOTH |
| 4 live protocol gate | `00168a5` | full, accurate | read the acceptance and timeout paths, ran all three host modes | BOTH |
| 5 login wrapper | `74f57ab` | full, accurate | ran the non-directory row and the probe seam, checked the ACE shape, verified `kimi login` against the real client | BOTH |
| 6 builder stops copying | `165e809` | **NONE — agent returned twice with only "I'll wait for the notification"** | copy absence, junction, seam message, terminating deletion, deleted-test audit, first-use live test, both hosts, full suite | **SESSION ONLY** |

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
