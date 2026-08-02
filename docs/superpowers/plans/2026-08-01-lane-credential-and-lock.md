# Lane Credential Ownership and Concurrency Lock Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Status: FROZEN at revision 35.** The user lifted the round cap and directed that this plan iterate until the cross-vendor reviewer issued an actual PASS rather than stopping at "converged with amendments". It reached one three times before building and was reopened twice, both times by a required whole-artifact fable review reading the frozen text start to finish. Round 28 was the PASS on the then-ten tasks and on the implementer packet: "PASS. A zero-judgment implementer can build this plan from the defined task packet without inventing behavior."

**That was not the end, and the record should not read as if it were.** Building reopened this plan EIGHT more times, at rounds 29 through 36, and added an ELEVENTH task. The reviewer's round-28 judgment was that the late findings were local expression failures rather than unresolved choices in the state machines — a static judgment about the text, explicitly not a prediction that implementation would reveal no bugs. Implementation revealed plenty: a recovery command that was fail-open at its parse boundary, four caller defects, a test written around a defect, a security ordering that could print a token, a fixture routing rule that could have expired the user's own credential, an oracle that could never fail, a pin that could never be stable, a guard that fired on non-secret metadata, and nine surviving instances of one defect class that three human sweeps had missed. Every one of those was found AFTER the terminal PASS, and most were found by running the case rather than by reading it. The last two reopenings found defects in a REPAIR rather than in the feature: a replacement gate that was described instead of written, and then two of its three stated load-bearing details having no failing oracle while a third was not load-bearing at all. Changes now require reopening the debate with a new round appended to the record; the implementer never edits this plan.

**Goal:** Stop the backup lane from copying the user's kimi-code credential. Give the lane its own login, reach it through a junction so one file holds it, guard the shared lane home with a liveness-anchored lock, stop the doctor touching credentials at all, and repair the Windows CI job this branch already broke.

**Architecture:** A persistent LANE HOME holds one credential produced by its own login. Each debate still gets a throwaway `KIMI_CODE_HOME`, but its `credentials` directory is a JUNCTION to the lane home's, so a refresh writes through to the single file instead of forking a copy. A persistent lock file in the lane home serializes access; every state transition is written in place under one exclusive handle, and the file is never unlinked. Staleness is decided by process liveness only, never by a clock.

**Tech Stack:** PowerShell 5.1 and 7 (both hosts, both gated), Python 3.12 + pytest, Markdown contract regions with the `contract:start`/`contract:end` checker.

## Revision history

**A notation warning, because this document uses `r<N>` in two senses.** Here
and in the status line, `r<N>` is a REVISION of this plan, and revision N was
frozen after debate ROUND N+1. Inside the task text, several "frozen at r<N>"
labels use the ROUND number instead. The two are off by one wherever they meet.
The labels are not being renumbered in this round, because moving them would
change frozen contract text that pins reference; they are recorded as a known
inconsistency rather than silently left to be discovered.

- **r35** — after Sol round 36. The r34 guard prose claimed three load-bearing
  details and could only prove one. TWO had no failing oracle: swapping
  `-cmatch` for `-match` passed every mutation because none supplied a
  lowercase-only message, and deleting the second `git log` exit check passed
  them because the invalid-range mutation never reaches that call. Both now have
  one, driven by a disposable `git` shim. The third claim was simply FALSE:
  `$ids = @($ids)` is defensive normalization, not load-bearing, because
  `foreach` already handles `$null`, a scalar and an array. Writing the mutation
  also reversed the operator: `-cmatch` is fail-open on a case variant of the
  trailer, so the guard now uses `-imatch`, and the r34 text had the safety
  argument backwards. Also corrected here: this revision history had no entries
  for r30 through r34 at all, while the status line claimed each of them.
- **r34** — after Sol round 35. Step 7 described a guard without containing one,
  so it could not be reproduced without being written again; the exact
  parameterized block is now frozen in the plan with its measured output. Two
  counts were stale: the outcome line said building reopened this plan five
  times when it was six, and the build ledger's header still said revision 30
  after 31 rounds.
- **r33** — after Sol round 34, on Task 10's last step. The trailer check
  required `6201e30..HEAD` to print `clean` and it does not; three commits carry
  the trailer. Re-scoping was rejected, and correctly: the range already
  excludes the base, so "adds no new carriers" would have been a rename rather
  than a re-scope. Two facts measured only after the gate was frozen decided it
  — this repository merges with MERGE COMMITS, so branch commits do reach
  `main`, and `main` already carries 65 such commits INCLUDING this branch's own
  base. The user waived the three rather than rewrite 44 of 70 commits and
  invalidate every commit id the build ledger records. Step 7 became an
  authorized-debt guard that names all three ids, fails on a fourth, permits
  fewer, and reports authorized debt rather than `clean`. The claim was narrowed
  with it, because searching one literal is not an oracle for every form of AI
  attribution.
- **r32** — after Sol round 33, the FIRST round with the live gate actually run.
  It found that Task 7's absolute-key oracle could never have failed: the test
  built its "absolute" key with `Path.resolve()`, which FOLLOWS a junction on
  Windows, so the key named the same credential the relative default already
  reached, and exit 0 was produced identically by "the absolute key resolved"
  and by "it was ignored". Replaced by a five-step three-state structural oracle
  that carries its own instruction — a success REFUTES measurement 5 and is a
  finding, not a test to fix. The probe record and all its machinery were
  deleted, its stderr pin having been shown unstable by construction. Two
  further live findings: the secret guard fired on `scope`, a nine-character
  RFC 6749 response FIELD rather than a secret, so the excluded fields are now
  frozen by name; and capture decoded with the locale rather than UTF-8, so
  capture is now strict UTF-8 with its own failure type. Classification is
  evaluated before stability wherever both exist.
- **r31** — after Sol round 32. Task 11 was ADDED: the session asked whether
  "discard blank lines, then require one survivor" could be swept mechanically
  after three sweeps had each missed an instance, and nine surviving sites were
  enumerated so that deleting one is visible. Item 4b was made to exercise the
  real DELETION rather than only the release, and the post-command merge became
  a callback running inside the capture helper, before any stream can be
  rendered.
- **r30** — after Sol round 31, which read Task 7 whole and returned TEN
  findings. Nine were confirmed and fixed. Two were serious in kind rather than
  degree: a token issued by the command being scanned could reach pytest output,
  and the live-home setup had no check preventing the suite's own deliberate
  expiry from landing on the user's real credential. The tenth did not hold —
  it claimed the hostile `-Model` refusal fires before any lock interaction,
  which would have made the failed-build cleanup test vacuous; the refusal is
  inside the main `try` and after the acquire, and the reviewer accepted the
  refutation. The session then found a second instance of the blank-line class
  that neither the reviewer nor round 30 had named: the custody line, which
  carries the nonce the release is performed with.
