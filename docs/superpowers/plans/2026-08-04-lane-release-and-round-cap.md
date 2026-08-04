# 0.22.0 - lane release, owner resolution, and the two debate policies

Backlog items 26, 24 and 25. Branch `feat/lane-release-and-round-cap`.

## Global Constraints

- The repo is PUBLIC. Never commit raw recordings; hand-normalized
  synthetic fixtures only.
- Stage by explicit path. Never `git add -A`, never `git add -u`.
- Checkout edits are not live. Bump `.claude-plugin/plugin.json` LAST,
  then `plugin update`, then restart, then verify cache CONTENT.
- Contract text inside `contract:start`/`contract:end` must sit WHOLE
  inside a single pin, in one of the three recognized clause forms.
  Editing a region means regenerating its pin whole and touching
  `DECLARED_REGIONS` if a region is added or removed.
- Tests first for every live-verified contract: they encode review
  findings, so they change before the thing they pin.
- A claim may never be wider than its evidence. An unmade, failed or
  unreadable measurement is never a clean one. A test is not evidence
  until it has been watched to FAIL for the reason it claims.

## Evidence this plan rests on

**Item 26, the stuck lane.** Measured 2026-08-03: two sessions blocked
over three hours. The lock behaved correctly at every step; the debate
never released it. The only documented release is a SIDE EFFECT of
`new-kimi-lane-home.ps1 -Remove`, stated inside the
`lane-lock-call-lifecycle` region rather than at debate end where a
driver would read it.

**Item 26, the owner resolution.** Measured here 2026-08-03:
`-ResolveOwner` returns the DIRECT PARENT of the PowerShell process and
nothing else (`tools/kimi-lane-lock.ps1:741`). On this machine that
parent is the long-lived `claude.exe` and four consecutive calls agreed.
Under a harness that inserts a wrapper, the parent is that intermediate,
which exits when the command does - reported by the KitnEssentials
session, NOT reproduced here. The instability is therefore SOMEONE
ELSE'S measurement and this plan may not claim otherwise.

**Item 24, the round cap.** Three independent runs now:

| run | rounds | contested | outcome |
|---|---|---|---|
| KitnEssentials field report | 8 | 0 | stopping at 4 would have shipped defects 5 and 6 |
| 0.20.0 mode-diff gate | 5 | 0 | converged when the finding count reached 0 |
| 0.21.1 (this repo, 2026-08-04) | 7 | 0 | cap hit at 4; rounds 5, 6 and 7 were confirming, and 5 and 6 each BLOCKED the merge |

The 0.21.1 run is the strongest of the three because both of its
post-cap rounds returned ESCALATE on defects that were real, and one of
those defects (an oracle asserting a word its refusal never prints)
could not have been found any other way.

**Item 25, the scope rule.** The field report's rounds 4 to 7 landed on
defects PREDATING the range. Mid-debate its session declared a policy to
the reviewer and it worked; the reviewer then offered a formulation
worth adopting: a pre-existing defect "can be a separate follow-up
commit, but I would not certify the module before that follow-up lands".

## File Structure

- `skills/multi-model-verify/references/backup-lane.md` - the named
  release step (26a).
- `skills/multi-model-verify/commands/` and `commands/parallax-doctor`
  surface - the quiet-holder INFO row (26b) lives in the doctor skill
  text, wherever check 8 is defined.
- `tools/kimi-lane-lock.ps1` - owner resolution reports a NAME (26c).
- `skills/multi-model-verify/references/debate-protocol.md` - the cap
  (24) and the scope rule (25).
- `evals/multi-model-verify/test_kimi_lane_lock.py` and
  `test_backup_lane.py` - oracles and pins.

## Task 1: a named release step at debate end (item 26a)

`backup-lane.md`'s closing steps must carry "the debate is over, release
the lane" as a STEP, not as a clause inside the lifecycle contract. A
driver reading the debate's close must see it without reading the
contract region.

**Verification.** A pin asserts the step exists in the closing-steps
text, and `test_contract_coverage` stays green.

## Task 2: `-ResolveOwner` reports the resolved process NAME (item 26c)

Add `ownerName` to the `-ResolveOwner` record and to what acquire
stores, so a teardown that cannot match its recorded owner can SAY what
it resolved instead of failing opaquely.

**Direction to settle in the debate, not decided here.** Whether
resolution should REFUSE when the parent is not a recognizable
long-lived harness. Refusing is the safe direction in principle, but a
name allowlist is fragile and a wrong refusal makes the lane
unavailable. The plan's default is: report the name, do NOT refuse on
it, and let the debate argue for more.

**Verification.** Schema oracles for the new field, watched to fail.
Every existing caller of `-ResolveOwner` must keep working: the doctor's
recovery command parses this record with an EXACT two-field schema check
and will refuse a third field, so that command changes in the same task
or the field does not land.

## Task 3: the doctor's recovery command stops re-resolving (item 26c)

The doctor's lane-login recovery command calls `-ResolveOwner` at
recovery time. When the recorded owner came from a wrapper that has
since exited, re-resolving cannot reproduce it, so the command cannot
release what it is trying to release. `-Status` already prints the
complete recorded identity - that is what a release must use.

**This is the half of item 26's severe defect that is fixable WITHOUT
reproducing the instability**, and the plan says so rather than implying
the whole defect is closed.

**Verification.** The doctor's text no longer routes a release through a
fresh resolution; the pin asserts the `-Status`-sourced form.

## Task 4: the quiet-holder INFO row (item 26b)

Check 8 reports a held+LIVE holder whose debate home has had no file
modified for an interval as INFORMATION in the detail text. It must
change NOTHING about reclaim rights and must NOT move the row off OK.
When the home is unreadable or gone, say nothing: an unmeasurable idle
time is not an idle debate.

