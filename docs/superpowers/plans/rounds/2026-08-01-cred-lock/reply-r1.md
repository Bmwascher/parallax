## Numbered claims

1. The repository proves the fork prerequisite: the builder selects the user credential at `tools/new-kimi-lane-home.ps1:231-236` and copies it into each debate home at `tools/new-kimi-lane-home.ps1:410-414`. Measurements 1–4 are only recorded in `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:39-44`; the offline builder tests use a fake token and never exercise refresh behavior (`evals/multi-model-verify/test_kimi_lane_home.py:310-339`). The logical “fork, not race” diagnosis follows if those measurements hold, but the repository cannot verify them.

**ESCALATE — a reproducible single-debate refresh probe is required to verify measurements 1–4.**

2. The rendered configuration does use the relative key `oauth/kimi-code` at `tools/new-kimi-lane-home.ps1:449-456`, and the TOML test pins that relative value at `evals/multi-model-verify/test_kimi_lane_home.py:231-240`. Nothing in the repository tests an absolute key; measurement 5 exists only in the design table at `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:45`.

**ESCALATE — add or retain a live absolute-path rejection probe; repository evidence does not close configuration redirect.**

3. The proposed structure creates a junction rather than a copy, and the design correctly states that this would leave one lane credential file if reads and refresh writes traverse it (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:109-121`). Measurements 6–7 are not reproduced by repository tests; the current builder tests still construct and assert copied credentials (`evals/multi-model-verify/test_kimi_lane_home.py:310-317`).

**ESCALATE — junction read-through and refresh write-through require the live measurements or equivalent integration tests.**

4. Current removal is exactly the recursive operation claimed (`tools/new-kimi-lane-home.ps1:127-133`), and failed-build cleanup also recursively removes an ancestor that could contain the junction (`tools/new-kimi-lane-home.ps1:482-489`). The current removal tests pin guards but do not create and delete a junction (`evals/multi-model-verify/test_kimi_lane_home.py:64-90`). The historical cross-host defect is real: the deleted lock documented that PowerShell 7 converted JSON time values differently while the Windows PowerShell suite stayed green (historical `tools/kimi-lane-lock.ps1` at `775472c^`:110-118). Measurement 10 itself remains external.

**ESCALATE — retain live deletion-through-junction tests on both PowerShell 5.1 and 7.**

5. The design genuinely limits intended ownership to a separate lane credential and explicitly forbids fallback to the user credential (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:93-107`). That bounds damage to backup-lane availability, although it does not make loss cost-free: a lane failure still stops or gates an active debate (`skills/multi-model-verify/references/fallbacks.md:139-168`). Coexistence itself is measurement 11 only (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:51`).

**ESCALATE — measurement 11 needs verification; if retained, word the blast radius as “the user’s ordinary login remains intact,” not “costs nothing.”**

6. The invoking shell is unsuitable if it exits after every call, and the spec records the stable harness observation at `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:150-157`. But the harness is too broad as the only liveness identity: the design handles “owner process died” but not “debate was abandoned while the harness session remains alive” (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:243-245`). Such a lock is permanently live until session exit or a successful explicit release.

**FIX — give each debate a dedicated long-lived owner process, or specify an authenticated abandon/recovery operation for a dead debate whose harness remains alive.**

7. The old lock explicitly used age alone, became breakable after 45 minutes, and admitted that a live long round could be broken (historical `tools/kimi-lane-lock.ps1` at `775472c^`:10-23,63-73). The replacement design removes clock-based staleness and defines PID plus start-time liveness, including PID reuse (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:132-163`). That is the correct conceptual rule.

**PASS.**

8. The design expressly treats foreign-host, unreadable, truncated, and malformed locks as held and reported (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:165-171`). That matches the existing fail-closed deletion guard, which refuses when `USERPROFILE` cannot be evaluated (`tools/new-kimi-lane-home.ps1:103-125`).

**PASS.**

9. The spec accurately limits measurements 12–13 to one observation and disclaims a universal credential-race result (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:52-60,193-210`). But one stated justification is not delivered: it says the lock protects against “a login racing a debate,” while login remains an external, user-run `kimi login` with no requirement to acquire the lock (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:95-103,198-203`).

**FIX — provide a lane-login wrapper that acquires the same lock, and make doctor point to it; otherwise delete the login-race protection claim.**

