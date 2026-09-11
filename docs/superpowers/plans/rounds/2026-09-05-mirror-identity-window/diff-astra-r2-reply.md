I accept your rebuttal to finding 1’s consequence. **I did not establish successful deletion and withdraw that implication.** Native `Remove-Item -WhatIf` reproduced `PSArgumentException` on both hosts, with both parameter forms, corroborating your recorded measurement. I cannot supply a real deletion reproduction: this session is read-only, so I did not perform destructive testing. The unchecked continuation remains visible immediately after the removal call. ([measurement](C:/Temp/pxd1/tools/new-review-mirror.ps1:1276), [continuation](C:/Temp/pxd1/tools/new-review-mirror.ps1:1817))

The five fixes are present:

- The spelling guard checks both source and mirror before overlap comparisons; its new tests require the intended refusal and source survival. ([guard](C:/Temp/pxd1/tools/new-review-mirror.ps1:1286), [tests](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:1877))
- The newline, control, and category tests now require positive output and exclude the fallback. ([newline](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:2111), [controls](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:2135), [category](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:2170))
- The timing conclusions now preserve uncertainty. ([backlog](C:/Temp/pxd1/BACKLOG.md:4004), [gate record](C:/Temp/pxd1/docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window/gate-results.md:62))
- README replaces the impossibility claim with discovery history. ([README](C:/Temp/pxd1/docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window/README.md:393))
- The parser comment now describes real empty records correctly. ([comment](C:/Temp/pxd1/tools/new-review-mirror.ps1:794))

Three residual findings:

1. **CONFIRMED — the new spelling guard still admits aliases that defeat overlap protection.**

   It rejects trailing punctuation but otherwise compares provider-returned spellings. Neither step establishes filesystem identity. ([resolution](C:/Temp/pxd1/tools/new-review-mirror.ps1:1228), [guard and comparisons](C:/Temp/pxd1/tools/new-review-mirror.ps1:1286))

   Read-only construction-prefix probes demonstrated:

   | Source argument | Mirror argument | Result |
   |---|---|---|
   | `C:\Temp\pxd1\skills\multi-model-verify` | `C:\Temp\pxd1\skills\MULTI-~1` | Recursive-delete call reached on both hosts |
   | `C:\Temp\pxd1::$INDEX_ALLOCATION` | `C:\Temp\pxd1` | Recursive-delete call reached on PowerShell 7 |
   | `C:\Temp\pxd1` | `\\?\C:\Temp\pxd1` | Recursive-delete call reached on PowerShell 5.1 |

   These are **reachability results**, with deletion intercepted. Separately, native `Remove-Item -WhatIf` accepted the 8.3 path on both hosts and identified the long directory as its target. The stream-form source case reaches deletion with the ordinary, undotted source pathname as the destination. ([deletion call](C:/Temp/pxd1/tools/new-review-mirror.ps1:1817))

   **Change:** normalize existing components to filesystem identity, including short-name aliases, before containment comparisons; reject unsupported stream/device forms explicitly. Test aliases on both operands.

2. **CONFIRMED — `OverrideOut` remains outside the new spelling guard.**

   The guard enumerates only source and mirror. Override protection still compares spelling and checks for reparse points. ([guard operands](C:/Temp/pxd1/tools/new-review-mirror.ps1:1286), [override comparison](C:/Temp/pxd1/tools/new-review-mirror.ps1:1333), [link check](C:/Temp/pxd1/tools/new-review-mirror.ps1:1675))

   On both hosts, all construction validation passed with:

   ```text
   RepoRoot:   C:\Temp\pxd1
   MirrorPath: C:\Temp\round2-destination-probe
   OverrideOut:C:\Temp\pxd1.\round2-override-probe.txt
   ```

   That admitted override names a location inside the source through a dotted ancestor. The build subsequently passes this value to the probe, whose writer calls `WriteAllBytes`. I did not execute that write. ([handoff](C:/Temp/pxd1/tools/new-review-mirror.ps1:2240), [writer](C:/Temp/pxd1/tools/codex-context-probe.ps1:1059))

   **Change:** apply the same spelling/identity validation to the effective override destination before its overlap check, with a source-survival regression.

3. **CONFIRMED — another negative-only oracle accepts an execution error as the expected block.**

   `test_an_unmeasurable_expected_digest_is_refused` supplies an empty mirror-state digest and asserts only `returncode != 0`. Exit 2 with empty stdout therefore satisfies every assertion. ([test](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:2912))

   The specified behavior is a named `BLOCKED` diagnostic and exit 1; the script distinguishes that from execution/environment errors. ([malformed-digest branch](C:/Temp/pxd1/tools/new-review-mirror.ps1:1118), [exit contract](C:/Temp/pxd1/tools/new-review-mirror.ps1:25))

   **Change:** require exit 1 and the missing/malformed mirror-state diagnostic.

The guard’s component split itself passed both-host probes for ordinary UNC spelling, drive-relative spelling, trailing separators, and `.`/`..` components. Provider resolution collapsed an ordinary `skills\..` path before comparison. I found no defect in those tested shapes; live UNC access was unavailable, so this does not establish end-to-end UNC support. ([resolution](C:/Temp/pxd1/tools/new-review-mirror.ps1:1228), [split](C:/Temp/pxd1/tools/new-review-mirror.ps1:1287))

The class sweep covered path aliases, omitted guard operands, negative-only assertions and their helpers, amended measurement conclusions, and adjacent comments. Finding 3 is the additional oracle instance. I found no additional confirmed measurement overclaim or self-count defect in the reread record passages. Full pytest was not rerun.

**FIX — the five local corrections hold, but destination protection still admits demonstrated aliases and an unguarded override spelling, and one remaining oracle confuses errors with blocks.**