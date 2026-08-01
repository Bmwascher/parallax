# Fable-reviewer whole-artifact review, 2026-08-01

Seat: `agents/fable-reviewer.md`, dispatched as a fresh subagent.
Subject: the frozen plan at revision 12 and its design spec at revision 2,
BEFORE any code was written. No diff and no SDD ledger existed, which is
the point: this is a pre-build whole-artifact read, not a mode-diff review.

Dispatched because all thirteen Sol rounds read the plan TASK BY TASK, and
three consecutive rounds found defects inside text the previous round had
just rewritten. Nothing had read it start to finish. In the previous cycle
that whole-artifact read found four material defects seven adversarial
rounds had missed.

Verdict: **Ready to merge — with fixes.** No Critical. Two Important. Six
Minor. The reply below is the report the subagent returned, reproduced
without edit.

**Provenance limit, stated plainly.** A subagent returns its report to the
dispatching session and writes no transcript of its own, so this file is
the session's reproduction of that report and there is no independent
source to check it against. Nothing here can prove it was not altered in
transcription. What CAN be checked is every claim it makes: the line
citations below resolve against the repo, and the two Importants were each
verified against the plan text before any change was made.

---

Whole-artifact review complete. The plan is coherent end to end, every premise I could check against the repo is true, and the r8 Task 6/7 custody contradiction is genuinely resolved. I found no Critical defects, two Important underspecifications the 13 rounds never froze, and a set of Minors.

### Strengths

- Every load-bearing premise checks out against the repo. The CI break is real: `.github/workflows/skill-evals.yml:84` and `:95` both name `evals/multi-model-verify/test_kimi_lane_lock.py`, and that file does not exist (glob confirms; `tools/kimi-lane-lock.ps1` is also absent, so Task 3 writes fresh as claimed). The copy the fix removes is at `tools/new-kimi-lane-home.ps1:414`; the fault seam at `:422-423`; the fixture the plan says to widen is exactly `test_kimi_lane_home.py:316-317` (credential with only `access_token`); the one-host selector is exactly `test_kimi_lane_home.py:21`. Every other line citation I resolved — builder `:131-133`, `:231-236`, `:482-489`, doctor `:157-168`, `:169-173`, `:6-9`, `test_backup_lane.py:162-194`, `test_contract_coverage.py:21-30`, `:517-526` — is accurate.
- The Task 6/7 custody contradiction the dispatch flagged is closed consistently in all three places it appears: Task 6 makes a successful build retain the lock (plan `:361`), Task 7 makes the builder the acquisition with `custodyReceived` gating (plan `:408-419`), and the shipped lifecycle region says the same (plan `:568`). The seed step is the declared sole direct-acquire exception (`:443`), and item 6 is the declared exception to that (`:444`). No task acquires against a hold another task retains.
- Surface ownership is complete. The only shipped texts carrying the old copied-credential claim are `skills/multi-model-verify/references/backup-lane.md:63-66` (Task 9 replaces the region, pin first) and `commands/doctor.md:157-168` (Task 8). `model-prompting-notes.md:315-316` mentions the builder only for effort/thinking and needs no change. `test_backup_lane.py` currently pins nothing from doctor.md, so Task 8's tests-first ordering has no hidden conflict. Files touched by two tasks (workflow: Tasks 1 and 10; `test_kimi_lane_home.py`: Tasks 2 and 6; `test_backup_lane.py`: Tasks 1, 8, 9) all state the split explicitly.
- The order is buildable: Task 2 (validator, selector refactor) precedes Task 5/6 which consume it; Task 3 precedes every lock caller; CI wiring waits for Task 10 while the ubuntu `pytest evals -q` job stays green in between because every new module carries the `os.name != "nt"` guard (plan `:43`).
- Verification steps can fail: Task 1 mutation-tests both checker directions (`:97`); Task 4 inverts the measurement-20 assertion and requires a failure (`:282`); Task 9 deletes a sentence and requires UNLOCKED (`:579`); Task 10's history check is converted into a throwing oracle (`:599-604`). The Task 9 normalized-comparison instruction matches how the checker actually works (`test_contract_coverage.py:21-30`, `:517-526` — whitespace-collapsed substring, never raw bytes).
- Both spec amendments the round-3 spec reply conditioned PASS on (`rounds/2026-08-01-cred-lock/reply-r3.md:7-41`) are incorporated: the hash-confirmed `-MalformedOverride` (plan `:164`, `:222-229`) and per-field `expires_at` validation with `0` valid (plan `:122`).
- Contract region texts use forward slashes only, honoring the backslash sweep on `references/` (Global Constraints `:39`), and keep the canonical model id as a placeholder (`:35`).

### Issues

#### Critical

None found.

#### Important

