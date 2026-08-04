The plan is not ready to build. Claims 2 and 3 rest on a misidentified release path, while claims 1, 5, and 6 leave safety or termination decisions unresolved.

### 1. Task 2 and Task 3 are the right split

**Design finding.** The severe mutual-exclusion hole remains open by deliberate policy. `-ResolveOwner` returns only PowerShell’s immediate parent, with no ancestor selection or suitability check; the plan then explicitly chooses not to refuse an unrecognized parent because refusal could make the lane unavailable. [tools/kimi-lane-lock.ps1:741-750](/C:/Users/Brandon/Documents/parallax/tools/kimi-lane-lock.ps1:741) [plan:82-99](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:82)

A fail-closed fix is available without reproducing the KitnEssentials harness: walk to a contractually recognized long-lived ancestor and refuse when none exists, exactly as the backlog already proposes. Availability loss is safer than recording an owner known only to be an arbitrary wrapper. [backlog:1606-1612](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:1606)

There is also an independent missing guard: acquire validates only the supplied PID/tick syntax and then records it without checking that the proposed owner is LIVE, even though the tool already has a three-state liveness function. [tools/kimi-lane-lock.ps1:205-223](/C:/Users/Brandon/Documents/parallax/tools/kimi-lane-lock.ps1:205) [tools/kimi-lane-lock.ps1:472-480](/C:/Users/Brandon/Documents/parallax/tools/kimi-lane-lock.ps1:472) [tools/kimi-lane-lock.ps1:525-555](/C:/Users/Brandon/Documents/parallax/tools/kimi-lane-lock.ps1:525)

**FIX — replace Task 3 as described below; make Task 2 fail closed by resolving a recognized ancestor and refusing unknown ancestry, and make acquire refuse a proposed owner unless its PID/ticks currently measure LIVE. Add a controlled wrapper/expired-owner oracle and watch it fail before implementation, as the plan’s own evidence rule requires.** [plan:16-20](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:16)

### 2. Task 3 identifies an independently reachable defect

**Design finding: refuted.** The doctor’s command is explicitly a **lane-login recovery command** printed for absent, unreadable, or malformed credentials. It resolves an owner and invokes `new-kimi-lane-login.ps1`; it does not attempt to release the recorded debate lock. [commands/doctor.md:171-192](/C:/Users/Brandon/Documents/parallax/commands/doctor.md:171)

The login wrapper creates a fresh debate ID, acquires using that fresh identity, and releases the same identity in its `finally`. That is a self-contained login-lock lifecycle, not teardown of the previous debate. [tools/new-kimi-lane-login.ps1:521-539](/C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-login.ps1:521) [tools/new-kimi-lane-login.ps1:541-574](/C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-login.ps1:541)

Normal debate release already uses the retained original PID, ticks, debate ID, and nonce: `new-kimi-lane-home.ps1 -Remove` first verifies that identity, deletes the debate home, and then invokes `-Release` with it. No `-ResolveOwner` occurs on that path. [tools/new-kimi-lane-home.ps1:357-375](/C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-home.ps1:357) [tools/new-kimi-lane-home.ps1:476-488](/C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-home.ps1:476)

The second half of the claim does stand: `-Status` emits every force-release identity field, and the doctor sources its guarded force command from those fields. That fact does not make the login command a release path. [tools/kimi-lane-lock.ps1:724-737](/C:/Users/Brandon/Documents/parallax/tools/kimi-lane-lock.ps1:724) [commands/doctor.md:238-249](/C:/Users/Brandon/Documents/parallax/commands/doctor.md:238)

**FIX — delete Task 3. If a status-sourced recovery command for an already-stuck debate is wanted, design it explicitly as guarded `-ForceRelease`; do not rewrite the credential-login command as though it were normal teardown.**

### 3. Task 2’s field addition is safe for every caller

**Implementation finding.** The stated doctor coupling is incomplete. The exact two-field validator originates in the shipped builder’s recovery-command template, which requires exactly `ownerPid` and `ownerStartTicksUtc`; the doctor contains a duplicate of that command. [tools/new-kimi-lane-home.ps1:151-173](/C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-home.ps1:151) [commands/doctor.md:186-193](/C:/Users/Brandon/Documents/parallax/commands/doctor.md:186)

The executable oracle also requires exactly those two keys, while the live-support helper merely requires their presence and therefore tolerates an added field. [evals/multi-model-verify/test_kimi_lane_lock.py:165-171](/C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_kimi_lane_lock.py:165) [evals/tools/lane_credential_live_support.py:162-180](/C:/Users/Brandon/Documents/parallax/evals/tools/lane_credential_live_support.py:162)

“Store it on acquire” is wider still: acquire has no `OwnerName` parameter, and both builder and login wrapper currently pass only PID and ticks. [tools/kimi-lane-lock.ps1:78-91](/C:/Users/Brandon/Documents/parallax/tools/kimi-lane-lock.ps1:78) [tools/new-kimi-lane-home.ps1:563-571](/C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-home.ps1:563) [tools/new-kimi-lane-login.ps1:527-535](/C:/Users/Brandon/Documents/parallax/tools/new-kimi-lane-login.ps1:527)

The persistent record is exact-schema: unknown held fields are malformed. Unless compatibility is specified, adding `ownerName` as required would turn a pre-upgrade held record into MALFORMED after update. [tools/kimi-lane-lock.ps1:125-132](/C:/Users/Brandon/Documents/parallax/tools/kimi-lane-lock.ps1:125) [tools/kimi-lane-lock.ps1:314-320](/C:/Users/Brandon/Documents/parallax/tools/kimi-lane-lock.ps1:314) [skills/multi-model-verify/references/backup-lane.md:86-103](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/backup-lane.md:86)