**Verification.** Doctor text pins for both the informational wording
and the degrade-to-silence rule.

## Task 5: the round cap counts CONTESTED rounds (item 24)

`debate-protocol.md`: the cap counts rounds carrying contested points. A
round whose findings are all ACCEPTED resets it. The debate ends when a
round produces no new accepted finding. The existing "converged with
amendments" rule already points this way and this makes it the counter.

**Verification.** Pins for the new rule; the three-run evidence table
goes in the plan record, not the shipped text.

## Task 6: a scope rule for pre-existing defects (item 25)

Adopt the policy that worked, in `debate-protocol.md`: fix a
pre-existing defect that is the SAME CLASS as what the branch already
fixes AND sits on the surface the verification will exercise; record
anything else for a follow-up branch; and do not certify a module whose
follow-up has not landed.

**Verification.** Pin the rule. This is policy text, so the debate is
where it earns its wording.

## Task 7: ship

Bump LAST, merge, attest, push, update, restart, verify cache CONTENT by
hashing shipped files rather than by reading the version string.

## Known limits this plan will not close

- The `-ResolveOwner` instability is not reproduced here and this branch
  will not claim to have fixed it. Tasks 2 and 3 make it LEGIBLE and
  make release work from the recorded identity; finding a wrapping
  harness remains open.
- Item 28's strict JSON lexer stays open and out of scope.

---

# Amendment 1 (2026-08-04, plan debate round 1) - the plan was not ready to build

Cross-vendor plan debate, session `019fcdd8`, brief binding clean. Claim
4 PASS; claims 1, 2, 3, 5, 6, 7 FIX. Every finding was reproduced here
before acceptance. One task is DELETED, one is added, and the added one
is the strongest thing in this branch.

## The finding that changes the release: acquire never checks its own owner

`Get-Liveness` exists at `tools/kimi-lane-lock.ps1:205` and
`Invoke-AcquireMode` calls it on ONE thing: the EXISTING holder's record,
to decide reclaim rights. It is never called on the PROPOSED owner.
Acquire validates that `-OwnerPid` and `-OwnerStartTicksUtc` are
syntactically well formed and then records them.

So a caller can record an owner that is ALREADY DEAD. The record then
reads DEAD to the next acquire, which reclaims it, and the mutual
exclusion the lock exists to provide is gone while every status read
looks ordinary. That is item 26's severe half, and it is REACHABLE AND
TESTABLE HERE: pass a pid that is not running and assert the refusal. No
wrapping harness required.

The plan said the severe defect could not be closed without reproducing
another session's harness. That was wrong, and this is why a plan debate
happens before the build.

## Task 3 is DELETED - its premise was false

The doctor's `-ResolveOwner` use is the LANE LOGIN recovery command,
printed for an absent, unreadable or malformed credential. It creates a
fresh debate id, acquires with the freshly resolved identity, and
releases the SAME identity in its own `finally`
(`tools/new-kimi-lane-login.ps1:521-574`). A self-contained login-lock
lifecycle, not a teardown of anyone else's lock.

Normal debate release already carries the retained identity:
`new-kimi-lane-home.ps1 -Remove` verifies it, deletes the home, then
calls `-Release` with it, and `-ResolveOwner` never appears on that path
(`tools/new-kimi-lane-home.ps1:357-375, 476-488`).

**Backlog item 26 carries the same misreading** and its text is corrected
when the item closes: "which the doctor's own recovery command does" is
not true of any release path. I reached this independently while the
round was in flight and the reviewer reached it from the other side;
both are recorded, because agreeing after the fact is not the same as
agreeing beforehand.

## Task 1's baseline was stale

`backup-lane.md`'s `lane-home-isolation` region already says "Remove the
home with `-Remove` when the debate ends". The plan's premise that
release exists only as an internal lifecycle side effect is therefore
false. What is TRUE is narrower: the instruction is a clause inside a
contract region rather than a step at the debate's close, and nothing
detects a debate that finished without one.

Task 1 must also admit what it does not do. Pinned prose does not
execute teardown and does not detect its omission, so forgotten release
stays a human-compliance failure mode after this branch.

## Task 2 becomes fail-closed, and the schema change is a migration

Two corrections. First, refusing unknown ancestry IS available without
the harness: walk to a contractually recognized long-lived ancestor and
refuse when none is found. Availability loss is the safe direction next
to recording an owner known only to be an arbitrary wrapper.

Second, my coupling analysis was incomplete in three ways the reviewer
enumerated and I confirmed: the exact two-field validator ORIGINATES in
`new-kimi-lane-home.ps1`'s recovery-command template and the doctor
holds a duplicate; `test_kimi_lane_lock.py` requires exactly those two
keys; and the PERSISTENT record is exact-schema, so a required
`ownerName` would turn every pre-upgrade HELD record MALFORMED after an
update. `ownerName` must therefore be OPTIONAL in held-v1, and acquire
has no `OwnerName` parameter today, so "store it on acquire" was wider
than the code.

## Task 5's termination predicate is logically wrong

"The debate ends when a round produces no new accepted finding" also
ends a round whose only new finding is CONTESTED - the exact case the
cap exists to escalate. And nothing bounds a session that keeps
accepting findings, because the session both adjudicates acceptance and
decides when to stop; that is one actor holding both.

Replacement: keep the four-round CONSECUTIVE-CONTESTED counter, add a
separate caller-configurable total fix-verify budget whose exhaustion
PAUSES for user authorization rather than certifying, and end only on an
adjudicated dry round with no new substantive finding AND no outstanding
contested point.

