The revised plan is closer, but it still has a concrete false-completion path and several invariant/build gaps. Most importantly, the answer claim does not close post-hoc classification when the wrapper is killed before classification.

## 1. The two original cases

### Case 1: killed after `exit=0` and reply publication

For the authoritative harness path, the composition is correct: the wrapper writes `exit`, invokes the classifier, and only then exits with its result. A kill before that final exit cannot produce a normally successful harness completion. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:117-126`

Task 10 now measures both failed and killed harness tasks and stops the build if either is reported as success, which removes the first version’s unmeasured premise. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1219-1240`

But the case is only **narrowed overall**, not closed:

1. The flagship test kills the wrapper after `exit=0` and a reply exist but explicitly before `classification` exists. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:723-739`
2. A later standalone `-Classify` therefore wins the still-unclaimed create-new `classification` file. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:174-177`
3. It then sees the claim, `exit=0`, workdir evidence and reply, and returns `reply-present`, exit 0. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:180-200`

That contradicts the claim that every later manual classification “is refused.” It is refused only after the wrapper has already reached classification. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:204-211`

### Case 2: invocation B answered by invocation A’s artifacts

The intended harness path is closed: B loses the create-new execution claim as its first filesystem act, before it touches A’s artifacts. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:115-121,145-146`

The complete surface is nevertheless only **narrowed**. Combine the prior case with B:

1. A publishes reply and `exit=0`, then is killed before classification.
2. B is dispatched from the same preparation and fails on the existing execution claim.
3. `classification` is still absent.
4. A first post-B standalone `-Classify` claims it and returns success from A’s artifacts.

This is the same execution-association shape described in the poll: claim presence does not identify which invocation produced the terminal artifacts. `docs/superpowers/plans/rounds/2026-08-31-dispatch-options-poll/POLL-RESULT.md:77-81`

The answer claim needs to be reserved by the wrapper before the kill interval, or `-Classify` must require wrapper-only authority. As written, Task 8’s statement that the claim “closes” the residual is false. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1092-1097`

## 2. Adversarial attack

I searched the requested shapes: death before/during both claims, kill before and after exit publication, body self-exit, concurrent starts, rerun after completion, torn receipt/exit/classification, missing and empty reply, missing transcript, failed relocation, transcript-forged outcome text, stale receipt reuse, and wrong initial working directory.

I found two success paths.

First is the killed-A/refused-B/post-hoc-classification sequence above.

Second is wrong-tree self-consistency:

- `-Prepare` accepts a caller-supplied `-WorkingDirectory` and caller-supplied workdir evidence. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:71-78`
- The receipt records those same supplied values; there is no independent comparison with the mirror identity record. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:90-99`
- Therefore a caller mistakenly supplying the live repository for both values gets a wrapper that deliberately relocates there, a client report agreeing with that wrong value, and `reply-present`.

That fails B4’s explicit requirement to detect a wrong initial value and B1’s requirement that entering the live repository be impossible to get wrong silently. `docs/superpowers/specs/2026-08-31-dispatch-invariants.md:52-55,68-76`

The proposed transcript check is also only a containment search. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:190-193` The repository already records that the human-readable transcript is prompt-steerable, so an unanchored occurrence is not necessarily the client’s own header. `tools/read-codex-round-evidence.ps1:13-19` It should parse the designated first `workdir:` header field, not search for an arbitrary literal.

I found no additional false zero from body `exit`, concurrent start, malformed exit, missing reply, or a torn classification claim: those now fail conservatively.

## 3. The six revisions

1. **Child-process body:** Structurally correct for `exit` and `[Environment]::Exit`; the wrapper survives to classify. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:129-141`  
   It does introduce an overclaim: the child invocation has no stdout/stderr redirection, so body output inherits the wrapper streams. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:118-125` The purported “only classifier line” test writes a forbidden child line but merely checks the last line, so it passes while that line leaks. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:749-755`

2. **Create-new classification claim:** Useful after a normal classification, but it does not cover a wrapper killed before classification. The plan claims more than it delivers. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:204-211`

3. **Post-exit-write seam:** Correct and buildable. Its placement precisely creates the disputed interval, is bounded, and can only delay or fail. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:158-170,758-785`

4. **Seal both binders:** Both files are now in scope, correcting the first version. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:813-870`  
   But E4 is still not enforceable:
   - The seal remains optional, and omission is explicitly allowed to produce `sealed: "not-checked"`. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:844-853`
   - Task 7 says only “clean binding” is required; it does not require `sealed` to be checked. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1024-1029`
   - The receipt is create-new only when written, not immutable afterward. No internal preparation artifact or wrapper-embedded digest binds its later contents. Its `token` is not checked by any classifier state. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:87-99,180-196,470`

   A caller can omit the seal, or rewrite `priorStateSha256` before binding. That does not meet E4’s “a state computed afterwards cannot satisfy it.” `docs/superpowers/specs/2026-08-31-dispatch-invariants.md:219-224`

