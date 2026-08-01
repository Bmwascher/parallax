Round 14. The plan was FROZEN on your round-13 PASS, then REOPENED, and this
round exists to re-confirm or reject the changes. Evidence rules and verdict
grammar as before.

WHY IT REOPENED. The user required a whole-branch fable-reviewer read before any
building. It read the plan and spec start to finish rather than task by task,
which is the thing thirteen adversarial rounds structurally could not do - three
consecutive rounds of ours found defects inside text the previous round had just
rewritten. It found no Criticals, and it confirmed the r8 Task 6/7 custody
contradiction is genuinely closed in all three places it appears. It found TWO
IMPORTANTS. I verified both against the plan text before touching anything and
both are real.

IMPORTANT 1, and this one is a two-definitions defect of exactly the class you
fixed for `host` on a free record at round 7. The acquire table keyed on
"identity fields" and NEVER DEFINED THEM. `-DebateHome` is mandatory on every
acquire and is a record field, so it sat in an undecided cell, and Task 6's
Remove uses that very call as its identity check - so the implementer's choice
decided whether Remove detects a wrong `-Path`. Frozen now:

- THE IDENTITY FIELDS ARE EXACTLY FIVE: `host`, `ownerPid`, `ownerStartTicksUtc`,
  `debateId`, `nonce`.
- `debateHome` is RECORDED but is NOT an identity field, and a mismatch under
  otherwise-exact identity is EXIT 2, a caller error. Not contention: converting
  it to contention would be wrong, because it IS the same holder. This is what
  makes Remove reject a wrong `-Path` at the lock rather than downstream at the
  sentinel.
- An idempotent re-acquire WRITES NOTHING and leaves the record byte-identical,
  `acquiredTicksUtc` included, so it can never be mistaken for a fresh
  acquisition.
- The table's two "all identity fields equal" rows are split into a
  `-DebateHome`-equal row and a `-DebateHome`-differs row, and the remaining rows
  now say "the four non-nonce identity fields".

IMPORTANT 2. `-Status` declared `"liveness":"LIVE"|"DEAD"|"UNKNOWN"` while the
liveness rule assigned only two values, because the one unmeasurable case - pid
found, start time unreadable - was defined as ALIVE. So UNKNOWN could never be
emitted by any rule, and Task 8 had no row consuming it. Frozen now: liveness has
THREE outcomes; every MUTATING mode treats unmeasurable as ALIVE and refuses to
reclaim, which is unchanged and is the fail-closed direction; `-Status` reports
UNKNOWN rather than LIVE, because reporting LIVE would claim a measurement that
was not made. Task 8 gains the consuming row - `N/A`, the doctor's own vocabulary
for a surface that did not answer, explicitly not `OK` because an unmade
measurement is never a clean one and explicitly not `STALE` because nothing will
reclaim it - and the foreign-host row now states the comparison it always needed:
the record's `host` against `$env:COMPUTERNAME`, case-insensitively.

SIX MINORS folded in rather than deferred, each removing an invention: Remove-mode
release-after-deletion precedence, with `removed <path>` printed only when both
the deletion and the release succeeded; Task 5 naming
`tools/read-kimi-credential-state.ps1` explicitly as Task 6 already did; C created
by the same six setup steps, third, writing no marker because only A and B are
ordered against each other; the three-coexisting-logins assumption recorded as a
GENERALIZATION of measurement 11, which established two, with its fail direction
stated as loud refusal; the absolute-key fixture built normally and then
hand-edited in the throwaway copy, since the builder renders only the relative
form; and the debate-home versus lane-home terminology collision fixed inside the
shipped `lane-home-isolation` region text.

QUESTIONS:

1. PASS, if these changes are correct and complete; or the precise FIXes.
2. Did any of them introduce a defect, or contradict text you passed at round 13?
   The acquire table and the liveness rules are both text you had already passed,
   and I have now changed both.
3. Do you agree with the two judgment calls I made rather than took? First, that a
   `-DebateHome` mismatch is exit 2 rather than contention. Second, that a held
   lock with UNKNOWN liveness is `N/A` rather than `STALE` or `BROKEN`.
