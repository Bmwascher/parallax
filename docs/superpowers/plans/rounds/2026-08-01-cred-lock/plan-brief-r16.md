Round 16. All three of your round-15 blocking fixes are applied. The plan header
now reads revision 15. I contest nothing. Same evidence rules and verdict
grammar.

I verified each of the three against the repo before applying it, because two of
them were consequences of my own r14 text and I wanted to be sure I was not
taking a correction I had not confirmed. All three were real.

## Task 3 — root-aware `debateHome` normalization

At `docs/superpowers/plans/2026-08-01-lane-credential-and-lock.md:199`.

The algorithm is now `GetFullPath()`, then `GetPathRoot()` of that result,
then a single trailing separator trimmed **only when the normalized string does
NOT equal its own root under ordinal case-insensitive comparison**, then the
ordinal case-insensitive comparison of the results.

The reason is on the record rather than left implicit, because the guard looks
removable: an unconditional trim takes `C:\` to `C:`, which is drive-RELATIVE
and resolves against that drive's current directory, so it is not the same path
at all, and Task 3 does not forbid a root-valued `-DebateHome`. The text cites
`tools/new-kimi-lane-home.ps1:89-99`, which is where the builder already treats
a drive root as its own case, so the plan and the existing tool now agree on
that hazard instead of only one of them knowing about it.

Tests, under BOTH hosts as you required: two equivalent spellings of one
NON-root path compare equal; two equivalent spellings of a drive ROOT compare
equal and normalize to the same absolute root rather than to a trimmed one; a
genuinely different path compares unequal.

## Task 5 — code 3 includes UNMEASURABLE

At `:327`. It now reads "the exclusive handle OR a holder that is LIVE or
UNMEASURABLE, since a preserved lock code 3 covers all three." The sentence
also states that this matches Task 3's wording exactly and that two definitions
of the same propagated code was the defect, and it carries your reason for why
one test per exit code stays sufficient: the wrapper receives the identical
lock-tool code 3 whichever holder produced it.

This is the third instance of the same class in this debate — `host` on a free
record at r7, the lock tool's own code 3 at r14, the wrapper's at r15 — so I
have written the reason into the text each time rather than just the value.

## Task 6 — the Remove release-fault seam is named

At `:381`. `PARALLAX_LANE_HOME_REMOVE_RELEASE_FAULT`, with every property you
froze: honored ONLY in Remove mode, firing immediately after a successful
deletion and immediately before the release; when nonempty it SKIPS the lock
mutation entirely and produces a simulated release result of code 5; it writes
exactly `PARALLAX_LANE_HOME_REMOVE_RELEASE_FAULT injected: simulated post-delete
release refusal` to stderr and nothing to stdout. The test requirements are
unchanged: home ABSENT, original held record UNCHANGED, exit 5, that sentinel on
stderr, no `removed <path>` on stdout, direct release as teardown.

The text also states why it needed a name at all — the other two seams carry
exact shared strings because production and tests must agree on them — so the
next editor does not read the name as arbitrary.

## Your two new UNVERIFIED items

I closed one partly and one fully, and I want you to check that I did not
overclaim on either.

**The fable artifact's verbatim claim.** You are right and I have written the
limit into the artifact rather than arguing it. A subagent returns its report to
the dispatching session and writes no transcript of its own, so that file is
this session's REPRODUCTION of a returned report, and nothing in it can prove it
was not altered in transcription. The artifact now says exactly that, at its
head, and says what CAN be checked instead: every line citation in it resolves
against the repo, and both Importants were verified against the plan text before
anything was changed. The word "verbatim" is gone.

I do not think this one can be closed. If you see a way to close it that I have
missed, say so.

**The remote and Actions claims.** Re-run just now rather than remembered, and
the re-run CORRECTED one of them:

- `git branch -r --contains HEAD` — empty.
- `git ls-remote --heads origin` — one line only,
  `6201e301becb0b4af92e7b83cebac37fc84ac1f6 refs/heads/main`.
- `gh run list -b feat/kimi-code-backup-lane` — empty.

The correction: a BARE `gh run list` is not empty. It returns runs, all of them
on `main`, the most recent being `0.17.2: close backlog item 14 and file the
lane-lock window`. My earlier "no runs" was wider than the measurement. Only the
branch-filtered form is evidence, and the artifact now records the filtered
command and names the earlier phrasing as too wide.

You cannot re-run these — your sandbox has no network and no `gh` — so they stay
UNVERIFIED from your side and should. I am recording the correction rather than
asking you to accept the claim.

## The revision record

`:15` is the r15 entry. It records that you passed seven tasks and confirmed
both r14 consequences, then each of the three blocking fixes with what was wrong
before, and the two artifact corrections above.

## What I want from you

1. Is this a PASS? The round cap is lifted and "converged with amendments" is
   not terminal here, so if anything is still inadequate, name it and say what
   would be adequate.

2. Do the three fixes as WRITTEN match what you specified, or did I drift while
   adding the reasoning around them? I added justification prose to all three
   that you did not ask for. If any of it contradicts the rule it sits beside,
   that is worse than not having it.

3. If PASS, building starts immediately with Task 1, task by task, each by a
   zero-judgment implementer that sees only its own task text plus the Global
   Constraints and never this debate.
