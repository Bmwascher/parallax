Round 4, mode diff. Fix re-review. Evidence rules and verdict grammar as before.

POSITION CHANGES. Every finding in your round 3 ACCEPTED in full, nothing contested. All three reproduced by running them before I touched anything, and all three re-probed by running the same attack after the fix.

R3.1a. Reproduced exactly. On this UTC-05:00 machine a lock stamped with the current instant as terminal `Z` printed `STALE - debate-A, held 1.79769313486232E+308 min`, and `debate-B` took it with no `-Force`.

R3.1b. Reproduced. A genuinely 300-minute-old `Z` stamp printed `held 0 min` and returned BUSY.

R3.2. Reproduced in substance, and my own probe misread it: I tested the exit code, printed "not reproduced", and the evidence on the line above showed the defect plainly. The object stamp threw inside the age routine, the caller compared nothing against the threshold, and the lock read `held 0 min` forever. Only `-Force` could clear it. You were right that the routine written to stop a malformed lock wedging the lane was the wedge.

WHAT CHANGED. `stamp` must be a string or the age is infinite. Parsing is `[System.DateTimeOffset]::TryParse` with `DateTimeStyles::None`, and age is `[System.DateTimeOffset]::Now - $parsed`, so every representation of one instant compares equal and a stamp with no offset is assumed local. Re-probe after: the current `Z` lock holds and its owner survives; the 300-minute `Z` lock reads `STALE - 300 min` and is broken; the object stamp is broken cleanly with empty stderr.

Your R2 and R3 PASSes are not re-opened. Your R3 answer also settled the question I put to you: `Get-LockOwner` stays out of the acquire path, because treating a null owner as free there would recreate the bypass round 2 closed.

BEYOND WHAT YOU ASKED. Re-probing the fix surfaced a second display path you had not named: the acquire notice builds its own age string and still printed "broke a stale lock, 1.79769313486232E+308 min old" after status had stopped. Both paths now say "age unusable". This is disclosed rather than folded in silently.

WHAT WAS APPLIED. Range `a8cf9bb..7ddb871`, one commit. Diff at C:\Users\Brandon\.claude\jobs\75fb2cba\tmp\diff-0160-r3fix.txt

271 passed, 1 skipped, from 262; the lock file holds 41 tests. Three static gates clean, PowerShell parse clean. `tools/check-drift.ps1` is unchanged in this range so the drift state machine was not re-run. All UNVERIFIED from your seat, as before.

CLAIMS FOR THIS ROUND.

R1. AGE NOW DEPENDS ON THE INSTANT AND NOT ON ITS REPRESENTATION. Attack the new parse path: a stamp with a fractional second beyond seven digits, a stamp with a leap second, an offset such as `+14:00` or `-12:00`, a bare date with no time, a string that parses as a date but means something else, a culture-specific format, and `DateTimeOffset.MinValue` or `MaxValue` written out in full. For each, does the lock end up held or breakable, and is that the right answer?

R2. THE THREE DEFECT CLASSES IN THIS ROUTINE ARE NOW CLOSED: non-string stamps, representation-dependent age, and impossible ages reaching a human. Find a fourth. In particular, is there any input for which the routine still throws rather than returning a value, and is every caller of it safe against the value it can return?

R3. THE FIX INTRODUCED NOTHING. Four rounds, three of them found a defect inside the previous round's fix. Treat that as prior probability. The new code is the type check, the DateTimeOffset parse, and two display branches. One of those four is the most likely to be wrong — say which and why before you look, then check it.

R4. THE RECORD IS ACCURATE. Item 6 now says the malformed-lock claim was false until this round, and the contract says an unreadable timestamp is breakable at once rather than after 45 minutes. Is either still overstated, and does anything in the record still assert a guarantee the script does not deliver?

Nothing else is under debate.

If it holds, say PASS plainly and say it first. Do not manufacture an objection to justify the round.
