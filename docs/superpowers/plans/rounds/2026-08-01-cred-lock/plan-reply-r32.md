Not PASS yet. I accept the refutation’s narrow point: the hostile-model case does acquire and subsequently release the lock. But Task 7 still has three blocking defects, and the mechanical blank-line sweep found nine surviving weak oracles across four earlier tasks.

## Task 7

### 1. Finding 3: refutation accepted, but the oracle remains incomplete

Acquire completes and sets `$lockAcquired` before model validation; the hostile model then throws and the `finally` releases the lock. Your reading is correct. `tools/new-kimi-lane-home.ps1:561-574`, `tools/new-kimi-lane-home.ps1:609-617`, `tools/new-kimi-lane-home.ps1:943-954`.

However, Task 7 requires the real failed-build deletion path, not merely failed-build lock release. The debate directory and junction are not created until after the hostile-model refusal, while recursive cleanup is conditional on `$createdByThisInvocation`. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:657`, `tools/new-kimi-lane-home.ps1:821-852`, `tools/new-kimi-lane-home.ps1:923-940`.

Specific fix:

1. Run with both `PARALLAX_LANE_HOME_FAULT=1` and `PARALLAX_LANE_HOME_CLEANUP_DELETE_FAULT=1`. Require the pre-emission fault and cleanup-deletion sentinel, the debate home still present with its junction, and the lock `free`. This proves the build reached the post-junction cleanup branch. `tools/new-kimi-lane-home.ps1:901-910`, `tools/new-kimi-lane-home.ps1:927-939`.
2. Run with only `PARALLAX_LANE_HOME_FAULT=1`. Require no custody stdout, debate home absent, lock `free`, and C’s credential byte-identical. That proves recursive cleanup does not traverse the junction.
3. Keep the hostile-model case only as an optional release-only control.

No additional measurement is needed to settle your refutation itself; source order settles it.

The builder comment should also be corrected: “before ANYTHING touches the filesystem” is false because lock mutation and credential validation already occurred. Say “before destination creation or rendering.” `tools/new-kimi-lane-home.ps1:561-586`, `tools/new-kimi-lane-home.ps1:609-612`.

### 2. One-debate-id rule was applied incompletely

The plan requires one debate ID per home for the entire module run, but the failed-build test generates a fresh ID and does not receive the `debate_ids` fixture. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:633`, `evals/multi-model-verify/test_lane_credential_live.py:347-363`.

Specific fix: add `debate_ids` to that test and pass `debate_ids["C"]`.

### 3. Finding B is real; choose neither proposed option

A plan carve-out would weaken an explicit security ordering: item 6 must merge before guarding and before streams become available to assertions. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:629`, `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:641-646`.

A generic lenient mode is also wrong. `merge_credential_file()` returns the same `False` for an unreadable file and malformed JSON, so it would treat an unmade measurement like an expected garbage/absent fixture. `evals/tools/lane_credential_live_support.py:614-626`.

Use the callback form already permitted by the plan:

- `dispatch_and_guard(..., post_capture_merge=callback)` invokes the callback after capture and before scanning, on both normal and timeout paths.
- A/B/C pass the existing strict `reread_and_merge_credential` operation.
- Item 6 passes a fixture-specific callback with an expected state:
  - `valid`: read, parse, and merge must succeed.
  - `garbage`: the read must succeed and parsing must fail as expected.
  - `absent`: absence must be measured successfully; other filesystem errors fail closed.
- Only after that callback succeeds may the guard scan and return the streams.

Currently item 6 omits `cred_path`, receives guarded streams, asserts them, and only then attempts its merge. `evals/multi-model-verify/test_lane_credential_live.py:404-430`. The helper itself only merges when `cred_path` is supplied. `evals/tools/lane_credential_live_support.py:671-708`.

Also repair the read-failure oracle: it presently calls `dispatch_and_guard` without a credential path and manually raises the read failure after the helper returned. It therefore does not test the helper’s promised failure boundary. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:684`, `evals/multi-model-verify/test_lane_credential_live_support.py:757-779`.

