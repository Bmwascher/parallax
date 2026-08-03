# Whole-branch fable review, PRODUCTION SLICE

**Range reviewed:** `6201e30..098e3e1`, branch `feat/kimi-code-backup-lane`.
**Slice:** `tools/`, `evals/tools/`, `skills/`, `commands/`, `agents/`,
`.github/`, `.claude-plugin/`, `hooks/` (`production.diff`, read whole).
**Retained verbatim.** The reviewer's raw reply follows, unedited.

The diff is 1.9 MB and does not fit one context, so the controller split it
into a production slice and a test slice and ran two reviewers concurrently,
each holding the whole-branch commit list and stat so each could see what it
was not given. That split is a controller decision recorded as a deviation:
no single reviewer saw the whole diff at once.

---

Range: `6201e30..098e3e1`, branch `feat/kimi-code-backup-lane`. Slice: `tools/`, `evals/tools/`, `skills/`, `commands/`, `agents/`, `.github/`, `.claude-plugin/`, `hooks/` (`production.diff`, read whole). Repo files read directly, one focused check per named risk: `.github/workflows/skill-evals.yml` (claim width: is `check_workflow_paths.py` actually wired into CI; answer: yes, through Tier 2b pytest via `test_backup_lane.py:1094-1272`, so its docstring claim is accurate), `tools/read-kimi-round-evidence.ps1:336-341`, `tools/kimi-lane-lock.ps1:293-299`, `tools/check-drift.ps1:221-256`, `tools/new-kimi-lane-home.ps1:201,591` and `tools/new-kimi-lane-login.ps1:232` (fail-open and claim-width risks named below).

### Strengths

- **The credential fork is genuinely closed.** The builder carries no `Copy-Item` and no reference to the user's credential path; `credentials` is a junction to the lane home (`tools/new-kimi-lane-home.ps1:527-529` in-diff, junction block), the lane credential is validated under the lock before the junction is cut, and the login wrapper scopes `KIMI_CODE_HOME` to the one client call and restores it in a `finally` covering both prior states (`tools/new-kimi-lane-login.ps1:216-227` in-diff).
- **Secret discipline is layered and value-free.** `read-kimi-credential-state.ps1` emits field names and frozen status pairs only; the live-support `SecretGuard` retains rotated-away values forever, scans both streams before any return, runs the merge callback before the scan so a just-issued token is in the union (`evals/tools/lane_credential_live_support.py:1555-1606`), and the strict single UTF-8 decode contract closes the mojibake-defeats-the-guard path.
- **The lock is a real state machine.** CreateNew-then-Open with no deletion path ever, three-outcome liveness with UNMEASURABLE treated alive by every mutating mode, `-cmatch` for the hex tokens with the live reproduction documented (`tools/kimi-lane-lock.ps1:179-186`), zero-length-file handling with the `,`-return trap explained, explicit stream close before every `exit` because `exit` bypasses an enclosing `catch`, and a monotonic Stopwatch wait budget.
- **Fail-closed is enforced, not asserted, in the new checkers.** `check-drift.ps1` refuses an unparseable version rather than passing the floor (`tools/check-drift.ps1:256`), stops the flag loop when `--help` itself could not be measured, and probes the client by absolute path so PATH cannot substitute the superseded binary. `check_workflow_paths.py` treats host-step discovery as part of the measurement, keeps steps as a list with multiset host counting, and freezes readability as an actual binary open.
- **The evidence validator is the strongest text in the slice.** Byte offsets plus prefix hashes prove identity rather than length, two record classes with presence required on fresh and absence required on resume, brief-hash canonicalization stated as part of the rule, and a check that could never fail was removed with the reasoning recorded in place (`tools/read-kimi-round-evidence.ps1:64-70` header history).
- **CI repair is complete and mirrored.** Both Windows host steps carry the same ten modules, the exact-line gate runs at Tier 1c, and the workflow checker is exercised against the real workflow inside the ubuntu job.

### Issues

#### Critical

None found.

#### Important

1. **`Get-SessionLeaves` suppresses enumeration errors in the route-attribution gate.** `tools/read-kimi-round-evidence.ps1:340` uses `Get-ChildItem -Recurse -ErrorAction SilentlyContinue`. A partly failed enumeration is silently accepted, so the fresh branch's "exactly one new session leaf" rule (rule 3) can be satisfied on an incomplete inventory: a second, concurrent session leaf inside an unenumerable subtree is simply not counted while the expected leaf passes the id match. This is the same suppressed-read class the plan bans by name in the four-part rule (`Get-Content -ErrorAction SilentlyContinue` was called "the governing invariant, inverted"), sitting inside the validator whose header says every rule fails closed. The practical window is narrow (the sessions root lives in a builder-created, ACL-protected home), which is why this is Important and not Critical, but it is the plan's own invariant broken inside its own enforcement tool. Fix: make the enumeration terminating and map any failure to a `Fail`.

