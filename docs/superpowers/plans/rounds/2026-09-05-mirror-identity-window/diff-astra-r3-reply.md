The specified edits are present: device/stream checks, short-name checks, override inclusion, the dotted-override regression, and the strengthened digest oracle. Their implementation still leaves substantive gaps. ([guard](C:/Temp/pxd1/tools/new-review-mirror.ps1:1286), [regressions](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:1884), [oracle](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:2986))

1. **CONFIRMED — the stream refusal misses a working directory alias.**

   Checking `Contains("::")` catches an unnamed stream spelling but misses `C:\Temp\pxd1:$I30:$INDEX_ALLOCATION`, whose colons are separated. ([condition](C:/Temp/pxd1/tools/new-review-mirror.ps1:1307))

   On PowerShell 7, that path reports `Directory`. Using it as `RepoRoot` with ordinary `C:\Temp\pxd1` as `MirrorPath` passed the complete validation prefix and reached the intercepted recursive-delete call targeting `C:\Temp\pxd1`. This establishes reachability, not completed deletion. ([comparison](C:/Temp/pxd1/tools/new-review-mirror.ps1:1345), [delete](C:/Temp/pxd1/tools/new-review-mirror.ps1:1857))

   **Change:** reject stream delimiters beyond the permitted drive-prefix colon, rather than only consecutive colons. Add this named-index-stream case on both hosts.

2. **CONFIRMED — the subject list still omits protected operands.**

   `ExtraInputPaths` and discovered `followedTargets` remain outside the shared spelling guard. Extra inputs receive separate equality, trailing-punctuation, and reparse checks; followed targets receive reparse and string-overlap checks. ([subject list](C:/Temp/pxd1/tools/new-review-mirror.ps1:1286), [extra inputs](C:/Temp/pxd1/tools/new-review-mirror.ps1:1759), [targets](C:/Temp/pxd1/tools/new-review-mirror.ps1:1730))

   Two read-only probes demonstrated the gaps on both hosts:

   - This mirror’s actual sidecar has short alias `C:\Temp\PXD1~1.SOU`. Supplying that as an extra input passed validation and reached deletion of `C:\Temp\pxd1.source-manifest`. The later copy is unchecked. ([deletion](C:/Temp/pxd1/tools/new-review-mirror.ps1:1848), [copy](C:/Temp/pxd1/tools/new-review-mirror.ps1:2110))
   - Executing the protected-target checks with actual alias `C:\Temp\pxd1\skills\MULTI-~1` accepted the corresponding long directory as the mirror destination. This was a direct guard probe; I did not create a junction to exercise discovery end-to-end. ([target comparison](C:/Temp/pxd1/tools/new-review-mirror.ps1:1740))

   **Change:** extract one validation helper. Apply it to extra inputs before collision checks and to discovered targets before cycle/overlap comparisons.

   The default override and sidecar are different: their parent spelling derives from the guarded mirror path, so their absence from the initial list is not another demonstrated omission. ([default override](C:/Temp/pxd1/tools/new-review-mirror.ps1:1369), [sidecar derivation](C:/Temp/pxd1/tools/new-review-mirror.ps1:698))

3. **CONFIRMED — unchecked removal is worth filing independently.**

   Refusing aliases does not handle ordinary removal failures. A simulated non-terminating error from the existing removal statement still reached `New-Item`. The subsequent copy uses `/E`, and later fingerprinting measures the resulting mirror rather than proving its directory was freshly emptied. ([removal boundary](C:/Temp/pxd1/tools/new-review-mirror.ps1:1857), [copy](C:/Temp/pxd1/tools/new-review-mirror.ps1:1890), [fingerprint](C:/Temp/pxd1/tools/new-review-mirror.ps1:2238))

   **Change:** make removal failure terminate construction with a named error before creation or copying. File this as a separate pre-existing defect if fixing it separately; the spelling changes are not its remedy. I did not reproduce a complete contaminated build under filesystem denial.

4. **CONFIRMED — the neighboring live-measurement oracle still accepts the wrong exit class.**

   `test_a_mirror_whose_current_state_cannot_be_measured_is_refused` accepts any nonzero exit and the generic substring `could not be`. Changing the intended refusal branch from exit 1 to exit 2 would leave those assertions green. ([assertions](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:3009), [intended branch](C:/Temp/pxd1/tools/new-review-mirror.ps1:1200))

   **Change:** require exit 1 and the specific mirror-current-state measurement diagnostic, as the preceding test now does.

On the regex’s opposite direction: **yes, it rejects legitimate full-name spellings**, including `release~2026` and `release~2026.txt`; both-host guard probes confirmed this. It has no eight-character stem constraint. Its message honestly says “looks like,” so this is a conservative compatibility restriction rather than evidence of an alias. Narrow the candidate shape or explicitly document that literal matching names are unsupported; “pass the full name” cannot help when that already is the full name. ([regex and message](C:/Temp/pxd1/tools/new-review-mirror.ps1:1329))

The final sweep covered guard operands, alias spellings, removal continuation, and refusal assertions with their intended branches. Findings 1, 2, and 4 are additional class instances. I found no further confirmed measurement-overclaim in the record passages revisited. I did not rerun pytest, perform real deletion, create junction fixtures, or validate every possible short-name assignment.

**FIX — the named-stream alias and omitted protected operands still bypass destination protection; this is not a dry round.**