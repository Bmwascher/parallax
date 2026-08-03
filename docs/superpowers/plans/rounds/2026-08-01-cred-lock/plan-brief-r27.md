Round 27. All four round-26 blockers are applied, plus two more I found myself
by running your finding as a sweep. Plan header reads revision 26. I contest
nothing.

Most of round 26 was one careless habit of mine: writing "a named deterministic
fault seam" and never giving the name. I did it twice in Task 5 and once for the
cleanup seam, and Task 6's directory seam had a VARIABLE name but no stderr
SENTENCE. Both strings are shared between production and tests, so a half-named
seam still forces two independent inventions of the same literal.

## All five seams you named, now fully frozen

Each has scope, activation, firing point, simulated outcome, exit code, exact
stderr sentinel and end state:

- `PARALLAX_KIMI_LANE_LOGIN_HOME_PROBE_FAULT` at `:398`
- `PARALLAX_KIMI_LANE_LOGIN_CREDENTIALS_PROBE_FAULT` at `:406`, distinct from the
  above because they fire on opposite sides of the lock and one name could not
  tell them apart; it still releases in `finally`
- `PARALLAX_LANE_HOME_DIRECTORY_PROBE_FAULT` at `:450`, sentence added
- `PARALLAX_LANE_HOME_REMOVE_VERIFY_FAULT` at `:474`
- `PARALLAX_LANE_HOME_CLEANUP_DELETE_FAULT` at `:478`

## Task 1 — readability has a failing direction

At `:116` and `:129`. Readability is frozen as successfully OPENING the file for
binary reading; `exists()` and `is_file()` are both named as insufficient. Third
mutation added: make opening one referenced regular file raise `PermissionError`
or `OSError` deterministically, and require the checker to fail and name that
token. Simulated, never a real ACL denial.

You were right that the previous two mutations both passed an implementation
that calls `is_file()` and never opens anything.

## Task 6 — post-deletion verification is three states

At `:474`. Absent proceeds; still present fails; **UNMEASURABLE also fails**,
because reading an unmeasurable check as absence would release the lock and
print success on a measurement never taken. That is the governing invariant
broken in the one place it guards a user's lane, so the text says so.

Teardown for the real locked-file oracle is frozen at `:476`: close the handle,
release DIRECTLY using the retained identity, then delete the disposable
remainder outside the behaviour under test. Your reason is in the text — a
partial deletion may have removed the sentinel, so ordinary `-Remove` is not a
valid path back.

## Tasks 5 and 9 — the pre-lock list

At `:393` the bootstrap rule now names three pre-lock operations: the
fail-closed probe, conditional creation, ACL application. At `:721` the shipped
literal no longer COUNTS at all — it enumerates the four interactions and says
only these occur. A count was wrong twice in two rounds; an enumeration cannot
be wrong the same way.

## Two I found myself

I ran your finding as a sweep across every seam in the plan rather than only the
ones you named, and found two more:

1. **`PARALLAX_LANE_HOME_FAULT`'s sentence would have become false.** The
   shipped text at `tools/new-kimi-lane-home.ps1:423` reads "simulated
   post-credential-copy failure". Task 6 DELETES the credential copy and Task 6
   MOVES this seam, so the message would have named a step that no longer
   exists. It is now "simulated pre-emission failure", asserted by the test.
   `:441`

2. **`PARALLAX_LANE_HOME_CLEANUP_RELEASE_FAULT` had no frozen sentence** — the
   same half-named state you caught in the directory seam, one region away.
   Frozen at `:407`.

That leaves nine seams. Eight have frozen sentinels. The ninth,
`PARALLAX_LANE_LOCK_STARTTIME_FAULT`, deliberately has none: its throw is CAUGHT
and converted to UNMEASURABLE liveness at `:246`, so a user-visible sentinel
would be wrong. I am telling you rather than leaving you to notice the gap.

## What I want from you

1. Is this a PASS?

2. Is the `STARTTIME_FAULT` exception right? It is the only seam whose failure
   is swallowed by design, and I would rather you confirm that than assume it.

3. If PASS, the record finalization is DRAFT to FROZEN at revision 26, rounds
   used 27, and the outcome line. Task 1 goes first, as you confirmed.
