Round 4. Evidence rules, citation requirement and verdict grammar as before.

This is a REWRITE, not a fourth patch, because your round 3 finding was
about the plan's own recurring defect rather than about any one task. Both
documents changed; the tree is rebuilt. Read the plan whole rather than
diffing it.

Two structural changes answer "prose stands in for mechanism, three rounds
running":

- There is now ONE launch block, defined in `model-prompting-notes.md` as
  region `detached-dispatch-launch`, and every lane cites it. A lane adds
  parameters and changes nothing else. The region says in its own text that
  a lane not citing it is not detached however its prose reads.
- Every task carries a TASK-LOCAL ORACLE: a check that fails if that task's
  own change is missing. That is your sweep (c), turned into a step.

<task>
For each item below say whether the revision CLOSES your round 3 finding, or
does not, and where it does not name what is still wrong. Then the sweeps.
</task>

<changes>

1. CREATE-NEW SEMANTICS. Replaced rather than patched. Every dispatch now
creates ITS OWN DIRECTORY with `New-Item -ItemType Directory` and no
`-Force`, which fails when the path exists; all eight control paths live
inside it. Creation IS the reservation, so the check-then-use window you
named is gone, and so is the round-numbering uniqueness problem you cited
against `model-prompting-notes.md:279-295`. Task 2 pins the create line and
separately pins that `-ItemType Directory -Force` appears nowhere.

2. THE STATE COUNT DISAGREEING ACROSS DOCUMENTS. Now SEVEN everywhere, with
LIVENESS FIRST and dominating: while the pid is alive nothing is
interpreted. Your (a) findings are in it - state three covers failed reads
and partial writes, and state six is a reply artifact that is empty,
unreadable, or refused by the lane's own binding. `SKILL.md` names "seven
states" at the point of use and Task 2 pins that phrase. The spec's
constraint section was rewritten and records how the count went four, five,
six, seven across three rounds, and says to treat the class as open.

3. THE KIMI LANE HAD WRAPPERS AND NO LAUNCH, AND NO REPLY ARTIFACT. Both
fixed. Task 5's pin asserts the launch line at count `>= 3` - dispatch,
resume and write-probe - and asserts the reservation at `>= 3`, so leaving
any one call behind fails it. The write-probe gets its own reservation,
wrapper and launch written out, not a sentence. The lane's REPLY ARTIFACT is
declared: stdout to `$d\reply`, stderr to `$d\transcript`, which is the
change that stops every successful Kimi call landing in state five.

4. WRAPPER EXTRACTION. Unique HTML-comment markers before every wrapper and
launch fence; exactly one match required per marker; the Markdown-to-copied
indentation transformation reproduced explicitly rather than normalized; an
assertion that no `<placeholder>` survives rendering; and
`<kimi-code-binary>` substituted with the stub's ABSOLUTE path, because you
are right that PATH shadowing cannot intercept an absolute invocation. Task
8 also deletes a marker in a scratch copy and requires the gate to FAIL, so
the gate is proven able to fail.

5. YOUR SWEEP (c), TASK BY TASK. Task 1 gains a test asserting the literal
`BODY_TOKEN_CEILING = 5900` and the reason string, because the band tests
read the constant dynamically and pass either way. Task 2's `-k` expression
now names all five of its own tests. Task 4's oracle is those same five.
Task 5's oracle is the `>= 3` counts. Task 6 adds a `grep -c core.hooksPath`
check. Task 7 adds `grep -c "STOP and surface it to the user"` expecting 0.
Task 8 proves it can fail. Task 10 is now "Reconcile the spec, close the
items, run the gates" and its oracle is a grep across BOTH documents for a
stale state count or a sentence saying the Kimi lane is not detached - the
check you found missing. The stale Task 9 and 10 record text is gone.

6. THE SPEC. Constraints rewritten to seven states with liveness first. The
three "open questions" are now "questions the debate settled", kept with
their answers. A section names the five regions that exist.

</changes>

<final-check>
UNVERIFIED list as before.

Base rate for the sweeps: you have found a completion-model hole in every
round so far - a stale-artifact combination, a missing state, and then
acceptance on path existence with no liveness priority. Three for three. Do
not treat the rewrite as having reset that.

(a) An EIGHTH state, or a combination the seven do not cover. Look hardest
at the boundary the rewrite introduced: the directory reservation succeeds,
and then the wrapper write or the launch itself fails. What is on disk, what
does the poll see, and which state is it?

(b) The single shared launch block is the structural fix. What does
CENTRALIZING it break or fail to catch that five separate copies would have
caught? Name a concrete failure, not a risk.

(c) Task-local oracles are the other structural fix. For each of the ten
tasks, is its oracle actually capable of failing while the rest of the suite
passes? Name any task whose oracle is still satisfied by a partial or absent
change. I would rather hear that three of them are weak than hear that all
ten are fine.
</final-check>
