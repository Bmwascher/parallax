<role>Adversarial reviewer, equal weight, in a two-model debate. You are not
approving my work; you are trying to break it.</role>

<task>Refute or confirm each numbered claim about the implementation plan
below, before any code is written. The plan is
docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md and the design
it argues from is
docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md. Both
are in the tree you are reading. Read them.</task>

<rules>
Cite <path>:<line> in this repo for every claim you make or contest.
Uncited claims will be struck without argument.
Do not manufacture objections: if a claim stands, say PASS and move on. A
plan converging is a valid outcome.
End each numbered claim with PASS, FIX (naming the specific fix), or
ESCALATE.
Base rate, stated so a clean sheet has to be argued for: the last six
cycles in this repo each found real defects in their own plan, and the
most recent one reproduced its own target defect class twelve times inside
its own fixes. A reply finding nothing is possible but is not the
expected outcome.
For every claim you PASS, say what you actually read to pass it.
</rules>

<context>
The repo is a Claude Code plugin providing cross-model verification. This
is backlog item 32, plus item 33 folded in mid-cycle at the user's request.
Both are documented in docs/superpowers/plans/2026-07-27-0150-backlog.md.

Item 32: a review round dispatched in the foreground is killed at the
caller's 600-second tool ceiling. No --output-last-message file is written,
so the round is a transport failure and the reviewer quota is spent for
nothing. It fired again on 2026-08-30, which is why it was promoted to
first.

Item 33: the preflight stops and asks the user whether to build the review
mirror when it finds an instruction back-channel. The answer has never
differed.
</context>

<claims>

1. THE ITEM'S PREMISE IS PARTLY STALE, AND THAT CHANGES THE FIX.
Item 32 says the detach rule "does NOT live in the skill". It does:
skills/multi-model-verify/references/model-prompting-notes.md:297 opens a
bullet "Dispatch the round DETACHED, and do not let the shell kill it."
Its consequence sentence is already pinned by
evals/multi-model-verify/test_multi_model_verify.py:970. What is NOT pinned
is the instruction clause itself, and skills/multi-model-verify/SKILL.md
contains no detach instruction at all. CLAIM: because the rule already
existed one file away from the command and a round was still lost on
2026-08-30, adding more prose is not a sufficient fix, and the command
itself must change.

2. THE IN-SCOPE SURFACE IS EXACTLY FOUR SHELL DISPATCH SITES.
SKILL.md:186 (codex round 1), SKILL.md:248 (codex resume),
references/backup-lane.md:25 (kimi round 1), references/backup-lane.md:30
(kimi resume). references/panels.md:49-52 routes both panel lanes to those
two files rather than repeating a command, so panels need no separate work.
CLAIM: that enumeration is complete for shell-dispatched long client calls
in this skill.

3. FOUR THINGS ARE OUT OF SCOPE AND EACH REASON IS DIFFERENT.
(a) agents/fable-reviewer.md and agents/fable-panel-reviewer.md are
subagents dispatched through the harness Agent tool, which runs them in the
background by default; references/panels.md:79 calls that lane "a resumed
background agent". The 600-second shell ceiling does not apply.
(b) tools/check-drift.ps1:1054 already uses Start-Job with
Wait-Job -Timeout 900.
(c) commands/doctor.md:70 is a reachability probe pinned to
model_reasoning_effort=low and its own text says it is "not a review".
(d) SKILL.md:325-327 is the attestation emitter, a local script.
CLAIM: none of these four is the same defect, and including any of them
would widen the change without reducing the risk.

4. Start-Job CANNOT BE THE MECHANISM.
The harness PowerShell tool gives each call a fresh shell; its own contract
states working directory persists between calls and shell state does not.
So a job handle from one call does not exist in the next, and waiting
inside the starting call is back under the 600-second ceiling.
check-drift.ps1:1054 can use Start-Job only because it starts and waits
inside one long-lived script. CLAIM: Start-Process with the pid on disk is
the only mechanism that survives the harness's call boundary.

5. THE WRAPPER MUST BE A FILE, NOT AN ARGUMENT LIST.
tools/new-kimi-lane-home.ps1:235-241 records, measured live, that
Start-Process -ArgumentList joins its array with a plain space and does NOT
quote an element containing one. Windows PowerShell 5.1 native argument
splatting also strips embedded double quotes. The dispatch carries a -c
override value and a brief. CLAIM: passing either through -ArgumentList is
unsafe, and a wrapper file has no quoting layer at all.

