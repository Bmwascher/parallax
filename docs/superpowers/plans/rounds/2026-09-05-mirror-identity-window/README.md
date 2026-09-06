# Debate record: the mirror identity window

Plan: `docs/superpowers/plans/2026-09-05-mirror-identity-window.md`
Spec: `docs/superpowers/specs/2026-09-05-mirror-identity-window-design.md`

Mode: plan. Lane: codex, GPT-6 Astra at `high`.
Fix-verify budget declared before round 1: 4 dispatched exchanges.

## Astra R1 - VOIDED

Dispatched 2026-09-05 against subject `c723066`, mirror `C:\Temp\pxr1`.

The wrapper classified `workdir-mismatch` and exited 1. The cause was the
driver's own argument: `-WorkdirEvidence` was passed as `C:/Temp/pxr1`
with forward slashes, and the codex transcript header records
`workdir: C:\Temp\pxr1` with backslashes. The classifier compares those
strings literally, so it refused.

**The round is not evidence and this is not a debate round.** The
dispatch contract is that the wrapper's exit code IS the classification,
and `0` is the only value that means `reply-present`. The reply is
retained here as INPUT, on the precedent of item 87's voided Astra R1,
and it was used to amend the plan and the design before a fresh round.
It counts as one unit of the fix-verify budget, because a unit is one
dispatched exchange whatever it returns.

The effective route WAS confirmed in the transcript header before the
classification failed: `model: gpt-6-astra`, `provider: openai`,
`sandbox: read-only`, `reasoning effort: high`, session id
`01a073d8-8ced-7fd0-aefb-02867c5fad74`. Both wrapper identity checks
passed, so the mirror did not move during the round. None of that makes
the round countable; it is recorded because a later reader will ask.

Artifacts:
- `brief-r1-voided.md` - the brief as sent
- `astra-r1-voided-reply.md` - the reply, input only
- `astra-r1-voided-transcript.txt` - the client transcript

### What the voided reply changed, before any countable round

Accepted and applied to the plan and the design:

1. "Fusing build and prepare is not constructible" was WRONG. The fusion
   is constructible; it simply does not close the round-length window.
   The design now says that.
2. The sidecar's destination had NO guards. A hard link or symbolic link
   at the derived path would carry the write to its target, and an
   explicitly supplied `-OverrideOut <MirrorPath>.source-manifest` would
   be silently overwritten, breaking the wrapper's override hash. The
   sidecar now takes the override's whole guard set plus create-new
   semantics.
3. A root-shaped mirror path such as `D:\` derived the drive-relative
   `D:.source-manifest` rather than a sibling. Now refused.
4. PowerShell hashtables compare keys case-insensitively, so a case-only
   rename would have reported no drift while the digest changed. Now
   ordinal dictionaries.
5. `appeared` and `vanished` overstated what manifest membership means.
   Now `entered manifest coverage` and `left manifest coverage`.
6. "No content difference, so the status listing itself changed" was an
   unsupported inference: a replaced sidecar produces the same result.
   Now says the manifest did not identify the cause.
7. Malformed records were silently dropped. Now counted and reported.
8. "Returns no value a caller could branch on" misstated PowerShell:
   `Write-Output` emits into the pipeline. The real protection is that
   the caller ignores it and exits unconditionally.
9. "Never throws" covered only the read. The whole body is now wrapped.
10. The quiet-period contract text claimed every trip spends quota. Only
    the post-client check does. It now states that and its two
    measurement limits.
11. Unbounded read and unescaped names in the printed explanation. Now
    bounded, with control characters rendered.
12. The reference told the operator to rebuild without reading the
    explanation first, and gave no route to `mirror.verify` for the
    wrapper's own refusals. Both fixed.

Pre-existing findings outside this plan's range are recorded as backlog
follow-ups rather than fixed here, per the debate protocol's scope rule.

## Astra R1 - COUNTED, verdict FIX

Dispatched 2026-09-05 against subject `0361a67`, mirror `C:\\Temp\\pxr2`.
Wrapper exit 0, classification `reply-present`.

Route confirmed: `model: gpt-6-astra`, `provider: openai`,
`sandbox: read-only`, `reasoning effort: high`, session id
`01a073e9-9f4f-78e2-8fa4-2dc33bb36c63`. Round evidence bound with
`read-codex-round-evidence.ps1 -Fresh`: `status: clean`,
`sealed: sealed`, prior state `3645f50e...` matching the receipt.

Artifacts: `brief-r1.md`, `astra-r1-reply.md`, `astra-r1-transcript.txt`.

**Reviewer verdict: FIX.** PASS on claims 1, 5, 7, 8, 9, 11 and 12. FIX
on 2, 3, 4, 6, 10 and 13, plus seven class-sweep items and seven
other-form items. Nothing was contested; the session accepted every
finding after verifying the two empirical ones itself.

### Session verification of the two empirical claims

- **Root detection.** Ran the proposed helper's condition on PowerShell 7:
  `Split-Path 'C:\' -Leaf` returns `C:\`, which does not match
  `^[A-Za-z]:$`, so the guard never fired; and
  `Split-Path '\\server\share\' -Leaf` returns `share` with parent
  `\\server`. Confirmed. The helper now uses
  `[System.IO.Path]::GetPathRoot` and appends rather than rejoins.
