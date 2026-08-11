# 0.23.0 plan-debate round records

Retained verbatim. TWELVE rounds plus one VOID round, primary lane
(gpt-5.6-sol via codex exec), session `019fef3e-9b6a-7a21-a49f-686e0d96ac53`.

| round | brief | reply | outcome |
|---|---|---|---|
| 1 (VOID) | `plan-brief-r1.md` | discarded unread | brief-attribution failure, see below |
| 1 | `plan-brief-r1.md` | `plan-reply-r1.txt` | FIX on all six claims |
| 2 | `plan-brief-r2.md` | `plan-reply-r2.txt` | 4 PASS, 1 FIX |
| 3 | `plan-brief-r3.md` | `plan-reply-r3.txt` | 3 FIX, 1 PASS, NOT TERMINAL |
| 4 | `plan-brief-r4.md` | `plan-reply-r4.txt` | PASS, conditional terminal, 3 sampling amendments |
| 5 | `plan-brief-r5.md` | `plan-reply-r5.txt` | FIX (budget ledger), NOT the dry round |
| 6 | `plan-brief-r6.md` | `plan-reply-r6.txt` | PASS, adjudicated dry round, terminal |
| 7 | `plan-brief-r7.md` | `plan-reply-r7.txt` | REOPENED mid-build; FIX on the ceiling and on two byte oracles |
| 8 | `plan-brief-r8.md` | `plan-reply-r8.txt` | FIX: test the fallback under a fault, not by asserting its shadow |
| 9 | `plan-brief-r9.md` | `plan-reply-r9.txt` | FIX: the PowerShell matrix was hand-picked, not the frozen product |
| 10 | `plan-brief-r10.md` | `plan-reply-r10.txt` | FIX: case count wrong; the frozen invariant contradicted itself |
| 11 | `plan-brief-r11.md` | `plan-reply-r11.txt` | FIX: the frozen plan still carried the superseded ceiling |
| 12 | `plan-brief-r12.md` | `plan-reply-r12.txt` | PASS, ADJUDICATED DRY ROUND, terminal |

## The reopening

Round 6 ended the debate. The BUILD then produced a measurement that
falsified a number the freeze rested on: I had estimated the UTF-8 guard at
about 100 tokens and it cost about 420, which left 23 tokens under a
ceiling the debate had set expecting room. The user chose to reopen rather
than let the session pick a number.

Six further rounds, every one finding something real, none contested.

## The void round

Round 1 was dispatched, answered, and REFUSED by
`tools/read-codex-round-evidence.ps1` before the reply was read. The reply
was discarded unread and the round's quota is spent for nothing. The cause
is a transport defect in shipped contract text, written up in
`finding-brief-encoding.md`, and it became this release's fourth work item.

The re-dispatch of the same brief, on the same interpreter, with the
encoding guard applied, bound CLEAN. `plan-reply-r1.txt` is that round.

## Every claim of mine that was wider than its evidence

Six, in a five-round debate, and every one was found by the reviewer rather
than by me:

1. "The budget has grown every cycle and never shrunk." FALSE. Recomputed at
   the release snapshots: 5120, 5120, 5117, 5129, 5404, 5404. It shrank
   once and has been flat for two releases.
2. The mirror paragraph measured 2192 characters, not the 1780 I published.
   I had sliced the wrong line range.
3. "The move is cheap, no contract region sits inside it." True but
   incomplete: six ordinary pins cover it. I found this one myself, before
   the reply arrived.
4. "Expectation 1 cannot pass in a realistic run." Too wide. It can become
   UNOBSERVABLE and fail independently of behaviour.
5. "The route parser is currently untested." FALSE. Six focused tests
   already exist. What is missing is generated combinatorial coverage.
6. "The worst realistic dispatch is 1327 characters." No corpus establishes
   a maximum. It is ONE measured realistic dispatch.

Plus two miscounts: 14 corrupted em dashes where there were 15, and a
fix-verify ledger one unit low.

## The thing I never looked at

`skill_lint.py` is VENDORED, and its own header says "unmodified except this
provenance header" with an instruction to re-diff upstream before editing.
Adding a hard ceiling falsifies three statements in that header. Round 3
found it. I had not opened the header at all.

## Process deviation

`debate-protocol.md` requires the total fix-verify budget to be declared
BEFORE round 1. I declared it at round 5, and the reviewer then corrected
the arithmetic. Both are recorded rather than tidied away.


## The second half's findings, and what they have in common

Rounds 7 to 12 found eight things. Three were defects in code or tests:

- two new byte oracles could pass on EMPTY output - written by me into the
  module whose entire subject is that an unmade measurement must never read
  as a clean one;
- asserting that three mutants survive locked in today's topology while
  proving nothing about whether the fallback works, and was replaced by a
  declared fail-open fault model that kills all three;
- the PowerShell matrix was 19 hand-picked arrangements where the plan had
  frozen a Cartesian product, so "all mutants killed" was true of a matrix
  nobody had specified.

Three more were the same shape as each other, and it is the shape worth
carrying forward: THE CODE WAS RIGHT AND THE RECORD WAS WRONG. A case count
stated two different wrong ways; a frozen invariant that contradicted
itself in consecutive sentences; a frozen plan still carrying a ceiling the
code had already moved past. A frozen plan is what mode diff adjudicates
drift against, so a stale record does not merely mislead a reader - it
makes correct work read as drift, or gets taken as authority and the
correct work reverted.

---

# The DIFF debate

Same directory, different debate. The plan debate above froze what to
build; this one reviews what was built, over `8ddda15..28bfd07`.

## Required input: the whole-branch review

`fable-whole-branch-review-8ddda15-28bfd07.md` — the `agents/fable-reviewer.md`
seat's raw reply, retained range-bound, with this session's per-finding
adjudication table appended. Nine findings, no critical ones, verdict
"ready to merge with fixes". Seven accepted as fixes, one accepted with no
action, one ESCALATED into the debate.

## Rounds

| round | brief | reply | outcome |
|---|---|---|---|
| 1 | `diff-brief-r1.md` | `diff-reply-r1.txt` | FIX. Ruled the escalation, then found four spec drifts the whole-branch review missed |
| 2 | `diff-brief-r2.md` | `diff-reply-r2.txt` | FIX. The fix re-review was not dry: one blocking spec miss and four record defects |
| 3 | `diff-brief-r3.md` | `diff-reply-r3.txt` | FIX. The fail-first repair accepted; a licence obligation and two record residues found |
| 4 | `diff-brief-r4.md` | `diff-reply-r4.txt` | ESCALATE. Two claims wider than their evidence, and the ROUND CAP reached |
| 5 | `diff-brief-r5.md` | `diff-reply-r5.txt` | ESCALATE. Two more, one of them introduced BY round 4's fix; budget exhausted |
| 6 | `diff-brief-r6.md` | `diff-reply-r6.txt` | FIX. A third unfrozen reading in the generator; two implementation areas cleared |

## What round 1 found, and why it matters more than the count

The escalated point was ruled the way the session had proposed: record
`tools/check-drift.ps1:700`, narrow the claim, open a follow-up, do NOT
fix it inside a range that never enumerated the file. That is
`debate-protocol.md:108-126` applied conjunctively, and it is the first
time this repo has drawn an explicit certification boundary rather than
either fixing everything in sight or saying nothing.

The four new findings were all SPEC DRIFT against the frozen plan, and
all four had survived a whole-branch review that read the same diff:

1. **Sweep B was 88 cases where the plan froze 360.** Presence was never
   crossed with form or escape at all. "All ten mutants killed" was true
   of a matrix nobody had specified — the same defect round 9 of the plan
   debate found in the PowerShell module, repeated in the module written
   after it. The rebuild changed which cases do the killing: three mutants
   now die on `presence=twice` and `presence=absent` cells INSIDE the
   specified product. It did not create those shapes — the 88-case build
   carried equivalent hand-added cases outside any enumeration, and the
   whole-branch review names old `B[sandbox,absent]` as mutant 9's killer.
   (This sentence first claimed the cells could not have been generated
   before. Corrected at diff round 3, in place rather than below, because
   a synopsis is not a verbatim record and a reader who stops here would
   otherwise carry the refuted claim away.)
2. **The required upstream re-diff was never performed.** The header
   disclosed that honestly, and the reviewer ruled that disclosing a
   skipped step does not discharge a frozen task. Correct: the question
   the step answers is whether UPSTREAM moved, and a local diff cannot
   answer it. Performed at the fix; upstream had not moved since import.
3. **The required new backlog entry did not exist.**
4. **The required retained mutation output did not exist.** The
   whole-branch review had noticed it and filed it under "could not
   verify"; the cross-vendor lane reclassified it as an unmet retention
   requirement, which is what it is.

Two more claims of the session's were narrowed: "5227 tokens" is a linter
estimate of `len(body) // 4`, and "the only outstanding task" was true
only of frozen-plan tasks.

