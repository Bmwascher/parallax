R4 is not yet a PASS. The binder narrowing is sufficient, and most round-4 changes are correct, but three Task 3 partition defects remain and several new oracles/lifecycles are still underspecified. All are blocking under the zero-judgment contract; none requires design escalation.

### Task 1 — CI repair

Host parity is now the right oracle, but its initial declared module set is not frozen. Before Task 10, the workflow contains four surviving dual-host modules after the orphan is removed; an implementer must decide which enter the required set. `.github/workflows/skill-evals.yml:79-99`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:74-80,442-443`.

Freeze the initial set as:

- `test_attestation.py`
- `test_codex_context_probe.py`
- `test_review_mirror.py`
- `test_kimi_round_evidence.py`

Task 10 then adds its five named modules. The parity mutation removes one member from one host step.

FIX — enumerate the checker’s initial four-module required set.

### Task 2 — Credential validation

The validator’s behavioral matrix is complete, but the shared-fixture modification has no Task 2 oracle. The current builder suite does not structurally validate `_fake_profile`’s credential, and its selector ignores `PARALLAX_PS_HOST` until Task 6. Therefore omitting the `refresh_token`/`expires_at` fixture change can pass Task 2’s advertised two-host gate. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:107-114`; `evals/multi-model-verify/test_kimi_lane_home.py:21,310-320`.

Move the lane-home selector refactor and module guard into Task 2, and add a test that creates `_fake_profile`, runs the new validator against its credential, and requires `status=ok` under each selected host. Task 6 can then treat that refactor as already complete.

FIX — directly exercise the changed shared fixture with the validator under both hosts.

### Task 3 — Lock tool

The binder narrowing is sufficient. Successfully bound invocations own codes `{0,2,3,4,5,6}`; binder rejection owns code 1 and is mutation-tested. This accurately reflects PowerShell’s binder boundary. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:132-159,221`; deleted `tools/kimi-lane-lock.ps1` at `775472c^:36-50`.

The unified token rule and per-mode missing-file behavior are also correctly applied. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:58-60,161-169`.

Three partition defects remain:

1. A free record carrying a held-only but globally known field, such as `host`, is excluded by the exact free schema but not clearly included by the exhaustive `MALFORMED` definition. “Unknown field” does not cover a known field illegal in that state. Specify: a free record containing any property other than `version` and `state` is malformed. Test both a held-only property and a wholly unknown property. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:124-130,207`.

2. `-MalformedOverride` on a well-formed foreign-host record has two outcomes. Row 9 says every well-formed record exits 5, while exit-code 4 and the foreign-host rule say the wrong override mode exits 4. Scope row 9 to free or same-host well-formed records, and add a foreign-host row returning 4. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:156,183-201`.

3. Code 5’s meaning covers only identity/hash mismatch, but missing-file and free-record rows also return 5. Change its meaning to “release or override refused because there was nothing applicable to release, or the supplied identity/hash did not match.” `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:151-159,187-197`.

For a mechanically total partition, insert this preprocessing before the release/override table:

- unreadable → 6 for every mode;
- readable malformed → 4 except `MalformedOverride`, which uses hash rows;
- readable well-formed foreign held → 4 for `Release` and `MalformedOverride`, while `ForceRelease` uses identity rows;
- remaining rows are missing, free, or same-host well-formed held.

Add explicit tests for each foreign-host/mode pairing.

FIX — reject every non-free property on free records, remove the foreign-host overlap, and widen code 5’s description.

### Task 4 — Lock live gate

The synchronized zero-byte and partial-prefix crash paths, two explicit hosts, and inverted measurement-20 mutation test remain decisive. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:231-252`.

PASS

### Task 5 — Login wrapper

The bounded bootstrap, captured nonce, acquired flag, lane-home `DebateHome`, and temporal stream oracle are correctly applied. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:269-283`.

The new exit table introduced three gaps:

