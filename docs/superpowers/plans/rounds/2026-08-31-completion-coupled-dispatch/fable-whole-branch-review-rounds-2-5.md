# Fable whole-branch review, rounds 2-5

Range-bound artifact for branch `item32-detached-dispatch`. Companion to
`fable-whole-branch-review-8af6ae0..3029599.md`, which holds round 1.

Every finding below was REPRODUCED by the driving session before it was
accepted. Where reproduction changed the finding, that is recorded. No
finding was accepted on the reviewer's word alone.

## Ranges

| round | range | commits reviewed | verdict |
|---|---|---|---|
| 1 | `8af6ae0..3029599` | whole branch to that point | With fixes |
| 2 | `3029599..c0ef41a` | 1 (the round-1 fix commit) | With fixes |
| 3 | `c0ef41a..846fc64` | 2 | With fixes |
| 4 | `846fc64..0ad2e32` | 1 | No |
| 5 | `0ad2e32..d264005` | 1 | With fixes |
| - | `d264005..ad62961` | 1 | NOT REVIEWED (see below) |

Rounds 4 and 5 were additionally asked to sweep four defect CLASSES over
the WHOLE branch, not only their own range, and to report an instance or
an explicit NONE. Both did.

As of the commit that ADDED this file, `ad62961` was the only commit
no Fable round had seen. That sentence went stale the moment this file
was committed, because the commit carrying it is unreviewed too - which
is the self-quoting-document trap this repo has hit before, and
cross-vendor round 1 caught it here. Read the table above against `git
log` rather than trusting this sentence. It implements
exactly the two edits round 5 named as its merge floor, plus three of its
minors. Round 5 stated it would verify those "by running the suite and
one grep rather than by a fifth whole-branch pass". The cross-vendor
debate reviews the full range `8af6ae0..ad62961` and is the gate that
covers it.

## The pattern this branch has to answer for

Rounds 2, 3, 4 and 5 EACH found that the previous round's fixes
reproduced the class they fixed. That is four consecutive rounds, and it
is the single most important fact about this branch's review history:

- round 2: 3 of its 4 Important findings were defects introduced by
  round 1's fix commit.
- round 3: 3 of 4, again introduced by round 2's fixes.
- round 4: 3 of 4, again.
- round 5: 2 Important, both again, and both single-line.

The size of the defects fell monotonically (a false refusal claim, then a
guard that could not see its own citation form, then a wrong argument
name), which is the reason the session stopped at round 5 rather than
running a sixth.

## Round 2 findings and adjudication

