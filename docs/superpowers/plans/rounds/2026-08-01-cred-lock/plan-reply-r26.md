Round 26 does not yet PASS. The six intended corrections are directionally right, but four tasks retain blocking oracle or specification gaps.

Task 1

The checker now requires every test token to be a readable regular file, but its mutations cover only a missing path and a directory named `.py`; neither fails an implementation that checks `is_file()` but never verifies readability. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:116](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:116) [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:129](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:129)

BLOCKING FIX: Add a deterministic mutation that makes opening one referenced regular file raise `PermissionError` or `OSError`, then require the checker to fail and identify that token. Do not depend on a real Windows ACL denial. Freeze the checker’s readability operation as successfully opening the file for binary reading; `exists()` or `is_file()` alone is insufficient.

Verdict: FIX — add a deterministic unreadable-regular-file oracle.

Task 2

The validator work remains adequately specified, including decisive opposite-direction duplicate-key tests and live validation of the generated fixture under both hosts. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:147](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:147) [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:163](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:163)

Verdict: PASS.

Task 3

The contention signal now occurs only after an actual contention decision, distinguishes handle from holder contention, fails closed if signalling fails, and drives both clamp and retry-success tests across both branches. That closes the false-positive startup path and the missing-branch problem. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:225](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:225) [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:238](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:238)

Verdict: PASS.

Task 4

Invocation success, result cardinality and parseability are established before type comparison, and the crash fixture does not inspect lock bytes unless the child proves it reached the synchronized crash point. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:347](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:347) [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:349](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:349)

Verdict: PASS.

Task 5

The new four-state probes are correct in principle, but the earlier bootstrap rule still says the only pre-lock operations are directory creation and ACL application. The new lane-home probe is itself a pre-lock filesystem interaction, making these paragraphs contradictory. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:393](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:393) [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:397](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:397)

Both fault seams are called “named,” but neither name, firing point, exact diagnostic, nor shared production/test literal appears in the plan. A zero-judgment implementer must invent them. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:397](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:397)

BLOCKING FIX:

- Amend the bootstrap rule to name the fail-closed lane-home probe, conditional creation and ACL application as the only pre-lock filesystem interactions.
- Freeze two distinct names, for example `PARALLAX_KIMI_LANE_LOGIN_HOME_PROBE_FAULT` and `PARALLAX_KIMI_LANE_LOGIN_CREDENTIALS_PROBE_FAULT`.
- For each, freeze: login-wrapper-only scope, nonempty activation, immediate firing before its real probe, simulated `UNMEASURABLE` outcome, exit 6, exact stderr sentinel and required stdout/verdict/client/mutation state. The credentials seam must still release in `finally`.
- Require tests to assert those exact shared literals.

Verdict: FIX — reconcile the pre-lock list and fully define both probe seams.

Task 6

The directory-probe seam has a name and location but still lacks the “exact stderr sentinel” the plan says production and tests share. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:448](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:448)

The deletion rule partitions deletion into error and verified absence/presence, but not an unmeasurable post-deletion absence check. A failed `Test-Path`-style measurement could therefore be interpreted as absence, allowing release and a false success report despite the governing invariant. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:470](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:470) [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:472](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:472)

The failed-build cleanup seam is also merely described as “named”; its actual name, exact firing point and diagnostic remain open. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:473](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:473)

Finally, the real locked-file deletion oracle does not specify teardown after asserting the failed state. Because deletion may have partially removed the sentinel or other contents, ordinary `-Remove` may not be a valid teardown path. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:470](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:470)

These checks target a real predecessor defect: Remove currently performs non-terminating deletion immediately followed by `removed <path>`. [tools/new-kimi-lane-home.ps1:131](C:\Users\Brandon\Documents\parallax/tools/new-kimi-lane-home.ps1:131)

BLOCKING FIX:

- Freeze the directory-probe sentinel, for example: `PARALLAX_LANE_HOME_DIRECTORY_PROBE_FAULT injected: simulated lane-home directory probe failure`.
- Add a third post-deletion verification state: `UNMEASURABLE` is failure, exits 6, prints no success line and does not release.
- Give it a deterministic named seam, such as `PARALLAX_LANE_HOME_REMOVE_VERIFY_FAULT`, firing after deletion and before verification, with exact diagnostic and end state: home absent, held record byte-identical, direct release used only during teardown.
- Name and completely define the cleanup seam, for example `PARALLAX_LANE_HOME_CLEANUP_DELETE_FAULT`, including its exact stderr line, Build-only firing point, skipped deletion, original-failure precedence, continued release attempt, and resulting home/lock state.
- Freeze teardown for the real locked-file oracle: close the handle, directly release using the retained identity, then remove the disposable remainder outside the behavior under test.

Verdict: FIX — complete all three failure-state partitions and seam contracts.

Task 7

The file-snapshot helper now prohibits equality-comparable failure sentinels, and both pre- and post-command measurement failures must still traverse the cleanup matrix. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:559](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:559) [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:561](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:561)

Verdict: PASS.

Task 8

The total matrix now has a positive `OK` row, a corresponding all-clean fixture, and a whole-region pin, so an implementation that never reports success cannot pass. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:650](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:650) [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:693](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:693)

Verdict: PASS.

Task 9

Changing “steps” to “filesystem interactions” fixes the parameter-validation/debate-ID problem, but the literal still says exactly three pre-lock filesystem interactions: creation, ACL application and the builder probe. Task 5 now requires the login wrapper to probe lane-home state before either creation or ACL application, making four interaction kinds. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:397](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:397) [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:717](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:717)

BLOCKING FIX: Replace the count with an exhaustive list: the login wrapper’s fail-closed lane-home probe, conditional lane-home creation, lane-home ACL application, and the builder’s read-only lane-home probe. “Only these pre-lock filesystem interactions occur” is safer than another numeric count.

Verdict: FIX — synchronize the shipped literal with Task 5’s new probe.

Task 10

The workflow gate now checks path usability and host parity, while the history check makes command failure fatal before interpreting its output. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:735](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:735) [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:747](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:747)

Verdict: PASS.

Overall verdict

FIX — blocking defects remain in Tasks 1, 5, 6 and 9. Do not freeze revision 25 or start building yet.

Task 1 should remain first once these plan fixes are applied and the plan passes. Its scope repairs the workflow’s existing path list and introduces the portable checker; Task 10 adds the six new modules only after their implementing tasks create them. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:105](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:105) [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:732](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:732) The existing Task 5 and Task 6 defects do not require reordering because Task 1 touches only the workflow and its checker/tests, not either affected PowerShell tool. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:113](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:113) [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:380](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:380) [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:423](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:423)

Final check

UNVERIFIED:

- Measurements 1–21 remain external measurements recorded in the design, not facts reproducible from the repository’s current test suite. [docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:35](C:\Users\Brandon\Documents\parallax/docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:35)
- The assumption that three dedicated login homes coexist remains a generalization with a required loud-failure direction, not a repository-proven measurement. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:514](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:514)
- The branch’s remote-ref and Actions-run claims were not rechecked because network access is unavailable.
- No implementation exists yet; the plan remains DRAFT at revision 25. [docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:5](C:\Users\Brandon\Documents\parallax/docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:5)
- Pytest gates were not run because no `python` executable is available; as instructed, that is not a finding.