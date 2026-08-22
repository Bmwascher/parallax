# Debate brief - round 5 - mode plan - Fable lane

## Continuity check, answer FIRST

Neither answer is in this message.

1. Your continuity nonce, verbatim.
2. In round 4 you reported one relayed item that you could NOT verify with read-only tools and flagged as UNVERIFIED. Name what it was and why you could not settle it.

If you cannot answer both from memory of your own earlier rounds, say so plainly rather than reconstructing.

## Subject revision

Plan file at commit `ff34793`, branch `item51-inline-brief-transport`. Re-read it.

Budget: three rounds were authorized after round 3. This is the second of them. If both lanes have not returned PASS by round 6, the debate pauses and returns to the user.

## Disposition of round 4

CONVERGENT, and the round's most serious finding:

1. **The exemption could not fire for the two tasks it was written for.** `survey.py` reads `git ls-files`, which lists TRACKED files only, and Tasks 4 and 7 ran their `--emit` check BEFORE staging the files they had just created. An invisible file and a fully classified one produce identical empty output. Both tasks now `git add` first and assert `git ls-files <dir> | wc -l` is nonzero before trusting the emit. That was the THIRD fail-open gate in this plan, each written while closing the previous one, and the pattern is now recorded in the plan text itself.

Accepted from one lane, verified:

2. The exemption reached too far: it covered `feasibility-record.md`, which is genuinely a record, never executed, and which GROWS through Tasks 4 to 8, so rows keyed to its line numbers would go stale on the record's own prose and block Task 9 for a reason that is not an entry point. `NOT_EXEMPT` now excludes it and `entry-points.tsv`. **This also resolves your A3**: those lines are prefix-covered as `record`, which is what they are, so the standing rule's "matching LINE" half no longer needs a step nobody wrote.
3. Two more filter shapes, both live: a generic call operator with a literal command (`& git -C ...`, `tools/new-kimi-lane-home.ps1:691`) and bare `python` (`tools/check-drift.ps1:983` — your instance).
4. Bare `git` stays a DECLARED miss: 179 further hits, starts no PowerShell host. The trade and its live instance `tools/check-drift.ps1:987` are written into `survey.py`'s comment and the blind-spot list, exactly as you proposed, rather than left as an implied empty set.
5. Your A2 was right and the count is now enumerated: EIGHT corrections across four rounds.
6. `probe.py` continued past a failed PATH strip and could still exit 0. Now returns 1 before invoking anything.
7. The timeout write-up blamed a blocked stdin read that `stdin=DEVNULL` rules out. Reworded.
8. Task 6's "the only evidence that anything PASSED under PowerShell 7" narrowed to the shipped test modules, since Task 4 runs four `pwsh7` arms.
9. "A line matching both families produces TWO rows" now reads one row per family matched, up to three.
10. Untracked files are invisible to `git ls-files`. Your lower-confidence lead about the auto-triage wrapper scripts turned out not to apply — I checked, `tools/drift-reports/` is untracked — so they are now named in the blind-spot list as the live example of that limit.

**Your A1 was REFUTED, not applied.** You reported the Task 2 Interfaces block still specifying the old survey line without `files not scanned`. It does not: that block already lists the `FAMILY` lines and the full final line, and the correction had been applied at both sites. Say so if you disagree, with the line.

## Run, not read

6346 matches, 981 hand rows — 168 host, 277 launch, 536 bare. All 18 entry points either lane has named are caught. The declared miss is still missing. Five exemption cases pass including three negative ones. Duplicate refusal holds; a legitimate three-family row set for one line is accepted.

## What I want from this round

A. Sweep round 4's amendments. Fourth time asking; three of four rounds found their worst defect inside the previous round's fixes. Name each instance with a line reference, or report explicitly that you found none.

B. `NOT_EXEMPT` and the staging fix specifically. Between them they changed which matches get hand rows and when a check can see a file. Can either fail open? Can either fail closed and block the plan?

C. The filter, an eighth time. Produce a live instance with a file:line, or report none found and say which shapes you looked for. Bare `git` is a declared miss and does not count.

D. Anything else.

End with exactly one verdict line: PASS, FIX, or ESCALATE. **If the plan is sound, PASS is correct and one line is the right length.** Four preceding rounds is not a reason to withhold it. Do not manufacture objections; do not concede a point you can refute.