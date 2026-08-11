# 0.24.0 debate record — the reviewer's tool surface, the agy contracts

Backlog items 7 and 11. Branch `0.24.0-tool-surface-agy-drift`.

Reviewer lane: codex `gpt-5.6-sol`, effort `high`, sandbox `read-only`,
isolation flags plus the probe-generated skill-disable override.

## Meters, declared before round 1

- ROUND CAP: 4 consecutive CONTESTED exchanges. Termination requires an
  adjudicated DRY round.
- TOTAL FIX-VERIFY BUDGET: 6 units, one unit = one dispatched exchange.
- The two meters are separate (backlog item 24, closed 0.22.0).

## Preflight

`tools/codex-context-probe.ps1 -WorkDir <repo> -SuppressSkills
-OverrideOut ... -Json`, run before round 1:

```
status: clean, skills_before: 29, skills_after: 0,
repo_scoped: 0, plugin_cache_scoped: 0, unknown_scoped: 0,
project_agents_md: false, global_agents_md: true,
global_agents_md_path: C:\Users\Brandon\.codex\AGENTS.md
override_sha256: 180f09f5...f432bb8
```

The global `AGENTS.md` survives a clean probe by design and is recorded
here rather than removed. Per `client-probe-scope-limit`, a clean probe is
not full reviewer isolation, and item 7 is the reason.

> **SUPERSEDED at round 3, in part.** A clean probe is still not full
> reviewer isolation, and that stop must survive this cycle. But "item 7
> is the reason" stops being the whole reason once item 7 closes: the
> tool-list half becomes measured, while the prompt flag-parity limit at
> `docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:184-197`
> stays unverified and becomes the reason on its own. Task 3 splits them.

## Round 0 — VOID, and the cost was real

Round 1 was dispatched once before this record existed, answered, exit 0,
a 15768-byte reply on disk. It was **discarded unread**.

`-PriorState` for `tools/read-codex-round-evidence.ps1` is an inventory of
the codex sessions root that must be captured BEFORE the dispatch. It was
not. Rebuilding it afterwards is not sound: Windows tunnels file creation
times, backlog item 29 is open on the ancestry walk having no
creation-time ordering guard, and any reconstruction that excludes "the
new one" assumes the answer it is meant to establish.

So the reply was never opened, and the round was re-run at full cost.

**This produced backlog item 35.** `SKILL.md` prints the round-1 dispatch
at lines 178-189 and states the pre-dispatch inventory requirement at
lines 229-232, as a subordinate clause about a parameter, roughly fifty
lines later. A session executing the skill in order dispatches first and
learns second. Every other pre-dispatch obligation in that step - the
enumeration, the mirror, the client probe, the override hash - is written
as an ordered step before the command that consumes it. This one is not.

**A second, smaller process defect from the same round.** The round-1
brief states `HEAD ef428c3`. Two commits landed between writing it and
dispatching it, so the reviewer opened with "the live branch was already
beyond the stated `ef428c3` and advanced again during review", and froze
its adjudication to `99a2099` itself. It adapted correctly and nothing was
lost, but the brief asserted a head the dispatch never verified. Worth
folding into item 35's fix, since it is the same family: bookkeeping the
dispatch depends on, written where nothing checks it.

## Round 1 — five FIXes, five PASSes, not dry

Brief: `plan-brief-r1.md`. Reply: `plan-reply-r1.txt`.
Binding: clean (`-Fresh`, session `019ff252-bb4d-7d43-816b-e3e9ca5f31a5`,
rollout boundary 641954 bytes).
Route verified from the transcript: `gpt-5.6-sol`, `openai`, `read-only`,
`high`.

Every FIX was a claim of the session's that was wider than its evidence,
and every one was re-verified against the cited files before being
accepted. That is the invariant this repo puts first, failing five times
in one round on its own plan.

| # | subject | verdict |
|---|---|---|
| 1 | the app-server surface exists and is bounded | PASS |
| 2 | `-c mcp_servers={}` is inert | PASS |
| 3 | removed and crashed are indistinguishable | PASS |
| 4 | the two-pass shape is a positive control | **FIX** |
| 5 | three agy contracts have no check anywhere | **FIX** |
| 6 | the transcript narrowing is stated, not smuggled | PASS |
| 7 | nothing has measured `allowNonWorkspaceAccess` | **FIX** |
| 8 | no version floor for agy | PASS |
| 9 | the `.codex` gap is newly found | **FIX** |
| 10 | two standing surfaces carry the false premise | **FIX** |

