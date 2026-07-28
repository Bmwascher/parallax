# Contract coverage checker — design

Date: 2026-07-27
Backlog item: 1 of 6 (docs/superpowers/plans/2026-07-27-0150-backlog.md)
Target release: 0.15.0

**Revision 7**, after six rounds of cross-vendor plan debate across two
reviewer lanes, which found twenty-one defects between them. The mechanism
changed three times: sentence splitting is gone, pin collection is a
clause-matching rule rather than a tree walk, and marker rejection now
runs over the whole document text. What changed and why is in "Revision
history" at the end. Read it before proposing a return to any earlier
behaviour.

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
3. **A pin is a string literal in a positive-presence assertion, not any
   string in the file and not any string inside an `assert`.** A string
   that participates in no assertion locks nothing; neither does an
   assertion's failure message, nor an assertion that text is ABSENT.
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

**A marker owns its line, and any line whose comment keyword is
`contract:` that does not exactly match the start or end syntax is a hard
failure.** Without this rule a typo such as `<!-- contract:end id=x -->`
matches neither pattern, both markers are ignored, and the region
silently ceases to exist. Silence is the one outcome this design may
never produce. Detection therefore does not wait for a closing `-->`,
because an unterminated marker would otherwise be invisible too.

Detection also runs over the WHOLE document text before the line-by-line
scan, not only over lines. An HTML comment may legally span lines, and
`<!--` on one line with `contract:start id=demo -->` on the next matches
no single line at all, so a line scan alone lets that region vanish
without a word.

The keyword is anchored to the start of the comment. `agents/` already
carries a different marker family — the 0.12.0 `shared-contract:start` /
`shared-contract:end` parity mechanism in `implementer.md` and
`flash-implementer.md` — and both files sit inside the tree this checker
scans. An unanchored rule would call every one of them malformed and the
checker could never run.

## The checker

**Inputs.**

- Regions: every `.md` under `skills/multi-model-verify/references/` and
  every `.md` under `agents/`. Both trees are required: the panel harness
  floor is contract text and lives in an agent file.
- Pins: every string literal that a POSITIVE-PRESENCE assertion checks
  against a document, in every `.py` under `evals/multi-model-verify/`,
  read through Python's `ast`. The parser joins implicitly concatenated
  literals, which is how nearly every pin in this repo is written.

  **The rule matches a COMPLETE assertion clause, and never descends into
  an expression it does not recognize.** This is the part that took three
  attempts to get right. Recognizing a shape anywhere in the tree lets an
  enclosing expression flip its meaning: `assert ("lit" in body) == False`
  and `assert flag or "lit" in body` both contain a positive membership
  test that the assertion as a whole does not require. The second shape
  is live, at `evals/multi-model-verify/test_flash_implementer.py:58`.

  Three clause forms, and only these three:

  | clause | pins |
  |---|---|
  | `"literal" in body` | the left operand |
  | `body.count("literal")`, alone or compared `== n`, `>= n` (n ≥ 1) or `> n` (n ≥ 0) | the call's single argument |
  | `<clause> and <clause>` | the union |

  **The needle must be a plain string literal, not an expression
  containing one, and a `.count` call takes exactly one such argument.**
  Adjacent literals fold into one constant at parse time, so nearly every
  existing pin qualifies. A conditional does not: `assert ("x" if flag
  else "y") in body` requires only the selected branch, and collecting
  every constant beneath the operand would pin the other one too.

  This costs five real fragment locks, and the cost is worth stating
  exactly. All five come from runtime-constructed needles such as
  `"--model " + CANONICAL_ID`, whose assertions genuinely do require the
  fragment to be present. They are dropped deliberately. The accurate
  claim is that the rule costs no CURRENT MARKED COVERAGE, not that it
  costs nothing.

  Everything else contributes nothing: a failure message, `not`,
  `not in`, `or`, `==` against anything but a positive count, a bare
  name, a call that is not `.count`. Measured on the live suite, the
  clause rule takes 715 strings down to 366. All nine regions in scope
  keep the coverage they had, and all three history controls stay
  covered.

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

**Every limit below is tagged by DIRECTION, and no total is stated.**
FALSE NEGATIVE means the region reads uncovered — a red, and safe. FALSE
COVERAGE means a region could read as locked when nothing locks it, which
is the defect this checker exists to catch, so those are the ones that
matter.

The tag replaces a count on purpose. The count of false-coverage limits
was written as "one", corrected to "two", and was still wrong: a reviewer
then showed cross-region coverage is a third. A decorative number nobody
re-derives is exactly what this repo has been burned by before, in
`fallbacks.md`'s invented class total. Tag each limit and let the reader
count if they care.

