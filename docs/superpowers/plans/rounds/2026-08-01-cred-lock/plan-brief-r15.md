Round 15. This round applies your four blocking round-14 fixes and asks you to
re-confirm or reject. The plan is now at revision 14 in its own header. Evidence
rules and verdict grammar as before: cite `path:line` for every claim, and end
with per-task verdicts plus an overall verdict and a Final check section listing
what you could NOT verify.

I accepted all four blocking fixes without argument. I contest nothing this
round. Two of your items had a consequence you did not name that I fixed as
well, and I flag both below so you can reject them if I read them wrong.

## What changed, by your item

### Task 3, item 1 — separate normalized `debateHome` comparison

The "not part of the comparison" sentence is gone. Replaced at
`docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:196` with the
two-stage shape you specified, stated as: excluded from holder-identity
equality but compared separately after all five identity fields match. The
paragraph also says why the two stages are not the same question — five fields
decide WHO holds the lock, `debateHome` then decides whether that holder is
talking about the debate it thinks it is — and why a mismatch cannot be
contention.

The five identity fields are named immediately above at `:194`.

### Task 3, item 2 — the equality rule

Frozen at `:198`: `[System.IO.Path]::GetFullPath()` to an absolute path, then a
single trailing directory separator trimmed, then ORDINAL CASE-INSENSITIVE
comparison. Required tests: two EQUIVALENT SPELLINGS of one path, specified as
a relative form and a trailing-separator form, and a genuinely different path.

### Task 3, item 3 — routing UNMEASURABLE through Acquire

At `:215`. The rule is stated as a delta against the table rather than as six
new rows, so the table cannot drift from it: a same-host UNMEASURABLE holder
follows every row above that is not the DEAD row, and is treated exactly as
LIVE for routing. All four directions are spelled out: exact identity with an
equal `-DebateHome` is idempotent, a differing `-DebateHome` is exit 2, any
competing identity contends, nothing reclaims.

Both seam directions are required tests, as you asked: an exact-identity
re-acquire under the seam succeeds idempotently, and a competing identity under
the seam contends rather than reclaiming.

**Consequence you did not name, which I fixed.** You said "update code 3
accordingly." The prose at `:215` says code 3 covers a LIVE or UNMEASURABLE
holder alike, but the exit-code table row still said only "a LIVE holder,"
which is exactly the two-definitions shape you made me fix for `host` at r7.
The row at `:178` now reads "a holder that is LIVE or UNMEASURABLE."

### Task 3, item 4 — foreign-host Status liveness

At `:250`. `UNKNOWN`, always, and the local process table is NOT consulted at
all. The reason is on the record: the recorded pid may coincidentally match an
unrelated local process, and reading it would report another machine's holder
as LIVE or DEAD on the strength of a collision. Its oracle: a foreign-host
record whose recorded pid IS a live local process must still report `UNKNOWN`.

The three liveness outcomes and the deciding-versus-reporting split sit at
`:246` and `:248`.

### Task 3, the row reference

`:213` now reads "Rows 5 and 6" and states that after the split row 4 is the
`-DebateHome` refusal.

### Task 6, item 1 — the wrong-`-Path` integration oracle

At `:380`, written as its own required test with its own justification —
"because Task 3 now excludes `debateHome` from identity and 'identity mismatch'
no longer covers it". The procedure is the one you specified: build home A,
prepare a distinct valid disposable home B, then call `-Remove` on B carrying
A's five identity fields and A's nonce; require exit 2, NO deletion, and both
homes and the lock byte-identical.

### Task 6, item 2 — the post-deletion release-failure oracle

Also at `:380`. A Remove-only seam firing immediately after deletion and before
release makes the internal release return a fixed code 5. Required: home
ABSENT, the original held record UNCHANGED, exit 5, the failure on stderr, and
NO `removed <path>` on stdout, with a direct release performed as teardown. The
text also records why Task 7's matrix does not reach this branch.

The precedence this oracle tests is at `:372`, unchanged from r13.

### Task 7 — C's creation

At `:412`: "C is created third, by steps 1 through 4 and 6, EXPLICITLY OMITTING
step 5." The self-contradiction is named in the same sentence, and the reason
only A and B need markers is stated.

### Task 8 — the two explicit pins

At `:572`, introduced with the reason the generic instruction was inadequate.
Pin one: the `UNKNOWN` row's `N/A` verdict TOGETHER WITH its required detail —
that liveness could not be determined and that no mutating mode will reclaim —
so mapping `UNKNOWN` to `OK` or `STALE` fails. Pin two: the foreign-host
branch's CASE-INSENSITIVE comparison of the record's `host` against
`$env:COMPUTERNAME`, together with its complete `-ForceRelease -ConfirmHost ...`
recovery command, so a case-sensitive comparison fails.

The `UNKNOWN` row itself is at `:540`.

## The UNVERIFIED item I could close

You listed the fable-reviewer report as UNVERIFIED because no artifact existed
to inspect, and you were right that a plan recording its own review is not
verification. The raw reply is now retained at
`docs/superpowers/plans/rounds/2026-08-01-cred-lock/fable-whole-plan-review.md`,
verbatim, with the dispatch context and my per-finding adjudication appended
below a rule. Read it directly. It is a review of the plan at revision 12 and
the spec at revision 2, so its line citations point at r12 line numbers, not
today's.

Two gaps that review named in ITSELF I have since closed, and the artifact says
so: it could not run `git show`, so the deleted-predecessor citations were
unverified there — I confirmed them; and it could not check the never-pushed
claim — I established that with `git branch -r --contains HEAD` (empty),
`git ls-remote --heads origin` (only `refs/heads/main`), and `gh run list` (no
runs).

Your other three UNVERIFIED items stand as you wrote them. Measurements 1-21
remain external, the three-login generalization remains a generalization with a
loud refusal direction, and no implementation exists.

## The revision record

`:15` is the new r14 entry. It records your agreement with both judgment calls
and the reasons you gave, then each of the four blocking fixes and what was
wrong before. `:5` now says revision 14, awaiting re-review.

## What I want from you

1. Is this a PASS? The user lifted the round cap and directed that this plan
   iterate until you issue an actual PASS, so "converged with amendments" is
   not a terminal state here. If any of the eight changes is inadequate, say
   which and what would be adequate.

2. The two consequences I fixed beyond your literal items — the exit-code 3 row
   at `:178`, and stating the UNMEASURABLE rule as a delta against the acquire
   table rather than as new rows — are my reading of your intent, not your
   instructions. Reject either if I read it wrong. The delta form in particular
   is a trade: it cannot drift from the table, but it does require the reader
   to hold two paragraphs at once.

3. If PASS, building starts immediately, task by task, by a zero-judgment
   implementer with no access to this debate. Say plainly whether Task 1 is
   safe to start from its own text alone.