2. **Case-insensitive `-eq` accepts case-variant literals where the shipped contract promises exact schema.** `tools/kimi-lane-lock.ps1:293-299` checks the state literal with `-ne "free"` / `-ne "held"` and branches on `-eq "free"`, all case-insensitive, so `{"version":1,"state":"Free"}` classifies as a well-formed free record and an acquire writes over it. The pinned `lane-lock` contract region (backup-lane.md) says a record that does not "exactly satisfy the record schema, version 1, one of the two state literals" is held and reported, never treated clean; the code is looser than the shipped claim, in the fail-open direction. Same family at `tools/new-kimi-lane-home.ps1:201`, `tools/new-kimi-lane-login.ps1:232` (`Test-ValidVerdictPair` with `-eq` accepts `"OK"`/`"Valid"`), `tools/new-kimi-lane-home.ps1:591` (`Status -ne "ok"`), and the evidence validator's `mode -ne "auto"`. Notably the Python twin enforces exact case (`VALID_VERDICT_PAIRS` membership, `lane_credential_live_support.py:895-904`), so the same frozen rule is implemented at two strictnesses. This branch itself documents this exact class as a live-reproduced defect and fixed it for the hex tokens with `-cmatch`; the remaining `-eq` literals are the unfixed instances. Fix: `-ceq`/`-cne` on the literals, or narrow the contract text, and this can only be settled with a failing oracle, so the test-slice reviewer should confirm whether any exists (named gap, route it).

#### Minor

3. **The exact-line gate silently skips files it cannot read or parse.** `evals/tools/check_exact_line_oracles.py:169-178`: `UnicodeDecodeError`, `OSError` and `SyntaxError` all `continue`, so a file the gate cannot measure reads as clean. The docstring's LIMIT paragraph honestly bounds the syntactic claim but does not name this skip. Low risk today (every repo `.py` is UTF-8 and parseable or the suite would fail), but it is a silent exemption in a gate built because three sweeps missed instances.
4. **Stale count in `check_workflow_paths.py`.** The comment above `REQUIRED_DUAL_HOST_MODULES` (`evals/tools/check_workflow_paths.py:55-58`) says "exactly these four" above a ten-entry list. The plan's own r27 lesson was to enumerate rather than count precisely because this sentence class goes stale; this one went stale the same way.
5. **`check-drift.ps1` interpolates the raw version string into findings.** `$kimiVersion` is now the untrimmed-in-the-middle raw output (`tools/check-drift.ps1:230-256`); a multiline `--version` output would produce a multiline finding line. Cosmetic; the floor logic itself fails closed on it.

### Ledger minors triage

- **Item 6 post-command merge outside the capture helper (r31, carried):** ride, actually CLOSED. `dispatch_and_guard` now makes capture, callback and scan one indivisible operation and item 6 homes pass fixture-specific callbacks (`lane_credential_live_support.py:1555-1606`).
- **Trailer waiver (three `Claude-Session:` commits):** ride. Authorized debt, user-decided, guarded by exact commit ids with a fourth failing, and the guard claims no more than it scanned.
- **Remote CI never run on this branch:** ride as a named gap. Nothing in the record may read as CI-verified until the pushed workflow completes; the mirrored dual-host lists reduce but do not remove that risk.
- **Behavioral eval skipped `backup-lane-consented-substitution` (the branch's own subject):** ride. The 63-per-host, zero-skip live gate is the covering evidence and the ledger states that boundary correctly.
- **Task 7 live gate formerly UNSATISFIED:** closed by the recorded live run; no action.

### Assessment

Ready to merge: **With fixes.** The credential fork, the lock protocol and the CI repair are sound and unusually well evidenced, and nothing in the slice can print, copy or expire the real credential; the two Important findings are small, contained edits (a terminating enumeration in the evidence validator, case-exact literal comparisons or a narrowed contract sentence) but both are live instances of the exact defect classes that reopened this plan twelve times, inside the surfaces that enforce them, so they should land before the mode-diff debate treats the branch as settled.

Named gaps for routing: whether failing oracles exist for the suppressed-enumeration path and for case-variant state/status literals lives in `evals/multi-model-verify/`, which is the other reviewer's slice.