- FALSE NEGATIVE. **Every positive assertion outside the three clause forms is rejected,
  whatever it means.** This is the categorical statement, and it is the
  honest way to put it: the checker does not attempt to understand
  assertions, it recognizes three shapes. Reversed count comparisons
  (`1 == body.count("x")`), chained comparisons, `all(...)`
  comprehensions, walruses, `count(...) != 0`, and a conditional operand
  all lock text and are all dropped. So are the three named below. The
  failure direction is identical in every case — the region reads
  uncovered, which is a red, and the author rewrites the assertion into
  one of the three forms. Listing only a few losses would suggest the
  rest are handled.

  The three worth naming, because each is live:
  - A string bound to a variable and asserted through that name. One such
    pin exists today, in `test_seat_reshuffle.py`. Following name
    bindings was considered and rejected as machinery with no failure
    behind it.
  - A regex lock. `re.search(r"converged with amendments", text)` at
    `test_multi_model_verify.py:318` genuinely locks a phrase in
    `debate-protocol.md`, and is dropped. This is NOT one case: lines
    306, 307, 311, 318 and 325 of that file all lock literal phrases in
    the same document this way, and more do so elsewhere. The loss is
    accepted anyway, because a regex is not a substring: admitting it
    would mean deciding which patterns are literal, which is a much
    larger rule than the one it would serve. An author who wants a
    marked region locked writes a membership assertion instead.
  - A literal compared with `==`.
- FALSE NEGATIVE. **A typo in the comment OPENER makes a marker invisible rather than
  rejected.** The detector tolerates a spaced colon, so
  `<!-- contract : start id=x -->` is now rejected rather than ignored.
  What it cannot see is a broken `<!--`, as in
  `<!--- contract:start id=x -->`. The failure table's promise covers
  comments the detector recognizes as ours; a mistyped opener is not one.
  This is a real limit and the safety argument is PROCESS-dependent
  rather than mechanical: a one-sided typo leaves an unmatched partner
  marker and fails, and a two-sided typo while ADDING a region fails
  against the declared inventory, which this plan's task order always
  populates before any document is touched. A different task order would
  not have that protection.
- FALSE COVERAGE. **Neither clause form can tell whether its container is a document.**
  `ast` sees names and method calls, never types. `paths.count("The rule
  stands.")` over a list registers as a pin, and so does
  `"The rule stands." in some_subprocess_output`. The live suite really
  does assert membership against subprocess output and hook context, not
  only document text. It needs a genuine coincidence: a non-document container asserted to hold a string that
  happens to contain a whole marked region. Every live `.count` receiver
  is a document string, and the wording everywhere else says
  `body.count(...)` and `in body` because that is the intended use.
  Checking a container's type is not possible from the syntax tree, so
  the limit is stated rather than closed.

  The same bullet covers a sibling that is easy to miss: **pins are
  collected from SYNTAX alone, with no awareness of whether the assertion
  ever runs.** An assertion inside a platform-skipped module or behind a
  `pytest.skip` guard still registers as a pin, and locks nothing at
  runtime. This is live structure, not a hypothetical:
  `test_attestation.py` carries a module-level `skipif` for a missing
  PowerShell host, and `test_multi_model_verify.py` has several
  `pytest.skip` guards. It is also FALSE COVERAGE. Neither is live for the nine
  regions in scope — all nine planned pins sit in unconditionally-run
  tests — but the suite's own baseline already reports one skip. Like the
  container limit, this cannot be closed from the syntax tree, so it is
  stated.
- REJECTED, not accepted. **`body.count("x") == 0`.** An earlier
  revision left it in as a limit, reasoning that the false-coverage path
  needed one document to both contain and exclude the same text. That
  reasoning was wrong: pins and regions are pooled repo-wide, so an
  absence assertion about document B can cover identical text in document
  A. The count comparison must therefore be positive.
- FALSE COVERAGE. **Cross-region coverage.** A region is covered if any
  pin anywhere contains it, and `uncovered` never binds a pin to the
  region's own document, so one region can be satisfied by another's pin.
  Regions are long enough that this requires a real coincidence. Accepted
  knowingly when pin discovery was chosen over a registry; a registry is
  the only thing that would close it.
- OUT OF SCOPE. **Semantic correctness.** The checker proves a region is locked, not
  that the region is right. That remains the reviewer's job.
- OUT OF SCOPE. **Unmarked text.** Contract text outside markers is exactly as exposed
  as it is today. The mechanism improves marked regions and worsens
  nothing.
- BY DESIGN. **No weakening valve.** As regions accumulate, keeping
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
| region text present only in an assertion's failure message | fails — the message checks nothing |
| region text present only in a `not in` assertion | fails — that asserts absence |
| region text present only in `("text" in body) == False` | fails — the enclosing expression inverts the clause |
| region text present only in `flag or "text" in body` | fails — the assertion does not require it |
| region text present only in one branch of a conditional operand | fails — only the selected branch is required |
| region text present only in `body.count("text") == 0` | fails — a zero count asserts absence |
| region text present only in an `==` comparison | fails — not one of the three clause forms |
| region text in a `body.count(...)` assertion | passes — the second positive shape |
| declared region absent from documents | fails — the deletion hole |
| `contract:` comment with invalid syntax | fails — the vanishing-region hole |
| `contract:` comment with no closing `-->` | fails — otherwise it is invisible |
| a `contract:` comment split across lines, by any line boundary | fails — a line-by-line scan alone would miss it entirely |
| a marker preceded elsewhere in the file by a stray `<!--` | fails — openers are found directly, so nothing can swallow one |
| `<!-- contract : start id=x -->` with a spaced colon | fails — the opener tolerates the space so the spelling is rejected, not ignored |
| a marker sharing its line with prose | fails — markers own their line |
| a `shared-contract:` comment from the 0.12.0 parity mechanism | ignored — a different marker family, not ours |
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

