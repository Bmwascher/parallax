# Whole-branch fable review, TEST SLICE

**Range reviewed:** `6201e30..098e3e1`, branch `feat/kimi-code-backup-lane`.
**Slice:** `evals/multi-model-verify/` (`tests.diff`, read in full).
**Retained verbatim.** The reviewer's raw reply follows, unedited.

See the production-slice artifact for why the review was split, and for the
deviation that records it.

---

Range `6201e30..098e3e1`, slice: `evals/multi-model-verify/` (tests.diff, read in full). One focused production read was made to evaluate one named risk: `tools/new-kimi-lane-home.ps1:171`, to check a suspected stale absence needle against the shipped recovery command.

### Strengths

- The tests overwhelmingly answer "can this fail?" with yes, and prove it inline. Exit-code exhaustiveness tests assert every branch is reachable (`test_kimi_lane_lock.py:test_exit_code_exhaustiveness_across_the_bound_invocation_matrix`, `test_kimi_lane_login.py:test_exit_code_exhaustiveness`), and mutation-style pin self-checks show each doctor pin covers its load-bearing words (`test_backup_lane.py:1484-1490`, `1500-1504`, `1568-1571`).
- The four historical defect classes are each attacked directly: the blank-line class via the shared anchored helper and explicit `"\n\n{json}\n\n"` fixtures at every call position (`test_kimi_lane_login.py:test_validator_blank_line_padded_stdout_rejected_at_both_call_positions`, `test_lane_credential_live_support.py` sections 12/12b); scalar-`fields` via stub validators (`test_kimi_lane_home.py:test_builder_rejects_scalar_fields_from_the_validator`); the quoting defect via a fixture that deliberately combines apostrophe and space, with a comment forbidding fixture-shaping (`test_kimi_lane_home.py:test_the_recovery_command_row9_full_success_with_apostrophe_and_space`); and the junction-following `Path.resolve()` defect replaced by the five-step three-state oracle whose step 4 states that success REFUTES the measurement (`test_lane_credential_live.py:test_absolute_oauth_key_structural_oracle`).
- Token safety is engineered, not asserted: rotation comparisons use `if`+`pytest.fail` specifically to defeat pytest introspection (`test_lane_credential_live.py:8371-8374` in-diff, the `test_refresh_write_through` body), every validator invocation auto-scans both streams for every fixture token (`test_kimi_credential_state.py:run_validator`), and the SecretGuard tests prove value-free exceptions on timeout, decode failure, and match (`test_lane_credential_live_support.py` sections 7, 8, 15).
- Skip discipline follows the invariant: the live gate's only skip is the opt-in, and every setup fixture uses `pytest.fail` (`test_lane_credential_live.py` module header and fixtures); `test_lock_protocol_live.py` goes further and fails per-test on a missing host, with the measurement-20 divergence gate requiring both hosts to have provably run before comparing.
- `test_kimi_round_evidence.py` is exemplary: one-field mutations against a real captured fixture, distinguishing reason substrings so a neighbouring check cannot mask a neutered one (`test_active_tools_names_unequal_to_allowlist_fails`), the chained fresh-state-feeds-resume test that closes the rule-16 gap, both directions of the toolCount equality, and a working-tree CRLF hygiene test protecting the byte-exact offsets.
- Absence checks that pin nothing are honestly labelled as restoration guards, not coverage (`test_backup_lane.py:test_deleted_machinery_does_not_return` docstring), and `DECLARED_REGIONS` was edited alongside the region swap with the reused `lane-lock` name documented (`test_contract_coverage.py:625-660`); the eight new regions each have a whole-region `in`-form pin in `test_backup_lane.py`.

### Issues

#### Critical
None.

#### Important
1. **Stale absence needle: the "no recovery command was fabricated" oracle cannot fail.** Four tests assert `"$ownerJson" not in proc.stderr` (`evals/multi-model-verify/test_kimi_lane_home.py:963, 981, 1056, 1141`). `$ownerJson` comes from the superseded r20/r21 command; the shipped recovery command (`tools/new-kimi-lane-home.ps1:171`, mirrored by `RECOVERY_COMMAND_TEMPLATE` at `test_kimi_lane_home.py:757-759`) uses `$ownerLines` and never contains `$ownerJson`, so these asserts pass even if the builder DOES print the recovery command on those paths. Three of the four have other discriminators (exit code, fault message, empty stdout), but `test_validator_failure_is_not_an_actionable_state` (`test_kimi_lane_home.py:1043-1058`) carries its headline claim — validator failure fabricates no recovery command, a frozen plan requirement — on this dead needle alone. Fix is one line per site: use a token the current command actually contains, e.g. `$ErrorActionPreference` or `new-kimi-lane-login.ps1`.

#### Minor
1. **Teardown NameError masks setup failures in two contention tests.** In `test_kimi_lane_home.py:1128-1152` and `1179-1199`, `holder_nonce` is assigned after the acquire assert inside `try`; if that assert fails, the `finally` raises `NameError` and buries the real failure. The test still fails loudly, so this is diagnosis quality, not a false pass.
2. **The evidence-validator test helper accepts extra stdout.** `parsed()` in `test_kimi_round_evidence.py` (file lines ~255-258) parses only the LAST stdout line, so a validator that printed stray lines before its JSON would pass every test here. Exit code and status are still asserted, so the gap is narrow.
3. Note for the production-slice reviewer, since my slice cannot settle it: `test_the_junction_oracle` (`test_kimi_lane_home.py`, the physical-inventory step) rests on the measured claim that `Get-ChildItem -Recurse` does not descend junctions on BOTH hosts; the ledger's dual-host green runs are the evidence, and I could not independently re-verify the 5.1 behaviour from the diff alone.

### Ledger minors triage

- **Item 6's post-command merge running after assertions (round-31, carried):** RESOLVED, not riding — r32 froze the merge as a callback inside `dispatch_and_guard`, and the tests exercise exactly that ordering (`test_lane_credential_live.py` items 6/7 callbacks; `test_lane_credential_live_support.py:test_merge_after_command_catches_a_rotated_value`).
- **Trailer waiver (three `Claude-Session:` commits):** ride — user-authorized 2026-08-02, and the replacement guard names all three ids and fails on a fourth; nothing for the test slice to do.
- **Remote CI never run on this branch:** ride to the push gate — the workflow-paths checker plus the host-parity and duplicate-step oracles (`test_backup_lane.py:913-1080` in-diff) are the best offline mitigation this slice can provide.
- **Behavioral eval skipped its two manual-only cases, including this branch's own lane case:** ride — recorded honestly in the ledger, with the 63-per-host zero-skip live gate as the lane's actual coverage.

### Assessment

Ready to merge: **With fixes**. The slice is the strongest test work in this repo's history and its oracles overwhelmingly discriminate, but the one Important finding is precisely the defect class this plan exists to prevent — an assertion that holds whatever the code does — and it guards a frozen plan requirement, so the four stale `$ownerJson` needles should be repointed before merge; the minors can ride.
