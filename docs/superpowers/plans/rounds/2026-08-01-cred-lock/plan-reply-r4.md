The plan does not freeze yet. `-ConfirmHost` closes the foreign-host contradiction, and the acquire table itself is now disjoint, but Task 3’s overall record partition remains incomplete. Several new lifecycle/oracle defects also remain. None requires design escalation; each has a deterministic fix.

### Task 1 — CI repair

The path checker has both a red-at-HEAD case and an explicit mutation test. The workflow currently names the deleted module in both host steps, and Task 1 removes both occurrences before later restoring the newly implemented suite explicitly. `.github/workflows/skill-evals.yml:79-99`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:60-72`.

PASS

### Task 2 — Credential validation

The status partition, precedence, field exposure, and type edges are complete. In particular, the plan correctly does not require optional fields, matching the settled structural-validity rule. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:80-102`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:144-163`.

PASS

### Task 3 — Lock tool

The acquire table is now a proper partition within its stated domain:

- Free/dead records split on nonce absent versus supplied.
- Live records split first on whether every non-nonce identity component matches, then on nonce equality.
- Foreign-host, malformed, unreadable, and handle-contention states are explicitly preclassified. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:158-168`.

`-ConfirmHost` closes the Task 3/Task 8 contradiction without enabling automatic foreign-host reclamation: only `-ForceRelease`, with every recorded identity component exactly confirmed, may mutate that record. Ordinary acquire/release still refuse it. That remains a guarded human override, not authentication. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:177-184,200`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:269-295`.

The total partition still has five defects:

1. `-MalformedOverride` covers only “unparseable” bytes, but `MALFORMED` also includes parseable objects with missing, unknown, wrongly typed, or invalid fields. Those reachable states have no override row. Replace “unparseable” in rows 8–9 with “readable MALFORMED,” and test every malformed class with matching and mismatching hashes. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:180-190`.

2. A free record is declared to be exactly two fields, but the `MALFORMED` definition rejects unknown fields only on held records. Explicitly declare any extra field on a free record malformed and test it. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:118,190`.

3. The exit-code row says malformed and foreign-host records produce exit 4 for mutating modes, contradicting the two override exceptions. Narrow code 4 to ordinary mutating modes when the applicable confirmed override is not being performed. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:139-148,177-184`.

4. The token rules conflict: one line permits a broad alphanumeric token, while the next requires exactly 32 lowercase hexadecimal characters. Delete the broad rule for `DebateId`/`Nonce` and use `\A[0-9a-f]{32}\z` for those values and their confirm forms. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:54-56`.

5. “Every parameter is `[string]`” cannot implement bare mode switches such as `-Acquire`, and real PowerShell parameter sets or mandatory parameters can reject an invocation before manual validation. To preserve the universal no-exit-1 claim, parse raw `$args` manually, including mode names, missing values, duplicate values, unknown names, and mode conflicts; otherwise narrow the exit-code guarantee. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:120-148`. The deleted implementation demonstrates that mode selectors were actual switches and typed values were binder-controlled. `tools/kimi-lane-lock.ps1` as shown by `git show 775472c^:tools/kimi-lane-lock.ps1:36-50`.

One reachable filesystem case is also missing: `-Status` is declared read-only, while the common open protocol creates and initializes a missing file. Freeze missing-file behavior. The least surprising rule is: status reports free without creating; release/overrides exit 5 without creating; only acquire may create the initial record. Add byte/nonexistence assertions for all modes. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:150-156,192-204`.

FIX — broaden malformed override to every readable malformed record; reject extra free fields; narrow exit 4 around the overrides; unify the token regex; replace binder-controlled parameter sets with raw argument parsing; and define absent-file behavior.

### Task 4 — Lock live gate

The synchronized ready marker proves truncation occurred before termination, and both zero-byte and partial-prefix outcomes are asserted before production acquire is invoked. Both hosts have explicit verification commands and a mutation test. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:210-233`.

PASS

### Task 5 — Login wrapper

Three execution gaps remain:

1. The plan says every alteration of shared lane state occurs under the lock, but immediately creates the lane home and rewrites its ACL before acquiring the lock. Because the lock lives inside that directory, bootstrap must be an explicit exception with prescribed concurrency behavior. State that directory creation and the idempotent same-identity ACL application are the only pre-lock operations. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:51,252-254`.

2. Acquire requires `-DebateHome`, but the wrapper neither accepts it nor says what value it supplies. Freeze it as the resolved lane-home path for a login operation, generate the login DebateId internally, capture the returned nonce, and release only when an acquired flag proves acquisition succeeded. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:123-126,241-254`.

3. Merely making the stub emit on both streams does not test inheritance. A wrapper that captures both streams until the child exits and then replays them could pass. Make the stub emit distinct stdout/stderr readiness markers and block; the parent must observe both markers before allowing it to finish, and neither marker may enter `VerdictOut`. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:250,258`.

The wrapper also needs a complete exit table. The plan specifies 0 and live contention 3 but leaves parameter refusal, malformed/foreign lock, invalid post-verdict, verdict-file failure, and runtime failure numerically open. Preserve the lock codes and assign invalid credential/verdict-write/runtime failures explicitly to 6. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:254-260`.

FIX — define bootstrap, the login lock identity and acquired flag, a temporal stream-inheritance oracle, and the full exit mapping.

### Task 6 — Builder

The conditional cleanup needs two flags, not one. As written, `!$buildCompleted` is also true when validation or acquire failed; release must be attempted only when `$lockAcquired -and -not $buildCompleted`. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:280-284`.

