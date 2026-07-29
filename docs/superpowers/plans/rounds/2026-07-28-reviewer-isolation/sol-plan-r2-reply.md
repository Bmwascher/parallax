The revised plan is still **FIX**. Several Round 1 changes hold, but the decisive override handoff remains incomplete in the normal execution paths.

1. **FIX** — Unplaceable paths now block, but the broader fail-closed parser fix is incomplete. `Get-PromptText` still silently ignores any content chunk lacking `text`; if one valid text chunk remains, the prompt passes with the unknown chunk discarded. That contradicts both the function comment and the design’s requirement that unrecognized shapes block. `Get-FeatureReport` likewise recognizes only its fixed marker list. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:345-380`; `docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:132-134`.

   Add an adversarial fixture containing one valid text chunk plus one unknown chunk and require a format failure. Unknown instruction-block families must also block or be explicitly recorded.

2. **PASS** — The plugin cache is now consistently blocking: surviving feature markers block, and surviving cache-scoped entries block independently. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:837-872`.

3. **PASS** — The flags remain consistently attached to probe, dispatch, and resume. The reasoning distinguishing them from `--ignore-user-config` is unchanged. `docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:79-97`; `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:770-774`; `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1617-1625`.

4. **FIX** — The empty-set control is still not wired into normal dispatch.

   - The SKILL preflight command invokes the probe without `-OverrideOut`, so it creates no verified override file. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1667-1675`.
   - The mirror script also invokes the probe without `-OverrideOut`. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1499-1509`.
   - Its interface provides no override-output parameter or record field. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:964-966`.
   - The later transport commands nevertheless require `<verified-override-file>`. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1612-1625`.

   Make `-OverrideOut <fresh-scratch-file>` mandatory on both review-preflight paths. The mirror must accept or generate the path and print it in its record.

5. **FIX** — The artifact is not byte-identical to the verified value as written. `Set-Content -Value` writes a line ending, while the second probe received `$override` without that line ending. The test hides this by calling `.strip()` and then checks only substring containment in a flattened argument log. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:711-736`; `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:875-910`.

   Write exact bytes without a terminator and compare raw bytes against a structured capture of the second call’s `-c` argument.

6. **FIX** — The revised code still has false-clean and false-failure directions.

   - Unknown prompt chunks can be discarded as described under claim 1. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:364-379`.
   - `Get-BackChannelEntry` returns an empty pipeline when enumeration succeeds with zero entries; the caller then treats `$null` as command failure. A normal clean mirror therefore cannot be distinguished from a failed enumeration. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1288-1293`; `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1439-1443`.
   - `Get-BaselineRaw` has the same empty-array ambiguity, so a legitimately empty baseline is treated as capture failure. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1301-1315`; `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1480-1486`.

   Return structured results such as `@{Ok=$true; Entries=@(...)}` and `@{Ok=$true; Lines=@(...)}` so successful empty output is representable. Add clean-repo tests for both cases.

7. **PASS** — The rejection of a redirected `CODEX_HOME` remains coherent and unchanged. `docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:341-348`.

8. **PASS** — The rejection of cached mirrors and standing consent decisions remains sound and unchanged. `docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:355-361`.

9. **FIX** — The operative SKILL correction and accepted-limit test now hold, but the proposed mirror script reintroduces the same false “any depth” statement in its own comment immediately above the root-anchored `.agents/*` command. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1288-1293`. This contradicts the corrected contract region and test boundary. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1715-1734`; `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1110-1128`.

   Correct the script comment; do not widen the pathspec.

10. **PASS** — The ignored-file reasoning still has an appropriate scratch-repo regression test, and no revised change undermines it. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1093-1107`.

11. **FIX** — The high-level ordering remains sensible, but the revised task text contains stale and contradictory instructions.

   - After replacing the absolute-workdir design, the plan still instructs the implementer to define `RECORDED_REPO_DIR`, read `repo-agents.workdir`, and write that machine-specific sidecar. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:750-758`.
   - Task 4 adds four tests but still says to expect three failures. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1558-1603`; `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1605-1608`.
   - Task 5’s interface still says it consumes two region IDs and produces three, although the revised inventory contains five. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1770-1773`; `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1842-1853`.
   - Doctor still says “three buckets” after adding `unknown_scoped`, making four skill buckets. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:522-525`; `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1923-1926`.

   Remove the obsolete sidecar section and update the task counts/interfaces.

12. **FIX** — The control list now correctly names three controls, but the generated override is not actually produced by either documented preflight path. Therefore the prose is accurate only aspirationally. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1779-1787`; `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1499-1509`; `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1667-1675`.

13. **FIX** — The raw-baseline, dual-column rename handling, missing-destination block, and lexical overlap guard are correctly added. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1301-1388`; `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1398-1420`. But the empty-result ambiguity makes an ordinary mirror with no back-channels fail before reaching that implementation, and an empty legitimate baseline also blocks. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1288-1293`; `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1480-1486`.

   Also add a clean repository fixture containing neither back-channels nor baseline entries. Existing fixtures always contain ignored and untracked files. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1000-1014`.

14. **FIX** — The aggregate buckets are now asserted, but the promised 24 user-skill versus 5 built-in split still is not. The fixture specification fixes those subcounts, while the test asserts only `home == 29`; a 23/6 normalization would pass. The closing prose nevertheless says every stated count is asserted. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:106-111`; `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:190-202`; `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2020-2026`.

   Assert the two home path-prefix counts separately, or stop fixing them in the fixture contract.

On artifact versus wrapper: an artifact is not inherently too weak, and a wrapper is not required. The current artifact handoff is weaker because it is optional, absent from both real preflight paths, written with different bytes than were verified, mutable without a recorded hash, and tested through normalization plus substring matching. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:711-736`; `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:905-910`.

A sound artifact version should use a fresh scratch path, write exact bytes, return the file’s SHA-256, and have the dispatch preamble read once and verify that hash before passing the same in-memory value to `codex exec`. That binds the existing transport without making a wrapper a second authority.

UNVERIFIED remains unchanged:

- All live Codex counts, prompt sizes, flag behavior, block behavior, and the claim that this debate round exercised the override. The documents record these observations but this review cannot reproduce them. `docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:57-109`.
- Nested `.agents` ingestion and ignored-path measurements. `docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:314-332`.
- The `git mv`/`RD` observation. The resulting fail-closed rule is reasonable, but the measurement remains external to this review. `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:25`; `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1336-1349`.

**Overall verdict: FIX.** The revised plan correctly identifies the verified override as load-bearing, but still does not produce that artifact on either documented review path, and its byte-identity test masks a real representation difference.