1. Unlike Task 3, it is not scoped to successfully bound invocations and omits binder code 1. Apply the same narrowing and mutation test. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:260-266,279-281`.

2. It says lock codes are preserved but omits code 5. A release can return 5 if the record was freed or displaced before `finally`. Add code 5. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:275-281`; the lock’s release rows are at `:187-193`.

3. Release-failure precedence is undefined. Freeze: if the main operation already failed, preserve that original code and write the release failure to stderr; if the main operation succeeded but release failed, return the release code. Test both directions.

The sentence “post-run verdict decides” also needs its opposite-direction oracle: client exits nonzero but leaves a structurally `ok` credential, and the wrapper exits 0. Otherwise an implementation that incorrectly propagates the client code passes every listed case. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:275-281`.

FIX — scope binder code 1, add lock code 5, freeze release-failure precedence, and test nonzero-client/valid-credential success.

### Task 6 — Builder

The two-flag predicate is correct, but `$buildCompleted` is set too early. The frozen order sets it immediately after filesystem rendering, before the required nonce-custody JSON is emitted. If JSON construction or output fails, `finally` retains a lock whose caller never received its nonce. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:299-311`.

Keep JSON construction and emission inside the guarded build `try`, and set `$buildCompleted = $true` only immediately after the one success line is emitted. Any earlier failure must run failed-build cleanup and release.

Both internal acquires also need their `DebateHome` frozen:

- Build: resolved `-Path`.
- Remove’s idempotent re-acquire: the same resolved `-Path`.

The lock requires that parameter, but Task 6 currently does not say what the builder supplies. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:135-138,307-315`.

Finally, replace the unnamed acquire-failure seam with a real held-by-different-owner fixture; it is a stronger oracle and needs no invented seam. Name the cleanup seam exactly `PARALLAX_LANE_HOME_CLEANUP_RELEASE_FAULT`, firing only after an original build failure and immediately before cleanup release. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:311,323`.

FIX — emit custody JSON before marking completion, freeze both `DebateHome` arguments, use a real acquire refusal, and name the cleanup-release seam.

### Task 7 — Live gates

The marker format and two-host execution are correctly frozen. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:338-365`.

Three blocking gaps remain:

1. Error normalization still delegates a choice: complete stderr “or if that is not stable” a selected line. Freeze complete normalized stderr as the oracle. Replace the resolved fixture root, case-insensitively, with exactly `<fixture-root>`; normalize CRLF to LF; trim one terminal newline. Run twice. If outputs differ after normalization, stop and amend the plan—do not let the implementer select a line. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:346,350`.

2. Before writing `probe-record.md`, compare captured stdout/stderr against every known credential string value. If one appears, fail naming only the field, write nothing, and never include the value in pytest output. The current plan records complete client streams while globally forbidding credential values in logs or commits. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:29,346`.

3. The token-rotation assertion can leak real token values through pytest assertion introspection. Compare the values through ordinary `if` branches and call `pytest.fail("access_token did not rotate")` or the refresh-token equivalent; never place either value in an `assert` expression or failure message. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:29,352`.

Freeze the C-fixture lock identity as well: call `-ResolveOwner` once per module run, use resolved home C as both `LaneHome` and `DebateHome`, generate one run DebateId, capture the nonce, and release with that complete identity. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:135-144,344`.

FIX — remove the normalization choice, add a secret-output guard and non-disclosing token assertions, and freeze C’s complete lock invocation.

### Task 8 — Doctor matrix

The total verdict order, missing-status row, narrowed hash claim, and authenticated-probe literal are correctly applied. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:374-399`; `commands/doctor.md:5-9`.

