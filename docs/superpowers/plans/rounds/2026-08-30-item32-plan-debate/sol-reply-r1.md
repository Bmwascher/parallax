The plan is not ready to implement. Claims 2, 3, 4, 5, 7, 10, 11, and 12 need correction before code.

1. The premise is partly stale

The detach instruction already exists in `model-prompting-notes.md`, including the caller-kill consequence (`skills/multi-model-verify/references/model-prompting-notes.md:297-301`). The existing test pins only that consequence, not the opening detach instruction (`evals/multi-model-verify/test_multi_model_verify.py:970-987`). The two copied commands remain foreground pipelines with no detachment at their point of use (`skills/multi-model-verify/SKILL.md:174-188`, `skills/multi-model-verify/SKILL.md:236-250`).

What I read to pass it: the current instruction bullet, both current dispatch blocks, and the complete existing consequence pin. The repo evidence supports changing the command rather than adding another adjacent instruction. **PASS**

2. The in-scope surface is exactly four shell dispatch sites

The four listed review-round commands exist where claimed (`skills/multi-model-verify/SKILL.md:174-188`, `skills/multi-model-verify/SKILL.md:236-250`, `skills/multi-model-verify/references/backup-lane.md:21-32`), and panels route Sol and Kimi through those documents (`skills/multi-model-verify/references/panels.md:47-55`).

But the enumeration misses the mandatory Kimi write-probe: before every backup-lane debate, a fresh disposable Kimi session is asked to create a marker file (`skills/multi-model-verify/references/backup-lane.md:353-359`). Panels require that client call too (`skills/multi-model-verify/references/panels.md:51-53`). The existing tests confirm it is a real session-creating call with the debate configuration (`evals/multi-model-verify/test_backup_lane.py:578-585`, `evals/multi-model-verify/test_backup_lane.py:620-623`).

Task 5 also does not actually detach either listed Kimi call: it adds only a prose paragraph, with no wrapper body, exit sidecar, PID write, or `Start-Process` command (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:450-463`).

**FIX — include the Kimi write-probe in the dispatch inventory and specify executable detached wrappers, PID files, exit sidecars, and polling for all three Kimi client calls.**

3. Four things are out of scope for four different reasons

The Fable files are read-only Agent seats with no shell tool (`agents/fable-reviewer.md:1-5`, `agents/fable-reviewer.md:25-29`; `agents/fable-panel-reviewer.md:1-5`), and panels describe resumed Fable execution as background (`skills/multi-model-verify/references/panels.md:78-82`). Doctor explicitly calls its low-effort invocation a reachability check rather than a review (`commands/doctor.md:58-70`). The attestation command invokes a local emitter after the terminal verdict (`skills/multi-model-verify/SKILL.md:311-327`).

The `check-drift.ps1` rationale is inaccurate, however. It does use `Start-Job`, but only until a deliberate 900-second timeout (`tools/check-drift.ps1:1054-1064`); on timeout it explicitly stops and removes the job (`tools/check-drift.ps1:1112-1115`). Thus it can still terminate a running review with no result—just under an internal automation policy rather than the harness’s 600-second foreground ceiling. Calling it “already detached; nothing to change” hides that distinction.

**FIX — keep `check-drift.ps1` out of this cycle, but state the correct reason: it is governed by a separate explicit 900-second automation timeout, not immune to the killed-round outcome. Also stop asserting the Agent tool is background “by default” unless the actual harness contract is cited.**

4. `Start-Job` cannot be the mechanism

The design explains why a job handle cannot cross fresh-shell calls and why `check-drift.ps1` can wait only because it remains inside one script (`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:105-116`). That supports rejecting `Start-Job`.

It does not support “`Start-Process` is the only mechanism”; the design evaluates only two rejected alternatives before selecting it (`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:105-124`). More importantly, the plan never measures its central promise that the launching harness call returns while the child remains alive. Task 7 measures encoding and evidence binding, not launch latency or survival across the call boundary (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:583-601`). The in-repo `Start-Process` precedent explicitly redirects all three standard streams (`tools/check-drift.ps1:923-927`), while the proposed launcher inherits them through `-NoNewWindow` (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:376-379`).

**FIX — call `Start-Process` the selected in-repo mechanism, specify safe standard-stream disposition, and add a two-host harness-boundary probe proving the starting call returns promptly while a deliberately still-running wrapper survives.**

5. The wrapper must be a file, not an argument list

The cited precedent does establish that `Start-Process -ArgumentList` joins elements without automatically quoting a path containing spaces (`tools/new-kimi-lane-home.ps1:235-241`). The repo separately records PowerShell 5.1 stripping embedded native-argument quotes without changing argument count (`tools/read-codex-round-evidence.ps1:5-11`).

But “a wrapper file has no quoting layer at all” is false. It removes one `Start-Process` serialization boundary; the wrapper still has PowerShell parsing and native argv construction. This matters especially for Kimi, whose brief remains an inline `-p "<the whole brief>"` argument (`skills/multi-model-verify/references/backup-lane.md:24-30`). Task 5 never specifies how arbitrary brief bytes become safe wrapper source (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:450-458`).

