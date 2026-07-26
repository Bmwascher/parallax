# Probe record: same-harness subagent resume (Fable panel-lane feasibility)

Date: 2026-07-26. Harness: Claude Code 2.1.220 (Windows). Session
driver: Fable 5. Settles the dual-advisory UNVERIFIED (both lanes,
0.14.0 spec advisory): whether a same-harness Claude subagent can hold
debate state across rounds, and whether its model pin can be silently
swapped on resume.

## Exact mechanics

1. Round-1 dispatch: the harness Agent tool, subagent type
   `general-purpose`, explicit `model: fable` parameter, prompt storing
   a nonce token (`PARALLAX-PROBE-7391`) and requiring a two-line
   fixed-format reply, no tools.
2. Observed round-1 reply (verbatim):

   ```
   READY
   Round 1 token stored.
   ```

3. Resume: the harness SendMessage tool addressed to the round-1
   agent id, requiring three fixed lines: the stored token, the
   self-believed model family, the word RESUMED. The SendMessage tool
   schema carries exactly three fields - recipient (`to`), `summary`,
   and `message` - and NO model parameter (read from the loaded tool
   schema this session, 2026-07-26).
4. Observed resumed reply (verbatim):

   ```
   PARALLAX-PROBE-7391
   Fable
   RESUMED
   ```

## Results

- Conversation state persists across resume: the nonce was recalled
  exactly.
- The resume surface has NO model parameter: the round-1 model pin
  cannot be silently swapped by a resume call — the inverse of the
  kimi bare-resume hazard (which reloads config defaults). The pin
  and tool grant ride the agent identity.
- Failure mode: a dead or completed agent surfaces as a loud harness
  task-notification; a send to a finished agent resumes it from its
  retained transcript (observed repeatedly this session with other
  agents).
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
