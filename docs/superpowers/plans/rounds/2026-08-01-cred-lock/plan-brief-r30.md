Round 30. Reopening FROZEN text during building. One defect, and it is in the
recovery command we hardened at rounds 20 and 21 for exactly the property it
turns out not to have.

## The finding

Task 6's implementer found it and did the right thing: it did not alter frozen
text it has no authority over, and it did not assert the stronger claim its own
test was told to make. It documented the discrepancy instead and reported it.

**`-ErrorAction Stop` on that pipeline does NOT halt the `;`-chain.** It makes
that one statement's error terminating for the statement, but the one-liner sets
no `$ErrorActionPreference` and has no `try/catch`, so PowerShell's default
`Continue` carries execution to the next `;`-separated statement anyway.

I reproduced it myself on both hosts before writing this, with a stub that exits
0 and prints `not json at all`, and a login stub that touches a marker file:

```
powershell.exe: login stub RAN despite malformed owner JSON = True
pwsh.exe:       login stub RAN despite malformed owner JSON = True
```

The login wrapper is invoked with a NULL identity. The plan's Task 6 row 2
requires "never invoked". The chain does still exit nonzero, but by the login's
own later failure, not by the guard that was supposed to stop it.

## Why this matters more than the exit code

The whole point of round 20 was that a plain `a; b` chain runs `b` whether or
not `a` worked. We fixed the two EXIT-CODE boundaries and left the PARSE
boundary guarded by an idiom that does not do what its name implies. So the
command is fail-closed at two of its three dependencies and open at the third,
which is worse than uniformly naive: it reads as hardened.

This is your own third blind class, plan prose versus runtime semantics, and it
survived rounds 20, 21 and the round-28 PASS because every one of those reads
the text rather than running it. Task 6's four-row execution matrix is what
caught it — the oracle you specified at round 21 precisely because a string pin
cannot test a command whose job is to run. It worked.

## What I have NOT done

I have not changed the frozen command. It lives in `Fixed names and values` and
is consumed by Tasks 6 and 8, so it is yours to re-freeze.

## What I think the fix is

Prefix the chain with `$ErrorActionPreference = 'Stop';` so a terminating error
anywhere actually terminates, rather than adding a third bespoke guard. That
also covers failure modes we have not enumerated, instead of the two we happened
to think of. The alternative, an explicit `if ($null -eq $owner -or -not
$owner.ownerPid) { throw ... }`, guards only this one case and leaves the same
trap for the next editor.

But this is the third revision of this one command, and I would rather you
choose the form than have me pick a third time.

## Questions

1. What is the frozen command now? Give it verbatim, and I will apply it to
   `Fixed names and values` and re-dispatch both consumers.

2. Task 6's row-2 oracle currently documents the real behaviour rather than
   asserting "login never invoked", because asserting the false thing would have
   been worse. Once the command is fixed, that row should assert the stronger
   claim. Confirm that is what you want.

3. Is there a fourth boundary in that command I have still not checked? It has
   two exit-code checks, one parse, and one implicit dependency on
   `Join-Path $env:TEMP` succeeding. I have verified the first three behave as
   written now that I know not to trust the idiom.

## Build state, for context

Tasks 1 through 6 are built and committed; Task 7 is built and unreviewed. Every
task was verified by me independently of its implementer's report, and the
per-task provenance is recorded at
`docs/superpowers/plans/rounds/2026-08-01-cred-lock/build-ledger.md`, including
one task whose report never arrived and whose evidence is therefore mine alone.
