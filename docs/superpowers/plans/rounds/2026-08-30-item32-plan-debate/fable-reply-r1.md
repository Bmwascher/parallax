<!-- Fable panel-reviewer lane, round 1, reviewed at HEAD 061a2ee.
     Extracted verbatim from the lane's own transcript;
     evidence/fable-lane-six-rounds.jsonl was the source. -->

Review complete. All citations below were opened and verified this round against branch `item32-detached-dispatch`, HEAD `061a2ee`.

**The answer.** The mechanism is sound and I could not break the completion model. I found six defects the eighteen rounds did not name, all FIX-level, none a false-completion path. Verdict: FIX.

## 1. What a fresh reader gets wrong

- **Task 1's outer-command test cannot be run from its own text.** `test_the_documented_outer_command_works_on_this_host` runs the exact string at plan:96, which embeds `${CLAUDE_PLUGIN_ROOT}`. In PowerShell that is a PowerShell variable, not an environment variable, and an undefined one silently expands to EMPTY, turning the path into `/tools/dispatch-detached.ps1` (the current drive root). The task never says how the test binds it. The only in-repo precedent is `hooks\hooks.json:10` and `:22`, where the HARNESS substitutes before any shell sees it; the backlog records the skill-text convention as "Shape of a fix, none decided" (`docs/superpowers/plans/2026-07-27-0150-backlog.md:4496`). The plan's Global Constraints (plan:32) admit exactly two non-repo-verifiable harness facts; this is a third, relied on and unlisted. Consequence is bounded, a wrong resolution fails the launch loudly, but it fails exactly like item 58's mislocated-tool BLOCKED, in every repo where nothing resolves the variable.
- **Task 8's Files list omits a file its commit stages.** Step 5 creates `test_wrapper_probe_record.py` and step 6 stages it (plan:772), but the **Files:** line (plan:745) names only the record md. Round 7 caught this exact shape on Task 9.
- **Task 3 keeps prose the rewrite orphans.** Step 3 says keep everything from the `verified-override-dispatch` marker onward exactly as it is (plan:477). That span includes `SKILL.md:222-226`: "Every round writes FRESH round-numbered `<reply-file>`/`<transcript-file>` paths." After the rewrite those placeholders appear in no command; the reply is the hardcoded `$PSScriptRoot\reply` and freshness is carried by the fresh dispatch directory. The instruction as written cannot be followed. This is defect class 2 of this very debate, sitting in `SKILL.md` instead of the spec.

## 2. Is the mechanism right

- I re-derived the twelve states against the poll order at plan:132-141 and could not construct an input that reads a killed, hung, or unfinished round as complete. The liveness shape correctly copies `tools/kimi-lane-lock.ps1:219-236` (verified: LIVE/DEAD/UNMEASURABLE on `StartTime.ToUniversalTime().Ticks`).
- Simplification candidates each reopen a demonstrated defect: dropping the external receipt reopens round 7 (the caller reads the token out of the directory it already holds); dropping the token loses `launch-not-ours`; folding `pid-unreadable` into terminal states makes an unmade measurement look made. I find no simpler design that meets the same requirements.
- **One overclaim in region three** (plan:270-275): it names NO RECEIPT as "the case that command CANNOT clear", singular. A COMMITTED launch whose wrapper host has died while the client child survives is a second such case: `taskkill /PID <id> /T /F` on a dead root reports process-not-found and reaches no orphan. The poll classifies it safely (DEAD, then `no-exit-file` or `exit-nonzero`, never success), so only the remedy claim is wrong, but an operator following the region would conclude nothing is running while the client still holds the round.
- Minor, not a defect: `-Poll` never reads `$d\startticks`; the receipt carries the value. The artifact is contract only because the publish-order test asserts it.

## 3. Is the plan too large

No split required. The one clean seam is Tasks 5+6 (item 33), which the plan itself says neither depends on nor is depended on by item 32 (spec:319). The shared-file, shared-gate-profile argument for keeping them is real, and every task has its own oracle. If the user wants it smaller, that seam is the only place to cut.

## 4. The floor: not verified when all nine tasks are done

