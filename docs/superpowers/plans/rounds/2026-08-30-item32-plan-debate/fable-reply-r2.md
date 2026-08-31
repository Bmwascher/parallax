<!-- Fable panel-reviewer lane, round 2, reviewed at HEAD c36f8c2.
     Extracted verbatim from the lane's own transcript;
     evidence/fable-lane-six-rounds.jsonl was the source. -->

All claims below were re-read at HEAD `c36f8c2`. My round-1 state is intact, so the comparisons are against what I actually reviewed, not a reconstruction.

## 1. The six findings

1. **`${CLAUDE_PLUGIN_ROOT}` - CLOSES** the finding I raised, at plan:65 (third harness fact, with `hooks/hooks.json:10`/`:22` and `SKILL.md:326` both verified real: :326 does use `<plugin-root>` and the backlog at 2026-07-27-0150-backlog.md:4496 does say "none decided") and plan:68-75 (Step 0 measures instead of assuming). The repair introduces two new defects; see section 3.
2. **Kimi reply encoding - CLOSES**, at plan:602-618. The cited measurement is real: `tools/new-review-mirror.ps1:59-65` records IBM437 as the default on both hosts. Judgement on your two questions is in section 2. One introduced gap; see section 3.
3. **Region three overclaim - CLOSES**, at plan:287-297. The second uncleaable case is named, the pid is identified as the dead wrapper, and "it is the REMEDY that fails, not the completion model" is exactly right: with a live client child the wrapper never wrote `exit`, so the poll lands on DEAD then `no-exit-file`, never success.
4. **Orphaned freshness prose - CLOSES**, at plan:497-499. The rewrite moves the rule onto the artifacts `-Launch` actually refuses (both are refused: the directory by `New-Item` without `-Force` at plan:134, the receipt at plan:133). I also checked the pre-existing pin this touches: `test_fresh_per_round_files` (`test_multi_model_verify.py:743`) matches `fresh[^\n]*round`, and Task 3's inserted "`<receipt-file>` is a FRESH path for this round" (plan:482) keeps it green.
5. **Task 8 Files list - CLOSES**, at plan:775-779, with the round-7 parallel recorded.
6. **Revision stamp and spec count - CLOSES**, at plan:13 (revision 19 delegates counts to the commit-bound section) and plan:863 plus plan:870 (grep pattern and exact replacement, "five" verified against `test_multi_model_verify.py:619-647`). One introduced record gap; see section 3.

## 2. The two questions on the encoding fix

**Does `[Console]::OutputEncoding` govern the decode of a child's stdout on 5.1?** Yes. Windows PowerShell decodes captured native stdout with `[Console]::OutputEncoding` at call time; your own repo documents both the default and the override at `new-review-mirror.ps1:57-65`. The fix is not wrong. Three caveats belong in the passage:

- The setter calls the console API, so in a process chain with NO attached console it throws. In this wrapper the throw lands in the `catch`, writes exit 1, and polls as `exit-nonzero`: fail-closed, never false-clean. Say so, because the first time it happens it will look like a client failure.
- The decode is NON-STRICT: a malformed byte becomes U+FFFD silently. `new-review-mirror.ps1:67-75` states this exact limitation as its own reason for reading raw bytes. Your fix narrows the defect; it does not prove byte identity, and the passage should say that so nobody later claims it does.
- It assumes the client emits UTF-8, which is unverified. Setting the console code page to UTF-8 is also the standard way to ask a well-behaved CLI for UTF-8 output, so it is the right move under either answer.

**Is `-join "`n"` worse than the redirect?** No, it is strictly better, and here is the part that matters: the redirect had already destroyed CRLF fidelity. PowerShell splits native stdout into lines at decode time in BOTH forms; `>` then rejoins with CRLF and re-encodes UTF-16LE on 5.1. Your join discards nothing the redirect preserved. Nothing binds the reply's bytes on this lane (the binder hashes the PROMPT from session records, `backup-lane.md:33-36`), and a `$null` output joins to an empty string, which lands on `reply-empty`, the correct state. Keep it.