- **r29** — REOPENED during BUILDING again, after Sol plan round 30, on a defect found by RUNNING frozen text rather than reading it. The recovery command hardened at r20 and r21 was NOT fail-closed: `-ErrorAction Stop` promotes an error to terminating for its own statement, but with no `$ErrorActionPreference` and no `try` in a `;`-chain, execution continues to the next statement anyway. Measured on both hosts: after a failed owner parse the login wrapper RAN, with a null identity, where the plan required "never invoked". Fail-closed at two of three dependencies and open at the third is worse than uniformly naive, because it reads as hardened. Task 6's four-row EXECUTION matrix caught it — the oracle Sol specified at r21 precisely because a string pin cannot test a command whose job is to run. The command now runs inside a child scriptblock setting `$ErrorActionPreference = 'Stop'` around a `try`, so later steps are structurally unreachable after any failure and the preference never leaks into the user's shell, and it VALIDATES what it received rather than only that the call returned. Three boundaries was also an under-count: the matrix is now NINE rows, adding owner launch failure, output cardinality, owner schema, and the environment the command reads, each asserting the login was never invoked by MARKER ABSENCE. Sol then found four more defects in already-committed callers, all of the same family — a scalar `fields` passing an array check because `@(...)` wraps it; blank lines discarded before counting, so extra blanks satisfy "exactly one line"; `Get-Content -ErrorAction SilentlyContinue` turning a failed stderr read into empty stderr, which is an unmade measurement satisfying the acceptance rule that exists to forbid exactly that; and unquoted `Start-Process` paths that mis-tokenize a space-plus-apostrophe segment. The last had a test written AROUND it, docstring and all, with the suite green over the bug — so the success fixture now requires both characters in one segment, and shaping a fixture to avoid a defect in code it drives is forbidden outright.
- **r28** — REOPENED during BUILDING, after Sol plan round 29, for one decision the plan never froze and an implementer therefore had to invent. The validator's OUTPUT line was frozen exactly; its CLI was not, so Task 2's implementer chose `ok` exits 0 and every other status exits 1 — including `absent`. That collides with Task 8's own table, which has `lane credential absent` as `N/A` and `the validator itself fails to run` as `BROKEN` on separate rows: one exit code for both makes a measurement that SUCCEEDED and found nothing indistinguishable from one that could not be made. All four classifications now exit 0 with empty stderr, and only an invocation that cannot classify exits 1. Sol then found the more dangerous half, which I had not: freezing the exit code alone leaves every CALLER free to accept missing or malformed stdout as a completed measurement, which is the same defect inverted. So acceptance is now a FOUR-PART rule — process launched, exit 0, stderr empty, exactly one schema-valid line — binding Tasks 5, 6 and 8, each of which gets TWO OPPOSING oracles: a nonzero exit carrying a valid-looking `absent` line, and an exit 0 carrying malformed output, neither readable as a credential state. Task 6 additionally emits NO recovery command on validator failure, because nothing was measured and nothing can therefore be recommended. Also frozen: `-Path`, resolution through `$PSScriptRoot` so a copied `tools` directory reaches its sibling, the `PARALLAX_KIMI_CREDENTIAL_STATE_FAULT` seam, a binding-refusal oracle, and a blank `-Path` taking the failure path rather than reporting `absent`.
- **r27** — after Sol plan round 27. Seven tasks PASS, and the `PARALLAX_LANE_LOCK_STARTTIME_FAULT` exception is confirmed right: its injected failure is deliberately CONVERTED into an ordinary `UNMEASURABLE` result with its own decisive oracles, so a seam-specific sentinel would describe something the user never sees. Three blockers, all small and all mine. The credentials-probe seam promised "no mutation" and then required a release in `finally`, which IS a mutation; it now says no mutation of the credentials-path object or its ACL, with the required release named as the only lock mutation. Three of the new seams were given names, sentinels, scopes and firing points but no ACTIVATION CONDITION, and the directory probe had no exit code either because its table said only "refuse nonzero" — all three now activate on any nonempty value, and the directory probe exits 6. And the shipped lifecycle literal, which r26 had just corrected from a wrong COUNT to an enumeration, still said "the first two are safe to repeat" from when the list had three entries: after inserting the probe FIRST, that ordinal silently dropped ACL application, which Task 5 defines as idempotent. It no longer counts or ordinals at all — all four are named safe, with the reason for each. That is the third consecutive round in which a numeric or ordinal reference in this one shipped sentence was wrong, which is the argument for enumerating rather than counting anywhere a list can grow.
- **r26** — after Sol plan round 26. Six tasks PASS, four blockers, and most of them are one careless habit of mine: writing "a named deterministic fault seam" and never giving the NAME. r25 did that twice in Task 5 and once more for the cleanup seam, and Task 6's directory seam had a variable name but no stderr SENTENCE — both strings are shared between production and tests, so a half-named seam still forces two independent inventions of the same literal. All five seams are now fully frozen: `PARALLAX_KIMI_LANE_LOGIN_HOME_PROBE_FAULT`, `PARALLAX_KIMI_LANE_LOGIN_CREDENTIALS_PROBE_FAULT` (distinct because they fire on opposite sides of the lock), `PARALLAX_LANE_HOME_DIRECTORY_PROBE_FAULT`, `PARALLAX_LANE_HOME_REMOVE_VERIFY_FAULT` and `PARALLAX_LANE_HOME_CLEANUP_DELETE_FAULT`, each with scope, firing point, exit code, exact sentinel and end state. Three real gaps beyond that. **Task 1's readability check had no failing direction**: both mutations pass an implementation that calls `is_file()` and never opens anything, so readability is now frozen as an actual binary open with a deterministic `PermissionError`/`OSError` mutation. **Post-deletion verification was two states when it is three** — a verification that CANNOT BE TAKEN would have been read as absence, releasing the lock and printing success on an unmade measurement, the governing invariant broken in the one place it guards a user's lane. And r25's own Task 5 probe made TWO other texts false at once: the bootstrap rule still said only two operations precede the lock, and Task 9's shipped literal, which r25 had just corrected from "three steps" to "three filesystem interactions", was now wrong at the COUNT rather than the kind. The literal no longer counts at all; it enumerates the four and says only these occur.
- **r25** — after Sol plan round 25, which was the SWEEP I asked for: having watched the same class produce a finding four rounds running, I asked where else this plan writes a binary over states that are not binary. Task 3 PASSED, its timing tolerances accepted now that cold start is outside the proof. The sweep found SIX, in five tasks. **Task 1** checked that a workflow path "exists", which a DIRECTORY named `test_x.py` satisfies while pytest collects nothing from it; it now requires a readable regular file, with a directory-ending-in-`.py` mutation. **Task 5** treated both of its directory bootstraps as create-or-apply, so a regular FILE at the lane-home path would have had its ACL REPLACED before the wrapper failed to create the lock — an ACL write onto an object the tool never established it owned, in the step that claims to be safe and identity-scoped; both probes are now four rows with named fault seams, and the credentials one releases so the lock ends `free` rather than stranded. **Task 6** had three: my own r24 sentence said "the last three rows" never invoke the lock, which swept in the DIRECTORY row and contradicted the table directly above it; the probe's fault seam was described but never NAMED, which is the exact gap r15 closed for a different seam; and DELETION ITSELF had no failure row, which matters because `tools/new-kimi-lane-home.ps1:131-133` deletes NON-TERMINATINGLY and prints `removed <path>` on the next line, so a failed deletion prints success and exits 0 today. **Task 8's** substate table called itself total while having no row for the CLEAN binary, so every fixture in that task was a failure fixture and an implementation that never emits `OK` would have passed all of them. **Task 9's** literal, which r24 had just rewritten, said "exactly THREE steps run before the lock" when parameter validation and debate-id generation also precede it; it now says three FILESYSTEM INTERACTIONS.
- **r24** — after Sol plan round 24. Seven tasks PASS; all three blockers are consequences of r23's own two edits, and two of the three are the fourth blind class AGAIN, now four rounds running. **The retry oracle I had just written was scheduler-dependent and covered one branch of two.** "The contender has not exited after one second" does not prove it ever REACHED contention, since a PowerShell process can still be starting, so releasing the holder then lets an implementation that never retries find a free record on its first real attempt and pass — the test would have certified the exact behaviour it was written to forbid. And contention has TWO branches, the exclusive handle and a readable holder, so a tool could retry one and refuse instantly in the other. Both oracles now synchronize on a frozen `PARALLAX_LANE_LOCK_CONTENTION_SIGNAL` seam, measure FROM the signal rather than from process start, and run against both branches; a signal-write failure exits 6, so the oracle cannot silently decay back into a timing test. That also answers the flakiness question I raised: cold-start scheduling is out of the proof entirely, rather than the window being widened, since the false-positive path was never about the window's size. **The first-use probe I had just added had FOUR reachable outcomes and I gave it two** — absent and directory — leaving a non-directory object at the lane-home path and an unmeasurable probe to be read as "absent", which would print a login command that cannot fix an obstruction. It is now a four-row table where only a successfully measured nonexistent path takes the recovery branch, with a regular-file collision oracle and a deterministic probe-fault seam rather than a test that depends on machine ACL behaviour. Third: that same new probe made the SHIPPED lifecycle literal false, because it still said creating the directory and applying its ACL are the ONLY pre-lock steps; the literal now names three and says explicitly that the builder never creates the directory.
- **r23** — after Sol plan round 23. Eight tasks PASS; the r22 fixes to Tasks 4, 5 and 7 all closed their defects completely. Two blockers, and both are the fourth blind class again — an oracle that does not partition its reachable states. **Task 3's new wait oracle bounded only the UPPER side**, so a tool that exits 3 IMMEDIATELY without ever waiting satisfied every assertion: it contends, exits 3, preserves the record, and returns well under five seconds, while contradicting the settled requirement that contention waits and retries. It now needs at least 0.8 seconds as well, plus a retry-SUCCESS oracle nothing covered — hold the lock, start a contender, prove it has NOT exited after a second, release, and require it to acquire before its budget expires — which is what separates retrying from sleeping once and giving up. And **the ordering question I raised about my own r22 change turned out to be a real pre-existing hole, in the other direction from the one I asked about**: Task 5's login wrapper is the ONLY thing that creates the lane home, and it creates it before acquiring, while Task 6 acquires FIRST and Task 3's missing-file protocol creates the lock FILE with no rule for creating its absent parent DIRECTORY. So on a machine where no lane login had ever run, the user's first debate would have failed inside Acquire — before credential validation, so before emitting the recovery command that an unusable credential is required to print. It would have failed with a lock error instead of instructions, which is the one moment the instructions matter most. Task 6 now has one bounded pre-lock test of the lane-home directory alone: absent means emit the command, exit nonzero, create nothing, and never invoke the lock tool.
- **r22** — after Sol plan round 22, which was a SWEEP I asked for rather than an ordinary round: Task 10's fail-open `git log` was pre-existing and had survived twenty rounds, so I asked whether the plan held others of its shape. It held two, plus two underspecifications. **Task 4's measurement 20 asserted DIVERGENCE between the two hosts and never required either host to have RUN** — one host failing and emitting nothing while the other succeeds IS divergence, so the gate could pass on a measurement never taken, which is precisely the empty-hash shape the spec records at `:89-95`. Each host must now exit 0 and emit one parseable result before any type is inspected, with a mutation making the subprocess exit nonzero and requiring failure rather than divergence. **Task 7's item 7 required the COMMAND to succeed but never required the SNAPSHOTS to**, so two suppressed hash failures would compare equal as empty strings — literally the way measurement 17 failed on its first attempt in this same cycle; there is now one helper that returns nothing unless all three components succeed, an explicit ban on equality-comparable sentinels, and two support oracles that force a hash failure and a stat failure. The two underspecifications: Task 3's wait budget did not bound the wait at all, so `-WaitSeconds 1 -PollSeconds 10` would have waited ten seconds against a spec promising the budget bounds caller patience, and the numeric domain said only `>= 0` and `> 0` without saying integer or range — the sleep is now clamped to the remaining budget, measured on a monotonic `Stopwatch`, with a five-second oracle. And Task 5's ACL said "one full-control rule" without inheritance flags, which a non-inheritable ACE satisfies while protecting nothing beneath, and left the `credentials` directory — the one that actually holds the credential — outside the protection the design requires; the exact ACE shape the builder already uses is now frozen for both directories, with the oracle comparing flags rather than existence and checking that a created credential file really inherited the access. Also fixed: the r20 Global Constraint over-reached and is narrowed to user-facing MULTI-STEP commands where a later step consumes an earlier step's output, since as written it demanded execution suites for single-invocation commands Task 3 already tests; and Step 1b's "both directions" hid four reachable rows, which Sol named as the FOURTH blind class, **oracle versus reachable failure-state partition**.
- **r21** — after Sol plan round 21, seven tasks PASS and three blockers, one of which my own r20 rule EXPOSED rather than caused. Task 10's history check piped `git log` straight into `Select-String` and never read its exit code, so a range it could not read produced no matches and no matches printed `clean`. That is an unmade measurement reading as a clean one, in the check that guards a merge, inside the plan whose governing invariant forbids exactly that — and it survived twenty rounds because every one of them read it as prose. It now captures the exit first and throws, with a second mutation on an invalid revision range. My r20 Global Constraint DID overreach, as Sol said: written to cover every executable snippet, it would have forced redundant execution suites onto Task 8's single-invocation override commands, which Task 3 already tests under both hosts, and blurred recovery commands together with verification commands, examples and prose lifecycles. It is narrowed to user-facing MULTI-STEP commands where a later step consumes an earlier step's output. And Sol named the FOURTH blind class on the strength of my own text: **oracle versus reachable failure-state partition**. "Both directions" sounded complete and hid four reachable rows — the recovery command has three dependent boundaries, so a JSON-parse failure and a login failure went unexercised — and the escaping had no failure direction at all, since every row could use an ordinary path. Step 1b is now a four-row matrix with an apostrophe-bearing lane home in the success row and frozen fixture routing. Sol's judgment on the comparison set, recorded because a stated judgment beats an absent finding: not closed at r20, and after these three fixes no further unexamined artifact boundary in this scope, the abstract category being unprovable either way.
- **r20** — after Sol plan round 20, which passed six tasks outright, confirmed r19's caller-propagation, fixture, doctor and shipped-contract work, and confirmed that the recovery command belongs in `Fixed names and values` rather than duplicated per task. The only behavioural blocker left was the constant I had just added, and it was broken in the way the THIRD blind class predicts: **plan prose versus runtime semantics**. It chained owner resolution and login with a semicolon and checked neither exit code, so a failed resolution would still have called the login wrapper with an empty owner, and its JSON parse had no `-ErrorAction Stop`. It reads as a finished command. The repository already does this properly at `tools/check-drift.ps1:145-149`, `:208-210` and `tools/read-kimi-round-evidence.ps1:206-210`, and the command now follows that idiom. The deeper fix is the oracle: **a string pin cannot test a command whose job is to run**, since the broken form and the correct one compare identical as strings, so Task 6 now EXECUTES the emitted command under both hosts in both directions — a failing `-ResolveOwner` stub must exit nonzero with the login stub never invoked, which is exactly the direction the broken form failed. That rule is also a Global Constraint now, so it binds every executable snippet the plan freezes rather than only this one. Two more: "emitted verbatim by every surface" was wider than its two real consumers and contradicted Task 2, Task 5 and Task 7, so the constant now names Task 6's builder refusal and Task 8's doctor rows and nothing else; and "single-quote-escaped" left the transformation implicit, so the substitution is now a literal algorithm.
- **r19** — after Sol plan round 19, which found that r18 restored the spec's visibility behaviours in the DIRECT TOOL and then let every caller swallow them. Sol named the class outright: **composition across caller boundaries**, where a tool implements the right behaviour while its wrapper or builder captures and discards the evidence, and no direct-tool oracle can see it. Both callers had it. The builder said all internal lock output is CAPTURED, full stop, so a correct lock plus a correct custody JSON plus every green test could still ship a silent reclaim; the login wrapper's contention test asserted only exit 3 and a non-invoked stub, which passes whether or not the diagnostic survives. Both now capture the lock's STDOUT, which is the nonce, and forward its STDERR unchanged, each with caller-boundary oracles for reclaim and contention. Four more: the r18 wording "a fresh acquisition prints NOTHING" contradicted "stdout is the nonce and nothing else" one line above; the oracle list covered the LIVE-record case but neither handle contention nor the UNMEASURABLE substitution, so a wrong handle message or a `liveness LIVE` under the seam would have passed; the spec says BOTH overrides are visible while the table left `-ForceRelease` at an underspecified "report what it displaced" and `-MalformedOverride` with nothing, both now frozen; and the shipped `lane-lock` literal's malformed list, which r18 had just widened, still enumerated fewer classes than Task 3 defines, so it now states the schema rule instead of listing instances, and carries the visibility rules too. Sol also named a SECOND blind class, fixture constructibility: r18's hand-built home B could not be built at all without contending with home A's retained hold, so the oracle could never reach its assertion; it is replaced by a six-step build-release-build sequence using only the real builder. Last, the spec requires the exact command that fixes an unusable credential, and both the builder and the doctor were naming the login wrapper instead of printing a runnable command; the command is now a single frozen constant in `Fixed names and values`, because two tasks emit it and a constant copied twice drifts.
- **r18** — REOPENED after the SECOND fable-reviewer whole-artifact read, dispatched on the frozen r17 because the first one read r12 and five adversarial rounds had rewritten substantial text since. No Criticals, and it confirmed both r12 Importants are closed consistently in every consumer. ONE IMPORTANT, and it is the class only a spec-versus-plan read can find: the design spec requires reclaim to be visible and a contention refusal to name the holder, and NEITHER survived into any task, while the identical requirement for `-ForceRelease` did. Because the implementer receives the packet and not the spec, a converged behaviour would simply have vanished from the shipped tool. The channel was not free either: acquire's stdout is the nonce Task 6 parses, so an invented stdout report would contaminate custody and an invented stderr one would be swallowed by the builder's capture. Both messages are now frozen on STDERR with exact wording and failure-capable oracles, and a fresh acquire over a `free` record prints nothing, so acquisition and reclaim stay distinguishable. Five Minors folded in rather than deferred: the doctor's UNKNOWN row overlapped the foreign-host row on every foreign-host record and now says same-host; the cleanup fault seam froze only its name while "the release failed" has two different end states, and now freezes skip-the-mutation with the record still held; the wrong-`-Path` oracle's home B had no construction, and building it with the builder would have contended with home A's retained hold and never reached the case; the shipped `lane-lock` text's malformed list read exhaustive but omitted a free record carrying a held-only known field, which is the exact case Task 3 twice says an unknown-field wording misses; and the region id `lane-lock` is reused from one deleted last cycle, so `DECLARED_REGIONS`' comment now says reused rather than restored.
- **r17** — after Sol plan round 17, which passed all ten tasks and confirmed both packet exclusions were right, then found that r16's packet boundary contradicted itself two ways. "Everything above this line" swallows the revision history, which the very next sentence excluded; and this section's own body is not above that line even though the packet must carry it, so the rule failed to include the rule. Both are the hazard of a RELATIVE boundary in a document that keeps growing. It is now an exhaustive numbered list of seven included blocks and a named list of what is excluded, with the failed wording recorded so nobody reintroduces it as a tidier phrasing.
- **r16** — after Sol plan round 16, which passed all three r15 content fixes and every one of the ten tasks on its own text, then found the last blocker OUTSIDE the tasks entirely: the HANDOFF. Fifteen rounds hardened what each task says while the packet the implementer would actually receive was never written down, and the one I stated when announcing the build — Global Constraints plus the task — is too narrow. `Fixed names and values` is a separate section, so under that packet Task 3 would have had to invent the token regex, the hostname comparer, the tick representation, the pid rule, the wait and poll bounds and the confirmation-hash rule, and Task 8 would have had to invent the lane-home path its recovery commands print, in a plan whose entire premise is that the implementer invents nothing. The packet is now a section of the plan rather than a habit of whoever dispatches it: the whole preamble plus one task, verbatim. Broadening it beats copying the values into each task, because duplicated constants drift and one edited copy becomes two contradictory definitions — which is the defect class this debate found three separate times, at r7, r14 and r15.
- **r15** — after Sol plan round 15, which passed seven of ten tasks and confirmed both consequences r14 drew beyond the literal instructions were correct, then found three blocking defects, two of them created by r14's own new semantics. The `debateHome` normalization trimmed a trailing separator UNCONDITIONALLY, which takes a drive root `C:\` to `C:` — a drive-relative path that resolves against that drive's current directory, so the comparison would have compared two different things — while nothing in Task 3 forbids a root-valued `-DebateHome` and the builder already treats a drive root as its own case at `tools/new-kimi-lane-home.ps1:89-99`; the trim is now guarded by a `GetPathRoot()` equality test, with root-spelling tests under both hosts. Task 5's exit code 3 still read "the exclusive handle OR a live holder" while Task 3's now covered LIVE or UNMEASURABLE, which is the same two-definitions-of-one-value shape r7 fixed for `host` and r14 fixed for the lock tool's own table; the wrapper's wording now matches. And the post-deletion release seam r14 added was described but never NAMED, while the other two seams carry exact shared strings precisely because production and tests must agree on them; it is now `PARALLAX_LANE_HOME_REMOVE_RELEASE_FAULT` with its scope, its skip-the-mutation behaviour, its fixed code 5, and its stderr sentinel all frozen. The fable artifact also gained an honest provenance limit — a subagent writes no transcript, so the file is this session's reproduction of a returned report and nothing can prove it was not altered in transcription, though every claim in it resolves against the repo — and the three remote checks were re-run rather than remembered, which corrected one of them: a bare `gh run list` is NOT empty, it returns runs on `main`, and only the branch-filtered form is evidence.
- **r14** — after Sol plan round 14, which agreed with both judgment calls r13 made rather than took (a `-DebateHome` mismatch is exit 2 because matching all five identity fields means there is no competing holder, so contention would be false; a same-host UNKNOWN liveness is `N/A` because staleness requires proof the owner is gone and the protocol's deliberate fail-closed outcome was reported successfully) and then found the execution detail around them defective in four tasks. r13 wrote that `debateHome` is "not part of the comparison" one paragraph above a table that compares it, and never said HOW to compare a path; it is now excluded from holder-identity equality but compared separately once all five identity fields match, under one frozen normalization. The new UNMEASURABLE liveness was defined but never routed through the acquire table, so the plan declared a third state and told the implementer nothing about it in the one mode that mutates. A foreign-host record's status liveness was still open, and could have been answered from a coincidentally matching local PID; it is now `UNKNOWN` always, with the local process table not consulted at all. Task 6's two new behaviours had no oracles that could fail: the wrong-`-Path` case tested "identity mismatch" when `debateHome` had just been excluded from identity, and post-deletion release failure had no test at all. Task 7 told the runner to build home C with "the same six steps" while writing no marker, when step 5 IS writing the marker. And Task 8's verification pinned "lock-status reporting" generically, which a wrong `UNKNOWN` mapping or a case-sensitive host comparison would have satisfied. Also retained: the fable-reviewer report, which round 14 correctly listed as UNVERIFIED because nothing inspectable existed, now sits at `rounds/2026-08-01-cred-lock/fable-whole-plan-review.md`.
- **r13** — REOPENED after the fable-reviewer whole-artifact read, which the thirteen adversarial rounds could not substitute for: every one of them read the plan task by task, and three consecutive rounds found defects inside text the previous round had just rewritten. No Criticals. TWO IMPORTANTS, both real and both invisible to a per-task read. The acquire table keyed on "identity fields" and never defined them, leaving `debateHome` in an undecided cell even though it is mandatory on every acquire, is a record field, and is what Task 6's Remove uses as its identity check; the five identity fields are now named, `debateHome` is recorded but excluded from the comparison with a mismatch as exit 2 rather than contention, and an idempotent re-acquire is frozen as writing NOTHING. And `-Status` declared a `UNKNOWN` liveness value that no rule ever assigned, because the only unmeasurable case was defined as ALIVE; liveness now has three outcomes, mutating modes treat unmeasurable as alive and refuse to reclaim while status reports UNKNOWN rather than claiming a measurement it did not make, and the doctor gains the row that consumes it plus the host comparison its foreign-host row always needed. Six Minors also folded in rather than deferred, each removing an invention: Remove-mode release precedence, the validator named in Task 5, C's creation sequence and its lack of a marker, the three-logins generalization recorded against measurement 11's two, the absolute-key fixture construction, and the debate-home/lane-home terminology collision in shipped contract text.
- **r12** — after Sol plan round 12. Two mechanical corrections, no behaviour added or cut. r11's new matrix was right, but an older sentence beside it still said the post-failure assertions are "the same in every case", which the matrix contradicts, so it is now scoped by the Remove outcome. And the matrix dropped one of the four main phases it was meant to cover: command and capture appeared in the production definition but not in either failure row, so a removal failure could have masked a command failure with nothing to catch it.
- **r11** — after Sol plan round 11. Nine tasks pass byte-unchanged. Both remaining defects were contradictions inside r10's own new oracle prose, not in the production contract. The combined cleanup oracle demanded an IMPOSSIBLE end state: a main-phase failure plus a removal failure, while also asserting the home absent and the lock free, when a deterministic sentinel refusal leaves the home present and the record unchanged. It is replaced by a three-row outcome matrix, which CUTS prose rather than adding it, on the reviewer's explicit advice that the state machine is converging and what to trim is duplicated oracle text. The seed matrix gained the direction that was never covered: a failing read with a SUCCEEDING release. And "every failure names only the field" contradicted the launch-failure and read-or-parse oracles, which have no matched field; it is now scoped to credential-match failures, with the other classes keeping their own sanitized messages.
- **r10** — after Sol plan round 10. Nine tasks pass byte-unchanged; all three remaining defects are Task 7 oracle gaps rather than design. The custody sequence had grown to four phases but the cleanup and precedence rules still named only the command, so a runner could mishandle a pre-command, merge or guard failure and pass every listed test; the MAIN OPERATION is now defined as all four phases, with combined oracles for each against a simultaneous removal failure, and the same rule applied to seeding. The helper promised to sanitize the timeout, launch-failure and error paths, but no test reached any of them; three exception-path oracles now do. And item 6, which deliberately has no lock, was still covered by a rule saying every post-command re-read happens while the hold is in force, which it cannot.
- **r9** — after Sol plan round 9. Nine of ten tasks pass byte-unchanged; every remaining defect is a consequence of r8's custody change and all three are in Task 7. r8 said the `finally` always calls `-Remove`, but a REFUSED build returns no nonce and Task 6 already released internally, so that path would have called removal with nothing to confirm; custody is now gated on a `custodyReceived` flag set only after Build exits 0 and its JSON parses, and item 4's routing row is split into successful and failed halves. The secret union had to be seeded while a hold was in force, but before the first build no hold exists; seeding is now the SOLE direct-acquire exception, with its own oracle. And the deliberate expiry writes had no declared place in the sequence, so an implementation could force expiry before the build, mutating a shared credential unlocked, and still pass everything; there is now an explicit PRE-COMMAND phase inside custody, and the contention oracle covers it.
- **r8** — after Sol plan round 8, which found a contradiction between two of my own tasks: Task 6 makes a successful build RETAIN its lock and return the nonce, while Task 7's routing told the runner to acquire again before every command and release in its own `finally`. The second acquire would have contended with the retained hold and the plain release would have broken `-Remove`'s identity confirmation. The builder is now the acquisition everywhere. Also: the shared helper had no file to live in, Task 7's own verification never collected the support suite, and one count said five modules where another said six.
- **r7** — after Sol plan round 7. Tasks 1, 2, 3, 4, 5, 6, 8, 9 and 10 now PASS; only Task 7 carried blocking defects, and all four were in the two surfaces r6 had just added. Its manual setup had no executable lifecycle: it must run the login wrapper, whose owner fields are mandatory, then write a marker under a lock, but the only owner rule resolved once per MODULE RUN and setup happens earlier. Its secret set had no timing contract, so a value ISSUED BY the command being scanned did not exist when the set was built, which is exactly C's rotation case. Neither the locking nor the guard had any oracle at all, so a runner with no locking and no helper passed all seven functional items. And four of the seven items never said which home they used. Also fixed: the exhaustive MALFORMED definition contradicted the per-state property rule by covering only UNKNOWN fields, leaving `host` on a free record with two definitions.
- **r6** — after Sol plan round 6. Preprocessing written in r5 was accidentally applied to `-Status` and `-ResolveOwner`, which would have made a read-only status of a malformed record exit 4 instead of reporting it. The custody-emission oracle pointed at the fault seam's OLD position, which cannot prove the boundary it exists to prove. The secret guard ran only at write time, while a pytest failure message prints captured streams first. That guard compared against optional credential fields that may be empty, and an empty string matches every output. And homes A and B were left unlocked despite performing authenticated dispatches that can refresh a 900-second token on their own.
- **r5** — after Sol plan round 5, with the cap lifted. Tasks 4 and 10 PASS. Two findings are SECURITY findings in a public repo and neither had occurred to me: Task 7 recorded the client's complete streams into a COMMITTED probe record, which can capture a credential value, and its token-rotation assertion compared token values inside an `assert`, where pytest's introspection prints both operands on failure. Both now have explicit guards. Three Task 3 partition defects survived r4: a free record carrying a held-only KNOWN field was not covered by the unknown-field rule, `-MalformedOverride` on a well-formed FOREIGN-HOST record had two different outcomes, and code 5's description covered only mismatch while three rows returned it for "nothing applicable". A mechanical preprocessing order now precedes the release table. Task 6's `$buildCompleted` was set before the custody JSON was emitted, so a failure to emit would retain a lock whose caller never received its nonce. Task 9's login literal omitted `-LaneHome`, so a custom lane home would build against one home and authenticate another. Task 2's fixture change had no oracle in its own task, and Task 5's exit table omitted two codes.
- **r4** — after Sol plan round 4, the cap. Every FIX accepted on the record; Sol stated they are mechanical and require no design escalation, and none was contested, so this is CONVERGED WITH AMENDMENTS per debate-protocol.md. The record-class partition is now total: `-MalformedOverride` covers every READABLE MALFORMED record rather than only unparseable bytes, an extra field on a FREE record is malformed too, exit 4 is narrowed so it cannot contradict the two overrides, the token regex is unified on 32 lowercase hex, and missing-file behaviour is frozen per mode. Also: the login wrapper's pre-lock bootstrap is now an explicit, bounded exception; its stream-inheritance oracle is TEMPORAL, because a wrapper that buffered both streams and replayed them would have passed the r3 test; the builder's cleanup needs TWO flags, since `!$buildCompleted` is also true when acquire itself failed; the doctor's aggregate is a total order including `N/A`; and the two-hash check no longer claims to establish WHO changed the bytes.
- **r3** — after Sol round 3, which found four CROSS-TASK contradictions r2 introduced: an acquire table that overlapped its own rows, a doctor override the lock forbade, a stream contract that was not jointly implementable, and a fixture contract that forbade what its own oracle required. Also fixed a region-comparison step that compared raw bytes which can never be equal.
- **r2** — after Sol rounds 1 and 2. Thirty findings. The load-bearing four: `OpenOrCreate` let a crash-truncated lock be stolen; idempotent acquire could not receive the nonce it required; the junction test was vacuous; and several live gates asserted invariance that holds when the command failed.
- **r1** — first draft, unreviewed.

Design spec: `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md` (revision 2, CONVERGED, PASS). Spec debate session `019fbb61-cc35-75b3-b34a-5b52219ad5bd`. Plan debate session `019fbb82-9e35-7b72-a64e-59fb60b981cd`. Replies retained at `docs/superpowers/plans/rounds/2026-08-01-cred-lock/`.

## Global Constraints

- **The invariant governing every check: an unmade, failed, or unreadable measurement is never a clean one.** A guard that cannot be evaluated REFUSES; it never skips. A live gate whose setup fails is a FAILED gate, never a skipped branch.
- **A claim may never be wider than its evidence.**
- **Every assertion of invariance requires a positive control first.** An unchanged file, hash, or absent side effect proves nothing unless the command that was supposed to act EXITED 0 and produced its expected output.
- The canonical backup model id may appear ONLY in `skills/multi-model-verify/references/model-prompting-notes.md` and `evals/multi-model-verify/test_backup_lane.py`.
- The client binary is `~/.kimi-code/bin/kimi.exe`, always by ABSOLUTE PATH.
- **Never print, log, or commit a credential VALUE.** Names, presence and file hashes only. Fixtures use obviously fake values.
- **Never `git add -A` and never `git add -u`.**
- Files under `skills/multi-model-verify/references/` are checked for the ABSENCE of backslashes.
- Contract regions must sit WHOLE inside a single pin. Adding or removing one means editing `DECLARED_REGIONS`.
- **Tests change FIRST for every live-verified contract, then the text.**
- Windows PowerShell 5.1 compatible, ASCII ONLY, in every `tools/*.ps1`. `-Encoding ascii`, never `utf8`.
- **Dual-host selection is `PARALLAX_PS_HOST`.** Copy `evals/multi-model-verify/test_codex_context_probe.py:35-67`. **Every module that touches Windows filesystem behaviour carries a module-level skip guard testing `os.name != "nt"`**, because Ubuntu supplies `pwsh` and a selector that merely finds a host will happily collect Windows tests there.
- **Every dual-host verification command in this plan is written TWICE, once per host.** A single invocation tests whichever selector happens to be in the environment, which is how this repo shipped a lock that did not lock on pwsh.
- **EVERY USER-FACING MULTI-STEP COMMAND emitted as one copy-paste unit, where a later step consumes an earlier step's output, MUST FAIL CLOSED AT EVERY DEPENDENCY.** Check an invoked command's exit code before consuming its output. **`-ErrorAction Stop` PROMOTES an error to terminating; it is NOT by itself a guard on a top-level semicolon chain.** Measured on both hosts: with no `$ErrorActionPreference` and no `try`, a failed `ConvertFrom-Json -ErrorAction Stop` still lets the NEXT `;`-statement run, so the command reads as hardened while remaining open at that dependency. **The later invocation must be made STRUCTURALLY UNREACHABLE after a failure** — a child scriptblock setting `$ErrorActionPreference = 'Stop'` around a `try`, so the preference does not leak into the user's interactive scope. Every dependency counts, not only the exit codes: output cardinality, schema, types, and the environment the command reads. **A string pin is necessary but NOT SUFFICIENT: the emitting task EXECUTES the exact emitted command under every host it claims, covering every prerequisite-failure row and the all-success row**, because a broken command and a correct one compare identical as strings. Standalone single-script commands, verification commands, parameter and JSON examples, and documented prose lifecycles stay governed by their task-local oracles. This is the plan-prose-versus-runtime gap: text can look complete and still continue past a failed prerequisite.
- Gate, all four: `skill_lint.py skills/multi-model-verify --strict`, `skill_scanner.py skills`, `run_trigger_evals.py`, `python -m pytest evals -q`.
- Destructive probes NEVER target the real `~/.kimi-code`, the real `$env:USERPROFILE`, or any drive root.

## Measured facts the plan is built on

**The fork (1-4).** `expires_in` 900s; a refresh rotates BOTH tokens; a copy that refreshes strands the source; the source's next use blanks it.
**Redirect is closed (5).** An absolute `oauth.key` does not resolve.
**The junction works (6-10).** Reads through; refresh writes THROUGH; no admin; an ACL does NOT propagate through; recursive delete does NOT delete through, BOTH hosts.
**Two logins coexist (11).**
**Concurrency was observed to survive (12, 13), n=1.** NOT relied on.
**The owner anchor (14, 21).** The harness-invoked shell's parent is stable and dies with the session; from a NESTED shell it names an intermediate process that exits. Resolve ONCE, pass EXPLICITLY.
**`provider list` proves nothing and mutates nothing (16, 17).**
**The credential schema (18).** Six keys.
**The exclusive-handle protocol is identical on both hosts (19).**
**Time representation (20).** Ticks round-trip as `Int64` on both; a date STRING is `String` on 5.1 and `DateTime` on 7.

## Fixed names and values

- Lane home `$env:USERPROFILE\.parallax-kimi-review`; credential `<lane-home>\credentials\kimi-code.json`; lock `<lane-home>\lane.lock`
- Lock `version` `1`. States `free`, `held`. No others.
- Required credential fields `access_token`, `refresh_token`, `expires_at`. Optional `scope`, `token_type`, `expires_in`.
- **`-DebateId` and `-Nonce` and their confirm forms match `\A[0-9a-f]{32}\z`** — exactly 32 lowercase hex, from `[System.Guid]::NewGuid().ToString("N")`. There is no second, broader token rule; r3 carried both and they conflicted.
- The DRIVER generates the debate id once, at the start of the debate, and retains it with the owner identity and the nonce for every later call.
- Hostname source `$env:COMPUTERNAME`, compared case-INSENSITIVELY. Tick strings `\A[0-9]+\z`, compared as STRINGS. `ownerPid` a JSON integer > 0. `-WaitSeconds` >= 0. `-PollSeconds` > 0. `-ConfirmSha256` exactly 64 hex, compared case-insensitively.
- **THE CREDENTIAL VALIDATOR'S INTERFACE, frozen here because Tasks 2, 5, 6 and 8 receive SEPARATE packets** and would otherwise each read an undefined contract differently:

  > Invoke the validator as `tools/read-kimi-credential-state.ps1 -Path <credential-file>`. `-Path` is a mandatory string, interpreted literally, and callers pass the resolved absolute credential-file path. For `ok`, `absent`, `unreadable` and `malformed`, classification SUCCEEDED: exit 0, exactly one schema-valid result line on stdout, and NOTHING on stderr. **Exit 0 means "classification completed", never "credential clean".** A bound invocation that cannot produce a classification exits 1, emits no stdout, and emits exactly `credential validator failed` on stderr. A PowerShell binding or process-launch failure is ALSO validator failure, even when script code never returns an exit code.

  | status | exit |
  |---|---|
  | `ok`, `absent`, `unreadable`, `malformed` | 0 |
  | no valid classification | 1 |

  **`absent` is a SUCCESSFUL measurement that found nothing, and it must not share an exit code with a measurement that could not be made** — the doctor has separate rows for the two, `N/A` against `BROKEN`, and an exit-1-for-everything mapping makes them indistinguishable at the exit code.

  **EVERY CALLER ACCEPTS A MEASUREMENT ONLY WHEN ALL FOUR HOLD**: the process launched, it exited 0, stderr was EMPTY, and stdout was exactly one parseable line whose object has exactly `status`, `detail` and `fields`, with a status/detail pairing from Task 2's table and `fields` an array of strings.

  **Four ways a caller can satisfy that rule while measuring nothing, all found in shipped code and all forbidden:**
  - **`@($parsed.fields)` wraps a SCALAR into a one-element array**, so a bare string passes an "array of strings" check. Require `$parsed.fields -is [System.Array]` BEFORE validating its elements. Every call position needs an exit-0 scalar-`fields` fixture.
  - **Discarding blank lines before counting them** lets `"\n\n{json}\n\n"` satisfy "exactly one line". Acceptance is ONE NONEMPTY LINE, optionally followed by exactly one LF or CRLF; leading, interior and extra blank lines are all rejected.
  - **Reading the captured streams with `-ErrorAction SilentlyContinue`** turns a failed stderr read into empty stderr, which is an unmade measurement satisfying the acceptance rule — the governing invariant, inverted, in the check that enforces it. Both capture reads are TERMINATING, and any read failure is validator failure, with a deterministic capture-read fault oracle.
  - **Unquoted paths in `Start-Process -ArgumentList`** mis-tokenize a path holding both a space and an apostrophe. Quote both file-path arguments, and make the dual-host success fixture contain BOTH characters. **A test may never be written around this defect**: one was, and its docstring recorded the workaround while the suite stayed green over the bug. Anything else is VALIDATOR FAILURE and is never read as a credential state. Checking exit 0 alone is the inverse of the defect above: it accepts missing or malformed stdout as a completed measurement.

- **THE LANE LOGIN RECOVERY COMMAND, emitted by EXACTLY TWO SURFACES: Task 6's builder refusal for an absent, unreadable or malformed lane credential, and Task 8's corresponding doctor rows.** It lives here rather than in one task because both emit it and both pin it, and a constant copied into two tasks drifts. **"Every surface that reports a credential status" would have been wider than that**: Task 2's validator prints one exact JSON line, Task 5 reports the same post-run verdicts, and Task 7's preflight promises only a message naming the wrapper, so a universal rule would have contradicted three tasks and left the implementer choosing which text wins.

  ```powershell
  & { $ErrorActionPreference = 'Stop'; try { $ownerLines = @(& 'tools/kimi-lane-lock.ps1' -ResolveOwner); $ownerExit = $LASTEXITCODE; if ($ownerExit -ne 0) { throw "owner resolution failed with exit $ownerExit" }; if ($ownerLines.Count -ne 1 -or -not ($ownerLines[0] -is [string]) -or [string]::IsNullOrWhiteSpace([string]$ownerLines[0])) { throw 'owner resolution returned invalid output' }; $owner = $ownerLines[0] | ConvertFrom-Json -ErrorAction Stop; if (-not ($owner -is [System.Management.Automation.PSCustomObject])) { throw 'owner resolution returned invalid schema' }; $ownerFields = @($owner.PSObject.Properties.Name); if ($ownerFields.Count -ne 2 -or -not ($ownerFields -ccontains 'ownerPid') -or -not ($ownerFields -ccontains 'ownerStartTicksUtc') -or -not (($owner.ownerPid -is [int]) -or ($owner.ownerPid -is [long])) -or [long]$owner.ownerPid -le 0 -or -not ($owner.ownerStartTicksUtc -is [string]) -or $owner.ownerStartTicksUtc -notmatch '\A[0-9]+\z') { throw 'owner resolution returned invalid schema' }; if ([string]::IsNullOrWhiteSpace($env:TEMP) -or -not (Test-Path -LiteralPath $env:TEMP -PathType Container -ErrorAction Stop)) { throw 'TEMP is not an existing directory' }; $verdictOut = Join-Path -Path $env:TEMP -ChildPath 'parallax-kimi-lane-login-verdict.json' -ErrorAction Stop; & 'tools/new-kimi-lane-login.ps1' -LaneHome '<lane-home>' -OwnerPid ([string]$owner.ownerPid) -OwnerStartTicksUtc $owner.ownerStartTicksUtc -VerdictOut $verdictOut; $loginExit = $LASTEXITCODE; if ($loginExit -ne 0) { throw "lane login failed with exit $loginExit" } } catch { throw } }
  ```

  **The command is FAIL-CLOSED, and the FIRST TWO attempts at it were not.** A plain `a; b` chain runs `b` whether or not `a` worked, so an early form called the login wrapper after a failed owner resolution. Adding `-ErrorAction Stop` to the parse looked like the fix and was not: measured on both hosts, a failed `ConvertFrom-Json -ErrorAction Stop` in a bare `;`-chain still lets the next statement run, and the login wrapper was invoked with a NULL identity. The command now runs inside a child scriptblock that sets `$ErrorActionPreference = 'Stop'` and wraps everything in `try`, so every later step is structurally unreachable after any failure, and the preference never leaks into the user's shell. It also validates what it received rather than only that the call succeeded: exactly one nonblank stdout line, a `PSCustomObject` carrying exactly `ownerPid` and `ownerStartTicksUtc`, an integral pid above zero, ticks matching `\A[0-9]+\z`, and a `TEMP` that exists and is a directory. Parsing alone would have accepted `{}`, `[]`, or extra fields.

  **`<lane-home>` substitution is a literal algorithm, not a description:** take the RESOLVED lane home the emitting surface is configured with, replace every `'` in it with `''`, then enclose the result in single quotes. "Single-quote-escaped" left the transformation implicit. The wrapper's owner fields are mandatory, so a message naming only the wrapper is not a command anyone can run.

## The implementer's task packet

**Every implementer receives exactly these blocks, verbatim: (1) the `For agentic workers` instruction; (2) Goal, Architecture and Tech Stack; (3) Global Constraints; (4) Measured facts the plan is built on; (5) Fixed names and values; (6) this entire `The implementer's task packet` section; and (7) its ONE assigned task.** It receives none of the Status text, Revision history, design and debate session pointers, other tasks, Debate record, raw rounds, or debate conversation.

The list is exhaustive on purpose. An earlier wording said "everything above this line", which failed twice over: the revision history is above the line and the next sentence excluded it, and this section's own body is not above the line even though the packet must carry it.

The narrower packet of Global Constraints plus the task alone is WRONG and was caught before any building started. Task 3 validates against the token regex, the hostname comparer, the tick representation, the pid rule, the wait and poll bounds and the confirmation-hash rule, and Task 8 emits recovery commands against the fixed lane-home path; all of those live in `Fixed names and values`, so under the narrow packet both tasks would have had to INVENT them, in a plan whose whole premise is a zero-judgment implementer.

Broadening the shared packet is the fix rather than copying the values into each task, because duplicated constants drift and one edited copy is then two contradictory definitions — the exact defect class this debate found three separate times.

---

### Task 1: Repair the Windows CI job

**Do this first. It is a merge blocker independent of everything else and is already broken at HEAD.**

`.github/workflows/skill-evals.yml:84` and `:95` both pass `evals/multi-model-verify/test_kimi_lane_lock.py` to pytest. That file does not exist: `775472c` deleted it with `tools/kimi-lane-lock.ps1` and did not touch the workflow. `python -m pytest <that path> -q` exits 4 with `ERROR: file or directory not found`. Verified never pushed and never run: `git branch -r --contains HEAD` empty, `git ls-remote --heads origin` returns only `refs/heads/main`, `gh run list --branch feat/kimi-code-backup-lane` returns no runs.

Task 3 later creates a file at that path. **Do not rely on that coincidence.**

**Files:** modify `.github/workflows/skill-evals.yml:79-99`; create `evals/tools/check_workflow_paths.py`; append to `evals/multi-model-verify/test_backup_lane.py`.

- [ ] **Step 1:** Write `check_workflow_paths.py` — pure Python, no PowerShell, no platform branch, so the ubuntu job runs it. **Two checks, not one:**
  - every `evals/...py` token named in the workflow resolves to a **READABLE REGULAR FILE**, and a stat or readability failure is FATAL. Plain existence is not the state that matters: a DIRECTORY named `test_something.py` exists happily, and pytest may then collect nothing from it, so an `exists()` check passes while the test module is gone. **READABILITY is frozen as successfully OPENING the file for binary reading** — `exists()` and `is_file()` alone are both insufficient, and only an actual open establishes the file can be read;
  - **HOST PARITY**: a declared set of required dual-host modules is present in BOTH Windows pytest steps. Existence alone is not an oracle for Task 10, because a module omitted from one host step still exists and stays green.

  **The initial required set is exactly these four**, the modules that survive in the workflow once the orphan is removed. It is not the implementer's to choose:

  - `evals/multi-model-verify/test_attestation.py`
  - `evals/multi-model-verify/test_codex_context_probe.py`
  - `evals/multi-model-verify/test_review_mirror.py`
  - `evals/multi-model-verify/test_kimi_round_evidence.py`

  Task 10 adds its SIX named modules to this set.

  Add tests asserting both checks. The path check must FAIL now.
- [ ] **Step 2:** Remove the orphaned line from both steps. Add nothing else; Task 10 adds the new modules once they exist.
- [ ] **Step 3: Verify.** `python evals/tools/check_workflow_paths.py` prints nothing, exits 0; the tests pass. Mutation-test BOTH checks, and the path check in BOTH of its directions: add a nonexistent path and confirm it is reported; **name a DIRECTORY ending in `.py` and confirm the checker reports it as not a test file**, which an `exists()` implementation would pass; **and make OPENING one referenced regular file raise `PermissionError` or `OSError` deterministically, requiring the checker to FAIL and to name that token** — which an `is_file()` implementation that never opens anything would pass. The unreadable case is simulated, never a real Windows ACL denial, because machine ACL behaviour is not something a test may depend on; remove one required module from ONE Windows step and confirm parity fails. Revert both.

---

### Task 2: Credential structural validation

**Files:** create `tools/read-kimi-credential-state.ps1` and `evals/multi-model-verify/test_kimi_credential_state.py`; modify `evals/multi-model-verify/test_kimi_lane_home.py:316-317`.

Output is exactly one line: `{"status":"<status>","detail":"<detail>","fields":[<names>]}`.

| status | detail | when |
|---|---|---|
| `ok` | `valid` | every required field present and well-typed |
| `absent` | `no-file` | the path does not exist |
| `unreadable` | `read-failed` | the path exists but the bytes cannot be read |
| `malformed` | `not-json` | the bytes do not parse as JSON |
| `malformed` | `not-object` | it parses but is not an object |
| `malformed` | `missing-field` | a required field is absent |
| `malformed` | `wrong-type` | a required field is present with the wrong type |
| `malformed` | `blank-token` | `access_token` or `refresh_token` is empty after trimming |

**Defect precedence, frozen.** One document can carry several defects and only one `detail` is emitted. Evaluate in this order, return the FIRST that fires: `not-json`, `not-object`, `missing-field`, `wrong-type`, `blank-token`. Tests include a document carrying the last three at once, asserting `missing-field`.

**`fields`** lists names observed in the parsed object, sorted with `[System.StringComparer]::Ordinal`, and is `[]` for exactly `absent`, `unreadable`, `not-json`, `not-object`. Names only.

**Types.** `access_token`, `refresh_token`: .NET `String`, non-empty after `Trim()`. `expires_at`: `Int32` or `Int64`. Anything else is `wrong-type`, specifically a fractional number, a boolean, `null`, the string `"123"`, and an `Int64`-overflowing value. **No truthiness and no freshness test:** `0` is VALID, a past expiry is VALID. On a duplicate key both readers take the last occurrence; the validator validates what the reader returned. **That behaviour needs its own opposite-direction oracle**, because an implementation that rejects duplicates outright, or that keeps the FIRST value, passes every other case: one fixture with an invalid first value and a valid last value must be `ok`, and one with a valid first value and an invalid last value must report the LAST value's precise defect. Both run under both hosts.

**The CLI contract is the one frozen in `Fixed names and values`, and it is not this task's to choose.** All FOUR statuses exit 0 with empty stderr, because each is a completed classification; only an invocation that cannot classify exits 1, with no stdout and exactly `credential validator failed` on stderr.

**Seam, frozen: `PARALLAX_KIMI_CREDENTIAL_STATE_FAULT`.** Validator only; activated by any nonempty value; fires AFTER parameter validation and immediately BEFORE the path probe; exit 1, EMPTY stdout, and exactly `PARALLAX_KIMI_CREDENTIAL_STATE_FAULT injected: simulated validator failure` on stderr. Tested under both hosts.

**Two more oracles the status table does not reach.** A PowerShell BINDING REFUSAL exits nonzero and produces no valid result line. And a bound `-Path` that is BLANK or whitespace-only takes the VALIDATOR-FAILURE path, never `absent`: an empty path is not a file that was measured and found missing.

- [ ] **Step 1: Write the failing tests.** Every status row asserts EXIT 0 and EMPTY stderr; the precedence case; `0` is `ok`; past expiry `ok`; fractional, boolean, `null`, `"123"`, overflow each `wrong-type`; all optional fields absent is `ok`; unknown extra field is `ok`; whitespace-only token is `blank-token`; `fields` sorted; `[]` for each of the four statuses; no output line contains a fixture token value. The `unreadable` fixture: create, deny read to the current identity with `icacls`, run, restore in a `finally`. Module guard `os.name != "nt"`; both hosts.
- [ ] **Step 2: Write the script.**
- [ ] **Step 3: Update the fixture** at `:316-317` to add a fake `refresh_token` and an integer `expires_at`.
- [ ] **Step 3b: Move the builder suite's host selector refactor HERE, out of Task 6.** Replace `shutil.which(...)` at `evals/multi-model-verify/test_kimi_lane_home.py:21` with the `PARALLAX_PS_HOST` pattern from `evals/multi-model-verify/test_codex_context_probe.py:35-67`, and add a module-level `os.name != "nt"` skip guard. Task 6 then treats this refactor as already done.
- [ ] **Step 3c: Give the fixture change its own oracle, in THIS task.** Without it, omitting step 3 still passes: the builder suite does not structurally validate `_fake_profile`'s credential, and until step 3b its selector ignored `PARALLAX_PS_HOST` entirely, so the advertised two-host gate ran one host. Add a test that builds `_fake_profile`, runs the new validator against the credential it wrote, and requires `status` of `ok` under EACH selected host.
- [ ] **Step 4: Verify, per host:**
```
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_kimi_credential_state.py evals/multi-model-verify/test_kimi_lane_home.py -q
$env:PARALLAX_PS_HOST = "pwsh.exe";       python -m pytest evals/multi-model-verify/test_kimi_credential_state.py evals/multi-model-verify/test_kimi_lane_home.py -q
```

---

### Task 3: The lock tool

`tools/kimi-lane-lock.ps1` is new. The previous file of that name was deleted at `775472c`; do NOT restore it. Read it once for the traps its header lists (`git show 775472c^:tools/kimi-lane-lock.ps1`), then write fresh. Its 45-minute clock, its last-writer-wins acquire, and its date-string timestamp are the three things this replacement exists to not have.

**Files:** create `tools/kimi-lane-lock.ps1` and `evals/multi-model-verify/test_kimi_lane_lock.py`.

**The record.** One line of ASCII JSON. Every time value is a DECIMAL STRING, never a number and never a formatted date: measurement 20 shows an integer is safe on both hosts and a date string is not, and a decimal string is safe by construction because neither reader coerces a non-date-shaped string.

```
{"version":1,"state":"held","host":"<name>","ownerPid":<int>,"ownerStartTicksUtc":"<digits>","debateId":"<32 hex>","nonce":"<32 hex>","debateHome":"<path>","acquiredTicksUtc":"<digits>"}
```

A free record is exactly `{"version":1,"state":"free"}`. `host` and `debateHome` must be non-blank strings.

**Property rules, stated per state so no reachable shape falls between them.** A HELD record carrying any property not named above is MALFORMED. **A FREE record carrying ANY property other than `version` and `state` is MALFORMED** — that wording, and not "unknown field", is what is required: a free record carrying `host` or `nonce` carries a KNOWN property that is simply illegal in that state, and an unknown-field rule does not reach it. Tests cover both a held-only known property and a wholly unknown one on a free record.

**Parameter sets.**

```
-Acquire  -LaneHome <p> -DebateId <t> -OwnerPid <n> -OwnerStartTicksUtc <s>
          -DebateHome <p> [-Nonce <t>] [-WaitSeconds <n>] [-PollSeconds <n>]
-Release  -LaneHome <p> -DebateId <t> -OwnerPid <n> -OwnerStartTicksUtc <s>
          -Nonce <t> [-WaitSeconds <n>] [-PollSeconds <n>]
-Status   -LaneHome <p> [-WaitSeconds <n>] [-PollSeconds <n>]
-ForceRelease -LaneHome <p> -ConfirmHost <s> -ConfirmOwnerPid <n>
              -ConfirmOwnerStartTicksUtc <s> -ConfirmDebateId <t> -ConfirmNonce <t>
              [-WaitSeconds <n>] [-PollSeconds <n>]
-MalformedOverride -LaneHome <p> -ConfirmSha256 <hex> [-WaitSeconds <n>] [-PollSeconds <n>]
-ResolveOwner
```

`-WaitSeconds` defaults to `0`; `-PollSeconds` to `2`. **Every LOCK-FILE mode accepts both, `-Status` included, because each takes the same exclusive handle. `-ResolveOwner` accepts neither**, because it touches no lock file at all.

**The exit-code guarantee is scoped to SUCCESSFULLY BOUND invocations**, and says so in the header. PowerShell's parameter binder rejects an unknown name, a missing mandatory value, or an ambiguous parameter set BEFORE any script code runs, and that failure exits 1. The deleted lock had exactly this shape — `[CmdletBinding]` with `[switch]` mode selectors and a typed `[int]$WaitSeconds` (`775472c^:tools/kimi-lane-lock.ps1:36-50`). Hand-rolling `$args` parsing to own that path was considered and rejected: it trades a documented, testable refusal for a large hand-written parser that can itself be wrong. **What the tests must guarantee instead is the property that matters: a binding failure exits nonzero and MUTATES NOTHING.** All value-shaped parameters are declared `[string]` and parsed inside the script, so no *value* can fail binding; only the invocation SHAPE can.

| Code | Meaning |
|---|---|
| 0 | the mode succeeded |
| 2 | a parameter value was refused, or owner resolution failed |
| 3 | contention: the handle, or a holder that is LIVE or UNMEASURABLE, and the wait budget expired |
| 4 | MUTATING FILE MODES ONLY: the record is MALFORMED or names a foreign host, and the applicable confirmed override is NOT the mode being run. `-Status` never emits it |
| 5 | a release or override was refused: either there was nothing applicable to release, or the supplied identity or hash did not match |
| 6 | the file is UNREADABLE, a write or flush failed, or any unclassified runtime failure |
| 1 | reserved for PowerShell's own parameter-binding refusal; never emitted by script code |

**The file-open protocol.** `OpenOrCreate` is FORBIDDEN: it cannot distinguish a file this call created from a pre-existing zero-length file, and a crash after `SetLength(0)` leaves exactly that, which it would read as free and STEAL.

1. Try `CreateNew`/`ReadWrite`/`None`. Success means this call created it.
2. On `IOException` because it exists, open `Open`/`ReadWrite`/`None`.
3. On `IOException` because another process holds the handle: CONTENTION. Sleep `min(-PollSeconds, the budget remaining)`, retry until the budget expires, exit 3.

**The wait budget BOUNDS the wait, and the naive procedure broke that promise.** Sleeping the whole poll interval means `-WaitSeconds 1 -PollSeconds 10` waits ten seconds, while the spec at `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:275-278` and the shipped literal both say the budget bounds caller patience. So the sleep is clamped to what remains, and **the elapsed budget is measured with a monotonic `Stopwatch`**, never by comparing clock readings.

**The numeric domain is frozen too**, because `>= 0` and `> 0` alone never said integer or fractional, nor gave a range: both are base-10 INTEGER strings that fit `Int32`, `-WaitSeconds` >= 0 and `-PollSeconds` > 0, and anything else is exit 2 with NO mutation.

**Its oracles need BOTH bounds, because an upper bound alone is satisfied by an implementation that never waits at all.** A tool that exits 3 immediately contends, exits 3, preserves the record and returns well under five seconds — passing every assertion while contradicting the settled requirement that contention WAITS and RETRIES (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:275-278`). Under both hosts:

**The oracles are synchronized on a SIGNAL, never on elapsed wall time, and they cover BOTH contention branches.** "The contender has not exited after one second" does not prove it ever REACHED contention — a PowerShell process can still be starting — so releasing the holder then lets an implementation that never retries find a free record on its first real attempt and pass. And there are TWO contention branches, the exclusive HANDLE and a readable HOLDER, so a tool can retry one while refusing immediately or oversleeping in the other.

**Seam, frozen: `PARALLAX_LANE_LOCK_CONTENTION_SIGNAL=<path>`.** On the FIRST actual contention decision, and once only, write exactly one ASCII line to that path — `handle` or `holder`, whichever branch it is — BEFORE sleeping. A failure to write the signal exits 6 with NO lock mutation, because an oracle that cannot synchronize must not silently become a timing test again.

Under both hosts, and **each of the two below is run against BOTH branches**:

- **The clamp**: `-WaitSeconds 1 -PollSeconds 10`. Wait at most ten seconds for the expected signal, then measure FROM the signal: the process stays alive at least 0.5 seconds and exits 3 within five, with the record preserved.
- **Retry SUCCESS**: `-WaitSeconds 30 -PollSeconds 1`. Wait at most ten seconds for the expected signal, assert the contender is still running, release the handle or the holder, then require acquisition within ten seconds with a NEW nonce and the contender's own held record.
- On signal timeout: terminate the contender in a `finally`, keep the original fixture until the assertions finish, and FAIL.
- The zero-budget immediate refusal stays as it is.

This takes cold-start scheduling out of the proof entirely and leaves generous CI tolerance. Widening the old bound would not have helped, because the false-positive path was never about the size of the window.
4. **A pre-existing zero-length file is MALFORMED, not free.**
5. Under the handle: read, decide, `SetLength(0)`, `Position = 0`, write, `Flush($true)`, close. **The file is never deleted by any path.** Close in a `finally`.

**Missing-file behaviour, frozen per mode.** Only ACQUIRE may create the file, initializing it to `free` and then proceeding through its table. `-Status` on a missing file reports `{"state":"free"}` and **creates nothing**. `-Release`, `-ForceRelease` and `-MalformedOverride` on a missing file exit 5 and **create nothing**. Every one of these has a test asserting the file's continued nonexistence.

**THE IDENTITY FIELDS ARE EXACTLY FIVE: `host`, `ownerPid`, `ownerStartTicksUtc`, `debateId`, `nonce`.** The table below said "identity fields" without ever defining them, which left `debateHome` in an undecided cell: it is mandatory on every acquire and it IS a record field, so an implementer could reasonably read it either way, and Task 6's Remove uses this very call as its identity check.

**`debateHome` is EXCLUDED from holder-identity equality but COMPARED SEPARATELY, after all five identity fields match.** Saying it was "not part of the comparison" contradicted the table, which does compare it. The two-stage shape is the point: the five fields decide WHO holds the lock, and `debateHome` then decides whether that holder is talking about the debate it thinks it is. Two callers cannot differ in `debateHome` while matching all five identity fields unless one is confused, so a mismatch is a caller error and exits 2, never 3: converting it to contention would be wrong, since it IS the same holder. This is what makes Task 6's Remove reject a wrong `-Path` at the lock rather than downstream at the sentinel.

**`debateHome` equality is normalized before comparison, by one stated algorithm:** `[System.IO.Path]::GetFullPath()` to an absolute path; then `[System.IO.Path]::GetPathRoot()` of that result; then, **only when the normalized string does NOT equal its own root under ordinal case-insensitive comparison**, a single trailing directory separator trimmed; then an ORDINAL CASE-INSENSITIVE comparison of the results. Without this the plan froze a comparer for the hostname and for the tick strings but left this one to invention. **The root guard is not decoration.** An unconditional trim takes a drive root `C:\` to `C:`, which is not the same path at all — it is drive-relative and resolves against that drive's current directory — and nothing in Task 3 forbids a root-valued `-DebateHome`, so the comparison would silently compare two different things. The builder already treats a drive root as its own case for exactly this reason, at `tools/new-kimi-lane-home.ps1:89-99`. Tests, under BOTH hosts: two EQUIVALENT SPELLINGS of one non-root path — a relative form and a trailing-separator form — compare equal; two equivalent spellings of a drive ROOT compare equal and normalize to the same absolute root rather than to a trimmed one; and a genuinely different path compares unequal.

**An idempotent re-acquire WRITES NOTHING.** It reprints the stored nonce and leaves the record byte-identical, `acquiredTicksUtc` included, so a re-acquire can never be mistaken for a fresh acquisition in the record.

**Acquire, over READABLE, WELL-FORMED, SAME-HOST records.** Foreign-host is exit 4, malformed is exit 4, unreadable is exit 6, handle contention is exit 3; all four are decided before this table and are not rows in it.

| Record state | `-Nonce` | Outcome |
|---|---|---|
| `free`, or `held` with a DEAD owner | absent | acquire or reclaim, generate a NEW nonce, print it |
| `free`, or `held` with a DEAD owner | supplied | exit 2 — a nonce may never be reused for a new acquisition |
| `held`, LIVE, all five identity fields equal, `-DebateHome` equal | supplied and equal | idempotent success, reprint the nonce, write NOTHING |
| `held`, LIVE, all five identity fields equal, `-DebateHome` DIFFERS | supplied and equal | exit 2 — caller error, not contention |
| `held`, LIVE, the four non-nonce identity fields equal | absent, or supplied and different | contention |
| `held`, LIVE, any of the four non-nonce identity fields differs | either | contention |

Rows 5 and 6 keep a lock debate-scoped rather than session-scoped: one session holds one debate's lock and never silently displaces its own other debate. After the split, row 4 is the `-DebateHome` refusal.

**RECLAIM AND CONTENTION ARE BOTH VISIBLE, and both report on STDERR.** The design spec requires this twice — "Reclaim is visible. Taking over a lock whose owner is genuinely dead reports what it reclaimed and from whom" at `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:297-298`, and a wait budget exhausted "is a refusal naming the holder" at `:276-278` — and the plan carried neither into any task, while keeping the same requirement for `-ForceRelease`. An implementer receives the packet, not the spec, so a converged behaviour would have vanished from the shipped tool.

The channel is not free to choose. **Acquire's STDOUT is the nonce and nothing else**, because Task 6 parses it, so both reports go to STDERR:

- **Reclaim**, on the DEAD-owner row only: `reclaimed a dead holder: pid <pid> ticks <ticks> debate <debateId> home <debateHome>`. **A fresh acquisition over a `free` record emits NO STDERR REPORT; its stdout is still exactly the new nonce.** Saying it "prints nothing" contradicted the stdout rule one line above. There is nothing to reclaim over a free record, and reporting one would make acquisition and reclaim indistinguishable.
- **Contention**, before exiting 3 from the acquire table's rows 5 and 6: `contended: holder pid <pid> ticks <ticks> debate <debateId>, liveness <LIVE|UNMEASURABLE>, wait budget <n>s expired`. Handle contention, which never reads a record, reports `contended: the lock file is held by another writer, wait budget <n>s expired`.

**BOTH OVERRIDES ARE VISIBLE TOO**, which the spec requires at `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:280-295` and which the table left as an underspecified "report what it displaced" for one and nothing at all for the other. On stderr, with stdout empty:

- `-ForceRelease`, on success: `force-released holder: host <host> pid <pid> ticks <ticks> debate <debateId> home <debateHome>`
- `-MalformedOverride`, on success: `overrode malformed lock: bytes <bytes> sha256 <sha256>`

No message carries a credential field, and the debate id is a random identifier rather than a secret.

**Oracles, each able to fail, and they must cover BOTH contention forms and BOTH liveness values** — a list covering only the LIVE record case passes an implementation that prints the wrong handle message or reports `liveness LIVE` under the seam:

- reclaiming a DEAD holder emits that exact stderr line naming the dead holder's pid and debate id, while stdout stays exactly the new nonce;
- a fresh acquire over `free` emits NO stderr line, with stdout still exactly the new nonce;
- an exhausted wait budget against a LIVE holder emits the holder line naming that holder before exit 3;
- **exclusive-handle contention** exits 3 with EMPTY stdout and the exact handle-contention line, which is the only case where no record was read;
- **a competing identity under `PARALLAX_LANE_LOCK_STARTTIME_FAULT`** exits 3 with an unchanged record, empty stdout, and a holder line containing exactly `liveness UNMEASURABLE`;
- each override's success emits its exact line with empty stdout.

**A same-host UNMEASURABLE holder follows every row above that is not the DEAD row.** It is treated exactly as LIVE for routing: exact identity with an equal `-DebateHome` is idempotent, a differing `-DebateHome` is exit 2, any competing identity contends, and NOTHING reclaims it. Exit code 3's meaning covers contention against a LIVE or UNMEASURABLE holder alike. The fault seam tests BOTH directions: an exact-identity re-acquire under the seam succeeds idempotently, and a competing identity under the seam contends rather than reclaiming.

**Preprocessing for MUTATING FILE MODES ONLY — `-Acquire`, `-Release`, `-ForceRelease` and `-MalformedOverride`.** `-Status` does NOT run it and follows its own read-only rule below, which returns 0 on a malformed record; `-ResolveOwner` performs no lock-file operation at all. Applied before the release table so the partition is mechanically total, these four steps run in order and only what survives them reaches the table:

1. **Unreadable** file: exit 6, every mode.
2. **Readable but MALFORMED**: exit 4 for every mode EXCEPT `-MalformedOverride`, which proceeds to its hash rows.
3. **Readable, WELL-FORMED, FOREIGN-HOST held**: exit 4 for `-Acquire`, `-Release` and `-MalformedOverride`; `-ForceRelease` proceeds to its identity rows. This is the only mode permitted to act on a foreign-host record, and scoping it here is what removes the r4 overlap where a well-formed foreign-host record matched both "well-formed, exit 5" and "foreign-host, exit 4".
4. Everything remaining is a missing file, a `free` record, or a same-host well-formed `held` record.

**Release and the overrides, over what survives preprocessing.**

| Mode | Record | Outcome |
|---|---|---|
| `-Release` | missing file | exit 5, creates nothing |
| `-Release` | `free` | exit 5 — nothing applicable, the signature of a late duplicate release |
| `-Release` | `held`, complete identity equal | write `free`, exit 0 |
| `-Release` | `held`, any field differs | exit 5, record untouched |
| `-ForceRelease` | missing file, or `free` | exit 5 |
| `-ForceRelease` | `held` (same-host OR foreign-host), complete identity equal INCLUDING `-ConfirmHost` | write `free`, exit 0, emit the frozen `force-released holder:` line above |
| `-ForceRelease` | `held`, any field differs | exit 5, record untouched |
| `-MalformedOverride` | missing file | exit 5 |
| `-MalformedOverride` | readable, WELL-FORMED, free or same-host held | exit 5 — this mode is only for malformed records |
| `-MalformedOverride` | **any READABLE MALFORMED record**, hash equal | write `free`, exit 0, emit the frozen `overrode malformed lock:` line above |
| `-MalformedOverride` | any readable malformed record, hash differs | exit 5 |

Tests cover every FOREIGN-HOST and mode pairing explicitly, because that intersection is where r3 and r4 both left an overlap.

**`-MalformedOverride` covers EVERY readable malformed class, not only unparseable bytes.** MALFORMED includes parseable objects with a missing, unknown, wrongly typed or invalid field, and those states are reachable; r3 scoped the override to "unparseable" and left them with no recovery. Tests cover each malformed class with a matching and a mismatching hash.

**`-ForceRelease` carries `-ConfirmHost` and may free an exactly-confirmed FOREIGN-HOST record.** That and `-MalformedOverride` are the only mutations permitted on records ordinary modes refuse, which is why exit 4 is scoped as it is in the table above. Ordinary acquire and release still refuse a foreign-host record outright.

**Liveness has THREE outcomes, and they are not the same for deciding and for reporting.** LIVE: a process with that pid exists and its start ticks match. DEAD: no process with that pid, or one whose start ticks differ. **UNMEASURABLE: the pid lookup succeeded but the start time could not be read**, which `Get-Process` does on another user's process. The catch wraps the start-time read specifically.

**Every MUTATING mode treats UNMEASURABLE as ALIVE and refuses to reclaim**, because an unevaluable measurement is never a clean one. **`-Status` reports it as `UNKNOWN`, never as `LIVE`**, because reporting LIVE would claim a measurement that was not made. r12 declared `UNKNOWN` in the status output while assigning only LIVE and DEAD, which left the third value with no rule at all.

**A FOREIGN-HOST record's status liveness is `UNKNOWN`, always, and the local process table is NOT consulted at all.** Its liveness cannot be checked from here, so the recorded pid may coincidentally match an unrelated local process, and reading that would report another machine's holder as LIVE or DEAD on the strength of a collision. Its own oracle: a foreign-host record whose recorded pid IS a live local process must still report `UNKNOWN`.

A **test seam** forces that branch: with `PARALLAX_LANE_LOCK_STARTTIME_FAULT` set, the start-time read throws AFTER the pid lookup succeeds. It is safe by construction — its only possible production effect is to classify a holder ALIVE and refuse a takeover, never to reclaim. Precedent `tools/new-kimi-lane-home.ps1:416-423`, tested at `evals/multi-model-verify/test_kimi_lane_home.py:102-106`. A SYSTEM-owned process is an OPTIONAL live confirmation only.

**MALFORMED** means any of: not JSON; not an object; `version` absent or not `1`; `state` not one of the two literals; a record missing any field required for its state; **a record carrying ANY PROPERTY FORBIDDEN FOR ITS STATE, which includes any unknown property in either state AND any held-only KNOWN property on a free record**; any field failing its type or pattern rule; a zero-length file. The forbidden-for-its-state wording is required: an unknown-field rule alone contradicts the per-state property rule above, because `host` on a free record is a known property, and two definitions of the same condition is two behaviours for an implementer to choose between. **Time fields that are date-shaped rather than digits are MALFORMED**, so the representation cannot regress to the shape measurement 20 shows diverging.

**`-Status`** is READ-ONLY, takes the handle only long enough to read, **creates nothing**, and exits 0 for every READABLE file state including MALFORMED; unreadable is exit 6.

```
{"state":"free"}
{"state":"held","host":...,"ownerPid":...,"ownerStartTicksUtc":"...","debateId":"...","nonce":"...","debateHome":"...","liveness":"LIVE"|"DEAD"|"UNKNOWN"}
{"state":"MALFORMED","bytes":<n>,"sha256":"<hex>"}
```

**The held object carries every field `-ForceRelease` requires, the nonce and host included.** That closes the lost-nonce deadlock: the nonce distinguishes two debates from one session, it is not a secret, and these overrides are not authentication. `liveness: LIVE` means the process is running and NOTHING MORE.

**`-ResolveOwner`** prints `{"ownerPid":<n>,"ownerStartTicksUtc":"<digits>"}` for the parent of the invoking shell, and its help states this is correct only for a DIRECT invocation (measurement 21). Failure to resolve is exit 2.

- [ ] **Step 1: Write the failing tests.** One per row of both tables, per exit code, per rule. Plus: a pre-existing zero-length file is MALFORMED and recoverable by `-MalformedOverride`; **each readable malformed class is recoverable by matching hash and refused by mismatching hash**; an extra field on a FREE record is MALFORMED; every mode's missing-file behaviour including the creates-nothing assertion; the file still exists after every mutating mode; a date-string time value is MALFORMED; a 4-second wait against a LIVE holder exits 3 and does NOT reclaim; status-provided identity force-releases, including a foreign-host record; an old nonce fails after a reclaim; status leaves the file byte-identical; **a binding-refused invocation exits nonzero and leaves the lock byte-identical**; and **exit-code exhaustiveness** across the bound-invocation matrix, asserting every observed code is in `{0,2,3,4,5,6}`. Module guard `os.name != "nt"`; both hosts.
- [ ] **Step 2: Write the script.**
- [ ] **Step 3: Verify, per host:**
```
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_kimi_lane_lock.py -q
$env:PARALLAX_PS_HOST = "pwsh.exe";       python -m pytest evals/multi-model-verify/test_kimi_lane_lock.py -q
```

---

### Task 4: Live gate for the lock protocol on both hosts

Task 3's tests are the implementation oracle. This gate proves the OS behaviour underneath. **It is not a regression gate for the implemented record format.**

**Files:** create `evals/multi-model-verify/test_lock_protocol_live.py`.

- [ ] **Step 1: Write the gate,** exercising the sequence production uses:

1. `CreateNew` succeeds fresh and raises `IOException` on an existing path; `Open` then succeeds.
2. A second exclusive open while held raises `IOException`.
3. Truncate-and-rewrite in place under the held handle succeeds; final bytes are exactly the new record.
4. **The crash oracle, synchronized so the crash point is proven.** The file starts with a VALID held record. A child opens it exclusively, calls `SetLength(0)`, flushes, writes a ready marker to a signal file, then blocks forever without writing a record. The parent waits for the marker, kills the child, asserts the file is EXACTLY zero bytes, and asserts `-Acquire` against it exits 4 rather than reclaiming. A second fixture repeats it with the child writing a fixed partial prefix before blocking, asserting those exact bytes survive and `-Acquire` still exits 4.
5. The tick/date-string divergence of measurement 20, asserting the DIVERGENCE — **but only after each host invocation is proven to have HAPPENED.** "Assert divergence" is satisfied by one host failing and emitting nothing while the other succeeds, which is the same shape as the discarded empty-hash measurement at `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:89-95`, where a clean verdict was produced by two empty strings comparing equal. So: the selected host process must EXIT 0 and emit exactly ONE parseable result before any type is inspected, and the asserted types are the measured ones — ticks `Int64` on both hosts, the date value `String` on 5.1 and `DateTime` on 7 (`:65-66`). Its own mutation: make that subprocess exit NONZERO and confirm the gate FAILS rather than reporting divergence.

**The crash oracle's synchronization is BOUNDED.** The parent waits for the ready marker at most TEN SECONDS. On timeout it terminates the child in a `finally` and FAILS WITHOUT INSPECTING THE LOCK BYTES, because a child that died or wedged before signalling never reached the crash point the oracle exists to prove. **Only an observed ready marker licenses killing the child and asserting the crash state.** Without a bound, "waits for the marker" against a child that then blocks forever left both the timeout and the cleanup to invention.

Module guard `os.name != "nt"`; on Windows both hosts are REQUIRED and an unavailable host FAILS.

- [ ] **Step 2: Verify, per host:**
```
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_lock_protocol_live.py -q
$env:PARALLAX_PS_HOST = "pwsh.exe";       python -m pytest evals/multi-model-verify/test_lock_protocol_live.py -q
```
Then change the measurement-20 assertion to expect agreement between hosts and confirm it FAILS; revert.

---

### Task 5: The lane login wrapper

**Files:** create `tools/new-kimi-lane-login.ps1` and `evals/multi-model-verify/test_kimi_lane_login.py`.

```
-LaneHome <p>            default: $env:USERPROFILE\.parallax-kimi-review
-OwnerPid <s>            MANDATORY
-OwnerStartTicksUtc <s>  MANDATORY
-KimiBinary <p>          default: $env:USERPROFILE\.kimi-code\bin\kimi.exe
-VerdictOut <p>          MANDATORY
-Force                   switch
```

**Stream mechanism, frozen.** The child's stdout and stderr are INHERITED and untouched, so an interactive login renders normally. **The machine-readable verdict goes to `-VerdictOut`, never to stdout.** An inherited child writes to the wrapper's own stdout handle, so "inherited" and "stdout carries only JSON" cannot both hold; a dedicated file resolves it without touching the child's streams. The wrapper's own messages go to stderr.

**The bootstrap exception, stated explicitly.** The lock lives INSIDE the lane home, so it cannot guard the creation of that home. **The only pre-lock operations are THREE: the fail-closed lane-home PROBE, then creating the lane-home directory if the probe measured it nonexistent, then applying the ACL idempotently for the current identity.** The probe is itself a pre-lock filesystem interaction, so a two-item list stopped being true the moment it was added. All three are safe to race: the probe only reads, and the other two are idempotent and identity-scoped. Everything that reads or writes the CREDENTIAL happens under the lock.

**Order of operations, frozen.**

1. Validate parameters. 2. **Probe the lane home, FOUR rows, not "create if absent otherwise apply".** Only a successfully measured NONEXISTENT path creates. A DIRECTORY applies the ACL. An existing NON-DIRECTORY object and an UNMEASURABLE path each exit 6 with NO mutation, NO lock invocation, NO client invocation and NO `-VerdictOut` write. Without those two rows a REGULAR FILE at the lane-home path would have its ACL REPLACED before the wrapper eventually failed to create `lane.lock`, which contradicts this task's own claim that the pre-lock steps are safe and identity-scoped. **Its fault seam is `PARALLAX_KIMI_LANE_LOGIN_HOME_PROBE_FAULT`**, and calling a seam "named" without giving the name left production and tests to invent the same string separately. Login-wrapper scope only; activated by any nonempty value; fires immediately BEFORE the real probe; simulates the UNMEASURABLE row; exits 6; writes exactly `PARALLAX_KIMI_LANE_LOGIN_HOME_PROBE_FAULT injected: simulated lane-home probe failure` to stderr and nothing to stdout; no `-VerdictOut` write, no client invocation, no lock invocation, no mutation. Both the file-collision and the fault are tested with the object's bytes AND its ACL asserted unchanged, and the tests assert that exact literal. Apply the ACL idempotently, **as the EXACT ACE shape the builder already uses at `tools/new-kimi-lane-home.ps1:399-408`**: `SetAccessRuleProtection($true, $false)`, every existing access rule removed, then ONE rule for the current `WindowsIdentity` SID — `FullControl`, inheritance flags `ContainerInherit,ObjectInherit`, propagation `None`, type `Allow`. "One full-control rule" alone did not say inheritable, and a non-inheritable ACE satisfies that wording while protecting nothing beneath. Measurement 9 shows the throwaway home's ACL does not propagate through the junction, so this target needs its own. 3. Generate a login debate id, 32 lowercase hex. 4. ACQUIRE, with **`-DebateHome` set to the resolved LANE-HOME path**, and set `$lockAcquired` only on success. 4b. **Probe the `credentials` path with the SAME FOUR ROWS, then create if nonexistent and apply the SAME protected DACL DIRECTLY to it**, after the lock is held and before any credential is read or the client is invoked. A DIRECTORY applies the ACL; a NON-DIRECTORY object and an UNMEASURABLE path each exit 6, invoke NO client, PRESERVE the obstructing object byte-for-byte with its ACL intact, and RELEASE in the `finally` — so the lock ends `free` rather than stranded. **Its own seam is `PARALLAX_KIMI_LANE_LOGIN_CREDENTIALS_PROBE_FAULT`**, distinct from the lane-home one because they fire on opposite sides of the lock and a shared name could not tell them apart. Login-wrapper scope only; any nonempty value activates; fires immediately BEFORE the real credentials probe; simulates the UNMEASURABLE row; exits 6; writes exactly `PARALLAX_KIMI_LANE_LOGIN_CREDENTIALS_PROBE_FAULT injected: simulated credentials probe failure` to stderr and nothing to stdout; no client invocation; **no mutation OF THE CREDENTIALS-PATH OBJECT OR ITS ACL** — saying "no mutation" flatly contradicted the next clause, since a release IS a mutation — and after injection **the required `finally` release is the ONLY lock mutation, transitioning the held record exactly to `free`**. Both directions are tested, asserting that exact literal, and the credentials case additionally asserts the lock is `free` afterwards. The design protects the lane home AND its credentials directory at `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:183-187`; protecting only the parent leaves the directory that actually holds the credential outside the intended protection. 5. Read the existing credential verdict **with `tools/read-kimi-credential-state.ps1`**, the same validator Task 6 names explicitly, **resolved through `$PSScriptRoot` so a copied `tools` directory resolves the sibling rather than the repository's**, and accepted ONLY under the four-part rule in `Fixed names and values`. 6. If `ok` and no `-Force`, skip the client; otherwise invoke it. 7. Re-read the verdict with the same validator. 8. Write it to `-VerdictOut`. 9. In a `finally`, RELEASE using the captured nonce, but **only when `$lockAcquired`**.

**VALIDATOR FAILURE IS NOT A CREDENTIAL STATE**, and the wrapper calls the validator TWICE, so both positions need rules. A failure at the PRE-CLIENT call exits 6, invokes NO client, writes NO `-VerdictOut`, and releases in `finally`. A failure at the POST-CLIENT call also exits 6 and writes no `-VerdictOut` and releases, and the client may already have run. Two OPPOSING oracles, because each catches what the other misses: a NONZERO exit carrying a syntactically valid `absent` line is validator failure, and an EXIT 0 carrying malformed or schema-invalid output is ALSO validator failure. Both invocation positions are exercised, using a disposable copied `tools` directory holding the wrapper, the lock tool and a STATEFUL validator stub, so `$PSScriptRoot` resolves the stub without touching the repository's own tool.

**Success requires structural validity.** The post-run verdict decides the exit code, never the client's.

**Exit codes, scoped to SUCCESSFULLY BOUND invocations exactly as Task 3 is.** `0` success. `2` parameter refusal. `3` lock contention: the exclusive handle OR a holder that is LIVE or UNMEASURABLE, since a preserved lock code 3 covers all three. The wording matches Task 3's code 3 exactly; two definitions of the same propagated code is the defect this replaced. One test per exit code stays sufficient here, because the wrapper receives the identical lock-tool code 3 whichever holder produced it. `4` the lock is malformed or foreign-host. **`5` a release refusal propagated from the lock tool** — reachable, because the record can be freed or displaced between acquire and the `finally`. `6` an invalid post-run credential, a `-VerdictOut` write failure, or any unclassified runtime failure. `1` is reserved for PowerShell's binder and never emitted by script code, with the same mutation test: a binding-refused invocation exits nonzero and mutates nothing.

**Release-failure precedence, frozen.** If the MAIN operation already failed, preserve that original code and write the release failure to stderr only. If the main operation SUCCEEDED but the release failed, return the release code. Both directions are tested.

**The post-run verdict decides the exit code, in BOTH directions.** A client exit of 0 followed by an `absent`, `unreadable` or `malformed` credential FAILS with 6. **A client exit that is NONZERO followed by a structurally `ok` credential SUCCEEDS with 0.** Without that second test an implementation that simply propagates the client's exit code passes every other listed case.

**The wrapper's handling of the LOCK's streams is frozen separately from the CLIENT's.** The internal lock call's STDOUT alone is captured, because it is the nonce; **its STDERR is forwarded UNCHANGED to the wrapper's own stderr.** Without this the lock can implement every visibility rule correctly and the wrapper can silently discard the evidence, and the existing contention test — exit 3 plus a non-invoked stub — passes either way. This is the composition failure the direct-tool oracles structurally cannot catch, so it needs caller-boundary oracles of its own.

- [ ] **Step 1: Write the failing tests.** Lock acquired before any credential read and released in a `finally` only when acquired; refuses when held by a live DIFFERENT owner with exit 3 and the stub recording NO invocation; **that same LIVE-holder contention surfaces the lock's EXACT holder diagnostic on the wrapper's stderr**; **a DEAD-holder reclaim surfaces the lock's EXACT reclaim diagnostic while the wrapper otherwise succeeds**; **the ACL asserted DECISIVELY on BOTH protected directories** — the lane home and its `credentials` child — comparing the exact ACE set, the inheritance flags and the propagation flags, not merely that some rule exists, since "the ACL is asserted" passes against a non-inheritable ACE; a second run leaves both byte-equivalent, proving idempotence; and **a fake credential created by the client under that directory carries the intended current-SID access**, which is what proves the inheritance actually reached the file rather than only the parent; **environment restoration asserted INSIDE the same shell** by a wrapper script that invokes the tool then prints `KIMI_CODE_HOME`, covering previously-set and previously-unset; never references `~/.kimi-code/credentials` and leaves a planted fake user credential byte-identical; existing-`ok` without `-Force` exits 0 with the stub not invoked; client exit 0 leaving `absent`, `unreadable` or `malformed` each fail with 6; `-VerdictOut` contains exactly one parseable JSON line; one test per exit code.

  **The stream-inheritance oracle must be TEMPORAL.** A wrapper that captured both streams and replayed them after the child exited would pass a mere both-streams-emitted check. So: the stub writes a distinct readiness marker to stdout AND a different one to stderr, then BLOCKS. The parent must OBSERVE BOTH MARKERS BEFORE the stub is allowed to finish, and neither marker may appear in `-VerdictOut`.
- [ ] **Step 2: Write the script.**
- [ ] **Step 3: Verify, per host:**
```
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_kimi_lane_login.py -q
$env:PARALLAX_PS_HOST = "pwsh.exe";       python -m pytest evals/multi-model-verify/test_kimi_lane_login.py -q
```

---

### Task 6: The builder stops copying

**Files:** modify `tools/new-kimi-lane-home.ps1` (credential source `:231-236`, the copy `:410-414`, new parameters, lock handling, and the fault seam's position) and `evals/multi-model-verify/test_kimi_lane_home.py` (tests only; its selector and module guard belong to Task 2).

**Added parameters, all MANDATORY `[string]` in BOTH modes:** `-LaneHome`, `-DebateId`, `-OwnerPid`, `-OwnerStartTicksUtc`. `-Nonce` is additionally MANDATORY on Remove. This matches the exact lifecycle invocation written into the contract in Task 9.

**Nonce custody, frozen.** Build's success output becomes exactly one line of JSON with exactly these two keys and no others:

```
{"debateHome":"<resolved path>","nonce":"<32 hex>"}
```

**The lock tool's STDOUT is captured** — it is the nonce, and capturing it is what stops it contaminating the custody line. **Its STDERR is FORWARDED UNCHANGED to the builder's own stderr.** An earlier wording said all internal lock output is captured, full stop, which would have let the lock implement every visibility rule correctly while the builder silently swallowed the evidence, with the custody JSON still perfectly correct and every existing test still green. **Remove's stdout stays exactly `removed <path>`**, the one line it prints today at `:131-133`, with the internal lock's stdout captured and its stderr forwarded the same way.

Two integration oracles for that boundary, which the lock tool's own tests cannot prove: a build that RECLAIMS a dead holder succeeds, emits the exact reclaim line on stderr, and leaves stdout exactly the custody JSON; a build that CONTENDS with a live holder fails, emits the exact holder line on stderr, and writes nothing to stdout.

**FIRST USE, when the ENTIRE lane home is absent — one bounded, read-only, fail-closed pre-lock probe.** Before anything else, measure the configured lane-home path. **The probe has FOUR reachable outcomes, not two**, and treating either of the last two as "absent" would print a command that cannot fix the obstruction, which contradicts the recovery command's whole contract at `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:135-142`:

| Outcome | Behaviour |
|---|---|
| successfully measured as NONEXISTENT | emit the exact shared lane login recovery command, exit nonzero |
| a DIRECTORY | proceed to Acquire, normal order below |
| exists but is NOT a directory | refuse nonzero, emit NO recovery command |
| existence or type CANNOT be measured | fail closed, refuse nonzero, emit NO recovery command |

**The recovery row and the TWO REFUSAL rows create nothing and never invoke the lock tool. The DIRECTORY row alone proceeds to the normal build order.** An earlier wording said "the last three rows", which swept the directory row in with the refusals and contradicted the table one line above it. The probe itself only READS.

**The probe's fault seam is named: `PARALLAX_LANE_HOME_DIRECTORY_PROBE_FAULT`.** Build mode only; **activated by ANY NONEMPTY value**; fires immediately BEFORE the real probe; simulates the UNMEASURABLE row; **exits 6**, which the table's "refuse nonzero" left open; produces no stdout and no recovery command, no mutation, and no lock invocation; and writes exactly `PARALLAX_LANE_HOME_DIRECTORY_PROBE_FAULT injected: simulated lane-home directory probe failure` to stderr. Naming the VARIABLE while leaving the SENTENCE to invention is the same gap one step smaller: both strings are shared between production and the test, so both are frozen here.

Two oracles beyond the recovery case: a regular FILE sitting at the lane-home path refuses with no recovery command and no lock invocation, and the seam above produces the unmeasurable row with the same prohibitions. The fault is a seam rather than a real permission denial, because machine ACL behaviour is not a thing a test may depend on.

This exists because Task 5's login wrapper is the only thing that creates the lane home, and it creates it BEFORE acquiring. Task 6 acquires first, and Task 3's missing-file protocol creates the lock FILE while giving no rule for creating its absent parent DIRECTORY. So before any login has ever run, Build would fail inside Acquire, before reaching credential validation, and never emit the recovery command that an unusable credential is required to print. The user's very first debate would fail with a lock error instead of instructions.

**Build order, frozen** once the lane home exists. Lock FIRST, because a login can otherwise mutate the shared credential between validation and acquisition. An absent `credentials` directory or an absent credential FILE is then measured UNDER the lock, exactly as now — the pre-lock test is about the lane home directory and nothing else.

Both directions are tested: an entirely absent lane home refuses with the complete recovery command, mutates nothing, and never invokes the lock tool; an EXISTING lane home with an absent credential acquires, validates `absent`, emits the same command, and releases.

1. Validate parameters. 2. ACQUIRE, with **`-DebateHome` set to the resolved `-Path`**; set `$lockAcquired` on success. 3. Validate the lane credential via `tools/read-kimi-credential-state.ps1`, **resolved through `$PSScriptRoot`** and accepted only under the four-part rule in `Fixed names and values`. **A VALIDATOR FAILURE is not one of the three actionable states**: it exits 6, emits NO login recovery command — nothing was measured, so nothing can be recommended — performs no build work after validation, runs failed-build cleanup, and RELEASES the acquired lock, with no custody JSON, no retained lock and no credential value in any diagnostic. The same two opposing oracles as Task 5: nonzero carrying valid-looking status output, and exit 0 carrying invalid output, neither read as a credential state. 4. Every existing gate, unchanged. 5. Create, junction, render. 6. Construct AND EMIT the custody JSON line. 7. **Only now set `$buildCompleted`.**

**`$buildCompleted` is set only after the success line is emitted, and JSON construction and emission stay INSIDE the guarded `try`.** Setting it after rendering, as r4 did, means a failure to construct or write that line leaves the flag true, the `finally` skips the release, and the lock is retained by a caller who never received the nonce it needs to release it. That is an unreleasable lane. Any failure before the line is out runs failed-build cleanup and releases.

**MOVE the existing `PARALLAX_LANE_HOME_FAULT` seam** from its current post-credential position at `tools/new-kimi-lane-home.ps1:416-423` to fire immediately AFTER custody JSON construction and immediately BEFORE emission. **Its SENTENCE moves with it**: the shipped text at `tools/new-kimi-lane-home.ps1:423` reads `PARALLAX_LANE_HOME_FAULT injected: simulated post-credential-copy failure`, and after Task 6 there IS no credential copy, so leaving it would name a step this plan deletes. It becomes `PARALLAX_LANE_HOME_FAULT injected: simulated pre-emission failure`, and the test asserts that literal. That placement is the whole oracle for the boundary above: a pre-render fault cannot distinguish an implementation that sets `$buildCompleted` after rendering from one that sets it after emission. Its test requires NO stdout, the home cleaned up, and the persistent lock record exactly `free`.

**Cleanup needs TWO flags.** The `finally` releases only when `$lockAcquired -and -not $buildCompleted`. One flag is not enough: `-not $buildCompleted` is also true when acquire itself failed, and releasing then would release a lock this call never took. If the failure cleanup cannot itself release, the ORIGINAL failure is what the script reports and the release failure goes to stderr only; a cleanup error never masks the error that caused the cleanup.

**Remove order, frozen.** Identity check BEFORE deletion.

1. Verify the caller's complete identity by an idempotent `-Acquire -Nonce`, with **`-DebateHome` set to the same resolved `-Path`** build used, which is what makes a wrong `-Path` exit 2 at the lock. A mismatch exits nonzero and leaves BOTH the home and the lock byte-identical. 2. The existing sentinel and dangerous-root guards. **If any refuses, no deletion occurs and the pre-existing held lock REMAINS HELD** — the caller still owns the debate. 3. Delete the home. 4. Release.

**THE DELETION ITSELF CAN FAIL, and nothing covered that.** The plan had rows for identity refusal, sentinel refusal, successful deletion and post-deletion release failure — every state except the deletion not working. It matters because `tools/new-kimi-lane-home.ps1:131-133` calls `Remove-Item` NON-TERMINATINGLY and prints `removed <path>` on the very next line, so a failed deletion today still prints success and exits 0, and the failed-build cleanup at `:482-489` deletes with no frozen error boundary either.

- **Remove mode** uses TERMINATING deletion and then VERIFIES the path is absent before releasing. **The verification has THREE outcomes, not two.** Absent: proceed. Still present: failure. **UNMEASURABLE — the absence check itself failed — is ALSO failure**, because reading it as absence would release the lock and print success on the strength of a measurement never taken, which is this plan's governing invariant exactly. Every failing outcome is PRIMARY: no `removed` line, NO release, and the held record left byte-identical. Its seam is `PARALLAX_LANE_HOME_REMOVE_VERIFY_FAULT`, Remove mode only, activated by any NONEMPTY value, firing AFTER deletion and BEFORE verification, exit 6, writing exactly `PARALLAX_LANE_HOME_REMOVE_VERIFY_FAULT injected: simulated post-delete verification failure` to stderr and nothing to stdout, ending with the home ABSENT and the held record byte-identical, with a direct release used only in teardown.
- **The deletion-failure oracle is real rather than seamed** — an exclusively opened file beneath the debate home, under both hosts — requiring nonzero, the home still present, no success line, and the lock still held. **Its teardown is frozen**, because a partial deletion may have removed the sentinel and ordinary `-Remove` is then not a valid path back: close the handle, release DIRECTLY using the retained identity, then delete the disposable remainder outside the behaviour under test.
- **Failed-build cleanup** keeps the ORIGINAL build failure as primary even when its deletion fails, still ATTEMPTS the release, reports the cleanup error on stderr only, and leaves the lock `free` when that release succeeds. Its seam is `PARALLAX_LANE_HOME_CLEANUP_DELETE_FAULT`, Build mode only, activated by any NONEMPTY value, firing immediately before the cleanup deletion, which it SKIPS, writing exactly `PARALLAX_LANE_HOME_CLEANUP_DELETE_FAULT injected: simulated cleanup deletion failure` to stderr; the original build failure's code is what the script returns, the debate home remains on disk, and the lock ends `free`.

**Remove's own failure precedence, frozen.** A release that fails AFTER the deletion succeeded is reported as the failure and exits with the lock tool's code; the `removed <path>` line is printed only when BOTH the deletion and the release succeeded, so that line never reports a removal whose lock is still held. Build mode's precedence rule does not cover this path and r12 left it to inference.

**The junction oracle.** Three assertions, all required, each failing hard if its own measurement cannot be taken:

- **File identity is primary.** Open both credential paths and compare the full NTFS file identity, not a textual resolved path.
- **Write-through is required.** Mutate the obviously-fake lane fixture and observe the new bytes through the debate path in the same test.
- **A non-following physical inventory.** Enumerate the debate home WITHOUT traversing reparse points and assert no standalone credential file exists beneath it. The first two both pass on a correct junction that ALSO has a stray copy.

- [ ] **Step 1: Write the failing tests.** The three junction assertions; stdout is exactly one JSON line with exactly `debateHome` and `nonce`, and removal uses the RETURNED nonce rather than reading the lock file; the credential source is the LANE home and a planted differing user credential is never read; absent, unreadable and malformed lane credentials each refuse with **THE LANE LOGIN RECOVERY COMMAND FROM `Fixed names and values`, asserted whole** — the spec requires "the exact command that fixes it" at `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:140-141`, and a message that merely NAMES the wrapper is not a command a user can run, since the wrapper's owner fields are mandatory; acquire precedes validation and releases on every later refusal; **a successful build RETAINS the lock**; **a failure to emit the custody line runs cleanup and RELEASES**, proven by firing the relocated `PARALLAX_LANE_HOME_FAULT` seam at its new position between construction and emission, and asserting no stdout, the home gone, and the lock exactly `free`; **an acquire failure does NOT attempt a release**, proven with a REAL held-by-a-different-owner fixture rather than an invented seam, which is the stronger oracle; **a successful remove leaves the home ABSENT and the lock record exactly `free`** — without this, deletion-without-release passes; a cleanup-release fault seam named exactly `PARALLAX_LANE_HOME_CLEANUP_RELEASE_FAULT`, firing only after an original build failure and immediately before the cleanup release, **which when nonempty SKIPS the lock mutation entirely and produces a simulated release result of code 5, leaving the record still HELD, and writes exactly `PARALLAX_LANE_HOME_CLEANUP_RELEASE_FAULT injected: simulated cleanup release refusal` to stderr** — the mechanism and end state are frozen for the same reason the Remove seam's are, because "the release failed" has two different end states and the test must assert one of them — proves the original failure stays primary while the release failure appears only on stderr, with the record's still-held state asserted and a direct release performed as teardown; remove's identity mismatch leaves home and lock byte-identical; **the WRONG-`-Path` case has its own integration oracle, because Task 3 now excludes `debateHome` from identity and "identity mismatch" no longer covers it**: **by this exact setup and teardown**, which is deterministic and uses only the real builder — "prepare a distinct valid home by hand" still left its construction to invention, and building B while A holds the lock would contend and never reach the case at all: (1) build B normally and capture its nonce; (2) directly `-Release` B's lock, leaving B on disk; (3) build A normally, retaining A's hold; (4) call `-Remove` on B carrying A's complete identity and A's nonce; (5) require exit 2 and byte-identical A, B and lock; (6) tear down by removing A normally, then acquiring a fresh hold for B and removing B normally; **the post-deletion release failure has a failure-capable oracle**, through a seam named exactly `PARALLAX_LANE_HOME_REMOVE_RELEASE_FAULT` — the other two seams are given exact shared names because production and tests must agree on the string, and leaving this one unnamed left that agreement to invention — honored ONLY in Remove mode, firing immediately after a successful deletion and immediately before the release; when nonempty it SKIPS the lock mutation entirely and produces a simulated release result of code 5, writing exactly `PARALLAX_LANE_HOME_REMOVE_RELEASE_FAULT injected: simulated post-delete release refusal` to stderr and nothing to stdout; the test requires the home ABSENT, the original held record UNCHANGED, exit 5, that sentinel on stderr, and NO `removed <path>` on stdout, with a direct release performed as teardown — Task 7's matrix exercises the pre-deletion sentinel refusal and never reaches this branch; a sentinel or dangerous-root refusal after the identity check leaves home and lock unchanged; `-Remove` does not delete through the junction; the failed-build cleanup at `:482-489` does not either; every existing test still passes.
- [ ] **Step 1b: The recovery command is EXECUTED, not just compared.** Asserting the emitted string whole is NOT an adequate oracle for a command whose whole job is to run: the earlier broken semicolon form, which called the login wrapper after a failed owner resolution, would have satisfied a string comparison perfectly. So take the string the builder ACTUALLY EMITTED and RUN it, under BOTH hosts.

  **THREE boundaries was itself an under-count; there are NINE reachable rows.** An earlier version listed owner-exit, JSON parse and login-exit, which left owner LAUNCH failure, output cardinality, owner SCHEMA, and the environment the command reads all unexercised — and the parse row asserted "never invoked" while the shipped command actually invoked the login with a null identity. Every row BEFORE the login launch must assert the login was NEVER invoked, by marker absence, not merely that the command exited nonzero.

  | # | Injected condition | Required |
  |---|---|---|
  | 1 | owner command fails to LAUNCH | nonzero; login never invoked |
  | 2 | owner command exits nonzero | nonzero; login never invoked |
  | 3 | owner stdout is zero lines, or several | nonzero; login never invoked |
  | 4 | owner stdout is malformed JSON | nonzero; login never invoked; NO verdict; no credential mutation |
  | 5 | owner JSON is valid but the wrong shape — not an object, wrong property set, wrong pid type or a pid <= 0, wrong ticks type or ticks failing `\A[0-9]+\z` | nonzero; login never invoked |
  | 6 | `TEMP` missing or not a directory, and separately a forced `Join-Path` failure | nonzero; login never invoked |
  | 7 | login fails to LAUNCH | nonzero |
  | 8 | login exits nonzero | nonzero; NO `ok` verdict |
  | 9 | full success | exits zero; `ok` verdict; a structurally valid fake credential |

  **The escaping needs its own failure direction.** Every row can use an ordinary path, which would let an implementation that never doubles apostrophes pass all of them. So the SUCCESS row uses a resolved lane home containing **BOTH AN APOSTROPHE AND A SPACE IN THE SAME PATH SEGMENT**, and requires that the emitted command contains the DOUBLED apostrophe, that it writes only to the intended lane home, and that the credential is structurally `ok`. Both characters, because the apostrophe alone exercises the template's escaping while the space exercises the callers' `Start-Process` argument quoting, and an earlier fixture deliberately avoided combining them — its docstring named the mis-tokenization as pre-existing and the suite stayed green over it. **A fixture may not be shaped to avoid a defect in code it drives.**

  **Fixture routing, frozen, so no judgment remains:** execute from a disposable current directory containing a `tools/` directory. For the first three rows, place the specified owner and login stubs there and use invocation-marker files. For the success row, copy the real lock tool, login wrapper and validator into that disposable `tools/`, and provide the fake client under a disposable `USERPROFILE`. In every row, execute the exact line extracted from the builder's refusal. No row touches a real credential or the real user profile.
- [ ] **Step 2:** The host-selector refactor and the module guard were moved into Task 2 step 3b, because Task 2's own fixture change had no oracle without them. Confirm they are in place; do not repeat them.
- [ ] **Step 3: Modify the builder,** keeping every existing gate.
- [ ] **Step 4: Verify, per host:**
```
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_kimi_lane_home.py -q
$env:PARALLAX_PS_HOST = "pwsh.exe";       python -m pytest evals/multi-model-verify/test_kimi_lane_home.py -q
```

---

### Task 7: Live gates for the junction and credential facts

**Files:** create `evals/tools/lane_credential_live_support.py` (the shared production helper), `evals/multi-model-verify/test_lane_credential_live.py`, and `evals/multi-model-verify/test_lane_credential_live_support.py`.

**The helper lives in its own non-test module**, `evals/tools/lane_credential_live_support.py`, and BOTH test modules import it. It performs NO live-environment check at import time, so the offline support suite does not drag live setup in. Leaving it inside the opt-in live module, as r7 implied, would have done exactly that; leaving it unnamed would have made the import boundary the implementer's invention.

**Three homes, three roles.** `PARALLAX_LANE_LIVE_HOME_A` and `_B` are the coexistence pair; `_C` is the EXPENDABLE mutation fixture and **the only home the suite DELIBERATELY expires and requires to rotate**. That is narrower than r5's "the only home any test rotates", which was wrong: A and B perform authenticated dispatches, access tokens expire in 900 seconds (measurement 1), and a dispatch can therefore refresh them on its own. A and B may refresh NATURALLY, but only while locked. The suite never creates a login and never touches `~/.kimi-code`. Any variable unset, or any home lacking a structurally `ok` credential, FAILS the suite with a message naming `tools/new-kimi-lane-login.ps1`.

**The marker contract, frozen.** The documented manual setup runs the login wrapper for A, writes A's marker, then for B, writes B's. The marker is a file named exactly `.parallax-login-created-ticks-utc` in the home's root, ASCII, containing exactly one line: the UTC tick count as decimal digits, matching `\A[0-9]+\z`. The gate requires A's value to be strictly less than B's; a missing, empty or non-matching marker FAILS the suite.

**The manual setup sequence, frozen and executable.** It is performed once, by hand, before the suite runs. It cannot borrow the module's owner, because `-ResolveOwner` runs once per MODULE RUN and setup happens earlier. For A, then for B:

1. Run `tools/kimi-lane-lock.ps1 -ResolveOwner` in THAT setup shell, directly, and keep its two values for the rest of this setup.
2. Run `tools/new-kimi-lane-login.ps1 -LaneHome <home> -OwnerPid <pid> -OwnerStartTicksUtc <ticks> -VerdictOut <path>` and require the verdict `ok`.
3. Generate a fresh setup debate id, 32 lowercase hex.
4. Acquire that home's lock with the home as BOTH `-LaneHome` and `-DebateHome`; capture the nonce.
5. Write the ASCII marker.
6. Release with the complete identity.

A's tick must be strictly below B's, which the ordering of these two runs is what produces.

**C is created third, by steps 1 through 4 and 6, EXPLICITLY OMITTING step 5.** Step 5 is the marker write, so "the same six steps while writing no marker" was an instruction that contradicted itself. Only A and B are ordered against each other, so only they need a marker; C is the mutation fixture and nothing compares its creation time. r12 wrote the sequence as "for A, then for B" while also requiring C to carry a structurally `ok` credential, leaving C's creation to inference.

**Three coexisting lane logins plus the user's own is a GENERALIZATION of measurement 11, which established two.** The fail direction is safe and loud: if a third login cannot coexist, setup produces a home without an `ok` credential and the suite REFUSES rather than running degraded. Recorded here so the assumption is visible rather than buried in a fixture.

**The fixture routing table.** Every live item names its homes; r6 assigned only items 3 and 7.

| Item | Lane home | Debate home | Custody |
|---|---|---|---|
| 1 absolute-key, and its control | C | fresh builder-created | build holds C; `-Remove` releases |
| 2 junction read-through | C | fresh builder-created | build holds C; `-Remove` releases |
| 3 refresh write-through | C | fresh builder-created | build holds C; `-Remove` releases |
| 4a delete path, SUCCESSFUL build | C | fresh builder-created | build holds C; the real `-Remove` releases |
| 4b delete path, FAILED build | C | fresh builder-created | the builder's own internal cleanup releases; no nonce is returned and `-Remove` is never called |
| 5 coexistence | A and B | fresh builder-created per dispatch | build holds the dispatching home; `-Remove` releases |
| 6 `provider list` false positives | isolated disposable homes carrying a structurally valid FAKE credential, a garbage one, and no credential file | not applicable | NONE: no real credential exists to protect |
| 7 `provider list` is not a refresh path | C | fresh builder-created | build holds C; `-Remove` releases |

**The coexistence claim, narrowed to what a pre-provisioned fixture supports.** A pytest suite handed existing homes cannot observe the creation event. The gate asserts A's marker precedes B's, then dispatches A, then B, then A again, all requiring exit 0. **Its claim is "A remains usable after B was created", not "the creation of B was observed to be harmless"**, and the test docstring says exactly that.

**Locking is PER HOME, and THE BUILDER IS THE ACQUISITION.** Call `tools/kimi-lane-lock.ps1 -ResolveOwner` ONCE per module run and use one per-home debate id.

For every case that uses a builder-created debate home, **do NOT acquire separately and do NOT plainly release.** A successful build already holds that lane's lock and returns its nonce, and Task 6 deliberately stops a successful build from releasing it. A second acquire would CONTEND against that retained hold, and a plain release would then make Task 6's identity-confirming `-Remove` fail. So:

1. Pass the module owner and that home's debate id to `tools/new-kimi-lane-home.ps1`; the build acquires.
2. **Set `custodyReceived` ONLY after Build exits 0 AND its exact JSON line parses.** Retain the nonce.
3. **The PRE-COMMAND phase**, which exists only for `custodyReceived`: every deliberate credential mutation happens HERE, under builder custody, together with the pre-command hashes. Items 3 and 7 force expiry, and without this phase an implementation could force it BEFORE the build, mutating a shared credential unlocked, and still pass every functional assertion.
4. Run the command under that EXISTING hold.
5. Merge new credential values and run the stream guard while the hold is still in force.
6. In a `finally`, call the real `-Remove` with that nonce, which releases.

**Steps 3 through 6 run ONLY when `custodyReceived`.** A refused or failed Build returns no nonce and Task 6 already owns its own cleanup and release, so on that path invoke NEITHER the command NOR `-Remove`, and preserve the Build failure as the reported error. r7's blanket "`finally` always calls `-Remove`" would have called it with no nonce, against a lock the builder had already freed.

**The MAIN OPERATION is all four phases inside custody**, not just the command: the pre-command phase, the command and its capture, the post-command re-read and merge, and the stream guard. Naming only the command left three phases where a runner could skip `-Remove` or let a removal failure mask the real one.

**Cleanup coverage, frozen:** a failure in any main phase still ATTEMPTS the real `-Remove`. When Remove succeeds, the debate home is ABSENT and the lock is exactly `free`; when Remove fails, the required report and filesystem state are those in the support matrix below.

**Cleanup precedence, frozen:** a failure from ANY main phase stays PRIMARY even when `-Remove` also fails; a `-Remove` failure is primary only when every main phase succeeded.

**The same precedence governs seeding:** a seed-read failure stays primary if the release also fails, and a release failure is primary only after a successful seed read.

**A and B's setup markers are written under their own locks** by the manual setup below, which is a separate lifecycle because it precedes any build.

Freezing only C's custody, as r5 did, left every A and B dispatch able to refresh a shared credential outside the lock this suite exists to respect.

**The absolute-key case is a THREE-STATE STRUCTURAL oracle, and NOTHING about the message text is pinned. Frozen at r33, replacing the r31 pin protocol entirely.**

Two things were wrong at once, and the live run exposed both.

The old oracle could not fail. It built the absolute key as `str(cred_path.resolve())`, and `Path.resolve()` FOLLOWS A JUNCTION on Windows (measured: an unresolved `link/f.json` resolves to `real/f.json`). So the "absolute" key named the same credential file the relative default already reached through the junction, and exit 0 with `PROBE` was produced identically by "the absolute key resolved" and by "it was ignored and the default was used". The case established measurement 5 in neither direction.

The pin could not be stable. The client's stderr carries a MODEL-GENERATED summary line, different words each run, and a FRESH session id. The frozen normalization removes neither, so "the COMPLETE normalized stderr" is unachievable for this command and no amount of re-running fixes it.

And the two hid each other: the gate compared the tuples for stability BEFORE checking whether the supposedly-failing case had exited 0, so "the absolute key unexpectedly SUCCEEDED" was reported as mere stream instability. The graver fact was masked by the trivial one. **Wherever both a classification and a stability check exist, the CLASSIFICATION is evaluated first.**

So item 1 becomes five steps, all under C's builder-retained hold, with the strict merge callback and the stream guard applied throughout. No second credential copy is created; C's real credential is used in place.

1. The relative-key positive control: exit 0 and stdout contains `PROBE`.
2. **Make the default UNREACHABLE.** Rename the `credentials` junction to a non-default name, then PROVE `<debate-home>/credentials/kimi-code.json` is absent while C's real credential is still readable.
3. **The missing-absolute negative control.** Set `oauth.key` to a NONEXISTENT absolute path: require nonzero and no `PROBE`. This is load-bearing — without it, removing the default and testing one absolute path cannot distinguish "absolute paths are unsupported" from unrelated fallback behaviour.
4. Set `oauth.key` to the absolute path of C's REAL credential file. Run TWICE. Both must exit nonzero and neither may contain `PROBE`. Either success REFUTES measurement 5, and that is the finding, not a test failure to work around.
5. C's credential stays measurable and guarded after every command.

**What is pinned and what is not.** Zero versus nonzero, and the presence or absence of `PROBE`. NOT the exact numeric exit code, which is wider than the design requires; not stdout or stderr text; not the session id; not the model's summary line. `docs/superpowers/plans/rounds/2026-08-01-cred-lock/probe-record.md`, the refresh opt-in `PARALLAX_LANE_PROBE_RECORD_REFRESH`, the stability comparison and every oracle built for them are DELETED rather than left standing beside the replacement, because a dead pin reads as a live one.
**The live homes are SAFETY-CHECKED before any seed or mutation, frozen at r31.** Checking only "is a directory with an `ok` credential" let the suite's own deliberate expiry land on the user's real home if a variable were mistyped, which is the exact defect this plan exists to remove, reintroduced through the fixture routing. Before anything is seeded or mutated, FAIL unless every one of these MEASUREMENTS SUCCEEDS and passes:

- A, B and C resolve to three pairwise-distinct PHYSICAL directories, compared after full resolution so a case-only difference or a junction alias does not read as distinct;
- none resolves to a drive root, and none resolves to the real `USERPROFILE`;
- none equals or resolves beneath the real `USERPROFILE\.kimi-code`.

A measurement that cannot be made is a failure, never a pass. Offline fixtures cover C aliasing A, a case-only alias, a junction alias, a drive root, the profile root, and the ordinary `.kimi-code` tree.

**The post-command credential merge happens INSIDE the capture helper, before any stream can be returned or rendered. Frozen at r31, SECURITY.** Scanning only the pre-command secret set and then returning the streams means a token ISSUED BY the command being scanned is not in the set when the scan runs, so pytest assertion output can print it. Capture, the locked post-command credential re-read and merge, the stream scan, and the return are ONE indivisible helper operation. The helper takes the credential path or a locked merge callback. The same order governs a timeout's partial streams. If the re-read fails, NO captured stream is exposed and the sanitized read failure is raised. The offline oracle is ONE fake command that writes a new credential value and emits THAT SAME new value in the same invocation; a command that merely echoes a pre-written value does not reach this path.

**A cleanup call that THROWS may not mask the main failure. Frozen at r31.** A `finally` that invokes the remover directly loses the saved main exception when the remover itself raises on a launch failure or a timeout, which contradicts the frozen precedence above. Capture cleanup invocation exceptions separately, rethrow the main failure first, and report the cleanup failure only when every main phase succeeded. The same applies to the seed's release. The oracles cover the THROWN timeout and launch-failure directions, not only nonzero returns, and the simultaneous-refusal case is parameterized across all four main phases rather than reaching only command launch failure.

**One debate id PER HOME for the whole module run, not per operation.** `{A, B, C} -> debateId` is resolved once and used for seeding and for every later operation against that home.

**Item 6's disposable homes get a MINIMAL GENERATED config, never a copy of the user's real `config.toml`.** It carries only the non-secret managed Kimi provider and OAuth declaration `provider list` needs; the builder's own provider block is already explicit and credential-free. Item 6 also runs its positive control, the structurally valid FAKE credential the routing table names, before the garbage and absent cases.

**SECRET GUARD — one helper, applied to EVERY live command.** It was once scoped to the probe record alone, which was too narrow twice over: other live commands capture client streams as well, and an ordinary pytest failure message can print a captured stream BEFORE any write-time guard runs. The probe record itself is gone as of r33; the helper's scope is unchanged and is now simply every live command.

So: one helper inspects both captured streams against a RETAINED UNION of **every NONEMPTY credential string value** across every fixture home, and it runs BEFORE any assertion or failure message that could surface those streams. On a match it fails naming ONLY the field.

**Two fields are EXCLUDED by name, and this is a security decision rather than a helper constant. Frozen at r33.**

```python
NON_SECRET_CREDENTIAL_FIELDS = frozenset({"scope", "token_type"})
```

The nonempty restriction was written because "an empty string is a substring of every output". That reasoned about the EMPTY case and missed the SHORT one. Measured live: `scope` is a NINE-character value and a literal substring of ordinary `provider list` output, so the guard fired on a completely clean run and failed four of twelve live tests. `access_token` and `refresh_token` measured 677 and 678 characters and matched nothing.

`scope` and `token_type` are RFC 6749 response METADATA, not secrets. The exclusion is by FIELD NAME at merge time, and it is deliberately not a length or entropy threshold, because a threshold would silently stop protecting a short secret.

The rules, all four:

- those two fields never enter the retained union;
- `access_token` and `refresh_token` always do;
- **every unknown future string field still does**, so the fail-safe direction is preserved for anything not yet seen — this is an exclusion list, never an allowlist of secrets, because an allowlist inverts that direction;
- if a metadata field and a secret field hold the SAME value, the secret field still causes retention and detection.

Four oracles, one per rule: metadata in ordinary output does not fire; each token field fires independently; an unknown string field fires; a token sharing its value with excluded metadata still fires.

**Captured output is decoded as STRICT UTF-8, never the locale. Frozen at r33.** The capture used `text=True` with no encoding while the timeout path decoded bytes as UTF-8 with replacement, so the two paths did not share one byte-to-text contract, and the live run's captured output arrived mojibaked. This is not cosmetic: credentials are read as UTF-8, so a non-ASCII secret decoded through a different or lossy codec may not compare equal to itself, and the guard's claim covers every retained string rather than ASCII tokens only. Capture BYTES, decode both paths through one strict helper, and on invalid UTF-8 raise a fixed value-free `DispatchDecodeFailure` exposing NEITHER stream. Oracles: an invalid-byte normal path, an invalid-byte timeout path, and a correctly encoded NON-ASCII fake secret that must still be caught.

**The secret set's lifecycle, frozen, because a set built once is already stale.** C deliberately rotates, so a value ISSUED BY the command being scanned does not exist when that command starts:

- **Seed the union BEFORE any live command, through the one DIRECT-ACQUIRE exception to builder custody.** No build has run yet at that point, so there is no hold to borrow. For A, then B, then C: acquire with the module owner and that home as BOTH `-LaneHome` and `-DebateHome`, read and merge, then release with the captured nonce in a `finally`. **This is the ONLY place in the suite that acquires directly**; everywhere else the builder is the acquisition.
- **Item 6's disposable homes are the exception to the exception: their values are loaded and merged WITHOUT any lock**, because those homes are isolated, disposable, and contain no real shared credential. All values, locked and unlocked alike, still pass through the same stream guard.
- **After every command against A, B or C — the builder-custodied homes — and while that home's hold is STILL IN FORCE, re-read the home and MERGE any new values into the union before scanning the streams.** Item 6's disposable homes are re-read and merged after their command WITHOUT a lock, because they never had a hold to keep in force; the same stream guard then runs over their output unchanged.
- **Never discard an old value.** A rotated-away token is still a secret that must not be printed.

**The helper owns process capture**, so nothing can render a stream before the guard runs: it invokes the command without raising, and it sanitizes the timeout, launch-failure and error paths too, since those are exactly the paths a test framework prints captured output on.

**Token-rotation assertions must not disclose.** `assert $before -ne $after` on token values prints BOTH operands through pytest's assertion introspection on failure, into a log that may be pasted anywhere. Compare through an ordinary `if` and call `pytest.fail("access_token did not rotate")`, or the refresh-token equivalent. Neither value may appear in an assert expression or a failure message.

- [ ] **Step 1: Write the gate.** Each item begins with a POSITIVE CONTROL.

1. **Absolute `oauth.key`** (5): the FIVE-STEP three-state structural oracle frozen above at r33 — relative control, default made unreachable, missing-absolute negative control, C's real absolute path twice, credential still measurable. **The home is built normally and its `config.toml` is hand-edited in the throwaway copy** to replace the rendered `key = "oauth/kimi-code"`. The builder renders only the relative form (`tools/new-kimi-lane-home.ps1:456`) and gains no parameter for this; the edit is confined to the disposable home and never touches a real one. The absolute path is taken WITHOUT `Path.resolve()`, which follows the junction and was what made the old oracle undiscriminating.
2. **Junction read-through** (6): a dispatch through a junctioned credentials directory exits 0 and returns `PROBE`.
3. **Refresh write-through** (7), on C: force expiry IN THE PRE-COMMAND PHASE, dispatch, require exit 0 AND `PROBE`, then assert C's token fields rotated and no second credential file exists anywhere under the debate home.
4. **Both delete paths** (10): invoke the real `-Remove` and the real failed-build cleanup HERE, directly. This module's verification command runs only this module, so delegating the assertion elsewhere would assert nothing.
5. **Coexistence** (11), as narrowed above.
6. **`provider list` false positives** (16): garbage credential and absent credential file, each requiring exit 0 and each reporting `source=oauth`.
7. **`provider list` is not a refresh path** (17), on C: force expiry IN THE PRE-COMMAND PHASE and take the pre-command snapshot there, run it, require exit 0 AND the expected provider line, THEN assert byte-identity by SHA-256, length and mtime. **Every snapshot component must have been MEASURED SUCCESSFULLY before any comparison happens.** Requiring the command to succeed does not make the MEASUREMENTS succeed: two suppressed hash failures compare equal as empty strings or as `None`, which is exactly the shape measurement 17 produced on its first attempt, where a clean verdict came from two empty strings comparing equal (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:89-95`). So:
   - ONE helper, `measure_file_snapshot`, returns SHA-256, byte length and mtime **only after all three succeed**; any read, hash or stat failure TERMINATES the main phase before equality is ever evaluated.
   - **A failed measurement is never represented by an equality-comparable sentinel.** No empty string, no `None`, no zero.
   - Two offline support oracles force the failures: a pre-command HASH failure and a post-command STAT failure. Each must FAIL, still attempt the real `-Remove`, and follow the existing cleanup-precedence matrix.

**Item 4b must exercise the real DELETION, not merely the release. Frozen at r32.** A hostile `-Model` is refused at `tools/new-kimi-lane-home.ps1:613`, which is inside the main `try` and AFTER the acquire at line 573, so it does prove acquisition and release. It does NOT reach the deletion branch: `$createdByThisInvocation` is set at line 828, long after that refusal, and the recursive cleanup at line 927 is conditional on it. So item 4b is three cases:

1. **`PARALLAX_LANE_HOME_FAULT=1` AND `PARALLAX_LANE_HOME_CLEANUP_DELETE_FAULT=1`.** Require the pre-emission fault, the cleanup-deletion sentinel, the debate home still PRESENT with its junction, and the lock exactly `free`. This is what proves the build reached the post-junction cleanup branch at all.
2. **`PARALLAX_LANE_HOME_FAULT=1` alone.** Require no custody stdout, the debate home ABSENT, the lock exactly `free`, and C's credential BYTE-IDENTICAL. That last clause is what proves the recursive deletion does not traverse the junction.
3. The hostile-`-Model` case is kept only as an optional release-only control, and its docstring says exactly that.

The failed-build test uses the module's debate id for C like every other operation; generating a fresh one there was an incomplete application of the one-id-per-home rule.

**The post-capture merge is a CALLBACK, not a credential path, and item 6 supplies its own. Frozen at r32.** `dispatch_and_guard(..., post_capture_merge=callback)` invokes the callback after capture and BEFORE scanning, on the normal and the timeout path alike; only after the callback SUCCEEDS may the guard scan and the streams be returned. A, B and C pass the strict `reread_and_merge_credential`. Item 6 passes a fixture-specific callback carrying its EXPECTED state:

- `valid` — the read, the parse and the merge must all succeed;
- `garbage` — the read must succeed and the parse must fail AS EXPECTED;
- `absent` — absence must be MEASURED successfully; any other filesystem error fails closed.

A generic lenient mode is forbidden, because `merge_credential_file` returns the same `False` for an unreadable file and for malformed JSON, so a lenient mode would read an unmade measurement as an expected garbage fixture. A plan carve-out letting item 6 merge after its assertions is equally forbidden: the merge-before-guard boundary is a security ordering, and the disposable homes' streams are still scanned against a union holding A, B and C's real values.

The read-failure oracle is repaired with it. It currently calls `dispatch_and_guard` with no credential path and raises the read failure by hand after the helper has already returned, so it exercises the test's own code rather than the helper's promised failure boundary.

Opt-in on `PARALLAX_LANE_LIVE`; module guard `os.name != "nt"`.

- [ ] **Step 1b: Give the locking and the secret guard their OWN oracles, offline.** The seven items above test the CLIENT. None of them proves the runner acquired the intended home's lock, released it afterwards, or caught a credential value in a stream, so a runner with no locking and no helper at all passes every one of them. Create `evals/multi-model-verify/test_lane_credential_live_support.py`, which imports the SAME production helper the live suite uses and drives it against fake commands, with no real credential and no opt-in required:

- pre-hold A's, B's and C's locks individually under a DIFFERENT live owner and prove the BUILD refuses, the fake command is never invoked, **`-Remove` is never attempted, and the pre-held record is byte-identical afterwards**;
- pre-hold a SEED home and prove its credential is never read, and that a successful seed leaves that home's record exactly `free`;
- prove contention is observed against the BUILDER-RETAINED hold **during the PRE-COMMAND phase as well as during the client process**, since a second acquire must contend the whole time custody is held and not only while the client runs;
- prove cleanup after BOTH a zero and a nonzero command exit runs through the real `-Remove`, leaving the debate home ABSENT and the lock record exactly `free`;
- prove cleanup precedence with THIS MATRIX, which replaces the prose bullets rather than adding to them. The r10 wording demanded an impossible end state: a main-phase failure PLUS a `-Remove` failure, while also asserting the home absent and the lock free. Those cannot coexist. A deterministic sentinel or dangerous-root refusal leaves the home PRESENT and the held record unchanged (`tools/new-kimi-lane-home.ps1` remove order, frozen in Task 6), and a release that fails after deletion leaves the lock NOT free, because the release is what would have freed it.

| Main phases | `-Remove` outcome | Required state and report |
|---|---|---|
| pre-command, command/capture, merge or guard FAILS | succeeds | main failure primary; Remove attempted; home ABSENT; lock `free` |
| pre-command, command/capture, merge or guard FAILS | deterministic sentinel refusal | main failure primary; Remove attempted; home PRESENT; the original held record BYTE-IDENTICAL |
| all succeed | deterministic sentinel refusal | Remove failure primary; home PRESENT; the original held record BYTE-IDENTICAL |

  Repair the sentinel and run a normal `-Remove` as test TEARDOWN only, after the failure state has been asserted.

- prove seed precedence with the corresponding three directions, since two cases never showed a release happening after a failing read: a seed-read failure with a SUCCEEDING release reports the SEED failure and leaves the record `free`; a seed-read failure with a FAILING release reports the SEED failure, asserts the release was attempted, and pins the record state the chosen deterministic fault produces; a successful seed read with a failing release reports the RELEASE failure;
- **exercise the three exception paths the helper promises to sanitize, since none of the ordinary cases reaches them.** A fake command that emits a fake credential value and then BLOCKS UNTIL TIMEOUT must produce a field-only failure carrying neither the value nor the captured stream, write no probe record, and still clean up through `-Remove`. A NONEXISTENT EXECUTABLE must produce a sanitized launch failure and still clean up. A post-command credential read-or-parse FAULT must produce a value-free failure and still clean up;
- inject an existing fake credential value into stdout, and separately into stderr, and require the guard to fire on each;
- have a fake command ROTATE a credential and emit the NEW value, proving the merge-after-command rule, which a seed-once implementation fails;
- assert every CREDENTIAL-MATCH failure from the secret guard names ONLY the matched field, contains no value, and writes no probe record. That scoping is required: the launch-failure and read-or-parse cases have no matched field to name, so "every failure names only the field" would contradict the oracles directly above it. The timeout, launch, read-or-parse, phase and cleanup failures each keep their own individually specified sanitized message, and none of them may carry a credential value or a captured stream either.

Its lock cases are PowerShell-facing, so Task 10 adds this module to both Windows steps and to the host-parity required set.

- [ ] **Step 2: Verify, per host, because item 4 claims both:**
```
$env:PARALLAX_LANE_LIVE = "1"
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_lane_credential_live.py evals/multi-model-verify/test_lane_credential_live_support.py -q
$env:PARALLAX_PS_HOST = "pwsh.exe";       python -m pytest evals/multi-model-verify/test_lane_credential_live.py evals/multi-model-verify/test_lane_credential_live_support.py -q
```
Expected: all pass, ZERO skipped. **Both commands collect the support suite**; collecting only the live module would let a broken helper pass this task's own gate and be caught six tasks later.

---

### Task 8: The doctor stops touching credentials

**Files:** modify `commands/doctor.md:151-173` and `evals/multi-model-verify/test_backup_lane.py`.

**Aggregate verdict, a TOTAL order.** Check 8 observes several substates and emits ONE row. Binary absent short-circuits to `N/A`. Otherwise the row is the worst substate by **`BROKEN > STALE > N/A > OK`**, and every substate is still named in the detail text. `N/A` must be IN the order: `commands/doctor.md:6-9` defines it as a real row verdict that never contributes to overall failure, and without it a valid binary plus an absent credential plus a free lock has no defined row.

| Substate | Contribution |
|---|---|
| binary absent | `N/A`, short-circuit, "backup lane unavailable, primary unaffected" |
| **binary present, readable version AT OR ABOVE the floor** | **`OK`** — the CLEAN row, which the table claimed to be total while omitting. `commands/doctor.md:146-156` already treats a present usable version as the non-failure branch, so leaving it out let an implementation map the clean case to `N/A` or emit nothing. Its detail names the successful binary and floor comparison, and it is PINNED, so a wrong mapping fails |
| binary present, version below floor or unreadable | `BROKEN` |
| lane credential `ok` | `OK` — "lane credential structurally present" |
| lane credential `absent` | `N/A`, **and no hash is taken at all**, with the lane login recovery command |
| lane credential `unreadable` or `malformed` | `BROKEN`, with the lane login recovery command |
| the validator itself fails to run | `BROKEN`, **and NO credential recovery command is fabricated**, because no credential state was measured |
| a hash cannot be taken on a PRESENT credential | `BROKEN` |
| the two hashes differ | `BROKEN` — "credential bytes changed during the check; actor not established" |
| lock `free` | `OK` |
| lock `held` and LIVE | `OK`, reported as held with the holder |
| lock `held` and DEAD | `STALE`, reclaimable at the next acquire |
| lock `held`, SAME-HOST, and UNKNOWN | `N/A` — the doctor's own vocabulary for a surface that did not answer. **Same-host is what selects this row**: a foreign-host record also reports `UNKNOWN` liveness, so without that word the two rows overlap on every foreign-host record, and this row's mandated detail describes the same-host mechanism rather than the foreign-host exit-4 path. Report that liveness could NOT be determined and that every mutating mode therefore treats the holder as alive and will not reclaim. It is not `OK`, because an unmade measurement is never a clean one, and not `STALE`, because nothing will reclaim it |
| lock foreign-host — the record's `host` differs from `$env:COMPUTERNAME`, compared case-insensitively, which is the comparison the doctor makes since `-Status` reports the field | `STALE`, with the `-ForceRelease -ConfirmHost ...` command |
| lock MALFORMED | `STALE`, with the `-MalformedOverride -ConfirmSha256 ...` command |
| **lock status cannot be measured** — unreadable lock, missing lock tool, or a status invocation failure | `BROKEN`, and **no recovery command is fabricated from evidence the check does not have** |

**WHICH ROW FIRES IS DECIDED BY THE FOUR-PART ACCEPTANCE RULE, not by the exit code alone.** `ok`, `absent`, `unreadable` and `malformed` are consumed ONLY from a strictly accepted exit-0 report. A process-launch failure, ANY nonzero exit, nonempty stderr, zero or several stdout lines, a JSON parse failure, wrong keys or types, or a status/detail pairing not in Task 2's table all select "the validator itself fails to run" and `BROKEN`. Two fixtures prove the boundary in both directions: a NONZERO exit carrying a valid-looking `absent` report stays `BROKEN`, and an EXIT 0 carrying a valid `absent` report is `N/A`.

**All three credential-failure rows print THE LANE LOGIN RECOVERY COMMAND from `Fixed names and values`, complete and executable, against the configured lane home.** The doctor pins the complete emitted form and needs NO duplicated literal and NO execution suite of its own, because Task 6 executes the same shared command in both directions and there is exactly one command to be wrong. The doctor had recovery commands for both lock overrides and none for the one failure a user can actually fix themselves, while the spec requires the exact fixing command at `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:140-141`. The pin covers the COMPLETE command, not the wrapper's filename, so a message naming only the script fails.

**The hash claim is narrowed.** Two hashes show only that bytes changed during the interval, not WHO changed them. Equal hashes are reported as "no net byte change observed", never as proof that nothing wrote the file.

**Hash procedure, as a seven-step algorithm.** The r4 prose said to confirm readability before hash 1 while also requiring the validator substate to be reported, and a hash-1 failure would then prevent the validator from ever running, leaving that substate unmeasured. This ordering has no such gap:

1. Test existence.
2. If ABSENT: run the validator, require `absent`, take NO hash.
3. If PRESENT: attempt hash 1 and record success or failure.
4. Run the validator REGARDLESS of hash 1's outcome.
5. If the file is still present, attempt hash 2. Disappearance between the two is `BROKEN`.
6. Compare ONLY if both hashes exist. **Never compare a missing value to anything.**
7. Any hash failure is `BROKEN`, and it does NOT suppress the validator detail.

**The two recovery commands, complete rather than described:**

```
tools/kimi-lane-lock.ps1 -ForceRelease -LaneHome <lane-home> -ConfirmHost <host> -ConfirmOwnerPid <pid> -ConfirmOwnerStartTicksUtc <ticks> -ConfirmDebateId <id> -ConfirmNonce <nonce>
tools/kimi-lane-lock.ps1 -MalformedOverride -LaneHome <lane-home> -ConfirmSha256 <sha256>
```

Every CONFIRMATION placeholder is a field `-Status` prints, which is why `-Status` carries the complete identity. `<lane-home>` is not: it is the configured lane home against which status was requested.

**The authenticated-probe literal, exact:**

> An AUTHENTICATED probe is a SEPARATE operation and is never part of check 8. It acquires the lane lock, it MAY REFRESH the dedicated lane credential, and it never touches the user's ordinary credential. Check 8 reports STRUCTURE only, so a structurally present credential is not a working one.

- [ ] **Step 1: Write the failing tests.** **An ALL-CLEAN fixture requires the aggregate verdict `OK` with a detail naming the successful binary and floor comparison** — without it every fixture in this task is a failure fixture, and an implementation that never emits `OK` at all passes the lot. Pin the new text and the ABSENCE of the old: no home construction in check 8; no `provider list`; the string `credential present and OAuth-sourced` is gone, because measurement 16 shows the check could not support it. Pin the total-order precedence rule, the exact hash order, the narrowed hash wording, the lock-status reporting including the measurement-failure row, the statement that `LIVE` means the process is running and never that a debate was abandoned, **the authenticated-probe literal above**, both override commands, and the unchanged containment-artifact check at `:169-173`.

  **Two of those need EXPLICIT pins rather than the generic "lock-status reporting", because a wrong mapping would satisfy the generic one.** Pin the `UNKNOWN` row's `N/A` verdict TOGETHER WITH its required detail — that liveness could not be determined and that no mutating mode will reclaim — so an implementation mapping `UNKNOWN` to `OK` or `STALE` fails. And pin the foreign-host branch's CASE-INSENSITIVE comparison of the record's `host` against `$env:COMPUTERNAME`, together with its complete `-ForceRelease -ConfirmHost ...` recovery command, so a case-sensitive comparison fails.
- [ ] **Step 2: Rewrite check 8.**
- [ ] **Step 3: Verify.** `python -m pytest evals/multi-model-verify/test_backup_lane.py -q` and `python evals/tools/skill_lint.py skills/multi-model-verify --strict`

---

### Task 9: The contract

**Tests change first.** Three regions: one revised, two new. Forward slashes only.

**Files:** modify `evals/multi-model-verify/test_backup_lane.py:162-194`, `evals/multi-model-verify/test_contract_coverage.py` (`DECLARED_REGIONS`), and `skills/multi-model-verify/references/backup-lane.md:47-67`.

**Region `lane-home-isolation`, exact replacement text:**

> Build the DEBATE home ONCE, before round 1, with `tools/new-kimi-lane-home.ps1`, and set `KIMI_CODE_HOME=<debate-home>` on EVERY call of that debate, fresh and resumed alike. Two directories matter here and the shipped text must not blur them: the DEBATE home is this debate's throwaway `KIMI_CODE_HOME`, and the LANE home is the persistent directory holding the lane's own login and the lock. Two INDEPENDENT reasons, either one sufficient: the real user-global `~/.kimi-code/config.toml` can carry lifecycle hooks that run a shell command on the reviewer's own approval path, and the home is where this lane's effort pin and this debate's session evidence live. One debate is ONE home: that debate's ROUNDS are one session, and the only other session the home may hold is the write-probe's own disposable one, created before round 1 and therefore already in the inventory the freshness rule captures. A home is never reused across DEBATES, because a reused home carries another debate's sessions into this one's evidence. The home holds NO COPY of any credential. Its `credentials` directory is a JUNCTION to a DEDICATED LANE LOGIN, distinct from the user's ordinary login, so a refresh writes THROUGH to one file and no copy can go stale; the lane never falls back to the ordinary credential. A home that cannot be built, or a lane credential that is absent, unreadable or structurally invalid, makes the lane UNAVAILABLE, never a reason to dispatch from the real home. Remove the home with `-Remove` when the debate ends. The lock protocol every one of those calls follows is the call-lifecycle region below.

**Region `lane-lock`, exact text:**

> The lane home is shared between debates and sessions, so one PERSISTENT lock file beside the credential guards it. That file is NEVER unlinked: acquire, reclaim and release are all state transitions written IN PLACE, each under one exclusive handle that serializes every writer. Staleness is LIVENESS and never a clock. A holder is stale only when no process carries its recorded id, or a process carries it with a different start time, which is the identity-reuse guard. A predecessor of this lock decided staleness by AGE, so a live round past the threshold became breakable by anyone; nothing here has a time-based expiry, and a wait budget bounds only caller patience and never widens what counts as stale. What cannot be evaluated is HELD: a record naming another machine, an unreadable file, a zero-length file, a file that is not a JSON object, or a JSON object that does not exactly satisfy the record schema — version 1, one of the two state literals, that state's exact field set, and every field's type and validation rule — are each held and reported rather than reclaimed, because an unmade measurement is never a clean one. A DEAD-holder reclaim reports the holder it replaced. An exhausted wait reports the LIVE or UNMEASURABLE holder it refused, or reports handle contention when no record could be read. Each confirmed override reports the record or bytes it displaced. Contention WAITS up to the caller-supplied budget and then refuses; a zero budget refuses at once, and no budget ever breaks a holder. Two human overrides exist because one cannot cover both states: a well-formed HELD record is freed by confirming its complete recorded identity, machine name included, and a record too damaged to trust its identity is freed by confirming the exact hash of its current bytes. Both are guarded human overrides, not authentication, and both leave the file in place.

**Region `lane-lock-call-lifecycle`, exact text:**

> Ownership is RESOLVED ONCE per debate and PASSED EXPLICITLY thereafter. The owner is the harness session process, not the shell, which exits between calls and would make every lock instantly stale; deriving it from the invoking shell's parent is correct only for a DIRECT invocation, and under any wrapper it names an intermediate process that also exits. So run `tools/kimi-lane-lock.ps1 -ResolveOwner` once at the start of the debate, keep its `ownerPid` and `ownerStartTicksUtc`, generate one 32-character lowercase hexadecimal debate id, and hand all three to every later call. Build with `tools/new-kimi-lane-home.ps1 -Path <debate-home> -Model <canonical-backup-model-id> -Effort <canonical-backup-effort> -LaneHome <lane-home> -DebateId <id> -OwnerPid <pid> -OwnerStartTicksUtc <ticks>`; it acquires the lock before it validates the credential, because a login could otherwise write that credential in between, and it releases only when the build itself failed. Build prints one JSON line carrying `debateHome` and `nonce`: keep that nonce, because removal requires it and a hold nobody can release is a lane nobody else can use. Remove with `tools/new-kimi-lane-home.ps1 -Path <debate-home> -Remove -LaneHome <lane-home> -DebateId <id> -OwnerPid <pid> -OwnerStartTicksUtc <ticks> -Nonce <nonce>`; it confirms the complete identity BEFORE it deletes anything, so a caller who cannot release also cannot destroy, and it releases only after the home is gone. Log the lane in with `tools/new-kimi-lane-login.ps1 -LaneHome <lane-home> -OwnerPid <pid> -OwnerStartTicksUtc <ticks> -VerdictOut <path>`, passing the SAME lane home the build was given, because omitting it authenticates the default home while the debate dispatches from another; the wrapper generates its own debate id, takes the same lock with the lane home as its debate home, and releases it on the way out. A login outside that lock would be the one writer this protocol never sees. Only these filesystem interactions occur before lock acquisition, because the lock lives inside the lane directory: the login wrapper's fail-closed probe of the lane directory, the login wrapper creating that directory when the probe measured it missing, the login wrapper applying its access rules, and the builder's own read-only fail-closed probe of whether that directory is there. All four interactions are safe to repeat: both probes only read, and directory creation and ACL application are idempotent. The builder NEVER creates the directory: if it is missing the builder prints the login command and stops without taking the lock, and once the directory is confirmed the credentials directory and the credential file are both measured UNDER the lock. A debate that ends without removal leaves its home on disk and its record still HELD; that record is not freed by the session exiting, it merely becomes DEAD by liveness and is reclaimable at some later acquire. Read the state at any time with `tools/kimi-lane-lock.ps1 -Status -LaneHome <lane-home>`, which reports the holder and its liveness and reports LIVE to mean the process is running, never to mean the debate is still going.

- [ ] **Step 1: Rewrite the `lane-home-isolation` pin FIRST** to the exact text above.
- [ ] **Step 2: Add `lane-lock` and `lane-lock-call-lifecycle` pins** to the exact texts above.
- [ ] **Step 3: Add both identifiers to `DECLARED_REGIONS`.** The id `lane-lock` is REUSED: the comment at `evals/multi-model-verify/test_contract_coverage.py:624-632` lists a `lane-lock` among seven regions deleted last cycle, so once the new one is declared that comment reads as if it narrated deleting this region. Amend it to say the name is reused for an unrelated rule about the persistent lane lock file, not restored.
- [ ] **Step 4: Edit `backup-lane.md`.**
- [ ] **Step 5: Verify equality over NORMALIZED RUNTIME VALUES, not raw bytes.** Raw source bytes can never match: the Markdown is line-wrapped and the pin is Python adjacent string literals. `evals/multi-model-verify/test_contract_coverage.py:21-30` shows `parse_regions` collapsing whitespace, `:517-520` shows `collect_pins` doing the same, and `:523-526` shows coverage is a SUBSTRING test. So: call `parse_regions` on the edited Markdown and `collect_pins` on the edited test file, then for each region assert its normalized string is a substring of some normalized pin, printing both lengths. **A raw-byte length or hash comparison is the wrong equality and must not be used.**

```
python -m pytest evals/multi-model-verify/test_contract_coverage.py evals/multi-model-verify/test_backup_lane.py -q
```
Then delete one sentence from a new region and confirm the checker reports it UNLOCKED; revert.

---

### Task 10: CI wiring, version, and full gate

**Files:** modify `.github/workflows/skill-evals.yml:79-99` and `.claude-plugin/plugin.json`.

- [ ] **Step 1: Add every new offline dual-host module to BOTH Windows steps** — `test_kimi_lane_lock.py`, `test_lock_protocol_live.py`, `test_kimi_credential_state.py`, `test_kimi_lane_login.py`, the now-dual-host `test_kimi_lane_home.py`, and **`test_lane_credential_live_support.py` from Task 7 step 1b** — and add all SIX to the required-module set in `evals/tools/check_workflow_paths.py`. `test_lane_credential_live.py` is NOT added: it is opt-in and needs real logins, and CI must not acquire credentials merely to avoid a skip.
- [ ] **Step 2:** `python evals/tools/check_workflow_paths.py` — empty, exit 0, with host parity satisfied.
- [ ] **Step 3:** Bump `.claude-plugin/plugin.json` to `0.19.0`.
- [ ] **Step 4:** All four gates. Four exit-zero runs and a green pytest line.
- [ ] **Step 5: Re-run the opt-in live suite at FINAL HEAD, per host,** because Task 7 ran it mid-plan and later tasks changed the builder:
```
$env:PARALLAX_LANE_LIVE = "1"
$env:PARALLAX_PS_HOST = "powershell.exe"; python -m pytest evals/multi-model-verify/test_lane_credential_live.py -q
$env:PARALLAX_PS_HOST = "pwsh.exe";       python -m pytest evals/multi-model-verify/test_lane_credential_live.py -q
```
Expected: ZERO skipped.
- [ ] **Step 6:** Skill text changed, so run `python evals/tools/run_behavioral_evals.py --head`.
- [ ] **Step 7: The known `Claude-Session:` trailer debt guard.** Frozen at r34, replacing "the history check" — the user has AUTHORIZED the three carriers rather than rewrite 44 of the branch's 70 commits and invalidate every commit id the build ledger records.

**Why the original could not simply be re-scoped.** `6201e30..HEAD` already EXCLUDES the base, so it already measures only what this branch adds, and what this branch adds is three. Calling it "no new carriers" would have been a rename, not a re-scope. Pre-existing violations elsewhere establish historical debt; they do not turn three into zero.

**What was measured before deciding**, and neither fact was known when this step was first frozen: this repository merges with MERGE COMMITS rather than squashes, so branch commits do reach `main`; and `main` already carries 65 commits with the trailer, including `6201e30`, the base of this step's own range. Stripping three here would make one branch look clean against a repository that is not.

The guard enumerates each commit in `6201e30..HEAD`, reads its message with FATAL exit handling, and collects every commit whose message contains `Claude-Session:`. It FAILS if any carrier is outside the authorized set. FEWER than three is permitted, so a later rewrite that removes one does not fail this gate. The three authorized commit ids, in full:

```
c79da4182a3595c76ba03e3b222021afaf3ab7c3
9d50196c3215b019b643fd40906966b36f77da30
e3f98c23ee1f14ac14d86d470185af7eaa8db1e4
```

**It reports `authorized Claude-Session debt: <n> known carriers; no unapproved carrier added`, and NEVER `clean`.** The word would claim more than the check can hold.

**The claim is narrowed with it.** Searching for the literal `Claude-Session:` is not an oracle for every form of AI attribution. The old message said "AI-attribution trailer found" while the pattern recognized ONE form, which is a claim wider than its evidence sitting inside a gate. The new message names the literal it actually searched for.

**Recorded, separately and without softening:** the repository-wide no-attribution convention remains historically unmet; this branch carries three explicit user-authorized exceptions; the rewrite was rejected because it would invalidate the branch's recorded commit provenance; and NO claim is made that `main` is clean or that every attribution format was scanned.

**The exact executable, frozen verbatim.** A description of a guard is not a
guard. This is the block that produced the results below, parameterized ONLY so
that the FIRST THREE mutations can be driven without editing it:

```powershell
param(
    [string] $Range = '6201e30..HEAD',
    [string[]] $Authorized = @(
        'c79da4182a3595c76ba03e3b222021afaf3ab7c3',
        '9d50196c3215b019b643fd40906966b36f77da30',
        'e3f98c23ee1f14ac14d86d470185af7eaa8db1e4'
    )
)

$ErrorActionPreference = 'Stop'

$ids = & git log --format=%H $Range 2>$null
if ($LASTEXITCODE -ne 0) { throw "git log failed with exit $LASTEXITCODE for range '$Range'" }
if ($null -eq $ids) { $ids = @() }
$ids = @($ids)

$authorizedSet = [System.Collections.Generic.HashSet[string]]::new()
foreach ($a in $Authorized) { [void] $authorizedSet.Add($a) }

$carriers = @()
foreach ($id in $ids) {
    $message = & git log -1 --format=%B $id 2>$null
    if ($LASTEXITCODE -ne 0) { throw "git log failed with exit $LASTEXITCODE reading message of $id" }
    $text = ($message -join "`n")
    if ($text -imatch 'Claude-Session:') { $carriers += $id }
}

