# Probe record: subagent resume across seats, idle and depth (backlog item 50)

Date: 2026-08-19 (local, CDT), 2026-08-20 UTC.
Harness: **Claude Code 2.1.237** (Windows), read from `claude --version` at
probe time, 2026-08-19 23:40 CDT.
Repo: `main` at `de85e8f`, working tree clean. Plugin cache 0.26.1,
`gitCommitSha` `6c24b99`.
Driver: Opus 5, this session.

## Why this probe exists

Backlog item 50 records a REPORT, relayed by the user from another
session, that the Fable panel lane would not resume between rounds on
Claude Code 2.1.233, failing with `No transcript found`. That report
contradicts two LOCKED contract regions - `panel-floor-reference` in
`skills/multi-model-verify/references/panels.md` and `panel-floor-agent`
in `agents/fable-panel-reviewer.md` - whose surrounding text says that at
or above Claude Code **2.1.216** a resumed background agent keeps its
conversation state, its model pin and its read-only tool grant.

Item 50 requires a PROBE before any contract edit, and the build order
adds that the probe "should cover more than the panel seat", because
0.25.0 measured the same literal failure three times on general-purpose
and implementer seats.

**The version this probe measures is 2.1.237, NOT the reported 2.1.233.**
2.1.233 is still published and could be pinned; the user chose to measure
the running harness first. Nothing here confirms or refutes the 2.1.233
report directly.

## What the 2026-07-26 probe actually measured

`docs/superpowers/plans/rounds/2026-07-26-seat-reshuffle/subagent-resume-probe.md`
is the record the contract rests on. Read at its real width it measured:

- ONE resume, issued immediately after round 1.
- Subagent type `general-purpose` with `model: fable`, NOT the
  `fable-panel-reviewer` agent file. Its own "Residual limits" section
  says so.
- Harness 2.1.220.

It did not measure a long idle, a second or third resume, or the panel
agent file. Those are the three gaps this probe covers.

## Probe design

Four arms, crossing seat against idle, with resume depth on the short arms:

| Arm | Seat | Idle before first resume | Resumes planned |
|---|---|---|---|
| A | `parallax:fable-panel-reviewer` | about 3 minutes | 3 |
| B | `parallax:fable-panel-reviewer` | about 25 minutes | 1 |
| C | `general-purpose` | about 3 minutes | 3 |
| D | `general-purpose` | about 25 minutes | 1 |

Each subject stores a unique nonce at round 1 and is asked to repeat it
verbatim on every resume, so a SILENT state loss is visible and not only a
hard `No transcript found` error.

The panel-seat arms are additionally asked, on resume, to attempt a Bash
tool call. That is a capability test, not a self-report: the seat's grant
is `Read, Grep, Glob`, so a Bash call that SUCCEEDS is direct evidence the
agent reverted to a default, fully-tooled agent. Self-reported identity is
priming-class and is not counted as evidence, per the same rule the
2026-07-26 record states.

### Seat provenance

The probe dispatches the SHIPPED seat, not the checkout copy. The cached
`agents/fable-panel-reviewer.md` under plugin cache 0.26.1 was diffed
against the checkout with CRLF normalized: **identical**, and the
frontmatter carries `model: fable` and `tools: Read, Grep, Glob`.

## Round 1: dispatch

All four dispatched concurrently at about 23:41 CDT. Round-1 prompt shape,
identical across arms apart from the nonce and the leading sentence:

```
This is a HARNESS-CAPABILITY PROBE, not a code review. [...]

Round 1 of a multi-round probe.

Store this token for later rounds: <NONCE>

Reply with exactly two lines and nothing else:
line 1: READY
line 2: Round 1 token stored.

Do not use any tools.
```

Observed round-1 results, verbatim replies plus harness result metadata:

| Arm | agentId | Nonce | Reply | tokens / tool_uses / duration_ms |
|---|---|---|---|---|
| A | `a4dc07cbe282c235d` | `PARALLAX-P50-ALPHA-4417` | `READY` / `Round 1 token stored.` | 13761 / 0 / 2500 |
| B | `acde12a644e38f23b` | `PARALLAX-P50-BRAVO-8823` | `READY` / `Round 1 token stored.` | 13759 / 0 / 3632 |
| C | `a6eebe2300d0c8ff2` | `PARALLAX-P50-CHARLIE-5591` | `READY` / `Round 1 token stored.` | 34587 / 0 / 1610 |
| D | `aa1251a7b0b6684a6` | `PARALLAX-P50-DELTA-2076` | `READY` / `Round 1 token stored.` | 34585 / 0 / 1788 |

All four completed and went idle. Note the token asymmetry: the two
panel-seat arms report about 13.7k and the two general-purpose arms about
34.6k, consistent with different system prompts and tool grants being in
play, which is the expected shape for a correctly dispatched pinned seat.

## Round 2 onward


### The resume surface at 2.1.237

The literal `SendMessage` tool schema loaded this session has required
properties `to` and `message`, with optional `summary`. The full property
set is {to, summary, message}. **There is still NO model, effort, or
tool-grant parameter on the resume surface**, which is the same finding
the 2026-07-26 probe recorded and is the half of the contract that
concerns the model pin.

The synchronous tool result HAS changed shape since 2.1.220. Then it read
`Agent "<id>" had no active task; resumed from transcript in the
background with your message.` At 2.1.237 it is JSON:

```json
{"success":true,"message":"Resuming agent a4dc07c","resumedAgentId":"a4dc07cbe282c235d","pin":{"id":"a4dc07cbe282c235d","name":"a4dc07cbe282c235d","ref":"2d4e59"}}
```

The `pin` object carries id, name and ref only - no model. Recorded
because the 2026-07-26 record quotes the older string verbatim, and a
future reader comparing them should not mistake the change for a defect.

### Arm A - panel seat, resume 1 (about 3 minutes idle)

Issued 23:45:34 CDT. Resume message asked for the nonce, a Bash
invocation attempt, and the agent's tool list.

Verbatim reply:

```
PARALLAX-P50-ALPHA-4417
RESUMED
BASH-NOT-GRANTED
Read, Grep, Glob
```

(14053 tokens / 0 tool_uses / 2867 ms.)

**Result: PASS on every claim the contract makes.** State persisted (the
nonce came back exactly). The read-only tool grant survived the resume -
the seat could not invoke Bash, and the tool list it reports matches the
`tools: Read, Grep, Glob` in its agent file. That is the capability
evidence, not a self-report about model identity.

### Arm C - general-purpose, resume 1 (about 3 minutes idle)

Verbatim reply:

```
PARALLAX-P50-CHARLIE-5591
RESUMED
```

(34718 tokens / 0 tool_uses / 2284 ms.) **Result: PASS.** State persisted.

### Arm A - panel seat, resume 2 (issued immediately, no idle)

This arm separates DEPTH from IDLE: a second resume with no waiting.

Verbatim reply:

```
PARALLAX-P50-ALPHA-4417
2
RESUMED-TWICE
```

(14335 tokens / 0 tool_uses / 24496 ms.) **Result: PASS, and stronger
than nonce recall.** Line 2 is the round number in which the agent was
asked to attempt a Bash call. It answered `2`, correctly, which is a
detail from a round OTHER than the one that planted the nonce. A seat
that had silently reverted and been re-primed from a single carried
message could not answer that.

### Arm C - general-purpose, resume 2 (issued immediately, no idle)

Verbatim reply:

```
PARALLAX-P50-CHARLIE-5591
RESUMED-TWICE
```

(34867 tokens / 0 tool_uses / 23225 ms.) **Result: PASS.**

### Arm A - panel seat, resume 3 (about 4 minutes idle)

Verbatim reply:

```
PARALLAX-P50-ALPHA-4417
RESUMED-TWICE
RESUMED-THRICE
```

(14571 tokens / 0 tool_uses / 2347 ms.) **Result: PASS.** Line 2 asked for
the word written on line 3 of the PREVIOUS reply - answered correctly,
again a detail from another round.

### Arm C - general-purpose, resume 3 (about 4 minutes idle)

Verbatim reply:

```
PARALLAX-P50-CHARLIE-5591
RESUMED-TWICE
RESUMED-THRICE
```

