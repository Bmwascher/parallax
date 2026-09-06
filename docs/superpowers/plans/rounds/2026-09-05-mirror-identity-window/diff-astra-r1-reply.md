Claim 1 survived: I found no sidecar-content path that changes the verification verdict. The reader’s size refusal, parsing, rendering, and exception fallback all return to the already-selected `exit 1`; clean verification skips the reader. ([reader](C:/Temp/pxd1/tools/new-review-mirror.ps1:974), [fallback](C:/Temp/pxd1/tools/new-review-mirror.ps1:1032), [caller](C:/Temp/pxd1/tools/new-review-mirror.ps1:1186))

1. **CONFIRMED — High: the trailing-dot alias defect remains on the destructive destination path.**  
   The overlap guard compares path spelling, while the new trailing-dot/space refusal applies only to extra inputs. ([overlap guard](C:/Temp/pxd1/tools/new-review-mirror.ps1:1274), [extra-input guard](C:/Temp/pxd1/tools/new-review-mirror.ps1:1713))

   On **both PowerShell 5.1 and 7**, I executed the shipped construction prefix with `Remove-Item` replaced by a harmless interceptor. With `-RepoRoot C:\Temp\pxd1 -MirrorPath C:\Temp\pxd1. -Force`, it reached the recursive deletion call targeting `C:\Temp\pxd1.`. No deletion ran. ([deletion](C:/Temp/pxd1/tools/new-review-mirror.ps1:1786))

   This is a pre-existing instance of the same alias defect class, rather than an inversion of the newly added checks. **Change:** reject ambiguous trailing-dot/space components on destination and protected paths before comparisons, and add a regression proving the source survives this invocation.

2. **CONFIRMED — the rendering tests can pass without measuring rendering.**  
   The runtime-category test checks only exit 1 and absence of raw U+0890. The trailing-newline test checks only exit 1 and absence of “could not be read.” Consequently, both accept the reader’s legitimate `what moved: unknown - the advisory explanation failed (...)` fallback. ([category assertions](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:2114), [newline assertions](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:2069), [fallback](C:/Temp/pxd1/tools/new-review-mirror.ps1:1032))

   These are not literally tautological assertions; they become green when the intended behavior was never exercised. **Change:** require the complete expected escaped filename in its expected group, and require the known changed filename in the newline test. Use exact output assertions to reject doubled escapes too; the existing substring assertion accepts them. ([substring oracle](C:/Temp/pxd1/evals/multi-model-verify/test_review_mirror.py:2089))

3. **CONFIRMED — item 93’s amendment overstates the measurements.**  
   The measurements establish non-reproduction in the three recorded runs. They do not establish “item 90 did not close one” or “Whatever produced it is not a property of the tracked tree.” ([measurements and conclusions](C:/Temp/pxd1/docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window/gate-results.md:56), [backlog conclusion](C:/Temp/pxd1/BACKLOG.md:4004))

   Code can cause a slowdown only under particular inputs or environmental conditions; fresh-worktree non-reproduction does not exclude that interaction. **Change:** say the runs neither reproduced the slowdown nor established its cause or resolution. Retain the unexplained original observation and the OPEN status.

4. **CONFIRMED — the record claims static review could not catch an ordinary assertion mismatch.**  
   README says neither oracle defect “was catchable by any round” because no round ran the tests. Its next paragraph directly explains a mismatch between the asserted phrase `extra input` and the specified message `-ExtraInput`. That mismatch is inspectable without execution. ([claim](C:/Temp/pxd1/docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window/README.md:391), [counterexample](C:/Temp/pxd1/docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window/README.md:397))

   **Change:** “The reviews missed these defects; implementation runs exposed them.” Discovery history does not prove impossibility of earlier discovery.

5. **CONFIRMED — a shipped parser comment still teaches the discarded empty-record explanation.**  
   The introductory comment calls an empty line a trailing-newline split artifact. The implementation’s nearby comment correctly says `StringReader` eliminates that artifact and every arriving empty string is a real malformed record. ([stale comment](C:/Temp/pxd1/tools/new-review-mirror.ps1:794), [actual behavior](C:/Temp/pxd1/tools/new-review-mirror.ps1:805))

   **Change:** remove the obsolete explanation and state the real-empty-record rule once.

The remaining dispositions and sweep limits:

- **Ordering:** I found no ordering inversion among the added lexical, alias, extra-input, and sidecar-existence checks. They precede sidecar deletion. Finding 1 concerns missing validation. ([checks](C:/Temp/pxd1/tools/new-review-mirror.ps1:1644), [deletion boundary](C:/Temp/pxd1/tools/new-review-mirror.ps1:1751))
- **Formatter:** exact-escape and output-bound probes passed on both hosts, including control-heavy and supplementary-character inputs. I found no defect in the implemented category set or 200-character bound. Claim 3 holds for the explanation’s stated scope; it is not true of all script output, because the construction record prints the sidecar path directly. ([formatter](C:/Temp/pxd1/tools/new-review-mirror.ps1:910), [raw construction output](C:/Temp/pxd1/tools/new-review-mirror.ps1:2247))
- **Class sweep:** I inspected changed escape literals, negative-only assertions, categorical measurement conclusions, adjacent comments, and self-count wording. No fifth executable backslash-doubling incident or unambiguous self-count error was found. README’s “Both” is ambiguous, but can refer to its two oracle defects; its separate ordering defect makes explicit wording preferable. ([README](C:/Temp/pxd1/docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window/README.md:391))
- **Behavioral evidence:** the skipped suite is honestly recorded and supplies no evidence that sessions follow the quiet period. ([declared gap](C:/Temp/pxd1/docs/superpowers/plans/rounds/2026-09-05-mirror-identity-window/gate-results.md:74))

**FIX — the reproduced destination-alias bypass reaches recursive source deletion, and the test oracles and record need the corrections above.**