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
