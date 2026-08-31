The shipped-tool rebuild closes several structural findings, but the completion model still has a fifth false-completion path: a failed launch against an old committed directory can be polled as the old round’s successful reply.

## Changes

1. FAIL-CLOSED RESERVATION — CLOSES

The proposed tool uses terminating behavior on reservation and launch, and catches failures after process creation to kill the tree at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:77-83`. The tests cover an occupied directory, argument-order-independent `-Force` detection, publication order, and injected post-start failure at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:57-66`. I read both the executable sequence and its real-script tests.

PASS

2. THE EIGHTH CONDITION — PARTLY CLOSES

`launch-unknown` is now first and conservatively dominates every other artifact when `launch.committed` is absent at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:85-92`. The contract correctly admits that a hard kill can leave a live untracked process at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:147-163`.

The remediation is impossible in one of the state’s expressly admitted forms. The operation region says to clear LAUNCH UNKNOWN with `taskkill /PID <id>` at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:170-180`, but a hard kill before PID publication is precisely the case where no `<id>` exists on disk at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:79-83`.

More importantly, the poll carries no launch-attempt identity, producing the false completion in sweep (a).

FIX — bind `-Poll` to a token returned only by a successful `-Launch`, and state that PID-less LAUNCH UNKNOWN cannot be cleared by PID without a separate targeted-discovery mechanism.

3. SITE-BOUND KIMI ORACLES — CLOSES THE ROUND 4 FINDING

I read the exact-one marker check, section splitting, and per-section launch/client/reply assertions at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:353-384`, plus the named three-case oracle at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:410-413`. Leaving an entire call behind now fails by that call’s parameter name.

The assertion does not prove that each call has its correct flags—it merely finds some Kimi invocation—but that is beyond the specific round 4 “global counts bind nothing” finding; the implementation instruction separately requires each call’s documented flag order at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:392-408`.

PASS

4. ACTUAL CENTRALIZATION — PARTLY CLOSES

The executable `Start-Process` sequence now exists only in the proposed tool at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:73-83`, and both lane tests forbid copied launches at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:244-253` and `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:383-384`.

But the Codex oracle still uses a global `>= 2` count at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:244-249`. Two tool calls under round 1 and none under resume satisfy it while the document contains no `Start-Process`. Centralization is proven; detachment of each Codex site is not.

FIX — mark Codex fresh and resume separately and assert one anchored `-Launch`, one corresponding wrapper, and one `-Poll` inside each section.

5. TASK-LOCAL ORACLES — DOES NOT FULLY CLOSE

Two claimed repairs are still absent:

- Task 2’s negative test points at a scratch copy, but `test_declared_regions_match_the_documents` currently reads fixed `DOC_PATHS` with no injectable source at `evals/multi-model-verify/test_contract_coverage.py:734-750`. Unlike Task 7, Task 2 never specifies modifying that API; it merely says to make the existing test fail “on” the scratch copy at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:198-208`.
- Task 9 says its grep now catches the refuted encoding claim at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:598-600`, but the actual pattern contains no encoding phrase at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:612-618`. The stale claim at `docs/superpowers/specs/2026-08-30-item32-detached-dispatch-design.md:159-164` would pass that grep.

FIX — make the contract collector accept injected document paths, and add an exact stale encoding pattern plus exact expected new wording to Task 9.

6. THE ANCHOR — CLOSES THE STATED SCOPE

I read the new anchored call at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:309-315`, item 58’s diagnosis that bare paths resolve against the reviewed repository at `docs/superpowers/plans/2026-07-27-0150-backlog.md:4440-4455`, and its prescribed `${CLAUDE_PLUGIN_ROOT}` mechanism at `docs/superpowers/plans/2026-07-27-0150-backlog.md:4457-4480`. The closure record also explicitly preserves the three existing defects at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:638-642`.

PASS

7. CONDITIONAL CEILING — DOES NOT CLOSE OPERATIONALLY

Conditional measurement is correct, but Task 9 says to use “the command in Task 2’s preamble” at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:604-606`; Task 2’s preamble contains a historical measurement but no command at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:108-110`.

The ordering is also circular if the ceiling is exceeded: Task 3 requires strict lint to pass before its commit at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:325-336`, while the permitted ceiling change is deferred until Task 9.

