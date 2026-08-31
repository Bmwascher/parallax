# Round 15 - every unpropagated consequence you named

You are the cross-vendor reviewer on backlog item 32 (detached dispatch) and
item 33 (automatic review mirror). This is round 15. Your round 14 reply is
above in this session.

The mirror is a fresh file copy of the working tree at source commit
`32026b1` on branch `item32-detached-dispatch`. Its own `HEAD` is the
builder's remediation commit, by construction. The plan file in the mirror
was hash-compared to the source before dispatch and is identical.

The plan is `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md`.
The spec is
`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md`.

Ground every claim in a `path:line` you actually opened in this mirror.

## Your round 14 findings

All accepted. Your sweep for unpropagated consequences is what this round
answers, and it found more of them than my own reading did.

**1. The four stale LAUNCH UNKNOWN associations.** All four replaced. The
opening now says the irreducible hard-kill case leaves NO RECEIPT and states
that LAUNCH UNKNOWN has become narrower - a valid receipt whose marker has
since disappeared. The residual comparison, the DECLARED_REGIONS rationale,
and item 32's closure text all follow.

**2. The spec's orphan section.** Task 9 now schedules it for replacement by
name. You were right that it is backwards for the dangerous case: it claims
the orphan half has a documented answer because the pid is on disk, when the
interrupted launch may have no pid at all. The instruction is to rewrite it
so the pid is on disk for every COMMITTED launch, and the interrupted one is
the residual the contract names and does not remedy.

**3. LIVENESS IS CHECKED FIRST.** Task 9 now names `design.md:190-194` for
replacement, and the convergence grep gained both `LIVENESS IS CHECKED
FIRST` and `the pid is on disk, so a session can find`.

**4. The positive oracle missed `-ExpectedRound`.** It now requires six
tokens, not three: the three it had, plus `-ExpectedRound`, `no-receipt` and
`receipt-not-expected`, so the receipt-last consequences must actually
appear in the mechanism section rather than being merely not-contradicted.

**5. The debate record.** You were right that the count was
prompt-supplied while the document recorded only four rounds. It now records
fourteen, plus the poll, plus the round the evidence binder refused and I
discarded unread. It states plainly that rounds 1 to 9 each found a
completion path and rounds 10 to 14 found none, and it names round 13 as the
deepest finding after round 4.

## What I want from you

1. For each of your round 14 findings, say CLOSES or DOES NOT CLOSE, citing
   the `path:line` you read. Check the debate record I just wrote against
   what you actually said in those rounds; if I have overstated or
   misattributed anything, name it.

2. **The base rate is fourteen rounds out of fourteen** finding at least one
   completion-model hole, a non-binding oracle, or an internal
   contradiction - though rounds 10 through 14 all found NO new
   false-completion path. State the base rate. Then either name a new
   instance of any of the three kinds, or say explicitly that you searched
   and found none, and name what you searched.

3. Sweep once more for unpropagated consequences, which is now the only
   class still producing findings. Revision 14 touched the plan's opening,
   the residual bullet, the DECLARED_REGIONS rationale, item 32's closure
   text, two Task 9 paragraphs, the convergence grep, the positive oracle,
   and the whole debate record.

4. Say whether this plan is ready to freeze and execute. If not, name the
   smallest set of changes. If it is ready, say so without hedging and give
   me the honest FLOOR: what these nine tasks will NOT have verified when
   they are all done.

End with PASS, FIX, or ESCALATE.
