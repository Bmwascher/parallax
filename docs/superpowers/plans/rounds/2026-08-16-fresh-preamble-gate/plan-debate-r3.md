# Plan debate, round 3 - 0.26.0 fresh-preamble gate

Same session `01a00b96-1d26-77f2-bb53-13702ab58e1a`, resumed a second time.
Route re-confirmed against the transcript header - `gpt-5.6-sol`, openai,
read-only, effort high - and the reply bound by
`tools/read-codex-round-evidence.ps1 -Resume` before it was read: verdict
`clean`, brief digest `9d7d0f2486aed72b1a925413ee0c4b3e100f60200b3310365851d63356bf7f83`,
over round 2's `nextState` verbatim as the prior state.

The round asked three things: read the new `check_backlog.py` as code and
say whether any check can pass VACUOUSLY; re-sweep the two known classes
over the changed steps only; and say whether a third class exists, or
plainly that none does.

Verdict: **FIX**. It named a THIRD CLASS - oracle vacuity - and found four
instances of it inside the checker this side had just written to close the
second class. All accepted, none refuted.

The reply is retained verbatim.

---

The arithmetic corrections are sound, but the new backlog oracle still has refusal gaps. The plan needs another revision.

## 1. `check_backlog.py`

- Missing status rows do fail closed. If `BLOCK_ROW` matches nothing, all four required groups are appended as failures, and any accumulated failure produces exit 1 ([plan:1347](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1347), [plan:1371](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1371), [plan:1423](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1423)).

- A missing or renamed build-order heading fails, but a moved heading can pass vacuously. If the heading is moved below the entries while the entries stay in place, `ranked` is empty and `nums == list(range(1, 1))` is true. The checker prints `ranked entries 0` without adding a failure ([plan:1375](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1375), [plan:1383](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1383), [plan:1390](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1390)). Add an explicit `if not ranked: fail.append(...)`.

- An empty paragraph file refuses on the current nonempty backlog: `want` becomes `""`, and its occurrence count is not one ([plan:1403](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1403), [plan:1407](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1407), [plan:1409](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1409)). An explicit empty-input failure would give a better diagnostic but is not required for refusal.

- Check 2 extracts the current rows correctly. Their non-item numbers are inside parentheses, while their item numbers are outside; stripping the former and discarding the bold status label therefore yields the correct four sets ([backlog:25](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:25), [backlog:31](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:31), [backlog:33](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:33), [backlog:34](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:34), [plan:1358](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1358)). I found no real row producing the wrong set.

- The current section boundary is right: the build-order heading is at line 49 and the next `## ` heading is at line 214 ([backlog:49](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:49), [backlog:214](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:214), [plan:1376](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1376)). The contiguity comparison catches gaps, duplicates, and disorder for a nonempty list, but not the empty case above.

- The closed-item scan does not scan complete entries. It stores only the first line matched by `RANKED` and searches that line for item references ([plan:1383](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1383), [plan:1397](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1397)). Entry 24 places item 37 on its continuation line, so making 37 DONE while leaving that ranked reference would not be detected ([backlog:191](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:191)). Accumulate each entire ranked entry before extracting bold item numbers.

- Duplicate evidence is silently collapsed. Duplicate item-number headings overwrite `heading_line[num]` and `from_headings[num]`; duplicate status rows collapse into `seen_groups` ([plan:1325](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1325), [plan:1331](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1331), [plan:1348](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1348)). Thus leaving an original OPEN heading and inserting the new DONE heading can still report OK. Require every item number and every block group exactly once.

- Every failure actually appended to `fail` leads to exit 1 ([plan:1423](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1423)). The defect is that the cases above append nothing.

## 2. Changed-step sweep

Class 1: no further incorrect expected result found.

Task 1 Step 6 now states the three correct mechanisms. The old tool hashes normalized-but-untrimmed text ([Kimi tool:891](C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:891)); the second test supplies that exact untrimmed digest ([plan:228](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:228)); and `assert_failed` tests status before message ([Kimi tests:295](C:/Users/Brandon/Documents/parallax/evals/multi-model-verify/test_kimi_round_evidence.py:295)). The three stated failure mechanisms are therefore correct ([plan:279](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:279)).

Task 4’s six-failure split and final count of 25 are also arithmetically correct: the stale block contains 52 and 56 as OPEN and 57 as partially closed ([backlog:31](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:31), [backlog:34](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:34)); entries 6, 7, and 25 rank those three items ([backlog:96](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:96), [backlog:100](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:100), [backlog:195](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:195)). Removing three from 28 leaves 25.

Class 2: one verification-coverage defect remains.

Item 56’s prescribed closing text contains two paragraphs ([plan:1227](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1227), [plan:1243](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1243)), but the plan explicitly saves and checks only the first ([plan:1431](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1431)). Moreover, Step 2 requires the text at the end of its item with blank-line separation ([plan:1198](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1198)), while Check 4 merely requires normalized text somewhere inside the item ([plan:1416](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1416)). A missing second paragraph or a closing paragraph pasted near the beginning can therefore pass Steps 3, 4, and 6.

Save the complete two-paragraph Item 56 block and require each named closing block to be the terminal content of its item. If exact blank-line placement remains a requirement, compare the raw normalized-newline block rather than whitespace-collapsed text.

## 3. Third defect class

Yes: oracle ambiguity/vacuity. This is distinct from an incorrect predicted result or verifying the wrong file. Empty ranked sections, continuation lines never scanned, and duplicate headings or block rows can all produce OK after the checker discarded or never collected the evidence it claims to measure ([plan:1325](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1325), [plan:1348](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1348), [plan:1383](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1383)).

**Verdict: FIX** — reject empty ranked sections, parse complete ranked entries, reject duplicate item headings and duplicate status rows, and verify the complete Item 56 closing block at the required end-of-item position.

**UNVERIFIED**

- The claimed three historical executions of `check_backlog.py` have no retained artifact; the plan only records that they occurred ([plan:1271](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1271)).
- The postimplementation static-check and dual-host pytest results cannot be verified before the plan is executed ([plan:1516](C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1516)).
- The session-store measurements, including the unretained 769-record follow-up, remain unreproducible from the reviewed files.