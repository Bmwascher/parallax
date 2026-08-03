The revision is materially stronger, but all five claims still need fixes. Several new defects are implementation-breaking.

1. `round-freshness-boundary` fully restores freshness

It restores ordinary append-only freshness, but not file identity. The rule detects only absence or a post-call length smaller than the captured offset (`2026-07-31-kimi-code-swap.md:741-755`; validator rules at `:683-690`). A replaced, truncated, then regrown file with length at least the old offset passes the boundary even though the prefix no longer identifies the same stream. Per-session log rotation remains explicitly unverified (`probe-record.md:248-249`).

That is the same false-negative shape for which the old contract eventually added creation-time identity. Per-session isolation removes foreign-session attribution, but it does not prove that a cumulative file was not replaced between measurements.

The test list also has a wire-truncation case but no corresponding log-truncation or log-offset-zero stale case (`2026-07-31-kimi-code-swap.md:655-670`).

Verdict: **FIX — capture and verify file identity plus a hash of the pre-call prefix, or otherwise prove the prefix is unchanged; add symmetric wire and log freshness tests.**

2. Task 5’s failure cases are sufficient

Several validator requirements have no listed negative test:

- `llm.tools_snapshot` can carry the wrong tool names while `tools.set_active_tools.names` remains correct. Rule 6 requires snapshot equality, but no listed test mutates it (`2026-07-31-kimi-code-swap.md:655-670,687-689`).
- Missing or duplicated `config.update` and `llm.tools_snapshot` records are untested; only missing active-tools and duplicated request records are named (`:660-663,687`).
- Missing/unreadable wire or log files, log truncation, missing/duplicated `llm config`, and missing/null output hashes are untested (`:655-672,683-690`).
- `profileName` mismatch is required to fail but has no enumerated test (`:687-688`).
- Hash continuity is prose-only operational logic: the validator emits hashes but accepts no expected round-1 hashes and therefore cannot enforce later-round equality itself (`:645,690,759-763`).

The brief binding is also implemented against `-BriefFile` as it exists after the call, despite the contract requiring a hash captured before dispatch. A file modified between dispatch and validation changes the expected value silently. The validator should receive the immutable pre-dispatch hash, not recompute it from mutable input (`:645,689,763`).

Finally, “exactly one `llm.request`” may reject legitimate tool-using reviews if one prompt produces multiple model requests around tool calls. The probe establishes the record type but not its per-call cardinality (`probe-record.md:177-186`). That needs a real tool-using fixture before exact-one becomes a contract.

Verdict: **FIX — add the missing cases, pass an immutable `-ExpectedBriefHash`, enforce hash continuity in the validator, and probe legitimate per-call record cardinalities before requiring exactly one request.**

3. Both declined fixes are correctly declined

Neither replacement closes the corresponding risk.

Recording hashes makes a schema change observable in a retained record, but it does not make the upgrade fail or require approval. Every new debate still establishes a fresh round-1 baseline automatically (`2026-07-31-kimi-code-swap.md:761,992`). The drift rule permits every version above 0.31.1, and the current drift script has transition handling for Claude, Codex, and Superpowers—but none for a changed Kimi version (`2026-07-31-kimi-code-swap.md:128-149`; `tools/check-drift.ps1:243-284`). Thus an upgrade can advance the snapshot and hashes without a blocking review.

Resume is more serious. `--agent-file`—the load-bearing tool control—cannot be re-pinned (`2026-07-31-kimi-code-swap.md:733-734`; `probe-record.md:226-236`). Re-pinning model or skills does not protect against a future release losing the inherited agent. Because print mode auto-approves tools, post-call evidence detects that loss only after tools may have executed (`probe-record.md:135-149`).

A floor is not a version bound: it prevents older versions, while the inheritance measurement applies specifically to 0.31.1 (`2026-07-31-kimi-code-swap.md:128-147,734`).

Verdict: **FIX — either stop on every unapproved version change or run the sacrificial resume containment probe. Recording hashes and enforcing only a lower bound are not preventive replacements.**

4. No new defect was introduced

New defects exist in every attacked area.

Critical — state-machine stubs:

