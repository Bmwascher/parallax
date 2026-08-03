• Let me read the plan file first.Now I've read the whole plan. Let me check the citations the plan makes. Key files to verify:

  1. `skills/multi-model-verify/references/kimi-reviewer-agent.md:21` — Skill deny list line.
  2. `skills/multi-model-verify/references/backup-lane.md:341-344` and `:345-353` — SKILL DISCOVERY bullet, confounded prior result.
  3. `evals/multi-model-verify/fixtures/kimi-round/fresh-wire.jsonl:13-18` — tool.call/tool.result shape.
  4. `tools/read-kimi-round-evidence.ps1:780, :803-805, :865-867, :877-879`.
  5. `evals/multi-model-verify/test_codex_context_probe.py:50-53, :55-61`.
  6. `evals/multi-model-verify/test_review_mirror.py:31-34`.
  7. `.github/workflows/skill-evals.yml:59-112` — powershell-hosts job.
  8. `docs/superpowers/plans/2026-07-27-0150-backlog.md` — item 10 heading at :577, status at :11-14, item 17 at :16-19.
  9. `evals/multi-model-verify/test_backup_lane.py:848-856` — retired pin.
  10. `evals/multi-model-verify/test_contract_coverage.py:651-664` — DECLARED_REGIONS.
  11. `docs/superpowers/plans/rounds/2026-07-31-kimi-code-swap/probe-record.md:92-96, :136-140, :170-190, :240`.

  Let me read these in parallel.

• I've read the plan in full. Now let me verify its citations against the files it names.