$unapproved = @($carriers | Where-Object { -not $authorizedSet.Contains($_) })
if ($unapproved.Count -gt 0) {
    throw "unapproved commit(s) carrying the literal 'Claude-Session:': $($unapproved -join ', ')"
}

"authorized Claude-Session debt: $($carriers.Count) known carriers; no unapproved carrier added"
```

**Two details are load-bearing, and each has a mutation below that FAILS
without it.** `-imatch`, because a case variant of the trailer is still an
attribution trailer, and a guard that silently ignores one is fail-open in the
only direction that matters here; the r35 text specified `-cmatch` and called it
load-bearing, which had the safety argument exactly backwards. And the exit
check on BOTH `git log` calls, because an unreadable message must never be read
as a non-carrier. The known cost of `-imatch` is a commit message that merely
DISCUSSES the literal in prose, which this guard will report as a carrier; that
is a visible false failure a human resolves, not a silent pass.

`$ids = @($ids)` after the null check is DEFENSIVE NORMALIZATION and nothing
more. `foreach` already iterates `$null`, a scalar and an array correctly, so
removing it breaks nothing. It is written here so that a later reader who adds
an indexed or `.Count` use does not have to rediscover that a one-commit range
returns a scalar.

Run it, with `$Range` and `$Authorized` left at their defaults, from the
repository root. FIVE mutations, because the guard has five failure directions.
The first three need only parameters:

1. `-Range 'nosuchref..HEAD'` — an INVALID REVISION RANGE must throw on `git
   log`'s exit code and never report debt.
2. `-Authorized @('c79da4182a3595c76ba03e3b222021afaf3ab7c3')` — a carrier
   OUTSIDE the authorized set must fail.
3. the three authorized ids plus a fourth that is not a carrier, such as
   `'0000000000000000000000000000000000000000'` — an authorized id that is not a
   carrier must not be required to be one.

The last two need a DISPOSABLE `git` SHIM, because neither can be reached from
real history:

4. The shim enumerates ONE id that is not in the authorized set, and returns a
   message whose only trailer is lowercase `claude-session:`. The guard must
   FAIL. Repeat against a copy weakened to `-cmatch`, which must report clean —
   that contrast is the oracle.
5. The shim enumerates that id successfully and then FAILS the message read with
   exit 1. The guard must throw on the read. Repeat against a copy with the
   second exit check deleted, which must report clean.

**The shim harness, frozen verbatim.** Save the block above as a `.ps1` file and
pass it as `-Guard`. It is written out here for the same reason the guard is:
its mechanics are consequential, not clerical, and one of them already produced
a false result once.

```powershell
param([string] $Guard)