- Production lookup now requires `$USERPROFILE/.kimi-code/bin/kimi.exe`, but the harness creates only a PATH stub and points `USERPROFILE` at a fake profile containing no such executable (`2026-07-31-kimi-code-swap.md:103-114,155-165`; `evals/tools/drift_statemachine_tests.ps1:110-117,237-276,287-315`). Every Kimi scenario will therefore take the “absent” path.
- The proposed stub advertises `-S`, while the production regex requires literal `--session` (`2026-07-31-kimi-code-swap.md:132-136,159-161`).
- Step 5 replaces the import scenario with a below-floor scenario but never adds a stub mode that emits a below-floor version; the existing stub always emits 9.9.9 except for total failure (`evals/tools/drift_statemachine_tests.ps1:243-246,700-720`; plan `:162-165`).

High — credential home:

- `Remove-KimiLaneHome` is defined inside a script invoked via `pwsh -File`; that function does not survive in the caller that later invokes it (`2026-07-31-kimi-code-swap.md:330-333,421-425,450,507-511`).
- The removal function recursively deletes any caller-supplied path without a builder sentinel or broad-path guard (`:330-333`).
- Failure after credential copying leaves the secret behind because creation is not transactional and has no cleanup handler (`:363-411`).
- The Git check treats any nonzero `git rev-parse` result as “not in a worktree”; `$LASTEXITCODE` is never checked (`:340-354`).
- Disabling inheritance does not explicitly purge or verify every existing explicit ACE, and neither the tests nor the two-host live step inspects the resulting effective ACL (`:259-263,365-378,419-428`).

High — floor parsing:

`$kimiVersion` is populated only after a numeric regex succeeds, so malformed output never reaches `TryParse`; it falls into the “absent or version unparseable” note instead of a failure (`:103-111,138-150`). The advertised fail-closed `TryParse` branch is effectively unreachable for raw malformed version output, while the static test checks only that the identifier exists (`:77-82`).

High — validator:

The validator receives mutable `-BriefFile` rather than the pre-dispatch hash, omits symmetric file-error tests, and may impose an unprobed exact-one request cardinality (`:645,655-690`).

Low — tool inventory:

`len(ALLOWLIST) + len(DENYLIST) == 22` does not make a future built-in visible. Replacing one real name with a nonexistent name—or adding a client tool without editing either constant—leaves the test green (`:579-585`). It pins a count, not the client inventory.

Low — task accounting:

Task 3 says five unknowns and five answers but defines six behavioral probes plus the freshness measurement (`:439-449,452-505`).

Verdict: **FIX — repair the executable stub location and modes, make cleanup callable and safe, fail closed on Git/version-probe errors, verify the ACL, and correct the validator and inventory tests.**

5. Executable without repository context

It still contains direct ordering and interface contradictions:

- Task 3 says to rebuild the one debate home with low effort, but the builder refuses every existing destination; no new path/removal/update of `$h` is specified (`2026-07-31-kimi-code-swap.md:335-338,450,473-481`).
- Task 3 deletes its probe home, but Task 5 later says to copy fixtures from that deleted home (`:507-511,647-651`).
- Task 5 requires a canonical provider before Task 9 creates that declaration. Its interface has no `-Provider` argument, even though rule 6 compares against one (`:645,688`; Task 9 at `:893-906`).
- Task 9 unconditionally says thinking is confirmed per call, although Task 3 may conclude it is only config-asserted (`:483-487,906-909`). The builder comment makes the same unconditional claim before that probe runs (`:303-306`).
- Task 7’s `-Exclude *.git*` filters file names, not traversal beneath the `.git` directory, so the recursive search can still enter repository metadata (`:802-819`).
- Task 10’s end-to-end sequence says “dispatch, capture offsets,” reversing the load-bearing requirement to capture offsets before dispatch (`:741-755,956-958`).
- Cleanup remains unavailable to callers and unsafe even if dot-sourced (`:330-333,507-511`).

Verdict: **FIX — repair the task dependencies and fixture lifetime, move canonical declarations before validator construction, define every probe home explicitly, make cleanup a guarded script interface, and correct the end-to-end sequence.**

UNVERIFIED:

- Actual per-call cardinality of `config.update`, `tools.set_active_tools`, `llm.tools_snapshot`, and `llm.request` during a tool-using review.
- Whether per-session files rotate, compact, or can be replaced while retaining or exceeding their former length.
- Effective ACL contents produced by the proposed builder on PowerShell 5.1 and 7.
- Results of the planned skills, subagent, effort, thinking, resume-flag, encoding, and cumulative-file probes; Task 3 has not yet run.