## The shape of it

Three of the four drifts are the same failure: a frozen requirement that
produces no artifact when skipped. A missing test fails a gate. A missing
RECORD fails nothing, so nothing catches it but a reader comparing the
plan to the tree line by line. That is what mode diff is for, and it is
why the whole-branch review is an input to it rather than a substitute.

## Other artifacts

- `finding-brief-encoding.md` — the void round's transport defect, now
  carrying its reconciled character delta and the two dispatch sites this
  release does NOT guard.
- `mutation-evidence.md` — the retained failing output for all eighteen
  mutants across both generated modules, each naming the case that killed
  it.

## Round 2, and the finding worth carrying forward

The fix re-review found that round 1's fix to whole-branch finding 4 had
made the docstring honest and left the measurement missing. The frozen
plan required a test proving the PRE-CHANGE implementation does not fail
above the ceiling; two drafts restated the old rule inline instead of
running it, the second one openly admitting in its own docstring that it
could not fail. AN HONEST DESCRIPTION OF A MISSING MEASUREMENT IS STILL A
MISSING MEASUREMENT. The fix is a hash-pinned fixture holding the linter
frozen at `dd0db13` and a proof that RUNS it.

That is the same shape as round 1's finding B, where the vendored header
disclosed a skipped upstream fetch and the disclosure was mistaken for
discharge. Twice in one debate, this session substituted an accurate
account of not having done something for doing it.

Four narrower corrections, all of them claims of mine wider than their
evidence:

- the sweep-B derivation cited rules 5 and 7 when rule 1 is what licenses
  dropping the escape axis;
- "a test fails if any declaration is removed" was true only of the
  module, not of the authoritative plan, so the test was widened;
- "round 13 of the diff debate" conflated the cycle exchange number with
  the diff round number;
- "cells the first build could not generate" was refuted by the retained
  whole-branch review, which names old `B[sandbox,absent]` as mutant 9's
  killer. The rebuild moved equivalent inputs into the specified product;
  it did not create the shapes.

Note that `diff-brief-r2.md` is retained VERBATIM and therefore still
contains two of those overstatements. That is what a retained record is
for: the corrections live in the code and the backlog, not in a rewritten
brief.

## Round 3, and the obligation nobody was reading

The blocking finding was `evals/tools/LICENSE-THIRD-PARTY.md`. It still
said `skill_lint.py` was "unmodified except the provenance header" while
the file's own header, four lines of code away, recorded a substantive
delta. Two promises to two different readers, and only one was kept. It is
also the Apache-2.0 section 4(b) statement of changes, which the notice's
own last paragraph cites, so it is a licence obligation rather than a
courtesy.

NOTHING IN THE SUITE READ THAT FILE. That is the whole mechanism: the file
header was pinned, so it stayed true; the notice was not, so it went false
and stayed false for the length of a branch. It is now pinned by two
tests, which is more than the reviewer asked for and is the part that
stops the next recurrence.

Two record residues alongside it, both the same shape as each other: a
correction applied where I was looking and not where else the same
sentence lived. One stale "round 13 of the diff debate" in a docstring
after the module's invariant block and the plan were both fixed; and the
README's own synopsis still carrying "cells the first build could not
generate" sixty lines above the paragraph refuting it.

## The through-line of this diff debate

Six rounds, and every one of them found something: four spec drifts and
two narrowed claims at round 1, one blocking spec miss and four record
defects at round 2, one licence obligation and two record residues at
round 3, two overstated claims at round 4, two more at round 5, one
specification gap and one recreated total at round 6. Almost none of them
were about code behaviour.

**Which briefs still carry uncorrected claims.** Retained briefs and
replies are verbatim and are never edited, so some of them still state
things later rounds refuted. `diff-brief-r2.md` says three mutants die on
cells the first build could not generate, and that sweep B's values follow
from rules 5 and 7 alone. `diff-brief-r5.md` says the fix range touches
three files; it touches five. `diff-brief-r6.md` says five rounds found
seventeen things; the enumeration above says eighteen. Every correction
lives in the code, the plan and the backlog, which is where a reader acts
from.

(An earlier draft of this paragraph said "eleven findings", which
contradicted this file's own round table. The count is now enumerated
rather than totalled, because a total is the kind of number that goes
stale the moment a round is added.) The code was right nearly every time. What kept being wrong was
the RECORD: a plan surface that did not match the tree, a licence notice
nobody pinned, a synopsis contradicting its own corrections, and twice, an
accurate description of a missing measurement standing in for the
measurement.