**FIX — describe the file as avoiding the extra `Start-Process -Command`/argument serialization boundary, and specify/test byte-safe wrapper generation for paths, overrides, and the Kimi inline brief on both hosts.**

6. The encoding preamble must move inside the wrapper

The current dispatch blocks establish `$OutputEncoding` around the native pipe (`skills/multi-model-verify/SKILL.md:177-187`, `skills/multi-model-verify/SKILL.md:239-249`). The existing test pins all five relevant lines and records that moving the assignment into a child scope left the native pipe on the outer value (`evals/multi-model-verify/test_multi_model_verify.py:609-650`). The proposed wrapper begins with that full preamble (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:353-367`).

What I read to pass it: both current blocks, the complete encoding regression test, and the proposed wrapper body. The “single most likely” ranking is not independently verifiable, but it is unnecessary to the technical conclusion. **PASS**

7. The exit code must come from a wrapper-written sidecar

The precedent supports a sidecar rather than depending on a later `$proc.ExitCode` read (`tools/check-drift.ps1:902-913`, `tools/check-drift.ps1:950-955`). Cross-call operation also means the original `$proc` object will not be available.

The proposed implementation is nevertheless unsafe:

- It writes the sidecar before the `finally` restoration, so the sidecar is not its “last act” (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:364-366`).
- An exception during brief reading, hash verification, or native invocation bypasses the sidecar entirely (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:356-366`).
- Existing freshness rules require only round-numbered reply/transcript paths, not fresh wrapper/PID/exit paths (`skills/multi-model-verify/SKILL.md:220-226`). The new plan adds no corresponding exit-sidecar freshness rule (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:364-378`).
- Therefore “process exited but sidecar missing or invalid” is an additional state not represented by the asserted four states (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:227-239`).

**FIX — require fresh unique round-numbered wrapper/PID/exit paths, reject missing/malformed/not-fresh sidecars, capture a nonzero code for every pre-client failure, restore encoding before publishing completion, and define “process exited without a valid fresh sidecar” as transport failure.**

8. The `SKILL.md` budget is binding and should be raised deliberately

The plan records the measured 20,983-character/5,245-estimated-token body and keeps the soft budget at 5,250 (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:29-54`). The linter currently defines 5,250/5,500 (`evals/tools/skill_lint.py:97-102`) and explicitly names relocation or a deliberate measured ceiling raise as the two remedies (`evals/tools/skill_lint.py:308-326`). Leaving the soft budget unchanged preserves the growth warning.

What I read to pass it: the measurement task, both current constants, and the complete warning/error branch. The linter notes that these are global numbers, but also records that only one tracked `SKILL.md` currently exists (`evals/tools/skill_lint.py:73-75`). **PASS**

9. Existing pins constrain the wrapper body and should stay green unamended

