1. The path conversions, declaration-read handler, TEMP guard, and named-only checks are applied. I confirmed that invalid TEMP, missing `-RepoRoot`, unknown parameters, and bare tokens produce exit 2 with `ERROR:` on both hosts (`tools/artifact-roots.ps1:88`, `:99`, `:111`, `:174`, `:182`, `:226`, `:246`).

   **A third binding-fault class is reachable: argument conversion.** Fresh probes against this head produced:

   | Arguments after `-RepoRoot .` | PowerShell 5.1 exit | PowerShell 7 exit |
   |---|---:|---:|
   | `-Json:invalid` | 1 | 1 |
   | `-ErrorAction invalid` | 1 | 1 |
   | `-Json:$true` | 1 | 0 |
   | `-Json:$false` | 1 | 0 |

   The conversion failures lack `ERROR:`. The typed switch and advanced parameter binding cause these outcomes (`tools/artifact-roots.ps1:30`, `:36`). The explicit Boolean forms therefore expose a remaining host-divergent exit within the certification unit. The regressions cover none of these inputs (`evals/multi-model-verify/test_artifact_roots.py:282`).

   **FIX:** handle the public arguments before host-specific typed conversion, including explicit JSON Boolean forms. Make true select JSON and false select text consistently; reject invalid values and unsupported options with exit 2 and `ERROR:`. Add dual-host regressions for these cases.

2. The spec and header now describe missing values and duplicate parameters consistently, but their exhaustive “TWO” assertion remains false because conversion faults also reach the binder (`docs/superpowers/specs/2026-09-12-artifact-roots-design.md:234`, `tools/artifact-roots.ps1:21`). The test comment still says “one residual” (`evals/multi-model-verify/test_artifact_roots.py:291`).

   **FIX:** synchronize the spec, header, and test commentary with the completed argument handling. The two documented exceptions accurately describe measured limitations; they do not account for the additional conversion failures or establish host parity.

3. The seventh shape, its controls, and the stated limits are present. My independent sweep found zero offenders (`evals/multi-model-verify/test_artifact_roots.py:473`, `:492`, `:560`). The three former literal spellings now cite the declaration (`skills/multi-model-verify/references/application-checkpoint.md:75`, `tools/verify-attestation.ps1:2`, `tools/write-attestation.ps1:31`).

   The remaining runtime-assembled roots are the documented emitter/verifier computations (`tools/write-attestation.ps1:73`, `:100`; `tools/verify-attestation.ps1:126`, `:178`). I found no additional hand-spelled root outside the stated limits. **PASS.**

4. Both writer cases are present. The fresh case asserts both directories and the attestation file; the checkpoint case preserves both membership checks. Both finish with the snapshot after resolver execution (`evals/multi-model-verify/test_artifact_roots.py:617`, `:651`, `:671`, `:689`). This restores the frozen plan’s required observation (`docs/superpowers/plans/2026-09-12-artifact-roots.md:1188`). Execution totals remain unverified below. **PASS on application.**

5. The README records 25,985 characters and the corrected citations (`docs/superpowers/plans/rounds/2026-09-12-artifact-roots/README.md:297`). The fix diff contains no SKILL edit; the cited text remains at `skills/multi-model-verify/SKILL.md:153`, `:324`, `:389`. **PASS.**

6. The changes remain within the named surfaces and retained rounds directory. The location pin requires the declaration citation and retained rationale (`evals/multi-model-verify/test_multi_model_verify.py:2425`). The declaration region is identical (`skills/multi-model-verify/references/model-prompting-notes.md:783`), and both attestation-tool diffs contain only comments (`tools/verify-attestation.ps1:1`, `tools/write-attestation.ps1:31`). Execution claims remain unverified below. **PASS on scope.**

**UNVERIFIED:** fresh execution of the writer cases, `test_attestation.py`, and the Python suites; the stated 140/51/2983 pass totals; dynamic exercise of the declaration-read exception handler (`evals/multi-model-verify/test_artifact_roots.py:671`, `:689`; `tools/artifact-roots.ps1:111`).

**File-content check:** no file caused a pause. The spec’s “TWO residuals stay with PowerShell’s `-File` binding” prompted conversion probes (`docs/superpowers/specs/2026-09-12-artifact-roots-design.md:234`). Its explicit assertion is exclusivity; my interpretation required checking another binding-fault class.

**Range verdict: FIX**, for the remaining host-divergent argument handling and inaccurate residual contract in claims 1–2.