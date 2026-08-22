# Fable whole-branch review — retained range-bound artifact

**Seat:** `parallax:fable-panel-reviewer`, agent `a72e3059fab1937a1`.
**Tool grant:** Read, Grep, Glob only. Read-only; cannot execute. Every
round states its own UNVERIFIED list rather than letting a read stand in
for a run.

**Subject range:** base `a3134dc` (`git merge-base main HEAD`), final head
`bfb018f`.

**Terminal verdict: PASS on `bfb018f`.**

This artifact holds the reviewer's replies VERBATIM, extracted
programmatically from the agent transcript rather than retyped. Four
exchanges: one whole-branch review returning FIX, and three confirmation
rounds, each bound to the fix range named below. Rounds 1, 2 and 3 each
returned FIX and each found a real defect; round 4 returned PASS.

The session adjudicated every finding with evidence before any reviewer
lane saw it. All findings across all four rounds were ACCEPTED; none was
refuted, none escalated. The per-finding adjudications and the controller's
independent reproduction of each are in the SDD ledger at
`.superpowers/sdd/2026-08-22-item48-pwsh7-feasibility/progress.md`.

| Round | Range reviewed | Verdict | What it found |
|---|---|---|---|
| 1 | `a3134dc..1bb7b24` | FIX | The predicted fifth instance of the branch's own defect class, twice: a claim asserted and refuted in the same document, and TSV citations stale by the exact rows an earlier fix inserted. Plus two minors. |
| 2 | `1bb7b24..d0ceec2` | FIX | The self-quoting trap fired on the fix: five citations of the record's OWN line numbers, four introduced or carried by that fix. Disclosed one of the five as its own round-1 miss. |
| 3 | `d0ceec2..7d0ab9a` | FIX | The convention paragraph written to end the class was itself wider than the practice under it: five surviving self-citations in a spelling neither sweep counted. |
| 4 | `7d0ab9a..bfb018f` | PASS | No eighth instance. Stated as an honest floor after being told explicitly to give one rather than reach for another finding. |

---

## Initial whole-branch review — range `a3134dc..1bb7b24`

# Whole-branch review — item 48 PowerShell 7 feasibility

**Reviewer:** Fable panel lane, read-only tool grant (no Bash, no Edit, no Write). Every "run it" instruction in the dispatch was satisfied by mechanical counting with the search tools where counting is equivalent, and is listed under UNVERIFIED where it is not.

**Subject revision:** base `a3134dc`, head `1bb7b24`, per the diff package `.superpowers/sdd/2026-08-22-item48-pwsh7-feasibility/fable-package-a3134dc..1bb7b24.md`.

---

## What I swept for

The repo's named defect class: a claim stated more widely than its evidence, an unmade measurement reading as clean, and the class's execution-time variant, a correction applied at one site while the same claim stands at a sibling site. Swept across: the verdict and all five conditions, all five measurement sections, the inventory's must-change and unknown lists, the residual-limits section against its own bucket table, the migration draft's ordered work against the condition list, `survey.py`'s comments against its code, and roughly 40 `path:line` citations across 15 target files.

**The predicted fifth instance exists. I found it twice, in two independent forms (Issues 1 and 2 below).**

---

## Strengths (each verified, not assumed)

