Round 23. All four round-22 blockers are applied. Plan header reads revision 22.
I contest nothing. Same evidence rules and verdict grammar.

The sweep was worth asking for. Two of the four are the same pattern as Task
10's, and both would have shipped a live gate that passes on a measurement never
taken.

## Task 4 — two fixes

**Measurement 20**, at
`docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:347`. The
assertion now runs only after each host invocation is proven to have HAPPENED:
the selected host process must exit 0 and emit exactly ONE parseable result
before any type is inspected, and the asserted types are the measured ones —
ticks `Int64` on both hosts, the date value `String` on 5.1 and `DateTime` on 7.
Its own mutation makes the subprocess exit nonzero and requires the gate to FAIL
rather than report divergence.

The text names why, in the plan's own terms: one host failing and emitting
nothing while the other succeeds IS divergence, which is the empty-hash shape
the spec records at `:89-95`.

**The crash oracle**, at `:349`. The ready-marker wait is bounded at ten
seconds. On timeout the child is terminated in a `finally` and the test FAILS
WITHOUT INSPECTING THE LOCK BYTES, because a child that died before signalling
never reached the crash point. Only an observed ready marker licenses killing
the child and asserting the crash state.

## Task 7 — item 7

At `:561`. One `measure_file_snapshot` helper returning SHA-256, byte length and
mtime only after all three succeed; any read, hash or stat failure terminates
the main phase before equality is evaluated. An explicit ban on representing a
failed measurement with an equality-comparable sentinel — no empty string, no
`None`, no zero. Two support oracles forcing a pre-command hash failure and a
post-command stat failure, each required to fail, still attempt the real
`-Remove`, and follow the existing cleanup-precedence matrix.

The text records that this is the shape measurement 17 produced on its FIRST
attempt in this same cycle, where a clean verdict came from two empty strings
comparing equal. That is the strongest available argument against anyone
simplifying it later.

## Task 3 — the wait budget

At `:218`. The sleep is `min(-PollSeconds, budget remaining)`, elapsed measured
on a monotonic `Stopwatch` and never by comparing clock readings. The numeric
domain is frozen: both are base-10 INTEGER strings fitting `Int32`,
`-WaitSeconds` >= 0, `-PollSeconds` > 0, anything else exit 2 with no mutation.
Oracle under both hosts: `-WaitSeconds 1 -PollSeconds 10` contends, exits 3,
leaves the record unchanged, and returns in under five seconds. Zero-budget
immediate refusal unchanged.

Your example is in the text, because "the budget bounds caller patience" reads
as already true and only the ten-second case shows it was not.

## Task 5 — the ACL

At `:381`, the exact ACE shape the builder already uses at
`tools/new-kimi-lane-home.ps1:399-408`, cited so the two cannot drift:
`SetAccessRuleProtection($true, $false)`, every existing rule removed, one rule
for the current `WindowsIdentity` SID, `FullControl`, inheritance flags
`ContainerInherit,ObjectInherit`, propagation `None`, type `Allow`. The text
says why "one full-control rule" was not enough: a non-inheritable ACE satisfies
that wording while protecting nothing beneath.

New step 4b: after the lock is held and before any credential read or client
invocation, create the `credentials` directory if absent and apply the SAME
protected DACL directly to it, citing the design line that requires both.

The oracle at `:393` now compares the exact ACE set, inheritance flags and
propagation flags on BOTH directories rather than asserting a rule exists;
requires a second run to leave both byte-equivalent; and requires that a fake
credential created by the client under that directory carries the intended
current-SID access, which is what proves inheritance reached the FILE and not
just the parent.

## What I want from you

1. Is this a PASS?

2. Task 5's step 4b creates the `credentials` directory inside the login
   wrapper. Task 6's builder junctions each debate home's `credentials` at that
   directory. If a debate is ever built before any login has run, the junction
   target will not exist. I believe that is already handled — the builder
   refuses on an absent lane credential before it would matter — but I am
   telling you rather than assuming, because I introduced the ordering this
   round.

3. If PASS, the record finalization is DRAFT to FROZEN at revision 22, rounds
   used 23, and the outcome line.
