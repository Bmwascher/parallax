# Contract coverage checker — design

Date: 2026-07-27
Backlog item: 1 of 5 (docs/superpowers/plans/2026-07-27-0150-backlog.md)
Target release: 0.15.0

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

Detect under-pinning mechanically. Keep substring pins as the way contract
text is locked. Do not replace the 529 existing assert statements.

Explicitly out of scope: proving a pin is semantically correct, and
locking text that is explanation rather than rule.

## Approach

Mark contract regions in the documents. Require every sentence inside a
marked region to sit whole inside some pin string. Declare the set of
region ids so a region cannot be deleted silently.

Three decisions were taken during design and are recorded here because
each rules out a plausible alternative:

1. **Markers, not whole-file scanning or keyword detection.** Reference
   files carry explanation, probe records, and dates next to the rules,
   so most sentences must not demand a pin. Keyword detection was
   rejected on evidence: instance 10 was `That is a route-attribution
   failure`, which contains no MUST or NEVER, so a modal-word heuristic
   would have missed the case that started this.
2. **Whole-sentence containment, not overlap.** Overlap catches instance
   10 only. Instance 11 had a pin touching the sentence; it just stopped
   early. Requiring containment catches both.
3. **Pins read from the test sources, not a registry.** A registry binds
   regions to pins exactly, but requires rewriting existing pins and
   moves them away from the assertion that uses them. Reading the test
   sources costs nothing in migration.

## Marker format

```
<!-- contract:start id=rotation-guard -->
Before trusting the offset, confirm the stream did not rotate under the
call: if after the call the file is SMALLER than the captured offset, or
absent, it was rotated or replaced.
<!-- contract:end -->
```

HTML comments, so nothing renders. The `id` lets a failure name the
region instead of quoting text back at the reader.

The author decides what sits between the markers. Only text worth pinning
word for word goes inside; rationale, observation dates, and version
notes stay outside. This keeps regions small and dense, and it is what
makes whole-sentence containment affordable.

## The checker

**Inputs.**

- Regions: every `.md` under `skills/multi-model-verify/references/` and
  every `.md` under `agents/`. Both trees are required: the panel harness
  floor is contract text and lives in an agent file.
- Pins: every string constant in every `.py` under
  `evals/multi-model-verify/`, read through Python's `ast`. The parser
  joins implicitly concatenated literals, which is how nearly every pin
  in this repo is written. Verified against the live tree: 172 string
  constants in `test_backup_lane.py`, 40 of them over 60 characters.

**Procedure.**

1. Locate marked regions.
2. Normalize whitespace inside each region, so reflowing a paragraph is
   not a contract change. This matches the existing `_norm` convention.
3. Split each region into sentences.
4. For each sentence, require at least one pin string that contains it in
   full.
5. Report every sentence with no containing pin.

**Sentence rule.** Split at `.`, `?`, or `!` followed by whitespace and
then a capital letter. Skip a fixed abbreviation list: `e.g.`, `i.e.`,
`vs.`, `etc.`, `cf.`. Measured against the live reference set: six `e.g.`
occurrences exist and none is followed by a capital letter, so the rule
mis-splits nothing today.

**Why an imperfect splitter is acceptable.** A wrong split demands a pin
for a fragment, which is a visible red. It cannot produce a silent pass.
The failure direction is safe by construction.

## Region inventory

Coverage alone can be defeated by deleting a whole region: the markers go
with it, the checker finds nothing, and the suite stays green. That is
instance 12 in a new form.

The test declares the region ids it expects. The checker compares the
declared set against the found set.

- Deleting a region: declared id not found, red.
- Adding a region: one line added to the list, deliberate.
- Renaming a region: one deletion plus one addition, both visible.

**Ids are unique across the whole repo, not per file.** One subject can
span two documents and then needs two ids. The panel harness floor is
exactly this case: `references/panels.md:66` states it as
`**Harness floor: Claude Code 2.1.216.**` while
`agents/fable-panel-reviewer.md:23` states it as `has a FLOOR: **Claude
Code 2.1.216**`. Same rule, different wording, two regions, so two ids
such as `panel-floor-reference` and `panel-floor-agent`. A single id
covering both would make the failure message ambiguous about which file
to open.

## Failure behaviour

All of the following are hard failures, never warnings:

| condition | why |
|---|---|
| sentence in a marked region with no containing pin | the defect this exists to catch |
| declared region id not found in any document | a region was deleted or renamed |
| found region id not declared | a region was added without being registered |
| start marker with no end | ambiguous extent |
| nested markers | ambiguous extent |
| empty region | almost certainly an editing mistake |
| duplicate region id | the id is the failure message's only handle |

A coverage failure names the region id, the file, and the exact uncovered
sentence, then states the fix in one line: add a pin containing that
sentence whole. The reader never has to search 529 assertions to find
which one is short.

## Accepted limits

- **Cross-region coverage.** A sentence is covered if any pin anywhere
  contains it, so two regions could in principle be satisfied by each
  other's pins. Sentences are long enough that this requires a real
  coincidence. Accepted knowingly when pin discovery was chosen over a
  registry.
- **Semantic correctness.** The checker proves a sentence is locked, not
  that the sentence is right. That remains the reviewer's job.
- **Unmarked text.** Contract text outside markers is exactly as exposed
  as it is today. The mechanism improves marked regions and worsens
  nothing.

## Testing the checker

The checker is itself a test, so it needs its own proof. Fixtures in a
temporary directory, each a small document plus a small test file:

| fixture | expected |
|---|---|
| region fully covered | passes |
| region with one unpinned sentence | fails, message names that sentence |
| pin stops mid-sentence | fails — instance 11 reproduced deliberately |
| declared region absent from documents | fails — the deletion hole |
| start marker with no end | fails |
| duplicate region id | fails |

**Regression proof against real history.** Before the three regions are
marked, run the checker against the repo as it stood at the commits where
instances 10, 11, and 12 lived. It must go red on each. A mechanism that
cannot catch the failures that motivated it is not worth shipping. This
is a gate on the work, not a nice-to-have.

## Scope for this cycle

Three regions marked, chosen because each has a recorded failure behind
it:

1. The rotation guard in `references/backup-lane.md`.
2. The panel harness floor. Two regions, because the rule is stated
   separately in `references/panels.md` and in
   `agents/fable-panel-reviewer.md`.
3. The failure-class entries in `references/fallbacks.md`.

New contract text gets marked as it is written. No mass edit of existing
files.

**Sequencing note.** Backlog item 5 rewrites the rotation guard paragraph,
because the claim that log rotation fails on Windows was falsified on
2026-07-27. That region is therefore a natural first customer, and item 5
should land either with this work or immediately after it, so the marked
text is the corrected text rather than the false one.

## Deliverables

- `evals/multi-model-verify/test_contract_coverage.py`: the checker, its
  declared region inventory, and its fixture tests.
- Markers added to the three regions above.
- Any pins those regions reveal as short, extended to cover their
  sentences.

No changes to existing assertions beyond extending ones the checker
proves are short.
