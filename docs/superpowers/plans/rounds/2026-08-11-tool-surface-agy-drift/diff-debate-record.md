# 0.24.0 diff debate — record

Mode `diff`, over the branch `0.24.0-tool-surface-agy-drift`. This file is
a SYNTHESIZED STANDING RECORD and is read as current: superseded
conclusions are marked superseded in place with the adjudication that
replaced them. The `diff-brief-r*.md` and `diff-reply-r*.txt` files beside
it are VERBATIM ARTIFACTS and are never rewritten.

## Meters, declared BEFORE round 1

Written here before any round was dispatched, which is what makes the
declaration a control rather than a description.

- **Round cap: 4 CONSECUTIVE CONTESTED exchanges.** A round is contested
  while any contested point is OUTSTANDING, whether it was raised that
  round or earlier.
- **Total fix-verify budget: 4 units**, a SEPARATE meter from the round
  cap. Exhaustion PAUSES for user authorization; it never certifies.
- **Both authorized by the user in advance**, in answer to a question that
  named the alternatives (lean 2/2, standard 4/4, deep 6/6, or no
  cross-vendor rounds at all). The user chose 4 and 4.
- **Termination requires an ADJUDICATED DRY ROUND**: no new substantive
  finding AND no outstanding contested point. A reviewer PASS is never
  terminal by itself.

The plan-mode debate for this same branch is a different debate with its
own meters, which it exhausted at 6/6. Nothing carries over.

## Required input: the whole-branch reviews

Mode diff requires the Fable whole-branch review to run on the SAME RANGE
before round 1, its raw reply retained as a range-bound artifact, and the
round-1 brief to cite it with this session's per-finding adjudications.

| Artifact | Range | Verdict |
|---|---|---|
| `fable-review-1-ef428c3-5133f98.md` | `ef428c3..5133f98` | ready to merge WITH FIXES; 2 Important, 4 Minor |
| `fable-review-2-ef428c3-710d74f.md` | `ef428c3..710d74f` | ready to merge YES; 0 Important, 4 Minor |

Review 2 exists because review 1's fixes are NEW CODE and a fix gets no
discount: a review of an older head is not a review of this branch.

Adjudications: build checkpoint amendments 7 and 8. Every review-1 finding
was ACCEPTED and fixed. Of review 2's four, one was fixed, one was FILED as
backlog item 40 under the scope rule, one tightened an assertion, and one
was recorded as verified-by-reading with no change requested. The round-1
brief puts the two dispositions worth attacking in front of the reviewer
explicitly.

## Pre-dispatch controls, all measured before round 1

| Control | Result |
|---|---|
| Back-channel enumeration (`git ls-files --cached --others '*AGENTS.md' '.agents/*' '.kimi-code/*'`) | EMPTY. No mirror needed; the reviewed tree is the repo itself. |
| Reviewer context probe | `clean`, exit 0. `repo_scoped` 0, `plugin_cache_scoped` 0, `unknown_scoped` 0, `skills_after` 0 (from `skills_before` 29). |
| Global instruction file | `C:\Users\Brandon\.codex\AGENTS.md` PRESENT. Recorded, not a stop: nothing available removes it, and it survives a clean probe. |
| Skill-disable override | sha256 `180f09f50d282b5603f1c0d0621f2913ff66c8b7798e7a2f3b7fe8d41f432bb8`, 2313 bytes. Hashed INDEPENDENTLY of the probe's own report; the two agree. |
| Tool surface, pwsh 7 | `clean`. 133 baseline tools, `dispatch_tools` 0, `node_repl` present but SILENT. |
| Tool surface, Windows PowerShell 5.1 | `clean`, byte-identical result. Both hosts run because a green suite on one host proves one interpreter. |

**What the tool-surface result does NOT mean**, restated here because a
debate record is exactly where this gets over-read later: absence in pass 2
is a MITIGATION, never proof of removal, and the probe reads
`codex app-server` while the round dispatches `codex exec`, so it is a
PROXY for the reviewer's own surface. Item 39 carries the measurement.