## Task 6 needs operational definitions

"Same class" becomes violation of the same NAMED invariant, contract
clause or frozen postcondition - not symptom similarity. "Verification
surface" becomes the exact files, symbols, runtime paths and gates
enumerated BEFORE the finding. The certification unit gets named, and an
exercised surface with an outstanding follow-up forces FIX or ESCALATE
with no attestation, or an explicitly narrowed certification claim.

## Task 4's undecided rule

The backlog said a rule for what "quiet" reads from was required and the
plan did not supply one. Interval, measured file universe, timestamp
rule and partial-unreadability behaviour are all decided before
implementation, not during it.

## A limit the reviewer could not check, and it is a real gap

It could not find primary round records for the 0.20.0 `6,5,2,1,0`
sequence or for this repo's own 0.21.1 seven-round account. Both are
assertions in prose. The 0.21.1 debate's replies were never retained
into the repo, so the strongest evidence for item 24 is not citable by
anyone who was not in the session. Retaining them is now a task.

## Revised task list

1. Surface the release step at the debate's close, correct the stale
   baseline, and admit it stays advisory.
2. `-ResolveOwner` reports the resolved process NAME and refuses when no
   recognized long-lived ancestor is found.
3. **Acquire REFUSES a proposed owner that does not measure LIVE.** New,
   testable here, and the closest thing this branch has to closing item
   26's severe half.
4. `ownerName` as an OPTIONAL held-v1 field, with every in-repo consumer
   enumerated and updated: builder template, doctor duplicate, lock
   schema oracle, recovery-command execution tests, both wrapper call
   chains, status output.
5. The quiet-holder INFO row, with its interval, universe, timestamp and
   partial-unreadability rules decided here.
6. The round cap: consecutive-contested counter plus a total fix-verify
   budget that pauses for authorization.
7. The scope rule, with operational definitions.
8. Retain the 0.21.1 debate round records so item 24's evidence is
   primary rather than asserted.
9. Ship.

Deleted: the old Task 3.

---

# Build record - task 3, acquire refuses a DEAD proposed owner (2026-08-04)

Built. `tools/kimi-lane-lock.ps1`, top of `Invoke-AcquireMode`. Four new
oracles in `test_kimi_lane_lock.py`. 90 passed on BOTH hosts.

## The claim shipped is NARROWER than the amendment asked for

Amendment 1 task 3 said "refuses a proposed owner that does not measure
LIVE". That was built first and it was WRONG, and the suite said so
before any review did.

`Get-Liveness` has three outcomes. UNMEASURABLE means the pid lookup
SUCCEEDED and only the start-time read failed, so the process EXISTS and
the thing left unmeasured is the pid-REUSE guard, not existence. The
file already carries one meaning for that state, stated at
`tools/kimi-lane-lock.ps1:195`: every mutating mode treats it as ALIVE
and refuses to reclaim.

Refusing it at acquire contradicted that in the worst direction. Two
shipped fault-seam oracles went red immediately:
`test_unmeasurable_exact_identity_reacquires_idempotently` and
`test_unmeasurable_competing_identity_contends_not_reclaims`. The first
one is the real cost: the TRUE owner could not re-enter its own lock
whenever the start time was unreadable. That is an availability loss
inside a live debate, not a safe direction.

So the shipped rule refuses **DEAD only**, and the claim is "acquire
refuses an owner measured DEAD", never "the recorded owner is live".

**Residual, stated rather than hidden:** a running pid carrying the
WRONG ticks still records if the start-time read fails, because that is
the one measurement that would have caught it. Recorded in the tool and
pinned by `test_acquire_accepts_an_unmeasurable_proposed_owner`.

## Evidence

Every oracle was watched to FAIL for its stated reason before the code
existed:

- `test_acquire_refuses_an_owner_that_is_not_live` - a started-and-reaped
  pid. Failed against the unguarded tool.
- `test_acquire_refuses_an_owner_whose_ticks_do_not_match` - a live pid
  with wrong ticks, the identity-reuse case. Failed the same way.
- `test_acquire_still_accepts_a_live_owner` - positive control. Passed
  throughout, which is what a positive control does.
- `test_acquire_accepts_an_unmeasurable_proposed_owner` - the boundary
  the refusal may not cross. Watched failing against the WIDE rule, then
  green against the narrow one.

The whole module also migrated off a synthetic owner identity. 23 paired
call sites passed `-OwnerPid 1 -OwnerStartTicksUtc 1`, which no
proposed-owner check could ever accept. They now use `LIVE_PID` /
`LIVE_TICKS`, measured from the pytest process itself. That migration
was confirmed a no-op (86 passed) BEFORE the new oracles were added, so
the four new results are not confounded with it.

## What this does NOT close

Item 26's `-ResolveOwner` instability is untouched here; that is task 2.
This closes the silent half only: a dead identity can no longer be
written into the record in the first place.

---

# Build record - task 2, owner resolution walks past its own transports (2026-08-04)

Built. `tools/kimi-lane-lock.ps1` `Invoke-ResolveOwnerMode`, plus every
consumer of the resolved record. Four new oracles in
`test_kimi_lane_lock.py`.

## Item 26's instability is reproducible HERE, and the item said it was not

The item's evidence status reads: "Reproducing the instability needs a
harness that wraps, and finding one is the first step of this item."
That is wrong, and the correction goes into the item when it closes.

One added shell frame reproduces it exactly.
`test_resolve_owner_is_stable_across_an_added_shell_frame` calls
`-ResolveOwner` twice - once as the suite always has, once through one
extra PowerShell host - and against the shipped tool the two calls
returned pid 30944 and pid 4872. Different owner, same machine, same
second. That IS the reported defect: the direct parent under a wrapper
is the shell the wrapper just spawned, a new pid every call, dead by the
next status read.