The “exact” hash procedure is not executable as stated. It says to confirm readability before hash 1, but also requires reporting validator and hash substates; a hash-1 failure can prevent the validator from running and leaves those substates unmeasured. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:376-395`.

Replace it with this exact algorithm:

1. Test existence.
2. If absent, run the validator, require `absent`, take no hash.
3. If present, attempt hash 1 and record success/failure.
4. Run the validator regardless of hash-1 success.
5. If still present, attempt hash 2; disappearance is `BROKEN`.
6. Compare only if both hashes exist.
7. Any hash failure is `BROKEN`, but does not suppress the validator detail.

The recovery commands are also described but not literal. Freeze the complete templates using every Task 3 parameter:

- `tools/kimi-lane-lock.ps1 -ForceRelease -LaneHome <lane-home> -ConfirmHost <host> -ConfirmOwnerPid <pid> -ConfirmOwnerStartTicksUtc <ticks> -ConfirmDebateId <id> -ConfirmNonce <nonce>`
- `tools/kimi-lane-lock.ps1 -MalformedOverride -LaneHome <lane-home> -ConfirmSha256 <sha256>`

`docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:140-143,389-401`.

FIX — replace the hash prose with the seven-step algorithm and freeze both complete recovery commands.

### Task 9 — Contract

The exact literals still have no backslashes, remain cohesive single-pin regions, and use the correct normalized substring oracle. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:409-434`; `CLAUDE.md:55-90`.

The newly expanded login lifecycle is wrong for a custom lane home. Build takes `-LaneHome <lane-home>`, but login omits `-LaneHome`, silently using the default and authenticating a different home. Add `-LaneHome <lane-home>` to the exact login invocation. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:261-266,423`.

Replace “Remove with the same four values plus…” with the full command:

`tools/new-kimi-lane-home.ps1 -Path <debate-home> -Remove -LaneHome <lane-home> -DebateId <id> -OwnerPid <pid> -OwnerStartTicksUtc <ticks> -Nonce <nonce>`

That removes the remaining operator inference from the call-lifecycle region. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:297,313-315,423`.

FIX — pass the custom lane home to login and spell out the complete remove command.

### Task 10 — Final wiring

Once Task 1 freezes the initial required set, Task 10 explicitly adds all five new modules to both the workflow and parity checker, reruns every main gate, and reruns the credential live suite under both hosts at final HEAD. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:438-460`.

PASS

## Round-4 application audit

Correctly applied and accepted as-is:

- binder guarantee narrowing;
- unified token rule;
- missing-file behavior;
- bounded login bootstrap;
- temporal stream oracle;
- two cleanup flags as a predicate;
- marker schema and explicit host runs;
- doctor’s total ordering, status-failure row, hash-claim narrowing, and authenticated-probe literal;
- host-parity concept and final dual-host rerun. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:58-60,149-169,271-283,311,340-365,374-403,442-452`.

Applied incompletely or with a new defect:

- Task 3’s malformed/free/exit-code edits still leave the foreign-host overlap and held-only-field gap. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:130,156,183-207`.
- Task 5’s new exit table omitted binder code 1 and lock code 5. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:279-281`.
- Task 6’s completion flag is now explicitly placed before custody output. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:299-311`.
- Task 7’s “frozen” normalization retains an implementer-selected fallback. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:346`.
- Task 9’s new login literal omits the custom lane home used by the same lifecycle. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:423`.

## Overall verdict

FIX. Every finding above is BLOCKING under the plan’s zero-judgment and oracle-adequacy contracts. I found no merely advisory objection that I would ask you to change. There is no design deadlock and no ESCALATE item.

## Final check

UNVERIFIED: measurements 1–21 remain externally taken measurements recorded in the design rather than currently committed, runnable repo gates. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:35-67`; `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:40-51`.

UNVERIFIED: every proposed pytest/live result, because implementation files have not been written and the sandbox has no runnable `python`; this is not a finding. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:37,438-453`.

UNVERIFIED: the current remote-head and Actions-run assertions in Task 1; repository-local workflow/deletion facts were inspectable, but current remote state was not refreshed. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:64-70`.

