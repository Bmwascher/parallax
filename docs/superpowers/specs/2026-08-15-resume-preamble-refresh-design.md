# Design: a resumed round binds across a refreshed client preamble

Backlog item 42, `docs/superpowers/plans/2026-07-27-0150-backlog.md:2849`.
Design settled 2026-08-15 by a user-invoked PANEL (Sol + Fable) in mode
plan. Panel invariant satisfied: Sol is the cross-vendor lane.

Subject revision, round 1 claims section:
`13f3ba53bcfb7ed44b3151f5cbe61a72455dc462ccd4834918c6b633a52fea4b`.

## The defect

`tools/read-codex-round-evidence.ps1:639-687` accepts a user record ahead
of the brief on a resumed round only when that record canonically equals
the session's FIRST user record. On 2026-08-14 a resume carried a
REFRESHED environment preamble - a different date, and the instructions
block absent - so the identity test could not match it, the round was
discarded unread, and its quota was spent for nothing. Record:
`docs/superpowers/plans/rounds/2026-08-11-tool-surface-agy-drift/diff-debate-record.md:85-104`.

The guard was RIGHT to refuse. Its rule is that anything in front of the
brief must be text this client already emitted in this session, so novel
text cannot reach the reviewer ahead of the brief. What is wrong is the
rule's WIDTH: the comment at `tools/read-codex-round-evidence.ps1:622-638`
records that this bound was once arithmetic and that the field falsified
it; identity replaced it, and the field has now falsified identity in
turn.

This design does not relax the guard to "any record may precede the
brief". It teaches the guard to RECOGNISE the one thing the client
legitimately emits, by structure and by value, and to keep refusing
everything else.

## What was measured, and when

Swept 2026-08-15 across every rollout under the user's codex session
store (749 files at the first sweep). Two sweeps, both by the driver.

**Sweep 1 - the shape of the environment element.** Every `input_text`
element of a `response_item` / `message` / `role=user` record that carries
an `environment_context` tag falls into exactly two shapes:

- 748 elements: exactly one `environment_context` tag with five direct
  fields - `cwd`, `shell`, `current_date`, `timezone`, `filesystem`.
- 16 elements: the same tag with three - `current_date`, `timezone`,
  `filesystem`. A strict subset of the first.

No matched element carried an unknown field, a duplicate direct field, or
text outside the tag. The common core of both shapes is exactly
`current_date`, `timezone`, `filesystem`.

**Sweep 2 - the composition of the RECORD.** Ran because a claim about
elements is not a claim about records, and the design depends on both.
User records carrying an environment element come in three compositions:

- 454 records: 3 elements, one of them the environment element.
- 196 records: 2 elements, one of them the environment element.
- 122 records: 1 element, the environment element alone.

The observed refresh is the one-element case. A session's FIRST user
record is the two- or three-element case. Three elements is the most
common composition, so any rule that assumes the baseline record holds
exactly two elements is narrower than the store.

A concrete pair to read:
`C:/Users/Brandon/.codex/sessions/2026/08/12/rollout-2026-08-12T02-41-22-019ff4eb-346e-7be2-9af3-520ebc876707.jsonl`,
user records 1 and 3. The same file carries `environment_context` text
inside a `type=compacted` record at line 218; that record is not a
`response_item`, so `Test-RecordIsUserMessage` never sees it and it is out
of scope here.

## The rule

Applies ONLY on `-Resume`, ONLY when the slice carries two user records,
and ONLY to the record ahead of the brief. The at-most-two cap, the
brief-must-be-last rule, the brief hash match
(`tools/read-codex-round-evidence.ps1:698-718`) and the entire `-Fresh`
path are untouched.

**Order of checks - this changes.** Today the extra-record check runs
BEFORE the brief is identified and proved last. On a resumed slice ordered
`[brief, extra]` the tool therefore tests the BRIEF as though it were the
record in front of the brief, and reports "does not repeat the client's
own preamble" when the true fault is that a record follows the brief. Both
panel lanes raised this independently, and it is convergent. The fixed
order is: prove the brief present, unique and last, THEN validate the
record ahead of it. The outcome was always a refusal, so this is a
direction fix, not a permissiveness fix - but this design requires every
refusal to name its true direction, so it is in scope.

**Acceptance.** A record ahead of the brief is accepted when EITHER of the
following holds, and refused otherwise.