5. **Working-directory measurement:** It is now wired into the round call sites, but the plan declares a Kimi result with no client workdir report “acceptable” and explicitly says B5 remains unsatisfied. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:995-1013` B5 is an invariant, not an optional quality signal. `docs/superpowers/specs/2026-08-31-dispatch-invariants.md:73-78,255-256`

6. **`already-classified` and `no-transcript`:** Both are worthwhile. `no-transcript` fixes the dishonest “mismatch” label when no transcript exists. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:213-218` But it is hidden whenever exit is nonzero because of the chosen order, and `already-classified` has the pre-classification-kill gap above.

## 4. Buildability

One existing call site is omitted.

`backup-lane.md` contains a third tool-driven operation, `kimi-write-probe`, with its own `-Launch` and `-Poll` calls. `skills/multi-model-verify/references/backup-lane.md:469-492` Task 7 names only round 1 and resume in that file. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:945-950`

After Task 2 deletes both modes, the write probe is broken. Task 7’s global `"-Poll" not in body_backup_lane` assertion will detect it, but no step defines its replacement body, preparation, dispatch, classification, or evidence behavior. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:960-963`

This matters particularly under the child contract: the existing write-probe body writes `$code` to the `exit` file but never executes `exit $code`. `skills/multi-model-verify/references/backup-lane.md:474-483` The new wrapper would take the child PowerShell process’s normal zero exit and overwrite the body’s recorded failure. The write probe must be migrated explicitly.

Minor plan drift: Task 3 and its commit message still say “eleven states” although the task defines thirteen. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:493,507-513,653`

The former unbuildable kill test and missing Kimi binder interface are fixed.

## 5. Classifier order

States 1–7 are ordered correctly: identity and receipt failures precede terminal artifacts, and malformed exit cannot reach success. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:180-188`

I reject `exit-nonzero` before `no-transcript` and workdir confirmation. A wrong-tree failure is not merely secondary diagnostic detail: it means the client ran under an instruction back-channel and its failure report came from the wrong review subject. B1 identifies that as the fact the preflight exists to prevent. `docs/superpowers/specs/2026-08-31-dispatch-invariants.md:52-60`

The plan’s “client failure is more actionable” rationale therefore chooses the less consequential fact and relies on an operator opening the transcript after receiving a generic `exit-nonzero`. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:220-226` Put workdir confirmation before `exit-nonzero`, or emit a composite state. Also, a transcript that exists but lacks the literal proves “workdir unconfirmed,” not necessarily “mismatch”; `workdir-mismatch` still overstates that measurement.

## 6. Missing requirements

The self-review misses or overstates:

- **A4 stdin and stream ownership.** The invariant requires stdin at EOF and explicit stdout/stderr ownership. `docs/superpowers/specs/2026-08-31-dispatch-invariants.md:42-46` The wrapper’s child process inherits all three streams; only the native-client snippets are expected to redirect some output. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:118-125,249-258`
- **B4 independent mirror identity**, as described above.
- **B5 on every review lane.** `-NoWorkdirEvidence` cannot be an acceptable successful branch while B5 remains required.
- **E4 mechanical enforcement.** Both-binder coverage is not sufficient while the seal is optional and the receipt is mutable.
- **The write-probe migration.**
- **A claim reserved before the post-exit-write kill interval**, or equivalent wrapper-only authorization for classification.

Accordingly, self-review row 5 and the “E4 in both lanes” paragraph are not established. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1372,1378-1384`

## 7. Scope that should not be present

The rename is justified because the tool no longer detaches. Deleting `-Poll` is directionally correct, the test seam is necessary, and moving mirror rationale out of the skill body is explicitly required by the invariants. `docs/superpowers/specs/2026-08-31-dispatch-invariants.md:241-245,261-266`

Two pieces should not remain in their current form:

- A public, independently successful `-Classify` surface that the plan claims is no longer post-hoc.
- The receipt’s `token` as dead schema weight. It should either bind the external receipt to an internal immutable preparation record or be removed. `docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:93,180-196`

## 8. Deliberate omissions

The four listed omissions are appropriate:

- version bump after review;
- no liveness model;
- no correctness claim about session survival;
- no hung-round time policy, with the backlog filing now explicit.

`docs/superpowers/plans/2026-08-31-completion-coupled-dispatch.md:1327-1334,1345-1362`

None is load-bearing for completion correctness: a hung wrapper still lacks an acceptable exact-task completion. The load-bearing omissions are instead the unreserved pre-classification interval, independent mirror identity, mandatory/immutable evidence sealing, A4 stream handling, and the missing write-probe migration.

**FIX**