## Rounds

(appended as they land, with the round-evidence binding verdict for each)

### Round 1 — 2026-08-12, binding CLEAN

Fresh dispatch, session `019ff4eb-346e-7be2-9af3-520ebc876707`. Brief
`diff-brief-r1.md`, reply retained verbatim at `diff-reply-r1.txt`.

**Six FIX, one PASS, one ESCALATE.** Every finding was verified against the
code before anything changed, and every one was ACCEPTED. Two were faults
in this branch's own earlier fixes. Adjudications: build checkpoint
amendment 9. Fixes committed at `ac7dc43`.

Meters after round 1: **1 contested exchange of 4; 1 fix-verify unit of 4.**

### Round 2 — 2026-08-14, binding FAILED, reply DISCARDED UNREAD

Resume of the same session. Brief `diff-brief-r2.md`, canonical sha256
`a04f122d145ce793...`. The client exited 0 and wrote a 9233-byte reply.
The round-evidence binding then FAILED:

    a resumed slice carries a user record in front of the brief that does
    not repeat the client's own preamble from this session, so it is
    unattributed text in front of the reviewer

Under the contract a non-clean binding means the reply is DISCARDED
UNREAD, and it was. **No content from that reply has been read, quoted, or
acted on, and none appears anywhere in this branch.** The round's quota is
spent for nothing.

**Cause, measured rather than reasoned.** Round 1 ran on 2026-08-12 and
round 2 on 2026-08-14. The session's first user record is 1532 characters
- the AGENTS.md instructions block plus `<environment_context>` dated
2026-08-12. The record the resumed slice placed in front of the brief is
390 characters: `<environment_context>` ALONE, dated 2026-08-14, with no
instructions block. Shorter AND differently dated, so the identity test
cannot match them.

**The guard was right and is not being relaxed to get past it.** Its rule
is that anything in front of the brief must be text this client already
emitted in this session, so novel text cannot reach the reviewer ahead of
the brief. A refreshed environment context has never been emitted in that
session. This is the rule working, on a case it was never measured
against: the bound was earned from rounds that all ran inside one day.
Filed as backlog item 42, priority HIGH.

**Narrowed at round 3, in place.** This entry first said the item blocks
"any debate that spans midnight". That is wider than the evidence. The
binder applies its identity test only when a resumed slice carries TWO
user records, so the condition is a resumed slice carrying a REFRESHED,
NON-IDENTICAL preamble ahead of the brief. A day boundary is the one cause
OBSERVED to produce that refresh, once. A resume that refreshes nothing
binds normally.

**Meters are UNCHANGED at 1 of 4 and 1 of 4.** A transport failure is not
an exchange. Nothing was adjudicated, contested, or conceded, because
nothing was read.

### Round 2, RETRY — 2026-08-14, same session and same day, binding CLEAN

Dispatched again on the user's decision, after the options and their costs
were put to them. Brief `diff-brief-r2.md` with one paragraph added
telling the reviewer its earlier answer was never read and must not be
referred back to. Canonical sha256 `629f3a81a89e5787...`. Reply retained
verbatim at `diff-reply-r2.txt`.

**This retry MEASURED what item 42 had recorded as unknown, and the item
has since been updated to say so.** With the environment context already
refreshed inside the session, the same-day resume carried the brief ALONE -
one user record, no preamble - and bound clean.

That is a workaround, not a fix, and the workaround is that **a resume
carrying no refreshed preamble binds**. Staying inside one day is the only
way observed to get that rather than the condition itself; what else
triggers a refresh is unmeasured. This paragraph said "records as
unknown", "stands unchanged" and "inside one day" after all three had
stopped being true - stale record text found by round 4.

**Five FIX, four PASS.** Every finding was verified against the code
before anything changed. Two were faults in fixes made at round 1, and one
was a false sentence the session wrote itself. Adjudications: build
checkpoint amendment 11.

