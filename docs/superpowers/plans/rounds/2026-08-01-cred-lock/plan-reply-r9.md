Not PASS. Four of the five round-8 fixes are correct. The successful-build custody path is correct, but its failure boundary, initial secret seeding, and pre-command mutations remain open.

### Task 1

Task 1 now correctly says Task 10 adds six modules, matching Task 10’s exact list. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:77-92`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:551-556`.

Verdict: PASS.

### Task 2

Byte-unchanged from the passed revision. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:96-128`.

Verdict: PASS.

### Task 3

Byte-unchanged from the passed revision; the exhaustive MALFORMED definition remains consistent with the per-state property rule. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:144-146`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:232-246`.

Verdict: PASS.

### Task 4

Byte-unchanged from the passed revision. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:256-277`.

Verdict: PASS.

### Task 5

Byte-unchanged from the passed revision. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:281-317`.

Verdict: PASS.

### Task 6

Task 6’s successful-build-retains/removal-releases lifecycle remains internally complete. Build returns custody only after success; failed builds release internally; successful removal confirms identity, deletes, then releases. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:328-348`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:356`.

Verdict: PASS.

### Task 7

Three blocking fixes remain.

1. **Build-failure cleanup is not partitioned from successful custody.**

   The common sequence says `finally` always calls real `-Remove`, but a refused or failed Build returns no custody nonce and Task 6 already owns failed-build cleanup. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:402-410`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:338-344`. Item 4 also gives both deletion paths the blanket custody description “build holds C; `-Remove` releases,” although its failed-build half releases internally and returns no nonce. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:395`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:439`.

   Required fix:

   - Set `custodyReceived` only after Build exits 0 and its exact JSON is successfully parsed.
   - Invoke the command and later `-Remove` only when `custodyReceived`.
   - On Build refusal/failure, invoke neither the command nor `-Remove`; preserve the Build failure because the builder owns its cleanup.
   - Split item 4’s routing row into successful-build/real-Remove and failed-build/internal-cleanup paths.
   - Extend the pre-held support oracle to assert no Remove attempt and a byte-identical pre-held record.
   - Freeze cleanup precedence: original command/guard failure stays primary if Remove also fails; Remove failure is primary only after main success.

2. **Initial A/B/C secret seeding has no acquisition lifecycle or oracle.**

   The union must be seeded from A, B, and C while each home’s hold is active, but before the first builder-created case no such hold exists. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:424-428`. “The builder is the acquisition” covers builder-created cases only and does not say how module initialization obtains the three seed holds. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:402-410`.

   Required fix: before any live command, seed A, B, and C sequentially through an explicit direct-acquire lifecycle: acquire with the module owner and that home as both LaneHome and DebateHome, read and merge, then release with the nonce in `finally`. Name this as the sole direct-acquire exception to builder custody. Add an offline oracle that a pre-held seed home prevents its credential read and that successful seeding leaves its record exactly free.

3. **The deliberate expiry mutations are not explicitly placed under custody, and no oracle proves they are.**

   Items 3 and 7 say “force expiry” before dispatch/provider-list, while the custody sequence names only Build, command, post-command merge, and Remove. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:406-410`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:438-442`. An implementation can therefore force expiry before Build, mutate C unlocked, and still pass every functional assertion.

   Required fix: add a pre-command callback phase after successful Build and before client invocation; all expiry writes and their pre-command hashes occur there while builder custody is held. Extend the blocking-command support oracle so a second acquire contends during this callback, not only during the client process.

The shared helper file and import boundary are now exact. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:367-371`. Both Task 7 host commands now collect the support suite. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:446-460`.

Item 6’s no-lock choice is correct. Its homes are isolated and fake, and the secret lifecycle now explicitly allows their values to be loaded without a lock while still applying the same stream guard. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:397`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:420-430`.

Verdict: FIX — BLOCKING: partition failed Build from successful custody, define and test initial seed acquisition, and place/test all pre-command credential mutations under builder custody.

### Task 8

Byte-unchanged from the passed revision. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:466-516`.

Verdict: PASS.

### Task 9

Byte-unchanged from the passed revision. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:520-547`.

Verdict: PASS.

### Task 10

The support suite is correctly listed among all six dual-host modules and retained outside the credential-dependent live module. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:551-565`.

Verdict: PASS.

### Plan record

The file identifies itself as revision 7, contains no r8 history entry, and records seven rounds, although the submitted plan is r8 after Round 8. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:5-21`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:577-585`.

Verdict: FIX — NONBLOCKING: update the revision label, add r8 history, and record eight completed rounds.

## Overall verdict

FIX.

Applied correctly:

- Task 1’s six-module correction.
- The shared-helper module and import boundary.
- Collection of the support suite under both hosts.
- Item 6’s no-lock exception.
- Builder-retained custody for the successful path.

Remaining blocking defects are confined to Task 7’s failure boundary, initial seeding lifecycle, and pre-command mutation boundary.

## Final check

- **UNVERIFIED:** Measurements 1–21 remain external measurements; the design assigns them to live gates because repository tests cannot establish them. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:35-67`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:348-364`.
- **UNVERIFIED:** No planned Task 7 implementation exists yet, so the new custody/support gates cannot presently be executed. The plan declares all three files as new. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:367-371`.

