# Item 74 mode-diff debate, round record

Branch `item74-fable-5-1-notes`. Base `5d20eed`. Two lanes, hub-and-spoke.

Two different bindings, because an earlier version of this sentence ran
them together and was wrong. THE ROUND TABLE below is complete through
round 8, which is the last. THE INVENTORY and the hash tables describe this directory at the
commit that carries this text, not at any round's subject revision; the
briefs, for instance, entered the directory during round 6 and were absent
at round 6's own subject revision. A count about a tree the document sits
in goes stale on the next edit, which is item 70's convention and has been
broken twice here.

## Blindness, and where it ended

Rounds 1 to 4 were blind. Neither lane saw the other's reply, and findings
reached each lane only as anonymized relay in the next round's brief.

FROM ROUND 5 THE PANEL WAS NO LONGER BLIND. Retaining the replies put both
lanes' words inside the reviewed tree, and both lanes were then asked to
read them: round 5's briefs sent each lane to check the other's round 3
reply, and both did. That was the price of making the round 4 attribution
finding checkable, and it is stated here rather than left under a sentence
claiming blindness throughout. Weigh rounds 5 and later accordingly.

The same-harness lane ran its own contamination check in round 7 and
reported that no finding of its own in rounds 5 or 6 originated in the
other lane's text (`fable-diff-r7-reply.md`, N4). That is its word, not a
measurement, and it is the only such check either lane performed.

## Subject revision per round

| Round | Subject revision | Sol | Fable |
|---|---|---|---|
| 1 | `e0dbb89` | FIX | FIX |
| 2 | `ced2f53` | FIX | FIX |
| 3 | `ee27f27` | FIX | PASS |
| 4 | `fad9b2b` | PASS | FIX |
| 5 | `b9c17bc` | FIX | FIX |
| 6 | `233a340` | VOID, see incident | FIX |
| 7 | `08ba01b` | FIX | FIX |
| 8 | `fa86675` | ATTEST | ATTEST |

ROUND 8 CLOSED THE DEBATE. Both lanes attested the same revision, each with
its own narrowed claim naming what it excludes. Both exclusion lists are in
the round 8 replies; they agree on every item and the same-harness lane
names four more that only it could not check.

Round 3 is the split. Both lanes named the same five LOCATORS into
`model-prompting-notes.md`, and they disagreed about more than ownership.
The cross-vendor lane called all five stale and all five merge blockers.
The same-harness lane called four stale, treated the fifth - item 66's
`:46-52` - as a historical reference bound to its own cycle by its wording,
and held all of them outside the branch's scope.

It was settled by reading the notes at `5d20eed` rather than by preference:
four were already stale at base, and `:46-52` was CORRECT at base and broken
by this branch. So neither lane had it right. Recorded under item 69 in the
backlog.

THAT ERROR TRAVELLED FURTHER THAN THIS FILE. An earlier version here said
the lanes "disagreed on ownership, not on facts". The retained briefs show
the same false premise was put to BOTH lanes in their round 4 briefs
(`sol-diff-r4-brief.md`), so it shaped round 4's adjudication and not only
this summary. The cross-vendor lane caught it in round 5; the same-harness
lane traced its reach in round 7.

## What is retained here, and what is not

`whole-branch-review.md` is the required pre-debate whole-branch review,
cited by SHA-256 in the round 1 brief.

`sol-diff-r1-brief.md` through `sol-diff-r8-brief.md` are the exact texts
piped to the cross-vendor lane, copied verbatim from the dispatch brief
files. That lane confirmed in round 7 that all six then retained were what
it was actually sent (`sol-diff-r7-reply.md`, N2); briefs 7 and 8 were
retained after that check and carry no such confirmation.

`sol-diff-r1-reply.md` through `sol-diff-r8-reply.md` are that lane's raw
replies, copied verbatim from each dispatch directory's `reply` file. There
is NO round 6 reply: that round is void, see the incident.

`fable-diff-r2-reply.md` through `fable-diff-r8-reply.md` are the
same-harness lane's replies, transcribed from the subagent result. That
lane writes no reply file, so these are a transcription rather than a copy
of an artifact, and each file says so rather than let it read as one.