(35097 tokens / 0 tool_uses / 2100 ms.) **Result: PASS.**

### Arm B - panel seat, resume 1 after 25 minutes idle

Round 1 completed 23:42 CDT; resume issued 00:07:31 CDT, so 25 minutes
idle. That is the condition present in two of the three failures 0.25.0
measured.

Verbatim reply:

```
PARALLAX-P50-BRAVO-8823
RESUMED-AFTER-LONG-IDLE
BASH-NOT-GRANTED
Read, Grep, Glob
```

(14103 tokens / 0 tool_uses / 3279 ms.) **Result: PASS on every claim.**
State persisted across a 25-minute idle and the read-only grant survived.

### Arm D - general-purpose, resume 1 after 25 minutes idle

Verbatim reply:

```
PARALLAX-P50-DELTA-2076
RESUMED-AFTER-LONG-IDLE
```

(34730 tokens / 0 tool_uses / 1898 ms.) **Result: PASS.**

## Interim tally after the four planned arms

**Eight resumes issued across four arms. Eight passed. Zero
`No transcript found`. The reported failure did NOT reproduce on 2.1.237.**

| Condition | Panel seat | general-purpose |
|---|---|---|
| Resume after about 3 minutes | PASS | PASS |
| Second resume, no idle | PASS | PASS |
| Third resume | PASS | PASS |
| Resume after 25 minutes idle | PASS | PASS |

Two contract claims held under direct measurement rather than
self-report: the read-only tool grant survived every panel-seat resume
(the seat could not invoke Bash and enumerated exactly its three granted
tools), and the resume surface still exposes no model parameter.

**This tally does NOT clear the contract, and must not be read that way.**
See the analysis section below.

## Arm E - the live-background-child hypothesis

Added mid-probe, not in the original four, because re-reading the 0.25.0
record supplied a better hypothesis than idle time. Its FIRST failure was
an agent that "appears to have backgrounded the 20-minute suite run and
returned while it was still going". The harness note attached to every
task-notification in this session reads: "A task-notification fires each
time this agent stops with no live background children of its own." That
is a concrete, testable mechanism.

Arm E: a `general-purpose` agent instructed to start
`sleep 200; echo CHILD-DONE` with `run_in_background` set to true, to NOT
wait for it, and to return immediately.

Round 1 verbatim reply (37556 tokens / **1 tool_use** / 3913 ms), which
confirms it did start the child:

```
READY-WITH-LIVE-CHILD
Round 1 token stored.
```

**Observation worth keeping:** the agent fired a completion notification
anyway, while its background child was still running. So the note's
"stops with no live background children" is not a precondition that held
here, or the child was not tracked as its own.

Resumed at 00:08:47 CDT, with the child due to run until about 00:12.
Verbatim reply (35135 tokens / 1 tool_use / 28619 ms):

```
PARALLAX-P50-ECHO-6634
RESUMED-WITH-LIVE-CHILD
```

**Result: PASS.** The live-background-child hypothesis did NOT reproduce
the failure.

## Final tally

**Nine resumes across five arms. Nine passed. Zero `No transcript
found`.**

| Condition tested | Panel seat | general-purpose |
|---|---|---|
| Resume after about 3 minutes | PASS | PASS |
| Second resume, no idle | PASS | PASS |
| Third resume | PASS | PASS |
| Resume after 25 minutes idle | PASS | PASS |
| Resume with a live background child | not testable (no Bash grant) | PASS |

## Analysis

### What this probe DID establish

- **On 2.1.237 the panel seat's containment survives resume, measured by
  capability rather than self-report.** Across both panel arms the seat
  could not invoke Bash and enumerated exactly `Read, Grep, Glob`. A seat
  that had silently reverted to a default agent would have had Bash.
- **Conversation state genuinely persists, not merely the carried
  message.** Both multi-round arms answered questions about rounds OTHER
  than the one that planted the nonce - which round asked for the Bash
  attempt, and what word the previous reply ended on. A re-primed default
  agent could not answer those.
