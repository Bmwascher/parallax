# Diff debate, round 4 — item 48 PowerShell 7 feasibility

Both round-3 findings reproduced and accepted. Head is now `daee2b2`.
Range for this round: `778961e..daee2b2`.

Eight findings, then five, then two. This round is the confirming one
unless you find something.

## What changed

- **Finding 1 (tenth instance).** The `:400` bullet now names the test it is
  actually in — `test_measurement_20_a_failed_host_invocation_never_reads_as_divergence`
  — and states plainly that it was the tenth instance of this record
  asserting and refuting the same characterization, rather than swapping the
  text silently.

  **While checking the other split groups for the same "same X as"
  shorthand, the implementer found a second instance nobody had asked for:**
  the `test_backup_lane.py` 16-line group actually spans **three different
  test functions**, not the one "test group" every follow-on bullet claimed.
  It was rewritten as three correctly attributed sub-groups. The other three
  groups — the five dual-family pairs, the six-line
  `test_multi_model_verify.py` group, and the three-line
  `check_workflow_paths.py` group — were checked and are correct.

- **Finding 2.** "83 rows, 83 one-line entries" and "3 bullets for 3 rows"
  are now bound explicitly to `b1e9cfa`. A convention sentence was added:
  **a figure does not inherit a binding from a nearby bound figure**, since
  the bound commit can be provably wrong for it — as `a13d3c3` literally
  was, holding 50 bullets where the figure claims 83.

The must-change bullet citations were re-extracted and matched against the
TSV after the content fixes: still exactly 83, still an exact match. I
verified the bullet count independently.

## What I want from this round

1. **The `test_backup_lane.py` regrouping is new content produced by the
   fix.** It is exactly the shape that has generated defects all cycle: new
   text written to correct old text. Check the three sub-group attributions
   against source.
2. **The convention now has two clauses** — commit-bound or invariant, and
   no inheriting a neighbour's binding. Both were written after a finding
   showed the previous version too narrow. Ask whether a third gap exists
   rather than whether these two are stated.
3. **Sweep the class and name an eleventh instance, or report none
   explicitly.** Ten have been found across this branch. Six were inside a
   fix for the previous one, the ninth was inside the paragraph written to
   end the class, and the tenth was inside content produced to fix a
   different finding. That base rate is the reason I keep asking.

## On stopping

If what remains is genuinely below the threshold that should block a merge,
**say that plainly and return PASS.** I asked the other reviewer for an
honest floor rather than a clean sheet and got one, and the same request
applies to you.

I am not looking for a courtesy PASS and I am not looking for a manufactured
finding. A reviewer that has produced fifteen real findings across three
rounds is exactly the one at risk of reaching for a sixteenth. If the
document is sound at this head, the useful thing you can tell me is that it
is sound, and what you swept to be able to say so.

## Standing

The record and its directory are the only editable surface. The verdict is
CONDITIONAL on five conditions; you have confirmed that adjudication sound
in all three rounds.

End with **PASS**, **FIX**, or **ESCALATE**.
