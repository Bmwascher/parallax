Overall: only claim 9 passes unchanged. The largest defect is that per-session files are still cumulative across resumed rounds; the plan removes the old offset without replacing its freshness function.

1. Deleting all four attribution mechanisms

The lock, global-log rotation guard, and session-block ordering can go: the existing contract ties them directly to concurrent attribution in `~/.kimi/logs/kimi.log`, while kimi-code places evidence under a session-specific directory (`skills/multi-model-verify/references/backup-lane.md:47-63,81-105`; `docs/superpowers/plans/rounds/2026-07-31-kimi-code-swap/probe-record.md:164-191`).

The byte-offset function cannot simply disappear. Resumed rounds append to the same session’s log and wire transcript, and the plan merely asks for matching records somewhere in that session directory without binding them to the current call (`probe-record.md:214-236`; `2026-07-31-kimi-code-swap.md:660-682`). A resumed round can therefore reuse round-1 `config.update`, tool, request, or log records. The fallback contract also still explicitly depends on the old offset and rotation concepts, but the plan never schedules their removal (`skills/multi-model-verify/references/fallbacks.md:152-159`; `2026-07-31-kimi-code-swap.md:880-923,989-1027`).

Verdict: **FIX — delete the shared-stream lock/rotation/session-block machinery, but add a per-call freshness boundary for cumulative session files and rewrite the stale fallback rationale.**

2. Per-round evidence cannot silently pass

The positive equalities are stronger than the old negative grep, and missing evidence is explicitly failure under the proposed prose (`2026-07-31-kimi-code-swap.md:667-690`). They are not sufficient as written:

- There is no requirement that the selected records were appended by the current resumed call. Earlier matching records remain available in the same session files (`probe-record.md:214-236`; `2026-07-31-kimi-code-swap.md:660-682`).
- The proposed tests only pin Markdown text; they do not implement or fixture-test an evidence parser, despite the design promising captured log/wire fixtures and missing-record tests (`2026-07-31-kimi-code-swap-design.md:258-265`; `2026-07-31-kimi-code-swap.md:750-864`).
- “An allowlist that failed to apply yields a different set” is not universally true. If `tools:` failed but the current denylist applied, that denylist excludes every currently known non-allowlisted tool, leaving the same five effective names (`2026-07-31-kimi-code-swap.md:419-423`; `probe-record.md:151-155`). That outcome is still contained, but it refutes the stated diagnostic inference.

Verdict: **FIX — require newly appended, turn-associated records and add executable fixtures covering stale, missing, duplicate, malformed, and unequal evidence.**

3. Hashes only within a debate, never literal

A timeless literal is unsuitable: `toolsHash` covers full schemas and may legitimately change across client versions (`2026-07-31-kimi-code-swap-design.md:174-181`). But “never” is too broad because the lane accepts every version at or above a floor, while checking only tool names and using round 1 as its own trust anchor (`2026-07-31-kimi-code-swap.md:85-97,667-698`). An unreviewed upgrade can establish a new round-1 hash without any approved schema baseline.

The rule is also not properly locked. It sits outside the `per-round-session-evidence` region, and its test pins only two fragments rather than the whole round-1/later-round requirement (`2026-07-31-kimi-code-swap.md:692-698,813-815`). The repository grammar requires a marked region to sit whole inside one recognized assertion (`CLAUDE.md:55-92`).

Verdict: **FIX — recompute `systemPromptHash` from the committed body; bind `toolsHash` or the full schema snapshot to an explicitly supported client version; and place the complete hash rule inside a pinned contract region.**

4. Brief hash is strictly better

It is strictly better than nonce echoing for completeness and cooperation: the transcript records the received prompt, and the 9,033-character probe established an end-to-end hash match without reviewer assistance (`probe-record.md:198-212`).

It is not strictly better than file transport in every respect. Hash comparison detects and rejects truncation; it does not deliver a brief that exceeded the inline transport’s capability. The plan also omits the probe’s required newline-normalization detail: the recorded match was obtained “after newline normalisation,” while the contract does not define normalization, encoding, or which `turn.prompt` field is hashed (`probe-record.md:205-207`; `2026-07-31-kimi-code-swap.md:700-714`).

Verdict: **FIX — describe it as a stronger fail-closed detector within the measured inline envelope, specify the exact UTF-8/newline canonicalization and JSON field, and retain a defined oversized-brief fallback.**