No wrapping harness was needed. A shell was.

## What changed

Resolution now walks up from `$PID`, SKIPS the hosts this tool is
invoked through (`pwsh.exe`, `powershell.exe`, `cmd.exe`,
`conhost.exe`), and stops at the first ancestor that is not one. It
reports that ancestor's NAME alongside its pid and start ticks.

Measured chain on the shipped path, 2026-08-04:
`pwsh -> claude -> pwsh -> Code -> Code -> explorer`. The direct parent
is already non-transparent there, so the ordinary caller's resolved
owner is UNCHANGED. Only nested invocations move, and they move onto the
answer the un-nested call already gave.

Refusals, all exit 2 with nothing on stdout: the walk reaching the top
of the process tree, exceeding 16 levels, an unreadable process name, an
unreadable start time, or the ancestry read throwing.

## The cost, stated rather than buried

A genuinely long-lived orchestration script running inside one of those
four hosts is skipped, and the owner resolves to ITS parent - a lock
that can outlive the debate instead of one that dies inside it.

That is item 26's VISIBLE half traded against its SILENT half. It is the
direction that fails toward a stuck lane rather than toward two debates
against one credential, which is the trade this repo's lock design
already makes everywhere else. It is also the weakest point in this
task and the reviewer should be pointed straight at it.

The list names TRANSPORTS, not approved owners. Adding a name to it says
"this tool is invoked through that" and nothing more, which is why it
needs no allow-list of session hosts that would rot with every new
install shape.

## The coupling, enumerated and closed

`ownerName` is a THIRD field in a record validated by an EXACT field-set
check, so every copy of that check moved in the same commit or the
recovery path would have thrown `owner resolution returned invalid
schema` on its next real use:

- `tools/new-kimi-lane-home.ps1` - the recovery-command template, where
  the check originates.
- `commands/doctor.md` - the duplicate the doctor prints.
- `evals/multi-model-verify/test_backup_lane.py` - the frozen literal.
- `evals/multi-model-verify/test_kimi_lane_home.py` - the frozen literal
  and the owner-stub set.

The stub set gained three rejection reasons (missing name, non-string
name, blank name) and its EXTRA-field stub was rebuilt on the full
three-field record, because left at two fields it would have quietly
become a second copy of the missing-name case.

## A scoping error of my own, recorded

Task 3 was committed after running `test_kimi_lane_lock.py` only. The
full suite then failed in modules that drive the same tool with
synthetic owner identities. The verification surface for a change to a
shared tool is every module that drives that tool, not the one module
named after it - which is the operational definition task 7 is being
asked to write, failed in the same branch that writes it.

---

# Build record - task 4, ownerName as an optional held-v1 field (2026-08-04)

Built. `ownerName` reaches the persistent record, both wrapper call
chains forward it, and status reports it when it is there. Ten new
oracles across three modules.

## Why OPTIONAL, and why that is the whole design

The held record is an EXACT field set: a property the schema does not
name makes the record MALFORMED, which is exit 4 and a lane nobody can
take without the guarded override.

The lock already carried two lists, `$HeldFields` (admitted) and
`$HeldRequired` (demanded). Adding `ownerName` to the first and not the
second IS the migration. A required field would have turned every record
written before this change MALFORMED the moment the plugin cache
updated - a lane locked by an upgrade rather than by a debate.

Both directions are pinned, because only pinning one of them would let
the other rot:

- `test_a_held_record_carrying_owner_name_is_well_formed`
- `test_a_held_record_without_owner_name_is_still_well_formed`

Optional in PRESENCE is not optional in SHAPE. A record that carries the
field at all must carry something a reader can act on, so a blank or
non-string name is MALFORMED, and a supplied-but-blank `-OwnerName` is a
REFUSED acquire rather than a silent absence. That is the rule `-Nonce`
already follows in the same file.

## Two writers, two chains, and both were live traps

The lock has TWO record writers - the fresh acquire and the RECLAIM of a
dead holder - and a field added to one is a field that vanishes the
first time a lane is reclaimed. Pinned by
`test_reclaiming_a_dead_holder_carries_the_new_owner_name`.

The tools have TWO call chains into acquire - the builder and the login
wrapper - and the login one is what the doctor's own recovery command
drives, so it is the chain most likely to be holding a lane an operator
is trying to understand. Each is pinned from the RECORD rather than from
the wrapper's own output, and each was watched failing with its
forwarding line removed.

Neither wrapper forwards an empty name. Adding the key with an empty
value would turn a nameless call into a REFUSED acquire, which is a
wrapper failing a call the caller made correctly.

## The consumers, enumerated

- `tools/kimi-lane-lock.ps1` - parameter, schema, validation, both
  writers, status output.
- `tools/new-kimi-lane-home.ps1` - parameter and both acquire sites.
- `tools/new-kimi-lane-login.ps1` - parameter and its acquire site.
- The recovery command in all four copies, which now forwards
  `-OwnerName $owner.ownerName` to the login wrapper.
- `test_kimi_lane_lock.py`, `test_kimi_lane_home.py`,
  `test_kimi_lane_login.py`.

## What this does NOT do

Nothing yet passes a name on the shipped debate path: the skill's
lifecycle region still says to keep `ownerPid` and `ownerStartTicksUtc`
and hand those to every later call. That sentence moves with task 1's
edit to the same file, and until it does, the field is available rather
than used.

---

# Build record - tasks 1 and 5, the release step and the quiet-holder row (2026-08-04)

