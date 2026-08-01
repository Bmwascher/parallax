# Fable-reviewer whole-artifact review 2, 2026-08-01

Seat: `agents/fable-reviewer.md`, dispatched as a fresh subagent.
Subject: the plan FROZEN at revision 17 (commit `1892dfa`) and its design
spec at revision 2. No code exists, so no diff and no SDD ledger.

Dispatched because the FIRST whole-artifact read
([fable-whole-plan-review.md](fable-whole-plan-review.md)) read revision 12,
and five adversarial rounds had rewritten substantial text since: the
`debateHome` comparison and its normalization, the UNMEASURABLE liveness
routing, foreign-host status, two new Task 6 oracles, Task 7's home-C
sequence, two Task 8 pins, a root-aware path normalizer, an exit-code-3
alignment, a named Remove fault seam, and the implementer packet section.
Those rounds read the plan task by task. Nothing had read the frozen text
start to finish.

Verdict: **Ready to merge — with fixes.** No Critical. One Important. Five
Minor.

**Provenance limit, same as the first artifact.** A subagent returns its
report to the dispatching session and writes no transcript of its own, so
this file is the session's reproduction of that report and there is no
independent source to check it against. What can be checked is every claim
it makes.

---

### Strengths

- Every line citation I could resolve against the repo is accurate at HEAD. The CI break is real and stated exactly: `C:\Users\Brandon\Documents\parallax\.github\workflows\skill-evals.yml:84` and `:95` both pass `evals/multi-model-verify/test_kimi_lane_lock.py`, which does not exist. Task 1's frozen four-module set matches the workflow's surviving modules byte for byte (`:85-88`, `:96-99`).
- The builder citations all hold: credential source `tools/new-kimi-lane-home.ps1:233`, the copy `:414`, the seam `:422-423` (name `PARALLAX_LANE_HOME_FAULT` matches its pin at `evals/multi-model-verify/test_kimi_lane_home.py:106`), the drive-root case `:89-99`, `removed <path>` at `:132`, failed-build cleanup `:482-489`, `key = "oauth/kimi-code"` at `:456`, ACL `:399-408`. Fixture `test_kimi_lane_home.py:316-317` and one-host selector `:21` are exactly as described; the selector pattern to copy is at `test_codex_context_probe.py:54-67` inside the cited `:35-67`.
- Both r12 Importants are genuinely closed, and closed consistently. The five identity fields are named once (plan `:207`) and every consumer agrees: the acquire table rows (`:217-226`), the `-DebateHome` two-stage rule with exit 2 (`:209`), and Task 6's wrong-`-Path` integration oracle (`:393`), which correctly requires exit 2 now that `debateHome` is out of identity. UNKNOWN liveness has an emission rule (`:261-263`), an acquire-side routing rule (`:228`), a doctor row that consumes it (`:553`), and explicit pins that a wrong mapping fails (`:585`).
- Exit code 3 now means the same thing in all three texts: the lock table (`:191`), the UNMEASURABLE paragraph (`:228`), and Task 5's wrapper (`:339`). All three name the same three sources: the handle, a LIVE holder, an UNMEASURABLE holder.
- The `debateHome` normalizer (`:211`) is coherent, including edge spellings I traced by hand (drive root, UNC root, trailing separator), and its root guard matches the builder's own root-is-special handling at `tools/new-kimi-lane-home.ps1:89-99`.
- The lifecycle is one story in all three places: Task 6 build order and Remove order (`:373`, `:383`), Task 7's routing, custody flag, cleanup matrix and its explicit never-reaches-the-remove-seam statement (`:446-461`, `:506-514`, `:393`), and the Task 9 `lane-lock-call-lifecycle` text (`:607`) all agree that the builder is the acquisition, a successful build retains, Remove verifies identity before deleting and releases after.
- The implementer packet (`:75-83`) is sound. I walked every task against the seven blocks: every constant a task consumes is in Fixed names and values, in Global Constraints, in Measured facts, or stated inline in the task itself (Task 5 lists the validator's status vocabulary it depends on; Task 8 embeds both recovery commands; Task 10 embeds the baseline SHA). Cross-task references that remain are informational, not load-bearing.
- Task 10's mechanics verify: `.claude-plugin\plugin.json` is `0.18.0` so `0.19.0` is the right bump, and the history-check baseline `6201e30` matches `origin/main` (`.git\refs\remotes\origin\main` reads `6201e301be...`).
- Old-text removal targets are real: `credential present and OAuth-sourced` is live at `commands/doctor.md:166`; `N/A` is defined as a non-failing row verdict at `:6-9`; the containment check to keep is at `:169-173`; the region to replace is `backup-lane.md:48-67` with its whole-region pin at `test_backup_lane.py:162-194`; the normalized-substring equality Task 9 mandates matches how the checker works (`test_contract_coverage.py:21-30`, `:517-526`).

### Issues

#### Critical

None found.

#### Important

1. **Two spec-mandated visibility behaviours have no rule and no oracle anywhere in the frozen plan, and the packet excludes the spec, so they will not be built.** The design spec requires "Reclaim is visible. Taking over a lock whose owner is genuinely dead reports what it reclaimed and from whom" (`docs/superpowers/specs/2026-08-01-lane-credential-and-lock-design.md:297-298`) and that exhausting the wait budget "is a refusal naming the holder" (`:276-278`). Task 3's DEAD-reclaim row says only "acquire or reclaim, generate a NEW nonce, print it" (plan `:219`); exit 3 has no message contract anywhere (`:191`, `:228`), and Task 5's exit-3 test requires only the code and a non-invoked stub (`:345`). `-ForceRelease` alone kept its "report what it displaced" (`:246`). This matters twice over: the implementer receives the packet, not the spec, so a converged design behaviour silently vanishes from the shipped tool; and the reclaim report's channel needs freezing anyway, because acquire's stdout is the nonce that Task 6 captures and parses, so an invented stdout report would contaminate custody while an invented stderr one would be swallowed by the builder's capture (`:369`). Settle by appended round: freeze both messages (content and stream) in Task 3 with oracles, or amend the spec to narrow both claims on the record.

#### Minor

2. **The doctor's `held and UNKNOWN` row overlaps the foreign-host row on every foreign-host record.** Task 3 makes foreign-host status liveness `UNKNOWN` always (plan `:263`), so a foreign-host record matches both `:553` and `:554`. Worst-of aggregation makes the verdict deterministic (STALE), but the UNKNOWN row's mandated detail, that mutating modes treat the holder as alive, describes the same-host mechanism, not the foreign-host exit-4 path. One word, "same-host", in the UNKNOWN row closes it.
3. **`PARALLAX_LANE_HOME_CLEANUP_RELEASE_FAULT`'s mechanism and end state are not frozen** (plan `:393`). The Remove seam freezes skip-the-mutation, code 5, and an exact stderr sentinel; the cleanup seam freezes only its name, firing point, and precedence outcome. Whether it skips the release (record left held) or fails after releasing (record free) changes the end state its test should assert, which is the same invention class r15 closed for the Remove seam.
4. **The wrong-`-Path` oracle's home B has no stated construction** (plan `:393`). "Prepare a distinct valid disposable home B": building it with the builder against the same lane home would contend with A's retained hold, so B must be hand-made or built against a second lane home. Left to invention; harmless to the assertion, since the exit-2 refusal fires at step 1 either way.
5. **The shipped `lane-lock` region's malformed enumeration reads exhaustive but omits one class Task 3 includes.** "...one carrying a field this reader does not know... are each held" (plan `:603`) does not reach a free record carrying a held-only KNOWN property, which Task 3 twice insists is exactly the case an unknown-field wording misses (`:166`, `:267`). Prose summary versus frozen rule; no mechanical conflict, but it is the r7 two-wordings shape in shipped text.
6. **Region id `lane-lock` reuses a deleted region's identifier.** The `DECLARED_REGIONS` comment (`test_contract_coverage.py:625-632`) still narrates deleting an old `lane-lock` region as subjectless; after Task 9 the comment reads as if the new region were that one. Cosmetic; the checker itself is indifferent.

Named gaps, checks I could not make with the tools granted: the `775472c^` blob citations (`:154`, `:185`, resolved point 26), the three known trailer carriers `c79da41`/`9d50196`/`e3f98c2` (`:644`), and the never-pushed / no-Actions-runs claims (`:91`) all require git or gh commands. The artifact records the session closing the first and third with tools I lack, and I verified the adjacent claim I could reach: `origin/main` is `6201e301...`. Of the six debate rounds since r12 I audited the plan's own revision history and the current text; I did not re-read the raw round replies.

### Ledger minors triage

No SDD ledger exists; nothing has been built. Nothing to triage.

### Assessment

Ready to merge: With fixes. As a whole artifact the plan is internally consistent, its premises are true against the repo, and the six post-r12 rounds' changes are coherently integrated; but one converged spec behaviour (reclaim and contention-refusal visibility) fell out of the plan entirely and, under this plan's own packet rules, would fall out of the shipped tool, so it needs one appended round before implementation begins. The five Minors can ride into that round or into implementation.

---

## Session adjudication

The Important was verified against both documents before anything changed,
and accepted. All five Minors were accepted rather than deferred.

The finding is a class neither debate participant could reach: all
eighteen rounds compared the plan against ITSELF, while this compared the
plan against the SPEC. What made it more than an omission is that
`-ForceRelease` had KEPT its visibility requirement, so the plan carried
the rule for one of three modes and dropped it for two.

**Round 19 then found that the fix was not enough**, and its finding
belongs beside this one. The r18 amendment restored the behaviour in the
DIRECT TOOL and left every CALLER free to swallow it: the builder captured
all internal lock output, and the login wrapper's contention test asserted
only an exit code. Sol named the class as **composition across caller
boundaries** and a related one as **fixture constructibility** — this
review's own Minor 4 was the concrete survivor, because the hand-built
home B could not be constructed without contending with home A's retained
hold, so that oracle could never have reached its assertion. Both are
recorded in the plan's r19 revision entry.