5. Containment is adequate

The five-tool resolved surface plus denylist, empty subagent catalog, exact evidence, and write probe would be adequate for 0.31.1; print mode’s automatic permission mode makes those controls load-bearing (`probe-record.md:135-162`; `2026-07-31-kimi-code-swap.md:535-552,667-682`).

Two gaps remain:

- `subagents: []` working is explicitly unverified, and Task 4 writes it unconditionally without specifying the negative branch from Task 2 (`probe-record.md:238-243`; `2026-07-31-kimi-code-swap.md:405-460`).
- The denylist only defends against known current tool names. It does not cover a future newly added dangerous tool if the allowlist simultaneously stops applying, contrary to the design’s broader claim (`2026-07-31-kimi-code-swap-design.md:101-107`; `2026-07-31-kimi-code-swap.md:419-423`).

The resumed-call freshness defect from claims 1–2 also allows old containment evidence to satisfy a later round.

Verdict: **FIX — make a failed empty-subagent probe stop the lane with an explicit branch, narrow the denylist claim to known tools, and verify the effective surface from records belonging to the current call.**

6. A per-round isolated home is required for two independent reasons

The hook reason stands: the real home has seven command-executing hooks, including two on the approval path (`probe-record.md:99-116`). A caller-controlled isolated home is also the practical way to establish config-only effort and thinking values (`probe-record.md:118-132`; `2026-07-31-kimi-code-swap.md:288-363`).

What is required is an isolated, plugin-controlled home—not necessarily a new home per round. The contract actually creates one before round 1 and reuses it for every call in the debate (`2026-07-31-kimi-code-swap.md:616-629`). In addition, the evidence contract verifies `thinkingEffort` but contains no runtime equality for `[thinking] enabled = true` (`2026-07-31-kimi-code-swap.md:667-681`).

Verdict: **FIX — call this a per-debate isolated home, and add a differentiating probe/evidence rule for thinking-enabled before claiming it is runtime-verifiable.**

7. Copying the OAuth credential is acceptable

Portability was measured, but secret safety was not (`probe-record.md:81-90`). The builder:

- Accepts an arbitrary destination.
- Force-creates or reuses it.
- Force-copies the OAuth credential.
- Applies no owner-only ACL.
- Does not reject a repository/worktree destination.
- Defines no credential cleanup or retention period (`2026-07-31-kimi-code-swap.md:309-330,360-383`).

Reusing a nonempty destination also leaves stale contents in `skills/` and `sessions/`, undermining both containment and evidence discovery (`2026-07-31-kimi-code-swap.md:326-330`).

Verdict: **FIX — require a fresh scratch path outside every repo, refuse nonempty destinations, apply and verify user-only ACLs before copying, never print credential contents, and securely remove the credential after the debate while retaining only sanitized evidence.**

8. Nothing needs re-pinning on resume

This is confirmed only for 0.31.1: correct-directory resume inherited the hashes, and wrong-directory resume was refused (`probe-record.md:220-236`). The plan nevertheless accepts any version above a floor and turns that observation into an indefinite rule (`2026-07-31-kimi-code-swap.md:85-97,636-646`).

That is unsafe because evidence is checked after the resumed prompt. If a future release resumes with a broader tool surface, print mode may auto-execute those tools before the reply is discarded (`2026-07-31-kimi-code-swap-design.md:114-117,183-185`). The artifacts establish only that `--agent-file` is incompatible with resume—not that `-m`, `--skills-dir`, or other supported controls cannot be re-pinned (`probe-record.md:118-130`).

Verdict: **FIX — probe every resume-compatible defensive flag and re-pin those accepted; refuse unvalidated client versions; add a sacrificial resume write-probe; and require current-call evidence rather than inherited old records.**

9. Drift watch belongs first

Confirmed. Bare `kimi` now resolves to kimi-code after the old executable was renamed, while the current drift script still probes the old `--quiet`, `--thinking`, `-w`, and Python-module surface (`probe-record.md:49-65,118-133`; `tools/check-drift.ps1:133-136,197-215`). Restoring a meaningful watchdog before modifying the lane is the correct order (`2026-07-31-kimi-code-swap.md:29-40`).

Verdict: **PASS**

10. Both conditional tasks are correctly gated