Built together because task 1's text cites task 5's row, and a rule that
cites something not yet built is a claim wider than its evidence.

## Task 1: the baseline really was stale, and the correction is narrower

The plan's premise - that release exists only as an internal lifecycle
side effect - was FALSE. `lane-home-isolation` already says "Remove the
home with `-Remove` when the debate ends".

What is TRUE is narrower, and it is what the new region fixes: the
instruction was a CLAUSE INSIDE a contract region about building the
home, not a STEP a driver reads at the debate's close. New region
`lane-debate-close` in `backup-lane.md`, declared in `DECLARED_REGIONS`
and pinned by `test_lane_debate_close_region`.

It names the three cases most likely to skip it - a debate that ended in
ESCALATE, one the user abandoned mid-round, one whose rounds failed on
transport - because the lock is held identically in all three and none
of them is a reason to keep it.

**The admission is pinned WITH the rule, deliberately.** Pinned prose
does not execute a teardown and nothing detects a debate that finished
without one. A region stating the step without stating its own limit
would be exactly the defect this repo's first invariant names. So the
region says so, in the region, where it cannot be separated from the
instruction it qualifies.

## Task 5: four rules the backlog said had to be decided, decided

The item required a rule for what "quiet" reads from and said it must
degrade to silence. The plan did not supply one. All four are now in
`commands/doctor.md` and pinned:

- **INTERVAL: 30 minutes.** A single review round can legitimately run
  past the ten-minute dispatch ceiling and a debate can sit between
  rounds. A shorter interval reports an ACTIVE debate as quiet, which is
  the failure that makes an operator distrust the row and then ignore
  it.
- **UNIVERSE: files under the recorded `debateHome`, recursive,
  directories excluded.** Directory timestamps move for reasons that are
  not debate activity, and the per-round session evidence this lane
  writes is files.
- **TIMESTAMP: the NEWEST `LastWriteTimeUtc`.** One number, compared
  against now.
- **PARTIAL UNREADABILITY: say nothing at all.** Missing home, not a
  directory, no files, or ANY read failure anywhere in the walk, and the
  doctor reports neither quiet nor active. A partial walk measures the
  files it could open, not the debate.

**The constraint that keeps it information.** The row stays OK, no
reclaim rule moves, and nothing in the lock tool reads it. A predecessor
expired holders by AGE and that let anyone break a live round; an idle
reading that moved a verdict would be that expiry under another name.
`test_doctor_quiet_row_never_becomes_an_expiry` pins that sentence.

## The pins were mutation-tested, not merely written

Prose pins are easy to write and easy to write uselessly. Both were
checked by MUTATING the doctor text rather than deleting it:

- `more than 30 MINUTES` -> `more than 10 MINUTES`: the interval pin
  failed. The number is pinned, not the paragraph.
- `if ANY part of the walk fails to read` -> `if the walk fails to
  read`: the silence pin failed. The word that makes a partial failure
  count is pinned, which is the whole rule.

## Task 4's loose end, closed here

The lifecycle region now says to keep `ownerName` from resolution and
pass `-OwnerName <name>` to both the build and the login, and states
that it is optional everywhere and never part of the identity a release
must match. Until this edit the field was available but nothing on the
shipped path passed one.

---

# Build record - tasks 6, 7 and 8 (2026-08-04)

Both rules land in `references/debate-protocol.md`, which SKILL.md names
as REQUIRED READING before the first round and routes iteration through.
Nothing was added to SKILL.md, which is already over its token budget
(5404 against ~5000) as backlog item 19 records.

## Task 6: the cap counts the thing it was named for

The old cap counted EXCHANGES. That fits a contested debate and not a
fix-verify loop, where every round finds something new, the session
verifies and accepts it, and nothing is argued.

- The cap is now **4 CONSECUTIVE CONTESTED exchanges**. A contested
  round increments it; a round whose findings are all accepted RESETS it
  to zero.
- A **total fix-verify budget**, caller-set and declared before round 1,
  bounds the other regime. Exhausting it PAUSES for the user's
  authorization. It never certifies and never converts into a verdict,
  because the session both adjudicates acceptance and decides when to
  stop - one actor holding both roles - and a budget the USER controls
  is the bound a session cannot grant itself.
- Termination requires an **adjudicated dry round**: no new substantive
  finding AND no outstanding contested point. The plan's own predicate
  ("ends when a round produces no new accepted finding") was logically
  wrong: it also ends a round whose only new finding is CONTESTED, which
  is the exact case the cap exists to escalate. The text says why, so
  the shorter version cannot return as a simplification.

Both overrun runs are named in the shipped text - the field report's 8
rounds and this repo's own 0.21.1 seven - so the rule cannot be rewritten
without confronting the measurements that produced it.

## Task 7: the scope rule, with definitions that decide cases

The improvised rule worked and was two judgement calls. Two reviewers
who define them differently produce two different attestations, and an
attestation that means something different run to run means nothing.

- **SAME CLASS** is a violation of the same NAMED invariant, contract
  clause or frozen postcondition, cited by name. Not similar symptoms,
  not the same file, not the same subsystem.
- **VERIFICATION SURFACE** is the exact files, symbols, runtime paths
  and gates enumerated BEFORE the finding is raised. Enumerated after,
  it is a surface drawn around the answer someone already wanted.
- **The certification unit** is named before the debate ends rather than
  inferred from what was touched.
- **An exercised surface with an outstanding follow-up cannot be
  attested**: FIX, ESCALATE, or an explicitly narrowed claim naming what
  is excluded.

## The pins are mutation-tested, all five

