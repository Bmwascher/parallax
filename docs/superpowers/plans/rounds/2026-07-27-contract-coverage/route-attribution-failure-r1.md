# Route-attribution failure — 0.15.0 plan debate, round 1

Date: 2026-07-27
Lane: Kimi backup lane, mode `plan`
Disposition: reply DISCARDED unread, quarantined, no retry, consent gate.
Artifact: `QUARANTINED-kimi-r1-reply-UNREAD.md`. Never opened. Not
evidence and must not enter any debate record.

## What the rule requires

`references/backup-lane.md`: past the captured offset, require exactly
one new `Using LLM model:` line, one `Loading agent:` line naming the
committed yaml, and one `Loaded tools:` line equal to the allowlist.
"Zero matching new lines, more than one, a wrong id, a wrong agent path,
or any extra tool entry is a route-attribution failure."

## What was observed

Window: offset 25991 to 40788. No rotation: file identity (creation time
`2026-07-27T15:34:43.2752960-05:00`) unchanged across the call, and the
file grew. The 0.14.4 rotation guard passed.

Two complete sets of route lines appeared in the window:

| time | event | session |
|---|---|---|
| 16:08:44 | `Created new session` | `08d55837-99ba-4a1f-8a03-dd7d622b3017` |
| 16:10:22 | `Resuming session` | `29d43d90-d43d-4cb2-a247-95b462f5e55f` |

The second carried the command `Round 2. Re-read KIMI-REVIEW-BRIEF.md in
this workspace; it has been replaced with the round-2 position.` This
session dispatched no round 2 and never created session `29d43d90`. It
belongs to a concurrent debate in another project on the same user
account.

## What is and is not established

**Containment held, on evidence independent of the log.** No marker file
on disk, mirror status delta against baseline empty, `Loaded tools:`
equal to the five-tool allowlist on both entries.

**Attribution is lost.** With two calls in one window, the log cannot
establish which lines belong to this call. The reply is very likely the
correct one, and that is exactly why the rule is mechanical rather than
adjudicated: "probably mine" is not attribution.

## Why this is a lane defect, not a lane success

The rule fired correctly, but what it detected was not a substitution
attempt or a misroute. It was a scheduling collision. The offset rule
assumes serial use of a user-global log; nothing in the lane defends
against two sessions running at once on one machine, and nothing warns a
driver that a concurrent session will invalidate its evidence.

Recorded as backlog item 6.
