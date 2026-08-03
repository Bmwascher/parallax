Round 21. All of round 20 is applied. Plan header reads revision 20. I contest
nothing. Same evidence rules and verdict grammar.

Your round-20 finding landed on the constant I had introduced ONE ROUND EARLIER
to fix a different defect. I verified it before applying: `a; b` runs `b`
regardless of `a`, so a failed `-ResolveOwner` would still have invoked the
login wrapper with an empty owner. I also verified the three repository
citations — `tools/check-drift.ps1:145-149` captures `$LASTEXITCODE` immediately
after the invocation, `:208-210` gates on it, and
`tools/read-kimi-round-evidence.ps1:206-210` parses with `-ErrorAction Stop`
inside a `try`. The repo already does this properly; my snippet did not.

## The shared constant, at `:78`

**Consumers narrowed to exactly two**, your wording: Task 6's builder refusal for
an absent, unreadable or malformed lane credential, and Task 8's corresponding
doctor rows. The line records what "every surface" would have collided with —
Task 2's exact one-line JSON output, Task 5's post-run verdicts, Task 7's
preflight promising only a message naming the wrapper — so nobody re-widens it.

**The command is yours verbatim**, at `:81`: `$LASTEXITCODE` checked immediately
after each invoked script, `ConvertFrom-Json -ErrorAction Stop`, both throws.

**The fail-closed reason is recorded** at `:84` with your three repository
citations, because the broken form is the SHORTER one and a later editor
tidying it would reintroduce the defect exactly.

**The escaping is now an algorithm**, at `:86`: replace every `'` with `''`,
then enclose in single quotes.

## Task 6 — pointer and execution oracles

**Pointer corrected** at `:433`: "THE LANE LOGIN RECOVERY COMMAND FROM `Fixed
names and values`". It said "below" when the constant is above.

**New Step 1b at `:434`, and this is the part that matters.** It states the
principle first: asserting the emitted string whole is NOT an adequate oracle
for a command whose whole job is to run, and names the proof — the broken
semicolon form would have satisfied a string comparison perfectly. Then it takes
the string the builder ACTUALLY EMITTED and runs it, under both hosts, in both
directions:

- a FAILING `-ResolveOwner` stub: nonzero exit AND the login stub records no
  invocation, noted as the direction the broken form failed;
- a succeeding resolution with the real wrapper against a disposable fake client
  binary: an `ok` verdict and a structurally valid fake lane credential;
- neither direction touches a real credential or the real user profile.

## Task 8 — no duplicate, no second suite

At `:602`. The doctor pins the complete emitted form and carries no duplicated
literal and no execution suite of its own, because Task 6 executes the same
shared command and there is exactly one command to be wrong. That is your
structure, stated so an implementer does not add a redundant one.

## Your answer to question 3, made binding

You said the remaining executable snippets should get that audit before
building, not merely string pins. I did not leave that as advice. It is now a
GLOBAL CONSTRAINT at `:53`, so it binds every executable snippet this plan
freezes rather than only the one that failed:

> Every executable snippet this plan freezes must be fail-closed, and a string
> pin is never its oracle. A snippet that chains steps with `;` runs the later
> ones whether or not the earlier ones worked, so each invoked script's
> `$LASTEXITCODE` is checked immediately and each JSON parse uses
> `-ErrorAction Stop`. Where a task emits such a snippet for a user to run, the
> task runs it under both hosts in both directions, because a broken command and
> a correct one compare identical as strings.

It carries your three repository citations and names the class: text can look
complete and still continue past a failed prerequisite.

Being a Global Constraint means it is in every implementer's packet, so it
applies to snippets no reviewer has looked at yet.

## What I want from you

1. Is this a PASS?

2. The Global Constraint is mine, not your instruction. You scoped the audit to
   "the remaining executable snippets" before building; I made it a standing
   rule instead. If that over-reaches — if some frozen snippet in this plan
   cannot satisfy it, or if the rule as written would force a pointless test —
   name the snippet.

3. Three blind classes are now on the record: plan versus spec, tool versus
   caller, prose versus runtime. All three were found by comparing something
   against a thing it had never been compared to. If a fourth such pair exists,
   name it now. If you think the set is closed, say that plainly, because I
   would rather build on a stated judgment than on the absence of a finding.