**FIX 4.** Pass 1 calibrates the INSTRUMENT under baseline conditions. It
says nothing about the MCP subsystem under pass-2 conditions, and an empty
pass 2 stays observationally identical to the deliberate-crash arm. So the
presence direction is a control and the absence direction is a mitigation.
The pair is not a positive removal control and may not be called one.

> **SUPERSEDED at round 2.** "The presence direction is a control" is
> still too strong. Observing a tool is a DETECTION. Nothing measured
> establishes that every tool actually present would be observed, so there
> is no guarantee running in that direction either. The word this design
> is entitled to is detection, and only about what it saw.

**FIX 5.** `agents/flash-implementer.md:45-59` already runs three of item
11's contracts as a per-dispatch preflight, `:100-105` bans any
approval-bypass flag, and `:81-92` blocks a missing transcript after the
run. The gap is that the weekly drift watcher covers none of them and the
doctor mirrors two, so a drift lands mid-build on a frozen plan rather
than before it. Safe, but late.

> **SUPERSEDED at rounds 2 and 3, twice.** "The doctor mirrors two" is a
> miscount: `commands/doctor.md:129-144` covers MODEL DECLARATION AND
> REACHABILITY, with its own caveat that the route language is client-side
> requested/propagated only. That is not two of item 11's five contracts.
> And the round-2 replacement, "the contracts ARE enforced", overshot in
> the other direction: item 11's fifth contract is the absence of ANY
> bypass mechanism, while the wrapper checks one known rule class. The
> settled wording is that the KNOWN OPERATIONAL CHECKS are enforced at
> dispatch and the full security contract remains UNMEASURED.

**FIX 7.** `docs/superpowers/plans/2026-07-25-flash-implementer.md:590-603`
records the 0.12.0 build setting the key to `false`, watching a
trusted-workspace print-mode write get soft-denied, restoring `true`, and
documenting it as required on agy 1.1.7. `true` is a measured lane
requirement. The residual is only what it permits OUTSIDE the workspace on
1.1.12, and item 11's security contract stays explicitly UNMEASURED.

> **SUPERSEDED at round 2.** "`true` is a measured lane requirement",
> present tense, promotes a version-bounded result into a standing one. It
> was required ON AGY 1.1.7. TWO questions are open on 1.1.12, not one:
> whether `false` still soft-denies the lane's intended writes, and what
> `true` permits outside the workspace. If `false` no longer denies, the
> setting can simply go.

**FIX 9.** `references/model-prompting-notes.md:288-291` already says
"'.codex/' stays unswept — unprobed; probe before adding". Reconfirmed,
not found. The half of the session's claim asserting that codex loads
project-local skills from there while untrusted is RETRACTED: it was the
client's own description, never a measurement, and no canary artifact was
kept.

**FIX 10.** Two more surfaces carry the false premise: `README.md:186-200`
states it independently, and
`evals/multi-model-verify/test_multi_model_verify.py:762-782` pins the
SKILL region VERBATIM as one multi-line literal, so editing the region
without the pin turns a documentation fix into a red suite.

> **SUPERSEDED at rounds 2 and 3.** Four was not the count, and neither
> was five. Round 2 added
> `docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:378-395`
> as surface 5. Round 3 added THIS FILE as surface 6. The operative count
> is six.
>
> **SUPERSEDED AGAIN, after round 3.** Seven. The session's own sweep
> found `rounds/2026-07-28-reviewer-isolation/README.md:14-21` as surface
> 7. Round 4 caught that this very line had gone stale inside the cycle
> that wrote it, which is the propagation defect appearing INSIDE its own
> correction. The count is a claim like any other and goes stale like one.

**Design questions, answered.** No sound survivor control exists in the
measured configuration, because after the flags `node_repl` is the only
server left and shape A removes the only candidate. Shape A ships anyway,
on both the fresh AND resume dispatches, as risk reduction with an empty
allowlist. No agy version floor; 1.1.12 is an observed baseline, not a
compatibility boundary. Watch `allowNonWorkspaceAccess`, do not flip it.

> **SUPERSEDED at round 3.** "Shape A removes the only candidate" asserts
> an effect the record cannot establish. Shape A makes `node_repl`
> UNREPORTED, with disable versus launch failure unresolved.

Applied at `4be7eee`.

## Round 2 — six findings, not dry

Brief: `plan-brief-r2.md`. Reply: `plan-reply-r2.txt`. Binding clean
(`-Resume`, boundary 876878 bytes).