THE SAME-HARNESS LANE'S BRIEFS FOR ROUNDS 1 TO 7 ARE NOT RETAINED. They
were sent as agent messages and no artifact was written, so unlike the
cross-vendor briefs there is nothing to copy. What each lane was asked
therefore differs in how well it can be checked for those rounds.

FROM ROUND 8 BOTH LANES' BRIEFS ARE RETAINED. `fable-diff-r8-brief.md`
exists because that round's brief was written to disk BEFORE it was sent,
which is the practice this debate's own finding produced. Do that from the
first round of the next debate. That file holds the message body from the
continuity check down; the transport prepends one line, which the file's
header states.

FABLE'S ROUND 1 REPLY IS NOT RETAINED. The session that ran it lost the
agent to a context break before any artifact was written, and the round 1
Fable lane's verbatim text does not survive. What survives is the session's
paraphrase of its findings inside the round 2 brief, which is not the same
thing and is not filed here as if it were. The round 2 Fable lane was a
FRESH dispatch for that reason.

## The disclosures the attestation rests on

Recorded here because they otherwise live only in briefs.

Gates at every subject revision from `e0dbb89` to this head: all five green,
2720 passed and 14 skipped, unchanged across every round.

THE BEHAVIOURAL SUITE HAS THREE FAILURES AND THEY ARE BASELINE. Measured
once, in round 1, against the checkout with `--head`: `plan-mode-debate-runs`
2/4, `diff-mode-spec-fidelity` 3/4, `no-manufactured-objections` 1/3. The
same three fail against the installed 0.28.1 cache, none worse.
`plan-mode-debate-runs` improved from 0/4 to 2/4 with `--head`, attributed
to this branch's dispatch fix. It was NOT re-run for any amendment since,
all of which are documentation prose.

THERE IS NO APPLICATION CHECKPOINT FOR THIS BRANCH EITHER. Eight rounds of
fix edits were applied inside the attested range and none was authorized by
a checkpoint artifact; nothing enforces its emission, which is item 59's
complaint and the same gap as the ledger. Recorded here because the
attestation emitter takes a checkpoint argument and this one will be
written without it.

THERE IS NO SDD LEDGER FOR THIS BRANCH. The plan's header requires
`superpowers:subagent-driven-development`, which writes a
`.superpowers/sdd/<date>-<name>/` ledger. None exists. Nothing enforced it.
Disclosed in every round's brief and judged non-blocking by both lanes; it
is item 59's class.

## The continuity answers

Every round after the first opened with a continuity check: name the branch,
the previous subject revision, and the verdict you gave it. That check is
prose with nothing behind it, which is item 67's open complaint, and this
debate demonstrated the gap rather than closing it.

The same-harness lane answered it in every round it was asked, which is
rounds 3 onward; round 2 was a fresh dispatch with no check to answer. Its
answers are quoted in the header of each reply file, recovered from the
subagent transcript, because the harness returns only a lane's FINAL message
and the answers were not in it. The lane itself found them missing, in round
5, from its own retained replies.

The cross-vendor lane WAS ASKED in rounds 2 and 3 and did NOT answer. The
asking is checkable: `sol-diff-r2-brief.md` and `sol-diff-r3-brief.md` both
carry the `<continuity-check>` block. The not-answering is checkable too:
`sol-diff-r2-reply.md` and `sol-diff-r3-reply.md` open straight into the
claims. It answered in rounds 4, 5 and 7, in the first line of each reply.
Nothing noticed at the time and no round was re-run over it. That is the
gap, in this debate's own record.

## Source hashes for the copied replies

SHA-256 of each cross-vendor `reply` file as it was read from its dispatch
directory.

TO REPRODUCE ONE: take the retained file's bytes after the `---` separator
line, and REMOVE THE SINGLE TRAILING NEWLINE the retention appended. Hashing
the retained body as stored does NOT reproduce these values. An earlier
version of this section said it did; the cross-vendor lane checked and
reported that none of the five matched, which is the whole reason a hash
table belongs here.

