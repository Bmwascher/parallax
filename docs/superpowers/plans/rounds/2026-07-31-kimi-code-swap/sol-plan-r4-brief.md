<task>Round 4. Re-read docs/superpowers/plans/2026-07-31-kimi-code-swap.md, which
was revised again. Evidence rules, verdict grammar and boundaries as before.
One of your round-3 fixes is CONTESTED rather than applied; see below and
either refute my reasoning or withdraw it.</task>

<fixed>
Every concrete defect from round 3 is fixed.

- KNOWN_TOOLS is now an independent frozen literal of 22 names, not the union
  of the lists it tests. You were right; it detected nothing.
- The builder uses PARAMETER SETS: Build (-Path -Model [-Effort]) and Remove
  (-Path -Remove). -Model is mandatory within Build only, so -Remove is
  callable.
- The drift stub is now possible: production resolves `kimi.exe` OR `kimi.cmd`
  in that directory, and the harness stubs the .cmd. Real Windows CLIs ship
  either form, and no environment seam is introduced - deliberately, because
  an env-redirectable lookup is the lock-stealing shape this repo was bitten
  by twice.
- A present binary whose --version fails or prints nothing is now a FINDING,
  not the "absent" note. --help exit is checked too. Three outcomes, kept
  distinct.
- The sentinel now carries a magic string plus the resolved path it was
  written for, and removal additionally refuses drive roots, USERPROFILE and
  anything containing .git.
- Transaction cleanup runs only for a directory this invocation created and
  marked, and a PARALLAX_LANE_HOME_FAULT seam exists so Task 3 Step 5 can
  prove the cleanup actually runs.
- Offsets are now BYTE counts for both files, and both files carry an
  independent prefix hash. That kills the framing ambiguity you named and the
  wire/log asymmetry in one change.
- New rule 7, `slice-misaligned`: the slice must BEGIN at a call boundary. This
  is your mid-call stale offset, which passed every count and value check.
- The second config.update's modelAlias and thinkingEffort are compared;
  permission.set_mode.mode is compared against `auto`; every llm.request must
  carry nonempty toolsHash and systemPromptHash identical across the slice.
- The validator takes ONE -PriorState object carrying sessionDirExisted, both
  byte offsets, both prefix hashes and the continuity hashes, and emits
  nextState. That makes the fresh-directory test executable, binds each
  invocation to the previous one so an old state cannot be replayed, and moves
  hash continuity from caller advice into the validator.
- Task 6's case list grew to cover every gap you named, including the resume
  branch's forbidden-record cases, which had no negative test at all.
- The rotation probe has a finite criterion: grow one session log past 16 MB
  and look for siblings. A negative result at a stated depth is a result.
- Task 11 persists nextState and adds a live negative confirmation: re-validate
  round 2 with round 1's state and require failure.
</fixed>

<contested>
Round 3 asked the plan to "define exact parsing and hashing algorithms" for the
validator, and listed under-specification of the algorithm as an executability
blocker.

I have applied every part of this that concerns the INTERFACE and the
INVARIANTS - byte offsets, both prefix hashes, the state object, rule ordering,
which fields are compared. I have not written the parsing algorithm into the
plan, and I do not intend to.

The reasoning: Task 6 is a TDD task with a now roughly fifty-case enumerated
test list, and the plan mandates writing those tests FIRST. For a program, the
tests ARE the specification, and they are executable where prose is not. A plan
that also carries the algorithm has two specifications of the same thing, and
this repo's history is largely a record of two descriptions of one rule drifting
apart - that is what the contract-coverage checker exists to catch. The plan's
job is to fix the interface, the invariants, and the cases; the algorithm is the
implementer's, constrained by tests that fail if they get it wrong.

Refute this if you think the enumerated cases are insufficient to constrain the
implementation - that would be a real argument, and it is testable against the
case list. "The plan does not state the algorithm" is not, by itself, the same
claim.
</contested>

<claims>
1. Every round-3 concrete defect is fixed, and no fix introduced a new one.
   Attack the new material: the .cmd resolution, the three-way version outcome,
   the parameter sets, the sentinel content check plus root guards, the
   createdByThisInvocation flag, the byte-offset prefix hashing, rule 7's
   boundary check, and the -PriorState object.

2. The contested position above is correct.

3. The case list is now sufficient to constrain a correct implementation.
   If you disagree, name a case that is missing - not an algorithm that is
   unstated.

4. The plan is executable by an engineer with no repository context.

5. Nothing in the plan now claims more than the measurements support.
</claims>

<final-check>
List anything you could not verify against files you read this session, as
UNVERIFIED.
</final-check>