The added parameters are not declared mandatory/defaulted. Freeze `LaneHome`, `DebateId`, `OwnerPid`, and `OwnerStartTicksUtc` as mandatory strings in both modes, with `Nonce` additionally mandatory on remove. This matches the exact lifecycle invocation already written in Task 9. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:268-276,377-379`.

Two defined behaviors lack decisive tests:

- Successful remove must assert the home is absent and the persistent lock record is exactly `free`; otherwise deletion without release passes the current list.
- Add a cleanup-release fault seam and assert the original build failure remains primary while the release failure appears only on stderr. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:284-296`.

Finally, this existing module exercises Windows junctions and ACLs but Task 6 only changes its host selector. Add a module-level `os.name != "nt"` skip guard so Ubuntu’s installed `pwsh` cannot collect Windows filesystem tests. The current selector unconditionally falls back to whichever host is found. `evals/multi-model-verify/test_kimi_lane_home.py:15-21,123-124`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:32,297-299`.

FIX — add `$lockAcquired`, freeze parameter requirements, assert normal removal releases, fault-test release-error precedence, and mark the module Windows-only.

### Task 7 — Live credential gates

The three-home fixture still requires invention. No marker filename, schema, encoding, tick representation, or exact setup sequence is specified, even though the gate depends on comparing those markers. Prescribe an exact ASCII marker such as `.parallax-login-created-ticks-utc` containing one decimal UTC-ticks line, written immediately after successful login A and then successful login B; require `A < B`. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:307-313`.

The measure-once rule also leaves the implementer choosing which stream, which line, and what normalization constitutes the “exact error text.” Require the probe to exit nonzero, record stdout and stderr separately, define newline/path normalization, and pin the complete normalized output or a deterministically selected line. If no qualifying message exists, the measurement fails rather than producing a guessed pin. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:313-318`.

The deletion claim requires both hosts, but Task 7’s verification command runs only once without setting `PARALLAX_PS_HOST`. Run the module explicitly once with `powershell.exe` and once with `pwsh.exe`, as Task 4 already does. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:320,325-327`; compare `:226-231`.

FIX — freeze the marker contract and measurement normalization, and run the live suite explicitly under both hosts.

### Task 8 — Doctor matrix

The aggregate is not total. `N/A` is a credential contribution, but the stated ordering contains only `BROKEN > STALE > OK`; with a present valid binary, absent credential, and free lock, the implementer must invent whether the row is `OK` or `N/A`. Use `BROKEN > STALE > N/A > OK`, while retaining the binary-absent short circuit. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:335-351`. This also matches the doctor’s definition that N/A is non-failing but still a real row verdict. `commands/doctor.md:5-9`.

The matrix omits an unreadable lock, a missing lock tool, and a status invocation failure even though Task 3 explicitly allows status to exit 6. Add one row: any lock-status measurement failure is `BROKEN`, with no recovery command fabricated from unavailable evidence. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:148,192-200,337-351`.

“The doctor mutated a credential” is wider than two hashes establish: they show only that bytes changed during the interval, not which process changed them. Replace it with “credential bytes changed during the check; actor not established,” and describe equal hashes as “no net byte change observed.” `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:346,355`.

The separate authenticated-probe pin still has no exact literal. Supply the exact sentence before implementation, including that it is not part of check 8 and that it may refresh the dedicated lane credential. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:357-358`; `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:344-346`.

FIX — total-order N/A, add lock-status failure, narrow the hash claim, and provide the exact authenticated-probe literal.

### Task 9 — Contract

All three proposed literals contain no backslash, and each is one cohesive region: isolation, lock semantics, and call lifecycle. Adjacent Python literals are folded into one pin, and the checker imposes no character-length limit. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:365-385`; `CLAUDE.md:55-90`; `evals/multi-model-verify/contract_coverage.py:361-400`.

The normalized comparison and deletion mutation are now adequate oracles. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:381-391`; `evals/multi-model-verify/test_contract_coverage.py:21-30,517-526`.

The lifecycle literal is nevertheless incomplete for login: it says the wrapper takes the lock but omits the exact invocation and the wrapper’s internally generated DebateId, nonce custody, and `DebateHome` value. Add the Task 5 resolution to this same region; it remains one lifecycle region. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:377-379`.

FIX — extend `lane-lock-call-lifecycle` with the exact login lock call and custody rules; no region split is needed.

### Task 10 — Final wiring

Adding modules to both workflow steps has no oracle. The path checker proves only that referenced files exist; a module omitted from one host step remains green. Extend its workflow tests to assert that the required dual-host module set is contained in both Windows pytest steps, and mutation-test removing one module from one step. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:68-72,397-400`; `.github/workflows/skill-evals.yml:79-99`.

The final live rerun again executes only once under whichever selector happens to remain in the environment. Run it explicitly under both `powershell.exe` and `pwsh.exe`. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:399-404`.

FIX — add workflow host-parity validation and two explicit final live-suite invocations.

## Overall verdict

FIX. `-ConfirmHost` is sound, and the acquire table is now disjoint, but the record-class partition, login/bootstrap lifecycle, cleanup guard, doctor aggregation, and dual-host oracles are not yet complete. The fixes above are mechanical and require no design escalation.

## Final check

UNVERIFIED: measurements 1–21 remain externally taken measurements recorded by the design, not facts currently reproducible from committed repository gates. Tasks 4 and 7 propose future live gates for subsets, but those files do not exist yet. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:35-67`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:36-47,210-233,303-327`.

UNVERIFIED: the current remote-head and GitHub Actions assertions in Task 1. The local workflow and deletion history were inspectable, but network access failed, so I could not independently refresh `git ls-remote` or `gh run list`. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:60-66`.

UNVERIFIED: all proposed pytest and live gates. No implementation exists, and the unavailable `python` executable is not a finding. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:33,395-404`.