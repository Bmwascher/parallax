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

Round 3 is the split. Both lanes found the same five stale numeric cites
into `model-prompting-notes.md` and disagreed on OWNERSHIP, not on facts.
It was settled by reading the notes at `5d20eed` rather than by preference:
four were already stale at base, one was correct at base and broken by this
branch. Recorded under item 69 in the backlog.

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

## Why these are retained at all

Round 4 asked both lanes to check an attribution in the backlog and neither
could: the replies were not in the tree. One lane returned it as
UNVERIFIED, the other as an attribution note. Retaining them is the fix.
