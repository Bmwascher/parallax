# Round 22 - both lanes found the same broken oracle, independently

You are the cross-vendor reviewer on backlog item 32 (detached dispatch) and
item 33 (automatic review mirror). This is round 22.

The mirror is a fresh file copy of the working tree at source commit
`3140df9` on branch `item32-detached-dispatch`. Its own `HEAD` is the
builder's remediation commit, by construction. The plan file in the mirror
was hash-compared to the source before dispatch and is identical.

The plan is `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md`.
The spec is
`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`.

Ground every claim in a `path:line` you actually opened in this mirror.

## Note on the previous round

Round 21 was dispatched twice. The first attempt ended
`ERROR: Selected model is at capacity`, exit 1, with no reply file written -
a transport failure per fallbacks.md, discarded and re-dispatched on fresh
round-numbered paths. Worth recording that the round-evidence binder
returned CLEAN for that attempt, correctly: it binds the brief this side
sent to what the client recorded, and the brief did land. What caught the
failure was the missing reply and the exit code, not the binder.

## Your three findings

**1. The `NameError` oracle - fixed, and I ran it.** You and the Fable lane
found this independently in the same round, which is the first time in this
debate that has happened. `con` is now assigned at the top beside `orph`,
before any assertion uses either.

I did not take that on faith. I extracted the heredoc from the plan and
executed it against the current unreconciled spec. It exits 1 with
`AssertionError: orphan section missing: the pid is on disk for every
committed launch` - the right failure, naming the right clause, rather than
a `NameError`. It can run, and it can fail.

The step now records that this was the THIRD oracle in this debate broken by
the fix to the previous oracle.

**2. The two-form split was not propagated.** You named six sites. Four were
already repaired from the Fable lane's parallel finding (68, 79, and the
record's promise, plus the "below" pointer). Your other three were not, and
are now:

- The design bullet at :20 now says the new calls NAME the plugin root:
  `${CLAUDE_PLUGIN_ROOT}` in `SKILL.md` where substitution is measured,
  `<plugin-checkout>` in `backup-lane.md` which is read raw.
- The scope bullet at :30 now says item 58 is not fixed here beyond naming
  the plugin root - RESOLVED for the two SKILL.md calls, only NAMED for the
  three backup-lane ones.
- Region one no longer says the path "is anchored". It says the path NAMES
  the plugin root, and then that naming is not always resolving, with the
  two documents' behaviour stated rather than blurred.

**3. "Task 7 step 4 below"** now reads "is".

## On your base-rate remark

You are right, and I want it recorded rather than argued: the base rate I
state each round is prompt-supplied. The repository's record is deliberately
bound to a seventeen-dispatch point at a named commit and lists later rounds
separately, precisely so it does not carry a running total that goes stale.
That makes the figure honest about its own provenance and NOT
repo-verifiable, and you should keep treating it that way.

## What I want from you

1. CLOSES or DOES NOT CLOSE on each of your three, citing the `path:line`
   you read. If any site still carries the single-form claim, name it.

2. **The base rate is twenty-one numbered dispatches out of twenty-one**,
   prompt-supplied as above. Either name a new instance of a
   completion-model hole, a non-binding oracle, or an internal
   contradiction, or say explicitly that you searched and found none, and
   name what you searched.

3. Name anything this revision INTRODUCED. It touched two design bullets,
   region one, the Task 9 oracle's variable order and its expected-result
   text, and the debate record's entries for rounds 20 and 21.

4. If the plan is ready, say FREEZE without hedging. If not, name the
   smallest set of changes.

End with PASS, FIX, or ESCALATE.
