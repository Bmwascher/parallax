# Fable whole-branch review — `6201e30..f46be73`

Seat: `parallax:fable-reviewer`. Branch `feat/kimi-code-backup-lane`,
documentation only, 19 files, 2979 insertions. Run 2026-07-31, after Sol
plan-debate round 7 and plan revision 8, before the freeze.

Dispatched with the plan, the design spec, both probe records and the seven
retained Sol rounds named as inputs, and with an explicit instruction NOT to
re-run the round-by-round attack but to look for what arguing round by round
would miss: whole-artifact coherence, plan versus measurement, whether the
deletions are safe, executability, and record honesty.

## Raw reply

Whole-branch review, range `6201e301..f46be738` (`feat/kimi-code-backup-lane`, documentation only). No controller diff package was attached to the dispatch, so this review reads the named artifacts directly. Focused repo checks made, each against a named risk: `test_contract_coverage.py` (region-list claim), `check-drift.ps1` (cited line ranges and flag content), `fallbacks.md` and `model-prompting-notes.md` (cited line ranges), `drift-snapshot.json:4` and the backlog file path (staging targets), plus the two orientation files the dispatch named. The `sol-plan-r1..r7` round files were not re-read; revision-history claims were spot-checked against the plan and probe records instead.

### Strengths

- The measured-facts block (`docs/superpowers/plans/2026-07-31-kimi-code-swap.md:41-57`) matches the probe records line for line: record classes and counts (`probe-record-2.md:25-37`), record order (`probe-record-2.md:69-82`), the four-flag resume result stated at exactly its measured width (`probe-record-2.md:166-185`), effort observable and thinking not (`probe-record-2.md:150-164`), `--skills-dir` claiming nothing (`probe-record-2.md:110-133`).
- Every deletion is paired with a measured property and a replacement check: the lock's interleaving job becomes the two-new-leaves detection (`plan:708`), the rotation guard becomes prefix hashes over both files (`plan:770`), the offset rule survives as the freshness boundary with an explicit lineage comment required in `DECLARED_REGIONS` (`plan:806`), and the restoration guards are honestly labeled as non-pins (`plan:844`).
- Record honesty holds where spot-checked: r8's claimed leaf-definition fix is in the region text (`plan:825`), the substituted-drive fail-closed gate is present (`plan:478`), the sandbox-nested fake profile is present (`plan:477`), the `session_`/`wd_` addendum exists in the record (`probe-record-2.md:49-65`), and the self-review's mappings (`plan:1027`) each land on a real step.
- Line references verified are accurate: `check-drift.ps1:133-136` and `:197-216`, `drift-snapshot.json:4`, `fallbacks.md:152-179`, `model-prompting-notes.md:298-315`, `test_contract_coverage.py:624-648`, and all seven removed region names exist in `DECLARED_REGIONS`.
- Fail-closed discipline is uniform and specific: the drift probe's three-way absent/broken/usable split (`plan:174,226`), the git work-tree check (`plan:454`), the cleanup fault injection (`plan:456`).

### Issues

#### Critical

None. The range is documentation; nothing on it executes.

#### Important