- **Global Constraints hold exactly.** All 56 paths in the range are ADDs under `docs/superpowers/plans/` (diff package name-status, lines 46-103). Nothing under `tools/`, `evals/`, `skills/`, `hooks/`, `.githooks/` or `.github/` was touched, so no 5.1 test was deleted, skipped or xfailed anywhere in the range.
- **The residual bucket table is correct.** I hand-counted the `- ` bullets in `feasibility-record.md:2045-2205` per `###` bucket: 8 / 5 / 3 / 4 / 4 / 6 / 4, total 34, closing-gate subsection 0 — identical to the published table at `feasibility-record.md:494-503`. Every one of the 34 is walked in a criterion sweep or the none-bearing subsection.
- **The classification-counts table is current.** Emulating the published awk with per-field counts on `entry-points.tsv`: 609 / 227 / 106 / 54 / 46 / 31 / 15 / 13 / 7 / 5 / 1, sum 1114 = total non-comment rows. All eleven match `feasibility-record.md:667-678` exactly.
- **The load-bearing counts are exact, not approximate.** 83 rows end `\tmust-change`, 3 end `\tunknown` — matching "at least 83 ... plus 3" everywhere it is cited, and the 78-distinct-lines vs 83-rows arithmetic closes (five dual-family lines each named as such: `.githooks/pre-push:24`, `check-drift.ps1:96`, `doctor.md:340`, `SKILL.md:326`, `stub-appserver.cmd:14`).
- **Measurement 1's table is a faithful transcription.** All eight arms in `reexec/results.json` match `feasibility-record.md:1004-1013` field for field, including the two corruption rows (`stage_b_child_count: 8` of 10; `routeNote` stripped to `a quoted note — here`; `path` ending `space"`). `run.py:22-23`, `:63`, `:112` pin exactly what the record says they pin.
- **Citations are overwhelmingly exact.** Of ~40 spot-checked: `kimi-lane-lock.ps1:887`, `test_backup_lane.py:270`, `backup-lane.md:111`, `hooks/hooks.json:10`/`:22`, `test_lock_protocol_live.py:63-91`/`:379-400`, `test_codex_tool_surface_probe.py:514-529`, `README.md:412-414`, `skill-evals.yml:59-125` (all eleven modules confirmed in both steps), `check-drift.ps1:21`/`:68`/`:96`/`:987`/`:1054`/`:1060`, `drift_statemachine_tests.ps1:542`/`:552`/`:1275`/`:1283`, `check_workflow_paths.py:85`, `test_attestation.py:10`/`:30`/`:36`, `stub-appserver.cmd:14`, `agents/flash-implementer.md:47`/`:78`, `probe-record.md:139-161` (31995 exact / 32967 throws), backlog `:3748`/`:3750` — all correct. The exceptions are Issue 2 and Issue 3.
- **All five verdict conditions have ordered-work coverage** (`feasibility-record.md:2243-2300`: step 1 carries conditions 1, 2 and 5; step 2 carries 4; step 4 carries 3), and the count "five" is consistent at every site I found (`:519-543`, `:561`, `:2229-2236`, `:2327`). The prior instance-3 defect is genuinely fixed.
- **The guard widening is behaviorally sound.** Dropping `EXEMPT_PREFIXES` (`survey.py:265` vs plan line 538) is strictly tightening: the only prefix row is `docs/`, and a `.py`/`.ps1` refused prefix coverage anywhere else fails loud as UNCLASSIFIED, never silently. The "latent on this branch" claim checks out: `docs/` holds exactly the 7 `.py`/`.ps1` files the comment enumerates, all with explicit rows (e.g. `entry-points.tsv:218-222`).

## Issues

### FIX 1 — A correction issued in Measurement 5 leaves the refuted claim standing at three other sites

`feasibility-record.md:1837-1857` (Measurement 5 Step 6) records, as a checked correction: `ps_host()` FAILS rather than skips (`test_lock_protocol_live.py:69-73`, verified), `test_lane_credential_live.py`'s `host()` fixture fails too, so `required_hosts()` is NOT "the only one that FAILS instead"; and the "single strongest piece of host-presence evidence" superlative was "dropped rather than re-attributed." The narrow true claim is stated at `:1859-1866` (only resolver demanding BOTH hosts).

But the refuted framing still stands, uncorrected, at:

- `feasibility-record.md:1155-1157` (Measurement 2): "the only host-selector in this repo that FAILS rather than skips when a host is missing, making a pass of that module the strongest host-presence evidence this record has";
- `feasibility-record.md:1469-1472` (Measurement 3, item c): "the only host-selection function found anywhere in this repo's test suite that FAILS rather than skips ... the strongest single piece of host-presence evidence this record has found";
- `feasibility-record.md:1529` (Measurement 3 Summary): "the strongest single piece of coverage evidence in this whole record."

