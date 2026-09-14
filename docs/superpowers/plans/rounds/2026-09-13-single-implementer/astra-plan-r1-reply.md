1. The remaining capabilities have destinations: consented reroutes already appear in `agents/escalation-implementer.md:3`, and the Flash contract requires exact transcription and route evidence at `agents/flash-implementer.md:22-33` and `agents/flash-implementer.md:113-136`. This matches `BACKLOG.md:101-120`. The deletion is explicitly a session action before dispatch in `docs/superpowers/plans/2026-09-13-single-implementer.md:487`, consistent with the unmeasured-delete statement at `agents/flash-implementer.md:102-103`. **PASS.**

2. The existing diff rule adjudicates decisions against the envelope; an empty envelope authorizes no decisions (`skills/multi-model-verify/SKILL.md:340-343`). The three claimed rule strings are contiguous in the proposed text at `docs/superpowers/plans/2026-09-13-single-implementer.md:545`, `docs/superpowers/plans/2026-09-13-single-implementer.md:557`, and `docs/superpowers/plans/2026-09-13-single-implementer.md:683`. The additional report pin has a separate defect in finding 11. **PASS.**

3. Comparing the quoted replacement against the current Flash file confirms identical shared-contract content, including em dashes (`docs/superpowers/plans/2026-09-13-single-implementer.md:515-530`; `agents/flash-implementer.md:19-34`). The suspension is explicit, the numbered headings survive, and all five seat-reshuffle strings remain contiguous (`docs/superpowers/plans/2026-09-13-single-implementer.md:534-577`; `evals/multi-model-verify/test_seat_reshuffle.py:101-110`). **PASS.**

4. The exemption accepts more than the specified line shape. Running the quoted hook under pwsh produces empty stdout for both `**Lane:**\nparallax:escalation-implementer` and `**Lane:** parallax:escalation-implementer:other`. The first crosses a newline through `\s*`; the second passes the insufficient suffix boundary (`docs/superpowers/plans/2026-09-13-single-implementer.md:825-827`). The design requires the exact type on one line (`docs/superpowers/specs/2026-09-13-single-implementer-design.md:114-118`).

   The dispatch condition, empty-prompt placement, and event registrations otherwise support the claim (`docs/superpowers/plans/2026-09-13-single-implementer.md:820-848`; `hooks/hooks.json:6-10`; `hooks/hooks.json:18-22`).

   **FIX:** “Replace Task 4’s `$laneLine` assignment with:”

   ```powershell
   $laneLine = '(?m)^[ \t*_>-]*Lane:\**[ \t]*' + [regex]::Escape($subagent) + '(?=[ \t]|\r?$)'
   ```

5. The three warning cases do fail against the current hook, and the proposed hook produces their expected outputs. Their assertions nevertheless check different content: only the first checks both lane names and `Lane:`; the other-agent case checks only the escalation name, and the deleted-agent case checks only the Flash name (`docs/superpowers/plans/2026-09-13-single-implementer.md:394-400`, `docs/superpowers/plans/2026-09-13-single-implementer.md:434-436`, `docs/superpowers/plans/2026-09-13-single-implementer.md:448-452`). Silence assertions also accept whitespace-only output because the helper strips stdout (`evals/multi-model-verify/test_multi_model_verify.py:2708`). None of the six cases detects finding 4.

   **FIX:** “Change `run_hook` to return `proc.stdout, proc.returncode`. In each warning case, assert that `additionalContext` contains the dispatched agent, `parallax:flash-implementer`, and `Lane:`. Extend `test_lane_line_naming_another_agent_still_warns` to run the same assertions for these four prompts:”

   ```python
   "**Lane:** parallax:flash-implementer\n"
   "**Lane:**\nparallax:escalation-implementer\n"
   "**Lane:** parallax:escalation-implementer:other\n"
   ""
   ```

   “Keep these inputs inside the existing method so the six-method count remains unchanged.”

6. The replacement’s six initial failing tests are consistent with the current source, and the heading and literal exceptions are supported by `agents/escalation-implementer.md:49-57`, `agents/implementer.md:1-53`, and the replacement assertions at `docs/superpowers/plans/2026-09-13-single-implementer.md:215-338`.

   The post-implementation sweep claim is false. Two included files retain matching paths: `evals/multi-model-verify/contract_coverage.py:28` and `evals/multi-model-verify/test_contract_coverage.py:189`. Both fall under `evals/**/*.py`, and neither receives an edit in Task 3 (`docs/superpowers/plans/2026-09-13-single-implementer.md:305-308`; `docs/superpowers/plans/2026-09-13-single-implementer.md:653-656`). Applying the quoted replacements in memory leaves exactly these two offenders.

   **FIX:** “Add both contract-coverage files to Task 3’s Files list and commit command. In each file, replace the exact fragment `agents/implementer.md and agents/flash-implementer.md already carry` with `agents/escalation-implementer.md and agents/flash-implementer.md already carry`.”

