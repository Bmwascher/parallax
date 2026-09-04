# Item 74 mode-diff debate, round record

Branch `item74-fable-5-1-notes`. Base `5d20eed`. Two lanes, hub-and-spoke.
Counts in this file are bound to `233a340` and this directory's own state
at that commit; a count about a tree the document sits in goes stale on the
next edit, which is item 70's convention and was broken once here already.

At `233a340`: six rounds dispatched, five answered by both lanes and
recorded below. Round 6 was invalidated for the cross-vendor lane; see the
incident note at the end.

## Blindness, and where it ended

Rounds 1 to 4 were blind. Neither lane saw the other's reply, and findings
reached each lane only as anonymized relay in the next round's brief.

FROM ROUND 5 THE PANEL WAS NO LONGER BLIND. Retaining the replies put both
lanes' words inside the reviewed tree, and both lanes were then asked to
read them: round 5's briefs sent each lane to check the other's round 3
reply, and both did. That was the price of making the round 4 attribution
finding checkable, and it is stated here rather than left under a sentence
claiming blindness throughout. Weigh rounds 5 and later accordingly.

## Subject revision per round

| Round | Subject revision | Sol | Fable |
|---|---|---|---|
| 1 | `e0dbb89` | FIX | FIX |
| 2 | `ced2f53` | FIX | FIX |
| 3 | `ee27f27` | FIX | PASS |
| 4 | `fad9b2b` | PASS | FIX |
| 5 | `b9c17bc` | FIX | FIX |
| 6 | `233a340` | VOID, see below | FIX |

Round 3 is the split. Both lanes named the same five LOCATORS into
`model-prompting-notes.md`, and they disagreed about more than ownership.
The cross-vendor lane called all five stale and all five merge blockers.
The same-harness lane called four stale, treated the fifth - item 66's
`:46-52` - as a historical reference bound to its own cycle by its wording,
and held all of them outside the branch's scope. An earlier version of this
file said the disagreement was "ownership, not facts"; that was wrong, and
the cross-vendor lane caught it in round 5 by reading the retained replies
this directory exists to hold.

It was settled by reading the notes at `5d20eed` rather than by preference:
four were already stale at base, and `:46-52` was CORRECT at base and broken
by this branch. So neither lane had it right. Recorded under item 69 in the
backlog.

## What is retained here, and what is not

`whole-branch-review.md` is the required pre-debate whole-branch review,
cited by SHA-256 in the round 1 brief.

`sol-diff-r1-brief.md` through `sol-diff-r6-brief.md` are the exact texts
piped to the cross-vendor lane, copied verbatim from the dispatch brief
files.

`sol-diff-r1-reply.md` through `sol-diff-r5-reply.md` are that lane's raw
replies, copied verbatim from each dispatch directory's `reply` file.

`fable-diff-r2-reply.md` through `fable-diff-r5-reply.md` are the
same-harness lane's replies, transcribed from the subagent result. That
lane writes no reply file, so these are a transcription rather than a copy
of an artifact, and each file says so rather than let it read as one.

THE SAME-HARNESS LANE'S BRIEFS ARE NOT RETAINED. They were sent as agent
messages and no artifact was written, so unlike the cross-vendor briefs
there is nothing to copy. What each lane was asked therefore differs in how
well it can be checked, and the next debate should write every brief to
disk before sending it.

FABLE'S ROUND 1 REPLY IS NOT RETAINED. The session that ran it lost the
agent to a context break before any artifact was written, and the round 1
Fable lane's verbatim text does not survive. What survives is the session's
paraphrase of its findings inside the round 2 brief, which is not the same
thing and is not filed here as if it were. The round 2 Fable lane was a
FRESH dispatch for that reason.

## The disclosures the attestation rests on

Recorded here because they otherwise live only in briefs.

Gates at every subject revision from `e0dbb89` to `233a340`: all five green,
2720 passed and 14 skipped, unchanged across every round.

THE BEHAVIOURAL SUITE HAS THREE FAILURES AND THEY ARE BASELINE. Measured
once, in round 1, against the checkout with `--head`: `plan-mode-debate-runs`
2/4, `diff-mode-spec-fidelity` 3/4, `no-manufactured-objections` 1/3. The
same three fail against the installed 0.28.1 cache, none worse.
`plan-mode-debate-runs` improved from 0/4 to 2/4 with `--head`, attributed
to this branch's dispatch fix. It was NOT re-run for any of the five
amendments, all of which are documentation prose.

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
claims. It answered in rounds 4 and 5, in the first line of each reply.
Nothing noticed at the time and no round was re-run over it. That is the
gap, in this debate's own record.

## Source hashes for the copied replies

SHA-256 of each cross-vendor `reply` file as it was read from its dispatch
directory. The retained file is that content with a header prepended above
the `---` separator; hashing the retained body below the separator
reproduces the value. The dispatch directories are temporary and will not
survive, so these are recorded rather than the artifacts.

| Round | SHA-256 of the source `reply` |
|---|---|
| 1 | `ee8312b25921db96fa4af6b1005d867bdf4e80cc226a957ba2e391cdba7f19c9` |
| 2 | `0531bd1558671350e08cffb413a80cc8118fd757210c5c00008e6355af3b13fa` |
| 3 | `66b890e18033291994733f7f712ea6c5173a6ed55922ebf183ad3a97c07e95ca` |
| 4 | `ce07a4649e2673c887f2603a71d53676f0e5456c386ff93637dd8d37f381802a` |
| 5 | `475051dd0be4f788eb78ae78c3bb3a0d08342ad246c1765d1278475a5b9424ac` |

The same-harness lane's replies have no such artifact. They are
transcriptions, and nothing hashes them.

## INCIDENT: round 6 was invalidated by the session, 2026-09-04

The cross-vendor lane's round 6 dispatch ran to completion and then FAILED
its own post-run check with `the mirror changed while the round ran`. The
wrapper exited 1, which under the dispatch contract is not `reply-present`,
so THE ROUND IS NOT EVIDENCE and its output was not read. The wrapper's exit
code is the classification; the dispatch directory was not re-read to argue
otherwise.

The cause was the session, not the tool. While the round was running, the
session wrote the six `sol-diff-r*-brief.md` files into the repository, in
response to the same-harness lane's round 6 finding that the briefs were not
retained. Untracked files move `git status`, the source fingerprint is built
from what status names, and the gate fired exactly as designed.

The cost is real and is recorded rather than smoothed over: the round's
quota was spent, the lane answered, and the answer is unusable. The session
rollout grew from 1,510,090 to 1,768,331 bytes, so the work happened. This
is the second time in this debate that a mid-round edit tripped the identity
gate; the first was in round 1 and was also the session's doing.

The rule this breaks is simple and already written: do not touch the
reviewed tree between `-Prepare` and the wrapper's exit.

## Why the replies are retained at all

Round 4 asked both lanes to check an attribution in the backlog and neither
could: the replies were not in the tree. One lane returned it as UNVERIFIED,
the other as an attribution note. Retaining them is the fix, and it is what
cost the panel its blindness from round 5 on.
