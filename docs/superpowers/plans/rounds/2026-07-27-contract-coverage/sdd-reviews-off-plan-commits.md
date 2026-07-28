# The two SDD reviews that authorized the off-plan commits

The Fable whole-branch review's Important 1
(`fable-review-8d54f6c-23709fa.md`) is correct: five of the twelve
commits in `8d54f6c..23709fa` have no basis in plan revision 7, and the
reviews that authorized them were never retained. This file states
precisely what survives and what does not, because the honest answer is
partial.

Both reviews were subagent dispatches inside the controlling session. The
subagent-driven-development skill retains its artifacts in the SDD
workspace, which was deleted at cleanup; the review replies themselves
were returned in-session and were never written to disk at the time. That
was the error.

## 1. Final whole-branch review — `8d54f6c..4ec80b1`

**Raw reply: LOST.** Dispatched on Opus over an eight-commit, 135 KB diff
package. The session's context was compacted afterwards, so the verbatim
text is gone and cannot be recovered. What follows is the compaction
summary's account of it — a second-hand session claim, weaker evidence
than the reply itself, and labelled as such.

Verdict recorded: safe to merge. Four gates confirmed green at the time:
216 passed / 1 skipped, `skill_lint --strict` clean, `skill_scanner` 0
findings, trigger evals clear.

**Its Important finding**, which produced commit `f872b34`:

`DOC_PATHS` at `test_contract_coverage.py:485-488` covered only
`skills/multi-model-verify/references/*.md` and `agents/*.md`.
`skills/multi-model-verify/SKILL.md` and `commands/*.md` are contract
documents and were not scanned. The reviewer verified live that appending
a well-formed unpinned region to `SKILL.md` left all 46 tests green, and
that appending a malformed unterminated marker did the same. The second
defeats the design's headline invariant. No document named the scanned
set. It reported verifying the widening as a drop-in: `collect_regions`
over `skills/**/*.md` + `agents/*.md` + `commands/*.md` parsed clean, same
nine regions, no new errors.

**Its Minor findings**, which produced `8a6a9fb`, `8d313b9` and `23709fa`:
region shrink in lockstep stays green; `CLAUDE.md:64` was 105 characters
where the file wraps near 72; `test_flash_implementer.py:141` carries the
same `evals/**/*.py` sweep glob with no exclusion; `PIN_PATHS` excludes
the self-quoting module by exact filename only.

It reported that it could not produce a false pass on a declared region
after probing roughly twenty near-miss forms, that it independently
verified the three fixtures byte-verbatim against git, and that it
confirmed all four live documents byte-identical after stripping markers
and normalizing.

Its closing recommendation, as recorded: the `DOC_PATHS` widening was the
only finding that can create a false belief that a rule is locked, and it
had verified the fix to be a drop-in that changes nothing else.

**Note the dependency this creates.** The independent verifications this
review claims — fixtures byte-verbatim against git, documents
byte-identical — now rest on a summary of a lost reply. The Fable review
re-derived the document claim by its own method and confirmed it
(`fable-review-8d54f6c-23709fa.md`, Strengths 2), and named the fixture
claim as a gap it could not close under its tool grant (Minor 4). The
fixture claim therefore still needs first-hand verification. It is put to
the cross-vendor lane in round 1.

## 2. Scoped re-review of the fix wave — `4ec80b1..23709fa`

**Raw reply: RETAINED VERBATIM** at
`opus-fixwave-rereview-4ec80b1-23709fa.md` in this directory. Dispatched
on Opus. Verdict: SAFE TO MERGE.

It reproduced every proof independently rather than reading the diff,
mutation-tested each of the five new tests, word-diffed the `CLAUDE.md`
paragraph, and audited the widened scan for collateral damage. It raised
one Minor of its own (no fenced-code-block awareness) and one "also
found" outside its range.

## Both reviews' assurances, after the diff debate refuted two of them

Added after the mode-diff round 1. Reading this file without these
corrections would leave two false impressions.

**The lost review's classifier assurance is REFUTED.** It reported
probing roughly twenty near-miss forms without producing a false pass on
a declared region, and concluded the `DOC_PATHS` gap was the only path to
a false belief that a rule is locked. The cross-vendor lane then produced
one it missed:

```python
with pytest.raises(AssertionError):
    assert "Entire marked region." in body
```

That test passes when the region text is ABSENT, and the checker read the
region as covered. Three shapes did it — `raises`, `suppress`, and
`try`/`except AssertionError`. This is false coverage, the direction the
design forbids, and no live instance existed in the repo, so it had never
shown itself. The probe set behind the lost review's assurance cannot be
audited, because the reply is gone. Treat the assurance as withdrawn, not
merely dated.

**The retained re-review's no-stale-design-text claim is REFUTED.** It
stated that nothing in the design spec named the pre-widening globs, so
the widening left no description behind. The design's Inputs section did
name them, and still did at `23709fa`. Corrected in the same fix wave as
the entry above.

Both refutations point the same way. The two reviews were thorough on
what they examined and wrong about the completeness of their own sweep.
That is an argument for the cross-vendor gate, not against those reviews.

## The off-plan commits, restated plainly

| commit | source | plan basis |
|---|---|---|
| `4ec80b1` | Task 7 review, human ruling | none — corrects the plan itself |
| `f872b34` | final whole-branch review, Important | none |
| `8a6a9fb` | final whole-branch review, Minor | none |
| `8d313b9` | final whole-branch review, Minor | none |
| `23709fa` | final whole-branch review, Minor | none |

All five were authorized by review findings, not by the plan. Four of the
five rest on a review whose raw text is lost. The Fable reviewer verified
each commit's content directly and found all five strengthen the branch.
That is the strongest statement the record can currently support, and it
is a content verification, not a provenance one.