Prose pins are easy to write and easy to write uselessly, so each was
checked by CHANGING the text rather than deleting it. Every mutation
failed its own pin and nothing else:

| Mutation | Pin that failed |
| --- | --- |
| `RESETS it to zero` -> `keeps it as it was` | contested-round counter |
| `Exhausting it PAUSES` -> `Exhausting it ENDS` | fix-verify budget |
| `ENUMERATED BEFORE` -> `enumerated when` | verification surface |
| `finding AND left no` -> `finding OR left no` | adjudicated dry round |
| `cannot be attested` -> `should not be attested` | outstanding follow-up |

## Task 8: the evidence is primary now

`docs/superpowers/plans/rounds/2026-08-04-transport-and-mirror/` holds
all seven plan-debate replies with their briefs and all five diff-debate
replies, verbatim, with a README indexing each round by the verdict line
the reply itself carries.

The README also states what they do NOT establish. No round record
carries a contested-point count, so "seven rounds, zero contested" is
still a reconstruction rather than a reading, and the 0.20.0 `6,5,2,1,0`
sequence is not retained anywhere and stays an assertion. The reviewer
raised both as a gap; only one of them is closed.

---

# Fable whole-branch review, `02adc87..HEAD` (2026-08-04)

Verdict: **ready to merge WITH FIXES**. No Critical. No Important. Five
Minor. Every finding was reproduced here against the source before it
was accepted; none was taken on the reviewer's authority.

## Two were fixed because of WHERE they sit

Both land in the exact policy text this branch exists to make
unambiguous, which is the one place an ambiguity cannot ride.

**F1 - "carrying" was undefined.** `debate-protocol.md:54` said a round
"carrying a CONTESTED point increments the counter". A point contested
in round N and still outstanding while round N+1's new findings are all
accepted read BOTH ways. Under the not-carrying reading the counter
RESETS while the outstanding point still blocks termination, so neither
the cap nor the dry-round rule could end the debate and only the
fix-verify budget - built for the other regime entirely - would bound
it. Settled explicitly: a round is CONTESTED while any contested point
is OUTSTANDING, raised that round or earlier, and a round that merely
accepts other findings does not settle it.

**F2 - a claim one word wider than this branch's own evidence.** The
shipped text said the 0.21.1 debate ran "with zero contested points",
while the rounds README this same branch wrote says no round record
carries a contested-point count. The text now says what the records
support: rounds 5 and 6 each returned ESCALATE, only round 7 was
terminal, and the absence of contested points is a reconstruction from
the claims rather than a reading off the records.

The corrected pin was re-mutation-tested: `whether it was raised` ->
`when it was raised` fails it.

## One was NAMED rather than fixed, on purpose

**F3 - no creation-time ordering guard in the ancestry walk.** Real. A
pid that exits and is REUSED inside the walk's own window resolves a
wrong live owner. A merely dead ancestor already fails closed, so only
reuse during the walk slips through, and it lands on the stuck-lane
direction this function already trades toward.

The standard guard is one comparison. It was NOT added, because no test
in this repo can watch it fail for the reason it claims - reproducing
pid reuse inside a specific microsecond window is not something a suite
can arrange - and adding unverified code to the one function this branch
exists to make trustworthy is the wrong trade. The residual is named in
the code and filed as backlog item 29, which is exactly what task 7's
own scope rule prescribes for a defect the verification surface cannot
reach.

## Two were fixture fragility, both fixed

**F4** - `run_lock_through_an_extra_shell` spliced the host path
unquoted. It passes today only because `PARALLAX_PS_HOST` is normally a
bare name and the powershell fallback lives under System32 with no
spaces; the `shutil.which("pwsh")` fallback is under Program Files, and
an unquoted splice there fails the INNER parse - which would fail this
oracle for a transport reason while looking exactly like the resolution
defect it exists to catch.

**F5** - the login stub absorbed the new `-OwnerName` argument into
`$args` because it is a simple script. Functioning, invisible, and one
added `[CmdletBinding()]` would have flipped the invoked rows to
"binding refused" for a reason nobody would look for. The parameter is
now declared.

## What the review CONFIRMED, and it was asked to attack these

- The proposed-owner liveness check running BEFORE the lock file is read
  is correct: it is parameter validation, matching every other exit-2
  path in the tool, nothing mutates either way, and `-Status` remains
  the malformed-diagnosis surface. The masking is diagnostic ordering,
  not a lost measurement.
- The task 2 trade is defensible as shipped, the transport list names
  transports rather than approved owners, and 16 levels against a
  measured depth of 6 is generous with a fail-closed overflow.
- The synthetic-identity migration did not weaken any oracle. The lock
  module's `write_held` plantings stay valid because a record whose
  owner died after acquire is a reachable state; the home module's
  reclaim fixture correctly moved to spawn-and-kill because it drives
  the real acquire path the tool now guards.
- The mutation tests picked load-bearing words rather than convenient
  ones.

---

# Amendment 2 (2026-08-04, diff debate round 1) - a deviation I did not record, and a window I did not see

Cross-vendor diff debate, session `019fce61`, brief binding CLEAN. Claim
7 PASS; claims 1, 2, 3, 4, 5, 6 and 8 FIX. Every finding was reproduced
here before acceptance.

## The severe one: liveness was measured once, and the write happens later

Task 3 shipped a check at the TOP of `Invoke-AcquireMode`, before the
acquisition loop. A caller that WAITS behind a holder is therefore
measured LIVE, waits, may DIE, and is still written the moment the
holder releases. That is the already-dead record item 26 calls the
silent half, reached by a different road, and the branch's own build
record claimed it was closed.

