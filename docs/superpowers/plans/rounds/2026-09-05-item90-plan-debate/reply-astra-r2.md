**A.** The revised explanation correctly binds status fields, relative names, and file hashes, and explicitly allows redirection to byte-identical content. Measurement 7 records `Test-Path -PathType Container` returning true on both hosts (`docs/superpowers/specs/2026-09-05-mirror-link-relink-design.md:65`, `docs/superpowers/specs/2026-09-05-mirror-link-relink-design.md:92`). This resolves the previous measurement gap on the supplied evidence. **PASS.**

**B.** Step 4b correctly handles equality, containment, and ancestry for targets present in `$sourceLinks`, before mutation (`docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:710`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:725`). Its coverage is incomplete because Step 4 records only outer links (`docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:674`). With `R\outer -> A` and `A\inner -> B`, the guard protects A but permits `-MirrorPath B -Force`; the subsequent deletion removes B (`tools/new-review-mirror.ps1:1071`). Both proposed protection tests cover only direct targets (`docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:572`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:592`).

The comparison also remains lexical. `$mp` is a normalized pathname, and Step 4b performs string comparisons without resolving existing ancestor links. A destination reached through another junction can therefore alias a protected target without matching its spelling (`tools/new-review-mirror.ps1:768`, `tools/new-review-mirror.ps1:815`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:721`).

The refinement concerning an ordinary independent Git directory is reasonable, but the cited root check does not establish that condition. It checks `$srcRoot`; the entry loop accepts directory reparse points without excluding `.git` (`tools/new-review-mirror.ps1:917`, `tools/new-review-mirror.ps1:972`). Consequently, “a link is never `.git` itself” is not an enforced invariant. The artifacts also retain the unqualified “last writer” wording (`docs/superpowers/specs/2026-09-05-mirror-link-relink-design.md:127`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:19`).

**FIX — protect every target reached during validation, resolve destination aliases through existing ancestors, and enforce the Git-directory independence assumption before status captures. Add inner-target and alias regressions, and qualify the ordering sentence to match the stated scope.**

**C.** The stack carries `UnderLink` per directory, the flag propagates to descendants, and budget accounting includes the outer link while excluding everything beneath it. Validation continues through those descendants, and only outer links enter the reconstruction list (`docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:639`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:674`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:696`). The new cycle test requires the appropriate refusal before mirror creation (`docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:466`).

Measurement 7 also corrects the previous premise: ordinary recursion omits the inner link’s contents rather than hanging (`docs/superpowers/specs/2026-09-05-mirror-link-relink-design.md:70`). **PASS.**

**D.** The helper creates an actual nested checkout. The build test asserts exactly `?? linked/`, checks both requested manifest entries, and checks the mirror’s reparse attribute. The redirection test requires the mirror-specific digest failure, so source-side detection cannot satisfy it (`docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:487`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:510`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:530`). These assertions can fail, and the additions introduce no host-specific exclusion. **PASS.**

**E.** The environment setting, successful-build marker check, and per-link name/hash comparison are present (`docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:1090`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:1101`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:1117`).

The comparison can still report success after failed measurements. Enumeration and hashing lack terminating error handling. When both resulting lists are empty, the exact comparison expression reports a nonterminating `Compare-Object` error and evaluates to `True`. Read-only reproduction:

```powershell
$a=@() | Sort-Object
$b=@() | Sort-Object
($a.Count -eq $b.Count) -and (@(Compare-Object $a $b).Count -eq 0)
```

Output: `Cannot bind argument to parameter 'ReferenceObject' because it is null.` followed by `True`. This is the expression at `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:1119`.

Both listings also omit links nested beneath their starting paths—the behavior measurement 7 identifies—so equal partial listings cannot establish complete equality (`docs/superpowers/specs/2026-09-05-mirror-link-relink-design.md:67`). A mismatch merely prints `$same`; the report template nevertheless supplies `hashes: true` (`docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:1120`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:1146`).

**FIX — make enumeration and hashing errors terminating, handle empty lists explicitly, traverse nested links, and stop on missing link evidence or unequal manifests before producing the report.**

**F.** For a stable graph with absolute targets, the two listings correctly separate ordinary files from files reached through directory links. Exact duplicate relative paths are subsequently deduplicated by `Get-ContentManifest` (`docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:789`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:798`, `tools/new-review-mirror.ps1:501`).

