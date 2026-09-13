**FIX.** The round-2 repairs are present, but path-error handling still violates the resolver’s exit contract.

`plan` below means `docs/superpowers/plans/2026-09-12-artifact-roots.md:1`.

**A.** All three applications are present. `Resolve-Absolute` precedes validation and Git, with the new location regression (`plan:403`, `:548`, `:596`). The writer test checks membership for the attestation directory and file, refusal for their shared parent, and both paths in the older negative control (`plan:1147`, `:1157`, `:1162`, `:1177`). The declaration prose, backlog replacement and spec now date the copy September 8 (`plan:234`, `:1303`; `docs/superpowers/specs/2026-09-12-artifact-roots-design.md:40`). **PASS.**

**B.** The relative-path repair works on both hosts: the extracted resolver now returns the correct common-directory paths when PowerShell’s location differs from the process directory (`plan:596`, `:621`). However, resolving before `Test-Path` changes a refusal. For `-RepoRoot NoSuchArtifactDrive:/repo`, the previous directory test returns false; the new resolution call throws, producing exit **1** on both hosts instead of the documented **2** (`plan:527`, `:551`, `:596`, `:597`).

The same uncaught exception occurs with `-Assert NoSuchArtifactDrive:/x` (`plan:700`). Another host difference remains for `-DocsRoot 'bad|root'`: PowerShell 5.1 throws from `IsPathRooted`, while PowerShell 7 accepts and prints the unusable Windows path (`plan:629`, `:637`).

Route path-resolution exceptions through `Fail`, validate forbidden Windows characters in the supplied docs-root consistently across hosts, and add regressions requiring exit 2 with `ERROR:` output for these inputs (`plan:539`).

Also correct the new explanation at `plan:405`, `:591` and `docs/superpowers/specs/2026-09-12-artifact-roots-design.md:182`. Both probes show native Git using PowerShell’s location. The round-2 failure came from the relative common-dir value reaching `.NET GetFullPath`; the existing mirror-tool explanation identifies that distinction correctly (`tools/new-review-mirror.ps1:1234`). **FIX.**

**C.** The writer assertions are now mutually consistent. The exact set contains the file and its two new directories; membership checks cover only the attestation directory and file, and the shared parent is refused (`plan:1147`, `:1157`, `:1162`). Both negative controls account for their created directories (`plan:1177`, `:1192`). Resolver probes on both hosts returned 0 for the two retained destinations and 1 for the parent and both straying destinations, matching the membership rule (`plan:704`, `:712`). **PASS.**

**D.** The round-2 findings are addressed, and the amendments add no consumer-repository artifact root (`plan:173`, `:1147`). The new unhandled refusal and inaccurate explanation identified in B prevent confirmation that the amendments introduce no defect (`plan:591`, `:596`). Apply B’s error handling, validation, regression tests and wording corrections. **FIX.**

### Final check

**UNVERIFIED:** the historical 54 MB measurement, explicitly excluded from the verdict by `docs/superpowers/specs/2026-09-12-artifact-roots-design.md:49`.

No file content caused a pause.

**Verdicts: A PASS; B FIX; C PASS; D FIX. Plan blob `ed251078e695d34a68675aaeb4655e619bb3bc62`: FIX.**