| # | Finding | Disposition |
|---|---|---|
| 1a | status and feature id windows collide past 100 polls | FIXED, bases derived from the poll count |
| 1b | `{"result":{"data":null}}` reduces to an empty surface | FIXED, blocks |
| 2 | the disabled-feature policy was read but never enforced, and a test certified `memories=True` as clean | FIXED, blocks; policed list derived from the flags sent |
| 3 | `%` absent from the cmd metacharacter set | FIXED, such a path is refused rather than launched |
| 4 | `[string]` flattened `null` and `""` in the watcher | FIXED, values keep their JSON type |
| 5 | the workflow comment "as soon as it existed" was false | FIXED at the source |
| - | round-1 parser repairs, proxy propagation, the verification record, item 40's disposition | PASS |

Eleven new probe cases and two new drift assertions were watched RED
against the pre-fix code, with 31 existing probe cases green in the same
run and exactly two drift assertions failing.

Meters after this round: **2 contested exchanges of 4; 2 fix-verify units
of 4.** Not terminal: termination needs an adjudicated DRY round, and this
one found five things.

### Round 3 — 2026-08-14, same-day resume, binding CLEAN

Brief `diff-brief-r3.md`, canonical sha256 `e79ba5ac0fef7627...`. Reply
retained verbatim at `diff-reply-r3.txt`. **Four FIX, three PASS.**
Adjudications: build checkpoint amendment 12.

| # | Finding | Disposition |
|---|---|---|
| 1a | missing `data` and null `data` collapsed, so a null blocked with the wrong reason - and a case REQUIRED that wrong sentence | FIXED, reported separately |
| 1b | round 2's feature-entry schema was only applied to POLICED names, so a malformed entry elsewhere still read clean | FIXED, every entry validated |
| 2 | `-eq` is case-insensitive, so `Memories` satisfied `--disable memories` and contradicted round 2's own declared limit | FIXED, `-ceq` |
| 3 | `ConvertTo-Json` truncates silently at depth 2, in the token AND the snapshot write | FIXED, `-Depth 100` in both |
| 4 | item 42 said "not measured" after the retry measured it; "spans midnight" was wider than one observed cause | FIXED at all three sites |
| - | the derived id windows, the percent refusal, the corrected false sentence | PASS |

Seven new probe cases were watched RED against the pre-fix code with 41
existing cases green in the same run.

**Two claims were NARROWED by measurement rather than confirmed**, and one
of them was this record's own. Of three new drift assertions only one went
red; measuring why showed a Hashtable truncates to a type name but a
PSCustomObject truncates to `@{deep=one}`, a string that still carries the
nested text. One assertion had therefore been checking the wrong marker and
passed against the defect - vacuous, in a fixture written to catch vacuous
behaviour - and the nested-CHANGE scenario passed pre-fix because the
truncated text still differed. The truncation corrupts the STORED value; it
did not blind change detection for this shape. Corrected assertion now red;
the change scenario kept and labelled a regression guard.

Meters after this round: **3 contested exchanges of 4; 3 fix-verify units
of 4.** Round 4 reaches both caps. Exhaustion PAUSES for user
authorization; it never certifies.

### Round 4 — the CAP round, binding CLEAN, verdict DRY: NO

Brief `diff-brief-r4.md`, canonical sha256 `20777e224eb333ee...`. Reply
retained verbatim at `diff-reply-r4.txt`. **Two PASS, four FIX.** The brief
asked for the dry question to be answered explicitly, and told the
reviewer not to soften it to help the branch land nor invent an objection
to look rigorous. It answered **DRY: NO**, naming one Important functional
false-clean, one moderate serialization workstream, and one minor repeated
record-width cleanup.

| # | Finding | Disposition |
|---|---|---|
| 1 | `data` coerced with `@()` instead of checked; two enablement members read as the first | FIXED, the Important one |
| 2 | `-Depth 100` had no truncation detection; nested-array cases missing | FIXED, by measuring depth - see below |
| 3 | round 3's "truncation does not blind change detection" held only for the tested shape | RETRACTED, scenario made discriminating |
| 4 | item 42's title, workaround sentence and a stale record paragraph still wide | FIXED at all three |
| - | the two data reasons, and case-sensitive name matching | PASS |