- **The resume surface still carries no model parameter.** The full
  `SendMessage` property set is {to, summary, message}. The model pin
  cannot be silently swapped by a resume call.
- **Three hypotheses were tested and none reproduced the failure**: long
  idle, resume depth, and a live background child.

### What this probe did NOT establish, and cannot

**A clean probe cannot establish a guarantee about an intermittent
fault.** The 0.25.0 record is explicit that resumability "is not a
property of the agent: the same id resumed and then did not". Nine
consecutive passes are perfectly consistent with a low-rate intermittent
failure. This probe has LOW POWER and its clean result must never be
cited as evidence that resume is reliable.

**It says nothing about 2.1.233**, the reported version, and nothing
about whether the panel seat specifically failed there.

### The load-bearing evidence is not this probe

It is the three failures 0.25.0 measured, recorded in
`.superpowers/sdd/2026-08-15-resume-preamble-refresh/progress.md` and
marked MEASURED HERE, all on Claude Code **2.1.233** - which is ABOVE the
2.1.216 floor.

That fact alone settles one of item 50's three candidates:

- **Candidate 1, "the floor is wrong and the real one is higher", is
  REFUTED by measurement.** The failures occurred above the floor. Bumping
  the number to 2.1.233 or 2.1.237 would put the same unearned guarantee
  in a new suit, which is exactly what item 50 warns against.
- **Candidates 2 and 3 cannot be separated from 2.1.237.** Candidate 2 is
  "something else in 2.1.233 broke resume"; candidate 3 is "resume was
  never reliable and the 2026-07-26 probe measured a narrower case".
- **The 2026-07-26 probe was narrower than the contract built on it**, and
  said so itself. Its "Residual limits" section records that it used
  `general-purpose`, not the panel agent file. It also measured exactly
  one immediate resume. The contract generalized that into a versioned
  platform guarantee.

### Why separating candidates 2 and 3 does not change the fix

Under candidate 2 the fault is version-specific and 2.1.237 may have
fixed it. Under candidate 3 it is rare and version-independent. **The
contract must change the same way under both**, because the repo runs on
whatever harness the user has, and in the measured case a floor did not
protect the session. Either way the contract must stop asserting that
being above a number makes resume reliable.

So the 2.1.233 measurement is worth having for the record but is NOT
decision-relevant to step 2.

### The precise defect, which is disposition and not detection

`No transcript found` is LOUD to the driver: the resume call returns it as
a failure and the driver sees it. Detection is not the gap.

The gap is what the contract tells the driver to DO. `panels.md` names the
lane's failure mode as "agent death, which is loud (class
panel-lane-loss, fallbacks.md)". `panel-lane-loss` routes to the consent
gate and forbids quietly convening a smaller panel. But a resume that
returns `No transcript found` does not READ as "agent death" - the agent
is not dead, it simply cannot be resumed - so a driver meeting it does
not recognize the case as panel-lane-loss. The reported session
re-dispatched fresh and carried on, and the panel still reported as a
panel.

**That is the silent degradation item 50 describes, and it is a naming
and routing defect in the contract, not a missing failure class.** The
class already exists and already has the right disposition.

## Verdict

The reported failure did not reproduce on 2.1.237 in nine attempts across
five conditions. **The contract is still wrong**, on evidence that does
not depend on this probe: it promises reliable resume above a version
floor, and this repo measured three failures above that floor.

Recommended shape for step 2, for the user to accept or reject:

1. The floor stays as a floor for the thing it actually fixed - the
   pre-2.1.216 SILENT revert to a default agent. That claim is sound and
   this probe supports it: containment held on every resume tested.
2. The contract STOPS claiming that being above the floor makes resume
   reliable. Resume is a best-effort operation that can fail.
3. A failed resume gets NAMED in the failure-mode sentence, alongside
   agent death, so it routes to `panel-lane-loss` and its consent gate
   rather than to a quiet fresh re-dispatch.
4. A fresh re-dispatch, if the user consents to one, is RECORDED as a
   fresh dispatch, so a degraded panel cannot report as an intact one.

Both affected regions are locked, so per `CLAUDE.md` the pins in
`evals/multi-model-verify/` change BEFORE the text.
