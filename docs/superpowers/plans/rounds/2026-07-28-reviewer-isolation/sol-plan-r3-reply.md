1. **FIX.** The parser now correctly blocks any non-text content chunk instead of silently discarding it, and the mixed text/image fixture covers that direction (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:364-405`). But the “whole instruction surface” claim remains stronger than the classifier: it recognizes only the named skills, plugin, and apps markers (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:408-455`). A new textual instruction family such as `<memories_instructions>` would be present in the measured prompt yet ignored. Add an unknown-instruction-block bucket and block on unrecognized top-level `*_instructions` blocks. This is necessary to support the design’s claim that unknown instruction classes are caught (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:71-75`).

2. **PASS.** The design consistently treats plugin-cache skills as blocking contamination and requires their removal before dispatch (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:142-178`).

3. **PASS.** The two feature flags remain the explicit first subtraction layer, while the generated override preserves user configuration rather than bypassing it wholesale (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:183-200`).

4. **FIX.** The override artifact is now produced on both paths: direct preflight supplies a fresh output path (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1833-1837`), and the mirror path supplies or defaults one and records it (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1631-1647`). However, the verified value is converted using ASCII before being written (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:975-988`). Any non-ASCII character in a real skill path becomes `?`, so the dispatched configuration is not necessarily the configuration the second probe verified at `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:944-969`.

   Fix this by writing strict UTF-8 without a BOM. At dispatch, read the raw bytes once, hash those exact bytes, strictly decode those same bytes as UTF-8, and pass the resulting string. Add a non-ASCII path fixture; the current byte test explicitly uses ASCII and therefore cannot expose the defect (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:740-773`).

5. **FIX.** Outcome-based verification still avoids needing to model merge semantics, but only if the exact verified value is dispatched. ASCII conversion currently breaks that identity. There is also a round-lifetime gap: the hash/read preamble appears once, while dispatch and resume later reuse `$override` (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1767-1792`). The contract test only requires two `-c $override` occurrences and one hash marker; it does not require each round to perform its own verified read (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1721-1741`).

   Put the byte-read, hash comparison, strict decode, and `codex exec` call in one PowerShell block for every dispatch and resume. Pin two complete verification preambles, not merely two uses of `$override`. A wrapper is not required; a correctly bound artifact is sufficient.

6. **FIX.** The missing-block and malformed-block false-clean paths are now distinguished, and the second pass requires actual block absence (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:924-969`). The structured failure results also close the clean-repository ambiguity (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1403-1444`). Two failure directions remain:

   - An unknown textual instruction block is ignored by the known-marker classifier (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:408-455`).
   - A non-ASCII verified override can be lossy-converted to ASCII and then successfully hash-checked and dispatched in its corrupted form (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:975-988`, `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1767-1775`).

7. **PASS.** The design continues to reject `CODEX_HOME` isolation for the documented credential and user-home coverage reasons (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:206-220`).

8. **PASS.** Both a cached remediated mirror and a standing per-repository decision remain rejected as stale judgments rather than current measurements (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:222-242`).

9. **PASS.** The asymmetry is now stated accurately: `*AGENTS.md` reaches any depth, while `.agents/*` is root-anchored (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1403-1408`). The matching contract region records the limit without widening it beyond the observed client behavior (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1873-1890`).

10. **PASS.** The ignored-file contract remains explicit and separate from the accepted depth asymmetry (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:320-338`).

11. **FIX.** The order remains sensible, but the mandatory `OverrideOut` fix is not integrated through several consumers:

   - The shared `run_probe` helper adds `-SuppressSkills` without adding `-OverrideOut` (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:594-611`), while the probe explicitly blocks that combination (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:971-974`). Consequently, suppression tests using the helper will fail before reaching their intended assertions.
   - The live Task 2 command also uses `-SuppressSkills -Json` without `-OverrideOut`, yet expects success (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1020-1025`).
   - Doctor Check 9 makes the same invalid call (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2082-2097`).
   - The design still says doctor reports “all three buckets,” although the revised contract has four (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:397-410`).
   - Doctor promises the global `AGENTS.md` path, but the probe output exposes only a Boolean `global_agents_md` field (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:547-551`, `docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2090-2093`).

   Update every suppressing caller to allocate a fresh artifact path. Add one non-`SkipProbe` mirror integration test that proves the default artifact is created, hashed, and recorded. Correct doctor to four buckets and either expose the global file’s path or stop promising it.

   The custom mirror `-OverrideOut` also needs a containment guard: it is accepted as an arbitrary path (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1394-1400`) and checked only for prior existence before the probe writes it (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1636-1647`). Reject locations equal to, inside, or containing either the real repository or mirror. Otherwise a caller can make the supposedly non-mutating mirror workflow write into the reviewed repository or alter the mirror after its baseline was captured.

12. **FIX.** The design now identifies all three intended controls: feature flags, the verified generated override, and the second measurement (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:261-278`). The control chain is nevertheless unsound until the ASCII conversion and per-round verification lifetime are fixed. The scope brief remains properly characterized as mitigation rather than isolation (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:249-259`).

13. **PASS.** The baseline now preserves raw status lines and codes, while manifest subjects are derived separately (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1425-1482`). Manifest construction returns an explicit error instead of silently skipping a missing path (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1484-1516`). Rename/copy handling covers both status columns and blocks a deleted rename destination (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1454-1477`).

   I found no additional empty-collection ambiguity: `Get-BackChannelEntry` and `Get-BaselineRaw` return `{Ok, …}`, while `Get-ManifestSubject` and `Get-ContentManifest` return `{Error}` or `{Paths}` (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:1403-1516`).

14. **PASS.** The fixture contract now asserts total, plugin-cache, home, repository, and unknown buckets, including the 24 user-directory versus 5 built-in split (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:200-215`). The closing prose accurately says that split is asserted (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:2187-2193`).

**UNVERIFIED**

The following remain outside repository-only verification and do not affect the verdicts:

- All recorded live Codex prompt counts, reductions, and prompt sizes (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:57-109`).
- The measured treatment of nested `.agents` entries and ignored files (`docs/superpowers/specs/2026-07-28-reviewer-isolation-design.md:320-338`).
- The observed `git mv`/`RD` output (`docs/superpowers/plans/2026-07-28-reviewer-isolation.md:25-25`).
- The statement that this debate round was dispatched using the generated override.

**Overall verdict: FIX.** The round-two fixes materially improve the plan, and the structured-return repair is complete. The decisive remaining defect is that ASCII serialization can make the hash faithfully authenticate a value different from the one the second probe verified. Mandatory artifact production is also missing from the shared test helper, live gate, and doctor. The artifact approach remains defensible without a wrapper once raw-byte hashing, strict UTF-8 decoding, and per-round verification are bound into each transport invocation.