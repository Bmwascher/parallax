Round 31. Your round-30 fix is applied and verified. This round is the Task 7
review you asked for, plus one finding I found in it and one gate I cannot
satisfy on this machine.

## Round 30's fix, closed

I froze the child-scriptblock form you recommended, prefixing the chain with
`$ErrorActionPreference = 'Stop'` inside `& { ... }` with a `try/catch`, rather
than adding a third bespoke guard. Plan revision 29, `Fixed names and values`.

Verified three ways before accepting:

1. The template stored in `tools/new-kimi-lane-home.ps1:171` is BYTE-IDENTICAL
   to the plan's frozen line once PowerShell's doubled-quote escaping is undone.
   1589 characters each.
2. The reproduction that started round 30, re-run on both hosts with the same
   stubs, an owner stub printing `not json at all` and a login stub touching a
   marker:

   ```
   powershell.exe: exit=1  login stub RAN = False
   pwsh.exe:       exit=1  login stub RAN = False
   ```

   Was `True` on both hosts before.
3. Task 6's matrix is now NINE rows. Rows 1 through 6 assert the login wrapper
   is never invoked by MARKER ABSENCE, not by exit code, because the old chain
   did exit nonzero, by the login's own later failure. Rows 7 through 9 assert
   it IS invoked once owner resolution is valid.

Four caller defects went with it, all confirmed by me in the committed code
before the fix:

- a scalar `fields` value was coerced by `@(...)` and read as a valid
  one-element list;
- blank lines were discarded before the line count, so a two-line reply with a
  blank separator counted as one and satisfied "exactly one line";
- `Get-Content -ErrorAction SilentlyContinue` turned a FAILED stderr read into
  an EMPTY stderr, which the four-part acceptance rule reads as clean;
- `Start-Process -ArgumentList` joined unquoted paths, so a path with a space
  split into two arguments.

The fourth one had a test written around it. The success-row fixture's docstring
said it kept the lane home "free of a space in the SAME path segment" because
the shipped code "mis-tokenizes a `-File` argument that combines a space with an
embedded apostrophe; that is a pre-existing property of a script this task only
invokes." A green suite over a real bug. The fixture is now `o'learys lane
home`, apostrophe and space in one segment, and it passes because the code is
fixed rather than because the fixture avoided it.

113 tests per host on `powershell.exe` and `pwsh.exe`. Commit `8e5dcaf`.

`tools/new-kimi-lane-login.ps1` turned out to emit NO recovery command at all,
so that defect was in one file, not two. I checked rather than assuming.

## Task 7, which you flagged as unreviewed

Built and committed at `29f975b`. Three modules, as the plan freezes them:
`evals/tools/lane_credential_live_support.py` (the shared production helper in
its own non-test module), `test_lane_credential_live.py` (the seven live items,
9 tests), `test_lane_credential_live_support.py` (the offline oracles, 23
tests).

What I verified myself:

- The support suite passes 23 tests on BOTH hosts with no opt-in and no real
  credential. It imports the same production helper the live suite uses.
- The helper imports clean with no live environment set, so the offline suite
  does not drag live setup in. That was your r7 point.
- `dispatch_and_guard` owns process capture and runs the secret guard before
  anything can render a stream, so the `probe-record.md` write happens on
  guard-cleared values. The plan requires exactly that.
- The refusal direction is the safe one. With `PARALLAX_LANE_LIVE` set and the
  homes absent, all nine tests ERROR rather than skip, naming
  `tools/new-kimi-lane-login.ps1` and the three missing variables. Without the
  opt-in they skip.

## The finding: a pin that cannot fail

`PROBE_RECORD` is WRITTEN and never read back. Three references in the whole
tree: the constant, the `mkdir`, the `write_text`. No assertion consumes it.

So each run re-measures the absolute-key stderr and REWRITES the record. If the
kimi-code client changes its error message tomorrow, the record silently
updates and nothing fails. The two-run stability check inside the test proves
stability WITHIN one session only.

The plan calls this value "the pin": "Live command oracles are MEASURED ONCE,
then pinned" and "**The pin is the COMPLETE normalized stderr.**" A file that
rewrites itself on every run is not pinned.

I want to be accurate about the blast radius rather than overstate it. The
LOAD-BEARING fact, that an absolute `oauth.key` does not resolve, is still
checked directly by `assert exit1 != 0`. It is only the exact message text that
is unlocked. And the plan text is genuinely ambiguous: it says the implementer
"runs that case once and records" the values, which reads as documentation, and
separately calls the result "the pin", which reads as a locking assertion. The
implementer picked the first reading. I do not think that was unreasonable, and
I would rather you tell me which one the plan meant than have me decide.

There is a practical edge too. `probe-record.md` is COMMITTED to a public repo,
so a test that rewrites it on every run dirties the tree every time the live
suite executes.

## The gate I cannot satisfy

Task 7 step 2 requires both host commands to pass with ZERO skipped. That
collects the live module, which needs three pre-provisioned lane homes.
`PARALLAX_LANE_LIVE_HOME_A`, `_B` and `_C` do not exist on this machine,
because creating them requires the one-time interactive login the suite is
explicitly forbidden to perform, and the manual setup sequence is a human
action by design.

So Task 7 is verified OFFLINE and UNRUN LIVE, and I have recorded it that way
in the build ledger rather than claiming the gate. Nothing in this branch may
claim measurements 5, 6, 7, 10, 11, 16 or 17 are re-verified by an executed
gate.

## Questions

1. Which reading of the pin did the plan mean? If it is the locking one, I will
   have the record READ when it exists and asserted against, with the write
   confined to a first measurement or an explicit refresh flag. Say which, and
   say what a run must do when the record is ABSENT: fail, or measure and
   write. Both directions have a trap and I would rather you choose.

2. Task 10 requires a clean local suite and CI wiring. How should it treat a
   live gate that cannot run without a human login? My inclination is that the
   branch merges with Task 7's live half explicitly UNRUN and named as such in
   the attestation's verification status, rather than either faking the homes
   or dropping the gate. But that weakens the merge claim and you should say
   whether it weakens it too far.

3. Is there anything in the Task 7 code you want me to check that I have not?
   You have found four defects in code I had already reviewed and committed, so
   I am asking rather than assuming my offline verification covered it.

## Build state

Tasks 1 through 7 built and committed, plus the round-30 remediation. Per-task
provenance, including one task with no implementer report and Task 7's unrun
live half, is at
`docs/superpowers/plans/rounds/2026-08-01-cred-lock/build-ledger.md`. Tasks 8,
9 and 10 remain.
