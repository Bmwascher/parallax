# Build ledger, 2026-08-01 lane credential and lock

Per-task record of WHO built each task, WHAT verification exists, and
WHOSE evidence it is. The last column matters: the session verifies every
task independently and never accepts an implementer's report as the
verdict, so where a report did not arrive the evidence is the session's
own and must not later be attributed to the implementer.

Plan: `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md`,
FROZEN at revision 30 after 31 cross-vendor rounds. Round 30 reopened
the frozen recovery command during building and round 31 reopened Task 7;
the two remediation rows below are the result.

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
| 7 r31 remediation | `fd712b1` | full, accurate | read the fixed capture order and its call sites, confirmed both new instances of the exact-line rule, ran the old-vs-new custody-line demonstration, listed the six pin oracles and six safety fixtures, 51 tests per host, full suite 840 | BOTH, plus **two session-only findings** |
| mirror utf-8 output | `51b4554` | n/a, session change | measured IBM437 on both hosts, showed the byte difference, 65 mirror tests per host, clean full suite | SESSION ONLY |

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

The offline half is fully verified: 51 tests per host after the round-31
remediation, driving the same production helper the live suite imports,
with no opt-in and no real credential.

The LIVE half has never run. It needs three pre-provisioned lane homes,
and `PARALLAX_LANE_LIVE_HOME_A`, `_B` and `_C` do not exist, because
creating them needs a one-time interactive login this suite is forbidden
to perform. **Task 7 step 2 requires all pass and ZERO skipped, so that
gate is UNSATISFIED.** Nothing in this branch may claim measurements 5,
6, 7, 10, 11, 16 or 17 are re-verified by an executed gate.

What IS verified is the refusal direction, which is the safe one: with
the opt-in set and the homes absent, all ten tests ERROR rather than
skip, naming the login wrapper and the missing variables. Without the
opt-in they skip.

The probe-record finding raised here is CLOSED at `fd712b1`: the record is
now a locking assertion with six oracles, and rewriting it needs an exact
opt-in.

## Round 31, and what each side caught

The reviewer read Task 7 whole and returned ten findings. Nine were
confirmed against the code by the session and fixed at `fd712b1`. Two of
them were serious in kind rather than in degree: a token issued by the
command being scanned could reach pytest output, and the live-home setup
had no check preventing the suite's own deliberate expiry from landing on
the user's real credential.

The tenth does not hold. It claimed the hostile `-Model` refusal fires
before any lock interaction, which would make the failed-build cleanup
test vacuous. The refusal is at `tools/new-kimi-lane-home.ps1:613`, inside
the main `try` and after the acquire at line 573. The reviewer appears to
have read the comment at line 610, "This runs before ANYTHING touches the
filesystem", and generalized it from filesystem to lock. That test is
unchanged.

Two findings are the session's own. The blank-line acceptance bug had a
SECOND instance neither the reviewer nor the round-30 remediation named:
the custody line, which carries the nonce the release is performed with.
And item 6's post-command merge still runs after its assertions rather
than inside the capture helper; that one is left as-is because those
homes are disposable and hold no real credential, and it is carried to
the next round rather than changed unilaterally.

Neither side's list contained the other's. That is the argument for
running both, stated as a fact about this round rather than as a slogan.

## The live gate HAS RUN. Rounds 32 and 33.

The user performed the three manual logins on 2026-08-01 and the live
suite executed against three real lane homes. This supersedes the "Task
7, stated plainly" section above, which was written when the gate was
unrunnable.

**Current live state, `powershell.exe`: 11 passed, 1 failed.** `pwsh.exe`
has NOT been run. Task 10 requires both hosts with zero skipped at final
HEAD, so the gate is still UNSATISFIED.

Passing with live evidence: measurements 6 (junction read-through), 7
(refresh write-through and rotation), 10 (both delete paths, including
the r32 deletion oracle that is the only thing ever to exercise that
branch), 11 (coexistence), 16 and 17 (`provider list`).

**Measurement 5 has NO passing live evidence and its old oracle could
never have produced any.** That test built its "absolute" key with
`Path.resolve()`, which follows a junction on Windows, so the key named
the same credential the relative default already reached. Exit 0 with
`PROBE` was produced identically by "the absolute key resolved" and by
"it was ignored". Round 33 replaces it with a five-step three-state
oracle; that work is NOT done.

**One fact worth recording on its own.** Three lane logins now coexist
with the user's own, and the user's real credential is untouched: still
`ok`, file unwritten since hours before the three logins. That is the
first direct evidence that this branch's fix works. Under the copy-based
approach a lane login could retire the real refresh token.

## What is NOT done

- Round 33 fixes 1 and 2: the absolute-key oracle rewrite and the
  deletion of the probe-record machinery. Not started.
- The oracles for round 33 fixes 3 and 4. Both fixes work and are
  committed at `6a6a5f9`, but neither is locked by a test.
- `pwsh.exe` live execution.
- Tasks 8, 9, 10.

## Standing note for the whole-branch review

Do not read this ledger's "BOTH" rows as two independent verifications of
equal weight. The implementer runs first and the session checks it; they
share a machine, a working tree and an interpreter. Neither substitutes
for the cross-vendor lane or for CI.

The local suite is now CLEAN, which was Task 10's precondition. The one
former failure,
`test_review_mirror.py::test_a_non_ascii_baseline_entry_reaches_the_manifest`,
was recorded here as a local console-encoding artifact. It was not: the
mirror decoded git's pathnames as strict UTF-8 and then printed them in
the OEM code page, so an accented name reached the baseline and the
manifest as U+FFFD. Fixed at `51b4554`. The earlier reading was too
generous to the tool, and the order-dependence was the clue - ambient
console encoding varies, and another test in the same run could change
it.
