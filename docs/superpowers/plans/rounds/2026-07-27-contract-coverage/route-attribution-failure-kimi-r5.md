# Route-attribution failure — 0.15.0 plan debate, Kimi round 5

Date: 2026-07-27
Lane: Kimi backup lane, mode `plan`, panel round 5.
Disposition: reply DISCARDED unread, quarantined, no retry, consent gate.
Artifact: `QUARANTINED-kimi-r5-reply-UNREAD.md`. Never opened. Not
evidence and must not enter any debate record.

## What the rule requires

`references/backup-lane.md`: past the captured offset, require exactly
one new `Using LLM model:` line, one `Loading agent:` line naming the
committed yaml, and one `Loaded tools:` line equal to the allowlist.
"Zero matching new lines, more than one, a wrong id, a wrong agent path,
or any extra tool entry is a route-attribution failure."

## What was observed

Window: offset 91430 to 106330. No rotation: file identity (creation time
`2026-07-27T15:34:43.2752960-05:00`) unchanged across the call, and the
file grew. The rotation guard passed.

Two complete sets of route lines appeared in the window:

| time | event | session |
|---|---|---|
| 18:42:48 | `Resuming session` | `049ce8a8-b55a-4be2-a41d-d3d81104faba` |
| 18:43:34 | `Created new session` | `49d54441-69e6-403d-9971-b79be160eabf` |

This session dispatched a RESUME of `049ce8a8` and created no new
session. `49d54441` belongs to a concurrent kimi call on the same user
account, from another project.

## What is and is not established

**Containment held, on evidence independent of the log.** Both entries
carried `Loaded tools:` equal to the five-tool allowlist and the
committed reviewer yaml, and the mirror status delta against baseline was
exactly the declared expected untracked set (`KIMI-REVIEW-BRIEF.md`) and
nothing else.

**Attribution is lost.** With two calls in one window, the log cannot
establish which lines belong to this call. The reply is very likely the
correct one, and that is exactly why the rule is mechanical rather than
adjudicated: "probably mine" is not attribution.

## This is the SECOND occurrence in this same debate

Round 1 of this debate was discarded for the identical cause, recorded in
`route-attribution-failure-r1.md` and filed as backlog item 6. The rule
fired correctly both times; what it caught both times was a scheduling
collision, not a misroute.

The recurrence raises the cost estimate on item 6 from "discarded a paid
round once" to "discarded two of six dispatched rounds in a single
debate". The offset rule assumes serial use of a user-global log, and
nothing in the lane warns a driver that a concurrent session will
invalidate its evidence before the round is spent.

## Disposition

Per fallbacks.md: no retry, consent gate. The user decides whether to
spend another round. Nothing was retried automatically.

The Sol lane's round 5 was unaffected — a different transport with its
own evidence — and its findings were adjudicated normally.
