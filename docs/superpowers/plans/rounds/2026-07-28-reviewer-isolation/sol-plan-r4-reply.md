1. **FIX.** An outer-block allowlist is the right generalization, but the current implementation is not actually top-level-aware. `Get-PromptText` flattens all chunks into one string, then the regex examines every line in that string (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:364-405`, `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:477-486`). Because `<INSTRUCTIONS>` contains the global and project `AGENTS.md` bodies, a legitimate line such as `<role>` inside either body is indistinguishable from a new outer surface (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:120-130`). For the permitted global `AGENTS.md`, that is a false block.

   The tag grammar also does not match every tagged surface: names containing `-` or `:`, tags with attributes, self-closing tags, and indented tags evade `[A-Za-z][A-Za-z0-9_ ]*` (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:477-480`). Those are tagged structures, not the accepted “untagged prose” limit.

   Specific fix: parse or mask the complete spans of recognized outer containers, then classify only openings outside those spans. Expand and document the supported tag grammar. Add tests proving:

   - A top-level unknown block stops.
   - `<role>` inside the global `INSTRUCTIONS` body does not.
   - A supported unknown tag with a hyphen or attributes stops.

   The untagged-prose limit is defensible; detecting arbitrary prose without a stable outer boundary would be noisy. But it currently exists only in a script comment (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:458-470`), while the design still claims coverage of classes nobody enumerated and still describes only `<*_instructions>` failures (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:71-75`, `docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:278-287`). Put the limit in the design’s Accepted limits and narrow the guarantee to unknown structurally tagged outer surfaces.

2. **PASS.** Plugin-cache residue remains blocking after the feature flags, with no path that reclassifies it as a note (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:990-993`, `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1029-1032`).

3. **PASS.** Every probe invocation includes both feature flags, while the override is additive rather than a replacement for them (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:923-927`). Both dispatch forms likewise carry both flags and the verified override (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1988-2000`).

4. **PASS.** The second pass requires the skills block to be absent and the residue count to be zero (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1051-1075`). The artifact is encoded as strict UTF-8 without a BOM and hashed over those raw bytes (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1090-1103`). The non-ASCII fixture exercises `café-naïve` and verifies its encoded bytes and hash (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:826-854`).

5. **PASS.** The probe verifies `$override` directly, writes the strict UTF-8 representation of that value, and hashes those bytes (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1051-1053`, `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1097-1103`). Each transport round independently reads the raw bytes, hashes them, strictly decodes those same bytes, and passes that in-memory value (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1960-1986`). The hash now binds what it claims; no wrapper is needed.

6. **FIX.** The failure table is not yet complete because the unknown-block check runs only on the first pass (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:973-1000`). On the second pass, the script parses only the skills block (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1056-1075`). Consequently:

   - A new unknown outer block appearing only under the generated `-c` configuration passes silently.
   - `<apps_instructions>` could reappear on the second pass without skills and pass because the second pass does not repeat `Get-FeatureReport`.
   - Conversely, embedded tag-looking lines in permitted global instructions can cause a false block on the first pass.

   Run the outer-shape, unknown-block, feature-block, and required-instructions validations on both prompt renders. Add a fixture whose first pass is ordinary and whose second pass introduces an unknown block, plus one whose second pass reintroduces the apps block.

7. **PASS.** Redirected `CODEX_HOME` remains rejected on credential cost and incomplete `~/.agents/skills` coverage (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:347-356`).

8. **PASS.** Cached mirrors and standing repository decisions remain rejected as stale judgments, including stale consent (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:363-369`).

9. **PASS.** The depth asymmetry is now consistent in both design and implementation: `*AGENTS.md` reaches depth, `.agents/*` is root-anchored, and the measured nested limitation is explicitly accepted (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:322-332`, `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1567-1582`).

10. **PASS.** The ignored-file reasoning remains explicit: `--others` without `--exclude-standard` includes ignored entries (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:333-340`).

11. **FIX.** The main ordering is still sound, but four test/interface defects remain:

   - The claimed six-direction override guard matrix is not present. The three cases are `repo/o.txt`, `repo/sub/o.txt`, and `mirror/o.txt`; all are “inside” cases. None tests equality or a path containing either protected tree (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1483-1499`). Parameterize independently over protected tree `{repo, mirror}` and relation `{same, inside, parent}`.
   - The probe’s direct path says the output must be fresh (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2038-2045`), but `WriteAllBytes` overwrites an existing target without checking (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1097-1100`). Reject an existing `OverrideOut` before probing or writing.
   - The mirror does not compute and reject an existing default override until after creating, copying, remediating, and manifesting the mirror (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1732-1809`, `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1811-1825`). Resolve the effective override path and perform overlap and freshness checks beside the initial mirror guard.
   - Task 2’s declared JSON interface omits `global_agents_md_path`, although the produced report and doctor consume it (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:578-582`, `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1106-1119`, `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2298-2304`).

   The non-ASCII test should also extract the second call’s exact `-c` argument and assert `passed.encode("utf-8") == raw`; it currently creates a call log but verifies only the artifact and its hash (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:837-854`).

12. **PASS.** The scope guard remains expressly a mitigation, while the flags, generated disable list, and second measurement are named as controls (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:297-313`).

13. **PASS.** The mirror implementation still preserves raw baseline status, derives manifest subjects separately, handles both rename/copy columns, and blocks missing destinations (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1589-1646`). Manifest generation returns explicit success/error shapes and blocks missing files (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1648-1680`).

14. **PASS.** The fixture assertions separately bind the 24 user-directory and five built-in entries rather than merely preserving the combined total (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:191-215`). The closing provenance statement matches those assertions (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2398-2404`).

**UNVERIFIED**

The unchanged external measurements remain outside this review:

- Live Codex counts, prompt sizes, flag effects, and zero-residue measurement (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:57-109`).
- Nested `.agents` and ignored-file observations (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:322-339`).
- The observed `R`/`RD` Git status behavior (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1628-1641`).
- Whether an actual debate dispatch used the documented mechanism; the documents specify that mechanism but contain no execution record (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1960-2000`).

**Overall verdict: FIX.** These are record-acceptable fixes, not unresolved disputes: no claim requires ESCALATE. The UTF-8/hash handoff is now sound. The shipping blocker is the allowlist operating on flattened nested content while validating only the first pass. Close that, correct the guard matrix and artifact freshness ordering, and the plan converges at the cap.