The central finding was a PROPAGATION failure. Round 1's corrections were
right and were applied to the sections the reviewer had cited, and to
nothing else. The retracted overclaim survived in five further places: a
task heading, two findings, a summary bullet, and the sentence justifying
shape A.

Three more, and one of them corrected a correction:

- "the contracts ARE enforced" overshot. Replacing an understatement with
  an overstatement is not a correction.
- the `allowNonWorkspaceAccess` residual was too narrow, and in naming
  only one of two questions it promoted a version-bounded measurement into
  a present-tense requirement.
- a FIFTH standing surface, the 0.17.0 reviewer-isolation design, which
  needs a SPLIT rather than a rewrite: its tool-list premise is now false,
  its prompt flag-parity limit beside it is still real, and the document
  currently calls them the same gap.

Round 2's own new finding: DQ3's answer was "report agy version changes"
and Task 5 never said to do it. `check-drift` emits change notes for codex
(`:321-323`) and superpowers (`:324-326`) only, which is exactly how agy
moved four releases unremarked.

Applied at `5737d4d`.

## Round 3 — five findings, not dry, and the propagation repeated

Brief: `plan-brief-r3.md`. Reply: `plan-reply-r3.txt`. Binding clean
(`-Resume`, boundary 1084313 bytes).

Round 3 was asked to sweep for propagation specifically, because round 2's
finding predicted its own recurrence. It recurred. **This file was the
surface**: written between rounds 1 and 2, stating round-1 conclusions in
its own words, never revisited when rounds 2 and 3 corrected them. Hence
the SUPERSEDED blocks above, and hence Task 3's count moving to six, and
then to seven when the session swept for itself.

The distinction that makes editing it correct: `plan-brief-r*.md` and
`plan-reply-r*.txt` are VERBATIM HISTORICAL ARTIFACTS and are never
rewritten. This README is a SYNTHESIZED STANDING RECORD and is read as
current, so leaving a superseded conclusion in it is the falsification,
not marking it.

The other four:

- three remnants of removal language survived round 2's sweep, including
  finding 5's title.
- the Goal said "four of five contracts lack drift-side checks" while Task
  5 said the watcher covers none. The version string is not one of item
  11's five contracts (`backlog:787-800`), so the count was wrong: it is
  none of five.
- **A FALSE-CLEAN INTRODUCED BY THE ROUND-2 FIX.** That fix specified an
  unreadable agy version as a NOTE. In this script notes print beside "No
  findings." (`tools/check-drift.ps1:341,345-348`) and the exit is decided
  by findings alone (`:411`), so an unmade measurement would have exited
  CLEAN. The plan's own opening invariant, defeated by its own fix, three
  rounds in. It is now a FINDING with a non-clean exit, and Task 7 must
  assert the exit code rather than the report text.

Applied at `6f1a93e`.

## Round 4 — eight PASSes, two FIXes, CAP REACHED

Brief: `plan-brief-r4.md`. Reply: `plan-reply-r4.txt`. Binding clean
(`-Resume`, boundary 1618355 bytes).

This round carried the session's OWN findings rather than only answering
the reviewer's. Six of the seven previously contested points were
confirmed closed, and both new session findings were adjudicated.

- **Finding A confirmed.** Surface 7 is the 0.17.0 debate record, and the
  split it needs is exactly the one proposed: the tools-are-not-in-the-
  prompt half stays true, the not-measured half does not.
- **Finding C confirmed.** Excluding gitignored local state from the
  shipped-surface count is right.
- **Seven is the count.** No eighth. Three other tracked matches were
  checked and are historical statements that stay true: two plans
  recording item 7 as out of THEIR cycle's scope, and the mirror design
  doing the same.
- **Finding B was half right and then overclaimed, and the correction is
  sharper than the finding.** Saying the repo has "no place" for
  adjudication rules to accumulate is FALSE:
  `references/debate-protocol.md` is that place and `SKILL.md:27` makes it
  required reading before round 1. The real gap is the absence of a
  PROMOTION STEP out of a cycle's record into it.
- **The debate record went stale again, inside the cycle that corrected
  it.** It said the count was six while the plan said seven. The
  propagation defect, appearing inside its own fix, one round after being
  named. The count is a claim and goes stale like one.

**THE ROUND CAP IS REACHED.** Four consecutive contested exchanges. Both
remaining fixes are applied, and both were accepted without contest, but
the protocol's termination condition is an adjudicated DRY round and this
round was not dry. The debate is PAUSED for user authorization rather than
continued.

Meters at the pause: 4/4 consecutive contested exchanges, 4/6 total
fix-verify units. Two units remain unspent.

Applied at `e876ca8`.