7. The quoted format replacement preserves the build-lane and ROUTE strings; the existing envelope sentence and pinned-lane wording sit outside the replaced span (`docs/superpowers/plans/2026-09-13-single-implementer.md:663-701`; `skills/multi-model-verify/references/frozen-plan-format.md:4`; `skills/multi-model-verify/references/frozen-plan-format.md:30`). The three resulting documents contain no `contract:start` regions, so this change does not alter the declared-region inventory checked at `evals/multi-model-verify/test_contract_coverage.py:793-801`. **PASS.**

8. Applying the Lane-note replacement in memory leaves the drift regex resolving to the same canonical literal. The parser’s input precedes the edited span (`tools/check-drift.ps1:295`; `agents/flash-implementer.md:168-170`; `docs/superpowers/plans/2026-09-13-single-implementer.md:600-613`). **PASS.**

9. The live sweep misses the two contract-coverage references identified in claim 6 (`evals/multi-model-verify/contract_coverage.py:28`; `evals/multi-model-verify/test_contract_coverage.py:189`). The doctor and drift “explicit none” statements are supported by their actual Flash-file references (`commands/doctor.md:152-157`; `tools/check-drift.ps1:291-300`).

   **FIX:** “Apply claim 6’s two replacements and include both files among the edited surfaces in the sweep report required by `docs/superpowers/plans/2026-09-13-single-implementer.md:917`.”

10. Applying the README edits in memory preserves both exact 0.13.0 strings and the escalation references required by `evals/multi-model-verify/test_seat_reshuffle.py:336-347`. Their source locations are outside the replacement spans (`README.md:33`; `README.md:93`; `README.md:101`; `docs/superpowers/plans/2026-09-13-single-implementer.md:703-745`). **PASS.**

11. **Additional finding: Task 2’s oracle masks broken agent rules, and its replacement cannot satisfy one pin.** The routing test combines agent and format assertions, while the empty-envelope test checks the pending format change before reaching any agent assertions (`docs/superpowers/plans/2026-09-13-single-implementer.md:258-289`). Task 2 expects both test names to fail, so broken agent changes can produce exactly its expected failure list (`docs/superpowers/plans/2026-09-13-single-implementer.md:640`).

   There is also a definite failure after Task 3: the pin requires `An empty envelope means an empty section`, but Task 2 inserts a newline before `section` (`docs/superpowers/plans/2026-09-13-single-implementer.md:289`; `docs/superpowers/plans/2026-09-13-single-implementer.md:572-573`). This contradicts Task 3’s green expectation at `docs/superpowers/plans/2026-09-13-single-implementer.md:764`.

   **FIX:** “Move the frontmatter assertions into a separate `test_agent_frontmatter_routes`; retain the format assertions in `test_flash_lane_is_the_declared_default`. Move the escalation-body assertions into `test_escalation_empty_envelope_is_zero_judgment`; retain the format assertion in `test_empty_envelope_is_zero_judgment`. Add those two new test names to Task 1’s expected failures, changing six to eight. Require both new tests to pass after Task 2. Replace the report’s two continuation lines with this single physical line:”

   ```text
      why, and the evidence behind it. An empty envelope means an empty section, stated explicitly.
   ```

UNVERIFIED: The complete pytest execution totals associated with claims 4–6 were not reproduced; Python is unavailable on this session’s PATH. The six hook scenarios were exercised directly under pwsh. The installed-superpowers canary additionally reads an installation outside the reviewed tree (`evals/multi-model-verify/test_multi_model_verify.py:2817-2835`), so the plan’s machine-specific `15 passed` assertion remains unverified (`docs/superpowers/plans/2026-09-13-single-implementer.md:903`).

No file instruction caused a pause, refusal, or change of scope. The plan’s explicit “REQUIRED SUB-SKILL” instruction is at `docs/superpowers/plans/2026-09-13-single-implementer.md:3`; I treated it as implementation-plan content under this brief’s evidence-only rule.