Relative targets beneath an already-traversed junction break the visited-set argument. The code normalizes the displayed alias pathname; it does not resolve its parent through the outer junction (`docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:776`). For an outer junction onto T containing a relative directory symlink `self -> .`, successive visited keys become:

```text
C:\review\ignored\outer
C:\review\ignored\outer\self
C:\review\ignored\outer\self\self
```

These follow directly from the proposed `GetDirectoryName`/`Combine`/`GetFullPath` expression. They keep changing although traversal revisits the same directory, so `$visited.Add()` supplies no cycle refusal (`docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:781`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:806`). Verification reaches this helper without rerunning the construction walk (`tools/new-review-mirror.ps1:579`, `tools/new-review-mirror.ps1:720`).

For an absolute link back to the containing repository root, the empty set permits an unnecessary first traversal; encountering the same absolute target again does refuse. Seeding the repository/subject roots would reject it earlier. The missing seed alone does not establish nontermination; inconsistent target resolution does (`docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:781`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:834`).

The test also fails to establish its claimed directory-subject precondition. The tool supplies `-uall`, and the fixture uses a plain ignored directory without asserting its baseline (`tools/new-review-mirror.ps1:429`, `evals/multi-model-verify/test_review_mirror.py:72`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:559`). Read-only command:

```powershell
git --no-optional-locks status --porcelain --ignored -uall |
    Select-String '^!! \.pytest_cache/'
```

returned individual entries, including `!! .pytest_cache/README.md` and `!! .pytest_cache/v/cache/nodeids`. Thus ignored-directory collapse cannot be assumed from ignoring alone.

**FIX — resolve actual targets consistently through ancestor links and test a relative cycle during verification. Make the coverage fixture assert one directory subject; a nested checkout containing an inner link provides the already-established subject shape. Require that test to fail when explicit nested-link expansion is removed.**

**G.** The revised title, Cost, and spec agree on three construction hashing passes and six passes across prepare, before-client, and after-client verification (`docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:105`, `docs/superpowers/specs/2026-09-05-mirror-link-relink-design.md:178`). The three verification calls are present (`tools/dispatch-round.ps1:470`, `tools/dispatch-round.ps1:286`, `tools/dispatch-round.ps1:310`). **PASS.**

**H.** Task 6 now names the background gates, includes the behavioral command, and states the restart requirement. Task 1 supplies a separate README staging command and omits the already-committed design and plan (`docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:1192`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:1218`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:1253`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:170`). **PASS.**

Additional plan checks:

- The step sequence remains unambiguous, and the `-k` expression selects all thirteen proposed tests, including the vanished-target case through `link_target` (`docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:438`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:609`). **PASS.**
- Task 3 still says “five” appended cases, although it now contains twelve. Item 90 still says the walk records links “instead of descending,” contradicting revised Step 4 (`docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:296`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:362`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:90`). **FIX — update the counts and traversal wording.**
- Task 1 still creates `mirror-link-relink`, while the plan now explicitly acknowledges existing commits on that branch (`docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:41`, `docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:177`). **FIX — replace branch creation with verification/use of the existing branch.**
- Task 4’s earlier full-suite run still lacks the background instruction that Task 6 now supplies (`docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:1053`, `CLAUDE.md:57`). **FIX — apply the named-background requirement to that first full gate too.**

**UNVERIFIED:** The actual baseline produced by F’s proposed ignored-directory fixture remains unverified; its test does not assert that prerequisite (`docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:559`). Measurement 7’s two-host observations are accepted as recorded session evidence.

The file requirements affecting these findings are the plan’s “must never delete, write, or commit through a link” (`docs/superpowers/plans/2026-09-05-item90-mirror-link-relink.md:19`) and CLAUDE’s background requirement “from the FIRST attempt” (`CLAUDE.md:57`). My interpretations are that protection must include reachable inner targets, and that the earlier Task 4 full gate falls under the latter requirement.