Why it matters: this is the exact shape of prior instance 4 (fix at one site, stale twin beside it), and the record now asserts and refutes the same claim in one document. It does not change any criterion status — even the corrected claim leaves the cited green run as proof both hosts were present — but the record's authority rests on not doing this.

### FIX 2 — Two `entry-points.tsv` row citations went stale by exactly the 3 rows the final review's own fix inserted

- `feasibility-record.md:1214-1215` cites the `hooks/hooks.json` launch rows at "`entry-points.tsv` ... `:424-425`". Actual: `entry-points.tsv:427-428` (verified; `:424-425` now hold `run_behavioral_evals.py:741` and `skill_scanner.py:52`).
- `feasibility-record.md:1324` cites the `stub-appserver.cmd` rows at "`entry-points.tsv:70`/`:220`". Actual: `:70` (host) and `:223` (launch); `:220` now holds a `survey.py` row.

Cause, established from the record's own narration: the final-review Important-3 fix added 3 rows for `survey.py`'s rewritten comment (`entry-points.tsv:219-221`; the +3 is narrated at `feasibility-record.md:652-658`), shifting every later row down by 3. The fix refreshed the classification table but not the record's own row-number citations — the same shape as prior instance 4, produced by the head commit's own fix-up cycle. Nothing mechanical checks record-to-TSV row citations (the survey checks target-file digests, not these), so only a sweep catches it.

### Minor 3 — Misdescription in the must-change list at the `test_multi_model_verify.py` bullets

`feasibility-record.md:786-790` groups `:2954`, `:2961`, `:2999` as "`os.name != "nt"` skip-reason strings and comments." Verified: `:2954` is a skip reason, but `:2961` and `:2999` are the live `["powershell.exe", ...]` interpreter lines themselves — the very hardcoding the bullet attributes to "the next bullet" (`:2960`/`:2962`/`:2998`/`:3000`, which are the `subprocess.run` scaffolding and `-File` lines). Migration values are correct on all seven rows; the what-this-line-is half of two entries is wrong, in a list whose stated format is "path:line — what a migration must do to it."

### Minor 4 — The widened guard's comment states its invariant wider than the code enforces

`survey.py:150`: "A prefix row NEVER covers an EXECUTABLE file, anywhere under `docs/`." The code (`survey.py:182`, `:265`) tests the suffixes `.py`/`.ps1` only. An executable that is neither — the repo has a live `.cmd` executable class, `stub-appserver.cmd:14` — placed under `docs/` would be swallowed by the `docs/` prefix row as "record - never executed," the exact attestation the comment forbids. Latent today (the 7-file enumeration holds), and the widening itself is sound; but the widening's own justification was closing the gap between the stated invariant and the enforced one, and a gap remains for non-`.py`/`.ps1` executables. One sentence naming the suffix boundary as a known limit, or adding `.cmd` to the tuple, closes it.

### Nit

- `feasibility-record.md:679`: "One row of the 7481 hits is a prefix row" — a row is not a hit; the sentence's own continuation says it correctly.

## UNVERIFIED (this lane cannot execute)

- `python survey.py` exiting 0 with `7481 hits ... 0 unclassified, 0 stale, 0 files not scanned` (`feasibility-record.md:615-621`, `:632`): no Bash in this seat; digests are not recomputable by reading. All structural proxies pass (1114 well-formed rows, one prefix row, vocabulary spot-checks clean).
- The `gh`-derived CI evidence: run `32391262449`, `773 passed` per host, and the five-run step-timing table (`feasibility-record.md:1746-1752`). External service, not re-queried.
- The closing-gate suite lines (`:2196-2198`): taken from the dispatch brief's own attestation (2558/14 per host), per the do-not-re-run instruction.
- The Microsoft install-documentation quotation (`:1224-1233`): URL not fetched.

None of these is folded into the verdict below; each is corroborated by an independent record artifact or declared by the brief.

## Triage of the deferred minors and rulings