**Task 7: FIX — BLOCKING: exercise actual post-junction deletion, reuse C’s module debate ID, and move item 6’s measured merge plus the read-failure oracle inside the capture helper.**

## Mechanical blank-line sweep

Yes, this class can be checked mechanically. The fixed implementation already demonstrates the correct shared regex and uses it for both validator and custody output. `evals/tools/lane_credential_live_support.py:267-305`, `evals/tools/lane_credential_live_support.py:334-355`.

A targeted repository sweep found nine remaining weak exact-one oracles:

- Task 2: one validator-output parser. `evals/multi-model-verify/test_kimi_credential_state.py:110-124`.
- Task 4: one measured type-report parser. `evals/multi-model-verify/test_lock_protocol_live.py:328-347`.
- Task 5: six `-VerdictOut` parsers. `evals/multi-model-verify/test_kimi_lane_login.py:382-384`, `evals/multi-model-verify/test_kimi_lane_login.py:443-445`, `evals/multi-model-verify/test_kimi_lane_login.py:710-712`, `evals/multi-model-verify/test_kimi_lane_login.py:725-727`, `evals/multi-model-verify/test_kimi_lane_login.py:984-986`, `evals/multi-model-verify/test_kimi_lane_login.py:1013-1015`.
- Task 6: one custody parser. `evals/multi-model-verify/test_kimi_lane_home.py:363-368`.

All discard blanks before requiring one survivor, contrary to the frozen rule that leading, interior, and extra blank lines are rejected. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:98-103`.

Specific mechanical fix:

1. Extract one shared `accept_exactly_one_nonempty_line()` helper using `\A([^\r\n]+)(\r\n|\n)?\Z`.
2. Replace all nine sites.
3. Add an AST-based repository test that rejects an assignment from a blank-filtering `splitlines()` comprehension when the assigned value is subsequently tested as having length one in the same scope.
4. Mutation-test the checker with:
   - the bad filter/count idiom, which must fail;
   - an intentional multi-record blank filter, which must pass;
   - the strict regex helper, which must pass.

This mechanically catches the syntactic class. It cannot prove that arbitrary differently written parsers have equivalent semantics, but it stops this exact recurring implementation from returning unnoticed.

**Task 2: FIX — replace the weak exact-one classification oracle and include it in the mechanical check.**

**Task 4: FIX — replace the weak measurement-output oracle; otherwise blank-padded output still counts as one measurement.**

**Task 5: FIX — replace all six weak `-VerdictOut` oracles.**

**Task 6: FIX — replace `_parse_custody`; also correct the false pre-filesystem comment.**

## Task 10

The mechanical checker should become part of the full-suite gate before finalization. Task 10 also still requires both opt-in live invocations at final HEAD with zero skipped. `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:798-808`.

The ledger correctly records that this gate has never run and that measurements 5, 6, 7, 10, 11, 16, and 17 therefore remain unverified. `docs/superpowers/plans/rounds/2026-08-01-cred-lock/build-ledger.md:48-64`.

**Task 10: FIX — add the mechanical exact-line gate and complete both zero-skip live runs after the three human logins.**

## Overall verdict

**FIX.** Your refutation is accepted regarding acquisition and release, but the test still does not exercise failed-build directory deletion. Task 7 additionally violates the per-home debate-ID rule and item 6’s frozen merge-before-guard boundary. The mechanical sweep also reopens Tasks 2, 4, 5, and 6 at the oracle layer.

## Final check

UNVERIFIED:

- The Task 7 live suite under either host; the repository ledger says it remains unrun. `docs/superpowers/plans/rounds/2026-08-01-cred-lock/build-ledger.md:48-64`.
- Measurements 5, 6, 7, 10, 11, 16, and 17 at current HEAD.
- The reported 51-tests-per-host and 840-test full-suite runs were not independently rerun in this review.
- The three manual logins have not yet been evidenced by an executed zero-skip gate.