**Meters EXHAUSTED at 4 of 4 and 4 of 4 with findings outstanding, so the
debate PAUSED.** The user was given the size of the remainder and
authorised: fix all three, then a SINGLE round 5 to adjudicate the fixes.
Written down because an unrecorded authorization is indistinguishable from
a decision the session made for itself.

### The round-5 fixes, and what measuring them changed

- The reviewer's remedy for finding 2 could NOT be built as written.
  `ConvertTo-Json` emits no warning when it truncates, measured on 5.1, so
  there is nothing to turn into a finding. Depth is measured directly
  instead - and that check is unreachable on 5.1, because
  `ConvertFrom-Json` throws its own recursion error first, so no
  red-green record is claimed for it.
- Finding 3 was confirmed against this session, not the reviewer. The
  collapse boundary is FOUR nesting levels, measured by tokenising the
  values rather than counting them.
- Two of this session's own instruments were wrong and were caught by
  running them: a fail-watch aimed at a commit that already had the fix,
  and a scenario built one level shallower than the measured boundary.
  Both proved nothing until corrected.

Watched to fail against the pre-fix code: two probe cases with 48 green,
and five drift assertions.

### Round 5 — 2026-08-15, FRESH session, binding CLEAN, verdict DRY: NO

**Dispatched FRESH rather than resumed, and that was a deliberate trade.**
Rounds 1 to 4 ran in one session across 08-12 to 08-14. It was now a new
day, and a refreshed preamble is the condition item 42 describes; a day
boundary is the one cause observed to produce it, and it had already cost
a whole round on 08-14. Rather than spend the single authorised round on a
dispatch likely to be discarded unread, the session gave up the reviewer's
continuity instead. The brief said so, pointed the reviewer at its own
retained replies, and told it to treat the claims as claims rather than as
agreed history.

Brief `diff-brief-r5.md`, canonical sha256 `2d16391ca8b1a663...`. Reply
retained verbatim at `diff-reply-r5.txt`. **One PASS, four FIX, DRY: NO.**

| # | Finding | Disposition |
|---|---|---|
| 1 | the bare-object case went red for the WRONG reason - a pass-2 object failed the disabled-feature policy, so it never demonstrated the false clean it names | FIXED, moved to the baseline |
| 2 | the depth guard FIRES on a value that parses and serialises intact: an off-by-one, reproduced on 5.1, and "unreachable on 5.1" was false | FIXED, threshold is `+ 1`; boundary case added |
| 3 | the nested-array scenario covered round-trip only; round 4 asked for round-trip AND change | FIXED, change scenario added on a measured collapsing shape |
| 4 | item 42's TITLE omitted "non-identical"; the round-5 brief said the dispatch was "known to fail" | FIXED in the title; the brief is a verbatim artifact, so the correction is recorded below rather than rewritten |
| 5 | the two mis-set fail-watches and the 92 correction are candidly recorded; keeping the labelled non-discriminating assertion is appropriate | PASS |

**The reviewer reproduced finding 2 independently, and so did this side
afterwards:** at 99 nested objects the value parses, measures 101,
serialises intact at `-Depth 100`, and the guard raised a CRITICAL finding
against it. A watcher that reports drift on a healthy file is its own
false measurement. Three of round 5's four findings were defects in round
5's own fixes.

**CORRECTION to `diff-brief-r5.md`, recorded here rather than in the
brief.** That brief said resuming across a day boundary was "known to
fail". It was not known: a day boundary is the single OBSERVED cause of a
refreshed preamble, and the refreshed preamble is the binding condition.
The accurate statement is that resuming RISKED REPRODUCING the one
observed failure, which is why the round was dispatched fresh. Briefs and
replies are verbatim artifacts and are never rewritten - this file is the
synthesized standing record, so the correction belongs here.
