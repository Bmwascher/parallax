# Second-reader verification of the backlog rewrite

Read by a different agent from the one that wrote `BACKLOG.md`. The old
text is `docs/superpowers/plans/2026-07-27-0150-backlog.md` at commit
`d19a5ca`, 5,905 lines, read in full. The new file is `BACKLOG.md` at
`1802eae`, read in full. The Task 10 report was treated as claims, not as
evidence; every row below was checked against the two texts.

83 items: 32 DONE, 1 GONE, 3 PARTIAL, 47 OPEN.

## Step 1: every closed item

`| id | resolution matches? | record matches? | note |`

| id | resolution matches? | record matches? | note |
|---|---|---|---|
| 1 | yes | yes | the old item carries NO resolution text, only a problem and a shape-of-fix; the new resolution is built from the old header list (`1a014b5` plus `c6b7c85`) and from item 5's "the coverage checker shipped in 0.15.0". `Record: c6b7c85` is the commit the old header names for the 0.15.1 half, matching `Closed: 0.15.1` |
| 2 | yes | yes | `Write(**)`, the toast and its two remedy classes, the reason riding the pending entry, the runner's stderr, BLOCKED requiring `$agentExit -eq 0`, three new scenarios plus the `no-verdict` assertion: all present |
| 3 | yes | yes | names the failing field, route note an exact token, pass rule untouched, three tests re-pointed |
| 4 | yes | yes | Record is the design spec the old resolution names; the constraint's "deletion is still committed there" is kept, which item 75 cites |
| 5 | yes | yes | observed truth, `rotation-guard-identity`, creation time beside the byte offset, coverage checker caught all three consequences |
| 6 | yes | yes | order binding, live concurrent-session verification, lane lock narrowed three times, residual answered YES by 0.18.0 |
| 7 | yes | yes | premise FALSE, 128 to 3, `node_repl` survives, `-c mcp_servers={}` inert, disabled-vs-failed indistinguishable, two-pass probe, present=detection / absent=mitigation, proxy handed to item 39 |
| 8 | yes | yes | brief-hash rule, inline not file-planted, truncation did not reproduce. Record policy note: `Record:` is item 13's live-debate record while the body names `tools/read-kimi-round-evidence.ps1`; the record is where the 2026-07-31 measurement lives, so it is defensible, but the file is not consistent about record-vs-artifact (see concerns) |
| 9 | yes | yes | 498/512 and 780/792 and the two mutant counts are exact. The old text announces "Three things the exercise taught" and then lists FIRST to FIFTH; the new three drop the declared-fault-model lesson. The old header was already self-inconsistent, so this is compression of a defect, not a new one (see concerns) |
| 10 | yes | yes | dual-host job, four implementer points settled, non-silent skip, the vacuously-true first oracle kept |
| 13 | yes | yes | eleven tasks and the live two-round proof; drops the three live probe rounds and the doctor check-8 rewrite, which is compression |
| 14 | yes | yes | 5810 of 11874, `-z` chosen, inverted rename order, 2 of 87 ASCII names quoted, `core.quotepath=false` a no-op. `Closed: record` with a commit `Record:` is the brief's own header decision |
| 16 | yes | yes | GONE, not fixed; 832 lines deleted; `test_deleted_machinery_does_not_return`. Same record-policy note as item 8 |
| 17 | yes | yes | YES the root is reachable, SUPPRESSED BY THE FLAG, positive control and canary-absent baseline, lane not open in the measured configuration, three shipped changes |
| 18 | yes | yes | 600-character render cap, the intermittency mechanism, 2400-character cap for both shell tools, 10 of 12 with expectation 1 at zero |
| 19 | yes | yes | three bands and the two constants, the FALSE growth claim, 5404 to 5069 to 5227, fourth relocation refused, `len(body) // 4`, the fail-first fixture |
| 20 | yes | yes | stdin plus client-echo binding, the 5.1 splatting measurement, rollout not transcript, 49 oracles, both NOT-covered limits |
| 21 | yes | yes | pre-copy length check, 259/260 boundary pair, the limit is policy not a maximum, `\\?\` ruled out |
| 22 | yes | yes | status output does not detect an ignored-file edit, fingerprint widened to content, and all four NOT-covered limits |
| 23 | yes | yes | one paragraph, three pins watched to fail, nothing enforces it, item 27 named |
| 24 | yes | yes | 4 consecutive contested, reset on acceptance, separate fix-verify budget that pauses, the sketched predicate replaced by an adjudicated dry round, both overruns named |
| 25 | yes | yes | SAME CLASS and VERIFICATION SURFACE as operational definitions, unit named before the end, FIX/ESCALATE/narrowed claim |
| 30 | yes | yes | both defects in series, script-scope `$OutputEncoding` with the `& { }` wrong fix pinned, three whole-payload live tests, all three unguarded sites named with their classes |
| 32 | yes | yes | the tool and its two modes, the exit code IS the classification, the measured killed round, the WITHDRAWN headline claim, 5 + 7 rounds, items it opened. Drops the attested head `15f85ec`, the install verification and the plan's DEGRADED verification status (see concerns) |
| 33 | yes | yes | prompt removed, report not question, the "Skip Sol" option removed with it, and everything the fix must not lose |
| 42 | yes | yes | both acceptance paths, the five-field closed set with three required, the moved validation, the still-unmeasured refresh trigger |
| 48 | yes | yes | CONDITIONAL, 5.1 not dropped, five conditions, the twice-corrected survey, the cost and the attested head. The `~32000-character` ceiling and the fallback-transport alternative were dropped and are restored by this reader |
| 50 | yes | yes | probe did not reproduce, nine resumes on 2.1.237, low power stated, load-bearing evidence unchanged, candidate 1 refuted, floor scoped, the class reproduced three times inside its own fixes, 67 and 68 filed |
| 52 | yes | yes | one canonicalization, only the Kimi lane moved, `ConvertTo-CanonicalBrief`, the diagnostic may not say the content differs, both outcomes refuse |
| 56 | yes | yes | three independent shape clauses, no value compared and why, and all three still-open points named in `codex-brief-binding-fresh-record` |
| 57 | yes | yes | (c) in 0.25.0 with the overlooked IDENTITY path, (a) `\z` for `$`, (b) `Get-EnvDate` canonicalization, and why (a) stopped being diagnostic |
| 62 | yes | yes | filter-not-compare, round 1 refused and round 2 half-refuted it, each width safe where the other is not, the class sweep, the three consumption sites, 60 sessions / 32437 records |
| 74 | yes | yes | Fable 5.1 rewrite with four pins, both dispatch-contract defects, nine rounds, attested at `fa86675` then merged UNATTESTED, both corrections, the dead resume hypothesis, items 80 and 81 |

## Step 2: the PARTIAL remainders

| id | remainder matches? | note |
|---|---|---|
| 11 | yes | old "What stays OPEN" is the security contract plus `allowNonWorkspaceAccess` and item 36's two questions; the new `**What remains.**` carries both and adds the two deliberate narrowings (no version floor, transcript path unasserted), which the old text states as narrowings of the same close |
| 26 | yes | four transport names accepted against amendment 1's opposite shape, the deviation found by the cross-vendor round, `node.exe` and `python.exe` still accepted, and the oracle establishing only an added SHELL frame. Matches the old "WHAT STAYS OPEN" clause for clause |
| 65 | yes | the mechanical half - nothing checks at release time that the installed `gitCommitSha` equals the attested head - plus its never-designed status and its pairing with item 64. Matches. The body's compression of Parts A to C loses some values; those are noted under concerns because Step 2 checks the remainder |

## Step 3: OPEN bodies, substance kept

Losses counted: a deleted measurement, citation, constraint or "must NOT"
clause. A deleted ranking-history sentence is not a loss.

| id | body kept? | what was lost | fixed? |
|---|---|---|---|
| 12 | yes | nothing | n/a |
| 15 | yes | nothing | n/a |
| 27 | yes | nothing | n/a |
| 28 | yes | nothing; the whole leniency table survives byte for byte | n/a |
| 29 | yes | nothing | n/a |
| 31 | yes | nothing | n/a |
| 34 | yes | nothing; the Fable raw-reply case is ADDED from item 74's close, as the brief directs | n/a |
| 35 | yes | the `SKILL.md` line ranges 178-189 and 229-232, and the quoted `-PriorState` requirement. Both are the stale-citation class item 69 owns; the parameter name survives in the Cost line as `-PriorStateFile` | no, deliberate |
| 36 | yes | nothing; the `2026-07-25-flash-implementer.md:590-603` citation survives | n/a |
| 37 | yes | nothing; all four citations survive | n/a |
| 38 | yes | `model-prompting-notes.md:288-291`, which item 69 records as already stale at `5d20eed` | no, deliberate |
| 39 | yes | nothing | n/a |
| 40 | yes | nothing; both line ranges and `debate-protocol.md:100-131` survive | n/a |
| 41 | yes | nothing | n/a |
| 43 | yes | nothing | n/a |
| 44 | yes | nothing; the four-run table and `99d1961` / `e713081` survive | n/a |
| 45 | yes | the model generation in "Gemini 3.6 Flash". Not restored: the shipped agent now names a later Flash, so re-inserting 3.6 would re-state a stale number as current | no, concern |
| 46 | yes | nothing | n/a |
| 47a | yes | nothing; the split from 47b keeps both halves whole | n/a |
| 47b | yes | nothing | n/a |
| 49 | yes | nothing; both measurements and both "must NOT" clauses survive | n/a |
| 51 | yes | nothing | n/a |
| 53 | yes | nothing | n/a |
| 54 | yes | the three artifact filenames (`brief-sol-r1.md`, `brief-kimi-r2.md`, `amend-r3.md`) and a clause of the hand-built-mirror permission. The 63/47/16/15/1 counts, the 8,613 MB, both dates and every "must NOT" survive | no, concern |
| 55 | no | "It was built 2026-07-26 and roughly ten versions have shipped since" - the span the never-used measurement covers | yes, restored |
| 58 | yes | `model-prompting-notes.md:150`, which item 69 records as already stale at `5d20eed` | no, deliberate |
| 59 | no | the second instance's record citation ("A required control the session did not run", named in the merge commit, the user's choice to ship with the gap visible) and the four `application-checkpoint.md` clauses the session sided with | yes, both restored |
| 60 | yes | nothing; all five corrected citations survive | n/a |
| 61 | yes | nothing; the four-row reproduction and the 60-of-60 measurement survive | n/a |
| 63 | no | the on-disk location `~/.kimi-code/sessions` of the 90 wire files. The five expectations were also compressed to "lane ORCHESTRATION", which is descriptive | yes, path restored |
| 64 | yes | nothing | n/a |
| 66 | yes | `model-prompting-notes.md:343-345` and `:350-355` and `:46-52`, all recorded as stale or converted by item 69 and item 74. The identification of item 50's fixed bullet is compressed to "the resume bullet of the same file" | no, deliberate |
| 67 | yes | nothing; both halves and both item-74 instances survive | n/a |
| 68 | no | the retained transcript path for Part C, the parenthetical that `ALLOWED_TOOLS` also pre-approves `Skill`, `Read(**)`, `Glob` and `Grep`, and the `round-dispatch-operation` region citation for the SKILL-side fix | yes, all three restored |
| 69 | yes | nothing; the four stale instances, the split and its settlement survive | n/a |
| 70 | yes | nothing; the five wrong hit counts and all three conventions survive | n/a |
| 71 | yes | nothing | n/a |
| 72 | yes | nothing; the receipt's fourteen fields survive | n/a |
| 73 | yes | nothing | n/a |
| 75 | no | the Sol session id, "advertised skills 31 to 0", the gloss that the subject revision is the byte-identical brief, and item 4's "Problem"/"Evidence" paragraph names. The old item deferred its panel record to item 74's, and item 74 is now a resolution paragraph, so these had no other home | yes, all restored |
| 76 | yes | nothing; all seven citations and all four constraints survive | n/a |
| 77 | yes | nothing; every line citation, the three phases and the UNVERIFIED block survive | n/a |
| 78 | yes | nothing; both readings survive | n/a |
| 79 | yes | nothing; the ten cases and the hook sha256 were restored in `1802eae` before this read | n/a |
| 80 | yes | new item; its citation `docs/superpowers/plans/2026-07-27-0150-backlog.md:435-439` at `d19a5ca` was resolved against the old text and lands on the classifier-refusal bullet | n/a |
| 81 | yes | new item; `:400-419` at `d19a5ca` lands on item 74's problem statement and its effort bullet | n/a |
| 82 | yes | new item; `:3351` at `d19a5ca` is exactly "The resume-after-a-kill recovery is still unmeasured" | n/a |

## Step 4: the header decisions against spec 1d

Every bullet checked against the ranking block and the headers, and
against the restatement in the frozen plan's Task 10 Steps 2 to 4
(`docs/superpowers/plans/2026-09-04-backlog-rewrite.md`; the Task 10
brief the implementer worked from was an extract of that task, kept in
the git-ignored SDD workspace and not retained).

- **75 first, no pair.** Yes. Entry 1 of the First group; `Pairs: none`.
- **49, 59, 67, 78 at entries 2 to 5.** Yes, in that order, each with the
  other three as `Pairs`.
- **35 narrowed.** Yes. The Cost line is the spec's exact wording, and the
  body carries the "Half of this item is now closed by the dispatch tool"
  paragraph saying the "no file at all" half is gone.
- **68, 69, 43 placements.** Yes. 43 sits in First between 51 and 31; 69
  sits in Second between 44 and 77; 68 sits in Fourth between 63 and 81.
  All three moved from the group the old file had them in.
- **73, 79, 71, 72 slotted.** Yes. 73 leads the Fourth group; 71, 72 and
  79 close the Last group. All four were unranked in the old file.
- **The pairing repairs.** Yes, all eighteen sides. 27's old pairing with
  19 is dropped (19 is DONE), and 36's dependency on 45 is in its Cost
  line rather than as a pair, both as the brief directs.
- **34 amended.** Yes. The Cost line carries the retained-reply half, and
  the body carries "A THIRD CASE, carried in from item 74's close".
- **80, 81, 82 present.** Yes, with commit-bound citations into the old
  path that this reader resolved.
- **No renumbering narrative.** Yes. No sentence about entries moving,
  renumbering, or what entry an item used to hold survives in any body,
  and the whole ranking-history preamble of the old file is gone.

## Fixes applied

Seven edits, all restorations from the old text, in six items:

1. **48** - restored `~32000-character` on the command-line ceiling and
   the "or specifying a fallback transport" alternative.
2. **55** - restored "It was built 2026-07-26 and roughly ten versions
   have shipped since."
3. **59** - restored the second instance's record citation paragraph.
4. **59** - restored the four `application-checkpoint.md` clauses the
   session sided with, and the "not a disclosure line" cost sentence.
5. **63** - restored `under ~/.kimi-code/sessions`.
6. **68** - restored the Part C transcript citation, the non-shell
   allowlist parenthetical, and the `round-dispatch-operation` citation.
7. **75** - restored the Sol session id, "advertised skills 31 to 0", the
   subject-revision gloss, and item 4's "Problem"/"Evidence" paragraph
   names.

Each item's `Verified` digest was refreshed from the value the lint
printed: 48 `cb75841dc930`, 55 `5f5681efc252`, 59 `bbdc7d66c0db`, 63
`de95c61797a9`, 68 `73bae3504790`, 75 `71eee7a370df`.

`python evals/tools/backlog_lint.py` then reports
`backlog lint: clean`.

Every one of the 33 `Record:` values was resolved: 12 commits with
`git cat-file -e`, 21 paths with a filesystem check. All exist.

## Concerns, not fixed

- **Record policy is uneven, and items 8 and 16 are the clearest cases.**
  Both point `Record:` at item 13's live-debate record while their own
  bodies name the artifact that actually carries the fix
  (`tools/read-kimi-round-evidence.ps1` for 8, the deleted
  `tools/kimi-lane-lock.ps1` for 16). Neither old item names a record at
  all, so nothing is contradicted and the brief fixes the field; but the
  file mixes "the record of the cycle" with "the artifact that shipped"
  across the 33 values and nothing says which a reader should expect.
- **Item 47b's Cost line is a fragment.** "only once something measures
  whether the opt-out changes what the model does" has no subject; it
  reads as the tail of the old ranking entry ("**47** (its preamble half)
  - only once..."). Every other Cost line is a clause that states a cost.
  The brief fixes the Cost lines, so it is not changed here.
- **Item 9's three lessons drop the declared-fault-model one.** The old
  text says "Three things" and then lists five, so the new three are a
  faithful compression of an inconsistent source; the lesson that three
  mutants could not be killed by any input, and were killed only under a
  declared fault model, now exists nowhere in this file.
- **Item 32 drops three closing facts**: the attested head `15f85ec` over
  `8af6ae0..15f85ec`, the twice-verified install, and the plan's
  `Verification status: DEGRADED` with class
  `final-revision-reviewed-late`. The residual it also drops - an
  interrupted launch that leaves NO RECEIPT, narrowed rather than
  eliminated - is now carried by no item, where the other four things
  that close named said became items 51, 31, 58 and 82.
- **Item 24 drops** that the 0.20.0 `6,5,2,1,0` finding sequence is
  retained nowhere and remains an assertion. That is a stated evidence
  limit rather than a shipped fact.
- **Item 65's body compresses two measurements** that its remainder
  paragraph does not need: the two stale files
  (`tools/read-kimi-round-evidence.ps1` and
  `evals/multi-model-verify/test_kimi_round_evidence.py`) with the three
  defects the installed binder still carried, and the verified cache's
  own `gitCommitSha` `6c24b99`. Step 2 checks the remainder, which is
  correct, so these are recorded rather than restored.
- **Item 14's header is `Closed: record` with a commit as its
  `Record:`.** The old heading says "DONE, shipped 2026-07-31" and names
  merge `2b3c384` attested at `fed25a4`, so this closed on a merge rather
  than on a record, unlike item 48. The brief fixes the value, so it
  stands.
- **Item 45's dropped "3.6"** is listed as a loss above and deliberately
  not restored: the shipped Flash lane runs a later generation, so
  putting the old number back would state a stale figure in the present
  tense, which is the class this file exists to avoid.
