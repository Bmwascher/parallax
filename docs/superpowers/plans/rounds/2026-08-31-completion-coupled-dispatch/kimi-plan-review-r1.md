• Now the code the plan changes:

• I have the plan and the two mirror/dispatch tools. Now the backup lane's own files — this is my lane, so I'll read them in full — plus the binders and the key tests.

• Two more checks: the backlog's duplicate of the "three recorded values" instruction, and the existing mirror-test helpers.

• # Backup-lane review, round 8: completion-coupled dispatch plan

  Continuity: I have no prior round state on this plan. I read the plan, the poll, the invariants, the two most recent rounds, and every code file the plan touches, in the frozen copy.

  **Verdict up front: FIX — one mechanism defect nobody has caught, plus a small set of minors.** The defect is in the newest part of the design and it is this cycle's signature shape: a call written in a form that cannot do what its guard assumes.

  ---

  ## 1. The newest changes

  **(a) Whole-receipt digest — PASS.** The wrapper carries `<receiptSha256>` minted over the receipt's finished bytes (plan:272-277), `-Classify` re-hashes and refuses as `receipt-altered` (state 6, plan:360), and the per-field tests include the `workdirEvidence`-to-`none` case that gated B5 (plan:1221-1238). This genuinely removes the class fable-r2 named (fable-plan-review-r2.md:28) rather than moving it: the mirror-identity fields stay baked into the wrapper text (plan:141-150) and everything else is now digest-bound. One sequencing nit, not a blocker: Task 2 writes the wrapper at step 5 and the receipt "LAST" at step 6 (plan:865-870), while the design reads "writes the receipt, hashes its finished bytes, and writes that one digest into the wrapper" (plan:273-275). Since the wrapper embeds the hash, the receipt bytes must be final in memory before the wrapper is written even though the file lands last. Buildable either way; the two orderings as written contradict.

  **(b) Task 1a naming the pinned sentence — PASS, verified directly.** The sentence exists at `skills/multi-model-verify/references/backup-lane.md:650-652` ("re-run the tool with `-VerifyIdentity` and the three recorded values"), inside the `mirror-identity-gate` contract region (backup-lane.md:631), and is pinned verbatim as a raw-text pin at `evals/multi-model-verify/test_backup_lane.py:1970-1972`. After Task 1a makes `-MirrorStateSha256` and `-ExpectedMirrorPath` mandatory (plan:589-591), that documented call fails at binding while the pin stays green. Task 1a's file list and warning (plan:568-585) now cover exactly this. One sibling the task does not name: `docs/superpowers/plans/2026-07-27-0150-backlog.md:4018-4027` states the same "three recorded values BEFORE EVERY fresh and resumed dispatch" rule as the standing premise of a live backlog item — the same document Task 11 appends to (plan:1990). Not historical round record; a living document. Minor.

  **(c) The second-call-site-only regression test — PASS.** I re-derived it rather than trusting fable-r2. Pre-fix wrapper: the second call fails under `Continue`, `$LASTEXITCODE` holds the client's stale 0, the guard passes, classification proceeds to `reply-present` at exit 0 — so `assert out.returncode != 0` fails against the defective version. Post-fix: `Stop` is restored (plan:176), the broken second call terminates the wrapper, `classification` stays `reserved` (plan:1328). The test discriminates, and the comment explaining why the helper must break only the second occurrence (plan:1318-1323) is accurate. The companion mutation test (plan:1293-1309) is the real lock, as fable said.

  ---

  ## 2. The backup lane, read as its owner

  - **All three of my lane's bodies have the shape the plan attributes only to the probe.** `kimi-dispatch` (backup-lane.md:105-114), `kimi-resume` (backup-lane.md:135-144) and `kimi-write-probe` (backup-lane.md:475-484) each write `$code` into `$PSScriptRoot/exit` and never run `exit $code`. Task 7 names this only for the probe (plan:1553-1556). The new body contract is stated in the design (plan:293-295), so it is covered — but the task that rewrites the call sites never says "the body contract changed at all five sites," and the probe call-out's "also" does that work by implication. One sentence.
  - **The probe decision block and the probe pin disagree.** Task 7's header demands a deliberate either/or: add a binder to `kimi-write-probe` knowingly, or exempt it (plan:1540-1547). But `test_every_call_site_passes_the_seal` pins `total >= 5` (plan:1599-1603), which only the add-a-binder branch satisfies. The pin forecloses a decision the same task says must be made deliberately. Choosing "exempt" means rewriting a pin the plan presents as fixed. One clause.
  - **Task 7 breaks three pins in a module it does not name.** `test_each_kimi_call_is_launched_through_the_tool` (test_backup_lane.py:2005-2037) pins the exact `-Launch` and `-Poll` command lines per call section, for all three backup-lane calls. Task 7's rewrite turns all three cases red; its Files list names only `test_multi_model_verify.py` (plan:1562). The task's own gate (full module run, plan:1690) catches it loudly, so it self-corrects — but this is the same "task breaks a pinned file it doesn't name" class fable-r2 found in Task 1a, recreated in Task 7, differing only in that this one fails loud instead of green.
  - **The copied-in-inputs flow silently dies.** My lane documents copying review inputs into the mirror after construction (backup-lane.md:721-724) and the per-round status check explicitly tolerates "baseline plus exactly the expected untracked set" (backup-lane.md:763). After Task 1a, `mirrorStateSha256` is minted at build time and there is no interface to re-mint it; anything copied in afterwards fails `-Prepare`'s verification (plan:822-827) and the wrapper's first check. No task updates that documentation, and the residuals list does not state the restriction. Conservative direction — it blocks, never false-passes — but a documented workflow becomes unrunnable with no acknowledgment.
  - Task 5's kimi half checks out: the binder takes mandatory `-PriorState` (tools/read-kimi-round-evidence.ps1:85), `evals/multi-model-verify/test_kimi_round_evidence.py` exists, and the kimi workdir unknown is handled as an honest STOP (plan:1642-1647), matching the poll's demand.

  ---

  ## 3. Attack: the case nobody has named

  I searched: kill before the claim; kill in the claim-to-reservation gap; kill during either verification; kill mid-client; kill after consume but before the `exit` write; kill in the seam window; hung wrapper; rerun after completion; concurrent first runs; deleted tree at relocation; same-path tree swap; mid-round mutation persisted and reverted; receipt edits field-by-field and whitespace-only; transcript forgery and header spoofing; body self-exit; body tampering with `claim`/`exit`/`classification`/`reply`; seam abuse by a parent; hand-run `-Classify` with and without the nonce; cross-round receipt/task misattribution; missing host binary at run time; missing classifier at run time. All closed or stated as residuals — **except one, which is in the wrapper's literal text.**

  **The wrapper invokes exit-bearing PowerShell scripts in-process, and their `exit` terminates the wrapper.** The wrapper calls the verifier twice and the classifier once as `& '<mirrorToolPath>' @mirrorArgs` and `& '<toolPath>' -Classify ...` (plan:153, 177, 187). Those are .ps1 files invoked with the call operator — same process. Both tools end every exit path with a literal `exit N` (verify mode: tools/new-review-mirror.ps1:594-654; the dispatch tool throughout, e.g. tools/dispatch-detached.ps1:567-573). An `exit` inside an `&`-invoked script terminates the host process, it does not "return a code." I am read-only and cannot measure this here, but it is long-settled PowerShell semantics on both hosts, and the repo's own code treats it as settled: every sibling-script call in this tree goes through the host executable precisely so `$LASTEXITCODE` carries the child — `& $hostExe -NoProfile -NonInteractive -File $probeScript` (tools/new-review-mirror.ps1:1182-1185), the launcher command line (tools/dispatch-detached.ps1:712), and every documented call site (SKILL.md:218, backup-lane.md:121). The plan itself uses the host form for the body (plan:158) for exactly this reason — and then doesn't for the other three calls.

  The concrete false success, on the design's literal text:

  1. `-Prepare` succeeds. The wrapper starts; claim and reservation land.
  2. First mirror verification runs in-process and **succeeds** — `new-review-mirror.ps1` reaches `exit 0` (line 654). The wrapper's host process **exits 0 at plan:153**. The client never runs. No classification is computed, no state line is printed.
  3. The harness task completes with **exit code 0** — the one surface the whole design makes authoritative, the one the call sites read as "`0` meaning `reply-present` and nothing else" (plan:1666-1667).

  An unfinished round — one whose client never launched — reads as success at the exact point the design claims success can never be forged. The guards at plan:154/178 are dead code on this path; the `$LASTEXITCODE` they read is never set by an in-process script call on 5.1 anyway. Task 2's step 1a has the same defect one level up: a successful in-process verify exits `-Prepare` itself with 0 before the receipt and JSON are written (plan:822-827).

  To be fair to the plan: its tests-first discipline catches this at build time — `test_the_wrapper_stdout_is_the_classifier_line_and_nothing_else` (plan:1344-1348) goes red on an empty stdout, and Task 2's receipt test fails on the missing receipt. But the plan's instruction is to emit the wrapper "exactly as in the design section" (plan:1367), and its only hedge — "verify, do not assume, that `& '<tool>.ps1'` calling `exit N` sets `$LASTEXITCODE`" (plan:1383-1386) — is attached to the classify call alone, and even there misdiagnoses the mechanism (the classifier's in-process `exit N` would terminate the wrapper with N, which is accidentally the right code but makes `exit $LASTEXITCODE` at plan:190 dead and any post-classify act impossible). The mirror calls carry no hedge at all. Seven rounds in, "the tests will catch what the design text gets wrong" is precisely the arrangement this cycle keeps calling FIX.

  ## 4. Buildability walk

  Tasks 1, 1a, 3, 5, 6, 8, 9 buildable as written (Task 1a's existing verify tests in test_review_mirror.py:1598-1680 need the two new mandatory args, but that module is in the file list and fails loud). **Task 2 is not buildable as specified** (step 1a's invocation form, above). **Task 4 is not buildable as specified** ("exactly as in the design section" reproduces the defect; its own suite goes red). Task 7 buildable with the three minors in §2. Tasks 10-11 transitively depend on 4.

  ## 5. The residuals section

  Five listed, each real and honestly bounded — including residual 3's dependence on the second verification actually running (plan:2029-2031). Not complete: the copied-inputs restriction (§2), the stale backlog instruction (§1b), and — though I count it inside residual 2's "filesystem the caller owns" class — the wrapper text itself is editable post-preparation and nothing detects it; the digest binds the receipt, not the wrapper. Also note residual 4's premise gets its measurement only in Task 10 on one harness version, correctly STOP-gated (plan:1880-1901).

  ## 6. Good enough to build from?

  No — one change short, again, and again in the newest hardening. **Single smallest change:** state once, in the design section, that the wrapper (and `-Prepare` at step 1a) invokes the verifier and the classifier **as child processes under the resolved host** — `& '<hostPath>' -NoProfile -NonInteractive -File <tool> ...` — exactly as the body is already invoked at plan:158. One mechanism sentence covering four call sites, matching the repo's own convention. The rest rides along as one-liners (§2 minors, §1b sibling).

  **FIX**
