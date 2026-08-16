# Whole-branch review from the fable-reviewer seat, 0.26.0

**Range:** `8cc00d1345a75f164741f0ea847d86ea97546603..60230437d1ee712e84efbeacd9fd360a3eb008bb`
(14 commits, `a170756` through `6023043`).
**Seat:** `agents/fable-reviewer.md`, dispatched 2026-08-16 by the driving
session. Read-only. Never a merge gate by itself.
**Inputs it was given:** the diff package for exactly that range (commits,
`--stat`, full diff at `-U10`), the frozen plan, the settled design, and the
SDD ledger including every deferred minor and the one user ruling.
**Retained because:** mode diff requires this review before round 1, and its
raw reply is the artifact the round-1 brief cites.

The reply below is VERBATIM. The session's per-finding adjudications follow
it, under a separate heading, and are not part of the reviewer's text.

---

## Reviewer reply, verbatim

### Strengths

- The fresh gate fails closed on every direction I could construct. `Get-FreshPreambleFault` (`tools/read-codex-round-evidence.ps1`, package lines 4004-4061) returns a fault for: no envelope, several envelopes, text after the envelope, any scanner fault, and any missing core field; an empty or whitespace-only lead record canonicalizes to a string with no envelope and lands on "carries no environment preamble at all". The `$null -eq $lead` guard (package line 4113) catches non-text records. I found no input that reaches clean without the envelope being parsed.
- The `Get-BaselineEnvelopeFields` reroute through `Find-EnvelopeSpan` is a faithful refactor. The old and new code check second-open before missing-close in the same order, map "open present, close missing" to the same `$none` fault, and take the identical substring (package lines 3977-3993). The resumed path's messages are untouched.
- The gate placement is correct and defended: `if ($Fresh)` sits after the resumed block and after the brief is proved last (package lines 4097-4124), and the existing `test_a_user_record_after_the_brief_is_refused` is the regression net if it ever moves earlier.
- Task 2's `\z` anchor at `tools/read-codex-round-evidence.ps1:192` and the `Get-EnvDate` canonicalization are both minimal and correct; `Get-CanonicalText` of an empty or garbage value still fails the `TryParseExact`, so the control case (`test_a_date_that_is_not_a_calendar_date_is_still_refused`) holds.
- The Kimi diagnostic branch cannot fall through: `Fail` routes to `Write-Result`, which exits (`tools/read-kimi-round-evidence.ps1:111-115`), so the two sequential `Fail` calls are both refusals, never a double message and never a clean.
- The "four agent-file callers" claim, once a record defect, is now exact: `ConvertTo-NormalizedLF` has callers at `:345`, `:756`, `:757`, `:888` (all agent-file or systemPrompt comparisons) plus the deliberately untrimmed re-hash at `:920`.
- The test discipline is real, not recited: the ledger records red-first splits with the failing side landing on `status: clean` for all seven fresh-gate negatives, which is the exact defect class being closed. Each new refusal case asserts a message a distinct branch produces, so none is unfalsifiable.
- The backlog closing paragraphs claim exactly what the code delivers, including item 56's "STILL OPEN" paragraph and item 61's honest filing of the non-user-record channel with its 60-of-60 measurement. The `:192` citation in item 57's closing paragraph is exact.
- The late amendment (commit `4fdccf4`) that added the record-type limit and the relocated-drift consequence to `codex-brief-binding-fresh-record` matches its pin in `test_multi_model_verify.py` word for word, and the region id is in `DECLARED_REGIONS`.

### Issues

#### Critical

None found.

#### Important

None found.

#### Minor

- `Get-FreshPreambleFault` reports a stray `</environment_context>` close tag after a single well-formed envelope as "carries more than one environment preamble" (`Find-EnvelopeSpan` counts closes, package lines 3956-3958). One envelope plus one stray close is not "more than one preamble". Refusal-direction only, and the same wording behavior exists on the baseline path, so it is a message-precision issue, not a hole.
- The Kimi brief comparison is case-insensitive end to end (`-ne` at the primary check, `-eq` at the diagnostic), which is internally consistent and deliberate, but no test passes an uppercase `-ExpectedBriefSha256`, so the consistency is protected only by comments. This is the same exposure as the Task 1 deferred minor and rides with it.

### Ledger minors triage

The five deferred minors from Task 3:

