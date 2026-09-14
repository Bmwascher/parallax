<!-- parallax:fable-reviewer whole-branch review, range 65f70c2..1ab7426, 2026-09-14. Retained from the agent's final message as delivered to the session (the harness transcript file for this agent was empty); the harness rendered `<` and `>` as HTML entities in delivery, restored here. -->

### Strengths

- Tests landed first and their oracles are real. `evals/multi-model-verify/test_multi_model_verify.py:2708` returns raw stdout so a silent case means byte-empty output, and the six new `TestHook` cases (2754-2845) cover both silent shapes (2774, 2785) and the four must-warn shapes in one method (2804-2807), each warning asserted by agent, build lane and `Lane:` (2766-2771). The Task 1 paraphrase incident was caught by the sonnet task review and repaired byte-exact (b96051d); every inline rationale block the plan mandated is present in the range (e.g. `test_flash_implementer.py:215-226`, `test_multi_model_verify.py:2740-2747`).
- The hook regex does what the six cases require. `hooks/superpowers-review-companion.ps1:42` is `(?m)^[ \t*_>-]*Lane:\**[ \t]*<escaped agent>(?=[ \t]|\r?$)` under `-cmatch` (line 44). Traced: `**Lane:** parallax:escalation-implementer\n` matches at `$`; the ledger line matches at the space before `(consented reroute, ...)`; a `Lane:` line naming `parallax:flash-implementer` fails on the escaped literal; `**Lane:**\nparallax:...` fails because `[ \t]*` cannot cross the newline and the second line has no `Lane:`; `...:other` fails the lookahead on `:`; an empty prompt (`[string]$null` at line 43) matches nothing. A missing `subagent_type` is `""` and falls through at line 35. The reviewer-fingerprint path (lines 64-76) is unchanged except for moving the `$prompt` read below the new block.
- Every raw-text pin sits on one physical line in the file it reads. Checked against the package: `test_flash_implementer.py:215-226` against `agents/flash-implementer.md:3` and `agents/escalation-implementer.md:3`; `:256-260` against `escalation-implementer.md:44, 56, 71`; `:235-245, 247-253` against `frozen-plan-format.md:12, 18, 25, 26, 27`; `:264-272` against `flash-implementer.md:171, 181, 192`; `:313-322` against `README.md:279, 283`. `test_seat_reshuffle.py:101-110` (`only with user consent` at `escalation-implementer.md:55`, `DEVIATIONS - must be \`none\`` at `:72`) and `:276-284` (`frozen-plan-format.md:41`, untouched) stay green.
- The named risk on contract regions is closed by evidence: `frozen-plan-format.md` carries no `contract:start`/`contract:end` marker at all (grep of the working-tree file), and `SKILL.md` is absent from the stat.
- The sweep is a gate, not a promise: `test_flash_implementer.py:299-310` applies `(?<![\w-])implementer\.md` per match over the live globs, which is exactly the shape that caught `contract_coverage.py:28` and `test_contract_coverage.py:189` after the hand sweep dropped them.
- The shared block in `agents/escalation-implementer.md:14-29` is the Flash block byte for byte, including both em dashes, and the envelope section (31-46) names precisely where that contract is suspended.
- The delete of `agents/implementer.md` is a separate session commit (5637ff3), keeping the Flash preflight tree clean and not measuring a Flash delete this cycle, as the plan required.

### Issues

#### Critical

None.

#### Important

None.

#### Minor

1. `agents/escalation-implementer.md:33-34` still opens the envelope section with "The frozen plan (or the consented reroute record) ENUMERATES this task's open decision points". That parenthetical is the one sentence on any live surface that tells a rerouted agent its consent record can carry decision points, and it contradicts `:43-46` (an EMPTY envelope delegates nothing) and `:54-58` (EMPTY by construction) in the same file. Mode diff catches any resulting DECISIONS entry as drift, so the cost is a wasted dispatch rather than a merged defect. No eval pins that sentence (grep of `evals/` for `consented reroute record` and `ENUMERATES`: none), so dropping the parenthetical on its line is safe. Plan-mandated text, so this is for the debate to fold in.

2. `agents/escalation-implementer.md:54-58` (route 2) does not say the dispatch prompt carries the ledger's `**Lane:** ... (consented reroute, <ledger path>)` line, while route 1 (`:50-53`) does name its field. `frozen-plan-format.md:25` and the hook (`:48-53`) both carry it, so the two routes are the same two routes in substance; the agent file is simply less explicit about the second. Ride.

3. `hooks/superpowers-review-companion.ps1:48-55`: on a `PostToolUseFailure` for the deleted `parallax:implementer`, the warning's first remedy is "add the line `**Lane:** parallax:implementer` from the plan", which can never silence a dispatch to an agent that no longer exists; only the second remedy (route to the Flash lane) applies. Non-blocking and plan-mandated. Ride.

4. Spec/plan divergences the debate brief should carry so they are not read as drift: the spec (`docs/superpowers/specs/2026-09-13-single-implementer-design.md:60-63`) names the shared block's section "The contract (outside the envelope)", but the heading sits inside the byte-identical block, so the file has `## The contract` (`agents/escalation-implementer.md:15`); and the spec's section 4 puts the agent-description pins in `test_flash_lane_is_the_declared_default`, which the frozen plan split into `test_agent_frontmatter_routes` (`test_flash_implementer.py:215`) on Astra R1 finding 11. The frozen plan governs both.

5. Gaps the package cannot close, named rather than assumed: (a) the six-gate run at head 1ab7426 is scheduled after the tasks and is not in the ledger yet, so tiers 1c, 1d and the backlog lint on the BACKLOG.md digest (`BACKLOG.md:96`) are unproven here; (b) the ledger records the doctor 7b weekly figure before Task 1 (98 percent) but not the after figure the plan's step 5 calls for; (c) `tool_input.subagent_type` reaching the hook in a live payload is not measured on this range. The existing fingerprint already reads `tool_input.prompt` from the same object and the harness's Agent tool names that field, so the risk is low, but the first real escalation dispatch after install is the proof.

### Ledger minors triage

None recorded. Two rulings are in the ledger, both sound:

- Copy-the-bytes rule for every later Flash dispatch (`progress.md:28`): ride, and worth carrying forward. The observation underneath it is the real finding: the wrapper's route and authorship checks proved a Flash-typed file that had silently lost 6 KB of mandated comments, so a byte check by hand is what caught it and nothing mechanical did. That belongs on item 105 or a new item, not just in this ledger.
- "Truncated package" refuted (`progress.md:35-37`): ride. `@@ -1,36 +1,76 @@` is the hunk span for a change confined to lines 1-66 plus ten trailing context lines on a 76-line file; the package I read ends its hunk on `$warn = @{`, which is that tenth context line.

### Assessment

Ready to merge: Yes

Every branch claim is borne out by the range with evidence on one physical line per pin, the hook's six shapes trace correctly under `-cmatch` and `(?m)`, and no contract region or SKILL.md moved; the only findings are one contradictory parenthetical in the escalation file (cheap to fold in during the debate) and three named evidence gaps that the plan's own remaining session steps cover.
