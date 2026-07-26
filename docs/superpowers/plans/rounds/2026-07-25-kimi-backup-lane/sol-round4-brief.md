# Mode plan, round 4 — one-row post-convergence delta; confirmation requested

Evidence rules and verdict grammar as before. Both lanes reached
terminal PASS at f5fc46c (the second lane's round 3 landed after its
quota window reset — its transcript is retained). One session-raised
delta was then applied at e128efb, and per the freeze rule it needs
reviewer confirmation before the plan freezes:

THE DELTA (only change; `git diff f5fc46c..e128efb` is 10 inserted
lines in the plan file): the Task 4 backup failure table gains a
`kimi-quota-exhausted` row, and the Task 1 fallbacks-wiring test gains
`assert "access_terminated_error" in fb`. The row is pinned from a LIVE
event during this very debate: the second lane's first round-3 attempt
failed with HTTP 403 `access_terminated_error` whose text said
"billing cycle" — while the user's quota dashboard showed 6.42% monthly
usage; the exhausted window was the 5-HOUR one, and the retry after its
reset succeeded. The row therefore: skips the in-window retry, warns
that the error text cannot identify WHICH window died, names the
dashboard (5-hour / 7-day / monthly) as the reset-horizon authority
quoted at the consent gate, and notes the kimi session id in the debate
record for post-reset resumption.

Confirm: the row is internally consistent with the surrounding table
(fallbacks.md remains the single failure-class home), the new test pin
matches the shipped row text, and nothing else moved. End with a
verdict on the candidate at e128efb: PASS / FIX / ESCALATE.