| # | finding | adjudication |
|---|---|---|
| 1 | Two new call-site pointers used a bare `(round-dispatch-operation)` form the citation guard cannot see | ACCEPTED. Reproduced: the guard's regex matched only `model-prompting-notes.md's <id>`. Fixed both pointers AND widened the guard. |
| 2 | The never-END clause covered 2 of 5 call sites | ACCEPTED. Reproduced by grep. Three kimi sites had the WHAT but not the clause. |
| 3 | The kimi resume paragraph claims a refusal that does not exist on that lane | ACCEPTED. Reproduced: `-ExpectedMirrorPath` is compared against `-MirrorPath`, both caller arguments; `read-kimi-round-evidence.ps1` has zero working-directory handling. |
| 4 | The operation region asserts a measurement contradicted by backlog item 68 Part C | ACCEPTED AND BOTH SIDES REFUTED. The retained transcript shows the executor was NOT refused (Part C was wrong) and did NOT do every step correctly (the region was wrong). Both texts rewritten to what the transcript shows. |

## Round 3 findings and adjudication

| # | finding | adjudication |
|---|---|---|
| 1 | The never-END clause is pinned on 3 of 5 sites; the two codex sites are unguarded | ACCEPTED. Only one assertion existed and it read `backup-lane.md` only. Added a per-section pin for the codex sites, mutation-verified. |
| 2 | `backup-lane.md` says the working-directory binding is both enforced by the client and enforced by nothing | ACCEPTED. The session's own previous fix over-corrected. Rewritten to state a consequence, explicitly one layer away and unmeasured. |
| 3 | `-ExpectedMirrorPath` is still credited with a construction-time refusal in a PINNED paragraph | ACCEPTED, and the most serious of the branch. The suite was ENFORCING the false sentence. Corrected in the doc, the pin, and both tool comments. |
| 4 | The bare-id regex risks false positives; a backticked citation is a false negative | ACCEPTED IN PART. The suggested widening to backticks was MEASURED and REJECTED: it matches 8 tokens over the scanned documents and only 2 are regions. Solved from the other direction instead (see round 4). |
| 5 | The item-51 fix removed one of two mentions | ACCEPTED for the one remaining deficient mention. The other four backlog citations were judged to already state their content; round 5 agreed and triaged them "ride". |
| 6 | Part C cites a transcript the repository does not retain | ACCEPTED. The transcript and its graded verdicts now ship beside the record. |
| 7 | The reaper docstring is silent on the consequence | ACCEPTED. |

## Round 4 findings and adjudication

| # | finding | adjudication |
|---|---|---|
| 1 | `-ExpectedMirrorPath` still credited with a recorded identity at `SKILL.md:290` and in the tool's own BLOCKED message | ACCEPTED. The previous fix reached four places and missed two, one of them a runtime string. |
| 2 | The citation guard's central claim is false for every file but one; both rewritten citations moved from one invisible form to another | ACCEPTED, and this is the sharpest finding of the branch. The dangling check now reads any file's possessive and verifies the named file DECLARES the region. Mutation-verified in both directions. |
| 3 | The consequence paragraph names a binder rule that would not fire | ACCEPTED. Read the binder: an unchanged file passes both the truncation rule and the prefix hash; the empty-slice rule is what refuses. Paragraph corrected. |
| 4 | Part C understates its own transcript | ACCEPTED. Counted: 18 shell calls, 13 Bash and 5 PowerShell, 3 errors, none a permission denial. |
| 5 | Per-section pins for the LAST call in each file run to EOF | ACCEPTED. Bounded at the next heading, mutation-verified by drifting a clause past one. |
| 6 | The backlog cites a region id bare, outside DOC_PATHS | ACCEPTED, rewritten resolvable. The scope limit is now recorded in the guard's docstring. |
| 7 | Awkward phrasing | ACCEPTED. |

## Round 5 findings and adjudication

| # | finding | adjudication |
|---|---|---|
| 1 | The SKILL.md fix names `-MirrorPath`, which `-Prepare` does not take | ACCEPTED. Verified: `dispatch-round.ps1` contains no `$MirrorPath`. Took the reviewer's stronger recommendation and DELETED the clause rather than correcting the name, recovering 35 tokens against a 28-token margin. |
| 2 | The section bound went into 2 of the 3 tests sharing the idiom; the third has POSITIVE assertions | ACCEPTED. Reproduced at `test_multi_model_verify.py:1026`. The earlier mutation could not have caught it because it asserts different strings. |
| 3 | A declared two-word id is invisible to the dangling rule outside one file | ACCEPTED AS A RECORDED LIMIT. Zero instances (`lane-lock` is the only two-word id and is not cited that way). Recorded in the docstring rather than fixed. |
| 4 | The dangling test's SCOPE paragraph says the opposite of what the code now does | ACCEPTED. |
| 5 | The heading bound reads `##` and not `###` | ACCEPTED AS A RECORDED LIMIT. No instance today; recorded in the comment. |

## What the session refused or narrowed

- Round 3's backtick widening: MEASURED and REJECTED with the measurement
  recorded in the test's own docstring.
- Round 3's item-51 sweep: narrowed to the one deficient citation, with
  the reasoning stated. Round 5 independently agreed.
- Round 5's finding 1: the session took a STRONGER action than proposed
  (deletion rather than correction), on the reviewer's own argument that
  the clause was not worth its tokens.

## Verification state at `ad62961`

- Full suite, Windows PowerShell 5.1 and PowerShell 7, both run at
  `d264005`: 2715 passed / 14 skipped and 2714 passed / 15 skipped, both
  exit 0. Re-run at `ad62961` before the debate.
- All four fast gates exit 0.
- Every guard added in rounds 2-5 was mutation-tested. One mutation was
  itself wrong and passed; the session caught that and redid it.