• Verified so far:
  - `kimi-reviewer-agent.md:21` — yes, `- Skill` is at line 21. And the deny list runs lines 11-27 — plan says "17 names running `:11-27`". Count lines 11-27: Bash, Write, Edit, WebSearch, FetchURL, EnterPlanMode, ExitPlanMode, Agent, AgentSwarm, AskUserQuestion, Skill, TaskList, TaskOutput, TaskStop, CronCreate, CronList, CronDelete = 17 names. ✓
  - backup-lane.md:341-344 — the "unprobed territory" instruction sits at :341-344 ✓. Confounded probe at :345-353 ✓ (probed 2026-07-31 with canaries at both project roots, reviewer reported no skills at all). Plan fact 8 cites `backup-lane.md:345-353` — checks.
  - fresh-wire.jsonl:13-18 — line 13 tool.call, line 14 tool.result with result.output ✓. Plan cites identifiers `parentUuid`, `toolCallId`, `traceId` at :13-18 — line 14 has parentUuid, toolCallId, traceId ✓.

  Note: plan's probe agent containment test (Task 3) asserts `"\n  - Skill\n" not in tools_block` for review agent and in probe file. Also asserts `"subagents: []"`. The review file has `subagents: []` at line 28 ✓.

  Note also: Task 3's test for the probe agent expects deny list to include Agent, AgentSwarm, Bash, Write, Edit, WebSearch, FetchURL — review file has all these ✓.

  Now the tools/read-kimi-round-evidence.ps1 citations: :780, :803-805, :865-867, :877-879.Verified:
  - `tools/read-kimi-round-evidence.ps1:780` — snapshot names multiset equality ✓ (fact 5).
  - `:803-805` — llm.request bounded from below (Count -lt 1 fails) ✓ (fact 6b).
  - `:865-867` — toolCount vs agent file's allowlist length ✓ (fact 6).
  - `:877-879` — systemPromptChars vs agent body LF-normalized length ✓ (fact 4).

  - `test_codex_context_probe.py:50-53` — the stale header is at lines 50-53 ✓ ("CI is Linux, so CI does not exercise these 155 cases at all... Backlog item 10 carries the fix"). Task 1 Step 3 says replace `:50-53` with the new header. The new test asserts "CI does not exercise these 155 cases at all" not in body — line 51 currently says "not exercise these 155 cases at all" — yes the sentence at :50-51 is "CI does not exercise these 155 cases at all" (split across lines but _norm presumably joins? Actually the string appears with a newline between "does" and "not exercise" — the test asserts the exact substring "CI does not exercise these 155 cases at all" is not in body. But the current file has "CI does\nnot exercise these 155 cases at all." — with a newline! `_norm` normalizes line endings to LF presumably, but does it strip newlines? If not, the assertion "CI does not exercise these 155 cases at all" not in body would pass even now, because the text has a line break inside the sentence. Hmm. That's the retired-sentence guard. Let me check _norm definition in test_backup_lane.py.

  Also Task 1's test asserts `"Backlog item 10 carries the fix" not in body` — line 52 of the probe file has "Backlog item 10 carries the fix," — that exact substring appears on one line ✓.

  And `test_review_mirror.py:31-34` — the mirror header lines 31-34 don't contain "CI does not exercise these 155 cases at all" nor "Backlog item 10 carries the fix". So the mirror file would currently pass both "not in body" assertions. The probe file's "CI does not exercise..." is split across a line boundary. Need to check _norm.

  Also `test_codex_context_probe.py:55-61` for the PARALLAX_PS_HOST selector — lines 54-60 are the POWERSHELL selector and pytestmark. The plan says copy the selector at `:55-61`. Lines 55-61: `or shutil.which...` through `def ps_host():` start at 63. Lines 54-61 cover the POWERSHELL assignment + pytestmark start. Close enough; the selector is at 54-55 actually ("PARALLAX_PS_HOST" is at line 54, not 55). Plan cites :55-61. The relevant env read is at line 54. Hmm — minor off-by-one. The selector idiom spans lines 54-55. Citation :55-61 includes line 55 which has the shutil.which part, and the pytestmark. Slightly imprecise but arguably within. Let me check what _norm is and the workflow file and backlog.

  Now check the workflow file for powershell-hosts job at :59-112 and the markers "PARALLAX_PS_HOST: powershell.exe" and "PARALLAX_PS_HOST: pwsh.exe", plus per-step "- name:" at list indentation ("\n      - name:").Good:
  - Workflow: `powershell-hosts:` at line 59, job ends at 112 (end of file) ✓. Both steps set `PARALLAX_PS_HOST: powershell.exe` (line 84) and `PARALLAX_PS_HOST: pwsh.exe` (line 100) ✓. Each step lists `evals/multi-model-verify/test_codex_context_probe.py` and `test_review_mirror.py` exactly once ✓. The step slice uses `tail.split("\n      - name:", 1)[0]` — the next `- name:` at 6-space indentation; here steps are at 6-space indent (`      - name:`) ✓. The YAML `run: >` folds the module names onto separate lines — the slicing works on raw text, so `test_review_mirror.py` appears once per step ✓.
  - `_norm` joins on whitespace — so "CI does not exercise these 155 cases at all" IS present in the normalized body of test_codex_context_probe.py (lines 50-51 "CI is Linux, so CI does / not exercise these 155 cases at all." → normalized "CI is Linux, so CI does not exercise these 155 cases at all."). ✓ And the new test asserts this string not in body → fails now as expected. Step 2 expects FAIL on exactly that assertion. ✓

  Wait — but the mirror file's header (lines 31-34) doesn't contain that sentence. After Task 1 Step 4 replaces the mirror header with the new text, "powershell-hosts" must appear in the mirror body — the new header includes "powershell-hosts" ✓.

  Also the new test asserts `steps[host].count(rel) == 1` — each step currently contains each module path once ✓.

  Now check backlog item 10 heading at :577 and status at :11-14, and item 17's heading and `:16-19` paragraph, plus test_backup_lane.py:848-856 pin, test_contract_coverage.py:651-664 DECLARED_REGIONS, and probe-record.md citations (:92-96, :136-140, :170-190, :240).Findings so far on citations:

  1. Task 5 cites `test_backup_lane.py:848-856` as "the pin at :848-856 that asserts the retired sentence". Actually the retired "unprobed territory" pin spans lines 848-853 (the assert at 848-853). Lines 854-856 are the start of the NEXT pin's comment ("The old 'LATENT surface' pin..."). So the citation :848-856 slightly over-ranges: the retired pin assert is :848-853; the comment block above it is :842-847. Step 1 says "delete the pin at `:848-856` that asserts the retired sentence". Deleting :848-856 would delete the assert plus the first two lines of the next pin's comment, leaving a dangling comment ("`--skills-dir` is a MITIGATION..." assertion would lose its opening comment lines and the assert at :861 stays). Minor imprecision — deleting exactly lines 848-856 would corrupt the following comment block but not the code; a zero-judgment implementer told "delete the pin at :848-856 and put in its place [new asserts]" would insert the new asserts then the orphaned comment remainder ("# presence says nothing about whether anything is actually being / # merged. Its successor is stronger..." from :855-856 onward... wait lines 855-856 are part of the old LATENT comment: lines 854-856 are comment, 857-860 comment, 861 assert). Deleting 848-856 removes the assert (848-853) and comment lines 854-856, leaving comment 857-860 ("# `--skills-dir` is a MITIGATION...") preceding assert 861 — still syntactically fine. So it's a cosmetic citation imprecision, not a false-clean path. Worth a minor note.

  Hmm, actually more precisely: does the "pin" include its comment at :842-847? The comment at :842-847 describes the retired pin ("The retired 'unprobed territory' pin carried a DISPOSITION..."). If the implementer deletes only :848-856, the comment at :842-847 stays, now describing a pin that no longer exists — and it says "Its successor names..." which would be stale. But the new asserts inserted in place have their own comment. Minor staleness, not a correctness defect of the measurement. The plan itself says "delete the pin at :848-856 that asserts the retired sentence" — the assert of the retired sentence is exactly :848-853. Not dangerous. I'll flag as a minor citation-range issue.

  2. Backlog item 10 heading is at :577 ✓ exactly matches. Status block at :11-14 ✓ and matches; item 17 in Open list ✓. The `**Item 17 is FIRST**` paragraph is at :16-19 ✓.

  3. DECLARED_REGIONS at test_contract_coverage.py — need to confirm the list spans :651-664 and where to add. The read shows 651-669 are entries; the declaration presumably continues past 669. Let me check lines 669-692 to see the end. Also need to check whether "home-skill-root-disposition" would be added correctly — trivial.

  4. Fact 2: backup item 17's wording stale — check item 17's text to confirm. Let me read item 17 around line 24-60.

  5. probe-record.md citations: :92-96 (27 skill dirs, KIMI_CODE_HOME doesn't relocate; --skills-dir help text UNVERIFIED at :240), :136-140 (permission.set_mode auto), :170-190 (session log llm config line carries systemPromptChars and toolCount; wire llm.request carries hashes; tools_snapshot carries schemas). Need to verify.

  Let me read those.Verified:
  - probe-record.md:92-96 — `~/.agents/skills/` not relocated by home relocation, --skills-dir help text quote at :93-94. But plan fact 1 says "holds 27 skill directories on this machine (`probe-record.md:92-96`)". Lines 92-96 do NOT mention 27 skill directories. Where does the count 27 appear? Let me grep the probe-record for "27".

  - :136-140 — permission.set_mode auto ✓ (:137-139).
  - :170-190 — llm config line carries systemPromptChars and toolCount ✓ (:172-175); wire carries hashes and snapshot schemas ✓ (:177-186).
  - :240 — UNVERIFIED item 1 ✓.

  Check "27" in probe-record.The grep for "27" in the probe-record returned no "27 skill directories" — only port and SHA hits. The plan's measured fact 1 says "holds 27 skill directories on this machine (`probe-record.md:92-96`)". Lines 92-96 say nothing about 27 directories. Let me search more broadly for where the 27 count is recorded — maybe in the backup-lane.md or elsewhere. Let me grep the whole repo for "27 skill" or "27 entries".Confirmed: the "27 skill directories" figure is recorded at `docs/superpowers/plans/2026-07-27-0150-backlog.md:41` and `docs/superpowers/plans/rounds/2026-07-31-kimi-code-swap/kimi-live-debate-record.md:39`, NOT at `probe-record.md:92-96`. The plan's fact 1 cites `probe-record.md:92-96` for a compound claim — the relocation part is at :92-96 but the 27-count is not there. That's a citation defect per the brief ("A plan that cites a line that does not say what the plan says it says is a defect"). Severity: low for the measurement itself (the count exists elsewhere in the repo), but the brief's rules say a miscited claim is a defect. However, does it affect the false-clean? Task 4 Step 4 requires "Confirm ~/.agents/skills/ holds 27 entries" — if the count were wrong, the restoration check would fail closed (stop), not false-clean. So it's a citation defect, not a dangerous one.

  Also Task 4 Step 4's check: "holds 27 entries" — hardcoded 27. If the user's root legitimately changes between measurement and the run (user installs a skill), the check fails — fail-closed, fine. Not a false-clean path.

  Now check remaining citations:

  - Fact 7: "--skills-dir loads skills ... 'instead of auto-discovered user and project directories', per its own help text" — probe-record.md:93-94 has that quote ✓. "Whether it actually suppresses a planted skill is listed as UNVERIFIED (probe-record.md:92-96, :240)" ✓ (:96-97, :240).

  - Fact 8 cites backup-lane.md:345-353 for the confounded result ✓ (lines 345-353 describe the 2026-07-31 probe with canaries at both project roots, indistinguishable, reviewer reported no skills available).

  - Fact 9 cites probe-record.md:136-140 ✓.

  - Fact 11: `.github/workflows/skill-evals.yml:59-112` runs powershell-hosts on windows-latest, passes test_codex_context_probe.py and test_review_mirror.py under both interpreters ✓ (:59-112 confirmed). "It landed at 6a462f9" — commit hash, can't verify from files (UNVERIFIED-ish but it's a git claim; not needed for the measurement).

  - Task 1: `test_codex_context_probe.py:50-53` ✓ (the stale header is exactly lines 50-53). `test_review_mirror.py:31-34` — hmm. Lines 31-34: "Guarding only on a PowerShell host being present was not enough: the CI runner ships pwsh, so these cases ran on Linux and failed there for a second, different reason. See the probe suite's header for the full sequence and for the coverage cost this skip accepts." That is the header to replace? The plan's replacement says the mirror header "repeats the false claim in its own header and points readers at item 10". Lines 31-34 don't contain the false claim text ("CI does not exercise these 155 cases at all" or "Backlog item 10 carries the fix") — it says "See the probe suite's header for the full sequence and for the coverage cost this skip accepts". The coverage cost pointer is at line 34 ("for the coverage cost this skip accepts"). The plan says replace :31-34 with the new header. That works — the new header for the mirror references "See the probe suite's header for the full sequence" ✓. And the new test only requires the mirror to name "powershell-hosts" and not carry the two retired sentences — which the mirror never had. So fine. But wait — does the new test pass BEFORE Task 1 Step 4 on the mirror? The mirror currently doesn't contain "powershell-hosts" → fails that assert. Fine, expected failure.

    Task 1 Step 2 expects: "FAIL on `assert "CI does not exercise these 155 cases at all" not in body`". In the current probe file, normalized body contains "CI does not exercise these 155 cases at all" (lines 50-51 joined by _norm) ✓. But note the assertion order in the test: the loop `for rel in covered` iterates over test_codex_context_probe.py first, and asserts workflow slicing first. The workflow slice asserts `marker in workflow` — markers exist ✓. Then `tail.split("\n      - name:", 1)[0]` — for the pwsh step, the step is at end of file (line 112 is last), so split won't find "\n      - name:" and split(...)[0] returns the whole tail — fine, still one occurrence each ✓. But wait: for the powershell.exe step, tail after marker at line 84 contains "run: > python -m pytest ... -q" then "\n      - name: PowerShell-facing tests under PowerShell 7" at line 98 — split works ✓.

    One subtlety: the test's `steps[host].count(rel) == 1` — the pwsh step tail includes trailing content to EOF; count of each module = 1 ✓.

  - Task 3: probe agent test asserts probe deny list includes FetchURL, Agent, AgentSwarm, etc. Review file denies those ✓. The probe agent file is a copy with Skill moved. Test also asserts `"\n  - Skill\n" in tools_block` where tools_block is everything before "disallowedTools:" — includes the name/description frontmatter; fine.

    Note: `test_the_review_agent_still_denies_skill` asserts `"\n  - Skill\n" not in tools_block`. In the review agent file, tools are Read, Grep, Glob, ReadMediaFile, TodoList ✓ no Skill.

  - Task 3 interface: "an agent file identical to kimi-reviewer-agent.md except that Skill moves... giving a SIX-name allowlist" — review has 5 tools + Skill = 6 ✓. But Step 3 says tools become `[Read, Grep, Glob, ReadMediaFile, TodoList, Skill]` ✓.

  - Task 4's nonce: `[System.Guid]::NewGuid().ToString("N")` gives 32 lowercase hex ✓ matches `\A[0-9a-f]{32}\z`.

  - Task 5: `test_contract_coverage.py:651-664` — DECLARED_REGIONS region list. I read :645-669; entries run well past 664. The citation :651-664 is where DECLARED_REGIONS entries are; adding two ids there. Slight imprecision (the list spans beyond 664 — need to check where it ends; file is 692 lines). Let me check lines 669-692.

  - Task 5 Step 3: replace `backup-lane.md:341-344`. Current lines 341-344: "...`~/.agents/skills/` lives in the user's own home, is not relocated by KIMI_CODE_HOME, and NOTHING this lane runs removes it. Enumerate that root before round 1 and record what it holds; a non-empty one is unprobed territory, recorded as such rather than assumed absorbed by the tool allowlist." The plan's replacement text keeps "`~/.agents/skills/` lives in the user's own home, is not relocated by KIMI_CODE_HOME, and NOTHING this lane runs removes it." as the FIRST lines, then adds two contract regions, and DELETES the "Enumerate that root before round 1... unprobed territory" sentence. Wait — but the new test pin (Task 5 Step 1) asserts the FIRST sentence is present: "`~/.agents/skills/` lives in the user's own home, is not relocated by `KIMI_CODE_HOME`, and NOTHING this lane runs removes it." ✓ present in replacement. And the limit region says "Enumerate it before round 1 and record what it holds." — keeps the enumeration instruction ✓.

    But there's a subtlety: the current text at :341-344 is part of a larger bullet that begins earlier (the SKILL DISCOVERY bullet spans :330-354+). Lines 345-354 (the `--skills-dir` mitigation sentence and confounded probe record) are NOT replaced — they stay. And the pin at test_backup_lane.py:861-862 ("`--skills-dir` is a MITIGATION whose effect is UNMEASURABLE in this configuration, not a control") pins :345-346 which stays. Hmm — but under the NOT REACHABLE branch, Task 4 measures D and C both not-found, so `--skills-dir` suppression remains unproven, and the mitigation sentence stays accurate. Under the SUPPRESSED BY THE FLAG branch, the plan stops. OK.

    Wait, actually there is an issue: under NOT REACHABLE, the C cell (flag on) produced a valid not-found. Does that make `--skills-dir` "measured as suppression"? No — C is not-found either way; you can't distinguish suppression from non-delivery when D is also not-found. The mitigation sentence stays. Fine.

  - Task 6: backlog item 17 heading change; item 17 heading is at :24 ("## 17. `~/.agents/skills/` reaches the Kimi lane and nothing measures it"). The plan says change heading to `## 17. ... — DONE, 0.20.0` ✓. And delete `**Item 17 is FIRST**` at :16-19 ✓.

  - Fact 2 claim: "Backlog item 17's own wording is stale on this point" — need to check item 17's wording. Let me read item 17 body.

  Now the core: Task 4 gate analysis. Is there any path to a false clean (NOT REACHABLE when the root actually reaches the reviewer)?

  Cells:
  - A: reviewer agent, one-word prompt, --skills-dir passed, no canary anywhere. Baseline.
  - B: reviewer agent, one-word prompt, --skills-dir passed, canary in real home.
  - C: probe agent, invocation prompt, --skills-dir passed, canary in real home.
  - D: probe agent, invocation prompt, --skills-dir omitted, canary in real home.
  - E: probe agent, invocation prompt, --skills-dir omitted, canary in <debate-home>/skills/.
  - E2: resume of E, invocation prompt with absent name.

  NOT REACHABLE requires:
  1. E VALID (tool.call for exact canary name + matching tool.result) and result carries nonce.
  2. E2 VALID and canonicalizable not-found result.
  3. C and D VALID and their results equal E2's under frozen comparison.
  4. A, B, C, D fire on NEITHER primary readout.

  Potential false-clean paths:

  (a) E's positive control: canary planted in `<debate-home>/skills/`. Is that root actually discovered by the client when --skills-dir is omitted? If `<debate-home>/skills/` is NOT a discovery root for the client, then E produces a not-found result, its tool.result would match E2's shape (both not-found)... wait, but then E's result would NOT carry the nonce, and the VOID branch requires E's result to carry the nonce unconditionally. E fails → VOID, not NOT REACHABLE. Fail-closed. Good.

  But subtle: in E, the model invokes Skill with "parallax-home-root-canary" — if the debate-home root IS discovered, the result carries the canary body with nonce → positive. Good.

  But wait: is `<debate-home>/skills/` actually one of the four roots? The context says four roots: `.agents/skills/`, `<debate-home>/skills/`, `~/.agents/skills/`... Actually backup-lane.md:330 lists `.agents/skills/`, `<debate-home>/skills/` and `~/.agents/skills/` (three mentioned there; the fourth root per context is something else — maybe project `.kimi-code/skills` or plugin skills). Anyway, cell E's premise is that `<debate-home>/skills/` is a discovered root. Is that established in the repo? backup-lane.md:339 says "`<debate-home>/skills/` is created empty by the builder" — implying it's a root the lane controls. But is it established that the client DISCOVERS skills there? If the client does not discover that root at all, E fails → VOID, fails closed. Fine.

  Hmm, but here's a subtler issue: if `<debate-home>/skills/` is discovered but `~/.agents/skills/` is not, E fires, D not-found → NOT REACHABLE — correct answer. If both discovered: D carries nonce → REACHABLE. Correct.

  (b) The system-prompt delivery path in cells B/C/D with Skill invocation: if the canary body is injected into the system prompt, readout 2 fires (systemPromptChars ≠ agent body length) → gate catches (B fires → REACHABLE EVEN AS CONFIGURED; C/D fire → not NOT REACHABLE). But wait — readout 2 compares systemPromptChars against agent file body length. If the canary is injected into the system prompt for the reviewer agent in B... readout 2 fires ✓. What if the canary content is injected into the TOOL SCHEMA (Skill tool description enumerates skills)? Then readout 2 wouldn't fire, but toolsHash would differ (readout 3, corroboration only). However cells C/D/E invoke Skill by name — an invocation-time lookup would return the body → nonce in tool.result → D positive → REACHABLE. So invocation covers that path.

  (c) What if the Skill tool result does NOT echo the skill body into the wire (e.g., the client loads skill content into a subsequent message without a tool.result record, or the result is suppressed)? Then E would produce a tool.call + tool.result, but the tool.result doesn't carry the nonce → VOID (E's unconditional requirement fails). Fail-closed. But wait — what if the client delivers the skill content to the model NOT via tool.result but via some other context mechanism, so the model replies with the tool's result verbatim (which contains the nonce) — the model's REPLY text appears in the wire as a content.part text record! Readout 1 searches the whole wire.jsonl for the nonce, so the model's reply containing the nonce would fire readout 1. In E, the prompt says "reply with the tool's result verbatim" — if the model actually received the canary body through any channel, its reply would very likely contain the nonce → readout 1 fires in E. But does the gate's NOT REACHABLE branch require E's tool.result specifically to carry the nonce? Yes: "cell E is VALID and its result carries the nonce" — result, i.e., tool.result. If delivery happens through a non-tool.result channel (e.g., skill content appended to the next user message), E's tool.result would lack the nonce → VOID, not false clean. OK fail-closed again.

  Hmm, but actually there's a subtle one: what if in E the tool.result lacks the nonce BUT the model's reply carries it (readout 1 fires for E)? VOID branch says "Cell E does not produce a tool.call ... AND a matching tool.result carrying the nonce" → VOID. Correct — instrument can't validate → no conclusion.

  (d) D cell with --skills-dir omitted: could the client still not read ~/.agents/skills/ because KIMI_CODE_HOME relocation changes the user-home resolution? Fact 1 says KIMI_CODE_HOME does not relocate it ✓ measured.

  (e) The nonce search: readout 1 searches wire.jsonl and kimi-code.log raw bytes for the literal `PARALLAX-CANARY-<nonce>`. The canary SKILL.md carries the nonce twice ✓. If the client reads the skill and sends it, the nonce appears. Case sensitivity: nonce is lowercase hex, prefix uppercase — raw byte search for exact literal ✓. What if the client transforms content (e.g., escapes, or truncates the description)? If the Skill tool result includes only the name+description frontmatter, the nonce is in BOTH the description line and the body ✓ — description carries "PARALLAX-CANARY-<nonce>". Good — the description field carries the nonce too (line 99). So even a metadata-only advertisement in the system prompt or tool schema carries the nonce... wait, but if it's in the system prompt, readout 1 wouldn't see it (wire only carries systemPromptHash, not text) — readout 2 catches that via systemPromptChars. If it's in the Skill tool schema (tools_snapshot), the snapshot DOES carry the exact schema text into the wire (fresh-wire.jsonl:10 shows llm.tools_snapshot with full descriptions). So a schema-advertised canary → nonce in wire → readout 1 fires ✓. Nice.

  But wait — readout 1 for cell B: B runs the reviewer agent which has Skill DENIED. tools.set_active_tools and llm.tools_snapshot wouldn't include Skill at all. If skills are advertised only through the Skill tool schema and Skill isn't offered, B stays silent even if the root is read. That's why B is only "the lane as configured" — and C/D cover the offered case. Fine, design intent.

  (f) Now a potential false-clean: cell C vs D ordering and session/home reuse. Each fresh cell gets its own throwaway home ✓. Same workspace path? "same workspace path" — cells run in the same working directory. Sessions per home. OK.

  (g) E2 resume: validator RESUME form. E2's prompt uses skill name `parallax-absent-canary-<nonce>` — contains the nonce! So the turn.prompt and context.append_message in E2's wire WILL contain the nonce string (as part of "parallax-absent-canary-<nonce>"). And the searched token is `PARALLAX-CANARY-<nonce>` (uppercase prefix). "parallax-absent-canary-<nonce>" — lowercase "canary". The search token is "PARALLAX-CANARY-<nonce>" — does "parallax-absent-canary-abc123..." contain "PARALLAX-CANARY-abc123"? No — case differs ("absent-canary" lowercase vs "PARALLAX-CANARY" uppercase). So no cross-contamination on the token itself. But E2 shares E's home and session, so E2's wire.jsonl is the SAME file as E's (appended). Readout 1 for E searches the whole wire — including any earlier content. E's wire contains E2's prompt with "parallax-absent-canary-<nonce>" — but again case mismatch with the searched token. OK.

  Hmm wait — but there's a bigger one: E2 resumes E's session in the same home. Readout 1 for E is taken after step 5 (before E2). The gate requires E's tool.result carries the nonce. Fine.

  (h) A false-clean via the frozen comparison: C and D results must equal E2's canonicalized result. If the client's not-found result for a skill in a searched-but-empty root differs from a skill whose name exists nowhere... E2's name exists at no root; D's name exists at the real-home root (if reachable). If the root is reachable AND the client returns a not-found result that differs in some field from E2's (e.g., an error field saying "found but unreadable")... then D's result ≠ E2's → D is FAILED (not negative) → not NOT REACHABLE. Fail-closed ✓. If root reachable and found, D's result carries the nonce → REACHABLE ✓.

  But here's the tricky one: what if the client, when --skills-dir is omitted, discovers the real-home canary but the Skill invocation result for a FOUND skill is delivered WITHOUT the nonce — e.g., result says "skill loaded: parallax-home-root-canary" with the body delivered into a subsequent system/reminder message rather than the tool result? Then D's tool.result has no nonce and doesn't match E2's not-found shape → D FAILED → not NOT REACHABLE. Fail-closed ✓. Unless... D's "found but content elsewhere" result coincidentally matches E2's shape? If a found skill returns the exact same result payload as a not-found (after name substitution), then the client is indistinguishable... that would mean the tool result for found vs not-found is identical modulo name — in that case E would also produce that same result for its found canary, E's result wouldn't carry the nonce → VOID. Fail-closed ✓.

  (i) What about the possibility that cell D finds the skill but the model doesn't call with the EXACT name (e.g., calls "Skill" with different arg)? FAILED, not negative ✓.

  (j) Cell validity checks "wire slice" — how is the slice determined for a fresh cell? Presumably the validator handles it. The plan cites the validator. OK.

  (k) One more: cell B fires on readout 2. systemPromptChars comparison — but B runs the reviewer agent file. If the real-home canary is merged into the system prompt, systemPromptChars ≠ agent body length → the VALIDATOR fails the round (route-attribution failure, per fact 4). The plan says readout 2 is "does systemPromptChars equal..." — the driver records it. If it doesn't equal, B fires → REACHABLE EVEN AS CONFIGURED. ✓.

  (l) False clean via the "same prompt" clause: cells C, D, E use the invocation prompt verbatim ✓.

  (m) A subtle one: cell D with `--skills-dir` omitted — the client then auto-discovers user and project directories, including the PROJECT roots `.agents/skills` and `.kimi-code/skills` in the workspace (the throwaway mirror of the repo). If the repo mirror contains skills (e.g., the repo's own `skills/` directory is not a client discovery root — roots are `.agents/skills` etc.), could the model open the user's 27 real skill directories? The prompt names one skill exactly; exposure noted in plan ✓.

  (n) What about cell D picking up the canary through the MODEL reading the file with Read rather than via Skill? The probe agent HAS Read. The prompt says "Invoke your Skill tool with the skill name...". If the model instead Reads the canary file... it doesn't know the path (~/.agents/skills/parallax-home-root-canary/SKILL.md) — the nonce/name wouldn't tell it the location. It could Glob... unlikely, and validity gate requires the Skill tool.call ✓.

  (o) E's plant: "Plant the same canary in <debate-home>/skills/ for this cell only, by a plain directory copy inside the throwaway home". Wait — `<debate-home>` is the KIMI_CODE_HOME throwaway home, and `<debate-home>/skills/` is a discovery root. Copy from where? Presumably copy of the canary content (same nonce). But the harness tool refuses to plant outside... the tool accepts -Root for tests; the plan says E uses a plain directory copy, not the tool. Open question 1 acknowledges this. The canary content must carry the SAME nonce ✓ ("same canary", "same nonce" per cells table).

  Hmm — but wait: does E's home removal happen? It's a throwaway home, discarded. Fine.

  (p) Step 4: verify real home restored — 27 entries, hardcoded. If a canary removal fails, the Remove tool exits nonzero and the finally throws ✓; then step 4 checks count. Fail-closed.

  (q) One more false-clean candidate: E's positive control proves the instrument can detect a canary at `<debate-home>/skills/` with the probe agent and no --skills-dir. D is the same configuration but the canary at ~/.agents/skills/. The only difference is the root. So D-silence + E-fire isolates the root variable ✓. 

  But: is it established that `~/.agents/skills/` would be discovered as a "user directory" when --skills-dir is omitted? The help text says auto-discovered "user and project directories". Whether `~/.agents/skills/` is the "user directory" the client reads — that's exactly the open question being measured. Good.

  (r) Potential confound: E2's calibration happens AFTER E, in the same warmed session. Open question 4 addresses: warmed path can only make C/D fail to match → fails closed. Hmm, is that right? If warming changes the result shape between E2 and C/D (fresh sessions), C/D (fresh, first-call) results might differ in shape from E2 (resumed) even when all are genuine not-founds → C/D FAILED → not NOT REACHABLE. Fail-closed ✓.

  (s) The comparison substitution: "the requested skill identifier is replaced by a fixed placeholder in both sides". E2's result contains "parallax-absent-canary-<nonce>", C/D's contain "parallax-home-root-canary". Replace each requested identifier with placeholder, compare ordinally ✓. But what if the not-found result embeds a per-request nonce or timestamp beyond the named identifiers? Then C/D won't equal E2 → FAILED → fail-closed ✓.

  (t) One genuine remaining hole candidate: the gate's NOT REACHABLE requires "cells A, B, C and D fire on NEITHER primary readout". Readout 1 = nonce in wire/log; readout 2 = systemPromptChars equality. What about a delivery path that (i) doesn't put the nonce in the wire, (ii) doesn't change systemPromptChars, and (iii) doesn't respond to the named invocation? E.g., the client reads the skill root and injects skill content as a `context.append_message` with origin "injection" (like the permission_mode reminder at fixture line 8) — that WOULD put the nonce in the wire → readout 1 fires ✓. Or injects into the system prompt without changing... no, systemPromptChars must change if text is added. Unless the client replaces other content to keep length constant — absurd. Or the client passes skills through a side channel not logged in wire.jsonl or the log — then the model has the content but nothing records it. In cells C/D, though, the named invocation asks the Skill tool — if the client resolves skills via this side channel, the tool result would carry the body → nonce. Unless the tool result doesn't echo content but the model's reply does ("reply with the tool's result verbatim") → model reply text in wire carries nonce → readout 1 fires ✓. Actually — readout 1 searches the wire for the nonce, and the model's reply is in the wire. So even a weird delivery that reaches the model surfaces in the reply, provided the model obeys "reply with the tool's result verbatim". If the model disobeys and doesn't echo... then cell validity: was there a valid tool.call/result? If the client found the skill via a side channel, there might be no Skill tool.call at all → cell FAILED → fail closed. If there is a tool.call+result with no nonce but model got content via side channel and didn't echo it — cell valid, result matches E2's not-found shape → false clean! But wait: would E catch this? In E, the same delivery mechanism applies to `<debate-home>/skills/`. If the side channel delivers E's canary to the model without echoing into tool.result, E's tool.result lacks the nonce → VOID. E only validates if the tool.result carries the nonce. So any delivery mechanism that reaches the model in D also applies in E; if it leaves tool.result nonce-free, E fails → VOID. The only asymmetric case: a delivery mechanism that works for ~/.agents/skills/ but not <debate-home>/skills/ — but that's precisely "not reachable via the measured path"... no wait, if the mechanism works for the real home root but not the debate-home root, then E's positive control fails (VOID), never NOT REACHABLE. So the gate structure makes E the witness for whatever D's delivery mechanism is, as long as the mechanism is root-independent. If the client uses DIFFERENT delivery mechanisms per root (e.g., real-home skills injected into system prompt silently, debate-home skills via tool), then: D's canary injected into system prompt → systemPromptChars changes → readout 2 fires for D → not NOT REACHABLE ✓. Injected into wire-recorded message → readout 1 fires ✓. Delivered invisibly to model without any record → the model knows it, but D's invocation of Skill... the Skill tool would still do its lookup and return the body → nonce in result. Hmm, for the Skill tool to return not-found for D's canary while the real-home root IS read through another channel — that other channel would have to leave no trace in wire, log, systemPromptChars, or the reply. And in E, the equivalent trace for the debate-home root must fire (E requires nonce in tool.result). Since the channels differ per root in this hypothetical, E firing doesn't prove the real-home channel leaves a trace. So: a client that (1) reads ~/.agents/skills/, (2) delivers it to the model through a channel that produces zero record in wire.jsonl/kimi-code.log and zero systemPromptChars delta, and (3) whose Skill tool nonetheless answers not-found for the named canary... The model's reply: the prompt says "reply with the tool's result verbatim". If the tool said not-found, the model replies SKILL-NOT-FOUND even while "knowing" the skill via the invisible channel. That's a conceivable false clean, but it requires a delivery channel with no wire/log record at all — everything the repo has measured shows skill content reaching the model travels through either the system prompt (readout 2) or tool records (readout 1). The plan's fact 6c acknowledges the invocation-time-lookup possibility and covers it. Is there a recorded delivery path in this repo that bypasses both? The fixture shows context.append_message injections ARE recorded in the wire. So a truly unrecorded channel would contradict the measured record model ("every fact is inside a file created by and named after this round's own session", probe-record.md:188-191). I think the gate is as tight as the evidence supports. This residual is inherent to any black-box measurement and is bounded by the disposition-limit region in Task 5 ("bound to what the probe reached... does not establish that a later release leaves that root unread"). Actually the limit region doesn't quite say "or through a channel the wire does not record". But the branch requires the root to reach the REVIEWER while leaving no trace anywhere and while the Skill tool denies knowledge — a contradictory client behavior. I'll note it as a theoretical residual, not a FIX.

  (u) Now check the write-probe leg: "Ask the contained agent to create a named marker file; require an explicit refusal in the reply, the marker absent on disk, and an empty mirror status delta." "empty mirror status delta" — references the review mirror tooling. This is a containment check on the probe agent; failure → presumably stop. The plan doesn't explicitly say what happens if the write-probe fails — "before cell C uses it... its containment is verified before use" implies a failed write-probe stops the probe (cells C/D/E never run) → no false clean. Fine, though the gate branches don't name a write-probe-failure outcome explicitly. Slight underspecification: what does the driver record if the write-probe leg fails? Presumably abort. Not a false-clean path since it precedes the cells.

  (v) Task 4 Step 3's snippet: `if (Test-Path -LiteralPath $stateFile)` in the finally — if Plant failed before writing the state file but after creating the directory, Plant's own transactional rollback handles it (Task 2). If Plant created the directory and crashed WITHOUT rollback (hard fault), no state file exists → finally skips removal → canary left. The plan acknowledges: "the only surviving residue path is hard host termination, which the canary's own body addresses". OK.

  But hmm — one gap in the finally: if Plant succeeded (state file written), then Remove runs with -Root $root -State $stateFile. If removal fails (exit nonzero), throw. Fine. But what if the Remove tool's guards refuse because a foreign entry appeared (e.g., antivirus drops a file)? Removal fails → throw → driver alerted. Fail-closed ✓.

  (w) Cell B runs with the REVIEWER agent file — the real lane agent. It dispatches against the mirror workspace? "same workspace path" — which workspace? The debate mirror presumably. Fine.

  (x) Validator for probe cells: fact 6 says toolCount must equal the agent file's allowlist length — probe agent has 6 → validator works unchanged pointed at probe agent file ✓ (Task 3 interface note). But wait — the validator also checks snapshot names equal the active allowlist by multiset equality (rule 12). For the probe agent, active allowlist includes Skill; snapshot would include the Skill schema — fine.

  One more check on the validator: does the FRESH form require `turn.prompt` count == 1 (:797-800)? Each cell is one dispatch with one prompt ✓. For E2 RESUME form — also exactly 1 turn.prompt ✓.

  Also rule at :882-888: RESUME hash continuity — E2's toolsHash/systemPromptHash must equal prior state's. E2 resumes E's session with the same agent file → same hashes ✓. Good.

  Now Task 1 detail check: new test's workflow slicing — `workflow.split(marker, 1)[1]` for powershell.exe marker at line 84: `PARALLAX_PS_HOST: powershell.exe`. The env line is `          PARALLAX_PS_HOST: powershell.exe`. Marker `"PARALLAX_PS_HOST: " + host` matches ✓. Step slice ends at `"\n      - name:"` — next step at line 98 `      - name: PowerShell-facing tests under PowerShell 7` ✓. Each module path occurs once in each step ✓ (:88-89, :104-105).

  But wait — the test file itself, `test_backup_lane.py`, after Task 1 will contain the string "test_review_mirror.py" in the `covered` tuple... irrelevant.

  Another check on Task 1 test: `assert "powershell-hosts:" in workflow` ✓ line 59.

  Task 1 Step 7 mutation: "Delete test_review_mirror.py from the pwsh step only — the per-step clause must fail naming pwsh.exe". The clause message: `rel + " must appear exactly once in the " + host + " step"` — names pwsh.exe ✓. "MOVE test_review_mirror.py's second occurrence so both sit in the 5.1 step" — then pwsh step count = 0 → fails naming pwsh.exe ✓, total count still two ✓.

  Now let me check DECLARED_REGIONS end and item 17 body, and the `extra_skill_dirs` line — actually not needed. Let me verify test_contract_coverage.py:651-664 range and check whether `DECLARED_REGIONS` starts there and where it ends.

• Let me verify the remaining citations: `test_contract_coverage.py` DECLARED_REGIONS range, backlog item 17's body, and the selector citation at `test_codex_context_probe.py:55-61`.

• Notes:

  - DECLARED_REGIONS set ends at :672. The citation :651-664 points into the middle of the set; adding two ids anywhere in the set works. Plan says "add ... to DECLARED_REGIONS" with citation :651-664 — close enough, it's within the set (:651-671 are entries). Minor.

  - Item 17's body at :41 records the 27 count ✓. Item 17 :52 says "Skill is absent from the five-tool allowlist" — plan fact 2 says item 17's wording is stale because Skill is on the explicit DENY list, not merely absent. Item 17 :52 does say "absent from the five-tool allowlist, so 'nothing advertised' cannot be told apart from 'root not read'". backup-lane.md:349-350 also says "most likely because Skill is absent from the agent's tool allowlist". Fact 2's claim "Backlog item 17's own wording is stale on this point, and the fix therefore flips a denied tool rather than adding a missing one" — hmm, item 17's shape-of-a-fix at :66 says "add Skill to the allowlist for the probe run ONLY". The plan's probe agent flips it from denied to allowed. Item 17's wording "absent from the allowlist" is technically true (it IS absent from the allowlist — it's on the deny list) but incomplete. The plan calls it stale; that's a judgment, and the plan's probe agent correctly derives from the actual file. Fine.

  - Task 6 Step 4: "Bump the version in .claude-plugin/plugin.json from 0.19.0 to 0.20.0" — let me verify plugin.json version. Quick check.

  - Task 5's replacement text asserts "MEASURED 2026-08-03" — pre-written verdict text for the NOT REACHABLE branch only. Fine given the gate.

  - One thing to check: Task 5 Step 3 replaces backup-lane.md:341-344, but the new text keeps the sentence that the pin at test_backup_lane.py:848-853 asserts. The OLD pin asserted "lives in the user's own home, is not relocated by KIMI_CODE_HOME, and NOTHING this lane runs removes it. Enumerate that root before round 1 and record what it holds; a non-empty one is unprobed territory, recorded as such..." — the old pin is DELETED and replaced by new pins ✓.

    But careful — the replacement in backup-lane.md: does the first sentence remain inside the replaced region? The new text at :633-635 keeps "`~/.agents/skills/` lives in the user's own home, is not relocated by KIMI_CODE_HOME, and NOTHING this lane runs removes it." as a continuation of the bullet. The new pin (Task 5 Step 1) asserts exactly that ✓.

    Also: is there another pin elsewhere asserting the old "Enumerate that root before round 1... unprobed territory" text? The pin at :848-853 includes it and is being deleted. But there might be OTHER pins referencing the same sentence (e.g., a region lock). backup-lane.md:341-344 currently — is that sentence inside a contract region? Looking at the read, lines 330-344 are a bullet; I don't see contract markers around :341-344 in what I read. But there could be a region starting earlier. Let me grep backup-lane.md for contract markers near that bullet. Actually the plan says new regions home-skill-root-disposition are added; if the old text were already inside a declared region, deleting it would break that region's pin. Let me check contract regions in backup-lane.md around lines 320-360.

• Let me check the contract regions in `backup-lane.md` near the text Task 5 replaces, the plugin version, and the `new-kimi-lane-home.ps1` tool the plan relies on.

• Interesting: the contract markers grep shows no region between :262 and the SKILL DISCOVERY bullet at :330-344. But DECLARED_REGIONS (from the earlier read) lists ids like "panel-floor-reference", "panel-unavailable-principle", etc. — those markers must be later in the file (after :262). The grep shows markers only up to :262... but DECLARED_REGIONS has more ids (panel-*, client-context-probe, etc.). The grep output seems truncated? It showed 18 lines, ending at :262. That would mean the region ids declared in test_contract_coverage.py (panel-floor-reference etc.) have no markers in backup-lane.md — but maybe those regions live in OTHER documents (DOC_PATHS plural). Fine — collect_regions runs over DOC_PATHS. Not a defect in the plan.

  Key point for Task 5: the text at backup-lane.md:341-344 is NOT inside any contract region (no markers between :262 and :330+). So replacing it and adding two new regions works, and no existing pin besides :848-853 covers it. The old pin at :848-853 asserts the sentence and is deleted ✓. 

  plugin.json version 0.19.0 ✓ (Task 6 Step 4 premise correct).

  Now, remaining checks:
  1. `tools/new-kimi-lane-home.ps1` exists? The plan references it in Task 4 standing rules.
  2. Fact 10: "recursive delete does NOT delete through a junction on Windows, and Path.resolve() DOES follow one. Both were established by the 0.19.0 cycle" — no citation; acceptable as stated ("established by the 0.19.0 cycle") — no file:line. The plan's own rules require citations for claims *I* make; the plan's facts section says "Citations are to the artifact that holds each" — fact 10 has none. Minor.
  3. Task 4 Step 5b: E2's invocation prompt "with the skill name parallax-absent-canary-<nonce>". But the frozen prompt for cells C/D/E is verbatim "Invoke your Skill tool with the skill name parallax-home-root-canary. Then reply..." — for E2 the name differs, so the prompt is a modified version. Fine, stated.

  Also E2 validity: "a tool.call naming exactly ... (or, for E2, exactly the absent name)" ✓.

  4. Check the E2 resume validator constraint: resume slices must NOT contain config.update, tools.set_active_tools, llm.tools_snapshot, permission.set_mode (:787-793) — that's the client's behavior on resume; if the client emits them, the validator fails the round → fail-closed. Fine.

  5. Also `rule 14: continuity` — prior state file written BEFORE dispatch ✓ standing rule.

  Now let me verify `tools/new-kimi-lane-home.ps1` exists and quickly glance at Task 4's "same workspace path" claim. Also confirm the plan's claim in fact 3 that lane records systemPromptChars/toolCount — verified via probe-record :170-190 ✓.

  One more check on Task 2's interface: the state file `before` key sorted Ordinal; Remove verifies root byte-for-name identical. Fine.

  Task 2 test: "it contains PARALLAX-CANARY-<nonce> exactly twice" — canary body has nonce in description (:99) and in body (:104) = twice ✓.

  Task 2: "Plant refuses a -Root that resolves to $env:USERPROFILE itself" — default root is USERPROFILE/.agents/skills. Fine.

  Now check new-kimi-lane-home.ps1 exists.Exists ✓.

  Now, one more consideration on Task 4 gate — cell B and the validator. Cell B runs the reviewer agent with --skills-dir passed and the canary in the real home. Fact 4 says systemPromptChars must equal the agent body length or the validator FAILS the round. If the canary is injected into B's system prompt, the round fails validation → readout 2 fires → REACHABLE EVEN AS CONFIGURED ✓. But hold on: in cells C/D/E with the probe agent, if the skill is injected into the system prompt, the validator also fails (systemPromptChars mismatch) — plan Step 5 notes "A readout-2 firing here means the round's validator reports status not clean, and that failure IS the measurement — record it as an expected failure, not a broken probe" — that's said for cell E specifically, but applies to all. OK.

  Now think about Task 4 ordering subtlety: cell B runs before C and D inside the try. B uses reviewer agent (Skill denied). If the client eagerly injects real-home skills into the system prompt for ANY agent, B's readout 2 fires → gate REACHABLE EVEN AS CONFIGURED. If instead the injection only happens when Skill is offered... C/D readout 2 or readout 1 fires. Covered.

  One more potential false-clean: the nonce reuse across cells — the same nonce in every cell. Cell B could put the nonce in ITS wire (in B's home). Cells C and D are separate homes, so no cross-contamination. Cell A runs before any plant ✓. Step 4 verifies removal before E ✓. But wait — is there cross-contamination via the MODEL or client caches? E.g., the client's global cache outside KIMI_CODE_HOME (e.g., ~/.kimi-code is NOT redirected? The plan says the binary lives at ~/.kimi-code/bin/kimi.exe but KIMI_CODE_HOME redirects the data home). If the client caches skill scans globally per machine and cell B's scan of the real home (with canary) is cached, then... cells C/D run with the canary still planted, so cache doesn't matter. E runs after removal but plants its own canary in the debate home. If a global cache retained the real-home canary scan, E could see "parallax-home-root-canary" from the cache even if <debate-home>/skills/ isn't discovered → E's tool.result carries the nonce → positive control validates — but then D (run earlier, canary present) also would have fired if cache were in play... D ran while the canary was actually present, so D-fires would be REACHABLE anyway. The dangerous order: D silent + E fires from stale cache → NOT REACHABLE, when actually the root IS reachable but... wait, if the root is reachable and cached, D would have found the canary (it was planted during D). For D to be silent while E fires from a cache of the real-home scan, the cache would have to be written during B/C (canary present) but unread during D and read during E — incoherent. Also global cache across different KIMI_CODE_HOMEs would contradict per-home isolation but nothing rules it out. However E's canary is planted in E's own debate home — if the client caches by home, no issue. This is speculative; the measured record structure (per-session homes) suggests per-home state. I won't press it as a finding; the residual is theoretical and the gate fails closed on incoherence (D silent + E fires is exactly NOT REACHABLE, hmm — that's the one case... let me think again).

  Scenario: real-home root IS reachable. Cells B/C/D run with canary present. If reachable via Skill invocation, D's result carries the nonce → REACHABLE, not silent. For NOT REACHABLE, D must be a valid not-found — meaning when D asked for the canary by name with the root readable, the tool returned not-found. That's contradictory with reachability via the Skill tool. The only way: the root reaches the reviewer through a non-Skill channel (system prompt or injection) while the Skill tool doesn't resolve it. Then D's tool.result is a valid not-found matching E2. Would the other channel leave a trace? System-prompt → readout 2 fires for B/C/D → not clean. Wire-recorded injection → readout 1 fires → not clean. A channel with NO wire record and NO systemPromptChars change → the model receives the content invisibly. As discussed, that requires the client's wire to not record delivered content, contradicting probe-record.md:188-191's measured claim that all delivery surfaces are recorded. But actually probe-record.md only measured the surfaces that exist; an invisible channel is unfalsifiable by prior measurement. The plan's Task 5 disposition-limit text bounds the claim to "what the probe reached". This is the inherent limit of black-box measurement; I'll note it as an accepted residual rather than a FIX, since any measurement has this and the plan bounds its claim.

  Now let me also double-check the "six of the eighteen" claim and the debate record consistency — not needed for defects.

  One more citation to verify: plan line 59 cites `evals/multi-model-verify/test_codex_context_probe.py:55-61` for the PARALLAX_PS_HOST selector. The actual selector is at :54-55 (`POWERSHELL = (os.environ.get("PARALLAX_PS_HOST")` at :54) and ps_host docstring at :63-67. Lines :55-61 cover `or shutil.which(...)`, pytestmark — the selector's env read is at :54. Slightly off. Minor.

  Also plan line 73 fact 2: "one of 17 names running :11-27" ✓ verified (lines 11-27 = 17 entries) ✓.

  Task 5 Step 1 comment cites "0.20.0" — consistent with Task 6 bump ✓.

  Task 1, Step 5 backlog status replacement: current :11-14 matches the "from" — the plan's new status text moves 10 to Done ✓. Task 6 moves 17 ✓. No conflict between Task 1's edit of :11-14 and Task 6's later edit — sequential, fine.

  Now Task 1 test detail: `workflow.split(marker, 1)[1]` — for powershell.exe the marker appears at :84. But note the string "PARALLAX_PS_HOST: powershell.exe" — the YAML has it inside an env block. Also check: does the ubuntu job earlier in the file contain "PARALLAX_PS_HOST"? The plan's test asserts the marker exists; split(marker,1)[1] takes the FIRST occurrence. If an earlier step (ubuntu job) sets PARALLAX_PS_HOST: powershell.exe, the slice would start there and include more than one step. Let me check the workflow before line 55.

• One more check — whether `PARALLAX_PS_HOST` appears earlier in the workflow (Task 1's test splits on the first occurrence):

• Good — markers appear exactly once each, at :84 and :100, first occurrence = the host step ✓.

  I have enough. Let me also quickly sanity-check the claim in plan fact 4 that read-kimi-round-evidence.ps1:877-879 "already FAILS a round where systemPromptChars doesn't equal agent body LF-normalized length" ✓ verified at :876-879.

  And fact 5 :780 ✓; fact 6 :865-867 ✓; 6b :803-805 ✓.

  Now assemble findings, ranked by false-clean danger:

  1. Citation defect: fact 1 cites probe-record.md:92-96 for "holds 27 skill directories" — those lines do not contain the count; the count is at backlog.md:41 and kimi-live-debate-record.md:39. Effect on measurement: Step 4's restoration check hardcodes 27; the number exists elsewhere in the repo so the value is corroborated, but the cited line does not say what the plan says it says — defect per the brief. Danger to false-clean: low (fails closed if wrong). Rank: it's not a false-clean path; moderate as a record defect.

  2. Task 5's pin-range citation `test_backup_lane.py:848-856` over-ranges: the retired assert is :848-853; :854-856 is the head of the NEXT pin's comment. A literal deletion of :848-856 beheads the following comment (leaves :857-860 dangling) and leaves the retired pin's own comment (:842-847, "The retired 'unprobed territory' pin carried a DISPOSITION...") in place describing a pin that no longer exists. Not a false-clean path; implementer-confusion defect.

  3. Minor citation imprecision: `test_codex_context_probe.py:55-61` for the PARALLAX_PS_HOST selector — the env read is at :54; `test_contract_coverage.py:651-664` is inside DECLARED_REGIONS but the set runs :651-672. Trivial.

  4. Gate analysis: I could not find a false-clean path that the evidence supports. Walked through: E's unconditional nonce-bearing tool.result means any delivery mechanism that D would use must also fire for E's root or the probe goes VOID; C/D validity gates and the frozen not-found comparison fail closed; A/B/C/D readout requirements cover system-prompt and wire-recorded injection; readout 3 can't designate. The one theoretical residual — a client delivery channel that reaches the model while leaving no record in wire.jsonl, no systemPromptChars delta, and no echo in the reply — is unfalsifiable by any black-box probe and is bounded by the disposition-limit text. I'll state it as an accepted residual, not a FIX.

  5. Write-probe leg failure outcome is not named in the gate branches — what does the driver record if the probe agent fails its containment check? It runs before C/D, so a failure presumably aborts; but the plan doesn't say STOP explicitly for that leg. If a zero-judgment driver hit a write-probe failure with no instruction, it might proceed to C with an uncontained agent — a safety defect, not a false-clean. Actually re-read: "The probe agent is a loosened deny list on a live client, so its containment is verified before use, never assumed" — "before use" implies a failed check blocks use, but the plan never says what to DO on failure. Given the global invariant ("a guard that cannot be evaluated REFUSES"), the driver has a standing rule to stop. Weak finding; worth one line.

  6. Fact 10 has no citation at all (junction/delete behavior "established by the 0.19.0 cycle"). The plan's facts header says citations are to the artifact that holds each. Minor.

  Also checked and pass: Task 1 oracle slicing against the real workflow; _norm behavior making the expected failure fire; backup-lane.md:341-344 not inside a contract region; plugin.json 0.19.0; backlog :577 and :11-14; item 17 :16-19; validator citations; fixture wire shape; agent file deny list.

  Verdict: FIX — for the fact-1 miscitation and the Task 5 pin range. Are these serious enough for FIX on a frozen plan? The brief says "A plan that cites a line that does not say what the plan says it says is a defect." Fact 1 is exactly that. The Task 5 :848-856 range would cause a zero-judgment implementer to behead a comment. Both are concrete, evidence-backed fixes. The false-clean question (the ranked-first concern) — I found no supported path. So verdict FIX naming: (1) correct fact 1's citation to include backlog.md:41 / kimi-live-debate-record.md:39 for the count; (2) correct the Task 5 pin range to :842-853 (comment+assert) so the following pin's comment at :854-860 is not beheaded. Minor notes for the rest.

  Wait — should I double-check that deleting :848-856 actually beheads a comment? Lines 854-860:
  854: "# The old "LATENT surface" pin recorded that a back-channel key's"
  855: "# presence says nothing about whether anything is actually being"
  856: "# merged. Its successor is stronger and states the same restraint:"
  857: "# `--skills-dir` is a MITIGATION whose effect is UNMEASURABLE here,"
  ...
  So deleting :848-856 removes the assert AND the first three lines of the LATENT comment, leaving :857-860 as a dangling fragment above the assert at :861. Syntactically valid Python (comments), tests still pass, but the comment is garbled — and the retired pin's own comment at :842-847 ("The retired 'unprobed territory' pin carried a DISPOSITION for the source this lane cannot clear. Its successor names...") would remain, describing a successor in terms that predate the new pins. Cosmetic but real for a zero-judgment implementer following line numbers literally. The correct range is :842-853.

  UNVERIFIED section: commit hashes 6a462f9, f527301 (git objects, not readable as files); kimi-code client behavior claims not yet measured (by design); whether `<debate-home>/skills/` is actually a discovery root of the client (the plan asserts it in the cell table — backup-lane.md:339 says the builder creates it empty, implying it's a root, but nothing I read proves the client discovers skills there; if it doesn't, E fails → VOID, fail-closed). Also tools/new-kimi-lane-home.ps1 contents not read (only existence). Fact 10's 0.19.0 establishment not read.

  Write the report.

• I have read the plan in full and every file I needed to judge its claims. Report below.

  ---

  ## Findings (ranked by false-clean danger)

  **1. The gate: I could not construct a supported false-clean path. PASS on the central question.** The brief asks whether the probe can report NOT REACHABLE when the root does reach the reviewer. Walking the delivery paths against the gate (`docs/superpowers/plans/2026-08-03-home-skills-root-probe.md:515-530`): any delivery through the system prompt fires readout 2, which the validator already fails hard (`tools/read-kimi-round-evidence.ps1:877-879`); any delivery recorded in the wire fires readout 1, and the fixture confirms both `tool.result` output and injected messages land in `wire.jsonl` (`evals/multi-model-verify/fixtures/kimi-round/fresh-wire.jsonl:8,14`); the invocation path is covered because cell E's nonce-bearing `tool.result` is an UNCONDITIONAL requirement (`plan:521,528`), so any mechanism that could deliver D's canary must also deliver E's or the probe goes VOID, never NOT REACHABLE. A found-skill result that differs from E2's calibrated not-found shape makes C/D FAILED, not negative (`plan:517-519`), and the frozen ordinal comparison over the complete `event.result` (`plan:519`) matches the identifier-carrying records in the fixture (`fresh-wire.jsonl:13-14`). The only residual is a client channel that reaches the model while leaving no wire record, no `systemPromptChars` delta, and no reply echo — unfalsifiable by any black-box probe, contradicted by the measured record model (`docs/superpowers/plans/rounds/2026-07-31-kimi-code-swap/probe-record.md:188-191`), and bounded by the disposition-limit text (`plan:647-652`). Accepted residual, not a defect.

  **2. Measured fact 1 cites a line that does not contain the claim.** The plan asserts "`~/.agents/skills/` holds 27 skill directories on this machine" and cites `probe-record.md:92-96` (`plan:72`). Those lines say only that the root is not relocated and quote the `--skills-dir` help text; the count 27 appears nowhere in that file (grep for `27` finds only a port and a SHA fragment). The count IS recorded, at `docs/superpowers/plans/2026-07-27-0150-backlog.md:41` and `docs/superpowers/plans/rounds/2026-07-31-kimi-code-swap/kimi-live-debate-record.md:39`. This matters because Task 4 Step 4 hardcodes "holds 27 entries" as the restoration gate (`plan:565`) — the value is real, but an implementer verifying the citation finds nothing and the frozen plan contains a mis-citation, the exact defect class the debate exists to catch. Fail-closed in effect, but a record defect.

  **3. Task 5's pin range `test_backup_lane.py:848-856` over-ranges by three lines.** The retired assert is `:848-853`; lines `:854-856` are the head of the NEXT pin's comment ("The old 'LATENT surface' pin recorded…"). A literal deletion of `:848-856` beheads that comment, leaving `:857-860` dangling above the assert at `:861`, and leaves the retired pin's own comment at `:842-847` ("The retired 'unprobed territory' pin carried a DISPOSITION… Its successor names…") in place describing a pin that no longer exists. Tests would still pass — this is a zero-judgment-implementer trap, not a false-clean. The correct deletion is `:842-853`.

  **4. Minor citation imprecision, no action needed beyond noting.** The `PARALLAX_PS_HOST` selector is at `test_codex_context_probe.py:54-55`, not `:55-61` as cited (`plan:59,302`); `DECLARED_REGIONS` spans `test_contract_coverage.py:651-672`, so `:651-664` points inside it but not at its bounds (`plan:588`). Fact 10 (`plan:85`) carries no citation at all despite the section's own rule that citations are to the artifact holding each fact.

  **5. Write-probe leg failure has no named outcome.** Task 4 Step 3 requires the probe agent's containment to be "verified before use" (`plan:559`) but no gate branch or step says what the driver records or does if the write-probe fails. The global invariant (`plan:47`) covers it by refusal, and it precedes the invocation cells so it cannot produce a false clean — one line of "STOP and reopen" would close it, but I do not press it.

  ## Verified sound, one line each

  Task 1's per-step oracle works against the real workflow: markers at `.github/workflows/skill-evals.yml:84,100`, each module exactly once per step (`:88-89,:104-105`), and `_norm`'s whitespace-join (`evals/multi-model-verify/test_backup_lane.py:48-50`) makes the expected failure on the retired sentence fire, since the live text at `test_codex_context_probe.py:50-51` normalizes into the asserted string. The deny-list citation `kimi-reviewer-agent.md:21` is exact, 17 names at `:11-27` as claimed. The confounded-probe citation `backup-lane.md:345-353` says what fact 8 says. The replaced text at `backup-lane.md:341-344` sits inside no contract region (no markers between `:262` and end of that bullet), so Task 5's region surgery is clean. Backlog `:577`, `:11-14`, `:16-19`, and `plugin.json` 0.19.0 all match. Validator citations `:780,:803-805,:865-867` verified. `tools/new-kimi-lane-home.ps1` exists.

  ## UNVERIFIED

  - Commit hashes `6a462f9`, `f527301`, `1a014b5`, `c6b7c85` — git objects, not readable as files in this workspace.
  - That `<debate-home>/skills/` is in fact a discovery root of the kimi-code client. `backup-lane.md:339` says the builder creates it empty, which presumes it; if the client does not discover it, cell E fails and the probe goes VOID — fail-closed, so the plan is safe either way, but the premise itself is not proven by anything I read.
  - The contents of `tools/new-kimi-lane-home.ps1` (existence only) and the 0.19.0 establishment behind fact 10.
  - All claims about unmeasured client behavior, which the plan itself declares unmeasured.

  ## Verdict

  **FIX.** Two changes, both to citations/ranges, neither touching the gate: (1) repoint fact 1's 27-directory claim to `docs/superpowers/plans/2026-07-27-0150-backlog.md:41` (evidence: the count exists there and at `kimi-live-debate-record.md:39`, and not at the cited `probe-record.md:92-96`); (2) change Task 5 Step 1's deletion range from `test_backup_lane.py:848-856` to `:842-853` (evidence: the retired assert is `:848-853` with its comment at `:842-847`, and `:854-856` belongs to the next pin's comment). On the question the review was told to focus on — a false NOT REACHABLE — the gate stands.

To resume this session: kimi -r session_acd52b98-bad1-4382-8283-dcf41c7454d4