**FIX — enumerate and update the builder template, doctor copy, lock schema oracle, recovery-command execution tests, both wrapper call chains, and status output. Define `ownerName` as optional in existing held-v1 records or introduce an opt-in/versioned resolver output so old records and exact-schema callers remain valid. Narrow “every caller” to “every in-repo caller.”**

### 4. The quiet-holder row cannot become age-based expiry

The separation currently holds. The lock tool decides staleness only from PID/start-time liveness and has no age or debate-home-mtime input. [tools/kimi-lane-lock.ps1:13-21](/C:/Users/Brandon/Documents/parallax/tools/kimi-lane-lock.ps1:13) [tools/kimi-lane-lock.ps1:724-737](/C:/Users/Brandon/Documents/parallax/tools/kimi-lane-lock.ps1:724)

The doctor is report-only, keeps LIVE at OK, explicitly says LIVE never means abandoned, and exposes reclaim actions only for DEAD, foreign-host, or malformed states. [commands/doctor.md:5-9](/C:/Users/Brandon/Documents/parallax/commands/doctor.md:5) [commands/doctor.md:222-244](/C:/Users/Brandon/Documents/parallax/commands/doctor.md:222) Task 4 preserves those boundaries and suppresses the observation when the home cannot be measured. [plan:116-125](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:116)

**PASS**

### 5. Task 5 is supported and removes no protection

**Policy finding.** The evidence supports distinguishing contested debate from fix-verify convergence: the field report records eight rounds, no contested findings, and defects that would have survived a four-round stop. [field report:190-212](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/parallax-field-report-2026-08-03.md:190)

It does not support removing every total-round protection. Under the proposed rule, every accepted finding resets the only counter, while the session is also the actor that adjudicates acceptance and has final say. Nothing bounds a session that continues accepting findings. [plan:127-135](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:127) [skills/multi-model-verify/references/debate-protocol.md:63-92](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/debate-protocol.md:63)

The proposed termination predicate is also wrong for mixed regimes: a round with a new contested or refuted finding may contain “no new accepted finding,” yet contested points are supposed to continue to their cap or go to the user. [plan:129-132](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:129) [skills/multi-model-verify/references/debate-protocol.md:53-58](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/debate-protocol.md:53)

**FIX — use two controls: retain the four-round consecutive-contested counter, and add a separate caller-configurable total fix-verify budget whose exhaustion pauses for user authorization rather than certifying. End only on an adjudicated dry round with no new substantive finding and no outstanding contested point—not merely “no new accepted finding.”**

### 6. Task 6’s scope rule is decidable by an independent reviewer

**Policy finding.** The rule is not presently deterministic. “Same class,” “surface,” and “module” receive no operational definitions; the only evidence is that one session improvised the wording and one reviewer accepted it. [plan:137-146](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:137) [field report:216-237](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/rounds/parallax-field-report-2026-08-03.md:216)

Two reviewers are therefore not forced to converge: one can classify by root cause, another by violated invariant, and either can expand “surface” from a named smoke path to every adjacent function it traverses. The existing checkpoint already supplies machinery for making this exact: named file paths, intended postconditions, named gates, and mandatory amendment on scope growth. [skills/multi-model-verify/references/application-checkpoint.md:30-43](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/application-checkpoint.md:30) [skills/multi-model-verify/references/application-checkpoint.md:50-61](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/application-checkpoint.md:50)

**FIX — define “same class” as violation of the same named invariant, contract clause, or frozen postcondition—not symptom similarity. Define “verification surface” as the exact files/symbols/runtime paths and gates enumerated before the finding. Define the certification unit and require FIX/ESCALATE with no attestation when an exercised surface has an outstanding follow-up; otherwise narrow the recorded certification claim explicitly.**

### 7. The stated limits are complete

**Plan-grounding finding.** They are incomplete. The shipped backup-lane text already says, outside the lifecycle region, “Remove the home with `-Remove` when the debate ends.” That directly contradicts the plan’s baseline that release exists only as an internal lifecycle side effect. [skills/multi-model-verify/references/backup-lane.md:47-73](/C:/Users/Brandon/Documents/parallax/skills/multi-model-verify/references/backup-lane.md:47) [plan:24-29](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:24)

Task 1 still adds only pinned prose; it does not mechanically execute teardown or detect its omission. Therefore forgotten release remains a human-compliance failure mode, but the known-limits section admits only owner-resolution instability and item 28. [plan:72-80](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:72) [plan:153-159](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:153)

Task 4 has another unmade decision: neither the interval nor the file universe/mtime rule is specified, even though the backlog explicitly says a rule for what “quiet” reads is required. [plan:118-125](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:118) [backlog:1573-1575](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:1573)

**FIX — correct Task 1’s stale baseline and admit that release remains advisory unless a mechanical finish-line action/detection mechanism is added. Specify Task 4’s interval, measured file universe, timestamp rule, and partial-unreadability behavior before implementation.**

### UNVERIFIED

- The KitnEssentials per-call PID instability remains another session’s measurement; this checkout establishes only direct-parent resolution. [plan:31-38](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:31)
- I found the primary eight-round field report, but not primary round records substantiating the stated 0.20.0 `6,5,2,1,0` sequence or the plan’s 0.21.1 seven-round/ESCALATE account. Those remain assertions in the backlog and current plan. [backlog:1481-1484](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:1481) [plan:40-51](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:40)
- External third-party consumers of the public `-ResolveOwner` JSON schema cannot be enumerated from this repository; only in-repo consumers were verified. The plan’s universal caller claim is therefore wider than available evidence. [plan:7-8](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:7) [plan:95-99](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-04-lane-release-and-round-cap.md:95)