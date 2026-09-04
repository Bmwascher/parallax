# Fable diff round 2, reply

Lane: same-harness, `parallax:fable-panel-reviewer`, read-only tool grant
(Read, Grep, Glob). FRESH dispatch, because the round 1 agent did not
survive a session context break. Subject revision `ced2f53`.

Transcribed from the subagent result. This lane writes no reply file, so
this is a transcription and not a copy of an artifact. Angle brackets
arrived HTML-escaped through the agent transport and are restored here;
nothing else is changed.

---

I have what I need. Findings follow, per claim, with evidence and conclusions only.

## Round 2 (fresh dispatch, no round-1 context): verdicts on `ced2f535e6223fd69114db68b3feaa0690ac9f96`

Tooling note: this lane has Read, Grep and Glob only. I could not run `git diff`, so every finding below is against the tree at the amended head, and the two things that need a diff to establish are listed as UNVERIFIED rather than folded in.

### G1: the Fable section (R1-a to R1-d) - FIX, one instance of R1-d's class remains

R1-a fixed. `skills/multi-model-verify/references/model-prompting-notes.md:32-35` now says ONE bullet carries two claims forward and is marked; the marked bullet is `:37-40` and it is the only marked one.

R1-b fixed. `:46` reads "Effort guidance must be re-evaluated"; no prior sweep is implied.

R1-c fixed. `:50-51` says "no Fable effort sweep is recorded in this repo", which is a claim about the record, and the record supports it: no other file matches "Fable effort sweep" (grep across the tree returned only the notes and the test comment at `evals/multi-model-verify/test_multi_model_verify.py:1136`).

R1-d fixed. `:52-53` reads "At the two highest effort levels", which is the wording item 74 carries at `docs/superpowers/plans/2026-07-27-0150-backlog.md:400-401`. `xhigh` and `max` no longer appear in the section (the only `xhigh` left in the file is the Opus 5 bullet at `:129`, untouched).

Two protected facts stay unverified: `:41-43` states the alias is UNVERIFIED from the tree and names no resolution; no sentence in `:28-114` assigns an effort to any seat.

Sweep result, remaining instance of R1-d's class: `:67-68` states 5.1 "can return `stop_reason: "refusal"` on benign code work". Item 74 carries the refusal finding at `backlog.md:416-419` without that literal; grep for `stop_reason` in the backlog returns nothing. The plan's Step 3 says every claim in the section is carried from item 74 (`docs/superpowers/plans/2026-09-03-item74-fable-51-notes.md:356-358`) and the plan's own draft carries the literal (`:395-396`), so the plan contradicts itself in the same way the whole-branch review's issue 5 named for `xhigh`/`max`. It is a guide attribution, not a measurement of the seats, so it is the weaker half of the class. FIX: either record the literal in item 74 as verified against the 5.1 guide, or replace it with "a classifier refusal" in the notes. Nothing pins the literal, so the notes side needs no test change.

No other sentence in `:28-92` reads as a measurement this branch does not establish; every remaining claim resolves to item 74 (`:395-471`) or to a file I read (`agents/*.md:4-5`, `agents/escalation-implementer.md:22-25`, `docs/superpowers/specs/2026-08-31-dispatch-options-costing.md:54-55`, `docs/superpowers/plans/rounds/2026-08-19-item50-resume-probe/probe-record.md:336-337, 353-366`).

### G2: the backlog (R1-e to R1-h) - FIX, two small items

R1-e fixed. `backlog.md:129-134` no longer says first, second and third; it says read the rank from the list, and the list has 49, 59, 67 at entries 3, 4, 5 (`:168-189`).

R1-f fixed. `:145-150` says the list was renumbered twice and no single offset describes it; `:191-193` says the promotion and the 2026-09-03 filings each renumbered the three defects; `:233-236` says the Third group opened on 69 at the promotion "but later filings renumbered the whole list". Entry 12 is 69 (`:238`), consistent.

R1-g fixed. Entry 2 at `:161-163` reads "a CANDIDATE Fable-lane instruction channel, unverified, would sit outside any mirror", matching the heading at `:518` and the body at `:538-559`.

R1-h partly fixed, or one instance of its class remains. Item 75's two cites into the notes are now by region and section name (`:565-567`, `:579-580`). But item 74 at `:419` still carries `model-prompting-notes.md:43-45` for the reasoning_extraction bullet, which at the amended head sits at `model-prompting-notes.md:79-81`. The only `5d20eed` in the file is the panel record's mirror line (`:514`); no sentence says item 74's cites are as of that commit. FIX: bind the cite ("at `5d20eed`") or name the bullet instead of a line range.

Internal consistency, checked: the status block's Open list (`:41-43`) matches every heading marked OPEN (headings at `:1777, :1864, :2875, :2904, :2979, :3059, :3291, :3345, :3400, :3436, :3469, :3495, :3526, :3565, :3702, :3732, :3780, :3922, :3960, :4254, :4411, :4491, :4517, :4629, :4899, :4936, :4968, :5033, :5117, :5165, :5277, :5325, :5373, :5466, :5541, :5579, :5606, :5644, :375, :518, :628, :729`), 42 entries both ways. Items 74 to 77 carry OPEN in their headings, ranking entries 1, 2, 11 and 23 name 74, 75, 77, 76 (`:155, :161, :223, :298`), and all four sit in the Open list. The whole-branch review's issue 7 is fixed: a blank line separates entry 11 from the Third header (`:230`), and entries 12 and 23 use four-space continuation (`:239, :299`).

