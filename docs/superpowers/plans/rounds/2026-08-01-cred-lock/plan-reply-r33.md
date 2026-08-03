Task 7 is still FIX. All three reported defects are real. I also found one masked failure classification, and the mojibake should be fixed now because it weakens the secret guard’s stated coverage.

## 1. Absolute-key oracle

“Make the default unreachable” is the correct shape. No discriminating oracle can keep the junction at its active `credentials` location: the current relative control and absolute case both ultimately reach the same credential, and `Path.resolve()` is used before writing the supposedly absolute key. `evals/multi-model-verify/test_lane_credential_live.py:225-257`.

Do not create another credential copy. Use C’s real credential directly while C’s builder-retained hold remains active:

1. Run the existing relative-key positive control: exit 0 and `PROBE`.
2. Rename the `credentials` junction to a non-default name, then prove `<debate-home>/credentials/kimi-code.json` is absent while C’s real credential remains readable.
3. Set `oauth.key` to a nonexistent absolute path. Require nonzero and no `PROBE`. This proves there is no fallback capable of producing success.
4. Set it to the absolute path of C’s real credential file. Run twice. Both must exit nonzero and produce no `PROBE`; either success refutes measurement 5.
5. Scan every stream and re-read C’s credential through the strict callback throughout.

The missing-path negative control is load-bearing: merely removing the default and testing one absolute path cannot distinguish “absolute paths are unsupported” from unrelated fallback or configuration behavior. The design licenses only “absolute path does not resolve,” not a particular diagnostic. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:45-56`, `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:652-655`.

**Defect 1: FIX — make the default unreachable and add the missing-absolute negative control before testing C’s valid absolute credential.**

## 2. Replace the text pin with a structural oracle

Choose the structural invariant. Do not widen normalization.

The varying summary and session ID are behaviorally irrelevant client prose. Removing them through normalization would indeed be a selector disguised as normalization, contradicting the plan’s reason for rejecting selected lines. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:610-619`.

Freeze these assertions instead:

- Relative-key control: exit 0 and stdout contains `PROBE`.
- Missing absolute target with no default: nonzero and stdout does not contain `PROBE`.
- Valid C absolute target with no default, twice: both nonzero and neither contains `PROBE`.
- C’s credential remains measurable and guarded after every command.
- No exact stdout, stderr, session ID, summary line, or particular nonzero numeric code is pinned.

The exact numeric exit code is wider than the design requirement; only zero versus nonzero carries the fact being measured. `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:51`, `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:104-105`.

Delete the probe-record refresh machinery and its message-stability oracles rather than leaving a dead “pin” beside the replacement. The current gate compares complete tuples before checking whether the supposedly failing case exited 0, so nondeterministic streams mask the more important failure as `ProbeRecordUnstable`. `evals/tools/lane_credential_live_support.py:1101-1122`, `evals/tools/lane_credential_live_support.py:1128-1146`.

That is the fourth defect in the five-failure path: the gate’s decision order hides “absolute key unexpectedly succeeded” behind stream instability. Removing the textual gate closes it; if any portion remains temporarily, check the zero/nonzero classification before stability.

**Defect 2: FIX — remove the complete-stderr pin and probe-record lifecycle; pin the three structural outcomes above.**

## 3. Secret-guard exclusion

Exclude exactly `scope` and `token_type`, by field name, at merge time. Record it in the plan as a security decision, not merely as a helper constant.

The frozen schema distinguishes required token fields from optional `scope` and `token_type`, while the implementation currently retains every nonempty string indiscriminately. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:81-84`, `evals/tools/lane_credential_live_support.py:602-618`.

Freeze:

```python
NON_SECRET_CREDENTIAL_FIELDS = frozenset({"scope", "token_type"})
```

Rules:

- Those two fields never enter the retained secret union.
- `access_token` and `refresh_token` always do.
- Every unknown future string field still enters it.
- No length or entropy threshold is introduced.
- If a metadata field and a secret field contain the same value, the secret field still causes retention and detection.

Required oracles:

- `scope` and `token_type` appearing in ordinary output do not fire.
- Each token field still fires independently.
- An unknown string field fires.
- A token sharing its value with excluded metadata still fires.

This preserves the fail-safe direction for unknown fields while removing only the two named false-positive sources. The current guard’s value-to-field map makes the shared-value oracle important. `evals/tools/lane_credential_live_support.py:603-645`.

**Defect 3: FIX — exclude exactly `scope` and `token_type`, with the decision and the four directions above frozen in Task 7.**

## 4. Mojibake is not merely cosmetic

Close it now. `dispatch_and_guard` captures with `text=True` but no explicit encoding, while timeout bytes are decoded separately using UTF-8 with replacement. The normal and timeout paths therefore do not share one byte-to-text contract. `evals/tools/lane_credential_live_support.py:677-723`.

That matters to the secret guard: credentials are read as UTF-8, but captured output decoded through a different or lossy codec may not compare equal to the same non-ASCII value. The plan claims every retained string is scanned before exposure, not only ASCII tokens. `evals/tools/lane_credential_live_support.py:627-645`, `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:637-646`.

Specific fix:

- Capture bytes, not locale-decoded text.
- Decode both normal and timeout streams through one strict UTF-8 helper.
- On invalid UTF-8, raise a fixed value-free `DispatchDecodeFailure`; expose neither captured stream.
- Add normal and timeout invalid-byte oracles.
- Add a Unicode fake-secret oracle proving a correctly encoded non-ASCII secret is caught.

**Additional Task 7 finding: FIX — BLOCKING because locale-dependent decoding can defeat the guard’s broader contract.**

## Task verdicts

**Task 7: FIX — BLOCKING.** Replace item 1 with the three-state structural oracle, remove the unstable prose pin, exclude exactly the two metadata fields, and make capture decoding explicitly UTF-8 and fail-closed.

**Task 10: FIX.** `pwsh.exe` remains unrun, and the final-HEAD gate explicitly requires both hosts with zero skipped. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:818-826`.

The build ledger must also be updated: it still says the live half never ran and the three homes do not exist, which now contradicts the reported execution. `docs/superpowers/plans/rounds/2026-08-01-cred-lock/build-ledger.md:48-64`.

## Overall verdict

**FIX.** The seven passing live cases are meaningful progress, especially the failed-build deletion path, but Task 7 cannot pass until the absolute-key oracle is discriminating, the unstable text pin is removed, metadata cannot trip the guard, decoding is deterministic, and both hosts pass at final HEAD.

## Final check

UNVERIFIED:

- The reported `powershell.exe` result of 7 passed and 5 failed; no retained run artifact currently records it.
- The reported three-login coexistence and unchanged real-user credential.
- Measurement 5’s original external procedure; the spec records only its conclusion, not enough fixture detail to compare against the newly discovered oracle flaw.
- The reported 51-test and 849-test runs.
- `pwsh.exe` live execution, which has not yet occurred.