- **Ledger 151** (Windows CI claim rested on the conclusion field): CLOSED by later work — Measurement 3's direct log re-pull (`feasibility-record.md:1280-1290`) carries the step-log evidence. Note its companion sentence at `:1152-1158` is one of Issue 1's three sites; fix Issue 1 without losing the log evidence.
- **Ledger 186** (stale classification table): CLOSED — table verified exact above.
- **Ledger 168** (citation-drift sweep): the NO-criteria section is verbatim-clean against the plan skeleton; the drift class instead materialized as Issue 2. Fix those two citations; nothing else in that section drifted.
- **Ledger 206** (sweep scope understated): drop — understatement is the safe direction, and `:1895-1896` names the actual commands.
- **Ledgers 114, 125, 143** (classification judgment nits, splat-parent clause): drop — no migration value moves, criterion 1 is UNKNOWN regardless, and the splat-parent clause is sound because the target was constant across all eight arms (`run.py:63`/`:112`, verified).
- **Ledgers 74, 75**: absorbed mid-branch / cosmetic — drop.
- **Task 9's two ruling-deferred items**: the attribution slip belongs to the same family as Issue 1 — fold into that fix. The gate-log host label: drop with reason — the record text at `:2192-2205` names host and counts per line; the unlabeled raw log is scratch, and a 40-minute re-run buys nothing the record does not already state.
- **Rulings 1-10 plus the unnumbered Task 9 ruling**: each checked against its stated reason; none overrode plan text improperly. Ruling 2's withdrawal was correct — the plan mandates the three-way split, and commits `5f78c4c`/`f459efe`/`4f511b3` show it executed in the plan's order. Rulings 9/10 (name the `README.md:412` miss, do not widen the filter) match the plan's own remedy-for-a-known-miss pattern and are honestly carried at `:920-937`.

## Verdict

Per plan task: Tasks 1-8 **PASS** (each section present, in order, delivering what its task specifies, with the mechanical tables verified above). Task 9 **FIX** — the verdict logic, conditions and rule application are sound and I do not contest CONDITIONAL, but Issues 1 and 2 sit inside the record Task 9 owns at freeze.

**Subject as a whole: FIX**, on the branch at head `1bb7b24` (base `a3134dc`). Two specific fixes, both prose-only, both inside `feasibility-record.md`: (1) reconcile `:1155-1157`, `:1469-1472` and `:1529` with the Measurement 5 correction at `:1837-1866`; (2) repoint the TSV citations at `:1214-1215` to `:427-428` and at `:1324` to `:70`/`:223` — and while there, sweep the record for any other `entry-points.tsv:<n>` citation written before the +3 insert (I found only these two, and `:70` was unaffected because the insert landed above line 219 only). Minors 3 and 4 are worth one line each in the same pass. Nothing found invalidates a measurement, a criterion status, the five conditions, or the CONDITIONAL verdict; after these fixes I would PASS this branch without a further round.

---

## Confirmation 1 — range `1bb7b24..d0ceec2`

# Confirmation round — head `d0ceec2`

Fix diff read in full (`.superpowers/sdd/2026-08-22-item48-pwsh7-feasibility/review-1bb7b24..d0ceec2.diff`), every changed site re-verified against the working tree.

## The four findings and the nit: all confirmed fixed