6. THE ENCODING PREAMBLE MUST MOVE INSIDE THE WRAPPER.
Start-Process starts a new process, which does not inherit the caller's
$OutputEncoding. SKILL.md:178-188 currently sets it at script scope, and
evals/multi-model-verify/test_multi_model_verify.py:609-660 records that a
child-scope assignment was MEASURED not to reach the native pipe. CLAIM:
wrapping the current block without moving the preamble inside would
silently reinstate the fault 0.23.0 fixed, and this is the single most
likely way to get this build wrong.

7. THE EXIT CODE MUST COME FROM A SIDECAR FILE THE WRAPPER WRITES.
tools/check-drift.ps1:902-912 records that PS 5.1's file-redirect
Start-Process never retains a native process handle and $proc.ExitCode
reads null when the child exits before the next statement touches .Handle.
CLAIM: a review round always wins that race, so the exit code must be
written by the wrapper itself rather than read from the handle. Note the
plan deliberately DIFFERS from check-drift's .cmd sidecar: our wrapper is
PowerShell and can write its own code as its last statement.

8. THE SKILL.md BUDGET IS THE BINDING CONSTRAINT AND THE PLAN RAISES IT
DELIBERATELY.
Measured 2026-08-30: SKILL.md body is 20983 chars / 5245 estimated tokens,
against BODY_TOKEN_BUDGET 5250 and BODY_TOKEN_CEILING 5500 in
evals/tools/skill_lint.py:102. That is 20 characters before a warning and
1020 before a gate error. The change needs roughly 1400. skill_lint.py's
own error text names exactly two legitimate remedies, relocation and a
deliberate ceiling raise, and Task 1 uses both. CLAIM: raising
BODY_TOKEN_CEILING to 5900 with the measurement recorded is correct here
and is not a way of dodging the budget.

9. THE EXISTING PINS CONSTRAIN THE WRAPPER BODY AND MUST STAY GREEN
UNAMENDED.
test_multi_model_verify.py:600-650 counts five exact strings at >= 2
occurrences across SKILL.md; test_resume_pipes_the_brief_on_stdin matches
"$brief | codex exec ... resume <SESSION_ID> -" with [^\n]*, so that span
must stay on ONE physical line; and a raw pin forbids a three-space
indented "& {". CLAIM: keeping the wrapper body byte-identical except for
one added line satisfies all of these, and any amendment to those pins is
evidence the body changed more than it should have.

10. ITEM 51 IS NOT TOUCHED, AND THE PROOF IS A PIN THAT STAYS GREEN.
The kimi command strings at references/backup-lane.md:25 and :30 stay
byte-identical, inline -p payload included.
evals/multi-model-verify/test_backup_lane.py:137-148 pins both exactly.
CLAIM: those two assertions passing WITHOUT amendment is sufficient
evidence that the item 51 surface did not move, and a red there means the
change went out of scope.

11. ITEM 33 IS SAFE TO REMOVE THE PROMPT FOR, FOR ONE SPECIFIC REASON.
The review mirror is a FILE COPY preserving .git, and every deletion
happens in the copy; the user's tree is never touched
(tools/new-review-mirror.ps1:1-13). CLAIM: because there is no destructive
act, there is nothing to consent to, and the prompt was buying a round trip
while putting "skip the cross-vendor lane" one tap from the recommended
answer. The CHECK is not removed; only the question is. The plan's Task 6
region keeps the evidence duty, the empty post-mirror re-enumeration, and a
BLOCKED state when the mirror cannot be built.

12. THE PLAN DELIBERATELY LEAVES ONE QUESTION OPEN.
Whether a timeout is documented, and what a session does at it. A stated
"fell the tree at N minutes" reintroduces a caller kill, just later;
omitting it risks polling a hung process forever. CLAIM: leaving the
mechanism (pid, four states, taskkill) without a policy is the right call
for this plan, and the policy belongs to whoever operates it.

</claims>

<boundaries>
Already decided by the user and NOT under debate:
- That the fix changes the COMMAND rather than adding prose. The user chose
  this after being offered prose-only and a shipped wrapper tool.
- That items 32 and 33 are built in one cycle.
- That backlog items 51 and 31 are out of scope for this cycle.
- Repo conventions: tests change before the contract they lock; both
  PowerShell hosts; execution is subagent-driven.
Do not re-litigate these. Do challenge anything that depends on them being
true and is wrong anyway.
</boundaries>

<final-check>
List any claim you could not verify against files you actually read, as
UNVERIFIED, and do not fold unverified material into your verdict.
Then answer two sweep questions explicitly, naming an instance or reporting
none:
(a) Does the plan introduce any NEW way for an unfinished or killed round to
be read as a completed one? That is the one outcome this change may never
produce.
(b) The plan asserts an enumeration is complete (claim 2) and that four
things are out of scope (claim 3). What OTHER shape could a blocking long
client call take in this repo that neither list would catch?
</final-check>
