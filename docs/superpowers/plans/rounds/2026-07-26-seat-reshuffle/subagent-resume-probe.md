# Probe record: same-harness subagent resume (Fable panel-lane feasibility)

Date: 2026-07-26. Harness: Claude Code 2.1.220 (Windows). Session
driver: Fable 5. Settles the dual-advisory UNVERIFIED (both lanes,
0.14.0 spec advisory): whether a same-harness Claude subagent can hold
debate state across rounds, and whether its model pin can be silently
swapped on resume.

## Exact mechanics

1. Round-1 dispatch — the literal Agent tool call arguments:

   ```json
   {
     "description": "Probe: fable subagent round 1",
     "subagent_type": "general-purpose",
     "model": "fable",
     "run_in_background": false,
     "prompt": "You are a probe subject in a harness-capability test. This is round 1. Remember this token for later rounds: PARALLAX-PROBE-7391. Reply with exactly two lines: line 1 the word READY, line 2 the sentence \"Round 1 token stored.\" Do not use any tools. Do not add anything else."
   }
   ```

2. Observed round-1 result (verbatim reply plus the harness result
   metadata as returned):

   ```
   READY
   Round 1 token stored.
   agentId: af3d72520c818b10c (use SendMessage with to: 'af3d72520c818b10c' ... to continue this agent)
   subagent_tokens: 26084 / tool_uses: 0 / duration_ms: 5849
   ```

3. Resume — the literal SendMessage tool call arguments:

   ```json
   {
     "to": "af3d72520c818b10c",
     "summary": "Probe round 2: token recall check",
     "message": "Round 2 of the harness-capability probe. Reply with exactly three lines: line 1 the token you stored in round 1 (exactly as given), line 2 the model family you are (one word, honestly - if you are a Claude model say which named Claude model you believe you are running as), line 3 the word RESUMED. Do not use any tools."
   }
   ```

   The SendMessage tool schema, quoted from the schema loaded this
   session (2026-07-26): required properties `to` and `message`, with
   optional `summary` ("A 5-10 word summary shown as a preview in the
   UI") - the full property set is {to, summary, message}; there is NO
   model, effort, or tool-grant parameter on the resume surface.

4. The resume call's synchronous tool result (verbatim): "Agent
   \"af3d72520c818b10c\" had no active task; resumed from transcript
   in the background with your message. You'll be notified when it
   finishes." - i.e. a send to a FINISHED agent resumes it from its
   retained transcript; the reply then arrived as a harness
   task-notification (task-id af3d72520c818b10c, status completed)
   whose result block carried the reply verbatim:

   ```
   PARALLAX-PROBE-7391
   Fable
   RESUMED
   ```

   (subagent_tokens: 24640 / tool_uses: 0 / duration_ms: 4854.) The
   task-notification channel is the same one that surfaces agent
   completion and death throughout this harness - this is the loud
   failure/completion surface the lane's failure-mode claim rests on,
   observed here directly for the finished-agent case.

## Results

- Conversation state persists across resume: the nonce was recalled
  exactly.
- The resume surface has NO model parameter: the round-1 model pin
  cannot be silently swapped by a resume call — the inverse of the
  kimi bare-resume hazard (which reloads config defaults). The pin
  and tool grant ride the agent identity.
- Failure/completion surface: the resumed probe's own reply arrived
  as a harness task-notification for a background-resumed agent
  (section 4 above — observed directly, quoted verbatim); a send to a
  finished agent resumes it from its retained transcript (the
  synchronous tool result, quoted). The DEAD-agent (terminal API
  error) case specifically was not exercised by this probe; the claim
  the lane rule may cite from this record is the notification channel
  and transcript-resume behavior — the dead-agent case is narrowed to
  the attended smoke's observation scope.
- Line 2 of the resumed reply (self-reported model family) is
  priming-class behavioral output and is NOT counted as evidence —
  recorded here only for completeness. Identity evidence for this
  lane is the dispatch metadata (the explicit model parameter on the
  round-1 Agent call), client-side class, reported with the same
  vocabulary discipline as the codex and kimi lanes.

## Residual limits

- The probe used subagent type `general-purpose`; the panel lane will
  use a dedicated agent file (agents/fable-panel-reviewer.md). The
  no-model-parameter-on-resume fact is a property of the resume
  surface, not the agent type; the agent-file variant is re-probed in
  the 0.14.0 attended smoke (two rounds: dispatch + one resumed
  rebuttal) before the lane carries a real review.
- Self-report is never identity evidence (above). No server-side
  attestation of subagent model identity exists in this harness;
  the record language is "requested and propagated" class.
