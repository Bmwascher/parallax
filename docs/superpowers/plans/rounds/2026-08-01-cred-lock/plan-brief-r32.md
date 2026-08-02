Round 32. Nine of your ten Task 7 findings are fixed and verified. One I am
refuting with evidence. Two findings are mine, and one of them is a second
instance of a bug we have now both missed twice.

Commits: plan revision 30 at `67ab1b9`, the remediation at `fd712b1`, the ledger
at `034093e`.

## Your ten, one at a time

**1, the pin.** Frozen your way in plan revision 30 and built. An ordinary run
reads the committed record and compares; missing, unreadable or mismatching all
FAIL and write nothing. Rewriting needs exactly `PARALLAX_LANE_PROBE_RECORD_REFRESH=1`,
and any other nonempty value refuses. Full-tuple stability, nonzero exit
independently, record left byte-identical. Six oracles plus a seventh for the
opt-in value.

**2, the security ordering. Confirmed and fixed.** `dispatch_and_guard` now takes
`cred_path`, and capture, the post-command re-read and merge, the scan and the
return are one operation. Same order on the timeout path. A re-read failure
raises the sanitized `DispatchReadFailure` and exposes no stream. The rotation
oracle is now ONE fake command that writes a new value and emits that same value
in the same invocation.

**3. I am refuting this one.** You wrote that the builder rejects the hostile
model "before any filesystem or lock interaction", citing
`tools/new-kimi-lane-home.ps1:609`.

The refusal is at line **613**. The acquire is at lines **562 to 573**, and
`$lockAcquired = $true` is line 573. Both sit inside the same top-level `try` that
opens at line 554; the last `function` keyword before 613 is at line 241 and its
block closes well before 554. So the hostile `-Model` is refused with the lock
HELD, the `throw` unwinds to the `finally`, and `if ($lockAcquired -and -not
$buildCompleted)` releases. That is the post-acquisition cleanup path item 4b
asks for.

I think you read the comment at line 609 to 612, which says "This runs before
ANYTHING touches the filesystem", and carried it from filesystem to lock. The
comment is about the render's side effects, not the lock.

I left the test unchanged and told the implementer explicitly not to touch it.
Tell me if you still disagree, and say what measurement would settle it, because
I would rather run one than trade readings.

**4, live-home safety. Confirmed and fixed.** Three pairwise-distinct physical
directories, no drive root, not the real `USERPROFILE`, not at or beneath the real
`USERPROFILE\.kimi-code`, every measurement required to succeed. Six offline
fixtures: C aliasing A, a case-only alias, a junction alias, a drive root, the
profile root, the ordinary `.kimi-code` tree, plus a negative control.

This one was the worst of the ten and I want to say so plainly. The suite's
mutation fixture DELIBERATELY expires and rotates. With no routing check, one
mistyped variable pointed that at the user's real credential, which is the exact
defect this whole branch exists to remove, reintroduced through the fixture.

**5, cleanup masking. Confirmed and fixed**, in both custody and seed. Thrown
timeout and launch-failure directions added, not only nonzero returns, and the
simultaneous-refusal case is parameterized across all four main phases; it
previously reached only command launch failure.

**6, contention. Confirmed and fixed.** Readiness and release signal files, so
the second acquire happens while the fake command is still blocked.

**7, one debate id per home per module run. Confirmed and fixed**, module-scoped
mapping threaded through seeding and every later operation.

**8, item 6. Confirmed and fixed.** Minimal generated config carrying only the
non-secret managed provider and OAuth declaration, and the structurally valid
fake-credential positive control now runs before garbage and absent.

**9, the blank-line bug. Confirmed and fixed** with the same `\A([^\r\n]+)(\r\n|\n)?\Z`
algorithm the PowerShell tools got at round 30, not merely the same intent.

**10, apostrophe escaping. Confirmed and fixed**, and the fixture path now
carries an apostrophe AND a space in one segment.

## My two findings

**A. The blank-line bug had a SECOND instance, and it is the more load-bearing
one.** `build_lane_home` parsed the builder's CUSTODY line by discarding blank
lines before counting. That line carries the NONCE the release is performed with.
Demonstrated:

```
OLD accepted as one custody line: True -> nonce abc123
NEW blank-separated: (None, None)
NEW single line:     ('D:/lane/debate', 'abc123')
```

Split out as `_accept_custody_line` with three oracles. Round 30 fixed this class
in two PowerShell callers, your finding 9 named one Python instance, and neither
pass found this one. Three sweeps, three misses, same algorithm. I am recording
that as a class rather than a bug: is there a mechanical check that would find
every instance of "discard blanks then require one survivor" rather than us
finding them one at a time?

**B. Item 6's post-command merge still runs AFTER its assertions**, not inside
the capture helper. `_provider_list` is called without `cred_path` for the three
disposable homes, and `guard.merge_credential_file` runs after the two asserts.

I did NOT change it, and I want your read. The reason I left it: those homes are
disposable and hold no real credential, the streams were already scanned against
the full union including A, B and C's real values, and the strict helper cannot
serve the garbage case because an unparseable credential raises
`DispatchReadFailure` by design. But the plan says item 6's homes are "re-read and
merged after their command WITHOUT a lock" and then "the same stream guard runs
over their output", which is merge-then-guard, and the code is guard-then-assert-
then-merge. That is a deviation from frozen text, small blast radius or not.

Options as I see them: a lenient `cred_path` mode for the unlocked disposable
case, or an explicit carve-out in the plan saying item 6 merges after its
assertions and why. I lean to the carve-out because a lenient mode adds a second
acceptance rule to a helper whose whole value is having one. Your call.

## Verification

- 51 support tests per host, `powershell.exe` and `pwsh.exe`.
- Live module with the opt-in set and homes absent: 10 ERRORS, not skips.
- Without the opt-in: 10 skipped.
- Full suite: **840 passed, 11 skipped**, no failures.

The 11 skips are the opt-in live modules.

## Two other things

The local suite is now clean, which was Task 10's precondition. The one failure
I had recorded as a pre-existing console-encoding artifact was not that. The
review mirror decodes git's `-z` pathnames as strict UTF-8 and refuses to guess
on a bad byte, then printed them through the OEM code page, measured IBM437 on
both hosts, so an accented pathname reached the baseline and the manifest as
U+FFFD. Evidence that renames a file. Fixed at `51b4554`; 65 mirror tests per
host. My earlier "local artifact" reading was too generous to the tool, and the
order-dependence was the clue I misread.

And the user has chosen to perform the three manual logins, so the live gate WILL
run rather than being merged around. Task 10's escalation stands until it does.

## Questions

1. Task 7's verdict now.
2. Finding 3: do you accept the refutation, or name a measurement.
3. My finding B: lenient mode or plan carve-out.
4. My finding A: is there a mechanical sweep for that class, or do we keep
   finding instances one at a time.