The skills-directory task has a positive and negative interpretation, although its coverage of discovery roots remains narrow (`2026-07-31-kimi-code-swap.md:156-181,738-747`).

The encoding branch is broken structurally:

- Task 2 defines only skills-directory, subagent, and effort probes (`2026-07-31-kimi-code-swap.md:145-206`).
- The design says the cp1252 probe gates deletion (`2026-07-31-kimi-code-swap-design.md:211-214,283-286`).
- Task 8 nevertheless refers to “Task 2’s encoding probe,” which does not exist (`2026-07-31-kimi-code-swap.md:1052-1055`).
- Task 5 already replaces the entire Transport section, thereby deleting the old guard before Task 8 reaches that conditional step (`2026-07-31-kimi-code-swap.md:603-653`).

Verdict: **FIX — add the cp1252 probe to Task 2 and resolve its branch before Task 5 rewrites Transport; explicitly state the positive and negative Task 7 branches as well.**

11. Executable by an engineer with no repository context

Refuted. In addition to the fixes above:

- Task 2 depends on “the isolated home from task 3” even though Task 3 comes later, or on an ephemeral probe home that the record says will not survive (`2026-07-31-kimi-code-swap.md:171-175,217-225`; `probe-record.md:255-260`).
- The proposed builder hardcodes the canonical model literal despite the plan’s single-source rule; the existing sweep includes `tools/*.ps1`, so the resulting script fails `test_backup_literal_single_source` (`2026-07-31-kimi-code-swap.md:14,310-313`; `evals/multi-model-verify/test_backup_lane.py:588-618`).
- Transport says to use the absolute executable, but the exact command and pin use bare `kimi` (`2026-07-31-kimi-code-swap.md:610-615,631-635,755-765`).
- Task 1 demands that `--help` list `-r`, while the probe calls `-r` a hidden alias and identifies `-S/--session` as the public option (`2026-07-31-kimi-code-swap.md:87-97`; `probe-record.md:126-130`).
- The required drift state-machine suite still contains old kimi-cli help stubs and Python-import scenarios, but Task 1 does not schedule edits to that file (`evals/tools/drift_statemachine_tests.ps1:43-45,249-270,679-706`; `2026-07-31-kimi-code-swap.md:33-36,129-134`).
- “Canonical provider” and “canonical effort” are required equalities but are not declared as single-source values. The declaration surface currently names only model id and thinking flag (`2026-07-31-kimi-code-swap.md:667-681`; `skills/multi-model-verify/references/model-prompting-notes.md:298-315`).
- The promised evidence fixtures/parser never appear in Task 5’s file list or implementation (`2026-07-31-kimi-code-swap-design.md:258-265`; `2026-07-31-kimi-code-swap.md:567-575,750-864`).
- Task 6 uses `grep` despite declaring PowerShell 5.1/7 as the stack, and `git add -u` violates the plan’s explicit-path staging rule (`2026-07-31-kimi-code-swap.md:9,16,893-923`).
- Task 8 names `fallbacks.md` but supplies no rewrite for its stale offset/rotation and four-flag UTF-8 recovery rules (`skills/multi-model-verify/references/fallbacks.md:152-179`; `2026-07-31-kimi-code-swap.md:989-1027`).
- The builder reuses arbitrary nonempty homes, so an engineer following it exactly can inherit stale skills and sessions (`2026-07-31-kimi-code-swap.md:309-330`).

The proposed marked-region assertions themselves do conform to the repository’s recognized positive-membership grammar; that portion is executable (`CLAUDE.md:55-75`; `2026-07-31-kimi-code-swap.md:775-842`).

Verdict: **FIX — repair the dependency order and conditional probes, eliminate the single-source and absolute-path contradictions, define an actual evidence validator and canonical values, update the state-machine/fallback surfaces, and make scratch-home creation and cleanup explicit.**

UNVERIFIED:

- Whether `subagents: []` actually produces an empty runtime catalog (`probe-record.md:238-243`).
- Whether `--skills-dir` suppresses every user and project discovery root, rather than only the one canary path proposed (`probe-record.md:92-97,238-247`).
- Whether kimi-code has a cp1252 output hazard; no Task 2 probe currently measures it (`2026-07-31-kimi-code-swap-design.md:283-286`).
- Resume inheritance on any release after 0.31.1; the evidence is explicitly version-specific (`probe-record.md:220-236`).