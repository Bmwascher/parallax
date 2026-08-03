Round 2. Evidence rules and verdict grammar as before.

<position-changes>
ACCEPTED IN FULL: every finding in Tasks 1 through 9, and all five answers
to Q1 through Q5. I am not contesting any of them. Plan r2 will carry them.
The three I want to single out because they are the ones that would have
reached built code:

- Task 1.1. My step 1 said `OpenOrCreate` and "empty means we just created
  it", which contradicts my own rule 7 and the settled design. A crash after
  `SetLength(0)` leaves a zero-length file that the next caller reads as
  free and STEALS. This is the exact class the design exists to prevent and
  I wrote it into the plan.
- Task 1.2 with Q2. Rule 3 demands a nonce that `-Acquire` cannot receive,
  and force-release demands one too, so a caller that lost its nonce is
  deadlocked until its own process dies. Unimplementable and a deadlock,
  both.
- Task 5.4. "No regular file that is not visible through the junction" is
  vacuous, because everything under a correct junction is visible through
  it. It would pass on a plain copied directory too if the junction happened
  to exist beside it.

Task 6.2 deserves a specific note: you cited my own discarded empty-hash
measurement as the reason command failures must be fatal. That is the right
citation. I made that mistake with a real measurement three hours ago and
then wrote the same shape into a plan.
</position-changes>

<new-claim>
15. THE WINDOWS CI JOB IS BROKEN AT HEAD ON THIS BRANCH, and it is a merge
blocker independent of everything else here. Your Task 1.8 citation of
`.github/workflows/skill-evals.yml:79-99` led me to check the modules it
names. `evals/multi-model-verify/test_kimi_lane_lock.py` is listed in BOTH
Windows steps, at `:84` and `:95`, and the file DOES NOT EXIST: commit
`775472c` deleted it along with `tools/kimi-lane-lock.ps1` and did not touch
the workflow. Verified three ways:

- `git show --name-only 775472c` lists the test file and the tool as its
  only deleted paths, and the workflow is not among the files it touched.
- `git log 6201e30..HEAD -- .github/workflows/skill-evals.yml` names only
  `9d50196`, which predates the deletion.
- `python -m pytest evals/multi-model-verify/test_kimi_lane_lock.py -q`
  exits 4 with `ERROR: file or directory not found`.

Nobody saw it because `git rev-parse --abbrev-ref '@{u}'` reports
`no upstream configured for branch 'feat/kimi-code-backup-lane'`. The branch
has never been pushed, so this job has never run on it. Pushing it as-is
turns both Windows steps red.

My Task 1 creates a file at that exact path, so the plan as drafted would
un-break CI BY COINCIDENCE, with a suite for a different tool that happens
to share a name. That is not a fix and r2 will not rely on it. The workflow
is repaired explicitly and every new dual-host module is added to both
steps.
</new-claim>

<proposals-to-check>
Five resolutions where your finding named the defect but left the choice
open. Tell me whether each closes it.

P1, for Q2's deadlock. Make the NONCE VISIBLE rather than secret.
`-Status` prints it as part of the `held` object. The nonce's job is to
distinguish two debates from ONE session, not to be unforgeable, and the
design already states these are guarded human overrides and explicitly not
authentication. So the recovery path becomes: run `-Status`, read the
complete identity including the nonce, pass it to `-ForceRelease`. Combined
with your Task 1.2 fix, `-Acquire -Nonce <t>` is required for idempotent
re-acquire and forbidden otherwise. Does printing the nonce close the
deadlock without weakening anything the nonce was carrying?

P2, for Task 1.7's missing oracle. Rule 5 says an unreadable start time is
ALIVE. Deterministic Windows fixture: a SYSTEM-owned process, for which
`Get-Process` succeeds while reading `.StartTime` raises for a
non-elevated caller. If that proves machine-dependent or elevation-
dependent, fall back to an explicit test seam in the script. Which do you
want as the primary, given that a seam is testable everywhere but tests the
seam rather than the condition?

P3, for Task 5.4's vacuous oracle. Replace it with FILE IDENTITY: assert the
debate path and the lane path resolve to the same NTFS file id, and
separately assert that a byte written to the lane credential is observable
through the debate path within the same test. A copy fails both; a junction
passes both. Is file-id equality the right primary oracle, or do you want
the write-through observation as primary?

P4, for Task 1.8, Task 2.4, Task 5.5 and Task 9.2 together. Adopt the
selector the workflow already uses: honour `PARALLAX_PS_HOST`, refactor
`evals/multi-model-verify/test_kimi_lane_home.py:21` off
`shutil.which("powershell") or shutil.which("pwsh")` onto it, mark the new
OS-level modules Windows-only so the ubuntu job does not collect them, and
list every new dual-host module in both Windows steps. Does that cover all
four findings, or does the ubuntu job need something beyond a platform
marker?

P5, for Task 8.1. r2 will carry the exact literal text of both contract
regions and both pins, not a description of what they must say. Before I
write it: the `lane-lock` region must also carry the CALL LIFECYCLE you
identified in Task 8.2 — where owner identity is resolved once, how the
builder receives it, how the nonce is captured and retained, and how
cleanup supplies it. Should that lifecycle live INSIDE the `lane-lock`
region, or as a separate declared region, given that a region too long for
one pin is by rule two regions?
</proposals-to-check>

<final-check>
Same as before. Note that claim 15's three verifications are repository
facts you can check directly, unlike measurements 1 to 21.
</final-check>
