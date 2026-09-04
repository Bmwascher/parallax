# Item 74 mode-diff debate, round record

Branch `item74-fable-5-1-notes`. Base `5d20eed`. Four rounds, two lanes,
hub-and-spoke and blind: neither lane saw the other's reply, and findings
reached each lane only as anonymized relay in the next round's brief.

## Subject revision per round

| Round | Subject revision | Sol | Fable |
|---|---|---|---|
| 1 | `e0dbb89` | FIX | FIX |
| 2 | `ced2f53` | FIX | FIX |
| 3 | `ee27f27` | FIX | PASS |
| 4 | `fad9b2b` | PASS | FIX |
| 5 | `b9c17bc` | FIX | FIX |

Round 3 is the split. Both lanes named the same five LOCATORS into
`model-prompting-notes.md`, and they disagreed about more than ownership.
The cross-vendor lane called all five stale and all five merge blockers.
The same-harness lane called four stale, treated the fifth - item 66's
`:46-52` - as a historical reference bound to its own cycle by its
wording, and held all of them outside the branch's scope. An earlier
version of this file said the disagreement was "ownership, not facts";
that was wrong, and the cross-vendor lane caught it in round 5 by reading
the retained replies this directory exists to hold.

It was settled by reading the notes at `5d20eed` rather than by
preference: four were already stale at base, and `:46-52` was CORRECT at
base and broken by this branch. So neither lane had it right. Recorded
under item 69 in the backlog.

## What is retained here, and what is not

`whole-branch-review.md` is the required pre-debate whole-branch review,
cited by SHA-256 in the round 1 brief.

`sol-diff-r1-reply.md` through `sol-diff-r4-reply.md` are the cross-vendor
lane's raw replies, copied verbatim from each dispatch directory's `reply`
file.

`fable-diff-r2-reply.md` through `fable-diff-r4-reply.md` are the
same-harness lane's replies, transcribed from the subagent result. That
lane writes no reply file, so these are a transcription rather than a copy
of an artifact, and this file says so rather than let them read as one.

FABLE'S ROUND 1 REPLY IS NOT RETAINED. The session that ran it lost the
agent to a context break before any artifact was written, and the round 1
Fable lane's verbatim text does not survive. What survives is the session's
paraphrase of its findings inside the round 2 brief, which is not the same
thing and is not filed here as if it were. The round 2 Fable lane was a
FRESH dispatch for that reason.

## The continuity answers

Every round after the first opened with a continuity check: name the branch,
the previous subject revision, and the verdict you gave it. That check is
prose with nothing behind it, which is item 67's open complaint, and this
debate demonstrated the gap rather than closing it.

The same-harness lane answered it every time. Its answers are quoted in the
header of each reply file, recovered from the subagent transcript, because
the harness returns only a lane's FINAL message and the answers were not in
it. The lane itself found them missing, in round 5, from its own retained
replies.

The cross-vendor lane did NOT answer it in rounds 2 or 3. Its replies open
straight into the claims (`sol-diff-r2-reply.md`, `sol-diff-r3-reply.md`).
It answered in rounds 4 and 5, in the first line of each reply. Nothing
noticed at the time, and no round was re-run over it. That is the gap, in
this debate's own record.

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

## Why these are retained at all

Round 4 asked both lanes to check an attribution in the backlog and neither
could: the replies were not in the tree. One lane returned it as
UNVERIFIED, the other as an attribution note. Retaining them is the fix.
