Round 5. SHORT POLL, not a review round. Answer only the question below.
Evidence rules as before; cite what you read.

Your round 4 sweep (b) named the fork and I am putting it to you and to a
Claude-side reviewer in parallel. The user decides; you are advising.

THE QUESTION. The launch is a four-step transaction - reserve the directory,
write the wrapper, start the process, publish the pid - and your round 4
finding is that it is currently five literal copies of a snippet with the
rule written elsewhere. Two ways forward:

OPTION A - SHIP A TOOL. `tools/dispatch-detached.ps1` performs all four steps
as one fail-closed unit and publishes a single launch-commit artifact. The
skill's five call sites each become one call to it with lane parameters. The
eighth state you found becomes impossible rather than documented, and the
transaction is tested once, in a real test file, rather than through five
document pins.

The argument against, which is the user's own from the design phase: backlog
item 58, where a run in another repo could not resolve the skill's own
tooling path, landed on the oldest of ten cached plugin copies, and reported
a false BLOCKED. The counter is that the skill already calls
`tools/read-codex-round-evidence.ps1`, `tools/new-review-mirror.ps1` and
`tools/codex-context-probe.ps1` at dispatch time, so this adds a fourth
member to an existing class rather than a new class.

OPTION B - FIVE COPIES, FIVE ORACLES. Keep the copies and bind one exact
site-specific oracle to each of the five call sites, per your own round 4
fix. Add the eighth state to the contract and make the four steps guarded in
each copy.

ANSWER THESE, briefly:

1. Which option, and why. One recommendation, not a survey.
2. Under option A, does item 58 actually get worse, or only wider? Cite what
   you read about how the skill resolves its existing tool paths.
3. Under option B, can five site-bound oracles actually close the eighth
   state, or does a four-step transaction spread across five copied snippets
   keep regenerating it?
4. What does the option you did NOT pick have that the other one loses?

No verdict grammar needed. Keep it under 600 words.
