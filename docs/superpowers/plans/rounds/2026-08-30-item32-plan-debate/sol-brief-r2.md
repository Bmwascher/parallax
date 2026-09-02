Round 2. Evidence rules, citation requirement and verdict grammar as before.

The plan was revised against every finding you returned. It is at
docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md, now nine
tasks, and it carries a "What round 1 changed" table at the end mapping each
of your findings to where it landed. Re-read it; the tree you are reading has
been rebuilt at the revised head.

I reproduced all eight FIX findings against the repo before accepting them.
None was refuted. Four I verified by reading the code you cited rather than
taking the citation: check-drift.ps1's Stop-Job at 1112-1115, the
whitespace-normalized _norm reader at test_backup_lane.py:47-50, the
write-probe at backup-lane.md:353-359, and the mirror's git commit at
new-review-mirror.ps1:1071-1089 whose own BLOCKED message names the hooks.

<task>
For each numbered item below, say whether the revision CLOSES the finding, or
does not. Where it does not, name what is still wrong. Then answer the two
new questions and the two sweeps.
</task>

<changes>

1. FALSE COMPLETION. Four states became five, and every control path -
wrapper, pid, exit, reply, transcript - is now round-numbered and must not
exist before the launch, with the launch refusing if one does. Region
detached-dispatch-states in Task 3. Task 8 Step 2 plants a stale exit file
and asserts the launch REFUSES, then kills the wrapper after the reply
appears and asserts the poll reports transport failure.

2. THE EXIT WRITE WAS NOT LAST. The wrapper now opens `$code = 1`, captures
`$priorOutputEncoding` OUTSIDE the try, ends `} catch { $code = 1 } finally
{ ... }`, and writes the exit file after all of it.

3. check-drift.ps1. Reason corrected. It stays out of scope because it is
governed by its own explicit 900-second automation timeout, not because it
is immune.

4. THE BACKUP-LANE PINS. Claim withdrawn. Global Constraints now records
that those pins read whitespace-normalized text and prove neither byte
identity nor that any wrapper invokes the strings.

5. THE THIRD KIMI CALL. Named in Task 5 with its line reference, and handed
to item 51 along with the other two.

6. TASK 5 CLAIMED DETACHMENT AND IMPLEMENTED NONE. Task 5 is now a
deferral. See question A.

7. THE QUOTING CLAIM. Region detached-dispatch-mechanism now says the
wrapper file removes the `Start-Process -ArgumentList` serialization
boundary and does NOT remove every quoting layer, because the wrapper is
still parsed by PowerShell and still builds a native argv.

8. "ONLY MECHANISM". Region one calls Start-Process the selected mechanism
and states why Start-Job fails.

9. STREAMS. All three redirected, matching check-drift.ps1:923-927.

10. TIMEOUT. Policy frozen at the user's direction: bounded polls, a
THIRTY-MINUTE escalation that reports the round UNFINISHED and asks the
user to continue or abandon, and neither answer is ever a review result.
Region detached-dispatch-operation.

11. THE TWO UNVERIFIABLE HARNESS FACTS. Both now marked in Global
Constraints as harness tool contract rather than repo evidence.

</changes>

<new-questions>

A. THE SCOPE REDUCTION, which is the largest change and the one I am least
sure of. Task 5 no longer detaches the Kimi lane at all. My reasoning: the
brief is passed inline in the `-p` payload (backup-lane.md:24-30), and every
way of getting those bytes into a wrapper changes the argument path -
embedding the brief as wrapper source needs byte-safe generation for
arbitrary text, and reading it into a variable inside the wrapper replaces a
literal argument with a variable expansion, which is exactly the 5.1
splatting surface item 51 measured. So detaching this lane requires deciding
item 51, which the user placed out of scope.

Is that reasoning sound? Specifically: is there a way to detach all three
Kimi calls that leaves the argument path byte-for-byte as it is today? If
there is, the deferral is wrong and I want to know now. If there is not, say
so, because a deferral nobody checked is how an item quietly stops being
done.

B. AN AMENDMENT INTRODUCED BETWEEN ROUNDS, at the user's request, not from
your review. The user asked that a backgrounded call always name its
reviewer LANE and its ROUND, so a task list showing several lanes across
several rounds is readable. It landed as the last two sentences of region
detached-dispatch-operation, including the admission that nothing enforces
it and the region is its only carrier.

Judge it on the same terms as the rest: does it belong in this cycle at all,
and does putting an unenforceable convention inside a pinned contract region
weaken that region? A pin proving a rule is WRITTEN, next to rules that are
mechanically enforced, may be worse than no pin.

</new-questions>

<disclosure>
Two things happened during the revision that you should weigh.

First, I introduced a PowerShell parse error into the revised wrapper - a
`} finally {` after an already-closed `catch` - and caught it myself before
dispatching this round. It is fixed. I am telling you because it is evidence
about the design rather than about me: the wrapper block is transcription-
sensitive, a session copying it can break it in a way that dies before codex
runs, and that is a new failure mode this change creates. Task 4 now warns
about the three load-bearing details and Task 8 Step 1 runs the wrapper for
real. Ask whether that is enough.

Second, the mirror rebuild for this round FAILED with: "ERROR: ... 
skills-override.txt already exists - a stale override reads exactly like a
fresh one". That is the same defect class as the exit-file staleness rule in
change 1, already enforced by this repo's own tooling. I offer it as
supporting precedent for the round-numbered control paths, not as proof.
</disclosure>

<final-check>
UNVERIFIED list as before.

Then the two sweeps, naming an instance or reporting none explicitly:

(a) Does the REVISED plan introduce any new way for an unfinished or killed
round to be read as a completed one? You found one last round. Assume the
class is not exhausted and look for a second, including in the parts that
changed since you last read them.

(b) The revision adds failure paths that did not exist before: a wrapper
that will not parse, a launch that refuses because a control path exists, a
poll that escalates at thirty minutes, and a mirror build that BLOCKS on
hook suppression. For each, say whether the plan makes the failure
DISTINGUISHABLE from success, or whether any of them can end up looking
like a clean result or a clean skip.
</final-check>