**Revision 2** fixed those three, and a second review round found three
more in the fixes themselves:

4. **Pin collection walked the whole `ast.Assert`, including its failure
   message.** 194 of 715 collected strings came from `assert x, "msg"`,
   which checks nothing about any document. Re-deriving that surfaced a
   second path the review named but had not counted: 19 strings sit in
   `not in` comparisons, which assert ABSENCE.
5. **Marker detection required a closing `-->`,** so an unterminated
   `<!-- contract:start id=demo` was ignored rather than rejected. The
   same silent-deletion hole in a new shape.
6. **A marker-placement step gave no indentation instruction,** so a
   zero-judgment implementer could put a marker at column zero and end
   the enclosing markdown list item.

A third round, run across BOTH lanes independently, found four more —
and both lanes independently reported the same one:

7. **Restricting to `Assert.test` was not enough, because the collector
   still descended generically.** `assert ("lit" in body) == False` and
   `assert flag or "lit" in body` both contain a positive membership test
   the assertion does not require, and the second shape is live at
   `test_flash_implementer.py:58`. The fix is the clause rule above: no
   generic descent at all.
8. **`body.count("x") == 0` was accepted as a limit on wrong reasoning.**
   Revision 2 argued the false-coverage path needed one document to both
   contain and exclude the text. Pins and regions are pooled repo-wide,
   so an absence assertion about document B covers identical text in
   document A. Now rejected.
9. **A multi-line marker comment vanished.** `<!--` on one line and
   `contract:start id=demo -->` on the next matches no single line, so a
   line-by-line scan missed it entirely. Detection now runs over the
   whole text first.
10. **Task 7 still told future authors that a pin is "a string inside an
    `assert`"** — the definition finding 4 had just refuted, written into
    the standing instruction file. Both lanes found this one, and it is
    the pattern this whole mechanism exists to break: a defect inside the
    fix, in the last-written and least-checked artifact.

**Revision 3** applied those, and a fourth round across both lanes found
four more — again including one inside the fix for the one before:

11. **The clause rule collected every constant beneath an operand.**
    `assert ("x" if flag else "y") in body` requires only the selected
    branch, so the other became a pin the assertion never checks. The
    needle must now be a plain string literal.
12. **Single-line-ness was tested with `"\n" in span`.** `splitlines`
    also breaks on `\r`, `\v`, `\f`, `\x1c`-`\x1e`, `\x85`, ` ` and
    ` `, so a marker split by a bare CR passed the whole-text check
    and was then split into two invisible halves by the line scan.
13. **A stray comment opener could swallow a real marker.** The
    whole-text pass iterated comment SPANS, and `re.finditer` yields
    non-overlapping matches, so a `<!-->` earlier in the file consumed
    forward through a later marker's `-->`. Openers are now found
    directly.
14. **The rewritten CLAUDE.md text was itself wrong** — it named two
    clause forms where the code has three, omitted the count bounds, and
    contradicted itself on `==`. That is the instruction-file defect
    recurring inside its own fix, and both lanes reported it.

The same round corrected the accepted limits: a wrong line citation
copied from a review without checking, a "one case" claim where at least
five live assertions match, an unstated `.count` receiver limit, and a
marker-spelling limit that named one spelling out of a class. The spaced
colon is no longer a limit at all — the opener now tolerates the space so
the spelling is rejected rather than ignored.

**Revision 4** applied those, and a fifth round found four more. This was
the first round where nothing in the mechanism's LOGIC was wrong:

15. **The claim that the strict literal rule "costs nothing real" was
    wrong**, and the reviewer refuted the session's own measurement. All
    five dropped fragments come from runtime-constructed needles such as
    `"--model " + CANONICAL_ID`, whose assertions genuinely do require
    the fragment present. They are real partial locks. The accurate claim
    is "no current marked coverage".
16. **The code accepted `.count()` with any number of arguments** while
    all four artifacts specify the singular form — the same
    code-versus-documentation drift that produced defects 10 and 14. Now
    exactly one positional literal argument, matching all seven live
    count pins.
17. **The `.count` receiver limit had an unstated twin**: a membership
    container is equally untyped.
18. **Pin collection is execution-blind.** An assertion inside a
    platform-skipped module still registers as a pin. Found by the
    read-only lane, in the same bullet the other lane had just extended.

Across five rounds the lane that ran the code found thirteen of the
eighteen, including every mechanism defect. The lane that could only read
found the instruction-file defects twice, plus a wrong line citation the
session had copied from the other lane without checking, plus this
execution-blindness limit. Neither seat was redundant, and every round
through the fourth found something inside the previous round's fixes.

The fifth round broke that streak: both lanes attacked the round-4 marker
parser with constructed inputs and neither could make a region vanish.
What remained were two limit statements and one arity mismatch.