$ErrorActionPreference = 'Stop'

$body = Get-Content -Raw $Guard
$weakA = Join-Path ([System.IO.Path]::GetTempPath()) 'guard-weak-cmatch.ps1'
$weakB = Join-Path ([System.IO.Path]::GetTempPath()) 'guard-weak-noexit2.ps1'

$textA = $body.Replace("-imatch 'Claude-Session:'", "-cmatch 'Claude-Session:'")
if ($textA -ceq $body) { throw 'weakening A did not apply' }
$textB = $body.Replace(
    'if ($LASTEXITCODE -ne 0) { throw "git log failed with exit $LASTEXITCODE reading message of $id" }',
    '')
if ($textB -ceq $body) { throw 'weakening B did not apply' }

function Show {
    param([string] $Label, [string] $Script)
    try { "$Label -> $(& $Script)" }
    catch { "$Label -> threw: $($_.Exception.Message)" }
}

try {
    Set-Content -Path $weakA -Value $textA -NoNewline
    Set-Content -Path $weakB -Value $textB -NoNewline

    function global:git {
        if ($args -contains '-1') {
            if ($global:parallaxShimMode -eq 'message-read-fails') {
                $global:LASTEXITCODE = 1
                return
            }
            $global:LASTEXITCODE = 0
            return @('chore: an ordinary subject', '', 'claude-session: https://example.invalid/session_x')
        }
        $global:LASTEXITCODE = 0
        return @('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa')
    }

    'MUTATION 4: a lowercase-only `claude-session:` trailer'
    $global:parallaxShimMode = 'lowercase-carrier'
    Show 'frozen (-imatch)   ' $Guard
    Show 'weakened (-cmatch) ' $weakA
    ''
    'MUTATION 5: enumeration succeeds, the message read FAILS'
    $global:parallaxShimMode = 'message-read-fails'
    Show 'frozen             ' $Guard
    Show 'weakened (no check)' $weakB
}
finally {
    Remove-Item function:git -ErrorAction SilentlyContinue
    Remove-Item variable:global:parallaxShimMode -ErrorAction SilentlyContinue
    Remove-Item $weakA, $weakB -ErrorAction SilentlyContinue
    if (Test-Path function:git) { throw 'the git shim survived cleanup' }
}
```

Four things in the harness are deliberate. The shim is GLOBAL, because `& git`
resolves a function ahead of the executable only if the function is visible from
the guard's child scope. Its mode is read from the GLOBAL scope: a global
function does not see the defining script's `$script:` scope, so a
`$script:`-held mode silently never changes, and the pair then agrees on both
runs — which is a pair that cannot discriminate, and it happened. It sets
`$global:LASTEXITCODE` itself, because a function does not set it. And cleanup
sits in `finally` with a verification, because a shim left behind would shadow
real `git` for the rest of the session; after the harness runs, `(Get-Command
git).Source` must be the real executable again.

Expected: the authorized-debt line, with `n` at most 3, and each mutation as
stated. Measured at `7527a2c`:

```
default:      authorized Claude-Session debt: 3 known carriers; no unapproved carrier added
mutation 1:   threw: git log failed with exit 128 for range 'nosuchref..HEAD'
mutation 2:   threw: unapproved commit(s) carrying the literal 'Claude-Session:': e3f98c2..., 9d50196...
mutation 3:   authorized Claude-Session debt: 3 known carriers; no unapproved carrier added
mutation 4:   frozen   threw: unapproved commit(s) carrying the literal 'Claude-Session:': aaaa...
              -cmatch  authorized Claude-Session debt: 0 known carriers; no unapproved carrier added
