<!-- Fable panel-reviewer lane, round 3, reviewed at HEAD 685a7c7.
     Extracted verbatim from the lane's own transcript;
     evidence/fable-lane-six-rounds.jsonl was the source. -->

All verifications this round were made at HEAD `685a7c7`. I also opened the measurement fixture itself: `C:\Users\Brandon\.claude\plugins\cache\openai-codex\codex\1.0.6\skills\codex-cli-runtime\SKILL.md:12` holds the on-disk literal exactly as claimed. The substitution half of the measurement is your observation of what reached a model; I can verify its input, not the observation, so it stays a recorded harness fact, correctly marked non-repo-verifiable at plan:34.

## 1. The five round-2 changes

1. **Measurement before freeze - CLOSES.** Plan:65 (constraint rewritten as measured), plan:68-76 (Step 0 records and re-takes), no conditional anywhere downstream. The adequacy question is answered in section 2, and it is not clean.
2. **Step 0 home and oracle - CLOSES.** Plan:76 (field and stop-on-verbatim), plan:168 (Task 1's commit stages the record), plan:798 (Task 8 says Modify and names Task 1 as creator), plan:826 (schema carries the harness line), plan:847 (test asserts `plugin_root_token=substituted` and non-empty version, red on `verbatim`).
3. **Task 7 split per lane - CLOSES.** Plan:765-780: codex keeps its three outcomes, the kimi stub emits stdout, the four cases include the byte-exact no-BOM comparison with the astral-plane character, and the red demonstration deletes the `[Console]::OutputEncoding` line. This is the oracle that was missing.
4. **The three caveats - CLOSES.** Plan:619-625, and both citations are accurate against the file: the IBM437 measurement at `new-review-mirror.ps1:57-65`, the non-strict U+FFFD decode at `:67-75`. The `-join` reasoning at plan:625 matches what I told you.
5. **The record - CLOSES.** Plan:992, round 18 at plan:1016, the second lane and round 19 at plan:1018. Cosmetic only: the entries now run 10-12, 18, 19, 13-17, out of order; the headers keep it readable.

## 2. Is the measurement adequate?

**For what it measured, yes. For where the plan now ships the token, no.** One observation of a deterministic loader behavior, on a named client version, with the fixture verifiable on disk, a mandated re-take, and a test that goes red on `verbatim` is as strong as a harness fact gets in this repo. Sample size is not the problem.

The problem is scope, and your own constraint wording exposes it. Plan:34 states the fact as substitution "in plugin skill body text." The fixture is SKILL.md body, and the two codex calls live in SKILL.md - covered. But **three of the five detached calls live in `references/backup-lane.md`** (plan:565, :573, and step 3 at plan:611), and region one lives in `model-prompting-notes.md` (plan:200), and the pointer in CLAUDE.md (plan:967). References files are not loaded as skill body: the session reads them with the Read tool, raw. Nothing measured says the token is substituted there, and everything known says it is not. A session copying the kimi launch command out of backup-lane.md pastes the literal into PowerShell, where it expands to EMPTY and the path becomes the drive root - the exact failure plan:65 documents for the unsubstituted case, on three of the five commands this plan exists to detach. The Task 9 closure sentence (plan:973, "resolved by the harness, measured") would then be true for two call sites and false for three.

So: you replaced an honest fork with a fact that is true where it was measured and silently extended to where it was not.

The fix does not need a new measurement. `backup-lane.md`'s own pinned convention for plugin paths is the `<plugin-checkout>` placeholder (`backup-lane.md:25`, pinned at `test_backup_lane.py:139-142`). Use `<plugin-checkout>/tools/dispatch-detached.ps1` in that file's launch and poll literals, keep `${CLAUDE_PLUGIN_ROOT}` in SKILL.md where substitution is measured, and say in region one and the closure text that the two documents carry two forms for a measured reason. Alternatively, extend Step 0 to measure a references-file read; that adds a fourth harness fact where the placeholder adds none, so I recommend the placeholder.

## 3. What revision 20 introduced

- **The scope gap above.** Plan:565, :573, :611, :200, :967, against the constraint's own wording at plan:34.
- **Plan:835 is false as written.** It says the harness line is "the only place in this plan where a step in one task writes into a file another task creates." Plan:780 has Task 7 step 4 writing `kimi_reply:` rows into that same record - into host sections that Task 8 step 5 creates AFTER Task 7 runs - and Task 7's commit (plan:789) does not stage the record. One writer claim, contradicted two tasks earlier, plus an impossible write order, plus an unstaged artifact. Smallest fix: give the two `kimi_reply` lines to one owner - either Task 8 records them when it writes the host sections, or Task 7 writes them beside the harness line, stages the record, and plan:832/:835 are amended to match.
- **Plan:946 says "all three clauses"; the oracle above it requires four** (plan:928-932, the fourth being `the pid on disk is the dead wrapper`). A count in prose contradicting the code beside it is this debate's signature class.
- **Task 1's Files list (plan:43-45) omits the probe record** its own step 0 creates and its step 5 stages (plan:168). Same shape I flagged on Task 8 in round 2.
- One clause worth adding, not a defect in outcome: Task 7's kimi stub must be a NATIVE executable. `&` on a `.ps1` runs in-process, never crosses the console decode boundary, and the byte comparison then passes with the `[Console]::OutputEncoding` line deleted. Your mandated red demonstration at plan:775 would catch this operationally - the red would refuse to appear - but the implementer deserves the reason in the task text.

## 4. Verdict

**FIX**, on `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md` at `685a7c7`. Smallest set:

1. Split the token per document: `<plugin-checkout>` form in `backup-lane.md`'s launch and poll literals (plan:565, :573, :611), the measured token in SKILL.md; state the split and its reason at plan:34 or :65, in region one (plan:200), and in the closure text (plan:973).
2. Resolve the probe-record ownership: one writer for `kimi_reply`, staged by its writer; correct plan:835 and, if Task 7 keeps the write, plan:832 and plan:789.
3. Plan:946: "three clauses" becomes four.
4. Plan:43-45: add the probe record to Task 1's Files list.
5. One sentence at plan:773: the kimi stub is a native executable, because an in-process script never crosses the decode boundary the case exists to measure.

UNVERIFIED, stated and not folded in: the substitution observation itself (your session's context, outside the repo); whether references files are substituted (unmeasured either way - which is exactly why item 1 avoids relying on it); the kimi client's stdout encoding, unchanged.

FIX
