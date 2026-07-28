Round 4, mode diff. Fix re-review, narrow. Evidence rules and verdict grammar as before.

POSITION CHANGE. R2 ACCEPTED in full. You were right and the counterexample is decisive: distinct session ids are necessary and not sufficient, because the round-numbered reply and transcript names the freshness rule requires are unique WITHIN a debate and not across two debates running at once. Two callers both writing `reply-r1.md` can truncate or overwrite each other and pair one session's header with another session's reply. My three-call probe used distinct paths, so it proved the arrangement it exercised and nothing wider. I have said that in the note rather than leaving the probe looking like a general proof.

The note now reads: safe across distinct session ids THAT ALSO USE DISTINCT FILES; each concurrent invocation must write its own transcript and reply paths; resuming one session twice is never safe. Your narrowing is adopted verbatim in substance — "no shared global output log is parsed for route attribution" — and the note now says plainly that codex still shares auth, config, session storage and quota, none of which is read as evidence.

Your R1, R3 and R4 PASSes are not re-opened. Your R1 inventory correction is noted and needs no change: the drift state-machine test pins `powershell.exe` because the scheduled task does, which the README already states.

WHAT WAS APPLIED. Range `11f28ce..9ff5558`, one commit, 46 diff lines, documentation only. Diff at C:\Users\Brandon\.claude\jobs\75fb2cba\tmp\diff-0161-r4.txt

284 passed, 1 skipped. Static gates clean. CI is now GREEN on both jobs for BOTH `f527301` and `11f28ce` — skill-evals on ubuntu and powershell-hosts on windows — so the host gap has independent confirmation twice. This commit's run is not in yet.

CLAIMS FOR THIS ROUND. One only.

R1. THE CONCURRENCY NOTE IS NOW TRUE AND COMPLETE ENOUGH TO ACT ON. A driver reading it should be able to run two debates at once without corrupting either, and should know the two things that would. Is any condition still missing, is any sentence still asserting more than was probed, and does the distinct-files requirement need to name WHICH files rather than describing them?

Nothing else is under debate. This is a documentation-only range; if it holds, say PASS plainly and say it first.