- **The alias guards.** Read `tools/new-review-mirror.ps1:1258-1290`.
  There is a second guard block that walks each path's ancestors for a
  reparse point and checks every followed link target, covering the
  mirror path and the override path and NOT the sidecar. The draft's
  claim to carry "the override's whole guard set" was false, and its
  `-Force` removal sat above this block, so a build headed for refusal
  would already have deleted a file. Confirmed. Removal moved after all
  validation, and the sidecar added to both loops.

### Accepted and applied

Claims 2, 3, 4, 6, 10 and 13 in full. The class sweep's stale interface
block, the Global Constraints contradiction with the new exit 2 refusals,
the backlog quota overstatement, the "content of every path" wording, and
the test selectors. The other-form list's extra-input collision, dangling
reparse point detection by attributes rather than `Test-Path`, the
unbounded split, the non-terminating `Get-Item`, the C1 and bidirectional
rendering gap, and the host-dependent root cases.

Two were accepted as WORDING rather than mechanism, and the plan says so
where it matters: create-new bounds the final path component only, and
the advisory reader does not resolve a file link. Both are now stated
limits instead of implied guarantees.

Budget after this round: 2 of 4 dispatched exchanges used.

## Astra R2 - VOIDED by a concurrent writer

Dispatched 2026-09-05 against subject `557e1e1`, mirror `C:\\Temp\\pxr2`,
resuming session `01a073e9`. The wrapper's FIRST identity check passed
(`identity: verified`) and its SECOND, after the client finished, refused
with `the source status changed since construction`. Wrapper exit 1.

**Cause, found by hand.** Two TRACKED files were modified while the round
ran: `CLAUDE.md` and `skills/multi-model-verify/SKILL.md`. The session
driving this debate did not touch either. Two other parallax sessions
were live at the time (`parallax-6a` and `parallax-1b`), and one of them
is rewriting the skill: the working-tree diff adds a "Controller host
gate" section about Codex-to-Codex being same-vendor, and trims the
description and overview.

Those changes are ANOTHER SESSION'S IN-FLIGHT WORK. They were left
exactly as found: not staged, not reverted, not committed here.

**This is the defect the plan documents, reproducing during the debate
about it.** Finding the cause took a manual mtime sweep across the
ignored and dirty set, which is precisely the work Task 2 exists to
remove. Had the sidecar shipped, the refusal would have printed
`content changed (2): CLAUDE.md, skills/multi-model-verify/SKILL.md`.

It is also a case the quiet-period rule as drafted does NOT cover. That
rule addresses one session's own writes. It says nothing about a SECOND
session writing to the same repository, which no ordering discipline
available to this session can prevent. Recorded here rather than fixed;
it belongs to backlog item 94's open question.

Artifacts: `brief-r2-voided.md`, `astra-r2-voided-reply.md`,
`astra-r2-voided-mirror-verify.txt`.

**The reply is retained as INPUT.** It reports PASS on claims 2, 3 and
13, on class-sweep items 1, 4 and 5, and on other-form items 2 and 3,
with a residual FIX list covering the unrestricted split, empty-record
handling, the extra-input collision binding, root failure reporting, the
renderer's category naming, two paragraphs still saying "every path",
and the Task 2 test selector. None of it is evidence and none of it has
been applied.

Budget: 3 of 4 dispatched exchanges used. PAUSED at the user's direction
until the other sessions are finished with the repository.

### The voided R2 reply's residual findings, applied 2026-09-05

Applied while the debate is PAUSED, so the confirming round has less to
catch. None of this is evidence: the reply that prompted it was voided,
and these amendments are unreviewed until a counted round says otherwise.

The reply reported PASS on claims 2, 3 and 13, on class-sweep items 1, 4
and 5, and on other-form items 2 and 3. Its section B accepted both
wording-only dispositions from R1 as correct within their stated limits.
What follows is its residual FIX list, all accepted:

1. **The record cap invented malformed records.** At record 200,001 the
   parser incremented the malformed counter once and abandoned the rest,
   so 200,003 malformed records reported 200,001 and a resource limit
   read as a grammar diagnosis. Truncation is now the reader's own
   state, reported separately as "the remainder was NOT examined".
2. **The cap applied after the split.** `-split` materialized every line
   before any bound could matter. A new `Read-BoundedRecords` uses a
   `StringReader` and stops AT the cap.
3. **Empty records were dropped.** The parser skipped every empty string
   as "the trailing split artifact", losing leading and interior empty
   records with it. `ReadLine` returns nothing for a file ending in a
   newline, so the artifact does not exist and every empty line is now
   counted as malformed. The condition was removed rather than refined.
4. **The root helper called resolution failures roots.** Both catch
   blocks returned the same null as a genuine root. It now returns
   `ok`, `root` or `error`, and both callers report the difference.
   Windows PowerShell 5.1 refused a 278-character path from
   `GetFullPath` that PowerShell 7 accepted, so this was reachable.
5. **The extra-input guard compared spelling only.** An extra input
   reached through a junction can name the sidecar while comparing
   unequal, after which `-Force` removes it. Such a path is now refused
   outright, because physical identity cannot be established here.
6. **The extra-input fragment used variables that do not exist.** The
   real resolver uses `$eiPath` and stores resolved paths in
   `$ExtraInputPaths`. The plan now carries the actual loop, at a place
   where `$smp` and `Test-PathOrAncestorIsLink` both exist.
7. **The root test had the wrong oracle and never reached the helper.**
   The containment guard refuses first with a different message. There
   are now direct unit tests that extract the function from the shipped
   file and run it, plus an integration test whose assertion matches
   what actually fires.
8. **The renderer interface promised more than it escapes.** "Every
   separator character" includes `SpaceSeparator`, which is not escaped;
   U+00A0 passes through. The interface now names the five categories.
9. **Two paragraphs still said "every path".** The backlog entry and the
   design's measured-facts list now carry the deletion-only
   qualification.
10. **Both test selectors matched on substrings** and missed cases that
    had been written. Both now name every test and state the expected
    collected count.

The design's success criteria also dropped a universal "proven by test"
claim for a statement of what the two cases actually establish.

## Astra R3 - DISCARDED UNREAD (brief-attribution)

Dispatched 2026-09-05 against subject `374571c`, mirror `C:\\Temp\\pxr3`,
resuming session `01a073e9`. The wrapper classified `reply-present` and
exited 0, and BOTH identity checks passed (`mirror.verify` holds
`identity: verified` twice).

The ROUND-EVIDENCE BINDER refused:

    a resumed slice carries a user record in front of the brief that
    neither repeats the client's own preamble from this session nor
    reads as a refreshed one: it is not a recognised client environment
    preamble

Cause: the mirror was rebuilt at a NEW path. Rounds 1 and 2 ran against
`C:\\Temp\\pxr2`; this round resumed the same session against
`C:\\Temp\\pxr3`. SKILL.md:290-293 states the rule exactly - a resumed
round needs the mirror at the path its identity was recorded at, a mirror
at a new path makes the binder refuse the resumed slice, and the remedy
is to rebuild at the SAME path with `-Force` or to dispatch FRESH rather
than resume. The driver did neither. Session error, documented in the
very skill under review.

**THE REPLY IS DISCARDED UNREAD, and this is not the same as a void.**
A binder verdict other than clean is class `brief-attribution`
(fallbacks.md), and that class discards the reply unread. The earlier
voided rounds still PROVED the brief-to-reply binding, so their content
was usable as input and was used. Here the binding is exactly what could
not be proved, so the content is worth nothing. `astra-r3-discarded-reply`
is deliberately NOT retained in this directory; the brief and the
transcript are, because they are evidence about the dispatch rather than
about the review.

**A prediction this session got wrong, recorded because the reasoning
matters.** Before the round finished, the session predicted it would void
because two pytest runs wrote `.pytest_cache` inside the repo while the
reviewer read. Both identity checks passed instead. The prediction
reasoned from MODIFICATION TIME; the digest hashes CONTENT. Both suites
rewrote the cache with byte-identical content, so the digest never moved.
The quiet-period rule is still correct as written - a content change
there would have voided the round - but "a file was touched" and "the
digest moved" are different claims and this session conflated them.

**The quiet-period rule has a gap this exposed, in the other direction.**
The session read "nothing may write inside the reviewed repository" as
"do not edit files" and then started a 21-minute background gate that
writes. Backgrounded work in the repo is exactly what the rule must
forbid, and no draft sent to the reviewer contained the gap in that form,
so no round could have caught it.

Budget: 4 of 4 dispatched exchanges used. ONE counted round (R1, FIX,
fully applied). Two voided with usable input, both applied. One discarded
unread.

