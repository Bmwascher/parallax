# Debate record — parallax 0.15.0 contract coverage (mode plan)

**Subject:** the design spec and implementation plan for backlog item 1,
reviewed before any implementation. Nothing was built during this debate.

- `docs/superpowers/specs/2026-07-27-contract-coverage-design.md`
- `docs/superpowers/plans/2026-07-27-contract-coverage.md`

**Final revision:** `add7c07`. Round 1 reviewed `d8c1a54`; round 2
reviewed `18f948d`; the round-2 fix landed as `add7c07`.

**Verification status:** FULL. The reviewer lane is cross-vendor, no
substitution occurred, and no degraded mode was entered.

**Lane selection:** user-directed, Kimi solo, 2 rounds, on quota grounds.
Codex sits at 77% of a window that resets Aug 1 and was probed healthy
the same day. This is fallbacks.md's "available on user request" route,
not a substitution for a failed primary.

## Why this debate happened late

The spec and plan were written and self-reviewed, then offered for
execution. The user asked whether they had been reviewed. They had not.
This debate is that review, run on finished documents rather than during
their construction. Recorded because the omission is the failure mode the
plugin exists to prevent, and a record that hides it teaches nothing.

## Round 1 — discarded unread

The first dispatch was DISCARDED UNREAD under the route-attribution rule:
two calls wrote route lines into one measurement window, this session's
at 16:08:44 and another project's round 2 at 16:10:22. Full record and
evidence: `route-attribution-failure-r1.md`. The reply is quarantined at
`QUARANTINED-kimi-r1-reply-UNREAD.md` and never entered this debate.

Disposition per fallbacks.md: no retry, consent gate. The user chose
re-dispatch once the other project went idle. That is the recorded
consent for the re-run; nothing was retried automatically.

The collision is now backlog item 6. The rule fired correctly and what it
caught was a scheduling collision, not a misroute.

## Route evidence

`effective route confirmed` under backup-lane.md's per-round rules, for
the write-probe and both counted rounds. Each window carried exactly one
`Using LLM model:` line with the canonical id, one `Loading agent:` line
naming the committed yaml, one `Loaded tools:` line equal to the
five-tool allowlist, and exactly one session event.

Rotation guard: file identity (creation time
`2026-07-27T15:34:43.2752960-05:00`) unchanged across every call, and the
log grew each time. This is the first cycle to check identity as well as
length, which the 0.14.3 residual-gap paragraph instructed once rotation
began succeeding. It began succeeding earlier the same day.

Session `049ce8a8-b55a-4be2-a41d-d3d81104faba`, all four flags re-pinned
on the resume.

**Effort evidence:** NO VERIFIED EFFORT PIN. `~/.kimi/config.toml` still
carries no `overrides` block for the canonical id.

## Workspace

File-copy mirror preserving `.git`, no tracked modifications, baseline
and content manifest captured together at 121 entries. Preflight-3 sweep
empty in both the real tree and the mirror. Write-probe PASS on all three
conditions: explicit refusal, marker absent, mirror delta empty.

## Findings

**Round 1: FIX, on ten PASSes and two corrections.** The mechanism itself
was confirmed on every load-bearing point the lane could check against
the live tree, including the six-sentence split of the rotation guard,
the five unlocked sentences the session had first predicted were covered,
and the containment direction.

| finding | disposition |
|---|---|
| "fallbacks.md defines eleven failure classes" is derivable from no counting rule | ACCEPTED. Verified independently: ten `###`-headed entries, five backticked class names. Replaced the total with the selection rule and two anchors. |
| "wrap only the two operative sentences" where the specified body is one sentence | ACCEPTED, wording corrected. |
| "529 existing assert statements" (raised as UNVERIFIED, not as a finding) | ACCEPTED and it was wrong: 529 counted three files while the text implied the suite. The suite is 633 across five modules. Both documents now say 633 and name the glob. |
| instance-12 fixture merges a bold heading into the next sentence | NOT ACTED ON. The fixture's job is to prove the checker goes red on that historical state. Special-casing markdown emphasis would add a rule with no failure behind it; editing historical evidence would be worse. |
| pin-sync friction will grow as regions accumulate, with no weakening valve | NOT ACTED ON, agreed on the record. The absence of a valve is the design intent, because the repo's prior failure was weakening a perpetually-red check. |

**Round 2: FIX, one item, then PASS.** The amendment left the invented
number alive by arithmetic: "The other nine get marked as they are next
edited" still implied eleven, inside the paragraph rewritten to remove
it. Accepted and corrected to "The rest". The lane stated the condition
for PASS explicitly, which makes this converged with amendments under
debate-protocol.md rather than an open dispute.

**Session final adjudication.** Verified the round-2 finding against the
live file before acting, applied it, and swept both documents for any
surviving trace of `eleven`, `other nine`, or `529`. None remain. Gates
re-run after the docs-only change: 170 passed, 1 skipped.

## Terminal verdict

**PASS.** The mechanism, the six regions, the containment direction, and
the task order are confirmed. Every finding across both rounds was a
factual error in the documents, not a design objection; the reviewer
raised no objection to coverage as the approach, which was the question
most in need of an outside opinion because the session had recommended it
unreviewed.

## Carried

- Backlog item 6, the concurrent-session collision, has a live cost: it
  discarded a paid round of this very debate.
- The pin-sync friction debate is expected later, not pre-empted.
