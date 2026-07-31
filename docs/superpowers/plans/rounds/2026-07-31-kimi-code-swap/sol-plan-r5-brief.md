<task>Round 5, a confirmation round. Every round-4 finding is applied. Re-read
docs/superpowers/plans/2026-07-31-kimi-code-swap.md and the amended
docs/superpowers/plans/rounds/2026-07-31-kimi-code-swap/probe-record-2.md.
Evidence rules, verdict grammar and boundaries as before.</task>

<applied>
Every one of your round-4 findings, no exceptions and nothing contested.

Code paths:
- The flag loop is now inside an `else`, so a failed or empty --help stops at
  one measurement-failure finding instead of emitting five that describe
  nothing. The --help invocation is wrapped in try/catch.
- -PriorState now carries `sessionDir` and `sessionId`, and a new rule 2 fails
  `state-session-mismatch`. You were right that the binding was incidental
  rather than enforced - a foreign state was rejected only if a prefix hash
  happened not to match.
- New rule 3 rejects internally inconsistent states: fresh with nonzero
  offsets, fresh carrying continuity hashes, resume with sessionDirExisted
  false.
- New rule 4 rejects an unusable -AgentFile and a malformed
  -ExpectedBriefSha256. The validator compares against the agent file, so an
  unreadable one made every comparison vacuous.
- Rule 9 now also fails a VALID-JSON record with structurally invalid fields,
  as `record-malformed`, rather than throwing or coercing.
- Rule 12 requires the requests' toolsHash to equal llm.tools_snapshot.hash on
  a fresh slice. Consistent request hashes that contradict the snapshot are a
  disagreement, not a pass.
- Removal guards: the live step now exercises USERPROFILE, a drive root and a
  .git-containing directory, EACH with a correctly formed sentinel planted for
  that exact path. Your point stands that a guard which has only ever seen a
  malformed sentinel has not been tested.
- The fault seam is explicitly cleared after the fault test.
- Task 11's step numbering is sequential.

Eight test cases added, covering each gap you named.

Three overclaims narrowed:
- The floor is a LOWER BOUND and forces no re-probe at upgrade. Both the
  comment and the test docstring now say so, and name the manual re-probe at a
  deliberate version bump as what actually covers it.
- Resume results are stated as "of the four flags tested", in the plan and in
  the probe record.
- Record ORDER was your sharpest catch and it was worse than you put it. I had
  asserted the fresh slice opens with "a session-creation record". Measured
  from the retained session, the actual order is metadata, config.update,
  tools.set_active_tools, config.update, permission.set_mode, turn.prompt - so
  the rule named a record that is not first. Rule 10 now requires `metadata`
  for fresh and `turn.prompt` for resume, and the probe record carries the
  measured order with a note that counts establish no ordering.
</applied>

<claims>
1. Every round-4 finding is correctly applied, and no application introduced a
   new defect. Attack specifically: the else-guarded flag loop, the session
   binding in rules 2 and 3, the agent-file and argument validation in rule 4,
   the snapshot-versus-request hash check in rule 12, and the corrected
   slice-boundary record names in rule 10.

2. The three narrowed claims are now stated at exactly the width of their
   evidence, neither wider nor narrower.

3. The plan is executable by an engineer with no repository context.

4. This plan is ready to freeze and implement. If you disagree, name what
   remains that is STRUCTURAL rather than an addressable detail - I am asking
   you to distinguish "this design is wrong" from "this list could be longer",
   because the second is true of every test list ever written and is not a
   reason to keep a plan open.
</claims>

<final-check>
List anything you could not verify against files you read this session, as
UNVERIFIED.
</final-check>