FIX — put the measurement command and conditional ceiling adjustment immediately before Task 3’s lint oracle, with an exact test only when a raise occurs.

## UNVERIFIED

- Skill-body substitution of `${CLAUDE_PLUGIN_ROOT}` is not executed by the cited repo test: the existing test only checks that the hook command contains the token and that its script exists at `evals/multi-model-verify/test_multi_model_verify.py:2258-2262`. Item 58 itself says static gates missed the failure at `docs/superpowers/plans/2026-07-27-0150-backlog.md:4427-4438`.
- The live-untracked LAUNCH UNKNOWN variant is unverified. The injected failure invokes the tool’s catch and kills the process at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:61-63`; it does not hard-kill the tool between `Start-Process` and PID publication.
- The terminal-state fixture construction is unspecified beyond “planted files” at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:63-66`, so I could not verify whether those cases include a valid committed PID.

## Sweeps

The base rate is four completion-model holes in four rounds, recorded at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:657-663`. This rebuild does not exhaust the class.

### (a) The fifth hole: old committed directory after a refused launch

Input:

- An old directory contains `launch.committed`, a dead PID, `exit = 0`, and a nonempty reply.
- A new round mistakenly selects that same `DispatchDir`.

Sequence:

1. New `-Launch` refuses the occupied directory and starts nothing, as required by `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:57-60`.
2. The caller later invokes `-Poll` on that path; the documented call sequence does not capture a launch token or mechanically condition polling on successful launch at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:301-315`.
3. Poll sees the old `launch.committed`, skips `launch-unknown`, finds the old PID dead, reads old `exit = 0` and the old reply, and reports `reply-present` under the ordered branches at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:85-92`.

The taken-directory test checks only that launch blocks and starts nothing; it never polls a pre-existing completed directory at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:57-66`.

FIX — return an unpredictable launch token only on successful commit, store it inside `launch.committed`, require it on `-Poll`, and add the refused-old-directory regression test.

### (b) New failure created by the separate tool process

The shipped call hardcodes `powershell` at both launch and poll sites at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:309-315`. Therefore a session running PowerShell 7 starts the tool under Windows PowerShell 5.1; the tool then uses its own executable path to launch the wrapper at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:77-82`.

That silently changes the wrapper host from the caller’s host to 5.1. The tests instead promise to invoke the script using whichever host `PARALLAX_PS_HOST` names at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:53-55`, so a direct pwsh-7 test does not exercise the shipped outer command. The five inline snippets used the caller process path and had no extra host-selection boundary.

FIX — invoke the tool through the current host executable and test the exact documented outer command on each host.

### (c) `Start-Process` absence is not sufficient

Yes, a lane can remain foreground-free yet still not be detached. The Codex file passes when both required tool strings occur in one section and the other section has none because its test is a global `>= 2` count at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:244-249`. `"Start-Process" not in text` only proves that no second launch implementation exists; it does not prove every call reaches the centralized implementation at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:250-253`.

FIX — retain the absence assertion as a centralization guard, but add per-site positive launch assertions.

### (d) State-test reachability

Three gaps remain:

- The dangerous LAUNCH UNKNOWN case—a live child after the tool itself is hard-killed—is not reached. The planned injected failure executes `catch` and kills the child; the launch-unknown poll test merely plants a directory without a commit at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:61-66`.
- There is no state or test for `launch.committed` plus a missing, unreadable, or non-integer PID. The poll jumps directly from commit existence to “PID alive,” then terminal artifacts at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:85-90`. Such an input can fall through to `reply-present`.
- “One case per terminal state, driven by planted files” does not require those fixtures to originate from a successful real `-Launch` at `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md:63-66`. A planted commit with no valid dead PID can prove an impossible fixture rather than the production transition.

FIX — hard-kill the tool in the start/publication window, add committed-PID validation states, and construct terminal fixtures by launching a stub successfully before altering only the artifact relevant to each case.