- The Kimi lane's detached dispatch never touches the real client: stub-run only, and the live kimi suite is opt-in and absent from Task 9's gates.
- **The Kimi REPLY path's encoding is unmeasured, and this is my strongest new finding.** The wrapper at plan:580 captures native stdout with `> $PSScriptRoot\reply`. On Windows PowerShell 5.1 that is decoded via `[Console]::OutputEncoding` (OEM code page) and re-encoded UTF-16LE; on PowerShell 7 it is UTF-8. A non-ASCII reply can be mangled between client and file, differently per host. The plan's deliberate no-preamble note (plan:588) reasons only about the OUTBOUND brief; `$OutputEncoding` does not govern the inbound decode. Task 8 step 3's live encoding round goes through Task 3's blocks and binds with the codex binder (plan:757-761), and the codex reply never crosses this boundary at all (`--output-last-message` is written by the client itself). So the one lane whose reply passes through the PowerShell redirect is the one lane with no live encoding measurement, in a repo that has paid for this class three times. The Kimi binding hashes the PROMPT from the session directory, so nothing refuses a mangled reply.
- The interrupted-launch residual (live untracked child, possibly no pid), the resume-after-kill recovery, and the thirty-minute policy are named, never exercised.
- Item 33's automatic mirror is a documentation-presence pin; no gate in this plan observes a session actually building without asking.
- `${CLAUDE_PLUGIN_ROOT}` resolution at real dispatch time is unverified by any test this plan writes.

## 5. What the eighteen rounds missed

Named above: the `${CLAUDE_PLUGIN_ROOT}` resolution gap, the Kimi reply encoding gap, the region-three remedy overclaim, the Task 8 Files omission, the orphaned `<reply-file>` prose. Two more:

- **The plan's own revision stamp is stale.** Plan:13 says "Revision 5 ... Four Sol rounds ... plus a two-lane poll", while plan:17 cites revision 13 and plan:903 records seventeen dispatches bound to `92c892f`. The record section fixed this class for its counts and the header escaped the fix. My terminal verdict below therefore cites the file at HEAD, not the stamp.
- **Spec staleness Task 9 does not sweep:** spec:208-210 says `test_the_brief_is_read_and_piped_as_utf8` "counts four exact strings"; the test holds five `>= 2` counts (`test_multi_model_verify.py:619-647`), and the plan itself says five (plan:30). No Task 9 grep or oracle touches it.

Searched and found clean: the Task 2 insertion point cannot break the trap pins (all three pinned literals at `test_multi_model_verify.py:983-997` end before and resume after the split); the coverage machinery matches its citations (`test_contract_coverage.py:611`, `:737`, `:749`); `Start-Process` is at zero occurrences in both documents today, as Tasks 3 and 4 claim; the spec scope-table oracle's regex matches the real rows; panels routing (`panels.md:49-53`), the mirror commit and its exit codes (`new-review-mirror.ps1:17-18`, `:1071-1091`), the backup-lane pins (`test_backup_lane.py:48-50`, `:137-148`), and both backlog headings (backlog:2634, :2712) are as cited.

UNVERIFIED, not folded into the verdict: whether Claude Code substitutes `${CLAUDE_PLUGIN_ROOT}` into skill text before the model sees it; the kimi client's stdout encoding; the Sol session history and the prior Fable poll (plan:17 attributes a statement to my lane that I do not hold; I take it as the driver's record, not as my claim).

## Verdict

**FIX**, on `docs/superpowers/plans/2026-08-30-item32-detached-dispatch.md` as it stands at HEAD `061a2ee` (its internal "Revision 5" stamp is itself one of the fixes). Smallest set:

1. Plan:93-101 and :473-475: state who resolves `${CLAUDE_PLUGIN_ROOT}` at dispatch and how Task 1's test binds it, or add it as a third named harness fact at plan:32.
2. Plan:757-761: extend Task 8 to one live non-ASCII round (or write-probe) through the Kimi wrapper on both hosts, or give the wrapper a byte-clean reply capture and state the reply file's encoding per host.
3. Plan:270-275: region three names the dead-launcher-live-client committed launch as a second case `taskkill /PID` cannot clear.
4. Plan:477: reconcile `SKILL.md:222-226`'s `<reply-file>`/`<transcript-file>` freshness prose with the tool-supplied paths instead of keeping it verbatim.
5. Plan:745: add `evals/multi-model-verify/test_wrapper_probe_record.py` to Task 8's Files list.
6. Plan:13: correct or commit-bind the revision stamp; plan:798-805: add the spec's "four exact strings" claim to Task 9's reconciliation list.