10. The primary lane clears `CODEX_HOME` and the other auth-routing variables before both preflight and dispatch (`skills/multi-model-verify/references/model-prompting-notes.md:169-180`). Its concurrency contract uses distinct session and output paths, while acknowledging that auth, config, storage, and quota remain shared (`skills/multi-model-verify/references/model-prompting-notes.md:200-229`). The design scopes the new lock exclusively to Kimi (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:188-191`). Immunity is therefore limited correctly to this copied-credential fork.

**PASS.**

11. The current `lane-home-isolation` region explicitly says copied credential, user credential availability, and copied-credential removal (`skills/multi-model-verify/references/backup-lane.md:48-67`). Its whole-region pin carries the same text (`evals/multi-model-verify/test_backup_lane.py:162-194`). Tests-first and whole-region pinning are required by `CLAUDE.md:41-56`, while region additions/removals must update `DECLARED_REGIONS` (`CLAUDE.md:89-92`; `evals/multi-model-verify/test_contract_coverage.py:624-677`). The proposed new lock region therefore also requires a new declaration and whole-region pin.

**PASS.**

## Open questions

Q1. Use the fixed `~/.parallax-kimi-review` path for this change. It is the only measured location; the alternative is explicitly untried (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:232-236`). Do not place credentials inside the versioned plugin cache, which is replaced during plugin updates (`CLAUDE.md:32-39`). A stable `%LOCALAPPDATA%\parallax\...` location can be reconsidered after the same login, junction, ACL, and update-lifecycle probes.

Q2. Acquire in the builder. The shipped contract already makes the builder mandatory before round 1 (`skills/multi-model-verify/references/backup-lane.md:47-67`), while the write-probe occurs afterward (`skills/multi-model-verify/references/backup-lane.md:210-216`). Build should acquire before touching the shared credential; `-Remove` should release only after debate-home cleanup. Keep the lock logic internally separable and directly tested.

Q3. WAIT with a caller-supplied bounded budget. This is already the stated user behavior, and exhaustion must refuse without breaking the holder (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:173-177`). The wait deadline limits caller patience; it must never become a staleness deadline.

Q4. The next acquire should report and reclaim the dead owner, and `/parallax:doctor` should report a stale or held lock on demand. The spec already requires visible reclaim (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:183-186`) and doctor is report-only (`commands/doctor.md:5-9`). No background service is justified merely to report a dead lock when nobody is waiting.

Q5. Yes, doctor should check the lane login before debate construction, but it must not continue treating `provider list` as authentication. The current doctor calls `source=oauth` sufficient while admitting dispatch can still return `auth.login_required` (`commands/doctor.md:146-168`); measurement 16 says even garbage or absent credentials produce that source (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:55-56`). Default doctor should verify path, readability, valid JSON, and required nonblank fields without printing secrets, then provide the locked login-wrapper command. A true live-auth verdict requires an explicitly labeled authenticated probe.

## Unhandled failure modes

- Release identity is not debate-specific. The file records `debate id`, but release compares only owner PID/start time (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:144-148,179-181`). A delayed duplicate release from one debate can delete a later debate’s lock when both run under the same harness. Require hostname, PID, start time, debate id, and a random acquisition nonce.

- Stale reclaim is not specified atomically. `CreateNew` closes fresh acquisition, but the design does not define an atomic compare-and-remove for an existing dead lock (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:144-148,183-186`). Two reclaimers can inspect the same stale file and one can remove the other’s newly created lock. Use an OS-level meta-lock or an exclusive-handle/generation-checked reclaim protocol.

- A present but malformed or blank lane credential is not classified UNAVAILABLE. The design names only missing or unreadable credentials (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:95-107`), matching the current builder’s existence-only check (`tools/new-kimi-lane-home.ps1:231-236`). Validate JSON shape and required nonblank token fields before building.

- Owner start-time encoding is underspecified. The design records and compares a start time without fixing representation or precision (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:144-163`), despite the historical PowerShell 5.1/7 JSON time-type divergence (historical `tools/kimi-lane-lock.ps1` at `775472c^`:110-132). Specify UTC ticks or another byte-stable representation and gate both hosts.

- Conditional on measurement 9, the persistent credential target lacks the builder’s ACL protection. The builder hardens only the throwaway home (`tools/new-kimi-lane-home.ps1:393-408`), while the junction target lives elsewhere (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:95-117`). The lane home and credential need their own restrictive ACL validation.

OVERALL VERDICT: FIX — irrespective of the external measurements, the design is not implementation-ready until login participates in the lock, release ownership is debate/generation-specific, stale reclaim is atomic, and live-harness/abandoned-debate recovery is defined.

## Final check

UNVERIFIED:

- Claim 1: measurements 1–4.
- Claim 2: measurement 5.
- Claim 3: measurements 6–7.
- Claim 4: measurement 10.
- Claim 5: measurement 11.
- Claim 6: measurement 14.
- Claim 9: measurements 12–13.
- Conditional ACL finding: measurement 9.
- Doctor authentication limitation: measurement 16.
- Measurements 8 and 15 were recorded but not needed for a numbered verdict.

All measurements 1–16 appear only as recorded results in `docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:33-60`; the current backup contract suite describes itself as offline with zero CLI calls (`evals/multi-model-verify/test_backup_lane.py:1-7`). I attempted the targeted pytest gates required by `CLAUDE.md:11-16`, but no `python`, `python3`, or `py` executable is available in this environment, so no test result was folded into the verdict.