1. **Identity (today's rule, kept unchanged).** Its canonical text equals
   the canonical text of the session's first user record.

2. **Recognised refresh (new).** ALL of the following hold.
   - Its canonical text is exactly one `environment_context` envelope with
     nothing before or after it.
   - Every direct field name comes from the closed set `cwd`, `shell`,
     `current_date`, `timezone`, `filesystem`. Names are matched ORDINAL
     and CASE-SENSITIVE. PowerShell's default string comparison is
     case-insensitive, and the current code is immune only because it
     compares SHA-256 hashes; a naive port would accept `<CWD>`.
   - No direct field appears more than once.
   - The three fields of the measured common core - `current_date`,
     `timezone`, `filesystem` - are all present. `cwd` and `shell` are
     optional. Accepting a preamble carrying only `current_date` would be
     accepting a shape never observed.
   - Every present field EXCEPT `current_date` canonically equals the
     same-named field inside the BASELINE envelope.
   - `current_date` satisfies the date rule below.

The refresh record must be envelope-and-nothing-else, while the baseline
record may carry other text around its envelope. That asymmetry is
deliberate and follows sweep 2: the observed refresh is the one-element
case, and a session's first record is the two- or three-element case.
Widening the refresh side to "an envelope somewhere in the record" would
admit exactly the unattributed text this guard exists to refuse.

Every "canonically equals" in this design means the canonicalization the
tool already declares and uses everywhere else - UTF-8 bytes, CRLF folded
to LF, leading and trailing whitespace removed - applied here to a single
field's value rather than to a whole record.

**The baseline envelope.** The session's first user record may hold one,
two or three elements (sweep 2), and `Get-UserText`
(`tools/read-codex-round-evidence.ps1:603-612`) joins them all, so "the
element" must be defined rather than assumed. The baseline is the single
`environment_context` envelope found in that record's joined canonical
text. If there is no envelope, or more than one, the structural path is
UNAVAILABLE and the record is refused. Duplicate direct fields inside the
baseline, or a baseline `current_date` that is not a real date, disable it
the same way.

**The date rule.** `current_date` must parse as a real calendar date under
invariant `yyyy-MM-dd` - `ParseExact`, not a regular expression, because
`^\d{4}-\d{2}-\d{2}$` accepts `2026-02-31`. It must be no earlier than the
baseline's own `current_date` and no later than the binder's local date at
verification. The upper bound stays: the date is the only intentionally
novel value in the record, so without it any future date rides through.
Clock or timezone disagreement between the client and the binder is
therefore a REFUSAL, which is the fail-closed direction; asserting the two
share a clock is an unverified claim and is not made.

**The scan.** A purpose-built cursor, not a general XML parser and not a
global search for field tags. It consumes the envelope from its opening
tag to its closing tag, recognises direct-child field boundaries only,
matches each closing tag to its opening tag, treats a field's nested
contents as an opaque value, and rejects every unconsumed character. A
global search cannot tell a direct field from nested content, and the
`filesystem` value demonstrably contains nested tags -
`<workspace_roots>`, `<permission_profile>`, `<entry>`. The JSON line
scanner at `tools/read-codex-round-evidence.ps1:157-189` is the in-repo
pattern to follow: track structure, then reject anything left over.

**Refusals.** Every refusal keeps the property that an unmade or
unrecognised measurement never reads as clean, and each names its own
direction: brief missing, brief ambiguous, brief not last, envelope
unrecognised, baseline unavailable, unknown field, duplicate field,
missing core field, value mismatch, invalid date, date earlier than the
baseline, date later than today.

## What this does NOT claim

- It does not establish what triggers a refresh. A day boundary is the one
  cause OBSERVED, once. Whether a changed cwd, permission profile or
  client upgrade also refreshes the preamble is UNMEASURED, and a resume
  that refreshes nothing still binds by the identity path.
- It does not widen the evidence class. This remains a client-echo
  binding: it proves what the measured client recorded for this call,
  never what the server or model received.

## Scope of change, in order

Tests change before the tool - the contract is live-verified and locked.

1. `evals/multi-model-verify/test_codex_round_evidence.py`. New cases:
   the three-field refresh ACCEPTED; unknown field, duplicate field,
   case-variant field name, missing core field, value mismatch, invalid
   date, date earlier than the baseline, date later than today, text
   outside the envelope, nested delimiter-shaped value content, baseline
   with no envelope, baseline with two envelopes - all REFUSED; and the
   resumed `[brief, extra]` ordering case, which today reports the wrong
   direction and has no coverage (the only ordering case,
   `test_codex_round_evidence.py:391-406`, is `-Fresh` only). The existing
   `preamble_row()` fixture at `test_codex_round_evidence.py:104-115` is a
   one-line placeholder, so the structural cases need a realistic helper
   built from the measured shapes.
2. `tools/read-codex-round-evidence.ps1` - the reorder, the baseline
   selection, the cursor, the field and date rules, the refusal messages.
3. `skills/multi-model-verify/references/model-prompting-notes.md`,
   contract region `codex-brief-binding-record` at lines 475-521. More
   than the one identity sentence goes stale: the rationale at
   `model-prompting-notes.md:490-493` ("the identity rule is what the
   measurement supports") becomes false the moment the structural path
   ships and is rewritten with the 2026-08-14 falsification.
4. `evals/multi-model-verify/test_multi_model_verify.py:335-349`, where
   that contract text is pinned - the resumed-identity sentence is pinned
   at `:341-343`.
5. `evals/multi-model-verify/test_contract_coverage.py` ONLY if the region
   id or the declared region set changes. It excludes itself from pin
   collection by design (`test_contract_coverage.py:617-622`), so it is
   never where the pin lives.
6. Item 42's text in the backlog, last.

## Panel record

- **Sol** (`gpt-5.6-sol`, codex lane), round 1, fresh, effective route
  confirmed, brief binding CLEAN. Voted SHAPE-AND-VALUES and
  FIELD-BY-FIELD. Offered no OPTION-C. Returned seven amendments, all
  verified against the repo by the driver and all accepted.
- **Fable** (`fable-panel-reviewer`, same-harness lane; harness 2.1.233,
  above the 2.1.216 floor), round 1. Voted the same on both questions.
  Verdict FIX on the subject revision above. Agreed with all seven relayed
  findings, judging R7 partly stale because claim 6 had already folded it
  in. Added two of its own: the required common core, and the stale
  rationale sentence in scope item 3.
- **Convergent** (raised independently by both lanes): the check-order
  defect, and the ambiguity of "the element" in the baseline comparison.
  Counted once, fixed once.
- **Driver correction to a supporting detail.** Fable stated that the
  first user record carries TWO content elements, reading one file. Sweep
  2 measured the store: three-element records are the most common
  composition at 454. The conclusion Fable drew from it - that the
  baseline element must be selected rather than assumed - is unaffected
  and is adopted; the supporting count was too narrow and is corrected
  here rather than carried forward.
- **Session verdict.** The design is ready to plan. No point was left
  contested, and nothing was escalated to the user.
