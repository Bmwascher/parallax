# Fable diff round 3, reply

Lane: same-harness, `parallax:fable-panel-reviewer`, read-only tool grant
(Read, Grep, Glob). Resumed from round 2. Subject revision `ee27f27`.

This is the reply that produced the panel SPLIT: it returned PASS on the
branch while the cross-vendor lane returned FIX, both having found the same
five stale cites. The disagreement is about OWNERSHIP, not about facts.
Note that this lane marked its own base arithmetic UNVERIFIED, which is
what prompted the session to read the base file rather than pick a lane.

Transcribed from the subagent result. This lane writes no reply file, so
this is a transcription and not a copy of an artifact. Angle brackets
arrived HTML-escaped through the agent transport and are restored here;
nothing else is changed.

---

## Round 3 verdicts on `ee27f273df18278fa003c7b2d3852e72d6e0e7f8`

Same tool limits as round 2: no diff, tree read at the amended head.

### H1: B1 to B6 - PASS

- B1: `docs/superpowers/plans/2026-07-27-0150-backlog.md:48-50` now says "never added to the ranking. They ARE in the Open list above"; the Open list at `:41-43` contains 71, 72, 73. Consistent.
- B2: `skills/multi-model-verify/references/model-prompting-notes.md:67-68` reads "can end a turn with a classifier refusal on benign code work". `stop_reason` no longer occurs anywhere in the file (grep: only `xhigh` hits remain, at `:129` and `:202`, both outside the Fable section).
- B3: `backlog.md:422-424` describes the bullet by content ("the bullet of `model-prompting-notes.md` that forbids instructing a Fable seat to echo its internal reasoning"), which resolves to `notes:79-81`. No numeric cite into the notes remains in items 74 to 77 (grep `model-prompting-notes\.md:\d` in the backlog hits only `:3480, :4994, :5291, :5308, :5322`, all in older items).
- B4: `backlog.md:337-341` now says 33 rode 32's entry and 32's entry was removed when 32 closed, "so neither is in the ranking now". Agrees with `:100-101` and the Done list at `:36`.
- B5: `backlog.md:53-59` states the sweep is not in the tree and the grouped-bullet explanation is inferred; only "the five carry entries" is stated flat, and that is what `:336-337` shows. `a3134dc` now resolves in the record as the 2026-08-22 `main` head (`docs/superpowers/plans/rounds/2026-08-22-item51-inline-brief-probe/probe-record.md:6`, `rounds/2026-08-22-item48-pwsh7-feasibility/feasibility-record.md:4`), so the commit reference is no longer unsupported; the sweep itself still is, and the text now says so.
- B6: `backlog.md:59-60` reads "DONE at its own heading"; item 33's heading at `:3234` says DONE, 0.28.0. No date is claimed.

No new error introduced by any of the six that I can find in the affected lines.

### H2: the two classes, swept - one class NONE in the branch's own text, the other has pre-existing instances the branch did not introduce

**Class 1: numeric cites into `model-prompting-notes.md`.** Shapes searched, repo-wide excluding `rounds/` (retained round artifacts are frozen records by design): `model-prompting-notes.md:<n>`, `notes.md:<n>`, `notes.md:<n>-<n>`, a bare `:<n>` or `` `:<n>` `` within 80 characters of "prompting-notes", "line(s) <n>" within 60 characters of "prompting-notes", and "(line" after "notes.md". Also "lines 28-70" in the plan.

Results in the branch's own changed text: NONE. Items 74 to 77, the notes, `SKILL.md`, `backup-lane.md`, `agents/`, `evals/` and `CLAUDE.md` carry no numeric cite into the notes. The plan carries "currently lines 28-70" at `docs/superpowers/plans/2026-09-03-item74-fable-51-notes.md:307`, which is a base-time statement inside a frozen plan and is correct for base (the section now spans `notes:28-114`, a shift of 44 lines for everything below).

Results outside the branch's text, at head, in living backlog items: four cites, all already stale BEFORE this branch and made staler by it:
- `backlog.md:3480` (item 38) cites `:288-291` for "'.codex/' stays unswept"; that text is at `notes:539` at head, so it sat at 495 at base. Already wrong at base.
- `backlog.md:5322` (item 66) cites `:343-345` for the same text. Same.
- `backlog.md:4994` (item 58) cites `:150` for `tools/codex-tool-surface-probe.ps1`; it is at `notes:212` at head, 168 at base. Already wrong at base.
- `backlog.md:5291` (item 66) cites `:350-355` for the tier-map parenthetical; it is at `notes:548` at head, 504 at base. Already wrong at base.
- `backlog.md:5308` cites `:46-52` as item 50's former resume-guarantee instance "fixed in that cycle", a historical reference bound to that cycle by its own wording.

These are item 69's class (`backlog.md:5466`), pre-existing, not this branch's. I do not fold them into the verdict; they belong under item 69 or a filing note. Dated plans and specs (`docs/superpowers/plans/2026-07-31-kimi-code-swap.md:267`, `2026-08-11-budget-flake-generator.md:166, :774`, `2026-08-11-tool-surface-agy-drift.md:480`, `2026-08-19-resume-not-guaranteed.md:334, :373`, `2026-08-30-item32-detached-dispatch.md:188`, `2026-08-31-completion-coupled-dispatch.md:2574`, `2026-07-26-seat-reshuffle.md:1682, :1693`, and five specs under `docs/superpowers/specs/`) also carry numeric cites into the notes; they are records of their own date and are listed here only because the shape matched.