Fixed as the reviewer proposed and better than the plan asked: the gate
stays a fast DEAD-only refusal, and `Assert-OwnerLiveForWrite` runs
IMMEDIATELY BEFORE EVERY RECORD WRITE requiring LIVE. (Round 3: "every
record write" is too wide and is corrected to every HELD-OWNER write
throughout - the free-record writes carry no owner. See Amendment 4.) UNMEASURABLE now
survives only where NOTHING is written - the idempotent re-entry path,
where a matching nonce and a matching retained identity already
establish ownership without a measurement. The case the DEAD-only rule
was protecting is protected, and the residual it carried is GONE rather
than restated.

`test_an_owner_that_dies_during_contention_is_never_written` reproduces
the window. Watched failing before the fix. NOTE, added by round 2: this
paragraph originally called the fixture synchronized and said the write
"provably" follows the death. It slept two seconds. See Amendment 3.

**The fix carried its own defect, and this branch's own new oracle
caught it.** Refusing at the fresh-acquire write site left a ZERO-LENGTH
lock file when that call had just created it - and a zero-length file is
MALFORMED by rule, so a refusal would have turned a free lane into one
needing the guarded override. The same obligation the nonce-against-free
refusal already carries. Fifth instance in this repo's history of a fix
carrying its own defect.

## The deviation: task 2 is not the shape Amendment 1 froze

Amendment 1 said `-ResolveOwner` should "walk to a recognized long-lived
ancestor and REFUSE when none is found". What shipped is the opposite
shape: a DENY-list of four transports, accepting whatever sits above
them. I made that choice deliberately during the build, for reasons that
are still good - an allow-list of session-host names cannot be validated
against install shapes nobody here has seen, and it would refuse this
repo's own harness, which runs under `python.exe` - but I did not record
it as a deviation, and an unrecorded deviation from a frozen plan is
drift whatever its merit.

The consequence is real and was overclaimed. An EPHEMERAL wrapper named
`node.exe`, `python.exe` or anything outside the four transport names is
still accepted as the owner. The stability oracle inserts another copy
of the SAME PowerShell host, so what it establishes is stability across
an added SHELL FRAME, not "under any wrapper".

**Disposition, decided by the user 2026-08-04:** amend the task, narrow
every claim to what the oracle establishes, and keep item 26 PARTIALLY
CLOSED with the remaining wrapper class named at its own heading. The
alternative - build the allow-list now - closes the item fully and buys
a refusal path nobody here can validate.

## The rest

- **Claim 3.** The non-name schema stubs omitted `ownerName`, so every
  one of them could pass through the missing-name rejection even with
  its intended validation deleted. All SEVEN now carry a valid name and
  exactly one defect. (Round 2 corrected this count from six: the
  extra-field stub is a seventh non-name fixture and was rebuilt
  earlier in the branch.) Measured rather than asserted: removing the
  `-le 0` clause fails EXACTLY `pid_zero` and `pid_negative`; removing
  the digits clause fails EXACTLY `ticks_non_digit`. The template's own
  comment still described a two-field record and now describes three.
- **Claim 4.** The quiet-holder walk did not say what to do with reparse
  points, so two implementations could measure different file universes
  while both following the rule. They are now NEVER followed, and one
  encountered under the home makes the measurement INCOMPLETE, which
  takes the silence rule.
- **Claim 5.** "Converged with amendments" and the new termination rule
  contradicted each other, and the suite pinned BOTH, so green tests
  preserved the contradiction instead of detecting it. This entry
  originally claimed a new pin covered the clarification. IT DID NOT:
  the script that would have added it exited on an earlier failure
  before writing, and only the budget pin was rewritten. Round 2 caught
  the false claim; the pin exists now. Convergence is
  now explicitly AGREEMENT, not termination: the amendments are applied
  and the debate still ends on an adjudicated dry round. The budget's
  unit was undefined; one unit is now one DISPATCHED EXCHANGE, whatever
  it returns, because counting only productive rounds lets the
  unproductive ones run free.
- **Claim 6.** The rounds README said round 1 was "FIX, eight findings".
  The reply's own first line says "claims 2 and 5 pass; claims 1, 3, 4,
  6, 7, and 8 need fixes" - eight CLAIMS, six fixes. Corrected. A
  retained record's index misreading the record is the one error that
  makes retention worthless.
- **Claim 8.** The backlog's top-level status summary still called 24,
  25 and 26 open and omitted 28 and 29 while their own headings said
  otherwise.

## What the reviewer got right that no earlier pass did

Fable reviewed this same branch and returned no Critical and no
Important. The contention window in claim 1 is a genuine
mutual-exclusion defect in the task built to close mutual-exclusion
defects, and it survived my build, my own gates and a whole-branch
review before a second vendor read it. That is the case for the
cross-vendor gate, made again.

---

# Amendment 3 (2026-08-04, diff debate round 2) - the confirming round found six more

Session `019fce61` resumed, brief binding CLEAN, head judged
`ad61503e5814819f4616e2f26ed9b1b72f787606`. Claims 6 and 7 PASS; claims
1, 2, 3, 4, 5 and 8 FIX. Every finding reproduced here before
acceptance. A confirming round again blocked the merge, for the third
consecutive release.

## The one that matters most: my new oracle was not synchronized

Amendment 2 called
`test_an_owner_that_dies_during_contention_is_never_written`
"synchronized rather than timed" and said the write attempt "provably"
follows the death. BOTH WERE FALSE. The fixture slept two seconds and
then killed the victim.

The consequence is exactly the failure this repo's third invariant
exists to prevent. If the victim died before the waiter reached its
PRE-LOOP measurement, the DEAD gate refused, and every assertion still
passed - the test went green for a gate it was not testing, while
appearing to prove the write-site rule.