## Astra R4 - COUNTED, verdict FIX with one ESCALATE

Dispatched 2026-09-05 against subject `048c0c1`, mirror `C:\Temp\pxr4`,
FRESH rather than resumed. Wrapper exit 0, classification
`reply-present`. Route confirmed: `gpt-6-astra`, `openai`, `read-only`,
`high`, session `01a0746f`. Binder `-Fresh`: `status: clean`,
`sealed: sealed`.

Fresh was chosen deliberately after R3 died on preamble continuity: a
fresh session needs no preamble to match, so a new mirror path is
harmless. The cost is the reviewer's accumulated context, which the brief
carried instead by pointing at this record.

Artifacts: `brief-r4.md`, `astra-r4-reply.md`, `astra-r4-transcript.txt`.

**PASS on claims 2, 5, 6 and 8**, and on the `StringReader`, `GetPathRoot`,
dictionary and `Split-Path` halves of the host sweep. The reviewer ran
extracted-function probes on BOTH hosts rather than reading only.

**FIX on claims 1, 3, 4 and 7 plus six class-sweep items.** All applied.
Three were verified by this session first:

- `BACKLOG.md.` passes `Test-Path`, resolves WITH the trailing dot,
  hashes identical to `BACKLOG.md`, and compares unequal by spelling.
  Confirmed here. An extra input spelled `<mirror>.source-manifest.`
  would have passed the collision guard and still named the file `-Force`
  removes.
- `skill_lint.py:340` reads `est_tokens > BODY_TOKEN_CEILING`, so 6500
  exactly is a warning and not an error. The plan said "at or above".
- Task 4 still cited `SKILL.md's mirror-quiet-period` after Task 3 moved
  the region to `preflight-mirror.md`, and wrote the id in backticks,
  which the citation checker's required `<file>.md's <id>` spelling
  rejects.

The rest, applied on the reviewer's evidence: the bounded reader
allocated one record PAST its cap because `ReadLine` ran before the count
check, measured with a million-character line that was built and
discarded; `Format-AdvisoryName` bounded its INPUT at 200 and then
expanded escapes, returning 1,211 characters for a control-heavy name;
item 97's guard asked `bool(old)`, a question about ITEMS, so a backlog
that parsed cleanly and held none could not attest its first item; the
two junction tests placed the MIRROR under the junction, where the
existing mirror-path guard refuses first, so neither could detect the
sidecar guard's omission; the resolution-failure test's oracle accepted
`ok` and passed without exercising the error branch; and item 97 claimed
resistance to fabricated work that its own linter documents it does not
have.

**A measured host difference, now closed.** Windows PowerShell 5.1
classifies U+08E2, U+0890 and U+0891 as `OtherNotAssigned`; PowerShell 7
classifies them as `Format`. A renderer keyed on `Format` alone escapes
them on one host and not the other. `OtherNotAssigned` and `PrivateUse`
joined the escape set so the two agree for that class, and the interface
now states that identical rendering is claimed only for the listed
categories rather than for every input.

**ESCALATED, then MEASURED 2026-09-05 and closed.** Whether
`[System.IO.File]::GetAttributes` behaves the same on both hosts for a
DANGLING reparse point. Task 1 Step 5c reads attributes rather than
calling `Test-Path` precisely because the link walker documents
`Test-Path` as unreliable there, so the replacement's own cross-host
behaviour matters and neither side measured it. It is the one place where
a wrong "it is not there" becomes a write.

The probe created a junction, deleted its target, and read four cases
under each host: an intact junction, the dangling junction, a plainly
missing path, and an ordinary file. Windows PowerShell 5.1 and
PowerShell 7 returned identical results on all four:

| case | `Test-Path` | `GetAttributes` |
| --- | --- | --- |
| intact junction | True | `Directory, ReparsePoint` |
| DANGLING junction | True | `Directory, ReparsePoint` |
| plain missing path | False | throws |
| ordinary file | True | `Archive` |

So the cross-host risk does not exist for a junction, and Step 5c's
`FileNotFoundException` / `DirectoryNotFoundException` handling is the
only branch a dangling junction never takes. Two limits, stated rather
than papered over. The link walker's premise - that `Test-Path` "may
report as absent" for a dangling reparse point - was NOT reproduced here;
it returned True on both hosts, so that comment's justification is
unmeasured even though its choice is still right. And a dangling FILE
SYMLINK was not measured, so nothing above claims anything about one.
The shipped walker's comment is left as it stands; correcting it is not
in this plan's scope.

Budget: 5 dispatched exchanges. Two counted rounds, both FIX, both fully
applied.
