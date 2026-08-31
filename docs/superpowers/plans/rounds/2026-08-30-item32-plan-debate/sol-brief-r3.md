Round 3. Evidence rules, citation requirement and verdict grammar as before.

The plan is now ten tasks and carries a "What round 2 changed" table. The
tree has been rebuilt at the revised head. Re-read both documents; the spec
changed too.

I verified your scope reversal against item 51's probe record directly
rather than against your summary of it, and you are right: probe-record.md
lines 27-31 say the measured shape is a brief file READ and passed inline as
`-p <brief>`, which is what a wrapper does. The deferral is withdrawn.

<task>
For each item below, say whether the revision CLOSES the round 2 finding, or
does not, and where it does not, name what is still wrong. Then the sweeps.
</task>

<changes>

1. THE UNIMPLEMENTED STALENESS RULE. The launch block now opens with an
executable refusal loop over the six OUTPUT paths, and Task 2 pins that exact
line as `test_the_launch_refuses_a_pre_existing_output_path`. `<empty-file>`
is created in the same block rather than assumed.

2. THE UNSATISFIABLE FRESHNESS RULE. Split. Two INPUT paths - wrapper and
empty stdin - are created fresh by this round with create-new semantics. Six
OUTPUT paths - pid, exit, reply, transcript, launch stdout, launch stderr -
must not exist. Global Constraints and region detached-dispatch-states both
say so.

3. THE STATE LIST. Six states now, numbered. The duplicate is gone. "Exited
with an exit file carrying zero but NO reply file" is state five, is a
transport failure, and the region says it is the one an operator is most
likely to wave through.

4. THE KIMI DEFERRAL. Withdrawn. Task 5 detaches all three calls. The two
display bullets in backup-lane.md are untouched, so the pins that read them
stay green; the wrapper carries the same binary, the same flags in the same
order, and `$b`, the brief read from its file. A new RAW pin - not the
normalized reader - asserts each wrapper's native line intact on one physical
line, plus `-WorkingDirectory <review-mirror>`, because this client binds a
session to the directory it was created in. No `$OutputEncoding` preamble
appears on this lane, deliberately, because the brief goes as an argument and
the brief-encoding-transport region already says that mechanism does not
apply here. Item 51 keeps the escaping repair.

5. THE STALE ENUMERATION IN THE SPEC. Corrected to five calls with a
disposition column: two codex, three kimi, all five detached. It also records
that the deferral happened and was reversed, and why.

6. NAMING. Moved out of detached-dispatch-operation into its own
background-task-naming region, declared separately, with a pin named
`test_the_background_task_naming_rule_is_documented` and a docstring saying
it is a documentation-presence pin and not behavioural enforcement. The
region text itself says NOTHING ENFORCES THIS.

7. PARSE SENSITIVITY. New Task 8, before any real dispatch and costing no
quota: render all four wrappers from the documents - extracted by reading
them, never a second copy in the test - parse each with
`[System.Management.Automation.Language.Parser]::ParseFile` on both hosts,
then execute each against a stub for three outcomes: clean zero, non-zero
exit, and a pre-client throw. The third asserts the exit file EXISTS with a
non-zero code, which is what `$code = 1` before the `try` is for. The test
asserts no real client was invoked.

8. THE KILL RACE. Task 9 now kills a STUB that writes the reply and then
sleeps thirty seconds, so the window is deterministic. It also plants a stale
exit file of `0` beside a fresh reply and asserts the poll still refuses.

</changes>

<final-check>
UNVERIFIED list as before.

Then three sweeps, naming an instance or reporting none explicitly. State the
base rate you are working against: you found a false-completion path in round
1 and a second unclassified state in round 2, so the prior that this class is
now exhausted is weak.

(a) Is there a SEVENTH state, or a combination of the six, that the contract
does not classify? Round 1 and round 2 each found one. Look particularly at
the interaction between the refusal loop, a partially written exit file, and
a reply file the client is still writing when the poll runs.

(b) Task 8 renders wrappers by extracting fenced blocks from the documents.
What can that extraction get wrong such that the gate passes while the real
wrapper a session copies would fail? Name the failure, not the risk.

(c) The plan now touches four shipped surfaces - SKILL.md, backup-lane.md,
model-prompting-notes.md and new-review-mirror.ps1 - across ten tasks with an
ordering constraint between Task 6 and Task 7. Is any task's verification
capable of passing while its own change is absent or partial? That is the
shape Task 5 had in the last revision and I want it looked for again rather
than assumed gone.
</final-check>