The encoding test contains five positive exact-string checks: output encoding, strict brief decoding, native pipe, prior-value capture, and finally restoration (`evals/multi-model-verify/test_multi_model_verify.py:617-647`). The resume regex forbids a newline before `resume <SESSION_ID> -` (`evals/multi-model-verify/test_multi_model_verify.py:586-598`), and the raw guard forbids the three-space-indented `& {` form (`evals/multi-model-verify/test_multi_model_verify.py:648-650`). The proposed Codex wrapper preserves those strings and adds only the exit write (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:353-367`).

What I read to pass it: all relevant assertions and both proposed Codex wrapper bodies/instructions. These pins do not prove correct detachment, but they do constrain the unchanged body exactly as claimed. **PASS**

10. Passing the existing Kimi command pins proves item 51 did not move

The tests do not pin byte identity. They read a whitespace-normalized document (`evals/multi-model-verify/test_backup_lane.py:44-50`) and assert that normalized command substrings appear (`evals/multi-model-verify/test_backup_lane.py:123-148`). Rewrapping or whitespace changes can pass.

More seriously, those assertions prove only that the displayed strings remain somewhere in the document. They do not prove that an executable wrapper invokes those exact strings. Task 5 adds only a prose claim of detachment (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:450-463`).

**FIX — add raw exact-line pins if byte identity is required, and separately pin each Kimi command inside its actual wrapper/launch contract rather than accepting an unchanged display string plus detached prose.**

11. Item 33 is safe to remove the prompt for because the mirror is a copy

The mirror tool guards against a mirror path equal to, inside, or containing the real repo (`tools/new-review-mirror.ps1:657-695`), copies into the mirror (`tools/new-review-mirror.ps1:929-967`), and removes back-channels beneath the resolved mirror path (`tools/new-review-mirror.ps1:1047-1069`). The post-remediation enumeration remains mandatory (`tools/new-review-mirror.ps1:1094-1102`).

But construction is not side-effect-free: deleting a tracked back-channel causes `git commit` inside the copied repository (`tools/new-review-mirror.ps1:1071-1089`), and the contract explicitly acknowledges that the copied `.git` hooks execute (`skills/multi-model-verify/references/backup-lane.md:480-495`). An automatically executed arbitrary repository hook invalidates “there is no destructive act, so nothing to consent to.” This does not re-litigate the user’s decision to remove the question; it means automatic construction needs tighter execution containment.

**FIX — suppress all repository hooks during the mirror-only remediation commit, using a verified empty hooks directory, and pin that behavior before making mirror construction automatic.**

12. Timeout policy should remain open

The plan contradicts this claim. Its open-question section says the timeout must be settled “in the debate before the plan is frozen” (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:661-667`). It also recognizes that no policy risks indefinite polling (`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:227-240`).

A timeout policy need not recreate false completion: bounded polling calls can reach an escalation threshold, report that the round remains unfinished, and ask whether to continue polling or abandon it. Neither branch reads the round as a review result; abandonment uses the documented whole-tree kill mechanism (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:227-239`).

**FIX — freeze an operator policy now: bounded individual polls, a defined escalation threshold, and explicit continue-or-kill handling that always remains a transport failure unless a valid fresh completion tuple exists.**

## UNVERIFIED

- The repository does not contain the cited authoritative harness contract establishing that working directory persists while shell state does not. The design states it (`docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:110-114`), and the lock tool records fresh wrapper shells (`tools/kimi-lane-lock.ps1:859-872`), but neither is the harness contract itself.
- “The Agent tool runs subagents in the background by default” was not verifiable from the files read. The repo establishes only that the Fable resume was a background agent (`skills/multi-model-verify/references/panels.md:78-82`).
- The claim that moving the encoding preamble is the “single most likely” implementation failure is a risk ranking, not a repository-verifiable fact. The underlying encoding failure is pinned (`evals/multi-model-verify/test_multi_model_verify.py:635-650`).

## Final sweeps

(a) Yes: the plan introduces a new false-completion path. Existing text requires fresh paths only for reply/transcript (`skills/multi-model-verify/SKILL.md:220-226`). The new native command writes the current reply before the wrapper writes its exit sidecar (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:364-366`). If an old zero sidecar is reused and the new wrapper is killed after the client writes the fresh reply but before the sidecar rewrite, polling observes: process exited, exit code zero, fresh reply—and incorrectly accepts the forbidden third state despite the wrapper being killed (`docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:19-20`). Fresh unique control paths and sidecar validation are mandatory.

(b) The missed shape is a prose-mandated client generation that does not repeat the canonical review command: the pre-round-1 Kimi write-probe creates a fresh disposable session and asks the agent to write a marker (`skills/multi-model-verify/references/backup-lane.md:353-359`). Panels inherit it (`skills/multi-model-verify/references/panels.md:51-53`). It is neither one of the four enumerated round commands nor one of the four out-of-scope cases.