A missing test fails a gate. A missing or stale RECORD fails nothing, so
the only thing that catches it is a reader comparing the frozen plan to
the tree line by line. That is what mode diff is, and it is why the
whole-branch review is an input to it rather than a replacement for it.

## Round 4, and the cap

Two findings, both mine, both record-only, and both the same species as
everything above: the licence notice said the frozen fixture's "content
is hash-pinned" when the test splits the banner off and hashes only the
copied text, and the through-line paragraph above said "eleven findings"
when this file's own round table lists twelve. Neither touched code. Both
were claims wider than their evidence, in a file whose subject is claims
wider than their evidence.

The reviewer then did something worth recording. It counted four
consecutive contested exchanges, observed that the round cap declared in
the round-1 brief was reached even though two fix-verify units remained,
and returned ESCALATE rather than absorbing the finding or quietly
continuing. The cap and the fix-verify budget are separate meters, which
is exactly what backlog item 24 changed in 0.22.0; this is the first time
the separation has been exercised in a live debate.

The user was asked, chose to reset the cap, and authorized ONE more
round. That round is the confirming re-review.

## Round 5, the authorized confirming round, which was not dry either

Two findings, both mine, both narrower than round 4's:

- The licence notice had been narrowed at round 4 to say banner prose is
  excluded from the fixture's hash. It then went on to say banner edits
  break no pin, which is false: the same test splits on the banner's two
  75-dash separator lines and requires exactly three parts, so editing a
  separator fails a STRUCTURAL assertion even though it changes no hash.
  Two consecutive drafts of one paragraph, wrong in opposite directions —
  first claiming more coverage than the test has, then more freedom.
- The round-5 brief said the fix range "touches three files". It touches
  five: three fix targets plus the two retained round-4 artifacts. The
  brief is retained verbatim and still says three; the correction lives
  here, which is the same treatment `diff-brief-r2.md` got.

The reviewer then paused rather than spending another exchange, because
the user's cap reset had authorized exactly one round and this was it.

## The user's second intervention

At round 5's pause the ledger read 6 authorized, 5 spent, 1 remaining. The
session put four options to the user, including merging on ESCALATE with
recorded risk acceptance and stopping outright, and said plainly that the
findings were shrinking each round and that nothing since round 2 had been
about code behaviour. The user chose to EXTEND BY UP TO THREE ROUNDS and
let the debate run until it goes dry rather than stop at a number.

New ledger: 8 authorized, 5 spent, 3 remaining.

Worth naming why that is the harder and better call. Round 5's first
finding was a defect INTRODUCED BY ROUND 4'S FIX: narrowing the notice's
overclaim overshot into an underclaim. A fix is new code and gets no
discount, and this is what that rule looks like in a record file rather
than in a function.

## Round 6

Two findings, and one of them is not a record defect.

**The generated matrix had a THIRD unfrozen interpretation.** The plan
recorded two readings the freeze had not settled — how `twice` crosses
with form and escape, and what `absent` does with axes that have nothing
to act on. It did not record a third: `K:` and `K: ` have no value, so
"escape in value" is undefined for them too. `render_field` resolved it
after the freeze, by writing the escape where the value would have been,
and specifically to AVOID the duplicate cells that `absent` deliberately
keeps. Two of the three readings were in the authoritative record and the
third was only in the code, and the two that were recorded went opposite
ways from the one that was not.

The reviewer was explicit that no expected verdict is read from
production — rule 1 makes either rendering verdict-neutral — so this is a
specification gap, not a wrong answer. It is now in the plan, with the
reason the two degenerate crossings are treated differently: an absent
key has no line and so no value position, while a valueless form has a
value position that is merely empty.

**And a total, three rounds after totals were removed.** The round-6 brief
said "five rounds have found seventeen things". The README's own
enumeration comes to eighteen. Round 4 removed a total from this file
precisely because totals go stale, and the very next brief written after
that correction contained a new one. The brief is retained verbatim and
still says seventeen.

**What round 6 did NOT find, which is worth as much.** The brief asked the
reviewer to spend the round on the three places the session built and
cannot audit neutrally, rather than on the record surface: the rebuilt
`sweep_b`/`render_field`, the FAIL_OPEN fault model, and the behavioural
cap change that no generated suite covers. It found the specification gap
above in the first, and reported no substantive defect in the other two,
citing the lines it checked: the fault model proves the unchanged fallback
over the complete matrix before mutating it, and the cap change matches
the frozen four-tool rule with visibility, exact-cap and exhaustion
coverage.