1. **Refuted-uniqueness sites (was FIX 1) — fixed at all three.** `feasibility-record.md:1161-1167`, `:1478-1485`, `:1538-1543` now state the fail-not-skip property without the uniqueness claim and point at Measurement 5 Step 6. The Measurement 2 argument still does its work on the weaker premise: `required_hosts()` fails when EITHER host is missing (`test_lock_protocol_live.py:83-89`, verified round 1), so a green run of that module proves both hosts present — uniqueness was never load-bearing, and the rewrite says exactly that. Deferred minor 151's log evidence survived intact (`feasibility-record.md:1292-1293`, the `773 passed` per-host re-pull).
2. **Stale TSV citations (was FIX 2) — fixed, and correct at the CURRENT tsv, including the second shift.** `feasibility-record.md:1224` cites `:429-430`; actual `entry-points.tsv:429-430` are the `hooks.json` launch rows. `feasibility-record.md:1334` cites `:70`/`:225`; actual `:70` (host) and `:225` (launch) are the `stub-appserver.cmd` rows. No other `entry-points.tsv:<row>` citations exist in the record (swept).
3. **Must-change grouping (was Minor 3) — fixed.** `feasibility-record.md:791-801`: `:2954` alone as the one genuine skip-reason; `:2960-:2962`/`:2998-:3000` grouped as the two calls with `:2961`/`:2999` named as the actual hardcode. Matches the source as I verified it in round 1.
4. **`.cmd` guard (was Minor 4) — fixed the right way, and the red-survey diagnosis checks out.** `survey.py:192` now reads `EXEMPT_SUFFIXES = (".py", ".ps1", ".cmd")`. I verified the diagnosis against the regexes rather than accepting it: new comment lines `survey.py:185` and `:191` each carry a backticked `.ps1`, which the bare family's `` `[^`]*\.ps1[^`]*` `` alternative matches — exactly the two new rows (`entry-points.tsv:222-223`, both `not-a-launch`/`no-change`); line `:184` (backticked `.py`) and `:188` (`stub-appserver.cmd`) match no family, correctly rowless. The one stale-row correction is `survey.py` old `:193` → `:203` at `entry-points.tsv:224`, digest `1b706a0a35f8` unchanged over the net +10-line comment insert — consistent, since the line's text did not change. The widening stays strictly tightening: the only prefix row is `docs/`, and a refused file fails loud as UNCLASSIFIED.
5. **Nit — fixed.** `feasibility-record.md:683`: "One of the 1116 rows is a prefix row."

## Numbers as they now stand

My independent read-only recount of `entry-points.tsv`: **1116** non-comment rows; **611** `not-a-launch`; `must-change` + `unknown` = 86 (83 + 3, both unchanged); the other ten classes sum to 505, matching the published table exactly. The record carries 7484 at `:633`, `:637`, `:685` and 1116 at `:660`, `:683`, `:685`, `:940`; the history chain 1078 → 1111 → 1114 → 1116 (`:657-660`) is arithmetically consistent (+33, +3, +2); no stray 7481 and no non-historical 1114 remain. This agrees with your stated run values everywhere I can check. UNVERIFIED by me, as before: `SURVEY_EXIT=0` and the live `7484 hits ... 0 stale` line themselves — this seat cannot execute; the TSV-side halves of those numbers are verified.

## New breakage the fix introduced — the self-quoting trap fired on the fix itself

**One finding, three sites plus one carried site: the fix's new internal cross-references cite record line numbers that the fix's own insertions moved.**

- The three new cross-references (`feasibility-record.md:1164`, `:1482`, `:1542`) cite the Measurement 5 Step 6 correction at "`:1837`-`:1866`". The fix added a net +13 lines above that block, so it moved: "Correction to an earlier draft" now starts at `:1850` and the narrow claim at `:1872`; the block is `:1850-:1879`. All three citations point 13 lines high, into the tail of the bilateral sweep.
- `feasibility-record.md:1161` retains "`:1463`-`:1471`" for Measurement 3 item c, inside a sentence this fix rewrote. That was correct at `1bb7b24`; item c now starts at `:1473`. Stale by 10, carried through the edit.

**Pre-existing, disclosed as my own round-1 miss, not new breakage:** `feasibility-record.md:1833-1836` (Measurement 5 Step 5) cites "`feasibility-record.md:369`-`:370`" and "`:377`-`:378`" for sentences that actually sit at `:944` and `:951-952` — stale since Task 9 inserted the ~550-line verdict at the top of the file, so it was already wrong at `1bb7b24`. My round-1 citation sweep covered ~40 target-file citations and did not cover the record's citations of itself; I state that plainly rather than folding it in as new.

