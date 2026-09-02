Round 6, a full review round. Evidence rules, citation requirement and
verdict grammar as before.

The user chose Option A. The plan is REBUILT around a shipped tool and is
now nine tasks. Read it whole; diffing it against revision 4 will mislead
you, because the launch no longer exists as document text at all.

A Claude-side reviewer was polled on the same fork in parallel and chose the
same option independently. Where you two differed I took YOUR weaker claim:
`LAUNCH UNKNOWN` is a named state in the contract rather than an eliminated
one, on your reasoning that a hard kill between process creation and pid
publication stays reachable. The other lane argued the state is removed; it
also stated it had not re-verified the round 4 finding, so I did not take it.

<task>
Judge the rebuilt plan. For each item below say whether it CLOSES your round
4 finding, and where it does not, name what is still wrong. Then the sweeps,
which are the part I care most about.
</task>

<changes>

1. FAIL-CLOSED RESERVATION. Task 1 specifies `$ErrorActionPreference =
'Stop'` around every step, `-ErrorAction Stop` on both the reservation and
`Start-Process`, and a `catch` that runs `taskkill /PID $proc.Id /T /F` and
exits 1 if anything fails after the process starts. The `-Force` test now
parses the command rather than forbidding one token order, which was your
finding about `-Force -ItemType Directory` evading it.

2. THE EIGHTH CONDITION. It is now the FIRST check, named `launch-unknown`,
and the region says in its own text that shipping the transaction in one
tool narrows it and does not remove it. The tool writes `pid` and then
`launch.committed` LAST, so the commit artifact is what distinguishes a
completed launch, and `-Poll` never reports anything else without it.

3. `>= N` COUNTS BINDING NOTHING. Gone. Task 4 uses one `<!-- call:... -->`
marker per Kimi call and a parametrized test that splits the document on the
marker and asserts the launch, the client invocation and the reply artifact
INSIDE that call's section. Leaving one behind now fails by name.

4. THE LAUNCH WAS NEVER CENTRALIZED. It is now, literally: the launch is a
script, not text. `SKILL.md` and `backup-lane.md` each assert
`"Start-Process" not in text`, so a copied launch anywhere in either file
fails the suite.

5. TASK-LOCAL ORACLES. Rewritten per your table. Task 1 has a negative
self-test that deletes its own `catch` and requires a red. Task 2 deletes a
region's markers in a scratch copy and requires
`test_declared_regions_match_the_documents` to fail. Task 6 now asserts BOTH
removed passages, not just the first. Task 7's extractor takes a source path
so the scratch-copy negative test can actually reach it. Task 8 gained the
oracle it did not have: a test that the probe record exists and carries a
row per host per measurement. Task 9's grep now searches for the stale
region names, the refuted quoting claim and the refuted encoding claim.

6. THE ANCHOR. The one new call uses `${CLAUDE_PLUGIN_ROOT}`. The three
existing bare relative paths at `SKILL.md:94`, `:121` and `:228` are NOT
touched, and Task 9 Step 7 records that asymmetry in item 32's closure
rather than leaving it to be found.

7. THE CEILING RAISE IS NOW CONDITIONAL. The tool-based design shrinks the
dispatch steps, so Task 9 Step 1 measures first and raises nothing if the
body is under the ceiling.

</changes>

<final-check>
UNVERIFIED list as before.

Base rate, and I want you to hold it against the rebuild rather than reset
it: you have found a completion-model hole in EVERY round - four for four.
Revision 5 changes the mechanism, not the class.

(a) Find the fifth hole. The state machine is now code rather than prose, so
look at the ORDER of the checks in Task 1 Step 3 and at what each branch
does NOT read. Name the input, the sequence, and which state is wrongly
reported.

(b) The tool is a NEW shipped surface on the dispatch path of every round,
including this one. What can it break that five copied snippets could not?
Answer concretely: name a failure mode that only exists because the launch
is now a separate process invoking a separate script.

(c) The plan asserts the launch is centralized because neither document
contains `Start-Process`. Is that assertion actually load-bearing, or can a
lane still fail to be detached while satisfying it? If it can, say how.

(d) Task 1's tests drive the real script. Is there any state in `-Poll` that
its test cases cannot reach, or that they reach only by planting files that
the real `-Launch` could never produce? A test that can only exercise an
impossible arrangement proves nothing about the real one.
</final-check>