## 3. What the repairs introduced

Four things, in the order I rate them.

- **Step 0's losing branch contradicts five unconditional literals downstream.** If the measurement says the harness does NOT substitute, the documented form becomes `<plugin-root>` (plan:73), but the token is hardcoded unconditionally in Task 1's verbatim commands (plan:108, :112), Task 3's test literals and skill text (plan:384, :390, :478, :490), Task 4's test literals (plan:564, :572), Task 2's region one (plan:199), and Task 9's CLAUDE.md pointer (plan:934). Plan:75 says "Either way ... use ONE form", but the Task 2, 3, 4 and 9 implementers see only their own task, which asserts the token without a condition. This plan's own standard, cited twice inside it (plan:105, plan:509), is that a task must be executable from its own text.
- **Step 0 is an oracle-less step writing into a file another task creates.** It records into Task 8's probe record (plan:70), but Task 8 still says Create for that file (plan:776), its fixed shape (plan:803-808) has no field for the measurement, and its test (plan:814-818) asserts only the fixed shape's values. A skipped Step 0 passes every oracle in the plan. Task 1's commit (plan:167) also stages neither the record nor its directory. This is the round-4 class (a step with no oracle) plus the round-7 class (an artifact written but not listed), both reproduced inside the fix, which matches this debate's own pattern since round 8.
- **Task 7 step 4 is now stale against the revision-19 kimi wrapper.** Plan:758 still says "stub exits 0 writing a reply, expect ... a reply present". Under the new wrapper (plan:603-605) the wrapper writes the reply FROM CAPTURED STDOUT; a kimi stub that writes a reply file and prints nothing gets its file overwritten with an empty string and the case cannot pass. The instruction fits only the codex body, where the client writes the artifact itself. This is text left behind by a mechanism change, the exact class of rounds 13 to 17.
- **The encoding fix has no oracle, and the record section stopped short of its own reviews.** Nothing anywhere runs the `[Console]::OutputEncoding` path against non-ASCII content: Task 7's stubs specify no non-ASCII, and Task 8's encoding measurement (plan:791-795) is codex-only, unchanged. Separately, plan:957 promises "later rounds are recorded below by number", and the record (plan:963-985) ends at round 17 plus the poll: round 18 and the two Fable rounds, the rounds that produced revision 19, exist only inside task prose (plan:497, :614, :779, :801, :870).

## 4. Verdict

**FIX.** Smallest set:

1. Resolve Step 0's conditional before freeze, or mark every downstream literal. Either run the measurement now so the frozen plan carries ONE form, or add at plan:199, :384, :478, :564 and :934 the rider that the anchor token is the form Step 0 selected. I recommend measuring before freeze: it is cheap and a frozen plan should not carry a fork its later tasks cannot see.
2. Give Step 0 a home and an oracle: Task 1 step 0 creates the probe record with a named field (for example `plugin_root_token=<substituted|verbatim>`), Task 8's Files line becomes Modify for that file, and `test_wrapper_probe_record.py` asserts the field (plan:70, :776, :814-818).
3. Rewrite Task 7 step 4 per lane (plan:756-758): the codex stub writes the reply file; the kimi stub EMITS stdout including at least one non-ASCII character, and the test asserts the reply file holds its exact UTF-8 bytes on both hosts. This one change also becomes the missing oracle for the encoding fix, with a real red available by deleting the `[Console]::OutputEncoding` line.
4. Add the three caveats from section 2 to the Task 4 passage (plan:614-618), citing `new-review-mirror.ps1:67-75` for the non-strict decode.
5. Record round 18 and the Fable rounds below plan:985, or amend the promise at plan:957.

UNVERIFIED, unchanged from round 1 and not folded into this verdict: whether the harness substitutes `${CLAUDE_PLUGIN_ROOT}` in skill text (Step 0 now exists to answer it); the kimi client's stdout encoding; the Sol session history beyond what this repository records.

FIX
