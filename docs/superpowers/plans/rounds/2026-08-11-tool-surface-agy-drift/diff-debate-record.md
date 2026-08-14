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
Filed as backlog item 42, priority HIGH, because it blocks the repo's own
review process on any debate that spans midnight.

**Meters are UNCHANGED at 1 of 4 and 1 of 4.** A transport failure is not
an exchange. Nothing was adjudicated, contested, or conceded, because
nothing was read.

### Round 2, RETRY — 2026-08-14, same session and same day, binding CLEAN

Dispatched again on the user's decision, after the options and their costs
were put to them. Brief `diff-brief-r2.md` with one paragraph added
telling the reviewer its earlier answer was never read and must not be
referred back to. Canonical sha256 `629f3a81a89e5787...`. Reply retained
verbatim at `diff-reply-r2.txt`.

**This retry also MEASURED what item 42 records as unknown.** With the
environment context already refreshed inside the session, the same-day
resume carried the brief ALONE - one user record, no preamble - and bound
clean. Item 42 stands unchanged: that is a workaround available only while
a debate stays inside one day, not a fix.

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
