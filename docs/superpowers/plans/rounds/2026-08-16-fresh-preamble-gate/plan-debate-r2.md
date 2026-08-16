# Plan debate, round 2 - 0.26.0 fresh-preamble gate

Same session `01a00b96-1d26-77f2-bb53-13702ab58e1a`, resumed. Route
re-confirmed against the transcript header - `gpt-5.6-sol`, openai,
read-only, effort high - and the reply bound by
`tools/read-codex-round-evidence.ps1 -Resume` before it was read: verdict
`clean`, brief digest
`a47ab4ec91cfe6a23c382d38a96bc1bcdd130045e0a3572837d2fe9f250bad90`, over
round 1's `nextState` verbatim as the prior state - the same rollout file,
709876 bytes, prefix hash unchanged.

The round asked two things: are round 1's four fixes correct, and then -
the round's purpose - sweep the whole plan for further instances of the two
CLASSES round 1 found, rather than re-checking the fixes.

Verdict: **FIX**, five required corrections. The session accepted all five
and refuted none. Three of them were arithmetic this side got wrong.

The reply is retained verbatim.

---

## First: the four fixes

1. **Explicit test selection: correct.** Task 2 names exactly four node IDs. Its first three cases fail before the fix and its invalid-date control passes. [plan:442-459](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:442)

   Task 3 also names exactly its twelve new cases. The split is correctly counted:

   - Seven REFUSAL tests: novel text, text after envelope, missing core, one-field envelope, two envelopes, repeated field, newline-bearing field name.
   - Five CLEAN tests: text before envelope, envelope alone, trailing whitespace, unknown name, malicious field value.

   Before the fresh gate exists, all twelve pass count/hash/order; therefore the seven negatives fail because the tool returns clean, while the five positives pass. [plan:628-759](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:628) [plan:777-798](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:777)

2. **Unknown-field-name documentation: correct.** The proposed pin and region both contain the same added sentence under whitespace normalization. [plan:1001-1015](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1001) [plan:1063-1077](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1063)

3. **Task 4’s zero-judgment prose and terminal gate: partly correct.** The headings and closing paragraphs are now literal, and Step 6 reads back the version and runs the static gates plus both PowerShell hosts. [plan:1132-1247](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1132) [plan:1331-1357](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1331)

4. **Task 4’s rebuild and renumbering fix is not correct.**

   The heading regex does match all 59 item headings, including the older `## 17.` form, the later `## Item 26:` form, and both `DONE` and `CLOSED` status spellings. [backlog:214](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:214) [backlog:2128](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:2128) [backlog:4081](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:4081) [plan:1273-1292](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1273)

   After changing 52, 56 and 57 to `DONE`, the actual groups are:

   ```text
   DONE               26
   PARTIALLY CLOSED    2
   GONE                 1
   OPEN                30
   no status in heading: none
   ```

   The plan prints `OPEN 29` even though its own accompanying list contains 30 numbers, and it omits the fifth line that the script always prints. [plan:1289-1302](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1289)

   The renumbering is also incomplete. Step 1 fully closes item 57, but Step 4 deletes only ranked entries 52 and 56; item 57 remains at ranked entry 25. [plan:1166-1175](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1166) [plan:1311-1329](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1311) [backlog:195-198](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:195)

   All three closed entries—52, 56 and 57—must be deleted. The correct ranked-entry count is therefore **25**, not 26.

   Moreover, the proposed `awk` range runs from the build-order heading to EOF. It also counts nine later numbered bold lists, such as those at backlog lines 1172, 1639, 2160 and 3461. [backlog:1172](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:1172) [backlog:1639](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:1639) [backlog:2160](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:2160) [backlog:3461](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-07-27-0150-backlog.md:3461) As written, after deleting only 52 and 56, that command reports **35**, not 26. After correctly deleting all three, the same unbounded command would report 34.

## Class 1 sweep: stated expected result differs from reality

1. **Task 1 Step 6 gives the wrong reason for one of its three failures.** All three tests do fail, but `test_a_whitespace_only_mismatch_names_the_canonicalization` does not fail because the old tool emits its old message. It supplies the digest of the padded, untrimmed prompt; the old tool hashes that same untrimmed prompt, so it returns CLEAN, and `assert_failed` fails on status. Only the real-mismatch control receives the old generic mismatch message. [plan:228-273](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:228) [read-kimi-round-evidence.ps1:891-897](/C:/Users/Brandon/Documents/parallax/tools/read-kimi-round-evidence.ps1:891)

   Correct expected result:

   - Padded-clean test fails because the old hash moves.
   - Whitespace-only diagnostic test fails because the old tool returns clean.
   - Real mismatch test fails because the old tool emits the generic message.

2. **Task 4 Step 3’s expected output is wrong.** Real post-change output is `OPEN 30`, not 29, followed by `no status in heading: none`. [plan:1289-1302](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1289)

3. **Task 4 Step 4’s expected result is wrong twice.** The correct build-order membership has 25 entries after removing 52, 56 and 57; the command as written reports 35 after the plan’s two removals because it counts to EOF. [plan:1311-1329](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1311)

No further Class 1 instances found among the remaining `Expected:` steps.

## Class 2 sweep: changed tree is not verified

1. **Task 4 Step 2’s three closing paragraphs have no oracle.** The rebuild script reads only headings, the ranked-order check reads only numbered entries, and the terminal gates contain no stated comparison against those verbatim paragraphs or their placement. [plan:1178-1247](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1178) [plan:1278-1292](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1278) [plan:1343-1357](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1343)

   Add a readback assertion for each exact normalized paragraph and verify that each occurs once inside the intended item before the next item heading.

2. **Task 4 Step 3 edits the status block after running a script that never parses or compares that block.** The script prints membership derived from headings; it does not establish that the subsequently edited `Done`, `Partially closed`, `Gone`, and `Open` lists match. [plan:1251-1309](/C:/Users/Brandon/Documents/parallax/docs/superpowers/plans/2026-08-16-fresh-preamble-gate.md:1251)

   Extend the script to parse the status block and fail on any membership difference, then run it after editing the block.

No further Class 2 instances found in Tasks 1–3.

## Verdict

**FIX**

Required corrections:

- Change Task 1 Step 6’s stated failure reasons.
- Correct Task 4’s post-change output to `OPEN 30` and include `no status in heading: none`.
- Remove ranked item 57 as well as 52 and 56; expect 25 entries.
- Bound the ranked-entry counting command to the build-order section.
- Add readback verification for the closing paragraphs and regenerated status block.

**UNVERIFIED**

- The reported 769-record follow-up session-store sweep; no retained artifact for it was among the files read.
- Future full-suite pass/skip counts, because the planned implementation has not yet been executed.