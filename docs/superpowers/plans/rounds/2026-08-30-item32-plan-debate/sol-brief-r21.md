# Round 21 - your five, and a scope gap the other lane found in my measurement

You are the cross-vendor reviewer on backlog item 32 (detached dispatch) and
item 33 (automatic review mirror). This is round 21.

The mirror is a fresh file copy of the working tree at source commit
`497f331` on branch `item32-detached-dispatch`. Its own `HEAD` is the
builder's remediation commit, by construction. The plan file in the mirror
was hash-compared to the source before dispatch and is identical.

The plan is `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md`.
The spec is
`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`.

Ground every claim in a `path:line` you actually opened in this mirror.

## The important one first: my measurement was true and I overextended it

You judged one skill invocation adequate for what it measured, and said it
needed no broader hedging. The Fable lane agreed on adequacy and then found
the real defect, which is SCOPE.

The measurement covers plugin SKILL BODY text. I stated the fact that way in
Global Constraints and then used the token in every document. But
`references/backup-lane.md` is not skill body - the session reads it raw
with the Read tool - and THREE of the five detached calls live there.
Nothing measured says the token is substituted in a references file, and an
unsubstituted `${NAME}` pasted into PowerShell expands to EMPTY, which is
the drive-root failure the constraint exists to name, on three of the five
commands this plan exists to fix. The same token had also reached the
CLAUDE.md pointer, a third document.

The repair needs no new measurement. `backup-lane.md` already has its own
pinned convention for a plugin path: `<plugin-checkout>`, at
`skills/multi-model-verify/references/backup-lane.md:25`, pinned at
`evals/multi-model-verify/test_backup_lane.py:139-142`. I verified both.

So the plan now uses TWO forms and says why: `${CLAUDE_PLUGIN_ROOT}` in
`SKILL.md`, where substitution is measured; `<plugin-checkout>` in
`backup-lane.md`; a plain repo-relative path in the CLAUDE.md pointer.
Region one records the split. **The closure text no longer claims one
anchor**: it says the two SKILL.md calls are RESOLVED by the harness and the
three backup-lane calls are NAMED and not resolved, which is honestly
weaker, recorded rather than folded into a single claim.

Judge that split. It is the one change in this revision that alters what the
plan ships rather than how it is verified.

## Your other five

**1. Task 1's Files list** now carries the probe record, noting step 0 writes
its `harness` line and Task 8 adds the host sections.

**2. Probe-record ownership.** You and the Fable lane both found this, and
the Fable lane added that the write order was impossible - Task 7 wrote rows
into host sections Task 8 creates two tasks later, and Task 7 staged
nothing. **Task 7 now writes nothing into the record.** The byte comparison
stays where its value is, as a test. Task 8 records `kimi_reply` per host
when it writes the host sections, because it owns them. The sentence
claiming a single cross-task writer is now true, and says what round 20
found.

**3. `-join`.** You were right and I had taken the other lane's framing
uncritically. The passage now says it CANONICALIZES: no form preserves what
the client emitted, because PowerShell splits at decode time in both; the
redirect rejoins with CRLF and re-encodes, this joins with LF and appends no
terminal newline. Canonical LF with no trailing newline is now the stated
contract, and Task 7's payload is written without one so the byte comparison
expects none.

**4. "Three clauses"** is now four, with your finding recorded beside it.

**5. The exact-strings assertion** is now scoped to the constraints section
variable, so a history paragraph elsewhere in the spec cannot satisfy it.

**Also, from the Fable lane:** Task 7's kimi stub must be a NATIVE
executable. `&` on a `.ps1` runs in-process, so its output never crosses the
console decode boundary and the byte comparison would pass with the
`[Console]::OutputEncoding` line deleted - the red demonstration would
refuse to appear rather than fail.

## What I want from you

1. CLOSES or DOES NOT CLOSE on each of your five, citing the `path:line` you
   read. Then judge the token split on its merits: is shipping two forms in
   two documents right, or worse than one form plus a fourth harness fact?

2. **The base rate is twenty numbered dispatches out of twenty.** State it.
   Then either name a new instance of a completion-model hole, a non-binding
   oracle, or an internal contradiction, or say explicitly that you searched
   and found none, and name what you searched.

3. Name anything revision 21 INTRODUCED. It touched Global Constraints,
   region one, the Kimi test literals and passage, Task 1's Files list, Task
   7 step 4, Task 8 step 2, Task 9's expected-result prose and its oracle,
   and the closure text.

4. If the plan is ready, say FREEZE without hedging. If not, name the
   smallest set of changes.

End with PASS, FIX, or ESCALATE.
