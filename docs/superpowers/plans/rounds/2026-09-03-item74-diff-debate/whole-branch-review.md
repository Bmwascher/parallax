# Whole-branch review artifact — range 5d20eed..7fed651

Seat: `agents/fable-reviewer.md`, single dispatch, read-only tool grant.
Range reviewed: `5d20eed..7fed651`. The branch head is now `5399655`, which
is the review's own fixes applied; see the adjudication table in the
round-1 brief.

Raw reply below, verbatim.

---

### Strengths

- Task 1 is the right minimal fix. `tools/dispatch-round.ps1:1609-1612` (package lines; repo `:588-591`) prepends the call operator and says why in an ASCII comment; `evals/multi-model-verify/test_dispatch_round.py:1283-1287` (package) pins `startswith('& "')` with the measured reason. No other field of the `-Prepare -Json` object changed.
- The five `using `command` verbatim` replacements are consistent and keep both raw-text pins intact on one physical line: package `SKILL.md:1391, 1410` and `backup-lane.md:1433, 1452, 1471`. The new pin `"exactly as printed"` at `test_multi_model_verify.py:1353` (package) locks the replacement for both bodies.
- Risk 5, checked against the tool: `tools/dispatch-round.ps1:485-495` at head accepts exactly `pwsh` or `powershell` (case-sensitive `-cne`), resolves it with `Get-Command`, and exits 2 on anything else. The new `SKILL.md` sentence (package `:1377-1379`) describes exactly that. The printed command at `:1612` is a valid PowerShell statement, so "running `command` exactly as printed" is now true rather than aspirational.
- Risk 1, checked phrase by phrase: all three needles in `test_multi_model_verify.py:1318-1329` (package) are present in the notes under the normalized read (package `model-prompting-notes.md:1513-1522, 1557-1559`) and each is the sentence that carries the measurement limit, not incidental prose.
- Risk 3: the rewritten section states no value for the `model: fable` alias ("UNVERIFIED from the tree", package `:1515`) and assigns no effort level to any seat. The two protected facts stay conditional.
- The rewrap of the resume bullet (package `:1579-1586`) changed no words; only line breaks moved.
- Item 74 records its own two false drafts and how the false sentence got written (package `:386-420`). That is the honest form.

### Issues

#### Critical

None.

#### Important

1. **Item 75 cites line numbers in the backlog file that point into item 75 itself, and were wrong in the commit that wrote them.** Package `:541-542` says "item 4's constraint at `:561-564`" and `:580-581` says "(`:530-535`, `:543-545`)". At head, item 4 begins at `docs/superpowers/plans/2026-07-27-0150-backlog.md:983`; lines 530-564 sit inside item 75 (which spans `:501-605`). Commit a5470ea inserted about 430 lines above item 4 in the same edit. These cites are bound to nothing; the panel record's `5d20eed` binding covers the cross-file cites but not these. This is item 69's class, produced by the branch while filing item 69's neighbours.
   - Same class, softer because the panel record binds them to `5d20eed`: item 74's `model-prompting-notes.md:43-45` (package `:384`) is `:75` at head; item 75's `:572-582` and `:488-489` (package `:530, :542`) are `:618` and `:528` at head, both shifted by this branch's Task 3; item 74's `SKILL.md:213`, `:301`, `:327,332` shift by one from Task 2; `test_multi_model_verify.py:3500` is now about `:3523`; `test_dispatch_round.py:432-434` now asserts the opposite of what item 74 says it asserts. Nothing in either item says the cites are as of `5d20eed`.

2. **The ranking preamble contradicts itself in the edit meant to correct it.** Package `:76-77` says "every entry below is renumbered up by two and nothing else moved", but 77 was inserted as entry 11 (package `:159`) and 76 as entry 23 (package `:251`), so entries 12-22 moved by three and 24-36 by four. And package `:49` (unchanged context, `backlog.md:49`) still says "nobody has costed those five" one sentence after the same paragraph added 71, 72 and 73 to the unranked set (package `:43-44`), making it eight. The paragraph two lines below states the file's own rule: a summary that disagrees with the items is worse than no summary and is corrected in the same commit.

#### Minor

3. **A pinned phrase names a sweep this repo never ran.** `model-prompting-notes.md` (package `:1520`) says "so the Fable 5 sweep does not carry", and `test_multi_model_verify.py:1322-1324` (package) pins it. The bullet it replaced (package `:1507-1509`) was guide advice with permission to sweep, not a recorded sweep. In a section whose purpose is to keep unmeasured things unmeasured, this reads as a measurement. Reword, tests first, to something like "so Fable 5 effort guidance does not carry".

4. **Risk 2: `"### Fable 5" in notes` is accidentally green, and nothing else locks 5.1.** `evals/multi-model-verify/test_seat_reshuffle.py:290` passes for `### Fable 5`, `### Fable 5.1`, or any later heading. The new test's name says "are_51" (package `:1309`) but no assertion in it contains "5.1". Reverting the heading and the fetch line to the Fable 5 guide leaves every test green. Add `"### Fable 5.1" in notes` to the new test.

5. **Two sentences were retargeted from the 5 guide to the 5.1 guide with no recorded check.** Package `:1502-1503` "the three seat-invariant rules above appear in it near-verbatim" and `:1505-1506` "Bug-finding recall is a documented strength" now attribute to the 5.1 document. Item 74 carries neither claim, and the plan's Step 3 says every claim is carried from item 74. Same for the effort names `xhigh` and `max` (package `:1523-1524`): item 74 says "the two highest effort levels" and names none. None of these is about the seats, so they are not the forbidden class, but they are attributions the record does not show anyone verifying.

6. **The test docstring presumes a version.** `test_multi_model_verify.py:1310` (package) says "0.29.0 item 74". The bump happens after the debate and is not set by this branch.

7. **Markdown structure in the ranking.** No blank line between entry 11 and the `**Third` header (package `:165-166`), so the header renders as a continuation of entry 11. Entries 12 and 23 use a five-space continuation indent (package `:181-186, :252-258`) where every neighbour uses four.

8. **No step closes item 74 at merge.** Item 74 is filed OPEN and describes `SKILL.md:213` and `test_dispatch_round.py:432-434` in the present tense as saying things head no longer says. The plan's "After the tasks" (plan `:479-493`) has no step to mark 74 done and move it out of the Open list, and the file's rule wants that in the same commit as the heading change.

### Ledger minors triage

There is no SDD ledger for this branch. The plan header (plan `:3`) requires `superpowers:subagent-driven-development`, which in this repo writes a `.superpowers/sdd/<date>-<name>/` ledger; a glob for `.superpowers/sdd/*item74*` finds nothing. Either the plan ran without SDD or the ledger was never committed. Either way there are no deferred minors to triage, and the absence is itself a gap of item 59's class: nothing enforced the process the plan named. Name it in the debate brief rather than treating it as clean.

### Assessment

Ready to merge: With fixes

The code, skill and reference edits are correct, minimal and pinned; the two `-DispatchHost` and dispatch-clause corrections match what the tool does. The backlog record, which is most of the diff by volume, contradicts itself (Issue 2) and cites itself wrongly in the same commit (Issue 1); both are cheap prose fixes and should land before the mode-diff debate reads that file as the spec.
