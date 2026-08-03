Round 29. The plan is FROZEN at revision 27 on your round-28 PASS, and building
has started. This round reopens it for ONE unfrozen decision that surfaced
during implementation. Same evidence rules and verdict grammar.

## Where building is

Task 1 is built and committed at `ac3e4d8`. I reviewed it before accepting and
found one defect, which is worth telling you because it is a class you found
four times in the plan text and it reappeared in the code the plan produced.

The parity checker returned no errors when it discovered NO host steps:
`check_host_parity({}, REQUIRED) == []`. Rename the environment variable, break
the regex, or delete the Windows job, and the check exits 0 having verified
nothing. I sent it back. It now refuses unless the discovered host set is
exactly `powershell.exe` and `pwsh.exe`, with a fifth mutation that renames the
variable and requires failure. I verified all four directions myself: none
found, one found, two-plus-a-rogue, and the correct pair.

Task 2 is built and NOT yet committed. Both hosts pass 54 tests. Steps 3, 3b and
3c all landed, both module guards are present, the script is ASCII-only, and no
token value reaches any output line.

## The unfrozen decision

The implementer reported, correctly, that the plan freezes the validator's
OUTPUT line exactly and says nothing about its CLI contract. It chose `-Path`
for the parameter and this exit-code mapping:

- `ok` exits 0
- every other status exits 1, including `absent`

Measured just now:

```
{"status":"ok","detail":"valid","fields":[...]}                 exit=0
{"status":"malformed","detail":"missing-field","fields":[...]}  exit=1
{"status":"absent","detail":"no-file","fields":[]}              exit=1
```

I did not accept this. It is a design decision, the implementer is meant to make
none, and three later tasks consume the validator.

**My concern is specific.** Task 8's doctor table has these as SEPARATE rows:

- `lane credential absent` -> `N/A`, no hash taken, with the recovery command
  (plan `:656`)
- `the validator itself fails to run` -> `BROKEN` (plan `:658`)

Under the current mapping both are exit 1, so the doctor cannot tell them apart
by exit code and must distinguish them purely by whether stdout parses. That is
survivable but fragile, and it conflates a measurement that SUCCEEDED and found
nothing with a measurement that could not be made — the distinction this plan's
governing invariant exists to protect.

Task 5 also reads the verdict at its step 5 and branches on `ok` at step 6, and
Task 6 validates at its step 3. Both treat `absent` as an ordinary, actionable
reading rather than a tool failure: absent is precisely the state that means
"run the login".

## What I think, and what I want from you

My view is that a validator which successfully determines the credential's state
has SUCCEEDED, whatever that state is, and should exit 0; a nonzero exit should
mean the validator could not do its job. That keeps "no credential" and "no
measurement" distinguishable at the exit code, which is the distinction every
caller in this plan cares about.

But I am not confident, and the opposite convention is defensible: nonzero for
any non-`ok` is a familiar shell idiom and makes `if (tool) {}` work.

1. Freeze the validator's exit-code contract. Say what each of the four statuses
   returns, and what a validator that cannot run returns, so Tasks 5, 6 and 8
   consume one definition rather than three readings of an undefined one.

2. Freeze the parameter name, or confirm `-Path` is right. It is currently the
   implementer's choice too.

3. Is there anything else the validator's callers need that the output table
   does not give them? I would rather find the second one now than after Task 5
   is built against a half-frozen interface.

## One measured fact, recorded not asked

The `unreadable` fixture needs an ACL denial and then a restore. On this machine
`icacls /reset` alone FAILS with "Access is denied" after `icacls /deny
"$user:(R)"` on a pytest temp directory: ownership does not resolve through the
OWNER RIGHTS SID for the running identity there. The implementer added
`takeown /f` before `/reset`, still inside the `finally`. It round-trips
reliably on both hosts. I am recording it rather than asking about it, but say
so if you think a test that needs `takeown` to clean up after itself is a test
that should be built differently.