**Class 2: literals in the Fable section that item 74 does not carry.** Shapes searched in `notes:28-92` (the rewritten text; `:93-114` is the pre-existing resume bullet passed in round 2): backticked tokens, quoted strings, URLs, dates, version and release numbers, file paths, `path:line` cites, item numbers, and named classes or hypotheses. Each was checked against item 74 (`backlog.md:375-516`) or a file I read.

Carried and verified: `model: fable` (`:385`), `test_seat_reshuffle.py` (`:386`), "two highest effort levels" (`:400-401`), `agents/fable-reviewer.md` and the mode-diff reference (`:402`), `agents/escalation-implementer.md` and the write-tool claim (`:409-410`), `fallbacks.md` (`:421`), `dispatch-options-costing.md:54-55` (`:427`, and the file itself at `:54-55`), item 47's shape (`:432-434`), item 55 (`:451-452`), reasoning_extraction (`:422`), `No transcript found`, 2.1.233, 0.25.0, the sdd progress path (`:459-462`), 2026-08-31 accounts rule (`:466-467`), nine clean resumes, three hypotheses, three candidates (`:463-471`), and "rewrites whole files ... more readily than 5 did" (`:406-407`).

Remaining shape matches, not carried by item 74: the guide URL at `notes:31` and "fetched 2026-09-03" at `notes:32`. Both are in the plan's draft (`plan:364-365`), both are external provenance in the same form the section's neighbour uses (`notes:118-120`, Opus 5), and neither states anything about the seats or the repo. I list them as the only instances of the shape and as UNVERIFIED facts, not as defects. With that said: NONE remaining of the defect the class names, a literal presented as repo-supported that the repo does not support.

### H3: backlog consistency - PASS, one observation, no contradiction

Re-checked at head: the Open list (`:41-43`) still matches every OPEN heading; the ranking (`:155-370`) still names every open item except 71, 72, 73, which `:47-50` states; items 74 to 77 are OPEN at their headings (`:375, :518, :628, :729`) and at entries 1, 2, 23, 11 (`:155, :161, :298, :223`); the "headings carry status" rule (`:18-24`) holds for all four.

Observation, not a contradiction: `:63-64` singles out 65 as "ranked while its heading says partially closed", while 26 is also ranked, at entry 29 "(its remainder)" (`:336`), with a PARTIALLY CLOSED heading (`:2717`). The sentence does not say 65 is the only such item, so nothing is false; a reader could take it that way. No FIX required.

Item 74's Problem paragraph still describes the base tree in the present tense (`:381-390`, `:420-424`, `:479-494`); the plan's post-debate step 4 (`plan:488-497`) commits to rewriting it at close, which round 2 accepted.

### H4: the disclosed deviation - PASS

The plan's Step 3 rule is at `plan:356-358`: every claim is carried from item 74, "do not add claims that item 74 does not carry". The draft at `plan:395-396` carries `stop_reason: "refusal"`, which item 74 does not (grep `stop_reason` in the backlog: no hit). So the draft violated the plan's own rule, and the shipped text at `notes:67-68` follows the rule over the draft. That is fidelity to the plan, not a departure from it. Nothing pins the literal (`test_multi_model_verify.py:1129-1146` pins four other phrases). The same treatment already stands for two accepted deviations: the effort bullet (`plan:375` "Effort must be re-swept" versus `notes:46`) and the test (`plan:325-346` has no heading pin and a "0.29.0" docstring versus `test_multi_model_verify.py:1116-1129`).

One factual note on the disclosure's reasoning: the plan has been edited on this branch after the whole-branch review. `docs/superpowers/plans/rounds/2026-09-03-item74-diff-debate/whole-branch-review.md:47` cites the "After the tasks" section as `plan:479-493` with no close step; at head it spans `plan:479-503` and step 4 closes item 74. Which commit did it is UNVERIFIED without a diff. It does not change the H4 verdict.

### H5: scope of the amendment - UNVERIFIED

No diff available. Nothing I read outside the backlog and the notes shows a change since round 2 (`test_multi_model_verify.py:1116-1146`, `:3531-3539`, `tools/dispatch-round.ps1:588-592`, `SKILL.md:200-202, :214, :302`, `backup-lane.md:143, :205, :558` all read as in round 2), which is consistent with the claim but does not establish it.

## UNVERIFIED (kept out of every verdict)

- H5: the amendment's file set.
- The existence and code of the 2026-08-22 sweep (`backlog.md:53-58` now says so itself).
- `notes:30-32`: the guide URL and the 2026-09-03 fetch, external facts.
- Which commit added steps 4 to 6 to the plan's "After the tasks".
- The four pre-existing stale notes cites in items 38, 58 and 66 were stale at base by arithmetic from the plan's stated base extent (`plan:307`), not from a base read.

## Verdicts

- H1: PASS.
- H2: PASS for the branch. Class 1 has NONE in the branch's text and four pre-existing instances in items 38, 58, 66 named above for item 69. Class 2 has NONE of the defect; two provenance literals listed by shape.
- H3: PASS.
- H4: PASS.
- H5: no verdict; UNVERIFIED.

Branch, at amended subject revision `ee27f273df18278fa003c7b2d3852e72d6e0e7f8`: PASS. Every round-2 finding landed, the two classes are clean in the branch's own text, and the only remaining findings are pre-existing item 69 instances outside the branch's scope. The absent SDD ledger stands as disclosed and does not block.