1. **An unmeasured equality sits inside a hard validator rule.** Rule 13 requires fresh-slice `llm.request.toolsHash` to equal `llm.tools_snapshot`'s own `hash` (`plan:775`; negative case at `plan:746`). Neither probe record states that equality: `probe-record.md:180-183` lists the snapshot's `hash` field and `probe-record.md:229-230` gives a request `toolsHash` value, but no measurement compares them. The plan's own constraint says every such claim is measured (`plan:26`). If the client computes the two hashes over different serializations, every clean fresh round fails, which is exactly the fails-every-clean-call class r3 through r7 kept removing. The retained probe session files can settle this for free in Task 4.
2. **Large parts of `backup-lane.md` are assigned to no task and will contradict the rewrite.** Task 7 modifies only `:18-140` and `:159-198` (`plan:797`). Unowned: the intro (`backup-lane.md:1-16`, "via kimi-cli", "thinking flag"), the Containment section (`backup-lane.md:143-150`, which names the deleted `kimi-reviewer-agent.yaml` pair as "the ONLY agent configuration" and the dead `Loaded tools:` check), and the Workspace section's brief rule (`backup-lane.md:218-220,263`, brief planted as `KIMI-REVIEW-BRIEF.md` with a `-p` pointer). The new transport is inline-brief (`plan:821`), so the shipped contract would carry both rules at once. The manual eval case pins the file-planted form too (`test_backup_lane.py:419,425-426`, grading `evals.json`, which no task touches) - the same superseded-manual-case class the 0.14.2 review caught. None of these fail the suite, so the contradiction ships silently.
3. **Task 7 Step 7 ("full suite, Expected: PASS", `plan:846-849`) cannot pass as scoped.** Step 5 rewrites the Client config surface (`plan:835-840`), but its exact current sentences are pinned by `test_backup_lane_client_config_sweep` at `test_backup_lane.py:429-459`, outside Task 7's declared test range of `:80-257` (`plan:798`). And Step 3's Transport spec never says to preserve the encoding-guard bullet (`backup-lane.md:20-32`, inside the `:18-140` rewrite range) that `test_output_encoding_class_is_wired` pins at `test_backup_lane.py:496-501` and that Task 10 Step 2 later expects to still exist (`plan:955`). Either Task 7's surface grows or its verification step fails by construction, far from the cause.
4. **The 16 MB rotation probe has no feasibility basis.** Task 4 Step 2 (`plan:508-510`) requires growing one session's log past 16 MB by "repeated cheap dispatches", but no per-dispatch log-growth rate was ever measured, and the only recorded scale is 359 KB across a full day of real use (`plan:508`). Reaching the stated depth could cost hundreds of quota-charged model calls on a lane that has exhausted quota windows before, for a probe whose outcome Task 7 explicitly does not depend on (`plan:512`). The probe needs a measured growth rate and a call budget, or a cheaper stated depth.

#### Minor

1. Task 1's `-k` filter (`plan:141,242`) selects only four of the six tests Step 1 writes: `test_the_production_lookup_accepts_a_cmd_stub` (`plan:108`) and `test_a_present_but_unusable_binary_is_a_finding_not_a_note` (`plan:130`) match none of `drift/state_machine/hidden_alias/failure_branch`, so they are never verified to fail or pass inside Task 1, and "FAIL, all four" undercounts what was written.
2. Task 2 Step 1 (`plan:274-282`) adds `"Canonical backup thinking flag: --thinking" not in notes` without saying to delete the existing positive assertion at `test_backup_lane.py:49`; as written, Step 4's PASS is unreachable until the executor infers the deletion.
3. The two probe records disagree on the printed session-id token: `probe-record.md:38-39` shows `kimi -r <uuid>` while `probe-record-2.md:60-61` says the printed id "is the leaf's name exactly", and leaves are `session_`-prefixed. The exact token is load-bearing twice (`-SessionIdFromStdout` equality at `plan:763`, the resume argument at `plan:988`). UNVERIFIED which record is precise.
4. `CronList` appears in `KNOWN_TOOLS` (`plan:562`) and the denylist (`plan:544`) but in neither probe record's tool enumeration (`probe-record.md:151-155` lists 21 distinct names without it), and the design's own denylist (`design.md:90-92`) is 16 names without `CronList` while `probe-record-2.md:20-21` says "sixteen-name denylist including CronList". Three artifacts, three inventories; UNVERIFIED whether `CronList` exists on 0.31.1. The partition test is self-consistent either way, so this cannot fail loudly.
5. Task 10's Files block (`plan:944-945`) omits `backup-lane.md`, yet Step 2 edits it (`plan:955`) and Step 4 stages it (`plan:968`).
6. Task 6's fixture normalization (`plan:684`) lists paths and session ids but not the canonical model literal; captured `.jsonl`/`.log` fixtures will carry `kimi-code/k3-256k`, which `SWEEP_GLOBS` (`test_backup_lane.py:588-593`) cannot see (no `.jsonl`/`.log` patterns), so the Global Constraint's "may appear ONLY in" statement (`plan:27`) is textually violated while every test stays green. Either normalize it or record the exclusion the way `docs/**` is recorded.
7. The `systemPrompt` "byte for byte" and `systemPromptChars`-equals-length comparisons (`plan:624,773,775`) state no unit or newline canonicalization, on a repo where `core.autocrlf=true` is a documented trap (`backup-lane.md:289-292`); the brief hash got exactly this treatment (`plan:831`) and the agent-body comparison did not. Self-consistent if both sides read the same worktree file raw, but that assumption should be written down.

