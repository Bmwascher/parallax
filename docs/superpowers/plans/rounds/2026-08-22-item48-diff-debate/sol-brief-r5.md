# Diff debate, round 5 — item 48 PowerShell 7 feasibility

All three round-4 findings reproduced and accepted. Head is now `9cc3a5f`.
Range for this round: `daee2b2..9cc3a5f`.

**This is the last round I intend to run.** Read the closing section before
you answer.

## What changed

- **Structural (your findings 1 and 2's shared root).** Two canonical
  binding places now exist — `### must-change rows, whole file` and
  `### unknown rows, whole file` — and **nine other sites** across the
  record were converted to point at them by name instead of restating the
  numbers. A third convention clause was added: **a count about this
  record's own inventory is stated once, bound once, and referenced
  everywhere else.**

  This is the same form as the section-anchor fix and the commit-bound fix:
  remove the duplicate rather than keep copies in step. Your observation
  that no migration-value count can ever be an invariant — because
  `survey.py` accepts any of the three values and the exit predicate never
  reads them — is what settled the direction.

- **Finding 1.** The convention paragraph's own example is now bound on both
  sides at both commits: 83 rows and 50 bullets at `a13d3c3`, 83 and 83 at
  `b1e9cfa`. The rows-versus-bullets mislabel is fixed.

- **Finding 2.** "Five dual-family rows" is now "five dual-family pairs …
  ten rows". All 20 other uses of "five" in the document were swept; none
  else needed changing.

- **Finding 3.** The description now says what the test does: it
  deliberately builds an incomplete `pwsh.exe` step and asserts the detector
  **flags the gap**. The other two sub-group descriptions were re-checked
  against source as a precaution and held.

The implementer also caught two stray edit artifacts mid-round and fixed
them before continuing. I checked the two remaining backslash-backtick
sequences in the file myself: both are legitimate Windows paths ending in a
separator, not artifacts.

Gates at this head: `SURVEY_EXIT=0`, 83 bullets against 83 TSV rows
re-verified, 11 headings, zero placeholders.

## What I want from this round

1. **Attack the canonical-binding fix.** Nine sites were converted. Did any
   conversion change what a sentence claims? Is there a tenth site that
   still restates a number? Does the third convention clause overreach the
   way the first two did — both were found too narrow within one round of
   being written.
2. **Sweep the class and name a twelfth instance, or report none
   explicitly.** Eleven have been found on this branch. The ninth was inside
   the paragraph written to end the class; the eleventh was inside the
   sentence written to state the rule. I am asking with a clear expectation
   that something may still be there.

## Closing this debate

Four rounds have produced eighteen findings and every one was real. I have
accepted all eighteen and refuted none. The trend across rounds is 8, 5, 2,
3.

**I intend to close after this round and adjudicate any residuals myself**,
because a reviewer's verdict is not terminal in this protocol and the
remaining findings have moved from structure to phrasing.

So the most useful thing you can do now is be precise about severity:

- If something here **should block a merge**, say so and say why in terms of
  what a reader of this record would get wrong.
- If what remains is **real but below that bar**, say that plainly and say
  it should not block. I will record it as a residual with your wording,
  not bury it.
- If the document is **sound at this head**, say so and say what you swept.

I would rather have an accurate floor than a clean sheet, and I would rather
have "these three are real but minor" than either a courtesy PASS or a
manufactured twelfth finding. You have earned the benefit of the doubt on
this; use it to tell me the truth about severity.

End with **PASS**, **FIX**, or **ESCALATE**.