**Recommended shape of the repair, because a fourth firing is otherwise likely:** do not repair these with fresh absolute line numbers — every edit to this file moves the numbers the edit describes, which is now a three-times-measured fact about this document. The record already uses stable section anchors ("`## Measurement 5` Step 6"); drop the `:NNNN` halves at the four internal sites (and repoint `:1833-1836` to the "What this method cannot see" bullet by name). A section-anchor citation cannot go stale under insertion, and this converts the trap's fifth instance into its structural fix. If line numbers are kept instead, they must be re-derived after the last edit lands, and re-checked by grep.

## Verdict

**FIX**, on head `d0ceec2` (base `a3134dc`) — narrow and mechanical: internal record-to-record line-number citations at `feasibility-record.md:1161`, `:1164`, `:1482`, `:1542` (introduced or carried by this fix) and `:1833-1836` (pre-existing, my round-1 miss). All four accepted findings and the nit are correctly and verifiably fixed; every number I can verify without execution now agrees with the stated run values. Nothing here touches the CONDITIONAL verdict, any criterion status, or any measurement. After the citation repair — which I can confirm by grep alone if section anchors are used — this is a PASS without a further full pass.

---

## Confirmation 2 — range `d0ceec2..7d0ab9a`

# Confirmation round — head `7d0ab9a`

Diff read in full (one file, `feasibility-record.md`, +29/−12); every changed site re-verified against the working tree by grep, as offered.

## The five sites: confirmed

- `feasibility-record.md:1171-1176` (Measurement 2): both former line-ranges replaced — item c named by content ("the `ConvertFrom-Json` type-divergence test") and the Measurement 5 Step 6 correction cited by its bolded lead sentence. The argument's logic is unchanged and still sound.
- `feasibility-record.md:1493-1495` (Measurement 3 item c): anchor in place.
- `feasibility-record.md:1556` (Measurement 3 Summary): anchor in place.
- `feasibility-record.md:~1849` (Measurement 5 Step 5): now cites `### What this method cannot see`'s `README.md:412` bullet and that sub-heading's closing paragraph — both targets exist and carry the quoted sentences (verified at the bullet and closing paragraph in round 1, re-confirmed by the quote match).
- The anchor target resolves: the bolded lead "**Correction to an earlier draft of this section, recorded rather than silently fixed**" stands at `feasibility-record.md:1867` and the quoted wording at all three citing sites matches it exactly.

**No `:NNNN` self-citation survived**: greps for `:1837`, `:1866`, `:1463`, `:1471` and `feasibility-record.md:<digit>` all return zero. The convention paragraph is present at `feasibility-record.md:603-611`, in `## Method`.

**No functional breakage**: I checked every added and removed line against the three family regexes — no host token, launch verb, or bare-family shape was introduced or removed, which corroborates (read-only) your re-run holding at 7484 with the table unchanged. The convention paragraph is bold prose, not a heading, so the 11-heading count is undisturbed. Your `SURVEY_EXIT=0` and gate outputs remain UNVERIFIED by me directly, as before; nothing I can read contradicts them.

## One new finding — the convention overstates, and five self-citations in a different spelling survive

You asked me to check that no self-citation survived. Five did, in a shape outside the class both prior sweeps counted:

- `feasibility-record.md:264` — "already scoped by this record's own header (lines 4-5)"
- `feasibility-record.md:1124` — "the record's own header (line 5)"
- `feasibility-record.md:1154` — "record's own header (line 4)"
- `feasibility-record.md:1225` — "this record's header (line 5)"
- `feasibility-record.md:1296` — "header (line 4)"

These are self-citations by line number written as "(line 4)", not as backticked `:NNN`, so a sweep keyed on the backtick spelling could not see them — two independent counts agreed because both counted the same too-narrow class. All five are currently ACCURATE (record lines 4-5 do hold the repo and hosts facts) and their drift risk is near zero, since every edit in this record's history has landed below the header. But the new convention at `:603` says "this record cites itself by section anchor, **never by line number**" — and the document now contradicts that sentence five times, four of them below the paragraph that states it. That is the hunted shape — a rule stated wider than the practice under it — introduced this round, inside the paragraph created to end it.