1. **Weak needle "environment preamble" in `test_novel_text_in_front_of_a_fresh_brief_is_refused`** - ride. The case still fails on the shipped-defect payload binding clean, which is its whole job; tightening the needle to "carries no environment preamble at all" is a one-line follow-up.
2. **`$null -eq $lead` branch untested, message unpinned** - ride. It lands on REFUSED, so the worst outcome is an unexercised refusal message; add its test when item 61's non-user-record design work reopens this code.
3. **`Find-EnvelopeSpan` unreachable `$null` guard** - ride. `[string]` coercion makes it dead on both the old and new code; it was preserved faithfully and can only be harmless.
4. **`$env` as a local variable name** - ride. Style only; PowerShell does not confuse it with the `$env:` drive.
5. **Region does not enumerate the three scanner refusals inside "no text it cannot account for"** - ride. All three land on refusal, and the region's summary phrase covers them truthfully if not exhaustively.

None is fix-before-merge: every one is refusal-direction or cosmetic, and none can make an unmade measurement read as clean.

### Assessment

Ready to merge: **Yes**

The branch closes items 52, 56 and 57 exactly as the frozen plan and spec specify, every new failure direction lands on a refusal, the one Critical found mid-branch was resolved by a user-ruled contract amendment whose pin I verified against the shipped region, and the only findings on the range are message-precision minors already ledgered or of the same weight. The cross-vendor mode-diff debate remains the merge gate; this report is its input.

Range reviewed: `8cc00d1345a75f164741f0ea847d86ea97546603..60230437d1ee712e84efbeacd9fd360a3eb008bb` (14 commits, `a170756` through `6023043`).

Files central to this review:
- `C:\Users\Brandon\Documents\parallax\tools\read-codex-round-evidence.ps1`
- `C:\Users\Brandon\Documents\parallax\tools\read-kimi-round-evidence.ps1`
- `C:\Users\Brandon\Documents\parallax\skills\multi-model-verify\references\model-prompting-notes.md`
- `C:\Users\Brandon\Documents\parallax\skills\multi-model-verify\references\backup-lane.md`
- `C:\Users\Brandon\Documents\parallax\evals\multi-model-verify\test_codex_round_evidence.py`
- `C:\Users\Brandon\Documents\parallax\docs\superpowers\plans\2026-07-27-0150-backlog.md`

---

## The session's adjudications

Each finding was read against the repo before it was disposed of. The
reviewer's own line citations were checked, not taken on authority.

**Minor 1, the stray close tag.** ACCEPTED as accurate, RECORDED as a
follow-up rather than fixed. `Find-EnvelopeSpan` at
`tools/read-codex-round-evidence.ps1:240-242` returns `several` when a
second `</environment_context>` is found after the first close, with only
one open tag present, and `Get-FreshPreambleFault` words that as "more than
one environment preamble". The reviewer's claim that this is pre-existing
was checked and is right: `git show 8cc00d1:tools/read-codex-round-evidence.ps1`
lines 238-240 carry the identical test and the identical `$several`
message. The branch preserved it exactly, which is what the plan required
of the reroute. It is refusal-direction message precision, not the
"unmade measurement reads clean" class, so under the pre-existing-defect
scope rule it is RECORDED, not fixed on this branch.

**Minor 2, the untested uppercase digest.** ACCEPTED as accurate, RECORDED.
Verified: `tools/read-kimi-round-evidence.ps1:906` compares with `-ne` and
`:921` with `-eq`, both case-insensitive, and the argument check's
`-notmatch` is case-insensitive too, so an uppercase digest is admitted and
compares equal to the lowercase computed hash. That is the CORRECT
behaviour - a caller passing the right digest in uppercase should bind -
and the three-way consistency is deliberate and commented. What is missing
is a test that locks it: `evals/multi-model-verify/test_kimi_round_evidence.py`
passes no uppercase `-ExpectedBriefSha256` anywhere. A test-coverage gap
over correct behaviour is not a merge blocker.

**The five ledger minors.** The session had already deferred all five and
the reviewer's independent triage agrees with each disposition. No change.

**Verdict on this review:** no finding blocks the merge, and no finding is
applied on this branch, so the head does not move. Both accepted minors go
to the backlog as named follow-ups. This report is now the required input
to the cross-vendor mode-diff debate, which remains the merge gate.