mutation 5:   frozen   threw: git log failed with exit 1 reading message of aaaa...
              no check authorized Claude-Session debt: 0 known carriers; no unapproved carrier added
```

Both weakenings report CLEAN on an input that carries a defect. That is the
shape this plan forbids everywhere else, and it is why these two mutations
exist.
- [ ] **Step 8: The mechanical exact-line checker from Task 11 runs in the full gate**, added to the four gates in step 4 and to CI.

---

### Task 11: The mechanical exact-line gate

**Files:** create the shared helper and `evals/tools/check_exact_line_oracles.py`, plus its own test module; modify the nine sites below.

Added at r32. The session asked whether "discard blank lines, then require one survivor" could be swept mechanically rather than found one instance at a time, after round 30 fixed the class in two PowerShell callers, r31 fixed one Python instance, and the session then found a second Python instance in the custody-line parser that both earlier passes had missed. Three sweeps, three misses, one algorithm.

**The nine surviving sites, enumerated so that deleting one is visible:**

| File | Line | What it parses |
|---|---|---|
| `evals/multi-model-verify/test_kimi_credential_state.py` | 118 | the validator's classification output |
| `evals/multi-model-verify/test_kimi_lane_home.py` | 364 | the builder's custody line |
| `evals/multi-model-verify/test_kimi_lane_login.py` | 382, 443, 710, 725, 984, 1013 | six `-VerdictOut` reads |
| `evals/multi-model-verify/test_lock_protocol_live.py` | 340 | the measured type report |

All nine discard blanks before requiring one survivor, contrary to the frozen caller rule that leading, interior and extra trailing blank lines are all REJECTED.

- [ ] **Step 1: One shared `accept_exactly_one_nonempty_line()`** using `\A([^\r\n]+)(\r\n|\n)?\Z` — the same algorithm as `tools/new-kimi-lane-home.ps1`'s `singleLine` pattern and as `_accept_validator_output`, not merely the same intent. Replace all nine sites with it.
- [ ] **Step 2: An AST-based repository checker**, `evals/tools/check_exact_line_oracles.py`. It rejects an assignment whose value is a `splitlines()` comprehension filtering on truthiness or on `!= ""` WHEN the assigned name is later tested for length one in the same scope. Both halves are required: an intentional multi-record blank filter is legitimate and must not be flagged.
- [ ] **Step 3: Mutation-test the checker itself**, three directions: the bad filter-then-count idiom must FAIL it; an intentional multi-record blank filter must PASS; the strict regex helper must PASS. A checker that cannot fail is the defect this plan exists to prevent, and it is the checker's own turn to prove it can.
- [ ] **Step 4: State the limit in the checker's own docstring.** It catches this SYNTACTIC class. It cannot prove that an arbitrarily-written parser is semantically equivalent, and it must never be described as proving the class is gone.
- [ ] **Step 5: Verify.** `python evals/tools/check_exact_line_oracles.py` exits 0 with empty output, its own test module passes, and the full suite stays green on both hosts.

---

## Debate record

**Participants:** Opus 5 (session) / gpt-5.6-sol (codex exec, session `019fbb82-9e35-7b72-a64e-59fb60b981cd`)
**Rounds used:** 36, cap lifted by the user
**Outcome:** ELEVEN tasks. Reviewer PASS on Tasks 1 through 9 and 11; Task 10 ESCALATE, narrowly, on one repository-policy gate the user waived. Building reopened the plan EIGHT times after the round-28 PASS, at rounds 29 through 36, each time on a defect that only running the case could reach. The last two reopenings found defects in the ROUND-34 REPAIR itself: a guard that was described rather than written, and then two of its three stated load-bearing details having no oracle and one of them being false.
**Verification status:** FULL. Every round's route matched the canonical declarations and the cross-vendor gate was satisfied throughout; nothing here was degraded by a transport failure.
**Degradation:** NONE in the verification sense, and the distinction is deliberate. There is one accepted POLICY WAIVER, which is a different thing and must not be read as either: three commits in this branch carry a `Claude-Session:` trailer that `CLAUDE.md` forbids, and they stay. Task 10 step 7 freezes the waiver, names all three commit ids in full, fails on a fourth, and reports authorized debt rather than `clean`.
**Authorized by:** the user, 2026-08-02, after being shown that this repository merges with merge commits so branch commits do reach `main`, that `main` already carries 65 such commits including this branch's own base, and that removing three would rewrite 44 of 70 commits and invalidate every commit id the build ledger records. Their decision, verbatim: "Don't rewrite."
**Not claimed:** that `main` is clean, that every form of AI attribution was scanned rather than the one literal `Claude-Session:`, or that remote CI has run.
**Raw rounds:** `docs/superpowers/plans/rounds/2026-08-01-cred-lock/`

The user lifted the round cap and directed that this iterate to an actual reviewer PASS. Nothing has been struck and nothing is contested; every FIX in every round was accepted and applied. Rounds 4 and 5 both reported that no finding required design escalation.

### Resolved points

| # | Claim | Raised by | Outcome | Evidence |
|---|-------|-----------|---------|----------|
| 1 | `OpenOrCreate` reads a crash-truncated lock as free and steals it | reviewer | accepted into Task 3 | design spec `:237-250` |
| 2 | Idempotent acquire could not receive the nonce; lost-nonce deadlock | reviewer | accepted into Task 3 | plan r1 `:95-105` |
| 3 | Making the nonce visible in `-Status` closes the deadlock | session | accepted by reviewer | design spec `:211-215` |
| 4 | Junction "no file copied" oracle was vacuous | reviewer | accepted into Task 6 | plan r1 `:288-290` |
| 5 | Live gates asserted invariance that holds when the command failed | reviewer | accepted into Task 7 | design spec `:89-95` |
| 6 | Start-time fault needs a seam, not a SYSTEM process | reviewer | accepted into Task 3 | `tools/new-kimi-lane-home.ps1:416-423` |
| 7 | Builder could not release the lock it acquired | reviewer | accepted into Task 6 | plan r1 `:276-294` |
| 8 | Removal destroyed the home before discovering it could not release | reviewer | accepted into Task 6 | `tools/new-kimi-lane-home.ps1:65-133` |
| 9 | Host selector tests one host whatever CI sets | reviewer | accepted into Task 6 | `evals/multi-model-verify/test_kimi_lane_home.py:21` |
| 10 | Windows CI job runs a deleted test module | session | accepted, promoted to Task 1 | `.github/workflows/skill-evals.yml:84,95` |
| 11 | "Never pushed" was wider than the evidence | reviewer | accepted, then verified | no remote ref contains HEAD; `ls-remote` returns only `refs/heads/main`; no Actions runs |
| 12 | Contract lifecycle belongs in its own declared region | reviewer | accepted into Task 9 | `CLAUDE.md:55-92` |
| 13 | Acquire state table overlapped rows and overclaimed completeness | reviewer | accepted into Task 3 | plan r2 `:216-240` |
| 14 | Release and override behaviour on non-held records was undefined | reviewer | accepted into Task 3 | plan r2 `:232-265` |
| 15 | Task 8 promised a foreign-host override Task 3 forbade | reviewer | accepted; `-ConfirmHost` added | plan r2 `:181-206,436-452` |
| 16 | Inherited child streams and a JSON-only stdout are not jointly implementable | reviewer | accepted; verdict moved to a file | plan r2 `:316-341` |
| 17 | Task 7 forbade creating login B while its oracle required it | reviewer | accepted; claim narrowed | plan r2 `:399-426` |
| 18 | Unconditional `finally` released a SUCCESSFUL build's lock | reviewer | accepted into Task 6 | plan r2 `:369-375` |
| 19 | Region comparison compared raw bytes that can never be equal | reviewer | accepted, then verified | `evals/multi-model-verify/test_contract_coverage.py:21-30,517-526` |
| 20 | The history check printed matches without failing | reviewer | accepted into Task 10 | plan r2 `:529-535` |
| 21 | Three contract literals overstated their evidence | reviewer | accepted into Task 9 | design spec `:122-142` |
| 22 | `-MalformedOverride` covered only unparseable bytes, leaving reachable malformed classes unrecoverable | reviewer | accepted into Task 3 | plan r3 `:180-190` |
| 23 | An extra field on a FREE record was not malformed | reviewer | accepted into Task 3 | plan r3 `:118,190` |
| 24 | Exit 4 contradicted the two override exceptions | reviewer | accepted into Task 3 | plan r3 `:139-148` |
| 25 | Two conflicting token rules for `DebateId`/`Nonce` | reviewer | accepted; unified on 32 lowercase hex | plan r3 `:54-56` |
| 26 | The universal no-exit-1 claim cannot survive PowerShell's binder | reviewer | accepted; guarantee scoped to bound invocations, with a mutates-nothing test | `775472c^:tools/kimi-lane-lock.ps1:36-50` |
| 27 | Missing-file behaviour was undefined per mode | reviewer | accepted into Task 3 | plan r3 `:150-156` |
| 28 | The login wrapper wrote the home and ACL before taking the lock | reviewer | accepted; bootstrap made an explicit bounded exception | plan r3 `:51,252-254` |
| 29 | Stream inheritance was not actually tested; a buffer-and-replay wrapper would pass | reviewer | accepted; oracle made temporal | plan r3 `:250,258` |
| 30 | Cleanup needed two flags, not one | reviewer | accepted into Task 6 | plan r3 `:280-284` |
| 31 | The doctor's aggregate was not a total order; `N/A` had no rank | reviewer | accepted into Task 8 | `commands/doctor.md:6-9` |
| 32 | "The doctor mutated a credential" was wider than two hashes establish | reviewer | accepted; narrowed to bytes changed, actor not established | plan r3 `:346,355` |
| 33 | Adding modules to both CI steps had no oracle | reviewer | accepted; host parity added to the checker in Task 1 | `.github/workflows/skill-evals.yml:79-99` |
| 34 | The probe record commits complete client streams to a PUBLIC repo and can capture a credential value | reviewer | accepted; secret guard added to Task 7 | plan r4 `:29,346` |
| 35 | A token-rotation `assert` leaks both token values through pytest introspection | reviewer | accepted; comparison moved to `if` plus `pytest.fail` | plan r4 `:29,352` |
| 36 | `$buildCompleted` was set before the custody line was emitted, retaining an unreleasable lock | reviewer | accepted into Task 6 | plan r4 `:299-311` |
| 37 | The login literal omitted `-LaneHome`, authenticating a different home than the build used | reviewer | accepted into Task 9 | plan r4 `:261-266,423` |
| 38 | A free record carrying a held-only KNOWN field was not reached by the unknown-field rule | reviewer | accepted into Task 3 | plan r4 `:124-130,207` |
| 39 | `-MalformedOverride` on a well-formed foreign-host record had two outcomes | reviewer | accepted; preprocessing order added | plan r4 `:156,183-201` |
| 40 | Code 5's meaning covered only mismatch while three rows returned it for "nothing applicable" | reviewer | accepted into Task 3 | plan r4 `:151-159` |
| 41 | Task 2's fixture change had no oracle in its own task | reviewer | accepted; selector refactor moved into Task 2 | `evals/multi-model-verify/test_kimi_lane_home.py:21,310-320` |
| 42 | Task 5's exit table omitted binder code 1 and lock code 5 | reviewer | accepted into Task 5 | plan r4 `:279-281` |
| 43 | The doctor's hash prose could leave the validator substate unmeasured | reviewer | accepted; seven-step algorithm | plan r4 `:376-395` |
| 44 | The checker's initial required module set was not frozen | reviewer | accepted into Task 1 | `.github/workflows/skill-evals.yml:79-99` |
| 45 | Task 7's normalization retained an implementer-selected fallback | reviewer | accepted; complete normalized stderr, no fallback | plan r4 `:346` |

### Escalated points (user-decided)

None.







