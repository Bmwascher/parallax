# Contract coverage checker — design

Date: 2026-07-27
Backlog item: 1 of 6 (docs/superpowers/plans/2026-07-27-0150-backlog.md)
Target release: 0.15.0

**Revision 2**, after a two-lane cross-vendor plan debate. The mechanism
changed as a result: sentence splitting is gone, pins are no longer "any
string constant", and malformed markers are now a hard failure. What
changed and why is in "Revision history" at the end. Read that before
proposing a return to any revision-1 behaviour.

## Problem

Contract text in this plugin is prose executed by a driver, so the tests
lock it with hand-written substring pins. A pin can stay green while the
operative half of the sentence it claims to lock is deleted.

Twelve instances across three consecutive cycles: nine in 0.14.2, two in
0.14.3, one in 0.14.4. Two appeared inside the fix for the previous one.
The three most recent are the design targets:

- **Instance 10.** The sentence `That is a route-attribution failure` had
  no pin at all. Detection and a prohibition were pinned; the consequence
  was not, leaving a driver with no defined action.
- **Instance 11.** A pin existed but stopped mid-sentence at
  `IS transient`, leaving the operative justification loose. Found inside
  the fix for instance 10.
- **Instance 12.** The pinned phrase `Claude Code 2.1.216` occurred twice
  in the same file, so deleting the whole paragraph left the pin green
  via the surviving occurrence.

The common factor is not that any pin was wrong. It is that a pin covered
less than it appeared to, and nothing measured the gap.

## Goal

Detect under-pinning mechanically. Keep substring pins as the way
contract text is locked. Do not replace the 633 existing assert
statements in `evals/**/test_*.py`.

Explicitly out of scope: proving a pin is semantically correct, and
locking text that is explanation rather than rule.

## Approach

Mark contract regions in the documents. Require each region to sit WHOLE
inside a single pin string. Declare the set of region ids so a region
cannot be deleted silently.

**One region, one pin.** There is no sentence splitting and no attempt to
infer English sentence boundaries. The region is the unit of coverage,
and the author sizes it to be pinnable by one string. A region too long
for one pin is two regions. This is the central change from revision 1,
and it removes a whole bug class rather than patching it.

Four decisions, each recorded because it rules out a plausible
alternative:

1. **Markers, not whole-file scanning or keyword detection.** Reference
   files carry explanation, probe records, and dates next to the rules,
   so most sentences must not demand a pin. Keyword detection was
   rejected on evidence: instance 10 was `That is a route-attribution
   failure`, which contains no MUST or NEVER, so a modal-word heuristic
   would have missed the case that started this.
2. **Whole-region containment, not overlap and not per-sentence.**
   Overlap catches instance 10 only; instance 11 had a pin touching the
   sentence that stopped early. Per-sentence coverage was the revision-1
   design and is refuted below.
3. **A pin is a string inside an `assert` statement, not any string in
   the file.** A string that participates in no assertion locks nothing.
4. **Pins come from the test sources, not a registry.** A registry binds
   regions to pins exactly, but requires rewriting existing pins and
   moves them away from the assertion that uses them.

## Marker format

```
<!-- contract:start id=rotation-guard-detection -->
Before trusting the offset, confirm the stream did not rotate under the
call: if after the call the file is SMALLER than the captured offset, or
absent, it was rotated or replaced.
<!-- contract:end -->
```

HTML comments, so nothing renders. The `id` lets a failure name the
region instead of quoting text back at the reader. Ids are lowercase
letters, digits, and hyphens, and unique across the whole repo.

The author decides what sits between the markers. Only text worth pinning
word for word goes inside; rationale, observation dates, and version
notes stay outside. This keeps regions small, which is what makes
one-region-one-pin affordable.

**Any comment containing `contract:` that does not exactly match the
start or end syntax is a hard failure.** Without this rule a typo such as
`<!-- contract:end id=x -->` matches neither pattern, both markers are
ignored, and the region silently ceases to exist. Silence is the one
outcome this design may never produce.

## The checker

**Inputs.**

- Regions: every `.md` under `skills/multi-model-verify/references/` and
  every `.md` under `agents/`. Both trees are required: the panel harness
  floor is contract text and lives in an agent file.
- Pins: every string constant appearing syntactically inside an `assert`
  statement, in every `.py` under `evals/multi-model-verify/`, read
  through Python's `ast`. The parser joins implicitly concatenated
  literals, which is how nearly every pin in this repo is written.

**Procedure.**

1. Locate marked regions; reject malformed marker comments.
2. Normalize whitespace inside each region, so reflowing a paragraph is
   not a contract change. This matches the existing `_norm` convention.
3. Require at least one pin string that contains the whole region body.
4. Report every region with no containing pin.

## Region inventory

Coverage alone can be defeated by deleting a whole region: the markers go
with it, the checker finds nothing, and the suite stays green. That is
instance 12 in a new form.

The test declares the region ids it expects. The checker compares the
declared set against the found set, in both directions.

- Deleting a region: declared id not found, red.
- Adding a region: one line added to the list, deliberate.
- Renaming a region: one deletion plus one addition, both visible.

**Ids are unique across the whole repo, not per file.** One subject can
span two documents and then needs two ids. The panel harness floor is
exactly this case: `references/panels.md` states it as
`**Harness floor: Claude Code 2.1.216.**` while
`agents/fable-panel-reviewer.md` states it as `has a FLOOR: **Claude
Code 2.1.216**`. Same rule, different wording, two regions, two ids. A
single id covering both would make the failure message ambiguous about
which file to open.

## Failure behaviour

All of the following are hard failures, never warnings:

| condition | why |
|---|---|
| a marked region contained by no pin | the defect this exists to catch |
| a `contract:` comment that is neither valid start nor valid end | otherwise the region vanishes silently |
| declared region id not found in any document | a region was deleted or renamed |
| found region id not declared | a region was added without being registered |
| start marker with no end | ambiguous extent |
| nested markers | ambiguous extent |
| empty region | almost certainly an editing mistake |
| duplicate region id | the id is the failure message's only handle |

A coverage failure names the region id, the file, and the region body,
then states the fix in one line: add a pin containing that region whole.
The reader never has to search 633 assertions to find which one is short.

## Accepted limits

- **A pin must appear syntactically inside its `assert`.** A string bound
  to a variable and asserted through that name is not collected. One such
  pin exists today, in `test_seat_reshuffle.py`. The failure direction is
  safe: an uncollected pin makes its region read as uncovered, which is a
  red, and the author inlines the string. It can never manufacture
  coverage. Following name bindings was considered and rejected as
  machinery with no failure behind it.
- **Cross-region coverage.** A region is covered if any pin anywhere
  contains it, so two regions could in principle be satisfied by each
  other's pins. Regions are long enough that this requires a real
  coincidence. Accepted knowingly when pin discovery was chosen over a
  registry.
- **Semantic correctness.** The checker proves a region is locked, not
  that the region is right. That remains the reviewer's job.
- **Unmarked text.** Contract text outside markers is exactly as exposed
  as it is today. The mechanism improves marked regions and worsens
  nothing.
- **No weakening valve, deliberately.** As regions accumulate, keeping
  pins in sync costs effort. There is no mechanism to soften a failing
  check, because this repo's demonstrated failure mode is weakening a
  perpetually-red test. If the cost becomes real, that is a debate to
  have on the record, not a valve to build in advance.

## Testing the checker

The checker is itself a test, so it needs its own proof. Fixtures in a
temporary directory, each a small document plus a small test file:

| fixture | expected |
|---|---|
| region contained by one pin | passes |
| region contained by no pin | fails, message names the region |
| pin stops mid-region | fails — instance 11 reproduced deliberately |
| two pins that jointly span the region but neither contains it | fails — the revision-1 silent pass, kept as a regression test |
| region text present only in a docstring, in no assert | fails — a string that locks nothing is not a pin |
| declared region absent from documents | fails — the deletion hole |
| `contract:` comment with invalid syntax | fails — the vanishing-region hole |
| start marker with no end | fails |
| duplicate region id | fails |

**Regression proof against real history.** Before the regions are marked,
run the checker against the repo as it stood at the commits where
instances 10, 11, and 12 lived. It must go red on each. A mechanism that
cannot catch the failures that motivated it is not worth shipping. This
is a gate on the work, not a nice-to-have.

## Scope for this cycle

**Nine marked regions across three subject areas.** Each area is chosen
because it has a recorded failure behind it. Nine regions rather than
three because one region is one pin, so a subject stating three rules
becomes three regions.

1. The rotation guard in `references/backup-lane.md`: detection,
   disposition, residual gap.
2. The panel harness floor: one region in `references/panels.md`, one in
   `agents/fable-panel-reviewer.md`.
3. The panel lane classes in `references/fallbacks.md`: the
   `panel-lane-loss` disposition, and the three sentences that state what
   `panel-lane-unavailable` does — its shared principle, its procedure,
   and its invariant. Four regions.

New contract text gets marked as it is written. No mass edit of existing
files.

**Sequencing note.** Backlog item 5 rewrites the rotation guard paragraph,
because the claim that log rotation fails on Windows was falsified on
2026-07-27. That region is therefore a natural first customer, and item 5
should land either with this work or immediately after it, so the marked
text is the corrected text rather than the false one.

## Deliverables

- `evals/multi-model-verify/contract_coverage.py`: the checker.
- `evals/multi-model-verify/test_contract_coverage.py`: the declared
  region inventory, the live repo check, and the fixture tests.
- Markers added to the nine regions above.
- Any pins those regions reveal as short, extended to cover them.

No changes to existing assertions beyond extending ones the checker
proves are short.

## Revision history

**Revision 1** proposed per-sentence coverage: split each region into
sentences with a regex, and require every sentence to sit inside some
pin. It collected every string constant in the test files as a pin, and
matched marker comments with a search rather than a full match.

Two lanes reviewed it. The first reached PASS over two rounds. The second
had a shell, ran the checks, and refuted three claims. All three were
reproduced independently before this revision was written:

1. **"Every string constant is a pin" is unsound.** 47 of 172 string
   constants in `test_backup_lane.py` appear in no assertion. Module and
   helper docstrings would therefore have counted as pins, so a region
   could read as locked by a docstring that locks nothing. Fixed by
   collecting only strings inside `assert` statements.
2. **"A wrong split cannot produce a silent pass" is false.**
   Counterexample: `Use U.S. Servers only.` splits into `Use U.S.` and
   `Servers only.`, and two fragment pins cover both halves while no pin
   contains the sentence, so coverage passes. This mattered because the
   repo's existing pins ARE fragments, making the failure mode live
   rather than hypothetical. Fixed by dropping sentence splitting
   entirely.
3. **Malformed markers vanish silently.**
   `<!-- contract:end id=Bad_ID -->` matched neither pattern, so both
   markers were ignored and the region ceased to exist with no error,
   contradicting this design's own rule that marker problems are hard
   failures. Fixed by rejecting any `contract:` comment that does not
   exactly match.

Two documentation errors were corrected in the same pass: a task
predicted two failing tests where one passes vacuously with zero regions,
and this document said "three regions" where the inventory holds nine
ids.

The difference between the two lanes was not judgement. It was that one
of them ran the code.