It now waits for the tool's own `"holder"` contention signal, which
establishes that the waiter is PAST the gate and inside the acquisition
loop before the victim dies. Re-verified by discrimination: removing the
fresh-acquire write-site guard fails it.

I wrote "synchronized" in a record about a test that slept. The reviewer
read the test.

## A pin I claimed existed and did not

Amendment 2 said a new pin covered the convergence clarification. It did
not. The script that would have added it exited on an earlier failure
BEFORE writing, and only the budget pin was rewritten. The pre-existing
neighbour checks that the phrase "converged with amendments" appears,
which stays green with the entire clarification deleted.

The reviewer found it by reading the assertion rather than the record.
The pin exists now and was mutation-tested.

## The contract still claimed more than the tool does

`lane-lock-call-lifecycle` still said "the owner IS the harness session
process" and then sent callers to `-ResolveOwner`. After Amendment 2
narrowed everything else, this was the last surface asserting what the
implementation had just been admitted not to do - and the stale sentence
was PINNED, so the suite was holding it in place.

Rewritten: the owner SHOULD be the session process, `-ResolveOwner`
APPROXIMATES that and does not guarantee it, it returns the first
ancestor outside four named transports, and under a wrapper named
anything else it returns THAT WRAPPER. A caller that knows its own
session process should pass that identity instead of resolving one.

## Three smaller corrections

- **"Every record write" overclaimed.** Free-record writes carry no
  owner and legitimately do not call the helper. The guarantee is now
  stated as every HELD-OWNER write.
- **The check-to-write race is now admitted.** The helper establishes
  LIVE BEFORE the write, not AT it: nonce generation, record
  construction and serialization run in between. Microseconds against
  the seconds-long window the pre-loop-only check left open, and closing
  it entirely would need an atomicity this tool cannot have, since the
  process being measured is not the process writing. Named in the code.
- **Seven, not six.** The non-name schema fixtures number seven; the
  extra-field stub is the seventh and was rebuilt earlier in the branch.
- **"Measures a directory" was false for the file-link case.** Following
  a file link measures a filesystem object outside the debate home, not
  a directory. The prose and its pin both carried the false statement.

## What this round says about the process

Fable returned no Critical and no Important on this branch. Round 1 then
found a mutual-exclusion defect in the task built to close
mutual-exclusion defects. Round 2 found that the oracle written to prove
round 1's fix did not prove it, and that a record claimed a pin that did
not exist.

Every one of those is a claim wider than its evidence, written by me,
surviving my own gates. Three of the last three releases have had a
confirming round block the merge.

---

# Amendment 4 (2026-08-04, diff debate round 3) - three surviving surfaces

Session `019fce61` resumed, brief binding CLEAN, head judged
`6565ca0d2cbcd81cc982eb9c6b51b221980ac662`. Claims 3, 4, 5, 6 and 7
PASS; claims 1, 2 and 8 FIX. Third consecutive round to find something
real; none of it contested.

## A narrowed claim that was narrowed in only one of three places

Amendment 3 said the guarantee "is now" stated as every HELD-OWNER
write. It was, at the helper's own definition - and the GATE comment
twelve lines away still said "before every record write and requires
LIVE", and Amendment 2 still said "IMMEDIATELY BEFORE EVERY RECORD
WRITE". So the operative source contradicted itself, and a narrowing
that lands on one surface out of three is not a narrowing.

All three now agree. Amendment 2's sentence is corrected in place with a
pointer here, not rewritten.

## "Microseconds" was a number I did not measure

The check-to-write residual was described as "microseconds against the
seconds-long window the pre-loop-only check left open". The comparison
is sound; the magnitude is not a measurement. The scheduler can pause
the process anywhere between the check and the write, so wall-clock
duration is not bounded by the number of intervening statements.

Now stated as what is actually known, and ROUND 4 had to narrow it a
second time. "A far narrower window" is itself a comparative magnitude,
and it is not supported: a successful acquisition need not wait the
whole budget, and the scheduler pause the same sentence admits means the
new interval is not PROVEN shorter in wall clock. What is established is
CONTROL-FLOW PLACEMENT - the old interval began before the acquisition
loop and could include contention waiting up to the entire budget; this
one begins after the loop commits to a write and contains only nonce
generation, record construction and serialization. Neither duration is
measured and no comparison is claimed.

Same defect class as the two the confirming rounds already found, twice
in the same sentence: a claim wider than its evidence, in the sentence
that exists to state a limit.

## A failing oracle could leak a two-minute process

`test_an_owner_that_dies_during_contention_is_never_written` kills the
victim only on the success path. If the contention signal timed out or
the branch assertion failed, execution never reached the kill, and the
`finally` terminated only the waiter - so a 120-second sleeper outlived
the failing oracle. The victim is now reaped in `finally` too.

Worth noting where this came from: the fixture was rewritten in round 2
to fix a synchronization defect, and the rewrite introduced this one.
Sixth instance in this repo of a fix carrying its own defect.

## The exception the next sentence took back

The lifecycle contract gained "a caller that KNOWS its own session
process should pass that identity instead of resolving one" and then
continued "So run `-ResolveOwner` once at the start of the debate" -
an unconditional instruction immediately after the exception to it. Now
"OTHERWISE, run". The whole-region pin moved with it.

## What passed

Claims 3, 4, 5, 6 and 7 all PASS, including the convergence pin that did
not exist a round ago and the reason-sensitive schema fixtures. The
reviewer also settled a question I had left open: the phrase-only
convergence test may stay, because it no longer bears the semantic
burden and Amendment 3 names its limitation.
