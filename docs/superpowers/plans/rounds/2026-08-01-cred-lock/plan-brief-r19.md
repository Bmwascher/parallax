Round 19. The plan FROZE on your round-18 PASS and is now REOPENED, by its own
freeze rule, because a second whole-artifact read found a real defect. Same
evidence rules and verdict grammar. Plan header reads revision 18.

## Why it reopened

The user required a final whole-artifact fable-reviewer read before building.
The first one read revision 12; five of our rounds had rewritten substantial
text since, so I dispatched a second on the frozen r17.

No Criticals. It confirmed both r12 Importants are closed consistently in every
consumer, that exit code 3 now means the same thing in all three texts, and that
the packet is sound — it walked every task against the seven blocks and found no
constant falling outside them.

ONE IMPORTANT, and it is a class neither of us could have found. Every one of
our eighteen rounds compared the plan against ITSELF. This compared the plan
against the SPEC.

## The Important

**Two converged spec behaviours never made it into any task.**

The design spec requires reclaim to be visible — "Taking over a lock whose owner
is genuinely dead reports what it reclaimed and from whom",
`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:297-298` —
and a contention refusal to name the holder — exhausting the wait budget "is a
refusal naming the holder", `:276-278`.

Neither is anywhere in the plan. The DEAD-owner acquire row said only "acquire
or reclaim, generate a NEW nonce, print it". Exit 3 had no message contract in
the code table, in the UNMEASURABLE paragraph, or in Task 5's wrapper test,
which required only the code and a non-invoked stub.

What makes it more than an omission: `-ForceRelease` KEPT its "report what it
displaced". So the plan carried the visibility requirement for one of the three
and dropped it for the other two, which is exactly the shape that reads as
deliberate to a later editor.

And it would have shipped that way. The implementer receives the packet, not the
spec, and we spent rounds 16 through 18 making that boundary exact. A converged
design behaviour that is not in the packet does not get built.

I verified all of this against both documents before changing anything.

## The fix

`docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:229`, a new frozen
paragraph in Task 3.

**The channel was not free to choose, and this is the part I most want you to
check.** Acquire's stdout IS the nonce, and Task 6 parses it. So an invented
stdout report contaminates custody, and the plan already says the builder
CAPTURES the lock tool's output, so an invented stderr report is swallowed
rather than lost noisily. Both reports therefore go to STDERR, and acquire's
stdout is stated as the nonce and nothing else.

Frozen wording:

- Reclaim, on the DEAD-owner row ONLY:
  `reclaimed a dead holder: pid <pid> ticks <ticks> debate <debateId> home <debateHome>`
- A fresh acquisition over a `free` record prints NOTHING. Without that,
  acquisition and reclaim are indistinguishable, which defeats the point of
  making reclaim visible.
- Contention, before exiting 3 from acquire rows 5 and 6:
  `contended: holder pid <pid> ticks <ticks> debate <debateId>, liveness <LIVE|UNMEASURABLE>, wait budget <n>s expired`
- Handle contention, which never reads a record:
  `contended: the lock file is held by another writer, wait budget <n>s expired`

No message carries a credential field; the debate id is a random identifier, not
a secret.

Three oracles, each able to fail: reclaiming a DEAD holder emits that exact line
naming the dead holder's pid and debate id while stdout stays exactly the new
nonce; a fresh acquire over `free` emits NO stderr line; an exhausted budget
against a LIVE holder emits the contention line naming that holder before
exit 3.

The exact strings are mine. Reject them if the wording is wrong, but the
stdout-is-the-nonce constraint is not a preference.

## Five Minors, all folded in

1. **The doctor's UNKNOWN row overlapped the foreign-host row** on every
   foreign-host record, since Task 3 makes foreign-host liveness `UNKNOWN`
   always. Worst-of aggregation kept the verdict deterministic, but the UNKNOWN
   row's mandated detail describes the same-host mechanism, not the foreign-host
   exit-4 path. `:565` now reads "lock `held`, SAME-HOST, and UNKNOWN" and says
   why that word selects the row.

2. **`PARALLAX_LANE_HOME_CLEANUP_RELEASE_FAULT` froze only its name**, firing
   point and precedence, while the Remove seam froze mechanism and end state.
   "The release failed" has two different end states — record still held, or
   record free — and the test must assert one. At `:405` it now skips the lock
   mutation and produces code 5 with the record still HELD, with that state
   asserted and a direct release as teardown. Same invention class you closed
   for the Remove seam at r15.

3. **The wrong-`-Path` oracle's home B had no construction.** Building it with
   the builder against the same lane home would contend with A's RETAINED hold,
   so the test would never reach the case it exists to prove. `:405` now says
   by hand, and says why.

4. **The shipped `lane-lock` region's malformed list read exhaustive but dropped
   a class.** "one carrying a field this reader does not know" does not reach a
   FREE record carrying a held-only KNOWN field, which Task 3 twice insists is
   the case an unknown-field wording misses. That is the r7 two-wordings shape,
   in shipped text this time. `:615` now reads "one whose set of fields is not
   exactly the set its own state requires".

5. **Region id `lane-lock` is reused**, not new: a `lane-lock` is among seven
   regions the `DECLARED_REGIONS` comment says were deleted last cycle, so once
   the new one is declared that comment reads as if it narrated deleting this
   region. `:623` now requires amending the comment to say reused, not restored.

## What I want from you

1. Is this a PASS? If it is, the record finalization is the same three edits you
   specified at round 18, with round 19 and revision 18.

2. The stderr wording and the print-nothing-on-a-fresh-acquire rule are my
   choices. Check them.

3. Minor 4 changes SHIPPED contract text that Task 9 pins whole. Confirm the
   replacement still describes the same rule Task 3 freezes, because a shipped
   summary that drifts from the frozen rule is worse than the omission it
   replaced.

4. This is now the second time a whole-artifact read found something eighteen
   per-task rounds could not. If you see a third class we are both structurally
   blind to, name it now rather than after building starts.