These hash the SOURCE artifact, not the retained file, deliberately. This
repository normalizes line endings on checkout, so a byte hash of a
retained file is not stable across clones, while the source hash is a fixed
fact about what the lane produced.

| Round | SHA-256 of the source `reply` |
|---|---|
| 1 | `ee8312b25921db96fa4af6b1005d867bdf4e80cc226a957ba2e391cdba7f19c9` |
| 2 | `0531bd1558671350e08cffb413a80cc8118fd757210c5c00008e6355af3b13fa` |
| 3 | `66b890e18033291994733f7f712ea6c5173a6ed55922ebf183ad3a97c07e95ca` |
| 4 | `ce07a4649e2673c887f2603a71d53676f0e5456c386ff93637dd8d37f381802a` |
| 5 | `475051dd0be4f788eb78ae78c3bb3a0d08342ad246c1765d1278475a5b9424ac` |
| 7 | `73c62591d6e9d9135eb4eab6c32be1e1033fc801f45c154869ec57f583be1627` |
| 8 | `cc7efd90cc8b487432e2585a553d24b683456e5d858acc250e495f763525e41c` |

The same-harness lane's replies have no such artifact. They are
transcriptions, and nothing hashes them.

## INCIDENT: the cross-vendor round 6 was voided by the session, 2026-09-04

That lane's round 6 dispatch ran to completion and then FAILED its own
post-run check with `the mirror changed while the round ran`. The wrapper
exited 1, which under the dispatch contract is not `reply-present`, so THE
ROUND IS NOT EVIDENCE and its output was not read. The wrapper's exit code
is the classification; the dispatch directory was not re-opened to argue
otherwise.

The cause was the session, not the tool. While the round was running, the
session wrote the six `sol-diff-r*-brief.md` files into the repository.
Untracked files move `git status`, the source fingerprint is built from what
status names, and the gate at `tools/dispatch-round.ps1` fired as designed.

The cost is real and is recorded rather than smoothed over: the round's
quota was spent, the lane answered, and the answer is unusable. The session
rollout grew from 1,510,090 to 1,768,331 bytes, so the work happened. AND
THE REMEDY COST A SECOND DISPATCH: round 7 re-asked that lane at the next
head, so the void's true price is two rounds of quota, not one.

WHAT IT MEANT FOR THE VERDICTS, which the first version of this note left
out and the same-harness lane demanded in round 7: for as long as the void
stood, the cross-vendor lane's last valid word on this branch was round 5's
FIX on `b9c17bc`, two revisions back, and its own round 5 findings had been
applied in `233a340` without that lane ever confirming them. The branch was
NOT attestable in that state. It was resolved by re-dispatching that lane at
round 7 against `08ba01b`, with the void disclosed to it in its own brief
(`sol-diff-r7-brief.md`). Its round 7 reply is retained and its verdict is
in the table.

THE RULE IS IN THE TOOL, NOT IN THE SKILL TEXT. `tools/dispatch-round.ps1`
enforces it; no prose rule in `skills/` says "do not touch the reviewed tree
between `-Prepare` and the wrapper's exit". An earlier version of this note
called the rule "already written", which implied skill text that does not
exist.

AN EARLIER INCIDENT IS ASSERTED HERE WITHOUT EVIDENCE, and is kept only
because dropping it would hide a repeat. During round 1 setup the same
identity gate fired, twice, because the session had edited the backlog
between building the mirror and dispatching. It fired at PREPARE and
refused to proceed, so no round ran and no quota was spent; the fix was a
rebuild with `-Force` and a fresh override path. That is a materially
different outcome from this incident and is not a second instance of it.
Nothing in this directory records it; it is the session's own recollection
and no artifact survives.

## Why the replies are retained at all

Round 4 asked both lanes to check an attribution in the backlog and neither
could: the replies were not in the tree. One lane returned it as UNVERIFIED,
the other as an attribution note. Retaining them is the fix, and it is what
cost the panel its blindness from round 5 on.
