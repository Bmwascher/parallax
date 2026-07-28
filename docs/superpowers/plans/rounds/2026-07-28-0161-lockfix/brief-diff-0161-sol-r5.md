Round 5, mode diff. Fix re-review. Documentation only. Evidence rules and verdict grammar as before.

Both corrections ACCEPTED, adopted in substance as you wrote them.

1. All three caller-selected files are named. The rule is now: each concurrent debate uses its own scratch DIRECTORY, or its own `<brief-file>`, `<reply-file>` and `<transcript-file>` paths — all three, and the note says WHY the brief is included: it is read back by the dispatch, so a second debate can overwrite it before that read even when the output paths differ. It also states that later rounds send the rebuttal inline, so from round 2 only reply and transcript need uniqueness.

2. "None of that is read as evidence" is gone. The note now says the opposite where it was wrong — `codex login status` is the auth preflight and config resolution is what the header reports, so both ARE consulted — and then states the precise claim: none of those stores is a shared global output log, and none is parsed to attribute one invocation's transcript or reply to another.

WHAT WAS APPLIED. Range `9ff5558..f41b95f`, one commit, 37 diff lines, one file. Diff at C:\Users\Brandon\.claude\jobs\75fb2cba\tmp\diff-0161-r5.txt

284 passed, 1 skipped. Static gates clean. CI green on both jobs for `f527301` and `11f28ce`; the run for `9ff5558` was still in flight when I dispatched this.

CLAIM. One.

R1. THE NOTE IS NOW ACTIONABLE AND SAYS NOTHING FALSE. A driver reading only this bullet should be able to run two debates at once safely, and should know precisely what would break it. Is any condition still missing, does any sentence still claim more than was probed, and is the round-2-onward relaxation stated correctly given how the transport actually sends a rebuttal?

This is the fifth round on a fix for a defect that shipped. If it holds, say PASS plainly and say it first; do not manufacture an objection to justify the round.