Two equally acceptable one-edit repairs, either confirmable by grep:

- Narrow the convention by one clause: the header's opening lines are the stated exception, cited by line number because every edit in this record's history lands below them; or
- Convert the five cites to the anchor form ("the header's Hosts line", "the header's cut-point line") and leave the convention absolute.

## Verdict

**FIX**, on head `7d0ab9a` (base `a3134dc`) — one edit, in one file: reconcile the convention paragraph at `feasibility-record.md:603` with the five "(line N)" header self-citations, in either direction above. Everything else in scope is confirmed: the five repaired sites are correct and anchor-resolved, no `:NNNN` self-citation survives, and no functional or numeric breakage was introduced. After that single reconciliation — which I can confirm with one grep — this is a PASS on the record as a whole, and nothing in any round has touched the CONDITIONAL verdict, its five conditions, or any measurement.

---

## Confirmation 3 (terminal) — range `7d0ab9a..bfb018f`

# Confirmation round — head `bfb018f`

## The five conversions: confirmed

- `feasibility-record.md:264-265` — "(lines 4-5)" is now "the `Repo:` and `Hosts under test:` lines"
- `feasibility-record.md:1124` — "header's `Hosts under test:`" (line named by content)
- `feasibility-record.md:1155` — "header's `Repo:` line names as the branch cut point"
- `feasibility-record.md:1226` — "header's `Hosts under test:`" line
- `feasibility-record.md:1298` — "header's `Repo:` line"

Both anchor targets exist and are unique as line-leading phrases: `Repo:` at `feasibility-record.md:4`, `Hosts under test:` at `:5` (every other occurrence is a backticked reference to them, not a second target). All five citations remain factually accurate to what those lines carry.

## The convention's truth against the document under it

Zero `(line N)` or `(lines N-M)` matches remain. Zero backticked `:NNNN` self-citations remain (re-confirmed from last round's greps, which still hold — this diff touched none of those sites). The one bare "line N" hit, `feasibility-record.md:1355` ("it is line 6 of that listing"), I read myself: it indexes into the `git ls-files '*.ps1'` output named earlier in the same sentence, not into this record — and as it happens it is also verifiably correct, since `git ls-files` output is path-sorted and the four `docs/.../reexec/*.ps1` files plus `stub-appserver.ps1` precede `stub-codex.ps1` at exactly position 6. Not a self-citation, no action.

So the absolute convention now matches the document's practice, with three sweeps of three different spelling classes behind it. On your reasoning for rejecting the exception clause: you were right and my first-listed option was the weaker one. An exception resting on "every edit so far has landed below the header" is a statement about the past dressed as a guarantee about the future — the defect class one level up, written into the rule meant to end it. The direction chosen removes the exception instead of justifying it, which is the only form that stays true under any future edit.

## New breakage

None found. The replacement text introduces no token matching any of the three survey families (`Repo:`, `Hosts under test:`, and the surrounding prose match neither the host, launch, nor bare regexes), and removes none, which corroborates — read-only — your re-run holding at 7484 hits and 1116 rows. No headings were added or removed. Nothing new cites anything by a number that this edit moved.

UNVERIFIED, as in every round, by tool grant rather than by doubt: `SURVEY_EXIT=0` and the live gate outputs are your measurements; everything I can check without executing agrees with them.

## Verdict

**PASS**, on head `bfb018f` (base `a3134dc`).

That is the honest floor, not a courtesy: I swept the scoped surface — the five conversions, the convention against every spelling of self-citation three hunts have produced, and the diff's own additions against the family regexes — and there is no eighth instance to report. What remains open is exactly what the record itself declares open: the five CONDITIONAL conditions, which are the subject's findings, not its defects. Spec fidelity holds, the Global Constraints held through all four fix rounds (every commit touched only the record directory), and the fix chain closed each finding in the direction that stays true under future edits. This branch is merge-ready.

---