One remaining contradiction, not touched by the amendment, named because the brief asks: entry 29 at `:334-337` says 33 "rides 32's" entry and "the total entry count is unchanged". `:100-101` says the ranking no longer carries an entry for 32, and `:36` lists 33 as done. So 33 rides an entry that does not exist. FIX: drop or past-tense the parenthetical. Low weight.

### G3: the session's own correction - PASS

Verified against the ranking text. Entry 29 at `:333-334` lists **29**, **26**, **34**, **35**, **28**, **27**, **37**. So 27, 28, 34, 35 and 37 each carry a ranking entry, and the old claim that they had none was wrong.

Every open item was matched to an entry: 74(1), 75(2), 49(3), 59(4), 67(5), 51(6), 31(7), 58(8), 43(9), 44(10), 77(11), 69(12), 46(13), 47(14 and 25), 45(15), 55(16), 70(17), 41(18), 39(19), 63(20), 36(21), 38(22), 76(23), 40(24), 66(26), 68(27), 53(28), 29/34/35/28/27/37(29), 54(30), 65(31), 64(32), 15(33), 12(34), 60(35), 61(36). Open items with no entry: 71, 72, 73, and only those. `:47-48` and `:62-64` ("three unranked items") are correct.

Two sentences in the rewritten paragraph are not supported by anything in the tree and are listed under UNVERIFIED below; neither changes the correction's truth.

### G4: the four pins - PASS

`test_multi_model_verify.py:1129` pins `### Fable 5.1`; `:1132-1133`, `:1139-1141` and `:1145-1146` pin the three sentences. Each needle matches the notes under the normalized read: `notes:28`, `:41-43`, `:47-49`, `:84-86`. The heading pin alone makes a revert to `### Fable 5` fail, because `### Fable 5.1` occurs only at `notes:28` and `test_seat_reshuffle.py:290`'s substring test would not catch it. The effort pin's needle changed from "the Fable 5 sweep does not carry" to "Fable 5 effort guidance does not carry" (`:1139-1141`, reason at `:1134-1138`); that is a rewording for R1-b/c, not a loosening, since the pin still fixes the whole clause. The docstring at `:1117-1122` names no version, closing the whole-branch review's issue 6. The dispatch pin `"exactly as printed"` at `:3539` matches `SKILL.md:214, :302` and `backup-lane.md:143, :205, :558`.

### G5: scope of the amendment - UNVERIFIED

Without a diff I cannot establish which files the amendment commit touched or that nothing outside three files changed. I do not fold this into the verdict.

### Disclosures

D-A: confirmed. `.superpowers/sdd/` holds no `*item74*` and no `2026-09-*` directory (both globs empty). `.superpowers/sdd/.gitignore:1` is `*`, so a ledger would be untracked in any case and its absence is a process gap, not a tree defect. It does not block merge on its own: the plan's own required verification is the pins and the gates, and the disclosure says those ran. It is item 59's class and item 59 is already open at `backlog.md:5033`.

D-B: not re-checked here; behavioural failures are outside what this lane can read. Nothing in the amendment touches a behavioural surface: the notes are a reference, the backlog is a record, and the test edit is a comment plus a needle reword.

## UNVERIFIED (kept out of every verdict)

- G5 entirely: the amendment's file set and the absence of unrequested changes. No diff available to this lane.
- `backlog.md:52-53`: "The 2026-08-22 script, re-run at `a3134dc`". No script about ranking coverage exists anywhere in the tree (grep for "unranked", "ranking entry", "27, 28, 34" outside the backlog returns only the whole-branch review), and I cannot resolve the commit hash. If no script exists, the sentence attributes the error to an artifact nobody can find.
- `backlog.md:56-57`: item 33 "closed as of 2026-08-31". Item 33's body (`:3234-3289`) carries no close date; only item 32's does (`:3212`).
- The base text of the Fable 5 section, so whether the three sentence pins would each fail on a byte-for-byte revert. The heading pin makes the revert fail regardless.
- `notes:30-32` "fetched 2026-09-03": a claim about an external fetch, not checkable from the tree.

## Verdicts

- G1: FIX. Remove or record the `stop_reason: "refusal"` literal at `model-prompting-notes.md:67-68`; the R1-a to R1-d fixes themselves stand.
- G2: FIX. Bind or de-number `backlog.md:419`; retire the "rides 32's" parenthetical at `:334-337`. The R1-e to R1-h fixes otherwise stand.
- G3: PASS. The correction is right and the measurement is reproducible from `:333-334` and the Open list at `:41-43`.
- G4: PASS.
- G5: no verdict; UNVERIFIED.

Branch, at amended subject revision `ced2f535e6223fd69114db68b3feaa0690ac9f96`: FIX, prose only. Three sentences, no code, no pin change, no behavioural surface. The amendment fixed everything round 1 named except one numeric notes cite in item 74, and introduced nothing I can see at head. D-A does not block.