1. **`debateHome`'s role in the acquire identity comparison is an unfrozen cell in an otherwise frozen table** — plan `:194-201` vs design spec `:262-267`. The acquire rows key on "identity fields", which the plan never defines; the spec defines the exact-match set as hostname, pid, start ticks, debate id, nonce — excluding `debateHome`, yet `-DebateHome` is mandatory on every acquire (`:156-157`) and is a record field (`:146`). Two defensible readings diverge: an idempotent re-acquire supplying a *different* `-DebateHome` under an otherwise exact identity is either idempotent success (spec reading) or contention (broad reading), and nothing says whether an idempotent success rewrites the record (`debateHome`, `acquiredTicksUtc`). Task 6's Remove leans on this exact call as its identity check (`:353`), so the implementer's choice decides whether Remove detects a wrong `-Path`. This is the same two-definitions class r7 fixed for `host` on a free record (`:20`), and the plan's own bar is a zero-judgment implementer.
2. **Status liveness `UNKNOWN` has no emission rule, and Task 8 has no row that consumes it** — plan `:243` declares `"liveness":"LIVE"|"DEAD"|"UNKNOWN"`, but Task 3 assigns only LIVE and DEAD (`:233`: an unreadable start time "is ALIVE"), so when UNKNOWN prints is invented by the implementer. Task 8's substate table (`:514-519`) keys rows on LIVE, DEAD, foreign-host, MALFORMED, and unmeasurable; a same-host held record reported UNKNOWN falls between rows, and the foreign-host row itself requires a host comparison against `$env:COMPUTERNAME` that check 8's procedure never states. The doctor's aggregate was made a total order over verdicts (`:502`) but its substate partition is not total over `-Status`'s declared outputs.

#### Minor

3. **Remove-mode release failure after deletion is specified in prose but has no exit, report, or oracle.** Build mode has a frozen precedence rule (`:349`); Remove's order ("3. Delete. 4. Release.", `:353`) has none, and Task 7's matrix (`:472-476`) covers only the deterministic sentinel refusal, while its preamble acknowledges the release-after-deletion failure state (`:470`). Whether "removed <path>" has already printed and what code returns is invented.
4. **The live suite depends on three coexisting lane logins (A, B, C) plus the user's own; measurement 11 licenses two** (spec `:57`). Fail direction is safe — the suite refuses loudly, never silently green — but the setup rests on an unmeasured generalization.
5. **C's login setup is owned by no frozen sequence.** The manual setup (`:382-391`) is written "For A, then for B"; C also requires a structurally ok credential (`:378`) but its creation and its lack of a marker are left to inference.
6. **Item 1's absolute-`oauth.key` fixture construction is uninvented.** The builder renders only the fixed `key = "oauth/kimi-code"` (`tools/new-kimi-lane-home.ps1:456`), so producing the absolute-key home means hand-editing a throwaway config — workable, but unstated (`:454`).
7. **Terminology collision inside the shipped contract:** the replacement `lane-home-isolation` region opens "Build the lane home ONCE" meaning the *debate* home (`:560`), while `<lane-home>` in the lifecycle region (`:568`) is the persistent credential home. Both texts are exact and the commands disambiguate, but the shipped file will use "lane home" for two different directories.
8. **Task 5 never names the validator tool** behind "read the existing credential verdict" (`:305`); Task 6 names `tools/read-kimi-credential-state.ps1` explicitly (`:343`), Task 5 leaves it inferred.

Named gaps in this review (checks I could not make with the tools granted): the deleted predecessor at `775472c^:tools/kimi-lane-lock.ps1` requires `git show`, so the plan's citations into that blob (`:139`, `:170`, resolved point 26) are unverified here; likewise the never-pushed / no-Actions-runs claims in Task 1 (`:76`). Of the 16 debate rounds I verified the decisive ones in full (plan r12, r13, spec r3) against the plan's revision history; the earlier rounds were checked through that audited history, not re-read line by line.

### Ledger minors triage

No SDD ledger exists — nothing has been built. Nothing to triage.

### Assessment

Ready to merge: With fixes — as a plan, ready to implement after the two Important items are settled by an appended round (the plan's own freeze rule at `:5` requires that form): freeze `debateHome`'s comparison and rewrite semantics in the acquire table, and freeze `UNKNOWN`'s emission rule plus its doctor row. The Minors can ride into implementation, where the fail directions are loud.

---

## Session adjudication

Both Importants VERIFIED against the plan text before anything was changed,
and both accepted. All six Minors were accepted too rather than deferred,
because each removed an invention and all were cheap.

The two judgment calls the session made rather than took — a `-DebateHome`
mismatch as exit 2 rather than contention, and a held lock with UNKNOWN
liveness as `N/A` rather than `STALE` or `BROKEN` — were both put to the
cross-vendor reviewer at plan round 14 and both agreed with, with reasons
recorded in `plan-reply-r14.md`.

Two gaps this review named in itself were closed by the session, which had
the tools it lacked: the `775472c^` predecessor citations were confirmed by
`git show`, and the never-pushed claim was established by three checks.

Those three were re-run on 2026-08-01 so the record carries current
results rather than remembered ones:

- `git branch -r --contains HEAD` — empty.
- `git ls-remote --heads origin` — one line only,
  `6201e301becb0b4af92e7b83cebac37fc84ac1f6 refs/heads/main`.
- `gh run list -b feat/kimi-code-backup-lane` — empty. A bare `gh run list`
  is NOT empty: it returns runs, all of them on `main`. The branch filter
  is what makes this evidence, and the earlier unfiltered phrasing was
  wider than what was measured.