### Ledger minors triage

No SDD ledger path was provided in the dispatch, so there are no deferred minors to triage. Naming the gap rather than inventing one: if a ledger exists for this branch, it was not part of my inputs.

### Assessment

Ready to merge: With fixes. The plan is structurally sound and its measured foundation is real, but Important 1 plants an unmeasured equality in the one rule class this debate spent four rounds hardening, and Important 2 and 3 mean the execution as scoped either ships a self-contradicting contract or fails its own verification step; all three are cheap plan edits, and the debate should weigh Important 4's probe cost before execution begins.

## Session adjudication

All four Important findings ACCEPTED and fixed in plan revision 9. Five of the
seven Minor findings accepted; two refuted with evidence.

| # | Finding | Disposition | Where |
| --- | --- | --- | --- |
| I1 | Unmeasured `toolsHash` = snapshot `hash` equality inside rule 13 | ACCEPTED | Task 4 Step 1b measures it free from a probe already scheduled; rule 13 branches on the answer; `probe-record-2.md` lists it under Still unmeasured until then |
| I2 | Four sections of `backup-lane.md` owned by no task | ACCEPTED | Task 7's Files block widened to the intro, Containment, the Workspace brief rule, the export note, `evals.json` and two out-of-range pins; new Steps 3b and 3c |
| I3 | Task 7 Step 7 cannot pass as scoped | ACCEPTED | Step 3 now preserves the encoding bullet verbatim and names Task 10 as its owner; Step 5 rewrites the client-config pin in the same step; Step 7 states which out-of-range pins are in play |
| I4 | 16 MB rotation probe has no feasibility basis | ACCEPTED | Task 4 Step 2 measures bytes-per-call first, caps at 40 dispatches, targets `min(16 MB, 40 x R)`, and records the achieved depth as the claim's width |
| m1 | `-k` filter selects four of six tests | ACCEPTED | Task 1 Step 2 filter and count corrected |
| m2 | Task 2 never says to delete the positive thinking-flag assertion | ACCEPTED | Task 2 Step 1 states the deletion explicitly |
| m3 | Probe records disagree on the printed session-id token | REFUTED | `kimi -r <uuid>` is `backup-lane.md:38-39`, the OLD lane's contract for the OLD client, not a probe record. `probe-record.md:126` is about the FLAG; `probe-record-2.md:60-61` measured the ID. They agree. |
| m4 | `CronList` unverified across three inventories | ACCEPTED | Task 5 Step 3b re-enumerates from the client and reconciles; the unverifiable count is removed from `probe-record-2.md` rather than guessed |
| m5 | Task 10's Files block omits `backup-lane.md` | ACCEPTED | added |
| m6 | Fixtures would carry the canonical model literal past `SWEEP_GLOBS` | ACCEPTED | Task 6 Step 1 normalizes it to `fixture-model/x`, tests pass the same placeholder |
| m7 | `systemPrompt` comparison states no newline canonicalization | ACCEPTED | Task 6 rule 12 now canonicalizes both sides to LF and compares `systemPromptChars` against the normalized recorded prompt; a new test case covers a line-ending-only difference returning clean |

The partition test's inability to see a future client's new tool is a stated
accepted limit, not a defect; nothing offline can close it, and Task 5 Step 3b
closes the part that is measurable today.
